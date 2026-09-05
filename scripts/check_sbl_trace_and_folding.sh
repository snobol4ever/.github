#!/usr/bin/env bash
# check_sbl_trace_and_folding.sh [sbl]  -- ceo 2026-09-05 (CEO-282): the SPITBOL oracle's OWN self-test for row
# snobol4-oracle-sbl-trace-dispatch-constants-fixed-in-the-fork-and-swapped (hq_B's four acceptance tests, the two computable here).
# rc 0 = the binary traces TRACE(X,'VALUE') AND TRACE(Y,'value') under -bf AND still folds names under -b (abc==ABC prints 5);
# rc 1 = one arm red (today: the x64 fork refuses every trace type with ERROR 199); rc 2 = no binary. ⛔ The -b arm is the oracle's
# folding self-test on the oracle itself, never a grading arm for SCRIP (RULES.md: programs are graded under -bf, always).
set -u
O="${1:-/home/resources/x64/bin/sbl}"; [ -x "$O" ] || { echo "REFUSED rc=2: no oracle at $O"; exit 2; }
W=$(mktemp -d); trap 'rm -rf "$W"' EXIT
printf '\t&TRACE = 5\n\tTRACE("X", "VALUE")\n\tTRACE("Y", "value")\n\tX = 1\n\tY = 2\nEND\n' > "$W/t.sno"
printf '\tabc = 5\n\tOUTPUT = ABC\nEND\n' > "$W/f.sno"
t=$(timeout 8s "$O" -bf "$W/t.sno" </dev/null 2>&1); f=$(timeout 8s "$O" -b "$W/f.sno" </dev/null 2>&1)
rc=0
if printf '%s\n' "$t" | grep -q 'X = 1'; then echo "PASS: TRACE(X,'VALUE') traces"; else echo "RED: $O does not trace TRACE(X,'VALUE'): $(printf '%s' "$t" | grep -m1 ERROR)"; rc=1; fi
if printf '%s\n' "$t" | grep -q 'Y = 2'; then echo "PASS: TRACE(Y,'value') traces"; else echo "RED: lowercase type 'value' not traced"; rc=1; fi
if [ "$f" = "5" ]; then echo "PASS: abc==ABC under -b folding prints 5"; else echo "RED: folding broke: abc==ABC under -b must print 5, got [$f]"; rc=1; fi
echo "oracle=$O rc=$rc"; exit $rc
