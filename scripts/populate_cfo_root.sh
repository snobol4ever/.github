#!/usr/bin/env bash
# populate_cfo_root.sh -- stock /home/claude_cfo, THE CFO SEAT (identity cfo; Lon 2026-09-07 08:0x CDT "The /home/claude_cfo is ready to populate."), the way the cto root was stocked
# 2026-09-06 (GOAL-CEO CEO-358; populate_cto_root.sh is the parent): local clones of the ceo root's three repos re-pointed at GitHub and fast-forwarded,
# ONE-IDENTITY config, the commit-msg + pre-commit hooks, refs/ symlinks into /home/resources, .claude/settings.json
# with the Stop banner + UserPromptSubmit inbox hook for d=/home/claude_cfo, CLAUDE.md from .github/CFO-CLAUDE.md,
# an empty .scratch/. Idempotent: every step is skipped when its result is already on disk. The build is NOT run
# here (see the tail): `make -C /home/claude_cfo/SCRIP` is the CFO's own first step per its digest.
#   bash /home/claude_ceo/.github/scripts/populate_cfo_root.sh
# rc 0 = stocked and verified · rc 2 = refused (root absent, or a repo did not fast-forward), nothing half-done is hidden.
set -u
CFO=/home/claude_cfo; SRC=/home/claude_ceo; ORG=git@github.com:snobol4ever
[ -d "$CFO" ] || { echo "REFUSED rc=2: $CFO does not exist -- Lon creates the root"; exit 2; }
for r in SCRIP corpus .github; do
  if [ ! -d "$CFO/$r/.git" ]; then
    git clone -q "$SRC/$r" "$CFO/$r" || { echo "REFUSED rc=2: clone of $r failed"; exit 2; }
  fi
  git -C "$CFO/$r" remote set-url origin "$ORG/$r.git"
  git -C "$CFO/$r" config user.name  LCherryholmes
  git -C "$CFO/$r" config user.email lcherryh@yahoo.com
  git -C "$CFO/$r" fetch -q origin || { echo "REFUSED rc=2: fetch of $r failed"; exit 2; }
  git -C "$CFO/$r" merge -q --ff-only origin/main || { echo "REFUSED rc=2: $r did not fast-forward to origin/main"; exit 2; }
  printf '%-8s %s origin=%s user=%s\n' "$r" "$(git -C "$CFO/$r" rev-parse --short HEAD)" "$(git -C "$CFO/$r" remote get-url origin)" "$(git -C "$CFO/$r" config user.name)"
done
bash "$CFO/SCRIP/scripts/install_commit_msg_hook.sh" && echo "hooks: $(ls "$CFO"/SCRIP/.git/hooks | grep -v sample | tr '\n' ' ')"
mkdir -p "$CFO/SCRIP/refs" "$CFO/.scratch" "$CFO/.claude"
for l in icon-master jcon-master rakudo-main; do ln -sfn "/home/resources/$l" "$CFO/SCRIP/refs/$l"; done
ln -sfn /home/resources/roast-master "$CFO/SCRIP/refs/roast"
echo "refs: $(ls "$CFO/SCRIP/refs" | tr '\n' ' ')"
if [ ! -f "$CFO/.claude/settings.json" ]; then
cat > "$CFO/.claude/settings.json" <<'JSON'
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "d=/home/claude_cfo; out=$(timeout 100 bash \"$d/SCRIP/scripts/s4e_msg.sh\" banner 2>&1); printf '%s' \"$out\" | python3 -c 'import json,sys; print(json.dumps(dict(systemMessage=sys.stdin.read())))'",
            "timeout": 120,
            "statusMessage": "Firing cfo banner"
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "out=$(timeout 20 bash /home/claude_cfo/SCRIP/scripts/s4e_inbox_hook.sh 2>&1); printf '%s' \"$out\" | python3 -c 'import json,sys; print(json.dumps({\"hookSpecificOutput\":{\"hookEventName\":\"UserPromptSubmit\",\"additionalContext\":sys.stdin.read()}}))'",
            "timeout": 30,
            "statusMessage": "Checking cfo inbox"
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
python3 -c 'import json,sys; json.load(open(sys.argv[1]))' "$CFO/.claude/settings.json" && echo "settings.json: valid JSON, hooks for d=$CFO"
[ -f "$CFO/CLAUDE.md" ] || cp "$SRC/.github/CFO-CLAUDE.md" "$CFO/CLAUDE.md"
head -1 "$CFO/CLAUDE.md"
for d in inbox archive; do mkdir -p "/home/resources/postoffice/cfo/$d"; done
[ -s /home/resources/postoffice/cfo/HQ ] || echo ceo > /home/resources/postoffice/cfo/HQ
echo "postoffice cfo: HQ=$(cat /home/resources/postoffice/cfo/HQ) inbox=$(ls /home/resources/postoffice/cfo/inbox | wc -l) msgs"
( cd "$CFO/SCRIP" && bash scripts/s4e_msg.sh check 2>&1 | head -1 )
echo "STOCKED $CFO -- next: make -C $CFO/SCRIP (the CFO's first step); the digest gate reads $CFO/CLAUDE.md from here on"
