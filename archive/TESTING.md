# TESTING.md — Four-Paradigm TDD Protocol

**The goal:** `beauty_full_bin` reads `beauty.sno`, diff vs SPITBOL oracle is empty. **M-BEAUTY-FULL.**
**Oracle:** SPITBOL x64 (`/home/claude/x64/bin/sbl`). CSNOBOL4 = Silly track only.
**The invariant:** 106/106 rungs 1–11 pass after every commit. Regression = rollback.

---

## The Corpus Ladder (all repos — TINY, JVM, DOTNET)

```
Rung 1:  output      — OUTPUT = 'hello'
Rung 2:  assign      — X = 'foo', null assign
Rung 3:  concat      — OUTPUT = 'a' 'b'
Rung 4:  arith       — OUTPUT = 1 + 2
Rung 5:  control     — goto, :S(), :F()
Rung 6:  patterns    — LIT, ANY, SPAN, ARB, ARBNO, POS, RPOS
Rung 7:  capture     — . and $ operators
Rung 8:  strings     — SIZE, SUBSTR, REPLACE, DUPL
Rung 9:  keywords    — IDENT, DIFFER, GT/LT/EQ, DATATYPE
Rung 10: functions   — DEFINE, RETURN, FRETURN, recursion
Rung 11: data        — ARRAY, TABLE, DATA types
Rung 12: beauty.sno  — tiny inputs → full self-beautification
```
Rule: stop at first failing rung. Fix. Retest. Never skip.

---

## Four Paradigms

### Paradigm 1 — Crosscheck (corpus diff)
What: compile .sno → binary, run, diff output vs .ref oracle.
Catches: wrong output — any observable bug.
Tool: `test/crosscheck/run_crosscheck.sh` (rungs 1–11), `test/crosscheck/run_beauty.sh` (rung 12).
```bash
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh   # must be 106/106
bash test/crosscheck/run_beauty.sh                       # rung 12
```

### Paradigm 2 — Probe (&STLIMIT frame-by-frame)
What: run program N times at &STLIMIT=1..N with &DUMP=2. Show what changed each step.
Catches: exactly WHERE divergence first appears — which variable, which statement.
Tool: `harness/probe/probe.py`
```bash
python3 /home/claude/harness/probe/probe.py --oracle spitbol --max 200 failing.sno
```
When to use: Paradigm 1 finds failure → Paradigm 2 locates statement.

### Paradigm 3 — Monitor (TRACE double-trace diff)
What: TRACE('fn','CALL'/'RETURN'/'VALUE') hooks in beauty.sno. Both oracle and compiled
emit same event stream. Diff stream event by event. First divergence = root cause.
Tool: `corpus/programs/beauty/beauty_trace.sno` + `test/crosscheck/monitor_beauty.sh`
```bash
spitbol -b beauty_trace.sno < input.sno 2>oracle_trace.txt
./beauty_full_bin_trace < input.sno 2>compiled_trace.txt
diff oracle_trace.txt compiled_trace.txt | head -20
```
When to use: Paradigm 2 finds divergence in recursion → Paradigm 3 shows call/return stream.

### Paradigm 4 — Triangulate (cross-engine)
What: same program through SPITBOL + compiled. Compiled differs → our bug.
Tool: `test/crosscheck/triangulate_beauty.sh`
```bash
/home/claude/x64/bin/sbl -b $BEAUTY < $BEAUTY > oracle_spl.txt
./beauty_full_bin < $BEAUTY > compiled_out.txt
diff oracle_spl.txt compiled_out.txt   # empty = M-BEAUTY-FULL
```
Note: SPITBOL x64 is the sole oracle. All `.ref` files are generated from SPITBOL.

---

## Sprint Map to M-BEAUTY-FULL

