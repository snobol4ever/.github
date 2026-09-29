# MISC-STATUS.md — Test Baselines and Status

Test baselines, conformance, known gaps, and performance benchmarks across all implementations.

---

## Test Baselines

| Repo | Tests | Failures | Last Confirmed |
|------|------:|--------:|----------------|
| snobol4dotnet | 1,607 | 0 | 2026-03-10 `63bd297` |
| snobol4jvm | 1,896 (4,120 assertions) | 0 | 2026-03-10 `9cf0af3` |
| snobol4csharp | 263 | 0 | 2026-03-07 |
| snobol4artifact | 70+ | 0 | 2026-03-10 `330fd1f` |
| SCRIP | crosscheck ladder: output 7/8, assign 7/8 | 2 | 2026-03-15 `29c0a4b` — corpus ladder methodology adopted Session 89; null-assign + &ALPHABET bugs active |

**How to update**: run the test suite, paste the new count with date and commit hash.

---

## snobol4dotnet

**Runner**: `dotnet test TestSnobol4/TestSnobol4.csproj -c Release`

| Group | Status | Notes |
|-------|--------|-------|
| ThreadedCompilerTests | ✅ | |
| ThreadedExecutionTests | ✅ | |
| Numeric (95 tests) | ✅ | |
| Pattern (most groups) | ✅ | |
| Pattern.Bal | ⛔ excluded | Hangs in threaded execution |
| FunctionControl.Define/Apply/Opsyn | ✅ | TEST_Opsyn_001 skipped (requires AreaLibrary.dll) |
| Function.InputOutput | ⛔ excluded | Hangs on Linux (hardcoded Windows file paths) |
| Gimpel / ArraysTables / StringComparison | ✅ | |
| LOAD/UNLOAD plugin system | ✅ | |
| MSIL emitter (Steps 1–13) | ✅ | |
| TRACE hooks (Step 13) | ✅ | |
| Snocone Step 2 parser | ✅ | |

### Known Gaps

| # | Issue | Severity |
|---|-------|----------|
| 1 | Pattern.Bal — hangs under threaded execution | Medium |
| 2 | Deferred expressions `pos(*A)` — TEST_Pos_009 | Low |
| 3 | TestGoto _DIRECT — CODE() dynamic compilation | Medium |
| 4 | Function.InputOutput — Linux (hardcoded Windows paths) | Low |

### Test Suite History

| Branch | Tests |
|--------|------:|
| `rungs` (Roslyn) | 1,271 |
| threaded execution | 1,386 |
| post-threaded-dev | 1,413 |
| msil-emitter | 1,484 |
| main (merged) | 1,466 |
| after Snocone Step 2 | **1,607** |

---

## snobol4jvm

**Runner**: `lein test`

### What Is Working

Full arithmetic, string ops, pattern engine (all primitives), ARBNO, FENCE, BAL, CONJ, deferred `*var` patterns, `$`/`.` capture, TABLE/ARRAY, DEFINE/RETURN/FRETURN, recursive functions, APPLY, OPSYN, CODE(), -INCLUDE, named I/O, TERMINAL, TRACE/STOPTR.

### Known Gaps

| # | Issue | Status |
|---|-------|--------|
| 1 | CAPTURE-COND (`.`) assigns immediately — deferred-assign not built | Open |
| 2 | ANY(multi-arg) inside EVAL string — ClassCastException | Open |
| 3 | Sprint 23E — inline EVAL! in JVM codegen (arithmetic bottleneck) | Next |

### Test Suite History

| Sprint | Tests | Assertions | Failures |
|--------|------:|-----------:|---------:|
| Sprint 13 baseline | 220 | 548 | 0 |
| Sprint 18D | 967 | 2,161 | 0 |
| Sprint 18B | 1,488 | 3,249 | 0 |
| Session 11 | 1,749 | 3,786 | 0 |
| Session 12c | 1,865 | 4,018 | 0 |
| Sprint 19 | 2,017 | 4,375 | 0 |
| Sprint 25E | 2,033 | 4,417 | 0 |
| Snocone Step 2 | **1,896** | **4,120** | **0** |

---

## snobol4csharp

**Runner**: `dotnet test tests/SNOBOL4.Tests` — 263 / 0

