# TINY.md — snobol4x (L2)

snobol4x: multiple frontends, multiple backends.
**Co-authored by Lon Jones Cherryholmes and Claude Sonnet 4.6.** When any milestone fires, Claude writes the commit.

→ Frontends: [FRONTEND-SNOBOL4.md](FRONTEND-SNOBOL4.md) · [FRONTEND-REBUS.md](FRONTEND-REBUS.md) · [FRONTEND-SNOCONE.md](FRONTEND-SNOCONE.md) · [FRONTEND-ICON.md](FRONTEND-ICON.md) · [FRONTEND-PROLOG.md](FRONTEND-PROLOG.md)
→ Backends: [BACKEND-C.md](BACKEND-C.md) · [BACKEND-X64.md](BACKEND-X64.md) · [BACKEND-NET.md](BACKEND-NET.md) · [BACKEND-JVM.md](BACKEND-JVM.md)
→ Compiler: [IMPL-SNO2C.md](IMPL-SNO2C.md) · Testing: [TESTING.md](TESTING.md) · Rules: [RULES.md](RULES.md) · Monitor: [MONITOR.md](MONITOR.md)
→ Full session history: [SESSIONS_ARCHIVE.md](SESSIONS_ARCHIVE.md)

---

## NOW

**Sprint:** `monitor-ipc` — wire 5-way FIFO IPC; SPITBOL + JVM + NET participants
**HEAD:** `6eebdc3` B-229 (asm-backend)
**Milestone:** M-MONITOR-IPC-5WAY (next to fire)
**Invariants:** 100/106 C (6 pre-existing) · 26/26 ASM

**⚠ CRITICAL NEXT ACTION — Session B-230:**

```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git checkout asm-backend && git pull --rebase origin asm-backend

export CORPUS=/home/claude/snobol4corpus/crosscheck
STOP_ON_FAIL=0 CORPUS=$CORPUS bash test/crosscheck/run_crosscheck.sh   # 100/106
CORPUS=$CORPUS bash test/crosscheck/run_crosscheck_asm.sh               # 26/26

# Goal: M-MONITOR-IPC-5WAY
# Step 1: check if spitbol binary available; if not, build from /home/claude/spitbol-x64/
# Step 2: verify SPITBOL uses same monitor_ipc.so ABI (dlopen/LOAD — confirmed in B-228 research)
# Step 3: add SPITBOL participant to run_monitor.sh
#   - SPITBOL sends TRACE to stdout, not stderr — redirect stdout → FIFO
#   - Or: SPITBOL also supports LOAD() → use monitor_ipc.so directly
# Step 4: add JVM participant (sno2c -jvm → jasmin → java)
# Step 5: add NET participant (sno2c -net → ilasm → mono)
# Step 6: hello PASS all 5 participants → M-MONITOR-IPC-5WAY fires
# Full design → MONITOR.md §IPC Architecture §run_monitor.sh
```

## Last Session Summary

**Session B-229 (2026-03-21) — M-MONITOR-IPC-SO + M-MONITOR-IPC-CSN:**
- Built monitor_ipc.c/.so: MON_OPEN/MON_SEND/MON_CLOSE, lret_t ABI
- Empirically verified CSNOBOL4 string layout: BCDFLD=64, block hdr[0].v=length
- Fixed HOST(4,...) for env var reads; fixed MON_IPC_='1' string vs integer bug
- CSNOBOL4+ASM both write trace via named FIFOs; hello/multi/assign PASS
- Pushed `8bf1c0c` (IPC-SO) + `6eebdc3` (IPC-CSN) to asm-backend

## Active Milestones

| ID | Trigger | Status |
|----|---------|--------|
| M-MONITOR-IPC-SO | monitor_ipc.so built; MON_OPEN/MON_SEND/MON_CLOSE; CSNOBOL4 LOAD() confirmed | ✅ `8bf1c0c` B-229 |
| M-MONITOR-IPC-CSN | inject_traces.py IPC preamble; CSNOBOL4 trace via FIFO; hello PASS | ✅ `6eebdc3` B-229 |
| **M-X64-LOAD** | snobol4ever/x64: `make bootsbl` clean; LOAD()/UNLOAD() end-to-end; SPITBOL test suite passes | ❌ |
| M-MONITOR-IPC-5WAY | all 5 participants via FIFO; hello PASS all 5; no stderr/stdout blending | ❌ |
| M-MONITOR-IPC-TIMEOUT | monitor_collect.py watchdog: FIFO silence > T sec → kill + report | ❌ |
| M-MONITOR-4DEMO | roman+wordcount+treebank pass all 5 | ❌ |

Full milestone history → [PLAN.md](PLAN.md) · Beauty detail → [BEAUTY.md](BEAUTY.md)

---

## Concurrent Sessions

| Session | Branch | Focus |
|---------|--------|-------|
| B-229 | `asm-backend` | monitor-ipc — IPC-SO + IPC-CSN ✅ done |
| x64-fork | `snobol4ever/x64 main` | LOAD() fix — forked spitbol/x64, fixed sysld.c + Makefile; M-X64-LOAD defined |
| J-next | `jvm-backend` | TBD |
| N-next | `net-backend` | TBD |
| F-next | `main` | TBD |
