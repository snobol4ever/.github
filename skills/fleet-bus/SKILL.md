---
name: fleet-bus
description: How the fleet coordinates: the officers and seats, MODE and its keyed lines, the postoffice bus (s4e_msg.sh verbs), rows and their batons (GOAL, DONE-WHEN, PREMISE-WHEN, NEXT, QA, LEDGER), the four ports of a task, mint, claim, park, done, the sweep, test requests, telegrams and SendMessage, the wake rule, and the provenance law. Load it before minting, assigning, parking, closing or telegramming, or when a bus verb refuses.
---

# The fleet bus

The law is `.github/RULES.md`; the postoffice's own rules are `/home/resources/postoffice/PROTOCOL.md` (cto custody); the rulings are `CTO-NNNN` entries in `GOAL-CTO.md`'s LIVE CURSOR (the fired ceo seat's series CEO-1 to CEO-2133 is closed in `GOAL-CEO.md` and is cited as the record, CTO-469). Detail and every verb's behaviour are in `reference.md` beside this file.

## 1. Who is who (MODE is the record; read it, never prose)

- **Lon is the CEO** (2026-10-31). The **cto** is the officer in charge and the designer: rulings, DESIGN-PLANs, MODE custody, grants put to Lon (CEO-2089/2095). The **coo** is the admin boss and the one testing officer: the loop, the board, the queue, assignments, the suite table, test requests (CEO-1342, CEO-2095). The cfo, cao and cqo are officers; the `hq_*` seats work their lanes.
- `head -1 /home/resources/postoffice/MODE` is the mode (SOLO, DUO, TRIO, QUARTET, TENET); line 2 is each seat's business, newest block first; the keyed lines `ROSTER:` `LANES:` `ORDER-OF-WORK:` `CONCERNS:` `REPORT-TO-LON:` are machine-read. A MODE flip: back up, one edit at the head of line 2, `.github/scripts/mode_flip.sh --check` rc 0.
- **The go** (CEO-2071): an `assign` or a SendMessage from the cto or the coo naming a row is Lon's go; a question never stops the work; only Lon answers a permission prompt.

## 2. The bus: `bash harness/scripts/s4e_msg.sh <verb>` from the root

`next claim unclaim park done assign reown mint rule resume ask send check clear mailbox sweep board banner fleet whoami premise`. Run bus verbs one at a time with absolute paths; never pipe one into a short read; a send during a bus lock delivers nothing.

- **next** serves rows ASSIGNED to you, then your unfinished claim, then FREE rows by rank. A seat holds at most two live claims (CEO-2078); an ASSIGNED row not yet running does not count.
- **mint** `<topic> [rank] [--owner <seat>] --stdin` is the only way to add work: a GOAL with its own `DONE-WHEN:` and `PREMISE-WHEN:` lines. A topic needs a language prefix or `--owner`. Mint refuses a prose criterion.
- **done** `<topic>` runs the DONE-WHEN and refuses a red; the claim is untouched on a refusal. A criterion over `S4E_DONE_TIMEOUT` refuses rc 2 (could not measure). `S4E_DONE_OVERRIDE="why"` is loud and written into the claim.
- **park** `<topic> <STATE>`: `PARKED-AWAITING:<request-id>` (waiting on the coo's verdict), `BLOCKED-ON:<topic>` (waiting on another row; it clears when that row is DONE), `PARKED-LON-HOLD:<why>`, `GRANT-NEEDED:<why>`. `MEASURING:<seat>:<pid>` (your own live measurement: accepted while the pid is alive and yours; the Stop gate passes the row while it lives and blocks the moment it ends; the sweep reverts a dead-pid row to ASSIGNED).
- **claim notices** (step 21): a claim tells only the seats whose live rows touch a path the claimed row touches, by prefix, from the batons' `TOUCHES:` lines (else the `Landing files:` words); a row with no `TOUCHES:` tells nobody and the claim says so. Put `TOUCHES: <path prefixes under the root>` on every live baton; a notice names the overlapping paths and needs no reply unless your measurement moves.
- **resume** `<topic> --tree <path> --command '<cmd>' --state <word> --log <path>` (step 16): one timestamped RESUME line under `## RESUME`, newest first, which `next` prints before anything but the MODE line; `resume <topic>` reads the newest. Write it before any stop.
- **the Stop gate** (step 10): a seat holding unread mail or a row ASSIGNED, CLAIMED or MEASURING-with-a-dead-pid cannot end its turn; its hook continues it with the row and its NEXT (12 continuations an hour). Park a row before waiting on it.
- **rule** `<GOAL-file> <ID> --to <seat,seat> --row <topic> --stdin` (headline line, then body; CTO-496 box-scheduler step 12): ONE act writes a ruling once -- the bullet at the head of the GOAL file's LIVE CURSOR, committed alone, rebased and pushed; a telegram to each named seat citing the hash; the row's baton LEDGER line. Every input is checked before the first write; an id already heading a bullet refuses; a failed push undoes the commit. `rule --probe` proves it on scratch.
- **send** `<seat> <topic> --stdin` with a quoted heredoc; it refuses a backtick or a command substitution. **check** displays the inbox; **clear** archives exactly what check displayed. An empty inbox is the acknowledgement.

## 3. The baton: `/home/resources/postoffice/tasks/<topic>.task.md`

Line 1 is `# TASK <topic>` and nothing else (state lives only in `QUEUE.tsv`: rank, topic, owner, state). Then `GOAL:`, `DONE-WHEN:` (a command, rc 0 green; `${S4E_HOME:?}` is its root), `PREMISE-WHEN:` (rc 0 while the problem exists), `LINKS:`, then `## NEXT` (exactly one, first, the β re-entry point; a replaced block is demoted to `## SUPERSEDED-NEXT`), `## QA`, `## LEDGER` (append-only, newest first, receipts). A task is a generator whose frame outlives its activation: α claim, β resume at NEXT, γ the computed DONE-WHEN, ω concede with the reason written.

## 4. The rules every row obeys

- **The provenance law**: every statement is MEASURED (the command beside it) or a HYPOTHESIS, marked. A number with no command is a hypothesis, whoever wrote it.
- **A row exists only while a measurement says so** (CEO-1386/553/555): a DONE-WHEN a deletion satisfies is false; a DONE-WHEN is proven red once and green once at mint (the mint receipt names both witnesses); a test that cannot measure refuses rc 2 (CEO-1680).
- **A row name states the symptom, never the hypothesis**; a lane is decided by the cure, never by a noun in the name.
- **The chat is not the record**: a ruling lands in its GOAL file's LIVE CURSOR on origin before the sitting ends; what a seat did goes in the baton's LEDGER.
- **Tests**: a lander runs its program in both modes, `test_feature_reps.sh`, and the smokes; the suites are the coo's, asked for by `s4e_test_request.sh` (at most eight programs).

## 5. Telegrams, SendMessage and the wake rule (CTO-469)

- A telegram (`send`) is the record and is read at the recipient's next sitting; it wakes nobody. A SendMessage is a pointer that starts a turn. `send ceo` is refused: that seat was fired 2026-10-31.
- To the cto: a ruling ask, a design gap, a grant. To the coo: a cross-seat fact, a claim collision, a test request, a red. Unsure: both.
- THE WAKE RULE (Lon 2026-11-04: "You ensure that the seat HAS WORK first, and then you wake it."): the coo, every tick, for each ROSTER seat with no live row and an idle session, finds its work (a red in its language, or an ASSIGNED or FREE row it can serve), mints what is not yet a row, assigns it, and only then sends the SendMessage naming the row. A seat with a RUNNING row and an idle session is sent its row. No wake list, no WAKE.txt. The cto wakes nobody.
- A seat that stops because it waits parks the wait first (`PARKED-AWAITING:` or `BLOCKED-ON:`), shows its banner and stops; a seat that finished its row hands off and stops, and the coo gives it work and wakes it.

## 6. Ending a sitting

The baton's NEXT rewritten, the LEDGER written, the seat's LIVE CURSOR moved, everything pushed (code repos first, `.github` last; a rejected push is logged with `s4e_push_rejected.sh`), and `bash harness/scripts/handoff_status.sh` pasted verbatim.
