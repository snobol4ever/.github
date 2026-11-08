#!/usr/bin/env bash
# rename_seats_by_map.sh --map "old=new old=new ..." --plan | --records | --roots -- SEVEN NAMED SEATS BECOME NUMBERED ONES (Lon 2026-11-07 16:5x: "We keep CIO and CTO And COO.
# All other names can be generic"; 17:1x: "I rename everything. I restart all and see it start from scratch."). The folders are Lon's mv (/home is root's); this script moves
# every record the fleet keeps about a seat, by one map, in one act: --records rewrites QUEUE.tsv (owner and state cells), the .claim head lines, the mailboxes
# (moved, a pointer left in the old box), MODE's ROSTER and FLEET: IDLE EXCEPT lines, TIERS.tsv (seat, NAME, root; the role becomes designer or senior), and moves
# /tmp/s4e/<old> to /tmp/s4e/<new>; --roots re-plumbs each moved root that exists at /home/claude_<new>: .claude/settings*.json (root path and seat), then the digest.
# --plan prints what each step would touch and changes nothing. Every file written is backed up beside itself as <file>.bak-<stamp>-rename. rc 0 done; 1 refused; 2 usage.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; PO=/home/resources/postoffice; TIERS="$HERE/../TIERS.tsv"; STAMP="$(date +%Y%m%dT%H%M)"
MAPSTR=""; MODE_ARG=""
while [ $# -gt 0 ]; do case "$1" in --map) MAPSTR="${2:?}"; shift 2;; --plan|--records|--roots) MODE_ARG="$1"; shift;; *) echo "usage: $0 --map 'old=new ...' --plan|--records|--roots"; exit 2;; esac; done
[ -n "$MAPSTR" ] && [ -n "$MODE_ARG" ] || { echo "usage: $0 --map 'old=new ...' --plan|--records|--roots"; exit 2; }
declare -A MAP; for kv in $MAPSTR; do MAP["${kv%%=*}"]="${kv#*=}"; done
apply=0; [ "$MODE_ARG" != --plan ] && apply=1
say() { printf '%s\n' "$*"; }
bak() { cp -p "$1" "$1.bak-$STAMP-rename" 2>/dev/null || true; }
tier_of_new() { case "$1" in officer_*) echo "claude-opus-5-5	high	yellow	2	designer";; senior_*) echo "claude-sonnet-5-5	medium	purple	3	senior";; junior_*) echo "claude-haiku-5-5	medium	cyan	4	junior";; *) return 1;; esac; }   # Lon 2026-11-08 06:4x: WORKER becomes JUNIOR to match SENIOR
if [ "$MODE_ARG" = --plan ] || [ "$MODE_ARG" = --records ]; then
    say "== QUEUE.tsv owner and state cells"
    for o in "${!MAP[@]}"; do n="${MAP[$o]}"; c=$(awk -F'\t' -v o="$o" '$3==o || $4 ~ ("^(ASSIGNED|CLAIMED|RUNNING):" o "$") || $4 ~ ("^MEASURING:" o ":")' "$PO/QUEUE.tsv" | wc -l); say "  $o -> $n: $c row(s)"; done
    if [ $apply = 1 ]; then bak "$PO/QUEUE.tsv"; python3 - "$PO/QUEUE.tsv" "$MAPSTR" <<'PY'
import sys, re
p, mapstr = sys.argv[1], sys.argv[2]; m = dict(kv.split("=", 1) for kv in mapstr.split())
out = []; changed = 0
for line in open(p, encoding="utf-8").read().split("\n"):
    f = line.split("\t")
    if len(f) >= 4 and not line.startswith("#"):
        o = line
        if f[2] in m: f[2] = m[f[2]]
        mm = re.match(r"^(ASSIGNED|CLAIMED|RUNNING):([^:]+)$", f[3])
        if mm and mm.group(2) in m: f[3] = "%s:%s" % (mm.group(1), m[mm.group(2)])
        mm = re.match(r"^MEASURING:([^:]+):(.*)$", f[3])
        if mm and mm.group(1) in m: f[3] = "MEASURING:%s:%s" % (m[mm.group(1)], mm.group(2))
        line = "\t".join(f); changed += line != o
    out.append(line)
