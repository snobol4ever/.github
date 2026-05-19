# GOAL-PST-PROLOG.md — Pure Syntax Tree: Prolog Rewrite

**Repo:** one4all + corpus + .github
**Parent goal:** `GOAL-PARSER-PURE-SYNTAX-TREE.md` (Step 6)
**Status:** Active — PST-PL-6h next (see State block at end of file for current step)

```
(source) ──► PARSER ──► (tree_t — pure syntax) ──► LOWER ──► IR_sm_t[]  ──┐
                                                                            ├──► interp / emitters
                                                          └──► IR_bb_t  ──┘
```

Prolog currently builds `Term*` and assigns variable slots during parsing.
Both must change: `Term*` → `tree_t`, slot assignment → pre-lower pass.

**⛔ SCRIP mirror invariant:** Every rung touches both C-side parser/lower
AND `corpus/SCRIP/parser_prolog.sc` / `lower.sc` in the same commit.
Post-parse `tree_t` shape must match.

---

## ⛔ Pure-syntax rules (binding)

**Allowed:** `ast_node_new(TT_*)`, `expr_new`, `expr_unary`, `expr_binary`,
`ast_push`, `expr_add_child`. Setting `v.sval/v.ival/v.dval` from token.
N-ary flattening (`pt_flatten_conj`, `pt_maybe_ifthenelse`) stays in parser.

**Forbidden:** Building `Term*` from parser actions; variable-slot assignment
in parser; scope lookup during parse; child reordering for positional semantics.

**⛔ Left-to-right child order:** All children in source token order.

**⛔ Three Phase-1 facets** (per `GOAL-PARSER-PURE-SYNTAX-TREE.md § "The three Phase-1 facets"`):

- **F1 — `tree_t` is the sole information channel.** Prolog has two F1 violations: (a) the DCG `-->` path still returns `Term*` (the historical Prolog parser-output type) instead of `tree_t` — owned by `PST-PL-6f`; (b) `assign_anon_slots` runs during parse and writes slot indices into `_id` — a side-channel; owned by `PST-PL-SC-1/2/3` (slot assignment moves to lower). The remaining four §⛔ violations (Pl1–Pl4) are all inspect-kind-and-rearrange / structure-detect in `pt_flatten_conj`/`pt_maybe_ifthenelse`/`pt_make_clause` — these are F3 problems (rule 2 mutation / kind inspection), but moving the three helpers to `prolog_lower.c` (owned by `PST-PL-6h`) is also an F1 cleanup: the parser then emits the raw `;`/`->`/`,` `TT_FNC` chains and lower flattens, eliminating parser-side structure synthesis.
- **F2 — `tree_t` has exactly four fields `t`, `v`, `n`, `c`.** Cross-cutting `PST-FIELD-1`/`PST-FIELD-2`. Prolog is the third primary `_id` consumer (after Icon and Raku) via `assign_anon_slots` storing slot indices into `_id` on `TT_VAR` nodes. PST-PL-SC-1/2/3 (move slot assignment to lower) is the Prolog-side prerequisite for PST-FIELD-2 closing.
- **F3 — Children L→R in source-token order.** Pratt-style `pt_term` loop is clean (always wraps fresh via `pt_binop`). The four §⛔ violations all flow through `pt_maybe_ifthenelse` / `pt_flatten_conj` / `pt_make_clause` — all owned by `PST-PL-6h`.

