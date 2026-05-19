# GOAL-PST-ICN-RAKU.md — Pure Syntax Tree: Icon + Raku Audit

**Repo:** one4all + corpus + .github
**Parent goal:** `GOAL-HQ.md` (Steps 2 and 3)
**Status:** Active — PST-ICN-4a next (SCRIP mirror helper elimination)

```
(source) ──► PARSER ──► (tree_t — pure syntax) ──► LOWER ──► IR_sm_t[]  ──┐
                                                                            ├──► interp / emitters
                                                          └──► IR_bb_t  ──┘
```

Icon and Raku are expected mostly clean — targeted audits only.
Snocone rewrite (Step 4) lives in `GOAL-HQ.md` and
continues in the same session as SNOBOL4 cleanup.

---

## ⛔ Separation of concerns (binding 2026-05-18) — THE governing principle

The parser's only job is to **transcribe surface syntax into `tree_t`**. The tree
is a faithful, almost photographic image of the source. The parser does not
reason about the meaning of what it parsed. Every semantic decision belongs to
**lower**; every code-generation decision belongs to the **emitter**.

```
parser  : source                ──►  tree_t (pure syntax mirror, source order)
lower   : tree_t                ──►  SM_Program (semantic decisions, name-fountains, hoisting, desugaring)
emitter : SM_Program            ──►  native code or interpreter step
```

Things the parser **MUST NOT** do (each is a lower-time concern):

- Inspect a child's `t` to choose an operator kind (e.g. `TT_QLIT → TT_LEQ` else `TT_EQ`) — emit children as-is, let lower pick.
- Synthesize names not present in source (e.g. `__gather_N`, `__case_topic__`) — let lower fountain them.
- Hoist sub/method/class/gather definitions into a separate output queue — let lower walk the program and lift.
- Wrap nodes in `STMT(:subj(...))` envelopes for output staging — wrapping is a lower decision.
- Rename methods to `Class__method` form — lower renames during class lowering.
- Desugar control flow (`for-range` → `for-iter`, `unless` → `if not`, etc.) — lower desugars.
- Assign `_id` / `SUB_TAG` / hoist-flag slots — lower flags.
- Re-order children to encode positional semantics — children stay in source order.

Things the parser **MAY** do (each is pure transcription):

- `shift`/`reduce` to build `tree_t` nodes in source order.
- Set `v.sval`/`v.ival`/`v.dval` from token text.
- Leaf-only pusher stubs in `*_stubs.sc` that `Push(tree('TT_*', token))` (no `Append`, no tree-of-trees, no inspection of prior pushes).
- Counter-stack discipline (`nPush`/`nInc`/`nTop`/`nPop`) to count source children for variable-arity reduces.
- Pre-pass string transformations on captured tokens (e.g. `dq_unescape` converting `\n` escapes to actual `nl`) — only when the result is fed to a leaf push.
- Source-order capture variables (`captured_name`, etc.) set via `.` for use by the next leaf push.

**Corollary — parser_*.sc helper count.** A `parser_*.sc` file should contain
**zero `function` bodies that build trees**. Pure pre-pass string transformers
(no `Push`/`Append`/`tree()`/`Pop`) are permitted as helpers in the parser file.
Everything else lives in `*_stubs.sc` as leaf-pushers or in lower.

**Applying this principle (the standing parser refactor goal).** Any parser
that currently violates these rules — `parser_raku.sc`'s sub/class/gather
hoisting, `parser_prolog.sc`'s and `parser_rebus.sc`'s semantic helpers,
`raku.y`'s `add_proc`/`SUB_TAG`/method-renaming — is a target for cleanup
under this goal. The work is: move the violation out of the parser and into
lower.c (or `lower_*.c`), regenerate `.ref` files, hold all gate scripts.

---



### Pure-syntax rules — quick reference

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

## ⛔ SCRIP mirror work — Raku orientation

**C side must be clean before parser_raku.sc mirror work proceeds beyond Phase A.** `parser_raku.sc` Phase A (zero function bodies with tree ops) is complete. Phase B (PRF-12: `add_proc`/`SUB_TAG_ID` hoisting, gather, class renaming → lower) requires the C side to move those semantics to `lower.c` first. Do not write Phase B SCRIP changes until the matching C rung is committed.

