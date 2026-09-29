#!/usr/bin/env python3
"""CEO-1316 digest propagation (Lon-run for sibling roots: the harness refuses a ceo Bash write into a sibling root).
Lon 2026-09-27 10:4x, to the cfo: batch up at least 3-4 changes before requiring a test run. This inserts one dated paragraph after the
title line of every /home/claude_*/CLAUDE.md that carries no CEO-1316 yet, a dated .bak beside each file first; it also runs
python3 .github/scripts/propagate_excluded_not_spitbol_dialect_ceo_1286.py's pending digests if passed --with-1286.
    python3 .github/scripts/propagate_heavy_verification_once_per_batch_ceo_1316.py --dry-run | --apply [--only /home/claude_X/CLAUDE.md]
"""
import glob, shutil, sys, datetime
OV = ("⛔⭐⭐⭐⭐ **HEAVY VERIFICATION RUNS ONCE PER BATCH OF THREE TO FOUR CHANGES, NEVER PER CHANGE (Lon 2026-09-27 10:4x CDT, in-chat to the cfo, "
      "verbatim: *\"I suspect you should batch up at least 3-4 changes before requiring a test run. You'll know that one of the four is the culprit.\"*; "
      "ruled fleet-wide at CEO-1316; RULES.md section HEAVY VERIFICATION RUNS ONCE PER BATCH, at the head of the SHARED-NODE VERDICT SCOPE block):** the full "
      "blocking set, a pristine rebuild, the tiny-arena pass and stress plant, a rung suite/package/bench suite pass and a cross-language sweep run ONCE PER BATCH "
      "of three to four landings (an HQ's pass on origin: per three to four origin landings reaching its language, stamping the range); a batch red is bisected "
      "within the batch; PER LANDING stays the row's DONE-WHEN + the gates it touched + make preflight; SNOBOL4 boards one pass per day; never two heavy runs "
      "in flight. Every \"once per landing\" and \"per collector landing\" below reads \"once per batch of three to four\".\n\n")
apply = "--apply" in sys.argv
only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
stamp = datetime.datetime.now().strftime("%Y-%m-%d-%H%M")
for f in sorted(glob.glob("/home/claude_*/CLAUDE.md")):
    if only and f != only: continue
    t = open(f, encoding="utf-8").read()
    if "CEO-1316" in t: print("already:", f); continue
    lines = t.split("\n")
    ti = next((i for i, l in enumerate(lines) if l.startswith("# ")), None)
    if ti is None: print("no title line, skipped:", f); continue
    j = ti + 1
    while j < len(lines) and lines[j] == "": j += 1
    new = "\n".join(lines[:j]) + "\n" + OV + "\n".join(lines[j:])
    print(("APPLY " if apply else "would ") + f)
    if apply:
        shutil.copy2(f, f + ".bak-" + stamp + "-ceo1316")
        open(f, "w", encoding="utf-8", newline="\n").write(new)
if "--with-1286" in sys.argv:
    import subprocess
    subprocess.run([sys.executable, __file__.replace("propagate_heavy_verification_once_per_batch_ceo_1316.py", "propagate_excluded_not_spitbol_dialect_ceo_1286.py")] + (["--apply"] if apply else ["--dry-run"]), check=False)
