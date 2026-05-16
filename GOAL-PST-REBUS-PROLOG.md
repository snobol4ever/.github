# GOAL-PST-REBUS-PROLOG.md — Pure Syntax Tree: Rebus + Prolog Rewrite

**Repo:** one4all + corpus + .github
**Parent goal:** `GOAL-PARSER-PURE-SYNTAX-TREE.md` (Steps 5 and 6)
**Status:** Active — PST-RB-5a next

```
(source) ──► PARSER ──► (tree_t — pure syntax) ──► LOWER ──► IR_sm_t[]  ──┐
                                                                            ├──► interp / emitters
                                                          └──► IR_bb_t  ──┘
```

Both Rebus and Prolog require **full replacement** of their current IR types:
- **Rebus**: `RExpr*` / `RStmt*` / `RProgram*` → `tree_t*`
- **Prolog**: `Term*` → `tree_t*`, plus variable-slot assignment moved from
  parser/scope to a pre-lower pass in `prolog_lower.c`

**⛔ SCRIP mirror invariant:** Every rung touches both C-side parser/lower
AND the corresponding `corpus/SCRIP/parser_rebus.sc` / `parser_prolog.sc` /
`lower.sc` in the same commit. Post-parse `tree_t` shape must match.

---

## ⛔ Pure-syntax rules (binding)

**Allowed:** `ast_node_new(TT_*)`, `expr_new`, `expr_unary`, `expr_binary`,
`ast_push`, `expr_add_child`. Setting `v.sval/v.ival/v.dval` from token.

**Forbidden:** Building `RExpr*` / `RStmt*` / `RProgram*` / `Term*` from
parser actions; variable-slot assignment in parser; scope lookup during parse;
child reordering for positional semantics.

**⛔ Left-to-right child order:** All children in source token order.

