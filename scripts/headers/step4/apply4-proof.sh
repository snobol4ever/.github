#!/usr/bin/env bash
# the step-4 proof (the step-3 shape): pristine cache-off rebuild at the work path, the amended DONE-WHEN, R5-prime against the 75a5a69a9 objects, readings, style, the implicit-declaration pass, the smokes, the gates
S4=/tmp/claude-1000/-home-claude-cto/b1caac4c-9b75-4393-9260-1c72f906f86b/scratchpad; SO=/tmp/claude-1000/-home-claude-cto/25cbd82c-ea4e-46bc-9ee6-3c52fc5dcc1f/scratchpad; W=$SO/hdr/SCRIP; H=$SO/hdr/harness/scripts; cd $W || exit 2
echo "== 0 a full cache-free rebuild (pristine) so the objects are the tree's  $(date +%T)"
CCACHE_DISABLE=1 S4E_NO_BUILD_CACHE=1 make -j8 pristine > $S4/work4-pristine.log 2>&1; echo "pristine rc=$? compiles=$(grep -c -- ' -c ' $S4/work4-pristine.log) errors=$(grep -c ' error' $S4/work4-pristine.log)"
echo "== 1 DONE-WHEN (amended text in $S4/dw4.sh)"
S4E_HOME=$SO/hdr bash $S4/dw4.sh 2>&1 | tail -2 | cut -c1-240
echo "== 2 R5-prime against the 75a5a69a9 objects (same path, cache off)"
WO=/tmp/si_objs$(printf %s "$W" | tr / -)
bash $H/util_objects_identical_stripped.sh --no-comdat --moved $S4/hdr4_moved.txt $SO/parent-objs-step4/obj $WO $SO/parent-objs-step4/out $W/out > $S4/r5-step4.log 2>&1; echo "R5-prime rc=$? :: $(grep '^objects=' $S4/r5-step4.log | cut -c1-220)"; grep -E '^(DIFF|ONLY)' $S4/r5-step4.log | head -20 | cut -c1-200
echo "== 3 readings"
python3 -I $H/util_header_fanin.py --root $W 2>/dev/null | awk -F'\t' 'NR==1 || $7 ~ /^ir\/(ir_|bb_box|bb_program|stage2|SM)|^planner\/|emitter\/emit_regime|emitter\/emit_state|emitter\/emit\.h|lower_common|gen_runtime|call_forms|ir_index|zeta_depth/' | cut -c1-120
echo "== 4 style on every touched src file"
files=$(git diff --name-only HEAD -- src | grep -E '\.(c|cpp|h|inc)$' | while read f; do [ -f "$f" ] && echo "$f"; done; git ls-files --others --exclude-standard src | grep -E '\.(c|cpp|h|inc)$')
python3 ../harness/scripts/util_reflow_200.py --check $files 2>&1 | tail -1 | cut -c1-160; python3 ../harness/scripts/strip_comments.py --check $files 2>&1 | tail -1 | cut -c1-160
echo "== 5 implicit declarations (the parent carries 12; anything more is this landing's)"
CCACHE_DISABLE=1 S4E_NO_BUILD_CACHE=1 make -B -k -j8 WARN="-Werror=implicit-function-declaration -Werror=implicit-int" build-all > $S4/mkw4-work.log 2>&1; echo "diag rc=$? implicit=$(grep -c 'implicit declaration' $S4/mkw4-work.log)"; grep -oE "[^ /]+\.(c|cpp):[0-9]+:[0-9]+: error: implicit declaration of function ‘[^’]+’" $S4/mkw4-work.log | sort -u | cut -c1-120
CCACHE_DISABLE=1 S4E_NO_BUILD_CACHE=1 make -j8 pristine > $S4/work4-pristine2.log 2>&1; echo "pristine again rc=$?"
echo "== 6 smokes  $(date +%T)"
for l in snobol4 snocone rebus icon prolog pascal raku scrip_all_modes; do S4E_DONE_WHEN_RUN=1 timeout -k 5 1800 bash ../harness/scripts/test_smoke_$l.sh > $S4/smoke4-$l.log 2>&1; echo "SMOKE $l rc=$?"; done
echo "== 7 gates  $(date +%T)"
for g in test_gate_no_header_reaches_more_units_than_its_users.sh test_gate_mint_op_is_one_numbering.sh test_gate_stage2_isolation.sh test_gate_one_retains_table.sh test_gate_planner_objects_leave_no_emitter_symbol_undefined.sh test_gate_planner_six_passes_read_no_emitter_state.sh test_gate_zd_omega_head_acceptance.sh test_gate_zd_a_back_edge_leaves_a_blob_run_and_alternation_arms_stay_unplanned.sh test_gate_zd_check_reads_zero_violations_on_the_cores.sh test_gate_frame_layout_retires_a_dead_graphs_record.sh test_gate_dyn_caps_ratchet.sh test_gate_no_script_passes_a_retired_include_directory.sh test_gate_bb_label_no_silent_truncation.sh test_gate_fb_adopt_one_predicate.sh test_gate_emit_fields_read_by_a_template_have_a_writer.sh test_gate_template_medium_invisible.sh test_gate_core_fn_table_is_current.sh test_gate_pl_trail_mechanism.sh test_gate_gc_map_table_present_in_both_media.sh test_gate_no_rsp_reset_at_beta.sh test_gate_gc_every_safe_point_has_a_compile_time_frame_shape.sh test_gate_icn_tag_single_source.sh test_gate_sno_statement_mark_mode_releases_the_hook_residue_before_the_statement.sh; do f=../harness/scripts/$g; [ -f "$f" ] || { echo "GATE $g: missing"; continue; }; t0=$(date +%s); S4E_DONE_WHEN_RUN=1 timeout -k 5 1800 bash $f > $S4/gate4-$g.log 2>&1; echo "GATE $g rc=$? $(( $(date +%s) - t0 ))s :: $(grep -E 'GATE (OK|PASS|FAIL|RED|GREEN|UNPROVEN)|⛔|REFUSE' $S4/gate4-$g.log | tail -1 | cut -c1-110)"; done
grep -E '^  (RED|ok) ' $S4/gate4-test_gate_no_header_reaches_more_units_than_its_users.sh.log | cut -c1-160
echo "APPLY4 PROOF DONE $(date +%T)"
