#!/usr/bin/env python3
"""Append the CEO-1368/1369 digest block to the four officer roots' CLAUDE.md (Lon-run for the sibling roots).

Usage: propagate_no_frame_markers_and_tree_once_ceo_1368.py [--apply] [--root ceo|cto|coo|cfo ...]
Without --apply it prints what it would do. Idempotent: a root whose CLAUDE.md already names CEO-1368 is skipped.
The block goes right after the '# CLAUDE.md' header line; a dated backup CLAUDE.md.bak-2026-09-30-ceo-1368 is written first.
"""
import sys, os, shutil
ROOTS = ["ceo", "cto", "coo", "cfo"]
MARK = "CEO-1368"
BLOCK = (
    "⛔⭐⭐⭐⭐ **NO FRAME MARKERS — THE COLLECTOR NEVER INSPECTS A STACK WORD TO FIND A FRAME (Lon 2026-09-30 09:2x CDT, in-chat to the cto, verbatim: "
    "*\"Seems you should get rid of frame markers; they appear to be problematic. Find another better solution than scanning to markers on a stack.\"*; "
    "ruled CEO-1368; RULES.md § FACT RULE — NO FRAME MARKERS; design ARCH-GC-COMPILE-TIME-FRAME-MAPS.md § 11 THE FRAME LEDGER, the cto's rank-0 row):** "
    "the code that carves a mapped frame pushes a 16-byte {base, map} record on a per-thread ledger (one per co-expression, the top pointer one RTCC slot, "
    "grown like every runtime population); every release site trims the ledger to the new rsp BY ADDRESS; the collection trims to the floor and reads the "
    "records in address order; a frame whose interior is all tagged DESCRs needs no record. `gc_walk_cell`, the sniff loop, the DT_MAP cell stores and "
    "`map_off` are GONE at the end of the row's one batch (L1–L4); a landing that adds a marker the walker scans for is reverted on sight; the cto lands "
    "both halves, the cfo reviews the walker half after the fact; each layer gets a parse grid reading (no worse) because the push and the trims sit on "
    "the parse clock.\n\n"
    "⛔⭐⭐⭐⭐ **THE TREE IS BUILT ONCE, DIRECTLY, IN RECOGNITION ORDER; THE C TREE IS THE CANONICAL FORM; NO POST-PROCESSING (Lon 2026-09-30 morning, "
    "in-chat to the cfo, verbatim: *\"The C tree is the canonical form. It matters not, settle on ONE and we'll improve it later.\"* · *\"Just ensure that "
    "the tree is built from tokens in the same order as they are recognized by the PATTERN. No post processing of trees. The tree gets built directly and "
    "once only.\"*; ruled CEO-1369; RULES.md § FACT RULE — THE TREE IS BUILT ONCE):** every `bootstrap/parser_*.sc` builds its tree once at recognition and "
    "no pass rewrites a built node; a clause KEPT ASIDE until its parent is built (C's `dflt` for a case's default clause) is an operand of the single build, "
    "not a post-process, so the .sc holds it the same way and the trees stay identical with C untouched.\n\n"
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
        head = "# CLAUDE.md\n\n"
        if t.count(head) < 1:
            print(f"{r}: no '# CLAUDE.md' header, refused"); rc = 2; continue
        if not apply:
            print(f"{r}: would insert the {MARK}/CEO-1369 block after the header of {p}"); continue
        shutil.copy2(p, p + ".bak-2026-09-30-ceo-1368")
        t = t.replace(head, head + BLOCK, 1)
        open(p, "w", encoding="utf-8", newline="\n").write(t)
        print(f"{r}: inserted into {p}")
    return rc
if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
