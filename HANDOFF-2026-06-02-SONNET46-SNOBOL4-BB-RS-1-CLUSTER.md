# HANDOFF — RS-1 CLUSTER: Runtime Symbol Inventory + Partition Map

**Date:** 2026-06-02  
**Session:** Sonnet 4.6  
**Goal:** GOAL-SNOBOL4-BB.md — RS-1 (first `- [ ]` step of RUNTIME SUBSYSTEM REORG)  
**Commit:** N/A (analysis only — no code moves per RS-1 METHOD)  
**Gates:** All green at HEAD `85677cb` (m2 SNOBOL4 7/7 HARD, Icon 12/12 HARD, Prolog 5/5 HARD, prove_lower2 67, no_bb_bin_t 0, concurrency OK)

---

## RS-1 Method

Full inventory of every function/global/type **DEFINED** in `src/runtime/**` (the three subdirectory groups: `core/`, `rt/`, `builtins/`). For each symbol: current file, CS capability it serves, which languages call it. Cluster by capability, ignoring source-language origin. Produce the `subsystem → {symbols}` and `subsystem → new filename` partition map.

**Definition-location is authoritative.** Parser/driver-defined symbols that are merely *called* in runtime are NOT runtime's to move (e.g. `prolog_atom_*`, `raku_nfa_*`, `pl_write*` are parser-DEFINED → held).

---

## Current File Inventory (src/runtime/**)

### src/runtime/rt/rt.c + rt.h  (1415 lines, 157 functions)
The "grab-bag" — contains arith, WAM trail/unify, pattern-vstack helpers, proc-frame arena, output, capture, generator scaffolding, call marshalling.

### src/runtime/rt/rt_protected.c + rt_protected.h  (tiny)
`is_protected_pat_name`, `protected_pat_name_to_sm_op` — SNOBOL pattern-name protection layer.

