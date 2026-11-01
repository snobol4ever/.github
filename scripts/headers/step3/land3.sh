#!/usr/bin/env bash
set -u
S=/tmp/claude-1000/-home-claude-cto/25cbd82c-ea4e-46bc-9ee6-3c52fc5dcc1f/scratchpad; W=$S/hdr/SCRIP; HW=$S/hdr/harness
G="-c user.name=LCherryholmes -c user.email=lcherryh@yahoo.com"
cd $W || exit 2
until [ -f $S/sudoku-done ]; do sleep 10; done
echo "== SCRIP: one commit on origin/main"
git add -A src && git $G commit -q -m "wip: headers step 3" ; echo "wip head $(git rev-parse --short HEAD) on $(git branch --show-current)"
git fetch -q origin; echo "origin/main $(git rev-parse --short origin/main) (parent b275c0c27; ahead $(git rev-list --count b275c0c27..origin/main))"
git checkout -q -B cto-headers-3-land origin/main || exit 2
git merge -q --squash cto-headers-3-wip || { echo "SQUASH CONFLICT"; git status --short | head; exit 2; }
git status --short | wc -l | sed 's/^/files staged: /'
git $G commit -q -F $S/commit3-msg.txt || exit 2
SH=$(git rev-parse --short HEAD); echo "SCRIP landing commit $SH ($(git show --stat --format= HEAD | tail -1))"
echo "== harness: the two gates"
cd $HW && sed -i "s/\[SCRIP_HASH\]/$SH/" $S/harness3-commit-msg.txt && git add scripts/test_gate_bb_label_no_silent_truncation.sh scripts/test_gate_fb_adopt_one_predicate.sh scripts/lib_elf_noncomdat.py scripts/header_base_set.tsv scripts/header_inline_allowed.tsv scripts/fixtures/dyn_caps/CLASS_AB.tsv && git $G commit -q -F $S/harness3-commit-msg.txt || exit 2
echo "harness landing commit $(git rev-parse --short HEAD)"
echo "== push SCRIP then harness"
cd $W && git push -q origin HEAD:main && echo "SCRIP pushed $SH" || { echo "SCRIP PUSH REJECTED"; exit 3; }
cd $HW && git fetch -q origin && git rebase -q origin/main && git push -q origin HEAD:main && echo "harness pushed $(git rev-parse --short HEAD)" || { echo "HARNESS PUSH REJECTED"; exit 3; }
echo "SCRIP=$SH HARNESS=$(git rev-parse --short HEAD)" > $S/landed3-hashes.txt
echo "== root fast-forward and rebuild (after the control gate running in the root has reported)"
until grep -q "^rc=" $S/root-gcsafe-gate.log 2>/dev/null; do sleep 5; done
cd /home/claude_cto && for r in SCRIP harness; do git -C $r fetch -q origin && git -C $r merge -q --ff-only origin/main && echo "$r root at $(git -C $r rev-parse --short HEAD)"; done
cd /home/claude_cto/SCRIP && make -j8 pristine > $S/root-make3.log 2>&1; echo "root pristine rc=$? compiles=$(grep -c -- " -c " $S/root-make3.log)"
echo "LAND3 DONE $(date +%T)"
