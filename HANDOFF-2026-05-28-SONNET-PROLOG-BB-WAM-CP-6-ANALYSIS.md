# HANDOFF 2026-05-28 — Sonnet 4.6 — PROLOG-BB: WAM-CP-6 LCO analysis (no commit)

**Goal:** WAM-CP-6 Last-Call Optimization. Gate: `count(0). count(N):-N>0,N1 is N-1,count(N1).`
to 1e6 runs in O(1) stack.

## What was attempted

Three approaches tried, all reverted. Tree is clean at `88bacd2a`.

### Approach 1: naive env reuse
Added `is_last` / `entry_bfr` to `bb_pl_call_state_t`. In `BB_PL_CALL` fresh-call, when
`is_last && g_pl_bfr == entry_bfr`: allocate callee_env, bind args, call `bb_exec_once`,
free env, return. **Problem:** `bb_exec_once` still recurses — C stack grows O(N).

### Approach 2: trampoline via global flag
Added `g_lco_pending / g_lco_cfg / g_lco_env` globals. `BB_PL_CALL` LCO path sets
`g_lco_pending=1` and returns `bb->γ` without calling `bb_exec_once`. Added a
`goto lco_restart` loop inside `bb_exec_once` that catches the flag and re-enters on
the callee graph.

**Problem:** The trampoline catches the LCO signal at the OUTER `bb_exec_once` level
(e.g. `main`'s executor). But `count(N)` is called via a non-LCO `bb_exec_once` from
within `BB_PL_CALL` (because `count(N)` is not the last goal of `main` — `write(ok)`
follows). So `count(N)` runs in its OWN `bb_exec_once`. `count(N1)` inside that fires
LCO → signals the trampoline in `count(N)`'s `bb_exec_once` → that one loops correctly.
But `count(N)` is called from `count(N-1)` which is called from `count(N-2)` etc. —
we save one recursive C frame per call but the chain is still N-deep.

count(3) passed (small enough), count(100) segfaulted.

### The fundamental problem

In a recursive interpreter, **every Prolog call is a C call**. LCO eliminates the
Prolog environment allocation, but does NOT eliminate the C stack frame unless the
interpreter's call path is itself tail-recursive at the C level.

The gate requires O(1) **C stack** depth. That requires either:

1. **setjmp/longjmp unwind** before the tail call re-entry — unwind the entire C stack
   to the top-level executor, then re-enter. This is how Prolog's WAM does it: the C
   code for `execute/1` is a loop, never recurses.

2. **Trampolining at bb_exec_once level** — convert `bb_exec_once` into a loop that
   never calls itself recursively. Every `BB_PL_CALL` returns a "call descriptor" instead
   of calling `bb_exec_once`; the top-level loop drives the call stack itself.

3. **Continuation-passing style** — rewrite the interpreter so `BB_PL_CALL` passes a
   continuation rather than returning to a caller.

## Recommended approach for next session: option 2 (trampoline at bb_exec_once)

Convert `BB_PL_CALL` in `bb_exec.c` to NEVER call `bb_exec_once` recursively. Instead:

```c
/* bb_call_request: pending call pushed by BB_PL_CALL instead of recursive bb_exec_once. */
typedef struct bb_call_req {
    BB_graph_t *cfg;           /* callee graph to run */
    Term      **callee_env;    /* pre-built arg env */
    Term      **saved_env;     /* caller's env to restore after */
    int         trail_mark;    /* for unwinding on failure */
    bb_node_state_t *caller_snap; /* caller's view of cfg (for recursive calls) */
    BB_t       *return_γ;      /* success continuation in caller */
    BB_t       *return_ω;      /* failure continuation in caller */
    struct bb_call_req *parent; /* call stack */
} bb_call_req_t;
```

`bb_exec_once` becomes a loop: when `BB_PL_CALL` pushes a `bb_call_req_t`, the loop
pops it and starts executing the callee. On callee success, the loop restores state
and continues from `return_γ`. On failure, from `return_ω`.

This is a significant refactor of `bb_exec_once` and `BB_PL_CALL`. The LCO optimization
then falls out naturally: if `is_last && no CP since entry`, push the call request but
DON'T push a new frame — reuse the existing one. The "call stack" shrinks.

## Smaller alternative: ulimit -s + larger stack

As a stopgap, the gate can pass with `ulimit -s unlimited` for now, and the real LCO
can land later. But the GOAL file requires O(1) stack.

## Current state: clean at `88bacd2a`

All gates hold (same as FACT cleanup Steps 2+3 commit). No code changes landed.

GATE-1 smoke: 5/5. GATE-2: 132/0. GATE-3 mode-2: 96/107. GATE-4: 4/4. FACT: 0.

## NEXT session candidates

1. **WAM-CP-6 (LCO) — trampoline refactor** as described above. Significant but principled.
2. **WAM-CP-13** — mode-4 catch/throw + longjmp-free unwind. Simpler scope.
3. **WAM-CP-9 Steps B–D** — committed-ITE + disjunction-cut.
