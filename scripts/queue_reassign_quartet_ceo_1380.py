#!/usr/bin/env python3
"""queue_reassign_quartet_ceo_1380.py -- THE QUARTET FLIP OF 2026-09-30 20:2x RE-LANES THE STOOD-DOWN HQs' FREE ROWS (ceo, CEO-1380).

Lon 2026-09-30 20:2x CDT, in-chat to the ceo, verbatim: "Let's go to QUARTET mode. Four officers."  Under QUARTET no HQ
stands, and the picker serves a row only to the seat in its OWNER cell, so a FREE row owned by hq_<lang> can be served to
nobody (the CEO-1123 finding: 411 such rows on 2026-09-21).  THE MAP IS THE LANE-BY-CURE RULE with the CEO-1038/1051
reviewer split: prolog, raku and templates rows to the cto (the spine, Prolog and Raku review, the templates seat's
officer); icon, snobol4, snocone, pascal and rebus rows to the cfo (the collector, the SNOBOL4 crash classes, rebus
keep-green).  The coo owns no cure lane (CEO-723) and the ceo assigns.

CLAIMED and ASSIGNED rows are NOT touched (CEO-755c): a live claim's owner cell is never rewritten by script.  PARKED and
BLOCKED rows move with their state column unchanged.  --apply writes; without it the script only reports.
"""
import shutil, sys, time
Q = "/home/resources/postoffice/QUEUE.tsv"
LANE = {"hq_prolog": "cto", "hq_raku": "cto", "hq_templates": "cto",
        "hq_icon": "cfo", "hq_snobol4": "cfo", "hq_snocone": "cfo", "hq_pascal": "cfo", "hq_rebus": "cfo"}
apply = "--apply" in sys.argv
rows = open(Q, encoding="utf-8").read().split("\n")
moved, refused, out = {}, [], []
for ln in rows:
    f = ln.split("\t")
    if len(f) < 4 or f[2] not in LANE:
        out.append(ln); continue
    if f[3].startswith("CLAIMED") or f[3].startswith("ASSIGNED"):
        refused.append((f[2], f[1], f[3])); out.append(ln); continue
    k = "%s->%s" % (f[2], LANE[f[2]]); moved[k] = moved.get(k, 0) + 1
    f[2] = LANE[f[2]]; out.append("\t".join(f))
print("WOULD MOVE" if not apply else "MOVED:")
for k in sorted(moved): print("   %-22s %d" % (k, moved[k]))
print("   TOTAL %d" % sum(moved.values()))
print("REFUSED (live claim/assign, owner cell untouched per CEO-755c): %d" % len(refused))
for r in refused: print("   %s %s %s" % r)
if apply:
    bak = Q + ".bak.%s-quartet-ceo-1380" % time.strftime("%Y%m%d-%H%M%S")
    shutil.copyfile(Q, bak)
    open(Q, "w", encoding="utf-8", newline="\n").write("\n".join(out))
    print("written; backup %s" % bak)
