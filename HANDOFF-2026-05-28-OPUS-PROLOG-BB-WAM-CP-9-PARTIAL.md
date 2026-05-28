# HANDOFF — 2026-05-28 Opus 4.7 — PROLOG-BB WAM-CP-9 partial

## Watermark

- one4all HEAD: `549c7fca` (atop upstream `b84153c3` RENAME)
- Gates: **G1=5/5, G2=132/0, G3=91/107, G4=4/4, mode-4 corpus=54/107 (+1 rung07_cut_cut), FACT=0**
- No regressions in any gate.

## What changed

**Goal:** WAM-CP-9 (committed-ITE + cut=truncate). Partially landed — the clause-side cut path.

### Substrate

`src/runtime/interp/pl_runtime.h` — `pl_choice` gained two append-only fields:
- `int               saved_cut_flag;`    (offset +56)
- `struct pl_choice *saved_cut_barrier;` (offset +64)

Sizeof grows 56→72. Pre-existing offsets used by mode-4 templates (16 trail_mark, 24 env, 40
saved_args, 48 cursor) are untouched.

### Runtime helpers (KEEP side, no port logic)

`src/runtime/rt/rt.[ch]`:
- `void rt_pl_choice_cut_enter(void *cp)` — save outer `g_pl_cut_{flag,barrier}` into `cp`'s
  slots, set `g_pl_cut_barrier = cp->parent`, clear `g_pl_cut_flag`.
- `void rt_pl_choice_cut_exit(void *cp)` — restore outer state from `cp`. No truncate, no pop.
- `void rt_pl_choice_cut_unwind(void *cp)` — restore outer state from `cp`, then
  `pl_cp_truncate(cp->parent)` (pops `cp` itself and any nested CPs).
- `int  rt_pl_get_cut_flag(void)` — register-clean read of `g_pl_cut_flag` for template use
  (avoids GOTPCREL).

### Template changes

`src/emitter/BB_templates/bb_pl_choice.cpp` — restructured (only mode-4 TEXT path; macro/binary
paths unchanged):

```
α:  pl_cp_push → rax=cp → rt_pl_choice_cut_enter(cp) → fall into dispatch
dispatch: pl_cp_current → cursor → pre[cursor] → body[cursor]
body[i].γ → exit_γ
body[i].ω → β  (this is the shared β label)
exit_γ: rt_pl_get_cut_flag; if !=0 → cut_unwind_γ; else cut_exit + jmp γ_in
cut_unwind_γ: pl_cp_current → rt_pl_choice_cut_unwind → jmp γ_in
cut_unwind_ω: pl_cp_current → rt_pl_choice_cut_unwind → jmp ω_in
exhausted: cut_exit + trail_unwind + pl_cp_pop + jmp ω_in
β: rt_pl_get_cut_flag FIRST; if !=0 → cut_unwind_ω.
   Else pl_cp_current; if NULL → β_nosol(=jmp ω_in); else cut_enter + jmp dispatch.
β_nosol: jmp ω_in
```

`src/emitter/BB_templates/bb_pl_cut.cpp` — code unchanged (still `call rt_pl_cut_set; jmp γ`),
header comment expanded to document the new deferred-truncate contract with BB_CHOICE.

## Why deferred truncate (CUT sets flag, CHOICE truncates)

Mode-2 BB_CUT does both `pl_cp_truncate(g_pl_cut_barrier)` and `g_pl_cut_flag = 1`. It can do
this safely because mode-2 BB_CHOICE keeps `saved_cut/saved_barrier` on the **C stack** (function
locals) — those values survive after the heap CP is freed.

Mode-4 cannot: the BB_CHOICE template has no live stack frame across the α→γ→caller→β
round-trip. The saved-state values must live on the heap. They live in `cp` itself. But if CUT
eagerly truncates and frees `cp`, those slots are gone before BB_CHOICE's dispatch/exit_γ can
read them. So mode-4 CUT only sets the flag; CHOICE owns the truncate.

## Where the flag-check order matters

The shared `lbl_β` of a CHOICE receives two distinct flows:
1. Body[i].ω chains here on failure (including cut+fail).
2. Caller's BB_PL_CALL.β chains here on legitimate redo.

