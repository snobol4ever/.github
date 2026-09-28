#!/usr/bin/env python3
"""util_declared_sizes_census.py -- every test unit of every language declares its heap and stack WITH ITSELF (Lon 2026-09-28
15:5x CDT, in-chat to the ceo, verbatim: "Ensure that every program in every language as it necessary stack size and heap size
values stored in the per-program attribute file, and ensure that those command-line switches and environment variable values are
being used by the harness shell scripts which run all of them."; ceo CEO-1353; RULES.md hard-cap rule clause 8 (b), (f), (g)).

A no-run census over the corpus. It never runs a program; it reads what is stored.

  util_declared_sizes_census.py [--lang L] [--names N] [--corpus DIR]

THE POPULATIONS:
  * the attribute tables: tests/<lang>/ALL.csv and packages/<lang>/<pkg>/ALL.csv -- every row carries a numeric heap_kb
    (at least 1024, the -i window) and a numeric stack_kb (at least 64); the census also prints how many rows carry the
    builder's default (131072 / 4096) and how many a measured value, because a default written by a builder is a
    declaration nobody measured (clause (g));
  * the standalone test units: every program under benchmarks/<lang>/ and demos/<lang>/ that carries a .ref beside it
    (RULES.md: a ref for every benchmark and test) -- each needs <stem>.heap and <stem>.stack sidecars, one line
    NAME<TAB>KB, read by SCRIP/scripts/lib_declared_arena.sh.

rc 0: every unit of the languages asked declares both, every value numeric and at or above its floor.
rc 1: a gap, NAMED (up to --names per population).
rc 2: could not measure (the corpus is missing, or a language asked has no population at all).
"""
import argparse, csv, os, sys

EXT = {"snobol4": (".sno",), "icon": (".icn",), "prolog": (".pl",), "pascal": (".pas",), "raku": (".raku",),
       "rebus": (".reb",), "snocone": (".sc",), "scrip": (".scrip", ".md")}
HEAP_DEFAULT, STACK_DEFAULT, HEAP_FLOOR, STACK_FLOOR = 131072, 4096, 1024, 64

def kb(v):
    v = (v or "").strip()
    return int(v) if v.isdigit() else None

def sidecar(path):
    try:
        with open(path, "rb") as f:
            line = f.read().decode("utf-8", "replace").strip().splitlines()
    except OSError:
        return None
    if not line:
        return None
    parts = line[0].split("\t")
    return kb(parts[-1]) if len(parts) >= 2 else None

def tables(corpus, lang):
    out = []
    t = os.path.join(corpus, "tests", lang, "ALL.csv")
    if os.path.isfile(t):
        out.append(t)
    pk = os.path.join(corpus, "packages", lang)
    if os.path.isdir(pk):
        for d in sorted(os.listdir(pk)):
            p = os.path.join(pk, d, "ALL.csv")
            if os.path.isfile(p):
                out.append(p)
    return out

def standalone(corpus, lang):
    units = []
    for tree in ("benchmarks", "demos"):
        root = os.path.join(corpus, tree, lang)
        if not os.path.isdir(root):
            continue
        for dp, dn, fn in os.walk(root):
            dn.sort()
            for f in sorted(fn):
                if f.endswith(EXT[lang]) and not f.startswith("ALL."):
                    stem = os.path.join(dp, os.path.splitext(f)[0])
                    if os.path.isfile(stem + ".ref"):
                        units.append((tree, stem, os.path.join(dp, f)))
    return units

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", choices=sorted(EXT), action="append")
    ap.add_argument("--names", type=int, default=12)
    ap.add_argument("--corpus", default=os.path.join(os.environ.get("S4E_HOME", os.getcwd()), "corpus"))
    a = ap.parse_args()
    corpus = a.corpus
    if not os.path.isdir(os.path.join(corpus, "tests")):
        print(f"REFUSE: no corpus at {corpus} (set S4E_HOME or --corpus)")
        return 2
    langs = a.lang or sorted(EXT)
    gaps = 0
    empty = []
    print(f"{'population':58} {'units':>6} {'declared':>8} {'gap':>5} {'default':>8} {'measured':>8}")
    for lang in langs:
        seen = 0
        for t in tables(corpus, lang):
            with open(t, newline="", encoding="utf-8", errors="replace") as f:
                rows = list(csv.DictReader(f))
            bad, dflt = [], 0
            for r in rows:
                h, s = kb(r.get("heap_kb")), kb(r.get("stack_kb"))
                if h is None or s is None or h < HEAP_FLOOR or s < STACK_FLOOR:
                    bad.append(r.get("entry") or r.get("rank") or "?")
                elif h == HEAP_DEFAULT and s == STACK_DEFAULT:
                    dflt += 1
            seen += len(rows)
            gaps += len(bad)
            rel = os.path.relpath(t, corpus)
            print(f"{rel:58} {len(rows):6} {len(rows) - len(bad):8} {len(bad):5} {dflt:8} {len(rows) - len(bad) - dflt:8}")
            if bad:
                print("    GAP rows: " + ", ".join(bad[:a.names]) + (" ..." if len(bad) > a.names else ""))
        by = {}
        for tree, stem, prog in standalone(corpus, lang):
            by.setdefault(tree, []).append((stem, prog))
        for tree in ("benchmarks", "demos"):
            us = by.get(tree, [])
            if not us:
                continue
            bad, dflt = [], 0
            for stem, prog in us:
                h, s = sidecar(stem + ".heap"), sidecar(stem + ".stack")
                if h is None or s is None or h < HEAP_FLOOR or s < STACK_FLOOR:
                    miss = [x for x, v in (("heap", h), ("stack", s)) if v is None or v < (HEAP_FLOOR if x == "heap" else STACK_FLOOR)]
                    bad.append(os.path.relpath(prog, os.path.join(corpus, tree, lang)) + "(" + "+".join(miss) + ")")
                elif h == HEAP_DEFAULT and s == STACK_DEFAULT:
                    dflt += 1
            seen += len(us)
            gaps += len(bad)
            label = f"{tree}/{lang} (units carrying a .ref)"
            print(f"{label:58} {len(us):6} {len(us) - len(bad):8} {len(bad):5} {dflt:8} {len(us) - len(bad) - dflt:8}")
            if bad:
                print("    GAP units: " + ", ".join(bad[:a.names]) + (" ..." if len(bad) > a.names else ""))
        if seen == 0:
            empty.append(lang)
    if empty and a.lang:
        print(f"REFUSE: no population found for {', '.join(empty)}")
        return 2
    print(f"DECLARED-SIZES {'CLEAN' if gaps == 0 else 'GAP'}: {gaps} unit(s) without a numeric heap and stack declaration"
          f" over {', '.join(langs)} (corpus {corpus})")
    return 0 if gaps == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
