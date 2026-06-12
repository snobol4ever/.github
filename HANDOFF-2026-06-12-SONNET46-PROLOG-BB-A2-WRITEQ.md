# HANDOFF-2026-06-12-SONNET46-PROLOG-BB-A2-WRITEQ.md

## Session summary

**Goal:** GOAL-PROLOG-BB.md — A2 writeq/write_canonical GZ admission.

**What landed:** SCRIP `84ae655` · `.github` `ef55117c`

## Work done

### A2 — writeq/write_canonical GZ admission (+3 m3, partial)

**Files changed:** `src/driver/scrip.c`, `src/emitter/BB_templates/bb_det_write.cpp`

**Mechanism:** Extended `IR_DET_WRITE` with a write-mode discriminator in `IR_LIT(nn).ival`:
- `ival=0` → `rt_pl_write_cell` (existing `write`)
- `ival=1` → `rt_pl_writeq_cell` (new `writeq`)
- `ival=2` → `rt_pl_write_canonical_cell` (new `write_canonical`)

Both runtime functions already existed in `unification.c`. The build arm synthesizes a CELL_UNIFY slot for non-LOGICVAR args (ATOM/STRUCT) then passes the slot to `IR_DET_WRITE` with the mode ival.

**Four scrip.c sites touched:**
1. `pl_gz_rule_body_goal_ok` — admission check (LOGICVAR/ATOM/STRUCT args)
2. `pl_gz_rule_clause` whitelist
3. `pl_gz_count_synth_goal` — counts +1 synth for ATOM/STRUCT arg
4. `pl_gz_build_goal` — new `else if` arm before generic arity-2 block; also added `pl_gz_arith_to_struct` helper (available but not yet wired)

**bb_det_write.cpp:** Three `IF(_.op_sb && _.op_ival == N, ...)` arms replacing the single `IF(_.op_sb, ...)` arm.

**Why only +3 not +4:**
`write_canonical(1+2)` arg lowers as `IR_ARITH` (not `IR_STRUCT`). In m3 the CELL_UNIFY sh=0 path embeds a live IR node pointer in `.quad` — valid in-process but crashes in m4 separate-process. The ARITH case was explored (IR_CELL_UNIFY sh=0 extended, `pl_build_term_gz_r` extended, `pl_gz_arith_to_struct` converter) but reverted to avoid a m4 ratchet violation. The one affected file (`rung22_write_canonical_write_canonical_ops.pl`) stays m2-only; it hits the GZ FENCE on m3/m4.

**Gate results (final):**
- GATE-1: m2 5/5 · m3 5/5 · m4 5/5 ✅
- GATE-3: m2 114/115 · m3 **71**/115 (was 68) · m4 **56**/115 (unchanged)
- seg_byte=0, g_vstack=0 ✅
- PL-HY-FENCE: **PRE-EXISTING FAIL** (not introduced by this session — see below)

## Pre-existing issue: PL-HY-FENCE gate

`test_gate_bb_one_box.sh` reports FAIL on `bb_binop_concat_slot.cpp`. This predates our session — the STRIP-WRAPPER commit `a1a2191` (landed before we started) renamed `bb_binop_concat_slot_str→bb_binop_concat_slot` across 108 files but missed this one. The file still has `std::string bb_binop_concat_slot()` (old C++ style) and no `extern "C" void bb_binop_concat_slot(void)` entry wrapper. Fix: add `extern "C" void bb_binop_concat_slot(void) { bb_emit_x86(bb_binop_concat_slot()); }` and rename the inner fn — but the inner function is also named `bb_binop_concat_slot` which conflicts. The inner function needs a rename to `bb_binop_concat_slot_str` first.

## Next step recommendation

**A3 — rung24 string_ops (+5 m3):** `atom_string/2`, `number_string/2`, `string_length/2`, `string_concat/3`, `string_upper/2`, `string_lower/2` — extend `IR_DET_ATOM_OP` dispatch in `rt_atom_op` (already handles `atom_length`, `upcase_atom`, `atom_chars`, etc.). Admission recipe is identical to the existing ATOM_OP builtins. Four scrip.c sites + `bb_det_atom_op.cpp` + `unification.c` or `string_ops.c`.

## Session setup for next session (GOAL-PROLOG-BB)

```bash
cd /home/claude/SCRIP && bash scripts/install_system_packages.sh
make -j4 scrip && make libscrip_rt
bash scripts/test_smoke_prolog.sh         # GATE-1
bash scripts/test_prolog_rung_suite.sh    # GATE-3 (expect m2=114 m3=71 m4=56)
bash scripts/test_gate_bb_one_box.sh      # PL-HY-FENCE (pre-existing fail on bb_binop_concat_slot)
grep -rnE 'seg_byte\(SEG_CODE|SL_B\(' src/ --include="*.c" --include="*.cpp" | grep -v "_templates/" | grep -v emit_core.c | wc -l   # 0
grep -rn 'g_vstack' src/ | wc -l          # 0
```
