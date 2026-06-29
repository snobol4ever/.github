# HANDOFF — 2026-06-29 — Sonnet 4.6 — GZ#5 enum amputation (68 members deleted) + branchopt.c removed

## SCRIP HEAD: a0cec369 — pushed to origin/main ✅

---

## Session arc

Two tasks: (1) delete unused IR_e members leaving only the 26 needed by the 87/86 passing
programs; (2) remove branchopt.c per Lon's directive (GROUND ZERO — optimization rebuilt later).

---

## What landed

### IR.h — 68 enum members deleted (94 → 26 + IR_OP_COUNT)

**Keep-set (26):**
IR_LIT_I  IR_LIT_S  IR_LIT_F  IR_VAR  IR_ASSIGN  IR_BINOP  IR_UNOP  IR_CALL
IR_SEQ  IR_FAIL  IR_SUCCEED  IR_GOTO  IR_RETURN  IR_IF  IR_CONJ  IR_EVERY
IR_ALT  IR_NOT  IR_TO  IR_PROC_GEN  IR_KEYWORD
IR_CALL_PROC_STAGED  IR_CALL_USERPROC  IR_CALL_BYNAME  IR_CALL_BUILTIN  IR_CALL_GVAR_USERPROC

**Key finding: IR_UNOP retained.** The prior session's dump-derived list marked IR_UNOP dead;
--dump-ir segfaults on most passers, hiding it. The real regression gate caught it: 5 programs
(write(-x), write(*s), null_test/nonnull) lower through IR_UNOP with the operator token in
op_ival. Its fanned variants (IR_NEG/POS/SIZE/NONNULL/NULL_TEST) remain deleted — lower never
emits those directly.

**binop_cat_t added to IR.h.** The relop/concat/arith binop category discriminant had been
riding on three deleted IR_e values (IR_BINOP_RELOP/CONCAT/ARITH). Folded into a small
`typedef enum { BINOP_CAT_ARITH=0, BINOP_CAT_RELOP=1, BINOP_CAT_CONCAT=2 } binop_cat_t;`
in IR.h. binop_slot_kind() return type changed from IR_e to int; walk_bb_node binop sub-switch
updated to match. This is the B2 fold applied at the discrimination layer.

**ir_is_scan_kind() neutralized** (return 0; no scan kinds remain).

### Files edited to chase compiler breaks

- `src/contracts/scrip_ir.c` — 65 designated-init line-deletes; ir_node_produces_value / jcon_converted_producer / dump-print switch / IR_GEN_SCAN/CALL_DEFINE guards updated
- `src/contracts/IR.h` — enum body; ir_is_scan_kind→0; binop_cat_t added
- `src/emitter/emit_bb.c` — binop_slot_kind returns binop_cat_t; descr_chain_arity rewritten to keep-set only; dead enum conditions sentinel-repointed (IR_OP_COUNT)
- `src/emitter/emit_core.c` — walk_bb_node: dropped IR_LIT_NUL/deleted unary labels; repointed binop sub-switch to binop_cat_t; fixed op_a_slot guard
- `src/emitter/emit_x86_drive.c` — dropped IR_LIT_NUL label; dropped deleted unary labels, kept IR_UNOP+IR_NOT
- `src/emitter/emit_drive.h` — binop_slot_kind declaration int not IR_e
- `src/lower/lower_icon.c` — all build(cx, IR_DELETED, ...) → build(cx, IR_FAIL, ...); IR_UNOP sites restored; scan-name helper neutralized; IR_GEN_SCAN guard → IR_OP_COUNT
- `src/driver/scrip.c` — all deleted conditions sentinel-repointed
- `src/opt/ir_query.c` — ir_is_generator_kind reduced to IR_TO/IR_ALT/IR_PROC_GEN
- `src/opt/branchopt.c` — **DELETED** (git rm)
- `src/opt/branchopt.h` — **DELETED** (git rm)
- `Makefile` — branchopt.c compile recipe removed
- 9 BB templates — dead IR_X conditions repointed to IR_OP_COUNT sentinel:
  bb_assign_local, bb_binop_gvar_arith_slot, bb_binop_gvar_concat, bb_binop_gvar_relop,
  bb_call, bb_gvar_assign, bb_lit_scalar, bb_to, bb_unop, bb_unop_gvar_slot

### branchopt.c removed

bopt_chain() had zero callers (confirmed by grep across all of src/). Already dead after the
GZ reduction. Lon's directive: GROUND ZERO, optimization rebuilt from scratch later. git rm'd
both files, Makefile recipe deleted. No impact on any passing program.

---

## Verification

- **Build:** scrip + libscrip_rt both rc=0, no errors
- **Mutation gate: HARD=4** (unchanged — same 4 sites in resolve_call_kinds_descr)
- **Informational rt_* refs: 20 → 14** (incidental reduction from dead conditions removed)
- **Mode-3 --run: PASS=91/289** (baseline was 87; +4 coincidental gains, zero regressions)
- **Mode-4 --compile→link→run: PASS=90/289** (baseline was 86; +4, zero regressions)
- **Zero regressions confirmed by stash-rebuild-diff** (both modes): every original passer intact
- **Heartbeat:** write("hello world")→hello world, write(1+2)→3, both modes green

---

## What is NOT done / next session

1. **B4 (gate to 0):** 4 remaining mutations in resolve_call_kinds_descr — move call-kind
   classification to LOWER so emit time does not call rt_proc_is_*/rt_builtin_is_*.

2. **Dead BB templates still in Makefile build** (previous session's note): bb_assign_frame.cpp,
   bb_binop_arith.cpp, bb_binop_gvar_arith.cpp, etc. — their IR ops are now deleted so they're
   unreachable dead object code. Can be pulled from the build in a follow-up sweep.

3. **lower_icon.c IR_FAIL reroutes:** the ~20 construct arms now produce IR_FAIL rather than
   their proper ops (while/until/case/scan/section/…). These will be rebuilt as proper
   BB ops as GROUND ZERO fills in new constructs. The FAIL reroutes are correct temporary
   behavior — those programs already FAILed before this session.

4. **Growing the pass set:** the driver owns IR_EVERY/IR_ALT/IR_CONJ/IR_IF/IR_RETURN/IR_TO
   but the corresponding constructs may have lower-side gaps (e.g. IR_EVERY's body wiring).
   Next session can probe which FAIL programs are close to passing.
