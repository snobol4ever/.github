# BACKEND-JVM.md — JVM Backend Reference

Full SNOBOL4/SPITBOL in Clojure targeting JVM bytecode.
Multi-stage pipeline: interpreter → transpiler → stack VM → JVM `.class` bytecode.

*Session state → JVM.md. Testing protocol → TESTING.md.*

---

## Design Decisions (Immutable — 10 laws)

1. ALL UPPERCASE keywords.
2. Single-file engine. `match.clj` is one `loop/case`. Cannot be split.
3. Immutable-by-default, mutable-by-atom. TABLE and ARRAY use `atom`.
4. Label/body whitespace contract. Labels flush-left, bodies indented.
5. INVOKE is the single dispatch point. Add both lowercase and uppercase entries.
6. `nil` means failure; epsilon means empty string.
7. `clojure.core/=` inside `operators.clj`. Bare `=` builds IR lists.
8. INVOKE args are pre-evaluated. Never call `EVAL!` on args inside INVOKE.
9. Two-tier generator discipline. `rand-*` probabilistic. `gen-*` exhaustive lazy.
10. Two-strategy debugging: (a) run a probe; (b) read CSNOBOL4/SPITBOL source. Never speculate.

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

---

## Open Issues

| # | Issue | Status |
|---|-------|--------|
| 1 | CAPTURE-COND (`.`) assigns immediately — deferred-assign not built | Open |
| 2 | ANY(multi-arg) inside EVAL string — ClassCastException | Open |

---

## Performance Baseline

| Stage | Speedup vs interpreter |
|-------|----------------------|
| EDN cache (`jvm-edn-cache`) | 22× per-program |
| Transpiler (`jvm-transpiler`) | 3.5–6× |
| Stack VM (`jvm-stack-vm`) | 2–6× |
| JVM bytecode (`jvm-bytecode`) | 7.6× |

Test baseline: 1,896 tests / 4,120 assertions / 0 failures.
