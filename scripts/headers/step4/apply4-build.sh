#!/usr/bin/env bash
S4=/tmp/claude-1000/-home-claude-cto/b1caac4c-9b75-4393-9260-1c72f906f86b/scratchpad; SO=/tmp/claude-1000/-home-claude-cto/25cbd82c-ea4e-46bc-9ee6-3c52fc5dcc1f/scratchpad; W=$SO/hdr/SCRIP; cd $W || exit 2
prev=-1
for i in 1 2 3 4 5 6 7 8; do
  CCACHE_DISABLE=1 S4E_NO_BUILD_CACHE=1 timeout -k 5 1500 make -k -j8 > $S4/mk4-$i.log 2>&1; rc=$?
  e=$(grep -c ' error: \|fatal error' $S4/mk4-$i.log); echo "round $i: make rc=$rc errors=$e compiles=$(grep -c -- ' -c ' $S4/mk4-$i.log) $(date +%T)"
  [ "$e" = 0 ] && { echo "BUILD GREEN at round $i"; break; }
  [ "$e" = "$prev" ] && { echo "NO PROGRESS at round $i"; grep ' error: \|fatal error' $S4/mk4-$i.log | sed -E 's#.*/hdr/SCRIP/##' | sort | uniq -c | sort -rn | head -30 | cut -c1-220; break; }
  prev=$e
  python3 -I $S4/hdr4_fix.py $W $S4/mk4-$i.log 2>&1 | tail -3 | cut -c1-400
done
echo "APPLY4 BUILD DONE $(date +%T)"
