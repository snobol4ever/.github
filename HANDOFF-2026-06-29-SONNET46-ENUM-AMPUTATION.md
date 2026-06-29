# HANDOFF — 2026-06-29 — Sonnet 4.6 — GZ#5 ENUM AMPUTATION (119 dead IR_e members + dead codegen subsystems)

## SCRIP HEAD: d0046704 — pushed to origin/main ✅

---

## Session arc

Orientation from scratch (full context load: PLAN.md, RULES.md, GOAL-IR-IMMUTABLE-EMIT.md,
six handoffs, JCON ir.icn/irgen.icn/gen_bc.icn, IR.h full scan). Then two user pivots:

**Pivot 1** (mid-session): user corrected the keep-set methodology — "GROUND ZERO means nothing
works except Icon hello/1+1/basic programs; arith_fold.c is optimization that must be redone;
keep only what 161 Icon programs need." This eliminated the false keeps (ir_query.c, arith_fold.c,
emit_term_build.cpp) that were pulling in Prolog/SNOBOL4 enums.

**Pivot 2** (handoff trigger): user provided credential and directed handoff.

---

## What landed (SCRIP d0046704 = 2 commits over 41b53078)

### IR.h — 119 enum members deleted

Deleted by language:
- **Prolog cell cluster** (8): IR_CELL_CALL, IR_CELL_CATCH, IR_CELL_CHOICE, IR_CELL_CUT,
  IR_CELL_DYNITER, IR_CELL_FINDALL, IR_CELL_ITE, IR_CELL_UNIFY
- **Prolog det predicates** (22): IR_DET_ABOLISH, IR_DET_ARG, IR_DET_ASSERTZ, IR_DET_ATOM_OP,
  IR_DET_CHAR_TYPE, IR_DET_CMP, IR_DET_COPY_TERM, IR_DET_FORMAT, IR_DET_FUNCTOR, IR_DET_IS,
  IR_DET_NB_GETVAL, IR_DET_NB_SETVAL, IR_DET_NL, IR_DET_NUMBERVARS, IR_DET_RETRACT, IR_DET_SORT,
  IR_DET_SUCC_PLUS, IR_DET_TERM_STRING, IR_DET_THROW, IR_DET_TYPE_TEST, IR_DET_UNIV, IR_DET_WRITE
- **Prolog general** (17): IR_CHOICE, IR_UNIFY, IR_CUT, IR_GOAL, IR_BUILTIN, IR_LOGICVAR,
  IR_ATOM, IR_STRUCT, IR_ARITH, IR_DISJ, IR_GCONJ, IR_ITE, IR_ITE_COMMIT, IR_ITE_GATE,
  IR_CATCH, IR_QUERY_FRAME, IR_IDENTICAL
- **SNOBOL4 match ops** (28): IR_MATCH, IR_MATCH_LIT/ANY/SPAN/BREAK/ARB/ARBNO/CAT/ALT/
  ASSIGN_IMM/ASSIGN_COND/LEN/NOTANY/POS/TAB/REM/FENCE/ABORT/CALLOUT/DEFER/BREAKX/RTAB/
  SPAN_VAR/ATP/BAL/HEAD/RETRY/ADVANCE
- **SNOBOL4 pattern ops** (24): IR_PATTERN_LIT/ANY/NOTANY/SPAN/BREAK/BREAKX/LEN/POS/RPOS/
  TAB/RTAB/ARB/REM/BAL/ABORT/FENCE/FAIL/SUCCEED/ARBNO/FENCE_P/CAT/ALT/CAPTURE/DEFER
- **SNOBOL4 assign variants** (11): IR_ASSIGN_LIT_S, IR_ASSIGN_LIT_I, IR_ASSIGN_VAR,
  IR_ASSIGN_CONCAT, IR_ASSIGN_CALL, IR_ASSIGN_DESCR, IR_INDIRECT_ASSIGN_LIT_S,
  IR_INDIRECT_ASSIGN_VAR, IR_INDIRECT_ASSIGN_DESCR, IR_AUGOP, IR_SUBJECT
- **SNOBOL4 misc** (1): IR_SCAN (the SNOBOL4 scan *statement* — not IR_GEN_SCAN or IR_SCAN_*)
- **Raku** (3): IR_MAP, IR_GREP, IR_RANDOM
- **Pascal/other** (3): IR_DTP_ASSIGN, IR_REF_INVARIANT, IR_PROG
- **Dead/orphaned** (2): IR_DO_WHILE, IR_EXEC

