# FINDING — s22a (2026-07-31, Claude): THE RPO FILL WAS PREORDER WEARING THE NAME, AND THE SEED FORBIDS THE POP THAT FINDING 3 ASKED FOR

Goal: `GOAL-SNOBOL4-BB.md`. Commits: SCRIP `61b2b7a` (RPO-FILL v2) + `331cb26` (ZGPOP-STF),
artifacts SCRIP `7c8db47`/`ce0a5ea`, corpus `7ae64ab`/`fdb31c3`/`06cc5a2`.
Watermark held EXACT at both ends: crosscheck **m3 232/85 · m4 229/86/2 · DIV=1 {W04_arbno_basic}**,
broad **244/92 · 238/90/8**. Fail sets BYTE-IDENTICAL by SET, both modes, both commits.

---

## ⭐⭐ FINDING 1 — v1's `RPO_*` WALK WAS PREORDER, AND PREORDER IS NOT A LAYOUT ORDER

s21x-z's fill (SCRIP `4c4fdd9`) named itself reverse-post-order and appended each node on
FIRST VISIT. That is preorder. Preorder does **not** guarantee a node precedes its successors:
for `A→B, A→C, B→D, C→D` it yields `A,B,D,C` — D placed ahead of its own predecessor C.
Nothing broke because the arithmetic shapes carry no merges. **That is coverage, not correctness**,
and the s21x-z cursor said so itself; this rung is the correction it asked for.

