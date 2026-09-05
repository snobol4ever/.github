# FINDING (seat02, 2026-09-05): jcon's `collate` cured — a nine-function strlen-on-embedded-NUL class, plus a second layer at STRVAL(), plus a missing image() escape set

**Seat:** seat02 · **Mode at measurement:** FLEET-16 · **Tree:** SCRIP `0679df433`, corpus `911c49b77`, RT_OPT=`-O0`, incremental `make`
**Row:** `icon-jcon-suite-39-non-pass-censused-by-class-and-cured` (this row's own established diff-size-sweep methodology, 8th pass)

## METHOD (unchanged from the 7 prior passes on this row)

Fresh board, then a diff-size sweep of the m3 FAIL bucket (`diff <(./scrip --run) .std | wc -l`, sorted)
to find the smallest untried gap. `lists` (6) is the already-known oracle-disagreement class (not a bug).
`collate` (10) had never been examined by any of the 7 prior passes — picked as the target.

## THE SYMPTOM, ISOLATED

`collate.icn`'s output has 126 lines: the first 4 (from `collate()`/`decollate()` on `&cset`-derived
strings) were empty (`""`), the remaining 120 (an unrelated `permute()`/`sort()` block with zero cset
interaction) were byte-perfect. A minimal repro narrowed it in two calls:

```
write(image(left(&cset,3)))     -- got "   " (three pad spaces, as if given "")
write(image(reverse(&cset[1:4]))) -- got ""
```

Direct indexing (`&cset[1:4]`) and `string()` coercion both return `&cset`'s content correctly
(`"\x00\x01\x02"`); only a specific family of BUILTIN FUNCTIONS mishandled it.

## ROOT CAUSE, LAYER 1: strlen() on a string that legitimately starts with byte 0

