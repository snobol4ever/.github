# FINDING — Prolog LCO (rung 11) drops the output-argument binding through the tail chain

**seat04, 2026-09-04.** Tree: SCRIP `ce6b2817d` · corpus `524f32243` · .github `680a617b`. MODE `FLEET-16`.
Row `prolog-ladder-every-feature-in-isolation-with-variations` (isolation walk, hq_C). Found while minting
rung11 (`last_call`) isolation witnesses — not a regression caused by this session (SCRIP tree unchanged
all session; the same `ce6b2817d` graded every rung 6-13 witness below).

## The result

Any tail-recursive predicate that threads an **output argument** through the recursive call, to be bound in
the base case, loses that binding by the time control returns to the ORIGINAL caller — but only when the
recursive call is in tail position (i.e. only when LCO fires). The identical predicate, made non-tail by
appending a trailing `true`, is correct. Two independent minimal witnesses, two different shapes:

**Accumulator (arithmetic), LCO'd — WRONG:**
```prolog
sum_acc(N, Acc, Acc) :- N =< 0, !.
sum_acc(N, Acc, Sum) :- N > 0, Acc1 is Acc + N, N1 is N - 1, sum_acc(N1, Acc1, Sum).
main :- sum_acc(1000, 0, Sum), write(Sum), nl.
```
Expected `500500` (swipl). scrip prints `_G0` — Sum is completely **unbound**, not merely wrong.

**List accumulator (the classic `append`), LCO'd — WRONG:**
```prolog
myapp([], L, L).
myapp([H|T], L, [H|R]) :- myapp(T, L, R).
main :- myapp([1,2], [3,4], R), write(R), nl.
```
Expected `[1,2,3,4]`. scrip prints `[1|_G0]` — only the first cons cell is real; everything the recursion
was supposed to build after it is an unbound tail.

## Control arm — the same predicates, non-tail, are CORRECT

Appending `true` after the recursive call moves it out of tail position, which the existing LCO admission
test (FINDING-2026-09-03-hq_P) refuses on sight — this disables LCO for the identical logic:

```prolog
sum_acc3(N, Acc, Sum) :- N =< 0, !, Sum = Acc.
sum_acc3(N, Acc, Sum) :- N > 0, Acc1 is Acc + N, N1 is N - 1, sum_acc3(N1, Acc1, Sum), true.
main :- sum_acc3(1000, 0, Sum), write(Sum), nl.
```
→ `500500`. Correct.

```prolog
myapp2([], L, L) :- true.
myapp2([H|T], L, [H|R]) :- myapp2(T, L, R), true.
main :- myapp2([1,2], [3,4], R), write(R), nl.
```
→ `[1,2,3,4]`. Correct.

Same clauses, same arguments, same recursion depth — the only variable between the wrong pair and the
right pair is tail position. This isolates the defect to the LCO fast path itself, not to unification,
`is/2`, cut, or list construction in general (all proven working elsewhere in the rung 0-9 walk).

## What this is NOT

Ruled out by isolated sub-tests before landing on the above:
- **Repeated head variable as implicit unify** (`p(X,X) :- write(matched).`) works fine standalone —
  not the base-case pattern's fault.
- **`findall/3` with a ground/constant template** (`findall(x, true, L)`) works fine — not what broke
  `rung13`'s `semidet` witness's `findall(x, even(4), L)` (same root cause as here: `length(L,N)` after
  it also depends on a binding surviving a tail call, since `even/1`'s own call sits in a chain).
- Plain (non-recursive, non-tail) unification of a repeated or fresh variable is unaffected everywhere
  else in the corpus — this is specific to the LCO-rewritten call site.

## Why this reads as a gap in FINDING-2026-09-03-hq_P, not a new mechanism

That finding's own verification measured **stack flatness** (RSS at N=1000 vs N=1000000) using a witness
whose base case prints *inside itself* (`count(N,N) :- !, write(...)`) — it never needed a value to survive
the trip back up through the collapsed frames to the original caller, because it never looked at anything
after the call returned. Every rung 0-9 SNOBOL4/Icon/Prolog control arm that finding ran checked *that LCO
fires* (the RSS number) and *that it doesn't break non-tail siblings* — never that **a live binding is still
visible in the caller once the tail-recursive chain has finished succeeding.** That finding's own closing
line applies to itself: *"A verification list is evidence about what was run, never about what was not."*
The `sum_acc`/`myapp` shape above — get a result back from a loop — is arguably the single most common
reason anyone writes a tail-recursive Prolog predicate at all (accumulator sum, naive reverse, DCG
translation state-threading), so this is not an edge case; it likely also explains rung11's own
`nreverse_large` and rung13's own `semidet` isolation witnesses failing (both filed as RED against this
FINDING rather than re-diagnosed independently — same shape, same cause).

## Affected ladder rows (RED, filed against this FINDING, not independently diagnosed)

- rung11 `last_call`: `last_call_accumulator_loop`, `last_call_nreverse_large`
- rung13 `determinism`: `determinism_semidet` (its `findall(x,even(4),L)` + `length/2` chain depends on
  the same surviving-binding property)

## Not chased further here

Root-causing *why* the LCO fast path clobbers the output cell (the likely shape, per
FINDING-2026-09-03-hq_P's own description of the mechanism: the tail call reuses the caller's frame slots
rather than landing fresh, so an output argument that's supposed to alias the caller's variable cell may be
getting rebound to a callee-local slot instead of dereferencing through to it) is `src/runtime/rtx/*.s` /
`src/templates/bb/` work belonging to whoever owns rung 11 next (hq_C's lane; hq_P built the original
feature). This FINDING is the isolation walk's job: minimal, control-armed, precisely located — not the cure.
