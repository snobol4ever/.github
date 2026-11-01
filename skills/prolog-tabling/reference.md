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
