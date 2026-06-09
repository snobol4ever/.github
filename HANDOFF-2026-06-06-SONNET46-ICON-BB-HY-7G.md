# HANDOFF — 2026-06-06-g · Sonnet 4.6 · GOAL-ICON-BB · HY-7g gvar/frame-var producer boxes

**Landed:** SCRIP `bc95d97`
**Columns:** m2 143 HARD · m3 31 · m4 41 (baseline identical to HY-7f — hygiene step, no new native coverage)

## What landed

**DUP-FORM-3 de-fuse (HY-7g):** gvar/frame-var reads promoted to producer boxes; operand-kind
arms deleted from `marshal_call_arg`; gamma-chain walk deleted from `marshal_varparam_addr`.

**`emit_bb.c`**
- `gvar_callarg_admit`: widened from {LIT_I, LIT_S, LIT_F, LIT_NUL} to also admit
  `IR_VAR_FRAME`, `IR_VAR_FRAME_REF`, and `IR_VAR` (non-`&`-keyword, terminal).
  These now flow through `gvar_drive_call_arg_slots` → `walk_bb_flat` as producer boxes.
- `IR_VAR` `walk_bb_node` case: added `g_gvar_flat_chain && sval && sval[0]!='&'` branch
  that calls `bb_slot_alloc16(nd)` + sets `op_sval`. Enables the new `bb_var` arm.

**`bb_var.cpp`**
- New arm: `g_gvar_flat_chain && op_off >= 0 && op_sval`: emits `NV_GET_fn` call,
  stores 16-byte DESCR result in `[r12+op_off]`, four-port wiring. Mirrors `bb_var_global`.
  Sealed RO name data via `x86_ro_seal_str(0, op_sval)`.
- Added `x86_begin()` to entry point: without it, TEXT-mode `x86_internal_name()` returned
  stale UID for all invocations, producing duplicate `.Lx*` labels that failed `as`.
  `x86_begin()` is a no-op in BINARY mode (safe for all existing arms).
- Previous `g_gvar_flat_chain` pass-through retained for keywords (sval[0]=='&') and
  any unslotted case.

**`bb_call.cpp`**
- `marshal_call_arg`: added `bb_slot_get(lf) >= 0` fallback block immediately after the
  owner-guard. Handles nested `marshal_single_call` args whose producer boxes were
  pre-emitted (slot recorded in `g_bb_slotmap`) but not in `_.op_arg_slot[]`.
- **DELETED** inline `IR_VAR`, `IR_VAR_FRAME`, `IR_VAR_FRAME_REF` operand-kind arms from
  the `if (g_gvar_flat_chain)` block. DUP-FORM-3 fusion eliminated.
- `marshal_varparam_addr`: `while (fin && fin->γ ...)` gamma-chain walk deleted.
  `lf` is used directly. The `lf->t` kind-dispatch (frame/ref/global) is retained —
  this is the correct address-computation switch, not fused consumer logic.

## Proof
- SNOBOL4 `DEFINE('DOUBLE(X)')` → `DOUBLE(A)` → m2==m3==m4=42 (gvar as proc arg).
- TEXT (m4) assembles cleanly: no duplicate `.Lx*` labels.
- Suite: 143/31/41 · smokes icon 12/10/10, sno FAIL=0, prolog 5/4+exc/5, broker 32/35.
- FACT 0 · no_stack 0 · g_vstack 0 · one_reg 0 · one_box PASS.

## Next: ICN-HY-FENCE

HY-7g unblocks HY-FENCE. The FENCE gate is `scripts/test_gate_bb_one_box.sh`. It currently
covers Prolog-owned files only. Extend it to Icon-owned files.

**Pre-audit (already clean):** every Icon-owned BB template has exactly 1 `extern "C" void bb_*`
entry (boxes) or 0 (helpers). Verified manually across all families:
  Boxes (1 each): bb_alt, bb_every, bb_gen_scan, bb_iterate, bb_keyword, bb_lit, bb_lit_scalar,
    bb_return, bb_succeed, bb_to, bb_unop, bb_var, bb_var_global, bb_var_frame, bb_var_frame_ref,
    bb_assign_frame, bb_assign_frame_ref, bb_assign_local, bb_call, bb_callee_frame,
    bb_scan_{any,bal,find,many,match,move,pos,stmt,tab,upto}, bb_binop_{arith,concat_slot,
    gvar_arith,gvar_arith_slot,gvar_relop,relop}, bb_gvar_assign{,_lit_i,_lit_s},
    bb_det_{nl,write}, bb_gather, bb_subject, bb_match.
  Helpers (0 each): bb_call_{fn,proc_staged,userproc,write_slot}.
  NOT in scope (SNOBOL4/Pascal-owned): bb_pat_*, bb_cell_*, bb_callee_frame (Prolog).

**HY-FENCE steps:**
1. Add the Icon BOX file list to `test_gate_bb_one_box.sh` (expect 1 per file).
2. Add the Icon HELPER file list (expect 0 per file).
3. Update gate header comment.
4. Run gate: must show PASS.
5. Add gate to Session Setup gate list in GOAL-ICON-BB.md.
6. Mark HY-7g + HY-FENCE done in GOAL-ICON-BB.md; delete completed rungs per Lon directive.
7. Update watermark. Commit + push both repos.
