# GOAL-PST-PROLOG.md — Pure Syntax Tree: Prolog Rewrite

**Repo:** one4all + corpus + .github
**Parent goal:** `GOAL-PARSER-PURE-SYNTAX-TREE.md` (Step 6)
**Split from:** `GOAL-PST-REBUS-PROLOG.md` — Prolog half only
**Status:** Active — PST-PL-6e next

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

- [ ] **PST-PL-6f** — Delete all `Term*`-returning code paths from
  `prolog_parse.c`. Delete slot-assignment from `scope_get`. `Term` type
  survives only as a runtime type (for unification), not as a parse output.
  Remove `VarScope.next_slot`. Remove `lower_term()` call sites that were
  replaced by tree_t path in 6d.

- [ ] **PST-PL-6g** — Decide whether `IfFrame` directive-stack stays in
  parser (answer from 6a: yes — it is a preprocessor concern, not
  control-flow lowering). Document in `prolog_parse.c` comment. Close rung.

Gates per rung: `smoke_prolog`, `crosscheck_prolog`, `smoke_scrip_all_modes`,
`crosscheck_snobol4`.

---

## Done criterion

1. PST-PL-6a through 6g all checked [x].
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
watermark: PST-PL-6e complete 2026-05-16 (session 30/60)
next: PST-PL-6f — Delete all Term*-returning code paths from prolog_parse.c; remove lower_term() call sites replaced by tree_t path in 6d.
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

## Authorship

Drafted by Claude Sonnet 4.6, 2026-05-16.
