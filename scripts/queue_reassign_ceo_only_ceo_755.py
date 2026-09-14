#!/usr/bin/env python3
"""CEO-755 queue re-lane for MODE CEO (one working seat).

The EXECUTIVE re-lane (CEO-748) put 300 language rows on the three cure
officers.  With the cto, the cfo and the coo stood down those rows are
unreachable again -- `next` refuses a stood-down identity outright now, so a
row owned by one of them can be served to nobody at all.

Every FREE row owned by cto/cfo/coo is re-owned by the ceo.  A CLAIMED or
otherwise non-FREE row is left exactly as it is: its owner is mid-turn and
the closing telegram, not this script, is what releases it -- rewriting a
live claim's owner cell would hide the row from the seat holding it.

The 167 rows parked PARKED-EXECUTIVE-NO-SEAT keep that status and that
custody: concerns 2-5 still have no seat, and the ceo un-parks one when a
cure reaches it.

Writes a dated backup beside QUEUE.tsv first, changes only column 3 of the
rows it names, and prints its counts.
"""
import shutil
import time

QUEUE = "/home/resources/postoffice/QUEUE.tsv"
STOOD_DOWN = ("cto", "cfo", "coo")


def main():
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    shutil.copy2(QUEUE, QUEUE + ".bak.ceo-755-ceo-only-" + stamp)
    with open(QUEUE, encoding="utf-8") as fh:
        lines = fh.read().split("\n")
    out, moved, held = [], {s: 0 for s in STOOD_DOWN}, 0
    for line in lines:
        f = line.split("\t")
        if len(f) >= 4 and not f[0].startswith("#") and f[2] in STOOD_DOWN:
            if f[3] == "FREE":
                moved[f[2]] += 1
                f[2] = "ceo"
                line = "\t".join(f)
            else:
                # a non-FREE row stays with its holder: the closing telegram releases it, not this script
                held += 1
        out.append(line)
    with open(QUEUE, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(out))
    print("backup: " + QUEUE + ".bak.ceo-755-ceo-only-" + stamp)
    print("FREE rows re-owned to ceo: cto %d · cfo %d · coo %d" % (moved["cto"], moved["cfo"], moved["coo"]))
    print("non-FREE rows left with their holder (released by the closing telegram, not here): %d" % held)


if __name__ == "__main__":
    main()
