#!/usr/bin/env python3
"""util_progress_flips.py -- THE TIME-BASED QUERIES OVER THE PROGRESS DATABASE (Lon 2026-09-06: "how many programs have
flipped green per hour?" · "Are you tracking every single package test suite and benchmark program individually?" ·
"You should have a list of every program and when it began working and its current status as to known problems.").

The table: /home/resources/progress/results.tsv (writer: SCRIP/scripts/util_progress_append.py; contract in its docstring).

  util_progress_flips.py [--since 3d|12h] [--per hour|day|10m] [--mode m3|m4|ast|any] [--class master|package|benchmark]
                         [--suite KEY] [--live-only] [--names]
        the flip histogram: per bucket, programs that went not-PASS -> PASS (+) and PASS -> not-PASS (-), from
        consecutive readings of the same (suite, program, mode). Zero rows in a window prints "no rows recorded", never 0 flips.
  util_progress_flips.py --coverage
        every suite of .github/SUITES.tsv (and every benchmark suite seen): rows, programs seen / suite total, live vs
        replay rows, last row's age -- the answer to "are we tracking everything?", MISSING named as MISSING.
  util_progress_flips.py --register [--out FILE] [--problems] [--program NAME]
        THE PROGRAM REGISTER: one line per (suite, program): status, when it first passed (began working), when it was
        last seen, its outcome per mode, and -- with --problems -- the queue rows that name it (known problems).
"""
import sys, csv, argparse, collections, datetime, os, re, glob, io

HERE = os.path.dirname(os.path.abspath(__file__))
SUITES_TSV = os.path.join(HERE, "..", "SUITES.tsv")
PO = "/home/resources/postoffice"
MASTER_KEYS = {"snobol4-master": "sno-master", "icon-master": "icn-master", "prolog-master": "pl-master", "pascal-master": "pas-master",
               "raku-master": "raku-master", "snocone-master": "snc-master", "rebus-master": "reb-master"}
REPLAY = "ceo-replay"
NOT_A_READING = ("REFUSE", "SKIP", "MISSING", "UNGRADED")  # the run did not measure the program: never a flip, never "the previous reading", never a status


def parse_since(s):
    m = re.fullmatch(r"(\d+)([dhm])", s.strip())
    if not m:
        raise SystemExit(f"--since wants <n>d, <n>h or <n>m, got {s!r}")
    n, u = int(m.group(1)), m.group(2)
    delta = datetime.timedelta(days=n) if u == "d" else datetime.timedelta(hours=n) if u == "h" else datetime.timedelta(minutes=n)
    return (datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) - delta).strftime("%Y-%m-%dT%H:%M:%S")


def load(db):
    if not os.path.isfile(db):
        raise SystemExit(f"REFUSE(2): no progress database at {db}")
    rows = []
    with open(db, encoding="utf-8", errors="replace", newline="") as f:
        rd = csv.DictReader(f, delimiter="\t")
        for r in rd:
            if not r.get("ts_utc") or not r.get("program"):
                continue
            r["note"] = r.get("note") or ""
            r["measurer"] = r.get("measurer") or ""
            rows.append(r)
    rows.sort(key=lambda r: r["ts_utc"])
    return rows


def bucket_of(ts, per):
    if per == "hour":
        return ts[:13]
    if per == "day":
        return ts[:10]
    if per == "10m":
        return ts[:15] + "0"
    raise SystemExit(f"--per wants hour, day or 10m, got {per!r}")


