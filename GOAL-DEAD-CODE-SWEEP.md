# GOAL-DEAD-CODE-SWEEP.md — Deterministic dead-code elimination

**Method:** GC-sections linker oracle (`-ffunction-sections -fdata-sections` + `--gc-sections --print-gc-sections`) on the full scrip binary. 841 programs compiled across all 6 languages to build ROOTS_EMIT. Combined roots: 2208 symbols. Dead: **601 functions** confirmed unreachable.

**Attic convention:** dead snippets → `src/attic/<mirror-path>/file.c` with provenance header. Whole-file-dead → `git mv` to `src/attic/<mirror-path>/file.c`.

**Completed removals (2026-06-14):**
- `src/attic/smx_dead_stubs.c` — dropped from Makefile compile (already in attic); `generator_state_new_proc` + `bb_broker_drive_sm_one` SM stubs
- `src/driver/interp_ast_stubs.c` — `execute_program_steps` stub excised → attic mirror
- `src/driver/interp_globals.c` — `g_ir_step_limit/done/jmp`, `rs24_diag_hits_ptr`, `rs24_diag_dump`, `rs24_diag_kind_name` excised → attic mirror
- `src/driver/interp.h` — `execute_program_steps`, `g_ir_step_limit/done/jmp` declarations removed → attic mirror
- `src/runtime/builtins/gen_runtime.c` — `sm_yield_to_caller` stub excised → attic mirror
- `src/runtime/rt/rt.c` — weak stubs `sm_opcode_name`, `_is_pat_fnc_name`, `_expr_is_pat` excised → attic mirror
- `src/contracts/SM.h` — `sm_opcode_name` declaration removed → attic mirror
- `src/contracts/ast_print.c` — `ir_set_print_width`, `ir_get_print_width` excised → `src/attic/contracts/ast_print.c`
- `src/lower/ast_clone.c` + `ast_clone.h` — **whole file dead → `git mv` to attic**; `lower.h` `#include "ast_clone.h"` removed; Makefile entry removed
- `src/emitter/emit_core.c` — 11 functions excised → `src/attic/emitter/emit_core.c`: `emit_mode_set`, `emitter_init_macro_def`, `ef_u32`, `ef_u64`, `ef_t3c`, `emit_call_label`, `emit_text_stno_banner`, `emit_text_rawf`, `bb_is_generator`, `bb_walk`, `bb_walk_rec`; plus associated `g_visited`/`g_vcount`/`IR_WALK_MAX` data
- `src/emitter/emit_ir.h` — `bb_is_generator`, `bb_walk` declarations removed
- `src/emitter/emit_core.h` — `emit_mode_set`, `emit_text_rawf`, `emit_text_stno_banner`, `emit_call_label` removed
- `src/emitter/emit_form.h` + `emit.h` — `emitter_init_macro_def` removed

**POLICY: JVM / .NET / JS / WASM backend helpers are KEPT** even when dead from the current x86-only build. Do not touch: `js_*`, `jvm_*`, `net_*`, `wasm_*` functions.

**Remaining 601-item dead list (GC oracle, 2026-06-14) — next sessions:**

Functions confirmed dead by `--gc-sections` but NOT yet removed. Sorted by source cluster:

