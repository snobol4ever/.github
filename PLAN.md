# SNOBOL4ever — HQ

SNOBOL4/SPITBOL compilers targeting JVM, .NET, and native C.
Shared frontends. Multiple backends. Self-hosting goal: sno2c compiles sno2c.
**Team:** Lon Jones Cherryholmes (arch, MSIL), Jeffrey Cooper M.D. (DOTNET Roslyn), Claude Sonnet 4.6 (TINY co-author, third developer).

---

## ⚡ NOW

| | |
|-|-|
| **Active repo** | SNOBOL4-jvm |
| **Sprint** | `jvm-inline-eval` — polish M-JVM-EVAL, emit arith/assign/cmp into JVM bytecode |
| **HEAD TINY** | `8761bc1` session121: 5-primitive SEQ counter instrumented |
| **HEAD HARNESS** | `0bf728b` session124: oracle-verify complete — keyword grid live-verified |
| **HEAD CORPUS** | `82907ff` session122: M-DIAG1 suite committed 35/35 CSNOBOL4 oracle |
| **HEAD JVM** | `9cf0af3` jvm-snocone-expr complete |
| **HEAD HQ** | `ab12de7` session126: fix stale &STCOUNT claims across all MD files |
| **Next action** | `jvm-inline-eval` — implement inline EVAL! in jvm_codegen.clj, lein test confirm 1896/4120/0 |
| **Invariant** | 106/106 rungs 1–11 must pass before any work on SNOBOL4-tiny |

**Read the active L2 doc: [JVM.md](JVM.md)**

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

### TINY (SNOBOL4-tiny)

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

### JVM (SNOBOL4-jvm)

| ID | Trigger | Status |
|----|---------|--------|
| M-JVM-EVAL | Inline EVAL! — arithmetic no longer calls interpreter | ❌ Sprint `jvm-inline-eval` |
| M-JVM-SNOCONE | Snocone self-test: compile snocone.sc, diff oracle | ❌ |
| M-JVM-BOOTSTRAP | snobol4-jvm compiles itself | ❌ |

### DOTNET (SNOBOL4-dotnet)

| ID | Trigger | Status |
|----|---------|--------|
| M-NET-DELEGATES | Instruction[] → pure Func<Executive,int>[] dispatch | ❌ Sprint `net-delegates` |
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
| [TINY.md](TINY.md) | SNOBOL4-tiny — HEAD, build, active sprint + steps, milestone map, pivot log |
| [JVM.md](JVM.md) | SNOBOL4-jvm — HEAD, lein commands, active sprint + steps, pivot log |
| [DOTNET.md](DOTNET.md) | SNOBOL4-dotnet — HEAD, dotnet commands, active sprint + steps, pivot log |
| [HARNESS.md](HARNESS.md) | SNOBOL4-harness — oracle builds, probe, monitor, benchmarks |
| [CORPUS.md](CORPUS.md) | SNOBOL4-corpus — layout, update protocol |

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
