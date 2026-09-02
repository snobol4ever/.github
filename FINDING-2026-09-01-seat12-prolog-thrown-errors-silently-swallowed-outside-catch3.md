# FINDING — uncaught Prolog exceptions are silently swallowed by every control construct except
# catch/3; this is the mechanism behind GOAL-PROLOG-100.md's banked "cross-clause catch/throw" item,
# and it blocks row `prolog-abolish-leaves-predicate-defined-but-empty` from reaching its stated
# observable outcome

**seat12 · 2026-09-01 · row `prolog-abolish-leaves-predicate-defined-but-empty`**

## Summary

Landed the abolish/1 fix this row asked for (SCRIP `src/runtime/unification.c`: `rt_pl_dyn_abolish_cell`
now removes the dyn-pred row instead of clearing it; `rt_pl_dyn_iter_gen` now calls
`rt_pl_iso_throw_pi("existence_error", "procedure", Name, Arity)` when no row is found). gdb confirms
both halves fire correctly and in the right order (breakpoints on `rt_pl_dyn_abolish_cell`,
`rt_pl_dyn_iter_gen`, `rt_pl_iso_throw_pi` — `g_pl_dyn_pred_n` goes 1→0 across abolish, and
`rt_pl_iso_throw_pi(errfn="existence_error", what="procedure", nm="fact", ar=1)` is reached on the
next call). **But the observable output is unchanged** — `rung15_abolish_abolish_existing.pl` still
prints `gone`, not an uncaught error, in both modes.

## Root cause: nothing outside catch/3 ever checks `rt_pl_throw_pending()`

`rt_pl_iso_throw_pi` → `plc_iso_ball` → `rt_pl_throw_set` only ever SETS `g_pl_throw_ball`; it does not
unwind anything itself. Propagation depends entirely on callers checking `rt_pl_throw_pending()` and
treating a pending throw differently from an ordinary failure. Measured:

```
grep -c "rt_pl_throw_pending()" src/runtime/by_name_dispatch.c   → 8
grep -c "rt_pl_throw_pending()" src/driver/*.c src/templates/bb/*.cpp  → 0
```

All 8 checks live inside `by_name_dispatch.c`'s `catch/3`/`plc_*` machinery. **Zero checks exist in the
driver or in any BB codegen template.** The generator-dispatch call site a compiled `IR_CALL_BUILTIN_GEN`
/`IR_SUSPEND` pair reaches (`rt_call_arr_gen`, `by_name_dispatch.c:4864`) returns `FAILDESCR` on a throw
exactly as it would for genuine exhaustion — the two are indistinguishable to whatever compiled code
consumes the result. Confirmed the same gap on the DET dispatch side too: `$throw` itself
(`by_name_dispatch.c:2655`) sets the ball and returns `FAILDESCR`, so an un-caught `throw/1` as a
clause's last goal just makes the clause "fail" — same generic `Warning: initialization goal failed:
main/0` a plain `fail` would produce, no distinct signal, rc=0.

## Three independent witnesses, not specific to abolish or to generators

| construct | expected (swipl) | SCRIP today | mechanism |
|---|---|---|---|
| `between(a, 5, X)` | `type_error(integer, a)` | silently fails, `->` takes else | generator throw (`rt_pl_between_gen`) |
| `clause(foo(_), true)` on a **static** `foo/1` | `permission_error(access, private_procedure, foo/1)` | silently fails | generator throw (`rt_pl_clause_gen`) |
| `fact(_)` after `abolish(fact/1)` | `existence_error(procedure, fact/1)` | silently fails, prints `gone` | generator throw (`rt_pl_dyn_iter_gen`, this row's fix) |
| `throw(oops)` as a bare clause goal, nothing after | uncaught, distinct abort | clause just "fails", generic warning | DET throw (`$throw`) |

Control run, same file: `catch(( write(a), throw(oops), write(never) ), E, (write(caught), write(E)))`
→ SCRIP prints `acaughtoops`, byte-matching swipl. **catch/3 itself works.** The gap is specifically
"propagate past an intervening `,`/`;`/`->`/`\+` that is not the exact goal a `catch/3` wraps" — i.e.
exactly ISO's unwind-to-nearest-enclosing-catch-or-top-level behavior, which nothing outside catch/3
implements.

## This is not a new scope discovery, only a mechanism for a known one

`GOAL-PROLOG-100.md:173` already banks two separate items in its PZ-9 backlog: *"silent-fail on
undefined predicates (→ existence_error)"* (this row) and, as a distinct feature-rung item,
*"cross-clause catch/throw"*. This FINDING is the mechanism trace for the second item, discovered while
trying to close the first. Fixing it means making `,`/`;`/`->`/`\+` (wherever they're compiled — BB
templates, shared with Icon per `bb_call_proc_staged.cpp`'s existing note on the adjacent
`prolog-backtracking-yields-first-solution-only` row) check `rt_pl_throw_pending()` after every subgoal
and unwind rather than continue, plus a top-level check that turns a still-pending ball at the end of a
directive into swipl-shaped uncaught-error output. That is BB-codegen work with real blast radius
(shared-node, both-medium), not a same-session extension of a data-structure fix in `unification.c`.

## Disposition

Not fixed here — out of this row's charter (see this row's own DONE-WHEN, which only ever asked for the
abolish-specific half). Minted as its own row, `prolog-exceptions-uncaught-propagation`, ranked near the
backtracking row since both touch generator/control-flow codegen and may share a landing session. This
row (`prolog-abolish-leaves-predicate-defined-but-empty`) is PARKED BLOCKED-ON it — the code fix already
landed and is correct progress (verified independently: the dyn-pred table now genuinely undefines on
abolish, and the throw genuinely fires), but the 3 `.expected` pins cannot be safely regenerated to their
oracle-true (empty-output, uncaught-error) values until propagation actually produces that output —
pinning them now would enshrine a permanently-red regression against a still-true bug, the exact
anti-pattern this row's own mint warned about from the other direction.

## What's actually needed, for whoever picks up `prolog-exceptions-uncaught-propagation`

1. Find where `,`/`;`/`->`/`\+` are compiled (BB templates — likely near `bb_call_proc_staged.cpp` /
   wherever `IR_CONJ`/`IR_DISJ`/`IR_ITE`-equivalent Prolog nodes lower) and add a `rt_pl_throw_pending()`
   check after every subgoal call, short-circuiting to unwind (β/ω-port equivalent of "abandon, don't
   continue") rather than treating the result as ordinary fail.
2. A top-level check (driver, after each directive/`initialization/1` goal) that formats a still-pending
   ball into an swipl-shaped uncaught-error report and a distinguishable rc — today even the working
   `catch/3` case leaves rc=0 on the caught-and-handled path, which is correct, but the genuinely
   uncaught case is currently indistinguishable from that.
3. Re-verify against `between(a,5,X)`, `clause(foo(_),true)` on a static predicate, and this row's 3
   abolish witnesses as independent regression witnesses — none of them share a mechanism with the
   generator resume-cell frame-wipe `prolog-backtracking-yields-first-solution-only` is tracing (that
   bug is about RETRIES losing state; this one fires on the FIRST call, before any resume cell exists),
   but the codegen they'll touch may be adjacent or the same file — coordinate before landing either.
