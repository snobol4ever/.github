#!/usr/bin/env python3
"""CEO-759 queue re-lane for MODE CEO -> EXECUTIVE (Lon 2026-09-16, verbatim: "Go to EXECUTIVE mode with CEO, CTO, CFO, and COO.").

Under MODE CEO every FREE row was re-owned to the ceo (CEO-755c).  With the cto and the cfo standing again,
a FREE row in their lane is unreachable while its owner cell still says ceo: `next` serves only rows in the
caller's own lane.  Same dispositions and the same regexes as queue_reassign_executive_ceo_748.py, same
provenance caveat: this is a BY-SHAPE sweep and therefore PROVISIONAL under the LANE-BY-CURE RULE -- the
receiving officer writes the LANE REVIEW ledger line that makes an owner final.

  * FREE rows owned by ceo whose topic names prolog -> cto; snobol4/snocone/pascal -> cfo; icon/raku/rebus
    stay ceo.  The coo owns no language (CEO-723) and receives nothing.
  * PARKED-EXECUTIVE-NO-SEAT rows stay parked under ceo custody (concerns 2-5 still have no seat).
  * Every non-FREE row is left exactly as it is (CEO-755c: rewriting a live claim's owner cell hides the
    row from the seat holding it).

Writes a dated backup beside QUEUE.tsv first.  Binary-safe LF, changes only column 3 of the rows it names,
prints its counts.  --dry-run prints the counts and writes nothing.
"""
import re
import shutil
import sys
import time

QUEUE = "/home/resources/postoffice/QUEUE.tsv"
ICON = r"^(icon|icn)-|^(raku|roast)-|^rebus-"
PROLOG = r"^(prolog|pl|swi|inria|logtalk|gnu)-"
SNOBOL = r"^(snobol4|sno|snocone|snc|pascal|pas|spitbol|gimpel|snoflake|csnobol4|ais|fpc|pat)-"


def owner_for(topic):
    if re.match(ICON, topic):
        return "ceo"
    if re.match(PROLOG, topic):
        return "cto"
    if re.match(SNOBOL, topic):
        return "cfo"
    return "ceo"


def main():
    dry = "--dry-run" in sys.argv[1:]
    data = open(QUEUE, "rb").read()
    if b"\r" in data:
        print("REFUSED: QUEUE.tsv carries CR bytes; this script writes LF only", file=sys.stderr)
        return 2
    lines = data.decode("utf-8").split("\n")
    moved = {"cto": 0, "cfo": 0}
    stay = 0
    out = []
    for line in lines:
        f = line.split("\t")
        if len(f) >= 4 and not f[0].startswith("#") and f[3] == "FREE" and f[2] == "ceo":
            o = owner_for(f[1])
            if o != "ceo":
                f[2] = o
                moved[o] += 1
                line = "\t".join(f)
            else:
                stay += 1
        out.append(line)
    print("FREE ceo rows re-owned: cto %d, cfo %d; staying ceo %d" % (moved["cto"], moved["cfo"], stay))
    if dry:
        print("dry-run: nothing written")
        return 0
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    shutil.copy2(QUEUE, QUEUE + ".bak.ceo-759-executive-" + stamp)
    open(QUEUE, "wb").write("\n".join(out).encode("utf-8"))
    print("written; backup QUEUE.tsv.bak.ceo-759-executive-" + stamp)
    return 0


if __name__ == "__main__":
    sys.exit(main())
