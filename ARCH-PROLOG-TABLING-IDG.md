# ARCH-PROLOG-TABLING-IDG — THE INCREMENTAL DEPENDENCY GRAPH: INCREMENTAL, MONOTONIC (EAGER AND LAZY), TRANSACTIONS AND ANSWER SUBSUMPTION OVER THE THREE ZETAS (the cto, Fable 5.1, 2026-10-24 18:4x CDT, CEO-1960)

**Status: DESIGN OF RECORD for the tabling sub-system beyond the header. Nothing below is built yet.** Lon, in-chat to the ceo, 2026-10-24 17:4x
CDT, verbatim: *"Maybe we could get CTO seated as Fable 5.1 high to do the design work?"* · *"I promoted CTO."* (CEO-1960: the cto holds design
authority for tabling, constraints and engines; the cfo keeps placement and the activation lifetime). This page keeps `ARCH-PROLOG-TABLING-BOXES.md`
§§ 1-3 (WHERE an evaluation's state lives: the header of the box doing it) and `ARCH-PROLOG-WFS-TABLING.md` § 3 (the fixpoint over rounds, the
alternating fixpoint, the residual pass) as they stand, and adds the graph those two pages do not have: WHICH tables depend on WHICH tables and
dynamic predicates, and what a change to a dynamic predicate does to them. The meaning reference is SWI-Prolog 9 (`/usr/lib/swi-prolog/boot/tabling.pl`,
2314 lines, the monotonic section at 1530-1760 and the incremental section after it; `boot/syspred.pl` 1591 for `transaction/1`); the refs are swipl's.

## 0. The population (measured 2026-10-24 18:2x CDT, `results.tsv`, the latest m3 reading per case)

SWI `tabling/` and `xsb/`: 381 PASS, 72 FAIL, 5 CRASH, 3 HANG, 25 UNGRADABLE, 13 UNGRADED. The reds by file and by what each needs:

| file | red | needs |
|---|---|---|
| `tabling/test_monotonic.pl` | 10 (pa1 pa2 pb closure closure2 incr_mono x2 nested_reeval_mono twice_invalid incr_propagate) | § 2-4: the IDG, eager monotonic, `incr_is_invalid/1`, `incr_propagate_calls/1` |
| `tabling/test_monotonic_lazy.pl` | 15 | § 5: lazy queues, forcing, `'$idg_forced'`, `'$idg_mono_affects_lazy'` |
| `tabling/test_transact_mono.pl`, `test_transact_mono_lazy.pl`, `test_transact_incr.pl` | 7 + 13 + 6 = 26 | § 6: `transaction/1`, `snapshot/1` (defined NOWHERE in SCRIP today: the meta table of `prolog_lower.c` names them, nothing implements them) |
| `tabling/test_incr_answer_subsumption.pl` | 9 | § 7: moded tables under § 3-5 |
| `tabling/test_reeval.pl` | 5 CRASH (dynamic_tabled wfs: signal 11 both modes) | § 9: a bug row first (a predicate both tabled and dynamic, incremental, with `tnot`) |
| `xsb/incremental_tests` | 7 | § 3 (incr_depends, inc_switch, sound_updates, abolish_nonincremental, atc_gc_tricky, romero) |
| `xsb/table_tests` | 4 FAIL (pps, 3vwfs, cyclic_tabling, maxans_decl) + 3 HANG (negcycle, tda, tda_i) | § 9: the hangs are WFS scheduling, the WFS page's |
| `tabling/test_trie.pl`, `test_trie_attvars.pl` | 24 + 12 | § 9: the trie API surface, its own row, not this design |
| `test_shared_units` 1, `test_tabled_shortest_path` 1 UNGRADABLE, `xsb/delay_tests` 1 UNGRADED | 3 | read per case when reached |

XsbTests (the package of its own, graded through the XSB loader): 160 PASS, 393 FAIL, 4 CRASH, 3 HANG, 339 UNGRADED in `results.tsv`; the SUITE TABLE row is the
denominator of record. ProPuzzles `p4_binary_trees` FAIL both modes (`:- table minNodes/2`), `p7_miscellaneous` HANG both modes (`:- table factorial/2`).

