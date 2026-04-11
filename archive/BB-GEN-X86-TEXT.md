# BB-GEN-X86-TEXT.md — Textual x86 (.s) BB Generator

**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6
**Date:** 2026-04-04
**Status:** AUTHORITATIVE — ✅ existing path proven (106/106 vs SPITBOL oracle)

Generates NASM `.s` text files for each Byrd Box.
Output: `.s` file → NASM → `.o` → linked into executable.

---

## The Three-Column NASM Layout — The Law

Every generated NASM line follows the three-column SNOBOL4 form:

```
    LABEL:              ACTION                          GOTO
```

- Column 1 (label): col 0, width 20. Real NASM labels.
- Column 2 (action): col 20, width 40. Macro name + params. One macro per semantic op.
- Column 3 (goto): col 60+. Semicolon comment OR live `jmp`. Port terminator.

Comments are `;---...---` separator lines between logical sections.
This matches the C reference implementations (test_sno_*.c) exactly.

---

## One NASM Proc Per Box

Each named pattern or primitive box maps to exactly ONE NASM proc.
Sub-box ports become local labels within the enclosing proc.

```nasm
proc BIRD
    .alpha:     LIT_CHECK "Bird", 4, .gamma, .omega
    .beta:      LIT_UNDO  4,         .omega
    .gamma:     ret                                 ; γ — eax=1
    .omega:     xor     eax, eax                   ; ω — eax=0
                ret
endp
```

- C function  → NASM proc
- C label     → NASM local label (.name)
- goto        → jmp
- return      → ret (or jmp caller's γ/ω label)
- α/β entry   → test entry param, jmp .alpha / .beta

### Multi-Line Port Bodies

A port may require more than one macro line. Each line keeps its column position.
The last line of a port body carries the `jmp` in column 3:

```nasm
;   LABEL:              ACTION                          GOTO
;   ──────────────────────────────────────────────────────────
    BIRD_α:             MACRO0_port(param1, p2, p3)     ;
                        MACRO1(p5, p7)                  ; jmp BIRD_γ
                                                        ; jmp BIRD_ω

    BIRD_β:             MACRO2(p1)                      ; jmp BIRD_ω
```

---

## Globbing — Multiple Sub-Boxes Per Proc

Named patterns glob their sub-box labels into one proc.

```nasm
proc SEQ_BIRD_BLUE
    ; ── BIRD sub-box ──────────────────────────────────────────────
    .bird_α:    LIT_CHECK "Bird", 4                 ; jmp .bird_γ
                                                    ; jmp .bird_ω
    .bird_β:    LIT_UNDO  4                         ; jmp .bird_ω
    .bird_γ:                                        ; jmp .blue_α
    .bird_ω:                                        ; jmp .seq_ω
    ; ── BLUE sub-box ──────────────────────────────────────────────
    .blue_α:    LIT_CHECK "Blue", 4                 ; jmp .blue_γ
                                                    ; jmp .blue_ω
    .blue_β:    LIT_UNDO  4                         ; jmp .blue_ω
    .blue_γ:                                        ; jmp .seq_γ
    .blue_ω:                                        ; jmp .bird_β
    ; ── SEQ wiring ────────────────────────────────────────────────
    .seq_α:                                         ; jmp .bird_α
    .seq_β:                                         ; jmp .blue_β
    .seq_γ:     ret                                 ; γ
    .seq_ω:     xor     eax, eax                   ; ω
                ret
endp
```

---

## The snobol4_asm.mac Macros — Correct Role

The 151 NASM macros in `snobol4_asm.mac` define the TEXT mode expansion for
each Byrd box operation (`LIT_α`, `ALT_α`, `ARBNO_β`, etc.).

These macros are the correct abstraction for the NASM `.s` path (`emit_x64.c`
static backend). They are NOT the right abstraction for the dynamic binary path
or for the C-text path — for those, see `BB-GEN-X86-BIN.md` and `BB-GEN-LANG.md`.

The NASM macro names document what the x86 sequences DO — they remain the
reference for the binary encoding of each box type.

---

## Dual-Mode Unity

`bb_emit.c` in EMIT_TEXT mode produces this NASM. In EMIT_BINARY mode it
produces the same logic as raw x86-64 bytes (see `BB-GEN-X86-BIN.md`).
Same call sites. Same function arguments. The mode switch is global state.

The TEXT path and BINARY path produce identical execution behavior —
any difference is a bug in the BINARY branch.

---

## Existing Status

- `snobol4_asm.mac` — 151 macros ✅
- `src/runtime/boxes/*/bb_*.s` — hand-written box implementations ✅
- `bb_emit.c` EMIT_TEXT mode ✅
- Proven: 106/106 vs SPITBOL oracle ✅

---

## References

- `BB-GEN-X86-BIN.md` — binary mode counterpart
- `BB-GRAPH.md` — the graph structure these .s procs implement
- `EMITTER-X86.md` — the emitter that calls this generator
