#!/usr/bin/env bash
# spawn_fleet.sh [--dry] [--stagger S] [--all | SEAT...] -- THE FLEET FIRES BACK FROM ONE COMMAND (the cio, 2026-11-05; Lon, in the cio's window 15:5x CST,
# verbatim: "What I would prefer versus manually SPAWNING the fleet which takes 30 minutes, but instead a shell script that fires a process with a window
# being the claude executable with proper title based on seat name and proper model and effort on the command-line."). One gnome-terminal window per seat,
# titled by the seat's name, working directory the seat's root, running `claude --name NAME --model MODEL --effort EFFORT` -- the three the box controller
# and the postoffice read (the controller lowercases the name and turns - into _ for the postoffice identity). The table below is the fleet (Lon's org
# model, MODE 2026-11-05 15:1x: Fable 5.1 high for the cio and cto, Opus for the CxOs, Sonnet 5.5 xhigh for the four company men, Haiku 5.5 xhigh for
# the twenty workers); edit the table, never a window by hand. A seat whose `claude --name NAME` already runs is skipped, never doubled; a seat whose
# root is missing is refused and named. --stagger S seconds between windows (default 4: twenty-nine sessions starting at once would spike the box).
# Models and efforts as Lon names them (15:5x: "models are fable-5-5 opus-5-5 sonnet-5-5 haiku-5-5", efforts xhigh high medium); claude 2.1.318 has no --color flag
# (the color is the /color command inside a session), so the window title is the seat's mark. Lon runs the copy at /home/satirical/spawn_fleet.sh; the source is .github/scripts/spawn_fleet.sh.
# --dry prints every command and opens nothing. The FLEET: line on MODE is the cio's to remove on Lon's word; this script only opens the windows.
set -uo pipefail
DRY=0; STAGGER=4; SEATS=()
while [ $# -gt 0 ]; do case "$1" in --dry) DRY=1;; --stagger) STAGGER="${2:?seconds}"; shift;; --all) SEATS=(ALL);; -h|--help) sed -n '2,12p' "$0"; exit 0;; *) SEATS+=("$1");; esac; shift; done
[ ${#SEATS[@]} -gt 0 ] || { echo "usage: spawn_fleet.sh [--dry] [--stagger S] --all | SEAT..."; exit 2; }
# seat  NAME  root  model  effort
TABLE="$(cat <<'T'
cio	CIO	/home/claude_cio	fable-5-5	high
cto	CTO	/home/claude_cto	fable-5-5	high
coo	COO	/home/claude_coo	opus-5-5	xhigh
cfo	CFO	/home/claude_cfo	opus-5-5	high
cao	CAO	/home/claude_cao	opus-5-5	high
cqo	CQO	/home/claude_cqo	opus-5-5	high
president	PRESIDENT	/home/claude_president	sonnet-5-5	xhigh
vice_president	VICE-PRESIDENT	/home/claude_vice_president	sonnet-5-5	xhigh
secretary	SECRETARY	/home/claude_secretary	sonnet-5-5	xhigh
manager	MANAGER	/home/claude_manager	sonnet-5-5	xhigh
T
)"
for n in $(seq -w 1 20); do TABLE="$TABLE
worker_$n	WORKER_$n	/home/claude_worker_$n	haiku-5-5	xhigh"; done
command -v gnome-terminal >/dev/null || { echo "REFUSE(2): no gnome-terminal on PATH"; exit 2; }
[ "$DRY" = 1 ] || [ -n "${DISPLAY:-}${WAYLAND_DISPLAY:-}" ] || { echo "REFUSE(2): no DISPLAY or WAYLAND_DISPLAY -- run this from a desktop terminal of the box"; exit 2; }
opened=0; skipped=0; refused=0
while IFS=$'\t' read -r seat name root model effort; do
    [ -n "$seat" ] || continue
    if [ "${SEATS[0]}" != ALL ]; then want=0; for s in "${SEATS[@]}"; do [ "$s" = "$seat" ] || [ "$s" = "$name" ] && want=1; done; [ $want = 1 ] || continue; fi
    if [ ! -d "$root" ] || [ ! -f "$root/CLAUDE.md" ]; then echo "REFUSED $seat: root $root missing or unpopulated"; refused=$((refused+1)); continue; fi
    if pgrep -f "^claude --name $name( |$)" >/dev/null; then echo "SKIP    $seat: claude --name $name already runs (pid $(pgrep -f "^claude --name $name( |$)" | head -1))"; skipped=$((skipped+1)); continue; fi
    cmd="claude --name $name --model $model --effort $effort"
    echo "OPEN    $seat: gnome-terminal --title=$name --working-directory=$root -- $cmd"
    if [ "$DRY" = 0 ]; then
        gnome-terminal --title="$name" --working-directory="$root" -- bash -lc "cd '$root' && exec $cmd" >/dev/null 2>&1 || { echo "REFUSED $seat: gnome-terminal did not open"; refused=$((refused+1)); continue; }
        opened=$((opened+1)); sleep "$STAGGER"
    fi
done <<< "$TABLE"
echo "SPAWN_FLEET opened=$opened skipped=$skipped refused=$refused dry=$DRY -- the FLEET: line on MODE is removed by the cio on Lon's word; the coo assigns by row"
[ $refused = 0 ]
