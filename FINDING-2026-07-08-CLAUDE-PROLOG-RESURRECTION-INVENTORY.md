# FINDING 2026-07-08 (Claude) — PROLOG RESURRECTION INVENTORY: what GZ#5 left behind, where it lives in git, and the new-way ladder to bring it forward

Session ask (Lon): go back in GitHub history to the exclusion point, inventory what Prolog features were left behind, resurrect any old code that fits — with the single restriction that everything lands the NEW way (reduced IR, Icon-pattern lowering, one emitter, template menu).

## 1. The amputation, located (git hashes — re-extract any time with `git show <hash>:<path>`)

| Event | Commit | Date |
|---|---|---|
| Last fully-green Prolog tree (115/115 m3+m4 + bench) | `63c666ba` (= parent of first GZ#5 commit `e2f1d61b`) | 2026-06-27 |
| GZ#5 begins (IRM-0 emitter-no-mutation) | `e2f1d61b` | 2026-06-28 |
| **Enum amputation** — 119 Prolog/SNOBOL4/Raku/Pascal IR_e members + dead codegen subsystems removed | `8de0fb46` | 2026-06-29 |
| **Makefile exclusion** — non-Icon lowerers out of build; `lower_noicon_stubs.c` link glue | `e1ec0679` | 2026-06-29 |
| Re-admit lowerers, phantom IR_* → `IR_OP_COUNT` (compiles, not functional) | `667b9cd6` | 2026-07-01 |
| GZ#6 reconstruction starts (rung01+02) | `8a687b51` | 2026-07-05 |

Key structural fact: in the green tree the Prolog GOAL-BUILDING lived in **`src/driver/scrip.c` (`pl_gz_*`, ~3580 lines)** and emission in **`src/emitter/emit_bb.c` (`gz_emit_*`, ~4179 lines)** — `lower_prolog.c` was thin (629 lines). Per GROUND ZERO #6 these are SEMANTICS REFERENCES ONLY; the control machinery does not transplant. Old Prolog box files at `63c666ba`: `bb_callee_frame, bb_cell_{call,catch,choice,cut,dyniter,findall,ite,unify}, bb_det_retract, bb_goto_dyn, bb_query_frame` (all under the deleted `src/emitter/BB_templates/`).

## 2. The single biggest live resurrection target: `src/runtime/unification.c`

Present in the CURRENT tree, **out of the build** (referenced nowhere in Makefile), 1029 lines / 79 functions — the whole GZ-era deterministic-builtin family: `rt_pl_{univ,functor,arg,copy_term,sort,atom_op,type_test,succ_plus,char_type,numbervars,term_string,dyn_assertz,dyn_retract,dyn_abolish,nb_setval,nb_getval,format,write,writeq,write_canonical}_cell` + a linked-list dynamic clause store (`dyn_clause_t`/`dyn_pred_row_t`).

It does NOT re-link as-is: it compiles against the amputated IR vocabulary (`IR_ATOM`, `IR_LOGICVAR` in `rt_node_to_term`) and the old `Term*` representation. The CURRENT term world is DESCR-based (`by_name_dispatch.c`: vars = NAMEPTR→cell chains, unbound = `DT_SNUL`/self-`DT_PLVAR`, bind = `plw_bind` + `pl_trail_push`; compound = `DT_PLREF`, `slen=(atom_id<<16)|arity`, `p=DESCR_t kids[]`; unify = `plw_unify_cells`). **Rule adopted: port the ALGORITHMS into DESCR-world `$name` arms in `by_name_dispatch.c`; never link the old cell bodies.**

## 3. Current failure census (fresh run this session, interp mode, 83 FAIL / 115)

Dominant mode: `FATAL emit_drive: IR op=104` = `IR_OP_COUNT` from `lower_prolog.c`'s `is_builtin_exec` fallback (line ~387) — i.e. the lowerer recognizes the name (old `g_pl_nl_builtins` list) but has no new-way arm. Family → need:

| Family (count) | Predicates required (verified from rung sources) | Old algorithm home |
|---|---|---|
| rung14_retract (5), rung15_abolish (5) | runtime dynamic DB: retract/1, abolish/1, re-assert after abolish | `unification.c` dyn store; NOTE current assertz passes only via **lower-time seeding** (`prolog_lower.c` `pld_seed`), no runtime store exists |
| rung16_atop (5) | `@< @=< @> @>=` standard order | `rt_pl_term_compare` (in unification.c) |
| rung17_sort (5) | sort/2, msort/2 | `rt_pl_sort_cell` |
| rung19_format (5) | format/1,2 with `~w ~a ~d ~i ~n` | `rt_pl_format_cell` |
| rung20_numbervars (5) | numbervars/3 incl. rollover, start offset | `rt_pl_numbervars_cell` |
| rung21_char (5) | char_type/2 (alpha, digit(W), space, alnum, upper(L), lower(U), to_upper, to_lower) | `rt_pl_char_type_cell` |
| rung22_write (5) | writeq/1, print/1, write_canonical/1 (atoms, lists, ops) | `rt_pl_writeq_cell`, `rt_pl_write_canonical_cell` |
| rung23_arith_ext (4 open) | bitwise `>> << /\ \/ xor`, max/min, sign, truncate | GREEN scrip.c arith table: `abs sign min max gcd rem truncate integer float floor ceiling round sqrt sin cos atan log exp msb xor << >> /\ \/` |
| rung24_string (5) | string_upper/lower, atom_string, number_string, string_concat, string_length | `rt_pl_atom_op_cell` + `rt_pl_term_string_cell` |
| rung25_term (3) | term_to_atom/2 (ground→atom direction in corpus), term_string | writeq-to-buffer |
| rung26_copy (5) | copy_term/2, atomic_list_concat/2,/3, string_to_atom | `rt_pl_copy_term_cell` |
| rung27_aggregate (4) | aggregate_all(count/sum(E)/max(E)/min(E)), nb_setval/getval | `rt_pl_agg_minmax_finish` survives in-tree; nb via `rt_pl_nb_*_cell` |
| rung28_exceptions (5) | catch/3, throw/1 | old `bb_cell_catch` + `pl_gz_catch_state_t`; NEEDS NEW-WAY DESIGN (control-flow) |
| rung29_number (5) | float fns/parts/conversion, gcd, constants (pi; exp(1.0)) | arith table |
| rung30_dcg (5) | phrase/2,3 (DCG **translation survives in `prolog_parse.c` `dcg_*`**) | phrase arm currently OP_COUNT |
| rung40_typetest (4) | compound, callable, ground, is_list | `rt_pl_type_test_cell` |
| rung11 (2) | findall with conjunction/arith inner goal | investigate after arith |
| rung09 (1) | mixed | falls out of the above |

Other amputated arms in current `lower_prolog.c`: `\=` (bb_ite_state OP_COUNT block), `catch`, `aggregate_all` (old bb_findall_state subgraph), `phrase`, `TT_UNIFY`, plus `lower_pl_dyniter_graph` (OP_COUNT dyniter residue — dead).

Also: rung05/07/08 (backtrack/cut/recursion) **PASS** since PROC-STAGED (`1f0ebdab`) — the goal file's "multi-clause dispatch is NEXT" item is stale; user-predicate calls with args, choice, cut, recursion work in m2/m3 (m4 too, modulo write/1 below).

## 4. The new-way resurrection ladder (this session begins executing it)

- **R1 `$write`** — write/1 → `IR_CALL_BUILTIN_PROLOG "$write"` → `out_write_descr` (one path all modes). Closes the 5 m4 list-print divergents (27→32 compile). The 07-07 crash retry: previous attempt's failure mode unexplained; mitigate by mirroring the proven `$atom_length` shape exactly and gating m2-smoke-first.
- **R2 det-builtin slab** — table-ize the lowering arm (`{name, arity} → $name`, args term_lval-threaded, the existing line-340 pattern); dispatch arms in by_name_dispatch porting unification.c algorithms into DESCR world: type tests, @-compare (+ shared standard-order compare), sort/msort, writeq/print/write_canonical, format/1-2, numbervars/3, char_type/2, copy_term/2 (fresh-var deep copy helper — also serves assert store later), atom_string/number_string/string_*/atomic_list_concat, term_to_atom (print direction).
- **R3 arith extension** — binary suffix table += min max gcd xor >> << /\ \/ rem; NEW unary path `$is1_<fn>` (abs sign truncate integer float floor ceiling round sqrt msb sin cos atan log exp float_integer_part float_fractional_part); constants (pi).
- **R4 `\=`** — pure rewire on existing prims: `$trail_mark` → unify → on γ `$trail_unwind`+fail, on ω `$trail_unwind`+succeed. Deletes the OP_COUNT/bb_ite_state block.
- **R5 phrase/2,3** — lower to the generic-call shape with two extra list args (DCG clauses are ordinary after parser translation).
- **R6 aggregate_all** — findall-shape lowering (inner goal via thread1 in the MAIN graph, the proven redo loop) + `$agg_finish_<op>` fold; deletes the bb_findall_state subgraph block.
- **DEFERRED (next sessions, in order):** runtime dynamic DB (retract/abolish; design: DESCR clause store + call-path enumeration as a generator — evaluate riding `IR_CALL_BUILTIN_GEN`); nb_setval/getval (trivial once store helper exists); catch/throw (control design: scratch-trail per DESIGN §4 — needs Lon sign-off on mechanism); rung10 `.expected` generation (gprolog oracle; 21 files); findall-inner residual (rung11) if not freed by R3.

## 5. Other recovered assets (for later sessions)

- `.github/wip-patches/2026-06-02-prolog-bb-regression-restore-WIP.patch` (196K) — pre-reset BB-era Prolog work; treat as semantics quarry only.
- `.github/pl-areas-3b-detpop-WIP.patch` + the PL-AREAS ladder — performance track, untouched by this reconstruction.
- `.github/test_pl_1.c` — the seed shape reference (unchanged canon).
- gprolog/SWI sources mounted at `SCRIP/refs/{gprolog-master,swipl-devel-master}` (uploaded zips); cited files verified present: `EnginePl/wam_inst.h`, `Pl2Wam/indexing.pl`, `src/pl-incl.h`, `src/pl-index.c`.
