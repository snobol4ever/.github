# HANDOFF-2026-06-12-SONNET46-PROLOG-BB-A3-A4-A5PARTIAL.md

**Goal:** GOAL-PROLOG-BB.md — PL-GZ-9 corpus reconquest A3/A4/A5.
**Watermark:** SCRIP `c718f58` · .github `(this commit)` (both green).

## Landed

### A3 — rung24 string_ops (+6 m3, +6 m4). GATE-3 m3 71→77, m4 56→62.

**Files changed:** `src/runtime/unification.c`, `src/driver/scrip.c`

Extended `rt_pl_atom_op_cell` with six new dispatch arms:
- `string_length` — strlen via `atom_op_text`
- `string_upper`/`string_lower` — toupper/tolower loop → intern
- `atom_string`/`string_to_atom` — bidirectional: if t0 bound, text(t0)→unify(t1); else text(t1)→unify(t0)
- `number_string`/`atom_number` — bidirectional: if t0 bound, text(t0)→unify(t1); else parse t1 as int/float→unify(t0) via strtol/strtod
- `string_concat` — mirrors `atom_concat` (arity-3, cat→t2)

Four scrip.c sites updated:
1. `pl_gz_rule_body_goal_ok`: extended `is_atom2` with 8 new names; a1ok now includes IR_ATOM (for reverse-direction `atom_string`); a0ok now includes IR_LIT_F; `atom_concat` guard extended to also match `string_concat`
2. `pl_gz_rule_clause` whitelist: both new arity-2 names and `string_concat` arity-3
3. `pl_gz_count_synth_goal`: same extended condition
4. `pl_gz_build_goal`: `else if` condition extended; `string_concat` arity-3 arm reuses atom_concat code path, passing `catfn` through to `IR_LIT(nn).sval`; sa1 synthesis now handles both IR_STRUCT and IR_ATOM; sa0 handles IR_LIT_F

### A4 — rung25 term_string/term_to_atom (+3 m3). GATE-3 m3 77→80.

**New files:** `src/emitter/BB_templates/bb_det_term_string.cpp`
**Modified:** `src/contracts/IR.h`, `src/contracts/scrip_ir.c`, `src/emitter/emit_bb.c`, `src/emitter/emit_core.c`, `src/emitter/BB_templates/bb_templates.h`, `Makefile`, `src/runtime/unification.c`, `src/driver/scrip.c`

`IR_DET_TERM_STRING` — new IR kind. `rt_pl_term_string_cell(void *term_cell, void *str_cell)`: creates a pipe, `dup2(pipefd[1], STDOUT_FILENO)`, calls `pl_writeq(t)`, restores stdout fd, reads from pipefd[0] into buf[4096], interns, unifies. The dup2/pipe approach is process-global (works in m4 separate-process unlike the old `stdout = ms` assignment). `bb_det_term_string.cpp`: rdi=FRQ(s_term), rsi=FRQ(s_result), call, test/jne γ/jmp ω/def β/jmp ω.

Four scrip.c sites: a0ok = LOGICVAR|STRUCT|ATOM|LIT_I|ARITH. IR_ARITH build path calls `pl_gz_arith_to_struct(ts0)` first (enables `term_to_atom(1+2, A)`).

**m4 gap:** rung25 m4 0/3. `term_string(point(3,4), S)` — the synth slot's `IR_CELL_UNIFY` embeds the live `IR_STRUCT` pointer as `.quad` in the emitted TEXT, which is invalid in a separately-linked binary. Same root cause as the 17 excised m4 cases. Not a regression; no ratchet violation.

### A5 partial — rung26 infra

**New files:** `src/emitter/BB_templates/bb_det_copy_term.cpp`
**Modified:** `src/contracts/IR.h`, `src/contracts/scrip_ir.c`, `src/emitter/emit_bb.c`, `src/emitter/emit_core.c`, `src/emitter/BB_templates/bb_templates.h`, `Makefile`, `src/runtime/unification.c`, `src/driver/scrip.c`

`IR_DET_COPY_TERM` added everywhere. `rt_pl_copy_term_cell`: iterative var-map (Term* pairs, cap=256), `copy_term_deep` recursive (var→fresh, atom/int/float→same, compound→new compound with copied args). `bb_det_copy_term.cpp`: same 2-slot FRQ pattern.

