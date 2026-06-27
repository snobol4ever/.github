# HANDOFF 2026-06-24 (Claude) — PB-BENCH-3: zebra GREEN, arity-4 bug fixed, nested-arith + `//` landed

## Result
Bench suite `corpus/benchmarks/prolog/bench`: **green=7 frontier=4 broken=0** (was 6/5/0).
- **GREEN added:** `zebra` (m3∧m4, byte-identical to `zebra.expected`).
- Rung suite **115/115 in m3 (--run) and m4 (--compile)**; smoke 5/5 m3+m4.
- m2 (`--run`) remains 0/115 / 0/5 — PRE-EXISTING unwired `--run` at HEAD (prior handoff documented this); NOT touched this session.
- Artifacts: 7 real `.s` (`fib mu nreverse qsort queens_8 tak zebra`) + 4 `.s.FENCED` (`crypt deriv meta_qsort sendmore`).

## Three changes landed (all tested, floor-safe)

### 1. `zebra` GREEN — slot caps were a conservative guard, not an ABI limit
`rt_frame()` (`src/runtime/rt/rt.c:88`) returns `static int64_t g_frame_buf[4096]` and `GZ_CELL_OFF(s)=8+8s` (`bb_template_common.h:24`) is unbounded — the main frame holds 4096 cells. Callee frames (`rt_enter`, `unification.c:84`) are `GC_malloc(8+8*nslots)`, dynamic. So the 64-slot ceiling in `pl_gz_admit` was purely conservative.
- `src/driver/scrip.c`: `>= 64 → >= 2048` (LOGICVAR slot-index bounds, lines ~379 + ~2022); `g->nslots > 64 → > 2048` (~1974); `*cslot + N > 62 → > 2046` (control-cell reserve, 6 sites).
- **The actual zebra blocker:** `pl_gz_rule_clause` capped a CALLEE clause at `cg->nslots > 16` (line ~651) → `> 2048`. zebra/1 is a ~80-slot callee of `main`. Callee frames auto-size via `arity+nlocals+nchild` (emit_bb.c:1215), confirmed; no register/ABI change.
- Left `ngoals > 64` / `goals_buf[64]` / `ngoals > 32` (line ~695) UNCHANGED — zebra/1 has 17 goals.

### 2. Pre-existing ARITY-4 bug FIXED — synth count vs build mismatch
The prior session's "arity 3→4" raise added the 4th SysV reg `r8` and the `ar > 3 → > 4` ceilings, but MISSED the synth-slot **count** side. The count loops in `pl_gz_count_synth_goal` (~1284), `pl_gz_nsynth_chain` (~747), `pl_gz_clause_nsynth` (~769) were capped `for (ai = 0; ai < ar && ai < 3; ...)` while the **build** loops (`pl_gz_build_goal` ~1396, `pl_gz_callee_body_node` ~884) use `ai < ar`.
- Symptom: an arity-4 call with **all-non-var** args (e.g. `main :- f(1,2,3,4).`) counts 3 synth slots but builds 4 → `ncells` is 1 short → the `IR_CELL_CALL` child-slot (`cslot = ncells`) collides with arg-3's cell, and `rt_pl_gz_init(frame, ncells)` under-initializes it. `rt_enter` then overwrites arg-3 with the callee frame pointer (`lea rdi,[r12+32]` == arg-3 cell). Silent wrong/no output (NOT a fence, NOT a crash).
- Why it hid: every prior test/rung with arity-4 had its 4th arg as a **variable** (needs no synth slot), so count==build by luck. `nest.pl`'s `run(3,4,5,R)` worked for exactly this reason.
- Fix: the three count loops → `ai < ar` / `ai < ar2`. Verified `f(1,2,3,4)→3`, two-`is` arity-4→correct, nested arity-4→77; floor held 115/115.
- **This is the prerequisite for arity≥5** (the count side now scales to any arity).

### 3. Nested arith in `is/2`/comparisons + `//`,`div`,`/`
New helpers in `src/driver/scrip.c` (after `pl_gz_struct_slot_map`): `pl_gz_flat_arith_op_ok`, `pl_gz_arith_nested_ok`, `pl_gz_arith_node_count`, `pl_gz_expr_nsynth`, `pl_gz_arith_emit_is`, `pl_gz_arith_flatten`. The flattener walks an arith tree bottom-up, emitting one flat `IR_DET_IS` (var-op-var / var-op-lit) per internal node into a fresh synth slot, returning the leaf. Normalizes `lit OP var → var OP var` (materializes the lit into a slot) because the emitter has const / var-op-lit / var-op-var arms but NO lit-op-var arm.
- `rt_runtime.c`: added `//`/`div` (integer, `(long)a/(long)b`) + `/` (float) to `rt_pl_is_cell_arith` and `//`/`div` to `rt_pl_is_cell_bivar` (`/` already present).
- `emit_bb.c`: appended `//`/`div`/`/` to the op-sets in `gz_arith_var_plus_const` (~998) and `gz_arith_var_bivar` (~1011) so they reach arms 1/2 instead of bombing (-2).
- Admit: `pl_gz_cmp_operand_ok` and the is/2 arm in `pl_gz_rule_body_goal_ok` now call `pl_gz_arith_nested_ok`. Synth counting: `pl_gz_cmp_nsynth` and both is/2 count sites use `pl_gz_expr_nsynth` (= `2 * node_count`, a safe over-bound).
- **SCOPE:** only the CALLEE build path (`pl_gz_callee_body_node` is/2 + cmp arms) got the flatten logic — crypt/sendmore arith is in callee clauses (`sum`,`mult`,`sumdigit`). The generic main-clause `pl_gz_build_goal` is/2 arm (~1515) still handles only flat shapes; a main clause with nested arith FENCES (safe, not a bomb). Extending the generic path is straightforward future work (call `pl_gz_arith_flatten` with `ar=0,lbase=0` — identity slot map — and `*synth_next`).

