# SNOBOL4ever — HQ

SNOBOL4/SPITBOL compilers: one shared frontend (beauty.sno → compiler.sno),
three backends (C native, JVM, .NET). Self-hosting goal: sno2c compiles sno2c.
**Team:** Lon Jones Cherryholmes (arch), Jeffrey Cooper M.D. (DOTNET), Claude Sonnet 4.6 (TINY author).

---

## ⚡ NOW — read this, know what to do

| | |
|-|-|
| **Active repo** | SNOBOL4-tiny |
| **Sprint** | `beauty-crosscheck` — Sprint A — rung 12 crosscheck tests |
| **HEAD** | `08eabba` |
| **Next action** | Build beauty_full_bin → write 101_comment test → run run_beauty.sh → Sprint A |
| **Invariant** | 106/106 rungs 1–11 must pass before any work |

**If working on TINY → read [TINY.md](TINY.md)**
**If working on JVM  → read [JVM.md](JVM.md)**
**If working on .NET → read [DOTNET.md](DOTNET.md)**

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
| M-NET-DELEGATES | .NET Instruction[] eliminated | DOTNET | ❌ |

---

## Platform Map (frontend × backend)

| Platform | Repo | L2 doc | Sprint | Next milestone |
|----------|------|--------|--------|---------------|
| C native | [SNOBOL4-tiny](https://github.com/SNOBOL4-plus/SNOBOL4-tiny) | [TINY.md](TINY.md) | `beauty-crosscheck` | M-BEAUTY-CORE |
| JVM/Clojure | [SNOBOL4-jvm](https://github.com/SNOBOL4-plus/SNOBOL4-jvm) | [JVM.md](JVM.md) | `jvm-inline-eval` | M-JVM-EVAL |
| .NET/C# | [SNOBOL4-dotnet](https://github.com/SNOBOL4-plus/SNOBOL4-dotnet) | [DOTNET.md](DOTNET.md) | `net-delegates` | M-NET-DELEGATES |
| Corpus | [SNOBOL4-corpus](https://github.com/SNOBOL4-plus/SNOBOL4-corpus) | [CORPUS.md](CORPUS.md) | Stable | — |
| Harness | [SNOBOL4-harness](https://github.com/SNOBOL4-plus/SNOBOL4-harness) | [HARNESS.md](HARNESS.md) | Stable | — |

---

## L2 → L3 Reference Map

*Read L2 (platform doc) first. Go deeper only when needed.*

| L2 doc | When you need more detail → read L3 |
|--------|--------------------------------------|
| TINY.md | Architecture deep dive → [ARCH.md](ARCH.md) |
| Any platform | Testing protocol, four paradigms → [TESTING.md](TESTING.md) |
| Any platform | Mandatory rules (token, identity, artifacts) → [RULES.md](RULES.md) |
| Any platform | Session history → [SESSIONS_ARCHIVE.md](SESSIONS_ARCHIVE.md) |
| Any platform | Runtime patches → [PATCHES.md](PATCHES.md) |
| Background | Origin, JCON, keyword tables → [MISC.md](MISC.md) |

---

*PLAN.md = L1 index only. Max 4096 bytes. Edit downstream files, not this one.*
*When Lon says "update HQ": update the L2 or L3 file, not PLAN.md.*
