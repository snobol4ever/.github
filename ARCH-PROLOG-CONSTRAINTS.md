# ARCH-PROLOG-CONSTRAINTS — CLP(FD) FINISHED, CLP(Q) AND CLP(R) VENDORED, CHR LOWERED: THE CONSTRAINT SUB-SYSTEMS OVER ONE ATTRIBUTED VARIABLE (the cto, Fable 5.1, 2026-10-24 21:1x CDT, CEO-1960/1964)

**Status: DESIGN OF RECORD. Nothing below is built yet except what § 0 measures as standing.** The cto designs, a builder the ceo names builds one
program at a time (CEO-1964); this page is the row `prolog-the-constraint-sub-systems-clpfd-finished-clpqr-and-chr-designed-by-the-cto-and-built-ceo-1960`'s
design. It stands on `ARCH-PROLOG-CLPFD.md` (10-10: the attributed variable as a flagged self word in a two-DESCR heap block, the wake word a trail
offset, the probe placed by the lowerer, hooks by module, the library vendored verbatim under CEO-1473) and adds nothing to that mechanism: every
constraint system below is Prolog over that one attributed variable. The oracles are swipl 9.0.4 (`library(clpfd)`, `clpq`, `clpr`, `simplex`, `chr`)
and gprolog (the GNU FD spelling).

## 0. The population and what stands (measured 2026-10-24 20:5x CDT, `results.tsv`, the latest m3 reading per program)

