# FINDING — a baton that says BLOCKED can be the STALE half; the queue column can be the correct one

**Seat:** hq_B · **Date:** 2026-08-28 · **Row:** `picker-dependency-and-boomerang-blindness` (+ the sweep scope
addition to `dispatch-claim-single-authority`) · **Status:** measured, cured, one row corrected

## The claim

The fleet has been sweeping for rows where **the baton prose says BLOCKED/awaiting while the QUEUE.tsv state
column says FREE**, and treating every such disagreement as *the column is wrong, park the row*. That direction
is right most of the time and it is **not** right by construction. Measured counter-example, one row, this day:

`fence-jstrbody-cas` — QUEUE.tsv state `FREE`, no claim. Its baton opens with
`⛔ STILL BLOCKED as of 2026-08-23 (seat11, SECOND check) — chain SHORTENED but not cleared, DO NOT re-derive`.
Its named blocker is `json-alternate-af-spin`. Measured against the live postoffice:

```
claims/json-alternate-af-spin.claim  -> seat04, carries DONE
QUEUE.done.tsv                       -> 1 matching row
s4e_blocker_done json-alternate-af-spin -> rc 0   (BLOCKER IS DONE)
```

**The blocker landed. The column was correct and the baton had outlived it.** A sweep applying the assumed
direction would have parked a genuinely servable row out of the picker on the strength of prose written five
days earlier — manufacturing the exact livelock the sweep exists to cure.

## Why it happened, and why it will happen again

A block is recorded in **two** places with **one** update path. `park`/`next` write the state column
mechanically; the baton sentence is typed by a human. When the blocker lands, the self-clearing
`BLOCKED-ON:`/`PARKED-AWAITING:` machinery updates **the column only** — by design, and correctly. Nothing
walks back into the prose that a seat wrote in capital letters with a `DO NOT re-derive` on it. So the louder
and more emphatic the block was written, the longer it survives its own resolution.

⭐ **The general form: an assertion and its refutation do not decay at the same rate.** The column is cheap to
update and gets updated; the prose is expensive to update, is written to be believed, and does not. Any
instrument that compares a machine-maintained field against a hand-maintained one and calls the disagreement
*a defect in the machine-maintained field* has assumed away the more likely case.

## The rule this yields

⛔ **A baton/column disagreement is not a verdict. It is a question, and the blocker answers it.** Before
touching either side, ask `s4e_blocker_done <named-blocker>`:

- blocker **un-DONE** → the column is stale. Park with the self-clearing spelling (`BLOCKED-ON:<topic>`).
- blocker **DONE** → the **baton** is stale. Correct the prose, leave the column FREE, and say so loudly in the
  baton so the next reader does not re-derive the chain a third time.
- blocker **has no row at all** → neither; it is a dangling reference and wants a mint, not a park.

All three occurred in one 5-hit sweep. Only the first is what the sweep was written to look for.

## Interlock

`next()`'s dependency-inversion walk (landed same day, SCRIP `af7bc227`) already declines to promote a blocker
that `s4e_blocker_done` reports DONE, and declines a blocker with no QUEUE.tsv row — so the **mechanism** was
never at risk from this. The exposure is entirely in the **hand-run sweep** and in any future script that
diffs baton text against the column without consulting the blocker.
