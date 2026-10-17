#!/usr/bin/env bash
# land_harness_in_roots.sh -- THE SWITCH-OVER FOR EVERY ROOT (ceo CEO-1819/1820): clone snobol4ever/harness as a sibling of SCRIP, corpus and
# .github in each /home/claude_* root that lacks it, install the org's commit-msg hook in it, and re-point the root's two Claude hooks
# (the Stop banner and the UserPromptSubmit inbox check) from <root>/SCRIP/scripts/ to <root>/harness/scripts/. The port roots
# (/home/claude_dotnet, /home/claude_jvm) borrowed the ceo root's SCRIP for the bus; they now run it from their own harness clone.
# Idempotent: a root that already has harness and re-pointed hooks prints its state and is left alone. It pulls NOTHING else: each seat
# pulls its own SCRIP, corpus and .github on HOLD LIFTED (their SCRIP/scripts directory leaves with that pull).
#   bash /home/claude_ceo/.github/scripts/land_harness_in_roots.sh            every root
#   bash /home/claude_ceo/.github/scripts/land_harness_in_roots.sh /home/claude_x   one root
# rc 0 every root stocked · rc 2 a clone or a hook rewrite failed (named), the rest still done.
set -u
ORG=git@github.com:snobol4ever; rc=0
roots="${1:-$(ls -d /home/claude_* 2>/dev/null)}"
for R in $roots; do
  [ -d "$R/corpus/.git" ] || [ -d "$R/SCRIP/.git" ] || { echo "skip   $R (no corpus or SCRIP clone)"; continue; }
  if [ ! -d "$R/harness/.git" ]; then
    git clone -q "$ORG/harness.git" "$R/harness" || { echo "⛔ $R: clone of harness failed"; rc=2; continue; }
  fi
  git -C "$R/harness" config user.name LCherryholmes; git -C "$R/harness" config user.email lcherryh@yahoo.com
  git -C "$R/harness" fetch -q origin && git -C "$R/harness" merge -q --ff-only origin/main 2>/dev/null
  H="$R/harness/scripts/lib_commit_msg_hook.txt"
  for g in "$R"/*/.git "$R"/.github/.git; do [ -d "$g" ] && [ ! -f "$g/hooks/commit-msg" ] && [ -f "$H" ] && { cp "$H" "$g/hooks/commit-msg"; chmod +x "$g/hooks/commit-msg"; }; done
  s="$R/.claude/settings.json"
  if [ -f "$s" ]; then
    python3 - "$s" "$R" <<'PY' || { echo "⛔ $R: settings.json could not be re-pointed"; rc=2; }
import json, sys, re
p, r = sys.argv[1], sys.argv[2]
t = open(p, encoding='utf-8').read(); o = t
t = t.replace('/home/claude_ceo/SCRIP/scripts/', r + '/harness/scripts/')          # the port roots borrowed the ceo root's bus
t = re.sub(r'(/home/claude_[a-z0-9]+)/SCRIP/scripts/', r'\1/harness/scripts/', t)   # every other root's own bus
t = t.replace('$d/SCRIP/scripts/', '$d/harness/scripts/')
json.loads(t)
assert '/SCRIP/scripts/' not in t, 'a hook still names SCRIP/scripts'
if t != o: open(p, 'w', encoding='utf-8', newline='\n').write(t)
PY
  fi
  printf '%-24s harness=%s hooks=%s\n' "$R" "$(git -C "$R/harness" rev-parse --short HEAD 2>/dev/null || echo MISSING)" \
    "$([ -f "$s" ] && { grep -q '/harness/scripts/' "$s" && echo harness || echo UNCHANGED; } || echo none)"
done
exit $rc
