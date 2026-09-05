# FINDING (seat02, 2026-09-05): jcon census 11th pass — a real instrument bug (fncs1) cured directly, three fresh oracle-verified compiler-defect witnesses minted/added for hq_B

**Seat:** seat02 · **Mode at measurement:** FLEET-20 (seat02 = hq_B lane, Icon) · **Tree:** SCRIP `7481d1337`+rebuild, corpus `0d87acbfb`, RT_OPT=`-O0`, incremental `make`
**Row:** `icon-jcon-suite-39-non-pass-censused-by-class-and-cured` (11th pass; see task file's own `## NEXT` for the 10th pass this resumes)

## ROLE BOUNDARY THIS PASS FOLLOWED

Per MODE FLEET-20 line 1, `.github/MASTER-PLAN.md`:128/134, and the standing rule recorded in this
row's own 10th-pass `## NEXT`: Sonnet seats (this seat) walk/census/witness/mint; Opus HQs (hq_B for
Icon) cure compiler/runtime defects. The ONE exception, exercised once below: fixture-, xfail-, or
instrument-level repairs (a bad `.ref`/`.std`, a broken DONE-WHEN, a runner bug) stay this seat's own
to fix directly. Zero `src/` changes this pass; one `scripts/` (test runner) change, three new corpus
fixtures, two new QUEUE rows, two witness-additions to existing rows.

## 1. INSTRUMENT BUG, FIXED DIRECTLY: `test_icon_jcon_suite.sh` never gave programs a cwd where their
own relative file-opens resolve

`fncs1.icn` opens its own `.dat` companion by a bare literal (`open("fncs1.dat")`) — normal JCON style,
since real `addtest` presumably runs from inside the test directory. This script never `cd`s anywhere;
it runs with whatever cwd the caller had (documented usage: from `SCRIP/`), so that `open()` always
failed, cascading into a 147-line wrong-output diff that looked exactly like a real compiler defect.
Confirmed by direct A/B: same invocation, only cwd changed, diff went from 147 lines to 0.

**Fix** (`scripts/test_icon_jcon_suite.sh`, SCRIP `134ca56f3`): each test now executes from its own
`$WORK/<name>.rundir/`, with the `.dat` companion (if any) copied in under its own basename — never
`$CORPUS` itself, since a program that WRITES a scratch file by relative name (`loadfunc.icn`'s
`tmp.icn`/`foo.baz`) must never be able to touch the tracked corpus working tree. Scoped only to the
already-modeled `.dat` convention, not every possible literal filename a program might reference (see
`recent.icn` caveat below).

**Board effect**: m3 44→45, m4 41→42. `fncs1` FAIL→PASS both modes; CRASH/HANG counts unchanged in both
modes, confirming nothing else moved (verified via a full clean re-run, tail-untruncated).

**Sanity-tested both ways**: ran with the fix (fncs1 passes, others unchanged) and confirmed the
pre-fix script genuinely reproduces the 147-line diff (not a fluke of my manual test's own cwd).

## 2. NEW WITNESS + QUEUE ROW: `sortf(x, &null)` throws on a heterogeneous-type list

`recent.icn`'s `test()` (line 263, first arm of `every test(&null | 1 | "2" | ...)`) calls
`sortf(data, &null)` where `data` mixes two record types, a plain list, and an integer. SCRIP throws
`ERROR 022 -- Undefined function called`, both modes; real Arizona icont/iconx sorts it fine
(`list_3(5)` then `list_4(5)` for the set variant). Control-arm isolated: an all-same-record-type list
sorts fine under `sortf` with both `&null` and an explicit field index — the trigger is specifically
comparing across DIFFERING types with no field selector.

This is the DOMINANT cause of `recent.icn`'s own FAIL (~418 of ~443 expected lines lost to this one
call) — NOT the cwd-sensitive `open("recent.dat")`/`open(".")` calls earlier in the same program, which
turned out to be unreachable this pass (main() calls the sortf-triggering path first; that later code
never executes long enough to matter). Flagging for whoever cures this: `recent.icn`'s own diff also
shows a `sort(data)` (no field, same heterogeneous mix, called via plain `sort()` not `sortf()`)
reordering ONE element vs. oracle — likely the same comparator family, not chased to ground.

Witness: `corpus/tests/icon/icon_sortf_mixed_type_default_compare_undefined_function.{icn,ref}`
(corpus `06b5d4aac`). Minted: `icon-jcon-class-sortf-heterogeneous-type-default-compare-throws`
(rank 1, hq_B).

