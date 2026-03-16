# TESTING.md — Four-Paradigm TDD Protocol

**The goal:** `beauty_full_bin` reads `beauty.sno`, diff vs CSNOBOL4 oracle is empty. **M-BEAUTY-FULL.**
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
Tool: `SNOBOL4-harness/probe/probe.py`
```bash
python3 /home/claude/SNOBOL4-harness/probe/probe.py --oracle csnobol4 --max 200 failing.sno
```
When to use: Paradigm 1 finds failure → Paradigm 2 locates statement.

### Paradigm 3 — Monitor (TRACE double-trace diff)
What: TRACE('fn','CALL'/'RETURN'/'VALUE') hooks in beauty.sno. Both oracle and compiled
emit same event stream. Diff stream event by event. First divergence = root cause.
Tool: `SNOBOL4-corpus/programs/beauty/beauty_trace.sno` + `test/crosscheck/monitor_beauty.sh`
```bash
snobol4 -f -P256k -I$INC beauty_trace.sno < input.sno 2>oracle_trace.txt
./beauty_full_bin_trace < input.sno 2>compiled_trace.txt
diff oracle_trace.txt compiled_trace.txt | head -20
```
When to use: Paradigm 2 finds divergence in recursion → Paradigm 3 shows call/return stream.

### Paradigm 4 — Triangulate (cross-engine)
What: same program through CSNOBOL4 + SPITBOL + compiled. Two oracles agree, compiled
differs → our bug. Two oracles disagree → semantic edge case, check Gimpel §7.
Tool: `test/crosscheck/triangulate_beauty.sh`
```bash
snobol4 -f -P256k -I$INC $BEAUTY < $BEAUTY > oracle_csn.txt
./beauty_full_bin < $BEAUTY > compiled_out.txt
diff oracle_csn.txt compiled_out.txt   # empty = M-BEAUTY-FULL
```
Note: SPITBOL excluded from full beauty.sno (error 021 at END). CSNOBOL4 is primary oracle.

---

## Sprint Map to M-BEAUTY-FULL

| Sprint | Paradigm | Milestone trigger |
|--------|----------|------------------|
| `diag1-corpus` | Crosscheck | 35/35 PASS all backends → **M-DIAG1** |
| `beauty-crosscheck` | Crosscheck | beauty/140_self passes → **M-BEAUTY-CORE** |
| `beauty-probe` | Probe | All crosscheck failures diagnosed + fixed |
| `beauty-monitor` | Monitor | Trace streams match all test inputs |
| `beauty-triangulate` | Triangulate | Empty diff → **M-BEAUTY-FULL** |

## Rung 12 Test Format

Tests live in `SNOBOL4-corpus/crosscheck/beauty/`:
- `NNN_name.input` — SNOBOL4 snippet to pipe to beauty_full_bin
- `NNN_name.ref` — oracle output: `snobol4 -f -P256k -I$INC $BEAUTY < NNN_name.input`

Test progression: 101_comment → 102_output → 103_assign → 104_label → 105_goto →
109_multi → 120_real_prog → 130_inc_file → 140_self (M-BEAUTY-CORE).

## Session Start Checklist

```bash
cd /home/claude/SNOBOL4-tiny
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
apt-get install -y libgc-dev && make -C src/sno2c
mkdir -p /home/SNOBOL4-corpus
ln -sf /home/claude/SNOBOL4-corpus/crosscheck /home/SNOBOL4-corpus/crosscheck
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh   # must be 106/106 before any work

# Build beauty_full_bin
RT=src/runtime; INC=/home/claude/SNOBOL4-corpus/programs/inc
BEAUTY=/home/claude/SNOBOL4-corpus/programs/beauty/beauty.sno
src/sno2c/sno2c -trampoline -I$INC $BEAUTY > beauty_full.c
gcc -O0 -g beauty_full.c $RT/snobol4/snobol4.c $RT/snobol4/mock_includes.c \
    $RT/snobol4/snobol4_pattern.c $RT/mock_engine.c \
    -I$RT/snobol4 -I$RT -Isrc/sno2c -lgc -lm -w -o beauty_full_bin
```
