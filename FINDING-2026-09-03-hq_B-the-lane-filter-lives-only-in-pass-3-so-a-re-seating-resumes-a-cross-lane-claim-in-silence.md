# FINDING — the lane filter lives only in PASS 3, so a re-seating resumes a cross-lane claim in silence

**Seat:** hq_B · **Date:** 2026-09-03 (box clock) · **Row:** `next-serves-a-seat-only-rows-in-its-hqs-lane-and-no-row-carries-a-blank-owner-cell`
**Trigger:** ceo witness, 22:55 CDT — *"seat07 (HQ file hq_P since 22:45) ended up holding raku-roast-100-percent-compile
(a hq_T-lane row; claim line: RUNNING) while snocone-ladder-top-rung-census (rank 0, owner hq_P, FREE) sat in its own lane.
Either an HQ assigned across lanes or next fell through when it should not have."*

## THE ANSWER TO THE CEO'S QUESTION: NEITHER. IT WAS A THIRD ROUTE.

**Not an HQ assign.** `assign` writes the claim atomically as two lines — the seat, then `ASSIGNED-BY <hq> <ts>`
(`s4e_msg.sh:1287`). The claim read exactly:

```
seat07
RUNNING
```

No `ASSIGNED-BY` line. No HQ dispatched that row across lanes.

**Not the free-row picker either — and this is the measured control arm, not an argument.** With the claim removed and
the identical two rows in a throwaway queue, `next` as seat07 (lane hq_P) prints:

```
↩ skipped 4 free row(s) owned by another seat (topmost: rank 0  raku-roast-100-percent-compile  (owner hq_T)).
QUEUE EMPTY — every row claimed.
```

PASS 3 skips it unconditionally on its **owner cell** (`hq_T` is neither `seat07` nor blank), exactly as ceo ruled
2026-09-03 and exactly as `test_gate_s4e_next_serves_own_lane.sh` case (d) already documents as deliberate. The
free-row picker could not have served that row to that seat, in either lane pass.

**It was PASS 2.** PASS 2 resumes *any* unfinished claim held by `$ME` — no lane check, no owner-cell check, no rank
gate. `_my_lane` was not even computed until line 1633, *after* both earlier passes had already run. Reproduced from
the witness shape:

```
RESUME raku-roast-100-percent-compile (yours, unfinished — s4e_msg.sh done ... when the handoff clause is met)
owner: hq_T   state: CLAIMED:seat07
```

Served in silence, every turn, forever.

## ⛔ THE GENERAL FORM — A SEAT'S LANE IS MUTABLE AND ITS CLAIM IS NOT

The claim was **perfectly in-lane when it was taken.** seat07 was the Raku runner and ceo assigned it that row at
~16:15 CDT ("Do not park ROAST" — Lon). FLEET-8 then rewrote `postoffice/seat07/HQ` from hq_T to hq_P at **22:45:05**;
hq_P force-released the claim at **22:55:35**. For those ten minutes the row was cross-lane — and *nothing re-asks the
lane question after a serve.* The lane filter was built as a property of **picking**, and a held claim is never
re-picked.

⭐ This is the same shape as the picker's own already-cured defects, one level up: `BLOCKED-ON` used to be evaluated
once and honoured forever until CURE 1 made it re-ask every time the row was considered. Lane has the identical
weakness and it was not visible because the *input* changes rather than the row. **Any filter applied at acquisition
time silently decays when the thing it filters on is mutable.**

## THE CURE — A NOTICE, NEVER AN AUTO-RELEASE

`_my_lane` is hoisted above PASS 1, and `s4e_cross_lane_notice()` fires on both resume paths:

```
⛔ CROSS-LANE HOLD — raku-roast-100-percent-compile is hq_T's lane; your lane is hq_P (.../seat07/HQ).
   You are being served it because it is YOUR CLAIM, not because it is your work: PASS 2 resumes a
   claim without re-asking the lane question, and a re-seating changes your lane under a held claim.
   ⭐ WAITING IN YOUR OWN LANE:  rank 0  snocone-ladder-top-rung-census  (owner hq_P)
      An HQ-owned row is not auto-served to a seat -- ask your HQ to run: ... assign <topic> seat07
   KEEP WORKING IT if that was the intent (an HQ may assign across lanes on purpose -- this is a
   notice, not a refusal). Otherwise put it back for its owner:  ... unclaim raku-roast-100-percent-compile
```

⛔ **It does not auto-release and does not change the exit status.** Dropping an in-flight claim to chase a lane would
strand real work, and a cross-lane hold is often deliberate — an HQ may assign across lanes on purpose, and those
claims carry `ASSIGNED-BY`, so they are attributable already. A notice that can block is a notice that gets worked
around. Lane-undetermined topics and a seat with no readable HQ file stay silent, the same degradation every other
lane rule already takes.

## ⭐ THE SECOND-ORDER FINDING THE WITNESS ALSO EXPOSES — AN HQ-OWNED ROW IS NEVER AUTO-SERVED TO THAT HQ'S OWN SEATS

The row ceo expected seat07 to be on (`snocone-ladder-top-rung-census-...`, rank 0, owner `hq_P`) **would not have
been served to seat07 by `next` even after the re-seating** — the owner-cell skip fires on `hq_P != seat07` before the
lane filter is ever consulted. Measured above: it is one of the 4 skipped rows.

This is not a defect of the owner rule; it is a consequence worth stating in one place, because the queue currently
tags most lane work with an **HQ** name in col3 while **seats** do the work. The practical rule that follows:
**every HQ-owned row a seat should work needs an explicit `assign` — the picker will never hand one over on its own.**
hq_P did exactly that at 22:49Z and the situation resolved. Whether that is the intended steady state (rather than,
say, an owner cell that means "this HQ's lane, any of its seats") is a **ceo question, not hq_B's to change** — the
unconditional skip is ceo's own ruling and the gate pins it deliberately.

## EVIDENCE

- `s4e_msg.sh` PASS 1 / PASS 2 / PASS 3; `s4e_topic_lane()` / `s4e_my_lane()`.
- `claims/raku-roast-100-percent-compile.claim` (read live before release): `seat07` / `RUNNING`, no `ASSIGNED-BY`.
- `postoffice/seat07/HQ` mtime `2026-09-03 22:45:05 -0500`; `released/raku-roast-100-percent-compile.release` `22:55:35`.
- Baton ledger: ceo ASSIGNED seat07 at ~16:15 CDT; hq_P force-release at 03:55Z *"Picker slip, not seat07's error."*
- `test_gate_s4e_next_serves_own_lane.sh` — **22/22**, the 11 pre-existing cases carried unchanged as control arms;
  new (m1)-(m4) cross-lane resume announced/still-resumed/names-the-waiting-row/rc=0, (n) in-lane silent,
  (o) undeterminable lane silent.

## ⛔ TWO PRE-EXISTING REDS, NOT CAUSED BY THIS CHANGE, NOT YET OWNED

`test_gate_s4e_one_process_per_identity.sh` (pass=0 m1-red=1 m2-red=1 m3-red=1) and
`test_gate_s4e_park_additive_blocker.sh` (arm-A=0 arm-B=1 fail-once-red=1) fail **identically on the unpatched tree**
— verified by restoring `HEAD:scripts/s4e_msg.sh` and re-running, because ⛔ **neither gate honours `SUT`**, so the
obvious `SUT=`-override control arm is a lie: it runs the working-tree script both times. Reported to ceo; not this
row's scope.
