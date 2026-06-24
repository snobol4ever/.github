#!/usr/bin/env bash
# handoff_status.sh — THE ONLY SANCTIONED SOURCE OF A HANDOFF COMPLETION CLAIM.
#
# Per RULES.md FACT RULE (2026-06-24): the assistant MUST NOT compose the words
# "HANDOFF COMPLETE" as prose. It runs THIS script and presents the verbatim output.
# The script reads GROUND TRUTH — working tree clean, and local HEAD == origin/<branch>
# with zero unpushed commits — for every touched repo, and prints HANDOFF COMPLETE
# ONLY when all pass. Otherwise it prints HANDOFF BLOCKED with the precise reason.
# Reading origin needs no credential (fetch of a public repo is unauthenticated);
# only the push that PRECEDES this check needs one. Exit 0 = complete, 1 = blocked.
#
# Usage: handoff_status.sh [repo_dir ...]   (defaults to the three SCRIP repos)
set -uo pipefail
REPOS=("$@")
if [ ${#REPOS[@]} -eq 0 ]; then
  REPOS=(/home/claude/SCRIP /home/claude/corpus /home/claude/.github)
fi
blocked=0; reasons=()
echo "=== HANDOFF STATUS — ground truth from git, not assertion ==="
for r in "${REPOS[@]}"; do
  [ -d "$r/.git" ] || { echo "  $(basename "$r"): NOT A GIT REPO — skipped"; continue; }
  name=$(basename "$r")
  br=$(git -C "$r" rev-parse --abbrev-ref HEAD 2>/dev/null)
  dirty=$(git -C "$r" status --porcelain 2>/dev/null | wc -l)
  git -C "$r" fetch --quiet origin 2>/dev/null || reasons+=("$name: fetch failed (origin ref may be stale)")
  lh=$(git -C "$r" rev-parse HEAD 2>/dev/null)
  oh=$(git -C "$r" rev-parse "origin/$br" 2>/dev/null || echo MISSING)
  unpushed=$(git -C "$r" log --oneline "@{u}..HEAD" 2>/dev/null | wc -l)
  st="OK"
  if [ "$dirty" -ne 0 ]; then st="DIRTY"; reasons+=("$name: $dirty uncommitted change(s) — commit them"); blocked=1; fi
  if [ "$lh" != "$oh" ] || [ "$unpushed" -ne 0 ]; then st="UNPUSHED"; reasons+=("$name: local HEAD not on origin/$br ($unpushed unpushed) — run: git pull --rebase && git push"); blocked=1; fi
  printf "  %-22s %-10s local=%s origin=%s\n" "$name [$br]" "$st" "${lh:0:9}" "${oh:0:9}"
done
echo "------------------------------------------------------------"
if [ "$blocked" -eq 0 ] && [ ${#reasons[@]} -eq 0 ]; then
  echo "HANDOFF COMPLETE"
  exit 0
else
  echo "HANDOFF BLOCKED — DO NOT report done:"
  printf '  - %s\n' "${reasons[@]}"
  exit 1
fi
