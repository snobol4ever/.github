#!/usr/bin/env python3
# queue_restore_retired_ceo_1607.py -- RESTORE rows a sweep retired on a refusal that was not a measurement of the row (the CEO-1574 shape).
# 2026-10-10 11:48 the sweep retired ten cto prolog-speed rows and one hq_raku ratchet row as cannot-measure rc 2: the bench bars' gnu single-shot
# correctness arm read the 1.6.0 banner's blank line (the oracle swap of CEO-1598, filters not yet re-cut by the coo) and refused without naming the
# load guard. A retired row keeps its baton; this puts the QUEUE row back as FREE at its rank, refusing a topic that is live or claimed.
# Usage: queue_restore_retired_ceo_1607.py <reason-slug> <topic>...   (backups beside both files; a LEDGER line in each baton)
import sys, os, shutil, time
PO = "/home/resources/postoffice"; Q = PO + "/QUEUE.tsv"; R = PO + "/QUEUE.retired.tsv"
reason, topics = sys.argv[1], sys.argv[2:]
assert topics, "no topics"
q = open(Q, "rb").read(); r = open(R, "rb").read()
assert b"\r" not in q and b"\r" not in r
qlines = q.split(b"\n"); rlines = r.split(b"\n")
live = {l.split(b"\t")[1] for l in qlines if l and not l.startswith(b"#") and l.count(b"\t") >= 3}
moved = []; keep = []
for l in rlines:
    f = l.split(b"\t")
    if l and not l.startswith(b"#") and len(f) >= 4 and f[1].decode() in topics:
        t = f[1].decode()
        if f[1] in live: print("REFUSED live:", t); keep.append(l); continue
        if os.path.exists(f"{PO}/claims/{t}.claim"): print("REFUSED claimed:", t); keep.append(l); continue
        moved.append(b"\t".join([f[0], f[1], f[2], b"FREE"])); continue
    keep.append(l)
missing = [t for t in topics if t.encode() not in {m.split(b"\t")[1] for m in moved}]
if missing: print("NOT IN RETIRED (or refused):", *missing, sep="\n  ")
if not moved: sys.exit("nothing to restore")
stamp = time.strftime("%Y%m%d-%H%M%S")
shutil.copy2(Q, f"{Q}.bak.{stamp}-restore-{reason}"); shutil.copy2(R, f"{R}.bak.{stamp}-restore-{reason}")
newq = q.rstrip(b"\n") + b"\n" + b"\n".join(moved) + b"\n"
open(Q, "wb").write(newq); open(R, "wb").write(b"\n".join(keep))
for m in moved:
    t = m.split(b"\t")[1].decode(); b = f"{PO}/tasks/{t}.task.md"
    if os.path.exists(b):
        s = open(b, encoding="utf-8").read()
        line = f"- [ceo·{time.strftime('%Y-%m-%d %H:%M')} CDT] RESTORED to FREE by queue_restore_retired_ceo_1607.py ({reason}): the 11:48 sweep retired this row as cannot-measure rc 2, but the refusal was the bench bar's gnu single-shot correctness arm reading the 1.6.0 banner's blank line (CEO-1598's swap; the coo's filter re-cut pending), not a measurement of the row.\n"
        s = s.replace("## LEDGER\n", "## LEDGER\n" + line, 1) if "## LEDGER\n" in s else s + "\n## LEDGER\n" + line
        open(b, "w", encoding="utf-8").write(s)
print("restored", len(moved), "row(s):", *[m.split(b"\t")[1].decode()[:70] for m in moved], sep="\n  ")
