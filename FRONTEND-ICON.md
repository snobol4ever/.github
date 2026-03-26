# FRONTEND-ICON.md — Icon Language Frontend (snobol4x)

Icon parser, AST, and IR mapping. No session state here.
**Session state** → `SESSION-icon-x64.md` (x64) or `SESSION-icon-jvm.md` (JVM)

---
**Deep reference:** all ARCH docs cataloged in `ARCH-index.md`
---

## Why Icon fits the Byrd Box model

Icon's goal-directed evaluation: every expression either succeeds (generating
zero or more values) or fails. Expressions suspend and resume like generators.
This maps exactly to α/β/γ/ω. JCON (Townsend + Proebsting, 1999) proved this:
Icon → JVM via Byrd Box IR. Proebsting 1996 §4.1–4.5 gives the four-port
templates for every Icon operator. Those templates are our emitter spec.

---

## Design Decisions

**Explicit semicolons — no auto-insertion.**
Icon's standard lexer inserts semicolons on newlines. We reject this. Every
expression sequence requires explicit `;`. Simpler lexer, no ambiguity.
Corpus patched to use explicit semicolons. `icon_semicolon` tool for end-users
only — never in the pipeline.

**Backend: shared IR, new nodes only where needed.**

| Icon concept | IR node | Notes |
|---|---|---|
| Integer/Real/String literal | `E_ILIT`/`E_FLIT`/`E_QLIT` | exact reuse |
| Cset literal | `E_QLIT` + DT_CS tag | cset = typed string |
| Variable | `E_VART` | exact reuse |
| `+` `-` `*` `/` `%` `^` | `E_ADD/SUB/MPY/DIV/EXPOP` | exact reuse |
| `\|\|` string concat | `E_CONC` | exact reuse |
| Function call | `E_FNC` | exact reuse |
| `upto(cs)` | `BREAK` Byrd box | semantic match |
| `many(cs)` | `SPAN` Byrd box | semantic match |
| `\|` value alternation | `E_ICN_ALT` | NOT `E_OR` |
| `to` generator | `E_TO` | paper §4.4 |
| `every`/`do` | `E_EVERY` | drives generator to exhaustion |
| `if`/`then`/`else` | `E_ICN_IF` | paper §4.5 indirect goto |
| `suspend` | `E_SUSPEND` | β port of enclosing call |
| `?` string scan | `E_SCAN` | explicit cursor threading |

**`bounded` flag:** deferred optimization. All four ports emitted unconditionally for now.

---

## Milestone Table

| ID | Feature | Status |
|----|---------|--------|
| M-ICON-ORACLE | `icont`+`iconx` built; oracle confirmed | ✅ |
| M-ICON-LEX | `icon_lex.c` 108/108 | ✅ |
| M-ICON-PARSE-LIT | Parser AST for all Proebsting §2 examples | ✅ |
| M-ICON-EMIT-LIT | Byrd box for `ICN_INT` matches paper §4.1 | ✅ |
| M-ICON-EMIT-TO | `to` generator | ✅ |
| M-ICON-EMIT-ARITH | `+` `*` `-` `/` binary ops | ✅ |
| M-ICON-EMIT-REL | `<` `>` `=` `~=` relational | ✅ |
| M-ICON-EMIT-IF | `if`/`then`/`else` | ✅ |
| M-ICON-EMIT-EVERY | `every E do E` | ✅ |
| M-ICON-CORPUS-R1 | 6/6 rung01 | ✅ |
| M-ICON-PROC | `procedure`/`end`, `local`, `return`, `fail` | ✅ |
| M-ICON-SUSPEND | `suspend E` user-defined generator | ✅ |
| M-ICON-CORPUS-R2 | rung02 arithmetic generators | ✅ |
| M-ICON-CORPUS-R3 | rung03 user procedures + generators | ✅ `bab5664` |
| **M-ICON-STRING** | `ICN_STR`, `\|\|` concat via `CAT2_*` | ❌ NEXT |
| M-ICON-SCAN | `E ? E` string scanning | ❌ |
| M-ICON-CSET | Cset literals; `upto`/`many`/membership | ❌ |
| M-ICON-CORPUS-R4 | rung04 string ops + scanning | ❌ |

---

## Key Files

| File | Role |
|------|------|
| `src/frontend/icon/icon_lex.c` | Lexer |
| `src/frontend/icon/icon_parse.c` | Parser |
| `src/frontend/icon/icon_ast.c` | AST node types |
| `src/frontend/icon/icon_emit.c` | x64 ASM emitter |
| `src/frontend/icon/icon_emit_jvm.c` | JVM emitter |
| `src/frontend/icon/icon_semicolon.c` | End-user tool only |
| `test/frontend/icon/corpus/` | Test corpus |

---

## Reference

- Proebsting 1996: "Simple Translation of Goal-Directed Evaluation" — §4.1–4.5 templates
- JCON source: `jcon-master/tran/ir.icn`, `irgen.icn`
- Deep JCON analysis: `ARCH-icon-jcon.md`
