# BB-GEN-X86-TEXT.md — Textual x86 (.s) BB Generator

**Status:** STUB — to be filled from EMITTER-X86-DEEP.md

Generates NASM .s text files for each Byrd Box.
Output: .s file → nasm → .o → linked into executable.

Each box becomes a labeled NASM procedure with α/β entry points and γ/ω jump targets.
See snobol4_asm.mac for the macro layer.
See src/runtime/boxes/*/bb_*.s for existing hand-written box implementations.
