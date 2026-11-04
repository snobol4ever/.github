#!/usr/bin/env bash
# propagate_skills_ceo_2071.sh [--check] -- EVERY SEAT GETS THE FLEET'S SKILLS (Lon 2026-10-31, in-chat to the ceo: the seats specialise through
# skills, each language's knowledge in one place every seat loads on demand; ceo CEO-2071). The source of truth is .github/skills/<name>/SKILL.md
# (committed); this script copies each skill into every root's project skills folder /home/claude_<seat>/.claude/skills/<name>/ so a seat loads it
# as /<name>, and removes a root copy whose source is gone. --check only reports which roots differ (rc 1 when any does). Idempotent; never a
# symlink (CEO-1853). Re-run after every skill landing. Only skills from .github/skills are touched; a root's other skills are left alone.
HERE=$(cd "$(dirname "$0")" && pwd); SRC=$HERE/../skills
CHECK=0; [ "${1:-}" = "--check" ] && CHECK=1
[ -d "$SRC" ] || { echo "REFUSE(2): no $SRC"; exit 2; }
diff_n=0; roots=0
for root in /home/claude_*; do
  [ -f "$root/CLAUDE.md" ] || continue; roots=$((roots+1))
  for s in "$SRC"/*/; do
    n=$(basename "$s"); dst=$root/.claude/skills/$n
    if [ -d "$dst" ] && diff -rq "$s" "$dst" >/dev/null 2>&1; then continue; fi
    diff_n=$((diff_n+1))
    if [ $CHECK = 1 ]; then echo "DIFF $(basename "$root") $n"; else mkdir -p "$dst" && rm -rf "$dst"/* && cp -r "$s"/. "$dst"/ && echo "INSTALLED $(basename "$root") $n"; fi
  done
done
echo "SKILLS roots=$roots skills=$(ls -d "$SRC"/*/ | wc -l) $([ $CHECK = 1 ] && echo differing || echo installed)=$diff_n"
[ $CHECK = 0 ] || [ $diff_n = 0 ]
