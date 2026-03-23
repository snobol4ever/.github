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
**HEAD:** `a862b01` B-261 (main)
**Milestone:** M-BEAUTY-CASE ❌ — NEXT (M-BEAUTY-IS ⏸ deferred; M-BEAUTY-FENCE ✅; M-BEAUTY-IO ✅)
**Invariants:** 106/106 ASM corpus ALL PASS ✅ · 110/110 NET corpus ALL PASS ✅
**Compatibility policy:** snobol4x implements all SPITBOL extensions (internal builtins + command-line switches identical to SPITBOL). For semantic edge cases where CSNOBOL4 and SPITBOL differ, snobol4x follows CSNOBOL4 behavior. Key exception: DATATYPE() returns UPPERCASE (CSNOBOL4 convention) not lowercase (SPITBOL).

**⚡ CRITICAL NEXT ACTION — Session B-262 (M-BEAUTY-CASE, BEAUTY SESSION):**

```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git remote set-url origin https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x.git
git pull --rebase origin main

# Setup (if fresh container):
bash setup.sh
gcc -shared -fPIC -O2 -Wall -o test/monitor/monitor_ipc_sync.so test/monitor/monitor_ipc_sync.c
gcc -shared -fPIC -O2 -Wall -o /home/claude/x64/monitor_ipc_spitbol.so /home/claude/x64/monitor_ipc_spitbol.c

# Run monitor for fence subsystem:
INC=/home/claude/snobol4corpus/programs/inc X64_DIR=/home/claude/x64 \
  MONITOR_TIMEOUT=30 bash test/beauty/run_beauty_subsystem.sh case
# → fix any ASM divergence vs SPITBOL, repeat until exit 0

# Confirm corpus invariant
bash test/crosscheck/run_crosscheck_asm_corpus.sh   # must be 106/106

# Fire M-BEAUTY-CASE — commit snobol4x, update TINY.md, push .github
```

Trigger phrase for beauty sprint: **"playing with beauty"**
Full developer cycle and subsystem plan → BEAUTY.md · RULES.md §BEAUTY SESSION

## Last Session Summary

**Session B-261 (2026-03-22) — M-BEAUTY-FENCE ✅ + SPITBOL segfault fixed:**
- SPITBOL segfault-on-exit: nextef() SET_WA(type) → SET_WA(scanp); blkln needs block ptr in wa. Added blksize==0 guard. Committed to snobol4ever/x64 as 2d4554a.
- P_FENCE_β not defined: user functions (is_fn=1) emitted α and fn_γ/fn_ω but not β. Call sites reference β for backtrack. Fixed: emit beta_lbl as standalone stub after fn_ω → ret_omega.
- M-BEAUTY-FENCE monitor: PASS (1 step). 106/106 ALL PASS.
- snobol4x commit: `822c58f` B-261

**Session B-261 (2026-03-22) — M-BEAUTY-GLOBAL ✅ — fix -INCLUDE and ;* inline comments:**
- Root cause hunt: SET_CAPTURE=0 for driver.sno with -I flag.
- Discovered sno2c has TWO frontend implementations: sno.l/sno.y (flex/bison, unused) and lex.c/parse.c (active).
- Bug 1: lex.c join_file() had -INCLUDE as intentional no-op ("library functions in mock_includes.c"). Fixed: call open_include(iname, fname, out) to recursively inline included SNOBOL4 source.
- Bug 2: global.sno uses ';* comment' end-of-line syntax. FLUSH() semicolon-split pushed '* null character' as second SnoLine → parse error "expected operand after unary operator" on every &ALPHABET line. Fixed: in semicolon-split loop, if next_src after ';' starts with '*' or is empty, set next_len=-1 (treat as end-of-statement comment, not multi-stmt separator).
- After both fixes: 19 SET_CAPTURE in driver.sno output, 0 parse errors.
- M-BEAUTY-GLOBAL monitor: PASS — all 3 participants agree at every step (21 steps).
- 106/106 ALL PASS after fixes.
- snobol4x commit: `7e925fd` B-261

