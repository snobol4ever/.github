# SNOBOL4-plus — Assessments

Unified tracking of test suite status, conformance, known gaps, and
cross-platform compatibility across all implementations.

---

## Current Status Summary

| Repo | Tests | Failures | Oracles | Last Confirmed |
|------|------:|--------:|---------|----------------|
| SNOBOL4-dotnet | 1,484 | 0 | — | 2026-03-07 |
| SNOBOL4-jvm | 2,033 (4,417 assertions) | 0 | SPITBOL v4.0f, CSNOBOL4 2.3.3 | 2026-03-09 |
| SNOBOL4-python | — | — | — | 2026-03-02 |
| SNOBOL4-csharp | 263 | 0 | — | 2026-03-07 |

---

## SNOBOL4-dotnet Test Catalog

**Test runner**: `dotnet test TestSnobol4/TestSnobol4.csproj -c Release`
**Total**: 1,484 passing / 0 failing

| Group | Status | Notes |
|-------|--------|-------|
| ThreadedCompilerTests | ✅ pass | |
| ThreadedExecutionTests | ✅ pass | |
| SlotResolutionTests | ✅ pass | |
| Numeric (95 tests) | ✅ pass | |
| Pattern (most groups) | ✅ pass | |
| FunctionControl.Define (8) | ✅ pass | |
| FunctionControl.Apply (5) | ✅ pass | |
| Gimpel | ✅ pass | |
| ArraysTables | ✅ pass | |
| StringComparison | ✅ pass | |
| StringSynthesis | ✅ pass | |
| LOAD/UNLOAD plugin system | ✅ pass | 1,413 → 1,484 range |
| MSIL emitter (Steps 1–12) | ✅ pass | |
| TRACE hooks (Step 13) | ✅ pass | |

### Known Gaps — SNOBOL4-dotnet

| # | Issue | Severity |
|---|-------|----------|
| 1 | Pattern.Bal — hangs under threaded execution | Medium |
| 2 | Deferred expressions in patterns `pos(*A)` — TEST_Pos_009 | Low |
| 3 | TestGoto _DIRECT — CODE() dynamic compilation | Medium |
| 4 | OPSYN custom operator `!` alias | Low |
| 5 | DLL loading tests require local build of AreaLibrary.dll | Low |
| 6 | Function.InputOutput — hangs on Linux (hardcoded Windows paths) | Low |

---

## SNOBOL4-jvm Test Catalog

**Test runner**: `lein test`
**Total**: 2,033 tests / 4,417 assertions / 0 failures
**Last confirmed**: 2026-03-09

### Test Catalogs (28 files)

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
| t_gimpel | — | Gimpel corpus (135 routines) |
| t_aisnobol | — | Shafto AI corpus (SNOLISPIST) |
| t_spitbol | — | SPITBOL testpgms corpus |
| t_include | 5 | -INCLUDE preprocessor |
| t_terminal | 2 | TERMINAL I/O |
| t_code | 4 | CODE() dynamic compilation |
| t_io | 13 | Named I/O channels |
| t_io_channels | — | Channel edge cases |
| t_opsyn | 11 | OPSYN operator redefinition |
| t_missing | 3 | LGT and other recovered gaps |
| t_worm_patterns | 23 | Worm-generated pattern tests |
| t_worm_algorithms | 12 | Worm-generated algorithm tests |
| t_worm_expr_parser | 19 | Worm-generated expression parser tests |
| t_worm_t3t5 | 47 | Worm T3-T5 band tests |
| t_patterns_ext | — | Extended pattern tests |

### Known Gaps — SNOBOL4-jvm

| # | Issue | Status |
|---|-------|--------|
| 1 | CAPTURE-COND (`.` operator) assigns immediately like `$` — deferred-assign not yet built | Open |
| 2 | ANY(multi-arg) inside EVAL string — ClassCastException | Open |
| 3 | Sprint 23E — inline EVAL! in JVM codegen (arithmetic bottleneck) | Next sprint |

### Oracle Validation — SNOBOL4-jvm

Three-oracle cross-check on every test:
- **SPITBOL v4.0f** — primary oracle (built from source)
- **CSNOBOL4 2.3.3** — secondary oracle (built from source)
- **SNOBOL4clojure** — our implementation

Triangulation: both agree → use agreed output. Disagree → use SPITBOL, flag for review.
1,500 systematic programs validated via three-oracle harness — 1,499 pass, 1 skip, 0 fail.

---

## SNOBOL4-python

**Version**: 0.5.1 (published to PyPI)
**Backends**: C/SPIPAT (default), pure Python (fallback)

Test suite details to be documented. Dual backend conformance cross-check pending.

---

## SNOBOL4-csharp

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

## Cross-Platform Conformance

*The goal: identical output from all implementations on the same programs.*

### Shared Test Programs (planned)

Programs that should run identically on dotnet, jvm, and produce compatible
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
| ANY charset range syntax `"A-Z"` | jvm | jvm treats `-` as literal (standard). Python/csharp TBD. |

---

## Conformance Against Reference

### SNOBOL4 Standard Conformance

Both full implementations (dotnet, jvm) target Emmer & Quillen's
*MACRO SPITBOL* as the specification, with the original
*The SNOBOL4 Programming Language* (Griswold, Poage, Polonsky) as the base.

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

