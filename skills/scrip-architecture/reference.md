# SCRIP's architecture: the reference (the detail behind SKILL.md; read the section you need)

Every path and symbol here was checked against SCRIP origin on 2026-11-01 (9cb24d2ca). Counts are not quoted: re-count before citing one.

## 1. The types that cross the stages

- **`tree_t`** (`src/ir/ast.h`): `{ tree_e t; int start; union { char *sval; long long ival; double dval; } v; int n; int end; tree_t **c; int line; int slen; }`. Children are `->c[i]` for `i < ->n`; `ast_push(parent, child)` grows the child vector on the compile-time arena (`ct_grow`). Kinds are `TT_*`. The tree is the PRUNED parse tree: a parser drops what lower does not need, and nothing but `tree_t` crosses to lower.
- **`IR_t`** (`src/ir/ir_node.h`): `{ IR_e op, op0; IR_ref_t γ, ω; IR_t **operands; int n_operands; int seal, pat_static, strict, elem_access; union { sval, ival, dval }; }`. Only γ and ω are stored edges; α and β are wiring concepts. `ir_operand_push(nd, child)` is the one operand-growth path: grow operands, never add fields (the PEERS RULE). `IR_ref_t` is `{ IR_t *node; char sz[4]; }`.
- **`IR_e`**, the kinds (`src/ir/ir_node.h`, the enum at the top): one kind per box form, `IR_OP_COUNT` last. A new kind needs a cell-shape row (`harness/scripts/box_cell_shapes.tsv`, generated into `src/planner/box_cell_shapes.inc` with `--write`) and a binding in `walk_bb_node_inner`.
- **`IR_graph_t`** (`src/ir/ir_graph.h`): `entry`, `all`/`n`/`max` (the nodes), the slot and name tables (`nslots`, `nparams`/`pnames`, `nlocals`/`lnames`, `vslots`), and the graph facts of § 2.
- **`stage2_t`** (`src/ir/stage2.h`, the one instance `g_stage2`): `bbp` (the `bb_program_t` of every graph, `bb_program_add`), the label table, the proc registry (`ProcEntry`), the lower segments (`lower_seg_t { prog, fn }`). Registry lookups: `src/runtime/builtins/` and the resolution helpers.
- **`DESCR_t`** (`src/ir/descr.h`): 16 bytes, a SysV rax:rdx INTEGER-class pair. Byte 0 `v` is the type tag, bytes 1-3 the source-node stamp, bytes 4-7 `slen`, then the payload union. The size and the layout are static-asserted: a 17th byte flips the return class across every asm leaf. The tags are in `descr_tags.h` and `descr_tags.inc`; `DT_FAIL` is the failure tag a caller tests in `al`.

## 2. The graph facts: the registry every language variance travels in (CEO-1836/1838/1840)

The driver reads the extension once and calls that language's parser and lowerer; after that there is no language. A machine-level difference between languages is written by the lowerer, because a construct is in the source, as (a) a graph fact from this closed registry, (b) a node fact (kind, operands, attributes), or (c) a runtime entry named on the node, so the emitter emits a call without knowing why. A fact named for a language (the deleted `icn_cells_graph`, `pl_frame`, `icn_retain`, `emit_pl_frame()`, `zls_g_pl_frame()`) never returns.

| fact (on `IR_graph_t` unless noted) | what the emitter does with it | set by |
|---|---|---|
| `cell_frame` | the activation frame holds every parameter and local as a 16-byte variable cell at a fixed offset; the frame stays live across a suspend; a call stages arguments into the callee's cells | `lower_icon.c` (every procedure), `lower_raku.c` (a generator) |
| `spine_cells` | the planner's regime: operands are spine cells read by rsp distance; a local's VAR or ASSIGN reads the local's home | same as `cell_frame` |
| `zframe_graph` | the graph owns an RBP activation frame | `frame_layout.c` from the node kinds; the driver for a main graph with an `entry_frame` |
| `resumable_callable` | the callee may be re-entered at β after γ (its frame survives γ) | `lower_prolog.c` (every clause graph), `lower_snobol4.c` (a pattern thunk, a deferred callee) |
| `resumable_frame` (on `g_emit`), `emit_resumable_frame()`, `zls_g_resumable_frame()` | derived: `zframe_graph` and (`resumable_callable` or `root_graph`) and not `cell_frame` | the emitter, per graph |
| `frame_retained` (on `g_emit`) | the graph holds a retaining node, so the frame base stays in a register for the body | derived by a scan over every graph's nodes |
| `root_graph` | the program's root (main, the Prolog top) | `lower_icon.c`, `lower_prolog.c` |
| `body_root` | the node heading the body after the pattern or head part | `lower_snobol4.c`, `lower_prolog.c` |
| `entry_frame` | the main graph installs an entry frame | `lower_raku.c` |
| `static_calls`, `decl_level`, `caller_frame` | a procedure called only statically at a known nesting level may read its caller's frame | `lower_pascal.c` |
| `poll_alpha` | the procedure's entry tests the goal-interrupt word and raises `time_limit_exceeded` | `lower_prolog.c` (a predicate on a static call cycle, a run-time compiled predicate) |

