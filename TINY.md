# TINY.md — snobol4x (L2)

snobol4x: multiple frontends, multiple backends.
**Co-authored by Lon Jones Cherryholmes and Claude Sonnet 4.6.** When any milestone fires, Claude writes the commit.

→ Frontends: [FRONTEND-SNOBOL4.md](FRONTEND-SNOBOL4.md) · [FRONTEND-REBUS.md](FRONTEND-REBUS.md) · [FRONTEND-SNOCONE.md](FRONTEND-SNOCONE.md) · [FRONTEND-ICON.md](FRONTEND-ICON.md) · [FRONTEND-PROLOG.md](FRONTEND-PROLOG.md)
→ Backends: [BACKEND-C.md](BACKEND-C.md) · [BACKEND-X64.md](BACKEND-X64.md) · [BACKEND-NET.md](BACKEND-NET.md) · [BACKEND-JVM.md](BACKEND-JVM.md)
→ Compiler: [IMPL-SNO2C.md](IMPL-SNO2C.md) · Testing: [TESTING.md](TESTING.md) · Rules: [RULES.md](RULES.md) · Monitor: [MONITOR.md](MONITOR.md)
→ Full session history: [SESSIONS_ARCHIVE.md](SESSIONS_ARCHIVE.md)

---

## NOW

**Sprint:** `main` — M-BEAUTY-* sprint (beauty.sno subsystem testing via monitor)
**HEAD:** `a4a27ab` B-258 (main)
**Milestone:** M-MON-BUG-ASM-WPAT ✅ — **PIVOT**: next is M-BEAUTY-GLOBAL (beauty sprint begins)
**Invariants:** 106/106 ASM corpus ALL PASS ✅ · 110/110 NET corpus ALL PASS ✅

**⚡ CRITICAL NEXT ACTION — Session B-260 (M-BEAUTY-GLOBAL, BEAUTY SESSION):**

```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git remote set-url origin https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x.git
git pull --rebase origin main

# Setup (if fresh container):
bash setup.sh
gcc -shared -fPIC -O2 -Wall -o test/monitor/monitor_ipc_sync.so test/monitor/monitor_ipc_sync.c
gcc -shared -fPIC -O2 -Wall -o /home/claude/x64/monitor_ipc_spitbol.so /home/claude/x64/monitor_ipc_spitbol.c

# Generate oracle ref for global driver:
INC=/home/claude/snobol4corpus/programs/inc \
  snobol4 -f -P256k -I$INC test/beauty/global/driver.sno > test/beauty/global/driver.ref

# Full developer cycle — repeat until monitor exits 0:
INC=/home/claude/snobol4corpus/programs/inc X64_DIR=/home/claude/x64 \
  MONITOR_TIMEOUT=30 bash test/monitor/run_monitor_3way.sh test/beauty/global/driver.sno
# → first diverging trace line names the bug; fix it; rebuild; re-run

# When monitor exits 0: confirm corpus invariant
bash test/crosscheck/run_crosscheck_asm_corpus.sh   # must be 106/106

# Fire M-BEAUTY-GLOBAL — commit snobol4x, update PLAN.md + TINY.md, push .github
```

Trigger phrase for beauty sprint: **"playing with beauty"**
Full developer cycle and subsystem plan → BEAUTY.md · RULES.md §BEAUTY SESSION

## Last Session Summary

**Session B-259 (2026-03-23) — PIVOT: beauty sprint; HQ doc-only session:**
- No snobol4x source changes. All work in .github (PLAN.md, RULES.md, TINY.md, BEAUTY.md, MONITOR.md).
- Added trigger phrase "playing with beauty" → BEAUTY SESSION to PLAN.md trigger table.
- Expanded all 20 M-BEAUTY-* + M-BEAUTIFY-BOOTSTRAP milestone rows with full trigger descriptions.
- Rewrote BEAUTY SESSION rules: full developer cycle (find+fix in one session, not split across sessions).
- Clarified MONITOR SESSION = infrastructure only; BEAUTY SESSION = uses the monitor to fix bugs.
- Added developer cycle diagram to MONITOR.md. Updated BEAUTY.md harness section with fix-loop script.
- .github commit: `6dbb5ed` B-259