| Test File | Coverage |
|-----------|---------|
| Tests_Primitives | All primitives |
| Tests_01 | identifier, real_number, bead, bal, arb |
| Tests_Arbno | ARBNO patterns |
| Tests_RE_Grammar | Recursive RE grammar with Shift/Reduce |
| Tests_CLAWS | CLAWS5 NLP corpus parser |
| Tests_TreeBank | Penn Treebank parenthesized-tree parser |
| Tests_Porter | Porter Stemmer — 23,531-word corpus |
| Tests_Snobol4Parser | SNOBOL4 source code parser |
| Tests_JSON | ⚠️ Disabled — pending port to delegate-capture API |

---

## Cross-Platform Conformance

Both full implementations (dotnet, jvm) target Emmer & Quillen's *MACRO SPITBOL* as spec, with Griswold, Poage & Polonsky's *The SNOBOL4 Programming Language* as base.

| Feature | dotnet | jvm |
|---------|:------:|:---:|
| GOTO-driven execution | ✅ | ✅ |
| Pattern matching | ✅ | ✅ |
| DEFINE / DATA / FIELD | ✅ | ✅ |
| CODE() | ✅ | ✅ |
| EVAL() | ✅ | ✅ |
| OPSYN | ✅ | ✅ |
| TABLE / ARRAY | ✅ | ✅ |
| Named I/O channels | ✅ | ✅ |
| -INCLUDE preprocessor | ✅ | ✅ |
| TRACE / STOPTR | ✅ | ✅ |
| LOAD / UNLOAD (plugins) | ✅ | ❌ dotnet only |
| Windows GUI | ✅ | ❌ dotnet only |

### Cross-Platform Gaps

| Gap | Affected | Notes |
|-----|----------|-------|
| CAPTURE-COND deferred semantics | jvm | `.` assigns immediately; deferred infra not built |
| ANY charset range `"A-Z"` | jvm | `-` treated as literal (standard SNOBOL4) |

---

## Benchmarks — SCRIP vs Competitors

### vs PCRE2 JIT — Pattern Matching

**Date**: 2026-03-10 · Platform: Linux x86-64, PCRE2 10.42, gcc -O2

**Test 1 — `(a|b)*abb` on positive inputs (5M iterations)**

| Engine | ns/match | vs PCRE2 |
|--------|:--------:|:--------:|
| SCRIP Round 1 (hand-optimized) | **5.49 ns** | **10×** |
| SCRIP Round 2 (pipeline + arena + Proebsting) | **33 ns** | **2.3×** |
| PCRE2 JIT | 55–78 ns | baseline |

**Test 2 — Pathological: `(a+)+b` on all-`a` strings**

PCRE2 explores exponentially many backtrack paths. SCRIP detects failure structurally.

| Length | SCRIP | PCRE2 JIT | Tiny faster |
|--------|:------------:|:---------:|:-----------:|
| 10–28 chars | 0.7–3.3 ns | 21–23 ns | **7–33×** |

**Where PCRE2 wins**: long literal search (Boyer-Moore). SCRIP scans char-by-char — `hello` in a 1000-char string: tiny 462 ns, PCRE2 93 ns. **Addable optimization, not architectural.**

### vs Bison LALR(1) — Context-Free Parsing

**Date**: 2026-03-10 · Platform: Linux x86-64, Bison 3.8.2, gcc -O2, 2M iterations

| Test | SCRIP | Bison | Faster by |
|------|:------------:|:-----:|:---------:|
| `{a^n b^n}` recognition | **11.54 ns** | 158.45 ns | **14×** |
| Dyck language (balanced parens) | **7.50 ns** | 113.89 ns | **15×** |

**Bison ceiling: Type 2. SCRIP has no ceiling.**

### The Full Picture

| Competitor | Tier | Tiny Round 1 | Tiny Round 2 (pipeline) | Competitor ceiling |
|------------|------|:------------:|:-----------------------:|-------------------|
| PCRE2 JIT | Regular (Type 3) | **10×** faster | **2.3×** faster | Type 3 only |
| Bison LALR(1) | Context-Free (Type 2) | **14–15×** faster | **1.6–1.7×** faster | Type 2 only |
| *(none)* | Context-Sensitive (Type 1) | — | SCRIP only | — |
| *(none)* | Turing (Type 0) | — | SCRIP only | — |

