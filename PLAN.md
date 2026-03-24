# snobol4ever — HQ

SNOBOL4/SPITBOL compilers targeting JVM, .NET, and native C.
Shared frontends. Multiple backends.
**Team:** Lon Jones Cherryholmes (arch, MSIL), Jeffrey Cooper M.D. (DOTNET), Claude Sonnet 4.6 (TINY co-author, third developer).

---

## ⚡ NOW

Each concurrent session owns exactly one row. Update only your row on every push. `git pull --rebase` before every push — see RULES.md §CONCURRENT SESSIONS and §NOW TABLE ROW FORMAT.

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **TINY backend** | `main` B-285 — full accounting: 106/106 ASM ✅; beauty 15/19 (is/TDump/Gen/semantic FAIL); bootstrap Parse Error after header | `deae788` B-284 | M-BEAUTIFY-BOOTSTRAP |
| **TINY NET** | `net-t2` N-248 — M-T2-NET ✅ 110/110 clean | `425921a` N-248 | M-T2-FULL |
| **TINY JVM** | `jvm-t2` J-213 — M-T2-JVM ✅ 106/106 clean | `8178b5c` J-213 | M-T2-FULL |
| **TINY frontend** | `main` F-223 — rung05 encoding fix attempted, reverted clean; see TINY.md | `b4507dc` F-223 | M-PROLOG-CORPUS |
| **DOTNET** | `main` D-164 — 1903/1903 pass 0 fail on Linux | `e1e4d9e` D-164 | TBD |
| **README** | `main` — M-README-CSHARP-DRAFT ✅ | `00846d3` snobol4csharp | M-README-DEEP-SCAN |
| **ICON frontend** | `main` I-10 — SESSIONS_ARCHIVE pruned 782KB→15KB; fixes documented, not yet applied | `54031a5` I-7 | M-ICON-CORPUS-R3 |
| **Prolog JVM** | `main` PJ-9 — fix var-slot mismatch + non-linear head + pj_term_str; rungs 01-05 PASS | `5ae73e3` PJ-9 | M-PJ-LISTS |
| **Icon JVM** | `main` IJ-6 — Fix1+Fix2+Fix3+Fix2b applied; VerifyErrors dead; no-output bug for IJ-7 | `a3d4a55` IJ-6 | M-IJ-CORPUS-R3 |
| **README v2 sprint** | `main` R-2 | TBD R-2 | M-FEAT-JVM |

**Invariants (check before any work):**
- TINY: `106/106` ASM corpus (`run_crosscheck_asm_corpus.sh`) · ALL PASS ✅
- DOTNET: `dotnet test` → 1903/1903 (Linux); 0 failures

**Read the active L2 docs: [TINY.md](TINY.md) · [JVM.md](JVM.md) · [DOTNET.md](DOTNET.md)**

---

## Goals

*(Clean slate — new goals TBD.)*

---

## 4D Matrix

```
Products:   TINY (native x64) · JVM (Clojure→bytecode) · DOTNET (C#→MSIL)
Frontends:  SNOBOL4 · Snocone · Rebus · Icon · Prolog · C#/Clojure
Backends:   x64 ASM (native) · JVM bytecode · .NET MSIL
            [C backend: ☠️ DEAD — 99/106, sno2c failures on word*/pat_alt_commit; not maintained]
Matrix:     Feature matrix (correctness) · Benchmark matrix (performance)
```

| Frontend | TINY-x64 | TINY-NET | TINY-JVM | JVM | DOTNET |
|----------|:--------:|:--------:|:--------:|:---:|:------:|
| SNOBOL4/SPITBOL | ⏳ | ⏳ | — | ⏳ | ⏳ |
| Snocone | — | — | — | ⏳ | ⏳ |
| Rebus | — | — | — | — | — |
| Icon | — | — | — | — | — |
| Prolog | ⏳ | — | — | ⏳ | — |
| C#/Clojure | — | — | — | — | — |

