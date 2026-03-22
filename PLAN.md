# snobol4ever — HQ

SNOBOL4/SPITBOL compilers targeting JVM, .NET, and native C.
Shared frontends. Multiple backends.
**Team:** Lon Jones Cherryholmes (arch, MSIL), Jeffrey Cooper M.D. (DOTNET), Claude Sonnet 4.6 (TINY co-author, third developer).

---

## ⚡ NOW

Each concurrent session owns exactly one row. Update only your row on every push. Never touch another session's row. `git pull --rebase` before every push — see RULES.md.

Session numbers use per-type prefixes (see RULES.md §SESSION NUMBERS): B=backend, J=JVM, N=NET, F=frontend, D=DOTNET.

**Isolation guarantee:** No session ever works on two same frontends or two same backends. Each session owns one frontend OR one backend. Rebases on common code go smoothly because of this isolation.

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **TINY backend** | `asm-t2` B-245 — T2 codename removed | `66b7148` B-245 | M-T2-CORPUS |
| **TINY NET** | `net-backend` N-209 — clean slate | `2c417d7` N-209 | TBD |
| **TINY JVM** | `jvm-backend` J-212 — clean slate | `b67d0b1` J-212 | TBD |
| **TINY frontend** | `main` F-210 — clean slate | `6495074` F-210 | TBD |
| **DOTNET** | `net-polish` D-163 — clean slate | `8feb139` D-163 | TBD |
| **README** | `main` — M-README-CSHARP-DRAFT ✅ | `00846d3` snobol4csharp | M-README-DEEP-SCAN (next) |

**Invariants (check before any work):**
- TINY: `97/106` ASM corpus (`run_crosscheck_asm_corpus.sh`) · 9 known failures: 022, 055, 064, cross, word1-4, wordcount
- DOTNET: `dotnet test` → 1873/1876 before any dotnet work

**Read the active L2 docs: [TINY.md](TINY.md) · [JVM.md](JVM.md) · [DOTNET.md](DOTNET.md)**

---

## ⛔ ARTIFACT REMINDER — VISIBLE EVERY SESSION

**All five demo programs and data live in `demo/` — single source of truth.**
Every session that changes `emit_byrd_asm.c` or any `.sno` → `.s` path MUST regenerate all tracked artifacts:

| Artifact | Source | Assembles clean? |
|----------|--------|--------------------|
| `artifacts/asm/beauty_prog.s` | `demo/beauty.sno` | ✅ required |
| `artifacts/asm/samples/roman.s` | `demo/roman.sno` | ✅ required |
| `artifacts/asm/samples/wordcount.s` | `demo/wordcount.sno` | ✅ required |
| `artifacts/asm/samples/treebank.s` | `demo/treebank.sno` | ✅ required |
| `artifacts/asm/samples/claws5.s` | `demo/claws5.sno` | ⚠️ track error count (3 undef β labels) |

See RULES.md §ASM ARTIFACTS for the full regeneration script (`INC=demo/inc`).

**One canonical file per artifact. Never create `beauty_prog_sessionN.s`. Git history is the archive.**

---

## Goals

*(Clean slate — new goals TBD.)*

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

> **Clean slate reset 2026-03-21 — all incomplete milestones archived.**

