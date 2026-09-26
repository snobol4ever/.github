#!/usr/bin/env python3
"""CEO-1281 digest propagation (Lon-run for the sibling roots: the harness refuses a ceo Bash write into one; the ceo applies its own root).
Lon 2026-09-26 11:1x-11:2x CDT, in-chat to the ceo, verbatim: "We are meant to have stack and heap size parameters stored in the per-test
attribute file for all the test suites." and "Basically the command-line arguments for compile time and run time (if needed) should be stored
per-test unit." -- RULES.md hard-cap rule clause 8 (f), GOAL-TEST-SUITE-CONSISTENCY.md point 8. This inserts one dated digest paragraph in front
of the SHIPPED DEFAULTS paragraph of every /home/claude_*/CLAUDE.md that carries it (else after its ## Testing heading), a dated .bak beside each.
    python3 .github/scripts/propagate_attribute_row_carries_the_command_line_ceo_1281.py --dry-run | --apply [--root /home/claude_X]
"""
import glob, os, shutil, sys, datetime
PARA = ("⛔⭐⭐⭐ **THE ATTRIBUTE ROW CARRIES THE TEST UNIT'S COMMAND LINE (Lon 2026-09-26 11:1x–11:2x CDT, in-chat to the ceo, verbatim: "
        "*\"We are meant to have stack and heap size parameters stored in the per-test attribute file for all the test suites.\"* · *\"Basically the "
        "command-line arguments for compile time and run time (if needed) should be stored per-test unit.\"*; CEO-1281; RULES.md hard-cap rule clause 8 (f); "
        "GOAL-TEST-SUITE-CONSISTENCY.md point 8):** every test unit — a master entry, a package program, a benchmark kernel, a demo — stores WITH ITSELF "
        "the command-line arguments its compile and its run need, and the runner reads them there and types none of its own. Today: `heap_kb` and `stack_kb` "
        "(every master and package row declares both; census 2026-09-26: 0 empty cells), argv (`ALL.argv`, `<stem>.argv`) and stdin (`ALL.in`, `<stem>.in`); "
        "the general shape ruled is a `compile_args` and a `run_args` attribute per test unit read by the ONE reader (`corpus_suite_harness.py` for the masters "
        "and package tables, `lib_declared_arena.sh` for a standalone program's sidecars) — the coo's rank-1 row. A standalone program (a benchmark kernel, an "
        "extracted entry) declares in `<stem>.heap` / `<stem>.stack` sidecars (one line `NAME<TAB>KB`), carried as `-d<kb>k -s<kb>k` switches on its command line "
        "(`declared_switches_beside`) — ⛔ NEVER `SCRIP_HEAP_KB`, which `gc_heap.c` reads as the collector's initial WINDOW. The Prolog, Pascal and Rebus "
        "benchmark kernels declare since corpus `a91273cef`/`e65e530ed`; snobol4, icon and raku kernels are a rank-2 row per HQ. Found because the Prolog benchmark "
        "angles ran tak at the shipped 4 MB stack, where it needs 64 MB (swipl 16 MB), and SKIPped it: a program graded under a default it did not declare is a false reading.\n\n")
ANCHOR = "⛔⭐ **THE SHIPPED DEFAULTS ARE SPITBOL'S"
TEST = "\n## Testing\n\n"
apply = "--apply" in sys.argv
roots = sorted(glob.glob("/home/claude_*/CLAUDE.md"))
if "--root" in sys.argv:
    roots = [os.path.join(sys.argv[sys.argv.index("--root") + 1], "CLAUDE.md")]
stamp = datetime.datetime.now().strftime("%Y-%m-%d-%H%M")
for f in roots:
    t = open(f, encoding="utf-8").read()
    if "CEO-1281" in t and "THE ATTRIBUTE ROW CARRIES" in t:
        print("already:", f); continue
    lines = t.split("\n"); hit = None
    if ANCHOR in t:
        new = t.replace(ANCHOR, PARA + ANCHOR, 1); how = "before the SHIPPED DEFAULTS paragraph"
    elif TEST in t:
        new = t.replace(TEST, TEST + PARA, 1); how = "after ## Testing"
    else:
        for i, l in enumerate(lines):
            if l.startswith("## Test"): hit = ("after", i); break
        if hit is None:
            for i, l in enumerate(lines):
                if l.startswith("## THE COLLECTOR"): hit = ("before", i); break
        if hit is None:
            print("no anchor, skipped (no Test or COLLECTOR heading):", f); continue
        kind, i = hit
        if kind == "after": lines = lines[:i + 1] + ["", PARA.rstrip("\n")] + lines[i + 1:]; how = "after its " + lines[i]
        else: lines = lines[:i] + [PARA.rstrip("\n"), ""] + lines[i:]; how = "before its " + lines[i + 2]
        new = "\n".join(lines)
    print(("APPLY " if apply else "would ") + f + " " + how)
    if apply:
        shutil.copy2(f, f + ".bak-" + stamp + "-ceo1281")
        open(f, "w", encoding="utf-8", newline="\n").write(new)