### NOT landed — `nbodies` 8→16 (reverted)
Raising `pl_gz_choice_inline`/`pl_gz_choice_rule_clauses` `nbodies > 8 → > 16` (+ choice arrays `consts[16][8]`,`clause_head[16]` in `box_state.h`) admits `digit/1`(10)/`leftdigit/1`(9) AND deriv's `d/3`(10). deriv then **miscompiles → `broken`** (its structure-build-in-head + repeated-head-var machinery is absent — the "cap-bump segfaults" the prior session proved). Since sendmore is fenced on arity-8 anyway, this yielded no green, so it was reverted to keep `broken=0`. box_state.h is back to clean (verified `git status` empty for it).
- **To re-land safely:** add a fence rejecting choice/rule clauses whose head args are ARITH-functor compounds (deriv's `U+V`, `DU+DV`) but NOT list-struct compounds (zebra's `[B,A|_]` must still pass). Then `digit`/`leftdigit` (simple `digit(0)` int-fact heads) admit while deriv stays fenced. Location: `pl_gz_rule_clause` head-unify check (lines ~696-705, currently `u1->op == IR_STRUCT continue` accepts all structs) and/or `pl_gz_fact_clause_units`.

## Corrected PB-BENCH-3 triage (supersedes prior STATE)
| program | blockers (corrected) |
|---|---|
| crypt | `top/16` arity + **CUT** (`!`, fenced at IR_CUT) + nested-arith ✅ + `//` ✅ + list-struct call args. Cut is the gating rung. |
| sendmore | `solve/8` arity (needs arity≥5 hybrid; count side ✅ now) + nested-arith ✅ + **ITE-in-callee-clause** (`sumdigit`, rejected at `pl_gz_rule_clause` IR_ITE) + nbodies-16 (gated). Most reachable. |
| deriv | nbodies-16 (gated) + structure-build-in-head + repeated-head-var. PL-BB-2/3. |
| meta_qsort | `clause/2` + `call/N` meta rail. PL-BB-5. |

## Next-session ARITY≥5 plan (sendmore)
Keep registers for args 0–3 (≤4 path byte-identical ⇒ 115-floor safe); pass args 4+ through the callee's freshly-`rt_enter`'d frame cells:
- `bb_cell_call.cpp`: after `mov rdi,rax` keep the ≤4 reg-FOR; ADD `FOR(4, nargs, …)` doing `mov r11,[r12+GZ_CELL_OFF(arg_slot_i)]; mov [rax+GZ_CELL_OFF(i)],r11` (rax = callee frame, still live; r11 scratch). Raise `bcc_sh: op_parts_ival[1] <= 4 → <= 8` and extend `bcc_ar` to check `op_parts_ival[3..3+nargs-1]`.
- `bb_callee_frame.cpp`: cap the register-store FOR at `min(arity,4)` (args 4+ already in cells); `rt_pl_cells_init` already starts at `arity`. Raise the `op_parts_ival[0] > 4 → > 8` gate.
- `scrip.c`: `ar > 4 → ar > 8` at the admit gates (`pl_gz_rule_body_goal_ok` ~481, `pl_gz_rule_inline_check` ~714, `pl_gz_choice_inline` ~416, `pl_gz_choice_rule_clauses` ~445, `pl_gz_callee_body_node` ~820, `pl_gz_build_goal` ~1396). `pl_gz_call_state_t.args[8]` holds 8 exactly; `op_parts_ival[16]` holds arg slots at [3..10].
Then ITE-in-callee (`pl_gz_rule_clause`: allow `IR_ITE`, and `pl_gz_callee_body_node`: build it — the generic `pl_gz_build_goal` already has an `IR_ITE` arm to mirror) + the gated nbodies-16.

## Verification commands
- Bench: `bash scripts/test_bench_prolog_modes.sh` (expect `green=7 frontier=4 broken=0`).
- Floor: `bash scripts/test_prolog_rung_suite.sh` (expect run+compile 115/115).
- Regen artifacts: `bash scripts/util_regen_prolog_bench_s_artifacts.sh "<rung>"` (uses `timeout 12` per program — a transient host-load timeout can mislabel a green program FENCED; re-run if `emitted` < 7).
- One program m4: `./scrip --compile --target=x86 bench/<p>.pl > p.s 2>p.err </dev/null`; `as --64 -o p.o p.s && gcc -no-pie -o p.bin p.o out/libscrip_rt.so -lgc -lm -lstdc++ -Wl,-rpath,out`; `timeout 30 ./p.bin | diff - bench/<p>.expected`.

## Commits (this session)
- SCRIP: `src/driver/scrip.c` (zebra caps, arity-4 count fix, nested-arith helpers + admit/count/build), `src/emitter/emit_bb.c` (`//`/`div`/`/` op-sets), `src/runtime/rt_runtime.c` (`//`/`div`/`/` evaluators). `box_state.h` UNCHANGED (nbodies reverted).
- corpus: `bench/zebra.s` (new, FENCED removed); `bench/fib.s mu.s queens_8.s tak.s` re-emitted (arity-4 count fix changes their slot numbering — still green).
- .github: this handoff + GOAL-PROLOG-BB STATE watermark `7 GREEN / 4 frontier`.

NOTE: prior session's commits were "pending push awaiting user token". Local commits made; **push still needs the user's credential.**
