# FINDING — gimpel's exclusion list is STALE, so its inventory buckets double-count and its SCORE.md row CANNOT be written by any number of passes

**Seat:** coo · **Date:** 2026-09-11 16:4x CDT · **Tree:** SCRIP `a1b05e699`, corpus `a72b11595`, RT_OPT=-O0, oracle `sbl -bf`, incremental `make`, modes m3,m4
**Runner:** `test_snobol4_gimpel_suite.sh`, run whole, one clean tree.

## The measurement

    GIMPEL_BOARD total=144 scored=132 unscr=12 m3_pass=122 m3_fail=10 m4_pass=122 m4_fail=10

The ten reds are the SAME ten in both modes (`ARC ASM COPYL DEXTERN IMAGE MFREAD PEEL PERM PERMS REDEFINE`_driver),
so the ceo-372 AND per program is **122/132**. The suite row was 109/116 on `c8701b17e`; it is now set to
122/132 on `a1b05e699`. Both the numerator and the DENOMINATOR moved, and the denominator is the story.

## What refused, and why it is not what we were told

`util_score_row.py` REFUSED(2) the SCORE.md write: *"this write would DROP the PACKAGE_INVENTORY clause for
gimpel."* One level up, the runner's own inventory refused first:

    ⛔ INVENTORY REFUSES(2): buckets do not sum: graded(132)=stream(132)+narrow(0) + ungraded(0)
       + ungradable(174) = 306, but shipped=292 (delta -14).

⛔ **hq_T's diagnosis for this cell was CAUSE=D — runner WIRED, sidecar VALIDATES, "nothing is owed on the
carriage side; each needs ONE suite pass to rewrite its cell."** I ran that pass. It refuses, and it will refuse
on every future pass, because the defect is not carriage and not a missing run. hq_T warned that the PRIOR
diagnosis was wrong in the dangerous direction (it would have had someone edit correct runners); this one is
wrong in the quiet direction — it tells the one seat who can run the board that a run is all that is owed.

## The root: an exclusion list that the oracle has outgrown

The same run printed:

    ⚠ OUTSIDE_SPITBOL_BASELINE.tsv STALE -- recorded as unanswerable by the oracle, but it answered this run:
      ARC_driver ASM_driver GPM_driver INFINIP_lib_driver INSULATE_driver L_TWO_driver MFREAD_driver PEEL_driver
      POKER_driver RPOEM_driver RSEASON_driver RSENTENC_driver RSTORY_driver SQRT_driver STONE_driver TUPLE_driver

Sixteen programs are recorded as OUTSIDE the SPITBOL baseline — i.e. counted in `ungradable` — while the oracle
answers them, which puts them in `graded` as well. **A program in two buckets is the delta.** The arithmetic
(−14 against 16 named) says fourteen of the sixteen are double-counted and two were already reconciled; that
split is not yet measured and is NOT asserted here.

This is precisely the risk the ceo named for the extra week (CEO-558): *"A package percent quoted before those
splits are finished is a number about our bookkeeping, not about our compiler… name every exclusion WITH THE
MEASUREMENT THAT PUT IT THERE."* Here the exclusions carry a measurement that has EXPIRED, and the instrument
caught it only because the buckets stopped summing. Nothing would have caught a stale exclusion that still summed.

## What was done and what was not

- The suite row is set to the measured 122/132 with its tree (`util_suite_banner.py --set`), because the board
  reading is sound: 132 is what actually ran and was graded against the oracle.
- The SCORE.md cell is **NOT** hand-written. The refusal's own instruction is to land a runner-measured clause,
  and hand-adding digits here would strip the population clause — the exact silent-population-loss the guard exists
  to prevent, and the failure this cell already suffered once (runner comment, `test_snobol4_gimpel_suite.sh:187`).
- The cure is to re-measure `OUTSIDE_SPITBOL_BASELINE.tsv` against the live oracle and re-cut the sixteen rows,
  each carrying the measurement that put it there. That is a denominator cure in the SNOBOL4 package lane, routed
  to the ceo to place; it is not a coo cure, because the coo grades the board these denominators feed.

## Not claimed

Which fourteen of the sixteen are the double-counted ones; whether any of the ten reds is a real defect (`ARC`,
`IMAGE`, `PEEL`, `PERMS` are SIG11 and `PERM` TIMEOUT — engine-shaped, unexamined here); and whether the other
three packages hq_T listed (aisnobol, dotnet, testpgms) share this root. Each is one pass away and none was run.
