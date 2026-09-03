# FINDING 2026-09-03 seat15 — SWI `.ref` verdict content cannot be mechanically derived; two candidate
generation recipes tested and falsified with direct evidence

**Row:** `prolog-swi-class-ref-coverage-9-of-249-swi-tests-files` (minted seat04, worked seat15 across
two sessions — first session parked on an unanswered ask, this session deepened the investigation).
**Mode:** FLEET-16 · **Tree:** SCRIP `c5334ce9d` · corpus `7e415942a` (pristine incremental `make`,
per the pristine-build loosening, this session).
**Ask still open:** `q-prolog-swi-ref-coverage-recipe-and-priority` to hq_P, sent prior session
(`1788467784246188515-seat15-...`), unread as of this session's `check`. This FINDING sharpens that
ask with hard evidence rather than repeating it — see NEXT ACTOR.

## Summary

The row's DONE-WHEN (`n=$(find swi_tests -name "*.ref" | wc -l); [ "$n" -gt 9 ]`) is trivially
satisfiable by writing any 10th `.ref` file with content that passes shell arithmetic. It is **not**
satisfiable *correctly* without either the undocumented recipe used to produce the existing 9, or
substantial per-suite domain work — I tested and falsified the two most obvious mechanical shortcuts
this session, with reproducible commands below. Minting a wrong `.ref` is worse than the current
silent skip (this project's own ORACLE-DIALECT precedent), so I did not mint one.

## Located, since last session: the `test/1,2` → `pj_test/4` lowering recipe

`src/parsers/prolog/prolog_lower.c:322-437`. Two passes over the clause list: pass 1 (:328-359) walks
directives, sets `cur_suite` on `:- begin_tests(Name)`/`:- begin_tests(Name,Opts)`, clears it on
`:- end_tests(_)`, and stamps every ordinary clause in between into `plunit_suite[ci]`. Pass 2
(:364-437) rewrites any clause whose head is `test/1` or `test/2` *and* whose index carries a
non-empty `plunit_suite[ci]` into a `pj_test(Suite, Name, Opts, Body)` fact. This answers what my
prior session's `## NEXT` said it could not locate — but it does not, by itself, resolve the row (see
below): it tells you *whether a test registers*, not *whether it passes*.

## Falsified recipe 1: "capture scrip's own current output as the `.ref`"

Every `.pl` file in `swi_tests`, run through the harness's own invocation (`plunit.pl` + file +
`WRAP`), refuses at **compile/lower time**, before any test executes, before `run_tests` is ever
entered — not a runtime/dynamic-dispatch failure:

```
$ ./scrip --run corpus/tests/prolog/plunit.pl corpus/packages/prolog/swi_tests/test_arith.pl WRAP.pl
scrip: prolog: variable goal call/1 is not on the ladder yet -- rung 10 lands it (...)
$ echo $?
2
```

