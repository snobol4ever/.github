# GOAL-PARSER-PURE-SYNTAX-TREE.md — Six Frontends, One Pure tree_t

**Repo:** one4all + .github
**Status:** scoping
**Two stages:**

- **Stage 1 (parsers):** every frontend produces a pure `tree_t` syntax tree,
  one-to-one with surface syntax. No lowering, no desugaring, no graph
  construction. Built directly with `tree_t` — no separate intermediate types.
- **Stage 2 (lower):** the single `lower` stage consumes the pure `tree_t` and
  produces `IR_t` — the directed graph with c[] children for the AST skeleton
  and α/β/γ/ω ports for the execution wiring.

```
(source) ──► PARSER ──► (tree_t — pure syntax) ──► LOWER ──► (IR_t — DCG with ports)
```

The only license parsers have to deviate from one-to-one is:

- **Discarding pure layout tokens** that exist solely for grouping or punctuation
  and carry no semantic content. The canonical example: `( x )` — the parentheses
  exist in the parse tree only to disambiguate precedence; they do **not** appear
  in the syntax tree. Same for statement terminators, separators, head/tail
  keyword pairs that bracket a structure, etc.
- **Choosing a node kind for an operator** (e.g. `T_PLUS` token → `TT_ADD` node).
  This is mechanical, not semantic.

Everything else — every rewrite, every introduced node not directly named by the
grammar, every label, every goto chain, every clone of an expression — is a
**violation** and belongs in `lower`.

---

## Why now

The five language frontends arrived at the current shared `tree_t` from very
different starting points. Three of them (SNOBOL4, Icon, Raku) are already
close. Three of them (Snocone, Rebus, Prolog) carry significant historical
deviation:

- **Snocone** desugars `+=`/`-=`/`*=`/etc. at parse time by cloning the LHS into
  the RHS; generates fresh labels via `sc_label_new` for every `if`/`while`/`do`/
  `for`/`switch`/`break`/`continue`; splices synthetic `STMT_t` chains directly
  into the live `CODE_t` statement list; tracks loop frames (`LoopFrame`) and
  pending user-labels mid-parse; and emits gotos as completed statements.
  Essentially the entire control-flow lowering already runs in the parser
  action bodies. (`snocone_parse.y` 1227 lines, 80+ helper references.)
- **Rebus** builds an entirely separate IR (`RProgram`/`RStmt`/`RExpr` /
  `REKind`) that never touches `tree_t`. Zero references to `TT_*` or `tree_t`
  in `rebus.y`. The conversion to `tree_t` happens elsewhere, untraceable from
  the grammar.
- **Prolog** builds yet a third IR (`Term` / `term_new_atom` / `term_new_compound`
  / `term_new_var`) and tracks variable scopes during parsing. Zero references
  to `tree_t` in `prolog_parse.c`. The `if/then/else` directive stack
  (`IF_STACK_MAX`, `IfFrame`) does control-flow logic during parsing.

The result: `lower` is asymmetric across languages. For SNOBOL4 it does real
lowering work; for Snocone it gets pre-lowered input and has nothing left to
do; for Rebus and Prolog there is a hidden conversion stage between parser and
lower that nobody owns. This blocks the goal stated in PLAN.md:

> Every frontend (SNOBOL4, Icon, Prolog, Snocone, Rebus, Scrip) produces the
> shared AST. SM-LOWER compiles the AST to SM_Program …

The shared AST is `tree_t`. Today it is only shared in two-and-a-half of six
cases.

---

## What "pure syntax tree" means, concretely

For every grammar production `LHS → RHS`, the action body either:

1. Returns one of its RHS children unchanged (delegation — e.g. `expr8 : expr9`
   in SNOBOL4), or
2. Allocates **one** new `tree_t` node whose kind names the construct, attaches
   the relevant RHS subtrees as children **in source order**, and returns it.

Allowed in action bodies:
- `ast_node_new(TT_*)` / `expr_new(TT_*)` / `expr_unary` / `expr_binary` / `ast_push` / `expr_add_child`.
- Setting `v.sval`/`v.ival`/`v.dval` from the immediate token value.
- Choosing between flat-list nodes (`ast_push` onto an existing same-kind parent
  for left-associative left-recursive rules) vs. nested binary. **Either is
  fine, as long as no extra semantic work happens.** The current SNOBOL4
  `expr3 T_2PIPE expr4` rule that grows a flat `AST_ALT` list is the model.

Forbidden in action bodies:
- Cloning subtrees (`sc_clone_expr_simple` and friends).
- Allocating labels (`sc_label_new`).
- Allocating and splicing `STMT_t` chains into a global statement list as a
  side effect (`sc_append_stmt`, `sc_splice_after`, `sc_finalize_if_*`,
  `sc_finalize_while`, `sc_finalize_for`, `sc_finalize_switch`,
  `sc_finalize_function`).
- Tracking loop frames or scope state for the purpose of resolving `break` /
  `continue` to labels. The parser may push a tree node `TT_LOOP_BREAK`; it
  must **not** resolve which loop it targets.
- Building any non-`tree_t` IR (Rebus's `RExpr*`, Prolog's `Term*`).
- Variable-slot allocation (`scope_get` in `prolog_parse.c` assigning
  `next_slot++` to each new variable). Slots are a lowering concern.
- Special-casing labels by string (the `EXPORT`/`IMPORT` branches in
  `sno4_stmt_commit_go`).
- Resorting children of a node because the language has positional semantics
  (the `if(!pat && subj && subj->kind==AST_SCAN)` rearrangement near the end
  of `sno4_stmt_commit_go` is borderline — see Step 1 below).

The simplest rule: **if the action body reads or writes anything other than its
own RHS values, it is doing something other than building the syntax tree.**

