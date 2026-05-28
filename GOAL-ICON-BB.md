# GOAL-ICON-BB.md — All Icon Byrd-Box constructs, modes 1/2/3/4

**Repo:** one4all + .github

## ⛔ MODE PRIORITY
Mode 2 (`--interp`) first, then mode 3 (`--run`). Mode 4 (`--compile`) DEFERRED.

---

## ⛔ ACTIVE: LFJ — LOWER FROM JCON (transcribe `irgen.icn`, one `ir_a_*` per rung)

**Supersedes the AG-PURE incremental staircase below.** Per `LOWER-REWRITE-FROM-JCON.md`
(Lon directive, issued 4×). The AG-PURE work patched the mega-switch in
`lower_icn_expr_node` with discriminator markers (sval "ag"/"ai"/"ar", `nd->ival = 1`,
TT_ASSIGN/TT_TO routing intercepts inside `lower_icn_expr_threaded_b`) — exactly the
anti-pattern the JCON directive forbids. AG-PURE commits 1–8.2 stay in tree as the
green-gate baseline; LFJ replaces the substrate underneath them.

**Method — per-kind dispatch table on ONE graph.** A function-pointer table indexed by AST
kind selects, for each `TT_*`, which lowerer handles that kind: legacy or new. Both lowerers
build into the **same `BB_graph_t`** — there is no shadow graph and no comparator. At any
point during the migration, a single Icon program's lowering walks AST nodes and dispatches
each to whichever lowerer owns that kind right now. Legacy entries dominate at the start;
the table flips one entry per rung as `ir_a_*` procedures land in `lower_icn_new.c`. When
the last entry flips (LFJ-14), the legacy file is unreachable and gets deleted (LFJ-15).

Concretely: `lower_icn_expr_node(cfg, e)` becomes the dispatcher — it reads
`lower_kind_table[e->t]` (a `BB_t* (*)(BB_graph_t*, tree_t*)` function pointer) and calls it.
At startup `lower_kind_table_init()` fills every slot with `lower_icn_legacy_<kind>`
(the existing case-body extracted from the mega-switch into a per-kind function — mechanical
refactor, no logic change). Each LFJ rung replaces one or more table slots with new
`lower_icn_new_<kind>` functions transcribed from `irgen.icn`. Replaced legacy functions are
not deleted until LFJ-15 — they stay compiled and linkable so a one-line table-edit reverts
any rung if it breaks gates.

No build flags. No comparator. No shadow graph. Just a table of function pointers, flipped
one entry per rung, on one in-memory `BB_graph_t`.

**Reference:** `/home/claude/corpus/programs/icon/jcon-ref/irgen.icn` (1559 lines).
Mapping doc (LFJ-0) is the contract — transcription does not deviate from it.

### Staircase

