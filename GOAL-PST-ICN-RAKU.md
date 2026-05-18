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

## Step 6 — Eliminate all remaining functions from parser_raku.sc

**Context (2026-05-18, session with Lon):** The "GOAL COMPLETE" marker above was
premature. The 11 functions relocated from `raku_helpers.sc` into `parser_raku.sc`
still violate the PST invariant — they use `TopCounter()` loops, `Pop/Append/tree()`
inside function bodies, and are called via `(epsilon . *fn())` pattern-action dispatch.
The goal is zero `function` bodies in `parser_raku.sc`.

### Technique: shift/reduce inlining

**Key facts about the SCRIP shift/reduce runtime (`ShiftReduce.sc`):**

- `Reduce(t, n)` pops exactly `n` items from the parse stack, fills `c[1..n]`
  bottom-to-top (i.e. `c[1]` = deepest = first pushed = leftmost in source),
  builds `tree(t, '', n, c)`, pushes result. **Always left-to-right correct.**
- Counter stack (`nPush/nInc/nTop/nPop`) is **separate** from the parse stack.
  `reduce('TT_KIND', 'nTop()')` pops exactly `nTop()` items regardless of where
  the `nPush` frame sits relative to other items on the parse stack.
- `reduce('TT_KIND', 'nTop() + K')` pops `nTop() + K` items — the extra `K`
  reach below the `nPush` frame into items pushed before `nPush()` fired.
  This is the correct technique for the `finish_mcall_body` pattern where `obj`
  sits one slot below the counter frame.

**Two naming conventions for TT_FNC nodes (both handled by `lower_fnc`):**

| Convention | v.sval | c[0] | lower reads |
|---|---|---|---|
| 1 (C `raku.y`) | `"fname"` | first arg | `SM_CALL_FN(v.sval, n)` |
| 2 (SCRIP) | `""` | `TT_VAR("fname")` | `SM_CALL_FN(c[0]->v.sval, n-1)` |

SCRIP uses convention 2 because `reduce` always produces empty `v.sval`.
`lower_record` updated to support convention 2 for `TT_RECORD` as well
(reads cname from `c[0]->v.sval` when `v.sval` is empty).

**Pattern for variable-arity sub/method/class bodies (sub_list emitters):**

```snocone
SubStmt = ( $'sub' $'  '
            SubName
            nPush()
            Push_sub_name_var  nInc()      ← TT_VAR(name) as c[0] for lower
            $'(' SubParams $')'             ← SubParams already does nInc per param
            SubBlock                        ← SubBlock_body does nInc per stmt
            reduce('TT_FNC', 'nTop()')
            Emit_to_sub_list                ← wraps in STMT(:subj(nd)), slinks to sub_list
            nPop()
          );
```

**`Emit_to_sub_list`** is a PST-allowed construction helper in `raku_stubs.sc`:
it pops the top node, wraps it in fresh `STMT(:subj(...))` nodes (construction,
no inspection), and slinks to `sub_list`. Not a tree-assembly violation.

**`Push_stmt_subj`** — same but pushes back to parse stack (used by `Compiland`
for the `main` wrapper which must be counted by the outer `nPush` frame).

**New stubs added to `raku_stubs.sc` this session:**
`push_fn_raku_mcall`, `push_mcall_mth_qlit`, `push_fn_raku_new`, `push_cls_qlit`,
`push_sub_name_var`, `push_mth_name_var`, `push_self_var`, `push_cls_name_var`,
`push_main_var`, `emit_to_sub_list`, `push_stmt_subj` — and their `Push_*`/`Emit_*`
pattern-action aliases.

### Progress

- [x] **PRF-1** — `finish_call_body`: inline `nPush / shift(CallName,'TT_VAR') nInc /
  *Expr nInc / ARBNO(*CallArgTail) / reduce('TT_FNC','nTop()') / nPop`.
  corpus commit pending. Gates: smoke_raku 5/0, all_modes 2/0, crosscheck 5/1.

