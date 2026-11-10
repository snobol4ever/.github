# Prolog tabling: the reference

Verified 2026-11-01 against SCRIP 9cb24d2ca (`tabling.pl` and `xsb_tables.pl` read for every predicate named below). Consolidated from ARCH-PROLOG-TABLING-BOXES, ARCH-PROLOG-TABLING-IDG and ARCH-PROLOG-WFS-TABLING, all retired (`.github/RETIRED-ARCH-PAGES.tsv`).

## 1. Well-founded semantics as the alternating fixpoint

- **Phases.** U (overestimate): `tnot(A)` succeeds iff A has no answer in the last T set. T (underestimate): `tnot(A)` succeeds iff A has no answer in the last U set. Positive calls read the current phase. U0 is the ordinary evaluation; then T1, U1, T2, ... until T stops growing (T only grows, U only shrinks). Answers in T are true; in U minus T undefined; the rest false. Answer completion falls out of the construction.
- **The residual pass.** After T is stable, one more U phase runs with the delay list on: a literal consuming an undefined answer and a `tnot` of an undefined goal push a delay element; each answer stores the distinct delay lists it was derived with. This is swipl's residual program with simplification already done.
- **Phases run only when needed**: a stratified or negation-free program completes after phase 0 at no extra cost.
- **The state**: per table, the T and U sets as two tries named in the table's data term; per evaluation, the phase (`'$tbl_ph'`); per derivation, the current delay list, one backtrackable cell (`'$tbl_dl'`) saved and restored by the caller's own frame, never a stack. The prelude's drivers are `tbl_rounds` and `tbl_wfsrun`.
- **The surface** (SWI's names, no dialect switch): `tnot/1`, `not_exists/1`, `undefined/0`, `call_delays/2`, `get_residual/2`, `abolish_table_pred/1`, `abolish_all_tables/0`, `get_calls/3`, `get_returns/2,3`, `op(900, fy, tnot)`. (`delays_residual_program/2` is named by the design and not built.)
- **Ruled 2026-10-25 (the cfo's two measurements)**: re-running bodies per round prints each side effect once per round where swipl prints it once; the cure is SUSPENSION, not re-run: a consumer meeting an incomplete table parks as a generator context on its own trail arena (the `rt_proc_call_gen_h` road) and resumes when answers arrive.

## 2. The incremental dependency graph in full

- The node lives in the table's trie meta term: `d(Goal, Impl, Kind, SemiNaive, W, idg(Kind, Deps, Affects, False, Queue, Forced))`, `Kind` one of `plain`, `incr`, `mono(eager)`, `mono(lazy)` from the declaration (`:- table p/1 as incremental`, `as monotonic`, `as (monotonic, lazy)`). A dynamic predicate declared incremental or monotonic gets a node `dyn(F/N)`.
- Recording edges costs nothing new: the pass's header cell 9 already holds the tables it sliced; at the end of the pass it is written as `Deps` and the reverse edges as `Affects`.
- The surface the tests read: `incr_is_invalid/1`, `incr_propagate_calls/1`, `incr_invalidate_calls/1`, `'$idg_forced'/1`, `'$idg_mono_affects_lazy'/5`, `'$tbl_table_status'/4`, `get_calls/3`, `get_call/3`, `get_returns_for_call/2`.
- Re-evaluation of an invalid table keeps its old answer set until the new one is complete and compares it: equal, and every dependent's falsecount drops and nothing re-runs.
- A moded table re-evaluated drops its aggregate and recomputes it; a changed aggregate is the new answer propagated onward.
- Forbidden: a global list of tables being evaluated or propagated; a worklist anywhere but the machine stack; a new root cell; an answer or dependency outside the trie's meta term; `nb_setval` on a `$tbl_` name; invalidating every incremental table on a change.

## 3. The XSB loader

`load_files(M:File, Options)` and `consult/1` at run time, `if(changed)` remembered per absolute path, `dialect(xsb)` or a `.P` extension selecting XSB's reading (`:- import ... from ...` ignored, since SCRIP's builtins are global; `:- export`, `:- table`, `:- dynamic`, `:- op`; `:- index`, `:- hilog`, `:- compiler_options` ignored; `?- G` and `:- G` run at load time in M). A module-local predicate is named `'M:p'`: the loader reads the whole file first, collects its heads, then asserts each clause with every head and body goal naming a predicate of the file renamed, recursing into the meta-arguments. A run-time goal runs as `call(M:X)`, which resolves `'M:p'` first and the global `p` after. Delay elements and `get_residual/2` print a goal without its `'M:'` prefix.

## 4. Grading

The XSB package runner with `S4E_CHUNK=entry:<name>` (refs compared ignoring white space, the driver appended as XSB's `test.sh` runs it); SWI's `tabling/test_tabling.pl`, `test_answer_subsumption.pl`, `test_monotonic.pl`, `test_monotonic_lazy.pl` and the transaction files through the SWI runner; the tabling handful and `test_smoke_prolog.sh` before every push, all eight smokes for a prelude change (the prelude is parsed for every tabling program).

## 5. DESIGN: tabling-one-engine (CIO-104, the cio 2026-11-10; Lon: "now make a design your mother would be proud of.")

**The design in one sentence.** Every table, of every kind, is evaluated by the one suspend-and-resume scheduler; the round engine is deleted; what makes a table incremental, monotonic, subsumptive or moded is what it REMEMBERS about its evaluation, never HOW it is evaluated.

**Why, measured (SCRIP 679a69764, mode 3, the programs of `/home/resources/progress/TABLING-ONE-ENGINE` before their phase tags; a "body run" is one printed line from inside a rule body).** SCRIP's ANSWERS equal swipl's in every case; the body runs do not:

| table kind, program | body runs, swipl 9.0.4 | body runs, SCRIP | engine today |
|---|---|---|---|
| plain, a 3-cycle | 3 | 3 | scheduler |
| monotonic, two facts added | 4 | 4 | resume clauses |
| incremental, a 3-cycle | 3 | 15 | rounds |
| subsumptive, a 3-cycle then the open call | 4 | 9 | rounds |
| incremental, re-evaluated after an assert and a retract | 10 | 35 | rounds |
| incremental under negation, before and after an assert | 7 | 24 | rounds |

The cause is one fact: `tabling.pl` holds TWO evaluators. Plain and plain-moded tables run on the scheduler (`'$tbl_sl_*'`, the `'$tbl_sl'`, `'$tbl_park'`, `'$tbl_resume_all'` leaves: a consumer of an incomplete table parks and is resumed when answers arrive, so a body runs once). Incremental, monotonic, lazy, subsumptive and kind-moded tables run on the round engine (`'$tbl_get'`, `'$tbl_lead'`, `'$tbl_rounds'`, `'$tbl_eval'`: a body is re-run every round until nothing is new, and three-valued answers come from an alternating fixpoint that re-runs everything again per phase). The ruling of 2026-10-25 (section 1's last bullet: the cure is suspension, not re-run) was carried out for the first group only. Every side effect in a table of the second group is repeated, every such table costs a multiple of its work, and each feature added since (the dependency graph, the transactions, the inspection view of CIO-102) has had to be written against two engines or left blind to one.

**What a kind is, after.** A table is a trie of answers and a record. One evaluator fills it. A kind adds memory, nothing else:

- **plain**: remembers nothing.
- **incremental**: remembers what it read (its edges), and while it is being evaluated again keeps its old answers to compare with the new.
- **monotonic** (eager or lazy): remembers, for each read of a source that can grow, the RESUME CLAUSE the lowerer compiled for the rest of the body (`'$rs NAME#clause.read'`, `lower_prolog.c` `pl_rs_clause`) and the variables as they stood at that read. A new fact runs those clauses with the fact; nothing is evaluated again. This already exists and is already right (the table above); it only stops borrowing the round engine's loop.
- **subsumptive**: a call first looks for a completed table that subsumes it.
- **moded**: joins each answer into an aggregate as it is entered.

**The five laws.**

1. **One body, one run, in every kind.** A consumer of an incomplete table parks; nothing is re-run to find a fixpoint.
2. **An edge is written where the read happens**: on the reading table's own record, at the moment of the read, with the bindings of that moment. Never gathered in a header cell and merged when a pass ends: a parked consumer carries a COPY of its header, so a header cell is a fact of one segment, not of the table; and a list merged after the body has backtracked has lost the bindings made before the read (witness 7 asks swipl what a monotonic table must remember there).
3. **Three-valued answers come from delay lists and simplification in every kind** (`'$tbl_sl_wfs'`, as plain tables do today and as XSB and swipl do). The alternating fixpoint, its phases, its two snapshot tries per table and its re-creation of every table per phase go. Section 1 of this page is rewritten by the deleting step.
4. **A change never evaluates.** It marks (incremental: invalid, and its dependents) or runs resume clauses (monotonic). Evaluation happens at the next call, by the one evaluator. Invalidation, the lazy force, the comparison of the old and new answer sets, revalidation of dependents and the transaction log are untouched by this design: they read and write the record, not the engine.
5. **The dependency on a dynamic predicate is on the CALL that was read, not on the predicate.** A changed clause touches a table only if it unifies with a call of that predicate the table read (swipl, witness 6: retracting `edge(c,a)` re-runs the tables that read `edge(c,_)` and their dependents, and leaves `path(d,_)` alone; SCRIP today invalidates every table that read `edge/2` at all).

**The header cells, after.** Cell 1: the table a generator fills (unchanged). Cell 6: the delta context of a monotonic step, and `all` in every generator, so a table first met inside a resume clause does not inherit the step's delta. Cells 7 and 8: the read position and its maximum, used only by the positional fallback of a monotonic table whose clauses were loaded at run time and have no resume clause. Cell 9: the reading table's kind (a single atom; it was the list of sources). Cells 2 (raise), 3 (phase), 4 (new-answer flag), 5 (dependency depth) fall free; `PL_TBH_CELLS` stays 10 until a later row shrinks the box.

**What is deleted** (the last step; about 130 of the file's 573 lines): `'$tbl_get'` `'$tbl_enter'` `'$tbl_lead'` `'$tbl_eval1'` `'$tbl_eval1n'` `'$tbl_nest'` `'$tbl_dup'` `'$tbl_scc'` `'$tbl_indep'` `'$tbl_srounds'` `'$tbl_upto'` `'$tbl_fin_all'` `'$tbl_depn'` `'$tbl_pos'` `'$tbl_idx'` `'$tbl_dmin'` `'$tbl_done'` `'$tbl_wfsrun'` `'$tbl_alt'` `'$tbl_alt2'` `'$tbl_reset'` `'$tbl_renew'` `'$tbl_count'` `'$tbl_snapw'` `'$tbl_snapins'` `'$tbl_final'` `'$tbl_final1'` `'$tbl_wdrop'` `'$tbl_finvals'` `'$tnot_st'` `'$tnot_u'` `'$tnot_i'` `'$tbl_rounds'` `'$tbl_round'` `'$tbl_eval'` `'$tbl_gshort'` `'$tbl_runs'` `'$tbl_run'` `'$tbl_snap'` `'$tbl_snapat'` `'$tbl_slice'` `'$tbl_use'` `'$tbl_range'` `'$tbl_radd'` `'$tbl_rput'` `'$tbl_rhas'` `'$tbl_fa'`'s phase clause `'$tbl_ph'` `'$tbl_raise'` `'$tbl_w'` `'$tbl_wany'` `'$tbl_wtin'` `'$tbl_add'` `'$tbl_answer'` `'$tbl_aval'` `'$tbl_ucons'` `'$tbl_manswer'` `'$tbl_mcond'` `'$tbl_sget'` `'$tbl_sanswer'` `'$tbl_idg_deps'` `'$tbl_duse'` `'$tbl_inprog'` `'$tbl_abort'` `'$tbl_complete'`, the second and third clauses of `tnot/1`, and the `sn(R,Ps)` context. The step's probe is a census: none of these names occurs in the file.

**What is NOT in this design, each named.** (a) A subsumed call consuming from a subsumer still IN PROGRESS (XSB's sharing): a call with no completed subsumer makes its own table, as today; `sub_tests_decker` decides later whether sharing is worth a step. (b) Keeping parked consumers alive after completion, as swipl keeps continuations: not needed, the resume clauses do that work without copying a stack, and a parked segment is restored at its original stack address, so it cannot outlive its leader. (c) The order in which a completed table's answers are returned (CIO-102's measurement row). (d) An update of a monotonic source made from inside a tabled evaluation: refused or undefined today, unchanged.

**The plan.** `corpus/tests/prolog/one_engine/STEPS.tsv`, `harness/scripts/test_design_tabling_one_engine_steps.sh`; the witnesses `oe1` to `oe7` are SWI-syntax programs, each beside a `.ref` that is swipl's output with its lines sorted (the order of body runs is the engine's business; their number per phase is the law). Every step keeps every guard: the SWI tabling files green today (`test_tabling` 35, `test_wfs` 8, `test_reeval` 8, `test_incr_answer_subsumption` 9, `test_monotonic` 10, `test_monotonic_lazy` 18, `test_transact_incr` 6, `test_transact_mono` 7, `test_transact_mono_lazy` 13, `test_transaction_tabling` 3, `xsb/sub_tests` 36, `xsb/incremental_tests` 7 of 15) and the XsbTests families (`incremental_tests` 19 PASS of 84, `sub_tests` 36, `delay_tests` 80, `wfs_tests` 71, `neg_tests` 24, mode 3, results.tsv of 2026-11-10).

| step | what moves | witnesses | what it changes |
|---|---|---|---|
| 1 | the plan lands: witnesses, table, harness, every probe proven fail-once and pass-once; SCRIP's reading of each witness recorded | all | corpus, harness |
| 2 | incremental tables are evaluated by the scheduler; the edge is written at the read | oe1 oe4 oe5 | `tabling.pl` |
| 3 | a dynamic dependency is the call that was read | oe6 | `tabling.pl` |
| 4 | a monotonic table's first evaluation runs on the scheduler; its step loses its rounds; the resume record is written at the read | oe2 oe7 | `tabling.pl` |
| 5 | subsumptive tables are evaluated by the scheduler | oe3 | `tabling.pl` |
| 6 | the round engine is deleted; section 1 of this page and section 2 of SKILL.md are rewritten | all | `tabling.pl`, this skill |
| 7 | what the round engine was holding up is re-cut: CIO-89's `'$tbl_pos'` row is deleted as not real, CIO-102's limit "tables of the round engine are not on the chain" is struck, `table_tests_test_sdg_preds` joins step 15 of xsb-tabling-wfs | none | rows |

**Step 2 in full (the pattern the others follow).** (a) `'$tbl_sl_get'` takes the kind: a new table's record is `idg(TK,[],0,[],Fo)`, with `Fo` the atom false, or `old(T0)` when an invalid incremental table is being evaluated again (its old trie kept for the comparison, exactly as `'$tbl_enter'` keeps it today). (b) `'$tbl_kcall'(G,I,incr)` is the plain clause with that kind. (c) `'$tbl_sl_gen'` owns cell 6 as `all` and cell 9 as the kind. (d) `'$tbl_dep'(Source)`: when cell 9 is not `plain`, add Source to the Deps of the table in cell 1 unless it is there; called by `'$tbl_sl_read'`, `'$tbl_sl_mread'` and the two reads of `tnot` when the table read is not plain, and by `'$tbl_dcall'` in place of `'$tbl_duse'`. While the round engine still stands, a cell 9 that holds a LIST is a round header and takes the source the old way; that branch goes in step 6. (e) After `'$tbl_sl_plain'` at the completion of an SCC, each of its tables runs `'$tbl_cmpl'` (the comparison with the old answers, the revalidation or the dirty mark of dependents) and logs `evald` for a transaction. (f) `tnot` of an incremental table takes the scheduler's road (`'$tbl_sl_ncall'` with the kind). (g) `'$tbl_mcall'` with kind `incr` takes the scheduler's moded road with the kind. (h) `'$incr_guard'` finds a table in progress by its status in the variant table, not by the round engine's list.

**The risks, each with the reading that would show it.** (1) The comparison must see final answers: `'$tbl_cmpl'` after simplification, never before (`test_reeval`). (2) Old and new answer sets compared across the two three-valued constructions during the migration: an incremental table evaluated by rounds before step 2 and by the scheduler after is never compared with itself, since no table survives a rebuild. (3) A generator that owns two more cells costs two stores per table call; the instruction count of the tabling benchmarks is read before and after step 2 (skill `speed-measurement`), and the body-run table above says which way it moves for the other kinds. (4) If a guard file loses a case, the step does not land: the case's first differing line comes to the cio by telegram, never patched around.
