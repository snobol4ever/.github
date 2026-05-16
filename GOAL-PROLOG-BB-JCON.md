# GOAL-PROLOG-BB-JCON.md — Prolog: BB-land DCG per predicate + lower_pl DCG

**Repo:** one4all + corpus + .github
**Prereq:** GOAL-PROLOG-BB-COMPLETE ✅ `c9b7428d` (PB-8 honest 111/294 FAIL=0 ABORT=0)
**Sister:** GOAL-ICON-BB-JCON.md — mirror; only port semantics and names differ.

## Invariants (READ FIRST)

The five invariants from GOAL-ICON-BB-JCON.md apply verbatim with names substituted:
Icon `proc_table` ↔ Prolog `dcg_table`; `icn_bb_dcg` ↔ `pl_bb_dcg`; `SM_BB_PUMP_PROC` ↔ `SM_BB_ONCE_PROC`. **Cross-language semantics differ per port** — Icon β advances a generator counter; Prolog β pops a choice-point + unwinds the trail; SNOBOL4 β backtracks the pattern anchor. Never invoke language-A's SM-bridge handler with language-B's BB object.

## Session Setup

```
cd /home/claude/one4all && bash scripts/build_scrip.sh
```

## Architecture

Same shape as Icon (SM is entry; SM_BB_XXX bridges into BB-land; nothing dereferences `tree_t*` at runtime), with three differences in port semantics:

| Port | Icon semantics | Prolog semantics |
|---|---|---|
| α | enter generator, first attempt | enter predicate, first clause, trail_mark |
| β | resume, advance generator state | retry: trail_unwind, advance to next clause |
| γ | success (yield value) | success (unification succeeded; head bound) |
| ω | failure (exhausted) | failure (no more clauses) |

**Target shape per Prolog program:** the SM stream contains one `SM_BB_ONCE_PROC` per top-level call (typically just `?- main.`). Each predicate's body is one `IR_block_t*` in `dcg_table[i].ir_body`. Multi-clause predicates compose alternatives via `IR_PL_CHOICE`; recursive calls via `IR_PL_CALL`; cut via `IR_PL_CUT`.

**The `pl_bb_dcg` bridge (to be added):**
```c
typedef struct { IR_block_t *cfg; int first; int trail_mark; } pl_dcg_state_t;
DESCR_t pl_bb_dcg(void *zeta, int entry) {
    pl_dcg_state_t *z = zeta;
    if (entry == α) { z->first = 1; z->trail_mark = pl_trail_top(); }
    if (z->first) { z->first = 0; return IR_exec_once(z->cfg); }
    pl_trail_unwind(z->trail_mark);
    return IR_exec_resume(z->cfg);
}
```

**`dcg_table` (to be added):** mirror of `proc_table`. Indexed by `name/arity`. Each entry holds `ir_body : IR_block_t*` plus argument scope info.

## IR executor cases needed (ir_exec.c)

