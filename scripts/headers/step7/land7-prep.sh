#!/usr/bin/env bash
# step 7 on the landed 6C tree: the parent objects are the 6C proof's pristine build of W (the same content as the landed commit), then the cures, the harness side, the build, the gate, the baseline, the Makefile line, the proof
set -u
S4=/tmp/claude-1000/-home-claude-cto/b1caac4c-9b75-4393-9260-1c72f906f86b/scratchpad; SO=/tmp/claude-1000/-home-claude-cto/25cbd82c-ea4e-46bc-9ee6-3c52fc5dcc1f/scratchpad; W=$SO/hdr/SCRIP; HS=$SO/hdr/harness/scripts; cd $W || exit 2
git fetch -q origin; [ -z "$(git status --short)" ] && [ "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)" ] || { echo "REFUSE: W is not the clean landed tree"; git status --short | head -3; exit 2; }
WO=/tmp/si_objs$(printf %s "$W" | tr / -); rm -rf $S4/parent-objs-7; mkdir -p $S4/parent-objs-7/obj $S4/parent-objs-7/out && cp $WO/*.o $S4/parent-objs-7/obj/ && cp -r $W/out/rt_pic-* $S4/parent-objs-7/out/ && echo "parent objects (the 6C pristine build): $(ls $S4/parent-objs-7/out/rt_pic-*/*.o | wc -l) + $(ls $S4/parent-objs-7/obj | wc -l)"
git -C $SO/hdr/harness fetch -q origin && git -C $SO/hdr/harness checkout -q --detach origin/main && echo "harness worktree at $(git -C $SO/hdr/harness rev-parse --short HEAD)"
git checkout -q -B cto-headers-7-wip origin/main && echo "W on $(git branch --show-current) at $(git rev-parse --short HEAD)"
python3 -I $S4/hdr7.py $W --apply || exit 2
python3 -I $S4/hdr7_harness.py $HS || exit 2
make -j8 > $S4/s7-build1.log 2>&1; echo "build rc=$? errors=$(grep -c ' error:' $S4/s7-build1.log)"; grep ' error:' $S4/s7-build1.log | sed 's|^.*/src/|src/|' | head -5 | cut -c1-160
echo "== the gate before the baseline"; S4E_DONE_WHEN_RUN=1 bash $HS/test_gate_no_header_reaches_more_units_than_its_users.sh > $S4/s7-gate1.log 2>&1; echo "gate rc=$?"; grep -E '^  (RED|ok|FAIL) +ARM|RAISED|^GATE' $S4/s7-gate1.log | cut -c1-140
echo "== over-ceiling headers now"; python3 -I $HS/util_header_fanin.py --root $W --ceiling 2>/dev/null | tail -3 | cut -c1-140
echo "== lower the baseline to this tree"; python3 -I $HS/util_header_fanin.py --root $W --write-baseline 2>&1 | tail -2 | cut -c1-160; git -C $SO/hdr/harness diff --stat -- scripts/header_fanin.baseline.tsv | tail -1
echo "== the gate after the baseline"; S4E_DONE_WHEN_RUN=1 bash $HS/test_gate_no_header_reaches_more_units_than_its_users.sh > $S4/s7-gate2.log 2>&1; echo "gate rc=$?"; grep -E '^  (RED|ok|FAIL) +ARM|RAISED|^GATE' $S4/s7-gate2.log | cut -c1-140
echo "== the Makefile line"; python3 - <<'PY'
p='/tmp/claude-1000/-home-claude-cto/25cbd82c-ea4e-46bc-9ee6-3c52fc5dcc1f/scratchpad/hdr/SCRIP/Makefile'; t=open(p).read()
anchor='\tbash ../harness/scripts/test_gate_batch_scripts_run_in_the_batch_slice.sh'; i=t.index(anchor); j=t.index('\n', i)+1
assert 'test_gate_no_header_reaches_more_units_than_its_users' not in t
line='\tbash ../harness/scripts/test_gate_no_header_reaches_more_units_than_its_users.sh   # ~9s MEASURED (cto 2026-10-31, step 7 of ARCH-HEADER-SPLIT, CEO-2032): THE HEADER CEILING (R4): no header outside the base set reaches more units than its users plus four, no umbrella, no multi-statement inline body outside the allowed list, no bare cross-directory include, no unused direct include; a ratchet against header_fanin.baseline.tsv, lowered and never raised\n'
open(p,'w').write(t[:j]+line+t[j:]); print('Makefile: the ceiling gate joins make test after the batch gate')
PY
echo "PREP7 DONE $(date +%T)"