Landed: two-phase iterative post-order (each node pushed twice — EXPAND discovers and pushes
successors, EMIT appends — so every successor subtree drains before the node's own EMIT pops),
then REVERSED. γ is pushed FIRST so it pops LAST, finishes last, and after the reversal lands
IMMEDIATELY after its predecessor. The contiguity and fall-through v1 got by accident, now by
construction, in the `jcon_irgen.icn:472 ir_a_Binop` children-before-parent shape.

## ⛔⭐⭐ FINDING 2 — REVERSING THE POST-ORDER VECTOR WHOLESALE LOSES THE ENTRY NODE

**This is the trap, and it is silent until you run the program.** `RPO_PUSH`'s visited test fires
at EXPAND time, not EMIT time. So if a later root's subtree reaches `entry` before `entry`'s own
stack slot is popped, `entry` is absorbed INTO that root's post-order block, stops finishing last,
and **stops being `nodes[0]`**. The prologue then falls into the wrong statement and the program
begins executing in the middle.

WITNESS: `214_indirect_goto` printed `at BETA` forever and never `at ALPHA`. The whole-vector
reversal also cost 24 m3 / 18 m4 programs and took DIVERGE 1 → 6, every new DIVERGE member an
indirect/computed-goto program — i.e. exactly the merge-heavy shapes.

FIX: each ROOT gets its own drain and its own reversal (`RPO_FLUSH`), and the root blocks append
in v1's order — entry, anchors ascending, generator ω tails. **Block order is byte-identical to
v1/BFS; only the order WITHIN a block changes.** The visited set is now its own array (`seen`),
because a node is marked at EXPAND but does not enter `nodes[]` until EMIT, so `nodes[]` is no
longer a valid membership test mid-walk.

⚠ FALSE LEAD, RECORDED SO IT IS NOT RE-RUN: the first hypothesis was the `st_first_seen`
layout-coupling at `emit.cpp:2103` (`st_x[i]` NULL for the FIRST-EMITTED head — a genuinely
layout-order-dependent invariant, and still worth an audit on its own merits). It was **not** the
cause: the STMT-FRAME killswitch did not change the failure. One two-regime run falsified it.
Killswitch-first is cheaper than reading the emitter.

## ⭐⭐ FINDING 3 (s21x-z) HAS THE WRONG SPELLING — THE SEED FORBIDS HAND-COUNTED POPS

s21x-z's FINDING 3 proposed `add rsp, ΣK` on transfer/goto edges as the missing half of the
consumer-pop deletion. Reading the design of record FIRST — `seed/test_sno_stmt_frame_1.s`, as
NEXT(2) directs — that spelling is wrong, and the seed says so in its own annotations:

```
stmt_ADD3_1_fail:  je stmt_ADD3_1_fail   # fail edge = bracket cut; ZERO hand-counted pops
RETURN_floater:    mov rsp, rbp          # cut: reclaim EVERY statement/BB carve at any depth
```

**The release is the rbp bracket, not ΣK arithmetic.** Depth-INDEPENDENCE is the entire point of
law 4's occasional C-style RBP: the value spine rides RSP FORTH-style, and the housekeeping that
must survive an unwind rides a base that does not move. A ΣK term reintroduces exactly the
graph-wide depth bookkeeping the per-BB model exists to delete.

## ✅ LANDED — ZGPOP-STF: ON AN ARMED GRAPH THE STAGED POP IS ALREADY DEAD

Under STF a cross-statement γ edge is REDIRECTED to the statement head's `st_x` leave stub
(`emit.cpp` ~2327) emitting `bb_glue_framed_leave` = `mov rsp,rbp; pop rbp`. WITNESS (023 shape,
`OUTPUT = A + B`): `n7_assign` emitted `add rsp,48` immediately before `jmp main_stγ` whose first
instruction is `mov rsp,rbp`. `op_zgpop` is zeroed under `flat_stmt_frame`.

⛔ ZEROED AT THE **PLANNER CHOKE**, NOT THE EMISSION SITE — `op_zgpop` has TWO consumers: the
emitter (`x86_asm.h:1943`) and the conditional-γ path (`x86_asm.h:282`), which routes through the
jcc invert synth on `op_zgpop > 0`. Gating only the emitter fires that synth with **no payload**.
Same two-authorities shape as the s21x-w `zd_nops` defect; the rule generalizes — *when a staged
field feeds a synth as well as an emitter, retire it at the stage, never at one reader.*

NON-VACUITY (the s21x-w law — an unexercised arm proves nothing, and a wrong ZD arm returns wrong
ANSWERS rather than crashing): `add rsp` sites on the 023 witness fall **8 → 5**.

## ⛔ SCOPE, STATED PLAINLY — THE FIVE CONSUMER POPS ARE **NOT** DELETED

The pops in `bb_assign_global` (×2), `bb_binop_arith` (×2), `bb_binop_concat_slot` (×1) are gated
`IF(!stf(), …)`. They are the **UNARMED-graph fallback** and remain load-bearing.
MEASURED THIS SESSION: **96 of 317** compiled crosscheck programs emit an rbp bracket, so ~221
graphs still have no bracket to cut back to. That is why s21x-z's deletion experiment broke
transfer programs with `armed=0` — the pop was standing in for a bracket that was never built.

**Deleting the five pops is gated behind widening STF arming** (`emit.cpp:2657`, whose conjunction
includes `!flat_pat`), which carries the s21x-q un-welded `stfh` 48B-carve mine. Not attempted:
a half-finished arming widen is the one outcome worse than the pops existing.

## ⭐ NEXT — ORDERED

1. ⭐⭐ **STF ARMING WIDEN** — the real rung, and the gate on everything below. Weld the s21x-q
   `stfh` 48B carve vs `bb_match_release`'s fixed head-cell reads FIRST, then admit `flat_pat` at
   `emit.cpp:2657`. Success metric is the bracket census **96/317 → higher**, not the watermark.
2. Delete the five `IF(!stf())` consumer pops — mechanical ONCE (1) lands, worthless before.
3. **`st_first_seen` AUDIT** (`emit.cpp:2103`) — exonerated as this session's cause but still a
   layout-order-keyed invariant. Correct rule is a graph property ("is this head reachable only by
   the prologue fall-through?"), not a position in `nodes[]`.
4. **LAYOUT PASS** as its own rung — branch-chaining + fall-through reorder over generated chunks,
   per Proebsting Figure 1→2, strictly AFTER generation, `op_flat_disp` recomputed on the new order.
5. The 130/131 clean-HEAD segv, still unchased.

## ⚠ CARRIED

**COMPARE m4, NEVER m3.** `test_string` re-measured this session at **8 PASS / 4 FAIL over 12**
standalone m3 runs — it manufactured a phantom −1 on m3 during the RPO gate and would have read as
a regression on counts alone. The **SET** diff is what settled it. `213_gc_exhaustion_churn`
unchanged.
