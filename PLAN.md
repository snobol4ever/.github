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
| **TINY backend** | `main` B-258 — M-MON-BUG-ASM-WPAT ✅: stmt_concat pattern SEQ fix (pat_cat); run_monitor_3way.sh (csn+spl+asm); wordcount ASM AGREE; treebank diverges step 10 STK='cell' vs 'CELL' → M-MON-BUG-ASM-DATATYPE-CASE open; **PIVOT: beauty subsystem testing begins (M-BEAUTY-* sprint)** | `a4a27ab` B-258 | M-BEAUTY-GLOBAL (beauty sprint) |
| **TINY NET** | `net-t2` N-248 — M-T2-NET ✅ 110/110 clean | `425921a` N-248 | M-T2-FULL |
| **TINY JVM** | `jvm-t2` J-213 — M-T2-JVM ✅ 106/106 clean | `8178b5c` J-213 | M-T2-FULL |
| **TINY frontend** | `main` F-221 — rung01 ✅ rung02 ✅ rung03 ✅ rung04 ✅ rung05 ✅ rung06 ✅ rung07 ✅. Fixes: (1) cut E_CUT redirects next_clause→omega after _cut=1 so fail/0 exits correctly; (2) if-then-else user-call condition emits pl_<pred>_r call + js else_lbl; (3) sequential body ucalls: only last call uses base-relative sub_cs, earlier calls always fresh (xor edx). M-PROLOG-R6+R7 fire. Open: rung08 sub_cs propagation across sequential recursive calls (fib→factorial); rung09 NASM FAIL (undiagnosed). | `692a9ff` F-221 | M-PROLOG-R8 |
| **DOTNET** | `net-polish` D-163 — clean slate | `8feb139` D-163 | TBD |
| **README** | `main` — M-README-CSHARP-DRAFT ✅ | `00846d3` snobol4csharp | M-README-DEEP-SCAN (next) |
| **ICON frontend** | `main` I-3 — M-ICON-PROC WIP `5cf9295`: param/local fixes done; t01_add_proc PASS; t02_fact+t03_locals FAIL — BSS _val slots global not per-invocation; recursive calls overwrite parent node vals; fix = stack-allocate node temps | `5cf9295` | M-ICON-PROC (fix BSS recursion bug) |
| **README v2 sprint** | `main` R-2 — PIVOT: snobol4x M-FEAT-X deferred (partial, 12/20 pass); 20 feature test programs written to snobol4x/test/feat/; M-FEAT-* and M-GRID-REFERENCE MERGED (same work — see below); next: M-FEAT-JVM on snobol4jvm | TBD R-2 | M-FEAT-JVM |