`&cset` is Icon's 256-byte "every possible character" string, byte-value-ordered — its first character
IS byte 0. `src/runtime/by_name_dispatch.c` implements nine related builtins (`left right center reverse
map trim repl detab entab` — literally the one alphabetized family this file's own two builtin-name
tables list together) by materializing the subject via `VARVAL_fn()`/`icn_pad_str()` (both return a raw
`const char *`, discarding the descriptor's own length) and then computing the subject's length via
plain `strlen()`. `strlen("\x00...")` is 0. Every one of the nine treated `&cset`, or any string derived
from it, as empty.

This is the SAME class as the cset-type fix two days ago (FINDING-2026-08-19-...-cset-canonical..., and
more recently the trace-dispatch case-folding finding this same morning) — a NUL-terminated-C-string
assumption meeting a value that is not conceptually NUL-terminated at all. That fix covered the `cset`
TYPE's own construction/read primitives; this is a sibling family of plain STRING builtins that never
got the same treatment.

**Fix:** a new `icn_true_len(DESCR_t d, const char *materialized)` helper — `descr_slen(d)` (already used
elsewhere for exactly this reason, immune to embedded NULs) when `d.v == DT_S`, else `strlen(materialized)`
(safe: a coerced int/real string can never contain an embedded NUL). Applied at all nine call sites'
length computation (`repl`'s replication count, `reverse`'s loop bound, `map`'s subject AND its two
mapping-table lengths, `trim`'s truncation boundary, `left`/`right`/`center`'s source length, `detab`'s
loop bound — rewritten from an implicit NUL-scanning `for (int i=0; s[i]; i++)` to an explicit bound,
`entab`'s explicit `strlen`).

## ROOT CAUSE, LAYER 2: STRVAL() ALSO derives its length via strlen()

Fixing layer 1 alone was insufficient — `left(&cset,3)` then computed the CORRECT 3-byte content but
still displayed as `""`. `#define STRVAL(s_) ... .slen = descr_cstrlen(_sv_) ...` and `descr_cstrlen` is
`strlen()`. So a freshly-built, byte-correct output buffer that itself happens to start with (`left`) or
end with (`reverse`, on this specific witness) a `\x00` byte gets silently re-truncated on the way OUT,
independent of whether the computation that built it was correct. This codebase already carries the
fix for this exact shape elsewhere — `BSTRVAL(buf, explicit_len)`, used by `bn_trim`/`bn_dupl`/`bn_replace`
(SNOBOL4-side sibling functions, unrelated to this row, already correct) — so this is not a new pattern,
just one that never got propagated to these nine Icon builtins. Switched all nine output sites from
`STRVAL(buf)` to `BSTRVAL(buf, <the already-known correct length>)`.

**Both layers were necessary and neither alone was sufficient** — layer 1 without layer 2 still shows
`left(&cset,3)` as `""` (computed right, displayed wrong); layer 2 without layer 1 never gets a correct
length to pass to BSTRVAL in the first place.

## A THIRD, SEPARATE GAP FOUND ALONG THE WAY: image()'s missing escape mnemonics

After both layers, `collate.icn`'s diff was reduced from "wrong content" to a pure escape-spelling
mismatch: every byte value already agreed with the oracle, but SCRIP's `image()` rendered `\x08 \x0b \x0c
\x1b \x7f` as hex escapes where real Icon uses the short mnemonics `\b \v \f \e \d`. Confirmed against
`collate.std`'s own 256-byte cset dump byte-for-byte (`\n \t \r` were already handled; `\x07`/BEL is
genuinely `\x07` in the oracle too, not `\a` — checked directly, not assumed). Added the five missing
`case` arms to `image()`'s string-quoting branch. `image()`'s CSET-typed branch (a separate code path,
`IS_CSET_fn`) has NO short mnemonics at all and is very likely the same gap — NOT fixed here, no failing
witness exercises it in this suite, flagged rather than guessed at.

## VERIFICATION

- `collate.icn`: byte-identical against oracle, both modes (was empty-output FAIL, both modes).
- Icon smoke: 15/15 both modes (unchanged, control arm).
- SNOBOL4 smoke: 7/7 both modes (unchanged, control arm — this file is shared runtime infrastructure
  across all seven languages).
- Full SNOBOL4 corpus gate (the real regression arm, given the shared file): **m3 PASS=1801 FAIL=0,
  m4 PASS=1801 FAIL=0 SKIP=0, ast 28/28, MISSING=0, GATE OK** — zero movement anywhere outside `collate`.
- Full JCON board: **m3 PASS 43→44, m4 PASS 40→41** (`collate` only; grepped both FAIL/CRASH/HANG name
  lists before and after — no other entry's bucket changed in either mode). DONE-WHEN still far from met
  (m3_pass=44 of the row's own `>=50` floor).

## BLAST RADIUS NOT CHASED HERE

`by_name_dispatch.c`'s builtin-ID dispatch (`BID_left` etc.) is a SHARED mechanism keyed on the function
NAME's numeric id, not on language — whether Raku, Pascal, Snocone, or Prolog ever reach these same nine
arms (as opposed to their own separately-implemented same-named builtins, e.g. the file's OTHER, unrelated
`reverse` at a different dispatch point that appears to be Raku's list-reverse) is unconfirmed. The full
SNOBOL4 corpus gate (which shares this file) is clean, which is meaningful control-arm evidence, but the
other five languages' own suites were not individually re-run — a fresh `make test` before the next
cross-language landing would close this gap cheaply if anyone needs the assurance sooner than that.

## ADDENDUM, SAME SITTING: a concurrent, UNRELATED commit regressed `coerce` on the very next re-measure

Re-running the JCON board after pushing (to land the SCORE.md update on a clean tree) showed
**m3 PASS=43 FAIL=27** — `collate` correctly gone, but `coerce` newly appeared in the FAIL bucket,
netting to the same headline count as before this row's own fix. Confirmed deterministic (3 identical
runs) and confirmed NOT caused by this row's own change: `git log` between my verified-clean build and
this one names `6dddcc237` ("Raise SPITBOL error 29 for unregistered unary ! instead of a silent
fallback"), landed by a different sitting in the same file, ~13 minutes after my own commit.

That commit changed `try_call_builtin_by_name_bl`'s `fn[0]=='!'` arm: previously, calling `!` as a
BY-NAME-invoked procedure value (`o(i)` where `o` holds the string `"!"`) returned the argument unchanged
for ints/reals, or its first character for strings; now it raises runtime error 29 ("Undefined operator
referenced") unless `!` is OPSYN-registered. The commit's own verification checked ONLY Icon's *direct*
`!x` AST syntax (`bang_invoke.icn`/`bang_binary.icn`, confirmed unaffected) and the SNOBOL4 corpus
(verified clean) — it did not check Icon's BY-NAME invocation path, which is the SAME shared function.
`coerce.icn` ("check coercion of operator arguments — uses string invocation of operations") deliberately
exercises exactly this: `every unop(!"+-*!/\\", i, r, c, s)` generates each operator character including
`!` itself, then calls `o(i)` etc. **The oracle's own `.std` proves Icon's actual contract**: row `!x`
reads `1 2 3 9` for i/r/c/s=`1,2,'3',"9"` — i.e. real Icon's by-name `!` returns int/real unchanged and
a string's first character, EXACTLY the old "silent fallback" behavior 6dddcc237 replaced. SNOBOL4 wants
error 29 here; Icon wants the old identity/first-char answer; both requirements land on the same
unconditional code arm with no language discriminant between them.

**Not my bug, not fixed here, not chased further** — this is squarely a SHARED-NODE VERDICT SCOPE
conflict needing a language-aware dispatch (or a separate Icon-side implementation of this specific
by-name-call idiom), which is a design decision, not a quick patch. Minted
`icon-jcon-shared-bang-dispatch-error29-regresses-coerce-by-name-invocation` (owner hq_C, shared-engine
lane) with the full diagnosis and both oracles' evidence; sent hq_C the handoff and hq_B (this suite's
own lane) a heads-up that `coerce` is a real, understood, already-routed regression, not a mystery and
not this row's fault. **This row's own verification stands**: the SNOBOL4 corpus gate I ran to confirm
my fix (1801/1801 FAIL=0 both modes) was measured BEFORE `6dddcc237` landed, so it does not, and was
never claimed to, cover that commit's own effect — re-verify SNOBOL4 fresh before citing this addendum's
board number as a joint verdict on both changes.

## WHOEVER RESUMES THIS ROW

`collate` is closed. Per this row's own established practice (re-diff fresh, never trust a prior pass's
size list without re-measuring): the current m3 FAIL bucket, smallest-first, no longer contains `collate`
or `lists`(oracle-disagreement, not a bug) — re-run the sweep from the current board before picking the
next target. `image()`'s CSET-branch escape gap (above) is a small, well-scoped, likely-quick next lead if
a failing witness for it turns up.

## 9TH PASS ADDENDUM (2026-09-05 seat02, FLEET-16, SCRIP `674319235`)

**Cured and pushed**: a THREE-SITE class defect in how this codebase compares Icon procedure/record-
constructor VALUES (the `DT_E` descriptor flavor tagged `slen==0xFFFFFFFEu`, minted by `rt_proc_value()`
in `rtx_icncall.s`). Every bare reference to a global procedure or record-constructor name (`main`, a
user record like `rec`) bakes its OWN separate `.string` literal in the emitted `.s` — same CONTENT,
different POINTER per occurrence. Three independent runtime comparisons all compared these values by raw
pointer/int bits instead of by name, so they never matched even against themselves:
1. `descr_identical()` (`src/runtime/values.c`) — used by `bb_ident.cpp`/`IR_IDENT` and the by-name
   `===`/`~===`/`IDENT()` dispatch paths (`by_name_dispatch.c:4019`,`:6105`) — fell through to a raw
   `memcmp(&a,&b,sizeof(DESCR_t))`, which also compares the per-node `src_node` debug stamp.
2. `rt_jct_relop_impl()` (`by_name_dispatch.c:3785`) — the actual implementation of Icon's DIRECT `===`/
   `~===` syntax (lowers to `IR_BINOP_TEST` with `binop=BINOP_EQV`/`NEQV`, NOT through `bb_ident.cpp` —
   that box is for a different path; confirmed via `--dump-ir`). Compared via `lhs.i==rhs.i` (raw
   pointer-as-int).
3. `BID_IDENTICAL` (`by_name_dispatch.c:5773`) — the builtin Icon's `case` statement calls for any
   arm label that isn't a foldable literal (confirmed via `--dump-ir`: `main:`/`rec:` labels lower to
   `CALL_BUILTIN [..] "IDENTICAL"`, a THIRD, separate mechanism from both of the above). Compared via
   `a.ptr==b.ptr`.
All three now special-case the procval flavor of `DT_E` by comparing `.s` (the name) with `strcmp`. Empirically
verified with `if main === main then write("EQ") else write("NE")`-style repros before AND after each fix —
this is a case where reading the box template alone (`bb_ident.cpp`) pointed at the WRONG implementation;
`--dump-ir` on a minimal repro was needed to find the real one, twice.

**Two adjacent bugs fixed in the same functions, found while isolating the above**:
- `image()`'s `DT_E` formatter (`by_name_dispatch.c:4744`) reported EVERY procval as `"function NAME"` or
  `"procedure NAME"`, never `"record constructor NAME"` — real Icon's `image()` distinguishes them (`type()`
  correctly does not, matching real Icon). Fix reuses the ALREADY-EXISTING `dat_find_type(name)` registry
  (the same one `record_register()` populates) rather than adding any new tracking — record constructors
  were never added to `g_stage2.proc_table`, they go through `record_register()`/`dat_register()` instead,
  a separate mechanism this file already calls elsewhere.
- `BID_IDENTICAL`'s `DT_S`/`DT_SNUL` branch compared string CONTENT without checking the cset sentinel
  (`slen==0xFFFFFFFFu`), so a cset and a same-content string (`'1'` vs `"1"`) compared identical — the other
  two implementations already guarded this (`lcs`/`rcs` in `rt_jct_relop_impl`, `a_cset`/`b_cset` in
  `descr_identical`); only `BID_IDENTICAL` was missing it.

**Effect on `jcon_tests`**: `case.icn` (3-sub-bug cluster since the 3rd pass) is now down to ONE remaining
diff line — `image()` of a co-expression (`c : ""` vs `c : co-expression_2(0)`), which is the already-open,
already-minted `icon-jcon-class-serial-and-image-object-numbering-missing` design-scale gap. Not a full PASS,
so the jcon board headline is UNCHANGED at m3 43/81 · m4 40/81 (no other FAIL-bucket program happened to use
a bare-identifier case-arm label or a mismatched cset/string case-arm in a way that flips it, per a fresh grep
of the corpus for `===`/`~===`/`case` users: `sorting recent gener io` all use `case` and are worth a quick
re-diff by the next pass, though their diffs were large (122-492 lines) before this fix and are unlikely to
fully flip). DONE-WHEN still far from met (43 of the >=50 floor).

⛔ **SEPARATE, NOT-FIXED, FLAGGED FINDING — reported to hq_B, not this row's scope**: the SNOBOL4 corpus gate
(`bash scripts/test_corpus_snobol4.sh`), the fleet's cross-language regression control arm, currently reads
**mode-3 PASS=1803 FAIL=26, mode-4 PASS=1803 FAIL=21** (plus 4 separately-reported TIMEOUT-KILLED, not counted
in FAIL) — NOT the `FAIL=0` this file's own CLAUDE.md digest and this row's every prior pass have measured.
**Isolated via stash/rebuild/re-measure**: ran the FULL gate twice, once with this pass's 3-file identity fix
applied (SCRIP dirty, load 22.37/16 cores) and once with it `git stash`ed out (clean pre-fix tree, load
13-17/16 cores) — **both runs read the exact identical FAIL=26/21**, proving this is a pre-existing condition
on origin/main, not caused or worsened by this pass's fix, and not machine-load jitter (a deterministic
content-mismatch count, reproduced twice under different load, is not what timeout/hang noise looks like).
Likely candidate cause (not chased, out of lane): the SNOBOL4 master corpus itself grew substantially between
this row's earlier passes and now (1801 -> 1859 entries, from an unrelated `corpus` pull absorbing new
`ALL.sno`/`ALL.ref`/`ALL.csv` content mid-session) — but this is a guess, not verified, and is SNOBOL4-lane
work, not Icon/jcon work. Reported via `ask` to hq_B (this row's HQ) rather than chased or fixed here.
