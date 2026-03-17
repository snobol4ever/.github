# PATCHES.md — Runtime Patches and Fixes Log
## snobol4x Sprint 20+

> **What this file is**: Every time we patch the runtime (`snobol4.c`,
> `snobol4.h`, `emit_c_stmt.py`, `mock_includes.c`, `snobol4_pattern.c`)
> to fix a bug found by the double-trace monitor or other diagnosis,
> it is recorded here. Patch number, symptom, root cause, fix, commit.
>
> **Why**: The monitor finds bugs fast. We need a record of what was
> found, why it was wrong, and what the fix was. This is the audit trail.
> Each patch is a data point about the gap between SNOBOL4 semantics
> and our compiled C translation.
>
> **Cross-reference**: See `PLAN.md` § Outstanding Items for priority
> classification (P1/P2/P3). See `MONITOR.md` for the diagnostic
> methodology. See `STRING_ESCAPES.md` for string literal handling.
> See `COMPILAND_REACHABILITY.md` for inc-file → C mapping.

---

## Patch Index

| # | File | Symptom | Root Cause | Status |
|---|------|---------|------------|--------|
| P001 | `snobol4.c` | `./beautiful` hangs forever | `&STLIMIT` declared but never enforced | **RESOLVED** |
| P002 | `snobol4.c`, `snobol4_pattern.c`, `snobol4.h` | Loop at STNO 160↔161 — `i` increments forever | `sno_array_get`/`get2` returned `SNO_NULL_VAL` on out-of-bounds instead of failure | **RESOLVED** |

---

## P001 — &STLIMIT Not Enforced
**Date**: 2026-03-10
**Found by**: Double-trace monitor (binary STNO stream, timeout run)
**Symptom**: `./beautiful < beauty.sno` hangs. Exit 124 (timeout).
STNO stream shows loop at statements 160↔161, variable `i` incrementing
without bound (observed value: 92020+ after 5 seconds).

**Diagnosis**:
```
STNO 160
VAR i "92018"
STNO 161
VAR  ""
STNO 160
VAR i "92019"
...repeating forever...
```
Statement 160 increments `i`. Statement 161 checks a condition and loops
back to 160. This is `&STLIMIT` territory — the loop should terminate
when the statement count exceeds the limit. But `sno_kw_stlimit = 50000`
is declared in `snobol4.c` and never checked. `sno_kw_stcount` does not
exist. The guard that should stop this loop has never been wired up.

**Root Cause**: `snobol4.h` declares `sno_kw_stlimit` as an `int64_t`
global. `snobol4.c` initializes it to 50000. Neither file increments
a counter or checks it. The keyword is a stub — present in name only.

**Fix**:
1. Add `int64_t sno_kw_stcount = 0;` to `snobol4.c`
2. Add `extern int64_t sno_kw_stcount;` to `snobol4.h`
3. In `sno_comm_stno(n)`: increment `sno_kw_stcount`; if it exceeds
   `sno_kw_stlimit` (and `sno_kw_stlimit >= 0`), abort with error message.
4. `sno_kw_stlimit` default: keep at 50000 for safety during development.
   Beautiful.sno's full run needs more — raise to 500000 once confirmed.

**Files changed**: `snobol4.c`, `snobol4.h`
**Commit**: (applying now)

---

*Template for future patches:*
```
## PNNN — Short title
**Date**: YYYY-MM-DD
**Found by**: [monitor / oracle diff / manual]
**Symptom**: [what the user/monitor saw]
**Diagnosis**: [trace output that identified it]
**Root Cause**: [the actual code defect]
**Fix**: [what was changed and why]
**Files changed**: [list]
**Commit**: [hash]
```

**P001 Resolution**: Fixed. `sno_kw_stcount` added, incremented in
`sno_comm_stno()`, checked against `sno_kw_stlimit`. Binary now exits
cleanly with error message at the limit instead of hanging forever.
Confirmed: `** &STLIMIT exceeded at statement 161 (&STCOUNT=50001)`.
But raising `&STLIMIT` to 2,000,000 still loops at 161 — revealing P002.

---

