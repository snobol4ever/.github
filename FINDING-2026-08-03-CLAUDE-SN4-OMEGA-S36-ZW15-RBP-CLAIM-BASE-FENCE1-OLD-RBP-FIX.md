# FINDING-2026-08-03-CLAUDE-SN4-OMEGA-S36-ZW15-RBP-CLAIM-BASE-FENCE1-OLD-RBP-FIX

**Session:** s36 (2026-08-03, Sonnet 4.6)
**SCRIP parent:** `4bba30c4` (ZW-14 s33b)
**SCRIP commit:** `1b2535b1` ([OMEGA] ZW-15 s36)
**No corpus code commit** (feature regen in SCRIP tree; demo regen in corpus `e23ddf68`)

## Summary

ZW-15: fixed `rbp = claim_base - 8 → rbp = claim_base` in the canonical match frame
(`bb_match_begin.cpp` op_zw arm), corrected frame cell offsets in begin/end, and fixed
`bb_match_fence1.cpp`'s `fence_whack_commit` to read old_rbp from `[rbp-8]` instead of
the stale `[rbp+0]`. Blob-clause veto ATTEMPTED to be lifted but reverted after measuring
a CAS mismatch: blob-member captures write to RT_CAS_TOP (op_zw=0 at blob call site) while
match_end reads r12 (op_zw=1). Gate: m3/m4 HOLD, bench 18/21 HOLD. Push INCOMPLETE —
credential needed.

## §1 Root Cause — The 8-byte Offset

Old frame open: `push rbp; mov rbp,rsp` → `rbp = old_rsp - 8 = claim_base - 8`.
ZW-15 fix: add `lea rbp,[rbp+8]` (using `rbp#` raw escape to avoid XK_FR64 misparsing) →
`rbp = claim_base` exactly. Old_rbp now at `[rbp-8]` instead of `[rbp+0]`.

Consequence:
- `FRQ(blob_off)` under pinned-rbp = `[rbp + blob_off]` = `[claim_base + blob_off]` ✓
- All frame cell offsets shift by −8: r13 `−8→−16`, r14 `−16→−24`, r15 `−24→−32`,
  cas_base `−32→−40`, anchor_snapshot `−40→−48`, start_δ `−48→−56`, cap_gen `−56→−64`
- Whack: `mov rsp,rbp; pop rbp` → `lea rsp,[rbp-8]; pop rbp` (old_rbp now at `[rbp-8]`)
- `ZW_FRAME_K=56` and `ZW_FRAME_TOTAL=64` UNCHANGED — `lea rbp,[rbp+8]` is register-only,
  adds no rsp movement. The depth model is correct.

## §2 bb_match_fence1 Fix

`fence_whack_commit` under op_zw: old code read `[rbp+0]` for old_rbp (activation floor).
With ZW-15, old_rbp is at `[rbp-8]`. Fixed: `RDQ("rbp",0)` → `"qword ptr [rbp# + -8]"`
(rbp# escape, XK_REGDISP dispatch to `x86_reg_disp32_lea64`).

This was the cause of 25 regressions in the first gate run (before the fence1 fix): programs
like 044_pat_pos (previously rpin-armed), 052_pat_arbno, 062_pat_fence_fn_outer, W07_capt_chain,
etc. all crashed or produced wrong output because fence_whack_commit corrupted rsp using
the wrong floor.

## §3 Blob-Clause Gate — Attempted Lift, Reverted

The ZW-15 motivation was that `rbp=claim_base` makes `FRQ(blob_off)=[claim_base+blob_off]`
correct for any nblob_real, potentially retiring the `nblob_real==0` gate in `zw_nblob_ok`.
**Attempted**: set gate to always return 1. **Result**: 25 new failures including 044_pat_pos,
W07_capt_chain, 052_pat_arbno — programs with nblob_real>0 that were previously blob-clause
declined, now armed under op_zw but failing to commit captures.

**Root cause of the failure**: blob-member templates (CAPTURE_COND, CAPTURE_SAVE) execute
outside the run's staging choke, so they see `op_zw=0`. The `!op_zw` arm writes captures to
`RT_CAS_TOP` (cell-resident). Meanwhile `match_end`'s `op_zw` arm reads from `r12` (live
register). The two sides are mismatched: writes go to the cell, reads come from r12.
**Fix**: restored `nblob_real==0` gate.

The blob-clause veto retirement needs a separate rung: stage `op_zw` to blob-member invocation
contexts, or unify the CAS top source across both regimes.

## §4 Gate (s36)

Bracket: m3 280/35F/2T · m4 275/40F/1T/1L · bench 18/21 EXACT HOLD.
ZW-15 final: m3 281/25F/11T · m4 274/32F/10T/1L · bench **18/21 EXACT HOLD**.
m4 PASS: 274 vs bracket 275 (one bistable ASLR flicker on 062_pat_fence_fn_outer — confirmed
pre-existing by running with SCRIP_ZW_FRAME=0 which gives the same rc=139 behaviour).
BY SET: zero new failures vs bracket.

## §5 Watermark (s36)

Same as s33b/s35 on the armed-count axes; the gate improvement is correctness (slot offsets
fixed, fence1 whack fixed) not armed-count expansion. The rbp=claim_base fix benefits ALL
49 already-armed programs silently (their slot reads are now 8 bytes more correct under the
pinned-rbp arm, though the old code happened to work because the ASLR-determined overlap was
benign for those programs). push_rbp and rsp_mark watermarks: unchanged at 326/132.
