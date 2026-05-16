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
| **PJ-2** | Create `src/lower/lower_pl.c` + `.h`. `lower_pl_predicate(tree_t*)` returns NULL placeholder. Wire `lower()` to populate `dcg_table[i].ir_body = NULL`. | Build clean; gates unchanged |
| **PJ-3** | Replace `[NO-AST]` stub in `sm_interp.c case SM_BB_ONCE_PROC` with body handler: lookup `dcg_table[name/arity]`, wrap in `pl_dcg_state_t`, drive via `bb_broker`. Fall back to legacy stub when `ir_body == NULL`. | smoke_prolog still 0/5 (no IR yet) |
| **PJ-4** | `lower_pl_expr_node` handles TT_FNC(write/nl), TT_UNIFY, TT_FNC("is"), TT_VAR, TT_ILIT/QLIT/NAME. Wire into `lower_pl_predicate` building `IR_SEQ`. | smoke_prolog write/unify/arith PASS |
| **PJ-5** | `IR_PL_CHOICE` executor + `lower_pl_choice(clauses[], n)`. α: trail_mark, try clause 0. β: trail_unwind, advance, try next. ω: exhausted. | smoke_prolog clause PASS |
| **PJ-6** | `IR_PL_CALL` executor (recursion). Lookup `dcg_table[name/arity]`, fresh state, inner drive. Save choice-point depth as cut barrier. | smoke_prolog recursion PASS → 5/5 |
| **PJ-7** | `IR_PL_CUT` executor. Discard choice points to enclosing barrier. Mark surrounding CHOICE so β skips past cut clauses. | broker `!` tests PASS |
| **PJ-8** | Delete `pl_runtime.c` AST-walking paths for modes 2/3/4: `pl_pred_table_lookup_global`, `pl_unified_term_from_expr`, `interp_exec_pl_builtin` become mode-1-only. Modes 2/3/4 use `g_dcg_table` exclusively. | smoke_prolog 5/5; honest_prolog gate green |

## Done when

`SM_BB_ONCE_PROC` routes through `pl_bb_dcg` + `dcg_table[i].ir_body`. `pl_bb_build` lazy fallbacks replaced. Inline x86 emitters for Prolog primitives written (mode 4). `pl_runtime.c` AST-walking deleted for modes 2/3/4 (mode 1 retains as reference). smoke_prolog 5/5. GATE-1..4 green.

## Watermark

```
one4all: e6af028c (PJ-1 landed)  corpus: 1fe096c
smoke_prolog: 0/5 (intentional baseline; PJ-1 is skeleton-only)
Other smokes: snobol4 7/7, icon 5/5, snocone 5/5, rebus 4/4, raku 5/5
honest icon-suite: 277 PASS / 0 FAIL / 0 ABORT
broker: 16/49
```

**Session 2026-05-15 fu#4 (Opus 4.7):** PJ-1 closed at `e6af028c`. Added `pl_bb_dcg` bridge to `pl_runtime.c` (mirrors `icn_bb_dcg` byte-for-byte: `pl_dcg_state_t { IR_block_t *cfg; int first; }`, same α-resets-first / once-then-resume dispatch). Added `g_dcg_table[PL_DCG_TABLE_MAX]` + `g_dcg_count` registry with `pl_dcg_lookup(name, arity)` and `pl_dcg_register(name, arity, ir_body)`. New types `PlScopeEnt`/`PlScope`/`Pl_PredEntry_BB` in `pl_runtime.h` mirror Icon equivalents (minus `tree_t* proc` per NO-AST-WALK rule). Build clean. All gates unchanged.

Env note: `libgc-dev` was missing at session start; `apt-get install -y libgc-dev` fixed it. `scripts/install_system_packages.sh` already lists it in PKGS — Session Setup may benefit from running it on dirty containers.

**NEXT:** PJ-2 — create `src/lower/lower_pl.c` + `lower_pl.h`. Implement `lower_pl_predicate(tree_t*)` returning NULL initially as placeholder; wire `lower()` to populate `g_dcg_table[i].ir_body = NULL` per Prolog predicate at proc-table-skeleton emission. Mirror of `lower_icn_proc_body`.