**Invariants (check before any work):**
- TINY: `106/106` ASM corpus (`run_crosscheck_asm_corpus.sh`) · ALL PASS ✅
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
| **M-BEAUTY-GLOBAL** | `test/beauty/global/driver.sno` exercises all character constants + &ALPHABET extractions from `global.sno`; driver passes 3-way monitor (CSNOBOL4+SPITBOL+ASM) with zero divergence; `run_beauty_subsystem.sh global` exits 0 | snobol4x | ❌ |
| **M-BEAUTY-IS** | `test/beauty/is/driver.sno` exercises IsSnobol4()/IsSpitbol() from `is.sno`; 3-way PASS; depends on M-BEAUTY-GLOBAL | snobol4x | ✅ `be215bb` B-262 |
| **M-BEAUTY-FENCE** | `test/beauty/FENCE/driver.sno` exercises FENCE primitive wrapper from `FENCE.sno`; 3-way PASS; depends on M-BEAUTY-IS | snobol4x | ❌ |
| **M-BEAUTY-IO** | `test/beauty/io/driver.sno` exercises INPUT/OUTPUT OPSYN channels from `io.sno`; 3-way PASS; depends on M-BEAUTY-FENCE | snobol4x | ❌ |
| **M-BEAUTY-CASE** | `test/beauty/case/driver.sno` exercises UpperCase/LowerCase/ToUpper/ToLower from `case.sno`; 3-way PASS; depends on M-BEAUTY-GLOBAL | snobol4x | ❌ |
| **M-BEAUTY-ASSIGN** | `test/beauty/assign/driver.sno` exercises assign(name,expression) conditional assignment from `assign.sno`; 3-way PASS | snobol4x | ❌ |
| **M-BEAUTY-MATCH** | `test/beauty/match/driver.sno` exercises match()/notmatch() from `match.sno`; 3-way PASS | snobol4x | ❌ |
| **M-BEAUTY-COUNTER** | `test/beauty/counter/driver.sno` exercises Init/Push/Inc/Dec/Top/Pop counter stack from `counter.sno`; 3-way PASS | snobol4x | ❌ |
| **M-BEAUTY-STACK** | `test/beauty/stack/driver.sno` exercises Init/Push/Pop/Top value stack from `stack.sno`; 3-way PASS | snobol4x | ❌ |
| **M-BEAUTY-TREE** | `test/beauty/tree/driver.sno` exercises DATA tree(t,v,n,c): Append/Prepend/Insert/Remove from `tree.sno`; 3-way PASS; depends on M-BEAUTY-STACK | snobol4x | ❌ |
| **M-BEAUTY-SR** | `test/beauty/ShiftReduce/driver.sno` exercises Shift(t,v)/Reduce(t,n) tree builder from `ShiftReduce.sno`; 3-way PASS; depends on M-BEAUTY-TREE + M-BEAUTY-COUNTER | snobol4x | ❌ |
| **M-BEAUTY-TDUMP** | `test/beauty/TDump/driver.sno` exercises TLump/TDump tree pretty-printer from `TDump.sno`; 3-way PASS; depends on M-BEAUTY-TREE | snobol4x | ❌ |
| **M-BEAUTY-GEN** | `test/beauty/Gen/driver.sno` exercises Gen/GenLine code generation output from `Gen.sno`; 3-way PASS; depends on M-BEAUTY-IO | snobol4x | ❌ |
| **M-BEAUTY-QIZE** | `test/beauty/Qize/driver.sno` exercises Qize/DeQize quoting/unquoting from `Qize.sno`; 3-way PASS; depends on M-BEAUTY-GLOBAL | snobol4x | ❌ |
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
| **M-PROLOG-RECUR** | `fibonacci/2`, `factorial/2` via recursion. T2 per-invocation DATA blocks correct. `rung08_recursion` PASS. | ❌ |

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
| **M-DEEP-SCAN-PYTHON** | snobol4python | Full source scan: all `.py` and `.c` extension files, docstrings, test names; benchmark run (C extension vs pure-Python timing); v0.5.0 API surface verified | snobol4python | ⏸ DEFERRED |
| **M-DEEP-SCAN-CSHARP** | snobol4csharp | Full source scan: all `.cs` files, XML doc comments, test names; benchmark run (pattern match timing on Porter/Treebank/CLAWS5 corpora); delegate-capture API surface verified | snobol4csharp | ⏸ DEFERRED |
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

---

## README v2 — Grid Sprint (added 2026-03-22)

> **Goal:** Each of the five main repos gets a world-class README that is a one-stop community reference.
> The org profile README gets a rolled-up summary grid.
> Every grid cell is backed by an actual run or source scan — no placeholders in the published version.
>
> This sprint defines **10 new grid types** (some per-repo, some cross-repo) and the milestones to fill them.
> It extends and supersedes the stub work in GRIDS.md Grid 1–4.
>
> **Comparators in every cross-engine grid:** CSNOBOL4 · SPITBOL · SNOBOL5
> (SNOBOL5 added as third external reference — historical completeness)
>
> **Seven engines in all timed/run grids:**
> CSNOBOL4 · SPITBOL · snobol4dotnet · snobol4jvm · snobol4x/ASM · snobol4x/JVM · snobol4x/NET

---

### Grid Taxonomy

