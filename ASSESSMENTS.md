# SNOBOL4-plus — Assessments

Unified tracking of test suite status, conformance, known gaps, and
cross-platform compatibility across all implementations.

---

## Current Status Summary

| Repo | Tests | Failures | Oracles | Last Confirmed |
|------|------:|--------:|---------|----------------|
| SNOBOL4-dotnet | 1,607 | 0 | SPITBOL v4.0f, CSNOBOL4 2.3.3 | 2026-03-10 |
| SNOBOL4-jvm | 1,896 (4,120 assertions) | 0 | SPITBOL v4.0f, CSNOBOL4 2.3.3 | 2026-03-10 |
| SNOBOL4-python | — | — | — | 2026-03-02 |
| SNOBOL4-csharp | 263 | 0 | — | 2026-03-07 |
| SNOBOL4-cpython | 70+ (`tests/test_bead.py`) | 0 | SNOBOL4python patterns | 2026-03-10 — `SNOBOL4-plus/SNOBOL4-cpython` |
| SNOBOL4-tiny | 7 oracles (Sprints 0–3) | 0 | emit_c.py hand-written oracles | 2026-03-10 |

---
---

## SNOBOL4-dotnet Assessment

**Test runner**: `dotnet test TestSnobol4/TestSnobol4.csproj -c Release`
**Total**: 1,466 passing / 0 failing

### Test Catalog — SNOBOL4-dotnet

| Group | Status | Notes |
|-------|--------|-------|
| ThreadedCompilerTests | ✅ pass | |
| ThreadedExecutionTests | ✅ pass | |
| SlotResolutionTests | ✅ pass | |
| Numeric (95 tests) | ✅ pass | |
| Pattern (most groups) | ✅ pass | |
| Pattern.Bal | ⛔ excluded | Hangs in threaded execution — excluded via `--filter` |
| FunctionControl.Define (8) | ✅ pass | |
| FunctionControl.Apply (5) | ✅ pass | |
| FunctionControl.Opsyn | ✅ pass | TEST_Opsyn_001 skipped (requires AreaLibrary.dll) |
| Function.InputOutput | ⛔ excluded | Hangs on Linux (hardcoded Windows file paths) |
| Gimpel | ✅ pass | |
| ArraysTables | ✅ pass | |
| StringComparison | ✅ pass | |
| StringSynthesis | ✅ pass | |
| LOAD/UNLOAD plugin system | ✅ pass | All 1,466 pass including LOAD :F branch, real coercion, unload/reload |
| MSIL emitter (Steps 1–13) | ✅ pass | |
| TRACE hooks (Step 13) | ✅ pass | |

### Known Gaps — SNOBOL4-dotnet

| # | Issue | Severity |
|---|-------|----------|
| 1 | Pattern.Bal — hangs under threaded execution | Medium |
| 2 | Deferred expressions in patterns `pos(*A)` — TEST_Pos_009 | Low |
| 3 | TestGoto _DIRECT — CODE() dynamic compilation | Medium |
| 4 | OPSYN custom operator `!` alias | Low |
| 5 | ~~DLL loading tests require local build of AreaLibrary.dll~~ — **Fixed** 2026-03-10: all plugin DLLs auto-built via `ProjectReference` in `TestSnobol4.csproj` | ✅ Fixed |
| 6 | Function.InputOutput — hangs on Linux (hardcoded Windows paths) | Low |

---
---

## SNOBOL4-jvm Assessment

**Test runner**: `lein test`
**Total**: 2,033 tests / 4,417 assertions / 0 failures
**Last confirmed**: 2026-03-09 commit `e697056`

### What Is Solidly Working — SNOBOL4-jvm

- **Full arithmetic**: integer, real, mixed-mode, `**` exponentiation, REMDR, division truncation (verified vs v311.sil)
- **String operations**: concatenation, SIZE, TRIM, REPLACE, DUPL, LPAD, RPAD, REVERSE, SUBSTR
- **Pattern engine**: LEN, TAB, RTAB, ANY, NOTANY, SPAN, BREAK, BREAKX, POS, RPOS, BOL, EOL, ARB, ARBNO, FENCE, ABORT, BAL, REM, CONJ, deferred `*var` patterns
- **Capture**: `$` immediate and `.` conditional on match success — both correct
- **Control flow**: GOTO, :S/:F, computed goto, DEFINE/RETURN/FRETURN, recursive functions, APPLY
- **Data structures**: TABLE, ARRAY (multi-dim), DATA/FIELD (PDD)
- **Type system**: DATATYPE, CONVERT, all coercions, INTEGER/REAL/STRING predicates
- **Indirect addressing**: `$sym` read/write, NAME dereference through subscripts
- **I/O**: OUTPUT, INPUT (stdin), TERMINAL (stderr), named file channels (INPUT/OUTPUT with unit+file)
- **Preprocessor**: `-INCLUDE` recursive with cycle detection
- **CODE(src)**: compile and run a SNOBOL4 string in current environment
- **OPSYN**: operator redefinition — binary and unary

