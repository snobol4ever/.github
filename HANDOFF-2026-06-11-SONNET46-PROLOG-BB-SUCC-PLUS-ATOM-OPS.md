# HANDOFF — 2026-06-11 — Sonnet 4.6 — PROLOG-BB PL-GZ-9 succ/plus + atom_ops (rung18+rung12)

**Goal:** GOAL-PROLOG-BB.md · PL-GZ-9 corpus reconquest.
**Watermark:** SCRIP `5a3e13f` · .github `06f5a6cb` (both pushed, battery green).

## Landed

Two batches in one session, 10 new m3 rungs total (+10 m4).

---

### Batch 1 — succ/2 + plus/3 (commit `70d4eb2`, m3 43→48 +5)

Root cause: both builtins were admitted by the legacy flat tier (`pl_flat_goal_is_simple` lines 323/328 in `scrip.c`) which mishandled them, emitting `[]` with rc=0 — silent-wrong on both m3 and m4, no abort, no signal.

Newly passing: rung18_succ_plus_succ_forward, succ_backward, plus_xy_bound, plus_xz_bound, plus_yz_bound.

#### New components

- **`IR_DET_SUCC_PLUS`** — new IR kind in `src/contracts/IR.h` + name table in `scrip_ir.c`.
- **`rt_pl_succ_plus_cell(long arity, void *a_cell, void *b_cell, void *c_cell)`** — new runtime function in `src/runtime/unification.c`. Semantics verified against SWI `pl-arith.c` PRED_IMPL succ/plus and cross-checked against m2 IR_interp blocks. arity=2: X-bound → fail if X<0 else Y=X+1; Y-bound → fail if Y≤0 else X=Y-1. arity=3: bitmask of bound args solves third via addition/subtraction. Trail-mark/unwind on all failure paths. Cell-based (void* is Term*), no `g_resolve_env`.
- **`bb_det_succ_plus.cpp`** — new BB template in `src/emitter/BB_templates/`. `edi=arity`, `rsi=FRQ(GZ_CELL_OFF(s0))`, `rdx=FRQ(GZ_CELL_OFF(s1))`, `rcx=FRQ(GZ_CELL_OFF(s2))` or `xor ecx,ecx` (arity=2). Single `call rt_pl_succ_plus_cell`. `test eax,eax; jne γ; jmp ω`. β→`jmp ω`. bomb arm for unadmitted shapes.
- **`bb_prepare` block for `IR_DET_SUCC_PLUS`** in `src/emitter/emit_bb.c`: `op_parts_ival[0]=arity`, `[1]=s0`, `[2]=s1`, `[3]=s2` (=-1 for arity=2).
- **`emit_core.c`** dispatch: `case IR_DET_SUCC_PLUS: { extern void bb_det_succ_plus(void); bb_prepare(nd); bb_det_succ_plus(); return 0; }`
- **Makefile**: `bb_det_succ_plus.cpp` in `RT_PIC_SRCS` + explicit compile rule.

#### Admission wiring (scrip.c, all four sites)

- **`pl_gz_rule_body_goal_ok`**: named arms for succ/2 (LOGICVAR/LIT_I for both args) and plus/3 (LOGICVAR/LIT_I for all three args), placed before the generic arity-2 comparator arm.
- **`pl_gz_rule_clause`** BUILTIN whitelist: `succ` arity 2 and `plus` arity 3 both `continue`.
- **`pl_gz_count_synth_goal`**: +1 per non-LOGICVAR arg for both succ/2 and plus/3.
- **`pl_gz_build_goal`**: named arm before the generic arity-2 arm; LIT_I args materialised via IR_CELL_UNIFY synth slots; emits IR_DET_SUCC_PLUS with `ival=arity`, operands = LOGICVAR slot nodes.

---

### Batch 2 — atom_length/concat/chars/codes/upcase_atom/downcase_atom (commit `5a3e13f`, m3 48→53 +5)

Newly passing: rung12_atom_builtins_atom_length, atom_concat, atom_chars, atom_codes, atom_case.

#### New components

- **`IR_DET_ATOM_OP`** — new IR kind in `src/contracts/IR.h` + name table in `scrip_ir.c`.
- **`rt_pl_atom_op_cell(const char *fn, void *a0_cell, void *a1_cell, void *a2_cell)`** — new runtime function in `src/runtime/unification.c`. Static helper `atom_op_text(Term*, buf, bufsz)` mirrors m2 `resolve_atomic_text`. Dispatches on fn: `atom_length` (strlen → unify int); `atom_concat` (GC_MALLOC concat → intern → unify); `upcase_atom`/`downcase_atom` (toupper/tolower loop → intern → unify); `atom_chars`/`atom_codes` (forward: walk atom text → build list of char-atoms or code-ints; reverse: walk list → reconstruct atom via buf). All paths trail-mark/unwind on failure. a2_cell is NULL for arity-2 builtins.
- **`bb_det_atom_op.cpp`** — new BB template. `rdi=ROQ(0)` (sealed fn string pointer in RO section), `rsi=FRQ(GZ_CELL_OFF(s0))`, `rdx=FRQ(GZ_CELL_OFF(s1))`, `rcx=FRQ(GZ_CELL_OFF(s2))` or `xor ecx,ecx` (arity≠3). `call rt_pl_atom_op_cell`. `test eax,eax; jne γ; jmp ω`. β→`jmp ω`. `.quad`/`.string` data section for fn name literal.
- **`bb_prepare` block** in `emit_bb.c`: `op_parts_str[0]=fn`, `op_parts_ival[0]=arity`, `[1]=s0`, `[2]=s1`, `[3]=s2` (=-1 for arity-2).
- **`emit_core.c`** dispatch: `case IR_DET_ATOM_OP: { extern void bb_det_atom_op(void); bb_prepare(nd); bb_det_atom_op(); return 0; }`
- **Makefile**: `bb_det_atom_op.cpp` in `RT_PIC_SRCS` + explicit compile rule.