| Grid ID | Name | Scope | Lives in |
|---------|------|-------|----------|
| G-BENCH | Benchmark — total time | cross-engine | GRIDS.md + all READMEs |
| G-STARTUP | Benchmark — cold/warm startup | cross-engine | GRIDS.md + all READMEs |
| G-CORPUS | Corpus ladder pass rates | cross-engine | GRIDS.md + all READMEs |
| G-COMPAT | Compatibility / behavior divergences | cross-engine | GRIDS.md + all READMEs |
| G-BUILTIN | Built-in functions (all ~50) | cross-engine | GRIDS.md + all READMEs |
| G-KEYWORD | Program keywords / &-vars (~30) | cross-engine | GRIDS.md + all READMEs |
| G-SWITCH | CLI switches per engine | cross-engine | GRIDS.md + all READMEs |
| G-OPERATOR | Operators (binary, unary, pattern) | cross-engine | GRIDS.md + all READMEs |
| G-VOLUME | Source code volume by category | per-repo | each repo README |
| G-FEATURE | Feature completeness matrix | per-repo | each repo README |

---

### New Milestone Definitions

#### G-STARTUP (extends G-BENCH)

Startup time matters for scripting use. Two columns per engine:
- **cold**: first invocation after OS reboot (page cache cold)
- **warm**: second invocation, same binary, same file

| Program | CSNOBOL4 cold | CSNOBOL4 warm | SPITBOL cold | SPITBOL warm | dotnet cold | dotnet warm | jvm cold | jvm warm | x-asm cold | x-asm warm | x-jvm cold | x-jvm warm | x-net cold | x-net warm |
|---------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| null.sno (zero work) | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| hello.sno (one print) | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| roman.sno (real work) | — | — | — | — | — | — | — | — | — | — | — | — | — | — |

Units: milliseconds. Machine spec recorded at run time.

#### G-OPERATOR

All operators across the three comparison points + seven engines.

Categories:
- **Arithmetic**: `+` `-` `*` `/` `**` (exponent) `REMDR`
- **Relational (numeric)**: `EQ` `NE` `LT` `LE` `GT` `GE`
- **Relational (string)**: `IDENT` `DIFFER` `LGT`
- **Pattern**: concatenation (juxtaposition) `|` (alternation) `~` (complement, SPITBOL) `.` (cond assign) `$` (immediate assign) `@` (cursor)
- **Indirect reference**: `$` prefix (unary indirect)
- **Unary negation**: `-` unary
- **Unevaluated**: `*` prefix (named pattern ref)
- **OPSYN-defined**: user-defined operator aliases

| Operator | CSNOBOL4 | SPITBOL | SNOBOL5 | dotnet | jvm | x-asm | x-jvm | x-net |
|----------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `+` `-` `*` `/` | ✅ | ✅ | ✅ | — | — | — | — | — |
| `**` (exponentiation) | ✅ | ✅ | ✅ | — | — | — | — | — |
| `REMDR` | ✅ | ✅ | ✅ | — | — | — | — | — |
| `EQ NE LT LE GT GE` | ✅ | ✅ | ✅ | — | — | — | — | — |
| `IDENT DIFFER LGT` | ✅ | ✅ | ✅ | — | — | — | — | — |
| Pattern concat (juxtaposition) | ✅ | ✅ | ✅ | — | — | — | — | — |
| `\|` alternation | ✅ | ✅ | ✅ | — | — | — | — | — |
| `~` complement | ❌ | ✅ | — | — | — | — | — | — |
| `.` conditional assign | ✅ | ✅ | ✅ | — | — | — | — | — |
| `$` immediate assign | ✅ | ✅ | ✅ | — | — | — | — | — |
| `@` cursor capture | ✅ | ✅ | ✅ | — | — | — | — | — |
| `$` unary indirect ref | ✅ | ✅ | ✅ | — | — | — | — | — |
| `*` unevaluated / named ref | ✅ | ✅ | ✅ | — | — | — | — | — |
| `-` unary negation | ✅ | ✅ | ✅ | — | — | — | — | — |
| OPSYN user operators | ✅ | ✅ | ⚠ | — | — | — | — | — |

SNOBOL5 column to be filled from SNOBOL5 documentation + source review (not a live run).

#### G-VOLUME (per-repo)

