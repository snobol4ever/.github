# HANDOFF 2026-05-28 — Opus 4.7 — PROLOG-BB: SWI-2c plunit fold revival + call/1-atom runtime bug discovery

**Repos:** one4all `a88f1e68` · corpus `c4e0229` (untouched) · .github (this commit)

Continuation of SWI-2-fold. Triaging the remaining 4/57 SWI failures
(`catch`, `variant`, `float_compare`, `max_integer_size`) led to a layered
discovery: the plunit test-fold has been silently dead since PST-PL-6f
landed, and a separate `call/1`-on-bound-atom runtime bug in mode-2 masks
the impact.

---

## What landed

### one4all `a88f1e68` — SWI-2c plunit fold revival

`src/frontend/prolog/prolog_lower.c`: the plunit fold synthesizes
`pj_test(Suite, Name, Opts, Goal)` facts from `test/2` clauses inside
`begin_tests`/`end_tests` windows. Two stale checks made the fold dead:

1. **First-pass suite tagging** at line ~457 required `cl->head != NULL`.
   Post-PST-PL-6f, non-DCG rule clauses store the head in `cl->tr->c[0]`
   (a `tree_t`) and leave `cl->head` NULL. So no SWI `test/2` clause was
   ever tagged with its surrounding suite.

2. **Second-pass test-fold** at line ~497 read `cl->head` / `cl->body`
   unconditionally. Even if a clause had been tagged, `term_deref(NULL)`
   would have crashed.

Fix:
- First pass: classify each clause as directive vs rule/fact via the same
  `is_rule || is_dcg` check the second pass uses. Tag any rule/fact inside
  a begin_tests window.
- Second pass: when `cl->tr` is set, synthesize `pj_test/4` from
  `cl->tr->c[0]` (head) and `cl->tr->c[1]` (body), using a new `tr_dup`
  helper to deep-clone shared subtrees (avoids heap corruption from
  `lower_clause_from_tree`'s slot reassignment running twice over the
  same TT_VAR nodes, and from `expr_free` double-walks at `code_free`
  time).
- Legacy Term* path retained for DCG-style `test/2` (`cl->head` set,
  `cl->tr` NULL).

The `tr_dup` step matters. First attempt at the rebuild shared nodes
between the synthesized `pj_test/4` clause and the original `test/2`
clause (which continues through the fold to register in `test/2`'s choice
table). Result was an `unaligned fastbin chunk in malloc_consolidate`
abort. `tr_dup` mirrors `ast_gc_clone` but uses `ast_node_new`/
`expr_add_child` so every node carries the `size_t` capacity prefix
required by `ast_push` and by `expr_free` in `ast_clone.c`.

Verification: `findall(t(N,O,G), pj_test(S,N,O,G), L)` directly returns
the populated list for the synthesized clauses; pre-fix it always
returned `[]`.

---

## Gates at this HEAD

| Gate | Mode-2 | Mode-3 | Mode-4 |
|---|---|---|---|
| GATE-1 smoke | (not run) | (not run) | (skipped per directive) |
| GATE-2 crosscheck | **132/0** ✅ | (part of G2) | n/a |
| GATE-3 rung suite | **104/107** ✅ | (not separately run) | (not run) |
| GATE-SWI plunit | **53/57 (92%)** ✅ | (not separately run) | n/a |
| FACT grep | (not run — frontend-only change) | — | — |

GATE-SWI is byte-identical to `43933846`. The fix is real but the gate
number does not move because of a separate runtime bug — see below.

---

## Discovery: call/1 on a bound atom fails in mode-2

The fold now correctly populates `pj_test/4`. Direct queries confirm.
But `pj_run_tests` still reports 0 passed / 0 failed / 0 skipped per
suite, identical to the pre-fix behavior.

Root cause is downstream in mode-2 (`--interp`) runtime, not in the
fold. Minimal reproduction:

```prolog
main :- ( call(true) -> write(ok) ; write(fail) ), nl.
:- initialization(main).
```

Output: `fail`. Literal `call(true)` returns failure.

`is_pl_user_call("true")` correctly returns 0 (builtin). Walking the
code: `call(true)` in `interp_exec_pl_builtin` at line 1042 hits the
`call/1` arm, dereferences the arg to `TERM_ATOM:true`, calls
`pl_invoke_var_goal(g_term, env)`. That function synthesizes a fresh
`tree_t` via `pl_term_to_synth_expr` — for an atom it builds
`TT_FNC(sval="true", n=0)`. Then `interp_exec_pl_builtin(synth, tenv)`
hits the `true` arm at line 894 (`if (strcmp(fn,"true")==0&&arity==0)
return 1;`) and should return 1.

Empirically it does not. Something between the synth-expr build and
the builtin dispatch is returning 0. Not investigated to root in this
session — out of tool budget.

This bug pre-dates the fold fix. Pre-fix, no test/2 body was ever
stored, so `pj_run_one`'s `catch(Goal, _, ...)` path never reached
`call/1` on a bound atom — the bug was completely masked. Post-fix,
the fold works correctly and exposes the runtime gap.

The 53/57 PASSes remain false-positives via `pj_suite_verdict`'s
`SF =:= 0 -> PASS` clause. The 4 expected-FAIL suites still emit
PASS via the same mechanism, which is why they MISS the FAIL in
their `.ref`.

---

## Next session options

1. **call/1-on-bound-atom in mode-2** (highest leverage). Once fixed,
   real test bodies start running. Some currently-PASS suites will
   reveal real failures (and need new builtins or .ref adjustments).
   Some currently-FAIL suites may flip if the underlying test body
   genuinely succeeds.

   Diagnosis hooks:
   - `pl_invoke_var_goal` at `src/runtime/interp/pl_runtime.c:845`
   - `pl_term_to_synth_expr` at line 781 — TERM_ATOM branch at 805
   - `interp_exec_pl_builtin` `true` arm at line 894
   - Single-step from `call(true)` to determine which return 0 fires
     on the path back up.

2. **SWI-5 (EMPTY verdict)** — independent of #1. Change
   `pj_suite_verdict` in `plunit.pl` to emit `EMPTY` (or `FAIL`) when
   zero tests ran. This makes the gate number honest but doesn't add
   any real test coverage. Update `.ref` files for genuinely-empty
   suites accordingly. May invert the gate (53 PASSes flip to EMPTY).

3. **PL-RT-ASSERTZ** — runtime assertz so plunit.pl can ditch the
   nb_setval workaround.

4. **WAM-CP-13** — longjmp-free catch + mode-4 catch emit.

5. **WAM-CP-6 LCO** — principled SEGFAULT-CLUSTER fix.

Recommendation: #1 first. Even if it only moves the gate by a small
amount, the runtime bug is on the critical path for any further
SWI-suite progress — without `call/1` working on bound atoms, the
plunit shim can never execute test bodies, and the gate stays at
"53/57 by accident" forever.

---

## Files touched this session

- `one4all/src/frontend/prolog/prolog_lower.c` — fold revival (+146/-33)

## Commit identity

```bash
git config user.name "LCherryholmes"
git config user.email "lcherryh@yahoo.com"
```
