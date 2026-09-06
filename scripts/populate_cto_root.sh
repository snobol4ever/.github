#!/usr/bin/env bash
# populate_cto_root.sh -- stock /home/claude_cto, THE CTO SEAT (identity cto), the way seats 17-20 were stocked
# 2026-09-05 (GOAL-CEO CEO-292): local clones of the ceo root's three repos re-pointed at GitHub and fast-forwarded,
# ONE-IDENTITY config, the commit-msg + pre-commit hooks, refs/ symlinks into /home/resources, .claude/settings.json
# with the Stop banner + UserPromptSubmit inbox hook for d=/home/claude_cto, CLAUDE.md from .github/CTO-CLAUDE.md,
# an empty .scratch/. Idempotent: every step is skipped when its result is already on disk. The build is NOT run
# here (see the tail): `make -C /home/claude_cto/SCRIP` is the CTO's own first step per its digest.
#   bash /home/claude_ceo/.github/scripts/populate_cto_root.sh
# rc 0 = stocked and verified · rc 2 = refused (root absent, or a repo did not fast-forward), nothing half-done is hidden.
set -u
CTO=/home/claude_cto; SRC=/home/claude_ceo; ORG=git@github.com:snobol4ever
[ -d "$CTO" ] || { echo "REFUSED rc=2: $CTO does not exist -- Lon creates the root"; exit 2; }
for r in SCRIP corpus .github; do
  if [ ! -d "$CTO/$r/.git" ]; then
    git clone -q "$SRC/$r" "$CTO/$r" || { echo "REFUSED rc=2: clone of $r failed"; exit 2; }
  fi
  git -C "$CTO/$r" remote set-url origin "$ORG/$r.git"
  git -C "$CTO/$r" config user.name  LCherryholmes
  git -C "$CTO/$r" config user.email lcherryh@yahoo.com
  git -C "$CTO/$r" fetch -q origin || { echo "REFUSED rc=2: fetch of $r failed"; exit 2; }
  git -C "$CTO/$r" merge -q --ff-only origin/main || { echo "REFUSED rc=2: $r did not fast-forward to origin/main"; exit 2; }
  printf '%-8s %s origin=%s user=%s\n' "$r" "$(git -C "$CTO/$r" rev-parse --short HEAD)" "$(git -C "$CTO/$r" remote get-url origin)" "$(git -C "$CTO/$r" config user.name)"
done
bash "$CTO/SCRIP/scripts/install_commit_msg_hook.sh" && echo "hooks: $(ls "$CTO"/SCRIP/.git/hooks | grep -v sample | tr '\n' ' ')"
mkdir -p "$CTO/SCRIP/refs" "$CTO/.scratch" "$CTO/.claude"
for l in icon-master jcon-master rakudo-main; do ln -sfn "/home/resources/$l" "$CTO/SCRIP/refs/$l"; done
ln -sfn /home/resources/roast-master "$CTO/SCRIP/refs/roast"
echo "refs: $(ls "$CTO/SCRIP/refs" | tr '\n' ' ')"
if [ ! -f "$CTO/.claude/settings.json" ]; then
cat > "$CTO/.claude/settings.json" <<'JSON'
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "d=/home/claude_cto; out=$(timeout 100 bash \"$d/SCRIP/scripts/s4e_msg.sh\" banner 2>&1); printf '%s' \"$out\" | python3 -c 'import json,sys; print(json.dumps(dict(systemMessage=sys.stdin.read())))'",
            "timeout": 120,
            "statusMessage": "Firing cto banner"
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "out=$(timeout 20 bash /home/claude_cto/SCRIP/scripts/s4e_inbox_hook.sh 2>&1); printf '%s' \"$out\" | python3 -c 'import json,sys; print(json.dumps({\"hookSpecificOutput\":{\"hookEventName\":\"UserPromptSubmit\",\"additionalContext\":sys.stdin.read()}}))'",
            "timeout": 30,
            "statusMessage": "Checking cto inbox"
          }
        ]
      }
    ]
  },
  "includeCoAuthoredBy": false,
  "attribution": {
    "commit": "",
    "pr": "",
    "sessionUrl": false
  }
}
JSON
fi
python3 -c 'import json,sys; json.load(open(sys.argv[1]))' "$CTO/.claude/settings.json" && echo "settings.json: valid JSON, hooks for d=$CTO"
[ -f "$CTO/CLAUDE.md" ] || cp "$CTO/.github/CTO-CLAUDE.md" "$CTO/CLAUDE.md"
head -1 "$CTO/CLAUDE.md"
for d in inbox archive; do mkdir -p "/home/resources/postoffice/cto/$d"; done
[ -s /home/resources/postoffice/cto/HQ ] || echo ceo > /home/resources/postoffice/cto/HQ
echo "postoffice cto: HQ=$(cat /home/resources/postoffice/cto/HQ) inbox=$(ls /home/resources/postoffice/cto/inbox | wc -l) msgs"
( cd "$CTO/SCRIP" && bash scripts/s4e_msg.sh check 2>&1 | head -1 )
echo "STOCKED $CTO -- next: make -C $CTO/SCRIP (the CTO's first step); the digest gate reads $CTO/CLAUDE.md from here on"
