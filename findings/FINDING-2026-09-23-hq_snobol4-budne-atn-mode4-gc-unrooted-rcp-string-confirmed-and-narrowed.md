# FINDING — Budne's `atn` mode-4 failure IS the unrooted-`rcp`-string bug from tonight's other finding; one site confirmed safe to land, a third site found, a fourth still open (hq_snobol4, 2026-09-23)

Extends `FINDING-2026-09-23-hq_snobol4-six-open-bugs-from-tonights-suites-to-100-percent-push.md` §2
("Unrooted compile-time string baked into JIT code"). That finding was written chasing an ARBNO
backtracking bug and found the mechanism as a byproduct, blocked from landing by one unresolved
regression. This finding: (a) proves the SAME mechanism is why `csnobol4_suite`/Budne sits at 70/71
(`atn`, mode-4 only — RED-M4, m3 is clean), (b) narrows which part of that finding's two-line fix is
actually safe to land, (c) finds a third vulnerable site in the same function, (d) confirms a fourth,
still-unlocated instance blocks full resolution. Tree: SCRIP `a22f9c6ed`, corpus `00de9e950`.

## The Budne symptom

`corpus/packages/snobol4/csnobol4_suite/atn.sno` (Budne's ATN-grammar self-compiler, uses `EVAL`/`CODE`
runtime code generation extensively) passes byte-identical to `.ref` in mode-3, fails in mode-4 only.
Minimal repro: the real `atn.sno` fed only its first 76 lines of ATN-grammar stdin (two `NETWORK` blocks,
no `FUNCTION`/`LEXICON`/`EXEC`) already reproduces it — no hand-written substitute needed, and hand-written
substitutes are a trap here (see "Repro-authoring pitfalls" below).

**Decisive, reproducible test:** running the *unmodified* binary with `SCRIP_HEAP_MB=64` (a large-enough
GC arena that no collection ever fires during the run) makes mode-4's output byte-identical to mode-3 and
to `.ref`. This isolates the defect class to a GC-collection-triggered corruption, not a codegen or
pattern-matching logic bug — confirmed both for the 76-line minimal repro and for the full `atn.sno`.

## Mechanism, traced to source

`atn.sno`'s ATN-compiler builds each network's parse pattern via `S(NA)` (`S = EVAL("(NULL $ *S_('" NA
"')) FENCE ")`), producing a `DT_P` pattern value that gets **concatenated into a larger, statically-defined
pattern** (`NETWORK_PAT = NETWORK_HEADER S('NTW') RULES_PAT ...`). That concatenation runs through
`pat_seq()` → `rcp_of()` (`src/runtime/pattern_match.c`), which — because the `DT_P` operand's `.fn` is
already set (built eagerly by `EVAL`) but its `.rcp` is `NULL` — falls into the generic "embed a foreign
pattern value" branch: mint a synthetic global name `OPQ$<n>`, `NV_SET_fn` it (this part correctly roots the
`DTP_t`), and bake `rt_heap_strdup_c(nb)` — **a GC-heap string** — as a raw C pointer into the `rcp` tree
node that later gets read back by `dtp_rcp_tree()` when `NETWORK_PAT`'s own lazy compile runs.

