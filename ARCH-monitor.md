# ARCH-monitor.md — Five-Way Sync-Step Monitor

**The core insight:** TRACE output is a deterministic sequential log.
The first line where any participant diverges from the oracle is the exact
moment — the exact variable, function, or label — where the bug fires.
No bisecting. No bombing. No chasing.

**The bonus:** A bug in one backend is almost certainly not in the other two.
The agreeing backends become the living specification for the fix.
Known symptom + two reference implementations = essentially free fix.

**The developer cycle:**
```
write driver → run monitor → first diverging line names the bug
              → fix backend → re-run monitor → repeat → milestone fires
```
This is the full cycle in one BEAUTY SESSION. The monitor is the engine that
makes it fast. MONITOR SESSION builds the tool; BEAUTY SESSION uses it.

**The goal:** M-BEAUTIFY-BOOTSTRAP — `beauty.sno` reads `beauty.sno` and
all three compiled backends produce output identical to the oracle AND
identical to the input. A fixed point.

---

## The Five Participants

| # | Participant | Role | TRACE stream |
|---|-------------|------|-------------|
| 1 | SPITBOL x64 4.0f | **Primary oracle** (D-005) | stdout |
| 2 | CSNOBOL4 2.3.3 | Secondary reference | stderr |
| 3 | snobol4x ASM backend | Compiled target | stderr |
| 4 | snobol4x JVM backend | Compiled target | stderr |
| 5 | snobol4x NET backend | Compiled target | stderr |

**Compatibility target: snobol4x implements SPITBOL. SPITBOL is the primary oracle. (D-001)**
- All SPITBOL extensions, switches, HOST() semantics are matched.
- `DATATYPE()` returns **UPPERCASE** (snobol4x convention, D-002). SPITBOL lowercase is an ignore-point.
- `.NAME` is a third dialect matching SPITBOL *observable* behaviour. See D-004.
- CSNOBOL4 quirks (FENCE semantics, DATATYPE case) do not drive fixes.

**Consensus rules (updated D-005):**
- SPITBOL and snobol4x agree, CSNOBOL4 diverges → known CSNOBOL4 quirk; not our bug.
- SPITBOL and CSNOBOL4 agree, snobol4x diverges → our bug; fix to match SPITBOL.
- SPITBOL and CSNOBOL4 disagree, snobol4x matches SPITBOL → correct.
- SPITBOL and CSNOBOL4 disagree, snobol4x matches neither → our bug; fix to SPITBOL.
- DATATYPE case differences → ignore-point always (D-002).
- `.NAME` DT_N vs DT_S differences → ignore-point (D-004).

**SPITBOL stream quirk:** SPITBOL sends TRACE to stdout, all others to stderr.
**IPC solution:** All participants use LOAD'd `monitor_ipc.so` — see §IPC Architecture below.
No stream redirection needed. Each participant writes trace events directly to its own named FIFO.

---

## IPC Architecture — monitor_ipc.so

**The problem with stderr/stdout:** TERMINAL= callbacks write to stderr (CSNOBOL4) or stdout
(SPITBOL). Runtime panics, error messages, and trace events all land in the same stream.
Redirect hacks are fragile. Parallel execution is impossible.

**The solution:** A LOAD'd C shared library that writes trace events to a named FIFO (pipe),
bypassing all stdio streams entirely. One `.so` file, compatible ABI for both CSNOBOL4 and
SPITBOL (`lret_t fn(LA_ALIST)` — identical dlopen/dlsym convention, verified from source).

### monitor_ipc.c — three functions

```c
// LOAD("MON_OPEN(STRING)STRING",    "./monitor_ipc.so")
// LOAD("MON_SEND(STRING,STRING)STRING", "./monitor_ipc.so")
// LOAD("MON_CLOSE()STRING",         "./monitor_ipc.so")

lret_t MON_OPEN(LA_ALIST)  // arg0 = FIFO path → opens O_WRONLY, stores fd
lret_t MON_SEND(LA_ALIST)  // arg0 = kind, arg1 = body → write atomic line to FIFO
lret_t MON_CLOSE(LA_ALIST) // closes FIFO fd
```

`write()` on a named FIFO is atomic for lines < PIPE_BUF (4096 bytes) — no locking needed
even with parallel participants, since each participant has its own FIFO.

### inject_traces.py — new preamble

Instead of MONCALL/MONRET/MONVAL writing to `TERMINAL =`, they call `MON_SEND()`:

