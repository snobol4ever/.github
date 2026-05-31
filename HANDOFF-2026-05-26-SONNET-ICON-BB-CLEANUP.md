# HANDOFF 2026-05-26 — Sonnet 4.6 — GOAL-ICON-BB opcode cleanup

## Commit

SCRIP `216f543c` — rename SM_BB_PUMP_{SM,CASE}, tombstone SM_PUMP_SM

## What was done

### Investigation

Lon asked whether SM_BB_PUMP_SM / SM_BB_PUMP_CASE relate to Byrd Boxes.
Answer: No. Neither touches BB_graph_t, four-port x86, or the emitter.

- SM_BB_PUMP_CASE: Raku case-expression dispatch. Gated on LANG_RAKU in
  lower.c (line 1242). Icon's case expression uses a completely different
  inline SM path (STORE_VAR + JUMP_F chain). Not an Icon concern at all.

- SM_BB_PUMP_SM: Never emitted by lower.c. Dead opcode. No call sites.

### Renames

SM_BB_PUMP_SM  → SM_PUMP_SM  (then immediately tombstoned)
SM_BB_PUMP_CASE → SM_PUMP_CASE (Raku-only, kept active)

The _BB_ prefix was misleading — these are SM-to-SM dispatch, not Byrd-box x86.

### Tombstone

SM_PUMP_SM → SM_UNUSED_7. h_pump_sm handler deleted. g_handlers registration
removed. 5 files touched: SM.h, lower.c, sm_prog.c, sm_jit_interp.c, sm_interp.c.

## Gates

smoke 5/5, broker 23 — unchanged.

## NEXT SESSION

Priority order:
1. Wire SM_ACOMP (opcode 80, arith compare) in sl_emit_one — needed for
   Icon `if n <= 1` etc. Implement rt_acomp(int kind) mirroring h_acomp.
2. Verify SM_JUMP_S / SM_JUMP_F work correctly with SM_ACOMP last_ok.
3. Test fib(7)=13 under SCRIP_JIT_FLAT_BB=1.
4. Run full J-4 gate: broker ≥19, rungs ≥195 with flag ON.
5. J-5: SM_PUMP_CASE mode-3 (Raku thunks → direct slab calls).
6. J-6: flip default, delete rt_bb_pump_proc + two bake sites.

## State of mode-3 x86

With SCRIP_JIT_FLAT_BB=1:
- SM spine: 100% x86 (was already complete)
- SM_BB_PUMP_PROC: now call rel32 to SM entry_pc (no C walker) ✅
- SM_LOAD/STORE_FRAME: wired via icn_frame_env_* ✅
- VOID_POP+RETURN: correct fall-through semantics ✅
- IcnFrame push in rt_call_fn: args visible to frame slots ✅
- SM_ACOMP: still rt_unimpl_op — NEXT
- SM_PUMP_CASE: still rt_unimpl_op (Raku only, not Icon) — J-5
- SM_PUMP_SM: DELETED (was dead)
- rt_bb_pump_proc: still reachable when flag OFF — deleted at J-6
