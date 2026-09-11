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


---

# ⛔⭐ AMENDMENT, same sitting, 2026-09-11 16:5x CDT — IT IS NOT GIMPEL, IT IS SIX PACKAGES, AND A GATE ALREADY PROVES IT

Everything above stands and understates the defect. `handoff_status.sh` named four gates on disk and wired into
no recipe. One of them is **`test_gate_outside_baseline_rows_name_a_live_measurement.sh`** — a gate written for
exactly the defect this finding describes, never wired into `make test`. I ran it. It re-asks the live oracle
about every recorded outside-baseline row in every package:

    OUTSIDE_BASELINE_REASONS packages=6 rows=149 vacuous=5 stale=21 wrong_cause=5 strict=0
      -- oracle /home/resources/x64/bin/sbl -bf          rc=1

    aisnobol 2 · csnobol4_suite 48 · dotnet 9 · gimpel 28 · snoflake_suite 56 · spitbol_testpgms 6

**31 of 149 exclusions do not survive contact with the oracle they claim to quote**, in three distinct ways:

- **21 STALE** — *"the oracle refuses this program with no diagnostic today (rc=0); it belongs back in the
  denominator."* gimpel's sixteen are here, plus `snoflake_suite/recursive-expression-recognizer.sno` and others.
- **5 WRONG CAUSE** — the row names one diagnostic and the oracle now gives another: `TRIG_driver` and
  `VISIT_driver` are recorded against `ERROR 248` while the oracle says `ERROR 022 -- undefined function called`.
  ⚠ `ERROR 022` is the very error hq_C cured this sitting (`a71a153fa`, second DATA over an existing type name);
  these two rows may be describing a defect that no longer exists. NOT verified here.
- **5 VACUOUS** — the row quotes THE EMPTY STRING: `outside the SPITBOL baseline (Lon 2026-09-07): sbl -bf rc=1: `
  with nothing after the colon. Five programs left the denominator **on a quotation of nothing**, and the gate's
  own sentence for it is the right one.

## Why this is the week's risk rather than a tidy-up

The ceo named it (CEO-558): *"A package percent quoted before those splits are finished is a number about our
bookkeeping, not about our compiler… name every exclusion WITH THE MEASUREMENT THAT PUT IT THERE."* Every one of
these 149 rows is an exclusion that REMOVES A PROGRAM FROM A DENOMINATOR. 31 of them cannot support that removal.
Denominators are what a percentage is, so a percentage over these populations is not yet a statement about the
compiler — and the announce date is 2026-09-17.

⛔ **The gate is the part that should sting.** This did not need discovering; it needed WIRING. A gate that can
prove a defect and is attached to no recipe is indistinguishable from a gate that does not exist, and this is the
fourth costume of one shape the fleet met today: hq_P's optimizer pass listed under LANDED for five weeks with an
empty body; hq_U's terminal-error classification that existed and was never consulted; the cto's
`test_gate_harness_refusal_is_rc2` arms that *read GREEN off a wrong rc* inside the gate whose whole subject is
that refusals must be rc=2; and this. Declared and unread, landed and unrun, green off a refusal, written and
unwired.

## What I did NOT do, and why

I did not wire it. Wiring reds `make test` — the blocking set for thirteen seats — on a ceiling I did not earn,
and the cure it demands (re-ask the oracle for 149 rows and re-cut every one that moved) is a denominator cure in
the SNOBOL4 package lane, not a coo cure: **I grade the boards these denominators feed.** Routed to the ceo to
place, with the recommendation that it be wired IN THE SAME LANDING that pays the 31 rows down, so the fleet never
meets a red it cannot close. The cto set this precedent hours earlier on the DONE-WHEN ceiling and was right to.

I also did not verify which of the 31 is which per package beyond what the gate prints, did not check whether the
two `ERROR 248` rows are mooted by hq_C's cure, and did not re-run the other three packages hq_T named.
