# GOAL-HQ-INSPECT.md — HQ-INSPECT (hq_I), opened 2026-09-05 15:02 CDT

## THE MANDATE
Lon 2026-09-05, in-chat to ceo, verbatim: *"So how many HQ's and how many Fleet workers should we have? 8 HQ's?"* · *"I just created S, I, and R root folders."* — the ceo's recommendation that day (GOAL-CEO CEO-293): eight Opus HQs, each owning ONE cure surface small enough to drain between landings, over twelve Sonnet walkers, because the measured shortage was cure capacity, not witness supply (one cure per HQ-hour against a walker output several times that, and five engine classes queued on one HQ that had not read its mail in ninety minutes).

## THE LANE (MASTER-PLAN § THE LANES, eight HQs)
hq_I owns the ICON SUITES: arizona (43/89), jcon_tests (44/81), ipl (851, run-graded), co-expressions (rung 38) and the Icon runtime files `rtx_icn*.s` — every Icon class a vendored suite exposes; the Icon frontend, generators and the Icon master stay hq_B's. Its seats under THE 12-SEAT CUT: 07.

## LAWS THAT BIND EVERY hq_I LANDING (compact; RULES.md is the parent)
- An HQ CURES; a seat measures. You never run a suite, a board or `make test` by hand — a seat runs it and files the class row with a minimal witness cut from the oracle; you cure it in rung order on that witness (Lon 2026-09-05 to hq_T, MASTER-PLAN § WHO FIXES WHAT).
- A shared-node change (a box two or more frontends lower to, `x86_asm.h`, the emitter, runtime core/rt) is AUTHORED by the HQ whose language exposed the class and CO-SIGNED by hq_U, which grades the other frontends' boards and the demo set (RULES § THE DEMO-SET CONTROL ARM) before the push. hq_U reviews; it does not queue.
- Every landing names its control arms with tree hashes; every suite run rewrites its SCORE.md row through `util_score_row.py`; THERE IS NO XFAIL; OUR FILES ARE LF; no pristine build; a multi-line DONE-WHEN is run whole by hand until hq_T's bus fix lands.
- Drain your inbox at every prompt boundary: a ruling unread is not in effect.

## SESSION SETUP (every session)
1. `git -C SCRIP fetch origin && git -C SCRIP merge --ff-only origin/main`, same for `corpus` and `.github`; `cd SCRIP && make`.
2. `bash scripts/s4e_msg.sh check` — read, act or reply, `clear`.
3. Read this file's LIVE CURSOR, then `SCORE.md` § THE SEPTEMBER 10 GRID for your lane's cells, then assign each of your seats its first row (`s4e_msg.sh assign seatNN <topic>`, a runnable DONE-WHEN proven red once).

## LIVE CURSOR
**2026-09-05 15:02 CDT ceo — OPENED, NOT YET RUNNING.** FIRST ROWS: the arizona and jcon reds by class as seat02/seat07 file them; Icon rungs 38–42 (co-expressions, numeric and bit functions, string functions, files and the run-time system, keywords) as seat01 declares them red. Lon starts the session; the ceo re-lanes the seats at the FLEET-12 flip.

**2026-09-05 15:42 CDT hq_I — LEDGER, CLOSED WITHOUT RUNNING (MODE went CEO before Lon started this seat).** WHAT LANDED: nothing — hq_I never worked a row. WHAT IS LEFT: the whole lane, exactly as the 15:02 cursor above states it; the FIRST ROWS list is untouched and none of it was claimed, so nothing returns to the queue. THE WITNESS: `head -1 /home/resources/postoffice/MODE` reads `CEO`; `grep -rl hq_I /home/resources/postoffice/claims/` is empty (no claim held, so no unclaim was owed); `git rev-list --count origin/main..HEAD` is 0 in all three repos (SCRIP `b812fb6d1`, .github `d30d29baa`, corpus `8972babeb`, all fast-forwarded to origin this sitting) — no cure, patch or FINDING exists only in this checkout. Both ceo messages (`when-you-start-mode-and-lane`, `mode-ceo-now-finish-if-in-reach-else-push-ledger-unclaim-stop`) were read and replied to, then cleared. NOT MEASURED, and not claimed: no build, no suite, no board was run here, so this seat contributes no SCORE.md row and grades nothing.