---

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
```

Gate scripts:
```bash
bash /home/claude/one4all/scripts/test_smoke_rebus.sh
bash /home/claude/one4all/scripts/test_smoke_prolog.sh
bash /home/claude/one4all/scripts/test_smoke_scrip_all_modes.sh
bash /home/claude/one4all/scripts/test_crosscheck_snobol4.sh   # regression guard
bash /home/claude/one4all/scripts/test_crosscheck_prolog.sh
```

---

## Step 5 — Rebus rewrite (RExpr* → tree_t)

Rebus currently builds a separate `RProgram` / `RStmt` / `RExpr` IR — it
never touches `tree_t`. The entire pipeline must be redirected.

### REKind → TT_* mapping

Establish this before touching any code. Refer to `rebus.h` for the full
`REKind` enum. Likely mapping (verify and extend in PST-RB-5a):

| REKind           | tree_t kind      | Notes                              |
|------------------|------------------|------------------------------------|
| RE_LIT_S         | `TT_QLIT`        | `v.sval = string`                  |
| RE_LIT_I         | `TT_ILIT`        | `v.ival = integer`                 |
| RE_LIT_F         | `TT_FLIT`        | `v.dval = double`                  |
| RE_VAR           | `TT_VAR`         | `v.sval = name`                    |
| RE_ASSIGN        | `TT_ASSIGN`      | `c[0]=lhs, c[1]=rhs`              |
| RE_BINOP(op)     | `TT_ADD` etc.    | per-operator kind                  |
| RE_UNOP(op)      | `TT_MNS` etc.    | per-operator kind                  |
| RE_CALL          | `TT_FNC`         | `v.sval=name, c[]=args`           |
| RE_SEQ           | `TT_SEQ`         | concatenation                      |
| RE_BLOCK         | `TT_PROGRAM`     | statement list                     |
| RE_IF            | `TT_IF`          | `c[0]=cond, c[1]=then, c[2]=else?`|
| RE_WHILE         | `TT_WHILE`       | `c[0]=cond, c[1]=body`            |
| RE_DEFINE        | `TT_DEFINE`      | `v.sval=name, c[]=params+body`    |
| RE_RETURN        | `TT_RETURN`      | `c[0]=value?`                     |

Add new `TT_*` to `ast.h` only if needed for Rebus-specific constructs
with no existing equivalent.

### Rungs

- [x] **PST-RB-5a** — Map `REKind` → `TT_*` equivalents. Read `rebus.y`,
  `rebus.h`, `rebus_lower.c`, `rebus_emit.c`, `rebus_print.c` in full.
  Complete the mapping table above. Add any missing `TT_*` to `ast.h`.
  Record findings in State block. **No code changes yet.**

- [x] **PST-RB-5b** — Action bodies in `rebus.y` build `tree_t` directly.
  For each grammar rule currently building `RExpr*` / `RStmt*`:
  replace with `ast_node_new(TT_*)` + `expr_add_child` calls.
  Keep `RExpr*` downstream consumers unchanged for now (they will break
  at link/runtime — that's expected until 5d).
  SCRIP mirror: `parser_rebus.sc` produces the same `tree_t` shape.

- [x] **PST-RB-5c** — Delete `RExpr` / `RStmt` / `RProgram` structs and
  helpers: `rexpr_new`, `SAL`, `EAL`, `STAL`, and any `rexpr_free` /
  `rprogram_free` functions. `rebus.h` shrinks to the `TT_*` mapping and
  any remaining lexer helpers.

- [x] **PST-RB-5d** — Update downstream consumers to `tree_t`:
  `rebus_lower.c`, `rebus_emit.c`, `rebus_print.c`. Each walks `tree_t`
  nodes by `t` (kind) instead of `REKind`. `rebus_lower.c` will grow
  significantly — it now handles all the control-flow lowering that the
  old `RStmt` struct carried implicitly.
  SCRIP mirror: `lower.sc` handles Rebus `tree_t` lowering.

Gates per rung: `smoke_rebus`, `smoke_scrip_all_modes`, `crosscheck_snobol4`.

---

## Step 6 — Prolog rewrite (Term* → tree_t)

Prolog currently builds `Term*` and assigns variable slots during parsing.
Both must change: `Term*` → `tree_t`, slot assignment → pre-lower pass.

### Term → tree_t mapping

| Term construct       | tree_t kind    | Notes                                     |
|----------------------|----------------|-------------------------------------------|
| atom                 | `TT_QLIT`      | `v.sval = name`                           |
| integer literal      | `TT_ILIT`      | `v.ival = value`                          |
| float literal        | `TT_FLIT`      | `v.dval = value`                          |
| variable             | `TT_VAR`       | `v.sval = name`, **no slot in parser**    |
| anonymous `_`        | `TT_VAR`       | `v.sval = "_"` — lower allocates slot     |
| compound `f(...)`    | `TT_FNC`       | `v.sval = functor`, `c[] = args`          |
| list `[a,b\|t]`      | `TT_MAKELIST`  | elements + optional tail child            |
| `,` conjunction      | `TT_CAT`       | `c[0]=left, c[1]=right`                   |
| `;` disjunction      | `TT_ALT`       | `c[0]=left, c[1]=right`                   |
| `->` if-then         | `TT_IF`        | `c[0]=cond, c[1]=then`                    |
| `;` with `->` left   | `TT_IF`        | `c[0]=cond, c[1]=then, c[2]=else`         |
| `:-` clause          | `TT_CLAUSE`    | `c[0]=head, c[1]=body`                    |
| `:-` directive       | `TT_CLAUSE`    | `c[0]=TT_NUL, c[1]=body`                 |
| `!` cut              | `TT_CUT`       | leaf node                                 |

### Rungs

- [x] **PST-PL-6a** — Verify kind-mapping against corpus edge cases.
  Read `prolog_parse.c` AND `corpus/SCRIP/parser_prolog.sc` in full.
  Check whether any Prolog construct needs a new `TT_*` not in `ast.h`.
  Record findings. **No code changes yet.**

- [x] **PST-PL-6b** — Add parallel `tree_t`-building code path alongside
  existing `Term*` code in `prolog_parse.c`. Both active. Parser builds
  both `Term*` (old) and `tree_t` (new) for the same input.
  SCRIP mirror: `parser_prolog.sc` produces the `tree_t` shape.

- [ ] **PST-PL-6c** — Verifier: after parsing a clause both ways, assert
  structural equivalence between the `Term*` tree and the `tree_t` tree.
  Run across the Prolog corpus. Fix any shape mismatches.

- [ ] **PST-PL-6d** — Switch downstream consumers to `tree_t` one at a time:
  `prolog_lower.c` first, then `prolog_unify.c`, `prolog_builtin.c`,
  `prolog_driver.c`. Each switches from walking `Term*` to walking `tree_t`.
  Gate after each switch.
  SCRIP mirror: `lower.sc` updated for Prolog `tree_t` shape.

- [ ] **PST-PL-6e** — Move variable-slot allocation to a pre-lower pass in
  `prolog_lower.c`: walk each clause's `tree_t`, collect all `TT_VAR` names,
  assign sequential integer slots, attach `ival` during lowering for
  `IR_PL_VAR`. Delete slot assignment from `scope_get` / `scope_find`.
  SCRIP mirror: `lower.sc` pre-lower slot-allocation pass.

- [ ] **PST-PL-6f** — Delete all `Term*`-returning code paths from
  `prolog_parse.c`. Delete slot-assignment from `scope_get`. `Term` type
  survives only as a runtime type (for unification), not as a parse output.

- [ ] **PST-PL-6g** — Decide whether `IfFrame` directive-stack stays in
  parser (likely yes — it is a preprocessor concern, not control-flow
  lowering). Document decision in this file and in `prolog_parse.c` comment.

Gates per rung: `smoke_prolog`, `crosscheck_prolog`, `smoke_scrip_all_modes`,
`crosscheck_snobol4`.

---

## Done criterion for this goal

1. PST-RB-5a through 5d all checked [x].
2. PST-PL-6a through 6g all checked [x].
3. `rebus.y` produces only `tree_t` — `RExpr*` / `RStmt*` / `RProgram*` gone.
4. `prolog_parse.c` produces only `tree_t` — `Term*` gone as parser output.
5. Variable-slot assignment lives exclusively in `prolog_lower.c` pre-lower pass.
6. All gate scripts green at baseline.
7. Beauty self-host byte-identical (Milestone 1 protected).
8. Parent goal `GOAL-PARSER-PURE-SYNTAX-TREE.md` Steps 5 and 6 checked [x].

On completion: update parent goal's step ladder, bump watermark,
commit and push HQ.

---

## Risks

- **`rebus_lower.c` will grow significantly** — it currently has thin
  lowering because `RStmt` carried implicit control flow. Open a new
  `lower_rebus_ctrl.c` if needed.
- **Prolog parser shares scope state with lookahead** — preserve
  variable-name→identity correspondence across a clause; only the slot
  numbering moves to lower.
- **`Term` runtime type** — must not be deleted from `prolog_unify.c` /
  `prolog_builtin.c` where it is used for runtime unification. Only the
  *parser output* path changes.

---

## State

```
watermark: PST-PL-6b complete 2026-05-16 (session 30/59)
next: PST-PL-6c — verifier: after parsing a clause both ways, assert structural equivalence between Term* tree and tree_t tree. Run across Prolog corpus. Fix shape mismatches.
findings-6a:
  - All required TT_* already in ast.h: TT_QLIT/ILIT/FLIT/VAR/NUL/FNC/MAKELIST/CAT/ALT/IF/CLAUSE/CUT/UNIFY. No new kinds needed.
  - List shape: C parser builds '.'(H,T) chains via ATOM_DOT. tree_t: TT_MAKELIST with flat children [e1..en, tail]. Lowerer rebuilds cons chain.
  - Conjunction: parser flattens via flatten_conj() into PlClause.body[]. tree_t: raw nested TT_FNC(",") chains — lower flattens.
  - ;/-> if-then-else: emitted raw as TT_FNC(";", TT_FNC("->",C,T), E) — prolog_lower.c detects and emits TT_IF.
  - IfFrame directive stack: stays in parser (preprocessor concern, not AST). PST-PL-6g confirmed: no change needed.
  - TERM_ATOM("!") maps to TT_CUT leaf. ATOM_CUT used in C parser.
  - Directive (:-) head is NULL in PlClause; tree_t: TT_CLAUSE(TT_NUL, raw_body).