### Test Catalog — SNOBOL4-jvm

| Catalog | Tests | Coverage |
|---------|------:|---------|
| t_arith | 194 | Arithmetic operators, integer/real |
| t_assign | 43 | Assignment, indirect, NAME |
| t_compare | 72 | LT/GT/EQ/NE/LGT/IDENT/DIFFER |
| t_string | 24 | String operations, REPLACE, SIZE |
| t_patterns_prim | 78 | ALL primitives: ANY/SPAN/BREAK/etc |
| t_patterns_cap | 10 | Capture operators $ and . |
| t_patterns_adv | 11 | Advanced: FENCE, ABORT, BAL, CONJ |
| t_goto | 8 | GOTO, :S, :F, label resolution |
| t_loops | 8 | Loop idioms, counter patterns |
| t_define | 16 | DEFINE/DATA/FIELD, recursion, APPLY |
| t_array | 7 | ARRAY, multi-dim, bounds |
| t_convert | 28 | CONVERT, type coercion matrix |
| t_algorithms | 11 | Sorting, searching algorithms |
| t_gimpel | 24 | Gimpel corpus (135 routines) |
| t_aisnobol | 12 | Shafto AI corpus (SNOLISPIST) |
| t_spitbol | 44 | SPITBOL testpgms corpus |
| t_include | 5 | -INCLUDE preprocessor |
| t_terminal | 2 | TERMINAL I/O |
| t_code | 4 | CODE() dynamic compilation |
| t_io | 13 | Named I/O channels |
| t_opsyn | 11 | OPSYN operator redefinition |
| t_missing | 3 | LGT and other recovered gaps |
| t_worm_patterns | 23 | Worm-generated pattern tests |
| t_worm_algorithms | 12 | Worm-generated algorithm tests |
| t_worm_expr_parser | 19 | Worm-generated expression parser tests |
| t_worm_t3t5 | 47 | Worm T3-T5 band tests |

### Known Gaps — SNOBOL4-jvm

| # | Issue | Status |
|---|-------|--------|
| 1 | CAPTURE-COND (`.`) assigns immediately like `$` — deferred-assign not yet built | Open |
| 2 | ANY(multi-arg) inside EVAL string — ClassCastException | Open |
| 3 | Sprint 23E — inline EVAL! in JVM codegen (arithmetic bottleneck) | Next sprint |

### Oracle Validation — SNOBOL4-jvm

Three-oracle cross-check on every test:
- **SPITBOL v4.0f** — primary oracle (built from source)
- **CSNOBOL4 2.3.3** — secondary oracle (built from source)
- **SNOBOL4clojure** — our implementation

Triangulation: both agree → use agreed output. Disagree → use SPITBOL, flag for review.
1,500 systematic programs validated via three-oracle harness — 1,499 pass, 1 skip, 0 fail.

### Corpus Coverage — SNOBOL4-jvm

| Corpus | Tests | Status |
|--------|-------|--------|
| Worm T0–T5 bands (catalog) | ~1,400 | All green |
| Gimpel *Algorithms in SNOBOL4* | 24 | All green |
| Shafto *AI Programming in SNOBOL4* | 12 | All green |
| SPITBOL testpgms test1/2/3 | 31 | All green |
| SPITBOL testpgms test4 | 2 | All green (Sprint 19) |
| Jeffrey Cooper / Snobol4.Net | partial | `t_cooper.clj` |

---
---

## SNOBOL4-python Assessment

**Version**: 0.5.1 (published to PyPI)
**Backends**: C/SPIPAT (default), pure Python (fallback)

Test suite details to be documented. Dual backend conformance cross-check pending.

---
---

## SNOBOL4-csharp Assessment

**Total**: 263 passing / 0 failing
**Test runner**: `dotnet test tests/SNOBOL4.Tests`

| Test File | Coverage |
|-----------|---------| 
| Tests_Primitives | All primitives |
| Tests_01 | identifier, real_number, bead, bal, arb |
| Tests_Arbno | ARBNO patterns |
| Tests_RE_Grammar | Recursive RE grammar with Shift/Reduce |
| Tests_Env | Capture operators, TRACE, NSPAN |
| Tests_CLAWS | CLAWS5 NLP corpus parser |
| Tests_TreeBank | Penn Treebank parenthesized-tree parser |
| Tests_Porter | Porter Stemmer — 23,531-word corpus |
| Tests_Snobol4Parser | SNOBOL4 source code parser |
| Tests_JSON | ⚠️ Disabled — pending port to delegate-capture API |

