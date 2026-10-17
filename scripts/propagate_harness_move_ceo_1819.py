#!/usr/bin/env python3
"""propagate_harness_move_ceo_1819.py [--apply] [--root=<seat>] -- ONE digest block into every root's CLAUDE.md: THE HARNESS IS ITS OWN REPO,
A SIBLING OF SCRIP, corpus AND .github; NO SYMLINKS, EVER (Lon 2026-10-17; ceo CEO-1819/1820). The block is inserted after the `# CLAUDE.md`
line the way every propagate script inserts its block, or replaced in place by its opening words when present, so a second run changes
nothing. Bytes are read and written as UTF-8 with LF kept; a dated backup CLAUDE.md.bak-2026-10-17-ceo-1819 is written beside each root
changed. Without --apply it prints what it would do."""
import sys, os, shutil
ROOTS = ["ceo", "cto", "coo", "cfo", "icon", "prolog", "pascal", "snocone", "snobol4", "raku", "templates", "runtime", "collector", "zetas", "dotnet", "jvm"]
BLOCK_KEY = "⛔⭐⭐⭐⭐ **THE HARNESS IS ITS OWN REPO, A SIBLING OF SCRIP, corpus AND .github; SCRIP HAS NO scripts/; NO SYMLINK, EVER"
BLOCK = (BLOCK_KEY + " (Lon 2026-10-17 17:2x-17:5x CDT, in-chat to the ceo, verbatim: *\"Should not all this infrastructure around test harness and benchmarks be outside of "
         "SCRIP. Should it not be in snobol4ever/harness repo?\"* · *\"So if gates are shell scripts, they would go into snobol4ever/harness. The test harness LOGIC goes in HARNESS. "
         "The source code that is run by the harness goes in CORPUS.\"* · *\"Do not EVER use symlinks. Remove all symlink everywhere found in anywhere.\"* · *\"Use proper absolute and "
         "relative paths for things.\"* · *\"You guarantee the all repos are siblings at the same level in their root folder. done and done.\"* · *\"You also know that /home/resources is a "
         "sibling to the seat's roots.\"*; ruled CEO-1817/1819/1820):** every root holds its repos as siblings at one level -- `<root>/SCRIP` (the compiler: src/, the Makefile, the tools "
         "that generate or check its own source), `<root>/corpus` (the programs the harness runs, their refs and inputs), `<root>/harness` (EVERY script of the fleet: the postoffice bus "
         "`harness/scripts/s4e_msg.sh`, the suite harness and score rows, the runners, the 1,420 gates, the smokes, the benchmarks, the IPC sync-step monitor, the oracle builds and "
         "accessors, the censuses), `<root>/.github` (the law), and a port repo where the seat has one -- and `/home/resources` beside the roots. SCRIP/scripts/ IS GONE: a bus verb is "
         "`bash harness/scripts/s4e_msg.sh <verb>` from the root (or `bash ../harness/scripts/s4e_msg.sh` from SCRIP), a gate is `bash ../harness/scripts/test_gate_X.sh` from SCRIP, "
         "the Makefile's arms read `../harness/scripts/`, a DONE-WHEN that cds into SCRIP names `../harness/scripts/...`. A moved script reaches its siblings by fixed relative paths "
         "from its own folder (`$HERE/../../SCRIP`, `$HERE/../../corpus`), never by a link or an environment override. NO SYMBOLIC LINK is created by any code, build or seat "
         "(`test_gate_no_symlinks.sh`, blocking: no repo tracks one, SCRIP's build makes none, the 58 harness sites that still make one may only fall); a gate that stages a scratch "
         "tree copies the real shape (`lib_fixture_root.sh`), and a scratch SCRIP or corpus is a git worktree, never a link. The same harness and monitor drive SCRIP, snobol4dotnet "
         "and snobol4jvm, each an engine the harness grades against the same corpus and oracles.")
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
            shutil.copy2(p, p + ".bak-2026-10-17-ceo-1819")
            open(p, "wb").write(nt.encode("utf-8"))
            print("%-10s WRITTEN (%s)" % (r, note))
        else:
            print("%-10s would write (%s)" % (r, note))
    return rc
if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
