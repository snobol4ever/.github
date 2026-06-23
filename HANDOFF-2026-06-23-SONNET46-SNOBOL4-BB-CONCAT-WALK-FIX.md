# Handoff: session-14 — SNOBOL4-BB concat double-walk fix

**Date:** 2026-06-23  
**Model:** Claude Sonnet 4.6  
**SCRIP commit:** `b3245a2`  
**corpus commit:** `351df26d`

## What landed

Fixed `flat_drive_gvar_concat` in `src/emitter/emit_bb.c`: the function
was unconditionally calling `walk_bb_flat(c0)` / `walk_bb_flat(c1)` even
when those operand nodes had already been emitted by the statement's
γ-chain (via `sno_concat_chain`'s `γ_to` wiring in lower_snobol4.c:586).
The `IR_BINOP_GVAR_CONCAT` box correctly read the first-emitted slots so
the re-walk produced dead values — but any function call in c0/c1
re-executed, doubling all side effects through the entire recursion tree.

Fix: guard each operand walk with `bb_slot_get(child) >= 0`, mirroring the
identical pattern already present in `flat_drive_gvar_assign_binop`
(lines ~1533/1544). If the slot is already populated, read it and skip
the walk.

**Effect on roman:** 15 ROMAN recursive calls → 4 (matching oracle).
All 16 benchmarks GREEN=9 / DIFF=4 / BOMB=0 — zero regressions.
Feature tests 20/21 (061_capture_in_arbno is a pre-existing POS/loop hang,
not caused by this fix; do NOT run its binary).

## Roman still wrong (CXI not CLXXVI) — next target

The concat doubling is gone, but `T` (local in `DEFINE('ROMAN(N)T')`)
emits as a global NV access and is absent from `.Lpnames0` (proc save-set
lists only the param `N`). So `rt_call_named_proc` never saves/restores
`T` across recursion; innermost frame's `T=I` clobbers all outer frames.

Root: `lower_sno_stage2` (lower_snobol4.c:1149–1163) correctly adds T to
`lower_sc`, but capture targets inside the function body resolve against
global NV instead of the frame scope, and/or `rt_proc_register` pnames
is built from params only, not locals.

Expected fix: `roman('176')` → CLXXVI, `roman('1776')` → MDCCLXXVI.

## Pre-existing items (not this session)
- `061_capture_in_arbno`: POS(N) likely not failing at end-of-string → infinite loop. Binary must not be executed.
- func_call / func_call_overhead / var_access: correct results, >30s at 10M iters.
- eval_dynamic / eval_fixed: OOM (pre-existing, EVAL path).
- indirect_dispatch: XFAIL (expected).
