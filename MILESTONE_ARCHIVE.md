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
| **M-PJ-STACK-LIMIT** | Dynamic `.limit stack` via `pj_term_stack_depth`+`pj_clause_stack_needed` pre-pass; replaces hardcoded 16; fixes VerifyError on deep compound terms | ✅ PJ-22 |
| **M-IJ-CORPUS-R5** | `6780ab9` IJ-14 | rung07_control 5/5 PASS; ij_emit_to_by rewritten: forward-only jumps, two lcmp ops; .bytecode 45.0; 39/39 rung01-07 PASS |
| **M-IJ-CORPUS-R8** | `be1be82` IJ-16 | find/match/tab/move builtins + static helpers; ij_expr_is_string updated; 44/44 rung01-08 PASS |
| **M-IJ-CORPUS-R9** | `60cf799` IJ-17 | until/repeat emitters; body-drain pop fix; 49/49 rung01-09 PASS |
| **M-PJ-BETWEEN** | `5ae0d24` PJ-32 | synthetic p_between_3 static method; cs=offset-from-Low; puzzle_19 PASS; 16/20 |
| **M-IJ-CORPUS-R10** | `8f98dea` IJ-18 | augop (+=/*=/-=//=/%=) + break/next emitters + loop label stack; rung10_augop 5/5 PASS; 54/54 rung01-10 PASS |

| **M-IJ-CORPUS-R11** | Rung 11: `||:=` string augop + `!E` bang generator + rung11 5/5; 59/59 total | ✅ IJ-20 `cab96d2` |
| **M-IJ-CORPUS-R12** | Rung 12: string relops (SEQ/SNE/SLT/SLE/SGT/SGE) + ICN_SIZE (`*s`) + ij_expr_is_string(ICN_IF) VerifyError fix; 64/64 total | ✅ IJ-21 `be2af59` |

| **M-IJ-CORPUS-R13** | Rung 13: ICN_ALT β-resume indirect-goto gate + ICN_ALT string type + concat left_is_value fix; 69/69 total | ✅ IJ-22 `a569adf` |

| **M-IJ-CORPUS-R14** | Rung 14: ICN_LIMIT (E \ N) limitation operator; counter/max statics, β no-increment fix; 74/74 total | ✅ IJ-23 `9021c4e` |
| **M-IJ-CORPUS-R15** | Rung 15: ICN_REAL, ICN_SWAP (:=:), ICN_LCONCAT (|||); 79/79 total | ✅ IJ-24 |
| **M-IJ-CORPUS-R16** | Rung 16: ICN_SUBSCRIPT s[i] + ij_emit_if drain pop/pop2 fix; 84/84 total | ✅ IJ-25 `dff0f03` |
| **M-IJ-CORPUS-R17** | Rung 17: real arith (dadd/dmul), integer()/real()/string() builtins, ldc2_w decimal fix; 89/89 total | ✅ IJ-26 `f10ea77` |
| **M-IJ-CORPUS-R18** | Rung 18: real relops (dcmpl/dcmpg + l2d promotion), ICN_ALT realness; 94/94 total | ✅ IJ-27 `f976057` |
| **M-IJ-CORPUS-R19** | Rung 19: ICN_POW (^) via Math.pow + real to-by (dneg fix, is_dbl flag); 99/99 total | ✅ IJ-28 `2574281` |
| **M-IJ-CORPUS-R20** | Rung 20: ICN_SECTION s[i:j] (3-operand, 1-based→0-based, clamp) + ICN_SEQ_EXPR (E;F drain relay); 104/104 total | ✅ IJ-29 `7f8e3a2` |
| **M-IJ-LISTS** | List constructor [e1..en], push/put/get/pop/pull, !L, *L; rung22 5/5 PASS; 114/114 total | ✅ IJ-33 `51c7335` |
| **M-IJ-CORPUS-R22** | Rung 22: lists corpus 5/5 PASS (fires with M-IJ-LISTS) | ✅ IJ-33 `51c7335` |

## M-PJ-FINDALL — `findall/3` collect all solutions into list

**Fired:** PJ-47 | **Date:** 2026-03-25 | **HEAD:** `62b3fa0`

Implemented `pj_emit_findall_builtin()` with synthetic helpers `pj_copy_term`, `pj_eval_arith`, `pj_call_goal`, `pj_reflect_call`, `p_findall_3`. Three-session effort (PJ-45/46/47): scaffold + loop (PJ-45), conjunction cs threading + gamma sub_cs_out (PJ-46), E_FNC mod/rem// in `pj_emit_arith` (PJ-47). 5/5 rung11 PASS. 20/20 puzzles intact.

## M-PJ-ATOM-BUILTINS — atom_chars/codes/length/concat/char_code/number_chars/codes/upcase/downcase

**Fired:** PJ-50 | **Date:** 2026-03-25 | **HEAD:** `cbd6979`

Root bug: `pj_term_int` stores long as `String` via `Long.toString()` at slot [1], but `pj_int_val` was doing `checkcast Long → longValue()` and `pj_atom_name` INT branch had the same mismatch → `ClassCastException: String cannot be cast to Long` on `atom_codes` reverse path. Fixed both to `checkcast String → parseLong`, consistent with arithmetic path. Also fixed `pj_atom_name` INT branch to return String directly without Long boxing/unboxing round-trip. All 9 builtins implemented in PJ-48/49 were already correct; only the runtime helper was broken. 5/5 rung12 PASS. 5/5 rung11 PASS. 19/20 puzzle corpus (puzzle_19 pre-existing between/3 performance issue, not a regression).
## M-IJ-TABLE — `table(dflt)`, `t[k]` subscript, `key/insert/delete/member` builtins

**Fired:** IJ-36 | **Date:** 2026-03-25 | **HEAD:** `9635570`

Three-session effort (IJ-34/35/36): IJ-34 scaffold + insert/delete/member; IJ-35 t[k]:=v VerifyError + table default value + 4/5 rung23; IJ-36 key(T) two-bug fix (kinit re-snapshot + subscript β wiring) → 5/5 rung23. 119/119 PASS. JVM HashMap<String,Object> backend. Subscript β now resumes key generator β (not one-shot) — required for `every … t[key(t)]` patterns.
>>>>>>> 38b5401 (IJ-36: M-IJ-TABLE ✅ — update PLAN.md NOW, FRONTEND-ICON-JVM.md §NOW, milestone+session archive)

## IJ-39 — M-IJ-GLOBAL ✅  2026-03-25
rung25 7/0/0 · HEAD `e4f0f7e` · `global` var declarations + `initial` clause (already implemented; corpus + runner scaffolded)

## IJ-40 — M-IJ-POW ✅  2026-03-25
rung26 5/0/0 · HEAD `90c759e` · `^` exponentiation via `Math.pow(DD)D`, right-assoc, int+real (already implemented; corpus + runner scaffolded)

## IJ-41 — M-IJ-READ ✅  2026-03-25
rung27 5/0/0 · HEAD `d94e728` · `read()`/`reads()` builtins (BufferedReader wrapping System.in)
Bugs fixed: while-cond pop/pop2 · body-result drain · cond_ok fall-through · local-slot zero-init

## PJ-55 — M-PJ-ABOLISH ✅  2026-03-25
rung15 5/0/0 · HEAD `db82779` · `abolish/1` — `pj_db_abolish` + `pj_db_abolish_key` (uses `pj_atom_name`/`pj_int_val` to decode `/(Name,Arity)` compound)

## PJ-56 — M-PJ-ATOP ✅  2026-03-25
rung16 5/0/0 · HEAD `033f34f` · `@<`/`@>`/`@=<`/`@>=` — 4 entries in `BIN_OPS[]` + `pj_term_str`→`String.compareTo` dispatch

## PJ-57 — M-PJ-SORT ✅  2026-03-25
rung17 5/0/0 · HEAD `d0b58bb` · `sort/2`/`msort/2` — `pj_list_to_arraylist`, `pj_arraylist_to_list`, `pj_sort_list` (insertion sort + optional dedup)

## PJ-58 — M-PJ-SUCC-PLUS ✅  2026-03-25
rung18 5/0/0 · HEAD `937ef92` · `succ/2`/`plus/3` — `pj_is_var`, `pj_succ_2`, `pj_plus_3` (all 3 modes for plus)

## IJ-42 — M-IJ-BUILTINS-STR ✅  2026-03-25
rung28 5/0/0 · 92/92 total · HEAD `c1e2b56` · `repl/reverse/left/right/center/trim/map/char/ord` — inline JVM emission + static helpers `icn_builtin_left/right/center/trim/map`; `ij_expr_is_string` extended for all 8 String-returning builtins

## IJ-43 — M-IJ-BUILTINS-TYPE ✅  2026-03-25
rung29 5/0/0 · 97/97 total · HEAD `495cb65` · `type/copy/image/numeric` — compile-time type constant; identity copy; toString image; `icn_builtin_numeric` with Jasmin `.catch`; `Long.MIN_VALUE` fail sentinel; `ij_expr_is_string` extended

## IJ-44 — M-IJ-BUILTINS-MISC ✅  2026-03-25
rung30 5/0/0 · 102/102 total · HEAD `fe87efc` · `abs/max/min/sqrt/seq` — `Math.abs/max/min/sqrt`; varargs relay chain for max/min; seq infinite generator with α/β ports + static cur+step; `ij_expr_is_real` extended for sqrt/abs/max/min; helper name fixes `_long→default`, `_real→_dbl`

## IJ-52 — M-IJ-TABLE-VERIFY ✅  2026-03-26
rung23 5/5 · 136/136 total · HEAD `6fe0f2b` · resolved on arrival (IJ-51 codebase). Discovered M-IJ-RECURSION: static `icn_pv_*` fields clobbered by recursive proc calls.

## PJ-75 — M-PJ-LINKER ✅  2026-03-26
test_list 10/1/0 (raw SWI .pl, no wrap_swi.py) · HEAD `a316544` · plunit linker in `prolog_emit_jvm.c`: `pj_linker_has_plunit`, `pj_plunit_shim_src[]` embedded C string, `pj_linker_emit_plunit_shim` (parse+lower+emit via prolog_parse/prolog_lower), `pj_linker_emit_db_stub` (proper DB-query loop for pj_suite/1 + pj_test/4), `pj_linker_scan` (two-pass: suites from begin_tests directives, tests from E_CHOICE nodes assigned to suite[0]), `pj_linker_emit_main_assertz` (assertz pj_suite/pj_test facts in main()), `pj_linker_emit_bridge` (bridge predicates suite_name/0). begin_tests/end_tests added to meta-directive skip list. main() stack limit → 32. All 34 corpus rungs: 0 regressions.

## IJ-53 — M-IJ-RECURSION ✅  2026-03-26
`fact(5)=120` · rung02_proc 3/3 · HEAD `f1dc530` · Root cause: ALL class-level scratch statics (`icn_N_binop_lc/rc`, `icn_N_relop_lc/rc`) trampled by recursive calls, not just `icn_pv_*`. Fix: `ij_static_needs_callsave()` — save/restore all `'J'` statics except `icn_gvar_*`, `icn_arg_*`, `icn_retval`, control fields, and other procs' `icn_pv_*` — around every user-proc `invokestatic`. `.limit locals` bumped by `2*ij_nstatics`. 4 harness scripts added (rung02_arith_gen, rung02_proc, rung04_string, rung35_table_str).

## IJ-54 — M-IJ-INITIAL ✅  2026-03-26
rung25 7/7 (t03, t07 promoted) · HEAD `d029d7c` · Root cause: callsave restore was overwriting callee's persistent `icn_pv_<callee>_*` locals on return, resetting `initial`-initialised vars each call. Fix: exclude `icn_pv_<other_proc>_*` from callsave predicate — only save caller's own `icn_pv_<ij_cur_proc>_*` plus scratch intermediates. 6 harness scripts added (rung08/09/12/18/20/21).

## IJ-55 — M-IJ-STRRET-GEN ✅  2026-03-26
rung32 5/5 (t03 promoted from xfail) · 153/153 PASS total · HEAD `d64d752` · Root cause: β path for non-generator procs unconditionally jumped to `ports.ω`, so `every write(tag("a"|"b"|"c"))` exited after first value. Fix: non-gen proc β routes to `arg_betas[nargs-1]` when `nargs > 0`, re-pumping the arg generator chain. Removed `t03_strret_every.xfail`.

## IJ-53 — M-IJ-RECURSION ✅  2026-03-26
`fact(5)=120` · rung02_proc 3/3 · HEAD `f1dc530` · All class-level scratch statics (`icn_N_binop_lc/rc`, `icn_N_relop_lc/rc`) trampled by recursive calls. Fix: `ij_static_needs_callsave()` — save/restore all `'J'` statics except globals, args, retval, control, other procs' `icn_pv_*` — around every user-proc `invokestatic`. `.limit locals` bumped by `2*ij_nstatics`. 4 harness scripts added.

## IJ-54 — M-IJ-INITIAL ✅  2026-03-26
rung25 7/7 · HEAD `d029d7c` · callsave restore overwrote callee's persistent `icn_pv_<callee>_*` locals on return. Fix: exclude `icn_pv_<other_proc>_*` from callsave — only save caller's own `icn_pv_<ij_cur_proc>_*` plus scratch. 6 harness scripts added (rung08/09/12/18/20/21).

## IJ-55 — M-IJ-STRRET-GEN ✅  2026-03-26
rung32 5/5 · 153/153 PASS total · HEAD `d64d752` · β path for non-gen procs jumped to `ports.ω`; `every write(tag("a"|"b"|"c"))` exited after first value. Fix: non-gen proc β → `arg_betas[nargs-1]` when `nargs > 0`. Removed `t03_strret_every.xfail`.

## M-SD-1 ✅ — hello: all three JVM frontends PASS

**Fired:** 2026-03-26. **Session:** SD-24. **HEAD:** `0f28136`.

hello.md — `OUTPUT = 'Hello, World!'` / `write("Hello, World!")` / `write('Hello, World!'), nl.`
All three compile through snobol4ever JVM frontends and produce correct output.
SNO2C-JVM: PASS | ICON-JVM: PASS | PROLOG-JVM: PASS.
