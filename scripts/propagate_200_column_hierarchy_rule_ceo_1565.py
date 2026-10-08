#!/usr/bin/env python3
"""propagate_200_column_hierarchy_rule_ceo_1565.py [--apply] [--root=<seat>] -- THE 200-COLUMN HIERARCHY RULE digest block into all fourteen
roots (ceo, CEO-1565). Lon 2026-10-08 16:5x-17:5x CDT, in-chat to the ceo: "Put code on 200 character lines. If does not fit, begin wrapping
at that level and keep those lines long." -- "when you begin wrapping, it must be at hierarchical C structures." -- "each child at the level gets
its own line." -- the template .cpp files stay line-oriented. Per root: the block line is inserted right after the ORDER OF WORK block, or
refreshed in place when present and different. Bytes are read and written as UTF-8 with LF kept; a dated backup CLAUDE.md.bak-2026-10-08-ceo-1565
is written beside each root changed. Without --apply it prints what it would do. Idempotent: a second run changes nothing.
"""
import sys, os, shutil
ROOTS = ["ceo", "cto", "coo", "cfo", "icon", "prolog", "pascal", "snocone", "snobol4", "raku", "templates", "runtime", "collector", "zetas"]
BLOCK = ('⛔⭐⭐⭐ **THE CODE IS UNDER LON\'S 200-COLUMN HIERARCHY RULE AND EVERY LANDING KEEPS IT (Lon 2026-10-08 16:5x–17:5x CDT, in-chat to the ceo, verbatim: '
         '*"Put code on 200 character lines. If does not fit, begin wrapping at that level and keep those lines long. No line shall EXCEED 200 characters, all must fit."* · *"when you begin wrapping, it must be at hierarchical C structures."* · *"if at one level it over flows a line, then you break at the hiearchical level and start the rule over again at the indention. But each child at the level gets its own line."* · *"Regarding the template CPP files, those should be more line oriented ... the lines of C++ code should match closely the lines of ASM being emitted."*; ruled CEO-1565; RULES.md § C code style; the whole tree re-flowed at SCRIP cfcfaf46d):** '
         'in every hand-written `.c`, `.h` and `.inc` under `src/` (the parsers and the two generated tables excepted) an item — a statement, or a whole block with its else-chain — that fits goes on ONE line of at most 200 UTF-8 bytes at its indent; an item that does not fit is a block that opens on its own line, lays every child out by the same rule one level deeper, each child on its own line, and closes on its own line; a longer statement wraps at its own level with long continuation lines; no comment but the 200-character separators, no blank line, a directive on its own line. Every `.cpp` and everything under `src/templates/` is LINE-ORIENTED (one line of C++ per line of emitted asm; only comments and blank lines go; an over-long line wraps at its level). '
         'THE INSTRUMENT is `SCRIP/scripts/util_reflow_200.py`: `--check <paths>` is the ratchet every landing owes on the files it touched (rc 1 names a file that would change), `--apply` the cure, `--proof` and `--objproof` the two proofs a re-flow landing carries (preprocessed token streams identical; objects byte-identical, gcc\'s -O0 brace-line nops the only tolerated residue). Write new code in the rule from the start; a gate that greps a source SHAPE by line dies under it and is re-cut to read statements (the allocator census\'s statement head), never reverted; `strip_comments.py --check` stays 0.')
KEY = "⛔⭐⭐⭐ **THE CODE IS UNDER LON'S 200-COLUMN HIERARCHY RULE"
KORDER = "⛔⭐⭐⭐⭐ **THE ORDER OF WORK: EACH LANGUAGE TO 100% FIRST"
KSTACK = "⛔⭐⭐⭐⭐ **NO GLOBAL HOLDS A STACK"
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
    anchor = line_span(t, KORDER) or line_span(t, KSTACK)
    if anchor:
        e = anchor[1]
        if t[e:e + 1] == "\n":
            e += 1
        return t[:e] + BLOCK + "\n\n" + t[e:], "block inserted after the %s block" % ("ORDER OF WORK" if line_span(t, KORDER) else "NO GLOBAL HOLDS A STACK")
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
            shutil.copy2(p, p + ".bak-2026-10-08-ceo-1565")
            open(p, "wb").write(nt.encode("utf-8"))
        print("%-10s %s%s" % (r, what, "" if apply else " (dry run)"))
    return 0
if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
