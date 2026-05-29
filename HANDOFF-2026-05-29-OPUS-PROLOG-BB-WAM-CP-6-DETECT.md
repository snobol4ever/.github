# HANDOFF — 2026-05-29 Opus 4.7 — Prolog BB WAM-CP-6 Step A LCO-DETECT

**Step closed:** WAM-CP-6 Step A — LCO-eligibility DETECT (audit, no semantic change).

**one4all commit:** `860d1163` (rebased onto `8d3a8cdf` Raku-BB-1c).
**.github commit:** this commit.

## What landed
24-line instrumentation in `src/lower/bb_exec.c` BB_PL_CALL fresh-call success path
detecting the SWIPL `I_DEPART` (Last-Call Optimization) two-condition eligibility:

1. **Tail position:** `bb->γ == NULL` — the AG/four-port lowering of clause bodies
   already initializes `succ = NULL` (`lower_pl.c:596`) for the rightmost statement,
   meaning "clause exit / success". When the BB_PL_CALL node has `γ == NULL`, the
   call IS the last goal of the body. Free signal, no compiler change needed.

2. **Determinacy:** `g_pl_bfr` unchanged across the call AND
   `!bb_body_has_live_choice(_bcfg)`. Together: no choice point opened by the callee
   survives, so resume is impossible — the call yields exactly one solution and
   never has to be re-entered.

When both hold, the call is the LCO target.

Trace gated on `SCRIP_LCO_TRACE=1` env var (default OFF). Control flow unchanged.

## Architectural compass: SWIPL study (re-read)
The dependency graph in `doc/SWIPL-STUDY-2026-05-28-OPUS.md` predicts the layering:

```
#4 choice-point stack (parent-linked records)   ← landed (WAM-CP-1..5)
   ├── makes CUT trivial                         ← landed (WAM-CP-4)
   ├── prerequisite for #6 LCO                   ← in progress (this step)
   └── this is what CAT-A-3's r12 buffer is groping toward
#7 JIT indexing (needs #1 keys + #4 to elide CPs)  ← required for #6 to be effective
```

Step A confirms empirically that we sit on top of #4 cleanly. **The trace also
reveals exactly what the study warned about:** WAM-CP-8 (first-arg indexing) is
a precondition for LCO to fire on the common case (tail-recursive multi-clause
predicates) because each multi-clause call currently pushes a BB_CHOICE CP that
the LCO check correctly identifies as "callee not deterministic from caller's
perspective."

## Empirical results

### Singleton-clause chain (LCO ideal target)
```prolog
hello(X) :- write(X), nl.
greet :- hello(hi).
main :- greet.
```
Trace:
```
hi
[LCO] hello/1 tail=1 det=1 eligible=1 bfr_before=(nil) bfr_after=(nil)
[LCO] greet/0  tail=1 det=1 eligible=1 bfr_before=(nil) bfr_after=(nil)
```
**Both calls eligible — these are the LCO targets in this session's state.**

### Multi-clause tail-recursive with cut on base case (NOT eligible)
```prolog
count(0) :- !.
count(N) :- N > 0, N1 is N - 1, count(N1).
main :- count(5), write(done), nl.
```
Trace (excerpted):
```
[LCO] count/1 tail=1 det=1 eligible=1 bfr_before=0x...a90 bfr_after=0x...a90  ← base case
[LCO] count/1 tail=1 det=0 eligible=0 bfr_before=0x...310 bfr_after=0x...a90  ← recursive
[LCO] count/1 tail=1 det=0 eligible=0 ...                                      ← recursive
[LCO] count/1 tail=1 det=0 eligible=0 ...                                      ← recursive
[LCO] count/1 tail=1 det=0 eligible=0 ...                                      ← recursive
[LCO] count/1 tail=0 det=0 eligible=0 bfr_before=(nil) bfr_after=0x...a90      ← top
done
```
Only the innermost (base-case-after-cut) is `det=1`. The recursive calls show
`tail=1 det=0` because the clause-selection CHOICE pushed a CP on each call that
hadn't been torn down by the time the call returned. **The cut in `count(0):-!`
truncates AFTER the call returns, not before.** This is the WAM-CP-8 precondition.

### Multi-clause without cut (NOT eligible)
```prolog
count(0).
count(N) :- N > 0, N1 is N - 1, count(N1).
```
Every call shows `tail=1 det=0` — same reason, no cut to even rescue the base case.

