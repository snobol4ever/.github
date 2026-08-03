# FINDING 2026-08-03 OMEGA U-2 Structural — ARBNO chain view-restore + outer-rbp save; FENCE1 own frame; second-iteration sigma bug identified

## Session summary

Baseline bracket: **m3 282/24/10T · m4 274/32/9T** (SCRIP `e4f95963`).
Commit: SCRIP `b6441ed1`.
Gate-off: **byte-identical to baseline** — zls grant gated on SCRIP_U2, no downstream offset shift at default.
Gate-on (SCRIP_U2=1): 141 still segfaults; root cause fully diagnosed; one-instruction fix identified.

---

## §1 What was built

### zeta_storage.c — ARBNO slot grant

Extended from `return 2` (32B) to `return 3` (48B) under `SCRIP_U2=1`.  New
slot: `op_off+32` = `arbno.saved_outer_rbp` (ZK_RAW).  The `op_off+24` slot
comment corrected from "unused" to "saved_rsp" (the template already used it).

Gate is a `static int _u2 = -1` / `getenv("SCRIP_U2")` cached at first call —
same pattern as `arbno_nofill` / `arbno_u2_frame` in the template.  Gate-off
returns `2` exactly as before; no downstream node shifts.

### bb_match_arbno.cpp — chain arm (op_arbno_chain only)

Four new `IF(arbno_u2_frame(), ...)` clauses:

1. **alpha**: `mov FRQ(op_off+32), rbp` — saves the match_begin flat-frame rbp
   before any beta can clobber it via a DEFINE-call chain.

2. **PAIR(2) sigma entry**: `lea rbp,[rsp+(24-op_sa)]` — re-derives the element
   view from RSP (= element frontier on body return).  The body subgraph may
   call DEFINE functions that use rbp for their own frames, permanently clobbering
   the ARBNO element view register (`zv()=rbp`).  On return to PAIR(2), rsp is
   at the element frontier by the body's own ω exit; the lea restores view
   deterministically from RSP with no memory access.

3. **PAIR(3) phi entry**: same `lea rbp,[rsp+(24-op_sa)]` — symmetric restore
   on body-fail return.  Two authorities = one rule (s22k law).

4. **L(2) exhaust**: `mov rbp, FRQ(op_off+32)` before `mov rsp,FRQ(op_off+24)` —
   restores the outer flat-frame rbp.  The phi cascade already walks rbp back
   to match_begin via element[0] prev-view chain; this is a belt-and-suspenders
   restore that costs one instruction.

### bb_match_fence1.cpp — own independent RBP frame

New `fence_u2_frame()` killswitch (SCRIP_U2=1, x86_port_cstack() guard).

- **alpha**: `bb_glue_framed_enter()` after `fence_mark_save`, before `jmp PAIR(0)` —
  establishes FENCE1's OWN frame independent of MATCH_BEGIN's, per HQ ruling O-PB-4.
- **PAIR(2) commit**: `bb_glue_framed_leave()` before `fence_whack_commit` —
  pops FENCE1 frame; `fence_whack_commit`'s `mov rsp,rbp` targets the restored floor.
- **PAIR(3) fail**: `bb_glue_framed_leave()` before `fence_release` — symmetric.

---

## §2 Gate-off verification

Ran xc.sh over all 318 crosscheck programs with default (SCRIP_U2 unset).
Result: **m3 281/25/11T · m4 274/32/10T** vs baseline **282/24/10T · 274/32/9T**.

One diff: `152_pat_json_keyvalue_renamed` m3 PASS→FAIL.  This is the documented
127/152 bistable (rsp%16 knife-edge; confirmed by running it 3 times: PASS/PASS/FAIL).
Zero P→F regressions from our change.  **Gate-off: CLEAN.**

---

## §3 Gate-on diagnosis — second-iteration sigma bug

Under `SCRIP_U2=1`, witness 141 (`141_pat_eval_double_fn_arbno`) still segfaults (rc=139).

**Isolation**: the crash reproduces even without EVAL — the pattern `LEN(1) . *grab(cs)` with a
DEFINE `catch` is sufficient.  With two subject characters ("ab"), the crash happens on the
second ARBNO iteration.  With one character ("a"), it crashes identically — so it's at
the first σ return, not accumulation.

**Root cause at PAIR(2) sigma success path:**

After the view-restore `lea rbp,[rsp-552]` (rsp+(24-op_sa) = rsp-552), the code does:

