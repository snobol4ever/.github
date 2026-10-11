#!/usr/bin/env python3
"""propagate_suite_partitions_ceo_1676.py [--apply] [--root=<seat>] -- ONE digest block into all fourteen roots' CLAUDE.md: EVERY SUITE CARRIES A STORED
PARTITION (Lon 2026-10-11 13:0x CDT; ceo CEO-1676; RULES.md section ONE TESTING OFFICER clause (9); SCRIP a70e8e7e5, corpus 501ad6e77). The block is
inserted after the `# CLAUDE.md` line the way every propagate script inserts its block, or replaced in place by its opening words when present, so a
second run changes nothing. Bytes are read and written as UTF-8 with LF kept; a dated backup CLAUDE.md.bak-2026-10-11-ceo-1676 is written beside each
root changed. Without --apply it prints what it would do."""
import sys, os, shutil
ROOTS = ["ceo", "cto", "coo", "cfo", "icon", "prolog", "pascal", "snocone", "snobol4", "raku", "templates", "runtime", "collector", "zetas"]
BLOCK_KEY = "⛔⭐⭐⭐⭐ **EVERY SUITE CARRIES A STORED PARTITION -- A CORE, FEATURE SHELLS, BOUNDED CHUNKS -- LOOKED UP BY NAME, NEVER QUERIED PER LANDING"
BLOCK = (BLOCK_KEY + " (Lon 2026-10-11 13:0x CDT, in-chat to the ceo, verbatim: *\"One of the main take-aways concerning test suites, is that subsets need to be identified "
         "independent of a query against the attribute file for the long running test suites. So to partition them as major cores, and shells around that core with each major feature "
         "broken out. Or some kind of clustered partitioning.\"* · *\"One reason for the subsets on large suites is so they can be run in chunks even when the full regressions are being "
         "run in its \"spare\" time.\"*; ruled CEO-1676; RULES.md § ONE TESTING OFFICER clause (9); ARCH-SUITE-PARTITIONS.md; SCRIP a70e8e7e5, corpus 501ad6e77):** `PARTITION.tsv` sits "
         "beside every suite table (the seven masters' and every package's `ALL.csv`, 31 in all), built by `SCRIP/scripts/util_suite_partition.py build <ALL.csv>` and gated current by "
         "`test_gate_suite_partitions_are_current.sh` (blocking): the CORE covers every distinctive feature three times (2-11% of a suite; a feature marked by over half the entries is "
         "ubiquitous and the core's by definition), a SHELL is every entry marking a feature, every other entry is in one CLUSTER (its rarest distinctive feature, else its family or "
         "directory), and the clusters pack into CHUNKS of at most 100 entries, sized by seconds once the runners record them. The coo's loop runs tier 2 as `core` plus `shell:<feature>` "
         "for the features a landing's diff marks (a lookup) and tier 3 as every suite's chunks, one at a time in its spare time, pre-empted at chunk boundaries; a suite's row assembles "
         "from the latest per-program readings. A SEAT RUNS NO PARTITION (clause 7); it may read a shell's entries by name in `PARTITION.tsv` to choose a witness; A LANDING THAT CHANGES A "
         "SUITE TABLE (adds entries or feature columns) RUNS `util_suite_partition.py build` ON IT IN THE SAME LANDING, or the gate names it.")
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
