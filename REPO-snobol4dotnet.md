# REPO-snobol4dotnet.md

Jeff Cooper's complete SNOBOL4/SPITBOL runtime in C#. Compiler pipeline, threaded
execution, MSIL delegate JIT, pattern engine, plugin system. Polish → beta release.

**Platform target:** Windows and Linux. macOS is expected to work (same .NET SDK)
but is untested — no macOS CI or hardware available. All platform-specific code
(native lib paths, export macros, DLL vs .so selection) must support Windows and
Linux. Never hardcode one platform only.

→ Backend reference: [INTERP-NET.md](INTERP-NET.md)
→ Testing: [TESTING.md](TESTING.md) · Rules: [RULES.md](RULES.md)
→ Full session history: [SESSIONS_ARCHIVE.md](SESSIONS_ARCHIVE.md)

---

## NOW

**Sprint:** `D-184` — fix @N VarSlotArray bug → M-NET-P35-FIX → 80/80 crosscheck
**HEAD:** `0d3d9e4` D-183
**Invariant:** `dotnet test` → 1953/1956 (3 skipped, 0 failed) before any work
**Milestone:** D-183 ✅ — 51 corpus ref tests added, RunWithInput helper, 3 [Ignore] with bug refs

**⚠ CRITICAL NEXT ACTION — Session D-184:**

```bash
cd /home/claude/snobol4dotnet
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git pull --rebase
git log --oneline -3   # verify HEAD = 0d3d9e4 D-183
dotnet build TestSnobol4/TestSnobol4.csproj -c Release -p:EnableWindowsTargeting=true
dotnet test TestSnobol4/TestSnobol4.csproj -c Release -p:EnableWindowsTargeting=true --no-build
# Expect 1953 passed, 0 failed, 3 skipped — then fix @N bug (M-NET-P35-FIX)

# @N BUG — root cause identified D-183:
# AtSign.Scan writes IdentifierTable["NH"] = cursor correctly.
# BUT: IdentifierTable write calls SyncVarSlot() which only updates VarSlotArray
# if the symbol already has a slot. NH is first created at runtime by @NH —
# it has no slot at compile time. So SyncVarSlot silently does nothing.
# PushVar reads VarSlotArray[idx] — stale zero.
#
# Fix location: ExecutionCache.cs SyncVarSlot() — when symbol has no slot,
# allocate one via ExpandVarSlotArray() and add to SymbolToSlotIndex.
# OR: AtSign.Scan — after writing IdentifierTable, call ExpandVarSlotArray()
# to pick up the new symbol.
#
# Gate: TEST_Corpus_W07_capt_cur PASS (already passes — simpler case)
#       TEST_Corpus_strings_cross PASS (unanchored loop case — the hard one)
#       Remove [Ignore] from TEST_Corpus_strings_cross
#       crosscheck: 80/80

# Crosscheck command:
# DOTNET_REPO=/home/claude/snobol4dotnet CORPUS=/home/claude/corpus/crosscheck \
# DOTNET_ROOT=/usr/local/dotnet10 \
# bash /home/claude/harness/adapters/dotnet/run_crosscheck_dotnet.sh
# Currently: 79/80 (1 fail: strings/cross — @N bug)
```

**CRITICAL:** `apt-get install -y dotnet-sdk-10.0`. Always `-p:EnableWindowsTargeting=true`.

---

## Sprint: D-184 (next)

Fix @N VarSlotArray bug in ExecutionCache.SyncVarSlot / AtSign.Scan → M-NET-P35-FIX → 80/80 crosscheck.
Then: ASGNIC string coercion (099_keyword_rw) → M-NET-PAT-PRIMITIVES.
Then: NRETURN → EVAL/CODE → M-NET-EVAL-COMPLETE → expr_eval passes.
Then: M-NET-CORPUS-TESTS (all 3 [Ignore] removed, library tests wired).

## Completed: D-183 — corpus ref tests + RunWithInput

```
0d3d9e4  D-183: corpus ref tests — 51 new tests from crosscheck .ref oracle files
```
- SetupTests.RunWithInput() — 18-line helper using Executive.ReadLineDelegate
- CorpusRef_Hello (4), CorpusRef_Keywords (5), CorpusRef_Patterns (2),
  CorpusRef_Misc (5), CorpusRef_RungW (26), CorpusRef_InputTests (9)
- 3 [Ignore] with documented bug refs:
  - TEST_Corpus_strings_cross → M-NET-P35-FIX (@N VarSlotArray)
  - TEST_Corpus_099_keyword_rw → ASGNIC string coercion error 208
  - TEST_Corpus_control_expr_eval → M-NET-EVAL-COMPLETE (NRETURN+*func+EVAL)
