#!/usr/bin/env python3
"""CEO-766 queue re-lane: the ceo is coordination only (Lon 2026-09-16, verbatim: "CEO is coordination only.").

Under CEO-759 the ceo still held ICON, RAKU and REBUS.  With those lanes handed to officers (raku -> cto,
icon and rebus -> cfo) a FREE row whose owner cell still says ceo is unreachable: `next` serves only rows
in the caller's own lane.  Same dispositions and provenance caveat as queue_reassign_executive_ceo_759.py:
a BY-SHAPE sweep, PROVISIONAL under the LANE-BY-CURE RULE, made final by the receiving officer's
LANE REVIEW line.

  * FREE rows owned by ceo whose topic names raku/roast -> cto; icon/icn/rebus -> cfo.
  * Every other row (a topic naming no language, PARKED-EXECUTIVE-NO-SEAT, any non-FREE row) is left
    exactly as it is (CEO-755c).

Writes a dated backup beside QUEUE.tsv first.  Binary-safe LF, changes only column 3, prints its counts.
--dry-run prints the counts and writes nothing.
"""
import re
import shutil
import sys
import time

QUEUE = "/home/resources/postoffice/QUEUE.tsv"
RAKU = r"^(raku|roast)-"
ICON = r"^(icon|icn|rebus)-"


def owner_for(topic):
    if re.match(RAKU, topic):
        return "cto"
    if re.match(ICON, topic):
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
    shutil.copy2(QUEUE, QUEUE + ".bak.ceo-766-" + stamp)
    open(QUEUE, "wb").write("\n".join(out).encode("utf-8"))
    print("written; backup QUEUE.tsv.bak.ceo-766-" + stamp)
    return 0


if __name__ == "__main__":
    sys.exit(main())
