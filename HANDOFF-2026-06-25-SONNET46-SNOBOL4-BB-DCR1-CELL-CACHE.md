# SNOBOL4-BB DCR-1: cell-cache save/restore

**Date:** 2026-06-25
**Model:** Claude Sonnet 4.6
**SCRIP commit:** `4b663b0`
**corpus commit:** (no change — runtime-only, no .s artifacts)

## What landed

DCR-1 per GOAL-SNOBOL4-BB.md: replace per-call `NV_GET_fn`/`NV_SET_fn`
hash-walks in `rt_name_save_push` / `rt_name_restore` /
`rt_call_named_proc{,_sl}` with direct `*cell` ops.

### rt.c

- `NameSaveEnt` gains `DESCR_t *cell` (NULL ⇒ by-name fallback).
- `g_cell_cache[2048]`: direct-mapped, keyed by `(uintptr_t)name >> 4`.
  Hit is a pointer-identity compare — single cycle. Miss calls `NV_PTR_fn`,
  fills slot. Stable forever: GST entries are GC-malloc'd + chained, never
  moved; GVA cells are static `.data`. `gva_register` runs in the preamble,
  before any call, so cache is always filled post-bind.
- `rt_name_side_effecting(nm)`: forces `cell=NULL` for the 11 names where
  `NV_GET`/`NV_SET` have side effects beyond a plain cell access:
  7 protected-pattern names (ARB BAL REM FENCE ABORT FAIL SUCCEED) +
  TERMINAL (write→stderr) + ALPHABET/STCOUNT/STNO (computed reads).
  All other keyword/special names are already NULL-listed by `NV_PTR_fn`
  and fall back automatically.
- `rt_call_fastpath_ok()`: returns `!g_call_fastpath_off`.
- Both `rt_call_named_proc` and `rt_call_named_proc_sl` return-fetch now
  uses cached cell when non-NULL.
- Removed redundant local `NV_PTR_fn` extern from `rt_gvar_cell`.

### core.c

- `int g_call_fastpath_off = 0`: flipped permanently true at both
  I/O-association sites (`_io_chan[ch].varname` assignment with non-NULL
  `vn`) so any run that associates a variable with a channel uses the safe
  by-name path for the remainder of that run.

## Correction to rung spec (guard b)

The spec said "skip the fast path when `g_protected_pat_vars_armed`."
That flag is set **unconditionally** in `core_lib_init` (the built-in
ARB/BAL/REM/FENCE/etc. are always installed). Using it as the gate makes
the fast path dead code — confirmed by instrumentation (gate always false,
`fast=0 slow=10` on 5 calls). Correct guard: per-name `rt_name_side_effecting`
check at cache-fill time. Audited the full side-effecting name set against
`NV_GET_fn` / `NV_SET_fn` / `NV_PTR_fn` source before writing the list.

## Gate results

- `make libscrip_rt`: clean.
- `test_crosscheck_snobol4.sh`: PASS=171 FAIL=84 SKIP=6,
  fail-set `diff` vs pristine HEAD: **empty** (zero regressions).
  `082_keyword_stcount` / `fileinfo` / `triplet` exercise guards b+c live.
- Same-binary A/B (identical binary, `.so` swapped underneath):
  - `func_call` (10M calls): 17174 ms → 6582 ms  **(2.61×)**
  - `fibonacci`  (~2.7M calls):  4821 ms → 2324 ms  **(2.07×)**

## Next session

DCR-2: codegen-side resolution — replace `lea rdi,name; call rt_call_named_proc@PLT`
with a baked proc-index/cells table resolved at preamble, so the call site
drops even the `g_rt_gen_procs[]` linear-strcmp scan. See DCR-2 step in
GOAL-SNOBOL4-BB.md.
