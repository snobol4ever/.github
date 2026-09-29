#!/usr/bin/env python3
"""Restore the .inc extension on SNOBOL4 include libraries (Lon 2026-09-14).

Lon, in-chat to ceo, verbatim: "Change the *.sno to *.inc. We changed many of those names way back
and we should not have changed *.inc to *.sno for include files."

WHAT AN INCLUDE FILE IS, DECIDED BY THE FILE ITSELF and not by this script's taste: its first line
names it, e.g. `* SNOREAD.inc - SNOREAD() will read in and return the next SNOBOL4 statement`. That
header is upstream's own statement of the file's name, so it is the authority for both the decision
and the extension.

WHICH SPELLING: the vendored programs that include these libraries overwhelmingly write
`-INCLUDE "NAME.INC"` -- 140 uppercase against 6 lowercase at the time of writing -- and the gimpel
basenames are already upper case. On a case-sensitive filesystem exactly one spelling resolves, so
the rule is: use the spelling an actual reference uses; where a file has references in both cases, or
none, fall back to the directory's prevailing case.

⛔ SCOPE IS PACKAGES AND include/ ONLY. tests/snobol4 has six include-headed files that belong to the
rungs suite's own fixtures; renaming those would move a denominator, which is a different decision
from restoring vendored upstream names, and it is not what Lon asked for.

Every rename is a `git mv` so history follows the file, and every `-INCLUDE "X.sno"` reference that
points at a renamed file is rewritten in the same run -- a rename without the references is a corpus
that builds nowhere.

Usage:  corpus_restore_inc_extension.py --dry-run | --apply   [--root CORPUS]

--root defaults to the seat's own corpus, $S4E_HOME/corpus (D-17: a tool never names another seat's
root), else the corpus beside this checkout of .github. The dry run prints its full counts and every
rename and every rewrite, never a sample (ceo CEO-1315).
"""
import argparse
import collections
import os
import re
import subprocess
import sys

HEADER = re.compile(r'^\*\s*(\S+)\.inc\b', re.I)
# EITHER QUOTE (coo COO-203): the SNOBOL4 rungs' `-INCLUDE 'FORTPUT.sno'` is single-quoted and resolves to include/FORTPUT.sno; a
# double-quote-only pattern left it naming a file this tool renames, which reds that rung suite entry.
REF = re.compile(r'''(-INCLUDE\s+(["']))(.+?)(\2)''', re.I)
REF_B = re.compile(rb'''(-INCLUDE\s+(["']))(.+?)(\2)''', re.I)
RECORD_EXT = (".tsv", ".txt", ".md", ".csv")
SCOPE = ("packages/", "include/")
SOURCE_EXT = (".sno", ".sbl")
INCLUDER_EXT = (".inc", ".INC")   # an include file already so named may itself include a renamed .sno; it is rewritten, never counted as a spelling vote


