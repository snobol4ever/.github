#!/usr/bin/env python3
"""⛔⭐ REMOVE THE `modes=ast` ENTRIES FROM A MASTER (Lon 2026-09-13: "Remove those bogus AST
tests."; CEO-702/703).

WHY THEY GO: `run_ast` runs `scrip --dump-ast` and diffs the dump as text. It NEVER EXECUTES
the program, and the ref is our OWN dump format -- no oracle produces one -- so the ref was
necessarily cut from our own output, which the standing law forbids. Such an entry CANNOT
DETECT A WRONG PARSE: whatever we parse becomes correct by definition.

⛔ IDENTITY-ANCHORED, NEVER POSITIONAL (§ THE INSTRUMENT LAWS): a block runs from its banner
line -- which carries `<rank> <entry>` after a rule of dashes -- to the line before the next
banner, and blocks are selected BY ENTRY NAME read from ALL.csv, never by rank or offset.
Ranks are left exactly as they are: this drops entries, it does not renumber a population
(hq_T's 2026-09-12 finding -- a moved population blinds every instrument derived from it).

Writes ALL.<ext>, ALL.ref and ALL.csv in BINARY with LF, changing only the bytes it means to.
"""
import csv, io, os, re, sys, argparse

EXT = {"snobol4": ".sno", "icon": ".icn", "prolog": ".pl", "raku": ".raku",
       "snocone": ".sc", "rebus": ".reb", "pascal": ".pas"}

def banner_entry(line, names):
    if "---" not in line:
        return None
    for n in names:
        if re.search(r"(?<![\w.])" + re.escape(n) + r"(?![\w.])", line):
            return n
    return None

def split_blocks(text, names):
    lines = text.split("\n")
    blocks, cur, cur_name = [], [], None
    for ln in lines:
        e = banner_entry(ln, names) if "---" in ln else None
        is_banner = e is not None or ("---" in ln and re.search(r"-{5,}", ln) and re.search(r"\s\d+\s+\S+", ln))
        if is_banner:
            blocks.append((cur_name, cur)); cur, cur_name = [ln], e
        else:
            cur.append(ln)
    blocks.append((cur_name, cur))
    # ⛔ THE FIRST BLOCK IS THE PREAMBLE AND IS EMPTY WHEN THE FILE OPENS ON A BANNER. Keeping
    # it emits a spurious leading newline -- ONE CHARACTER, which shifted seven masters and
    # killed extraction in all of them (CEO-703, reverted). Dropped here, and the round-trip
    # assertion below is what makes that provable instead of hoped.
    if blocks and blocks[0][0] is None and blocks[0][1] == []:
        blocks = blocks[1:]
    return blocks

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", required=True)
    ap.add_argument("--root", default=os.path.expanduser("~/../claude_ceo/corpus/tests"))
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    d = os.path.join(a.root, a.lang)
    csv_p = os.path.join(d, "ALL.csv")
    with open(csv_p, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f)); f.seek(0); fields = next(csv.reader(f))
    drop = {r["entry"] for r in rows if (r.get("modes") or "").strip() == "ast"}
    if not drop:
        print(f"{a.lang}: no ast entries"); return 0
    print(f"{a.lang}: {len(drop)} ast entries to drop, of {len(rows)} declared")
    for name, path in (("container", os.path.join(d, "ALL" + EXT[a.lang])),
                       ("ref", os.path.join(d, "ALL.ref"))):
        if not os.path.exists(path):
            print(f"  ⛔ REFUSE(2): missing {path}"); return 2
        raw = open(path, "rb").read().decode("utf-8", "surrogateescape")
        blocks = split_blocks(raw, drop)
        # ⛔⭐ THE PRECONDITION, AND IT IS NOT OPTIONAL: REASSEMBLING EVERY BLOCK MUST REPRODUCE
        # THE FILE BYTE FOR BYTE BEFORE ANY BLOCK IS DROPPED. A transformer that has not been
        # proven identity-preserving on a no-op has no business removing anything -- this is
        # the instrument law (fail once AND pass once) applied to a rewriter rather than a gate.
        rt = "\n".join("\n".join(b[1]) for b in blocks)
        if rt != raw:
            print(f"  ⛔ REFUSE(2): {name} does not round-trip ({len(raw)} -> {len(rt)} chars); "
                  f"the splitter does not model this file and nothing is written"); return 2
        keep = [b for b in blocks if b[0] not in drop]
        removed = len(blocks) - len(keep)
        print(f"  {name}: {len(blocks)} blocks -> {len(keep)} ({removed} removed)")
        if removed != len(drop):
            print(f"  ⛔ REFUSE(2): removed {removed} but ALL.csv declares {len(drop)} -- "
                  f"identity match is incomplete; nothing written"); return 2
        if a.write:
            out = "\n".join("\n".join(b[1]) for b in keep)
            open(path, "wb").write(out.encode("utf-8", "surrogateescape"))
    if a.write:
        buf = io.StringIO()
        w = csv.DictWriter(buf, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        for r in rows:
            if r["entry"] not in drop: w.writerow(r)
        open(csv_p, "wb").write(buf.getvalue().encode("utf-8"))
        print(f"  ALL.csv: {len(rows)} -> {len(rows)-len(drop)} rows")
    return 0

sys.exit(main())
