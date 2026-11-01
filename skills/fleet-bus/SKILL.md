---
name: fleet-bus
description: How the fleet coordinates: the officers and seats, MODE and its keyed lines, the postoffice bus (s4e_msg.sh verbs), rows and their batons (GOAL, DONE-WHEN, PREMISE-WHEN, NEXT, QA, LEDGER), the four ports of a task, mint, claim, park, done, the sweep, test requests, telegrams and SendMessage, the wake rule, and the provenance law. Load it before minting, assigning, parking, closing or telegramming, or when a bus verb refuses.
---

# The fleet bus

The law is `.github/RULES.md`; the postoffice's own rules are `/home/resources/postoffice/PROTOCOL.md` (cto custody); the rulings carry their numbers in `GOAL-CEO.md`. Detail and every verb's behaviour are in `reference.md` beside this file.

## 1. Who is who (MODE is the record; read it, never prose)

- **Lon is the CEO** (2026-10-31). The **cto** is the officer in charge and the designer: rulings, DESIGN-PLANs, MODE custody, grants put to Lon (CEO-2089/2095). The **coo** is the admin boss and the one testing officer: the loop, the board, the queue, assignments, the suite table, test requests (CEO-1342, CEO-2095). The cfo, cao and cqo are officers; the `hq_*` seats work their lanes.
- `head -1 /home/resources/postoffice/MODE` is the mode (SOLO, DUO, TRIO, QUARTET, TENET); line 2 is each seat's business, newest block first; the keyed lines `ROSTER:` `LANES:` `ORDER-OF-WORK:` `CONCERNS:` `REPORT-TO-LON:` are machine-read. A MODE flip: back up, one edit at the head of line 2, `.github/scripts/ceo_mode_flip.sh --check` rc 0.
- **The go** (CEO-2071): an `assign` or a SendMessage from the cto or the coo naming a row is Lon's go; a question never stops the work; only Lon answers a permission prompt.

## 2. The bus: `bash harness/scripts/s4e_msg.sh <verb>` from the root

`next claim unclaim park done assign reown mint ask send check clear mailbox sweep board banner fleet whoami premise`. Run bus verbs one at a time with absolute paths; never pipe one into a short read; a send during a bus lock delivers nothing.

- **next** serves rows ASSIGNED to you, then your unfinished claim, then FREE rows by rank. A seat holds at most two live claims (CEO-2078); an ASSIGNED row not yet running does not count.
- **mint** `<topic> [rank] [--owner <seat>] --stdin` is the only way to add work: a GOAL with its own `DONE-WHEN:` and `PREMISE-WHEN:` lines. A topic needs a language prefix or `--owner`. Mint refuses a prose criterion.
- **done** `<topic>` runs the DONE-WHEN and refuses a red; the claim is untouched on a refusal. A criterion over `S4E_DONE_TIMEOUT` refuses rc 2 (could not measure). `S4E_DONE_OVERRIDE="why"` is loud and written into the claim.
- **park** `<topic> <STATE>`: `PARKED-AWAITING:<request-id>` (waiting on the coo's verdict), `BLOCKED-ON:<topic>` (waiting on another row; it clears when that row is DONE), `PARKED-LON-HOLD:<why>`, `GRANT-NEEDED:<why>`.
- **send** `<seat> <topic> --stdin` with a quoted heredoc; it refuses a backtick or a command substitution. **check** displays the inbox; **clear** archives exactly what check displayed. An empty inbox is the acknowledgement.

## 3. The baton: `/home/resources/postoffice/tasks/<topic>.task.md`

Line 1 is `# TASK <topic>` and nothing else (state lives only in `QUEUE.tsv`: rank, topic, owner, state). Then `GOAL:`, `DONE-WHEN:` (a command, rc 0 green; `${S4E_HOME:?}` is its root), `PREMISE-WHEN:` (rc 0 while the problem exists), `LINKS:`, then `## NEXT` (exactly one, first, the β re-entry point; a replaced block is demoted to `## SUPERSEDED-NEXT`), `## QA`, `## LEDGER` (append-only, newest first, receipts). A task is a generator whose frame outlives its activation: α claim, β resume at NEXT, γ the computed DONE-WHEN, ω concede with the reason written.

## 4. The rules every row obeys

- **The provenance law**: every statement is MEASURED (the command beside it) or a HYPOTHESIS, marked. A number with no command is a hypothesis, whoever wrote it.
- **A row exists only while a measurement says so** (CEO-1386/553/555): a DONE-WHEN a deletion satisfies is false; a DONE-WHEN is proven red once and green once at mint (the mint receipt names both witnesses); a test that cannot measure refuses rc 2 (CEO-1680).
- **A row name states the symptom, never the hypothesis**; a lane is decided by the cure, never by a noun in the name.
- **The chat is not the record**: a ruling lands in its GOAL file's LIVE CURSOR on origin before the sitting ends; what a seat did goes in the baton's LEDGER.
- **Tests**: a lander runs its program in both modes, `test_feature_reps.sh`, and the smokes; the suites are the coo's, asked for by `s4e_test_request.sh` (at most eight programs).

## 5. Telegrams, SendMessage and the wake rule (CEO-2107)

- A telegram (`send`) is the record and is read at the recipient's next sitting; it wakes nobody. A SendMessage is a pointer that starts a turn.
- To the cto: a ruling ask, a design gap, a grant. To the coo: a cross-seat fact, a claim collision, a test request. Unsure: both.
- Wake a seat only if it has not finished its row: a SendMessage goes to a seat with a RUNNING row and an idle session, to name that row. A seat that finished is started only by Lon's `/clear` and `next`; the coo assigns its next row ahead so `next` serves it.
- A seat that stops because it waits parks the wait first (`PARKED-AWAITING:` or `BLOCKED-ON:`), shows its banner and stops.
- The wake list (`s4e_msg.sh wake`, `postoffice/WAKE.txt`) is designed (`reference.md` § 6) and is the coo's ASSIGNED row; neither the verb nor the file exists on 2026-11-01.

## 6. Ending a sitting

The baton's NEXT rewritten, the LEDGER written, the seat's LIVE CURSOR moved, everything pushed (code repos first, `.github` last; a rejected push is logged with `s4e_push_rejected.sh`), and `bash harness/scripts/handoff_status.sh` pasted verbatim.
