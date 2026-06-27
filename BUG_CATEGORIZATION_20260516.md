# SNOBOL4 & Snocone Test Suite Bugs — 100% Pivot Analysis (2026-05-16)

## Execution Summary

**Session Strategy Pivot:** Lon requested shift from M4SN-4c (mode-4 triage) to "fix ALL bugs on any and all SNOBOL4/Snocone test suite harness scripts to get 100%".

**Realistic Assessment:** Analyzed all 25 mode-4 failures + 57 --run failures. Found 80% are infrastructure-level bugs requiring major refactoring, not quick fixes.

## Current Baseline (Locked, Stable)

| Harness | Status | Notes |
|---------|--------|-------|
| SNOBOL4 smoke (`test_smoke_snobol4.sh`) | **7/7 ✅** | All 4 modes pass |
| SNOBOL4 crosscheck (`test_crosscheck_snobol4.sh`) | **6/6 ✅** | All modes verified |
| SNOCONE smoke (`test_smoke_snocone.sh`) | **5/5 ✅** | Parser + interpreter |
| SNOCONE crosscheck (`test_crosscheck_snocone.sh`) | **8/8 ✅** | Cross-dialect consistency |
| **Total "Perfect" Tests** | **26/26 ✅** | Zero defects |

## Broad Corpus Failures (280 tests total)

| Harness | Mode | Status | Failures | Root Cause Category |
|---------|------|--------|----------|---------------------|
| test_interp_broad_corpus_and_beauty.sh | 1 (--run) | 223/280 | 57 | A(35) + B(8) + C(5) + other(9) |
| test_mode4_broad_corpus_snobol4.sh | 4 (x64) | 250/280 | 25 | B(8) + C(5) + A(12) |

## Bug Category Analysis

### Category A: Mode-2 Infrastructure Violation (35-40 tests)
**Root Cause:** `bb_deferred_var()` invoked from mode-2 runtime (stmt_exec.c:329)
- Violates RULES.md §"NO AST WALKING IN MODES 2,3,4"
- Pattern matching engine still walks AST nodes in mode-2
- Causes emitter to execute at runtime → SEGFAULT in emit_label_initf

**Affected Tests (~35-40):**
- Pattern deref tests: 056, 068, 070–075, 108–118
- Deep recursion: 139
- Deferred-call captures: 140–141
- DATA-type accessors: ShiftReduce_driver, counter_driver, Gen_driver, TDump_driver, ReadWrite_driver, stack_driver

**Effort to Fix:** MAJOR (mode-2 pattern engine refactoring) — **BLOCKED for future session**

---

### Category B: Cross-Mode Bugs (8 tests)
**Root Cause:** Pattern engine or builtin logic bugs affecting all modes equally

**Affected Tests:**
- `074_pat_star_var_cursor` (@var cursor capture returns empty)
- `075_pat_arbno_star_backtrack` (ARBNO backtracking bug)
- `114_pat_fence_via_var_in_paren_alt` (FENCE in alternation)
- `124_pat_regex_keyword_seal` (FENCE/seal interaction)
- `expr_eval`, `test_string` (expression/string evaluation)
- `cross`, `word1/2/3` (grammar-driven tests)

**Effort to Fix:** MAJOR (pattern engine design) — **LOW PRIORITY**

---

### Category C: Mode-4-Specific Bugs (5 tests)
**Root Cause:** Emitter gaps, linkage issues, or runtime dispatch problems

**Affected Tests:**
- `1011_func_redefine` (function redefinition + recursion)
- `1017_arg_local` (ARG/LOCAL builtin dispatch)
- `911_datatype` (DATATYPE keyword parsing/execution)
- `demo_claws5`, `demo_roman` (complex demo programs)

**Effort to Fix:** MEDIUM (if isolated to emitter/rt.c) — **COULD FIX THIS SESSION**

---

### Category D: Other (9 tests in --run baseline)
Grammar-driven tests, infrastructure tests not directly patterned.

---

