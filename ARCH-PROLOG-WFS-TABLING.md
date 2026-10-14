# ARCH-PROLOG-WFS-TABLING — WELL-FOUNDED TABLING AND THE XSB LOADER (hq_prolog, 2026-10-14, CEO-1721)

**Status: DESIGN, for the cto's review (CEO-1721 step 1). Nothing below is built yet.** Owner: hq_prolog. Ruling: the ceo,
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
  entry per live call -- the call nesting lives where it always did, on the machine stack. ⛔ **The cto rules this item**: if a
  backtrackable cell holding a list reads as a second stack under CEO-1542, the alternative is an extra argument threaded through
  the renamed `'$tbl p'` clauses by lower.

### 3.2 The surface (SWI's names; the ISO superset adds them, no dialect switch)

`tnot/1`, `not_exists/1`, `undefined/0` (`:- table undefined/0. undefined :- tnot(undefined).`), `call_delays/2`,
`delays_residual_program/2`, `get_residual/2`, `abolish_table_pred/1` (with `abolish_all_tables/0` destroying the W tries),
`get_calls/3` and `get_returns/2,3` as the XSB programs use them; `op(900, fy, tnot)` as SWI's `library(tables)` declares it. A
non-tabled caller of an undefined answer succeeds and pushes the answer's own goal on the current delay list, which is what
`call_delays/2` reads (§ 1: `D = p`).

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
