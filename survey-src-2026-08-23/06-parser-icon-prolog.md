# Survey 06 — src/parser/icon + src/parser/prolog (agent report, condensed verbatim)

## 1. INVENTORY
**icon/ (11 files, 2728 LOC)**: icon_lex.c/.h 783/145 LIVE (hand lexer + $define/$include pp); icon_parse.c/.h 899/17 LIVE (recursive-descent → tree_t); icon_driver.c/.h 74/6 LIVE (icon_compile + -LINK); icon_runtime.c 67 LIVE but MISPLACED; icon_emit.h 21 **DEAD** (declares fns with zero implementations); icn_main.c 114 **DEAD** (old standalone scrip-cc CLI, self-describes emit paths "archived"); icon_lex_test.c 374 + icon_parse_test.c 228 **DEAD/STALE** (unbuilt; reference nonexistent icon_ast.h/IcnNode API); README.md STALE ("planned, not yet implemented" — Icon is live).

**prolog/ (27 files + 2 .bak, 4407 LOC)**: prolog_lex.c/.h 323/49 LIVE (.h declares 3 dead prototypes); prolog_parse.c/.h 1351/33 LIVE (duplicated parser, §4); prolog_atom.c/.h 141/8 MIXED (atom table + Term ctors that belong to term.h); prolog_unify.c 63 LIVE (used by rt_runtime.c interpreter path); prolog_driver.c/.h 16/6 LIVE; prolog_lower.c/.h 866/10 LIVE, misnamed (§3); prolog_builtin.c/.h 468/20 MIXED/MISPLACED (only term-printing; header promises 6 unimplemented fns); pl_area.h 52 + pl_cell.h 116 + pl_cell_conv.h 91 LIVE header-only runtime structures, MISPLACED; pl_resolve.h 12 **DEAD** (zero includers; shadow-dup of runtime/builtins/resolution.h); term.h 48 + prolog_runtime.h 20 LIVE (consumed by runtime/ + driver/ — backward dep); 8 test files (pl_cell_conv_test, pl_cell_test, pl_descr2_hot_test, prolog_lower_test, prolog_parse_test, prolog_unify_test, test_pl_area, test_pl_env_area) **DEAD/TEST-SCAFFOLD** (own main(), zero refs in scripts/ or Makefile — grep-verified); prolog_emit_jvm.c.bak (427KB) + prolog_lex.c.bak PARKED.

Build: Makefile:317-327 = icon_runtime, icon_parse, icon_lex, icon_driver; prolog_lex, prolog_parse, prolog_atom, prolog_builtin, prolog_unify, prolog_driver, prolog_lower. All other .c confirmed absent from build + scripts.

## 2. DEAD PARTS
- icon_lex.c:667-669 empty always-false conditional (had_error only ever 0/1).
- icon_lex.c:101-105 writes g_jcon (defined runtime/keywords.c) from magic `# SRC: JCON` comment — **g_jcon never read anywhere** — write-only global.
- icon_runtime.c:1-8 — icn_stack[256]/icn_sp, icn_retval, icn_failed, subscript_buf[2] never referenced (g_vstack-shaped residue, unused; delete). icn_str_arena/str_arena_pos live.
- icon_parse.c:899 icn_parse_file always returns NULL CODE_t*; all callers discard. Dead return channel. Also 3× unused `int line` (:201,282,543).
- icon_emit.h: icn_emit_file/expr, icn_label_α/β, IcnPorts — zero implementations; only includer is dead icn_main.c.
- icn_main.c: both do_jvm branches return unconditionally → lines 98-113 unreachable even within the dead file.
- prolog_lex.h declares lexer_expect, token_free, tk_name — none defined/called.
- prolog_builtin.c:468 — 5 static _aid_* atom-cache vars referenced nowhere (abandoned).
- prolog_builtin.h declares pl_functor/pl_arg/pl_univ/pl_is/pl_is_float/pl_term_to_string — zero implementations in live tree.
- pl_resolve.h whole file.

