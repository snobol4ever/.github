# snobol4ever — HQ

SNOBOL4/SPITBOL compilers targeting JVM, .NET, and native C.
Shared frontends. Multiple backends. Self-hosting goal: sno2c compiles sno2c.
**Team:** Lon Jones Cherryholmes (arch, MSIL), Jeffrey Cooper M.D. (DOTNET Roslyn), Claude Sonnet 4.6 (TINY co-author, third developer).

---

## ⚡ NOW

| | |
|-|-|
| **Active repo** | snobol4dotnet |
| **Sprint** | `net-load-dotnet` Steps 7+8 — SnobolVar/Pattern/Table/Array return coercions + F# DU coercion layer |
| **HEAD TINY** | `cf27329` session136: AGPL-3.0 LICENSE + badge added |
| **HEAD HARNESS** | `9fed541` session136: MIT badge added to README |
| **HEAD CORPUS** | `9c00acd` session136: CC0 badge + NOTICE added |
| **HEAD DOTNET** | `6edc653` session139: net-load-dotnet Step 7 ✅ |
| **HEAD HQ** | (this commit) session139 |
| **Next action** | `net-load-dotnet` Step 8: F# option/DU coercion layer — `option<T>` → fail/value, discriminated unions → SnobolVar; F# library loads and executes correctly |
| **Invariant** | `dotnet test` → 1832/1833 before any dotnet work |

**Read the active L2 doc: [DOTNET.md](DOTNET.md)**

---

## Goals

**Goal 1 — Fill the 4D matrix:**
Every cell of Product × Frontend × Backend is implemented, tested, and benchmarked.

**Goal 2 — Self-hosting:**
`sno2c` compiles `sno2c`. The compiler writes itself. Milestone: `M-BOOTSTRAP`.

**Goal 3 — Created Intelligence substrate:**
The Byrd Box model — one universal pattern engine — runs SNOBOL4, Icon, Prolog, Snocone, and Rebus on JVM, .NET, and native x64. The grammar machine is the AI engine.

---

## 4D Matrix

```
Products:   TINY (native C/x64) · JVM (Clojure→bytecode) · DOTNET (C#→MSIL)
Frontends:  SNOBOL4 · Snocone · Rebus · Icon · Prolog · C#/Clojure
Backends:   C (portable) · x64 ASM (native) · JVM bytecode · .NET MSIL
Matrix:     Feature matrix (correctness) · Benchmark matrix (performance)
```

| Frontend | TINY-C | TINY-x64 | TINY-NET | TINY-JVM | JVM | DOTNET |
|----------|:------:|:--------:|:--------:|:--------:|:---:|:------:|
| SNOBOL4/SPITBOL | ⏳ | — | — | — | ⏳ | ⏳ |
| Snocone | — | — | — | — | ⏳ | ⏳ |
| Rebus | ✅ | — | — | — | — | — |
| Icon | — | — | — | — | — | — |
| Prolog | — | — | — | — | — | — |
| C#/Clojure | — | — | — | — | — | — |

✅ done · ⏳ active · — planned

---

## Milestone Dashboard

One row per milestone. Milestones fire when their trigger condition is true.
Sprint detail lives in the active platform L2 doc (TINY.md / JVM.md / DOTNET.md).

### TINY (snobol4x)

| ID | Trigger | Status |
|----|---------|--------|
| M-SNOC-COMPILES | snoc compiles beauty_core.sno | ✅ |
| M-REBUS | Rebus round-trip diff empty | ✅ `bf86b4b` |
| M-COMPILED-BYRD | sno2c emits Byrd boxes, mock_engine only | ✅ `560c56a` |
| M-CNODE | CNode IR, zero lines >120 chars | ✅ `ac54bd2` |
| M-STACK-TRACE | oracle == compiled stack trace, rung-12 inputs | ✅ session119 |
| **M-MONITOR** | 152 corpus tests: oracle_trace == compiled_trace, zero diffs | ⏳ Sprint M1 |
| **M-DIAG1** | 35/35 diag1 suite TINY vs CSNOBOL4 oracle | ⏳ via M-MONITOR |
| M-BEAUTY-CORE | beauty_full_bin self-beautifies (mock stubs) | ❌ |
| M-BEAUTY-FULL | beauty_full_bin self-beautifies (real -I inc/) | ❌ |
| M-FLAT | flat() emitter wired, Style B verified | ❌ |
| M-CODE-EVAL | CODE()+EVAL() via TCC | ❌ |
| **M-BOOTSTRAP** | sno2c_stage1 output = sno2c_stage2 | ❌ |

