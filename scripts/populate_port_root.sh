#!/usr/bin/env bash
# populate_port_root.sh -- stock /home/claude_dotnet (HQ-DOTNET, the seat for snobol4ever/snobol4dotnet) or /home/claude_jvm (HQ-JVM,
# the seat for snobol4ever/snobol4jvm), opened by Lon 2026-10-17 (in-chat to the ceo, verbatim: "We need to create two new HQ seats and
# their corresponding root folders (I'll do that part) for finishing and polishing snobol4ever/snobol4dotnet and snobol4ever/snobol4jvm.
# Call them HQ-DOTNET and HQ-JVM." · "These two roots will need corpus and .github but not SCRIP." · "These two HQ's have ZERO to do
# with SCRIP. Not related at all."; GOAL-CEO CEO-1817). A root holds THREE clones -- the seat's own port repo, corpus (the SNOBOL4
# programs and their SPITBOL refs) and .github (the org brain and the seat's GOAL file) -- re-pointed at GitHub and fast-forwarded,
# with the ONE-IDENTITY config and the org's commit-msg hook (no Claude trailers) in each. Lon, the same sitting: "These two HQ's will
# certainly need to be fully apart of our fleet, they just happen not to be SCRIP." -- so the seat is ON THE POSTOFFICE like every other:
# its box hq_<seat>/{inbox,archive} with an HQ file naming the cfo, and .claude/settings.json derived from the cto's (Stop banner +
# UserPromptSubmit inbox hook), the bus run from the ceo root's SCRIP scripts with S4E_HOME naming this root (no SCRIP clone here);
# CLAUDE.md from .github/HQ-<SEAT>-CLAUDE.md; an empty .scratch/. Idempotent: every step is skipped when its result is already on disk.
#   bash /home/claude_ceo/.github/scripts/populate_port_root.sh dotnet
#   bash /home/claude_ceo/.github/scripts/populate_port_root.sh jvm
# rc 0 = stocked and verified · rc 2 = refused (bad argument, root absent, or a repo did not fast-forward); nothing half-done is hidden.
set -u
case "${1:-}" in
  dotnet) PORT=snobol4dotnet; DIGEST=HQ-DOTNET-CLAUDE.md;;
  jvm)    PORT=snobol4jvm;    DIGEST=HQ-JVM-CLAUDE.md;;
  *) echo "REFUSED rc=2: usage: populate_port_root.sh dotnet|jvm"; exit 2;;
esac
SEAT="hq_$1"; R="/home/claude_$1"; SRC=/home/claude_ceo; ORG=git@github.com:snobol4ever; PO=/home/resources/postoffice; BUS="$R/harness/scripts"
HOOK="$SRC/harness/scripts/lib_commit_msg_hook.txt"
[ -d "$R" ] || { echo "REFUSED rc=2: $R does not exist -- Lon creates the root"; exit 2; }
[ -f "$SRC/.github/$DIGEST" ] || { echo "REFUSED rc=2: $SRC/.github/$DIGEST is missing -- pull .github first"; exit 2; }
[ -f "$HOOK" ] || { echo "REFUSED rc=2: the org commit-msg hook text $HOOK is missing"; exit 2; }
/usr/bin/grep -q "ME=$SEAT;;" "$SRC/harness/scripts/s4e_msg.sh" || { echo "REFUSED rc=2: the bus does not know $SEAT yet -- pull harness in $SRC first"; exit 2; }
for r in "$PORT" corpus harness .github; do
  if [ ! -d "$R/$r/.git" ]; then
    git clone -q "$SRC/$r" "$R/$r" || { echo "REFUSED rc=2: clone of $r failed"; exit 2; }
  fi
  git -C "$R/$r" remote set-url origin "$ORG/$r.git"
  git -C "$R/$r" config user.name  LCherryholmes
  git -C "$R/$r" config user.email lcherryh@yahoo.com
  git -C "$R/$r" fetch -q origin || { echo "REFUSED rc=2: fetch of $r failed"; exit 2; }
  git -C "$R/$r" checkout -q main 2>/dev/null || git -C "$R/$r" checkout -q -B main origin/main
  git -C "$R/$r" merge -q --ff-only origin/main || { echo "REFUSED rc=2: $r did not fast-forward to origin/main"; exit 2; }
  [ -f "$R/$r/.git/hooks/commit-msg" ] || { cp "$HOOK" "$R/$r/.git/hooks/commit-msg"; chmod +x "$R/$r/.git/hooks/commit-msg"; }
  printf '%-14s %s origin=%s user=%s hook=%s\n' "$r" "$(git -C "$R/$r" rev-parse --short HEAD)" "$(git -C "$R/$r" remote get-url origin)" \
    "$(git -C "$R/$r" config user.name)" "$([ -x "$R/$r/.git/hooks/commit-msg" ] && echo commit-msg || echo MISSING)"
done
mkdir -p "$R/.scratch" "$R/.claude"
if [ ! -f "$R/.claude/settings.json" ]; then
  python3 - "$R" "$SEAT" "$BUS" <<'PY' || { echo "REFUSED rc=2: settings.json could not be derived from the cto's"; exit 2; }
import json, sys
r, seat, bus = sys.argv[1], sys.argv[2], sys.argv[3]
s = open('/home/claude_cto/.claude/settings.json', encoding='utf-8').read()
s = s.replace('d=/home/claude_cto; out=$(timeout 100 bash \\"$d/harness/scripts/s4e_msg.sh\\" banner',
              'd=%s; out=$(S4E_HOME=$d timeout 100 bash \\"%s/s4e_msg.sh\\" banner' % (r, bus))
s = s.replace('out=$(timeout 20 bash /home/claude_cto/harness/scripts/s4e_inbox_hook.sh',
              'out=$(S4E_HOME=%s timeout 20 bash %s/s4e_inbox_hook.sh' % (r, bus))
s = s.replace('Firing cto banner', 'Firing %s banner' % seat).replace('Checking cto inbox', 'Checking %s inbox' % seat)
json.loads(s)
assert '/home/claude_cto' not in s and s.count('S4E_HOME=') == 2, 'a hook command did not take the bus path'
open(r + '/.claude/settings.json', 'w', encoding='utf-8', newline='\n').write(s)
PY
fi
python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); assert d["includeCoAuthoredBy"] is False and sys.argv[2] in json.dumps(d)' "$R/.claude/settings.json" "$R" \
  && echo "settings.json: valid, attribution off, the banner and inbox hooks run the bus with S4E_HOME=$R"
[ -f "$R/CLAUDE.md" ] || cp "$R/.github/$DIGEST" "$R/CLAUDE.md"
head -1 "$R/CLAUDE.md" | cut -c1-120
for d in inbox archive; do mkdir -p "$PO/$SEAT/$d"; done
[ -s "$PO/$SEAT/HQ" ] || echo cfo > "$PO/$SEAT/HQ"
echo "postoffice $SEAT: HQ=$(cat "$PO/$SEAT/HQ") inbox=$(ls "$PO/$SEAT/inbox" | wc -l) msgs"
( cd "$R" && S4E_HOME="$R" bash "$BUS/s4e_msg.sh" check 2>&1 | head -1 )
echo "STOCKED $R -- next: Lon starts a Claude session in $R (its model is Lon's to seat)"
