#!/usr/bin/env bash
set -u
S4=/tmp/claude-1000/-home-claude-cto/b1caac4c-9b75-4393-9260-1c72f906f86b/scratchpad; SO=/tmp/claude-1000/-home-claude-cto/25cbd82c-ea4e-46bc-9ee6-3c52fc5dcc1f/scratchpad; W=$SO/hdr/SCRIP; HW=$SO/hdr/harness
G="-c user.name=LCherryholmes -c user.email=lcherryh@yahoo.com"
cd $W || exit 2
echo "== SCRIP: one commit on origin/main"
git add -A src && git $G commit -q -m "wip: headers step 4"; echo "wip head $(git rev-parse --short HEAD) on $(git branch --show-current)"
git fetch -q origin; echo "origin/main $(git rev-parse --short origin/main) (parent 75a5a69a9; ahead $(git rev-list --count 75a5a69a9..origin/main))"
git checkout -q -B cto-headers-4-land origin/main || exit 2
git merge -q --squash cto-headers-4-wip || { echo "SQUASH CONFLICT"; git status --short | head; exit 2; }
git status --short | wc -l | sed 's/^/files staged: /'
git $G commit -q -F $S4/commit4-msg.txt || exit 2
SH=$(git rev-parse --short HEAD); echo "SCRIP landing commit $SH ($(git show --stat --format= HEAD | tail -1))"
echo "== harness: the twin"
cd $HW && sed -i "s/\[SCRIP_HASH\]/$SH/" $S4/harness4-commit-msg.txt && git add -A scripts && git $G commit -q -F $S4/harness4-commit-msg.txt || exit 2
echo "harness landing commit $(git rev-parse --short HEAD)"
echo "== push SCRIP then harness"
cd $W && git push -q origin HEAD:main && echo "SCRIP pushed $SH" || { echo "SCRIP PUSH REJECTED"; exit 3; }
cd $HW && git fetch -q origin && git rebase -q origin/main && git push -q origin HEAD:main && echo "harness pushed $(git rev-parse --short HEAD)" || { echo "HARNESS PUSH REJECTED"; exit 3; }
echo "SCRIP=$SH HARNESS=$(git rev-parse --short HEAD)" > $S4/landed4-hashes.txt
echo "== root fast-forward and rebuild"
cd /home/claude_cto && for r in SCRIP harness; do git -C $r fetch -q origin && git -C $r merge -q --ff-only origin/main && echo "$r root at $(git -C $r rev-parse --short HEAD)"; done
cd /home/claude_cto/SCRIP && make -j8 > $S4/root-make4.log 2>&1; echo "root make rc=$? compiles=$(grep -c -- " -c " $S4/root-make4.log) $(grep -oE 'FETCHED|PUBLISHED' $S4/root-make4.log | head -1)"
echo "LAND4 DONE $(date +%T)"
