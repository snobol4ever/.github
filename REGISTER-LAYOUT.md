# REGISTER-LAYOUT.md — SCRIP mode-3 x86-64 register convention

⛔ **This is the locked register convention for mode-3 SM-blob emission
and for flat-BB glob emission.**  Every blob, every glob, every PLT
call signature in mode 3 obeys this.  Changes require an explicit goal
rung and Lon sign-off.

**Sources of truth referenced in this doc:**
- `archive/backend/bb_boxes.s` — proven 25-box library, 106/106 oracle.
- `/home/claude/x64/int.h`, `int.asm`, `sbl.min` — SPITBOL x64
  MINIMAL register map and save/restore discipline.
- `/home/claude/csnobol4/v311.sil`, `snobol4.c`, `res.h` — CSNOBOL4
  memory-resident SIL working slots (XPTR, YPTR, ZPTR, WCL, WPTR…).
- `src/runtime/x86/bb_flat.c` — live flat-glob emitter; the `r10`
  convention this doc locks already ships there.
- `ARCH-x86.md` — defines the flat-BB ABI and the intra-/extra-BLOB
  jump rules this doc operates against.

---

## TL;DR — register assignments

| Reg | Class | Role | Scope | When loaded |
|-----|-------|------|-------|-------------|
| **r12** | callee-saved | `SM_State*` | Whole program | Once at `sm_jit_run` entry; never reloaded |
| **r13** | callee-saved | `SM_State.stack` base ptr (value-stack data) | Whole program | Once at `sm_jit_run` entry; reloaded by SM_STNO blob |
| **r14** | callee-saved | `SM_State.sp` — current value-stack index, kept hot | Whole program | Once at `sm_jit_run` entry; reset to 0 by SM_STNO blob |
| **r15** | callee-saved | Reserved for ME-8 chunk return-frame anchor | Per chunk call | ME-8; free until then |
| **rbx** | callee-saved | Reserved for ME-11 SM_EXEC_STMT subject anchor | Per EXEC_STMT | ME-11; free until then |
| **rbp** | callee-saved | Chunk frame ptr for DEFINE'd chunks | Per chunk | `push rbp; mov rbp, rsp` at chunk α-entry |
| **r10** | caller-saved | **BB-glob LOCAL data ptr** — `[r10+N]` addresses every box's locals in the active glob | Per BLOB; **constant inside a BLOB** | `lea r10, [rip + Δ_data]` at α-preamble of every BLOB |
| **rax rdi rsi rdx rcx r8 r9 r11** | scratch | Per-blob arithmetic + PLT arg shuffle | Per blob | As needed |
| **xmm0–xmm15** | scratch | Real arithmetic when DESCR_t is real | Per blob | As needed |

**Three "always-live" SM-blob registers: r12, r13, r14.**  Loaded once at
`sm_jit_run` entry, preserved by every PLT call (System V callee-saved),
reset/reloaded only by SM_STNO at statement boundaries.  All inline
arithmetic and stack ops can assume them hot.

**One always-live BB-glob register: r10.**  Set by every BLOB's α-preamble
to point at *that BLOB's* LOCAL data region.  Constant for the duration
of execution inside the BLOB.  No PLT calls inside a glob (flat-glob
eligibility rules already enforce this — `flat_is_eligible_node`), so
`r10`'s caller-saved status is not a problem there.

---

## Two stacks

Mirrors SPITBOL's design — one value/operand stack in the heap, one
native stack for control flow.

### Stack 1 — SM value stack (heap, `[r13 + r14*16]`)

Allocated and grown by `rt_*` runtime; anchored at `r13`; index in `r14`.
Stores DESCR_t values (16 bytes each).  Used by:
- All SM_PUSH_* / SM_POP / arithmetic / store/load opcodes.
- Pattern construction (after ME-1 — pat-stack collapsed in).
- SM_EXEC_STMT operands (subject, pattern, replacement).

**Reset at every statement boundary** by SM_STNO blob (the mode-2
contract at `sm_interp.c:295`).

### Stack 2 — Native rsp (the C stack)

Used by:
- C-ABI `call`/`ret`.
- Chunk prologue/epilogue (`push rbp ; mov rbp, rsp` / `pop rbp ; ret`).
- Byrd-box history (every alternative pushes `{cursor, failback_ptr}`).
  This is exactly SPITBOL's `xs = rsp` discipline — `sbl.min`'s pattern
  engine uses `mov -(xs), pmhbs` style pushes throughout.