| Sprint | Paradigm | Milestone trigger |
|--------|----------|------------------|
| `monitor-scaffold` | Monitor | runner + inject_traces.py, 1 test passing |
| `monitor-value` | Monitor | assign/ + concat/ 14/14 → |
| `monitor-control` | Monitor | control_new/ 7/7 → |
| `monitor-patterns` | Monitor | patterns/ + capture/ 27/27 → |
| `monitor-functions` | Monitor | functions/ 8/8 → |
| `monitor-data` | Monitor | data/ + strings/ 17/17 → |
| `monitor-keywords` | Monitor | keywords/ 10/10 → |
| `monitor-full` | Monitor | all 152 corpus tests zero diffs → **M-MONITOR** |
| `beauty-crosscheck` | Crosscheck | beauty/140_self passes → **M-BEAUTY-CORE** |
| `beauty-triangulate` | Triangulate | Empty diff → **M-BEAUTY-FULL** |

## Rung 12 Test Format

Tests live in `corpus/crosscheck/beauty/`:
- `NNN_name.input` — SNOBOL4 snippet to pipe to beauty_full_bin
- `NNN_name.ref` — oracle output: `spitbol -b $BEAUTY < NNN_name.input`

Test progression: 101_comment → 102_output → 103_assign → 104_label → 105_goto →
109_multi → 120_real_prog → 130_inc_file → 140_self (M-BEAUTY-CORE).

## Oracle Index

| System | Version | Author | Role | Invocation |
|--------|---------|--------|------|------------|
| SPITBOL x64 | 4.0f | Dewar / Shields | **Sole execution oracle** (D-001, D-005) | `/home/claude/x64/bin/sbl -b file.sno` |
| CSNOBOL4 | 2.3.3 | Philip L. Budne | **SOURCE REFERENCE ONLY** — v311.sil / snobol4.c for Silly SNOBOL4. Never executed as oracle. Lacks FENCE. | — do not invoke — |
| SPITBOL x32 | — | Dewar | Reference (32-bit — not runnable in container) | `spitbol file.sno` |
| SNOBOL5 | beta 2024-08-29 | Viktors Berstis | 64-bit native SIL port | `snobol5 file.sno` |

| System | Source / Download | GitHub |
|--------|-------------------|--------|

| SPITBOL x64 | https://github.com/spitbol/x64 | [`spitbol/x64`](https://github.com/spitbol/x64) |
| SPITBOL x32 | https://github.com/snobol4ever/x32 | [`snobol4ever/x32`](https://github.com/snobol4ever/x32) — **our fork** of [`hardbol/spitbol`](https://github.com/hardbol/spitbol) |
| SNOBOL5 | Linux binary: https://snobol5.org/snobol5 · Docs: https://snobol5.org/snobol5.htm | No GitHub — binary only, no public source |

Step-by-step build: `harness/oracles/spitbol/BUILD.md`

**SNOBOL5 notes:** 64-bit ints/strings. `&CASE` → Error 7. `CODE()` broken. OPSYN single-char only. Not a drop-in oracle.

---

## Sprint: `oracle-verify` — Verify the Keyword Grid (Session 124)

**Goal:** Every `?` and every unverified cell in the keyword grid below becomes ✅ or ❌, confirmed by live test. Every oracle must have ≥1 working probe statement counter.

**Deliverables:**
1. SPITBOL installed from snobol4ever/x64 (via SESSION_SETUP.sh)
2. SPITBOL x64 built from source (needs `x64-main.zip` upload)
3. SNOBOL5 located, installed if available, or documented as unavailable
4. `oracles/verify.sno` — single test program that probes all keywords and emits a result line per keyword
5. All `?` cells in the grid below replaced with live-tested ✅ or ❌
6. `&STCOUNT` is portable across SPITBOL versions
7. SNOBOL5 probe counter situation resolved: `&STNO`, `&LASTNO`, or neither?
8. Commit to harness with updated grid

