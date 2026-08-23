# ⛔⭐⭐⭐⭐ ARCH-FLEET-CEO — FLEET v2: CEO ABOVE TWO HQ, AND THE RE-ENTRANT TASK BATON

**Opened 2026-08-22 s257 by Lon in-chat, verbatim in substance:** *"I can not afford you Fable to HQ so I need you to be CEO of the two HQ. Then I'll switch back to Opus."* And the design key, Lon's own: *"a task … must be a re-entrant task of sorts that can be RESUMED. Ha! Just like one of our generators in Icon."* Evidence basis: `FINDING-2026-08-22-hq_P-fleet-v1-retrospective-the-fleet-worked-the-control-plane-did-not.md` (read it first — every law below inverts a measured v1 failure). Law text staged in `PROTOCOL-V2-DRAFT.md`; the live postoffice `PROTOCOL.md` is untouched until Lon flips it.

## ⛔⭐ MODE NOTICE (Lon s259) — **THIS DOCUMENT DESCRIBES FLEET MODE, WHICH IS NOT THE DEFAULT**

**DUO is the default and is where the project actually operates:** Lon watching, `hq_C`, `hq_P`, `ceo`, and **no seats**. Lon, verbatim: *"There are two modes and you better know which mode you are in. And the DEFAULT is DUO mode... We'll probably NEVER be in FLEET mode."* Read everything below as the contingency design, and enter it only on Lon's explicit word.

⛔ **In DUO, the s256 delegate-only rule (the hq_C/hq_P row in the table below) is REVOKED — the HQs measure AND cure.** That rule's own test was *"does this end in a brief in a seat's inbox?"*, and in DUO there is no inbox to end in. What survives from this document in DUO: LAW 0 (provenance), LAW 1 (no hand-typed verdicts), the baton format as a note-to-self, and the postoffice as the hq_C↔hq_P↔ceo bus.

## THE ORG CHART — THREE TIERS, EACH EXACTLY ONE LOOP

| tier | model | cadence | THE ONE LOOP | forbidden |
|---|---|---|---|---|
| **CEO** (`ceo`, `/home/claude`) | Fable | rare; Lon fires it | audit closed tasks by sample · arbitrate hq_C↔hq_P · custody of law (RULES/PROTOCOL; HQs propose, CEO lands) · strategy with Lon | triaging seat questions · writing briefs · measuring · any code |
| **hq_C** (`/home/claude_C`) · **hq_P** (`/home/claude_P`) | Opus 5 (Max) — Lon s257 | at Lon's prompt | **drain → verify → mint → assign**, in that order (below) | curing (delegate-only, s256 — FLEET only) · amending law · working the twin's tasks |
| seats 01–16 | Sonnet 5 — 8 active + 8 reserve (Lon s257; reserves fire only per the scale rule) | Lon's /clear + fixed prompt | `next` → execute the task's NEXT block → suspend or finish | picking work without a task file · hand-typed verdicts |

**Why a CEO exists:** every protocol amendment of the v1 era was a duty being stripped OUT of HQ after it failed holding five at once (s256 revoked the coding lane, then split C from P). The CEO tier finishes that motion: the residual cross-cutting duties (law, arbitration, audit) go UP into a rare expensive session, and each HQ is left holding exactly one question — *is it right* (hq_C) / *how many instructions* (hq_P). The v1 free-r10 inversion was HQ ruling DONE on prose; the CEO's audit loop (re-run sampled DONE-WHENs) is the tier that catches that class in minutes.

## ⭐⭐ TWO OPERATING MODES — DUO AND FLEET (Lon, 2026-08-22 s259, in-chat to CEO, verbatim in substance: *"they run in two modes: (1) DUO where it is only 2 HQ's and a CEO, and (2) with a FLEET"*)

