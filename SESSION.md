# SESSION.md — Live Handoff

> This file is fully self-contained. A new Claude reads this and nothing else to start working.
> Updated at every HANDOFF. History lives in SESSIONS_ARCHIVE.md.

---

## Active Session

| Field | Value |
|-------|-------|
| **Repo** | SNOBOL4-tiny |
| **Sprint** | `beauty-first` — fix Parse Error → M-BEAUTY-CORE |
| **Milestone** | M-BEAUTY-CORE (mock includes first) → M-BEAUTY-FULL (real inc, second) |
| **HEAD** | `29c0a4b` — fix(emit_byrd): nInc beta emits NDEC_fn() — compensate on backtrack |

---

## ⚡ SESSION 89 FIRST ACTION

### Active bug: ARBNO loop — partial token output, ~64 iterations, then Parse Error

**Smoke test result (session 88):** 2/21 pass — only `comment line` and `control line` pass.
All Stmt-type inputs fail: the subject token (e.g. `X`) is output ~64 times, then Parse Error.

**What this means:**
Each ARBNO iteration is matching a tiny fragment (just the label/subject) instead of a full
statement. The loop runs ~64 times (ARBNO stack depth limit?) then fails.

**Session 89 first action:**
1. Build binary + run smoke test to confirm baseline:
   ```bash
   bash test/smoke/test_snoCommand_match.sh /tmp/beauty_core_bin
   ```
2. Feed minimal failing case and observe:
   ```bash
   printf '    X = 1\nEND\n' | /tmp/beauty_core_bin 2>&1
   ```
3. Check `pat_Commands` struct — `arbno_stack[64]` field? That would cap iterations at 64.
4. Check whether `pp` is being called per-token vs per-statement. The fragment output
   (`X`, `1`, then loop) suggests `pp(c[i])` is walking tokens not tree nodes.
5. Check `pat_Parse` ARBNO wiring in generated C — is ARBNO correctly wrapping
   `*Commands` (plural) or just `*Command` (single)?

**nInc fix (session 88, commit 29c0a4b):** CORRECT and committed.
`NDEC_fn()` now emitted at nInc beta port. The ntop leak is fixed.
The ARBNO loop bug is a separate pre-existing issue now unmasked.

**Build commands:**
```bash
cd /home/claude/repos/SNOBOL4-tiny
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
apt-get install -y libgc-dev
make -C src/sno2c

RT=src/runtime
STUBS=src/runtime/inc_mock
BEAUTY=/home/claude/repos/SNOBOL4-corpus/programs/beauty/beauty.sno

src/sno2c/sno2c -trampoline -I$STUBS $BEAUTY > /tmp/beauty_core.c
gcc -O0 -g /tmp/beauty_core.c \
    $RT/snobol4/snobol4.c $RT/snobol4/mock_includes.c \
    $RT/snobol4/snobol4_pattern.c $RT/engine_stub.c \
    -I$RT/snobol4 -I$RT -Isrc/sno2c \
    -lgc -lm -w -o /tmp/beauty_core_bin
```

⚠️ engine_stub.c — NOT engine.c
⚠️ beauty_core (mock includes) FIRST — beauty_full (real inc) only after M-BEAUTY-CORE
⚠️ NEVER write the token into any file
⚠️ inc_mock/ contains comment-only .sno stubs — sno2c reads them at compile time, binary never sees INCLUDE at runtime

Oracle: `test/smoke/outputs/session50/beauty_oracle.sno`

---

## What was done this session (Session 88)

### Bug 2 fixed: nInc beta now emits NDEC_fn() (commit 29c0a4b)
- Root cause confirmed: `cat_l_534_α: NINC_fn()` fired on every Command attempt,
  including the failing termination attempt by ARBNO. No compensation on beta.
- Fix: one line in `emit_byrd.c` — `PL(beta, omega, "NDEC_fn();")` replaces `PLG(beta, omega)`
- Generated code confirmed: `cat_l_534_β: NDEC_fn(); goto _Command_ω;`

### Smoke test run: 2/21 pass
- PASS: comment line, control line
- FAIL: all Stmt-type inputs — subject token output ~64 times, then Parse Error
- This is a **pre-existing structural bug** now clearly visible via smoke test
- ARBNO loop iterates ~64 times per statement, each matching only a token fragment

### -INCLUDE diagnostic (ruled out)
- Removing all -INCLUDE lines from beauty.sno input made no difference
- Parse Error still hits on `START` (first non-comment line)
- -INCLUDE lines (Control pattern) parse correctly — confirmed by smoke test

---

## What was done this session (Session 87)

### Renames
- `src/runtime/inc_stubs/` → `src/runtime/inc_mock/`
- `src/runtime/snobol4/snobol4_inc.c/.h` → `mock_includes.c/.h`
- All references updated in both repos

### SESSION.md corrected
Removed false "Parse Error on -INCLUDE lines" bug description. -INCLUDE is
compile-time, not runtime. Previous session had this completely wrong.

### csnobol4 2.3.3 built
Available at `/tmp/snobol4-inst/bin/snobol4` for oracle comparison.

