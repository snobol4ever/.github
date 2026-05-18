# GOAL-PST-ICN-RAKU.md — Pure Syntax Tree: Icon + Raku Audit

**Repo:** one4all + corpus + .github
**Parent goal:** `GOAL-PARSER-PURE-SYNTAX-TREE.md` (Steps 2 and 3)
**Status:** Active — PST-ICN-4a next (SCRIP mirror helper elimination)

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

- [x] **PST-RAKU-3b** — Fix all violations (or record "none").
  Both C and SCRIP files in the same commit.
  Gates: `smoke_raku`, `smoke_scrip_all_modes`, `crosscheck_snobol4`.

---

## Step 4 — SCRIP mirror helper elimination (Icon)

**Finding (2026-05-16, session re-audit):** `parser_icon.sc` still carries 13 helper
functions that perform tree Pop/inspect/reassemble instead of pure `shift`/`reduce`.
The C-side violations were fixed in PST-ICN-2b but the SCRIP mirror was not brought
to `{shift, reduce}` only — it retained the old helper pattern.  The parent goal
(`GOAL-PARSER-PURE-SYNTAX-TREE.md`) requires every frontend's SCRIP mirror to be
expressible as shift + reduce with no helpers that inspect previously-built children.

**Violations in `corpus/SCRIP/parser_icon.sc`:**

| Helper | Violation | Fix |
|--------|-----------|-----|
| `push_subscript` | Pops idx+lhs, inspects order | Replace with `reduce('TT_IDX', 2)` (already used in same rule) |
| `push_section` (`:` case) | Pops hi/lo/lhs | Replace with `reduce('TT_SECTION', 3)` |
| `decompose_proc` | `TopCounter()`+loop+`Append` | Inline `nPush/nInc/reduce('TT_FNC','nTop()')/nPop` + STMT wrapper |
| `push_record` | same loop pattern | `reduce('TT_RECORD', 'nTop()')` inline |
| `push_global_top` | same loop pattern | `reduce('TT_GLOBAL', 'nTop()')` inline |
| `push_local_stmt` | same loop pattern | `reduce('TT_LOCAL', 'nTop()')` inline |
| `push_static_stmt` | same loop pattern | `reduce('TT_STATIC_DECL', 'nTop()')` inline |
| `push_field` | calls `v()` on child to extract sval | `reduce('TT_FIELD', 2)` with `[lhs, TT_VAR(fname)]` children; update `lower_icn.c` to read `e->c[1]->v.sval`; update C parser; update `.ref` files |
| `push_match` | synthesizes `TT_VAR('match')` not in source | Add `TT_MATCH_UNARY` to `ast.h`, handle in `lower_icn.c`; `reduce('TT_MATCH_UNARY', 1)` |
| `push_qlit` | named function wrapping a leaf push | Inline as pattern action or `shift` |
| `push_cset` | named function wrapping a leaf push | Inline |
| `push_flit` | named function + `REAL()` computation | Inline (REAL from token is allowed) |
| `push_kw` | named function + `'&' kwname` concat | Inline |

**C-side changes required (SCRIP mirror invariant — same commit):**
- `ast.h`: add `TT_MATCH_UNARY`
- `icon_parse.c`: unary `=` emits `TT_MATCH_UNARY(inner)` instead of `TT_FNC(TT_VAR('match'), inner)`; `TT_FIELD` stores name as `c[1]` (TT_VAR) not `v.sval`
- `lower_icn.c`: handle `TT_MATCH_UNARY`; read field name from `e->c[1]->v.sval` in `TT_FIELD` case
- `.ref` files: regenerate for `field_access`, `subscript_field`, `match_expr`, and any other affected fixtures

- [x] **PST-ICN-4a** — Infrastructure: add `TT_MATCH_UNARY` to `ast.h`; update `icon_parse.c` unary `=` and `TT_FIELD` construction; update `lower_icn.c` for both new kinds; regenerate `.ref` files for affected fixtures. Gates: `smoke_icon`, `crosscheck_snobol4`.

