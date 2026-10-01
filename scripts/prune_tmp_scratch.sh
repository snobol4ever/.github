#!/usr/bin/env bash
# prune_tmp_scratch.sh -- the Lon-run /tmp prune (ceo, 2026-10-01, CEO-754 grant widened by Lon's in-chat word "Clean the /tmp").
# DRY RUN by default: prints what it would delete and the bytes. --apply deletes. Four classes, each named in the output:
#   A  dead-session scratchpads: /tmp/claude-1000/-home-claude-<seat>/<session>/ whose transcript jsonl under
#      ~/.claude/projects/ is absent or unwritten for DEAD_H hours (default 24); a dir holding a git repo with commits
#      on no remote is SKIPPED and named, never deleted
#   B  /tmp top-level entries older than OLD_H hours (default 48) -- never claude-1000, never si_objs* (a seat's objdir)
#   C  harness work dirs (/tmp/tmp.*, lgtsuite.*, csh_*) older than WORK_H hours (default 2)
#   D  loose files written straight into /tmp/claude-1000/ (not a seat dir) older than OLD_H hours
# Anything a live process holds as cwd or an open fd is SKIPPED and named. find on this box is bfs and rejects a
# relative -newermt, so every cutoff is an absolute ISO stamp from date -d (CLAUDE.md § Hard rules digest, CEO-754).
set -u
APPLY=0; [ "${1:-}" = "--apply" ] && APPLY=1
DEAD_H=${DEAD_H:-24}; OLD_H=${OLD_H:-48}; WORK_H=${WORK_H:-2}
dead_cut=$(date -d "$DEAD_H hours ago" '+%Y-%m-%dT%H:%M:%S'); old_cut=$(date -d "$OLD_H hours ago" '+%Y-%m-%dT%H:%M:%S'); work_cut=$(date -d "$WORK_H hours ago" '+%Y-%m-%dT%H:%M:%S')
held=$(ls -l /proc/[0-9]*/cwd /proc/[0-9]*/fd/* 2>/dev/null | grep -oE '/tmp/[^ ]+' | sort -u)
is_held() { printf '%s\n' "$held" | grep -q "^$1" ; }
live=$(find /home/satirical/.claude/projects/ -maxdepth 2 -name '*.jsonl' -newermt "$dead_cut" 2>/dev/null | sed -E 's#.*/([0-9a-f-]+)\.jsonl#\1#' | sort -u)
victims=(); skipped=0
consider() { # consider <class> <path>
  if is_held "$2"; then echo "SKIP $1 held by a live process: $2"; skipped=$((skipped+1)); return; fi
  if [ "$1" = A ]; then
    for g in $(timeout 30 find "$2" -maxdepth 4 -name .git 2>/dev/null); do r=$(dirname "$g"); a=$(git -C "$r" rev-list --count --not --remotes HEAD 2>/dev/null || echo 1)
      if [ "$a" != 0 ]; then echo "SKIP A unpushed commits ($a) in $r"; skipped=$((skipped+1)); return; fi; done
  fi
  victims+=("$2")
}
for sd in /tmp/claude-1000/-home-claude-*/*; do [ -d "$sd" ] || continue; sid=$(basename "$sd"); printf '%s\n' "$live" | grep -qx "$sid" && continue; consider A "$sd"; done
while IFS= read -r -d '' e; do case "$(basename "$e")" in claude-1000|si_objs*|lost+found) continue;; esac; consider B "$e"; done < <(find /tmp -mindepth 1 -maxdepth 1 ! -newermt "$old_cut" -print0 2>/dev/null)
while IFS= read -r -d '' e; do consider C "$e"; done < <(find /tmp -mindepth 1 -maxdepth 1 \( -name 'tmp.*' -o -name 'lgtsuite.*' -o -name 'csh_*' \) -newermt "$old_cut" ! -newermt "$work_cut" -print0 2>/dev/null)
while IFS= read -r -d '' e; do consider D "$e"; done < <(find /tmp/claude-1000 -mindepth 1 -maxdepth 1 ! -name '-home-claude-*' ! -newermt "$old_cut" -print0 2>/dev/null)
n=${#victims[@]}; [ "$n" = 0 ] && { echo "nothing to prune (skipped $skipped)"; df -h /tmp | tail -1; exit 0; }
mb=$(printf '%s\0' "${victims[@]}" | du -sc --block-size=1M --files0-from=- 2>/dev/null | tail -1 | cut -f1)
echo "would delete $n entries, $mb MB (skipped $skipped)"
printf '%s\n' "${victims[@]}" | sed -E 's#^/tmp/claude-1000/-home-claude-([a-z0-9_]+)/.*$#A dead session of \1#; t; s#^/tmp/claude-1000/.*$#D loose file in claude-1000#; t; s#^/tmp/(tmp\.|lgtsuite\.|csh_).*$#C harness work dir \1*#; t; s#^/tmp/([A-Za-z_]+[._-]).*$#B \1*#; t; s#^/tmp/.*$#B other#' | sort | uniq -c | sort -rn | head -40
[ "$APPLY" = 1 ] || { echo "DRY RUN -- rerun with --apply to delete"; exit 0; }
printf '%s\0' "${victims[@]}" | xargs -0 rm -rf --; echo "deleted $n entries, $mb MB"; df -h /tmp | tail -1