**verify.sno — probe program:**
```snobol4
*       verify.sno — oracle keyword verification
*       Run: spitbol -b verify.sno  (or snobol5)
*       Each line of output: KEYWORD = value  OR  KEYWORD = FAIL

        &STLIMIT = 100000

*       &STCOUNT
        X = &STCOUNT
        OUTPUT = '&STCOUNT = ' X

*       &STEXEC is CSNOBOL4-only — do not use
        X = &STEXEC                                         :F(NO_STEXEC)
        OUTPUT = '&STEXEC = ' X                             :(DONE_STEXEC)
NO_STEXEC
        OUTPUT = '&STEXEC = FAIL'
DONE_STEXEC

*       &STNO
        X = &STNO                                           :F(NO_STNO)
        OUTPUT = '&STNO = ' X                               :(DONE_STNO)
NO_STNO
        OUTPUT = '&STNO = FAIL'
DONE_STNO

*       &LASTNO
        X = &LASTNO                                         :F(NO_LASTNO)
        OUTPUT = '&LASTNO = ' X                             :(DONE_LASTNO)
NO_LASTNO
        OUTPUT = '&LASTNO = FAIL'
DONE_LASTNO

*       &DUMP=2 — tested by checking &DUMP is writable
        &DUMP = 2
        OUTPUT = '&DUMP = ' &DUMP

*       &ANCHOR, &TRIM, &FULLSCAN defaults
        OUTPUT = '&ANCHOR = ' &ANCHOR
        OUTPUT = '&TRIM = ' &TRIM
        OUTPUT = '&FULLSCAN = ' &FULLSCAN

        END
```

**Pass condition:** every keyword row in the grid has a live result. No `?` remaining. Each oracle has ≥1 cell in {`&STCOUNT`, `&STEXEC`, `&STNO`, `&LASTNO`} that returns a non-zero-always value.

**Build steps:**
```bash
# SPITBOL x64 — clone snobol4ever/x64, binary is pre-built at x64/bin/sbl
git clone https://TOKEN@github.com/snobol4ever/x64 /home/claude/x64
# Oracle: /home/claude/x64/bin/sbl -b file.sno
# CSNOBOL4 = Silly track only. See SESSION-silly-snobol4.md.

# SNOBOL5 — prebuilt binary, no build required
wget -O /usr/local/bin/snobol5 https://snobol5.org/snobol5
chmod +x /usr/local/bin/snobol5
```

---

## Oracle Keyword & TRACE Reference

Every cell proven by live test on 2026-03-10. SPITBOL-x32 not runnable in container (32-bit execution disabled) — values inferred from source.

### Keywords

All cells marked ✅/❌ verified by live test 2026-03-16 on CSNOBOL4 2.3.3, SPITBOL x64 4.0f, SNOBOL5 beta 2024-08-29. SPITBOL-x32 inferred.

| Keyword | CSNOBOL4 | SPITBOL-x64 | SPITBOL-x32 | SNOBOL5 | Use for portability |
|---------|:--------:|:-----------:|:-----------:|:-------:|---------------------|
| `&STLIMIT` | ✅ -1 (unlimited) | ✅ MAX_INT | ✅ (inferred) | ✅ | ✅ primary probe/abort tool — works everywhere |
| `&STCOUNT` | ✅ **increments** | ✅ increments | ✅ (inferred) | ✅ increments | ✅ portable counter — **prior "always 0" was wrong** |
| `&STEXEC` | ✅ increments | ❌ error 251 | ❌ | ❌ | ❌ CSNOBOL4-only |
| `&STNO` | ✅ current stmt# | ✅ current stmt# | ✅ (inferred) | ✅ current stmt# | ✅ works on all three live oracles |
| `&LASTNO` | ✅ same as &STNO | ✅ same as &STNO | ✅ (inferred) | ✅ same as &STNO | ✅ works everywhere |
| `&DUMP=2` fires at `&STLIMIT` | ✅ | ✅ | ? | ✅ | ✅ safe to use |
| `&ANCHOR` default | 0 | 0 | ? | 0 | ✅ consistent — 0 on all live oracles |
| `&TRIM` default | 0 | **1** | ? | 0 | ⚠️ SPITBOL differs — set explicitly |
| `&FULLSCAN` default | 0 | **1** | ? | 0 | ⚠️ SPITBOL differs — set explicitly |
| `&MAXLNGTH` | 4G | 16M | 16M | 64-bit | ⚠️ all differ |
| TRACE output stream | stderr | **stdout** | stdout | stderr | ⚠️ redirect per oracle |

