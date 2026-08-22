# PROTOCOL v2 — DRAFT (⛔ NOT LIVE; Lon activates per ARCH-FLEET-CEO.md rollout V2-6)

Staged 2026-08-22 s257 by CEO (Fable). Replaces postoffice `PROTOCOL.md` ONLY when Lon flips it at a fleet-quiet boundary, AFTER V2-1…V2-5 land and every seat re-pulls SCRIP. Versioned here in `.github` because v1's law lived in one unversioned copy on one box (s191 row `postoffice-git-home`) — on flip, the postoffice copy is written from this file and says so in its header.

## THE SEAT LOOP (what changes from v1 is marked ⭐)

At EVERY prompt, from SCRIP/:
1. `bash scripts/s4e_msg.sh check` — inbox is a DOORBELL, not a document: ⭐ any message about your task says "re-read your task file"; the task file is always authoritative. Read → act/reply → `clear`.
2. `bash scripts/s4e_msg.sh next` — serves, in order: ⭐ tasks ASSIGNED to you → your unfinished claim → rank-sorted FREE tasks. It prints the task file path `/home/resources/postoffice/tasks/<topic>.task.md`. Read GOAL + NEXT (⭐ not the whole ledger). Execute NEXT exactly.
3. Work. NON-BLOCKING default unchanged (v1 LAW 17): a surprising number is a ledger line, not a stop. ⭐ Questions go in the task file's QA section AND a doorbell to your owning HQ (`ask`); if the answer gates ALL remaining work, set state BLOCKED and take `next` again — the task leaves the picker until HQ answers in the file and re-FREEs it.
4. ⭐ SUSPEND IS THE HANDOFF: before you stop (or whenever a rung lands), append PROVEN/DISPROVEN lines with receipts and REWRITE the NEXT block so any seat resumes without you. The Stop-hook banner flags a RUNNING task whose NEXT you never touched.
5. DONE = the task's DONE-WHEN command exits 0 AND `handoff_status.sh` COMPLETE. `done <topic>`, `board`, `next` again. Banner stays automatic and computed — never hand-type a verdict.
6. Clone trouble: unchanged from v1 — disposable clone, SAVE-BEFORE-RECLONE, no destructive git, ever.
7. Lon's word beats every file, and the override routes back the same session — unchanged.

## THE HQ LOOP (hq_C correctness · hq_P performance; MEASURE FREELY, CURE NEVER)

Strict order, every HQ session: **1 DRAIN** (answer every pending seat question into the task files' QA; your banner refuses ✅ while inbox mail is >30 min old) → **2 VERIFY** (run the DONE-WHEN of anything claiming γ; sample one older DONE) → **3 MINT** (new tasks: computed DONE-WHEN that a correct fix CAN meet and a wrong fix CANNOT; WIP cap ≤ 2× live seats; dedupe against tasks/ AND QUEUE.done.tsv) → **4 ASSIGN** (`assign <seat> <topic>` — the mail and the lock are one atomic act). Cross-HQ: a task that crosses the correctness/speed line ω-flips owner with one ledger line; disagreements escalate to `ceo` and the task BLOCKs till ruled. HQs propose law; only CEO lands it.

## THE MECHANICS (V2-1…V2-5 must be landed before flip)

- `next`: rank-sort free rows; assigned-first; presence-asserted (a topic with no task file is a loud error, never silence).
- QUEUE.tsv = index only: `rank · topic · owner · state`. Briefs/state live in `tasks/<topic>.task.md`. DONE rows auto-sweep to `QUEUE.done.tsv`.
- Identity asserted against an existing mailbox; no mailbox auto-creation; `check` sweeps orphaned `.msg.*` temp files; the fleet census enumerates postoffice mailboxes (hq_C/hq_P included), never home-dir globs.
- Task file format + the four ports (α claim · β resume · γ computed-done · ω concede/handover): normative definition in `ARCH-FLEET-CEO.md` — one block, ≤15-line NEXT, append-only ledger, QA rides the baton.
- Gates cited by any DONE-WHEN must pass negative-injection (can say NO). seat16's audit (`rung-gate-false-green-audit`) is the conversion worklist.
