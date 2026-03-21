# TINY.md — snobol4x (L2)

snobol4x: multiple frontends, multiple backends.
**Co-authored by Lon Jones Cherryholmes and Claude Sonnet 4.6.** When any milestone fires, Claude writes the commit.

→ Frontends: [FRONTEND-SNOBOL4.md](FRONTEND-SNOBOL4.md) · [FRONTEND-REBUS.md](FRONTEND-REBUS.md) · [FRONTEND-SNOCONE.md](FRONTEND-SNOCONE.md) · [FRONTEND-ICON.md](FRONTEND-ICON.md) · [FRONTEND-PROLOG.md](FRONTEND-PROLOG.md)
→ Backends: [BACKEND-C.md](BACKEND-C.md) · [BACKEND-X64.md](BACKEND-X64.md) · [BACKEND-NET.md](BACKEND-NET.md) · [BACKEND-JVM.md](BACKEND-JVM.md)
→ Compiler: [IMPL-SNO2C.md](IMPL-SNO2C.md) · Testing: [TESTING.md](TESTING.md) · Rules: [RULES.md](RULES.md) · Monitor: [MONITOR.md](MONITOR.md)
→ Full session history: [SESSIONS_ARCHIVE.md](SESSIONS_ARCHIVE.md)

---

## NOW

**Sprint:** `monitor-4demo` — roman + wordcount + treebank through all 5 participants
**HEAD:** `c6a6544` B-237 (asm-backend) · x64: `4fcb0e1` B-233
**Milestone:** M-MONITOR-4DEMO (next to fire)
**Invariants:** 97/106 ASM corpus (9 known failures: 022, 055, 064, cross, word1-4, wordcount)

**⚠ CRITICAL NEXT ACTION — Session B-238:**

```bash
cd /home/claude/snobol4x && git checkout asm-backend
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git pull --rebase origin asm-backend   # HEAD should be c6a6544 B-237

# ALL TOOLS VERIFIED INSTALLED: snobol4, bootsbl, mono, ilasm, nasm, libgc-dev, java
# Run precheck first — confirms all 30 checks PASS before any work
export PATH=$PATH:/usr/local/bin:/home/claude/x64
export X64_DIR=/home/claude/x64
bash test/monitor/precheck.sh

# GOAL: M-MONITOR-4DEMO — roman + wordcount + treebank PASS all 5 participants
INC=/home/claude/snobol4corpus/programs/inc
PROG=/home/claude/snobol4corpus/programs

# Fire each demo through 5-way monitor:
bash test/monitor/run_monitor.sh $PROG/roman/roman.sno
bash test/monitor/run_monitor.sh $PROG/wordcount/wordcount.sno
bash test/monitor/run_monitor.sh $PROG/treebank/treebank.sno

# For claws5: run and document divergence count (known 3 undef beta labels in ASM)
bash test/monitor/run_monitor.sh $PROG/claws5/claws5.sno || true

# Each failure: read first FAIL diff line → that is the exact bug location.
# Two agreeing backends specify the fix. Fix emit_byrd_asm.c / emit_byrd_jvm.c /
# emit_byrd_net.c as appropriate. Rebuild with: cd src && make -j4

# On success: update PLAN.md M-MONITOR-4DEMO → ✅, commit as B-238, push.
```

```bash
cd /home/claude/snobol4x && git checkout asm-backend
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git pull --rebase origin asm-backend   # HEAD should be 080a834 B-235

# ALL TOOLS ALREADY INSTALLED: snobol4, bootsbl, mono, ilasm, nasm, libgc-dev, java

# BLOCKER 1: sno2c -net segfaults on asm-backend even for trivial programs.
# The working NET emitter is on origin/net-backend (commit 2c417d7 N-209).
# Fix: fetch and merge the net emitter, then reapply B-235 monitor patches.
git fetch origin net-backend
# Get the last good emit_byrd_net.c from net-backend:
git show origin/net-backend:src/backend/net/emit_byrd_net.c > /tmp/net_base.c
# Then manually apply the B-235 monitor additions on top (they are documented
# in the commit message of 080a834). Key additions:
#   1. .field static StreamWriter sno_monitor_out  (after sno_vars field)
#   2. .cctor maxstack 4, MONITOR_FIFO open block before ret
#   3. net_monitor_write() helper after net_indr_set
#   4. OUTPUT site: dup + WriteLine + stloc V_20 + net_monitor_write
#   5. VAR stsfld site: dup + stsfld + stloc V_20 + net_monitor_write
# Then: cd src && make -j4

# BLOCKER 2: JVM trace empty despite sno_var_put hooks and OUTPUT fast-path dup fix.
# Verify MONITOR_FIFO env var actually reaches the JVM process in run_monitor.sh.
# In run_monitor.sh Step 7 (JVM), the MONITOR_FIFO= prefix is on the mono launch
# (Step 6) but the JVM step uses: MONITOR_FIFO="$TMP/jvm.fifo" java -cp ...
# Check that the JVM clinit is actually reading the env var at class load time.
# Quick diagnosis:
MONITOR_FIFO=/tmp/jvm_test.fifo mkfifo /tmp/jvm_test.fifo
cat /tmp/jvm_test.fifo &
cd /home/claude/snobol4x && ./sno2c -jvm /tmp/hello_monitor.sno > /tmp/t.j 2>/dev/null
java -jar src/backend/jvm/jasmin.jar /tmp/t.j -d /tmp 2>/dev/null
CN=$(grep '\.class' /tmp/t.j | head -1 | awk '{print $NF}')
MONITOR_FIFO=/tmp/jvm_test.fifo java -cp /tmp $CN < /dev/null
cat /tmp/jvm_fifo_out.txt  # should show: VAR OUTPUT "hello"

# BLOCKER 3: Oracle case divergence (CSNOBOL4 uppercase OUTPUT, SPITBOL lowercase).
# Add to test/monitor/tracepoints.conf:
#   IGNORE  OUTPUT  .*   <- suppresses the csn/spl oracle diff for OUTPUT var name

# STEP FINAL: run 5-way and fire:
printf "        OUTPUT = 'hello'\nEND\n" > /tmp/hello_monitor.sno
bash test/monitor/run_monitor.sh /tmp/hello_monitor.sno
# Expected: PASS [asm] PASS [jvm] PASS [net]
# On success: update PLAN.md milestone M-MONITOR-IPC-5WAY to ✅, commit, push
```