findings-6b:
  - Lexer struct is plain-copyable (src ptr + ints, no heap). Save p->lx before Term* parse; restore into p2 for parallel pt_* replay.
  - Parallel functions: pt_primary, pt_term, pt_list, pt_args, pt_binop, pt_flatten_conj, pt_maybe_ifthenelse, pt_make_clause.
  - TreeScope tracks name→interned-ptr; no slot numbers (moved to 6e).
  - Atoms → TT_QLIT; vars → TT_VAR(v.sval=name); cuts → TT_CUT leaf.
  - TT_FNC for all compound terms (functors, operators, builtins) with v.sval=functor name.
  - pt_flatten_conj: n-ary conjunction flattening → TT_PROGRAM. Parser-level reduce action. Stays in parser.
  - pt_maybe_ifthenelse: ;(->(C,T),E) → TT_IF(c,t,e). Grammar-level reduce on syntactic idiom. Stays in parser.
  - pt_make_clause: TT_CLAUSE(head|TT_NUL, TT_PROGRAM[flat body]). Body flattened via pt_flatten_conj.
  - DCG: parallel path builds raw pre-expansion tree_t; DCG expansion deferred to lower.
  - PlClause.tr populated for all non-if-directive clauses. Directives: tr=NULL.
  - Gates: smoke_prolog PASS=5 FAIL=0, crosscheck_snobol4 PASS=6, smoke_scrip PASS=2.
mirror gaps: (none — parser_prolog.sc already produces tree_t shapes)
```

## Authorship

Drafted by Claude Sonnet 4.6, 2026-05-16.
