# FINDING 2026-07-22 (Claude) — SN4: kill manufactured pattern names; match by VALUE OPERAND, not by global name

**Goal:** GOAL-SNOBOL4-BB. **Session intent:** beauty suite → beauty self-host.
**Directive (Lon, this session):** *"Get rid of stupid names being manufactured regardless of where. You do not need them."* This finding records the root cause, why the previously-recorded plan (extend the s123 PAT$/EXPR$ dedup) was the WRONG path, and the correct fix in enough detail to implement without re-deriving it.

## MEASURED THIS SESSION (faithful baseline — build reproduces the s123 cursor)
- Clean build of `scrip` + `out/libscrip_rt.so` from origin. **Beauty suite (SN-7 gate): PASS=48 FAIL=3**, the 3 = `omega_driver`×3 — byte-identical to the s123 LIVE CURSOR. Build is faithful.
- **Oracle machinery is ALREADY CORRECT — no fix needed there.** `scripts/util_run_beauty_oracle.sh` already invokes `sbl -bf` (banner-off + `-f` case-sensitive, per RULES.md case-sensitivity). `beauty.sno` self-beautify under `sbl -f` runs **rc=0, 622 lines**, md5 `9cddff2534472b822438801d8db58a99`. That 622-line output is the byte-identical acceptance oracle for full-program self-host. ⚠ TRAP FOR THE NEXT SESSION: running `sbl -b` WITHOUT `-f` segfaults (rc=139) with `semantic.inc(16): ERROR 217 duplicate label` — a SPURIOUS collision because default case-folding merges label `shift`/`reduce` with function `Shift`/`Reduce`. beauty.sno REQUIRES case-sensitivity to keep `Shift`(fn) and `shift`(label) distinct. Always oracle beauty with `-f`.
- **scrip --run self-beautify dies at `zls: mark table overflow (8192)`** (`src/contracts/zeta_storage.c:40`, `abort()`), 0 lines out. `zls_reset()` IS called (lower/eval/pat-build) — this is genuine per-compilation VOLUME, not a missing-reset leak. Cap-bumping is proven NOT the fix (s123 diagnostic: with caps raised, `PATTMP$P3128` still floods `GLOBAL_MAX=4096`, then zls fields flood).

## ROOT CAUSE — the manufactured names ARE the bug, and here is exactly what they do
SNOBOL4-in-SCRIP matches deferred/computed patterns **by NAME**. When a pattern element is a computed expression (not a bare variable), the lowerer INVENTS a global name, compiles the expression into its OWN separate IR thunk-graph, registers that graph in the stage2 proc table under the invented name, and emits a match node that at match time looks the name up and runs the thunk. The name is the KEY binding {pattern-expression occurrence} → {its compiled thunk-proc}. This does not scale: one invented global + one thunk-proc PER OCCURRENCE, against finite budgets (`GLOBAL_MAX=4096` in `gen_runtime.h`; the zls tables). beauty.sno's many pattern-position expressions exhaust them.

### The four manufacture sites (all in `src/lower/lower_snobol4.c`)
1. **`PATTMP$P%d`** — line **1466** (`g_pattmp_pat_n++`), case `TT_FNC` (eager value-returning call in pattern position, e.g. `S ? Func(x)`). Emits `IR_ASSIGN(name) ; IR_MATCH_DEFER(name)`. **UNDEDUPED — this is the beauty/omega flood (`PATTMP$P3128`).** The value node from `sx_lower` is already an operand on the ASSIGN (line 1471); the name only couriers it to the adjacent DEFER.
2. **`EXPR$%d`** — via `sno_expr_collect` (def line **80**; call sites **215, 279, 1194, 1278, 1319**), for deferred `*expr` with a computed inner. s123 deduped this by structural `sno_expr_eq`. Each surviving distinct EXPR$ still becomes a named thunk in `sno_expr_thunks_build` (line ~1996).
3. **`PAT$%d`** — via `sno_pat_collect` (def line **1544**; call sites **966, 1792**), stored/frozen patterns. s123-deduped.
4. **`PATTMP$%d`** — line **1762** (`g_pattmp_n++`), replacement/match path.

### The name-resolution is fully name-based at runtime (verified — no value path exists to route to)
- `bb_match_defer.cpp` reads `_.op_sval` (a STRING) and calls `rt_defer_get_pat_fn(varname,…)` / `rt_defer_open(varname,…)` (`src/runtime/pattern_match.c:879,951`) → stage2 proc table lookup by name.
- `bb_match_atp.cpp` also reads `_.op_sval` and calls `rt_at_cursor(varname,…)` — ATP is the `@var` cursor matcher, NOT a general value-pattern matcher. It cannot be reused.
- `sno_expr_thunks_build` (line ~1996) compiles each `EXPR$n` into its own `IR_graph_t` and registers it in `g_stage2.proc_table` under the name. This IS the thing the name keys.
**Conclusion: there is no existing `IR_MATCH_*` op that takes a VALUE OPERAND. So killing the names REQUIRES adding one. This is NOT a lowering-only change.**

