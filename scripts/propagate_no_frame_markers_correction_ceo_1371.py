#!/usr/bin/env python3
"""Correct the CEO-1368/1369 digest block on the four officer roots' CLAUDE.md to Lon's later words of the same hour (CEO-1371).

Usage: propagate_no_frame_markers_correction_ceo_1371.py [--apply] [--root ceo|cto|coo|cfo ...]
Without --apply it prints what it would do. Idempotent: a root already carrying CEO-1371 is skipped; a root without the
CEO-1368 block gets the corrected block inserted after the '# CLAUDE.md' header. Backup CLAUDE.md.bak-2026-09-30-ceo-1371.
"""
import sys, os, shutil, re
ROOTS = ["ceo", "cto", "coo", "cfo"]
MARK = "CEO-1371"
BLOCK = (
    "⛔⭐⭐⭐⭐ **NO FRAME MARKERS, NO SECOND STACK: ONE STACK, EVERY WORD ON IT A TAGGED DESCR (Lon 2026-09-30, in-chat to the cto, three words of one hour, "
    "verbatim: *\"Seems you should get rid of frame markers; they appear to be problematic. Find another better solution than scanning to markers on a stack.\"* · "
    "*\"How silly. So you have an side-car stack to manage your stack. Is that one way of saying it?\"* · *\"Do you have a plan without markers and without TWO stacks "
    "which should be one?\"*; ruled CEO-1368 then corrected CEO-1371; RULES.md § FACT RULE — NO FRAME MARKERS):** the collector never scans the stack for a marker "
    "and keeps no side-car ledger of frames; the design is § 7's own sentence with its exception closed — every raw word the frame headers and the stored-pattern "
    "interiors put on the emitted stack (saved rbp, γ, ω, the DTP pointer, saved-rsp watermarks, the choice record, leaf scratch) becomes a 16-byte tagged cell, so the "
    "walker is a pure sweep by 16 that finds nothing and remembers nothing; the map cells, the emitter's cell stores, the interior layouts, gc_walk_cell, the scan and "
    "map_off are deleted at the end of the row's one batch. The row is the cto's rank-0 `gc-one-stack-all-descriptors-…`; the cto and the cfo are IDLE on Lon's word "
    "of 2026-09-30 10:0x until he reseats them.\n\n"
    "⛔⭐⭐⭐⭐ **THE TREE IS BUILT ONCE, DIRECTLY, IN RECOGNITION ORDER; THE C TREE IS THE CANONICAL FORM; NO POST-PROCESSING; A PARSER MOVES NOTHING, THE "
    "LOWERER PLACES IT (Lon 2026-09-30 morning, in-chat to the cfo, verbatim: *\"The C tree is the canonical form. It matters not, settle on ONE and we'll improve it "
    "later.\"* · *\"Just ensure that the tree is built from tokens in the same order as they are recognized by the PATTERN. No post processing of trees. The tree gets "
    "built directly and once only.\"* · on the Icon case default: *\"Fix the C's parser to not move it. Why move it in parser. That is the lower's job.\"*; ruled "
    "CEO-1369, the default-clause answer CEO-1371; RULES.md § FACT RULE — THE TREE IS BUILT ONCE):** every `bootstrap/parser_*.sc` and every C parser builds its tree "
    "once at recognition and no pass rewrites a built node; a clause is never moved by a parser, C or .sc — the lowerer places it (SCRIP 44dacedfb: the Icon case "
    "default stays where it is recognised and lower_case lowers it last).\n\n"
)
def main(argv):
    apply = "--apply" in argv
    roots = [a for a in argv if a in ROOTS] or ROOTS
    rc = 0
    for r in roots:
        p = f"/home/claude_{r}/CLAUDE.md"
        if not os.path.exists(p):
            print(f"{r}: MISSING {p}"); rc = 2; continue
        t = open(p, encoding="utf-8").read()
        if MARK in t:
            print(f"{r}: already carries {MARK}, skipped"); continue
        m = re.search(r"⛔⭐⭐⭐⭐ \*\*NO FRAME MARKERS — .*?\n\n⛔⭐⭐⭐⭐ \*\*THE TREE IS BUILT ONCE.*?\n\n", t, re.S)
        head = "# CLAUDE.md\n\n"
        if not m and t.count(head) < 1:
            print(f"{r}: neither the CEO-1368 block nor a '# CLAUDE.md' header, refused"); rc = 2; continue
        if not apply:
            print(f"{r}: would {'replace the CEO-1368 block' if m else 'insert the block after the header'} in {p}"); continue
        shutil.copy2(p, p + ".bak-2026-09-30-ceo-1371")
        t = (t[:m.start()] + BLOCK + t[m.end():]) if m else t.replace(head, head + BLOCK, 1)
        open(p, "w", encoding="utf-8", newline="\n").write(t)
        print(f"{r}: {'replaced' if m else 'inserted'} in {p}")
    return rc
if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
