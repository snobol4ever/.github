#!/usr/bin/env bash
# delete_dead_github_branches_2026_10_30.sh [--apply] -- DELETE THE DEAD BRANCHES OF THE snobol4ever ORG ON GITHUB (Lon 2026-10-30, in-chat to the ceo,
# verbatim: "we need to get all those github branches accounted for and deleted. We want only the main branch and active branches to still exist.";
# ceo CEO-2036). THE ACCOUNTING is /home/resources/branch-archive/2026-10-30/MANIFEST.tsv, one row per non-default branch of the eight repositories
# that carry any (82 at 10:3x CDT), each with its tip commit, its last-commit date, its commits not on the default branch counted by patch (git cherry)
# and by ancestry, and its class:
#   DELETE-NOWORK        36  merged into main, or every patch already on main
#   DELETE-AFTER-BUNDLE  35  unique work, last commit over 7 days ago (and the ceo's own whack-all wip); each saved FIRST as a git bundle of
#                            main..branch beside the manifest (git bundle unbundle, or git fetch <bundle> <branch>, restores it on any clone of main)
#   KEEP-ASK-OWNER       11  unique work within 7 days: never touched here; the owning seats are asked
# x64's nine branches all still exist upstream in spitbol/x64, so deleting them from the fork loses nothing.
# The ceo's own run of this deletion was refused by the session's permission classifier, so Lon runs it.
#   bash /home/claude_ceo/.github/scripts/delete_dead_github_branches_2026_10_30.sh            # dry run: prints what would be deleted
#   bash /home/claude_ceo/.github/scripts/delete_dead_github_branches_2026_10_30.sh --apply    # deletes, one push per repository, then re-lists
# EXIT: 0 done (or dry run); 1 a push failed; 2 refused (the manifest or a bundle is missing).
set -u
M=/home/resources/branch-archive/2026-10-30/MANIFEST.tsv
APPLY=0; [ "${1:-}" = "--apply" ] && APPLY=1
[ -s "$M" ] || { echo "REFUSED rc=2: $M is missing"; exit 2; }
miss=$(awk -F'\t' 'NR>1 && $1=="DELETE-AFTER-BUNDLE" {print $9}' "$M" | while read -r f; do [ -s "$f" ] || echo "$f"; done)
[ -z "$miss" ] || { echo "REFUSED rc=2: a bundle is missing, so a branch with unique work would be lost:"; echo "$miss"; exit 2; }
rc=0
for r in $(awk -F'\t' 'NR>1 && $1 ~ /^DELETE/ {print $2}' "$M" | sort -u); do
  bs=$(awk -F'\t' -v r="$r" 'NR>1 && $1 ~ /^DELETE/ && $2==r {print $3}' "$M")
  n=$(printf '%s\n' "$bs" | wc -l)
  if [ "$APPLY" -eq 0 ]; then echo "== $r: would delete $n"; printf '   %s\n' $bs; continue; fi
  src=/home/claude_ceo/$r; [ -d "$src/.git" ] || src=/home/claude_ceo/SCRIP
  out=$(timeout 300 git -C "$src" push "git@github.com:snobol4ever/$r.git" --delete $bs 2>&1); prc=$?
  echo "== $r: asked $n, rc=$prc, deleted $(printf '%s\n' "$out" | grep -c '\[deleted\]')"
  [ "$prc" -eq 0 ] || { printf '%s\n' "$out" | grep -v '\[deleted\]' | head -5; rc=1; }
done
[ "$APPLY" -eq 1 ] || { echo "dry run: nothing deleted; re-run with --apply"; exit 0; }
echo "== branches left on GitHub"
for r in .github SCRIP corpus csnobol4 harness snobol4artifact snobol4csharp snobol4dotnet snobol4jvm snobol4python x32 x64; do
  echo "$r: $(timeout 60 git ls-remote --heads "https://github.com/snobol4ever/$r.git" 2>/dev/null | awk '{sub("refs/heads/","",$2); print $2}' | tr '\n' ' ')"
done
exit "$rc"
