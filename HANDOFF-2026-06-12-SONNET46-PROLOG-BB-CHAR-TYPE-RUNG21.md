# HANDOFF — 2026-06-12 — Sonnet 4.6 — PROLOG-BB PL-GZ-9 char_type/2 (rung21)

**Goal:** GOAL-PROLOG-BB.md · PL-GZ-9 corpus reconquest.
**Watermark:** SCRIP `d60ed89` · .github `(pending push)` (both green).

## Landed

**rung21 char_type/2 — 5 new m3 rungs.** GATE-3 m3 ratchet **53 → 58**. No regressions: m2=114, m4=57.

### New components

- **`IR_DET_CHAR_TYPE`** — new IR kind in `src/contracts/IR.h` + name table in `scrip_ir.c`.
- **`rt_pl_char_type_cell(void *char_cell, void *type_cell, void *val_cell)`** in `unification.c`. Two dispatch paths: (1) compound type (`tt->tag == TERM_COMPOUND`): reads functor name as type, inner var from `args[0]` — handles digit/to_lower/to_upper/upper/lower/code; (2) atom type: isalpha/isalnum/isdigit/isspace(white)/isupper/islower/ispunct/isgraph/csym/csymf/end_of_line/newline. All paths trail-mark/unwind. `val_cell` always NULL (inner var embedded in compound Term after materialisation via `rt_pl_unify_struct_gz`).
- **`bb_det_char_type.cpp`** — `rdi=FRQ(char_cell)`, `rsi=FRQ(type_cell)`, `edx=0` (val_cell=NULL), `call rt_pl_char_type_cell`, `test eax,eax; jne γ; jmp ω; def β; jmp ω`. No RO data section needed.
- **`bb_prepare` for `IR_DET_CHAR_TYPE`** in `emit_bb.c`: 2 slots, `op_parts_ival[0]=char_slot`, `[1]=type_slot`.
- **`emit_core.c`** dispatch: `case IR_DET_CHAR_TYPE`.
- **Makefile**: `bb_det_char_type.cpp` in `RT_PIC_SRCS` + explicit compile rule.

### Admission (scrip.c, four sites)

- **`pl_gz_rule_body_goal_ok`**: char_type arm (ATOM/LOGICVAR char, ATOM/STRUCT type) placed before generic comparator arm.
- **`pl_gz_rule_clause`** whitelist: `char_type` arity 2 `continue`.
- **`pl_gz_count_synth_goal`**: +1 per non-LOGICVAR arg (both char and type can be non-LOGICVAR).
- **`pl_gz_build_goal`**: char_type arm after atom_concat arm; both char (ATOM→synth) and type (ATOM/STRUCT→synth) materialised via `IR_CELL_UNIFY`; arm closes with `} else if` restoring the comparator arm — critical: the `} else if` that opens the comparator arm had been dropped during my edit, causing the comparator body to run unconditionally after char_type; fixed before commit.

### Key bug (found and fixed in-session)

After inserting the char_type arm, the `} else if (gg->op == IR_BUILTIN && ... ir_pair_arg ...)` that guards the comparator arm was missing — the comparator arm's body ran after char_type regardless of what `gg` was. All char_type programs aborted with "not admitted" because the comparator arm's `!is_arith_cmp && !is_tcmp && strcmp(fn,"format") != 0` guard then returned 0. Fix: restore `} else if (...)` before the comparator arm body.

## Gates

- GATE-1: m2/m3/m4 5/5 HARD ✓
- GATE-3: m2=114 · m3=**58**/57-FAIL (ratchet floor=58) · m4=57/41-FAIL+17excised ✓
- `bb_bin_t`: 0 · `g_vstack`: 0 · `test_gate_bb_one_box`: PASS ✓

## Next open in PL-GZ-9 (recommended order)

1. **rung17** — `sort/2` + `msort/2` (5 rungs): new `IR_DET_SORT`, `rt_pl_sort_cell(void *list_cell, int msort_flag, void *result_cell)`. Build Term* array from list, qsort with `term_compare`, rebuild list. Materialise non-LOGICVAR list arg via synth slot. Admission: arity-2, ir_call_arg.
2. **rung20** — `numbervars/3` (5 rungs): new `IR_DET_NUMBERVARS`, mirrors `rt_numbervars_term` already in `IR_interp.c`. Three ir_call_args.
3. **rung26** — `copy_term/2`, `string_to_atom/2` (5 rungs): atom_op recipe extended.

## Session notes

- `ir_call_arg` vs `ir_pair_arg`: `char_type` uses `ir_call_arg` (lowered via `is_builtin_exec` path, not pair-encoded). Verify before writing admission arms.
- Compound type materialisation: after `rt_pl_unify_struct_gz`, `term_deref(cell)` gives the compound Term. `tt->compound.args[0]` IS the inner variable cell — no separate `val_cell` needed.
- **Named arm order in `pl_gz_build_goal` is critical**: char_type arm must appear before the generic `} else if (gg->op == IR_BUILTIN && ival==2 && ir_pair_arg(gg,0) && ir_pair_arg(gg,1))` arm. char_type uses `ir_call_arg` not `ir_pair_arg`, so the guard would fail cleanly — but the returned-0 from the format/tcmp guard inside the comparator arm is the failure mode for any non-admitted builtin that falls through.
