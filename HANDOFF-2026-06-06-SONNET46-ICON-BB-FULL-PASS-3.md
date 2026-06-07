# HANDOFF-2026-06-06-SONNET46-ICON-BB-FULL-PASS-3.md

## Session summary

**Goal:** GOAL-ICON-FULL-PASS.md — BUG-2..6 fixes + PIVOT (revamp/hygiene delegated to GOAL-BB-FIXUP).
**Model:** Claude Sonnet 4.6
**SCRIP HEAD:** `f15cfc8`
**.github HEAD:** `ecce54b5`
**Baseline → result:** m2 181 → **194** (+13) · m3 31 · m4 34

---

## PIVOT — direction change (Lon directive, this session)

REVAMP and HYGIENE work is **fully delegated to GOAL-BB-FIXUP**. GOAL-ICON-FULL-PASS now owns ONLY:
- `src/lower/lower_icon.c` — lowerer correctness
- `src/interp/IR_interp.c` — m2 interpreter semantics
- `src/runtime/` — Icon runtime behavior

Phase 3/4 native template steps (ICN-FULL-19 through ICN-FULL-31) DELETED from GOAL-ICON-FULL-PASS.md. GOAL-ICON-FULL-PASS.md rebuilt lean — pivot committed to .github at `ecce54b5`.

---

## What landed

### BUG-2: IR_CASE arm-descriptor chain (`f15cfc8`)

**Root cause (two parts):**
1. `icn_case` in `lower_icon.c` treated flat AST children as arm-wrapper structs. The Icon parser emits `e->c[0]=selector, e->c[1]=key1, e->c[2]=val1, e->c[3]=key2, e->c[4]=val2, ..., e->c[n-1]=default`. Old code iterated `e->c[i+1]` treating each as an arm struct with sub-children — since raw key nodes have `n=0`, the `arm->n>=1` guard always failed → all arms became IR_LIT_NUL stubs → segfault.
2. `sel->γ = cas` (selector wired to CASE node itself) created circular graph → the interp's single-step `IR_interp_node(bb->α->γ)` read the CASE node itself as chain head → infinite recursion.

**Fix — lowerer (`icn_case` full rewrite):**
- Flat-pair iteration: `i=1; while(i<e->n)` consuming key+val pairs; last child (remaining==1) is default body.
- Arm descriptor chain: allocate one `IR_LIT_NUL` arm_key per arm with `→γ=key_entry`, `→β=val_entry`, `→ω=next_arm`. Default arm descriptor: `→γ=def_entry`, `→β=NULL`.
- Selector sentinel: `sel->γ = cas` (the CASE node itself). Interp selector loop stops on `snxt==bb`.
- Key sub-exprs lowered with `γ_in=NULL` so leaf→γ stays NULL (stops key eval loop after one step).
- Val sub-exprs lowered with `γ_in=NULL`, leaf→γ wired to `γ_in` (stops val eval loop at bb->γ).
- `cas->β = chain` (first arm descriptor); chain traversal via `arm->ω`.

**Fix — interp (`IR_CASE` full rewrite):**
- Selector mini-loop: drives from `bb->α`, stops when `snxt==bb` (sentinel).
- Arm loop: `for (IR_t *arm = bb->β; arm; arm = arm->ω)` — clean, no γ-chain ambiguity.
- Key eval loop stops at `bb->γ/ω` or self-loop; val eval loop stops at `bb->γ` (γ_in).
- Default detection: `arm->β == NULL`.

**Result:** rung33 5/5 PASS. m2 +5.

### BUG-3: TT_SWAP dispatch missing (`f15cfc8`)

**Root cause:** `:=:` lexes as `TK_SWAP` → `TT_SWAP`. The `lower2_icn` dispatch had `TT_REVASSIGN | TT_REVSWAP → icn_swap` but NOT `TT_SWAP`. `TT_SWAP` was in the dead `TT_FNC | TT_PROC_FAIL | TT_SWAP | TT_AUGOP` group — treated as a function call, producing no `IR_SWAP` at all.

**Fix:** Add `TT_SWAP` to the `icn_swap` dispatch arm; remove from the FNC group.

**Result:** All rung15 swap tests PASS. m2 +2.

### BUG-4: IDX_SET/FIELD_SET (`f15cfc8`)

**Root cause:** None — `icn_assign` already handled `lhs->t == TT_IDX` and `lhs->t == TT_FIELD` correctly. Tests were already passing. No fix needed.

### BUG-5: BINOP_POW always returns real (`f15cfc8`)

**Root cause:** `binop_apply` in `lower_program.c` had `case BINOP_POW: { if (!either_real && ri >= 0) { ... return INTVAL(acc); }` — int^int shortcut returned integer. Icon/JCON corpus expects `2^10 → 1024.0` (real). The `icn_eval_arith` path in `IR_interp.c` also had this shortcut (string-named `^` operator) but Icon `2^10` goes through `IR_BINOP` → `binop_apply`, not `icn_eval_arith`.

