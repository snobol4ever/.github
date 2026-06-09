# HANDOFF 2026-06-06 — Opus 4.8 — ICON-BB ICN-VAR-AUGOP-PREREQ: TT_AUGOP desugar

## What landed (one gated rung)

`x op:= e → x := x op e` AST desugar for **plain-var lhs**, in the lowerer at the SCAN-13a interception
point (top of `lower_value`, mirroring the AUGOP_SCAN arm; Rebus `rebus_lower.c` precedent). Canonical
per JCON `ir_augmented_assignment` (`tmp := op(lv,rv); :=(lv,tmp)` — for a plain var, evaluate-once vs
twice is indistinguishable). Map `icn_augop_binop_tt`: ADD/SUB/MUL/DIV/MOD/POW/CONCAT + numeric relops
EQ/LT/LE/GT/GE/NE + string relops SEQ/SLT/SLE/SGT/SGE/SNE → their TT binops. **Cset augops (8/9/10)
excluded** — TT_CSET_* is the standing lower2-UNHANDLED abort tier. Non-var lhs untouched → the VAR-1
by-name CALL fence **stays load-bearing** for `a[i] +:= 1`-class misroutes.

## The finding

The misroute was worse than flagged: `x +:= 5` lowered to a bare no-op `IR_CALL`, so **mode 2 printed
the stale value** (probe printed 1, not 6). The desugar therefore repaired the ORACLE too: m2
**129 → 143 (+14)** — the HARD gate is `>=`; climbing is the win. Probes `x+:=5`→6 and `-:= *:=`
chain→28 are m2==m3==m4; `||:=` m2-correct + clean native EXCISE (concat lens).

## Gates

Diff: `src/lower/lower.c` only. Corpus set-diff vs the committed VAR-3 state (`94841cd` sweep files):
m2 129→143 · m3 25→30 (+rung10_augop_{augplus,augstar,augsub_mod,break_while}, rung35_block_body_
while_do_block — all EXCISED→PASS) · m4 35→40 (same five). One failure-MODE change inside the FAIL
bucket: `rung36_jcon_augment` m4 rc 134→1 (emitter-abort → runs-and-exits-1; records/image/alt-in-args
territory; m2 also FAILs it on a pre-existing `[NO-AST] interp_eval stub` line). Zero PASS/EXCISED→FAIL
flips; m3 FAIL=82 m4 FAIL=136 both unchanged. Smoke Icon 12/10/10 · Prolog 5/5 · broker 32 · scan fence
GATE: PASS at the ratcheted floors (bucket 11/11) · no_stack 0 · one-reg 0 · bb_bin_t 0 · handencoded
--strict 0 · prove_lower2 PASS.

## Next

**ICN-VAR-FENCE** — probe sweep + corpus var-bucket floors + structural battery, the ICN-SCAN-FENCE
pattern (capture-then-match, never `cmd | grep -q` under pipefail). Swap (`:=:`)/rung11/15/37 remainders
stay fenced — their own tiers.
