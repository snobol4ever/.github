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
| **PJ-5a** ✅ | Fix entry-point invocation + add IR_PL_SEQ + cut barrier. (1) `lower.c` TT_CHOICE-subject stmts made no-op (was auto-invoking every defined predicate at program start, with no args, before main); `:- initialization(name).` now emits `SM_BB_ONCE_PROC name/arity` (was no-op). (2) Added `IR_PL_SEQ` opcode + executor: short-circuit on first goal failure, succeed if all succeed (replaces Icon-flavored IR_SEQ in `lower_pl.c`). (3) `IR_PL_CUT` now sets `g_pl_cut_flag`; `IR_PL_CHOICE` checks it and stops trying alternatives. smoke_prolog 4/5: recursion PASS (was FAIL). broker: 19/49 (was 18). Other smokes & honest gates unchanged. |
| **PJ-7** ✅ | Backtracking pump for `clause` test landed. Three coordinated changes in `src/lower/ir_exec.c`: (1) `IR_PL_CHOICE` made stateful — `nd->state` = next clause to try; resume picks up where prior success left off via `IR_exec_resume` (no reset). (2) `IR_PL_CALL` made resumable — stores `PlCallSt{callee_env, saved_env, trail_mark, nslots}` in `nd->opaque`; shared-term propagation (the same `term_new_var(ai)` instance lives in both caller's `saved_env[caller_slot]` AND `callee_env[ai]` so unifications flow via `term_deref` and respect trail unwind). (3) `IR_PL_SEQ` made backtracking — on goal-j failure, scans leftward via `backtrack_from` cursor for resumable goal (IR_PL_CALL state==1 or IR_PL_ALT state==1); calls `IR_exec_resume` on callee's body; on success restarts forward at `found+1`; on exhaustion continues leftward without restarting the exhausted call. smoke_prolog 5/5: clause PASS (was FAIL). broker: 20/49 (was 19). |
| **PJ-8** ✅ | Stub the AST-walking Prolog branch in `_usercall_hook` (`src/driver/interp_hooks.c:81`) when SM dispatch is active. Single 5-line change: gates the `g_pl_active` branch with `if (g_sm_dispatch_active && !g_ast_pump_active)` printing `[NO-AST] _usercall_hook prolog branch: needs fresh SM/BB lowering (PJ-8)` and returning FAILDESCR. This shuts down the only path by which SM-dispatch code reaches `pl_unified_term_from_expr` / `pl_pred_table_lookup` AST helpers. The `pl_broker.c` AST callers (lines 31, 90-91, 122, 387, 396) are only reached from mode 1 (`pl_runtime.c` and `interp_eval.c`), which RULES.md keeps as the reference AST-walking path. No changes to `pl_broker.c` needed. Gates: smoke_prolog 5/5, broker 20/49, honest_prolog 124/0/0, honest_icon 277/0/0 — all unchanged. |
| **PJ-9a** ✅ | **Wired `h_bb_once_proc` in sm_jit_interp.c through `pl_bb_once_proc_by_name`+`bb_broker` (Mode 3 JIT dispatch).** Was `[NO-AST]` stub, so `--jit-run` Prolog crosscheck was 0/4. Mode 2 (`sm_interp.c:671`) already did this work; Mode 3 now mirrors it: lookup name+arity from `CUR_INS->a[0].s` / `a[1].i`, call `pl_bb_once_proc_by_name`, on `node.fn` push/run/pop `pl_bb_env`, drive via `bb_broker(node, BB_ONCE, NULL, NULL)`, set `STATE->last_ok`. On miss keeps the `[NO-AST]` print. Also regenerated stale `snocone_parse.tab.h` (out-of-sync since `4aa8727b` PST-SC-4b blocked all builds). Gates: `test_crosscheck_prolog.sh` 0→**4/4** ✅ (jit-run rows now PASS); smoke_prolog 5/5, honest_prolog 124/0/0, honest_icon 277/0/0, unified_broker 20/49 — all unchanged. |

## Done when

`SM_BB_ONCE_PROC` routes through `pl_bb_dcg` + `dcg_table[i].ir_body` ✅. PJ-8 closed: SM-dispatch no longer reaches AST helpers (the `_usercall_hook` Prolog branch is `[NO-AST]`-stubbed). `pl_runtime.c` AST-walking paths remain only for mode 1 (`--ir-run` reference). `pl_bb_build` lazy fallbacks replaced ✅. Inline x86 emitters for Prolog primitives written (mode 4) — STILL TODO for full Mode 4 deliverable. smoke_prolog 5/5 ✅. GATE-1..4 green ✅.

## Watermark

```
one4all: fc6fa0a8 (PJ-9a)  corpus: 1fe096c
smoke_prolog: 5/5 ✅ (write_atom+unify+arith+clause+recursion all PASS)
crosscheck_prolog: 4/4 ✅ (hello+backtrack+arith+recursion all PASS across --ir-run/--sm-run/--jit-run)
Other smokes: snobol4 7/7, icon 5/5, snocone 5/5, rebus 4/4, raku 5/5
honest gates: prolog 124/0/0, icon 277/0/0 (no regression)
broker: 20/49 (was 19)
NOTE: PJ-9a also regenerated snocone_parse.tab.h from snocone_parse.y to fix the
upstream PST-SC-4b (4aa8727b) build break ('ScParseState' has no member
'if_before_body'). Tree now builds clean from HEAD.
```

**Session 2026-05-16 (Claude Opus 4.7):** PJ-9a landed. Mode-3 JIT dispatcher's `h_bb_once_proc` was a `[NO-AST]` stub at `src/processor/sm_jit_interp.c:288`; `--jit-run` Prolog crosscheck was 0/4. Wired it through `pl_bb_once_proc_by_name` + `bb_broker` mirroring Mode 2's `sm_interp.c:671` body (push `pl_bb_env`, drive `bb_broker(node, BB_ONCE, NULL, NULL)`, pop env, set `STATE->last_ok`). On lookup miss the `[NO-AST]` print is retained. `test_crosscheck_prolog.sh` 0/4 → 4/4 (hello+backtrack+arith+recursion now agree across all three modes). Independently regenerated `snocone_parse.tab.h` (was stale from upstream PST-SC-4b commit `4aa8727b` which committed the `.y` change without regenerating headers — that broke every build since PJ-8). All other gates unchanged: smoke_prolog 5/5, honest_prolog 124/0/0, honest_icon 277/0/0, unified_broker 20/49.

**Open findings (post-PJ-9a audit, same session):** Two `[NO-AST]` stubs in mode 2/3 dispatch are still reachable from legitimate programs and would be candidate rungs (PJ-9b? PJ-9c?):
- `sm_interp.c:1266` and `sm_jit_interp.c:804` — `SM_CALL_FN "PL_UNIFY"` stub. Emitted by `lower.c:1185` for top-level `TT_UNIFY` (not in any current gate's expected-pass set, but reachable).
- `sm_interp.c:1290` and `sm_jit_interp.c:828` — `SM_CALL_FN "PL_BUILTIN"` stub. Emitted by `lower.c:1018` for **top-level Prolog directives** like `:- assertz(color(red)).`. Verified reachable: `rung13_assertz_*.pl` programs fire this stub in both `--sm-run` and `--jit-run`. The body-level path (predicates calling `write`, `is`, `assertz`, etc.) already goes through `IR_PL_BUILTIN` via `lower_pl.c`; the gap is *directive-level* lowering in shared `lower.c` not yet routed to the IR_PL_* pipeline. Honest gate doesn't catch it because `--ir-run` oracle also fails on these programs.
- Mode 4 (x86 / .NET emit) `SM_BB_ONCE_PROC` is a no-op fallthrough in `emit_net.c:1108`; no `emit_x86.c` Prolog path. This is the "inline x86 emitters for Prolog primitives" item in Done-When.

**Session 2026-05-16f (Claude Opus 4.7):** PJ-8 landed as a 5-line surgical stub. In `src/driver/interp_hooks.c:81`, the `g_pl_active` branch of `_usercall_hook` is now gated by `if (g_sm_dispatch_active && !g_ast_pump_active)` which prints `[NO-AST] _usercall_hook prolog branch: needs fresh SM/BB lowering (PJ-8)` and returns FAILDESCR. This was the ONLY SM-dispatch-reachable AST path into `pl_unified_term_from_expr` / `pl_pred_table_lookup`. The other AST callers in `pl_broker.c` (lines 31, 90-91, 122, 387, 396) are only reached from mode 1 (`pl_runtime.c` + `interp_eval.c`), which per RULES.md remains the authoritative AST-walking reference path. All gates green and unchanged from PJ-7.

**Session 2026-05-16e (Claude Opus 4.7):** PJ-7 landed. Backtracking pump for Prolog conjunction works. Three coordinated changes in `src/lower/ir_exec.c`:

(1) **`IR_PL_CHOICE` made stateful** — `nd->state` = next clause index to try (0=fresh). On re-entry via `IR_exec_resume`, the for-loop body `for (ci = nd->state; ci < nd->n; ci++)` skips clauses already tried. On success: `nd->state = ci+1`. On exhaustion: `nd->state = 0` and FAIL.

(2) **`IR_PL_CALL` made resumable** — first call stores `PlCallSt{callee_env, saved_env, trail_mark, nslots}` in `nd->opaque` and sets `nd->state = 1`. The KEY insight: **shared-term propagation** — when caller arg is an unbound `IR_PL_VAR`, allocate one `term_new_var(ai)` and store the SAME pointer in both `callee_env[ai]` AND `saved_env[caller_slot]`. The callee's body unifies via `unify()` which trail-pushes binding. Caller reads `g_pl_env[slot]` and does `term_deref` to get current binding. Trail unwind correctly reveals next solution. Earlier attempt used `term_deref(callee_env[ai])` for propagation — that's WRONG because deref returns a fresh atom value that doesn't track future rebindings.

(3) **`IR_PL_SEQ` made backtracking** — added `int backtrack_from` cursor. Forward: run goals 0..n-1; on success advance. On failure: set `backtrack_from = j` and enter backtrack loop. Backtrack scans left of `backtrack_from` for nearest goal with state==1 (resumable IR_PL_CALL or retryable IR_PL_ALT). For CALL: unwind trail to `cs->trail_mark`, swap `g_pl_env = cs->callee_env`, refresh trail mark, call `IR_exec_resume(rbb->ir_body)`. If yields: re-propagate shared terms, restart forward at `found+1`, `backtrack_from = -1`. If exhausted: free cs, opaque=NULL, state=0, `backtrack_from = found` (continue scanning further left). For ALT: set state=2 (signal to ALT case "skip left, run right"), execute c[1].

(4) **`IR_PL_ALT` extended** — state==2 means "called from SEQ backtrack pump: skip left branch and run right directly." After taking right branch, state reset to 0.

Key facts for next session:
- `libgc-dev` needed: `apt-get install -y libgc-dev`.
- IR_t union: `ival`, `dval`, `sval` all alias. Always use `ival2` for integer fields on nodes that also carry `sval`.
- tree_t.v union: `sval`, `ival`, `dval` alias. Arity must be passed explicitly or extracted from sval key.
- TT_FNC(">" / "<" / ">=" / "<=" / "=:=" / "=\\=") are how Prolog comparison goals appear. Already handled in lower_pl.c.
- Atom arg-binding check is `av.v == DT_S && av.s && av.s[0]` (was `(DT_S || DT_SNUL) && av.s` — that wrongly created empty atom for NULVCL).
- The `--ir-run` mode is the only place these IR_PL_* opcodes execute. Modes 2/3/4 (SM dispatch) currently route through `_usercall_hook` in `interp_hooks.c` which still calls AST-walking `pl_unified_term_from_expr` — PJ-8 cleans that up.

**NEXT (PJ-8 — delete AST walking from modes 2/3/4):**
Three callers outside mode 1 (interp_eval.c) need stubbing per RULES.md `[NO-AST]` template:
- `src/driver/interp_hooks.c:88` — `_usercall_hook` Prolog branch calls `pl_unified_term_from_expr`. Replace with `[NO-AST] _usercall_hook prolog` stub + `st->last_ok = 0`. This routes mode-2/3/4 SM dispatch through fresh `g_dcg_table` lookup instead.
- `src/frontend/prolog/pl_broker.c` — entire file is AST-walking legacy mode-2. Lines 31 (interp_exec_pl_builtin), 90-91 (pl_unified_term_from_expr), 122 (head-arg unify), 387 (pl_pred_table_lookup_global), 396 (caller_args). Stub each call site.

Mode 1 reference path stays: `src/driver/interp_eval.c:3633-34` keeps calling `pl_unified_term_from_expr` (this is `--ir-run` standalone AST interp per RULES.md).

Gate: smoke_prolog 5/5 must stay; honest_prolog 124/0/0 stays; broker baseline at 20/49 — some broker tests may shift if pl_broker.c stub triggers different paths.
