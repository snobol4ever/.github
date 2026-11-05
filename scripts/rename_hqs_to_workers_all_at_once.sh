#!/usr/bin/env bash
# rename_hqs_to_workers_all_at_once.sh --plan | --records | --roots -- THE MASSIVE REPLACE: EVERY HQ BECOMES A NUMBERED WORKER IN ONE ACT (the cio,
# 2026-11-05; Lon, in the cio's window 15:3x CST, verbatim: "Someone, probably you, needs to do an ALL AT ONCE MASSIVE replace. We want 20 workers." / 15:4x: "So use worker_01 and worker_02. Add the underscaore." / "Start from 01 not 00.";
# 15:1x in the coo's window: "rename them all 01, 02, ..., 20. Because there are no longer any specialties seats. We have skills now instead use by ANY
# ASSIGNED seat."). THE MAP is MAP below (the coo's order of 15:2x; hq_dotnet, hq_jvm and hq_packages stay named: the ports have their own repos).
#   --plan      print every action and change nothing
#   --records   the fleet's records, all at once: QUEUE.tsv owners and states (ASSIGNED CLAIMED RUNNING MEASURING), the .claim files, CLAIMS.log, the
#               mailboxes (inbox and archive moved, the old box DRAINED with a pointer), MODE ROSTER and ON-CALL, the controller's sleeping list
#   --roots     the roots: for every map row whose /home/claude_worker_NN exists -- EMPTY: populate_numbered_seat.sh fills it; MOVED (Lon ran the
#               `sudo mv` the plan prints, so it holds the old HQ's repos): rewrite .claude/settings*.json to the worker and regenerate the digest;
#               a worker with no old HQ (12-20) is populated fresh. /home is root's, so the folders are Lon's; the plan prints the one sudo block.
# Every file written is backed up beside itself as <file>.bak-<stamp>-workers. rc 0 done; 1 a refusal (named); 2 usage.
set -uo pipefail
MODE_ARG="${1:-}"; case "$MODE_ARG" in --plan|--records|--roots) ;; *) echo "usage: $0 --plan | --records | --roots"; exit 2;; esac
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; PO=/home/resources/postoffice; S=/home/claude_coo/.scratch/verifier
STAMP="$(date +%Y%m%dT%H%M)"; apply=0; [ "$MODE_ARG" != --plan ] && apply=1
declare -A MAP=( [worker_01]=hq_collector [worker_02]=hq_icon [worker_03]=hq_zetas [worker_04]=hq_templates [worker_05]=hq_snocone [worker_06]=hq_pascal [worker_07]=hq_prolog [worker_08]=hq_unicon [worker_09]=hq_runtime [worker_10]=hq_snobol4 [worker_11]=hq_raku [worker_12]= [worker_13]= [worker_14]= [worker_15]= [worker_16]= [worker_17]= [worker_18]= [worker_19]= [worker_20]= )
WORKERS="$(printf '%s\n' "${!MAP[@]}" | sort)"
say() { printf '%s\n' "$*"; }
bak() { [ -f "$1" ] && cp "$1" "$1.bak-$STAMP-workers"; }
if [ "$MODE_ARG" = --plan ] || [ "$MODE_ARG" = --records ]; then
    say "== THE MAP (new <- old)"; for w in $WORKERS; do say "  $w <- ${MAP[$w]:-(new)}"; done
    say "== QUEUE.tsv: owner and state cells"; n=0
    for w in $WORKERS; do o="${MAP[$w]}"; [ -n "$o" ] || continue; c=$(awk -F'\t' -v o="$o" '$3==o || $4 ~ ("^(ASSIGNED|CLAIMED|RUNNING):" o "$") || $4 ~ ("^MEASURING:" o ":")' "$PO/QUEUE.tsv" | wc -l); say "  $o -> $w: $c row(s)"; n=$((n+c)); done
    say "  total $n row(s); hq_dotnet, hq_jvm, hq_packages rows untouched"
    if [ $apply = 1 ]; then bak "$PO/QUEUE.tsv"; python3 - "$PO/QUEUE.tsv" "$STAMP" "${!MAP[@]}" "${MAP[@]}" <<'PY'
import sys, re
p, stamp = sys.argv[1], sys.argv[2]; names = sys.argv[3:]; k = len(names)//2; mp = {o: w for w, o in zip(names[:k], names[k:]) if o}
rows = open(p, encoding='utf-8').read().split('\n'); out = []; changed = 0
for l in rows:
    f = l.split('\t')
    if len(f) >= 4 and not l.startswith('#'):
        o = f[2]; st = f[3]; g = f[:]
        if o in mp: g[2] = mp[o]
        m = re.match(r'^(ASSIGNED|CLAIMED|RUNNING):([a-z_0-9]+)$', st)
        if m and m.group(2) in mp: g[3] = m.group(1) + ':' + mp[m.group(2)]
        m = re.match(r'^MEASURING:([a-z_0-9]+):(\d+)$', st)
        if m and m.group(1) in mp: g[3] = 'MEASURING:' + mp[m.group(1)] + ':' + m.group(2)
        if g != f: changed += 1
        l = '\t'.join(g)
    out.append(l)