---

## Scope, per frontend

Diagnosis already completed in the scoping session.

### SNOBOL4 (`src/frontend/snobol4/snobol4.y`) — closest to clean

- ✅ Expression layer (`expr0`..`expr17`) is essentially pure: one node per rule, children in source order.
- ✅ Parentheses dropped on `T_LPAREN expr0 T_RPAREN { $$ = $2; }`.
- ⚠ `sno4_stmt_commit_go` performs three non-trivial transformations on the
  committed statement:
  1. `EXPORT`/`IMPORT` labels intercepted and written to a side table.
  2. If subject is `AST_SCAN(a, b)` and no pattern given, it re-attaches `a` as
     subject and `b` as pattern (re-shuffling syntax for downstream
     convenience).
  3. If subject is `AST_SEQ` whose head is a Var/Keyword/Qlit/Indirect, it
     splits head as subject and tail as pattern.
  These belong in `lower`.
- ⚠ Goto fields are stored as `s->goto_u`/`s->goto_s`/`s->goto_f` raw strings
  on the `STMT_t` rather than as `TT_GOTO_U`/`TT_GOTO_S`/`TT_GOTO_F` children
  of the `TT_STMT` tree node. The pure-tree form would put them on the tree.

### Icon (`src/frontend/icon/icon_parse.c`) — clean

- ✅ Builds `tree_t` directly via `ast_node_new(TT_*)`, `expr_unary`, `expr_binary`.
- ✅ Each Icon construct (`if`, `every`, `while`, `repeat`, `case`, `to`/`to by`)
  maps to one node kind.
- No major violations found in the scoping pass. **Targeted audit only.**

### Raku (`src/frontend/raku/raku.y`) — clean

- ✅ Uses `AST_t` (= `tree_t`) throughout. ~50 references.
- `strip_sigil` and the `ExprList` arglist accumulator are mechanical and OK.
- **Targeted audit only.**

### Snocone (`src/frontend/snocone/snocone_parse.y`) — major rewrite

The parser today performs the entirety of control-flow lowering. Required:

- Replace the `sc_if_head_new` / `sc_finalize_if_*` machinery with a single
  rule that builds `TT_IF` with three children: `cond`, `then-block`,
  `opt-else-block`.
- Replace `sc_while_head_new` / `sc_finalize_while` with `TT_WHILE(cond, body)`.
- Replace `sc_do_head_new` / `sc_finalize_do_while` with a single
  `TT_REPEAT(body, cond)` (or a new `TT_DO_WHILE`).
- Replace `sc_for_head_new` / `sc_finalize_for` with `TT_FOR(init, cond, step, body)`.
- Replace `sc_switch_*` with `TT_CASE(disc, case-list)` where each case is a
  `(value, body)` pair node.
- Replace `sc_append_break` / `sc_append_continue` (which resolve to labels)
  with `TT_LOOP_BREAK` / `TT_LOOP_NEXT` nodes carrying the optional user-label
  string only — **no** resolution.
- Replace `sc_func_head_new` / `sc_finalize_function` with `TT_DEFINE` (or
  reuse an existing kind) carrying name, arglist children, body block.
- Move the augmented-assignment expansions (`+= → ASSIGN(x, ADD(x, e))`) into
  `lower`. The parser emits a single `TT_AUGOP` node tagged with the operator
  enum (`AUGOP_ADD`, etc.) — that enum already exists in `ast.h`.
- Move `sc_split_subject_pattern` (post-parse subject/pattern split for SNOBOL4-style
  scanned statements within Snocone) to `lower`.
- The parser produces a `TT_PROGRAM` whose children are statement-tree
  nodes — **not** a linear `STMT_t` list with goto-and-label statements
  spliced in.
- Remove all per-parse `ScParseState` machinery related to labels, loop frames,
  pending user-labels, switch heads, function heads. The parser state shrinks
  to: the lexer, the file name, the error count.

This is the **bulk of the work** and the heart of the GOAL.

### Rebus (`src/frontend/rebus/rebus.y`) — entire IR replacement

Rebus today builds `RProgram`/`RStmt`/`RExpr` and converts to `tree_t`
elsewhere. The grammar action bodies need to build `tree_t` directly,
matching the pattern used by SNOBOL4 and Icon. Then the `RProgram` types
and `rexpr_new` API are deleted.

### Prolog (`src/frontend/prolog/prolog_parse.c`) — entire IR replacement + slot deferral

Prolog today builds `Term *` and assigns variable slots during parsing
(`scope_get(...)` → `term_new_var(next_slot++)`). The grammar must build
`tree_t` directly: clauses are `TT_CLAUSE(head, body)`, atoms are
`TT_QLIT`/`TT_VAR`, compound terms are a kind like `TT_FNC` with name in
`v.sval` and arg children, the `;` operator is `TT_ALT`, the `,` operator
is `TT_CAT`, `:-` is `TT_CLAUSE`, `->` is its own kind, cut is `TT_CUT`.
Variable-slot allocation moves to `lower`.

The `IfFrame` / `ifst_top` directive-stack logic for conditional file
inclusion is separable; it can stay or move depending on how directives
land elsewhere. **Defer judgment to the rung that touches it.**

---

## Stage 1 step ladder — Parsers

Each step lands a single commit (or a small sequence) and a green build of
the existing test gates. **No new test regressions per step.** When a step
removes desugaring from a parser, the corresponding desugaring is added to
`lower` first (or in the same commit), so end-to-end behavior is preserved.

### Step 0 — Diagnosis ✅ (this document)

- [x] Diagnose each of the six parsers and record findings (above).
- [x] Identify violations per frontend.
- [x] Identify the canonical pure-syntax model (SNOBOL4 expression layer).

