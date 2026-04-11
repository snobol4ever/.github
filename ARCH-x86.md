# ARCH-x86.md — x86 Backend

Backend: x86 (native binary). Emitter file: `src/backend/emit_x64.c`.
Human name: x86. File/folder name: x64 (historical).

## Byrd Box model

Each pattern node compiles to a self-contained x86 code+data blob in `bb_pool`.
Four ports: α (proceed), β (resume), γ (succeed), ω (fail).

**ABI:**
- `rdi` on entry = buffer base address (fn ptr == buffer start)
- `esi` = 0 (α) or 1 (β)
- `r10`, `r11` = scratch only (zero push/pop)
- Prologue: `mov r10,rdi(3) + cmp esi,0(3) + je α(2) + jmp β(2)` = 10 bytes
- Data section appended after code in same sealed RX buffer
- Baked absolute ptr slots for Σ/Δ/Ω/memcmp in data section

**Pool:**
- `bb_pool.c` — `bb_alloc/bb_seal(mprotect RW→RX)/bb_free`
- `bb_emit.c` — byte/label/patch primitives

## scrip unified executable

One binary: `scrip`, three modes:
- `scrip --ir-run file.sno` — IR tree-walk interpreter
- `scrip --sm-run file.sno` — stack machine interpreter (default)
- `scrip --gen file.sno` — in-memory x86 generation

## Binary box coverage (current)

XCHR / XEPS / XSPNC / XANYC / XNNYC / XBRKC / XPOSI / XRPSI / XTB / XRTB / XLNTH /
XNME / XFNME / XSTAR / XOR / XFARB / XBRKX — 85.5% corpus coverage.
C-path fallback: XATP(12) XCALLCAP(5) XARBN(5) XDSAR(1) XFAIL(1).

## Stack machine (SM_Program)

SM-LOWER compiles IR → flat array of SM_t instructions.
INTERP dispatches instructions. EMITTER walks same SM_Program → native code.
One instruction set. No divergence between interpreter and emitter.
