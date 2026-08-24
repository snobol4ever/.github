# Survey 10 — src/runtime top level (21 files, 13,931 lines) (agent report, condensed verbatim)

## 1. INVENTORY
| File | LOC | Purpose | Verdict |
|---|---|---|---|
| by_name_dispatch.c/.h | 7164/10 | Builtin-name dispatch for EVERY frontend: SNOBOL4/Icon builtins, Prolog plw_* glue, Pascal heap sim (pas_*), Raku junctions/multi-method + full TAP harness, grammar-parse glue | LIVE, badly MIXED |
| unification.c | 1716 | Prolog runtime: unify, ISO type/compare/throw, findall/bagof/setof, assert/retract, flags, streams, format/2 | LIVE, one dead scaffold |
| pattern_match.c | 1578 | pat_* builder API, DTP compile-on-demand cache, deferred-capture engine (asm-twinned rtx_match.S), lvalue/subscript/assign/deref | LIVE, MIXED |
| aggregates.c | 469 | array + TABLE hash engine (s262 typed-hash rewrite) | LIVE, MISPLACED → rt/ |
| rt_runtime.c | 553 | BB codegen glue: Prolog resolution caches, generator-suspend buffers keyed by IR_t*, IR-node term compare, scan-literal fast path | LIVE, MISPLACED |
| runtime_eval.c | 481 | EVAL/CODE(): parses+lowers+emits fragment AT RUN TIME | LIVE, MISPLACED (compiler-driver logic) |
| arithmetic.c | 312 | arith + operator-overload dispatch | LIVE |
| builtin_ids.h | 324 | perfect-hash BID_* table, shared contract with templates/bb_call*.cpp | LIVE |
| keywords.c/.h | 434/28 | &KEYWORD for SNOBOL4 (rt_keyword_read_snobol4) and Icon (kw_read) — split by entry point, not branch | LIVE |
| runtime_init.c | 178 | ZDP/ZSM frame-discipline diagnostics | LIVE (diag) |
| name_binding.c | 113 | is_global/global_register + scope_*/static_* | LIVE, **MISPLACED — compile-time code** |
| string_ops.c/.h | 158/13 | concat/repeat/real-format | LIVE |
| string_builtins.c | 143 | DUPL/REPLACE/SUBSTR/TRIM/… | LIVE |
| invocation.c | 81 | sm_call_proc/proc_table_call SM-era indirect call | LIVE-BUT-SUSPECT |
| io_format.c | 70 | output/write | LIVE |
| values.c | 33 | descr_identical | LIVE |
| snobol4_system_fns.h | 14 | SNOBOL4 system-fn name list (OPSYN guard) | LIVE |
| rt_gram_trampoline.S | 66 | BB entry trampoline (RK-GRAM-3b) | LIVE, MISPLACED → rtx/ |

No runtime.h umbrella — core/core.h fills that role.

