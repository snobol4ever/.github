# PARSER-ICON.md — Icon Parser

**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6
**Date:** 2026-04-04
**Status:** AUTHORITATIVE — ✅ M-ICON-PARSE-LIT complete

Consumes token stream from LEXER-ICON and produces shared IR (Program*).
File: `src/frontend/icon/icon_parse.c`

**Main program:** `scrip-cc`. The `icon_driver` (`icon_driver_main`) is called by
`scrip-cc -icn`. Use a shim for standalone testing.

---

## Why Icon Fits the Byrd Box Model

Goal-directed evaluation: every expression succeeds (generating values) or fails.
Maps exactly to α/β/γ/ω. JCON (Townsend + Proebsting 1999) proved Icon → JVM via
Byrd Box IR. Proebsting 1996 §4.1–4.5 gives four-port templates for every Icon operator.

---

## IR Node Mapping

| Icon concept | IR node | Notes |
|---|---|---|
| Int/Real/String literal | `E_ILIT`/`E_FLIT`/`E_QLIT` | exact reuse |
| Variable | `E_VART` | exact reuse |
| `+` `-` `*` `/` `^` | `E_ADD/SUB/MPY/DIV/EXPOP` | exact reuse |
| `\|\|` concat | `E_CONC` | exact reuse |
| `upto(cs)` | `BREAK` Byrd box | semantic match |
| `many(cs)` | `SPAN` Byrd box | semantic match |
| `\|` value alternation | `E_ICN_ALT` | NOT `E_OR` |
| `to` generator | `E_TO` | paper §4.4 |
| `every`/`do` | `E_EVERY` | drives generator |
| `if`/`then`/`else` | `E_ICN_IF` | paper §4.5 |
| `suspend` | `E_SUSPEND` | β port of enclosing call |
| `?` string scan | `E_SCAN` | explicit cursor threading |

---

## x64 Milestone Table

| ID | Feature | Status |
|----|---------|--------|
| M-ICON-LEX | icon_lex.c 108/108 | ✅ |
| M-ICON-PARSE-LIT | Parser AST Proebsting §2 | ✅ |
| M-ICON-EMIT-LIT through M-ICON-EMIT-EVERY | All paper templates | ✅ |
| M-ICON-CORPUS-R1 through R3 | rungs 01–03 | ✅ |
| M-ICON-PROC | procedure/return/fail | ✅ |
| M-ICON-SUSPEND | user-defined generators | ✅ |
| **M-IX-STRING** | Fix `\|\|` concat segfault; rung04 100% | ❌ NEXT |
| M-IX-SCAN | `E ? E` string scanning (rung05) | ❌ |
| M-IX-CSET | Cset literals + any/many/upto (rung06) | ❌ |
| M-IX-CONTROL | if/then/else, next, break (rung07) | ❌ |
| M-IX-CORPUS-R10 | rungs 01–10 all green | ❌ |

---

## Key Files

| File | Role |
|------|------|
| `src/frontend/icon/icon_lex.c` | Lexer |
| `src/frontend/icon/icon_parse.c` | Parser |
| `src/frontend/icon/icon_ast.c` | AST node types |
| `src/frontend/icon/icon_emit.c` | x64 ASM emitter |
| `src/frontend/icon/icon_emit_jvm.c` | JVM emitter |
| `src/frontend/icon/icon_runtime.c` | x64 runtime (syscall-based, no libc) |
| `test/frontend/icon/corpus/` | Test corpus (rung01–rung36) |

## References

- `LEXER-ICON.md` — token stream input
- `IR.md` — shared IR produced
- `INTERP-JVM.md` — JCON correspondence for Icon generators
