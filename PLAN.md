# snobol4ever — HQ

SNOBOL4/SPITBOL compilers targeting JVM, .NET, and native C.
Shared frontends. Multiple backends. Self-hosting goal: sno2c compiles sno2c.
**Team:** Lon Jones Cherryholmes (arch, MSIL), Jeffrey Cooper M.D. (DOTNET), Claude Sonnet 4.6 (TINY co-author, third developer).

---

## ⚡ NOW

Each concurrent session owns exactly one row. Update only your row on every push. Never touch another session's row. `git pull --rebase` before every push — see RULES.md.

Session numbers use per-type prefixes (see RULES.md §SESSION NUMBERS): B=backend, J=JVM, N=NET, F=frontend, D=DOTNET.

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **TINY backend** | `asm-backend` A-SAMPLES — roman.sno + wordcount.sno PASS | `3f2c8b9` B-201 | M-ASM-SAMPLES |
| **TINY JVM** | `jvm-backend` J5 — capture rung: . and $ capture | `09a3f4d` J-200 | M-JVM-CAPTURE |
| **TINY NET** | `net-backend` N-R2 — verify goto/:S/:F + E_FNC results | `b15164e` N-198 | M-NET-GOTO |
| **TINY frontend** | `sc-corpus-ladder` SC-CORPUS-2 — control/ | `23765b1` F-192 | M-SC-CORPUS-R2 |
| **DOTNET** | `net-perf-analysis` — dotnet test + BenchmarkSuite2 re-run | `a029cae` D-156 | M-NET-PERF |

**Invariants (check before any work):**
- TINY: `106/106` C crosscheck · `26/26` ASM crosscheck
- DOTNET: `dotnet test` → 1869/1872 before any dotnet work

**Read the active L2 docs: [TINY.md](TINY.md) · [JVM.md](JVM.md) · [DOTNET.md](DOTNET.md)**

---

## ⛔ ARTIFACT REMINDER — VISIBLE EVERY SESSION

**Every session that changes `emit_byrd_asm.c` or any `.sno` → `.s` path MUST:**

1. `src/sno2c/sno2c -asm -I$INC $BEAUTY > artifacts/asm/beauty_prog.s`
2. `nasm -f elf64 -I src/runtime/asm/ artifacts/asm/beauty_prog.s -o /dev/null` — confirm clean
3. `git add artifacts/asm/beauty_prog.s && git commit`

**One canonical file per artifact. Never create `beauty_prog_sessionN.s`. Git history is the archive.**