### Optimization Milestones (SCRIP)

| Milestone | Result | Commit |
|-----------|--------|--------|
| Arena allocator | 1,776 ns → 40 ns on `(a|b)*abb` | `13248d9` |
| Proebsting pass (copy propagation) | +28% on RE patterns (42 ns → 33 ns) | `83721c0` |
| Production runtime (arena in runtime.c) | 33.96 ns vs PCRE2 78.60 ns = **2.3×** | — |

---

## Benchmarks — snobol4dotnet

**Platform**: Linux / .NET 10 / Release · **Date**: 2026-03-07

| Benchmark | Phase 9 | Phase 10 | Best |
|-----------|--------:|---------:|-----:|
| Roman_1776 | 5.0 ms | 6.2 ms | — |
| FuncCallOverhead_3000 | 8.2 ms | **5.0 ms** | **-39%** |
| StringConcat_500 | 3.0 ms | **0.4 ms** | **-87%** |
| VarAccess_2000 | 81.6 ms | **64.8 ms** | **-21%** |
| MixedWorkload_200 | 158.0 ms | **125.4 ms** | **-21%** |

**Roslyn → MSIL headline**: Roman numerals 96 ms → 7 ms (**13.7×**). Pattern scan 40 ms → 4 ms (**10.3×**).

**vs CSNOBOL4**: ~165× slower per statement. Gap is in the interpreter loop — target for future optimization phases.

---

## Benchmarks — snobol4jvm

**Platform**: Linux / OpenJDK 21 / Leiningen 2.12.0 · **Date**: 2026-03-09

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║     SNOBOL4 ENGINE BENCHMARK GRID  (ms / run — lower = faster)               ║
╠═══════════════════╦══════════╦══════════╦══════════╦══════════╦══════════╦══════════╣
║ Program           ║ SPITBOL  ║ CSNOBOL4 ║ Interp   ║ Transpil ║ Stack VM ║ JVM code ║
╠═══════════════════╬══════════╬══════════╬══════════╬══════════╬══════════╬══════════╣
║ arith-10k         ║   15.83  ║   27.25  ║  112.14  ║   88.03  ║  107.02  ║   85.55  ║
║ strcat-500        ║   15.09  ║   26.16  ║    9.70  ║    7.99  ║   26.02  ║    6.93  ║
║ pat-span          ║   15.47  ║   26.29  ║   28.05  ║   25.89  ║   52.06  ║   25.22  ║
║ fact45            ║   16.59  ║   24.73  ║     N/A* ║    1.11  ║  167.46  ║    0.89  ║
╚═══════════════════╩══════════╩══════════╩══════════╩══════════╩══════════╩══════════╝
```

SPITBOL/CSNOBOL4 times include ~15 ms process-spawn overhead — subtract for fair comparison.

**Highlights**: strcat-500: Clojure interpreter (9.7 ms) beats CSNOBOL4 (26 ms net ~11 ms). fact45: JVM codegen (0.89 ms) is **14–19× faster than SPITBOL** (net ~1.6 ms).

### JVM Backend Comparison

| Backend | Speedup vs interpreter | Notes |
|---------|:----------------------:|-------|
| EDN cache (Stage 23A) | **22×** | Memoized compile |
| Transpiler (Stage 23B) | 3.5–6× | IR → Clojure `loop/case` |
| Stack VM (Stage 23C) | 2.5–5.7× | Flat bytecode, 7 opcodes |
| JVM bytecode (Stage 23D) | **7.6×** | ASM `.class`, DynamicClassLoader |
| Cold-start cumulative (EDN + JVM) | **~190×** | |

Bottleneck: `EVAL!` in arithmetic loops. Sprint 23E (inline EVAL!) targets this.

---

## How to Update This File

- **dotnet**: `dotnet test ... -c Release`, record Failed count + commit hash
- **jvm**: `lein test`, record tests/assertions/failures + commit hash
- **tiny**: `pytest test/`, record sprint oracles passing + any new baselines
- **benchmarks**: run the bench harness, paste updated grid with date stamp
- Always record both raw and net columns for oracle comparisons
