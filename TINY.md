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
**HEAD:** `832c236` B-257 (main)
**Milestone:** M-MONITOR-4DEMO — next blocker: M-MON-BUG-ASM-WPAT (PATTERNPATTERN vs PATTERN)
**Invariants:** 106/106 ASM corpus ALL PASS ✅ · 110/110 NET corpus ALL PASS ✅

**⚡ CRITICAL NEXT ACTION — Session B-258 (M-MON-BUG-ASM-WPAT: fix PATTERNPATTERN stringification):**

```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git remote set-url origin https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x.git
git pull --rebase origin main

# Setup (if fresh container):
bash setup.sh
apt-get install -y mono-complete
gcc -shared -fPIC -O2 -Wall -o test/monitor/monitor_ipc_sync.so test/monitor/monitor_ipc_sync.c
gcc -shared -fPIC -O2 -Wall -o /home/claude/x64/monitor_ipc_spitbol.so /home/claude/x64/monitor_ipc_spitbol.c

# Confirm hello still PASS all 5:
INC=/home/claude/snobol4corpus/programs/inc X64_DIR=/home/claude/x64 \
  MONITOR_TIMEOUT=15 bash test/monitor/run_monitor_sync.sh \
  /home/claude/snobol4corpus/crosscheck/hello/hello.sno

# Run wordcount monitor — diverges at step 3 WPAT:
INC=/home/claude/snobol4corpus/programs/inc X64_DIR=/home/claude/x64 \
  MONITOR_TIMEOUT=30 bash test/monitor/run_monitor_sync.sh demo/wordcount.sno

# The ASM WPAT bug: VALUE WPAT = 'PATTERNPATTERN' instead of 'PATTERN'
# Fix location: comm_var() in src/runtime/snobol4/snobol4.c
# When val.type == DT_PATTERN, stringification calls CONVERT($var,'STRING')
# which walks the pattern tree and concatenates child type names instead of
# returning the single string 'PATTERN'.
# Fix: in comm_var(), detect DT_PATTERN type and return literal "PATTERN"
# rather than calling the general string conversion path.
grep -n "DT_PATTERN\|comm_var\|PATTERN" src/runtime/snobol4/snobol4.c | head -20
```

## Last Session Summary

**Session B-257 (2026-03-22) — M-MONITOR-4DEMO partial:**
- Root cause of treebank step-0 timeout: three layered bugs found and fixed
- Bug 1: `FAIL_BR` emitter bug — assignment with unconditional goto `:(LABEL)` + NRETURN fn:
  `FAIL_BR` jumped to next statement instead of goto target. Fixed in 5 assignment cases
  (VART/KW general path, E_INDR indirect, E_IDX array, field-set, item-set). All emit
  `has_u_only` stub routing NRETURN failure to `tgt_u`. 106/106 corpus ALL PASS after fix.
- Bug 2: `demo/treebank.sno` program: pre-built `WBRKS = '( )' NL` before `word` pattern
  (inline concat inside NOTANY/BREAK fails in ASM). DATATYPE checks made case-insensitive.
  ASM treebank now produces correct output vs oracle.
- Bug 3: `run_monitor_sync.sh`: ASM/NET were compiling original `$SNO` not `$TMP/instr.sno`
  (no TRACE() calls → zero events → step-0 timeout). Also: `blk_alloc.c`/`blk_reloc.c`
  missing from ASM link. Both fixed. ASM now participates in treebank monitor.
- Status after fix: wordcount diverges at step 3 (M-MON-BUG-ASM-WPAT: PATTERNPATTERN);
  treebank NET still step-0 timeout (NET deferred per command decision).
- Commits: `832c236` B-257

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
| M-MON-BUG-NET-TIMEOUT | ✅ `1e9f361` B-256 |
| M-MONITOR-4DEMO    | ❌ **NEXT** — fix treebank ASM/NET step-0 timeout; then all 5 PASS on wordcount+treebank+claws5 |
| M-MON-BUG-SPL-EMPTY   | ❌ |
| M-MON-BUG-ASM-WPAT    | ❌ |
| M-MON-BUG-JVM-WPAT    | ❌ |

## Concurrent Sessions

| Session | Branch | Focus |
|---------|--------|-------|
| B-next | `main` | M-MONITOR-4DEMO finish |
| F-213  | `main` | M-PROLOG-EMIT retry loop — rungs 2,5 backtracking; then rung 10 puzzles |