```snobol4
        LOAD('MON_OPEN(STRING)STRING',       &MONITOR_SO)
        LOAD('MON_SEND(STRING,STRING)STRING', &MONITOR_SO)
        LOAD('MON_CLOSE()STRING',             &MONITOR_SO)
        MON_OPEN(&MONITOR_FIFO)
MONCALL MON_SEND('CALL',   MONN)                                  :(RETURN)
MONRET  MON_SEND('RETURN', MONN ' = ' CONVERT(VALUE(MONN),'STRING')) :(RETURN)
MONVAL  MON_SEND('VALUE',  MONN ' = ' CONVERT(VALUE(MONN),'STRING')) :(RETURN)
```

`&MONITOR_FIFO` and `&MONITOR_SO` are set as SNOBOL4 variables by the injector preamble
(read from env vars `MONITOR_FIFO` and `MONITOR_SO` via `HOST()`).

### ASM/JVM/NET runtime — comm_var() change

`comm_var()` in `snobol4.c` currently writes to `monitor_fd` (fd 2 = stderr).
Change: open `getenv("MONITOR_FIFO")` at init time; write there instead.
Same atomic write, zero stderr pollution.

### Timeout = Infinite Loop Detection

**The key insight:** Between any two TRACE callbacks, a correct participant emits its next
event promptly. A FIFO that goes **silent for longer than T seconds** between events means
exactly one thing: that participant is in an infinite loop (or deadlocked). No bisecting
needed — we already know *which* participant and *which* trace event was last seen before it
hung.

`monitor_collect.py` uses `select()`/`poll()` with a configurable timeout (default 10s)
on all open FIFO file descriptors simultaneously:

```python
INTER_EVENT_TIMEOUT = 10   # seconds; configurable via --timeout

ready = select.select(open_fifos, [], [], INTER_EVENT_TIMEOUT)
if not ready[0]:
    # silence on ALL remaining FIFOs → global timeout → kill all
    kill_all_participants()
else:
    for fd in ready[0]:
        line = fd.readline()
        if line == '':          # EOF = participant exited cleanly
            close_fifo(fd)
        else:
            record_event(fd, line)
            # per-participant watchdog: reset this participant's timer
```

Per-participant watchdog: each participant has its own `last_event_time`. After any `select()`
returns, any participant whose `last_event_time` is more than T seconds ago is declared hung:

```python
now = time.monotonic()
for p in participants:
    if p.alive and (now - p.last_event_time) > INTER_EVENT_TIMEOUT:
        print(f"TIMEOUT [{p.name}] — last event: {p.last_event!r}")
        print(f"  → infinite loop or deadlock at this trace point")
        p.kill()
        p.alive = False
```

**What the operator sees:**
```
PASS [csn] hello
PASS [spl] hello
TIMEOUT [asm] — last event: 'VALUE X = 3'
  → infinite loop or deadlock at this trace point
PASS [jvm] hello
PASS [net] hello
```

The two agreeing participants (csn + spl = oracles) immediately specify where the loop is.
The last trace event before silence is the exact statement where the ASM backend diverged
into non-termination. No `&STLIMIT` needed. No binary search. The monitor *is* the debugger.

**Note on `&STLIMIT`:** Still useful as a hard backstop *inside* the SNOBOL4 program to
prevent truly runaway programs from filling the FIFO. Set `&STLIMIT = 5000000` in
`tracepoints.conf` preamble. If hit, CSNOBOL4/SPITBOL emit an error to stderr (clean,
not the trace FIFO) and exit — the FIFO closes, the collector sees EOF, marks that
participant done. Belt and suspenders.

### ⚠️ M-MONITOR-IPC-5WAY WAS IMPLEMENTED WRONG — ASYNC NOT SYNC-STEP

The B-236 implementation used async parallel FIFOs: all 5 ran at full speed,
a passive collector logged traces, divergences found by post-hoc diff.
This does NOT stop participants at the exact moment of first divergence.

**M-MONITOR-SYNC** replaces it with the correct sync-step barrier protocol.

### Sync-Step Barrier Protocol (M-MONITOR-SYNC)

**Two FIFOs per participant:**
- `<n>.evt` — participant writes events, controller reads
- `<n>.ack` — controller writes `G`/`S`, participant blocks reading

**Per trace event:**
1. Participant writes `"KIND body\n"` to `<n>.evt`
2. Participant **blocks** on `read()` from `<n>.ack`
3. Controller reads one event from each of all 5 `*.evt` FIFOs
4. Consensus rule applied — oracle = CSNOBOL4 (participant 0)
5. Controller writes `G` (go) or `S` (stop) to each `*.ack`
6. `G` → `MON_SEND` returns, participant continues
   `S` → `MON_SEND` returns FAIL, participant branches `:F(END)`

