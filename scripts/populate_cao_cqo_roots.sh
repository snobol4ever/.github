#!/usr/bin/env bash
# populate_cao_cqo_roots.sh -- stock /home/claude_cao (THE CAO, Chief Architecture Officer, identity cao, Fable 5.1 xhigh) and /home/claude_cqo (THE CQO,
# Chief Quality Officer, identity cqo, Opus 5.5 xhigh), opened by Lon 2026-10-30 (in-chat to the ceo, verbatim: "I like CAO and CQO so I will build those
# root folders." · "The two folders are created Go populate them. Thanks."; GOAL-CEO CEO-2025/2026). Copied from populate_packages_root.sh, one seat per
# argument. Each root gets the four sibling repos SCRIP, corpus, harness and .github (CEO-1817/1819, no symlink anywhere, CEO-1820), cloned from the ceo
# root, re-pointed at GitHub and fast-forwarded, with the ONE-IDENTITY config and the org's commit-msg hook in each. It also gets .claude/settings.json
# derived from the cto's (Stop banner + UserPromptSubmit inbox hook) with the root re-pointed, CLAUDE.md from .github/<SEAT>-CLAUDE.md, an empty
# .scratch/, and the postoffice box <seat>/{inbox,archive} with its HQ file naming the ceo. Idempotent: every step is skipped when its result is already
# on disk. The build is NOT run here: `make -j8 -C /home/claude_<seat>/SCRIP` is the seat's own first step.
#   bash /home/claude_ceo/.github/scripts/populate_cao_cqo_roots.sh            # both
#   bash /home/claude_ceo/.github/scripts/populate_cao_cqo_roots.sh cqo        # one
# rc 0 = stocked and verified · rc 2 = refused (root absent, the bus does not know the seat, or a repo did not fast-forward); nothing half-done is hidden.
set -u
SRC=/home/claude_ceo; ORG=git@github.com:snobol4ever; PO=/home/resources/postoffice
HOOK="$SRC/harness/scripts/lib_commit_msg_hook.txt"
[ -f "$HOOK" ] || { echo "REFUSED rc=2: the org commit-msg hook text $HOOK is missing"; exit 2; }
populate() {
  local SEAT="$1" R="/home/claude_$1" DIGEST; DIGEST="$(echo "$1" | tr a-z A-Z)-CLAUDE.md"
  echo "=== $SEAT -> $R"
  [ -d "$R" ] || { echo "REFUSED rc=2: $R does not exist -- Lon creates the root"; return 2; }
  [ -f "$SRC/.github/$DIGEST" ] || { echo "REFUSED rc=2: $SRC/.github/$DIGEST is missing -- pull .github in $SRC first"; return 2; }
  /usr/bin/grep -q "ME=$SEAT;;" "$SRC/harness/scripts/s4e_msg.sh" || { echo "REFUSED rc=2: the bus does not know $SEAT yet -- pull harness in $SRC first"; return 2; }
  for r in SCRIP corpus harness .github; do
    if [ ! -d "$R/$r/.git" ]; then
      git clone -q "$SRC/$r" "$R/$r" || { echo "REFUSED rc=2: clone of $r failed"; return 2; }
    fi
    git -C "$R/$r" remote set-url origin "$ORG/$r.git"
    git -C "$R/$r" config user.name  LCherryholmes
    git -C "$R/$r" config user.email lcherryh@yahoo.com
    git -C "$R/$r" fetch -q origin || { echo "REFUSED rc=2: fetch of $r failed"; return 2; }
    git -C "$R/$r" checkout -q main 2>/dev/null || git -C "$R/$r" checkout -q -B main origin/main
    git -C "$R/$r" merge -q --ff-only origin/main || { echo "REFUSED rc=2: $r did not fast-forward to origin/main"; return 2; }
    [ -f "$R/$r/.git/hooks/commit-msg" ] || { cp "$HOOK" "$R/$r/.git/hooks/commit-msg"; chmod +x "$R/$r/.git/hooks/commit-msg"; }
    printf '%-8s %s origin=%s user=%s hook=%s\n' "$r" "$(git -C "$R/$r" rev-parse --short HEAD)" "$(git -C "$R/$r" remote get-url origin)" \
      "$(git -C "$R/$r" config user.name)" "$([ -x "$R/$r/.git/hooks/commit-msg" ] && echo commit-msg || echo MISSING)"
  done
  mkdir -p "$R/.scratch" "$R/.claude"
  if [ ! -f "$R/.claude/settings.json" ]; then
    python3 - "$R" "$SEAT" <<'PY' || { echo "REFUSED rc=2: settings.json could not be derived from the cto's"; return 2; }
import json, sys
r, seat = sys.argv[1], sys.argv[2]
s = open('/home/claude_cto/.claude/settings.json', encoding='utf-8').read()
s = s.replace('/home/claude_cto', r).replace('Firing cto banner', 'Firing %s banner' % seat).replace('Checking cto inbox', 'Checking %s inbox' % seat)
json.loads(s)
assert '/home/claude_cto' not in s and s.count(r) == 2, 'a hook command was not re-pointed'
open(r + '/.claude/settings.json', 'w', encoding='utf-8', newline='\n').write(s)
PY
  fi
  python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); assert d["includeCoAuthoredBy"] is False and sys.argv[2] in json.dumps(d)' "$R/.claude/settings.json" "$R" \
    && echo "settings.json: valid, attribution off, the banner and inbox hooks run from $R/harness/scripts"
  [ -f "$R/CLAUDE.md" ] || cp "$R/.github/$DIGEST" "$R/CLAUDE.md"
  grep -m1 '^# CLAUDE.md — ' "$R/CLAUDE.md" | cut -c1-120
  for d in inbox archive; do mkdir -p "$PO/$SEAT/$d"; done
  [ -s "$PO/$SEAT/HQ" ] || echo ceo > "$PO/$SEAT/HQ"
  echo "postoffice $SEAT: HQ=$(cat "$PO/$SEAT/HQ") inbox=$(ls "$PO/$SEAT/inbox" | wc -l) msgs"
  ( cd "$R" && echo "whoami: $(bash harness/scripts/s4e_msg.sh whoami 2>&1 | head -1)" )
  echo "STOCKED $R -- next: start a Claude session in $R (its model is Lon's to seat); its first step is make -j8 -C $R/SCRIP"
}
rc=0
for s in "${@:-cao cqo}"; do for t in $s; do case "$t" in cao|cqo) populate "$t" || rc=2;; *) echo "REFUSED rc=2: $t is not cao or cqo"; rc=2;; esac; done; done
exit $rc
