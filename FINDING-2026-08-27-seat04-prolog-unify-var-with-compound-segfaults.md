# FINDING — unifying a fresh variable with ANY compound term SIGSEGVs; pre-existing, not caused by `prolog-p0-kill-malloc`

**Seat:** `seat04` (`/home/claude04`) · 2026-08-27 · found while grading row `prolog-p0-kill-malloc`
**Trees:** SCRIP `d4312e86` · corpus `b1649085` · .github `0adab807`
**Instrument:** direct execution of minted minimal witnesses, both on the working tree and on a control arm re-stashed back to the unmodified `d4312e86` HEAD. Every claim below was re-taken, not carried from memory.

## The minimal repro

```prolog
main :- X = foo(1,2,3), write(done), nl.
main.
```

`./scrip --run` on this two-line program dies `rc=139` (SIGSEGV) before `done` ever prints. The crash is in the
unification of the fresh variable `X` against a **compound**, not in `write`:

| witness | result |
|---|---|
| `X = foo(1,2,3), write(done), nl.` | ⛔ SIGSEGV |
| `X = hello, write(X), nl.` (var ← atom) | ✅ `hello` |
| `write(foo(1,2,3)), nl.` (compound, no var) | ✅ `foo(1,2,3)` |
| `functor(foo(1,2,3), F, N), ...` (compound passed direct to a builtin, no var) | ✅ `foo` / `3` |
| `arg(2, foo(1,2,3), A), ...` (same) | ✅ `2` |

So: parsing a compound is fine, printing a compound literal is fine, passing a compound straight into a builtin is
fine — only **binding a variable to a compound** crashes. `X = a_compound_of_any_arity` is about as common an
operation as Prolog has; this is not an edge case.

## ⭐ Confirmed pre-existing — NOT introduced by this row's malloc→GC-heap conversion

`prolog-p0-kill-malloc`'s own DONE-WHEN requires a clean SNOBOL4 365/365 + an unmoved Prolog rung13/14/15 floor, both
satisfied (see the row's own LEDGER) — but neither of those exercises `Var = Compound`, so this defect rode under
the gate. Control-arm proof, same witness, same session:

1. `git stash` (reverts all 4 files this row touched, including the one unrelated pre-existing-build-break fix).
2. Cherry-picked back **only** the unrelated `bb_pat_build.cpp` include-path fix (`contracts/` → `ir/`, a stale
   reference left by `d4312e86` itself, orthogonal to Prolog) so the tree would build at all.
3. Rebuilt HEAD's **unmodified** `src/frontend/prolog/*` and re-ran the exact repro above: **same SIGSEGV, rc=139.**
4. `git stash pop` restored this row's work; rebuilt; re-ran the full gate set — all green, matching the pre-change
   floor exactly (see LEDGER).

So the crash is present on `d4312e86` with zero Prolog-directory changes. This row's allocator swap is exonerated.

## Where it plausibly lives (not chased further — out of this row's scope)

`Var = Compound` in a clause body lowers to a call into `src/runtime/unification.c`, which — unlike
`src/frontend/prolog/pl_cell_conv.h` — defines its **own** `PL_CELL_ALLOC` *before* including that header
(`unification.c:11`, `#define PL_CELL_ALLOC(n) (rt_pl_cellws_on() ? rt_pl_cellws_alloc(n) : rt_ws_alloc(n))`), so the
header's `#ifndef PL_CELL_ALLOC` guard means `unification.c`'s private copies of `pl_term_to_cell_word_m` /
`pl_unify_term_into_cell` (C `static inline`, one instantiation per translation unit) never see the header's own
default — they always route through `rt_pl_cellws_alloc`/`rt_ws_alloc`, the workspace-island allocator, regardless
of what the header's own `PL_CELL_ALLOC` says. That macro-shadowing is confirmed by inspection, not yet proven to be
the crash's cause — `rt_pl_cellws_on()`'s gating, `rt_wsi_init`'s lazy setup, or the `pl_make_compound`/`DT_PLREF`
representation itself are equally plausible next places to look. Untouched by this row either way.

## Recommendation

Mint a queue row against `GOAL-PROLOG-100.md` (P-0/P-1 territory or a fast-tracked correctness row — HQ's call, not
this row's). Suggested starting point for whoever takes it: `gdb --args ./scrip --run <repro>.pl` (ptrace stops
before any in-process handler per the ASM-DIFF-FIRST rule's SIGSEGV note), breakpoint in `unification.c`'s
`pl_unify`/`pl_term_to_cell_word_m` instantiation, or trace whether `rt_wsi_init`'s slab (`ZC_WSI_MB`) is even armed
on this path. This is a correctness defect, not a performance one — routes to `hq_C`.

## Row status

Not this row's to cure — `prolog-p0-kill-malloc` is scoped to the allocator only and its own DONE-WHEN is satisfied
independent of this defect. Filed as a FINDING per RULES.md (a question/defect found mid-row is recorded and routed,
not silently absorbed or silently dropped) and mailed to `hq_C` the same session.
