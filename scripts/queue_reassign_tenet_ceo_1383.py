#!/usr/bin/env python3
"""queue_reassign_tenet_ceo_1383.py -- THE TENET FLIP OF 2026-10-01 09:0x RE-LANES THE LANGUAGE ROWS TO THEIR HQs (ceo, CEO-1383).

Lon 2026-10-01 09:0x CDT, in-chat to the ceo, verbatim: "Let's get all test suites for all languages to 100%. Go to TENET mode,
4 officers, and 7 HQ's."  Under TENET every language is its HQ's (THE SEATS clause of MODE line 2, the picker lane table of
SCRIP s4e_msg.sh), and a language's defect is that HQ's row and outranks its completeness work (CEO-1010).  The QUARTET re-lane
of 18:3x (CEO-1380) had moved the stood-down HQs' rows to the cfo and the cto; this moves every FREE, PARKED or BLOCKED row
owned by an officer whose topic prefix names a standing HQ's language -- snobol4-, prolog-, pascal-, snocone-, icon-, raku- --
or templates- to that HQ.  rebus- rows stay the ceo's (REBUS -- the ceo).  The coo's rows are not touched: the coo's rows are
instruments, its own by cure (CEO-723).

CLAIMED and ASSIGNED rows are NOT touched (CEO-755c).  --apply writes with a dated backup; without it the script only reports.
"""
import shutil, sys, time
Q = "/home/resources/postoffice/QUEUE.tsv"
HQ_OF = {"snobol4": "hq_snobol4", "prolog": "hq_prolog", "pascal": "hq_pascal", "snocone": "hq_snocone", "icon": "hq_icon", "raku": "hq_raku", "templates": "hq_templates"}
FROM = {"ceo", "cto", "cfo"}
apply = "--apply" in sys.argv
rows = open(Q, encoding="utf-8").read().split("\n")
moved, refused, out = {}, [], []
for ln in rows:
    f = ln.split("\t")
    if len(f) < 4 or ln.startswith("#"):
        out.append(ln); continue
    topic, owner, state = f[1], f[2], f[3]
    pre = topic.split("-", 1)[0]
    if owner not in FROM or pre not in HQ_OF:
        out.append(ln); continue
    if state.startswith("CLAIMED") or state.startswith("ASSIGNED"):
        refused.append((owner, topic, state)); out.append(ln); continue
    k = "%s->%s" % (owner, HQ_OF[pre]); moved[k] = moved.get(k, 0) + 1
    f[2] = HQ_OF[pre]; out.append("\t".join(f))
print("WOULD MOVE" if not apply else "MOVED:")
for k in sorted(moved): print("   %-24s %d" % (k, moved[k]))
print("   TOTAL %d" % sum(moved.values()))
print("REFUSED (live claim/assign, owner cell untouched per CEO-755c): %d" % len(refused))
for r in refused[:12]: print("   %s %s %s" % r)
if apply:
    bak = Q + ".bak.%s-tenet-ceo-1383" % time.strftime("%Y%m%d-%H%M%S")
    shutil.copyfile(Q, bak)
    open(Q, "w", encoding="utf-8", newline="\n").write("\n".join(out))
    print("written; backup %s" % bak)
