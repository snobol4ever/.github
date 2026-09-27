#!/usr/bin/env python3
"""propagate_one_pass_geometric_start_small_ceo_1332.py -- append the CEO-1332 law digest to every seat root's CLAUDE.md.
Lon runs it (a seat's Bash write into a sibling root is refused by the harness classifier). Idempotent: a root whose
CLAUDE.md already carries 'CEO-1332' is skipped. LF only, bytes appended, nothing else touched.
Usage: python3 propagate_one_pass_geometric_start_small_ceo_1332.py [--dry-run]"""
import os, sys
ROOTS = ["ceo", "cto", "coo", "cfo", "icon", "prolog", "pascal", "snocone", "snobol4", "raku", "templates"]
BLOCK = ("\n## ⛔⭐⭐⭐ ONE PASS, GEOMETRIC, START SMALL -- NO MORE WHACK-A-MOLE (Lon 2026-09-27 ~16:5x CDT, in-chat to the cto; CEO-1332; "
         "law: RULES.md § FACT RULES, the NO FIXED LIMIT bullet; mechanism: ARCH-DYNAMIC-STORAGE.md § 4.1)\n\n"
         "Lon, verbatim, three messages in order: *\"How about instead of playing whack-a-mole with arrays that store lists (which can always overflow), "
         "do a scan and convert all in one pass. For the compiler it is easy, use the ct_realloc/ct_grow function (spelling?). For the runtime, do realloc at "
         "the frontier, and double-alloc with move and de-reference for GC heap items. Just go get them ALL in ONE SHOW. NO MORE WHACK A MOLE!!!!!!\"* · "
         "*\"What I mean by double-alloc, is geo-metric growth: i.e. times 2, then times 2, etc.\"* · *\"This also means you can start small and save memory "
         "space. Like 4, 8, 16, 32, etc. Or 1, 2, 4, 8, etc.\"* WHAT IT MEANS FOR THIS SEAT: every fixed table a program can fill is converted in ONE SWEEP "
         "under the cto's umbrella row `no-more-whack-a-mole-every-fixed-table-a-program-can-fill-is-converted-in-one-pass-…` (the cfo lands the compile-time "
         "half under it; the coo's `audit_fixed_caps_census.py` is the ratchet at both scopes, unguarded 0). Do not land a per-table cap cure of your own: a cap "
         "you hit is named to the cto's row by `ask`; a landing that adds a fixed cap or keeps an old cap as an `*_INIT` hint is reverted on sight. Growth is "
         "geometric (times 2) from a tiny start (4 or 8, or 1): compile-time through `ct_grow`/`cv_t`, runtime by realloc at the frontier and a typed doubling "
         "vector with a rooted handle on the GC heap.\n")
dry = "--dry-run" in sys.argv
for r in ROOTS:
    p = f"/home/claude_{r}/CLAUDE.md"
    if not os.path.exists(p):
        print(f"{r}: no CLAUDE.md at {p} -- skipped"); continue
    b = open(p, "rb").read()
    if b"CEO-1332" in b:
        print(f"{r}: already carries CEO-1332 -- skipped"); continue
    if dry:
        print(f"{r}: would append {len(BLOCK.encode())} bytes"); continue
    with open(p, "ab") as f:
        f.write(BLOCK.encode("utf-8"))
    print(f"{r}: appended")
