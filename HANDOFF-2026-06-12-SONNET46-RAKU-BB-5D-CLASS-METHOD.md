# HANDOFF-2026-06-12-SONNET46-RAKU-BB-5D-CLASS-METHOD.md

## Goal: GOAL-RAKU-BB — RK-LOWER-5d class/method/field/new

## Session result

m2: **26/26 PASS** (was 25/25 at session start).
m3: **1 PASS / 0 FAIL / 25 EXCISED** (unchanged — clean).
m4: **1 PASS / 0 FAIL / 25 EXCISED** (unchanged — clean).
Peers: SNOBOL4 7/7 m2/m3/m4 ✓, Icon m2 12/12 ✓, NFA oracle 5/5 ✓, g_vstack=0 ✓.

SCRIP HEAD: `ef8fa7d`. .github HEAD: `d76b96e5`.

## What was done

### Root cause 1 — [SBB] FATAL for pure .raku files

`polyglot.c`'s proc-discovery loop only processes SCRIP-syntax nodes carrying
`:lang`/`:subj` attributes. Raw Raku AST nodes (`TT_SUB_DECL`, `TT_CLASS_DECL`)
are never visited. So `lower_raku_stage2` received `proc_count=0` → "main" never
in proc_table → fatal.

**Fix:** `rk_discover_procs(prog)` in `lower_raku.c` — walks the raw Raku AST
directly, calls `stage2_proc_grow` for each top-level `TT_SUB_DECL` and for each
method inside `TT_CLASS_DECL` (as `ClassName__methodname`). Called from
`lower_raku_stage2` before the build loop.

### Root cause 2 — class types never registered

`DEFDAT_fn`/`dat_register` only fire via `IR_RECORD_DEF` during graph execution,
which the driver never ran for class declarations (they live in the top-level
`lower_raku()` IR_PROG graph, not in any proc graph).

**Fix:** `rk_register_classes(prog)` in `lower_raku.c` — walks the raw AST,
calls `record_register("ClassName(f1,f2,...)")` for each `TT_CLASS_DECL` at
stage2 time, before any proc is built.

### Root cause 3 — wrong cname source

`TT_CLASS_DECL.v.sval` is empty. Class name is in `c[0]->v.sval` (a `TT_VAR`
leaf pushed first by the parser). Fixed in `lower_decl`, `rk_register_classes`,
`rk_discover_procs`.

### Root cause 4 — meth_call used proc_table_call (SM-only path)

`proc_table_call` only handles SM-mode procs (`entry_pc >= 0`). IR-mode procs
have `entry_pc = -1` → always returns FAILDESCR.

**Fix:** `rk_ir_call_proc(pi, args, nargs)` added at end of `IR_interp.c` —
replicates the dval==2.0 IR-graph proc-call path (NV param binding via `lower_sc`,
frame push/pop, `bb_snapshot_state`/`bb_restore_state`, `FRAME.returning` check).
`meth_call` handler in `by_name_dispatch.c` now checks `bb_idx >= 0` and calls
`rk_ir_call_proc` instead of `proc_table_call`.

### Root cause 5 — TT_RETURN absent from lower_rv

Method bodies go through `lower_raku_proc`'s reverse loop which calls `lower_rv`.
`lower_rv` had no `TT_RETURN` case → hit default (IR_SUCCEED) → body silently
discarded.

**Fix:** `TT_RETURN` case added to `lower_rv`: builds `IR_RETURN`, lowers the
return-value expression as operand, chains correctly.

### Additional fixes in lower_raku.c

- `lower_decl(TT_CLASS_DECL)`: builds `"ClassName(f1,f2,...)"` spec from `c[0]->v.sval`
  (name) and `c[1..]` (fields, skipping `TT_SUB_DECL`). No longer pushes method
  children as IR operands.
- `lower()` and `lower_rv()`: `TT_METHCALL` → `IR_CALL("meth_call")`;
  `TT_NEW` → `IR_CALL("obj_new")`.
- `lower()` and `lower_rv()`: `TT_TWIGIL_FIELD` (`$!x`) → `IR_FIELD_GET` with
  `IR_VAR("self")` operand (method `self` bound as slot-0 param in `lower_sc`).
- `lower_rv()`: `TT_FIELD` (`$obj.field`) → `IR_FIELD_GET` with lowered object operand.
- `lower_raku_stage2`: method procs detected via `strchr(pname,'_')[1]=='_'`; `self`
  inserted as slot-0 in `lower_sc` before explicit params.
- `test_smoke_raku.sh`: `class_method` rung added (26th test).

## Files touched

- `src/lower/lower_raku.c` — rk_register_classes, rk_discover_procs, lower_decl,
  lower(), lower_rv(), lower_raku_stage2
- `src/interp/IR_interp.c` — rk_ir_call_proc() helper at end of file
- `src/runtime/by_name_dispatch.c` — meth_call handler uses rk_ir_call_proc
- `scripts/test_smoke_raku.sh` — class_method rung

## Next session start checklist

1. Read `GOAL-RAKU-BB.md` (live state) and `RULES.md` in full.
2. Build: `bash scripts/build_scrip.sh && make libscrip_rt` (rc=0).
3. Confirm gate: `bash scripts/test_smoke_raku.sh` → 26/26 m2 PASS.
4. Run peer gates: `test_smoke_snobol4.sh`, `test_smoke_icon.sh`,
   `test_gate_raku_nfa_oracle.sh`.
5. **NEXT rung:** say(jct)/say(list) composite output polish, then
   RK-EMIT-MAP/GREP (blocked on Icon GZ-7 — IR_ASSIGN ζ-slot store).
   The lockstep "three→four" FACT-RULE roster expansion still deferred.

## Authors

Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
