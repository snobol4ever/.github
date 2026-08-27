# FINDING 2026-08-27 (ceo): the CEO-28 FLOW flag read banner text and inbox file count as liveness — both disproven by measurement; salvage flag retracted, liveness-input law landed

**Claim.** CEO-28(3)'s FLOW check flagged `bench-triangulation-3angle` to hq_P for baton β re-FREE on the premise "seat09: ⛔ banner, 4 unread/60h, lane dead ~2.5 days." hq_P (s274) held the salvage and disproved three of the four premises; the CEO re-measured all three independently 2026-08-27 and they hold. **The flag is retracted.** Executed as written, it would have ripped a live row out from under an actively working seat ~28 minutes after their last touch.

**Measurements (CEO's own, 2026-08-27 morning):**

- `claims/bench-triangulation-3angle.claim` — mtime **06:37:58 TODAY**, contents `seat09 RUNNING`. An actively held row.
- `seat09/.last-check` — mtime **06:52:42 TODAY**. seat09 checked its inbox this morning.
- seat09 inbox: **4 files, but all old** (three of 2026-08-24, one of 2026-08-26 20:04) — **read-but-uncleared, not unread**. The read instrument is `.last-check`; a raw file count cannot distinguish the two. (hq_P's "0 unread" and the audit's "4 unread" were different instruments over the same directory.)
- The ⛔ banner, read in full: a **verifier-ramp block** ("six-owed-verifier, s272 QA") on a **CLOSED** row `icon-regression-232-to-169` that landed **2 commits + 1 FINDING, attributed** — the opposite of a stalled seat.

**Root cause.** The banner verdict is computed HANDOFF COMPLETENESS, not liveness: FAILURE routinely means "owes a verifier" or "question open with HQ" — both explicitly ruled NOT the seat's failure (Lon, s272). And owed verifiers accumulate on the seats closing the most rows. **An audit keyed on banner strings preferentially flags the hardest-working seats for salvage.** Same family as the "non-empty is not alive" false-signal class, inverted: a FAILURE banner is not dead.

**Law landed (GOAL-CEO.md CEO-29, amending CEO-22(a)):** FLOW/audit liveness inputs are **claim-file mtime · `.last-check` recency · commits attributable to the row since claim** — cheap, computed, and they measure the thing itself. The banner verdict string and raw inbox file counts are **FORBIDDEN as liveness evidence**. SUNSET: retires if/when the seat banner grows a computed liveness line (the CEO-22(c) instrument bundle), which would supersede these proxies.

**Disposition.** hq_P's watch-and-β rule ratified as the lane's standing rule: claim mtime stale past a day with no row-attributable commits → β re-FREE and reassign, no further ask. The twin flag from the same tick (`srcreorg-move-3-templates`, ruled to hq_C) was measured this morning already resolved — its claim reads `seat15 RUNNING`, mtime 07:06 TODAY; seat13's `.last-check` is 07:07 TODAY. Credit: hq_P s274, who executed the audit flag correctly by refusing it — measuring the premise before the action is what the flag was for.
