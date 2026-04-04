# BB-GEN-LANG.md — Language BB Generators (C, JS, WASM, Java, C#)

**Status:** STUB

Generates Byrd Box implementations as source code in each target language.
Each language gets a sequence of function definitions that implement the
α/β/γ/ω protocol for each box type.

| Language | Generator | Output |
|----------|-----------|--------|
| C        | bb_gen_c.c | bb_*.c source files |
| JS       | bb_gen_js.c | bb_*.js functions |
| WASM     | bb_gen_wasm.c | bb_*.wat text |
| Java     | bb_gen_java.c | bb_*.java classes |
| C#       | bb_gen_net.c | bb_*.cs classes |

Existing: src/runtime/boxes/*/bb_*.c (C) ✅, src/runtime/boxes/bb_*.java (Java) ✅
