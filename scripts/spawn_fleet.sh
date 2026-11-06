#!/usr/bin/env bash
# spawn_fleet.sh [--dry] [--table] [--stagger S] [--all | SEAT...] -- THE FLEET FIRES BACK FROM ONE COMMAND (the cio, 2026-11-05; Lon, in the cio's window 15:5x CST,
# verbatim: "What I would prefer versus manually SPAWNING the fleet which takes 30 minutes, but instead a shell script that fires a process with a window
# being the claude executable with proper title based on seat name and proper model and effort on the command-line."). One gnome-terminal window per seat,
# titled by the seat's name, working directory the seat's root, running `claude --name NAME --model MODEL --effort EFFORT` -- the three the box controller
# and the postoffice read (the controller lowercases the name and turns - into _ for the postoffice identity). The fleet is read from .github/TIERS.tsv,
# THE ONE TIERS TABLE (fleet-queue step 2; Lon's org model, MODE 2026-11-05 15:1x: Fable 5.1 high for the cio and cto, Opus for the CxOs, Sonnet 5.5 xhigh
# for the four company men, Haiku 5.5 xhigh for the twenty workers); edit TIERS.tsv, never a window by hand, never a seat list in this file. A seat whose
# `claude --name NAME` already runs is skipped, never doubled; a seat whose root is missing is refused and named. --stagger S seconds between windows
# (default 4: twenty-nine sessions starting at once would spike the box).
# Model IDs as the sessions ran today (ps: claude-fable-5-1, claude-opus-5-5, claude-sonnet-5-5, claude-haiku-5-5; Lon 15:5x named fable-5-5, which does not exist -- the coo 16:06), efforts xhigh high medium; claude 2.1.318 has no --color flag
# (the color is the /color command inside a session), so each session is started with "/color COLOR" as its opening prompt (claude's [prompt] argument; a local command, no model turn; verified 2.1.318 for red green yellow purple cyan) and the window title is the seat's name. Lon runs this file by its FULL PATH, /home/claude_cio/.github/scripts/spawn_fleet.sh (any root's .github/scripts/spawn_fleet.sh is the same file at the same commit): ONE file, NO SYMLINK (Lon 2026-11-06: "Ensure that ALL symlink are deleted. We do not use symlinks in this project." / "We instead use FULL pathnames." / "And also RELATIVE pathnames. No symlinks are EVER necessary.").
# --dry prints every command and opens nothing. --table prints the seat rows read from TIERS.tsv (seat name root model effort color) and opens nothing; util_tiers.py --check compares that output with the table. The FLEET: line on MODE is the cio's to remove on Lon's word; this script only opens the windows.
set -uo pipefail
HERE="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"; TIERS="$HERE/../TIERS.tsv"
DRY=0; STAGGER=4; SEATS=(); TABLEONLY=0
while [ $# -gt 0 ]; do case "$1" in --dry) DRY=1;; --table) TABLEONLY=1;; --stagger) STAGGER="${2:?seconds}"; shift;; --all) SEATS=(ALL);; -h|--help) sed -n '2,12p' "$0"; exit 0;; *) SEATS+=("$1");; esac; shift; done
# seat  NAME  root  model  effort  color, from TIERS.tsv (the session color, Lon 16:0x: "red, green, yellow, purple, and cyan. From top down": Fable red, the coo green, the CxOs yellow, the company men purple, the workers cyan; run as the /color command at session start, never a terminal background)
[ -f "$TIERS" ] || { echo "REFUSE(2): no tiers table at $TIERS"; exit 2; }
TABLE="$(awk -F'\t' '!/^#/ && $1 != "seat" && NF >= 8 {print $1 "\t" $2 "\t" $3 "\t" $4 "\t" $5 "\t" $6}' "$TIERS")"
[ -n "$TABLE" ] || { echo "REFUSE(2): $TIERS names no seat"; exit 2; }
if [ "$TABLEONLY" = 1 ]; then printf '%s\n' "$TABLE"; exit 0; fi
[ ${#SEATS[@]} -gt 0 ] || { echo "usage: spawn_fleet.sh [--dry] [--table] [--stagger S] --all | SEAT..."; exit 2; }
command -v gnome-terminal >/dev/null || { echo "REFUSE(2): no gnome-terminal on PATH"; exit 2; }
[ "$DRY" = 1 ] || [ -n "${DISPLAY:-}${WAYLAND_DISPLAY:-}" ] || { echo "REFUSE(2): no DISPLAY or WAYLAND_DISPLAY -- run this from a desktop terminal of the box"; exit 2; }
opened=0; skipped=0; refused=0
while IFS=$'\t' read -r seat name root model effort color; do
    [ -n "$seat" ] || continue
    if [ "${SEATS[0]}" != ALL ]; then want=0; for s in "${SEATS[@]}"; do [ "$s" = "$seat" ] || [ "$s" = "$name" ] && want=1; done; [ $want = 1 ] || continue; fi
    if [ ! -d "$root" ] || [ ! -f "$root/CLAUDE.md" ]; then echo "REFUSED $seat: root $root missing or unpopulated"; refused=$((refused+1)); continue; fi
    if pgrep -f "^claude --name $name( |$)" >/dev/null; then echo "SKIP    $seat: claude --name $name already runs (pid $(pgrep -f "^claude --name $name( |$)" | head -1))"; skipped=$((skipped+1)); continue; fi
    cmd="claude --name $name --model $model --effort $effort '/color $color'"
    echo "OPEN    $seat: gnome-terminal --maximize --title=$name --working-directory=$root -- $cmd"
    if [ "$DRY" = 0 ]; then
        # NO exec (Lon 2026-11-06 08:3x CST, in the coo's window: "I tried to exit a claude worker to re-execute it from the bash shell and when I did it
        # DISAPPEARED since there is NO bash shell. So go fix that in your spawn script."): claude runs as a child of the window's bash, and when it exits the
        # window drops to an interactive login shell in the seat's root, titled by the seat, with the exact restart command printed, so a seat is restarted in place.
        gnome-terminal --maximize --title="$name" --working-directory="$root" -- bash -lc "printf '\\e]2;$name\\a'; cd '$root' && $cmd; rc=\$?; printf '\\e]2;$name (shell)\\a'; echo; echo \"[$name] claude exited rc=\$rc; this window is a bash shell in $root. Restart the seat with:\"; echo \"  $cmd\"; exec bash -l" >/dev/null 2>&1 || { echo "REFUSED $seat: gnome-terminal did not open"; refused=$((refused+1)); continue; }
        opened=$((opened+1)); sleep "$STAGGER"
    fi
done <<< "$TABLE"
echo "SPAWN_FLEET opened=$opened skipped=$skipped refused=$refused dry=$DRY -- the FLEET: line on MODE is removed by the cio on Lon's word; the coo assigns by row"
[ $refused = 0 ]