See also: RULES.md §ASM ARTIFACTS

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
| SNOBOL4/SPITBOL | ⏳ | — | ⏳ | — | ⏳ | ⏳ |
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
| **M-ASM-NAMED** | Named patterns flat labels PASS | ✅ session148 |
| **M-ASM-CROSSCHECK** | 106/106 via ASM backend | ✅ session151 |
| **M-ASM-R1** | hello/ + output/ — 12 tests PASS via run_crosscheck_asm_rung.sh | ✅ session188 |
| **M-ASM-R2** | assign/ — 8 tests PASS | ✅ session188 |
| **M-ASM-R3** | concat/ — 6 tests PASS | ✅ session187 |
| **M-ASM-R4** | arith/ — 2 tests PASS | ✅ session188 |
| **M-ASM-R5** | control/ + control_new/ — goto/:S/:F PASS | ✅ session189 |
| **M-ASM-R6** | patterns/ — 20 program-mode pattern tests PASS | ✅ session189 |
| **M-ASM-R7** | capture/ — 7 tests PASS | ✅ session190 |
| **M-ASM-R8** | strings/ — SIZE/SUBSTR/REPLACE/DUPL PASS | ✅ session192 |
| **M-ASM-R9** | keywords/ — IDENT/DIFFER/GT/LT/EQ/DATATYPE PASS | ✅ session193 |
| **M-ASM-R10** | functions/ — DEFINE/RETURN/FRETURN/recursion PASS | ✅ session197 |
| **M-ASM-R11** | data/ — ARRAY/TABLE/DATA PASS | ✅ session198 |
| **M-ASM-SAMPLES** | roman.sno and wordcount.sno pass via ASM backend; artifacts/asm/roman.s and artifacts/asm/wordcount.s committed and assembling clean | ❌ |
| **M-DROP-MOCK-ENGINE** | `mock_engine.c` removed from ASM program link path; 26-test harness suite migrated to full `.sno` format or harness rewritten to not call `engine_match`; 26/26 + 106/106 hold without linking `mock_engine.o` in ASM path | ✅ `06df4cb` B-200 |
| **M-SNOC-LEX** | sc_lex.c: all Snocone tokens; `OUTPUT = 'hello'` → 3 tokens PASS | ✅ `573575e` session183 |
| **M-SNOC-PARSE** | sc_parse.c: full stmt grammar; SC corpus exprs + control flow PASS | ✅ `5e20058` session184 |
| **M-SNOC-LOWER** | sc_lower.c: Snocone AST → EXPR_t/STMT_t wired | ✅ `2c71fc1` session185 |
| **M-SNOC-ASM-HELLO** | `-sc -asm`: `OUTPUT='hello'` → assembles + runs → `hello` | ✅ `9148a77` session187 |
| **M-SNOC-ASM-CF** | DEFINE calling convention; `double(5)` → 10 via `-sc -asm` | ✅ `0371fad` session188 |
| **M-SNOC-ASM-CORPUS** | SC corpus 10-rung all PASS via `-sc -asm` | ✅ `d8901b4` session189 |
| **M-SNOC-ASM-SELF** | snocone.sc compiles itself via `-sc -asm`; diff oracle empty | ❌ Sprint SC6-ASM |
| **M-SNOC-EMIT** | `-sc` flag in sno2c; `OUTPUT = 'hello'` .sc → C binary PASS | ❌ (deferred — C backend) |
| **M-SNOC-CORPUS** | SC corpus 10-rung all PASS (C backend) | ❌ Sprint SC4 (deferred) |
| **M-SNOC-SELF** | snocone.sc compiles itself via C pipeline; diff oracle empty | ❌ Sprint SC5 (deferred) |
| **M-REORG** | Full repo layout: frontend/ ir/ backend/ driver/ runtime/; binary at snobol4x/sno2c; 106/106 26/26 from new paths | ✅ `f3ca7f2` session181 |
| **M-ASM-READABLE** | Special-char expansion: asm_expand_name(); _ literal passthrough; uid on collision (M-ASM-READABLE-A). Original spec revised — pure bijection without _ escape destroys readability. | ✅ `e0371fe` session176 |
| **M-ASM-MACROS** | NASM macro library `snobol4_asm.mac` — every emitted line is `LABEL  MACRO(args)  GOTO`. LIT/SPAN/SEQ/ALT/DOL/SUBJECT/MATCH/REPLACE/GOTO. Three-column .s matches three-column .c. | ❌ Sprint A12 |
| **M-ASM-IR** | ASM IR phase: AsmNode tree between parse and emit. Same architecture as CNode. Separates tree walk from pretty-print. One IR, two emitters (C + ASM). | ⏸ DEFERRED — ASM and C backends may need different IR shapes. Revisit after both reach feature parity. Premature unification risks blocking ASM progress. |
| **M-ASM-BEAUTIFUL** | beauty_prog.s as readable as beauty_full.c. Lon reads it and declares it beautiful. | ✅ `7d6add6` session175 |
| **M-BOOTSTRAP** | sno2c_stage1 output = sno2c_stage2 | ❌ |
| **M-SC-CORPUS-R1** | hello/output/assign/arith all PASS via `-sc -asm` | ✅ session192 |
| **M-SC-CORPUS-R2** | control/control_new all PASS via `-sc -asm` | ❌ |
| **M-SC-CORPUS-R3** | patterns/capture all PASS via `-sc -asm` | ❌ |
| **M-SC-CORPUS-R4** | strings/ all PASS via `-sc -asm` | ❌ |
| **M-SC-CORPUS-R5** | keywords/functions/data all PASS via `-sc -asm` | ❌ |
| **M-SC-CORPUS-FULL** | 106/106 SC equivalent of SNOBOL4 crosscheck | ❌ |

