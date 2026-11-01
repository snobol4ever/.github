---
name: lowering
description: Writing lowerers in SCRIP/src/lower (pruned parse tree in, IR graph out): every language variance as an IR fact, runtime tables built by lower, builtins resolved at lower, --dump-ast and --dump-ir as proof. REQUIRED by the skill gate before editing src/lower, with the language skill.
---

# Lowering: the craft

The lowerer is the ONE stage that knows a language. The parser hands it a `tree_t` and nothing else (CEO-1322); it builds an `IR_graph_t` population of four-port nodes wired γ/ω, and from there on there is no language: the planner, the emitter and the templates read the IR and nothing else (`ARCH-IR-CARRIES-EVERY-LANGUAGE-VARIANCE.md` § 1). The law is RULES.md (THE TREE IS THE PRUNED PARSE TREE, A PARSER MOVES NOTHING, THE LOWERER PLACES IT, CEO-1369/1371/1377/1378/1532; ONLY tree_t CROSSES, EVERY RUNTIME TABLE IS BUILT BY LOWER, CEO-1322; NO LANGUAGE FLAG PAST THE DRIVER, A DELETION CARRIES ITS RE-EXPRESSION, CEO-1838/1840; NO C FUNCTION ENTERS A BOX, CEO-1576), the design `ARCH-IR-CARRIES-EVERY-LANGUAGE-VARIANCE.md` and `ARCH-BUILTIN-TABLE.md`. Lines quoted below are from SCRIP 8e366c454.

## 1. THE RULES (each with its receipt)

