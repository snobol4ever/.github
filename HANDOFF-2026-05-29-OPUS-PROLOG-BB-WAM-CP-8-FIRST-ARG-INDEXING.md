# HANDOFF — Prolog BB — WAM-CP-8 First-Arg Clause Indexing

**Author:** Claude Opus 4.8 · **Date:** 2026-05-29
**Parent one4all commit:** `e9f09fdc`
**Goal:** `GOAL-PROLOG-BB.md` · **Rung:** WAM-CP-8 (now `- [x]`)

---

## What landed

First-argument clause indexing for multi-clause Prolog predicates, mode-2 only.
137 lines, purely additive, three files, zero deletions:

- `src/include/BB.h` (+23) — index-key encoding macros + two struct fields.
- `src/lower/lower_pl.c` (+31) — compile-time key computation.
- `src/lower/bb_exec.c` (+83) — runtime key + CP-elision dispatch + trace.

NO emitter, template, SM, or FACT change. This is interpreter logic; it emits
zero x86 bytes. Both FACT grep arms are byte-identical to baseline (0 and 12).

## The idea

A multi-clause predicate lowers to a `BB_CHOICE` node holding `bodies[]`. On
fresh entry it unconditionally `pl_cp_push`es a `PL_CP_CLAUSE` choice point, then
tries each clause body, leaving the CP live for backtracking. For a call like
`color(grape, X)` against a four-fact table, only one clause can match — the CP
and the scan of the other three are pure waste, and (more importantly for the
benchmark arc) the live CP defeats LCO.

WAM-CP-8 computes a **first-arg index key** for each clause at lower time and,
at runtime, filters the clause set by the caller's bound first arg. When exactly
one clause survives the filter AND its body is statically single-solution, the
clause is dispatched with **no `pl_cp_push`** — `g_pl_bfr` is left unchanged.
That unchanged-`g_pl_bfr` property is the WAM-CP-8 gate and is exactly what
Phase B2 of WAM-CP-6 LCO needs (gate condition 2).

## Key encoding (`BB.h`)

Class-tagged `long`. Bits 60-62 carry a class tag so the key spaces never
collide; payload below.

```
PL_IDX_VAR    = 0      var-headed clause: wildcard, matches any caller arg
PL_IDX_NOKEY  = -1     caller arg unbound/var at runtime: cannot filter
PL_IDX_CLS_ATOM (1<<60) | atom_id
PL_IDX_CLS_INT  (2<<60) | int value
PL_IDX_CLS_FLT  (3<<60)              (float: class-only, no value refinement)
PL_IDX_CLS_CMP  (4<<60) | (functor<<16 | arity)
```

Compile-time `pl_clause_first_arg_key(clause, n_args)` reads `clause->c[0]`
(`TT_ILIT/TT_FLIT/TT_QLIT/TT_NAME/TT_VAR/TT_MAKELIST/TT_FNC`). Runtime
`pl_term_first_arg_key(Term*)` reads the deref'd `g_pl_env[0]`
(`TERM_INT/FLOAT/ATOM/COMPOUND/VAR`). Same macros both sides → match is an exact
`long` compare. Empty list `[]` keys as the atom `[]`; non-empty list literal
keys as `./2`.

## Dispatch (BB_CHOICE fresh entry, `bb->state == 0`)

```
ckey = pl_term_first_arg_key(g_pl_env[0])
if ckey == PL_IDX_NOKEY: fall through to normal scan   # unbound arg, no filter
count candidates: clauses where idx_key[ci] == ckey OR == PL_IDX_VAR
  ncand == 0:                          fail immediately (bb->ω)
  ncand == 1 && body single-solution:  run it, NO pl_cp_push, det commit
  else:                                fall through to unchanged CP scan
```

The det-commit path leaves `bb->state == 0` and `zc->cp == NULL`, so any later
backtrack into this node simply re-fails — correct, because the one matching
single-solution clause has produced its one answer.

## The bug that taught the safety gate

First cut gated the commit only on `ncand == 1`. GATE-SWI regressed 57→56:
`memberchk(f(x,b), [...])` calls `member/2`; with a bound first arg the index
selected `member/2` clause 2 (`member(X,[_|T]) :- member(X,T)`) as the unique
non-var-conflicting candidate and committed deterministically — discarding the
recursive `member(X,T)` tail call's choice points, so the second list element
was never reached. The body of that "unique" clause is NOT deterministic.

Fix: a new stricter static helper `bb_body_single_solution(bbg)` returns 1 only
if the body has NO `BB_CHOICE`, `BB_PL_ALT`, or `BB_PL_CALL` of any kind. This
is stricter than the Phase-B1 `bb_body_cp_free_except_tail` (which exempts a
tail `BB_PL_CALL`), because clause-selection commit lets the caller backtrack
into the body — a tail recursive call is a live generator there. Gated on this,
GATE-SWI is back to 57/57.

**Lesson for the next dev:** a unique *clause selection* is not the same as a
deterministic *predicate*. The clause body can still be a multi-solution source.
Only elide the clause-selection CP; never suppress the body's own backtracking.

## Proof (`SCRIP_IDX_TRACE=1`, default OFF)

```
color(apple,red). color(banana,yellow). color(grape,purple). color(lime,green).
?- color(grape,X)     → [IDX] CP-ELIDED clause=2/4  → purple
?- color(banana,Y)    → [IDX] CP-ELIDED clause=1/4  → yellow
?- color(cherry,_)    → (no IDX line) zero candidates → fails fast

p(a,1). p(a,2). p(b,3). p(a,4). p(c,5).
?- p(a,V) backtrack   → NO elision (3 candidates) → enumerates 1,2,4
?- p(b,W)             → [IDX] CP-ELIDED clause=... → 3
```

Selective firing confirms both the elision and the safety gate.

## Gates (all byte-identical to parent `e9f09fdc`, ZERO regressions)

| Gate | Result |
|---|---|
| GATE-1 smoke | 5/5 ✅ |
| GATE-2 crosscheck | 132/0 (5 ORACLE_MISS) ✅ |
| GATE-3 rung m2 | 104/107 ✅ |
| GATE-SWI plunit | 57/57 (100%) ✅ |
| FACT grep | 0 / 12 ✅ |
| sibling smokes | icon 5/5, raku 5/5, snobol4 13/13 ✅ |

## NEXT — Phase B2 (pairs WAM-CP-8 with WAM-CP-6 LCO)

The benchmark `count(0). count(N):-N>0,N1 is N-1,count(N1).` to `1e6` is still
the target. With first-arg indexing, a call `count(5)` against those two clauses
now filters to clause 2 only (clause 1's key is `INT 0`, clause 2's first arg is
a var = wildcard — note both are candidates when the arg is a nonzero int unless
clause 1 is `INT 0` specifically, which it is, so `count(5)` → only clause 2).
That makes the recursive call leave `g_pl_bfr` unchanged → LCO gate (2) passes.

The missing piece: the current det-commit path uses `bb_body_single_solution`,
which excludes ALL `BB_PL_CALL` — including the tail recursion B2 wants to
flatten. B2 must, when the index proves a unique clause whose body is
tail-CALL-only (the B1 `bb_body_cp_free_except_tail` shape), dispatch via the
**B1 redirect sentinel** (`g_pl_tail_redirect_cfg`/`_entry`, frame-reuse)
INSTEAD of `bb_exec_once`-and-return. Extend the gate; reuse the B1 mechanism —
do not invent a new path. See `doc/WAM-CP-6-STEP-B-DESIGN-2026-05-29-OPUS.md`.
