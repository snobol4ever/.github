# HANDOFF — PLG-9h: mode-4 native float `is/2` (+ pre-existing integer-`/` miscompile fix)

**Date:** 2026-06-01 · **Model:** Opus 4.8 · **Track:** GOAL-PROLOG-BB, mode-4 ladder
**Status:** COMPLETE, all gates green, landed.

## What shipped

Float-producing/consuming `is/2` now emits natively in mode-4 (`--compile --target=x86`).

**GATE-3 rung suite m4: 76 → 80 PASS** (0 FAIL, 35 → 31 EXCISED). Closed the 4 rung29 float rungs:

| rung29 test | exercises | result type |
|---|---|---|
| `float_conversion` | `truncate(3.7)` `ceiling(3.2)` `floor(3.9)` `round(3.5)` | float input → **int** output |
| `float_constants`  | `pi` `exp(1.0)` | float |
| `float_math`       | `sqrt(4.0)` `sin(0.0)` `cos(0.0)` | float |
| `float_parts`      | `float_integer_part(3.7)` `float_fractional_part(3.7)` `float(5)` | float (incl. `0.7000000000000002` byte-exact) |

(`rung29_number_ops_gcd` already passed m4 — integer.)

**Bonus fix:** a **pre-existing** mode-4 integer-`/` miscompile, surfaced by edge-probing, not by any rung.
`X is 7/2` gave `3` (integer `rt_pl_arith` division) while the mode-2 oracle and mode-3 give `3.5`. `/` now
routes through the float evaluator, which yields a float when integer operands do not divide evenly and an
int when they do. Verified across all three modes: `7/2`→3.5, `1/3`→0.333…, `6/2`→3, `5/5`→1, `10/4`→2.5.

## Root cause

The MEDIUM_TEXT `is` arm called `rt_pl_is`@PLT (integer-only `rt_pl_arith`, `long` result) and the admission
gate `pl_flat_arith_leaf_simple` rejected `IR_LIT_F`. The MEDIUM_BINARY arm (PLR-K-12) already handled floats
via `rt_pl_is_eval(IR_t* lhs, IR_t* rhs)` → `resolve_arith_eval`, but those are **in-process IR_t\* pointers**,
dead in a standalone `.s`. So mode-3 (in-process JIT, BINARY arm) was fine; only mode-4 (separate process,
TEXT arm) lacked a float path.

## The four changes (Prolog-arm-only, FACT-clean)

1. **`src/lower/bb_exec.c`** — new `rt_pl_is_f(int dst_slot, const char *op, int lk, long li, double ld,
   int rk, long ri, double rd)`, the serialized-scalar twin of `rt_pl_is_eval`, placed next to `rt_pl_is`.
   Lives in `bb_exec.c` because that TU is linked into `libscrip_rt.so` (reachable `@PLT`) and already has
   `<math.h>`, `M_PI`/`M_E`, `term_new_float`/`term_new_int`, `term_deref`, `unify`, `trail_mark/unwind`,
   `g_resolve_env`/`g_resolve_trail`. Resolves operands (int lit→`li`; float lit→`ld`; bound slot→read
   `g_resolve_env[li]` and deref); applies the op **mirroring `resolve_arith_eval` byte-for-byte** (pi/e
   nullary; unary trig/sqrt/exp/log/float/rounding; binary +,-,\*,/,\*\*,^,min,max with the int-vs-float
   result decision incl. `/` divisibility and min/max type-preservation); builds an int|float Term; unifies
   into the dst slot in `g_resolve_env` under a trail mark. **SysV: 6 GP (`edi,rsi,edx,rcx,r8d,r9`) + 2 SSE
   (`xmm0,xmm1`) — all in registers, no stack args.** `rk == -1` marks a unary/nullary RHS.

2. **`src/emitter/emit_bb.c`** (`bb_prepare_pl`) — interns the op label (`bb_op_lbl`) for the `is` + `IR_ATOM`
   RHS case (`X is pi` / `X is e`). The pre-existing code only set it for the `IR_ARITH` RHS. Prolog-only:
   SNOBOL never emits `IR_BUILTIN("is")`.

