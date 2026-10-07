#!/usr/bin/env python3
"""queue_reassign_tenet_prolog_ceo_1530.py -- THE TENET FLIP OF 2026-10-07 GIVES hq_prolog BACK THE BREADTH ROWS THE QUARTET FLIP HANDED THE cfo (ceo, CEO-1530).
Lon 2026-10-07 08:5x CDT, in-chat to the ceo, verbatim: "Go to TENET mode with 4 officers and 7 HQ's."  The QUARTET flip (CEO-1521,
queue_reassign_quartet_prolog_ceo_1521.py) moved every non-live hq_prolog row to the cto (the spine) or the cfo (everything else), so at
this flip hq_prolog owned 0 FREE rows and `next` would serve it nothing.  THE MAP: a row that hq_prolog owned in the pre-QUARTET snapshot
(QUEUE.tsv.bak.20261005T102852-quartet-prolog-ceo-1521) and that the cfo owns today goes back to hq_prolog; the cto keeps the spine rows,
so the officers keep Prolog work as MODE line 2 says.  CLAIMED, ASSIGNED and DONE rows are NOT touched (CEO-755c): a live claim's owner
cell is never rewritten by script.  PARKED and BLOCKED rows move with their state column unchanged.  The write takes the bus's own lock
($PO/.mint.lock) and writes a dated backup first.  --apply writes; without it the script only reports.
"""
import os, re, shutil, sys, time
PO = "/home/resources/postoffice"
Q = os.path.join(PO, "QUEUE.tsv")
SNAP = os.path.join(PO, "QUEUE.tsv.bak.20261005T102852-quartet-prolog-ceo-1521")
LOCK = os.path.join(PO, ".mint.lock")
apply = "--apply" in sys.argv
def rows(path):
    out = {}
    for ln in open(path, "rb").read().decode("utf-8").split("\n"):
        f = ln.split("\t")
        if len(f) >= 4 and f[0].isdigit():
            out[f[1]] = f[2]
    return out
was = {t for t, o in rows(SNAP).items() if o == "hq_prolog"}
def plan(lines):
    out, moved = [], []
    for ln in lines:
        f = ln.split("\t")
        if len(f) >= 4 and f[0].isdigit() and f[1] in was and f[2] == "cfo" and not re.match(r"^(CLAIMED|ASSIGNED|DONE)", f[3]):
            moved.append((f[1], f[3])); f[2] = "hq_prolog"; ln = "\t".join(f)
        out.append(ln)
    return out, moved
out, moved = plan(open(Q, "rb").read().decode("utf-8").split("\n"))
print("hq_prolog in the pre-QUARTET snapshot: %d row(s); cfo -> hq_prolog now: %d row(s)" % (len(was), len(moved)))
for topic, state in moved:
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
    shutil.copyfile(Q, Q + ".bak.%s-tenet-prolog-ceo-1530" % stamp)
    open(Q, "wb").write("\n".join(out).encode("utf-8"))
    print("WRITTEN: hq_prolog %d; backup QUEUE.tsv.bak.%s-tenet-prolog-ceo-1530" % (len(moved2), stamp))
finally:
    os.rmdir(LOCK)
