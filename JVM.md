# JVM.md — SNOBOL4-jvm

**Repo:** https://github.com/SNOBOL4-plus/SNOBOL4-jvm  
**What it is:** Full SNOBOL4/SPITBOL in Clojure targeting JVM bytecode. Multi-stage compiler pipeline: interpreter → transpiler → stack VM → JVM `.class` bytecode.

---

## Current State

**Active sprint:** Sprint 23E — inline EVAL! in JVM codegen  
**Milestone target:** MJVM  
**HEAD:** `9cf0af3`  
**Test baseline:** 1,896 tests / 4,120 assertions / 0 failures  
**Test runner:** `lein test`

**Next action:** Implement inline EVAL! in `jvm_codegen.clj` — emit arithmetic/assign/cmp
directly into JVM bytecode instead of calling back into the interpreter.

---

## Session Start Checklist

```bash
cd SNOBOL4-jvm
git log --oneline --since="1 hour ago"   # fallback: -5
lein test                                 # confirm baseline 1896/4120/0
git show HEAD --stat
```

---

## Milestones

| ID | Trigger | Status |
|----|---------|--------|
| **MJVM** | Sprint 23E inline EVAL! complete — arithmetic no longer bottleneck | ❌ Active |
| **MJVM2** | Snocone self-test: compile `snocone.sc`, diff oracle (Step 9) | ❌ Future |

---

## Sprint Map

### Sprints toward MJVM (active track)

| Sprint | What | Status |
|--------|------|--------|
| Sprint 23A | EDN cache — 22× per-program | ✅ `b30f383` |
| Sprint 23B | Transpiler: SNOBOL4 IR → Clojure `loop/case` — 3.5–6× | ✅ `4ed6b7e` |
| Sprint 23C | Stack VM: flat bytecode, 7 opcodes — 2–6× | ✅ `d9e4203` |
| Sprint 23D | JVM bytecode gen: ASM `.class`, DynamicClassLoader — 7.6× | ✅ `c185893` |
| **Sprint 23E** | **Inline EVAL! — emit arith/assign/cmp directly into JVM bytecode** | **← active** |
| Sprint 23F | Compiled pattern engine — compile pattern objects to Java methods | ❌ Planned |

### Sprints toward MJVM2 (Snocone)

| Sprint | What | Status |
|--------|------|--------|
| Snocone Step 0 | Corpus reference files | ✅ `ab5f629` |
| Snocone Step 1 | Lexer | ✅ `d1dec27` |
| Snocone Step 2 | Expression parser (`&&`, `\|\|`, `~`, `$`, `.`) | ✅ `9cf0af3` |
| Snocone Step 3 | `if/else` → label/goto | ❌ |
| Snocone Steps 4–8 | `while`, `for`, `procedure`, `struct`, `#include` | ❌ |
| Snocone Step 9 | Self-test: compile `snocone.sc`, diff oracle → **MJVM2 triggers** | ❌ |

### Completed foundation sprints

| Sprint | What | Baseline |
|--------|------|---------|
| Sprint 13 | Baseline | 220 / 548 / 0 |
| Sprint 18B | Pattern engine complete | 1,488 / 3,249 / 0 |
| Sprint 19 | Variable shadowing fix | 2,017 / 4,375 / 0 |
| Sprint 25E | -INCLUDE, TERMINAL, CODE(), Named I/O, OPSYN | 2,033 / 4,417 / 0 |
| Snocone Step 2 | Current baseline | **1,896 / 4,120 / 0** |

---

## Open Issues

| # | Issue | Status |
|---|-------|--------|
| 1 | CAPTURE-COND (`.`) assigns immediately — deferred-assign not built | Open |
| 2 | ANY(multi-arg) inside EVAL string — ClassCastException | Open |
| 3 | Sprint 23E — inline EVAL! in JVM codegen | **Active** |

---

## Design Decisions (Immutable)

1. **ALL UPPERCASE keywords.**
2. **Single-file engine.** `match.clj` is one `loop/case`. Cannot be split.
3. **Immutable-by-default, mutable-by-atom.** TABLE and ARRAY use `atom`.
4. **Label/body whitespace contract.** Labels flush-left, bodies indented.
5. **INVOKE is the single dispatch point.** Add both lowercase and uppercase entries.
6. **nil means failure; epsilon means empty string.**
7. **`clojure.core/=` inside `operators.clj`.** Bare `=` builds IR lists.
8. **INVOKE args are pre-evaluated.** Never call `EVAL!` on args inside INVOKE.
9. **Two-tier generator discipline.** `rand-*` probabilistic. `gen-*` exhaustive lazy.
10. **Two-strategy debugging.** (a) run a probe; (b) read CSNOBOL4/SPITBOL source. Never speculate.

---

## File Map

| File | Responsibility |
|------|---------------|
| `match.clj` | MATCH state machine — the single-file engine |
| `primitives.clj` | LIT$, ANY$, SPAN$, BREAK$, POS#, etc. |
| `patterns.clj` | ANY, SPAN, ARBNO, FENCE, ABORT, BAL, CONJ, DEFER |
| `grammar.clj` | instaparse grammar + parse-statement/parse-expression |
| `emitter.clj` | AST → Clojure IR |
| `operators.clj` | EVAL/EVAL!/INVOKE, comparison primitives |
| `runtime.clj` | RUN: GOTO-driven statement interpreter |
| `jvm_codegen.clj` | Stage 23D: ASM-generated JVM `.class` bytecode |
| `transpiler.clj` | Stage 23B: SNOBOL4 IR → Clojure `loop/case` |
| `vm.clj` | Stage 23C: flat bytecode stack VM |