**What exists, read:** `src/parsers/prolog/prelude/tabling.pl` (298 lines) has no monotonic, lazy, transaction or snapshot clause. Incremental is
`'$tbl_icall'` recording a tabled functor as `'$tbl_incrp'(F/N)` and `'$incr_inval'` marking EVERY incremental table invalid on ANY change: no graph,
right answers, wrong `incr_is_invalid` (which the tests read per table) and no monotonic propagation at all. hq_zetas' aca5f8246 (`pl_incremental_dynamics`
in `prolog_parse.c`) hooks plain `assert*`/`retract*` on a functor declared `as incremental` to that invalidation, statically, with three limits it named:
whole-table invalidation, a variable clause argument is not hooked, `predicate_property(_, incremental)` is a compile-time constant. The table store is the
trie (`rt_pl_trie_meta_set/get`, `unification.c` 3962: meta slots 0 and 1, non-backtrackable). The header has `TABLE_HDR_CELLS` = 10 (`IR.h` 35; the runtime's
`PL_TBH_CELLS`): cell 0 the bank, cells 1-9 all owned (TABLING-BOXES § 3). `assert/2` with a clause reference and `erase/1` exist (`test_monotonic` pa2,
`prelude/gensym.pl`).

## 1. The rule: what lives where (THE LIFETIME RULE, the three zetas, CEO-1542)

- **THE ANSWERS AND THE GRAPH outlive every call that made them: HEAP.** A table's node, its dependencies, its dependents, its falsecount, its lazy
  queues live in the table's own trie meta term (slot 1, `d/5` today, `d/6` below), rooted as the trie is, off the variant table. A dynamic predicate
  declared incremental or monotonic gets a node of its own the same way (§ 2).
- **AN EVALUATION OR A PROPAGATION IN PROGRESS lives exactly as long as the box doing it: THE HEADER (ACT frame)**, TABLING-BOXES §§ 1-3 unchanged:
  the delta context of a monotonic step is a value of cell 6, the sources a pass consumed are cell 9, both already the header's.
- **A TRANSACTION is an activation.** Its UNDO LOG is a heap list rooted from a spine local of the `transaction/1` activation (§ 6, the cfo's placement
  ruling of 19:1x: no header cell), found by every change through ONE trailed current-transaction root cell, which the transaction banks in its own cell.
