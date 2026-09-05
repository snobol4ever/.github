# GOAL-HQ-RESOLVE.md — HQ-RESOLVE (hq_R), opened 2026-09-05 15:02 CDT

## THE MANDATE
Lon 2026-09-05, in-chat to ceo, verbatim: *"So how many HQ's and how many Fleet workers should we have? 8 HQ's?"* · *"I just created S, I, and R root folders."* — the ceo's recommendation that day (GOAL-CEO CEO-293): eight Opus HQs, each owning ONE cure surface small enough to drain between landings, over twelve Sonnet walkers, because the measured shortage was cure capacity, not witness supply (one cure per HQ-hour against a walker output several times that, and five engine classes queued on one HQ that had not read its mail in ninety minutes).

## THE LANE (MASTER-PLAN § THE LANES, eight HQs)
hq_R owns the PROLOG BUILTINS: ISO 13211-1 § 8 builtins, § 7.12 error terms, streams and term I/O, the INRIA suite (275/445 outcome class, 268 bindings) and the swi/gnu vendor suites — every Prolog class whose cure is a builtin or the runtime; the Prolog frontend, clause DB, cut and control stay hq_C's. Its seats under THE 12-SEAT CUT: 10.

## LAWS THAT BIND EVERY hq_R LANDING (compact; RULES.md is the parent)
- An HQ CURES; a seat measures. You never run a suite, a board or `make test` by hand — a seat runs it and files the class row with a minimal witness cut from the oracle; you cure it in rung order on that witness (Lon 2026-09-05 to hq_T, MASTER-PLAN § WHO FIXES WHAT).
- A shared-node change (a box two or more frontends lower to, `x86_asm.h`, the emitter, runtime core/rt) is AUTHORED by the HQ whose language exposed the class and CO-SIGNED by hq_U, which grades the other frontends' boards and the demo set (RULES § THE DEMO-SET CONTROL ARM) before the push. hq_U reviews; it does not queue.
- Every landing names its control arms with tree hashes; every suite run rewrites its SCORE.md row through `util_score_row.py`; THERE IS NO XFAIL; OUR FILES ARE LF; no pristine build; a multi-line DONE-WHEN is run whole by hand until hq_T's bus fix lands.
- Drain your inbox at every prompt boundary: a ruling unread is not in effect.

## SESSION SETUP (every session)
1. `git -C SCRIP fetch origin && git -C SCRIP merge --ff-only origin/main`, same for `corpus` and `.github`; `cd SCRIP && make`.
2. `bash scripts/s4e_msg.sh check` — read, act or reply, `clear`.
3. Read this file's LIVE CURSOR, then `SCORE.md` § THE SEPTEMBER 10 GRID for your lane's cells, then assign each of your seats its first row (`s4e_msg.sh assign seatNN <topic>`, a runnable DONE-WHEN proven red once).

## LIVE CURSOR
**2026-09-05 15:02 CDT ceo — OPENED, NOT YET RUNNING.** FIRST ROWS: Prolog rungs 14–18 (evaluable functors, stream/char/byte I/O, term I/O options, term_variables/current_predicate/number_chars/halt, ISO error terms) as seat05 declares them red; the INRIA reds by ISO section. Lon starts the session; the ceo re-lanes the seats at the FLEET-12 flip.

**2026-09-05 15:2x CDT hq_R — STOOD DOWN AT MODE CEO, WITHOUT EVER RUNNING A ROW. The cursor above is unmoved and still correct.**
LANDED: nothing in `src/`, nothing in any suite, no SCORE.md cell rewritten — hq_R opened at 15:02 and the mode flipped to CEO at 15:15, so the seat never held a row. Session setup is the whole of it: `SCRIP` `b812fb6d1`, `corpus` `8972babeb`, `.github` `d30d29baa`, all three `merge --ff-only origin/main` clean and equal to origin; incremental `make` green (`scrip` + `out/libscrip_rt.so -> libscrip_rt-f65f143e2f.so`, 15:12), which is the build any later verdict here would have graded on — no board was run, so no verdict is claimed.
LEFT: **all of it, untouched** — Prolog rungs 14–18 (evaluable functors; stream/char/byte I/O; term I/O options; `term_variables`/`current_predicate`/`number_chars`/`halt`; ISO § 7.12 error terms) and the INRIA reds by ISO section, pending seat05's red declarations. No row was claimed, so nothing returns to the queue and nothing is hidden from the next picker.
WITNESS: `s4e_msg.sh next` REFUSES **rc=2** — *"you are hq_R, an HQ, and MODE line 1 is CEO"* — which is the dispatcher working, not a blocker; `grep -rl hq_R /home/resources/postoffice/claims/` exits **1** (no claim names this seat, so there is nothing to unclaim); `git status --porcelain` empty and `origin/main..HEAD` empty in all three repos (nothing stayed only in this checkout). hq_P's `define` diagnosis named in the ceo's stand-down note is already at origin as tracked `.github/wip-patches/define-redefinition-ordering-hq_P-2026-09-05-three-of-four-layers.patch` — not an hq_R debt.
