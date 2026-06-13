# HANDOFF-2026-06-13-OPUS48-PASCAL-BB-NESTED-FRAME-SL-HOPS.md

## Session summary
Goal: GOAL-PASCAL-BB.md — bring M3/M4 to parity with M2 (103/0).

## Gate state
- Entering: M2 103/0 XFAIL=1 · M3 91/12 XFAIL=1
- Leaving:  M2 103/0 XFAIL=1 · M3 97/6  XFAIL=1  (+6)

## What landed (SCRIP commit cba8a04)
Nested-procedure static-link addressing. Three coordinated changes:

1. **`lower_pascal.c` `lower_var` / `lower_assign_var`** — compute static-link
   hop count = number of scope-chain steps from `cx->sc` to the scope that
   actually declares the name (`found_sc`), and store it in `IR_LIT(nd).dval`
   for IR_VAR_FRAME, IR_VAR_FRAME_REF, IR_ASSIGN_FRAME, IR_ASSIGN_FRAME_REF.
   The BB templates (bb_var_frame.cpp, bb_var_frame_ref.cpp, bb_assign_frame*.cpp)
   already walk the SL chain with `FOR(0,(int)_.op_dval,...) { mov rax,[rax+0] }`,
   but dval was never set by the lowerer (always 0.0), so every nested procedure
   dereferenced its own frame. Setting dval makes outer-scope reads/writes follow
   the correct number of SL hops.

2. **`lower_pascal.c` `lower_pascal_stage2`** — added `lower_pascal_enum(prog, NULL, 0)`
   at function entry. CRITICAL discovery: in the M3/M4 path, `sm_preamble` →
   `polyglot_init` → `lower_pascal_stage2` is what lowers each proc body. But
   `lower_pascal()` (which is the only other caller of `lower_pascal_enum`) is
   NOT called in --run/--compile. So `g_pas_proc_list` and the parent-pointer
   array were empty when `lower_pascal_proc` → `build_scope_chain` ran, meaning
   every nested proc's `cx->sc.outer` was NULL → variables resolved as gvars and
   emitted `NV_GET_fn`/`rt_gvar_assign_int` instead of frame refs. Calling
   `lower_pascal_enum` first populates the list so `build_scope_chain` links
   inner→outer correctly.

3. **`emit_bb.c` `bb_prepare`** — for IR_ASSIGN_FRAME / IR_ASSIGN_FRAME_REF whose
   RHS is IR_VAR_FRAME (bb_lk==5) or IR_VAR_FRAME_REF (bb_lk==6), copy the RHS
   node's `dval`/`ival` into `op_a_dval`/`op_a_ival_sg` so the lk=5/6 arms of
   bb_assign_frame(_ref) address the correct outer frame for frame→frame copies.

Fixes: nestvar, nestvar2, nestvar3, nestfunc, nestrec, nestshadow.

## IMPORTANT learnings / landmines
- **Pascal procs are FLATTENED to top level by the parser.** Nested `procedure inner`
  appears as a SIBLING of `outer` in the program body, not inside `outer`'s c[2]
  body. `decl_level` (stored in the locals VLIST `v.ival`) encodes nesting depth.
  `assign_parents()` uses level arithmetic to link each proc to its parent — this
  is the source of truth. DO NOT add recursion to `collect_procs` and DO NOT turn
  `assign_parents` into a no-op (I tried both; they break parent assignment — all
  parents come back NULL because the procs really are flat siblings).
- A red herring this session: I briefly added `pas_scan_nested_procs` to polyglot.c
  to recurse into proc bodies. Unnecessary (procs already top-level) and reverted
  fully — polyglot.c has ZERO net change. Confirm with `git diff src/driver/polyglot.c`.

## Remaining 6 failures (root causes in GOAL-PASCAL-BB.md)
varframe, arr2dtype, arr2dtype3, boolidx, alphacmp, forward1.
Priority order and per-test analysis are in the goal file's REMAINING section.

## What to read next session
- GOAL-PASCAL-BB.md (live state), RULES.md
- varframe: `marshal_varparam_addr` (IR_VAR arm) in bb_call.cpp; `use_frame` in lower_var
- arr2dtype: `marshal_arith_rax` / `arith_opnd_a/b` CALL-operand arms in bb_call.cpp
- boolidx: `marshal_call_arg` boolean-relop arm vs arr_set_pure value arg

## Watermark
Session 48 (2026-06-13, Opus 4.8). M3: 91→97 (+6). 6 remaining.
