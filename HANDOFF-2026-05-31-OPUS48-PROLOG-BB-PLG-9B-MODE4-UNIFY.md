# HANDOFF — PLG-9b: Prolog mode-3/mode-4 first per-box logic-variable slot (`X = world, write(X), nl`)

**Author:** Claude Opus 4.8 · **Date:** 2026-05-31 · **SCRIP HEAD (pre-commit):** `6260d53`
**Goal:** GOAL-PROLOG-BB.md
**Directive (Lon):** continue GOAL-PROLOG-BB — climb the mode-4 ladder; PLG-9b is the next sub-rung after PLG-9a.

## What landed

**The unify tier — one logic-variable slot bound to a constant — now emits, assembles, links, and runs
in BOTH mode-3 (native flat walk) and mode-4 (standalone `.s`).**

```prolog
greet :- X = world, write(X), nl.
:- initialization(greet, main).
```
`scrip --compile --target=x86 greet.pl` → standalone GAS `.s`; `as --64` + `gcc -no-pie … libscrip_rt.so`
links it; running prints `world`. Variants verified 3-mode AGREE (m2 `--interp` == m3 `--run` == m4):
- integer constant: `X = 42, write(X), nl` → `42`
- symmetric: `world = X, write(X), nl` → `world`
- multi-variable: `X = hello, Y = world, write(X), nl, write(Y), nl` → `hello\nworld`

## Gates (all green, no regression)

| Gate | Before | After |
|---|---|---|
| GATE-1 smoke m2 | 5/5 | 5/5 |
| GATE-1 smoke m3 | 5/5 | 5/5 |
| GATE-1 smoke m4 | 1 PASS / 4 EXCISED | **2 PASS** (`write_atom`+`unify`) / 3 EXCISED |
| GATE-3 rung m2 | 111/111 | 111/111 |
| GATE-3 rung m3 | 111/111 | 111/111 |
| GATE-3 rung m4 | 2 PASS / 109 EXCISED | 2 PASS / 109 EXCISED (corpus has no bare-unify rung; see below) |
| prove_lower2 | 53/53 | 53/53 |
| FACT grep | 0 | 0 |
| Icon smoke | m2/m3/m4 6/6 | unaffected (zero template files touched) |
| SNOBOL4 smoke | m2 7/7 | unaffected |

The smoke `unify` source IS exactly `X = world, write(X), nl`, so GATE-1 m4 1→2 is the direct signal.
GATE-3 m4 is unchanged because no corpus rung is a *bare* unify-tier program — **rung03 is COMPOUND unify**
(`f(X,a) = f(b,Y)`), which routes through `IR_STRUCT` operands that PLG-9b deliberately does NOT yet admit;
it correctly still EXCISES (that is the PLG-9b+ IR_STRUCT tier).

## Mechanism (additive, Prolog-only, +63/−3 across 3 files)

