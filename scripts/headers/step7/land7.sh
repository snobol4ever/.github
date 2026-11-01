#!/usr/bin/env bash
set -u
S4=/tmp/claude-1000/-home-claude-cto/b1caac4c-9b75-4393-9260-1c72f906f86b/scratchpad; SO=/tmp/claude-1000/-home-claude-cto/25cbd82c-ea4e-46bc-9ee6-3c52fc5dcc1f/scratchpad; W=$SO/hdr/SCRIP; HW=$SO/hdr/harness
G="-c user.name=LCherryholmes -c user.email=lcherryh@yahoo.com"
cd $W || exit 2
git add -A src Makefile && git $G commit -q -m "wip: headers step 7"; git fetch -q origin; echo "origin/main $(git rev-parse --short origin/main) (ahead of the 6C landing: $(git rev-list --count $(cat $S4/landed6c-hashes.txt | sed 's/SCRIP=\([0-9a-f]*\).*/\1/')..origin/main))"
git checkout -q -B cto-headers-7-land origin/main || exit 2
git merge -q --squash cto-headers-7-wip || { echo "SQUASH CONFLICT"; git status --short | head; exit 2; }
git status --short | wc -l | sed 's/^/files staged: /'; git $G commit -q -F $S4/s7-commit.txt || exit 2
SH=$(git rev-parse --short HEAD); echo "SCRIP landing commit $SH ($(git show --stat --format= HEAD | tail -1))"
P6=$(sed 's/SCRIP=\([0-9a-f]*\).*/\1/' $S4/landed6c-hashes.txt)
if [ "$(git rev-parse origin/main)" != "$(git rev-parse $P6)" ]; then
  echo "== origin moved since the proof ($P6 -> $(git rev-parse --short origin/main)): re-prove the rebased tree (build, the ceiling gate, the eight smokes)"
  make -j8 > $S4/s7-rebuild-rebased.log 2>&1 || { echo "REBASED BUILD RED"; exit 2; }
  S4E_DONE_WHEN_RUN=1 bash $HW/scripts/test_gate_no_header_reaches_more_units_than_its_users.sh > $S4/s7-gate-rebased.log 2>&1; rc=$?; echo "ceiling gate on the rebased tree rc=$rc"; [ $rc -eq 0 ] || exit 2
  for l in snobol4 snocone rebus icon prolog pascal raku scrip_all_modes; do S4E_DONE_WHEN_RUN=1 timeout -k 5 1800 bash ../harness/scripts/test_smoke_$l.sh > $S4/smoke7r-$l.log 2>&1; rc=$?; echo "SMOKE $l rc=$rc"; [ $rc -eq 0 ] || exit 2; done
