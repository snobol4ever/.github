# MONITOR.md — M-MONITOR Milestone (L3)

**The core insight:** TRACE output is a deterministic sequential log.
The first line where oracle trace ≠ compiled trace is the **exact moment** a bug fires.
No bisecting. No bombing. No chasing. You see it instantly.

---

## Milestone Definition

| ID | Trigger | Repo |
|----|---------|------|
| **M-MONITOR** | All 152 corpus diag tests: oracle_trace == compiled_trace for every test | TINY |

**What fires it:** for every `.sno` in `snobol4corpus/crosscheck/`, run both
CSNOBOL4 and the snobol4x compiled binary with full TRACE active.
Every test must produce identical trace streams. Zero diffs.

---

## Why This Is Different

Previous paradigms chase bugs after output diverges:
- Crosscheck: tells you *something* is wrong
- Probe: binary-searches *where* in &STLIMIT steps
- Bomb: instruments C source to find *which* call

**Monitor tells you instantly:**
- Which variable was assigned the wrong value
- Which function was called when it shouldn't have been
- Which function returned the wrong value
- At which statement number it first went wrong

First diverging trace line = root cause. Fix it. Move on.

---

## Trace Event Format

All events go to stderr. Format matches CSNOBOL4 TRACE output exactly:

```
*** varname = newvalue          ← VALUE trace: variable assigned
*** labelname                   ← LABEL trace: statement reached  
*** funcname(arg1, arg2, ...)   ← CALL trace: function entered
*** funcname => returnvalue     ← RETURN trace: function returned (RETURN)
*** funcname => *FRETURN*       ← RETURN trace: function returned (FRETURN)
*** funcname => *NRETURN*       ← RETURN trace: function returned (NRETURN)
```

**CSNOBOL4 gotchas (confirmed from FRONTEND-SNOBOL4.md):**
- `TRACE(...,'KEYWORD')` does NOT work in CSNOBOL4 — never use it
- `&STCOUNT` increments correctly on CSNOBOL4 (verified 2026-03-16 — prior "always 0" claim was wrong)
- `TRACE('var','VALUE')` works correctly — primary tool

---

## Sprint Plan

### Sprint M1 — `monitor-scaffold` (session 123)

**Goal:** Build the monitor runner. One script, one test, one diff.

```bash
# harness/monitor/run_monitor.sh
# Usage: run_monitor.sh <sno_file> <oracle_binary> <compiled_binary>
#   Runs both with full TRACE, diffs stderr streams.
#   Exit 0 = match. Exit 1 = divergence (prints first diff).
```

**Deliverables:**
1. `snobol4harness/monitor/run_monitor.sh` — single-test runner
2. `snobol4harness/monitor/run_monitor_suite.sh` — runs all corpus tests
3. One passing test end-to-end (001_output_string_literal.sno)

**How it works:**
```bash
ORACLE=snobol4
COMPILED=./beauty_full_bin   # or snobol4-tiny binary

# Wrap each .sno with TRACE registrations prepended
cat trace_header.sno $SNO_FILE > /tmp/monitored.sno

# Run both, capture stderr
$ORACLE  /tmp/monitored.sno < /dev/null 2>/tmp/oracle_trace.txt
$COMPILED /tmp/monitored.sno < /dev/null 2>/tmp/compiled_trace.txt

# Diff — first line = first bug
diff /tmp/oracle_trace.txt /tmp/compiled_trace.txt
```

**trace_header.sno** — prepended to every test:
```snobol4
*       MONITOR HEADER — prepended by run_monitor.sh
*       Registers VALUE traces on all user variables via &DUMP trick,
*       and CALL/RETURN traces on all DEFINE'd functions.
*       Works by hooking OUTPUT and tracing key keywords.
        &TRIM = 1
```

**Step-by-step with Lon:**
1. Write `run_monitor.sh`
2. Run on `001_output_string_literal.sno` — confirm oracle trace captured
3. Run compiled binary on same — confirm compiled trace captured
4. Diff — should be empty for a passing test
5. Commit to harness

---

### Sprint M2 — `monitor-value` (session 124)

**Goal:** VALUE traces firing correctly for all assign/ and concat/ tests.

**Tests:** `crosscheck/assign/*.sno` + `crosscheck/concat/*.sno` (14 tests)

**Trace header for this sprint:**
```snobol4
*       VALUE trace all variables known to these tests
        TRACE('BAL','VALUE')
        TRACE('I','VALUE')
        TRACE('S','VALUE')
        TRACE('X','VALUE')
        TRACE('Y','VALUE')
        TRACE('OUTPUT','VALUE')
```

**Pass condition:** `run_monitor_suite.sh assign/ concat/` → 14/14 empty diffs.

**Step-by-step with Lon:**
1. Run suite — see which tests diverge
2. First diverging line in first failing test = exact bug
3. Fix in sno2c/emit_byrd.c or runtime
4. Rerun — confirm fixed
5. Check 106/106 invariant still holds
6. Commit

---

### Sprint M3 — `monitor-control` (session 125)

**Goal:** LABEL traces + goto correctness. control_new/ tests (7 tests).

**Tests:** `crosscheck/control_new/*.sno`

