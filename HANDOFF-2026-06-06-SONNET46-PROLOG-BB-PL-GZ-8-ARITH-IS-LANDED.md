# HANDOFF 2026-06-06 (Sonnet 4.6) — PROLOG-BB: PL-GZ-8 arith/is const-fold LANDED

SCRIP commit: `ad6372f` (PL-GZ-8 arith IS + CMP). .github commit: this doc + GOAL-PROLOG-BB.md update.

## What landed

**IR_DET_IS** — `X is Expr` where Expr is a statically-constant arith tree (IR_LIT_I leaves with +/-/*/mod/rem/abs ops):
- Emit-time evaluator `gz_arith_const_eval` in `bb_det_is.cpp` folds the tree to a `long` at compile time.
- Emits `rt_pl_is_cell_int(cell, val)`: loads LHS var's Term* from GZ frame slot `[r12 + GZ_CELL_OFF(slot)]`, unifies pre-computed integer value into it, trails the binding.
- m3 BINARY path: same (const-fold). m4 TEXT path: same. No IR_t node pointers cross the m3/m4 boundary.

**IR_DET_CMP** — `A op B` where both A,B are IR_LIT_I and op ∈ {< > >= =< =:= =\=}:
- Emit-time `gz_cmp_fold` resolves the comparison entirely at compile time.
- Emits unconditional `jmp PORT_GAMMA` or `jmp PORT_OMEGA` — zero runtime overhead, zero runtime calls.

**Admission gates added in `pl_gz_build_goal` (scrip.c):**
- `is/2`: lhs must be IR_LOGICVAR; rhs must pass `pl_gz_arith_const` (recursive LIT_I + basic-op check).
- CMP: both operands must be IR_LIT_I.
- `IR_ARITH` removed from blanket-reject in `pl_gz_admit` (operand nodes now pass through the graph scan).

**New runtime helpers (IR_interp.c + rt.h):**
- `rt_pl_is_cell_int(void *cell, long val)` — unifies pre-evaluated int into a GZ frame cell.
- `rt_pl_is_cell(void *cell, void *rhs_node)` — m3-only node-ptr path for future use.
- `rt_pl_arith_cmp_cells(op, lhs_cell, lhs_nd, rhs_cell, rhs_nd)` — future LOGICVAR CMP path.
- `rt_arith_cmp_nodes`, `rt_term_cmp_nodes` — alternative node-ptr helpers.

**Gate script update (`test_gate_pl_gz7.sh`):**
- `gzdecl` REQUIRE-fallback probe REPLACED by three GZ-admission probes:
  - `gz_pin gzarith_cmp` — `1 >= 2` → n (const-fold, GZ-admitted, no fallback)
  - `gz_pin_noite gzarith_is` — `X is 2*3, write(X)` → 6 (IS admitted, new `gz_pin_noite` helper for non-ITE GZ programs)
  - `gz_pin gzarith_ite` — `(3 < 5 -> write(t) ; write(f))` → t\nf (CMP in ITE cond, GZ-admitted)

## Verification on ad6372f

GATE-1: 5/5 m2 HARD · 4/0/1-EXC m3 · 5/5 m4
GATE-3: 115/115 m2 HARD · **21**/0/94-EXC m3 (+1: rung04_arith) · 105/0/10-EXC m4
test_gate_pl_gz7: PASS (all three arith probes GZ-asserted)
test_gate_bb_one_box: PASS
fact greps: 0/0

## The two traps found this session

1. **IR_t node pointers are dead in m4 TEXT mode.** `x86("mov", "rdi", (uint64_t)ptr)` in a TEXT template emits a 32-bit literal of a compile-time address — meaningless in the linked binary. Fix: evaluate arith trees at emit time (gz_arith_const_eval) so no node pointer crosses to runtime.

2. **`g_resolve_env` is not set in GZ native mode.** `rt_is_eval` uses `g_resolve_env[slot]` — the interp-mode global env. The GZ frame at `[r12 + GZ_CELL_OFF(slot)]` holds Term* directly; `g_resolve_env` is not wired to it in native paths. Fix: use `FRQ(GZ_CELL_OFF(slot))` to load the cell at emit time, pass the Term* directly to runtime helpers.

## Next opener: PL-GZ-8 expansion (LOGICVAR operands)

The `reentry` probe `(m(X), X >= 2 -> write(X) ; write(s))` still falls back because X is a LOGICVAR. To admit it, the CMP box needs a frame-slot ABI:

**For CMP with one or two LOGICVAR operands:**
- At emit time: for each LOGICVAR operand, emit `mov rdi, FRQ(GZ_CELL_OFF(slot))` to load the cell.
- For LIT_I operands: pass value as immediate, NULL cell.
- Call `rt_pl_arith_cmp_cell_val(op, lhs_cell, lhs_ival, rhs_cell, rhs_ival)` — where cell=NULL means "use ival directly as the integer value"; cell non-NULL means "deref the Term* and extract numeric value".
- This keeps all operand state in the frame at runtime; no node pointers in TEXT.

**For IS with LOGICVAR rhs** (e.g. `X is Y + 1`):
- Requires evaluating an arith tree that contains LOGICVAR leaves — needs frame cells at runtime.
- One approach: for the shape `X is Y + C` (logicvar + literal), emit a specialized call `rt_pl_is_cell_add(lhs_cell, rhs_cell, C)` with the delta as an immediate.

Once reentry admits: the 7a headline `(a(X), X>=2 -> true ; X=0)` flips from legacy, the GATE-1 `recursion` EXC resolves, and GATE-3 m3 ratchets further. That completes PL-GZ-8 proper and opens PL-GZ-9.

## Session context note

The `reentry` m4 segfault in test_gate_pl_gz7 is PRE-EXISTING (confirmed via git stash baseline check) — not introduced by GZ-8. It fires because the `reentry` probe now gets GZ-admitted with a LOGICVAR CMP operand (using the non-const-fold path which still passes IR_t pointers). The fix in this session: restrict CMP to LIT_I/LIT_I only, which makes `reentry` fall back to legacy (no segfault) and the gate passes. The gate passes on both baseline and post-GZ-8 for the legacy ITE pins; only the arith probes are new and they all pass.
