# LEXER-REBUS.md — Rebus Lexer

**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6
**Date:** 2026-04-04
**Status:** AUTHORITATIVE — ✅ M-REBUS complete (bf86b4b)

Rebus is a structured language that transpiles to SNOBOL4.
Flex-generated lexer. File: `src/rebus/rebus.l`

## Output

Token stream → `PARSER-REBUS` → Rebus AST → SNOBOL4 source

## References

- `PARSER-REBUS.md` — consumes this token stream
