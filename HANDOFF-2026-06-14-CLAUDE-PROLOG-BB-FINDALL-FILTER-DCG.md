# HANDOFF — 2026-06-14 · Claude · Prolog BB — rung11 findall_filter + rung30 DCG (m3/m4 93→98)

## Watermark
SCRIP `89e8dd0` (pushed; rebased across upstream Icon/SNOBOL4/Raku/Pascal commits, no conflict) · .github `(this commit)`.
**m2 114/115 · m3 98/115 · m4 98/115.** GATE-1 5/5/5 HARD. NO-NEW-GLOBAL floor 15 (unchanged). m3≡m4 by construction.

## Gates (verified before each push AND re-verified post-rebase)
GATE-1 `test_smoke_prolog.sh` 5/5/5 ✓. GATE-3 `test_prolog_rung_suite.sh` m2=114 / m3=98 / m4=98 ✓.
`test_gate_pl_no_new_global.sh` green at floor 15 ✓. rung27 5/5 ✓, rung30 4/5 ✓.
Cross-lang HARD: SNOBOL4 m4 7/7 ✓, Icon m2 12/12 ✓, Raku m2 35/35 ✓ (unification.c + emit_bb.c + IR_interp_state.h are shared).
`bb_one_box` unchanged at 56 (git-stash A/B + "none of my 4 files in the fail list" — all pre-existing SNOBOL4/Icon).

---

## Two commits this session

### `ae2dd38` — rung11 findall_filter (+1 m3/m4)
`findall(X, even(X), Xs)` with `even(X) :- num(X), 0 is X mod 2.` and `num(1..5)`.

**Fix A — literal-LHS `is/2`** (the documented blocker). The runtime needed NO change:
`rt_pl_is_cell_int/arith/bivar` (IR_interp.c) all `unify(term_deref(lhs), result, trail)`, so a
bound/literal LHS already compares correctly. The gaps were admission + emission:
- `pl_gz_rule_body_goal_ok` (scrip.c ~551): the `is` arm now admits `IR_LIT_I`/`IR_LIT_F` LHS, not just `IR_LOGICVAR`.
- `pl_gz_rule_callee_body` (scrip.c ~875): when the LHS is a literal, synthesize a fresh logicvar slot
  (`synth_next++`), emit an `IR_CELL_UNIFY` binding it to the literal, then drive `IR_DET_IS` against the
  fresh slot (the same `pl_gz_lv(kk)` synth pattern the call-arg path uses). `IR_DET_IS`'s emitter
  (`bb_det_is.cpp`) requires the LHS be a frame slot, so the literal must become a bound cell first.
- `pl_gz_clause_nsynth` (scrip.c ~747): counts the new literal-LHS-`is` synth slot so the callee frame is
  sized correctly (else the synth slot collides with a child slot).

**Fix B — choice clause cap 4→8** (the SECONDARY blocker the real test exposed). `num/1` has 5 facts;
the cap was 4. Widened, all in lockstep:
- `IR_interp_state.h`: `pl_gz_callee_t.clause_head[4]→[8]`, `pl_gz_choice_state_t.consts[4][8]→[8][8]`.
- `emit_bb.c` `gz_emit_callee`: stack arrays `nb[4]→[8]`, `cladv[4]/redo[4]/cbase[4]→[8]`.
- `scrip.c` `pl_gz_callee_get_choice`: `zsk[4]/lbase[4]→[8]`.
- The three `nbodies > 4` / `bcch_N() > 4` caps (`pl_gz_choice_inline`, `pl_gz_choice_rule_clauses`,
  `bb_cell_choice.cpp`) → `> 8`.
- The emit loops (`bb_cell_choice` `FOR(0,bcch_N())`, `gz_emit_callee` `for c<NC`) were ALREADY dynamic
  over the clause count — only the fixed arrays and the caps were the ceiling. 8 was chosen as a safe
  round bump; raise again the same way if a >8-clause predicate appears.

### `89e8dd0` — rung30 DCG 4/5 (+4 m3/m4)
DCG `-->` rules are expanded IN THE PARSER (`dcg_expand_clause`/`dcg_expand_body`, prolog_parse.c) into
ordinary clauses threading a difference list `(S0,S)`: `ab --> [a],[b]` becomes
`ab(S0,S) :- S0=[a|S1], S1=[b|S].`. The body unifies a logicvar with a LIST (a cons struct). Two GZ gaps
fenced every expanded clause (both are admission/codegen, NO runtime change, NO new box):
- ADMISSION `pl_gz_rule_body_goal_ok` IR_UNIFY arm (scrip.c ~536): only allowed scalar operands. Extended
  to allow a STRUCT operand on either side, copied verbatim from `pl_gz_admit`'s own top-level IR_UNIFY
  struct-unify allowance (which feeds `IR_CELL_UNIFY` shape-0).
- CODEGEN `pl_gz_rule_callee_body` IR_UNIFY arm (scrip.c ~864): passed a non-logicvar operand VERBATIM, so
  a list operand's nested logicvars kept graph-relative slot indices instead of frame slots. Now routes a
  STRUCT operand through `pl_gz_struct_slot_map` (already used by the call-arg + findall + term_string
  paths) to recursively slot-map inner vars.

Closes 4/5: `basic_terminals`, `nonterminals`, `phrase3`, `pushback_rest` (m3 and m4, byte-identical).

