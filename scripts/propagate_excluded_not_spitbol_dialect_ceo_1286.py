#!/usr/bin/env python3
"""CEO-1286 digest propagation (Lon-run: the harness refuses a ceo Bash write into a sibling root).
Lon 2026-09-26: a vendored SNOBOL4 package's denominator is the SPITBOL dialect; EXCLUDED=k is shown. This inserts one dated
override sentence in front of the first CEO-749 mention of every /home/claude_*/CLAUDE.md that carries one and no CEO-1286 yet,
a dated .bak beside each file first.
    python3 .github/scripts/propagate_excluded_not_spitbol_dialect_ceo_1286.py --dry-run | --apply [--only /home/claude_X/CLAUDE.md]
"""
import glob, shutil, sys, datetime
OV = ("(\u26d4\u2b50\u2b50\u2b50 CEO-1286, Lon 2026-09-26: a vendored SNOBOL4 package's published denominator is the SPITBOL DIALECT -- shipped minus the "
      "programs sbl -bf refuses FOR A CSNOBOL4 FEATURE SPITBOL LACKS, both halves measured and ruled one row each in the package's EXCLUDED.tsv; the row, "
      "the grid's Excl column and SUITES.tsv today_excluded show EXCLUDED=k; a refusal for any other cause keeps the program in as debt, and SPITBOL's own "
      "test deck is SPITBOL by origin; RULES.md section FACT RULES, THE PACKAGE DENOMINATOR IS THE SPITBOL DIALECT; the masters are unchanged; CEO-1288, Lon: the Excl column classifies EVERY exclusion for a good reason only -- a container fragment (CONTAINERS.tsv) or a not-SPITBOL program -- so shipped = denominator + Excl reads off any package row) ")
apply = "--apply" in sys.argv
only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
stamp = datetime.datetime.now().strftime("%Y-%m-%d-%H%M")
for f in sorted(glob.glob("/home/claude_*/CLAUDE.md")):
    if only and f != only: continue
    t = open(f, encoding="utf-8").read()
    if "CEO-1286" in t: print("already:", f); continue
    if "CEO-749" not in t: print("no anchor, skipped:", f); continue
    new = t.replace("CEO-749", OV + "CEO-749", 1)
    print(("APPLY " if apply else "would ") + f)
    if apply:
        shutil.copy2(f, f + ".bak-" + stamp + "-ceo1286")
        open(f, "w", encoding="utf-8").write(new)
