#!/usr/bin/env python3
"""CEO-1241 digest propagation (Lon-run: the harness refuses a ceo Bash write into a sibling root).
Lon 2026-09-24 15:2x CDT to the ceo: "Always show the x-factor in a consistent manner. That is 1.5x faster for example."
This inserts one dated override sentence in front of the s266 unit bullet of every /home/claude_*/CLAUDE.md that still
carries it, a dated .bak beside each file first.
    python3 .github/scripts/propagate_x_factor_direction_word_ceo_1241.py --dry-run | --apply
"""
import glob, shutil, sys, datetime
OV = ("⛔⭐⭐ **THE x-FACTOR ALWAYS CARRIES ITS DIRECTION WORD (Lon 2026-09-24 15:2x CDT, in-chat to the ceo, verbatim: "
      "*\"Always show the x-factor in a consistent manner. That is 1.5x faster for example.\"*; CEO-1241; RULES.md FACT RULE at the head of "
      "THE UNIT IS x): one spelling everywhere, `<factor>x faster` or `<factor>x slower`, the factor at or above 1.0 with one decimal, read "
      "from SCRIP's side against the named reference (0.16x is spelled 6.3x slower); `perf_mult` prints it; the s266 sentence that follows "
      "is the record.** ")
MARKS = ["**THE UNIT IS `x`, A MULTIPLE, ON THE FASTER AXIS", "THE UNIT IS `x`", "THE UNIT IS x"]
apply = "--apply" in sys.argv
stamp = datetime.datetime.now().strftime("%Y-%m-%d-%H%M")
for f in sorted(glob.glob("/home/claude_*/CLAUDE.md")):
    t = open(f, encoding="utf-8").read()
    if "CEO-1241" in t:
        print("already:", f); continue
    mark = next((m for m in MARKS if m in t), None)
    if mark is None:
        print("no unit bullet, skipped:", f); continue
    new = t.replace(mark, OV + mark, 1)
    print(("APPLY " if apply else "would ") + f + " at " + repr(mark))
    if apply:
        shutil.copy2(f, f + ".bak-" + stamp + "-ceo1241")
        open(f, "w", encoding="utf-8").write(new)
