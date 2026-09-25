#!/usr/bin/env python3
"""queue_reassign_nonet_ceo_1266.py -- THE NONET FLIP RE-LANES THE ROWS (ceo, CEO-1266, 2026-09-25).

Lon, in-chat to the ceo: "Go now to NONET mode." and, asked which five HQs stand, "SNO, PL, PAS, SNOCONE, and ICON".
The picker serves a row only to the seat in its OWNER cell (s4e_topic_lane: an explicit owner beats the prefix), so a
row owned by a seat that does not stand is served to nobody. Two populations move:

  (1) every row owned by the stood-down hq_raku, FREE or PARKED, goes to the cto -- RAKU's lane under NONET. PARKED
      rows move with their state unchanged, because a parked row owned by a seat that cannot stand is still invisible
      the day it is unparked (CEO-1123's reason).
  (2) the FREE rows the ceo held under MODE CEO whose topic names a language with a standing HQ go to that HQ --
      snobol4-*, prolog-*, pascal-*, snocone-*, icon-* -- the lane-by-cure rule reading the prefix the minting seat
      wrote. The ceo's PARKED rows stay the ceo's (it stands), and a raku-* FREE row of the ceo's goes to the cto.

THE MAP IS THE MODE `LANES:` LINE: icon=hq_icon prolog=hq_prolog pascal=hq_pascal snobol4=hq_snobol4
snocone=hq_snocone rebus=ceo raku=cto.

⛔ CLAIMED AND ASSIGNED ROWS ARE NOT TOUCHED (CEO-755c: rewriting a live claim's owner cell hides the row from the
seat holding it); each is printed. Dry run by default; --apply writes QUEUE.tsv with a dated backup beside it.
"""
import shutil, sys, time
Q = "/home/resources/postoffice/QUEUE.tsv"
HQ_OF = {"snobol4": "hq_snobol4", "prolog": "hq_prolog", "pascal": "hq_pascal", "snocone": "hq_snocone", "icon": "hq_icon", "raku": "cto"}
apply = "--apply" in sys.argv
rows = open(Q, encoding="utf-8").read().split("\n")
moved, refused, out = {}, [], []
for ln in rows:
    f = ln.split("\t")
    if len(f) < 4 or ln.startswith("#"):
        out.append(ln); continue
    owner, state, topic = f[2], f[3], f[1]
    live = state.startswith("CLAIMED") or state.startswith("ASSIGNED")
    to = None
    if owner == "hq_raku":
        to = "cto"
    elif owner == "ceo" and state.startswith("FREE"):
        to = HQ_OF.get(topic.split("-", 1)[0])
    if not to:
        out.append(ln); continue
    if live:
        refused.append((owner, state, topic)); out.append(ln); continue
    k = "%s->%s" % (owner, to); moved[k] = moved.get(k, 0) + 1
    f[2] = to; out.append("\t".join(f))
print("WOULD MOVE" if not apply else "MOVED:")
for k in sorted(moved): print("   %-22s %d" % (k, moved[k]))
print("   TOTAL %d" % sum(moved.values()))
print("REFUSED (live claim/assign, owner cell untouched per CEO-755c): %d" % len(refused))
for r in refused[:12]: print("   %-11s %-26s %s" % (r[0], r[1][:26], r[2][:70]))
if apply:
    shutil.copy2(Q, Q + ".bak.ceo1266-" + time.strftime("%Y%m%d-%H%M%S"))
    open(Q, "w", encoding="utf-8", newline="\n").write("\n".join(out))
    print("WROTE %s (backup beside it)" % Q)
