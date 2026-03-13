# JVM.md — SNOBOL4-jvm

**Repo:** https://github.com/SNOBOL4-plus/SNOBOL4-jvm  
**What it is:** Full SNOBOL4/SPITBOL in Clojure targeting JVM bytecode. Multi-stage compiler pipeline: interpreter → transpiler → stack VM → JVM `.class` bytecode.

---

## Current State

**Active sprint:** `jvm-inline-eval`  
**Milestone target:** M-JVM-EVAL  
**HEAD:** `9cf0af3`  
**Test baseline:** 1,896 tests / 4,120 assertions / 0 failures

**Next action:** Implement inline EVAL! in `jvm_codegen.clj` — emit arithmetic/assign/cmp
directly into JVM bytecode instead of calling back into the interpreter.

## Pivot Log

| Date | What changed | Why |
|------|-------------|-----|
| 2026-03-12 | `jvm-inline-eval` declared active | Sprint 23D complete, 23E next |

---

## Session Start Checklist

```bash
cd SNOBOL4-jvm
git log --oneline --since="1 hour ago"   # fallback: -5
lein test                                 # confirm 1896/4120/0
git show HEAD --stat
```

---

## Milestones

| ID | Trigger | Status |
|----|---------|--------|
| **M-JVM-EVAL** | Inline EVAL! complete — arithmetic no longer calls interpreter | ❌ Active |
| **M-JVM-SNOCONE** | Snocone self-test: compile `snocone.sc`, diff oracle | ❌ Future |

---

## Sprint Map

### Active: toward M-JVM-EVAL

| Sprint | What | Status |
|--------|------|--------|
| `jvm-edn-cache` | EDN cache — 22× per-program | ✅ `b30f383` |
| `jvm-transpiler` | SNOBOL4 IR → Clojure `loop/case` — 3.5–6× | ✅ `4ed6b7e` |
| `jvm-stack-vm` | Flat bytecode stack VM, 7 opcodes — 2–6× | ✅ `d9e4203` |
| `jvm-bytecode` | ASM `.class` gen, DynamicClassLoader — 7.6× | ✅ `c185893` |
| **`jvm-inline-eval`** | **Emit arith/assign/cmp directly into JVM bytecode** | **← active** |
| `jvm-pattern-engine` | Compile pattern objects to Java methods | ❌ Planned |

### Toward M-JVM-SNOCONE (Snocone)

| Sprint | What | Status |
|--------|------|--------|
| `jvm-snocone-corpus` | Corpus reference files | ✅ `ab5f629` |
| `jvm-snocone-lexer` | Lexer | ✅ `d1dec27` |
| `jvm-snocone-expr` | Expression parser (`&&`, `\|\|`, `~`, `$`, `.`) | ✅ `9cf0af3` |
| `jvm-snocone-control` | `if/else`, `while`, `for`, `procedure`, `struct`, `#include` | ❌ |
| `jvm-snocone-selftest` | Compile `snocone.sc`, diff oracle → **M-JVM-SNOCONE** | ❌ |

### Completed foundation

| Sprint | What | Baseline |
|--------|------|---------|
| `jvm-baseline` | Interpreter baseline | 220 / 548 / 0 |
| `jvm-pattern-engine-v1` | Pattern engine complete | 1,488 / 3,249 / 0 |
| `jvm-var-shadow` | Variable shadowing fix | 2,017 / 4,375 / 0 |
| `jvm-include-io` | -INCLUDE, TERMINAL, CODE(), Named I/O, OPSYN | 2,033 / 4,417 / 0 |
| `jvm-snocone-expr` | Current baseline | **1,896 / 4,120 / 0** |

---

## Open Issues

| # | Issue | Status |
|---|-------|--------|
| 1 | CAPTURE-COND (`.`) assigns immediately — deferred-assign not built | Open |
| 2 | ANY(multi-arg) inside EVAL string — ClassCastException | Open |

---

## Design Decisions (Immutable)

1. ALL UPPERCASE keywords.
2. Single-file engine. `match.clj` is one `loop/case`. Cannot be split.
3. Immutable-by-default, mutable-by-atom. TABLE and ARRAY use `atom`.
4. Label/body whitespace contract. Labels flush-left, bodies indented.
5. INVOKE is the single dispatch point. Add both lowercase and uppercase entries.
6. nil means failure; epsilon means empty string.
7. `clojure.core/=` inside `operators.clj`. Bare `=` builds IR lists.
8. INVOKE args are pre-evaluated. Never call `EVAL!` on args inside INVOKE.
9. Two-tier generator discipline. `rand-*` probabilistic. `gen-*` exhaustive lazy.
10. Two-strategy debugging. (a) run a probe; (b) read CSNOBOL4/SPITBOL source. Never speculate.

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
