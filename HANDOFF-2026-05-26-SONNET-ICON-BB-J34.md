# HANDOFF 2026-05-26 — Sonnet 4.6 — GOAL-ICON-BB J-3/J-4

## What was done

one4all `de0f2352` pushed. Two changes in `src/processor/sm_jit_interp.c`:

### 1. J-3/J-4: SCRIP_JIT_FLAT_BB=1 routes SM_BB_PUMP_PROC to SM entry_pc

When env `SCRIP_JIT_FLAT_BB=1` is set, `sl_emit_one` SM_BB_PUMP_PROC arm:
- Looks up proc name in `g_stage2.proc_table` at emit time (while proc_table is alive)
- Gets `entry_pc` (the SM PC of the proc's linear blob entry label)
- Emits `sub rsp,8 / call rel32 / add rsp,8` with a patch placeholder
- `sl_add_patch(slot, entry_pc)` — pass 2 patches to `sl_instr_addr[entry_pc]`

Mirrors mode-4 `CALL_EXPRESSION .L<entry_pc>` from sm_bb_calls.cpp.
No BB_graph_t, no SM ptr, no C walker at runtime. Respects FACTS 1-4.
Flag OFF: original broken `call rt_bb_pump_proc` unchanged.

### 2. rt_call_fn fix: try icn_try_call_builtin_by_name before INVOKE_fn

Before INVOKE_fn fallback in linear `rt_call_fn`, now calls
`icn_try_call_builtin_by_name(name, args, nargs, &br)`. Mirrors mode-2
`SM_CALL_FN`. Fixes Icon builtins like `write` in the flat path.

## Gate results

- `--run hello.icn` SCRIP_JIT_FLAT_BB=1: prints **hello** ✅
- Flag OFF: `sm_eval_subexpr: invalid entry_pc 1` (unchanged) ✅
- smoke 5/5 both flag states ✅; broker 23 unchanged ✅

## NEXT SESSION

1. Full J-4 gate: broker ≥19, rungs ≥195 with SCRIP_JIT_FLAT_BB=1.
2. J-5: migrate PUMP_SM/PUMP_CASE/BB_SWITCH from ignored slots.
3. J-6: flip default, delete rt_bb_pump_proc + bake sites.

## Architecture note

`call rel32` to `entry_pc` works because the SM spine is one contiguous
linear blob. Return: `rt_return` with `call_depth==0` sets `g_jit_halted=1`,
returns 1 → `sl_ret_if_eax` emits native ret → unwinds to `add rsp,8`.
Procs with args/locals need SmCallFrame setup (J-5 work).