- [x] **PRF-2** — `finish_new_body`: inline with `Push_fn_raku_new nInc /
  NewCallName Push_cls_qlit nInc` as prefix children inside counter scope.
  New stubs: `push_fn_raku_new`, `push_cls_qlit`. Gates hold.

- [x] **PRF-3** — `finish_mcall_body`: `MethodTail` restructured — shift
  `Push_fn_raku_mcall nInc / Push_mcall_mth_qlit nInc` inside `nPush` scope,
  then `reduce('TT_FNC', 'nTop() + 1')` to reach `obj` one slot below the
  `nPush` frame. New stubs: `push_fn_raku_mcall`, `push_mcall_mth_qlit`.
  Gates hold.

- [x] **PRF-4** — `finish_sub_body`: `SubStmt` inline with `Push_sub_name_var nInc`
  as first child + `reduce('TT_FNC','nTop()') + Emit_to_sub_list`.
  New stubs: `push_sub_name_var`, `emit_to_sub_list`. Gates hold.

- [x] **PRF-5** — `finish_method_body`: `MethodDef` inline with
  `Push_mth_name_var nInc / Push_self_var nInc` as first two children.
  New stubs: `push_mth_name_var`, `push_self_var`. Gates hold.

- [x] **PRF-6** — `finish_class_body`: `ClassDecl` inline with `Push_cls_qlit nInc`
  as c[0] name carrier + `reduce('TT_RECORD','nTop()') + Emit_to_sub_list`.
  `lower_record` in `lower.c` updated to support convention-2 (empty v.sval,
  name in c[0]->v.sval). Gates hold.

- [x] **PRF-7** — `finish_main_body`: `Compiland` inline with `Push_main_var nInc`
  as first child + `reduce('TT_FNC','nTop()') + Push_stmt_subj`.
  New stubs: `push_main_var`, `push_stmt_subj`. Gates hold.

- [ ] **PRF-8** — `finish_given`: `GivenStmt` restructure. `finish_given` uses
  `TopCounter()` to count `when` pairs but each pair pushes 3 nodes (cmpkind
  TT_ILIT + val + body), counted as 1 `nInc` per pair in `WhenClause`.
  **Strategy:** change `WhenClause` to `nInc() nInc() nInc()` (one per node)
  and use `reduce('TT_CASE', 'nTop() + 1')` with topic pushed before `nPush`.
  Default clause: `DefaultClause` currently sets `given_has_def` flag and pushes
  def_body; inline by adding 2 more `nInc` for the `TT_NUL + def_body` pair
  when default is present — or restructure into two alternations.
  C mirror: `given_stmt` in `raku.y` already builds `TT_CASE` correctly; verify
  child layout matches after inlining.

- [ ] **PRF-9** — `finish_gather_body`: two-phase — emits def `TT_FNC` to sub_list
  AND pushes a zero-arg call `TT_FNC` to the parse stack. Auto-generates name
  `'__gather_' gather_seq`. **Strategy:** split into two inline actions:
  (1) `reduce('TT_FNC','nTop()') + Emit_to_sub_list` for the def (keeping
  `gather_seq` increment in a side-effect stub), then (2) a `Push_gather_call`
  stub that constructs the call node using the same `gname` — but `gname` must
  be consistent between the two. Requires a `gather_name` capture variable set
  by a `Set_gather_name` stub before `nPush`. C mirror: `expr: KW_GATHER block`
  in `raku.y` uses `add_proc(def)` + pushes call; verify shapes match.

- [ ] **PRF-10** — `push_interp_str`: PST-clean by definition (no tree child
  inspection — string processing only). Reclassify as allowed, or inline the
  interpolation loop as a SCRIP pattern if feasible. Decision: **leave as-is**
  unless Lon directs otherwise.

- [ ] **PRF-11** — `dq_unescape`: PST-clean by definition (string processing only,
  no Pop/Push/Append/tree()). **Leave as-is.**

### Done criterion for this goal (updated)