## WHY THE PREVIOUSLY-RECORDED PLAN WAS WRONG
The s123 cursor + LANDED dedup treats the flood as "too many duplicate names → deduplicate them." That polishes the smell. Deduping still manufactures a name per DISTINCT expression and still routes match-by-name; it just delays the wall. The directive is correct: the IR graph already contains the computation — feed the matcher the VALUE, drop the name entirely. Dedup (`sno_expr_collect`/`sno_pat_collect` structural-eq machinery) becomes UNNECESSARY, not something to extend.

## THE FIX (IR + runtime + template, both mediums — NON-NEGOTIABLE codegen-doc reads first)
Before writing ANY template / `x86_asm.h` code, read `ARCH-ICON.md` and `GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md` (RULES.md rule 6). Then:

1. **IR:** add `IR_MATCH_VALUE` to `src/contracts/IR.h` (beside `IR_MATCH_DEFER`, line ~139). It carries the pattern as an **operand** (`ir_operand_push`), NOT `op_sval`. Semantics = "match the pattern VALUE in operand[0] at the current cursor," identical control edges to DEFER (γ=succeed/advance, ω=fail, β=resume for a generator pattern value).
2. **Lower — eager `TT_FNC` (site 1):** replace lines 1465–1472 with: `IR_t * vr=NULL; IR_t * ec = sx_lower(cx, t, <succ-ward>, fail, &vr);` then `IR_t * mv = lc_build(g, IR_MATCH_VALUE, succ, NULL); sno_ω_to(mv, fail); ir_operand_push(mv, vr);` and wire `ec`→`mv`. NO `sno_reg_var`, NO name, NO IR_ASSIGN. Eager-once semantics preserved: expr lowered once before the match node (manual Ch.6 — a value-returning call in pattern position is evaluated once and its result used as the pattern).
3. **Lower — deferred `*expr` (site 2, `TT_DEFER` computed arm, line 1194):** the value must be RE-evaluated per match visit, so operand[0] must be a *thunk value* re-run on each open. Two options — pick per ARCH-ZETA: (a) keep a compiled-thunk value but reference it by OPERAND/subgraph edge instead of a global name (retire the name key, keep the thunk); (b) fold the thunk graph inline as a suspending pattern-value producer. (a) is the smaller step and still kills the name.
4. **Runtime:** `rt_match_value_open(DESCR_t patval, …)` + `rt_match_value_step(...)` replacing the name-lookup entries for the value path (model on `rt_defer_open`/`rt_defer_step` in `pattern_match.c`, but taking the DESCR value directly instead of `varname`→table lookup).
5. **Template:** `bb_match_value.cpp` — consume operand[0]'s value via `bb_emit_x86`'s in-band L/J/D/E/F record walk; ONE `x86(...)` per instruction, medium switched INVISIBLY inside the encoder (add encoders to `x86_asm.h` if missing). NO `MEDIUM_*`. Must pass `scripts/test_gate_template_medium_invisible.sh --strict` and `test_gate_em_template_byte_identity.sh`.
6. **Retire:** delete all four manufacture sites and the `sno_expr_collect`/`sno_pat_collect` dedup helpers + `g_sno_exprs`/`g_sno_pats` tables + `sno_expr_thunks_build`'s name registration (or reduce it to operand-linked thunk values per 3a). Confirm `grep -n 'PATTMP\$\|EXPR\$\|PAT\$%d' src/lower/lower_snobol4.c` == 0.

## ACCEPTANCE / GATES
- **Self-host (the goal):** `bash scripts/util_run_beauty_oracle.sh --input .../beauty.sno --output /tmp/ref` (md5 `9cddff25…`, 622 lines) === `scrip --run beauty.sno < beauty.sno` === `scrip --compile` build+run. Currently scrip dies at zls-mark; success = byte-identical to the 622-line ref, both modes.
- **No regression:** `scripts/test_crosscheck_snobol4.sh` m3 FAIL=0 m4 FAIL=0 SKIP=0 **DIVERGE=0** (watermark 307/x). Stash-verify byte-identical to pre-change where a program's output shouldn't move.
- **Both-medium:** the two gate scripts above.
- **`.s` artifacts:** touches codegen → RULES.md handoff step 4 (`util_regen_benchmark_s_artifacts.sh` / `util_regen_feature_s_artifacts.sh` / `util_regen_demo_s_artifacts.sh`).
- **Smokes:** sno 7/7 ×2 modes.

## STATE FOR NEXT SESSION
- No code changed this session (diagnosis + direction only). Build faithful, oracle correct, root cause + fix specified above.
- omega_driver AND semantic_driver AND beauty self-host all sit behind THIS fix (the zls/global flood is the common wall; semantic_driver additionally has the exit-crash JIT continuation `0x0000000700000001` — separate, MONITOR-FIRST per RULES.md, but only reachable once the flood is gone).
- NEXT ACTION: read the two codegen docs, add `IR_MATCH_VALUE`, do site 1 (eager `TT_FNC`) first as the reference conversion (it is the flood and the simplest), re-measure beauty self-host, then sites 2–4.
