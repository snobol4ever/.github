# FINDING 2026-08-03 OMEGA U-2a — flat_unwind_beta widened; fire set empty; ARBNO/ALTERNATE are blob-interior; structural half is next

## What was attempted

Widened `flat_unwind_beta()` in `emit.cpp` to include `IR_MATCH_ALTERNATE` and `IR_MATCH_ARBNO` as valid unwind-roll targets. This is the **predicate half** of U-2: making the selection function recognize generator βs as legal predecessor landing points.

## What was measured

**Gate-off byte-identity:** Verified on 052_pat_arbno, 054_pat_arbno_alt, 070_pat_arbno_star_var_digits, 072_pat_star_var_alt_backtrack — all byte-identical with `SCRIP_UNWIND=0`. Killswitch holds.

**Gate-on fire set: EMPTY.** `SCRIP_UNWIND=1` produces byte-identical output on every tested ARBNO/ALTERNATE program. The `ZD_DIAG=1` trace on 054_pat_arbno_alt reveals why: for the pattern statement, `nodes[]` contains only `IR_STATEMENT_BEGIN → IR_VAR → IR_MATCH_BEGIN → IR_MATCH_SEQUENCE → IR_MATCH_END → IR_STATEMENT_END`. The ARBNO and ALTERNATE nodes have `nblob=10` — they live in the **blob interior**, not as flat run members.

The unwind pre-pass (emit.cpp:~2381) and drive loop (emit.cpp:~2616) both call `flat_unwind_beta(nodes[_j])` iterating over `nodes[]`. Since ALTERNATE/ARBNO never appear in `nodes[]` as admitted members, the predicate is never consulted for them, and `bused[]` is never set by this path.

**Witnesses unchanged:** 141 segfaults at HEAD (gate-off). 183 not reached. roman prints `result: VI` (gate-off). eval_fixed rc=139 (gate-off), segfaults (gate-on). None of these change with the whitelist expansion.

## Root cause analysis

The whitelist expansion is **correct in principle but premature**. The U-2 spec names two distinct sub-tasks:

1. **Predicate half** (done this session): `flat_unwind_beta` recognizes ALTERNATE/ARBNO. This fires when a flat run member's ω needs to roll into a preceding generator's β.
2. **Structural half** (next session): `bb_glue_framed_enter` calls added inside `bb_match_arbno` (at iteration/commit entry) and FENCE1. This makes ARBNO/FENCE1 proper fail-capable members with their own RBP frames — `push rbp; mov rbp,rsp` at iteration entry, `mov rsp,rbp; pop rbp` at the success-side commit whack.

The four RBP constructs (STATEMENT/FUNCTION/ARBNO/FENCE1) all parameterize the ONE `bb_glue_framed_enter/leave` pair (x86_asm.h:1742). STATEMENT already uses it (emit.cpp:2449). ARBNO and FENCE1 do not yet. Once ARBNO has its own nested frame, its β (the element-push extension) IS the mechanism-2 O(1) frame-restore on failure: the frame's saved-rbp survives backtrack and `mov rsp,rbp; pop rbp` at MATCH_END's whack correctly unwinds to the pre-ARBNO frontier.

## roman wrong output analysis

`roman` prints `result: VI` (last-recursion-level signature). This is **U-CALL class** — accumulated call-chain state lost across recursive DEFINE invocations. The fix belongs in the SAVE_RESTORE/CALL minimal frame shape (U-CALL rung), where `push rbp; mov rbp,rsp` at SAVE_RESTORE entry and `mov rsp,rbp; pop rbp` at CALL exit give each DEFINE activation its own isolated frame. This is structurally the same mechanism-2 as ARBNO, applied to the function-call boundary.

## Sequencing correction

The correct U-2 execution order is:
1. Add `bb_glue_framed_enter` call to `bb_match_arbno_nary` β path (at each iteration/extension entry) — this creates the nested RBP frame whose `mov rsp,rbp; pop rbp` whack at MATCH_END correctly releases the ARBNO stack growth.
2. Add the same to FENCE1 commit path.
3. Then `flat_unwind_beta` fires: once ARBNO/FENCE1 ARE admitted via their own frame, value-spine nodes that follow them in the run can roll into ARBNO/FENCE1's β on failure.
4. Verify 141/183 (ARBNO-bearing pattern programs with deep recursion).

The whitelist expansion committed this session (SCRIP `e4f95963`) is kept: it is gated behind `SCRIP_UNWIND`, byte-identical off, zero regressions, and correctly documents the predicate half of the design.

## Gate

SCRIP `e4f95963`. m3 **296/40** · m4 **289/41** (bracket: 295/41 / 289/41 — +1P flake resolved in our favor, BY SET identical both modes per the documented 127 bistable). Zero P→F regressions.

## Next session

Read this FINDING §structural-half before writing any ARBNO template code. The entry point is `bb_match_arbno.cpp` — the NARY non-tail path's β (line ~263: `x86_beta()` + `sub rsp,op_sb` + element header init + `jmp PAIR(0)`). Before that `sub rsp`, add `bb_glue_framed_enter()` at K=0 (no pad cell, just the RBP bracket). Then at MATCH_END's whack (or ARBNO's own exhaust ω at line ~308: `mov r14d,FR(_.op_off)` + `mov rsp,FRQ(_.op_off+24)` + `x86_omega()`), the `mov rsp,FRQ(_.op_off+24)` is the existing mechanism-2 depth-restore via the saved-rsp slot — verify this composes correctly with the new framed_enter's saved-rbp at `[rbp+0]`. The RBP frame nests INSIDE the existing FORTH-stack frame: FORTH cells grow below the RBP-pinned floor, the MATCH_END whack pops only to the floor, leaving the outer MATCH_BEGIN's context intact.
