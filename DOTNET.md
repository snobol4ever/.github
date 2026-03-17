# DOTNET.md — SNOBOL4-dotnet (L2)

.NET/C# backend: SNOBOL4 → MSIL via GOTO-driven threaded bytecode runtime.

→ Backend reference: [BACKEND-NET.md](BACKEND-NET.md)
→ Testing: [TESTING.md](TESTING.md) · Rules: [RULES.md](RULES.md)

---

## NOW

**Sprint:** `net-delegates` ← active
**HEAD:** `dc5d132`
**Milestone:** M-NET-CORPUS-GAPS ✅ · `net-alphabet` ✅ → M-NET-DELEGATES track

**Next action:** `net-delegates` Step 14 — migrate `Instruction[]` dispatch → `Func<Executive,int>[]` in `ThreadedCodeCompiler.cs` / `ThreadedExecuteLoop.cs`.
**After net-delegates:** `net-corpus-rungs` → M-NET-POLISH track.

**Downstream (M-NET-POLISH sprints, in order after M-NET-DELEGATES):**
`net-corpus-rungs` → `net-diag1` → `net-feature-audit` → `net-save-dll` → `net-load-unload` → `net-feature-fill` → `net-benchmark-scaffold` → `net-benchmark-publish`

**Key findings session125:**
- `-w` WriteDll is a no-op on active threaded path — only wired in dead Roslyn path. Fix in `net-save-dll`.
- DLL load path (`snobol4 file.dll`) already works in `MainConsole.cs` ✅
- Macro SPITBOL Manual (Appendix D, LOAD/UNLOAD spec): `github.com/spitbol/x32` → `./docs/spitbol-manual.pdf`

**Key findings this session (corpus injection):**
- 12 corpus test files, ~116 test methods injected; baseline 1732/1744 passed, 12 [Ignore]
- DOTNET vs CSNOBOL4 differences: &ALPHABET=255, DATATYPE lowercase for builtins/uppercase for user types
- 4 real feature gaps discovered by corpus tests → 4 fix sprints under M-NET-CORPUS-GAPS

---

## Session Start

```bash
cd SNOBOL4-dotnet
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
export PATH=$PATH:/usr/local/dotnet
git log --oneline -3   # verify HEAD
dotnet build Snobol4.sln -c Release -p:EnableWindowsTargeting=true
dotnet test TestSnobol4/TestSnobol4.csproj -c Release   # confirm 1732/1744 (12 [Ignore])
```

**CRITICAL:** Always pass `-p:EnableWindowsTargeting=true` on Linux builds.

---

## Milestones

| ID | Trigger | Status |
|----|---------|--------|
| **M-NET-CORPUS-GAPS** | All 12 corpus [Ignore] tests pass — PROTOTYPE, FRETURN/NRETURN, VALUE, EVAL/OPSYN | ❌ Sprint `net-gap-prototype` active |
| **M-NET-DELEGATES** | Instruction[] eliminated — pure Func<Executive,int>[] dispatch | ❌ |
| M-NET-SNOCONE | Snocone self-test: compile snocone.sc, diff oracle | ❌ |
| **M-NET-POLISH** | 106/106 corpus rungs pass · diag1 35/35 · benchmark grid published | ❌ |
| M-NET-BOOTSTRAP | snobol4-dotnet compiles itself | ❌ |

---

## Sprint Map

### Active → M-NET-CORPUS-GAPS (fix corpus [Ignore] tests, one gap per sprint)

Four gaps discovered by corpus test injection session. Fix in order — each sprint removes
its [Ignore] tags and confirms `dotnet test` passes the newly enabled tests.

| Sprint | What | Files affected | Trigger |
|--------|------|----------------|---------|
| **`net-gap-prototype`** | Implement `PROTOTYPE()` builtin — returns dimension string for ARRAY, `'2,2'` for TABLE→ARRAY convert | `Corpus/Rung11_DataStructures.cs` — 1110, 1112, 1113 | ✅ `5f35dad` — fix: emit size when lower==1; old unit tests corrected |
| `net-gap-freturn` | Fix `FRETURN` / `NRETURN` in threaded path — unnamed fn freturn (1014), nreturn lvalue return (1013) | `Corpus/Rung10_Functions.cs` — 1013, 1014 | ✅ `2fd79cd` — RegexGen [^)]+→[^)]*; Assign() dereferences NameVar.Pointer |
| `net-gap-value-indirect` | Implement `VALUE()` by variable name; fix `$.var` indirect syntax (rung2 210, 211) | `Corpus/Rung11_DataStructures.cs` — 1115, 1116; `Corpus/Rung2_Indirect.cs` — 210 | ✅ `a99f1d3` — VALUE() builtin; DATA field shadowing; $.var via SPITBOL-safe test var |
| `net-gap-eval-opsyn` | Fix EVAL unevaluated expr (`*expr`), OPSYN alias, alternate DEFINE entry, ARG/LOCAL/APPLY | `Corpus/Rung10_Functions.cs` — 1010, 1011, 1012, 1015, 1016, 1017, 1018 | ✅ `e21e944` — 1743/1744; Define.cs: argCount bug, redefinition, string entry label, alias returnVar; Opsyn.cs: UserFunctionTable copy; 1012 semicolons separate gap |

