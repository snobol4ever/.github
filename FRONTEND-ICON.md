# FRONTEND-ICON.md — Icon Language Frontend (snobol4x)

Icon parser, AST, IR mapping. No session state here.
**Session state** → `SESSION-icon-x64.md` (x64) or `SESSION-icon-jvm.md` (JVM)
**Deep reference:** all ARCH docs cataloged in `ARCH-index.md`

**Main program is `sno2c`.** The `icon_driver` is an internal entry point
(`icon_driver_main`) called by `sno2c -icn`. Use a shim for standalone testing.

---

## Why Icon fits the Byrd Box model

Goal-directed evaluation: every expression succeeds (generating values) or fails.
Maps exactly to α/β/γ/ω. JCON (Townsend + Proebsting 1999) proved Icon → JVM via Byrd Box IR.
Proebsting 1996 §4.1–4.5 gives four-port templates for every Icon operator.

---

## Design Decisions

**Explicit semicolons — no auto-insertion.** Simpler lexer, no ambiguity.
`icon_semicolon` tool for end-users only — never in the pipeline.

**IR node reuse:**

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
| M-ICON-ORACLE | icont+iconx oracle confirmed | ✅ |
| M-ICON-LEX | icon_lex.c 108/108 | ✅ |
| M-ICON-PARSE-LIT | Parser AST Proebsting §2 | ✅ |
| M-ICON-EMIT-LIT through M-ICON-EMIT-EVERY | All paper templates | ✅ |
| M-ICON-CORPUS-R1 | 6/6 rung01 | ✅ |
| M-ICON-PROC | procedure/return/fail | ✅ |
| M-ICON-SUSPEND | user-defined generators | ✅ |
| M-ICON-CORPUS-R2 | rung02 | ✅ |
| M-ICON-CORPUS-R3 | rung03 `bab5664` | ✅ |
| **M-IX-STRING** | Fix `\|\|` concat segfault; rung04 100% | ❌ NEXT |
| M-IX-SCAN | `E ? E` string scanning (rung05) | ❌ |
| M-IX-CSET | Cset literals + any/many/upto (rung06) | ❌ |
| M-IX-CONTROL | if/then/else, next, break (rung07) | ❌ |
| M-IX-STRBUILTINS | size/trim/repl/left/right (rung08) | ❌ |
| M-IX-LOOPS | while/until/repeat (rung09) | ❌ |
| M-IX-AUGOP | `+:=` etc augmented assignment (rung10) | ❌ |
| M-IX-REAL | Real arithmetic + swap (rung15) | ❌ |
| M-IX-CORPUS-R10 | rungs 01–10 all green | ❌ |
| M-IX-BENCHMARK | rung36_jcon subset on x64 | ❌ |

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
