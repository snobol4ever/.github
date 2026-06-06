# HANDOFF 2026-06-06 (Sonnet 4.6) — PROLOG-BB: lower_prolog.c standalone + PL-GZ-8b

SCRIP commit: `3dfdc7c`. .github commit: this doc + GOAL-PROLOG-BB.md watermark update.

## Session summary — two things landed

### 1. PL-GZ-8b: LOGICVAR operands for DET_CMP and DET_IS (commit d1ac369)

Extended GZ substrate to admit LOGICVAR operands in arith CMP (`X >= 2`) and IS with
variable RHS (`Y is X - 3`). Frame-slot ABI — no IR_t* pointers cross to runtime.

New runtime helpers in `IR_interp.c` + `rt.h`:
- `rt_pl_arith_cmp_cell_val(op, lhs_cell, lhs_ival, rhs_cell, rhs_ival)` — cell=NULL
  means use ival as literal; cell non-NULL means deref Term* from frame slot
- `rt_pl_is_cell_arith(lhs_cell, rhs_cell, op, rhs_ival)` — evaluates Y op C at runtime

Template changes: `bb_det_cmp.cpp` uses `FRQ(slot)` + `xor`/immediate for both operands;
`bb_det_is.cpp` adds `gz_arith_var_plus_const` recognizing LOGICVAR, Y+C, Y-C, Y*C shapes.

Admission in `scrip.c`: CMP now accepts `LIT_I|LOGICVAR` on both sides; IS rhs accepts
`LOGICVAR` or `ARITH(LOGICVAR, LIT_I)`.

Bug caught: `x86("test32","eax","eax")` had no TEXT encoder — silently dropped in m4,
leaving `je PORT_OMEGA` on stale ZF. Fixed to `x86("test","eax","eax")`.

Gate additions to `test_gate_pl_gz7.sh`:
- `gz_pin gzvarith_cmp` — `m(X), X>=2 → write(X)` outputs `s\n2\n3`, GZ-asserted
- `gz_pin_noite gzvarith_is` — `X=5, Y is X-3` outputs `2`, GZ-asserted

### 2. lower_prolog.c: fully standalone (commit 3dfdc7c)

Rewrote `lower_prolog.c` to call no shared `lower.c` function at runtime.

Own static helpers:
- `pl_nalloc` → `IR_node_alloc` direct
- `pl_set_succ_fail`, `pl_ret` → trivial
- `pl_emit_leaf` → Prolog-specific: β always = ω_in (no resumable Prolog nodes)
- `pl_lower_unhandled` → fprintf + NULL return
- `pl_tm`, `pl_tm_g` → pattern matchers (verbatim copies from lower.c)
- `pl_wire_seq` → sequence wiring, calls `pl_lower_goal` internally
- `pl_wire_alt` → alternation wiring, calls `pl_lower_goal` internally

Internal entry: `static pl_lower_goal` — handles all Prolog TT types.

Three public symbols only:
- `lower_goal(lcx_t)` — thin adapter for `lower.c`'s `ROLE_GOAL` dispatch
- `lower2_goal_entry` — called by `prove_lower2.c`
- `lower2_clause_body_entry` — called by `lower_program.c`

`lower_internal.h` retained for `lcx_t`/`pl_vars_t` typedef sharing and the
`lower_goal(lcx_t)` declaration. No shared functions called at runtime.

## Gate verification on 3dfdc7c

GATE-1: 5/5 m2 HARD · 4/0/1-EXC m3 · 5/5 m4
GATE-3: 115/115 m2 HARD · 21/0/94-EXC m3 · 105/0/10-EXC m4
test_gate_pl_gz7: PASS (all probes including gzvarith_cmp + gzvarith_is)
test_gate_bb_one_box: PASS
seg_byte/SL_B grep: 0 · g_vstack: 0

## Next opener: PL-GZ-9

Corpus reconquest — all 115 rungs onto the new GZ path. Mechanisms to re-land:
findall (drive new boxes, no meta rail), catch/throw (PT-3 CP-truncate + ball-copy
LAW), aggregate/nb, dynamic DB (B-full: runtime assert → MEDIUM_BINARY emit into
RX slab; m3 ≡ m4 by construction). Session setup per GOAL-PROLOG-BB.md §Session setup.
