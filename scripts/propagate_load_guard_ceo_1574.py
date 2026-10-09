#!/usr/bin/env python3
"""propagate_load_guard_ceo_1574.py [--apply] [--root=<seat>] -- THE LOAD GUARD clause into the A-ROW-EXISTS digest block of all fourteen
roots (ceo, CEO-1574, 2026-10-08 22:xx CDT). The sweep's rule in every root's CLAUDE.md reads "a refusal retires it, a TIMEOUT keeps it";
since SCRIP 470a0fc7b and .github a3248fbb a refusal that NAMES THE LOAD GUARD (a bench bar's timing-shaped refusal taken at or above
BENCH_LOAD_GUARD_PER_CORE per core, printed through perf_load_guard with the words load-guard) is KEPT as a TIMEOUT is kept -- the sweeps of
10-07 20:16 and 10-08 15:18 and 19:17 had retired fourteen live performance rows under the fleet's builds. Per root: the one phrase is
rewritten in place inside the block; a root that already carries the clause is unchanged. Bytes are read and written as UTF-8 with LF kept;
a dated backup CLAUDE.md.bak-2026-10-08-ceo-1574 is written beside each root changed. Without --apply it prints what it would do.
Idempotent: a second run changes nothing. RULES.md § FACT RULE -- A ROW EXISTS ONLY WHILE A MEASUREMENT SAYS THE PROBLEM EXISTS carries the law.
"""
import sys, os, shutil
ROOTS = ["ceo", "cto", "coo", "cfo", "icon", "prolog", "pascal", "snocone", "snobol4", "raku", "templates", "runtime", "collector", "zetas"]
KEY = "⛔⭐⭐⭐⭐ **A ROW EXISTS ONLY WHILE A MEASUREMENT SAYS THE PROBLEM EXISTS"
OLD = "a refusal retires it, a TIMEOUT keeps it"
NEW = ("a refusal retires it unless it NAMES THE LOAD GUARD (CEO-1574: a bench bar prints `load-guard` with the load on a timing-shaped refusal taken at or above "
       "`BENCH_LOAD_GUARD_PER_CORE` per core, and the sweep keeps that row as a TIMEOUT, its ledger line not restarting the expiry clock -- a timing refusal under load is not a measurement, CEO-743), "
       "a TIMEOUT keeps it")
def line_span(t, k):
    s = t.find("\n" + k)
    if s < 0:
        return None
    s += 1
    e = t.index("\n", s) + 1
    return s, e
def rewrite(t):
    sp = line_span(t, KEY)
    if not sp:
        return t, "REFUSED: no A-ROW-EXISTS block"
    line = t[sp[0]:sp[1]]
    if NEW in line:
        return t, None
    if OLD not in line:
        return t, "REFUSED: the block carries neither the old phrase nor the new one"
    return t[:sp[0]] + line.replace(OLD, NEW, 1) + t[sp[1]:], "load-guard clause written into the block"
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
            shutil.copy2(p, p + ".bak-2026-10-08-ceo-1574")
            open(p, "wb").write(nt.encode("utf-8"))
        print("%-10s %s%s" % (r, what, "" if apply else " (dry run)"))
if __name__ == "__main__":
    main(sys.argv[1:])