def is_include_file(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return bool(HEADER.match(fh.readline()))
    except OSError:
        return False


def collect(root):
    includes, sources, includers = [], [], []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        rel = os.path.relpath(dirpath, root)
        for fn in filenames:
            p = os.path.join(dirpath, fn)
            if os.path.islink(p):
                continue
            if fn.endswith(SOURCE_EXT):
                sources.append(p)
            if fn.endswith(INCLUDER_EXT):
                includers.append(p)
            if fn.endswith(".sno") and (rel + "/").startswith(SCOPE) and is_include_file(p):
                includes.append(p)
    return includes, sources, includers


def reference_spellings(sources):
    spellings = collections.defaultdict(collections.Counter)
    for p in sources:
        try:
            text = open(p, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for _, _, target, _ in REF.findall(text):
            name = target.strip().rsplit("/", 1)[-1]
            if "." not in name:
                continue
            base, ext = name.rsplit(".", 1)
            spellings[base][ext] += 1
    return spellings


def default_root():
    home = os.environ.get("S4E_HOME")
    if home:
        return os.path.join(home, "corpus")
    return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "corpus")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=default_root())
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if args.apply == args.dry_run:
        print("give exactly one of --apply or --dry-run", file=sys.stderr)
        return 2

    root = os.path.abspath(args.root)
    if not os.path.isdir(os.path.join(root, "packages")) or not os.path.isdir(os.path.join(root, "include")):
        print("REFUSED(2): %s is not a corpus (no packages/ and include/)" % root, file=sys.stderr)
        return 2
    print("root: %s" % root)
    includes, sources, includers = collect(root)
    spellings = reference_spellings(sources)
    print("include-headed files in scope: %d" % len(includes))

    renames = {}
    for p in includes:
        base = os.path.basename(p)[:-4]
        counts = spellings.get(base, collections.Counter())
        inc_cases = {e: n for e, n in counts.items() if e.lower() == "inc"}
        # One spelling in the references wins; both, or none, take the directory's case, as the docstring says (coo COO-203: the code took
        # the majority, so RANDOM's 6 "RANDOM.INC" against programs/'s 6 'RANDOM.inc' was decided by dict order once single quotes counted).
        if len(inc_cases) == 1:
            ext = next(iter(inc_cases))
        else:
            ext = "inc" if os.path.dirname(p).endswith("/include") else "INC"
        renames[p] = os.path.join(os.path.dirname(p), base + "." + ext)

    # A DESTINATION ALREADY OCCUPIED: a symlink that points at the very file being renamed is an alias of it (gimpel/SNOREAD.INC ->
    # SNOREAD.sno, corpus ef22d72a2, the name the snoflake program asks for) and collapses into the renamed file; anything else there
    # refuses the whole run before a byte moves.
    aliases, occupied = [], []
    for old, new in sorted(renames.items()):
        if os.path.islink(new) and os.path.realpath(new) == os.path.realpath(old):
            aliases.append(new)
        elif os.path.lexists(new):
            occupied.append(new)
    for a in aliases:
        print("alias collapses into its target: %s" % os.path.relpath(a, root))
    if occupied:
        for o in occupied:
            print("REFUSED(2): the destination %s exists and is not an alias of the file renamed onto it" % os.path.relpath(o, root), file=sys.stderr)
        return 2

    by_ext = collections.Counter(os.path.basename(v).rsplit(".", 1)[1] for v in renames.values())
    print("target extensions: %s" % dict(by_ext))

    # A REFERENCE IS REWRITTEN ONLY WHEN IT RESOLVES TO A RENAMED FILE, resolved as the SNOBOL4 lexer resolves it (src/driver/scrip.c):
    # the including file's own directory first, then SNO_LIB (the harness sets it to corpus/include). A basename match is not a
    # resolution: the rungs' `-INCLUDE "OR.sno"` and config/BLANKS.sno's "DIFF.sno" resolve to the copies beside them in
    # tests/snobol4/config, which keep their names, and include/PUT.sno and gimpel/PUT.sno take different spellings.
    unresolved = collections.Counter()

    def resolve(src, target):
        for d in (os.path.dirname(src), os.path.join(root, "include")):
            c = os.path.normpath(os.path.join(d, target))
            if os.path.isfile(c):
                return c
        return None

    # IN BINARY: a file is read and written as bytes, so its line endings and any byte that is not UTF-8 survive untouched and
    # `git diff --numstat` reads only the lines meant to change (the baton's own condition). Paths are decoded latin-1 to resolve.
    rewrites = []
    for p in sources + includers:
        try:
            raw = open(p, "rb").read()
        except OSError:
            continue

        def sub(m):
            target = m.group(3).decode("latin-1").strip()
            hit = resolve(p, target)
            if hit is None:
                if target.lower().endswith(".sno"):
                    unresolved[os.path.relpath(p, root) + " -> " + target] += 1
                return m.group(0)
            if hit not in renames:
                return m.group(0)
            name = target.rsplit("/", 1)[-1]
            new = target[: len(target) - len(name)] + os.path.basename(renames[hit])
            return m.group(1) + new.encode("latin-1") + m.group(4)

        changed = REF_B.sub(sub, raw)
        if changed != raw:
            rewrites.append((p, changed))

    # THE PACKAGE'S OWN RECORDS NAME A RENAMED FILE TOO: gimpel's UNGRADED.tsv, UNGRADABLE.tsv and EXCLUDED.tsv key a library by its
    # file name, and lib_inventory.sh and the EXCLUDED gate match that key against the shipped file -- a key left at NAME.sno names a
    # file that is gone. Every whole-token OLD name in a record file (.tsv .txt .md .csv) beside a renamed file is rewritten to its new
    # name; a token with a path or a word character on either side is left, and program source is never a record.
    records = []
    by_dir_map = collections.defaultdict(dict)
    for old, new in renames.items():
        by_dir_map[os.path.dirname(old)][os.path.basename(old)] = os.path.basename(new)
    for d, mp in sorted(by_dir_map.items()):
        tok = re.compile(rb"(?<![\w./-])(" + b"|".join(re.escape(k.encode()) for k in sorted(mp, key=len, reverse=True)) + rb")(?![\w])")
        for fn in sorted(os.listdir(d)):
            f = os.path.join(d, fn)
            if not fn.endswith(RECORD_EXT) or os.path.islink(f) or not os.path.isfile(f):
                continue
            raw = open(f, "rb").read()
            n = [0]

            def rec(m):
                n[0] += 1
                return mp[m.group(1).decode()].encode()

            changed = tok.sub(rec, raw)
            if changed != raw:
                records.append((f, changed, n[0]))
    if unresolved:
        print("-INCLUDE references to a .sno that resolve nowhere (left as written): %d" % len(unresolved))
        for k in sorted(unresolved):
            print("   unresolved %s" % k)
    print("files whose -INCLUDE references need rewriting: %d" % len(rewrites))
    print("record files naming a renamed file: %d (%d name(s))" % (len(records), sum(r[2] for r in records)))

    by_dir = collections.Counter(os.path.dirname(os.path.relpath(k, root)) for k in renames)
    print("renames by directory: %s" % ", ".join("%s=%d" % kv for kv in sorted(by_dir.items())))
    if args.dry_run:
        for k in sorted(renames):
            print("   would rename %s -> %s" % (os.path.relpath(k, root), os.path.basename(renames[k])))
        for p, _ in sorted(rewrites):
            print("   would rewrite refs in %s" % os.path.relpath(p, root))
        for f, _, n in records:
            print("   would rewrite record %s (%d name(s))" % (os.path.relpath(f, root), n))
        print("owed: %d rename(s), %d rewrite(s), %d record(s)" % (len(renames), len(rewrites), len(records)))
        return 0

    # the references first, at the paths they were read from, THEN the renames: a renamed library whose own references were rewritten
    # carries its rewritten text to its new name (renaming first and writing after would recreate every rewritten .sno beside its .INC)
    for p, data in rewrites:
        with open(p, "wb") as fh:
            fh.write(data)
    for f, data, _ in records:
        with open(f, "wb") as fh:
            fh.write(data)
    for a in aliases:
        subprocess.run(["git", "-C", root, "rm", "-q", os.path.relpath(a, root)], check=True)
    for old, new in sorted(renames.items()):
        subprocess.run(["git", "-C", root, "mv", os.path.relpath(old, root), os.path.relpath(new, root)], check=True)
    print("renamed %d file(s), rewrote references in %d file(s) and names in %d record(s)" % (len(renames), len(rewrites), len(records)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
