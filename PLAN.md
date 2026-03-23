# snobol4ever — HQ

SNOBOL4/SPITBOL compilers targeting JVM, .NET, and native C.
Shared frontends. Multiple backends.
**Team:** Lon Jones Cherryholmes (arch, MSIL), Jeffrey Cooper M.D. (DOTNET), Claude Sonnet 4.6 (TINY co-author, third developer).

---

## ⚡ NOW

Each concurrent session owns exactly one row. Update only your row on every push. Never touch another session's row. `git pull --rebase` before every push — see RULES.md.

Session numbers use per-type prefixes (see RULES.md §SESSION NUMBERS): B=backend, J=JVM, N=NET, F=frontend, D=DOTNET.

**Isolation guarantee:** No session ever works on two same frontends or two same backends. Each session owns one frontend OR one backend. Rebases on common code go smoothly because of this isolation.

**Session trigger key:** Always read PLAN.md first to find the next ❌ milestone for your session type. See RULES.md for full rules per session type.

| Trigger phrase | Session type | Work target |
|----------------|-------------|-------------|
| "playing with MONITOR" | MONITOR SESSION | Next ❌ M-MONITOR-* milestone in order (monitor infrastructure) |
| "playing with fixing bugs" | BUG SESSION | First ❌ M-MON-BUG-* milestone — one bug only |
| "playing with beauty" | BEAUTY SESSION | Next ❌ M-BEAUTY-* milestone in dependency order — write driver, run monitor (CSNOBOL4+ASM 3-way), file M-MON-BUG-* for any divergences found, fire milestone when PASS |
| "playing with README" or "playing with grids" | README SESSION | Next ❌ M-VOL-* then M-FEAT-* then M-README-V2-* in order — run `wc -l`, generate real numbers, fill Grid 7/8 in repo README, commit to that repo |
| "I'm playing with ICON" | ICON SESSION | Next ❌ M-ICON-* milestone in order — see FRONTEND-ICON.md |

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **TINY backend** | `main` B-272 — M-BEAUTY-READWRITE partial: driver+ref created (8/8 CSN PASS); ASM diverges at step 1; root cause = `@var` AT-capture returns empty instead of cursor integer (AT_α macro does not call stmt_set). snobol4x HEAD `c7439cd`. Fix in emit_byrd_asm.c AT_α / snobol4_asm.mac AT_α. See snobol4x PLAN.md §29. | `c7439cd` B-272 | M-BEAUTY-READWRITE |
| **TINY NET** | `net-t2` N-248 — M-T2-NET ✅ 110/110 clean | `425921a` N-248 | M-T2-FULL |
| **TINY JVM** | `jvm-t2` J-213 — M-T2-JVM ✅ 106/106 clean | `8178b5c` J-213 | M-T2-FULL |
| **TINY frontend** | `main` F-225 — M-PROLOG-BUILTINS ✅ rung09 PASS first try (functor/arg/univ/type-tests all correct). rung10 puzzles silent (puzzle_01/06 produce no output vs oracle). Root cause: `;/2` disjunction or `write('...\n')` escape in display. PLAN.md archived 368 lines of README/grid narrative → SESSIONS_ARCHIVE. | `4121ea2` F-225 | M-PROLOG-R10 |
| **DOTNET** | `main` D-164 — Jeff's branch merged: ErrorJump→OnErrorGoto, StartTimer(), DetectConfiguration(), Griswold tests (7), VbLibrary+FSharpOptionLibrary wired, LOAD :F semantics correct; **1903/1903 pass 0 fail on Linux** | `e1e4d9e` D-164 | TBD |
| **README** | `main` — M-README-CSHARP-DRAFT ✅ | `00846d3` snobol4csharp | M-README-DEEP-SCAN (next) |
| **ICON frontend** | `main` I-7 — M-ICON-CORPUS-R2 ✅: rung02_arith_gen 5/5 PASS (range, relational filter, nested add, nested filter, paper mul). Total corpus 15/15. | `54031a5` I-7 | M-ICON-CORPUS-R3 |
| **README v2 sprint** | `main` R-2 — PIVOT: snobol4x M-FEAT-X deferred (partial, 12/20 pass); 20 feature test programs written to snobol4x/test/feat/; M-FEAT-* and M-GRID-REFERENCE MERGED (same work — see below); next: M-FEAT-JVM on snobol4jvm | TBD R-2 | M-FEAT-JVM |

