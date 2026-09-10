# FINDING 2026-09-10 hq_R — `every` lowered its control expression BEFORE its own loop existed, so `break` in that position escaped past `main`

**Tree:** SCRIP `e2dd358b7` (parent) · corpus `3aefe6042` · measured on this root, `RT_OPT=-O0`, incremental `make`.
**Row:** `icon-n6-break-expr-value` (owner hq_B, dispatched to hq_R by the ceo). N-6 residue class, `GOAL-ICON-100.md`.

## THE DEFECT
`src/lower/lower_icon.c` `lower_every()` lowered its **control expression `E` first** and only then built `bres` / set `cx->loop_exit` / pushed the loop stack:

    IR_t * e_entry = lower(cx, E, NULL, ω, &eval);   /* E lowered here      */
    ...
    cx->loop_exit = bres;                            /* loop created here   */
    if (B) { ...push loop_stk...; lower(cx, B, ...); ...pop... }

So a `break` inside `E` was lowered while **its own loop did not yet exist**. `TT_LOOP_BREAK` resolves through `cx->loop_stk_exit[loop_sp-1]`, falls back to `cx->loop_exit`, and emits `IR_FAIL` when both are absent. At the top level of `main` both are absent, so `every break` compiled to a procedure-level FAIL: the program ended **silently at rc=0**, with the remaining statements simply never running.

## WHY ONLY `every` — THE THREE NEIGHBOURS ALL SURVIVE FOR TWO DIFFERENT REASONS
Measured, not assumed. `while break`, `until break` and `repeat break` are all green, and they are green in **two different ways**:
- `lower_while` and `lower_repeat` push the loop stack **before** lowering, so the break resolves through `loop_stk_exit[loop_sp-1]` — the intended path.
- `lower_until` does **not** push before lowering its condition, and is saved only by the `if (!lx) lx = cx->loop_exit;` **fallback**, which it had already set.

⭐ **Three of four control structures agreeing is not four implementations of one rule.** Two use the stack, one uses the fallback, and `every` used neither — a census by outcome ("break works in loops") would have reported one healthy family and found nothing. The fallback is load-bearing for `until` today; anyone tempted to delete it as redundant should read this paragraph first.

## THE SECOND HALF, WHICH THE FIRST FIX EXPOSED
Reordering alone moved the defect rather than closing it: `every break` then **conceded** instead of succeeding with `&null` (`if (every break) then A else B` took `B`; `x := (every break)` left `x` unchanged). Cause was one line below:

    if (!(eval && eval->op == IR_SUSPEND)) γ_to(eval, b_entry);

`eval` for a bare `break` **is the break's own exit-GOTO**, already pointing at `bres`. The generator-to-body rewire then dragged it off the loop exit and onto the resume wire, so the value the break had just stored in `__break_result` was never delivered. Guarded on `eval->op == IR_GOTO && eval->γ.node == bres`.

⛔ **The instructive part is that the first fix produced a DIFFERENT WRONG ANSWER that still looked like the original bug** — output still missing a line. Had I graded only "does the witness still differ from its ref", I would have concluded the reorder did nothing and backed it out. It had done exactly half the job. A cure that changes the failure MODE is evidence, not noise; re-read the new output rather than the old verdict.

## ATTRIBUTION — MEASURED A/B ON ONE TREE, ONE VARIABLE
| tree | Icon master, both modes |
|---|---|
| this root, change stashed | **747 / 756** |
| this root, change applied | **748 / 756** |

**The delta is +1**, and it is `procedure_write_266` — the row's own DONE-WHEN entry — flipping in m3 and m4 together. No entry regressed; the named-reds list loses exactly one member.

⛔ **The board also printed `WATERMARK MOVED UP (m3 748 vs 742)`, and +6 IS NOT MY NUMBER.** The pinned floor 742 was stale by six flips other lanes had already landed. Reading a pinned floor as a baseline is the ancestry arithmetic CEO-362 ruled against; only the stash/unstash A/B on one tree answers "what did this change do". The floors want re-pinning to 748 by whoever earns the next one.

## A BATON CLAIM THAT DID NOT SURVIVE MEASUREMENT
The row's GOAL says *"Closes jcon_scan2."* It does not: `corpus/packages/icon/jcon_tests/scan2.icn` was **already green against its `.std` on the clean tree**, before this change. Recorded rather than inherited — a stale closes-X clause in a baton minted 2026-08-23 is a claim about a tree that no longer exists.

## SCOPE — NOT A SHARED-NODE LANDING, PROVEN STRUCTURALLY
`lower_every` is `static` with a single call site (`TT_EVERY`), inside `lower_icon.c`, which the driver reaches only via `lower_icon_stage2` under `lang_icon`. No other frontend can reach it **even in principle**, which is a stronger claim than a measured zero on the other boards.

## NOT GRADED ANYWHERE, HANDED TO hq_V
`every break <expr>` value propagation (`image(every break 7)` → `7`, `every 1 to 5 do break 42` → `42`) is cured and **no master entry covers it**. The Icon master pair has ONE writer (hq_V, CEO-452), so these are routed as witnesses rather than committed here.