✅ done · ⏳ active · — planned · ☠️ dead

---

## Milestone Dashboard

> Completed milestones → [MILESTONE_ARCHIVE.md](MILESTONE_ARCHIVE.md)
> One row per **active or future** milestone. ✅ rows move to archive on session end.

### TINY backend — Active + Upcoming

| ID | Trigger | Status |
|----|---------|--------|
| **M-BUG-IS-DIALECT** | `is` driver: both IsSnobol4+IsSpitbol succeed in ASM — dialect detection broken | ❌ |
| **M-BUG-TDUMP-TLUMP** | `TDump` driver: TLump returns `.` instead of tree string — DATATYPE/field dispatch | ❌ |
| **M-BUG-GEN-BUFFER** | `Gen` driver: buffered output emits `]` then crashes at step 5 — Gen buffer flush | ❌ |
| **M-BUG-SEMANTIC-NTYPE** | `semantic` driver: nPush/nInc/nPop return PATTERN but DATATYPE reports STRING in ASM | ❌ |
| **M-BUG-BOOTSTRAP-PARSE** | beauty bootstrap: ASM outputs `Parse Error` after 10-line header; INCLUDE expansion fails | ❌ |
| **M-SNO2C-FOLD** | sno2c lexer folds identifiers to uppercase; `-F`/`-f` switches | ❌ |
| **M-MON-BUG-SPL-EMPTY** | SPITBOL trace empty for treebank/claws5 — diagnose + fix | ❌ |
| **M-MON-BUG-ASM-DATATYPE-CASE** | ASM DATA type name lowercase; fix to uppercase | ❌ |
| **M-MON-BUG-JVM-WPAT** | JVM pattern datatype emits empty string; fix | ❌ |
| **M-MONITOR-4DEMO** | roman + wordcount + treebank pass all 5 participants | ❌ |
| **M-BEAUTIFY-BOOTSTRAP** | beauty.sno reads + writes itself; fixed point | ❌ |
| **M-MONITOR-GUI** | 🌙 HTML/React monitor GUI — diverging cells highlighted | 💭 |

### Prolog Frontend — Active

| ID | Trigger | Status |
|----|---------|--------|
| **M-PROLOG-BUILTINS** | `functor/3`, `arg/3`, `=../2`, type tests — rung09 PASS | ✅ |
| **M-PROLOG-R10** | Lon's word-puzzle solvers — rung10 PASS | ✅ |
| **M-PROLOG-CORPUS** | All 10 rungs PASS via `-pl -asm` | ❌ |

Full sprint detail → [FRONTEND-PROLOG.md](FRONTEND-PROLOG.md)

### Prolog JVM — Active

Full sprint detail → [BACKEND-JVM-PROLOG.md](BACKEND-JVM-PROLOG.md) · [FRONTEND-PROLOG-JVM.md](FRONTEND-PROLOG-JVM.md)

### ICON Frontend — Active

| ID | Trigger | Status |
|----|---------|--------|
| **M-ICON-CORPUS-R3** | Rung 3: user procedures + generators | ✅ |
| **M-ICON-STRING** | `ICN_STR`, `\|\|` concat | ❌ |
| **M-ICON-SCAN** | `E ? E` string scanning | ❌ |
| **M-ICON-CSET** | Cset literals → BREAK/SPAN/ANY | ❌ |
| **M-ICON-CORPUS-R4** | Rung 4: string operations and scanning | ❌ |

Full sprint detail → [FRONTEND-ICON.md](FRONTEND-ICON.md)



### Icon JVM Frontend — Active