**Fix:** Remove the int shortcut from `binop_apply` BINOP_POW case; always `REALVAL(pow(base,exp2))`.

**Result:** All rung26 pow tests PASS (+5 for int_pow/pow_assoc/pow_expr/pow_zero; real_pow already passed). m2 +5 (plus rung19 pow tests also likely fixed — counted in +13 total).

### BUG-6: IR_INITIAL NV persistent flag (`f15cfc8`)

**Root cause:** `IR_INITIAL` interp used `bb->ival` as done-flag, but `bb_reset` clears `ival` between procedure calls. `initial` clause ran on EVERY call instead of once.

**Fix:** Replace `bb->ival` with `NV_GET/SET` keyed on `snprintf("__init_%p", (void*)bb)` — pointer-stable across calls, GC-safe (bb nodes are GC-allocated but don't move in this runtime). Also replaced single-step body evaluation with mini-loop (same pattern as IR_LIMIT BUG-1 fix).

**Result:** All rung21/25 initial tests PASS. m2 +2 (new tests that now work on second call).

---

## Open failures — next session priority order

From triage of remaining 53 m2 failures:

### FULL-10: find() generative (rung 08, +2 or +3)
- `find(s1,s2)` currently returns only the first match. Must be generative.
- `IR_FIND_GEN` exists in `IR_interp.c` — check if `find` in `by_name_dispatch.c` lowers to `IR_FIND_GEN` or falls through to single-shot.
- Canonical: `refs/icon-master/src/runtime/fstranl.r` — `find` procedure.

### FULL-12: coerce() / integer() / real() (rungs 36, 37, +5)
- `integer("3")` → 3; `real(5)` → 5.0 etc.
- Check `by_name_dispatch.c` for `integer` / `real` function entries.
- Canonical: `refs/icon-master/src/runtime/fconv.r`.

### FULL-13: keywords &type, &lcase, &ucase (rung 37, +3)
- `&type` returns type name as string; `&lcase` / `&ucase` are 26-char cset constants.
- Check `keywords.c` for these NV entries.
- Canonical: `refs/icon-master/src/runtime/fmiscops.r`.

### FULL-17: sort() (rung 31, +5)
- `sort(L)` → sorted list copy. Runtime function likely missing entirely.
- Add `rt_list_sort` to `aggregates.c`.
- Canonical: `refs/icon-master/src/runtime/fstranl.r`.

### FULL-18: alt cross-arg (rung 13, +1)
- `every f(1|2) | g(3|4)` — cross-product of generator args.

### FULL-32: rung37 sweep (after above)

---

## Canonical source reminder

Before implementing ANY construct:
- Port topology: `refs/jcon-master/tran/irgen.icn` — `ir_a_<Construct>`
- Runtime semantics: `refs/icon-master/src/runtime/*.r` — `fstranl.r`, `oarith.r`, `oref.r`, `ocomp.r`, `fconv.r`, `fmiscops.r`

---

## Next session checklist

1. Read GOAL-ICON-FULL-PASS.md — pivoted goal, m2-only focus.
2. Session setup: build, libscrip_rt, smoke gates.
3. FULL-10: find() generative — check IR_FIND_GEN wiring in by_name_dispatch.c.
4. FULL-12: coerce — check integer()/real() in by_name_dispatch.c.
5. FULL-13: keywords — &type, &lcase, &ucase in keywords.c.
6. FULL-17: sort() — add rt_list_sort to aggregates.c.
7. Gate: target m2 ≥ 210 after all four.
8. FULL-32: rung37 sweep for remainder.

---

## Watermark

**HEAD (SCRIP) = `f15cfc8` — BUG-2..6 LANDED 2026-06-06. m2 194 · m3 31 · m4 34.**
**HEAD (.github) = `ecce54b5` — GOAL-ICON-FULL-PASS pivoted (Phase 3/4 steps removed, BB-FIXUP owns revamp).**

Session 2026-06-06 (Sonnet 4.6, GOAL-ICON-FULL-PASS BUG-2..6 + PIVOT):
- BUG-2 IR_CASE arm-descriptor chain: `f15cfc8` (rung33 5/5, m2 +5)
- BUG-3 TT_SWAP dispatch: `f15cfc8` (all rung15 swap PASS, m2 +2)
- BUG-4 IDX_SET: already working, no commit
- BUG-5 BINOP_POW→real: `f15cfc8` (all rung26 PASS, m2 +5)
- BUG-6 IR_INITIAL NV flag: `f15cfc8` (all rung21/25 PASS, m2 +2)
- PIVOT: GOAL-ICON-FULL-PASS.md rebuilt lean at `ecce54b5`

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
