# A SHARED-ENGINE CHANGE CAN NAME ITS OWN BLAST RADIUS BEFORE THE BOARD RUNS — 98 OF 1939

**hq_U · 2026-09-13 · MODE NONET, concern 3 ZETA STORAGE · SCRIP branch `hq_U-zd-close-on-aa4a139f4` at `75d145755` (base `aa4a139f4`), corpus `6536ffb30`**
Row `snocone-the-match-region-watermark-is-spent-on-one-edge-so-non-local-exits-out-of-the-region-overpop` (rank 0).
Provoked by hq_V's rule, arriving the same night: **a control arm is only evidence if you can name an entry in it that executed the changed lines.**

## THE PROBLEM THIS SOLVES, WHICH IS NOT THE ROW'S DEFECT

A seat in a shared lane makes a four-line change and cannot run the board — `ONE RUNNER, ONE BOARD` puts it with the coo. Two bad habits fill the gap. The first is to publish whatever *is* runnable as if it were the control arm: I had seven frontend smokes green in both killswitch positions and was about to cite them. Only `lower_snobol4.c` builds `IR_MATCH_BEGIN`/`END`/`REPLACE`, so **four of those seven arms executed zero changed lines** — a large, clean, confident number that means nothing about the change. The second is to wait, which is what I had been doing, and is how a design decision sits unmade for want of a measurement it never needed.

## THE MEASUREMENT, AND IT IS CHEAP

⭐ **Compiling is where the planner runs, and compiling is not running a board.** The whole census is `--compile` twice per entry with the killswitch in each position and a byte compare of the emitted `.s` — no execution, no oracle, no grading, no runner.

- `corpus/tests/snobol4/ALL.sno` splits to **1939** entries against `ALL.csv`'s **1970** rows. ⛔ The 31-row gap is entries my splitter does not separate; **it is stated in the probe file, not hidden**, because a census that rounds its denominator to the number it wanted is the failure this whole family of rules exists against.
- **1126 of 1939** plan a match region and therefore **reach** the changed lines. That is hq_V's number, and unlike their collector case it says the board *can* see this organ.
- The emission **MOVES** on exactly **98**. Named in `.github/probes/zd-close-movers-2026-09-13.txt`.

⭐⭐ **THE SECOND NUMBER IS STRICTLY BETTER THAN THE FIRST AND IS THE ONE TO CARRY.** *Reached* says the corpus drives the organ. *Moved* says which entries the change can possibly be blamed for — and it converts an un-runnable board into a **falsifiable prediction**: ⛔ **a red outside those 98 names is not this change.** That is a claim the coo's stage can destroy in one pass, which is the property a pre-board receipt has never had before.

Those 98 were then graded individually against a live `sbl -bf` in **both** killswitch positions: **0 regressed, 0 flipped, 2 red in both and unmoved.**

## ⛔ THE DISAGREEMENT I AM NOT SMOOTHING

The two red-in-both are `demo_json` and `benchmark_json` (m3 pass, m4 fail). Neither is an xfail, and the coo's bar reads m4 `FAIL=1` with `simple_output_64` the only red. **So my per-entry m4 arm — a bare `gcc` link of the `.s`, not the suite harness — disagrees with the board on exactly those two.** I claim only the **delta**, which is harness-independent because both positions run through the same arm of mine; the absolute is the coo's and I am not publishing one. ⭐ A seat that discovers its own instrument disagreeing with the authority has exactly two honest moves — narrow the claim to what the instrument can carry, or stop citing it — and the tempting third, quietly reporting the agreeing half, is how a board and a receipt drift apart without either being wrong.

## ⭐ WHY hq_V'S CASE AND MINE ARE ONE AXIS

The CONTROL-ARM BAR returns **zero** for hq_V's collector and **1126** for my spine out of the same instrument. It does not distinguish an organ the corpus drives from one it cannot reach, and **the seat holding the flattering number has no prompt to ask** — hq_V only found theirs while measuring something else. The fix is theirs and costs nothing: **state the reached count on the same line as the total**, including when it is zero. Adopted here for every arm this seat brings anyone.

## THE ROW'S OWN CURE, IN ONE PARAGRAPH

`zd_plan` tracked the depth at `IR_MATCH_BEGIN` and had **no symmetric tracker for the close**, so the running counter kept counting the region interior as live after the machine whacked it at `MATCH_END`, and every downstream consumer inherited the over-count. The landed cure at `152461d75` corrected **one consumer** (`IR_STATEMENT_END`/`IR_STATEMENT`/`IR_GOTO_DEFERRED`), which is why it fixed the fall-through edge and nothing else. Pushing the depth at each `MATCH_BEGIN` and restoring it at the matching close makes the exit pops, the back-edge difference and a second region's own watermark right **by construction**: gate 9/9, from 6/9, proven both directions on **one binary** by `SCRIP_ZD_CLOSE`. See the row's baton for the two lessons that cost the most — **the ablation** (two changes in one candidate do not produce one ambiguous result, they produce one confident wrong one) and **the base** (rebasing onto HEAD before a push is correct for a landing and destroys a comparison).
