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
| **HEAD** | `ba93890` — WIP: fix decl_flush static→local; ntop=1 after pp bug active |

---

## ⚡ SESSION 88 FIRST ACTION

### Active bug: ntop=1 after pp — nstack frame leak

**Background:** `-INCLUDE` is compile-time only — `sno2c -I inc_mock` handles it.
The mock `.sno` files in `src/runtime/inc_mock/` are comment-only stubs.
The compiled binary never sees INCLUDE directives at runtime.

**Two bugs fixed this session:**
1. `decl_flush()` in `emit_byrd.c` was emitting `static` locals for deref frame
   pointers in statement bodies. Fixed to plain locals. (`static` is correct only
   inside named pattern functions where re-entry requires persistence.)
2. This fixed the stale-frame corruption, but revealed a second bug:

**Current bug:** After `pp(sno)` runs for the first beautified statement,
`ntop()` returns 1 when it should return 0 (clean). This means a `NPUSH_fn()`
call somewhere inside `pp` is not matched by a `NPOP_fn()`.

**Diagnostic confirmed:**
```
stmt_214 ntop=0    ← first *Parse call, clean
stmt_217 ntop=1    ← second *Parse call (main05), dirty → Parse Error
```

`stmt_214` is line 790 (`Src POS(0) *Parse *Space RPOS(0) :F(mainErr1)`) — main02 path.
`stmt_217` is line 793 (`Src POS(0) *Parse *Space RPOS(0) :F(mainErr1)`) — main05 path.

**What is known:**
- `pat_Parse` itself correctly calls `NPUSH_fn()` then `NPOP_fn()` — verified in generated C
- The leak is INSIDE `pp` execution (between stmt_214 returning and stmt_217 being called)
- `pp` calls `pp_Parse` which loops calling `pp(c[i])` recursively
- Each recursive `pp` call triggers another `pat_Parse` → `NPUSH/NPOP` pair
- Somewhere one of these inner `pat_Parse` calls (or a `pat_Command`/`nInc` call) pushes without popping

**Session 88 first action:**
1. Build the binary (see Build commands below)
2. Add ntop trace at pp entry — find which pp call is the leaker:
   ```bash
   # Find stmt number for line 427 (pp entry label)
   grep -n "line=427\|label:pp\b" /tmp/beauty_core.c | head -5
   # Then patch that stmt to print ntop on entry
   ```
3. The leak is likely in `pat_Command`: `Command = nInc() FENCE(...)` — if
   FENCE backtracks after nInc, does nInc get un-done? `nInc` is NOT reversible
   on backtrack. If `*Comment` or `*Control` or `*Stmt` fails after `nInc()`,
   the FENCE tries the next alt — but `nInc` already fired. Check ARBNO backtrack
   behavior in `pat_Parse`: when ARBNO tries `*Command`, `Command` calls `nInc()`
   then FENCE tries alts. If all alts fail, ARBNO stops — but `nInc` was called.
   That means every ARBNO iteration that FAILS (the one that terminates ARBNO)
   leaves a leaked `nInc`. Over N statements processed, this accumulates.
4. Fix: `nInc` should only fire AFTER a `Command` alt succeeds. In the compiled
   `pat_Command`, `NINC_fn()` fires at `cat_l_534_α` before FENCE. If FENCE
   fails, `cat_l_534_β` goes to `_Command_ω` — but `nInc` already fired.
   The fix is to emit `nInc` as part of each successful FENCE branch, not before.
   OR: save ntop on Command entry and restore on Command failure.

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
