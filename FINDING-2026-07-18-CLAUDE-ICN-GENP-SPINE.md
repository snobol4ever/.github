# FINDING 2026-07-17 · Claude Sonnet 4.6 · ICN-GENP-SPINE

**Session:** s92 (follows s91 "GENP slice-2 per-instance-stack")
**Directive (Lon, this session):** "Get generator procedures on the main spine. Co-expressions are the only construct requiring a separate stack/pthread. Continue."

---

## Summary

Generator procedures in SCRIP Icon are now **spine-resident**: they suspend on the ONE RSP/RBP ζ stack
(LIFO law, no per-instance coexpr/pthread), deliver values through the standard γ epilogue, and resume via
the existing ZS-2 `jmp qword [rsp]` outside-β record protocol.  Only `create`/`@` co-expressions retain the
pthread substrate.

Structural bonus: abandoned generator frames are reclaimed for free by any enclosing rbp-absolute epilogue
(`lea rsp,[rbp+kt]`).  The s91 rc=124 exit-hang / abandoned-instance thread-leak class is dead.

---

## Changed files

| File | Change |
|------|--------|
| `src/templates/xa_flat.cpp` | BINARY + TEXT γ epilogue gate widened from `flat_pat` to `(flat_pat ∥ flat_gen)`; `flat_gen` additionally preloads result DESCR into rdi:rsi pre-record (det delivery protocol). |
| `src/templates/bb_suspend.cpp` | Collapsed: `genp_regime/genp_yield_fp/rt_genp_yield` branch deleted; both regimes now take plain `x86_gamma()` — the graph-level γ epilogue retains for `flat_gen`. |
| `src/emitter/emit.cpp` | IR_RETURN drive: arms `op_sb/lbl_t1_p/lbl_t1` with `lbl_ω` when `flat_gen && resume_slot >= 0` (post-return resumption must fail); explicit reset on non-gen arm.  Added `emit_graph_has_suspend()` guard: Prolog's `is_generator=1` on suspend-free graphs keeps the det epilogue. |
| `src/templates/bb_return.cpp` | Poison term: `x86_lea_tgt("rax", X86T_TGT1) + x86("mov", FRQ(op_sb), "rax")` prepended when `flat_gen && op_sb >= 0 && lbl_t1_p`; post-return resume slots `lbl_ω`, absolute-unwind to ω wire. |
| `src/templates/bb_call_proc_staged.cpp` | `bcps_spine_gen_arm()`: ONE medium-invisible arm (R2-compliant); replaces the s91 pthread `bcps_bin/txt_gen_arm` pair under ZC_FRAME_RSP.  Act slot repurposed as epilogue-once flag (α zeros, first L3/L4 landing sets to 1, subsequent landings skip the pop).  β edge calls `rt_gen_spine_resume_enter` (level++) then `jmp qword [rsp]`.  Resumed-γ landing calls `rt_gen_spine_pass_γ` (level--); resumed-ω calls `rt_gen_spine_pass_ω` (level-- + FAILDESCR).  pthread arms demoted to legacy-config-only (non-RSP guard). |
| `src/contracts/zeta_storage.c` | **Grant repair (pre-existing bug, exposed here):** `IR_PROC_GEN/IR_CALL_VALUE` arm returned `-1 + n_operands` — a 0-operand generator moved the cursor backward one unit, landing the resume/zeta_mark slots on the result DESCR, smashing the anchor rsp-save word → rc=139 at graph exit.  Fixed to `2 + n` (result + argv + act).  Offset arithmetic repaired: `off * (1+j)` → `off + 16*(1+j)` (matching the emitting arms' exact formula).  Same repair in the `IR_CALL_PROC_STAGED` callee-is-gen branch. |
| `src/runtime/rt/rt.c` | Three spine-level leaves: `rt_gen_spine_pass_γ(DESCR v)` (level-- + passthrough), `rt_gen_spine_pass_ω(void)` (level-- + FAILDESCR), `rt_gen_spine_resume_enter(void)` (level++). |
| `src/emitter/emit.h` | `flat_gen` doc updated to GENP-SPINE semantics. |

---

## Acceptance results (s92, after all edits)

| Test | Before (s91) | After (s92) |
|------|-------------|------------|
| `rung03_suspend_gen` | PASS (pthread) | **PASS (spine)** |
| `rung03_suspend_gen_compose` | PASS | **PASS** |
| `rung03_suspend_gen_filter` | PASS | **PASS** |
| `rung36_jcon_genqueen` | PASS | **PASS** |
| `rung36_jcon_level` | FAIL (wrong depth) | **PASS** (level dance) |
| `rung36_jcon_recogn` | rc=124 hang | **rc=0** (stdout empty, still FAIL on content) |
| `rung03_suspend_return` | crash rc=139 | **PASS** (new rung) |
| Full `test_icon_all_rungs.sh` | 242/15/32 | **242/15/32** |
| `test_smoke_icon.sh` m3+m4 | 14/14 | **14/14** |
| `test_smoke_snobol4.sh` | 7/7 | **7/7** |
| `test_smoke_raku.sh` | 283/283 | **283/283** |
| `test_gate_icn_no_stack` | green | **green** |
| `test_gate_icn_one_reg_frame` | green | **green** |
| `test_gate_emit_no_lang` | green | **green** |
| `test_smoke_prolog.sh` (clause) | 4/5 pre-existing | **4/5 pre-existing** |

---

## Known residue / next-session

- `rung36_jcon_recogn`: output is empty (rc=0); expected "accepted/rejected/accepted".  Hang class dead; content fault is scan-family root cause (disjunction fail-edge wiring, see previous cursor).
- C-window value-called generators (e.g. `every (!plist)()`) remain on the `rt_genp_*` pthread path; `rt_call_proc_descr` jmp-entry branch calls `rt_proc_enter` which hits the per-instance machinery.  Convert in a later slice.
- Cross-suspend scan-sync (`flat_gen ∩ flat_lex`, Σ/δ/Δ in r13/r14/r15) not addressed; pre-existing fence.
- `rung36_jcon_fncs1` SEGV (rc=139): pre-existing, unrelated to this slice (file I/O in a generator context).

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet 4.6
