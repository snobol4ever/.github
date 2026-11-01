#!/usr/bin/env bash
set -u
S4=/tmp/claude-1000/-home-claude-cto/b1caac4c-9b75-4393-9260-1c72f906f86b/scratchpad; SO=/tmp/claude-1000/-home-claude-cto/25cbd82c-ea4e-46bc-9ee6-3c52fc5dcc1f/scratchpad; W=$SO/hdr/SCRIP; HW=$SO/hdr/harness
G="-c user.name=LCherryholmes -c user.email=lcherryh@yahoo.com"
cd $W || exit 2
git add -A src && git $G commit -q -m "wip: headers step 6 B1"; echo "wip head $(git rev-parse --short HEAD) on $(git branch --show-current)"
git fetch -q origin; echo "origin/main $(git rev-parse --short origin/main) (parent 9b3829c38; ahead $(git rev-list --count 9b3829c38..origin/main))"
git checkout -q -B cto-headers-6b1-land origin/main || exit 2
git merge -q --squash cto-headers-6b1-wip || { echo "SQUASH CONFLICT"; git status --short | head; exit 2; }
git status --short | wc -l | sed 's/^/files staged: /'
git $G commit -q -F $S4/b1-commit.txt || exit 2
SH=$(git rev-parse --short HEAD); echo "SCRIP landing commit $SH ($(git show --stat --format= HEAD | tail -1))"
cd $HW && sed -i "s/\[HASH\]/$SH/" $S4/b1-harness-commit.txt && git add -A scripts && git $G commit -q -F $S4/b1-harness-commit.txt || exit 2
cd $W && git push -q origin HEAD:main && echo "SCRIP pushed $SH" || { echo "SCRIP PUSH REJECTED"; exit 3; }
cd $HW && git fetch -q origin && git rebase -q origin/main && git push -q origin HEAD:main && echo "harness pushed $(git rev-parse --short HEAD)" || { echo "HARNESS PUSH REJECTED"; exit 3; }
echo "SCRIP=$SH HARNESS=$(git rev-parse --short HEAD)" > $S4/landed6b1-hashes.txt
cd /home/claude_cto && for r in SCRIP harness; do git -C $r fetch -q origin && git -C $r merge -q --ff-only origin/main && echo "$r root at $(git -C $r rev-parse --short HEAD)"; done
cd /home/claude_cto/SCRIP && make -j8 > $S4/root-make6b1.log 2>&1; echo "root make rc=$? $(grep -oE 'FETCHED|PUBLISHED' $S4/root-make6b1.log | head -1)"
. $S4/landed6b1-hashes.txt; T=$(date '+%H:%M')
cd /home/claude_cto/.github && git fetch -q origin && git merge -q --ff-only origin/main && python3 -I $S4/b1-page.py "$SCRIP" "$T" "$(cat $S4/b1-r5.txt)" "$(cat $S4/b1-fanin.txt)" || exit 2
mkdir -p scripts/headers/step6 && cp $S4/hdr6b1.py $S4/apply6b1-proof.sh $S4/land6b1.sh $S4/hdr6c.py $S4/hdr6c_harness.py scripts/headers/step6/
git add ARCH-HEADER-SPLIT.md scripts/headers/step6 && git $G commit -q -F - <<EOF
ARCH-HEADER-SPLIT: step 6 B1 as built (the cto under CEO-2091; SCRIP $SCRIP, harness $HARNESS): the driver_private.h row landed as measured, roll-out row 6 (B1 landed, C next); the method scripts of step 6 under scripts/headers/step6 (hdr6b1.py the split by definer, hdr6c.py the sweep and the -I cut, hdr6c_harness.py its harness twin).
EOF
git push -q origin HEAD:main && echo ".github pushed $(git rev-parse --short HEAD)" || { echo ".github PUSH FAILED"; exit 3; }
sed -i "s/\[T\]/$T/g; s/\[HASH\]/$SCRIP/g; s/\[HHASH\]/$HARNESS/g" $S4/b1-baton-next.txt $S4/b1-baton-ledger.txt
python3 - "$S4" <<'PY'
import sys, glob
S4=sys.argv[1]; p=glob.glob('/home/resources/postoffice/tasks/headers-step-6-the-layers-*.task.md')[0]; t=open(p).read()
i=t.index('## NEXT\n')+len('## NEXT\n'); j=t.index('\n## ', i); old=t[i:j]
t=t[:i]+open(S4+'/b1-baton-next.txt').read().rstrip('\n')+'\n## SUPERSEDED-NEXT\n'+old.strip('\n')+t[j:]
t=t.rstrip('\n')+'\n'+open(S4+'/b1-baton-ledger.txt').read(); open(p,'w').write(t); print('step-6 baton: NEXT rewritten (the old one kept as SUPERSEDED-NEXT), LEDGER line appended')
PY
echo "LAND6B1 DONE $(date +%T)"