`atomic_list_concat`/`concat_atom` arms added to `rt_pl_atom_op_cell`: list walk, sep insertion, concat → intern → unify result_cell (t2 for arity-3, t1 for arity-2).

scrip.c sites 1+2 updated for `atomic_list_concat`/`concat_atom`/`copy_term`.

**INCOMPLETE: scrip.c sites 3+4 not written.** rung26 still fails m3 (GZ FENCE).

## Gates

- GATE-1: m2 5/5 · m3 5/5 · m4 5/5 ✅
- GATE-3: m2=114 · m3=**80**/115 (ratchet floor=80) · m4=**62**/115+17excised ✅
- seg_byte=0, g_vstack=0 ✅

## Next session — start here

```bash
cd /home/claude/SCRIP && bash scripts/install_system_packages.sh
make -j4 scrip && make libscrip_rt
bash scripts/test_smoke_prolog.sh          # GATE-1
bash scripts/test_prolog_rung_suite.sh     # GATE-3 (expect m2=114 m3=80 m4=62)
```

### Step 1 — Finish A5 (rung26): write scrip.c sites 3+4

**Site 3 (pl_gz_count_synth_goal)** — add after the `term_string` block (around line 1010):
```c
if ((!strcmp(fn,"atomic_list_concat")||!strcmp(fn,"concat_atom")) && (IR_LIT(gg).ival == 2 || IR_LIT(gg).ival == 3)) {
    IR_t *al0 = ir_call_arg(gg,0), *al1 = (IR_LIT(gg).ival == 3) ? ir_call_arg(gg,1) : NULL;
    if (al0 && al0->op != IR_LOGICVAR) (*nsynth)++;
    if (al1 && al1->op != IR_LOGICVAR) (*nsynth)++;
}
if (!strcmp(fn,"copy_term") && IR_LIT(gg).ival == 2) {
    IR_t *ct0 = ir_call_arg(gg,0);
    if (ct0 && ct0->op != IR_LOGICVAR) (*nsynth)++;
}
```

**Site 4 (pl_gz_build_goal)** — add before the comparator `else if` (after the `term_string` arm):

For `atomic_list_concat` arity-2 and arity-3 (reuse `IR_DET_ATOM_OP`, fn=`"atomic_list_concat"`):
- arity-2: synth-slot al0 (IR_STRUCT/IR_ATOM → IR_CELL_UNIFY); al1 must be LOGICVAR; emit `IR_DET_ATOM_OP` with sval=`"atomic_list_concat"`, ival=2, operands [al0_slot, al1]
- arity-3: synth-slot al0; synth-slot al1 if IR_ATOM; al2 must be LOGICVAR; emit `IR_DET_ATOM_OP` with sval=`"atomic_list_concat"`, ival=3, operands [al0_slot, al1_slot, al2]

For `concat_atom` arity-2: same as alc arity-2, sval=`"concat_atom"`.

For `copy_term` arity-2:
- synth-slot ct0 (IR_STRUCT/IR_ATOM/IR_LIT_I → IR_CELL_UNIFY); ct1 must be LOGICVAR; emit `IR_DET_COPY_TERM` with operands [ct0_slot, ct1]

### Step 2 — After rung26 passes

Check what rung26 m4 does (likely same struct-pointer gap).

### Step 3 — B1 (rung11/43 findall, +6 m3)

`pl_gz_rule_body_goal_ok` needs a findall arm for `IR_BUILTIN` findall — call `pl_findall_conj_member_admissible`. See GOAL-PROLOG-BB.md B1 for details.

### Step 4 — Commit and push

Per RULES.md: commit SCRIP first, then `.github` last.

## Key facts for next session

- `atom_op_text` already handles TERM_ATOM/INT/FLOAT — the list walk in `atomic_list_concat` uses it per-element
- `pl_gz_arith_to_struct` exists at ~line 1053 in scrip.c — use for IR_ARITH terms in term_to_atom
- Named arm order in `pl_gz_build_goal` is critical: new arms must come BEFORE the generic `else if (gg->op == IR_BUILTIN && ival==2 && ir_pair_arg(...))` comparator arm
- `ir_call_arg` for `is_builtin_exec`-lowered builtins; `ir_pair_arg` for pair-encoded arity-2 comparators
- m4 ATOM_* warning: always `prolog_atom_intern(".")` not `ATOM_DOT` in GZ runtime helpers
- 200-char line max, zero blank lines, only dashed-separator comments in C code