## 3. NEW WITNESS + QUEUE ROW: `sort()` on a zero-field record throws

`sorting.icn`'s `rectest()` (line 52, `wlist(sort(r0()))` where `record r0()` has zero fields) throws
the same `ERROR 022`, both modes; real Arizona returns `list_1(0)` (an empty list). Isolated precisely:
constructing the zero-field record works and prints correctly (`record r0_1(0)`); only `sort()` on the
resulting instance fails — points at an edge in sort's per-field iteration/dispatch when field count is
exactly 0, not a general record-handling gap. This single call aborts the rest of `sorting.icn`'s `main`
(`rectest`/`tbltest`/`copytest`/`messtest` never run), almost certainly the dominant contributor to that
program's 494-line diff — not confirmed further past this isolation.

Witness: `corpus/tests/icon/icon_sort_zero_field_record_undefined_function.{icn,ref}`
(corpus `e935f1913`). Minted: `icon-jcon-class-sort-zero-field-record-throws-undefined-function`
(rank 1, hq_B).

## 4. NEW WITNESS ADDED TO AN EXISTING ROW: `copy()` with zero arguments

`fncs.icn`'s `p1()` (line 15, `copy() ----> &null`) calls `copy` with NO arguments (a plain short call,
not a comma-marked gap like `seq(,4)`) — SCRIP throws `ERROR 022`; real Arizona returns `&null`. This
single call truncates ~444 of `fncs.icn`'s ~452 expected lines. Possibly the SAME class as the already-
minted `icon-jcon-class-omitted-leading-arg-not-null-coerced-to-builtin-default` (that row's own GOAL
text already speculates a broad blast radius across "any builtin documenting an omittable-defaults-to-X
argument"), or a genuinely separate code path (Icon's "fewer args than declared" is ordinarily just a
shorter call, no AST placeholder needed, unlike a comma-marked gap) — not resolved here, added as a
LEDGER witness on that row for whoever cures it to judge.

## 5. RE-CONFIRMED, NO NEW INFORMATION: `large.icn` is the already-known bignum gap

`111111111111111111111` (a 21-digit literal) round-trips through SCRIP as if it were wrapped to int64
range — the already-scoped `icon-bignum-arithmetic-not-implemented` row already names `large.icn`
explicitly. Added a one-line LEDGER re-confirmation; no new mint. ⚠️ Flagged, not merged: a SECOND FREE
row, `icon-arizona-class-bignum-not-implemented` (also hq_B), appears to be the same class from a
different suite's census — worth hq_B's dedup attention, not chased further (outside this row's lane).

## DIFF-SIZE SWEEP STATUS OF THE FORMERLY-"GENUINELY UNEXAMINED" BUCKET

`loadfunc` (104): confirmed entirely unimplemented (`grep -rn loadfunc src/` — zero hits) AND
fundamentally JVM-specific (loads precompiled `.zip`/Java-bytecode procedures by name, shells out to
`jcont` to compile+load at runtime) — no real analog for a natively-compiled x86 backend. Flagging as
likely permanently out of scope rather than a normal unimplemented-builtin gap; not minted as a fresh
row (no existing row found naming it either — leaving that judgment call to hq_B rather than guessing).
`fncs1` (147): CURED via the instrument fix above. `fncs` (454): dominant cause isolated to §4.
`recent` (430): dominant cause isolated to §2. `large` (434): confirmed §5. `sorting` (494): dominant
cause isolated to §3. Every entry from the 10th pass's own "genuinely unexamined" list has now been
walked at least to a first isolation; none required a compiler fix I was positioned to make myself.

## BOARD

Fresh, post-fix, post-rebuild (SCRIP `7481d1337`+rebuild, corpus `0d87acbfb`): **m3 PASS=45 FAIL=25
CRASH=8 HANG=3, m4 PASS=42 FAIL=30 CRASH=6 HANG=3 / 81** (m3 44→45, m4 41→42; both deltas are `fncs1`
alone — everything else held). DONE-WHEN still short: m3_pass=45 of needed ≥50. 11 `icon-jcon-class-*`
rows total now (1 closed, 10 FREE, all hq_B).

See task file `icon-jcon-suite-39-non-pass-censused-by-class-and-cured.task.md`'s 11th-pass `## NEXT`
for the live cursor.
