#!/usr/bin/env python3
"""FLEET STAND-DOWN BANNER -- the ceo's answer to ONE question Lon asks: which seats
should he still prompt, and may he stop prompting altogether.

⛔ IT NEVER GUESSES A STAND-DOWN.  A seat is STOOD DOWN only when it has SAID SO and the
ceo has recorded it in STANDDOWN.tsv with the measurement it cited.  A silent seat is
UNKNOWN, never stood down -- silence and "no work" are different readings and only one of
them lets Lon stop prompting (CEO-582: DARK is worse than RED).
"""
import os, sys, csv, datetime
PO = os.environ.get("S4E_PO", "/home/resources/postoffice")
SEATS = ["cto", "cfo", "coo", "hq_icon", "hq_prolog", "hq_raku", "hq_snobol4", "hq_snocone", "hq_pascal"]

GC_WORDS = ("gc-", "-gc-", "collector", "under-collection", "unmapped-slot", "no-layout",
            "frame-map", "frame-layout", "safe-point", "rooted", "unrooted", "root-", "-root",
            "heap", "arena", "gc-stress", "sliding", "slides", "stompage", "collection")

def is_gc(topic):
    """⛔ THIS IS A NAME HEURISTIC AND THE BANNER SAYS SO.  A row's GC-ness is a fact about
    what it CURES, never about a noun in its name (THE LANE-BY-CURE RULE), and a topic string
    cannot carry that.  The first cut keyed on a `gc-` prefix and read hq_snobol4's
    `snobol4-the-pattern-replacement-class-prints-a-wrong-answer-under-collection` -- the
    fleet's own corruption witness -- as NON-GC, because that row is named for its SYMPTOM.
    A classifier keyed on a shape that means something else is the defect this fleet has a
    law against, so the vocabulary below is wide and the banner marks every call as a guess
    the owning seat may overturn in one line."""
    t = topic.lower()
    return any(w in t for w in GC_WORDS)

def held(seat, rows):
    gc, other = [], []
    for rank, topic, owner, state in rows:
        who = state.split(":", 1)[1] if ":" in state else owner
        if who != seat or not state.startswith(("CLAIMED", "ASSIGNED")):
            continue
        (gc if is_gc(topic) else other).append(topic)
    return gc, other

def main():
    rows = []
    with open(os.path.join(PO, "QUEUE.tsv"), encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("#"):
                continue
            p = line.rstrip("\n").split("\t")
            if len(p) >= 4:
                rows.append((p[0], p[1], p[2], p[3]))
    sd = {}
    sdp = os.path.join(PO, "STANDDOWN.tsv")
    if os.path.exists(sdp):
        with open(sdp, encoding="utf-8", errors="replace") as f:
            for line in f:
                if line.startswith("#") or not line.strip():
                    continue
                p = line.rstrip("\n").split("\t")
                if len(p) >= 3:
                    sd[p[0]] = (p[1], p[2])
    print("=" * 78)
    print("FLEET STAND-DOWN BANNER   %s   -- PROMPT means Lon still drives that seat" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M %Z").strip())
    print("=" * 78)
    prompt_n = unknown_n = 0
    for s in SEATS:
        gc, other = held(s, rows)
        if s in sd:
            when, why = sd[s]
            print("  %-11s STOOD DOWN   do not prompt   (%s) %s" % (s, when, why[:60]))
        elif gc:
            prompt_n += 1
            print("  %-11s WORKING      PROMPT          %s" % (s, gc[0][:58]))
        elif other:
            prompt_n += 1
            print("  %-11s ⛔ NON-GC    PROMPT          %s" % (s, other[0][:58]))
        else:
            unknown_n += 1
            print("  %-11s ⛔ UNKNOWN   PROMPT          no claim and no stand-down reported" % s)
    print("-" * 78)
    print("  PROMPT these: %d    STOOD DOWN: %d    UNKNOWN (silent, NOT stood down): %d" % (prompt_n, len(sd), unknown_n))
    if len(sd) == len(SEATS):
        print("  ⭐ EVERY SEAT HAS STOOD DOWN -- Lon may stand down too.")
    else:
        print("  ⛔ LON KEEPS PROMPTING: %d seat(s) still working or silent." % (prompt_n + unknown_n))
    print("  \u26d4 GC-ness is classified BY NAME, which is a heuristic: a row is GC by what it CURES,")
    print("     and a topic string cannot carry that. Any seat may overturn a cell in one line.")
    print("=" * 78)
    return 0

if __name__ == "__main__":
    sys.exit(main())