- Library tests (-include) excluded entirely — need corpus path config
- **Result: 1953 passed, 0 failed, 3 skipped, 0 warnings**

## Completed: D-182 — Jeff Cooper improvements

```
521ee5f  D-182: Jeff Cooper's improvements — cross-platform, MSIL debug, NOCONV fix
```
- Cross-platform EXPORT macros in all C fixture libs (Windows + Linux)
- spitbol_xn.c: snobol4_rt_register() bridge (replaces RTLD_GLOBAL, works on Windows)
- BuilderEmitMsil.cs: DetectGotoForms() + EmitBodyIntoIL() extracted as shared helpers
- BuilderEmitMsilDebug.cs: new DumpMsilToFile() diagnostic for ILSpy/ildasm
- SetupTests.cs / LoadSpecTests.cs: Windows/Linux platform branching for native lib paths
- TestSnobol4.csproj: Windows pre-build target for native C libs
- build_native.ps1: new Windows PowerShell build script
- Snobol4.sln: VS 2026 with new projects
- Load.cs: fix NOCONV GCHandle.Pinned → GCHandle.Normal for ArrayVar/TableVar
- ExtNoconvTests.cs: [DoNotParallelize] + remove [Ignore] from 2 tests now passing
- **Result: 1905/1905, 0 warnings**

## Completed: net-spitbol-switches (D-162 / D-163)



---

## Last Session Summary

**Session D-182 — Jeff Cooper improvements merged (Lon + Claude Sonnet 4.6):**
- Reviewed Jeff's 2026-04-07 ZIP against main; all changes correct and Linux-safe
- Merged: cross-platform EXPORT macros, snobol4_rt_register bridge, BuilderEmitMsilDebug,
  Windows/Linux path branching in tests, build_native.ps1, VS 2026 solution
- Fixed pre-existing NOCONV bug (GCHandle.Pinned → Normal for ArrayVar/TableVar)
- Fixed parallel test interference ([DoNotParallelize] on ExtNoconvTests)
- Removed all [Ignore] — 1905/1905 passing, 0 warnings
- Platform policy documented: Windows + Linux target; macOS expected but untested

**Session D-164 — @N bug diagnosed (cross test, 79/80 crosscheck):**
- Ran crosscheck: 79/80 — only failure is `strings/cross` (`@N` cursor capture = 0 when should be > 0)
- Diagnosed: `X ? @N ANY('B')` — `AtSign.Scan` writes `IdentifierTable["N"]=cursor` correctly,
  but something in Phase 5 (`CheckGotoFailure` or post-match cleanup) overwrites it. Not yet fixed.

---

## Active Milestones

Full ladder: `MILESTONE-NET-SNOBOL4.md` — organized around 5-phase executor model.

| ID | Priority | Status | Notes |
|----|----------|--------|-------|
| M-NET-PERF | — | ✅ | Hotfixes A–D confirmed; baseline published |
| M-NET-SPITBOL-SWITCHES | — | ✅ | 1911/1913 D-163 |
| M-NET-P35-FIX | 1 | ❌ | Fix @N Phase 3/5 capture boundary → 80/80 crosscheck · unblocks TEST_Corpus_strings_cross |
| M-NET-PAT-CAPTURES | 2 | ❌ | @/./$var capture audit vs stmt_exec.c |
| M-NET-PAT-PRIMITIVES | 3 | ❌ | 16 pattern primitives vs SPITBOL oracle → 1913/1913 · unblocks TEST_Corpus_099_keyword_rw (ASGNIC string coercion) |
| M-NET-NRETURN | 4 | ❌ | NRETURN lvalue (follow DYN-42 fix) |
| M-NET-EVAL-COMPLETE | 5 | ❌ | EVAL/CODE edge cases + rung10/1016 · unblocks TEST_Corpus_control_expr_eval |
| M-NET-POLISH | 6 | ❌ | 106/106 + diag1 35/35 + benchmark grid |
| M-NET-CORPUS-TESTS | 7 | ⚠️ | All corpus ref tests passing — 0 [Ignore], 0 skipped · library/-include tests wired once corpus path is configurable |
| M-NET-SNOCONE | 8 | ❌ | Snocone self-test (code generator not yet written) |
| M-NET-BOOTSTRAP | 9 | ❌ | Self-hosting — snobol4dotnet compiles itself |

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

SPITBOL MINIMAL is authoritative.
Key semantics: DATATYPE builtins lowercase; user DATA types `ToLowerInvariant`;
`&UCASE`/`&LCASE` = exactly 26 ASCII letters; `@N` is **0-based** cursor position.
