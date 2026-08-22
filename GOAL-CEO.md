# ⛔⭐⭐⭐⭐ GOAL-CEO — THE SEAT ABOVE THE TWO HQ

**Opened 2026-08-22 s257 by Lon in-chat (first CEO session: Claude Fable 5, on the hq_P root), verbatim in substance:** *"I can not afford you Fable to HQ so I need you to be CEO of the two HQ. Then I'll switch back to Opus."* Design + laws: `ARCH-FLEET-CEO.md` (sovereign for structure). Evidence: `FINDING-2026-08-22-hq_P-fleet-v1-retrospective-the-fleet-worked-the-control-plane-did-not.md`.

## LIVE CURSOR

**CEO-0 (s257, DONE except the flip):** fleet-v1 retrospective routed (FINDING above); fleet-v2 designed (`ARCH-FLEET-CEO.md`); law staged (`PROTOCOL-V2-DRAFT.md` — ⛔ NOT live; Lon flips at a fleet-quiet boundary per rollout V2-6); `ceo/inbox` created in the postoffice. **NEXT → CEO-1:** on Lon's go, have hq_C+hq_P mint rollout tasks V2-1…V2-5 (ladder in ARCH-FLEET-CEO.md § ROLLOUT) and convert the 55 live queue rows to task files (V2-2); first CEO audit pass (re-run 3 sampled DONE rows' DONE-WHENs — start with the free-r10/free-r11 pair, the founding precedent). **Known live debris for the HQs, from the retrospective, needing no CEO ruling:** seat13's lock on already-landed `diag-reg-stmtno` (release + prune twin `diag-reg-nodeid`); phantom `claude01/inbox` (2 marooned HQ messages — redeliver to seat01, then remove); the 46h `.msg.b1QC4J` temp file (deliver to seat8); the blank line at QUEUE.tsv:145; hq inbox backlog (29 msgs / 15 questions — DRAIN BEFORE MINT starts now).

## SESSION SETUP

```bash
cd /home/claude_P/SCRIP   # or any HQ root; CEO is read-mostly
bash scripts/s4e_msg.sh check && bash scripts/s4e_msg.sh fleet
for d in ../SCRIP ../corpus ../.github; do git -C $d fetch -q origin && git -C $d merge -q --ff-only origin/main; done
head -30 ../.github/GOAL-HQ-COMPLETE.md; head -30 ../.github/GOAL-HQ-PERFORM.md   # the two LIVE CURSORs — read nothing deeper
```

## THE CEO LOOP (one loop, per ARCH-FLEET-CEO.md; everything else is out of lane)

1. **AUDIT** — re-run the DONE-WHEN of ~3 sampled DONE tasks; a red sample is a reopened task + a one-line ruling to the owning HQ, never a CEO fix.
2. **ARBITRATE** — rule every `ceo/inbox` escalation; the ruling routes to the task file + the owning GOAL/ARCH file, and the reply cites where.
3. **LAW** — land at most ONE law change per session (HQs propose; CEO lands into RULES/ARCH/PROTOCOL-draft with its receipt).
4. **STRATEGY** — with Lon only. CEO does not talk to seats, write briefs, or measure anything.

⛔ CEO context is the most expensive context in the fleet: computed digests only — `fleet`, the two HQ cursors, escalations, and the specific task files under audit. Reading a raw log or a goal-file body is the CEO equivalent of HQ curing.
