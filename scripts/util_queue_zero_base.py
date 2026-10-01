#!/usr/bin/env python3
"""util_queue_zero_base.py [--apply] [--timeout S] [--no-run] -- A ROW EXISTS ONLY WHILE A MEASUREMENT SAYS THE PROBLEM EXISTS (ceo, CEO-1386).

Lon 2026-10-01 09:3x CDT, in-chat to the ceo, verbatim: "So it appears the work list is out of date with reality. How can we
tighten up what work items actually exist for real, i.e. are necessary?" and "So get your findings=0 or whatever you need to get
your act together and the fleet working real needed work." and "Do everything you suggest to modify your protocol, standard
operating procedure, mode of operation, ways to communicate, etc. You are the CEO."

THE PRINCIPLE: a live row names a red that an instrument shows TODAY. Every row of QUEUE.tsv is classified and the live file is
rebuilt from the classes; nothing is deleted -- an archived or retired row keeps its task file and comes back only by being
re-minted from a current red (mint refuses a placeholder DONE-WHEN since this ruling).

  KEEP      CLAIMED or ASSIGNED (a live claim is never touched by script, CEO-755c); PARKED-LON-HOLD; PARKED-UMBRELLA (an HQ's
            own steps under its one thing); BLOCKED-ON / PARKED-AWAITING whose blocker is itself live after the sweep.
  ARCHIVE   a DONE row still in the live file -> QUEUE.done.tsv (its receipt, if any, is in its claim file; none is minted here).
  RETIRE    SUPERSEDED and RETIRED rows -> QUEUE.retired.tsv; PARKED-EXECUTIVE-NO-SEAT (parked by a mode flip, never by a
            judgement), PARKED-REBUS-CLOSED, plain PARKED, orphaned BLOCKED/AWAITING -> QUEUE.retired.tsv as
            RETIRED:zero-base-<reason>; a FREE row whose DONE-WHEN is the mint placeholder (no finish line) or RUNS A BOARD
            (cannot close through done, CEO-1342 clause 5) -> retired likewise: the red it meant lives on the SUITE TABLE, and
            its owner re-mints one row per cause with a reader of the coo's row as the criterion.
  RUN       every other FREE row's DONE-WHEN is executed as the bus executes it (cwd $S4E_HOME, S4E_HOME exported, the progress
            and score writes off): rc 0 -> GREEN, the work is done, archived as DONE:zero-base-green; rc 1 -> RED, kept, and
            re-ranked to 2 (urgency is the board's to say; an every-suite-to-100 row keeps its rank); rc 2 -> CANNOT MEASURE,
            retired; a timeout -> kept at rank 2 and named.

The three files are written ONLY with --apply, against a FRESH read of QUEUE.tsv at write time: a row whose state moved while the
criteria ran (a claim, a done) is left as the fleet left it. Backups are written beside the files; every decision is written to
postoffice/salvage/zero-base-<stamp>.tsv (topic, owner, old state, class, rc, new place). Without --apply the classes and counts are
printed and nothing is written; --no-run skips the execution and reports the static classes only.
"""
import json, os, re, shutil, signal, subprocess, sys, time
PO = os.environ.get("S4E_POSTOFFICE", "/home/resources/postoffice")
Q, QD, QR, TASKS = PO + "/QUEUE.tsv", PO + "/QUEUE.done.tsv", PO + "/QUEUE.retired.tsv", PO + "/tasks"
S4E = os.environ.get("S4E_HOME", "/home/claude_ceo")
if "--help" in sys.argv or "-h" in sys.argv: print(__doc__); sys.exit(0)
apply = "--apply" in sys.argv; norun = "--no-run" in sys.argv
tmo = int(sys.argv[sys.argv.index("--timeout") + 1]) if "--timeout" in sys.argv else 240
stamp = time.strftime("%Y%m%d-%H%M%S")
PLACEHOLDER = ("NOT MEASURED", "minted with no acceptance criterion", "NOT EXPRESSED")