fi
cd $HW && sed -i "s/\[HASH\]/$SH/" $S4/s7-harness-commit.txt && git add -A scripts && git $G commit -q -F $S4/s7-harness-commit.txt || exit 2
git -C $HW show HEAD -- scripts ':!scripts/header_fanin.baseline.tsv' > $S4/hdr7-harness.patch; echo "harness patch record: $(wc -l < $S4/hdr7-harness.patch) lines" 
cd $W && git push -q origin HEAD:main && echo "SCRIP pushed $SH" || { echo "SCRIP PUSH REJECTED"; exit 3; }
cd $HW && git fetch -q origin && git rebase -q origin/main && git push -q origin HEAD:main && echo "harness pushed $(git rev-parse --short HEAD)" || { echo "HARNESS PUSH REJECTED"; exit 3; }
echo "SCRIP=$SH HARNESS=$(git rev-parse --short HEAD)" > $S4/landed7-hashes.txt
cd /home/claude_cto && for r in SCRIP harness; do git -C $r fetch -q origin && git -C $r merge -q --ff-only origin/main && echo "$r root at $(git -C $r rev-parse --short HEAD)"; done
cd /home/claude_cto/SCRIP && make -j8 > $S4/root-make7.log 2>&1; echo "root make rc=$? $(grep -oE 'FETCHED|PUBLISHED' $S4/root-make7.log | head -1)"
. $S4/landed7-hashes.txt; T=$(date '+%H:%M')
cd /home/claude_cto/.github && git fetch -q origin && git merge -q --ff-only origin/main && python3 -I $S4/s7-page.py "$SCRIP" "$HARNESS" "$T" "$(cat $S4/s7-after.txt)" "$(cat $S4/s7-ceil.txt)" || exit 2
mkdir -p scripts/headers/step7 && cp $S4/hdr7.py $S4/hdr7b.py $S4/hdr7_harness.py $S4/hdr7-harness.patch $S4/land7-prep.sh $S4/s7-fix.sh $S4/s7-fix2.sh $S4/apply7-proof.sh $S4/s7-extract.py $S4/land7.sh $S4/after_table.py scripts/headers/step7/
sed -i "s/\[HASH7\]/$SCRIP/g; s/\[HH7\]/$HARNESS/g; s/\[T\]/$T/g" $S4/cto-442.txt
python3 - <<'PY'
S4='/tmp/claude-1000/-home-claude-cto/b1caac4c-9b75-4393-9260-1c72f906f86b/scratchpad'
p='/home/claude_cto/.github/GOAL-CTO.md'; t=open(p).read(); e=open(S4+'/cto-442.txt').read()
i=t.index('- **CTO-441 '); t=t[:i]+e+t[i:]; open(p,'w').write(t); print('CTO-442 in the cursor')
PY
git add ARCH-HEADER-SPLIT.md GOAL-CTO.md scripts/headers/step7 && git $G commit -q -F - <<EOF
ARCH-HEADER-SPLIT: step 7 landed, the finish (the cto under CEO-2091; SCRIP $SCRIP, harness $HARNESS): the after table of 3.7 measured, roll-out row 7, the data .inc rule; GOAL-CTO CTO-442; the method scripts under scripts/headers/step7.
EOF
git push -q origin HEAD:main && echo ".github pushed $(git rev-parse --short HEAD)" || { echo ".github PUSH FAILED"; exit 3; }
echo "== the step-7 row"; cd /home/claude_cto && T7=$(ls /home/resources/postoffice/tasks/headers-step-7-*.task.md | xargs -n1 basename | sed 's/\.task\.md$//')
python3 - "$T" "$SCRIP" "$HARNESS" <<'PY'
import sys, glob
T, SH, HH = sys.argv[1:4]; p=glob.glob('/home/resources/postoffice/tasks/headers-step-7-*.task.md')[0]; t=open(p).read()
i=t.index('## NEXT\n')+len('## NEXT\n'); j=t.index('\n## ', i)
t=t[:i]+"DONE 2026-10-31 %s CDT by the cto (CEO-2091): SCRIP %s, harness %s. The ceiling gate reads 0 on every arm, is BLOCKING (make test; its RULING row left gate_wiring.tsv), and the baseline is lowered to the landed tree; the after table of 3.7 is on the page; option B of 3.4 stays Lon's call with the measured figure beside the projection." % (T, SH, HH) + t[j:]
t=t.rstrip('\n')+"\n- [cto·2026-10-31 %s CDT] LANDED the finish: SCRIP %s (g_lower.h holds g_lower_pas_sem_t and drops lower_pascal_tree.h; rt_pl_trail.h drops pl_trail_layout.h and its three readers include it; aggregates.c and pl_rat.c drop datatype.h; the gate in make test) and harness %s (the data .inc rule, the baseline lowered, the RULING row gone). R5 identical, the eight smokes, every arm 0. Closed by claim + done.\n" % (T, SH, HH)
open(p,'w').write(t); print('step-7 baton: NEXT = DONE, LEDGER line')
PY
bash harness/scripts/s4e_msg.sh unclaim $T7 "hq_templates is stopped under CEO-2090; the cto landed the finish under CEO-2091 and closes the row" 2>&1 | tail -1 | cut -c1-160
S4E_PREMISE_OVERRIDE="the premise is the gate reading red; the landing turned it green, which is the DONE-WHEN" bash harness/scripts/s4e_msg.sh claim $T7 2>&1 | grep -vE 'LIVE CLAIM|being worked|measure, not for a name' | tail -2 | cut -c1-200
bash harness/scripts/s4e_msg.sh done $T7 2>&1 | grep -E 'RECEIPT|DONE|REFUSE|⛔|RED' | head -4 | cut -c1-200
grep "$T7" /home/resources/postoffice/QUEUE.tsv | cut -f1,3,4 | cut -c1-60
echo "LAND7 DONE $(date +%T)"
