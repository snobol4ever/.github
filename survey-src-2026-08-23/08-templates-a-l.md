# Survey 08 — src/templates/bb_[a-l]*.cpp (65 files, 5793 LOC) + bb headers (agent report, condensed verbatim)

## 1. INVENTORY (by family)
| Family | Files | LOC | Verdict |
|---|---|---|---|
| call | bb_call{,_bool,_define,_fn,_proc_staged,_value,_write_slot} | 2199 | LIVE — largest family; bb_call() pure dispatcher on _.op_call_route |
| binop/arith | bb_arith, bb_binop_{arith,concat_slot,gvar_arith,gvar_arith_slot,relop,xrep_slot} | 852 | LIVE |
| define | bb_define(632), bb_enter_init, bb_initial | 678 | LIVE — bb_define.cpp = 3 boxes behind role-switch |
| keyword | bb_keyword_{assign,assign_snobol4,icon,snobol4} | 362 | LIVE — filenames carry language identity |
| coerce | bb_coerce_{integer,numeric,real,string} | 155 | LIVE, uniform |
| control/glue | bb_bound, bb_conjunction, bb_cut, bb_disjunction, bb_every, bb_fail, bb_goto, bb_goto_deferred, bb_glue_flat, bb_glue_framed, bb_indirect_goto | 323 | LIVE |
| field/idx/agg | bb_field_get, bb_idx_get, bb_idx_set, bb_iterate, bb_key_gen | 261 | LIVE |
| cmp/ident | bb_cmp_test, bb_differ, bb_ident | 181 | LIVE (differ/ident documented sibling pair s199) |
| grammar (Snocone) | bb_galt, bb_gcc, bb_gen_scan, bb_glit | 149 | LIVE — fixed r13/r14/r15 Sigma/delta/Delta |
| case/cell (Prolog) | bb_case_arm, bb_cell_cut, bb_cell_ite | 78 | LIVE |
| coexpr (Icon) | bb_activate, bb_create, bb_coret, bb_cofail | 107 | LIVE |
| assign | bb_assign_global, bb_assign_local, bb_assign_var | 189 | LIVE |
| indirect_assign | bb_indirect_assign_lit_s, bb_indirect_assign_var | 40 | LIVE near-duplicate pair |
| lit | bb_lit, bb_lit_scalar | 129 | LIVE |
| misc | bb_deref(38), bb_limit(35), bb_det_nl(17) | 90 | LIVE |

## 2. DEAD PARTS
- **"3 unbuilt files" premise FALSE — grep artifact** (pattern without digits missed bb_keyword_assign_snobol4/bb_keyword_snobol4, both in Makefile:147,169). Re-verified with [A-Za-z0-9_]: **all 65 in range, all 131 bb_*.cpp repo-wide, 1:1 matched in Makefile — zero unbuilt templates.**
- bb_binop_arith.cpp:57-58,69-84 — SCRIP_DEF_I2D_MAGIC #defined 0, permanently disabling NaN-boxing branch (functional #if 0).
- bb_glue_framed.cpp:15-19 — unreachable double-empty-concat after return (:17); same no-op pattern reachable at :10-11. Stripped-prefix residue.
- bb_call.cpp:114-116,149-151,234-236 — three x86_bomb() tripwires guarding retired marshal_single_call ("dead at NCB-1b, 0/592 sweep") — intentional.

## 3. VIOLATIONS
- MEDIUM_*: zero. Raw-byte producers: zero. LANG_/language branches: zero. Per-op filters: none (bb_call dispatches on lowering-assigned op_call_route; explicit ⛔ NO PER-OP FILTER comments). C Byrd-box (void*,int) shape: zero.
- Blank lines: only bb_assign_global.cpp:31,69 (whitespace-only, recent edit — mtime Aug-21 vs siblings Aug-20).
- **Globals: bb_glue_flat.cpp:18-19 `int g_glue_entered = 0; int g_glue_o_sup = 0;` — the ONLY file-scope mutable state in range outside g_emit, and carries NO grant citation** (other global-adjacent sites carry explicit ⛔ justification comments). Provenance check needed.

## 4. STRUCTURE
- Canonical skeleton: `bb_X(){ if(!PLATFORM_X86)…; return x86("comment") + x86_alpha() + body + x86_gamma() + x86_beta_trampoline(); }` — ~45/65 fit exactly, often with a _.op_zres ZK-2-cells arm duplicating shape against ZOPQ/ZRES vs FRQ.
- Deviants: bb_call/bb_call_fn/bb_call_proc_staged/bb_define — internal enum/role dispatch to several box bodies. bb_call_fn has ~12 sink_* fns (Prolog $unify/$trail fast paths, bare-integer label IDs 40-120) — a distinct micro-DSL.
- **bb_define.cpp is two files concatenated** (duplicate include preamble + extern-C block at 361-379); strongest split candidate (activate/bind vs sr).
- Reorg: subdirs by family (call/, binop/, coerce/, keyword/, coexpr/, grammar/, control/) work cleanly; call/ = 38% of range LOC.
- Headers: bb_templates.h = master prototype list (~160 signatures, the de facto contract). bb_template_common.h = shared macros (`_` = g_emit, GZ_CELL_OFF) + dormant JVM/NET/JS hook prototypes (permanently unused). **bb_common.h despite generic name is ~40 extern-C Prolog-runtime prototypes (rt_is, rt_functor, rt_univ…) — rename candidate bb_prolog_rt.h.**

## 5. DEPENDENCIES
- Beyond mandated: descr.h (36), SM.h+ast.h paired (7-8), runtime/builtins/gen.h (9), runtime/rt/rt_coexpr.h (4, Icon), builtin_ids.h/ab_abi.h/pin_va.h/rt.h (call/define family).
- Emitter-internals reach-in: bb_call_write_slot (xa_bb_emit_pair_* table), bb_indirect_goto/bb_call_proc_staged (zframe_graph), bb_call_fn/bb_lit_scalar (pl_cells_graph). **bb_define.cpp:308-360 bb_ab_emit_nodes() saves/swaps/restores the g_emit/g_emit_cfg/g_gva_active singleton and pokes fn pointers into bb_emit_buf — a mini emitter driver inside a template.**

## 6. NAMING
- bb_keyword_assign.cpp is the Icon one yet unmarked while siblings carry _snobol4/_icon suffixes — asymmetric.
- "ZK-2 cells" spelled 3 ways: _slot file suffix, zd/ZD labels, _.op_zres field.
- bb_key_gen.cpp:26 bare 99L vs bb_iterate.cpp:30 (long)DT_FAIL for identical comparison.
- bid_bake_on/of() redefined verbatim in bb_call.cpp + bb_call_fn.cpp; duplicated rt_proc_call_epilogue_γ/ω extern blocks across bb_call_proc_staged + bb_call_value → hoist to shared call-family header.