## Gates (all byte-identical to `5bf88205` baseline)
| Gate | Result |
|------|--------|
| GATE-1 prolog smoke | 5/5 ✅ |
| GATE-2 3-mode crosscheck | 132/0 (5 ORACLE_MISS) ✅ |
| GATE-3 mode-2 (`--interp`) | 104/107 ✅ |
| GATE-4 mode-4 minimal | 4/4 ✅ |
| GATE-SWI mode-2 | 57/57 (100%) ✅ |
| GATE-SWI mode-3 | 57/57 (100%) ✅ |
| FACT RULE | 0 ✅ |
| smoke icon | 5/5 ✅ |
| smoke raku | 5/5 ✅ |
| smoke snobol4 | 13/13 ✅ |

ZERO regressions.

## Detection-logic correctness audit
The two conditions match SWIPL `I_DEPART` semantics:
- SWIPL's tail position: emitted at clause compile time when the goal is last in
  the body. We get the same fact from `bb->γ == NULL` post-AG-lowering, no
  compile-time annotation needed.
- SWIPL's determinacy: `BFR <= FR` (no choice point younger than this frame).
  Our equivalent is `g_pl_bfr` pointer-equality against the entry snapshot —
  guaranteed equal iff no `pl_cp_push` net-uncanceled since entry. The second
  conjunct `!bb_body_has_live_choice(_bcfg)` catches the case where the callee
  pushed AND popped CPs during execution but left an open one inside its body
  (e.g. mid-clause CHOICE with state>0 awaiting resume).

The conjunction is **necessary AND sufficient** for LCO — a Prolog identity:
*if and only if no resume is possible AND the caller will exit on success, the
caller's frame is dead and can be reused.*

## NEXT
This step continues into:

**Step B (next session, ~1-2 sessions):** convert `eligible=1` cases to actual
frame-reuse. The semantic transform:
- Before: `bb_exec_once(_bcfg)` recursion + `calloc(callee_env)` + `malloc(PlCallSt)`
  push, with the caller's frame still on the C stack.
- After (eligible): no `calloc(callee_env)` (reuse `g_pl_env` *if safe* — arg
  unification through the trail handles aliasing, but careful: the caller's
  cells must still be live for the trail's reference chain), no `PlCallSt` push
  (no resume needed by definition), and crucially — **no recursive `bb_exec_once`
  call.** Instead, the dispatch loop in `bb_exec_once` becomes a trampoline: a
  successful LCO-eligible PL_CALL returns a sentinel that the outer driver
  recognizes as "restart with `_bcfg` as the new graph." The C stack stays flat.

Two design questions for Step B:
1. **Where does the trampoline live?** Cleanest: a new `BB_PL_TAIL_CALL` node
   emitted by `lower_pl_clause_body` when the rightmost statement is a
   `BB_PL_CALL`; the executor returns to the bb_exec_once driver with an
   explicit "switch graph" descriptor. Mode-2 only; mode-4 follows.
2. **Arg-binding aliasing:** the recursive call uses the caller env's TERM_REF
   chains to propagate bindings. With LCO, the caller env disappears. SWIPL
   handles this with `copyFrameArguments(lTop, FR, arity)` — copying the
   trail-bound args into the new frame slot before the old frame goes away.
   Our equivalent: `term_deref` every callee arg into a freshly-allocated
   slot vector that lives only as long as the trail mark covers it. Trickier
   than SWIPL because our Term boxes are GC-allocated individually (SWIPL
   study idea #1 — a long-term win we don't have yet).

**Step C (longer arc):** WAM-CP-8 first-arg indexing. With indexing, multi-clause
calls like `count(N)` against `count(0). count(N):-...` would dispatch directly
to clause 2 with no CP, making the recursive call `eligible=1` and unlocking
the full benchmark target (`count/1` to 1e6 in O(1) stack).

## Files touched
- `one4all/src/lower/bb_exec.c` (+24 lines)
- `.github/PLAN.md` (Prolog BB row updated)
- `.github/GOAL-PROLOG-BB.md` (State-at-HEAD prepended; rung WAM-CP-6 marked partial)
- `.github/HANDOFF-2026-05-29-OPUS-PROLOG-BB-WAM-CP-6-DETECT.md` (this file)
