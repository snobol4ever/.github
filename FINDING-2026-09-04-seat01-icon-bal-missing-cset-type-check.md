# FINDING — CLASS FILED (not cured): SCRIP's `bal()` does not validate that its arguments are csets or
# cset-convertible. Real Icon (icont/iconx v9.5.25a) raises a runtime error and aborts; SCRIP silently
# continues past the call as if it succeeded.

**seat01 · 2026-09-04 · row `icon-ladder-top-rung-census-from-the-icon-book`** (LADDER RECIPE step 2:
walking PLAN-rung37/bal(); this is that rung's mandated REFUSAL witness).

## What's wrong

Witness (`corpus/tests/icon/ALL.icn`, entry `ladder_rung37_bal_refusal`, origin
`ladder__rung37_bal_refusal`, 5 lines):
```
procedure main()
  write("before");
  write(bal([1,2,3]));
  write("after");
end
```

Oracle (`/home/resources/icon-master/bin/icont` + `iconx`, v9.5.25a, run fresh this session —
`icont -s file.icn -x`):
```
before
```
stderr:
```
Run-time error 104
File spike2.icn; Line 3
cset expected
offending value: list_1 = [1,2,3]
Traceback:
main()
bal(list_1 = [1,2,3],&null,&null,"",&null,&null) from line 3 in spike2.icn
```
rc=1.

SCRIP (tree `e8a7263d`, both m3 `--run` and m4 `--compile`):
```
before
after
```
rc=0 — `bal([1,2,3])` neither errors nor visibly does anything useful; execution just falls through to
the next statement (whatever `write(bal(...))` actually returned/failed as, `after` still prints, so the
call did not abort the program the way the oracle does).

## Same class as the rung36 finding

This is the SECOND builtin found silently accepting an argument type its own oracle rejects outright —
see `FINDING-2026-09-03-seat01-icon-insert-missing-set-table-type-check.md` (rung36, `insert()` given a
non-set/table, oracle Run-time error 122, SCRIP rc=0). Two independent scanning/structure builtins now
show the identical shape (oracle: Run-time error + abort; SCRIP: silent continue). **Not confirmed** this
is one shared root cause (e.g. a missing/no-op coercion-check helper called from both, or two separate
call sites that each independently skip validation) — raising it as a possible CLASS defect for hq_B to
determine, per this project's own "class defect" discipline (CLAUDE.md § No per-op filters: "A defect
reachable through one family member is a class defect: fix the class or leave it visibly red, don't hide
it behind an op-name filter"). Not grepped for the owning source this session.

## Isolation

The other three rung37 witnesses all PASS SCRIP byte-for-byte in both modes:
- default open/close-paren balancing, including the plain-generator-FAIL case (`bal(',')` inside a fully
  parenthesized string finds no top-level comma and correctly fails, not errors — ordinary Icon control
  flow, distinct from this REFUSAL);
- custom `c2`/`c3` delimiters (brackets instead of parens);
- a `bal()`-vs-`upto()` contrast (`upto(',')` stops at the first literal comma even when nested; `bal(',')`
  correctly skips the nested one and stops at the true top-level comma).

So `bal()`'s core scanning semantics (default and custom delimiters, balance-tracking, generator failure)
are all correctly implemented — this is narrowly an argument-type-validation gap, not a missing-feature
gap, mirroring rung36's finding exactly.

**Not otherwise checked**: whether other scan-family builtins (`any()`, `many()`, `upto()`, `find()`,
`match()`, `tab()`, `move()`) share the same gap when given a non-cset/non-integer argument — out of
scope for this row; a systematic sweep across the scan-family builtins would be the way to size the CLASS
question above rather than guess from two data points.

Also explored (not filed as a witness): `bal()` called with zero arguments, as a bare position-generator.
On probe string `"(a(b)c)d"`, oracle `every write(bal())` prints `1` then `8` (verified live). The
mechanism behind exactly two positions — and not, say, every point where running paren-balance returns to
0 — wasn't fully worked out in the time available, and a ladder witness whose expected output I can't
explain from the book's stated semantics is worse than no witness at all, so it was deliberately left out
rather than landed as an opaque regression check. Flagging here in case it's useful groundwork for
whoever eventually writes a rung covering `bal()`'s pure-generator form.

Not read/confirmed which source owns `bal()`'s argument handling this session (candidates by name, not
grepped: `src/runtime/builtins/`, `src/runtime/rt/rt_stack_overflow.c`-adjacent scan dispatch, or wherever
`bb_scan_bal.o`/`rtx_match.o` argument marshalling lives — `bal` appears in `src/driver/scrip.c`,
`src/lower/lower_icon.c`, `src/templates/x86/x86_asm.h`, `src/runtime/keywords.c`,
`src/runtime/by_name_dispatch.c`, `src/runtime/builtin_ids.h` per a quick grep, but the actual
type-validation gap wasn't isolated to one of these). **Walker scope ends here** per `MASTER-PLAN.md` §
WHO FIXES WHAT — did not touch `src/`.

## What this row did / didn't do

- Wrote and oracle-cut 4 new witnesses for PLAN-rung37 (bal()) — `corpus/tests/icon/ALL.{icn,ref,csv}`
  entries 728-731, origin `ladder__rung37_bal_*`; added to `corpus/tests/icon/ALL.wantrc`
  (`ladder_rung37_bal_refusal	1`).
- Promoted `PLAN-rung37` to `rung37` (`BUILT-RED`, honestly RED) in
  `corpus/tests/icon/config/LADDER.tsv`; PLAN-rung38 (co-expressions, the true top) remains unwalked.
- Verified via `python3 scripts/corpus_suite_harness.py list --lang icon ALL.icn ALL.ref` (rc=0, all 4
  new entries listed, no banner-parse errors) before and after landing.
- Did **not** touch `src/`. Did **not** attempt a cure. The fix and the shared-root-cause question both
  belong to hq_B.

Verified: `bash scripts/test_icon_ladder.sh --only 37` (SCRIP `e8a7263d` / corpus `b7c674a17`-dirty this
session, 2026-09-04) — `graded=8 PASS=6 FAIL=2` (the 2 = `ladder_rung37_bal_refusal` × 2 modes; the other
3 witnesses PASS both modes). Row's own DONE-WHEN re-run for real: `--to 37`, `graded=394 PASS=386
FAIL=8` — the 8 = rung19's pre-existing 4 (still owed) + rung36's 2 (still owed) + rung37's new 2 (this
finding), all independently reasoned in `ALL.xfail`.