### src/runtime/core/core.c + core.h  (3449 lines, 238 functions)
The SNOBOL execution model: name/variable system (NV_*), arithmetic (+/-/*/÷), string operations, array/table, I/O, data constructors, function registration (DEFINE/APPLY), SNOBOL pattern-primitive wrappers (_PAT_*), monitor/trace.

### src/runtime/core/pattern.c  (776 lines, 46 functions)
Pattern builder: `pat_lit`, `pat_span`, `pat_any`, `pat_alt`, `pat_cat`, `pat_assign_*`, `var_as_pattern`, `pat_at_cursor`, etc. The `PATND_t`-building layer (being retired → byrd-boxes).

### src/runtime/core/eval_code.c  (468 lines, 6 functions)
`eval_expr`, `code`, `CODE_fn` — runtime EVAL/CODE execution (parse SNOBOL source at runtime).

### src/runtime/core/eval_pat.c  (182 lines, 2 functions)
`interp_eval_pat`, `NAME_DEREF` — evaluate a pattern expression (mode-2 pattern executor helper).

### src/runtime/core/stmt_exec.c  (428 lines, 15 functions)
`exec_stmt` / `patnd_*` helpers — SNOBOL statement execution (the mode-2 PATND→byrd-box translator layer, slated for retirement). Also contains the legacy cursor globals (`Σlen`, `Δ`, `Ω`, `cursor`) that belong to the subject/scan model.

### src/runtime/core/name_t.c + name_t.h  (136 lines, 3 functions)
`name_commit_value`, `name_init_as_var`, `name_init_as_ptr` — the `NAME_t` lvalue descriptor (variable, pointer, indexed, or call-site lvalue).

### src/runtime/core/name_save.c  (126 lines, 6 functions)
`NAME_ctx_enter`, `NAME_ctx_leave`, `NAME_pop`, `NAME_commit` — name-binding context save/restore (SNOBOL function call frame name save).

### src/runtime/core/argval.c  (4 functions)
`VARVAL_d_fn`, `INTVAL_fn`, `PATVAL_fn`, `VARVUP_fn` — argument coercion helpers.

### src/runtime/core/coerce.c  (2 functions)
`descr_to_str`, `shared_arith` — DESCR coercion (to string, to numeric).

### src/runtime/core/invoke.c  (2 functions)
`INVOKE_fn`, `ARGVAL_fn` — general function invocation and argument access.

### src/runtime/builtins/gen_runtime.c + gen.h + gen_runtime.h  (2026 lines, 32 functions)
Icon/generator runtime: frame stack (`GenFrame`), generator state, proc-table call (`sm_call_proc`, `proc_table_call`), scope management (`scope_add/get/patch`), string ops (`str_concat_d`, `lconcat_d`), cset algebra (`cset_union/diff/inter/complement/canonical`), keyword system (`kw_assign`, `kw_read`), `try_call_builtin_by_name`, `rt_call_arr`, `rt_jct_relop`.

### src/runtime/builtins/resolve_runtime.c + resolve_runtime.h  (2047 lines, 32 functions)
Prolog WAM resolver: choice-point stack, trail, environment, predicate table, assert/retract/abolish, `rt_unify_terms`, `rt_trail_*`, `rt_compound_build_n`, `rt_node_to_term`, ISO error throwing, `interp_exec_builtin`, `resolve_call_term`, `rt_catch`/`rt_throw`/`rt_findall`, `rt_sort_msort`, `rt_copy_term`, `rt_atom_*`, `rt_char_type`, `rt_numbervars_term`.

### src/runtime/builtins/scan_builtins.c + scan_builtins.h  (194 lines, 3 functions)
`cset_resolve`, `cset_has`, `scan_try_call_builtin` — Icon string scanning + cset resolution.

### src/runtime/builtins/script_builtins.c + script_builtins.h  (528 lines, 1 function)
`script_try_call_builtin` — Raku/script by-name builtin dispatch entry.

### src/runtime/builtins/script_builtins_byname.c  (1042 lines, 11 functions)
Raku junction/grammar builtins: `elem_to_descr`, `junction_is`, `junction_collapse`, `gram_set/get/expand`, `script_try_call_builtin_by_name`, `script_try_hash_mutating_builtin`, `script_try_hash_builtin`.

---

## CLUSTER MAP (CS Capability → Symbols)

The following partition reorganizes `src/runtime/**` so each FILE is a CS SUBSYSTEM, not a language. Languages contributed ideas; SCRIP uses all ideas together.

---

### SUBSYSTEM 1: `values.c` / `values.h`
**CS concept:** Value representation, type coercion, DESCR operations.  
**Current sources:** `core/coerce.c`, `core/argval.c`, parts of `core/core.c`

| Symbol | Current File | Notes |
|--------|-------------|-------|
| `descr_to_str` | coerce.c | DESCR→string coercion |
| `shared_arith` | coerce.c | Shared numeric coercion |
| `VARVAL_d_fn` | argval.c | Var-value coercion |
| `INTVAL_fn` | argval.c | Integer coercion |
| `PATVAL_fn` | argval.c | Pattern coercion |
| `VARVUP_fn` | argval.c | Var-up coercion |
| `coerce_numeric` | core.c | Numeric coercion |
| `to_int` | core.c | String→int |
| `to_real` | core.c | String→real |
| `size_value` | rt.h | Size of value |
| `rt_size_d` | rt.c | DESCR size |
| `descr_identical` | gen_runtime.c | DESCR identity test |

**New file:** `src/runtime/values.c` + `src/runtime/values.h`

---

### SUBSYSTEM 2: `name_binding.c` / `name_binding.h`
**CS concept:** Variable name binding, lvalue model, name save/restore.  
**Current sources:** `core/name_t.c`, `core/name_save.c`, `core/core.c` (NV_* functions)

| Symbol | Current File | Notes |
|--------|-------------|-------|
| `name_commit_value` | name_t.c | Commit value to NAME_t lvalue |
| `name_init_as_var` | name_t.c | Init NAME_t as named variable |
| `name_init_as_ptr` | name_t.c | Init NAME_t as pointer |
| `NAME_ctx_enter` | name_save.c | Enter name-binding context |
| `NAME_ctx_leave` | name_save.c | Leave context |
| `NAME_pop` | name_save.c | Pop saved name |
| `NAME_commit` | name_save.c | Commit name binding |
| `same_var_target` | name_save.c | Check same variable |
| `ctx_ensure_capacity` | name_save.c | Capacity helper |
| `NV_GET_fn` | core.c | Name→value lookup |
| `NV_SET_fn` | core.c | Name→value assignment |
| `NV_CLEAR_fn` | core.c | Clear a name |
| `NV_REG_fn` | core.c | Register a name |
| `NV_SYNC_fn` | core.c | Sync names |
| `nv_reset` | core.c | Reset name table |
| `nv_snapshot` | core.c | Snapshot name table |
| `nv_restore` | core.c | Restore name table |
| `_var_init` | core.c | Init variable hash |
| `_var_hash` | core.c | Variable hash fn |
| `var_dump` | core.c | Debug: dump variables |
| `INDR_GET_fn` | core.c | Indirect reference get |
| `INDR_SET_fn` | core.c | Indirect reference set |
| `NAME_fn` | core.c | &name expression |
| `ASGNIC_fn` | core.c | Assign-not-in-class |
| `rt_nv_get` | rt.c | Runtime NV get (mode-3 path) |
| `rt_nv_set` | rt.c | Runtime NV set (mode-3 path) |
| `rt_gvar_assign_str` | rt.c | Assign string to global var |
| `rt_gvar_assign_int` | rt.c | Assign int to global var |
| `rt_gvar_assign_var` | rt.c | Var→var assignment |
| `is_global` | gen_runtime.c | Is name global? |
| `global_register` | gen_runtime.c | Register global name |
| `frame_lookup` | gen_runtime.c | Frame-local lookup |
| `frame_lookup_sv` | gen_runtime.c | Frame-local lookup with sval |
| `scope_add` | gen_runtime.c | Add to scope |
| `scope_get` | gen_runtime.c | Scope lookup |
| `scope_patch` | gen_runtime.c | Patch scope entry |
| `g_root_ctx` | name_save.c | Root name-binding context (global) |

**New file:** `src/runtime/name_binding.c` + `src/runtime/name_binding.h`

---

### SUBSYSTEM 3: `string_ops.c` / `string_ops.h`
**CS concept:** String operations: concat, substr, length, case, padding, search.  
**Current sources:** `core/core.c` (string builtins), `rt/rt.c` (rt_concat), `builtins/gen_runtime.c` (str_concat_d)

| Symbol | Current File | Notes |
|--------|-------------|-------|
| `CONCAT_fn` | core.c | String concatenation |
| `SIZE_fn` | core.c | String size |
| `DUPL_fn` | core.c | String duplicate |
| `REPLACE_fn` | core.c | String replace |
| `SUBSTR_fn` | core.c | Substring |
| `TRIM_fn` | core.c | Trim whitespace |
| `lpad_fn` | core.c | Left-pad |
| `rpad_fn` | core.c | Right-pad |
| `REVERS_fn` | core.c | Reverse |
| `BCHAR_fn` | core.c | Character from code |
| `INTGER_fn` | core.c | Integer from string |
| `real_fn` | core.c | Real from string |
| `string_fn` | core.c | To string |
| `_LCASE_` | core.c | Lowercase |
| `_UCASE__fn` | core.c | Uppercase |
| `_SUBSTR_` | core.c | Substring builtin |
| `_REPLACE_` | core.c | Replace builtin |
| `_TRIM_` | core.c | Trim builtin |
| `_LPAD_` | core.c | Lpad builtin |
| `_RPAD_` | core.c | Rpad builtin |
| `_REVERSE_` | core.c | Reverse builtin |
| `_CHAR_` | core.c | Char builtin |
| `_DUPL_` | core.c | Dupl builtin |
| `_SIZE_` | core.c | Size builtin |
| `rt_concat` | rt.c | Runtime concat (mode-3) |
| `rt_gen_concat` | rt.c | Generator concat |
| `str_concat_d` | gen_runtime.c | DESCR-based concat |
| `lconcat_d` | gen_runtime.c | Left-concat DESCR |
| `string_section_assign` | gen_runtime.c | String section assignment |
| `size` | core.c | Size utility |

**New file:** `src/runtime/string_ops.c` + `src/runtime/string_ops.h`

---

### SUBSYSTEM 4: `arithmetic.c` / `arithmetic.h`
**CS concept:** Numeric arithmetic, comparison, coercion.  
**Current sources:** `core/core.c` (add/sub/mul/div/comparison), `rt/rt.c` (rt_arith, rt_acomp, rt_lcomp, rt_unop_*)

| Symbol | Current File | Notes |
|--------|-------------|-------|
| `add` | core.c | DESCR addition |
| `sub` | core.c | DESCR subtraction |
| `mul` | core.c | DESCR multiplication |
| `DIVIDE_fn` | core.c | DESCR division |
| `POWER_fn` | core.c | DESCR exponentiation |
| `neg` | core.c | Negate |
| `pos` | core.c | Positive |
| `eq` `ne` `lt` `le` `gt` `ge` | core.c | Numeric comparison |
| `ident` `differ` | core.c | Identity/differ |
| `_GT_` `_LT_` `_GE_` `_LE_` `_EQ_` `_NE_` | core.c | Arithmetic comparison builtins |
| `_b_add` `_b_sub` `_b_mul` `_b_div` `_b_pow` `_b_neg` `_b_pos` | core.c | SNOBOL arith helpers |
| `_INTEGER_` `_REAL_` `_NUMERIC_` | core.c | Type predicates |
| `_REMDR_` | core.c | Remainder |
| `_IDENT_` `_DIFFER_` `_VDIFFER_` | core.c | Identity predicates |
| `is_numeric_like` | core.c | Numeric test |
| `rt_arith` | rt.c | Runtime arithmetic (WAM-style) |
| `rt_acomp` | rt.c | Arithmetic comparison |
| `rt_lcomp` | rt.c | Lexicographic comparison |
| `rt_exp` | rt.c | Exponentiation |
| `rt_neg` | rt.c | Negation |
| `rt_unop_neg` `rt_unop_pos` `rt_unop_nonnull` `rt_unop_null_test` `rt_unop_not` `rt_unop_size` | rt.c | Unary ops |
| `rt_incr` `rt_decr` | rt.c | Increment/decrement |
| `rt_coerce_num` | rt.c | Coerce to numeric |
| `rt_is` `rt_is_eval` | rt.c | Prolog IS evaluation |
| `rt_arith_cmp` | rt.c | Arithmetic comparison |
| `shared_arith` | coerce.c | Shared arith (move here) |
| `resolve_unified_eval_arith` | resolve_runtime.c | Prolog unified arith eval |
| `_LGT_` `_LLT_` `_LGE_` `_LLE_` `_LEQ_` `_LNE_` | core.c | Lexicographic comparison builtins |

**New file:** `src/runtime/arithmetic.c` + `src/runtime/arithmetic.h`

---

### SUBSYSTEM 5: `backtrack.c` / `backtrack.h`
**CS concept:** Backtracking engine — choice points, goal-directed evaluation, generators, cut.  
**Current sources:** `builtins/resolve_runtime.c` (Prolog choice-points/trail), `builtins/gen_runtime.c` (Icon generator state), `rt/rt.c` (rt_trail_*, rt_choice_cut_*)

This is Lon's highest-value unification: Prolog backtracking / Icon goal-direction / Raku junctions are ONE backtracking engine.

| Symbol | Current File | Notes |
|--------|-------------|-------|
| `g_resolve_trail` | resolve_runtime.c | WAM trail |
| `g_resolve_bfr` | resolve_runtime.c | Backtrack frame register (choice-point stack) |
| `g_resolve_cp_stamp` | resolve_runtime.c | Choice-point stamp |
| `g_resolve_cut_flag` | resolve_runtime.c | Cut flag |
| `g_resolve_cut_barrier` | resolve_runtime.c | Cut barrier |
| `resolve_cp_pop` | resolve_runtime.c | Pop choice point |
| `resolve_cp_truncate` | resolve_runtime.c | Truncate to barrier |
| `rt_trail_mark` | rt.c | Mark trail position |
| `rt_trail_unwind` | rt.c | Unwind trail to mark |
| `rt_trail_mark_push` | rt.c | Push trail mark |
| `rt_trail_unwind_top` | rt.c | Unwind to top mark |
| `rt_trail_mark_pop` | rt.c | Pop trail mark |
| `rt_choice_cut_enter` | rt.c | Enter cut scope |
| `rt_choice_cut_exit` | rt.c | Exit cut scope |
| `rt_choice_cut_unwind` | rt.c | Unwind cut |
| `rt_get_cut_flag` | rt.c | Get cut flag |
| `rt_cut_set` | rt.c | Set cut |
| `g_resolve_active` | resolve_runtime.c | Resolver active flag |
| `g_sm_dispatch_active` | gen_runtime.c | SM dispatch active flag |
| `g_ast_pump_active` | gen_runtime.c | AST pump active flag |
| `g_last_ok` | rt.c | Last goal success flag (Prolog) |
| `rt_last_ok` `rt_set_last_ok` | rt.c | Get/set last-ok |
| `sm_yield_to_caller` | gen_runtime.c | Generator yield |
| `is_suspendable` | gen_runtime.c | Generator suspendable test |
| `gen_bb_pump_proc_by_name` | gen_runtime.c | Generator BB pump |
| `frame_env_active` | gen_runtime.c | Frame env active |
| `frame_env_load` | gen_runtime.c | Load frame env |
| `frame_env_store` | gen_runtime.c | Store frame env |
| `static_proc_entry_pc` | gen_runtime.c | Static proc entry |
| `static_get` `static_set` | gen_runtime.c | Static var access |
| `sm_call_proc` `proc_table_call` | gen_runtime.c | Proc-table call |
| `rt_init_arbno` | rt.c | Init ARBNO generator |
| `rt_init_cap` `rt_init_cap_call` | rt.c | Init capture |
| `rt_register_cap` | rt.c | Register capture |
| `rt_cap_assign` `rt_cap_assign_cursor` | rt.c | Capture assignment |
| `rt_defer_match` | rt.c | Deferred match |
| `rt_dcap_record` `rt_dcap_flush` `rt_dcap_clear` | rt.c | Deferred capture management |
| `rt_at_cursor` | rt.c | @var cursor capture |
| `g_rt_dcap_n` `g_rt_dcap_active` `g_rt_cap_count` `g_rt_gen_proc_count` | rt.c | Generator state globals |

**New file:** `src/runtime/backtrack.c` + `src/runtime/backtrack.h`

---

### SUBSYSTEM 6: `unification.c` / `unification.h`
**CS concept:** WAM term unification, term building, substitution.  
**Current sources:** `builtins/resolve_runtime.c` (rt_unify_*, environment), `rt/rt.c` (rt_unify_terms, rt_unify_const)

| Symbol | Current File | Notes |
|--------|-------------|-------|
| `rt_unify_terms` | rt.c | Unify two terms |
| `rt_unify_const` | rt.c | Unify with constant |
| `rt_compound_build_n` | rt.c | Build compound term |
| `rt_node_to_term` | rt.c (via resolve) | Node to term |
| `rt_copy_term` `rt_copy_term_term` `rt_copy_term_terms` | rt.c | Copy term |
| `resolve_unified_term_from_expr` | resolve_runtime.c | Unify term from expr |
| `resolve_env_new` | resolve_runtime.c | New WAM environment |
| `rt_env_alloc` | rt.c | Allocate WAM environment |
| `rt_cp_save_caller_env` | rt.c | Save caller env |
| `g_resolve_env` | resolve_runtime.c | Current WAM environment |
| `resolve_bb_env_push` | resolve_runtime.c | Push BB environment |
| `resolve_bb_env_pop` | resolve_runtime.c | Pop BB environment |
| `resolve_bb_bind_arg` | resolve_runtime.c | Bind BB argument |
| `resolve_nb_setval` | resolve_runtime.c | Non-backtrackable setval |
| `rt_nb_setval_term` `rt_nb_getval_term` | rt.c | Prolog nb_setval/nb_getval |
| `g_resolve_nb_count` | resolve_runtime.c | NB count |
| `rt_term_cmp` `rt_term_cmp_terms` | rt.c | Term comparison |

**New file:** `src/runtime/unification.c` + `src/runtime/unification.h`

---

### SUBSYSTEM 7: `pattern_match.c` / `pattern_match.h`
**CS concept:** String pattern matching and scanning — SNOBOL patterns, Icon scanning, the shared search model.  
**Current sources:** `core/pattern.c`, `core/eval_pat.c`, `core/stmt_exec.c` (patnd helpers), `rt/rt.c` (rt_pat_*), `rt/rt_protected.c`, `builtins/scan_builtins.c`

| Symbol | Current File | Notes |
|--------|-------------|-------|
| `pat_lit` `pat_span` `pat_break_` `pat_any_cs` `pat_notany` `pat_len` `pat_pos` `pat_rpos` `pat_tab` `pat_rtab` `pat_arb` `pat_arbno` `pat_rem` `pat_fence_p` `pat_fence` `pat_fail` `pat_abort` `pat_succeed` `pat_bal` `pat_epsilon` `pat_cat` `pat_alt` | pattern.c | Pattern node builders |
| `pat_ref` `pat_assign_imm` `pat_assign_cond` `pat_assign_callcap` `pat_user_call` `pat_at_cursor` `var_as_pattern` | pattern.c | Pattern combinators/captures |
| `patnd_set_children` `patnd_append_child` `spat_val` | pattern.c | PATND construction |
| `patnd_print_r` `patnd_print` | pattern.c | Debug pattern print |
| `NAME_DEREF` | eval_pat.c | Name deref for pattern |
| `interp_eval_pat` | eval_pat.c | Evaluate pattern (mode-2) |
| `patnd_contains_arbno` `patnd_contains_defer` `patnd_is_simple_atom` `patnd_is_capture_wrapped_safe` `patnd_tree_eligible` `patnd_is_combinator_root` `patnd_needs_xlate` `patnd_is_pure_altcat_leaf` `patnd_is_pure_altcat` | stmt_exec.c | PATND classification helpers |
| `is_protected_pat_name` `protected_pat_name_to_sm_op` | rt_protected.c | Protected pattern name guard |
| `rt_exec_stmt_pat` | rt.c | Execute pattern statement |
| `rt_match_lit` `rt_match_variant` | rt.c | Pattern matching |
| `rt_pat_lit` `rt_pat_refname` `rt_pat_span` `rt_pat_break` `rt_pat_breakx` `rt_pat_any` `rt_pat_notany` `rt_pat_len` `rt_pat_pos` `rt_pat_rpos` `rt_pat_tab` `rt_pat_rtab` `rt_pat_arb` `rt_pat_rem` `rt_pat_fence` `rt_pat_fence1` `rt_pat_fail` `rt_pat_abort` `rt_pat_succeed` `rt_pat_bal` `rt_pat_eps` `rt_pat_arbno` `rt_pat_cat` `rt_pat_alt` `rt_pat_deref` `rt_pat_capture` `rt_pat_capture_fn` `rt_pat_capture_fn_args` `rt_pat_usercall` `rt_pat_usercall_args` | rt.c | Pattern runtime ops (mode-3 bridge) |
| `rt_dcap_record` `rt_dcap_flush` `rt_dcap_clear` `rt_cap_assign` `rt_cap_assign_cursor` `rt_at_cursor` `rt_defer_match` | rt.c | Capture/deferred match |
| `scan_try_call_builtin` `cset_resolve` `cset_has` | scan_builtins.c | Icon scanning |
| `cset_union` `cset_diff` `cset_inter` `cset_complement` `cset_canonical` | gen_runtime.c | Charset algebra (moved to cs_canonical in LI-4) |
| `rt_subject_load` | rt.c | Load subject string |
| `g_subject_dbg_len` | rt.c | Debug subject length |
| `_PAT_SPAN_` `_PAT_BREAK_` `_PAT_BREAKX_` `_PAT_ANY_` `_PAT_NOTANY_` `_PAT_LEN_` `_PAT_POS_` `_PAT_RPOS_` `_PAT_TAB_` `_PAT_RTAB_` `_PAT_ARB_` `_PAT_REM_` `_PAT_FAIL_` `_PAT_ABORT_` `_PAT_SUCCEED_` `_PAT_BAL_` `_PAT_ARBNO_` `_PAT_FENCE_` `_PAT_ALT_` `_PAT_CONCAT_` | core.c | SNOBOL pattern builtin wrappers |
| `kw_anchor` | core.c / stmt_exec.c | &ANCHOR keyword |

**New file:** `src/runtime/pattern_match.c` + `src/runtime/pattern_match.h`

---

### SUBSYSTEM 8: `invocation.c` / `invocation.h`
**CS concept:** Function/procedure call frames, argument staging, invocation model.  
**Current sources:** `core/invoke.c`, `core/name_save.c` (frame push/pop), `rt/rt.c` (rt_frame_*, rt_call_proc, rt_arg_stage), `builtins/gen_runtime.c` (GenFrame, frame_stack)

| Symbol | Current File | Notes |
|--------|-------------|-------|
| `INVOKE_fn` | invoke.c | Generic invocation |
| `ARGVAL_fn` | invoke.c | Arg value |
| `rt_frame_enter` `rt_frame_leave` | rt.c | Frame push/pop |
| `rt_load_frame` `rt_store_frame` | rt.c | Frame slot access |
| `rt_call_proc` `rt_call_proc_descr` | rt.c | Call procedure |
| `rt_arg_stage` | rt.c | Stage argument |
| `rt_proc_register` `rt_proc_reset` `rt_proc_is_registered` `rt_proc_set_fn` | rt.c | Proc table management |
| `rt_call_builtin` `rt_builtin_is_known` | rt.c | Builtin call |
| `rt_frame_enter` `rt_frame_leave` | rt.c | Frame management |
| `rt_do_return` `rt_do_nreturn` | rt.c | Return paths |
| `rt_define_entry` `rt_define` | rt.c | Define a function |
| `rt_call` | rt.c | Generic call |
| `rt_proc_depth` | rt.c | Recursion depth |
| `g_rt_frame_depth` | rt.c | Frame depth global |
| `DEFINE_fn` `DEFINE_fn_entry` `register_fn_alias` `APPLY_fn` | core.c | SNOBOL DEFINE/APPLY |
| `_func_init` `_func_hash` | core.c | Function table init/hash |
| `fn_has_builtin` `core_fn_registered` | core.c | Function registration |
| `FNCEX_fn` `FUNC_NPARAMS_fn` `FUNC_NLOCALS_fn` `FUNC_IS_ENTRY_LABEL` | core.c | Function introspection |
| `_DEFINE_` `_FUNCTION_` `_LABEL_` `_APPLY_` | core.c | Builtin wrappers |
| `_ARG_` `_LOCAL_` `_FIELD_` | core.c | Arg/local/field access |
| `NAME_ctx_enter` `NAME_ctx_leave` | name_save.c | Name context (already in name_binding, shared) |
| `sm_call_proc` `proc_table_call` | gen_runtime.c | Proc-table calls |
| `rt_push_expression_descr` | rt.c | Push expression descriptor |
| `rt_call_arr` | gen_runtime.c | Call array builtin |

**New file:** `src/runtime/invocation.c` + `src/runtime/invocation.h`

---

### SUBSYSTEM 9: `control_flow.c` / `control_flow.h`
**CS concept:** Statement/control flow — SNOBOL goto, label model; generalized to all languages.  
**Current sources:** `core/stmt_exec.c` (exec_stmt, the SNOBOL stmt executor), `core/core.c` (indirect_goto, _GOTO_)

| Symbol | Current File | Notes |
|--------|-------------|-------|
| `rt_in_native_chunk` | rt.c / stmt_exec.c | Native chunk depth guard |
| `cache_insert` `cache_reset` `exec_stmt_pool_reset` `bin_audit_print` | stmt_exec.c | Statement cache |
| `scan_body_fn_u9` | stmt_exec.c | Scan body (mode-2 bridge) |
| `indirect_goto` | core.c | Indirect goto |
| `rt_set_stno` | rt.c | Set statement number |
| `g_dvar_depth` `g_scan_pre_delta` `g_bb_mode` | stmt_exec.c | Control-flow state |
| `Σlen` `Δ` `Ω` `cursor` `subject_len_val` | stmt_exec.c | Subject/cursor state (legacy, → pattern_match or backtrack) |
| `g_cache_hits` `g_cache_misses` `g_bin_hits` `g_bin_misses` `g_bin_str_hits` | stmt_exec.c | Cache metrics |
| `_SETEXIT_` `_COLLECT_` `_DUMP_` `_TRACE_` `_STOPTR_` | core.c | Control builtins |
| `rt_halt_tos` | rt.c | Halt on TOS |
| `g_halt_rc` `g_halt_set` | rt.c | Halt state |
| `rt_unhandled_op` `rt_unhandled_sm` | rt.c | Unhandled operation |
| `rt_bomb` | rt.c | Abort with message |

**New file:** `src/runtime/control_flow.c` + `src/runtime/control_flow.h`

---

### SUBSYSTEM 10: `collections.c` / `collections.h`
**CS concept:** Associative data structures — arrays, tables, stacks, data records.  
**Current sources:** `core/core.c` (array/table/data/stack operations)

| Symbol | Current File | Notes |
|--------|-------------|-------|
| `_tree_ensure_cap` `tree_append` `tree_prepend` `tree_insert` | core.c | Tree/list ops |
| `array_get` `array_set` `array_get2` `array_set2` | core.c | Array ops |
| `_tbl_hash` `table_get` `table_set` `table_set_descr` `table_has` | core.c | Table ops |
| `DEFDAT_fn` `DATCON_fn` `FIELD_GET_fn` `FIELD_SET_fn` | core.c | User-defined data types |
| `_data_ctor_fn` `_make_ctor` `_make_fget` `_make_fset` `_DATA_` | core.c | Data type constructors |
| `core_DATA_register` | core.c | Register data type |
| `NPUSH_fn` `NHAS_FRAME_fn` `NINC_fn` `NINC_AT_fn` `NDEC_fn` `ntop` `NPOP_fn` | core.c | Named stack ops |
| `PUSH_fn` `POP_fn` `TOP_fn` `STACK_DEPTH_fn` | core.c | Generic stack ops |
| `_b_nPush` `_b_nInc` `_b_nDec` `_b_nTop` `_b_nPop` `_b_tree_n` `_b_tree_t` `_b_tree_v` `_b_tree_c` | core.c | Internal tree/stack |
| `_b_field_value` `_b_field_next` | core.c | Field iteration |
| `_ARRAY_` `_TABLE_` `_CONVERT_` `_COPY_` `_ITEM_` `_VALUE_` | core.c | Collection builtins |
| `subscript_get` `subscript_set` `subscript_get2` `subscript_set2` | pattern.c | Subscript ops (move here) |
| `sort_fn` `rsort_fn` `_sort_type_rank` `_sort_cmp_descr` `_SORT_` `_RSORT_` | pattern.c / core.c | Sort operations |
| `NTOP_INDEX_fn` `NSTACK_AT_fn` | core.c | Named stack indexing |
| `rt_field_get` `rt_field_set` | rt.c | Runtime field access |
| `rt_idx_get` `rt_idx_set` | rt.c | Runtime index access |
| `rt_list_bang` | rt.c | List ! operator (generator) |
| `nhome_info` | core.c | Named-stack home info |

**New file:** `src/runtime/collections.c` + `src/runtime/collections.h`

---

### SUBSYSTEM 11: `io_format.c` / `io_format.h`
**CS concept:** I/O and value formatting — write, print, format.  
**Current sources:** `core/core.c` (output/input), `rt/rt.c` (rt_write_*, rt_format_*)

| Symbol | Current File | Notes |
|--------|-------------|-------|
| `output_val` `output_str` | core.c | Output a value/string |
| `input_read` `_INPUT_` `_OUTPUT_` | core.c | Input/output builtins |
| `_io_chan_setup` `_io_chan_find_by_var` `_io_chan_close` `_ENDFILE_` | core.c | I/O channel management |
| `rt_write_str_nl` `rt_write_int_nl` `rt_write_any_nl` `rt_write_strz_nl` | rt.c | Write with newline |
| `rt_pop_write_int_nl` `rt_pop_write_any_nl` | rt.c | Pop-and-write (vstack-era, deprecated) |
| `rt_write_atom` `rt_write_int` `rt_write_float` `rt_write_cstr` | rt.c | Atom/int/float write |
| `rt_write_var` `rt_write_term_ptr` `rt_writeq_term_ptr` `rt_write_canonical_term_ptr` | rt.c | Term write (Prolog) |
| `rt_format_float` | rt.c | Float formatting |
| `rt_push_str` `rt_push_int` `rt_push_null` `rt_push_null_noflip` `rt_push_real_bits` | rt.c | Push value (vstack-era) |
| `rt_pop_void` `rt_pop_store_i64` `rt_push_stored_i64` `rt_pop_store_descr` | rt.c | Pop/store ops |
| `rt_push_expression_descr` | rt.c | Push expression |
| `rt_push_expr` | rt.c | Push expr |
| `rt_case_eq` | rt.c | Case equality |
| `rt_main_init` | rt.c | Main init (I/O setup) |

**New file:** `src/runtime/io_format.c` + `src/runtime/io_format.h`

---

### SUBSYSTEM 12: `resolution.c` / `resolution.h`
**CS concept:** Predicate resolution, clause database, assert/retract — Prolog-specific BUT generalizable to SNOBOL DEFINE/function lookup.  
**Current sources:** `builtins/resolve_runtime.c` (predicate table, assert/retract, ISO error throw, call/findall)

| Symbol | Current File | Notes |
|--------|-------------|-------|
| `resolve_pred_hash` `resolve_pred_table_insert` `resolve_assert_clause` `resolve_retract_clause` `resolve_abolish_pred` | resolve_runtime.c | Predicate DB |
| `resolve_throw_iso_error` `resolve_throw_instantiation_error` `resolve_throw_type_error_evaluable` `resolve_throw_existence_error_procedure` `resolve_throw_term` | resolve_runtime.c | ISO exception model |
| `resolve_catch_pop_top` `resolve_catch_top_trail_mark` | resolve_runtime.c | Exception catch stack |
| `resolve_tenv_add_dedup` | resolve_runtime.c | Term env dedup |
| `resolve_call_term` `resolve_call_term_n` `resolve_invoke_var_goal` | resolve_runtime.c | Goal invocation |
| `interp_exec_builtin` | resolve_runtime.c | Execute builtin goal |
| `is_user_call` | resolve_runtime.c | Is user-defined call? |
| `term_order_cmp` | resolve_runtime.c | Term order comparison |
| `resolve_synth_add_child` `resolve_synth_free` | resolve_runtime.c | Synthetic term building |
| `resolve_iso_mod` | resolve_runtime.c | ISO modulo |
| `resolve_bb_pred_count` `resolve_bb_pred_arity_at` `resolve_bb_once_proc_by_name` | resolve_runtime.c | BB predicate table |
| `g_resolve_bb_table` `g_resolve_bb_count` | resolve_runtime.c | BB pred table globals |
| `rt_findall` | rt.c | findall/3 |
| `rt_catch` `rt_throw` | rt.c | catch/3, throw/1 |
| `rt_aggregate_all_term` | rt.c | aggregate_all |
| `rt_sort_msort` `rt_sort_msort_term` | rt.c | sort/msort |
| `rt_atom_length` `rt_upcase_atom` `rt_downcase_atom` `rt_char_type` `rt_numbervars_term` | rt.c | Atom builtins |
| `rt_atom_concat` `rt_atom_string_pair` `rt_number_string_pair` | rt.c | Atom/string conversion |
| `rt_term_to_atom_term` `rt_atomic_list_concat_term` | rt.c | Term-to-atom |
| `rt_atom_chars_codes` `rt_atom_chars_codes_term` | rt.c | Atom chars/codes |
| `rt_type_test` `rt_type_test_term` | rt.c | Type test builtins |
| `rt_toby_real` | rt.c | To/by real generator |
| `rt_limit_begin` `rt_limit_more` `rt_limit_inc` | rt.c | Limitation generator |
| `resolve_cp_push` `resolve_cp_current` | resolve_runtime.c | Choice-point push/current |

**New file:** `src/runtime/resolution.c` + `src/runtime/resolution.h`

---

### SUBSYSTEM 13: `by_name_dispatch.c` / `by_name_dispatch.h`
**CS concept:** By-name builtin dispatch table — the string→function lookup used by all language layers.  
**Current sources:** `builtins/script_builtins.c`, `builtins/script_builtins_byname.c`, `builtins/gen_runtime.c` (try_call_builtin_by_name), `builtins/scan_builtins.c`

| Symbol | Current File | Notes |
|--------|-------------|-------|
| `script_try_call_builtin` | script_builtins.c | Raku/script entry |
| `script_try_call_builtin_by_name` | script_builtins_byname.c | By-name dispatch |
| `script_try_hash_mutating_builtin` `script_try_hash_builtin` | script_builtins_byname.c | Hash builtins |
| `elem_to_descr` | script_builtins_byname.c | Junction element→DESCR |
| `junction_is` `jct_one_cmp_num` `jct_one_cmp_str` `junction_collapse` | script_builtins_byname.c | Junction ops |
| `gram_set` `gram_get_flavor` `gram_expand` `gram_n` | script_builtins_byname.c | Grammar dispatch |
| `try_call_builtin_by_name` | gen_runtime.c | Icon by-name dispatch |
| `scan_try_call_builtin` | scan_builtins.c | Icon scan dispatch |
| `call_builtin` | gen_runtime.c | Call a builtin |
| `builtin_is_generator` | rt.c | Is builtin a generator? |
| `rt_builtin_is_known` | rt.c | Is builtin known? |
| `rt_jct_relop` | gen_runtime.c | Junction relational op |
| `proc_as_value` | gen_runtime.c | Proc as first-class value |
| `rt_call_arr` | gen_runtime.c | Array-style builtin call |
| `fn_has_builtin` | core.c | Function has builtin? |

**New file:** `src/runtime/by_name_dispatch.c` + `src/runtime/by_name_dispatch.h`

---

### SUBSYSTEM 14: `runtime_eval.c` / `runtime_eval.h`
**CS concept:** Runtime compilation/evaluation — EVAL, CODE, runtime code generation.  
**Current sources:** `core/eval_code.c`

| Symbol | Current File | Notes |
|--------|-------------|-------|
| `eval_node` `eval_expr` `code` | eval_code.c | EVAL/CODE eval |
| `EXPVAL_fn` `CONVE_fn` `CODE_fn` | eval_code.c | Exported EVAL/CODE |
| `EVAL_fn` `opsyn` `compile_to_expression` | pattern.c | EVAL, OPSYN, compile |
| `_EVAL_` `_CODE_` `_OPSYN_` | core.c | Builtin wrappers |

**New file:** `src/runtime/runtime_eval.c` + `src/runtime/runtime_eval.h`

---

### SUBSYSTEM 15: `runtime_init.c` / `runtime_init.h`
**CS concept:** Runtime initialization, finalization, GC, language mode.  
**Current sources:** `rt/rt.c` (rt_init, rt_finalize, rt_gc_init, rt_set_lang)

| Symbol | Current File | Notes |
|--------|-------------|-------|
| `rt_init` `rt_finalize` | rt.c | Init/finalize |
| `rt_gc_init` | rt.c | GC init |
| `rt_set_lang` | rt.c | Set active language |
| `rt_bomb` | rt.c | Fatal abort |
| `rt_unhandled_op` | rt.c | Unhandled op |
| `g_proc_depth` `g_native_chunk_depth` | rt.c | Runtime depth counters |
| `rt_in_native_chunk` | rt.c | Native chunk guard |
| `rt_halt_tos` | rt.c | Halt |
| `g_halt_rc` `g_halt_set` | rt.c | Halt state |
| `SNO_INIT_fn` | core.c | ⚠ SNOBOL runtime lib init (LI-CORE, Lon decision) |
| `g_expression_reg_count` | rt.c | Expression registry count |
| `rt_register_expressions` | rt.c | Register expressions |

**New file:** `src/runtime/runtime_init.c` + `src/runtime/runtime_init.h`

---

### SUBSYSTEM 16: `monitor_trace.c` / `monitor_trace.h`
**CS concept:** Debugging, tracing, monitor IPC.  
**Current sources:** `core/core.c` (trace/monitor/comm), `rt/rt.c` (vstack depth)

| Symbol | Current File | Notes |
|--------|-------------|-------|
| `trace_slot_lookup` `trace_register` `trace_register_callback` `trace_unregister` `trace_registered` `trace_is_active` | core.c | Trace system |
| `mon_send` `mon_at_exit` `mon_emit_label_bin` `_b_MON_*` | core.c | Monitor IPC |
| `load_names_file_bin` `lookup_name_id_bin` `intern_name_bin` | core.c | Binary name table |
| `scrip_tag_to_wire` | core.c | Monitor wire tag |
| `comm_stno` `comm_var` `comm_call` `comm_return` | core.c | Monitor comm helpers |
| `bin_audit_print` | stmt_exec.c | Binary audit print |
| `g_dump` `g_trace` `g_error` | gen_runtime.c | Runtime flags |
| `kw_trace` `kw_ftrace` `kw_stno` `kw_stcount` `kw_stlimit` `kw_fnclevel` | core.c | Keyword trace/count globals |
| `_TRACE_` `_STOPTR_` `_COLLECT_` `_DUMP_` `_SETEXIT_` | core.c | Builtin wrappers |
| `rt_vstack_depth` `rt_vstack_pop` | rt.c | Vstack (scaffolding) |

**New file:** `src/runtime/monitor_trace.c` + `src/runtime/monitor_trace.h`

---

### SUBSYSTEM 17: `keywords.c` / `keywords.h`
**CS concept:** Keyword variable system (&NAME).  
**Current sources:** `core/core.c` (kw_* globals, NV_SET_fn keyword path), `builtins/gen_runtime.c` (kw_assign, kw_read, kw_can_assign)

| Symbol | Current File | Notes |
|--------|-------------|-------|
| `kw_assign` `kw_can_assign` `kw_read` | gen_runtime.c | Keyword assign/read |
| `make_kw_cset` `kw_cset_len` | gen_runtime.c | Keyword cset creation |
| `kw_cset_name` | gen_runtime.h | Keyword cset name |
| `kw_anchor` `kw_trim` `kw_fullscan` `kw_maxlngth` `kw_stlimit` `kw_errlimit` `kw_code` `kw_ftrace` `kw_stno` `kw_stcount` `kw_fnclevel` | core.c | Keyword globals |
| `g_kw_cset_count` `g_kw_ctx` | gen_runtime.c / core.c | Keyword cset state |
| `_HOST_` `_DATE_` `_TIME_` | core.c | Keyword-like builtins |

**New file:** `src/runtime/keywords.c` + `src/runtime/keywords.h`  
*(These could merge into name_binding; keeping separate because they're a distinct protocol)*

---

## SNOBOL RUNTIME LIBRARY — `core/` (LI-CORE, Lon decision)

`src/runtime/core/` hosts the SNOBOL execution model. Per the `SNO_INIT_fn` precedent (a generic CS name would be vague), these are NOT renamed in the LI sweep and NOT partitioned by the RS rung without Lon's call:

- `SNO_INIT_fn`, `SnoRt`, `SNO_LIB`, `SNO_SAVE_MAX`, `g_sno_save`, `g_sno_save_top` — the SNOBOL save/restore frame.

The rung's RS-2..RS-N moves will pull the functions OUT of `core/` into the subsystem files above, leaving `core/` with only the irreducibly-SNOBOL items. After all moves, `core/` should contain: `SNO_INIT_fn`, the SNOBOL save/restore frame, and any remaining SNOBOL-specific items Lon decides stay named.

---

## Proposed File Layout (post-RS)

```
src/runtime/
  values.c / values.h             — DESCR ops, type coercion
  name_binding.c / name_binding.h — NV_*, NAME_t, name ctx save/restore
  string_ops.c / string_ops.h     — concat, substr, length, case, pad
  arithmetic.c / arithmetic.h     — numeric ops, comparison
  backtrack.c / backtrack.h       — choice points, trail, generators, cut
  unification.c / unification.h   — WAM unify, term build, env
  pattern_match.c / pattern_match.h — string scan/pattern (SNOBOL+Icon)
  invocation.c / invocation.h     — call frames, arg staging, proc table
  control_flow.c / control_flow.h — goto, label, stmt execution model
  collections.c / collections.h   — array, table, data, stack
  io_format.c / io_format.h       — write, print, I/O channels
  resolution.c / resolution.h     — predicate DB, assert/retract, ISO errors
  by_name_dispatch.c / .h         — by-name builtin lookup tables
  runtime_eval.c / runtime_eval.h — EVAL, CODE, runtime compile
  runtime_init.c / runtime_init.h — init, finalize, GC, lang mode
  monitor_trace.c / monitor_trace.h — trace, monitor IPC
  keywords.c / keywords.h         — &NAME keyword variable system
  core/                           — SNOBOL runtime lib (LI-CORE, Lon decision)
    core.c / core.h               — (residual SNOBOL items after moves)
    pattern.c                     — (residual patnd builders → pattern_match)
    stmt_exec.c                   — (residual → control_flow)
    eval_code.c                   — (→ runtime_eval)
    eval_pat.c                    — (→ pattern_match)
    name_t.c / name_save.c        — (→ name_binding)
    argval.c / coerce.c           — (→ values)
    invoke.c                      — (→ invocation)
  rt/ (dissolve after moves)
    rt.c                          — (grab-bag, emptied into subsystems above)
  builtins/ (dissolve after moves)
    gen_runtime.c                 — (→ backtrack + name_binding + by_name)
    resolve_runtime.c             — (→ unification + backtrack + resolution)
    scan_builtins.c               — (→ pattern_match + by_name)
    script_builtins*.c            — (→ by_name_dispatch)
```

---

## RS-1 NOTES FOR LON

1. **`backtrack.c` is the highest-value unification** (the one Lon specifically called out): Prolog choice-points (`resolve_choice` stack, trail), Icon generator state (`GenFrame`, `sm_yield_to_caller`), and Raku junction evaluation all implement the same backtracking/goal-direction engine. One file.

2. **`pattern_match.c` unifies** the SNOBOL pattern tree (`pat_*`, `patnd_*`) with Icon string scanning (`scan_try_call_builtin`, `cset_*`) and the mode-3 bridge (`rt_pat_*`). "SNOBOL `find`/Raku `index`/Icon string-scan are the same search" — Lon's observation.

3. **`resolution.c` vs `by_name_dispatch.c`**: Resolution owns the Prolog clause database (assert/retract, choice-point protocol). By-name dispatch owns the string→function lookup tables (which all languages share). These are two different mechanisms and should stay separate.

4. **`rt/rt.c` dissolves completely** — every function in it maps to one of the subsystems above. It is the current grab-bag.

5. **`core/core.c` (3449 lines) is the biggest split** — its 238 functions map to: `name_binding`, `string_ops`, `arithmetic`, `collections`, `io_format`, `invocation`, `keywords`, `monitor_trace`, `runtime_eval`, `control_flow` (roughly 20–50 functions each). The SNO-specific residue (save/restore, SNOBOL lib init) stays in `core/` by the LI-CORE carve-out.

6. **Method reminder** (RS-2..RS-N): definition-location authoritative; MOVE-ONLY, zero behavioral change; update Makefile `RT_PIC_SRCS` + `build_scrip.sh` in lockstep with every file add/move/delete; gate byte-identical (m2 SNOBOL4 7/7 + Icon 12/12 + Prolog 5/5 HARD, prove_lower2 67, no_bb_bin_t 0, concurrency OK) after every commit.

---

## Gates (unchanged — RS-1 is analysis only)

```
m2 SNOBOL4 7/7 HARD  ✅
m2 Icon 12/12 HARD   ✅
m2 Prolog 5/5 HARD   ✅
prove_lower2 67       ✅
no_bb_bin_t 0         ✅
LI-FENCE              ✅
concurrency OK        ✅
```

**SCRIP HEAD:** `85677cb` (unchanged — no code committed)  
**Next step:** Lon reviews this map → approve/revise → RS-2 (first subsystem move slice, gated)

---

# RS-2 EXECUTION — PARTITION STARTED (2026-06-02 Sonnet 4.6, continuation)

Lon directive: "Rearrange ALL the runtime so files are SUBSYSTEMS not language silos. I'm trusting you."
Executed as **gated slices** per the rung's "never start a split you can't finish+gate+commit" rule. Two slices landed green; stopped at a green committed state when context budget (~70% at session start) ran low rather than leave a half-moved broken tree.

## ✅ SLICE 1 — `runtime_eval` (SCRIP `970dbf5`)
`git mv src/runtime/core/eval_code.c → src/runtime/runtime_eval.c` (EVAL/CODE runtime-compile capability). Fixed one relative include (`../../parser/` → `../parser/` after moving up a dir). Makefile RT_PIC_SRCS + scrip per-`.o` rule updated in lockstep. **Validated the gated-slice loop end-to-end.** Gates byte-identical.

## ✅ SLICE 2 — `unification` (SCRIP `17e759e`)
Extracted the **WAM execution core** from the grab-bag `rt/rt.c` (lines 1135–1263) into new `src/runtime/unification.c`: `rt_node_to_term`, `rt_unify_terms`, `rt_unify_const`, `rt_trail_mark/unwind/push/pop` (+ statics `g_resolve_mark_stack`/`_top`), `rt_env_alloc`, `rt_env_current`, `rt_cp_save_caller_env`, `rt_choice_cut_enter/exit/unwind`, `rt_get_cut_flag`, `rt_main_init`. Cut+paste move-only; call sites untouched (decls live in `rt.h` and the emitter's `bb_unify.cpp` extern). Breaks the "Prolog WAM lives in the grab-bag" coupling — this is the start of Lon's #1 backtracking-engine unification. Gates byte-identical.
- ⚠ **Residual to re-home in a follow-up micro-slice:** `rt_main_init` (setvbuf + bb_pool_init + trail_init + prolog_atom_init) is cross-capability "runtime init" — it rode along in the contiguous block; belongs in `runtime_init.c`. The trail/choice/cut functions are arguably `backtrack.c` not `unification.c` (per RS-1 map they're separate subsystems); they were kept together here because they share the `g_resolve_mark_stack` static and are one physical WAM block. A later slice may split unification(term/unify/env) from backtrack(trail/choice/cut).

## 🔑 KEY FINDINGS (save the next session real time)
1. **Build lockstep = the Makefile ONLY.** `build_scrip.sh` just calls `make scrip`. Per new `.c`: add ONE line to `RT_PIC_SRCS` (line ~71–148) AND ONE compile rule in the `scrip:` target (line ~221+). Linking is a `$(OBJ)/*.o` glob — no per-`.o` link prereq. Per emptied/removed `.c`: remove from both.
2. **INCLUDE GOTCHA for files moved to `src/runtime/` (sibling of core/rt/builtins):** the `scrip:` per-`.o` build uses `CRT`/`CBASE` which have `-I$(SRC)/runtime` and `-I$(SRC)/runtime/core` but **NOT `-I$(SRC)/runtime/rt`**. So a file in `src/runtime/X.c` must use **relative** includes: `"rt/rt.h"`, `"builtins/resolve_runtime.h"`, `"../parser/prolog/prolog_atom.h"`. (`"core.h"` and `"bb_pool.h"` resolve via -I.) `core.h` brings `<gc/gc.h>`; `resolve_runtime.h` brings `Term`/`Trail`/`resolve_choice`/`g_resolve_*`/IR enum/term API. The `libscrip_rt` build DOES have `-I.../rt` so it's more forgiving — always test BOTH `make scrip` and `make libscrip_rt`.
3. **PROLOG BUILTINS ARE OUT OF SCOPE.** `rt_findall`, `rt_compound_build_n`, `rt_atom_*`, `rt_copy_term`, `rt_sort_msort`, `rt_catch/throw`, `rt_type_test`, `rt_char_type`, `rt_numbervars`, `rt_is*` are DEFINED in `src/interp/IR_interp.c` (the IR-graph interpreter), NOT in `src/runtime/**`. Definition-location is authoritative ⇒ they are NOT runtime's to move under this rung. The RS-1 map's `resolution.c` therefore draws ONLY from `builtins/resolve_runtime.c` (predicate DB / choice-point protocol / assert-retract / ISO errors), not from the `rt_*` builtins.

## REMAINING WORK (recommended order, each a gated slice)
The grab-bag `rt/rt.c` and the language-named files are the targets. Cleanest-first:
- **`runtime_init.c`** — `rt_init`, `rt_finalize`, `rt_gc_init` (~1253), `rt_set_lang` (~1258), `rt_bomb`, `rt_unhandled_op` + re-home `rt_main_init` here from unification.c. (Adjacent-ish; small.)
- **`io_format.c`** — the `rt_write_*` family from rt.c (scattered — needs per-function moves). Pairs with `output_val`/`output_str` from core.c.
- **`arithmetic.c`** — `rt_arith`(~1144), `rt_neg`(~892), `rt_coerce_num`(~865), `rt_incr/decr`(~1022/1028), `rt_acomp`/`rt_lcomp`, `rt_unop_*`, `rt_exp` + the core.c `add/sub/mul/DIVIDE_fn/POWER_fn/eq/ne/lt/...` block. (Scattered in rt.c; the core.c block is more contiguous.)
- **`pattern_match.c`** — the big `rt_pat_*` family from rt.c + `core/pattern.c` (whole-file) + `core/eval_pat.c` + `scan_builtins.c` + the `patnd_*` helpers from `stmt_exec.c`. (Largest; do whole-file `git mv` of pattern.c/eval_pat.c first, then pull rt_pat_* in.)
- **The language-named FILES (the loudest silos):** `gen_runtime.c` (Icon), `resolve_runtime.c` (Prolog), `script_builtins*.c` (Raku) → split by capability into `backtrack.c` / `unification.c` / `resolution.c` / `by_name_dispatch.c` / `keywords.c` / `name_binding.c`. These have intricate file-local statics ⇒ each is its own multi-slice effort; move whole coherent blocks, gate after each.
- **`core/core.c` (3449 lines)** — the biggest split, into `name_binding` / `string_ops` / `arithmetic` / `collections` / `io_format` / `invocation` / `keywords` / `monitor_trace` / `control_flow`. SNO-specific residue (`SNO_INIT_fn`, save/restore frame) stays in `core/` per LI-CORE.
- **`RS-FENCE`** — `scripts/test_gate_runtime_subsystems.sh` asserting the partition; wire into Session Setup.

## Gates after slice 2 (byte-identical baseline, every commit)
```
m2 SNOBOL4 7/7 HARD  · m2 Icon 12/12 HARD · m2 Prolog 5/5 HARD
prove_lower2 67 · no_bb_bin_t 0 · LI-FENCE OK · concurrency OK
```
**SCRIP HEAD after slice 2:** `17e759e` (slices `970dbf5` runtime_eval, `17e759e` unification — both pushed-pending).
