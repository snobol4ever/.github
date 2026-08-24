# Survey 05 — src/emitter + src/optimizer (agent report, condensed verbatim)

## 1. INVENTORY
| Path | LOC | Purpose | Verdict |
|---|---|---|---|
| emitter/emit.cpp | 3482 | BB-graph linearizer + IR→x86 driver + box dispatch + text/binary primitives + strtab/csettab + label/patch | MIXED (live core + ~150 lines retired-backend residue + 6 dead abort-stubs) |
| emitter/emit.h | 803 | Umbrella: 6 concatenated extern-C blocks (bb_emit core, `sm_emit_t g_emit` mega-struct 369-616, bb driver, SM/text, EmitStr) | LIVE, unmerged concatenation of ≥6 former headers |
| emitter/emit_str.cpp | 247 | std::string text builders: generic (emit_fmt, u8/u32le/u64le/bytes, gas_escape_str) + JVM/.NET/JS/WASM builders | MIXED — generic half LIVE (private to x86_asm.h), JVM/NET half 100% DEAD |
| emitter/sil_macros.h | 83 | Legacy SIL descriptor macros (MOVD, GETDC, IS_INT…) | LIVE but MISPLACED — zero use inside emitter/; 12 consumers all in driver/ + runtime/ |
| optimizer/optimizer.c/.h | 36+6 | optimizer_run fixpoint driver | LIVE |
| optimizer/branch_chain.c/h | 64+9 | bc_run — collapse GOTO/SUCCEED chains | LIVE |
| optimizer/const_fold.c/h | 46+6 | cf_run | LIVE |
| optimizer/copy_prop.c/h | 48+6 | cp_run | LIVE |
| optimizer/dead_goto.c/h | 26+6 | dg_run | LIVE |
| optimizer/dead_pure.c/h | 22+6 | dp_run | LIVE |
| optimizer/pat_fold.c/h | 33+6 | pf_run | **DEAD STUB** — pf_run is `(void)g; return 0;`; 3 static helpers unreachable |
| optimizer/gva_collect.c/h | 40+10 | GVA admission table | LIVE |
| optimizer/proc_collect.c/h | 61+12 | direct-call proc slots + scc_taint_graph | LIVE |
| optimizer/ir_query.c/h | 39+5 | IR predicates | LIVE |
| optimizer/ir_index.h | 75 | O(1) ptr→index map (replaced O(N²) scans) | LIVE, well-documented |
| optimizer/region_report.c | 29 | SCRIP_REGION_REPORT diagnostic | LIVE (diag-only) |
| optimizer/arith_fold.c/h | 133+10 | Prolog-flavored gz_arith_* folders | **FULLY DEAD** — unbuilt AND references IR_ARITH/IR_ATOM/IR_LOGICVAR which don't exist in IR.h — would not compile |

## 2. DEAD PARTS
- arith_fold.c: unbuilt + uncompilable; its .h included once at emit.cpp:489, none of its 5 fns called. Delete pair + include.
- emit_str.cpp:77-244 — all 7 jvm_*_str + 11 net_*_str: zero callers. emit.h:774-790 declares them for nothing. `g_platform` hard-set BB_PLATFORM_X86 (emit.cpp:195,204), never other value → PLATFORM_JVM/NET/JS/WASM permanently false.
- **bomb_text/bomb_bytes (emit_str.cpp:31-52, decl emit.h:767-768): zero callers.** CLAUDE.md's named "sole legacy exception" is itself dead — superseded by x86_bomb() (x86_asm.h:2121).
- js_escape_string_str (emit_str.cpp:157) + wasm_emit_data_segments_str (emit.cpp:304): single callers gated behind permanently-false PLATFORM_JS/WASM.
- Six abort()-stubs in emit.cpp ("GROUND ZERO … Icon-only reset"): bb_emit_limit_init(293), child_cache_get_lbl(588), gz_emit_catch(654), resolve_choice_clause_label(657), bb_kind_is_driver_owned(660), walk_bb_flat(958). First four zero callers; last two called only from unbuilt src/tools/emit_per_kind_audit.c.
- `struct tree_t;` fwd-decl emit.h:166 — never dereferenced; area clean of forbidden AST-walking.

## 3. MISPLACED
- sil_macros.h → src/runtime/core/ (no -I change needed).
- arith_fold → delete (or rewrite against real IR ops if is/2 folding wanted).
- JVM/.NET/JS/WASM string builders + g_wasm_* tables (emit.cpp:290-332) → delete, matching the recorded WASM-removal precedent.

## 4. SPLIT/MERGE
- emit.cpp: 3 fns = 48% of file (emit_drive 1441-2046=605ln; codegen_flat_chain_body 2612-3191=579ln; walk_bb_node_inner 1001-1293=292ln). Pipeline: codegen_flat_chain_body (RPO linearize) → emit_drive (switch(op) populating g_emit slots) → walk_bb_node_inner (second switch(op), universal fields, dispatch to bb_*()). Proposed split: emit_chain.c (~900), emit_drive.c (~750), emit_walk.c (~900 incl. frame/zdepth heuristics), emit_core.cpp (~500: labels/patches/init/text/strtab — merge emit_str.cpp survivors in). emit.h split along same 4 seams; the 247-line sm_emit_t struct is a flat bag (op_*/flat_*/xa_*/bb_*/zop_* families) worth sub-structuring later (riskier).
- Optimizer: 24 tiny files — DO NOT consolidate (each pass independently-testable, idiomatic .c/.h pairing; ir_index.h correctly factored). Exception: pat_fold implement-or-delete.

## 5. VIOLATIONS
- 10 MEDIUM_* occurrences in emit.cpp (26,129,155,195,204,247,978,1060,1425,3445) — infrastructure beneath x86(...), not letter-violations; but bb_emit_patch_rel32/abs64/byte abort() in TEXT mode — naming pass suggested (e.g. bb_emit_byte_binary).
- Raw-byte: bb_emit_byte/u32/u64/i32 (emit.cpp:166-184) are the primitive layer x86_asm.h delegates to — infrastructure, not bypass.
- **200-char: emit.cpp 211 lines over (some >2000 chars, e.g. ARBNO-K16 block ~1145-1149)** — largest style violation in area. emit.h 1. Optimizer clean.
- Blank lines: 0 everywhere. No LANG_*/AST-walk: clean.

## 6. DEPENDENCIES
- emit.h widest header in pipeline (bb_pool.h, IR.h, XA.h, core.h, bb_box.h funnel through it) — splitting it riskier than splitting bodies.
- emit.cpp → optimizer headers (gva/proc_collect lookups live inside emit_drive) — legitimate intentional backward dep.
- emit_str.cpp generic helpers consumed solely by x86_asm.h; one stray external caller in templates/xa_flat.cpp (see survey 07).

## 7. NAMING
- Prefix soup in g_emit: op_*/flat_*/xa_*/bb_*/zop_*/zd_* overlap (both op_zdepth and zd_stage track z-depth).
- Five verbs (walk/codegen/drive/emit/chain) for one pipeline — rename to emit_chain_*/emit_walk_*/emit_drive_* post-split.
- Optimizer pass naming consistent and good.