### TINY (snobol4x) — Completed

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
| **M-ASM-R1** | hello/ + output/ — 12 tests PASS | ✅ session188 |
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
| **M-ASM-RECUR** | Recursive SNOBOL4 functions correct via ASM backend | ✅ `266c866` B-204 |
| **M-ASM-SAMPLES** | roman.sno and wordcount.sno pass via ASM backend | ✅ `266c866` B-204 |
| **M-ASM-RUNG8** | rung8/ — REPLACE/SIZE/DUPL 3/3 PASS | ✅ `1d0a983` B-223 |
| **M-ASM-RUNG9** | rung9/ — CONVERT/DATATYPE/INTEGER/LGT 5/5 PASS | ✅ `3133497` B-210 |
| **M-DROP-MOCK-ENGINE** | mock_engine.c removed from ASM link path | ✅ `06df4cb` B-200 |
| **M-FLAT-NARY** | Parser: E_CONC and E_OR flat n-ary nodes | ⚠ `6495074` F-209 |
| **M-EMITTER-NAMING** | All four emitters canonical; Greek labels α/β/γ/ω | ✅ `69b52b8` B-222 |
| **M-SNOC-LEX** | sc_lex.c: all Snocone tokens | ✅ `573575e` session183 |
| **M-SNOC-PARSE** | sc_parse.c: full stmt grammar | ✅ `5e20058` session184 |
| **M-SNOC-LOWER** | sc_lower.c: Snocone AST → EXPR_t/STMT_t wired | ✅ `2c71fc1` session185 |
| **M-SNOC-ASM-HELLO** | `-sc -asm`: OUTPUT='hello' → assembles + runs | ✅ `9148a77` session187 |
| **M-SNOC-ASM-CF** | DEFINE calling convention via `-sc -asm` | ✅ `0371fad` session188 |
| **M-SNOC-ASM-CORPUS** | SC corpus 10-rung all PASS via `-sc -asm` | ✅ `d8901b4` session189 |
| **M-REORG** | Full repo layout: frontend/ ir/ backend/ driver/ runtime/ | ✅ `f3ca7f2` session181 |
| **M-ASM-READABLE** | Special-char expansion: asm_expand_name() | ✅ `e0371fe` session176 |
| **M-ASM-BEAUTIFUL** | beauty_prog.s as readable as beauty_full.c | ✅ `7d6add6` session175 |
| **M-SC-CORPUS-R1** | hello/output/assign/arith all PASS via `-sc -asm` | ✅ session192 |

### JVM backend — snobol4x TINY — Completed

| ID | Trigger | Status |
|----|---------|--------|
| **M-JVM-HELLO** | null.sno → .class → java null → exit 0 | ✅ session194 |
| **M-JVM-LIT** | OUTPUT = 'hello' correct via JVM backend | ✅ session195 |
| **M-JVM-ASSIGN** | Variable assign + arith correct | ✅ session197 |
| **M-JVM-GOTO** | :S(X)F(Y) branching correct | ✅ J-198 |
| **M-JVM-PATTERN** | Byrd boxes in JVM — LIT/SEQ/ALT/ARBNO | ✅ J-199 |
| **M-JVM-CAPTURE** | . and $ capture correct | ✅ `62c668f` J-201 |
| **M-JVM-R1** | hello/ output/ assign/ arith/ — Rungs 1–4 PASS | ✅ `2b1d6a9` J-202 |
| **M-JVM-R2** | control/ patterns/ capture/ — Rungs 5–7 PASS | ✅ `fa293a1` J-203 |
| **M-JVM-R3** | strings/ keywords/ — Rungs 8–9 PASS | ✅ `fa293a1` J-203 |
| **M-JVM-R4** | functions/ data/ — Rungs 10–11 PASS | ✅ `876eb4b` J-205 |
| **M-JVM-CROSSCHECK** | 106/106 corpus PASS via JVM backend | ✅ `a063ed9` J-208 |
| **M-JVM-SAMPLES** | roman.sno + wordcount.sno PASS | ✅ `13245e2` J-210 |
| **M-JVM-BEAUTY** | beauty.sno self-beautifies via JVM backend | ✅ `b67d0b1` J-212 |

### NET backend — snobol4x TINY — Completed

| ID | Trigger | Status |
|----|---------|--------|
| **M-NET-HELLO** | sno2c -net null.sno → exit 0 | ✅ session195 |
| **M-NET-LIT** | OUTPUT = 'hello' → hello via NET backend | ✅ `efc3772` N-197 |
| **M-NET-ASSIGN** | Variable assign + arith correct | ✅ `02d1f9b` N-206 |
| **M-NET-GOTO** | :S(X)F(Y) branching correct | ✅ `02d1f9b` N-206 |
| **M-NET-PATTERN** | Byrd boxes in CIL — LIT/SEQ/ALT/ARBNO | ✅ `02d1f9b` N-206 |
| **M-NET-CAPTURE** | . and $ capture correct | ✅ `590509b` N-202 |
| **M-NET-R1** | hello/ output/ assign/ arith/ — Rungs 1–4 PASS | ✅ `02d1f9b` N-206 |
| **M-NET-R2** | control/ patterns/ capture/ — Rungs 5–7 PASS | ✅ `02d1f9b` N-206 |
| **M-NET-R3** | strings/ keywords/ — Rungs 8–9 PASS | ✅ `02d1f9b` N-206 |
| **M-NET-CROSSCHECK** | 110/110 corpus PASS via NET backend | ✅ `fbca6aa` N-208 |
| **M-NET-SAMPLES** | roman.sno + wordcount.sno PASS | ✅ `2c417d7` N-209 |

