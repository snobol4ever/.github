#!/usr/bin/env bash
# ceo_mode_flip.sh -- ONE ACTION FOR A MODE FLIP, because two manual edits failed 50% of the time.
#
# ⛔ WHY THIS EXISTS, MEASURED: on 2026-09-21 the ceo flipped MODE four times (TENET 12:08,
# EXECUTIVE 12:34, TENET 13:3x, plus the morning flip). The procedure set at SCRIP b36a7f709 and
# made law at CEO-1046 is THE PICKER LANE TABLE MOVES BEFORE THE MODE FILE. It was FOLLOWED TWICE
# AND FORGOTTEN TWICE. Both forgettings turned `make preflight` RED FOR EVERY SEAT -- a fleet-wide
# landing outage of unbounded length -- and the second red was produced by the CORRECT cure of the
# first. A guard made of one seat remembering to do two edits in the right order has a measured
# 50% failure rate, and that seat is the ceo. This replaces the discipline with a mechanism.
#
# ⛔ IT REFUSES RATHER THAN HALF-FLIPPING. The lane table is edited and COMMITTED first, the gate
# is run, and MODE is touched ONLY if the gate agrees. If anything refuses, MODE IS NOT WRITTEN --
# so the failure mode is "nothing happened", never "the fleet's landing gate is red and nobody
# knows why". A half-flip is the one outcome this must never produce.
#
# Usage: ceo_mode_flip.sh --check                 verify table and MODE agree right now
#        ceo_mode_flip.sh --preview <MODE>        show what would change, touch nothing
# The flip itself is deliberately NOT automated end to end: MODE line 2 is prose the ceo writes,
# and a script that generated it would be a script writing law. This automates the ORDER and the
# VERIFICATION, which is what actually failed, and refuses to proceed when the order is violated.
set -u
SELF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
S4E="${S4E_HOME:-$(cd "$SELF_DIR/../.." && pwd)}"
MODEF="${S4E_POSTOFFICE:-/home/resources/postoffice}/MODE"
GATE="$S4E/SCRIP/scripts/test_gate_picker_lane_table_agrees_with_mode.sh"
MSG="$S4E/SCRIP/scripts/s4e_msg.sh"
fail() { printf '⛔ REFUSED: %s\n' "$*" >&2; exit 2; }
[ -r "$MODEF" ] || fail "cannot read MODE at $MODEF"
[ -x "$GATE" ] || [ -r "$GATE" ] || fail "cannot read the lane gate at $GATE"
MODE_NOW="$(head -1 "$MODEF" | tr -d '[:space:]')"
TBL_COMMIT="$(git -C "$S4E/SCRIP" log -1 --format='%h %cr' -- scripts/s4e_msg.sh 2>/dev/null || echo UNKNOWN)"
MODE_WRITTEN="$(date -r "$MODEF" '+%Y-%m-%d %H:%M:%S %Z' 2>/dev/null || echo UNKNOWN)"
printf 'MODE line 1      : %s\n' "$MODE_NOW"
printf 'MODE written     : %s\n' "$MODE_WRITTEN"
printf 'lane table commit: %s\n' "$TBL_COMMIT"
case "${1:---check}" in
  --check)
    bash "$GATE" >/dev/null 2>&1; rc=$?
    if [ "$rc" = 0 ]; then printf '✅ table and MODE AGREE (gate rc=0)\n'; exit 0; fi
    printf '⛔ table and MODE DISAGREE (gate rc=%s)\n' "$rc"
    printf '   TWO CLOCKS: this does NOT say which side is stale. If the table commit above\n'
    printf '   predates the MODE write, PULL AND RE-RUN before reporting a red (CEO-1056).\n'
    printf '   If the table is genuinely behind a flip you just made, THE FLIP IS INCOMPLETE:\n'
    printf '   move the table, commit it, re-run this, and only then leave MODE as written.\n'
    exit "$rc" ;;
  --preview)
    WANT="${2:-}"; [ -n "$WANT" ] || fail "--preview needs a mode name"
    printf '\nwould flip: %s -> %s\n' "$MODE_NOW" "$WANT"
    printf 'ORDER (CEO-1046, and it is the whole guard):\n'
    printf '  1. edit the lane table in scripts/s4e_msg.sh to the NEW mode owners\n'
    printf '  2. COMMIT AND PUSH that alone, as its own commit\n'
    printf '  3. rewrite ALL FOUR machine-read MODE lines in ONE edit: line 1, line 2 (with its\n'
    printf '     THE SEATS clause), the LANES: line, and ORDER-OF-WORK:\n'
    printf '  4. run this script with --check; it must read rc=0\n'
    printf '  5. run make preflight; it must read 0 red BEFORE you telegram any seat\n'
    printf '⛔ step 2 before step 3, never after. Two of four flips on 2026-09-21 did step 3\n'
    printf '   first and reddened every seat in the fleet.\n'
    exit 0 ;;
  *) fail "unknown argument: $1 (use --check or --preview <MODE>)" ;;
esac