**Invariants (check before any work):**
- TINY: `106/106` ASM corpus (`run_crosscheck_asm_corpus.sh`) · ALL PASS ✅
- DOTNET: `dotnet test` → 1903/1903 (integrate/jeffrey, Linux); 0 failures

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
| Icon | ⏳ | — | — | — | — | — |
| Prolog | ⏳ | ⏳ | — | — | — | — |
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
| **M-MONITOR-IPC-5WAY** | all 5 participants (CSNOBOL4+SPITBOL+ASM+JVM+NET) write trace to per-participant FIFO; `run_monitor.sh` parallel launch + collector; hello PASS all 5; zero stderr/stdout blending — **NOTE: async logger only, not sync-step; M-MONITOR-SYNC adds the barrier protocol** | snobol4x | ✅ `064bb59` B-236 |
| **M-MONITOR-SYNC** | Replace async FIFO design with sync-step barrier protocol: two FIFOs per participant (`<n>.evt` write, `<n>.ack` read); `MON_OPEN(evt,ack)` opens both; `MON_SEND` writes event then **blocks** on ack FIFO read; controller reads one event from all 5, compares, sends `G` (go) or `S` (stop); first divergence stops all 5 immediately with exact diverging event reported; `monitor_ipc_sync.c` + `monitor_sync.py` + `run_monitor_sync.sh` + `inject_traces.py` preamble updated (MON_OPEN now two-arg, reads `MONITOR_ACK_FIFO` env var); hello PASS all 5 sync. **Approach: run monitor → identify divergence → fix → repeat (4-5 cycles) until hello PASS all 5.** | snobol4x | ✅ `2652a51` B-255 |
| **M-SNO2C-FOLD** | sno2c lexer folds identifiers to uppercase at parse time when `-F` (default); `-f` suppresses fold; emitted names are canonical uppercase matching CSNOBOL4/SPITBOL internal representation; `-F`/`-f` switches already accepted (B-254), fold_mode flag wired, lexer fold not yet implemented | snobol4x | ❌ |
| **M-MONITOR-IPC-TIMEOUT** | `monitor_collect.py` per-participant watchdog: FIFO silence > T seconds → TIMEOUT report with last trace event + participant kill; infinite loop detected automatically | snobol4x | ✅ `c6a6544` B-237 |
| **M-MERGE-3WAY** | `asm-backend` + `jvm-backend` + `net-backend` merged into `main` via staged merge-staging branch; all invariants hold after merge; fresh fan-out tags cut (`v-post-merge`); three new per-backend branches from tag | snobol4x | ✅ `425921a` B-239 |
| **M-T2-RUNTIME** | `src/runtime/asm/t2_alloc.c`: `t2_alloc(size)` → mmap RW; `t2_free(ptr,size)` → munmap; `t2_mprotect_rx/rw` toggle; unit test passes | snobol4x | ✅ `ab2254f` B-239 |
| **M-T2-RELOC** | `src/runtime/asm/t2_reloc.c`: `t2_relocate(text,len,delta,table,n)` patches relative jumps + absolute DATA refs; unit test with synthetic table passes | snobol4x | ✅ `b992be8` B-239 |
| **M-T2-EMIT-TABLE** | `emit_byrd_asm.c` emits per-box relocation table as NASM data: `box_N_reloc_table` lists (offset, kind) for every relative ref and DATA ref; null.sno assembles clean | snobol4x | ✅ `06e1bdc` B-239 |
| **M-T2-EMIT-SPLIT** | `emit_byrd_asm.c` splits each named box into separate aligned TEXT+DATA sections; `r12` reserved as DATA-block pointer; all locals `[r12+offset]` not `[rbp-N]`; null.sno + hello.sno assemble and run | snobol4x | ✅ `9968688` B-240 ⚠ 3 regressions to fix |
| **M-MACRO-BOX** | Complete macro coverage: every Byrd box type gets one NASM macro per port (α/β/γ/ω); ARBNO fully macroized (currently raw inline asm); all emitter `saved`/`cursor_save` refs use `bref()` — no bare `.bss` symbol names in call sites; 97/106 invariant holds | snobol4x | ✅ `b606884` B-242 |
| **M-T2-INVOKE** | `emit_byrd_asm.c` emits T2 call-sites: `t2_alloc` + `memcpy TEXT` + `t2_relocate` + `memcpy DATA` + `mov r12,new_data` + `jmp new_text_α`; γ/ω emit `t2_free`; corpus rungs 1–9 still pass | snobol4x | ✅ `1cf8a0a` B-243 |
| **M-T2-RECUR** | Recursive SNOBOL4 functions correct under T2: two simultaneous live DATA blocks, one shared CODE; roman.sno correct; stack-frame bridge (`push rbp`) removed | snobol4x | ✅ `1cf8a0a` B-244 |
| **M-T2-CORPUS** | 106/106 ASM corpus under T2 — 9 known failures fixed by construction; no per-bug patches | snobol4x | ✅ `50a1ad0` B-247 |
| **M-T2-JVM** | JVM backend T2-correct: per-invocation objects on JVM heap (natural); 106/106 JVM corpus clean | snobol4x | ✅ `8178b5c` J-213 |
| **M-T2-NET** | NET backend T2-correct: per-invocation objects on CLR heap; 110/110 NET corpus clean | snobol4x | ✅ `425921a` N-248 |
| **M-T2-FULL** | All three backends T2-correct; `v-post-t2` tag cut; MONITOR sprint resumes from clean base | snobol4x | ✅ `v-post-t2` N-248 |
| **M-MONITOR-4DEMO** | roman + wordcount + treebank pass all 5 participants; claws5 divergence count documented | snobol4x | ❌ |
| **M-MONITOR-CORPUS9** | Run remaining corpus failures through 5-way monitor post-T2; first diverging trace line identifies any residual bugs; ASM corpus at 106/106 confirmed | snobol4x | ✅ `a8d6ca0` B-248 |
| **M-MON-BUG-NET-TIMEOUT** | net_mon_var: replace open-per-call StreamWriter with static-open pattern (mirrors JVM sno_mon_init/sno_mon_fd); NET participant no longer times out on wordcount/treebank/claws5 | snobol4x | ✅ `1e9f361` B-256 |
| **M-MON-BUG-SPL-EMPTY** | SPITBOL trace empty for treebank/claws5: diagnose why monitor_ipc_spitbol.so produces zero events on these programs; SPITBOL participant traces all 5-way demos | snobol4x | ❌ |
| **M-MON-BUG-ASM-WPAT** | ASM VARVAL_fn: SEQ-of-two-patterns variable stringifies as PATTERNPATTERN instead of PATTERN; fix comm_var type reporting so VALUE WPAT = PATTERN matches oracle | snobol4x | ✅ `a4a27ab` B-258 |
| **M-MON-BUG-ASM-DATATYPE-CASE** | ASM DATA type name returned lowercase (e.g. 'cell') instead of uppercase ('CELL'); treebank diverges at step 10 STK='cell' vs oracle 'CELL'; fix datatype() or DATA constructor to uppercase type names | snobol4x | ❌ |
| **M-MON-BUG-JVM-WPAT** | JVM sno_mon_var: pattern datatype not handled in type-name path, emits empty string; fix so VALUE WPAT = PATTERN matches oracle | snobol4x | ❌ |
| **M-BEAUTY-GLOBAL** | `test/beauty/global/driver.sno` exercises all character constants + &ALPHABET extractions from `global.sno`; driver passes 3-way monitor (CSNOBOL4+SPITBOL+ASM) with zero divergence; `run_beauty_subsystem.sh global` exits 0 | snobol4x | ✅ `7e925fd` B-261 |
| **M-BEAUTY-IS** | `test/beauty/is/driver.sno` exercises IsSnobol4()/IsSpitbol() from `is.sno`; 3-way PASS; depends on M-BEAUTY-GLOBAL | snobol4x | ✅ `be215bb` B-262 |
| **M-BEAUTY-FENCE** | `test/beauty/FENCE/driver.sno` exercises FENCE primitive wrapper from `FENCE.sno`; 3-way PASS; depends on M-BEAUTY-IS | snobol4x | ✅ `822c58f` B-261 |
| **M-BEAUTY-IO** | `test/beauty/io/driver.sno` exercises INPUT/OUTPUT OPSYN channels from `io.sno`; 3-way PASS; depends on M-BEAUTY-FENCE | snobol4x | ✅ `a862b01` B-261 |
| **M-BEAUTY-CASE** | `test/beauty/case/driver.sno` exercises UpperCase/LowerCase/ToUpper/ToLower from `case.sno`; 3-way PASS; depends on M-BEAUTY-GLOBAL | snobol4x | ✅ `82d5815` B-263 |
| **M-BEAUTY-ASSIGN** | `test/beauty/assign/driver.sno` exercises assign(name,expression) conditional assignment from `assign.sno`; 3-way PASS | snobol4x | ✅ `9e50b20` B-264 |
| **M-BEAUTY-MATCH** | `test/beauty/match/driver.sno` exercises match()/notmatch() from `match.sno`; 3-way PASS | snobol4x | ✅ `5cf53ff` B-265 |
| **M-BEAUTY-COUNTER** | `test/beauty/counter/driver.sno` exercises Init/Push/Inc/Dec/Top/Pop counter stack from `counter.sno`; 3-way PASS | snobol4x | ✅ `a64ae21` B-266 |
| **M-BEAUTY-STACK** | `test/beauty/stack/driver.sno` exercises Init/Push/Pop/Top value stack from `stack.sno`; 3-way PASS | snobol4x | ✅ `c09c33a` B-267 |
| **M-BEAUTY-TREE** | `test/beauty/tree/driver.sno` exercises DATA tree(t,v,n,c): Append/Prepend/Insert/Remove from `tree.sno`; 3-way PASS; depends on M-BEAUTY-STACK | snobol4x | ✅ `ed72c0f` B-268 |
| **M-BEAUTY-SR** | `test/beauty/ShiftReduce/driver.sno` exercises Shift(t,v)/Reduce(t,n) tree builder from `ShiftReduce.sno`; 3-way PASS; depends on M-BEAUTY-TREE + M-BEAUTY-COUNTER | snobol4x | ✅ `163c952` B-269 |
| **M-BEAUTY-TDUMP** | `test/beauty/TDump/driver.sno` exercises TLump/TDump tree pretty-printer from `TDump.sno`; 3-way PASS; depends on M-BEAUTY-TREE | snobol4x | ✅ `6255a71` B-271 |
| **M-BEAUTY-GEN** | `test/beauty/Gen/driver.sno` exercises Gen/GenLine code generation output from `Gen.sno`; 3-way PASS; depends on M-BEAUTY-IO | snobol4x | ✅ `50313ae` B-271 |
| **M-BEAUTY-QIZE** | `test/beauty/Qize/driver.sno` exercises Qize/DeQize quoting/unquoting from `Qize.sno`; 3-way PASS; depends on M-BEAUTY-GLOBAL | snobol4x | ✅ `33e5f7f` B-271 |
| **M-BEAUTY-READWRITE** | `test/beauty/ReadWrite/driver.sno` exercises ReadLine/WriteLine buffered I/O from `ReadWrite.sno`; 3-way PASS; depends on M-BEAUTY-IO | snobol4x | ❌ |
| **M-BEAUTY-XDUMP** | `test/beauty/XDump/driver.sno` exercises XDump extended variable dump from `XDump.sno`; 3-way PASS; depends on M-BEAUTY-TDUMP | snobol4x | ❌ |
| **M-BEAUTY-SEMANTIC** | `test/beauty/semantic/driver.sno` exercises semantic action helpers from `semantic.sno`; 3-way PASS; depends on M-BEAUTY-SR + M-BEAUTY-GEN | snobol4x | ❌ |
| **M-BEAUTY-OMEGA** | `test/beauty/omega/driver.sno` exercises omega pattern helpers from `omega.sno`; 3-way PASS; depends on M-BEAUTY-SEMANTIC | snobol4x | ❌ |
| **M-BEAUTY-TRACE** | `test/beauty/trace/driver.sno` exercises xTrace control + trace output helpers from `trace.sno`; 3-way PASS | snobol4x | ❌ |
| **M-BEAUTIFY-BOOTSTRAP** | All 19 M-BEAUTY-* fire; `beauty.sno` reads itself via ASM backend; output byte-for-byte identical to CSNOBOL4 oracle AND identical to `beauty.sno` input; fixed point | snobol4x | ❌ |
| **M-MONITOR-GUI** | 🌙 *Dream* — HTML/React monitor GUI: source + trace matrix, diverging cells highlighted | snobol4x | 💭 |

