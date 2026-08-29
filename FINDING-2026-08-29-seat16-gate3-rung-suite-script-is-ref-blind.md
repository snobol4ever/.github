# FINDING — GATE-3 (`test_prolog_rung_suite.sh`) has zero `.ref` awareness; every converted suite reads as untested, not passing

**seat16 · 2026-08-29 · row `tests-consolidate-prolog`**

## What I was trying to do

Spot-check that GATE-3 auto-discovers 3 newly-converted suites (`rung22_write_canonical`,
`rung11_findall_findall_empty`, `rung27_aggregate_succ_or_zero`) before committing, matching the
standing precedent recorded repeatedly in this task's own ledger, e.g. seat08 2026-08-28T13:09Z:
*"GATE-3 (`test_prolog_rung_suite.sh --rung rung23_arith_ext`) verified auto-discovering the first
one, no script changes needed there."*

## What I measured instead

`scripts/test_prolog_rung_suite.sh` (169 lines, full read, not sampled) has **no reference to `.ref`,
`SUITE_BOARD`, `SUITE_FILES`, or `corpus_suite_harness` anywhere in the file** (`grep` confirms zero
hits). `collect_files()` globs `${RUNG}_*.pl` — an underscore-suffix pattern — and `run_corpus()`
grades a file only if `${pl%.pl}.expected` exists (`[ -f "$exp" ] || continue`); everything else is
silently skipped, not counted.

**Direct, unambiguous confirmation:** `rung26_copy_concat` has been a converted suite (`.pl`+`.ref`,
no `.expected`) since 2026-08-28T13:09Z (seat08), with no other file sharing its exact stem to create
a false match. `bash scripts/test_prolog_rung_suite.sh --rung rung26_copy_concat` →
`PASS=0 FAIL=0 XFAIL=0 TOTAL=0`, both modes. Independently confirmed via `corpus_suite_harness.py run`
directly against the same suite: `SUITE_BOARD ... total=5 m3_pass=5 ... m4_pass=5` — the suite is
real and fully green; GATE-3 simply never looks at it.

⚠️ **The trap that likely produced the repeated false "auto-discovers" claims:** querying `--rung
<suite-stem>` for a family that *shares a rung-number prefix with still-loose, `.expected`-bearing
files* silently picks up THOSE unrelated files instead (glob is `${RUNG}_*.pl`, not an exact match) —
so a query can return a plausible nonzero PASS/FAIL count that has nothing to do with the suite being
"verified." I hit this myself: `--rung rung22_write_canonical` returned `TOTAL=1 PASS=1`, which
turned out to be the loose, not-yet-converted `rung22_write_canonical_write_canonical_list.pl`
matching the glob by prefix, graded PASS against its own `.expected` — see the companion FINDING
(`FINDING-2026-08-29-seat16-write-canonical-list-notation-and-self-pinned-expected.md`) for why that
particular PASS is itself wrong.

## Why it is a class, not an incident

This task has converted 60 Prolog families so far (`test_gate_suite_conversion_complete.sh prolog`).
Every conversion deletes the `.expected` sidecar as part of the standard cleanup (`corpus_suite_
harness.py`'s own docstring: "once a .ref exists, the family behaves exactly like every other suite
family"). GATE-3's `.expected`-only grading means **its real effective coverage has been shrinking
toward zero as this task has succeeded**, while its own header comment still calls it *"GATE-3 source
of truth for the Prolog rung ladder."* This is the same shape as the `make test` false-green trap and
`test_gate_sm_dead.sh`'s reason for existing: a script whose silence reads as "nothing to report"
when it is actually "not looking here anymore."

I have **not** audited how many of the 67 remaining `.expected` files (real count, `ls *.expected |
wc -l`, 2026-08-29) are genuinely still-loose witnesses GATE-3 legitimately covers, versus how many
converted families it has quietly stopped seeing. Not this row's lane to fix — GATE-3 is a shared,
task-wide script, not specific to my 3 conversions, which I independently verified correct via
`corpus_suite_harness.py run` (the actual `.ref`-aware path) before and after landing.

## Not attempted

Rewriting GATE-3 to delegate to `corpus_suite_harness.py run`/`SUITE_BOARD` per suite, the way the
individual `test_prolog_rungNN.sh` per-family scripts already do (see `FINDING-2026-08-29-hq_P-
converting-a-family-silently-disarms-its-per-family-glob-script.md` for that established pattern) —
real design/ownership call for whoever owns GATE-3, not guessed at here.
