#!/usr/bin/env bash
# populate_zetas_root.sh -- stock /home/claude_zetas, THE SEAT HQ-ZETAS (identity hq_zetas), opened by Lon 2026-10-07
# (in-chat to the ceo, verbatim: "Would there be a HQ-THREE-ZETAS to mirror HQ-COLLECTOR, one for stack and one for heap?" and
# "Okay. I will create /home/claude_zetas in a minute."; GOAL-CEO CEO-1539), exactly the way
# populate_templates_root.sh stocked HQ-TEMPLATES: local clones of the ceo root's three repos re-pointed at GitHub and fast-forwarded,
# ONE-IDENTITY config, the commit-msg + pre-commit hooks, .claude/settings.json derived from the cto's (Stop banner +
# UserPromptSubmit inbox hook) with the root re-pointed, CLAUDE.md from .github/HQ-ZETAS-CLAUDE.md, an empty .scratch/, and the
# postoffice box hq_zetas/{inbox,archive} with its HQ file naming the cto (its officer, the owner of the spine and the frame law). Idempotent: every
# step is skipped when its result is already on disk. The build is NOT run here: `make -C /home/claude_zetas/SCRIP` is the seat's
# own first step.
#   bash /home/claude_ceo/.github/scripts/populate_zetas_root.sh
# rc 0 = stocked and verified · rc 2 = refused (root absent, or a repo did not fast-forward), nothing half-done is hidden.
set -u
R=/home/claude_zetas; SRC=/home/claude_ceo; ORG=git@github.com:snobol4ever; PO=/home/resources/postoffice
[ -d "$R" ] || { echo "REFUSED rc=2: $R does not exist -- Lon creates the root"; exit 2; }
for r in SCRIP corpus .github; do
  if [ ! -d "$R/$r/.git" ]; then
    git clone -q "$SRC/$r" "$R/$r" || { echo "REFUSED rc=2: clone of $r failed"; exit 2; }
  fi
  git -C "$R/$r" remote set-url origin "$ORG/$r.git"
  git -C "$R/$r" config user.name  LCherryholmes
  git -C "$R/$r" config user.email lcherryh@yahoo.com
  git -C "$R/$r" fetch -q origin || { echo "REFUSED rc=2: fetch of $r failed"; exit 2; }
  git -C "$R/$r" checkout -q main 2>/dev/null || git -C "$R/$r" checkout -q -B main origin/main
  git -C "$R/$r" merge -q --ff-only origin/main || { echo "REFUSED rc=2: $r did not fast-forward to origin/main"; exit 2; }
  printf '%-8s %s origin=%s user=%s\n' "$r" "$(git -C "$R/$r" rev-parse --short HEAD)" "$(git -C "$R/$r" remote get-url origin)" "$(git -C "$R/$r" config user.name)"
done
bash "$R/SCRIP/scripts/install_commit_msg_hook.sh" && echo "hooks: $(ls "$R"/SCRIP/.git/hooks | grep -v sample | tr '\n' ' ')"
mkdir -p "$R/.scratch" "$R/.claude"
if [ ! -f "$R/.claude/settings.json" ]; then
  python3 - "$R" <<'PY' || { echo "REFUSED rc=2: settings.json could not be derived from the cto's"; exit 2; }
import json, sys
r = sys.argv[1]
s = open('/home/claude_cto/.claude/settings.json', encoding='utf-8').read()
s = s.replace('/home/claude_cto', r).replace('Firing cto banner', 'Firing hq_zetas banner').replace('Checking cto inbox', 'Checking hq_zetas inbox')
json.loads(s)
assert '/home/claude_cto' not in s
open(r + '/.claude/settings.json', 'w', encoding='utf-8', newline='\n').write(s)
PY
fi
python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); assert "/home/claude_zetas" in json.dumps(d)' "$R/.claude/settings.json" && echo "settings.json: valid JSON, hooks for d=$R"
[ -f "$R/CLAUDE.md" ] || cp "$R/.github/HQ-ZETAS-CLAUDE.md" "$R/CLAUDE.md"
head -3 "$R/CLAUDE.md" | tail -1 | cut -c1-120
for d in inbox archive; do mkdir -p "$PO/hq_zetas/$d"; done
[ -s "$PO/hq_zetas/HQ" ] || echo cto > "$PO/hq_zetas/HQ"
echo "postoffice hq_zetas: HQ=$(cat "$PO/hq_zetas/HQ") inbox=$(ls "$PO/hq_zetas/inbox" | wc -l) msgs"
( cd "$R/SCRIP" && bash scripts/s4e_msg.sh check 2>&1 | head -1 )
echo "STOCKED $R -- next: start a Claude session in $R (its model is Lon's to seat); its first step is make -C $R/SCRIP; the digest gate reads $R/CLAUDE.md from here on"
