# HANDOFF — 2026-06-13 · Opus 4.8 · Prolog BB — DELETE the AST interpreter + new FACT RULE

## Watermark
SCRIP `603b185` · .github `(this commit)` (both build green).
**m2 114/115 · m3 83/115 · m4 83/115.** Ratchet floors UNCHANGED (m3 83 / m4 83). No score movement.

## Gates
GATE-1 5/5/5 ✓ (HARD m2 intact). GATE-3 m2=114, m3=83, m4=83.
SNOBOL4 7/7/7 ✓ · Icon m2 12 / m3 12 / m4 12 ✓ (shared `interp_hooks.c` / `IR_interp.c` touched — verified no other-language regression).

---

## Lon's directives this session
1. "If there exist any AST (`tree_t`) walker used for interpretation, then DELETE IT. We do not even want it for mode 2. An AST walker that does NOT EMIT IR nodes is worth NOTHING."
2. "Yep, if it breaks mode 2, then so it will be."
3. "Make a FACT RULE: No AST AND no IR reading or writing during mode 3 or mode 4 EXECUTION. One exception is inside these two: EVAL() and CODE()."

## What was done

### 1 · DELETED the `tree_t` AST interpreter (SCRIP `603b185`, −1693 / +13 lines)
The AST interpreter was a 1666-line island in `src/runtime/builtins/resolution.c` (former lines 395–2060). Centerpiece: **`interp_exec_builtin`** — a `switch(goal->t)` that EXECUTED `tree_t` AST nodes directly (unify, cut, arith, control constructs, sort/msort, copy_term, catch/throw-via-AST, etc.). Supporting cast deleted with it:
- `resolve_unified_term_from_expr`, `resolve_unified_eval_arith`, `resolve_unified_eval_arith_term` (AST→Term + AST arith eval)
- `resolve_term_to_synth_expr` + `resolve_synth_new/add_child/free` + `resolve_tenv_add_dedup` (reconstructed AST FROM Terms just to feed the AST switch — the worst of it)
- `resolve_call_term`, `resolve_call_term_n`, `resolve_invoke_var_goal` (the public meta-call wrappers)
- `is_user_call`, and utilities used ONLY by the interpreter: `term_order_cmp`, `copy_term_rec`, `resolve_copy_term`, `resolve_unified_deep_copy`, `resolve_iso_mod`.

**KEPT in resolution.c (lines 1–394):** CP machinery (`resolve_cp_push/pop/truncate`, `g_resolve_*`), the BB pred table (`resolve_bb_lookup/register/...`), the Prolog pred table (`resolve_pred_table_*`), dynamic-DB ops (`resolve_assert_clause`/`resolve_retract_clause`/`resolve_abolish_pred`), `resolve_env_new`. None of these call the deleted island.

### 2 · Rerouted m2 `call/N` + `once/1` to the Term-based meta rail
The ONLY external callers of the deleted code were:
- `IR_interp.c` (m2 `IR_GOAL` arm for `call/N` + `once/1`) → **rewritten** to build the extended goal `Term*` inline (append extras to the goal's functor via `term_new_compound`) and call the Term-based **`rt_call_term`** (unification.c's `meta_compile`/`rt_meta_solve` rail — the SAME engine the GZ m3/m4 path uses). This is WHY m2 did not drop: the AST interpreter provided nothing the Term rail couldn't.
- `interp_hooks.c` (a dead `g_resolve_active` Prolog branch that `abort()`ed anyway) → removed its lone call into the deleted code.
- Header decls removed from `resolution.h`, `pl_interp.h`, `prolog_builtin.h`; orphan `resolve_execute_program_unified` decl removed.

**Audit:** all 8 deleted public names grep to 0 references. The only remaining `switch(->t)` over `tree_t` in runtime/interp is `is_suspendable` (gen_runtime.c) — a shape CLASSIFIER for the Icon lowerer (returns 0/1, emits nothing-but-decides), not an executor. Left in place.

### 3 · New FACT RULE — byte-identical across all five GOAL-*-BB files
**"NO AST AND NO IR DURING MODE-3/MODE-4 EXECUTION"** added before the NO VALUE STACK rule in GOAL-SNOBOL4-BB / GOAL-ICON-BB / GOAL-PROLOG-BB / GOAL-RAKU-BB / GOAL-SNOCONE-IR-BB. Body md5 `f624eb8e23b69518ebba4cf62074b3d8` (verified identical in all five). Substance:
- During EXECUTION of a mode-3/4 program, nothing reads or writes the AST (`tree_t`) or IR (`IR_t`/`IR_graph_t`). The compiler reads IR ONCE before execution to emit the m3 image / m4 `.S`; the produced binary runs with zero reference to either tree.
- Subsumes IR-NEVER-TOUCHED, extends to the AST. An AST walker that does not EMIT IR may not exist on any run path — not even mode 2. (`IR_interp_once` is the sole sanctioned IR walker, `--run`-only.)
- **THE ONE EXCEPTION — `EVAL()` and `CODE()`** (SNOBOL4 dynamic-compilation builtins, `CONVE_fn`→`EXPVAL_fn` / `g_eval_str_hook`/`g_eval_pat_hook`). Compiling a string to executable form at runtime is intrinsic to their meaning, so the prohibition does NOT apply inside `EVAL`/`CODE` (and only there).
- FORBIDDEN on the run path: any `rt_*`/template-called fn taking `IR_t*`/`IR_graph_t*`/`tree_t*`, walking `->operands`/`->c[]`/`->t`/`->op`, reading `IR_LIT`/`IR_EXEC`, dispatching on `IR_e`/`tree_e`, or baking a live node address into emitted code. Unconverted box = LOUD `x86_bomb`, never a silent read.

## Why m2 didn't move (the important insight)
The AST interpreter was a parallel m2-ONLY shadow of the Term-based meta rail. SCRIP already had TWO meta-call engines: (1) `meta_compile`/`rt_meta_solve`/`rt_call_term` in unification.c — Term-based, solves a goal by jumping to the GZ-emitted predicate's α-label, used by m3/m4 GZ; and (2) `interp_exec_builtin` in resolution.c — AST-based, m2-only. Deleting (2) and pointing m2's `call/N` at (1) lost nothing because (1) is strictly more aligned with the architecture. The m2 IR-graph interpreter (`IR_interp_once`) was never the AST interpreter — it walks IR, which is sanctioned.

## Completion proof
```
grep -rn "interp_exec_builtin|resolve_call_term|resolve_call_term_n|resolve_invoke_var_goal|resolve_unified_term_from_expr|resolve_unified_eval_arith|resolve_term_to_synth_expr|is_user_call" src/ → 0
md5 of FACT RULE block, all 5 GOAL files → f624eb8e23b69518ebba4cf62074b3d8 (identical)
make scrip + make libscrip_rt → rc=0
GATE-1 5/5/5 · GATE-3 m2 114 / m3 83 / m4 83 · SNOBOL4 7/7 · Icon 12/12/12
```

## Next session
Open work unchanged from prior handoffs: GROUP B rungs (B2 catch/throw, B3 retract, B4 abolish, B5 DCG) and the remaining dead-code demolition of `resolution.c`'s control engine + `resolve_bb_env_*`. This session REMOVED standing debt (the AST interpreter and its ~1.7k lines) and added no new debt. The new FACT RULE is now the governing law for any future m3/m4 work: a box either reads only `Term*`/`DESCR_t` at runtime, or it is an `x86_bomb` — with `EVAL`/`CODE` the sole carve-out.
