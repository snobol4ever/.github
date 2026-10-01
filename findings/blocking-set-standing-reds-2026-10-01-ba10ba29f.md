# Blocking set standing reds, 2026-10-01, SCRIP ba10ba29f (the coo's round 3, stage B2')

FINDING by the coo. `make test` at SCRIP ba10ba29f, corpus 38f66bd30, .github 4aef1bd6: 687 arms, 600 green, 71 red, 16 refused (52 blocking reds, 14 blocking refusals), 4 shards, 1680 s. The same set at c8dc0d182 read 575 green / 76 red / 35 refused; 26 reds were cured by the landings between (hq_icon's 5dd66942c witness semicolons, b7706863b link order, c22d4d983); 2 entered (test_gate_gc_the_caller_saved_spill_block_never_holds_a_heap_reference, the cfo's origin red already sent to the cto; test_gate_sno_parser_refuses_at_compile_time_what_spitbol_refuses, landed red by design at 9dc17e4e7). No earlier full reading of the set is on file from this seat, so each red below is STANDING at both readings and carries no landing range. The coo's own landings of the day were A/B'd on the seven harness-touching reds (origin scripts against 9206cc73b's): identical failing checks.

Class key: icon-semicolon = an inline Icon witness without the semicolons SCRIP (c299b8a03) and, since CEO-1393, the oracle require; gc = a test_gate_gc_*; port-trace = REPORTED by design.

## cfo -- 10 (7 blocking)

| gate | set | verdict | class | first failing line |
|---|---|---|---|---|
| test_gate_gc_a_shared_concat_slot_capture_survives_a_collection | blocking | RED | gc |  |
| test_gate_gc_an_arena_pin_names_the_shipped_window_and_the_record_can_see_it | blocking | RED | gc | ok   (d) a KB-pinned run declares its arena to the progress record -- axis reads [SCRIP_GC_STRESS=3,SCRIP_HEAP_KB=64]; before this landing it read SCR |
| test_gate_gc_emitted_safe_point_matches_its_contract | blocking | RED | gc | note hb_icn_op_context_after_a_converted_error hb_icn_op_context_held_into_a_builtin_traceback hb_apply_opens_and_lands carry no .ref AND are absent f |
| test_gate_gc_every_credited_bare_poll_site_has_a_zero_collection_witness | blocking | RED | gc | FAIL (d) unwitnessed=57 is above the declared ceiling 53 -- a site lost its witness (STALE), a witness stopped reading zero (NOT-ZERO), or the census  |
| test_gate_gc_instrument_censuses_are_wired_and_trip | blocking | RED | gc | FAIL; census rc |
| test_gate_gc_rbx_is_the_frontier | blocking | RED | gc | FAIL_ONCE=1 plants a scratch rbx spelling into arm 1's population (run with FAIL_ |
| test_gate_gc_a_collection_over_a_small_live_set_stays_under_its_instruction_budget | blocking | REFUSED | gc | build-behaviour probe [test_gate_gc_a_collection_over_a_small_live_set_stays_under_its_instruction_budget]: consistent -- tree 29dfe5aa232021914e4fb43 |
| test_gate_gc_a_safe_point_stores_into_a_mapped_slot | reported | RED | gc | FAIL (h) 972 safe point(s) still store outside their graph's frame map. |
| test_gate_gc_one_stack_the_walker_sweeps_tagged_cells | reported | RED | gc | FAIL (d) NO MAP IS READ: 12 of 12 run(s) still carry DT_MAP cells the walk scans for: hb_blob_span_defer.sno[m3] hb_blob_span_defer.sno[m4] hb_eval_na |
| test_gate_gc_the_caller_saved_spill_block_never_holds_a_heap_reference | reported | RED | gc | FAIL-ONCE HOLDS: with a heap pointer planted in slot 7 the detector NAMES it 166 time(s) over 166 planted collection(s); with the plant off the same w |

## coo (instruments) or the ceo -- 19 (13 blocking)

| gate | set | verdict | class | first failing line |
|---|---|---|---|---|
| test_gate_add_ladder_witness_declares_every_attribute_column | blocking | RED | other | FAIL  (4) the disagreeing rungs: rc=2 |
| test_gate_baton_donewhen_reads_its_runner_rc | blocking | RED | other | B       preprocessing-leaves-scrip-the-icon-lexer-drops-its-ipp-pass-scrip-e-retires-and-a-directive-is-a-parse-error  fallback=['/home/claude_ceo'] b |
| test_gate_corpus_coverage_classified | blocking | RED | other | ⛔ GATE FAILED -- the corpus is not fully classified; see above. |
| test_gate_delimited_aggregate_census_ratchet | blocking | RED | other | arm 3 PASS: the planted joined-value site reads RED against the baseline, OTHER 0 -> 1, named by file and function arm 4 PASS: 3 declared non-member r |
| test_gate_demos_suite_grades_each_demo_in_both_modes | blocking | RED | other | REFUSES rc 2 and echoes nothing -- never a skip ok    (11) a blank line REFUSES rc 2 -- one unit per line, nothing else ok    (12) an absolute path RE |
| test_gate_dyn_caps_ratchet | blocking | RED | other | FAIL-ONCE: a declaration of only wrong rows names each RED and sets nothing aside -- the census reads the real counts plus what the real declaration s |
| test_gate_preflight_arms_stay_cheap | blocking | RED | other |  |
| test_gate_progress_configuration_declarations_do_not_regress | blocking | RED | other | FAIL [progress_configuration_ratchet]: 1 of 11 checks red -- the configuration record can regress with |
| test_gate_rungs_order_is_the_builders_order | blocking | RED | other | ⛔ GATE FAIL [rungs_order_is_the_builders_order]: 2 of 7 rung suite(s) not in the builder's order CURE: python3 scripts/util_build_rungs_suite.py --lan |
| test_gate_runners_refuse_on_a_stale_binary | blocking | RED | other | FAIL  gate(s) that execute ./scrip with NO freshness guard: test_gate_gc_one_stack_the_walker_sweeps_tagged_cells.sh test_gate_pas_an_unnamed_file_lea |
| test_gate_scrip_switches_are_spitbols | blocking | RED | other | FAIL) population: 26 arm(s), 1 FAIL GATE RED [test_gate_scrip_switches_are_spitbols]: 1 arm(s) failed |
| test_gate_pattern_operand_reentry | blocking | REFUSED | other | ⛔ REFUSE(rc=2): SELF-TEST DID NOT FAIL ON THE PRE-CURE LOWERING (0/2 arms went red). SCRIP_PB_ARGORDER=1 reproduces the interleaved eval/store chain a |
| test_gate_suite_runners_honour_the_tests_declared_memory | blocking | REFUSED | other | REFUSED rc=2 by name -- never read as 'no declaration' ok   H3 a program with no sidecar reads nothing (rc=0): the shipped default, not an error ok    |
| test_gate_every_runner_passes_the_declared_heap_and_stack | reported | RED | other | ⛔ GATE FAIL [every_runner_passes_the_declared_heap_and_stack]: 7 red (pairs that failed, and 7 family group(s) not yet fixtured) tree: SCRIP=ba10ba29f |
| test_gate_no_runner_types_a_size_or_sets_the_window | reported | RED | other | ⛔ GATE FAIL [no_runner_types_a_size_or_sets_the_window]: 1 of 6 check(s) failed tree: SCRIP=ba10ba29f corpus=38f66bd30 .github=4aef1bd6  measured 2026 |
| test_gate_parser_demos_match_bootstrap | reported | RED | other | FAIL(1) [parser_demos_match_bootstrap]: 7 of 7 present, stale or missing: parser_icon(drifted) -- run scripts/util_regen_parser_demos.sh |
| test_gate_readme_suite_table_matches_suites_tsv | reported | RED | other | FAIL(1) [readme_suite_table_matches_suites_tsv]: 1 arm(s) failed (the README suite table must be the render of .github/SUITES.tsv) (examined 5) tree:  |
| test_gate_score_tables_agree | reported | RED | other | ⛔ Note a DENOMINATOR IS NOT A POPULATION IDENTITY -- two different suites of the same size land under one key here, so a hit may be two unrelated suit |
| test_gate_monitor_grades_the_output_event | reported | REFUSED | other | ok    (4) a stream left longer at END DIVERGEs (byte 2: one side wrote a line the other never did) ok    (5) a participant without the hello leaves ou |

