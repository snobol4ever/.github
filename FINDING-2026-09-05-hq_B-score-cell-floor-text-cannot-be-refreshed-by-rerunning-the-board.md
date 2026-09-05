# FINDING — a SCORE cell's FLOOR text cannot be refreshed by re-running the board

**Seat:** hq_B · **Date:** 2026-09-05 (MODE OCTET) · **Measured on:** SCRIP `b812fb6d1`→`e5b9f3333`, corpus `8972babeb`, RT_OPT=-O0, incremental `make`.

## The claim

`board_icon_master.sh` composes its SCORE text with the floors interpolated live
(`scripts/board_icon_master.sh:229`, `floors m3 $M3_PASS_FLOOR / m4 $M4_PASS_FLOOR`), so a
re-pin plus a re-run *looks* like it must republish the new floor. It does not. After
re-pinning 596 → 607 and re-running the board **green, twice**, `SCORE.md` still read
`floors m3 596 / m4 596` beside the correct `607/609` measurement.

## Why

`util_score_row.py`'s merge is keyed on the **measurement**, not on the whole clause. The
measured pair `607/609 · 607/609` was unchanged between the pre-pin and post-pin runs, so the
clause was treated as already present and the surrounding text — the floors — was never
rewritten. A floor-only change is invisible to the merge.

## Why it matters, and the shape it belongs to

The cell then asserts a floor **that no longer exists in the script it cites**, next to a true
measurement and a true date. Nothing is stale-looking: the numbers are right, the runner is
named, the timestamp is fresh. This is the same family already recorded in this corpus —
`test_gate_score_tables_agree.sh` compares BY VALUE precisely because *same-day staleness is
invisible to any freshness check*; here the stale half is not a value at all but the **bar the
value is being judged against**, which no by-value comparison inspects.

⭐ The general form, and the reusable half: **a merge keyed on one field silently freezes every
other field in the same clause.** Re-running the instrument is the ordinary cure for a stale
cell, and it is exactly what fails here — so the seat who does the right thing walks away
believing the cell was refreshed.

## Corrected by hand, and deliberately only the live clause

The live clause now reads `floors m3 607 / m4 607`. The folded provenance clause below it still
reads `floors m3 596` and was left alone: as history that is TRUE, and rewriting it would have
back-dated today's pin onto a measurement taken under the old one.

## Not cured

The merge behaviour itself. A cure belongs in `util_score_row.py` (re-render the whole clause
when any interpolated field changes, not only the measurement), and until it lands, **a re-pin
is not published by re-running the board** — the floor must be corrected by hand, or the row
carries a bar it no longer enforces.
