#!/usr/bin/env python3
"""util_stack_countdown.py -- THE COUNTDOWN BANNER of the global-stack eradication (Lon 2026-10-07, verbatim: "Give me a countdown
counter: how many global stack have you eradicated."; CEO-1544). One line, computed from the source tree, never typed:
every censused second stack (SCRIP/scripts/audit_second_stacks_census.py, the KEPT r12 islands excluded) is GONE when no whole-word
reference remains under src/, BOMBED when every remaining reference is a bomb string that names its deletion, LIVE otherwise.
    python3 .github/scripts/util_stack_countdown.py [--long]
"""
import os, re, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CENSUS = os.path.join(ROOT, "SCRIP", "scripts", "audit_second_stacks_census.py")


def main(argv):
    if not os.path.isfile(CENSUS):
        print("STACK COUNTDOWN: REFUSED (rc=2): %s is missing" % CENSUS)
        return 2
    spec = importlib.util.spec_from_file_location("census", CENSUS)
    census = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(census)
    files = list(census.source_files())
    if not files:
        print("STACK COUNTDOWN: REFUSED (rc=2): no source files under SCRIP/src")
        return 2
    gone, bombed, live = [], [], []
    for name, lane, lang, smoke, place in census.TABLE:
        rx = re.compile(r"(?<![A-Za-z0-9_])" + re.escape(name) + r"(?![A-Za-z0-9_])")
        refs = bomb = 0
        for p in files:
            try:
                with open(p, "rb") as fh:
                    for line in fh.read().decode("utf-8", "replace").split("\n"):
                        k = len(rx.findall(line))
                        if not k:
                            continue
                        refs += k
                        if "is deleted" in line or "BOMB" in line or "bomb" in line:
                            bomb += k
            except OSError:
                continue
        (gone if refs == 0 else bombed if refs == bomb else live).append(name)
    total = len(census.TABLE)
    print("STACK COUNTDOWN: %d to eradicate | GONE %d | BOMBED %d | LIVE %d  (kept by Lon: the CAS and the Prolog trail, r12 islands)" % (total, len(gone), len(bombed), len(live)))
    if "--long" in argv:
        for label, names in (("GONE", gone), ("BOMBED", bombed), ("LIVE", live)):
            print("  %-7s %s" % (label, " ".join(names) if names else "-"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
