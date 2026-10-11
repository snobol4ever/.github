#!/usr/bin/env python3
"""propagate_no_oracle_answer_ceo_1696.py [--apply] [--root=<seat>] -- ONE digest block into all fourteen roots' CLAUDE.md: A PROGRAM WITH NO ORACLE
ANSWER IS EXCLUDED (Lon 2026-10-11 16:0x CDT; ceo CEO-1696; RULES.md section Oracles). The block is
inserted after the `# CLAUDE.md` line the way every propagate script inserts its block, or replaced in place by its opening words when present, so a
second run changes nothing. Bytes are read and written as UTF-8 with LF kept; a dated backup CLAUDE.md.bak-2026-10-11-ceo-1696 is written beside each
root changed. Without --apply it prints what it would do."""
import sys, os, shutil
ROOTS = ["ceo", "cto", "coo", "cfo", "icon", "prolog", "pascal", "snocone", "snobol4", "raku", "templates", "runtime", "collector", "zetas"]
BLOCK_KEY = "⛔⭐⭐⭐⭐ **A PROGRAM WITH NO ORACLE ANSWER IS EXCLUDED, NEVER DEBT"
BLOCK = (BLOCK_KEY + " (Lon 2026-10-11 16:0x CDT, in-chat to the ceo, verbatim: *\"Exclude any program in which we have no way to get output from an oracle, or in which we do not "
         "know the answer.\"*; ruled CEO-1696; RULES.md § Oracles, the FACT RULE of the same name; amends CEO-749 and CEO-1518 for that class only):** a program the oracle gives NO "
         "OUTPUT for (it refuses, crashes, aborts, hangs past its declared time, or cannot run it) or whose ANSWER IS NOT KNOWN (no ref, a ref not the oracle's, an answer no run reproduces) "
         "leaves its suite's denominator as an EXCLUDED row of class NO_ORACLE_ANSWER with its measurement, shown in the Excl column; every program the oracle DOES answer stays in "
         "the denominator as debt SCRIP owes, including one SCRIP refuses by a dialect rule or lacks a feature for. The runners' UNGRADABLE.tsv lists become those exclusions and the "
         "coo re-reads each moved row with criterion_changed naming CEO-1696; a program that becomes answerable returns to the denominator in the landing that gives it its answer.")
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