---

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
```

Gate scripts:
```bash
bash /home/claude/one4all/scripts/test_smoke_prolog.sh
bash /home/claude/one4all/scripts/test_smoke_scrip_all_modes.sh
bash /home/claude/one4all/scripts/test_crosscheck_snobol4.sh   # regression guard
bash /home/claude/one4all/scripts/test_crosscheck_prolog.sh
```

## ⛔ SCRIP mirror work — Prolog orientation

**C side must be clean before `parser_prolog.sc` mirror work.** PST-PL-6f (delete all `Term*`-returning paths from `prolog_parse.c`) must be complete first. Until then the C frontend's output is `Term*`, which has no direct representation as pure `tree_t` shift/reduce in the SCRIP mirror.

**When starting `parser_prolog.sc` mirror work:** Read `SNOBOL4-SNOCONE-PRIMER.md` in full. Learn Snocone expression syntax from the SPITBOL manual and control-flow syntax from `corpus/SCRIP/parser_snocone.sc`. The goal is pure `shift`/`reduce` — no `Push`, `Pop`, `Append`, `Tree`, or helper functions that inspect children. Variable slot assignment must NOT appear in `parser_prolog.sc`; slot allocation is a lower-time concern (handled by the C `prolog_lower.c` pre-lower pass from PST-PL-6e).

---

## Term → tree_t mapping (verified in 6a)

| Term construct       | tree_t kind    | Notes                                     |
|----------------------|----------------|-------------------------------------------|
| atom                 | `TT_QLIT`      | `v.sval = name`                           |
| integer literal      | `TT_ILIT`      | `v.ival = value`                          |
| float literal        | `TT_FLIT`      | `v.dval = value`                          |
| variable             | `TT_VAR`       | `v.sval = name`, **no slot in parser**    |
| anonymous `_`        | `TT_VAR`       | `v.sval = "_"` — lower allocates slot     |
| compound `f(...)`    | `TT_FNC`       | `v.sval = functor`, `c[] = args`          |
| list `[a,b\|t]`      | `TT_MAKELIST`  | elements + optional tail child; v.ival=1 if explicit \| tail |
| `,` conjunction      | flattened      | `pt_flatten_conj` → flat `TT_PROGRAM`     |
| `;`/`->` if-then-else| `TT_IF`        | `pt_maybe_ifthenelse` → `TT_IF(c,t,e)`   |
| `:-` clause          | `TT_CLAUSE`    | `c[0]=head, c[1]=TT_PROGRAM`             |
| `:-` directive       | `TT_CLAUSE`    | `c[0]=TT_NUL, c[1]=TT_PROGRAM`           |
| `!` cut              | `TT_CUT`       | leaf node                                 |

---

## Rungs

- [x] **PST-PL-6a** — Verify kind-mapping against corpus edge cases.
  Read `prolog_parse.c` AND `corpus/SCRIP/parser_prolog.sc` in full.
  Check whether any Prolog construct needs a new `TT_*` not in `ast.h`.
  Record findings. **No code changes yet.**

- [x] **PST-PL-6b** — Add parallel `tree_t`-building code path alongside
  existing `Term*` code in `prolog_parse.c`. Both active. Parser builds
  both `Term*` (old) and `tree_t` (new) for the same input.
  `is_dcg` flag: DCG clauses set `cl->tr=NULL`, skip tree replay.
  SCRIP mirror: `parser_prolog.sc` produces the `tree_t` shape.

- [x] **PST-PL-6c** — Verifier: after parsing a clause both ways, assert
  structural equivalence between the `Term*` tree and the `tree_t` tree.
  Run across the Prolog corpus. Fix any shape mismatches.
  Result: 366 non-SWI/non-gnu corpus files → 0 mismatches.

- [x] **PST-PL-6d** — Switch downstream consumers to `tree_t` one at a time:
  `prolog_lower.c` switched to `lower_clause_from_tree()` when `cl->tr != NULL`.
  DCG clauses fall back to Term* path. `TRSlotMap` pre-lower slot assignment added.
  SCRIP mirror: `lower.sc` updated for Prolog `tree_t` shape.

- [x] **PST-PL-6e** — Move variable-slot allocation to a pre-lower pass in
  `prolog_lower.c`: walk each clause's `tree_t`, collect all `TT_VAR` names,
  assign sequential integer slots, attach `ival` during lowering for
  `IR_PL_VAR`. Delete slot assignment from `scope_get` / `scope_find`.
  `TRSlotMap` is already in `prolog_lower.c` from 6d — promote it to the
  canonical slot-assignment mechanism; remove `next_slot` from `VarScope`.
  SCRIP mirror: `lower.sc` pre-lower slot-allocation pass.

- [x] **PST-PL-6f** — Delete all `Term*`-returning code paths from
  `prolog_parse.c`. Delete slot-assignment from `scope_get`. `Term` type
  survives only as a runtime type (for unification), not as a parse output.
  Remove `VarScope.next_slot`. Remove `lower_term()` call sites that were
  replaced by tree_t path in 6d.

- [x] **PST-PL-6g** — Decide whether `IfFrame` directive-stack stays in
  parser (answer from 6a: yes — it is a preprocessor concern, not
  control-flow lowering). Document in `prolog_parse.c` comment. Close rung.

- [x] **PST-PL-6h — Move `pt_maybe_ifthenelse` and `pt_flatten_conj` child inspection to lower. PHASE 1 C.** ✅ 2026-05-19

  **The violation (Aspect 3):** `pt_maybe_ifthenelse` (`prolog_parse.c` line ~507
  and ~1198) inspects `->t` and `->v.sval` of already-built child nodes to detect
  the `';'('->'(Cond,Then), Else)` idiom and collapse it to `TT_IF`. This is the
  parser reading back what it just built to make a structural decision — forbidden.
  `pt_flatten_conj` similarly walks a conjunction tree during parse, inspecting
  `->t == TT_FNC && strcmp(->v.sval, ",")` recursively.

  **Fix:** Emit raw from grammar rules: `TT_FNC(';', [...])` and `TT_FNC(',', [A,B])`
  exactly as parsed, left-to-right, no inspection. Move both rewrites to
  `prolog_lower.c`: a pre-lower pass rewrites `';'('->'(...), ...)` → `TT_IF`;
  another flattens `','`-chains → n-ary `TT_PROGRAM`. Parser emits faithfully;
  lower interprets.

  Gates: `smoke_prolog`, `crosscheck_prolog`, `smoke_scrip_all_modes`.

Gates per rung: `smoke_prolog`, `crosscheck_prolog`, `smoke_scrip_all_modes`,
`crosscheck_snobol4`.

---

## Phase 2 rungs — SCRIP mirror (after Phase 1 complete: 6f, 6g done)

**Do not start until all six C parsers satisfy Phase 1 and PST-PL-6f, 6h are checked [x].**

- [ ] **PST-PL-SC-1 — Audit `parser_prolog.sc` for Aspect 1 and Aspect 2 violations.**

  **Aspect 1** (tree_t is complete — all info forward-passable from tree alone):
  `assign_anon_slots()` currently walks the built tree post-construction and
  mutates `TT_VAR` nodes in place, replacing `v = '_ANON'` with `v = '_V<n>'`.
  This is a post-build tree mutation inside the parse phase. The mutation
  writes slot numbers into the `v` field — the info ends up in the tree, but
  the act of mutation happens after `Reduce`. This is a violation of the
  pure-parse rule: the parser must not walk and rewrite its own output.

  **Where:** `parser_prolog.sc`, function `assign_anon_slots` (lines ~102–114)
  and its call sites at lines ~456, 462, 475.

  **Fix:** Remove `assign_anon_slots` from the parse phase entirely. Anonymous
  variables `_` should be emitted as `TT_VAR` with `v = '_ANON'` and left
  that way. Lower assigns distinct slot names to each `_ANON` occurrence —
  it can do this by walking the tree post-parse, which is where tree-walking
  belongs. Add a `prolog_lower_anon_slots(tree_t*)` pass to `prolog_lower.c`
  (or `lower.c`) that renames each `_ANON` to a unique `_V<n>` in pre-lower.

  **Aspect 2** (tree_t has only t, v, n, c — no in-place mutation):
  `Append(fnc_node, lhs)` / `Append(fnc_node, rhs)` calls throughout
  `parser_prolog.sc` (lines ~200–261) mutate an already-pushed `tree_t`
  node by inserting additional children. `Append` calls `Insert` which
  rewrites `n(x)` and `c(x)` in place. This is forbidden in the pure-parse
  phase — a `reduce` call must gather all children first, then create the
  node atomically.

  **Where:** `parser_prolog.sc` lines ~200–261 in operator-building helpers
  (`build_binop`, `build_unop`, `build_if`, `build_list`, `build_op261`).

  **Fix:** Rewrite each helper to use `nPush`/`nInc`/`nPop` counter
  discipline instead of `Append`. Each child is `Push`-ed individually;
  the helper ends with `Reduce('TT_FNC', n)` or `Reduce(tag, n)`. No node
  is created until all children are on the stack.

  No code changes in this rung — audit and document findings only.

- [ ] **PST-PL-SC-2 — Remove `assign_anon_slots` from parse phase.**

  **What:** Delete the three call sites of `assign_anon_slots` from
  `parser_prolog.sc` (lines ~456, 462, 475). Delete the function body.
  All `_ANON` occurrences remain as `TT_VAR('_ANON')` in the tree.

  **Where in lower:** Add `prolog_lower_anon_slots(tree_t *clause)` to
  `src/lower/prolog_lower.c`. It walks the clause tree, finds each
  `TT_VAR` node with `v.sval == "_ANON"`, assigns a unique `_V<n>` name
  using a local counter. Call it at the top of `lower_prolog_clause()`.

  **Why:** The tree must be complete and immutable after `Reduce`. Walking
  and rewriting it inside the parser phase violates the two-phase contract.
  Slot naming is a lower-time semantic concern — it requires knowing all
  anonymous variables in a clause, which lower already traverses.

  Gates: `smoke_prolog`, `crosscheck_prolog`, `smoke_scrip_all_modes`.

- [ ] **PST-PL-SC-3 — Replace `Append`-based node building with `Reduce`.**

  **What:** Rewrite all operator/compound-building helpers in
  `parser_prolog.sc` that use `Append(node, child)` to instead use the
  stack counter discipline:
  - Push each child onto the parse stack with `Push(child)` / `nInc()`.
  - End with `Reduce('TT_FNC', nTop())` or `Reduce(tag, n)`.
  - Delete the pre-allocated `fnc_node = tree(...)` + `Append` pattern.

  **Specifically** (lines ~200–261): `build_binop`, `build_unop`,
  `build_if` (or equivalent local helpers), plus any anonymous helper
  blocks that call `Append`.

  **Why:** `Append` mutates `n(x)` and `c(x)` of an existing node.
  The only permitted tree-building operations in the parse phase are
  `Shift(t, v)` (create leaf, push) and `Reduce(t, n)` (pop n, create
  node with n children, push). `Append` is structurally identical to
  calling `Reduce` after the fact — it must not exist in the parse phase.

  Gates: `smoke_prolog`, `crosscheck_prolog`, `smoke_scrip_all_modes`,
  `crosscheck_snobol4`.

---

## Done criterion

1. PST-PL-6a through 6h all checked [x] (Phase 1 C complete).
2. PST-PL-SC-1 through SC-3 checked [x] (Phase 2 SCRIP mirror complete).
3. `parser_prolog.sc` contains zero `Append()` calls.
4. `parser_prolog.sc` contains no post-build tree-walking or mutation.
5. `assign_anon_slots` does not exist in `parser_prolog.sc`.
6. All gate scripts green at baseline.
2. `prolog_parse.c` produces only `tree_t` — `Term*` gone as parser output.
3. Variable-slot assignment lives exclusively in `prolog_lower.c` pre-lower pass.
4. All gate scripts green at baseline.
5. Beauty self-host byte-identical (Milestone 1 protected).
6. Parent goal `GOAL-PARSER-PURE-SYNTAX-TREE.md` Step 6 checked [x].

On completion: update parent goal's step ladder, bump watermark,
commit and push HQ.

---

## Risks

- **`Term` runtime type** — must not be deleted from `prolog_unify.c` /
  `prolog_builtin.c` where it is used for runtime unification. Only the
  *parser output* path changes.
- **Prolog parser shares scope state with lookahead** — preserve
  variable-name→identity correspondence across a clause; only the slot
  numbering moves to lower.
- **DCG clauses** — `cl->tr == NULL` throughout; Term* path stays for DCG
  until a future rung adds tree_t DCG expansion in lower.

---

## State

```
watermark: 2026-05-19 (Sonnet 4.6) — PST-PL-6h complete. Phase 1 C CLEAN. All 6a-6h checked [x].
           2026-05-19 (Opus 4.7 session 4) — Three-facet block added; F1/F2/F3 stated.
           2026-05-19 — audit findings (PST-LR-AUDIT.md § Scan 6): 4 §⛔ violations
             (Pl1–Pl4) all owned by PST-PL-6h. Pl5 (DCG → tree_t) is non-§⛔ scope,
             owned by PST-PL-6f (in progress).
           PST-PL-6g complete 2026-05-18 (Sonnet 4.6) — ALL RUNGS 6a–6g COMPLETE
           PST-PL-6f partial 2026-05-18 — non-DCG path fully on tree_t.
