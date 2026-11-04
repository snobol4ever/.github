#!/usr/bin/env bash
# propagate_banner_compact_ceo_2129.sh -- THE DOUBLE-SIDED BANNER ON EVERY SEAT'S STOP HOOK (Lon 2026-11-04, in-chat to the cto, verbatim: "In the
# display banner add a column for a delta/difference and distribute the new double-sided banner across the fleet."; CEO-2129).
# The banner a seat sees at every Stop is `s4e_msg.sh banner` piped through .claude/banner_compact.py (the two-column grid with the Δ column,
# source .github/scripts/banner_compact.py, first built in the cto's root 2026-11-03). This script copies the filter into every root's .claude/
# and rewrites the root's Stop hook command to pipe through it when present (the file's absence is guarded in the hook, so a root without the
# file keeps the plain banner; a hook written into settings reaches a running session at once). A settings.json is backed up beside itself
# before it is rewritten. --check reports without writing.
#   usage: propagate_banner_compact_ceo_2129.sh [--check]
CHECK=0; [ "${1:-}" = "--check" ] && CHECK=1
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/banner_compact.py"
[ -f "$SRC" ] || { echo "REFUSE(2): no $SRC"; exit 2; }
stamp=$(date +%Y%m%dT%H%M%S); roots=0; files=0; hooks=0; same=0; skipped=0
for root in /home/claude_*; do
  [ -f "$root/CLAUDE.md" ] && [ -d "$root/.claude" ] || continue; roots=$((roots+1))
  dst="$root/.claude/banner_compact.py"; st="$root/.claude/settings.json"
  if ! cmp -s "$SRC" "$dst"; then [ $CHECK = 1 ] && echo "FILE-DIFFERS $root" || { cp -p "$SRC" "$dst" && echo "FILE $root"; }; files=$((files+1)); fi
  [ -f "$st" ] || { echo "SKIP $root (no settings.json)"; skipped=$((skipped+1)); continue; }
  r=$(python3 - "$st" "$root" "$CHECK" "$stamp" <<'PY'
import json, sys, shutil
st, root, check, stamp = sys.argv[1], sys.argv[2], sys.argv[3] == "1", sys.argv[4]
d = json.load(open(st))
hs = d.get("hooks", {}).get("Stop", [])
import re
pat = re.compile(r'(out=\$\((?:S4E_HOME=\$d )?timeout 100 bash "[^"]*s4e_msg\.sh" banner 2>&1\);) printf')
clause = (r'\1 if [ -f "$d/.claude/banner_compact.py" ]; then '
          'c=$(printf \'%s\' "$out" | python3 -I "$d/.claude/banner_compact.py" 2>/dev/null) && [ -n "$c" ] && out="$c"; fi; printf')
changed = 0; present = 0
for h in hs:
    for k in h.get("hooks", []):
        c = k.get("command", "")
        if "banner_compact.py" in c: present += 1; continue
        if pat.search(c):
            k["command"] = pat.sub(clause, c, count=1); changed += 1
if changed and not check:
    shutil.copy2(st, st + ".bak-" + stamp + "-banner-compact")
    json.dump(d, open(st, "w"), indent=2); open(st, "a").write("\n")
print("HOOK-PRESENT" if present and not changed else ("HOOK-WRITTEN" if changed and not check else ("HOOK-WOULD-WRITE" if changed else "HOOK-NOT-FOUND")))
PY
)
  case "$r" in HOOK-PRESENT) same=$((same+1));; HOOK-WRITTEN|HOOK-WOULD-WRITE) hooks=$((hooks+1)); echo "$r $root";; *) echo "$r $root -- its Stop hook names no s4e_msg.sh banner; left alone"; skipped=$((skipped+1));; esac
done
echo "BANNER-COMPACT roots=$roots files_copied=$files hooks_rewritten=$hooks hooks_already=$same skipped=$skipped $([ $CHECK = 1 ] && echo '(check only)')"
[ $skipped = 0 ]
