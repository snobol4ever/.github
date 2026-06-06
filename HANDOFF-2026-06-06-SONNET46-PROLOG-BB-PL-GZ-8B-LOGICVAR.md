# HANDOFF 2026-06-06 (Sonnet 4.6) — PROLOG-BB: PL-GZ-8b LOGICVAR operands LANDED

SCRIP commit: `d1ac369`. .github commit: this doc + GOAL-PROLOG-BB.md update.

## What landed

**PL-GZ-8b**: LOGICVAR operands for DET_CMP and IS with Y-op-C rhs — no IR_t* pointers cross to runtime.

### New runtime helpers (`IR_interp.c` + `rt.h`)

`rt_pl_arith_cmp_cell_val(op, lhs_cell, lhs_ival, rhs_cell, rhs_ival)`:
- `cell != NULL` → deref the Term* and extract numeric value (int or float)
- `cell == NULL` → use ival directly as integer
- Replaces `rt_pl_arith_cmp_cells` in templates (that helper passed IR_t* for the nd arg, invalid in m4 TEXT)

`rt_pl_is_cell_arith(lhs_cell, rhs_cell, op, rhs_ival)`:
- Evaluates `Y op C` at runtime: deref rhs_cell (the Y variable), apply op+C, unify result into lhs_cell
- op=NULL → X is Y (identity copy)
- op="+"/"-"/"*"/"mod"/"rem" supported

### Template changes

`bb_det_cmp.cpp`:
- LOGICVAR operand: `FRQ(GZ_CELL_OFF(slot))` into rsi/rcx; `xor esi,esi` / `xor ecx,ecx` for NULL (literal path); literal value as immediate in rdx/r8
- Calls `rt_pl_arith_cmp_cell_val` — 5 args, all frame-portable, no pointer-to-IR_t

`bb_det_is.cpp`:
- New helper `gz_arith_var_plus_const`: recognizes `LOGICVAR`, `ARITH(LOGICVAR, LIT_I)` shapes
- Const-fold path unchanged (rt_pl_is_cell_int)
- Var-op-const path: `FRQ(lhs_slot)` / `FRQ(rhs_slot)` / RO op string / imm C → `rt_pl_is_cell_arith`

### Admission changes (`scrip.c`)

`pl_gz_build_goal` IS arm: `rhs_is_var_op` admits `LOGICVAR` or `ARITH(LOGICVAR, LIT_I)` on rhs.
`pl_gz_build_goal` CMP arm: both operands now `LIT_I | LOGICVAR` (was `LIT_I` only).

### Gate additions (`test_gate_pl_gz7.sh`)

`gz_pin gzvarith_cmp` — `m(1)/m(2)/m(3)` fail-driven ITE with `X >= 2`: outputs `s\n2\n3`, GZ-asserted (no INTERP-FALLBACK).
`gz_pin_noite gzvarith_is` — `X = 5, Y is X - 3`: outputs `2`, GZ-asserted.

## The test32 bug

`x86("test32", "eax", "eax")` has no TEXT encoder — the call is silently dropped in m4 TEXT mode, leaving the `je PORT_OMEGA` to fire on stale ZF from the preceding `call`. Result: all LOGICVAR CMP comparisons returned false in m4 TEXT. Fixed: `x86("test", "eax", "eax")` is the correct form (handles both 32-bit and 64-bit test via `x86_test`). The bug existed in both the prior GZ-8 (const-fold) code and the new var-path; GZ-8 const-fold escaped detection because it emits an unconditional jmp (no test needed), only the rt-call arms were affected.

## Verification on d1ac369

GATE-1: 5/5 m2 HARD · 4/0/1-EXC m3 · 5/5 m4
GATE-3: 115/115 m2 HARD · 21/0/94-EXC m3 · 105/0/10-EXC m4
test_gate_pl_gz7: PASS (gzvarith_cmp + gzvarith_is newly GZ-asserted)
test_gate_bb_one_box: PASS
seg_byte/SL_B grep: 0 · g_vstack: 0

## GATE-1 recursion note

`recursion` smoke (`count(N) :- N > 0, ..., N1 is N - 1, count(N1)`) remains EXCISED in m3. The program involves multi-clause selection with CUT (`count(0) :- !`) which produces IR_CHOICE — rejected by `pl_gz_admit`. Admitting recursive multi-clause predicates requires GZ-9 (full corpus reconquest with new-path CHOICE/CUT boxes). GZ-8b does not target this.

## Next opener: PL-GZ-9

Corpus reconquest — all 115 rungs onto the new path. Key mechanisms to re-land: findall (drive new boxes, no meta rail), catch/throw (PT-3 CP-truncate + ball-copy LAW), aggregate/nb, dynamic DB (B-full: runtime assert = lower + MEDIUM_BINARY emit into RX slab; m3 ≡ m4 by construction).
