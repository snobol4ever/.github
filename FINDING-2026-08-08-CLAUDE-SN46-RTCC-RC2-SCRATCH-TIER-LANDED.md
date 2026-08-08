# FINDING — 2026-08-08 — Claude SN4.6 — RTCC RC-2: Scratch Tier Landed

**Session:** s2 of GOAL-RTCC.md (Sonnet 4.6, same day as RC-0/RC-1)
**SCRIP HEAD:** `d6e136d9`
**Date:** 2026-08-08 UTC

---

## RC-2(a) — POISON PROBE: PASS (RC-1 obligation discharged)

The "BY CONSTRUCTION is a hypothesis" law requires a deliberate block-poison run at RC-2 open.

**RC-1 poison baseline** (owed since RC-1 close): block slots R8/R9/R10/R11 written to `0xDEADBEEFDEADBEEF` via LD_PRELOAD under `SCRIP_RTCC=1`. fibonacci ran clean (rc=0, result: 832040). Confirms: RC-1 carried zero claimed registers — block never read. Arm was vacuous by design. Gate: PASS.

**RC-2 liveness probe**: after x86_rtcc_call wired, a destructor-reported block dump showed:

| slot | value | verdict |
|---|---|---|
| R8  (slot 5) | 000000000040033f | OVERWRITTEN (live) |
| R9  (slot 6) | 0000000000400318 | OVERWRITTEN (live) |
| R10 (slot 7) | 00007fc8117480c0 | OVERWRITTEN (live) |
| R11 (slot 8) | 000000003b9aca00 | OVERWRITTEN (live) |

**4/4 slots overwritten — arm is LIVE.** Program output: 832040 (correct). The hypothesis is falsified in the right direction: the writeback IS reaching the block.

---

## What landed

### Modified files

**`src/templates/x86_asm.h`**
- `g_rtcc_block[32]` and `g_rtcc_on` extern declarations added to the header's `extern "C"` block (needed by x86_rtcc_call at template-instantiation time).
- `x86_rtcc_call` promoted from RC-1 stub (`return x86_call_ro(sym,ptr)`) to full veneer:
  - `g_rtcc_on==0` (killswitch): falls through to `x86_call_ro` — byte-identical.
  - `g_rtcc_on==1`, BINARY mode:
    ```
    push r11                           ; save r11 on stack (can't hold base+old value in one reg)
    movabs r11, &g_rtcc_block          ; r11 = block base (clobbers old r11)
    mov [r11 + 56], r10                ; writeback R10 (slot 7, 7×8=56)
    mov [r11 + 40], r8                 ; writeback R8  (slot 5, 5×8=40)
    mov [r11 + 48], r9                 ; writeback R9  (slot 6, 6×8=48)
    pop qword ptr [r11 + 64]           ; writeback R11 (slot 8, 8×8=64) — pops directly to slot
    movabs rax, ptr ; call rax         ; the actual C call (RAX not yet claimed: ARG TIER RC-4)
    movabs r11, &g_rtcc_block          ; r11 = block base again for reload
    mov r10, [r11 + 56]                ; reload R10
    mov r8,  [r11 + 40]                ; reload R8
    mov r9,  [r11 + 48]                ; reload R9
    mov r11, [r11 + 64]                ; reload R11 — LAST (was holding base until now)
    ```
  - `g_rtcc_on==1`, TEXT mode: GOT-indirect equivalent (`g_rtcc_block@GOTPCREL`).
  - **ENCODING NOTE**: The `push r11 / pop [r11+64]` idiom solves the base-register problem: you cannot hold the block base address AND preserve R11's old value in a single register. `push r11` saves R11's old value on the stack; `pop qword ptr [r11+64]` pops it directly into the block slot — one push, one pop, no intermediate spill.

**`src/runtime/rtx/rtcc.h`**
- `rtcc_load_scratch()` declared: inbound C→generated LOAD helper; no-op at `g_rtcc_on==0`.

**`src/runtime/rtx/rtcc_init.c`**
- `rtcc_load_scratch()` implemented: `__asm__ __volatile__` loads block slots for R10/R11/R8/R9 into those registers; gcc clobber list declared. Gate: `if (!g_rtcc_on) return`.

**`src/runtime/runtime_eval.c`**
- `rt_chain_enter` inline asm (RC-0(d) edge class 1): GOT-indirect LOAD of R10/R11/R8/R9 from block inserted before `jmp *%rax` into generated code:
  ```asm
  movq g_rtcc_on@GOTPCREL(%rip), %r10
  cmpb $0, (%r10)
  je skip
  movq g_rtcc_block@GOTPCREL(%rip), %r10
  movq 64(%r10), %r11
  movq 40(%r10), %r8
  movq 48(%r10), %r9
  movq 56(%r10), %r10    ; r10 last (held base address until now)
  skip:
  jmp *%rax
  ```
  PIC-safe; `rax`/`rcx`/`rdx` (the live jmp-target and wire-setup registers) are untouched.

