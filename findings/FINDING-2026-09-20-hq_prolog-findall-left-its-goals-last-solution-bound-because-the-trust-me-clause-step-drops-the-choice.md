# FINDING 2026-09-20 hq_prolog: findall left its goal's LAST solution bound, because with no live choice the trail logs nothing

**Row:** prolog-findall-over-a-dynamic-predicate-yields-one-solution-when-it-follows-another-dynamic-findall (CEO-964).
**Cure:** SCRIP `src/lower/lower_prolog.c` -- the findall goal now runs inside `IR_BOUND`/`IR_UNMARK`.
**Tree:** SCRIP 76ef697a9 + this change, corpus 8d4656ada, .github 66eccbfc. Arena `SCRIP_HEAP_MB=1` throughout.

## WHAT IT ACTUALLY WAS, AND IT IS NOT WHAT THE ROW SAYS

`findall/3` left every variable its goal bound **still bound, at the last solution**, instead of restoring them.
`findall(X, s(X), L)` over `s(a). s(b). s(c).` returned `L=[a,b,c]` correctly **and left `X` bound to `c`**; swipl leaves it unbound.

Everything the row describes follows from that one fact, and nothing else is wrong:

- a second `findall` reusing the same template variable enumerated an **already-bound** goal --
  `findall(X,s(X),A), findall(X,s(X),B)` reads `3-1` (only `s(c)` matches);
- against a *different* predicate it reads `3-0` -- `findall(X,s(X),A), findall(X,t(X),B)` with `t(1). t(2). t(3).`
  yields **zero** solutions, because `X` is still `c`;
- `hb_pl_root_cells`'s `3-1-1-1-1` is exactly this: its five findalls all use the template variable `X`.

⛔ **IT IS NOT A COLLECTOR DEFECT, NOT A DATABASE DEFECT, AND NOT AN ENUMERATION DEFECT.**
Identical at `SCRIP_GC_STRESS` 0/1/3/5 and at the default arena. **A STATIC predicate reproduces it** (`3-1-1`), so the
dynamic database is not involved at all. The enumeration is correct throughout -- the survivor is `[c]`, the **last**
solution, not `[a]`, which is what an enumeration that stopped early would have left.

## ⭐ THE RULE ALREADY EXISTED. findall IS THE CONSTRUCT THAT NEVER GOT IT.

This is not a missing design. **`ARCH-PROLOG-BYRD-BOX-TRANSLATION.md` § B.14 already specifies the cure**, in the
wiring for the all-solutions loop: *"`Goal.ω → finish`: **undo `F.LOG`**, `F.B := F.B0`, unify(Result, list(F.ACC))"*,
and again in (iii): *"**`F.LOG` is undone at finish so the template's bindings never leak.**"* The implementation
never did it -- `lower_prolog.c` wired `Goal.ω` straight to `$findall_result`.

And **§ B.7 already carries the whole lesson**, discovered on the if-then-else and written down verbatim:
*"the mark was USELESS until the box also OPENED A CHOICE: with no live choice `pl_tr_needs_log` returns 0 for every
cell, so the unwind walked an empty suffix and the witness stayed red. ... **A construct that must undo must first be
a choice; that is now the rule, not a coincidence.**"*

⛔ **AND I WALKED INTO IT ANYWAY, WHICH IS THE POINT.** My first cure banked a mark and unwound to it, exactly the
arm § B.7 says is useless, and it changed nothing for exactly the reason § B.7 gives. The rule was written on the
construct where it was found and never applied to the other construct that needs it; a rule recorded beside its
discovery site is not the same as a rule enforced across the constructs it governs. The three constructs that call
`rt_pl_disj_open` (rung 3 disjunction, rung 7 generator, rung 5 bound) were each fixed when their own witness went
red. **findall had no witness that could go red** -- see the DONE-WHEN section below.

## ROOT CAUSE

The rung-2 clause step drops the choice on the **trust-me** (last) clause. `pl_tr_needs_log` (`src/runtime/rt/rt_pl_trail.h`)
returns 0 for **every** cell when no choice is live, so the last clause's binding of the caller's variable is **never logged**.
findall then intercepts the goal's exhaustion at ω and builds its result with those bindings standing.
`bb_bound.cpp` states this exact hazard in its own comment: *"a mark is useless while nothing is LOGGED, and with no live
choice pl_tr_needs_log returns 0 for every cell."*

**Predictive confirmation (the measurement that decided it).** Add a trailing always-failing clause `s(_) :- fail.` so a
choice stays live past the last solution: the same program goes **green** (`unbound 3-3`) while the identical 3-clause
program reads `bound(c) 3-1`. Nothing else differs.

⭐ **AND THE MEASUREMENT THAT KILLED MY FIRST CURE, RECORDED BECAUSE IT IS THE EXPENSIVE HALF.**
I first banked a trail mark in the findall accumulator and unwound to it at `$findall_result`. It changed **nothing**.
A temporary instrument in the result road measured `delta_entries=0` -- the trail between `$findall_new` and
`$findall_result` was **empty**. A trail unwind cannot restore a binding that was never trailed. That arm is reverted;
it is recorded here so nobody re-derives it.

## THE CURE

Exactly what § B.14 already specified. Run the findall goal inside the barrier the machine already has: `IR_BOUND` banks the trail top **and calls
`rt_pl_disj_open`**, which lowers `F.HI` to the frame base so the goal's bindings to the enclosing activation become
loggable; the paired `IR_UNMARK` unwinds to that mark on the exhausted edge. Flags `pl_fence_on() ? 5 : 1` -- the same
ones `pl_lower_ite` already uses for `\+`, `once/1`, `->`, `forall` and `ignore`, which is why those four were never
affected and `\+ \+ s(X)` always left `X` unbound. No new mechanism, no new global, no runtime allocation.
Covers `findall/3`, `findall/4`, `bagof/3` and `setof/3` on the no-free-variable road.

## ⛔ THREE CLAIMS IN THE HANDED-OVER BISECT ARE FALSE ON THIS TREE

The row was handed over with the bisect "already done"; I re-measured it and three of its statements do not hold. Each
one, believed, routes a seat to the database road, where there is nothing to find.

| handed-over claim | measured here |
|---|---|
| "findall over a static p/1 three times reads 3-3-3" | **`3-1-1`** -- static reproduces it |
| "findall over the SAME dynamic predicate twice reads 3-3" | **`3-1`** |
| "enumerating d2 once by plain backtracking before its findall restores 3" | **still 1** |

The routing sentence *"it is a Prolog ENUMERATION defect in the runtime road -- start at the db enumeration, not at the
map"* is wrong in both halves: the db is not involved, and the enumeration is correct.

⭐ **The discriminator nobody had isolated is the TEMPLATE VARIABLE, not the predicate.** Two findalls over the same
predicate with *distinct* template variables are green; two over *different* predicates with the *same* template
variable are red. That is why `hb_pl_findall.pl` was green all along -- its three findalls use `X`, `Y-Z` and `Q`.

## ⛔ THE ROW'S OWN DONE-WHEN COULD NEVER HAVE FAILED FOR THIS DEFECT

The baton's `DONE-WHEN` greps `scripts/gc_witnesses/hb_pl_findall.pl`. **That witness was already green before the cure**,
at all four stress levels, for the reason above. The GOAL text names the right one ("reads 3-3-3-3-3" is
`hb_pl_root_cells.pl`). A DONE-WHEN that passes on the unfixed tree is not a gate; it is reported to the ceo and the
baton's DONE-WHEN is replaced with one that fails on the base tree and passes on the cured one.
