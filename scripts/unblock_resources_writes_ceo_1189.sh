#!/usr/bin/env bash
# unblock_resources_writes_ceo_1189.sh -- LON RUNS THIS (the ceo's harness classifier refuses the ceo editing its own
# permissions and refuses its writes under /home/resources; Lon 2026-09-23 05:2x: "get those writes unblocked or give me a
# shell script to run").
#   1. Adds Bash allow rules for the fork-build writes to .claude/settings.local.json of the ceo root (default), of every
#      root named on the command line, or of all eleven roots with --all; a dated backup sits beside each file edited.
#   2. Installs the instrumented Icon oracle at /home/resources/icon-mon with build_icon_mon.sh (4 s, ends in its control
#      arm), so every seat's monitor_run.sh prog.icn --oracle finds the default prefix. --no-install skips it.
# Usage:  bash /home/claude_ceo/.github/scripts/unblock_resources_writes_ceo_1189.sh [--all | /home/claude_x ...] [--no-install]
set -uo pipefail
ROOTS=(); INSTALL=1
for a in "$@"; do
    case "$a" in
        --all) ROOTS=(/home/claude_ceo /home/claude_cto /home/claude_coo /home/claude_cfo /home/claude_icon /home/claude_prolog /home/claude_raku /home/claude_pascal /home/claude_snocone /home/claude_snobol4) ;;
        --no-install) INSTALL=0 ;;
        /*) ROOTS+=("$a") ;;
        *) echo "usage: $0 [--all | /home/claude_x ...] [--no-install]"; exit 2 ;;
    esac
done
[ "${#ROOTS[@]}" -gt 0 ] || ROOTS=(/home/claude_ceo)
STAMP=$(date +%Y%m%d-%H%M%S)
for R in "${ROOTS[@]}"; do
    F="$R/.claude/settings.local.json"
    [ -f "$F" ] || { echo "SKIP $R: no $F"; continue; }
    cp "$F" "$F.bak-unblock-$STAMP" || { echo "FAIL $R: could not back up $F"; continue; }
    python3 - "$F" <<'PY'
import json, sys
p = sys.argv[1]
d = json.load(open(p))
perm = d.setdefault('permissions', {})
allow = perm.setdefault('allow', [])
want = ["Bash(rsync:*)", "Bash(cp:*)", "Bash(mkdir:*)", "Bash(patch:*)", "Bash(make:*)", "Bash(cd /home/resources/:*)",
        "Bash(bash scripts/monitor/oracles/build_:*)", "Bash(bash SCRIP/scripts/monitor/oracles/build_:*)"]
added = [w for w in want if w not in allow]
allow.extend(added)
json.dump(d, open(p, 'w'), indent=2)
open(p, 'a').write("\n")
print(f"  {p}: {len(added)} rule(s) added, {len(allow)} allow rule(s) now")
PY
    python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$F" && echo "OK $R (backup $F.bak-unblock-$STAMP)" || { echo "FAIL $R: $F is not valid JSON after the edit -- restoring the backup"; cp "$F.bak-unblock-$STAMP" "$F"; }
done
if [ "$INSTALL" = 1 ]; then
    B=/home/claude_ceo/SCRIP/scripts/monitor/oracles/build_icon_mon.sh
    [ -f "$B" ] || { echo "SKIP install: $B missing (pull SCRIP)"; exit 0; }
    echo "--- installing the instrumented Icon oracle at /home/resources/icon-mon"
    ICON_PRISTINE=/home/resources/icon-master bash "$B" /home/resources/icon-mon; rc=$?
    echo "build_icon_mon rc=$rc"
    [ "$rc" = 0 ] && ls -l /home/resources/icon-mon/bin/icont /home/resources/icon-mon/bin/iconx
fi