| population | count | standing |
|---|---|---|
| ProPuzzles programs loading `library(clpfd)` | 400 of 415 graded | 251 are EXCLUDED as `OUTSIDE_CLPFD` (Lon, CEO-579: *"Do not count the FD as failures for us"*; CEO-1593), yet the harness grades them: **220 PASS, 27 FAIL, 3 HANG, 1 OOM**. The other 149: 146 UNGRADED (`ORACLE_REFUSES`: the hakank_sicstus dialect swipl refuses; `NEEDS_DRIVER`), 1 PASS, 1 FAIL (`hakank_swi_shifted_division`). |
| the 31 red excluded CLP(FD) programs | 31 | HANG: hidato, stable_marriage, sudoku. OOM at the 128 MB cap: euler27. FAIL rc 0 (wrong or missing output): clock_triplets, euler10, euler13, euler24, euler40, extract_from_indices, farmer2, fill_in_the_squares, furniture_moving, futoshiki, isbn, labeled_dice, quasigroup_completion, queens, schedule1, sicherman_dice. FAIL rc 1 (an error): ackermann, euler12, euler14, euler21, euler23, euler37, euler44, euler45, euler47. |
| the GNU FD examples, `corpus/packages/prolog/gnu_fd` | 30 programs, `ALL.csv` with `--dialect=gnu` | NO `.ref`, no runner, no SUITE TABLE row: `lib_inventory.sh` names it the one DEFERRED population. The GNU spelling itself landed (the cfo's CEO-1596 row, DONE). |
| `library(clpfd)` in SCRIP | `prelude/clpfd.pl`, 7,903 lines | SWI's library verbatim (CEO-1473), its operators imported at the directive, the three CEO-1596 witnesses equal to swipl (DONE). The puzzles above run on it. |
| ProRosetta reds touching a constraint library | 14 of 51 red programs | clpfd: 10001th-prime, 100-doors-1, 100-doors-2, bulls-and-cows-player-1, catamorphism-5, nonogram-solver-1 and others; CHR: 6 (below); `library(clpq)`: old-russian-measure-of-length-1; `library(clpr)`: orbital-elements; `library(simplex)`: the four knapsack programs (continuous, unbounded, 0-1-2, bounded-2). |
| SWI attvar and coroutining | `attvar/test_attvar` 16/16, `test_call_residue_vars` 36/36, `test_dif` 48 (+2 `cyclic` UNGRADED), `core/test_coroutining` 20 of 24, `library/test_when` 0 of 6 | the reds: `when:nested_ground` x3 (a nested `ground/1` disjunction's frozen form must read `=@=` the original `when/2` term under `copy_term/3`), `coroutining:frozen` (`frozen/2` must report every goal as `freeze(V, M:G)` once, de-duplicated and module-qualified), `coroutining:when4_inf`. |
| CLP(Q/R) in the corpus | 5 programs | `swi_tests/clp/linprog.pl` (clpr; a module program, never graded), puzzles `hakank_swi_spreadsheet` and `hakank_swi_mortgage` (clpr, FAIL), rosetta `old-russian-measure-of-length-1` (clpq, FAIL), `orbital-elements` (clpr, FAIL). SCRIP has NO clpq/clpr. |
| CHR in the corpus | 8 programs, 1-11 rules and 1-3 constraints each | rosetta hofstadter-figure-figure-sequences-1, hailstone-sequence-5, power-set-3, ethiopian-multiplication-3 and -4, greatest-subsequential-sum-1 (FAIL), integer-sequence-2, abc-problem-2 (UNGRADED). SCRIP has NO CHR. |
| `library(simplex)` in the corpus | 4 rosetta knapsack programs, all FAIL | SWI's `clp/simplex.pl` is 1,580 lines of plain Prolog over rationals (111 mentions of rational arithmetic; no attributes). SCRIP's rationals: `swi_tests/rational` 130 of 130. |

## 1. CLP(FD): what is left is not the solver

The solver is SWI's own library and 220 of the 251 "outside" programs already answer as swipl. What is left is four things, none a new mechanism:

1. **RE-ADMISSION, a ruling for Lon.** `OUTSIDE_CLPFD` was cut when SCRIP had no FD (CEO-579). CEO-1696 says a program that becomes answerable returns to the
   denominator in the landing that gives it its answer. 220 programs are answerable today and read PASS; the 31 reds are debt SCRIP owes on a library it ships.
   The ceo puts to Lon: retire the `OUTSIDE_CLPFD` class, return the 251 to ProPuzzles' denominator (`EXCLUDED.tsv` loses its 251 rows, `util_suite_partition.py build`
   on `ALL.csv` in the same landing), and the 31 become rows. Until Lon rules, the 31 are worked as rows anyway: they are the measurement.
2. **THE 31 REDS, one program at a time**, each bracketed against swipl (`monitor_run.sh --oracle`, swipl under `MONITOR_PL_ORACLE=swipl`) before its cure:
   the three HANGs first (hidato, sudoku and stable_marriage are `all_distinct`/`all_different` propagation over a grid or a matching: a propagation loop that
   does not reach its fixpoint, or reaches it in a time swipl does not take -- measured, never guessed, since the vendored propagators are swipl's own and a
   hang there is SCRIP's engine, not the library); the OOM (euler27 at the 128 MB cap: a labeling search's live set, or a missing safe point, in that order,
   CEO-1101 clause 6); then the sixteen rc 0 and the nine rc 1. Every cure lands in the engine (`src/`), the prelude's non-library part, or a declared
   `heap_kb`; the vendored `clpfd.pl` is never edited (the sync gate).
3. **THE COROUTINING FIDELITY ROWS** (9 cases): `frozen/2` reports `freeze(V, M:G)` per goal once; `when/2`'s residual form; `when4_inf`; `dif:cyclic`.
   They are `ARCH-PROLOG-CLPFD.md` § 4's library (`freeze`, `dif`, `when` vendored over the four attvar leaves), so each is a prelude fix graded by its case.
4. **THE GNU FD SUITE OPENS**: refs cut from `gplc` for the 30 `gnu_fd` programs (`build_official_oracles.sh` has gprolog), a runner key (`gnu-fd`) in
   `lib_inventory.sh` and `s4e_test_request.sh --suites`, a SUITE TABLE row; the coo opens it (CEO-1342: the coo alone writes the table), the programs are then
   debt like any other. ARCH-PROLOG-CLPFD § 5.3's spelling layer is what they run on.

**Refused for CLP(FD)** (ARCH-PROLOG-CLPFD § 5.4, § 7 stand): a native C or asm propagator; a second attributed-variable mechanism; editing the vendored library.

## 2. CLP(Q) and CLP(R): vendored verbatim, two instances of one shared core

SWI's `library(clpq)` and `library(clpr)` are 13,192 lines of plain Prolog in `clp/clpq.pl`, `clp/clpr.pl`, the shared `clp/clpqr/` (`itf`, `geler`, `dump`,
`class`, `project`, `redund`, `ordering`) and the parallel pairs `clpq/{bv_q,nf_q,ineq_q,store_q,fourmotz_q,bb_q}` and `clpr/{bv_r,nf_r,ineq_r,store_r,
fourmotz_r,bb_r}`: 419 attribute sites (`put_attr`/`get_attr`/`del_attr`, module-keyed `clpqr_itf`, `clpqr_geler`, `clpqr_class`, ...), 7 global-variable sites
(`b_setval`/`nb_setval`), no `term_expansion`. The design is the CLP(FD) one applied twice:

- **Vendor under CEO-1473** (verbatim, parsed only for a program naming an export, helpers renamed by the reader, the sync and cost gates) as THREE prelude
  libraries: `clpqr` (the shared core), `clpq` (its `_q` files folded in), `clpr` (its `_r` files). A program names one of `clpq`/`clpr`; the two are never
  loaded together (swipl refuses that too). The attribute module names (`clpqr_itf` and the others) are the `attr_unify_hook` keys of ARCH-PROLOG-CLPFD § 4.
- **The operators arrive with the directive** (ARCH-PROLOG-CLPFD § 5.1): `{}/1` is already a curly term; `clpq` and `clpr` declare no operator the base
  grammar lacks.
- **CLP(Q) runs on SCRIP's rationals** (`swi_tests/rational` 130/130, `prefer_rationals` honoured): `rdiv`, `rational/1`, `rationalize/1` are the arithmetic it
  needs and has. **CLP(R) runs on floats** with swipl's `clpr` epsilon handling as vendored.
- **`library(simplex)`** (1,580 lines, rationals, no attributes) is vendored the same way as a fourth library; the four knapsack programs are its witnesses.
- **What a builder measures first:** `linprog.pl`, `mortgage`, `spreadsheet`, `old-russian-measure-of-length-1`, `orbital-elements` against swipl in both modes;
  the libraries' own `dump/3` output format (`{X=2*Y+1}`) is the oracle's.

**Refused:** a SCRIP-written linear solver; a shared `clpqr` loaded twice under two module names (one instance, the program picks Q or R); editing the
vendored files to fit the flattener -- a flattening defect is a row on the flattener.

## 2b. CLP(B): vendored verbatim, BSD, no licence question (hq_snobol4's TreallaTests issues_test0338 and issues_test0369, 2026-10-25; ruled by the cto 08:4x CDT)

swipl's `library/clp/clpb.pl` is Markus Triska's, copyright 2014-2018 under the BSD-2 terms every other SWI library carries (its header: redistribution in source and binary forms with the two conditions), NOT the GPL that `clpq`, `clpr` and the `clpqr` core carry (`license(gpl_swipl)`, the question before Lon). It is vendored VERBATIM through the library road § 2 built (one library file, the `<lib>:<name>` private keys, the dialect flag it reads), nothing rewritten; `sat/1`, `taut/2`, `labeling/1`, `sat_count/2` are its exports; its attributed-variable and `attr_unify_hook` roads are the ones CLP(FD) already exercises. BUILDER: hq_snobol4, whose two Trealla entries are the witnesses (all three solutions of `sat(X*Y + X*Z)` under `labeling`; `sat(A+B), A=B` giving `A=1, B=1`), one program at a time against swipl 9.0.4, the Prolog smoke before the push; a defect the vendored text exposes in SCRIP's attributed-variable road comes back here as a row with its bracket, never as a patch to the library.

## 3. CHR: the LOWERER translates the rules; the store is the vendored runtime over attributed variables