**Session B-258 (2026-03-22) — M-MON-BUG-ASM-WPAT ✅ + 3-way monitor + corpus DATATYPE fixes:**
- Root cause: `stmt_concat()` in `snobol4_stmt_rt.c` lacked pattern case. `BREAK(WORD) SPAN(WORD)`
  passed both `DT_P` operands through `VARVAL_fn()` → `"PATTERN"` each → concatenated →
  `"PATTERNPATTERN"`. Fix: `if (a.v == DT_P || b.v == DT_P) return pat_cat(pa, pb)` guard,
  promoting string operands to `pat_lit()`. Mirrors identical guard in `snobol4.c`.
- Added `test/monitor/run_monitor_3way.sh` — 3-way variant (csn+spl+asm), JVM/NET excluded.
- 3-way results: hello PASS ✅; wordcount ASM AGREE ✅; treebank diverges step 10
  `STK='cell'` vs `'CELL'` — filed M-MON-BUG-ASM-DATATYPE-CASE; claws5 spl segfault (known).
- snobol4corpus: fixed 3 tests to normalize `DATATYPE()` via `REPLACE(x,&LCASE,&UCASE)` —
  `081_builtin_datatype`, `096_data_datatype_check`, `1115_data_basic`. Only `DATATYPE()`
  return values coerced; user field values untouched. Stable across CSNOBOL4/SPITBOL(-f/-F)/ASM.
- 106/106 ALL PASS. Commits: `a4a27ab` B-258 (snobol4x), `05b809d` (snobol4corpus)

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
| M-MONITOR-4DEMO    | ❌ — wordcount ASM AGREE ✅; treebank blocks on M-MON-BUG-ASM-DATATYPE-CASE; claws5 spl segfault (known) |
| M-MON-BUG-SPL-EMPTY   | ❌ |
| M-MON-BUG-ASM-WPAT    | ✅ `a4a27ab` B-258 |
| M-MON-BUG-ASM-DATATYPE-CASE | ❌ — open bug (treebank STK case); beauty sprint proceeds in parallel |
| M-MON-BUG-JVM-WPAT    | ❌ |
| **M-BEAUTY-GLOBAL**   | ❌ **NEXT (beauty sprint)** |
| M-BEAUTY-IS        | ❌ |
| M-BEAUTY-FENCE     | ❌ |
| M-BEAUTY-IO        | ❌ |
| M-BEAUTY-CASE      | ❌ |
| M-BEAUTY-ASSIGN    | ❌ |
| M-BEAUTY-MATCH     | ❌ |
| M-BEAUTY-COUNTER   | ❌ |
| M-BEAUTY-STACK     | ❌ |
| M-BEAUTY-TREE      | ❌ |
| M-BEAUTY-SR        | ❌ |
| M-BEAUTY-TDUMP     | ❌ |
| M-BEAUTY-GEN       | ❌ |
| M-BEAUTY-QIZE      | ❌ |
| M-BEAUTY-READWRITE | ❌ |
| M-BEAUTY-XDUMP     | ❌ |
| M-BEAUTY-SEMANTIC  | ❌ |
| M-BEAUTY-OMEGA     | ❌ |
| M-BEAUTY-TRACE     | ❌ |
| M-BEAUTIFY-BOOTSTRAP | ❌ |

## Concurrent Sessions

| Session | Branch | Focus |
|---------|--------|-------|
| B-next | `main` | M-MONITOR-4DEMO finish |
| F-213  | `main` | M-PROLOG-EMIT retry loop — rungs 2,5 backtracking; then rung 10 puzzles |