Both arrive with `g_pl_cut_flag` reflecting whatever happened in the body just exited (case 1)
or in the caller's state (case 2 — usually 0 since caller's own CHOICE consumed any cut). The
β handler MUST check the flag **before** `cut_enter` — `cut_enter` clears the flag and would
mask a body-fired cut. That ordering was the critical fix that flipped rung07 from
`yes\nyes` to `yes\nno`.

## NOT done — pickup for next session

### WAM-CP-9 Steps B–D (open)

- **Step B (committed-ITE node).** `(Cond -> Then ; Else)` currently lowers via ALT/IFTHEN
  chains. A dedicated stateful BB_IF-style node would commit on Cond's first success without
  threading through the flag mechanism. Mirror Icon's stateful `BB_IF` (`bb_exec.c:803`).

- **Step C (disjunction-cut).** `bb_pl_alt.cpp` (BB_PL_ALT, `(A ; B)`) uses the small
  `rt_pl_trail_mark_push/pop` stack — a totally separate mechanism from `pl_choice`. A `!`
  in the left branch of a disjunction does NOT truncate a disjunction CP today. Two paths:
  either migrate BB_PL_ALT to push `PL_CP_DISJ` records (and apply the same cut-scope nesting
  as BB_CHOICE), or fold disjunction into the Step B committed-ITE node.

- **Step D (retire `g_pl_cut_flag` global).** Use `pl_cp_current()` identity comparisons
  instead. Currently the flag is the only signal CHOICE has that body fired `!`.

### Edge cases I traced but didn't exercise

- Caller-driven β with our `cp` truncated by an outer cut → `pl_cp_current()` may return
  parent-of-our-old-cp (some unrelated CP) rather than NULL. β handler does `test rax, rax`
  → not zero → falls into `cut_enter` of someone else's cp. Could mis-fire. The NULL guard
  catches only the case where our cp was the bottom of the chain. If a corpus test surfaces
  this, β needs a stronger identity check (stamp comparison against a remembered value).

- `!` followed by more goals that succeed: exit_γ → cut_unwind_γ truncates our cp → caller's
  BB_PL_CALL.β reads `pl_cp_current()` which is now some unrelated parent. Today's BB_PL_CALL.β
  does `mov rdi, [rax+24]` (cp->env) and calls `pl_bb_env_install`, then `call redo_lbl`,
  then on success reads `[rax+40]` (saved_args). If rax is now a non-CHOICE CP, this misreads.
  No corpus test currently exercises a successful cut+more_goals followed by external redo, so
  this is latent.

### Other open items unchanged

- rung15_then_reassert (PL-RT-ASSERTZ runtime materialization of clauses).
- rung28 catch/throw (WAM-CP-10 — would reuse the pl_choice-extension pattern).
- CAT-D mode-4 emit gaps (findall, retract, abolish, numbervars, writeq, char_type, etc.).
- PL-LOWER-REVAMP β-heuristic replacement (recommend after WAM-CP-6/9 land).

## Suggested next step

Three viable directions, Lon's pick:

1. **Finish WAM-CP-9 Step C (disjunction-cut).** Smallest scope — migrate BB_PL_ALT to push
   `PL_CP_DISJ` and apply the cut-scope nesting. Would let any future `!`-in-`(A;B)` test pass.

2. **WAM-CP-6 (LCO).** Per PLAN.md, the originally-next step. Bigger lift — needs determinism
   detection. Gate: `count(N):-N>0,N1 is N-1,count(N1). count(0).` to 1e6 in O(1) stack.

3. **WAM-CP-10 (catch/throw).** Closes rung28 (5 OPENs in mode-2, 5 OPENs in mode-4). Reuses
   the pl_choice-extension pattern with a parallel `g_pl_catch` chain. High user-visible payoff.

My recommendation: **WAM-CP-10**, because (a) it converts directly into rung passes (concrete
gate), (b) the substrate pattern is freshly proven, and (c) exception handling unblocks a class
of programs that touches many downstream Prolog features.