- **THE TREE IN IS THE PRUNED PARSE TREE, IN SOURCE ORDER**: one node per rule that fired, the operator in the value, `TT_NUL` for an absent operand, positions as one byte-offset field; the lowerer imposes the semantics where canonical order differs from source order (the Icon `case` default, CEO-1371: *"Why move it in parser. That is the lower's job."*). The lowerer reads tree attributes by name (`lc_stmt_subj` finds the `:subj` TT_ATTR child, lower_common.c 248) and never patches the tree.
- **EVERY VARIANCE IS AN IR FACT** (CEO-1838/1840; ARCH-IR-CARRIES § 1): one of three things, written because a construct is in the source -- a GRAPH FACT from the closed registry (`cell_frame`, `spine_cells`, `zframe_graph`, `resumable_callable`, `root_graph`, `body_root`, `entry_frame`, `static_calls`, `decl_level`, `caller_frame`, ...; § 2's table names each fact's behaviour, its setter and its readers), a NODE FACT (the kind, the operands, the literal attributes `IR_LIT(nd).ival/sval/dval`), or a RUNTIME ENTRY NAMED ON THE NODE as data (`IR_LIT(mk).sval = "SNO$PB0"`, lower_snobol4.c 1116), so the emitter emits the call without knowing why. A new graph fact is a ROW of § 2's registry before it is a field.
- **ONE FORM PER BOX, THE FORM CHOSEN HERE** (ARCH-IR-CARRIES § 3): where one box would hold two bodies chosen by an attribute, lower emits two kinds (`IR_X_CELLS` beside `IR_X`); the emitter's dispatch is a table lookup before the box, never an `if` inside it (`test_gate_template_form_choices_outside_lower_only_fall.sh`).
- **EVERY RUNTIME TABLE IS BUILT HERE** (CEO-1322): the procedure registry, the record and class shapes (Pascal's `lower_pascal_class.c`, Icon's records, Unicon's class records per ARCH-UNICON R3), the atom and functor tables, the string table, the pattern blobs, the standing cells; a table the runtime needs that no lowerer built is a defect of lower, never a runtime global (NO NEW GLOBAL without Lon's grant; `test_gate_gc_the_lowerer_registries_are_rooted_not_malloced.sh`: the registries are arena-rooted, never malloced).
- **THE BUILTIN TABLE RESOLVES AT LOWER** (ARCH-BUILTIN-TABLE § 4; `harness/scripts/builtins.tsv`, `bid vocab name min max entry conv recv flags op src`): a call to a literal name is looked up in ITS vocabulary (`bt_lookup(VOCAB_ICN, "map")`), the bid written into the node, the op chosen by the row's `conv` (`leaf` → `IR_CALL_DIRECT`, `gen` → `IR_CALL_GEN`, `open` → the method/redispatch/apply/eval ops); THE PROGRAM'S OWN DEFINITION WINS, checked before the table; ARITY is the lowerer's (pad below `min`, the vocabulary's over-arity rule above `max`), so no leaf pads at run time; no row and no definition → the dynamic road `IR_CALL_BYNAME`, the only one.
- **PLACEMENT IS NOT HERE EITHER** (CEO-1895): lower names kinds and facts; the planner decides every cell's zeta and depth once; a lowerer that writes a slot offset or a frame distance is deciding placement (`ir_varslot_of` and the frame layout are the planner's readers, `frame_layout.c`'s inputs are the kinds).
- **A DELETION CARRIES ITS RE-EXPRESSION IN THE SAME LANDING** (CEO-1840): a language-prefixed op, flag or helper removed from the emitter is re-expressed as an IR fact in the same commit; the restoration of 2026-10-18 (ARCH-IR-CARRIES § 5) is what happens otherwise.
- **THE RUN-TIME COMPILE ROADS LOWER THE SAME WAY**: `CODE`/`EVAL`, an asserted clause, a Pascal `exec` fragment go through the same lowerer (`sno_lower_fragment_at`, `runtime_eval.c`'s four sites) -- no second lowerer, no shortcut.
- **STYLE** (CEO-1565): hand-written `.c` on the 200-column hierarchy rule, zero comments, zero blank lines; `lower_common.c` holds what two lowerers share, and `lc_*` is its prefix.

## 2. THE FILES

- `SCRIP/src/lower/`: `lower_snobol4.c` (5,545; `lower_snobol4(const tree_t *)` at 5543 returning `sno_lower_fragment_at(prog, 0, 0, 0)`; the pattern kinds, `sno_predef_pat_names` 205, the SPITBOL semantics), `lower_snocone.c` (230, over the SNOBOL4 lowerer), `lower_rebus.c` (518), `lower_icon.c` (3,635; `lower_icon_proc(prog, pd)` 3303; the `lower_*_impl(icx_t * cx, const tree_t * t, IR_t * γ, IR_t * ω, IR_t ** res, int lv)` family), `lower_prolog.c` (6,459; the clause graphs, `resumable_callable`, the trail and choice points) and `lower_prolog_chr.c` (627), `lower_pascal.c` (1,537; `lower_pascal_proc` 1307), `lower_pascal_tree.c` (7,739; the elaboration over the typer, `pas_shadow_name` the one authority that names a routine), `lower_pascal_types.c` (1,411), `lower_pascal_class.c` (1,104), `lower_raku.c` (7,714; `lower_raku_proc` 3020), `lower_common.c` (529; `lc_build`, `lc_γ_to`, `lc_ω_to`, `lc_stmt_subj`, the bb-source index), `tree_to_sno.c` (676; the Snocone transpile road). `g_lower.h` (`g_lower_t g_lower`, the lowerer's one state struct; its `lc` sub-struct the common state).
- `SCRIP/src/ir/`: `IR.h` (the op enum at 27, `IR_t` 133-150: `operands`, `n_operands`, `IR_LIT(nd)` 150 the literal payload; `IR_graph_t` and the graph-fact registry), `scrip_ir.c` (the op name table the dumps print), `ct_arena.c` (every compile-time population).
- The tables lower writes from: `harness/scripts/builtins.tsv` → `src/runtime/builtin_table.inc` + `builtin_table.h` (`util_gen_builtin_table.py`, gated by `test_gate_builtin_table_is_current.sh`); `src/lower/lower_call_forms.c` (the table-driven call road).
- The dumps: `./scrip --dump-ast prog` (the tree the parser handed over), `./scrip --dump-ir prog` (the graph: slot, γ, ω, kind, operands, payload), `--dump-bb`, `--dump-plan`; `SCRIP_PARSE_STAGE=sc` to lower from the Snocone parser's tree.

## 3. WORKED EXAMPLES (quoted)

The one constructor every lowerer builds with, `lower_common.c` 245: a node of kind `op` wired to its γ and ω successors at birth; the attribute reader beside it finds a tree attribute by its name.

```c
IR_t * lc_build(IR_graph_t * g, IR_e op, IR_t * γ, IR_t * ω) { IR_t * nd = IR_node_alloc(g, op); lc_γ_to(nd, γ); lc_ω_to(nd, ω); return nd; }
const tree_t * lc_stmt_subj(const tree_t * s) {
    for (int i = 0; i < s->n; i++) { const tree_t * a = s->c[i]; if (a && a->t == TT_ATTR && a->v.sval && !strcmp(a->v.sval, ":subj")) return (a->n > 0) ? a->c[0] : NULL; }
    return NULL;
}
```

A predefined pattern lowered as a RUNTIME ENTRY NAMED ON THE NODE, `lower_snobol4.c` 1110-1118 (`SUCCEED`, `ABORT`, `FLUSH`): a user redefinition wins (`sno_predef_registered`), else a `CALL` node carries the entry's name as data and the kind as an integer literal operand; the emitter emits `call SNO$PB0` knowing nothing of SNOBOL4.

```c
        case TT_SUCCEED:
        case TT_ABORT:
        case TT_FLUSH:
        {
            if (t->v.sval && sno_predef_registered(t->v.sval)) return sx_call_named(cx, t->v.sval, t, 0, γ, ω, res);
            IR_t * mk = lc_build(cx->g, IR_CALL, γ, ω);
            IR_LIT(mk).sval = (char *) "SNO$PB0";
            IR_t * kt = lc_build(cx->g, IR_LIT_INTEGER, mk, ω);
            IR_LIT(kt).ival = (int64_t) t->t;
```

The tree in and the graph out for `x = 'ab' 'c'` / `OUTPUT = x` (`--dump-ast`, then `--dump-ir`): the tree is one STMT per statement with named attributes; the graph is a chain of boxes, each with its γ and ω, the payload the lowerer wrote (`binop=31` is concatenation, `var="x"` the name the planner will home).

```text
(STMT :eq :subj (TT_VAR x) :repl (TT_SEQ (TT_QLIT "ab") (TT_QLIT "c")))
(STMT :eq :subj (TT_VAR OUTPUT) :repl (TT_VAR x))
;  slot   γ    ω    kind                   [operands]  payload
3@     4    19@  STATEMENT_BEGIN        []
4      5    20@  LIT_STRING             [] "ab"
5      6    20@  LIT_STRING             [] "c"
6      7    20@  BINOP                  [4,5] binop=31
7      8@   20@  ASSIGN                 [6] var="x"
```

A builtin row, `builtins.tsv`: `1 sno ** - - bt_x2Ax2A leaf - - 0 fn_arms,ids` -- bid 1, the SNOBOL4 vocabulary, the exponent operator, unbounded arity, its entry symbol, a leaf conv. The lowerer writes bid 1 into the node and op `IR_CALL_BUILTIN`; the emitter reads the row and decides nothing (ARCH-BUILTIN-TABLE § 5).

The graph-fact registry row the Prolog lowerer sets (ARCH-IR-CARRIES § 2): `resumable_callable` -- *"the callee may be re-entered at β after it has succeeded at γ (its frame survives γ)"*, set by `lower_prolog.c` for every clause graph and by `lower_snobol4.c` for a pattern thunk, read by the emitter through `resumable_frame`. A lowerer that needs the frame kept alive sets that fact; it never tells the emitter "this is Prolog".

## 4. THE PROVING INSTRUMENTS (harness/scripts)

- The dumps are the proof: `--dump-ast` unchanged by a lowering landing (the parser is not touched), `--dump-ir` of the one program before and after, read side by side; `test_gate_bootstrap_parse_stage_ir_identity.sh` (the C and `.sc` trees lower to the same IR).
- The boundary gates: `test_gate_lower_isolation.sh` (the parse→lower firewall: no parser symbol read past lower, no lower symbol read by a parser), `test_gate_emit_no_lang.sh` and `test_gate_no_lang_names.sh` (no `LANG_*`, no language name past lower), `test_gate_no_language_discriminator_in_the_runtime.sh`, `test_gate_ir_field_discipline.sh` (each `IR_t` field holds ONE kind of thing, never a pointer smuggled in an integer), `test_gate_ir_tmp_slots.sh`, `test_gate_ir_reading_voids_a_dead_run.sh`, `test_gate_template_form_choices_outside_lower_only_fall.sh` (a form chosen outside lower), `test_gate_builtin_table_is_current.sh`, `test_gate_gc_the_lowerer_registries_are_rooted_not_malloced.sh`.
- The language's own: `prove_lower.sh` (the lowering differential over the witness programs), the construct ladder `test_<lang>_ladder.sh --only N` (one rung, one construct, both modes), `test_feature_reps.sh <lang> <feature>`, `test_smoke_<lang>.sh`; a lowering change shared by two languages runs both smokes, `lower_common.c` all eight.
- The bracket for a wrong answer: `monitor_run.sh prog --oracle` (the first diverging event names the construct), then ASM-DIFF-FIRST against a passing sibling in one mode, `--dump-ir` of both, and only then gdb on the lowerer with a breakpoint at the construct's case.

## 5. THE FORBIDDEN FORMS

A language flag, name or enum written on the graph or the node for the emitter to branch on (`LANG_*`, `is_icon`, a `dval == 2.0` vocabulary stamp: the bid replaces them); a helper in the emitter or a template that means "if Prolog"; a side table keyed by node address that outlives lower (CEO-1715); a tree rewritten, re-parented or reordered by lower before it is read (the tree is read, the graph is built); a slot offset or frame distance decided here; a runtime table built by the runtime from names at run time (lower builds it, baked); a call to a literal builtin name that bypasses the table; a padded or variadic call reaching a leaf (arity is lower's); `malloc` for a registry (`ct_alloc`, rooted); a deletion of a language op without its re-expression in the same commit; a second lowerer for the run-time compile roads; a `tree_t` field added for lower's convenience (the parser owns the tree's shape, CEO-1369); a comment or a blank line.

## 6. THE ARCH PAGES

| question | page |
|---|---|
| the three kinds of variance, the graph-fact registry, one form per box, the measurables, the 2026-10-18 restoration | ARCH-IR-CARRIES-EVERY-LANGUAGE-VARIANCE.md § 1-5 |
| the builtin table: the row, the lowerer resolves, the emitter reads, the runtime leaves | ARCH-BUILTIN-TABLE.md § 3-7 |
| the pruned tree per language, the tree law and its receipts | ARCH-PASCAL-PRUNED-TREE.md, ARCH-LANGUAGES.md, ARCH-PARSER-SC-BOOTSTRAP.md § 7, RULES.md (THE TREE IS THE PRUNED PARSE TREE) |
| what the planner reads from the graph (kinds, facts), the carve per kind | ARCH-THREE-ZETAS-EMISSION.md § 6, ARCH-ZETA-ONE-COORDINATE.md § 3.5 |
| the language pages (each language's constructs as the lowerer builds them) | ARCH-ICON-RTX.md, ARCH-PROLOG-ACTIVATION-LIFETIME.md, ARCH-PROLOG-DATABASE.md, ARCH-PASCAL-REDESIGN.md, ARCH-RAKU-TO-100.md, ARCH-UNICON.md, ARCH-SNOBOL4-RTX.md |
| the receipts: CEO-1322, CEO-1369/1371/1377/1378/1532 (the tree), CEO-1838/1840 (no flag past the driver), CEO-1895 (one placement), CEO-2016 (the builtin table), CEO-1715 (no side table) | RULES.md, GOAL-CEO.md |

## 7. HOW A LANDING IS PROVED

1. Reproduce on the one program: `monitor_run.sh --oracle`, then `--dump-ast` (is the tree right? if not, the parser's row, not this one) and `--dump-ir` against a passing sibling.
2. Cure in a clean worktree: the case in `lower_<lang>.c`, a new kind in `IR.h` with its name in `scrip_ir.c` and its template (one form), a new graph fact as a registry row of ARCH-IR-CARRIES § 2 first, a new builtin as a row of `builtins.tsv` with the table regenerated before the build.
3. Prove: the DONE-WHEN red before and green after; the program re-graded in both modes (`corpus_suite_harness.py run ... --modes m3,m4 --partition entry:<name>`); `prove_lower.sh`; the boundary gates of § 4; `test_feature_reps.sh`; the smokes of every language the diff touches; `util_reflow_200.py --check` and `strip_comments.py --check` on every file touched; the dyn-caps ratchet if a table grew.
4. Land: named files only, `git commit -F -`, pull --rebase, re-prove, push; the coo re-grades the suite by `s4e_test_request.sh`.