## P002 — sno_subscript_get2 Never Returns Failure
**Date**: 2026-03-10
**Found by**: P001 fix revealing the underlying loop structure
**Symptom**: After P001, `./beautiful` exits at `&STLIMIT` instead of
hanging — but the loop is still at STNO 160↔161, variable `i` incrementing
to 2,000,001. Raising `&STLIMIT` to any value does not help.

**Diagnosis**:
```c
/* Statement 161 — beautiful.c */
_stmt_152: {  /* L161 */
    SnoVal _subj = sno_var_get(sno_to_str(sno_var_get("UTF_Array")));
    int _ok = sno_match_and_replace(&_subj,
                  sno_pat_epsilon(),
                  sno_subscript_get2(sno_var_get("UTF_Array"),
                                     sno_var_get("i"),
                                     SNO_INT_VAL(1LL)));
    sno_var_set(sno_to_str(sno_var_get("UTF_Array")), _subj);
    if (_ok) goto SNO_G1;   /* loop back to stmt 160: i = i + 1 */
    else     goto _stmt_153; /* exit loop */
}
```
The loop exit condition is `_ok == 0` (match failure). This fires when
`sno_subscript_get2(UTF_Array, i, 1)` returns a value that causes the
match to fail — i.e. when `i` is past the end of the array.

`sno_subscript_get2` is returning a value for every `i` (likely
`SNO_NULL_VAL` or empty string) rather than signaling end-of-array.
The pattern `sno_pat_epsilon()` matches the empty string, so even a
null subscript result causes `_ok = 1` and the loop continues.

**Root Cause**: Two interacting bugs:
1. `sno_subscript_get2` does not return a sentinel that signals
   out-of-bounds — it returns NULL_VAL or empty string for any `i`.
2. `sno_pat_epsilon()` matches NULL_VAL/empty string, so the replacement
   always succeeds regardless of subscript result.

In SNOBOL4 semantics, accessing a nonexistent array element should either
(a) fail the statement (causing the `F:` branch — `goto _stmt_153`), or
(b) return an uninitialized value that causes the match to fail.
CSNOBOL4 takes approach (a): out-of-bounds subscript causes statement failure.

**Fix**: `sno_subscript_get2` must return a failure signal when `i` is
out of bounds. The emitter's match-and-replace wrapper must propagate
that signal as `_ok = 0`.

**Files to change**: `snobol4.c` (`sno_subscript_get2`), possibly `emit_c_stmt.py`
**Status**: DIAGNOSING

---

## P002 — sno_subscript_get / get2 Never Signals Out-of-Bounds Failure
**Date**: 2026-03-10
**Found by**: Double-trace monitor — binary STNO stream, STNO 160↔161 looping, VAR i incrementing to 92000+
**Symptom**: `./beautiful < beauty.sno` hangs. Variable `i` increments without bound in a SNOBOL4 array-iteration loop.

**Diagnosis**:
```
STNO 160   VAR i "92018"
STNO 161   VAR  ""
STNO 160   VAR i "92019"
...forever
```
Statement 161: `UTF_Array = UTF_Array` with replacement `UTF_Array[i][1]` using epsilon pattern.
When `i` exceeds array bounds, `sno_array_get2` returned `SNO_NULL_VAL` (valid value).
`sno_match_and_replace` with epsilon pattern always succeeds — null replacement is a valid empty string.
`_ok = 1` always → goto STNO 160 forever.

**SNOBOL4 semantics**: `arr[i]` where `i` is out of bounds **fails** — takes the F-branch.
Our runtime had no failure sentinel distinct from null.

**Root Cause**:
1. `sno_array_get` and `sno_array_get2` in `snobol4.c` returned `SNO_NULL_VAL` on out-of-bounds — indistinguishable from a valid empty string result.
2. No `SNO_FAIL` type existed in the runtime.
3. `sno_match_and_replace` did not check if the replacement value signalled failure.