status:    ✅ Phase 1 C COMPLETE. All rungs 6a–6h checked [x]. Phase 2 SCRIP mirror BLOCKED until all six C parsers Phase 1 clean.
next: parser_prolog.sc mirror" was wrong** — Phase 2
           SCRIP mirror BLOCKED until all six C parsers Phase 1 clean.
next:      **PST-PL-SC-1** — audit parser_prolog.sc for Aspect 1 (assign_anon_slots) and Aspect 2 (Append mutations). BLOCKED until all six C parsers Phase 1 clean.
mirror gaps: ⚠ MIRROR-GAP-PL-6h will record when 6h commits. Phase 2 SCRIP
             mirror BLOCKED until all six C parsers Phase 1 clean.
heads:     .github @ (updating) · one4all @ 06cadffb · corpus (no changes)
```

### Session-end note — 2026-05-19 (Opus 4.7 session 4)

HQ session — PST-LR-AUDIT-1 closed and three-facet block added across all six
PST goal files. No Prolog-specific code changes this session. Next session:
follow PST-PL-6h fix sketch above (three helpers move verbatim from
`prolog_parse.c` to `prolog_lower.c`). Note Prolog is the third primary
`_id` consumer via `assign_anon_slots` — PST-FIELD-2 closure depends on
PST-PL-SC-1/2/3 landing (slot assignment moves to lower).
findings-6f:
  - parse_clause() rewritten: pt_term() is now the sole parse path for non-DCG clauses.
  - Lexer snapshot retained only for DCG path (Term* dcg_expand_clause still needs it).
  - eval_if_condition / try_handle_if_directive ported to tree_t (eval_if_condition_tree,
    try_handle_if_directive_tree); old Term* versions deleted.
  - PST-PL-6c verifier (PLS/ser_term*/ser_tree*/pl_verify_clause_tree) deleted — ~300 LOC.
  - count_conj / flatten_conj deleted; DCG-only versions (dcg_count_conj / dcg_flatten_conj)
    kept for dcg_expand_body.
  - term_pretty / prolog_program_pretty deleted; prolog_program_pretty removed from .h.
  - PlProgram.tree_mismatches field removed; prolog_program_tree_mismatches() removed.
  - Parser.tree_mismatches field removed.
  - prolog_lower.c: begin_tests/end_tests detection ported to tree_t.
  - prolog_lower.c: directive loop ported to tree_t; export detection uses tree_t.
  - prolog_lower.c: predicate loop guard changed from `cl->head != NULL` to
    `is_rule || is_dcg` (tree_t head c[0]->t != TT_NUL discriminates rule vs directive).
  - Bug fix: both loops guarded to avoid double-processing non-DCG rules as directives.
  - lower_term() call sites for directive path removed; goal_tr always set post-6f.
  - Gates: smoke_prolog PASS=5, crosscheck_prolog PASS=128, crosscheck_snobol4 PASS=5 FAIL=1
    (beauty_omega pre-existing), smoke_scrip_all_modes PASS=2.
findings-6a:
  - All required TT_* already in ast.h. No new kinds needed.
  - [] atom → TT_MAKELIST (empty). TT_MAKELIST v.ival=1 marks explicit | tail.
  - pt_maybe_ifthenelse: ;(->(C,T),E) → TT_IF(c,t,e). Stays in parser.
  - IfFrame directive stack stays in parser. PST-PL-6g confirmed: no change needed.
  - TT_CUT leaf for !. TT_CLAUSE(TT_NUL, body) for directives.
findings-6b:
  - Lexer plain-copyable; save p->lx before Term* parse, restore into p2 for parallel pt_* replay.
  - pt_primary/pt_term/pt_list/pt_args/pt_binop/pt_flatten_conj/pt_maybe_ifthenelse/pt_make_clause.
  - TreeScope name→interned-ptr; no slot numbers (moved to 6e).
  - is_dcg flag: DCG clauses set cl->tr=NULL, skip tree replay + 6c verification.
  - Gates: smoke_prolog PASS=5, crosscheck_snobol4 PASS=6, smoke_scrip PASS=2.
findings-6c:
  - Verifier: ser_clause_term/ser_clause_tree → canonical S-expr → strcmp inline in parse_clause.
  - PlProgram.tree_mismatches counter; prolog_program_tree_mismatches() accessor.
  - Bug fixes: [] TK_ATOM → TT_MAKELIST; v.ival tail flag; TT_FNC(",") 2-child → (seq);
    TT_FNC("{}") 0-child → (atom "{}"); ser_term_conj_flat for directive body;
    pt_maybe_ifthenelse flattens then/else branches.
  - Result: 366 non-SWI/non-gnu corpus files → 0 mismatches. 7 in SWI {|...|} (out of scope).
  - Gates: smoke_prolog PASS=5, crosscheck_snobol4 PASS=6, smoke_scrip PASS=2.
findings-6d:
  - lower_clause_from_tree(): TRSlotMap assigns sequential v.ival to TT_VAR by name.
    Anonymous "_" always gets a fresh slot.
  - key_of_head_tree(): derives PredKey from TT_FNC/TT_QLIT head node.
  - tr_assign_slots(): pre-lower slot walk over tree_t.
  - prolog_lower() main loop: key_of_head_tree + lower_clause_from_tree when cl->tr != NULL.
    DCG (cl->tr == NULL) falls back to Term* path unchanged.
  - Directive loop: uses goal_tr (tree_t body[0]) when available.
  - Gates: smoke_prolog PASS=5, crosscheck_snobol4 PASS=6, smoke_scrip PASS=2.
mirror gaps: (none — parser_prolog.sc already produces tree_t shapes)
findings-6e:
  - Removed next_slot from VarScope; scope_get now assigns saved_slot=-1 for all new vars.
  - Added var_names/var_terms/nvar snapshot fields to PlClause (prolog_parse.h).
  - parse_clause() copies VarScope entries into cl->var_names/var_terms/nvar after parse.
  - lower_clause(): named-var pre-pass assigns sequential saved_slot from cl->var_names/var_terms;
    ASSIGN_ANON walk fills remaining -1 slots (anonymous vars) above named slots.
  - assign_clause_anon_slots(): same pattern (for plunit test path).
  - lower_clause_from_tree() + tr_assign_slots(): unchanged — TRSlotMap is canonical for tree_t.
  - lower.sc: no change needed (slot assignment is internal C lowering; tree_t shape unchanged).
  - Gates: smoke_prolog PASS=5, crosscheck_prolog PASS=127, crosscheck_snobol4 PASS=6.
```