### Step 1 — SNOBOL4 cleanup (small, sets the template)

- [ ] **PST-SN4-1a** — Remove EXPORT/IMPORT special-case from `sno4_stmt_commit_go`. Move to a post-parse pass in `lower` or driver.
- [ ] **PST-SN4-1b** — Remove the `AST_SCAN`-unpacking and `AST_SEQ`-splitting subject/pattern rearrangement. Equivalent logic added to `lower`.
- [ ] **PST-SN4-1c** — Lift goto fields (`goto_u`, `goto_s`, `goto_f`, and their `_expr` variants) off `STMT_t` and onto the `TT_STMT` tree as `TT_GOTO_U`/`TT_GOTO_S`/`TT_GOTO_F` children.
- [ ] **PST-SN4-1d** — Document in `snobol4.y` header comment: this grammar is the reference for pure-syntax-tree style. Other frontends should match.

Gates after each rung: scrip_all_modes, smoke_snobol4, broad corpus.

### Step 2 — Icon audit

- [ ] **PST-ICN-2a** — Read `icon_parse.c` in full, list any places building synthetic structure (e.g. the `TT_TO_BY` from a `to ... by ...` rule is fine; a `for` loop secretly expanding into a `(_init; cond; step)` triplet wrapping `IF` and `EVERY` would be a violation). Record findings.
- [ ] **PST-ICN-2b** — If violations found, fix them with same pattern as SNOBOL4.

### Step 3 — Raku audit

- [ ] **PST-RAKU-3a** — Read `raku.y` in full, list any helper that does work beyond node construction. Record findings.
- [ ] **PST-RAKU-3b** — Fix violations if any.

### Step 4 — Snocone rewrite (the big one)

Each sub-step lands the lower-side equivalent first, then strips the
parser-side desugaring.

- [ ] **PST-SC-4a** — Add `lower_snocone.c` (or extend existing lower) handling for `TT_AUGOP`. Run gates. Remove `+=`/`-=`/`*=`/`/=`/`%=`/`^=`/`||=` expansion from the parser; replace with `TT_AUGOP` node. Gates green.
- [ ] **PST-SC-4b** — Lower handles `TT_IF(cond, then, else?)`. Parser replaces `sc_if_head_new` + `sc_finalize_if_no_else`/`sc_finalize_if_else` with single `TT_IF` build. `IfHead` struct deleted.
- [ ] **PST-SC-4c** — Same for `TT_WHILE(cond, body)`. `WhileHead`/`sc_finalize_while` deleted.
- [ ] **PST-SC-4d** — Same for `TT_REPEAT` / do-while. `DoHead`/`sc_finalize_do_while` deleted.
- [ ] **PST-SC-4e** — Same for `TT_FOR(init, cond, step, body)`. `ForHead`/`sc_finalize_for` deleted.
- [ ] **PST-SC-4f** — Same for `TT_CASE` (switch). `SwitchHead`/`CaseEntry`/`sc_finalize_switch` deleted.
- [ ] **PST-SC-4g** — Same for `TT_DEFINE` (function definition). `FuncHead`/`sc_finalize_function` deleted.
- [ ] **PST-SC-4h** — `break` / `continue` build `TT_LOOP_BREAK` / `TT_LOOP_NEXT` carrying optional user-label string. Loop-frame resolution moves to lower. `LoopFrame`/`sc_loop_push`/`sc_loop_pop`/`sc_loop_find_by_user_label` deleted.
- [ ] **PST-SC-4i** — Labels (`label:` form). Parser builds `TT_STMT` with a label attribute or a sibling `TT_GOTO_U` target name; deletes `sc_emit_label_pad` and pending-label tracking.
- [ ] **PST-SC-4j** — `return`/`freturn`/`nreturn` → `TT_RETURN(value?)` and dedicated kinds for the fail/null variants. `sc_append_return`/`sc_append_freturn`/`sc_append_nreturn` deleted.
- [ ] **PST-SC-4k** — `goto LABEL` → `TT_GOTO_U` node. `sc_append_goto_label` deleted.
- [ ] **PST-SC-4l** — `sc_split_subject_pattern` moved to lower.
- [ ] **PST-SC-4m** — Top-level changes: `TT_PROGRAM` is now a tree of nested statement trees (not a flat linear list with synthetic gotos and labels). `sc_append_stmt`/`sc_splice_after`/`sc_make_label_stmt`/`sc_make_goto_uncond_stmt` deleted.
- [ ] **PST-SC-4n** — `ScParseState` shrunk to lexer + filename + error count. Audit complete.

Gates after each rung: snocone_smoke, snocone broad corpus, scrip_all_modes.

### Step 5 — Rebus rewrite (RExpr* → tree_t)

- [ ] **PST-RB-5a** — Map `REKind` enum values to `TT_*` equivalents. Where a Rebus operator has no direct `tree_t` counterpart, either reuse the nearest (e.g. Rebus arithmetic → `TT_ADD`/`TT_SUB`/...) or add a new `TT_*` kind to `ast.h`.
- [ ] **PST-RB-5b** — Action bodies rewritten to build `tree_t` directly.
- [ ] **PST-RB-5c** — `RExpr`/`RStmt`/`RProgram` and helpers (`rexpr_new`, `SAL`, `EAL`, `STAL`) deleted from `rebus.y` and `rebus.h`.
- [ ] **PST-RB-5d** — Downstream consumers (`rebus_lower.c`, `rebus_emit.c`, `rebus_print.c`) updated to consume `tree_t` instead of `RExpr*`.

Gates: rebus smoke, rebus corpus, scrip_all_modes.

