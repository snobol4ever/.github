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
**Milestone:** M-X64-S1 (next to fire)
**Invariants:** 97/106 ASM corpus (9 known failures: 022, 055, 064, cross, word1-4, wordcount)

**⚠ CRITICAL NEXT ACTION — Session B-231:**

```bash
# Repo: snobol4ever/x64  (NOT snobol4x)
cd /home/claude/x64
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git pull --rebase origin main

# Goal: M-X64-S1 — syslinux.c compiles clean; make bootsbl succeeds
# Context: syslinux.c callef/loadef/nextef/unldef use missing struct ef fields
#   xnhand → xndta[0], xnpfn → xndta[1] (already fixed in B-230)
#   Remaining errors: MINIMAL_ALOST/ALOCS/ALLOC macros, TYPET, MINFRAME, ARGPUSHSIZE
#   mword declared as int in port.h but used as long — fix to long/word
# Step 1: audit all compile errors from: make bootsbl 2>&1 | grep error:
# Step 2: fix each macro/type mismatch in syslinux.c and port.h
# Step 3: make bootsbl succeeds → M-X64-S1 fires
# Step 4: write minimal SpitbolCLib (spl_add/spl_strlen) — matches snobol4dotnet fixture
# Step 5: LOAD('spl_add(INTEGER,INTEGER)INTEGER','libspl.so') → spl_add(3,4)=7 → M-X64-S2
# Tests: snobol4dotnet/TestSnobol4/Function/FunctionControl/LoadSpecTests.cs as oracle
# Full sprint design → BACKEND-X64.md §M-X64-FULL
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
| **M-X64-S1** | syslinux.c compiles clean; `make bootsbl` succeeds | ❌ |
| **M-X64-S2** | LOAD end-to-end; spl_add(3,4)=7 | ❌ |
| **M-X64-S3** | UNLOAD lifecycle; reload; double-unload safe | ❌ |
| **M-X64-S4** | SNOLIB; errors 139/140/141; monitor_ipc.so in SPITBOL | ❌ |
| **M-X64-FULL** | S1–S4 done; SPITBOL = monitor participant | ❌ |
| M-MONITOR-IPC-5WAY | all 5 participants via FIFO; hello PASS all 5; no stderr/stdout blending | ❌ |
| M-MONITOR-IPC-TIMEOUT | monitor_collect.py watchdog: FIFO silence > T sec → kill + report | ❌ |
| M-MONITOR-4DEMO | roman+wordcount+treebank pass all 5 | ❌ |

Full milestone history → [PLAN.md](PLAN.md) · Beauty detail → [BEAUTY.md](BEAUTY.md)

---

## Concurrent Sessions

| Session | Branch | Focus |
|---------|--------|-------|
| B-229 | `asm-backend` | monitor-ipc — IPC-SO + IPC-CSN ✅ done |
| x64-fork | `snobol4ever/x64 main` | M-X64-S1: fix syslinux.c xndta fields; make bootsbl |
| J-next | `jvm-backend` | TBD |
| N-next | `net-backend` | TBD |
| F-next | `main` | TBD |