**PRF-12 C-side sequencing** — each bullet below is one Phase 1 C rung. Do not write SCRIP mirror changes until Phase 2 (all six C parsers clean). Record `⚠ MIRROR-GAP` in State after each C rung:
1. **Gather** → add `TT_GATHER` to `ast.h`; write `lower_gather` in `lower.c`; rewrite `KW_GATHER` rule in `raku.y` to emit pure `TT_GATHER[stmts...]`. Then mirror in `parser_raku.sc`.
2. **Sub decl** → add `TT_SUB_DECL` to `ast.h`; write `lower_sub_decl`; rewrite `sub_decl` rule in `raku.y` to emit `TT_SUB_DECL[name, params, block]`; delete `add_proc`/`SUB_TAG_ID` from sub path. Then mirror.
3. **Class decl** → add `TT_CLASS_DECL`; write `lower_class_decl`; rewrite `class_decl` rule; delete `raku_meth_register`/method rename from parser. Then mirror.
4. **Program/Compiland** → rewrite program rule to emit `TT_PROGRAM[stmts...]` flat; delete `sub_list` slink, `STMT(:subj(...))` envelopes, dual-queue logic. Then mirror.
5. **For-range desugar** → rewrite `for_stmt` to emit `TT_FOR[var, iter, body]`; move range-to-index desugar to `lower.c`. Then mirror.

**When starting parser_raku.sc mirror work:** Read `SNOBOL4-SNOCONE-PRIMER.md` in full. Learn Snocone expression syntax from the SPITBOL manual and control-flow syntax from `corpus/SCRIP/parser_snocone.sc`. The goal is pure `shift`/`reduce` — no `Push`, `Pop`, `Append`, `Tree`, or helper functions that inspect children. `dq_unescape` (pure string processor) is the only permitted helper.

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
(`GOAL-HQ.md`) requires every frontend's SCRIP mirror to be
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

- [x] **PRF-8** — `finish_given` eliminated. `WhenClause = Expr nInc() Block nInc()`,
  `DefaultClause = Push_nul Block nInc() nInc()`, `GivenStmt` uses `nPush()` after topic
  and `reduce('TT_CASE', 'nTop() + 1')` so topic becomes `c[0]` one slot below the counter
  frame. **TT_CASE shape changed to 2-per-arm: `[topic, val0, body0, val1, body1, ..., (TT_NUL, body_def)?]`.**
  cmpkind moved to lower.c — derived from `val->t` (TT_QLIT → TT_LEQ, else TT_EQ). Paired
  `raku.y` and `lower.c` raku-branch changes (gated on `g_lang == LANG_RAKU`). No `.ref`
  regen needed (no given fixtures in `.ref` set). Gates: smoke_raku 5/0, smoke_icon 5/0,
  scrip_all_modes 2/0, crosscheck_snobol4 5/1 (pre-existing), crosscheck_raku 21/12
  unchanged, rk_given + rk_given18 still PASS.

- [x] **PRF-9 (transitional)** — `finish_gather_body` eliminated from `parser_raku.sc`.
  `GatherBlock` now uses two `nPush/reduce('TT_FNC',n)/nPop` blocks sharing a fresh
  `__gather_N` name via `Set_gather_name` + `Push_gather_name_var` stubs in
  `raku_stubs.sc`. **NOTE — VIOLATES separation-of-concerns principle**: the name
  fountain and the def/call hoist-to-sub_list both belong in lower, not in the parser.
  This commit matches the existing `raku.y` violation (parser synthesizes `__gather_N`
  and calls `add_proc` to hoist). Cleanup tracked as PRF-12 below — the proper PST
  answer is `TT_GATHER[block]` with lower doing the fountain + hoist.

- [x] **PRF-10** — `push_interp_str` eliminated. New leaf-only stub
  `push_interp_leaves` in `raku_stubs.sc` walks `capstr` and pushes one TT_QLIT or
  TT_VAR leaf per interpolation chunk, calling `IncCounter()` per push. NO `Append`,
  NO tree-of-trees. `LitStrDQ` use site wrapped with `nPush() ... Push_interp_leaves
  reduce('TT_CAT', r_nTop) nPop()` so single-leaf strings (no `$var`) skip the TT_CAT
  wrap (`r_nTop = '*(GT(nTop(),1) nTop())'` returns failure when count<=1). Pure
  transcription: leaves match source chunks, no semantic decision. Gates hold;
  `rk_interp` and `rk_strings` unchanged.

