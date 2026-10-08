#!/usr/bin/env python3
"""propagate_order_of_work_100_then_perf_then_parsers_ceo_1562.py [--apply] -- the ORDER OF WORK digest block into all fourteen roots (ceo, CEO-1562).
Lon 2026-10-08 16:1x CDT, in-chat to the ceo, verbatim: "The first priority now that global stacks-based variables have been moved onto the
stack, is to get each language to 100%. Then after that is performance for each language. And also getting boot-strap parsers to replace the
current C-based parsers in SCRIP." Per root: the block line is inserted right after the NO GLOBAL HOLDS A STACK block, or refreshed in place
when present and different. Bytes are read and written as UTF-8 with LF kept; a dated backup CLAUDE.md.bak-2026-10-08-ceo-1562 is written
beside each root changed. Without --apply it prints what it would do. Idempotent: a second run changes nothing.
"""
import sys, os, shutil
ROOTS = ["ceo", "cto", "coo", "cfo", "icon", "prolog", "pascal", "snocone", "snobol4", "raku", "templates", "runtime", "collector", "zetas"]
BLOCK = ('⛔⭐⭐⭐⭐ **THE ORDER OF WORK: EACH LANGUAGE TO 100% FIRST, THEN PERFORMANCE, THEN THE BOOTSTRAP PARSERS REPLACE THE C PARSERS (Lon 2026-10-08 16:1x CDT, in-chat to the ceo, verbatim: '
         '*"The first priority now that global stacks-based variables have been moved onto the stack, is to get each language to 100%. Then after that is performance for each language. And also getting boot-strap parsers to replace the current C-based parsers in SCRIP."*; ruled CEO-1562; MODE line 2):** '
         'the global-stack rewrite is DONE (the countdown reads 18 of 18, CEO-1560: every per-construct second stack of the runtime is on the machine stack, the CAS and the Prolog trail the two r12 islands Lon keeps) and the fleet serves in this order: '
         '(1) EVERY SUITE ROW OF EVERY LANGUAGE AT 100% — the rank-0 and rank-1 rows of each HQ\'s lane are its suite reds (at the 10-08 table: SnoRungs 1968/1980, PAT 408/427, Logtalk 3497/3577, SWI 883/2935, GNU source 11/55, ProDemo 0/2, RakRungs 934/960, RakBench 65/84, Roast 83/1464) and `next` serves them first; '
         '(2) PERFORMANCE for each language — the `*-speed-*` rows and the bench bars (the two-number basis, the kernel convention, the bare `x` multiple), which a seat serves once its language has no red; '
         '(3) THE BOOTSTRAP PARSERS — hq_snocone\'s seven `bootstrap/parser_<lang>.sc` parse every corpus program into the same `tree_t` as the C parsers (`test_gate_snocone_parsers_match_the_c_parsers_tree_for_tree.sh`) at C\'s parse clock and 2x SPITBOL (`util_parser_grid.sh`), then replace the C parsers one language at a time (LARGE CHUNKS: one language and its smoke, then everywhere); '
         'the runtime-globals rows and the two parser-stack rows of CEO-1561 ride under (2) and (3). The coo\'s standing loop is live again over origin HEAD (CEO-1547 lifted at CEO-1560), every HQ is started by Lon, and nobody idles with a FREE row in its lane.')
KEY = "⛔⭐⭐⭐⭐ **THE ORDER OF WORK: EACH LANGUAGE TO 100% FIRST"
KSTACK = "⛔⭐⭐⭐⭐ **NO GLOBAL HOLDS A STACK"
KFRAME = "⛔⭐⭐⭐⭐ **NO FRAME MARKERS"
def line_span(t, k):
    s = t.find("\n" + k)
    if s < 0:
        return None
    s += 1
    e = t.index("\n", s) + 1
    return s, e
def rewrite(t):
    sp = line_span(t, KEY)
    if sp:
        if t[sp[0]:sp[1]] == BLOCK + "\n":
            return t, None
        return t[:sp[0]] + BLOCK + "\n" + t[sp[1]:], "block refreshed"
    anchor = line_span(t, KSTACK) or line_span(t, KFRAME)
    if anchor:
        e = anchor[1]
        if t[e:e + 1] == "\n":
            e += 1
        return t[:e] + BLOCK + "\n\n" + t[e:], "block inserted after the %s block" % ("NO GLOBAL HOLDS A STACK" if line_span(t, KSTACK) else "NO FRAME MARKERS")
    head = t.find("\n# CLAUDE.md\n")
    if head < 0:
        return t, "REFUSED: no # CLAUDE.md line and no anchor block"
    e = head + len("\n# CLAUDE.md\n")
    if t[e:e + 1] == "\n":
        e += 1
    return t[:e] + BLOCK + "\n\n" + t[e:], "block inserted after # CLAUDE.md"
def main(argv):
    apply = "--apply" in argv
    only = [a for a in argv if a.startswith("--root=")]
    roots = [only[0][7:]] if only else ROOTS
    for r in roots:
        p = "/home/claude_%s/CLAUDE.md" % r
        if not os.path.isfile(p):
            print("%-10s MISSING %s" % (r, p)); continue
        t = open(p, "rb").read().decode("utf-8")
        nt, what = rewrite(t)
        if what is None:
            print("%-10s unchanged" % r); continue
        if what.startswith("REFUSED"):
            print("%-10s %s" % (r, what)); continue
        if apply:
            shutil.copy2(p, p + ".bak-2026-10-08-ceo-1562")
            open(p, "wb").write(nt.encode("utf-8"))
        print("%-10s %s%s" % (r, what, "" if apply else " (dry run)"))
    return 0
if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