open(p, "w", encoding="utf-8").write("\n".join(out)); print("  QUEUE.tsv rewritten: %d row(s) changed" % changed)
PY
    fi
    say "== .claim files whose head names an old seat"
    for f in "$PO"/claims/*.claim; do [ -f "$f" ] || continue; h="$(head -1 "$f")"; [ -n "${MAP[$h]:-}" ] || continue; say "  $(basename "$f"): $h -> ${MAP[$h]}"
        [ $apply = 1 ] && { bak "$f"; sed -i "1s/^$h\$/${MAP[$h]}/" "$f"; }; done
    say "== mailboxes"
    for o in "${!MAP[@]}"; do n="${MAP[$o]}"; [ -d "$PO/$o" ] || { say "  $o: no mailbox"; continue; }; say "  $PO/$o -> $PO/$n ($(ls "$PO/$o/inbox" 2>/dev/null | wc -l) unread)"
        if [ $apply = 1 ]; then if [ -d "$PO/$n" ]; then say "  REFUSE(1): $PO/$n exists"; exit 1; fi; mv "$PO/$o" "$PO/$n"; mkdir -p "$PO/$o/inbox"; printf 'MOVED to %s on %s (rename_seats_by_map.sh; Lon 2026-11-07: generic names)\n' "$n" "$STAMP" > "$PO/$o/MOVED"; fi; done
    say "== MODE ROSTER and FLEET lines"
    if [ $apply = 1 ]; then bak "$PO/MODE"; python3 - "$PO/MODE" "$MAPSTR" <<'PY'
import sys, re
p, mapstr = sys.argv[1], sys.argv[2]; m = dict(kv.split("=", 1) for kv in mapstr.split())
L = open(p, encoding="utf-8").read().split("\n")
for i, l in enumerate(L):
    if l.startswith("ROSTER:") or l.startswith("FLEET: IDLE EXCEPT") or l.startswith("ON-CALL:"):
        L[i] = re.sub(r"\b(" + "|".join(map(re.escape, m)) + r")\b", lambda x: m[x.group(1)], l)
open(p, "w", encoding="utf-8").write("\n".join(L)); print("  MODE ROSTER, FLEET and ON-CALL rewritten")
PY
    else sed -n 's/^ROSTER:[[:space:]]*/  ROSTER now: /p' "$PO/MODE" | cut -c1-200; fi
    say "== TIERS.tsv rows"
    for o in "${!MAP[@]}"; do n="${MAP[$o]}"; grep -q "^$o	" "$TIERS" || { say "  $o: no row"; continue; }; t="$(tier_of_new "$n")" || { say "  REFUSE(1): $n is not officer_NN or senior_NN"; exit 1; }; say "  $o -> $n	${n^^}	/home/claude_$n	$t"
        [ $apply = 1 ] && { bak "$TIERS"; awk -F'\t' -v OFS='\t' -v o="$o" -v n="$n" -v t="$t" '$1==o { split(t, a, "\t"); nm = toupper(n); gsub(/_/, "-", nm); print n, nm, "/home/claude_" n, a[1], a[2], a[3], a[4], a[5]; next } { print }' "$TIERS" > "$TIERS.tmp" && mv "$TIERS.tmp" "$TIERS"; }; done
    say "== /tmp/s4e/<seat>"
    for o in "${!MAP[@]}"; do n="${MAP[$o]}"; [ -d "/tmp/s4e/$o" ] || continue; say "  /tmp/s4e/$o -> /tmp/s4e/$n"; [ $apply = 1 ] && { [ -d "/tmp/s4e/$n" ] && mv "/tmp/s4e/$n" "/tmp/s4e/$n.before-rename-$STAMP"; mv "/tmp/s4e/$o" "/tmp/s4e/$n"; }; done
fi
if [ "$MODE_ARG" = --plan ] || [ "$MODE_ARG" = --roots ]; then
    say "== roots"
    for o in "${!MAP[@]}"; do n="${MAP[$o]}"; r="/home/claude_$n"
        [ -d "$r" ] || { say "  $n: $r does not exist yet (Lon's mv)"; continue; }
        [ -d "/home/claude_$o" ] && say "  WARNING: /home/claude_$o still exists beside $r"
        cur="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["env"]["S4E_SEAT"])' "$r/.claude/settings.local.json" 2>/dev/null || echo '?')"
        say "  $n: root $r, settings name seat '$cur'"
        if [ $apply = 1 ] && [ "$cur" = "$o" ]; then
            for f in settings.json settings.local.json; do bak "$r/.claude/$f"; sed -i "s#/home/claude_$o#$r#g; s#\b$o\b#$n#g" "$r/.claude/$f"; done
            python3 -c 'import json,sys; [json.load(open(f)) for f in sys.argv[1:]]' "$r/.claude/settings.json" "$r/.claude/settings.local.json" || { say "  REFUSE(1): $n settings not valid JSON after rewrite"; exit 1; }
            python3 "$HERE/propagate_seat_digests_cto_484.py" --apply "--root=$n" | tail -1
        fi
    done
fi
say "RENAME $MODE_ARG done stamp=$STAMP map=$MAPSTR"
