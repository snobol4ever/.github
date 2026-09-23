#!/usr/bin/env python3
"""queue_reassign_quartet_ceo_1123.py -- THE QUARTET FLIP RE-LANES THE ROWS, NOT JUST THE BRIEFS (ceo, CEO-1123).

⛔ THE DEFECT THIS CURES, AND IT IS THE ceo's.  MODE went QUARTET at 10:50 and the ceo re-laned the two returning
seats' BRIEFS while leaving every row owned by the six stood-down language HQs exactly where it was.  The picker
serves a row only to the seat in its OWNER cell, and under QUARTET no HQ stands, so 411 FREE rows -- 159 of them at
rank 0 or 1 -- COULD NOT BE SERVED TO ANY SEAT.  That is where the defects that mean the collector does not WORK
live: a SNOBOL4 pattern-replacement class printing a wrong answer under collection, Raku silent wrong answers, the
Icon coexpr and cset segvs, the Icon vendor crash triage.  Four officers were polishing the bar's instruments while
the rows that say it does not work were invisible.  Lon, in-chat: "We move to QUARTET therefore all should be
available to the picker."

THE MAP IS THE MODE `LANES:` LINE, NOT A JUDGEMENT: icon, snobol4, snocone and rebus -> ceo; prolog, raku and
pascal -> cto.  A row's language comes from its OWNER (hq_<lang>), which is what the HQ rename of CEO-767 made
reliable.

⛔ CLAIMED ROWS ARE NOT TOUCHED.  CEO-755c forbids rewriting a LIVE claim's owner cell by script, because it hides
the row from the seat holding it.  This script refuses any row whose state begins with CLAIMED or ASSIGNED and
prints it.  PARKED and BLOCKED rows DO move, with their state column unchanged, because a parked row owned by a
seat that cannot stand is still invisible the day it is unparked.
"""
import os, shutil, sys, time
Q = "/home/resources/postoffice/QUEUE.tsv"
LANE = {"hq_icon": "ceo", "hq_snobol4": "ceo", "hq_snocone": "ceo", "hq_rebus": "ceo",
        "hq_prolog": "cto", "hq_raku": "cto", "hq_pascal": "cto"}
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
for r in refused[:8]: print("   %-11s %-22s %s" % (r[0], r[2], r[1][:56]))
if apply:
    shutil.copy2(Q, Q + ".bak.ceo1123-" + time.strftime("%Y%m%d-%H%M%S"))
    open(Q, "w", encoding="utf-8", newline="\n").write("\n".join(out))
    print("WROTE %s (backup beside it)" % Q)
