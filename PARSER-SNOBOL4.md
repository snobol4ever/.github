# PARSER-SNOBOL4.md — SNOBOL4 Parser

**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6
**Date:** 2026-04-04
**Status:** AUTHORITATIVE

---

## Role

Consumes token stream from LEXER-SNOBOL4 and produces the shared IR (Program*).
Together with the lexer, implements the SNOBOL4 frontend of the scrip-cc compiler.

## Implementation — Hand-Rolled Parser

**File:** `src/frontend/snobol4/parse.c` — hand-rolled recursive descent.

Bison was tried and abandoned (Session 53): 20 SR + 139 RR conflicts. Root cause:
`*snoWhite` misparsed as function call inside `FENCE(...)`. LALR(1) state merging
is structural — unfixable for SNOBOL4's grammar without heavy disambiguation.

**Key invariant:** `STAR IDENT` in `parse_pat_atom()` is always `E_DEREF(E_VAR)`.
`*foo (bar)` = concat(deref(foo), grouped(bar)) — two sequential atoms, no lookahead.

**Two separate parse entry points:**
- `parse_expr()` — value context (produces E_CAT for juxtaposition)
- `parse_pat_expr()` — pattern context (produces E_SEQ for juxtaposition)

## Parse → IR Mapping

See `IR.md` §SNOBOL4 Parse → IR Mapping for the full `parse_exprN` → EKind table.

## Four Statement Forms

| Form | subject | pattern | replacement | has_eq |
|------|---------|---------|-------------|--------|
| invoking | present | NULL | NULL | 0 |
| matching | present | present | NULL | 0 |
| assigning | present | NULL | present | 1 |
| replacing | present | present | present | 1 |

## Migration Plan — M-PARSE-1

Replace `parse.c` with a bison-generated `parse.y` (~500 lines). The recursive
descent functions become bison grammar rules. IDENT immediately followed by LPAREN
(no T_WS) becomes unambiguously E_FNC in the grammar rule, fixing 1013/003.
The body-reconstruction bridge (bbuf/body_toks → re-lex) is eliminated.
The IR output is identical — same EKind nodes, same STMT_t structure.

**Reference stash:** `WIP Session 53: partial Bison fixes` — reference only. DO NOT APPLY.

## Source Layout

```
src/frontend/snobol4/parse.c    Hand-rolled parser: token queue → IR
src/frontend/snobol4/lex.c      Lexer (produces token queue)
src/ir/ir.h                     EKind enum, EXPR_t struct
src/frontend/snobol4/scrip_cc.h STMT_t, Program, expr_new/add_child
```

## Output

IR (Program*) → `SM-LOWER` → `SM_Program` → INTERP or EMITTER

## References

- `LEXER-SNOBOL4.md` — produces the token stream this consumes
- `IR.md` — the shared IR this produces
- `SCRIP-SM.md` — SM-LOWER compiles IR to SM_Program
`Program*` — linked list of `STMT_t` nodes with `EXPR_t` trees.
This is the input to SM-LOWER (see SCRIP-SM.md).

## Files
TBD — see src/frontend/snobol4/

## References
- `LEXER-SNOBOL4.md` — input token stream
- `IR.md` — output representation
- `SCRIP-SM.md` — SM-LOWER compiles IR to SM_Program

---

## Status by Repo

| Repo | Implementation | Next milestone |
|------|---------------|----------------|
| one4all | scrip-cc (C compiler) | M-BEAUTIFY-BOOTSTRAP-ASM-MONITOR |
| snobol4jvm | Clojure + JVM codegen | M-JVM-STLIMIT-STCOUNT |
| snobol4dotnet | C# + MSIL | M-T2-FULL |

---

## The Proof Program — beauty.sno

Self-contained SNOBOL4 parser+pretty-printer written in SNOBOL4.
If a backend runs `beauty.sno` self-beautification correctly, the frontend is correct.

```bash
INC=/home/claude/corpus/programs/inc
BEAUTY=/home/claude/corpus/programs/beauty/beauty.sno
spitbol -b $BEAUTY < $BEAUTY > oracle.sno
<backend-binary> < $BEAUTY > compiled.sno
diff oracle.sno compiled.sno   # empty = correct
```
