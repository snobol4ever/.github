# FINDING: `park` never writes the session-attribution receipt — the Stop-hook banner silently misattributes to a stale prior action

**Seat:** seat12 (FLEET-16) · **Date:** 2026-08-30 · **Row:** `zd-omega-head-per-op-filter-one-cause-behind-boolptr-boolidx-and-the-spine-leaks` · **Found while:** parking that row `BLOCKED-ON:calling-convention-depth-tracked` (to stop 13 consecutive unworked plain-releases churning the picker) and then checking the resulting banner before ending the session.

## MEASURED
`s4e_msg.sh park zd-omega-head-per-op-filter-one-cause-behind-boolptr-boolidx-and-the-spine-leaks BLOCKED-ON:calling-convention-depth-tracked` succeeded — verified directly, not assumed: `QUEUE.tsv` row reads `0	zd-omega-head-...	unassigned	BLOCKED-ON:calling-convention-depth-tracked`, and `claims/zd-omega-head-....claim` is gone. Immediately after, `s4e_msg.sh banner` printed:
```
✅ SUCCESS — seat12 — safe to /clear — row RELEASED tests-consolidate-icon · 16 commit(s) · 1 FINDING(s), attributed since 12 hours ago · row tests-consolidate-icon
```
Wrong row name, wrong verb (RELEASED vs the PARK this session actually did), wrong commit count — none of it describes this session. `cat postoffice/seat12/.last-row`:
```
tests-consolidate-icon
RELEASED 2026-08-30T08:55Z
```
~1 hour stale — the closing receipt of whatever the immediately-prior seat12 session last closed, before this session ever started.

## ROOT CAUSE
`s4e_mark_row` is the writer of `.last-row` — the session-scoped receipt the banner's row-1 fallback reads (per this file's own `banner-attributes-wrong-row-on-unclaim (s273)` header comment, minted to fix a related but different misattribution). Grepped the full `park)` case block (`s4e_msg.sh`, roughly lines 536–637): it never calls `s4e_mark_row`. `unclaim` (line ~530: `s4e_mark_row "$topic" RELEASED`) and `done` both call it; `park` does not. A session whose terminal action on a row is `park` leaves `.last-row` untouched, so the banner reports the *prior* session's close as if it were this one's — silently, with no error, a plausible-looking correct-shaped banner that is simply describing the wrong session.

## WHY THIS MATTERS NOW SPECIFICALLY
`park <topic> BLOCKED-ON:<x>` is a first-class, sanctioned dispatch verb (`s4e_msg.sh`'s own header treats it as such), not an edge case — it's the documented cure for exactly the picker-thrash this row had, and seat16 already used it successfully earlier in this same row's own history. This session's own task-file NEXT block encourages using it again over a 14th plain release. Doing that now makes the banner — described in THE LOOP's own text as "the only thing Lon reads" — systematically wrong for every session whose last act is a park, not a one-off. Same failure shape as the s273 fix already in this file (a stale/wrong row surfacing as if it were the current session's), just a verb that fix didn't cover.

## NOT FIXED HERE
Did not touch `s4e_msg.sh` — this session's actual claimed row is the zd-omega-head park, and `s4e_msg.sh` is fleet-wide-blast-radius infrastructure every seat loads every prompt. Mechanical fix by the existing s273 precedent: add an `s4e_mark_row "$topic" "PARKED:$st"` call inside the `park)` block, mirroring `unclaim`'s. Flagging to hq_C (queue custodian) rather than fixing solo, same restraint this row's own history uses for shared-mechanism code.

## EVIDENCE
- `postoffice/seat12/.last-row` — stale receipt, `08:55Z` vs this session's park at `09:55Z`–`10:0xZ`.
- `SCRIP/scripts/s4e_msg.sh`, `park)` block (~536–637) — no `s4e_mark_row` call anywhere in it.
- `SCRIP/scripts/s4e_msg.sh`, `unclaim)` block, ~line 530 — `s4e_mark_row "$topic" RELEASED`, the call `park` is missing.
