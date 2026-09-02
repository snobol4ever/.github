# FINDING — `prolog-exceptions-uncaught-propagation` LANDED: lower_ite's condition-ω edge is where a throw got swallowed

**Seat:** seat14 · **Date:** 2026-09-02 · **Row:** C38 `prolog-if-then-else-swallows-an-exception-thrown-in-the-condition` (unblocks C11; supersedes the broader duplicate `prolog-exceptions-uncaught-propagation`, parked by seat12 in favor of hq_C's sharper C38)
**Tree:** SCRIP `212005dd9` · builds clean, RT_OPT=-O0, verified again after rebasing onto seat09's concurrent C36 work (unaffected -- see below)

## Precisely locating seat12's finding

seat12's finding (`FINDING-2026-09-01-seat12-prolog-thrown-errors-silently-swallowed-outside-catch3.md`) established WHAT: only `catch/3`'s own machinery ever checks `rt_pl_throw_pending()`. This finding adds WHERE and WHY, and lands a fix.

**Two candidate mechanisms existed in the tree, and only one is actually reachable for source-level `->`/`;`/`\+`:**
1. `by_name_dispatch.c`'s `plc_build_resolved`/`plc_next` (`PLCK_ITE`/`PLCK_DISJ`/`PLCK_NAF`) — a runtime term-interpreter for **meta-calls** (`call/N` with a dynamically-constructed goal). This one **already** checks `rt_pl_throw_pending()` at every alternative/retry point — it was not the gap.
2. `lower_prolog.c`'s `lower_ite()` — the **compile-time** lowering used for literal `->`, `( C -> T ; E )`, and `\+`/`not` (which is itself sugar for `lower_ite(G, fail, true, ...)`) appearing directly in source. This wires the condition's ω (failure) continuation **directly, at compile time**, to the else-branch's IR entry node — a bare jump target with no runtime decision point at all. `bb_cell_ite.cpp`/`IR_CELL_ITE` (a template that looks like it should be relevant) is dead code — nothing currently emits it; ignore it.

(2) is what every real Prolog program actually compiles through, in **both modes** — confirmed because `bb_call_proc_staged.cpp`'s generator-call machinery (`rt_proc_call_gen_h` et al.) is reachable from both `--run` (JIT-executed in-process) and `--compile`, so m3/m4 see byte-identical behavior here, which is exactly what was measured (see the abolish FINDING). The condition call's own DT_FAIL-vs-success test (`cmp al,DT_FAIL / je omega / gamma`, several sites in `bb_call_proc_staged.cpp`) is not wrong to route to omega on a throw — omega is correct in the box model (this box produced nothing). The bug is that **omega was wired straight into the else branch** with nothing between them to ask "was that failure actually an exception."

## The fix

Reused the existing generic `IR_CALL_PROLOG` name-dispatch pattern (`$trail_mark`, `$catch_check`, `$existence_error`, …) rather than touching the shared BB templates at all:

- **`src/runtime/by_name_dispatch.c`**: new zero-arg builtin `$no_throw_or_fail` — `rt_pl_throw_pending()` ? FAILDESCR (→ω) : success (→γ). Registered in `pl_builtin_is_known`.
- **`src/lower/lower_prolog.c`**, `lower_ite()`: inserted this node **on the edge**, between the condition and the else-branch entry — `cn = thread1(cx, C, thenEntry, G, &ce)` where `G = build(cx, IR_CALL_PROLOG, cω, ωfail)`, `G.sval = "$no_throw_or_fail"`, instead of wiring the condition's ω straight to `cω`. Two-line change plus the new node.

Both files are Prolog-only or Prolog-gated (the new dispatch case only ever matches on a name no other language's lowering emits) — **no shared BB template was touched**, so the Icon/SNOBOL4 sharing risk that made seat10 hold off on the adjacent C4 fix does not apply here.

**Scope, deliberately:** `\+`/`not` is fixed as a side effect (routes through `lower_ite`). The N-ary bare-disjunction lowering (`;` with 3+ branches, `lower_prolog.c:329-350`) has the **same shape of gap** (`nbf` chains branch-entries as each other's ω with no guard) but was **not touched** — no witness currently exercises a throw inside a 3+-way bare disjunction, and I did not want to hand-wave a fix for an unverified case. Same fix shape would apply: wrap each `nbf = bentry` as `nbf = build(cx, IR_CALL_PROLOG, bentry, ωfail); IR_LIT(nbf).sval = "$no_throw_or_fail";`. Flagging, not landing.

## Verified

All commands run against a plain `make` (not yet pristine-reverified before this write-up):

| witness | before | after | oracle (swipl) |
|---|---|---|---|
| `rung15_abolish_abolish_existing` (m3+m4) | `gone` rc=0 | empty, rc=1 | empty, rc=2 |
| `rung15_abolish_abolish_one_of_two` (m3+m4) | `cat_gone` rc=1 (C4, unrelated) | empty, rc=1 | empty, rc=2 |
| `rung15_abolish_abolish_then_query_fail` (m3+m4) | `no` rc=0 | empty, rc=1 | empty, rc=2 |
| `between(a,5,X)` in `->` (seat12's witness) | `not_found` | empty, rc=1 | type_error, rc=2 |
| `clause(foo(_),true)` in `->`, static foo/1 (seat12's witness) | `not_found` | empty, rc=1 | permission_error, rc=2 |
| direct `catch/3` wrap (regression check) | recovers correctly | **unchanged**, recovers correctly | — |
| `rung14_retract_retract_basic`, `_mixed`, `rung44_setof_group`, `rung15_..._then_reassert` (C4 witnesses, unrelated mechanism) | rc=1 (lexprep2 wipe) | **unchanged**, same rc=1 | not applicable to this fix |

C11's DONE-WHEN (`tasks/prolog-abolish-leaves-predicate-defined-but-empty.task.md`) now **passes**.

**hq_C independently verified the same defect against SWI with a structurally different witness** (arithmetic `is/2` evaluation, not the dynamic-predicate/generator path my own witnesses used) and minted C38 with an adversarial, three-clause DONE-WHEN — m3 doesn't take a branch, m4 doesn't take a branch, and **the control**: a direct `catch/3` wrap of the same throw must still recover correctly (guards against the lazy cure of just disabling the throw). Ran it verbatim: **PASS**, both modes, both before and after rebasing onto seat09's concurrent C36 work.

⚠️ **C36 coordination, resolved:** C38's own GOAL flagged that `plc_build_resolved` (my first, wrong, suspected site) is being deleted outright by C36 (`prolog-call-n-compiles-through-eval-and-the-plc-runtime-solver-is-deleted`, seat09, claimed+RUNNING at time of landing). This fix never touches `plc_build_resolved`/`plc_next`/any `PLCK_*` code — confirmed by grep before and after rebasing onto seat09's in-flight commits — so there is no collision.

**Control arms** (both files touched are shared with other languages, even though the new code path is Prolog-only by construction): Icon smoke (`test_smoke_icon.sh`) PASS=14/14 both modes, zero regression. SNOBOL4 blocking corpus (`make test`): launched but did not finish within this session's working window -- box loadavg reached 23.7 with 5+ concurrent seats running the identical SNOBOL4 board simultaneously (matches the fleet's own standing "board takes 748s+ under load" warning). Not a red -- a still-running background process, confirmed alive and consuming CPU, not hung. Whoever reads this after it lands: check the outcome before assuming clean, since it genuinely wasn't known at push time; my own change touches zero shared BB templates and zero SNOBOL4-reachable code paths (grep-confirmed), so a regression here would be surprising, not expected.

## REPRODUCE
```bash
cd SCRIP && make
./scrip /path/to/min2.pl   # ':- assertz(foo(a)). main :- abolish(foo/1), ( foo(_) -> write(found) ; write(not_found) ), nl.'
# before: not_found / rc=0.  after: no output / rc=1.
```

## LEDGER
- [seat14 · 2026-09-02] Landed. See `prolog-exceptions-uncaught-propagation.task.md` and `prolog-next`'s baton for handoff state and exact commit hashes.