**Fix**:
1. Added `SNO_FAIL = 10` to `SnoType` enum in `snobol4.h`
2. Added `SNO_FAIL_VAL` macro and `sno_is_fail()` inline to `snobol4.h`
3. `sno_array_get`: return `SNO_FAIL_VAL` when `!a` or index out of bounds
4. `sno_array_get2`: return `SNO_FAIL_VAL` when `!a`, row out of bounds, or col out of bounds
5. `sno_match_and_replace`: return 0 (fail) immediately if `sno_is_fail(replacement)`
6. `sno_to_str` / `sno_to_int` / `sno_to_real`: existing `default:` cases handle `SNO_FAIL` safely

**Verification**:
- Unit test `test_p002.c`: `arr[0]`, `arr[4]` → `SNO_FAIL`; `arr[1]`, `arr[3]` → correct values. PASS.
- `match_and_replace` with `SNO_FAIL_VAL` → returns 0. PASS.
- `smoke_gaps`: 40/40. No regressions.

**Files changed**: `snobol4.h`, `snobol4.c`, `snobol4_pattern.c`

---

## P003 — Conditional Expression Failure Not Propagated as Statement Failure
**Date**: 2026-03-10
**Found by**: P002 fix breaking loop at STNO 161, exposing next loop at STNO 578-579
**Symptom**: After P002, binary advances past statement 161 but loops at STNO 578↔579.
`&STCOUNT` reaches 10,000,000+ with no output produced.

**Source SNOBOL4** (beauty.sno line 578):
```snobol4
findRefs_0  n  =  LT(n, n(x)) n + 1  :F(FRETURN)
```
Semantics: if `LT(n, n(x))` fails (n >= n(x)), the entire statement fails → `FRETURN`.
If LT succeeds, `n + 1` is the result, assigned to `n`, falls through to line 579.

**Generated C** (beautiful.c statement 578):
```c
sno_var_set("n", SNO_STR_VAL(sno_concat(
    sno_to_str((sno_lt(...) ? sno_var_get("n") : SNO_NULL_VAL)),
    sno_to_str(sno_add(sno_var_get("n"), SNO_INT_VAL(1LL))))));
goto _stmt_1060;  /* always falls through — :F(FRETURN) never fires */
```
The ternary `(sno_lt(...) ? n : NULL)` silently produces empty string on failure,
then concatenates with `n+1`, producing `"1"`, `"2"`, etc. — a non-null string.
The assignment always succeeds. The `:F(FRETURN)` branch is never taken.

**Root Cause**: The emitter translates conditional SNOBOL4 expressions
(functions that succeed/fail) into C ternary expressions that swallow failure.
Failure of `LT(...)` → `SNO_NULL_VAL` in the ternary → concatenated away → lost.
The statement-level `_ok` flag is never set to 0 because the emitter doesn't
propagate function-call failure through expressions.

**The Pattern**: This is pervasive. Any SNOBOL4 statement of the form:
```snobol4
var = F(...) expr  :F(label)
```
where `F` is a success/fail function (LT, GT, EQ, DIFFER, IDENT, etc.) used
inside an expression — the failure is silently converted to empty string
rather than failing the statement and branching to `:F(label)`.

**Fix Required**: The emitter must generate code where function-call failure
inside an expression propagates as statement failure. Options:
1. Use `SNO_FAIL_VAL` as the ternary false-branch result, then check
   `sno_is_fail` on the final expression result before assignment.
2. Use `setjmp`/`longjmp` for failure propagation through expressions.
3. Restructure emitter to generate if/goto chains instead of ternary expressions.

Option 1 is the least invasive — extend the existing `SNO_FAIL` mechanism.
Check `sno_is_fail(result)` before `sno_var_set`, branch to fail label if true.

**Files to change**: `emit_c_stmt.py` (expression emission), `snobol4.c` (var_set check)
**Status**: P1 — blocks all progress. Every loop in beautiful.sno uses this pattern.

---

## P003 — UPDATE: Root Cause Is Flat Function Emission
**Date**: 2026-03-10 (update)
**Status**: PARTIAL — FAIL propagation works, but exposed deeper architectural issue

