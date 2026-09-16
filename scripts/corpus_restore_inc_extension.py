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
master suite's own fixtures; renaming those would move a denominator, which is a different decision
from restoring vendored upstream names, and it is not what Lon asked for.

Every rename is a `git mv` so history follows the file, and every `-INCLUDE "X.sno"` reference that
points at a renamed file is rewritten in the same run -- a rename without the references is a corpus
that builds nowhere.

Usage:  corpus_restore_inc_extension.py --dry-run | --apply   [--root /home/claude_ceo/corpus]
"""
import argparse
import collections
import os
import re
import subprocess
import sys

HEADER = re.compile(r'^\*\s*(\S+)\.inc\b', re.I)
REF = re.compile(r'(-INCLUDE\s+")([^"]+)(")', re.I)
SCOPE = ("packages/", "include/")
SOURCE_EXT = (".sno", ".sbl")


def is_include_file(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return bool(HEADER.match(fh.readline()))
    except OSError:
        return False


def collect(root):
    includes, sources = [], []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        rel = os.path.relpath(dirpath, root)
        for fn in filenames:
            p = os.path.join(dirpath, fn)
            if fn.endswith(SOURCE_EXT):
                sources.append(p)
            if fn.endswith(".sno") and (rel + "/").startswith(SCOPE) and is_include_file(p):
                includes.append(p)
    return includes, sources


def reference_spellings(sources):
    spellings = collections.defaultdict(collections.Counter)
    for p in sources:
        try:
            text = open(p, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for _, target, _ in REF.findall(text):
            name = target.strip().rsplit("/", 1)[-1]
            if "." not in name:
                continue
            base, ext = name.rsplit(".", 1)
            spellings[base][ext] += 1
    return spellings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="/home/claude_ceo/corpus")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if args.apply == args.dry_run:
        print("give exactly one of --apply or --dry-run", file=sys.stderr)
        return 2

    root = os.path.abspath(args.root)
    includes, sources = collect(root)
    spellings = reference_spellings(sources)
    print("include-headed files in scope: %d" % len(includes))

    renames = {}
    for p in includes:
        base = os.path.basename(p)[:-4]
        counts = spellings.get(base, collections.Counter())
        inc_cases = {e: n for e, n in counts.items() if e.lower() == "inc"}
        if inc_cases:
            ext = max(inc_cases, key=inc_cases.get)
        else:
            ext = "inc" if os.path.dirname(p).endswith("/include") else "INC"
        renames[p] = os.path.join(os.path.dirname(p), base + "." + ext)

    by_ext = collections.Counter(os.path.basename(v).rsplit(".", 1)[1] for v in renames.values())
    print("target extensions: %s" % dict(by_ext))

    old_names = {os.path.basename(k) for k in renames}
    rewrites = []
    for p in sources:
        try:
            text = open(p, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        changed = text
        for _, target, _ in REF.findall(text):
            name = target.strip().rsplit("/", 1)[-1]
            if name in old_names:
                new = os.path.basename(renames[[k for k in renames if os.path.basename(k) == name][0]])
                changed = changed.replace('"%s"' % target, '"%s"' % target.replace(name, new))
        if changed != text:
            rewrites.append((p, changed))
    print("files whose -INCLUDE references need rewriting: %d" % len(rewrites))

    if args.dry_run:
        for k in sorted(renames)[:8]:
            print("   would rename %s -> %s" % (os.path.relpath(k, root), os.path.basename(renames[k])))
        for p, _ in rewrites[:8]:
            print("   would rewrite refs in %s" % os.path.relpath(p, root))
        return 0

    for old, new in sorted(renames.items()):
        subprocess.run(["git", "-C", root, "mv", os.path.relpath(old, root), os.path.relpath(new, root)], check=True)
    for p, text in rewrites:
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
    print("renamed %d file(s), rewrote references in %d file(s)" % (len(renames), len(rewrites)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