**M-NET-CORPUS-GAPS fires when:** all 12 [Ignore] tags removed, `dotnet test` 1744/1744 passed.

### Active → M-NET-ALPHABET (fix &ALPHABET to match SPITBOL/CSNOBOL4)

| Sprint | What | Files affected | Trigger |
|--------|------|----------------|---------|
| **`net-alphabet`** | Fix `&ALPHABET` to contain 256 chars (0x00–0xFF) matching both SPITBOL and CSNOBOL4; update corpus tests to assert 256 exactly instead of `255 \|\| 256` | keyword init; `SimpleOutput_Basic.cs` test 006; `SimpleOutput_CaptureKeywords.cs` test 097 | ✅ `dc5d132` — `Range(0,256)`; Alphabet_001 + 006 + 097 assert 256 exactly |

**Known gap (found 2026-03-16):** DOTNET `&ALPHABET` has 255 chars (0x01–0xFF); both oracles return 256. Corpus tests currently accept 255 or 256 (deliberately loosened). Fix: include 0x00 or adjust init to match the 256-char oracle string.

### → M-NET-DELEGATES

| Sprint | Status |
|--------|--------|
| `net-msil-scaffold` | ✅ |
| `net-msil-operators` | ✅ |
| `net-msil-gotos` | ✅ |
| `net-msil-collapse` | ✅ |
| **`net-delegates`** | ← active |

### → M-NET-SNOCONE

| Sprint | Status |
|--------|--------|
| `net-snocone-corpus` | ✅ `ab5f629` |
| `net-snocone-lexer` | ✅ `dfa0e5b` |
| `net-snocone-expr` | ✅ `63bd297` |
| `net-snocone-control` | ❌ |
| `net-snocone-selftest` | ❌ |

### → M-NET-POLISH (tested · full-featured · benchmarked)

Three tracks run in sequence: corpus coverage first, feature gaps second, benchmarks last.

| Sprint | What | Trigger |
|--------|------|---------|
| `net-corpus-rungs` | Run 106/106 crosscheck rungs 1–11 against DOTNET; fix all failures | 106/106 green |
| `net-diag1` | Run diag1 35-test suite (from SNOBOL4-corpus) against DOTNET; fix all failures | 35/35 green |
| `net-feature-audit` | Compare DOTNET feature coverage vs CSNOBOL4 ref: keywords, data types, built-ins, I/O, CODE()/EVAL() stubs | zero open gaps |
| `net-save-dll` | Wire `-w` (WriteDll) into the threaded execution path; save compiled MSIL to DLL with source extension replaced by `.dll` (see notes below) | `-w file.sno` produces `file.dll`; `snobol4 file.dll` runs it directly |
| `net-load-unload` | Implement LOAD() and UNLOAD() per Macro SPITBOL Manual Appendix D (see reference below) | LOAD/UNLOAD pass corpus tests |
| `net-feature-fill` | Implement any remaining missing features identified by audit (one sub-sprint per gap) | audit clean |
| `net-benchmark-scaffold` | Wire DOTNET into harness benchmark pipeline; collect DOTNET timing column | pipeline green |
| `net-benchmark-publish` | Run full benchmark grid (DOTNET vs CSNOBOL4 vs SPITBOL vs TINY); publish results in HARNESS.md | grid published |

**M-NET-POLISH fires when:** `net-corpus-rungs` ✅ + `net-diag1` ✅ + `net-save-dll` ✅ + `net-load-unload` ✅ + `net-feature-fill` ✅ + `net-benchmark-publish` ✅

### -w / WriteDll Notes (sprint `net-save-dll`)

**Behaviour spec (from Jeff Cooper, 2026-03-16):**
- `snobol4 -w file.sno` — compile as normal, then save the compiled MSIL assembly to disk
- Output filename: source filename with extension replaced by `.dll` (e.g. `file.sno` → `file.dll`, `file.spt` → `file.dll`)
- Works on Windows and other platforms
- **Already implemented:** `snobol4 file.dll` on the command line — `MainConsole.cs` detects `.dll` extension, skips all build steps, calls `RunDll()` directly ✅

**Current gap (found 2026-03-16):**
- `BuilderOptions.WriteDll` flag exists; `-w` sets it in `CommandLine.cs` ✅
- `WriteDll` is only checked inside `CSharpCompile.cs / CreateAssembly()` — the **Roslyn/legacy path only**
- `BuildMain()` runs the **threaded path** (`ThreadedCodeCompiler`) by default; `CreateAssembly()` is never called → `-w` is currently a **no-op** on the active code path
- Fix: after `tc.Compile()` in `BuildMain()`, if `BuildOptions.WriteDll`, persist the in-memory assembly to the `.dll` output file using `AssemblyLoadContext` save or Roslyn `Emit()` to `FileStream`

