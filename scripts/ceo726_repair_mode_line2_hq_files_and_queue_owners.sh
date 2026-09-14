#!/usr/bin/env bash
# ceo726_repair_mode_line2_hq_files_and_queue_owners.sh -- Lon-run, because no ceo path may write under
# /home/resources (the harness classifier refuses both Bash and Edit from the ceo root; the precedent is
# populate_*_root.sh and the propagate_* digest writers). Everything here is postoffice shared state the
# ceo owns and cannot reach from its own seat. Idempotent: every substitution asserts its own occurrence
# count first and the script exits non-zero without writing if any assertion fails.
#
# WHAT IT REPAIRS, all four found by seats and ruled this sitting:
#   (1) MODE line 2, CEO-736: two fragments still hand Rebus to hq_S after CEO-723 closed Rebus, and the
#       SEATS list carries a stale suite reading for Raku that CEO-675 forbids a MODE line to carry at all.
#       Found by hq_S, who grepped its own name and found it twice with Rebus attached; hq_T's ladder is
#       exhausted at 184/184 so "red from rung 2" is false as well as forbidden.
#   (2) hq_C/HQ and hq_R/HQ, CEO-726: every one of the thirteen working seats' HQ files reads `ceo` while
#       MODE line 2 gives hq_R and hq_C to the cto. MODE line 2 is the authority; the files are re-cut.
#   (3) QUEUE.tsv column 3, CEO-728: all fifteen snocone rows are owned by seats that do not hold the
#       snocone lane, so hq_I's own picker cannot see a single row in its own lane -- measured by hq_I,
#       whose `next` handed it an ICON row and then nothing. FREE rows only: a DONE row's owner is a
#       historical fact and a claimed or ASSIGNED row is never moved under its holder.
#   (4) the same for pascal rows, which CEO-723 moved to hq_S.
set -uo pipefail
PO=/home/resources/postoffice
STAMP=$(date +%Y-%m-%d-%H%M)
cd "$PO" || exit 2
fail() { echo "⛔ REFUSED: $*" >&2; exit 2; }
[ -f MODE ] && [ -f QUEUE.tsv ] || fail "not the postoffice: MODE or QUEUE.tsv missing in $PO"
cp -p MODE "MODE.bak-$STAMP-ceo736-line2-rebus-and-raku-residue" || fail "could not back up MODE"
cp -p QUEUE.tsv "QUEUE.tsv.bak.$STAMP-ceo728-owner-column" || fail "could not back up QUEUE.tsv"
python3 - "$STAMP" <<'PYEOF'
import sys, os, shutil
po = "/home/resources/postoffice"
stamp = sys.argv[1]
rc = 0
# ---------------------------------------------------------------- (1) MODE line 2
p = os.path.join(po, "MODE")
b = open(p, "rb").read()
subs = [
    (b" Rebus moves to hq_S.",
     b" REBUS IS CLOSED (RebM 43/43 both modes with zero xpass, coo 2026-09-13; second reader hq_S on"
     b" SCRIP 5bfbd5d57, 43 master entries all carrying a ladder__rungNN origin and zero xfail rows) AND"
     b" HAS NO LANE OWNER."),
    (b"REBUS -- hq_S;", b"REBUS -- CLOSED, NO OWNER;"),
    (b"RAKU -- hq_T (red from rung 2 today);", b"RAKU -- hq_T;"),
]
todo = []
for old, new in subs:
    n = b.count(old)
    if n == 1:
        todo.append((old, new))
    elif n == 0 and b.count(new) >= 1:
        print("   already repaired: %s" % old[:46].decode())
    else:
        print("⛔ MODE line 2: %r occurs %d times, expected 1 -- nothing written" % (old[:46], n))
        rc = 2
if rc == 0 and todo:
    for old, new in todo:
        b = b.replace(old, new, 1)
    open(p, "wb").write(b)
    print("✅ MODE line 2: %d fragment(s) repaired" % len(todo))
