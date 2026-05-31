# HANDOFF-2026-05-31-OPUS48-PROLOG-BB-PLG-2-ARITH-AND-PLG-3.md

**Session:** Claude Opus 4.8, 2026-05-31 (continues HANDOFF-...-PLG-0-AND-PLG-1).
**Goal:** GOAL-PROLOG-BB → PLG ladder.
**Result:** PLG-2-arith ✅ + PLG-3 ~substantially done (facts/first-solution/head-unify/multi-clause).
**Gates:** `prove_lower2.sh` **37/37**; GATE-1 smoke **3/5** (write_atom, unify, arith); FACT grep 0.

---

## What landed (all FACT-RULE clean — Prolog-only arms/IR kinds, no peer arm touched)

### PLG-2-arith — `is/2` and arithmetic comparisons (GATE-1 `arith` now PASS)

Three diagnosed bugs, all fixed:

1. **`g_compare` emitted the wrong node.** It built `IR_ARITH` with `ival = BinopKind`, but
   `resolve_arith_eval` (the `IR_ARITH` exec) reads `bb->sval` as the op NAME, not `ival`. Rewritten to
   emit `IR_BUILTIN(sval=op_str)` with LHS→`bb->α`, RHS→`bb->β`, matching the already-correct `IR_BUILTIN`
   comparison arm at `bb_exec.c:~3552` (which reads both sides via `resolve_arith_eval`).

2. **The Prolog parser emits arith as `TT_FNC`, not `TT_ADD`.** `2 + 3` from the live parser path
   (`lower_clause_from_tree`) is `TT_FNC("+", [2,3])`. (The `TT_ADD`/`TT_SUB`/… kinds only come from the
   OTHER frontend path, `lower_clause`, which takes a `PlClause`.) `lower_value` has no arith-`TT_FNC` arm,
   so the RHS hit `lower_unhandled` (`role=0 kind=45`). Fixed with **`g_arith_expr`** (new, in `lower.c`):
   for `TT_FNC` it emits `IR_ARITH(sval=op, ival=arity, α=left, β=right)` recursively (which
   `resolve_arith_eval` traverses: IR_ARITH recursion, IR_LIT_I/F constants, IR_LOGICVAR slot lookup,
   default→bb_exec_node); for `TT_ADD`/`TT_ILIT`/`TT_VAR`/etc. it falls through to `lower2(VALUE)` which
   already has `v_binop`/`emit_leaf`. Used by BOTH `g_compare` and `g_is`.

3. **`is/2` had no arm.** Added **`g_is`** (new): `IR_BUILTIN(sval="is")`, LHS via `g_term`→`bb->α`
   (read by `resolve_node_to_term` for unify), RHS via `g_arith_expr`→`bb->β` (read by
   `resolve_arith_eval`). Matches the existing `is` exec arm at `bb_exec.c:~4072` exactly.

`prove_lower2.c`: `X < 5` re-described to IR_BUILTIN; added `X is 5` (3 nodes) and `X is 2+3` (5 nodes).
35→37/37.

### PLG-3 — user-predicate calls (facts + first solution + head unification + multi-clause)

**`lower.c`:**
- **`g_goal`** (new) — user-pred call (bare atom arity-0 OR compound) → Prolog-OWNED `IR_GOAL` +
  `bb_goal_state_t` sidecar (callee/arity/arg-term-trees on `bb->ival` — PEERS rule, no new BB_t fields).
  β=self so the conjunction backtrack re-enters. Wired into BOTH the `TT_QLIT` arm (bare atom `foo`, which
  the parser emits as `TT_QLIT("foo")` — this is what `main :- greet.` needs) AND the `TT_FNC` arm
  (`foo(a,b)`). The `IR_GOAL` exec arm (`bb_exec.c:3317`) already existed compiled-but-unreachable; g_goal
  is the producer that connects it.
- **`g_head_unify`** (new) + **rewritten `lower2_clause_body_entry`** — head matching. The IR_GOAL caller
  binds callee env slot `i` to the caller's `i`-th arg (`term_new_var(i)`), so each head-arg position `i`
  must unify with `LOGICVAR(i)`. For a head VAR at slot i this is a trivial self-unify (frontend assigns
  head var position i → slot i); for an atom/number it binds. The entry now emits, in one `IR_GCONJ`:
  head-unify(0..arity-1) then body goals, with the exact fail-chain threading copied from `wire_seq`.

**`lower_program.c`:**
- **`lower_pl_choice_graph`** (new) — multi-clause predicate (`TT_CHOICE`) → `IR_CHOICE` graph +
  `bb_choice_state_t` listing each clause's body graph (`zc->bodies`/`nbodies`, `idx_ok=0`).