### Step 6 — Prolog rewrite (Term* → tree_t)

The Prolog parser today builds a `Term *` IR with `term_new_atom` /
`term_new_compound` / `term_new_var`, and assigns variable slots during
parsing (`scope_get` → `term_new_var(next_slot++)`). The conversion to
`tree_t` must happen, and slot assignment must move to lower.

Term-kind to tree_t-kind mapping:

| Term construct | tree_t kind | Notes |
|---|---|---|
| atom              | `TT_QLIT`     | `v.sval = atom name` |
| integer literal   | `TT_ILIT`     | `v.ival = value` |
| float literal     | `TT_FLIT`     | `v.dval = value` |
| variable          | `TT_VAR`      | `v.sval = name`, **no slot** |
| anonymous var `_` | `TT_VAR`      | `v.sval = "_"` — lower allocates fresh slot |
| compound `f(...)` | `TT_FNC`      | `v.sval = functor name`, `c[] = arg trees` |
| list `[a,b\|t]`   | `TT_MAKELIST` | `c[] = elements followed by optional tail` |
| string `"abc"`    | `TT_QLIT`     | (whichever convention the Prolog dialect chose) |
| `,` conjunction   | `TT_CAT`      | left-associative flat or nested per convention |
| `;` disjunction   | `TT_ALT`      | flat list of branches |
| `->` if-then      | `TT_IF`       | `c[0]=cond, c[1]=then` (no else when used inside `;`) |
| `;` w/ `->` left  | `TT_IF`       | `c[0]=cond, c[1]=then, c[2]=else` |
| `:-` clause       | `TT_CLAUSE`   | `c[0]=head, c[1]=body` |
| `:-` directive    | `TT_CLAUSE`   | `c[0]=NULL or TT_NUL, c[1]=body` (head-less) |
| `!` cut           | `TT_CUT`      | leaf |
| arithmetic `+/-/*` | `TT_ADD/SUB/MUL...` | only when in `is/2` context — let lower decide |

Step-by-step:

- [ ] **PST-PL-6a** — Decide the kind-mapping table above against any
  edge cases in the current corpus (anonymous vars, named numbers,
  special atoms). Add new `TT_*` kinds to `ast.h` only if no good
  reuse exists. Likely no new kinds needed.
- [ ] **PST-PL-6b** — Add a parallel `tree_t`-building code path to
  `prolog_parse.c` alongside the existing `Term *` code. Each parse
  function gets a sibling that returns `tree_t *`. **Both code paths
  active simultaneously during this rung** — provides ground truth.
- [ ] **PST-PL-6c** — Add a verifier: parse a clause both ways, walk
  both representations, assert structural equivalence (atom/var/compound
  identity, child counts, ordering). Run across the Prolog corpus.
- [ ] **PST-PL-6d** — Switch downstream consumers (`prolog_lower.c`,
  `prolog_unify.c`, `prolog_builtin.c`, `prolog_driver.c`) one at a
  time to consume `tree_t` for **source-level** clauses. The runtime
  `Term` machinery is **unaffected** — `Term` remains the runtime
  representation; only its role as parser output is removed.
- [ ] **PST-PL-6e** — Move variable-slot allocation to a pre-lower
  pass in `prolog_lower.c`: walk each clause's `tree_t`, collect every
  `TT_VAR` name into a per-clause table, assign sequential slots, and
  attach the slot to the corresponding `IR_PL_VAR` node's `ival` during
  lowering. The parser keeps **no** scope state.
- [ ] **PST-PL-6f** — Delete the `Term *`-returning code paths from
  `prolog_parse.c`. Delete `scope_get`'s slot-assignment side. The
  `VarScope` may shrink to a name-set or disappear entirely.
- [ ] **PST-PL-6g** — Decide whether the `IfFrame` directive-stack
  (conditional file inclusion) stays in the parser. It is separable;
  likely stays as a preprocessor concern. Document the decision.

Gates: prolog smoke, prolog corpus, scrip_all_modes, Byrd-box prolog
gates (Prolog BB JCON / Prolog BB Byrd).

### Step 7 — Cross-frontend invariant tests

- [ ] **PST-INV-7a** — Add `scripts/test_pure_syntax_tree.sh`: for each frontend, parse a representative file, dump the resulting `tree_t` via `ast_print`, and assert: no synthetic label nodes, no statement-list splicing artifacts, no non-`tree_t` types present in the parser's output.
- [ ] **PST-INV-7b** — Add an `ast_verify` mode that walks a `tree_t` and asserts every node kind is justified by the source language's syntax production set (per-language allow-list).
- [ ] **PST-INV-7c** — Add a lint pass over the grammar files (`*.y`) and parser sources (`prolog_parse.c`, `icon_parse.c`) that flags forbidden patterns: `strdup` of label names, `sprintf("L%d", ++counter)`, `clone_*` of expression nodes, anything matching `sc_label_new` / `sc_finalize_*` patterns.

---

## Lower's new responsibilities (Stage 1 summary)

Everything stripped from parsers lands here. The catalog:

- **Augmented assignment** (`TT_AUGOP` with `AUGOP_*` enum) → expand to the
  natural `TT_ASSIGN(lhs, TT_<op>(lhs, rhs))` form, cloning `lhs` once.
- **Control flow → labels and gotos**: `TT_IF`, `TT_WHILE`, `TT_REPEAT`,
  `TT_FOR`, `TT_CASE` expand into IR_t graphs with α/β/γ/ω wiring.
- **Break/continue resolution**: walk the surrounding loop context; the parser
  no longer pre-resolves which loop is the target.
