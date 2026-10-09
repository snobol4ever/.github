# The SCRIP_C2BB_TRACE reading over the SNOBOL4 rungs and packages, and the Icon, Pascal and Prolog rungs (coo, 2026-10-09)

For the cfo's rank-0 row gc-rt-c-c-to-bb-entries-leave-no-emitted-code-... (asked 10-07, answered here). A MEASUREMENT: no progress row, no score row.

**Tree.** SCRIP 62a0d4ff8 (a clean build of origin in a scratch worktree), corpus 0b4153e33, RT_DIAG on (the default). Run 11:30-11:56 CDT, load 5-11 on 16 cores, single-threaded.

**Method.** rt_c2bb_hit appends one line per box entered from C to the file SCRIP_C2BB_TRACE names. Every entry and mode got its own file. The harness containers (SNOBOL4 rungs 1980, aisnobol 8, Icon rungs 904, Pascal rungs 252, Prolog rungs 563) ran through corpus_suite_harness.py run with a local hook, S4E_ENTRY_TRACE_DIR. Gimpel's 145 drivers, and the runner-only packages (csnobol4_suite 131, dotnet 14, snoflake 180, testpgms 8, spitbol_x32 21, spitbol_x64 36), ran directly, m3 and m4, in a scratch copy of each package. csnobol4_suite's container refused: its ALL.mask names diag1, which the container no longer holds; its board grades the loose pairs. util_c2bb_trace_census.py counted each directory by mark (the site column). An entry that entered nothing from C leaves no file.

## By mark, all suites

```
mark                     hits entries  suites (suite:entries)                           first witness
apply.open              10888      24  rungs:12 aisnobol:3 csnobol4:3 gimpel:3 snoflake rungs apply_omitted_args_1 m3
callee.open            280260      18  rungs:2 aisnobol:4 gimpel:11 snoflake:1          rungs user_function_6 m3
dtx.open                  190      10  rungs:6 aisnobol:1 csnobol4:1 gimpel:1 testpgms: rungs eval_defer_1 m3
named.tiny              13852       9  rungs:4 aisnobol:2 csnobol4:1 gimpel:1 testpgms: rungs user_function_len_datatype_replace_branch_1 m3
chain.eval.conve          232       8  rungs:3 aisnobol:2 gimpel:3                      rungs convert_expression_is_deferred_and_reads_expression_1 m3
chain.eval.v              232       8  rungs:3 aisnobol:2 gimpel:3                      rungs convert_expression_is_deferred_and_reads_expression_1 m3
descr.tiny              25448       7  rungs:3 aisnobol:2 snoflake:2                    rungs ladder__rung22_access_calls_a_program_defined_trace_function_with_the_name_and_the_tag m3
gen_h.coro_resume          54       5  icon_rungs:5                                     icon_rungs ladder__rung29_builtins_variable_by_a_runtime_name_reaches_locals_params_and_statics m3
gen_h.resume_frame         54       5  icon_rungs:5                                     icon_rungs ladder__rung29_builtins_variable_by_a_runtime_name_reaches_locals_params_and_statics m3
gen_h.call_value           30       5  icon_rungs:5                                     icon_rungs ladder__rung29_builtins_variable_by_a_runtime_name_reaches_locals_params_and_statics m3
gen_h.coro                 30       5  icon_rungs:5                                     icon_rungs ladder__rung29_builtins_variable_by_a_runtime_name_reaches_locals_params_and_statics m3
genp.spine.n2              30       5  icon_rungs:5                                     icon_rungs ladder__rung29_builtins_variable_by_a_runtime_name_reaches_locals_params_and_statics m3
descr.enter.thunk           2       1  snoflake:1                                       snoflake pattern-assignment-targets m3
```

**No trace file at all:** dotnet, spitbol_x32 and spitbol_x64 (the programs run and answer; none enters a box from C), Pascal rungs, and Prolog rungs (gen_h.pl_goal never fires).

