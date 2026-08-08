# FINDING-2026-08-08-CLAUDE-SN4-CLIMB-D06-RSP-ZLS-ALIAS-AND-D07-RTX-LEN-REVERT

## Session
CLIMB s17 (Sonnet 4.6)

## D07 — CLOSED (commit e0fb77e7)

### Defect
`55c045eb` (SN4-RTX: LEN deferred-arg fix) broke D07 by routing `LEN(*N)` through
`sx_lower(cx, t->c[0], ...)` where `t->c[0]` is the `TT_DEFER` node. `sx_lower` on
`TT_DEFER` always builds `SNO$MKEXPR` (full runtime-compilation path), producing
`CALL SNO$MKEXPR` in the IR. D07 was green at `6bda3acb` and broken by `55c045eb`.

### Fix
Restored `TT_LEN` handler to use `sno_pre_req`, which correctly unwraps `TT_DEFER`
to its inner child and defers that expression to pre-match evaluation, producing
`VAR "N" → COERCE_INTEGER → MATCH_LEN`. Commit `e0fb77e7`.

### Watermark
m3 135/7/0/0 · m4 139/3/0/0 · 0 REGRESSION both modes.

---

## D06 — DIAGNOSED, MECH CROSS-REQUEST

### Program
```snobol4
        SUBJ = 'abcd'
        P = LEN(1)
        SUBJ ? POS(0) *P $ OUTPUT                              :F(NO)
        OUTPUT = '=S'                                   :(EN)
NO      OUTPUT = '=F'
EN      P = LEN(3)
        SUBJ ? POS(0) *P $ OUTPUT
END
```
Expected: `a\n=S\nabc\n`. Actual: `a\n=S\nSIGSEGV`.

### Two independent defects

**Defect 1 (structural/MECH): OOM on cold GVA path.**
Any single `*P $ OUTPUT` match where P holds a pattern and the GVA cache is cold
crashes with heap exhaustion inside `dtp_fn_of → bb_compile_pat_tree_sz` recursive
chain. Same class as D02/D03/D04. Two consecutive `*P $ OUTPUT` statements (P=LEN(1)
then P=LEN(3)) work because the first warms the GVA fn-pointer cache.

