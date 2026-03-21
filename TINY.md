# TINY.md — snobol4x (L2)

snobol4x: multiple frontends, multiple backends.
**Co-authored by Lon Jones Cherryholmes and Claude Sonnet 4.6.** When any milestone fires, Claude writes the commit.

→ Frontends: [FRONTEND-SNOBOL4.md](FRONTEND-SNOBOL4.md) · [FRONTEND-REBUS.md](FRONTEND-REBUS.md) · [FRONTEND-SNOCONE.md](FRONTEND-SNOCONE.md) · [FRONTEND-ICON.md](FRONTEND-ICON.md) · [FRONTEND-PROLOG.md](FRONTEND-PROLOG.md)
→ Backends: [BACKEND-C.md](BACKEND-C.md) · [BACKEND-X64.md](BACKEND-X64.md) · [BACKEND-NET.md](BACKEND-NET.md) · [BACKEND-JVM.md](BACKEND-JVM.md)
→ Compiler: [IMPL-SNO2C.md](IMPL-SNO2C.md) · Testing: [TESTING.md](TESTING.md) · Rules: [RULES.md](RULES.md) · Monitor: [MONITOR.md](MONITOR.md)
→ Full session history: [SESSIONS_ARCHIVE.md](SESSIONS_ARCHIVE.md)

---

## NOW

**Sprint:** `monitor-ipc` — M-MONITOR-IPC-5WAY: JVM OUTPUT fast path + NET emitter + 5-way fire
**HEAD:** `9a94aaa` B-234 (asm-backend) · x64: `4fcb0e1` B-233
**Milestone:** M-MONITOR-IPC-5WAY (next to fire)
**Invariants:** 97/106 ASM corpus (9 known failures: 022, 055, 064, cross, word1-4, wordcount)

**⚠ CRITICAL NEXT ACTION — Session B-235:**

```bash
cd /home/claude/snobol4x && git checkout asm-backend
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git pull --rebase origin asm-backend
cd src && make -j4   # rebuild sno2c (JVM monitor patch in emit_byrd_jvm.c)

# STEP 1: Fix JVM OUTPUT fast path — bypasses sno_var_put entirely.
# In emit_byrd_jvm.c, grep for "Lout_ok_0" or "Lout_fail" to find the OUTPUT
# statement fast path in main(). After the invokevirtual println emit, add:
#   J("    ldc \"OUTPUT\"\n");
#   J("    <reload val onto stack>\n");  // need to re-push val — it was consumed
#   J("    invokestatic %s/sno_monitor_write(...)\n", classname);
# The val string was consumed by println. Must reload: push ldc "hello" again
# OR better: before the println, dup the val so it stays on stack.
# EXACT FIX: find "ldc "hello"" pattern — actually grep emit_byrd_jvm.c for
# the OUTPUT fast path emit and add a dup before the swap+println.
# After dup: stack is [val, val]. swap → [val, PS, val]. println consumes PS+val.
# Wait — the pattern is: ldc val, dup, ifnonnull Lout_ok, pop, goto fail
# At Lout_ok: getstatic stdout, swap, println. Stack after: [val_dup].
# Then: ldc "OUTPUT", swap, invokestatic sno_monitor_write → fires.
# grep -n "Lout_ok\|Lout_fail\|sno_stdout.*swap\|out_ok" emit_byrd_jvm.c | head -10

# STEP 2: Add monitor to NET emitter (emit_byrd_net.c).
# Same pattern as JVM: field sno_monitor_out, clinit open MONITOR_FIFO,
# write VAR events via a helper method. NET uses C# MSIL not JVM but similar.
# grep -n "OUTPUT\|TERMINAL\|println\|monitor" src/backend/net/emit_byrd_net.c | head -20

# STEP 3: Run full 5-way and fire M-MONITOR-IPC-5WAY:
export X64_DIR=/home/claude/x64 SNO2C_NET=/home/claude/sno2c_net
export SNO2C_JVM=/home/claude/snobol4x/sno2c SNO2C=/home/claude/snobol4x/sno2c
export JASMIN=/home/claude/snobol4x/src/backend/jvm/jasmin.jar
echo "        OUTPUT = '"'"'hello'"'"'" > /tmp/hello_monitor.sno && echo "END" >> /tmp/hello_monitor.sno
bash test/monitor/run_monitor.sh /tmp/hello_monitor.sno
# Expected: PASS [asm] PASS [jvm] PASS [net]
```

## Last Session Summary

**Session B-234 (2026-03-21) — monitor-ipc fixes + JVM monitor infrastructure:**
- Fixed 5 bugs blocking M-MONITOR-IPC-5WAY: `set -e` FIFO race, missing SPITBOL `MONITOR_SO`,
  UTF-8 arrow in preamble, `&TRACE` limit (SPITBOL max 2^24), `VALUE()` → `$` portable indirect
- CSNOBOL4 ✅ SPITBOL ✅ ASM ✅ all verified IPC-to-FIFO working in isolation
- JVM emitter: added `sno_monitor_out` field, clinit FIFO open, `sno_var_put` monitor hooks,
  `sno_monitor_write` helper method (bipush 34 for quote, astore local for PS ref)
- Root cause of remaining JVM silence: OUTPUT fast path in main() bypasses sno_var_put entirely
- Pushed `9a94aaa` B-234; NET emitter not yet done

## Active Milestones

| ID | Trigger | Status |
|----|---------|--------|
| M-MONITOR-IPC-SO | monitor_ipc.so; CSNOBOL4 LOAD() confirmed | ✅ `8bf1c0c` B-229 |
| M-MONITOR-IPC-CSN | CSNOBOL4 trace via FIFO; hello PASS | ✅ `6eebdc3` B-229 |
| **M-X64-S1–S4 + M-X64-FULL** | SPITBOL confirmed monitor participant | ✅ `4fcb0e1` B-233 |
| **M-MONITOR-IPC-5WAY** | all 5 via FIFO; hello PASS all 5 | ❌ next — JVM OUTPUT path + NET |
| M-MONITOR-IPC-TIMEOUT | watchdog: FIFO silence → kill + report | ❌ |
| M-MONITOR-4DEMO | roman+wordcount+treebank all 5 | ❌ |

## Concurrent Sessions

| Session | Branch | Focus |
|---------|--------|-------|
| B-233 | `asm-backend` | monitor-ipc — 5-way WIP pushed `a72e417` |
| x64-fork | `snobol4ever/x64 main` | M-X64-FULL ✅ `4fcb0e1` |
| J-next | `jvm-backend` | TBD |
| N-next | `net-backend` | TBD |
| F-next | `main` | TBD |
