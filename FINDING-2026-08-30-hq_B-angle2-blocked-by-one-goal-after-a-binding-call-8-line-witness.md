# FINDING: all 21 Prolog triangulation kernels crash for one reason — **a named variable bound by a user-predicate call, followed by one more goal, re-entered by backtracking**. 8-line witness, both modes.

**Seat:** hq_B (TRIO) · **Date:** 2026-08-30 · **Row:** `bench-grids-rebase-to-two-number-basis` · **Found while:** trying to unblock angle 2, which would have rescued the refused GNU Prolog work column.

## ⛔ THIS FINDING OPENS BY RETRACTING MY OWN CLAIM FROM AN HOUR EARLIER

I told ceo that `bench_triangulate_prolog.sh`'s header was **stale** and that angles 1–2 were available for m3/m4. **That was wrong.** The header describes a real, live defect. Angle 2 is still blocked and the gplc column stays refused.

**How I got it wrong is the reusable part.** I wrote a hand-made repro — a tail-recursive loop calling `fib` — saw it pass, and generalized. That is precisely the rule hq_C and I had reconciled that same morning:

> **A probe that does not reproduce the caller's invocation measures a different program.**

I committed it within hours of writing it down, in a message asserting that someone *else's* prose was stale. The header was describing something real; my probe was the wrong program. The authoritative instrument (`bench_prolog_fixed_iter.sh`) reports **m3 CRASH on every kernel** — `signal 11` ×10, `signal 6` ×5 in the first 15 — while `gnu` and `swi` columns fill normally.

## THE REAL DISCRIMINATOR IS FAR NARROWER THAN THE HEADER SAYS

The header claims SCRIP crashes on *"ANY repeated entry into a compiled user predicate — backtrack-driven, flat-sequential, or tail-recursive alike."* Measured, that is **over-broad**:

```
tail-recursive repeated entry              -> WORKS   (50 reps, m3 23617us / m4 23096us)
plain between/3 + fail failure-driven loop -> WORKS
```

Ablated to the minimum, the crash needs **one more goal after a binding call**:

```
bench__main :- fib(10,_).              rc=0    clean
bench__main :- fib(10,F).              rc=0    clean
bench__main :- fib(10,F), true.        rc=134  *** stack smashing detected ***
bench__main :- fib(10,F), write(F), nl. rc=134  *** stack smashing detected ***
```

`fib(10,F)` alone is fine. `fib(10,F), true` is not. **A single trailing `true` is the whole difference.**

## THE WITNESS (8 lines, crashes m3 AND m4, swipl clean)

```prolog
:- initialization(main).
fib(0,1) :- !.
fib(1,1) :- !.
fib(N,F) :- N>1, N1 is N-1, N2 is N-2, fib(N1,F1), fib(N2,F2), F is F1+F2.
bench__main :- fib(10,F), true.
l__(N) :- between(1, N, _), bench__main, fail.
l__(_).
main :- l__(20).
```

```
scrip --run      rc=134  *** stack smashing detected ***: terminated
scrip --compile  rc=134  *** stack smashing detected ***: terminated
swipl            rc=0    (only a harmless singleton-F warning)
```

## WHY ALL 21 KERNELS DIE AT ONCE

Every vanroy kernel is shaped `bench__main :- <compute>(..., F), write(F), nl.` — **exactly** the crashing form, in all 21. That is why the board shows a clean sweep of crashes rather than a scattered subset, and it is why a 21-kernel board was never going to localize it. The population is uniform in precisely the variable that matters.

This places the defect in the **PZ-4 / multiclause-backtrack family** — a clause carrying a continuation after a resumable call, re-entered by backtracking — adjacent to the parked rows `prolog-multiclause-fail-backtrack-segv` and `prolog-between-generator-backtrack-crash`. Correctness lane; **not taken here**, reported with the witness.

## CONSEQUENCE FOR THE BENCHMARK ROW

Angle 2 (fixed iterations) is the mechanism that would lift the sub-millisecond kernels above GNU Prolog's **1 ms clock floor**, where eight of ten currently read `work_us = 0` and are therefore refused rather than estimated. **That column stays refused until this defect is cured.** Angle 3 (work/overhead) is landed and published and does not depend on it.

## THE HEADER SHOULD BE NARROWED, AND THAT IS NOT COSMETIC IN EITHER DIRECTION

As written it tells a seat that *all* repeated entry is broken — too pessimistic, since two shapes now work, and pessimism in a header is what stops someone attempting a thing that would succeed. Narrowed to the measured discriminator it hands whoever takes the defect an **8-line witness instead of a 21-kernel board**. Both errors cost real passes; they just cost them in opposite directions.
