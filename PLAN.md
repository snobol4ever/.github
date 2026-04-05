# PLAN.md — snobol4ever / SCRIP HQ Plan

## ⚠️ ARCHITECTURE RESET — 2026-04-04
## The interpreter must execute SM_Program (stack machine instructions), NOT tree-walk IR.
## Read SCRIP-SM.md FIRST every session. See Component Map below.

**Product:** SCRIP — Snobol4, SnoCone, Rebus, Icon, Prolog. Ten times faster.
**Team:** Lon Jones Cherryholmes (arch), Jeffrey Cooper M.D. (DOTNET), Claude Sonnet 4.6 (co-author).

---

## ⛔ SESSION START — every session, no exceptions

**Step 1 — Read in order (always):**
```
cat /home/claude/.github/SCRIP-SM.md          # THE stack machine — read this FIRST, every session
cat /home/claude/.github/BB-GRAPH.md          # Byrd Box graph
cat /home/claude/.github/BB-DRIVER.md         # BB executor
cat /home/claude/.github/IR.md                # shared IR
tail -120 /home/claude/.github/SESSIONS_ARCHIVE.md
grep "^## " /home/claude/.github/GENERAL-RULES.md
cat /home/claude/.github/PLAN.md
```

**Step 2 — Read your component docs (session-specific):**
```
INTERP-<backend>.md     (interpreter session)
EMITTER-<backend>.md    (emitter session)
LEXER-<frontend>.md + PARSER-<frontend>.md  (frontend session)
```