def rows_of(path):
    return open(path, encoding="utf-8").read().split("\n") if os.path.exists(path) else []

def donewhen(topic):
    f = os.path.join(TASKS, topic + ".task.md")
    if not os.path.exists(f): return None
    for ln in open(f, encoding="utf-8", errors="replace"):
        if ln.startswith("DONE-WHEN:"): return ln[len("DONE-WHEN:"):].strip()
    return ""

def board_topics():
    xc = S4E + "/SCRIP/scripts/util_donewhen_exemption_census.py"
    try:
        p = subprocess.run([sys.executable, xc, "--json"], capture_output=True, text=True, timeout=600, env=dict(os.environ, S4E_TASKS=TASKS))
        d = json.loads(p.stdout or "{}")
        return {r["topic"] for r in d.get("rows", []) if r.get("live") and r.get("class") in ("BOARD", "GUARD")}
    except Exception as e:
        print("WARNING: the exemption census could not be read (%s); no BOARD class" % e); return set()

def descendants(pid):
    kids = {}
    for d in os.listdir("/proc"):
        if not d.isdigit(): continue
        try: st = open("/proc/%s/stat" % d).read()
        except Exception: continue
        try: pp = int(st[st.rindex(")") + 2:].split()[1])
        except Exception: continue
        kids.setdefault(pp, []).append(int(d))
    out, todo = [], [pid]
    while todo:
        x = todo.pop(); ch = kids.get(x, []); out.extend(ch); todo.extend(ch)
    return out

def kill_tree(p):
    # GNU timeout(1) puts its child in a process group of its own, so killpg alone leaks a runner (measured 2026-10-01: a
    # ladder run outlived its 45 s criterion by minutes); every descendant is killed by pid, deepest first, then the group.
    for d in reversed(descendants(p.pid)):
        try: os.kill(d, signal.SIGKILL)
        except Exception: pass
    try: os.killpg(os.getpgid(p.pid), signal.SIGKILL)
    except Exception: pass
    try: p.kill()
    except Exception: pass
    p.wait()