- LOCAL save/restore on call-style extra-BLOB jumps (see "Push/pop
  matrix" below).

---

## Push/pop matrix

| Event | Pushed | Popped | Notes |
|-------|--------|--------|-------|
| `sm_jit_run` entry | (nothing) | (nothing) | C compiler's prologue saves r12/r13/r14/r15/rbx/rbp as callee-saved per SysV.  `sm_jit_run` is the C function whose frame holds them. |
| **Intra-BLOB jump** | nothing | nothing | LOCAL unchanged.  Plain `jmp rel32 target`. |
| **Extra-BLOB tail-jump** (most common) | nothing | nothing | Source BLOB's r10 dies; destination BLOB's α-preamble loads its own r10. |
| **Extra-BLOB call-style jump** (rare; capture callbacks) | `push r10` before outbound `jmp`/`call` | `pop r10` at the resume point inside the source BLOB | Push/pop are the **source BLOB's responsibility**.  The destination's α-preamble unconditionally loads its own r10. |
| **α-entry of any BLOB** | (nothing) | (nothing) | First instruction of every BLOB is `lea r10, [rip + Δ_data_for_THIS_glob]`. |
| **γ/ω-exit of a BLOB** | (nothing on its own) | (nothing on its own) | Whatever push happened before entering this BLOB is mirrored by the source BLOB's pop on the back-jump. |
| **Chunk α-entry (DEFINE'd fn)** | `push rbp ; mov rbp, rsp` | `pop rbp` (at chunk ω-exit / `ret`) | Standard SysV-compatible frame. |
| **PLT call from SM-blob land** | (nothing extra) | (nothing extra) | r12/r13/r14/r15/rbx/rbp are callee-saved by SysV — the PLT target preserves them.  r10/r11 are scratch — SM-blob land never uses them, so no save is needed there. |
| **SM_STNO blob** | (nothing) | (nothing) | Inline: `xor r14d, r14d ; mov r13, [r12 + STACK_OFFSET]`.  Resets sp; reloads stack base (handles realloc). |
| **SM_CALL_CHUNK (ME-8)** | `push <return_pc> ; push r14_at_call ; push last_ok ; mov r15, rsp` | mirror `pop` at SM_RETURN; restore `r15` | Three-word return frame.  See §"EVAL/CODE re-entrancy" below. |
| **SM_EXEC_STMT (ME-11)** | `mov [r12+STACK_OFFSET], r13 ; mov [r12+SP_OFFSET], r14` before `call rt_exec_stmt` | reload r13/r14 from `[r12+...]` after return | Spill to SM_State so the BB engine's nested calls see canonical state.  rt_exec_stmt itself preserves r12/r13/r14 by ABI, but the BB engine called from within it reads `SM_State.stack/sp` directly. |
| **EVAL/CODE/`*expr` (ME-8 consumer)** | `push r10 ; push sm_pc_return ; push r14 ; push last_ok ; push pmhbs_equiv ; push pmdfl_equiv` | mirror pop on resume | SPITBOL's `evalp` saves 6 things; SCRIP needs the same 6 with different names. |

---

## Why this layout — evidence base

### r12 = SM_State* (mirrors SPITBOL's IA = r12 discipline)

SPITBOL `int.h:48`: `%define ia r12`.  `int.asm:162`: `reg_ia: d_word 0 ; register ia (r12)`.  IA is SPITBOL's integer
accumulator, used as the "always-live" callee-saved register for the duration
of every MINIMAL routine.  SCRIP's `r12 = SM_State*` is the same play in a
different role — one callee-saved register reserved for the most-frequently-
accessed pointer in the system.

`SM_State` carries the value-stack base, sp, last_ok, kw_rtntype, and the
PC.  Anchoring `r12` at it means every SM-blob can reach every piece of
runtime state with a single `[r12 + offset]` load — no PLT round-trip,
no global-variable mov.

### r13 = stack base + r14 = sp (split decision)

Two options were considered:

**Option A: r13 = stack base, r14 = sp** (chosen).  Push is
`mov [r13 + r14*16], rax ; mov [r13 + r14*16 + 8], rdx ; inc r14d`.
Three instructions, ~16 bytes.

**Option B: r13 = end-of-stack ptr** (rejected).  Push is
`mov [r13], rax ; mov [r13+8], rdx ; add r13, 16`.  Also three
instructions, ~12 bytes.  Cheaper per-push but loses easy random access
(`SM_PEEK n`, `SM_DUP`, pattern-construction operands at varying depths
all need `r13 - (sp - target_idx) * 16` arithmetic instead of a clean
`[r13 + idx*16]`).

Pattern construction (SM_PAT_CAT, SM_PAT_ALT, SM_PAT_ARBNO after ME-1)
needs to pop multiple operands of varying depth.  Option A keeps that
addressing as a single SIB-encoded mov.  Option B would force a per-pop
`sub r13, 16` and complicate any multi-operand operation.

**Mirrors SPITBOL only loosely.**  SPITBOL's value stack is the same as
its history stack (`xs = rsp`).  We can't do that because the SM value
stack carries 16-byte DESCR_t entries that need realloc, while the
history stack is C-ABI rsp.  Splitting them costs one register; that's
the price of having a richer value type than SPITBOL's word-sized
descriptors.

### r10 = BB-glob LOCAL (already in `bb_flat.c`)

This convention isn't new — `bb_flat.c` already loads `r10` at glob
entry as `lea r10, [rip + Δ_data]` and accesses every box-local as
`[r10 + N]`.  This doc just **promotes it from "what bb_flat happens
to do" to "the locked convention" and adds the intra-/extra-BLOB
push/pop discipline.**

Why caller-saved?  Because System V x86-64 marks `r10`/`r11` caller-
saved.  Mode-3 SM-blob land neither reads nor writes `r10`, so PLT
calls from SM-blob land can freely clobber it.  Inside a flat glob,
there are no PLT calls (flat-glob eligibility requires invariant
sub-trees), so `r10` is effectively callee-saved-by-convention — the
glob body never observes a `r10` clobber because nothing clobbers it.

**The intra-/extra-BLOB rule formalizes the boundary.**  Inside a BLOB,
r10 is constant.  Crossing a BLOB boundary, r10 is reloaded by the
destination's α-preamble.  The source BLOB's `push r10` / `pop r10`
is only needed if control returns mid-BLOB (call-style); in the common
tail-jump case (γ/ω → next glob), neither push nor pop is emitted.

### r15, rbx — held in reserve

These two callee-saved registers are deliberately left unclaimed so
ME-8 (chunk dispatch, return frames) and ME-11 (SM_EXEC_STMT subject)
have headroom.  Pre-claiming them now would either lock in a design
before evidence (we don't know yet exactly what ME-8's return frame
will hold) or waste them (using rbx for some short-lived thing only
to need it later for the subject pointer).

**SPITBOL has 8 named MINIMAL registers (IA, W0, WA, WB, WC, XL, XR,
CP).**  SCRIP claims 4 of those slots (r12, r13, r14, r10) and reserves
2 more (r15, rbx) for the next two rungs.  rbp is the chunk frame; the
SysV C scratch set (rax/rdi/rsi/rdx/rcx/r8/r9/r11) covers everything
else.  We are not over-budgeted.

### rbp = chunk frame ptr

Standard SysV-compatible discipline.  `push rbp ; mov rbp, rsp` at chunk
α-entry; `pop rbp ; ret` at ω-exit.  Required to fix the realloc bug's
sibling: bbsim/define drivers that PLT-call `vsnprintf` faulted on
`rsp%16==8` in the legacy emitter (`emit_x64.c`).  The 16-byte alignment
is reachable for free via the standard `push rbp` + ABI rules.

---

## SPITBOL register map (for reference)

| MINIMAL | x86-64 | Class | Role |
|---------|--------|-------|------|
| IA | r12 | callee-saved | Integer accumulator |
| W0 | rax | scratch | Wide-zero / temp |
| WA | rcx | scratch | Working register A |
| WB | rbx | callee-saved | Working register B (cursor in match) |
| WC | rdx | scratch | Working register C |
| XL | rsi | scratch | Index-left (source) |
| XR | rdi | scratch | Index-right (current node ptr) |
| XS | rsp | (special) | History stack = native stack |
| XT | rsi (alias) | scratch | Temporary (aliased to XL) |
| CP | r13 | callee-saved | Code pointer (current opcode-stream PC) |
| RA | xmm12 | (preserved) | Real accumulator |

SPITBOL save/restore (from `save_regs` / `restore_regs` in `int.asm`)
captures all of these to a fixed `reg_block` in `.bss` whenever MINIMAL
calls into C OSINT — used to preserve state across the C→MINIMAL→C
re-entry path triggered by syscalls.

SCRIP doesn't need an analogous `save_regs`.  System V's callee-saved
discipline plus the per-PLT-call convention give us re-entry safety
for free: r12/r13/r14/r15/rbx/rbp survive every `call`, and the
sm_jit_run C-frame's epilogue restores them when mode-3 execution
ends.

---

## CSNOBOL4 register map (for reference)

CSNOBOL4 (v311.sil → snobol4.c) keeps every SIL "register" as a memory-
resident `struct descr` slot in `res` (XPTR, YPTR, ZPTR, WCL, WPTR, TPTR,
TVAL, ~20 working slots total).  Register allocation is delegated to gcc.

The SIL spec defines an *abstract* register file; SPITBOL realized 8 of
them in x86 hardware; CSNOBOL4 realizes zero.  SCRIP follows SPITBOL's
"realize the hot ones in hardware" approach but with a much smaller
working set (3 always-live in SM-blob land + 1 in BB-glob land = 4)
because SCRIP's IR-to-SM lowering does the SIL-register-allocation work
ahead of time, not at MINIMAL-instruction-dispatch time.

---

## EVAL/CODE re-entrancy (relevant to ME-8)

SPITBOL's `evalp` (sbl.min:20767–20825) saves 6 words on `xs` before
running the expression:

```
push xr     ; node pointer
push wb     ; cursor
push r_pms  ; subject string pointer
push pmssl  ; subject string length
push pmdfl  ; dot flag
push pmhbs  ; history stack base
```

`evalx` for full expression evaluation saves an additional 5 words (old
code block pointer, code offset, fail pointer, name/value flag, new
fail offset).  Total: ~11 words per nested EVAL.

The SCRIP equivalent (ME-8) needs to save:
- `sm_pc_return` — where to resume after SM_RETURN.
- `r14_at_call` — value-stack sp at call time (for SM_RETURN balance check).
- `last_ok` — currently the only SM_State field that sub-expressions mutate.
- `r10_at_call` — only if the EVAL is happening mid-glob (rare but possible).
- A pmhbs-equivalent (history stack base) — only if mid-pattern.
- A pmdfl-equivalent (dot flag) — only if mid-pattern.

The minimum viable return frame is 3 words: `{return_pc, r14, last_ok}`.
The pattern-context cases add up to 3 more.  Total: 3–6 words per nested
EVAL/CODE — substantially less than SPITBOL's 11 because SCRIP doesn't
have OCBSCL/PATBCL/specifier slots.  DESCR_t carries the whole world.

---

## Audit checklist before ME-4-post

When ME-4-post (the inline-native blob re-emission) lands, every blob
must satisfy:

- [ ] **No `[r12 + 0]` reload of stack base.**  Use `r13` directly.
- [ ] **No reload of sp from memory.**  Use `r14` directly.
- [ ] **Stack push:** `mov [r13 + r14*16], rax ; mov [r13 + r14*16 + 8], rdx ; inc r14d`.  (May be re-ordered for scheduling.)
- [ ] **Stack pop:** `dec r14d ; mov rax, [r13 + r14*16] ; mov rdx, [r13 + r14*16 + 8]`.
- [ ] **No `xor edx, edx` ; `mov` ; `add rsp, 8`** alignment dance — chunk frames carry alignment now.
- [ ] **PLT calls preserve nothing additional** — System V handles r12/r13/r14/r15/rbx/rbp.
- [ ] **SM_STNO blob:** `xor r14d, r14d ; mov r13, [r12 + STACK_OFFSET]`.  Both reset.
- [ ] **No emitted code writes r10** unless we have entered a BB-glob via SM_EXEC_STMT (and even then, the glob's preamble does the write — SM-blob land never touches r10 directly).

Pass criteria for ME-4-post: smoke 7/7, unified_broker 49/49 hold;
the canonical multi-statement arithmetic reproducer (from the ME-4
emergency handoff note) runs byte-identical between `--jit-run` and
`--sm-run`; per-blob size shrinks from ~28 bytes to ~18 bytes (the
~25-byte-per-blob savings the goal file predicted).

---

## Watermark

**Carved sess 2026-05-10 (Claude latest), Lon-directed.**  Architecture
based on close reading of SPITBOL x64 (`int.h`/`int.asm`/`sbl.min`),
CSNOBOL4 (`v311.sil`/`snobol4.c`/`res.h`), `bb_boxes.s` 106/106 oracle,
live `bb_flat.c` flat-glob discipline, and the existing ME-1/ME-2/ME-3
locked decisions.  No code lands under ME-4-pre — this doc is the
deliverable.  ME-4-post unblocks once Lon signs off.

**Lon sign-off:** [ ] pending

When signed, ME-4-pre closes; ME-4-post becomes active; the audit
checklist above gates ME-4-post's commit.
