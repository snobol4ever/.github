# TINY.md — snobol4x (L2)

snobol4x: multiple frontends, multiple backends.
**Co-authored by Lon Jones Cherryholmes and Claude Sonnet 4.6.** When any milestone fires, Claude writes the commit.

→ Frontends: [FRONTEND-SNOBOL4.md](FRONTEND-SNOBOL4.md) · [FRONTEND-REBUS.md](FRONTEND-REBUS.md) · [FRONTEND-SNOCONE.md](FRONTEND-SNOCONE.md) · [FRONTEND-ICON.md](FRONTEND-ICON.md) · [FRONTEND-PROLOG.md](FRONTEND-PROLOG.md)
→ Backends: [BACKEND-C.md](BACKEND-C.md) · [BACKEND-X64.md](BACKEND-X64.md) · [BACKEND-NET.md](BACKEND-NET.md) · [BACKEND-JVM.md](BACKEND-JVM.md)
→ Compiler: [IMPL-SNO2C.md](IMPL-SNO2C.md) · Testing: [TESTING.md](TESTING.md) · Rules: [RULES.md](RULES.md) · Monitor: [MONITOR.md](MONITOR.md)
→ Full session history: [SESSIONS_ARCHIVE.md](SESSIONS_ARCHIVE.md)

---

## NOW

**Sprint:** `main` — M-MONITOR-4DEMO in progress
**HEAD:** `2652a51` B-255 (main)
**Milestone:** M-MONITOR-4DEMO — roman + wordcount + treebank PASS all 5; claws5 divergence count documented
**Invariants:** 106/106 ASM corpus ALL PASS ✅

**⚡ CRITICAL NEXT ACTION — Session B-256 (M-MONITOR-4DEMO: run demos through monitor):**

```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git remote set-url origin https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x.git
git pull --rebase origin main

# Setup (if fresh container) — tarball at /mnt/user-data/uploads/snobol4-2_3_3_tar.gz:
bash setup.sh
apt-get install -y mono-complete   # needed for NET participant
gcc -shared -fPIC -O2 -Wall \
    -o test/monitor/monitor_ipc_sync.so test/monitor/monitor_ipc_sync.c
gcc -shared -fPIC -O2 -Wall \
    -o /home/claude/x64/monitor_ipc_spitbol.so \
    /home/claude/x64/monitor_ipc_spitbol.c

# Run demo programs through 5-way sync monitor:
INC=/home/claude/snobol4corpus/programs/inc X64_DIR=/home/claude/x64 \
  MONITOR_TIMEOUT=15 bash test/monitor/run_monitor_sync.sh \
  /home/claude/snobol4corpus/crosscheck/hello/hello.sno

# Then roman, wordcount, treebank, claws5:
for prog in roman wordcount treebank; do
  INC=/home/claude/snobol4corpus/programs/inc X64_DIR=/home/claude/x64 \
    MONITOR_TIMEOUT=30 bash test/monitor/run_monitor_sync.sh \
    /home/claude/snobol4corpus/benchmarks/${prog}.sno
done
# Note: demo programs may need STDIN; check run_monitor_sync.sh STDIN_SRC handling
# Note: 4 bug milestones still open (M-MON-BUG-*) — file them as found, fix in BUG SESSIONs
```

## Last Session Summary

**Session B-255 (2026-03-22) — M-MONITOR-SYNC ✅:**
- Added trace-registration hash set (64-slot open-addressed, `trace_set[]`) to snobol4.c
- `trace_register/trace_unregister/trace_registered` helpers using djb2 hash
- `comm_var()` now gates on `trace_registered(name)` — only sends events for variables explicitly registered via `TRACE(name,'VALUE')`; pre-init variables (tab/digits/etc.) silently skipped
- `_b_TRACE` builtin: `TRACE(varname,'VALUE')` registers name; other types accepted but no-op
- `_b_STOPTR` builtin: removes name from trace set
- Registered both with `register_fn` (TRACE 1-4 args, STOPTR 1-2 args)
- `monitor_ready` flag retained as secondary pre-init guard
- Result: hello **PASS all 5 sync** (csn/spl/asm/jvm/net agree at every step, 2 steps)
- SPL segfault is known sandbox artifact — harmless, SPITBOL still participates correctly
- mono installed via apt (needed for NET participant in fresh containers)
- 106/106 ALL PASS unchanged

## Active Milestones

| ID | Status |
|----|--------|
| M-MONITOR-SYNC     | ✅ `2652a51` B-255 |
| M-MONITOR-4DEMO    | ❌ **NEXT** — run roman/wordcount/treebank/claws5 through 5-way sync monitor |
| M-MON-BUG-NET-TIMEOUT | ❌ |
| M-MON-BUG-SPL-EMPTY   | ❌ |
| M-MON-BUG-ASM-WPAT    | ❌ |
| M-MON-BUG-JVM-WPAT    | ❌ |

## Concurrent Sessions

| Session | Branch | Focus |
|---------|--------|-------|
| B-next | `main` | M-MONITOR-SYNC finish |
| F-212  | `main` | M-PROLOG-TERM — term.h + pl_unify.c + pl_atom.c (Sprint 1) |
