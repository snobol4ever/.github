#!/usr/bin/env python3
"""queue_reassign_quartet_prolog_ceo_1521.py -- THE QUARTET FLIP OF 2026-10-05 RE-LANES THE STOOD-DOWN hq_prolog's ROWS TO THE cto AND THE cfo (ceo, CEO-1521).

Lon 2026-10-05 10:2x CDT, in-chat to the ceo, verbatim: "As I see it now, SNOBOL4 and Icon test suites are at 100%. Hurray!!! Let's focus
on Prolog to 100%. Let's CTO and CFO involved. Go to QUARTET mode."  Under QUARTET no HQ stands and the picker serves a row only to the seat
in its OWNER cell, so a row owned by hq_prolog can be served to nobody (the CEO-1123 finding).  THE MAP IS THE LANE-BY-CURE RULE, split
inside Prolog so both officers Lon named have Prolog work: the rows that cure the SPINE -- emitted unification, the trail, choice points,
operator-term speed, rational trees and the unifier's variable order, findall's reclaim, the rung-8 frame cells, the dead uncaught
wrappers -- go to the cto; every other Prolog row -- builtins, SWI breadth, the Logtalk families, the GNU and INRIA package rows, the
error-term and bagof/setof rungs -- goes to the cfo.  The coo owns no cure lane (CEO-723) and the ceo assigns.

CLAIMED and ASSIGNED rows are NOT touched (CEO-755c): a live claim's owner cell is never rewritten by script.  PARKED and BLOCKED rows
move with their state column unchanged.  DONE rows stay where they are.  The write takes the bus's own lock ($PO/.mint.lock, the lock
s4e_msg.sh's state writer and mint take) and writes a dated backup first.  --apply writes; without it the script only reports.
"""
import os, re, shutil, sys, time
PO = "/home/resources/postoffice"
Q = os.path.join(PO, "QUEUE.tsv")
LOCK = os.path.join(PO, ".mint.lock")
CTO = re.compile(r"^prolog-(speed-|rational-trees-|copy-term-2-does-not-terminate-on-a-rational-tree|a-variable-bound-to-a-variable-|findall-reclaims-|rung-8-f-acc-|pl-iso-uncaught-)")
apply = "--apply" in sys.argv
def target(topic):
    return "cto" if CTO.match(topic) else "cfo"
def plan(lines):
    out, moved = [], {"cto": [], "cfo": []}
    for ln in lines:
        f = ln.split("\t")
        if len(f) >= 4 and f[0].isdigit() and f[2] == "hq_prolog" and not re.match(r"^(CLAIMED|ASSIGNED|DONE)", f[3]):
            t = target(f[1]); moved[t].append((f[1], f[3])); f[2] = t; ln = "\t".join(f)
        out.append(ln)
    return out, moved
raw = open(Q, "rb").read().decode("utf-8")
lines = raw.split("\n")
out, moved = plan(lines)
for seat in ("cto", "cfo"):
    print("%s: %d row(s)" % (seat, len(moved[seat])))
    for topic, state in moved[seat]:
        print("   %-12s %s" % (state.split(":")[0], topic[:120]))
if not apply:
    print("DRY RUN -- nothing written; --apply writes")
    sys.exit(0)
got = False
for _ in range(50):
    try:
        os.mkdir(LOCK); got = True; break
    except FileExistsError:
        time.sleep(0.1)
if not got:
    print("REFUSED(2): the bus lock %s is busy -- nothing written" % LOCK); sys.exit(2)
try:
    fresh = open(Q, "rb").read().decode("utf-8").split("\n")
    out, moved2 = plan(fresh)
    stamp = time.strftime("%Y%m%dT%H%M%S")
    shutil.copyfile(Q, Q + ".bak.%s-quartet-prolog-ceo-1521" % stamp)
    open(Q, "wb").write("\n".join(out).encode("utf-8"))
    print("WRITTEN: cto %d, cfo %d; backup QUEUE.tsv.bak.%s-quartet-prolog-ceo-1521" % (len(moved2["cto"]), len(moved2["cfo"]), stamp))
finally:
    os.rmdir(LOCK)
