# HANDOFF 2026-05-26 (Opus) — Prolog DCG phrase + compound-write landed; next is unify-based call binding

**SCRIP HEAD: `f43aff1d` (clean, all gates green). `.github`: this session.**
smoke_prolog 5/5 · prolog_bb_honest 124/0/0 · smoke_icon 5/5 · smoke_snobol4 13/13 ·
GATE-3 prolog_rung_suite 19/107 (was 16 at session start).

## Landed this session (two commits, both verified, zero regressions)

### `0c547c01` — lower-time `phrase/2,3` DCG rewrite (`src/lower/lower_pl.c`)
Intercept `phrase` in `lower_pl_goal` BEFORE the general predicate-call case and rewrite:
`phrase(NT,List) -> NT(List,[])`, `phrase(NT,List,Rest) -> NT(List,Rest)`.
NT atom → callee `NT/2`; NT compound `NT(A..)` → callee `NT/arity+2` (A.. kept).
Builds a `BB_PL_CALL` with `zc->args` = NT's lowered args + List + (Rest|`[]`-atom).
Previously `phrase/N` hit a `pl_bb_lookup` miss and failed (`no`). Now the live BB path
(`BB_PL_CALL` → `pl_bb_lookup` → `bb_graph_of_pred`) resolves the difference-list call.
→ rung30_dcg_basic_terminals, rung30_dcg_nonterminals PASS (were FAIL).

### `f43aff1d` — `write/1` of compound terms bound via a variable (`src/lower/bb_exec.c`)
Two coordinated gaps in the live `--run` BB path:
1. `BB_PL_VAR` value resolution converted only INT/FLOAT/ATOM to a DESCR; a bound
   `TERM_COMPOUND` fell through to `NULVCL`. Added an arm emitting
   `(DESCR_t){.v=DT_DATA,.ptr=t}` (mirrors `BB_PL_STRUCT`).
2. `BB_BUILTIN` write/writeln rendered only DT_I/DT_R/DT_S. Added a `DT_DATA` arm
   that renders the compound/list via `pl_write` (already list-aware in
   `prolog_builtin.c`; declared `extern` locally in the handler).
→ `foo(X):-X=[a]. main:-foo(R),write(R)` now prints `[a]` (was empty).
→ rung30_dcg_phrase3 PASS (phrase/3 difference-list `Rest`).

## ⛔ NEXT STEP — the principled fix attempted, working but with ONE residual segfault

**Diagnosis (solid):** `BB_PL_CALL` fresh-call arg binding (`bb_exec.c` ~line 2034) uses a
**slot-copy writeback** hack: after the callee succeeds it does
`saved_env[caller_slot] = callee_env[ai]` but ONLY for args whose node is a top-level
`BB_PL_VAR`. Vars nested inside a compound arg (e.g. the `R` in `append([H|T],L,[H|R])`'s
third head arg, or any `[H|R]` passed to a recursive call) are NEVER written back.
This is the `append/3` tail bug: `append([a],[b],L)` gave `[a|_G5]` instead of `[a,b]`.

**The correct fix (attempted, REVERTED due to residual segfault — do this properly next):**
Replace the whole bind+writeback scheme with WAM-style **shared-variable unification**:
at fresh-call time, for every arg build the caller-arg TERM with `pl_node_to_term(zc->args[ai])`
WHILE `g_pl_env` still points at the CALLER env (so `BB_PL_VAR` resolves to / materialises the
caller's actual var cell), then `unify(callee_param_var, caller_term, &g_pl_trail)`. Bindings
the callee makes — including to vars nested in compounds — then propagate back through the
shared trail automatically. Delete BOTH slot-copy writeback loops (fresh path ~2074 and resume
path ~2092); they become dead once vars are shared.

**Result of the attempt:** append/3 FIXED at all depths (`[a,b]`, `[a,b,c,x]`); `reverse/2`
FIXED (`[d,c,b,a]`, and it uses nested append); rung30_dcg_phrase3 still PASS. BUT a residual
**segfault** in the recursion+arith shape. Minimal repros:
```prolog
% SEGFAULTS at depth>=2, empty (wrong, should be 1) at depth 1:
len([], 0).
len([X|T], N) :- len(T, N1), N is N1 + 1.
:- initialization(main). main :- len([a,b], N), write(N), nl.
```
Confirmed NOT the cause (all work under the attempt): head/tail decompose (`hd`/`tl`),
recursion-on-tail without arith (`last/2` → `c`), recursion + plain `N=N1` unify
(`cnt([a,b],N)` → `0`), `bar(N), M is N+1` → `1`. The segfault needs BOTH recursion AND `is`
reading the recursively-bound output var. Likely `g_pl_env` points at a freed/stale callee env
during `pl_arith_eval`'s `g_pl_env[slot]` read at depth ≥2 (the recursion snapshot/restore
+ shared-var trail interaction). Honest gate caught it as a regression: 124 → 120. REVERTED to
keep the tree green per RULES.md ("no broken commits").

