#!/usr/bin/env python3
"""propagate_handful_ceo_1677.py [--apply] [--root=<seat>] -- ONE digest block into all fourteen roots' CLAUDE.md: THE HANDFUL (Lon 2026-10-11
13:4x CDT; ceo CEO-1677; RULES.md section ONE TESTING OFFICER clause (7a); SCRIP 53a2be475). The block is
inserted after the `# CLAUDE.md` line the way every propagate script inserts its block, or replaced in place by its opening words when present, so a
second run changes nothing. Bytes are read and written as UTF-8 with LF kept; a dated backup CLAUDE.md.bak-2026-10-11-ceo-1677 is written beside each
root changed. Without --apply it prints what it would do."""
import sys, os, shutil
ROOTS = ["ceo", "cto", "coo", "cfo", "icon", "prolog", "pascal", "snocone", "snobol4", "raku", "templates", "runtime", "collector", "zetas"]
BLOCK_KEY = "⛔⭐⭐⭐⭐ **THE HANDFUL: A SEAT'S VERIFICATION OF A LANDING IS ITS DONE-WHEN PLUS A SMALL HANDFUL OF REPRESENTATIVE PROGRAMS DIRECTLY RELATED TO THE FIX"
BLOCK = (BLOCK_KEY + " (Lon 2026-10-11 13:4x CDT, in-chat to the ceo, verbatim: *\"I suspect the ONE TEST per change is too restrictive. It should be a small handful of representative "
         "programs directly related to the fix.\"*; ruled CEO-1677, amending CEO-1671's \"and nothing else\"; RULES.md § ONE TESTING OFFICER clause (7a); SCRIP 53a2be475):** per landing a seat "
         "runs its row's DONE-WHEN, then `bash scripts/test_feature_reps.sh <lang> <feature>...` -- the master partition's CORE entries whose shells carry the feature the fix touches "
         "(CEO-1676: 3-26 core entries carry a feature), in core order, capped at eight (`REPS_CAP`), graded by the harness's smoke engine in both modes with no progress row and no "
         "score row (measured: FENCE 8 of 15, 3.7 s); `--list` names them and runs nothing; the feature is named as the attribute table spells it (`test_area_smoke.sh --list-only` maps a "
         "diff to its features; a feature no shell carries refuses rc 2 and prints the vocabulary). THE BOUND STANDS: at most eight programs of the seat's own master -- never a package, "
         "a shell, a chunk, a suite, a gate sweep, `make preflight`, the area smoke or an artifact regeneration, which remain the coo's (CEO-1671/1673/1676); a landing that touches no "
         "feature column runs its DONE-WHEN alone. Then push and move to the next row; the coo's loop catches the rest.")
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
