# FINDING 2026-07-22 (Claude) — SN4: beauty self-host blocked by two independent floods; fix plan

**Goal:** GOAL-SNOBOL4-BB. **Session directive:** "Get beauty self host. Fix the stupid name manufacturing."

## WHAT WAS DONE THIS SESSION (TWO CODE CHANGES, BOTH LANDED)

### Change 1 — IR_MATCH_VALUE: kill the PATTMP$P manufactured-name flood (SITE 1)
The prior-session finding (FINDING-2026-07-22-CLAUDE-SN4-MATCH-VALUE-OPERAND-KILL-MANUFACTURED-NAMES.md)
correctly diagnosed that `PATTMP$P%d` names (site 1, `lower_snobol4.c:1466`, eager `TT_FNC` in pattern
position) manufacture a global name + IR_ASSIGN + IR_MATCH_DEFER per occurrence, flooding `GLOBAL_MAX=4096`
and contributing to the zls tables.  This session implemented the full fix:

**Files changed (all in SCRIP repo, committed):**
- `src/contracts/IR.h` — added `IR_MATCH_VALUE` enum after `IR_MATCH_DEFER` with doc comment
- `src/contracts/scrip_ir.c` — name table entry `[IR_MATCH_VALUE] = "IR_MATCH_VALUE"`
- `src/optimizer/ir_query.c` — `IR_MATCH_VALUE` in `ir_is_generator_kind` (mirror DEFER)
- `src/contracts/zeta_storage.c` — 16B pad slot grant + `zls_locals_shifted` (mirror DEFER)
- `src/emitter/emit.cpp` — template dispatch (`bb_match_value()`) + `emit_drive` field setup + both ω-chain BFS conditions
- `src/templates/bb_templates.h` — `std::string bb_match_value();` prototype
- `src/templates/bb_match_value.cpp` — NEW FILE: the template (DEFER clone, name-lookup replaced by `lea rdi, FR(_.op_a_slot)` + `rt_match_value_get_pat_fn`, *X owed-call loop dropped)
- `src/runtime/pattern_match.c` — `rt_match_value_get_pat_fn(DESCR_t*)` + `rt_match_value_open(DESCR_t*)` runtime functions
- `src/lower/lower_snobol4.c` — site 1 rewritten: `IR_MATCH_VALUE` with `ir_operand_push(mv, vr)`, no `sno_reg_var`, no `IR_ASSIGN`, no name mint
- `Makefile` — `bb_match_value.cpp` added to `RT_PIC_SRCS` list and explicit compile rule

**Validation:** reproduction test (`/tmp/mv_test.sno`) passes byte-identically vs SPITBOL oracle
for both the scalar-value path (`PASS1`) and the DT_P compiled-pattern path (`PASS2`).  Builds
clean (`make scrip` rc=0, `make libscrip_rt` rc=0).

### Change 2 — LBL__ re-lowering: kill the O(n²) mark-table flood for EVAL/CODE programs
When `g_sno_uses_code` is set (beauty.sno uses CODE/EVAL 3×), the DEFINE loop re-lowered the ENTIRE
statement array once per labeled statement to create `LBL__<name>` pseudo-procs that `rt_goto_transfer`
can reach at runtime.  This means `sno_build_graph` (which calls `zls_group_mark` for every statement
label inside it) ran N_label times on the same N_label-statement program = N² marks.  beauty has ~163
labels across its 17 files → 163² ≈ 26,000 marks → overflow at 8192 on the FIRST COMPILATION.

