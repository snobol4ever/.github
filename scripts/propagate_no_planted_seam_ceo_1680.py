#!/usr/bin/env python3
"""propagate_no_planted_seam_ceo_1680.py [--apply] [--root=<seat>] -- ONE digest block into all fourteen roots' CLAUDE.md: NO BROKEN CODE PLANTED SO A
TEST CAN TRIP (Lon 2026-10-11 13:1x CDT to hq_snobol4; ceo CEO-1680; RULES.md FACT RULES, the CEO-554 line amended). The block is
inserted after the `# CLAUDE.md` line the way every propagate script inserts its block, or replaced in place by its opening words when present, so a
second run changes nothing. Bytes are read and written as UTF-8 with LF kept; a dated backup CLAUDE.md.bak-2026-10-11-ceo-1680 is written beside each
root changed. Without --apply it prints what it would do."""
import sys, os, shutil
ROOTS = ["ceo", "cto", "coo", "cfo", "icon", "prolog", "pascal", "snocone", "snobol4", "raku", "templates", "runtime", "collector", "zetas"]
BLOCK_KEY = "⛔⭐⭐⭐ **NO BROKEN CODE PLANTED SO A TEST CAN TRIP: CEO-554 NARROWED"
BLOCK = (BLOCK_KEY + " (Lon 2026-10-11 13:1x CDT, in-chat to hq_snobol4, verbatim: *\"Do not add broken code just to enable a test to determine a bug in PATTERN matching is fixed. "
         "Just create a proper test instead.\"*; ruled CEO-1680; RULES.md § FACT RULES, the CEO-554 line amended):** a criterion still fails once before it is trusted, but NEVER through a "
         "seam in SCRIP's own code -- no switch, plant or deliberately broken arm in `src/`, the runtime, the templates or the emitter that exists only so a test can fail (hq_snobol4's "
         "`SCRIP_TEST_PLANT_PATV_STAGING` in lower_snobol4.c, SCRIP 109979a01, is the counter-example; 99c52204d removed it). A gate proves it can fail with a PROPER test: a witness whose ref "
         "is cut from the oracle, shown red against a corrupted ref or the oracle's different answer, or a witness that reads red on the commit before the cure (a worktree of <cure>^). A "
         "cached-getenv seam stays allowed only inside an INSTRUMENT (a script's own switch), never in SCRIP. Every \"manufacture the trip through a cached-getenv test seam\" below reads this way.")
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
            shutil.copy2(p, p + ".bak-2026-10-11-ceo-1671")
            open(p, "wb").write(nt.encode("utf-8"))
            print("%-10s WRITTEN (%s)" % (r, note))
        else:
            print("%-10s would write (%s)" % (r, note))
    return rc
if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
