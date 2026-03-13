# DOTNET.md — SNOBOL4-dotnet

**Repo:** https://github.com/SNOBOL4-plus/SNOBOL4-dotnet  
**What it is:** Full SNOBOL4/SPITBOL in C# targeting .NET/MSIL. GOTO-driven threaded bytecode runtime, MSIL delegate JIT compiler, plugin system (LOAD/UNLOAD), Windows GUI.

---

## Current State

**Active sprint:** `net-delegates`  
**Milestone target:** M-NET-DELEGATES  
**HEAD:** `63bd297`  
**Test baseline:** 1,607 passing / 0 failing

**Next action:** Implement `net-delegates` in `ThreadedCodeCompiler.cs` — replace
`Instruction[]` storage with direct `Func<Executive, int>[]`. No intermediate instruction objects.

## Pivot Log

| Date | What changed | Why |
|------|-------------|-----|
| 2026-03-10 | `net-delegates` declared active | Steps 1–13 complete, Step 14 next |

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
| **M-NET-DELEGATES** | `Instruction[]` eliminated — pure `Func<Executive,int>[]` dispatch | ❌ Active |
| **M-NET-SNOCONE** | Snocone self-test: compile `snocone.sc`, diff oracle | ❌ Future |

---

## Sprint Map

### Active: toward M-NET-DELEGATES

| Sprint | What | Status |
|--------|------|--------|
| `net-msil-scaffold` | Scaffolding, expression emission, var reads/writes | ✅ |
| `net-msil-operators` | Operator coverage, init/finalize inline | ✅ |
| `net-msil-gotos` | Fall-through, direct, conditional, indirect gotos | ✅ |
| `net-msil-collapse` | Collapse execute loop, TRACE hooks | ✅ |
| **`net-delegates`** | **Eliminate `Instruction[]` → `Func<Executive,int>[]` directly** | **← active** |

### Toward M-NET-SNOCONE (Snocone)

| Sprint | What | Status |
|--------|------|--------|
| `net-snocone-corpus` | Corpus reference files | ✅ `ab5f629` |
| `net-snocone-lexer` | Lexer | ✅ `dfa0e5b` |
| `net-snocone-expr` | Expression parser — shunting-yard, 35 tests | ✅ `63bd297` |
| `net-snocone-control` | Control structures | ❌ |
| `net-snocone-selftest` | Compile `snocone.sc`, diff oracle → **M-NET-SNOCONE** | ❌ |

### Completed foundation

| Sprint | What | Tests |
|--------|------|------:|
| `net-roslyn-baseline` | Roslyn baseline | 1,271 |
| `net-threaded-exec` | Threaded execution (15.9× speedup on Roman) | 1,386 |
| `net-msil-steps-1-13` | MSIL emitter Steps 1–13 | 1,484 |
| `net-load-unload` | LOAD/UNLOAD plugin system | 1,466 |
| `net-snocone-expr` | Current baseline | **1,607** |

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
    BuilderEmitMsil.cs          MSIL delegate JIT
    ThreadedCodeCompiler.cs     emits Instruction[] → net-delegates eliminates this
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
