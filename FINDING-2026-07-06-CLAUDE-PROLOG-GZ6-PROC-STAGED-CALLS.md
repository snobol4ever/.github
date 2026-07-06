# FINDING 2026-07-06 — Prolog GZ#6: user-predicate calls via proc-staged route (THE WALL, breached)

## Summary
The GZ#6 rebuild reached and breached THE WALL (user-predicate calls via graphs, never
implemented — rung05/07/08 were always deferred). Multi-clause predicates now lower to one
graph per predicate on the reduced-IR spine, register as **generator procs**, and are
called through the **existing** `CALL_ROUTE_PROC_STAGED` convention. No new callee protocol,
no new driver loops, no template surgery on SUCCEED/FAIL. One runtime unification bug
(unbound-input-first args) remains and blocks rung05+.

## What is DONE and GREEN (committed this session)
- Build green both targets (`scrip` + `libscrip_rt`).
- Rungs 01-04 PASS m3. Prolog smoke 5/5 (mode-2 hard gate). Icon smoke 12/12 both modes.
- Slice 1 (runtime unify/trail in by_name_dispatch.c) — complete, from prior session.
- Slice 2a-2d (LOWER rewrite) — complete: term_e/term_lval_e/mkc_node entry-threading;
  user-call arms emit real IR_CALL (resumable, cx->beta); one-graph-per-predicate builder
  `lower_pl_pred_graph_new` (trail_mark → clause chain with per-clause trail_unwind →
  MOVE_LABEL(redo target = clause body β, ival=1 for generator/CALL) → SUCCEED; DISJUNCTION
  as body_root/β-entry).
- **THE WALL breakthrough**: predicates register as generator procs in `proc_table`
  (`is_generator=1`, `bb_idx`=their graph) in `lower_pl_register_all_preds`. The existing
  Icon m3 AND m4 proc emission/register/bind loops then emit them with
  `g_frame_active=1`+`g_gen_proc_active=1` for free, and `CALL_ROUTE_PROC_STAGED` routes
  calls to `rt_proc_call_gen`/`rt_proc_resume_gen`.
- Why it "just works": the flat epilogue (xa_flat.cpp) under g_frame_active already returns
  the frame-slot-0 verdict (fail writes [r12+0]=99=DT_FAIL, success leaves NULVCL);
  `rt_proc_call_gen` reads frame[0], `cmp eax,99` gives success/fail; esi=0 fresh / esi≠0
  redo matches the prologue `cmp esi,0; jne β`. Prolog predicate == Icon generator, verdict-wise.
- β-emission hook (emit.cpp, codegen_flat_chain_body β-label else-branch): when
  `g_emit_cfg->body_root` is a DISJUNCTION present in nodes[], redo jumps to its α label
  (bb_indirect_goto through the DJ slot). MOVE_LABEL writes clause redo targets into that
  same slot (operand[1]=dj → drive_value_slot(dj)). Guarded on DISJUNCTION → Icon unaffected
  (Icon uses the SUSPEND branch above), confirmed by Icon mode-4 byte-gate passing.
- WAM binding-direction fix (by_name_dispatch.c plw_unify_cells line ~86): two unbound vars
  now bind higher-address → lower-address cell (zeta allocator bumps UP, so callee frames are
  higher; younger→older keeps caller-visible cells alive after callee frame release).

## Verified call behavior (probes)
- Forward multi-clause, first solution: `p(a).p(b). main:-p(X),write(X),nl.` → a  [fact-choice inline path]
- Fact backtracking: `p(a).p(b).p(c). main:-p(X),write(X),nl,fail;true.` → a b c  [fact-choice + DISJ redo]
- Proc-staged route reached (no more FATAL) for compound/multi-arg calls.
- Ground/output arg binds propagate: `eq(X,X). main:-eq(a,Y),write(Y),nl.` → a  ✓

## THE ONE REMAINING BUG (blocks rung05)
Unbound-input-**first** arg does not surface the binding to the caller:
`eq(X,X). main:-eq(Y,b),write(Y),nl.` → prints empty (expected b).
- Confirmed NOT the bind direction (both directions fail; on success rt_proc_call_gen does
  NOT free the callee frame — activation kept — so it is not a dangling-pointer issue on the
  first solution).
- Trace (PLW_DBG, now removed): only the 2 head-unifies fire, both operands NAMETRAP(slen=2)
  as expected ($unify(VAR_REF("A{i}"), VAR_REF(clausevar))).
- By reasoning, after u_0 (var-var bind of deref(A0)=main_Y with callee_X) and u_1
  ($unify(b, X)), deref(main_Y) should be b via either binding direction — yet write(Y) sees
  unbound. So the fault is in the deref/entry chain for the **input-ref-in-a-param-slot**
  case, or write(Y) reads a cell that is not the one bound.
- NEXT STEP: re-add a deref probe INSIDE plw_unify_cells (print A,B cell addrs + tags before
  and after bind) for `eq(Y,b)`; compare the main_Y cell address seen at bind-time vs the
  cell write(Y) reads. Prime suspects: (a) plw_cell_deref not chasing a NAMETRAP that itself
  wraps a NAMETRAP (double DT_N slen=2 indirection: VAR_REF("A0")→callee_A0 whose CONTENT is
  the staged NAMETRAP→main_Y); (b) plw_entry vs plw_cell_deref divergence for slen=2;
  (c) write(Y) in main (lowered via the OLD lower_prolog_clause path) reading Y through a
  path that does not deref DT_PLVAR chains.
- Once fixed: test `eq(Y,b)`, then `first(Y,[a,b,c])` (compound head), then rung05
  (member/2 recursion+backtrack), m3 first then m4. Then rung ladder 06/07/08.

## Key file/line anchors (this session)
- src/lower/lower_prolog.c: term_e/term_lval_e/mkc_node (~30-100); thread_goals resume-rewrite
  with last_res_beta + lc_ω_to_β (~148-153); user-call IR_CALL arms (~400,~420);
  pl_param_name + lower_pl_clause_into (~458-490, BEFORE late includes);
  lower_pl_pred_graph_new (AFTER includes, ~522); register_all_preds proc_table registration
  (~640, the `if (!dyn) stage2_proc_grow` block); main proc registration (~825).
- src/emitter/emit.cpp: β-hook in codegen_flat_chain_body else-branch (~1547, the
  `g_emit_cfg->body_root ... IR_DISJUNCTION → resume_tgt = lbls[i]`).
- src/runtime/by_name_dispatch.c: plw_unify_cells var-var bind direction (~86);
  $unify arm (~739, probe REMOVED).
- src/runtime/rt/rt.c: rt_proc_call_gen (409), rt_proc_resume_gen (~458),
  rt_frame_bind_args (positional, ~358) — the reused call convention.
- src/templates/bb_call_proc_staged.cpp: bcps_txt_gen_arm / bcps_bin_gen_arm (the
  rt_proc_call_gen + rt_proc_resume_gen + cmp eax,99 verdict convention).
- src/templates/xa_flat.cpp: prologue (41) + epilogue (99) — frame verdict convention reused.

## Deferred (unchanged from prior plan)
- Arity overloading: predicates keyed by BARE name in proc_table (member vs member/2). Fine for
  single-arity-per-name programs (rung05). Add name-mangling if a program overloads arities.
- R14 trail-register, then R13/R15 arenas with PL-AREAS-4 escape-copy — AFTER rungs green.
- Dead code left harmless under -w: lower_pl_clause_graph / lower_pl_choice_graph (register
  now routes non-dyn through lower_pl_pred_graph_new).