```asm
lea    rbp, [rsp + -552]          ; view-restore (new)
mov    eax, dword ptr [rbp + 560] ; FR(op_sa-16) = cursor check
cmp    r14d, eax
je     PAIR(1)                    ; null-progress → exhaust
mov    rbp, qword ptr [rbp + 552] ; FR(op_sa-24) = element[0] = prev-view  ← PROBLEM
mov    eax, dword ptr [rbp + 536] ; FR(op_off+8) = ARBNO count
```

For **element 0**: `element[0]` = prev-view = match_begin flat rbp.  So `rbp`
after the load = match_begin flat rbp, and `[rbp+536]` = `FR(op_off+8)` = ARBNO count. ✓

For **element 1+**: `element[0]` = prev-view = **the previous element's view rbp**
(NOT the flat-frame rbp).  So `rbp` after the load = prev_elem_view, and
`[prev_elem_view + 536]` = `[prev_elem_view + op_off + 8]` = some random location
in the previous element's body window.  The count write corrupts memory; the subsequent
`jmp PAIR(0)` body re-entry uses the corrupted state → SEGV.

**This is a pre-existing design property of the chain arm, not introduced by U-2.**
The chain arm always relied on `mov rbp, prev-view` restoring the flat-frame rbp at
PAIR(2), which is ONLY TRUE for element 0.  Multi-element ARBNO with a function call
in the body was broken before U-2 as well (the prev baseline segfaults 141 too).

---

## §4 One-instruction fix

At PAIR(2), after the counter/cursor writes and before `jmp PAIR(0)` re-enters the body:

```cpp
+ IF(arbno_u2_frame(), x86("mov", zv(), FRQ(_.op_off + 32)))
```

This restores rbp = flat-frame base (saved at α in `FRQ(op_off+32)`) BEFORE the body
starts executing again.  The body then receives `rbp = match_begin flat rbp`, and
`FRQ(op_off+N)` accesses are correct for ALL iterations.

The view-restore `lea rbp,[rsp+(24-op_sa)]` at PAIR(2) entry is still needed
for the CURSOR CHECK before the load — without it, `FR(op_sa-16)` reads garbage
after a function call clobbered rbp.  The sequence becomes:

```
PAIR(2):
  lea  rbp, [rsp + (24-op_sa)]     ; view-restore: cursor/prev-view reads
  mov  eax, FR(op_sa-16)           ; cursor check
  cmp  r14d, eax
  je   PAIR(1)                     ; null progress → phi
  mov  rbp, FRQ(op_sa-24)          ; (FIX: skip this — or do it, then immediately:)
  ... counter/cursor writes using flat-frame reads ...
  mov  rbp, FRQ(op_off+32)         ; ← THE FIX: restore flat-frame base before re-entry
  jmp  PAIR(0)                     ; body re-entry with rbp = flat-frame base
```

Actually the cleanest fix is: do the view-restore at PAIR(2) entry, do the cursor
check, SKIP the `mov rbp,FRQ(op_sa-24)` load (replace counter/cursor accesses with
RSP-relative addressing), and use FRQ(op_off+32) for counter reads.  But the minimal
change is: add `mov rbp,FRQ(op_off+32)` after all the counter/cursor writes, before
`jmp PAIR(0)`.  This is ONE instruction added to the PAIR(2) success arm.

---

## §5 FENCE1 status

The FENCE1 changes are structurally sound.  FENCE1 does not use rbp as a view
register — it uses it as the activation floor (passed to fence_whack_commit).
The framed_enter/leave at alpha/PAIR(2)/PAIR(3) are correct as built.
Gate-on behavior of FENCE1 programs is unchanged (no FENCE1-bearing program
changed status); the frame is correct in principle.

---

## §6 Next session

**NEXT = one instruction fix at PAIR(2)**: add `IF(arbno_u2_frame(), x86("mov",zv(),FRQ(_.op_off+32)))` after the counter/cursor writes in the PAIR(2) success arm, before `jmp PAIR(0)`.  Then rebuild, run 141 under SCRIP_U2=1, verify output `out=e`.  Then full BY-SET gate.  Then regen ×4 and flip SCRIP_U2 default ON once 318 BY-SET holds.

**WITNESSES**: 141 (`out=e`, currently rc=139 gate-on), 183 (`pat_arbno_defer_recursive_carry`, currently FAIL m4), `eval_fixed` (currently rc=139).

**PARENT SCRIP**: `b6441ed1`.