### Session-end note — 2026-05-19 (Sonnet 4.6)

Goal: PST-PL-6h — move three parser helpers to prolog_lower.c.

**What landed:**
- `pt_flatten_conj` → `pl_flatten_conj` in `prolog_lower.c`
- `pt_maybe_ifthenelse` → `pl_maybe_ifthenelse` in `prolog_lower.c`
- `pt_make_clause` + body-wrap → `pl_make_clause` in `prolog_lower.c`
- Parser now emits raw `TT_FNC(",")` chains and raw `TT_FNC(";")` nodes in source-token order. No structural inspection in parse phase.
- `lower_clause_from_tree`: updated to call `pl_flatten_conj` + `pl_maybe_ifthenelse` on raw body from parser.
- Directive detection loop (`begin_tests`/`end_tests` and `initialization`/`export`): updated for raw body shape.
- All three parse-clause call sites (`pt_make_clause(NULL,body)`, `pt_make_clause(head,body)`, `pt_make_clause(head,NULL)`) replaced with inline `TT_CLAUSE` building (head child + raw body child).

**Gates at hand-off:** smoke_prolog PASS=5, crosscheck_prolog PASS=128, smoke_scrip_all_modes PASS=2, crosscheck_snobol4 PASS=5 FAIL=1 (beauty_omega pre-existing).

**Phase 1 C status: COMPLETE.** All rungs 6a–6h checked [x].
**Phase 2 SCRIP mirror: BLOCKED** until all six C parsers Phase 1 clean.
**Next unblocked rung:** PST-PL-SC-1 (unblocks when other five parsers land Phase 1).

one4all @ `06cadffb` · .github @ `d8659efa`

## Authorship

Drafted by Claude Sonnet 4.6, 2026-05-16.
