#!/usr/bin/env bash
# after land4.sh: the record (.github), the baton, done, the test requests, the telegrams
set -u
S4=/tmp/claude-1000/-home-claude-cto/b1caac4c-9b75-4393-9260-1c72f906f86b/scratchpad
. $S4/landed4-hashes.txt   # SCRIP=... HARNESS=...
T=$(date '+%H:%M'); R5LINE=$(cat $S4/r5line.txt)
for f in commit4-msg.txt harness4-commit-msg.txt page-3-3.txt cto-440.txt baton4-ledger.txt baton4-next.txt github4-commit-msg.txt tg4-hq_templates.txt tg4-hq_packages.txt; do sed -i "s/\[SCRIP_HASH\]/$SCRIP/g; s/\[HARNESS_HASH\]/$HARNESS/g; s/\[T\]/$T/g; s/\[R5LINE\]/$R5LINE/g" $S4/$f; done
G="-c user.name=LCherryholmes -c user.email=lcherryh@yahoo.com"
cd /home/claude_cto/.github && git fetch -q origin && git merge -q --ff-only origin/main
python3 -I $S4/page4.py || exit 2
python3 - <<'PY'
S4='/tmp/claude-1000/-home-claude-cto/b1caac4c-9b75-4393-9260-1c72f906f86b/scratchpad'
p='/home/claude_cto/.github/GOAL-CTO.md'; t=open(p).read(); e=open(S4+'/cto-440.txt').read()
i=t.index('- **CTO-439 '); t=t[:i]+e+t[i:]; open(p,'w').write(t); print('CTO-440 in the cursor')
PY
mkdir -p scripts/headers/step4 && cp $S4/hdr4.py $S4/fix2.py $S4/fix3.py $S4/apply4-reproof.sh $S4/hdr4_fix.py $S4/hdr_order.py $S4/order_cmp.py $S4/apply4-build.sh $S4/apply4-proof.sh $S4/dw4.sh $S4/page4.py $S4/land4.sh $S4/land4b.sh scripts/headers/step4/ && cp $S4/hdr4_moved.txt scripts/headers/step4/hdr4_moved.txt
git add ARCH-HEADER-SPLIT.md GOAL-CTO.md scripts/headers/step4 && git $G commit -q -F $S4/github4-commit-msg.txt && git push -q origin HEAD:main && echo ".github pushed $(git rev-parse --short HEAD)" || { echo ".github PUSH FAILED"; exit 3; }
GH=$(git rev-parse --short HEAD); sed -i "s/\[GITHUB_HASH\]/$GH/g" $S4/baton4-ledger.txt
echo "== baton"
python3 -I $S4/amend-dw4.py || exit 2
echo "== claim + done (runs the DONE-WHEN in the root)"
cd /home/claude_cto && T4=$(ls /home/resources/postoffice/tasks/headers-step-4-*.task.md | xargs -n1 basename | sed 's/\.task\.md$//')
bash harness/scripts/s4e_msg.sh claim $T4 2>&1 | tail -2 | cut -c1-200
bash harness/scripts/s4e_msg.sh done $T4 2>&1 | tail -4 | cut -c1-200
echo "== test requests"
bash $S4/test-requests-4.sh 2>&1 | tail -8 | cut -c1-160
echo "== telegrams"
for s in hq_templates hq_packages; do bash harness/scripts/s4e_msg.sh send $s $T4 --stdin < $S4/tg4-$s.txt 2>&1 | tail -1 | cut -c1-120; done
echo "LAND4B DONE $(date +%T)"
