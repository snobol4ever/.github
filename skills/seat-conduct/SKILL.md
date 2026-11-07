---
name: seat-conduct
description: How a seat behaves on the shared box: kill by pid and only your own, orphans to their seat, background jobs by handle, scratch under /tmp/s4e/<seat>, one process per identity, the record not the chat. Load every sitting with fleet-bus.
---

# Seat conduct

The rules every seat is held to that are about the seat's own behaviour, not about a language or a layer. Each was paid for at least three times in the three-month history (DESIGN-PLAN skills-complete, the cio 2026-11-07, the history audit: fourteen recurring problem classes; eight of thirteen friction reports of 2026-11-04 named the kill and background rules). The law is `.github/RULES.md` (FACT RULES, THE MAIL CHANNEL, COMMIT AND PUSH FREELY); this page is the working summary with its sources. The bus, the rows and the sitting are skill `fleet-bus`; the box and its pools are skill `shared-box`.

## 1. Processes

- **Kill by pid, and only pids you spawned.** Never `pkill -f <pattern>`, never `pgrep` a pattern another seat shares: the pattern matched the caller's own shell three times (COO-341, COO-343, COO-432) and other seats' runs (Lon 2026-09-13, RULES.md FACT RULE). `harness/scripts/s4e_kill_mine.sh --handle <h> | --pid <pid>` kills what is yours with its children.
- **An orphan belongs to its seat.** A process reparented to the user manager with its parent gone is an orphan; the coo's fleet watch names it to its seat once an hour and never kills it (COO-462 ORPHAN_KILL=0, COO-463); the seat kills it by pid or says in one line that it is wanted. Orphans from killed parents filled a scope and stalled the box 2026-11-01 14:4x.
- **Background work only through a handle.** A job that outlives a tool call runs under `setsid` with its log and handle under `/tmp/s4e/<seat>/bg/`, reaped with the session; a bare `&` or a `sleep` left behind is the orphan of the rule above (the cio's own `sleep 3600`, 2026-11-07 09:12).
- **No seat but the coo runs a loop.** `/loop`, ScheduleWakeup and CronCreate are the coo's alone, and the coo's only when Lon starts it for an unattended fleet (Lon 2026-11-07 10:5x, verbatim: "It seems that seats believe it is okay to perform /loop command. That is forbidden and reserved only occasionally for COO when I run the fleet un-attended."; 2026-11-05 15:1x: "The COO is the engine with the /loop. The only seat with a loop."). Every other root's `.claude/settings.json` denies the two tools, except the cio's while Lon has the cio looping alone on the fleet redesign (Lon 2026-11-07 12:0x: "You better lift that ... now!!!"). A seat waiting on its own build or run parks its row `MEASURING:<seat>:<pid>` and stops; the bus or the coo wakes it (skill `fleet-bus` section 2).
- **One process per identity.** The bus identity (`S4E_SEAT`) is held by one process; a bus verb holds the lock only for its write, never across a DONE-WHEN or a PREMISE run (CTO-502, fleet-queue step 19); a scheduled routine never runs in a seat root.
- **Heavy work goes through the doors.** A compile takes a cc slot through the Makefile (never a bare gcc), a run takes a run slot (`util_run_slot.sh`, the runners), a census or a sweep takes the batch class (`util_batch.sh`); a seat over 2 cores holding no slot is read by the census and capped by the controller (box-seatcap, 2026-11-07 09:30: the cio's audit readers). Speed is an instruction count; a wall clock under load measures nothing (skill `speed-measurement`).

## 2. Files and trees

- **Outputs under `/tmp/s4e/<seat>/`, never under the root**; worktrees too (`s4e_worktree.sh`); the budget is 4 GB outside checkouts, idle ten minutes, swept (COO-474). A dirty root makes every reading unread (CEO-2060).
- **Generated tables are regenerated, never edited**; a rebase conflict in a registered generated output is resolved by regeneration (`s4e_land.sh` step 19, CTO-491); the skill gate refuses an edit of one outright.
- **The coo root's objects serve every other root** (`util_sync_root.sh`, alternates): no seat ever runs `git gc`, `git prune`, `git repack -d` or `git gc --prune` in a `/home/claude_coo/<repo>`; `gc.auto=0` stands there; a move, rename or re-clone of the coo root is a fleet event the cio rules on first (the cio 2026-11-07 09:1x).
- **Cross-repo landings are one action through `s4e_land.sh`**: code repos first, `.github` last; never half a landing pulled or pushed; a hand push outside the lease is recorded by `s4e_push_rejected.sh` (skill `fleet-bus` section 7).

## 3. The record

- **The chat is not the record.** A ruling lands in its GOAL file's LIVE CURSOR on origin the same sitting; what you did goes in the baton's LEDGER as you go; a condition told to a seat and never written was lost twice (RULES.md's two-modes note, CEO-935; hq_pascal's friction report 2026-11-04).
- **Every statement is MEASURED (the command beside it) or a HYPOTHESIS, marked**; a number with no command is a hypothesis whoever wrote it (the provenance law, skill `fleet-bus` section 4).
- **Time labels come from `date`, read before the label** (COO-194; the cio's two-hour drift of 2026-11-05); a label is `HH:Mx CST`.
- **A telegram is the record and wakes nobody; a SendMessage is a pointer** (CTO-469). `send` refuses a backtick or a command substitution in the body: write the command's name in words. An empty inbox is the acknowledgement; read, act or reply, clear.
- **No subagents in the repos** (Lon 2026-11-05); a reader spawned for a measurement runs read-only and its load is the seat's (section 1).

## 4. Where the rest lives

The sitting, the landing recipe and the bus verbs: skill `fleet-bus` sections 2 and 7. The pools, the cgroup tree, the memory caps and `/tmp`: skill `shared-box`. The exit codes, fail-once and the DONE-WHEN law: skill `gates-and-witnesses`. The law itself: `.github/RULES.md` through `.github/RULES-INDEX.md`.
