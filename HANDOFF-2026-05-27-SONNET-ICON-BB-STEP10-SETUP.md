# HANDOFF — ICON-BB session end — Claude Sonnet 4.6 — 2026-05-27

## Session summary

Three items completed this session:

1. **LFJ-15b** (`6a631124`) — All six _threaded_b AG-pure intercept families (3/5/6/7/8.1/8.2) folded into `_ag` variants. `lower_icn_expr_threaded_b` early-exits cleanly for all AG-pure kinds.

2. **Step 9** (`1dfe9631`) — AG-pure N-ary applies: BB_LCONCAT, BB_SECTION, BB_IDX, BB_IDX_SET. Lower-side `_ag` variants + executor AG-pure branches gated on `nd->α==NULL`.

3. **GOAL-ICON-BB.md pruned** (`ca0a8ac2`) — 302→119 lines. LFJ staircase collapsed to summary; completed AG steps to a table; dead legacy-ref section dropped.

## Gates throughout
smoke_icon 5/5 · icon_all_rungs 198/268 · smoke_prolog 5/5 · broker 30/52 · FACT RULE 0

## Next: Step 10 — Sidecar cleanup

Delete `bb_operand_aux_set/get` from Icon lower path. Sidecar struct stays for Prolog/SNOBOL4.

**Four touch points:**

1. `lower_icn.c` Family 1 (BB_ASSIGN deep-thread, `_threaded_b` post-processing):
   - Currently: `bb_operand_aux_set(cfg, nd, &peer_one, 1)` then executor reads `ops[0]->value`
   - Target: executor reads `peek(0)` (rhs ran in chain before apply node)
   - Gate: `grep bb_operand_aux_set src/lower/lower_icn.c | wc -l` drops by 1

2. `lower_icn.c` Family 2 (BB_CALL non-gen args, `_threaded_b` post-processing):
   - Currently: `bb_operand_aux_set(cfg, nd, peer_buf, nargs)` then executor reads `call_ops[j]->value`
   - Target: args already γ-chained; executor reads `peek(nargs-1-j)` for arg j
   - Gate: `grep bb_operand_aux_set src/lower/lower_icn.c | wc -l` drops to 0

3. `bb_exec.c:845` BB_ASSIGN apply:
   - Currently: `call_ops = bb_operand_aux_get(...)` then `call_ops[0]->value`
   - Target: AG-pure branch `if (!nd->α && !nd->β)` → `peek(0)` = rhs value

4. `bb_exec.c:922` BB_CALL non-gen apply:
   - Currently: `call_ops = bb_operand_aux_get(...)` then `call_ops[j]->value` for j in 0..nargs-1
   - Target: AG-pure branch → `peek(nargs-1-j)` for arg j (ring ordering: last-pushed = peek(0) = last arg)
   - Generator-arg odometer path (state==2) stays on current path — do NOT touch

**Caution:** BB_CALL is complex (user procs, gen-proc pump, odometer). Only add the AG-pure branch for the `is_deep==1 && !has_gen_arg` path. All other BB_CALL paths unchanged.
