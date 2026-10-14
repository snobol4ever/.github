#!/usr/bin/env python3
"""util_relay_trigger.py -- WHEN TO START THE RELAY (ceo, CEO-1711, 2026-10-14).

Lon, in-chat to the ceo, verbatim: "You should delegate a baton in certain circumstances as you just did. Maybe a check for
something over a threshold and then kick in the RELAY-RACE build idea."

THE RELAY (CEO-1709): a set of seats passes a BATON -- the right to push to SCRIP main -- in a fixed order, one landing per leg,
at most 10 minutes a leg, "BATON to <next>: landed <hash> <what>" by instant message to the next seat and the ceo; a seat that is
not ready passes at once. It removes push races among the seats it holds and staggers their push-time rebuilds.

THIS INSTRUMENT measures, read-only, the three conditions under which the relay pays for itself, and prints one verdict line:
  VELOCITY   SCRIP commits on origin/main in the last 15 minutes (committer date, so a rebased commit counts at its push)
             -- ON at VELOCITY_ON or more. Calibration 2026-10-14: about 25 an hour (6 per 15 min) in steady work; 16 in the
             18 minutes after the STEP B hold lifted.
  PRESSURE   rebases against commits in the last 60 minutes, read from every seat root's own reflog -- ON when the fleet ratio
             reaches RATIO_ON over at least PRESSURE_MIN_COMMITS commits (CEO-1727: at 16:39 a 9-for-6 catch-up after the
             usage-limit pause read 1.50 at a velocity of 2 -- a ratio over a handful of commits is noise), or when one seat is in a REBASE LOOP: LOOP_REBASES or more rebases and LOOP_RATIO or more
             rebases per commit (Lon 13:4x, verbatim: "Keep an EYE on CPU speed and REBASE-CYCLE loops out of hand.").
             Calibration: 83 rebases for 69 commits (1.2) across the fleet from 11:15 to 13:2x; hq_collector lost two races
             outright landing STEP B.
  LOAD       load1 and load5 against the core count -- ON at LOAD1_ON x cores with load5 at LOAD5_ON x cores (a sustained
             rebuild herd, not a spike). Calibration: 45 -> 56 on 16 cores when twelve seats rebuilt at once.
REJECTS a seat whose push is rejected runs SCRIP scripts/s4e_push_rejected.sh, one line into $PO/PUSH_REJECTED.tsv (Lon
             13:4x, verbatim: "So maybe seats just report REJECTED pushes?") -- ON at REJECT_SEAT_ON lost races for one seat
             or REJECT_FLEET_ON for the fleet in 60 minutes: a lost race is the one thing a reflog cannot show.
  CPU     every reading prints the MEASURED clock (cpuinfo_avg_freq, the hardware's own average) against its maximum, the
             platform profile and the energy preference, and WARNs when the clock sags under CPU_SLOW_MHZ with load at or over the
             core count (calibration: 2295 MHz of 5135 at load 18 on 2026-10-14 13:4x, profile balanced -- the power limit).
Any one ON prints RELAY: ON with its reasons and the CONTENDING seats (most rebases first), the ceo's candidates for the
relay order; otherwise RELAY: OFF. Exit 1 ON, 0 OFF, 2 could-not-measure (no origin read, or no seat root readable).
The thresholds take RELAY_VELOCITY_ON, RELAY_RATIO_ON, RELAY_PRESSURE_MIN_COMMITS, RELAY_LOOP_REBASES, RELAY_LOOP_RATIO, RELAY_CPU_SLOW_MHZ, RELAY_REJECT_SEAT_ON, RELAY_REJECT_FLEET_ON, RELAY_LOAD1_ON and RELAY_LOAD5_ON
from the environment -- the instrument's own switch, for proving both arms (CEO-1680). It changes nothing and runs nothing but git reads and /proc/loadavg; the ceo runs it in THE CEO LOOP, starts the relay on ON,
and ends it after two OFF readings in a row.
"""
import calendar, os, re, subprocess, sys, time

