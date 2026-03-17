# snobol4ever — HQ

SNOBOL4/SPITBOL compilers targeting JVM, .NET, and native C.
Shared frontends. Multiple backends. Self-hosting goal: sno2c compiles sno2c.
**Team:** Lon Jones Cherryholmes (arch, MSIL), Jeffrey Cooper M.D. (DOTNET), Claude Sonnet 4.6 (TINY co-author, third developer).

---

## ⚡ NOW

| | |
|-|-|
| **Active repos** | `snobol4x` (TINY) · `snobol4dotnet` (DOTNET) |
| **TINY sprint** | `asm-backend` — Sprint A7: ASM harness → emitter crosscheck |
| **TINY HEAD** | `20f81a5` session148: M-ASM-ASSIGN ✅; assign_lit.s + assign_digits.s + E_DOL in emit_byrd_asm.c |
| **TINY next** | Sprint A8: named patterns — ref_astar_bstar.s + anbn.s + asm_emit_named() |
| **DOTNET sprint** | `net-corpus-rungs` — 106/106 crosscheck rungs 1–11 against DOTNET |
| **DOTNET HEAD** | `26e2144` session148: M-NET-XN ✅ |
| **DOTNET next** | net-corpus-rungs: run crosscheck, fix all failures |
| **HEAD HARNESS** | `9fed541` session136 |
| **HEAD CORPUS** | `9c00acd` session136 |
| **HEAD HQ** | (this commit) session146 |
| **Invariant TINY** | `106/106` crosscheck before any snobol4x work |
| **Invariant DOTNET** | `dotnet test` → 1869/1872 before any dotnet work |
| **⚠ Concurrent push** | `git pull --rebase origin main` before every .github push — see RULES.md |

**Read the active L2 docs: [TINY.md](TINY.md) (TINY chat) · [DOTNET.md](DOTNET.md) (DOTNET chat)**

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
| **M-ASM-HELLO** | null.s assembles+links+runs → exit 0 | ✅ session145 |
| **M-ASM-LIT** | LIT node: lit_hello.s PASS | ✅ session146 |
| **M-ASM-SEQ** | SEQ/POS/RPOS crosscheck PASS | ✅ session146 |
| **M-ASM-ALT** | ALT crosscheck PASS | ✅ session147 |
| **M-ASM-ARBNO** | ARBNO crosscheck PASS | ✅ session147 |
| **M-ASM-CHARSET** | ANY/NOTANY/SPAN/BREAK PASS | ✅ session147 |
| **M-ASM-ASSIGN** | $ capture PASS | ✅ session148 |
| **M-ASM-NAMED** | Named patterns flat labels PASS | ❌ Sprint A8 |
| **M-ASM-CROSSCHECK** | 106/106 via ASM backend | ❌ Sprint A9 |
| **M-ASM-BEAUTY** | beauty.sno self-beautifies via ASM | ❌ Sprint A10 |
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
| **M-NET-LOAD-DOTNET** | Full .NET extension layer: auto-prototype via reflection, multi-function assemblies, async/cancellation, IExternalLibrary fast path, any IL language (F#/VB/C++) | ✅ `1e9ad33` session140 |
| **M-NET-EXT-NOCONV** | SPITBOL noconv pass-through: ARRAY/TABLE/PDBLK passed unconverted; C block struct mirror in libsnobol4_rt.h; IExternalLibrary traversal API | ❌ Sprint `net-ext-noconv` |
| **M-NET-EXT-XNBLK** | XNBLK opaque persistent state: C function allocates/returns state block; xndta[] private storage; .NET per-entry Dictionary equivalent | ✅ `b821d4d` session145 |
| **M-NET-EXT-CREATE** | Foreign creates SNO objects: libsnobol4_rt alloc helpers for C-ABI; .NET IExternalLibrary already capable — C-side tests | ✅ `6dfae0e` session145 |
| **M-NET-VB** | VB.NET fixture + tests: string/long/double returns, null→fail, static, multi-load, UNLOAD | ✅ `234f24a` session142 |
| **M-NET-XN** | SPITBOL x32 C-ABI parity: xn1st first-call flag, xncbp shutdown callback, xnsave double-fire guard; libsnobol4_rt.so helper shim | ✅ `26e2144` session148 |
| M-NET-SNOCONE | Snocone self-test: compile snocone.sc, diff oracle | ❌ |
| **M-NET-PERF** | Performance profiling: hot-path report, ≥1 measurable win landed, regression baseline published | ❌ Sprint `net-perf-analysis` |
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
