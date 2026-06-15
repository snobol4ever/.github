# HANDOFF 2026-06-15 — Icon native real-arithmetic path (WIP, **NOT landed**)

**Author:** Claude Sonnet · **Trigger:** GOAL-ICON-FULL-PASS "real-arithmetic runtime path".
**Status: RED — do NOT push as-is.** The change is ~90% done; m3 gains are real but there are **two regressions** (one m3, two m4) that net m4 **worse** (25→27 FAIL). Two precise fixes remain (below). The full working-tree diff is preserved at `WIP-icon-real-arith-2026-06-15.patch` (apply with `git -C /home/claude/SCRIP apply <patch>` on top of HEAD `462a5cd`). The SCRIP tree currently still carries these uncommitted edits.

## Goal
Make Icon real/mixed binops run natively (m3/m4): `rung17_real_arith_real_add` (`x:=1.5;y:=2.5;write(x+y)`→4.0), `rung18` real relops (`real_gt`,`mixed_relop`,`real_eq`,`real_lt`,`real_relop_goal`). Per Lon's rule: add **value-only** RT (two `DESCR_t` in, one out; NO four-port logic) and let the box own the ports.

## What was implemented (7 files — all in the patch)
1. **`src/runtime/arithmetic.c`** — new `DESCR_t rt_num_arith(DESCR_t a, DESCR_t b, int op)`: Icon int/real/mixed coercion (`anyf = lf||rf`; ADD/SUB/MUL/DIV/MOD/POW), div-by-zero→`FAILDESCR`, matching the attic-interp reference (`src/attic/IR_interp.c` ~537). Pure value, no ports. Added `#include "builtins/gen.h"` for `BINOP_*`. Max line 191.
2. **`src/runtime/by_name_dispatch.c`** — `rt_jct_relop` got an **additive** real/mixed branch BEFORE the int-int fast path: `if (num_rel && (IS_REAL||IS_REAL) && both-numeric) { double compare }`. Improves SNOBOL4/Prolog real relops too; int-int + string paths untouched.
3. **`src/emitter/emit_globals.h`** — new representation flag `int op_num_real;` after `op_relop_descr`.
4. **`src/emitter/emit_bb.c`** — static helpers after `descr_binop_opnd_slot`: `var_assigned_real_static`, `binop_operand_real_static` (LIT_F→1; VAR→scan graph for `IR_ASSIGN(name,LIT_F-rhs)`; BINOP/ALT→recurse; depth≤8), `binop_is_num_real` (ADD..MOD or LT..NE **and** a real operand), and `descr_binop_set_slots(nd)` (sets `op_num_real`, resolves `op_sa/op_sb` via `bb_slot_get` LIT_F-inclusive + `bb_slot_alloc16`, else falls back to `descr_binop_opnd_slot`). Wired `descr_binop_set_slots` into **both** `flat_drive_binop_tree` tail AND `flat_drive_binop_gen_tree` tail AND the non-walk descr branch (~3014). Reset `op_num_real=0` at `case IR_BINOP` top.
5. **`bb_binop_arith.cpp`** — real arm gated on `op_num_real`: marshal both DESCRs (rdi:rsi / rdx:rcx, op→r8d) → `call rt_num_arith` → `cmp eax,DT_FAIL; je ω` → store rax:rdx → γ. Int arm got `&& !_.op_num_real`. Max 175, 0 blanks.
6. **`bb_binop_relop.cpp`** — int payload-compare arm gated `!op_num_real && LT..NE`; the rt_jct_relop call arm now fires on `(op_num_real && LT..NE) || (SLT..SNE)` — one call body, real-numeric + string merged, no duplication. Max 192, 0 blanks.
7. **`src/driver/scrip.c`** — `local_assign_rhs_ok_g` LIT_F guard relaxed `return !graph_has_binop(g)` → `return 1`. **THIS IS THE SOURCE OF REGRESSION #1 (see below).**

