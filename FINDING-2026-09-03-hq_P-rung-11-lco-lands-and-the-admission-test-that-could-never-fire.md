# FINDING — Prolog rung 11 (LCO) lands, and the sec B.18 admission test that could never have fired

**hq_P, 2026-09-03.** Tree: SCRIP `d90a860f` · corpus `54d5b5cf4` · .github at this commit. RT_OPT=`-O0`.
MODE `QUARTET`. Row `prolog-rung-11-last-call-optimisation-lco` (ceo GO, ASSIGNED hq_P).

## The result

`test_prolog_ladder.sh --only 11` goes **0/2 → 2/2**. `test_gate_pl_port_trace.sh --only 11` **PASS**.
The ARCH sec B.18 depth criterion is met and it is the number that matters:

| arm | N=1000 | N=1000000 | verdict |
|---|---|---|---|
| m3 `--run`, `ulimit -s 512` | max RSS 9900 kB | max RSS 9816 kB | FLAT over a 1000× range |
| m4 `--compile`, `ulimit -s 512` | max RSS 5384 kB | max RSS 5152 kB | FLAT over a 1000× range |

Before: `ERROR 246 -- stack overflow`, with the ceiling between N=60000 and N=70000 at the **default 8 MB**.
After: 10^6 deep in **512 KB**. That is O(1) stack, not a raised ceiling — the distinction the criterion exists
to force, and the reason RSS is reported at two N rather than a single "it didn't crash".

## FINDING 1 — the admission test sec B.18 specifies could never have been true

The zframe prologue ends in `rt_pl_choice_open(H)`, whose entire body is `mov r13, rdi; ret`. So **B := H
unconditionally at every clause-choice entry**, while F.B0 holds the *caller's* B. `cmp r13, [H+24]` is therefore
false for the whole life of a multi-clause activation. Implementing sec B.18's admission test literally — as the
section, and this row's own first reconnaissance, both describe it — yields a test that is correct on paper and
**never fires**, with no error, no diagnostic, and a fast path that is simply dead code.

The missing piece is the WAM's **trust_me**: the last alternative must DROP the choice (B := F.B0). The
alternative trampoline advanced F.CUR to the next alternative and zeroed it on the last one, but never restored
r13. ⭐ **This is a freestanding correctness fix and was worth landing on its own merits**, independent of LCO:
the existing `altdet` frame release at γ (`cmp r13, F.B0` / `je` / pop) is gated on the *same* test, so **every
multi-clause activation retained its frame past its last clause, forever.** LCO is the second beneficiary of the
fix, not its purpose.

⛔ **The transferable shape: a guard whose condition is never true is indistinguishable from a guard that is
working.** Both are silent, both cost nothing, and both leave a green board. The only thing that separated them
here was reading the *emitted asm* for every write to r13 and finding that the one write that mattered did not
exist — ASM-DIFF-FIRST doing exactly what it is for.

## The tail marker carries NO NEW GLOBAL — and the gate proves it, by name

The obvious implementation (and the one this row was handed as a passive pointer — see PROVENANCE) is a
pointer-keyed side table in `lower_prolog.c`, mirroring emit.cpp's `bb_slot_register`/`bb_slot_get`. It costs
**three file-scope globals** — `g_pl_tail_nodes`, `g_pl_tail_n`, `g_pl_tail_max` — in a file policed by both
Lon's NO-NEW-GLOBALS rule and `test_gate_pl_no_new_global.sh`, immediately after the Prolog cut deleted 47
Prolog-only globals.

✅ **Instead the mark rides the node's own existing `IR_t.seal` field** (`#define PL_SEAL_TAIL 1`). `seal` is
already a per-op multi-purpose int by established practice — `lower_pascal.c` stores `owner_level` in it,
`lower_snobol4.c` a defer-seal level, `bb_define.cpp` the formal count — and **no reader of it is reachable for a
CALL kind**: `emit.cpp:1067` takes `n_operands` for calls and consults `seal` only for `IR_GOTO_DEFERRED`, and
every other reader is guarded on `IR_MATCH_DEFER` / `IR_MATCH_ALTERNATE` / `IR_DISJUNCTION` / `IR_DEFINE` / the
frame boxes. It survives the optimizer because the optimizer relinks γ/ω and never reallocates an `IR_t`. It is
also O(1) where the side table was a linear scan per query, and it removes a Prolog-named symbol
(`pl_tail_is_marked`) from a shared template.

⭐ **NEGATIVE-TESTED, because a gate nobody has seen fail is not evidence.** Re-inserting the three globals makes
`test_gate_pl_no_new_global.sh` print `FAIL NEW GLOBAL(S) — not on the allowlist: g_pl_tail_max g_pl_tail_n
g_pl_tail_nodes`, and removing them restores PASS. So this is not a stylistic preference: the side-table design
would not have landed, and **the verification list it arrived with did not include this gate.**

## What LCO actually does

