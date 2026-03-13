# DOTNET.md — SNOBOL4-dotnet

**Repo:** https://github.com/SNOBOL4-plus/SNOBOL4-dotnet  
**What it is:** Full SNOBOL4/SPITBOL in C# targeting .NET/MSIL. GOTO-driven threaded bytecode runtime, MSIL delegate JIT compiler, plugin system (LOAD/UNLOAD), Windows GUI.

---

## Current State

**Active sprint:** Step 14 — eliminate `Instruction[]`, store `Func<Executive, int>[]` directly  
**Milestone target:** MNET  
**HEAD:** `63bd297`  
**Test baseline:** 1,607 passing / 0 failing  
**Test runner:** `dotnet test TestSnobol4/TestSnobol4.csproj -c Release`

**Next action:** Implement Step 14 in `ThreadedCodeCompiler.cs` — replace `Instruction[]`
storage with direct `Func<Executive, int>[]`. No intermediate instruction objects.

---

## Session Start Checklist

```bash
cd SNOBOL4-dotnet
export PATH=$PATH:/usr/local/dotnet
git log --oneline --since="1 hour ago"   # fallback: -5
dotnet build Snobol4.sln -c Release -p:EnableWindowsTargeting=true
dotnet test TestSnobol4/TestSnobol4.csproj -c Release
```

**CRITICAL:** Always pass `-p:EnableWindowsTargeting=true` on Linux builds.

---

## Milestones

| ID | Trigger | Status |
|----|---------|--------|
| **MNET** | Step 14 complete — `Instruction[]` eliminated, pure delegate dispatch | ❌ Active |
| **MNET2** | Snocone self-test: compile `snocone.sc`, diff oracle (Step 9) | ❌ Future |

---

## Sprint Map

### Sprints toward MNET (active track — MSIL emitter)

| Step | What | Status |
|------|------|--------|
| Steps 1–5 | Scaffolding, expression emission, var reads/writes, operator coverage | ✅ |
| Steps 6–10 | Init/Finalize inline, delegate signature, fall-through/direct/conditional gotos | ✅ |
| Steps 11–13 | Indirect gotos, collapse execute loop, TRACE hooks | ✅ |
| **Step 14** | **Eliminate `Instruction[]` — store `Func<Executive, int>[]` directly** | **← active** |

### Sprints toward MNET2 (Snocone)

| Step | What | Status |
|------|------|--------|
| Step 0 | Corpus reference files | ✅ `ab5f629` |
| Step 1 | Lexer | ✅ `dfa0e5b` |
| Step 2 | Expression parser — shunting-yard, 35 tests | ✅ `63bd297` |
| Steps 3–8 | Control structures | ❌ |
| Step 9 | Self-test → **MNET2 triggers** | ❌ |

### Completed foundation sprints

| Milestone | Tests | Date |
|-----------|------:|------|
| Roslyn baseline | 1,271 | 2026-03-05 |
| Threaded execution (15.9× speedup on Roman) | 1,386 | 2026-03-05 |
| MSIL emitter Steps 1–13 | 1,484 | 2026-03-07 |
| LOAD/UNLOAD plugin system | 1,466 | 2026-03-07 |
| Snocone Step 2 | **1,607** | 2026-03-10 `63bd297` |

---

## Open Issues

| # | Issue | Severity |
|---|-------|----------|
| 1 | Pattern.Bal — hangs under threaded execution | Medium |
| 2 | Deferred expressions `pos(*A)` — TEST_Pos_009 | Low |
| 3 | TestGoto _DIRECT — CODE() dynamic compilation | Medium |
| 4 | Function.InputOutput — Linux (hardcoded Windows paths) | Low |

---

## Solution Layout

```
Snobol4.Common/
  Builder/
    Builder.cs                  compile pipeline
    BuilderEmitMsil.cs          MSIL delegate JIT (Steps 1–14)
    ThreadedCodeCompiler.cs     emits Instruction[] → Step 14 eliminates this
    Token.cs                    Token.Type enum + Token class
  Runtime/Execution/
    ThreadedExecuteLoop.cs      main dispatch loop
    StatementControl.cs         RunExpressionThread()
    Executive.cs                partial class root
TestSnobol4/
  MsilEmitterTests.cs
  ThreadedCompilerTests.cs
```

---

## Performance

**Roslyn → MSIL:** Roman numerals 96 ms → 7 ms (13.7×). Pattern scan 40 ms → 4 ms (10.3×).

| Benchmark | Phase 9 | Phase 10 |
|-----------|--------:|---------:|
| FuncCallOverhead_3000 | 8.2 ms | **5.0 ms** (-39%) |
| StringConcat_500 | 3.0 ms | **0.4 ms** (-87%) |
| VarAccess_2000 | 81.6 ms | **64.8 ms** (-21%) |