| IR kind | Purpose | Notes |
|---|---|---|
| `IR_PL_UNIFY` | `X = Y` | calls `pl_unify(L, R)`; γ on success, ω on fail (with trail unwind via caller's mark) |
| `IR_PL_CALL` | predicate call | look up `dcg_table[name/arity]`, build fresh `pl_dcg_state_t`, drive via inner `IR_exec_once`/`_resume` |
| `IR_PL_CHOICE` | multi-clause `A; B; C` | `nd->state` = clause index; `nd->counter` = saved trail position; β unwinds + advances |
| `IR_PL_CUT` | `!` | discard choice points back to enclosing barrier; mark surrounding CHOICE so β skips past cut |
| `IR_PL_BUILTIN` | `write`, `nl`, `is`, type tests | direct C calls; γ on success, ω on failure |

## Gates

```
GATE-1  bash scripts/test_smoke_prolog.sh               # PASS=5 (currently 0)
GATE-2  bash scripts/test_smoke_unified_broker.sh       # PASS >= baseline (Prolog rows non-regressive)
GATE-3  bash scripts/test_prolog_rung_suite.sh          # PASS >= prev
GATE-4  bash scripts/test_icon_sm_no_ast_walk.sh        # cross-language honest gate non-regressive
```

## Active steps

| Step | Description | Gate |
|---|---|---|
| **PJ-1** ✅ | Add `pl_bb_dcg` bridge + `g_dcg_table[]` registry skeleton. Mirror of `icn_bb_dcg`/`proc_table`. Landed at one4all `e6af028c`. | Build clean; gates unchanged |
| **PJ-2** ✅ | Create `src/lower/lower_pl.c` + `.h`. `lower_pl_predicate(tree_t*)` returns NULL placeholder. Wire `lower()` to populate `dcg_table[i].ir_body = NULL`. Landed `d9fe1496`. | Build clean; gates unchanged |
| **PJ-3** ✅ | Replace `[NO-AST]` stub in `sm_interp.c case SM_BB_ONCE_PROC` with body handler: lookup `dcg_table[name/arity]`, wrap via `pl_bb_once_proc_by_name`, drive via `bb_broker`. Landed `f5db4e5f`. | smoke_prolog still 0/5 (no IR yet) |
| **PJ-4** ✅ | `lower_pl_expr_node` handles TT_FNC(write/nl), TT_UNIFY, TT_FNC("is"), TT_VAR, TT_ILIT/QLIT/NAME. Wire into `lower_pl_predicate` building `IR_SEQ`. IR_PL_BUILTIN/VAR/ATOM/ARITH/UNIFY executors in ir_exec.c. pl_bb_env_push/pop. Landed `cb1417a5`. | smoke_prolog 3/5 (write+unify+arith PASS) |
| **PJ-5/6** ✅ | IR_PL_ALT landed `141c4816`. IR_PL_CHOICE/ALT split done; arity emit fix; n-ary comma fix; ival/sval union collision fixed (IR_PL_VAR/CALL/BUILTIN). smoke_prolog 3/5. NEXT blockers: (A) head-arg unification: IR_PL_UNIFY executor must handle IR_LIT_I/F match (for count(0)); (B) comparison ops: lower_pl_stmt_node must route TT_FNC(">/<") to builtin, not IR_PL_CALL; (C) backtracking: IR_PL_CHOICE multi-clause + pump for clause test. |
| **PJ-7** | `IR_PL_CUT` executor. Discard choice points to enclosing barrier. Mark surrounding CHOICE so β skips past cut clauses. | broker `!` tests PASS |
| **PJ-8** | Delete `pl_runtime.c` AST-walking paths for modes 2/3/4: `pl_pred_table_lookup_global`, `pl_unified_term_from_expr`, `interp_exec_pl_builtin` become mode-1-only. Modes 2/3/4 use `g_dcg_table` exclusively. | smoke_prolog 5/5; honest_prolog gate green |

## Done when

`SM_BB_ONCE_PROC` routes through `pl_bb_dcg` + `dcg_table[i].ir_body`. `pl_bb_build` lazy fallbacks replaced. Inline x86 emitters for Prolog primitives written (mode 4). `pl_runtime.c` AST-walking deleted for modes 2/3/4 (mode 1 retains as reference). smoke_prolog 5/5. GATE-1..4 green.

## Watermark

```
one4all: 141c4816 (PJ-5/6 landed)  corpus: 1fe096c
smoke_prolog: 3/5 (write_atom+unify+arith PASS; clause+recursion blocked: IR_UNIFY literal match + TT_FNC comparison routing + backtracking pump)
Other smokes: snobol4 7/7, icon 5/5, snocone 5/5, rebus 4/4, raku 5/5
broker: 18/49
```

**Session 2026-05-16b (Claude Sonnet 4.6):** PJ-5/6 landed `141c4816`. IR_PL_ALT split done. Five union-collision bugs fixed (ival/sval alias in IR_t). N-ary comma. Arity emit fix.

Key facts for next session:
- `libgc-dev` needed: `apt-get install -y libgc-dev`.
- IR_t union: `ival`, `dval`, `sval` all alias. Always use `ival2` for integer fields on nodes that also carry `sval`.
- tree_t.v union: `sval`, `ival`, `dval` alias. Last write wins. `lower_clause` writes sval then dval then ival — so only `ival` (= n_vars) survives. Arity must be passed explicitly or extracted from sval key.
- TT_FNC(">" / "<" / ">=" / "<=" / "=:=" / "=\\=") are how Prolog comparison goals appear — NOT TT_GT/TT_LT. lower_pl_stmt_node generic FNC handler must intercept these before falling to IR_PL_CALL.
- IR_PL_UNIFY executor needs to handle IR_LIT_I/IR_LIT_F on RHS (for head-arg matching like count(0)).
- IR_PL_CHOICE (multi-clause): currently iterates all clauses eagerly. For backtracking (clause test), need pump mode — IR_PL_CALL should use IR_exec_pump or drive IR_PL_CHOICE as generator.

**NEXT (PJ-5 continuation — smoke_prolog 5/5):**
1. In `lower_pl_stmt_node`: add TT_FNC(">") / TT_FNC("<") / TT_FNC(">=") / TT_FNC("<=") / TT_FNC("=:=") / TT_FNC("=\\=") cases — emit IR_PL_BUILTIN with sval=op and two term children (same as TT_GT branch already added for non-FNC path).
2. In `ir_exec.c` IR_PL_UNIFY: add handling for IR_LIT_I/IR_LIT_F on RHS when LHS is IR_PL_VAR (unify slot with integer/float literal).
3. For `recursion` test: with fixes (1) and (2), count/1 IR should build and N>0 should work. Verify count(0):-! fires the cut correctly via IR_PL_CHOICE first-clause match.
4. For `clause` test: requires backtracking pump over fact/1 clauses driven by fail. May need IR_PL_CALL to drive IR_PL_CHOICE as a generator on repeated calls from parent fail.
