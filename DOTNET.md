# DOTNET.md — snobol4dotnet (L2)

Jeff Cooper's complete SNOBOL4/SPITBOL runtime in C#. Compiler pipeline, threaded
execution, MSIL delegate JIT, pattern engine, plugin system. Polish → beta release.

→ Backend reference: [BACKEND-NET.md](BACKEND-NET.md)
→ Testing: [TESTING.md](TESTING.md) · Rules: [RULES.md](RULES.md)
→ Full session history: [SESSIONS_ARCHIVE.md](SESSIONS_ARCHIVE.md)

---

## NOW

**Sprint:** `net-polish` — 106/106 corpus rungs + diag1 35/35 + benchmark grid → M-NET-POLISH
**HEAD:** `dbdcba7` D-163
**Invariant:** `dotnet test` → 1911/1913 (2 skipped) before any work
**Milestone:** M-NET-SPITBOL-SWITCHES ✅ fired D-163

**⚠ CRITICAL NEXT ACTION — Session D-164:**

```bash
cd /home/claude/snobol4dotnet
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
export PATH=/usr/local/dotnet10:$PATH   # .NET 10 required
git log --oneline -3   # verify HEAD = 8feb139 D-162
dotnet test TestSnobol4/TestSnobol4.csproj -c Release -p:EnableWindowsTargeting=true
# Expect: 1911/1913 invariant holds
# Sprint: M-NET-POLISH — run corpus crosscheck, diag1, benchmark grid
#   CORPUS=/home/claude/snobol4corpus/crosscheck
#   bash /home/claude/snobol4harness/adapters/dotnet/run_crosscheck_dotnet.sh
```

**CRITICAL:** Always pass `-p:EnableWindowsTargeting=true` on Linux builds. .NET 10 SDK at `/usr/local/dotnet10`.

---

## Sprint: net-polish (D-164 — next)

Next sprint: 106/106 corpus crosscheck via harness, diag1 35/35, benchmark grid → M-NET-POLISH.
See TESTING.md for corpus ladder and HARNESS.md for crosscheck scripts.

## Completed: net-spitbol-switches (D-162)



---

## Last Session Summary

**Session D-163 — M-NET-SPITBOL-SWITCHES confirmed + warnings eliminated:**
- Installed .NET 10 SDK; `dotnet build` → 0 errors; `dotnet test` → 1911/1913 — 26 SpitbolSwitchTests PASS
- M-NET-SPITBOL-SWITCHES ✅ fired; PLAN.md + DOTNET.md updated
- Fixed all compiler warnings: CS0114 `override` on `ExternalVar.Equals(Var?)`; CS8602 null-guards in `Load.cs` and `ExtXnblkTests.cs`; 1911/1913 invariant confirmed clean

**Session D-162 — SPITBOL switches authored:**
- 11 new BuilderOptions properties; CommandLine.cs rewrite with k/m suffix parser
- `ApplyStartupOptions()` wires -e/-m; 26 unit tests in SpitbolSwitchTests.cs

---

## Active Milestones (next 5)

| ID | Status | Notes |
|----|--------|-------|
| M-NET-PERF | ✅ | Hotfixes A–D confirmed; baseline published |
| M-NET-SPITBOL-SWITCHES | ✅ | 1911/1913 D-163 |
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
