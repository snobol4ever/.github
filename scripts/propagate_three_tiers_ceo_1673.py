#!/usr/bin/env python3
"""propagate_three_tiers_ceo_1673.py [--apply] [--root=<seat>] -- ONE digest block into all fourteen roots' CLAUDE.md: THE THREE TIERS OF THE VERIFIER
LOOP (Lon 2026-10-11 12:4x CDT; ceo CEO-1673; RULES.md section ONE TESTING OFFICER clause (8); SCRIP 6d639c986, .github 05d2d4ab) with the CEO-1674 template sentence. The block is
inserted after the `# CLAUDE.md` line the way every propagate script inserts its block, or replaced in place by its opening words when present, so a
second run changes nothing. Bytes are read and written as UTF-8 with LF kept; a dated backup CLAUDE.md.bak-2026-10-11-ceo-1673 is written beside each
root changed. Without --apply it prints what it would do."""
import sys, os, shutil
ROOTS = ["ceo", "cto", "coo", "cfo", "icon", "prolog", "pascal", "snocone", "snobol4", "raku", "templates", "runtime", "collector", "zetas"]
BLOCK_KEY = "⛔⭐⭐⭐⭐ **THE THREE TIERS OF THE VERIFIER LOOP: A SEAT PUSHES THROUGH; THE coo CATCHES SOON AFTER"
BLOCK = (BLOCK_KEY + " (Lon 2026-10-11 12:4x CDT, in-chat to the ceo, verbatim: *\"Re-think the work flow and ensure that each seat can push-thru fixing bugs and moving quickly to the next "
         "then having the COO catch soon after problems after the fact. The COO should run a set of super-fast test, a so-called smoke test, often. Then full regressions much less often. And in "
         "general run test subsets as features are changed.\"*; ruled CEO-1673, RULES.md § ONE TESTING OFFICER clause (8), SCRIP 6d639c986, .github 05d2d4ab):** TIER 0, THE SEAT: fix the bug, "
         "prove the row's ONE DONE-WHEN (CEO-1671), push, `done`, `next` -- wait for no verdict; a red the loop finds later reaches you by telegram with the range of landings since the last "
         "green reading, and you cure or revert within the tick (a one-landing range needs no bisect). TIER 1, THE FLEET SMOKE: `make fleet-smoke` (`../harness/scripts/test_fleet_smoke.sh`, the eight "
         "per-language smokes, measured 8-20 s, 121 checks) -- the coo runs it after EVERY origin landing, before anything else; it refuses every other seat; its record is "
         "`/home/resources/progress/SMOKE.tsv`. TIER 2, THE FEATURE SUBSET: per landing, the area smoke's selection through `area_map.tsv` and the attribute rows, CAPPED -- over 400 entries or "
         "a whole-language carrier means that language's rungs row (1-5 min), a shared node means the seven rungs rows (about 15 min) -- run ahead of any full-regression unit. TIER 3, THE FULL "
         "REGRESSION: the SUITE TABLE cycle, `make preflight`, the blocking set and the `.s` artifact regeneration in the loop's idle time, the last two at most once per three hours or per lap. "
         "TEMPLATES (CEO-1674; Lon 12:4x, verbatim: *\"For templates, Your rule of \"at most two static functions\" seems excessive.\"*): the two-statics cap is withdrawn from the templates census "
         "(SCRIP bc6df56f7); a template keeps the static helpers its shape needs; the line-oriented rules of CEO-1565 stand.")
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
