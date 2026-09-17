#!/usr/bin/env python3
import sys, shutil, os
SENT = " ⛔⭐ SINCE 2026-09-17 THE COLLECTOR GUESSES NOTHING (Lon, in-chat to ceo; RULES.md FACT RULE; `ARCH-GC-COMPILE-TIME-FRAME-MAPS.md`; CEO-812): the emitter writes a compile-time map per safe point, the collector walks maps not words, the allocator never collects (only emitted code at the return of an allocating runtime call does), no conservative scan and no pinning in any form; rows maps → hq_icon, safe points → hq_prolog."
ROOTS = ["cto", "coo", "cfo", "icon", "prolog", "raku", "pascal", "snocone", "snobol4"]
ANCHOR = "ARCH-GC-PINNED-ALLOCATOR-LIFETIME-CLASSES.md"
for r in ROOTS:
    p = f"/home/claude_{r}/CLAUDE.md"
    if not os.path.exists(p): print(f"{r}: no CLAUDE.md, skipped"); continue
    s = open(p, encoding="utf-8").read()
    if "COLLECTOR GUESSES NOTHING" in s: print(f"{r}: already carries it"); continue
    shutil.copy(p, p + ".bak-2026-09-17-gc-frame-maps-812")
    if ANCHOR in s:
        i = s.index(ANCHOR) + len(ANCHOR); j = s.find("\n", i)
        s = s[:j] + SENT + s[j:]
    else:
        s = s.rstrip("\n") + "\n\n## THE COLLECTOR (CEO-812)\n\n-" + SENT + "\n"
    open(p, "w", encoding="utf-8").write(s); print(f"{r}: amended")
