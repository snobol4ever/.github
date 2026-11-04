#!/usr/bin/env bash
# propagate_banner_delta_ceo_2129.sh -- THE DOUBLE-SIDED BANNER REACHES EVERY ROOT (Lon 2026-11-04, in-chat to the cto, verbatim: "In the display
# banner add a column for a delta/difference and distribute the new double-sided banner across the fleet."; CEO-2129).
# The banner is .github/scripts/util_suite_banner.py, read by every root from its OWN .github clone (the bus's Stop banner runs
# $S4E/.github/scripts/util_suite_banner.py), so the fleet carries the new column the moment each clone is at origin/main. A seat syncs at its
# sitting's step 1; this script does that one step for every root now, FAST-FORWARD ONLY: a clone that is dirty, not on main, or diverged is
# named and left alone (its seat syncs it). The table itself (/home/resources/progress/SUITES.tsv) is ONE file every seat reads in place; its
# prev_* columns appear on the first --set that moves a reading and need no distribution.
#   usage: propagate_banner_delta_ceo_2129.sh [--check]     --check reports without touching any clone
CHECK=0; [ "${1:-}" = "--check" ] && CHECK=1
ok=0; behind=0; skipped=0; roots=0
for root in /home/claude_*; do
  [ -f "$root/CLAUDE.md" ] && [ -d "$root/.github/.git" ] || continue; roots=$((roots+1))
  g="$root/.github"
  br=$(git -C "$g" rev-parse --abbrev-ref HEAD 2>/dev/null)
  if [ "$br" != "main" ] || [ -n "$(git -C "$g" status --porcelain 2>/dev/null)" ]; then echo "SKIP $root (.github on $br, $(git -C "$g" status --porcelain | wc -l) local change(s)) -- its seat syncs it"; skipped=$((skipped+1)); continue; fi
  git -C "$g" fetch -q origin 2>/dev/null || { echo "SKIP $root (fetch failed)"; skipped=$((skipped+1)); continue; }
  if [ "$(git -C "$g" rev-parse HEAD)" = "$(git -C "$g" rev-parse origin/main)" ]; then echo "AT-ORIGIN $root $(git -C "$g" rev-parse --short HEAD)"; ok=$((ok+1)); continue; fi
  if ! git -C "$g" merge-base --is-ancestor HEAD origin/main; then echo "SKIP $root (.github diverged from origin/main) -- its seat rebases"; skipped=$((skipped+1)); continue; fi
  if [ $CHECK = 1 ]; then echo "BEHIND $root $(git -C "$g" rev-parse --short HEAD) -> $(git -C "$g" rev-parse --short origin/main)"; behind=$((behind+1)); continue; fi
  if git -C "$g" merge -q --ff-only origin/main 2>/dev/null; then echo "FF $root -> $(git -C "$g" rev-parse --short HEAD)"; ok=$((ok+1)); else echo "SKIP $root (ff-only merge refused)"; skipped=$((skipped+1)); fi
done
echo "BANNER roots=$roots at_origin_or_ff=$ok behind=$behind skipped=$skipped"
[ $skipped = 0 ] && [ $behind = 0 ]