### DOTNET (snobol4dotnet) — Completed

| ID | Trigger | Status |
|----|---------|--------|
| **M-NET-CORPUS-GAPS** | 12 corpus [Ignore] tests pass | ✅ `e21e944` session131 |
| M-NET-DELEGATES | Instruction[] → pure Func<Executive,int>[] dispatch | ✅ `baeaa52` |
| **M-NET-LOAD-SPITBOL** | LOAD/UNLOAD spec-compliant | ✅ `21dceac` |
| **M-NET-LOAD-DOTNET** | Full .NET extension layer | ✅ `1e9ad33` session140 |
| **M-NET-EXT-XNBLK** | XNBLK opaque persistent state | ✅ `b821d4d` session145 |
| **M-NET-EXT-CREATE** | Foreign creates SNO objects | ✅ `6dfae0e` session145 |
| **M-NET-VB** | VB.NET fixture + tests | ✅ `234f24a` session142 |
| **M-NET-XN** | SPITBOL x32 C-ABI parity | ✅ `26e2144` session148 |
| **M-NET-PERF** | Performance profiling: hot-path report, ≥1 measurable win | ✅ `e8a5fec` D-159 |
| **M-NET-SPITBOL-SWITCHES** | All SPITBOL CLI switches; 26 unit tests PASS | ✅ `8feb139` D-163 |

### New Milestones — Five-Way Monitor + Beautify Bootstrap

Sprint detail and runner design → [MONITOR.md](MONITOR.md)

