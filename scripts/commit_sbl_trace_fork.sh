#!/usr/bin/env bash
# Commit + push the swapped x64 oracle fork (bin/sbl + sbl.min, hq_B's trace-dispatch fix, installed by Lon 2026-09-05 10:34:17 CDT)
# and write the ORACLES.md top line naming the landed hash. Lon-run: git under /home/resources/x64 is refused by the classifier
# from the ceo and hq_B seats (GOAL-CEO CEO-283, CEO-286). rc 0 = pushed and proven on origin/main · rc 1 = push not proven · rc 2 = refused.
set -u
R=/home/resources/x64; O=/home/resources/ORACLES.md; WANT=bc694a0cc699f91d06ff7fde01732000
st="$(git -C "$R" status --short | grep -v '^??' | sort | tr -s ' ' | tr '\n' '|')"
[ "$st" = "M bin/sbl|M sbl.min|" ] || { echo "REFUSED rc=2: expected exactly 'M bin/sbl' and 'M sbl.min' tracked changes, saw: ${st:-<none>}"; exit 2; }
have="$(md5sum "$R/bin/sbl" | cut -c1-32)"
[ "$have" = "$WANT" ] || { echo "REFUSED rc=2: bin/sbl md5 $have is not the installed fix $WANT"; exit 2; }
[ "$(git -C "$R" branch --show-current)" = main ] || { echo "REFUSED rc=2: not on main"; exit 2; }
git -C "$R" config user.name LCherryholmes; git -C "$R" config user.email lcherryh@yahoo.com
git -C "$R" add bin/sbl sbl.min
git -C "$R" commit -q -F - <<'MSG'
sbl.min: the eleven trace/cnc dispatch constants compared in the folded form, bin/sbl rebuilt -- the fork refused every documented TRACE type with ERROR 199

Found by hq_B 2026-09-05 (row snobol4-oracle-sbl-trace-dispatch-constants-fixed-in-the-fork-and-swapped, rank 0, RULES.md sec Oracles STOP-AND-FIX): the x64 fork folds names and refused every TRACE type; stock upstream traces only because a translator bug there compensates the same folded constants; the shared sbl.min carried the defect for both. The fix kept the fork's flc and repaired the eleven constants (never the three-line translator revert). Staged as .github/scripts/fix_sbl_trace_dispatch.sh: dry run 4/4 acceptance in one binary; 180-fixture snoflake census, exactly the 8 trace fixtures change, zero collateral; byte-identical with stock upstream on the free-pass witnesses and on all six exact-mode trace witnesses (hq_P). Installed by Lon 2026-09-05 10:34:17 CDT (20260905T153417Z); backup bin/sbl.bak-20260905T153417Z beside it; installed md5 bc694a0cc699f91d06ff7fde01732000. Broadcast to all 16 seats and 4 HQs at 10:3x: any board or ref measured before 10:34 on a program that calls TRACE or sets &FTRACE is re-measured, everything else stands (GOAL-CEO CEO-284, CEO-286).
MSG
h="$(git -C "$R" rev-parse --short HEAD)"
git -C "$R" push -q origin main || { echo "push failed"; exit 1; }
git -C "$R" fetch -q origin
git -C "$R" log origin/main -1 --format='%h' | grep -q "^$h" || { echo "NOT PROVEN: origin/main is $(git -C "$R" log origin/main -1 --format=%h), local $h"; exit 1; }
echo "LANDED on origin/main: $h  $(git -C "$R" log -1 --format='%an <%ae>')"
python3 - "$O" "$h" "$(date '+%H:%M')" <<'PY'
import sys
p,h,now=sys.argv[1:4]
s=open(p,encoding='utf-8').read()
line=('⭐ **SWAPPED 2026-09-05 10:34:17 CDT by Lon (`.github/scripts/fix_sbl_trace_dispatch.sh`, staged by hq_B under RULES.md § Oracles STOP-AND-FIX; committed '+now+' CDT by `commit_sbl_trace_fork.sh`):** '
 '`/home/resources/x64/bin/sbl` is the build of fork commit `'+h+'` — `sbl.min`\'s eleven trace/cnc dispatch constants repaired so every documented TRACE type is accepted and a bogus type still reads ERROR 199; '
 'md5 `bc694a0cc699f91d06ff7fde01732000`; backup `bin/sbl.bak-20260905T153417Z`; 8 of 180 snoflake fixtures change, all the trace class; byte-identical with stock upstream on the free-pass witnesses and the six exact-mode trace witnesses. '
 'Any board or ref measured before 10:34 on a program that calls TRACE or sets &FTRACE is re-measured; everything else stands (GOAL-CEO CEO-284, CEO-286).\n\n')
key='⭐ **SWAPPED 2026-09-04 18:19 CDT'
i=s.find(key)
if i<0: sys.exit('ORACLES.md: 09-04 SWAPPED line not found; not edited')
open(p,'w',encoding='utf-8',newline='\n').write(s[:i]+line+s[i:]); print('ORACLES.md top line written naming',h)
PY
