#!/bin/bash
set -u
CUT_ISO="$(date -d '48 hours ago' '+%Y-%m-%d %H:%M:%S')"
SP="$(dirname "$0")"; LOG="$SP/prune-$(date +%Y%m%d-%H%M%S).log"; LIST="$SP/prune-list.tsv"
ME=$(id -un)
HANDLES="$(ls -l /proc/[0-9]*/cwd /proc/[0-9]*/fd/* /proc/[0-9]*/exe 2>/dev/null | grep -oE ' /tmp/[^ ]+' | sort -u)"
held() { local e="$1"; printf '%s\n' "$HANDLES" | grep -qE "^ ${e//./\\.}(/|$)"; }
cands=()
for e in /tmp/* /tmp/.[!.]*; do [ -e "$e" ] || continue; [ "$e" = /tmp/claude-1000 ] && continue; cands+=("$e"); done
for e in /tmp/claude-1000/*; do [ -e "$e" ] || continue; case "$e" in /tmp/claude-1000/-home-claude-*) for s in "$e"/*; do [ -e "$s" ] && cands+=("$s"); done;; *) cands+=("$e");; esac; done
n_old=0; kb_old=0; n_keep=0; n_skip=0; : > "$LIST"
for e in "${cands[@]}"; do
  [ "$(stat -c %U -- "$e" 2>/dev/null)" = "$ME" ] || { n_skip=$((n_skip+1)); continue; }
  if find "$e" -xdev -newermt "$CUT_ISO" -print -quit 2>/dev/null | grep -q .; then n_keep=$((n_keep+1)); continue; fi
  find "$e" -xdev -print -quit 2>/dev/null | grep -q . || { n_skip=$((n_skip+1)); echo "UNMEASURABLE-KEPT $e" >> "$LOG"; continue; }
  if held "$e"; then n_skip=$((n_skip+1)); echo "HELD-KEPT $e" >> "$LOG"; continue; fi
  kb=$(du -xsk -- "$e" 2>/dev/null | cut -f1); n_old=$((n_old+1)); kb_old=$((kb_old+kb)); printf '%s\t%s\n' "$kb" "$e" >> "$LIST"
done
echo "cutoff=$CUT_ISO candidates=${#cands[@]} old=$n_old old_kb=$kb_old kept_young=$n_keep skipped=$n_skip list=$LIST log=$LOG" | tee -a "$LOG"
if [ "${DRY:-1}" = 0 ]; then
  before=$(df --output=avail -k / | tail -1); del=0
  while IFS=$'\t' read -r kb e; do
    find "$e" -xdev -newermt "$CUT_ISO" -print -quit 2>/dev/null | grep -q . && { echo "RACED-KEPT $e" >> "$LOG"; continue; }
    rm -rf -- "$e" && { del=$((del+1)); echo "DELETED $kb $e" >> "$LOG"; }
  done < "$LIST"
  after=$(df --output=avail -k / | tail -1)
  echo "deleted=$del freed_kb_by_df=$((after-before)) avail_before_kb=$before avail_after_kb=$after" | tee -a "$LOG"
fi
