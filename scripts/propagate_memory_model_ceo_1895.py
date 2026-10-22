#!/usr/bin/env python3
"""propagate_memory_model_ceo_1895.py [--apply] [--root=<seat>] -- the CEO-1895 digest into every root's CLAUDE.md: THE MEMORY MODEL IS
THE MALFUNCTION, THE PLACEMENT PROGRAMME IS CORRECTNESS, MODE TENET SIX SEATS (Lon 2026-10-22; ceo CEO-1895). It inserts its block after the
`# CLAUDE.md` line (or replaces it in place by its opening words), and rewrites the CEO-1886 block in place so no root still reads the
placement programme as speed. UTF-8, LF kept; a dated backup CLAUDE.md.bak-2026-10-22-ceo-1895 beside each root changed. Without --apply
it prints what it would do."""
import sys, os, shutil
ROOTS = ["ceo", "cto", "coo", "cfo", "icon", "prolog", "pascal", "snocone", "snobol4", "raku", "templates", "runtime", "collector", "zetas", "dotnet", "jvm", "packages"]
KEY = "⛔⭐⭐⭐⭐ **THE MEMORY MODEL IS THE MALFUNCTION; THE RSP/RBP PLACEMENT PROGRAMME IS CORRECTNESS, NOT SPEED; THE OFFICERS WORK IT"
BLOCK = (KEY + " (Lon 2026-10-22 09:3x-10:1x CDT, in-chat to the ceo, verbatim: *\"The CTO seems to think that we have been patching serious underlying "
         "problems with memory layout, usage, management. Do you agree. If so, work stops now and concentrates SOLELY on this with just the four officers "
         "working.\"* · *\"Well, CTO just said it was more than speed, that it WAS YOUR ENTIRE MALFUNCTION!!!!\"* · *\"Keep HQ-JVM and HQ-DOTNET working in the "
         "fleet.\"*; ruled CEO-1895, amending CEO-1886):** the cto measured it -- a third of SCRIP's landings re-decide memory placement one source shape at a "
         "time because two deciders exist (the layout grants every value box a frame slot, the emitter re-decides per shape through 27 predicates), frames are "
         "sized by keys (338,540 slots; a raised -s is the patch for a frame too big), and the Prolog activation's lifetime is not one rule; corrupted memory "
         "grades as FAIL, not segv. THE CURE is placement decided ONCE at lower from Lon's two tests (the home pass and the shared core, on origin), the "
         "per-regime switches in the order Pascal, Raku, Icon, Prolog, the emitter's predicates deleted as each lands, and the activation's lifetime under one "
         "design page. That programme is CORRECTNESS, rank 1 (the order census no longer reads it as speed). MODE TENET, SIX SEATS: ceo cto cfo coo hq_dotnet "
         "hq_jvm -- the four officers work the memory model alone (the cto designs and leads, the cfo builds, the coo verifies each landing and keeps the round "
         "robin, the ceo assigns and records), the two port HQs keep working snobol4dotnet and snobol4jvm one batched test run at a time; every other HQ stands "
         "down with its rows and batons in place until Lon restarts it. The box-wide pools stand: every SCRIP compile through util_cc_slot.sh (8 slots), every "
         "harness child through 8 run slots (CEO-1894).")
OLD_1886 = "⛔⭐⭐⭐⭐ **THE ORDER OF WORK IS (1) COMPLETENESS, (2) CORRECTNESS, (3) SPEED; THE RSP/RBP PLACEMENT PROGRAMME IS PART OF (3)"
NEW_1886 = ("⛔⭐⭐⭐⭐ **THE ORDER OF WORK IS (1) COMPLETENESS, (2) CORRECTNESS, (3) SPEED (Lon 2026-10-22 08:2x, CEO-1886; AMENDED at CEO-1895, the block above: "
            "the RSP/RBP placement programme is CORRECTNESS, not speed):** every seat serves (1) every program of its suites accepted and run, then (2) every "
            "suite row at 100% against its oracle, then (3) the bench bars and multiples. `test_gate_no_rsp_reset_at_beta.sh` is BLOCKING at 0; the placement "
            "watch measures at most once an hour under load and the ceo's banner prints it as one table.")
def span(t, k):
    s = t.find("\n" + k)
    if s < 0: return None
    s += 1
    return s, t.index("\n", s) + 1
def rewrite(t):
    notes = []
    sp = span(t, OLD_1886)
    if sp and t[sp[0]:sp[1]] != NEW_1886 + "\n":
        t = t[:sp[0]] + NEW_1886 + "\n" + t[sp[1]:]; notes.append("1886 block amended")
    sp = span(t, KEY)
    if sp:
        if t[sp[0]:sp[1]] != BLOCK + "\n":
            t = t[:sp[0]] + BLOCK + "\n" + t[sp[1]:]; notes.append("1895 block replaced")
    else:
        h = t.find("# CLAUDE.md\n")
        if h < 0: return t, "REFUSED: no '# CLAUDE.md' line"
        e = h + len("# CLAUDE.md\n")
        if t[e:e + 1] == "\n": e += 1
        t = t[:e] + BLOCK + "\n\n" + t[e:]; notes.append("1895 block inserted")
    return t, ", ".join(notes) or "present"
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
            shutil.copy2(p, p + ".bak-2026-10-22-ceo-1895"); open(p, "wb").write(nt.encode("utf-8")); print("%-10s WRITTEN (%s)" % (r, note))
        else:
            print("%-10s would write (%s)" % (r, note))
    return rc
if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
