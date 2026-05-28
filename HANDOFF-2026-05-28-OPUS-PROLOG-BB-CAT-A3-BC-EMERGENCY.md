# EMERGENCY HANDOFF 2026-05-28 — Opus 4.7 — PROLOG-BB: CAT-A-3 (b) Steps B–C (IN PROGRESS, NOT COMMITTED)

**Goal:** GOAL-PROLOG-BB.md — CAT-A-3 Steps B–C (mode-4 backtracking). The largest
single mode-4 unlock (+15–25 corpus). Design: HANDOFF-2026-05-27-OPUS-PROLOG-BB-CAT-A3-STEPA.md.

**Status: WORK IN PROGRESS. NOTHING COMMITTED. HEAD still `aeda3170`. Tree dirty (8 files).
Build is GREEN. Do NOT commit as-is — full mode-4 corpus currently regressed to 18 (baseline 28)
because of ONE timing bug (below). Fixing that bug should restore baseline AND add the new wins.**

## The core mechanism WORKS (proven mid-session)

At an intermediate state (always-r12, before the det/nondet split), **rung02 passed
`brown/jones/smith` and rung08 recursion passed `8/6` in mode-4** — full backtracking. The
design is sound. Two real bugs were found and fixed via runtime trace-debugging:

1. **`_redo` fall-through.** First attempt emitted `.Lplpred_<n>_<a>_redo: jmp bβ` BETWEEN the
   fresh entry label and the body, so the FRESH `call` fell through `_redo` into the choice
   dispatch, SKIPPING the prologue (`rt_pl_trail_mark` + cursor=0). The choice entry mark stayed
   0, so the first redo's `rt_pl_trail_unwind` unwound to 0 and destroyed the call-site arg-bind
   alias (X→callee_var) → solutions 2+ printed `_`. FIX: emit the `_redo` trampoline AFTER the
   callee body+epilogue (so fresh entry falls straight into the choice prologue). DONE — in
   sm_bb_switch.cpp PL_ENTRY arm.
2. **Duplicate-symbol collision.** Call-site control labels were derived from the callee name
   (`<blbl>_fresh_fail` etc.), so a predicate called from 2+ sites (recursion, multiple goals)
   produced duplicate symbols → assembler errors (rung05/06/08). FIX: per-call-site unique id
   `csid = g_flat_node_id++` → `.Lplcs<csid>_fresh_fail/_redo_fail/_exhausted`. DONE.

## THE ONE BLOCKER BUG (fix this first next session)

`pl_bb_pred_is_resumable(callee, arity)` — added in pl_runtime.c — calls `pl_bb_entry_node`
which calls `pl_bb_lookup`. **At call-template emit time this returns NULL ("no entry")** for
EVERY predicate (confirmed by trace: `[RESUM p/1: no entry]`). So every call falls to the
`det` path. The det path cannot backtrack, so rung02 etc. regress; and a few segfault because
the unconditional `_redo` emission in PL_ENTRY interacts badly. This is an **emit-pass timing
issue**: the pred BB table is not live (or already freed) when the call site is walked.

### THE FIX (clean, ~6 lines): stash determinacy at LOWER time, not emit time

In `lower_pl.c` `lower_pl_new_Call` (line ~167) the pred table IS live. Add a `resumable` int
to `bb_pl_call_state_t` (BB.h line 294) and set it there:
```c
// BB.h
typedef struct { BB_t ** args; int nargs; const char * callee; int arity; void * cs; int resumable; } bb_pl_call_state_t;
// lower_pl.c lower_pl_new_Call, after zc->callee=fn; zc->arity=n;
zc->resumable = pl_bb_pred_is_resumable(fn, n);   // table live here
```
Then in `bb_pl_call.cpp` replace `int resumable = pl_bb_pred_is_resumable(callee, arity);`
with `int resumable = zc ? zc->resumable : 0;`. There is a SECOND call-state builder in
lower_pl.c at line ~461 (the N-ary path) — set `zc->resumable` there too. Verify
`pl_bb_pred_is_resumable` itself is correct: it reads `en->t==BB_CHOICE` and casts
`en->ival` to `bb_pl_choice_state_t*`, checks `nbodies>1`. That logic is fine; only the
CALL-TIME lookup is too late.

After this fix: deterministic callees (single-clause, leaf) take the cheap old path (env_pop,
β→ω, no r12 — keeps r12 balanced); multi-clause callees take the resumable r12 path.

## SECOND problem (after the blocker): resumable γ-leak

A resumable call that SUCCEEDS but is never backtracked (e.g. `p(X), write(X), nl.` with no
`fail` — the m4-choice minimal test) leaves r12 = its buffer (never restored) and the pool slot
un-freed. rung02/05/06/08 all have `, fail` driving exhaustion (clean), so they work; m4-choice
does not. Options: (a) have the owning clause/SEQ free the buffer + restore r12 when it completes
deterministically; (b) restrict scope to fail-driven exhaustion and document it (m4-choice would
need exclusion or a determinacy-of-USE analysis). Recommend (a) but it needs the SEQ/clause
driver to know it owns a live buffer. GATE-4 m4-choice MUST pass before commit.

