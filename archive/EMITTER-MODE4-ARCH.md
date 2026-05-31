# EMITTER-MODE4-ARCH.md -- Mode-4 x86 Emitter Architecture

**Authors:** Lon Jones Cherryholmes, Claude Sonnet
**Date:** 2026-05-06
**Status:** AUTHORITATIVE -- settled session #67

Supersedes the ad-hoc libscrip_rt PLT-call approach started in EM-1/EM-2.
Derived from archaeology of: BB-GEN-X86-TEXT.md, BB-GRAPH.md,
EMITTER-COMMON.md, EMITTER-X86.md, EMITTER-X86-DEEP.md, BB-GEN-LANG.md,
SESSION-snobol4-x64.md, SCRIP-SM.md.

---

## The Two Separate Concerns

### 1. SM opcodes -> macros (the SM emitter)

The SM instruction set is the universal IR. All backends walk the same
SM_Program array. One switch, one case per opcode.

For text-asm output (--compile):
- Each opcode group maps to ONE named GNU-as macro in sm_macros.s
- The macro expands to actual inline x86 (not a PLT call per tiny op)
- Flat macro call per opcode -- NO three-column formatting:

    SM_PUSH_INT 42
    SM_ADD
    SM_JUMP_F  .Lpc17

- One emit_sm_* C function per opcode group in sm_codegen_x64_emit.c
- libscrip_rt.so is the boundary for: NV table, pattern matcher, GC only

### 2. BB boxes -> three-column layout (the BB box emitter)