| ID | Trigger | Repo | Status |
|----|---------|------|--------|
| **M-MONITOR-SCAFFOLD** | `test/monitor/` exists: `inject_traces.py` + `run_monitor.sh` + `tracepoints.conf`; CSNOBOL4 + ASM; single test passes | snobol4x | ✅ `19e26ca` B-227 |
| **M-MONITOR-IPC-SO** | `monitor_ipc.c` → `monitor_ipc.so`; MON_OPEN/MON_SEND/MON_CLOSE; CSNOBOL4 LOAD() confirmed; no stderr output | snobol4x | ✅ `8bf1c0c` B-229 |
| **M-MONITOR-IPC-CSN** | `inject_traces.py` emits LOAD+MON_OPEN preamble; MONCALL/MONRET/MONVAL call MON_SEND(); CSNOBOL4 trace arrives on FIFO; hello PASS | snobol4x | ✅ `6eebdc3` B-229 |
| **M-X64-S1** | snobol4ever/x64: `syslinux.c` compiles clean — `callef`/`loadef`/`nextef`/`unldef` all use `xndta[]` not missing `struct ef` fields; `mword` = `long` throughout; `make bootsbl` succeeds | snobol4ever/x64 | ✅ `88ff40f` B-231 |
| **M-X64-S2** | `LOAD('spl_add(INTEGER,INTEGER)INTEGER','libspl.so')` works end-to-end; `spl_add(3,4)` returns `7`; uses snobol4dotnet `SpitbolCLib` test fixture | snobol4ever/x64 | ✅ `145773e` B-232 |
| **M-X64-S3** | UNLOAD lifecycle; reload; double-unload safe | snobol4ever/x64 | ✅ `7193a51` B-233 |
| **M-X64-S4** | SNOLIB search; STRING ABI; monitor_ipc_spitbol.so LOAD confirmed in SPITBOL | snobol4ever/x64 | ✅ `4fcb0e1` B-233 |
| **M-X64-FULL** | S1–S4 fired; SPITBOL confirmed 5-way monitor participant | snobol4ever/x64 | ✅ `4fcb0e1` B-233 |
| **M-MONITOR-IPC-5WAY** | all 5 participants (CSNOBOL4+SPITBOL+ASM+JVM+NET) write trace to per-participant FIFO; `run_monitor.sh` parallel launch + collector; hello PASS all 5; zero stderr/stdout blending | snobol4x | ✅ `064bb59` B-236 |
| **M-MONITOR-IPC-TIMEOUT** | `monitor_collect.py` per-participant watchdog: FIFO silence > T seconds → TIMEOUT report with last trace event + participant kill; infinite loop detected automatically | snobol4x | ✅ `c6a6544` B-237 |
| **M-MERGE-3WAY** | `asm-backend` + `jvm-backend` + `net-backend` merged into `main` via staged merge-staging branch; all invariants hold after merge; fresh fan-out tags cut (`v-post-merge`); three new per-backend branches from tag | snobol4x | ✅ `425921a` B-239 |
| **M-T2-RUNTIME** | `src/runtime/asm/t2_alloc.c`: `t2_alloc(size)` → mmap RW; `t2_free(ptr,size)` → munmap; `t2_mprotect_rx/rw` toggle; unit test passes | snobol4x | ✅ `ab2254f` B-239 |
| **M-T2-RELOC** | `src/runtime/asm/t2_reloc.c`: `t2_relocate(text,len,delta,table,n)` patches relative jumps + absolute DATA refs; unit test with synthetic table passes | snobol4x | ✅ `b992be8` B-239 |
| **M-T2-EMIT-TABLE** | `emit_byrd_asm.c` emits per-box relocation table as NASM data: `box_N_reloc_table` lists (offset, kind) for every relative ref and DATA ref; null.sno assembles clean | snobol4x | ✅ `06e1bdc` B-239 |
| **M-T2-EMIT-SPLIT** | `emit_byrd_asm.c` splits each named box into separate aligned TEXT+DATA sections; `r12` reserved as DATA-block pointer; all locals `[r12+offset]` not `[rbp-N]`; null.sno + hello.sno assemble and run | snobol4x | ✅ `9968688` B-240 ⚠ 3 regressions to fix |
| **M-MACRO-BOX** | Complete macro coverage: every Byrd box type gets one NASM macro per port (α/β/γ/ω); ARBNO fully macroized (currently raw inline asm); all emitter `saved`/`cursor_save` refs use `bref()` — no bare `.bss` symbol names in call sites; 97/106 invariant holds | snobol4x | ✅ `b606884` B-242 |
| **M-T2-INVOKE** | `emit_byrd_asm.c` emits T2 call-sites: `t2_alloc` + `memcpy TEXT` + `t2_relocate` + `memcpy DATA` + `mov r12,new_data` + `jmp new_text_α`; γ/ω emit `t2_free`; corpus rungs 1–9 still pass | snobol4x | ✅ `1cf8a0a` B-243 |
| **M-T2-RECUR** | Recursive SNOBOL4 functions correct under T2: two simultaneous live DATA blocks, one shared CODE; roman.sno correct; stack-frame bridge (`push rbp`) removed | snobol4x | ✅ `1cf8a0a` B-244 |
| **M-T2-CORPUS** | 106/106 ASM corpus under T2 — 9 known failures fixed by construction; no per-bug patches | snobol4x | ❌ |
| **M-T2-JVM** | JVM backend T2-correct: per-invocation objects on JVM heap (natural); 106/106 JVM corpus clean | snobol4x | ❌ |
| **M-T2-NET** | NET backend T2-correct: per-invocation objects on CLR heap; 110/110 NET corpus clean | snobol4x | ❌ |
| **M-T2-FULL** | All three backends T2-correct; `v-post-t2` tag cut; MONITOR sprint resumes from clean base | snobol4x | ❌ |
| **M-MONITOR-4DEMO** | roman + wordcount + treebank pass all 5 participants; claws5 divergence count documented | snobol4x | ❌ |
| **M-MONITOR-CORPUS9** | Run remaining corpus failures through 5-way monitor post-T2; first diverging trace line identifies any residual bugs; ASM corpus at 106/106 confirmed | snobol4x | ❌ |
| **M-BEAUTY-GLOBAL** | global.sno driver passes ASM via monitor | snobol4x | ❌ |
| **M-BEAUTY-IS** | is.sno driver passes | snobol4x | ❌ |
| **M-BEAUTY-FENCE** | FENCE.sno driver passes | snobol4x | ❌ |
| **M-BEAUTY-IO** | io.sno driver passes | snobol4x | ❌ |
| **M-BEAUTY-CASE** | case.sno driver passes | snobol4x | ❌ |
| **M-BEAUTY-ASSIGN** | assign.sno driver passes | snobol4x | ❌ |
| **M-BEAUTY-MATCH** | match.sno driver passes | snobol4x | ❌ |
| **M-BEAUTY-COUNTER** | counter.sno driver passes | snobol4x | ❌ |
| **M-BEAUTY-STACK** | stack.sno driver passes | snobol4x | ❌ |
| **M-BEAUTY-TREE** | tree.sno driver passes | snobol4x | ❌ |
| **M-BEAUTY-SR** | ShiftReduce.sno driver passes | snobol4x | ❌ |
| **M-BEAUTY-TDUMP** | TDump.sno driver passes | snobol4x | ❌ |
| **M-BEAUTY-GEN** | Gen.sno driver passes | snobol4x | ❌ |
| **M-BEAUTY-QIZE** | Qize.sno driver passes | snobol4x | ❌ |
| **M-BEAUTY-READWRITE** | ReadWrite.sno driver passes | snobol4x | ❌ |
| **M-BEAUTY-XDUMP** | XDump.sno driver passes | snobol4x | ❌ |
| **M-BEAUTY-SEMANTIC** | semantic.sno driver passes | snobol4x | ❌ |
| **M-BEAUTY-OMEGA** | omega.sno driver passes | snobol4x | ❌ |
| **M-BEAUTY-TRACE** | trace.sno driver passes | snobol4x | ❌ |
| **M-BEAUTIFY-BOOTSTRAP** | All 19 M-BEAUTY-* fire; `beauty.sno` reads itself; all 3 backends = oracle = input; fixed point | snobol4x | ❌ |
| **M-MONITOR-GUI** | 🌙 *Dream* — HTML/React monitor GUI: source + trace matrix, diverging cells highlighted | snobol4x | 💭 |

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
| [MONITOR.md](MONITOR.md) | M-MONITOR design: TRACE double-diff, sprints M1–M5, beauty piecemeal approach |
| [BEAUTY.md](BEAUTY.md) | beauty.sno subsystem test plan: 19 drivers, milestone map, driver format, Gimpel cross-refs |
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