- **STANDING:** `'$tbl_cur'` and, with § 6, `'$tx_cur'` beside it: two single current-X cells (CEO-1885 (b)), never a stack. **No new global, no new root cell, no second stack**: the propagation
  worklist is the recursion of `'$tbl_mono_step'` on the machine stack (depth-first, SWI's `pdelim` shape), the lazy queues are heap lists on the graph's
  edges, nothing anywhere holds one entry per live call or per live evaluation. TABLING-BOXES § 5's `grep -rF "setval('\$tbl_" src` stays 0.

## 2. THE IDG: nodes and edges

**The node.** Slot 1 grows from `d(G, I, K, Sn, W)` to `d(G, I, K, Sn, W, idg(Kind, Deps, Affects, False, Queue, Forced))`:
`Kind` = `plain | incr | mono(eager) | mono(lazy)` from the declaration (`:- table p/1 as incremental`, `as monotonic`, `as (monotonic, lazy)`; the lowerer
already routes a tabled call to `'$tbl_call'`, `'$tbl_icall'` or `'$tbl_mcall'` by the declaration, `pl_table_wrapper`); `Deps` = the sources this table
consumed (tables and dynamic nodes); `Affects` = the tables that consumed it; `False` = SWI's falsecount (the node is invalid iff `False > 0`; slot 0's
`invalid` stays the flag today's `'$tbl_valid'` reads); `Queue` = `[Src-Answers, ...]`, the deltas a lazy table has not run yet; `Forced` = `true` after a
lazy table was forced (`'$idg_forced'`). Every write is `'$trie_meta_set'` (heap, non-backtrackable: a table's graph survives backtracking as its answers do).

**The dynamic node.** A functor declared `as incremental` or `as monotonic` (or `dynamic([..], [incremental(true)])`, or both) gets a node `dyn(F/N)` with
`Kind` = `incr | mono` and `Affects`; today's `'$tbl_incrp'(F/N)` facts become these nodes and hq_zetas' `'$tbl_isincr'` reads them.

**Recording edges costs nothing new.** `'$tbl_eval'(T, N)` already opens a header owning cells 6-9 and `'$tbl_use'(S)` already records in cell 9 every
table S the pass sliced (the semi-naive bookkeeping). At the end of the pass cell 9 IS `Deps`: write it into T's node and add T to each S's `Affects`
(set union). A call to a dynamic predicate declared incremental or monotonic reaches the graph through **`'$tbl_dcall'(G)`**, a lowerer rewrite at every
call site of such a functor — the symmetric twin of hq_zetas' assert/retract rewrite, with the same static limit (a variable goal is not hooked, named):
under a current header it does `'$tbl_use'(dyn(F/N))`, then calls G honouring the delta context (§ 4).

**The surface the tests read**, all over the node: `incr_is_invalid/1` (`False > 0` or slot 0 `invalid`; missing today), `'$idg_forced'/1`,
`'$idg_mono_affects_lazy'/5` (enumerates `Queue`: `Dst, Src, Dep, DepRef, Answers`), `incr_propagate_calls/1`, `incr_invalidate_calls/1` (§ 4),
`'$tbl_table_status'/4`, `get_calls/3`, `get_call/3`, `get_returns_for_call/2`, `abolish_all_tables/0` (exist).

## 3. INCREMENTAL: invalidation and re-evaluation

**The one change entry** `'$tbl_dchange'(Action, Head)` replaces `'$incr_inval'`: hq_zetas' rewrite, `incr_assert*`, `incr_retract*`, `erase/1` on a
declared functor and `incr_invalidate_calls/1` all enter here. For the dynamic node D of Head and each T in `D.Affects`: `Kind incr` → INVALIDATE T
(slot 0 `invalid`, `False + 1`) and transitively each of `T.Affects` (`False + 1` once per edge; SWI's falsecount); `Kind mono(eager)` with `Action`
an assert → § 4; `mono(lazy)` with an assert → § 5; a mono table with a retract → INVALIDATE (SWI `mon_invalidate_dependents`; `pa2`, the lazy `retract` test).

**Re-evaluation** at a call of an invalid T: today `'$tbl_valid'` deletes the table and the call re-creates it; that stays, with two additions. (a) An
invalid dependency called during T's re-run re-evaluates itself first, depth-first, by the same road (SWI's bottom-up `reeval_paths` is this order seen
from the leaves). (b) THE OLD ANSWER SET IS KEPT until the new one is complete and compared: equal → every dependent's `False - 1` and nothing re-runs
(`test_reeval` merged/only, `test_shared_units` propagate_falsecount); different → the dependents stay invalid. `abolish_table_subgoals/1` of a table
with incremental dependents invalidates them (xsb `test_abolish_nonincremental`).

## 4. MONOTONIC, EAGER: a delta-seeded semi-naive step in place of SWI's continuation

SWI captures, with `shift/1` inside `reset/3` (`'$start_monotonic'`, `pdelim`), the CONTINUATION of a clause body after the call to a monotonic dynamic,
stores it on the edge, and on an assert re-runs it per new fact. SCRIP's `reset/3` and `shift/1` are a one-shot coroutine road still 43 of 52 cases red (ARCH-PROLOG-CONTINUATIONS.md), and the tabling engine
re-runs clause bodies to a fixpoint (WFS § 3), so the equivalent is **the step the engine already knows how to take, seeded by an external delta**: on `'$tbl_dchange'(assert, F)` for mono D,
for each eager T in `D.Affects`:

`'$tbl_mono_step'(T, Src, Delta)`: open a header (`'$tbl_hdr'`), own cell 6 = **`mono(Src, Delta)`** (a third context form beside today's `all` and
`sn(R, Ps)`), cells 7-9 as a pass; run T's clauses once (`'$tbl_fa'(G, I, Fs)` as `'$tbl_runs'` does); under `mono(Src, Delta)`, `'$tbl_dcall'(G)`
for `Src = dyn(F/N)` unifies G with the members of `Delta` ONLY, and `'$tbl_slice'(S)` for `Src = S` a table returns `Delta` only — every other source
answers in full as today; close; add the answers (`'$tbl_addk'`); each NEW answer A (the trie insert returned new) propagates onward:
`'$tbl_mono_step'(T2, T, [A])` for each eager T2 in `T.Affects`, queued for a lazy T2 (§ 5), INVALIDATE for an `incr` T2 (`incr_mono`: an incremental
table never receives propagated answers). Depth-first recursion on the machine stack; it terminates because a present answer inserts nothing. A
self-dependent table (`cm/2`'s closure) propagates into itself. New dependencies met inside the step are recorded by cell 9 as in any pass (`closure`,
`closure2`: "deal with new dependencies while propagating").

`incr_propagate_calls(G)` is `'$tbl_dchange'(assert, G)` on G's dynamic node without touching the database (test 3: `d(X) :- data(X)` with `d/1`
declared mono and `data/1` plain); `incr_invalidate_calls(G)` the retract arm. A mono table invalidated by a retract re-evaluates fully at its next
call (`nested_reeval_mono`, `twice_invalid`). Nothing else in the engine changes: cell 6 is read by `'$tbl_range'` today, and the `mono` form is read
only by `'$tbl_slice'` and `'$tbl_dcall'`.

## 5. LAZY MONOTONIC: queue, invalidate, force

`Kind mono(lazy)`: on an assert (or a propagated answer from an eager source), push `Src-Delta` onto `T.Queue` and INVALIDATE T; the invalidation
propagates through T's lazy dependents (`intermediate`: both p1 and p2 read invalid) and INVALIDATES its eager dependents too (they have nothing new
until T is forced). **Forcing**, at a call of an invalid lazy T (`'$tbl_valid'`): force T's invalid lazy sources first (depth-first), then run
`'$tbl_mono_step'(T, Src, Delta)` for every queued pair (T's new answers propagate onward eagerly, queue on lazy dependents), clear `Queue`,
`False = 0`, `Forced = true`. `expect_queued_answers` reads `Queue` through `'$idg_mono_affects_lazy'/5`; `expect_forced` reads `Forced`. A retract on a
mono dynamic with lazy dependents invalidates them for a full re-evaluation (`retract`: `[2]` after `retract(d(1))`).

## 6. TRANSACTIONS AND SNAPSHOTS (placement ruled by the cfo, 2026-10-24 19:1x CDT: NO header cell)

`transaction/1` and `snapshot/1` exist nowhere in SCRIP (26 cases). SCRIP is single-threaded, so a change inside a transaction is simply APPLIED and
visible; what a transaction adds is UNDO on failure or exception, and `snapshot/1` is a transaction that always undoes.

**Where the log lives (the cfo's ruling, THE LIFETIME RULE):** the undo log lives exactly as long as the `transaction/1` (or `snapshot/1`) activation,
so its ROOT is a local of that activation, carved on the spine at first use like any local (RSP the default home, CEO-1942); its entries are unbounded
and go on the heap, rooted from that cell. A database change finds the innermost transaction through ONE trailed current-transaction root cell,
`'$tx_cur'` in the registry beside `'$tbl_cur'`, which the transaction banks in its own cell and restores at exit, failure or ball -- CEO-1542's single
current-X cell, the tabling header's own pattern, not a stack. The first ask (cell 10 of every tabling header, `TABLE_HDR_CELLS` 10 → 11) was REFUSED:
a DESCR in every tabled evaluation's frame for a cell only two predicates use is a pre-allocation, and CEO-1955/1959 hold those at zero. No new IR kind,
no header change; if a program ever needs the log through the header chain, that program goes to the cfo with the shape question (a per-header cell
count as a node fact, never the global count).

```prolog
transaction(G) :- '$tx_open'(Prev), ( catch(once(G), E, ('$tx_undo', '$tx_close'(Prev), throw(E))) -> '$tx_commit', '$tx_close'(Prev) ; '$tx_undo', '$tx_close'(Prev), fail ).
snapshot(G)    :- '$tx_open'(Prev), ( catch(once(G), E, ('$tx_undo', '$tx_close'(Prev), throw(E))) -> '$tx_undo', '$tx_close'(Prev) ; '$tx_undo', '$tx_close'(Prev), fail ).
```

`'$tx_open'(Prev)` banks `'$tx_cur'` in the clause's own local `Prev` and points `'$tx_cur'` at this activation's log cell (empty); `'$tx_close'(Prev)`
restores it. Every change under a transaction appends one record to the log the current cell names; `'$tx_undo'` replays the log in reverse;
`'$tx_commit'` drops it, or, nested, prepends it to the outer transaction's log (so an outer rollback still undoes the inner). The records, each with
its undo and the test that fixes it:

| record | written by | undo | fixed by |
|---|---|---|---|
| `added(Ref)` | `assert*/1,2` | `erase(Ref)` | transact_incr/mono commit, rollback, snapshot |
| `removed(Pred, Pos, Clause)` | `retract/1`, `retractall/1`, `erase/1` | re-insert `Clause` at `Pos` (a new leaf, `'$clause_reinsert'/3`; single-threaded, the chain is a list) | transact_mono_2 retract |
| `created(T)` | `'$tbl_enter'` | destroy T, delete it from the variant table | snapshot: a table first made inside |
| `answer(T, Sk)` | `'$tbl_mono_step'`'s new answer | `'$trie_delete'`: **the table stays VALID with its old answers** | transact_mono rollback, snapshot x4 (`expect_valid`, `[1,2]` after `[1,2,3]` inside) |
| `invalidated(T)` | § 3 on an `incr` dependent, § 3 on any retract | INVALIDATE T again: it was re-evaluated against the rolled-back database | transact_incr rollback and snapshot (`expect_invalid`), transact_mono_2 retract (`expect_invalid`) |

A table evaluated inside a transaction whose dependencies the transaction did not touch logs nothing and stays valid (transact_incr snapshot 2 and 3).
**Where the hook is:** the declared functors already pass through `'$tbl_dchange'` (§ 3), which logs when `'$tx_cur'` names a log; for an UNDECLARED
dynamic the runtime's database leaves (`assert*`, `retract*`, `erase`) log under the same test -- one root-cell read -- so the core `transaction/`
family (outside this page's population) rides the same road.

## 7. ANSWER SUBSUMPTION (moded tables) under §§ 3-5

A moded table (`:- table p(max) as incremental|monotonic|(monotonic, lazy)`) re-evaluated under § 3 drops its aggregate and recomputes it (`update`,
`keep`, `reeval`: a smaller fact keeps `[1]`, a larger one gives `[2]`, both after the dependency changed). A monotonic step into a moded T goes through
`'$tbl_madd'` (exists: it aggregates); a CHANGED aggregate is the new answer propagated onward (its `incr` dependent p2 is invalidated and re-reads `[2]`).
Lazy moded: queue, then `'$tbl_madd'` at force.

## 8. hq_zetas' glue, accounted (aca5f8246, harness bb6a6fc)

`pl_incremental_dynamics` stays the hook for a declared functor's `assert*`/`retract*`; its target becomes `'$tbl_dchange'(Action, Head)` in place of
`'$incr_inval'`, its three limits stand and are named here (the whole-table invalidation is replaced by the graph's; the static rewrite still misses a
variable clause argument; `predicate_property(_, incremental)` stays compile-time). `'$tbl_dcall'` is the same rewrite applied to CALL sites. The gate
`test_gate_pl_swi_incremental_tabling_a_plain_assert_or_retract_on_an_incremental_dynamic_invalidates_the_tables_that_read_it.sh` stays green: its
witness is the special case of § 3 where every incremental table happens to depend on the changed predicate. hq_zetas' incremental rows are not held.

## 8b. THE RUNTIME LOADER IS THE SECOND ROAD, AND IT NEEDS THE SAME THREE HOOKS (measured 2026-10-24 19:5x CDT)

A program that defines `term_expansion/2` or `goal_expansion/2` (every plunit file of the SWI tabling suite does, through its `cleanup` expansion) is
not compiled statically after that clause: `pl_load_hook_line` (lower_prolog.c) hands the rest of the file to THE RUNTIME LOADER, the `'$lfx_*'`
prelude in `prolog_parse.c`'s `PL_PRELUDE_SRC` (about lines 2780-2960), which scans the terms (`'$lfx_scan'`), wraps tabled predicates
(`'$lfx_wraps'`: `k(F/N, none|incr|moded)` → `'$tbl_call'`, `'$tbl_icall'`, `'$tbl_mcall'`), declares dynamics (`'$lfx_dir'(dynamic(S))`, dropping
`as` through `'$lfx_dspecs'`) and rewrites every body goal (`'$lfx_body'`). So the static hooks of §§ 2-4 (the lowerer's `'$tbl_dcall'` at the call
site, the parser's `'$tbl_dchange'` rewrite, the table kind in the wrapper) never see test_monotonic.pl's units, and its ten cases keep their
verdicts until the loader carries the same three: (1) `'$lfx_tspecs'(as(S,O),...)` reads `monotonic` and `lazy` beside `'$lfx_incr'` and
`'$lfx_wraps'` emits `'$tbl_kcall'(H,I,mono|lazy)` (and `'$tbl_mcall'(H,I,Sp,Kind)`); (2) `'$lfx_dir'(dynamic(S as O))` with incremental or
monotonic in O records the qualified functor as a hooked dynamic (a `'$tbl_dkind'(Q/N, Kind)` fact, the loader's runtime twin of the lowerer's
hook list), and `'$lfx_body'` rewrites a call to one as `'$tbl_dcall'(G2)`; (3) `'$lfx_body'`'s database arm (`'$lfx_mdb'` for a variable clause,
the `'$lfx_meta'` row for a bound one) appends `'$tbl_dchange'(Op, C2, Kind)` for a hooked head. The standalone witness (a monotonic table over a
monotonic dynamic, an incremental table over a monotonic one, the self-recursive closure) and the same program inside a plunit unit WITHOUT
term_expansion are equal to swipl in both modes on the static road (SCRIP, the IDG landing); with term_expansion present only the loader road runs.
Until (1)-(3) land, a change the graph has no edge for falls back to the coarse `'$incr_inval'` (every incremental table invalidated), which is
today's behaviour and what keeps `twice_invalid` green on the loader road.

## 9. Measured, not designed here

- **THE CRASHES** (`test_reeval` dynamic_tabled, dynamic_tabled2-4: `wfs`, `wfs2`, 5 cases, signal 11 in both modes): a predicate both `:- table` and
  `:- dynamic`, incremental, with `tnot/1` and `get_residual/2`. A compiler or runtime crash outranks a feature: it is BRACKETED FIRST (the monitor, then
  gdb at the signal) as its own bug row before § 3 lands, because § 3's re-evaluation runs exactly that shape.
- **xsb table_tests** `negcycle`, `tda`, `tda_i` HANG: WFS scheduling, `ARCH-PROLOG-WFS-TABLING.md` § 3's; `pps`, `3vwfs`, `cyclic_tabling`, `maxans_decl`
  (the `max_answers` declaration) read per case when reached.
- **THE TRIE API SURFACE** (`test_trie` 24, `test_trie_attvars` 12: `trie_new/insert/lookup/gen/delete/term/update/insert_with_value...`, attributed
  variables as keys): the table store already is `HB_TRIE` behind the `'$trie_*'` leaves; the SWI surface over it is its own row, after this page's.

## 10. The rows and the order (LARGE CHUNKS, CEO-1478..1484; CEO-1928; CEO-1953)

1. Bracket the § 9 crash (one row, one program at a time).
2. BUILD §§ 2-4 WHOLE in `prelude/tabling.pl` plus the lowerer's `'$tbl_dcall'` rewrite and `'$tbl_dchange'` (LANDED, the static road); then § 8b's three loader twins; SMALL ROLL-OUT on `test_monotonic.pl`
   (10 cases; the row's DONE-WHEN is `pa1` and `incr_mono`), with the Prolog smoke and the tabling handful (`test_tabling` 35/35, `test_answer_subsumption`,
   `test_wfs` unchanged) before the push; requests to the coo name at most 8 cases.
3. § 5 on `test_monotonic_lazy.pl` (15); § 6 on the three transaction files (26) under the cfo's placement ruling; § 7 (9); then xsb incremental (7).
4. The cto designs and builds (CEO-1960); the eight smokes before every push since the prelude is parsed for every tabling program; the coo grades.

## 11. What this page forbids

A global list of tables being evaluated or propagated (CEO-1542: the chain of headers IS the list); a worklist held anywhere but the machine stack; a
new root cell (the transaction is found through the header chain); an answer or a dependency kept outside the trie's meta term; `nb_setval` on any
`$tbl_` name; a continuation store (the one-shot `reset/3` road is not a foundation yet, and the delta step needs none); invalidating every incremental table on a change once § 3
is in (the graph decides).