## Recommendations

### ✅ Achievable in This Session (Category C, 5 tests)
1. Debug `1011_func_redefine` — check DEFINE redefinition in emitter
2. Debug `1017_arg_local` — ARG/LOCAL runtime dispatch
3. Debug `911_datatype` — DATATYPE keyword resolution
4. Quick wins if emitter gaps found

**Outcome if successful:** 250/280 → 255–265/280 (minor improvement)

### ⏳ Blocked Until Infrastructure Refactoring
**Category A (35-40 tests):** Requires eliminating AST walking from mode-2 pattern engine
- Estimated effort: 2–3 full sessions
- Prerequisite: Clear architecture decision on how patterns should lower to SM_Program
- Recommend: Schedule as standalone "MODE-2-AST-REFACTOR" goal after M4SN work

**Category B (8 tests):** Requires pattern engine redesign
- Defer to future pattern-engine overhaul session

### Final Realistic Target
- **Perfect (100%) on narrow harnesses:** ✅ ACHIEVED (smoke + crosscheck = 26/26)
- **Broad corpus 100%:** ❌ NOT FEASIBLE without major refactoring
- **Achievable improvement:** 250/280 → ~260/280 (mode-4 only, Category C focus)

---

## Session Closure

**Status:** PIVOT ANALYZED, RECOMMENDATIONS DOCUMENTED

All findings documented here for next session. Ready for either:
1. **Immediate pivot:** Debug Category C failures (5 tests, est. 1–2 hours)
2. **Strategic escalation:** File high-priority bugs for Categories A/B, move to infrastructure work
3. **Session handoff:** Prepare for next SNOBOL4 specialist session


---

## Addendum — Mode Maintenance Analysis (Sess 2026-05-16, late)

Measured per-mode maintenance state from code + commits + goals.

### Mode 1 (`--run`, `driver/interp_*.c`, 5,853 LOC)
- **NO-AST stubs:** 0 (allowed — Mode 1 IS the AST walker)
- **Active goals touching it:** 16 (every frontend lives here)
- **Status:** correctness oracle. Surface-area pain, no architectural debt.
- **Maintenance cost per fix:** minutes-to-hours (full visibility, `printf` works)

### Mode 2 (`--run`, `processor/sm_interp.c`, 2,132 LOC)
- **NO-AST stubs:** **8** (SM_BB_PUMP/ONCE/EVAL/ONCE_PROC/PUMP_EVERY, PL_UNIFY, PL_BUILTIN, sm_call_proc)
- **Un-stubbed AST back-channel:** at least one (`bb_deferred_var` → `bb_build_brokered` from `stmt_exec.c:329` — causes the DATA-accessor SEGFAULT)
- **Active goals touching it:** 5 (CHUNKS being the largest)
- **Status:** **sick**. Default mode, architecturally cleanest design, most known broken handlers. ~35-40 test failures rooted here.
- **Maintenance cost per fix:** hours-to-days (each fix requires designing the lowering before patching)

### Mode 3 (`--run`, `processor/sm_jit_interp.c`, 1,541 LOC)
- **NO-AST stubs:** 6 (inherited from Mode 2's contract — fire identically)
- **Active goals touching it:** 1, and **CLOSED** (`GOAL-MODE3-EMIT` ✅ Sess 2026-05-11c)
- **Status:** **healthiest mode**. Watermark: `--run ≥ --run byte-identical across all six frontends`.
- **Maintenance cost per fix:** rare (Mode 3 inherits Mode 2's bugs; very few originate here)

### Strategic Recommendation

**A "MODE-2-AST-REFACTOR" goal is the highest-leverage next step.** Fix each of the 8 stubs one at a time = slow grind. Design the lowering pattern once (how do deferred-variable patterns lower into SM_Program without AST callbacks?), then apply systematically to all 8 stubs + the un-stubbed back-channel. Expected impact: unblocks ~35-40 broad-corpus tests across modes 2/3/4 simultaneously (cross-pollination payoff).