**On divergence:** `S` to all, exact diverging event printed, all 5 stop immediately.
**On infinite loop:** participant never writes next event → per-participant timeout fires.

**Files:**
- `test/monitor/monitor_ipc_sync.c` — `MON_OPEN(evt,ack)` two-arg, `MON_SEND` blocks on ack
- `test/monitor/monitor_ipc_sync.so` — built from above
- `test/monitor/monitor_sync.py` — barrier controller: read×5, compare, send G/S
- `test/monitor/run_monitor_sync.sh` — 10 FIFOs, launch controller then 5 participants
- `test/monitor/inject_traces.py` — preamble: `MON_OPEN(STRING,STRING)STRING`, reads `MONITOR_ACK_FIFO`

**Env vars:** `MONITOR_FIFO` (evt), `MONITOR_ACK_FIFO` (ack), `MONITOR_SO`

---

## Trace-Points and Ignore-Points

### Trace-Points
A trace-point is an observation hook. The program keeps running.
The event appears in the stream. **Not a breakpoint — never stops execution.**

Four kinds of trace-points, all configurable:
- **VALUE** — fires on every assignment to a variable: `TRACE(var,'VALUE')`
- **CALL** — fires on function entry: `TRACE(fn,'CALL')`
- **RETURN** — fires on function exit (normal): `TRACE(fn,'RETURN')`
- **LABEL** — fires when a label is reached: `TRACE(label,'LABEL')`

Configured in `tracepoints.conf` (or per-test override files).

```
# tracepoints.conf — default rules (maximally inclusive)
INCLUDE  *            # all DEFINE'd functions: CALL + RETURN
INCLUDE  OUTPUT       # VALUE trace on OUTPUT
INCLUDE  *            # all variables found on LHS of =: VALUE trace
EXCLUDE  &RANDOM      # non-deterministic — always exclude
EXCLUDE  &TIME        # wall-clock — always exclude
EXCLUDE  &DATE        # wall-clock — always exclude
```

**INCLUDE/EXCLUDE use regular expressions** matching variable and function names.
Scope qualifiers narrow the match:
- `name` — matches any variable or function named `name` anywhere
- `func/var` — matches variable `var` only inside function `func`
- (planned) `{global}/var` — matches module-scope global `var` only

**Noise reduction as subsystems are proven clean:**
As each beauty subsystem milestone fires (see ARCH-snobol4-beauty-testing.md), add EXCLUDE rules
to suppress that subsystem's variables and functions from the trace stream.
This keeps the stream focused on the subsystem under test.

```
# Example: after M-BEAUTY-STACK fires, suppress stack internals
EXCLUDE  @S           # stack link variable — proven clean
EXCLUDE  InitStack    # proven clean
EXCLUDE  Push         # proven clean
EXCLUDE  Pop          # proven clean
EXCLUDE  Top          # proven clean
```

Per-test overrides: place a `<testname>.tracepoints` file alongside the `.sno`.

### Ignore-Points
An ignore-point fires when a trace-point value *differs* between participants
but the difference matches a known pattern. The event still appears in both
streams — it just does not count as a divergence.

```
# ignore-point rules in tracepoints.conf
IGNORE  &TERMINAL     tty\d+         # "tty02" vs "tty05" — session artifact
IGNORE  DATATYPE(*)   [a-z]+|[A-Z]+  # SPITBOL lowercase vs CSNOBOL4 uppercase
IGNORE  &STNO         *              # statement numbers may differ by dialect
```

`inject_traces.py` reads `tracepoints.conf` and:
1. Prepends `TRACE(var,'VALUE')` calls for all included variables
2. Prepends `TRACE(fn,'CALL')` + `TRACE(fn,'RETURN')` for all DEFINE'd functions
3. Emits ignore-rule table consumed by `normalize_trace.py` when diffing streams

---

## The Beautify Bootstrap Point

`beauty.sno` reads `beauty.sno` as input and produces output byte-for-byte
identical to `beauty.sno`. Oracle = compiled = input. A fixed point.
This is the SNOBOL4 frontend correctness proof for all three backends.

```bash
INC=/home/claude/corpus/programs/inc
BEAUTY=/home/claude/corpus/programs/beauty/beauty.sno

snobol4 -f -P256k -I$INC $BEAUTY < $BEAUTY > oracle.sno
./snobol4-asm < $BEAUTY > asm.sno
./snobol4-jvm < $BEAUTY > jvm.sno
./snobol4-net < $BEAUTY > net.sno

diff oracle.sno asm.sno    # empty
diff oracle.sno jvm.sno    # empty
diff oracle.sno net.sno    # empty
diff oracle.sno $BEAUTY    # empty  <- the bootstrap condition
```