The other graph fields (`keeps_choice`, `rt_redefinable`, `jcon_value_region`, `resume_slot`, ...) owe a row: each is a behaviour fact (it stays, its row written) or a language fact in disguise (it goes). The ratchets: `test_gate_emitter_language_flags_only_fall.sh` (deleted names stay 0; graph-fact reads and language-prefixed identifiers in the emitter and templates only fall), `test_gate_template_form_choices_outside_lower_only_fall.sh` with `audit_template_forms.py` (boxes with two live forms only fall), `test_gate_emit_no_lang.sh` (`g_lang`, `LANG_`, `IR_LANG_` stay 0). One box serves one form: where a box holds two bodies, the form is chosen in lower as a distinct kind or an attribute the emitter dispatches on before the box.

## 3. The source map (directory by directory)

- `src/driver/`: `scrip.c` (main, the switches, `scrip_exts[]`, the mode branches), `scrip_sm.c` (`sm_preamble`: reset, `polyglot_init`, each segment's lowerer, `sm_resolve_proc_entry_pcs`), `polyglot.c`, `sno_parse_stage.c` (`sno_parse_stage_buf`), `driver_*.c` (calls, data, labels, procs, hooks), `sync_monitor.c` (the monitor), `stmt_ast.c`.
- `src/parsers/<lang>/`: `snobol4/` (`snobol4.y`, `snobol4.l`), `snocone/` (`snocone_parse.y`, `snocone_lex.c`), `rebus/` (`rebus.y`, `rebus.l`), `pascal/` (`pascal.y`, `pascal.l`, `prelude/`), `icon/` (`icon_lex.c`, `icon_parse.c`, `icon_driver.c`), `prolog/` (`prolog_lex.c`, `prolog_parse.c`, `prolog_lower.c`, `prelude/`, the embedded `prolog_prelude_libs.inc`), `raku/` (`rk_syntax.c`, `rk_tree.c`, `rk_regex.c`, `setting/`, the embedded `raku_setting.inc`). A grammar edit is invisible until `harness/scripts/regenerate_parser_and_lexer_from_sources.sh` runs.
- `src/ir/`: the types of § 1, `ct_arena.c` (every compile-time population; SCRIP calls no malloc), `gc_frame_map.h` (the frame-map format), `bb_pool.c`, `ir_node_index.c`, `scrip_ir.c`.
- `src/lower/`: one lowerer per language (`lower_snobol4.c`, `lower_snocone.c`, `lower_rebus.c`, `lower_icon.c` and `lower_icon_class.c`, `lower_prolog.c` and `lower_prolog_chr.c`, `lower_pascal*.c`, `lower_raku.c`), `lower_common.c`, `lower_call_forms.c`.
- `src/optimizer/`: `optimizer.c` (`optimizer_run`), `const_fold.c`, `arith_fold.c`, `copy_prop.c`, `dead_goto.c`, `dead_pure.c`, `branch_chain.c`, `gva_collect.c`, `proc_collect.c`, `ir_query.c`.
- `src/planner/`: `planner_stage.c`, `planner_stage_chains.cpp`, `zeta_plan.cpp`, `zeta_depth.c`, `plan_facts.cpp`, `planner_operands.cpp`, `planner_road.cpp`, `act_words.cpp`, `frame_layout.c`, `planner_report.cpp` (`--dump-plan`), generated `box_cell_shapes.inc`.
- `src/emitter/`: `emit.cpp` (`walk_bb_node_inner`, the prologue and epilogue), `emit_str.cpp`, `emit_call_probe.cpp`, the state headers `emit_state.h`, `emit_regime.h`, `emit_medium.h`, `g_emitter.h`.
- `src/templates/`: `bb/` (one `bb_*.cpp` per box), `xa/` (emission helpers), `x86/` (the one encoder, `x86_asm.cpp` behind `x86_ops.h` and the family headers; the generated `gc_allocating_table.inc`).
- `src/runtime/`: top level (values, strings, patterns `pattern_match.c`, arithmetic, `bignum.c`, `unification.c`, `runtime_eval.c`, `builtin_table.inc`, the generated `rt_entry_table.inc`), `rt/` (`rt.c` the call protocol, `gc_heap.c` the collector, `rt_slab.c`, `rt_coexpr.c`, `rt_pl_engine.c`, `rt_pl_trail.c`, `rt_stack_overflow.c`, `bb_pat_build.cpp`), `rtx/` (the asm leaves), `core/` (`g_runtime*.h`: the one runtime state struct `g_runtime`), `builtins/`.
- `src/tools/`: `parser_main.c` (the `out/parser_<lang>` driver), `test_template_byte_identity.c`, `emit_per_kind_audit.c`, `ipp.icn`.
- Outside `src/`: `bootstrap/` (the Snocone parsers and their library), `miscellaneous/` (the 2026-08 backend prototypes, skill `scrip-backends`), `Makefile` (skill `scrip-build`).

## 4. Retired names: what an old receipt or page names, and what it is now

| old name | now |
|---|---|
| `src/ir/IR.h` | `ir_node.h` (IR_t, IR_e), `ir_graph.h` (IR_graph_t), `ir_fwd.h` |
| `src/frontend/`, `src/contracts/`, `src/include/` | `src/parsers/`, `src/ir/`, the split headers |
| `zeta_storage.c` | `src/planner/frame_layout.c` |
| `MOD_OP_*` trace tags in `descr_tags.inc` | deleted; the 255-tag ceiling no longer binds |
| `IR_INDIRECT_GOTO`, `IR_MOVE_LABEL` | `IR_GATE`, `IR_GATE_ARM` (if-type selection only) |
| `bb_broker`, `BrokerMode` (`bb_scan`, `bb_pump`, `bb_once`) | deleted; the drive is the compile-time wiring |
| `emit_core.c`, `SM_templates/`, `BB_templates/`, `emit_jvm.c`, `emit_js.c`, `emit_wasm.c`, the `IS_JVM`/`IS_NET` arms | deleted; non-x86 `--target` refuses |
| `STMT_t.lang`, `LANG_*`, `g_lang`, `IR_LANG_*` | deleted (CEO-1838); a ratchet holds them at 0 |
| the `plc_*` Prolog solver in `by_name_dispatch.c` | deleted (the runtime-goal ruling); `plc_catch_trim` is a helper that remains |
| modes 1 and 2 | deleted |
| `icn_retaining_kind` | gone; the retained scan is a node-kind test in the emitter |

## 5. The rulings in full (for the one-line forms in SKILL.md § 3)

- **The port-exit value contract** (2026-09-01): a port transfer carries no value; rax is scratch across α, β, γ, ω. A procedure's γ exit forwards rax:rdx as the returned DESCR and the caller tests `cmp al, DT_FAIL`; since the tag is the low byte of rax, an untagged value whose low byte equals `DT_FAIL` forges a failure and silently abandons the call chain. The only site that promotes rax is procedure-exit wiring and it must follow an explicit tagged-DESCR write. The check is at the encoder's port hook (`x86_port_hook`, `src/templates/x86/x86_call.cpp`), an audit that reports (`SCRIP_PORT_EXIT_AUDIT=1`) and does not refuse; `port_exit_prepass_build` in `emit.cpp` gives it the cross-graph view. Moving `DT_FAIL` out of the value space is held in reserve.
- **The runtime-goal ruling** (Lon 2026-09-01: "Remove that Prolog runtime interpreter, we already decided that Prolog should be re-using EVAL and CODE."): `call/N`, a catch goal, the goal of an all-solutions or negation builtin and an asserted body are compiled at run time through the EVAL/CODE path and run as wired boxes; a dispatch loop over goal terms is walking by another name.
- **The co-expression stack ruling** (Lon 2026-09-02: "The pthread's storage was meant to be MMAP'd. Like any thread it needs a proper stack just like the RSP stack."): the pthread's own stack, sized by `pthread_attr_setstacksize`; never a heap block (the compactor moves blocks) and never the slab.
- **Prolog's activation frame** (Lon 2026-09-02: "give Prolog its activation ZETA like all the rest"): a predicate call is a box with an RBP frame that survives γ so β can resume it; clause alternatives are the choice box's β path, cut its ω (skill `prolog-engine`).
- **Static wiring only, unless it is an if-type construct** (Lon 2026-09-13, CEO-694): the gate write belongs to the if construct's own lowering, never to a general op every construct can reach.
- **"Stackless" is a void term** (Lon 2026-08-27): all three zetas live on the machine stack; "no software value stack" means no hand-rolled stack beside them.
