# HANDOFF — PLG-9c: Prolog mode-3/mode-4 arith `is/2` into a logic-variable slot

**Author:** Claude Opus 4.8 · **Date:** 2026-05-31 · **SCRIP HEAD (pre-commit):** `afb6995`
**Goal:** GOAL-PROLOG-BB.md
**Directive (Lon):** continue GOAL-PROLOG-BB — climb the mode-4 ladder; PLG-9c follows PLG-9b.

## What landed

**The integer-arith tier — `Var is Expr` evaluating into a logic-variable slot — now emits, assembles,
links, and runs in BOTH mode-3 (native flat walk) and mode-4 (standalone `.s`).**

```prolog
main :- X is 2+3, write(X), nl.
:- initialization(main, main).
```
→ `5` in all three modes. Verified 3-mode AGREE: `6*7`→42, `10-3`→7, `abs(-9)`→9 (unary), and the
combined `X = 10, Y is X+5, write(Y), nl` → 15 (PLG-9b unify binds slot 0, the arith reads the bound
slot via `rt_pl_arith`'s IR_LOGICVAR operand handling, unifies the result into slot 1).

## Gates (all green, no regression)

| Gate | Before | After |
|---|---|---|
| GATE-1 smoke m2 | 5/5 | 5/5 |
| GATE-1 smoke m3 | 5/5 | 5/5 |
| GATE-1 smoke m4 | 2 PASS / 3 EXCISED | **3 PASS** (+`arith`) / 2 EXCISED |
| GATE-3 rung m2 | 111/111 | 111/111 |
| GATE-3 rung m3 | 111/111 | 111/111 |
| GATE-3 rung m4 | 2 PASS / 109 EXCISED | **8 PASS / 0 FAIL** / 103 EXCISED |
| prove_lower2 | 53/53 | 53/53 |
| FACT grep | 0 | 0 |
| Icon smoke | m2/m3/m4 6/6 | 6/6 (unaffected) |
| SNOBOL4 smoke | m2 7/7 HARD; m3 5/6; m4 0/6 | unchanged (peer-baseline floors; rt_pl_arith Prolog-only) |

The `arith` smoke source IS `X is 2 + 3, write(X), nl` — GATE-1 m4 2→3 is the direct signal. The 6 new
GATE-3 m4 passers (rung22 write_canonical, rung23 bitwise/max_min/power/sign/truncate, rung29 gcd) were
each checked m2==m4==expected.

## Mechanism (additive, +29/−0 across 2 files)

1. **`src/driver/scrip.c`** — widened the SAME shared flat-tier recognizer (mode-3 + mode-4 in lockstep,
   per PLG-8-native / PLG-9a). `pl_flat_goal_is_simple` now admits `IR_BUILTIN("is")` with `α = IR_LOGICVAR`
   and `β = IR_ARITH` — binary (both operands) or unary (left only) — where each arith leaf operand is a
   scalar `IR_LIT_I` or `IR_LOGICVAR` (new helper `pl_flat_arith_leaf_simple`). These are EXACTLY the shapes
   the `bb_builtin.cpp` MEDIUM_TEXT `is` arm (line ~1434) handles: it flattens the RHS at emit time into
   serialized scalars (`dst_slot`, op via `_.bb_op_lbl`, `lk/li`, `rk/ri`) and calls `rt_pl_is` — NO
   cross-process `IR_t*` pointer (that is the MEDIUM_BINARY twin's mode-3-only path). So, exactly like
   PLG-9b, **NO template change**; the `is` TEXT arm and `bb_prepare_pl`'s `is`→`bb_op_lbl` interning
   (emit_bb.c:610) already existed.

2. **`src/runtime/rt/rt.c`** — added `gcd` + `div` to `rt_pl_arith` (the bug fix below).

## THE ONE REAL BUG (rung29 gcd → 20 instead of 4) + FIX

Widening admitted `X is gcd(12,8)` (binary arith, scalar leaves). mode-4 emitted it but printed `20`
(= 12+8). Root cause: TWO arith evaluators had silently diverged.
- `bb_exec.c`'s `resolve_arith_eval` — the mode-2/3 path (via `rt_pl_is_eval`) — HAS `gcd`/`div`.
- `rt.c`'s `rt_pl_arith` — the mode-4 MEDIUM_TEXT `is` path (via `rt_pl_is`) — did NOT, and its default
  fallthrough is `return lv + rv`. So an unknown op (`gcd`) silently became addition.

This was latent and pre-existing; the mode-4 `is` arm only just started reaching `rt_pl_arith` for these
ops because PLG-9c is the first rung to compile `is` to mode-4. Fix: added `gcd` (Euclid on absolute
values) and `div` (floored integer division) to `rt_pl_arith`, byte-matching `bb_exec.c`. rung29 →
`4|25|` in all three modes; GATE-3 m4 FAIL→PASS.

**KNOWN RESIDUAL DIVERGENCE (not exercised by any corpus rung — left for a dedicated arith-parity rung):**
- `rt_pl_arith`'s `mod` is plain `%`; `bb_exec.c`'s is flooring-mod (differ on mixed signs).
- `rt_pl_arith`'s `lv+rv` default still silently swallows any op it lacks, vs `resolve_arith_eval`'s
  `FAILDESCR`.
The clean long-term fix is to route the mode-4 `is` arm through the SAME `resolve_arith_eval` the other
modes use — but that is a template change, out of PLG-9c's recognizer-only scope. Recommend a focused
`PL-ARITH-PARITY` rung that unifies the two evaluators and re-proves all arith rungs 3-mode.

## DELIBERATE non-coverage (correctly EXCISES — verified no miscompile)

- bare-literal RHS `X is 5` — β is `IR_LIT_I`, not `IR_ARITH`; the MEDIUM_TEXT arm requires `IR_ARITH`
  (mode-3 covers it via the BINARY twin). Recognizer declines → EXCISED m4, runs m2/m3.
- nested arith `X is 2+3*4` — `pl_flat_arith_leaf_simple` rejects a nested `IR_ARITH` operand (the
  MEDIUM_TEXT arm flattens only ONE operand level into `lk/li,rk/ri`). Declines → EXCISED m4, runs m2/m3.

Both give correct m2/m3 output (`5` and `14`) and cleanly EXCISE m4 rather than miscompiling.

## Mode-4 emission (verified — `X is 2+3, write(X), nl`)

```asm
main:
  push rbp ; mov rbp, rsp
  mov edi, 1 ; call rt_pl_env_alloc@PLT          # nslots=1 (PLG-9b: env + trail init)
  call rt_frame@PLT ; mov rdi, rax ; xor esi, esi ; call main_α
  ...
main_α_body:
  # BOX RESOLVE_BUILTIN(is/2)
  mov edi, 0                  # dst_slot 0
  lea rsi, [rip + .S0]        # op "+"
  mov edx, 0 ; mov rcx, 2     # lk, li=2
  mov r8d, 0 ; mov r9, 3      # rk, ri=3
  call rt_pl_is@PLT
  test eax, eax ; je main_ω ; jmp <write box>
  # BOX RESOLVE_BUILTIN(write/1): mov edi, 0 ; call rt_pl_write_var   # slot 0
  # BOX RESOLVE_BUILTIN(nl/0):    mov edi, 10 ; call putchar
```

## NEXT — PLG-9d (facts + clause choice)

`fact(a). main :- fact(X), write(X), nl.` runs m2/m3 (interim) and EXCISES m4. This is the first rung
needing more than a single linear clause body. Pieces:
- Emitter: walk `IR_GOAL` (user-pred call) + `IR_CHOICE` (multi-clause) in TEXT medium.
  `flat_drive_pl_choice` (emit_bb.c) already exists and is used by mode-3 native; confirm it emits in
  MEDIUM_TEXT too.
- Driver mode-4 arm: a predicate-registry emit loop, mirroring the Icon `mode_compile_x86` block's
  `rt_proc_register` loop — register each callee clause body via `walk_bb_flat` in TEXT medium with
  interned cross-block labels (`emit_label_intern`, the same the mode-3 BINARY arms use).
- Then PLG-9e recursion.

Each rung: emit+assemble+link+run AND GATE-1/GATE-3 m3 == m2 hold throughout. Note PLG-9d is a bigger
step than 9b/9c (it is the first that needs the driver to emit MORE than the single `main` graph) — it
is no longer pure recognizer-widening.

## Files

- `src/driver/scrip.c` — `pl_flat_goal_is_simple` admits `is/2` (LOGICVAR = IR_ARITH binary/unary, scalar
  leaves); new helper `pl_flat_arith_leaf_simple`.
- `src/runtime/rt/rt.c` — `rt_pl_arith` gains `gcd` + `div` (match `bb_exec.c`).
- `.github/GOAL-PROLOG-BB.md` — PLG-9c sub-rung marked done + gate-table refresh.