## Last Session Summary

**Session B-237 (2026-03-21) — M-MONITOR-IPC-TIMEOUT fires:**
- `monitor_collect.py`: select()-based watchdog; per-participant TIMEOUT on silence > T s
- `run_monitor.sh`: zero-race startup via ready.fifo named-pipe handshake (no sleeps);
  parallel launch of all 5; explicit kill after collector exits
- `inject_traces.py`: added &STLIMIT = 5000000 as backstop
- Verified: hello PASS [asm/jvm/net]; loop TIMEOUT [jvm/net] last event = start
- M-MONITOR-IPC-TIMEOUT fires ✅ `c6a6544`

**Session B-236 (2026-03-21) — M-MONITOR-IPC-5WAY fires: NET emitter + normalize fixes:**
- **NET emitter restored**: replaced asm-backend stub with full N-209 emitter; applied 6
  monitor patches (sno_monitor_out field, .cctor FIFO open, net_monitor_write helper,
  OUTPUT+VAR sites)
- **FIFO-seek fix**: `StreamWriter(path,append=true)` throws on FIFOs (no seek support);
  replaced with `FileStream(path,Open,Write)` + `StreamWriter(Stream)` — no seek
- **AutoFlush fix**: `TextWriter::set_AutoFlush` not on base class in mono; use
  `StreamWriter::set_AutoFlush`
- **Quote escape fix**: `ldstr """` invalid in mono ilasm; use `ldstr "\u0022"`
- **normalize_trace.py**: `RE_ASM_VAR` accepts `\u0022`; `name.upper()` folds
  SPITBOL lowercase vs CSNOBOL4 uppercase; STNO gating: absent STNO → `past_init=True`
  (JVM/NET emit no STNO line)
- **tracepoints.conf**: removed `IGNORE OUTPUT .*` (was stripping CSNOBOL4 events)
- **precheck.sh**: new 30-check pre-flight (tools/files/sno2c/null-smokes/IPC-smokes)
- **Result**: `run_monitor.sh hello_monitor.sno` → PASS [asm] PASS [jvm] PASS [net]
- **M-MONITOR-IPC-5WAY fires** ✅ `064bb59`

**Session B-235 (2026-03-21) — NET emitter monitor scaffold + harness fixes; ASM PASS:**
- **JVM OUTPUT fast-path fix** (`emit_byrd_jvm.c`): added `dup` before `getstatic/swap/println`
  at `Lout_ok_N` so val survives println → `sno_monitor_write("OUTPUT", val)` fires
- **NET emitter monitor scaffold** (`emit_byrd_net.c`): `StreamWriter sno_monitor_out` field;
  `.cctor` opens `MONITOR_FIFO` env var; `net_monitor_write` helper (5 Write calls);
  OUTPUT and VAR stsfld sites both call `net_monitor_write` via `dup+stloc V_20` pattern
- **run_monitor.sh fixes**: `set +e` around participant launches; `timeout 30 cat` on FIFO
  collectors; `SNO2C_NET`/`SNO2C_JVM` defaults fixed to `$DIR/sno2c`
- **Tools installed**: CSNOBOL4 2.3.3 built from tarball; SPITBOL `bootsbl` built from x64;
  mono+ilasm, nasm, libgc-dev all installed
- **ASM: PASS ✓** on 5-way hello run
- **BLOCKER**: `sno2c -net` segfaults on `asm-backend` even for trivial programs —
  working emitter on `origin/net-backend`; needs cherry-pick + monitor patches reapplied
- **JVM trace empty**: `MONITOR_FIFO` env routing to JVM process needs verification
- Pushed `080a834` B-235

## Active Milestones

| ID | Trigger | Status |
|----|---------|--------|
| M-MONITOR-IPC-SO | monitor_ipc.so; CSNOBOL4 LOAD() confirmed | ✅ `8bf1c0c` B-229 |
| M-MONITOR-IPC-CSN | CSNOBOL4 trace via FIFO; hello PASS | ✅ `6eebdc3` B-229 |
| **M-X64-S1–S4 + M-X64-FULL** | SPITBOL confirmed monitor participant | ✅ `4fcb0e1` B-233 |
| **M-MONITOR-IPC-5WAY** | all 5 via FIFO; hello PASS all 5 | ✅ `064bb59` B-236 |
| M-MONITOR-IPC-TIMEOUT | watchdog: FIFO silence → kill + report | ✅ `c6a6544` B-237 |
| M-MONITOR-4DEMO | roman+wordcount+treebank all 5 | ❌ |

## Concurrent Sessions

| Session | Branch | Focus |
|---------|--------|-------|
| B-233 | `asm-backend` | monitor-ipc — 5-way WIP pushed `a72e417` |
| x64-fork | `snobol4ever/x64 main` | M-X64-FULL ✅ `4fcb0e1` |
| J-next | `jvm-backend` | TBD |
| N-next | `net-backend` | TBD |
| F-next | `main` | TBD |
