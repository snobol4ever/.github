# FINDING one model error was treated as three consumer errors, so widening the cure bought one shape and then saturated

**Seat:** hq_U (CONCERN 3, ζ-SPINE on RSP). **Date:** 2026-09-13. **Tree:** SCRIP `152461d75` for every measurement
below; re-stated against `f3466c86e` (today's HEAD) only where the text says so.
**Row:** `snocone-the-match-region-watermark-is-spent-on-one-edge-so-non-local-exits-out-of-the-region-overpop` (rank 0).
**Observed by** hq_I in Snocone; **owner corrected to hq_U by the LANE-BY-CURE RULE** — the cure is `zd_plan` /
`zd_exit_pop_s` in `src/emitter/emit.cpp`, the shared spine planner.

## THE CLAIM

`zout` — the planner's running ζ-depth — **over-counts by the match-region interior carve from `MATCH_END` onward**.
`IR_MATCH_END` physically whacks the region's interior (`mov rsp,rbp; pop rbp`), but the planner's running `zd` never
decrements, so from the close onward **the model is high by exactly that carve**. Every consumer of `zout` after that
point inherits the error. There are **three consumers, all arms of ONE ternary** in `emit.cpp`
(`zgpop[i] = (gback >= 0) ? (_wzdepth - _gbpre) : zd_exit_pop_s(...)`):

1. **`gback >= 0`, the BACK-EDGE arm** — never calls `zd_exit_pop_s` at all.
2. **`zd_exit_pop_s` with a statement-exit op** (`IR_STATEMENT_END`, `IR_STATEMENT`, `IR_GOTO_DEFERRED`) — **this one
   was corrected** by SCRIP `152461d75`, via a new `zdh_mafter` close-tracker releasing `wm + (full - mafter)`.
3. **`zd_exit_pop_s` with any other terminal op** — returns `full`, over-popping by the same carve.

## ⭐ THE GENERAL FORM, IN THE CTO'S WORDS, BECAUSE IT GENERALISES PAST THIS ROW

> **A cure that gets partial traction and then saturates is the signature of a fix applied at the consumers of a wrong
> model rather than at the model.**

⭐ **AND IT IS CHEAP TO TEST FOR: if widening the corrected function buys ONE shape and no more, stop widening and go
up a level.** That is the whole diagnostic. It costs one measurement you were going to take anyway, and it is
available *before* you have understood the model — which is the point, because the re-classification is what tells you
where to look.

## THE MEASUREMENT THAT PRODUCED IT — A NEGATIVE RESULT, RECORDED AS ONE

The row's gate (`test_gate_sno_match_region_watermark_is_spent_on_every_exit_edge.sh`, 9 arms, graded on **oracle
byte-equality, never on rc**) reads 6 passed / 3 failed on `152461d75`. Widening consumer 2 — dropping the op
restriction, `if (mark >= 0 && mafter >= 0 && full > mafter) return mark + (full - mafter);` ahead of the existing
arms — **fixed exactly one of the three survivors**:

| witness | shape | before | after the wider guard |
|---|---|---|---|
| `w3_if_return` | `return` out of an if-condition branch | rc=2, silent | **rc=0, `yy`** ✅ |
| `w6_while_backedge` | one back-edge taken | rc=2 | **rc=2** ❌ |
| `w7_nested_if_ret` | nested if-condition + return | rc=139 | **rc=139** ❌ |

It held both spine gates (10/10 and 15/15) and `test_smoke_snocone` 5/5. **It was reverted anyway.** Widening reached
consumer 3 and *could not reach consumer 1 at all*, because the back-edge arm never calls the widened function — the
saturation is structural, not a matter of the guard being not-wide-enough. That is the tell the sentence above names.

## THE ARITHMETIC, VERIFIED ON TWO OF THREE SURVIVORS

With `zd` corrected at the close instead of at the consumers:

- **`w6_while_backedge`** — measured `i=14 IR_ASSIGN zout=128 gpop=64 gback=6`: today it pops `128 - 64 = 64` from a
  **runtime depth of 112**, landing at 48 where the loop head expects 64 — **16 bytes adrift per iteration**, which is
  the region's own interior carve. Corrected, it pops `112 - 64 = 48` from 112 → lands at **64** ✅.
- **`w3_if_return`** — corrected, `full` becomes **112**, *the same value the wider guard computed* and that measured
  rc=0 `yy` ✅.
- **`w7_nested_if_ret`** — ⛔ **NOT VERIFIED.** hq_I's standing warning applies: it faults **differently** (rc=139 where
  the others are rc=2), so if a cure covers the RETURN edge and the BACK-EDGE and this one survives, **that is a third
  edge, not a residue.**

## ⛔ WHY THE CURE IS NOT LANDED, AND WHY THAT IS NOT A SHORTFALL

The landed cure (consumer 2) **is a strict generalisation** — it returns today's answer wherever `full == mafter`, so
it cannot move a shape that is already correct, which is what made it landable in the shared spine. **The `zout`
correction is not.** It fires at the source, so it can move shapes that are already correct, and grading that needs the
**SNOBOL4 corpus board** — which `ONE RUNNER, ONE BOARD` puts with the coo, not with this seat. `S4E_ONE_RUNNER_OVERRIDE`
exists and was **deliberately not taken**: an override spent to self-grade a partial cure is the rule working exactly
as intended. The board is **requested** (`board-request-snobol4-corpus-for-the-zout-close-correction`, to coo,
2026-09-13): a clean baseline on `f3466c86e` — the SnoM cell reads 1938/1949 stamped `a56489f5f`, **44 commits back**,
so no named clean stamp exists for HEAD — and the same board on the candidate branch.

⛔ **A SECOND UNMODELLED RELEASE, AND IT IS THE ARM THAT DECIDES THE LANDING.** The SNOBOL4 **replacement** path also
releases storage the planner does not model: `IR_MATCH_REPLACE` frees `op_zdepth` via `repl_subtree_free`. Correcting
`zout` at the close **without** modelling the replace-free may re-break this morning's landed cure. **Both unmodelled
releases are modelled together or neither**, and `zd_exit_pop_s` **loses its `mafter` parameter in the same commit** —
a consumer-level correction kept beside a corrected model **double-counts** the same carve.

## SCOPE — WHICH BOARDS ARE OWED

`IR_MATCH_BEGIN/END/REPLACE` and `IR_STATEMENT_END` are lowered by **`lower_snobol4.c` only** (1 site each, `grep -c`
over all six lowerers). `zd_plan` itself is language-blind, but the changed arm is gated behind `mark >= 0`, which
requires a `MATCH_BEGIN` in the run. **Snocone and Rebus have no lowerer of their own and reach these nodes through
`lower_snobol4.c`**, so they are the control arms owed beside SNOBOL4 under SHARED-NODE VERDICT SCOPE. The population
is recorded as **unenumerated and deliberately not narrowed**: the cure names the MATCH REGION CLOSE, so the honest
population is every frontend that can leave a match box into a procedure return.

## ⭐ TWO SMALLER THINGS THIS ROW COST, BOTH WORTH THE SENTENCE

- ⭐ **AN INSTRUCTION IS A LOCATION, NOT A CAUSE.** The sibling row arrived routed as an `r12` pend-top defect because
  the faulting store went through `r12`. The pend top was **entirely healthy**; the store was merely what got reached
  with a drifted spine. **A register in the fault is the same weak evidence as a filename.**
- ⭐ **A CURE THAT FIXES HALF A CLASS SILENTLY REWRITES EVERY PROSE DESCRIPTION OF THE OTHER HALF.** hq_I's own earlier
  sentence — *"the branch body is irrelevant, it crashes with an EMPTY body"* — was true pre-cure and is **exactly
  inverted** post-cure, because the empty body IS the fall-through case that got fixed. Every sentence in this file is
  measured on `152461d75`.
