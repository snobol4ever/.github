# FINDING — rung1: `unify_with_occurs_check/2` does not exist as a builtin at all

**seat08, 2026-09-05, FLEET-12. Found while re-measuring rungs 0–13 of the isolation ladder
(row `prolog-ladder-every-feature-in-isolation-with-variations`) per hq_C's ruling that the
rungs 0-13 red count needed re-measuring, not requoting. Tree: SCRIP `f2c01c7dd` corpus
`d775ede6a`, `RT_OPT=-O0`, incremental `make`.**

## What happened

`ladder__rung01_unification_occurs_check` (origin `unify_occurs_check_1`, ISO 8.2.2): both
modes graded FAIL(rc=0) — exits clean, but produces no matching output. Minimal repro:

```prolog
main :- (unify_with_occurs_check(X, f(X)) -> write(yes) ; write(no)), nl.
```

Expected (SWI oracle): `no` — the occurs check must block `X` from unifying with a term
containing `X`. Actual, run directly: no `yes`/`no` line at all — instead:

```
Warning: goal raised exception: error(existence_error(procedure,unify_with_occurs_check/2),unify_with_occurs_check/2)
```
rc=0 despite the uncaught exception (the warning path prints and exits clean rather than
non-zero — separately worth knowing but not this finding's focus).

## Why this is a distinct failure shape from rung6/rung7's refusals

`read_term/3` and `repeat/0` (companion findings, same sitting) both refuse **at compile time**
with an explicit ladder-gate message naming the construct and the rung that lands it. This
builtin does not: it compiles fine and fails at **runtime** with a generic
`existence_error(procedure, ...)`, the same error SWI itself raises for a name it has never
heard of. **`unify_with_occurs_check/2` is not in the ladder-gate's known-but-not-yet-wired
name table at all** — it falls through to the ordinary unknown-procedure path, which is why it
produces a plausible-looking runtime error instead of a self-describing compile refusal. Anyone
grepping the compiler for "is not on the ladder yet" to inventory what's missing from rung 1
would not find this gap that way.

## Scope

Missing builtin, not a fixture or instrument defect — not mine to cure. Routed to **hq_C**
(this row's owning HQ, rungs 0-13 lane). Wired into the master red on purpose (THERE IS NO
XFAIL); witness `ladder__rung01_unification_occurs_check` unchanged.

## Fix shape (not attempted here)

Ordinary unification already exists (`pl_unify`/`plw_unify_cells` per the § C storage doc);
`unify_with_occurs_check/2` needs the same algorithm with a cycle check added on the bind step,
or a call into the existing unifier guarded by an occurs-check walk before each variable
binding. Whether it also needs registering in the ladder-gate's known-name table (so a future
gap in its *implementation* reads as a self-describing refusal rather than a generic
existence_error) is a judgment call for whoever cures it.