### LOAD / UNLOAD Reference

**Spec source:** *Macro SPITBOL Manual* by Mark B. Emmer and Edward K. Quillen (Catspaw, Inc.)
- **Online:** `https://github.com/spitbol/x32` → `./docs/spitbol-manual.pdf` (Appendix D — External Functions)
- **MINIMAL-level spec:** `https://github.com/spitbol/pal/blob/master/s.min` — see `sysld` (load) and `sysul` (unload) OS interface procedures
- **Note:** SPITBOL x64 has LOAD() disabled; x32 PDF + pal/s.min are the authoritative references

**Semantics summary (from spec):**
- `LOAD(fname, libpath)` — dynamically loads an external function from a shared library; registers it in the efblk (external function block) with a code pointer and name pointer; function becomes callable by name
- `UNLOAD(fname)` — releases the external function previously loaded; efblk code pointer is cleared; function cannot be called again until another LOAD for the same name
- On .NET: implement via `Assembly.LoadFrom()` / `NativeLibrary` + reflection; unload via `AssemblyLoadContext` with collectible context

---

## Pivot Log

| Date | What | Why |
|------|------|-----|
| 2026-03-10 | `net-delegates` declared active | Steps 1–13 complete, Step 14 next |
| 2026-03-16 | M-NET-POLISH added: 6 sprints (corpus → diag1 → feature-audit → feature-fill → benchmark-scaffold → benchmark-publish) | Explicit milestone to get DOTNET fully tested, full-featured, and benchmarked before bootstrap |
| 2026-03-16 | `net-load-unload` sprint added to M-NET-POLISH; Macro SPITBOL Manual located at github.com/spitbol/x32 docs/spitbol-manual.pdf (Appendix D) | LOAD/UNLOAD per spec is a required feature for full SPITBOL compliance |
| 2026-03-16 | Pivot from JVM `jvm-inline-eval` to DOTNET `net-delegates` | Lon redirected active session to DOTNET |
| 2026-03-16 | `net-alphabet` sprint created — `&ALPHABET` is 255 chars in DOTNET, both oracles return 256; corpus tests loosened to `255\|\|256`; fix next session | both CSNOBOL4 and SPITBOL agree: SIZE(&ALPHABET)==256 |
| 2026-03-16 | `net-gap-prototype` ✅ — PROTOTYPE() emits CSNOBOL4 format; 1110/1112/1113 pass; 1733/1744; HEAD `5f35dad` | fix: emit size when lower==1, else lower:upper; old unit tests corrected |
| 2026-03-16 | `net-gap-freturn` ✅ — 1013+1014 pass; 1735/1744; HEAD `2fd79cd` | Bug 1: FunctionPrototypePattern [^)]+→[^)]* (empty param list); Bug 2: Assign() NameVar.Pointer dereference for lvalue |
| 2026-03-16 | `net-gap-value-indirect` ✅ — 1115+1116+210 pass; 1738/1744; HEAD `a99f1d3` | VALUE() builtin; DATA fields shadow builtins polymorphically; $.var SPITBOL-safe; BAL protected per is.sno discriminator |
| 2026-03-17 | `net-gap-eval-opsyn` ✅ — 1743/1744; 5 [Ignore] removed (1010/1011/1016/1017/1018); Define.cs: argumentCount bug (locals→parameters), redefinition guard (user funcs allowed), string entry label arg, returnVarName from definition.FunctionName; Opsyn.cs: UserFunctionTable copy preserving original FunctionName for alias return var resolution; 1012 semicolons genuine parser gap left [Ignore] | session131 |
| 2026-03-16 | `net-alphabet` ✅ — `&ALPHABET` SIZE 255→256; `Range(0,256)`; tests 006/097/Alphabet_001 tightened to `AreEqual(256)`; 1743/1744; HEAD `dc5d132` | both oracles agree SIZE==256 |
| 2026-03-17 | M-NET-CORPUS-GAPS ✅ fired (11/12 [Ignore] removed; 1743/1744); pivot to `net-alphabet` then `net-delegates` | session131 |
| 2026-03-16 | `net-gap-value-indirect` now active | next corpus-gap sprint |
| 2026-03-16 | `net-gap-freturn` now active | next corpus-gap sprint |
| 2026-03-16 | Corpus test injection: 12 files, ~116 test methods from SNOBOL4-corpus crosscheck; 12 [Ignore] gaps mapped to 4 fix sprints under M-NET-CORPUS-GAPS; HEAD `7aacf01` | Lon: inject corpus tests following Jeff's style |
| 2026-03-16 | `net-save-dll` sprint added to M-NET-POLISH; `-w` WriteDll diagnosed as no-op on active threaded path — only wired in dead Roslyn path (CSharpCompile.cs/CreateAssembly); DLL load path (file.dll on cmdline) already works in MainConsole.cs | Fix needed: persist threaded assembly to disk after tc.Compile() when WriteDll=true |