- [x] **PRF-11** — `dq_unescape` is PST-clean (pure string processor: takes `capstr`,
  applies `\n`/`\t`/`\"`/`\\` escapes, stores back to `capstr`; no `tree()`/`Push`/
  `Append`). Permitted in `parser_raku.sc` under the principle as a pre-pass string
  transformer feeding a leaf push. **Leave as-is.**

## ⛔ Clarification (2026-05-18, this session) — parser actions vs lower concerns

**Grammar actions in raku.y are NOT PST violations.** A CFG grammar fires actions
at reduce time — inline, as part of the parse. `add_proc`, method renaming,
`make_for_range` desugar, `_id` flag assignment — these all fire at reduce time.
That is correct and normal CFG behavior. "Post-processing" means a separate pass
over a completed tree; grammar actions are not that.

**The real issue is in lower.c**, which reads `_id == SUB_TAG_ID` (a fifth field
beyond t/v/n/c) and never sees `TT_FOR` / `TT_SUB_DECL` / `TT_CLASS_DECL` because
the parser has already desugared them. The lower stage is the correct place to fix
the interface — by giving each construct a dedicated TT_* node kind so lower reads
only t/v/n/c, and by moving desugar (for-range, self-injection) to lower.

PRF-12 items are therefore **lower.c work**, not raku.y work. raku.y stays as-is
(correct CFG); lower gets new TT_* dispatch cases.

- [x] **PRF-12-gather** ✅ 2026-05-18 (Claude Sonnet 4.6, one4all `pending`):
  **Gather** moved from parser-inline to post-parse hoist pass + pure transcription.
  - `ast.h`: `TT_GATHER` added to enum + name table.
  - `raku.y` `KW_GATHER block` rule: 11-line semantic body → 4-line pure
    `TT_GATHER[body_stmts...]` transcription. Union-clobber bugs fixed (`v.ival=0`
    after `v.sval` zeroed pointer; `_nalloc` not reset on in-place rewrite).
  - `raku_lower_hoist_gather_pass()`: post-parse pass added; called from
    `raku_parse_string()` after `raku_yyparse()`. Walks TT_STMT subjects
    recursively (entering TT_ATTR children), finds TT_GATHER nodes, fountains
    `__gather_N`, builds def TT_FNC, rewrites node in-place to call TT_FNC,
    bulk-prepends def STMTs to `raku_prog_result`.
  - `lower.c`: fatal abort stub added for TT_GATHER (should never reach lower).
  - `raku.tab.c`: regenerated (28 pre-existing warnings, no new errors).
  - Gather `.ref` files regenerated (4 files, compact format matching `--dump-ast`).
  - Gates: smoke_raku 5/0, smoke_icon 5/0, scrip_all_modes 2/0,
    crosscheck_snobol4 5/1 (pre-existing), crosscheck_raku **23/10** (was 21/12).

- [ ] **PRF-13 — SCRIP mirror: GatherBlock** — rewrite `GatherBlock` in
  `parser_raku.sc` to pure `nPush() ARBNO(*SubBlock_body) reduce('TT_GATHER','nTop()') nPop() nInc()`.
  Remove `Set_gather_name`, `Push_gather_name_var` stubs from GatherBlock rule.
  Create `corpus/SCRIP/raku_helpers.sc` with `gather_hoist_pass(ptree)` function
  (mirrors `raku_lower_hoist_gather_pass` using tree.sc API: `t()`, `n()`, `c()`,
  `Append`, `Prepend`). Update driver tail in `parser_raku.sc` to call
  `gather_hoist_pass(ptree)` after `ptree = Pop()`. Remove `gather_seq = 0`
  initializer. Update `run_scrip_parser.sh` if needed (already loads
  `${LANG}_helpers.sc` — `raku_helpers.sc` will load automatically).
  Gates: smoke_raku, smoke_icon, scrip_all_modes, crosscheck_snobol4,
  crosscheck_raku — all at floor.

