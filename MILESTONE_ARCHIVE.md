# Milestone Archive

All completed (✅) milestone rows, moved from PLAN.md dashboard.
Append-only. Do not edit existing entries.

---

## TINY (snobol4x) — Completed

| ID | Trigger | Status |
|----|---------|--------|
| M-SNOC-COMPILES | snoc compiles beauty_core.sno | ✅ |
| M-REBUS | Rebus round-trip diff empty | ✅ `bf86b4b` |
| M-COMPILED-BYRD | sno2c emits Byrd boxes, mock_engine only | ✅ `560c56a` |
| M-CNODE | CNode IR, zero lines >120 chars | ✅ `ac54bd2` |
| M-STACK-TRACE | oracle == compiled stack trace, rung-12 inputs | ✅ session119 |
| M-ASM-HELLO | null.s assembles+links+runs → exit 0 | ✅ session145 |
| M-ASM-LIT | LIT node: lit_hello.s PASS | ✅ session146 |
| M-ASM-SEQ | SEQ/POS/RPOS crosscheck PASS | ✅ session146 |
| M-ASM-ALT | ALT crosscheck PASS | ✅ session147 |
| M-ASM-ARBNO | ARBNO crosscheck PASS | ✅ session147 |
| M-ASM-CHARSET | ANY/NOTANY/SPAN/BREAK PASS | ✅ session147 |
| M-ASM-ASSIGN | $ capture PASS | ✅ session148 |
| M-ASM-NAMED | Named patterns flat labels PASS | ✅ session148 |
| M-ASM-CROSSCHECK | 106/106 via ASM backend | ✅ session151 |
| M-ASM-R1 | hello/ + output/ — 12 tests PASS | ✅ session188 |
| M-ASM-R2 | assign/ — 8 tests PASS | ✅ session188 |
| M-ASM-R3 | concat/ — 6 tests PASS | ✅ session187 |
| M-ASM-R4 | arith/ — 2 tests PASS | ✅ session188 |
| M-ASM-R5 | control/ + control_new/ — goto/:S/:F PASS | ✅ session189 |
| M-ASM-R6 | patterns/ — 20 program-mode pattern tests PASS | ✅ session189 |
| M-ASM-R7 | capture/ — 7 tests PASS | ✅ session190 |
| M-ASM-R8 | strings/ — SIZE/SUBSTR/REPLACE/DUPL PASS | ✅ session192 |
| M-ASM-R9 | keywords/ — IDENT/DIFFER/GT/LT/EQ/DATATYPE PASS | ✅ session193 |
| M-ASM-R10 | functions/ — DEFINE/RETURN/FRETURN/recursion PASS | ✅ session197 |
| M-ASM-R11 | data/ — ARRAY/TABLE/DATA PASS | ✅ session198 |
| M-ASM-RECUR | Recursive SNOBOL4 functions correct via ASM backend | ✅ `266c866` B-204 |
| M-ASM-SAMPLES | roman.sno and wordcount.sno pass via ASM backend | ✅ `266c866` B-204 |
| M-ASM-RUNG8 | rung8/ — REPLACE/SIZE/DUPL 3/3 PASS | ✅ `1d0a983` B-223 |
| M-ASM-RUNG9 | rung9/ — CONVERT/DATATYPE/INTEGER/LGT 5/5 PASS | ✅ `3133497` B-210 |
| M-DROP-MOCK-ENGINE | mock_engine.c removed from ASM link path | ✅ `06df4cb` B-200 |
| M-FLAT-NARY | Parser: E_CONC and E_OR flat n-ary nodes | ⚠ `6495074` F-209 |
| M-EMITTER-NAMING | All four emitters canonical; Greek labels α/β/γ/ω | ✅ `69b52b8` B-222 |
| M-SNOC-LEX | sc_lex.c: all Snocone tokens | ✅ `573575e` session183 |
| M-SNOC-PARSE | sc_parse.c: full stmt grammar | ✅ `5e20058` session184 |
| M-SNOC-LOWER | sc_lower.c: Snocone AST → EXPR_t/STMT_t wired | ✅ `2c71fc1` session185 |
| M-SNOC-ASM-HELLO | `-sc -asm`: OUTPUT='hello' → assembles + runs | ✅ `9148a77` session187 |
| M-SNOC-ASM-CF | DEFINE calling convention via `-sc -asm` | ✅ `0371fad` session188 |
| M-SNOC-ASM-CORPUS | SC corpus 10-rung all PASS via `-sc -asm` | ✅ `d8901b4` session189 |
| M-REORG | Full repo layout: frontend/ ir/ backend/ driver/ runtime/ | ✅ `f3ca7f2` session181 |
| M-ASM-READABLE | Special-char expansion: asm_expand_name() | ✅ `e0371fe` session176 |
| M-ASM-BEAUTIFUL | beauty_prog.s as readable as beauty_full.c | ✅ `7d6add6` session175 |
| M-SC-CORPUS-R1 | hello/output/assign/arith all PASS via `-sc -asm` | ✅ session192 |
| M-MONITOR-SCAFFOLD | test/monitor/ scaffold — CSNOBOL4+ASM single test passes | ✅ `19e26ca` B-227 |
| M-MONITOR-IPC-SO | monitor_ipc.so — MON_OPEN/MON_SEND/MON_CLOSE | ✅ `8bf1c0c` B-229 |
| M-MONITOR-IPC-CSN | inject_traces.py + CSNOBOL4 trace on FIFO | ✅ `6eebdc3` B-229 |
| M-X64-S1 | syslinux.c compiles clean; make bootsbl succeeds | ✅ `88ff40f` B-231 |
| M-X64-S2 | LOAD spl_add end-to-end | ✅ `145773e` B-232 |
| M-X64-S3 | UNLOAD lifecycle; reload; double-unload safe | ✅ `7193a51` B-233 |
| M-X64-S4 | SNOLIB search; STRING ABI; monitor_ipc_spitbol.so | ✅ `4fcb0e1` B-233 |
| M-X64-FULL | S1–S4 fired; SPITBOL confirmed 5-way participant | ✅ `4fcb0e1` B-233 |
| M-MONITOR-IPC-5WAY | 5-way async FIFO monitor; hello PASS all 5 | ✅ `064bb59` B-236 |
| M-MONITOR-SYNC | sync-step barrier protocol; hello PASS all 5 sync | ✅ `2652a51` B-255 |
| M-MONITOR-IPC-TIMEOUT | per-participant watchdog timeout | ✅ `c6a6544` B-237 |
| M-MERGE-3WAY | asm+jvm+net backends merged to main | ✅ `425921a` B-239 |
| M-T2-RUNTIME | t2_alloc/t2_free mmap RW | ✅ `ab2254f` B-239 |
| M-T2-RELOC | t2_relocate patches relative jumps + DATA refs | ✅ `b992be8` B-239 |
| M-T2-EMIT-TABLE | per-box relocation table emitted as NASM data | ✅ `06e1bdc` B-239 |
| M-T2-EMIT-SPLIT | TEXT+DATA sections split; r12 = DATA-block pointer | ✅ `9968688` B-240 |
| M-MACRO-BOX | Complete NASM macro coverage for all Byrd box types | ✅ `b606884` B-242 |
| M-T2-INVOKE | T2 call-sites emitted; t2_alloc+memcpy+relocate+jmp | ✅ `1cf8a0a` B-243 |
| M-T2-RECUR | Recursive functions correct under T2 | ✅ `1cf8a0a` B-244 |
| M-T2-CORPUS | 106/106 ASM corpus under T2 | ✅ `50a1ad0` B-247 |
| M-T2-JVM | JVM backend T2-correct; 106/106 JVM corpus | ✅ `8178b5c` J-213 |
| M-T2-NET | NET backend T2-correct; 110/110 NET corpus | ✅ `425921a` N-248 |
| M-T2-FULL | All three backends T2-correct; v-post-t2 tag cut | ✅ `v-post-t2` N-248 |
| M-MONITOR-CORPUS9 | corpus failures through 5-way monitor; 106/106 confirmed | ✅ `a8d6ca0` B-248 |
| M-MON-BUG-NET-TIMEOUT | NET StreamWriter static-open; no timeout | ✅ `1e9f361` B-256 |
| M-MON-BUG-ASM-WPAT | ASM VARVAL_fn: PATTERNPATTERN → PATTERN | ✅ `a4a27ab` B-258 |
| **M-BEAUTY-OMEGA** | omega.sno — omega patterns correct | SEMANTIC | ✅ B-276 `151a99b` |
| M-BEAUTY-GLOBAL | global.sno 3-way PASS | ✅ `7e925fd` B-261 |
| M-BEAUTY-IS | is.sno 3-way PASS | ✅ `be215bb` B-262 |
| M-BEAUTY-FENCE | FENCE.sno 3-way PASS | ✅ `822c58f` B-261 |
| M-BEAUTY-IO | io.sno 3-way PASS | ✅ `a862b01` B-261 |
| M-BEAUTY-CASE | case.sno 3-way PASS | ✅ `82d5815` B-263 |
| M-BEAUTY-ASSIGN | assign.sno 3-way PASS | ✅ `9e50b20` B-264 |
| M-BEAUTY-MATCH | match.sno 3-way PASS | ✅ `5cf53ff` B-265 |
| M-BEAUTY-COUNTER | counter.sno 3-way PASS | ✅ `a64ae21` B-266 |
| M-BEAUTY-STACK | stack.sno 3-way PASS | ✅ `c09c33a` B-267 |
| M-BEAUTY-TREE | tree.sno 3-way PASS | ✅ `ed72c0f` B-268 |
| M-BEAUTY-SR | ShiftReduce.sno 3-way PASS | ✅ `163c952` B-269 |
| M-BEAUTY-TDUMP | TDump.sno 3-way PASS | ✅ `6255a71` B-271 |
| M-BEAUTY-GEN | Gen.sno 3-way PASS | ✅ `50313ae` B-271 |
| M-BEAUTY-QIZE | Qize.sno 3-way PASS | ✅ `33e5f7f` B-271 |

