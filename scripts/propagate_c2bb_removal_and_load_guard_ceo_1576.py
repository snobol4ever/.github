#!/usr/bin/env python3
"""propagate_c2bb_removal_and_load_guard_ceo_1576.py [--apply] [--root=<seat>] -- TWO digest clauses into all fourteen roots' CLAUDE.md in one
Lon-run command (ceo, 2026-10-09): (1) THE LOAD GUARD clause of CEO-1574 into the A-ROW-EXISTS block (propagate_load_guard_ceo_1574.py's edit,
still unapplied in the thirteen sibling roots at this writing; applied here idempotently), and (2) a new one-line ⛔ block, NO C FUNCTION ENTERS A
BOX, inserted after the `# CLAUDE.md` line the way every propagate script inserts its block (replaced in place by its opening words when present):
since SCRIP de85165fd no C function enters a box, the five asm shims are deleted, test_gate_no_c_to_bb.sh reads 0, and a program that dies with
"reached a C road into a box, DELETED" is a tolerated red that is already a row, never a regression to bisect. Bytes are read and written as UTF-8
with LF kept; a dated backup CLAUDE.md.bak-2026-10-09-ceo-1576 is written beside each root changed. Without --apply it prints what it would do; a
second run changes nothing. RULES.md § FACT RULE -- ERADICATE C->BB->C->BB (restated by Lon 2026-10-09, CEO-1576) carries the law."""
import sys, os, shutil
ROOTS = ["ceo", "cto", "coo", "cfo", "icon", "prolog", "pascal", "snocone", "snobol4", "raku", "templates", "runtime", "collector", "zetas"]
KEY_ROW = "⛔⭐⭐⭐⭐ **A ROW EXISTS ONLY WHILE A MEASUREMENT SAYS THE PROBLEM EXISTS"
OLD_ROW = "a refusal retires it, a TIMEOUT keeps it"
NEW_ROW = ("a refusal retires it unless it NAMES THE LOAD GUARD (CEO-1574: a bench bar prints `load-guard` with the load on a timing-shaped refusal taken at or above "
           "`BENCH_LOAD_GUARD_PER_CORE` per core, and the sweep keeps that row as a TIMEOUT, its ledger line not restarting the expiry clock -- a timing refusal under load is not a measurement, CEO-743), "
           "a TIMEOUT keeps it")
BLOCK_KEY = "⛔⭐⭐⭐⭐ **NO C FUNCTION ENTERS A BOX, ANYWHERE"
BLOCK = (BLOCK_KEY + " (Lon 2026-10-09 14:1x CDT, in-chat to the ceo, verbatim: *\"Go fix everywhere a C function calls into a BB. That is forbidden, not allowed.\"* · "
         "*\"List how many places call into BB's from C. Then stop the show and remove all of them.\"* · *\"instead of in C jumping to a BB, just return the address and have the BB that called the C function do the jump instead.\"* · "
         "*\"Another fix is to re-write the C in ASM.\"*; ruled CEO-1576, landed SCRIP a5ea776a8 → 5027d2161 → de85165fd the same day; RULES.md § FACT RULE — ERADICATE C→BB→C→BB, restated):** "
         "the five asm shims that jumped from C into emitted code (rt_tiny_record_enter, rt_proc_enter, rt_proc_enter_named, rt_chain_enter, rt_chain_enter_v) are DELETED and `test_gate_no_c_to_bb.sh` reads 0 sites "
         "outside the three sanctioned program entries; a C function that would transfer RETURNS THE ADDRESS and the box that called it does the jump (the `rt_call_next_t` open road: `rt_call_open_by_name_p`, "
         "`bb_glue_try_enter`, the request `rq` riding the call edge through the user-call hook), or the C is rewritten in asm; every C road that could not return mid-construct is a NAMED BOMB (`rt_c2bb_bomb`), "
         "so a program that dies with `reached a C road into a box, DELETED` is a TOLERATED RED THAT IS ALREADY A ROW (the ceo's: the CONVERT'd-expression chain road, the dynamic matcher's deferred call), "
         "never a regression to bisect or revert; a build flag such as `-ffixed-r12` is not a cure; a shim put back re-arms the gates by itself. A seat names these reds as tolerated under CEO-1576 in its receipts.\n")
def line_span(t, k):
    s = t.find("\n" + k)
    if s < 0: return None
    s += 1
    return s, t.index("\n", s) + 1
def rewrite(t):
    notes = []
    sp = line_span(t, KEY_ROW)
    if sp:
        line = t[sp[0]:sp[1]]
        if NEW_ROW not in line and OLD_ROW in line:
            t = t[:sp[0]] + line.replace(OLD_ROW, NEW_ROW, 1) + t[sp[1]:]; notes.append("load-guard clause written")
    else:
        notes.append("no A-ROW-EXISTS block (load-guard clause skipped)")
    sp = line_span(t, BLOCK_KEY)
    if sp:
        if t[sp[0]:sp[1]] != BLOCK:
            t = t[:sp[0]] + BLOCK + t[sp[1]:]; notes.append("C-to-BB block replaced in place")
    else:
        h = t.find("# CLAUDE.md\n")
        if h < 0: notes.append("REFUSED the C-to-BB block: no '# CLAUDE.md' line"); return t, notes
        e = h + len("# CLAUDE.md\n")
        if t[e:e + 1] == "\n": e += 1
        t = t[:e] + BLOCK + "\n" + t[e:]; notes.append("C-to-BB block inserted after '# CLAUDE.md'")
    return t, notes
def main(argv):
    apply = "--apply" in argv
    only = [a for a in argv if a.startswith("--root=")]
    for r in ([only[0][7:]] if only else ROOTS):
        p = "/home/claude_%s/CLAUDE.md" % r
        if not os.path.isfile(p): print("%-10s MISSING %s" % (r, p)); continue
        t = open(p, "rb").read().decode("utf-8")
        nt, notes = rewrite(t)
        if nt == t: print("%-10s unchanged (%s)" % (r, "; ".join(notes) or "both clauses present")); continue
        if apply:
            shutil.copy2(p, p + ".bak-2026-10-09-ceo-1576")
            open(p, "wb").write(nt.encode("utf-8"))
        print("%-10s %s%s" % (r, "; ".join(notes), "" if apply else " (dry run)"))
if __name__ == "__main__":
    main(sys.argv[1:])