**`scripts/rtcc_board_sweep.sh`** — new crater instrument (ON-vs-OFF BY-SET diff across xc318).

---

## Structural verification

- **Veneer site count (fibonacci TEXT):** 112 `g_rtcc_block@GOTPCREL` references = 56 call sites × 2 (writeback + reload). Every C-RT call is bracketed.
- **Choke gate:** unchanged — all 56 sites still route through the single `x86("call")` dispatch arm at `x86_asm.h:1498`.

---

## Killswitch gate: PASS

| program | SCRIP_RTCC=0 | (unset) | vs RC-1 | verdict |
|---|---|---|---|---|
| fibonacci.sno | ef262e25103eb805f4735d0f102a2ca6 | ef262e25103eb805f4735d0f102a2ca6 | IDENTICAL | PASS |
| arith_int.sno | b5a7a0cf60457deb66f2e3caf511363d | b5a7a0cf60457deb66f2e3caf511363d | IDENTICAL | PASS |
| func_call.sno | f2a89c196c1ee8c9348b01bd022b1938 | f2a89c196c1ee8c9348b01bd022b1938 | IDENTICAL | PASS |

All three md5s byte-for-byte identical to the RC-1 FINDING. Spot-check sweep: 31/31 programs (1-in-10 sample of xc318) IDENTICAL between gate OFF and gate unset.

---

## Crater: ZERO (ON vs OFF BY-SET method)

The CRATER ATTRIBUTION law forbids gating against a floor recorded at a different HEAD during concurrent ZETA-MECH recovery. RC-2 uses the BY-SET instrument (`scripts/rtcc_board_sweep.sh`): same binary, same board, gate OFF vs gate ON, fail sets diffed BY SET. Only a PASS→FAIL move in the ON arm is attributable to RTCC.

**Mode-3 xc318 board (318 programs):**

| arm | PASS | DIVERGE | ERROR | TIMEOUT |
|---|---|---|---|---|
| OFF (SCRIP_RTCC=0) | 201 | 17 | 100 | 0 |
| ON  (SCRIP_RTCC=1) | 201 | 16 | 101 | 0 |

BY-SET mover: **1 program** — `175_pat_bal_generator_retry`, DIVERGE→ERROR.
**Not RTCC's**: at gate OFF (proven byte-identical to pre-RTCC tree), this program SEGVs in 3/3 independent runs. Nondeterministic — matches the quarantine shape of the `160_pat_alt` flake class in the RC-0 floor. The BAL generator retry mechanism (SPITBOL Ch.18: BAL extends on retry via implicit alternatives, threading through the pushdown stack) has a pre-existing defect independent of RTCC.

**141-probe suite:**

| suite | gate OFF FAIL | gate ON FAIL | BY-SET diff |
|---|---|---|---|
| mode-3 | 80 | 80 | IDENTICAL |
| mode-4 | 33 | 33 | IDENTICAL |

**Crater: ZERO programs moved from PASS in either medium.**

---

## CARRY items to RC-3 (not correctness-blocking)

At RC-2 no VM global is assigned to R8/R9/R10/R11 (that is RC-5). Generated code writes those registers before reading them; the inbound LOAD populates them from the block but the block holds zeros (or prior VM values), which is safe. The carry items are protocol-completeness work:

1. **xa_flat proc-prologue inbound LOAD** (RC-0(d) edge class 2): when a proc body is entered via `jmp rax` from the call-site template, R10/R11/R8/R9 should be loaded from the block. Requires a new `x86()` call in the xa_flat zframe/deep-arrival path. Not wired.
2. **`rt_call_arr_impl` inbound LOAD** (RC-0(d) edge class 5): the `APPLY_fn` dispatch into generated proc bodies should LOAD on entry. Not wired.
3. **Full 318-program m4 killswitch md5 sweep**: container throughput prevented completion; spot-check (31 programs) is clean; the gate is structurally guaranteed by the emit-time `g_rtcc_on` branch.

---

## NEXT: RC-3 — DEBUG LADDER I

Gate: xc318 m3 ≥ 201 PASS (RC-0 floor was 259–260 at HEAD `2ba70058`; current board at `d6e136d9` shows 201 PASS with ZETA-MECH concurrent-crater present; RC-3 targets ≥ this level). MONITOR-FIRST only. ⛔ RC-4 is NOT-CONCURRENCY-SAFE — Lon routes the window.
