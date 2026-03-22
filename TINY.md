# TINY.md — snobol4x (L2)

snobol4x: multiple frontends, multiple backends.
**Co-authored by Lon Jones Cherryholmes and Claude Sonnet 4.6.** When any milestone fires, Claude writes the commit.

→ Frontends: [FRONTEND-SNOBOL4.md](FRONTEND-SNOBOL4.md) · [FRONTEND-REBUS.md](FRONTEND-REBUS.md) · [FRONTEND-SNOCONE.md](FRONTEND-SNOCONE.md) · [FRONTEND-ICON.md](FRONTEND-ICON.md) · [FRONTEND-PROLOG.md](FRONTEND-PROLOG.md)
→ Backends: [BACKEND-C.md](BACKEND-C.md) · [BACKEND-X64.md](BACKEND-X64.md) · [BACKEND-NET.md](BACKEND-NET.md) · [BACKEND-JVM.md](BACKEND-JVM.md)
→ Compiler: [IMPL-SNO2C.md](IMPL-SNO2C.md) · Testing: [TESTING.md](TESTING.md) · Rules: [RULES.md](RULES.md) · Monitor: [MONITOR.md](MONITOR.md)
→ Full session history: [SESSIONS_ARCHIVE.md](SESSIONS_ARCHIVE.md)

---

## NOW

**Sprint:** `main` — MONITOR sync-step redesign; M-MONITOR-SYNC in progress
**HEAD:** `e2c4fb5` B-249 (main) — no commit yet this session
**Milestone:** M-MONITOR-SYNC (sync-step barrier protocol replacing async M-MONITOR-IPC-5WAY)
**Invariants:** 106/106 ASM corpus ALL PASS ✅

**⚡ CRITICAL NEXT ACTION — Session B-251 (M-MONITOR-SYNC):**

```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git remote set-url origin https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x.git
git pull --rebase origin main

# Sync-step IPC already written this session:
#   test/monitor/monitor_ipc_sync.c  — MON_OPEN(evt,ack), MON_SEND blocks on ack read
#   test/monitor/monitor_ipc_sync.so — built OK
#   test/monitor/monitor_sync.py     — barrier controller
#   test/monitor/run_monitor_sync.sh — harness
#   test/monitor/inject_traces.py    — preamble updated for two-arg MON_OPEN
#   test/beauty/global/driver.sno    — first beauty driver (oracle: 20 PASSes)
#   test/beauty/global/driver.ref    — oracle reference output
#
# NEXT: get run_monitor_sync.sh working end-to-end on hello or global driver
# SPITBOL needs monitor_ipc_spitbol_sync.so (same two-arg ABI)
# ASM/JVM/NET backends need MONITOR_ACK_FIFO env var wired into comm_var / sno_mon_init
# Fire M-MONITOR-SYNC when hello PASS all 5 sync-step
```

## Last Session Summary

**Session B-250 (2026-03-22) — M-MONITOR-4DEMO diagnosis; 4 bug milestones filed:**
- Ran wordcount/treebank/claws5 through 5-way monitor; all three programs FAIL on NET (timeout), FAIL on ASM+JVM (WPAT divergence), ORACLE-DIFF on CSN vs SPL
- Root causes identified and documented as 4 new milestones (M-MON-BUG-NET-TIMEOUT, M-MON-BUG-SPL-EMPTY, M-MON-BUG-ASM-WPAT, M-MON-BUG-JVM-WPAT)
- No source changes this session — bugs are in backends, MONITOR infrastructure blocked; protocol: separate session per bug milestone
- 106/106 ALL PASS unchanged at handoff

## Active Milestones

| ID | Status |
|----|--------|
| M-MONITOR-4DEMO        | ❌ blocked on 4 bug milestones below |
| M-MON-BUG-NET-TIMEOUT  | ❌ next |
| M-MON-BUG-SPL-EMPTY    | ❌ |
| M-MON-BUG-ASM-WPAT     | ❌ |
| M-MON-BUG-JVM-WPAT     | ❌ |

## Concurrent Sessions

| Session | Branch | Focus |
|---------|--------|-------|
| B-next | `main` | M-MON-BUG-NET-TIMEOUT |
| F-next | `main` | TBD |
