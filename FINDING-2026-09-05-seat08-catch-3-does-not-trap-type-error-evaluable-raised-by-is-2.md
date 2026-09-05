# FINDING — `catch/3` does not trap `type_error(evaluable, _)` raised by `is/2`, though it traps every other shape tried

**seat08, 2026-09-05, FLEET-12. Measured while walking the isolation ladder, row
`prolog-ladder-every-feature-in-isolation-with-variations`, rung14 construct `evaluable functors`,
form `type_error_on_non_evaluable`.**

## What happened

ISO/IEC 13211-1 sec 9.3.4 requires `X is <non-evaluable functor>` to raise
`error(type_error(evaluable, F/A), _)`, catchable like any other ISO error ball. The ladder's
own witness:

```prolog
:- initialization(main).
main :-
    catch(( _ is foo(1), write(noerror) ),
          error(type_error(evaluable, foo/1), _),
          write(caught)), nl.
```

SWI-Prolog 9.0.4 (the oracle): prints `caught`, rc=0.

SCRIP (`./scrip`, both m3 and m4, tree SCRIP `23c6e45d6`): the `catch/3` does **not** run the
recovery goal at all. stdout is empty in both modes; stderr carries `Warning: goal raised
exception: error(type_error(evaluable, foo/1))`, rc=1 — the exception propagates straight past
the installed catch frame as if no catcher were present.

## Ablation (this is not a general `catch/3` bug, nor about arity or variable naming)

Five variants, all against the current build, m3 only (the m4 path showed the identical shape on
the full witness above, so not re-run per variant):

| variant | catcher | result |
|---|---|---|
| `X is foo` (arity 0, named var) — **the exact shape of the pre-existing general-suite entry `catch_1` (rank 445)** | `error(type_error(evaluable, foo/0), _)` | **NOT caught** |
| `X is foo(1)` (arity 1, named var) | `error(type_error(evaluable, foo/1), _)` | **NOT caught** |
| `_ is foo(1)` (arity 1, anon var) | `error(type_error(evaluable, foo/1), _)` | **NOT caught** |
| `X is bar(1,2)` (arity 2) | `error(type_error(evaluable, bar/2), _)` | **NOT caught** |
| `X is foo(1)` | wildcard `_` catcher | **NOT caught** |

A wildcard catcher failing rules out a unification/ball-shape mismatch: nothing about this
specific ball is special to `catch/3`'s matcher. Two further control tests pin the defect
precisely:

- `catch(( X is 1/0, ... ), error(evaluation_error(zero_divisor), _), ...)` — **raised by the
  same operator `is/2`, one line away in the ladder's own methodology note** — IS caught
  correctly (rc=0, `caught`).
- `catch( throw(error(type_error(evaluable, foo/1), context(is/2,_))), error(type_error(evaluable,
  foo/1), _), write(caught) )` — a **user-level `throw/1` of the byte-identical ball shape** — IS
  caught correctly (rc=0, `caught`).

So: `catch/3` itself is sound, and `is/2`'s own exception-raising path is sound for
`evaluation_error`. The defect is narrow — specifically the code path inside the arithmetic
evaluator that detects an unrecognized/non-evaluable functor and raises `type_error(evaluable,
F/A)` does not unwind through whatever mechanism installs and searches catch frames; it looks
like a different (fatal, catch-bypassing) raise path than the one `evaluation_error` and
user `throw/1` both go through.

## Blast radius

This is not confined to the new ladder witness: the pre-existing general-suite entry `catch_1`
(rank 445, corpus `tests/prolog/ALL.pl`/`ALL.csv`, origin `rung38_iso_errors__01_type_error`) is
the *exact* arity-0 shape above and, extracted and run directly against this same build, **fails
identically** (confirmed this session — `master_extract_name catch_1` then `./scrip --run`:
uncaught, rc=1, vs. its own `.ref` of `caught_type_error`). Whatever board currently scores that
entry green is scoring a stale or non-representative run; re-measure it before quoting it as
passing.

## Scope

Missing/misrouted exception path in the arithmetic evaluator's non-evaluable-functor case, not a
fixture or instrument defect — not mine to cure (Sonnet-seat role: mint, witness, ablate, file,
keep walking; hq_C's lane per the row's own LANE REVIEW for rung14). Wired into the master **red
on purpose**: `ladder__rung14_evaluable_type_error_on_non_evaluable` / entry
`evaluable_type_error_on_non_evaluable_1`. Not marked xfail (THERE IS NO XFAIL) — it reads FAIL
in `test_prolog_ladder.sh --only 14` (and every `--to N` for N>=14) until cured.

## Fix shape (not attempted here)

Find wherever `is/2`'s functor dispatch falls through to "unrecognized" and compare how it raises
against the `evaluation_error(zero_divisor)` path in the same evaluator (likely
`src/runtime/runtime_eval.c` or the Prolog arithmetic builtins under `src/runtime/`) — the
zero-divisor path already does the right thing, so it is the template, not a fresh design.
Sent to hq_C directly (this rung's owning lane) rather than filed only.
