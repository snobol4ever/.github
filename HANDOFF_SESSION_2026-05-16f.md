# HANDOFF — Session 2026-05-16f

**Goal:** PST-REBUS-PROLOG  
**Team:** Lon Jones Cherryholmes · Claude Sonnet 4.6

---

## What was done this session

### PST-RB-5c — Delete old RExpr/RStmt structs and helpers
- `rebus.h`: deleted `REKind` enum (44 values), `RExpr` struct, `RSKind` enum,
  `RStmt` struct, `rexpr_new`, `rstmt_new`. Stripped old `guard`/`body` fields
  from `RCase`; stripped old `initial`/`body` fields from `RDecl`.
  `SAL`/`TAL` helpers, `RCase`, `RDecl`, `RProgram`, `rdecl_new`, `rcase_new` all remain.
- `rebus_lower.c`: deleted `lower_expr(RExpr*)` and `lower_stmt(RStmt*)` (~350 lines).
  `lower_tree_expr` / `lower_tree_stmt` is the sole lowering path.
- `rebus_print.c`: full rewrite walking `tree_t` via `body_tree`/`initial_tree`.
- `rebus_emit.c`: old `RExpr`/`RStmt` emitter deleted.

### PST-RB-5d — rebus_emit.c rewritten to walk tree_t
- `rebus_emit.c`: full rewrite emitting SNOBOL4 syntax from `tree_t` nodes
  via `t->t`/`c[]`. Matches semantics of the old `RExpr`/`RStmt` emitter.
  (Note: `rebus_emit` is only used by the standalone `rebus_main.c` CLI —
  the scrip pipeline goes through `rebus_compile` → `rebus_lower` → `code_to_ast`.)

**one4all commit:** `8cdadc6d`

### PST-PL-6a — Prolog kind-mapping verified (no code changes)
Read `prolog_parse.c` (857 lines) and `corpus/SCRIP/parser_prolog.sc` (1040 lines) in full.

**Findings:**
- All required `TT_*` already exist in `ast.h`. **Zero new kinds needed.**
- Full verified mapping: `TERM_ATOM` → `TT_QLIT`, `TERM_INT` → `TT_ILIT`,
  `TERM_FLOAT` → `TT_FLIT`, `TERM_VAR` → `TT_VAR` (no slot in tree_t),
  `TERM_COMPOUND f/n` → `TT_FNC`, list `'.'(H,T)` chains → `TT_MAKELIST` flat,
  `,` conjunction → `TT_PROGRAM` flat children, `;` → `TT_ALT`,
  `->` → `TT_IF`, `;`/`->` if-then-else → `TT_IF(c,t,e)` via pattern-match,
  `:-` clause → `TT_CLAUSE`, `:-` directive → `TT_CLAUSE(TT_NUL, body)`,
  `!` → `TT_CUT` leaf.
- **List shape decision:** `TT_MAKELIST` with flat children `[e1..en, tail]`.
  Lowerer rebuilds `'.'(H,T)` cons chain.
- **Conjunction decision:** `flatten_conj()` output → `TT_PROGRAM` flat children
  (not nested `TT_CAT`).
- **`;`/`->` pattern:** C parser produces `';'('->'(Cond,Then),Else)`.
  6b must detect this shape and emit `TT_IF(cond,then,else)`.
- **`IfFrame` directive stack:** stays in parser. PST-PL-6g confirmed: no AST
  equivalent, `try_handle_if_directive()` is pure parse-time preprocessing.
- **Directive:** `cl->head == NULL` → `TT_CLAUSE(TT_NUL, body)`.

**`.github` commit:** `3fb2da5e`

---

## Gate baselines (end of session)

| Gate | Result |
|------|--------|
| `test_smoke_rebus.sh` | **4/4 PASS** |
| `test_smoke_prolog.sh` | 4/5 (clause known pre-existing fail, unchanged) |
| `test_crosscheck_snobol4.sh` | **6/6 PASS** |

---

## Next step: PST-PL-6b

Add parallel `tree_t`-building code path alongside existing `Term*` code in
`prolog_parse.c`. Both paths active simultaneously. The parser builds both
`Term*` (old) and `tree_t` (new) for the same input, stored on `PlClause`:

**Suggested `PlClause` extension:**
```c
struct PlClause {
    Term     *head;      /* old path */
    Term    **body;      /* old path */
    int       nbody;
    int       lineno;
    PlClause *next;
    tree_t   *head_tree; /* PST-PL-6b: new path */
    tree_t   *body_tree; /* PST-PL-6b: TT_PROGRAM with flat children */
};
```

**Key translation sites in `prolog_parse.c`:**
- `parse_primary()` → for each Term-building site, also build `tree_t`
- `parse_list()` → `TT_MAKELIST` flat
- `parse_term()` / `find_binop()` → `,`→`TT_PROGRAM`, `;`→`TT_ALT`, `:-`→`TT_CLAUSE`,
  `->` and `;`/`->` → `TT_IF`
- `parse_clause()` → populate `head_tree` and `body_tree`
- `scope_get()` → **do not assign slot** in tree_t path; `TT_VAR(v.sval=name)` only
- SCRIP mirror: `parser_prolog.sc` already produces `tree_t` shape; verify alignment.

Gates per rung: `smoke_prolog`, `crosscheck_prolog`, `smoke_scrip_all_modes`,
`crosscheck_snobol4`.

---

## Repo state

| Repo | Branch | HEAD |
|------|--------|------|
| one4all | main | `8cdadc6d` |
| .github | main | `3fb2da5e` |
| corpus | main | unchanged this session |