- **SNOBOL4 subject/pattern split**: when a SNOBOL4 statement's subject parses
  as `EXPR ? PAT` (`AST_SCAN`) or as `VAR EXPR…` (`AST_SEQ` with head being a
  Var/Keyword/Qlit/Indirect), split into subject and pattern in lower.
- **Goto fields onto tree**: lower reads `TT_GOTO_U`/`TT_GOTO_S`/`TT_GOTO_F`
  children of `TT_STMT` rather than `STMT_t` string fields.
- **Prolog variable slot allocation**: per-clause scope assigning each named
  variable an integer slot.
- **EXPORT/IMPORT**: walk `TT_PROGRAM` looking for the labeled statements;
  populate the export/import side tables.

`lower` is the right home for all of this. It is where `IR_t` is built, where
`IR_alloc`/`IR_node_alloc` live, where the Byrd-box port wiring happens.

The Stage 2 design below specifies how lower builds `IR_t` from `tree_t`.

---

## Stage 1 done criterion

1. Every parser action body either (a) returns one RHS child unchanged, or (b)
   calls `ast_node_new` / `expr_new` / `expr_unary` / `expr_binary` / `ast_push`
   / `expr_add_child` and returns the new `tree_t` node. No other side
   effects. No other allocations of node-like types.
2. The grammar files (`snobol4.y`, `snocone_parse.y`, `rebus.y`, `raku.y`)
   and the hand-written parsers (`icon_parse.c`, `prolog_parse.c`) all build
   only `tree_t` nodes. The types `RExpr`/`RStmt`/`RProgram` (Rebus) and the
   `Term` type used as a parser-output type (Prolog) are gone — at least from
   the parser. (`Term` remains as a Prolog runtime concept; only its use as
   parser output is removed.)
3. All existing test gates green: smoke for every frontend, scrip_all_modes,
   broad corpus, broker, Byrd-box gates, NEW pure-syntax-tree invariant
   gates from Step 7.
4. Beauty self-host still byte-identical (Milestone 1 not broken).

---

# STAGE 2 — Lower: from pure tree_t to IR_t (SM + BB)

Stage 1 (above) gets parsers right. Stage 2 designs and implements `lower`,
which consumes the pure `tree_t` and produces `IR_t` — the directed graph
that the interpreter and the native-code emitters share.

## The dual-nature design challenge

`IR_t` already has two ways of pointing at neighbors:

```c
struct IR_t {
    IR_e t;                         /* node kind                                 */
    IR_t *α, *β, *γ, *ω;            /* Byrd-box ports — control wiring           */
    IR_t **c;  int n;               /* children — operand / body skeleton        */
    ...                             /* value slots: ival/dval/sval, opaque, etc. */
};
```

The question raised in design: **the SM is a tree; the BB is a 4-port graph
with one edge per (node, port). How do they coexist in one IR_t?**

### Resolution

The two are **orthogonal axes of the same node**:

| Axis | What it expresses | When used |
|---|---|---|
| `c[]/n` children | **Abstract syntax skeleton** — what the program *says* | Always populated for compound nodes |
| `α/β/γ/ω` ports | **Control wiring** — where execution *goes* | Populated for nodes that participate in BB-style backtracking |

For nodes that produce a single deterministic value (e.g. `IR_LIT_I`,
`IR_ASSIGN(x, ADD(y,z))`), the BB wiring degenerates to: `α = self`,
`γ = next-in-sequence`, `ω = fail-out`, `β = ω`. The same backtracking
machinery walks both kinds without a special case — deterministic nodes
just never schedule a retry.

For pure pattern operators (`IR_PAT_LIT`, `IR_PAT_ARB`, etc.), the children
are typically empty (`n = 0`) and all four ports are populated — exactly
what `lower_pat_dcg.c` already does today.

For compound nodes that mix both (e.g. `IR_PL_CALL` of a Prolog predicate
that itself contains a `;` disjunction), children carry the static syntax
(c[0]=functor-name, c[1..]=args), and ports carry the dynamic wiring (γ to
next-on-success which is the next conjunct, ω to next-on-fail which is the
backtrack target).

**One edge per (source-node, port).** Not two. The target node does not
carry a back-pointer to the source. Backtracking-cycles are represented
by some downstream port pointing back upstream — that's a real cycle in
the directed graph, just expressed as `node_B->β = node_A` (single edge).

### The "tree-vs-graph" duality, made precise

Reading down `c[]` from `cfg->entry` recursively gives you the **AST-shaped
skeleton** (tree-shaped — no cycles, no shared subtrees in practice).
Reading `α/β/γ/ω` and following whichever port is "next" gives you the
**execution trajectory** (graph-shaped — cyclic for backtracking).

The interpreter walks the port edges. The emitters walk the children to
generate the instruction stream and walk the ports to generate the branch
targets.

### JCON's IR confirms the "single edge per labeled port" model

The reference Java implementation of Icon — JCON (Townsend & Proebsting,
1999, code archived) — uses exactly this discipline. Inspected
`jcon-master/tran/ir.icn` (48 lines) and `irgen.icn` (1559 lines):

**Every JCON IR record carries at most one extra edge as a labeled field:**

```icon
record ir_Field      (coord, lhs, expr, field,         failLabel)
record ir_OpFunction (coord, lhs, fn, argList,         failLabel)
record ir_Call       (coord, lhs, fn, argList,         failLabel)
record ir_ResumeValue(coord, lhs, value,               failLabel)
record ir_Key        (coord, lhs, name,                failLabel)
record ir_Goto       (coord, targetLabel)
record ir_Succeed    (coord, expr, resumeLabel)
record ir_CoRet      (coord, value, resumeLabel)
record ir_EnterInit  (coord, startLabel)
```

