# FINDING-2026-08-08-CLAUDE-SN4-CLIMB-S20: ORIENTATION — PARALLEL SESSIONS LANDED M-2 BUG-3/BUG-4; ROOT CAUSE OF REMAINING 32R DIAGNOSED BUT NOT FIXED THIS SESSION

**Session:** CLIMB s20 · **Date:** 2026-08-08 · **Author:** Claude Sonnet 4.6

---

## SITUATION AT OPEN

GOAL-SN4-ZETA-CLIMB LIVE CURSOR (s19) claimed m3 124/1/0/17 · m4 123/3/0/16 — local unpushed commits that never reached origin. Fresh clone showed origin HEAD `709d5f19` (RC-1). Actual probe suite at session start: m3 61/2/0/80 · m4 106/4/0/33.

During diagnosis, parallel MECH sessions (Opus) landed:
- `d2872e69` CLIMB-RSP-FIX: bb_match_begin β restores RSP before start_δ access; m3 61→128/2/0/13
- `1bbe3370` M-2 BUG-3: broaden zdh_match to all MATCH_BEGINs — G/H/D/N/X class 47-probe fix
- `2829ce8e` M-2 BUG-4: mirror fc_tail_head in MATCH_END hfc condition (ARBNO class partial)

After pulling and rebuilding: **m3 109/2/0/32 · m4 110/3/1-flaky/29**. SCRIP `27a207c2` · corpus `ba057fc4`.

---

## ROOT CAUSE DIAGNOSED THIS SESSION (the pre-MECH-fix 80R class)

### Monitor trace

PARTICIPANTS="spl scr" on A10 (`POS(0) ('ab' | 'xy' | 'pq') $ OUTPUT` on `'zzzz'`): PARTIAL EOF at step 4 — scrip crashes while SPITBOL still emitting on `LABEL stno=INT=5`. GDB: rsp = `0x7ffffbffeff0` (corrupted, ~4MB off). rc=139 SIGSEGV.

### Root cause

M-2 HFC-WINDOW (`9368fac6`) expanded MATCH_BEGIN's hfc claim from `sub rsp,32` to `sub rsp,80` inside `bb_match_begin.cpp` via `x86_zclaim(80)`, gated `ZC_FRAME_RSP && hfc()`. This carve bypasses `x86_alpha()` entirely — `op_fc_bytes` stays 0, `op_zdepth` is never told about the 80B.

Downstream pattern nodes (ALTERNATE, LIT_INTEGER, ASSIGN_SAVE, FENCE0/1, ARBNO etc.) use `FRQ(op_off)` which resolves via `x86_zop` → string `[rsp + N]` → parse → `x86_frame_off(N)` = `N + op_zdepth + op_flat_disp`. Since `op_zdepth = 0` for ALTERNATE (zero-cell), `op_flat_disp = 0` (CARVE-DATA-ERAD), the 80B is invisible. Every FRQ address lands 80B above the ZLS-allocated slot — overwriting MATCH_BEGIN's PATCTX save zone (`[rsp+48..72]` = outer r13/r14/r15/capgen) → SIGSEGV.

This explains all 80 regressions (D/F/G/H/N/X/A families) — all contain pattern nodes inside an hfc-bearing MATCH_BEGIN bracket. The MECH sessions diagnosed the same root cause independently and fixed it via zdh_match broadening and RSP restore in β.

### Fix attempted (reverted at handoff)

Added `int op_hfc_depth` persistent field to `sm_emit_t` (emit.h), staged 80 at MATCH_BEGIN, 0 at MATCH_END, added to `x86_frame_off` rsp arm. A10's ALTERNATE offset: 192 → 272 (+80). Still crashing — A10 has an additional pre-existing 48B deficit from sibling live cells (VAR=16 + LIT_INT=16 + ASSIGN_SAVE=16) that `op_zdepth` does not account for. Reverted cleanly to HEAD.

**Key double-count trap:** Must NOT add `op_hfc_depth` to both `x86_zop` string construction AND `x86_frame_off` at encode time — both paths add it, yielding double-count (192+80=272 in string → x86_frame_off(272)+80=352). Only `x86_frame_off` is the correct single site.

### A10 pre-existing 48B deficit

A10 crashed at every commit tested back to `a8661ef3` — it was always in the 112R floor. The sibling-cell gap: with `op_flat_disp=0` (CARVE-DATA-ERAD) there is no running depth prefix for non-zd pattern nodes. A10's ALTERNATE needs `[rsp + 192 + 128]` = `[rsp + 320]` (128B = 80B hfc + 16B LIT_INT + 16B ASSIGN_SAVE + 16B VAR) but gets `[rsp + 272]` with only the 80B fix. This may be a MECH structural gap or Lon may have an alternative accounting for it.

---

## REMAINING 32R CLASS

After M-2 BUG-3/BUG-4 landed, 32R remain in m3. Per the Opus s20 cursor: D02/D03/D04 (heap-exhaust, structural MECH), D06/D07/D08 (COERCE sequencing, MECH-blocked), plus ARBNO ZD arm / ZOPQ offsets / teardown class (BUG-2 cross-requests from s19). These are not CLIMB correctness items — they are MECH structural items.

---

## WATERMARK AT CLOSE

m3 **109/2/0/32** · m4 **110/3/1-flaky/29** · SCRIP `27a207c2` · corpus `ba057fc4` · no code commits this session.

D05 (*VAR holding SEQUENCE) is flaky m4 (XPASS when run serially, REGRESSION in some invocations). Kept in XFAIL.compile — not actioned.
