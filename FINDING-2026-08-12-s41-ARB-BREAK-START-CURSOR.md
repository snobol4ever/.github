# FINDING-2026-08-12-s41: ARB/BREAK `start` cursor aliased by primitive's own `fc_geom` scratch cell

**Seat:** LOWER · **Session:** s41 (Claude Sonnet 4.6) · **Date:** 2026-08-12  
**Status:** ROOT CAUSE CONFIRMED, FIX NOT YET LANDED  
**Witnesses:** `l3_spl_arb_nonterm`, `l3_spl_break_nonterm` (FAIL-silent after s39's L-3b partial fix)

## The bug in one sentence

`MATCH_END`'s `mov eax, dword ptr [rsp + op_fc_disp]` reads the **last match-primitive's own `fc_geom` scratch cell offset+0** — not a stable "match start cursor" — so ARB (which writes its extension counter there) and BREAK (which writes its scan-offset bookkeeping there) corrupt the `start` value that `MATCH_REPLACE` later uses to splice the subject string.

## Measured symptoms

After s39's fix landed (`op_zfc!=0` arm reading `FR(op_off)`/`FRQ(op_off+24)`), `SCRIP_REPL_TRACE=1` on the three FAIL-silent nonterm witnesses shows:

| witness | raw_start | raw_end | expected start | verdict |
|---|---|---|---|---|
| `span_nonterm` | 10 | 14 | 10 | PASS (accidentally correct) |
| `arb_nonterm` | 2 | 14 | 10 | FAIL — reads ARB's extension counter |
| `break_nonterm` | 11 | 14 | 10 | FAIL — reads BREAK's scan-offset state |

`end` is correct in all three. `raw_start` varies by primitive-kind, not by subject content.

## Root cause chain

1. `MATCH_BEGIN` establishes a 32-byte `hfc` frame: `[rsp+0]` = `start_δ` (the unanchored retry cursor), `[rsp+8]` = vacated (W-1c.3), `[rsp+16]` = `rsp_mark`.
2. The unanchored retry loop increments `start_δ` until the pattern's first element succeeds. At `L(0)`, `r14d := start_δ` = 10 (for these witnesses — `ANY('+')` succeeds at position 10 after 10 X's). This is the correct match-start cursor.
3. `x86_gamma()` jumps into the pattern body. Match-primitives (ARB, SPAN, BREAK, etc.) each carve an additional 16-byte `fc_geom` scratch cell via `sub rsp,16`. These carves are NOT popped on the success path.
4. At `MATCH_END`'s α, RSP = MATCH_BEGIN's frame base − 16 (one primitive carve still open). The instruction `mov eax, [rsp + op_fc_disp]` with `op_fc_disp=16` computes the absolute address `RSP + 16` = MATCH_BEGIN's frame base + 0 = `start_δ`'s slot. **This would be correct** — except that each primitive's own `fc_geom` scratch cell (the 16 bytes just carved) overlays the SAME absolute address. The primitive's body has already written into it:
   - **ARB** (`bb_match_arb.cpp`): `mov FR(x86_scratch_off+0), 0` then `add FR(x86_scratch_off+0), 1` per retry. x86_scratch_off = op_fc_disp, so this clobbers `start_δ`'s aliased address. ARB extended twice → counter = 2.
   - **BREAK** (`bb_match_break.cpp`): on success, `mov FR(x86_scratch_off+0), r14d` (stores the post-`ANY('+')` cursor = 11 as its own internal state). Clobbers `start_δ`'s aliased address.
   - **SPAN**: chain-mode arm writes only `FR(x86_scratch_off+4)` = `[rsp+20]`, never `+0`. `start_δ`'s bytes survive → accidentally correct.

## Why SPAN passes and the others don't

Not by design. SPAN's chain-mode arm (`sp_gu()`) happens to use `x86_scratch_off+4` for its backtrack save, leaving `+0` untouched. The aliased `start_δ` bytes (= 10) survive unmolested. This is pure coincidence of SPAN's internal layout — not a principled read of any start-cursor slot.

## Why three fix attempts in s41 failed

`op_zdepth` (what `FR(off)` adds for RSP-relative addressing) is **per-node-local** — "the bytes THIS box carved", not a graph-wide prefix sum. `MATCH_BEGIN`'s `op_zdepth` and `MATCH_END`'s `op_zdepth` are different constants. Using `FR(op_off+8)` at both sites emits `[rsp+8]` at both nodes symbolically, but the absolute addresses differ by the primitive's 16-byte carve — verified empirically: all witnesses regressed to `raw_start=0`.

The correct compensation mechanism is `op_fc_disp`, computed by `fc_walk_range` / `fc_head_register` as the explicit sum of all `fc_geom` K-values in the pattern range. This already correctly compensates the `end` stash: `RDD("rsp", op_off+op_fc_disp+32)` targets the right absolute address for the end-cursor store. The same `op_fc_disp` term, displaced by 8, targets the new `match_start` slot correctly.

## The fix (two lines, two files)

**`bb_match_begin.cpp`** — add immediately after `mov r14d, start_δ`, before `x86_gamma()`:
```cpp
+ x86("note", "match_start") + x86("mov", RDD("rsp", 8), "r14d")
// Gate: only on !stfh() (the hfc 32B-frame arm). stfh() uses a different frame.
// At this exact point in the instruction stream, MATCH_BEGIN's 32B carve is the
// ONLY open carve. [rsp+8] IS op_off+8 with zero further compensation — raw RDD,
// not FR (which would add op_zdepth, wrong).
```

**`bb_match_end.cpp`** — replace `x86("mov", "eax", RDD("rsp", (int)_.op_fc_disp))` with:
```cpp
x86("mov", "eax", RDD("rsp", (int)(_.op_fc_disp + 8)))
// Reads the new stable match_start slot. op_fc_disp already compensates for all
// primitive fc_geom carves open at MATCH_END's α (proven: this is the same term
// that makes the end stash correct). +8 displaces into match_start vs start_δ.
// Only rfc() / ZC_FRAME_RSP arm, op_dval!=0 gate — same as before.
```

## Verification protocol

1. `SCRIP_REPL_TRACE=1` on `arb_nonterm` and `break_nonterm` → expect `raw_start=10 raw_end=14` for both.
2. l3 board → expect `arb_nonterm` and `break_nonterm` flip to PASS; no regression on SPAN/LEN/REM/LIT_LEN controls; TAB/RTAB/POS still FAIL (separate defect, untouched).
3. Broad SNOBOL4 corpus both modes, FAIL-set diff (not just counts) — zero new regressions.

## What remains open (not this FINDING)

- **Carving class** (`tab_nonterm`, `rtab_nonterm`, `tab_linear3`, `pos`): separate defect per L-3's own text, untouched by s39 and untouched by this fix. Re-measure TAB/RTAB after this fix lands.
- **L-1 Defect A** and **L-2 Defect B**: unrelated; L-1's ⛔ (fixing A alone raises hang count) still applies.
