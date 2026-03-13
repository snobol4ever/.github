# SESSION.md — Live Handoff

> Written at every HANDOFF. A new Claude reads this first, then the active repo's MD file.
> Current state only. History lives in SESSIONS_ARCHIVE.md.

---

## Active Repo: TINY

**Last updated:** 2026-03-13  
**Active sprint:** Rebus R3 — `src/rebus/rebus_emit.c`  
**Milestone target:** MREBUS  
**HEAD:** `bceaa24`  
**Last substantive commit:** `01e5d30` — feat: Rebus lexer/parser — all 3 tests pass

## Current State

Rebus lexer + parser + AST complete. All 3 test files parse cleanly.
Sprint 26 (hand-rolled parser → M0) is paused until MREBUS.

**Next action:** Write `src/rebus/rebus_emit.c`. Walk RExpr/RStmt/RDecl tree,
emit valid SNOBOL4 source. Start with expressions (R3). See TINY.md §Rebus.

## Next Session Checklist

```bash
cd SNOBOL4-tiny
git log --oneline --since="1 hour ago"   # fallback: -5
find src -type f | sort
git show HEAD --stat
# Read TINY.md § Current State and § Rebus
```
