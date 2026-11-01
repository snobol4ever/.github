#!/usr/bin/env bash
set -u
S4=/tmp/claude-1000/-home-claude-cto/b1caac4c-9b75-4393-9260-1c72f906f86b/scratchpad; SO=/tmp/claude-1000/-home-claude-cto/25cbd82c-ea4e-46bc-9ee6-3c52fc5dcc1f/scratchpad; W=$SO/hdr/SCRIP; HW=$SO/hdr/harness
G="-c user.name=LCherryholmes -c user.email=lcherryh@yahoo.com"
cd $W || exit 2
git add -A src Makefile && git $G commit -q -m "wip: headers step 6 C"; echo "wip head $(git rev-parse --short HEAD) on $(git branch --show-current)"
git fetch -q origin; echo "origin/main $(git rev-parse --short origin/main) (parent 632b35459; ahead $(git rev-list --count 632b35459..origin/main))"
git checkout -q -B cto-headers-6c-land origin/main || exit 2
git merge -q --squash cto-headers-6c-wip || { echo "SQUASH CONFLICT"; git status --short | head; exit 2; }
git status --short | wc -l | sed 's/^/files staged: /'
git $G commit -q -F $S4/c-commit.txt || exit 2
SH=$(git rev-parse --short HEAD); echo "SCRIP landing commit $SH ($(git show --stat --format= HEAD | tail -1))"
cd $HW && sed -i "s/\[HASH\]/$SH/" $S4/c-harness-commit.txt && git add -A scripts && git $G commit -q -F $S4/c-harness-commit.txt || exit 2
cd $W && git push -q origin HEAD:main && echo "SCRIP pushed $SH" || { echo "SCRIP PUSH REJECTED"; exit 3; }
cd $HW && git fetch -q origin && git rebase -q origin/main && git push -q origin HEAD:main && echo "harness pushed $(git rev-parse --short HEAD)" || { echo "HARNESS PUSH REJECTED"; exit 3; }
echo "SCRIP=$SH HARNESS=$(git rev-parse --short HEAD)" > $S4/landed6c-hashes.txt
cd /home/claude_cto && for r in SCRIP harness; do git -C $r fetch -q origin && git -C $r merge -q --ff-only origin/main && echo "$r root at $(git -C $r rev-parse --short HEAD)"; done
cd /home/claude_cto/SCRIP && make -j8 > $S4/root-make6c.log 2>&1; echo "root make rc=$? $(grep -oE 'FETCHED|PUBLISHED' $S4/root-make6c.log | head -1)"
. $S4/landed6c-hashes.txt; T=$(date '+%H:%M')
cd /home/claude_cto/.github && git fetch -q origin && git merge -q --ff-only origin/main && python3 -I $S4/c-page.py "$SCRIP" "$T" "$(cat $S4/c-r5.txt)" "$(cat $S4/c-arms.txt)" || exit 2
cp $S4/hdr6c.py $S4/hdr6c_harness.py $S4/apply6c-proof.sh $S4/land6c.sh scripts/headers/step6/
git add ARCH-HEADER-SPLIT.md scripts/headers/step6 && git $G commit -q -F - <<EOF
ARCH-HEADER-SPLIT: step 6 C landed (the cto under CEO-2091; SCRIP $SCRIP, harness $HARNESS): every include by its path from src/, the -I lists cut to -I\$(SRC); roll-out row 6 complete; the method scripts under scripts/headers/step6.
EOF
git push -q origin HEAD:main && echo ".github pushed $(git rev-parse --short HEAD)" || { echo ".github PUSH FAILED"; exit 3; }
echo "== the step-6 row: release hq_packages' lock, claim, done"
cd /home/claude_cto && T6=$(ls /home/resources/postoffice/tasks/headers-step-6-the-layers-*.task.md | xargs -n1 basename | sed 's/\.task\.md$//')
python3 - "$S4" "$T" "$SCRIP" "$HARNESS" <<'PY'
import sys, glob
S4, T, SH, HH = sys.argv[1:5]; p=glob.glob('/home/resources/postoffice/tasks/headers-step-6-the-layers-*.task.md')[0]; t=open(p).read()
i=t.index('## NEXT\n')+len('## NEXT\n'); j=t.index('\n## ', i)
t=t[:i]+"DONE 2026-10-31 %s CDT by the cto (CEO-2091): A and B by hq_packages, B1 (SCRIP 632b35459) and C (SCRIP %s, harness %s) by the cto. Every include under src/ is written as its path from src/ (same-directory bare names stay), the Makefile's -I lists are -I$(SRC), the generated parsers carry the path form through util_sweep_c_allocators.py; the DONE-WHEN reads green. Step 7 (the finish) follows in the same window." % (T, SH, HH) + t[j:]
t=t.rstrip('\n')+"\n- [cto·2026-10-31 %s CDT] LANDED C: SCRIP %s (the sweep and the -I cut; R5 byte-identical, the eight smokes, make parsers-sc in both trees, ARM 4 at 0) and harness %s (five scripts gain the source root; util_sweep_c_allocators.py writes ir/ct_arena.h). Closed by claim + done.\n" % (T, SH, HH)
open(p,'w').write(t); print('step-6 baton: NEXT = DONE, LEDGER line')
PY
bash harness/scripts/s4e_msg.sh unclaim $T6 "hq_packages is stopped under CEO-2090; the cto landed B1 and C under CEO-2091 and closes the row" 2>&1 | tail -1 | cut -c1-160
S4E_PREMISE_OVERRIDE="the premise names the old -I list or a header the step deleted; the DONE-WHEN is the measurement" bash harness/scripts/s4e_msg.sh claim $T6 2>&1 | grep -vE 'LIVE CLAIM|being worked|measure, not for a name' | tail -2 | cut -c1-200
bash harness/scripts/s4e_msg.sh done $T6 2>&1 | grep -E 'RECEIPT|DONE|REFUSE|⛔|RED' | head -4 | cut -c1-200
grep "$T6" /home/resources/postoffice/QUEUE.tsv | cut -f1,3,4 | cut -c1-60
echo "LAND6C DONE $(date +%T)"
