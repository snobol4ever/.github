# FINDING-2026-08-03-CLAUDE-SN4-OMEGA-ZW16: blob-context op_zw staging attempted and reverted — r12 not coherent across backtrack re-entry, CAPTURE_SAVE/COND arm mismatch

**Session:** s37 (2026-08-03, Sonnet). **SCRIP parent:** `53705cf1` (ZW-15). **Commits from this session:** none (revert; finding in doc + cursor only).

## What was attempted

The OMEGA s36 cursor named the next rung as "blob-context op_zw staging": blob-member nodes (IR_MATCH_ASSIGN_COND, IR_MATCH_ASSIGN_SAVE executing as off-run operand-closure members inside a canonical-frame-armed run) see `op_zw=0` at their drive choke because they are never staged through the per-run zd_plan path that sets `zzw[i]=1`. MATCH_END's op_zw arm reads `r12` as the CAS top, but blob CAPTURE_COND writes to `RT_CAS_TOP` (cell-resident path, `op_zw=0`). Mismatch loses all captures on `nblob_real>0` programs.

**Attempt:** In `emit.cpp` zd_plan blob-member loop (line 2041), propagate `zzw[k]=1` for each blob member `cm[k]` when the run is canonical-frame-armed (`zws=1`), behind killswitch `SCRIP_ZW_BLOB=1`. In `emit.h`, add `zw_blob_on()` and widen `zw_nblob_ok()` to admit `nblob_real>0` when `SCRIP_ZW_BLOB=1`.

**Confirmed ZWS effect:** Under `SCRIP_ZW_BLOB=1`, 73 programs that were `DECLINED: blob-clause` (nblob_real>0) became ARMED. Example: `044_pat_pos` DECLINED → ARMED.

## Gate result (SCRIP_ZW_BLOB=1 vs baseline)

**m3:** 281→279 (−2): `152_pat_json_keyvalue_renamed` (bistable ASLR flip, pre-existing), `156_pat_cap_alt_abandon_pop` (**NEW P→F**).
**m4:** 274→273 (−1): `156_pat_cap_alt_abandon_pop` (**NEW P→F**), `162_pat_arbno_null_body_guard` (**NEW P→F**). **F→P:** `164_pat_arbno_nested` (net zero benefit).

**REVERTED.** Two net-new correctness regressions. Baseline m3 281/25F/11T · m4 274/31F/11T/1L restored byte-identically.

## Root cause 1 — r12 not coherent across ALTERNATE backtrack cycling (156)

156 `'ab' ? ('ab' . V1 | 'a' . V2) 'b'`: the ALTERNATE has two arms, each with a CAPTURE_SAVE + CAPTURE_COND pair. Under `op_zw=1`, CAPTURE_COND's γ arm does `add r12, 24` (push CAS entry) and its β arm does `sub r12, 24` (pop). This is balanced **within one arm's execution**. But ALTERNATE's β re-entry fires the failed arm's CAPTURE_COND β **before** MATCH_BEGIN's β restores `r12 ← [rbp-40]` (cas_base). So when arm-1 fails and ALTERNATE drives the arm-1 COND-β, r12 still reflects whatever the arm-1 COND-γ left — the sub undershoots by 24 × (however many entries COND-γ pushed). Subsequent arm-2 COND-γ then writes at the wrong r12 position, corrupting the CAS stack. **Correct fix:** ALTERNATE needs its own RBP frame that saves/restores r12 at each arm boundary — Lon's mechanism-2 (nested RBP frame at the indeterminacy boundary) verbatim.

## Root cause 2 — CAPTURE_SAVE uses C array path, CAPTURE_COND reads uninitialised ZD cell (156, 162)

The CAPTURE_COND ZD arm reads `ZOPD(1,0)` = `op_zread[0]` from SAVE's "cell" (the depth-delta between COND and SAVE in the ZD run). But blob-member CAPTURE_SAVE is **not ZD-admitted** (`zd_on[k]=0`, rpos[k]<0); it takes the `sfc()` or `rt_cap_push` path. It never writes a cell at `ZOPD(1,0)`. COND then reads `dword ptr [rsp + 0]` — an uninitialised claim slot — as the SAVE delta, computing the wrong match length. **Correct fix:** CAPTURE_SAVE inside the blob must be ZD-admitted for COND's `ZOPD(1,0)` read to be valid. This requires SAVE to be in the run (rpos[k]>=0), which is precisely what happens when ALTERNATE/ARBNO get their own mechanism-2 frames and their interior becomes a separate run with proper ZD planning.

## Architectural interpretation (Lon's HQ ruling confirmed)

Both root causes resolve to mechanism-2. The blob interior cannot coherently use r12-direct CAS without a frame at every indeterminacy boundary inside the blob:

- **ALTERNATE** = indeterminacy boundary (which arm succeeds is runtime-variable). Mechanism-2: RBP frame in ALTERNATE's α that saves r12; each arm-entry restores r12 from frame; arm-β pops; whack at ALTERNATE-ω.
- **ARBNO** = indeterminacy boundary (how many iterations is runtime-variable). Mechanism-2: same nested frame around each ARBNO body.

The `nblob_real>0` population (73 programs) is exactly the worklist for mechanism-2 placement. Each program's blob closure audit names which boundary needs the frame.

## What IS safe today (nblob_real==0, 49 programs)

The gate `nblob_real==0` correctly identifies programs where all blob closure members are K=0 scanner-register-only kinds (IR_MATCH_LIT/POS/RPOS/LEN/ANY/NOTANY/REM etc. with `zls_node_off` returning the elided sentinel). These have no CAPTURE_COND/SAVE in the blob, no r12 writes, no depth-fragile reads. The canonical ZW-15 frame is correct and safe for all 49. Gate stays at `nblob_real==0`.

## Next rung (OMEGA worklist)

Mechanism-2 landing in ALTERNATE's template (`bb_match_alternate.cpp`): RBP frame at ALTERNATE-α saving r12 = current CAS top; each arm-entry restores from frame cell; ALTERNATE-ω whacks frame. This is the same structure as MATCH_BEGIN's frame (ZW-1/ZW-15), one level deeper. Once ALTERNATE has its frame, CAPTURE_COND inside alternate arms sees r12 coherent at both γ and β — root cause 1 cured. Root cause 2 resolves when the ALTERNATE-framed interior becomes a clean sub-run with ZD planning.

**WATERMARK (s37, HEAD unchanged `53705cf1`):** m3 **281/25F/11T** · m4 **274/31F/11T/1L** · armed match programs **49** · push_rbp **326** · rsp_mark/patstk_mark **132** · UCLAIM-head **174** · blob-clause declined **73** · fused-terminal **0** · bench **18/21**.