SWI's CHR is `chr.pl` (632 lines: a `term_expansion` driver), `chr/chr_runtime.pl` (1,016 lines: the constraint store as attributed variables per variable
plus a global store, suspensions, the propagation history, `chr_show_store`) and `chr/chr_translate.pl` (25,423 lines: the compiler, itself written in CHR and
bootstrapped, with 15 helper files). The corpus has 8 CHR programs of 1-11 rules.

- **NOT vendored: the translator.** 25,423 lines of bootstrapped CHR running through the runtime loader's `term_expansion` road (ARCH-PROLOG-TABLING-IDG § 8b)
  to compile eleven rules is a cost gate's refusal before it is a design, and a CHR program is SOURCE: its rules are constructs the parser recognises and the
  LOWERER places (A PARSER MOVES NOTHING; THE LOWERER PLACES IT; LANGUAGE IDENTITY STOPS AT LOWER).
- **The grammar:** `:- chr_constraint c/1, d/2.` (with optional modes and types), `:- chr_type`, and the three rule forms `Name @ H <=> G | B` (simplification),
  `H ==> G | B` (propagation), `H1 \ H2 <=> G | B` (simpagation), with `@`, `<=>`, `==>`, `\`, `|` at SWI's priorities; `pragma passive`. The parser builds the
  pruned parse tree of each rule; nothing is desugared there.
- **The lowering (`lower_prolog_chr.c`) is the standard refined-operational-semantics scheme** (Holzbaur and Frühwirth; Schrijvers' occurrence compilation): for
  each constraint `c/N`, one Prolog predicate `c/N` whose clauses are its OCCURRENCES in textual rule order -- each occurrence clause looks up partner constraints
  in the store (through the variables' suspension lists when a shared variable exists, through the global store otherwise), checks the guard under
  `\+ \+` with no bindings, checks the propagation history for `==>`, removes the simplified heads, and runs the body; the last clause SUSPENDS the constraint
  (allocates its suspension, attaches it to its variables' attribute lists, adds it to the global store) and succeeds. Reactivation on a binding is the
  attributed variable's `attr_unify_hook` for module `chr` -- ARCH-PROLOG-CLPFD § 3's wake-up, no second mechanism. The lowering emits ordinary Prolog
  clauses into the program tree (as `pl_table_rewrite` does for tabled predicates) that call the runtime's primitives; the emitter never sees CHR.
- **The runtime is `chr_runtime.pl` vendored** for its store primitives (`'chr sbag_member'`, suspension records, `chr_show_store/1`, the history), with its
  `nb_setval` global store on one registry root cell (`'$chr_store'`, trailed through `b_setval`, CEO-1542's single current-X cell: a list on the heap rooted
  there). Where the vendored runtime assumes its own translator's data layout, the lowering produces that layout; the file stays verbatim.
- **Order:** the 8 programs, smallest first (`integer-sequence-2`: 1 rule, 1 constraint; `abc-problem-2`; `power-set-3`; `hailstone-sequence-5`; the two
  ethiopian; `hofstadter`; `greatest-subsequential-sum-1`), each against swipl in both modes; the program's `chr_show_store` output is part of the ref where
  the program prints it.

**Refused:** the bootstrapped translator in the shipping road; running the translator at run time through `'$lfx_*'` as the shipping road (a measurement
instrument at most); a C-side store; a global that holds the store without a root cell.

**§ 3 ANSWERS TO hq_runtime BEFORE lower_prolog_chr.c (2026-10-25 08:3x CDT):** the graded CHR population is six (integer-sequence-2, abc-problem-2 and hailstone-sequence-5 are NO_ORACLE_ANSWER: swipl prints nothing). (1) THE LAYOUT: mirror swipl's DEFAULT translation FIELD FOR FIELD -- the global-list stores `$chr_store_global_list_user____<name>___<arity>` newest first, the `suspension(Id, State, _, Generation, Continuation, Name, Args...)` record, the per-variable `v(Mask, L1..Ln)` attribute with one suspension list per constraint, the occurrence clauses `<name>___<arity>__<k>` with partner loops by member, `attr_unify_hook`'s merge and re-run, `$enumerate_constraints/2` and `$chr_initialization/0` -- with every debug event and the debugging branch left out (the six run with debug off) and none of the translator's optimisations (no hash stores, no guard simplification): the store ORDER is part of the printed answer (power-set-3's `find_chr_constraint` order), so a leaner layout is a divergence waiting for its program; an optimisation lands only when a measured program needs it and the refs still agree. (2) THE VENDORING of chr_runtime.pl, as listed: an INCLUDES table that splices an included file's `op` directives and refuses anything else (chr_op); library(dialect/hprolog) as its own library; the `user:goal_expansion` clauses dropped (the expanded predicates exist as ordinary predicates); the `user:exception/3` undefined-global hook through the existing library exception/3 root; the two initialization goals kept; `locked:attr_unify_hook` dropped while only check_guard_bindings reads it. All six one program at a time, the Prolog smoke before each push.

**§ 3 SECOND ANSWER TO hq_runtime (2026-10-28 11:3x CDT): NO GENERIC ENGINE; THE OCCURRENCE CLAUSES COME FROM A FIXED SHAPE FAMILY.** STEP 0, found and landed by hq_runtime (SCRIP d4b6b366d, harness f55b0b8): the rule lines died in the clause reader at priority 1199 because `library(chr)` exports `op(1200, xfx, @)`; a user-declared infix operator of priority 1200 now makes a top-level fact of that functor as swipl reads it, and the pass sees power-set-3's rules as one TT_CHOICE keyed @/2. THE QUESTION (hq_runtime measured swipl's debug-off translation of the smallest graded program at about 400 clause lines and sized the C that reproduces it for six programs at about 1,500 lines; may the occurrence part be one generic engine in SCRIP's own library(chr), about 200 lines of Prolog over the same layout, matching heads one way against one fact per rule at run time?): NO. An engine that walks rule facts and loops partners at run time is a dispatch loop over rule terms, the runtime interpreter ARCH-ENGINE forbids (NO RUNTIME INTERPRETER: a goal known at compile time is compiled; a dispatch loop over runtime terms is walking by another name); the rules are source, known at lowering, and are compiled. THE REFINEMENT the sizing finding earns: the occurrence clauses are not hand-built node by node in C; they are GENERATED FROM A FIXED SHAPE FAMILY carried ONCE as Prolog clause templates with holes (the constraint name and arity, the occurrence index, the argument positions, the partner list) -- per occurrence: the head role (kept or removed), the partner lookups (through a shared variable's suspension list when one exists, else the global list, newest first), the guard under `\+ \+` (no line when absent), the history check for propagation rules only, the removals, the body; simpagation's two same-constraint heads merged into one clause pair with a shared loop, as swipl's translator merges them; the attach analysis (which arguments a constraint attaches: those matched against a pattern) a lowering pass. The templates are the two hundred lines hq_runtime counted, instantiated per occurrence by one walk at lowering; the generated program is ordinary Prolog compiled to boxes; nothing runs over rule data at run time; the printed order (the store newest first, the textual firing order of the refined semantics) is reproduced by construction. power-set-3 first.

## 4. Order of the build and who measures

1. The ceo asks Lon the re-admission ruling (§ 1.1). 2. The 31 CLP(FD) reds and the 9 coroutining cases, one program at a time, by the builder the ceo names
(hq_prolog for the engine, hq_packages for the library), the three HANGs first. 3. The GNU FD suite opened by the coo. 4. CLP(Q/R) and simplex vendored
(hq_packages: the CEO-1473 scheme is theirs), five witnesses plus the four knapsacks. 5. CHR lowered (a builder under the cto's review), eight programs. Every
push after the Prolog smoke (CEO-1928); a change to the prelude regenerates `prolog_prelude_libs.inc` first (the generator, not the Makefile); requests to the
coo name at most 8 programs.

## 5. What this page forbids

A second attributed-variable representation or wake mechanism beside ARCH-PROLOG-CLPFD §§ 2-3; a native propagator or solver in C or asm; editing a vendored
library; a global holding a store or a history without a root cell; the CHR translator vendored or run at load as the shipping road; a `--compat`-style switch
between dialects (the superset grammar accepts both, the oracle per dialect grades).
