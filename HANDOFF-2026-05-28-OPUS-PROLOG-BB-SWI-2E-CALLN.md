# HANDOFF-2026-05-28-OPUS-PROLOG-BB-SWI-2E-CALLN

**Author:** Claude Opus 4.7
**Date:** 2026-05-28
**Predecessor HEAD:** `d805b0fe` (SWI-2d call/1)
**This HEAD:** `3b4a4ff2` (SWI-2e call/N for N>1)

---

## Summary

Extended SWI-2d to handle `call/N` for N>1 (partial application with appended
arguments). One mechanical fold: BB_PL_CALL's call-meta intercept now accepts
any `carity >= 1` instead of `carity == 1` only, and for `carity > 1` builds
a Term* array of extras from `zc->args[1..carity-1]` and dispatches via a
new public wrapper `pl_call_term_n` that reconstructs the goal compound and
delegates to `pl_invoke_var_goal`.

`rung33_bridge_callN`: **1/5 → 2/5** (01 stays PASS; 03 is the new PASS — the
canonical call/2 atom+extra-arg case `call(write, hello)`).

---

## Diagnosis

PLAN.md noted: *"call/N for N>1 (RECOMMENDED — mechanical extension of SWI-2d,
likely closes `rung33_bridge_callN` 1/5→5/5)."*

The "5/5" claim was optimistic. Actual outcome **2/5**, because tests 02/04/05
hit a *different* pre-existing bug that exists under SWI-2d already (confirmed
by re-baselining at `d805b0fe`: 01 PASS, 02/03/04/05 segfault). The SWI-2e
fold itself works cleanly for the case it targets — appended args to a
builtin goal.

### The other bug (separate scope)

`call(G)` where G is bound to a *user-defined* compound goal (e.g.
`G = foo(5)`) dispatches via `pl_invoke_var_goal` → `pl_term_to_synth_expr`
→ `interp_exec_pl_builtin` → user-call branch at `pl_runtime.c:894-900`.
That branch is **stubbed** at line 895:

```c
DESCR_t rd = FAILDESCR; g_pl_env = sv; fprintf(stderr, "[NO-AST] interp_eval stub\n");
```

It prints the `[NO-AST]` message, returns FAILDESCR, and the caller then
segfaults somewhere downstream (likely a NULL deref of an env slot that was
expected to be bound by the never-executed user goal). This is independent
of SWI-2e and was the actual blocker for tests 02/04/05.

Test 02 reproducer (no call/N reconstruction involved):
```prolog
:- initialization(main).
main :- G = foo(5), call(G), write(done), nl.
foo(_).
```
Output: `[NO-AST] interp_eval stub\nSegmentation fault`.

Test 03 PASSes because its reconstructed goal is `write(hello)` — a builtin,
not a user predicate, so it never touches line 895.

The fix for 02/04/05 lives in **making `interp_exec_pl_builtin`'s user-call
branch actually execute the user predicate** — either by routing it back
through the BB graph for that predicate (preferred, keeps the runtime
single-truth) or by wiring up a real interpreter walk. That's its own fold;
flag is "PL-RT-USER-FROM-SYNTH".

---

## Changes

### `src/runtime/interp/pl_runtime.c` (+36)

New public function `pl_call_term_n(Term *gt, int n_extra, Term **extras)`.
Mirrors the call/N arm of `interp_exec_pl_builtin` (~line 1050): derefs goal,
rejects VAR/INT/FLOAT, extracts functor+args from atom (carity_base=0) or
compound (carity_base=k), allocates `Term**` of size `carity_base + n_extra`,
copies base args (dereffed) and extras (dereffed), calls `term_new_compound`,
dispatches via `pl_invoke_var_goal`. `n_extra <= 0` short-circuits to plain
`pl_invoke_var_goal` (handles the "called with extras count zero" edge case).

### `src/runtime/interp/pl_runtime.h` (+6)

Declares `pl_call_term_n`.

### `src/lower/bb_exec.c` (+19 net, -8 old)

`BB_PL_CALL` call-meta intercept widened:
```c
if (carity >= 1 && strcmp(callee, "call") == 0) {
    ...
    Term *gt = pl_node_to_term(zc->args[0]); gt = term_deref(gt);
    if (carity == 1) {
        ok = pl_call_term(gt);
    } else {
        int n_extra = carity - 1;
        Term **extras = malloc(n_extra * sizeof(Term*));
        for (int i = 0; i < n_extra; i++)
            extras[i] = term_deref(pl_node_to_term(zc->args[i + 1]));
        ok = pl_call_term_n(gt, n_extra, extras);
        free(extras);
    }
    ...
}
```

Comment updated to reference SWI-2d/2e and explain the dispatch split.

---

## Gates

All gates byte-identical to `d805b0fe` except rung33:

| Gate | Value | Δ from d805b0fe |
|---|---|---|
| Smoke Prolog | 5/5 | — |
| G2 crosscheck | 132/0 (5 ORACLE_MISS) | — |
| G3 mode-2 (`--run`) rung_suite | 104/107 | — |
| GATE-SWI plunit | 53/57 (92%) | — |
| BB-honest | 128/0 | — |
| FACT | 0 violations | — |
| Smoke Icon | 5/5 | — |
| Raku smoke | 16 PASS / 1 FAIL | — |
| **rung33_bridge_callN** | **2/5** | **+1 ✅** |

FACT clean: my changes touch only mode-2 interpreter paths
(`pl_runtime.c/.h`, `bb_exec.c` BB_PL_CALL handler). No emitter
or template files touched. Mode-3/4 byte output unchanged.

---

## Open / next options

1. **PL-RT-USER-FROM-SYNTH** (closes rung33 02/04/05 — RECOMMENDED next).
   Make `interp_exec_pl_builtin`'s user-call branch (`pl_runtime.c:886-901`)
   actually execute the user predicate. Currently stubs at line 895. The
   cleanest path is probably: synthesize a `BB_PL_CALL`-equivalent dispatch
   via `pl_bb_lookup` + `bb_exec_once` on the predicate's BB graph, mirroring
   what BB_PL_CALL itself does after the call-meta intercept. This closes
   `call(G)` and `call(G, extras...)` for user predicates uniformly.

2. **SWI-5 EMPTY verdict** — investigate the 4 SWI plunit MISSes
   (catch / variant / float_compare / max_integer_size).

3. **PL-RT-ASSERTZ** — runtime assert/retract for dynamic predicates.

4. **WAM-CP-13** — mode-4 parity for catch/throw + deep backtracking.

5. **WAM-CP-6 LCO** — needs `bb_exec_once` non-recursive refactor
   (call-descriptor stack); deferred per `HANDOFF-2026-05-28-SONNET-PROLOG-BB-WAM-CP-6-ANALYSIS.md`.

---

## Files touched

```
M  src/lower/bb_exec.c              +27 -8
M  src/runtime/interp/pl_runtime.c  +36
M  src/runtime/interp/pl_runtime.h  +6
A  HANDOFF-2026-05-28-OPUS-PROLOG-BB-SWI-2E-CALLN.md
```

Commit: `3b4a4ff2` — "SWI-2e: call/N mode-2 fallback for N>1 (appended-args reconstruction)"