**Step 3 — Read SESSION-<frontend>-<backend>.md (§INFO first, then §NOW)**
```
cat /home/claude/.github/SESSION-<frontend>-<backend>.md
```
The SESSION doc has two mandatory sections:
- `## ⛔ §INFO` — session invariants (tool locations, oracle setup, baselines,
  don't-do-X warnings). Append-only. Read before touching anything.
- `## §NOW` — current sprint, HEAD hashes, next milestone, first actions.

---

## The Architecture in One Paragraph

Every frontend (SNOBOL4, Icon, Prolog, Snocone, Rebus, Scrip) produces the shared IR
(Program* of STMT_t/EXPR_t). SM-LOWER compiles IR to SM_Program — a flat array of stack
machine instructions. The INTERP executes SM_Program by dispatching instructions. When it
hits SM_EXEC_STMT, it calls BB-DRIVER which runs the BB-GRAPH built by preceding SM_PAT_*
instructions. The EMITTER walks the same SM_Program and emits native code (x86, JVM, .NET,
JS, WASM). Interpreter and emitter share one instruction set. When the interpreter passes
the corpus, the emitter is correct by construction.

---

## The 6 Frontends × 6 Backends

| | x86 | JVM | .NET | JS | WASM | C |
|--|:---:|:---:|:----:|:--:|:----:|:-:|
| SNOBOL4 | DYN | J | D | SJ | ⛔ | — |
| Icon | IX | IJ | — | IJJ | ⛔ | — |
| Prolog | PX | PJ | — | PJJ | ⛔ | — |
| Snocone | SC | — | — | — | — | — |
| Rebus | — | — | — | — | — | — |
| **SCRIP** | — | SD | — | — | — | — |

---

## Component Map — one doc per component

| Component | Doc | Status |
|-----------|-----|--------|
| **SCRIP Stack Machine** | `SCRIP-SM.md` | ✅ designed · ⬜ SM-LOWER not written |
| **IR** | `IR.md` | ✅ complete |
| **BB-GRAPH** | `BB-GRAPH.md` | ✅ 25 boxes complete |
| **BB-DRIVER** | `BB-DRIVER.md` | ✅ correct (in stmt_exec.c) |
| BB-GEN x86 binary | `BB-GEN-X86-BIN.md` | ⬜ stubs only |
| BB-GEN x86 text (.s) | `BB-GEN-X86-TEXT.md` | ✅ boxes exist as .s |
| BB-GEN languages | `BB-GEN-LANG.md` | ✅ C+Java done · others stub |
| **INTERP x86 (C)** | `INTERP-X86.md` | ⚠️ tree-walks IR — needs SM_Program |
| INTERP JVM (Java) | `INTERP-JVM.md` | ⬜ in progress |
| INTERP .NET (C#) | `INTERP-NET.md` | ⬜ in progress |
| INTERP JS | `INTERP-JS.md` | ⬜ in progress |
| INTERP WASM | `INTERP-WASM.md` | ⛔ parked |
| EMITTER x86 | `EMITTER-X86.md` | ⬜ needs SM_Program input |
| EMITTER JVM | `EMITTER-JVM.md` | ⬜ in progress |
| EMITTER .NET | `EMITTER-NET.md` | ⬜ in progress |
| EMITTER JS | `EMITTER-JS.md` | ⬜ in progress |
| LINKER | `LINKER.md` | ⬜ in progress |
| LEXER / PARSER (6× each) | `LEXER-*.md` / `PARSER-*.md` | ⬜ stubs needed |
| **SN4PARSE oracle** | `MILESTONE-SN4PARSE.md` | ⚠️ in progress — DYN-85 |
| **SN4PARSE validation** | `MILESTONE-SN4PARSE-VALIDATE.md` | ⬜ next after M-SN4PARSE |
| **RUNTIME** | `RUNTIME.md` | ✅ E=mc² model, EVAL/CODE/EXPRESSION/NAME |
| CORPUS | `CORPUS.md` | ✅ |
| HARNESS | `HARNESS.md` | ✅ |
| MONITOR | `MONITOR.md` | ✅ |
| BENCHMARK-GRID | `BENCHMARK-GRID.md` | ⬜ placeholders |

---

## ⚡ NOW

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **SNOBOL4 × x86** | 96 | one4all `07d9bf4` · corpus `8d5cc6a` | **M-SN4PARSE-VALIDATE** — chained `[]` ✅ — next: P2D EQTYP in subscript |
| **Snocone x86** | SC-14 | `05a50e8` one4all · `7729763` corpus | M-SC-SELFTEST |
| **TINY JVM** | J-233 | one4all `b8560bb` | J-234: 1011_func_redefine + 1017_arg_local → ≥165p |
| **one4all-SNOBOL4-NET** | D-181 | one4all `e1a66fb` | D-182: fix str splice write-back → ≥170p |
| **SNOBOL4 JS** | SJ-26 | one4all `d7cf03e` | 174p/4f · SJ-27: engine re-entrancy fix → ≥175p |

---

## File Taxonomy

| Prefix | Purpose |
|--------|---------|
| `SCRIP-SM.md` | Stack machine — THE central design doc |
| `BB-*.md` | Byrd Box components |
| `IR.md` | Shared intermediate representation |
| `INTERP-*.md` | Per-platform interpreters |
| `EMITTER-*.md` | Per-platform emitters |
| `LEXER-*.md` | Per-language lexers |
| `PARSER-*.md` | Per-language parsers |
| `LINKER.md` | Linker |
| `CORPUS.md` / `HARNESS.md` / `MONITOR.md` / `TESTING.md` | Test infrastructure |
| `BENCHMARK-GRID.md` | Benchmark results |
| `GENERAL-*.md` | Cross-cutting reference (decisions, rules, vision, ABI) |
| `ARCHIVE-*.md` | Completed or parked work |
| `MISC-*.md` | Background, reference, one-off docs |
| `SESSION-*.md` | Per-session operational state |
| `MILESTONE-*.md` | Milestone ladders |
| `SESSIONS_ARCHIVE.md` | Append-only session log |

---

*PLAN.md = routing + NOW + component map. No sprint content. No completed milestones.*
*Architecture reset: DYN-82 session, 2026-04-04, Lon Jones Cherryholmes + Claude Sonnet 4.6.*