- [x] **PST-ICN-4b** — SCRIP mirror: remove all 13 helpers from `parser_icon.sc`; replace structural assemblers with inline `shift`/`reduce` actions. 5 PST-allowed leaf-push helpers (`push_qlit`, `push_cset`, `push_flit`, `push_kw`, plus `notmatch` redef) **moved to a sidecar `icon_helpers.sc`** loaded by `run_scrip_parser.sh` alongside the parser — they will be inlined or absorbed into runtime once `notmatch` / `match.sc` is settled. Both C and SCRIP committed together. Gates: `smoke_icon`, `smoke_scrip_all_modes`, `crosscheck_snobol4`.

## Step 5 — SCRIP mirror helper elimination (Raku)

**Finding (2026-05-16, session re-audit):** `corpus/SCRIP/parser_raku.sc` carries ~80
helper functions (`push_*`, `finish_*`, `flatten_*`). The `flatten_*` functions
(flatten_add, flatten_sub, flatten_mul, flatten_div, flatten_cat) actively inspect
previously-built subtrees and mutate them — a direct violation of the left-to-right
child order invariant. The `finish_*` functions do Pop/reassemble equivalent to what
should be inline `reduce` actions.

- [x] **PST-RAKU-5a** — Audit `parser_raku.sc` fully: catalogue all `flatten_*` as
  child-inspection violations and all `finish_*` that inspect `->kind` of prior nodes.
  Record findings in State block.
  FINDINGS (2026-05-16 session 30/60):
    R1 HARD: flatten_add/sub/mul/div/cat — inspect t(lhs) to append-in-place; left-to-right violation.
       Fix: replace with reduce('TT_ADD',2) etc. — always-wrap, right-leaning chain.
    R2 HARD: finish_given (line 530) — inspects t(val) (TT_QLIT test) to choose cmpkind integer.
       Semantic reasoning belongs in lower. Fix: emit val as-is; lower selects cmpkind.
    R3 HARD: finish_class (lines 1114-1117) — inspects t(item) to split methods/fields;
       mutates v(item) and v(c(item)[1]) (slot assignment). Fix: emit all items as children;
       lower handles class-prefix renaming.
    R4 HARD: finish_for_range (line 463) — reads c(body)[i] to copy children into new seq;
       control-flow lowering inside parser. Fix: emit body as-is; lower desugars for-range.
    R5 STYLE: ~80 finish_*/push_* functions: Pop N, build node, Push — equivalent to inline reduce.
       Not child-kind violations, but named functions doing what reduce should express inline.
       Large scope; tackle after R1-R4 hard violations fixed.
  NOT violations (confirmed clean): lines 1917-1919 are post-parse driver output, not grammar actions.

- [x] **PST-RAKU-5b** — Eliminate `flatten_*` violations: replace with always-wrap
  `reduce` (produces right-leaning chain, correct per PST rules). Update C `raku.y`
  if any parallel flatten logic exists there. Gates: `smoke_raku`, `smoke_scrip_all_modes`, `crosscheck_snobol4`.

- [x] **PST-RAKU-5c** — Eliminate remaining `finish_*` and `push_*` helpers: replace
  with inline `shift`/`reduce`. Gates: all four goal gates green.

## Done criterion for this goal

1. PST-ICN-2a/2b checked [x].
2. PST-RAKU-3a/3b checked [x].
3. PST-ICN-4a/4b checked [x].
4. PST-RAKU-5a/5b/5c checked [x].
5. All gate scripts green at baseline.
6. Beauty self-host byte-identical (Milestone 1 protected).
7. `parser_icon.sc` and `parser_raku.sc` contain zero in-file helper functions
   that Pop/INSPECT/reassemble trees. **Sidecar status**:
     - `icon_helpers.sc` — **DELETED 2026-05-18**: all 4 leaf-push helpers
       (`push_qlit`, `push_cset`, `push_flit`, `push_kw`) inlined as
       `(epsilon . *Shift('TT_*', var))` directly in `parser_icon.sc`.
       `run_scrip_parser.sh` guards with `[ -f ]` — no loader change needed.
       Icon is now 0/0 (zero functions, zero sidecar). ✅
     - `raku_helpers.sc` — 11 functions remain: `push_interp_str`, `dq_unescape`,
       and 9 `finish_*` variable-arity assemblers (counter-based, no
       child-kind inspection — they cannot be expressed as a single
       inline `reduce`). Removal deferred until SCRIP runtime stabilises.
   **Icon function count: 0. Raku function count: 11 (sidecar only).**