VELOCITY_ON = int(os.environ.get("RELAY_VELOCITY_ON", "10"))
RATIO_ON = float(os.environ.get("RELAY_RATIO_ON", "1.5"))
PRESSURE_MIN_COMMITS = int(os.environ.get("RELAY_PRESSURE_MIN_COMMITS", "15"))
LOOP_REBASES = int(os.environ.get("RELAY_LOOP_REBASES", "3"))
LOOP_RATIO = float(os.environ.get("RELAY_LOOP_RATIO", "2.5"))
CPU_SLOW_MHZ = float(os.environ.get("RELAY_CPU_SLOW_MHZ", "2000"))
REJECT_SEAT_ON = int(os.environ.get("RELAY_REJECT_SEAT_ON", "2"))
REJECT_FLEET_ON = int(os.environ.get("RELAY_REJECT_FLEET_ON", "4"))
PO = os.environ.get("S4E_POSTOFFICE", "/home/resources/postoffice")
LOAD1_ON = float(os.environ.get("RELAY_LOAD1_ON", "2.0"))
LOAD5_ON = float(os.environ.get("RELAY_LOAD5_ON", "1.5"))
SEATS = ["ceo", "cto", "cfo", "coo", "icon", "prolog", "pascal", "snocone", "snobol4", "raku", "templates", "runtime",
         "collector", "zetas"]
HOME = os.environ.get("S4E_HOME", "/home/claude_ceo")


def git(args, root):
    try:
        r = subprocess.run(["git", "-C", root] + args, capture_output=True, text=True, timeout=60)
    except Exception:
        return None
    return r.stdout if r.returncode == 0 else None


