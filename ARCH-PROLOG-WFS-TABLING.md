# ARCH-PROLOG-WFS-TABLING — WELL-FOUNDED TABLING AND THE XSB LOADER (hq_prolog, 2026-10-14, CEO-1721)

**Status: BUILT AND CONFIRMED (the cto, 2026-10-25 03:0x CDT, CEO-1971 (1); the DESIGN status of 10-14 is history).** § 3 is what `prelude/tabling.pl` runs today: `tnot/1` (lines 212-228: the complete-table read, the raise, the T/U reads by phase, the residual push), the phases `'$tbl_ph'` 0/t/u/r with `'$tbl_alt'` and `'$tbl_wfsrun'` (193), the residual pass in `'$tbl_fin_all'`/`'$tbl_done'` (184, 192), `undefined/0` (229-230), `not_exists/1` (231-232), the delay list as the one trailed root word (`'$tbl_dlget'`/`'$tbl_dlset'`, the cto's 10-14 ruling in § 3.1). MEASURED on results.tsv (latest m3 reading per case): xsb/wfs_tests 72 of 72 PASS, xsb/delay_tests 87 PASS + 1 UNGRADED, xsb/sub_tests 36 of 36 PASS, SWI tabling/test_wfs 8 of 8 PASS. RE-CUT AGAINST THE IDG (ARCH-PROLOG-TABLING-IDG.md §§ 1-3): § 3.1's "single current X cells" are, as built, the EVALUATION HEADER's own cells (`'$tbl_hdr'`, `'$tbh_own'(1..5)`: the in-progress tables, the wfs raise, the depth, the phase words) -- the header of the box doing the evaluation, no global, no second stack -- and the per-table T/U tries ride `d/6` as the page says; nothing else of § 3 moves. WHAT REMAINS, rows not designs: xsb table_tests `pps` FAIL (both modes, 10-24) and `sub_table_tests_pps` FAIL, the IDG page § 9's `negcycle`/`tda`/`tda_i` scheduling hangs, and `incremental_tests_test_wfs_update` FAIL with empty output (the XSB directive/loader class of TABLING-IDG § 0b) -- each one program at a time against XSB, the builder the ceo names (tabling: hq_zetas after the IDG's § 6; the XSB loader rows: the XsbTests seat). § 4 (the XSB loader) and § 5-6 keep their 10-14 text as the record of the build. Owner: hq_prolog. Ruling: the ceo,
CEO-1721 (*"WFS TABLING IS OPEN -- go"*), under CEO-1562's order (1) and LARGE CHUNKS (CEO-1478..1484).

## 0. The population and what it needs (measured 2026-10-14 at SCRIP 2bf257e2e)

| SWI file | cases swipl passes | needs |
|---|---|---|
| `xsb/delay_tests/xsb_test_delay.pl` | 87 (+1 EMPTY) | loader + WFS + residual programs (6 programs call `get_residual/2`) |
| `xsb/wfs_tests/xsb_test_wfs.pl` | 72 | loader + WFS (34 golds print `undefined`) |
| `xsb/sub_tests/xsb_test_sub.pl` | 36 | loader + subsumptive tabling (its own class, § 7) |
| `xsb/table_tests/xsb_test_tables.pl` | 32 | loader + variant tabling, some WFS and residuals |
| `xsb/basic_tests/xsb_test_basics.pl` | 26 | loader only (no `tnot`) |
| `xsb/ptq/xsb_test_ptq.pl` | 25 | loader only |
| `xsb/neg_tests/xsb_test_neg.pl` | 24 | loader + stratified `tnot` |
| `xsb/incremental_tests/xsb_test_incremental.pl` | 15 | loader + incremental tabling (row b2, not this page) |
| `xsb/ai_tests/xsb_test_ai.pl` | 11 | loader only |
| `xsb/nonmt_tests/xsb_test_nonmt.pl` | 9 | loader + WFS |
| `xsb/attv_tests/xsb_test_attv.pl` | 2 (5 swipl FAIL) | loader + attributed variables in tables |
| `tabling/test_wfs.pl` | 8 | WFS, `call_delays/2`, `undefined/0` |

Every XSB case runs `xsb_test/3` (`swi_tests/xsb/xsb_test.pl`): `source_file/2` finds the driver's directory, `load_files(M:File,
[if(changed), dialect(xsb)])` loads `<case>.P` at RUN TIME into module `xsb_<case>`, `abolish_all_tables`, then
`with_output_to(string(S), ignore(@(M:test, M)))` and the output is compared with `<case>_old` as a SORTED SET of terms (one term per
line, read with `op(499, fy, tnot)`; unreadable lines compare as `line(Text)`). So the order of output lines never matters, and
`get_residual/2` callers sort each delay list themselves (`gcr/2`): the order of literals inside a delay list never matters either.

## 1. What swipl answers (measured on swipl 9.0.4, the ref's oracle)

```prolog
:- table p/0, q/0, r/0, s/1, n/1, a/0, b/0, c/0.
p :- tnot(p).          q :- p, tnot(r).       r :- fail.
s(X) :- member(X, [1,2,3]), tnot(n(X)).       n(2).    n(3) :- tnot(n(3)).
a :- b.   b :- a.   a :- tnot(c).   c.
```
`call_delays(p, D)` gives `D = p` (an undefined answer called from outside a table succeeds, its own goal the delay);
`call_delays(q, D)` gives `D = q`; `r` fails; `s(1)` true, `s(3)` undefined, `s(2)` fails; `a` and `b` FAIL (the positive loop is
unfounded once `tnot(c)` is false); `tnot(p)` succeeds with delay `tnot p`; `get_residual(q, [p])` (the literal `tnot r` resolved
true and is gone); `get_residual(s(3), [tnot n(3)])`; `get_residual(s(1), [])`.

## 2. The engine today (prelude, `src/parsers/prolog/prolog_parse.c`, the `'$tbl_*'` family)

A tabled `p/N` is a wrapper `p(Xs) :- '$tbl_call'(p(Xs), '$tbl p'(Xs))` over the renamed clauses `'$tbl p'/N` (lower,
`pl_table_wrapper`). `'$tbl_get'` finds or makes the variant's answer trie (`'$trie_*'` C leaves; meta slot 0 the status
`incomplete|complete`, slot 1 `d(Goal, Impl, Kind, SemiNaiveState)`). The first tabled call LEADS: it evaluates its table
(`findall` over `Impl`), then repeats ROUNDS over every in-progress table, semi-naive (each round re-derives only through answers new
since the last), until a round adds no answer and no table; then it completes them all. A table whose evaluation touched no
incomplete table completes early. Consumers read the answer trie (`'$tbl_answer'`). Moded tables (answer subsumption) ride the
same rounds (row b1, landed f268f740e).

**What is missing for WFS:** `tnot/1` (an `existence_error` today), a truth value per answer (every stored answer is `true`), delay
lists, and any notion of negation inside the evaluating component.

## 3. THE DESIGN: the alternating fixpoint over the rounds, then one residual pass

SLG's delay/simplify/answer-completion machinery exists to make a SUSPENSION engine compute the well-founded model. Our engine does
not suspend: it re-runs clause bodies to a fixpoint. The well-founded model of the in-progress component is the ALTERNATING
FIXPOINT (Van Gelder), and that is exactly a sequence of our round evaluations with `tnot/1` read against the previous one:

- **U-phase** (overestimate): `tnot(A)` succeeds iff A has no answer in the last **T** set (none yet = always succeeds).
- **T-phase** (underestimate): `tnot(A)` succeeds iff A has no answer in the last **U** set.
- Positive calls read the CURRENT phase's answers (the rounds, unchanged). A COMPLETE table read from inside a phase gives its true
  answers in a T-phase and all its answers (true and undefined) in a U-phase; `tnot(A)` of a complete A reads A the same way.
- `U0 = phase 0` (exactly today's evaluation, every `tnot` of an incomplete table optimistic); then `T1, U1, T2, ...` until T
  stops growing (T only grows and U only shrinks, so this terminates; for a stratified component it stops at T1 = U0).
- **Answers in T are true; answers in U \ T are undefined; the rest are false.** Positive loops with no foundation are never derived
  by a least fixpoint, so ANSWER COMPLETION falls out of the construction instead of being a separate pass.

**THE RESIDUAL PASS (R).** After T is stable, one more U-phase runs with the delay list switched on: a positive literal that consumes
an undefined answer (in U \ T, of an in-progress or a complete table) and a `tnot(A)` with A undefined push a delay element; a `tnot`
of a true A fails; a `tnot` of a false A and a true answer push nothing. Each answer then stores the distinct delay lists it was
derived with; an answer in T stores `true`. This is SWI's residual program with every element that SLG simplification would remove
already absent (§ 1: `get_residual(q, [p])`), because T and U are known when the pass runs.

**THE PHASES RUN ONLY WHEN NEEDED.** A cell `'$tbl_wfs'` is raised when, inside the leader's evaluation, a `tnot/1` meets an
incomplete table or any literal meets an undefined answer of a complete table; a table whose evaluation raised it does not complete
early. A leader that ends phase 0 with the cell down completes exactly as today: no extra phase, no cost for the stratified and the
negation-free programs (test_tabling, the moded tables, ProBench).

### 3.1 Where the state lives (NO GLOBAL HOLDS A STACK, CEO-1542)

- Per table: the T and U sets of the last phases are two answer tries named in the table's own data term, `d(Goal, Impl, Kind, SN,
  W)` with `W = none | w(TTrie, UTrie)` (the C trie gives meta slots 0 and 1 only); destroyed with the table.
- Per evaluation: the phase (`'$tbl_ph'`: `0 | t | u | r`) and the `'$tbl_wfs'` raise -- single "current X" cells beside the
  engine's existing `'$tbl_leader'`, `'$tbl_dep'`, `'$tbl_mx'`.
- Per derivation: the CURRENT DELAY LIST, a backtrackable cell (`b_setval('$tbl_dl', ...)`) holding the list the present derivation
  has pushed; the rounds' `findall` resets it per clause body and collects `Answer-DelayList`; backtracking restores it. This is
  SWI's own representation (`'$tbl_delay_list'`, boot/tabling.pl `add_delay/1`): one value, replaced on backtracking, never one
  entry per live call -- the call nesting lives where it always did, on the machine stack. **RULED by the cto (2026-10-14): the
  backtrackable cell, under three conditions.** (1) One current value, never a stack in disguise: a nested derivation saves the outer
  list in a clause variable of its caller (the caller's frame), runs with its own, and restores from that variable -- no list of
  per-call entries ever accumulates in the cell. (2) Nothing reads the cell across a derivation boundary except through that save and
  restore, so a `tnot` or a completion never sees another derivation's list. (3) Its `b_setval` stays trailed UNCONDITIONALLY once the
  cto's conditional trail lands (that landing exempts only variable bindings; the cto names this cell in its proof). The cto also
  read § 3 against its trail design: the fixpoint inside `findall` never meets its sentinels, no consumer is suspended, no new
  choice-point kind is added.

### 3.2 The surface (SWI's names; the ISO superset adds them, no dialect switch)

`tnot/1`, `not_exists/1`, `undefined/0` (`:- table undefined/0. undefined :- tnot(undefined).`), `call_delays/2`,
`delays_residual_program/2`, `get_residual/2`, `abolish_table_pred/1` (with `abolish_all_tables/0` destroying the W tries),
`get_calls/3` and `get_returns/2,3` as the XSB programs use them; `op(900, fy, tnot)` as SWI's `library(tables)` declares it. A
non-tabled caller of an undefined answer succeeds and pushes the answer's own goal on the current delay list, which is what
`call_delays/2` reads (§ 1: `D = p`).

### 3.1 THE TWO DEFECTS OF THE FIXPOINT AS BUILT, AND THE RULING (the cfo's measurements from the XSB delay and WFS entries, 2026-10-25 01:54 CDT; ruled by the cto 08:3x CDT under CEO-1964)

CTO-373 read this page as built; the cfo's four entries show two things that reading did not grade. (1) THE RE-RUN PRINTS EACH SIDE EFFECT PER ROUND: delay_tests_przy1 prints `Negations are OK` three times for swipl's once, abol_susp1 eleven writelns for five, abol_susp2 twenty for eight -- every round of `tbl_rounds` and of `tbl_wfsrun`'s alternating fixpoint RE-EXECUTES the in-progress tables' clause bodies from their first goal, so a side effect before a `tnot` of an incomplete table runs once per round. SLG executes a clause body ONCE per subgoal: a `tnot` (or a positive call) of an incomplete table SUSPENDS the body at that literal and RESUMES it when the table completes or the literal is delayed. (2) THE IN-PROGRESS LIST IS WALKED PER CALL: delay_tests_tabsimp_seq (the tnot ring, N=20000) runs 186 s against swipl's 0.56 s, about N to the 1.7 -- `tbl_pos` (length plus index), `tbl_done`, `tbl_use`'s `var_memberchk` over cell 9 and `tbl_srounds` each walk the header's cell-1 list per event, where swipl keeps the SCC's position in the subgoal frame as a depth number, O(1); and the nesting costs about 6 KB of machine stack per ring element.

THE RULING, two rows under the tabling design row, hq_zetas the builder, one program at a time: (1) SUSPENSION, NOT RE-RUN. A consumer that meets an incomplete table suspends as the parked generator context the engines already are (hq_packages's `rt_proc_call_gen_h` road on its own trail arena, ARCH-PROLOG-THREADS.md § 4 AS BUILT): the body's continuation lives in that context's frame -- the generator box of ARCH-PROLOG-TABLING-BOXES.md holding the clause's continuation -- and the completing table resumes each suspended consumer once per new answer (SLG's answer return) or once with the literal delayed (WFS); the alternating fixpoint iterates over the SUSPENDED consumers and the answers, never over clause bodies, so every side effect runs once as both oracles print it; the delta-seeded monotonic step of ARCH-PROLOG-TABLING-IDG.md § 4 is the same principle on the incremental road. Witnesses: przy1, abol_susp1, abol_susp2, graded by the XsbTests runner against XSB's refs. (2) THE SCC POSITION IS A DEPTH NUMBER IN THE TABLE HEADER, read and written O(1): cell 1's in-progress list goes, the leader and the depth take its place, `tbl_pos`, `tbl_done`, `tbl_use` and `tbl_srounds` become header reads, and a ring element costs a bounded frame, not a 6 KB nesting. Witness: tabsimp_seq under its declared stack within the runner's 60 s, then its instruction count against swipl's. The four entries move from the cfo's row to the tabling design row as its witnesses (the ceo is asked).

## 4. THE XSB LOADER (the gateway row, then the drivers row)

`load_files(M:File, Options)` and `consult/1` at RUN TIME, `if(changed)` remembered per absolute path, `dialect(xsb)` or a `.P`
extension selecting XSB's reading: `:- import _ from _` (ignored -- SCRIP's builtins are global), `:- export`, `:- table`,
`:- dynamic`, `:- op`, `:- index`/`:- hilog`/`:- compiler_options` (ignored), `?- G` and `:- G` run at load time in M.

**Module M without a module system:** SCRIP already names a unit-local or module-local predicate `'M:p'` (the plunit units, the
`'$mod_*'` helpers of d8b598107). The loader reads the WHOLE file first, collects the heads it defines (and its `table`/`dynamic`
declarations), then asserts each clause with every head and every body goal that names a predicate the file defines renamed to
`'M:p'` -- recursing into the meta-arguments of the control constructs, `tnot/1`, `findall/3`, `\+`, `call/N`, `forall/2`,
`setof/3`/`bagof/3`, `assert*/1`/`retract/1` (the clause inside), `get_residual/2`, `abolish_table_pred/1`, `catch/3`. A goal
built at run time (`call(X)`) runs as `call(M:X)`, which resolves `'M:p'` first and the global `p` after (measured: `call(plunit_u2:
xrun(c))` falls back to the user `xrun/1`). A tabled `p/N` of the file gets its wrapper `'M:p'(Xs) :- '$tbl_call'('M:p'(Xs),
'$tbl M:p'(Xs))` asserted once and its clauses asserted as `'$tbl M:p'/N`. `@(M:G, M)` runs `'M:G'`. Delay elements and
`get_residual/2` print a table's goal without its `'M:'` prefix (SWI's `unqualify_goal/3`).

**`source_file/2`:** lower emits `'$src_file'(Name, Arity, AbsPath)` facts for the user predicates -- ONLY when the program names
`source_file/2` (the prelude-closure test, as `term_expansion` already pulls `'$load_item'`), built by LOWER's traversal (CEO-1322;
the file is the statement's `:file` attribute); run-time loads add theirs by `assertz`.

## 5. Roll-out (LARGE CHUNKS, CEO-1721 steps 2-5)

1. Build the whole scheme locally (§ 3 + § 4); pass every relay turn at once while building ("BATON to hq_raku: pass"), landing a
   small ready class on a leg only.
2. THE SMALL ROLL-OUT: `xsb/wfs_tests/xsb_test_wfs.pl` -- the smallest file that exercises `tnot`, undefined answers and the loader
   together (72 cases, 34 undefined golds, no residual printing) -- with its smoke (test_tabling, test_answer_subsumption,
   test_wfs, the ProBench tabled kernels unchanged).
3. THE MASSIVE ROLL-OUT: the other XSB files and test_wfs in large sets, each set behind a file freeze on the tabling prelude and a
   short SCRIP push hold on request (CEO-1707).
4. Lon's ultracode -- the ceo asks him.

## 6. The rows (existing, CEO-1624 classes; DONE-WHENs re-cut onto the SWI runner per file, CEO-1721)

- `prolog-load-files-2-and-source-file-2-load-and-name-a-file-at-run-time-the-xsb-tabling-drivers-need-them` -- the gateway witness
  (a run-time `load_files/2` of a local file and `source_file/2` naming it, both modes).
- `prolog-swi-tabling-the-xsb-loader-runs-the-xsb-test-drivers` -- basic, table, ptq, ai, attv, sub (sub may split, § 7).
- `prolog-swi-tabling-well-founded-semantics-tnot-undefined-and-delays` -- test_wfs, delay, neg, wfs (+ nonmt).
- `prolog-swi-tabling-incremental-and-monotonic-re-evaluation` -- incremental_tests (not this page).

## 7. Not on this page

Call-SUBSUMPTIVE tabling (`:- table p/1 as subsumptive`, xsb sub_tests) is measured after the loader lands and gets its own section
or page if it is a mechanism of its own. Incremental and monotonic tabling, transactions and shared (thread) tables are their own rows.

---

## 8. DESIGN-PLAN: xsb-tabling-wfs -- the XSB test package's tabling families to XSB's own answers: the loader, the reading, the SLG engine on Byrd boxes, delay and simplification as XSB prints them, call subsumption (the cto, 2026-10-28 10:5x CDT, CEO-1996/1998, row `design-prolog-xsb-tabling-with-delay-and-well-founded-semantics-ceo-1998`)

DESIGN-PLAN: xsb-tabling-wfs

The step table is `corpus/tests/prolog/xsb_wfs/STEPS.tsv`; the witnesses are the `.P` programs beside it, XSB syntax, each with a `.ref` cut from XSB 5.0.0 (`xsb_bin()`, ORACLES.md) by XSB's own gentest protocol (`[w]. tell(temp). test. told.`, the answer the file `temp`'s non-empty lines sorted; the wfs kind `[driver]. test(program).`), and the step harness is `harness/scripts/test_design_xsb_tabling_wfs_steps.sh` (`--list` runs nothing; `--step N` runs the step's witnesses in both modes exactly as the package runs an entry -- the package prelude's five lines prefixed, the vendored driver appended, siblings staged beside, `diff -w` against the ref -- then the step's package entries through the harness's own smoke (at most eight, the handful of CEO-1677); `--cut` re-cuts every ref from XSB). The executor is hq_packages; the cfo builds the engine steps (6, 7, 10); the ceo mints one row per step.

### 8.1 The measure (SCRIP e2d5b18cc, results.tsv's latest reading per program, 2026-10-28 10:1x CDT)

**XsbTests: 550 entries graded (357 more are EXCLUDED, NO_ORACLE_ANSWER or no XSB script runs them), 180 PASS, 361 FAIL, 9 HANG in each mode** (the SUITE TABLE's 170/550 is the coo's 10-25 reading at 225a1687c). By family (pass/fail/hang): table_tests 13/70/5, delay_tests 57/27/0, wfs_tests 0/72/0, prolog_tests 22/43/0, incremental_tests 9/51/0, sub_tests 9/28/2, basic_tests 26/2/0, neg_tests 23/1/0, nonmt_tests 3/17/2, ai_tests 11/0/0, retract_tests 0/10/0, constraint_tests 1/9/0, attv_tests 2/8/0, foreign_tests 0/9/0, cdf_tests 0/7/0, float_tests 4/1/0, io_tests 0/3/0, regmatch_tests 0/2/0, json_tests 0/1/0. Of the 370 non-PASS, 209 print NOTHING (the fingerprint of the empty string; 152 with rc 0): an error swallowed by the vendored driver's `catch(ignore(G), E, print_message(error, E))`, a parse refusal, or a goal that fails.

**THE CLASSES, measured one entry at a time with the package prelude prefixed as the harness prefixes it:**
1. **THE RUN-TIME LOADER IGNORES `:- table` IN A CONSULTED FILE.** `existence_error(procedure, (table)/1)`: the directive runs as a goal. Every STAGED entry that consults a sibling program is behind it: the 72 wfs_tests (`test(pNN)` consults `pNN.P`: with the directive honoured, p06 reads EQUAL to XSB's ref; p33, p52, p77, p16 DIFF only because their tables are not tables), the 37 sub_tests (`['Driver']`, `['Programs/traversal', DataFile]`: lrtc1 overflows its stack on the untabled left recursion), and the staged table_tests, incremental_tests and prolog_tests that load siblings (STAGED.tsv: 184 entries).
2. **THE WFS ENTRIES RE-CONSULT THEMSELVES.** The vendoring compiled `pNN.P`'s clauses into the entry and appended `consult(wfs_test), test(pNN)`, whose `consult(pNN)` then asserts clauses of a static predicate: `permission_error(modify, static_procedure, query/5)`. XSB never does that: its script runs `[wfs_test]. test(p06).` -- the driver is the program, the example is loaded at run time. Measured with the entry built that way (prelude + wfs_test.P + `:- initialization((test(p06), told))`, p06.pl beside): p06 EQUAL; the four others wait on class 1.
3. **XSB'S READING.** `tnot` is `op(900, fy, tnot)` in XSB (`current_op(900, fy, tnot)`, measured) and SCRIP's XSB dialect does not declare it: 11 entries write `tnot win(Y)` (test_3vwfs_1 lines 110, 135, 141 refuse). The prelude declares `import`, `export`, `from`, `index` as operators and nothing else: `:- edb hitb/2.` (neg_tests_q7) refuses, `:- index(a/1, 1)` runs as a goal and raises (abol_test3), and the directive census over the 550 reads table 1363, import 581, use_module 479, dynamic 189, compiler_options 38, index 31, set_prolog_flag 23, op 19, auto_table 18 (22 files), writeln 15, ensure_loaded 15, hilog 11, export 9, if/elseif/else/endif 21, mc 5, multifile 4, use_subsumptive_tabling 3, ensure_dync_loaded 3, suppl_table 1 (3 files), edb 1, load_dync 1, load_dyn 1, xsb_flag 1, xsb_configuration 1.
4. **`auto_table` AND `suppl_table` ARE COMPILER DIRECTIVES WITH SEMANTICS** (XSB manual, system.tex 2280-2362): `:- auto_table` tables every predicate of the file that static analysis shows in a cycle of the predicate call graph or called through `tnot/1`; `:- suppl_table(N)` (`suppl_table` = `suppl_table(2)`) tables every predicate with a clause joining N or more `edb` or tabled literals. Today `existence_error(procedure, auto_table/0)` and the untabled left recursion overflows the stack: delay_tests seg1-5, fr1-3, win, dynstrat1/5/6/7, wmay_winbug and the rest of the 22 files.
5. **THE TABLE-BUILTIN SURFACE.** The package uses 29 of the manual's tabling builtins (table_builtins.tex); SCRIP's prelude and dispatch define 14 and lack 15: get_residual_sccs/3,5 (4 files), delete_return/2 (4), variant_get_residual/2 (3), get_calls_for_table/2 (3), explain_u_val/3,6 (3), abolish_nonincremental_tables/0,1 (3), table_state/4 (2), get_scc_dumpfile/1 (2), abolish_table_subgoal/1,2 (2), table_index/2 (1); `truth_value/2` (XSB syslib tables.P) and `timed_call/2` (not tabling: nonmt test_tc, out of this plan) are the two the entries raise first. `get_returns_and_tvs/3` is in the manual and not in XSB 5.0.0 (measured: existence_error).
6. **THE RE-RUN.** `delay_tests_przy1` prints `Negations are OK` three times for XSB's once (the body of `s` re-executed per round of the alternating fixpoint, § 3.1 (1)); abol_susp1 11 lines for 5, abol_susp2 20 for 8; tabsimp_seq (the tnot ring, N=20000) 186 s against XSB's 0.56 s and 6 KB of machine stack per element (§ 3.1 (2)).
7. **DELAY LISTS AS XSB PRINTS THEM.** test_wcs_1's ref carries `answer(t4(a),t4(a),[t4(a),tnot t4(a)])` and `answer(t3(a),t3(a),[t3(a),t3(a)])`: a conditional answer's delay list with POSITIVE delay elements, duplicates kept, `tnot` written as the prefix operator it is; SCRIP prints the ten `answer(...)` lines not at all (the residual pass of § 3 stores one simplified list per answer and never a positive element of an in-progress table).
8. **A CUT OVER AN INCOMPLETE TABLE RAISES.** XSB: `error(table_error, context(context('illegal cut over incomplete tabled subgoal: q(...), from within a call to p_$/3', q(...)), Backtrace))` (measured on test_cut_over_tables.P); SCRIP cuts silently and prints nothing (3 entries catch it).
9. **CALL SUBSUMPTION.** 37 sub_tests run under XSB's `-S` (every table subsumptive; ORACLE_RUNS.tsv's options column), 96 declarations say `as subsumptive`, 3 files say `:- use_subsumptive_tabling`. It is observable: sub_tests_sg1's ref has 8 `same_gen` lines where variant tabling prints 29 (every call instance its own table, the answers repeated); measured on a witness, `get_calls(anc(_,_), C, _)` counts 1 subsumptive table against 4 variant tables, and the subsumed call's answers come in the subsuming table's order.
10. **OUT OF THIS PLAN**, named so nobody waits on it: incremental_tests (60; `as incremental` 124 declarations: hq_prolog's row `prolog-xsb-package-incremental-tabling-programs-equal-swipl` and ARCH-PROLOG-TABLING-IDG.md), prolog_tests 65, retract_tests 10, constraint_tests 10, attv_tests 10, foreign_tests 9, cdf_tests 7, io_tests 3, regmatch_tests 2, json_tests 1, float_tests 1, basic_tests 2 (gpp_test, ensure_loaded_tst), timed_call/2 (nonmt test_tc), the abstraction and size flags (`as answer_abstract` 22, `as subgoal_abstract` 20: hq_packages' rows `prolog-xsb-tables-max-table-flags-...` and `...-call-depth-and-term-depth-abstraction-...`), `lattice` answer subsumption (5: row `prolog-xsb-tables-lattice-answer-subsumption-...`), the abolish family's bookkeeping lines (row `prolog-xsb-package-table-tests-abolish-residual-and-pps-...`), `as opaque` 6, `as intern` 4, `as index` 5.

**THE ORACLE'S SEMANTICS, measured so the engine aims at them.** XSB 5.0.0 here is `engine_mode slg-wam`, `scheduling_strategy local` (`xsb_configuration/2`). On the manual's answer-completion exercise (tables.tex 1292: `ac_p(X) :- ac_p(X). ac_p(_) :- tnot(ac_s). ac_s :- tnot(ac_r). ac_s :- ac_p(_). ac_r :- tnot(ac_s), ac_r.`) XSB 5.0.0 answers `ac_p false, ac_s true, ac_r false`, the well-founded model, and swipl 9.0.4 the same: this build completes answers, so the engine computes the WFS and `as compl_semantics` (31 declarations, test_wcs_*) is the per-table opt-out into Clark's completion semantics (`simple_loop(X) :- simple_loop(X)` answers X unbound as undefined). On § 1's program XSB prints `p - [tnot p]`, `q - [p]`, `s(3) - [tnot n(3)]`, `a - false`, `b - false` (swipl's residuals with `tnot` as an operator), and a top-level query whose answer is conditional prints `undefined`.

### 8.2 The law for this plan

1. **THE ENGINE IS SLG WITH DELAY AND SIMPLIFICATION, LOCAL SCHEDULING, A CLAUSE BODY RUN ONCE PER SUBGOAL.** The alternating fixpoint of § 3 (the phases `0 | t | u | r`, `'$tbl_wfsrun'`, `'$tbl_alt'`, the T and U tries) is the engine AS BUILT and is REPLACED: it re-runs bodies (class 6) and computes truth values the oracle does not print (class 7). What stays from § 3 and ARCH-PROLOG-TABLING-BOXES: the one trailed delay-list cell and its three conditions (§ 3.1), the answer trie with per-answer delay lists, the header box IR_TABLE_HDR and its cells (the state of an evaluation lives in the frame of the box evaluating), the renamed clauses and the wrapper.
2. **A SUSPENDED CONSUMER IS A RETAINED FRAME, NEVER A COPY, NEVER A SECOND STACK.** Its continuation is its box's β; its frame stays on the machine stack above its leader until the leader completes (THE LIFETIME RULE; the retains reason `table consumer` beside `suspend` and `generator callee` in the one retains table); the chain of suspended consumers of a table is threaded through the consumers' own frames from the table header (ARCH-PROLOG-TABLING-BOXES § 3), and the completion chain is the chain of generator headers already there. No `cv_t`, no heap list of continuations, no global.
3. **THE ANSWER IS XSB'S TEXT.** Every delay list prints as XSB prints it (`tnot` an operator, positive elements kept with their duplicates, the order XSB returns); a conditional top-level answer is `undefined`; a cut over an incomplete table is `error(table_error, context(context(Msg, Subgoal), Backtrace))`; the refs are XSB's and the compare `diff -w`.

### 8.3 The rulings

**R1 -- the loader honours every XSB directive of a consulted file.** `consult/1`, `load_dyn/1`, `load_dync/1`, `ensure_loaded/1`, `ensure_dync_loaded/1` and `[File]` at run time read `:- table Spec` (with `as subsumptive | incremental | opaque | intern | index(...) | compl_semantics` and the moded forms), `:- dynamic`, `:- import _ from _` (ignored), `:- export` (ignored), `:- index/1,2`, `:- mode`, `:- edb`, `:- hilog` (ignored), `:- auto_table`, `:- suppl_table`, `:- compiler_options`, `:- set_prolog_flag` and `:- op` exactly as the compile-time road reads them (§ 4's loader is the `load_files(_, [dialect(xsb)])` road; this ruling makes the plain roads the same reader): the loader's directive table is ONE table shared with lower (`pl_decl_directives`), and a directive it does not know is a `print_message(warning)`, never an existence error. The sibling is found under its upstream name or with `.pl` (the staging writes both).

**R2 -- a wfs entry is the program XSB runs.** The vendoring (`util_build_package_suite.py`, kind `wfs` in ORACLE_RUNS.tsv) writes the entry as the DRIVER (`wfs_test.P`'s text) followed by `:- initialization((test(pNN), told)).`, with `pNN.P` staged beside as today; the entry's compiled clauses are the driver's, `pNN`'s are consulted once. The refs do not move (they are XSB's temp, sorted). A corpus landing; the gate `test_gate_xsb_refs_are_cut_from_xsb_and_graded_ignoring_white_space.sh` gains the arm.

**R3 -- the XSB reading.** The XSB dialect's operator table (`'$lf_xops'`, prolog_parse.c 2977, and the package prelude) gains `op(900, fy, tnot)` and `op(1100, fy, edb)`, `op(1100, fy, hilog)`, `op(1100, fy, mc)`; `index/1,2`, `edb/1`, `hilog/1`, `mc/1`, `mode/1`, `auto_table/0`, `suppl_table/0,1`, `use_subsumptive_tabling/0`, `compiler_options/1`, `xsb_flag/2`, `xsb_configuration/2` are directives lower and the loader accept (R1); `ensure_dync_loaded/1`, `load_dyn/1`, `load_dync/1` are `consult/1`. The vendoring writes an XSB run's `-S` as `:- use_subsumptive_tabling.` at the head of the entry (ORACLE_RUNS.tsv's options column, 37 entries), and `-l` (print variables as letters) is already the ref's text.

**R4 -- auto_table and suppl_table are lower's.** After the file's clauses are read, lower builds the predicate call graph of the file (a body literal's name/arity, through `tnot/1`, `\+`, `findall/3`, `forall/2`, `call/N` with a callable literal) and under `:- auto_table` marks TABLED every predicate on a cycle of that graph and every predicate called through `tnot/1`; under `:- suppl_table(N)` every predicate with a clause whose body carries N or more literals that are `edb` or tabled (the graph is recomputed to a fixpoint, since a newly tabled predicate counts). The marking is the same `pl_table_wrapper` renaming a `:- table` declaration makes; the loader (R1) does the same at run time for a consulted file.

**R5 -- THE SLG ENGINE ON BYRD BOXES, local scheduling.** A tabled call site is one box (today's `'$tbl_call'` entry, `'$tbl_get'`, the header IR_TABLE_HDR). At α it finds the variant (or, R10, the subsuming) table and takes ONE of three roles. (a) COMPLETE: it is a trie consumer -- γ per answer with the answer's delay list appended to the current delay list when conditional (an unconditional answer appends nothing), β the next answer, ω when exhausted. (b) NEW: it is the GENERATOR: it opens its header, links it as the newest on the completion chain (the chain of generator headers on the machine stack, oldest the leader), runs the renamed clauses; every answer the body derives at γ is INSERTED into the trie with the current delay list (new or not) and the body is FAILED INTO (local scheduling: nothing returns to the caller until the generator's SCC completes); when the clauses are exhausted the generator either completes (R7) or, being inside an older generator's SCC, suspends as a generator (its frame retained, its consumers chained) and fails back. (c) INCOMPLETE: it is a CONSUMER: γ per answer the trie already holds; when the trie is exhausted it SUSPENDS: its record (the trie cursor of the last answer it returned, the link to the table's next consumer, its forward trail of R6) lives in its own retained frame, the header's consumer chain is pointed at it, and it executes ω -- its frame is NOT released (the planner's retains reason `table consumer`; the ω→β law pops nothing of it, the frame is an RBP activation frame by Lon's TEST 2, reached later by the scheduler through the chain, not by a fixed rsp distance). RESUME: the scheduler enters the consumer's β with rbp at its frame; the consumer returns the next answer from its cursor; its continuation (the rest of the clause body it sits in) runs to the body's γ (an answer for ITS generator, inserted) or to its own ω again (suspend again). A consumer is resumed only while its table has answers it has not returned.

**R6 -- THE FORWARD TRAIL.** When a consumer suspends by ω, the trail unbinds every variable its clause body bound since the consumer's α (older variables: the generator's call, the clause's head variables); on resume those bindings must stand again. The consumer's record carries the FORWARD TRAIL: at suspension the entries of the trail segment between the consumer's own choice mark and the top are copied as (address, value) pairs into a vector owned by the record (one cell of the retained frame; a heap block the frame map visits when its length exceeds the frame's fixed cell -- its lifetime is the suspension's, the frame's); at resume the pairs are rebound and re-trailed; at the next suspension the vector is rebuilt from the new segment. This is the SLG-WAM's forward trail and nothing else: no copying of continuations (SWI's delimited continuations are a term copy; ours is the frame that already exists), no re-execution.

**R7 -- COMPLETION, THE LEADER AND THE DEPTH NUMBER (§ 3.1 (2)).** Every generator header holds `depth` (its position on the completion chain) and `low` (the least depth of any incomplete table a consumer under it read; its own depth when none). A generator whose clauses are exhausted with `low == depth` is a LEADER and completes its SCC (every generator from it to the top of the chain): the FIXPOINT LOOP -- resume every consumer of every table of the SCC that has unreturned answers (R5), in chain order, until no table gained an answer and no consumer has an unreturned answer; then the NEGATIVE suspensions (R8); then SIMPLIFICATION (R9); then every table of the SCC is marked complete, the chain is cut back to the leader's predecessor, and ONE discard restores rsp and rbp to the leader's own frame (every consumer and inner generator of the SCC is younger than the leader: THE DISCARD LAW, a distance from the leader's frame base, never a saved rsp); the leader then returns its answers to its caller as a trie consumer (R5 (a)). `tbl_pos`, `tbl_done`, `tbl_use` and `tbl_srounds` (the cell-1 list walks of § 3.1 (2)) become reads of `depth`/`low`; a ring element costs its one frame.

**R8 -- NEGATIVE SUSPENSION AND DELAY.** `tnot(A)` with A COMPLETE: fails on an unconditional answer, succeeds on no answer, and on only-conditional answers succeeds pushing `tnot A` on the current delay list (today's reads, kept). `tnot(A)` with A INCOMPLETE and A's generator in the current SCC: the caller SUSPENDS NEGATIVELY (a record on A's negative-consumer chain, the same retained-frame shape as R5 (c)) and fails back; A gaining an UNCONDITIONAL answer discards the record (the literal is false; the frame is released at completion); at the SCC's fixpoint with A still incomplete the scheduler resumes every negative consumer of A: with success when A has no answer at all, with success and `tnot A` DELAYED when A has only conditional answers (the WFS's undefined), and the loop of R7 runs again until no resume produced an answer. A positive literal that consumes a CONDITIONAL answer of an incomplete table appends that answer's own delay element (the answer itself, `t4(a)` in class 7) to the current delay list -- positive delays, kept with duplicates, as XSB stores them. `tnot(A)` of a non-ground A raises XSB's instantiation error; `tnot(A)` outside any table (a top-level call) runs A to completion first.

**R9 -- SIMPLIFICATION AND ANSWER COMPLETION.** At completion the SCC's conditional answers are simplified to a fixpoint: a delay element `tnot B` with B complete and unconditional-true is FALSE, so the answer that carries it is deleted; with B complete and no answer it is TRUE, so the element is removed; a positive element `B'` whose answer became unconditional is removed and whose answer was deleted deletes its carrier; a table whose only answers were deleted is empty, which propagates to the consumers of `tnot` of it. Then ANSWER COMPLETION over the SCC: a conditional answer supported only by positive delay elements of conditional answers of the same SCC with no unconditional support (an unfounded positive loop) is deleted (the oracle completes answers: class 10 above), except for tables declared `as compl_semantics`, which keep such answers undefined. `get_residual/2`, `call_delays/2`, `delays_residual_program/2` read the lists as stored; printing is R3's operator.

**R10 -- CALL SUBSUMPTION.** For a predicate tabled `as subsumptive` (or every predicate under `:- use_subsumptive_tabling`), `'$tbl_get'` looks the call up by SUBSUMPTION: a table whose call subsumes the new call (the new call is an instance of it) answers it -- complete: the consumer iterates the subsuming trie, unifying each answer with its call (the subsuming table's order, measured); incomplete: the call is a consumer of the subsuming generator in its SCC (R5 (c)), reading only the answers that unify. No table is created for the subsumed call (`get_calls/3` lists the subsuming one; class 9: 1 against 4). A call that no existing table subsumes creates its own table as a variant would, and a LATER more general call creates a new table of its own (XSB does not retroactively merge). The subsumption test is one-way term subsumption (`subsumes_term/2`) over the call's argument vector, with the trie's call index narrowed by the principal functor.

**R11 -- A CUT OVER AN INCOMPLETE TABLE RAISES.** A `!` whose scope would remove the choice point of a generator or consumer that is INCOMPLETE (a tabled subgoal of the current SCC below the cut's clause) raises `error(table_error, context(context('illegal cut over incomplete tabled subgoal: <Subgoal>, from within a call to <Pred>', Subgoal), Backtrace))` with XSB's message text; a cut over a COMPLETE table's consumer is an ordinary cut. The check is the cut box's: the cut's target depth against the completion chain's newest header (one compare of two frame addresses).

**R12 -- THE BUILTIN SURFACE.** The prelude gains the 15 missing predicates of class 5 as XSB's syslib `tables.P` defines them (semantics, not text): `variant_get_residual/2`, `get_calls_for_table/2`, `get_returns_for_call/2`, `table_state/4` (PredType `variant | subsumptive`, CallType `producer | consumer | no_call_yet`, AnswerSetStatus `complete | incomplete | undefined`), `get_residual_sccs/3,5`, `delete_return/2`, `abolish_table_subgoal/1,2`, `abolish_nonincremental_tables/0,1`, `table_index/2`, `explain_u_val/3,6`, `get_scc_dumpfile/1`, `truth_value/2`.

### 8.4 The steps (`STEPS.tsv`; `test_design_xsb_tabling_wfs_steps.sh --list` prints them)

| step | slug | executor | depends | witnesses (corpus/tests/prolog/xsb_wfs) | package entries (the handful, through the harness smoke) |
|---|---|---|---|---|---|
| 1 | the-loader-reads-table-directives | hq_packages | - | xw01_loader_table (+ xw01_prog) | sub_tests_lrtc1 sub_tests_sg1 |
| 2 | the-wfs-driver-as-xsb-runs-it | hq_packages (corpus) | 1 | xw02_wfs_driver (+ xw02_p33) | wfs_tests_p06 wfs_tests_p33 wfs_tests_p52 wfs_tests_p77 |
| 3 | the-xsb-reading | hq_packages | - | xw03_reading | neg_tests_q7 table_tests_test_3vwfs_1 table_tests_abol_test3 |
| 4 | auto-table-and-suppl-table | hq_packages | 3 | xw04_auto_table xw05_suppl_table | delay_tests_seg1 delay_tests_win delay_tests_fr1 delay_tests_dynstrat1 |
| 5 | the-table-builtin-surface | hq_packages | - | xw06_builtins | table_tests_get_resid prolog_tests_std1 table_tests_test_not3_wcs |
| 6 | one-body-one-run | cfo (R5, R6, R8) | 1 | xw07_once_per_body | delay_tests_przy1 delay_tests_abol_susp1 delay_tests_abol_susp2 delay_tests_ac_tests |
| 7 | the-scc-depth-number | cfo (R7) | 6 | xw08_scc_ring | delay_tests_tabsimp_seq |
| 8 | delay-lists-as-xsb-prints-them | hq_packages (R3, R8, R9) | 6 | xw09_delay_print | table_tests_test_wcs_1 table_tests_test_wcs_simpl delay_tests_dl_dupl delay_tests_asl_dupl |
| 9 | the-cut-over-an-incomplete-table | hq_packages (R11) | 6 | xw10_cut_over_table | table_tests_test_cut_over_tables |
| 10 | call-subsumption | cfo (R10) | 1, 3 | xw11_subsumptive | sub_tests_sg1 sub_tests_decker sub_tests_lrtc1 sub_tests_drtc1 |
| 11 | the-finish | hq_packages records | 1-10 | every witness | every entry of wfs_tests, delay_tests, neg_tests and sub_tests PASS in both modes (results.tsv, read), and the XsbTests row at or above 380 of 550 (SUITES.tsv, read) |

### 8.5 Forbidden

A second stack or a global holding the suspended consumers (CEO-1542: the chains are threaded through the frames; the completion chain is the header chain); copying a continuation as a term; re-running a clause body to re-derive what a suspended consumer holds; a saved rsp for the completion discard (R-C of ARCH-PROLOG-ACTIVATION-LIFETIME § 9.3: the leader's frame base and a distance); grading a tabling entry against swipl (the refs are XSB's, CEO-1927); a witness ref cut from SCRIP; an XsbTests exclusion for a tabling entry the oracle answers (CEO-1696); a per-dialect branch in the emitter (the dialect is lower's and the loader's).

### 8.6 Order

1 and 3 first (the loader and the reading: small, each flips a family's blocker; 1 alone moves the staged entries); 2 (corpus) behind 1; 4 behind 3; 5 any time; then the engine: 6 (R5, R6, R8 in one scheme, rolled out small on the delay_tests witnesses, then everywhere), 7, 8, 9; 10 behind 1 and 3; 11 when the four families read green. The engine steps are the cfo's (CEO-1996: the cfo builds a step the HQ cannot), rolled out LARGE CHUNKS: the scheme whole in a scratch, its smoke the delay_tests witnesses, then the massive roll-out over wfs, delay, neg, sub and table_tests; every landing the Prolog smoke, the eight smokes when it touches the planner or a template, the coo's identity run when it moves a memory-model calculation.
