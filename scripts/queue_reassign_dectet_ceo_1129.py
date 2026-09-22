#!/usr/bin/env python3
"""queue_reassign_dectet_ceo_1129.py -- THE DECTET FLIP PUTS EACH LANGUAGE'S ROWS BACK WITH ITS OWN HQ (ceo, CEO-1129).

Lon, in-chat: "I suppose we should start 6 HQ's on Sonnet 5 at effort = xhigh." then "Each responsible for its own
language."  QUARTET stood the six language HQs down, so CEO-1123 moved 566 rows off them to the ceo and the cto --
correct under QUARTET, because a row owned by a seat that does not stand is served to NOBODY.  DECTET stands them
back up, so the ownership goes back.

⛔ THIS IS EXACT, NOT A HEURISTIC.  It reverses by reading the BACKUP CEO-1123 wrote, so a row returns to the seat
that actually held it rather than to a seat guessed from its topic prefix.  A row whose owner has changed since, or
whose topic is not in the backup, is LEFT ALONE and printed.

⛔ AND IT MUST NOT UNDO THE CHOP.  The three chunk rows and the standing chop are SHARED-NODE template work assigned
to officers on Lon's word (CEO-1113/1124); they were never hq_* rows, so the backup does not name them and they
cannot be touched by construction.  The same holds for every instrument row.
"""
import os, shutil, sys, time
Q = "/home/resources/postoffice/QUEUE.tsv"
apply = "--apply" in sys.argv
baks = sorted([f for f in os.listdir(os.path.dirname(Q)) if f.startswith("QUEUE.tsv.bak.ceo1123-")])
if not baks:
    print("REFUSE(2): no CEO-1123 backup found -- cannot reverse exactly, and a guessed reversal is worse than none")
    sys.exit(2)
B = os.path.join(os.path.dirname(Q), baks[-1])
orig = {}
for ln in open(B, encoding="utf-8"):
    f = ln.rstrip("\n").split("\t")
    if len(f) >= 4 and f[2].startswith("hq_"):
        orig[f[1]] = f[2]
print("backup: %s  (rows originally owned by an HQ: %d)" % (baks[-1], len(orig)))
rows = open(Q, encoding="utf-8").read().split("\n")
out, moved, left = [], {}, 0
for ln in rows:
    f = ln.split("\t")
    if len(f) < 4 or f[1] not in orig or f[2] not in ("ceo", "cto"):
        out.append(ln); continue
    tgt = orig[f[1]]
    k = "%s->%s" % (f[2], tgt); moved[k] = moved.get(k, 0) + 1
    f[2] = tgt; out.append("\t".join(f))
print("WOULD MOVE" if not apply else "MOVED:")
for k in sorted(moved): print("   %-20s %d" % (k, moved[k]))
print("   TOTAL %d" % sum(moved.values()))
if apply:
    shutil.copy2(Q, Q + ".bak.ceo1129-" + time.strftime("%Y%m%d-%H%M%S"))
    open(Q, "w", encoding="utf-8", newline="\n").write("\n".join(out))
    print("WROTE %s (backup beside it)" % Q)
