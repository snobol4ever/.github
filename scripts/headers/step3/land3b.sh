#!/usr/bin/env bash
# after land3.sh: the record (.github), the baton, done, the test requests, the telegrams
set -u
S=/tmp/claude-1000/-home-claude-cto/25cbd82c-ea4e-46bc-9ee6-3c52fc5dcc1f/scratchpad
. $S/landed3-hashes.txt   # SCRIP=... HARNESS=...
T=$(date '+%H:%M')
for f in commit3-msg.txt harness3-commit-msg.txt page-3-2.txt cto-438.txt baton3-ledger.txt baton3-next.txt github3-commit-msg.txt tg3-hq_templates.txt tg3-cao.txt tg3-hq_pascal.txt; do sed -i "s/\[SCRIP_HASH\]/$SCRIP/g; s/\[HARNESS_HASH\]/$HARNESS/g; s/\[T\]/$T/g" $S/$f; done
G="-c user.name=LCherryholmes -c user.email=lcherryh@yahoo.com"
cd /home/claude_cto/.github && git fetch -q origin && git merge -q --ff-only origin/main
python3 -I $S/page3.py || exit 2
python3 - <<'PY'
S='/tmp/claude-1000/-home-claude-cto/25cbd82c-ea4e-46bc-9ee6-3c52fc5dcc1f/scratchpad'
p='/home/claude_cto/.github/GOAL-CTO.md'; t=open(p).read(); e=open(S+'/cto-438.txt').read()
i=t.index('- **CTO-437 '); t=t[:i]+e+t[i:]; open(p,'w').write(t); print('CTO-438 in the cursor')
PY
git add ARCH-HEADER-SPLIT.md GOAL-CTO.md && git $G commit -q -F $S/github3-commit-msg.txt && git push -q origin HEAD:main && echo ".github pushed $(git rev-parse --short HEAD)" || { echo ".github PUSH FAILED"; exit 3; }
echo "== baton"
python3 -I $S/amend-dw3.py "$(cat $S/baton3-ledger.txt)" $S/baton3-next.txt || exit 2
echo "== done (runs the DONE-WHEN in the root)"
cd /home/claude_cto && bash harness/scripts/s4e_msg.sh done headers-step-3-emit-h-is-un-concatenated-into-emit-state-h-bb-label-h-emit-medium-h-emit-sm-h-and-the-walker-states-and-the-templates-read-three-small-headers-ceo-2032 2>&1 | tail -4 | cut -c1-200
echo "== test requests"
bash $S/test-requests-3.sh 2>&1 | tail -8 | cut -c1-160
echo "== telegrams"
for s in hq_templates cao hq_pascal; do bash harness/scripts/s4e_msg.sh send $s headers-step-3-emit-h-is-un-concatenated-into-emit-state-h-bb-label-h-emit-medium-h-emit-sm-h-and-the-walker-states-and-the-templates-read-three-small-headers-ceo-2032 --stdin < $S/tg3-$s.txt 2>&1 | tail -1 | cut -c1-120; done
echo "LAND3B DONE $(date +%T)"