---

### Prolog Frontend — snobol4x (F-session)

Design doc → [FRONTEND-PROLOG.md](FRONTEND-PROLOG.md)

**Key insight (F-214):** Byrd invented the four-port box *for Prolog*. Backtracking is structural — β wires to next clause α, ω signals exhaustion. No continuation state needed. Work in `-pl -asm` through `emit_byrd_asm.c`, not the C emitter.

**Sprint 1 — Foundation (done)**

| ID | Trigger | Status |
|----|---------|--------|
| **M-PROLOG-TERM** | `term.h` + `pl_atom.c` + `pl_unify.c`: TERM_t, atom interning, unify() + trail. | ✅ `d297e0c` F-212 |
| **M-PROLOG-PARSE** | `pl_lex.c` + `pl_parse.c`: tokeniser + parser → ClauseAST. | ✅ `2f1d73a` F-212 |
| **M-PROLOG-LOWER** | `pl_lower.c`: ClauseAST → PL_* IR nodes; EnvLayout computed. | ✅ `90be832` F-212 |
| **M-PROLOG-EMIT-NODES** | `case PL_*` branches in `emit_byrd_asm.c` for all node types. | ✅ `b8312ed` F-212 |

**Sprint 2 — Wire and smoke (one session)**

| ID | Trigger | Status |
|----|---------|--------|
| **M-PROLOG-EMIT-NODES** | New `case PL_*` branches in `emit_byrd_asm.c` for all 10 node types. Acceptance: null clause assembles without error. | ✅ `b8312ed` F-212 |
| **M-PROLOG-HELLO** | `hello :- write('hello'), nl.` compiles via `-pl -asm` and runs correctly. First end-to-end Prolog program. 4D matrix: Prolog×TINY-C ✅ | ✅ `082141e` F-214 |