### What Was Fixed
- `emit_c_stmt.py`: comparison functions (LT/GT/EQ/NE/IDENT/DIFFER/LE/GE) now emit `SNO_NULL_VAL : SNO_FAIL_VAL` (correct SNOBOL4 semantics — these return empty string on success)
- `emit_c_stmt.py`: Case 2 (assignment) and Case 5 (OUTPUT=) now check `sno_is_fail(_rhs)` before assigning
- `snobol4.c`: added `sno_concat_sv(SnoVal a, SnoVal b)` — propagates `SNO_FAIL_VAL` if either operand is FAIL
- `emit_c_stmt.py`: `concat` node now emits `sno_concat_sv(a, b)` instead of `SNO_STR_VAL(sno_concat(sno_to_str(a), sno_to_str(b)))`

### The Deeper Problem: Flat Function Emission
The program exits after only 514 trace steps with `exit: 1`.

**Root cause**: All SNOBOL4 functions are emitted as goto-labels inside a single flat `sno_program()` C function. There is only ONE `SNO_RETURN_LABEL` and ONE `SNO_FRETURN_LABEL` at the bottom of `sno_program()`. When `findRefs` hits `FRETURN` (loop exit condition fires), it jumps to the top-level FRETURN which does `return 1` — exiting the **entire program**, not returning from `findRefs`.

Meanwhile, `sno_apply("findRefs", ...)` doesn't call the inlined goto code at all — it dispatches to the null stub registered by `sno_define_spec`. So function calls both:
1. Don't actually call the function body
2. When the body IS reached via inline goto, RETURN/FRETURN exits the program

### Fix Required: Per-Function C Functions
Each SNOBOL4-defined function must be emitted as its own C function:

```c
/* DEFINE('findRefs(x)n,v') → entry label: findRefs_ */
static SnoVal sno_uf_findRefs(SnoVal *_args, int _nargs) {
    SnoVal x = (_nargs > 0) ? _args[0] : SNO_NULL_VAL;
    SnoVal n = SNO_NULL_VAL;  /* local */
    SnoVal v = SNO_NULL_VAL;  /* local */
    
    /* function body via goto labels */
    goto SNO_findRefs_;
    
SNO_findRefs_: ...
SNO_findRefs_0: ...
...

SNO_RETURN_LABEL:  return SNO_NULL_VAL;  /* returns FROM THIS FUNCTION */
SNO_FRETURN_LABEL: return SNO_FAIL_VAL;  /* signals failure to caller */
}
```

`sno_define` registers `sno_uf_findRefs` as the handler. `sno_apply("findRefs", ...)` calls it directly. RETURN/FRETURN are local to the function.

