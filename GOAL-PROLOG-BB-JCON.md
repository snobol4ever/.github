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
| **PJ-5/6** 🔄 | `IR_PL_CHOICE` (multi-clause) + `IR_PL_CALL` (predicate call with arg binding). WIP `7be007c2`. fact/1 lowers and executes correctly. KNOWN BUG: IR_PL_CHOICE has two shapes that collide: (A) multi-clause uses c[i]->opaque=IR_block_t*; (B) inline ';' disjunction uses c[i] as raw IR_t* from lower_pl_seq — executor reads opaque=NULL → main/0 ir_body=NULL. FIX: split IR_PL_ALT (new kind, inline two-branch, drives c[0]/c[1] directly as IR_t*) from IR_PL_CHOICE (multi-clause only, each c[i]->opaque=IR_block_t*). Add IR_PL_ALT to IR.h + ir_exec.c; change lower_pl_stmt_node ';' case to emit IR_PL_ALT. | smoke_prolog clause+recursion PASS → 5/5 |
| **PJ-7** | `IR_PL_CUT` executor. Discard choice points to enclosing barrier. Mark surrounding CHOICE so β skips past cut clauses. | broker `!` tests PASS |
| **PJ-8** | Delete `pl_runtime.c` AST-walking paths for modes 2/3/4: `pl_pred_table_lookup_global`, `pl_unified_term_from_expr`, `interp_exec_pl_builtin` become mode-1-only. Modes 2/3/4 use `g_dcg_table` exclusively. | smoke_prolog 5/5; honest_prolog gate green |

## Done when

`SM_BB_ONCE_PROC` routes through `pl_bb_dcg` + `dcg_table[i].ir_body`. `pl_bb_build` lazy fallbacks replaced. Inline x86 emitters for Prolog primitives written (mode 4). `pl_runtime.c` AST-walking deleted for modes 2/3/4 (mode 1 retains as reference). smoke_prolog 5/5. GATE-1..4 green.

## Watermark

```
one4all: 7be007c2 (PJ-5/6 WIP)  corpus: 1fe096c
smoke_prolog: 3/5 (write_atom+unify+arith PASS; clause+recursion blocked by IR_PL_CHOICE/IR_PL_ALT split bug)
Other smokes: snobol4 7/7, icon 5/5, snocone 5/5, rebus 4/4, raku 5/5
broker: 18/49
```

**Session 2026-05-16 (Claude Sonnet 4.6):** PJ-2 `d9fe1496`, PJ-3 `f5db4e5f`, PJ-4 `cb1417a5` landed. PJ-5/6 WIP `7be007c2`.

Key facts for next session:
- `libgc-dev` needed: `apt-get install -y libgc-dev` (already in install_system_packages.sh).
- arity-from-key fix in `pl_bb_once_proc_by_name`: `sm_emit_si` for SM_BB_ONCE_PROC always passes arity=0; fix parses arity from the slash in the key string.
- IR kinds added: `IR_PL_BUILTIN`, `IR_PL_VAR`, `IR_PL_ATOM`, `IR_PL_ARITH` in `IR.h`; executors in `ir_exec.c`.
- `pl_bb_env_push(n)` / `pl_bb_env_pop(saved)` in `pl_runtime.c/.h`; wired in `sm_interp.c SM_BB_ONCE_PROC`.
- `lower_pl_clause_body`: inserts `IR_PL_UNIFY(IR_PL_VAR(i), head_term_i)` for each head arg.

**NEXT (PJ-5/6 fix):** Add `IR_PL_ALT` to `IR.h` (new kind, inline two-branch disjunction). In `ir_exec.c`: `IR_PL_ALT` drives `c[0]` directly (as IR_t*, no opaque); on fail, drives `c[1]`. Keep `IR_PL_CHOICE` for multi-clause only (c[i]->opaque=IR_block_t*). In `lower_pl.c`: change ';' case in `lower_pl_stmt_node` to emit `IR_PL_ALT` (not `IR_PL_CHOICE`). After this fix main/0 with ';' will lower, smoke_prolog clause+recursion should PASS → 5/5.
