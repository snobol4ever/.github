# HANDOFF 2026-06-15 — CLAUDE — PROLOG-BB — DYNITER DYNAMIC RAIL (B2 LANDED, +6 → 113/113)

Goal: GOAL-PROLOG-BB. Topic: make dynamic predicates store-backed and enumerable so retract/abolish
work, closing 6 of the 8 dynamic reds. m3/m4 **107 → 113 byte-identical**.

## RESULT
- GATE-3 m3 **113** / m4 **113** (parity intact, by construction). GATE-1 m3/m4 5/5.
- NO-NEW-GLOBAL ratchet **15/15** (store rides existing SANCTIONED `g_pl_dyn_pred_table`; marked-set +
  seeds are FIELDS of `g_stage2`, NOT new `g_*`).
- Cross-lang stable: Icon run 122 (IR enum additions append-only before `IR_OP_COUNT`, no value shift).
- Closed: `rung14_retract_{basic,unify}` + `rung15_abolish_{existing,one_of_two,then_query_fail,then_reassert}`.
- 2 remaining reds (both `rung14`): `retract_mixed` (m4 integer-struct bug, FENCED both modes) +
  `retract_all` (callee-body retract, B3).
- Commit identity used: LCherryholmes / lcherryh@yahoo.com.

## THE DYNITER RAIL (how a dynamic predicate becomes a Byrd box)
Detection → suppression → dyniter callee → population → the box → runtime. Fork 1 (minimal Prolog-only
dynamic rail) per the A0 decision; clauses are Term DATA (not per-clause BBs), one dyniter box drives them.

1. **Marking** — `prolog_lower.c` `pld_mark_scan`, run at the TOP of `prolog_lower` (before the directive
   fold so seeds can be gated on it). A functor/arity is dynamic iff it is a target of
   `retract`/`retractall`/`abolish` (anywhere), `:- dynamic(F/A)`, or **runtime** `assertz`/`asserta`
   (in a RULE body — gated by `mark_assertz = (cl->head != NULL)`). **Directive `:- assertz` alone does
   NOT mark** (stays static-folded). THIS PRECISION IS LOAD-BEARING: marking on directive-assertz
   regressed all 5 rung13 (static-assertz) rungs. Marks: `g_stage2.pl_dyn_{name,arity,n}` (compile-time
   const metadata, `g_pl_nl_arith` tier); extern `pl_dyn_mark` / `pl_dyn_is_marked`.
   (`lower_prolog.c` also has a redundant `pl_dyn_mark_prepass` over post-fold pred-table trees — safe,
   it can't see directive-assertz as a call by then. Harmless; could be removed.)
2. **Suppression + dyniter callee** — `lower_prolog.c` `lower_pl_register_all_preds`: a marked pred SKIPS
   static clause/choice lowering; `lower_pl_dyniter_graph` builds a 1-node graph, entry =
   `IR_CELL_DYNITER`, state `pl_gz_dyniter_state_t{functor_atom, arity, cursor_slot=arity,
   mark_slot=arity+1}`, `nslots=arity+2`.
3. **Inline declines + callee acceptance** — `scrip.c`: `pl_gz_fact_inline` / `pl_gz_choice_inline`
   return early when the resolved callee is marked (so the call does NOT inline baked static clauses and
   instead falls to CELL_CALL → dyniter callee); `pl_gz_rule_inline_check` + `pl_gz_rule_body_goal_ok`
   accept a DYNITER-entry callee graph; NEW `pl_gz_callee_get_dyniter` (nclauses=1, **nlocals=2**
   [cursor+mark], body_head = the dyniter node) routed from `pl_gz_callee_get_any`.
4. **Population** — `prolog_lower.c`: directive-`assertz` clauses for MARKED preds are captured into
   `pld_seed[]` (a `tr_dup` of the `assertz(arg)` goal tree) and PREPENDED to `main`'s clause body so
   they run as the first goals, seeding the store at startup. (Directive-assertz for a marked pred is
   thus BOTH folded into the now-suppressed static pred AND seeded; suppression makes the fold inert, the
   seed populates the store.)
5. **The box** — `bb_cell_dyniter.cpp` (NONDET, four-port). α = `rt_trail_mark`→mark cell,
   `rt_pl_dyn_iter_begin(functor,arity)`→cursor cell, `rt_pl_dyn_iter_step`. β = `rt_trail_unwind(mark)`
   THEN `rt_pl_dyn_iter_step`. **The β trail-unwind is load-bearing**: without it the previous solution's
   bindings persist and the next step's head-unify fails against the still-bound arg (the bug that made
   retract_basic emit only `red` instead of `red`/`blue`).
6. **Runtime** — `unification.c`, all Term-only, rides `g_pl_dyn_pred_table` (the A0 linked-list store):
   `rt_pl_dyn_assertz_cell(clause_cell, prepend)` (split `H:-B`, copy_term_deep, append/prepend),
   `rt_pl_dyn_iter_begin`→heap cursor `dyn_cursor_t` held in a FRAME cell (NOT a global stack — same
   shape as the findall acc), `rt_pl_dyn_iter_step` (head-unify under a per-step trail mark; advance on
   match, unwind+next on mismatch, 0 when exhausted).
7. **`IR_DET_ASSERTZ`** + `bb_det_assertz.cpp` (det recipe; `op_parts_ival[0]`=clause slot, `[1]`=prepend;
   prepend carried in the node `ival`). Serves BOTH population AND main-level runtime `assertz`/`asserta`
   (`pl_gz_count_synth_goal` + `pl_gz_build_goal` arms, mirror of retract). A0's `IR_DET_RETRACT` /
   `IR_DET_ABOLISH` now operate on the POPULATED store.