## 3. MISPLACED
- **icon_runtime.c → runtime/builtins/**: cset_union/diff/inter/canonical declared in runtime/builtins/gen_runtime.h, called from runtime/arithmetic.c + keywords.c. Sits in parser/icon only for test-harness convenience.
- **pl_area.h, pl_cell.h, pl_cell_conv.h → runtime/core/ or contracts/**: pure DESCR_t runtime cell/allocator machinery consumed by rt_runtime.c, unification.c, resolution.c, by_name_dispatch.c — generic runtime depends on parser-dir headers.
- **prolog_builtin.c misnamed+misplaced**: actually Prolog term pretty-printing (pl_write/writeq/write_canonical/write_term_opts), called from runtime via raw local externs → rename/move e.g. runtime/builtins/prolog_term_io.c.
- **prolog_atom.c mixes**: atom table (matches header) + term_new_* ctors (belong with term.h).
- **prolog_lower.c: rename, don't move** (e.g. prolog_ast_build.c): it is PlProgram→tree_t AST finishing (TT_CHOICE grouping, if/then/else desugar, bagof/setof expansion, DCG/plunit/dynamic bookkeeping) — a different stage from src/lower/lower_prolog.c (tree_t→IR). The two call each other's private symbols by raw extern (parser/prolog/prolog_lower.c:500-501 externs pl_dyn_mark/pl_dyn_is_marked defined in lower/lower_prolog.c:890,897) — needs a shared header.

## 4. SPLIT/MERGE
- **prolog_parse.c contains two complete parallel operator-precedence parsers** (parse_primary/parse_term Term*-based ~250 lines; pt_primary/pt_term tree_t-based ~250 lines) with identical precedence tables. On DCG clause (`-->`), parse_clause (line 1117) REWINDS the lexer and re-parses the entire clause with the other parser — every DCG clause parsed twice. Split exists because DCG expansion (dcg_expand_body, 811-964) written against Term* while mainline migrated to tree_t.
- prolog_parse.c 1351 LOC also carries: op-table, both parsers, DCG translation, :- if/elif conditional compilation, embedded ~45-clause PL_PRELUDE_SRC (1158-1202) with reachability DCE. Split: op-table / DCG / prelude.
- prolog_builtin.c: four copies of the same 30-entry ops[] precedence table across its print variants.

## 5. VIOLATIONS
- No C Byrd-boxes, no g_vstack/rt_push in Icon, no #if 0, zero blank lines — compliant.
- 200-char: icon_lex.c:151,195,599,615 (up to 309); prolog_builtin.c:412; pl_cell.h:95 (293).
- Extern-instead-of-header pattern: runtime/unification.c:97-139, by_name_dispatch.c:4939, prolog_lower.c:500-501 (pl_write_term_opts not even in the header). icon_lex.c:100-105 bare `extern int g_jcon;` in function body instead of including keywords.h.

## 6. DEPENDENCIES
- **Cruft includes, safe to delete**: icon_lex.h included by driver_private.h:21, scrip.c:28, tree_to_sno.c:3, lower_snobol4.c:8, snocone_parse.tab.c:243 — zero symbols used in ALL FIVE (grep of every icon_lex.h symbol). (Note: lower agent found TK_AUG* used in lower_snobol4.c/tree_to_sno.c — reconcile: the TK_AUG* constants ARE from icon_lex.h; verification needed on those two.)
- **Backward dep runtime→parser**: pl_cell.h/pl_cell_conv.h ← rt_runtime.c, unification.c, resolution.c, by_name_dispatch.c; term.h/prolog_atom.h/prolog_runtime.h/prolog_builtin.h ← driver_private.h, scrip.c, polyglot.c, sync_monitor.c, most of runtime/. The "parser" dir is where Prolog's core runtime types live.
- pl_resolve.h duplicates resolution.h declarations — delete.
- icon_driver.h/prolog_driver.h: the two legitimate cross-boundary contracts.

## 7. NAMING
- Icon: files icon_*, symbols icn_*/Icn* — normalize or document.
- Prolog: three naming families = three data models: `pl_` (compiled DESCR-cell path), `prolog_` (parser/AST Term* path), bare Term/Trail/unify (tree-walking interpreter structs). Mirrors the real architectural split — should become two clearly-labeled families (pl_ vs plw_/plterm_) or two directories.

## sm_interp_run exception map
Term*/Trail apparatus (term.h, prolog_unify.c unify(), term ctors in prolog_atom.c, dead pl_resolve.h) = the machinery behind the granted sm_interp_run exception; exercised by rt_runtime.c:415-456 (findall/bagof), sync_monitor.c, polyglot.c via g_resolve_trail. Coexists with the DESCR/pl_cell_t compiled path (pl_cell.h ← unification.c rt_unify_terms). Retiring sm_interp_run retires the whole Term*/Trail family as a unit — no other live consumer.
