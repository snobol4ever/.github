# ARCH-x86.md — x86 Backend

Backend: x86 (native binary). Emitter file: `src/backend/emit_x64.c`.
Human name: x86. File/folder name: x64 (historical).

## Byrd Box model

Each pattern node compiles to a self-contained x86 code+data blob in `bb_pool`.
Four ports: α (proceed), β (resume), γ (succeed), ω (fail).

**ABI:**

```
Buffer layout:
  [0 .. CODE_END)   x86 code — position-independent via rel8/rel32 jumps
  [CODE_END .. end) data — mutable state (n, done, fired...) + baked ptr slots (Σ/Δ/Ω/memcmp addrs)

Entry convention:
  rdi = buffer base (fn ptr IS the buffer start — same address)
  esi = 0 (α) or 1 (β)
  r10, r11 = scratch (caller-saved — no push/pop needed)

Prologue (10 bytes, shared by all stateful boxes):
  49 89 FA          mov  r10, rdi        ; r10 = blob base
  83 FE 00          cmp  esi, 0
  74 dd             je   α
  EB dd             jmp  β

Data access pattern:
  4D 8B 42 dd       mov  rax, [r10+N]   ; load 8-byte baked ptr (Σ_addr, Δ_addr...)
  8B 00             mov  eax, [rax]     ; deref to int (Δ, Ω, n...)
  48 8B 00          mov  rax, [rax]     ; deref to ptr (Σ)
  45 89 42 dd       mov  [r10+N], eax   ; write int back to data slot (state update)
```

FAIL is the degenerate case — entry/rdi both ignored, no prologue, 5 bytes total.

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
