#!/usr/bin/env python3
"""propagate_pruned_parse_tree_ceo_1532.py [--apply] -- the two current law blocks into all eleven roots (ceo, CEO-1532).
The cto's 2026-10-07 09:0x measurement (cto to ceo, officer-digest-blocks-ceo-1529): RULES.md FACT RULE -- THE TREE IS THE PRUNED PARSE
TREE (Lon 2026-10-03, in-chat to hq_snocone) closes CEO-1369/1371/1377/1378, and ARCH-GC-COMPILE-TIME-FRAME-MAPS.md section 13 THE CHAIN
OVER THE MAPS is the live NO FRAME MARKERS design. The ceo, coo and cfo roots carried the superseded CEO-1377 and CEO-1369 tree blocks
and the 1492 frame block (the ceo's 09:0x CEO-1529 telegram told the cfo to copy them); the seven HQ roots carried neither rule, though
both bind every parser, C and .sc, and every frame. The two blocks below are the cto root's, verbatim.
Per root: the CEO-1377 block line is replaced by TREE; the CEO-1369 block line and the blank line after it are removed; a NO FRAME
MARKERS block line is replaced by FRAME; a root with no tree block gets TREE, and a root with no frame block gets FRAME, right after the
A ROW EXISTS block. Bytes are read and written as UTF-8 with LF kept; a dated backup CLAUDE.md.bak-2026-10-07-ceo-1532 is written beside
each root changed. Without --apply it prints what it would do. Idempotent: a second run changes nothing.
"""
import sys, os, shutil
ROOTS = ["ceo", "cto", "coo", "cfo", "icon", "prolog", "pascal", "snocone", "snobol4", "raku", "templates", "runtime", "collector"]
TREE = '⛔⭐⭐⭐⭐ **THE TREE IS THE PRUNED PARSE TREE: SOURCE ORDER, RAW SHIFT AND REDUCE WITH THE COUNTER STACK ONLY, BUILT ONCE; ONLY `tree_t` CROSSES TO LOWER (Lon 2026-10-03, in-chat to hq_snocone, verbatim: *"The right shape can be decided not by me but by the RULE, in the same left to right order as source input, and built directly from Shift/Reduce and the Counter stack primitives ONLY. That easy. The tree falls out directly from the syntax. It is a PRUNED PARSE TREE, it is not a FANCY SYNTAX TREE. Do not ask me this question again. Make a FACT RULE."*; closes CEO-1369/1371/1377/1378; and 2026-09-27, relayed at CEO-1322: *"Ensure that only the tree_t gets sent/used by parser stage to the lower stage. All global structures needed at runtime, are built in the lower stage."*; RULES.md § FACT RULE — THE TREE IS THE PRUNED PARSE TREE, § THE TREE IS BUILT ONCE, and the FACT RULES bullet ONLY tree_t CROSSES):** every language\'s `tree_t` is what the grammar\'s own rules produce when a pattern recognizes the source left to right and builds directly with `Shift`/`Reduce` and `PushCounter`/`IncCounter`/`PopCounter`/`nTop()` — one node per rule that fires, at the token that completes it, children in source order, nested as the syntax nests; no invented `STMT`/`ATTR` wrappers, no `ALT(SEQ(...))` framing, no desugaring, no keep-aside, no re-parenting, no second pass. Nobody chooses the shape and nobody asks Lon, the ceo or the cfo: a C or `.sc` tree that differs is the thing that changes and its desugars move to the lowerer (A PARSER MOVES NOTHING; THE LOWERER PLACES IT — Icon\'s case `default` is pushed where recognised and `lower_case` lowers it last, SCRIP `44dacedfb`); a `bootstrap/parser_*.sc` defines NO functions; the closure is `test_gate_snocone_parsers_match_the_c_parsers_tree_for_tree.sh`. CEO-1369\'s "the C tree is the canonical form" and its keep-aside reading are WITHDRAWN. A parser hands its lowerer the tree and nothing else — no side table keyed by node address, no registry, no parser function the lowerer calls; every table the runtime reads is built by LOWER, by a traversal over the tree, preferably during the lowering pass (CEO-1324).'
FRAME = '⛔⭐⭐⭐⭐ **NO FRAME MARKERS, NO SECOND STACK, THE MAPS STAY: THE STACK IS MAPPED, NOT TAGGED (Lon 2026-09-30 09:2x–09:5x CDT, in-chat to the cto, verbatim: *"Seems you should get rid of frame markers; they appear to be problematic. Find another better solution than scanning to markers on a stack."* · *"Do you have a plan without markers and without TWO stacks which should be one?"*; and 2026-10-03 17:1x CDT, to the cto: *"W do not want markers on the stack. We do want the stack mapped. We spent 3-4 days doing that. We do NOT want everything on the stack tagged. What is your malfunction?"*; ruled CEO-1368, corrected CEO-1371 and again CEO-1492; RULES.md § FACT RULE of the same name):** the compile-time frame maps of ARCH-GC-COMPILE-TIME-FRAME-MAPS.md § 7 (FROZEN) STAY; nothing on the stack is tagged beyond § 7 (a DESCR\'s type field is its only tag, a raw word is described by its frame\'s map); what goes is ONLY the marker scan. The side-car frame ledger (§ 11) and the every-raw-word-a-tagged-cell design (§ 12, CEO-1371) were the cto\'s readings under Lon\'s name and are WITHDRAWN — never revive either, and never widen a Lon ruling into a design Lon did not ask for. The live design is § 13 THE CHAIN OVER THE MAPS: a frame is found by its return PC (a per-site table emitted after each frame map, looked up by binary search) and its link word; the chain is checked against the marker scan at every collection under `SCRIP_GC_CHAIN_CHECK=1` until STEP B (§ 13.9 SIX) deletes the marker machinery — `DT_MAP`, `map_off`, `gc_walk_cell`, the 17 marker gates re-cut or retired by name — in ONE landing; GOAL-CTO.md\'s LIVE CURSOR holds where it stands. A landing that adds a marker scan, a second stack, a tagged-cell widening of raw words, or deletes a frame map is reverted on sight.'
K1377 = "\u26d4\u2b50\u2b50\u2b50\u2b50 **THE TREE IS THE ONE THE PATTERN BUILDS"
K1369 = "\u26d4\u2b50\u2b50\u2b50\u2b50 **THE TREE IS BUILT ONCE"
KTREE = "\u26d4\u2b50\u2b50\u2b50\u2b50 **THE TREE IS THE PRUNED PARSE TREE"
KFRAME = "\u26d4\u2b50\u2b50\u2b50\u2b50 **NO FRAME MARKERS"
KROW = "\u26d4\u2b50\u2b50\u2b50\u2b50 **A ROW EXISTS ONLY WHILE"
def line_span(t, k):
    s = t.find("\n" + k)
    if s < 0: return None
    s += 1; e = t.index("\n", s) + 1
    return s, e
