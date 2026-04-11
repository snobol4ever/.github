# LEXER-ICON.md — Icon Lexer

**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6
**Date:** 2026-04-04
**Status:** AUTHORITATIVE — ✅ M-ICON-LEX complete (108/108)

Tokenizes Icon source text. File: `src/frontend/icon/icon_lex.c`

**Design decision:** Explicit semicolons — no auto-insertion. Simpler lexer, no ambiguity.
`icon_semicolon` tool for end-users only — never in the pipeline.

## Output

Token stream → `PARSER-ICON` → IR (Program*)

## References

- `PARSER-ICON.md` — consumes this token stream
- `IR.md` — the shared IR produced
