# SESSION.md — Live Handoff

> This file is fully self-contained. A new Claude reads this and nothing else to start working.
> Updated at every HANDOFF. History lives in SESSIONS_ARCHIVE.md.

---

## Active Session

| Field | Value |
|-------|-------|
| **Repo** | SNOBOL4-tiny |
| **Sprint** | `rebus-emitter` |
| **Milestone** | M-REBUS |
| **HEAD** | `01e5d30` — feat: Rebus lexer/parser — all 3 tests pass |

## Last Thing That Happened

HQ branding/rename session — no code written. SNOBOL4-tiny repo unchanged at `01e5d30`.

Decisions made:
- Org rename: `SNOBOL4-plus` → `snobol4ever` (approved, not yet executed on GitHub)
- Naming rules locked: marketing=nodash lowercase, repo=one-dash lowercase, cli=sno4 prefix
- Full name grid settled for all repos (see RENAME.md)
- `SNOBOL4-cpython` renamed `snobol4-artifact` (signals: experimental, do not depend on)
- Brand text: `SNOBOL4ever` → `snobol4ever`, `SNOBOL4now` → `snobol4now`, etc.
- RENAME.md created in .github — 8-phase execution plan, locked naming rules, name grid
- ONE OPEN QUESTION: native kernel name — `snobol4-tiny` (Ant-Man: small source/binary, universe power) vs `snobol4-all` (does everything). Lon attached to `tiny`. Decide before executing Phase 4 of RENAME.md.
- Last .github commit: `dae46cb`

## One Next Action

Write `src/rebus/rebus_emit.c` — walk the AST and emit valid SNOBOL4 source.
Start with expression walk: RE_ASSIGN, RE_ADD, RE_CALL, etc.
Model the structure on `rebus_print.c`. Full translation rules in TINY.md §Rebus.

## Pivot Log

| Date | What changed | Why |
|------|-------------|-----|
| 2026-03-13 | Branding/rename session — RENAME.md created, naming rules locked | Lon pivot before public launch |
| 2026-03-13 | `hand-rolled-parser` paused → `rebus-emitter` active | Lon declared Rebus priority |
| 2026-03-12 | Bison/Flex → `hand-rolled-parser` decision | Session 53: LALR(1) unfixable (139 RR conflicts) |
| 2026-03-12 | M-BEAUTY-FULL inserted before M-COMPILED-SELF | Lon's priority: beautifier first |
