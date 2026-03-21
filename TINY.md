# TINY.md — snobol4x (L2)

snobol4x: multiple frontends, multiple backends.
**Co-authored by Lon Jones Cherryholmes and Claude Sonnet 4.6.** When any milestone fires, Claude writes the commit.

→ Frontends: [FRONTEND-SNOBOL4.md](FRONTEND-SNOBOL4.md) · [FRONTEND-REBUS.md](FRONTEND-REBUS.md) · [FRONTEND-SNOCONE.md](FRONTEND-SNOCONE.md) · [FRONTEND-ICON.md](FRONTEND-ICON.md) · [FRONTEND-PROLOG.md](FRONTEND-PROLOG.md)
→ Backends: [BACKEND-C.md](BACKEND-C.md) · [BACKEND-X64.md](BACKEND-X64.md) · [BACKEND-NET.md](BACKEND-NET.md) · [BACKEND-JVM.md](BACKEND-JVM.md)
→ Compiler: [IMPL-SNO2C.md](IMPL-SNO2C.md) · Testing: [TESTING.md](TESTING.md) · Rules: [RULES.md](RULES.md) · Monitor: [MONITOR.md](MONITOR.md)
→ Full session history: [SESSIONS_ARCHIVE.md](SESSIONS_ARCHIVE.md)

---

## NOW

**Sprint:** `monitor-ipc` — M-MONITOR-IPC-5WAY: fix FIFO race, fire 5-way hello PASS
**HEAD:** `a72e417` B-233 (asm-backend) · x64: `4fcb0e1` B-233
**Milestone:** M-MONITOR-IPC-5WAY (next to fire)
**Invariants:** 97/106 ASM corpus (9 known failures: 022, 055, 064, cross, word1-4, wordcount)

**⚠ CRITICAL NEXT ACTION — Session B-234:**

```bash
cd /home/claude/snobol4x && git checkout asm-backend
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git pull --rebase origin asm-backend

# Fix FIFO race in test/monitor/run_monitor.sh:
#   Remove set -e (or add || true after every bg job and wait).
#   The 5 `cat fifo > file &` jobs block until writers open; if set -e
#   sees any non-zero exit from wait it aborts. Use `wait 2>/dev/null || true`.
#   All participant runs already have `|| true`. The wait at step 9 just needs
#   `wait 2>/dev/null || true` (already written that way — confirm it's not
#   `set -euo pipefail` killing the script before step 9).
#
# Quick fix: change the shebang line from `#!/bin/bash` + `set -euo pipefail`
#   to `#!/bin/bash` + `set -uo pipefail` (drop -e) so FIFO cat EOF non-zero
#   doesn't abort.
#
# Then test:
#   bash test/monitor/run_monitor.sh /tmp/hello_monitor.sno
#   Expected: PASS [asm] / PASS [jvm] / PASS [net]
#
# sno2c binaries needed on this container:
#   /home/claude/sno2c_net  ← git checkout net-backend; cd src; make; cp sno2c /home/claude/sno2c_net
#   /home/claude/sno2c_jvm  ← already built in prior session from net-backend branch
#                              (net-backend has both -net and -jvm working)
#   /home/claude/x64/bootsbl ← make bootsbl in /home/claude/x64 (needs nasm)
#   snobol4 (CSNOBOL4)       ← build from /home/claude/csnobol4/snobol4-2.3.3; copy to /usr/local/bin
#
# Fire: M-MONITOR-IPC-5WAY when hello PASS [asm] [jvm] [net] with zero stderr blending
# Then: update PLAN.md milestone row, push, handoff
```

## Last Session Summary

**Session B-233 (2026-03-21) — M-X64-S3 + M-X64-S4 + M-X64-FULL ✅:**
- M-X64-S3 fired (`7193a51`): UNLOAD cleanup/reload/double-unload all PASS
- M-X64-S4 fired (`4fcb0e1`): SNOLIB search in loadDll(); STRING arg/return ABI in callef(); monitor_ipc_spitbol.so IPC confirmed end-to-end in SPITBOL
- M-X64-FULL fires: S1–S4 done; SPITBOL confirmed 5-way monitor participant
- snobol4x: wrapper scripts snobol4-asm/jvm/net written; run_monitor.sh rewritten for 5-way; normalize_trace.py extended to 5-way args; NET runtime DLLs committed; pushed `a72e417`
- Blocker: run_monitor.sh `set -euo pipefail` aborts on FIFO cat EOF — fix: drop `-e`

## Active Milestones

| ID | Trigger | Status |
|----|---------|--------|
| M-MONITOR-IPC-SO | monitor_ipc.so; CSNOBOL4 LOAD() confirmed | ✅ `8bf1c0c` B-229 |
| M-MONITOR-IPC-CSN | CSNOBOL4 trace via FIFO; hello PASS | ✅ `6eebdc3` B-229 |
| **M-X64-S1–S4** | SPITBOL LOAD/UNLOAD/SNOLIB/IPC | ✅ `4fcb0e1` B-233 |
| **M-X64-FULL** | SPITBOL = confirmed monitor participant | ✅ `4fcb0e1` B-233 |
| **M-MONITOR-IPC-5WAY** | all 5 via FIFO; hello PASS all 5 | ❌ next |
| M-MONITOR-IPC-TIMEOUT | watchdog: FIFO silence → kill + report | ❌ |
| M-MONITOR-4DEMO | roman+wordcount+treebank all 5 | ❌ |

Full milestone history → [PLAN.md](PLAN.md) · Beauty detail → [BEAUTY.md](BEAUTY.md)

---

## Concurrent Sessions

| Session | Branch | Focus |
|---------|--------|-------|
| B-233 | `asm-backend` | monitor-ipc — 5-way WIP pushed `a72e417` |
| x64-fork | `snobol4ever/x64 main` | M-X64-FULL ✅ `4fcb0e1` |
| J-next | `jvm-backend` | TBD |
| N-next | `net-backend` | TBD |
| F-next | `main` | TBD |
