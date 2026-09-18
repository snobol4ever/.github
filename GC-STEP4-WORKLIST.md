# F6 STEP 4 WORKLIST -- 208 unpolled allocating call sites, split disjoint by FILE

Measured 2026-09-18 at SCRIP HEAD with SCRIP_GC_CENSUS_LIST_ALL=1.
NO TWO SEATS IN ONE FILE. Re-run the census after each landing; the number that matters is unpolled -> 0.

## cto -- 70 sites over 26 files
- src/templates/bb/bb_call_proc_staged.cpp       13
- src/templates/bb/bb_to_by.cpp                  6
- src/templates/bb/bb_idx_get.cpp                5
- src/templates/bb/bb_binop_gvar_arith.cpp       5
- src/templates/bb/bb_scan_any.cpp               4
- src/templates/bb/bb_call.cpp                   4
- src/templates/bb/bb_scan_upto.cpp              3
- src/templates/bb/bb_limit.cpp                  3
- src/templates/bb/bb_binop_relop.cpp            3
- src/templates/bb/bb_subscript2.cpp             2
- src/templates/bb/bb_scan_move.cpp              2
- src/templates/bb/bb_match_len.cpp              2
- src/templates/bb/bb_keyword_snobol4.cpp        2
- src/templates/bb/bb_coerce_string.cpp          2
- src/templates/bb/bb_binop_relop_val.cpp        2
- src/templates/bb/bb_assign_global.cpp          2
- src/templates/bb/bb_subject.cpp                1
- src/templates/bb/bb_return.cpp                 1
- src/templates/bb/bb_match_value.cpp            1
- src/templates/bb/bb_match_rtab.cpp             1
- src/templates/bb/bb_match_pos.cpp              1
- src/templates/bb/bb_match_atp.cpp              1
- src/templates/bb/bb_keyword_icon.cpp           1
- src/templates/bb/bb_indirect_assign_lit_s.cpp  1
- src/templates/bb/bb_coret.cpp                  1
- src/templates/bb/bb_activate.cpp               1

## cfo -- 69 sites over 27 files
- src/templates/bb/bb_match_defer.cpp            10
- src/templates/bb/bb_to.cpp                     6
- src/templates/bb/bb_assign_var_sub.cpp         6
- src/templates/bb/bb_call_fn.cpp                5
- src/templates/bb/bb_scan_bal.cpp               4
- src/templates/bb/bb_field_get.cpp              4
- src/templates/bb/bb_section.cpp                3
- src/templates/bb/bb_scan_many.cpp              3
- src/templates/bb/bb_keyword_assign.cpp         3
- src/templates/bb/bb_suspend.cpp                2
- src/templates/bb/bb_scan_tab.cpp               2
- src/templates/bb/bb_scan_match.cpp             2
- src/templates/bb/bb_match_end.cpp              2
- src/templates/bb/bb_keyword_assign_snobol4.cpp 2
- src/templates/bb/bb_coerce_integer.cpp         2
- src/templates/bb/bb_binop_gvar_arith_slot.cpp  2
- src/templates/bb/bb_var_ref.cpp                1
- src/templates/bb/bb_unop_gvar_slot.cpp         1
- src/templates/bb/bb_rev_swap.cpp               1
- src/templates/bb/bb_ref_invariant.cpp          1
- src/templates/bb/bb_match_tab.cpp              1
- src/templates/bb/bb_match_rpos.cpp             1
- src/templates/bb/bb_match_notany.cpp           1
- src/templates/bb/bb_match_any.cpp              1
- src/templates/bb/bb_key_gen.cpp                1
- src/templates/bb/bb_idx_set.cpp                1
- src/templates/bb/bb_cofail.cpp                 1

## ceo -- 69 sites over 27 files
- src/templates/bb/bb_define.cpp                 9
- src/templates/bb/bb_unop.cpp                   6
- src/templates/bb/bb_match_capture.cpp          6
- src/templates/bb/bb_call_value.cpp             5
- src/templates/xa/xa_flat.cpp                   4
- src/templates/bb/bb_iterate.cpp                4
- src/emitter/emit.cpp                           4
- src/templates/bb/bb_scan_find.cpp              3
- src/templates/bb/bb_goto_deferred.cpp          3
- src/templates/bb/bb_subscript.cpp              2
- src/templates/bb/bb_scan_pos.cpp               2
- src/templates/bb/bb_rev_assign_var.cpp         2
- src/templates/bb/bb_match_breakx.cpp           2
- src/templates/bb/bb_gen_scan.cpp               2
- src/templates/bb/bb_call_write_slot.cpp        2
- src/templates/bb/bb_assign_var.cpp             2
- src/templates/bb/bb_var_global.cpp             1
- src/templates/bb/bb_swap_var.cpp               1
- src/templates/bb/bb_rev_assign_global.cpp      1
- src/templates/bb/bb_random.cpp                 1
- src/templates/bb/bb_match_span.cpp             1
- src/templates/bb/bb_match_replace.cpp          1
- src/templates/bb/bb_match_break.cpp            1
- src/templates/bb/bb_lit_scalar.cpp             1
- src/templates/bb/bb_indirect_assign_var.cpp    1
- src/templates/bb/bb_gcc.cpp                    1
- src/templates/bb/bb_coerce_real.cpp            1