- **`lower_pl_register_all_preds`** (new) — after lowering `main/0`, iterates the whole
  `resolve_pred_table` (buckets 0..STAGE2_PL_PRED_TABLE_SIZE-1) and lowers+registers every predicate via
  `resolve_bb_register`, so `IR_GOAL`'s `resolve_bb_lookup` finds callee graphs.
  Single-clause → `lower_pl_clause_graph`; multi-clause → `lower_pl_choice_graph`.
  Added `#include "../runtime/interp/resolve_runtime.h"`.

#### ⚠️ THE GOTCHA THAT COST AN HOUR (write this on your hand)
`bb_exec.c`'s IR_GOAL does `resolve_bb_lookup(key, carity)` where **`key` is the FULL `"name/arity"`
string** (`snprintf(key,...,"%s/%d",callee,carity)`), used as the NAME argument — NOT the bare name. So
`resolve_bb_register` MUST be called with the full key string as its `name` arg. Registering under the
bare name (`"fact"`) makes lookup silently return NULL even though the table has the entry and the count is
right (you'll see `pe=(nil)` with `count=2, t0name=fact`). Fixed; documented in the code comment.

---

## Verified working (mode-2 `--interp`)
- `hello.pl` → `Hello, World!` (PLG-1)
- `greet :- X=world, write(X), nl.  main :- greet.` → `world` (PLG-2 + bare-atom call)
- `X is 2+3, write(X)` → `5` (PLG-2-arith)
- `fact(a). fact(b). fact(c).  main :- fact(X), write(X), nl.` → `a` (PLG-3 first solution)
- `id(X,X).  main :- id(5,R), write(R).` → `5` (output binding through head unification of a var)
- `fact(a).  main :- fact(a), write(yes).` → `yes` (head atom matching)

## KNOWN GAPS (next session = PLG-4 then PLG-6)
1. **Full enumeration.** `fact(X),write(X),nl,fail` (or `; true`, or a second `main` clause) prints only
   `a`, not `a/b/c`. The IR_GOAL β-retry → IR_CHOICE next-clause path isn't producing further solutions.
2. **Rule-body computed-result binding.** `dbl(X,Y):-Y is X*2.  main:-dbl(5,R),write(R).` prints empty.
   A RULE (not fact) whose body computes a value that must thread back to the caller's unbound var doesn't
   propagate. Facts + simple var-passthrough work; computed-through-rule-body does not.

Both gaps live in the **same place**: the `IR_GOAL` retry path (`bb_exec.c:~3450`) uses
`bb_snapshot_state` / `bb_restore_state` / `bb_body_has_live_choice` — exactly the per-node snapshot
apparatus PLG is chartered to DELETE (PLG-7) and replace with a per-activation frame (PLG-6). The honest
read: re-growing first-solution wiring onto the OLD snapshot retry path got us facts + first solution, but
enumeration and rule-body binding need the per-activation frame the ladder is built around. PLG-4 (enumerate)
and PLG-6 (recursion) should implement that frame rather than lean further on the snapshot path.

Suggested next move: study how the archived `prolog_emit.c` user-call carries only `(cursor `_cs`, trail
mark)` across the fail edge (per the PLG directive's four canonical sources), and make the IR_GOAL retry +
IR_CHOICE dispatch carry exactly that — a per-activation cursor int + trail mark — instead of snapshotting
the shared graph. The `bb_choice_state_t` already has the cursor idea (`cur`/`bb->state`); the missing link
is making the caller's env survive as a per-activation frame so re-entry re-binds cleanly.

## Files touched (SCRIP only; nothing in .github except this handoff + GOAL doc)
- `src/lower/lower.c` — g_arith_expr, g_compare (rewrite), g_is, g_goal, g_head_unify,
  lower2_clause_body_entry (rewrite), TT_QLIT+TT_FNC user-call arms.
- `src/lower/lower_program.c` — resolve_runtime.h include, lower_pl_choice_graph,
  lower_pl_register_all_preds + its call after main/0.
- `src/lower/prove_lower2.c` — X<5 re-described, +X is 5, +X is 2+3.
- `.github/GOAL-PROLOG-BB.md` — PLG-3 entry + banner live-state.

## Session-setup for next time (unchanged)
```
cd /home/claude/SCRIP && bash scripts/install_system_packages.sh
make -j4 scrip && make libscrip_rt
bash scripts/prove_lower2.sh           # 37/37
bash scripts/test_smoke_prolog.sh      # 3/5 (write_atom,unify,arith)
./scrip --interp corpus/programs/prolog/hello.pl   # Hello, World!
```
