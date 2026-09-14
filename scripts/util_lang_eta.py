#!/usr/bin/env python3
"""⛔⭐ ETA TO 100% PER LANGUAGE, FROM GIT HISTORY (Lon 2026-09-13: "report the estimated time of
arrival for a 100% for each language. You calculate the rate of progress versus the total." then
"pull per time that file from github and create the extra dimension that way."; ceo CEO-721).

THE EXTRA DIMENSION IS TIME, AND GIT ALREADY HAD IT. SUITES.tsv is versioned in .github, so every
commit that touched it is a DATED SNAPSHOT carrying both today_pass AND today_total per suite --
263 of them at this writing, back to 2026-09-06. Replaying them gives a real series instead of the
two points (first, today) the live file holds.

⛔⛔ WHY BOTH COLUMNS MATTER AND A PASS-ONLY RATE WOULD LIE. Denominators MOVE, hugely and in both
directions: prolog 1025 -> 7554 as Logtalk was vendored, pascal 859 -> 854 as two criterion events
made previously-passing tests grade honestly. A rate that watched only `pass` would read the
Logtalk import as a burst of cures and the Pascal honesty as a regression. So every window reports
whether its TOTAL moved, and an ETA computed across a moved denominator is labelled, never hidden.

REFUSALS, because a projection that cannot be trusted should say so rather than print a date:
  DONE      -- gap is zero.
  STUCK     -- pass rate <= 0 across the window.
  NOISY     -- fewer than 3 distinct snapshot days in the window.
  ⚠ DENOM   -- the denominator moved during the window; the ETA is printed but is a projection
               over a target that is itself moving, which is a different and weaker claim.
⛔ AND ALL OF THEM ARE PROJECTIONS, NOT COMMITMENTS: a rate is what happened, not what will.
"""
import subprocess, csv, collections, datetime as dt, os, sys

WINDOW = int(os.environ.get("ETA_WINDOW_DAYS", "4"))
HERE = os.path.dirname(os.path.abspath(__file__))

def snapshots():
    out = subprocess.run(["git", "-C", HERE + "/..", "log", "--format=%H %ad",
                          "--date=format:%Y-%m-%dT%H:%M", "--reverse", "--", "SUITES.tsv"],
                         capture_output=True, text=True).stdout.strip().split("\n")
    for line in out:
        if " " not in line: continue
        sha, when = line.split(" ", 1)
        txt = subprocess.run(["git", "-C", HERE + "/..", "show", f"{sha}:SUITES.tsv"],
                             capture_output=True, text=True).stdout
        if not txt: continue
        p = collections.Counter(); t = collections.Counter()
        for r in csv.DictReader((l for l in txt.split("\n") if not l.startswith("#")), delimiter="\t"):
            if not r.get("today_pass"): continue
            try: p[r["lang"]] += int(r["today_pass"]); t[r["lang"]] += int(r["today_total"])
            except (ValueError, KeyError): pass
        yield when, p, t

def main():
    snaps = list(snapshots())
    if not snaps: print("⛔ REFUSE(2): no SUITES.tsv history"); return 2
    today = dt.date.today(); cut = (today - dt.timedelta(days=WINDOW)).isoformat()
    langs = sorted({l for _, p, _ in snaps for l in p})
    F = "%-9s %6s %7s %7s %9s %7s  %s"
    print(F % ("LANG", "PASS", "TOTAL", "GAP", "RATE/DAY", "DENOM", "ETA TO 100%"))
    print("-" * 74)
    for lg in langs:
        pts = [(w, p[lg], t[lg]) for w, p, t in snaps if lg in p]
        if not pts: continue
        w1, p1, t1 = pts[-1]; gap = t1 - p1
        win = [x for x in pts if x[0][:10] >= cut] or pts[-2:]
        w0, p0, t0 = win[0]
        dmoved = "moved" if t0 != t1 else "held"
        if gap <= 0:
            print(F % (lg, p1, t1, 0, "-", dmoved, "DONE")); continue
        ddays = len({x[0][:10] for x in win})
        span = max((dt.date.fromisoformat(w1[:10]) - dt.date.fromisoformat(w0[:10])).days, 1)
        rate = (p1 - p0) / span
        if ddays < 3: verdict = "NOISY (<3 snapshot days)"
        elif rate <= 0: verdict = "STUCK (no forward rate)"
        else:
            d = gap / rate
            verdict = ("⚠ " if dmoved == "moved" else "") + \
                      f"{d:.0f}d -> {(today + dt.timedelta(days=round(d))).isoformat()}"
        print(F % (lg, p1, t1, -gap, f"{rate:+.1f}", dmoved, verdict))
    print("-" * 74)
    print(f"{len(snaps)} snapshots of SUITES.tsv from git; window {WINDOW}d.")
    print("⛔ PROJECTIONS, NOT COMMITMENTS. ⚠ = denominator moved in the window.")
    return 0
sys.exit(main())
