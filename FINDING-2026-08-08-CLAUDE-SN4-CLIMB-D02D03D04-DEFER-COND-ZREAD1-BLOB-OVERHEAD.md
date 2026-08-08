# FINDING: C-6 D02/D03/D04 — COND after DEFER op_zread[1] blob-overhead correction

**Date:** 2026-08-08  **Session:** CLIMB s18 (Sonnet 4.6)

## Summary

D02/D03/D04 m3-only: `*P . OUTPUT` / `*P $ OUTPUT` / `POS(0) *P $ OUTPUT` where P is a compiled static
pattern — match succeeds, captured string is empty. Root cause: the ZD planner stages COND's cross-read
offset to SAVE's cell (`op_zread[1]`) without accounting for the DEFER blob's runtime stack overhead.
Fix: add `((48 + jcon_value_region + 15) & ~15) + 16` to `op_zread[1]` at COND/IMM emit time when the
predecessor is MATCH_DEFER with a registered PAT$ blob.

## Mechanism

ZD arms MATCH_ASSIGN_SAVE (K=16, writes ZRESD(0)=r14d at SAVE's α) and MATCH_ASSIGN_COND/IMM (K=0,
reads ZOPD(1,0)=[rsp+op_zread[1]] at COND's α). The staging loop at emit.cpp:2754 sets
`op_zread[1] = zd_out[COND] - zd_out[SAVE]`. MATCH_DEFER is K=0 and NOT admitted to the ZD run
(pat_static=0 ∧ SCRIP_ZD_PATREF default off → zdyn veto fires at the planner). So the planner sees
SAVE and COND as adjacent (no depth between them), stages `op_zread[1] = 0`.

At runtime, DEFER's blob runs between SAVE's α and COND's α:
- Blob prologue: `sub rsp, flat_frame_bytes` = `(48 + jcon_value_region + 15) & ~15` bytes
- proc_γ push pair: `push rbp; push rax` = 16 bytes
- Total overhead: `flat_frame_bytes + 16`

For D02's LEN(1) blob: jcon_value_region=48, flat_frame_bytes=96, total=112. Confirmed by
SCRIP_RSPDIFF=1: `save - g4 = 0x70 = 112`.

COND's template emits `mov eax, dword ptr [rsp + op_zread[1]]` = `[rsp + 0]` → reads RSP itself
(SAVE's cell is 112 bytes above). Saved delta = garbage or 0, capture is empty.

## Fix

`emit.cpp` lines 988–989, `IR_MATCH_ASSIGN_COND` and `IR_MATCH_ASSIGN_IMM` cases: when
`operands[0]->op == IR_MATCH_DEFER` with a named PAT$ operand and a registered blob size, add
`((48 + fb + 15) & ~15) + 16` to `g_emit.op_zread[1]` (ZD arm, op_zres=1) or
`g_emit.op_zdepth` (non-ZD non-cfc fallback). Gate: blob size > 0, predecessor is MATCH_DEFER
with LIT_STRING operand naming a registered proc. Byte-identical when no such predecessor.

## Verification

D02 (`*P . OUTPUT`) ✅ D03 (`*P $ OUTPUT`) ✅ D04 (`POS(0) *P $ OUTPUT`) ✅ both modes.
Monitor spl vs scr on D02 pre-fix: diverge step 8 (`scr @7 END` vs `spl LABEL stno=8`).
141-probe suite: m3 140/2/0/0 · m4 139/3/0/0 · 0 REGRESSION. D02/D03/D04 removed from XFAIL.run.

## Classification

CLIMB C-6 defect. ZD planner depth model gap — not a protocol change. No MECH cross-request needed.
m4 unaffected (D02/D03/D04 already pass m4 via a different emission path).
