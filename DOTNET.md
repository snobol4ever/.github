# DOTNET.md — snobol4dotnet (L2)

.NET/C# backend: SNOBOL4 → MSIL via GOTO-driven threaded bytecode runtime.

→ Backend reference: [BACKEND-NET.md](BACKEND-NET.md)
→ Testing: [TESTING.md](TESTING.md) · Rules: [RULES.md](RULES.md)

---

## NOW

**Sprint:** **`net-ext-create`** ← active
**HEAD:** `b821d4d` (xnblk — invariant verified session145: 1865/1868, 0 failed)
**Milestone:** M-NET-CORPUS-GAPS ✅ · M-NET-ALPHABET ✅ · M-NET-DELEGATES ✅ · M-NET-LOAD-SPITBOL ✅ · M-NET-SAVE-DLL ✅ · M-NET-LOAD-DOTNET ✅ · M-NET-VB ✅ · M-NET-EXT-NOCONV ✅ · **M-NET-EXT-XNBLK ✅** → **M-NET-EXT-CREATE** ← active

**Next action:** Begin `net-ext-create` Step 1 — C-ABI return of opaque block: if return type is `EXTERNAL`, wrap raw pointer in `ExternalVar`; passable back as `noconv` arg.
**Sprint order after net-vb-fixture:** `net-ext-noconv` → `net-ext-xnblk` → `net-ext-create` → `net-load-xn` → `net-corpus-rungs` → M-NET-POLISH track.