**Fix:** share main's `bb_idx`; set `proc_entry_node` to the label's existing `bb_label_landing(lbl)`
anchor (already in the registry from main's single build).  `bb_proc_entry()` in `gen_runtime.h` resolves
`proc_entry_node` before falling back to `g->entry`, so each `LBL__` proc emits from the right anchor
using main's slot layout.  Zero re-lowering, zero extra marks, zero extra graphs in `bbp`.

**File changed:** `src/lower/lower_snobol4.c` lines 2085-2101 (replaces `gl = sno_build_graph(...)` +
`bb_program_add(&g_stage2.bbp, gl)` with `proc_entry_node = bb_label_landing(lbl)` + shared `bb_idx`).

## CURRENT SELF-HOST STATUS

**Still failing at `zls: mark table overflow (8192)`.** The LBL__ fix is correct and the code is landed,
but beauty still overflows.  The diagnostic histogram after the fix shows the same numbers as before:
- 8192 marks, 27 distinct graphs, dollar_names=52, plain_names=8140
- First/last 20 names are real program labels (`START`, `G1`, `lwr`, `upr`, `cap`, ...)

**Root cause of remaining overflow: the DEFINE loop also re-lowers the full statement array.**
`lower_snobol4.c:2120` — when a DEFINE has no body block (its function body is just a labeled range in the
main program, the common SNOBOL4 style), `sno_build_graph(st, nst, eidx, is_def, rn)` is called with the
FULL main-program statement array.  beauty has 78 DEFINEs; a significant fraction (~39 confirmed by grep)
use the main-program label form.  These generate the 27 distinct graphs seen in the histogram (the
remainder share identical label sets).

**The fix for DEFINE re-lowering follows the SAME pattern as the LBL__ fix:**
Each DEFINE that points to a main-program label (line 2118-2120, `eidx >= 0` branch) should also
share main's `bb_idx` and use `proc_entry_node = bb_label_landing(defs[di].entry)` instead of calling
`sno_build_graph(st, nst, eidx, is_def, rn)`.  DEFINE bodies (line 2113-2114, the `def_body[di]` branch)
ARE their own graphs and must remain as-is; only the "entry-in-main" branch needs the fix.

## THE REMAINING FIX (NEXT SESSION START HERE)

In `src/lower/lower_snobol4.c`, the DEFINE loop at ~line 2103:

```c
// CURRENT (floods mark table):
} else {
    int eidx = -1;
    for (int i = 0; i < nst; i++) { const char * lbl = sfind_str(st[i], ":lbl"); if (lbl && !strcmp(lbl, defs[di].entry)) { eidx = i; break; } }
    if (eidx < 0) continue;
    gf = sno_build_graph(st, nst, eidx, is_def, rn);  // <-- THE FLOOD: full re-lower
}
int fpi = stage2_proc_grow(&g_stage2);
g_stage2.proc_table[fpi].bb_idx = bb_program_add(&g_stage2.bbp, gf);  // <-- adds graph
```

Replace with:

```c
// FIX: share main's graph, set proc_entry_node to the label's anchor
} else {
    IR_t * enode = bb_label_landing(defs[di].entry);
    if (!enode) continue;
    gf = NULL;  /* no new graph */
    int fpi = stage2_proc_grow(&g_stage2);
    g_stage2.proc_table[fpi].name = defs[di].fname;
    /* ... fill other fields as normal ... */
    g_stage2.proc_table[fpi].bb_idx = g_stage2.proc_table[pi].bb_idx;  /* share main */
    g_stage2.proc_table[fpi].proc_entry_node = enode;
    continue;  /* skip the bb_program_add below */
}
```

⚠ CAREFUL: the `gf` variable is used AFTER the if/else block to fill `proc_table[fpi]` fields (name,
nparams, lower_sc, is_generator, etc.).  The cleanest rewrite is to restructure the else-branch to register
the proc inline (before `continue`) rather than falling through.  See lines 2122-2131 for the full field list
to copy.

After applying the DEFINE fix, re-run beauty self-host.  If the mark table still overflows, instrument
again with `ZLS_DUMP` to find any remaining source (EXPR$ thunks from sno_expr_thunks_build are also graphs
but they are small and their mark counts are bounded by the expression count, not O(n²)).

## ACCEPTANCE GATES (unchanged from prior finding)
- `scrip --run beauty.sno < beauty.sno` byte-identical to oracle: 622 lines, md5 `9cddff2534472b822438801d8db58a99`
- `test_crosscheck_snobol4.sh` m3 FAIL=0 m4 FAIL=0 SKIP=0 DIVERGE=0
- `test_gate_template_medium_invisible.sh --strict` + `test_gate_em_template_byte_identity.sh`
- Smokes sno 7/7 ×2 modes
- `.s` artifact regen: `util_regen_benchmark_s_artifacts.sh`, `util_regen_feature_s_artifacts.sh`, `util_regen_demo_s_artifacts.sh`

## KEY PATH MAP (for next session orientation)
- `src/lower/lower_snobol4.c:2103-2131` — the DEFINE loop; lines 2113-2114 = body-branch (keep), 2116-2120 = entry-in-main branch (fix)
- `src/contracts/zeta_storage.c:38` — `zls_group_mark`: one call per label per `sno_build_graph` call; overflow at 8192
- `src/lower/lower_snobol4.c:1740` — the sole `zls_group_mark` call site (inside `sno_build_graph`)
- `src/contracts/gen_runtime.h:50-56` — `bb_proc_entry()`: resolves `proc_entry_node` before `g->entry` fallback
- `src/driver/scrip.c:1150` — uses `proc_entry_node` for mode-4 TEXT emit
- `src/driver/scrip.c:1431` — uses `proc_entry_node` for mode-3 native emit

## BUILD STATE AT HANDOFF
- `scrip` binary: built, rc=0, at `/home/claude/work/SCRIP/scrip`
- `libscrip_rt.so`: built from prior session run (18986696 bytes, Jul 22 16:24); needs rebuild after next edit
- All changes: committed and pushed to origin/main (see git log)
- ZLS diagnostic instrumentation: REVERTED (clean source)
- PATTMP$P site 1: GONE from lower_snobol4.c
- LBL__ O(n²) fix: LANDED but insufficient alone — DEFINE loop fix is the remaining blocker