```
ARGVAL_fn CODE_fn CONCAT_fn FUNC_IS_ENTRY_LABEL INDR_GET_fn INDR_SET_fn
INTGER_fn INTVAL_fn INVOKE_fn IR_sidecar_own IS_CSET_fn IS_FAIL_fn IS_INT_fn
IS_NULL_fn NAME_commit NAME_fn NAME_pop NAME_push NHAS_FRAME_fn NIINC_AT_fn
NSTACK_AT_fn NTOP_INDEX_fn NV_REG_fn NV_SYNC_fn PATVAL_fn POP_fn PUSH_fn
SIZE_fn STACK_DEPTH_fn STRCONCAT_fn STRDUP_fn TOP_fn VARVUP_fn
_b_field_next _b_field_value _data_ctor_fn _expr_is_pat _is_pat_fnc_name
_rt_DIFFER _rt_IDENT _rt_nv_fold_get _rt_nv_fold_set _rt_usercall _tree_ensure_cap
ag_ring_clear arg_common array_ptr assign_safe_kind ast_gc_clone ast_node_new ast_push
atom_chars_codes_common
bb_arbno_new bb_atp_new bb_body_cp_free_except_tail bb_body_has_live_choice
bb_body_live_choice_cut_aware bb_body_single_solution bb_cap_new bb_cap_new_call
bb_dcap_clear bb_dcap_flush bb_dcap_record bb_graph_of_pred bb_graph_of_proc
bb_in_pool bb_is_gen_kind_raw bb_is_gen_node bb_is_generator bb_label_landing
bb_pool_reset bb_prepare_capture_arbno bb_reset bb_restore_state bb_slot_alloc32
bb_snapshot_state bb_walk bb_walk_rec
call_builtin call_native_chunk chunk_reg_lookup clear_pending_flags code_free
collect_procs comm_stno core_fn_registered cset_complement ctx_ensure_capacity
ctx_entries dat_field_call
data_buf_emit_block_comment data_buf_pend_label data_buf_remember_label
data_buf_three_col descr_is_truthy dup_substr
ef_t3c ef_u32 ef_u64
emit_1asm emit_2asm emit_call_label emit_comment emit_decl emit_directive
emit_io_flush emit_io_get_sink emit_io_reset emit_mode_set emit_text_rawf
emit_text_stno_banner emit_textf emit_tree_expr emit_tree_stmt emitter_init_macro_def
eq exec_stmt_blob expr_add_child expr_free expr_new
flush_pending_captures fn_has_builtin frame_env_active frame_env_load frame_env_store
frame_lookup frame_lookup_sv functor_common
gen_bb_pump_proc_by_name gen_resume_target
gz_eval_cell
icn_lex_peek icn_parse_expr idx_to_handle ind indent indirect_goto input
interp_eval_ref ir_call_arg ir_get_print_width ir_is_scan_kind ir_is_single_shot
ir_print_node_nl ir_set_print_width is_current_frame_local is_suspendable is_user_proc
kind_native_stub kw_assign kw_can_assign lc_vec_at lconcat_d lex_at_end lex_destroy
lex_peek list_len local_assign_rhs_ok
lower_flat_reset lower_flat_set_cap_fixup lower_flat_set_intern_str
lower_icon lower_icon_enum lower_pascal lower_proc_gen lower_prolog lower_raku lower_raku_enum
make_list meta_arith meta_builtin_solve meta_compile meta_conj_drive meta_disj_advance
meta_disj_mark meta_disj_unwind meta_fr_new meta_pred_redo meta_pred_solve meta_redo
meta_solve mktok
name_commit_value name_init_as_call name_init_as_ptr name_init_as_var ne
net_charset_class net_class_hdr net_cursor_load net_escape_ldstr net_fail_ret
net_parse_define_proto net_push_i4 net_spec_of net_α_hdr net_β_hdr [KEEP - .NET backend]
next_label nfa_accept nfa_group_name_copy nfa_ngroups nfa_start nfa_states
nhome_info nv_reset nv_restore nv_snapshot
parse_expr parse_expr_from_str parse_program parse_program_tokens
pas_base pas_loc_of_name pas_slot_read pas_slot_write pas_uplevel_find
pascal_yyget_debug pascal_yyget_in pascal_yyget_leng pascal_yyget_lineno
pascal_yyget_out pascal_yyget_text pascal_yylex_destroy pascal_yypop_buffer_state
pascal_yypush_buffer_state pascal_yyset_debug pascal_yyset_in pascal_yyset_lineno pascal_yyset_out
pat_assign_callcap pat_assign_callcap_named pat_assign_callcap_named_imm
pat_assign_cond pat_assign_imm pat_at_cursor pat_pool_reset pat_ref pat_user_call
pl_arg pl_arith_op_floaty pl_assert_term pl_callee_disj_hint pl_catch_block_index
pl_disj_arm_enter pl_findall_goal_conj_admissible pl_findall_goal_graph_simple
pl_flat_arith_leaf_float_ok pl_flat_arith_leaf_simple pl_flat_goal_is_simple
pl_functor pl_ite_then_branch_trivial pl_make_clause pl_rich_is_lint_simple
pl_rt_assertz pl_term_to_string pl_univ pl_write_to_file
pop_loop print_decl print_tree prolog_atom_count prolog_program_free
protected_pat_name_to_sm_op push_loop
raku_meth_lookup raku_meth_register raku_yyget_debug raku_yyget_in raku_yyget_leng
raku_yyget_lineno raku_yyget_out raku_yyget_text raku_yylex_destroy
raku_yypop_buffer_state raku_yypush_buffer_state raku_yyset_debug raku_yyset_in
raku_yyset_lineno raku_yyset_out
real_fn rebus_emit rebus_print rebus_yy_delete_buffer rebus_yy_scan_buffer
rebus_yy_scan_bytes rebus_yy_scan_string rebus_yyfree rebus_yyget_debug rebus_yyget_in
rebus_yyget_leng rebus_yyget_lineno rebus_yyget_out rebus_yyget_text rebus_yylex_destroy
rebus_yypop_buffer_state rebus_yypush_buffer_state rebus_yyset_debug rebus_yyset_in
rebus_yyset_lineno rebus_yyset_out
reset_capture_registry
resolve_abolish_pred resolve_arith_eval resolve_assert_clause resolve_atomic_text
resolve_bb_bind_arg resolve_bb_entry_node resolve_bb_env_install resolve_bb_env_pop
resolve_bb_env_push resolve_bb_env_save_push resolve_bb_graph_at resolve_bb_once_proc_by_name
resolve_call_block_label resolve_catch_pop_top resolve_catch_push resolve_catch_take_exception
resolve_catch_top_cp_mark resolve_catch_top_env resolve_catch_top_trail_mark
resolve_choice_unique_indexed_body resolve_cp_current resolve_cp_pop resolve_cp_push
resolve_cp_truncate resolve_emit_callee_block_body resolve_env_new resolve_format_float
resolve_nb_get resolve_nb_set resolve_node_to_term resolve_pred_entry_lookup
resolve_pred_table_get_or_create_choice resolve_pred_table_lookup_global
resolve_retract_clause resolve_term_first_arg_key resolve_throw_existence_error_procedure
resolve_throw_instantiation_error resolve_throw_iso_error resolve_throw_term
resolve_throw_type_error_evaluable
rt_acomp rt_aggregate_all_meta rt_arg rt_arg_term rt_arith_cmp rt_arith_cmp_extract
rt_arith_cmp_nodes rt_atom_chars_codes rt_atom_chars_codes_term rt_atom_concat
rt_atomic_list_concat_term rt_call rt_call_builtin rt_call_term rt_cap_assign
rt_case_eq rt_catch_native rt_char_type rt_choice_cut_enter rt_choice_cut_exit
rt_choice_cut_unwind rt_coerce_num rt_concat rt_copy_term_term rt_copy_term_terms
rt_cp_get_cursor rt_cp_inc_cursor rt_cp_save_caller_env rt_cp_trail_unwind rt_cs_new
rt_dcap_clear rt_decr rt_define rt_define_entry rt_do_nreturn rt_do_return
rt_env_alloc rt_env_current rt_exec_stmt_pat rt_exp rt_field_get rt_field_set
rt_finalize rt_findall_term rt_format rt_format_resolve rt_format_term rt_format_walk
rt_frame_enter rt_frame_leave rt_functor rt_functor_term rt_gc_init rt_gen_concat
rt_get_cut_flag rt_halt_tos rt_idx_get rt_idx_set rt_in_native_chunk rt_incr
rt_init rt_init_arbno rt_init_cap rt_init_cap_call rt_is rt_is_cell rt_is_cell_lit
rt_is_lint rt_last_ok rt_lcomp rt_limit_begin rt_limit_inc rt_limit_more
rt_load_frame rt_main_init rt_match_blob rt_match_lit rt_match_variant
rt_meta_redo rt_meta_solve rt_nb_getval_term rt_nb_setval_term rt_neg
rt_number_string_pair rt_numbervars_term rt_nv_get rt_nv_set
rt_pat_abort rt_pat_alt rt_pat_any rt_pat_arb rt_pat_arbno rt_pat_bal
rt_pat_break rt_pat_breakx rt_pat_capture rt_pat_capture_fn rt_pat_capture_fn_args
rt_pat_cat rt_pat_deref rt_pat_eps rt_pat_fail rt_pat_fence rt_pat_fence1
rt_pat_len rt_pat_lit rt_pat_notany rt_pat_pos rt_pat_refname rt_pat_rem
rt_pat_rpos rt_pat_rtab rt_pat_span rt_pat_succeed rt_pat_tab rt_pat_usercall
rt_pat_usercall_args rt_pl_arith_cmp_cells rt_pl_frame_sync_env rt_pl_is_cell
rt_pl_pred_lookup rt_pl_table_install rt_pl_throw_clear rt_pl_unify_struct_gz
rt_plus rt_pop_nv_set rt_pop_store_descr rt_pop_store_i64 rt_pop_void
rt_pop_write_any_nl rt_pop_write_int_nl rt_push_expr rt_push_expression_descr
rt_push_int rt_push_null rt_push_null_noflip rt_push_real_bits rt_push_stored_i64
rt_push_str rt_redo_meta rt_register_cap rt_register_expressions rt_set_lang
rt_set_last_ok rt_set_stno rt_sort_msort rt_sort_msort_term rt_store_frame
rt_subject_load rt_succ rt_term_cmp rt_term_cmp_nodes rt_term_to_atom_term
rt_throw_term rt_toby_real rt_trail_mark_pop rt_type_test rt_unhandled_op
rt_unhandled_sm rt_univ rt_univ_term rt_univ_term_list rt_unop_neg rt_unop_nonnull
rt_unop_not rt_unop_null_test rt_unop_pos rt_unop_size rt_vstack_depth rt_vstack_pop
rt_write_canonical_term_ptr rt_write_cstr rt_write_float rt_write_str_nl
rt_write_term_ptr rt_write_var rt_writeq_term_ptr
same_var_target sc_label_new sc_loop_find_innermost sc_name_table_build
sc_switch_emit_implicit_break scan_try_call_builtin scope_slot_chain
script_try_call_builtin script_try_hash_mutating_builtin script_try_mutating_builtin_by_name
seq_cache_find seq_cache_get seq_cache_push setexit_label_get shadow_get
shared_arith size size_value sm_opcode_name sm_yield_to_caller
sno_parse sno_parse_string sno_reset sort_msort_common
stage2_free_bb_after_emit stage2_free_sm_bb stmt_free stmt_init stmt_subj
string_fn string_section_assign sub_label susp_gen_cache_get suspend_buf_push
table_ptr table_set term_deref trail_mark trail_mark_fn tree_append tree_insert
tree_new0 tree_prepend tree_remove
var_as_pattern walk_bb_register_child_label
wasm_intern_name wasm_intern_str wasm_parse_define_signature wasm_strtab_reset
wasm_userfn_find wasm_userfns_reset [KEEP - WASM backend]
yy_init_globals yy_pop_state yy_scan_string yy_top_state yyget_column yyget_debug
yyget_extra yyget_in yyget_leng yyget_lineno yyget_out yyget_text
yylex_init_extra yyset_column yyset_debug yyset_extra yyset_in yyset_lineno yyset_out
yyunput γ_to ω_to
```
