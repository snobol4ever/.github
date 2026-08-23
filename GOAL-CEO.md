# ⛔⭐⭐⭐⭐ GOAL-CEO — THE SEAT ABOVE THE TWO HQ

**Opened 2026-08-22 s257 by Lon in-chat (first CEO session: Claude Fable 5, on the hq_P root), verbatim in substance:** *"I can not afford you Fable to HQ so I need you to be CEO of the two HQ. Then I'll switch back to Opus."* Design + laws: `ARCH-FLEET-CEO.md` (sovereign for structure). Evidence: `FINDING-2026-08-22-hq_P-fleet-v1-retrospective-the-fleet-worked-the-control-plane-did-not.md`.

## LIVE CURSOR

**CEO-0 (s257, DONE except the flip):** fleet-v1 retrospective routed (FINDING above); fleet-v2 designed (`ARCH-FLEET-CEO.md`); law staged (`PROTOCOL-V2-DRAFT.md` — ⛔ NOT live; Lon flips at a fleet-quiet boundary per rollout V2-6); `ceo/inbox` created in the postoffice. **NEXT → CEO-1:** on Lon's go, have hq_C+hq_P mint rollout tasks V2-1…V2-5 (ladder in ARCH-FLEET-CEO.md § ROLLOUT) and convert the 55 live queue rows to task files (V2-2); first CEO audit pass (re-run 3 sampled DONE rows' DONE-WHENs — start with the free-r10/free-r11 pair, the founding precedent). **Known live debris for the HQs, from the retrospective, needing no CEO ruling:** seat13's lock on already-landed `diag-reg-stmtno` (release + prune twin `diag-reg-nodeid`); phantom `claude01/inbox` (2 marooned HQ messages — redeliver to seat01, then remove); the 46h `.msg.b1QC4J` temp file (deliver to seat8); the blank line at QUEUE.tsv:145; hq inbox backlog (29 msgs / 15 questions — DRAIN BEFORE MINT starts now).

## ⭐⭐⭐ WAVE-3 RUN PLAN (CEO proposal to Lon, s257 — executes only on Lon's go)

**Verdict: retry at 8 seats on a repaired control plane, with mechanical abort criteria.** Basis: scorecard FINDING (fleet 1.5–3.2x/day over watched week, retractions flat); retrospective (all wave-2 killers mechanical); law 5 (fleet size follows queue readiness — 16 was never earned).

**PHASE 0 — PRE-FLIGHT, 1–2 seats, ~half a day, ALL gated by negative tests:**
1. V2-1 picker: rank-sorted free rows + `s4e_msg.sh assign <seat> <topic>` + assigned-first `next` (kills the dispatch race and the rank-blind burying).
2. Queue purge: 112 DONE rows → `QUEUE.done.tsv`; blank line at :145 deleted; seat13/seat14 dead locks released; dup rows (`diag-reg-*`) pruned; every surviving brief pointer verified.
3. V2-3 banner: HQ ✅-refusal while inbox mail >30 min unread; board line gains oldest-unanswered age + row topic.
4. V2-4 identity assert + census-by-mailbox (unblinds hq_C/hq_P); deliver the marooned messages (claude01 ×2, `.msg.b1QC4J`); retire the phantom mailbox.
5. Convert ONLY the top ~16 dispatchable rows to `tasks/*.task.md` (8 per HQ), each DONE-WHEN demonstrated able to say NO. Not all 55 — no ocean-boiling.
**Firing gate:** `fleet` shows 0 unanswered questions; every seat root to be used passes the oracle preflight (absent-oracle false-FAIL class); both HQ cursors pushed.

**PHASE 1 — THE RUN: 8 seats (4 per HQ), one day.** Dispatch by `assign` only (no self-pick day 1). HQs run drain→verify→mint→assign strictly. CEO audits twice (sampled DONE-WHEN re-runs). Lon reads computed banners/board only, fires /clear, spot-audits at will.

**TARGETS, measured exactly as the scorecard FINDING (defined BEFORE the run, per LAW 0):** commit→row traceability >70% (was 34%) · median question-wait <30 min (was 45m–1h51m) · rework share of FINDINGs <15% (wave-2 day: 17%) · corpus watermark net-positive on stable denominator · zero re-dispatch of landed work · retractions ≤ wave-1 rate.

**ABORT/SHRINK, mechanical:** >6 unanswered questions for 30 min → HQs stop minting and drain (banner enforces) · 2 dispatch mismatches → halt, fix picker, resume · any seat 2h with no ledger delta → its task re-FREEs via β and reassigns (the baton working as designed).

**SCALE RULE:** 8 seats until two consecutive days green vs targets, then +4, never mid-day, never simultaneous with a namespace change or an HQ restructuring (wave 2's compounding error). ⏱ Note: the Claude Code 50% weekly-limit promotion currently ends Aug 31 — the cheap window for wave 3 is the next ~9 days.

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
