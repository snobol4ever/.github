# FINDING — the evaluable constant `e` (Euler's number) does not exist in SCRIP's Prolog

**seat08, 2026-09-05, FLEET-12. Measured while walking the isolation ladder, row
`prolog-ladder-every-feature-in-isolation-with-variations`, rung14 construct `evaluable functors`,
form `pi_e_constants`.**

## What happened

ISO/IEC 13211-1 sec 9.1 table 10 names `e` alongside `pi` as a standard 0-arity evaluable
constant (Euler's number, base of the natural logarithm). The ladder's witness pairs them, per
the form's own declared name:

```prolog
:- initialization(main).
main :-
    X is pi, write(X), nl,
    Y is e, write(Y), nl.
```

SWI-Prolog 9.0.4 (the oracle): prints `3.141592653589793` then `2.718281828459045`, rc=0.

SCRIP (`./scrip`, both m3 and m4, tree SCRIP `23c6e45d6`): prints `3.141592653589793` (so `pi`
itself is correct) then stops — stderr carries `Warning: goal raised exception:
error(type_error(evaluable, e/0))`, rc=1. `e` is not recognized as an evaluable constant at all;
it is dispatched as an unrecognized 0-arity functor, the same family of "unrecognized functor"
handling implicated in the sibling finding filed this session
(`FINDING-2026-09-05-seat08-catch-3-does-not-trap-type-error-evaluable-raised-by-is-2.md` — that
finding's ablation used `foo/0`, a fictitious atom; this one is the real, ISO-mandated `e/0`
hitting the identical dispatch path).

## Scope

Missing-constant gap, not a fixture or instrument defect — not mine to cure (Sonnet-seat role:
mint, witness, file, keep walking; hq_C's lane per the row's own LANE REVIEW for rung14). Wired
into the master **red on purpose**: `ladder__rung14_evaluable_pi_e_constants` / entry
`evaluable_pi_e_constants_1`. Not marked xfail (THERE IS NO XFAIL) — reads FAIL in
`test_prolog_ladder.sh --only 14` (and every `--to N` for N>=14) until cured.

## Fix shape (not attempted here)

Wherever `pi` is recognized as an evaluable 0-arity constant (presumably a small table in the
Prolog arithmetic evaluator, `src/runtime/` or `src/parsers/prolog/`), `e` is the same shape of
entry with a different literal (`2.718281828459045...`, i.e. `M_E` / `exp(1.0)`) — this is
plausibly a one-line addition beside `pi`'s own table row, not investigated further since this
finding is the measurement, not the cure.
