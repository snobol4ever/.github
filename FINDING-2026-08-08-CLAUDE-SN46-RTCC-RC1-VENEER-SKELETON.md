# FINDING — 2026-08-08 — Claude SN4.6 — RTCC RC-1: Veneer Skeleton

**Session:** s1 of GOAL-RTCC.md (Sonnet 4.6, same session as RC-0)
**SCRIP HEAD:** `b1aca5dc`
**Date:** 2026-08-08 UTC

---

## What landed

### New files
- `src/runtime/rtx/rtcc.h` — RTCC block layout (RTCC_GPR_COUNT=9, RTCC_XMM_COUNT=8, RTCC_BLOCK_BYTES=200→256B padded), slot indices, extern declarations, coexpr API.
- `src/runtime/rtx/rtcc_init.c` — 256B-aligned BSS block `g_rtcc_block[32]`, `g_rtcc_on` gate, `__attribute__((constructor))` init reading `SCRIP_RTCC` env (default 0), GC registration via `rt_gc_root_pin_add`, `rtcc_coexpr_save`/`rtcc_coexpr_restore` (Option B block-swap — `memcpy` of `RTCC_BLOCK_BYTES`, no-op when `g_rtcc_on==0`).
- Added to `Makefile` `RT_PIC_SRCS`.

### Modified files
- `src/runtime/rt/rt_coexpr.h` — `rtcc_spill[32]` field added to `scrip_coctx_t` (zero-init = safe at gate OFF).
- `src/runtime/rt/rt_coexpr.c` — `rtcc_coexpr_save(old->rtcc_spill)` wired immediately after the `__asm__` callee-save block; `rtcc_coexpr_restore(old->rtcc_spill)` wired after `sem_wait` resume before `rt_scan_state_apply`. Both calls are no-ops at `SCRIP_RTCC=0`.
- `src/templates/x86_asm.h` — `x86_rtcc_call(sym, ptr)` helper (= `x86_call_ro` structurally at RC-1, with comment noting RC-2 wires the block); `XK_SYM && xb.tag == 2` dispatch arm routes through `x86_rtcc_call` instead of bare `x86_call_ro`.

---

## Coexpr ruling: Option B (block-swap) — FINAL

`scrip_coswitch` already saves/restores `{rbx rbp r12 r13 r14 r15}` to `gc_spill[6]` at the same two sites (pre-`sem_post` and post-`sem_wait`). Adding a 256B `memcpy` at those sites costs nothing for non-coexpr programs (the block exists in BSS but `rtcc_coexpr_save` is guarded by `g_rtcc_on`) and is safe by the same induction argument as the BLOCK-CANONICAL design: each coexpr's `rtcc_spill` snapshot holds the VM-register values for its own activation; restore on resume completes the cache-semantics handshake.

Option A (TLS, `fs`-relative addressing) rejected: would require a new `x86("load_rtcc_tls")` encoder arm and `pthread_key` infrastructure with no correctness advantage over Option B.

---

## Killswitch md5 gate: PASS

| program | SCRIP_RTCC=0 | (unset) | verdict |
|---|---|---|---|
| fibonacci.sno | ef262e25103eb805f4735d0f102a2ca6 | ef262e25103eb805f4735d0f102a2ca6 | IDENTICAL |
| arith_int.sno | b5a7a0cf60457deb66f2e3caf511363d | b5a7a0cf60457deb66f2e3caf511363d | IDENTICAL |
| func_call.sno | f2a89c196c1ee8c9348b01bd022b1938 | f2a89c196c1ee8c9348b01bd022b1938 | IDENTICAL |

`SCRIP_RTCC=1` runs: fibonacci prints `result: 832040 ms: 584`, arith_int prints `iterations: 100000000 ms: 1811`. Veneer arm is live but vacuous (zero claimed registers at RC-1 — the block is correct per the killswitch and the GC is registered, but no register values are written to it).

## Crosscheck: on RC-0 floor

m3 260/57/0 DIVERGE 18 · m4 241/75/1 — identical to RC-0 floor within 160_pat_alt flake variance.

---

## RC-1 open items (carry to RC-2)

1. **Poison probe deferred**: the "BY CONSTRUCTION is a hypothesis until a probe kills the arm" law requires a deliberate block-poison run under `SCRIP_RTCC=1` to crash a witness before RC-2 spends. At RC-1, zero registers are claimed so the block is never read by generated code — the probe has no target. RC-2 (scratch-tier claim) is what gives the poison somewhere to land. Due at RC-2 open.

2. **Inbound stubs not yet wired**: `bb_glue_*`, `xa_flat`, `rt_chain_enter` glue do not yet emit LOAD on entry. These are C→generated edges (RC-0(d) edge class 1). Wiring them is the RC-2 inbound half — they need LOAD before the first generated instruction touches any claimed register.

3. **141-probe emit set killswitch sweep**: the full 141-probe md5 sweep is owed. The 3-program spot-check above passes; the full sweep is the RC-2 gate (per the rung notes).

---

## NEXT: RC-2 — Claim the SCRATCH TIER

RC-2 open items:
- Poison probe (crash a witness with a block-poisoned block under `SCRIP_RTCC=1`)
- Claim {R10 R11 R8 R9 XMM8–15} in the emitter register model
- Wire the 5 r8/r9-arg symbols (`rt_scan_enter`, `rt_scan_lit`, `rt_match_replace`, `rt_rev_swap_fwd`, `rt_rev_swap_undo`) with per-symbol staging in the veneer
- Wire inbound LOAD stubs at `bb_glue_*`, `xa_flat`, `rt_chain_enter`
- Full 141-probe killswitch sweep both modes
- Record crater vs RC-0 floor (ZETA-MECH may still be in recovery)

⛔ RC-2 is NOT-CONCURRENCY-SAFE. Lon routes the window.