**M-BEAUTIFY-BOOTSTRAP fires when all four diffs are empty.**

---

## Monitor Infrastructure

Lives in `snobol4x/test/monitor/` initially.
Will move to `harness/monitor/` when extending to other repos.

```
snobol4x/test/monitor/
    inject_traces.py        <- reads .sno + tracepoints.conf -> instrumented .sno
    normalize_trace.py      <- applies ignore-points, normalizes SPITBOL format
    run_monitor.sh          <- single test: 5 participants -> 5 streams -> diff
    run_monitor_suite.sh    <- loop over a directory of .sno files
    tracepoints.conf        <- default include/exclude/ignore rules
```

### run_monitor.sh (single test)

```bash
#!/bin/bash
# run_monitor.sh <sno_file> [tracepoints_conf]
# Exit 0 = all match. Exit 1 = divergence (prints first diff per backend).
SNO=$1
CONF=${2:-$(dirname $0)/tracepoints.conf}
TMP=/tmp/monitor_$$
INC=/home/claude/corpus/programs/inc
DIR=$(dirname $(realpath $0))/../../..   # snobol4x root

python3 $(dirname $0)/inject_traces.py $SNO $CONF > $TMP.sno

snobol4 -f -P256k -I$INC $TMP.sno < /dev/null 2>$TMP.csn  >/dev/null
spitbol -b           $TMP.sno < /dev/null >$TMP.spl 2>/dev/null
$DIR/snobol4-asm     $TMP.sno < /dev/null 2>$TMP.asm >/dev/null
$DIR/snobol4-jvm     $TMP.sno < /dev/null 2>$TMP.jvm >/dev/null
$DIR/snobol4-net     $TMP.sno < /dev/null 2>$TMP.net >/dev/null

python3 $(dirname $0)/normalize_trace.py $CONF \
    $TMP.csn $TMP.spl $TMP.asm $TMP.jvm $TMP.net

FAIL=0
for B in asm jvm net; do
    RESULT=$(diff $TMP.csn.norm $TMP.$B.norm)
    if [ -z "$RESULT" ]; then echo "PASS [$B] $SNO"
    else echo "FAIL [$B] $SNO"; echo "$RESULT" | head -5; FAIL=1; fi
done

ODIFF=$(diff $TMP.csn.norm $TMP.spl.norm)
[ -n "$ODIFF" ] && echo "ORACLE-DIFF [csnobol4 vs spitbol] — check Gimpel §7" \
    && echo "$ODIFF" | head -3

rm -f $TMP.*; exit $FAIL
```

### inject_traces.py (outline)

1. Parse `tracepoints.conf` — build include/exclude/ignore sets
2. Scan `.sno` for `DEFINE('funcname(` → CALL+RETURN trace-points
3. Scan `.sno` for `varname =` on LHS → VALUE trace-points
4. Apply EXCLUDE rules
5. Prepend `TRACE()` calls to `.sno` source
6. Emit ignore-rule table as SNOBOL4 comments at top (read by normalize)

### normalize_trace.py (outline)

1. Read ignore rules from conf
2. Strip lines matching any IGNORE pattern from each stream
3. Normalize SPITBOL format (`****N*******`) to CSNOBOL4 format (`*** name = val`)
4. Write `.norm` files for diffing

---

## Sprint Plan

### Sprints M1 + M2 ✅ COMPLETE

M1 (scaffold B-227): 2-way CSN+ASM via comm_var. M2 (IPC B-229–B-236): 5-way FIFO IPC, hello PASS all 5.
All sub-milestones through M-MONITOR-IPC-5WAY fired. See SESSIONS_ARCHIVE for detail.

---

### Sprint M3 — monitor-4demo (CURRENT)

**Goal:** wordcount + treebank + claws5 pass all 5 participants. **Fires:** M-MONITOR-4DEMO

**Blocking bug milestones (one session each, in order):**
1. **M-MON-BUG-NET-TIMEOUT** — `net_mon_var` opens StreamWriter per-call → FIFO deadlock. Fix: static-open pattern mirroring JVM `sno_mon_init/sno_mon_fd`. Owned by: NET backend session.
2. **M-MON-BUG-SPL-EMPTY** — SPITBOL trace empty for treebank/claws5. Diagnose `monitor_ipc_spitbol.so` path. Owned by: B-session.
3. **M-MON-BUG-ASM-WPAT** — ASM: SEQ-of-patterns stringifies as `PATTERNPATTERN`. Fix `comm_var` type path. Owned by: ASM backend session.
4. **M-MON-BUG-JVM-WPAT** — JVM: pattern DT not handled in `sno_mon_var`, emits empty. Owned by: JVM session.

