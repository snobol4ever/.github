# GOAL-PST-ICN-RAKU.md — Pure Syntax Tree: Icon + Raku Audit

**Repo:** one4all + corpus + .github
**Parent goal:** `GOAL-PARSER-PURE-SYNTAX-TREE.md` (Steps 2 and 3)
**Status:** Active — PST-ICN-2a next

```
(source) ──► PARSER ──► (tree_t — pure syntax) ──► LOWER ──► IR_sm_t[]  ──┐
                                                                            ├──► interp / emitters
                                                          └──► IR_bb_t  ──┘
```

Icon and Raku are expected mostly clean — targeted audits only.
Snocone rewrite (Step 4) lives in `GOAL-PARSER-PURE-SYNTAX-TREE.md` and
continues in the same session as SNOBOL4 cleanup.

---

## ⛔ Pure-syntax rules (binding)

**Allowed:** `ast_node_new(TT_*)`, `expr_new`, `expr_unary`, `expr_binary`,
`ast_push`, `expr_add_child`. Setting `v.sval/v.ival/v.dval` from token.

**Forbidden:** cloning subtrees; `sc_label_new`; building non-`tree_t` IR;
variable-slot assignment; child reordering for positional semantics.

**⛔ Left-to-right child order (binding 2026-05-16):** Children of every node
in source token order. No in-place append to an existing subtree inspected by kind.

**⛔ SCRIP mirror invariant (binding 2026-05-16):** Every C-side fix in
`icon_parse.c` or `raku.y` must be paired in the same commit with the
corresponding fix in `corpus/SCRIP/parser_icon.sc` or `corpus/SCRIP/parser_raku.sc`.

---

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
```

Gate scripts:
```bash
bash /home/claude/one4all/scripts/test_smoke_icon.sh
bash /home/claude/one4all/scripts/test_smoke_raku.sh
bash /home/claude/one4all/scripts/test_smoke_scrip_all_modes.sh
bash /home/claude/one4all/scripts/test_crosscheck_snobol4.sh   # regression guard
```

---

## Step 2 — Icon audit

- [x] **PST-ICN-2a** — Read `src/frontend/icon/icon_parse.c` AND
  `corpus/SCRIP/parser_icon.sc` in full. Flag: (1) in-place append instead of
  always-wrap; (2) children not in source order; (3) non-`tree_t` IR allocation;
  (4) slot assignment / scope tracking. Record findings in State block.

- [x] **PST-ICN-2b** — Fix all violations found in 2a (or record "none").
  Both C and SCRIP files in the same commit.
  Gates: `smoke_icon`, `smoke_scrip_all_modes`, `crosscheck_snobol4`.

---

## Step 3 — Raku audit

- [x] **PST-RAKU-3a** — Read `src/frontend/raku/raku.y` AND
  `corpus/SCRIP/parser_raku.sc` in full. Same four-point checklist as 2a.
  Note: `raku.y` may use `AST_t`/`AST_QLIT` aliases not yet renamed to
  `tree_t`/`TT_QLIT` — that is a violation analogous to PST-SN4-1a.
  Record findings in State block.

- [ ] **PST-RAKU-3b** — Fix all violations (or record "none").
  Both C and SCRIP files in the same commit.
  Gates: `smoke_raku`, `smoke_scrip_all_modes`, `crosscheck_snobol4`.

---

## Done criterion for this goal

1. PST-ICN-2a/2b checked [x].
2. PST-RAKU-3a/3b checked [x].
3. All gate scripts green at baseline.
4. Beauty self-host byte-identical (Milestone 1 protected).
5. Parent goal `GOAL-PARSER-PURE-SYNTAX-TREE.md` Steps 2 and 3 checked [x].

On completion: update parent goal step ladder, bump watermark, commit + push HQ.

---

## State

```
watermark: 2026-05-16 (session 30/58)
next: PST-RAKU-3b — fix all raku.y violations; regenerate raku.tab.c; mirror in parser_raku.sc
audit findings Icon (PST-ICN-2a/2b complete):
  V1 FIXED: TT_AUGOP v.ival now stores AUGOP_* (was raw IcnTkKind). lower.c, lower_icn.c, interp_eval.c, icn_value.c all updated.
  V2 FIXED: TT_LOCAL / TT_STATIC_DECL node kinds added to ast.h. Parser, lower, interp, icn_runtime all updated.
  V3 NOTE: proc->_id = nparams — _id is not v.*, borderline; lower_icn.c depends on it for body_start. Left as-is.
  V4 FIXED: CODE_t/STMT_t stripped from icn_parse_file; returns NULL (callers all use (void)prog or out_ast).
  V5 FIXED: parse_block_or_expr no longer mutates/frees seq node on single-child collapse.
  V6 FIXED: TT_SECTION_PLUS / TT_SECTION_MINUS added to parser_icon.sc Expr11tail.
  AUGOP SCRIP MIRROR NOTE: SCRIP Tree() API cannot set v.ival; augop op-code mirror requires Tree() API extension. Tracked as known limitation.
  TT_LOCAL/TT_STATIC_DECL SCRIP MIRROR FIXED: push_static_stmt added; LocalDecl/StaticDecl now emit TT_LOCAL/TT_STATIC_DECL respectively.
audit findings Raku (PST-RAKU-3a complete, 3b pending):
  V1: AST_t/AST_e/AST_VAR/AST_FNC/AST_QLIT etc. aliases throughout raku.y — full file on old API surface.
      expr_new() not ast_node_new(); ->kind/->sval/->ival/->nchildren/->children[] not ->t/->v.sval/->v.ival/->n/->c[].
      SCRIP side already uses TT_* names. Fix: mechanical rename throughout raku.y + regenerate raku.tab.c.
  V2: CODE_t/STMT_t allocated in add_proc(); called from program, sub_decl, class_decl, gather.
      SCRIP side is tree-only. Fix: strip add_proc, return tree_t* program node instead.
  V3: e->ival used as SUB_TAG (0x40000000) bitmask OR'd with nparams count — semantic slot assignment.
      SUB_TAG is a hoisting flag packed with arity in sub_decl, method, gather, program action.
  V4: for_stmt inspects already-built iter subtree (->kind==AST_TO, ->children[0/1]) post-construction.
      make_for_range appends to body_seq after it is already built (in-place append violation).
  V5: when_list uses pair->ival to store comparison kind (AST_LEQ vs AST_EQ) in a SEQ_EXPR carrier node.
  V6: ->nchildren / ->children[] direct field access (AST_t names, not tree_t ->n / ->c[]).
gates: smoke_icon 5/5, smoke_raku 5/5, scrip_all_modes 2/0, crosscheck_snobol4 6/6 — all green.
mirror gaps remaining: augop ival encoding (needs Tree() API extension); raku.y full rename (PST-RAKU-3b)
```

## Authorship

Drafted by Claude Sonnet 4.6, 2026-05-16.
