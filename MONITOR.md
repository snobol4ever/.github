# MONITOR.md — Five-Way Sync-Step Monitor (L3)

**The core insight:** TRACE output is a deterministic sequential log.
The first line where any participant diverges from the oracle is the exact
moment — the exact variable, function, or label — where the bug fires.
No bisecting. No bombing. No chasing.

**The bonus:** A bug in one backend is almost certainly not in the other two.
The agreeing backends become the living specification for the fix.
Known symptom + two reference implementations = essentially free fix.

**The goal:** M-BEAUTIFY-BOOTSTRAP — `beauty.sno` reads `beauty.sno` and
all three compiled backends produce output identical to the oracle AND
identical to the input. A fixed point.

---

## The Five Participants

| # | Participant | Role | TRACE stream |
|---|-------------|------|-------------|
| 1 | CSNOBOL4 2.3.3 | Primary oracle | stderr |
| 2 | SPITBOL x64 4.0f | Secondary oracle | stdout |
| 3 | snobol4x ASM backend | Compiled target | stderr |
| 4 | snobol4x JVM backend | Compiled target | stderr |
| 5 | snobol4x NET backend | Compiled target | stderr |

**Consensus rule:**
- Both oracles agree, one backend diverges → our bug; other backends are the reference.
- Both oracles agree, all three backends diverge the same way → systematic emitter bug.
- Oracles disagree → semantic edge case; check Gimpel §7.
- Two backends agree, one diverges → the two agreeing backends specify the fix.

**SPITBOL stream quirk:** SPITBOL sends TRACE to stdout, all others to stderr.
`run_monitor.sh` redirects per participant before diffing.

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
As each beauty subsystem milestone fires (see BEAUTY.md), add EXCLUDE rules
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
INC=/home/claude/snobol4corpus/programs/inc
BEAUTY=/home/claude/snobol4corpus/programs/beauty/beauty.sno

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
Will move to `snobol4harness/monitor/` when extending to other repos.

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
INC=/home/claude/snobol4corpus/programs/inc
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

### Sprint M1 — monitor-scaffold

**Goal:** Infrastructure exists. One test runs end-to-end against CSNOBOL4 only.

**Deliverables:**
- `snobol4x/test/monitor/inject_traces.py`
- `snobol4x/test/monitor/run_monitor.sh` (CSNOBOL4 only)
- `snobol4x/test/monitor/tracepoints.conf`
- One passing test: `crosscheck/hello/001_output_string_literal.sno`

**Pass condition:** `run_monitor.sh` on `001_output_string_literal.sno` exits 0,
CSNOBOL4 trace stream captured and non-empty.
**Fires:** M-MONITOR-SCAFFOLD

---

### Sprint M2 — monitor-5way

**Goal:** All 5 participants wired. SPITBOL + 3 backends alongside CSNOBOL4.

**Deliverables:**
- `run_monitor.sh` — all 5 participants + stream redirect logic
- `normalize_trace.py` — SPITBOL format normalization + ignore-points
- `tracepoints.conf` — initial ignore-points (`&TERMINAL`, `DATATYPE` case)
- `001_output_string_literal.sno` — all 5 streams captured, diffed, passing

**Pass condition:** `run_monitor.sh` on `001_output_string_literal.sno` exits 0,
all 5 streams present, no unexpected divergence.
**Fires:** M-MONITOR-5WAY

---

### Sprint M3 — monitor-4demo

**Goal:** Validate harness on known-good programs. Four working demos pass
all 5 participants with zero unexpected divergences.

**Programs** (from `snobol4x/demo/` on `asm-backend` branch):
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
and monitor run. Full plan → **[BEAUTY.md](BEAUTY.md)**.

**Strategy:**
- One driver per subsystem: a small `.sno` that `-INCLUDE`s only that file
  (plus dependencies) and exercises all DEFINE'd functions
- Drivers live in `snobol4x/test/beauty/<subsystem>/driver.sno`
- Gimpel corpus (145 programs) provides semantic cross-validation
- Monitor runs each driver: CSNOBOL4 oracle + ASM (expanding to JVM+NET as
  M-MONITOR-5WAY is reached)
- As each subsystem passes, EXCLUDE rules are added to `tracepoints.conf`
  to suppress proven-clean variables from future trace streams

**19 sub-milestones in dependency order** (full table in BEAUTY.md):
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

- `100/106` C crosscheck (6 pre-existing) — never regress
- `26/26` ASM crosscheck — never regress
- Monitor fixes never introduce new crosscheck failures
- If they do: fix the regression before continuing

---

*MONITOR.md = L3. Sprint content lives here. Milestone rows live in PLAN.md.*
