#!/usr/bin/env bash
# ceo_numbers.sh -- THE FOUR NUMBERS PLUS THE DELTA SINCE THE LAST TIME THEY WERE SHOWN.
#
# ⛔ WHY: on 2026-09-21 the ceo reported "one of four moved" as progress. Lon asked whether the
# other three had moved. THEY HAD NOT MOVED ONE UNIT IN 1h48m -- safe-point 125/251, callback
# 0/49, C->BB 0/49, byte-identical to the first reading -- and the ceo had not compared them to
# the previous reading before reporting. A number shown without its delta lets a stall be
# reported as a state. This makes the stall LOUDER THAN THE VALUE, mechanically, so it cannot
# be dressed up by whoever is reporting -- and that is the point, because the one who dressed
# it up was me.
set -u
SELF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
S4E="${S4E_HOME:-$(cd "$SELF_DIR/../.." && pwd)}"
LOG="${CEO_NUMBERS_LOG:-$S4E/.github/ceo-numbers.tsv}"
OUT="$(cd "$S4E/SCRIP" && timeout 600 python3 scripts/util_gc_acceptance.py 2>&1)" || true
g() { printf '%s\n' "$OUT" | grep -oE "$1" | head -1 | grep -oE '[0-9]+ / [0-9]+' | tr -d ' ' ; }
SP="$(g 'safe-point polls at allocating call returns +[0-9]+ / [0-9]+')"
CB="$(g 'callback wraps \(RT_GC_CALLBACK\) +[0-9]+ / [0-9]+')"
CB2="$(g 'C->BB entry sites carrying rt_c2bb_hit +[0-9]+ / [0-9]+')"
EV="$(g 'declared events observed +[0-9]+ / [0-9]+')"
AU=$(printf '%s\n' "$OUT" | grep -q 'built in:' && echo BUILT || echo NOT-BUILT)
WK=$(printf '%s\n' "$OUT" | grep -q 'WORKING: no board pass' && echo NOT-MEASURED || echo MEASURED)
VD=$(printf '%s\n' "$OUT" | grep -oE 'VERDICT: [A-Z()0-9]+' | head -1)
NOW="$(date '+%Y-%m-%dT%H:%M:%S')"
PREV="$(tail -1 "$LOG" 2>/dev/null)"
printf '%-14s %-10s %-8s %-8s %-8s %-10s %-13s %s\n' WHEN SAFE-POINT CALLBACK C-TO-BB EVENTS AUDITED WORKING VERDICT
[ -n "$PREV" ] && printf '%-14s %-10s %-8s %-8s %-8s %-10s %-13s %s\n' \
  "$(echo "$PREV"|cut -f1|cut -c6-16)" $(echo "$PREV"|cut -f2-7) "$(echo "$PREV"|cut -f8-)"
printf '%-14s %-10s %-8s %-8s %-8s %-10s %-13s %s\n' "$(echo "$NOW"|cut -c6-16)" "$SP" "$CB" "$CB2" "$EV" "$AU" "$WK" "$VD"
if [ -n "$PREV" ]; then
  p() { echo "$PREV" | cut -f"$1"; }
  moved=0
  for i in 2 3 4 5 6 7; do
    cur=$(printf '%s\t%s\t%s\t%s\t%s\t%s' "$SP" "$CB" "$CB2" "$EV" "$AU" "$WK" | cut -f$((i-1)))
    [ "$(p "$i")" != "$cur" ] && moved=$((moved+1))
  done
  echo
  if [ "$moved" = 0 ]; then
    echo "⛔⛔ NOTHING MOVED since $(p 1). SIX OF SIX COMPONENTS IDENTICAL."
    echo "    A stall is not a state. Say so in the first line of the report, name who owns each"
    echo "    stalled component, and if the answer is 'nobody' that is the finding (CEO-1069)."
  else
    echo "✅ $moved of 6 component(s) MOVED since $(p 1)."
  fi
fi
printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$NOW" "$SP" "$CB" "$CB2" "$EV" "$AU" "$WK" "$VD" >> "$LOG"
