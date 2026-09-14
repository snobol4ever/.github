#!/usr/bin/env bash
# ceo742_park_the_eight_free_rebus_rows_on_the_arbiter.sh -- Lon-run, same reason as CEO-726's script: no ceo
# path can write under /home/resources.
#
# WHY. CEO-736 made MODE line 2 say what is true -- REBUS -- CLOSED, NO OWNER -- and that turned the picker
# gate rc=2 (unparseable) for every seat, because the gate had two states for a language and needed a third.
# CEO-742 gave it the third: a language declared CLOSED must route to the ARBITER, since a row in a closed
# language is a REOPENING question and only Lon reopens a language. The table now sends rebus-* to the ceo
# (SCRIP, landed) and the gate proves it fail-once/pass-once.
#
# WHAT IS LEFT, AND IT IS THIS FILE: eight FREE rebus rows still sit in QUEUE.tsv owned by hq_S (7) and hq_P
# (1). Leaving them FREE means the ceo picker is the only one that can see them, which is worse than useless:
# `next` refuses under CEO, so they would be invisible to every seat including their new owner. Reowning them
# without parking them would ALSO be wrong in the other direction -- a seat working one would be reopening a
# closed language without Lon's word.
# SO: owner -> ceo AND state -> PARKED-REBUS-CLOSED. No picker serves them, the arbiter holds them, and the
# reason is in the state string where the next reader meets it rather than in a ruling they must find.
# A DONE row is never touched (its owner cell is a historical fact) and the one already-PARKED row keeps its
# state and only changes owner.
set -uo pipefail
PO=/home/resources/postoffice
STAMP=$(date +%Y-%m-%d-%H%M)
cd "$PO" || exit 2
[ -f QUEUE.tsv ] || { echo "⛔ REFUSED: not the postoffice, no QUEUE.tsv in $PO" >&2; exit 2; }
cp -p QUEUE.tsv "QUEUE.tsv.bak.$STAMP-ceo742-rebus-closed" || { echo "⛔ REFUSED: could not back up QUEUE.tsv" >&2; exit 2; }
python3 - <<'PYEOF'
p = "/home/resources/postoffice/QUEUE.tsv"
lines = open(p, "rb").read().split(b"\n")
moved = parked = 0
untouched = []
for i, ln in enumerate(lines):
    if not ln or ln.startswith(b"#"):
        continue
    f = ln.split(b"\t")
    if len(f) < 4 or not f[1].startswith(b"rebus"):
        continue
    state = f[3]
    if state.startswith(b"DONE") or state.startswith(b"RETIRED") or state.startswith(b"SUPERSEDED"):
        untouched.append((f[1].decode(), f[2].decode(), state.decode()))
        continue
    if state.startswith(b"CLAIMED") or state.startswith(b"ASSIGNED"):
        untouched.append((f[1].decode(), f[2].decode(), state.decode()))
        continue
    if f[2] != b"ceo":
        f[2] = b"ceo"; moved += 1
    if state == b"FREE":
        f[3] = b"PARKED-REBUS-CLOSED"; parked += 1
    lines[i] = b"\t".join(f)
open(p, "wb").write(b"\n".join(lines))
print("✅ QUEUE.tsv: %d rebus row(s) re-owned to ceo, %d FREE row(s) parked as PARKED-REBUS-CLOSED" % (moved, parked))
for t, o, s in untouched:
    print("   NOT TOUCHED (%s, owner %s): %s" % (s, o, t))
PYEOF
echo "--- VERIFY, measured not assumed ---"
awk -F'\t' '$2 ~ /^rebus/ {print $3" "$4}' QUEUE.tsv | sort | uniq -c
echo "--- the gate ---"
bash /home/claude_ceo/SCRIP/scripts/test_gate_picker_lane_table_agrees_with_mode.sh >/tmp/ceo742_gate.txt 2>&1
echo "picker gate rc=$? (0 = agrees)"
tail -2 /tmp/ceo742_gate.txt
