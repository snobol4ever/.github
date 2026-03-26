# snobol4ever — HQ

SNOBOL4/SPITBOL compilers targeting JVM, .NET, and native C.
Shared frontends. Multiple backends.
**Team:** Lon Jones Cherryholmes (arch, MSIL), Jeffrey Cooper M.D. (DOTNET), Claude Sonnet 4.6 (TINY co-author, third developer).

---

## ⚡ NOW

Each concurrent session owns exactly one row. Update only your row on every push. `git pull --rebase` before every push — see RULES.md §CONCURRENT SESSIONS and §NOW TABLE ROW FORMAT.

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **⚠ GRAND MASTER REORG** | G-7 — FRONTEND-PROLOG-JVM.md trimmed 12KB→4.6KB; §NOW bloat + Roadmap removed | `eb9f2ec` G-7 | M-G0-FREEZE (Lon schedules) |
| **⭐ Scrip Demo** | SD-10: Scripten→SCRIP global rename (all files, dirs, content); demo1 dir + run_demo.sh missing — next session creates them | `1e11076` SD-10 | M-SD-DEMO1 |
| **TINY backend** | `main` B-292 — 106/106 | `acbc71e` B-292 | M-BEAUTIFY-BOOTSTRAP-ASM-MONITOR |
| **TINY NET** | `net-t2` N-248 — 110/110 | `425921a` N-248 | M-T2-FULL |
| **TINY JVM** | `main` J-216 — STLIMIT/STCOUNT ✅ | `a74ccd8` J-216 | M-JVM-STLIMIT-STCOUNT |
| **TINY frontend** | `main` F-223 — see TINY.md | `b4507dc` F-223 | M-PROLOG-CORPUS |
| **DOTNET** | `main` D-164 — 1903/1903 | `e1e4d9e` D-164 | TBD |
| **README** | `main` R-2 | `00846d3` | M-README-DEEP-SCAN |
| **ICON frontend** | `main` I-11 — rung03 ✅ | `bab5664` I-11 | M-ICON-STRING |
| **Prolog JVM** | `main` PJ-72 — M-PJ-DCG ✅ · M-PJ-PLUNIT-SHIM ✅ | `4fbe5f1` PJ-72 | M-PJ-SWI-BASELINE |
| **Icon JVM** | `main` IJ-48 ✅ M-IJ-CASE complete; next: M-IJ-NULL-TEST or M-IJ-BLOCK-BODY | `2dad5b3` IJ-48 | M-IJ-NULL-TEST |

**Invariants:** TINY `106/106` (`run_crosscheck_asm_corpus.sh`) · DOTNET `1903/1903` (`dotnet test`)

---

## 4D Matrix

```
Frontends:  SNOBOL4 · Snocone · Rebus · Icon · Prolog · C#/Clojure
Backends:   x64 ASM · JVM bytecode · .NET MSIL · WebAssembly
            [C backend: ☠️ DEAD]
```

| Frontend | TINY-x64 | TINY-NET | TINY-JVM | TINY-WASM | JVM | DOTNET |
|----------|:--------:|:--------:|:--------:|:---------:|:---:|:------:|
| SNOBOL4/SPITBOL | ⏳ | ⏳ | — | — | ⏳ | ⏳ |
| Snocone | — | — | — | — | ⏳ | ⏳ |
| Rebus | — | — | — | — | — | — |
| Icon | — | — | — | — | — | — |
| Prolog | ⏳ | — | — | — | ⏳ | — |
| C#/Clojure | — | — | — | — | — | — |

✅ done · ⏳ active · — planned · ☠️ dead

---

## Milestone Dashboard

### ⭐⭐ Icon JVM — detail → [FRONTEND-ICON-JVM.md](FRONTEND-ICON-JVM.md)
`M-IJ-LISTS` ✅ · `M-IJ-TABLE` ✅ · `M-IJ-RECORD` ✅ · `M-IJ-RECORD-PROCARG` ✅ · `M-IJ-GLOBAL` ✅ · `M-IJ-POW` ✅ · `M-IJ-READ` ✅ · `M-IJ-BUILTINS-STR` ✅ · `M-IJ-BUILTINS-TYPE` ✅ · `M-IJ-BUILTINS-MISC` ✅ · `M-IJ-SORT` ✅ · `M-IJ-ALT-VALUE` ✅ · `M-IJ-STRING-RETVAL` ✅ · `M-IJ-CASE` ✅ · `M-IJ-NULL-TEST` ❌ **NEXT**

### ⭐⭐ Prolog JVM — detail → [FRONTEND-PROLOG-JVM.md](FRONTEND-PROLOG-JVM.md)
`M-PJ-FINDALL` ✅ · `M-PJ-ATOM-BUILTINS` ✅ · `M-PJ-ASSERTZ` ✅ · `M-PJ-RETRACT` ✅ · `M-PJ-ABOLISH` ✅ · `M-PJ-ATOP` ✅ · `M-PJ-SORT` ✅ · `M-PJ-SUCC-PLUS` ✅ · `M-PJ-FORMAT` ✅ · `M-PJ-NUMBER-VARS` ✅ · `M-PJ-CHAR-TYPE` ✅ · `M-PJ-WRITE-CANONICAL` ✅ · `M-PJ-SUCC-ARITH` ✅ · `M-PJ-STRING-IO` ✅ · `M-PJ-TERM-STRING` ✅ · `M-PJ-COPY-TERM` ✅ · `M-PJ-AGGREGATE` ✅ · `M-PJ-EXCEPTIONS` ✅ · `M-PJ-NUMBER-OPS` ✅ · `M-PJ-DCG` ✅ · `M-PJ-PLUNIT-SHIM` ✅ · `M-PJ-SWI-BASELINE` ❌ **NEXT**

