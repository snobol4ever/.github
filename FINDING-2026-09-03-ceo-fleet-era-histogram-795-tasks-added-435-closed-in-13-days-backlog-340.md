# FINDING 2026-09-03 (ceo) — the Fleet era in one histogram: 795 tasks added, 435 closed, 20 retired in 13 days; open backlog ~340

Asked by Lon 2026-09-03 ~21:55 CDT: *"piece together a histogram of tasks added and tasks completed per day going back to when we began our adventure using Claude Code … when we had the concept of Fleet."*

**Method (computed, not recalled).** Population: the 853 `tasks/*.task.md` batons in `/home/resources/postoffice`. ADDED day = the earliest of the baton's `mint` stamp and its earliest ledger `[who·date]` line (58 batons carry no date and are excluded). CLOSED = the topic is in `QUEUE.done.tsv` (565 rows; 472 of them still have a baton), or carries a `DONE` claim, or reads `DONE*` in `QUEUE.tsv`; CLOSED day = the baton's last ledger date (37 closed batons have no ledger line and are excluded). RETIRED = `SUPERSEDED*`/`RETIRED` states and `QUEUE.retired.tsv`. Dates are as the seats wrote them (UTC after 19:00 CDT), so the `09-04` bucket is the evening of 09-03 and is folded into it below. Landings = commits on `origin/main` of SCRIP + corpus + .github by box-clock day.

| day | added | closed | retired | landings (3 repos) | FINDINGs |
|---|---|---|---|---|---|
| 08-22 (CEO seat opens, s257) | 85 | 18 | 7 | 329 | 85 |
| 08-23 (first FLEET-4, s261) | 74 | 27 | 1 | 356 | 66 |
| 08-24 (FLEET-16, s272) | 40 | 29 | 2 | 308 | 69 |
| 08-25–26 (break / account switch) | 0 | 1 | 0 | 18 | 7 |
| 08-27 (FLEET-16 → 8 → 12) | 87 | 78 | 3 | 594 | 114 |
| 08-28 (FLEET-8/12, TRIO, hq_B opens) | 59 | 40 | 2 | 404 | 70 |
| 08-29 (FLEET-8, CEO mode) | 77 | 51 | 0 | 691 | 139 |
| 08-30 (TRIO, FLEET-16) | 67 | 38 | 1 | 225 | 100 |
| 08-31 (break) | 0 | 1 | 0 | 2 | 1 |
| 09-01 (FLEET-16 → TRIO) | 41 | 13 | 0 | 194 | 41 |
| 09-02 (TRIO, the Prolog cut) | 77 | 60 | 4 | 290 | 66 |
| 09-03 (FLEET-8→12→16, QUARTET, FLEET-16, QUARTET) | 188 | 79 | 0 | 384 | 58 |
| **total** | **795** | **435** | **20** | **3795** | **816** |

Open backlog by this reconstruction: 795 − 435 − 20 = **340**; `QUEUE.tsv` at 21:47 carries 379 rows with 327 free for the picker — the two agree within the undated remainder. Close rate over the era: 435 / 795 = **0.55 closed per added**; on the two big fleet days it was 0.90 (08-27) and 0.42 (09-03, when 130+58 rows were minted — the censuses, the class rows and the seven denominators — against 79 closures). The trough days (08-25/26, 08-31) are the account switches.

**Reading.** Adding has outrun closing every day but 08-27; the backlog is a census backlog by design (a class row per witness), but under Lon's 21:30 rulings (100% = the industry standard; there is no XFAIL) the rows that matter are the V-cell denominators and the xfail resolutions, and those are twelve rows, not 340. The number to watch from here is closed-per-day on rank-0 rows, not the total.