## JVM backend — Completed

| ID | Trigger | Status |
|----|---------|--------|
| M-JVM-HELLO | null.sno → .class → exit 0 | ✅ session194 |
| M-JVM-LIT | OUTPUT = 'hello' correct | ✅ session195 |
| M-JVM-ASSIGN | Variable assign + arith correct | ✅ session197 |
| M-JVM-GOTO | :S(X)F(Y) branching correct | ✅ J-198 |
| M-JVM-PATTERN | Byrd boxes in JVM | ✅ J-199 |
| M-JVM-CAPTURE | . and $ capture correct | ✅ `62c668f` J-201 |
| M-JVM-R1 | Rungs 1–4 PASS | ✅ `2b1d6a9` J-202 |
| M-JVM-R2 | Rungs 5–7 PASS | ✅ `fa293a1` J-203 |
| M-JVM-R3 | Rungs 8–9 PASS | ✅ `fa293a1` J-203 |
| M-JVM-R4 | Rungs 10–11 PASS | ✅ `876eb4b` J-205 |
| M-JVM-CROSSCHECK | 106/106 corpus PASS via JVM | ✅ `a063ed9` J-208 |
| M-JVM-SAMPLES | roman.sno + wordcount.sno PASS | ✅ `13245e2` J-210 |
| M-JVM-BEAUTY | beauty.sno self-beautifies via JVM | ✅ `b67d0b1` J-212 |

