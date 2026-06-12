# HANDOFF-2026-06-12-SONNET46-RAKU-BB-BLOCKER-ANALYSIS.md

## Goal: GOAL-RAKU-BB — investigate next EXCISED targets (bool_truthiness, bool_compare_store, class_method)

## Session result

m2: **31/31 PASS** (unchanged).
m3: **6 PASS / 0 FAIL / 25 EXCISED** (unchanged — no regression, no new PASS).
m4: **6 PASS / 0 FAIL / 25 EXCISED** (unchanged).
Peers: SNOBOL4 7/7 ✓, Icon m2 12/12 ✓, NFA oracle 5/5 ✓, g_vstack=0 ✓.

SCRIP HEAD: `b5df67a` (unchanged — no new commit). .github HEAD: this commit.

## What was analyzed

### bool_truthiness / bool_compare_store — `__rk_bool(dval=2.0)` blocker

Both programs are EXCISED because they contain `CALL(__rk_bool, dval=2.0)` nodes.
The emittable gate (`icn_graph_native_emittable_mode`) blocks all `IR_CALL` with `dval==2.0`.

The `dval==2.0` form of `__rk_bool` is produced by:
- `TT_IF` → `__rk_bool(dval=2.0)` where `IR_EXEC(bk).counter` = `IR_graph_t**[1]` holding the condition sub-graph
- `TT_ASSIGN` + relop rhs → same shape with `γ→LIT_I(1)`, `ω→LIT_I(0)`

The condition sub-graph in `IR_EXEC(bk).counter` must be evaluated at runtime. In mode-2 this is
done via `IR_interp_once(ab)`. In native mode this requires either sub-graph inlining (complex)
or a pre-emission sub-graph flatten step.

**Simplest native path** (next session target):
Detect in `bb_call.cpp` when `__rk_bool(dval=2.0)` has a `cblk` whose entry is a single
BINOP-relop node. In that case, inline the cmp+branch directly:
1. Gate: whitelist `__rk_bool(dval=2.0)` when `cblk->entry->op == IR_BINOP && is_relop`.
2. `bb_call.cpp`: add arm before the `dval==2.0` bomb — detect fn=="__rk_bool" && dval==2.0,
   fetch `blks[0]` (cblk), if entry is BINOP-relop, emit inline `mov/cmp/j<cond>` using the
   relop's operand slots. This is a single-level inline (no recursion).

For `if(True)` / `if(False)` (literal bool): `cblk->entry` is a VAR/LIT_S "True"/"False" —
detect and emit unconditional `jmp γ` / `jmp ω`.

For `if($x)` (variable truthiness): `cblk->entry` is an IR_VAR — emit load + `rt_rk_is_truthy`.

### class_method — `obj_new`/`meth_call`/`FIELD_GET` blocker

`class_method` is EXCISED for two reasons:
1. `ASSIGN($p)` has γ-predecessor `CALL(obj_new, dval=0.0)`. `icn_local_assign_rhs_ok_g` calls
   `icn_rhs_kind_ok(IR_CALL)` → returns 0 (CALL not in accepted set). Gate rejects.
2. No native templates for `obj_new`, `meth_call`, `FIELD_GET`.

**To unblock class_method:**
- Extend `icn_rhs_kind_ok` to accept `IR_CALL` with `dval==0.0` (non-sub-graph calls).
- Add `bb_call_obj_new.cpp` — emits call to `rt_rk_obj_new` runtime, stores result to ζ-frame slot.
- Add `bb_call_meth_call.cpp` — dispatches to method by name+receiver.
- Add `bb_field_get.cpp` — reads field from object record.
Not attempted this session; multi-template work for a future session.

## Files touched

None (analysis only; scrip.c debug probe was reverted; no net change).

## Next session start checklist

1. Read GOAL-RAKU-BB.md and RULES.md.
2. Build: `make -j4 scrip && make libscrip_rt` (rc=0).
3. Confirm gate: `bash scripts/test_smoke_raku.sh` → m2 31/31, m3/m4 6 PASS / 0 FAIL / 25 EXCISED.
4. Target `bool_truthiness` first: implement the `__rk_bool(dval=2.0)` simple-cblk inline path.
   - Gate: in `icn_graph_native_emittable_mode`, whitelist `IR_CALL dval==2.0` when fn=="__rk_bool".
   - `bb_call.cpp`: before the `dval==2.0` bomb, add arm for `fn=="__rk_bool" && dval==2.0`;
     inspect `cblk->entry->op`: if BINOP-relop → emit inline cmp+branch (reuse `relop_fail_mnem`);
     if IR_VAR → emit load + `rt_rk_is_truthy`; if literal True/False → unconditional jmp.
   - Run gate: target `bool_truthiness` m3/m4 PASS.
5. Then target `bool_compare_store` (same infrastructure, relop-to-1/0 assign path).

## Authors

Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