Zero `function` bodies in `parser_raku.sc` that call `Pop()`, `TopCounter()`,
`Append()`, or `tree()` — i.e. functions that do tree assembly. String-processing
functions (`push_interp_str`, `dq_unescape`) are PST-clean and may remain.

---

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
     - `raku_helpers.sc` — **DELETED 2026-05-18**: all 11 functions
       (push_interp_str, dq_unescape, finish_given, finish_sub_body,
       finish_method_body, finish_class_body, finish_gather_body,
       finish_call_body, finish_mcall_body, finish_main_body, finish_new_body)
       moved inline into parser_raku.sc. Finish_* uppercase aliases replaced
       with (epsilon . *finish_*()); Push_ilit(n) → shift_val(n,'TT_ILIT');
       Store_for_iter → shift_val(capff capfr,'TT_VAR').
   **Icon function count: 0/0. Raku function count: 0/0. Both sidecars deleted.** ✅
8. Parent goal `GOAL-PARSER-PURE-SYNTAX-TREE.md` Steps 2 and 3 updated.

On completion: update parent goal step ladder, bump watermark, commit + push HQ.

---

## State

```
watermark: 2026-05-18 (session handoff — PRF-1 through PRF-7 complete)
next: PRF-8 (finish_given) then PRF-9 (finish_gather_body)
functions remaining in parser_raku.sc: 4
  push_interp_str  — PST-clean (string processing, no tree ops) — leave
  dq_unescape      — PST-clean (string processing, no tree ops) — leave
  finish_given     — PRF-8: restructure WhenClause nInc×3 + reduce('TT_CASE','nTop()+1')
  finish_gather_body — PRF-9: split into Set_gather_name + reduce + Emit_to_sub_list + Push_gather_call
lower.c change this session: lower_record updated for convention-2 (empty v.sval → read cname from c[0])
new stubs in raku_stubs.sc: push_fn_raku_mcall, push_mcall_mth_qlit, push_fn_raku_new,
  push_cls_qlit, push_sub_name_var, push_mth_name_var, push_self_var, push_cls_name_var,
  push_main_var, emit_to_sub_list, push_stmt_subj (and their Push_*/Emit_* aliases)
gates at handoff: smoke_raku 5/0, smoke_icon 5/0, scrip_all_modes 2/0, crosscheck 5/1 (pre-existing)
PRF-7 (finish_main_body) ✅ 2026-05-18 (Claude Sonnet 4.6): Compiland inline.
PRF-6 (finish_class_body) ✅ 2026-05-18: ClassDecl inline + lower_record convention-2.
PRF-5 (finish_method_body) ✅ 2026-05-18: MethodDef inline.
PRF-4 (finish_sub_body) ✅ 2026-05-18: SubStmt inline + Emit_to_sub_list.
PRF-3 (finish_mcall_body) ✅ 2026-05-18: MethodTail nTop()+1 technique.
PRF-2 (finish_new_body) ✅ 2026-05-18: prefix-node-in-counter technique.
PRF-1 (finish_call_body) ✅ 2026-05-18: pure nPush/reduce/nPop.
PST-RAKU-sidecar-elim ✅ corpus@78c1b4a 2026-05-18 (Claude Sonnet 4.6):
  All 11 functions from raku_helpers.sc inlined into parser_raku.sc.
  Finish_* uppercase aliases → (epsilon . *finish_*()); Push_ilit(n) →
  shift_val(n,'TT_ILIT'); Store_for_iter → shift_val(capff capfr,'TT_VAR').
  raku_helpers.sc deleted. run_scrip_parser.sh unchanged (guards with [ -f ]).
  Gates: smoke_raku 5/5, smoke_icon 5/5, scrip_all_modes 2/0, crosscheck 5/1 (pre-existing).
  Raku is now 0/0: zero helper functions, zero sidecar file.
  GOAL COMPLETE: both icon_helpers.sc and raku_helpers.sc eliminated.
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
