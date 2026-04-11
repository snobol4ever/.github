# ARCH-JVM.md — JVM Backend

Backend: JVM (Jasmin assembly → .class bytecode).
Emitter: `src/backend/emit_jvm.c` (one4all) + `snobol4jvm` (Clojure, semantic oracle).

## Byrd Box model (compiled)

`emit_jvm.c` compiles each AST node to Jasmin α/γ/ω labels at compile time.
The `.class` IS the Byrd box graph. No interpreter loop at runtime.
Same model as `emit_x64.c` — labels + gotos, never execution at emit time.

## snobol4jvm (oracle)

Interpreted frame walker. `match.clj` walks pattern tree as data using 7-element
frame vector, dispatching on :proceed/:succeed/:recede/:fail.
Role: semantic oracle for emit_jvm.c. Baseline: 1,896 tests, 0 failures.

## Tools

- `javac`, `java` (JDK + JRE)
- `jasmin.jar` — bundled in repo
- `jvm_codegen.clj` uses `clojure.asm.ClassWriter` — no Jasmin (snobol4jvm path)

*Populate further from archive/EMITTER-JVM.md when a JVM goal is active.*