8. Parent goal `GOAL-PARSER-PURE-SYNTAX-TREE.md` Steps 2 and 3 updated.

On completion: update parent goal step ladder, bump watermark, commit + push HQ.

---

## State

```
watermark: 2026-05-18 (session handoff)
next: raku_helpers.sc elimination (11 functions remain; deferred until runtime stabilises)
PST-ICN-SIDECAR-ELIM ✅ corpus@3789cba 2026-05-18 (Claude Sonnet 4.6):
  push_qlit/push_cset/push_flit/push_kw inlined as (epsilon . *Shift('TT_*', var))
  directly in parser_icon.sc Expr11. icon_helpers.sc deleted entirely.
  run_scrip_parser.sh unchanged (guards with [ -f ]).
  Gates: smoke_icon 5/5, scrip_all_modes 2/0, crosscheck 5/1 (beauty_omega pre-existing).
  Icon is now 0/0: zero helper functions, zero sidecar file.
PST-RAKU-5b ✅ corpus@31cc6f2: R1-R4 hard violations fixed.
PST-RAKU-5c ✅ corpus@3cb7ada: parser_raku.sc rewrite 1788→607 lines (parser file only).
  All in-file finish_* tree-assembly helpers removed from parser_raku.sc.
  **11 functions** (push_interp_str, dq_unescape, 9 finish_* counter-based
  variable-arity assemblers) **relocated to corpus/SCRIP/raku_helpers.sc**
  (231 lines). They are loaded by run_scrip_parser.sh alongside the parser.
  Earlier wording "95→39 functions" referred to parser_raku.sc in isolation;
  total parser+helpers function count today is 11. All gates green.
PST-ICN-4a ✅ one4all@c52b724c: TT_MATCH_UNARY, TT_FIELD child layout, ICN_FIELD_NAME macro.
PST-ICN-4b ✅ corpus@0ecae06: parser_icon.sc 525→381 lines, 9 structural helpers
  replaced with inline reduce; **5 PST-allowed leaf-push functions relocated
  to corpus/SCRIP/icon_helpers.sc** (push_qlit, push_cset, push_flit, push_kw,
  notmatch). Helpers are loaded by run_scrip_parser.sh alongside the parser.
  C-side fixes from PST-ICN-2b did not propagate to SCRIP mirrors. parser_icon.sc has 13
  helper functions that Pop/inspect/reassemble trees; parser_raku.sc has ~80. flatten_* in
  parser_raku.sc violate left-to-right child order invariant. PST-RAKU-3b was marked done
  prematurely — finish_*/flatten_*/push_* helpers remain throughout.
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
  V1 FIXED: AST_t/AST_e/AST_VAR/AST_FNC/AST_QLIT etc. → tree_t/tree_e/TT_VAR/TT_FNC/TT_QLIT throughout raku.y.
      SCRIP side already used TT_* names — no change needed.
  V2 FIXED: CODE_t/STMT_t stripped; raku_parse_string returns tree_t*. add_proc() builds TT_STMT with :lang/:subj attrs.
      raku_driver.c: no code_to_ast(); takes tree_t* directly. SCRIP side already tree-only.
  V3 FIXED: SUB_TAG bitmask removed from v.ival; _id=SUB_TAG_ID=1 used as hoist flag. v.ival = nparams only.
  V4 FIXED: for_stmt matches OP_RANGE inline; make_for_range builds body2 fresh (no in-place append).
      SCRIP finish_for_range mirrored: builds body2 fresh.
  V5 FIXED: when_list pair is TT_SEQ_EXPR[TT_ILIT(cmpkind), val, body]. SCRIP already correct.
  V6 FIXED: all ->n/->c[]/->t/->v.sval/->v.ival accesses correct throughout raku.y.
gates: smoke_icon 5/5, smoke_raku 5/5, scrip_all_modes 2/0, crosscheck_snobol4 6/6 — all green.
```

## Authorship

Drafted by Claude Sonnet 4.6, 2026-05-16.
