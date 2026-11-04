#!/usr/bin/env bash
# propagate_banner_cached_cto_480.sh [--check] -- EVERY ROOT'S STOP HOOK PRINTS THE CACHED BANNER (the cto, 2026-11-04, CTO-480).
# The hook command becomes: if harness/scripts/s4e_banner_cached.sh exists in the root, run it (cache first, refresh in the background,
# never empty); else the previous inline command, kept verbatim as the fallback until the root's harness is fast-forwarded. The seat name is
# read from the hook's own statusMessage ("Firing <seat> banner"). settings.json is backed up beside itself. --check reports which roots differ.
CHECK=0; [ "${1:-}" = "--check" ] && CHECK=1
stamp=$(date +%Y%m%dT%H%M%S); roots=0; changed=0; same=0; skipped=0
for root in /home/claude_*; do
  [ -f "$root/CLAUDE.md" ] && [ -f "$root/.claude/settings.json" ] || continue; roots=$((roots+1))
  r=$(python3 - "$root/.claude/settings.json" "$root" "$CHECK" "$stamp" <<'PY'
import json, sys, re, shutil
st, root, check, stamp = sys.argv[1], sys.argv[2], sys.argv[3] == "1", sys.argv[4]
d = json.load(open(st)); hs = d.get("hooks", {}).get("Stop", []); changed = 0; present = 0
for h in hs:
    for k in h.get("hooks", []):
        cmd = k.get("command", "")
        if "s4e_banner_cached.sh" in cmd: present += 1; continue
        if 's4e_msg.sh" banner' not in cmd: continue
        m = re.search(r"Firing (\S+) banner", k.get("statusMessage", "")); seat = m.group(1) if m else root.rsplit("/claude_", 1)[1]
        k["command"] = ('d=%s; if [ -f "$d/harness/scripts/s4e_banner_cached.sh" ]; then bash "$d/harness/scripts/s4e_banner_cached.sh" "$d" %s; else %s; fi' % (root, seat, cmd))
        changed += 1
if changed and not check:
    shutil.copy(st, st + ".bak-" + stamp + "-cto-480"); json.dump(d, open(st, "w"), indent=2); open(st, "a").write("\n")
print("CHANGED" if changed else ("PRESENT" if present else "NO-BANNER-HOOK"))
PY
)
  case "$r" in CHANGED) changed=$((changed+1)); echo "${CHECK/1/WOULD-}CHANGE $root";; PRESENT) same=$((same+1));; *) skipped=$((skipped+1)); echo "SKIP $root ($r)";; esac
done
echo "BANNER_CACHED roots=$roots changed=$changed present=$same skipped=$skipped"
[ $CHECK = 1 ] && [ $changed -gt 0 ] && exit 1; exit 0