### Implementation Plan
1. **Parse function sections**: scan for DEFINE statements that set entry labels (e.g. `DEFINE('findRefs(x)n,v', 'findRefs_')`) — extract name, params, locals, entry label.
2. **Partition statements**: assign each statement to its enclosing function section (from entry label to next function's entry label, or END).
3. **Emit each function** as a separate C function with its own RETURN/FRETURN labels.
4. **Register with `sno_define`**: emit a registration call at program start.
5. **Main program section**: statements before first function definition only.

### Variables: Scoping Issue
SNOBOL4 params and locals must be saved/restored across calls (they're scoped per invocation). For now: use a global var table (already in place via `sno_var_get/set`), push/pop on entry/exit. Add `sno_func_enter(params, locals, nargs, args)` and `sno_func_exit()` to handle save/restore.

**Files to change**: `emit_c_stmt.py` (major restructure), `snobol4.c` (func enter/exit), `snobol4.h` (declarations)
**Commit**: 4a37a81 (WIP)

---

## P003 SESSION UPDATE (2026-03-10) — per-function emission + pattern fix chain

### Done this session:

**Compile fixed (was: 3 missing labels)**
- `findRefs_1`: parser mis-labels call as stmt → synthesized label from subj.name when name is in goto_targets & not func entry
- `io_end`/`lwr_end`: residual transfer on merge fixed; residuals stay in main flow
- `IsSnobol4`/`XDump` duplicate labels: synthesized label heuristic tightened (not func entries)
- `x`/`c` indirect gotos: emit `_sno_ind_x` stubs → `sno_indirect_goto(varname)` at runtime

**INPUT/OUTPUT wired** — `sno_var_get("INPUT")` calls `sno_input_read()`

**First real output: 7 comment lines** (commit `8e946d1`)

**Pattern emission chain:**
- `| alt` in function args: `_ExprParser.parse_alt()` added → FENCE/ARBNO args now have alt nodes
- `*var` indirect ref: `mul(null, var)` → `sno_pat_ref("name")`
- Pattern-aware concat: if either side is pattern → `sno_pat_cat`
- Array on pattern base → `sno_pat_assign_cond` (PAT ~ expr)
- `snoParse` now type=5 (PATTERN) ✓

### Still failing (STNO 619):

`snoSrc POS(0) *snoParse *snoSpace RPOS(0) :F(mainErr1)` fails on `"START\n"`.

Root cause: inside pattern construction for `snoCommand`/`snoStmt`, two issues remain:
1. `mul(PATTERN, var)` = `*PAT var` in pattern context = `pat_cat(PAT_REF, pat_ref(var))`. Currently emitted as `sno_mul(pat, var)` which is wrong.
2. `mul(NULL_VAL, complex_expr)` where complex_expr is not a simple var name (e.g., `mul(null, var_get(to_str(",")))`) → we'd need `sno_pat_ref_val(expr)` instead of `sno_pat_ref("name")`.

**Next fix needed**: In `emit_expr` for `mul`, when either operand involves a pattern, interpret `*X` as `pat_cat(pat_ref_of(X), ...)` in pattern concat context. Specifically:
- `mul(A, B)` where `_is_pattern_expr(A)` or A.kind=='null' → pattern context → if A.kind=='null': `sno_pat_ref_val(emit_expr(B))`
- `mul(PAT, VAR)` = `PAT * VAR` in pattern context = `sno_pat_cat(emit_as_pattern(PAT), sno_var_as_pattern(emit_expr(VAR)))`

The SNOBOL4 `*` operator is overloaded: arithmetic multiply OR pattern deferred-ref. Parser doesn't know which — emitter must infer from context.

## session121 — Bug7 Bomb Protocol

### Trace infrastructure (built this session, NOT committed to repo)

**Oracle trace:** copy `/home/claude/snobol4corpus/programs/inc/counter.sno` to `/tmp/inc_trace/counter.sno` with `PushCounter/IncCounter/PopCounter` shadowed to write `NPUSH/NINC/NPOP depth=N top=N` to `TERMINAL`. Run:
```bash
INC=/tmp/inc_trace
snobol4 -f -P256k -I$INC $BEAUTY < input > /dev/null 2>oracle_stack.txt
```

**Compiled trace:** instrument `snobol4.c` `NPUSH_fn/NINC_fn/NPOP_fn` with `fprintf(stderr,...)`. Normalize compiled depth (+1) vs oracle (1-based). Diff.

**First divergence confirmed:**
- Line 1 (match): `NPUSH depth=1 top=0`
- Line 2 oracle: `NINC  depth=1 top=1`
- Line 2 compiled: `NPUSH depth=2 top=0` ← spurious ghost frame

### Bomb Protocol — next session executes this

**Pass 1:** Add `static int _npush_count=0;` to `snobol4.c`. In `NPUSH_fn()` increment and print `#N`. Run on `109_multi.input`. Spurious call is #2.

**Pass 2:** Add `bomb_limit=2`. When `_npush_count==bomb_limit`: print `_ntop`, `_nstack[]`, call `backtrace()+backtrace_symbols_fd()`. Compile with `-rdynamic`. Run. Backtrace identifies exact C label in `beauty_full.c` → maps to emit_byrd.c node missing `NPOP_fn()` on ω path.

**WARNING — double-pop trap:** Earlier attempt added `NPOP_fn()` interpose in `emit_alt` on left-arm ω. This caused double-pop because `cat_r_N_β` (child backtrack) also routes through `cat_l_N_β` → interpose. Only add NPOP on the **first-fail** ω path, not backtrack paths. The bomb backtrace will show exactly which path to fix.

### Key files
- `src/sno2c/emit_byrd.c` — fix goes here
- `src/runtime/snobol4/snobol4.c` — bomb goes here (revert after fix)
- `beauty_full.c` — regenerated by `sno2c -trampoline -I$INC $BEAUTY`
- `/tmp/inc_trace/counter.sno` — oracle trace (rebuild each session from counter.sno)
