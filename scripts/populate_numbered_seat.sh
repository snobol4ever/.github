#!/usr/bin/env bash
# populate_numbered_seat.sh NN [--from ROOT] -- ONE NUMBERED HAIKU SEAT IN ONE COMMAND (the cio, 2026-11-05; Lon 15:1x CST: "rename them all 01, 02,
# ..., 20. Because there are no longer any specialties seats. We have skills now instead use by ANY ASSIGNED seat. Make it so."). Lon creates the folder
# /home/claude_worker_NN (/home is root's); this fills it: the four repos cloned from a populated root (local clone: the objects are hardlinked, origin set
# to github), a SPARSE corpus (tests packages programs library reference editor_configs; `git -C corpus sparse-checkout add benchmarks` widens it for a
# row that needs them), the Stop banner and inbox hooks and the skill gate named for the seat (from the source root's .claude, seat and root substituted),
# banner_compact.py, /tmp/s4e/worker_NN, the postoffice mailbox (inbox archive, HQ file naming cio), and the worker digest (propagate_seat_digests_cto_484.py).
# It does NOT touch ROSTER, FLEET or the old seat's rows: the cio adds the seat to ROSTER and reowns the retired HQ's rows in the same sitting, by hand, measured.
# rc 0 populated (prints the root's du); 1 refused (no folder, folder not empty, no source root); 2 usage.
set -uo pipefail
NN="${1:-}"; FROM=/home/claude_cio; [ "${2:-}" = --from ] && FROM="${3:?--from ROOT}"
case "$NN" in [0-9][0-9]) ;; *) echo "usage: populate_numbered_seat.sh NN [--from ROOT]  (NN two digits, 01..20; the seat is worker_NN)"; exit 2;; esac
seat="worker_$NN"; root="/home/claude_$seat"; PO=/home/resources/postoffice
[ -d "$root" ] || { echo "REFUSE(1): $root does not exist -- Lon creates the folder (/home is root's)"; exit 1; }
[ -z "$(ls -A "$root")" ] || { echo "REFUSE(1): $root is not empty -- this script fills an empty folder only"; exit 1; }
for r in SCRIP corpus harness .github; do [ -d "$FROM/$r/.git" ] || { echo "REFUSE(1): $FROM/$r is not a repo"; exit 1; }; done
[ -f "$FROM/.claude/settings.json" ] && [ -f "$FROM/.claude/settings.local.json" ] || { echo "REFUSE(1): $FROM/.claude has no settings to template"; exit 1; }
src_seat="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["env"]["S4E_SEAT"])' "$FROM/.claude/settings.local.json")"
for r in SCRIP harness .github; do git clone -q "$FROM/$r" "$root/$r" && git -C "$root/$r" remote set-url origin "$(git -C "$FROM/$r" remote get-url origin)" || exit 1; done
git clone -q --no-checkout "$FROM/corpus" "$root/corpus" && git -C "$root/corpus" remote set-url origin "$(git -C "$FROM/corpus" remote get-url origin)" || exit 1
git -C "$root/corpus" sparse-checkout set --no-cone tests packages programs library reference editor_configs README.md >/dev/null 2>&1 || git -C "$root/corpus" sparse-checkout set tests packages programs library reference editor_configs
git -C "$root/corpus" checkout -q main || exit 1
for r in SCRIP corpus harness .github; do git -C "$root/$r" fetch -q origin && git -C "$root/$r" merge -q --ff-only origin/main || exit 1; done
mkdir -p "$root/.claude" "$root/.scratch" "/tmp/s4e/$seat" "$PO/$seat/inbox" "$PO/$seat/archive"
[ -d "$PO/$seat/HQ" ] && rmdir "$PO/$seat/HQ"; echo cio > "$PO/$seat/HQ"
sed "s#$FROM#$root#g; s#\b$src_seat\b#$seat#g" "$FROM/.claude/settings.json" > "$root/.claude/settings.json"
sed "s#$FROM#$root#g; s#\b$src_seat\b#$seat#g" "$FROM/.claude/settings.local.json" > "$root/.claude/settings.local.json"
python3 -c 'import json,sys; [json.load(open(f)) for f in sys.argv[1:]]' "$root/.claude/settings.json" "$root/.claude/settings.local.json" || exit 1
[ -f "$FROM/.claude/banner_compact.py" ] && cp "$FROM/.claude/banner_compact.py" "$root/.claude/"
python3 "$root/.github/scripts/propagate_seat_digests_cto_484.py" --apply "--root=$seat" | tail -1
echo "POPULATED $seat at $root: $(du -sh "$root" | cut -f1) (sparse corpus; S4E_SEAT=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["env"]["S4E_SEAT"])' "$root/.claude/settings.local.json"))"
echo "NEXT, BY HAND: add $seat to ROSTER and FLEET: IDLE EXCEPT on MODE; reown the retired HQ's open rows to $seat; (cd $root/SCRIP && make -j4) under a run slot"