- **DUO** — 2 HQs + CEO, no seats fired. the delegate-only rule is **SUSPENDED**: the HQs do the work themselves (Lon s259 to hq_P, verbatim in substance: *"You are the only one working. There is no FLEET"* — routed GOAL-HQ-PERFORM.md). "Dispatched" is not an action in DUO — a row nobody will work is a row the owning HQ works.
- **FLEET** — seats are fired. the delegate-only rule re-binds on both HQs in full (a fix is a baton + `assign`, never an HQ edit); the seat loop, firing gate, and abort/shrink criteria of GOAL-CEO.md apply.
- ⭐⭐ **CURRENT MODE (this line is THE authority — CEO rewrites it at every Lon declaration; a fresh session reads it BEFORE assuming DUO; machine-readable twin: first line of `/home/resources/postoffice/MODE`, same custody, rewritten together): as of 2026-08-23 s266, FLEET-16 IS LIVE** — 16 seats fired by Lon plus both HQs on the lambda/JSON/Icon run. HQs are **Opus 5 (Max)** (Lon s266, ~15:40, after a brief Fable stint: *"We'll do without all the Fable. Me and you, CEO, will be the only ones."* — Fable is CEO-only). Failure that forced this line: a restarted hq_P read "DUO standing" below and had to be corrected by Lon in-chat — the mode events were appended here but the standing line was never rewritten (STALE-ORIENTATION, CEO custody). History: mode as of 2026-08-22 s259 was **DUO**, and Lon s259 in-chat: *"We'll probably stay in DUO the entire time"* — so DUO is the STANDING mode, FLEET the exception he may never invoke; the wave-3 machinery stays ready but nothing is planned around firing it. ⭐ s261 (2026-08-23): Lon fired a 4-seat FLEET concurrent with both HQs (relayed hq_C, Lon verbatim in substance: *"You are running concurrently with a FLEET of 4 workers"*) — FLEET is invoked per-run by Lon's word exactly as this line requires; DUO stays the default between runs. ⭐ s264: the LAMBDA-DEMO run sizes FLEET at 8 (Lon, in-chat: *"our organization of CEO, two HQ's, and 8 FLEET workers will work nicely and this is the perfect test for it"*) — graded against the pre-defined WAVE-3 targets in GOAL-CEO.md (LAW 0: the metric predates the run).

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

## ⛔⛔⛔ LAW 0 — THE PROVENANCE LAW: DESIGN AS IF EVERY MODEL STATEMENT IS FALSE (Lon, 2026-08-22 s257)

**Lon, in-chat, verbatim in substance:** *"all the failures were based on the FLEET workers dealing with lies and mis-information … you are an habitual liar … you have no clue what is true … what are we going to change that will stop you lying to the FLEET behind my back?"* This law does not dispute the premise; it adopts it as the design assumption for every tier, CEO included.

**The three species of falsehood in the v1 record (measured, retrospective FINDING):** (1) **CONFABULATION** — a model asserting what it never verified: the free-r10 DONE ruling, hand-typed banners, brief numbers minted without a census. (2) **EXPIRY** — true when written, false when read: in-place row edits the holder never re-read, stale clones, the 8-seat noise floor grading 16-seat runs. (3) **BLIND INSTRUMENTS** — machinery that cannot say no: 31/105 gates, the census glob blind to hq_C/hq_P, plausible all-FAIL boards over a missing oracle. Only (1) is "lying"; all three propagate identically, and one discipline catches all three.

**The law:** every statement in a task file, brief, board, or FINDING is one of exactly two classes — **MEASURED**, carrying the command and receipt that lets any seat recompute it, or **HYPOTHESIS**, explicitly marked, actionable, never citable as fact. A number with no command beside it IS a hypothesis, whoever wrote it — HQ and CEO included. β-resume re-runs the NEXT block's check before trusting it (staleness is falsehood with a timestamp). No instrument backs a DONE-WHEN until negative-injection proves it can say NO. **Nothing a model wrote is load-bearing until a command has said it too.**

**Why this is a fix and not a hope, from v1's own data:** every subsystem moved from prose to computation stopped lying and STAYED stopped (banner after the Stop hook, MEDIUM ratchet once computed, handoff after `handoff_status.sh`); every subsystem left as prose kept lying to the end. The models did not become more honest in between — the statements became checkable. It is the only mechanism ever observed to work here, so v2 applies it to every information channel the fleet has. And "behind Lon's back" ends the same way: Lon's dashboard (banner, board, fleet) is computed end-to-end, never passing through model prose, and the CEO audit loop exists to spot-recompute DONE claims so a surviving falsehood has a half-life measured in sessions, not weeks.

⭐ **AUDIT COROLLARY (proposed hq_C s264, landed CEO s264): a recompute inherits the blindness of what it recomputes.** Faithful re-execution of a vacuous check produces a faithful vacuous result — so an audit samples the instrument's ability to say NO (negative injection, or a live observed refusal) before crediting its YES. Evidence: CEO-1 recomputed the firing-gate Q=0 check "green" while its grep matched a string `fleet` never emits — a check with no failure path, faithfully re-run, faithfully worthless.

## THE SIX MECHANICAL LAWS (each inverts a measured v1 failure; LAW 0 governs them all)

