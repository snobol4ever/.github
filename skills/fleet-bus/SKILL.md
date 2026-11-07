---
name: fleet-bus
description: How the fleet coordinates: the officers and seats, MODE and its keyed lines, the postoffice bus (s4e_msg.sh verbs), rows and their batons (GOAL, DONE-WHEN, PREMISE-WHEN, NEXT, QA, LEDGER), the four ports of a task, mint, claim, park, done, the sweep, test requests, telegrams and SendMessage, the wake rule, and the provenance law. Load it before minting, assigning, parking, closing or telegramming, or when a bus verb refuses.
---

# The fleet bus

Law: `.github/RULES.md`. Rulings: `GOAL-CTO.md` LIVE CURSOR. Detail: `reference.md`.

## 1. Who is who (MODE is the record; read it, never prose)

- **Lon is the CEO** (2026-10-31); his word is the go. **THE BOSSES** (MODE `BOSSES: cio coo cto`, Lon 2026-11-04): the **cio** owns the fleet system (bus, records, landings, hygiene, the box controller and dispatcher, wakes; Fable 5.1) and designs the fleet; the **coo** finds the bugs and runs the fleet day to day (the one testing officer: suites, boards, test requests, grading every landing, routing each red with its evidence to its designer); the **cto** designs SCRIP and every design question (Fable 5.1, on call). The **cfo, cao, cqo** (Opus) diagnose reds and write designs with the cio and cto.
- **THE LADDER** (Lon 2026-11-07, COO-481, MODE keyed line `LADDER:`; verbatim: "Do not start work unless it is first designed by CIO or CTO. Then always start tasks at the WORKERS and let them escalate to company men, then general officers, and then finally CIO and CTO to implemenent when no one else can." / "You, CIO, and CTO are the designers since you are seated as Fable 5.1 high." / a design is "of anything that is needed, not just source code, but designing test strategy or fleet strategy in addition to code development."): a task exists only as a DESIGN by the cio (the fleet system, the test cycle) or the cto (SCRIP, the suites), of code, a test strategy or a fleet strategy alike; its steps are rows that meet THE HAIKU BAR below and start in `tier-haiku` or a worker's `seat-<worker>` tube (`mint --tier haiku` or `--to worker_NN`, `queue` for an existing row). Rung 4, the twenty Haiku 5.5 xhigh workers `worker_01` to `worker_20` (no specialty, no lane: a worker works ONLY a job the queue serves it, exactly as written, loading the skills its `SKILLS:` line names; it mints nothing and takes no FREE row). A worker that cannot land its row after one honest try runs `escalate <topic> --stdin` with the measurement: the job moves one tube up, to rung 3, the four Sonnet 5.5 xhigh company men `president vice_president secretary manager`, then to rung 2, the general officers `cfo cao cqo` (Opus), then to the cio or the cto, who implement only when no one else can; at the top the row parks for Lon. A senior starts no task of its own and `next` serves it no job of the tier below: its tubes are `seat-<me>`, `ask-<tier>` and `tier-<tier>`, fed by escalations and asks. A design fix a senior lands comes back down as new rows. The ports `hq_dotnet` and `hq_jvm` keep their names (skill `ports`).
- **THE HAIKU BAR** (Lon 2026-11-07, verbatim: "Ensure the tasks designed by CIO ad CTO are granular enough for Haiku-level workers."; the coo reads every job against it before waking a worker and returns a failing job to its designer; keyed by the cio 07:4x): (1) one row, one `DONE-WHEN:` command that reads RED now and GREEN when done, its probe on disk before the worker starts; (2) one symptom, one cause; a `TOUCHES:` line naming at most three files; one sitting of work, about 150 changed lines at most; (3) a `## NEXT` that spells it out in order: the reproduce command, the oracle command, the file and function to change, what to change, and the proof commands (the DONE-WHEN, both modes, the feature reps, the smoke, `s4e_land.sh`); (4) a `SKILLS:` line naming every skill the touched files need; (5) no open design question: every choice is made in the step text; a step that asks the worker to decide a design is too big. After landing, the coo measures each design's escalation rate over its last 20 outcomes; over 30 percent, the designer re-cuts smaller.
- `head -1 /home/resources/postoffice/MODE` is the mode (TENET today); line 2 is the dated head block of rulings, newest first; the keyed lines `ROSTER:` `LANES:` `ORDER-OF-WORK:` `BOSSES:` `ON-CALL:` `FLEET:` are machine-read (`FLEET: IDLE` passes every seat at its Stop; `FLEET: IDLE EXCEPT <seats>` holds only those named). A MODE edit: back up beside it, edit, `util_mode_cap.sh --check` (head -2 under 8192 bytes; `--apply` archives older blocks) and `.github/scripts/mode_flip.sh --check` rc 0.
- **The go** (CEO-2071): an `assign` or a SendMessage from an officer naming a row is Lon's go; a question never stops the work; only Lon answers a permission prompt.