### ⭐ Scrip Demo Ladder — detail → [SCRIP_DEMOS.md](SCRIP_DEMOS.md)
`M-SD-DEMO1` ❌ **NEXT** (hello) · `M-SD-DEMO2` ❌ (wordcount) · `M-SD-DEMO3` ❌ (roman) · `M-SD-DEMO4` ❌ (palindrome) · `M-SD-DEMO5` ❌ (fib) · `M-SD-DEMO6` ❌ (sieve) · `M-SD-DEMO7` ❌ (caesar) · `M-SD-DEMO8` ❌ (sort) · `M-SD-DEMO9` ❌ (rpn) · `M-SD-DEMO10` ❌ (anagram)
`M-SCRIP-DEMO` (family tree, now DEMO4) ❌ · `M-SCRIP-DEMO2` (puzzle, now DEMO5) ❌ · `M-SCRIP-DEMO3` (compiler) ❌ *(concept)*

### TINY backend — detail → [BEAUTY.md](BEAUTY.md) · [BACKEND-X64.md](BACKEND-X64.md)
`M-BEAUTIFY-BOOTSTRAP-ASM-MONITOR` ❌ **NEXT** · `M-BEAUTIFY-BOOTSTRAP` ❌ · `M-MONITOR-4DEMO` ❌

### Grand Master Reorg — all ❌ — detail → [GRAND_MASTER_REORG.md](GRAND_MASTER_REORG.md)
Phases 0–8 · ~80 milestones M-G0-FREEZE → M-G8-CI · **NEXT: M-G0-FREEZE (Lon schedules)**

### ICON frontend (ASM) — detail → [FRONTEND-ICON.md](FRONTEND-ICON.md)
`M-ICON-STRING` ❌ **NEXT** · `M-ICON-SCAN` ❌ · `M-ICON-CSET` ❌ · `M-ICON-CORPUS-R4` ❌

### Grid + README v2 — detail → [GRIDS.md](GRIDS.md)
`M-FEAT-JVM` ❌ **NEXT** · `M-FEAT-DOTNET` ❌ · `M-GRID-*×8` ❌ · `M-README-V2-*×3` ❌ · `M-PROFILE-V2` ❌

---

## Doc Index

| File | Level | Read when |
|------|-------|-----------|
| [SESSIONS_ARCHIVE.md](SESSIONS_ARCHIVE.md) | L5 | `tail -80` — **step 1 of every session** |
| [RULES.md](RULES.md) | L3 | Every session |
| [ARCH.md](ARCH.md) | L3 | Every session |
| [TINY.md](TINY.md) | L2 | B/N/J/F sessions |
| [JVM.md](JVM.md) | L2 | snobol4jvm sessions |
| [DOTNET.md](DOTNET.md) | L2 | D sessions |
| [FRONTEND-SNOBOL4.md](FRONTEND-SNOBOL4.md) | L4 | SNOBOL4 frontend |
| [FRONTEND-ICON.md](FRONTEND-ICON.md) | L4 | I sessions |
| [FRONTEND-ICON-JVM.md](FRONTEND-ICON-JVM.md) | L4 | IJ sessions |
| [FRONTEND-PROLOG.md](FRONTEND-PROLOG.md) | L4 | F sessions |
| [FRONTEND-PROLOG-JVM.md](FRONTEND-PROLOG-JVM.md) | L4 | PJ sessions |
| [FRONTEND-SNOCONE.md](FRONTEND-SNOCONE.md) | L4 | Snocone sessions |
| [FRONTEND-REBUS.md](FRONTEND-REBUS.md) | L4 | Rebus sessions |
| [BACKEND-X64.md](BACKEND-X64.md) | L4 | B sessions |
| [BACKEND-JVM.md](BACKEND-JVM.md) | L4 | J sessions |
| [BACKEND-NET.md](BACKEND-NET.md) | L4 | N sessions |
| [BEAUTY.md](BEAUTY.md) | L4 | beauty.sno sprint |
| [GRAND_MASTER_REORG.md](GRAND_MASTER_REORG.md) | L4 | G sessions only |
| [SCRIP_DEMO.md](SCRIP_DEMO.md) | L4 | SD sessions |
| [PATCHES.md](PATCHES.md) | L4 | runtime patch work |
| [MILESTONE_ARCHIVE.md](MILESTONE_ARCHIVE.md) | L5 | append only |

---

*PLAN.md = L1. 3KB max. NOW table + milestone IDs only. No sprint content. No completed rows. Ever.*
*Milestone fires → move to MILESTONE_ARCHIVE.md, update NOW table, update L4 doc.*