---

## Grid Milestones — Community Presentation Layer

> These milestones gate the public presentation of comparison data.
> No grid cell is published until the milestone for that grid has fired.
> All runs go through snobol4harness against snobol4corpus.
> Oracle: CSNOBOL4 2.3.3 (`snobol4 -f -P256k -I$INC file.sno`)
> Machine spec must be recorded at time of run (CPU, RAM, OS, date).

| ID | Trigger | Grid | Status |
|----|---------|------|--------|
| **M-GRID-BENCH** | All 7 engine columns of Grid 1 filled from actual timed runs via snobol4harness; PCRE2 JIT and Bison LALR(1) baselines documented with build flags and version; machine spec recorded | Benchmarks | ❌ |
| **M-GRID-CORPUS** | All 7 engine columns of Grid 2 filled; every engine run against full snobol4corpus crosscheck ladder (106 programs, 12 rungs including beauty.sno); pass/fail counts from actual runs, not from memory | Corpus ladder | ❌ |
| **M-GRID-COMPAT** | Grid 3 feature/compat matrix: all `—` cells replaced with ✅/⚠/🔧/❌ from actual test runs; known CSNOBOL4 vs SPITBOL divergences verified and annotated | Feature/compat | ❌ |
| **M-GRID-REFERENCE** | Grid 4 language reference: every builtin function, keyword, and CLI switch verified per engine; quality rating (✅/⚠/🔧/❌) from actual test runs; edge cases documented inline | Functions/keywords/switches | ❌ |

### Grid milestone dependencies

```
M-GRID-CORPUS   ←  requires all 7 engines buildable and runnable on same machine
M-GRID-BENCH    ←  requires same; also requires PCRE2 JIT and Bison installed
M-GRID-COMPAT   ←  requires M-GRID-CORPUS (corpus must pass before compat details matter)
M-GRID-REFERENCE ← requires M-GRID-COMPAT (coarse compat verified before fine-grained)
```

All four fire → GRIDS.md is publication-ready for community presentation.

---

## README Milestones — Per-Repo Documentation

> These milestones track the state of each repo's public README.
> "Draft" = written but not yet source-verified against actual repo code.
> "Verified" = a dedicated session has scanned the source and corrected every claim.
> Source verification is a separate session per repo — each will consume significant context.

