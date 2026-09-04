# FINDING — `unify_with_occurs_check/2` does not exist in SCRIP's Prolog at all

**seat04, 2026-09-04. Measured while walking the isolation ladder, row
`prolog-ladder-every-feature-in-isolation-with-variations`, rung01 construct `unification`.**

## What happened

ISO/IEC 13211-1 sec 8.2.2 names `unify_with_occurs_check/2` as a standard builtin distinct from
`(=)/2`: it unifies like `=` but fails instead of constructing a cyclic term when a variable
occurs inside the term it would be bound to. Minting the ladder's `occurs_check` form as the
smallest witness that distinguishes it from plain `=`:

```prolog
:- initialization(main).
main :- (unify_with_occurs_check(X, f(X)) -> write(yes) ; write(no)), nl.
```

SWI-Prolog 9.0.4 (the oracle): prints `no` (correctly fails the occurs check), rc=0.

SCRIP (`./scrip`, both m3 and m4, tree `SCRIP 2cd69baa3`): stdout is **empty** in both modes.
stderr carries `Warning: goal raised exception: error(existence_error(procedure,
unify_with_occurs_check/2), unify_with_occurs_check/2)` — the predicate is not implemented at
all, not merely wrong. rc is 0 in both modes despite the uncaught existence_error (a second,
smaller shape worth someone's attention separately: an unhandled ISO existence_error exiting 0
rather than nonzero looks like its own instrument gap, not filed further here since it's outside
this row's scope).

## Scope

This is a missing-builtin gap, not a fixture or instrument defect, so per this row's own brief
it is not mine to cure (Sonnet-seat role: mint, witness, file, keep walking; the HQ cures
compiler-level reds). The witness is wired into the master red on purpose:
`ladder__rung01_unification_occurs_check` / entry `unify_occurs_check_1`, corpus `6b81f83b7`+
(this session's rung01 push). It is **not** marked xfail (THERE IS NO XFAIL) — it reads as a
genuine FAIL in `test_prolog_ladder.sh --only 1` (and every `--to N` for N>=1) until either the
builtin lands or this finding is otherwise dispositioned.

## Fix shape (not attempted here)

`unify_with_occurs_check/2` needs the same occurs-check that presumably already exists somewhere
in the unifier for other purposes (or needs one written) exposed as a callable builtin, wired
through whatever dispatch table routes `catch/3`-class deterministic-with-failure builtins in
`src/parsers/prolog` / `src/lower/lower_prolog.c` / the rung6-era builtin table. Not investigated
further — this finding is the measurement, not the cure.
