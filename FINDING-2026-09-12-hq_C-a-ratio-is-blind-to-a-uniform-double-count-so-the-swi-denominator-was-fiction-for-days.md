# FINDING — a ratio is blind to a uniform double-count, so the SWI denominator was fiction and the only number anyone read was right

**Seat:** hq_C · **Date:** 2026-09-12 · **Row:** `prolog-swi-runner-prints-one-labelled-board-line-and-one-progress-row-per-program-per-mode` (CEO-601, on COO-60)
**Trees:** SCRIP `d2be2c928` · corpus `5b6dd7ab2` · .github `37df3528` · oracle-free (the suite grades SCRIP against cut refs)

## What the brief asked, and the thing that was underneath it

CEO-601 named three defects in `test_prolog_swi_suite.sh`: it printed two fractions, passed no
`--suite-pass`, and wrote 20 progress rows against a 118-line board. All three were real. Measuring them
surfaced a fourth that subsumes the third:

⛔ **THE DENOMINATOR WAS 59 SUITE-LINES COUNTED TWICE.** The grading loop walked
`find "$SWIT" -name "*.pl"` **recursively** and kept any file whose **basename** had a sibling `.ref` at the
top level. All ten graded basenames exist twice — once beside their ref, once inside the vendored upstream
`core/` tree. Every ref was therefore graded from **two different paths**, and both results were added to the
same `PASS` and the same `TOTAL`. "118 suite-lines over 20 files" was 59 over 10.

⭐ **THE PERCENTAGE HID IT PERFECTLY, AND THE PERCENTAGE IS THE ONLY THING THE RUNNER GATES ON.** `PASS`
doubled along with `TOTAL`, so `Coverage: N%` was correct throughout — and its `>=80%` gate behaved exactly
as it should have. **A ratio is blind to a uniform double-count by construction.** Every instrument pointed
at this suite was reading the one quantity the defect could not disturb.

⛔ **AND THE TWO COPIES ARE NOT ALWAYS THE SAME PROGRAM.** `test_string.pl` **differs** between the top level
and `core/`. One ref was being graded against two different sources, and nothing anywhere checked that they
agreed. The honest reading is therefore also slightly BETTER than the old one: run **9/59 = 15.3%** against
`17/118`'s 14.4%, because the `core/` copy was scoring worse against the shared ref. ⭐ **A denominator
correction is not automatically a regression and must not be reported as one.**

⭐ **THE GENERAL FORM: a basename is not an identity in a recursive tree — the path is.** The population of a
suite should be addressed by the artifact that DEFINES membership (here the `.ref`: a ref names exactly one
graded program) and the source graded should be the one that sits beside it. Same family as
`FINDING-…-grade-master-entries-by-origin-never-by-display-name` and the generated-suite collisions: every one
of them is a key that looked unique in the directory someone tested it in.

## A correct refusal upstream of a cell nobody re-measures is indistinguishable from a write

`util_score_row.py` **refused every write this runner attempted**, because the `--text` carried two fractions
and no `--suite-pass` — and the refusal was *right*: which fraction the row means is a judgement, and a helper
must not make one. ⭐ The cell nonetheless sat at a stale number for two days. **The refusal protected the
file and not the reader.** A helper that refuses must be paired with something that notices the refusal;
here nothing did, and the runner exited 0 on its own terms every time.

⛔ The cell was additionally the **wrong tier**: `11/118` was the COMPILE tier of the doubled denominator. The
compile tier still prints as an inventory line — deleting it would trade one wrong reading for a missing one —
but it is not the row.

## Two instrument lessons paid for in this sitting

⛔ **A REFUSAL CLAUSE THAT PRINTS `tail -2` OF ITS CALLEE PRINTS THE FOOTER.** My own DONE-WHEN reported
`REFUSE(2): the swi runner refused --` followed by a load average, because the runner's last two lines are its
tree/machine banner. The real cause was the stale-binary guard (a rebase had touched the Makefile after my
last build) and the ONE RUNNER exemption had fired correctly all along. Cure: `grep -m2 -E
"REFUS|UNPROVEN|not built|older than"` with a `tail -3` fallback — the criterion is unchanged, it just stopped
swallowing the reason. Same family as `FINDING-…-a-refusal-that-drops-the-callees-words-arrives-as-a-red`,
which I had already written and then re-committed from the other side.

⛔ **A SCORE CELL IS MERGED BY RE-RUNNING THE HELPER, NEVER BY HAND.** The first write of this row hit a
rebase conflict against a cell four other seats had moved in the same window (IPL, INRIA, icon, logtalk).
Resolved by taking upstream **whole** and re-running `util_score_row` with the numbers I had measured. **A row
is rewritten by the runner that measured it, and that holds for a merge as much as for a run** — hand-merging
a SCORE cell is precisely how a number nobody measured ends up in it.

## And the row had already been minted six days earlier, invisibly

`prolog-swi-runner-prints-per-unit-per-mode-verdicts-emits-its-inventory-and-declares-its-pair-under-ceo-372`
(coo, CEO-377(d), 2026-09-06, lane hq_T) describes the same two-fraction refusal and the same units-vs-files
split. Its DONE-WHEN is still the **mint placeholder**, so it is one of the permanently-uncloseable rows the
ratchet counts. ⭐ **A row that cannot close is invisible to anyone grepping for work that can** — so the
defect gets re-minted by the next seat who meets it. I nearly did exactly that blind, and only saw it because
`test_gate_baton_donewhen_runnable.sh` printed the old topic while I was checking my own. Parked
`BLOCKED-ON:` the new row; the shape is reported to the ceo, who has folded it into hq_T's mint-refusal cure.
