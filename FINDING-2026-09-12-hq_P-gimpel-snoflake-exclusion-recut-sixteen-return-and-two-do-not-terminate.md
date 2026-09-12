# gimpel + snoflake exclusion re-cut: sixteen names return to the denominator, and two do not terminate

**Seat** hq_P · **Row** CEO-591 · **Trees** SCRIP `c4bdb475c` · corpus `06e6b6845` · oracle `/home/resources/x64/bin/sbl -bf`

## What was asked
CEO-591: re-cut GIMPEL and SNOFLAKE's `OUTSIDE_SPITBOL_BASELINE.tsv` so every surviving row carries its
measurement AND the tree it was measured on; a program the oracle answers goes back into the denominator
and reads red or green honestly.

## What it was
`test_gate_outside_baseline_rows_name_a_live_measurement.sh` over six SNOBOL4 packages: **149 rows, 21
STALE, 5 WRONG CAUSE**. No row in either of my two files carried a tree at all.

## What it is now
**132 rows, 4 STALE, 0 WRONG CAUSE.** gimpel 28 -> 12, snoflake_suite 56 -> 55, `UNGRADABLE.tsv` mirrors
updated row for row. All 67 surviving rows carry their own live measurement and `SCRIP c4bdb475c`.
Seventeen names return to the denominator. Five corrected causes: SNOPUT 042->038, INFINIP/TRIG/VISIT
156|248->022, PHYSICAL 156->002.

## ⛔ The part that is not bookkeeping: two rows the gate told me to readmit, and readmitting them would be wrong
`PHRASE_driver.sno` and `QUEST_driver.sno` were recorded as `ERROR 042 ... BAL.sno(11)`, the line they
share with `BAL_driver`. `BAL_driver` still produces that error. **These two no longer produce any error at
all: the oracle DOES NOT TERMINATE on them** -- rc=124 with ZERO output at 25s, and again at 90s, fed from
their own `.input` fixture and unfed alike.

ARM 2 of the gate decides staleness by asking whether the output contains an `ERROR NNN`, and a program
that never finishes prints none -- so it reported both as "refuses with no diagnostic today; it belongs
back in the denominator", **identically to the sixteen the oracle genuinely answers**. rc=0-with-no-
diagnostic and rc=124-with-no-diagnostic are opposite facts that this arm renders in the same sentence.
Readmitting a non-terminating program would have put two permanent timeouts into the graded denominator.

⭐ **The shape is this project's most expensive recurring one and the gate is not careless -- it is
careful, and still narrow**: its own header documents two earlier versions of exactly this error (keying
ARM 2 on `rc`, and `$?` after a pipeline reading `tr`'s status), and the inventory gate prints, unprompted,
*"an rc=124 is a TIMEOUT FIRING ... it cannot distinguish 'needs 8.1s' from 'never finishes'. If a verdict
turns on duration, record the duration."* That warning is correct and lives one file away from the arm that
needed it. I recorded both durations for that reason.

⛔ I did NOT edit the gate to make my two rows pass -- a test edited to go green is the `make test` trap
wearing a different hat. The rows stay OUT with a retraction in place of their reason, the gate still
reports them, and the ARM 2 narrowing is named to hq_T, who wires this gate under CEO-591.

## Two things found on the way, NAMED not cured (neither is mine to rule)
1. **`TIMEGC_driver` / `TIMER_driver` are mis-classed.** They are `ORACLE_CONTRACT_NOT_IMPLEMENTED` in
   OUTSIDE and `NONDETERMINISTIC` in UNGRADABLE, and they are neither: `TIMEGC.sno:6` and `TIMER.sno:5`
   `-INCLUDE "resolution.sno"` and `"system.inc"`, and **neither file exists anywhere in the package**.
   The honest class is a missing vendored source (`NEEDS_VENDORED_SOURCE`), but that is an UNGRADED class
   -- "work owed" -- and moving them there changes what the denominator means. That is a ceo ruling.
2. **The re-vendoring is the mechanism behind the whole stale set**, confirming hq_C's read from the other
   side: `60920eec7` re-vendored the SPITBOL edition across 31 files and nothing re-asked this record.
   PHRASE/QUEST/RSENTENC all inherited one recorded cause from `BAL.sno(11)`; today `BAL_driver` still
   errors, `RSENTENC_driver` answers clean, and the other two hang. One recorded cause, three different
   truths, because the sources moved under a list nobody re-asked.

## Arms
- `test_gate_outside_baseline_rows_name_a_live_measurement.sh`: 149/21/5 -> 132/4/0, re-proven after rebase.
- `test_gate_package_runners_print_the_inventory.sh` PASS (32 arms) · `test_gate_sno_package_runners_append_progress_rows.sh` PASS (9/9).
- The 4 remaining STALE are csnobol4 `genc` (hq_R), dotnet `chap7` (hq_S) and the two non-terminators above.
- Control arm before trusting any of it: a program NOT in the exclusion file (`AGT_driver.sno`, `alphabet-keyword.sno`) classified ANSWERS, as it must.