def rewrite(t):
    notes = []
    sp = line_span(t, K1369)
    if sp:
        s, e = sp
        if t[e:e + 1] == "\n": e += 1
        t = t[:s] + t[e:]; notes.append("removed CEO-1369 block")
    sp = line_span(t, K1377)
    if sp:
        s, e = sp
        if line_span(t, KTREE): t = t[:s] + t[e + (1 if t[e:e + 1] == "\n" else 0):]; notes.append("removed CEO-1377 block (PRUNED present)")
        else: t = t[:s] + TREE + "\n" + t[e:]; notes.append("CEO-1377 block -> PRUNED PARSE TREE")
    sp = line_span(t, KTREE)
    if sp and t[sp[0]:sp[1]] != TREE + "\n":
        t = t[:sp[0]] + TREE + "\n" + t[sp[1]:]; notes.append("PRUNED PARSE TREE block refreshed")
    sp = line_span(t, KFRAME)
    if sp and t[sp[0]:sp[1]] != FRAME + "\n":
        t = t[:sp[0]] + FRAME + "\n" + t[sp[1]:]; notes.append("NO FRAME MARKERS block -> section 13 reading")
    add = []
    if not line_span(t, KTREE): add.append(TREE)
    if not line_span(t, KFRAME): add.append(FRAME)
    if add:
        sp = line_span(t, KROW)
        if not sp: raise SystemExit("REFUSED(2): no A ROW EXISTS block to anchor on")
        e = sp[1] + (1 if t[sp[1]:sp[1] + 1] == "\n" else 0)
        t = t[:e] + "".join(b + "\n\n" for b in add) + t[e:]; notes.append("inserted %d block(s) after A ROW EXISTS" % len(add))
    return t, notes
def main(argv):
    apply = "--apply" in argv
    changed = 0
    for r in ROOTS:
        p = "/home/claude_%s/CLAUDE.md" % r
        if not os.path.exists(p): print("%s: MISSING %s" % (r, p)); return 2
        t = open(p, "rb").read().decode("utf-8")
        nt, notes = rewrite(t)
        if nt == t: print("%s: current, unchanged" % r); continue
        assert rewrite(nt)[0] == nt, r
        changed += 1
        print("%s: %s%s" % (r, "; ".join(notes), "" if apply else " (dry run)"))
        if apply:
            shutil.copy2(p, p + ".bak-2026-10-07-ceo-1532")
            open(p, "wb").write(nt.encode("utf-8"))
    print(("APPLIED" if apply else "DRY-RUN"), changed, "of", len(ROOTS), "roots changed")
    return 0
if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