def run_dw(dw):
    env = dict(os.environ, S4E_HOME=S4E, S4E_PROGRESS_OFF="1", S4E_SCORE_NO_WRITE="1", S4E_DONE_WHEN_RUN="1")
    p = subprocess.Popen(["bash", "-c", dw], cwd=S4E, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    try:
        return p.wait(timeout=tmo)
    except subprocess.TimeoutExpired:
        kill_tree(p)
        return "timeout"

def baton_age_days(topic):
    f = os.path.join(TASKS, topic + ".task.md")
    try: return (time.time() - os.path.getmtime(f)) / 86400.0
    except Exception: return None
EXPIRE_FREE_DAYS, EXPIRE_PARKED_DAYS = 7, 30

live = [ln for ln in rows_of(Q)]
boards = board_topics()
decisions = {}   # topic -> (class, rc, place) ; place in KEEP/DONE/RETIRED
topics_live = set()
parsed = []
for ln in live:
    f = ln.split("\t")
    if len(f) < 4 or ln.startswith("#"): continue
    parsed.append(f); topics_live.add(f[1])
def stt(s): return s.split(":")[0]
# pass 1: static classes
for f in parsed:
    rank, topic, owner, state = f[0], f[1], f[2], f[3]
    s = stt(state)
    if s.startswith("CLAIMED") or s.startswith("ASSIGNED"): decisions[topic] = ("KEEP-LIVE-CLAIM", "", "KEEP"); continue
    if s.startswith("DONE"): decisions[topic] = ("ARCHIVE-DONE", "", "DONE"); continue
    if s.startswith("SUPERSEDED") or s.startswith("RETIRED"): decisions[topic] = ("RETIRE-ALREADY", "", "RETIRED"); continue
    if s == "PARKED-LON-HOLD" or s == "PARKED-UMBRELLA": decisions[topic] = ("KEEP-" + s, "", "KEEP"); continue
    if s in ("PARKED-EXECUTIVE-NO-SEAT", "PARKED-REBUS-CLOSED", "PARKED"): decisions[topic] = ("RETIRE-" + s.lower(), "", "RETIRED"); continue
    if s in ("PARKED-SUPERSEDED-BY", "PARKED-DUPLICATE-OF"): decisions[topic] = ("RETIRE-" + s.lower(), "", "RETIRED"); continue
    if s == "PARKED-EXPIRED":
        a = baton_age_days(topic)
        decisions[topic] = ("RETIRE-expired-%dd-parked" % EXPIRE_PARKED_DAYS, "", "RETIRED") if a is not None and a > EXPIRE_PARKED_DAYS else ("KEEP-PARKED-EXPIRED", "", "KEEP"); continue
    if s.startswith("PARKED-AWAITING") or s.startswith("BLOCKED-ON"): decisions[topic] = ("BLOCKER?", "", None); continue
    if s == "FREE":
        dw = donewhen(topic)
        if dw is None: decisions[topic] = ("RETIRE-no-task-file", "", "RETIRED"); continue
        if not dw or any(k in dw for k in PLACEHOLDER): decisions[topic] = ("RETIRE-placeholder-done-when", "", "RETIRED"); continue
        if topic in boards: decisions[topic] = ("RETIRE-board-done-when", "", "RETIRED"); continue
        decisions[topic] = ("RUN", dw, None); continue
    decisions[topic] = ("KEEP-other:" + s, "", "KEEP")
# pass 2: run the FREE criteria
todo = [t for t, d in decisions.items() if d[0] == "RUN"]
print("static classes:", {k: v for k, v in sorted(__import__("collections").Counter(d[0] for d in decisions.values()).items())})
print("criteria to run:", len(todo), "(timeout %ss each)" % tmo, flush=True)
if not norun:
    t0 = time.time(); tally = {"GREEN": 0, "RED": 0, "CANNOT": 0, "TIMEOUT": 0}
    for i, t in enumerate(todo, 1):
        print("RUNNING %s" % t, flush=True)
        rc = run_dw(decisions[t][1])
        if rc == 0: decisions[t] = ("GREEN-now", 0, "DONE"); tally["GREEN"] += 1; v = "GREEN"
        elif rc == 1: decisions[t] = ("RED-now", 1, "KEEP"); tally["RED"] += 1; v = "RED"
        elif rc == "timeout":
            a = baton_age_days(t); exp = a is not None and a > EXPIRE_FREE_DAYS
            decisions[t] = ("TIMEOUT-expired-parked" if exp else "TIMEOUT-kept", "timeout", "KEEP"); tally["TIMEOUT"] += 1; v = "TIMEOUT" + ("-EXPIRED" if exp else "")
        else: decisions[t] = ("RETIRE-cannot-measure-rc%s" % rc, rc, "RETIRED"); tally["CANNOT"] += 1; v = "CANNOT-MEASURE"
        el = time.time() - t0; eta = el / i * (len(todo) - i)
        print("COUNTDOWN %d left of %d | %d done | %dm%02ds elapsed, ~%dm%02ds to go | GREEN %d RED %d CANNOT %d TIMEOUT %d | last: %s -> %s" % (len(todo) - i, len(todo), i, el // 60, el % 60, eta // 60, eta % 60, tally["GREEN"], tally["RED"], tally["CANNOT"], tally["TIMEOUT"], t[:70], v), flush=True)
# pass 3: blockers
def blocker_of(state):
    m = re.match(r"(?:PARKED-AWAITING|BLOCKED-ON):(.*)", state); return m.group(1) if m else None
for f in parsed:
    topic, state = f[1], f[3]
    if decisions.get(topic, ("",))[0] == "BLOCKER?":
        b = blocker_of(state); live_b = b in decisions and decisions[b][2] == "KEEP"
        decisions[topic] = ("KEEP-blocked-on-live", "", "KEEP") if live_b else ("RETIRE-blocker-not-live", "", "RETIRED")
cnt = __import__("collections").Counter(d[0] for d in decisions.values())
print("final classes:"); [print("  %-36s %d" % (k, v)) for k, v in sorted(cnt.items())]
print("live rows after: %d  archived DONE: %d  retired: %d" % (sum(1 for d in decisions.values() if d[2] == "KEEP"), sum(1 for d in decisions.values() if d[2] == "DONE"), sum(1 for d in decisions.values() if d[2] == "RETIRED")))
greens = [t for t, d in decisions.items() if d[0] == "GREEN-now"]
if greens: print("GREEN now (archived as done):"); [print("   " + t) for t in greens]
if not apply: print("DRY RUN: nothing written"); sys.exit(0)
# write against a fresh read
fresh = rows_of(Q); out, done_add, ret_add, log, ledger_add = [], [], [], [], []
old_state = {f[1]: f[3] for f in parsed}
for ln in fresh:
    f = ln.split("\t")
    if len(f) < 4 or ln.startswith("#"): out.append(ln); continue
    topic = f[1]; d = decisions.get(topic)
    if d is None or f[3] != old_state.get(topic): out.append(ln); log.append((topic, f[2], f[3], "UNTOUCHED-moved-meanwhile", "", "KEEP")); continue
    cls, rc, place = d
    if place == "KEEP":
        if cls == "RED-now" and "-every-suite-to-100-" not in topic and f[0] in ("0", "1"): f[0] = "2"
        if cls == "TIMEOUT-expired-parked": f[3] = "PARKED-EXPIRED"
        if cls == "RED-now": ledger_add.append((topic, f[0]))
        out.append("\t".join(f))
    elif place == "DONE":
        f[3] = f[3] if cls == "ARCHIVE-DONE" else "DONE:zero-base-green-ceo-1386"; done_add.append("\t".join(f))
    else:
        f[3] = f[3] if cls == "RETIRE-ALREADY" else "RETIRED:zero-base-ceo-1386-" + cls.replace("RETIRE-", ""); ret_add.append("\t".join(f))
    log.append((topic, f[2], old_state[topic], cls, str(rc), place))
for p in (Q, QD, QR):
    if os.path.exists(p): shutil.copyfile(p, p + ".bak.%s-zero-base-ceo-1386" % stamp)
open(Q, "w", encoding="utf-8", newline="\n").write("\n".join(out))
def append(p, rows):
    if not rows: return
    cur = rows_of(p); txt = "\n".join([r for r in cur if r != ""] + rows) + "\n"; open(p, "w", encoding="utf-8", newline="\n").write(txt)
append(QD, done_add); append(QR, ret_add)
when = time.strftime("%Y-%m-%d %H:%M %Z")
for topic, rank in ledger_add:
    f = os.path.join(TASKS, topic + ".task.md")
    try:
        with open(f, "a", encoding="utf-8", newline="\n") as fh:
            fh.write("\n- %s zero-base (ceo, CEO-1386): the DONE-WHEN ran RED (rc=1) in %s under a %ss limit; the row stays live at rank %s. A measured red is the only reason this row exists; the clock for PARKED-EXPIRED restarts here.\n" % (when, S4E, tmo, rank))
    except Exception as e: print("WARNING: ledger line not written for %s: %s" % (topic, e))
os.makedirs(PO + "/salvage", exist_ok=True)
with open(PO + "/salvage/zero-base-%s-ceo-1386.tsv" % stamp, "w", encoding="utf-8", newline="\n") as fh:
    fh.write("topic\towner\told_state\tclass\trc\tplace\n")
    for l in log: fh.write("\t".join(l) + "\n")
print("WRITTEN: live %d rows, +%d done, +%d retired; log postoffice/salvage/zero-base-%s-ceo-1386.tsv; backups beside the files" % (sum(1 for l in out if l and not l.startswith("#")), len(done_add), len(ret_add), stamp))