**Sprint 3 — Deterministic (one session, depends M-PROLOG-HELLO)**

| ID | Trigger | Status |
|----|---------|--------|
| **M-PROLOG-WRITE** | `write/1` and `nl/0` builtins callable from ASM: emit `call pl_write` / `call pl_nl` with correct SysV ABI. Acceptance: `rung01_hello` PASS. | ✅ `45c467f` F-217 |
| **M-PROLOG-FACTS** | Fact lookup with deterministic head unification. `rung02_facts` PASS. One clause, no body, no backtracking. | ✅ `45c467f` F-217 |
| **M-PROLOG-UNIFY** | Compound head unification (`foo(X, bar(X))`). `rung03_unify` PASS. | ✅ `45c467f` F-217 |
| **M-PROLOG-ARITH** | `is/2` + integer comparison in body. `rung04_arith` PASS. | ✅ `45c467f` F-217 |

**Sprint 4 — Backtracking (one session, depends M-PROLOG-ARITH)**

| ID | Trigger | Status |
|----|---------|--------|
| **M-PROLOG-BETA** | β port fires on clause failure: two-clause predicate retries clause 2 when clause 1 head fails. Single small test PASS. This is the first live backtrack via Byrd box β wiring. | ✅ `caa3ed8` F-220 |
| **M-PROLOG-R5** | `member/2` with full backtracking. `rung05_backtrack` PASS: `a b c` printed correctly. | ✅ `caa3ed8` F-220 |
| **M-PROLOG-R6** | `append/3`, `length/2`, `reverse/2`. `rung06_lists` PASS. | ✅ `692a9ff` F-221 |

