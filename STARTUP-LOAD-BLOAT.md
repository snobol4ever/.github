# STARTUP LOAD BLOAT — the HQ itself has gotten too heavy

## The problem

A new session opens at ~15-20% of context used just from the system prompt and
tool descriptions. Then the session-start protocol (PLAN.md → RULES.md →
relevant GOAL-*.md → ARCH-*.md → REPO-*.md) adds another 10-15%. Reading even
ONE long goal file (GOAL-ICON-BB.md is ~800 lines, GOAL-HEADQUARTERS.md is
~300 lines with deep nested watermarks) can push another 5-10%.

By the time a session is "oriented" and ready to do its first real edit,
context is at ~35-50% used. The goal-file headers explicitly say "Fresh
context required (~80%+)" for hard rungs like ICN-Z-ATOMIC. That math doesn't
work — there is no path to 80%+ remaining at "first real edit" with the
current startup load.

This was experienced first-hand 2026-05-27 (Opus session). The session
opened oriented at ~35%, did real work down to ~95%, and ran out of budget
before completing the rung. The rung itself (ICN-Z-ATOMIC) was achievable;
the budget was eaten by orientation.

## Symptoms

- Watermarks accumulate in goal files (HEADQUARTERS has multiple "Previous
  Session State" blocks stacked).
- PLAN.md row notes accumulate across sessions and never shrink.
- Goal files have "NEXT SESSION — START HERE" blocks at the top followed by
  500+ lines of historical context.
- A session reading the goal file for orientation ends up reading the entire
  evolution of the rung, not just its current state.

## What I think needs to happen (grand master reorg)

1. **Watermark rotation**: each goal file holds at most ONE "current state"
   block. Prior sessions roll into a separate `HISTORY-<goal>.md` file (or a
   commit-log section at the bottom) that orientation does NOT read.
2. **PLAN.md row diet**: each row is at most 2 sentences. Detailed status lives
   in the goal file's current-state block, not in PLAN.md.
3. **Goal file shape contract**: every GOAL-*.md starts with
   - 5-line summary of what the rung accomplishes
   - 10-line "current state" block
   - "NEXT STEP" — the literal next action
   - everything else under a `## Detail` heading that orientation can skip.
4. **HEADQUARTERS.md diet**: should be the place orientation goes to BYPASS
   reading individual goal files. Currently it has the inverse property —
   reading it commits to a 300-line history walk.

This is a "grand master reorg" — not a normal rung. It needs its own session
with its own budget, BEFORE the next ICN-Z-ATOMIC attempt.

## Why this matters

Without fixing this, the ICN-Z-ATOMIC rewrite (now spec'd in
LOWER-REWRITE-FROM-JCON.md) will hit the same wall the 2026-05-27 Opus
session hit: orientation eats the budget, the BIG SHOT never lands.

## Discovered

2026-05-27 Opus 4.7 session, last 2% of context. Lon directed: "Prune the
GOAL file and PLAN file and ARCH file and everything else you read at start
up to get to 80% runway. Ha. Good luck." The "ha good luck" was the point:
you can't responsibly prune at 2%. The prune itself is a rung.
