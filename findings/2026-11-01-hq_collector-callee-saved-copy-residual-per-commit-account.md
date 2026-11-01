# FINDING 2026-11-01 (hq_collector): the callee-saved copy residual, 294 at CTO-143 to 533 at origin, commit by commit

Row `gc-the-callee-saved-copy-residual-drifted-from-284-to-533-since-cto-143-named-by-commit-and-file-each-reload-sanctioned-on-the-page-or-cured`; gate `test_gate_gc_a_callee_saved_register_at_an_allocating_return_is_named_not_assumed.sh` arm 5. METHOD: each commit built in a worktree (`make -j`), the gate's own eight witnesses compiled to mode-4 asm, read by ONE census (`util_gc_callee_saved_census.py`, harness at origin 2026-11-01); `copies` is the SUMMARY line's `copies=`. 79b7aa13d (CTO-143, 09-23) reads **294** on today's census against the ceiling's 284 (defer.sno 175 against 166, sno 44 against 43): the instrument agrees within 10. The two bisects (this seat, two sessions) agree where they overlap (1ba942a4a 167, 4030b0d03 323, e53f5dcd6 522).

## Every measured point in git order (delta against the previous measured point)

| date | commit | copies | delta | subject |
|---|---|---|---|---|
| 09-23 01:15 | `79b7aa13d` | 294 |  | icon: bb_deref's ordinary-branch poll wrongly assumed r13/r15d always hold the scan subject |
| 09-25 16:46 | `b921002ef` | 216 | -78 | prolog monitor plug: a predicate the program declares dynamic or creates by assert fires no CALL, no STMT insi |
| 09-27 18:40 | `3eee3be9d` | 218 | +2 | raku: index and rindex are character-indexed methods (the sub forms route to them), defined(x) is a Bool, and  |
| 10-01 12:15 | `928d35b87` | 230 | +12 | zd_plan: a node an unplanned path enters at depth is a wall -- the run stops before it and the graph is planne |
| 10-04 17:27 | `4aa623960` | 185 | -45 | gc: the SNOBOL4 root map cell is stored at its map offset whatever graph was emitted before main -- the emitte |
| 10-09 16:54 | `747f1637d` | 162 | -23 | gc chain: the pl_proto goal arm's gamma landing is a site -- a poll inside a goal that catch (or any meta-call |
| 10-10 09:34 | `821026786` | 162 | +0 | Pascal: a // line comment is a comment, as fpc -Miso reads it (ceo CEO-1589) |
| 10-10 11:18 | `442e05294` | 162 | +0 | prolog: library(rbtrees), (assoc), (ordsets), (option), (lists) vendored from swipl 9.0.4 -- the SSU set; a li |
| 10-10 13:35 | `c6f98a460` | 162 | +0 | Pascal: uses and units, compile-time and whole-program, through CEO-1614's one dialect switch -- every arm ans |
| 10-10 14:08 | `5104a446c` | 162 | +0 | prolog_parse.c: the attributed-variable arming's seen[] is sized from the API list at entry, not a fixed 32 -- |
| 10-10 14:27 | `c737ce731` | 162 | +0 | util_build_rungs_suite.py: raku's regex column marks every regex construct, and the reindex gate holds raku's  |
| 10-10 13:54 | `be78c471d` | 162 | +0 | raku regex chunk 1: a nested capture is not core (hq_raku's red) and the named-capture list is a VLA sized by  |
| 10-10 12:56 | `eec30c90d` | 167 | +5 | prolog: the module rule -- SCRIP flattens modules by qualified rename in prolog_lower.c's first pass: a plunit |
| 10-10 22:46 | `a7cca774a` | 167 | +0 | raku: an escaped sigil in a double-quoted string is a literal -- "\$" prints $ and "\$x" prints $x, where the  |
| 10-10 22:56 | `abcfc21e9` | 167 | +0 | Pascal: a function result belongs to its activation, a nested routine passes an outer var parameter on, a name |
| 10-10 22:50 | `1ba942a4a` | 167 | +0 | raku: my T $x .= m(...) calls m on the type T, and :$v is the pair v => $v, as Rakudo does -- the declaration' |
| 10-10 23:28 | `4030b0d03` | 323 | +156 | SNOBOL4: a VALUE trace fired by an assignment inside a match -- $ immediate, @ cursor and . conditional -- run |
| 10-10 22:14 | `a65dd04b8` | 323 | +0 | prolog: the vendored-library selection pass looks its keys up in hashed sets, not by two linear scans -- test_ |
| 10-11 00:24 | `8b0f30b01` | 323 | +0 | raku: a for loop over the topic restores the outer $_ when it ends -- by exhaustion, last or a failure -- wher |
| 10-11 04:42 | `515fb5622` | 323 | +0 | Pascal: an array of arrays holds each row as an array of its own bounds, and a row is a value that copies, as  |
| 10-11 12:23 | `87be0d5d8` | 324 | +1 | prolog: string_to_list/2 is SWI's backcomp alias of string_codes/2 -- the advent demo's day-1 reader answers a |
| 10-11 12:39 | `84e1a94a2` | 325 | +1 | Pascal: a call to a __pas_ runtime builtin is a direct call with its table index baked, not a by-name strcmp w |
| 10-11 12:49 | `a17dceec6` | 325 | +0 | prolog: string_concat/3 splits its third argument in the (+,-,+), (-,+,+) and enumerating (-,-,+) modes as swi |
| 10-11 12:51 | `fe63512cc` | 325 | +0 | lower_prolog.c: re-flow pl_det_leaves after a17dceec6 -- the 200-column ratchet the landing owed |
| 10-11 12:51 | `d85792e46` | 349 | +24 | rtx: layer 2 set 2 (match) and the arith fold -- rt_defer_close and rt_match_enter decline through the one ver |
| 10-11 12:52 | `417de74ae` | 349 | +0 | prolog: throw/1 keeps the ball's attributed variables, as swipl does -- the ball copy made at throw takes copy |
| 10-11 12:55 | `567d5b475` | 349 | +0 | gc: SCRIP_GC_PLANT_POISON, the cto's off-chain falsifier as a plant with an on-chain control, and the matrix d |
| 10-11 13:38 | `29699fe03` | 355 | +6 | rtx: re-land the plunify veneer removal with the unifier's working registers kept in its own frame; the ABI wa |
| 10-14 07:24 | `9052afaa7` | 355 | +0 | prolog: the reclaimed-clause bomb is a hand-written asm leaf that aligns its own stack, not a C function behin |
| 10-14 09:11 | `25c9c0f61` | 355 | +0 | Revert "prolog: nb_linkarg/3 stores a structure copy that shares only the unbound variables ..." (7edbcc787) |
| 10-14 10:10 | `58d8ee54e` | 355 | +0 | prolog: library(record) vendored, a DCG rule keeps an =/2 data term, strip_module/3 and prolog_load_context(mo |
| 10-14 10:30 | `3791c84ae` | 360 | +5 | prolog: retract/1 on the run-time road matches (H :- B) and a qualified head, keeps the logical update view; f |
| 10-14 11:06 | `1ae478e69` | 360 | +0 | prolog: IEEE 754 in the SWI dialect -- float flags, Annex F special values, roundtoward/2, number order, NaN u |
| 10-14 11:44 | `a61aea8a8` | 360 | +0 | icon: a procedure's frame is pinned to rbp only when its graph holds an op that can retain a callee frame or c |
| 10-14 11:54 | `0e2661ec2` | 360 | +0 | SNOBOL4: an out-of-memory under a SETEXIT trap returns FAIL to the emitted call site and the statement's SETEX |
| 10-14 12:04 | `75d498cd3` | 360 | +0 | icon: the preprocessor runs on the fly, one stage, as Arizona's does -- the lexer pulls each line through ipp  |
| 10-14 12:15 | `ca9f124e7` | 360 | +0 | CEO-1680: the SCRIP_TEST_PLANT_ZLS_HOLE seam is deleted from zls_dump; the two frame-slot-kind gates prove the |
| 10-14 12:15 | `36f2545b8` | 360 | +0 | SNOBOL4 lower: FAIL after a FENCE(x) in an alternation arm backtracks into the FENCE -- the fence segment's re |
| 10-14 11:57 | `10ca40892` | 415 | +55 | prolog: library(main) and library(optparse) vendored, argv_options/3,4 take their Argv module-qualified, curre |
| 10-14 12:35 | `ea8efaeca` | 415 | +0 | collector: the heap holds SPITBOL's error reserve inside its cap -- the cap's last page is never committed by  |
| 10-14 12:57 | `304f22799` | 415 | +0 | prolog: call/9 and call/10 take a module-qualified closure, and a meta-call whose goal passes 1024 arguments r |
| 10-14 13:06 | `3d7561dce` | 415 | +0 | prolog: a setup_call_cleanup compiled at run time inside a mode-4 binary is armed -- the run-time compiler rea |
| 10-14 13:11 | `287db27cb` | 415 | +0 | icon: the entry zero-fill of a plain or generator procedure frame is SSE stores, not rep stosb -- the same byt |
| 10-14 13:13 | `805b5a391` | 415 | +0 | SNOBOL4 family: a thunk's call prologue no longer resolves the procedure's parameter and result cells by name  |
| 10-14 13:16 | `9924a117a` | 415 | +0 | pascal: an array of string reads, stores, compares and measures its elements as strings; a string compared wit |
| 10-14 13:07 | `34a173dc2` | 415 | +0 | prolog: rational equality compares numerator and denominator in place, so rtx_pl_unify allocates nothing again |
| 10-14 13:57 | `ba03b7ef3` | 415 | +0 | gc: the streamed walk carries no fixed table and refuses a link below its gap by name -- the cto's finding (1) |
| 10-14 13:48 | `5b375694e` | 415 | +0 | prolog dicts: select_dict/3, :< and >:< (the reader's 700 xfx operators), b_set_dict/3 and nb_set_dict/3, get_ |
| 10-14 13:50 | `847a4db05` | 415 | +0 | caps: pl_skip_bom reads its byte-order mark into one word, and the stale class-B row bom leaves CLASS_AB.tsv - |
| 10-14 13:49 | `30c9c080d` | 458 | +43 | prolog: between(L, H, X) tests a bound X once instead of walking L..H, and takes inf or infinite as H, literal |
| 10-14 13:54 | `78e3857b8` | 458 | +0 | prolog: in the SWI dialect format/2 takes a single argument that is not a list as the one-element list swipl m |
| 10-14 14:09 | `b86a8edd0` | 458 | +0 | rtx: rt_jct_relop answers the numeric relops -- LT, LE, GT, GE, EQ, NE over integers and reals (mixed pairs as |
| 10-14 17:17 | `4ee926311` | 457 | -1 | RAKU parser: block-form `with` / `orwith` / `without` test DEFINEDNESS and bind the topic -- they parsed as if |
| 10-14 18:47 | `0b870cf3e` | 457 | +0 | stage 1 (CEO-1749): the module is entered only at compile time and the entry is pinned at 1; a run-time parse  |
| 10-14 19:22 | `3b0fae08a` | 457 | +0 | prolog: SWI's stream errors, eof_action(error), an alias in use and stream_pair/3 answer as swipl -- SWI core/ |
| 10-14 19:31 | `afc8f4b2f` | 457 | +0 | prolog: a program that runs load_files/2 references the lists and apply libraries whole -- code read at run ti |
| 10-14 19:42 | `311091c62` | 458 | +1 | snocone: import -- `import name;` is a statement, (TT_IMPORT "name") in the pruned tree of both parsers, resol |
| 10-14 19:42 | `c04c20de2` | 458 | +0 | stage 1: under --module, the startup procedure records and the field-guard thunk words are emitted into .data. |
| 10-14 19:42 | `bdef07dc8` | 458 | +0 | stage 1 (CEO-1761): the export glue holds no static table -- sc_text_of returns the string field or nothing (e |
| 10-14 19:50 | `48bd63328` | 470 | +12 | prolog: goal_expansion reaches a user meta-argument, a module's term_expansion sees its own facts, a dynamic b |
| 10-15 11:08 | `e8c88a8b3` | 444 | -26 | prolog: clause/2 and retract/1 read a body variable as call(V) under , ; -> (and *-> and \+ in the SWI dialect |
| 10-15 15:26 | `ce43ad338` | 447 | +3 | snobol4: the null string concatenated with an unevaluated expression is that expression -- x *POS(0), *POS(0)  |
| 10-17 14:25 | `43552a85a` | 447 | +0 | icon cure: the by-name "[]" and ":=" call the C twins, not the asm leaves b2f5fda77 made of rt_subscript_var_s |
| 10-17 15:41 | `1ef0e06c7` | 447 | +0 | prolog: term_variables walks its term once -- a variable is marked on first sight and threaded through its own |
| 10-17 15:58 | `4e1ac56b4` | 447 | +0 | prolog: the choice mark's internal labels are 245-249, above the ids the trace and fc roads synthesize -- a tr |
| 10-17 16:06 | `f8d98e955` | 447 | +0 | pascal: '><' with an operand that is not a set is refused at compile time -- PAT iso7185prt0714 (b := 1 >< 2)  |
| 10-17 16:13 | `de14c4404` | 447 | +0 | prolog: the occurs scan is an asm leaf -- rt_pl_occurs_a walks the term as plw_occurs_walk does and unmarks in |
| 10-17 16:13 | `0bb392122` | 468 | +21 | zetas: Prolog BB operands and locals on the RSP spine in every graph, retaining ones included -- PROLOG-SPINE- |
| 10-17 16:27 | `8ed67780e` | 468 | +0 | rtx icon: rt_lv_is_list is an asm leaf -- the list test every Icon list builtin and view runs no longer calls  |
| 10-17 17:14 | `d549ae02d` | 468 | +0 | snobol4: TRACE and STOPTR return the null string as SPITBOL does -- they returned the traced name, so X = TRAC |
| 10-17 17:32 | `2c1f2d637` | 468 | +0 | prolog: atom text carries its length and code 0 is an element -- the interner stores each atom's byte count be |
| 10-17 19:15 | `f543a7578` | 468 | +0 | snobol4: a file argument's options are read as SPITBOL reads them, for a plain file and a pipe alike -- the na |
| 10-17 19:21 | `452db403e` | 468 | +0 | prolog: the assertz reclaim carries no plant seam -- pl_db_reclaim no longer reads SCRIP_GC_PLANT_PL_RECLAIM,  |
| 10-17 19:22 | `26dbd33aa` | 468 | +0 | snobol4: a deferred capture into a table element assigns it, as SPITBOL does -- S 'y' . *T['k'] raised 239 "in |
| 10-17 19:23 | `2f03e45cf` | 468 | +0 | icon bignum: a small operand is a stack BIG, multiply puts the shorter operand outside and zeroes nothing, a B |
| 10-17 19:19 | `e53f5dcd6` | 522 | +54 | zetas: THE SPINE FLIP -- every code road that kept a box off the RSP spine is deleted, so a BB operand or loca |
| 10-18 21:38 | `d4095efc7` | 522 | +0 | icon: a repeated alternation /e lowers to a one-arm disjunction in a loop over a per-activation flag, not to t |
| 10-23 10:58 | `e3373e9fe` | 526 | +4 | snobol4: V = S ? P takes a computed capture target's name at statement time, as S ? P does; EVAL of a scan rea |
| 10-25 01:07 | `579537ddb` | 497 | -29 | planner: a run headed by the UNMARK that restores a BOUND's rsp belongs to that BOUND's family -- the clause e |
| 10-29 14:51 | `6221116ef` | 506 | +9 | pascal: an enumeration member's source spelling is an attribute child of the member leaf, and a written enumer |
| 10-29 19:49 | `edf347c58` | 506 | +0 | prolog: a fact table that gains a rule compiles no slot at the flip -- a slot with no fragment is compiled whe |
| 10-30 09:38 | `3503e761b` | 506 | +0 | raku: a nested sub declared under a name another sub already has is its own sub -- each enclosing scope binds  |
| 10-30 10:48 | `4c45d2882` | 506 | +0 | gc: a table's bucket pointer vector is stamped HB_AGGP, not HB_AGGB -- one block code, one shape (the cto's AR |
| 10-30 10:52 | `9a4b7e15b` | 506 | +0 | raku: the grep listop takes a type name as its matcher |
| 10-30 10:54 | `c407e1172` | 506 | +0 | pascal step 3, landing 16: the legacy OVERLAY-WORD producers and the variant-case stack are deleted -- pas_vca |
| 10-30 10:59 | `fba462415` | 506 | +0 | parser_snobol4.sc: a real literal's exponent letter is E, e, D or d, as snobol4.l's EXP [eEdD][+-]?{DIGIT}+ re |
| 10-30 10:59 | `5d15b5ca2` | 511 | +5 | prolog: copy_term/3 returns the residual goals of attributed variables as swipl -- freeze/2, when/2 and every  |
| 10-30 11:07 | `0a819f7c4` | 511 | +0 | gc: the six Prolog and trie typedefs move VERBATIM out of unification.c into src/runtime/prolog_db_blocks.h, t |
| 10-30 11:10 | `7a432a57e` | 511 | +0 | gc: the heap validator's slot table rows HB_PLDB, HB_PLDBS, HB_PLDBR, HB_PLDBK, HB_TRIE and HB_TRIEN, cut from |
| 10-30 11:11 | `045fbb979` | 511 | +0 | pascal step 3, landing 17: the variant-tag DECLARATION table is the typer's -- the arm masks and the tag field |
| 10-30 11:12 | `ae5420a68` | 511 | +0 | gc: three typed classes out of HB_WSB, small once -- HB_NVAR (NV_t), HB_FNCB (FNCBLK_t), HB_DATB (DATBLK_t) -- |
| 10-30 11:15 | `59cd3a109` | 468 | -43 | zeta-layout step 2a, chunk 4: the private low region -- the lowest bytes of a box's cell where a template's tr |
| 10-30 11:03 | `4ae2de882` | 508 | +40 | prolog: XSB's attributed-variable handler API -- install_verify_attribute_handler/4,5 names the goal a unifica |
| 10-30 11:06 | `dff2a78b2` | 508 | +0 | gc: gc_allocating_table.inc regenerated -- ef92378ed (SWI dialect U+FFFD read) added pl_read_term_text_raw and |
| 10-30 11:33 | `578746425` | 508 | +0 | prolog: copy_term keeps a cyclic subterm's sharing (an identity cache of 16 argument arrays in the copy walk), |
| 10-30 11:41 | `db22dac46` | 508 | +0 | raku: a for statement modifier restores the outer topic when it ends |
| 10-30 12:04 | `e12588207` | 508 | +0 | raku: .Numeric, .Int, .Real and .Num of an array, a list or a hash answer its element count |
| 10-30 13:36 | `8edfa91fd` | 511 | +3 | gc: gc_allocating_table.inc regenerated -- pl_gnu_ctx, added upstream of the whole-predicate landing, was a ro |
| 10-30 15:49 | `65dbbc9bd` | 511 | +0 | prolog: under the SWI dialect a DCG pass-through unifies S = S0, as swipl writes it (CEO-2063) |
| 10-31 08:28 | `d150a39e9` | 511 | +0 | prolog: under the SWI dialect a sort that removes duplicates accepts a cyclic list -- sort/2, and sort/4 with  |
| 10-31 08:40 | `830911958` | 511 | +0 | raku: Test is Raku source in the setting, not C (ARCH-RAKU-TO-100 section 1.2 (c) and section 6 step 0, CEO-20 |
| 10-31 08:43 | `bee1602c4` | 507 | -4 | prolog: char_type/2 and code_type/2 classify by Unicode code point as swipl 9.0.4 does -- the leaf read the fi |
| 10-31 09:11 | `d3af55419` | 507 | +0 | prolog: expand_file_name/2 in the swi_builtins layer -- swipl 9.0.4's glob (SWI files/test_glob glob_expand:gl |
| 10-31 10:19 | `f2faefaff` | 507 | +0 | gc: the mark loop gets its own class for the Pascal pointer, MK_PCELL, with an RT_DIAG containment check -- a  |
| 10-31 09:26 | `f6de7facb` | 507 | +0 | prolog: XSB WFS step 6, one body one run, and step 7, the SCC depth number (ARCH-PROLOG-WFS-TABLING section 8, |
| 10-31 10:42 | `71267630d` | 507 | +0 | pascal: the unsigned arms of 8.12, first four -- a QWord expression is the typer's fact (pty_of_low uns), and  |
| 10-31 10:54 | `a8d0fc5ce` | 507 | +0 | pascal: an element pointer indexed through a pointer-to-array type (p := @a[2]; p^[i]), the with form of it, a |
| 10-31 10:32 | `48b7cb4c3` | 533 | +26 | prolog: a structure symbol carries its module -- the atom table interns on (module, name), term_new_mod/3 and  |
| 10-31 11:42 | `882728745` | 533 | +0 | speed: REPLACE's cached-map hit is one compact block ahead of the general path, and rt_translate_bytes runs ei |
| 10-31 13:11 | `792c12cf0` | 533 | +0 | speed: bb_emit_x86 in the binary medium initialises only the internal labels its text references, not all 1000 |
| 10-31 16:19 | `decdc9920` | 533 | +0 | raku: NaN is identical to itself, answers isNaN and sign, orders to Nil under <=>, and Num(NaN) is a call (run |
| 11-01 08:47 | `b21fefc88` | 533 | +0 | make test: test_gate_skill_gate_refuses_an_edit_under_src_without_its_skill.sh joins the blocking set (the cto |

## The raises, attributed (both ends measured; file | register | class | callee)

- `1ba942a4a` -> `4030b0d03` **167 -> 323**: file {'sno': 28, 'defer.sno': 128}; registers {'r12': 54, 'rbx': 30, 'r14': 42, 'r13': 30}; class {'ARITH': 36, 'CELL': 132, 'CELL:CELL:CALLERS': -2, 'CELL:ARITH': -10}; callees {'rt_apply_open': 33, 'rt_dcap_resume': 33, 'rt_trace_pend_run': 33, 'rt_trace_pend_close': 33}. SNOBOL4: a VALUE trace fired by an assignment inside a match -- $ immediate, @ cursor and . conditio
- `be78c471d` -> `eec30c90d` **162 -> 167**: file {'pl': 5}; registers {'r12': 5}; class {'ARITH': 5}; callees {'to_int': 4, 'rt_pl_dop_atom_concat_n': 1}. prolog: the module rule -- SCRIP flattens modules by qualified rename in prolog_lower.c's first pass
- `fe63512cc` -> `d85792e46` **325 -> 349**: file {'defer.sno': 22, 'sno': 2}; registers {'rbx': 4, 'r12': 6, 'r13': 6, 'r15': 4, 'r14': 4}; class {'CELL': 24}; callees {'c_rt_match_enter': 24}. rtx: layer 2 set 2 (match) and the arith fold -- rt_defer_close and rt_match_enter decline through t
- `58d8ee54e` -> `3791c84ae` **355 -> 360**: file {'pl': 5}; registers {'r12': 5}; class {'ARITH': 5}; callees {'to_int': 4, 'rt_pl_dop_atom_concat_n': 1}. prolog: retract/1 on the run-time road matches (H :- B) and a qualified head, keeps the logical upda
- `36f2545b8` -> `10ca40892` **360 -> 415**: file {'pl': 55}; registers {'r13': 24, 'r12': 31}; class {'CELL': 24, 'ARITH': 31}; callees {'to_int': 46, 'rt_pl_dop_atom_concat_n': 7, 'rt_pl_dop_sub_atom_n': 2}. prolog: library(main) and library(optparse) vendored, argv_options/3,4 take their Argv module-qualif
- `847a4db05` -> `30c9c080d` **415 -> 458**: file {'pl': 43}; registers {'r12': 24, 'r13': 19}; class {'ARITH': 24, 'CELL': 19}; callees {'to_int': 40, 'rt_pl_dop_atom_concat_n': 3}. prolog: between(L, H, X) tests a bound X once instead of walking L..H, and takes inf or infinite as 
- `bdef07dc8` -> `48bd63328` **458 -> 470**: file {'pl': 12}; registers {'r12': 8, 'r13': 4}; class {'ARITH': 8, 'CELL': 4}; callees {'to_int': 12}. prolog: goal_expansion reaches a user meta-argument, a module's term_expansion sees its own facts, a
- `de14c4404` -> `0bb392122` **447 -> 468**: file {'pl': 21}; registers {'r13': 21}; class {'CELL': 21}; callees {'to_int': 8, 'rt_pl_dop_atom_concat_n': 4, 'dop_write': 3, 'dop_pl_set_input': 1}. zetas: Prolog BB operands and locals on the RSP spine in every graph, retaining ones included -- PRO
- `2f03e45cf` -> `e53f5dcd6` **468 -> 522**: file {'pl': 54}; registers {'r13': 54}; class {'CELL': 64, 'LEA': -10}; callees {'to_int': 52, 'rt_pl_dop_atom_concat_n': 1, 'rt_pl_dop_sub_atom_n': 1}. zetas: THE SPINE FLIP -- every code road that kept a box off the RSP spine is deleted, so a BB opera
- `fba462415` -> `5d15b5ca2` **506 -> 511**: file {'pl': 5}; registers {'r13': 2, 'r12': 3}; class {'LEA': 1, 'ARITH': 3, 'CELL': 1}; callees {'dop_pl_ground': 2, 'rt_pl_dop_findall_new': 2, 'rt_pl_dop_findall_add': 1}. prolog: copy_term/3 returns the residual goals of attributed variables as swipl -- freeze/2, when/2 
- `a8d0fc5ce` -> `48b7cb4c3` **507 -> 533**: file {'pl': 26}; registers {'r13': 13, 'r12': 13}; class {'LEA': 3, 'ARITH': 13, 'CELL': 10}; callees {'dop_pl_set_output': 10, 'to_int': 8, 'dop_pl_between_special': 4, 'dop_pl_ground': 2}. prolog: a structure symbol carries its module -- the atom table interns on (module, name), term_new_
- `ae5420a68` -> `59cd3a109` **511 -> 468**: file {'pl': -33, 'pas': 0, 'icn': -10}; registers {'r13': -52, 'r12': 9}; class {'LEA': -5, 'CELL': -47, 'ARITH': 9}; callees {'dop_pl_between_special': -28, 'c_rt_coerce_num2_d': -3, 'dop_pl_ground': -2, 'c_rt_relop_val_coerce': -2}. zeta-layout step 2a, chunk 4: the private low region -- the lowest bytes of a box's cell where a tem
- `59cd3a109` -> `4ae2de882` **468 -> 508**: file {'pl': 30, 'pas': 0, 'icn': 10}; registers {'r13': 49, 'r12': -9}; class {'LEA': 5, 'CELL': 44, 'ARITH': -9}; callees {'dop_pl_between_special': 28, 'c_rt_coerce_num2_d': 3, 'dop_pl_ground': 2, 'c_rt_relop_val_coerce': 2}. prolog: XSB's attributed-variable handler API -- install_verify_attribute_handler/4,5 names the goal

## Not yet attributed (the earlier session's refine.py was still running at nice 19 when this was written)
- `3eee3be9d..928d35b87` +12; `e3373e9fe` +4; `579537ddb..6221116ef` +9; falls with no attribution: `79b7aa13d..b921002ef` -78, `928d35b87..4aa623960` -45, `4aa623960..747f1637d` -23, `e8c88a8b3` -26, `579537ddb` -29.

## What it says
1. No raise is a new register or a new defining form (arm 3 read 0 until e3373e9fe); every raise is more allocating call sites reading the same copy classes (r12/r13/r14/r15/rbx as CELL, r12 as ARITH).
2. Two thirds of the 533 are CELL; looking through add/sub-by-immediate to the earlier value would remove at most about 23 of 549 readings (measured).
3. The ratchet went dark because its ceiling never followed the falls: 162 on 10-09 under 284, then 4030b0d03 (+156) crossed it on the day it landed.