#### Admission wiring (scrip.c, all four sites)

- **`pl_gz_rule_body_goal_ok`**: named arms for the five arity-2 atom ops (LOGICVAR/ATOM/LIT_I for a0; LOGICVAR/STRUCT for a1) and atom_concat/3 (LOGICVAR/ATOM for a0,a1; LOGICVAR for a2). All placed before the generic arity-2 comparator arm.
- **`pl_gz_rule_clause`** BUILTIN whitelist: the five arity-2 atom ops and atom_concat arity 3 all `continue`.
- **`pl_gz_count_synth_goal`**: +1 per non-LOGICVAR arg for atom_length/upcase/downcase (a0 only); +1 per non-LOGICVAR arg for atom_chars/codes (both a0 AND a1 — a1 can be a STRUCT list); +1 per non-LOGICVAR for atom_concat a0,a1.
- **`pl_gz_build_goal`**: named arms before the generic arity-2 arm. ATOM/STRUCT args materialised via IR_CELL_UNIFY synth slots. atom_chars/codes: a0 → ATOM/LIT_I through synth; a1 → STRUCT through synth (both materialised independently).

#### Key mid-stream bug

Initial atom_chars/codes build arm materialised non-LOGICVAR a0 correctly but passed a1 raw — a STRUCT list `[w,o,r,l,d]` as a1 was not recognised as needing materialisation, causing GATE-3 abort at runtime. Fix: STRUCT a1 also materialised through a synth slot. `pl_gz_count_synth_goal` updated in the same pass to count STRUCT a1 as +1.

---

## Gates at final commit `5a3e13f`

- GATE-1: m2/m3/m4 5/5 HARD ✓
- GATE-3: m2=114 · m3=**53**/62-FAIL (ratchet floor=53) · m4=**57**/41-FAIL+17excised ✓
- GATE structural: bb_bin_t=0 · g_vstack=0 · no-value-stack PASS ✓

## Next open in PL-GZ-9

Survey of remaining m3 failures (after the session):

```
rung10_programs_puzzle_01          — complex, skip
rung11_findall_*  (5 variants)     — findall/3: PT-2 re-land needed onto GZ path, larger work
rung14_retract_*  (5 variants)     — retract/1: dynamic DB mutation, non-trivial
rung15_abolish_*  (5 variants)     — abolish/1: dynamic DB mutation
rung17_sort_* (5 variants)         — sort/2, msort/2: deterministic, likely cheap
rung20_numbervars_* (5 variants)   — numbervars/3
rung21_char_type_* (4 variants)    — char_type/2: same recipe as atom_ops
rung26_copy_concat_* (5 variants)  — copy_term, atom_concat, string_to_atom
rung27_aggregate_*  (4 variants)   — aggregate_all/nb_setval/nb_getval
rung28_exceptions_* (5 variants)   — catch/throw
rung30_dcg_*        (5 variants)   — DCG phrase/3
rung43_findall_fail_meta           — findall variant
```

**Recommended first targets for next session:**
1. `rung21_char_type_*` — `char_type/2` follows the exact atom_op pattern: new `IR_DET_ATOM_OP` variant or a thin new IR kind, single runtime dispatch function.
2. `rung17_sort_*` — `sort/2` and `msort/2` are deterministic (no backtracking into them), well-bounded, already partially admitted in the rich path.
3. `rung20_numbervars_*` — `numbervars/3` is deterministic and the m2 implementation is self-contained.

## Session notes

- gprolog-master and swipl-devel-master reference zips extracted at `/home/claude/refs/` (persistent across the session, from original uploads).
- The "named arm before generic arm" rule is critical in `pl_gz_build_goal` — succ/plus, atom ops, format/2, =.., and all named builtins must appear before the generic `IR_BUILTIN && ival==2` arm or they get intercepted and rejected.
- `pl_gz_count_synth_goal` must be updated in lockstep with `pl_gz_build_goal` — every synth slot allocated in build must be counted in synth, or `ncells` underestimates and the frame overflows.
- The `ir_pair_arg` vs `ir_call_arg` distinction matters: `ir_pair_arg(gg,i)` is for arity-2 builtins stored as IR_BUILTIN with pair encoding; `ir_call_arg(gg,i)` is for all others. succ/2 uses `ir_pair_arg`; plus/3 uses `ir_call_arg`.