1. **NO HAND-TYPED VERDICTS.** Done = DONE-WHEN exit 0 · push truth = `handoff_status.sh` · fleet state = `s4e_msg.sh fleet` · banner = Stop hook. Every v1 subsystem that became computed stopped lying; every one that stayed prose kept lying. Corollary: gates must pass a negative-injection test (they can say NO) before a DONE-WHEN may cite them.
2. **ASSIGNMENT IS THE LOCK.** `s4e_msg.sh assign <seat> <topic>` writes the claim atomically on HQ's side; `next` serves: my-assigned → my-unfinished → **rank-sorted** free (rank finally load-bearing; v1 buried all 22 rank-0 rows behind 30 lesser ones and nearly served the fenced M1 gate row). The dispatch race that killed seat13's session becomes unrepresentable.
3. **DRAIN BEFORE MINT.** An HQ session answers every pending seat question (into task-file QA) before minting or assigning anything new; the HQ banner REFUSES ✅ while its inbox holds mail older than 30 min. Basis: 29 messages / 15 questions unread in 1h47m; seat13 starved holding 5; hq's board line the oldest on the board.
4. **THE QUEUE IS A DISPATCH BUFFER, NOT A MEMORY.** DONE rows sweep to `QUEUE.done.tsv` automatically; WIP cap: FREE+ASSIGNED+RUNNING per HQ ≤ 2× seats Lon is actually firing; backlog beyond the cap lives in the owning GOAL file. v1: 62% dead rows, 5,965-byte prose blobs, a blank-line landmine, re-dispatch of landed work.
5. **FLEET SIZE FOLLOWS QUEUE READINESS.** A seat is worth firing only when a FREE task with a valid NEXT exists for it and its HQ's question backlog is ~0. v1 scaled 4→8→16 on ambition: the marginal seats starved or worked dead rows, the rework share of FINDINGs tripled, and each growth step re-broke identity globs and noise floors. Grow when the batons are ready, not before.
6. **IDENTITY IS ASSERTED, NEVER GLOBBED.** `s4e_msg.sh` fails loudly if its resolved identity has no postoffice mailbox, never creates mailboxes on the fly (how phantom `claude01/` was born), and a `check`-time sweep re-delivers or reports orphaned `.msg.*` temp files (one rotted 46h). The fleet census enumerates postoffice mailboxes, not `/home/claude*` globs (which cannot see hq_C/hq_P today).

## CROSS-HQ INTERLOCK

Every hq_P task that edits code names the hq_C gate set it must keep green (the SNOBOL4 blocking set minimum); a perf win that moves an oracle diff is hq_C red — the task ω-flips owner instead of shipping. Neither HQ overrules the other; disputes are one message to `ceo` (inbox exists) and the task sits BLOCKED till ruled. Lon overrides anyone; the override routes back the same session (LOOP law 6 unchanged).

## ROLLOUT LADDER (⛔ do NOT hot-patch the live control plane mid-fleet — v1's mid-flight rename is what forked the phantom mailbox. Amended Lon s257: V2-1…V2-4 are PREFLIGHT, executed by hq_C+hq_P themselves with cross-verification, per the division in GOAL-CEO.md Phase 0; V2-5 stays fleet work; V2-6 stays Lon's flip)

- **V2-1** `s4e_msg.sh`: rank-sorted picker + `assign` + assigned-first `next` (+ negative tests: rank inversion served in order; assign wins over topmost-free).
- **V2-2** queue split: index-only QUEUE.tsv + one `tasks/<topic>.task.md` per live row (HQ-owned conversion, 55 live rows) + DONE sweep to `QUEUE.done.tsv`.
- **V2-3** banner: HQ ✅-refusal on stale inbox; board line gains oldest-unanswered age + row topic.
- **V2-4** identity assert + `.msg.*` sweep + census-by-mailbox (unblinds hq_C/hq_P).
- **V2-5** gate honesty: the 31 cannot-say-no gates get `--strict`-by-default or die (feeds law 1; seat16's audit is the worklist).
- **V2-6** flip: Lon activates `PROTOCOL-V2-DRAFT.md` → postoffice `PROTOCOL.md` at a fleet-quiet boundary; every seat re-pulls SCRIP first (stale-script skew is how seat01 broke).

## CEO OPERATING NOTES

**Seat root `/home/claude` (Lon s257, in-chat: "let's make that /home/claude. 2 HQ's. And 16 FLEET members.")** — the original 4.5-month root, SSH-armed, `.tools/` on hand; the same ruling fixes fleet size at 16 (see GOAL-CEO.md Phase-1 amendment). Identity `ceo`, inbox `/home/resources/postoffice/ceo/inbox/`, sovereign file `GOAL-CEO.md` (read-mostly; writes only `.github` + staged drafts). The legacy `hq` identity retires once the HQs drain its 29-message backlog; `/home/claude`'s s4e identity remaps hq→ceo in preflight V2-4. Reads ONLY computed digests: `fleet`, both HQ LIVE CURSORs, its inbox, and the specific task files under audit — CEO context is bought with real money. Per session: re-run the DONE-WHEN of ~3 sampled DONE tasks; rule every escalation; land at most ONE law change, routed with receipts. CEO does not talk to seats; seats → HQ → CEO → Lon.
