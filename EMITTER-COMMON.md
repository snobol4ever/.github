# EMITTER-COMMON.md — Common Emitter Architecture

**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6
**Date:** 2026-04-04
**Status:** AUTHORITATIVE

---

## What It Is

The EMITTER walks a `SM_Program` (flat array of `SM_Instr`) and produces
native code for a target platform. Every backend emitter shares this
structure — only the output format differs.

---

## The Emitter Contract

Input: `SM_Program` — the same instruction stream the INTERP executes.
Output: native code for the target platform.

**The fundamental guarantee:** if INTERP passes the full corpus on a
given `SM_Program`, the EMITTER for that same `SM_Program` is correct
by construction — because they execute the same instructions.

---

## Per-Instruction Emit

Each `SM_Op` maps to an emit function in every backend:

```c
void emit_instr(SM_Instr *instr, EmitState *st) {
    switch (instr->op) {
        case SM_PUSH_VAR:    emit_push_var(instr->u.name, st);   break;
        case SM_PAT_LIT:     emit_pat_lit(instr->u.str, st);     break;
        case SM_PAT_ALT:     emit_pat_alt(st);                   break;
        case SM_EXEC_STMT:   emit_exec_stmt(&instr->u.exec, st); break;
        case SM_JUMP_S:      emit_jump_s(instr->u.target, st);   break;
        /* ... all SM_Op cases ... */
    }
}
```

One switch. One case per instruction. No tree-walking. No IR access.

---

## Two-Mode Emission (x86 only)

The x86 emitter has two modes for BB-GRAPH generation:
- `EMIT_TEXT` — writes NASM .s text → assembled by nasm
- `EMIT_BINARY` — writes raw x86 bytes into bb_pool → executed directly

Both modes are driven by the same `SM_PAT_*` instruction sequence.
The mode switch is global state in `bb_emit.c`.

See `BB-GEN-X86-BIN.md` and `BB-GEN-X86-TEXT.md`.

---

## Label Resolution

Forward jumps (`SM_JUMP`, `SM_JUMP_S`, `SM_JUMP_F`) reference label
indices. The emitter resolves these in two passes:

1. First pass: record byte offset (or JVM pc, or .NET offset) for each
   `SM_LABEL` instruction.
2. Second pass: patch all forward jump targets.

Or: single pass with a backpatch list (same technique as `bb_emit.c`).

---

## Per-Backend Emitters

| Backend | Doc | Output | Status |
|---------|-----|--------|--------|
| x86 | `EMITTER-X86.md` | .s file (TEXT) or bb_pool bytes (BINARY) | ⬜ needs SM_Program input |
| JVM | `EMITTER-JVM.md` | .j Jasmin bytecode | ⬜ in progress |
| .NET | `EMITTER-NET.md` | .il MSIL | ⬜ in progress |
| JS | `EMITTER-JS.md` | .js source | ⬜ in progress |
| WASM | `ARCHIVE-WASM-BACKEND.md` | .wat text | ⛔ parked |

---

## References

- `SCRIP-SM.md` — the SM_Instr / SM_Program definition
- `IR.md` — what SM-LOWER compiles FROM (emitters never see IR directly)
- `BB-GEN-X86-BIN.md`, `BB-GEN-X86-TEXT.md` — x86 BB generation