**Sprint 5 — Cut + recursion (one session)**

| ID | Trigger | Status |
|----|---------|--------|
| **M-PROLOG-CUT** | `!` seals β → ω (FENCE semantics). `differ/2` closed-world negation PASS. `rung07_cut` PASS. | ✅ `692a9ff` F-221 |
| **M-PROLOG-RECUR** | `fibonacci/2`, `factorial/2` via recursion. T2 per-invocation DATA blocks correct. `rung08_recursion` PASS. | ✅ `ff1a492` F-222 |

**Sprint 6 — Builtins + programs**

| ID | Trigger | Status |
|----|---------|--------|
| **M-PROLOG-BUILTINS** | `functor/3`, `arg/3`, `=../2`, type tests. `rung09_builtins` PASS. | ❌ |
| **M-PROLOG-R10** | Lon's word-puzzle solvers (puzzle_01, puzzle_02, puzzle_06). `rung10_programs` PASS. | ❌ |
| **M-PROLOG-CORPUS** | All 10 rungs PASS via `-pl -asm`. 4D matrix Prolog×TINY-x64 complete. | ❌ |

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

### Milestone Table — ICON Frontend (snobol4x)

**Trigger phrase:** `"I'm playing with ICON"` → session type ICON, prefix `I`
**Full spec:** FRONTEND-ICON.md