| ID | Repo | Trigger | Status |
|----|------|---------|--------|
| **M-README-PROFILE-DRAFT** | profile/README.md rewritten: correct attributions (Byrd/Proebsting/Emmer/Budne/Koenig), updated test counts, softened benchmark claims, community tone, beauty.sno/compiler.sno bootstrap gates explicit | snobol4ever/.github | ✅ `88e8f17` F-211 |
| **M-README-PROFILE-VERIFIED** | profile/README.md verified against all repo READMEs and source; every number, claim, and attribution confirmed correct | snobol4ever/.github | ❌ |
| **M-README-JVM-DRAFT** | snobol4jvm README written: architecture, pipeline stages, performance numbers, corpus status, build instructions | snobol4jvm | ✅ `e4626cb` |
| **M-README-JVM-VERIFIED** | snobol4jvm README verified against Clojure source; every claim confirmed | snobol4jvm | ✅ `0ee1143` README-4 |
| **M-README-X-DRAFT** | snobol4x README updated: 15×3 frontend/backend matrix, corpus status per backend, build instructions, Byrd Box explanation | snobol4x | ✅ F-211b |
| **M-README-X-VERIFIED** | snobol4x README verified against C source; every claim confirmed | snobol4x | ✅ `5837806` README session |
| **M-README-DOTNET-DRAFT** | snobol4dotnet README: backup Jeff's original as README.jeff.md; new README written with current numbers and structure | snobol4dotnet | ✅ `aeac61e` |
| **M-README-DOTNET-VERIFIED** | snobol4dotnet README verified against C# source; coordinated with Jeff Cooper | snobol4dotnet | ✅ `e8b22cb` README-2 |
| **M-README-PYTHON-DRAFT** | snobol4python README light polish: verify version, test counts, backend description | snobol4python | ✅ `8669c58` README-4 |
| **M-README-CSHARP-DRAFT** | snobol4csharp README light polish: already solid; verify test counts and status | snobol4csharp | ✅ `1f668f5` README-4 |

### README session plan

Each "VERIFIED" milestone is a dedicated session that:
1. Clones the repo fresh
2. Scans every source file relevant to README claims
3. Runs the test suite to confirm counts
4. Corrects any claims that don't match source
5. Commits and pushes

Do not attempt more than one VERIFIED milestone per session — source scanning consumes most of the context window.

Order recommendation: JVM first (empty README, highest urgency), then snobol4x, then dotnet (coordinate with Jeff), then python/csharp (light touch).

---

## GRIDS.md Location Note

GRIDS.md lives in snobol4ever/.github (this repo) at the top level.
It is linked from profile/README.md as `../GRIDS.md` — this resolves correctly
when viewed on GitHub as the org's profile page reads from .github/profile/.
If GitHub does not resolve the relative link correctly, move GRIDS.md to
.github/profile/GRIDS.md and update the link.

---

## Deep Scan + Benchmark Milestone

**M-README-PROFILE-FINAL is on hold** pending M-README-DEEP-SCAN and the M-GRID-* harness runs.

M-README-DEEP-SCAN is the prerequisite: a dedicated session per repo that goes deeper than previous README verification passes — scanning every source file, header, comment, and doc string, and running the benchmark suite for that repo to produce verified, community-reproducible numbers.

| ID | Repo | Trigger | Status |
|----|------|---------|--------|
| **M-DEEP-SCAN-JVM** | snobol4jvm | Full source scan: every `.clj` file, all docstrings, grammar rules, emitter logic, test names; benchmark suite run (`lein bench` or equivalent); all README claims re-verified or corrected against actual source | snobol4jvm | ❌ |
| **M-DEEP-SCAN-X** | snobol4x | Full source scan: all `.c`/`.h` files in frontend/ ir/ backend/ driver/ runtime/; all comments and doc blocks; benchmark suite run (crosscheck + perf harness); ASM/JVM/NET corpus numbers re-verified | snobol4x | ❌ |
| **M-DEEP-SCAN-DOTNET** | snobol4dotnet | Full source scan: all `.cs` files, XML doc comments, test names; benchmark suite run (`dotnet run --project benchmarks`); MSIL emitter steps verified; coordinate with Jeff Cooper | snobol4dotnet | ❌ |
| **M-DEEP-SCAN-PYTHON** | snobol4python | Full source scan: all `.py` and `.c` extension files, docstrings, test names; benchmark run (C extension vs pure-Python timing); v0.5.0 API surface verified | snobol4python | ❌ |
| **M-DEEP-SCAN-CSHARP** | snobol4csharp | Full source scan: all `.cs` files, XML doc comments, test names; benchmark run (pattern match timing on Porter/Treebank/CLAWS5 corpora); delegate-capture API surface verified | snobol4csharp | ❌ |
| **M-README-DEEP-SCAN** | all | All five M-DEEP-SCAN-* milestones fired; every README in the org reflects actual source — line counts, function names, benchmark numbers, known gaps — not summaries from HQ docs | all repos | ❌ |

