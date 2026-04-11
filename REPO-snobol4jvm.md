# REPO-snobol4jvm.md — snobol4jvm

**What:** SNOBOL4 → JVM bytecode. Complete compiler/interpreter/runtime in Clojure.
Role: semantic oracle for `emit_jvm.c` (one4all JVM backend).
**Clone:** `git clone https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4jvm.git /home/claude/snobol4jvm`
**Path:** `/home/claude/snobol4jvm`

---

## Oracle role

`snobol4jvm` and `emit_jvm.c` both target JVM but use different models:

- **snobol4jvm** — interpreted frame walker: `match.clj` walks pattern tree as data
  at runtime using a 7-element frame vector, dispatching on :proceed/:succeed/:recede/:fail.
- **emit_jvm.c** — compiled pure Byrd boxes: each AST node compiled to Jasmin α/γ/ω labels.

Therefore: snobol4jvm = **semantic oracle** (what the 5 phases must produce).
`emit_byrd_asm.c` = **structural oracle** (how compiled Byrd boxes look).

Baseline: **1,896 tests · 4,120 assertions · 0 failures.**

---

## Pipeline stages

| Stage | File | Speedup |
|-------|------|---------|
| EDN cache | `compiler.clj` | 22× per-program |
| Transpiler | `transpiler.clj` | 3.5–6× |
| Stack VM | `vm.clj` | 2–6× |
| JVM bytecode (ASM) | `jvm_codegen.clj` | 7.6× |

`jvm_codegen.clj` uses `clojure.asm.ClassWriter` directly — no Jasmin.

---

## Design laws (immutable)

1. ALL UPPERCASE keywords.
2. Single-file engine. `match.clj` is one `loop/case`. Cannot be split.
3. Immutable-by-default, mutable-by-atom. TABLE and ARRAY use `atom`.
4. `nil` means failure; epsilon means empty string.
5. INVOKE is the single dispatch point.
6. INVOKE args are pre-evaluated. Never call `EVAL!` on args inside INVOKE.
7. `clojure.core/=` inside `operators.clj`. Bare `=` builds IR lists.
8. Two-strategy debugging: (a) run a probe; (b) read SPITBOL source. Never speculate.
