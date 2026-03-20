# DOTNET.md — snobol4dotnet (L2)

Jeff Cooper's complete SNOBOL4/SPITBOL runtime in C#. Compiler pipeline, threaded
execution, MSIL delegate JIT, pattern engine, plugin system. Polish → beta release.

→ Backend reference: [BACKEND-NET.md](BACKEND-NET.md)
→ Testing: [TESTING.md](TESTING.md) · Rules: [RULES.md](RULES.md)
→ Full session history: [SESSIONS_ARCHIVE.md](SESSIONS_ARCHIVE.md)

---

## NOW

**Sprint:** `net-polish` — confirm 106/106 → M-NET-CORPUS-RUNGS → fix semicolon → M-NET-POLISH
**HEAD:** `8a713cb` D-160
**Invariant:** `dotnet test` → 1873/1876 (3 C-ABI skipped) before any work
**Milestone:** M-NET-CORPUS-RUNGS ❌ → fix shipped D-160; pending dotnet test confirmation

**⚠ CRITICAL NEXT ACTION — Session D-161:**

```bash
cd snobol4dotnet
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
export PATH=$PATH:/usr/local/dotnet
git log --oneline -3   # verify HEAD = 8a713cb D-160
dotnet build Snobol4.sln -c Release -p:EnableWindowsTargeting=true
dotnet test TestSnobol4/TestSnobol4.csproj -c Release -p:EnableWindowsTargeting=true
# Expect: 1876/1876 (3 C-ABI skipped) → fire M-NET-CORPUS-RUNGS ✅

# Step 2: fix semicolon statement separator (one remaining [Ignore] in corpus)
# Root cause: Lexer state 2 (LABEL) fires for every sub-line from SplitLineByDelimiter.
# Sub-lines beyond the first (LineCountSubLine > 1) cannot have labels — but 'b = bb'
# starts with 'b' which matches the label pattern, so 'b' gets registered as a label
# and '= bb' fails to parse as a statement body.
# Fix: in Lexer.FindLexeme case 2, skip label extraction when sourceLine.LineCountSubLine > 1
# File: Snobol4.Common/Builder/Lexer.cs
# After fix: remove [Ignore] from TEST_Corpus_1012_func_locals → dotnet test → diag1 35/35
# → publish benchmark grid → M-NET-POLISH ✅
```

**CRITICAL:** Always pass `-p:EnableWindowsTargeting=true` on Linux builds.

---

## Last Session Summary

**Session D-160 — PosPattern/RPosPattern Clone() swap fixed:**
- Root cause of `cross` 105/106: `PosPattern.Clone()` returned `RPosPattern`; `RPosPattern.Clone()` returned `PosPattern` — copy-paste swap
- Fix: 4 lines across 2 files; `8a713cb` pushed; dotnet test pending SDK in next session
- Also diagnosed semicolon separator [Ignore]: Lexer labels sub-lines; fix is LineCountSubLine > 1 guard

**Session D-159 — M-NET-PERF fires:**
- BenchmarkSuite2 re-run; ≥1 alloc win confirmed; libspitbol_xn.so rebuilt; 1873/1876 ✅

---

## Active Milestones (next 5)

| ID | Status | Notes |
|----|--------|-------|
| M-NET-PERF | ✅ | Hotfixes A–D confirmed; baseline published |
| M-NET-CORPUS-RUNGS | ❌ | Fix shipped D-160; confirm with dotnet test |
| M-NET-POLISH | ❌ | 106/106 + diag1 35/35 + benchmark grid |
| M-NET-SNOCONE | ❌ | Snocone self-test |
| M-NET-BOOTSTRAP | ❌ | snobol4-dotnet compiles itself |

Full milestone history → [PLAN.md](PLAN.md)

---

## Performance Baseline (session159, post-hotfix A–D)

| Benchmark | Mean | Alloc/run |
|-----------|-----:|----------:|
| ArithLoop_1000 | 39.8ms | 1662 KB |
| VarAccess_2000 | 103.2ms | 6279 KB |
| Fibonacci_18 | 286.6ms | 11855 KB |
| MixedWorkload_200 | 223.2ms | 13928 KB |
| FuncCallOverhead_3000 | 40.6ms | 837 KB |

Full numbers → `perf/post_hotfix_session159.md`.

---

## SPITBOL Oracle Rule

When CSNOBOL4 and SPITBOL MINIMAL diverge: **SPITBOL MINIMAL wins.**
Key semantics: DATATYPE builtins lowercase; user DATA types `ToLowerInvariant`;
`&UCASE`/`&LCASE` = exactly 26 ASCII letters; `@N` is **0-based** cursor position.
