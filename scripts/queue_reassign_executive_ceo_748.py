#!/usr/bin/env python3
"""CEO-748 queue re-lane for MODE EXECUTIVE (four officers, nine HQs stood down).

FREE rows owned by a stood-down HQ are unreachable: `next` serves only rows in
the caller's own lane, so 467 free rows would sit invisible behind seats that
no longer run.  Two dispositions, and the difference is deliberate:

  * A row whose topic names a LANGUAGE is re-owned by that language's owner on
    MODE line 2 -- icon/raku/rebus -> ceo, prolog -> cto, snobol4/snocone/
    pascal -> cfo.  This is a BY-SHAPE sweep and therefore PROVISIONAL under
    the LANE-BY-CURE RULE: a row's owner is decided by what it CURES, and the
    receiving officer writes the LANE REVIEW ledger line that makes it final.

  * A row whose topic names no language belongs to concerns 2-5 (speed, zeta,
    GC, beauty/instruments), which under EXECUTIVE have NO SEAT and are not
    suspended: they fold into the lane whose cure needs them.  Those rows are
    parked PARKED-EXECUTIVE-NO-SEAT under ceo custody -- visible to every
    census, served to nobody, un-parked by the officer whose cure reaches one.
    Parking is the honest state; leaving them FREE under a seat that will
    never call `next` is a queue that lies about what is reachable.

Writes a dated backup beside QUEUE.tsv first.  Binary-safe LF, changes only
column 3 and column 4 of the rows it names, and prints its counts.
"""
import re
import shutil
import time

QUEUE = "/home/resources/postoffice/QUEUE.tsv"
ICON = r"^(icon|icn)-|^(raku|roast)-|^rebus-"
PROLOG = r"^(prolog|pl|swi|inria|logtalk|gnu)-"
SNOBOL = r"^(snobol4|sno|snocone|snc|pascal|pas|spitbol|gimpel|snoflake|csnobol4|ais|fpc|pat)-"
LANG = ICON + "|" + PROLOG + "|" + SNOBOL


def owner_for(topic):
    if re.match(ICON, topic):
        return "ceo"
    if re.match(PROLOG, topic):
        return "cto"
    return "cfo"


def main():
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    shutil.copy2(QUEUE, QUEUE + ".bak.ceo-748-executive-" + stamp)
    with open(QUEUE, encoding="utf-8") as fh:
        lines = fh.read().split("\n")
    out, moved, parked = [], {"ceo": 0, "cto": 0, "cfo": 0}, 0
    for line in lines:
        f = line.split("\t")
        if len(f) >= 4 and not f[0].startswith("#") and f[3] == "FREE" and f[2].startswith("hq_"):
            if re.match(LANG, f[1]):
                f[2] = owner_for(f[1])
                moved[f[2]] += 1
            else:
                f[2] = "ceo"
                f[3] = "PARKED-EXECUTIVE-NO-SEAT"
                parked += 1
            line = "\t".join(f)
        out.append(line)
    with open(QUEUE, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(out))
    print("backup: " + QUEUE + ".bak.ceo-748-executive-" + stamp)
    print("re-laned by language: ceo %d · cto %d · cfo %d" % (moved["ceo"], moved["cto"], moved["cfo"]))
    print("parked PARKED-EXECUTIVE-NO-SEAT under ceo custody: %d" % parked)


if __name__ == "__main__":
    main()
