#!/usr/bin/env bash
set -u
S4=/tmp/claude-1000/-home-claude-cto/b1caac4c-9b75-4393-9260-1c72f906f86b/scratchpad; SO=/tmp/claude-1000/-home-claude-cto/25cbd82c-ea4e-46bc-9ee6-3c52fc5dcc1f/scratchpad; W=$SO/hdr/SCRIP; HW=$SO/hdr/harness
G="-c user.name=LCherryholmes -c user.email=lcherryh@yahoo.com"
cd $HW && git add scripts/util_header_fanin.py scripts/test_gate_no_header_reaches_more_units_than_its_users.sh && git $G commit -q -F $S4/s7c-harness-commit.txt || exit 2
git fetch -q origin && git rebase -q origin/main && git push -q origin HEAD:main && echo "harness pushed $(git rev-parse --short HEAD)" || { echo "HARNESS PUSH REJECTED"; exit 3; }
HH=$(git rev-parse --short HEAD); git show HEAD -- scripts > $S4/hdr7c-harness.patch; echo "patch record $(wc -l < $S4/hdr7c-harness.patch) lines"
cd $W && git fetch -q origin && git checkout -q -B cto-headers-7c origin/main && python3 - <<'PY' || exit 2
p='/tmp/claude-1000/-home-claude-cto/25cbd82c-ea4e-46bc-9ee6-3c52fc5dcc1f/scratchpad/hdr/SCRIP/Makefile'; t=open(p).read()
old='test_gate_no_header_reaches_more_units_than_its_users.sh   # ~9s MEASURED (cto 2026-10-31, step 7 of ARCH-HEADER-SPLIT, CEO-2032):'
assert t.count(old)==1
t=t.replace(old, 'test_gate_no_header_reaches_more_units_than_its_users.sh   # ~17s MEASURED (cto 2026-10-31 23:5x, load 2: the instrument asks make -B -n and gcc -MM for the 297 units, never the .d files; step 7 of ARCH-HEADER-SPLIT, CEO-2032):')
open(p,'w').write(t); print('Makefile: the gate line re-measured')
PY
git add Makefile && git $G commit -q -F - <<EOF || exit 2
Makefile: the ceiling gate's line re-measured at ~17 s (the cto, headers step 7): util_header_fanin.py now asks make -B -n build-all and gcc -MM for the 297 units instead of reading the .d files, which the build cache carries stale from the producer's root (harness $HH); a comment, no code.
EOF
git push -q origin HEAD:main && echo "SCRIP pushed $(git rev-parse --short HEAD)" || { echo "SCRIP PUSH REJECTED"; exit 3; }
SH7=$(git rev-parse --short HEAD); echo "SCRIP=$SH7 HARNESS=$HH" > $S4/landed7c-hashes.txt
cd /home/claude_cto && for r in SCRIP harness; do git -C $r fetch -q origin && git -C $r merge -q --ff-only origin/main && echo "$r root at $(git -C $r rev-parse --short HEAD)"; done
cd /home/claude_cto/SCRIP && make -j8 > $S4/root-make7c.log 2>&1; echo "root make rc=$? $(grep -oE 'FETCHED|PUBLISHED' $S4/root-make7c.log | head -1)"
cd /home/claude_cto && echo "== the step-7 DONE-WHEN on the root"; S4E_HOME=/home/claude_cto bash $S4/dw7.sh 2>&1 | tail -1 | cut -c1-120
T7=$(ls /home/resources/postoffice/tasks/headers-step-7-*.task.md | xargs -n1 basename | sed 's/\.task\.md$//'); grep "$T7" /home/resources/postoffice/QUEUE.tsv | cut -f1,3,4 | cut -c1-80
bash harness/scripts/s4e_msg.sh done $T7 2>&1 | grep -E 'RECEIPT|DONE|REFUSE|⛔|RED|exited' | head -3 | cut -c1-200
grep "$T7" /home/resources/postoffice/QUEUE.tsv | cut -f1,3,4 | cut -c1-80
echo "LAND7C DONE $(date +%T)"
