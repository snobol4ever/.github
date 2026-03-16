# SNOBOL4ever — HQ

SNOBOL4/SPITBOL compilers targeting JVM, .NET, and native C.
Shared frontends. Multiple backends. Self-hosting goal: sno2c compiles sno2c.
**Team:** Lon Jones Cherryholmes (arch, MSIL), Jeffrey Cooper M.D. (DOTNET Roslyn), Claude Sonnet 4.6 (TINY co-author, third developer).

---

## ⚡ NOW

| | |
|-|-|
| **Active repo** | SNOBOL4-tiny |
| **Sprint** | `beauty-crosscheck` — Sprint A — rung 12 crosscheck tests |
| **HEAD** | `session107` |
| **Next action** | Fix E_DEREF(E_FNC) in emit_byrd.c — drops args, causes Function/BuiltinVar misclassification |
| **Invariant** | 106/106 rungs 1–11 must pass before any work |

**Read the active L2 doc: [TINY.md](TINY.md) · [JVM.md](JVM.md) · [DOTNET.md](DOTNET.md)**

---

## Product Matrix (frontend × backend)

| Frontend | TINY-C | TINY-x64 | TINY-NET | TINY-JVM | JVM | DOTNET |
|----------|:------:|:--------:|:--------:|:--------:|:---:|:------:|
| SNOBOL4/SPITBOL | ⏳ | — | — | — | ⏳ | ⏳ |
| Snocone | — | — | — | — | ⏳ | ⏳ |
| Rebus | ✅ | — | — | — | — | — |
| Tiny-ICON | — | — | — | — | — | — |
| Tiny-Prolog | — | — | — | — | — | — |
| C# | — | — | — | — | — | — |
| Clojure-EDN | — | — | — | — | ✅ | — |

✅ done · ⏳ active/in-progress · — planned/future

---

## Milestone Dashboard

| ID | Trigger | Repo | ✓ |
|----|---------|------|---|
| M-SNOC-COMPILES | snoc compiles beauty_core.sno | TINY | ✅ |
| M-REBUS | Rebus round-trip diff empty | TINY | ✅ `bf86b4b` |
| M-COMPILED-BYRD | sno2c emits Byrd boxes, mock_engine only | TINY | ✅ `560c56a` |
| M-CNODE | CNode IR, zero lines >120 chars | TINY | ✅ `ac54bd2` |
| **M-BEAUTY-CORE** | beauty_full_bin self-beautifies (mock stubs) | TINY | ❌ |
| **M-BEAUTY-FULL** | beauty_full_bin self-beautifies (real -I inc/) | TINY | ❌ |
| M-CODE-EVAL | CODE()+EVAL() via TCC → block_fn_t | TINY | ❌ |
| M-BYRD-SPEC | Language-agnostic Byrd box spec, all backends | HQ | ❌ |
| M-SNO2C-SNO | sno2c.sno compiled by C sno2c | TINY | ❌ |
| M-BOOTSTRAP | sno2c_stage1 output = sno2c_stage2 | TINY | ❌ |
| M-JVM-EVAL | JVM inline EVAL! | JVM | ❌ |
| M-JVM-SNOCONE | Snocone self-test on JVM | JVM | ❌ |
| M-NET-DELEGATES | .NET Instruction[] eliminated | DOTNET | ❌ |
| M-NET-SNOCONE | Snocone self-test on .NET | DOTNET | ❌ |

---

## L3 Reference Index

| Read when you need… | File |
|--------------------|------|
| **Frontends** | |
| SNOBOL4/SPITBOL: beauty.sno, TDD protocol, rung 12, probe/monitor/triangulate | [FRONTEND-SNOBOL4.md](FRONTEND-SNOBOL4.md) |
| Snocone: status, corpus, sprint sequence | [FRONTEND-SNOCONE.md](FRONTEND-SNOCONE.md) |
| Rebus: TR 84-9 §5 rules, round-trip protocol | [FRONTEND-REBUS.md](FRONTEND-REBUS.md) |
| Tiny-ICON: Byrd box connection, JCON reference | [FRONTEND-ICON.md](FRONTEND-ICON.md) |
| Tiny-Prolog: SLD resolution / Byrd box mapping | [FRONTEND-PROLOG.md](FRONTEND-PROLOG.md) |
| C# frontend (DOTNET only) | [FRONTEND-CSHARP.md](FRONTEND-CSHARP.md) |
| Clojure-EDN frontend (JVM only) | [FRONTEND-CLOJURE.md](FRONTEND-CLOJURE.md) |
| **Backends** | |
| C native: Byrd box techniques, block functions, setjmp, arch decisions | [BACKEND-C.md](BACKEND-C.md) |
| x64 ASM: Technique 2 mmap+memcpy+relocate | [BACKEND-X64.md](BACKEND-X64.md) |
| .NET MSIL: solution layout, open issues, performance | [BACKEND-NET.md](BACKEND-NET.md) |
| JVM bytecodes: design laws, file map, open issues | [BACKEND-JVM.md](BACKEND-JVM.md) |
| **Implementation** | |
| sno2c compiler internals: lex/parse/emit, SIL naming, CNode, artifacts | [IMPL-SNO2C.md](IMPL-SNO2C.md) |
| **Shared** | |
| Byrd box concept, oracle hierarchy, corpus ladder | [ARCH.md](ARCH.md) |
| Four testing paradigms, corpus ladder protocol | [TESTING.md](TESTING.md) |
| Mandatory rules: token, identity, artifacts, hierarchy | [RULES.md](RULES.md) |
| Session history | [SESSIONS_ARCHIVE.md](SESSIONS_ARCHIVE.md) |
| Runtime patches | [PATCHES.md](PATCHES.md) |
| Background, JCON reference, keyword tables | [MISC.md](MISC.md) |

---

*PLAN.md = L1 index only. ~3KB max. Edit L2/L3 files, not this one.*