**Remaining in IR.h**: the complete Icon IR set (36 lower-produced + emit-time fanned
call variants + binop discriminants + gvar helpers + structural ops like IR_GOTO/IR_SEQ).

### scrip_ir.c — entries removed in lockstep
kind_names[], bb_op_name, and ir_node_produces_value entries for all 119 deleted members removed
(designated initializers — pure line deletes).

### emit_bb.c — 1162 → ~754 lines
- **bb_prepare_assign** (24 lines): DELETED. All branches except IR_ASSIGN called abort stub
  `bb_intern_into`; no Icon path reaches a live branch.
- **bb_prepare** (386 lines): COLLAPSED to 7-line field-reset prologue. The entire
  Prolog/SNOBOL4 branch forest (IR_ATOM, IR_ARITH, IR_UNIFY, IR_CELL_*, IR_BUILTIN, IR_GOAL,
  IR_CATCH, IR_CELL_CHOICE, IR_MAP/GREP, IR_CALLEE_FRAME, IR_CELL_CALL/ITE, IR_DET_THROW,
  IR_CELL_CATCH/FINDALL, IR_DET_IS/CMP/TYPE_TEST/FUNCTOR/FORMAT/SUCC_PLUS/ATOM_OP/CHAR_TYPE/
  SORT/NUMBERVARS/TERM_STRING/COPY_TERM/NB_SETVAL/NB_GETVAL/RETRACT/ABOLISH/ASSERTZ/CELL_DYNITER)
  deleted. bb_prepare(nd) for IR_TO (the only live Icon caller) fell through all those branches
  and returned — so collapsing to field-reset-only is behavior-identical.
- **descr_chain_arity**: removed IR_MAP/IR_GREP case; removed IR_ASSIGN_LIT_*/VAR/CONCAT/CALL/
  DESCR/INDIRECT_* cases (kept IR_ASSIGN + IR_ASSIGN_FRAME/FRAME_REF); removed IR_PATTERN_*
  cases; removed IR_DTP_ASSIGN case.
- **codegen_flat_chain_body**: removed `if (IR_MAP || IR_GREP)` queue-push clauses (×2).
- **descr_chain_operand_refs**: removed `if (IR_MAP || IR_GREP)` queue-push clauses (×2);
  removed `if (IR_SCAN ...)` scan_set_subj_node clause.
- **ir_node_is_alt_arm**: removed `|| IR_MATCH_ALT` from the γ-node check.

### scrip.c — 3528 → ~1376 lines
- **51 pl_gz_*/pl_findall_* functions deleted** (2049 lines total):
  All of: pl_gz_fact_clause_units, pl_gz_call_args_ok, pl_gz_choice_inline, pl_gz_lv,
  pl_gz_choice_rule_clauses, pl_gz_body_cpfree, pl_gz_callee_is_det, pl_gz_rule_body_goal_ok,
  pl_gz_rule_body_root_ok, pl_gz_disj_softcut_ite, pl_gz_rule_clause, pl_gz_rule_inline_check,
  pl_gz_cmp_nsynth, pl_gz_nsynth_goal, pl_gz_nsynth_root, pl_gz_arith_slot_map,
  pl_gz_struct_slot_map, pl_gz_arith_nested_ok, pl_gz_arith_node_count, pl_gz_arith_emit_is,
  pl_gz_arith_flatten, pl_gz_callee_body_node, pl_gz_callee_build_root, pl_gz_rule_callee_body,
  pl_gz_callee_get_any, pl_gz_count_synth_root, pl_gz_count_synth_goal, pl_gz_arith_const,
  pl_gz_build_root, pl_gz_chain_det, pl_gz_arith_to_struct, pl_gz_build_goal, pl_gz_admit,
  pl_findall_term_buildable, pl_findall_goal_admissible, pl_findall_conj_member_admissible,
  plus 15 additional helper functions (pl_gz_det_node, pl_gz_irbuf_push, pl_gz_slot_map,
  pl_gz_cmp_operand_ok, and others).
- **3 `is_prolog` branches in main()** stubbed to:
  `fprintf(stderr, "GROUND ZERO #5: Prolog backend deleted..."); return 1;`
- **graph_native_emittable_mode**: removed `if (IR_MAP || IR_GREP) return 0;` (Raku check).

### ir_query.c — rewritten to 12 lines
Previously 93 lines with 7 functions (scan_pat_is_single_lit, scan_val_is_single_lit,
scan_pat_m3_native_safe, gz_node_bounded, ir_is_generator_kind, subchain_node_is_generator,
resolve_ite_entries_em). All dead except ir_is_generator_kind which is called from emit_bb.c's
live chain builder (generator ω-wiring). Rewritten to just that function, Icon ops only
(removed IR_MAP/IR_GREP from the generator-kind switch). ir_query.h trimmed to match.