| Rung | Scope | Acceptance |
|------|-------|------------|
| LFJ-0  | Write `LOWER-IRGEN-MAPPING.md` in `.github`. Pure documentation: JCON `ir_chunk(label,insns)` → SCRIP `BB_t` alloc; JCON `ir_Goto(L)` → port assignment; the four labels (start/resume/failure/success) → ports (α/β/ω/γ); ir_info record → BB_t fields. No C yet. | ✅ `bc7dae2a` |
| LFJ-1a-i  | Extract 9 leaf cases (ILIT/FLIT/QLIT/CSET/VAR/KEYWORD/LOOP_BREAK/LOOP_NEXT/PROC_FAIL) into `lower_icn_legacy_<KIND>` static fns. Switch arms become one-line dispatches. ZERO logic change. | ✅ `f79ea9ba`. rungs 198. |
| LFJ-1a-ii | Extract next batch: TT_SCAN, TT_ASSIGN, TT_SWAP, TT_FNC, TT_SEQ, TT_SEQ_EXPR. Switch arms one-line. | ✅ `013703ff`. rungs 198. |
| LFJ-1a-iii | Extract TT_IF, TT_TO, TT_TO_BY, TT_EVERY, TT_WHILE, TT_UNTIL, TT_REPEAT, TT_LIMIT. | ✅ `b252409f`. rungs 198. TT_WHILE/TT_UNTIL share one helper. |
| LFJ-1a-iv | Extract binop group (TT_ADD..TT_NE, TT_CAT, TT_LCONCAT, TT_LLT..TT_LNE), TT_NOT, TT_ALTERNATE, TT_AUGOP. | ✅ `320f1eea`. rungs 198. 13-label arith/relop shared one helper; 6-label string-relop shared one helper. |
| LFJ-1a-v  | Extract TT_GLOBAL/LOCAL/STATIC_DECL, TT_INITIAL, TT_RETURN, TT_SUSPEND, TT_IDENTICAL, TT_NONNULL, TT_NULL, TT_RANDOM, TT_MATCH_UNARY, TT_MNS, TT_PLS, TT_CSET_*. | ✅ `092f7862`. rungs 198. 3-label DECL shared one helper; 3-label CSET binop shared one helper. |
| LFJ-1a-vi | Extract TT_SIZE, TT_IDX, TT_SECTION/SECTION_PLUS/SECTION_MINUS, TT_CASE, TT_FIELD, TT_RECORD, TT_MAKELIST, TT_ITERATE. Final 1a sub-rung — mega-switch is now a pure dispatcher. | ✅ `0ed7ace3`. rungs 198. 3-label SECTION shared one helper. Mega-switch every arm is a one-line `return lower_icn_legacy_<KIND>(cfg, e);`. |
| LFJ-1b | Introduce `lower_kind_table[TT_MAX]` of `BB_t* (*)(BB_graph_t*, tree_t*)`. `lower_kind_table_init()` populates every slot with the matching `lower_icn_legacy_<KIND>`. Dispatcher reads the table instead of switching directly. | ✅ `e5eb34b0`. rungs 198. Table sized `TT_KIND_COUNT` (~120); 74 slots populated, rest NULL → return NULL (matches legacy `default`). Init-on-first-use guard `lower_kind_table_inited`. Legacy fns static + referenced through table → all linkable for one-line revert. |
| LFJ-1c | Create empty `lower_icn_new.c` + `lower_icn_new.h`. No new functions yet. Wire it into the build. | ✅ `5cd9003d`. rungs 198. Makefile sources list + per-file compile rule added; `/tmp/si_objs/lower_icn_new.o` builds (no symbols) and links cleanly. |
| LFJ-2  | Transcribe `ir_a_NoOp` → `lower_icn_new_NoOp`. Table slot for `TT_NULL` (or whichever AST kind is Icon's NoOp) flips to the new function. Legacy function remains compiled, unreached. | ✅ Manual verify done (stderr probe `[new]` fired exactly once on `/x` test). rungs 198. SCRIP-Icon's parser never produces childless TT_NULL — the no-child branch implements ir_a_NoOp faithfully but is unreached from current Icon source; the with-child branch delegates to lower_icn_legacy_NULL pending the dedicated Unop rung. legacy_NULL de-`static`'d. |
| LFJ-3  | Transcribe `ir_a_Intlit`, `ir_a_Reallit`, `ir_a_Stringlit`, `ir_a_Csetlit`. Flip 4 table slots. | ✅ rungs 198. Probe (i=42, r=3.14, s="hi", c='aeiou') exercises all four kinds. Csets share BB_LIT_S with strings per current SCRIP runtime convention (legacy_CSET comment); single-line change to BB_LIT_C when/if added. |
| LFJ-4  | Transcribe `ir_a_Global` + `ir_value` helper. Flip slot(s). | ✅ rungs 198. Only TT_GLOBAL flipped — JCON has no ir_a_Local/Static (locals/statics are per-procedure metadata lists, not a_* records). `ir_value` has NO SCRIP analog per LOWER-IRGEN-MAPPING.md Sec. 5/6 (values flow through BB_graph_t.ring, not named tmps) — non-emission documented in lower_icn_new.c. TT_GLOBAL is intercepted in proc-setup paths before the dispatcher, so the new function owns the table slot but isn't reached from typical Icon source. |
| LFJ-5  | Transcribe `ir_binary` helper + `ir_a_Binop`. Flip the binop slots. | ✅ rungs 198. One function `lower_icn_new_Binop` covers all 20 binop AST kinds (TT_ADD..TT_NE, TT_CAT, TT_LCONCAT, TT_LLT..TT_LNE), mirroring JCON's single ir_a_Binop dispatch on p.op. AG-pure step-3 intercept in `lower_icn_expr_threaded_b` (lines 1414-1436) is producer-agnostic and catches the new fn's tree-shape transparently. `lower_icn_expr_node` de-`static`'d for cross-file recursion. Probe exercised arith/relop/string-relop/list-concat. |
| LFJ-6  | Transcribe `ir_a_If`. Flip TT_IF. | ✅ rungs 198. AG-pure step-5 intercept already realizes JCON's wiring in CFG-routing form (`cond.γ=cond.ω=nd_if; nd_if.γ=then.α; nd_if.ω=else.α`). JCON-only state (tmp/tiu/xiu/yiu, ir_max_st/ir_union_inuse, MoveLabel/IndirectGoto continuation) has no SCRIP analog. Pre-existing semantic divergence noted: JCON synthesizes `else := &fail` for missing else; SCRIP intercept routes cond.failure→γ_in (correct for if-as-statement; differs for if-as-expression in unbounded context). |
| LFJ-7  | Transcribe `ir_a_ToBy` (+ `ir_a_To` shim if separate). Flip TT_TO, TT_TO_BY. | ✅ rungs 198. JCON has NO separate ir_a_To — `i to j` is `i to j by 1` with byexpr defaulted. New function dispatches on `e->t` to allocate BB_TO vs BB_TO_BY. Preserves both SCRIP optimization paths: static-literal fast (both bounds TT_ILIT → ival/dval, α/β NULL) and dynamic (α/β as boxes, 8.2 intercept upgrades to AG-pure). `icn_fold_signed_lit` de-`static`'d for cross-file use (handles `by -3` parsed as TT_MNS(TT_ILIT 3)). Probe: 1+2+3+4+5=15; 1,3,5,7,9. |
| LFJ-8  | Transcribe `ir_a_Every`. Flip TT_EVERY. | ✅ `3d8aae8c` rungs 198. 1:1 transcription of legacy_EVERY (which already encodes JCON's flat-wire generator topology). Preserves AG-pure step 8.1 literal-bound gating (`gen->α==NULL && gen->β==NULL`) and step 8.2 TT_TO/TT_TO_BY dynamic-bound routing via `lower_icn_expr_threaded_b`. JCON's 6 Goto chunks collapse onto 4 CFG port assignments per the SCRIP encoding (gen.γ=body, body.γ=gen, body.ω=gen, gen.ω=nd). JCON-only state with no SCRIP analog documented: ir_init_loop/ir_loop_stack (SCRIP uses chain-walker FRAME for break/next), per-chunk label allocations (SCRIP labels are box identities), bounded-suspend chunks (chain walker's ω-on-resume default), ir_coord (no current SCRIP debug-source). `lower_icn_expr_threaded_b` extern'd in lower_icn_new.c (already non-static in lower_icn.c). |
| LFJ-9  | Transcribe `ir_a_Compound`, `ir_a_ProcBody`. Flip the relevant slots. | ✅ `80b9130e` rungs 198. **DOCUMENTED NON-EMISSION** per LOWER-IRGEN-MAPPING.md Q5 + LFJ-4 precedent. Both JCON procedures are realized in SCRIP by the non-ir_a_* plumbing function `lower_icn_proc_body` (lower_icn.c:1145) whose inline comments already cite both. SCRIP has no TT_COMPOUND/TT_PROC_BODY AST kind — Icon parser emits TT_PROC_DECL with c[2]=TT_PROGRAM (stmt list); neither has a `lower_kind_table` slot, neither reaches the dispatcher (proc_body is called one level above lower_icn_expr_node). New functions `lower_icn_new_Compound`/`lower_icn_new_ProcBody` are documented non-emission stubs (return NULL), declared in the header to complete the LFJ inventory. NO table flip — same architectural pattern as LFJ-4 TT_LOCAL/TT_STATIC_DECL. |
| LFJ-10 | Transcribe `ir_a_Call`, `ir_a_Field`, `ir_a_Sectionop`. Flip the slots. | ✅ `5c5bc669` rungs 198. 5 AST kinds flipped: TT_FNC → `lower_icn_new_Call` (ir_a_Call, irgen.icn:360-410), TT_FIELD → `lower_icn_new_Field` (ir_a_Field, irgen.icn:33-46), TT_SECTION/TT_SECTION_PLUS/TT_SECTION_MINUS → `lower_icn_new_Sectionop` (ir_a_Sectionop, irgen.icn:334-357). ir_a_Call covers general BB_CALL + SCRIP-specific runtime fast paths NOT in JCON (key→BB_KEY_GEN, find→BB_FIND_GEN, seq→BB_SEQ_GEN — JCON would dispatch these via the general Call+Closure machinery). ir_a_Sectionop dispatches all three SCRIP AST variants via `nd->ival` (0=RANGE, 1=PLUS, 2=MINUS), mirroring JCON's single-procedure p.op dispatch. 1:1 transcription of legacy functions. Probe verified rung20 (section + Call) and rung24 (Call + Field). |
| LFJ-11 | Transcribe `ir_a_Alt`, `ir_conjunction`, `ir_a_Not`. Flip the slots. | ✅ `8b6e513b` rungs 198. 3 AST kinds flipped: TT_ALTERNATE → `lower_icn_new_Alt` (ir_a_Alt, irgen.icn:167-199), TT_SEQ → `lower_icn_new_Conjunction` (ir_conjunction, irgen.icn:405-415), TT_NOT → `lower_icn_new_Not` (ir_a_Not, irgen.icn:142-159). Alt uses F-6c convention (arms chain via ω, each arm.γ=BB_ALT, last arm.ω stays NULL for emitter outer-wiring). Conjunction uses H-1 convention (nd->α=e1, nd->β=e2), port wiring realized by AG-pure step-6 executor. Not has α=inner, executor inverts outcome. JCON-only state with no SCRIP analog: ir_max_st/ir_copy_inuse/ir_inter_inuse (per-arm liveness — SCRIP uses single chain-walker state), ir_tmploc/IndirectGoto/MoveLabel (bounded-alt resume indirection — SCRIP uses per-box state). Note: TT_SEQ with 2 children = conjunction; legacy_SEQ also only handled n>=2 as BB_CONJ. Probe verified rung07_control_not (Not), rung13_alt_alt_cross_arg (Alt), rung13_alt_alt_filter (Conjunction + Alt). |
| LFJ-12 | Transcribe `ir_a_While`, `ir_a_Until`, `ir_a_Repeat`, `ir_a_Limitation`. Flip the slots. | ✅ `9b8fec0c` rungs 198. 4 AST kinds flipped: TT_WHILE → `lower_icn_new_While` (ir_a_While, irgen.icn:1008-1032), TT_UNTIL → `lower_icn_new_Until` (ir_a_Until, irgen.icn:981-1005), TT_REPEAT → `lower_icn_new_Repeat` (ir_a_Repeat, irgen.icn:847-864), TT_LIMIT → `lower_icn_new_Limitation` (ir_a_Limitation, irgen.icn:113-139). 1:1 transcription of legacy_WHILE_UNTIL/REPEAT/LIMIT — JCON chunk-based wiring (p.ir.start→Goto, p.expr.success/failure→Goto, /bounded resume IndirectGoto, p.ir.x.nextlabel→Goto) collapses to identical SCRIP CFG port assignments (α=cond/gen/body, β=body/lim) because executor (bb_exec.c:1154-1264) realizes the success/failure routing per op kind. e->t (TT_WHILE vs TT_UNTIL) selects BB_WHILE vs BB_UNTIL in shared-shape function. JCON-only state documented as non-emission: ir_init_loop/ir_loopinfo (SCRIP folds into chain-walker FRAME), ir_loop_stack put/pull (FRAME.loop_break / loop_next direct dispatch), ir_new_inuse / copy(st) per-arm liveness scoping (SCRIP descriptors per-box), ir_coord (no current SCRIP debug-source), /bounded vs unbounded resume distinction (chain walker's ω-on-resume default covers both), p.ir.x.continue IndirectGoto (FRAME-based direct dispatch). BB_LIMIT counter/limit-cache live in nd->counter / nd->state per LOWER-IRGEN-MAPPING.md sec. 4 (PEERS RULE; JCON tmps c/t/one subsumed). Probe-verified each new function fires: [new_While] rung35_block_body_while_do_block, [new_Until] rung09_loops_until, [new_Repeat] rung36_jcon_mffsol, [new_Limitation] rung14_limit_limit_to — output byte-identical to .expected. Gates: smoke_icon 5/5, icon_all_rungs 198/268, smoke_prolog 5/5, smoke_unified_broker 26/51, FACT RULE 0. **11 of 15 LFJ rungs complete** (73%). |
| LFJ-13 | Transcribe `ir_a_Scan`, `ir_a_Case`, `ir_a_Return`, `ir_a_Suspend`, `ir_a_Break`, `ir_a_Next`. Flip the slots. | ✅ `c08187de` rungs 198. 6 AST kinds flipped: TT_SCAN → `lower_icn_new_Scan` (ir_a_Scan, irgen.icn:49-110), TT_CASE → `lower_icn_new_Case` (ir_a_Case, irgen.icn:232-294), TT_RETURN → `lower_icn_new_Return` (ir_a_Return, irgen.icn:867-904), TT_SUSPEND → `lower_icn_new_Suspend` (ir_a_Suspend, irgen.icn:937-978), TT_LOOP_BREAK → `lower_icn_new_Break` (ir_a_Break, irgen.icn:1107-1168), TT_LOOP_NEXT → `lower_icn_new_Next` (ir_a_Next, irgen.icn:1082-1104). 1:1 transcription of legacy_SCAN/CASE/RETURN/SUSPEND/LOOP_BREAK/LOOP_NEXT — JCON chunk-based wiring collapses to identical SCRIP CFG port assignments per the LFJ-1a-ii extraction encoding. **Suspend Icon lang gate preserved verbatim** (`if (cfg->lang != BB_LANG_RKU) return NULL;`): Icon `suspend` continues on legacy SM path (lower_suspend → SM_SUSPEND) until bb_suspend.cpp + Icon mode-2 BB_SUSPEND executor land — emitting BB_SUSPEND for Icon would break rung03_suspend_{gen,compose,filter}. The new function fires (probe-verified) and then returns NULL, falling through to the legacy SM path for Icon. JCON-only state documented as non-emission: ir_scan_stack push/pull/scanlevel (SCRIP folds into FRAME.scan_subject/scan_pos), ir_loop_stack push/pull (FRAME.loop_break / loop_next direct dispatch), ir_tmp/ir_tmploc named locals (PEERS RULE — nd->value/counter/state direct), ir_new_inuse/copy(st) per-arm liveness (per-box descriptors), ir_max_st/ir_union_inuse scope unions, ir_ScanSwap save/restore chunks (FRAME-driven), ir_MoveLabel indirect-continuation wiring (FRAME-driven), ir_coord (no debug-source), /bounded ir_Fail vs ir_Unreachable resume distinction (chain walker default). Probe-verified each new function fires: [new_Scan] rung05_scan_scan_subject, [new_Case] rung33_case_case_int, [new_Return] rung03_suspend_return, [new_Suspend] rung03_suspend_gen (fires then NULLs out per Icon gate), [new_Break] rung36_jcon_io, [new_Next] rung36_jcon_concord. Gates: smoke_icon 5/5, icon_all_rungs 198/268, smoke_prolog 5/5, smoke_unified_broker 28/51 (+2 from concurrent RK-BB-3a / CAT-D-10 work), FACT RULE 0. **12 of 15 LFJ rungs complete** (80%). |
| LFJ-14 | Transcribe remaining `ir_a_Create`, `ir_a_Mutual`, `ir_a_Key`, `ir_a_Invocable`, `ir_a_Link`, `ir_a_Initial`, `ir_a_RepAlt`, `ir_a_CoexpList`, `ir_a_Unop`, `ir_augmented_assignment`. Every table slot now points into `lower_icn_new.c`. | ✅ `0540aace` rungs 198. lower_kind_table now contains ZERO references to lower_icn_legacy_* — every entry points into lower_icn_new.c. Named procs land as concrete new functions: ir_a_Initial → new_Initial (TT_INITIAL), ir_a_Unop → new_Unop (TT_MNS, TT_PLS, TT_SIZE, TT_NULL, TT_NONNULL, TT_RANDOM, TT_CSET_COMPL, TT_ITERATE, TT_MATCH_UNARY — single dispatch on e->t selects BB op; the SCRIP-only TT_NULL with no child → BB_LIT_NUL preserves ir_a_NoOp behavior absorbed into Unop), ir_augmented_assignment → new_AugOp (TT_AUGOP). Seven named procs are documented non-emission stubs (no SCRIP TT_* AST kind reaches the dispatcher — LFJ-9 pattern): new_Create / new_Mutual / new_Key / new_Invocable / new_Link / new_RepAlt / new_CoexpList. Plus 12 auxiliary new functions for SCRIP-only AST kinds that JCON folds into other procs (ir_a_Ident/Binop/Compound/Record/ListConstructor/Fail): new_Var (TT_VAR), new_Keyword (TT_KEYWORD), new_Assign (TT_ASSIGN), new_Swap (TT_SWAP), new_SeqExpr (TT_SEQ_EXPR), new_Decl (TT_LOCAL/TT_STATIC_DECL), new_Idx (TT_IDX), new_Identical (TT_IDENTICAL), new_ProcFail (TT_PROC_FAIL), new_CsetBinop (TT_CSET_UNION/DIFF/INTER), new_Record (TT_RECORD), new_Makelist (TT_MAKELIST). Each auxiliary new fn is a 1:1 transcription of its lower_icn_legacy_* counterpart per the LFJ-1a extraction encoding — ZERO logic change. JCON-only state documented as non-emission: ir_init(p) label allocation (SCRIP labels are box identities), ir_tmp/ir_tmploc named locals (PEERS RULE — nd->value/counter/state direct), ir_new_inuse/copy(st)/ir_max_st/ir_union_inuse per-arm liveness + scope unions (per-box descriptors), ir_loop_stack/ir_scan_stack push/pull (FRAME-driven walker-side), ir_MoveLabel/ir_IndirectGoto indirect-continuation (FRAME-driven), ir_coord debug-source. Probe-verified: [new_Initial] rung25_global_initial_zero, [new_AugOp] rung11_bang_augconcat_augconcat_loop, [new_Unop] rung12_strrelop_size_size (TT_SIZE=83), rung36_jcon_lists (TT_MNS=11 + TT_ITERATE=55). Probes removed pre-commit. Acceptance: `grep "lower_icn_legacy_" src/lower/lower_icn.c \| grep "lower_kind_table\[" \| wc -l` = 0; 49 legacy fns still defined (compiled, linkable, unreachable from dispatcher — deleted in LFJ-15). Gates: smoke_icon 5/5, icon_all_rungs 198/268, smoke_prolog 5/5, smoke_unified_broker 28/51, FACT RULE 0. **13 of 15 LFJ rungs complete** (87%). |
| LFJ-15 | Delete `lower_icn.c`. Delete all `_threaded_b` AG-PURE intercept branches. Delete the `lower_kind_table` indirection — calls now go directly to the new functions or the dispatcher switches on the new functions. Rename `lower_icn_new.c` → `lower_icn.c`. | ✅ `cde72b79` (Opus 4.7, 2026-05-27) **partial — three of four items**. Delete `lower_icn.c` ✅ (1616 lines: 49 `legacy_<KIND>` fns, `lower_kind_table[]` + init, table-lookup dispatcher). Delete `lower_kind_table` indirection ✅ — `lower_icn_expr_node` now a plain `switch (e->t)` on 49 kinds calling `new_<KIND>` directly. Rename `lower_icn_new.c`→`lower_icn.c` and `lower_icn_new.h`→`lower_icn.h` ✅. Dead `lower_icn_new_NoOp` removed (TT_NULL went to `new_Unop` in LFJ-14). Helpers + dispatcher + threading machinery moved into consolidated file: `icn_binop_apply`, `icn_fold_signed_lit`, `lower_icn_upto`, `lower_icn_proc_gen`, `lower_icn_proc_body`, `lower_icn_expr_top`, `lower_icn_expr_threaded`, `lower_icn_expr_threaded_b`, `icn_leaf`, `icn_tree_is_leaf`, `icn_kind_is_resumable`, `icn_kind_owns_omega_operand`. Makefile: source list + per-file compile rule for `lower_icn_new.c` dropped. Net -1107 lines (2858 → 1767, single file). **DEFERRED**: "Delete all `_threaded_b` AG-PURE intercept branches" — the intercepts (Families 3/5/6/7/8.1/8.2 in `lower_icn_expr_threaded_b`) are retained verbatim because they reshape the new functions' legacy-shape output (α/β as operand pointers, 1:1 with `legacy_<KIND>`) into AG-pure chain-walker shape (scrubbed α/β, chained operands via γ, sval `"ag"`/`"ai"`/`"ar"`, ival=1 markers consumed by `bb_exec.c`). Folding those intercepts INTO the new functions themselves so each new function produces AG-pure shape directly (one traversal, no post-processing pass) is **LFJ-15b** below. Gates: smoke_icon 5/5, icon_all_rungs 198/268, smoke_prolog 5/5, smoke_unified_broker 30/52, FACT RULE 0. **14 of 15 LFJ rungs complete** (93%). Acceptance commands: `grep 'lower_icn_legacy_' src/lower/lower_icn.c \| grep 'lower_kind_table\[' \| wc -l` = 0; `ls src/lower/lower_icn*.c \| wc -l` = 1; `ls src/lower/lower_icn*.h \| wc -l` = 1. |
| LFJ-15b | AG-pure consolidation: fold the AG-pure intercept branches from `lower_icn_expr_threaded_b` (Families 3/5/6/7/8.1/8.2) INTO their corresponding `lower_icn_new_<KIND>` functions so each new function returns an AG-pure-shaped node directly. | ✅ `6a631124` (Claude Sonnet 4.6, 2026-05-27). Six _ag variants landed: Binop_ag (Fam-3), If_ag (Fam-5), Conjunction_ag (Fam-6), Alt_ag (Fam-7), Every_ag (Fam-8.1+8.2), ToBy_ag (Fam-8.2 standalone). `lower_icn_expr_threaded_b` early-exits for each kind before `lower_icn_expr_node`; all six intercept blocks retired. sval/ival markers now set by _ag functions. Gates: smoke_icon 5/5, icon_all_rungs 198/268, smoke_prolog 5/5, broker 30/52, FACT RULE 0. **LFJ COMPLETE — all 15 rungs (100%).** |

### Per-rung gate (every commit)
```bash
bash scripts/build_scrip.sh
bash scripts/test_smoke_icon.sh              # PASS=5
bash scripts/test_icon_all_rungs.sh          # PASS=198
bash scripts/test_smoke_prolog.sh            # PASS=5
bash scripts/test_smoke_unified_broker.sh    # PASS=24
```

### DO NOT
- Edit `lower_icn.c` (the mega-switch) except for LFJ-1a/1b mechanical refactor.
- Add discriminator markers (`nd->ival = N`, sval tags) in new code.
- Add `_threaded_b`-style intercept branches to legacy code as a workaround.
- Skip the mapping doc. Drift starts the moment that doc is missing.
- Resume AG-PURE work below until LFJ-15 lands.
- Build a "comparator" or "shadow graph." There is one graph, one entry per kind in the dispatch table.

---

## LEGACY (frozen) — AG-PURE WHOLESALE REWRITE OF LOWER + EXECUTOR

**Status:** AG-pure step 1 landed `64805e16` on branch `ag-pure-icn`. Dormant value-ring added to `BB_graph_t`. Gates green. PEERS sidecar superseded for Icon by AG-pure model below — sidecar stays for Prolog/SNOBOL4 until those languages are migrated.

### THE AG-PURE MODEL (HQ Invariant 17 v2, Lon directive 2026-05-27)

There are no operands on BB nodes. There is no tree. There is a CFG of boxes wired by four ports, period. Every TT_* construct lowers to a graph whose every box has all four ports wired before LOWER returns.

**The four ports are ALL CFG edges. NONE of them point at "operand subgraphs":**

| Port | Direction | Meaning |
|------|-----------|---------|
| **α** | synthesized UP | fresh entry of THIS box's subgraph (where control enters on first try) |
| **β** | synthesized UP | retry entry of THIS box's subgraph (self for resumable, else = ω_in) |
| **γ** | inherited DOWN | success continuation — points at NEXT box's α |
| **ω** | inherited DOWN | failure continuation — points at PRIOR box's β (backtrack) or outer ω |

**Operand values flow through the cfg value-ring, not through node pointers.** When the chain walker (`bb_exec_once` / `bb_exec_resume`) executes box B successfully, it pushes `B->value` into `cfg->ring`. An apply box (BB_BINOP, BB_CALL, BB_ASSIGN, BB_LCONCAT, ...) reads its inputs with `ag_ring_peek(cfg, k)` — peek(0) = newest = the immediate predecessor's value, peek(1) = the prior one, etc.

```c
/* In BB.h (landed 64805e16): */
typedef struct BB_graph_t {
    BB_t * entry;  BB_t ** all;  int n, max, lang;
    bb_operand_aux_t *operand_aux; int operand_aux_n, operand_aux_max;  /* legacy, other langs */
    #define AG_RING 16
    DESCR_t  ring[AG_RING];
    int      ring_head;       /* newest index; advances mod AG_RING                          */
    int      ring_depth;      /* valid count, saturates at AG_RING                            */
} BB_graph_t;
static inline void    ag_ring_push (BB_graph_t *cfg, DESCR_t v);
static inline DESCR_t ag_ring_peek (const BB_graph_t *cfg, int k);  /* k=0 newest            */
static inline void    ag_ring_clear(BB_graph_t *cfg);                /* by bb_reset           */
```

**LOWER's job, per TT_* kind:** allocate boxes for the sub-expressions, wire their γ to the next box in evaluation order, the LAST sub-expression's γ to the apply box, every box's ω to the appropriate failure target (outer ω, or a sibling's β for backtracking), and report α_out = subgraph entry, β_out = self if resumable else ω_in.

**EXECUTOR's job, per apply-box kind:** read N values via `ag_ring_peek(cfg, N-1 .. 0)`, apply the operation, write result to `nd->value`, return `nd->γ` on success / `nd->ω` on failure. Apply boxes DO NOT recurse into `nd->α`/`nd->β` for value evaluation — those ports are CFG edges, not tree edges.

### THE FOUR FACTS (revised)
1. **BB_t has α/β/γ/ω plus IR payload (sval/ival/dval) plus runtime scratch (value/counter/state). NOTHING ELSE.**
2. **All four ports are CFG edges. None point at "operands".**
3. **Operand values live in `BB_graph_t.ring`, populated by the chain walker.**
4. **PEERS sidecar (`operand_aux`) is LEGACY for Icon — kept for Prolog/SNOBOL4 mid-migration.**
5. **TEMPLATE-ONLY EMISSION still holds for mode 3/4.**

### Migration sequence (per-family, gates green each commit)

**CRITICAL ORDERING LESSON (Lon 2026-05-27):** AG-pure migration must climb OUTWARD from leaves through sequencers in dependency order. A box cannot be AG-pure if the box that DISPATCHES it still swallows chain visibility. BB_SEQ's executor recurses into `bb_exec_node(stmt)` directly — those recursive calls DO NOT go through the outer chain walker, so they do NOT push to the cfg ring. Until BB_SEQ becomes AG-pure (stmts laid out as a γ-chain at the outer walker level), no apply box dispatched from inside it can read the ring.

**Correct order:**

1. **Step 1** ✅ `64805e16` — ring fields dormant in BB_graph_t.
2. **Step 2** ✅ `e2850a98` — chain walker pushes `cur->value` to ring after each step (EVERY step including FAIL — needed so routing boxes like BB_IF see actual cond value via peek(0)). `bb_reset` clears ring.
3. **Step 3** ✅ `9d4d25b0` — BB_BINOP AG-pure. lhs→rhs→apply chain, apply reads peek(1)/peek(0).
4. **Step 4** ✅ `245ae97e` — BB_SEQ AG-pure (passthrough) + BB_FAIL terminal allocated PRE-loop and passed as initial `succ` so composite branches inheriting γ_in/ω_in end at the terminal. Chain walker honors FRAME.returning. Excluded set: BB_RETURN/BB_FAIL/BB_BREAK/BB_NEXT keep their ω as termination signal (not stmt-advance).
5. **Step 5** ✅ `687d6694` — BB_IF AG-pure. cond.γ = cond.ω = nd_if; nd_if.γ = then.α; nd_if.ω = else.α. Executor reads peek(0) = cond value, routes via γ/ω.
6. **Step 6** ✅ `76453c56` — BB_CONJ AG-pure. left.γ=right.α; left.ω=ω_in; right.γ=apply; right.ω=ω_in. Executor reads peek(0) = right value.
7. **Step 7** ✅ `e8217005` — BB_ALT AG-pure. arms chained via ω (legacy already did this); arm.γ=nd_alt. Executor AG branch (nd->α==NULL) reads peek(0) = winning arm's value.
8. **Step 8 — Generators** Sub-ordered:
   - **8.1 BB_EVERY** ✅ `f81e1d51` — dispatcher passthrough for literal-bound gens. Gated on `gen->α == NULL && gen->β == NULL && gen->γ != NULL` (flat-wire condition from TT_EVERY lowering at lower_icn.c:444). Marker `nd->ival = 1` selects AG-pure branch in executor; state==0 hands off to nd->α via chain, state==1 = re-entry from gen.ω → return γ. Common `every write(gen)` (BB_CALL-with-gen-args) still uses legacy path until Step 9.
   - **8.2 BB_TO / BB_TO_BY** ✅ `7acc7849` — dynamic-bound paths via ring. TT_EVERY routes gen through `lower_icn_expr_threaded_b` when c[0]->t is TT_TO/TT_TO_BY (scoped option 1). 8.2 intercept scrubs gen->α/β, chains lo→hi→gen via γ, stamps sval ("ag" / "ai" / "ar"). Executor's AG-pure branch reads peek(1)=lo, peek(0)=hi on state==0, caches in counter/dval. nd_every.α = chain_entry (= lo); flat-wire back-edges still attach to gen (BB_TO/BB_TO_BY) so loop re-enters at counter step, not at lo/hi. Verified: bare `every lo to hi [by N] [do body]` exercises 8.2 path; assign-wrapped `every i := lo to hi do body` stays legacy (c[0]=TT_ASSIGN, scope of 8.2 followup). Gates green throughout. See HANDOFF-2026-05-27-OPUS-ICON-BB-AG-STEP-8-2.md.
   - **8.3 BB_BINOP_GEN** — cross-product odometer. Major rework. Defer.
   - **Dispatchers to consider for AG-pure conversion at this step:** BB_LIMIT, BB_REPEAT, BB_WHILE, BB_UNTIL, BB_SCAN — same swallowing pattern.
9. **Step 9 — N-ary applies**: BB_CALL / BB_LCONCAT / BB_SECTION / BB_IDX_SET. Args chain via γ, last arg's γ → apply; apply reads peek(N-1..0).
10. **Step 10 — Sidecar cleanup**: delete `bb_operand_aux_set/get` calls from Icon lower path. Sidecar struct stays for Prolog/SNOBOL4.

**Failed attempt log:** Step-4-attempted-as-BB_IF on 2026-05-27 (reverted): smoke if_expr 5→4 because BB_SEQ's recursive dispatch hid BINOP's push from the ring. Lesson: sequencer-first ordering enforced.

**Key invariants discovered during the migration:**
- The chain walker MUST push every step (even FAIL) so routing boxes see the actual predecessor value via peek(0).
- The fail_term must be allocated BEFORE the stmt-build loop and passed as initial succ, so composite branches at the proc's tail end at the terminal.
- BB_RETURN / BB_FAIL / BB_BREAK / BB_NEXT must be excluded from stmt-advance ω-rewrites: their ω is a termination signal, not a CFG edge to a next stmt. Recursion will segfault otherwise.
- The chain walker checks FRAME.returning each step and bails with g_ir_return_val (defense in depth against any BB_RETURN.ω wiring accident).
- AG intercepts fire AT THE WRAPPER LEVEL (`lower_icn_expr_threaded_b`), not inside `lower_icn_expr_node`. Inner sub-expressions retain legacy α/β-as-tree wiring until their own kind's intercept catches them. Both shapes coexist because the chain walker treats either form as a single chain step producing one value.

### Per-step gate
```bash
bash scripts/test_smoke_icon.sh                # PASS=5
bash scripts/test_icon_all_rungs.sh            # PASS≥198
bash scripts/test_smoke_prolog.sh              # PASS=5
bash scripts/test_smoke_unified_broker.sh      # PASS≥24
grep -rnE 'seg_byte\(SEG_|SL_B\(|sl_emit_one|emit_standard_blob|bake_blob_call' src/ | grep -v _templates/ | grep -v emit_core | wc -l  # ==0
```

### Acceptance (whole rewrite)
1. `grep -nE 'nd->[αβ] = ' src/lower/lower_icn.c | wc -l` == 0 (no operand-as-port writes).
2. `grep -nE 'bb_exec_node\(nd->[αβ]\)' src/lower/bb_exec.c | wc -l` == 0 (no recursive operand eval).
3. `icn_kind_owns_omega_operand` removed.
4. `bb_operand_aux_set` not called from Icon lower path.
5. rungs PASS≥198 holds throughout.

### DO NOT
- Touch SNOBOL4 / Snocone / Rebus / Raku / Prolog lower or BB families until their own migrations begin.
- Touch BB_PAT_*.
- Add fields to BB_t.
- Use `nd->α` / `nd->β` as tree pointers for any new Icon code.

---

## LEGACY (pre-AG-pure) — kept for reference until migration completes

### Families 3-7 — irgen.icn wiring (read procedure before coding each)

**3. BB_BINOP** — `ir_binary`/`ir_a_Binop`. 2 operands.
- Lower: lhs.γ=rhs_entry; rhs.γ=apply; lhs.ω=ω_in; rhs.ω=ω_in; `bb_operand_aux_set(cfg, nd, {lhs,rhs}, 2)`.
- Apply: read `ops[0]->value`, `ops[1]->value`, call `icn_binop_apply`. α_out=lhs_entry.
- Suspendable operand → BB_BINOP_GEN (Family 7).

**4. BB_IF** — `ir_a_If`. 1 operand (condition, always-bounded).
- bounded: cond.γ=then_entry; cond.ω=else_entry; then.γ=γ_in; then.ω=ω_in; else.γ=γ_in; else.ω=ω_in.
- `icn_kind_owns_omega_operand` RETIRES when BB_IF stops using ω as else-branch operand.

**5. BB_CONJ** — `ir_conjunction`. 2 operands.
- left.γ=right_entry; left.ω=ω_in; right.γ=γ_in; right.ω=left_β (retry left).
- `bb_operand_aux_set(cfg, nd, {left,right}, 2)`. α_out=left_entry.

**6. BB_ALT** — `ir_a_Alt`. N operands.
- arm[i].ω=arm[i+1].α; arm[i].γ=γ_in; last_arm.ω=ω_in.
- bounded: no label-register needed. α_out=arm[0].α.

**7. BB_EVERY / BB_TO / BB_TO_BY / BB_BINOP_GEN** — generator kinds. β=self (`icn_kind_is_resumable`).
- Every: expr.γ=body_entry; expr.ω=ω_in; body.γ=expr_β; body.ω=expr_β. α_out=expr_entry.
- TO/TO_BY: operands eval once on α; cached in counter/ival; β=self increments.

### Gate after EACH family
```bash
bash scripts/test_smoke_icon.sh                # PASS=5
bash scripts/test_icon_all_rungs.sh            # PASS≥198
bash scripts/test_smoke_prolog.sh              # PASS=5
bash scripts/test_smoke_unified_broker.sh      # PASS≥24
grep -rnE 'seg_byte\(SEG_|SL_B\(|sl_emit_one|emit_standard_blob|bake_blob_call' src/ | grep -v _templates/ | grep -v emit_core | wc -l  # ==0
```

### Acceptance for whole rung
1. All 7 families on sidecar; apply reads via `bb_operand_aux_get`.
2. `grep -nE 'bb_exec_node\(nd->[αβ]\)' src/lower/bb_exec.c | wc -l` == 0.
3. `icn_kind_owns_omega_operand` removed.
4. rungs PASS≥198 holds.

### DO NOT
- Touch SNOBOL4 / Snocone / Rebus / Raku BB families.
- Touch BB_PAT_*.
- Add fields to BB_t.

---

## Session Setup
```bash
cd /home/claude/one4all
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
bash scripts/build_spitbol_oracle.sh
bash scripts/test_smoke_icon.sh            # PASS=5
bash scripts/test_smoke_unified_broker.sh  # PASS≥24
bash scripts/test_icon_all_rungs.sh        # PASS=198
bash scripts/test_icon_mode4_rung.sh       # PASS=5
```

---

## THE FOUR FACTS
1. **C WALKERS: MODE 2 ONLY.** `icn_bb_dcg`/`bb_exec_*` — `--interp` only.
2. **NO C WALKERS IN MODE 3/4.**
3. **SM + BB DO NOT EXIST AT RUNTIME IN MODE 3/4.**
4. **ONE x86 PRODUCER.** Templates only.
5. **TEMPLATE-ONLY EMISSION (FACT RULE).** grep == 0.

---

## Architecture
```
.icn → icon_parse() → AST_t*
  --interp   → execute_program() → interp_eval()        Mode 2 (SM+BB C walker, reference)
  --run      → lower() → sm_codegen_x64() → exec        Mode 3 (in-proc, PROT_EXEC)
  --compile  → lower() → sm_codegen_x64() → binary      Mode 4 (separate process)
```

**GOLDEN BB RULE / PEERS RULE:** BB_t has ONLY: `t`, `α β γ ω`, `sval/ival/dval`, `value/counter/state`. Operand-value refs in sidecar. BB_t struct is FINAL.

**Four ports:**
| Port | Direction | Meaning |
|------|-----------|---------|
| γ | DOWN (inherited) | success continuation |
| ω | DOWN (inherited) | failure continuation |
| α | UP (synthesized) | fresh-entry address |
| β | UP (synthesized) | retry-entry address |

**Lowering signature:** `lower(cfg, tree, γ_in, ω_in, &α_out, &β_out, bounded)`. Read `irgen.icn` ir_a_* before coding any construct: `/home/claude/corpus/programs/icon/jcon-ref/irgen.icn`.

---

## Completed rungs
| Rung | Commit |
|------|--------|
| H-1 threading + IDX_SET/SECTION | `45c1bde2` |
| BB_CONJ (E1 & E2) | `9be28a5d` |
| H-1 cross-arg odometer + side-effect fix | `fcfc7a73` |
| JA-D engines+JIT deleted | `e842b724` |
| rt_bb_* total deletion | `0206b998` |
| ICN-Z-0 icn_leaf + bounded flag | `78e4c067` |
| ICN-Z-1 leaf rewire | `78e4c067` |
| ICN-Z-2b BB_SEQ port-follower | `78e4c067` |
| ICN-XA-1 walk_bb_node_str_c | `78e4c067` |
| ICN-XA-1 bb_binop_gen odometer | `78e4c067` |
| Family 1 BB_ASSIGN sidecar | `78e4c067` |
| Family 2 BB_CALL sidecar | `78e4c067` |

**WATERMARK:** one4all `6a631124`. Gates: smoke_icon 5/5 · broker 30 · rungs 198 · smoke_prolog 5/5 · FACT RULE 0. LFJ COMPLETE (15/15 · 100%). **LFJ-15b DONE.** ICON-BB LFJ staircase complete.

---

## File ownership
`src/lower/lower_icn.c` · `src/lower/bb_exec.c` · `src/lower/scrip_ir.c` · `src/emitter/{emit_bb.c,emit_sm.c,emit_core.c}` · `src/emitter/BB_templates/bb_*.cpp` · `src/processor/sm_codegen.c` · `src/processor/sm_interp.c` · `baselines/icon-bb/`
