#!/usr/bin/env bash
# populate_coo_root.sh -- stock /home/claude_coo, THE COO SEAT (identity coo; Lon 2026-09-06 17:42 "I create /home/claude_coo which is ready for you to populate."), the way the cto root was stocked
# 2026-09-06 (GOAL-CEO CEO-358; populate_cto_root.sh is the parent): local clones of the ceo root's three repos re-pointed at GitHub and fast-forwarded,
# ONE-IDENTITY config, the commit-msg + pre-commit hooks, refs/ symlinks into /home/resources, .claude/settings.json
# with the Stop banner + UserPromptSubmit inbox hook for d=/home/claude_coo, CLAUDE.md from .github/COO-CLAUDE.md,
# an empty .scratch/. Idempotent: every step is skipped when its result is already on disk. The build is NOT run
# here (see the tail): `make -C /home/claude_coo/SCRIP` is the COO's own first step per its digest.
#   bash /home/claude_ceo/.github/scripts/populate_coo_root.sh
# rc 0 = stocked and verified · rc 2 = refused (root absent, or a repo did not fast-forward), nothing half-done is hidden.
set -u
COO=/home/claude_coo; SRC=/home/claude_ceo; ORG=git@github.com:snobol4ever
[ -d "$COO" ] || { echo "REFUSED rc=2: $COO does not exist -- Lon creates the root"; exit 2; }
for r in SCRIP corpus .github; do
  if [ ! -d "$COO/$r/.git" ]; then
    git clone -q "$SRC/$r" "$COO/$r" || { echo "REFUSED rc=2: clone of $r failed"; exit 2; }
  fi
  git -C "$COO/$r" remote set-url origin "$ORG/$r.git"
  git -C "$COO/$r" config user.name  LCherryholmes
  git -C "$COO/$r" config user.email lcherryh@yahoo.com
  git -C "$COO/$r" fetch -q origin || { echo "REFUSED rc=2: fetch of $r failed"; exit 2; }
  git -C "$COO/$r" merge -q --ff-only origin/main || { echo "REFUSED rc=2: $r did not fast-forward to origin/main"; exit 2; }
  printf '%-8s %s origin=%s user=%s\n' "$r" "$(git -C "$COO/$r" rev-parse --short HEAD)" "$(git -C "$COO/$r" remote get-url origin)" "$(git -C "$COO/$r" config user.name)"
done
bash "$COO/SCRIP/scripts/install_commit_msg_hook.sh" && echo "hooks: $(ls "$COO"/SCRIP/.git/hooks | grep -v sample | tr '\n' ' ')"
mkdir -p "$COO/SCRIP/refs" "$COO/.scratch" "$COO/.claude"
for l in icon-master jcon-master rakudo-main; do ln -sfn "/home/resources/$l" "$COO/SCRIP/refs/$l"; done
ln -sfn /home/resources/roast-master "$COO/SCRIP/refs/roast"
echo "refs: $(ls "$COO/SCRIP/refs" | tr '\n' ' ')"
if [ ! -f "$COO/.claude/settings.json" ]; then
cat > "$COO/.claude/settings.json" <<'JSON'
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "d=/home/claude_coo; out=$(timeout 100 bash \"$d/SCRIP/scripts/s4e_msg.sh\" banner 2>&1); printf '%s' \"$out\" | python3 -c 'import json,sys; print(json.dumps(dict(systemMessage=sys.stdin.read())))'",
            "timeout": 120,
            "statusMessage": "Firing coo banner"
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "out=$(timeout 20 bash /home/claude_coo/SCRIP/scripts/s4e_inbox_hook.sh 2>&1); printf '%s' \"$out\" | python3 -c 'import json,sys; print(json.dumps({\"hookSpecificOutput\":{\"hookEventName\":\"UserPromptSubmit\",\"additionalContext\":sys.stdin.read()}}))'",
            "timeout": 30,
            "statusMessage": "Checking coo inbox"
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
python3 -c 'import json,sys; json.load(open(sys.argv[1]))' "$COO/.claude/settings.json" && echo "settings.json: valid JSON, hooks for d=$COO"
[ -f "$COO/CLAUDE.md" ] || cp "$COO/.github/COO-CLAUDE.md" "$COO/CLAUDE.md"
head -1 "$COO/CLAUDE.md"
for d in inbox archive; do mkdir -p "/home/resources/postoffice/coo/$d"; done
[ -s /home/resources/postoffice/coo/HQ ] || echo ceo > /home/resources/postoffice/coo/HQ
echo "postoffice coo: HQ=$(cat /home/resources/postoffice/coo/HQ) inbox=$(ls /home/resources/postoffice/coo/inbox | wc -l) msgs"
( cd "$COO/SCRIP" && bash scripts/s4e_msg.sh check 2>&1 | head -1 )
echo "STOCKED $COO -- next: make -C $COO/SCRIP (the COO's first step); the digest gate reads $COO/CLAUDE.md from here on"