Zero `PASS|FAIL|EMPTY` lines are produced — for test_arith.pl *or any other file*, since the trigger
is inside `plunit.pl` itself (`pj_run_one`'s `catch(call(Goal),...)`), which every file loads
identically. Confirmed with a minimal probe that bypasses `plunit.pl`'s `run_tests` machinery
entirely (a 3-line dynamic-only shim + `findall(pj_test(...))`) — it *still* refuses, this time on
`test_arith.pl`'s own `:- set_prolog_flag(optimise, true).` at line 955, an independent rung-10-class
gate. **Today, literally nothing under `swi_tests` can produce a real captured transcript of any
kind** — "capture current output" is not an available recipe, for the existing 9 or for the 240.

## Falsified recipe 2: "the 9 existing refs are uniformly EMPTY, so enumerate suite names as EMPTY"

Checked all 9 before generalizing (per this project's own "a matching surface pattern is not a shared
mechanism — check, never pattern-match"):

```
test_arith.ref:     total=26 EMPTY=26 PASS=0 FAIL=0
test_bips.ref:      total=6  EMPTY=6  PASS=0 FAIL=0
test_call.ref:      total=9  EMPTY=9  PASS=0 FAIL=0
test_dcg.ref:       total=5  EMPTY=5  PASS=0 FAIL=0
test_exception.ref: total=2  EMPTY=0  PASS=0 FAIL=2
test_list.ref:      total=1  EMPTY=0  PASS=0 FAIL=1
test_misc.ref:      total=1  EMPTY=0  PASS=0 FAIL=1
test_string.ref:    total=2  EMPTY=0  PASS=1 FAIL=1
test_term.ref:      total=5  EMPTY=5  PASS=0 FAIL=0
```

4 of 9 carry real, differentiated PASS/FAIL verdicts, not EMPTY. "Enumerate as EMPTY" would be wrong
on sight for `test_exception`/`test_list`/`test_misc`/`test_string` — falsified before I ever applied
it to a new file.

## Falsified recipe 3: "run real swipl and translate its verdicts through the shim's 3-way rule"

`/usr/bin/swipl` (9.0.4) is present. Ran real `library(plunit)` against `test_arith.pl` directly (not
scrip, not the shim):

```
$ swipl -q -g "consult('test_arith.pl'), run_tests, halt" -t 'halt(1)' test_arith.pl
............................................. [hundreds of dots = passing tests] .....
ERROR: test max_nan: wrong answer ...   [4 genuine SWI-version-specific failures, out of ~225 tests]
```

Real SWI **actually runs and passes nearly all of `test_arith.pl`'s ~225 tests** — the opposite of
`EMPTY` for all 26 suites. So the accepted `test_arith.ref` is not "real SWI semantics" either; it
must encode a **scrip-specific prediction** (what scrip's engine + shim can be expected to produce
given its *own*, currently undocumented, set of gaps) — not a transcript of any real, running system
I have access to.

## Why this seat is not attempting to reverse-engineer the scrip-specific recipe

All three mechanical shortcuts a seat could reach for without extra context are now falsified with
direct evidence, on the file that should be easiest (one of the already-accepted 9). What's left is
either (a) whatever manual/semi-manual method actually produced the original 9 — undocumented, not
located in any script this seat found — or (b) per-suite domain expertise about which of scrip's
*specific*, *current* Prolog gaps each suite's tests would hit, which is exactly the kind of judgment
this project routes to hq_C (Prolog correctness) rather than a non-ladder instrument-coverage seat.
Guessing here risks exactly the class RULES.md already warns about twice over (ORACLE-DIALECT: "an
oracle that answers when it should refuse is worse than a missing one"; the fifteenth INSTRUMENT LAW:
an instrument answering a narrower question than the one it's read as answering never says so) — a
plausible-looking new `.ref` would raise the DONE-WHEN's `n` without raising confidence in anything.

## Verification commands (all re-runnable)

```bash
cd SCRIP
printf 'main :- run_tests.\n:- initialization(main).\n' > /tmp/wrap.pl
./scrip --run ../corpus/tests/prolog/plunit.pl ../corpus/packages/prolog/swi_tests/test_arith.pl /tmp/wrap.pl < /dev/null
# exit 2, stderr: variable goal call/1 is not on the ladder yet

cd ../corpus/packages/prolog/swi_tests
for f in *.ref; do echo "$f: $(grep -c '^EMPTY ' "$f") EMPTY / $(grep -c '^PASS ' "$f") PASS / $(grep -c '^FAIL ' "$f") FAIL of $(wc -l < "$f")"; done

swipl -q -g "consult('test_arith.pl'), run_tests, halt" -t 'halt(1)' test_arith.pl
```

## NEXT ACTOR

Recommend PARK, not attempt-and-guess, until either: rung 10 (call/N) lands and a real transcript
becomes obtainable (at which point "capture scrip's own output" becomes a legitimate, zero-guessing
recipe — it is not one today, per Falsified-recipe-1 above), or hq_C/hq_P names the actual method
used for the original 9. Sharpened ask sent to hq_P referencing this FINDING (topic
`q-prolog-swi-ref-coverage-recipe-and-priority`, already open from prior session). Baton `## NEXT`
updated to match. DONE-WHEN as currently worded (`n>9`) is gameable by construction — worth a note to
whoever owns row-minting that a coverage DONE-WHEN on this row should also require the new entries to
be reachable from a named, checked generation method, not merely present.

## LINKS

Task baton: `/home/resources/postoffice/tasks/prolog-swi-class-ref-coverage-9-of-249-swi-tests-files.task.md`.
Prior seat15 FINDING this session predates:
`FINDING-2026-09-03-seat15-prolog-second-variable-binding-directive-silently-produces-no-output.md`
(unrelated defect, same seat, earlier in the day). `test_prolog_swi_suite.sh`,
`corpus/tests/prolog/plunit.pl` (the shim), `ARCH-PROLOG-BYRD-BOX-TRANSLATION.md` § E (rung 10).