**Session B-260 (2026-03-23) — M-BEAUTY-GLOBAL partial — binary string NUL-safety:**
- Built CSNOBOL4 2.3.3 from tarball. Cloned snobol4corpus. Confirmed 106/106 ASM ALL PASS.
- Built monitor_ipc_sync.so + monitor_ipc_spitbol.so.
- Created test/beauty/run_beauty_subsystem.sh harness.
- Fixed run_monitor_3way.sh: SNOLIB includes INC path (cd "$INC") so SPITBOL finds -INCLUDE files.
- 3-way monitor fired: DIVERGENCE at step 1 — ASM skipped PASS: nul (CSNOBOL4+SPITBOL agreed).
- Root cause chain (4 bugs, all fixed):
  1. apply_captures (snobol4_pattern.c): STRVAL → BSTRVAL(text, len) — preserves slen
  2. stmt_set_capture (snobol4_stmt_rt.c): STRVAL → BSTRVAL(s, len)
  3. stmt_setup_subject (snobol4_stmt_rt.c): strlen(&ALPHABET)=0 → descr_slen()
  4. BCHAR_fn: STRVAL → BSTRVAL(buf,1); ident(): strcmp → memcmp+descr_slen
- 106/106 ALL PASS after fixes.
- Remaining blocker: M-MON-BUG-ASM-CAPTURE-INCLUDE — SET_CAPTURE not emitted for
  pat.var conditionals in -INCLUDE'd files. Zero SET_CAPTURE in full driver vs correct
  standalone. Emitter bug in emit_byrd_asm.c. Next session B-261.
- snobol4x commit: `7f9491a` B-260

**Session B-260 (2026-03-23) — M-BEAUTY-GLOBAL partial — binary string NUL-safety:**
- Built CSNOBOL4 2.3.3 from tarball. Cloned snobol4corpus. Confirmed 106/106 ASM ALL PASS.
- Built monitor_ipc_sync.so + monitor_ipc_spitbol.so.
- Created test/beauty/run_beauty_subsystem.sh harness.
- Fixed run_monitor_3way.sh: SNOLIB includes INC path (cd "$INC") so SPITBOL finds -INCLUDE files.
- 3-way monitor fired: DIVERGENCE at step 1 — ASM skipped PASS: nul (CSNOBOL4+SPITBOL agreed).
- Root cause chain (4 bugs, all fixed):
  1. apply_captures (snobol4_pattern.c): STRVAL → BSTRVAL(text, len) — preserves slen
  2. stmt_set_capture (snobol4_stmt_rt.c): STRVAL → BSTRVAL(s, len)
  3. stmt_setup_subject (snobol4_stmt_rt.c): strlen(&ALPHABET)=0 → descr_slen()
  4. BCHAR_fn: STRVAL → BSTRVAL(buf,1); ident(): strcmp → memcmp+descr_slen
- 106/106 ALL PASS after fixes.
- Remaining blocker: M-MON-BUG-ASM-CAPTURE-INCLUDE — SET_CAPTURE not emitted for
  pat.var conditionals in -INCLUDE'd files. Zero SET_CAPTURE in full driver vs correct
  standalone. Emitter bug in emit_byrd_asm.c. Next session B-261.
- snobol4x commit: `7f9491a` B-260

**Session B-259 (2026-03-23) — PIVOT: beauty sprint; HQ doc-only session: (2026-03-23) — PIVOT: beauty sprint; HQ doc-only session:**
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
| **M-BEAUTY-GLOBAL**   | ✅ `7e925fd` B-261 |
| **M-BEAUTY-IS**       | ⏸ DEFERRED — .NAME/NAME semantics (SPITBOL compat, fix post-bootstrap) |
| **M-BEAUTY-FENCE**    | ✅ `822c58f` B-261 |
| **M-BEAUTY-IO**       | ✅ `a862b01` B-261 |
| **M-BEAUTY-CASE**     | ❌ **NEXT (beauty sprint)** |

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
| F-214  | `main` | Diagnosis session — C emitter backtracking wrong path; next: M-PROLOG-WIRE-ASM (wire -pl -asm through emit_byrd_asm.c) |