A call that is the syntactically last goal of a clause body's top-level conjunction pops its own frame with the
**same `lea rsp,[rbp+kt]` / `mov rbp,[rbp+kt-8]` pair the altdet epilogue already uses**, and jumps the callee
with *this* activation's own inherited wires (`[rbp+kt-24]`/`[rbp+kt-16]`) rather than a fresh local landing — so
caller and callee interact as if the frame was never there, which is what relocates the F.RES-banking/redo chain
up one level. Three runtime legs, all required, any failure falling through **unchanged** to the ordinary call:

1. `rt_pl_tail_args_safe` — sec B.18's escape hazard made concrete. ⭐ **MEASURED, not assumed: ordinary Prolog
   arguments are NOT immediates.** A plain loop counter stages as a `DT_N` variable-cell reference, so a
   tag-only "immediates are safe" check refuses essentially every real call and the fast path never fires. It
   resolves through `rt_deref` (bounded to 4 hops; a hop landing on a pure immediate rewrites the staged slot)
   and range-checks any surviving pointer against `[rbp, rbp+kt)`. **What decides safety is the ADDRESS, not the
   tag.**
2. `r13 == F.B0` — no live choice of its own (the test FINDING 1 made reachable).
3. `rsp == rbp-16`, **not** bare `rsp == rbp` — the PL-CALL-ALIGN pad+L7 push is this call site's own
   unconditional transient bookkeeping, not a retained callee frame.

LCO is refused at **compile time** on the root graph, whose frame seeds r14/ROOT (`rt_pl_quad_seed` reads H off
the root's own `[rsp+kt-64]`) for the life of the run. Nested tail positions — disjunction, if-then-else and
catch/3 arms, findall's inner goal — are deliberately never marked: conservatively correct, and a real remaining
optimisation, since proving them needs tracing γtail through the join point.

## Control arms — the part that makes the number mean something

- ⭐ **Non-tail `sum/2` (`S is S0+N` *after* the call) at N=100000 still overflows at BOTH 512 KB and 8 MB.** So
  the flatness is LCO firing on tail position specifically, and not some global change to stack behaviour.
- ⭐ **A build of unmodified `origin/main`, in a git worktree OUTSIDE the seat root** (a clone inside it becomes a
  permanent `handoff_status.sh` blocker), grades `--to 11` at rung 10 `PASS=2 FAIL=4` — **identical to this
  tree** — and rung 11 `PASS=0 FAIL=2`. The four rung-10 reds are pre-existing and are not this row's. Without
  this arm the honest claim would have been "60/64, and I believe the 4 are someone else's".
- SHARED-NODE VERDICT SCOPE (`bb_call_proc_staged`: prolog 2 / icon 1 / raku 1): Icon smoke 14/14 both modes,
  Arizona 45/89 both modes, Raku smoke 724/724 both modes, quad gate 0 violations / 2360 enrolled (the new r13
  write auto-enrolled under the existing generic B/landing-or-cut-restore shape — no scanner change). And
  structurally: the LCO sequence appears in **0 of 12** Icon and **0 of 12** Raku emitted `.s` files while
  appearing for Prolog, so the probe is not vacuous.
- `make test` rc=0: SNOBOL4 m3 PASS=1689 FAIL=0 · m4 PASS=1689 FAIL=0 SKIP=0 · MISSING=0, identical before and
  after the rebase onto origin.

## Two things this row bumped into and did not chase

- ⚠️ **`test_icon_arizona_suite.sh` silently accepts unknown flags.** `--strict` is not a flag it defines; it was
  ignored rather than refused, and the run was the plain default. It happened not to matter — but a harness that
  accepts a flag it does not implement will one day print a board for an arm nobody ran. Not this row's to fix.
- ⚠️ **`scripts/jcon_selfhost_build.sh` still carries a LIVE `-O2` runtime build path** (`PERF=1` →
  `RTOPT='-O2 …'`, header: *"RULES: -O2 only for performance work"*). That is not stale prose, it is an
  executable arm, and it contradicts Lon's s262 FACT RULE outright. It is jcon/Icon lane and behavioural, so it
  is routed to ceo rather than fixed here. Note that `test_gate_digest_matches_rules.sh` polices the per-root
  digests, not `scripts/` — which is why this survived: **the gate's recall does not cover the file the
  violation lives in.**

## PROVENANCE

seat05 worked this row before the ceo released it (the picker served the LADDER row FREE; a fleet seat never
touches a rung) and, on the ceo's instruction, saved its work outside the root and pushed nothing, as an
explicitly passive pointer. **The design of the LCO fast path, the three guard legs, `rt_pl_tail_args_safe`'s
deref-then-range-check, the `rsp==rbp-16` correction, the root_graph hazard, and the trust_me diagnosis are
seat05's**, and its write-up was accurate on every point this seat re-derived. What changed here: both diffs
needed a 3-way merge (rungs 9 and 10 had landed under them — `call/1` now lowers via `pl_meta_call_dyn`, and
catch/3 added two `pl_lower_conj` call sites), the three globals were replaced by the `seal` marker, and the
explanatory C comments were removed because `src/` carries none (`strip_comments.py --check`, wired into
`make test` this same day) — which is precisely why they are written out at length here instead.

⭐ **The lesson worth keeping from the handoff itself: seat05's verification list was long, careful, and
green — and it did not contain the one gate that would have refused the design.** A verification list is
evidence about what was run, never about what was not.
