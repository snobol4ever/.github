# HANDOFF — 2026-05-25 Sonnet Session B

## Session summary

Goal: GOAL-PROLOG-BB — two new steps recorded and PJ-12 implemented.

## What was done

### PJ-12 — Three-deletion pipeline cleanup (one4all `d073acf9`)

Three data structures are now freed at the correct pipeline boundaries:

**1. `tree_t *ast_prog` — freed after `lower()` completes**
- Added `ast_tree_free(tree_t *p)` inline to `src/include/ast.h`
- Recursively frees every node and its `c[]` children block
- Does NOT free `v.sval` — may alias lexer buffers
- Called immediately after every `sm_preamble()` call in `scrip.c`
- Also called after `codegen_program()` for non-x86 paths

**2+3. `SM_sequence_t` arrays + `BB_graph_t` objects — freed after emitter**
- Added `stage2_free_sm_bb(stage2_t *s2)` to `scrip_sm.c`/`scrip_sm.h`
- Frees each `BB_graph_t*` in `bb_table[]` via `BB_free()`, then frees SM arrays
- Called after `sm_codegen_text` succeeds (text emit path)
- Called after `sm_jit_run` completes (JIT path — SM instrs needed during execution via `CUR_INS`, so free is AFTER run, not before)
- `--interp` path untouched — SM walked at runtime

### PJ-11 + PJ-12 steps recorded in GOAL-PROLOG-BB.md (.github `8cd1c14a`)

PJ-11: ban raw `(uintptr_t)pBB` pointer embedding in BB templates for text/binary emit arms. Known offenders: `bb_binop_gen.cpp`, `bb_alt.cpp`, `bb_arith.cpp`, `bb_builtin.cpp`. Fix: use `_.node->*` for scalar reads; `bb_ptr_slot_lbl` (TEXT) / `bb_rt_obj` (BINARY) for pointer operands.

## Gates at handoff

```
smoke_prolog:        5/5  ✅
crosscheck_prolog:   128/0 SKIP=4 ORACLE_MISS=11  ✅
crosscheck_snobol4:  5/0 (beauty_omega pre-existing ORACLE_MISS, not regression)  ✅
crosscheck_icon:     4/0  ✅
```

## Watermarks

```
one4all:  d073acf9
.github:  8cd1c14a
```

## Next step

**PJ-11a** — In all BB templates, replace `pBB->ival` / `pBB->ival2` / `pBB->sval` with `_.node->ival` / `_.node->ival2` / `_.node->sval`. This is the scalar read fix (no pointer embedding yet). Build clean; gates unchanged.

Then PJ-11b: add `bb_prepare_binop_gen()` in `emit_bb.c` (allocates `bb_rt_obj`, calls `xa_dispatch(XA_BB_PTR_SLOT)` in TEXT).
Then PJ-11c: TEXT arm — `lea rdi, [rip + _.bb_ptr_slot_lbl]`.
Then PJ-11d: BINARY arm — `u64le(_.bb_rt_obj)`.
Then PJ-12c: ASAN verify no use-after-free.

## Session start for next session

1. Clone `.github`, `corpus`, `one4all`
2. Read `PLAN.md` and `GOAL-PROLOG-BB.md`
3. Read `RULES.md`
4. Run `cd /home/claude/one4all && bash scripts/build_scrip.sh`
5. First incomplete step: **PJ-11a**