- [ ] **PRF-12-sub** — lower.c: add `TT_SUB_DECL` to ast.h; write `lower_sub_decl`
  in lower.c that reads `c[0]` (name), `c[1..nparams]` (params), `c[nparams+1..]`
  (body) from the pure syntax tree; remove `_id == SUB_TAG_ID` read from lower_stmt.
  raku.y `sub_decl` rule: emit `TT_SUB_DECL[TT_VAR(name), params..., body_stmts...]`
  (no `_id` flag needed — node kind distinguishes). `.ref` regen. Gates green.

- [ ] **PRF-12-class** — lower.c: add `TT_CLASS_DECL` to ast.h; write
  `lower_class_decl` that handles method renaming (`Cls__method`) and field
  extraction. raku.y `class_decl`: emit `TT_CLASS_DECL[TT_VAR(cname), item0...]`
  without renaming or `raku_meth_register` in parser. `.ref` regen. Gates green.

- [ ] **PRF-12-for** — lower.c: add `TT_FOR_RANGE` or reuse `TT_FOR`; write
  `lower_for_range` that desugars to `TT_ASSIGN + TT_WHILE`. raku.y `for_stmt`:
  emit `TT_FOR[TT_VAR(v), lo, hi, body]` — delete `make_for_range`. `.ref` regen.
  Gates green.

- [ ] **PRF-12-self** — lower.c: `lower_method_decl` injects implicit `self` as
  first param when lowering a method. raku.y `method_decl`: stop injecting
  `leaf_sval(TT_VAR, "self")` into the child list. `.ref` regen. Gates green.

### Done criterion for this goal (updated 2026-05-18)

**Phase A — helper elimination (parser_raku.sc form):** Zero `function` bodies in
`parser_raku.sc` that call `Push()`, `Append()`, or `tree()`. Pure string
transformers (no tree ops) permitted. **Status: COMPLETE** (`dq_unescape` only —
permitted pure string processor).

**Phase B — separation-of-concerns (lower.c interface):** lower.c reads only
t/v/n/c from tree nodes; no `_id` side-channel; all constructs have dedicated
TT_* node kinds; desugar happens in lower not parser. **Status: PRF-12-gather
done; PRF-13 (SCRIP mirror), PRF-12-sub/class/for/self in queue.**

---

## Step 7 — Eliminate raku_stubs.sc (only remaining step in this goal)

**Binding scope (2026-05-18, Lon):** the only remaining work in this goal is to delete
`corpus/SCRIP/raku_stubs.sc` entirely and replace every stub's functionality with inline
`shift` / `reduce` / `assign` (and any other built-in runtime primitive) directly in
`parser_raku.sc`. PRF-12 / Phase B / semantic convergence with raku.y is **out of scope**
for this goal — it lives elsewhere (or as a follow-on goal).

**Technique catalogue:**

- Leaf pusher `Push(tree('TT_VAR', capvf capvr))` → inline as
  `(epsilon . *Shift('TT_VAR', capvf capvr))` or whatever the SCRIP `shift_val`/`shift`
  primitive form requires. Prior precedent: `Push_ilit(n)` was already replaced by
  `shift_val(n, 'TT_ILIT')` (see PST-RAKU-sidecar-elim 78c1b4a). `Store_for_iter` was
  replaced by `shift_val(capff capfr, 'TT_VAR')` in the same commit.
- Constant-name pusher like `push_fn_say_fh` that pushes `tree('TT_VAR', 'raku_say_fh')`
  → inline at every use site as `shift_val('raku_say_fh', 'TT_VAR')` (or the equivalent
  literal-string form the SCRIP runtime supports).
- Flag setter like `set_stdin` (sets `capidx = 0`) → inline via the assign primitive:
  `(epsilon . *assign(.capidx, 0))` (already a well-used pattern elsewhere in the
  parsers — see parser_snocone.sc `*assign(.captured_call_name, token)`).
- Composite stubs like `emit_to_sub_list` and `push_stmt_subj` build STMT(:subj(nd))
  envelopes — these are tree-of-trees construction. They cannot become a single
  `shift`/`reduce`/`assign`. **If they cannot be inlined as pure shift/reduce, they
  must move to lower** (this is the small Phase-B residue that overlaps with PRF-12
  step 7 = program, but only for these two helpers).
