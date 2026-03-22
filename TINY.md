# TINY.md — snobol4x (L2)

snobol4x: multiple frontends, multiple backends.
**Co-authored by Lon Jones Cherryholmes and Claude Sonnet 4.6.** When any milestone fires, Claude writes the commit.

→ Frontends: [FRONTEND-SNOBOL4.md](FRONTEND-SNOBOL4.md) · [FRONTEND-REBUS.md](FRONTEND-REBUS.md) · [FRONTEND-SNOCONE.md](FRONTEND-SNOCONE.md) · [FRONTEND-ICON.md](FRONTEND-ICON.md) · [FRONTEND-PROLOG.md](FRONTEND-PROLOG.md)
→ Backends: [BACKEND-C.md](BACKEND-C.md) · [BACKEND-X64.md](BACKEND-X64.md) · [BACKEND-NET.md](BACKEND-NET.md) · [BACKEND-JVM.md](BACKEND-JVM.md)
→ Compiler: [IMPL-SNO2C.md](IMPL-SNO2C.md) · Testing: [TESTING.md](TESTING.md) · Rules: [RULES.md](RULES.md) · Monitor: [MONITOR.md](MONITOR.md)
→ Full session history: [SESSIONS_ARCHIVE.md](SESSIONS_ARCHIVE.md)

---

## NOW

**Sprint:** `main` — M-MONITOR-SYNC in progress
**HEAD:** `89fd186` B-252 (main)
**Milestone:** M-MONITOR-SYNC — sync-step barrier protocol; hello PASS all 5 sync = fire
**Invariants:** 106/106 ASM corpus ALL PASS ✅

**⚡ CRITICAL NEXT ACTION — Session B-253 (M-MONITOR-SYNC finish):**

```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git remote set-url origin https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x.git
git pull --rebase origin main

# Setup (if fresh container):
bash setup.sh
mkdir -p /home/claude/x64
ln -sf /home/claude/snobol4x64/bin/sbl /home/claude/x64/bootsbl
cp /home/claude/snobol4x64/monitor_ipc_spitbol.so /home/claude/x64/
gcc -shared -fPIC -O2 -Wall \
  -o test/monitor/monitor_ipc_sync.so test/monitor/monitor_ipc_sync.c

# What's done (B-252):
#   JVM: sno_mon_ack_fd field + sno_mon_init opens MONITOR_ACK_FIFO
#        sno_mon_var writes event then reads ack ('G'=continue, other=exit)
#   NET: net_mon_sw/net_mon_ack static fields + net_mon_init() added
#        net_mon_var rewritten: static StreamWriter, reads ack after write
#   run_monitor_sync.sh: participants launched BEFORE controller (deadlock fix)
#
# Remaining issue: LOAD of monitor_ipc_sync.so fails with error 142
#   Symptoms: snobol4 -f instr.sno at line 20 "load function does not exist"
#   Likely cause: MONITOR_SO env var path not reaching CSNOBOL4 subprocess
#                 OR snobol4 LOAD() needs absolute path / SNOLIB search
#   Diagnosis: check HOST(4,'MONITOR_SO') returns correct path in subprocess
#              try: MONITOR_SO=$(pwd)/test/monitor/monitor_ipc_sync.so
#   Fix: confirm LOAD works, then test hello PASS all 5 sync → fire M-MONITOR-SYNC

# Test run:
INC=/home/claude/snobol4corpus/programs/inc X64_DIR=/home/claude/x64 \
  MONITOR_TIMEOUT=5 timeout 60 bash test/monitor/run_monitor_sync.sh \
  /home/claude/snobol4corpus/crosscheck/hello/hello.sno
```

## Last Session Summary

**Session B-252 (2026-03-22) — M-MONITOR-SYNC wiring:**
- JVM: added `sno_mon_ack_fd` static field; `sno_mon_init` opens both MONITOR_FIFO+MONITOR_ACK_FIFO; `sno_mon_var` blocks on ack after each write, exits on non-G
- NET: added `net_mon_sw`/`net_mon_ack` static fields; `net_mon_init()` new method (static-open both FIFOs, called from main); `net_mon_var` rewritten (no per-call StreamWriter, reads ack)
- `run_monitor_sync.sh`: fixed launch-order deadlock — participants start first, then controller opens FIFOs
- Remaining: LOAD error 142 on `monitor_ipc_sync.so` path — needs one more debug step
- 106/106 ALL PASS unchanged

## Active Milestones

| ID | Status |
|----|--------|
| M-MONITOR-SYNC     | ❌ one step away — LOAD path fix + hello PASS |
| M-MONITOR-4DEMO    | ❌ blocked on M-MONITOR-SYNC + 4 bug milestones |
| M-MON-BUG-NET-TIMEOUT | ❌ (resolved by static-open in B-252) |
| M-MON-BUG-SPL-EMPTY   | ❌ |
| M-MON-BUG-ASM-WPAT    | ❌ |
| M-MON-BUG-JVM-WPAT    | ❌ |

## Concurrent Sessions

| Session | Branch | Focus |
|---------|--------|-------|
| B-next | `main` | M-MONITOR-SYNC finish |
| F-next | `main` | TBD |
