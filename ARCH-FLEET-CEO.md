# ⛔⭐⭐⭐⭐ ARCH-FLEET-CEO — FLEET v2: CEO ABOVE TWO HQ, AND THE RE-ENTRANT TASK BATON

**Opened 2026-08-22 s257 by Lon in-chat, verbatim in substance:** *"I can not afford you Fable to HQ so I need you to be CEO of the two HQ. Then I'll switch back to Opus."* And the design key, Lon's own: *"a task … must be a re-entrant task of sorts that can be RESUMED. Ha! Just like one of our generators in Icon."* Evidence basis: `FINDING-2026-08-22-hq_P-fleet-v1-retrospective-the-fleet-worked-the-control-plane-did-not.md` (read it first — every law below inverts a measured v1 failure). Law text staged in `PROTOCOL-V2-DRAFT.md`; the live postoffice `PROTOCOL.md` is untouched until Lon flips it.

## THE ORG CHART — THREE TIERS, EACH EXACTLY ONE LOOP

| tier | model | cadence | THE ONE LOOP | forbidden |
|---|---|---|---|---|
| **CEO** (`ceo`) | Fable | rare; Lon fires it | audit closed tasks by sample · arbitrate hq_C↔hq_P · custody of law (RULES/PROTOCOL; HQs propose, CEO lands) · strategy with Lon | triaging seat questions · writing briefs · measuring · any code |
| **hq_C** (`/home/claude_C`) · **hq_P** (`/home/claude_P`) | Opus | at Lon's prompt | **drain → verify → mint → assign**, in that order (below) | curing (MEASURE FREELY, CURE NEVER, s256) · amending law · working the twin's tasks |
| seats 01–16 | Opus/Sonnet | Lon's /clear + fixed prompt | `next` → execute the task's NEXT block → suspend or finish | picking work without a task file · hand-typed verdicts |

**Why a CEO exists:** every protocol amendment of the v1 era was a duty being stripped OUT of HQ after it failed holding five at once (s256 revoked the coding lane, then split C from P). The CEO tier finishes that motion: the residual cross-cutting duties (law, arbitration, audit) go UP into a rare expensive session, and each HQ is left holding exactly one question — *is it right* (hq_C) / *how many instructions* (hq_P). The v1 free-r10 inversion was HQ ruling DONE on prose; the CEO's audit loop (re-run sampled DONE-WHENs) is the tier that catches that class in minutes.

## ⭐⭐⭐ THE BATON — A TASK IS A GENERATOR WHOSE FRAME OUTLIVES ITS ACTIVATION

