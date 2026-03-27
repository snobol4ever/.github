# snobol4ever — HQ

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

Developer documentation for the snobol4ever project.
Three tiers: L1 (entry), L2 (platform), L3 (detail). Read only what you need.

---

## L1 — Start here

| File | What it is |
|------|------------|
| [PLAN.md](PLAN.md) | NOW pointer · milestone dashboard · product matrix · L3 index |

## L2 — One per platform (read when working on that platform)

| File | What it is |
|------|------------|
| [TINY.md](TINY.md) | snobol4x — HEAD, build commands, sprint, frontier table, pivot log |
| [JVM.md](JVM.md) | snobol4jvm — HEAD, lein commands, sprint, pivot log |
| [DOTNET.md](DOTNET.md) | snobol4dotnet — HEAD, dotnet commands, sprint, pivot log |
| [ARCH-corpus.md](ARCH-corpus.md) | snobol4corpus — layout, update protocol |
| [ARCH-harness.md](ARCH-harness.md) | snobol4harness — oracles, probe, benchmarks |

## L3 — Frontends (one per input language)

| File | What it is |
|------|------------|
| [FRONTEND-SNOBOL4.md](FRONTEND-SNOBOL4.md) | SNOBOL4/SPITBOL — beauty.sno, TDD protocol, rung 12, probe/monitor/triangulate |
| [FRONTEND-SNOCONE.md](FRONTEND-SNOCONE.md) | Snocone — status across repos, corpus, sprint sequence |
| [FRONTEND-REBUS.md](FRONTEND-REBUS.md) | Rebus — TR 84-9 §5 translation rules, round-trip protocol |
| [FRONTEND-ICON.md](FRONTEND-ICON.md) | Tiny-ICON — TINY only, planned, JCON reference |
| [FRONTEND-PROLOG.md](FRONTEND-PROLOG.md) | Tiny-Prolog — TINY only, planned |
| [FRONTEND-CSHARP.md](FRONTEND-CSHARP.md) | C# frontend — DOTNET only, planned |
| [FRONTEND-CLOJURE.md](FRONTEND-CLOJURE.md) | Clojure-EDN — JVM only, active |

## L3 — Backends (one per output target)

| File | What it is |
|------|------------|
| [BACKEND-C.md](BACKEND-C.md) | C native — Byrd box techniques, block functions, setjmp, arch decisions |
| [BACKEND-X64.md](BACKEND-X64.md) | x64 ASM — TINY planned, Technique 2 spec |
| [BACKEND-NET.md](BACKEND-NET.md) | .NET MSIL — solution layout, open issues, performance |
| [BACKEND-JVM.md](BACKEND-JVM.md) | JVM bytecodes — design laws, file map, open issues |

## L3 — Implementation & shared reference

| File | What it is |
|------|------------|
| [IMPL-SNO2C.md](IMPL-SNO2C.md) | sno2c compiler — lex/parse/emit, SIL naming, CNode IR, artifacts |
| [ARCH.md](ARCH.md) | Shared architecture — Byrd box concept, oracle hierarchy |
| [ARCH-testing.md](ARCH-testing.md) | Four testing paradigms · corpus ladder protocol |
| [RULES.md](RULES.md) | Mandatory rules — token, identity, artifacts, hierarchy |
| [PATCHES.md](PATCHES.md) | Runtime patch audit trail |
| [MISC.md](MISC.md) | Background, JCON reference, keyword tables |
| [RENAME.md](RENAME.md) | One-time rename plan (snobol4ever → snobol4ever) |
| [ARCH-status.md](ARCH-status.md) | Live test counts and benchmarks |
| [SESSIONS_ARCHIVE.md](SESSIONS_ARCHIVE.md) | Full session history — append-only |
