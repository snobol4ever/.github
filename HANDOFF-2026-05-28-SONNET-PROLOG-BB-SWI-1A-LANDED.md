# HANDOFF 2026-05-28 — Sonnet 4.6 — PROLOG-BB: SWI-PLUNIT SWI-1a landed, SWI-2 blocked

**Repos:** SCRIP `86abe166` · .github `19a4ea04` · corpus untouched (plunit.pl reverted).

---

## What landed this session

### `86abe166` — SWI-1a: directive whitelist in lower.c

In `lower.c` LANG_PL unrecognized-directive branch, added whitelist before the `[NO-AST]` drop:
`begin_tests/1`, `begin_tests/2`, `end_tests/1`, `dynamic/1`, `dynamic/2`, `use_module/1`,
`use_module/2`, `module/2`, `ensure_loaded/1`, `discontiguous/1`, `discontiguous/2`,
`meta_predicate/1`, `nb_setval/2`, `initialization/1`, `initialization/2`.

These now emit `SM_BB_PL_INVOKE(key, arity)` at load time instead of being silently dropped.
All gates byte-identical: G1=5/5, G2=132/0, G3 mode-2=104/107, G3 mode-3=104/107,
G4=4/4, mode-4=54/107, FACT=0.

**Confirmed working:** `begin_tests(Suite)` now fires and can call `nb_setval`. `[NO-AST]`
messages for `begin_tests`/`end_tests`/`dynamic` are gone when plunit.pl is loaded.

---

## SWI-2 status — blocked on two bugs, full diagnosis

### Bug 1: `SM_BB_PL_INVOKE` for builtins

`nb_setval/2` IS in the whitelist and emits `SM_BB_PL_INVOKE("nb_setval/2", 2)`. But
`SM_BB_PL_INVOKE` in the interpreter calls `pl_bb_entry_node(name, arity)` which looks in
`g_pl_bb_table`. `nb_setval` is a BB_BUILTIN in `bb_exec.c`, NOT a user-defined predicate
in `g_pl_bb_table`. Result: `[NO-AST] SM_BB_PL_INVOKE nb_setval/2/2: predicate not in bb_table`.

**Fix needed:** The SM_BB_PL_INVOKE interp handler must fall back to the goal evaluator
path (via `pl_invoke_var_goal` or equivalent) when the predicate is not in bb_table.
OR: initialize `pj_suites` via a user-defined predicate wrapper.

### Bug 2: `call(Goal)` from inside a predicate body

The plunit `pj_do_true` approach stores the test goal as a Term and calls it via
`catch(Goal, _, fail)`. When `Goal = test(memberchk, y==y)` is called from inside another
predicate's clause body (not from `main` directly), the `pl_invoke_var_goal` path fails
silently. Direct call `test(memberchk,y==y)` in `main` succeeds; same call as a variable
from inside `my_pred(Goal) :- call(Goal)` fails.

This is a deep runtime limitation in how `pl_invoke_var_goal` handles calling predicates
with compound-term arguments from nested environments.

### Bug 3: findall infinite loop with non-deterministic test body

`findall(N, test(N,_), Ns)` over `test(memberchk, X==y) :- memberchk(...)` gives
thousands of `memberchk` solutions instead of 1. Root cause: the `fa_safety` counter
in `bb_exec.c` findall loop (`fs->gcfg->n * 256 + 4096`) is too high for a predicate
whose clause body has many nodes. The BB_CHOICE for `test/2` after the body succeeds
does NOT advance cursor past clause 0 when resumed via `bb_exec_resume`, causing the
same body to re-fire on every findall iteration.

**Fix needed:** After `bb_exec_once(gcfg)` succeeds in findall, check
`bb_body_has_live_choice(gcfg)` and if false (deterministic body), don't call
`bb_exec_resume` — stop immediately. The existing `BB_PL_CALL` β-path has this guard
(lines 3335-3345) but findall's resume loop does not.

---

## Recommended next session approach

