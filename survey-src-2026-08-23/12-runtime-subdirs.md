# Survey 12 — src/runtime/{core,builtins,rt,rtx} (agent report, condensed verbatim)

## 1. INVENTORY
core/core.c 3020 LIVE (SNOBOL4 builtin library, NV/FUNC tables, DATA registry, monitor wire, error tables) · core/core.h 431 LIVE umbrella (guard still `SNOBOL4_H`) · argval/coerce/name_save/stmt_exec small LIVE (stmt_exec's exec_stmt = deliberate abort-bomb "legacy executor deleted (B0)" — **still called from driver_call.c:214 + driver_hooks.c:12**) · **core/runtime_shim.h 142 DEAD** (3 includers, ZERO macro invocations anywhere) · builtins/gen_runtime.c/.h 283/107 MIXED (SCAN/&POS/<->/REPLACE hot half LIVE; GenFrame tree-interpreter half reachable only via runtime/invocation.c — plausibly mode-1/2 residue, MEDIUM confidence, needs targeted trace) · builtins/resolution.c/.h 137/83 MIXED (**resolve_cp_stack[4096]/Resolve_ChoicePoint jmp_buf design DEAD, zero reads/writes anywhere**) · **builtins/box_rt.h DEAD** (zero includers) · rt/rt.c 1972 LIVE (call/frame + Icon suspend/resume + Prolog choicepoint/retry/zeta-resume + RTCC/GVA pinning) · rt/rt.h 231 LIVE too fat · rt/gc_heap.c 712 LIVE compacting GC · rt/zeta_alloc.c + zeta_heap.c LIVE (ZLS/ZLS2/ZH) · rt/rt_arena.c MIXED (generic arena + 2 Prolog-only bump islands grafted in) · rt/rt_slab.c LIVE · rt/rt_protected.c MIXED (protected_pat_name_to_sm_op declared never defined) · **rt/pat_pool.c DEAD-ish: 4MB RWX pool allocated unconditionally at startup (scrip.c:1043); pat_pool_emit zero callers** · rt/rt_coexpr.c + bbprof.c LIVE · rt/bb_pat_build.cpp 116 LIVE (see §2) · rt_asm_helpers.S + rt_sg_scan.S LIVE · rtx/rtcc_init.c LIVE (register-cache spill, NOT RTX-family) · rtx/rtx_init.c LIVE (RTX_GATE A/B init + _Static_assert ABI pins) · rtx test files (alloc/str/unit/varval_test.c) TEST-SCAFFOLD compiled by scripts/test_rtx_unit.sh only · **rtx_str_bench.c + rtx_str_shim.c DEAD** (shim would symbol-collide if linked) · 15 rtx_*.S LIVE (each A/B-gated vs named C-of-record except always-on rtx_zdp.S) · rtx_abi.inc LIVE (Intel-syntax ABI contract).

## 2. LAYERING
rtx/ = hand-asm leaves + gate/ABI plumbing · rt/ = memory/scheduling substrate · core/ = umbrella API. **core/ and rt/ are mutually dependent, not a stack** (gc_heap.c:281 includes core.h for TBBLK/ARBLK/DATINST layouts; core files include rt/ headers).
**bb_pat_build.cpp: NOT a template despite name/location** — drives IR_alloc/optimizer_run/ir_drive_slot_assign/emit_chain AT RUN TIME to JIT pattern boxes for runtime-argument LEN()/BREAK() and dynamic pattern trees. Correctly lives in rt/; rename → rt_pat_jit.cpp.

## 3. DEAD PARTS
- pat_pool.c (4MB RWX + zero-caller emitter) · rt_protected.h:18 phantom decl · box_rt.h · runtime_shim.h · resolution.c:125-137 jmp_buf CP stack · core.h PUSH_fn/POP_fn/TOP_fn/STACK_DEPTH_fn declared, never defined/called · name_save.c NAME_entry_t unused · rtx_str_bench.c, rtx_str_shim.c.
- Landmine: exec_stmt abort-bomb with live driver callers (see survey 09's g_exec_prog finding — the gate condition is permanently false, so unreachable in practice; the two surveys agree).
- frame-r12 retirement: zeta_alloc.c:157 name string at index 0 is cosmetic residue (runtime setter range excludes it); zeta_choices.h still accepts 0 compile-time (only ZC_FRAME_DEAD5 has #error) — retirement enforced above this layer.
- GenFrame apparatus (gen_runtime.c ↔ invocation.c): MEDIUM-confidence dead; needs trace through all lower_*.c before deletion.

## 4. SPLIT/MERGE
- rt/rt.c 1972 → split by language: rt_call.c generic + Icon suspend/resume + Prolog retry/cp/zf_resume (mirrors rtx_icn*/rtx_plunify precedent).
- rt_arena.c: extract rt_pl_cterm_*/rt_pl_cellws_* Prolog islands.
- rt.h: split rt_pl.h (~40 Prolog-only decls of ~180).
- rtx/: subdirs rtx/sn4/, rtx/icn/, rtx/pl/ matching the three ARCH-*-RTX.md contracts.
- rtcc_init.c → rt/ (calling-convention concern, in rtx/ by directory-mate history).

## 5. VIOLATIONS (file:line)
- **core.h:428 + rt.h:228 declare functions AFTER the #endif include-guard close** — C++-linkage landmine (core.h: indirect_goto, _x4_pending_parent_frame, _command_pending_parent_frame; rt.h: rt_gvar_assign_concat_parts, rt_concat_parts_d, rt_nofail_abort).
- **Systemic backward dep: ~13 runtime files #include "sil_macros.h" from src/emitter/** (argval.c:7, core.c:4, stmt_exec.c:6, name_save.c:6, +9) — shared-ABI vocabulary misplaced in emitter/ (matches survey 05's move-to-core recommendation).
- stmt_exec.c:7-12 includes machine/emitter/lower/ast headers, none used by its two functions.
- **core.c:26 `#include "../../../scripts/monitor/monitor_wire.h"` — reaches outside src/ entirely.**
- resolution.h:4 + resolution.c:5 include SNOBOL4 parser scrip_cc.h with ZERO symbols used — cleanest single deletion candidate. (gen_runtime's same include is justified: EVAL/CODE parse runtime strings.)
- **core.c ~2513-2528: NPUSH_fn/NINC_fn/NPOP_fn carry UNCONDITIONAL fprintf(stderr,"SEQ%04d…") on every call — forgotten debug instrumentation on the hot N-stack path** (every other trace in the file is getenv-gated).

## 6. DEPENDENCIES
- **rt.h is a Makefile-forced prerequisite of EVERY object (Makefile:391,393)** — editing it rebuilds the world regardless of inclusion. ~40/180 decls are a Prolog sub-API.
- ABI-pinned struct ownership split inconsistently: DESCR_t/VCELL_t in contracts/descr.h but TBBLK/TBPAIR/ARBLK/DATBLK/DATINST in core/core.h — both GC-walked, both asm-pinned in rtx_init.c.
- rt_arena.h declares rt_ws_alloc/realloc/strdup/rt_agg_alloc — defined in gc_heap.c (header/file mismatch).
- **No -fvisibility=hidden on the .so build** — the whole ~10k-line surface exported by default (only RTX gate bytes + a few g_* opt into hidden).
- templates → rt_coexpr.h/rt.h includes (bb_activate/create/coret/cofail/call_bool): expected direction, fine.

## 7. NAMING
- Three prefixes need documenting: rtcc_ (register-cache, not RTX) · rtx_ (A/B-gated leaf family) · rt_ (general API).
- .S naming consistent: unprefixed=SNOBOL4/shared, icn*=Icon, plunify=Prolog.
- rt_asm_helpers.S: AT&T syntax (recorded deliberate exception) and RTX-gated but lives in rt/ not rtx/.
- rtx_zdp.S: the one ungated .S (always-on anchor check) — correct as designed, the auditing outlier.
