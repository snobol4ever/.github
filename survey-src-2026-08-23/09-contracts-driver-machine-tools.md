# Survey 09 — src/contracts + src/driver + src/machine + src/include + src/tools (agent report, condensed verbatim)

## 1. INVENTORY
**contracts/ (17 files, 2836 LOC)**: IR.h 278 LIVE core · descr.h 83 LIVE core · SM.h 103 LIVE-vestigial (SM codegen deleted, only enum survives, 19 includers) · ast.h 233 LIVE · stage2.h 78 LIVE · zeta_choices.h 127 LIVE · zeta_storage.c/.h 882/46 LIVE (.h a dead letter, §6) · zeta_depth.c/.h 155/35 LIVE · scrip_ir.c 409 MIXED (dead debug tail) · ast_print.c 134 LIVE · **ast_verify.c 122 DEAD (zero callers, unbuilt)** · bb_program.h, pin_va.h, ab_abi.h, rk_opname.h, descr_tags.inc ~110 LIVE narrow.

**driver/ (18 files, 4032 LOC)**: scrip.c 1869 LIVE (**main() spans ~1080 lines, 790-1869**) · driver_call.c 400 MIXED (~240 lines dead, §3) · driver_data.c 427 LIVE (DatType registry, MRO) · driver_globals.c 89 LIVE · driver_hooks.c 156 LIVE · driver_label.c 89 LIVE · polyglot.c/.h 124/14 LIVE (.scrip/.md fenced multi-language) · stmt_ast.c 198 LIVE granted-AST-path · driver_ast_stubs.c 6 (fn proven dead §3) · scrip_sm.c/.h 36/9 LIVE · csnobol4_shim.c 119 TOOL (scrip-monitor only) · sync_monitor.c/.h 198/31 **DEAD STUB** ("codegen deleted…unavailable") · rs23_diag.c 87 TOOL (#ifdef RS23_DIAG, build_scrip_rs23_diag.sh) · driver.h 33, driver_private.h 147.

**machine/ (5 files, 156 LOC)**: bb_pool.c/.h 79/19 LIVE real (mmap RX slab) · sm_prog.c 51 LIVE real (owns stage2_t g_stage2) · bb_box.h 2 + bb_build.h 5 = **pure forwarding shims to include/bb_box.h — dead weight**.

**include/ (4 files, 126 LOC)** — grab-bag, no theme: bb_box.h 71 (Byrd-box runtime ABI: bb_box_fn, cap_t, α/β, Σ/Δ/Ω) · dtp.h 14 (pattern-pool allocator, sibling of machine/bb_pool.h) · emit_ir.h 9 · XA.h 32.

**tools/ (5 files, 723 LOC) — NONE built**: emit_per_kind_audit.c/.h 556/5 (backs dead --audit-per-kind flag) · demo_template_productions.c 30 DEAD orphan · tmatch_proto.c 86 DEAD scratch (80% #if 0) · test_template_byte_identity.c 46 DEAD via broken path (script expects it at src/runtime/x86/ which doesn't exist).

## 2. FLAG SURFACE (scrip.c main, 790-870)
--run (default) · --compile · --target=x86 (others "removed") · --dump-ast/-ir/-ir-verbose/-bb/-zeta · --transpile · --bench · --zeta=zls|zls2|zh · --zeta-port=plain|instrumented|alloc|inline|cstack|owned|forth|heap (**`owned`=5 defined in zeta_choices.h but NOT accepted by parser — silently absent**) · --zeta-storage=frame-rsp|cell-stack|cell-heap (frame-r12 rejected) · --monitor/--no-monitor · -o/-oFILE (**parsed TWICE — primary loop + second scavenging loop :835, redundant/fragile**) · -sN -mN -dN -iN (-d/-i ignored) · --audit-per-kind (**only argv[1], and unconditionally prints "unavailable (audit tool unlinked)" + exit 1 — whole flag dead**).
Undocumented in usage text: -o, --monitor family, entire --zeta* family, --audit-per-kind.

## 3. DEAD PARTS (grep-verified)
- contracts/ast_verify.c whole file.
- driver_ast_stubs.c:6 eval_ast() zero callers (rs23_diag's --wrap=eval_ast exists precisely to prove this). **g_exec_prog (same file :4) initialized NULL, never assigned anywhere.**
- **driver_call.c:139-376 — call_user_function's ~240-line AST-tree-walking interpreter body gated by `if (body && g_exec_prog)` → permanently unreachable (mode-1/2 residue). Compiled -fPIC into libscrip_rt.so — ships in every compiled program's runtime dependency.**
- sync_monitor.c:194-198 body = fprintf("[NO-SM-BB] … unavailable") + return -1.
- scrip_ir.c:191-192 IR_free_dyn no callers; :393-408 bb_print_v tail structurally unreachable (always-NULL locals).
- tools/: demo_template_productions.c + tmatch_proto.c zero refs; test_template_byte_identity.c script points at nonexistent path.
- scrip.c:1844-1852 two abort() canaries labeled "reached dead branch" — intentional.
- polyglot.c g_fi8_gen_init_count/g_fi8_pl_init_count — write-only counters.

## 4. MISPLACED
- **Dissolve src/include/**: bb_box.h → contracts/ · dtp.h → machine/ (sibling of bb_pool.h) · emit_ir.h + XA.h → emitter/.
- **Delete machine/bb_box.h + bb_build.h shims** (redirect 12+5 includers).
- **machine/sm_prog.c** owns g_stage2 (compiler-pipeline state, not slab) → move beside driver/scrip_sm.c; machine/ keeps bb_pool.* literally as "the RX slab".
- tools/test_template_byte_identity.c → fix path mismatch (either move or fix script).
- ast_verify.c: wire into a gate or delete. emit_per_kind_audit: relink or delete tool+flag together.

## 5. VIOLATIONS
- **Language identity survives past lower at scale: scrip.c computes is_icon/is_prolog/is_raku/is_pascal/is_sno_bb once (:876-894, sanctioned) then reads them 42 TIMES** deep into IR/BB/emission logic: gating optimizer_run (1114,1194,1650), rt_outer_call vs _delta0 at final call site (1836), zls_graph_name (1098,1282,1476,1682,1810), GVA strategy (1249-1253/1447/1553-1556), `const int is_raku` threaded into shared emit_module_init_body (444,669,735). The forbidden shape spelled as local ints instead of an enum.
- **Second undocumented dispatch point**: polyglot.c:64-124 re-dispatches by content-sniffed fence tag; actual extension set (.pl .icn .raku .reb .pas .scrip .md .sc) wider than CLAUDE.md's documented closed list (omits .scrip/.md).
- **Hardcoded absolute path breaking D-17 PORTABLE-HOME: csnobol4_shim.c:11 `#include "/home/claude/csnobol4/data.h"`** — fails from /home/claude_C, /home/claude_P.

## 6. DEPENDENCIES (include counts, repo-wide)
descr.h 83 · ast.h 48 · IR.h 31 · SM.h 19 (legacy) · stage2.h 14 · bb_box.h 12 · zeta_choices.h 11 · bb_program.h 11 · pin_va.h 9 · bb_pool.h 7 · bb_build.h 5 (shim) · XA.h 5 · dtp.h 4 · emit_ir.h/ab_abi.h/rk_opname.h 2 · **zeta_storage.h 1 (only its own .c!) · zeta_depth.h 1 (same)** — the declared public APIs of the two biggest contracts subsystems are included by NOBODY; all 12+ real consumers hand-write `extern zls_*/zdp_*` redeclarations. No compiler-checked prototype consistency — exactly the drift class descr_tags.inc's header warns about.
- Build boundary: RT_PIC_SRCS includes essentially all driver/*.c + contracts/*.c + machine/*.c; only scrip.c is the executable object. Intentional (EM-6) but ships dead interpreter (§3) in the .so.
- driver_private.h pulls ALL SEVEN frontend driver headers into every driver_*.c (driver_label.c, 89 lines SNOBOL4-only, compile-depends on Icon/Prolog/Raku internals).

## 7. NAMING
- SM.h/SM_op_t: vocabulary of a deleted mode kept alive via stage2.h typing (19 includers) — note-of-intent wanted.
- **Same-basename collision: machine/bb_box.h (2-line shim) vs include/bb_box.h (71-line real) — resolved only by -I order.**
- src/include/ name promises nothing; delete after moves.
- rs23_diag: opaque codename, no expansion in-tree.
