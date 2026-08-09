# FINDING-2026-08-09 — CLIMB s33 (Sonnet 4.6): H29 CRASH — FENCE1 U-2 dual-slot watermark fixes ZLS alias

## Status: LANDED — SCRIP `40b9e2e7` · corpus `075070df`

## Gate
m3: **135**/16xf/0/0R · m4: **134**/17xf/0/0R · 0 REGRESSION both modes.
H29 XPASS both modes (retired). t6m XPASS both modes (collateral, retired).

## Probe
`H29`: `SUBJ ? POS(0) FENCE(TAB(2) $ OUTPUT | ABORT) LEN(2) RPOS(0)` on `'abcd'`
Expected: `ab` / `=S`. Got: SIGSEGV (rc=139).

## Monitor bracket (MONITOR-FIRST, csn vs scr)
PARTIAL EOF step 4: csn still emitting `VALUE OUTPUT = STRING(2)='ab'`; scr EOF (crash).
Crash occurs after `$ OUTPUT` writes 'ab' to OUTPUT, before match-end bookkeeping.

## Nearest passing sibling
`H14`: `FENCE(LEN(2) . W)` — FENCE with simple capture, no ALTERNATE inside. Passes.
Delta: H29 has `ALTERNATE(TAB(2) $ OUTPUT, ABORT)` inside FENCE's P argument.

## Root cause (measured)

FENCE1's U-2 structural path (`fence_u2_frame()` active: SCRIP_U2_FENCE=1,
FORTH mode, ival≠2) pushes an inner RBP frame via `bb_glue_framed_enter()`:
```
push rbp; mov rbp, rsp; sub rsp, 8
```
This shifts `inner_rbp = outer_rbp − 32` (8B push + 8B sub + 16B alignment pad).

The ZLS planner assigns FENCE1's watermark slot at `op_off` (e.g. 144 for H29).
`fence_mark_save` saved the pre-fence rsp to `FRQ(op_off) = [outer_rbp + op_off]`.

After framed_enter, `fence_release` in the inner-frame paths (PAIR(2)/(3)/β) also
uses `FRQ(op_off)` — but now `rbp = inner_rbp`, so:

```
FRQ(op_off) = [inner_rbp + op_off] = [outer_rbp − 32 + op_off] = [outer_rbp + op_off − 32]
```

The ALTERNATE node inside the FENCE body uses (relative to inner_rbp):
- `FR(op_off)` = `[inner_rbp + op_off]` = `[outer_rbp + op_off − 32]` — **saved r14d cursor**

So `fence_release` was reading ALTERNATE's saved-r14 cursor (a small integer ~0..4)
into rsp, then jumping. The out-of-bounds rsp → SIGSEGV on the next memory access.

Specifically in H29: RPOS(0) fails (r14d=2 ≠ r15d-0=4), jumps to `n11_match_fence1_β`
with inner frame still live. `fence_release` reads `[inner_rbp + 144]` = ALTERNATE's
saved r14=0 into rsp, then `jmp n10_match_pos_β` dereferences rsp=0 → crash.

## Fix (template-only, `src/templates/bb_match_fence1.cpp`)

Dual-slot save exploiting the exact 32-byte frame shift:

```cpp
// fence_mark_save: U-2 arm writes pre-fence rsp to BOTH slots (outer rbp, before framed_enter)
FRQ(off)    = [outer_rbp + off]      ← slot-1
FRQ(off+32) = [outer_rbp + off + 32] ← slot-2

// fence_release: always read FRQ(off+32)
// inner frame live (rbp = inner_rbp):
//   FRQ(off+32) = [inner_rbp + off + 32] = [outer_rbp + off] = slot-1 ✓
// outer frame (rbp = outer_rbp, after framed_leave or β pass-through):
//   FRQ(off+32) = [outer_rbp + off + 32] = slot-2 ✓
```

`FRQ(off+32)` is inside FENCE1's own ZLS grant window (the planner grants enough
space; inner nodes start at `inner_rbp + op_off` = `outer_rbp + op_off − 32`, well
below `outer_rbp + op_off + 32`). No alias possible with ALTERNATE's slots.

All three release sites (PAIR(2) after framed_leave, PAIR(3) after framed_leave,
and the β path whether inner frame live or dead) now read the correct pre-fence rsp.

## Collateral: t6m XPASS

`t6m` (FENCE1 with deferred DIFFER call) was XFAIL both modes at the session open.
The dual-slot fix resolves the same U-2 alias class that affected t6m's pattern shape.
Retired from XFAIL both modes in the same corpus commit.

## C-7 rung status after this fix
- H29 ✅ CLOSED (this fix)
- t6m ✅ CLOSED (collateral)
- Remaining C-7 open: H21 (FENCE1 over deferred ALT — probe before inheriting D-gate),
  dc_sib_bt (defer-β re-yield, sibling ARBNO capture — witness committed corpus/226f904b)
- Nested-ARBNO class H24/H25/X02/X06/X11 (sno_seq_nary, lower-side)
- X08 pre-existing CRASH (ARBNO with ITEM=SPAN, not gated here)
