# TINY.md — snobol4x (L2)

snobol4x: multiple frontends, multiple backends.
**Co-authored by Lon Jones Cherryholmes and Claude Sonnet 4.6.** When any milestone fires, Claude writes the commit.

→ Frontends: [FRONTEND-SNOBOL4.md](FRONTEND-SNOBOL4.md) · [FRONTEND-REBUS.md](FRONTEND-REBUS.md) · [FRONTEND-SNOCONE.md](FRONTEND-SNOCONE.md) · [FRONTEND-ICON.md](FRONTEND-ICON.md) · [FRONTEND-PROLOG.md](FRONTEND-PROLOG.md)
→ Backends: [BACKEND-C.md](BACKEND-C.md) · [BACKEND-X64.md](BACKEND-X64.md) · [BACKEND-NET.md](BACKEND-NET.md) · [BACKEND-JVM.md](BACKEND-JVM.md)
→ Compiler: [IMPL-SNO2C.md](IMPL-SNO2C.md) · Testing: [TESTING.md](TESTING.md) · Rules: [RULES.md](RULES.md) · Monitor: [MONITOR.md](MONITOR.md)
→ Full session history: [SESSIONS_ARCHIVE.md](SESSIONS_ARCHIVE.md)

---

## NOW

**Sprint:** `monitor-scaffold` — build two-way sync-step monitor (CSNOBOL4 + ASM)
**HEAD:** `7f44985` B-226 (asm-backend) · `b67d0b1` J-212 (jvm-backend) · `2c417d7` N-209 (net-backend) · `6495074` F-210 (main)
**Milestone:** M-MONITOR-SCAFFOLD (next to fire)
**Invariants:** 100/106 C (6 pre-existing) · 26/26 ASM

**⚠ CRITICAL NEXT ACTION — Session B-227:**

Sprint `monitor-scaffold`. All work in `snobol4x/test/monitor/` on `asm-backend` branch.

```bash
# Setup
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git checkout asm-backend && git pull --rebase origin asm-backend

# Verify invariants before any work
export CORPUS=/home/claude/snobol4corpus/crosscheck
STOP_ON_FAIL=0 CORPUS=$CORPUS bash test/crosscheck/run_crosscheck.sh      # 100/106
CORPUS=$CORPUS bash test/crosscheck/run_crosscheck_asm.sh                  # 26/26

# Build sno2c
apt-get install -y libgc-dev && make -C src/sno2c

# Sprint goal: create these files
mkdir -p test/monitor
# 1. test/monitor/tracepoints.conf      — INCLUDE/EXCLUDE/IGNORE rules (regex-based)
# 2. test/monitor/inject_traces.py      — reads .sno + conf -> instrumented .sno
# 3. test/monitor/run_monitor.sh        — CSNOBOL4 + ASM only for M-MONITOR-SCAFFOLD
# 4. test/monitor/normalize_trace.py   — ignore-points; SPITBOL normalization (M-MONITOR-3WAY)

# M-MONITOR-SCAFFOLD pass condition:
SNO=/home/claude/snobol4corpus/crosscheck/hello/001_output_string_literal.sno
bash test/monitor/run_monitor.sh $SNO
# Must exit 0; CSNOBOL4 and ASM trace streams non-empty and matching
```

**Step-by-step:**
1. Write `tracepoints.conf` — INCLUDE `*` (functions + vars), EXCLUDE &RANDOM/&TIME/&DATE; IGNORE &TERMINAL tty pattern, IGNORE DATATYPE case
2. Write `inject_traces.py` — scan DEFINE( for functions (CALL+RETURN), scan LHS `=` for vars (VALUE); apply regex INCLUDE/EXCLUDE; inject TRACE() calls
3. Write `run_monitor.sh` — inject → run CSNOBOL4 → run ASM → diff streams → PASS/FAIL
4. Test on `001_output_string_literal.sno` → PASS
5. Commit → M-MONITOR-SCAFFOLD fires → update PLAN.md dashboard
6. Continue to M-MONITOR-3WAY: add SPITBOL + `normalize_trace.py`
7. Then M-MONITOR-5WAY: add JVM + NET
8. Then M-MONITOR-4DEMO: demo programs
9. Then M-BEAUTY-* series: 19 subsystem drivers → M-BEAUTIFY-BOOTSTRAP

**Full monitor plan → [MONITOR.md](MONITOR.md) · Beauty subsystem plan → [BEAUTY.md](BEAUTY.md)**

## Last Session Summary

**Session (strategize-3, 2026-03-21) — Full monitor + beauty piecemeal plan:**
- Refined tracepoints.conf: regex-based INCLUDE/EXCLUDE, four trace kinds (VALUE/CALL/RETURN/LABEL), scope qualifiers (name / func/var)
- Ignore-points: suppress known-diff patterns without stopping execution
- Monitor participant sequence: start 2-way (CSNOBOL4+ASM), grow to 3-way (+SPITBOL), then 5-way (+JVM+NET) — separate milestones M-MONITOR-SCAFFOLD → M-MONITOR-3WAY → M-MONITOR-5WAY
- Beauty piecemeal: 19 per-include-file drivers in snobol4x/test/beauty/, Gimpel corpus as semantic cross-validation; one M-BEAUTY-* milestone per include file
- New doc: BEAUTY.md (L3) — driver format, 19-milestone map, dependency order, Gimpel cross-refs, EXCLUDE noise-reduction protocol
- Updated MONITOR.md: regex trace-point design, Sprint M4 rewritten as 19-sprint beauty-subsystems series
- Updated PLAN.md: M-MONITOR-5WAY split into SCAFFOLD→3WAY→5WAY; 19 M-BEAUTY-* milestones added; BEAUTY.md in L3 table
- No code changes. No invariant runs (strategy session only).

## Active Milestones

| ID | Trigger | Status |
|----|---------|--------|
| M-MONITOR-SCAFFOLD | test/monitor/ exists; CSNOBOL4 + ASM; one test passes | ❌ |
| M-MONITOR-3WAY | + SPITBOL; normalize_trace.py; one test passes all 3 | ❌ |
| M-MONITOR-5WAY | + JVM + NET; one test passes all 5 | ❌ |
| M-MONITOR-4DEMO | roman+wordcount+treebank pass all 5 | ❌ |
| M-BEAUTY-GLOBAL | global.sno driver passes | ❌ |
| M-BEAUTY-IS … M-BEAUTY-TRACE | 18 more subsystem drivers | ❌ |
| M-BEAUTIFY-BOOTSTRAP | beauty.sno fixed point on all 3 backends | ❌ |

Full milestone history → [PLAN.md](PLAN.md) · Beauty detail → [BEAUTY.md](BEAUTY.md)

---

## Concurrent Sessions

| Session | Branch | Focus |
|---------|--------|-------|
| B-227 | `asm-backend` | monitor-scaffold — Sprint M1 |
| J-next | `jvm-backend` | TBD |
| N-next | `net-backend` | TBD |
| F-next | `main` | TBD |

Per RULES.md: `git pull --rebase` before every push. Update only your row in PLAN.md NOW table.
