# DOTNET.md — snobol4dotnet (L2)

Jeff Cooper's complete SNOBOL4/SPITBOL runtime in C#. Compiler pipeline, threaded
execution, MSIL delegate JIT, pattern engine, plugin system. Polish → beta release.

→ Backend reference: [BACKEND-NET.md](BACKEND-NET.md)
→ Testing: [TESTING.md](TESTING.md) · Rules: [RULES.md](RULES.md)
→ Full session history: [SESSIONS_ARCHIVE.md](SESSIONS_ARCHIVE.md)

---

## NOW

**Sprint:** `net-spitbol-switches` — implement all SPITBOL CLI switches → M-NET-SPITBOL-SWITCHES
**HEAD:** `0d4b2ee` D-161 (switches code authored D-162, commit pending dotnet build confirmation)
**Invariant:** `dotnet test` → 1874/1876 (2 skipped) before any work
**Milestone:** M-NET-SPITBOL-SWITCHES ❌ → code complete D-162; confirm with dotnet test

**⚠ CRITICAL NEXT ACTION — Session D-163:**

```bash
cd snobol4dotnet
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
export PATH=$PATH:/usr/local/dotnet
git log --oneline -3   # verify HEAD = 0d4b2ee D-161
dotnet build Snobol4.sln -c Release -p:EnableWindowsTargeting=true
dotnet test TestSnobol4/TestSnobol4.csproj -c Release -p:EnableWindowsTargeting=true
# Expect: 1874/1876 + 26 new SpitbolSwitchTests → 1900/1902 → fire M-NET-SPITBOL-SWITCHES ✅
# Then commit:
#   git add Snobol4.Common/Builder/BuilderOptions.cs
#   git add Snobol4.Common/Builder/CommandLine.cs
#   git add Snobol4.Common/Builder/Builder.cs
#   git add TestSnobol4/TestCommandLine/TestSpitbolSwitches/SpitbolSwitchTests.cs
#   git commit -m "D-162: SPITBOL switches — -d -e -g -i -m -p -s -t -y -z -N=file; k/m parser; 26 tests"
#   git push
```

**CRITICAL:** Always pass `-p:EnableWindowsTargeting=true` on Linux builds.

---

## Sprint: net-spitbol-switches (D-162)

Implement all SPITBOL command-line switches per manual Chapter 13.

### Files changed

| File | What |
|------|------|
| `Snobol4.Common/Builder/BuilderOptions.cs` | 11 new properties: `ErrorsToStdout`, `LinesPerPage` (60), `PageWidth` (120), `PrinterListing`, `FormFeedListing`, `HeapMaxBytes` (64m), `HeapIncrementBytes` (128k), `MaxObjectBytes` (4m), `StackSizeBytes` (32k), `WriteSpx`, `ChannelFiles` |
| `Snobol4.Common/Builder/CommandLine.cs` | Full `ArgumentSwitch` rewrite; `TryParseNumericArg` (k/m suffix); `ExtractStringArg`; channel `-N=file` association; updated `DisplayManual()` with all switches |
| `Snobol4.Common/Builder/Builder.cs` | `ApplyStartupOptions(Executive)` — wires `-e` (redirect Console.Error→Out) and `-m` (seeds `exec.AmpMaxLength`); called from `BuildMain`, `BuildMainCompileOnly`, `RunDll` |
| `TestSnobol4/TestCommandLine/TestSpitbolSwitches/SpitbolSwitchTests.cs` | 26 unit tests covering every new switch and edge cases |

### Switch inventory (post D-162)

| Switch | Status | Notes |
|--------|--------|-------|
| `-a -b -c -cs -f -F -h -k -l -n -o -r -u -v -w -x -?` | ✅ pre-existing | |
| `-e` | ✅ D-162 | Console.Error→Console.Out at startup |
| `-gN` | ✅ D-162 | LinesPerPage, default 60 |
| `-tN` | ✅ D-162 | PageWidth, default 120 |
| `-p` | ✅ D-162 | PrinterListing + ShowListing |
| `-z` | ✅ D-162 | FormFeedListing + ShowListing |
| `-dN` | ✅ D-162 | HeapMaxBytes (64m default); recorded, .NET GC manages |
| `-iN` | ✅ D-162 | HeapIncrementBytes (128k default); recorded |
| `-mN` | ✅ D-162 | MaxObjectBytes → seeds `&MAXLNGTH` at startup |
| `-sN` | ✅ D-162 | StackSizeBytes (32k default); recorded |
| `-y` | ✅ D-162 | WriteSpx flag (save file stub; full impl future) |
| `-N=file` | ✅ D-162 | ChannelFiles dictionary; `:` separator also accepted |

### Sprint steps remaining (D-163)
1. `dotnet build` → clean
2. `dotnet test` → 1900/1902 (26 new pass)
3. Commit + push → M-NET-SPITBOL-SWITCHES ✅
4. Update PLAN.md dashboard

---

## Last Session Summary

**Session D-162 — SPITBOL switches implemented:**
- Read SPITBOL manual Chapter 13 (command line options, pages 161–165)
- Identified 11 missing switches vs existing implementation
- `BuilderOptions.cs`: 11 new properties with SPITBOL defaults
- `CommandLine.cs`: full rewrite — k/m numeric parser, all switches, channel `-N=file`, updated manual display
- `Builder.cs`: `ApplyStartupOptions()` wires `-e` and `-m` at Executive creation
- `SpitbolSwitchTests.cs`: 26 unit tests, all switch/edge cases
- `PLAN.md`: `M-NET-SPITBOL-SWITCHES` milestone added
- `DOTNET.md`: sprint documented

**Session D-161 — CallFuncIndirect + semicolon fix:**
- CallFuncIndirect opcode + FunctionIndirect(); perf/post_d161.md benchmark grid; 1874/1876
- Semicolon separator fix — Lexer case 2 skips label on sub-lines; 1012_func_locals [Ignore] removed
- README.md cleaned up (removed fabricated term)

---

## Active Milestones (next 5)

| ID | Status | Notes |
|----|--------|-------|
| M-NET-PERF | ✅ | Hotfixes A–D confirmed; baseline published |
| M-NET-CORPUS-RUNGS | ✅ | D-161 confirmed 1874/1876 |
| M-NET-SPITBOL-SWITCHES | ❌ | Code complete D-162; confirm dotnet test D-163 |
| M-NET-POLISH | ❌ | 106/106 + diag1 35/35 + benchmark grid |
| M-NET-SNOCONE | ❌ | Snocone self-test |

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