3. **`src/emitter/BB_templates/bb_builtin.cpp`** — (a) extern decl of `rt_pl_is_f`; (b) static discriminator
   `bb_pl_op_floaty` (transcendental/float-producing functors, the rounding functors that consume a float,
   and `/`); (c) a float `is` MEDIUM_TEXT arm placed **before** the integer `is` arms. Fires when the RHS is
   `IR_ATOM` pi/e, an arith with a floaty op, or an arith with any `IR_LIT_F` operand. Serializes operands
   (float literal: `mov rax,<bits>; movq xmm0/xmm1, rax` — no `.rodata` constant, no value stack),
   `lea rsi,[rip+op_lbl]`, `sub rsp,8` (16-align across libm), `call rt_pl_is_f@PLT`, `add rsp,8`,
   `test eax / je ω / jmp γ; β→ω`.

4. **`src/driver/scrip.c`** — static helpers `pl_arith_op_floaty` (byte-identical to `bb_pl_op_floaty`) and
   `pl_flat_arith_leaf_float_ok` (admits `IR_LIT_I`/`IR_LIT_F`/`IR_LOGICVAR`). Rewrote the `is` branch of
   `pl_flat_goal_is_simple`: accept `IR_ATOM` pi/e; for `IR_ARITH`, if floaty use the float-leaf checker, else
   the integer path unchanged. **Deliberately did NOT widen `pl_flat_arith_leaf_simple` itself** — it is also
   used by the arith *comparison* gate, which reads `ival` not `dval`, so float comparisons (`3.5<4.0`)
   correctly still EXCISE in mode-4 (clean `[SMX]` banner, never a miscompile). Updated two stale
   "float `is` stays EXCISED" comments in `pl_rich_node_emittable`.

## Why mode-3 stayed byte-identical

`pl_flat_goal_is_simple` is shared by the mode-3 native flat tier and the mode-4 rich tier. Widening it moves
mode-3 float `is` from the interim `bb_exec_once` route to the native flat tier — but that tier emits via the
MEDIUM_BINARY arm, which calls `rt_pl_is_eval` → `resolve_arith_eval`, **the exact same evaluator the interim
route uses**. Same result Term, same unify into the same slot; only the dispatch mechanism differs. Confirmed:
m2 and m3 both 111/111, float output byte-exact via the native tier.

## Verification (all green)

- GATE-1 smoke: **5/5/5**.
- GATE-3 rung suite: m2 **111/111**, m3 **111/111**, m4 **80 PASS / 0 FAIL / 31 EXCISED**.
- FACT grep 0; `g_vstack` 0; `test_gate_pl_no_value_stack.sh` PASS; template-purity audit 7 baseline
  (`bb_builtin.cpp` NOT flagged — the TEXT arm is `s_2asm`/`movq`/`@PLT` only; `rt_pl_is_f` is a runtime
  effect-helper, not a byte-emitter); `prove_lower2.sh` PASS.
- Sibling neutrality: Icon 12/12/12; SNOBOL4 12 PASS / 7 FAIL (the `/` addition lives only in Prolog-only
  discriminator lists; `emit_bb.c` change only fires for `IR_BUILTIN("is")` with an `IR_ATOM` RHS).
- Robustness: binary float `1.5+2.5`→4.0 (m2/m3/m4); `/` with a bound-var operand (`Y=7, X is Y/2`)→3.5 m4;
  mixed `max(3,2.5)`→3; nested `(4/2)/2` EXCISES cleanly in m4 (no miscompile); float comparison EXCISES.
- C style: ≤200-char lines, zero blank lines inside functions, block comments above functions.

## Remaining 31 EXCISED — all substrate-requiring (none float)

findall ×5, retract/retractall ×5, abolish ×5, numbervars ×5, copy_term ×1, aggregate ×4, catch/throw ×5,
dcg_generate ×1. **The cheap "a BINARY arm exists, it just needs an `@PLT` TEXT twin" closures are now
exhausted** (writeq/write_canonical/atomic_list_concat were PLG-9g; float `is/2` was PLG-9h). The rest need a
real runtime substrate: the dynamic-DB families (retract/abolish/assertz) are owned by WAM-CP-13's
`pl_cp_*`→`rt_pl_cp_*` mode-4 emit; findall/aggregate need the goal-subgraph closure (PLG-10); numbervars/
copy_term need term-mutation/var-identity machinery in the standalone binary.

## Next tractable rung

No remaining EXCISED family is a self-contained closure. The next mode-4 progress requires committing to one
substrate: **WAM-CP-13** (dynamic-DB mode-4 emit — unblocks retract/abolish/assertz, 15 rungs) is the largest
single payoff but is the heaviest. **PLG-10** (findall/aggregate goal-subgraph) is next. Neither is a
single-session closure; both want a fresh design pass against the canonical sources before coding.