def age_str(ts):
    try:
        t = datetime.datetime.strptime(ts[:19], "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        return "?"
    d = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) - t
    m = int(d.total_seconds() // 60)
    return f"{m}m" if m < 120 else f"{m // 60}h" if m < 48 * 60 else f"{m // 1440}d"


def cmd_flips(a, rows):
    since = parse_since(a.since)
    sel = [r for r in rows if (a.mode == "any" or r["mode"] == a.mode) and (a.klass == "all" or r["class"] == a.klass)
           and (not a.suite or r["suite"] == a.suite) and (not a.live_only or r["measurer"] != REPLAY)]
    last = {}
    ups = collections.defaultdict(list)
    downs = collections.defaultdict(list)
    in_window = 0
    for r in sel:
        k = (r["suite"], r["program"], r["mode"])
        if r["ts_utc"] >= since:
            in_window += 1
        if r["outcome"] in NOT_A_READING:
            continue
        prev = last.get(k)
        last[k] = r
        if r["ts_utc"] < since or prev is None:
            continue
        b = bucket_of(r["ts_utc"], a.per)
        if prev["outcome"] != "PASS" and r["outcome"] == "PASS":
            ups[(b, r["class"])].append(f'{r["suite"]}:{r["program"]}:{r["mode"]}')
        if prev["outcome"] == "PASS" and r["outcome"] != "PASS":
            downs[(b, r["class"])].append(f'{r["suite"]}:{r["program"]}:{r["mode"]}')
    print(f"bucket({a.per}, UTC)   master +/-   package +/-   bench +/-   (mode {a.mode}; class {a.klass}; rows {len(sel)}; since {since}{'; live only' if a.live_only else ''})")
    if in_window == 0:
        newest = sel[-1]["ts_utc"] if sel else "none"
        print(f"  NO ROWS RECORDED in the window -- the newest matching row is {newest} ({age_str(newest) if sel else '-'} old). This is a recording gap, not zero flips.")
    buckets = sorted({b for b, _ in list(ups) + list(downs)})
    tm = tp = tb = 0
    for b in buckets:
        mu, md = len(ups[(b, "master")]), len(downs[(b, "master")])
        pu, pd = len(ups[(b, "package")]), len(downs[(b, "package")])
        bu, bd = len(ups[(b, "benchmark")]), len(downs[(b, "benchmark")])
        tm += mu; tp += pu; tb += bu
        print(f"{b:20s} {mu:5d}/{md:<4d}   {pu:5d}/{pd:<4d}   {bu:4d}/{bd:<4d}  " + ("#" * min(mu + pu + bu, 60)))
        if a.names:
            for k in ((b, "master"), (b, "package"), (b, "benchmark")):
                for x in ups[k]:
                    print("    +", x)
                for x in downs[k]:
                    print("    -", x)
    print(f"TOTAL newly-passing in window: master {tm}, package {tp}, benchmark {tb}  (rows in window: {in_window})")
    return 0


def read_suites_tsv():
    out = []
    if not os.path.isfile(SUITES_TSV):
        return out
    with open(SUITES_TSV, encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.rstrip("\n").split("\t")
            if parts[0] == "key":
                hdr = parts
                continue
            d = dict(zip(hdr, parts))
            out.append(d)
    return out


def cmd_coverage(a, rows):
    by = collections.defaultdict(lambda: {"rows": 0, "live": 0, "programs": set(), "last": "", "modes": set(), "class": ""})
    for r in rows:
        b = by[r["suite"]]
        b["rows"] += 1
        b["live"] += (r["measurer"] != REPLAY)
        b["programs"].add(r["program"])
        b["modes"].add(r["mode"])
        b["class"] = r["class"]
        if r["ts_utc"] > b["last"]:
            b["last"] = r["ts_utc"]
    suites = read_suites_tsv()
    inv = {v: k for k, v in MASTER_KEYS.items()}
    print(f"{'suite (SUITES.tsv key)':24s} {'nick':8s} {'db suite':16s} {'rows':>6s} {'live':>6s} {'programs':>12s} {'modes':8s} {'last row (UTC)':20s} age")
    missing = []
    seen = set()
    for s in suites:
        key = s["key"]
        dbk = inv.get(key, key)
        seen.add(dbk)
        b = by.get(dbk)
        total = s.get("today_total", "?")
        if not b:
            missing.append(f"{key} ({s.get('nick', '')}, {total} programs in the table)")
            print(f"{key:24s} {s.get('nick', ''):8s} {dbk:16s} {0:6d} {0:6d} {'0/' + str(total):>12s} {'-':8s} {'-':20s} MISSING")
            continue
        print(f"{key:24s} {s.get('nick', ''):8s} {dbk:16s} {b['rows']:6d} {b['live']:6d} {str(len(b['programs'])) + '/' + str(total):>12s} {','.join(sorted(b['modes'])):8s} {b['last']:20s} {age_str(b['last'])}")
    extra = [k for k in by if k not in seen]
    for k in sorted(extra):
        b = by[k]
        print(f"{'(not in SUITES.tsv)':24s} {'':8s} {k:16s} {b['rows']:6d} {b['live']:6d} {len(b['programs']):>12d} {','.join(sorted(b['modes'])):8s} {b['last']:20s} {age_str(b['last'])}  class={b['class']}")
    live_total = sum(b["live"] for b in by.values())
    print(f"SUMMARY: {len(suites) - len(missing)} of {len(suites)} table suites have rows; {len(missing)} MISSING; live (non-replay) rows {live_total} of {len(rows)}; benchmark suites seen: {sorted(k for k, b in by.items() if b['class'] == 'benchmark') or 'NONE'}")
    for m in missing:
        print("  MISSING:", m)
    return 0


def problems_index(programs):
    """program -> [queue rows / task files naming it]. One pass over the postoffice; exact-token match."""
    idx = collections.defaultdict(set)
    names = sorted(programs, key=len, reverse=True)
    pat = re.compile(r"(?<![A-Za-z0-9_])(" + "|".join(re.escape(n) for n in names if len(n) >= 4) + r")(?![A-Za-z0-9_])") if names else None
    if pat is None:
        return idx
    for f in glob.glob(os.path.join(PO, "tasks", "*.task.md")):
        topic = os.path.basename(f)[:-len(".task.md")]
        try:
            txt = io.open(f, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for m in set(pat.findall(txt)):
            idx[m].add(topic)
    states = {}
    try:
        for line in io.open(os.path.join(PO, "QUEUE.tsv"), encoding="utf-8", errors="replace"):
            p = line.rstrip("\n").split("\t")
            if len(p) >= 4 and not line.startswith("#"):
                states[p[1]] = p[3]
    except OSError:
        pass
    return {k: sorted(f"{t}[{states.get(t, 'done/retired')}]" for t in v) for k, v in idx.items()}


def cmd_register(a, rows):
    per = collections.defaultdict(lambda: {"class": "", "lang": "", "modes": collections.defaultdict(dict), "first_pass": "", "last": "", "ever_pass": False, "was_pass_then_broke": ""})
    for r in rows:
        if a.program and r["program"] != a.program:
            continue
        if a.suite and r["suite"] != a.suite:
            continue
        k = (r["suite"], r["program"])
        e = per[k]
        e["class"], e["lang"] = r["class"], r["lang"]
        e["last"] = max(e["last"], r["ts_utc"])
        if r["outcome"] in NOT_A_READING:
            e.setdefault("unmeasured", set()).add(r["mode"])
            continue
        md = e["modes"][r["mode"]]
        prev = md.get("outcome")
        md["outcome"], md["ts"], md["measurer"] = r["outcome"], r["ts_utc"], r["measurer"]
        if r["outcome"] == "PASS":
            e["ever_pass"] = True
            if not e["first_pass"] or r["ts_utc"] < e["first_pass"]:
                e["first_pass"] = r["ts_utc"]
            if not md.get("first_pass"):
                md["first_pass"] = r["ts_utc"]
        if prev == "PASS" and r["outcome"] != "PASS":
            md["broke"] = r["ts_utc"]
    probs = problems_index({p for _, p in per}) if a.problems else {}
    out = io.StringIO()
    w = csv.writer(out, delimiter="\t", lineterminator="\n")
    w.writerow(["suite", "program", "class", "lang", "status", "began_working_utc", "last_seen_utc", "m3", "m4", "ast", "last_measurer", "known_problems"])
    counts = collections.Counter()
    for (suite, prog), e in sorted(per.items()):
        modes = e["modes"]
        graded = {m: d["outcome"] for m, d in modes.items()}
        passing = [m for m, o in graded.items() if o == "PASS"]
        if graded and len(passing) == len(graded):
            status = "WORKING"
        elif passing:
            status = "PARTIAL(" + ",".join(sorted(passing)) + ")"
        elif e["ever_pass"]:
            status = "REGRESSED"
        elif not graded:
            status = "UNGRADED"
        else:
            status = "NEVER-PASSED"
        counts[status.split("(")[0]] += 1
        last_meas = max(modes.values(), key=lambda d: d["ts"])["measurer"] if modes else ""
        w.writerow([suite, prog, e["class"], e["lang"], status, e["first_pass"] or "-", e["last"], graded.get("m3", "-"), graded.get("m4", "-"), graded.get("ast", "-"), last_meas, "; ".join(probs.get(prog, [])) if a.problems else ""])
    text = out.getvalue()
    if a.out:
        with open(a.out, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        print(f"register: {len(per)} programs -> {a.out}  " + "  ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    else:
        sys.stdout.write(text)
        print("# " + "  ".join(f"{k}={v}" for k, v in sorted(counts.items())) + f"  programs={len(per)}", file=sys.stderr)
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", default=os.environ.get("S4E_PROGRESS_DB") or "/home/resources/progress/results.tsv")
    ap.add_argument("--since", default="3d")
    ap.add_argument("--per", default="hour")
    ap.add_argument("--mode", default="m3")
    ap.add_argument("--class", dest="klass", default="all")
    ap.add_argument("--suite", default="")
    ap.add_argument("--live-only", action="store_true")
    ap.add_argument("--names", action="store_true")
    ap.add_argument("--coverage", action="store_true")
    ap.add_argument("--register", action="store_true")
    ap.add_argument("--problems", action="store_true", help="with --register: name the queue rows / task files that mention each program (one pass over the postoffice)")
    ap.add_argument("--program", default="", help="with --register: one program")
    ap.add_argument("--out", default="", help="with --register: write the TSV here instead of stdout")
    a = ap.parse_args()
    rows = load(a.db)
    if a.coverage:
        return cmd_coverage(a, rows)
    if a.register or a.program:
        a.register = True
        return cmd_register(a, rows)
    return cmd_flips(a, rows)


if __name__ == "__main__":
    sys.exit(main())