Source code volume by **logical function** — categories must be comparable across all repos
regardless of implementation language (C, Clojure, C#). Do NOT use backend-specific names
like "x64 ASM emitter" or "Clojure IR" — those are implementation details, not logical functions.

**Cross-repo comparable categories (use these exactly in every repo's table):**

| Category | What counts | snobol4x | snobol4jvm | snobol4dotnet |
|----------|-------------|----------|------------|---------------|
| **Parser / lexer** | Source reading, tokenising, parsing to AST | `frontend/snobol4/`, `frontend/snocone/`, `frontend/rebus/` | `grammar.clj`, `emitter.clj`, `snocone*.clj` | `Builder/Lexer.cs`, `Builder/Parser.cs`, `Builder/Snocone*.cs`, `Builder/SourceCode.cs` |
| **Code emitter** | AST/IR → target code (C, MSIL, JVM bytecode, ASM) | `backend/c/`, `backend/x64/`, `backend/jvm/`, `backend/net/` | `transpiler.clj`, `vm.clj`, `jvm_codegen.clj` | `Builder/BuilderEmitMsil.cs`, `Builder/ThreadedCodeCompiler.cs`, `Builder/Builder.cs` |
| **Pattern engine** | Byrd Box match engine, pattern primitives | `runtime/engine/`, `runtime/asm/` | `match.clj`, `match_api.clj`, `primitives.clj`, `patterns.clj`, `engine_frame.clj` | `Runtime/Pattern/`, `Runtime/PatternMatching/` |
| **Runtime / builtins** | Statement execution, built-in functions, variables, I/O, keywords, TRACE | `runtime/snobol4/` | `runtime.clj`, `functions.clj`, `operators.clj`, `invoke.clj`, `env.clj`, `trace.clj`, `errors.clj` | `Runtime/Functions/`, `Runtime/Variable/`, `Runtime/Execution/`, `Runtime/ErrorHandling/` |
| **Driver / CLI** | Entry point, argument parsing, top-level dispatch | `driver/main.c` | `main.clj`, `core.clj` | `Snobol4/MainConsole.cs`, `Builder/CommandLine.cs` |
| **Extensions / plugins** | External function loading, native interop, probe tools | `runtime/mock/` | `src/probe/`, `src/t4probe/` | `CustomFunction/`, `Snobol4.Common/ExternalLibrary/` |
| **Tests** | All test programs, harness scripts, corpus runners | `test/` | `test/` | `TestSnobol4/` |
| **Benchmarks** | Benchmark programs and harness | — | `bench/`, `bench.clj` | `BenchmarkSuite1/`, `BenchmarkSuite2/` |
| **Docs / Markdown** | README, design docs, markdown | repo root `*.md` | `doc/`, `*.md` | `*.md` |
| **Total** | All source (excl. generated artifacts) | | | |

Columns: file count · line count (wc -l) · blank-stripped lines · % of total (src only, no generated artifacts)

#### G-FEATURE (per-repo)

What each repo implements vs. the full SNOBOL4 + SPITBOL feature surface.
Complements G-COMPAT (which is cross-engine) — G-FEATURE is per-repo depth.

Categories (rows):
- Core language (labels, GOTOs, subject/pattern/replacement)
- String operations
- Numeric operations and types
- Pattern primitives (all ~25)
- Capture operators
- Built-in functions (count implemented / total)
- Keywords (count implemented / total)
- DATA / ARRAY / TABLE types
- User-defined functions + recursion
- I/O (INPUT/OUTPUT channels, file I/O)
- LOAD / UNLOAD (external functions)
- EVAL / CODE (dynamic compilation)
- OPSYN
- TRACE / DUMP / debugging
- CLI switches (count implemented / total)
- INCLUDE preprocessing
- Error handling (&ERRLIMIT, SETEXIT)
- Real number support
- Unicode / &ALPHABET beyond ASCII

Rating per row: ✅ complete · ⚠ partial · 🔧 skeleton · ❌ missing · — N/A

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
| **M-ICON-PROC** | `procedure`/`end`, `local`, `return`, `fail`, call expressions | M-ICON-CORPUS-R1 | ❌ |
| **M-ICON-SUSPEND** | `suspend E` inside procedure = user-defined generator | M-ICON-PROC | ❌ |
| **M-ICON-CORPUS-R2** | Rung 2: arithmetic generators, relational filtering | M-ICON-SUSPEND | ❌ |
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

### README v2 Sprint Plan

Each repo README gets its own dedicated session (context window fills fast with source scans).
Order: snobol4x first (most complete, ASM backend proven), then jvm, dotnet (Jeff), then profile README rollup.
**snobol4python and snobol4csharp are DEFERRED** — their M-VOL, M-FEAT, M-DEEP-SCAN, and M-README-V2 milestones are out of scope for this sprint. Profile README v2 will roll up only the three active engines (dotnet, jvm, x/ASM) plus reference columns (CSNOBOL4, SPITBOL, SNOBOL5).

**⚠ M-FEAT-* and M-GRID-REFERENCE are the same work — MERGED**

Both require per-feature verification by running actual programs. M-FEAT-* fills Grid 8 per-repo;
M-GRID-REFERENCE fills Grid 4 cross-engine. Same test programs drive both. Do them together.
When M-FEAT-{repo} fires, fill that repo's Grid 8 column AND the corresponding engine columns in Grid 4.

**Feature verification technique — one test per feature (R-2 session discovery 2026-03-22):**

The correct approach for M-FEAT-* is NOT static source analysis (grep for register_fn).
It is: write one 1-3 line `.sno` program per feature, run it against CSNOBOL4 (oracle) first
to validate the test, then run it against the target engine. Output `PASS` or `FAIL`.
This reveals both presence AND correctness (e.g. DATATYPE returns lowercase in snobol4x — a real compat divergence).

Test programs live in `test/feat/` in each repo:
- `f01_core_labels_goto.sno` … `f20_alphabet_unicode.sno`
- Each outputs exactly `PASS` or `FAIL` (or `PASS (note)` for partial)
- CSNOBOL4 oracle must output `PASS` for every test before it's committed
- Run the full suite: `for f in test/feat/f*.sno; do echo "$f: $(snobol4-asm $f)"; done`
- Results map directly to Grid 8 rows and Grid 4 cells

snobol4x R-2 results (2026-03-22, 12/20 pass):
- ✅ f01 core labels/goto, f02 string ops, f03 numeric, f04 pattern primitives
- ✅ f07 keywords, f08 DATA/ARRAY/TABLE, f09 functions+recursion, f14 OPSYN
- ✅ f15 TRACE/DUMP, f16 CLI switches, f17 INCLUDE (noop), f20 &ALPHABET/256
- ❌ f05 `@` cursor capture (not implemented), f06 DATATYPE case (lowercase vs UPPERCASE)
- ❌ f10/f11 named I/O channels, f12 UNLOAD, f13 EVAL/CODE, f18 SETEXIT, f19 REAL predicate

**Per-repo session checklist (revised):**
1. Clone repo fresh; build engine
2. Run `wc -l` across all source dirs → G-VOLUME table (if not already done)
3. Copy `test/feat/` programs from snobol4x; adapt runner for this engine
4. Run all 20 against oracle (CSNOBOL4) to confirm tests valid
5. Run all 20 against target engine; record PASS/FAIL per feature
6. Fill Grid 8 column for this repo; fill Grid 4 engine columns
7. Run corpus + harness → fill G-CORPUS, G-BENCH for this engine
8. Commit test/feat/ + README with all grids; fire M-FEAT-* and partial M-GRID-REFERENCE
9. Note every G-COMPAT divergence (e.g. DATATYPE case) in Grid 3

**Profile README session (last):**
1. Pull from all five M-README-V2-* READMEs
2. Collapse each 10-grid into a summary row per repo
3. Write a single community-facing narrative intro
4. Commit; fire M-PROFILE-V2

---

### Dependency chain — README v2

```
per-repo source scans (M-DEEP-SCAN-*)
    │
    ├─ M-VOL-{X,JVM,DOTNET,PYTHON,CSHARP}    (source counting — fast, one session each)
    ├─ M-FEAT-{X,JVM,DOTNET,PYTHON,CSHARP}   (feature table — from source, no runs)
    │
    └─ harness runs (snobol4harness)
           │
           ├─ M-GRID-CORPUS     (106-program ladder)
           ├─ M-GRID-BENCH      (total-time benchmarks)
           ├─ M-GRID-STARTUP    (cold/warm startup — NEW)
           ├─ M-GRID-COMPAT     (behavior divergences)
           ├─ M-GRID-REFERENCE  (builtins/keywords/switches)
           └─ M-GRID-OPERATOR   (operator grid — NEW)
                    │
                    ▼
    M-GRID-SWITCH-FULL  (CLI switch grid — NEW, from source + runs)
                    │
                    ▼
    M-README-V2-{X,JVM,DOTNET,PYTHON,CSHARP}  (one session each)
                    │
                    ▼
           M-PROFILE-V2   ←  community one-stop shop
                    │
                    ▼
     post to groups.io SNOBOL4 + SPITBOL lists
```

Three new grids (G-STARTUP, G-OPERATOR, G-SWITCH-FULL) plus five new per-repo grids (G-VOLUME, G-FEATURE)
bring the total from 4 → 10 grids per repo and 6 → 9 cross-engine grids in GRIDS.md.

## §21 — Session B-264 (2026-03-23): M-BEAUTY-CASE — 4 fixes, 1 open (ANY_α_SLOT)

### Fixes applied

| # | Bug | File | Fix |
|---|-----|------|-----|
| 1 | `snobol4-asm` missing `-I"$INC"` → -INCLUDE fails silently | `snobol4-asm` | Add `-I"$INC"` to sno2c call |
| 2 | `LOAD_NULVCL` stores DT_S=1 not DT_SNUL=0; doesn't set rax/rdx | `snobol4_asm.mac` | `xor eax/edx` then store |
| 3 | `LOAD_NULVCL32` same bug | `snobol4_asm.mac` | same |
| 4 | `ANY(&UCASE &LCASE)` → E_CONC arg → emitted as `ANY("")` | `emit_byrd_asm.c` | emit_expr into temp .bss slot |

### §21.1 — Remaining open bug: ANY_α_SLOT needed

After fix 4, the emitter generates:
```nasm
any_expr_tmp_2_t resq 1   ; .bss: type field of evaluated charset DESCR_t
any_expr_tmp_2_p resq 1   ; .bss: ptr field
mov [rel any_expr_tmp_2_t], rax  ; store charset type at match-setup time
mov [rel any_expr_tmp_2_p], rdx  ; store charset ptr
; ... then ANY_α_VAR any_expr_tmp_2, ...
```

But `ANY_α_VAR` expands to `ANY_α_VAR varlab, ...` which calls `stmt_get(varlab)` → `NV_GET_fn("any_expr_tmp_2")`. That name is not in the SNOBOL4 variable table — it's just a .bss label. So charset lookup fails and ANY still doesn't match.

**Fix needed in B-265:**

Add `ANY_α_SLOT` macro to `snobol4_asm.mac`:
```nasm
; ANY_α_SLOT typelab, ptrlab, saved, cursor, subj, subj_len, gamma, omega
; Reads charset directly from .bss type+ptr labels (no NV_GET_fn).
%macro ANY_α_SLOT 8
    mov     rax, [rel %1]     ; type
    mov     rdx, [rel %2]     ; ptr
    ; build a DESCR_t on stack and call the engine's any_match_descr helper
    ; (or inline the charset-string extraction logic)
    ...
%endmacro
```

And in `emit_byrd_asm.c` ANY expr branch, emit `ANY_α_SLOT tmplab_t, tmplab_p, ...` instead of `ANY_α_VAR tmplab`.

### §21.2 — Next session action (B-265)

1. `bash setup.sh`
2. Add `ANY_α_SLOT` macro to `snobol4_asm.mac` that reads charset from two .bss labels directly
3. Update `emit_byrd_asm.c` ANY expr branch: emit `ANY_α_SLOT` instead of `ANY_α_VAR`
4. Test: `INC=demo/inc ./snobol4-asm /tmp/icase_test.sno` → must print PATTERN
5. Run 3-way monitor: `INC=demo/inc bash test/beauty/run_beauty_subsystem.sh case` → 9/9 PASS
6. Confirm `bash test/crosscheck/run_crosscheck_asm_corpus.sh` → 106/106
7. Commit `B-265: M-BEAUTY-CASE ✅`, update PLAN.md dashboard + TINY.md, push both repos

