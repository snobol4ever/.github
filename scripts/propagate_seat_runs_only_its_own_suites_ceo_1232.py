#!/usr/bin/env python3
"""CEO-1232 digest propagation (Lon-run: the harness refuses a ceo Bash write into a sibling root).
Lon 2026-09-24 ~08:0x CDT to hq_prolog: a seat runs only its own language's suites. This inserts one dated
override sentence in front of the CEO-757 batch bullet of every /home/claude_*/CLAUDE.md that still carries it
(and a retirement note on the CONTROL-ARM BAR heading where present), a dated .bak beside each file first.
    python3 .github/scripts/propagate_seat_runs_only_its_own_suites_ceo_1232.py --dry-run | --apply
"""
import glob, os, shutil, sys, datetime
OV = ("\u26d4\u2b50\u2b50\u2b50\u2b50 **A SEAT RUNS ONLY ITS OWN LANGUAGE'S SUITES (Lon 2026-09-24 ~08:0x CDT, in-chat to hq_prolog, verbatim: "
      "*\"tell CEO to figure a way for each seat to not run any other language tests. Just have each seat run only their own test suites.\"*; CEO-1232; "
      "RULES.md \u00a7 SHARED-NODE VERDICT SCOPE, the 2026-09-24 paragraph at its head): the CEO-757 batch below is RETIRED \u2014 a shared-node landing is graded "
      "by the lander on its OWN language's suites, the commit names the node and the frontends it reaches, and every other language's verdict is read by that "
      "language's HQ's next per-landing pass on origin (the HQ stamps the range it covers, bisects a red over it and names the commit; the lander cures or "
      "reverts within the tick); the officers run no board and ask an HQ for its pass; the one-runner override is no road to another language's board.** ")
MARK = "\u26d4\u2b50\u2b50\u2b50 **THE CROSS-LANGUAGE ARMS BATCH"
FOOT = "## \u26d4\u2b50 THE CONTROL-ARM BAR"
FOOTNEW = FOOT + " \u2014 \u26d4 THE BATCH FORM BELOW IS RETIRED 2026-09-24 (CEO-1232): the OTHER frontends' arms are each HQ's next per-landing pass on origin, never the lander's run; the bar (no worse than a clean tree, every tolerated red named) is unchanged and is now applied by the HQ that reads it"
apply = "--apply" in sys.argv
stamp = datetime.datetime.now().strftime("%Y-%m-%d-%H%M")
for f in sorted(glob.glob("/home/claude_*/CLAUDE.md")):
    t = open(f, encoding="utf-8").read()
    if "CEO-1232" in t:
        print("already:", f); continue
    n = t.count(MARK); m = t.count(FOOT)
    if n == 0:
        print("no batch bullet, skipped:", f); continue
    new = t.replace(MARK, OV + MARK, 1)
    if m == 1: new = new.replace(FOOT, FOOTNEW, 1)
    print(("APPLY " if apply else "would ") + f + " (batch bullets %d, foot %d)" % (n, m))
    if apply:
        shutil.copy2(f, f + ".bak-" + stamp + "-ceo1232")
        open(f, "w", encoding="utf-8").write(new)