**Defect 2 (ζ-frame/RSP alias): SIGSEGV in rt_cap_push on warm second match.**
`rt_cap_push` receives `slot=rbp+528` for the second match's MATCH_ASSIGN_SAVE.
That slot contains `0x300000003` (garbage) instead of the expected zero. Root cause:
the second match's LIT_INTEGER (for POS(0)) does `sub rsp,16` then `mov [rsp+480],3`.
With RSP at `rbp+48` at that moment, `[rsp+480] = rbp+528` — exactly the SAVE slot.
RSP is in the positive-rbp region because the JIT frame was established as
`push rbp; mov rbp,rsp; sub rsp,8` so `rbp = initial_rsp - 8` and the ζ allocations
use rbp+positive offsets (going UP into the caller's frame). As RSP shrinks during the
second match's ζ allocation chain, its stores hit the upper ζ frame slots.

### Mechanism detail (from ζ dump)

Scope 2 (group EN, `[320..576)`) ζ layout:
- `+480`: LIT_INTEGER result (second match's POS arg)
- `+512`: MATCH_ASSIGN_SAVE result
- `+528`: **capture.stack ws ptr** ← SAVE slot, written by rt_cap_push

LIT_INTEGER fires at `[rsp+480]`. With RSP at `rbp+48` after `sub rsp,16`:
`[rsp+480] = rbp+528` — overwrites the SAVE slot with the LIT_INTEGER DESCR value `3`
(DT_INTEGER type tag in the high dword, value 0 in low dword — packed as `0x300000003`).
By the time MATCH_ASSIGN_SAVE's alpha runs and calls `rt_cap_push`, the slot is corrupt.

### Confirmed by rt_cap_push diagnostic
First call (first match): `slot=0x7ffe1718ded8, content=[0,0]` — clean. ✓
Second call (second match): `slot=0x7ffe1718dff8, content=[300000003,0]` — pre-corrupted. ✗

### Isolation experiments
- Single `*P $ OUTPUT` (cold GVA): OOM (Defect 1).
- Single `*P $ OUTPUT` after warming GVA with `*P` (no capture): works.
- Two consecutive `*P $ OUTPUT` (no branch between): works (first warms GVA, RSP
  trajectory differs — no collision in the sequential layout).
- First `*P $ OUTPUT` succeeds via `:F(NO)/(EN)`, second `*P $ OUTPUT` reached via
  label: SIGSEGV (Defect 2, RSP at a different point due to the branch geometry).

### Fix direction (MECH cross-request)
The ζ-frame uses rbp+positive offsets but RSP is also in the positive-rbp region.
`sub rsp,N` within the match body lowers RSP, and `[rsp+large_off]` stores land in
upper ζ slots. Fix options:
1. Establish the ζ frame in NEGATIVE rbp offsets (below rbp), so RSP growth goes
   downward away from the frame.
2. Ensure `sub rsp` amounts during match body execution do not exceed `(ζ_slot_offset - current_depth)` — i.e., bound `sub rsp` amounts to stay below the ζ frame's lower bound.
3. Use a separate frame pointer for ζ accesses that is immune to RSP movement (the
   SEALED path with `op_seal=1` already does this — rbp is pinned at the claim base
   before `sub rsp` operations). Extend the seal geometry to cover the RSP-collision
   class even when `sno_seal_pat` eligibility fails.

### MECH cross-request
File as MECH M-NEW: ζ-frame RSP aliasing — LIT_INTEGER `[rsp+N]` store lands in
MATCH_ASSIGN_SAVE slot when flow path puts RSP at `slot_offset - N` relative to rbp.
Blocked pending MECH structural fix.

### Watermark (unchanged)
m3 135/7/0/0 · m4 139/3/0/0 · 0 REGRESSION both modes. SCRIP HEAD `e0fb77e7`.

---

## D08 — DIAGNOSED, MECH CROSS-REQUEST (appended s17)

### Program
```snobol4
SUBJ ? SPAN('0123456789') $ N LEN(*N) . FIELD
```
Expected: `FIELD=ABCDEFGHIJKL`. Actual: `FIELD=` (empty).

### Root cause
The `sno_pre_req` mechanism for `LEN(*N)` places `COERCE_INTEGER` in the PRE-CHAIN
(before MATCH_BEGIN). This is correct when N is set before the match (D07). But in
D08, `$ N` (MATCH_ASSIGN_IMM) sets N TO the matched span DURING the match. The
pre-chain COERCE reads N's value BEFORE `$ N` fires — getting null string → integer 0.
LEN(0) succeeds trivially (matching the null string), so `. FIELD` captures nothing.

### Verified
- N before match: empty string. COERCE_INTEGER(empty) = 0. LEN(0) matches null. FIELD = empty.
- N after match: "12" (correctly set by $ N). But too late for the pre-chain.
- Manual p.87: `SPAN('0123456789') $ N LEN(*N)` — SPAN matches, immediately assigns to N,
  then `*N` fetches N's CURRENT value at LEN-execution time (the newly set "12" → 12).

### COERCE_INTEGER slot vs read address
ζ slot for COERCE_INTEGER: `+240`. `FRQ(op_sa+8)` = `rsp + 248 + op_zdepth`. At
MATCH_LEN, `op_zdepth=160`, so reads `[rsp+408]`. Actual COERCE result at `[rsp+400+8]
= [rsp+408]` — the READ IS CORRECT. The value read is wrong (N's pre-match value = 0)
not the address. s16 "cross-arm mismatch" diagnosis was wrong; the slot offset is fine.

### Fix direction (MECH cross-request)
`sno_pre_req` for `LEN(*N)` must not be used when the `*N` argument variable is also
a capture target (`$ N`) earlier in the same pattern. In that case, COERCE_INTEGER must
be emitted as an in-body node sequenced after MATCH_ASSIGN_IMM (the `$ N` commit).
This is a lowerer structural change — the pre-chain vs in-body decision for `LEN(*N)`
must inspect whether the argument variable is also a `$ VAR` capture target in the same
pattern. If so, COERCE_INTEGER is emitted inline after the last `$ N` IMM. MECH territory.