elif rc == 0:
    print("✅ MODE line 2: nothing to do")
# ---------------------------------------------------------------- (2) the two HQ files
for seat in ("hq_C", "hq_R"):
    f = os.path.join(po, seat, "HQ")
    if not os.path.exists(f):
        print("⛔ %s: no HQ file" % seat); rc = 2; continue
    cur = open(f, "rb").read()
    if cur.strip() == b"cto":
        print("   already repaired: %s/HQ reads cto" % seat); continue
    if cur.strip() != b"ceo":
        print("⛔ %s/HQ reads %r, not ceo -- left alone, rule by hand" % (seat, cur.strip())); rc = 2; continue
    shutil.copy2(f, f + ".bak-" + stamp)
    open(f, "wb").write(b"cto\n")
    print("✅ %s/HQ: ceo -> cto (MODE line 2 gives this seat to the cto)" % seat)
# ---------------------------------------------------------------- (3)+(4) QUEUE.tsv column 3
p = os.path.join(po, "QUEUE.tsv")
raw = open(p, "rb").read()
lines = raw.split(b"\n")
moves = {b"snocone-": b"hq_I", b"pascal-": b"hq_S"}
# hq_I's nine icon rows only -- NOT every icon row. MODE line 2 gives Icon breadth to the ceo, but a
# ninety-row lane behind a seat whose picker refuses `next` is a queue-design question and not a typo,
# so this pass moves only the rows hq_I named as mis-dispatching to itself (arizona, ipl, jcon,
# flip-ipl-toktab). The rest stay visibly wrong rather than quietly undispatchable.
icon_from_hq_I = (b"icon-", b"flip-ipl-", b"ipl-")
changed = 0
skipped = []
for i, ln in enumerate(lines):
    if not ln or ln.startswith(b"#"):
        continue
    f = ln.split(b"\t")
    if len(f) < 4:
        continue
    topic, owner, state = f[1], f[2], f[3]
    if owner == b"hq_I" and any(topic.startswith(p) for p in icon_from_hq_I):
        if state == b"FREE":
            f[2] = b"ceo"
            lines[i] = b"\t".join(f)
            changed += 1
        else:
            skipped.append((topic.decode(), owner.decode(), state.decode()))
        continue
    for pref, new in moves.items():
        if not topic.startswith(pref):
            continue
        if owner == new:
            break
        if state != b"FREE":
            skipped.append((topic.decode(), owner.decode(), state.decode()))
            break
        f[2] = new
        lines[i] = b"\t".join(f)
        changed += 1
        break
if rc == 0 and changed:
    open(p, "wb").write(b"\n".join(lines))
print("✅ QUEUE.tsv: %d FREE row(s) re-owned (snocone -> hq_I, pascal -> hq_S, hq_I's icon rows -> ceo)" % changed)
for t, o, s in skipped:
    print("   NOT MOVED (%s, owner %s): %s" % (s, o, t))
sys.exit(rc)
PYEOF
PYRC=$?
echo "--- VERIFY, measured not assumed ---"
sed -n '2p' MODE | grep -oE 'REBUS[^;]{0,40}' || true
sed -n '2p' MODE | grep -cE 'Rebus moves to hq_S|REBUS -- hq_S|red from rung 2' | sed 's/^/stale fragments still present: /'
for s in hq_C hq_R; do printf "%s/HQ = %s\n" "$s" "$(cat $s/HQ)"; done
awk -F'\t' '$2 ~ /^snocone-/ {print $3" "$4}' QUEUE.tsv | sort | uniq -c
awk -F'\t' '$2 ~ /^pascal-/  {print $3" "$4}' QUEUE.tsv | sort | uniq -c
echo "--- the gate that holds the two copies against each other ---"
bash /home/claude_ceo/SCRIP/scripts/test_gate_picker_lane_table_agrees_with_mode.sh 2>&1 | tail -3
exit $PYRC