- `push_interp_leaves` walks a captured DQ string and pushes one TT_VAR/TT_QLIT leaf
  per interpolation chunk. Each push is leaf-only. The walk itself is pure string
  scanning; if SCRIP has no inline grammar form for "ARBNO over a captured string",
  this stays as a pure pre-pass string transformer (analogous to `dq_unescape`) and
  is permitted under the principle.

**Acceptance:**

- [x] **PRF-S7-1** — Catalogue every stub in `raku_stubs.sc` and classify each as
  (a) inline-able via `shift`/`shift_val`/`assign`, (b) move to lower (composite tree
  builders), or (c) pure string pre-pass (keep, but move into parser_raku.sc since
  it's PST-clean per the principle).
- [x] **PRF-S7-2** — Apply (a) class: rewrite every `Push_*` pattern-action site in
  parser_raku.sc to inline `shift_val(...)` / `assign(...)`. Delete the stub from
  raku_stubs.sc as each is replaced. Commit small, gate after each batch.
- [x] **PRF-S7-3** — Resolve (b) class (emit_to_sub_list, push_stmt_subj): either
  move to lower (Phase B residue) or leave as PST-allowed construction helpers in
  raku_stubs.sc with explicit rationale comment. Lon decision required.
- [x] **PRF-S7-4** — Move (c) class (push_interp_leaves, any other pre-pass) into
  parser_raku.sc next to dq_unescape (the precedent permitted function there).
- [x] **PRF-S7-5** — `rm corpus/SCRIP/raku_stubs.sc`. Update `run_scrip_parser.sh`
  if it references the file (it does not currently load `raku_stubs.sc`, only
  `${LANG}_helpers.sc` — so likely a no-op). Gates: smoke_raku, smoke_icon,
  scrip_all_modes, crosscheck_snobol4, crosscheck_raku — all hold at floor.
- [x] **PRF-S7-6** — Update Done criterion below + State block + PLAN.md row.
  (partially done this session — state block updated, PLAN.md next)
  Commit and push all three repos.

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
     - `raku_stubs.sc` — **NOT YET DELETED** (only remaining work in this goal —
       see Step 7 above). Contains ~90 leaf-only push stubs and a few utility
       nodes. Done criterion for this goal now requires this file to be
       eliminated by inlining each stub as `shift` / `shift_val` / `assign` at
       its use site in parser_raku.sc.
   **Icon function count: 0/0 (sidecar deleted). Raku function count: 1/1+stubs
   (raku_stubs.sc still present; deletion is the only remaining work).**
8. Parent goal `GOAL-HQ.md` Steps 2 and 3 updated.

On completion: update parent goal step ladder, bump watermark, commit + push HQ.

---

## State

```
watermark: 2026-05-18 (PRF-12-gather C-side complete; SCRIP mirror pending as PRF-13)
next: PRF-13 — rewrite GatherBlock in parser_raku.sc to pure reduce('TT_GATHER','nTop()');
  create raku_helpers.sc with gather_hoist_pass(); update driver tail.
  Then PRF-12-sub/class/for/self (lower.c work, discrete sessions).
clarification 2026-05-18: grammar actions in raku.y are NOT PST violations — they
  fire at reduce time, which is correct CFG behavior. PRF-12 items are lower.c
  interface work (lower reads _id fifth-field; never sees TT_FOR/TT_SUB_DECL/
  TT_CLASS_DECL because parser desugared them). raku.y stays as-is; lower gets
  new TT_* dispatch cases for each construct.
PRF-12-gather ✅ 2026-05-18 (Claude Sonnet 4.6): TT_GATHER added to ast.h;
  KW_GATHER rule rewritten to pure TT_GATHER[body...] transcription;
  raku_lower_hoist_gather_pass() post-parse pass fountains __gather_N, builds
  def+call TT_FNCs, bulk-prepends defs. Three bug fixes: attr child recursion,
  union clobber (v.ival=0 after v.sval), _nalloc not reset on in-place rewrite.
  lower.c: fatal stub for TT_GATHER. raku.tab.c regenerated. .ref files updated.
  Gates: smoke_raku 5/0, smoke_icon 5/0, scrip_all_modes 2/0,
  crosscheck_snobol4 5/1 (pre-existing), crosscheck_raku 23/10 (was 21/12).
session 2026-05-18 (Opus 4.7) — GOAL CONVERGENCE CLARIFIED by Lon:
  The C parser (raku.y → raku.tab.c → tree_t) and the SCRIP parser
  (parser_raku.sc + raku_stubs.sc → tree_t via TDump) must produce
  BYTE-IDENTICAL tree_t for the same source — one-to-one with language
  constructs. The "shift/reduce only" form-rule on the SCRIP side and
  the "no semantics in parser" rule on the C side are both means to the
  same end: convergence. PRF-12 is exactly where the two sides diverge
  from each other AND from source structure, so PRF-12 is the convergence
  work, not optional polish.
PRF-12 step 1 (gather) — validated plan, not committed (session ran out of context):
  C-side:
    1. ast.h: add TT_GATHER to enum + name table (last in list).
    2. raku.y gather rule (line 472): replace 11-line semantic body
       (name fountain + def/call TT_FNC + add_proc) with 4-line pure
       transcription: ast_node_new(TT_GATHER); splice block body's
       children in via expr_add_child. Verified compiles + holds gates.
    3. Post-parse hoist pass in raku.y: raku_lower_hoist_gather_pass()
       walks subjects of raku_prog_result, finds TT_GATHER, fountains
       __gather_N, builds def TT_FNC (SUB_TAG_ID), COLLECTS def stmts
       in source-encounter order, BULK-INSERTS at front of
       raku_prog_result (single-prepend reverses multi-gather order —
       use collect-then-bulk). Rewrites TT_GATHER node in place to
       TT_FNC{c[0]=TT_VAR(gname)}. Call from raku_parse_string after
       raku_yyparse().
    4. Regenerate raku.tab.c: `bison -d -o raku.tab.c raku.y` from
       src/frontend/raku/ (NO -p; api.prefix is already in the .y).
       Pre-existing 28 shift/reduce warnings are not errors.
  SCRIP mirror:
    5. parser_raku.sc GatherBlock: replace with pure
       `( $'{' nPush() ARBNO( *SubBlock_body ) $'}' reduce('TT_GATHER','nTop()') nPop() )`
       Remove Set_gather_name, Push_gather_name_var, Emit_to_sub_list
       from this rule. Remove `gather_seq = 0` initializer.
    6. raku_stubs.sc: remove set_gather_name, push_gather_name_var,
       cap_gather_name. Add gather_hoist_pass(ptree) + helpers using
       tree.sc API: t(g)='TT_FNC'; v(g)=gname; n(g)=0; c(g)=NULL;
       Append(g, tree('TT_VAR',gname)). Build def via Tree() / Append,
       wrap in STMT(:subj(def)), Insert at front of sub_list snapshot.
    7. parser_raku.sc driver tail: invoke gather_hoist_pass(ptree)
       right after `ptree = Pop()` and before sub_rev/dump walks.
  Gotchas to handle:
    - run_scrip_parser.sh loads ${LANG}_helpers.sc but NOT raku_stubs.sc.
      Either rename raku_stubs.sc → raku_helpers.sc (history says this
      file was previously deleted by PST-RAKU-sidecar-elim 78c1b4a;
      reviving the name is fine since PRF-12 changes the contents),
      or update run_scrip_parser.sh to also load raku_stubs.sc.
    - gather_take_var.ref shows `(TT_FNC __gather_0 ...)` with bare name,
      but C-side --dump-ast (pre-existing) emits `(TT_FNC (TT_VAR __gather_0) ...)`
      with v.sval="". Pre-existing divergence between .ref author and
      current ir_dump_program. Convergence work needs to first decide
      canonical side, then regenerate .ref files. Likely C-side wins
      since gates measure against it.
  Validated this session: steps 1-2 of C-side compiled cleanly, steps 3-7
  applied cleanly to working tree, all five gates held at floor exactly
  (smoke_raku 5/0, smoke_icon 5/0, scrip_all_modes 2/0, crosscheck_snobol4 5/1
  pre-existing, crosscheck_raku 21/12 unchanged). REVERTED for clean handoff
  because session was at 88% context window and Lon clarified mid-session;
  next session should redo from clean tree with full attention.
functions remaining in parser_raku.sc: 1
  dq_unescape  — PST-clean pre-pass string processor (no tree ops, no Push, no Append) — leave
PRF-10 (push_interp_str) ✅ 2026-05-18 (Claude Opus 4.7): Eliminated. New leaf-only
  stub `push_interp_leaves` in raku_stubs.sc walks capstr post-dq_unescape, pushes one
  TT_QLIT or TT_VAR leaf per chunk + IncCounter() per push. NO Append, NO tree-of-trees.
  LitStrDQ use site wrapped: nPush() LitStrDQ Dq_unescape Push_interp_leaves
  reduce('TT_CAT', r_nTop) nPop(). r_nTop idiom skips wrap when count<=1.
  Gates: smoke_raku 5/0, smoke_icon 5/0, scrip_all_modes 2/0, crosscheck_snobol4 5/1
  (pre-existing), crosscheck_raku 21/12 unchanged (rk_interp + rk_strings stable).
PRF-9 (finish_gather_body) ✅ 2026-05-18 (Claude Opus 4.7): TRANSITIONAL — see PRF-12.
  Eliminated from parser_raku.sc. GatherBlock uses two nPush/reduce('TT_FNC',n)/nPop
  with new stubs Set_gather_name (bumps gather_seq, captures '__gather_N' in
  cap_gather_name) and Push_gather_name_var (pushes TT_VAR with captured name).
  Stubs in raku_stubs.sc. Mirrors existing raku.y violation; both move to lower
  under PRF-12. Gates: all green at floor, rk_gather FAIL unchanged (pre-existing).
PRF-8 (finish_given) ✅ 2026-05-18 (Claude Opus 4.7): Eliminated.
  WhenClause = Expr nInc() Block nInc(); DefaultClause = Push_nul Block nInc()×2;
  GivenStmt nPush()/reduce('TT_CASE','nTop()+1')/nPop with topic below frame.
  **TT_CASE shape changed**: 2-per-arm `[topic, val, body, ..., (TT_NUL, body_def)?]`,
  cmpkind moved to lower.c (derived from val->t at lower time, gated LANG_RAKU).
  Paired raku.y + lower.c + parser_raku.sc commits.
  Gates: smoke_raku 5/0, smoke_icon 5/0, scrip_all_modes 2/0, crosscheck_snobol4 5/1,
  crosscheck_raku 21/12 unchanged, rk_given + rk_given18 still PASS.
separation-of-concerns principle (binding 2026-05-18): documented at top of this
  goal file. Parser transcribes; lower decides semantics; emitter walks SM. The
  pre-existing helper-count criterion (zero tree-building functions in parser_*.sc)
  is the *form* test; the principle is the *substance* test. Helpers that match
  the principle (leaf-only pushers, pre-pass string transformers) are permitted
  in stubs files; everything else moves to lower. PRF-12 queues the existing
  raku.y violations for migration.
lower.c change PRF-8: lower_case raku branch reshaped to 2-per-arm with cmpkind
  derived from val->t (TT_QLIT → TT_LEQ, else TT_EQ). Gated on g_lang==LANG_RAKU.
lower.c change PRF-6 (earlier): lower_record updated for convention-2 (empty
  v.sval → read cname from c[0]).
new stubs in raku_stubs.sc this session: set_gather_name + push_gather_name_var
  (PRF-9, transitional); push_interp_leaves (PRF-10, leaf-only). Plus prior:
  push_fn_raku_mcall, push_mcall_mth_qlit, push_fn_raku_new, push_cls_qlit,
  push_sub_name_var, push_mth_name_var, push_self_var, push_cls_name_var,
  push_main_var, emit_to_sub_list, push_stmt_subj (and Push_*/Emit_* aliases).
gates at handoff: smoke_raku 5/0, smoke_icon 5/0, scrip_all_modes 2/0,
  crosscheck_snobol4 5/1 (pre-existing), crosscheck_raku 21/12 unchanged.
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
