# ICON-BB handoff 2026-06-27b
## SCRIP fc64cac — PASS=208 (was 206)

### Session fixes (both mode-3 and mode-4, zero regressions)

**Fix 1 — scan double-emission (lower_icon.c, 1 line)**
TT_SCAN now sets `cx->beta = gs` so IR_GEN_SCAN is opaque.
Previously cx->beta leaked the inner body node; lower_every wired
IR_GEN_SCAN.γ into the body subgraph; codegen_flat_chain_body BFS
followed it and double-collected body nodes → every scan primitive
emitted twice, once inside flat_drive_gen_scan and once in the outer
chain with a fresh frame slot.
Symptom: `every ("hello world" ? write(upto(' ')))` printed `6` twice.
Punch-list item: TIER-B/B2 scan-double-emission.

**Fix 2 — match|fallback in scan body (emit_bb.c, ~14 lines)**
flat_emit_arg_subchain now calls ir_skip_alt_arms on entry and all
γ/ω queue pushes, and skips ir_node_is_alt_arm nodes (mirrors
codegen_flat_chain_body). flat_drive_gen_scan sets g_emit_cfg = body_sg
around body emission so ir_node_is_alt_arm can resolve arms.
Forward decls for ir_node_is_alt_arm / ir_skip_alt_arms added near the
flat_emit_arg_subchain forward decl.
Symptom: `"world" ? write(match("xyz") | 0)` produced nothing instead
of `0`.

### Remaining scan failures (next session)

1. **rung37_scan_alt** — `(A|B|C) ? move(1)` driven by `every` loops
   printing `a` instead of `a c e`. Two concrete defects in the asm:
   - Subject DESCR written to `[r12+0]/[r12+8]` but rt_scan_enter reads
     `[r12+(-1)]/[r12+7]` — off-by-one slot offset in how IR_GEN_SCAN
     resolves the subject producer slot.
   - Subject alternation's β never wired to the scan resume path — so
     `every` re-runs the same stale subject forever.
   Fix is in flat_drive_gen_scan: route the subject subchain's β back
   through rt_scan_enter to pull each next alternation arm.

2. **rung08_strbuiltins_find_gen** (rc=124 hang) — find() generator β
   doesn't advance. Punch-list TIER-B3: wire resume like bb_to.

3. **rung36_jcon_scan / scan1 / scan2 / endetab** (rc=134) — large
   integration programs; deferred until primitives above are solid.

### Suite baselines
mode-3 (--run):    PASS=208 FAIL=44 XFAIL=36 EXCISED=1 TOTAL=289
mode-4 (--compile): PASS=208 FAIL=44 XFAIL=36 EXCISED=1 TOTAL=289
Smokes: icon 12/12, snobol4 7/7, prolog 5/5
Gates: all four green

Authors this session: LCherryholmes, Claude Sonnet 4.6
