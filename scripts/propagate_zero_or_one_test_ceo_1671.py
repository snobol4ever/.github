#!/usr/bin/env python3
"""propagate_zero_or_one_test_ceo_1671.py [--apply] [--root=<seat>] -- ONE digest block into all fourteen roots' CLAUDE.md: ZERO OR ONE TEST PER SEAT
PER LANDING (Lon 2026-10-11 11:5x CDT; ceo CEO-1671; RULES.md section ONE TESTING OFFICER clause (7); SCRIP 19f33b101, .github 1f98063b). The block is
inserted after the `# CLAUDE.md` line the way every propagate script inserts its block, or replaced in place by its opening words when present, so a
second run changes nothing. Bytes are read and written as UTF-8 with LF kept; a dated backup CLAUDE.md.bak-2026-10-11-ceo-1671 is written beside each
root changed. Without --apply it prints what it would do."""
import sys, os, shutil
ROOTS = ["ceo", "cto", "coo", "cfo", "icon", "prolog", "pascal", "snocone", "snobol4", "raku", "templates", "runtime", "collector", "zetas"]
BLOCK_KEY = "⛔⭐⭐⭐⭐ **ZERO OR ONE TEST PER SEAT PER LANDING; THE coo VERIFIES BY FEATURE AND CYCLES EVERYTHING"
BLOCK = (BLOCK_KEY + " (Lon 2026-10-11 11:5x CDT, in-chat to the ceo, verbatim: *\"What is the operating procedure for each officer seat regarding what to do after making "
         "changes? If it is to run the entire regression test suite, then that is wrong. Look at the load on this machine. How are you going to fix this mess.\"* · *\"We had set up "
         "attribute files before. Are those being used to reduce the number of tests run. I'm thinking each seat can run ZERO test, oh ONE test, instead. Then let COO prioritize testing "
         "on a per feature basis and still cycle through everything eventually.\"*; ruled CEO-1671, landed SCRIP 19f33b101 and .github 1f98063b the same sitting; RULES.md § ONE TESTING "
         "OFFICER clause (7)):** MEASURED at 11:57 CDT, load 29-31 on 16 cores -- every seat ran its DONE-WHEN AND every gate its diff touched AND `make preflight` (77 arms) AND the "
         "area smoke per landing, and `handoff_status.sh` regenerated all 102 `.s` artifacts (every demo and benchmark of every language compiled) at EVERY RESPONSE of every seat "
         "through the Stop hook's banner. THE RULE: a seat's verification of a landing is ITS ROW'S DONE-WHEN -- one measurement -- and NOTHING ELSE: no `make preflight`, no gate "
         "sweep over the diff, no area smoke, no artifact regeneration, no census or instrument that compiles or runs more than one program (such a run is a BOARD and only the coo's "
         "loop runs it, on a row asking it; a seat that needs one reads the coo's row through `util_suite_row_at_or_after.sh`). THE coo IS THE VERIFIER: its loop runs one run at a "
         "time and, for each origin landing, runs FIRST the feature that landing's diff marks (`test_area_smoke.sh`'s selection through `scripts/area_map.tsv` and the attribute rows' "
         "feature columns -- change SPAN, run the SPAN programs first), then `make preflight` and the blocking set once per batch of landings, the artifact regeneration once per batch, "
         "and cycles the whole SUITE TABLE eventually; a red reaches the lane by telegram with the range. THE HARNESS ENFORCES IT: `make preflight`, `test_area_smoke.sh` (its "
         "`--list-only` stays open to every seat) and the handoff artifact verifier REFUSE rc 2 for every seat but the coo, and a seat's handoff is not blocked by the drift it no "
         "longer grades; `S4E_ONE_TEST_ADMIT=\"why\"` is the ceo's loud audit-window override, never a seat's road. CEO-1663's no-pass hold on the coo is LIFTED. Every \"DONE-WHEN + "
         "the gates it touched + make preflight (+ the area smoke)\" below reads \"the row's DONE-WHEN alone\" from this ruling on.")
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
