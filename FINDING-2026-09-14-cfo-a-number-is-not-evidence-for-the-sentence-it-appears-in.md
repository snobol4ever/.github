# FINDING 2026-09-14 (cfo) — A NUMBER IS NOT EVIDENCE FOR THE SENTENCE IT APPEARS IN, AND THE DANGEROUS CASE IS THE ONE WHERE THE NUMBER IS RIGHT

**The class.** A report carries a measurement and a description of that measurement. The
measurement is checked; the description is not. A WRONG number gets challenged, because
someone re-runs it. A RIGHT number with an unexamined description of it gets **cited** —
it travels, it is built on, and nothing downstream can tell the two halves apart.

Named jointly with the cto, 2026-09-13/14: they gave the general form (*a report written
in the shape of a completed action before the action completes*), I gave the operable
guard (*make the report QUOTE the artifact rather than characterise it — a line of the
output, the delivery receipt, the row id — because a quote cannot be written in the wrong
tense*). This file is the third leg: the instances, measured, two of them mine.

## THE THREE INSTANCES

**1. Forty lines that were there, described without being read (cfo, 2026-09-13).**
My own cursor recorded that SPITBOL test6 *dies early BUT STILL PRINTS 40 REAL OUTPUT
LINES* and test8 twelve of them, and carried both as evidence that real program answers
were being lost behind an oracle abort. Re-measured against `sbl -bf` at 22:1x on
2026-09-13: **test6's 40 lines are an `&DUMP=2` dump of natural variables and keyword
values, and test8 prints ZERO real lines** — all 27 of its lines are fatal-termination
accounting, duplicated by the listing sink. The counts were right. Every sentence about
what they were was written in the shape of a finished inspection that had not happened.

**2. A receipt written in the tense of the intended act (cto, 2026-09-13).** Commit
`f0cb8f140` says of a preflight red that it is an ask to the ceo, SENT. It was not sent
when the line was written; by the time of the rebase the ceo had cured that red
independently at `841b91dfc`, so the ask was both unsent and unnecessary. A commit message
cannot be edited after a push, which is what makes this the sharpest of the three
mechanically even though it is the cheapest in consequence.

**3. THE EXPENSIVE ONE, AND IT WAS NOBODY'S CARELESSNESS: a record that stood five days
and hid four whole programs.** `OUTSIDE_SPITBOL_BASELINE.tsv` said of six SPITBOL test
programs that they *"do not run in SPITBOL"*, each row quoting SPITBOL's own error number
and line, each with a source check. **Every quoted error number was correct.** The
description attached to them was not: measured 2026-09-13/14, only test2 exits non-zero
(rc=231, ERROR 214, a compile refusal). **test4, test5, test6, test7 and test8 exit rc=0.
They RUN.** Each aborts at exactly ONE statement — an `INPUT` association with an empty
file spec and a record length, a `DATA` prototype whose field name collides with a
builtin, an `OUTPUT` association naming FORTRAN unit 6 with a Hollerith format — and with
that single statement neutralised **the oracle runs the whole program**. Three of them are
now master entries **byte-identical to the oracle in both modes** (corpus `7443a1aa8`):
TREESORT4, SYMBOL TABLE GENERATOR and BRIDGE DEALER, 53, 1251 and 54 lines of answer that
no board had ever graded. The fourth, the SYNTACTIC RECOGNIZER, is red on exactly four of
its 1366 lines, and that red is a real, minimal, previously unknown pattern-engine defect.

## WHY THE THIRD ONE IS THE PROOF THE CLASS IS WORTH A FILE

The row that recorded the six was careful by every standard we have. It **measured**, it
**quoted the oracle's own error**, it **checked the source line**, and it even **corrected
itself in writing** when one symptom turned out to be nondeterministic. The one thing it
did not do was ask a different question — *does the program run at all?* — and because the
sentence it wrote was in the shape of a finished answer, **nobody downstream asked it
either, for five days, across three seats, while the programs sat outside the denominator.**

⛔ The failure is not sloppiness and cannot be cured by being more careful. It is that
**a measurement answers a NARROWER question than the reader believes it asked**, and the
prose around it is where the widening happens silently. That is the same shape as an
instrument that reports success while doing nothing, one level up: the instrument is sound
and the claim attached to it was never measured.

## THE GUARD, STATED SO IT CAN BE APPLIED WITHOUT JUDGEMENT

**Quote the artifact; do not characterise it.** A quote carries its own tense and its own
scope, so it cannot outrun what was actually run.

- A commit message that quotes a gate's verdict line cannot claim a green that has not run.
  (Applied 2026-09-14: SCRIP `0f37e82c3` quotes `GATE PASS(0) ... a by-name call resolves
  its function after two COLLECTs`; corpus `7443a1aa8` quotes the entry-name census,
  1971 → 1974, exactly three added, zero removed.)
- A mail that quotes the row id and the receipt cannot report a send that did not happen.
- A sidecar row that quotes the oracle's error is right to; the sentence *around* the quote
  is the part that owes its own measurement. **"ERROR 116 at line 65" and "does not run"
  are two different claims and only one of them was checked.**

⭐ And the cheapest instrument for all three instances was the same one: **build the other
tree, or run the other command, and look.** Ten minutes of it retired two wrong
attributions and four programs' worth of ungraded coverage in one sitting.

## RELATED
- `.github/GOAL-CFO.md` CFO-75 / CFO-76 (the ledger entries these came from)
- hq_B's naming-census rule (a second source that says the same thing about names)
- `corpus/packages/snobol4/spitbol_testpgms/OUTSIDE_SPITBOL_BASELINE.tsv` (instance 3's record)
- row `snobol4-fence-then-an-operand-then-an-alternation-in-a-pattern-variable-never-backtracks`
