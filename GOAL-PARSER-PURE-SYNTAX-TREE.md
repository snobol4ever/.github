# GOAL-PARSER-PURE-SYNTAX-TREE.md — Six Frontends, One Pure tree_t

**Repo:** one4all + .github
**Status:** scoping
**Objective:** Each frontend parser produces a pure syntax tree (`tree_t`) that
corresponds **one-to-one** with the surface syntax of the source language.
**No lowering.** **No desugaring.** **No graph construction.** **No statement
splicing.** **No label generation.** Just the syntax, made of `tree_t` nodes
linked by parent→children. The next stage (`lower`) is responsible for turning
that pure tree into the `IR_t` directed cyclic graph (DCG) with α/β/γ/ω ports.

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

## Step ladder

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

### Step 5 — Rebus rewrite

- [ ] **PST-RB-5a** — Map `REKind` enum values to `TT_*` equivalents. Where a Rebus operator has no direct `tree_t` counterpart, either reuse the nearest (e.g. Rebus arithmetic → `TT_ADD`/`TT_SUB`/...) or add a new `TT_*` kind to `ast.h`.
- [ ] **PST-RB-5b** — Action bodies rewritten to build `tree_t` directly.
- [ ] **PST-RB-5c** — `RExpr`/`RStmt`/`RProgram` and helpers (`rexpr_new`, `SAL`, `EAL`, `STAL`) deleted from `rebus.y` and `rebus.h`.
- [ ] **PST-RB-5d** — Downstream consumers (`rebus_lower.c`, `rebus_emit.c`, `rebus_print.c`) updated to consume `tree_t` instead of `RExpr*`.

Gates: rebus smoke, rebus corpus, scrip_all_modes.

### Step 6 — Prolog rewrite

- [ ] **PST-PL-6a** — Map Prolog constructs to `tree_t` kinds: atom (`TT_QLIT` with sval), variable (`TT_VAR` with sval = name, **no slot**), compound (`TT_FNC` with sval = functor, children = args), list `[…]` (`TT_MAKELIST`), `,` body conjunction (`TT_CAT`), `;` disjunction (`TT_ALT`), `:-` clause (`TT_CLAUSE(head, body)`), `->` if-then, cut `!` (`TT_CUT`), numbers (`TT_ILIT`/`TT_FLIT`).
- [ ] **PST-PL-6b** — Action functions rewritten to build `tree_t`. The `Term` type and `term_new_*` calls disappear from the parser.
- [ ] **PST-PL-6c** — Variable-slot allocation moves to `lower_pl.c`. Parser no longer keeps a `VarScope`.
- [ ] **PST-PL-6d** — Decide whether `IfFrame` directive-stack stays (conditional file inclusion is a preprocessor concern, separable). Likely stays. Document.
- [ ] **PST-PL-6e** — Downstream (`prolog_lower.c`, `prolog_unify.c`, `prolog_builtin.c`) updated to consume `tree_t` rather than `Term*` for source-program clauses. The runtime `Term` machinery is unaffected — that stays as a runtime concept.

Gates: prolog smoke, prolog corpus, scrip_all_modes, Byrd-box prolog gates.

### Step 7 — Cross-frontend invariant tests

- [ ] **PST-INV-7a** — Add `scripts/test_pure_syntax_tree.sh`: for each frontend, parse a representative file, dump the resulting `tree_t` via `ast_print`, and assert: no synthetic label nodes, no statement-list splicing artifacts, no non-`tree_t` types present in the parser's output.
- [ ] **PST-INV-7b** — Add an `ast_verify` mode that walks a `tree_t` and asserts every node kind is justified by the source language's syntax production set (per-language allow-list).
- [ ] **PST-INV-7c** — Add a lint pass over the grammar files (`*.y`) and parser sources (`prolog_parse.c`, `icon_parse.c`) that flags forbidden patterns: `strdup` of label names, `sprintf("L%d", ++counter)`, `clone_*` of expression nodes, anything matching `sc_label_new` / `sc_finalize_*` patterns.

---

## Lower's new responsibilities

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

---

## Done criterion

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
5. `lower` now contains all the desugaring and label-generation logic that
   used to live in the parsers.

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
watermark: Step 0 (diagnosis) ✅
head: .github HEAD = fb24c9d5 (post-BB0 correction)
next: PST-SN4-1a — remove EXPORT/IMPORT special-case from sno4_stmt_commit_go
ladder: SN4 cleanup → Icon/Raku audit → Snocone rewrite → Rebus rewrite → Prolog rewrite → invariants
```

---

## Authorship

Drafted by Claude Opus 4.7, 2026-05-16, session after BB0 correction.
Lon Jones Cherryholmes specified the architecture (pure syntax tree, lower owns
the DCG) and asked for the GOAL file.