## cto -- 4 (4 blocking)

| gate | set | verdict | class | first failing line |
|---|---|---|---|---|
| test_gate_dump_zeta_guard_arm_reads_a_name_only_from_an_op_that_carries_one | blocking | RED | other | ⛔ the witness does not dump |
| test_gate_frame_det_leaf_seal_matches_the_emitter_registry | blocking | RED | other | ⛔ r/1 does not seal exactly its four $-leaves (five before rung 3(f) removed the head unify) ; detleaf 'r/1' sealed=3 emitted_direct=3 emitted_byname= |
| test_gate_frame_reuse_relation_names_every_recession_edge | blocking | RED | other | ⛔ GATE FAIL: 1 finding(s) -- the reuse relation does not name every recession edge it must |
| test_gate_no_zeta_frame_switches | blocking | RED | other | ⛔ FAIL: 2 zeta frame switch(es) under src/ -- the tier is DERIVED, never enumerated (RULES.md, CEO-447): src/emitter/emit.cpp:2465:getenv("SCRIP_LEAF_ |

## hq_icon -- 25 (23 blocking)

| gate | set | verdict | class | first failing line |
|---|---|---|---|---|
| test_gate_abandoned_generator_handle_is_dropped_at_alpha | blocking | RED | icon-semicolon | FAIL m3 det: nonzero exit (the abandoned-handle class died SIGABRT in pthread_create at n=60000) FAIL m3 det: answer drift, want 1 got / GATE ABANDONE |
| test_gate_frame_reuse_rung1_straight_temps_share_a_pool | blocking | RED | icon-semicolon | ⛔ w.icn mode 3 printed [icon: parse error in /tmp/tmp.RD8HTAyhlJ/w.icn: line 3: every statement: expected ';' after the token at line 2 col 25 (SCRIP  |
| test_gate_frame_reuse_rung2_det_leaf_argv_share_one_pool | blocking | RED | icon-semicolon | ⛔ the Icon builtin call read across the generator is not PINNED, or an unsealed graph grew a pooled argv block |
| test_gate_frame_reuse_rung3_staged_argv_are_never_addressed_so_never_granted | blocking | RED | icon-semicolon | ⛔ w.icn mode 3 printed [icon: parse error in /tmp/tmp.DhMHA93Vcp/w.icn: line 3: every statement: expected ';' after the token at line 2 col 32 (SCRIP  |
| test_gate_frame_reuse_rung3d_the_dead_result_scratch_overlays_a_pool_slot | blocking | RED | icon-semicolon | ⛔ fewer than three graphs overlay (r/1, main/0, $fc/3 and ,/2 did on the landing tree) ; grants TOTAL graphs=174 graded=173 refs=6285 findings=0 |
| test_gate_frame_reuse_rung3e_a_single_reader_temp_takes_its_sealed_calls_argv_slot | blocking | RED | icon-semicolon | ⛔ fewer than seven temps of r/1 marshal directly (nine before rung 3(f) removed the head unify and its two operands) (5) ; grants TOTAL graphs=174 gra |
| test_gate_frame_reuse_rung3f_a_first_occurrence_head_variable_is_its_param_slot | blocking | RED | icon-semicolon | ⛔ r/1 frame is 208 bytes, not under the row's 200 ; grants TOTAL graphs=174 graded=173 refs=6285 findings=0 |
| test_gate_heap_exhaustion_at_the_cap_is_a_reported_error_not_an_abort | blocking | RED | icon-semicolon | FAIL (4) Icon at the default cap: rc=1 stderr: icon: parse error in w.icn: line 3: every statement: expected ';' after the token at line 2 col 59 (SCR |
| test_gate_pl_wall_us_arity1 | blocking | RED | icon-semicolon | FAIL  the arity-0 form stopped answering in ICON -- got: icon: parse error in /tmp/tmp.ZeESa11d6W/a0.icn: line 4: if statement: expected ';' after the |
| test_gate_icn_dump_ast_shows_the_parsed_program_and_pruning_stays_a_lowering_step | blocking | RED | other | FAIL (a cross-language callee is still dropped: mode-3 (--run):     PASS=0 FAIL=2   (HARD GATE) / mode-4 (--compile): PASS=0 FAIL=2   (HARD GATE)) GAT |
| test_gate_icn_ipl_declared_status_and_empty_output_are_graded | blocking | RED | other | FAIL (a) green: MINTED=0 M3=FAIL M4=FAIL REF=- FAIL (c) green: MINTED=0 M3=FAIL M4=FAIL REF=- |
| test_gate_icn_ipl_env_sidecar_reaches_the_oracle_and_both_modes | blocking | RED | other | FAIL green: MINTED=0 M3=FAIL M4=FAIL REF=- FAIL green: the ref does not carry the sidecar's values: |
| test_gate_icn_ipl_fixtures_stage_subdirectories_and_dotfiles | blocking | RED | other | FAIL green: MINTED=0 M3=FAIL M4=FAIL REF=- FAIL green: the ref does not carry the staged tree: |
| test_gate_icn_ipl_m4_run_ends_the_runtime_switches_before_the_programs_argv | blocking | RED | other | FAIL (b) green: MINTED=0 M3=FAIL M4=FAIL REF=- FAIL (c): no m4 binary to probe |
| test_gate_icn_ipl_outfiles_sidecar_grades_the_files_a_program_writes | blocking | RED | other | FAIL green: MINTED=0 M3=FAIL M4=FAIL REF=- FAIL green: the ref does not carry the written file: |
| test_gate_icn_ipl_pin_sidecar_fixes_the_clock_and_entropy_for_both_participants | blocking | RED | other | FAIL green: MINTED=0 M3=FAIL M4=FAIL REF=- FAIL green: the ref does not carry the pinned date: |
| test_gate_icn_ipl_pty_sidecar_runs_the_unit_on_a_terminal | blocking | RED | other | FAIL green: MINTED=0 M3=FAIL M4=FAIL REF=- FAIL green: the ref does not say the unit ran on a terminal: |
| test_gate_icn_if_without_else_invocable_arity_and_string_continuation | blocking | REFUSED | icon-semicolon | ⛔ REFUSED(2): oracle itself failed on if_noelse_taken (rc=1) -- the case is malformed, not the compiler |
| test_gate_icn_rundir_contract | blocking | REFUSED | icon-semicolon | ⛔ GATE REFUSES(2): rung36_jcon_btrees: the oracle would not compile -- File /home/claude_coo/corpus/tests/icon/rung36_jcon_btrees.icn; Line 22 # "end" |
| test_gate_icn_scan_find_and_match_carry_a_literals_length | blocking | REFUSED | icon-semicolon | ⛔ GATE REFUSE(2) [test_gate_icn_scan_find_and_match_carry_a_literals_length]: icont refuses witness w1 (find "\x00") |
| test_gate_int64_min_divided_by_minus_one_dies_of_no_signal_in_any_frontend | blocking | REFUSED | icon-semicolon | REFUSE(2) [int64_min_divided_by_minus_one_dies_of_no_signal_in_any_frontend]: icont/iconx could not run the Icon witness |
| test_gate_icn_a_clib_sidecar_builds_the_library_a_program_loads | blocking | REFUSED | other | ⛔ GATE REFUSE(2) [test_gate_icn_a_clib_sidecar_builds_the_library_a_program_loads]: the oracle did not answer 4244 through the fixture library: |
| test_gate_icn_call_traces_its_call_line_exactly_once | blocking | REFUSED | other | REFUSE(2) [icn_call_traces_its_call_line_exactly_once]: oracle could not build or run arity 1 -- cannot measure |
| test_gate_icn_rbp_census_ratchet | reported | RED | other | FAIL: RATCHET C_data=25444 > baseline=25391 (+53). |
| test_gate_icn_scrip_does_not_preprocess | reported | RED | other | FAIL icon_lex.c still carries the ipp port (102 lines name icn_pp_text or ipp_) FAIL scrip -E still preprocesses (rc=0, output: #line 0 "w.icn"  proce |

## hq_pascal -- 1 (0 blocking)

| gate | set | verdict | class | first failing line |
|---|---|---|---|---|
| test_gate_pas_port_trace | reported | RED | port-trace |  |

## hq_prolog -- 5 (5 blocking)

| gate | set | verdict | class | first failing line |
|---|---|---|---|---|
| test_gate_pl_a_predicate_with_more_than_64_clauses_keeps_every_clause | blocking | RED | other | ok  static70 m3 |
| test_gate_pl_only_tree_t_crosses_parser_to_lower | blocking | RED | other | arm 6 GREEN: a planted census reds on all six arms by name |
| test_gate_pl_print_1_honours_portray_and_costs_nothing_without_it | blocking | RED | other | ⛔ ARM 5 UNPROVEN: could not read maxrss for both runs (lo=[] hi=[]) -- an arm that cannot measure is no |
| test_gate_pl_swi_every_shipped_case_is_graded_by_path | blocking | RED | other | ok  no top-level duplicate of a subdirectory test file build-behaviour probe [test_gate_pl_swi_every_shipped_case_is_graded_by_path]: consistent -- tr |
| test_gate_pl_swi_shim_runs_a_forall_test_per_instance | blocking | RED | other |  |

## hq_raku -- 2 (0 blocking)

| gate | set | verdict | class | first failing line |
|---|---|---|---|---|
| test_gate_raku_aggregates_are_typed_storage | reported | RED | other | FAIL nest  m3: got [4 1 Nil 0 1 7 1 0 0] want [2 2 3 2 3 7 2 0 3 ] FAIL nest  m4: got [4 1 Nil 0 1 7 1 0 0] want [2 2 3 2 3 7 2 0 3 ] GATE FAIL(1) [ra |
| test_gate_raku_port_trace | reported | RED | port-trace |  |

## hq_snobol4 -- 14 (10 blocking)

| gate | set | verdict | class | first failing line |
|---|---|---|---|---|
| test_gate_harness_renders_a_spitbol_fatal_into_stdout | blocking | RED | other | ⛔ GATE FAIL [harness_renders_a_spitbol_fatal_into_stdout]: 4 of 9 check(s) failed tree: SCRIP=ba10ba29f corpus=38f66bd30 .github=4aef1bd6  measured |
| test_gate_sno_a_dynamic_function_called_from_a_code_built_function_returns_its_value | blocking | RED | other | FAIL arm 4  MONITOR: the witness agrees with the SPITBOL fork to its end -- rc=1: / **>**2561 / 95 / @95 VALUE NULL = STRING(0)='' / @95 RETURN NULL ( |
| test_gate_sno_by_name_paths_find_once_dollar_apply_eval | blocking | RED | other | FAILED: s |
| test_gate_sno_lastno_updates_on_every_plain_statement | blocking | RED | other | FAIL(1) [test_gate_sno_lastno_updates_on_every_plain_statement.sh]: 2 mode(s) whose &LASTNO/&LASTLINE do not advance across plain statements with no c |
| test_gate_sno_match_region_watermark_is_spent_on_every_exit_edge | blocking | RED | other | FAIL CONTROL  ctl_numeric_while  [non-local edge, NO match]  rc=1  want=[done] got=[/tmp/tmp.Ln6kCfmc74/ctl_numeric_while.sc] ^ CONTROL -- this shape  |
| test_gate_sno_rewind_on_an_unopened_unit_raises_174 | blocking | RED | other | FAIL=2  (expectation cut from /home/resources/x64/bin/sbl -bf at run time; SCRIP's own voice rendered through util_render_error_voice.py spitbol, neve |
| test_gate_sno_sort_and_rsort_answer_as_spitbol_does | blocking | RED | other | FAIL arm 3  m3: csnobol4_suite tab.sno stops with 256 at sbl's line and statement -- got [total words: 271/ERROR 256//14] want [total words: 271/ERROR |
| test_gate_sno_trace_of_an_array_or_table_element_fires_and_spells_it_like_the_oracle | blocking | RED | other |  |
| test_gate_testpgms_grades_a_spitbol_post_mortem_through_the_one_error_voice | blocking | RED | other | ok   H6 |
| test_gate_sno_the_real_model_is_spitbols_gtnum_reading_and_ftz_daz_arithmetic | blocking | REFUSED | other | ok   3 EVAL('3.0E-324') is 0. and ...316 is finite (math_limits' witness) ok   4 m3 arithmetic == sbl (7 lines: flushed quotient, folded quotient, DAZ |
| test_gate_sno_parser_refuses_at_compile_time_what_spitbol_refuses | reported | RED | other | ⛔ literal-target: SCRIP parser ACCEPT, SPITBOL compile REFUSE  [OUTPUT = 'a' = X] |
| test_gate_sno_recede_free_stored_pattern_runs_on_the_rsp_spine | reported | RED | other | FAIL PAT$0 is recede-free and still carves an RBP frame (1 frame prologue(s)) PASS PAT$1 (an alternation, a recede window) keeps its frame PASS PAT$2  |
| test_gate_snobol4_xfail_markers_are_attributed | reported | RED | other | ⛔ 5 of 5 xfail entries carry no usable route -- unresolvable by name. |
| test_gate_sno_port_trace_oracle_diff | reported | REFUSED | port-trace |  |

## hq_snocone -- 3 (0 blocking)

| gate | set | verdict | class | first failing line |
|---|---|---|---|---|
| test_gate_snocone_expressions_are_snobol4_expressions | reported | RED | other | OPEN A & B              Snocone refuses where SPITBOL accepts  [row: snocone-binary-opsyn-operators-parse-like-snobol4-and-spitbol-and-dispatch-throug |
| test_gate_reb_port_trace | reported | RED | port-trace |  |
| test_gate_sc_port_trace | reported | RED | port-trace |  |

