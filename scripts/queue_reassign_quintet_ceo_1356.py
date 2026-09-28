#!/usr/bin/env python3
"""queue_reassign_quintet_ceo_1356.py -- THE QUINTET FLIP RE-LANES THE STOOD-DOWN HQs' ROWS (ceo, CEO-1356).

Lon 2026-09-28 17:2x CDT, in-chat to the ceo, verbatim: "Bring the fleet into QUARTET mode: CEO, CTO, CFO, and COO. Leave
HQ-SNOCONE alone. So QUNTET mode."  Five seats work rows: the four officers and hq_snocone.  The six stood-down seats'
FREE, PARKED and BLOCKED rows move to an officer so the picker can still serve them (Lon 2026-09-22 at the QUARTET flip,
CEO-1123: "We move to QUARTET therefore all should be available to the picker.").

THE MAP IS THE QUINTET LANE TABLE IN s4e_msg.sh, the QUARTET map of CEO-1123 with Snocone left where it is:
icon and snobol4 -> ceo (rebus is already the ceo's); prolog, raku and pascal -> cto; hq_templates -> cto (its officer).
hq_snocone's rows are NOT touched.

⛔ CLAIMED AND ASSIGNED ROWS ARE NOT TOUCHED (CEO-755c: rewriting a live claim's owner cell hides the row from the seat
holding it).  A stood-down seat releases its claim first; the next run of this script then moves the row.
Usage: queue_reassign_quintet_ceo_1356.py [--apply]     (default: print what would move, write nothing)
"""
import shutil, sys, time
Q = "/home/resources/postoffice/QUEUE.tsv"
LANE = {"hq_icon": "ceo", "hq_snobol4": "ceo", "hq_prolog": "cto", "hq_raku": "cto", "hq_pascal": "cto", "hq_templates": "cto"}
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
for r in refused: print("   %-12s %-24s %s" % (r[0], r[2][:24], r[1][:70]))
if apply:
    shutil.copy2(Q, Q + ".bak.ceo1356-" + time.strftime("%Y%m%d-%H%M%S"))
    open(Q, "w", encoding="utf-8", newline="\n").write("\n".join(out))
    print("WROTE %s (backup beside it)" % Q)