`NETWORK_PAT`'s lazy compile happens once, early (first `TEXT COMPILE_PAT` match, i.e. network 1) — the
`OPQ$N` string is fresh then, so network 1 always works. `atn.sno`'s own `CODE()` call (`S_ENW`, at the very
end of network 1's processing) is itself a builtin call from compiled SNOBOL4 code — exactly this collector's
defined trigger point ("collection only happens at the return of an allocating runtime call from emitted
code," per `ARCH-GC-COMPILE-TIME-FRAME-MAPS.md`). `CODE()`'s own compilation work allocates enough to
trigger a collection. The `OPQ$N` *string bytes* (not the `DTP_t`, which stays reachable via the `NV_SET_fn`
name) aren't found live by that collection's root walk, because the raw pointer is baked into an `rcp` tree
node, not carried as a tracked `DESCR_t`. Reclaimed, the string corrupts; network 2's reuse of the *same,
already-lazily-compiled* `NETWORK_PAT` machine code reads the now-garbage name, the `DEFER` lookup silently
fails-to-nothing (not a crash — a graceful "nothing to do"), and the whole `S_(NA)` side-effect chain
(`DISPLAY`/`CODE`/`DEFINE` for every network after the first) silently never fires again. Confirmed at the
assembly level with gdb (`LBL__S_`, `LBL__S_NTW` breakpoints): `S_` is entered exactly 22 times (all of
network 1's calls) and zero times for network 2's 9 expected calls, with no error, rc=0.

This is the **identical mechanism** as the existing finding's §2 (`ARB$N` from `ARBNO`'s rewrite in
`dtp_rcp_tree`'s `TT_ARBNO` case) — same file, same `rt_heap_strdup_c`-into-`rcp`-tree pattern, different
trigger.

## What's now confirmed, narrowing the existing finding's blocked fix

The existing finding's proposed fix (switch both `rt_heap_strdup_c` sites in `pattern_match.c` to
`ct_strdup`, the established compile-time-arena allocator already used pervasively for exactly this) was
**not landed** because it flips `user_function_arbno_rpos_1` (an already-red, SPITBOL-itself-rejects-the-
program xfail — `sbl -bf` gives `ERROR 251: keyword operand is not name of defined keyword` on line 8's
`&Parse5`, which SCRIP doesn't validate at all, a separate pre-existing gap) from a terminating wrong answer
into an infinite hang, in both modes.

**Isolated tonight, with a controlled A/B (each site flipped independently, rebuilt, retested):**

- **`rcp_of`'s `DT_P` branch alone** (`src/runtime/pattern_match.c:65`, the `OPQ$N` site — the one that
  matters for `atn.sno`/Budne): `rt_heap_strdup_c` → `ct_strdup`. **Fixes the 76-line minimal repro
  completely** (byte-identical to `.ref`). **Does NOT trigger the `user_function_arbno_rpos_1` regression**
  — retested standalone, in both modes, still prints the same wrong-but-terminating `depth=1`, rc=0, same as
  baseline. This one line is safe to land on its own merits, independent of the ARBNO question.
- **`dtp_rcp_tree`'s `TT_ARBNO` branch** (`:97`, the `ARB$N` site): reverting *only* this one back to
  `rt_heap_strdup_c` while keeping `:65` fixed still leaves `user_function_arbno_rpos_1` at its baseline
  `depth=1` (not hung) — so the regression traces to this site (or its interaction with the third site
  below), not to `:65`. Not re-isolated further tonight (budget) — the existing finding's open lead ("a
  second DEFER call site... {fn=NULL, aux=3}") is exactly this territory and remains the next step.
- **A third site, found tonight, not in the existing finding:** `rcp_of`'s `DT_X` branch (`:67`, the bare
  `*name` indirect-reference case) allocates its `*`-prefixed name via `rt_str_alloc` — confirmed via
  `src/runtime/rt/gc_heap.c:307` (`c_rt_str_alloc` → `rt_gcheap_alloc`) to be the **same GC-heap allocator
  class**, same vulnerability shape, just a different call (length-based, not `strdup`). Swapped to
  `ct_alloc((size_t)nl + 2)` with the same manual `'*'`-prefix + null-terminate logic. Confirmed *not* the
  fix `atn.sno` needs on its own or in combination with `:65`+`:97` (see below), but it is the same defect
  class and should travel with the rest of this row when it lands, not be left half-migrated.

## Still open: a fourth (or more) site blocks full `atn.sno` resolution

With **all three sites above patched together** (`:65`, `:67`, `:97` all `ct_strdup`/`ct_alloc`), the
76-line minimal repro stays fixed, but the **full** `atn.sno` (real stdin, all networks + functions +
lexicon + sentences + exec) still fails, at a new, later point: compiling `FUNCTION TESTF` (`S_F`'s
`DISPLAY(NAME BLANK BODY); CODE(NAME BLANK BODY)`) — `COMPILE_PAT` genuinely fails to match this time
(`COMPILE5`'s `ERROR('Compilation failed')` fires, not a silent skip), a different symptom shape than the
network case. **Confirmed still the same GC-triggered class** — `SCRIP_HEAP_MB=64` against the *full*
`atn.sno` (all three sites patched) also makes it pass byte-identical to `.ref`. The corrupted object was not
found tonight; `dtp_rcp_tree`'s two `rt_str_alloc` re-null-termination calls (`:80`, `:84`, `TT_QLIT` and the
`TT_ANY`/`TT_NOTANY`/`TT_SPAN`/`TT_BREAK`/`TT_BREAKX` literal-text cases) are the same allocator family and
the next most likely candidates — untested tonight because they feed a `tree_t` consumed synchronously
within the same compile call, which makes them *less* obviously suspect than `:65`/`:67`/`:97`'s "baked into
a tree read back on a later, separate call" shape, but that reasoning was not verified, only assumed.

**Net: source reverted, nothing landed.** `git diff` on `SCRIP/` is clean. The three isolated single-line
substitutions above are safe, reproducible, and ready to re-apply the moment a seat has budget to (a) also
resolve the `:97`/regression question the existing finding already opened, and (b) find the fourth site for
`FUNCTION`-block compilation. Landing `:65` alone, right now, would move Budne's `atn` no further (mode-4
still fails at `FUNCTION TESTF`) — it's necessary but not sufficient, so there is no partial win available
by landing it in isolation today.

## Repro-authoring pitfalls hit and worth naming

Several hours went into hand-written minimal repros for the `CODE()`-nested-inside-an-active-match shape
before finding that **the real `atn.sno`, truncated at the stdin level, reproduces reliably and is easier to
trust** than anything hand-authored — every hand-written variant that used SPITBOL's `$ *EXPR(...)`
indirect-call-during-match idiom had a quoting or grouping bug that either silently changed the pattern's
semantics (no error, just doesn't test what you think) or broke the whole match outright. If chasing this
further: start from a real corpus program's stdin truncated by input length, not from scratch.

## Ownership note

`src/runtime/pattern_match.c` is SNOBOL4-lane (per the existing finding's own ownership note, unchanged
tonight) — `rcp_of`/`dtp_rcp_tree` are reachable from any language that builds a `DT_P` pattern value
dynamically, but today only SNOBOL4's `EVAL`/`CODE`/ARBNO paths exercise this function at all (grepped:
zero non-SNOBOL4 callers of `pat_seq`/`ARBNO`-shaped `DT_P` construction as of this tree). Land or ask per
RULES.md at the time this next lands, same as the existing finding says.
