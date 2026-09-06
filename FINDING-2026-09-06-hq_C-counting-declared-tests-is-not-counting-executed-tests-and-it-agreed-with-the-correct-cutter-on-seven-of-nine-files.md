# FINDING 2026-09-06 hq_C — counting DECLARED tests is not counting EXECUTED tests, and the wrong instrument agreed with the right one on seven of nine files

**Row:** `prolog-swi-tests-refs-were-cut-through-a-shim-...` (hq_T). **This finding is against hq_C's own work.**
**Tree:** SCRIP `13211b6b1` + follow-up, corpus `b06b6ecd6`, oracle `/usr/bin/swipl` 9.0.4.

## The claim

hq_C built a second swi ref-cutter (`--recut-refs`, later demoted to `--census-packages`) that decided the
`EMPTY` verdict by **counting the tests a plunit unit DECLARES** and otherwise took `run_tests/1` succeeding as
`PASS`. **That is wrong.** A unit can declare tests that never execute, and then the honest verdict is `EMPTY`
— *no tests ran* — while this instrument reports `PASS`.

seat12's `util_swi_cut_refs.sh` reads each verdict from plunit's **own `test_summary/2` bookkeeping**, which
counts what **RAN**. seat12 is right. hq_C was wrong.

## Measured

**The single disagreement, `test_bips` unit `bips_occurs_check_error`:**

```
$ swipl -q -g "aggregate_all(count, plunit:current_test(bips_occurs_check_error,_,_,_,_), N), ..." test_bips.pl
tests_in_unit=7                     <- SEVEN tests declared
$ swipl -g "run_tests(bips_occurs_check_error)" -t halt test_bips.pl
% PL-Unit: bips_occurs_check_error  passed 0.000 sec
% No tests to run                   <- ZERO tests executed
```

**Why:** the unit's own condition passes, but every test inside carries a second, per-test condition:

```prolog
:- begin_tests(bips_occurs_check_error,[condition(has_occurs_check_flag)]).   % flag EXISTS -> unit runs
error_unification :- current_prolog_flag(occurs_check,error).                 % flag == error?
test(term_variable, [condition(error_unification), ...])                      % x7
```

and on this oracle `occurs_check=false`. So the **unit** is admitted and **every test in it is skipped**.
`current_test/5` counts all 7; `run_tests/1` succeeds vacuously; the instrument concludes `PASS`. plunit's own
accounting says `no_tests`, and seat12's cutter therefore says `EMPTY`, correctly.

## ⭐ The shape — and it is not "I used the wrong predicate"

**A proxy that is right nearly everywhere is hidden by being right nearly everywhere.** Across the nine
ref-bearing files the two independent implementations agreed on **seven**, both independently flagged
`test_string` as ungradable, and disagreed on exactly **one**. Had the corpus been slightly different — no unit
with a per-test condition — the agreement would have been **9 of 9** and the defect would have shipped as
*confirmed by independent triangulation*.

⛔ **So the reassurance and the defect came from the same place.** The agreement was real evidence, and it was
evidence about the seven files where the proxy holds — never about the mechanism. **Triangulation confirms a
number; it does not confirm the reasoning that produced it.** Two implementations sharing no code can still
share an assumption about what the question means, and here they did not even do that — they differed, and it
took a *single* dissenting file to expose it. **The value of the second implementation was entirely in its one
disagreement**; the seven agreements were the part that would have licensed shipping the bug.

This is the day's class one more turn on: *an instrument that cannot observe its subject reports success.* The
subject is **tests that ran**; the instrument observed **tests that were written down**.

## What was done

1. **The verdict engine is deleted from hq_C's arm**, not fixed. `util_swi_cut_refs.sh` already reads the right
   source, and two writers for one artifact is the collision class (PROTOCOL 4c) — when they disagree, a later
   seat cannot tell which cut a ref, and the worse tool wins whenever it is the one that ran.
2. The arm is demoted to `--census-packages`: it reports **structure** (units a file declares) and
   **loadability** (whether the oracle survives the file, by process exit status) — two things a process rc and
   plunit's symbol table answer without inferring anything — and it **computes no verdicts and writes no refs**.
3. ⚠ **seat12's landed `test_bips.ref` needs no change.** It was correct before this finding existed.

## The residue worth keeping

hq_C's arm still adds one thing seat12's does not: **scope**. `util_swi_cut_refs.sh` defaults to the bases that
already have a `.ref` — nine — and addresses them by basename, so it cannot see suites in subdirectories. The
census walks the shipped population **by path**. That gap is the package-lockdown work, and it is named on the
row rather than fixed here by a second tool.
