# FINDING-2026-07-27-CLAUDE-SN4-ZB-VAL-8B-USE-2-CHOKE-POINT-AND-ASSIGN-GATE.md
# Session s183 — ZB-VAL-8b-USE-2: choke-point promotion + assign write-side gate

## THE DEFECT IN s182's PROMOTION SITE

s182 promoted `op_res_live` at the `IR_CMP_TEST`/`IR_COERCE_NUMERIC` dispatch arm (`emit.cpp:1305`).
That was safe while `bb_cmp_test` was the sole reader. The moment a second consumer exists — as this
session adds — the arm-local site becomes stale-unsafe:

`DRIVE_FILL` resets ~20 `op_*` fields (`op_zls2_bytes`, `op_fc_base`, `op_tail`, … full list in the
macro) but NOT `op_res_live`. Three macros reach templates via `walk_bb_node`:
  FILL / EMIT_PAIR_FILL (line ~581) / DRIVE_FILL (line ~1017)
None of them assign `op_res_live`. So any node dispatched via FILL or EMIT_PAIR_FILL, or any node
dispatched via DRIVE_FILL whose case arm never explicitly assigns it, would inherit the PREVIOUS
node's measured value. If that value was 0 (a dead CMP_TEST immediately before a live ASSIGN in
emission order), the live assign's template would see `_.op_res_live == 0` and skip the result store
a downstream reader needs. Wrong code, silent, intermittent by emission-order.

## THE FIX

Promote at `walk_bb_node_inner` entry — the single choke point:

```c
static int walk_bb_node_inner(IR_t * nd, FILE * out) {
    { extern int zls_result_live(const IR_t *); g_emit.op_res_live = zls_result_live(nd); }
    …
```

`zls_result_live` is conservative (unknown node → 1), so promotion here can only hand a template
the same answer the arm-local site did, or a safer one. The s182 arm-local line is deleted.
One authority, not two.

## THE ASSIGN GATE

`IR_ASSIGN` is 1,577 of 3,448 measured-dead result cells (46%) across 315 crosscheck programs
(full census from `SCRIP_SLOT_CENSUS=1` run, crosscheck corpus).

Both assign templates gated:
- `bb_assign_global.cpp`: GVA arm + NV_SET arm, two pairs each, wrapped in `IF(_.op_res_live,…)`.
- `bb_assign_local.cpp`: NUL arm + value-copy arm, two pairs each, wrapped in `IF(_.op_res_live,…)`.

The `op_sb` stores (the actual variable's frame slot) are NOT gated — those are real writes regardless
of whether the box's result cell is read. Only `FRQ(_.op_off)` / `FRQ(_.op_off+8)` are gated.

## MEASURED RESULT

5,146 instructions removed across 315 crosscheck programs. Deterministic: two full-corpus passes
produce byte-identical output (md5 `fb30ce73787cb95fadf807dd23680e49`). Crosscheck watermark held:
m3 314/1 · m4 312/1 · DIVERGE=0. Non-beauty FC gate offenders unchanged at 1,344 (pre-existing).

## FC GATE BASELINE PROBLEM (FOUND THIS SESSION)

`test_gate_fc_no_residual_rbp.sh` documents baseline 0 misses / 52 programs. The actual reading is
~5,600 ± 50. Root cause: `beauty.sno --compile` does not terminate in bounded time (>3.7M lines
before `timeout 30` kills it; the tool-call wrapper kills it even faster). The gate runs on its own
timeout, so `beauty.sno` is scored on a truncated compile that varies per run. The non-beauty stable
portion is exactly 1,344 misses and is a reliable regression signal. The headline number is not.

This explains the full session measurement history:
- "5,598 baseline", "5,526 local-only", "5,630 full-change", "5,668/5,630/5,680 on one binary"
  — all are beauty truncation noise ± the stable 1,344 non-beauty floor.
- Every non-beauty offender was byte-identical across all configurations. The FC gate is sound for
  completing programs; only the headline number is noise.

The gate needs one of: (a) exclude beauty explicitly, (b) `timeout` per-program with a FAIL on
timeout rather than a partial count. Without this fix, the gate cannot be used as a s182 prerequisite
and the documented baseline of 0 is structurally unreachable.

## NEXT RUNGS (in order)

1. Fix `test_gate_fc_no_residual_rbp.sh` — exclude beauty or detect timeout — so it is usable.
2. Diagnose `beauty.sno --compile` runaway (>3.7M lines, pathological vs corpus norm of hundreds).
3. Widen `zls_elide_ok` to `IR_CALL` (234 dead, zero locals per grep of zls_grant_locals):
   requires the same cross-box reader audit `bb_cmp_test` received in s182 — confirm no downstream
   template reads the IR_CALL result cell as a value before admitting it to S1.
4. `IR_MATCH_ASSIGN_COND` (123 dead, zero locals): same audit.
5. `ZB-VAL-8c` per-node `op_fc_wbytes`.
6. Statement-root spine entry (vfc gate still `a->op == IR_ASSIGN`).