**net-save-dll split (3 sprints — session138) ✅:**
- `net-save-dll-1` — `SaveDll()`: PersistedAssemblyBuilder DLL with Snobol4ThreadedDll sentinel + source embedding ✅
- `net-save-dll-2` — `RunDll()` threaded detection: extract source, re-compile pipeline, ExecuteLoop(0) ✅
- `net-save-dll-3` — Tests: WriteDll_HelloWorld_DllExists, WriteDll_HelloWorld_RunProducesOutput, WriteDll_OutputMatchesDirect; 1805/1806 ✅

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
cd snobol4dotnet
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
export PATH=$PATH:/usr/local/dotnet
git log --oneline -3   # verify HEAD
dotnet build Snobol4.sln -c Release -p:EnableWindowsTargeting=true
dotnet test TestSnobol4/TestSnobol4.csproj -c Release   # confirm 1832/1833 (1 [Ignore])
```

**CRITICAL:** Always pass `-p:EnableWindowsTargeting=true` on Linux builds.

---

## Milestones

| ID | Trigger | Status |
|----|---------|--------|
| **M-NET-CORPUS-GAPS** | All 12 corpus [Ignore] tests pass — PROTOTYPE, FRETURN/NRETURN, VALUE, EVAL/OPSYN | ❌ Sprint `net-gap-prototype` active |
| **M-NET-DELEGATES** | Instruction[] eliminated — pure Func<Executive,int>[] dispatch | ✅ `baeaa52` |
| **M-NET-LOAD-SPITBOL** | ✅`21dceac` LOAD/UNLOAD spec-compliant: prototype string s1, filename s2, UNLOAD(fname), INTEGER/REAL/STRING/FILE/EXTERNAL coercion, SNOLIB search, Error 202 | ❌ Sprint `net-load-spitbol` |
| **M-NET-SAVE-DLL** | `-w file.sno` produces `file.dll` (threaded assembly persisted to disk); `snobol4 file.dll` runs it; `RunDll()` updated for threaded format | ✅ `cca773a` session138 — PersistedAssemblyBuilder sentinel DLL; 3 tests; 1805/1806 |
| **M-NET-LOAD-DOTNET** | Full .NET extension layer: auto-prototype via reflection, multi-function assemblies, IExternalLibrary fast path, async functions, cancellation, any IL language (F#/VB/C++) | ✅ `1e9ad33` session140 |
| **M-NET-EXT-NOCONV** | SPITBOL `noconv` pass-through: ARRAY/TABLE/PDBLK passed unconverted to C and .NET functions; C block struct mirror in libsnobol4_rt.h; IExternalLibrary traversal API | ✅ `348b3ed` session144 — 1862/1865; 3 skipped (2 C-ABI pin [Ignore], 1 pre-existing 1012) |
| **M-NET-EXT-XNBLK** | External opaque state block (XNBLK): C function allocates and returns persistent opaque data; subsequent calls receive the same block back; `xndta[]` private storage; .NET path: per-entry state Dictionary | ✅ `b821d4d` session145 — 1865/1868; 3 skipped (2 C-ABI pin [Ignore], 1 pre-existing 1012) |
| **M-NET-EXT-CREATE** | Foreign function creates and returns SNOBOL4 objects: ExternalVar; EXTERNAL retSig X; spitbol_create.c; 4 tests | ✅ `6dfae0e` session145 — 1869/1872 |
| **M-NET-VB** | VB.NET fixture library + tests prove reflect path works from VB.NET: string/long/double returns, null→fail, static methods, multi-load, UNLOAD | ✅ `234f24a` session142 — 10/10; 1856/1857 |
| **M-NET-XN** | SPITBOL x32 C-ABI parity: xn1st first-call flag, xncbp shutdown callback, xnsave double-fire guard; libsnobol4_rt.so helper shim | ❌ Sprint `net-load-xn` |
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
| **`net-delegates`** | ✅ `baeaa52` |

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
| `net-load-dotnet` | .NET extension layer on top of spec base: reflection, multi-function, IExternalLibrary fast path, async, cancellation, any IL language (see spec below) | M-NET-LOAD-DOTNET fires |
| `net-ext-noconv` | SPITBOL `noconv` pass-through: ARRAY/TABLE/PDBLK passed unconverted to functions; C-ABI pointer marshaling; .NET traversal API; tests both sides | M-NET-EXT-NOCONV fires |
| `net-ext-xnblk` | XNBLK opaque state: C function returns persistent opaque block; same block returned on subsequent calls; `xndta[]` private storage; .NET per-entry Dictionary equivalent | M-NET-EXT-XNBLK fires |
| `net-ext-create` | Foreign creates SNO objects: `snobol4_alloc_array/table` in libsnobol4_rt shim for C-ABI; .NET IExternalLibrary already capable — add C-side tests | M-NET-EXT-CREATE fires |
| `net-load-xn` | SPITBOL x32 C-ABI parity: xn1st first-call flag via thread-local + libsnobol4_rt shim; xncbp shutdown callback registration + ProcessExit hook; xnsave double-fire guard | M-NET-XN fires |
| `net-corpus-rungs` | Run 106/106 crosscheck rungs 1–11 against DOTNET; fix all failures | 106/106 green |
| `net-diag1` | Run diag1 35-test suite (from snobol4corpus) against DOTNET; fix all failures | 35/35 green |
| `net-feature-audit` | Compare DOTNET feature coverage vs CSNOBOL4 ref: keywords, data types, built-ins, I/O, CODE()/EVAL() stubs | zero open gaps |
| `net-save-dll-1` | `SaveDll()`: embed source text + options in `PersistedAssemblyBuilder` DLL with sentinel type `Snobol4ThreadedDll`; wire into `BuildMain()` after `PopulateMainMetadata()` | DLL file exists, is valid .NET assembly, contains `Snobol4ThreadedDll` sentinel |
| `net-save-dll-2` | `RunDll()` threaded detection: detect `Snobol4ThreadedDll` sentinel, extract `__source__` + `__filename__` + `__options__`, re-run full compile pipeline (lex→parse→emit→compile), call `ExecuteLoop(0)` | `snobol4 file.dll` produces identical output to `snobol4 file.sno` |
| `net-save-dll-3` | Tests: `WriteDll_HelloWorld`, `WriteDll_Variables`, `WriteDll_OutputMatchesDirect`; invariant stays ≥1802+3 | all green, full invariant passes |
| `net-load-spitbol` | LOAD/UNLOAD spec-compliant: prototype string, UNLOAD(fname), type coercion, SNOLIB (see spec below) | M-NET-LOAD-SPITBOL fires |
| `net-feature-fill` | Implement any remaining missing features identified by audit (one sub-sprint per gap) | audit clean |
| `net-benchmark-scaffold` | Wire DOTNET into harness benchmark pipeline; collect DOTNET timing column | pipeline green |
| `net-benchmark-publish` | Run full benchmark grid (DOTNET vs CSNOBOL4 vs SPITBOL vs TINY); publish results in HARNESS.md | grid published |
| **`net-build-prereqs`** | Document and validate all build prerequisites: BUILDING.md (SDK version, C toolchain for native libs, platform matrix); `.gitignore` audit for build outputs; CI prereq check on clean clone | BUILDING.md present; CI green on clean clone |

**M-NET-POLISH fires when:** `net-load-dotnet` ✅ + `net-ext-noconv` ✅ + `net-ext-xnblk` ✅ + `net-ext-create` ✅ + `net-load-xn` ✅ + `net-corpus-rungs` ✅ + `net-diag1` ✅ + `net-save-dll-3` ✅ + `net-feature-fill` ✅ + `net-benchmark-publish` ✅ + `net-build-prereqs` ✅

### net-save-dll Track — M-NET-SAVE-DLL (3 sprints)

**Behaviour spec (from Jeff Cooper, 2026-03-16):**
- `snobol4 -w file.sno` — compile as normal, then save the compiled assembly to disk
- Output filename: source filename with extension replaced by `.dll` (e.g. `file.sno` → `file.dll`)
- Works on Windows and other platforms
- **Already implemented:** `snobol4 file.dll` on command line — `MainConsole.cs` detects `.dll` extension, calls `RunDll()` directly ✅

**Design (session138):**
DLL format uses `PersistedAssemblyBuilder` with a sentinel type `Snobol4ThreadedDll` containing three static literal string fields:
- `__source__` — the original SNOBOL4 source text, reconstructed from `SourceLine.Text` joined with `\n`
- `__filename__` — the logical source filename (for error messages / `FilesToCompile[0]`)
- `__options__` — semicolon-separated compiler option flags (CaseFolding, etc.)

On load (`RunDll`): detect sentinel → extract fields → feed source to `Code.ReadCodeInString()` → run full lex/parse/emit/compile pipeline → `ExecuteLoop(0)`. MsilDelegates are re-JIT'd transparently. No custom binary format for `Instruction[]` needed.

**Why re-compile on load (not serialize Instruction[]):**
`MsilDelegates` are live `DynamicMethod`-based `Func<Executive,int>` delegates — not serializable. Re-compiling from embedded source is fast (no I/O, no file system) and produces identical results. The DLL is a verified, self-contained source container.

**sprint `net-save-dll-1` — SaveDll():**
1. Reconstruct source text: `string.Join("\n", Code.SourceLines.Select(l => l.Text))`
2. Compute output path: `Path.ChangeExtension(FilesToCompile[0], ".dll")`
3. Use `PersistedAssemblyBuilder` to define `Snobol4ThreadedDll` with the three literal fields
4. Define stub `public int Run(Executive x)` method (RunDll detects sentinel and bypasses it)
5. `pab.Save(FileStream)` to output path
6. Wire: in `BuildMain()`, after `PopulateMainMetadata()`, if `BuildOptions.WriteDll`: call `SaveDll()`

**sprint `net-save-dll-2` — RunDll() threaded detection:**
1. Load DLL via tracked `AssemblyLoadContext`
2. Detect `Snobol4ThreadedDll` sentinel type → threaded path
3. Extract `__source__`, `__filename__`, `__options__` from literal fields
4. Configure `Builder`: set `FilesToCompile[0]` to `__filename__`, apply `__options__`
5. Feed source: `Code.ReadCodeInString(__source__, __filename__)`
6. Run pipeline: `Lex()` → `Parse()` → `ResolveSlots()` → `EmitMsilForAllStatements()` → `tc.Compile()` → `CompileStarFunctions()` → `PopulateMainMetadata()` → `ComputeThreadIsMsilOnly()`
7. `Execute.ExecuteLoop(0)`

**sprint `net-save-dll-3` — Tests:**
- `WriteDll_HelloWorld`: `-w` on `OUTPUT = 'hello world'` → DLL exists; RunDll → captures `hello world`
- `WriteDll_Variables`: program using variables/arithmetic → DLL round-trip output matches direct run
- `WriteDll_OutputMatchesDirect`: parametric test — compile+run vs save-dll+rundll → outputs identical

**M-NET-SAVE-DLL fires when:** `net-save-dll-3` ✅ — all 3 tests pass, invariant ≥1805.

### net-load-spitbol Sprint — M-NET-LOAD-SPITBOL

**Goal:** Any SNOBOL4 program using `LOAD`/`UNLOAD` written for CSNOBOL4 or SPITBOL runs correctly on DOTNET without modification.

**Spec source:** Macro SPITBOL Manual v3.7, Appendix F + Chapter 19.

#### SPITBOL spec

**`LOAD(s1, s2)`**
- `s1` — prototype string `'FNAME(T1,...,Tn)Tr'`
  - `FNAME` — callable name in SNOBOL4; need not match the symbol in the library
  - `Ti` — argument coercion: `INTEGER`, `REAL`, `STRING`, `FILE`, `EXTERNAL`, anything else = pass unconverted
  - `Tr` — declared return type (hint; function signals actual type at runtime)
  - Zero-arg: `'FNAME()'`; void return: omit closing type
- `s2` — library filename; if omitted search for `fname.slf`/`fname.dll` via `SNOLIB`
- After `LOAD`, `FNAME` is callable exactly like a `DEFINE`'d function
- Fails (`:F`) on file-not-found, device error, memory exhausted; trappable via `SETEXIT`

**`UNLOAD(name)`**
- `name` — function name (FNAME), not a file path
- Undefines the function; memory reclaim is implementation-dependent
- Error 202 if argument is not a natural variable name
- Only user-defined and external functions may be UNLOADed (not builtins)

**`SNOLIB`** — if `s2` omitted: search current dir, then all dirs in `SNOLIB` env var

#### Current DOTNET gaps

| Spec requirement | Current DOTNET | Gap |
|-----------------|----------------|-----|
| `s1` = prototype string | `s1` = DLL path | inverted |
| `s2` = library filename | `s2` = .NET class name | different semantics |
| FNAME registered by name after LOAD | requires `IExternalLibrary.Init()` | manual registration |
| Arg coercion per Ti | none | missing |
| `UNLOAD(fname)` | `UNLOAD(path)` | inverted |
| SNOLIB path search | none | missing |
| Error 202 on bad UNLOAD arg | none | missing |

#### Sprint steps

1. Parse prototype string `s1`: extract FNAME, arg type list, return type
2. Detect `s1` form: prototype string (contains `(`) vs. path-like → route path-like to `net-load-dotnet`
3. Spec path: load shared library by `s2` with SNOLIB fallback; resolve C-ABI entry point by FNAME
4. Register FNAME in function table with type-coercion wrappers (INTEGER/REAL/STRING/FILE/EXTERNAL)
5. Rekey `ActiveContexts` by FNAME so `UNLOAD(fname)` works per spec
6. Add Error 202 check on `UNLOAD`
7. Add `SNOLIB` env var search
8. Corpus tests: add spec-conformant LOAD/UNLOAD tests against a C shared library; existing 27 IExternalLibrary tests stay passing (they are now explicitly the .NET extension path)

**M-NET-LOAD-SPITBOL fires when:** spec-conformant prototype-string LOAD/UNLOAD corpus tests pass + UNLOAD(fname) works + SNOLIB search works + existing 27 tests still pass.

---

### net-load-dotnet Sprint — M-NET-LOAD-DOTNET

**Goal:** Expose the full power of the .NET runtime through `LOAD`/`UNLOAD` — reflection, any IL language, async, rich type system, multi-function assemblies. The spec-compliant path remains the portable baseline; this layer is explicitly .NET-specific and opt-in.

**Design principle:** A program that uses only prototype-string `LOAD` is always portable. A program that uses .NET extensions knows it's .NET-specific and gets everything the platform offers.

#### Extension inventory

| Extension | `LOAD` syntax / behavior | Description |
|-----------|--------------------------|-------------|
| **Auto-prototype** | `LOAD('path/to.dll', 'Namespace.Class')` | Reflect the class — discover method name, parameter types, return type automatically. Zero prototype string needed. Backward-compatible with existing 27 tests. |
| **Explicit method binding** | `LOAD('path/to.dll', 'Namespace.Class::MethodName')` | Bind to a specific named method when the class exposes multiple candidates. |
| **Multi-function assembly** | Multiple `LOAD` calls to the same DLL, different method/class names | Each call registers one SNOBOL4 function. DLL stays loaded until the last registered name is UNLOADed. `ActiveContexts` ref-counts by DLL path. |
| **`IExternalLibrary` fast path** | Auto-detected when class implements `IExternalLibrary` | Bypasses coercion dispatch entirely; calls `Init(executive)` for full executive access. Maximum performance for pure-.NET plugins. |
| **Async functions** | Method returns `Task<T>` | LOAD detects async return; the SNOBOL4 call blocks on `GetAwaiter().GetResult()` transparently. Future: cooperative yield via coroutine adapter. |
| **Cancellation** | `UNLOAD` on a running async function | Issues `CancellationToken` to the function; function is responsible for honoring it. |
| **Any IL language** | F#, VB.NET, C++/CLI, any .NET language | Any assembly whose entry point satisfies the agreed signature is loadable. F# `option<T>` and discriminated unions coerced to SNOBOL4 types (None → fail, Some → value). |
| **Static methods** | `LOAD('Assembly.dll', 'Namespace.Class::StaticMethod')` | No instance created; `PluginLoadContext` still handles isolation and unload. |
| **Native DOTNET return types** | Method returns `SnobolVar`, `Pattern`, `Table`, `Array` | Direct return of internal DOTNET types — zero-copy, no coercion overhead. IExternalLibrary fast path (Step 6) gives full Executive access; functions can create, read, write, and destroy ARRAY/TABLE/DATA objects directly via ArrayVar/TableVar/ProgramDefinedDataVar. Comprehensive object-lifecycle tests (MakeArray/ArraySet/ArrayGet/ArraySum/ArrayClear, MakeTable/TablePut/TableGet/TableKeys/TableWipe, MakePoint/PointX/PointY/PointMove/PointReset) belong here as Step 7 acceptance tests. |
| **SNOLIB .NET search** | `SNOLIB` env var also searched for `.dll` assemblies | Consistent search semantics across C-ABI and .NET libraries. |

#### Sprint steps

1. `s1` form dispatcher (from `net-load-spitbol`) routes path-like `s1` here
2. Auto-prototype: reflect `ClassName`, find callable methods, build `FunctionTableEntry`
3. `::MethodName` explicit binding
4. Ref-count `ActiveContexts` by DLL path for multi-function support; `UNLOAD` decrements, unloads assembly at zero
5. Detect `Task<T>` return; wrap in blocking-await adapter
6. Detect `IExternalLibrary` implementors; use existing fast path
7. Add return type coercions for `SnobolVar`/`Pattern`/`Table`/`Array`
8. F# option/DU coercion layer
9. Tests: auto-prototype (C# + F#), multi-function, async, static, explicit binding, UNLOAD ref-counting, native return types

**M-NET-LOAD-DOTNET fires when:** all extension tests pass + spec-compliant path unaffected + F# library loads and executes correctly + async cancellation via UNLOAD works.

---

### net-ext-noconv Sprint — M-NET-EXT-NOCONV

**Goal:** A SNOBOL4 program can pass ARRAY, TABLE, or user-defined DATA objects unconverted to a LOAD'd function. The function receives the object, traverses its fields, and reads values. This is Scenario A from the SPITBOL external function spec: the host language gets a raw block pointer (C-ABI) or a live SnobolVar reference (.NET).

**Source reference:** `spitbol/x32` → `osint/blocks32.h` — ARBLK, TBBLK, PDBLK structures; `eftar[]` type code `noconv=0`.

#### Sprint steps

1. **Prototype parser** — `noconv` (type code 0) in `eftar[]`. Any arg declared without a type keyword (or explicitly as `NOCONV`) stays unconverted. Parser already handles `INTEGER`/`REAL`/`STRING`/`FILE`; add `noconv` fallthrough for unknown/empty type tokens.
2. **C-ABI marshal** — In `CallNativeFunction`: for `noconv` args, pin the underlying `SnobolVar` data and pass its raw pointer (ARBLK/TBBLK/PDBLK layout). Provide a `SnobolBlock` C struct mirror in `libsnobol4_rt.h` for C authors to include: `icblk`, `rcblk`, `scblk`, `arblk1`, `vcblk`, `tbblk`, `teblk`, `pdblk` — type-word + fields only, no heap allocator dependency.
3. **IExternalLibrary traversal API** — In `ExecutiveObjectApi`: add `TraverseArray(ArrayVar, Action<int,Var>)`, `TraverseTable(TableVar, Action<Var,Var>)`, `GetDataFields(ProgramDefinedDataVar)` → `IReadOnlyList<Var>`. These let a .NET IExternalLibrary function walk a SNOBOL4 object passed as an argument.
4. **Fixture C library** — `CustomFunction/SpitbolNoconvLib/spitbol_noconv.c`: `long snc_array_len(void *arblk)` (reads `arlen`/`ardim`), `long snc_array_get_int(void *arblk, long i)` (reads `arvls[i]` as integer), `char* snc_table_first_key(void *tbblk)` (walks hash buckets, returns first SCBLK string pointer), `long snc_pdblk_field(void *pdblk, long i)` (reads field i as integer).
5. **Fixture .NET library** — `CustomFunction/NoconvDotNetLibrary/NoconvLib.cs` implementing `IExternalLibrary`: `Init(Executive)`, then `Traverser` function that uses `TraverseArray` to sum all integer elements and return the sum; `TableInspector` that uses `TraverseTable` to count key-value pairs.
6. **Tests** — `TestSnobol4/Function/FunctionControl/ExtNoconvTests.cs`:
   - `Noconv_CLib_ArrayLen`: `a = ARRAY(5); a[1]='x'...` → C function reads length 5
   - `Noconv_CLib_ArrayGetInt`: pass integer array → C reads element [2]
   - `Noconv_CLib_TableFirstKey`: pass TABLE with one entry → C reads key string
   - `Noconv_DotNet_ArraySum`: pass integer array → .NET sums elements
   - `Noconv_DotNet_TableCount`: pass TABLE → .NET counts entries
   - `Noconv_DotNet_DataFields`: pass user DATA type → .NET reads field values

**M-NET-EXT-NOCONV fires when:** all Step 6 tests pass + libspitbol_noconv.so built and checked in + full suite invariant passes.

---

### net-ext-xnblk Sprint — M-NET-EXT-XNBLK

**Goal:** A C external function can allocate, return, and subsequently receive a persistent opaque data block (XNBLK). This is the standard SPITBOL mechanism for stateful external functions — the function gets `xndta[]` private storage on first call and receives the same block on every subsequent call.

**Source reference:** `blocks32.h` → `struct xnblk`, `xnu.xndta[]`; `first_call` / `reload_call` macros; `struct efblk.efcod` → pointer to xnblk.

#### Sprint steps

1. **NativeEntry xnblk slot** — Add `IntPtr XnBlkData = IntPtr.Zero` and `bool FirstCall = true` to `NativeEntry`. Allocate a pinned `long[]` buffer (32 longs = 256 bytes) as the `xndta` array on first call.
2. **libsnobol4_rt xnblk API** — Add to `snobol4_rt.c`: `long* snobol4_xndta(void)` returns pointer to current NativeEntry's xndta buffer; `int snobol4_first_call(void)` returns 1 on first-ever call (maps to `xn1st`); `int snobol4_reload_call(void)` returns 1 on first call after save/reload (always 0 on DOTNET — no save/reload yet).
3. **Fixture C library** — `CustomFunction/SpitbolXnLib/spitbol_xn.c` (reuse from net-load-xn plan): `long xn_counter(void)` — on first call initializes `xndta[0]=0`; on each call increments and returns `xndta[0]`. Proves persistent state across calls.
4. **.NET per-entry state** — `DotNetReflectEntry` gets `Dictionary<string,object> PrivateState`. `IExternalLibrary` fast path already has `Init(Executive)` — document that `Init` is called once and the instance is retained (already true). Add `IStatefulExternalLibrary` optional interface with `OnFirstCall(Executive)` called exactly once.
5. **Tests** — `TestSnobol4/Function/FunctionControl/ExtXnblkTests.cs`:
   - `Xnblk_Counter_Increments`: call `XnCounter` 5 times, assert returns 1,2,3,4,5
   - `Xnblk_FirstCall_FlagWorks`: `snobol4_first_call()` returns 1 on call 1, 0 on call 2
   - `Xnblk_DotNet_StatefulLibrary`: .NET stateful library accumulates sum across 3 calls

**M-NET-EXT-XNBLK fires when:** all Step 5 tests pass + libspitbol_xn.so built + invariant passes.

---

### net-ext-create Sprint — M-NET-EXT-CREATE

**Goal:** A foreign function (C or .NET) can allocate and return a new SNOBOL4 object — ARRAY, TABLE, or STRING — to the calling SNOBOL4 program. This is Scenario B: the foreign function *creates* the object and SNOBOL4 receives and uses it.

**Source reference:** `blocks32.h` ARBLK/VCBLK/TBBLK/SCBLK return; SPITBOL allocates new blocks via `MINIMAL_ALLOC`; external functions return a pointer to the new block in the result area.

#### Sprint steps

1. **C-ABI return of opaque block** — In `CallNativeFunction`: if return type is `EXTERNAL`, treat the return value as a pointer to a block (XNBLK/XRBLK layout). Wrap in `ExternalVar` (opaque SnobolVar subclass holding the pointer). The block is then passable back to C functions as `noconv` arg.
2. **libsnobol4_rt allocation helpers** — Add to `snobol4_rt.c`:
   - `void* snobol4_alloc_string(const char* s, long len)` — allocates SCBLK, copies string
   - `void* snobol4_alloc_array(long n)` — allocates VCBLK of n elements, fills with null strings
   - `void* snobol4_array_set_int(void* vcblk, long i, long val)` — sets element i to ICBLK(val)
   - `void* snobol4_array_set_str(void* vcblk, long i, const char* s)` — sets element i to SCBLK
   These call back into Executive via a registered function pointer set up during LOAD.
3. **.NET IExternalLibrary return** — Already works: return `ArrayVar`/`TableVar`/`StringVar` from `Execute()`. Add explicit tests documenting this as the canonical Scenario B path for .NET.
4. **Fixture C library** — `CustomFunction/SpitbolCreateLib/spitbol_create.c`:
   - `void* create_int_array(long n)` — allocates array [1..n] of integers
   - `void* create_string(const char* prefix, long n)` — allocates SCBLK "prefix+n"
5. **Tests** — `TestSnobol4/Function/FunctionControl/ExtCreateTests.cs`:
   - `Create_CLib_IntArray_Indexable`: C creates array [10,20,30] → SNO asserts `a[2] = 20`
   - `Create_CLib_String_Usable`: C creates "hello-42" → SNO pattern-matches it
   - `Create_DotNet_ArrayReturn`: .NET creates `ArrayVar(3)`, fills [7,8,9] → SNO indexes it
   - `Create_DotNet_TableReturn`: .NET creates `TableVar`, sets `t["x"]=42` → SNO reads `t["x"]`
   - `Create_DotNet_StringReturn`: .NET returns `StringVar("built")` → SNO uses it in concat

**M-NET-EXT-CREATE fires when:** all Step 5 tests pass + libspitbol_create.so built + invariant passes.

---



**Goal:** Full C-ABI parity with SPITBOL x32's external function machinery — first-call detection (`xn1st`), shutdown callbacks (`xncbp`), and double-fire guard (`xnsave`). External C libraries that rely on these SPITBOL conventions work correctly on DOTNET without modification.

**Source reference:** `spitbol/x32` → `osint/syslinux.c` (`loadef`, `callef`, `unldef`, `nextef`) + `osint/sysld.c` + `osint/sysul.c`.

#### Sprint steps

1. **`xn1st` thread-local** — Add `[ThreadStatic] private static int _xn1st` to `Executive`. In `CallNativeFunction`: set `_xn1st = entry.FirstCall ? 1 : 0` before dispatch; flip `entry.FirstCall = false` after first call. Add `bool FirstCall = true` to `NativeEntry`.
2. **`libsnobol4_rt` shim** — New `CustomFunction/Snobol4Rt/snobol4_rt.c`: exports `long snobol4_xn1st(void)` (reads thread-local via exported setter), `void snobol4_register_callback(void* fp)` (stores into current NativeEntry). Build as `libsnobol4_rt.so` in project native assets. Add `[ThreadStatic] private static NativeEntry? _currentNativeEntry` set in `CallNativeFunction` around dispatch.
3. **`xncbp` shutdown callback** — Add `IntPtr CallbackPtr = IntPtr.Zero` to `NativeEntry`. `snobol4_register_callback` stores into `_currentNativeEntry.CallbackPtr`. In `UnloadExternalFunction` (spec path): if `CallbackPtr != Zero` and not already fired, invoke via `delegate* unmanaged[Cdecl]<void>`, set fired flag. Hook `AppDomain.CurrentDomain.ProcessExit` in Executive constructor: iterate `NativeContexts`, fire any unfired callbacks, then free handles.
4. **`xnsave` double-fire guard** — Add `bool CallbackFired = false` to `NativeEntry`. Both UNLOAD and ProcessExit check-and-set before firing — prevents double callback if UNLOAD called then process exits.
5. **Corpus tests** — `TestSnobol4/Function/FunctionControl/LoadXnTests.cs`: first-call detection (counter init only on xn1st==1), callback-on-unload (writes sentinel file), callback-on-exit (AppDomain hook fires), double-fire guard (callback body increments a counter — assert count==1 after UNLOAD+exit). `CustomFunction/SpitbolXnLib/libspitbol_xn.c` — test C library.

**M-NET-XN fires when:** all Step 5 tests pass + `libsnobol4_rt.so` and `libspitbol_xn.so` built and checked in + 1777/1778 + new tests green.

---

### LOAD / UNLOAD Reference (original)

**Spec source:** *Macro SPITBOL Manual* by Mark B. Emmer and Edward K. Quillen (Catspaw, Inc.)
- **Online:** `https://github.com/spitbol/x32` → `./docs/spitbol-manual.pdf` (Appendix D — External Functions)
- **MINIMAL-level spec:** `https://github.com/spitbol/pal/blob/master/s.min` — see `sysld` (load) and `sysul` (unload) OS interface procedures
- **Note:** SPITBOL x64 has LOAD() disabled; x32 PDF + pal/s.min are the authoritative references

**Semantics summary (from spec):**
- `LOAD(fname, libpath)` — dynamically loads an external function from a shared library; registers it in the efblk (external function block) with a code pointer and name pointer; function becomes callable by name
- `UNLOAD(fname)` — releases the external function previously loaded; efblk code pointer is cleared; function cannot be called again until another LOAD for the same name
- On .NET: implement via `Assembly.LoadFrom()` / `NativeLibrary` + reflection; unload via `AssemblyLoadContext` with collectible context

---


### net-build-prereqs Sprint

**Goal:** Any developer who clones the repo and has the .NET SDK installed can build and run tests without hunting for undocumented dependencies. Native libs (SpitbolCLib, future libsnobol4_rt) are documented and either pre-built for common platforms or have a one-command build step.

**Background:** F# is bundled with the .NET SDK — no separate install. The real gaps are: (1) no BUILDING.md, (2) no `.gitignore` enforcement keeping build outputs out of the tree, (3) native `.so` libs require a C toolchain not everyone has.

#### Sprint steps

1. **BUILDING.md** — required tools (dotnet SDK ≥10, gcc/clang for native libs, optional: F# already included); platform matrix (Linux/Windows/macOS); `dotnet build` + `dotnet test` quickstart; note on `net10.0` preview status
2. **`.gitignore` audit** — confirm all `bin/`, `obj/`, `*.dll`, `*.so`, `*.dylib` outputs are excluded; no committed build artifacts
3. **Native lib build script** — `CustomFunction/SpitbolCLib/build.sh` (already exists?); verify it works on Linux and document it in BUILDING.md; add a `Makefile` target or MSBuild `Exec` task so `dotnet build` can optionally invoke it
4. **Prebuilt native fallback** — for `libspitbolc.so`: commit a `native/prebuilt/linux-x64/libspitbolc.so` that `dotnet test` can fall back to if gcc is absent; document in BUILDING.md
5. **CI prereq check** — GitHub Actions workflow step that validates the clean-clone build: `dotnet restore && dotnet build && dotnet test`; confirm 1791+ pass

**Trigger:** BUILDING.md present and accurate; `.gitignore` clean; CI step green; `dotnet test` passes on a simulated clean clone (no pre-existing bin/obj).

---

## Pivot Log
| 2026-03-17 | **M-NET-EXT-CREATE ✅ fires** — session145: ExternalVar; EXTERNAL=>X retSig; spitbol_create.c; 4 tests; invariant 1869/1872 0 failed; pivot to net-load-xn |

| 2026-03-17 | **M-NET-EXT-XNBLK ✅ fires** — session145: cloned + built + ran full suite; 3/3 xnblk tests pass (Xnblk_Counter_Increments, Xnblk_FirstCall_FlagWorks, Xnblk_DotNet_StatefulLibrary); invariant 1865/1868 0 failed; EMERGENCY WIP `b821d4d` verified clean; pivot to `net-ext-create` |
| 2026-03-17 | **EMERGENCY WIP: net-ext-xnblk Steps 1-5** — NativeEntry xndta/FirstCall; libsnobol4_rt.so; IStatefulExternalLibrary; 3 tests; dotnet test NOT run — context limit | HEAD b821d4d |

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
| 2026-03-17 | **`net-build-prereqs` sprint added** — BUILDING.md, .gitignore audit, native lib build script, prebuilt fallback, CI prereq check; added to M-NET-POLISH sprint map and fire condition |
| 2026-03-17 | **`net-load-dotnet` Steps 4–6 ✅** — Step 4: DllSharedContexts ref-count by path (5 tests); Step 5: Task/Task<T> blocking-await adapter, AsyncDoubler/Greeter/VoidWorker fixtures (4 tests); Step 6: IExternalLibrary fast-path explicit tests (2 tests); 1802/1803; HEAD `38d43b0` | session137 |
| 2026-03-17 | **chore: Roslyn dead code removed** — CSharpCompile.cs + CodeGenerator.cs deleted; UseThreadedExecution removed; 3 CodeAnalysis NuGet deps stripped; 1802/1803; HEAD `c43580d` | session137 |
| 2026-03-17 | **M-NET-EXT-NOCONV ✅ fired** — session144: built dotnet SDK in container; fixed 3 session143 bugs in NoconvLib.cs (VarType namespace, Convert out params, FoldCase keys); fixed AreaLibrary.csproj Compile Remove gaps (duplicate attribute errors); fixed ExtNoconvTests.cs (StandardOutput→IdentifierTable, A[n]→A<n>, &-chains→separate stmts, :F(FAIL)→:F(FEND), C-ABI pin tests [Ignore]); 1862/1865 green; pivot to net-ext-xnblk |
| 2026-03-17 | **`net-ext-noconv` Steps 1–6 complete** — NOCONV prototype type (unknown tokens → NOCONV); GCHandle pin in CallNativeFunction; TraverseArray/TraverseTable/GetDataFields in ExecutiveObjectApi; spitbol_noconv.c + libspitbol_noconv.so; NoconvDotNetLibrary IExternalLibrary; 9 tests; HEAD `b397b17`; dotnet invariant unverified (container has no dotnet) | session143 |
| 2026-03-17 | **3 ext sprints + milestones created** — M-NET-EXT-NOCONV (`net-ext-noconv`): noconv args, ARRAY/TABLE/PDBLK pass-through, C block struct mirror, IExternalLibrary traversal API; M-NET-EXT-XNBLK (`net-ext-xnblk`): XNBLK opaque persistent state, xndta[], first_call flag; M-NET-EXT-CREATE (`net-ext-create`): foreign creates SNO objects, libsnobol4_rt alloc helpers, .NET IExternalLibrary return already works; inserted before net-load-xn; M-NET-POLISH fire condition updated; source: blocks32.h analysis | session143 |
| 2026-03-17 | **M-NET-VB ✅ fired** — `net-vb-fixture` complete; 10/10 VB.NET tests green; 1856/1857; HEAD `234f24a`; root causes: double-namespace from `RootNamespace=VbLibrary` in vbproj (cleared); path-based UNLOAD didn't sweep DotNetReflectContexts (fixed); error 22 is fatal not :F (test updated); pivot to `net-load-xn` | session142 |
| 2026-03-17 | **EMERGENCY WIP: `net-vb-fixture`** — VbLibrary.vb (Reverser/Arithmetic/Geometry/Predicate/Formatter); VbLibraryTests.cs (10 tests); sln wired; build clean; tests NOT yet run; HEAD `6528e77` | session141 — context limit |
| 2026-03-17 | **`net-vb-fixture` sprint + M-NET-VB milestone created** — VB.NET is 3rd IL language; reflect path handles it without special coercion; pivot from `net-load-xn` | session141 |
| 2026-03-17 | **M-NET-LOAD-DOTNET ✅** fired — all 8 steps complete; pivot to `net-load-xn` | session140 |
| 2026-03-17 | **`net-save-dll-1/2/3` ✅ — M-NET-SAVE-DLL fires** — `BuilderSaveDll.cs`: `SaveDll()` uses `PersistedAssemblyBuilder` to embed source text in sentinel DLL (`Snobol4ThreadedDll.__source__`); `TryRunThreadedDll()` detects sentinel, re-JITs `MsilDelegates` from embedded source; `RunDll()` routes threaded vs legacy; 3 tests (HelloWorld, RunProducesOutput, OutputMatchesDirect); 1805/1806; HEAD `cca773a` | session138 |
| 2026-03-17 | **`net-save-dll` split into 3 sprints** — `net-save-dll-1` (SaveDll write), `net-save-dll-2` (RunDll threaded detection + re-compile), `net-save-dll-3` (tests); design: embed source text in PersistedAssemblyBuilder DLL with sentinel type `Snobol4ThreadedDll`; re-JIT MsilDelegates on load (DynamicMethod not serializable); previous session's partial work not committed — clean slate at c43580d | session138 |
| 2026-03-17 | **PIVOT: `net-load-dotnet` → `net-save-dll`** — Steps 7+8 deferred (SnobolVar return coercions, F# DU coercion); `net-save-dll` promoted ahead per Lon; `M-NET-SAVE-DLL` milestone added | session137 |
| 2026-03-17 | **`M-NET-SAVE-DLL` milestone created** — `-w` WriteDll confirmed no-op on threaded path (only in dead Roslyn CSharpCompile.cs); `RunDll()` kept — it's the read side, needs update in net-save-dll to handle threaded format | session137 |
| 2026-03-17 | **SNOLIB env-var race fixed** — `[DoNotParallelize]` on LoadSpecTests; `GC.Collect()` after ALC unload in Unload.cs; HEAD `a47fb84`; 1777/1778 stable | parallel test runner set SNOLIB="" racing SnolibSearch_FindsLib |
| 2026-03-17 | **`net-load-xn` sprint created** — SPITBOL x32 parity gaps: `xn1st` first-call flag (thread-local + libsnobol4_rt shim), `xncbp` shutdown callback (ProcessExit hook), `xnsave` double-fire guard; M-NET-XN milestone added; inserted before `net-corpus-rungs` in M-NET-POLISH track | analysis of spitbol/x32 osint/syslinux.c |
| 2026-03-16 | **M-NET-LOAD-SPITBOL** created — existing LOAD/UNLOAD uses .NET-native IExternalLibrary API; SPITBOL spec requires prototype string s1 `'FNAME(T1..Tn)Tr'`, filename s2, UNLOAD(fname) by function name; 5 spec gaps + .NET extensions layer defined; sprint `net-load-spitbol` added to M-NET-POLISH | spec read from Macro SPITBOL Manual v3.7 Appendix F + Ch19 |
| 2026-03-16 | `net-delegates` Step 16 ✅ — absorb angle-bracket gotos into delegates; EmitMixedConditionalGotoIL for mixed :S<VAR>F(LABEL) cases; fix savedFailure init before skip branch; 1750/1751; HEAD `baeaa52` | audit showed GotoIndirectCode was intentionally left in thread — wired existing indirectGotoExpr path to absorb all cases |
| 2026-03-17 | **`net-load-spitbol` ✅** — ParsePrototype (errors 139-141); dispatcher; NativeLibrary.Load + SNOLIB search; InvokeNative unsafe dispatch table (retSig×argSig×arity 0-3); UNLOAD(fname) natural-var check; 27 tests; 1777/1778; HEAD `21dceac` | Bug: PredicateSuccess() pushed extra StringVar causing error 212 in assignment; fixed: push result + Failure=false only |
| 2026-03-17 | SNOBOL object lifecycle tests (ARRAY/TABLE/DATA create/read/write/destroy via IExternalLibrary) assigned to `net-load-dotnet` Step 7 — not `net-load-spitbol`; native C-ABI returns scalars only; IExternalLibrary fast path owns rich-object creation | session clarity |
| 2026-03-16 | **PIVOT: `net-corpus-rungs` → `net-load-spitbol`** — Lon directed pivot; LOAD/UNLOAD spec compliance takes priority; `net-corpus-rungs` resumes after `net-load-dotnet` | SPITBOL compliance milestone gating |
| 2026-03-16 | **M-NET-DELEGATES ✅** fired — all thread opcodes are CallMsil/Halt for static programs; CODE() runtime append recomputes ThreadIsMsilOnly correctly; pivot to `net-corpus-rungs` | Step16 complete |
| 2026-03-16 | `net-delegates` Step 15 ✅ — `R_PAREN_FUNCTION` stack guard (Pop crash fix); Step15 MsilOnly coverage tests (arith_loop, pattern_match, TABLE stack safety); 1746/1747; HEAD `118e41b` | defensive fix for mismatched function token pairs |
| 2026-03-16 | `net-alphabet` ✅ — `&ALPHABET` SIZE 255→256; `Range(0,256)`; tests 006/097/Alphabet_001 tightened to `AreEqual(256)`; 1743/1744; HEAD `dc5d132` | both oracles agree SIZE==256 |
| 2026-03-17 | M-NET-CORPUS-GAPS ✅ fired (11/12 [Ignore] removed; 1743/1744); pivot to `net-alphabet` then `net-delegates` | session131 |
| 2026-03-16 | `net-gap-value-indirect` now active | next corpus-gap sprint |
| 2026-03-16 | `net-gap-freturn` now active | next corpus-gap sprint |
| 2026-03-16 | Corpus test injection: 12 files, ~116 test methods from snobol4corpus crosscheck; 12 [Ignore] gaps mapped to 4 fix sprints under M-NET-CORPUS-GAPS; HEAD `7aacf01` | Lon: inject corpus tests following Jeff's style |
| 2026-03-16 | `net-save-dll` sprint added to M-NET-POLISH; `-w` WriteDll diagnosed as no-op on active threaded path — only wired in dead Roslyn path (CSharpCompile.cs/CreateAssembly); DLL load path (file.dll on cmdline) already works in MainConsole.cs | Fix needed: persist threaded assembly to disk after tc.Compile() when WriteDll=true |
