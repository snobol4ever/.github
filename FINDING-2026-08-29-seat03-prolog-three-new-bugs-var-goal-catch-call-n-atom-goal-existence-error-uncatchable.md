# FINDING — 3 previously-uncharacterized SCRIP Prolog bugs, found while triaging
# `tests-consolidate-prolog`'s loose-but-undeclared files that had no `.expected` pin at all. All 3 are
# deterministic (no backtracking, no generator/aggregation builtin) — a different bug class from the
# PZ-4/generator-resume-cell family, confirmed via ASM: none of these 3 call `rt_call_arr_gen` or
# `rt_jmp_frame_lexprep2`. m3 and m4 agree on all 3.

**seat03 · 2026-08-29 · row `tests-consolidate-prolog`.** Not fixed — compiler-debugging lane, not this
row's charter (matching every prior session's precedent: `write_canonical`, `abolish/1`, and the
between/3-family bugs were all left loose and mailed rather than fixed from this row). Left loose, **not**
KEEP.md'd — these are real, fixable interpreter/emitter gaps, not permanent design choices or standalone/
stdin-driven programs (see `GOAL`'s KEEP.md criterion).

## 0. The three files, oracle vs. scrip

Oracle: `/usr/bin/swipl -q` (files carry their own `:- initialization(main).`, so plain consult already
runs `main`; confirmed this is the identical convention `resolve_oracle_bin`'s `-q -g halt` already uses for
this corpus, just without needing to reach for `-g` since these files self-invoke). All 3 rc=1 under scrip
both m3 and m4 (spot-checked m4 for all 3 — identical output/rc to m3, no mode divergence).

| file | construct under test | swipl oracle | scrip actual (m3==m4) | `rt_call_arr_gen`/`rt_jmp_frame_lexprep2` in `.s`? |
|---|---|---|---|---|
| `rung31_bridge_catch/04_var_goal_userpred.pl` | `catch/3` where the goal is a **variable bound to a user predicate call** | `42` | *(nothing printed)* | no / no |
| `rung33_bridge_callN/04_call3_user_pred.pl` | `call/4` where the goal is a **variable bound to a bare atom**, reconstructing the compound from extra args | `7` | *(nothing printed)* | no / no |
| `rung38_iso_errors/03_existence_error.pl` | `catch/3` catching `error(existence_error(procedure, Name/Arity), _)` from calling an undefined predicate | `caught_existence_error` | `** Error 22 in statement 0`<br>`   Undefined function called` | no / no |

## 1. `rung31_bridge_catch/04` and `rung33_bridge_callN/04` — same family, both silent (no output, no error)

Sources (both files' own header comments already name the exact mechanism under test):

```prolog
% rung31_bridge_catch/04_var_goal_userpred — goal-as-var dispatches user predicate.
% Bridge requirement: walker must recognize TT_COMPOUND with user-defined
% functor (not in builtin or arith table) and route to pl_box_choice + bb_broker
% for clause resolution rather than treating as builtin.
double(X, Y) :- Y is X * 2.
main :- G = double(21, R), catch(G, _, fail), write(R), nl.
```
```prolog
% rung33_bridge_callN/04_call3_user_pred — call/3 with user predicate and two args.
% G is bound to a user-defined predicate atom; call(G, A, B) reconstructs
% the compound G(A,B) and dispatches via pl_box_choice.
add(X, Y, Z) :- Z is X + Y.
main :- G = add, call(G, 3, 4, R), write(R), nl.
```

Both print **nothing** and exit rc=1 — not a crash, not a wrong value, no partial output. `main/0` simply
fails as a whole with no diagnostic. Both files' own comments indicate this is a known-deliberate probe of
"goal supplied via a variable, naming a user predicate, dispatched through `pl_box_choice`/`bb_broker`
rather than the builtin table" — i.e. these look like they were written specifically to test a bridge/dispatch
seam the corpus authors already suspected was fragile, not a random find. Not ASM-diffed further (would need
`--dump-ir`/`--dump-bb` on the `catch(G,_,fail)`/`call(G,A,B,R)` compound-reconstruction path to say *why* it
silently fails; out of this row's charter to pursue).

## 2. `rung38_iso_errors/03_existence_error` — the error is real, but not catchable

```prolog
main :-
    catch(
        no_such_pred(42),
        error(existence_error(procedure, no_such_pred/1), _),
        write(caught_existence_error)
    ), nl.
```

scrip *does* detect the undefined predicate — it raises its own top-level error (`Error 22, "Undefined
function called"`) — but that error is never routed through `catch/3`'s catcher-unification machinery, so
`error(existence_error(procedure, no_such_pred/1), _)` never gets a chance to match and the whole process
aborts to scrip's own top-level handler instead of running the recovery goal. Two independently plausible
causes, not distinguished here: (a) scrip's undefined-predicate error is not represented as a proper ISO
`error/2` term the way `catch/3` expects, or (b) it is represented correctly but raised at a point in the
call machinery `catch/3`'s installed handler doesn't see (e.g. resolved at link/dispatch time rather than as
a catchable runtime throw). Needs an `--dump-ir` look at how `catch/3` installs its handler vs. where the
"Undefined function called" diagnostic is emitted from, before guessing further.

## 3. Confirmed independent of the PZ-4/generator-resume-cell family

All 3 files are single-shot, deterministic — no `fail`-loop, no `findall`/`bagof`/`between`, no
`assertz`/`retract`. `--compile`'d output for all 3 contains **zero** calls to `rt_call_arr_gen` and **zero**
calls to `rt_jmp_frame_lexprep2` (checked directly, not assumed from the absence of a generator construct in
the source). These are a genuinely separate bug class from
`FINDING-2026-08-29-seat03-prolog-generator-defect-blast-radius-widens-to-bagof-findall-clause-and-plain-assertz-backtracking.md`
filed alongside this one.

## 4. State

- Trees measured: SCRIP `358a88d6`, corpus `a37491bd`, `.github` `a63c19d9`; `make -j4 scrip && make
  libscrip_rt` (investigative build, not `make pristine` — no gate verdict claimed here).
- Left loose, not KEEP.md'd, not fixed — out of this row's charter (test consolidation, not compiler
  debugging), matching every prior precedent on this row.
- Mailed `hq_C` (this row's standing convention: "a wrong ANSWER belongs to hq_C").