### JVM (snobol4jvm)

| ID | Trigger | Status |
|----|---------|--------|
| M-JVM-EVAL | Inline EVAL! — arithmetic no longer calls interpreter | ❌ Sprint `jvm-inline-eval` |
| M-JVM-SNOCONE | Snocone self-test: compile snocone.sc, diff oracle | ❌ |
| M-JVM-BOOTSTRAP | snobol4-jvm compiles itself | ❌ |

### DOTNET (snobol4dotnet)

| ID | Trigger | Status |
|----|---------|--------|
| **M-NET-CORPUS-GAPS** | 12 corpus [Ignore] tests pass — PROTOTYPE/FRETURN/VALUE/EVAL | ✅ `e21e944` session131 — 11/12; 1012 semicolons separate gap |
| M-NET-DELEGATES | Instruction[] → pure Func<Executive,int>[] dispatch | ✅ `baeaa52` |
| **M-NET-LOAD-SPITBOL** | LOAD/UNLOAD spec-compliant: prototype string, UNLOAD(fname), type coercion, SNOLIB, Error 202 | ✅ `21dceac` |
| **M-NET-SAVE-DLL** | `-w file.sno` → `file.dll` (threaded assembly); `snobol4 file.dll` runs it; RunDll() updated | ❌ Sprint `net-save-dll` |
| **M-NET-LOAD-DOTNET** | Full .NET extension layer: auto-prototype via reflection, multi-function assemblies, async/cancellation, IExternalLibrary fast path, any IL language (F#/VB/C++) | ❌ Sprint `net-load-dotnet` |
| **M-NET-XN** | SPITBOL x32 C-ABI parity: xn1st first-call flag, xncbp shutdown callback, xnsave double-fire guard; libsnobol4_rt.so helper shim | ❌ Sprint `net-load-xn` |
| M-NET-SNOCONE | Snocone self-test: compile snocone.sc, diff oracle | ❌ |
| **M-NET-POLISH** | 106/106 corpus rungs pass, diag1 35/35, benchmark grid published | ❌ see DOTNET.md |
| M-NET-BOOTSTRAP | snobol4-dotnet compiles itself | ❌ |

### Shared (all products)

| ID | Trigger | Status |
|----|---------|--------|
| M-FEATURE-MATRIX | Feature × product grid 100% green | ❌ |
| M-BENCHMARK-MATRIX | Benchmark × product grid published | ❌ |

---

## L2 — Platform docs (read when working on that platform)

| File | What |
|------|------|
| [TINY.md](TINY.md) | snobol4x — HEAD, build, active sprint + steps, milestone map, pivot log |
| [JVM.md](JVM.md) | snobol4jvm — HEAD, lein commands, active sprint + steps, pivot log |
| [DOTNET.md](DOTNET.md) | snobol4dotnet — HEAD, dotnet commands, active sprint + steps, pivot log |
| [HARNESS.md](HARNESS.md) | snobol4harness — oracle builds, probe, monitor, benchmarks |
| [CORPUS.md](CORPUS.md) | snobol4corpus — layout, update protocol |

## L3 — Reference (read when you need deep detail)

| File | What |
|------|------|
| [TESTING.md](TESTING.md) | Four paradigms, corpus ladder, oracle index, keyword/TRACE grid |
| [MONITOR.md](MONITOR.md) | M-MONITOR design: TRACE double-diff, 8 sprints M1–M8 |
| [ARCH.md](ARCH.md) | Byrd Box model, shared architecture concepts |
| [IMPL-SNO2C.md](IMPL-SNO2C.md) | sno2c compiler internals |
| [FRONTEND-SNOBOL4.md](FRONTEND-SNOBOL4.md) | SNOBOL4/SPITBOL frontend, beauty.sno |
| [BACKEND-C.md](BACKEND-C.md) | C backend: Byrd boxes, block functions |
| [BACKEND-JVM.md](BACKEND-JVM.md) | JVM bytecode backend |
| [BACKEND-NET.md](BACKEND-NET.md) | .NET MSIL backend |
| [RULES.md](RULES.md) | Mandatory rules — token, identity, artifacts ← **read every session** |
| [PATCHES.md](PATCHES.md) | Runtime patch audit trail |
| [MISC.md](MISC.md) | Background, story, JCON reference |
| [SESSIONS_ARCHIVE.md](SESSIONS_ARCHIVE.md) | Full session history — append-only |

---

*PLAN.md = L1 index only. Never add sprint content here. Milestone fires → update dashboard. Sprint changes → update platform L2 doc.*