### Bug 1 fixed: static locals in statement bodies (emit_byrd.c)
`decl_flush()` was emitting `static` for deref frame pointers in statement
bodies. `static` locals persist across trampoline calls — second statement
saw stale pattern frames from first statement. Fixed to plain locals.
Commit: `ba93890`

### Bug 2 identified: ntop=1 after pp (not yet fixed)
After pp runs for first statement, `_ntop=1` when stmt_217 runs its *Parse.
Root cause: `nInc()` fires at start of every `*Command` attempt (even failed
ones). ARBNO termination attempt calls `nInc` then FENCE fails → `nInc`
not reversed. Accumulates across pp's recursive `pp(c[i])` calls.

---

## Active bug: ntop leak in ARBNO(*Command)

**Root cause (hypothesis):** `Command = nInc() FENCE(...)`. When ARBNO
terminates (tries *Command, Command calls nInc, FENCE fails, Command fails),
the nInc from the terminating attempt is not reversed. Each *Parse call
leaks one nInc. pp recurses → multiple *Parse calls → ntop accumulates.

**Fix location:** `emit_byrd.c` — how `nInc()` (E_FUNC side-effect) is
emitted relative to FENCE backtracking. The nInc must be conditional on
Command succeeding, not unconditional at Command entry.

---

## CRITICAL Rules

- **NEVER write the token into any file**
- **NEVER link engine.c** — engine_stub.c only
- **ALWAYS run `git config user.name/email` after every clone**
- **beauty_core (mock includes) FIRST — beauty_full (real inc) SECOND**
- **beauty.sno is NEVER modified — it is syntactically perfect**
- **-INCLUDE is compile-time (sno2c -I inc_mock) — NOT a runtime concern**

---

## Pivot Log

| Date | What changed | Why |
|------|-------------|-----|
| 2026-03-14 | PIVOT: block-fn + trampoline model | complete rethink with Lon |
| 2026-03-14 | Session 80 runtime fixes | engine_stub T_FUNC/T_CAPTURE etc |
| 2026-03-14 | Session 83 diagnosis | _c = data_define overwrites _b_tree_c (later disproved) |
| 2026-03-14 | Session 84 SIL rename | DESCR_t/DTYPE_t/XKIND_t/_fn/_t throughout |
| 2026-03-14 | Session 84 build fixes | cs_alloc, computed goto, label table, inc_mock |
| 2026-03-14 | Session 84 HALT | broke beauty_core/beauty_full agreement — reverted to stubs |
| 2026-03-14 | Session 85 cleanup | agreement breach resolved, rename audit, P4 undo, M-BEAUTY-CORE split |
| 2026-03-14 | Session 87 renames | inc_stubs→inc_mock, snobol4_inc→mock_includes |
| 2026-03-14 | Session 87 bug fix | decl_flush static→local (stale frame corruption) |
| 2026-03-14 | Session 87 bug found | ntop leak in ARBNO(*Command) nInc not reversed on fail |

---

## What was done this session (Session 88)

### nInc NDEC fix (commit 29c0a4b)
`emit_byrd.c`: nInc beta port now emits `NDEC_fn()` to compensate when
Command fails after nInc already fired. This was the ntop=1 leak.

### Diagnostic: -INCLUDE is not the issue
Confirmed: removing all -INCLUDE lines from beauty.sno input makes no
difference. Parse Error still occurs on the first Stmt-type line.

### Smoke test run
`test/smoke/test_snoCommand_match.sh` run for first time this session.
Result: 2/21 pass. Comment and control lines pass; all Stmt types fail
with ~64-repeat partial token loop then Parse Error.

### Active bug identified
ARBNO iteration is matching fragments rather than full statements.
Each iteration outputs one token (e.g. `X`) and succeeds, loops ~64
times, then fails. Root cause not yet identified — session 89 work.

---

## Pivot Log

| Date | What changed | Why |
|------|-------------|-----|
| 2026-03-14 | PIVOT: block-fn + trampoline model | complete rethink with Lon |
| 2026-03-14 | Session 80 runtime fixes | engine_stub T_FUNC/T_CAPTURE etc |
| 2026-03-14 | Session 83 diagnosis | _c = data_define overwrites _b_tree_c (later disproved) |
| 2026-03-14 | Session 84 SIL rename | DESCR_t/DTYPE_t/XKIND_t/_fn/_t throughout |
| 2026-03-14 | Session 84 build fixes | cs_alloc, computed goto, label table, inc_mock |
| 2026-03-14 | Session 84 HALT | broke beauty_core/beauty_full agreement — reverted to stubs |
| 2026-03-14 | Session 85 cleanup | agreement breach resolved, rename audit, P4 undo, M-BEAUTY-CORE split |
| 2026-03-14 | Session 87 renames | inc_stubs→inc_mock, snobol4_inc→mock_includes |
| 2026-03-14 | Session 87 bug fix | decl_flush static→local (stale frame corruption) |
| 2026-03-14 | Session 87 bug found | ntop leak in ARBNO(*Command) nInc not reversed on fail |
| 2026-03-14 | Session 88 bug fix | nInc beta now emits NDEC_fn() — ntop leak resolved |
| 2026-03-14 | Session 88 smoke test | 2/21 pass — ARBNO fragment-loop bug now active symptom |
