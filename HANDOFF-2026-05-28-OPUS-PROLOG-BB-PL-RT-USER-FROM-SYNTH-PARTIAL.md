# HANDOFF-2026-05-28-OPUS-PROLOG-BB-PL-RT-USER-FROM-SYNTH-PARTIAL

**Author:** Claude Opus 4.7
**Date:** 2026-05-28
**Predecessor HEAD:** `3de01576` (SWI-2e call/N for N>1)
**This HEAD:** (to be assigned at commit time)

---

## Summary

**Partial 🟡.** Replaced the `[NO-AST] interp_eval stub` at
`pl_runtime.c:931` with real BB-graph dispatch via `pl_bb_lookup` +
`bb_exec_once`, mirroring the post-intercept logic in BB_PL_CALL's
handler. **Works** for user predicates whose call args are all inputs
(literals or already-bound terms). **Fails** for user predicates with
output-mode vars — the body's local-var read doesn't connect to the
caller's variable cell through the round-trip:

```
caller BB_PL_VAR -> pl_node_to_term -> Term* (alias of caller_env[k])
                 -> pl_term_to_synth_expr -> tenv[slot] (still the same Term*)
                 -> pl_unified_term_from_expr(goal->c[i], env=tenv) -> Term*
                 -> unify with term_new_var(ai) into callee_env[ai]
                 -> bb_exec_once(body) -> body's BB_PL_VAR reads g_pl_env[?]
```

The final hop — what var slot the body actually reads when it sees
its local `C` (for `bind3(A,B,C) :- C = wow.`) — is the gap I didn't
close. The body's BB_PL_VAR for `C` may read a slot ≠ 2 (the input
arg slot), in which case my fresh-var allocation into `callee_env[2]`
never connects.

`rung33_bridge_callN`: **2/5 unchanged from `3de01576`** (no progress,
no regression).

---

## What works

- The 2/5 from SWI-2e (`01_call1_atom` + `03_call2_extra_arg`) still PASS.
- 3-ary user pred with all-atom args via call/3 works end-to-end —
  verified `greet3(A,B,C) :- write(A),write(B),write(C),nl.` via
  `call(G, hi, ho, hum)` prints `hihohum`. So the dispatch path is
  correct for input-only predicates.

## What doesn't work

