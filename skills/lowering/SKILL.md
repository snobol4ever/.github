---
name: lowering
description: Writing lowerers in src/lower: pruned tree in, IR graph out, every language variance an IR fact, builtins resolved at lower, --dump-ast and --dump-ir as proof. REQUIRED by the skill gate before editing src/lower.
---

# Lowering

The lowerer is the ONE stage that knows a language. It reads a `tree_t` (and nothing else, CEO-1322) and builds an `IR_graph_t` of four-port nodes wired γ/ω; past it there is no language. The law is RULES.md (THE TREE IS THE PRUNED PARSE TREE, ONLY tree_t CROSSES, EVERY RUNTIME TABLE IS BUILT BY LOWER, NO LANGUAGE FLAG PAST THE DRIVER); the design is skill `scrip-architecture` (the graph facts) and skill `runtime-calls` (the builtin table). Quoted code, file sizes and receipts are in `reference.md` beside this file.

## 1. THE RULES

- **The tree in is the pruned parse tree, in source order.** Read attributes by name (`lc_stmt_subj`); never patch, reorder or re-parent the tree. Where canonical order differs from source order, lower imposes it (CEO-1371).
- **Every variance is an IR fact** (CEO-1838/1840): a GRAPH FACT from the closed registry (skill `scrip-architecture` reference § 2; a new fact is a registry row first), a NODE FACT (kind, operands, `IR_LIT(nd)` payload), or a RUNTIME ENTRY NAMED ON THE NODE as data. Never a language flag.
- **One form per box, chosen here:** two bodies chosen by an attribute become two kinds (`IR_X_CELLS` beside `IR_X`).
- **Every runtime table is built here** (CEO-1322): procedure registry, record and class shapes, atom and functor tables, string table, pattern blobs; arena-rooted, never malloced; no new global.
- **Builtins resolve here** (`builtins.tsv`): look the literal name up in its vocabulary, write the bid, pick the op by `conv` (`leaf` → `IR_CALL_DIRECT`, `gen` → `IR_CALL_GEN`); the program's own definition wins; arity is lower's; no row and no definition → `IR_CALL_BYNAME`.
- **Placement is not here** (CEO-1895): lower names kinds and facts; the planner decides cells.
- **A deletion carries its re-expression in the same landing** (CEO-1840).
- **Run-time compile roads lower the same way** (CODE/EVAL, assert, exec): one lowerer.
- **Style**: the C rules of skill `scrip-c-code` section 1 (CEO-1565: the column rule, zero comments, zero blank lines); shared helpers in `lower_common.c` with the `lc_` prefix.

## 2. THE FILES

- `$S4E_SCRIP/src/lower/`: `lower_snobol4.c`, `lower_snocone.c`, `lower_rebus.c`, `lower_icon.c`, `lower_prolog.c` and `lower_prolog_chr.c`, `lower_pascal.c` with `lower_pascal_tree.c`, `_types.c`, `_class.c`, `lower_raku.c`, `lower_common.c`, `lower_call_forms.c`, `tree_to_sno.c`; `g_lower.h` (the one state struct).
- `$S4E_SCRIP/src/ir/`: `ir_node.h` (the op enum `IR_e`, `IR_t`, `IR_LIT`), `ir_graph.h` (`IR_graph_t` and the graph-fact registry), `scrip_ir.c` (op names), `ct_arena.c`.
- Tables: `/home/harness/scripts/builtins.tsv` → `src/runtime/builtin_table.inc` (`util_gen_builtin_table.py`).
- Dumps: `./scrip --dump-ast prog`, `--dump-ir`, `--dump-bb`, `--dump-plan`; `SCRIP_PARSE_STAGE=sc` lowers from the Snocone parser's tree.

## 3. WORKED EXAMPLES

The one constructor, `lower_common.c`:

```c
IR_t * lc_build(IR_graph_t * g, IR_e op, IR_t * γ, IR_t * ω) { IR_t * nd = IR_node_alloc(g, op); lc_γ_to(nd, γ); lc_ω_to(nd, ω); return nd; }
```

A runtime entry named on the node, `lower_snobol4.c` (SUCCEED, ABORT, FLUSH; a user redefinition wins):

```c
            if (t->v.sval && sno_predef_registered(t->v.sval)) return sx_call_named(cx, t->v.sval, t, 0, γ, ω, res);
            IR_t * mk = lc_build(cx->g, IR_CALL, γ, ω);
            IR_LIT(mk).sval = (char *) "SNO$PB0";
```

Tree in, graph out, for `x = 'ab' 'c'`:

```text
(STMT :eq :subj (TT_VAR x) :repl (TT_SEQ (TT_QLIT "ab") (TT_QLIT "c")))
6      7    20@  BINOP                  [4,5] binop=31
7      8@   20@  ASSIGN                 [6] var="x"
```

## 4. THE PROVING INSTRUMENTS

In `/home/harness/scripts/`: the dumps are the proof (`--dump-ast` unchanged, `--dump-ir` before and after); `test_gate_lower_isolation.sh`, `test_gate_emit_no_lang.sh`, `test_gate_no_lang_names.sh`, `test_gate_ir_field_discipline.sh`, `test_gate_template_form_choices_outside_lower_only_fall.sh`, `test_gate_builtin_table_is_current.sh`, `test_gate_bootstrap_parse_stage_ir_identity.sh`; `test_<lang>_ladder.sh --only N`; `test_feature_reps.sh`; the smokes (`lower_common.c`: all eight). For a wrong answer: `monitor_run.sh prog --oracle`, then asm-diff, then gdb at the construct's case.

## 5. THE FORBIDDEN FORMS

A language flag, name or enum on the graph for the emitter to branch on; "if Prolog" in the emitter or a template; a side table keyed by node address past lower (CEO-1715); the tree rewritten or reordered; a slot offset or frame distance decided here; a runtime table built at run time from names; a literal builtin call that bypasses the table; a padded call reaching a leaf; `malloc` for a registry; a deletion without its re-expression; a second lowerer; a `tree_t` field added for lower's convenience (CEO-1369); a comment or blank line.

## 6. WHERE THE REST LIVES

The three kinds of variance, the graph-fact registry and one form per box: skill `scrip-architecture` (reference § 2). The builtin table and its resolution at lower: skill `runtime-calls` § 3. The pruned tree per language: the language skill. What the planner reads from the graph and the carve per kind: skill `scrip-memory-model`. The bootstrap parsers' trees: skill `snocone-parser-patterns`.

## 7. HOW A LANDING IS PROVED

1. Reproduce on the one program: `monitor_run.sh --oracle`, `--dump-ast` (a wrong tree is the parser's row), `--dump-ir` beside a passing sibling.
2. Cure in a clean worktree: the case in `lower_<lang>.c`; a new kind in `ir_node.h` with its name in `scrip_ir.c` and its template; a new graph fact as a registry row first; a new builtin as a `builtins.tsv` row, the table regenerated before the build.
3. Prove: the DONE-WHEN red then green; the program in both modes; the boundary gates; feature reps; the smokes of every language touched; `util_reflow_200.py --check` and `strip_comments.py --check`.
4. Land named files, pull --rebase, re-prove, push; the coo re-grades by `s4e_test_request.sh`.
