# TINY.md — snobol4x (L2)

snobol4x: multiple frontends, multiple backends.
**Co-authored by Lon Jones Cherryholmes and Claude Sonnet 4.6.** When any milestone fires, Claude writes the commit.

→ Frontends: [FRONTEND-SNOBOL4.md](FRONTEND-SNOBOL4.md) · [FRONTEND-REBUS.md](FRONTEND-REBUS.md) · [FRONTEND-SNOCONE.md](FRONTEND-SNOCONE.md) · [FRONTEND-ICON.md](FRONTEND-ICON.md) · [FRONTEND-PROLOG.md](FRONTEND-PROLOG.md)
→ Backends: [BACKEND-C.md](BACKEND-C.md) · [BACKEND-X64.md](BACKEND-X64.md) · [BACKEND-NET.md](BACKEND-NET.md) · [BACKEND-JVM.md](BACKEND-JVM.md)
→ Compiler: [IMPL-SNO2C.md](IMPL-SNO2C.md) · Testing: [TESTING.md](TESTING.md) · Rules: [RULES.md](RULES.md) · Monitor: [MONITOR.md](MONITOR.md)
→ Full session history: [SESSIONS_ARCHIVE.md](SESSIONS_ARCHIVE.md)

---

## NOW

**Sprint:** `main` — MONITOR sprint; dual-pathway trace wired
**HEAD:** `52e947f` B-249 (main)
**Milestone:** M-MONITOR-4DEMO next
**Invariants:** 106/106 ASM corpus ALL PASS ✅

**⚡ CRITICAL NEXT ACTION — Session B-250:**

```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git remote set-url origin https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x.git
git pull --rebase origin main
bash setup.sh   # idempotent

# Two trace pathways are both live and selectable:
# 1. Oracle pathway (CSN/SPL): inject_traces.py instruments .sno → MONCALL/MONRET/MONVAL → IPC FIFO
# 2. Compiled pathway (ASM/JVM/NET): comm_var()/sno_mon_var()/net_mon_var() → MONITOR_FIFO directly
#
# Next: run wordcount through monitor — expect ASM PASS; JVM/NET trace now wired
# The FIFO open in JVM/NET uses FileOutputStream(append=true) per write — may block on FIFO.
# If JVM FIFO blocks: switch JVM to MONITOR=1 stderr fallback while debugging open semantics.
MDIR=test/monitor
CORPUS=/home/claude/snobol4corpus
MONITOR_TIMEOUT=30 bash $MDIR/run_monitor.sh $CORPUS/crosscheck/strings/wordcount.sno
# Check ASM passes; diagnose JVM/NET FIFO open behavior
# Then: treebank + claws5 → M-MONITOR-4DEMO
```

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
