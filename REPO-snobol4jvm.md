# REPO-snobol4jvm.md

JVM/Clojure backend: SNOBOL4 → JVM bytecode via multi-stage pipeline.
**Role (post J-217 pivot): semantic oracle for `emit_jvm.c` (one4all JVM backend).**

→ Session doc: [SESSION-snobol4-jvm.md](SESSION-snobol4-jvm.md)
→ Milestone ladder: [MILESTONE-JVM-SNOBOL4.md](MILESTONE-JVM-SNOBOL4.md)
→ Backend reference: [EMITTER-JVM.md](EMITTER-JVM.md)

---

## Oracle role (J-217 pivot)

`snobol4jvm` and `emit_jvm.c` both target the JVM but use different models:

**snobol4jvm** — interpreted frame walker: `match.clj` walks a pattern tree
as data at runtime using a 7-element frame vector, dispatching on
:proceed/:succeed/:recede/:fail. One engine handles all patterns.

**emit_jvm.c** — compiled pure Byrd boxes: `emit_jvm_pat_node()` compiles
each AST node to Jasmin α/γ/ω labels at compile time. The `.class` IS the
Byrd box graph. No interpreter loop at runtime. Same model as `emit_byrd_asm.c`.

**Therefore:**
- `snobol4jvm` = **semantic oracle** (what the 5 phases must produce)
- `emit_byrd_asm.c` = **structural oracle** (how compiled Byrd boxes look)
- Both oracles required; neither alone is sufficient.

Proven baseline: **1,896 tests · 4,120 assertions · 0 failures.**

---

## NOW

**Sprint:** J-217 pivot declared
**HEAD:** one4all `a74ccd8` (J-216 STLIMIT/STCOUNT)
**Milestone:** M-JVM-A02 — 2D subscript fix + rung8 clean → ≥100p

---

## Pipeline stages (snobol4jvm internal)

| Stage | File | Speedup |
|---|---|---|
| EDN cache | `compiler.clj` | 22× per-program |
| Transpiler | `transpiler.clj` | 3.5–6× |
| Stack VM | `vm.clj` | 2–6× |
| JVM bytecode (ASM) | `jvm_codegen.clj` | 7.6× |

`jvm_codegen.clj` uses `clojure.asm.ClassWriter` directly — no Jasmin.
Stage 23E inline-emit eliminates `EVAL_FN` dispatch for common patterns.

---

## Clone path

```
/home/claude/snobol4jvm/
```

---

## Design Decisions (Immutable — 10 laws)

1. ALL UPPERCASE keywords.
2. Single-file engine. `match.clj` is one `loop/case`. Cannot be split.
3. Immutable-by-default, mutable-by-atom. TABLE and ARRAY use `atom`.
4. Label/body whitespace contract. Labels flush-left, bodies indented.
5. INVOKE is the single dispatch point.
6. `nil` means failure; epsilon means empty string.
7. `clojure.core/=` inside `operators.clj`. Bare `=` builds IR lists.
8. INVOKE args are pre-evaluated. Never call `EVAL!` on args inside INVOKE.
9. Two-tier generator discipline. `rand-*` probabilistic. `gen-*` exhaustive.
10. Two-strategy debugging: (a) run a probe; (b) read SPITBOL source. Never speculate.
