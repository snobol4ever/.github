#!/usr/bin/env python3
"""THE DOUBLE-SIDED BANNER (the cto, 2026-11-03 22:3x CST, first as /home/claude_cto/.claude/banner_compact.py; fleet-wide on Lon's word
2026-11-04: "In the display banner add a column for a delta/difference and distribute the new double-sided banner across the fleet.";
CEO-2129). The Stop hook pipes `s4e_msg.sh banner` through this filter: the suite grid's rows are laid out in TWO COLUMNS side by side,
half the suites on the left, half on the right, each cell `Lang Suite Pass/Tot Δ Pct S`, so the whole fleet score fits one screen without
a wrapped line (Lon's terminal wraps a long line; the full grid is 45 rows). Δ is util_suite_banner.py's delta column: Total minus Pass, how many failures remain
(Lon 2026-11-04: "The delta column represents how many failures remain."). S is the state in one
character: ✓ done, V void, ? no reading. The grid's header names the columns, so this filter reads them by NAME and renders an older
grid without Δ the same way (Δ blank). Lines before and after the grid pass through, cut to the banner's width. When no grid row is found
the input passes through untouched, so a refused or missing grid is never hidden."""
import sys

CELLW = 44
WIDTH = 2 * CELLW + 3
STATE = {"DONE": "✓", "VOID": "V", "NO READING": "?", "": ""}


def cut(s, w=WIDTH):
    return s if len(s) <= w else s[: w - 1] + "…"


def main():
    raw = sys.stdin.read()
    lines = raw.splitlines()
    head, rows, tail, seen_table, names = [], [], [], False, None
    for ln in lines:
        if ln.startswith("│"):
            cells = [c.strip() for c in ln.strip("│").split("│")]
            seen_table = True
            if cells and cells[0] == "Lang":
                names = cells
            elif names and len(cells) == len(names):
                rows.append(dict(zip(names, cells)))
            continue
        if ln[:1] in "┌├└":
            seen_table = True
            continue
        (tail if seen_table else head).append(ln)
    if not rows:
        sys.stdout.write(raw)
        return

    def fmt(r):
        st = r.get("State", "")
        s = f"{r.get('Lang',''):<8} {r.get('Suite',''):<12} {r.get('Pass',''):>4}/{r.get('Total',''):<4} {r.get('Δ',''):>5} {r.get('Pct',''):>4} {STATE.get(st, st[:1])}"
        return s[:CELLW].ljust(CELLW)

    half = (len(rows) + 1) // 2
    left, right = rows[:half], rows[half:]
    out = [cut(h) for h in head if h.strip()]
    hdr = f"{'Lang':<8} {'Suite':<12} {'Pass/Tot':<9} {'Δ':>5} {'Pct':>4} S".ljust(CELLW)
    out.append(hdr + " │ " + hdr)
    for i in range(half):
        l = fmt(left[i])
        r = fmt(right[i]) if i < len(right) else ""
        out.append((l + " │ " + r).rstrip())
    out += [cut(t) for t in tail if t.strip()]
    sys.stdout.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
