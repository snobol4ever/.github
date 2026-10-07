#!/usr/bin/env python3
"""propagate_no_global_holds_a_stack_ceo_1542.py [--apply] -- the NO GLOBAL HOLDS A STACK digest block into all fourteen roots (ceo, CEO-1542/1543).
Lon 2026-10-07, in-chat to the ceo, verbatim: "Some Icon had not got the memo that global variables holding a stack are not allowed, since we
already have a stack." The law is RULES.md FACT RULE -- NO GLOBAL HOLDS A STACK; the Icon design is ARCH-ICON-RTX.md section 9; the plan for
the rest is ARCH-GLOBAL-STACKS-TO-THE-ZETAS.md. Per root: the block line is inserted right after the NO FRAME MARKERS block (which it widens),
or refreshed in place when present and different. Bytes are read and written as UTF-8 with LF kept; a dated backup CLAUDE.md.bak-2026-10-07-ceo-1542
is written beside each root changed. Without --apply it prints what it would do. Idempotent: a second run changes nothing.
"""
import sys, os, shutil
ROOTS = ["ceo", "cto", "coo", "cfo", "icon", "prolog", "pascal", "snocone", "snobol4", "raku", "templates", "runtime", "collector", "zetas"]
BLOCK = ('⛔⭐⭐⭐⭐ **NO GLOBAL HOLDS A STACK: THE MACHINE STACK IS THE STACK; A SECOND STACK IS DELETED FIRST AND ITS READERS LEFT AS NAMED BOMBS (Lon 2026-10-07 17:4x–18:2x CDT, in-chat to the ceo, verbatim: '
         '*"Some Icon had not got the memo that global variables holding a stack are not allowed, since we already have a stack."* · *"We keep all R12 usages of the stack, CAS and choice-point are in a seperate MMAP\'d region."* · '
         '*"So you, CEO, are in charge of all these global stacks and their re-design."*; to hq_icon, 16:2x: *"Remove the g_icn_act global variable from the source and replace all it\'s references with a "* (char *) NULL" construct so it bombs nicely. We like bombs to show where we need code to be fixed."* · '
         '*"Not a prolem that ALL Icon programs broke. They will be fixed soon enough."*; ruled CEO-1542/1543; RULES.md § FACT RULE — NO GLOBAL HOLDS A STACK):** no global, static, `cv_t`, arena or heap structure holds one entry per live call, activation, match, scan, generator or nested construct, pushed at entry and popped at exit or indexed by a level counter — '
         'that is a second stack and the machine stack already is one. The construct\'s record is its FRAME (THE LIFETIME RULE); what is a compile-time constant of the procedure or the call site (a name, an arity, a call site\'s line) is static data in the frame\'s SHAPE or the code map keyed by the return PC, never stored per activation; '
         'a reader that needs every live activation (a traceback, `display()`, `&trace`) walks the frames by ARCH-GC § 13\'s chain (return PC → site table → shape → link word), never a side table. A single "current X" cell is not a stack. THE BOMB IS THE METHOD: a forbidden second stack is deleted in one landing and every reader left as a named bomb '
         '(`x86_bomb("<site>: …")` in emitted code; in C a used load of `* (char *) NULL` — a bare one compiles to nothing at -O0); the reds are the work list, nobody reverts or bisects a bomb landing, and a receipt names them as tolerated under the ruling. THE ONLY STACKS OUTSIDE RSP/RBP are the two r12 islands Lon keeps — the SNOBOL4 conditional-assignment stack and the Prolog trail/choice points, mmap\'d slab regions whose entries are LIFO with a choice point or a match, not with frames. '
         'THE FIRST INSTANCE: Icon\'s `g_icn_act` (deleted at SCRIP `ca33ff82a`, every Icon call bombs rc 134 until hq_icon\'s rank-0 row lands ARCH-ICON-RTX.md § 9 THE ACTIVATION RECORD IS THE FRAME: zero words added to any frame, the name/np/args_off static facts of the shape, the caller\'s line a code-map row at the γ/ω landing, the one reader the § 13.4 chain walk with a visitor). '
         'THE REST: `SCRIP/scripts/audit_second_stacks_census.py` names the twelve others with their lane and placement (ARCH-GLOBAL-STACKS-TO-THE-ZETAS.md § 2: activation frame, spine, or ζ-STANDING for a head cell); each is a rank-2 row whose DONE-WHEN is `--name X` green plus the language\'s smoke. ALL OF THIS WORK IS THE ceo\'s (Lon 18:3x: *"Stay in TENET mode but know that ALL work is yours."* · *"The fleet will become idle while they wait for you."*): the ceo designs AND lands every one, Icon first, each deletion a whole landing, while every other seat keeps its own rows; a seat touches none of these names and names their reds as tolerated under CEO-1542; then Lon runs ultracode.')
KEY = "⛔⭐⭐⭐⭐ **NO GLOBAL HOLDS A STACK"
KFRAME = "⛔⭐⭐⭐⭐ **NO FRAME MARKERS"
KROW = "⛔⭐⭐⭐⭐ **A ROW EXISTS ONLY WHILE"


def line_span(t, k):
    s = t.find("\n" + k)
    if s < 0:
        return None
    s += 1
    e = t.index("\n", s) + 1
    return s, e


def rewrite(t):
    sp = line_span(t, KEY)
    if sp:
        if t[sp[0]:sp[1]] == BLOCK + "\n":
            return t, None
        return t[:sp[0]] + BLOCK + "\n" + t[sp[1]:], "block refreshed"
    anchor = line_span(t, KFRAME) or line_span(t, KROW)
    if anchor:
        e = anchor[1]
        if t[e:e + 1] == "\n":
            e += 1
        return t[:e] + BLOCK + "\n\n" + t[e:], "block inserted after the %s block" % ("NO FRAME MARKERS" if line_span(t, KFRAME) else "A ROW EXISTS")
    head = t.find("\n# CLAUDE.md\n")
    if head < 0:
        return t, "REFUSED: no # CLAUDE.md line and no anchor block"
    e = head + len("\n# CLAUDE.md\n")
    if t[e:e + 1] == "\n":
        e += 1
    return t[:e] + BLOCK + "\n\n" + t[e:], "block inserted after # CLAUDE.md"


def main(argv):
    apply = "--apply" in argv
    changed = 0
    for r in ROOTS:
        p = "/home/claude_%s/CLAUDE.md" % r
        if not os.path.isfile(p):
            print("%-10s MISSING %s" % (r, p))
            continue
        with open(p, "rb") as fh:
            raw = fh.read()
        t = raw.decode("utf-8")
        nt, note = rewrite(t)
        if note is None:
            print("%-10s unchanged" % r)
            continue
        if note.startswith("REFUSED"):
            print("%-10s %s" % (r, note))
            continue
        changed += 1
        if apply:
            shutil.copy2(p, p + ".bak-2026-10-07-ceo-1542")
            with open(p, "wb") as fh:
                fh.write(nt.encode("utf-8"))
        print("%-10s %s%s" % (r, note, "" if apply else " (dry run)"))
    print(("APPLIED" if apply else "DRY-RUN"), changed, "of", len(ROOTS), "roots changed")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
