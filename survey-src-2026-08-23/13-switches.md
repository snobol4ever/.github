# Survey 13 — Compile-time switch census: the passover-cleaning table (agent report, condensed verbatim)

**Lon's directive (s268, verbatim in substance):** identify the major #define switches governing compile-time behavior; the four ZETA modes are ONE now — delete all combinations, remove the guards, leave the proper raw code. Too many switches, all for the history that got us here.

**Scope measured:** 381 files under src/, 890 `#if`-family directives (244 #ifdef, 393 #ifndef, 191 #if, 62 #elif), 442 getenv() sites naming **351 unique env vars**. **Only ~8 env vars are ever set by the 456-script test suite** (SCRIP_BETA_ELIDE_OFF, SCRIP_DWARF_LOC, SCRIP_KW_DIRECT, SCRIP_STMT_FRAME, SCRIP_TRACE, SCRIP_ZSM, MONITOR_BIN, MONITOR_READY_PIPE) — 98% of switches have never been flipped by any automated path; the compiled default is what every gate has ever exercised. (Caveat: script check is substring-level, directional not per-var certified.)

## 1. THE BIG TABLE
| Switch | Arms | Live arm | Guard sites | Verdict | Est. lines freed |
|---|---|---|---|---|---|
| g_platform/PLATFORM_X86 family | X86\|JVM\|NET\|JS\|WASM | X86 | **193 sites/145 files**; PLATFORM_{JVM,NET,JS,WASM} have ZERO call sites outside emit.h's own defs | **COLLAPSE** (biggest single item) | 300–500 |
| ZC_STORAGE (frame-r12\|frame-rsp\|cell-stack\|cell-heap) | 4 (r12 CLI-errors) | cell-stack | see §2 | **COLLAPSE** | see §2 |
| ZC_PORT (8-value ladder) | 8 | forth (=cell-stack) | see §2 | **COLLAPSE** | see §2 |
| ZC_FRAME (isle\|dead5\|rsp) | 3 (dead5 #error) | rsp | 2 tautology #if in rt.c:1431,1507 (no #else) + rt_zc_frame_live() wrapper, 30 sites/5 files | **COLLAPSE** (rt.c guards provably no-op) | ~10 + §2 |
| ZC_ZETA (zls\|zls2\|zh) | 3 | zls2 | dispatch via g_zeta_mode read in rt.c/gc_heap.c/by_name_dispatch.c; zeta_heap.c (151 ln, ZH) + rt_zls_* legacy half of zeta_alloc.c appear unreached; --zeta= flag has ZERO uses in scripts/ | **INVESTIGATE→likely COLLAPSE** | ~150+ |
| ZC_COLLECTION (malloc\|arena\|gc) | 3 (gc #error) | malloc | pattern_match.c:1551,1561 | **COLLAPSE** | ~15 |
| ZC_INIT/ZC_POISON | ZERO/NONE/CLONE × OFF/FILL | ZERO | zeta_alloc.c:46-48 — poison #elif unreachable given ZC_INIT default | **COLLAPSE** | ~4 |
| ZC_COEXPR_STACK_GCHEAP | 2 | 1 | rt_coexpr.c:54,67,92 | **COLLAPSE** | ~15 |
| ZC_SELFLOAD | 5 | OFF | x86_asm.h:487,2015 + zeta_storage.c:755 (diag) | **COLLAPSE** (delete ALLOC arm) | ~10 |
| ZC_SPAN_GUTS (inline\|call) | 2 | inline | 12 hits/5 files | **INVESTIGATE** | — |
| ZC_LIT_GUTS (unroll\|inline\|call\|range) | 4 | unroll | 20 hits/4 files | **INVESTIGATE** (byte-diff sweep first) | — |
| ZC_TELEMETRY/ZC_OVERFLOW/ZC_PROMOTE | 2 each | ON/BOMB/GATE | 1 site each | PROMOTE **COLLAPSE** (#error stub); others INVESTIGATE | small |
| ZC_* numeric capacities (CSET_CHAIN_MAX, ARENA_MB, ZLS2_MB, HEAP_MB, WSI_MB, ZBLOCK_KB) | — | tuned | 1–7 each | **KEEP** (tuning, not modes) | 0 |
| MEDIUM_TEXT/BINARY/g_medium | 2 | both | 164 sites, 142 in x86_asm.h, ZERO in bb_*.cpp | **KEEP** — the dual-medium mechanism, not a config switch | 0 |
| SCRIP_DEF_I2D_MAGIC (=0) | 2 | off | bb_binop_arith.cpp 1 #if | **COLLAPSE** | ~13 |
| SCRIP_DEF_ARITH_FUSE (=1) | 2 | on | fuse_on() | **COLLAPSE** (inline constant) | ~3 |
| **DYN_ENGINE_LINKED (Makefile -D everywhere)** | — | — | **0 guard sites in src/** | **DELETE the -D — dead flag** | 0 |
| **IR_DEFINE_NAMES (Makefile -D, rt objects)** | — | — | **0 guard sites in src/** | **DELETE — dead flag** | 0 |
| WITH_CSNOBOL4 | 2 | off | sync_monitor.c:14 | **KEEP** (scrip-monitor target gate) | 0 |
| RS23_DIAG | 2 | never defined | whole rs23_diag.c #ifdef-wrapped, unreferenced by Makefile | **DELETE** (~87 ln; also AST-walks against the rule) | ~87 |
| BB_DEFINE_NAMES | 2 | on in 3 TUs | ast.h:144 + 3 definers | **KEEP** (name-table idiom) | 0 |
| AST_PRINT_TEST/AST_VERIFY_TEST | 2 | never defined | embedded test mains | **DELETE** | ~40 |
| RT_ARENA_ZERO/RT_ARENA_TITLE (=1) | 2 | on | rt_arena.c 4 sites | INVESTIGATE→collapse | ~10 |
| pl_area.h __linux__ · __cplusplus (54) · flex/bison yy*/YY_* (~150+, generated only) | — | — | — | **KEEP** | 0 |

## 2. ZETA COLLAPSE MAP
**The ruled winner (cell-stack ≡ forth ≡ ZC_FRAME_RSP) is ALREADY the compiled-in default everywhere** — no -D/ZCFLAGS/CLI override of any ZC value exists in Makefile or scripts/. Direct evidence the other arms are BROKEN, not just unused: test_gate_instr_budget.sh:48 documents --zeta-storage=cell-heap SIGSEGVs on roman and frame-rsp aborts beauty. The one selector-touching script (util_fc_spine_census.sh:15, SCRIP_ZETA_PORT=6) pins the default — a no-op.

Inventory of what dies: zeta_choices.h menu (21 ZC_* macros, 3 #error-dead arms) · zeta_alloc.c/.h runtime dispatch layer (~120 of 168 lines are mode machinery: rt_zeta_set_mode, rt_zeta_port_set_mode, rt_zeta_storage_set/get, rt_zc_frame_live, rt_zeta_cstack, rt_zeta_mode, g_zeta_mode/port/storage globals) · scrip.c 3 CLI flags (:818-820) + 8 bake-conditionals in 2 duplicated preamble sites (m3 ~1303-1310, m4 ~1487-1494) · x86_asm.h 9 wrapper inlines feeding ~90 call sites (x86_fb_pinned/x86_fb_data already hardcoded to 0 — the collapse pattern is a proven, half-executed playbook) · call sites in bb_call_proc_staged, bb_match_{end,begin,defer,fence1,arb}, bb_glue_flat, xa_flat, xa_file_header, emit.cpp (30+), lower_snobol4.c, by_name_dispatch.c, rt.c, gc_heap.c · 12 SCRIP_ZETA_* env twins. zeta_storage.c itself KEEPS (the live layout computer), audited after ZLS/ZH arms confirmed dead.

## 3. ENV-VAR CENSUS (351 vars by family)
EXPERIMENT-RESIDUE (winner decided, scripts never set): SCRIP_ARBNO_* (17) · SCRIP_DEFER_* (16, incl. SCRIP_DEFER_BETA_GUARD re-derived inline at 4+ sites) · SCRIP_CAP_* (14) · SCRIP_NO_* kill-switches (27, except NO_IX/NOHUGE/NOFC script-referenced) · SCRIP_ICN_*/SCRIP_PL_* (22) · fence/B1C/M3/M4 A/B (~20) · SCRIP_ZETA_* (12) · ~150 singleton session-named flags.
DIAGNOSTIC: SCRIP_ZD* (36 — fold under one master) · MONITOR* (~10, RULES.md-demoted but script-used).
LOAD-BEARING (scripts actually set): SCRIP_ZSM family (gate-used) · SCRIP_GC_STRESS/COVERAGE/UNROOT (test_gc_stress_suite.sh) · MONITOR_BIN/READY_PIPE · SCRIP_BETA_ELIDE_OFF, SCRIP_DWARF_LOC, SCRIP_KW_DIRECT, SCRIP_STMT_FRAME, SCRIP_TRACE.
Target state: ~292 never-set vars → delete toward one SCRIP_DEBUG-style master diag flag, per-family spot-verify first.

## 4. PLATFORM GATING
g_platform set at exactly emit.cpp:195,204 (always X86); 193 foldable sites/145 files; four dead enum values + macros have zero external call sites.

## 5. #if 0
Exactly ONE in all of src/: tools/tmatch_proto.c:27-86 (58/86 lines). Bonus: all of src/tools/ is unreferenced by the Makefile.

## 6. COLLAPSE ORDER (safe sequence)
1. **Zero-risk, grep-provable**: DYN_ENGINE_LINKED + IR_DEFINE_NAMES -D deletes · RS23_DIAG/AST_PRINT_TEST/AST_VERIFY_TEST · SCRIP_DEF_I2D_MAGIC #else arm · #error-blocked ZC arms (PROMOTE_ON, FRAME_DEAD5, STORAGE_FRAME_R12) · ZC_POISON #elif · tmatch_proto #if 0.
2. **Tautology-guard removals, byte-identical by construction**: the 2 rt.c ZC_FRAME #ifs (no #else, condition always true — delete guard lines, keep body verbatim); same class as the already-hardcoded x86_zr()/x86_fb_* precedent.
3. **PLATFORM_X86 sweep** (145 files, mechanically uniform: if(PLATFORM_X86)→keep body, if(!)→delete body) — scripted sweep + full blocking-gate re-proof after.
4. **ζ selector complex** — runtime-constant branches, NOT dead #ifs: collapse zeta_alloc.c mode fns to constants → x86_asm.h wrappers → ~90 call sites → CLI flags/env twins last (or hard-error stubs per the frame-r12 precedent). **Requires m3≡m4 byte-diff proof**: regen .s artifacts and diff a representative corpus slice before/after.
5. ZC_COLLECTION + ZC_COEXPR_STACK_GCHEAP + ZC_SELFLOAD — same byte-diff discipline, batched.
6. ZC_ZETA (zls/zls2/zh) + zeta_heap.c + rt_zls_* legacy half — INVESTIGATE first (grep inconclusive; needs --zeta=zls/zh smoke or runtime trace).
7. ZC_SPAN_GUTS/ZC_LIT_GUTS + the ~292 never-set env vars — dedicated follow-up, per-family confirmation before deletion.

Key files: contracts/zeta_choices.h · runtime/rt/zeta_alloc.c/.h · templates/x86_asm.h · driver/scrip.c:802-857,1303-1310,1487-1494 · emitter/emit.h:89-109 + emit.cpp:25,195,204.
