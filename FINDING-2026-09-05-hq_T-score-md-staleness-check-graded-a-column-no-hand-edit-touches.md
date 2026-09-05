# FINDING — `check` graded the Tree column, and every hand-edited cell was invisible to it

**Seat:** hq_T (HQ-TEST) · **Date:** 2026-09-05 ~12:10–12:30 CDT (box clock) · **Mode:** QUARTET
**Row:** `score-md-rows-are-rewritten-by-the-runner-that-measured-them` (hq_T rank 0)
**Found off:** seat13's follow-up on `ruling-supersede-fold-approved-with-a-bound` (a `make test` remainder report), while confirming their claim that nobody had a clean SNOBOL4 corpus reading.

## The claim

`scripts/util_score_row.py check` measured staleness from **one cell per row** — `cells[PROV_COL]`, the
`Tree · box clock · by` column — and from nothing else. So the tree a human reader of a `SCORE.md` cell is
actually looking at had **never been graded**, on any row, since the helper landed.

## Why the premise was reasonable, and where it fails

`write` does stamp provenance: `merge_prov()` keeps one `<column>: <stamp>` clause per measured column in the
Tree cell. If every measurement arrived through the helper, the Tree column would be a faithful index of all
four measured cells and scanning it alone would be sufficient.

It holds for writes **through the helper**. It fails silently for the **hand-edit** — and the board is full of
hand-edits, because the helper landed on 2026-09-03 into a file that seats had been editing by hand for weeks
and are still editing by hand today.

## The witness

`SCORE.md`, snobol4 row, `Master board` cell (measured, before this cure):

- the **cell** reads `⭐ LANE RE-MEASURE 2026-09-05 (hq_P, FLEET-8 opening task, ceo) … on SCRIP `f3f4870d7``
- its **`board:` clause** reads `SCRIP `7d7ff2dc5` · corpus `b6bb5d612` · RT_OPT=-O0 · 2026-09-04 22:25 CDT · hq_B`

One cell, two trees, two measurers, two dates. `check` reported the snobol4 row off nine hashes in the Tree
column and never once printed `f3f4870d7` — the only tree in that cell anyone reads.

Census at the moment of the find, over the whole board: **8 cells adrift** across snobol4, icon, raku and
pascal. Two distinct shapes, both now named:

- the clause stamps a tree **older** than the cell claims (snobol4 `board`, icon `board`, raku `board`, …)
- **no clause names the cell at all** (snobol4 `vendor`, icon `floor`, pascal `vendor`)

## ⛔ The dangerous direction is the quiet one

On the witness both trees were past the threshold, so the verdict survived and only the *attribution* was
wrong — `check` named hq_B for hq_P's number. That is the benign half. Reverse the freshness and it inverts:

- a cell **re-measured by hand onto today's tree** reads STALE off its old stamp → a seat re-runs a suite that
  was already current (the exact cost the FACT RULE was written to abolish: *"so whenever we want to know the
  state it is there not an hour away of running tests"*).
- a cell **left stale beside a freshly-stamped clause** reads **ok** → nobody re-runs anything, and the board
  quietly asserts a number measured on a tree the world has moved past.

A staleness check that cannot see the cell it is grading is the FACT RULE's own failure mode wearing the FACT
RULE's clothes.

## The cure (landed this session)

`cmd_check` now grades **every measured cell plus the Tree column**:

- per column, the cell's **current claim** is the newest tree it names — ranked by commit distance to
  `origin/main`, not by position. A measured cell is a running history (`⛔ SUPERSEDED READING BELOW …`), so
  the trees buried in its prose are retired by construction; ranking by distance retires them without this
  parser having to model the prose that says so.
- **ADRIFT** is reported as its own state, never folded into STALE, because the cure differs: STALE says
  *re-run the suite*; ADRIFT says *the number came in by hand, so the stamp names the wrong tree and the wrong
  measurer*. **A row can be perfectly current and still adrift.**
- vendor-suite clauses (`Snoflake:`, `CSNOBOL4:`, `gimpel:`, `aisnobol:`, `Arizona:`, `JCON:`, `IPL:`, …) have
  no cell of their own and are graded from the Tree column, as before.
- clause keys are no longer truncated to 7 characters — `CSNOBOL`, `port-tr`, `aisnobo` were lossy labels.

## The gate

`test_gate_score_row_rewrites_in_place.sh` **ARM 9**, over a scratch `SCORE.md` (the real board is never
touched; ARM 8 re-asserts that). ⭐ **Two-sided on purpose**: one row is built with the cell claiming a tree
strictly newer than its clause (must report ADRIFT and must grade the *cell's* tree), and a second row is built
with cell and clause naming the **same** tree (must stay silent). A one-sided arm would pass just as well
against a helper that shouts ADRIFT at every row.

**Proven to fail before it landed** — the gate run against `HEAD:scripts/util_score_row.py`:

```
PRE-CURE GATE rc=1
GATE FAIL: check never graded the tree the cell claims (327930877) -- it is reading only the Tree column,
GATE FAIL: cell/clause disagreement on 'snobol4' was graded but never reported as ADRIFT
GATE FAIL(1) [test_gate_score_row_rewrites_in_place]: 2 leaderboard write-path invariants broken (examined 19 arms)
```

and post-cure `GATE PASS(0) … (examined 19 arms)`, rc=0.

## ⭐ The general form — and this is the THIRD instance of it measured today

⛔ This is not a new class. It is
[[FINDING-2026-09-05-hq_T-a-check-that-cannot-see-its-subject-says-nothing-and-nothing-reads-as-a-pass]]
again, in a third tool: there, a guard's evidence was out of REACH (a widened markdown row, an extracted
family with no sibling `ALL.csv`); here, the evidence is right beside the check and the check reads the
*wrong cell*. Same silence, same reading-as-a-pass, different reason for the blindness — which is why the
cure has to be asserted per instrument rather than fixed once and assumed to have travelled.


**A bookkeeping index is only as true as the discipline that maintains it, and an index nobody is forced to
update is a claim about the past.** The helper was correct; its *reader* trusted a coupling that only exists
when every writer uses the helper. Whenever a check reads a derived field instead of the field a human reads,
ask what happens when the two disagree — if the answer is "the check believes the derived one and says
nothing", the check has a blind spot exactly the size of the hand-edit rate.

Related, same session and the reason this was found at all:
[[FINDING-2026-09-05-hq_T-an-orphaned-corpus-runner-taxes-every-root-and-nothing-reaps-it]].