## NET backend — Completed

| ID | Trigger | Status |
|----|---------|--------|
| M-NET-HELLO | sno2c -net null.sno → exit 0 | ✅ session195 |
| M-NET-LIT | OUTPUT = 'hello' correct | ✅ `efc3772` N-197 |
| M-NET-ASSIGN | Variable assign + arith correct | ✅ `02d1f9b` N-206 |
| M-NET-GOTO | :S(X)F(Y) branching correct | ✅ `02d1f9b` N-206 |
| M-NET-PATTERN | Byrd boxes in CIL | ✅ `02d1f9b` N-206 |
| M-NET-CAPTURE | . and $ capture correct | ✅ `590509b` N-202 |
| M-NET-R1 | Rungs 1–4 PASS | ✅ `02d1f9b` N-206 |
| M-NET-R2 | Rungs 5–7 PASS | ✅ `02d1f9b` N-206 |
| M-NET-R3 | Rungs 8–9 PASS | ✅ `02d1f9b` N-206 |
| M-NET-CROSSCHECK | 110/110 corpus PASS via NET | ✅ `fbca6aa` N-208 |
| M-NET-SAMPLES | roman.sno + wordcount.sno PASS | ✅ `2c417d7` N-209 |

## DOTNET — Completed

| ID | Trigger | Status |
|----|---------|--------|
| M-NET-CORPUS-GAPS | 12 corpus [Ignore] tests pass | ✅ `e21e944` session131 |
| M-NET-DELEGATES | Instruction[] → pure Func dispatch | ✅ `baeaa52` |
| M-NET-LOAD-SPITBOL | LOAD/UNLOAD spec-compliant | ✅ `21dceac` |
| M-NET-LOAD-DOTNET | Full .NET extension layer | ✅ `1e9ad33` session140 |
| M-NET-EXT-XNBLK | XNBLK opaque persistent state | ✅ `b821d4d` session145 |
| M-NET-EXT-CREATE | Foreign creates SNO objects | ✅ `6dfae0e` session145 |
| M-NET-VB | VB.NET fixture + tests | ✅ `234f24a` session142 |
| M-NET-XN | SPITBOL x32 C-ABI parity | ✅ `26e2144` session148 |
| M-NET-PERF | Performance profiling; ≥1 measurable win | ✅ `e8a5fec` D-159 |
| M-NET-SPITBOL-SWITCHES | All SPITBOL CLI switches; 26 unit tests PASS | ✅ `8feb139` D-163 |