1. **`src/driver/scrip.c`** — widened the flat-tier recognizer. NOTE this recognizer
   (`pl_flat_goal_is_simple` + `pl_flat_body_root`) is SHARED by the PLG-8-native mode-3 arm and the
   PLG-9a mode-4 arm, so both widen in lockstep (mode-3 and mode-4 stay byte-consistent automatically).
   - `pl_flat_goal_is_simple` now admits: (a) `IR_UNIFY` of the scalar shapes `(LOGICVAR = ATOM|LIT_I)`
     and the symmetric `(ATOM|LIT_I = LOGICVAR)`, plus the missing-operand vacuous-success case; (b)
     `write`/`print` of an `IR_LOGICVAR` arg (alongside PLG-9a's constant `IR_ATOM`/`IR_LIT_I`).
   - `pl_flat_body_root` drops the `nslots > 0` guard. A slot-bearing body now qualifies PROVIDED every
     conjunction element still passes the per-goal check — a compound/var-var unify or a user call has an
     element that fails → NULL → interim route (mode-3) / EXCISED (mode-4). Widening stays conservative.
   - Mode-4 `main:` wrapper emits `mov edi,nslots; call rt_pl_env_alloc@PLT` BEFORE `call rt_frame` when
     `pl_main->nslots > 0` (nslots==0 hello tier skips it; `g_resolve_env` stays NULL, never dereferenced).

2. **`src/runtime/rt/rt.c` + `rt.h`** — new public `rt_pl_env_alloc(int nslots)`, the native-flat Prolog
   runtime-state setup hook: `GC_MALLOC`s `g_resolve_env` to `nslots+8` (mirrors the driver's mode-3 alloc
   at `scrip.c`) AND `trail_init(&g_resolve_trail)`.

## THE SLOT HOME — reconciliation of the PLG-9a "Findings" speculation

PLG-9a's handoff guessed the logic-var slot "must live in the ζ-frame `[r12+off]`, NOT `g_resolve_env`."
**That was wrong for a Prolog logic variable.** `g_resolve_env` IS the legitimate per-activation home: it
is allocated fresh per activation (exactly like `pl_foo_2_r`'s locals in the archived `prolog_emit.c`),
NOT a global side-channel like a value stack or AG ring. The ζ-frame `[r12+off]` is for ANONYMOUS box-result
slots and Icon/SNOBOL named-variable slots; a Prolog logic variable's binding is a `Term*` that the existing
`bb_unify` / `bb_logicvar` / `bb_builtin`(write) templates ALREADY read & write through `g_resolve_env[slot]`
(via `rt_pl_node_to_term` / `rt_pl_unify_terms` / `rt_pl_write_var`). **So PLG-9b needed NO template change.**
The templates were already correct; only the driver's flat-tier recognizer had to widen, and the env + trail
had to be set up in the standalone binary.

## THE ONE REAL BUG (mode-4 multi-unify segfault) + FIX

A single unify worked; a SECOND unify segfaulted in mode-4 only (m2/m3 fine). Bisected to the second
`trail_push` (NOT the writes — `1 unify, write slot0 twice` worked; `2 unify, 1 write` crashed).

Root cause: the standalone mode-4 binary's `main:` never calls `rt_init` (that is the interpreter driver's
entry), so `g_resolve_trail` stayed zero-initialized `{stack=NULL, top=0, capacity=0}`. The first
`rt_pl_unify_terms` limps on a 0-capacity trail by luck — `trail_push` does `capacity *= 2` (still 0),
`GC_realloc(NULL, 0)` returns a usable tiny block, `stack[0]` write succeeds. The second `trail_push` then
writes `stack[1]` past the zero-size block → SIGSEGV. The PLG-9a hello tier never hit it (a constant-atom
`write` needs no trail).

Fix: `rt_pl_env_alloc` also `trail_init`s — done in the same function since it is the native-flat setup hook.
After the fix the multi-var case agrees `hello\nworld` across m2/m3/m4.

## Mode-4 emission (verified by inspection — `X = world, write(X), nl`)

```asm
main:
  push rbp ; mov rbp, rsp
  mov edi, 1 ; call rt_pl_env_alloc@PLT     # nslots=1: alloc env + init trail
  call rt_frame@PLT ; mov rdi, rax ; xor esi, esi ; call main_α
  xor eax, eax ; pop rbp ; ret
main_α:
  push r12 ; mov r12, rdi ; lea r10, [rip + Δ]
  # BOX RESOLVE_UNIFY (X = world)
  sub rsp, 16
  mov edi, 56 ; mov rsi, 0 ; xor edx,edx ; xorps xmm0,xmm0 ; call rt_pl_node_to_term  # L = LOGICVAR slot 0
  mov [rsp+0], rax
  mov edi, 57 ; mov rsi, 0 ; lea rdx,[rip+.S0] ; xorps xmm0,xmm0 ; call rt_pl_node_to_term  # R = ATOM "world"
  mov rsi, rax ; mov rdi, [rsp+0] ; add rsp, 16 ; call rt_pl_unify_terms
  test eax, eax ; je main_ω ; jmp <write box>
  # BOX RESOLVE_BUILTIN(write/1):  mov edi, 0 ; call rt_pl_write_var   # slot 0
  # BOX RESOLVE_BUILTIN(nl/0):     mov edi, 10 ; call putchar
  ...
.section .rodata
.S0: .string "world"
```
(IR_LOGICVAR=56, IR_ATOM=57 confirmed by enum probe.)

## NEXT — PLG-9c (arith `is/2` with a bound var → slot)

`main :- X is 2+3, write(X), nl.` already runs m2/m3 (interim) and EXCISES m4. Widen the SAME shared
recognizer to admit `IR_BUILTIN("is")` with an `IR_LOGICVAR` LHS slot and an arith RHS (`IR_ARITH` /
`IR_BUILTIN` over `IR_LOGICVAR`/`IR_LIT_I`). The `bb_builtin.cpp` `is` TEXT arm + `rt_pl_arith`/`rt_pl_is`
helpers already exist (CAT-D-arith), so — exactly as PLG-9b — expect NO template change, only recognizer
widening. Confirm the arith result unifies into the LHS slot in `g_resolve_env` (same path as PLG-9b's `=`).

Then: PLG-9d facts/choice (`IR_GOAL` + `IR_CHOICE` + a `rt_proc_register` predicate-registry emit loop
mirroring the Icon `mode_run`/`mode_compile_x86` block) → PLG-9e recursion. Each rung: emit+assemble+link+run
AND GATE-1/GATE-3 m3 == m2 hold throughout.

## Files

- `src/driver/scrip.c` — flat-tier recognizer widen (`pl_flat_goal_is_simple` IR_UNIFY + write(LOGICVAR);
  `pl_flat_body_root` nslots guard lifted); mode-4 `main:` wrapper emits `rt_pl_env_alloc(nslots)`.
- `src/runtime/rt/rt.c` / `rt.h` — `rt_pl_env_alloc(int)`: alloc `g_resolve_env` + `trail_init`.
- `.github/GOAL-PROLOG-BB.md` — PLG-9b sub-rung marked done + gate-table refresh.
