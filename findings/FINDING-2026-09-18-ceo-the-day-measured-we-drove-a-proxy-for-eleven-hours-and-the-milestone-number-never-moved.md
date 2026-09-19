# FINDING — THE DAY MEASURED: WE DROVE A PROXY FOR ELEVEN HOURS AND THE MILESTONE NUMBER NEVER MOVED

**ceo, 2026-09-18 20:1x CDT (`date`-read), on Lon's order to scan the commit history and say what went wrong. Status: MEASURED over `origin/main` of all three repos, 08:39–19:52 CDT.**
**Claims duplicated (Lon deletes FINDINGs; RULES.md line 31):** `GOAL-CEO.md` CEO-902 and `ARCH-GC-COMPILE-TIME-FRAME-MAPS.md` § 0. If this file is gone, those hold.

## 1. THE DAY IN NUMBERS, ALL FROM `git log origin/main --since='15 hours ago'`

| measure | reading |
|---|---|
| commits | **97** — SCRIP 46, `.github` 51, corpus 4 |
| span | 08:39 → 19:52 CDT |
| `src/` churn | 157 files, +6231 / −3949 |
| `scripts/` churn | 68 files, **+5395 / −103** |
| new gates | 14 |
| instrument files touched | 46 |
| ARCH-GC design page | **68 848 → 114 029 chars (+66 %)**, 8 amendments in one day |
| `safe-points.unpolled` | 208 → 132 → 131 → 120 → 117 → 110 → 109 → 97 → **123** |
| `conservative total` | **24 → 24. Byte-identical in all eight baseline revisions.** |

⛔⛔⛔ **THE DECISIVE READING, AND IT IS ONE LINE: `gc_heap.c` CARRIED `gc_zeta_frame_calls=14 cons_stack=6` AT EVERY SINGLE COMMIT THAT TOUCHED IT TODAY** — `1073aec49`, `c6a2c07e1`, `fd599cacd`, `d668557d1`, `665685f83`, `48d5a1a5e`, `de2e28d37`. The censused `conservative` line (`gc_zeta_frame_calls 12 · cons_stack_uses 8 · rt_cas_live_span_uses 2 · hb_scan_interior_uses 2 = 24, want 0`) is **identical in every one of the eight `gc_census_baseline.tsv` revisions the fleet pushed today.**

## 2. ⛔ WHAT WENT WRONG — FIVE THINGS, IN ORDER OF SEVERITY

**2a. WE DROVE A PROXY, NOT THE MILESTONE.** The milestone is *delete the conservative scan* — that is what makes the collector stop guessing, it is Lon's clause (4)+(5) of CEO-895, and it is `conservative → 0`. **The fleet drove `unpolled` instead, which fell 208 → 97 and looked like a day's work.** Polls are a PRECONDITION for deleting the scan, not the deletion. The deletion is blocked by three things that got almost no work: the blob frame (§ 6.2b), the Rule-4 callback residual (census RED all day), and the heap-interior visitors (step 5, blocked on `DT_DATA` since 13:52). **F6 step 3 — the walker, the thing that actually deletes the scan — received exactly ONE commit today (`665685f83`, 11:15).** Everything else was polls, instruments and prose.

**2b. THE RULER WAS RE-CUT FIVE TIMES WHILE IT WAS BEING READ.** `scripts/gc_census_baseline.tsv` now carries **five `CRITERION CHANGED` notes**. `unpolled` moved 202→203→210 on criterion alone, then 208→97 on work, then 97→123 on a denominator correction. ⛔ **A reader of the trajectory cannot separate progress from redefinition without reading five header paragraphs, which is why CTO-79's honest correction reads as a regression and why nobody could state the fleet's position in one number at any point today.**

**2c. INSTRUMENTS FAILED AT ROUGHLY ONE PER HOUR, AND NEARLY ALL WERE GREEN WHILE BROKEN.** Eleven distinct, all from today's own subject lines: board arm 9 red for a day against a correct board **plus eight sibling matchers with the same defect**; the fingerprint gate DARK for a day; the digest gate's five-thousand-character window; the FINDING arm's canary alive and its recall dead; **ten gates that could not say no, one of which had been scanning nothing on the real tree since it was written**; the safe-point census capping its listing at 25; a census reading zero over a population that was not Lon's; the callee-saved census at `heap=0` having never graded one instance of its own class; the conservative scan starting three bytes off a word boundary; **the decidable test finding 320 master entries ran with ZERO collections, so no board we own could grade the poll landings at all**; and the allocating set undercounted by 99 functions because a TAIL JUMP is not a call edge. ⛔ **THIS IS THE DISEASE. We are not slow at building the collector. We are fast at building instruments that grade nothing, and we spend the following day discovering it.**

**2d. THE DESIGN PAGE GREW 66 % IN A DAY AND IS BEING USED AS THE WORK LOG.** 68 848 → 114 029 chars, eight amendments, five in-place corrections and three retractions living inside a page marked FROZEN. Frozen law, mechanism findings, withdrawn cures and instrument lessons are all in one file, which is precisely why Lon had to ask *"how can CTO and CFO be working a design that you have no clue what it will be?"* — **the page could not answer it.** § 0 (CEO-900) is a partial cure; the structural cure is a split.

**2e. NOBODY OWNED THE MILESTONE.** CEO-873 split step 4 three ways at 11:03; CEO-879 re-cut it at **11:11, eight minutes later**. The cfo left step 4 for step 5, the cto took step 4, and **the ceo also landed four step-4 poll batches itself (17:15, 17:22, 19:00, 19:05) — cure work, not seat work, and one of them BROKE FOUR FRONTENDS (`d2e772200`).** All three officers converged on the same proxy and **no seat was on the critical path to `conservative = 0` at any point in the day.**

## 3. ⛔ THE ceo's OWN SHARE, STATED FIRST BECAUSE IT IS THE LARGEST

The seat that owns the design page let it grow 66 % without noticing it had become unreadable; ran four poll batches of its own instead of reading ahead of the officers; **did not know that `DESCR_t` carries `mint_op` and `src_node` until Lon pointed at them**, while the cfo was blocked for six hours on a question those three bytes answer; and published a precondition claim (§ 8.1) grounded on a grep of the wrong population, corrected within the hour by the cto. **Four of the day's five design corrections came from the cto and one from the ceo against itself. None came from the ceo reading ahead. That is the NO SECOND READER hazard of MODE line 2 arriving exactly where it was predicted, and it is a seat failure, not an officer failure.**

## 4. ⭐ WHAT IS NOT WRONG, SO THE DIAGNOSIS IS NOT READ AS DESPAIR

**The design held.** All eight frozen items of § 0 stood the whole day and not one landing contradicted one. Every correction was INSIDE a mechanism. The poll work is real — `polled 2 → 113` is 111 genuine safe points that did not exist this morning, each on its own asm evidence with a live fail-once. The root class is genuinely being closed (cset registry, bb-source registry, scan-subject saves, the lowerer registries — four rooting landings before 09:00). `malloc` left the tree (1880 sites, 79 files). And **every one of the eleven instrument failures was FOUND, which is the system working, just one day late each time.**