## FILES TOUCHED (all committed this session)
- `src/contracts/IR.h` — +IR_DET_ASSERTZ, +IR_CELL_DYNITER (append-only before IR_OP_COUNT).
- `src/contracts/scrip_ir.c` — name-table entries.
- `src/contracts/stage2.h` — +pl_dyn_{name[64],arity[64],n} fields on stage2_t.
- `src/emitter/box_state.h` — +pl_gz_dyniter_state_t.
- `src/emitter/BB_templates/bb_det_assertz.cpp`, `bb_cell_dyniter.cpp` — NEW templates.
- `src/emitter/BB_templates/bb_templates.h` — decls.
- `src/emitter/emit_core.c` — 2 dispatch cases.
- `src/emitter/emit_bb.c` — bb_prepare arms (DET_ASSERTZ, DYNITER) + IR_CELL_DYNITER into gz_node_bounded.
- `src/runtime/unification.c` — dyn_pred_intern, rt_pl_dyn_assertz_cell, dyn_cursor_t,
  rt_pl_dyn_iter_begin/step.
- `src/lower/lower_prolog.c` — pl_dyn marking helpers + prepass, lower_pl_dyniter_graph, suppression in
  lower_pl_register_all_preds, prepass call in lower_pl_stage2.
- `src/parser/prolog/prolog_lower.c` — pld_mark_* scan (rule-context-gated), seed capture + injection
  into main.
- `src/driver/scrip.c` — pl_dyn_is_marked extern, inline declines, dyniter callee accept +
  pl_gz_callee_get_dyniter, assertz admission arms, **integer-retract-head FENCE** (the parity guard).
- `Makefile` — 2 RT_PIC_SRCS + 2 compile rules (append-only).

## REMAINING WORK

### R1 — `retract_mixed` m4 integer-struct bug (un-fence after fixing)
`retract(fact(2))` works in m3, emits EMPTY in m4. Atom-arg retract (`retract(color(green))`) works in
BOTH; pure-integer dynamic facts (`assertz(fact(1))`+enumerate) work in m4. So the bug is the
**integer-literal-arg retract HEAD struct built in the m4 TEXT medium** — the `CELL_UNIFY(slot,fact(2))`
→ `gzu_build` path with an `IR_LIT_I` operand (same family as the historic C-FRAME m4 struct findings).
CURRENT MITIGATION: integer-literal retract heads are FENCED in BOTH modes (scrip.c `pl_gz_build_goal`
retract arm: `if h0 is IR_STRUCT with any IR_LIT_I operand return 0`) to hold m3≡m4 — this returns
retract_mixed to its pre-session failing state (no regression vs the 107 floor).
REPRO: `/tmp/tret.pl` = `:- assertz(fact(1)). :- assertz(fact(2)). :- assertz(fact(3)). main :-
retract(fact(2)), fact(X), write(X), nl, fail. main.` → m3 `./scrip --run` gives 1,3; m4
`bash scripts/run_prolog_via_x86_backend.sh /tmp/tret.pl` gives EMPTY. (Note: the fence will block this
repro now — temporarily remove the fence to reproduce, or test with the fence removed.)
FIX: gdb the m4 binary, diff the m3 vs m4 asm for the `fact(2)` term construction (likely the integer
operand isn't materialized into the built compound in the TEXT medium); fix the encoder/cell-build; then
DELETE the fence → +1 both modes (114/114).

### R2 — `retract_all` (callee-body retract), B3, the last original red
`retract(item(_))` lives in the BODY of a CALLED predicate (`retract_loop :- retract(item(_)),
retract_loop`), not at main level → FENCED both modes (callee-body admission has no retract arm). Three
sites (mirror A0's main-level retract + the rung28 catch-in-callee-body extraction):
(a) `pl_gz_rule_body_goal_ok` — add `IR_BUILTIN "retract"/1` arm (head LOGICVAR or STRUCT/ATOM; for
    `item(_)` the head is a STRUCT with a fresh-var arg — the integer fence does NOT apply, var arg);
(b) `pl_gz_rule_clause` whitelist — `continue` for `retract`/1;
(c) `pl_gz_callee_body_node` — emit `IR_DET_RETRACT` with slot-mapping (`pl_gz_struct_slot_map` the head
    if STRUCT, or synth a CELL_UNIFY to a slot as in the main-level path; count the synth slot in
    `pl_gz_clause_nsynth`).
`retract_loop` is a 2-clause pred (recursive clause + base `retract_loop.`), already CHOICE-admissible;
only the `retract` goal inside clause-1's body is unadmitted. Expected: +1 both modes → 114/114.

## NOTES / RISKS
- The DYNITER cursor + mark are FRAME cells (slots arity, arity+1), NOT globals — the no-new-global
  ratchet stays 15.
- retract is det first-match-remove (correct for these rungs: retract_basic removes one then enumerates
  the rest; the nondeterminism is in the dyniter enumeration, not in retract). A full NONDET cursor-
  retract is a later refinement, not needed.
- Logical-update view (generation numbers / seeing call-time clauses across concurrent assert+retract) is
  deferred — none of the rungs stress it (confirmed against gprolog's LDUV machinery in
  refs/gprolog_db/dynam_supp.c, which we deliberately do NOT port under Fork 1).
- `--dump-ast` segfaults on ALL Prolog programs on clean HEAD too (pre-existing, unrelated). Use
  `--dump-ir`.
- Harness `--mode all` still drives the deleted m2 `--run` arm → false FAILs; use `--mode run` /
  `--mode compile` separately. (Open item for Lon: re-baseline the gate scripts off m2.)