The BB graph is NOT a linear sequence of SM opcodes. It is a directed
graph of box nodes. Each box has exactly four ports:

  alpha  -- try     (IN: forward attempt)
  beta   -- retry   (IN: backtrack)
  gamma  -- success (OUT: drives next box's alpha)
  omega  -- failure (OUT: drives enclosing beta)

THE LAW (from BB-GEN-X86-TEXT.md, proven 106/106 SPITBOL oracle):
  One GNU-as proc per box. Each box = one labeled proc with local
  labels .alpha, .beta, .gamma, .omega. Emitted ONE BOX AT A TIME.

THREE-COLUMN LAW inside every box proc (this is where it applies):

  LABEL:              ACTION (macro name + params)     GOTO (jmp)

Example for a LIT box matching "Bird":

    proc BB_LIT_N
    .alpha:    LIT_CHECK  "Bird", 4    ; jmp .gamma / .omega
    .beta:     LIT_UNDO   4           ; jmp .omega
    .gamma:                           ; (wired to next box's alpha)
    .omega:                           ; (wired to enclosing omega)
    endp

Multi-box procs (globbing) for named patterns:

    proc BB_SEQ_BIRD_BLUE
    ; -- BIRD sub-box ---
    .bird_a:   LIT_CHECK "Bird", 4    ; jmp .bird_g / .bird_o
    .bird_b:   LIT_UNDO  4           ; jmp .bird_o
    .bird_g:                          ; jmp .blue_a
    .bird_o:                          ; jmp .seq_o
    ; -- BLUE sub-box ---
    .blue_a:   LIT_CHECK "Blue", 4    ; jmp .blue_g / .blue_o
    .blue_b:   LIT_UNDO  4           ; jmp .blue_o
    .blue_g:                          ; jmp .seq_g
    .blue_o:                          ; jmp .bird_b
    ; -- SEQ wiring ---
    .seq_g:    ret                    ; success
    .seq_o:    xor eax,eax / ret     ; failure
    endp

---

## File Layout

    src/runtime/x86/sm_macros.s           GNU-as macro file, one macro
                                          per SM opcode group (parallel
                                          to proven snobol4_asm.mac)
    src/runtime/x86/sm_codegen_x64_emit.c  SM emitter (emit_sm_instr)
                                          + BB box emitter (emit_bb_box)
    src/runtime/rt/scrip_rt.{h,c}        Runtime: NV table, GC, matcher

---

## sm_macros.s -- One Macro Per SM Opcode Group

    SM_PUSH_INT  val       -- push 64-bit integer literal onto SM stack
    SM_PUSH_STR  ptr, len  -- push string descriptor
    SM_PUSH_VAR  name_ptr  -- load NV table entry onto stack
    SM_STORE_VAR name_ptr  -- pop TOS -> NV table entry
    SM_POP                 -- discard TOS
    SM_ADD                 -- pop r,l; push l+r
    SM_SUB                 -- pop r,l; push l-r
    SM_MUL                 -- pop r,l; push l*r
    SM_DIV                 -- pop r,l; push l/r
    SM_MOD                 -- pop r,l; push l%r
    SM_NEG                 -- pop v; push -v
    SM_CONCAT              -- pop r,l; push l||r (string concat)
    SM_JUMP    label       -- unconditional jump
    SM_JUMP_S  label       -- jump if last result succeeded
    SM_JUMP_F  label       -- jump if last result failed
    SM_HALT                -- end program, rc <- TOS

---

## BB Box Macros -- One Macro Per Box Kind

    LIT_CHECK  ptr, len, gamma, omega  -- compare subject[cursor..cursor+len]
    LIT_UNDO   len                     -- cursor -= len; goto omega
    ANY_CHECK  charset, gamma, omega   -- subject[cursor] in charset
    SPAN_CHECK charset, gamma, omega   -- greedily consume charset chars
    ARB_ALPHA  gamma, omega            -- epsilon try; save cursor
    ARB_BETA   gamma, omega            -- grow by one; retry
    SEQ_WIRE   left_alpha, right_alpha -- connect left.gamma -> right.alpha
    ALT_ALPHA  left_alpha, right_alpha -- try left first
    ALT_BETA   right_alpha, omega      -- left failed; try right

---

## Multi-Backend Correspondence

The four-port alpha/beta/gamma/omega model is universal:

    x86 text asm:  local labels + jmp
    x86 binary:    byte offsets + patch list (bb_emit.c)
    JVM:           method-per-box, tableswitch on entry
    .NET:          delegate-per-box
    JS:            closure-per-box {alpha: fn, beta: fn}
    WASM:          function-per-box + indirect call table

Same protocol. Only representation differs.

---

## libscrip_rt.so Boundary (what stays in the runtime library)

STAYS in libscrip_rt.so (cannot be inlined):
  - NV table (scrip_rt_nv_get, scrip_rt_nv_set) -- needs GC + snobol4 runtime
  - Pattern matcher entry (scrip_rt_pat_match) -- complex C code
  - GC / memory management
  - Builtin function shims (scrip_rt_builtin_*)
  - BB broker pump (scrip_rt_bb_drive -- post-Step 19)

BAKED INLINE via macros (does NOT go through libscrip_rt):
  - Integer/real arithmetic (SM_ADD through SM_MOD)
  - Push/pop of literal integers and strings
  - Control flow (SM_JUMP, SM_JUMP_S, SM_JUMP_F)
  - SM_HALT (single epilogue jump)

---

## References

- BB-GEN-X86-TEXT.md -- three-column law + one-proc-per-box law
- BB-GRAPH.md -- four-port model, 25 standard boxes
- EMITTER-COMMON.md -- universal SM_Program walk contract
- EMITTER-X86.md -- x86 emitter status + Technique 2
- GOAL-MODE4-EMIT.md -- session state + rungs

---

## Artifact Tracking Protocol (settled session #67, 2026-05-06)

Tracked files (canonical location -- corpus repo):

    corpus/programs/snobol4/demo/roman.s           (7 KB)  side-by-side with roman.sno
    corpus/programs/snobol4/demo/wordcount.s       (10 KB)  side-by-side with wordcount.sno
    corpus/programs/snobol4/demo/claws5.s          (90 KB)  side-by-side with claws5.sno
    corpus/programs/snobol4/demo/treebank-list.s  (101 KB)  side-by-side with treebank-list.sno
    corpus/programs/snobol4/demo/treebank-array.s (120 KB)  side-by-side with treebank-array.sno

Rule: after every session touching the emitter --
  1. Regen both .s files.
  2. If assembles cleanly AND changed from repo copy -> commit.
  3. If does not assemble -> do NOT commit. Leave repo copy unchanged.
  4. Git history is the archive. No session-numbered copies.

roman.s is the primary reading artifact: small (36-line source),
recursive DEFINE, REPLACE, BREAK, pattern match -- covers key emitter
paths at readable scale. The larger three (claws5, treebank-list,
treebank-array) are tracked for assembly health, not line reading.

Programs deliberately excluded (too large for any use):
beauty.sno, expression.sno, porter.sno.

beauty_prog.s lives in SCRIP/artifacts/x64/ as the EM-7 gate artifact
(assembly check + zero UNHANDLED_OP count) but is not a reading artifact.
