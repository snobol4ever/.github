#!/usr/bin/env bash
# util_tmp_sweep_48h.sh -- THE /tmp SWEEP UNDER THE CEO-754 GRANT: delete /tmp scratch on AGE ALONE, over 48 hours, and print the freed bytes.
#
# Lon 2026-10-10 11:1x CDT, in-chat to the ceo, verbatim: "Fix the /tmp disk problem." -- /tmp (its own 63 GB partition) read 100% full; 42 GB was
# /tmp/claude-1000, the Claude Code harness directories of the fourteen seats (per-session scratchpads, background-task outputs and subagent
# transcripts), plus 13 GB of top-level scratch (verify_s_owed clones, mktemp dirs, 109 stale per-tree objdirs). The first sweep freed 26.5 GB.
# THE GRANT (RULES.md, CEO-754): /tmp scratch may be deleted on AGE ALONE, over 48 hours, the freed bytes recorded in GOAL-CFO.md.
# THE RULES OF THIS FILE: an ABSOLUTE ISO cutoff from `date -d '48 hours ago'` (find here is bfs and answers NO everywhere to a relative
# -newermt); a predicate that cannot be evaluated FAILS CLOSED (no cutoff, nothing deleted); a live seat's current session directory is newer
# than the cutoff by construction and is never touched; nothing under /tmp is anyone's record, so nothing is backed up.
# Usage: util_tmp_sweep_48h.sh [--dry-run]      (cron: 17 */6 * * * bash /home/claude_ceo/.github/scripts/util_tmp_sweep_48h.sh >> /home/claude_ceo/.scratch/tmp_sweep.log 2>&1)
set -u
dry=0; [ "${1:-}" = "--dry-run" ] && dry=1
cut=$(date -d '48 hours ago' '+%Y-%m-%dT%H:%M') || { echo "REFUSE(2): no cutoff from date -- nothing deleted"; exit 2; }
[ -n "$cut" ] || { echo "REFUSE(2): empty cutoff -- nothing deleted"; exit 2; }
before=$(df --output=used -m /tmp | tail -1) || exit 2
list=$(mktemp) || exit 2
{ find /tmp -maxdepth 1 -mindepth 1 -not -name 'claude-1000' -not -newermt "$cut"; find /tmp/claude-1000 -maxdepth 2 -mindepth 2 -type d -not -newermt "$cut"; } > "$list" 2>/dev/null
n=$(wc -l < "$list")
printf '%s tmp-sweep cutoff=%s candidates=%s objdirs=%s used-before=%sMB' "$(date '+%Y-%m-%dT%H:%M:%S%z')" "$cut" "$n" "$(grep -c si_objs "$list")" "$before"
if [ "$dry" = 1 ]; then printf ' DRY-RUN\n'; rm -f "$list"; exit 0; fi
xargs -a "$list" -d '\n' rm -rf -- 2>/dev/null
rm -f "$list"
after=$(df --output=used -m /tmp | tail -1)
printf ' freed=%sMB used-after=%sMB %s\n' "$((before-after))" "$after" "$(df -h /tmp | tail -1 | awk '{print $5" of "$2}')"
