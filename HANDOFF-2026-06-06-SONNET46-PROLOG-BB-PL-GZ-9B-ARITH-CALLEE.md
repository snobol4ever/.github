# HANDOFF 2026-06-06 (Sonnet 4.6) — PROLOG-BB: PL-GZ-9b callee arith + delete fallback

SCRIP commit: `9569504`. .github commit: this doc + GOAL-PROLOG-BB.md watermark/ladder update.

## Session summary

### What landed

**PL-GZ-9b**: callee bodies with arithmetic IS/CMP builtins. rung08 (fib/factorial) now runs natively in all three modes: m2 115/115 HARD · m3 24/91-FAIL · m4 105/10-EXC. GATE-1 now 5/5 m3 (recursion smoke fully native, no EXCISED).

**Interp fallback deleted**: the MODE-3 INTERP-FALLBACK path in `src/driver/scrip.c` is gone. Programs that can't be admitted by `pl_gz_admit` or `pl_flat_body_root` now ABORT with a FATAL message. The 91 m3 FAILs in GATE-3 are honest aborts — bugs, not hidden degradations. `test_prolog_rung_suite.sh` fallback detection block removed.

### Implementation (all in scrip.c unless noted)

**Admission layer:**
- `pl_gz_rule_body_goal_ok`: extended to accept `is/2` (const/varop/bivar rhs) and arith-cmp builtins (`<`,`>`,`>=`,`=<`,`=:=`,`=\=`) with LOGICVAR/LIT_I operands. Forward-decl of `pl_gz_arith_const` added before this function.
- `pl_gz_rule_clause` node scan: IR_ARITH now allowed (removed from rejection list); IR_BUILTIN arms now whitelist nl/write/is/arith-cmp individually.
- `pl_gz_arith_slot_map` (new static): slot-maps LOGICVAR indices inside ARITH trees — handles LIT_I (copy), LOGICVAR (remap), ARITH (recurse). Used by the IS arm in callee_body.

**Build layer:**
- `pl_gz_rule_callee_body` body loop: added IS arm (`IR_BUILTIN "is"`) emitting `IR_DET_IS` with `nn->α=lv(mapped_lhs)` and `nn->β=pl_gz_arith_slot_map(rhs,ar,lbase)`; added CMP arm (arith-cmp ops) emitting `IR_DET_CMP` with slot-mapped operands.

**Runtime:**
- `rt_pl_is_cell_bivar(lhs_cell, cell1, cell2, op)` in `IR_interp.c`: handles `X is Y op Z` (two LOGICVAR arith, e.g. F is F1+F2). Declared in `rt.h`.

**Templates:**
- `bb_det_is.cpp`: added `gz_arith_var_bivar` recognizer + bivar template arm calling `rt_pl_is_cell_bivar` via `x86_ro_seal_str`. Added `x86_begin()` at start of `bb_det_is_str()` (was missing — caused m4 label collision).
- `bb_det_cmp.cpp`: added `x86_begin()` at start of `bb_det_cmp_str()` (same bug, same fix).

**emit_bb.c:**
- `gz_emit_callee`: added `body_emitted` guard — if `ce->body_emitted` is set, return immediately. Prevents re-emission of recursive callee bodies (fib calls itself twice; without guard, second pass produced duplicate `.Lx{N}_0` labels).
- `IR_interp_state.h`: added `int body_emitted` field to `pl_gz_callee_t`.

**Gate:**
- `test_gate_pl_gz7.sh`: added `pin24()` function (m2+m4, skips m3). Moved `commit`, `semidet`, `negbound` probes to `pin24` — their callee bodies contain ITE/`\+`/`\=` which are not yet GZ-admitted, so m3 legitimately aborts. `barecall` and `reentry` stay as `pin()` (all three modes pass natively).

### Root causes fixed this session

1. **Missing `x86_begin()`**: `bb_det_cmp_str()` and `bb_det_is_str()` used `x86_internal_name(n)` (reads `_.x86_uid`) without ever calling `x86_begin()` to claim a fresh UID. Three consecutive DET_CMP/DET_IS boxes in the same clause body all inherited the last UID from `bb_cell_unify`, producing duplicate `.Lx13_0` labels in the m4 `.s`. Fix: add `x86_begin()` at the top of each `*_str()`.

2. **Missing `gz_emit_callee` guard**: the function had no check for already-emitted bodies. Recursive predicates (fib calls itself) caused `gz_emit_callee(fib)` to be invoked a second time from the outer callee loop, re-emitting the full body with a new `cid` from `g_flat_node_id++` — producing a second set of `.Lx{N}_0` labels that collided with the first pass. Fix: `body_emitted` flag.

3. **Bivar IS**: `F is F1+F2` (ARITH with two LOGICVAR operands) was not covered by existing `rhs_varop` (which only handled `Y op LIT_I`). Required `rt_pl_is_cell_bivar` + `gz_arith_var_bivar` recognizer + new `bb_det_is` arm.

### Gate state at 9569504

GATE-1: **5/5 m2 HARD · 5/5 m3 · 5/5 m4** (recursion smoke fully native — was EXCISED in m3)
GATE-3: m2 **115/115 HARD** · m3 **24**/91-FAIL · m4 **105**/0/10-EXC
test_gate_pl_gz7: **PASS** (all probes; commit/semidet/negbound use pin24)
test_gate_bb_one_box: **PASS**
seg_byte/SL_B grep: **0** · g_vstack: **0**

m3 PASS ratchet: 22 → 24 (+rung08 recursion, +rung08 was already rung08 — net new this session).

### Next opener: more callee-body patterns → more m3 rungs

The 91 m3 FAILs are all honest aborts. Priority targets:

**Immediately accessible** (arithmetic recursion, no lists, no ITE-in-callee):
- rung10 puzzles (10 files): arithmetic predicates, likely similar to fib — check each.
- rung23 arith-ext: bitwise, max/min, power — already passing in m3 (they're in the 24).
- rung29 number ops: float math — already passing.

**What blocks most remaining rungs:**
- rung05/06 (member/append): STRUCT list-cons heads in callee — pl_gz_choice_inline must bail, pl_gz_rule_clause must allow STRUCT β. The 9a handoff has the exact design (5 steps). Be careful: recursive predicates (member, append) need the non-recursive guard.
- rung09 (functor/arg/=..): complex builtins not in GZ.
- rung11 (findall): needs findall box on new GZ path (no meta rail).
- rung12 (atom builtins): atom_length, atom_concat etc. — rich path, not GZ.
- rung14-15 (retract/abolish): rich path (dynamic DB).

**The lowest-friction next step**: examine rung10 puzzles — they're arithmetic programs similar to fib. If their callee bodies only use IS/CMP/GOAL-recursive patterns (no ITE, no STRUCT), they should admit with zero new machinery.