### JVM (snobol4jvm)

| ID | Trigger | Status |
|----|---------|--------|
| M-JVM-EVAL | Inline EVAL! — arithmetic no longer calls interpreter | ❌ Sprint `jvm-inline-eval` |
| M-JVM-SNOCONE | Snocone self-test: compile snocone.sc, diff oracle | ❌ |
| M-JVM-BOOTSTRAP | snobol4-jvm compiles itself | ❌ |

### JVM backend — snobol4x TINY (emit_byrd_jvm.c)

| ID | Trigger | Status |
|----|---------|--------|
| **M-JVM-HELLO** | null.sno → .class → java null → exit 0 | ✅ session194 |
| **M-JVM-LIT** | OUTPUT = 'hello' correct via JVM backend | ✅ session195 |
| **M-JVM-ASSIGN** | Variable assign + arith correct | ✅ session197 |
| **M-JVM-GOTO** | :S(X)F(Y) branching correct | ✅ J-198 |
| **M-JVM-PATTERN** | Byrd boxes in JVM — LIT/SEQ/ALT/ARBNO | ✅ J-199 |
| **M-JVM-CAPTURE** | . and $ capture correct | ❌ Sprint J5 |
| **M-JVM-R1** | hello/ output/ assign/ arith/ — Rungs 1–4 PASS | ❌ Sprint J-R1 |
| **M-JVM-R2** | control/ patterns/ capture/ — Rungs 5–7 PASS | ❌ Sprint J-R2 |
| **M-JVM-R3** | strings/ keywords/ — Rungs 8–9 PASS | ❌ Sprint J-R3 |
| **M-JVM-R4** | functions/ data/ — Rungs 10–11 PASS | ❌ Sprint J-R4 |
| **M-JVM-CROSSCHECK** | 106/106 corpus PASS via JVM backend | ❌ Sprint J-R5 |
| **M-JVM-SAMPLES** | roman.sno + wordcount.sno PASS | ❌ Sprint J-S1 |
| **M-JVM-BEAUTY** | beauty.sno self-beautifies via JVM backend | ❌ Sprint J10 |

### NET backend — snobol4x TINY (net_emit.c)

| ID | Trigger | Status |
|----|---------|--------|
| **M-NET-HELLO** | `sno2c -net null.sno > null.il && ilasm null.il && mono null.exe` → exit 0 | ✅ session195 |
| **M-NET-LIT** | `OUTPUT = 'hello'` → `hello` via NET backend | ✅ `efc3772` N-197 |
| **M-NET-ASSIGN** | Variable assign + arith correct | ❌ Sprint N-R2 |
| **M-NET-GOTO** | :S(X)F(Y) branching correct | ❌ Sprint N-R3 |
| **M-NET-PATTERN** | Byrd boxes in CIL — LIT/SEQ/ALT/ARBNO | ❌ Sprint N-R4 |
| **M-NET-CAPTURE** | . and $ capture correct | ❌ Sprint N-R5 |
| **M-NET-R1** | hello/ output/ assign/ arith/ — Rungs 1–4 PASS | ❌ Sprint N-R1 |
| **M-NET-R2** | control/ patterns/ capture/ — Rungs 5–7 PASS | ❌ Sprint N-R2 |
| **M-NET-R3** | strings/ keywords/ — Rungs 8–9 PASS | ❌ Sprint N-R3 |
| **M-NET-R4** | functions/ data/ — Rungs 10–11 PASS | ❌ Sprint N-R4 |
| **M-NET-CROSSCHECK** | 106/106 corpus PASS via NET backend | ❌ Sprint N-R5 |
| **M-NET-SAMPLES** | roman.sno + wordcount.sno PASS | ❌ Sprint N-S1 |
| **M-NET-BEAUTY** | beauty.sno self-beautifies via NET backend | ❌ Sprint N-10 |

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