## What's implemented (all dirty, uncommitted)

### Runtime substrate (rt.c + pl_runtime.h) — SOUND, keep
- `rt_pl_resume_alloc()` / `rt_pl_resume_free(void*)` — bounded 64-deep pool of **5-qword**
  buffers (layout: [0]=state [8]=cursor [16]=trail_mark [24]=callee_env [32]=saved caller r12).
  Alloc returns zeroed buffer in rax; free pops top.
- `rt_pl_env_current()` → returns g_pl_env (the callee env, stashed by the call site for the
  redo path's non-freeing reinstall).
- `pl_bb_env_install` (from Step A) used for non-freeing env swaps.

### pl_runtime.c — `pl_bb_pred_is_resumable(name,arity)` — logic OK, called too late (see fix)

### bb_pl_choice.cpp — REWRITTEN to r12 cursor dispatcher — CORRECT
α: `rt_pl_trail_mark` → `[r12+16]`; `[r12+8]=0`; fall into dispatch. dispatch: read `[r12+8]`,
`cmp N / jge exhausted`, cursor-cascade to `c<i>_pre`. `c0_pre`: `inc [r12+8]` → body0.
`c<i>_pre`: unwind to `[r12+16]`, `inc [r12+8]` → body_i. β: `jmp dispatch`. exhausted: unwind →
ω_in. This is the WAM-style cursor. Single-emit preserved.

### emit_bb.c `flat_drive_pl_choice` — clause body ω now wires to `lbl_β` (dispatch re-entry)
instead of the static next-clause `pre` cascade. This is the resumable inversion. CORRECT.

### sm_bb_switch.cpp PL_ENTRY — emits `.Lplpred_<n>_<a>_redo:` trampoline AFTER body+epilogue,
jumping to `bβ` (the body's β = choice dispatch re-entry). CORRECT (fixed the fall-through).

### bb_pl_call.cpp — det/nondet SPLIT. Det path = verbatim old template (works, m4-call passes).
Resumable path: Phase 0 alloc buffer, save caller r12 into `[r12+32]`, set r12; Phases 1–3 build
args/env/bind (stashes callee env into `[r12+24]` via rt_pl_env_current); Phase 4 `call blbl`;
Phase 5 test last_ok → γ (non-freeing install caller env, keep buffer) / fresh_fail; β reinstalls
callee env, `call rlbl` (_redo), test → γ / redo_fail; fresh_fail+exhausted free callee env +
buffer, restore r12 from `[r12+32]`, → ω. Per-site labels `.Lplcs<csid>_*`.

## Gate state to restore/verify before commit (baseline at HEAD aeda3170)
GATE-1 5/5 · GATE-2 132/0 · GATE-3 mode-2 91/107 · GATE-4 4/4 · full mode-4 corpus **28** ·
FACT RULE 0 · sibling smokes icon 5/5 snocone 5/5 raku 5/5 rebus 4/4 snobol4 13/13.
Target after fix: GATE-4 4/4 (incl m4-choice), full mode-4 **≥ 28 + rung02 + rung08 + rung05/06**
(expected mid-30s to ~45). GATE-1/2/3 unchanged (mode-2 untouched). FACT RULE MUST stay 0 —
all new bytes are template-emitted (verify `grep -rnE 'seg_byte\(SEG_CODE|SL_B\(|sl_emit_one|emit_standard_blob' src/` outside *_templates/ + emit_core.c == 0).

## Verify sequence next session
1. Apply the `zc->resumable` lower-time fix (BB.h + lower_pl.c ×2 + bb_pl_call.cpp 1 line).
2. `make libscrip_rt && bash scripts/build_scrip.sh`.
3. `bash scripts/test_prolog_mode4_rung.sh` → expect 4/4 (m4-choice is the canary for the γ-leak).
4. rung02/05/06/08 via run_prolog_via_x86_backend.sh → expect PASS.
5. If m4-choice still fails → the γ-leak (second problem); fix before proceeding.
6. Full mode-4 corpus loop; then GATE-1/2/3; then sibling smokes; then FACT RULE grep.
7. Only then commit B–C together (bisectable). Update GOAL watermark + PLAN.md.

## Files dirty (uncommitted)
src/runtime/rt/rt.c · src/runtime/interp/pl_runtime.c · src/runtime/interp/pl_runtime.h ·
src/emitter/BB_templates/bb_pl_call.cpp · src/emitter/BB_templates/bb_pl_choice.cpp ·
src/emitter/SM_templates/sm_bb_switch.cpp · src/emitter/emit_bb.c · src/emitter/emit_bb.h