## Prolog Frontend — Completed (Sprints 1–5)

| ID | Trigger | Status |
|----|---------|--------|
| M-PROLOG-TERM | term.h + pl_atom.c + pl_unify.c | ✅ `d297e0c` F-212 |
| M-PROLOG-PARSE | pl_lex.c + pl_parse.c → ClauseAST | ✅ `2f1d73a` F-212 |
| M-PROLOG-LOWER | pl_lower.c: ClauseAST → PL_* IR | ✅ `90be832` F-212 |
| M-PROLOG-EMIT-NODES | case PL_* branches in emit_byrd_asm.c | ✅ `b8312ed` F-212 |
| M-PROLOG-HELLO | hello :- write('hello'), nl. runs | ✅ `082141e` F-214 |
| M-PROLOG-WRITE | write/1 and nl/0 builtins | ✅ `45c467f` F-217 |
| M-PROLOG-FACTS | Fact lookup deterministic | ✅ `45c467f` F-217 |
| M-PROLOG-UNIFY | Compound head unification | ✅ `45c467f` F-217 |
| M-PROLOG-ARITH | is/2 + integer comparison | ✅ `45c467f` F-217 |
| M-PROLOG-BETA | β port fires on clause failure | ✅ `caa3ed8` F-220 |
| M-PROLOG-R5 | member/2 full backtracking PASS | ✅ `caa3ed8` F-220 |
| M-PROLOG-R6 | append/3, length/2, reverse/2 PASS | ✅ `692a9ff` F-221 |
| M-PROLOG-CUT | ! seals β→ω; rung07 PASS | ✅ `692a9ff` F-221 |
| M-PROLOG-RECUR | fibonacci/2, factorial/2 PASS | ✅ `ff1a492` F-222 |
| M-PROLOG-BUILTINS | functor/3, arg/3, =../2, type tests — rung09 EXACT MATCH | ✅ (confirmed this session) |

## ICON Frontend — Completed (through R2)

| ID | Trigger | Status |
|----|---------|--------|
| M-ICON-ORACLE | icont + iconx built | ✅ `d364a14` |
| M-ICON-LEX | icon_lex.c 100% pass | ✅ `d1697ac` I-1 |
| M-ICON-PARSE-LIT | Parser correct for all §2 examples | ✅ 21/21 I-2 |
| M-ICON-EMIT-LIT | Byrd box for ICN_INT | ✅ I-2 |
| M-ICON-EMIT-TO | `to` generator | ✅ I-2 |
| M-ICON-EMIT-ARITH | +*-/ binary ops | ✅ I-2 |
| M-ICON-EMIT-REL | relational with goal-directed retry | ✅ I-2 |
| M-ICON-EMIT-IF | if/then/else | ✅ I-2 |
| M-ICON-EMIT-EVERY | every E do E | ✅ I-2 |
| M-ICON-CORPUS-R1 | Rung 1: all paper examples 6/6 PASS | ✅ `1c299e3` I-2 |
| M-ICON-PROC | procedure/end, local, return, fail | ✅ `d736059` I-6 |
| M-ICON-SUSPEND | suspend E user-defined generator | ✅ `d736059` I-6 |
| M-ICON-CORPUS-R2 | Rung 2: arith generators, relational 15/15 | ✅ `54031a5` I-7 |

## README v2 — Completed