def main():
    now = time.time()
    scrip = os.path.join(HOME, "SCRIP")
    git(["fetch", "-q", "origin"], scrip)
    log = git(["log", "--since=15 minutes ago", "--format=%h", "origin/main"], scrip)
    if log is None:
        print("REFUSE(2): could not read origin/main in %s -- nothing measured" % scrip)
        return 2
    velocity = len([l for l in log.splitlines() if l.strip()])
    per = {}
    for s in SEATS:
        out = git(["reflog", "-n", "600", "--date=unix", "--format=%gd\t%gs"], "/home/claude_%s/SCRIP" % s)
        if out is None:
            continue
        rb = c = 0
        for line in out.splitlines():
            m = re.match(r"HEAD@\{(\d+)\}\t(.*)", line)
            if not m or int(m.group(1)) < now - 3600:
                continue
            msg = m.group(2)
            if re.search(r"rebase.*\(finish\)", msg):
                rb += 1
            elif re.match(r"commit( \(amend\))?:", msg):
                c += 1
        per[s] = (rb, c)
    if not per:
        print("REFUSE(2): no seat root's reflog was readable -- nothing measured")
        return 2
    rejected = {}
    try:
        for line in open(os.path.join(PO, "PUSH_REJECTED.tsv"), encoding="utf-8", errors="replace"):
            f = line.rstrip("\n").split("\t")
            if len(f) < 2:
                continue
            try:
                t = calendar.timegm(time.strptime(f[0], "%Y-%m-%dT%H:%M:%SZ"))
            except Exception:
                continue
            if t >= now - 3600:
                rejected[f[1]] = rejected.get(f[1], 0) + 1
    except FileNotFoundError:
        pass
    rej_all = sum(rejected.values())
    rb_all = sum(v[0] for v in per.values())
    c_all = sum(v[1] for v in per.values())
    ratio = (rb_all / c_all) if c_all else (float(rb_all) if rb_all else 0.0)
    loops = sorted([s for s, (rb, c) in per.items() if rb >= LOOP_REBASES and rb >= LOOP_RATIO * max(c, 1)])
    try:
        l1, l5 = [float(x) for x in open("/proc/loadavg").read().split()[:2]]
    except Exception:
        l1 = l5 = 0.0
    cores = os.cpu_count() or 1
    mhz = []
    for i in range(cores):
        try:
            mhz.append(int(open("/sys/devices/system/cpu/cpu%d/cpufreq/cpuinfo_avg_freq" % i).read()) / 1000.0)
        except Exception:
            pass
    avg_mhz = sum(mhz) / len(mhz) if mhz else 0.0
    try:
        max_mhz = int(open("/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq").read()) / 1000.0
    except Exception:
        max_mhz = 0.0
    def rd(f):
        try:
            return open(f).read().strip()
        except Exception:
            return "?"
    profile = rd("/sys/firmware/acpi/platform_profile"); epp = rd("/sys/devices/system/cpu/cpu0/cpufreq/energy_performance_preference")
    reasons = []
    if velocity >= VELOCITY_ON:
        reasons.append("VELOCITY %d SCRIP commits in 15 min >= %d" % (velocity, VELOCITY_ON))
    if c_all >= PRESSURE_MIN_COMMITS and ratio >= RATIO_ON:
        reasons.append("PRESSURE %d rebases for %d commits in 60 min = %.2f >= %.1f" % (rb_all, c_all, ratio, RATIO_ON))
    if loops:
        reasons.append("REBASE LOOP %s (>= %d rebases and >= %.1f per commit in 60 min)" % (" ".join("%s %d/%d" % (x, per[x][0], per[x][1]) for x in loops), LOOP_REBASES, LOOP_RATIO))
    losers = sorted([x for x, n in rejected.items() if n >= REJECT_SEAT_ON])
    if losers or rej_all >= REJECT_FLEET_ON:
        reasons.append("LOST RACES %d rejected pushes in 60 min (%s; >= %d a seat or >= %d the fleet)" % (rej_all, " ".join("%s %d" % (x, n) for x, n in sorted(rejected.items())), REJECT_SEAT_ON, REJECT_FLEET_ON))
    if l1 >= LOAD1_ON * cores and l5 >= LOAD5_ON * cores:
        reasons.append("LOAD %.1f / %.1f on %d cores >= %.1fx / %.1fx" % (l1, l5, cores, LOAD1_ON, LOAD5_ON))
    print("relay-trigger %s  velocity=%d/15min  rebases=%d commits=%d ratio=%.2f (60 min, %d seat roots)  rejected-pushes=%d/60min  load=%.1f/%.1f cores=%d"
          % (time.strftime("%Y-%m-%dT%H:%M:%S%z"), velocity, rb_all, c_all, ratio, len(per), rej_all, l1, l5, cores))
    print("  cpu        measured %.0f MHz average over %d cpus (max %.0f MHz, %.0f%%); platform_profile=%s epp=%s%s"
          % (avg_mhz, len(mhz), max_mhz, (100.0 * avg_mhz / max_mhz) if max_mhz else 0.0, profile, epp,
             ("  WARN CPU SLOW: under %.0f MHz with load %.1f >= %d cores" % (CPU_SLOW_MHZ, l1, cores)) if mhz and avg_mhz < CPU_SLOW_MHZ and l1 >= cores else ""))
    for s, (rb, c) in sorted(per.items(), key=lambda kv: (-kv[1][0], kv[0])):
        if rb or c:
            print("  %-10s rebases %3d  commits %3d" % (s, rb, c))
    contending = [s for s, (rb, c) in sorted(per.items(), key=lambda kv: (-kv[1][0], -kv[1][1], kv[0])) if rb > 0 and s != "ceo"]
    if reasons:
        print("RELAY: ON -- " + "; ".join(reasons) + " -- contending seats, most rebases first: " + " ".join(contending[:5]))
        return 1
    print("RELAY: OFF -- velocity %d < %d, ratio %.2f < %.1f, no rebase loop, load under %.1fx cores" % (velocity, VELOCITY_ON, ratio, RATIO_ON, LOAD1_ON))
    return 0


if __name__ == "__main__":
    sys.exit(main())