**Recommendation:** redo the unify-binding change, then trace the `is`-after-recursion path with
`g_pl_env` logging at depth 2. Suspect the fix is to evaluate/snapshot arith operands against the
correct activation env, or to not free/clobber the caller env while a shared var is still live.
This single fix should unlock a large rung cluster: rung06 (lists), and the deterministic-output
half of many others.

## UPDATE (same session, second pass) — unify-binding + unify-`is` works for lists BUT couples with the backtrack snapshot

Re-applied the unify-binding (shared-var) approach AND fixed the real co-bug: the `is` handler
(`bb_exec.c` BB_BUILTIN `is` arm) was binding its result with a **raw `g_pl_env[slot] = vt`
overwrite**, which SEVERS the shared-var link a unify-bound caller var relies on (that's why
`len/2` went empty under unify-binding — the recursively-computed `N` never reached the caller).
Fix = `is` must `unify(pl_node_to_term(nd->α), vt, &g_pl_trail)` so the result propagates through
the shared trail. With BOTH changes:
- **rung06 lists FULLY PASSES**: `[a,b,c,d]` / `4` / `[d,c,b,a]` (append/3 tail + reverse/2 nested
  append + length/2 recursion+is all correct).
- `len([a,b],N)` → `2`, `append([a],[b],L)` → `[a,b]` — all the list class fixed.

**But it is NOT a clean win — exact tradeoff measured by PASS-set diff (suite + honest):**
- GATE-3 rung suite: **GAINED rung06, LOST rung05** → net 19 (no change).
- Honest gate: **124 → 122** (rung10_programs_puzzle_14 + _16 newly SIGSEGV; baseline already
  crashes puzzle_12/13/15/18 — deep constraint-search puzzles, pre-fragile).
- rung05 (`member(X,[a,b,c]),write(X),nl,fail;true`) over-generates: `a b <blanks>` instead of
  `a b c`.

**ROOT INSIGHT (the real design issue to solve next):** shared-var unification binding and the
**snapshot/restore backtracking machinery are coupled**. `BB_CHOICE`/`BB_PL_CALL` resume relies on
`bb_snapshot_state`/`bb_restore_state` (per-node state) + trail marks to rewind between solutions
(this is what PJ-AGW-3b carefully fixed for rung05/member). When caller and callee vars are ALIASED
through the trail (unify-binding), restoring per-node state no longer models the full binding state:
the shared var bindings made across the activation boundary are not captured by the per-node
snapshot, so a resumed backtrack sees stale/over-bound vars → rung05 blanks, and partial/aborted
deep graphs (rung10 puzzles) deref bad state → segfault. The slot-copy writeback (current committed
code) AVOIDS this coupling precisely because it does NOT alias — it copies values at success time,
keeping each activation's vars independent, which is why rung05 + the puzzles survive but append's
nested-compound output var is missed.

**Proper fix direction (for next session — this is the meaty one):** make backtrack resume
trail-complete under shared vars. On each `BB_CHOICE`/`BB_PL_CALL` retry, `trail_unwind` to the
call's `mark` BEFORE re-running (so shared-var bindings from the prior solution are undone via the
trail, not just the per-node snapshot), and ensure `bb_snapshot_state` either (a) also snapshots the
trail top so restore is trail-complete, or (b) is replaced for the binding-state dimension by pure
trail discipline (snapshot only the graph CURSOR/control state, let the trail own ALL var bindings).
Option (b) is the principled WAM model: control state in the snapshot, binding state in the trail,
never both. Once resume is trail-complete, re-apply unify-binding + unify-`is` and rung05 + rung06 +
the puzzles should all hold. Verify with: rung05 = `a b c`, rung06 = `[a,b,c,d]/4/[d,c,b,a]`,
honest >= 124, no new rung10 SIGSEGV, ASAN clean on member + rung05 + fib(6).

The unify-`is` fix (unify instead of raw slot overwrite) is correct INDEPENDENT of binding strategy
and should probably land on its own once the trail-complete resume is in — but DO NOT land it alone
on the current slot-copy code without checking it doesn't regress (slot-copy + unify-is may interact).

## Other gates / corpus notes
- rung30_dcg_generate still empty: blocked by `findall/3` being ABSENT from the live BB path
  (only in stubbed `pl_runtime.c`). Distinct meta-call feature (cross-backtrack solution
  collection). rung11_findall_* all fail for the same reason.
- rung30_dcg_pushback_rest: `[NO-AST] SM_BB_SWITCH PL entry main/0/0: predicate not in bb_table`
  — separate lowering gap (pushback `,` rest), not the phrase rewrite.
- `--dump-ast` segfaults on Prolog DCG files (the run path is fine; only the AST-dump path
  crashes). Low priority but worth a look — it blocked easy AST inspection this session.