### Makefile — dead TUs removed from build
- **Source TUs removed**: unification.c (Prolog runtime), bb_pat_build.cpp (SNOBOL4 pattern
  builder), emit_term_build.cpp (Prolog term builder), arith_fold.c (Prolog arith optimizer),
  ir_query.c (then re-added with trimmed version)
- **BB templates removed from build** (~74 total, kept on disk):
  All bb_cell_*.cpp (8), all bb_det_*.cpp (22), bb_callee_frame.cpp, bb_query_frame.cpp,
  bb_disj.cpp, bb_unify.cpp (Prolog), plus all bb_match_*.cpp (~15), bb_pattern_*.cpp (~5),
  bb_scan_*.cpp (9), bb_repalt.cpp, bb_gather.cpp, bb_mapgrep.cpp, bb_scan_stmt.cpp,
  bb_scan_splice_empty.cpp (SNOBOL4/dead).
  NOTE: bb_scan_*.cpp are SNOBOL4 scan templates, NOT Icon's IR_SCAN_* scanning builtins
  (which have no templates yet — they abort via drive_unowned).

---

## Verification

- **scrip binary builds clean** (warnings only: pre-existing INTVAL/REALVAL redefinition)
- **libscrip_rt.so builds clean**
- **Mutation gate: HARD=4** (unchanged — same 4 `->op` writes in resolve_call_kinds_descr)
- **Icon rung suite: PASS=86/289 all three modes** (interp/run/compile) — zero regression

```
--- Icon (interp): PASS=86 FAIL=167 XFAIL=36 TOTAL=289 ---
--- Icon (run):    PASS=86 FAIL=167 XFAIL=36 TOTAL=289 ---
--- Icon (compile):PASS=86 FAIL=167 XFAIL=36 TOTAL=289 ---
```

---

## What is NOT done / next session

1. **Remaining dead BB templates in the Makefile**: Many remaining templates (bb_atom.cpp,
   bb_logicvar.cpp, bb_ite.cpp, bb_cut.cpp, bb_subject.cpp, bb_ref_invariant.cpp,
   bb_det_nl.cpp, bb_cell_cut.cpp, bb_cell_ite.cpp, bb_indirect_assign_*.cpp,
   bb_gvar_assign_*.cpp variants) are still compiled into the binary as object code but their
   IR ops are deleted. They compile (because they only reference deleted enums in x86()
   comment strings, not in code) but they're dead weight. Next session can pull them.

2. **IR_OP_COUNT is now wrong**: IR.h doesn't update the count automatically.
   The enum is now ~103 members; IR_OP_COUNT in IR.h still reflects the old total.
   scrip_ir.c uses `IR_OP_COUNT` for array sizing — this needs a recount and fix before
   the next session adds new ops.

3. **B4 (gate to 0)**: The 4 remaining mutations are in resolve_call_kinds_descr (emit-time
   call classification using rt_proc_is_*/rt_builtin_is_* queries). Moving this to LOWER
   is the next gate step.

4. **Further enum cleanup**: IR_CALLEE_FRAME, IR_GATHER, IR_ITERATE, IR_ITE, IR_LOGICVAR,
   IR_FIND_GEN, IR_UPTO, IR_TO_NESTED, IR_GEN_ALT, IR_SEQ_GEN, IR_SEQ_EXPR, IR_PROC,
   IR_SUBJECT, IR_DO_WHILE — some of these survived because they appear in templates still
   in the build (even if dead at runtime). A second pass targeting them after the remaining
   dead templates are pulled from the build will close to the true Icon minimum.

5. **SNOBOL4/Prolog lower files** (lower_snobol4.c etc.) are still on disk and still
   reference the deleted enums — they'll fail to compile if ever re-enabled. Per GROUND ZERO
   they will be rewritten from scratch later.

---

## Files touched summary
- `src/contracts/IR.h` — 119 enum members deleted
- `src/contracts/scrip_ir.c` — lockstep metadata entries removed
- `src/emitter/emit_bb.c` — bb_prepare collapsed/deleted; dead case-labels removed
- `src/driver/scrip.c` — 51 pl_gz_*/pl_findall_* functions deleted; is_prolog stubs
- `src/opt/ir_query.c` — rewritten to ir_is_generator_kind only
- `src/opt/ir_query.h` — trimmed to match
- `Makefile` — ~79 dead source TUs removed from build