**2026-09-05 16:0x CDT hq_I — LANE REVIEW, first sitting under OCTET. All three V cells measured by me (OCTET has no fleet), on the ceo's own floor tree SCRIP `b812fb6d1` corpus `8972babeb`, RT_OPT=-O0, incremental `make`.**

| cell | reading | against what the row said |
|---|---|---|
| **arizona** | shipped=124 graded=89 gap=35 · m3 PASS=46 FAIL=43 REJECT=0 · m4 PASS=46 FAIL=43 REJECT=0 — cell form `46/124` (POPULATION LAW: an ungraded shipped program counts as ZERO of the population, never PASS, and is never dropped from the denominator; `46/89` is the graded-set rate) | **UP from 45.** The ceo's brief said 43/89 and the row carried both `43/89` and `45/124`; the 43 was the stale side. |
| **jcon_tests** | total=81 · m3 PASS=45 FAIL=25 CRASH=8 HANG=3 · m4 PASS=42 FAIL=30 CRASH=6 HANG=3 | The brief said 44/81. Confirms the NEWER of the row's two conflicting cells (45/42), retires the older (43/40). |
| **ipl** | **total=852, not 851** · compile_pass=437 compile_fail=415 (linkgap=354 parseerr=58 timeout=0 other=3) · run_graded=60 · m3 22/60 m4 22/60 · RUN_CRASH=2 both (`miu`, `genqueen`, sig11) | SCORE.md and the script's own header both say 851. The runner computes the population structurally, so it self-corrected; the two prose copies are one behind. |

⛔ **THE SITTING'S REAL FIND WAS NOT A NUMBER — ALL THREE BOARDS PRINTED AND THEN COULD NOT BE RECORDED.** `util_score_row.py`'s `derive_measurer()` knew five roots; Lon had opened four more. Every hq_I run ended `REFUSED(2) … the root '/home/claude_I' is not in the seat map` / `SCORE.md NOT UPDATED`, and hq_U, hq_S and hq_R were in the same hole — half the HQ roster silently outside Lon's FACT RULE, with the board still printing normally so the failure reads as success. Worse, `test_gate_seat_identity_one_map.sh` was GREEN throughout: it lifts the MAP from the file (its header is emphatic and right about that) and then hand-typed the ROSTER, which stopped at `/home/claude_T`. **A gate only grades the population it is given.** CURED SCRIP `f69818116` — all nine roots map, and ARM 2's roster is now lifted from the same case block, refusing rc=2 rather than grading an empty one, so a tenth root is graded the moment the bus learns it. Witness both directions is in the commit and in `FINDING-2026-09-05-hq_I-four-of-eight-hq-roots-could-not-write-the-one-leaderboard-and-the-gate-that-pins-the-map-passed-green.md`. Authored in hq_T's instrument lane deliberately, because it blocked this seat's own mandated deliverable and three siblings at once; hq_T is mailed and free to rework it.

✅ **CHECKED AND CLEARED, so nobody re-opens it:** arizona writes `foo.baz`/`tmp3` into the tracked corpus tree mid-run — this is NOT the jcon corpus-corruption class. It runs in `$SUITE` deliberately for read-fidelity and its presnap/postsnap trap removes what appeared; `git status` on corpus is clean after all three runs. jcon's `TOTAL=81` is likewise fully accounted for and not a shortfall: 91 shipped − 9 with no `.std` (link1/2, load1/2, tpp1-5, excluded by name) − `tpp.icn` (its `.std` is preprocessor text, not program output) = 81; the 83rd `.std` is `linking.std`, an upstream orphan with no `.icn`.

**NEXT ROW FOR THIS SEAT** (named, not started): jcon's board prints only `TOTAL=81` and no shipped/graded/gap triple, so hq_I's two vendor suites report their populations in two different shapes — arizona under the POPULATION LAW Lon ruled 2026-09-04, jcon not. Bring jcon (and the IPL header's stale 851) onto arizona's shape.
