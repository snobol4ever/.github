# LEXER-SNOBOL4.md — SNOBOL4 Lexer

**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6
**Date:** 2026-04-04
**Status:** AUTHORITATIVE

---

## Role

Tokenizes SNOBOL4 source text into a token stream consumed by PARSER-SNOBOL4.
Produces IR (Program*) together with the parser.

## Implementation

**File:** `src/frontend/snobol4/lex.c` — hand-rolled, one-pass lexer.

**Key structure:** `sno_charclass[256]` — a flat lookup table mapping each byte
value to its character class. This is the entire lexer dispatch mechanism —
no regex, no generated code, no flex.

**Token queue:** The lexer produces a flat token queue consumed by the parser.
The body-reconstruction bridge (`bbuf`/`body_toks` → re-lex) was needed to handle
ambiguous juxtaposition — eliminated when `lex.c` → `lex.l` migration completes
(M-LEX-1).

## Migration Plan — M-LEX-1

Replace `lex.c` with a flex-generated `lex.l` (~200 lines). The `sno_charclass[256]`
table becomes flex character classes. IDENT immediately followed by LPAREN (no T_WS)
becomes unambiguous in the flex rules, fixing corpus test 1013/003. The IR output
is identical — same EKind nodes, same STMT_t structure.

**Resume order:**
1. `lex.l` (~200 lines) — `sno_charclass[256]` table → flex rules
2. `parse.y` (~500 lines) — `parse_expr()` and `parse_pat_expr()` → bison grammar
3. Update Makefile — remove bison/flex workarounds
4. Smoke tests: 0/21 → 21/21

**Reference stash:** `WIP Session 53: partial Bison fixes` — reference only. DO NOT APPLY.

## Source Layout

```
src/frontend/snobol4/lex.c      One-pass lexer: source → token queue
src/frontend/snobol4/parse.c    Parser: token queue → EXPR_t/STMT_t/Program
```

## Output

Token stream → `PARSER-SNOBOL4` → `IR.md` (Program*)

## References

- `PARSER-SNOBOL4.md` — consumes this token stream
- `IR.md` — the shared IR both produce
Token stream: type, value, line/col.

## Files
TBD — see src/frontend/snobol4/

## References
- `PARSER-SNOBOL4.md` — consumes this token stream
- `IR.md` — the IR the parser produces