**After all 4 fire:** re-run wordcount/treebank/claws5 → fire M-MONITOR-4DEMO.

---

### Sprint M3b — monitor-corpus9

**Goal:** Use the 5-way monitor to diagnose and fix the 9 known ASM corpus failures.
The monitor does the work — run each failing test through all 5 participants, read
the first diverging trace line, fix the emitter, rerun. No bisecting needed.

**The 9 targets:**
- `022_concat_multipart` — concat slot aliasing (first literal clobbered)
- `055_pat_concat_seq` — same root cause
- `064_capture_conditional` — `L_unk_` undefined label emitted
- `cross`, `word1`, `word2`, `word3`, `word4`, `wordcount` — runtime issues (@ capture, REPLACE, INPUT loop)

**Protocol per test:**
1. `run_monitor.sh crosscheck/<dir>/<test>.sno` — read first FAIL line
2. Both oracles agree → ASM is wrong; other backends specify the fix
3. Fix `emit_byrd_asm.c`, rerun, confirm PASS
4. ASM corpus count climbs toward 106/106

**Fires:** M-MONITOR-CORPUS9 when ASM corpus reaches 106/106
- `roman.sno` — works on all 3 backends
- `wordcount.sno` — works on all 3 backends
- `treebank.sno` — works on all 3 backends
- `claws5.sno` — 3 undef beta labels; track divergence count as progress metric

**Pass condition:** roman + wordcount + treebank all PASS on all 5 participants.
claws5 divergence count documented. 100/106 C + 26/26 ASM invariants hold.
**Fires:** M-MONITOR-4DEMO

---

### Sprint M4 — beauty-subsystems (19 sprints)

**Goal:** Prove each of beauty.sno's 19 `-INCLUDE` subsystems correct in isolation
before attempting full self-beautification. Each subsystem gets its own test driver
and monitor run. Full plan → **[ARCH-snobol4-beauty-testing.md](ARCH-snobol4-beauty-testing.md)**.

**Strategy:**
- One driver per subsystem: a small `.sno` that `-INCLUDE`s only that file
  (plus dependencies) and exercises all DEFINE'd functions
- Drivers live in `snobol4x/test/beauty/<subsystem>/driver.sno`
- Gimpel corpus (145 programs) provides semantic cross-validation
- Monitor runs each driver: CSNOBOL4 oracle + ASM (expanding to JVM+NET as
  M-MONITOR-5WAY is reached)
- As each subsystem passes, EXCLUDE rules are added to `tracepoints.conf`
  to suppress proven-clean variables from future trace streams

**19 sub-milestones in dependency order** (full table in ARCH-snobol4-beauty-testing.md):
M-BEAUTY-GLOBAL → M-BEAUTY-IS → M-BEAUTY-FENCE → M-BEAUTY-IO →
M-BEAUTY-CASE → M-BEAUTY-ASSIGN → M-BEAUTY-MATCH → M-BEAUTY-COUNTER →
M-BEAUTY-STACK → M-BEAUTY-TREE → M-BEAUTY-SR → M-BEAUTY-TDUMP →
M-BEAUTY-GEN → M-BEAUTY-QIZE → M-BEAUTY-READWRITE → M-BEAUTY-XDUMP →
M-BEAUTY-SEMANTIC → M-BEAUTY-OMEGA → M-BEAUTY-TRACE

**Protocol per divergence (same as before):**
1. `run_monitor.sh test/beauty/<sub>/driver.sno` — note first diverging trace line
2. Check: do any two backends agree? Those two specify the correct behavior
3. Fix the diverging emitter
4. Rerun — confirm divergence gone; invariants hold
5. Repeat until driver passes all backends vs oracle
6. Add EXCLUDE rules for this subsystem's proven-clean variables

**After all 19 fire → Sprint M5:**
Run `beauty.sno` self-beautification through the monitor. At this point all
subsystems are proven correct individually; full-program divergences are
integration bugs only. Fix until all four diffs are empty.

**Fires:** M-BEAUTIFY-BOOTSTRAP

---

## Invariants During Monitor Work

- `97/106` ASM corpus crosscheck — never regress below 97
- Monitor fixes never introduce new crosscheck failures
- If they do: fix the regression before continuing

---

*MONITOR.md = L3. Sprint content lives here. Milestone rows live in PLAN.md.*