| ID | Trigger | Status |
|----|---------|--------|
| **M-IJ-SCAFFOLD** | `icon_emit_jvm.c` exists; `-jvm null.icn → null.j` assembles + exits 0 | ✅ |
| **M-IJ-HELLO** | `every write(1 to 5);` → JVM `1\n2\n3\n4\n5` | ✅ |
| **M-IJ-CORPUS-R1** | All 6 rung01 tests PASS vs ASM oracle | ✅ |
| **M-IJ-PROC** | rung02_proc: user procedures + locals | ❌ |
| **M-IJ-CORPUS-R2** | rung02 arith_gen 5/5 + proc 3/3 PASS | ✅ |
| **M-IJ-SUSPEND** | `suspend E` generators via tableswitch resume | ❌ |
| **M-IJ-CORPUS-R3** | rung03_suspend PASS | ❌ |
| **M-IJ-STRING** | `ICN_STR`, `\|\|` concat | ❌ |
| **M-IJ-SCAN** | `E ? E` string scanning | ❌ |
| **M-IJ-CSET** | Cset literals → BREAK/SPAN/ANY | ❌ |
| **M-IJ-CORPUS-R4** | Rung 4: string ops + scanning PASS | ❌ |

Full sprint detail → [FRONTEND-ICON-JVM.md](FRONTEND-ICON-JVM.md)

### Grid + README v2 — Active

| ID | Repo | Status |
|----|------|--------|
| **M-FEAT-JVM** | snobol4jvm | ❌ **NEXT** |
| **M-FEAT-DOTNET** | snobol4dotnet | ❌ |
| **M-GRID-BENCH** | .github | ❌ |
| **M-GRID-CORPUS** | .github | ❌ |
| **M-GRID-COMPAT** | .github | ❌ |
| **M-GRID-REFERENCE** | .github | ❌ |
| **M-GRID-STARTUP** | .github | ❌ |
| **M-GRID-OPERATOR** | .github | ❌ |
| **M-GRID-SWITCH-FULL** | .github | ❌ |
| **M-README-V2-X** | snobol4x | ❌ |
| **M-README-V2-JVM** | snobol4jvm | ❌ |
| **M-README-V2-DOTNET** | snobol4dotnet | ❌ |
| **M-PROFILE-V2** | .github | ❌ |

Full trigger specs → [GRIDS.md](GRIDS.md)

---

## L2/L3 Index

| File | Level | What |
|------|-------|------|
| [TINY.md](TINY.md) | L2 | snobol4x — HEAD, build, active sprint, pivot log |
| [JVM.md](JVM.md) | L2 | snobol4jvm — HEAD, lein commands, active sprint |
| [DOTNET.md](DOTNET.md) | L2 | snobol4dotnet — HEAD, dotnet commands, active sprint |
| [RULES.md](RULES.md) | L3 | Mandatory rules ← **read every session** |
| [BEAUTY.md](BEAUTY.md) | L3 | beauty.sno subsystem test plan: 19 drivers |
| [MONITOR.md](MONITOR.md) | L3 | 5-way monitor design and runner |
| [ARCH.md](ARCH.md) | L3 | Byrd Box model, shared architecture |
| [SESSIONS_ARCHIVE.md](SESSIONS_ARCHIVE.md) | L3 | Full session history — append-only |
| [MILESTONE_ARCHIVE.md](MILESTONE_ARCHIVE.md) | L3 | All ✅ completed milestone rows |
| [FRONTEND-PROLOG.md](FRONTEND-PROLOG.md) | L3 | Prolog frontend sprint detail |
| [FRONTEND-ICON.md](FRONTEND-ICON.md) | L3 | Icon frontend sprint detail |
| [FRONTEND-PROLOG-JVM.md](FRONTEND-PROLOG-JVM.md) | L3 | Prolog→JVM frontend sprint detail |
| [FRONTEND-ICON-JVM.md](FRONTEND-ICON-JVM.md) | L3 | Icon→JVM frontend sprint detail |
| [TESTING.md](TESTING.md) | L3 | Corpus ladder, oracle index |
| [PATCHES.md](PATCHES.md) | L3 | Runtime patch audit trail |

---

*PLAN.md = L1 index only. ~3KB max. No sprint content. No step content. No completed milestone rows. Ever.*
*Milestone fires → move its row to MILESTONE_ARCHIVE.md, update NOW table, update L2 doc.*
