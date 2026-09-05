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
