# HANDOFF 2026-05-26 — Sonnet 4.6 — GOAL-ICON-BB J-4 continuation

## Commits

- SCRIP `de0f2352` — J-3/J-4: SCRIP_JIT_FLAT_BB SM_BB_PUMP_PROC → call rel32 to SM entry_pc
- SCRIP `b9203411` — J-4 cont: LOAD/STORE_FRAME, IcnFrame push, VOID_POP+RETURN fix

## What was done (b9203411)

### 1. SM_VOID_POP before SM_RETURN* = no-op

Root cause found: `sm_interp.c` has `case SM_VOID_POP:` falling through (no break) to
`SM_RETURN` — so in mode-2, VOID_POP never actually pops; the return value stays on
the nested SM stack for `sm_eval_subexpr` to read via `nested->stack[sp-1]`.
Mode-3 was calling `rt_void_pop` (POP) before RETURN, discarding the value.
Fix: peek-ahead in `sl_emit_one` — if next instruction is any RETURN variant, emit nothing.

### 2. h_return_impl: stack-top fallback for Icon proc returns

When `NV_GET_fn(retval_name)` returns empty/null (Icon procs don't use the NV var;
`rt_call_fn` sets it to `""` before calling), fall back to stack top. Fixes Icon proc
return values reaching the caller.

### 3. SM_LOAD_FRAME / SM_STORE_FRAME wired

`rt_load_frame(slot)` → `icn_frame_env_load(slot)` → `FRAME.env[slot]`
`rt_store_frame(slot)` → `icn_frame_env_store(slot, val)` → `FRAME.env[slot] = val`
Both wired in `sl_emit_one`; removed from `ignored slots` list.

### 4. rt_call_fn: push IcnFrame from call args

Before `((blob_fn_t)blob)()`, push `frame_stack[frame_depth++]` with `env[0..na-1]`
set from `call_args[]`. Pop after. Makes `icn_frame_env_load` work inside called proc.

## Gate results

- `hello.icn --run SCRIP_JIT_FLAT_BB=1` → "hello" ✅
- `double(21) --run SCRIP_JIT_FLAT_BB=1` → 42 ✅
- smoke 5/5 both flag states ✅
- broker 23 both flag states ✅

## NEXT SESSION — must do first

**1. Wire SM_ACOMP (opcode 80)** — arithmetic comparison (`n <= 1`). Used in every Icon
`if` with numeric comparison. Currently hits `rt_unimpl_op`. Implement `rt_acomp(int kind)`
mirroring `h_acomp` in the trampoline path.

**2. Wire SM_JUMP_S / SM_JUMP_F** — conditional jumps (already in sl_emit_one via
`sl_jcc_last_ok`; check they work correctly with the new last_ok semantics from SM_ACOMP).

**3. Run full J-4 gate with SCRIP_JIT_FLAT_BB=1:**
   - broker ≥19 (currently 23 ✅ already)
   - --interp rungs ≥195 (unchanged baseline test)
   - fib(7)=13 working in --run

**4. J-5: migrate ignored slots** (PUMP_SM, PUMP_CASE, BB_SWITCH) to flat path.

**5. J-6: flip default, delete C bridge**, confirm zero C-walker reachability from --run.

## Architecture notes

- The `call rel32(entry_pc)` approach calls directly into the proc's SM linear blob.
  Return: `rt_return` at `call_depth==0` sets `g_jit_halted=1`, returns 1 →
  `sl_ret_if_eax` emits native ret → unwinds to `add rsp,8` after the call.
- Frame setup/teardown wraps the call: `rt_setup_icn_frame` + call + `rt_teardown_icn_frame`.
- The VOID_POP/RETURN discovery is systemic: any place in the linear JIT that calls
  `rt_void_pop` just before a RETURN-family opcode was wrong. The peek-ahead fix in
  sl_emit_one handles all variants (RETURN/FRETURN/NRETURN + _S/_F suffixes).
