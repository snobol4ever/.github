#!/usr/bin/env python3
"""propagate_order_of_work_ceo_1886.py [--apply] [--root=<seat>] -- ONE digest block into every root's CLAUDE.md: THE ORDER OF WORK IS
(1) COMPLETENESS, (2) CORRECTNESS, (3) SPEED, AND THE RSP/RBP PLACEMENT PROGRAMME IS PART OF (3) (Lon 2026-10-22; ceo CEO-1886). The block
is inserted after the `# CLAUDE.md` line the way every propagate script inserts its block, or replaced in place by its opening words when
present, so a second run changes nothing. Bytes are read and written as UTF-8 with LF kept; a dated backup CLAUDE.md.bak-2026-10-22-ceo-1886
is written beside each root changed. Without --apply it prints what it would do."""
import sys, os, shutil
ROOTS = ["ceo", "cto", "coo", "cfo", "icon", "prolog", "pascal", "snocone", "snobol4", "raku", "templates", "runtime", "collector", "zetas", "dotnet", "jvm", "packages"]
BLOCK_KEY = "⛔⭐⭐⭐⭐ **THE ORDER OF WORK IS (1) COMPLETENESS, (2) CORRECTNESS, (3) SPEED; THE RSP/RBP PLACEMENT PROGRAMME IS PART OF (3)"
BLOCK = (BLOCK_KEY + " (Lon 2026-10-22 08:2x CDT, in-chat to the ceo, verbatim, after the ceo estimated a week to take the placement columns to zero: *\"So put RBP/RSP "
         "priority lower than getting all language to 100% (1) completness, (2) correctness, and this task will be part of the (3) speed improvements.\"*; ruled CEO-1886, "
         "amending CEO-1562's order; MODE line 2 carries it):** every seat serves, in this order, (1) COMPLETENESS -- every program of every suite of its language accepted "
         "and run (an UNGRADED, NEEDS_DRIVER or feature-refused entry is incompleteness), then (2) CORRECTNESS -- every suite row of its language at 100% against its oracle, "
         "and only then (3) SPEED -- the bench bars AND the whole RSP/RBP placement programme: pre-allocations to 0, the misplaced locals, the disputed RBP homes, the "
         "state-word declarations and the per-regime switches (the eight placement rows are rank 3; the four switch rows stay PARKED-AWAITING the cto's shared core; the "
         "bootstrap parsers follow (3) as before). What stays: `test_gate_no_rsp_reset_at_beta.sh` is BLOCKING at 0 (a reset at a beta reds `make test`), the placement watch "
         "keeps measuring every origin tree and the ceo's banner keeps printing it as one table. `next` serves (1) and (2) rows before any (3) row in your lane; a seat with "
         "no (1)/(2) red in its language may then take a (3) row. The Prolog tabling rewrite (the cfo's, CEO-1883/1885) is (1)/(2) work, since SWI and XsbTests are the "
         "largest correctness debt on the board.")
def line_span(t, k):
    s = t.find("\n" + k)
    if s < 0: return None
    s += 1
    return s, t.index("\n", s) + 1
def rewrite(t):
    sp = line_span(t, BLOCK_KEY)
    if sp:
        if t[sp[0]:sp[1]] == BLOCK + "\n": return t, "block present"
        return t[:sp[0]] + BLOCK + "\n" + t[sp[1]:], "block replaced in place"
    h = t.find("# CLAUDE.md\n")
    if h < 0: return t, "REFUSED: no '# CLAUDE.md' line"
    e = h + len("# CLAUDE.md\n")
    if t[e:e + 1] == "\n": e += 1
    return t[:e] + BLOCK + "\n\n" + t[e:], "block inserted after '# CLAUDE.md'"
def main(argv):
    apply = "--apply" in argv
    only = [a for a in argv if a.startswith("--root=")]
    rc = 0
    for r in ([only[0][7:]] if only else ROOTS):
        p = "/home/claude_%s/CLAUDE.md" % r
        if not os.path.isfile(p): print("%-10s MISSING %s" % (r, p)); rc = 1; continue
        t = open(p, "rb").read().decode("utf-8")
        nt, note = rewrite(t)
        if nt == t: print("%-10s unchanged (%s)" % (r, note)); continue
        if apply:
            shutil.copy2(p, p + ".bak-2026-10-22-ceo-1886")
            open(p, "wb").write(nt.encode("utf-8"))
            print("%-10s WRITTEN (%s)" % (r, note))
        else:
            print("%-10s would write (%s)" % (r, note))
    return rc
if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
