# ARCH-ICON.md — Icon Frontend and BB Execution (register truth for ALL BB codegen)

Frontend: Icon → shared IR. See ARCH-IR.md. This file also carries the LIVE REGISTER CONTRACT that every BB template (all languages) obeys.

## Execution model
Icon is goal-directed: every expression Succeeds (γ, may resume for more) or Fails (ω). That IS the Byrd Box four-port model — α start · β resume · γ succeed · ω fail. Icon uses BB_PUMP (generate until ω); SNOBOL4 uses BB_SCAN (try each cursor position).

**STACKLESS (GROUND ZERO 3).** Icon emits ZERO SM opcodes, no value stack, no r12-TOS, no rt_push/pop. Each box's value lives in a flat per-box DATA slot; consumers read operand boxes' slots directly (Proebsting: `plus.value ← E1.value + E2.value`). Unbounded backtrack state (ARBNO, recursion) = per-box .bss arena by depth. Inter-box transitions are direct `jmp`. Reference embodiment: `corpus/probe/bb/test_icon.c`.

**Relational ops are NOT booleans** — a comparison is a {0,1} generator: γ yields a value, ω fails; constructs only choose where γ/ω go (verified vs canonical `ocomp.r` and JCON `ir_opfn`).

## Variable model (Lon 2026-06-03) — two backends, switch-selected, BOTH kept
- OLD per-procedure frame slots (`g_bb_varslot`, `[r12+off]` historically) — fast, per-graph namespace.
- NEW shared NV dictionary (`NV_GET_fn`/`NV_SET_fn`, same hash dict as SNOBOL4/Snocone/Rebus) — one cross-language global namespace. Only the GLOBAL arm of IR_VAR/IR_ASSIGN reroutes; locals stay frame slots. Kept side-by-side for A/B perf + standalone-Icon compilation. Ladder: `GOAL-ICN-GLOBAL-NV.md`.

## ⛔ REGISTER CONTRACT (CORRECTED 2026-07-18; verified vs live x86_asm.h + zeta_choices.h)
- ζ frame selection = `ZC_FRAME` build constant, default `ZC_FRAME_RSP` (s65 R12-ERAD). `x86_zr()` = **RSP** (FORTH-style port cells + carve discipline, shared with C stack).
- `x86_fb()` = **PER-GRAPH (s197 FLATDISP-8):** RBP for graphs whose prologue pins it (`emit_jmp_pin_rbp()` = flat_deep_arrival || flat_pat || flat_gen — suspended generators, pattern blobs, deep arrivals; `xa_flat` emits `mov [rsp+kt-8],rbp; mov rbp,rsp`); RSP for depth-static graphs (rbp untouched, `op_flat_disp` compensation on the rsp arm). ONE selector `x86_fb_pinned()` feeds all accessors in BOTH media. `ZC_FRAME_R12` accessor arm DELETED outright (ZR-RSPRBP-1, `da8c2347`); `x86_r12_modrm` renamed `x86_frame_modrm`.
- **R12 is FREE of frame duty** → in SNOBOL4 match code r12 = live DCAP/CAS top (CAS-R12-UNIFY). **R13=Σ subject base · R14=δ cursor (0-based; &pos=δ+1) · R15=Δ subject length.** RO constants sealed `[rip+disp]` (bb_pat_any idiom). Result DESCRs go to the box's own 16B frame slot.
- **RBX = WS/GC bump-frontier TOP** (ZC_PORT_HEAP α-carve, dormant under default ZC_PORT_FORTH where grants spend as `sub rsp,K`). GVA globals address ABSOLUTE (`ABSQ(RT_GVA_VA + k*16)`), no register base.

## String scanning — ICN-SCAN BB family (canonical set closed: fstranl.r any/bal/find/many/match/upto · fscan.r move/pos/tab · control `?` live, `?:=`, `=s` sugar)
Two semantic families (do not blur): position-returners δ-untouched — any/match/many {0,1}; upto/find/bal {*} generators (suspend each position; β re-pumps via bb_to). Cursor-movers reversed-on-resume — tab/move write δ, restore saved δ on β then fail; pos is stateless compare. Genuinely different from SNOBOL4 pattern leaves (which thread the cursor); reuse = Σ/δ/Δ walk + cset test loop.

## Box structure (from corpus/probe/bb/test_icon.c)
```
construct_α: init state; first value; goto γ or ω
construct_β: advance; next value; goto γ or ω
construct_γ: value ready — wire to caller success
construct_ω: exhausted — wire to caller fail
```
State lives in the per-α DATA block; CODE is shared.

## JCON reference
`refs/jcon-master/tran/irgen.icn` — 43 `ir_a_*` procedures; `ir_info(start,resume,failure,success)` = the four-port record. Ground truth for every construct's port topology.

## Co-expressions
LANDED 2026-07-01: create/`@`/coret/cofail via pthread+semaphore (`rt_coexpr.c` + bb_create/activate/coret/cofail), both modes. C-function Byrd constructs remain banned.