open(p, 'w', encoding='utf-8').write('\n'.join(out)); print('  QUEUE.tsv rewritten: %d row(s) changed' % changed)
PY
    fi
    say "== .claim files naming an old seat"; for f in "$PO"/claims/*.claim; do [ -f "$f" ] || continue; for w in $WORKERS; do o="${MAP[$w]}"; [ -n "$o" ] || continue; if grep -qw "$o" "$f"; then say "  $(basename "$f"): $o -> $w"; [ $apply = 1 ] && { bak "$f"; sed -i "s/\b$o\b/$w/g" "$f"; }; fi; done; done
    [ $apply = 1 ] && for w in $WORKERS; do o="${MAP[$w]}"; [ -n "$o" ] || continue; printf '%s\t%s\t%s\t%s\n' "$(date -u +%FT%TZ)" cio RENAMED-ALL-AT-ONCE "$o -> $w (Lon 2026-11-05: twenty workers, no specialty seats)" >> "$PO/CLAIMS.log"; done
    say "== mailboxes: inbox and archive move, the old box is DRAINED with a pointer"
    for w in $WORKERS; do o="${MAP[$w]}"; [ -n "$o" ] || continue; [ -d "$PO/$o" ] || { say "  $o: no mailbox"; continue; }
        ni=$(ls "$PO/$o/inbox" 2>/dev/null | wc -l); na=$(ls "$PO/$o/archive" 2>/dev/null | wc -l); say "  $o -> $w: $ni unread, $na archived"
        if [ $apply = 1 ]; then mkdir -p "$PO/$w/inbox" "$PO/$w/archive"; for d in inbox archive; do for f in "$PO/$o/$d"/*; do [ -e "$f" ] && mv "$f" "$PO/$w/$d/"; done; done; echo cio > "$PO/$w/HQ"; printf 'DRAINED %s: %s is %s now (Lon 2026-11-05, twenty workers); its mail lives in %s\n' "$(date -u +%FT%TZ)" "$o" "$w" "$PO/$w" > "$PO/$o/DRAINED"; fi; done
    say "== MODE ROSTER and ON-CALL, the sleeping list"
    roster="$(sed -n 's/^ROSTER:[[:space:]]*//p' "$PO/MODE")"; new=""; for s in $roster; do keep=1; for w in $WORKERS; do [ "${MAP[$w]}" = "$s" ] && keep=0; done; [ $keep = 1 ] && new="$new $s"; done; new="$(echo $new $WORKERS)"
    say "  ROSTER: $new"
    if [ $apply = 1 ]; then bak "$PO/MODE"; python3 - "$PO/MODE" "$new" <<'PY'
import sys, re
p, roster = sys.argv[1], sys.argv[2]; L = open(p, encoding='utf-8').read().split('\n')
for i, l in enumerate(L):
    if l.startswith('ROSTER:'): L[i] = 'ROSTER: ' + roster
    if l.startswith('ON-CALL:'): L[i] = 'ON-CALL: cto'
open(p, 'w', encoding='utf-8').write('\n'.join(L)); print('  MODE ROSTER and ON-CALL rewritten')
PY
        bak "$S/sleeping"; printf '%s\n' $new > "$S/sleeping"; say "  sleeping: $(tr '\n' ' ' < "$S/sleeping")"; fi
    say "== THE ROOTS (Lon's: /home is root's). One sudo block, then --roots:"
    for w in $WORKERS; do o="${MAP[$w]}"; if [ -n "$o" ]; then say "  sudo mv /home/claude_${o#hq_} /home/claude_$w"; else say "  sudo mkdir /home/claude_$w && sudo chown satirical:satirical /home/claude_$w"; fi; done
fi
if [ "$MODE_ARG" = --roots ]; then
    for w in $WORKERS; do o="${MAP[$w]}"; r="/home/claude_$w"
        if [ ! -d "$r" ]; then say "  $w: no root yet ($r)"; continue; fi
        if [ -z "$(ls -A "$r")" ]; then say "  $w: empty root, populating"; bash "$HERE/populate_numbered_seat.sh" "${w#worker_}" | tail -2; continue; fi
        if [ -d "$r/SCRIP/.git" ]; then
            old_seat="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["env"]["S4E_SEAT"])' "$r/.claude/settings.local.json" 2>/dev/null)"; old_root="/home/claude_${old_seat#hq_}"
            [ "$old_seat" = "$w" ] && { say "  $w: already plumbed"; continue; }
            say "  $w: moved root of $old_seat ($old_root), re-plumbing hooks and digest"
            for f in settings.json settings.local.json; do bak "$r/.claude/$f"; sed -i "s#$old_root#$r#g; s#\b$old_seat\b#$w#g" "$r/.claude/$f"; done
            python3 -c 'import json,sys; [json.load(open(f)) for f in sys.argv[1:]]' "$r/.claude/settings.json" "$r/.claude/settings.local.json" || { say "  $w: REFUSE(1) settings not valid JSON after rewrite"; exit 1; }
            mkdir -p "/tmp/s4e/$w"; [ -f "$r/CLAUDE.md" ] && bak "$r/CLAUDE.md"
            python3 "$HERE/propagate_seat_digests_cto_484.py" --apply "--root=$w" | tail -1
            continue
        fi
        say "  $w: REFUSE(1) $r is neither empty nor a moved HQ root"; exit 1
    done
fi
exit 0