## 2. LAYERING (inferred + confirmed)
core/ = descriptor/value kernel · rt/ = slab/arena/GC/zeta/coexpr · rtx/ = .S fast paths · top = language-semantics builtins + pattern engine. Misplacements:
- **aggregates.c → rt/** (general storage engine, HB_AGGB GC tagging, rtx_table.S twin; callers uniform across languages).
- **name_binding.c is_global/global_register → contracts/ or lower/**: compile-time utilities. global_register called only from lower/*; is_global consulted by lower_icon, zeta_storage.c (heaviest), emit.cpp (12+ sites), bb_call.cpp, scrip.c. Nothing queried by a running program. Starkest wrong-layer file.
- **rt_runtime.c = BB/codegen resolution glue**, includes emitter/emit.h + lower/lower.h (lower.h TWICE — :2/:33 redundant); needs IR_t to exist. Rename+reclassify.
- **runtime_eval.c drives the compiler at run time** (lower_snobol4, emit_chain, emit_jmp_entry_for_chain) — legit for m3, but it's driver logic.
- rt_gram_trampoline.S → rtx/ (speaks rtx_abi.inc wire protocol).
- pattern_match.c lvalue machinery (rt_subscript_var/rt_deref_slow/c_rt_assign_var/rt_swap_var) mixed in with capture engine — defensible, note for reorg.
- **builtins/ is a peer with a back-edge**: gen_runtime.c includes by_name_dispatch.h and calls back up; two-way coupling.

## 3. DEAD PARTS
- unification.c:214-225 meta_fr/meta_root/g_meta_builtins/meta_solve+meta_redo (fwd-declared, NEVER DEFINED)/g_meta_compat — abandoned meta-interpreter scaffold, zero refs.
- unification.c:208-210 pl_pred_row_t/g_pl_pred_table/g_pl_pred_n — never used.
- unification.c:24-32 rt_unify_const/rt_unify_var_var — ignore args, return 0, zero callers.
- **runtime_eval.c:295-300 eval_node + pattern_match.c:572-576 eval_ast_pat: bomb stubs WITH LIVE CALLERS** (driver_call.c:204; eval_expr DT_E arm) — landmines, not settled residue.
- **rt_runtime.c:531-534 ir_call_proc prints [NO-IR-INTERP] and returns FAILDESCR — reachable from 6 by_name_dispatch.c sites (Raku multi-method, call-by-index). Silently no-ops — worse for detection.**
- invocation.c sm_call_proc → sm_eval_subexpr (weak stub in rt/rt.c erroring "retired"); sm_call_proc zero direct callers; reached only via proc_table_call (driver_hooks.c, by_name_dispatch.c:691). If no strong override exists, invocation.c + scope_patch/static_* half of name_binding.c are dead SM residue together. NEEDS VERIFICATION.
- keywords.c:22 g_jcon — set by icon_lex.c, never read. Write-only.

## 4. SPLIT/MERGE
- **by_name_dispatch.c is the dominant structural problem**: two god-functions — script_try_call_builtin_by_name (1672-4027, 2355 lines) and try_call_builtin_by_name_bl (5271-7122, 1851 lines) — linear strcmp/switch chains (latter with dtax_ent_t inline cache). Split by frontend: dispatch_snobol4/icon/prolog/pascal/raku/grammar.c.
- **Duplicate ISO term-compare**: unification.c rt_pl_term_compare/class vs rt_runtime.c resolve_term_compare/class — near-identical, unaware of each other.
- invocation.c (81) merge into rt_runtime.c if it survives §3.

## 5. VIOLATIONS
- **AST walking: name_binding.c:93-111 scope_patch walks e->t, e->c[i], e->v.sval** — the forbidden pattern; reachable only via the suspect sm_call_proc path.
- Backward deps: rt_runtime.c → emit.h + lower.h; by_name_dispatch.c:19 → driver/driver_private.h.
- Style: by_name_dispatch.c:1508 the area's ONE stray blank line. 200-char: by_name_dispatch 127, pattern_match 51, aggregates 28, runtime_init 18, unification 12.
- C Byrd-box fns: zero. LANG_/language-string branches: zero (split by entry point — compliant).
- by_name_dispatch.c carries ~20 file-scope mutable globals (plw_* state, pascal heap, 7 TAP globals, perf counters) — audit pass warranted.

## 6. DEPENDENCIES
- builtin_ids.h = three-way contract (by_name_dispatch decode ↔ bb_call/bb_call_fn encode) — must move together.
- snobol4_system_fns.h shared with lower_snobol4.c + core.c.
- keywords.h/pattern_match.h/string_ops.h runtime-internal.

## 7. NAMING
- **rt_runtime.c vs rt/rt.c is a real collision**: unrelated architecturally. Rename rt_runtime.c → bb_resolve.c / codegen_rt_glue.c.
- rt_ prefix no longer signals "callable from running program" (rt_type_test_term is compile-time-only).
- script_try_call_builtin_by_name / try_call_builtin_by_name / _bl — three near-synonyms, two true aliases.