- `rung33_bridge_callN` 02 — `call(G)` with G = `(X=5)`. The reconstructed
  goal `=(X, 5)` is *not* a user call — it's the `=` builtin. It might be
  hitting a different gap (the TT_UNIFY arm or how `X` is shared with the
  caller's binding).
- 04 — `call(G, 3, 4, R)` with `add(X,Y,Z) :- Z is X+Y.` Reconstructed as
  `add(3, 4, R)`. With my fix `pl_bb_lookup("add/3", 3)` now finds the
  BB graph (vs. NULL pre-fix), but `bb_exec_once` returns DT_FAIL because
  the body's `is/2` doesn't see X/Y bound or can't unify back to R.
- 05 — `call(G, R)` with G = `succ(3)`. Same shape as 04.

The simplest reproducer that demonstrates the gap (no arithmetic,
just unify-out):
```prolog
bind3(A, B, C) :- C = wow.
main :- G = bind3, call(G, x, y, R), write(R), nl.
```
Returns nothing; `bb_exec_once` produces DT_FAIL.

---

## Key fixes that landed

1. **`pl_bb_lookup` key format.** The lookup must use `"name/arity"` as
   the *name* argument, not just `"name"` — `pl_bb_register` stores
   `e->key = "name/arity"` and `pl_bb_lookup` does a strcmp on the
   stored name. BB_PL_CALL in `bb_exec.c:3267` already builds the
   slash-key correctly; my user-call branch mirrors that.

2. **No AST walking.** The old stub at line 895 used
   `pl_pred_table_lookup(&g_stage2.pl_pred_table, ukey)` which retrieved
   the *clause AST*, then was supposed to interpret it directly —
   forbidden by RULES.md. The new code goes through the BB graph table
   instead, fully RULES-compliant.

3. **Env discipline.** `saved_env = g_pl_env`, swap to fresh
   `callee_env`, `bb_reset` + `bb_exec_once`, restore. Same idiom as
   BB_PL_CALL.

---

## Diagnostics for the next session

The investigation should focus on **how the body's local var slots map
to `g_pl_env` indices**. The lowerer assigns var slots via some
`PlScope` mechanism in `lower_pl.c`. Specifically:

- For `bind3(A,B,C) :- C = wow.` — is `C` assigned slot 2, or some
  other slot (e.g. body-local 0)?
- For the *direct* call `bind3(x, y, R)` (which works), how does the
  caller's BB_PL_CALL bind args into the callee env? Compare with what
  my synthesized-tree path does.

Likely next step is to add temporary `fprintf(stderr, ...)` instrumentation
inside `bb_exec_node` for `BB_PL_VAR` to log the slot being read, then
compare a direct-call trace with a call/N-via-synth trace side-by-side.

If the slot indices do match (both reach slot 2 for C), the issue is
in the **Term chain itself**: the unify chain between caller_R and
callee_var_2 may not survive the deref discipline used by the body's
unification.

---

## Alternative path worth considering

Rather than going through `pl_invoke_var_goal` → `pl_term_to_synth_expr`
→ `interp_exec_pl_builtin` (which converts Term*→tree_t→Term* and loses
fidelity at each hop), have `pl_call_term_n` **directly** call
`pl_bb_lookup` + `bb_exec_once` with a fresh callee_env built straight
from the Term* args (no synthesized goal-tree round trip). That mirrors
BB_PL_CALL exactly and avoids the synthesis layer entirely.

This is probably the right design and would close the partial cleanly,
but it requires moving the user-call BB dispatch out of
`interp_exec_pl_builtin` and into a new public helper that `pl_call_term_n`
can call directly when the deref'd goal Term is a TERM_COMPOUND or
TERM_ATOM whose functor matches a registered BB predicate.

---

## Changes

### `src/runtime/interp/pl_runtime.c` (+34, -8)

Replaced the 13-line `[NO-AST] interp_eval stub` block at the
user-call branch of `interp_exec_pl_builtin`'s TT_FNC case with a
~22-line BB-graph dispatch using `pl_bb_lookup("name/arity", arity)`,
`bb_reset`, `bb_exec_once`, env swap/restore, and trail rewind on
FAIL. ~25 lines of comment explaining the partial state and known
gaps.

No other files touched.

---

## Gates

| Gate | Value | Δ from `3de01576` |
|---|---|---|
| Smoke Prolog | 5/5 | — |
| G2 crosscheck | 132/0 (5 ORACLE_MISS) | — |
| G3 mode-2 (`--interp`) rung_suite | 104/107 | — |
| GATE-SWI plunit | 53/57 (92%) | — |
| BB-honest | 128/0 | — |
| FACT | 0 violations | — |
| rung33_bridge_callN | 2/5 | — (no regression, no progress) |

FACT clean. No emitter or template files touched. Mode-3/4 byte
output unchanged.

---

## Files touched

```
M  src/runtime/interp/pl_runtime.c  +34 -8  user-call branch BB-graph dispatch
A  HANDOFF-2026-05-28-OPUS-PROLOG-BB-PL-RT-USER-FROM-SYNTH-PARTIAL.md
```

---

## NEXT recommended

(a) **PL-RT-USER-FROM-SYNTH-2** — close the var-binding gap. Two approaches:
  - **Approach A (instrument & fix):** Add temporary BB_PL_VAR trace under
    this dispatch path to identify the slot mismatch, then adjust the
    env layout.
  - **Approach B (redesign):** Move BB dispatch out of
    `interp_exec_pl_builtin` and into a direct path in `pl_call_term_n`
    that bypasses `pl_term_to_synth_expr` entirely for user predicates.
    This mirrors BB_PL_CALL exactly. **Recommended over A.**

(b) SWI-5 EMPTY verdict — independent track.

(c) PL-RT-ASSERTZ.

(d) WAM-CP-13.

(e) WAM-CP-6 LCO.