| ID | Trigger | Status |
|----|---------|--------|
| M-VOL-X | G-VOLUME for snobol4x | ✅ `07a34d7` |
| M-VOL-JVM | G-VOLUME for snobol4jvm | ✅ README SESSION 2026-03-22 |
| M-VOL-DOTNET | G-VOLUME for snobol4dotnet | ✅ README SESSION 2026-03-22 |

| **M-BEAUTY-XDUMP** | XDump extended variable dump 3-way PASS | ✅ B-275 `fa0eee9` |
| **M-BEAUTY-SEMANTIC** | semantic action helpers 3-way PASS | ✅ B-276 `f721492` |

| **M-BEAUTY-TRACE** | xTrace control + trace output 3-way PASS | ✅ B-277 `22e291c` 2026-03-24 |

| **M-PJ-SCAFFOLD** | `prolog_emit_jvm.c` + driver wire; null.pl exits 0 | ✅ PJ-1 2026-03-24 `f7390c6` |
| **M-PJ-HELLO** | hello.pl → JVM → "hello" | ✅ PJ-1 2026-03-24 `f7390c6` |

| **M-BEAUTY-MATCH** | match.sno — match/notmatch correct | ✅ B-283 2026-03-24 |
| **M-BEAUTY-TREE** | tree.sno — tree DATA type correct | ✅ B-283 2026-03-24 |
| **M-BEAUTY-SR** | ShiftReduce.sno — Shift/Reduce correct | ✅ B-283 2026-03-24 |
| **M-BEAUTY-TDUMP** | TDump.sno — tree dump correct | ✅ B-283 2026-03-24 |
| **M-BEAUTY-GEN** | Gen.sno — code generation correct | ✅ B-283 2026-03-24 |
| **M-BEAUTY-QIZE** | Qize.sno — quoting/unquoting correct | ✅ B-283 2026-03-24 |
| **M-BEAUTY-READWRITE** | ReadWrite.sno — buffered I/O correct | ✅ B-283 2026-03-24 |
| **M-BEAUTY-XDUMP** | XDump.sno — extended dump correct | ✅ B-283 2026-03-24 |
| **M-BEAUTY-SEMANTIC** | semantic.sno — semantic actions correct | ✅ B-283 2026-03-24 |
| **M-PJ-BACKTRACK** | Rung 5: `member/2` — β port, all solutions | ✅ PJ-7 `c6a8bda` |
| **M-PJ-LISTS** | Rung 6: `append/3`, `length/2`, `reverse/2` | ✅ PJ-11 `e3c30ab` |
| **M-PJ-RECUR** | Rung 8: `fibonacci/2`, `factorial/2` | ✅ PJ-13 |
| **M-PJ-BUILTINS** | Rung 9: `functor/3`, `arg/3`, `=../2`, type tests | ✅ PJ-13 |
| **M-ICON-CORPUS-R3** | `bab5664` I-11 | Rung 3: user procedures + generators; rbp save/restore fix; 5/5 PASS |
| **M-IJ-CORPUS-R3** | `54c301b` IJ-9 | rung03 suspend generators PASS; named vars→static fields; clear suspend_id on done |
| **M-IJ-STRING** | `9932df5` IJ-9 | ICN_STR + || concat; String static fields; pop/pop2 drain; pre-pass type inference; 5/5 rung04 + t06 bonus fix |
| **M-IJ-SCAN** | `7d68a85` IJ-11 | ij_emit_scan four-port Byrd-box; &subject keyword; icn_subject/icn_pos globals; <clinit> init; ij_expr_is_string ICN_SCAN+&subject; 5/5 rung05 PASS; rung01-04 24/24 clean |
| **M-IJ-CSET** | `369f2bf` IJ-12 | ICN_CSET=ij_emit_str; any/many/upto builtins via static helpers; ICN_AND left-to-right relay drain fix; user-proc guard; 5/5 rung06 PASS; 34/34 total |
| **M-IJ-CORPUS-R4** | `6174c9f` IJ-13 | rung04+05+06=15/15 PASS; ICN_NOT/NEG/SEQ/SNE/SLT/SLE/SGT/SGE added; every-drain fix; 34/34 total |

| **M-PJ-CORPUS-R10** | Rung 10: Lon's puzzle corpus PASS | ✅ PJ-17 `e14bed2` |
| **M-PJ-NEQ** | `\=/2` emit added to `pj_emit_goal` — probe-unify+trail-unwind+inverted-branch; `pj_count_neq` added to locals budget; puzzle_08+09 JVM PASS | ✅ PJ-21 |