| ID | Trigger | Depends on | Status |
|----|---------|-----------|--------|
| **M-ICON-ORACLE** | `icont` + `iconx` built from icon-master; `every write(1 to 5);` → `1\n2\n3\n4\n5` confirmed; oracle at `icon-master/bin/icont`+`iconx` | — | ✅ `d364a14` |
| **M-ICON-LEX** | `icon_lex.c` tokenizes all Tier 0 tokens; `icon_lex_test.c` 100% pass | M-ICON-ORACLE | ✅ `d1697ac` I-1 |
| **M-ICON-PARSE-LIT** | Parser produces correct AST for all Proebsting §2 paper examples | M-ICON-LEX | ✅ 21/21 I-2 |
| **M-ICON-EMIT-LIT** | Byrd box for `ICN_INT` matches paper §4.1 exactly | M-ICON-PARSE-LIT | ✅ I-2 |
| **M-ICON-EMIT-TO** | `to` generator; `every write(1 to 5);` → `1..5` | M-ICON-EMIT-LIT | ✅ I-2 |
| **M-ICON-EMIT-ARITH** | `+` `*` `-` `/` binary ops via existing `E_ADD/MPY/SUB/DIV` | M-ICON-EMIT-TO | ✅ I-2 |
| **M-ICON-EMIT-REL** | `<` `>` `=` `~=` relational with goal-directed retry | M-ICON-EMIT-ARITH | ✅ I-2 |
| **M-ICON-EMIT-IF** | `if`/`then`/`else` with indirect goto `gate` temp (paper §4.5) | M-ICON-EMIT-REL | ✅ I-2 |
| **M-ICON-EMIT-EVERY** | `every E do E` drives generator to exhaustion | M-ICON-EMIT-IF | ✅ I-2 |
| **M-ICON-CORPUS-R1** | Rung 1: all paper examples pass; oracle = icon-master icont+iconx | M-ICON-EMIT-EVERY | ✅ 6/6 I-2 `1c299e3` |
| **M-ICON-PROC** | `procedure`/`end`, `local`, `return`, `fail`, call expressions | M-ICON-CORPUS-R1 | ✅ `d736059` I-6 |
| **M-ICON-SUSPEND** | `suspend E` inside procedure = user-defined generator | M-ICON-PROC | ✅ `d736059` I-6 |
| **M-ICON-CORPUS-R2** | Rung 2: arithmetic generators, relational filtering | M-ICON-SUSPEND | ✅ `54031a5` I-7 |
| **M-ICON-CORPUS-R3** | Rung 3: user procedures with return; user-defined generators | M-ICON-CORPUS-R2 | ❌ |
| **M-ICON-STRING** | `ICN_STR`, `\|\|` concat via `CAT2_*` macros | M-ICON-CORPUS-R3 | ❌ |
| **M-ICON-SCAN** | `E ? E` string scanning; explicit cursor threading | M-ICON-STRING | ❌ |
| **M-ICON-CSET** | Cset literals; `upto`→`BREAK`, `many`→`SPAN`, membership→`ANY` | M-ICON-SCAN | ❌ |
| **M-ICON-CORPUS-R4** | Rung 4: string operations and scanning | M-ICON-CSET | ❌ |

---

