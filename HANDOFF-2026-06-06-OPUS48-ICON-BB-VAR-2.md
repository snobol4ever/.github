# HANDOFF 2026-06-06 — Opus 4.8 — ICON-BB ICN-VAR-2: binop/relop var operands + the if/while/until/repeat cluster

## What landed (one gated rung)

**ICN-VAR-2** — native binop/relop var operands on the descr-flat-chain path, which lit up the entire
if_expr/while/until/repeat_break/bare_if smoke cluster. Smoke m3/m4 **5/12 → 10/12** each; corpus m3 **18→22**,
m4 **25→32**; m2 **129 HARD byte-identical**. Diff: `src/emitter/emit_bb.c` + `src/driver/scrip.c` only —
no template files touched.

## The discovery that shaped the rung

The Icon lowerer chains relop/arith operands as **producer boxes** — `IR_BINOP` shows `α=. β=.` in `--dump-bb`.
`descr_chain_operand_refs` (emit_bb.c ~2499, the emit-time RPN resolver) fills `α/β` from chain predecessors
before codegen, so `bb_binop_arith`/`bb_binop_relop` needed no template changes at all. The cluster kinds are
pure **chain joins**: cond `BINOP γ→body, ω→WHILE` (the exit join), body-tail `CONJ γ→cond` is the back-edge,
`REPEAT γ` = back-edge, `BREAK γ` = exit. `codegen_flat_chain_body`'s label resolver already wires back-edges
to emitted labels.

## Changes

`src/emitter/emit_bb.c`:
- `flat_drive_binop_tree`: deposits `op_sa/op_sb/op_off` from walked operand slots before `EMIT_PAIR_FILL`
  (descr mode) — previously stale.
- `IR_BINOP` descr arm: delegates to `flat_drive_binop_tree` when an operand has no slot yet (needs-walk
  fallback; dormant for chain-resolved operands).
- `IR_WHILE`/`IR_UNTIL`/`IR_IF`: gvar-style descr passthrough (`β: jmp γ; jmp γ`). IF must NEVER route through
  `walk_bb_node` — no emit_core template exists; the dispatch default is a loud abort at emit time.

`src/driver/scrip.c` (admission, the by-name CALL lens UNCHANGED — the AUGOP fence holds):
- `icn_assign_safe_kind` += `IR_BINOP IR_IF IR_WHILE IR_UNTIL IR_REPEAT IR_BREAK IR_NEXT IR_CONJ`.
- BINOP op lens in lassign graphs: numeric relops (`BINOP_LT..BINOP_NE`) + 5 arith ops ONLY (string relops
  `SLT..SNE` have no template arm).
- `icn_local_assign_rhs_ok` += arith `IR_BINOP` (`x := x + 1`).
- **Fence (caught by the stash/set-diff, the VAR-1 lesson):** `rung18_real_relop_mixed_relop` flipped
  EXCISED→FAIL — `IR_LIT_F` is **slotless** (only LIT_I/LIT_S allocate), so a float-fed relop bombs.
  `has_lassign && has_binop && (LIT_F || LIT_NUL)` → EXCISE. Sound: floats cannot reach vars either
  (rhs_ok excludes LIT_F), so LIT_F-direct-to-binop is the only ingress.

## Gates (all green)

Probes if/while/until/repeat_break/bare_if **m2==m3==m4**. Corpus full stash/rebuild/set-diff vs true baseline:
m3 `18P+82F+147E → 22P+82F+143E`, m4 `25P+136F+86E → 32P+136F+79E` — every flip **EXCISED→PASS, zero →FAIL**.
Smoke Icon 12/12 HARD · m3 10/12 · m4 10/12 (remaining 2 = userproc lane, standing flag 4) · Prolog 5/5 ·
broker 32 · bb_bin_t 0 · handencoded `--strict` 0 · icn_no_stack 0 · one-reg-frame 0 · scan fence PASS ·
prove_lower2 PASS · FACT 0 · g_vstack 0. Medium-invisible reads **347**: the +4 vs the VAR-1 watermark are
pre-existing peer-lane sites (`bb_conj/bb_ite/bb_pat_alt/bb_pat_cat`, PL/SNO files) — this diff is template-free.

## Process note

A baseline-capture attempt was contaminated by a tool timeout landing after `git stash pop` (the saved
"baseline" binary was the after-build; its sweep matched the after columns exactly). Re-verified by re-stashing
and confirming the baseline binary EXCISES the if_expr probe before sweeping. **Lesson: verify the baseline
binary's behavior on a known-flipped probe before trusting a baseline sweep.**

## Next

**ICN-VAR-3** (SCAN-13b adoption: var-subject scans, the written-up slot-adoption piece) or
**ICN-VAR-AUGOP-PREREQ** (the `x +:= e` desugar; 11 fenced m4 programs are its ready probe set).