**Trace header addition:**
```snobol4
        TRACE('LOOP','LABEL')
        TRACE('END','LABEL')
```

**Pass condition:** `run_monitor_suite.sh control_new/` → 7/7 empty diffs.

---

### Sprint M4 — `monitor-patterns` (session 126)

**Goal:** Pattern matching correctness. patterns/ + capture/ tests (27 tests).

**Tests:** `crosscheck/patterns/*.sno` + `crosscheck/capture/*.sno`

**Key insight:** Pattern bugs show up as VALUE trace divergences on capture
variables — the `.` and `$` operators assign to variables mid-match.
First wrong assignment = exact node in Byrd box tree that misfired.

**Pass condition:** `run_monitor_suite.sh patterns/ capture/` → 27/27 empty diffs.

---

### Sprint M5 — `monitor-functions` (session 127)

**Goal:** CALL/RETURN traces. functions/ tests (8 tests).

**Tests:** `crosscheck/functions/*.sno`

**Trace header addition:**
```snobol4
        TRACE('DOUBLE','CALL')    TRACE('DOUBLE','RETURN')
        TRACE('FIB','CALL')       TRACE('FIB','RETURN')
*       ... (runner auto-detects DEFINE'd names and traces all)
```

**Auto-detect approach:** `run_monitor.sh` greps each `.sno` for
`DEFINE('funcname` and auto-registers CALL+RETURN traces for every
function found. No manual trace header per test.

**Pass condition:** `run_monitor_suite.sh functions/` → 8/8 empty diffs.

---

### Sprint M6 — `monitor-data` (session 128)

**Goal:** ARRAY, TABLE, DATA types. data/ tests (6 tests) + strings/ (11 tests).

**Tests:** `crosscheck/data/*.sno` + `crosscheck/strings/*.sno`

**Pass condition:** `run_monitor_suite.sh data/ strings/` → 17/17 empty diffs.

---

### Sprint M7 — `monitor-keywords` (session 129)

**Goal:** Built-in predicates, keyword tests. keywords/ tests (11 tests).

**Tests:** `crosscheck/keywords/*.sno`

**Note:** `082_keyword_stcount.sno` — &STCOUNT increments correctly on CSNOBOL4 (verified 2026-03-16 — prior "always 0" claim was wrong).
Skip or special-case this test.

**Pass condition:** `run_monitor_suite.sh keywords/` → 10/10 empty diffs (stcount skipped).

---

### Sprint M8 — `monitor-full` (session 130)

**Goal:** All 152 corpus tests. Zero diffs. **M-MONITOR fires.**

**Tests:** entire `crosscheck/` tree

**Run:**
```bash
bash snobol4harness/monitor/run_monitor_suite.sh \
    /home/claude/snobol4corpus/crosscheck \
    snobol4 \
    ./snobol4-tiny-bin \
    2>monitor_results.txt
grep FAIL monitor_results.txt | wc -l   # must be 0
```

**Pass condition:** 0 failures → **M-MONITOR fires** → commit to all repos → update PLAN.md.

---

## The Runner Design

### `run_monitor.sh` (single test)

```bash
#!/bin/bash
# run_monitor.sh <sno_file> <oracle> <compiled>
# Exit 0 = traces match. Exit 1 = divergence.
SNO=$1; ORACLE=$2; COMPILED=$3
TMP=/tmp/monitor_$$

# Auto-inject trace registrations
python3 inject_traces.py $SNO > $TMP.sno

# Run both
$ORACLE  -f $TMP.sno < /dev/null 2>$TMP.oracle  >/dev/null
$COMPILED   $TMP.sno < /dev/null 2>$TMP.compiled >/dev/null

# Diff
RESULT=$(diff $TMP.oracle $TMP.compiled)
if [ -z "$RESULT" ]; then
    echo "PASS $SNO"
    exit 0
else
    echo "FAIL $SNO"
    echo "$RESULT" | head -5   # first divergence only
    exit 1
fi
```

### `inject_traces.py`

Reads a `.sno` file. Finds all `DEFINE('funcname(` patterns.
Prepends VALUE traces for known variables + CALL/RETURN for all DEFINE'd functions.
Outputs instrumented `.sno` to stdout.

### `run_monitor_suite.sh`

Loops over all `.sno` files in a directory. Calls `run_monitor.sh` for each.
Reports PASS/FAIL count. Stops on first FAIL and prints the diverging trace lines.

---

## Step-By-Step Protocol (Each Sprint with Lon)

1. **Run the suite** for this sprint's test group
2. **Read the first FAIL** — print the diverging trace lines
3. **Identify the bug** — first diverging line names the variable/function/label
4. **Fix** — in `emit_byrd.c` or runtime
5. **Verify** — rerun monitor on that test → PASS
6. **Invariant** — confirm 106/106 still holds
7. **Commit** — both snobol4x and harness
8. **Next test** — repeat until sprint group is all PASS

---

## Invariant During M-MONITOR

106/106 rungs 1–11 must pass after every fix.
Monitor work never breaks existing crosscheck.
If it does: fix the regression before continuing monitor work.

---

*MONITOR.md = L3. Edit here, not in PLAN.md.*
