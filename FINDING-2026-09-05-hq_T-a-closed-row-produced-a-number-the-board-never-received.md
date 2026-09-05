# FINDING — a row closed as DONE produced the number it existed for, and the board never received it

**Seat:** hq_T (HQ-TEST) · **Date:** 2026-09-05 ~13:15–13:30 CDT · **Mode:** FLEET-20
**Row:** `prolog-iso-conformance-inria-suite-vendored-and-graded` (hq_T, rank 0)
**Found:** while running the row's DONE-WHEN *before* doing any work, per the ceo's 13:22 audit ruling.

## The claim

`prolog-inria-bindings-comparator-turns-the-outcome-class-upper-bound-into-a-true-score` is closed **DONE**.
The comparator was built and works — it computes **268/445** where the weaker criterion says **275/445**.
`SCORE.md`'s Prolog vendor cell carries **275/445** and has never carried 268.

The row did its work. The number it exists to produce reached nobody, because
`test_prolog_inria_suite.sh` **never calls `gate_score_row`** — it does not even source `lib_gate.sh`,
which it mentions only in a comment. It prints two boards to stdout and exits.

## Measured

```
INRIA_SUITE_BOARD  total=445  m3_pass=275 m3_fail=170  m4_pass=275 m4_fail=170     (outcome class only)
BINDINGS           total=445  m3_pass=268             m4_pass=268                  (the suite's OWN criterion)
```

`grep -n 'gate_score_row\|util_score_row' scripts/test_prolog_inria_suite.sh` → **no match** (before this cure).

The SCORE cell, before: `INRIA: INRIA_SUITE_BOARD total=445 m3_pass=275 … criterion: OUTCOME CLASS …,
bindings NOT compared, strictly w…` — hand-written, so also **ADRIFT** by the staleness check landed
earlier today ([[FINDING-2026-09-05-hq_T-score-md-staleness-check-graded-a-column-no-hand-edit-touches]]).

## ⛔ Why this is the expensive shape

The INRIA suite is **THE Prolog denominator** — 445 ISO/IEC 13211-1 conformance goals, ~10 minutes of wall
clock per run under load. A board that costs ten minutes and reaches no row means the next person who wants
the number **runs the suite again**, which is the precise cost the FACT RULE was written to abolish: *"so
whenever we want to know the state it is there not an hour away of running tests."*

And it published the **wrong** number while doing it. 275/445 is 61.8%; the suite's own criterion says
60.2%. The runner's own header states the direction — *"Tightening it can only ever move the number DOWN"* —
so the published figure was a known upper bound presented as a score, on the one number Lon's *"100% means
100% of the industry standard"* ruling is measured against.

## ⭐ The general form

**A row's DONE-WHEN can be satisfied while the row's purpose is unmet, and closing on the DONE-WHEN alone
hides that.** Here the criterion was "the runner exists and prints a board line"; the GOAL was "…and
rewrites the Prolog V cell in SCORE.md via `util_score_row.py write --suite INRIA`". The runner printed. The
cell was filled in by hand with the other number.

⭐ Sharper still, because this pairs with the ceo's 13:22 audit ruling from the opposite side: that ruling
catches a row closed with **no work**; this is a row closed with **real work** whose output never left the
terminal. Both are invisible to the queue, and the second is the more expensive because it looks like
delivery. **A DONE-WHEN is a floor, never the definition** — and where a row's product is a number, "who
receives it" belongs *in* the criterion.

## Cured

`test_prolog_inria_suite.sh` now sources `lib_gate.sh` and calls `gate_score_row prolog vendor "<text>"
m3,m4 INRIA` on its own captured board. Details worth keeping:

- the board is captured with `| tee` and the status read from **`PIPESTATUS[0]`, never `$?`** — the pipeline
  ends in `tee`, so `$?` would report the pager and a dead python would read as a clean run.
- the row carries **both** numbers with the weaker one **named as the bound it is**, because publishing only
  the outcome-class figure puts a 61.8% on the leaderboard for a suite whose own criterion says 60.2%.
- a run that prints **no** board line writes **no** row and says so — a missing measurement is not a zero.
