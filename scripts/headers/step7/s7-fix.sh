#!/usr/bin/env bash
set -u
S4=/tmp/claude-1000/-home-claude-cto/b1caac4c-9b75-4393-9260-1c72f906f86b/scratchpad; SO=/tmp/claude-1000/-home-claude-cto/25cbd82c-ea4e-46bc-9ee6-3c52fc5dcc1f/scratchpad; W=$SO/hdr/SCRIP; HW=$SO/hdr/harness; HS=$HW/scripts; cd $W || exit 2
python3 -I $S4/hdr7b.py $W || exit 2
grep -c 'pl_trail_layout.h' src/templates/bb/bb_unify_const.cpp src/templates/xa/xa_flat.cpp src/runtime/by_name_dispatch.c | tr '\n' ' '; echo
make -j8 > $S4/s7-build3.log 2>&1; echo "build rc=$? errors=$(grep -c ' error:' $S4/s7-build3.log)"; grep ' error:' $S4/s7-build3.log | sed 's|^.*/src/|src/|' | head -5 | cut -c1-160
[ "$(grep -c ' error:' $S4/s7-build3.log)" = 0 ] || exit 2
git -C $HW checkout -- scripts/header_fanin.baseline.tsv && echo "HW baseline restored to origin's"
echo "== the gate against origin's baseline"; S4E_DONE_WHEN_RUN=1 bash $HS/test_gate_no_header_reaches_more_units_than_its_users.sh > $S4/s7-gate3.log 2>&1; echo "gate rc=$?"; grep -E '^  (RED|ok) +ARM [1-5]|RAISED|^GATE' $S4/s7-gate3.log | cut -c1-140
echo "== the layout and the Pascal header now"; python3 -I $HS/util_header_fanin.py --root $W 2>/dev/null | awk -F'\t' '$7 ~ /pl_trail_layout.h|lower_pascal_tree.h|rt_pl_trail.h|g_lower.h|datatype.h/' | cut -c1-120
echo "== lower the baseline"; python3 -I $HS/util_header_fanin.py --root $W --write-baseline 2>&1 | tail -1 | cut -c1-160; git -C $HW diff --stat -- scripts/header_fanin.baseline.tsv | tail -1
echo "== the gate after"; S4E_DONE_WHEN_RUN=1 bash $HS/test_gate_no_header_reaches_more_units_than_its_users.sh > $S4/s7-gate4.log 2>&1; echo "gate rc=$?"; grep -E '^  (RED|ok) +ARM|^GATE' $S4/s7-gate4.log | cut -c1-140
grep -c 'test_gate_no_header_reaches_more_units_than_its_users' Makefile | sed 's/^/Makefile names the gate: /'
echo "FIX7 DONE $(date +%T)"
bash $S4/apply7-proof.sh > $S4/apply7-proof.log 2>&1; echo "proof rc=$?"
