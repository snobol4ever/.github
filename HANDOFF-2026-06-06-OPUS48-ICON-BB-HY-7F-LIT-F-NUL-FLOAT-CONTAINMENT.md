# HANDOFF — 2026-06-06-f · Opus 4.8 · GOAL-ICON-BB · HY-7f LIT_F/NUL + float containment

**Landed:** SCRIP `e642753` · .github `1b15d374` (watermark + Lon-directed prune)
**Columns:** m2 143 HARD · m3 31 · m4 41 (+1/+1 = `write(real)` native)

## What landed
- `bb_lit_scalar.cpp`: IR_LIT_F arm `{DT_R, double-bits sealed RO [rip+disp]}`; IR_LIT_NUL arm `{DT_SNUL,0}` (two immediates, no seal). `emit_bb.c` `gvar_callarg_admit` + slot-alloc widened to F/NUL; `scrip.c` `icn_ring_to_tree` decline widened.
- **CONTAINMENT (the core finding):** adoption alone converts LOUD HEAD failures into SILENT miscompiles — binop int-adds double bit patterns (`2.5+1.0` → 9219994337134247936), `bb_unop` int-negs bits + retags DT_I (`write(-2.5)` → garbage int). Fixed driver-side: `descr_binop_opnd_slot()` (ONE definition) demotes F/NUL slots at both binop sites + `needs_walk` + the unop driver — restores exact HEAD routing/bombs. `bb_unop` sa<0 → `x86_bomb` (also closed a LATENT pre-existing silent `[r12+7]` read when sa=-1).
- `rt_write_any_nl` DT_R: `%g` → `rt_format_float` (round-trip, ".0" suffix). `%g` printed "2" for 2.0 vs m2 "2.0".
- Sanctioned F/NUL consumers (type-agnostic 16B descriptor reads): `bb_call_write_slot`, gvar call-arg marshal. Everything else: LOUD.

## Float relop intel — do NOT re-derive
Int-cmp on double bits is order-correct for all NON-NEGATIVE doubles (IEEE bits order-isomorphic; sign bit 0 ⇒ signed≡unsigned). Negative literals lower as `IR_UNOP NEG(LIT_F)`, and int-neg-of-bits is ALSO accidentally order-isomorphic — probes "looked right" while the VALUE was garbage (DT_I retag). Order-by-accident ≠ correct; hence the demotion.

## Proofs
- Icon `write(2.5)`/`write(2.0)`: m2==m3==m4. SNO `F(2.5)`→2.5, `F(7,)`→7 — omitted-arg TT_NUL is the ONLY live IR_LIT_NUL route; Icon source never makes one (`&null` lowers IR_VAR"&null"→`bb_keyword`).
- Suite 143/31/41 · smokes baseline (icon 12/10/10, sno FAIL=0, prolog 5/4+1exc/5, broker 32/35) · fences var+scan PASS · no_stack 0 · one_reg 0 · FACT 0.
- Stash-baseline BOTH directions. **LESSON: rebuild after stash/pop** — stashing sources without rebuilding tests the wrong binary (made and caught that mistake).

## Pre-existing, flagged (goal Standing flags 10/11)
`write(&null)` m3 abort — keyword path, `pat_flat_β` unresolved fwd ref. Pascal `writeln(real)` blank-pads identically all modes — Pascal real path unbuilt.

## Session mechanics
- The HY-7f diff was SEEDED into the working tree between turns (Lon applied the prior turn's proposed edits). Audit seeded diffs like any other — stash-baseline proved this one incomplete.
- GOAL/RULES/PLAN/REPO pruned per Lon directive: completed rungs DELETED (git history holds them); all byte-identical FACT bodies extracted VERBATIM, span-diff + sibling-md5 verified vs GOAL-SNOBOL4-BB.md. Concurrent Pascal prune `81d9be09` merged clean mid-push.

## Next
**HY-7g:** gvar/frame-var reads as producer boxes → nested `marshal_single_call` args (owner-guard excludes them today) → DELETE operand-kind arms in `marshal_call_arg` + `->t/->sval` reads in `marshal_varparam_addr` → HY-FENCE.