## Verified results (rebuilt clean, `WARN=-w`)
- **rung17**: m3 5/5, m4 5/5 — `real_add` PASS both modes. ✅
- **rung18 m3**: `real_gt`,`mixed_relop`,`real_eq`,`real_lt` PASS; `real_relop_goal` EXCISED.
- **rung18 m4**: `real_lt` PASS; `real_gt`,`mixed_relop`,`real_eq` **FAIL rc=1** (dup-label, regression #2); `real_relop_goal` EXCISED.

## FAIL-diff vs baseline (HEAD `462a5cd`: m3 25 FAIL, m4 25 FAIL)
- **m3 (run) → 24 FAIL.** FIXED: `rung18_real_relop_mixed_relop`, `rung18_real_relop_real_gt`. NEW (regression): **`rung19_pow_toby_pow_var`**. (Also EXCISED→PASS, not shown in FAIL-diff: `real_eq`, `real_lt`, `rung17 real_add`.)
- **m4 (compile) → 27 FAIL.** FIXED: none. NEW (regressions): **`rung18_real_relop_real_eq`** (EXCISED→FAIL) and **`rung19_pow_toby_pow_var`**. (`real_gt`/`mixed` were already m4-FAIL; rc changed 134→1.)

**Net: m3 −1 (but with a regression), m4 +2 (worse). Hence NOT pushed.**

## The two remaining fixes (both root-caused, well-scoped)

### FIX 1 — `rung19_pow_toby_pow_var` regression (m3 AND m4)
`x:=3.0; write(x^2)` → expected `9.0`. The relaxed gate (`local_assign_rhs_ok_g` LIT_F `return 1`) now **admits** this graph, but `x^2` is `BINOP_POW`, which is (a) NOT in `binop_is_num_real` and (b) routed by `binop_slot_kind` to `IR_BINOP` (generic), not `IR_BINOP_ARITH` — so it never reaches the new real arm. Result: `; [walk_bb_node: kind=7 unhandled]` garbage instead of the clean baseline EXCISE.
**Fix:** keep POW-bearing LIT_F-assign graphs EXCISED. Add `static int graph_has_pow(const IR_graph_t *g)` (scan for `IR_BINOP && IR_LIT(nd).ival==BINOP_POW`) and change the guard to `if (rhs && rhs->op == IR_LIT_F) return !graph_has_pow(g);`. `real_eq/real_lt/real_gt/mixed/real_add` contain no POW → still admitted. (Proper native real-POW is a separate item: route POW→`bb_binop_arith` and add POW to `binop_is_num_real`; `rt_num_arith` already computes `REALVAL(pow(ld,rd))`.)

### FIX 2 — m4 duplicate-label assembler error (`rung18` real_gt/mixed/real_eq)
The **root_node tree path** (`bb_build_flat`/`codegen_flat_build` → `codegen_flat_body` → `flat_drive_binop_tree`) RE-walks the LIT_F operands that were ALREADY emitted as chain nodes, producing the same `bb<id>_α` label twice. m3 (binary emitter) silently tolerates duplicate labels; m4 (`as` on the text) errors → `rc=1`. `real_lt` is fine in m4 because it has local assigns → `root_node==NULL` → the **chain path** (`descr_flat_chain_build`), which walks each operand once and the binop's non-walk branch reuses the slot.
**Fix:** in `flat_drive_binop_tree`, before walking each child, skip the walk if the child is already slotted (`bb_slot_get(child) >= 0`) and instead `emit_jmp_label(<child>_done, JMP_JMP)` — the value is already in its slot (the chain produced it earlier in execution order). `descr_binop_set_slots` already resolves via `bb_slot_get`, so it will pick up the original chain slot. Verify the β/retry edges still wire correctly (the skipped child has no β of its own). Confirm with `gcc -c <dump>.s` that the dup-label `as` errors disappear.

**After both fixes, expected:** m3 **+5** and m4 **+5** (real_gt, mixed, real_eq, real_lt, real_add), zero regressions. `rung18_real_relop_real_relop_goal` stays EXCISED — it is `every write(3.0<(2.5|3.5|4.5))`, a **generator (`every`+`ALT`) over a real relop**; the binop real arm is in place but the gen-alt resume machinery is the separate `cross_arg`/gen-resume track, not this one.

## Gate to run before landing (the discipline)
```bash
cd /home/claude/SCRIP && bash scripts/build_scrip.sh && make libscrip_rt
bash scripts/test_icon_rung_suite.sh --mode run     > /tmp/run.txt
bash scripts/test_icon_rung_suite.sh --mode compile > /tmp/comp.txt
# explicit FAIL-name diff vs baseline (stash + rebuild to regenerate baseline lists):
#   /tmp/base_run_names.txt , /tmp/base_comp_names.txt were captured this session
bash scripts/test_smoke_icon.sh      # 12/12 m3+m4 HARD
bash scripts/test_smoke_prolog.sh    # 5/5 m3+m4 (m2=0 is the phantom-interp artifact)
bash scripts/test_gate_icn_no_stack.sh ; bash scripts/test_gate_icn_one_reg_frame.sh   # =0
```
A net +PASS can hide an EXCISE→FAIL — always do the explicit FAIL-name diff (that is exactly how regression #2 surfaced).

## Notes / rules honored
- RT (`rt_num_arith`, `rt_jct_relop` real branch) is **value-only**, no α/β/γ/ω. Boxes own the ports.
- Templates dispatch on `op_num_real` (a representation flag), not language — `op_num_real` is set only in the `g_descr_flat_chain` (Icon) path; SNOBOL4/Prolog use `bb_binop_gvar_*` and never read it. New arms are pure `x86()` (medium-invisible), no `bb_bin_t`, 0 blank lines, 120-char separators.
- `DESCR_t` returns in **rax:rdx** (the union's int64/ptr members make the 2nd eightbyte INTEGER-class even with the `double`); the marshalling mirrors the proven `rt_call_arr` / relop string-arm convention.