Operations that **cannot fail** (`ir_Move`, `ir_MoveLabel`, `ir_Deref`,
`ir_Assign`, `ir_MakeList`, `ir_IntLit`, `ir_StrLit`, ...) carry **no
control edge at all** — they fall through to the next instruction in the
same `ir_chunk`. Operations that **can fail** carry exactly one extra
named edge (`failLabel`, or for suspend-style ops, `resumeLabel`).

Per AST node, JCON allocates a 4-label **interface block** —
`ir_info(start, resume, failure, success)` — declared in
`irgen.icn` line 10. That structure looks like our α/β/γ/ω port set, but
its role is different:

- The 4-label `ir_info` is **per AST node** (each parse-tree node gets
  one block of four entry/exit labels).
- The single `failLabel` / `resumeLabel` is **per instruction** (one
  outgoing edge from one node).

This is the model. **Per-node ports vs per-instruction edges.** And in
both cases — JCON or our IR — there is **never more than one outgoing
edge per (node, port-name)**.

**JCON has no 2-edge BB pattern.** Even where backtracking happens (alt
exhaustion, generator resumption), the wiring is always a single edge
labeled by its role. The "graph" emerges because multiple nodes' single
edges can converge on the same target, and back-edges form natural cycles.

The dot-export tool (`gen_dot.icn`) makes this concrete: it walks the
emitted instruction list and writes one `A -> B [label="failure"]` edge
per failure-carrying instruction, one `A -> B [label="resumeLabel"]` per
suspend. No instruction emits two parallel edges to the same neighbor.
The 4-port-per-AST-node and the single-edge-per-instruction live happily
together with no contradiction.

**Conclusion for our design:** the same is true in our IR_t. The four
`α/β/γ/ω` are four *named ports*, each holding one edge. They are not
"four edges between two nodes." A node that uses only `γ` (forward
control) is degenerately fine; a pattern node that uses all four is also
fine. Tree-shaped programs naturally use just `γ` (and ω for fail-out);
backtracking-shaped subgraphs use the full set. The IR switches mode
based on node kind — no representational change needed.

## Worked examples

### Example 1 — SNOBOL4 `X = 5`

Pure tree_t after Stage 1:

```
TT_STMT
└── TT_ASSIGN
    ├── TT_VAR "X"
    └── TT_ILIT 5
```

Lowered IR_t (one block, three nodes):

```
[entry → n0]

  n0: IR_LIT_I (ival=5)        children: []           α=n0  β=n2  γ=n1  ω=n2
  n1: IR_ASSIGN                children: [VAR("X")]   α=n1  β=n2  γ=n2  ω=n2
  n2: (HALT/success sentinel)
```

The `c[]` children of n1 carry the LHS name (a small leaf IR_VAR with
`sval="X"`). The port wiring threads n0 → n1 → halt. Pure tree on the
syntactic side; pure linear graph on the execution side, all in one
data structure.

### Example 2 — SNOBOL4 `S "hello" :S(DONE)`

(Pattern-match S against "hello", on success goto DONE.)

Pure tree_t:

```
TT_STMT
├── TT_SCAN
│   ├── TT_VAR "S"
│   └── TT_QLIT "hello"
├── TT_GOTO_S
│   └── TT_QLIT "DONE"
```

Lowered IR_t:

```
[entry → n0]

  n0: IR_VAR "S"               c:[]    α=n0  γ=n1     ω=fail
  n1: IR_SCAN                  c:[n0]  α=n2  γ=n3     ω=fail
  n2: IR_PAT_LIT "hello"       c:[]    α=n2  β=fail  γ=n3 (scan-success)  ω=fail
  n3: IR_GOTO sval="DONE"      α=n3  γ=halt           ω=halt
```

The pattern subgraph (just n2) is wired through n1's `α` port. On success,
n2's `γ` returns control to whatever follows the SCAN — here n3. On
failure, n2's `ω` falls out to the statement-level fail-out. This is the
same wiring `lower_pat_dcg.c` builds today.

### Example 3 — SNOBOL4 `LOOP X = X + 1 :(LOOP)`

(Unconditional goto-LOOP after add.)

Pure tree_t:

```
TT_STMT label="LOOP"
├── TT_ASSIGN
│   ├── TT_VAR "X"
│   └── TT_ADD
│       ├── TT_VAR "X"
│       └── TT_ILIT 1
├── TT_GOTO_U
│   └── TT_QLIT "LOOP"
```

Lowered IR_t:

```
[entry → n0 (labeled "LOOP")]

  n0: IR_VAR "X"               c:[]                    γ=n1    ω=fail
  n1: IR_LIT_I 1               c:[]                    γ=n2    ω=fail
  n2: IR_BINOP "+"             c:[]                    γ=n3    ω=fail
  n3: IR_ASSIGN                c:[VAR("X")]            γ=n4    ω=fail
  n4: IR_GOTO sval="LOOP"      γ=n0  (the back-edge — graph cycle)
```

`n4->γ = n0` is the **single back-edge** that makes this a cyclic
directed graph. There is no `n0->predecessor` field — n0 doesn't know n4
points at it. The cycle exists in the graph; no bookkeeping in the
target.

### Example 4 — Prolog `parent(tom, X).`

(Query: find X such that parent(tom, X).)

Pure tree_t after Stage 1 (no slot numbers — those come from lower):

```
TT_FNC "parent"
├── TT_QLIT "tom"        // atom
└── TT_VAR "X"           // unbound var
```

Lower assigns var slots (`X → slot 0`) and emits:

```
[entry → n0]

  n0: IR_PL_CHOICE                 (push choice point)
       c:[clause0_entry, clause1_entry, ...]   α=n0  γ=n1  ω=fail-out

  n1: IR_PL_CALL "parent"           c:[atom-tom, var-slot-0]
       (built-in dispatch happens through the choice point's α)
       γ=success-continuation  ω=n0->next-clause
```