### Milestone Table — README v2 Grid Sprint

| ID | Trigger | Repo | Depends on | Status |
|----|---------|------|-----------|--------|
| **M-VOL-X** | G-VOLUME table for snobol4x generated and committed | snobol4x | source scan | ✅ `07a34d7`+ README SESSION 2026-03-22 |
| **M-VOL-JVM** | G-VOLUME table for snobol4jvm generated and committed | snobol4jvm | source scan | ✅ README SESSION 2026-03-22 |
| **M-VOL-DOTNET** | G-VOLUME table for snobol4dotnet generated and committed | snobol4dotnet | source scan | ✅ README SESSION 2026-03-22 |
| **M-VOL-PYTHON** | G-VOLUME table for snobol4python generated and committed | snobol4python | source scan | ⏸ DEFERRED |
| **M-VOL-CSHARP** | G-VOLUME table for snobol4csharp generated and committed | snobol4csharp | source scan | ⏸ DEFERRED |
| **M-FEAT-X** | G-FEATURE table for snobol4x written and committed | snobol4x | M-DEEP-SCAN-X | ⏸ DEFERRED — 20 test programs in test/feat/ committed; 12/20 pass; snobol4x gaps: `@` cursor capture, DATATYPE case, named I/O channels, EVAL/CODE, SETEXIT, REAL predicate — resume after JVM/DOTNET |
| **M-FEAT-JVM** | G-FEATURE table for snobol4jvm written and committed | snobol4jvm | M-DEEP-SCAN-JVM | ❌ **NEXT** |
| **M-FEAT-DOTNET** | G-FEATURE table for snobol4dotnet written and committed | snobol4dotnet | M-DEEP-SCAN-DOTNET | ❌ |
| **M-FEAT-PYTHON** | G-FEATURE table for snobol4python written and committed | snobol4python | M-DEEP-SCAN-PYTHON | ⏸ DEFERRED |
| **M-FEAT-CSHARP** | G-FEATURE table for snobol4csharp written and committed | snobol4csharp | M-DEEP-SCAN-CSHARP | ⏸ DEFERRED |
| **M-GRID-STARTUP** | G-STARTUP cold/warm table filled for all 7 engines; machine spec recorded | snobol4ever/.github | all engines buildable | ❌ |
| **M-GRID-OPERATOR** | G-OPERATOR table filled; SNOBOL5 column from docs; all 7 engine columns from runs | snobol4ever/.github | M-GRID-COMPAT | ❌ |
| **M-GRID-SWITCH-FULL** | G-SWITCH table extended with all engine-specific switches beyond the stub in GRIDS.md Grid 4 | snobol4ever/.github | M-DEEP-SCAN-* (all) | ❌ |
| **M-README-V2-X** | snobol4x README v2: G-BENCH, G-STARTUP, G-CORPUS, G-COMPAT, G-BUILTIN, G-KEYWORD, G-SWITCH, G-OPERATOR, G-VOLUME, G-FEATURE — all filled, source-verified | snobol4x | M-FEAT-X, M-VOL-X, M-GRID-* | ❌ |
| **M-README-V2-JVM** | snobol4jvm README v2: same 10 grids, source-verified | snobol4jvm | M-FEAT-JVM, M-VOL-JVM, M-GRID-* | ❌ |
| **M-README-V2-DOTNET** | snobol4dotnet README v2: same 10 grids, source-verified; coordinate Jeff | snobol4dotnet | M-FEAT-DOTNET, M-VOL-DOTNET, M-GRID-* | ❌ |
| **M-README-V2-PYTHON** | snobol4python README v2: same 10 grids (engine columns applicable); source-verified | snobol4python | M-FEAT-PYTHON, M-VOL-PYTHON, M-GRID-* | ⏸ DEFERRED |
| **M-README-V2-CSHARP** | snobol4csharp README v2: same 10 grids (engine columns applicable); source-verified | snobol4csharp | M-FEAT-CSHARP, M-VOL-CSHARP, M-GRID-* | ⏸ DEFERRED |
| **M-PROFILE-V2** | org profile/README.md v2: one-level rollup of all 10 grids across all repos; every number backed by M-README-V2-* | snobol4ever/.github | M-README-V2-* (all five) | ❌ |

---

