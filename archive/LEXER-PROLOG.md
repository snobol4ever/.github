# LEXER-PROLOG.md — Prolog Lexer

**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6
**Date:** 2026-04-04
**Status:** AUTHORITATIVE

Tokenizes Prolog source text. File: `src/frontend/prolog/pl_lex.c`

## Output

Token stream → `PARSER-PROLOG` → IR (Program*)

## References

- `PARSER-PROLOG.md` — consumes this token stream
- `IR.md` — the shared IR produced
