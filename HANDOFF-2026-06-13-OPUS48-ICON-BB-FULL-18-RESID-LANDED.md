# HANDOFF 2026-06-13 — ICON-BB FULL-18-resid LANDED

**Goal:** GOAL-ICON-FULL-PASS (Icon m2 toward full pass; close m3/m4 gap).
**Result:** FULL-18-resid fixed and pushed. m2 196→197, zero regressions.
**HEAD (SCRIP) = `b3de0be`** (post-rebase onto a430139). HEAD (.github) = this file.

## What landed

`every`-conjunction with an embedded generator was dropping the generator's
resume. Two fixes in `src/lower/lower_icon.c` (LOWERING ONLY — no template,
emitter, or runtime change; no new files; conforms to 200-col / zero-blank /
one-comment C style):

1. **`lower_every` `!BODY` loop-back.** Was:
   `loop_target = (gen_result->op==IR_CONJ) ? E : (gen_node==gen_result ? E : gen_node)`.
   The `IR_CONJ ? E` clause routed a conjunction's success edge to the EVERY
   node, which (ival=0) returns γ and exits after ONE value. Now:
   `loop_target = (gen_node && gen_node!=gen_result && gen_node!=ω && gen_node!=E) ? gen_node : E`.
   This loops success back to the embedded generator's resume, unifying the CONJ
   case with the already-correct `every f(gen)` CALL case (that case is why
   `every write(1 to 5)` always worked — CALL.γ→TO).

2. **Relop BINOP failure resumes its generative operand.** The BINOP node was
   built with the outer `ω` as its fail port, so a false comparison (`1>2`) exited
   to the every-fail instead of resuming the generator feeding it. Added:
   `if (IR_LIT(op).dval==1.0 && lβ && lβ!=ω && lβ!=op) ω_to(op, lβ);`
   (relops = codes 5–10, marked `dval=1.0`; `lβ` = left operand's resume,
   captured right after lowering the left operand).

## Verification (4-layer ladder)

| program | before | after |
|---|---|---|
| `every write(1 to 5)` | 1,2,3,4,5 | 1,2,3,4,5 (unchanged) |
| `every (1 to 5) > 2 & write("hit")` | hit (×1) | hit,hit,hit |
| `every (x := (1 to 5)) & write(x)` | 1 | 1,2,3,4,5 |
| `every (x := (1 to 5)) > 2 & write(x)` | (empty) | 3,4,5 |

- `rung13_alt_alt_filter` FAIL→PASS.
- m2 196→197 by EXPLICIT before/after `test_icon_rung_suite.sh --mode interp`
  diff: EXACTLY one line changed (filter FAIL→PASS), ZERO regressions.
- HARD: smoke icon m2 12/12, prolog 5/5.
- `test_gate_icn_no_stack`=0, `test_gate_icn_one_reg_frame`=0.
- filter m3/m4 cleanly `[SMX] EXCISE` (sanctioned interim; interp is oracle).
- The 45 `test_gate_bb_one_box` FAILs are PRE-EXISTING (identical on pristine
  8b3eefb; emitter template entry-count gate, untouched here).

## Watermark-count note

The interp suite reports m2=197; the prior goal header said "200" (a different/
combined count). Trust `--mode interp` tally + an explicit before/after diff to
judge regressions. Status line updated accordingly.

## NEXT (open, separate, deeper) — `cross_arg` multi-generator CALL args

`every write(1|2, ":", 3|4)` → `1:3, 334, 2:3, 334` (want 1:3,1:4,2:3,2:4).
`rung13_alt_alt_cross_arg` + `_cross_arg_sideeffect` still FAIL. Precisely
isolated and NOT the FULL-18 path:

- `write((1|2)||(3|4))` (concat, ONE arg) is CORRECT (13,14,23,24).
- `write(1|2, 3|4)` (TWO generator args) is BROKEN (13,**34**,23,**34**).
- CALL trace: takes the `is_deep=1` ag_ring-peek path with `has_gen_arg=0`. The
  cross-product odometer block (IR_interp.c ~2576) is NEVER entered — multi-arg
  generators are lowered as flat chained producer boxes, so `ir_call_arg` sees
  them already-evaluated. Resume is driven by flat back-edges (`CALL.γ →
  rightmost ALT`), but the ag_ring is not maintained across the literal-separated
  args on carry → the left arg's ring slot goes stale (the leading "3" in "334").
- FIX LIVES IN: the `is_deep` CALL ring protocol and/or `lower_call`'s flat-chain
  arg wiring. Ring-protocol surgery, materially larger than FULL-18 — fresh
  session recommended. `--dump-bb` on `rung13_alt_alt_cross_arg` shows the two
  ALT `ω` ports both pointing at the FIRST ALT; carry order is the suspect.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
