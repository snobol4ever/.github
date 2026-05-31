# HANDOFF 2026-05-26 — Sonnet 4.6 — GOAL-ICON-BB JA-D Complete

## Repos
- SCRIP `e842b724` — pushed ✅
- .github  `46e80044` — pushed ✅

## Gates (final)
- smoke_icon 5/5 ✅
- unified_broker 23/23 ✅
- icon_all_rungs --interp 198 ✅
- Violator grep (seg_byte/SL_B/sl_emit_one/emit_standard_blob/bake_blob_call) = **0** ✅
- jit/JIT grep across src/ scripts/ test/ = **0** ✅

## What was done

### JA-D-2 `22a17fa3` — Engine B (SB-LINEAR) deleted
Deleted the entire SB-LINEAR block from sm_codegen.c (was sm_jit_interp.c,
lines 1759–2388, 630 lines): #define SL_B/U32/U64, all sl_* functions,
sl_emit_one, sm_emit_linear, sm_run_linear, g_jit_flat_bb.
Deleted sm_run_with_recovery_linear from scrip_sm.c.
Removed prototypes from headers. Violator count: 192 → 166.

### JA-D-3 `2073c081` — Engine A (trampoline codegen) deleted
Deleted from sm_codegen.c (lines 115–1756, 1641 lines):
g_label_blob_map/label_blob_lookup, bake_blob_call_s/si/i, STATE/PUSH/POP/CUR_INS
macros, all 44 h_* handlers + h_return_impl, handler_fn_t/g_handlers[],
g_blob_addrs/g_trampoline_offset, emit_trampoline, emit_standard_blob(+_no_stack),
emit_cond/jump/halt/label/exec_stmt_pat blob emitters, exec_stmt_pat_table_build,
SM_codegen (Engine A main entry), sm_jit_run, sm_jit_run_steps,
rt_stno/rt_push_*/rt_store_*/rt_pat_*/rt_call_fn/rt_bb_pump_proc (Engine A only).
Stubbed sync_monitor_run body. Removed dead sm_jit_run branch from
sm_run_with_recovery in scrip_sm.c. Rewrote sm_codegen.h minimal header.
Violator count: 166 → 2.

### JA-D-4+D-5 `b14a3312` — sm_image_test + GREEN-FIELD VERIFY
test_seal_and_execute() hand-emitted mov eax,42;ret into SEG_CODE — forbidden.
Replaced with seg_seal test against SEG_DATA covering the same invariant.
FACT RULE COMPLETION TEST: violator grep = **0**.
Gates: 5/5, 23, 198 — unchanged throughout.

### JA-D-6 `e842b724` — Total annihilation of jit/JIT
This project generates native x86 from the starting gate — whole-program,
one pass. JIT was borrowed mythology. Every occurrence removed:

File renames (5):
  sm_jit_interp.c → sm_codegen.c
  sm_jit_interp.h → sm_codegen.h
  test_gate_em8_snocone_jit_emit.sh → test_gate_em8_snocone_native_emit.sh
  test_monitor_2way_spitbol_vs_jit.sh → test_monitor_2way_spitbol_vs_run.sh
  test_smoke_snobol4_jit.sh → test_smoke_snobol4_run.sh

Identifier renames in sm_codegen.c:
  g_jit_prog/state/halted/step_limit/steps_done/step_jmp → g_codegen_*

7 files updated: all #include "sm_jit_interp.h" → #include "sm_codegen.h"
16 script files swept: local var jit → run_out, comment JIT → native codegen
Makefile updated for renamed .c file.
src/driver/wasm/README.md: --jit-emit → --compile --target=wasm

35 files changed. Verify grep == 0.

## Net deletions this session
- Engine B: 630 lines
- Engine A: 1641 lines
- **Total: 2271 lines of illegal x86 producers deleted**

## What Engine A and Engine B were
**Engine A** — trampoline codegen (SM_codegen): walked SM array, emitted blobs
that jumped through a central trampoline to C handlers (h_*). Used by --monitor.
Looked like native code, ran like an interpreter.

**Engine B** — SB-LINEAR (sm_emit_linear): walked SM array once, emitted flat
linear x86 with direct call rt_helper sequences. Used by --run for non-Prolog.
Honest approach but a second independent x86 producer that drifted from templates.

Both violated the ONE-PRODUCER FACT RULE. Both gone.

## State of --run
--run prints [NO-SM-BB] stub (JA-D-1, c352bf4d). Mode-3 is intentionally RED.
Prolog --run routes through sm_interp_run (AGW-1c sanctioned exception, 123 PASS).

## Next session: JA-1 rebuild
Route --run to load the SHARED emitter's template-produced bytes
(codegen_sm_x86 → emit_core dispatch → bb_*.cpp/sm_*.cpp/xa_*.cpp) into a
PROT_EXEC buffer and jump in. One-instruction thunk-templates are fine as
scaffolding. Fill real four-port x86 per opcode on the ladder.
Completion: mode-3 climbs from RED, grep stays 0, FACT RULE holds.

Read GOAL-ICON-BB.md § "THEN (next phase)" for the JA-1/J-5/J-6 spec.