**`dcg_generate` (the 1 remaining) is NOT a struct-unify issue** — it is
`findall(X, phrase(item(X), [a]), As)`. `item(X) --> [X]` expands to `item(X,S0,S):-S0=[X|S]` (fine), but
the findall callee `item/3` is invoked with `[a]` (a LIST literal) as an argument. The findall arm
requires every callee arg be a logicvar (see below). So `dcg_generate` belongs to the
findall-compound-goal family with `findall_arith`, not rung30 — fix them together.

---

## The 17 remaining m3/m4 fails — PRE-TRACED map

All 17 fail identically m3≡m4. Three families:

### findall-compound-goal ×2 (findall_arith + dcg_generate) — CHEAPEST NEXT, closes BOTH
- `findall_arith`: `findall(Y, (num(X), Y is X*X), Ys)`. The findall GOAL is a CONJUNCTION. In
  `pl_gz_build_goal`'s findall arm (scrip.c ~1498), `groot = fs->gcfg->entry` is the FIRST goal's α
  (`num(X)`, an IR_GOAL), so `groot->op==IR_GOAL` passes treating the goal as just `num(X)` and the
  conjunction TAIL (`Y is X*X`) is silently dropped → Y unbound → `[_,_,_]`.
- `dcg_generate`: `findall(X, phrase(item(X), [a]), As)`. Inner goal is a single `phrase` call lowering
  to an IR_GOAL on `item/3`, but the call passes `[a]` (a list), and the findall arm (scrip.c ~1539-1542)
  rejects any callee arg that is not `IR_LOGICVAR`.
- **FIX (one change closes both):** lambda-lift the findall goal into a synthetic helper predicate at
  lower time — `'$fa0'(SharedVars) :- <the goal>.` — then findall drives the single synthetic callee, and
  the helper's body (conjunction, non-logicvar args) is just an ordinary admitted clause body. Standard
  Prolog technique. Touch points: `lower_prolog.c` findall arm (build the synthetic pred + register it);
  the findall arm in `scrip.c` then sees a clean single-IR_GOAL-with-logicvar-args goal. The shared
  variables (those appearing in the template AND the goal) become the helper's head args.
  ALTERNATIVE (bigger): teach the `IR_CELL_FINDALL` box to drive a conjunction inner goal directly
  (emit the conj as the callee body) and to bind non-logicvar callee args via synth slots. The lambda-lift
  is cleaner and reuses the whole existing single-callee drive.

### retract ×5 (B3) — NEW generator box
DB-cursor generator (semidet→nondet, HAS a β). DESIGN §3: `ret.α`=first matching clause, bind+mark→γ;
`ret.β`=unwind(mark), next matching clause. `cursor` is a frame cell. New `IR_DET_RETRACT` +
`rt_pl_retract_cell`. Admission recipe in GOAL "Admission recipe" section.

### abolish ×5 (B4) — NEW bounded box
Bulk removal, bounded (no β). New `IR_DET_ABOLISH` + `rt_pl_abolish_cell`.

### catch/throw ×5 (B2) — NEW control box (the one genuinely Prolog-specific control box)
DESIGN §4: `catch.α` pushes a catch-frame cell (catcher + &Recovery.α + trail/CP marks), runs Goal as a
closure; matching `throw` is a non-local ω landing at Recovery.α. ⚠ GATED: the catch RESIDUE globals
(`g_resolve_catch_top/stack`, `rt_catch_native`) are still live and reached by m2's catch path (m2 rung28
passes). Do NOT delete them as part of DEMOLITION until this box lands AND a probe confirms the m3/m4 catch
box does not route through them.

---

## DEMOLITION — why floor 15 did not move (probed, recorded in GOAL STATE)
"Forget m2" means LEAVE m2 RUNNING (its 114 is a HARD gate), not delete it. Every one of the 15 doomed
`g_*` is load-bearing for the m2 meta-rail / catch / resolution engine:
- `g_meta_compat`/`g_meta_builtins` → `rt_call_term`/`rt_meta_solve`, called ONLY from `IR_interp.c`
  (m2 `call/N`+`once/1`).
- `g_resolve_active` read by `interp_hooks.c` (m2 dispatch), set by `polyglot.c`.
- `g_resolve_exception` is m2's catch ball (resolution.c only).
- `g_resolve_env`(125 refs), `g_resolve_cut_flag`(43), `g_resolve_cut_barrier`(34) deeply entangled with
  resolution.c + the meta rail.
Deleting any breaks m2's HARD 114. The floor drops ONLY when m2's `call/N`/`once`/`catch` are migrated off
the meta-rail (own project) or Lon retires those m2 paths. `g_resolve_nb_store`/`g_resolve_nb_count` are
already 0-ref (the floor-15-vs-list-17 gap). So the productive direction remains LANDING NEW BBs — which
also shrinks the *reachable* legacy surface even when the global count is pinned by m2.

## Discipline followed
Two code commits to SCRIP, each gated before push (GATE-1 5/5/5 HARD, GATE-3 m2 114 + m3/m4 ratchet up,
no-new-global floor 15, cross-lang smokes) AND re-verified after each mid-session rebase. Touched only the
Prolog GZ admission/codegen (`scrip.c`), the shared `emit_bb.c` `gz_emit_callee` clause arrays, the shared
`IR_interp_state.h` clause structs, and `bb_cell_choice.cpp` — cross-lang smokes confirmed unaffected. No
FACT RULE edited. No new global, no new box, no new IR kind. All injected debug traces removed before build
(verified `grep -c` == 0). My added lines kept ≤200 chars (the codebase has many pre-existing >200 lines;
I did not add to them). PLAN.md goals table NOT touched (routine handoff). Goal-file STATE updated to 98/98.