Children carry the syntactic structure (the call's name and arg list).
Ports carry the backtracking — on fail, control flows to the choice
point's next alternative, which is a graph edge into another clause head.

### Example 5 — Icon `every i := 1 to 10 do write(i)`

Pure tree_t (using existing kinds):

```
TT_EVERY
└── TT_ITERATE
    ├── TT_ASSIGN
    │   ├── TT_VAR "i"
    │   └── TT_TO_BY
    │       ├── TT_ILIT 1
    │       ├── TT_ILIT 10
    │       └── (implicit step=1 elided OR explicit TT_ILIT 1)
    └── TT_FNC "write"
        └── TT_VAR "i"
```

Lower wires a generator-loop:

```
  gen: IR_ICN_TO_BY               opaque=range state(1,10,1)
                                  α=gen  γ=body-α   ω=loop-exit

  body0: IR_ASSIGN                c:[VAR("i")]      γ=body1   ω=back-to-gen

  body1: IR_CALL "write"          c:[VAR("i")]      γ=back-to-gen
                                                    (gen's resume)
```

Every iteration: gen advances → body executes → control returns to gen's
`γ` resume edge → gen advances → ... until gen's pool exhausted, then
control flows out gen's `ω`. Single edges in each direction; cycles
naturally form between gen and body.

### Example 6 — Snocone `if (x < 5) { y = 1; } else { y = 2; }`

Pure tree_t (after Stage 1 — single TT_IF node, no labels):

```
TT_IF
├── TT_LT                  // cond
│   ├── TT_VAR "x"
│   └── TT_ILIT 5
├── TT_PROGRAM             // then-block
│   └── TT_STMT
│       └── TT_ASSIGN [VAR("y"), ILIT(1)]
└── TT_PROGRAM             // else-block
    └── TT_STMT
        └── TT_ASSIGN [VAR("y"), ILIT(2)]
```

Lower expands to labels + gotos as IR_t edges:

```
  cmp:  IR_BINOP "<"        c:[VAR("x"), ILIT(5)]    γ=br   ω=fail
  br:   IR_IF               γ=then-entry  ω=else-entry  (both = single edges)

  t0: ... then body ...      → goto join via γ
  e0: ... else body ...      → goto join via γ
  join: (next stmt)
```

No label strings exist after lowering. The "label" is just the identity
of the IR_t node that some other node's γ port points to.

## Design summary

| Concern | Where it lives |
|---|---|
| Surface syntax (parens, keywords, source-order) | Stage 1: pure tree_t |
| Compound-node operand skeleton                  | Stage 2: IR_t.c[] children |
| Sequential control flow                          | Stage 2: IR_t.γ port |
| Failure / backtracking                          | Stage 2: IR_t.ω, β ports |
| Self-loop (e.g. pattern retry)                  | Stage 2: IR_t.α = self  |
| Static labels / goto target strings             | Stage 2: collapsed into edges; no strings survive |
| Pattern subgraphs                                | Stage 2: full 4-port wiring (existing lower_pat_dcg) |
| Generators (Icon, Prolog)                        | Stage 2: opaque state + γ/ω ports for resume/fail |
| Loops (while/for/repeat)                         | Stage 2: γ-back-edge to head, ω forward-edge to exit |
| Procedure / clause calls                         | Stage 2: c[] for arg evaluation, γ to continuation |

**Net:** the tree-vs-graph tension dissolves. The same `IR_t` struct
serves both roles by populating different fields. The syntactic skeleton
walks via `c[]`. The execution graph walks via `α/β/γ/ω`. Single edges
throughout (no back-pointers). Cycles exist for loops, backtracking, and
pattern retry — and that is exactly what "directed cyclic graph" means.

### Mapping to JCON terminology

For anyone cross-referencing with JCON's `tran/ir.icn` and `tran/irgen.icn`:

| Our IR_t concept              | JCON equivalent                                |
|-------------------------------|------------------------------------------------|
| `IR_t` struct                 | `ir_*` record (one per instruction kind)       |
| `c[]/n` children              | record fields holding operand nodes (`expr`, `argList`) |
| α/β/γ/ω ports (per AST node)  | `ir_info(start, resume, failure, success)`     |
| Single edge per port          | per-instruction `failLabel` / `resumeLabel`    |
| `cfg->entry`                  | `codeStart` field of `ir_Function`             |
| Fall-through (deterministic)  | no label field — next insn in same `ir_chunk`  |
| Goto edge                     | `ir_Goto(targetLabel)`                         |
| Pattern subgraph              | (Icon has no patterns — N/A; SNOBOL4 specific) |

JCON groups instructions into `ir_chunk(label, insnList)` — a labeled
straight-line basic block. Our IR_t flattens that: each node carries its
own port wiring rather than relying on a containing chunk's position.
Same execution semantics; different layout choice.

## Stage 2 step ladder — Lower

- [ ] **PST-LR-1** — Audit current `lower.c` against new pure-tree input.
  Identify call sites that depend on parser-side desugaring (e.g. expect
  `STMT_t.goto_u` string instead of a child `TT_GOTO_U` tree node).
  Catalog them.
- [ ] **PST-LR-2** — Add new lowering passes for the constructs that
  Stage 1 *removed* from parsers:
    - [ ] PST-LR-2a — `TT_AUGOP` → `IR_ASSIGN(lhs, IR_BINOP(lhs', rhs))` with proper lhs duplication policy.
    - [ ] PST-LR-2b — `TT_IF` → cmp / br / then-entry / else-entry / join wiring.
    - [ ] PST-LR-2c — `TT_WHILE`/`TT_REPEAT`/`TT_UNTIL` → head/back-edge/exit.
    - [ ] PST-LR-2d — `TT_FOR(init, cond, step, body)` → init → head → cond → body → step → back-to-head.
    - [ ] PST-LR-2e — `TT_CASE` → cascade of compare-and-branch or jump-table (lower's choice).
    - [ ] PST-LR-2f — `TT_LOOP_BREAK` / `TT_LOOP_NEXT` → resolved against the innermost matching enclosing loop in the lowering walk.
    - [ ] PST-LR-2g — `TT_DEFINE` (Snocone function) → `IR_PROC` node with c[] = params, body lowered into a subgraph.
    - [ ] PST-LR-2h — SNOBOL4 subject/pattern split (the SCAN/SEQ rearrangement removed from parser).
    - [ ] PST-LR-2i — `TT_GOTO_U/S/F` children of `TT_STMT` → resolved to IR_t edges (γ/ω depending on success/fail/unconditional).
- [ ] **PST-LR-3** — Prolog variable-slot allocation moved from parser to a
  per-clause pre-lower pass: walk the clause's tree_t, collect every
  `TT_VAR sval`, assign sequential slots, attach the slot index to the
  corresponding `IR_PL_VAR` node's `ival`.
- [ ] **PST-LR-4** — Rebus lowering (currently thin) grows to handle
  tree_t input (replacing the old RExpr-consuming code path). Audit
  `rebus_lower.c` for what it must add.
- [ ] **PST-LR-5** — Cross-language audit: every front-end's lowered IR
  obeys the invariants below.

## IR_t invariants (Stage 2 lower-side contract)

After lower completes:

1. **Every IR_t with non-zero c[]/n carries valid children of declared kind**
   (e.g. an `IR_ASSIGN` always has `c[0]` being the lhs descriptor — typically
   `IR_VAR` or `IR_INDIRECT` — and the rhs comes from γ-chain evaluation).
2. **Every IR_t carries an ω port** (the fail-out). For deterministic nodes
   the ω points at the statement-level fail-out target. ω is never NULL in
   a completed graph.
3. **Every IR_t that can succeed carries a γ port** to the next-on-success
   target. Some terminal nodes (e.g. `IR_RETURN`) lack a γ.
4. **No node carries a label *string* as a control-flow target.** Labels are
   collapsed to edges. The only `sval` survivors are names of variables,
   atoms, builtins, and string literals (which are values, not jump targets).
5. **Cycles exist only via ports**, never via c[]. The c[] skeleton is a
   forest of trees; the port wiring is the directed cyclic graph.
6. **Block entry**: `cfg->entry` is the node where execution begins.
   `cfg->all[]` is the flat node table (existing convention from
   `IR_alloc` / `IR_node_alloc`).

## Stage 2 done criterion

1. `lower` produces `IR_t` from pure `tree_t` for all six languages.
2. The interpreter (`ir_exec.c`) runs the new IR with same outputs as today
   (broad corpus pass-counts ≥ current head).
3. Beauty self-host byte-identical (Milestone 1 protected).
4. The native emitters (x86, JVM, JS, .NET, WASM) consume the new IR with
   no regression in their corpus pass-counts.
5. All `tree_t` → `IR_t` lowering documented in per-construct comments in
   `lower.c` / `lower_*.c` so the design above is checkable from the code.

---

## Risks and mitigations

- **Beauty self-host regression.** Snocone changes are deep. Stage gate:
  every PST-SC-4* rung must pass `scripts/test_beauty_self_host_smoke.sh`
  (or whichever script covers Milestone 1) before commit.
- **Lower bloat.** `lower.c` is already large. Open new files for major
  pieces (`lower_snocone_ctrl.c` for Snocone control flow, `lower_pl_clause.c`
  for Prolog slot allocation) rather than piling on.
- **Rebus has no lower today** — `rebus_lower.c` exists but is thin. Step 5
  will grow it. Budget for that.
- **Prolog parser shares scope state with lookahead.** Carefully preserve
  the variable-name → identity correspondence across a clause; just don't
  assign slots in the parser. The lookup table stays; only the slot
  numbering moves to lower.

---

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
bash /home/claude/one4all/scripts/build_spitbol_oracle.sh
bash /home/claude/one4all/scripts/build_csnobol4_oracle.sh
```

For Step 4 (Snocone) and Step 7 (invariant tests), also build the
snocone smoke harness:

```bash
bash /home/claude/one4all/scripts/build_snocone_smoke.sh   # (verify path)
```

---

## State

```
watermark: Stage 1 Step 0 (parser diagnosis) ✅
           Stage 2 design ✅ (six worked examples; IR_t dual-axis resolution)
head: .github HEAD = 50293f9f (initial GOAL landed)
next: PST-SN4-1a — remove EXPORT/IMPORT special-case from sno4_stmt_commit_go
ladder Stage 1: SN4 cleanup → Icon/Raku audit → Snocone rewrite → Rebus → Prolog → invariants
ladder Stage 2: lower audit → per-construct passes (AUGOP/IF/WHILE/FOR/CASE/BREAK/DEFINE/SCAN-split/GOTO) → Prolog slots → Rebus lower → cross-lang audit
```

---

## Authorship

Drafted by Claude Opus 4.7, 2026-05-16, session after BB0 correction.
Stage 2 design added same session, after Lon raised the SM-tree vs BB-graph
question. JCON cross-reference added after Lon supplied the JCON tarball
to confirm the single-edge-per-port model. Lon specified the architecture
(pure syntax tree, lower owns the DCG, dual-nature `IR_t` carrying c[]
skeleton + α/β/γ/ω execution ports) and asked for the worked examples.
