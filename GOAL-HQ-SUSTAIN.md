# GOAL-HQ-SUSTAIN.md — HQ-SUSTAIN (hq_S), opened 2026-09-05 15:02 CDT

## THE MANDATE
Lon 2026-09-05, in-chat to ceo, verbatim: *"So how many HQ's and how many Fleet workers should we have? 8 HQ's?"* · *"I just created S, I, and R root folders."* — the ceo's recommendation that day (GOAL-CEO CEO-293): eight Opus HQs, each owning ONE cure surface small enough to drain between landings, over twelve Sonnet walkers, because the measured shortage was cure capacity, not witness supply (one cure per HQ-hour against a walker output several times that, and five engine classes queued on one HQ that had not read its mail in ninety minutes).

## THE LANE (MASTER-PLAN § THE LANES, eight HQs)
hq_S owns the SNOBOL4 RUNTIME: builtins, I/O and file association, keywords, error handling and limits (SETEXIT, &ERRLIMIT, &STLIMIT), tracing, the csnobol4 suite (60/119 at opening) and the SPITBOL testpgms — every SNOBOL4 class whose cure lives in `src/runtime/{builtins,rt,core}`, `rtx_match.s` or `rtx_str.s`; the parser, the lowerer and the pattern boxes stay hq_P's. Its seats under THE 12-SEAT CUT: 03–04.

## LAWS THAT BIND EVERY hq_S LANDING (compact; RULES.md is the parent)
- An HQ CURES; a seat measures. You never run a suite, a board or `make test` by hand — a seat runs it and files the class row with a minimal witness cut from the oracle; you cure it in rung order on that witness (Lon 2026-09-05 to hq_T, MASTER-PLAN § WHO FIXES WHAT).
- A shared-node change (a box two or more frontends lower to, `x86_asm.h`, the emitter, runtime core/rt) is AUTHORED by the HQ whose language exposed the class and CO-SIGNED by hq_U, which grades the other frontends' boards and the demo set (RULES § THE DEMO-SET CONTROL ARM) before the push. hq_U reviews; it does not queue.
- Every landing names its control arms with tree hashes; every suite run rewrites its SCORE.md row through `util_score_row.py`; THERE IS NO XFAIL; OUR FILES ARE LF; no pristine build; a multi-line DONE-WHEN is run whole by hand until hq_T's bus fix lands.
- Drain your inbox at every prompt boundary: a ruling unread is not in effect.

## SESSION SETUP (every session)
1. `git -C SCRIP fetch origin && git -C SCRIP merge --ff-only origin/main`, same for `corpus` and `.github`; `cd SCRIP && make`.
2. `bash scripts/s4e_msg.sh check` — read, act or reply, `clear`.
3. Read this file's LIVE CURSOR, then `SCORE.md` § THE SEPTEMBER 10 GRID for your lane's cells, then assign each of your seats its first row (`s4e_msg.sh assign seatNN <topic>`, a runnable DONE-WHEN proven red once).

## LIVE CURSOR
**2026-09-05 15:02 CDT ceo — OPENED, NOT YET RUNNING.** FIRST ROWS: SNOBOL4 ladder rungs 25–27, 29–32 (predicates, string functions, real math, I/O, system, SORT, error handling) once seat09 declares them red; the csnobol4 suite by class; the SPITBOL testpgms. Lon starts the session; the ceo re-lanes the seats at the FLEET-12 flip.
