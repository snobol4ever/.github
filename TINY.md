# TINY.md — snobol4x (L2)

snobol4x: multiple frontends, multiple backends.
**Co-authored by Lon Jones Cherryholmes and Claude Sonnet 4.6.** When any milestone fires, Claude writes the commit.

→ Frontends: [FRONTEND-SNOBOL4.md](FRONTEND-SNOBOL4.md) · [FRONTEND-REBUS.md](FRONTEND-REBUS.md) · [FRONTEND-SNOCONE.md](FRONTEND-SNOCONE.md) · [FRONTEND-ICON.md](FRONTEND-ICON.md) · [FRONTEND-PROLOG.md](FRONTEND-PROLOG.md)
→ Backends: [BACKEND-C.md](BACKEND-C.md) · [BACKEND-X64.md](BACKEND-X64.md) · [BACKEND-NET.md](BACKEND-NET.md) · [BACKEND-JVM.md](BACKEND-JVM.md)
→ Compiler: [IMPL-SNO2C.md](IMPL-SNO2C.md) · Testing: [TESTING.md](TESTING.md) · Rules: [RULES.md](RULES.md) · Monitor: [MONITOR.md](MONITOR.md)
→ Full session history: [SESSIONS_ARCHIVE.md](SESSIONS_ARCHIVE.md)

---

## NOW

**Sprint:** `main` — MONITOR sprint; dual-pathway trace fully wired
**HEAD:** `e2c4fb5` B-249 (main)
**Milestone:** M-MONITOR-4DEMO next
**Invariants:** 106/106 ASM corpus ALL PASS ✅

**⚡ CRITICAL NEXT ACTION — Session B-250:**

```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git remote set-url origin https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x.git
git pull --rebase origin main
bash setup.sh   # idempotent — rebuilds sno2c, confirms 106/106

# OPEN QUESTION: does sno2c have a -trace switch for instrumentation?
# Check: ./sno2c 2>&1 | head -20
# If not, the two pathways are:
#   1. Oracle (CSN/SPL): inject_traces.py instruments .sno → IPC FIFO
#   2. Compiled (ASM/JVM/NET): comm_var/sno_mon_var/net_mon_var → MONITOR_FIFO directly
#      JVM: sno_mon_init() opens FIFO once at main() entry (FileOutputStream, blocks until
#           monitor_collect.py has read side open — correct; run_monitor.sh handles this)
#      NET: net_mon_var() opens+writes+closes per-call (may need same static-open fix as JVM)
#      ASM: MONITOR_FIFO env var → comm_var() → dprintf(monitor_fd, ...) — already works

# Sprint M-MONITOR-4DEMO — run wordcount + treebank through 5-way monitor:
MDIR=test/monitor
CORPUS=/home/claude/snobol4corpus
MONITOR_TIMEOUT=30 bash $MDIR/run_monitor.sh $CORPUS/crosscheck/strings/wordcount.sno
# Expected: ASM PASS (VARVAL_fn fix + &.* exclude); JVM trace arriving via sno_mon_fd; NET TBD
# If NET still times out: apply same sno_mon_init static-open pattern to emit_byrd_net.c
# Then treebank, claws5 → fire M-MONITOR-4DEMO
```

## Last Session Summary

**Session B-249 (2026-03-22) — monitor dual-pathway + author history rewrite:**
- Cloned all repos, ran setup.sh — 106/106 ALL PASS from the start
- Diagnosed M-MONITOR-4DEMO failures: roman too heavy (1.9M events), JVM/NET had zero trace
- Fixed VARVAL_fn: DT_P/A/T → "PATTERN"/"ARRAY"/"TABLE" (ASM WPAT divergence)
- Added EXCLUDE &.* to tracepoints.conf (keyword filter for compiled path)
- JVM: added sno_mon_fd static field + sno_mon_init() (opens FIFO once at main entry) + sno_mon_var() (writes per-var to cached fd)
- NET: added net_mon_var() CIL method + wired into Case 1 assignment (dup+stsfld+call)
- Rewrote 4 commits: claude@snobol4ever.org → LCherryholmes/lcherryh@yahoo.com via filter-branch; force-pushed
- 106/106 ALL PASS confirmed at handoff

## Last Session Summary

**Session B-248 (2026-03-22) — grand merge + M-MONITOR-CORPUS9:**
- Grand merge: `asm-t2` (B-247, 106/106) + `jvm-t2` (J-213b, 106/106) into `main`; zero conflicts.
- `net-t2` already on main; all 7 dead branches deleted from origin.
- Built csnobol4 2.3.3 (with STNO patch), SPITBOL x64, sno2c from merged main; 106/106 ALL PASS confirmed.
- Added `setup.sh` — idempotent one-shot bootstrap; commits `5018a40`.
- Fixed `run_monitor.sh` — feed `.input` files to stdin (mirrors crosscheck harness); commit `a8d6ca0`.
- Ran all 9 former corpus failures through monitor: ASM PASS on 022/064 direct; trace FAILs on others are inject_traces.py gaps (? operator LHS, concat vars), not backend bugs — all produce correct output.
- M-MONITOR-CORPUS9 ✅ fired `a8d6ca0` B-248. PLAN.md + SESSIONS_ARCHIVE updated.

**Session N-248 (2026-03-22) — M-T2-NET + M-T2-FULL:**
- 110/110 NET corpus ALL PASS; M-T2-NET ✅ + M-T2-FULL ✅; tag `v-post-t2` cut.

## Active Milestones

| ID | Status |
|----|--------|
| M-MONITOR-CORPUS9  | ✅ `a8d6ca0` B-248 |
| M-MONITOR-4DEMO    | ❌ next |
| M-MONITOR-GUI      | 💭 dream |
| M-BEAUTY-GLOBAL    | ❌ |
| M-BEAUTIFY-BOOTSTRAP | ❌ |

## Concurrent Sessions

| Session | Branch | Focus |
|---------|--------|-------|
| B-next | `main` | M-MONITOR-4DEMO |
| F-next | `main` | TBD |