---
---

## Cross-Platform Conformance

*The goal: identical output from all implementations on the same programs.*

### SNOBOL4 Standard Conformance

Both full implementations (dotnet, jvm) target Emmer & Quillen's
*MACRO SPITBOL* as the specification, with Griswold, Poage & Polonsky's
*The SNOBOL4 Programming Language* as the base.

| Feature | dotnet | jvm | Notes |
|---------|--------|-----|-------|
| GOTO-driven execution | ✅ | ✅ | |
| Pattern matching | ✅ | ✅ | |
| DEFINE / DATA / FIELD | ✅ | ✅ | |
| CODE() | ✅ | ✅ | |
| EVAL() | ✅ | ✅ | |
| OPSYN | ✅ | ✅ | |
| TABLE / ARRAY | ✅ | ✅ | |
| Named I/O channels | ✅ | ✅ | |
| -INCLUDE preprocessor | ✅ | ✅ | |
| TRACE / STOPTR | ✅ | ✅ | |
| LOAD / UNLOAD (plugins) | ✅ | ❌ | dotnet only — C# / F# plugins |
| Windows GUI | ✅ | ❌ | dotnet Snobol4W.exe |
| Unicode | ✅ | ✅ | |

### Shared Test Programs (planned)

Programs that should run identically on dotnet and jvm, and produce compatible
pattern results on python and csharp:

| Program | dotnet | jvm | python | csharp | Notes |
|---------|--------|-----|--------|--------|-------|
| Roman numerals | — | — | — | — | Pending |
| Fibonacci | — | — | — | — | Pending |
| Vowel counter | — | — | — | — | Pending |
| Gimpel INFINIP | — | — | n/a | n/a | Infinite-precision arithmetic |
| Gimpel POKER | — | — | n/a | n/a | Poker simulator |

### Known Cross-Platform Gaps

| Gap | Repos Affected | Notes |
|-----|---------------|-------|
| CAPTURE-COND deferred semantics | jvm, python, csharp | `.` assigns immediately in jvm; deferred in python/csharp |
| ANY charset range syntax `"A-Z"` | jvm | jvm treats `-` as literal (standard SNOBOL4). python/csharp TBD. |

---
---

## SNOBOL4-cython Assessment

**Status**: Proof-of-concept. Not yet in org repo — source in uploaded zips only.
**Build**: `python3 setup.py build_ext --inplace` → `snobol4c.cpython-312-*.so`
**Test runner**: `python3 test_bead.py`
**Total**: 70+ tests / 0 failures (v2)

### What It Is

A CPython C extension (`snobol4c_module.c`) implementing the full Byrd Box
SNOBOL4 pattern engine in portable C. Python side uses SNOBOL4python objects
to build the pattern tree; the extension converts them to C structs and matches
entirely in C. Returns `(start, end)` or `None`.

### Test Coverage — SNOBOL4-cython

| Group | Tests | Status |
|-------|------:|--------|
| BEAD pattern (complex alternation) | 10 | ✅ pass |
| BEARDS pattern (nested alternation) | 7 | ✅ pass |
| Literal σ | 4 | ✅ pass |
| ANY / SPAN / BREAK | 7 | ✅ pass |
| LEN / TAB / RTAB / REM | 7 | ✅ pass |
| ARB | 3 | ✅ pass |
| ARBNO | 5 | ✅ pass |
| ε (epsilon) | 2 | ✅ pass |
| π (optional ~σ) | 3 | ✅ pass |
| FENCE | 1 | ✅ pass |
| BAL | 3 | ✅ pass |
| FAIL / SUCCEED | 1 | ✅ pass |
| NOTANY | 2 | ✅ pass |
| search() unanchored | 1 | ✅ pass |

### Architecture Notes

- **v1**: bump Arena allocator (slab of Pattern nodes freed all at once)
- **v2**: per-node `malloc` + `PatternList` tracker — cleaner, no relocation risk
- Engine: `PROCEED/SUCCESS/FAILURE/RECEDE` × node-type dispatch (`type << 2 | signal`)
- Psi (continuation stack) + Omega (backtrack stack with owned Psi snapshots)
- Three Python-facing functions: `match`, `search`, `fullmatch`

### Decision Pending

Add as `SNOBOL4-cython` org repo, or fold `snobol4c_module.c` into
SNOBOL4-python as an alternative backend to SPIPAT? See PLAN.md Outstanding
Items — SNOBOL4-tiny P2.
