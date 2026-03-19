# BACKEND-X64.md — x64 Assembly Backend (L3)

x64 ASM backend for snobol4x.
Current: near-term stack-frame bridge (M-ASM-RECUR).
Target: Technique 2 (mmap+memcpy+relocate), post-M-BOOTSTRAP.

*Session state → TINY.md. C backend → BACKEND-C.md. Architecture → ARCH.md §Technique 2.*

---

## The Core Insight — CODE shared, DATA per-invocation

Byrd boxes are naturally reentrant. The CODE (α/β/γ/ω goto sequence) never changes.
Only the DATA (locals: cursor, captures, params) differs between simultaneous invocations.

```
┌──────────────────────────────┐  ┌──────────────────────────────┐
│  CODE (RX, shared)           │  │  CODE (RX, shared)           │
│  P_ROMAN_α:                  │  │  P_ROMAN_α:        ← same    │
│    mov rax, [r12+OFFSET_N]   │  │    mov rax, [r12+OFFSET_N]   │
│    ...                       │  │    ...                       │
├──────────────────────────────┤  ├──────────────────────────────┤
│  DATA₁ (RW, invocation 1)   │  │  DATA₂ (RW, invocation 2)   │
│  r12 → N='12', T='', cur=0  │  │  r12 → N='1',  T='', cur=0  │
└──────────────────────────────┘  └──────────────────────────────┘
     ROMAN('12') call                  ROMAN('1') recursive call
```

Same instruction `mov rax, [r12+OFFSET_N]` reads different data in each invocation.
No save/restore needed. No stack. The mechanism IS the architecture:
- α allocates a DATA copy  → that IS the save
- γ/ω discards the copy   → that IS the restore
- Byrd boxes running forward and backward ARE save and restore

**Lon's note:** This is stackless by nature. Each SNO BLOCK is a Byrd-box sequence.
It runs correctly if you give it ONE REGISTER pointing to its locals. Two simultaneous
invocations = two DATA blocks, one CODE block. EVAL/CODE build these sequences at
runtime. The initial compile builds them statically. All run at full speed.

---

## Status

| Phase | What | Gate |
|-------|------|------|
| **Now** | Near-term bridge: per-invocation C stack frames | M-ASM-RECUR |
| **Next** | roman.sno + wordcount.sno PASS | M-ASM-SAMPLES |
| **Future** | Technique 2: mmap+memcpy+relocate | M-BOOTSTRAP |

---

## M-ASM-RECUR — Near-Term Bridge (implement now)

**Problem:** current ASM backend has ONE `rbp` frame for the entire program. All
`[rbp-8/16/32/48]` temporaries are shared globals. Recursive calls corrupt them.

**Fix:** Each user-defined function's α port establishes its own stack frame.
Each invocation gets private `[rbp-8/16/32/48]` slots. Hardware stack acts as
a cheap per-invocation DATA allocator. Same isolation as Technique 2, simpler.

```c
/* emit_asm_named_def(), is_fn branch, α label: */
asmL(np->alpha_lbl);
A("    push    rbp\n");
A("    mov     rbp, rsp\n");
A("    sub     rsp, 56\n");
/* ... load args, jmp body ... */

/* γ label: */
asmL(gamma_lbl);
A("    add     rsp, 56\n");
A("    pop     rbp\n");
A("    jmp     [%s]\n", np->ret_gamma);

/* ω label: */
asmL(omega_lbl);
A("    add     rsp, 56\n");
A("    pop     rbp\n");
A("    jmp     [%s]\n", np->ret_omega);
```

Call sites: **no change** — stack push/pop for param save/restore already correct (session197).

**Optimization note (Lon):** Do NOT skip to Technique 2 now. Optimization hurts when done
too early. Debugging static generated `.s` is hard enough. The stack bridge is correct and
fully inspectable. Prove correctness first, then optimize post-M-BOOTSTRAP.

**Acceptance test:** `roman.sno` runs correctly (recursive Roman numeral conversion).
roman.sno exercises self-recursion; max depth ~2 for '12'. Should not overflow.

**Milestone trigger:** M-ASM-RECUR fires when roman.sno produces correct output AND
26/26 ASM crosscheck + 106/106 C crosscheck both hold.

---

## Technique 2 — mmap + memcpy + relocate (post-M-BOOTSTRAP)

When `*X` fires or a function is called:
1. `memcpy(new_text, box_X.text_start, len)` — copy CODE section
2. `memcpy(new_data, box_X.data_start, len)` — copy DATA section (locals)
3. `relocate(new_text, delta)` — patch relative jumps + absolute DATA refs
   - Relative refs: add `delta = new_addr - orig_addr`
   - Absolute DATA refs: patch to point at `new_data`
4. Load `r12 = new_data`
5. Jump to `new_text[α]`

TEXT: PROTECTED (RX). `mprotect→RWX` during copy+relocate, back to RX after.
DATA: UNPROTECTED (RW). One copy per live invocation.
Reclamation: LIFO discipline — discard `new_data` on γ/ω return. No GC needed.
~20 lines of runtime. No heap. No explicit save/restore. No stack.

**Gates on:** M-BOOTSTRAP (need self-hosting sno2c to emit relocation tables).