### TRACE types

| TRACE call | CSNOBOL4 | SPITBOL-x64 | SPITBOL-x32 | SNOBOL5 | Use for portability |
|-----------|:--------:|:-----------:|:-----------:|:-------:|---------------------|
| `TRACE(var,'VALUE')` | ✅ | ✅ | ✅ (inferred) | ✅ | ✅ primary monitor tool |
| `TRACE(fn,'CALL')` | ✅ | ✅ | ✅ (inferred) | ✅ | ✅ |
| `TRACE(fn,'RETURN')` | ✅ | ✅ | ✅ (inferred) | ✅ | ✅ |
| `TRACE(fn,'FUNCTION')` | ✅ | ✅ | ✅ (inferred) | ✅ | ✅ |
| `TRACE(label,'LABEL')` | ✅ | ✅ | ✅ (inferred) | ✅ | ✅ |
| `TRACE('STCOUNT','KEYWORD')` | ✅ | ✅ | ? | ✅ | ✅ portable per-statement trace |
| `TRACE('STNO','KEYWORD')` | ✅ at `BREAKPOINT(n,1)` stmts only | ❌ error 198 | ❌ | ❌ silent | ❌ CSNOBOL4-only, avoid |
| `TRACE(...,'KEYWORD')` (general) | non-functional | error 198 | error 198 | ? | ❌ never use |

### TRACE output format

| Oracle | Format |
|--------|--------|

| SPITBOL-x64 | `****N*******  event` |
| SNOBOL5 | `    STATEMENT N: EVENT,TIME = T` |

Monitor pipe reader must normalize per oracle — all carry statement number and event description.

---

## Session Start Checklist

```bash
cd /home/claude/one4all
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
apt-get install -y libgc-dev && make -C src/scrip-cc
mkdir -p /home/corpus
ln -sf /home/claude/corpus/crosscheck /home/corpus/crosscheck
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh   # must be 106/106 before any work

# Build beauty_full_bin
RT=src/runtime; INC=/home/claude/corpus/programs/inc
BEAUTY=/home/claude/corpus/programs/beauty/beauty.sno
src/scrip-cc/scrip-cc -trampoline -I$INC $BEAUTY > beauty_full.c
gcc -O0 -g beauty_full.c $RT/snobol4/snobol4.c $RT/snobol4/mock_includes.c \
    $RT/snobol4/snobol4_pattern.c $RT/mock_engine.c \
    -I$RT/snobol4 -I$RT -Isrc/scrip-cc -lgc -lm -w -o beauty_full_bin
```

---

## M-SPITBOL-BEAUTY — Fix SPITBOL error 021 on beauty.sno

**Status:** 🔲 Open  
**Error:** SPITBOL exits with error 021 ("Function called by name returned a value") when running beauty.sno end-to-end.  
**Root cause:** beauty.sno uses functions that are called by name (NRETURN path); SPITBOL enforces that name-called functions must not return values. CSNOBOL4 was lenient on this. SPITBOL is strict.  
**Fix:** Identify the offending function(s) in beauty.sno (or its includes), change RETURN to NRETURN/FRETURN as appropriate, or restructure the call sites.  
**Gate:** `spitbol -b beauty.sno < beauty.sno > /tmp/spt.txt` exits 0 with non-empty output.  
**Fires when:** beauty.sno passes SPITBOL end-to-end. Then remove all "documented exception" notes and update `.ref` oracle to SPITBOL output.  
**Impact:** Removes the last reason CSNOBOL4 was considered "necessary". All `.ref` files become pure SPITBOL.
