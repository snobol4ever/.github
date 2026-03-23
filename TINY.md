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
**HEAD:** `3251cd4` B-269 (main)
**Milestone:** M-BEAUTY-TDUMP ❌ — IN PROGRESS; flat_bss_register fix applied; 2 open: (1) ANY(&UCASE &LCASE) inside box emits quoted type, (2) STLIMIT exceeded in Gen/TDump multi-line path
**Invariants:** 106/106 ASM corpus ALL PASS ✅ · 110/110 NET corpus ALL PASS ✅
**Compatibility policy:** snobol4x follows CSNOBOL4 behavior. DATATYPE() returns UPPERCASE.

**⚡ CRITICAL NEXT ACTION — Session B-265 (M-BEAUTY-CASE, BEAUTY SESSION):**

```bash
cd /home/claude/snobol4-project/snobol4x   # or: git clone snobol4ever/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git remote set-url origin https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x.git
git pull --rebase origin main   # HEAD should be 6fd01aa B-264

# Setup (if fresh container):
bash setup.sh
gcc -shared -fPIC -O2 -Wall -o test/monitor/monitor_ipc_sync.so test/monitor/monitor_ipc_sync.c
gcc -shared -fPIC -O2 -Wall -o /home/claude/snobol4-project/x64/monitor_ipc_spitbol.so     /home/claude/snobol4-project/x64/monitor_ipc_spitbol.c

# THE ONE REMAINING BUG (read §21 below before coding):
# ANY(&UCASE &LCASE) emits temp slot via emit_expr → any_expr_tmp_N_t/p .bss labels.
# But ANY_α_VAR calls NV_GET_fn(varname) which doesn't know temp labels.
# Fix: add ANY_α_SLOT macro to snobol4_asm.mac that reads charset directly from
# two absolute .bss addresses (type ptr + str ptr) rather than via NV_GET_fn.
# Then in emit_byrd_asm.c ANY expr branch: emit ANY_α_SLOT tmplab_t, tmplab_p, ...
# instead of registering a fake variable and calling emit_any_var.

# After fix — test icase:
INC=demo/inc ./snobol4-asm /tmp/icase_test.sno   # must print PATTERN

# Then 3-way monitor:
INC=demo/inc X64_DIR=/home/claude/snobol4-project/x64   MONITOR_TIMEOUT=30 bash test/beauty/run_beauty_subsystem.sh case
# → 9/9 PASS → fire M-BEAUTY-CASE

# Confirm corpus invariant
bash test/crosscheck/run_crosscheck_asm_corpus.sh   # must be 106/106

# Fire M-BEAUTY-CASE — commit snobol4x, update TINY.md + PLAN.md, push both repos
```
Trigger phrase for beauty sprint: **"playing with beauty"**
Full developer cycle → BEAUTY.md · RULES.md §BEAUTY SESSION

## Last Session Summary

**Session B-264 (2026-03-23) — M-BEAUTY-CASE partial — 4 fixes, 1 open:**
- Fix 1: `snobol4-asm` was not passing `-I"$INC"` to `sno2c` — `-INCLUDE` silently failed, program produced no output.
- Fix 2+3: `LOAD_NULVCL` / `LOAD_NULVCL32` used `DT_S=1` instead of `DT_SNUL=0`, and didn't set rax/rdx — function variable clear slots got garbage type tags.
- Fix 4: `emit_byrd_asm.c` ANY(expr) — `ANY(&UCASE &LCASE)` (E_CONC arg) was silently compiled as `ANY("")`. Added emit_expr into temp .bss slot + ANY_α_VAR dispatch.
- Open: `ANY_α_VAR` calls `NV_GET_fn(varname)` which doesn't find temp labels — needs `ANY_α_SLOT` macro reading charset directly from .bss type+ptr. Root cause of `icase` returning STRING. Fix in B-265.
- snobol4x commit: `6fd01aa` B-264

**Session F-214 (2026-03-22) — M-PROLOG-HELLO ✅ — Prolog x64 ASM backend first working program:**
- Wired `-pl -asm` in `main.c` to call new `asm_emit_prolog()` instead of `pl_emit()`.
- Replaced stub `emit_prolog_choice` with full implementation in `emit_byrd_asm.c`:
  - `emit_prolog_program()`: Prolog header (externs: unify, trail_*, term_new_*, pl_write, putchar, exit)
  - `emit_prolog_choice()`: resumable `_r` function with `cmp/je` clause dispatch on `start`
  - `emit_prolog_clause_block()`: α port, trail mark, head unify via `unify()` call, body goals, γ return
  - `emit_pl_term_load()`: atom→`lea [rel ATOM_LABEL]`, var→`[rbp-slot]`, int→`term_new_int`
  - `emit_pl_atom_data_v2()`: correct 24-byte Term structs (.data); `pl_rt_init()` fixes atom_ids at runtime
  - `emit_prolog_main()`: `main` calls `prolog_atom_init` + `trail_init` + `pl_rt_init` + init predicate
  - Body builtins handled inline: write/1→pl_write, nl/0→putchar(10), halt→exit, true/fail, writeln, =/2, ;/2, ,/2
- `prolog_unify.c`: added `trail_mark_fn()` non-inline wrapper (static inline not linkable from ASM).
- Fixed frame size bug: `sub rsp, 32` (not 16) — slots: mark(8)+cut(8)+args_ptr(8)+start(8).
- Fixed calling convention for arity-0: `rdi`=Trail*, `rsi`=start (not rdi=NULL, rsi=Trail*).
- Fixed atom struct size: 24 bytes (tag+saved_slot+union) not 16.
- **VERIFIED**: `hello.pro` → `hello` via `-pl -asm` pipeline end-to-end. M-PROLOG-HELLO ✅
- OPEN BUG blocking M-PROLOG-R1: call sites use `pl_NAME_ARITY_r` but predicates defined as `pl_NAME_sl_ARITY_r`. Fix: pass `"functor/arity"` through `pl_safe()` at every call site; drop `_%d` suffix. Grep: `pl_%s_%d_r` in `emit_byrd_asm.c`.
- snobol4x commit: `082141e` F-214



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
| **M-BEAUTY-GLOBAL**   | ❌ partial — M-MON-BUG-ASM-CAPTURE-INCLUDE blocker |
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
| M-PROLOG-HELLO     | ✅ `082141e` F-214 |
| **M-PROLOG-R1**    | ❌ **NEXT (F-215)** — fix pl_safe call-site naming; rung02+rung05 |
| M-PROLOG-R3        | ❌ |
| M-PROLOG-R4        | ❌ |
| M-PROLOG-R5        | ❌ |

## Concurrent Sessions

| Session | Branch | Focus |
|---------|--------|-------|
| B-next | `main` | M-BEAUTY-GLOBAL finish (M-MON-BUG-ASM-CAPTURE-INCLUDE) |
| F-215  | `main` | M-PROLOG-R1 — fix pl_safe call site naming, run rung02+rung05 |