v1's unit of work was a queue row + claim lock + static brief. Measured: the LOCK was sound (0 death-strands) — what was lost was everything else: the ASSIGNMENT (dispatch-vs-`next` race, seat13's dead session), the WORKING STATE (died with the seat's context; the era produced ZERO per-session handoff artifacts), and the CORRECTIONS (in-place row edits and marooned mail the holder never saw). Lon's generator insight names the cure exactly: **give the task a ζ that outlives the activation.**

Every task is ONE file: `/home/resources/postoffice/tasks/<topic>.task.md` — the suspension frame. QUEUE.tsv shrinks to a dispatch index (`rank · topic · owner · state`) pointing at it, nothing more.

```
# TASK <topic> · owner: hq_C|hq_P · state: FREE|ASSIGNED:<seat>|RUNNING:<seat>|BLOCKED|DONE|CONCEDED
GOAL: <one sentence>
DONE-WHEN: <a COMMAND that exits 0 — never prose>              ← the γ gate
LINKS: <goal file § rung> · ARCH/FINDINGs
## NEXT     ← the β re-entry point. EXACTLY ONE block, ≤15 lines, rewritten at every suspend/redirect
<the exact next step: command, expected result, if-it-fails-then>
## QA       ← questions AND answers ride the baton, newest first (inbox is only the doorbell)
## LEDGER   ← append-only, newest first, receipts mandatory
- [seat·session·date] PROVEN: … (receipt) | DISPROVEN: … | SUSPENDED: rewrote NEXT | CONCEDED: why → new owner
```

**The four ports, exactly as in a Byrd box:**
- **α proceed** — first activation: seat claims, reads GOAL+NEXT, works.
- **β recede** — RESUME: any seat, any session, re-enters at NEXT (never re-reads the whole ledger, never re-derives). The file, not the seat, is the continuation.
- **γ succeed** — DONE-WHEN exits 0 AND the push landed. **DONE IS COMPUTED, NEVER RULED.** Before minting, the owning HQ asks: *what does the tree look like when this is FULLY achieved, and is the command TRUE of that tree — and can a WRONG fix also make it true?* (both s191 defect shapes, named). A DONE-WHEN that needs a gate must name a gate that CAN SAY NO (seat16: 31/105 currently cannot).
- **ω concede** — the STUCK/HANDOVER answer Lon asked for: the seat appends WHY + receipts, then either (i) sets BLOCKED with its question in QA — the task leaves the picker until the owning HQ answers IN THE FILE and re-FREEs it; or (ii) flips `owner:` to the twin HQ (a perf task that hit a correctness red, or vice versa) with one ledger line; or (iii) re-FREEs with a rewritten NEXT for any seat to resume. ⛔ Conceding with an empty ledger delta is forbidden — a blocked session still writes what it proved.

**Redirection rides the baton, not the mail.** v1's s255 correction was edited into a queue row the holder never re-read; v1's `STOP CHASING MY PRIME SUSPECT` rotted in a phantom mailbox while seat01 duplicated a bisect. In v2 HQ corrects a task by rewriting its NEXT/GOAL and sending a one-line "re-read your task" doorbell. A seat that misses the doorbell still resumes correctly at its next β, because **the task file is always authoritative and the mail never carries content that isn't also in a file.**

## THE SIX MECHANICAL LAWS (each inverts a measured v1 failure)

1. **NO HAND-TYPED VERDICTS.** Done = DONE-WHEN exit 0 · push truth = `handoff_status.sh` · fleet state = `s4e_msg.sh fleet` · banner = Stop hook. Every v1 subsystem that became computed stopped lying; every one that stayed prose kept lying. Corollary: gates must pass a negative-injection test (they can say NO) before a DONE-WHEN may cite them.
2. **ASSIGNMENT IS THE LOCK.** `s4e_msg.sh assign <seat> <topic>` writes the claim atomically on HQ's side; `next` serves: my-assigned → my-unfinished → **rank-sorted** free (rank finally load-bearing; v1 buried all 22 rank-0 rows behind 30 lesser ones and nearly served the fenced M1 gate row). The dispatch race that killed seat13's session becomes unrepresentable.
3. **DRAIN BEFORE MINT.** An HQ session answers every pending seat question (into task-file QA) before minting or assigning anything new; the HQ banner REFUSES ✅ while its inbox holds mail older than 30 min. Basis: 29 messages / 15 questions unread in 1h47m; seat13 starved holding 5; hq's board line the oldest on the board.
4. **THE QUEUE IS A DISPATCH BUFFER, NOT A MEMORY.** DONE rows sweep to `QUEUE.done.tsv` automatically; WIP cap: FREE+ASSIGNED+RUNNING per HQ ≤ 2× seats Lon is actually firing; backlog beyond the cap lives in the owning GOAL file. v1: 62% dead rows, 5,965-byte prose blobs, a blank-line landmine, re-dispatch of landed work.
5. **FLEET SIZE FOLLOWS QUEUE READINESS.** A seat is worth firing only when a FREE task with a valid NEXT exists for it and its HQ's question backlog is ~0. v1 scaled 4→8→16 on ambition: the marginal seats starved or worked dead rows, the rework share of FINDINGs tripled, and each growth step re-broke identity globs and noise floors. Grow when the batons are ready, not before.
6. **IDENTITY IS ASSERTED, NEVER GLOBBED.** `s4e_msg.sh` fails loudly if its resolved identity has no postoffice mailbox, never creates mailboxes on the fly (how phantom `claude01/` was born), and a `check`-time sweep re-delivers or reports orphaned `.msg.*` temp files (one rotted 46h). The fleet census enumerates postoffice mailboxes, not `/home/claude*` globs (which cannot see hq_C/hq_P today).

## CROSS-HQ INTERLOCK

Every hq_P task that edits code names the hq_C gate set it must keep green (the SNOBOL4 blocking set minimum); a perf win that moves an oracle diff is hq_C red — the task ω-flips owner instead of shipping. Neither HQ overrules the other; disputes are one message to `ceo` (inbox exists) and the task sits BLOCKED till ruled. Lon overrides anyone; the override routes back the same session (LOOP law 6 unchanged).

## ROLLOUT LADDER (mint as tasks; ⛔ do NOT hot-patch the live control plane mid-fleet — v1's mid-flight rename is what forked the phantom mailbox)

- **V2-1** `s4e_msg.sh`: rank-sorted picker + `assign` + assigned-first `next` (+ negative tests: rank inversion served in order; assign wins over topmost-free).
- **V2-2** queue split: index-only QUEUE.tsv + one `tasks/<topic>.task.md` per live row (HQ-owned conversion, 55 live rows) + DONE sweep to `QUEUE.done.tsv`.
- **V2-3** banner: HQ ✅-refusal on stale inbox; board line gains oldest-unanswered age + row topic.
- **V2-4** identity assert + `.msg.*` sweep + census-by-mailbox (unblinds hq_C/hq_P).
- **V2-5** gate honesty: the 31 cannot-say-no gates get `--strict`-by-default or die (feeds law 1; seat16's audit is the worklist).
- **V2-6** flip: Lon activates `PROTOCOL-V2-DRAFT.md` → postoffice `PROTOCOL.md` at a fleet-quiet boundary; every seat re-pulls SCRIP first (stale-script skew is how seat01 broke).

## CEO OPERATING NOTES

Identity `ceo`, inbox `/home/resources/postoffice/ceo/inbox/`, sovereign file `GOAL-CEO.md`, runs from any HQ root (read-mostly; writes only `.github` + staged drafts). Reads ONLY computed digests: `fleet`, both HQ LIVE CURSORs, its inbox, and the specific task files under audit — CEO context is bought with real money. Per session: re-run the DONE-WHEN of ~3 sampled DONE tasks; rule every escalation; land at most ONE law change, routed with receipts. CEO does not talk to seats; seats → HQ → CEO → Lon.