## 2. The bus: `bash harness/scripts/s4e_msg.sh <verb>` from the root

Run verbs one at a time. Full text: `reference.md` section 2.

- `next` serves tube jobs, then ASSIGNED rows, then your claim.
- `claim <topic>` takes a FREE or ASSIGNED row; cap two live.
- `unclaim <topic>` releases your claim; the row goes FREE.
- `park <topic> <STATE>` sets the state (MEASURING for a live measurement).
- `done <topic>` closes on rc 0; refuses a red, rc 2, or no claim.
- `assign <seat> <topic>` writes `ASSIGNED:<seat>` and the claim.
- `reown <seat> <topic>` changes the owner column only.
- `mint <topic> ... --stdin` is the only way to add work.
- `recut <topic> --stdin` replaces DONE-WHEN or PREMISE-WHEN.
- `queue <topic> --tier|--to <seat>` moves a FREE or QUEUED row to a tube.
- `expire <topic>` is the tick's verb for a claim whose job is back.
- `rule <GOAL-file> <ID> --stdin` writes one ruling; refuses a used id.
- `resume <topic> ...` writes the RESUME line; write it before a stop.
- `ask <topic> ...` sends a question up the ladder (the ask tube of the tier above); `answer <topic> --stdin` is the senior's reply, delivered to the asker's inbox.
- `escalate <topic> --stdin` moves a job one tube up with the measurement in the body (refused without one); the baton gets an ESCALATION section.
- `send <seat> <topic> --stdin` is a telegram; wakes nobody.
- `check` displays the inbox.
- `clear` archives what check displayed.
- `mailbox` lists your mailbox.
- `sweep` moves receipted DONE rows to the done file.
- `board` is the computed board.
- `banner` is the Stop hook's banner.
- `fleet` is the fleet view.
- `whoami` names your identity.
- `premise <topic>` reads the PREMISE-WHEN through the bus.

## 3. The baton: `/home/resources/postoffice/tasks/<topic>.task.md`

The baton holds GOAL, DONE-WHEN, PREMISE-WHEN, LINKS, one `## NEXT`, QA and LEDGER. Full text: `reference.md` section 3.

## 4. The rules every row obeys

Every statement is measured or marked a hypothesis; a row exists only while a measurement says so. Full text: `reference.md` section 4.

## 5. Telegrams, SendMessage and the wake rule (CTO-469)

A telegram is the record and wakes nobody; the coo wakes a seat only once its work is assigned. Full text: `reference.md` section 5.

## 6. Ending a sitting

Hand-off checks: `handoff_status.sh` rc 0, everything pushed, one plain closing line. Full text: `reference.md` section 6.

## 7. The sitting and the landing

**Every sitting.** (1) `bash harness/scripts/util_sync_root.sh`; `cd SCRIP && make -j8`; never `git gc` or `git prune` in a coo-root repo. (2) `head -2 /home/resources/postoffice/MODE`. (3) Your rows in QUEUE.tsv; each NEXT; your LIVE CURSOR. (4) `s4e_msg.sh check`; act or reply; `clear`. (5) `s4e_msg.sh next`; load the gate's skills first. (6) One row at a time. (7) Hand off: NEXT and LEDGER written, pushed, `handoff_status.sh` rc 0; park the wait (`PARKED-AWAITING:`, `BLOCKED-ON:`, `MEASURING:<seat>:<pid>`); stop.

**The landing recipe.** (1) Reproduce with `monitor_run.sh <prog> --oracle`. (2) Criterion first: a DONE-WHEN red now, each line starting `cd "${S4E_HOME:?REFUSE(2): S4E_HOME unset}" &&`. (3) Cure in a clean `git worktree`; never edit a generated table. (4) Prove: DONE-WHEN green; both modes against the oracle; `test_feature_reps.sh`; the smoke. (5) Land: `s4e_land.sh --probe`, then `s4e_land.sh --row <topic>`; by hand only on refusal. (6) Record the LEDGER and NEXT; `claim` then `done` once the coo's reading is green.

**The fleet check (Lon 2026-11-07, CTO-541).** When Lon asks any seat for a fleet check, run `python3 harness/scripts/fleet_check.py` and paste what it prints AS IT IS: a 6x5 markdown grid of the thirty seats, a coloured square and a few measured words per cell; never in a code fence (dark blue on black), never HTML, never a hand-kept note; on demand only. Detail: reference.md section 7.

## 8. DESIGN: fleet-queue (the cio, 2026-11-05)

The queue design: tubes, tick, escalation and acceptance. Full text: `reference.md` section 8.

## 9. DESIGN: skills-complete (the cio, 2026-11-07)

Every name a skill speaks is live, the gate fires on exactly the files a skill owns, each law has one home, and the drift reads RED by a census (`util_skill_refs_census.py --check`, its gate `test_gate_skills_name_live_files.sh`, the plan `corpus/tests/shared/skills_complete/STEPS.tsv`, `test_design_skills_complete_steps.sh`). The full text is `reference.md` section 9.