**Marks the runtime can emit that fired nowhere in this population:** c_lex.enter, descr.enter.lex, descr.enter.dyn.named, lex.open, via.dtx, chain.goto, chain.eval.unguarded, chain.eval.guarded, gen_h.enter, gen_h.pl_goal.

## By mark and name, with the C caller pair (top lines per suite)

### rungs
```
mark                                                 hits  entries     m3     m4  witness (suite entry mode)
apply.open/ADD1                                      1006        3      3      3  rungs benchmark_indirect_dispatch m3
         503  ? <- ?
         503  ? <- __libc_start_main
apply.open/EQ                                          12        3      3      3  rungs apply_omitted_args_1 m3
           6  ? <- ?
           6  ? <- __libc_start_main
dtx.open/EXPR$0                                         8        4      4      4  rungs eval_defer_1 m3
           8  rt_eval_open <- ?
apply.open/SIZE                                         6        2      2      2  rungs apply_omitted_args_1 m3
           3  ? <- ?
           3  ? <- __libc_start_main
apply.open/WIDEN                                        6        1      1      1  rungs user_function_apply_trim_replace_1 m3
           3  ? <- ?
           3  ? <- __libc_start_main
chain.eval.conve/?                                      6        3      3      3  rungs convert_expression_is_deferred_and_reads_expression_1 m3
           4  ? <- ?
           2  ? <- rt_defer_open_cell
chain.eval.v/?                                          6        3      3      3  rungs convert_expression_is_deferred_and_reads_expression_1 m3
           4  ? <- ?
           2  ? <- rt_defer_open_cell
descr.tiny/MYFUN                                        6        1      1      1  rungs user_function_keyword_11 m3
           6  rt_call_proc_descr <- ?
named.tiny/OPSYN~                                      6        1      1      1  rungs user_function_len_datatype_replace_branch_1 m3
           6  _usercall_hook <- ?
apply.open/CHAR                                         4        1      1      1  rungs user_function_apply_trim_replace_1 m3
           2  ? <- ?
           2  ? <- __libc_start_main
apply.open/DUPL                                         4        1      1      1  rungs apply_omitted_args_1 m3
           2  ? <- ?
           2  ? <- __libc_start_main
apply.open/LGT                                          4        1      1      1  rungs apply_omitted_args_1 m3
           2  ? <- ?
           2  ? <- __libc_start_main
apply.open/LT                                           4        1      1      1  rungs apply_omitted_args_1 m3
           2  ? <- ?
           2  ? <- __libc_start_main
apply.open/TRFUN                                        4        1      1      1  rungs user_function_indirect_keyword_1 m3
           2  ? <- ?
           2  ? <- __libc_start_main
```
### aisnobol
```
mark                                                 hits  entries     m3     m4  witness (suite entry mode)
callee.open/ATOM                                   112404        2      2      2  aisnobol SIR m3
      112404  ? <- ?
callee.open/NUMBER                                  50014        1      1      1  aisnobol TEST m3
       50014  ? <- ?
callee.open/NULL                                    46294        2      2      2  aisnobol SIR m3
       46294  ? <- ?
callee.open/DFLOAT                                  22406        1      1      1  aisnobol TEST m3
       22406  ? <- ?
descr.tiny/LIST                                     21952        2      2      2  aisnobol SIR m3
       21952  rt_call_proc_descr <- rt_call_named_proc
named.tiny/OPSYNPOP                                11873        2      0      2  aisnobol SIR m4
       11873  _usercall_hook <- ?
callee.open/DIV                                     11036        1      1      1  aisnobol TEST m3
       11036  ? <- ?
callee.open/EQU                                      6620        2      2      2  aisnobol SIR m3
        6620  ? <- ?
callee.open/EQUAL                                    5920        2      2      2  aisnobol SIR m3
        5920  ? <- ?
callee.open/UNREAD.SINGLETON                         4160        2      2      2  aisnobol SIR m3
        4160  ? <- ?
callee.open/UNREAD.REGULAR                           4074        2      2      2  aisnobol SIR m3
        4074  ? <- ?
apply.open/UNREAD                                    3744        2      2      2  aisnobol SIR m3
        2554  ? <- rt_call_named_proc
         617  ? <- ?
         573  ? <- __libc_start_main
callee.open/FIX                                      3330        1      1      1  aisnobol TEST m3
        3330  ? <- ?
callee.open/LREVERSE                                 1990        2      2      2  aisnobol SIR m3
        1990  ? <- ?
apply.open/READ                                      1932        2      2      2  aisnobol SIR m3
         974  ? <- rt_call_named_proc
         479  ? <- ?
         479  ? <- __libc_start_main
descr.tiny/FAIL.IF.NIL                               1718        2      2      2  aisnobol SIR m3
        1718  rt_call_proc_descr <- rt_call_named_proc
descr.tiny/FAIL.IF.NIL.ELSE.SUCCEED                  1702        2      2      2  aisnobol SIR m3
        1702  rt_call_proc_descr <- rt_call_named_proc
named.tiny/OPSYNunary|                              1530        2      2      2  aisnobol SIR m3
```
### csnobol4
```
mark                                                 hits  entries     m3     m4  witness (suite entry mode)
apply.open/DIFFER                                      24        1      1      1  csnobol4 lexcmp m3
          12  ? <- ?
          12  ? <- __libc_start_main
apply.open/IDENT                                       24        1      1      1  csnobol4 lexcmp m3
          12  ? <- ?
          12  ? <- __libc_start_main
apply.open/LEQ                                         24        1      1      1  csnobol4 lexcmp m3
          12  ? <- ?
          12  ? <- __libc_start_main
apply.open/LGE                                         24        1      1      1  csnobol4 lexcmp m3
          12  ? <- ?
          12  ? <- __libc_start_main
apply.open/LGT                                         24        1      1      1  csnobol4 lexcmp m3
          12  ? <- ?
          12  ? <- __libc_start_main
apply.open/LLE                                         24        1      1      1  csnobol4 lexcmp m3
          12  ? <- ?
          12  ? <- __libc_start_main
apply.open/LLT                                         24        1      1      1  csnobol4 lexcmp m3
          12  ? <- ?
          12  ? <- __libc_start_main
apply.open/LNE                                         24        1      1      1  csnobol4 lexcmp m3
          12  ? <- ?
          12  ? <- __libc_start_main
apply.open/EQ                                           4        1      1      1  csnobol4 diag1 m3
           2  ? <- ?
           2  ? <- __libc_start_main
apply.open/FILE                                         2        1      1      1  csnobol4 file m3
           1  ? <- ?
           1  ? <- __libc_start_main
apply.open/TRIM                                         2        1      1      1  csnobol4 diag1 m3
           1  ? <- ?
           1  ? <- __libc_start_main
dtx.open/EXPR$0                                         2        1      1      1  csnobol4 diag1 m3
           2  rt_eval_open <- ?
dtx.open/EXPR$1$q                                       2        1      1      1  csnobol4 diag1 m3
           2  rt_eval_open <- ?
dtx.open/EXPR$2                                         2        1      1      1  csnobol4 diag1 m3
           2  rt_eval_open <- ?
```
### gimpel
```
mark                                                 hits  entries     m3     m4  witness (suite entry mode)
chain.eval.conve/?                                     86        3      3      3  gimpel find_driver m3
          66  ? <- ?
          20  ? <- rt_defer_open_cell
chain.eval.v/?                                         86        3      3      3  gimpel find_driver m3
          66  ? <- ?
          20  ? <- rt_defer_open_cell
apply.open/DIFF                                        50        1      1      1  gimpel infinip_driver m3
          25  ? <- ?
          25  ? <- __libc_start_main
apply.open/DIV                                         50        1      1      1  gimpel infinip_driver m3
          25  ? <- ?
          25  ? <- __libc_start_main
apply.open/EQ.                                         50        1      1      1  gimpel infinip_driver m3
          25  ? <- ?
          25  ? <- __libc_start_main
apply.open/LT.                                         50        1      1      1  gimpel infinip_driver m3
          25  ? <- ?
          25  ? <- __libc_start_main
apply.open/MULT                                        50        1      1      1  gimpel infinip_driver m3
          25  ? <- ?
          25  ? <- __libc_start_main
apply.open/REMDR.                                      50        1      1      1  gimpel infinip_driver m3
          25  ? <- ?
          25  ? <- __libc_start_main
apply.open/SUM                                         50        1      1      1  gimpel infinip_driver m3
          25  ? <- ?
          25  ? <- __libc_start_main
callee.open/CEIL                                       50        2      2      2  gimpel floor_driver m3
          50  ? <- ?
callee.open/POL                                        36        2      2      2  gimpel l_two_driver m3
          36  ? <- ?
callee.open/SS                                         26        2      0      2  gimpel l_two_driver m4
          26  ? <- ?
callee.open/FLOOR                                      25        2      0      2  gimpel floor_driver m4
          25  ? <- ?
callee.open/CPUSH                                      16        2      2      2  gimpel l_two_driver m3
          16  ? <- ?
callee.open/LOG                                        12        1      1      1  gimpel log_driver m3
          12  ? <- ?
```
### snoflake
```
mark                                                 hits  entries     m3     m4  witness (suite entry mode)
apply.open/DIFFER                                      24        1      1      1  snoflake lexical-comparison m3
          12  ? <- ?
          12  ? <- __libc_start_main
apply.open/IDENT                                       24        1      1      1  snoflake lexical-comparison m3
          12  ? <- ?
          12  ? <- __libc_start_main
apply.open/LEQ                                         24        1      1      1  snoflake lexical-comparison m3
          12  ? <- ?
          12  ? <- __libc_start_main
apply.open/LGE                                         24        1      1      1  snoflake lexical-comparison m3
          12  ? <- ?
          12  ? <- __libc_start_main
apply.open/LGT                                         24        1      1      1  snoflake lexical-comparison m3
          12  ? <- ?
          12  ? <- __libc_start_main
apply.open/LLE                                         24        1      1      1  snoflake lexical-comparison m3
          12  ? <- ?
          12  ? <- __libc_start_main
apply.open/LLT                                         24        1      1      1  snoflake lexical-comparison m3
          12  ? <- ?
          12  ? <- __libc_start_main
apply.open/LNE                                         24        1      1      1  snoflake lexical-comparison m3
          12  ? <- ?
          12  ? <- __libc_start_main
descr.tiny/TFN                                          6        1      1      1  snoflake value-trace-during-match m3
           6  rt_call_proc_descr <- ?
apply.open/dup                                          2        1      1      1  snoflake lowercase-indirect-and-apply m3
           1  ? <- ?
           1  ? <- __libc_start_main
callee.open/PRT                                         2        1      1      1  snoflake kalah-opening-search m3
           2  ? <- ?
descr.enter.thunk/EXPRNM$0                              2        1      1      1  snoflake pattern-assignment-targets m3
           2  rt_call_proc_descr <- rt_at_cursor
descr.tiny/SONG                                         2        1      1      1  snoflake twelve-days m3
           2  rt_call_proc_descr <- ?
population: 12 trace file(s) in 1 director(y/ies); 13 mark(s), 206 hit(s)
```
### testpgms
```
mark                                                 hits  entries     m3     m4  witness (suite entry mode)
apply.open/EQ                                           8        1      1      1  testpgms test1 m3
           4  ? <- ?
           4  ? <- __libc_start_main
apply.open/TRIM                                         2        1      1      1  testpgms test1 m3
           1  ? <- ?
           1  ? <- __libc_start_main
dtx.open/EXPR$0                                         2        1      1      1  testpgms test1 m3
           2  rt_eval_open <- ?
dtx.open/EXPR$1$Q                                       2        1      1      1  testpgms test1 m3
           2  rt_eval_open <- ?
dtx.open/EXPR$2                                         2        1      1      1  testpgms test1 m3
           2  rt_eval_open <- ?
named.tiny/OPSYNFACTO                                  2        1      1      1  testpgms test1 m3
           2  _usercall_hook <- ?
population: 2 trace file(s) in 1 director(y/ies); 6 mark(s), 18 hit(s)
```