**Step 1 — Fix findall determinism guard (1 change, bb_exec.c):**
In the findall loop (`BB_BUILTIN findall` case, around line 3434), after
`bb_exec_once(fs->gcfg)` succeeds and before the while loop calling `bb_exec_resume`:
```c
/* Don't resume deterministic bodies — mirrors BB_PL_CALL discipline */
while (!IS_FAIL_fn(res) && fa_safety-- > 0) {
    if (nacc >= 4096) break;
    acc[nacc++] = bb_copy_term(pl_node_to_term(fs->tmpl));
    if (!bb_body_has_live_choice(fs->gcfg)) break;  /* ADD THIS LINE */
    res = bb_exec_resume(fs->gcfg);
}
```
This makes `findall(N, test(N,_), Ns)` return `[memberchk]` instead of thousands.

**Step 2 — Fix plunit.pl to use direct test/2 calls (no goal-as-term):**
Replace `pj_do_true(Suite, Name, Goal, Expr)` which uses `catch(Goal,_,fail)` with
direct pattern matching. Since we know the Goal is always `test(N,O)`, call it directly:
```prolog
pj_exec_one(Suite, N, Opts) :-
    pj_has_true(Opts, Expr), !,
    ( test(N, Expr) ->              % Direct call, not call(Goal)
        pj_inc_pass, format('  pass: ~w:~w~n',[Suite,N])
    ;   pj_inc_fail, format('  FAIL: ~w:~w  (true check failed)~n',[Suite,N]) ).
```
This avoids the `pl_invoke_var_goal` bug entirely.

**Step 3 — Fix suite registration (nb_setval at load time):**
`begin_tests(Suite)` via SM_BB_PL_INVOKE fires and runs. It calls `nb_getval(pj_suites,L)`.
`nb_getval` is a BB_BUILTIN that IS accessible during SM_BB_PL_INVOKE execution
(the runtime evaluates it through `bb_exec_once`). The problem was the fallback to
`catch(nb_getval(...),...)/fail` catching non-existent keys incorrectly.

Simpler approach: define `pj_suites_reset/0` in plunit.pl and put
`:- initialization(pj_suites_reset)` at top of plunit.pl. `initialization/1` is now
in the whitelist. `pj_suites_reset :- nb_setval(pj_suites,[])`. This fires at end of
plunit.pl load, BEFORE any test file's `begin_tests` directives fire. Then
`begin_tests` does: `nb_getval(pj_suites,L), nb_setval(pj_suites,[Suite-Opts|L])`.

**Step 4 — fix run_tests to use nb_getval(pj_suites):**
```prolog
run_tests :- pj_init,
    nb_getval(pj_suites, Ss0), reverse(Ss0, Ss),
    pj_run_suite_list(Ss), pj_summary.
```

**Target after these 4 fixes:** `test_list` PASS memberchk, mode-2 and mode-3.

---

## GATE-SWI baseline

```
bash scripts/test_prolog_swi_suite.sh          # 0/57 (0%) — unchanged
bash scripts/test_prolog_swi_suite.sh --mode run   # 0/57
```

Mode-4 for SWI suite: always SKIP (no mode-4 templates for plunit builtins).

---

## Gates at HEAD `86abe166`

| Gate | Mode-2 | Mode-3 | Mode-4 |
|---|---|---|---|
| GATE-1 smoke | 5/5 ✅ | 5/5 ✅ | 5/5 ✅ |
| GATE-2 crosscheck | 132/0 ✅ | (part of G2) | n/a |
| GATE-3 rung suite | **104/107** | **104/107** | **54/107** |
| GATE-4 mode-4 minimal | 4/4 ✅ | n/a | 4/4 ✅ |
| GATE-SWI plunit | **0/57** | **0/57** | n/a |
| FACT grep | 0 ✅ | — | — |

## Commit identity
```bash
git config user.name "LCherryholmes"
git config user.email "lcherryh@yahoo.com"
```