### What each M-DEEP-SCAN-* session does

Each is a dedicated session (one repo per session — source scanning fills the context window):

1. Clone the repo fresh
2. Walk **every source file** — not just entry points:
   - All `.clj` / `.c` / `.h` / `.cs` / `.py` files
   - All inline comments, docstrings, and XML doc blocks
   - All test file names and test group names
   - All benchmark harness files and their programs
3. Run the benchmark suite and record actual numbers with machine spec (CPU, RAM, OS, date)
4. Run the test suite and confirm counts match README
5. Correct any README claim that doesn't match source
6. Add a **source line count table** (per file, from `wc -l`) — makes the scope of each component concrete
7. Add a **benchmark table** with actual measured numbers, build flags, and machine spec
8. Commit, push, fire the milestone

### Dependency chain

```
M-DEEP-SCAN-JVM    ┐
M-DEEP-SCAN-X      │
M-DEEP-SCAN-DOTNET ├──→  M-README-DEEP-SCAN  ──→  M-README-PROFILE-FINAL
M-DEEP-SCAN-PYTHON │
M-DEEP-SCAN-CSHARP ┘
```

M-README-DEEP-SCAN fires when all five individual scans are done.
M-README-PROFILE-FINAL fires after M-README-DEEP-SCAN AND all M-GRID-* milestones.

---

## Final Integration Milestone — Profile README v2

> **ON HOLD** — blocked on M-README-DEEP-SCAN + M-GRID-* harness runs. Do not attempt until both chains complete.

| ID | Trigger | Status |
|----|---------|--------|
| **M-README-PROFILE-FINAL** | profile/README.md updated a second time, after all of the following have fired: M-README-DEEP-SCAN, M-GRID-BENCH, M-GRID-CORPUS, M-GRID-COMPAT, M-GRID-REFERENCE. At that point every number, every claim, every repo description, every benchmark figure, and every feature statement in the profile README is backed by deep-scanned repo READMEs and actual harness runs. This is the version that goes to the SNOBOL4/SPITBOL community on groups.io and to the broader world. | ❌ |

### What M-README-PROFILE-FINAL incorporates

- Updated test counts from all repos (pulled from their verified READMEs)
- Updated corpus ladder results from M-GRID-CORPUS (real numbers, all 7 engines)
- Benchmark table from M-GRID-BENCH (real numbers, community-verifiable)
- Feature/compat summary from M-GRID-COMPAT and M-GRID-REFERENCE
- Any architectural changes that occurred during the bootstrap sprints
  (beauty.sno status, compiler.sno status, new milestones fired)
- Final tone review for the SNOBOL4/SPITBOL community audience
  (Phil Budne, Andrew Koenig, Mark Emmer, Cheyenne Wills, groups.io)
- Any corrections surfaced during source verification sessions

### Dependency chain (complete picture)

```
clone repos → deep source scan → benchmarks → verified READMEs
     │
     ├─ M-DEEP-SCAN-JVM
     ├─ M-DEEP-SCAN-X
     ├─ M-DEEP-SCAN-DOTNET        ← coordinate with Jeff Cooper
     ├─ M-DEEP-SCAN-PYTHON
     └─ M-DEEP-SCAN-CSHARP
                │
                ▼
     M-README-DEEP-SCAN  ←  all five scans complete
                │
                │    run harness → fill grids
                │    │
                │    ├─ M-GRID-CORPUS
                │    ├─ M-GRID-BENCH
                │    ├─ M-GRID-COMPAT
                │    └─ M-GRID-REFERENCE
                │         │
                └──────────▼
     M-README-PROFILE-FINAL  ←  the version that goes public
                │
                ▼
     post to groups.io SNOBOL4 + SPITBOL lists
     post to Hacker News / broader world
```

This milestone is the gate between internal development and public community presentation.
Do not post to groups.io before it fires.
