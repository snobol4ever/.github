# HANDOFF 2026-05-28 — Opus 4.7 — PROLOG-BB: SWI-2-fold + SWI-2b — GATE-SWI 0→53/57

**Repos:** SCRIP `43933846` · corpus `c4e0229` · .github (this commit)

Mode-4 testing intentionally skipped this session per Lon's directive (focus on
mode-2 + mode-3; full mode-4 pass deferred to project endgame — mode-3 exists
precisely to let correctness sprints skip mode-4 emit cycles).

---

## What landed

### SCRIP `0e53e265` (final hash `43933846` post-rebase)

#### SWI-2-fold — `src/frontend/prolog/prolog_lower.c`

Callable directives like `:- begin_tests(memberchk, []).` used to emit
`SM_BB_PL_INVOKE("begin_tests/2", 2)` — but that opcode **passes NO args** to
the callee, leaving head vars `Suite`/`Opts` unbound at runtime. Manual trace
confirmed: predicate body fires (printed "BEGIN_TESTS") but with `Suite` empty.

Fix is upstream at the frontend: in `prolog_lower.c`'s directive loop, when a
whitelisted callable-with-args directive is seen:

1. Generate fresh helper name `pj_dir_N`
2. Build synthetic clause `pj_dir_N :- <original_goal>`
3. Register in `keys`/`choices` as `pj_dir_N/0`
4. Rewrite the directive's `goal_tr` to `initialization(pj_dir_N)`

The existing `initialization/1` arm in `lower.c:2108` then dispatches the
0-ary helper, whose body's `BB_PL_CALL` to the original goal correctly
materializes args. Whitelist matches `lower.c:2138` (begin_tests, end_tests,
dynamic, use_module, module, ensure_loaded, discontiguous, meta_predicate,
nb_setval). Excludes `initialization` (handled directly) and 0-ary calls
(which work via SM_BB_PL_INVOKE since they need no args).

#### SWI-runner-fix — `scripts/test_prolog_swi_suite.sh`

WRAP previously relied on `PJ-AGW-MAIN0` auto-main fallback. But plunit.pl
now has its own `:- initialization(pj_suites_init).` (SWI-2b), which sets
`g_pl_initialization_seen=1` and suppresses the fallback. One-line fix:
explicit `:- initialization(main).` in the WRAP file.

### corpus `c4e0229` — `programs/prolog/plunit.pl`

#### SWI-2b — nb_setval-based suite registry

Suite registry used `assertz(pj_suite(Suite, Opts))` — but scrip's runtime
assertz (PL-RT-ASSERTZ) is a separate open task that doesn't work yet.
Replaced with `nb_setval(pj_suites, [Suite-Opts|Old])`:

- `pj_suites_init :- nb_setval(pj_suites, [])`
- `:- initialization(pj_suites_init).` seeds the list before any begin_tests fires
- `pj_suites_add(Suite, Opts) :- nb_getval(pj_suites, Old), nb_setval(pj_suites, [Suite-Opts|Old])`
- `begin_tests(Suite) :- pj_suites_add(Suite, []).`
- `begin_tests(Suite, Opts) :- pj_suites_add(Suite, Opts).`
- `end_tests(_).`
- `run_tests :- pj_init, nb_getval(pj_suites, Sx), pj_reverse(Sx, Ss), pj_run_pairs(Ss), pj_summary.`
- `pj_run_pairs([Suite-_Opts|T]) :- ...`

The `pj_test/4` table continues to populate via the existing
`prolog_lower.c` plunit_suite fold (line 484+) which synthesizes
`:- assertz(pj_test(Suite,Name,Opts,Goal)).` directives at lower time — these
flow through the existing static-assertz fold (line 561) and work correctly.

---

## Gates at this HEAD

| Gate | Mode-2 | Mode-3 | Mode-4 |
|---|---|---|---|
| GATE-1 smoke | 5/5 ✅ | 5/5 ✅ | (skipped per Lon directive) |
| GATE-2 crosscheck | 132/0 ✅ | (part of G2) | n/a |
| GATE-3 rung suite | **104/107** ✅ | **104/107** ✅ | (skipped) |
| **GATE-SWI plunit** | **53/57 (92%)** ✅ | **53/57 (92%)** ✅ | n/a |
| FACT grep | 0 ✅ | — | — |

GATE-SWI moved 0/57 → 53/57 in both mode-2 and mode-3 — first non-zero result
since SWI suite was introduced.

---

## Remaining 4/57 SWI failures

Not investigated this session (tool budget). Worth a triage session:

```
bash scripts/test_prolog_swi_suite.sh 2>&1 | grep FAIL | head -10
```

Likely classes: missing builtins (clause/2, variant/2, etc per existing SWI-7
plan), conditional compilation `:- if/else/endif` (SWI-4), bare `Var==Val`
options form (SWI-3).

---

## Next session options

1. **SWI cleanup** — chase remaining 4/57 SWI failures. Probably 1–2 are
   `:- if/else/endif` (SWI-4), 1–2 are missing builtins. Could push GATE-SWI
   to 57/57.
2. **PL-RT-ASSERTZ** — runtime assertz/asserta. Materialise fresh clause body
   BB graph at runtime and append to predicate's BB_CHOICE `zc->bodies[]`.
   Blocks rung15_then_reassert and removes the workaround that motivated SWI-2b.
3. **WAM-CP-13** — longjmp-free catch + mode-4 catch emit. Reuses WAM-CP-9 r12
   + saved-state-slot pattern.
4. **WAM-CP-6 LCO** — principled SEGFAULT-CLUSTER fix; needs `bb_exec_once`
   non-recursive refactor.

---

## Discovery: SM_BB_PL_INVOKE args limitation

Worth documenting separately: `SM_BB_PL_INVOKE` resolves predicates by
name+arity in `pl_bb_table` and dispatches via `bb_broker(pnode, bb_once,
NULL, NULL)` — **arg vector is always NULL**. For directives, args are
literals known at lower time, but they have no path to the callee env.

SWI-2-fold sidesteps this by wrapping the directive in a helper predicate
so the args travel via `BB_PL_CALL` (which does materialize them). A future
proper fix would either: (a) extend `SM_BB_PL_INVOKE` to carry a small
arg vector encoded in the SM stream; or (b) keep the wrapper-helper approach
as the canonical pattern and retire any other use of multi-arg directives.

Approach (b) is simpler and the wrapper is essentially free, so I'd
recommend keeping it.

---

## Commit identity
```bash
git config user.name "LCherryholmes"
git config user.email "lcherryh@yahoo.com"
```
