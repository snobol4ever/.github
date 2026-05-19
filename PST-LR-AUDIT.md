# PST-LR-AUDIT.md — Per-Production Left-to-Right Child Order Audit

**Goal:** for every `parser_*.{y,c}` in the codebase, enumerate every grammar
production that produces a `tree_t` node, list the resulting **parent kind**
and its **children in the order they appear in the produced node's `c[]`
array**, and flag any production where that order does not match the
left-to-right source token order.

## ⛔ Scope — the rules being enforced

This audit enforces **only** the three rules stated in
`GOAL-PARSER-PURE-SYNTAX-TREE.md § "⛔ Left-to-right child order"`:

1. **L→R child order.** Children of every node appear in the same
   left-to-right order in which their source tokens are read.
2. **No mutate-prior-in-place.** A reduce that wraps prior values into a
   new node must always build a fresh node — it must not mutate a
   previously-built child node by appending into it. (Right-leaning binary
   chains are correct and accepted; flat n-ary forms can be reconstructed
   downstream by `lower` or a tree pass.)
3. **No source token lifted OUT of the tree.** Every value-bearing source
   token must have a tree analog — as a child node, or contributing to a
   leaf's `v.sval`/`v.ival`/`v.dval`. Decoding multiple source tokens into
   a single leaf's value (e.g. `$IDENT` → `TT_QLIT("$IDENT")`) is **value
   decoding and is allowed**. What is forbidden is the token leaving the
   tree entirely: synthesized into a sibling statement that was not in the
   source, lifted into a `STMT_t` string field instead of a tree child,
   minted by the parser from non-source state (e.g. `_Lend_NNNN` labels).

**Rule 2 applies to trees, not values.** Mutating a previously-built tree
node (changing its `t`/`n`/`c[]`) is forbidden. Setting `v.sval`/`v.ival`/
`v.dval` from one or more source tokens during the construction of a fresh
leaf is **value decoding** and is allowed.

**A parser node built from N source positions is fine.** `TT_SCAN(subj,
pat)` produced for `subj ? pat` is **correct**: fresh wrap, children in
L→R source order, ready for shift/reduce. The fact that some consumer
later reads TT_SCAN's two children separately is a property of the
consumer, not a parser-side violation. The parser is allowed to build any
N-ary node that respects the three rules above.

**Explicitly NOT enforced** (these are the parser's free choices, not §⛔
violations):

- **TT_* kind selection.** The parser may pick any `tree_e` kind it likes
  for an operator or keyword. Using `TT_POW` for unary `!`, `TT_MUL` for
  `#`, `TT_DIV` for both `/` (binary) and `/x` (unary), or `TT_NUL` for both
  empty tuples and exprlist containers, is **not** a violation. Downstream
  `lower.c` interprets kinds.
- **Cross-frontend convention uniformity.** Icon's `TT_STMT` shape may
  differ from `stmt_to_ast`'s `TT_STMT` shape; one frontend may put a name
  in `v.sval` and another may put it in `c[0]`; one frontend may use a
  `TT_NUL` placeholder for `default:` and another may use position. Each
  frontend's children just have to be L→R from that frontend's source-
  token sequence.
- **Parser-side semantic dispatch by identifier text.** `pat_prim_kind`
  picking `TT_ANY`/`TT_SPAN`/… vs `TT_FNC` based on the identifier name is
  the parser "choosing a node kind for an operator" — explicitly permitted.

This is the prerequisite the session 4 (2026-05-18) handoff said was
incomplete. The table is built in scans, one frontend at a time. The
audit was originally written with a wider scope (flagging kind-reuse,
convention divergence, and semantic-dispatch as violations) and rescoped
2026-05-19 against this stricter rule list. Withdrawn flags are recorded
per-scan so the reasoning is visible.

Legend for each row:

| Column          | Meaning                                                    |
|-----------------|------------------------------------------------------------|
| **Loc**         | line in `.y` / `.c`                                        |
| **Production**  | LHS : RHS (RHS shows only the value-bearing pieces in order) |
| **Parent kind** | `tree_t.t` of the node produced                           |
| **Children L→R**| children in the order they appear in the result `c[]`     |
| **L→R OK?**     | ✅ matches source token order, ❌ does not, ⚠ structural/non-leaf |
| **Notes**       | helpers called, mutations, subtleties                     |

A child written `〈$N〉` means "the value reduced from RHS slot N, used
unchanged." Tokens with no `<expr>` type (e.g. `T_PLUS`, `T_LBRACE`, etc.)
contribute nothing to the resulting tree and so do not appear under
"Children L→R". A row whose action just passes a single RHS slot through
(`$$ = $1` etc.) does not appear at all — those productions build no node.

---

## SCAN 1 — Snocone (`src/frontend/snocone/snocone_parse.y`)

### 1.1 Grammar productions that build `tree_t` directly (in-line actions)

| Loc | Production | Parent kind | Children L→R | L→R OK? | Notes |
|-----|------------|-------------|--------------|---------|-------|
| 389–394 | `simple_stmt : T_RETURN expr0 T_SEMICOLON` (when inside func) | (two statements appended) `TT_ASSIGN` then `TT_RETURN` | `TT_ASSIGN(TT_VAR(func_name), 〈$2〉)`, then bare `TT_RETURN` | ⚠ | Action splits one source phrase `return EXPR;` into two stmts: an assign `func = EXPR` then a return. The `TT_ASSIGN`'s children are (lhs func-name, rhs $2) — LHS does **not** appear as a source token at all (it's synthesized from `st->cur_func_name`). This is a parser-side lowering — flagged for `PST-SC` review under the same family as `sno4_stmt_commit_go` mutations. |
| 389–394 | (same) when **not** inside func | `TT_RETURN` | (none — bare TT_RETURN appended *after* a stmt containing `$2`) | ⚠ | `sc_append_stmt(st, $2)` then `sc_append_stmt(st, TT_RETURN)`. Two stmts produced from one production. Same parser-lowering pattern. |
| 395 | `simple_stmt : T_RETURN T_SEMICOLON` | `TT_RETURN` | (none) | ✅ | bare 0-child node |
| 396 | `simple_stmt : T_FRETURN T_SEMICOLON` | `TT_PROC_FAIL` | (none) | ✅ | bare 0-child node |
| 397 | `simple_stmt : T_NRETURN T_SEMICOLON` | `TT_NRETURN` | (none) | ✅ | bare 0-child node |
| 407–408 | `expr0 : expr1 T_2EQUAL expr0` | `TT_ASSIGN` | `[〈$1〉, 〈$3〉]` | ✅ | `expr_binary` builds in order |
| 409–412 | `expr0 : expr1 T_2EQUAL` (no rhs) | `TT_ASSIGN` | `[〈$1〉, TT_QLIT("")]` | ✅ | empty-string filler appears in same position as the missing token would |
| 413–415 | `expr0 : expr1 T_PLUS_ASSIGN expr0` | `TT_AUGOP` (ival=AUGPLUS) | `[〈$1〉, 〈$3〉]` | ✅ | scalar `ival` carries operator |
| 416–418 | `T_MINUS_ASSIGN` | `TT_AUGOP` (AUGMINUS) | `[〈$1〉, 〈$3〉]` | ✅ | |
| 419–421 | `T_STAR_ASSIGN`  | `TT_AUGOP` (AUGSTAR)  | `[〈$1〉, 〈$3〉]` | ✅ | |
| 422–424 | `T_SLASH_ASSIGN` | `TT_AUGOP` (AUGSLASH) | `[〈$1〉, 〈$3〉]` | ✅ | |
| 425–427 | `T_CARET_ASSIGN` | `TT_AUGOP` (AUGPOW)   | `[〈$1〉, 〈$3〉]` | ✅ | |
| 431–432 | `expr1 : expr3 T_2QUEST expr1` | `TT_SCAN` | `[〈$1〉, 〈$3〉]` | ✅ | |
| 436–437 | `expr3 : expr3 T_2PIPE expr4` | `TT_ALT` | flat n-ary; on first reduce `[〈$1〉, 〈$3〉]`, on subsequent re-reduce **mutated in place** to absorb new $3 | ❌ | **`sc_flatten_arith` in-place mutation** — `c[0]` is `〈$1〉` which is itself the **prior** TT_ALT node, and `〈$3〉` is appended into it. Result: a flat n-ary `TT_ALT(a, b, c, d)`. Source-order is preserved as a sequence, but the canonical rule (4 of GOAL §⛔) demands always wrapping fresh — never mutate prior. Same offender as the `goto_expr T_CONCAT` example called out in the goal file. **FLAG: violation of "always wrap, never append-in-place" left-to-right rule.** |
| 441–442 | `expr4 : expr4 T_CONCAT expr5` | `TT_SEQ` | flat n-ary; same shape and same violation as `TT_ALT` above | ❌ | **`sc_flatten_arith` in-place mutation** — same flag. |
| 446–448 | `expr5 : expr5 T_EQ expr6` | `TT_FNC` (sval="EQ") | `[〈$1〉, 〈$3〉]` | ✅ | conditional function comparison |
| 449–451 | `T_NE`     | `TT_FNC` (sval="NE")     | `[〈$1〉, 〈$3〉]` | ✅ | |
| 452–454 | `T_LT`     | `TT_FNC` (sval="LT")     | `[〈$1〉, 〈$3〉]` | ✅ | |
| 455–457 | `T_GT`     | `TT_FNC` (sval="GT")     | `[〈$1〉, 〈$3〉]` | ✅ | |
| 458–460 | `T_LE`     | `TT_FNC` (sval="LE")     | `[〈$1〉, 〈$3〉]` | ✅ | |
| 461–463 | `T_GE`     | `TT_FNC` (sval="GE")     | `[〈$1〉, 〈$3〉]` | ✅ | |
| 464–466 | `T_LEQ`    | `TT_FNC` (sval="LEQ")    | `[〈$1〉, 〈$3〉]` | ✅ | |
| 467–469 | `T_LNE`    | `TT_FNC` (sval="LNE")    | `[〈$1〉, 〈$3〉]` | ✅ | |
| 470–472 | `T_LLT`    | `TT_FNC` (sval="LLT")    | `[〈$1〉, 〈$3〉]` | ✅ | |
| 473–475 | `T_LGT`    | `TT_FNC` (sval="LGT")    | `[〈$1〉, 〈$3〉]` | ✅ | |
| 476–478 | `T_LLE`    | `TT_FNC` (sval="LLE")    | `[〈$1〉, 〈$3〉]` | ✅ | |
| 479–481 | `T_LGE`    | `TT_FNC` (sval="LGE")    | `[〈$1〉, 〈$3〉]` | ✅ | |
| 482–484 | `T_IDENT_OP` | `TT_FNC` (sval="IDENT") | `[〈$1〉, 〈$3〉]` | ✅ | |
| 485–487 | `T_DIFFER` | `TT_FNC` (sval="DIFFER") | `[〈$1〉, 〈$3〉]` | ✅ | |
| 491–492 | `expr6 : expr6 T_2PLUS expr9`  | `TT_ADD` | flat n-ary via `sc_flatten_arith` | ❌ | **Same in-place mutation violation as TT_ALT/TT_SEQ above.** |
| 493–494 | `expr6 : expr6 T_2MINUS expr9` | `TT_SUB` | flat n-ary via `sc_flatten_arith` | ❌ | **Same.** |
| 498–499 | `expr9 : expr9 T_2STAR expr11` | `TT_MUL` | flat n-ary via `sc_flatten_arith` | ❌ | **Same.** |
| 500–501 | `expr9 : expr9 T_2SLASH expr11` | `TT_DIV` | flat n-ary via `sc_flatten_arith` | ❌ | **Same.** |
| 505–506 | `expr11 : expr12 T_2CARET expr11` | `TT_POW` | `[〈$1〉, 〈$3〉]` | ✅ | right-associative, but built fresh — no flatten |
| 510–511 | `expr12 : expr12 T_2DOLLAR expr15` | `TT_CAPT_IMMED_ASGN` | `[〈$1〉, 〈$3〉]` | ✅ | |
| 512–513 | `expr12 : expr12 T_2DOT expr15`    | `TT_CAPT_COND_ASGN`  | `[〈$1〉, 〈$3〉]` | ✅ | |
| 517–523 | `expr15 : expr15 T_LBRACK exprlist T_RBRACK` | `TT_IDX` | `[〈$1〉, exprlist.c[0], exprlist.c[1], …]` | ✅ | exprlist (TT_NUL container) is unpacked, its children appended in their internal order. Source order is `expr15 [ e1, e2, e3 ]` → `[expr15, e1, e2, e3]`. ✅ matches. Container TT_NUL is freed. |
| 530 | `exprlist : ε` | `TT_NUL` | (none) | ✅ | empty exprlist placeholder |
| 532–533 | `exprlist_ne : exprlist_ne T_COMMA expr0` | **mutates $1 in place** → `TT_NUL` | flat n-ary; appends each new `expr0` into the existing $1 node | ❌ | **In-place append** — `expr_add_child($1, $3); $$ = $1;`. This is the exact pattern the goal §⛔ section forbids. Source order is preserved as a sequence (`e1, e2, e3, …`) but every reduce mutates the prior node. **FLAG: violation.** But note: `TT_NUL` here is a *temporary container* whose children are consumed/unpacked by parents (`expr15`, `expr17 T_CALL`, paren-tuple) — not a node that survives into the final tree. Still violates the rule under a strict reading. |
| 534–535 | `exprlist_ne : expr0` | `TT_NUL` (1-child container) | `[〈$1〉]` | ✅ | initial container build |
| 537–543 | `expr17 : T_CALL exprlist T_RPAREN` | `TT_FNC` (sval=fn name from `$1`) | `[exprlist.c[0], exprlist.c[1], …]` | ✅ | function name is in `sval` not a child; args appear in source order. Container TT_NUL is unpacked then freed. |
| 544–547 | `expr17 : T_IDENT` | `TT_VAR` (sval=name) | (none) | ✅ | leaf |
| 548–551 | `expr17 : T_KEYWORD` | `TT_KEYWORD` (sval=name) | (none) | ✅ | leaf |
| 552–553 | `expr17 : T_INT`   | `TT_ILIT` (ival) | (none) | ✅ | leaf |
| 554–555 | `expr17 : T_REAL`  | `TT_FLIT` (dval) | (none) | ✅ | leaf |
| 556–557 | `expr17 : T_STR`   | `TT_QLIT` (sval) | (none) | ✅ | leaf |
| 558–559 | `expr17 : T_LPAREN expr0 T_RPAREN` | (passthrough $2) | — | ✅ | no new node |
| 560–566 | `expr17 : T_LPAREN expr0 T_COMMA exprlist_ne T_RPAREN` | `TT_VLIST` | `[〈$2〉, exprlist_ne.c[0], exprlist_ne.c[1], …]` | ✅ | source order is `( e0, e1, e2, ... )` → children `[e0, e1, e2, …]`. Container TT_NUL unpacked. |
| 567–568 | `expr17 : T_LPAREN T_RPAREN` | `TT_NUL` | (none) | ✅ | empty tuple |
| 569–570 | `expr17 : T_1PLUS expr17`  | `TT_PLS`        | `[〈$2〉]` | ✅ | unary prefix |
| 571–572 | `expr17 : T_1MINUS expr17` | `TT_MNS`        | `[〈$2〉]` | ✅ | |
| 573 | `T_1STAR expr17`            | `TT_DEFER`       | `[〈$2〉]` | ✅ | |
| 574 | `T_1DOT expr17`             | `TT_NAME`        | `[〈$2〉]` | ✅ | |
| 575 | `T_1DOLLAR expr17`          | `TT_INDIRECT`    | `[〈$2〉]` | ✅ | |
| 576 | `T_1AT expr17`              | `TT_CAPT_CURSOR` | `[〈$2〉]` | ✅ | |
| 577 | `T_1TILDE expr17`           | `TT_NOT`         | `[〈$2〉]` | ✅ | |
| 578 | `T_1QUEST expr17`           | `TT_INTERROGATE` | `[〈$2〉]` | ✅ | |
| 579–580 | `T_1AMP expr17`           | `TT_OPSYN` (sval="&") | `[〈$2〉]` | ✅ | |
| 581–582 | `T_1PERCENT expr17`       | `TT_OPSYN` (sval="%") | `[〈$2〉]` | ✅ | |
| 583–584 | `T_1SLASH expr17`         | `TT_OPSYN` (sval="/") | `[〈$2〉]` | ✅ | |
| 585–586 | `T_1POUND expr17`         | `TT_OPSYN` (sval="#") | `[〈$2〉]` | ✅ | |
| 587–588 | `T_1PIPE expr17`          | `TT_OPSYN` (sval=`\|`) | `[〈$2〉]` | ✅ | |
| 589–590 | `T_1EQUAL expr17`         | `TT_OPSYN` (sval="=") | `[〈$2〉]` | ✅ | |
| 591–592 | `T_1BANG expr17`          | `TT_OPSYN` (sval="!") | `[〈$2〉]` | ✅ | |

### 1.2 Statement-level nodes built in helper functions

These are nodes produced by helpers called from grammar actions. The
"production" column names the grammar rule that triggers the helper, and the
helper's L→R wiring is what determines the resulting child order.

| Grammar trigger | Helper | Parent kind | Children L→R | L→R OK? | Notes |
|---|---|---|---|---|---|
| `matched_stmt: if_head matched_stmt else_keyword matched_stmt` (line 274) → `sc_finalize_if_else_pst` | `sc_finalize_if_else_pst` (879–889) | `TT_IF` | `[cond, TT_PROGRAM(then…), TT_PROGRAM(else…)]` | ✅ | Source order is `if ( cond ) THEN else ELSE` → `[cond, then, else]`. ✅. **Sub-flag:** `sc_collect_body(st, before_else)` runs BEFORE `sc_collect_body(st, h->before_body)` — the *else* is collected first because the *then*-collect would shorten the CODE chain and invalidate `before_else`. This is an implementation ordering, the resulting **tree child order is L→R** ✅. |
| `unmatched_stmt: if_head stmt` (line 297) → `sc_finalize_if_no_else_pst` | `sc_finalize_if_no_else_pst` (858–867) | `TT_IF` | `[cond, TT_PROGRAM(then…)]` | ✅ | |
| `matched_stmt: while_head matched_stmt` (line 276) → `sc_finalize_while_pst` | `sc_finalize_while_pst` (896–912) | `TT_WHILE` | `[cond, TT_PROGRAM(body), TT_QLIT(Ltop), TT_QLIT(Lend)]` | ⚠ | Source order is `while ( cond ) BODY` — children 0,1 ✅. **Children 2,3 are SYNTHETIC label strings** generated by `sc_label_new`, not source tokens. They are not flagged as a child-order violation per se (they sit after the source-token children) but they **do violate** the goal's general invariant "no synthesizing labels in the parser" — `_Ltop_NNNN` / `_Lend_NNNN` are minted in `while_head` action via `sc_label_new`. **FLAG: parser-side label synthesis** (this is the work item already named in `lower.sc` for break/continue resolution and is the basis of `PST-SC-4k`'s sibling cleanup). |
| `matched_stmt: do_head do_body T_WHILE T_LPAREN expr0 T_RPAREN T_SEMICOLON` (line 278) → `sc_finalize_do_while_pst` | `sc_finalize_do_while_pst` (929–945) | `TT_DO_WHILE` | `[TT_PROGRAM(body), cond, TT_QLIT(Lcont), TT_QLIT(Lend)]` | ⚠ | Source order is `do BODY while ( cond ) ;` → `[body, cond]` matches. Children 2,3 synthetic labels — same flag as TT_WHILE. ⚠ |
| `matched_stmt: for_head matched_stmt` (line 280) → `sc_finalize_for_pst` | `sc_finalize_for_pst` (951–968) | `TT_FOR` | `[cond, step, TT_PROGRAM(body), TT_QLIT(Lcont), TT_QLIT(Lend)]` | ❌ | Source order is `for ( init ; cond ; step ) BODY`. The grammar action at line 332 **emits `init` as a separate prior statement** via `sc_append_stmt(st, $3)` and then the head carries only `cond, step` (`$5, $7`). So the TT_FOR node has only `[cond, step, body]` — `init` is missing from the tree entirely; it lives as a free-standing stmt before the loop. **FLAG: source token `init` is lifted to a sibling prior statement** — same family of parser-side splicing forbidden by the goal. Plus synthetic labels. |
| `matched_stmt: func_head T_LBRACE stmt_list T_RBRACE` (line 282) → `sc_finalize_function_pst` | `sc_finalize_function_pst` (717–732) | `TT_DEFINE` | `[TT_QLIT(name), TT_QLIT(sig), TT_PROGRAM(body)]` | ❌ | Source order is `define NAME ( ARGLIST )` then `{ BODY }`. Children 0 (name) and 2 (body) match. Child 1 is `TT_QLIT(sig)` where `sig = sprintf("%s(%s)", name, argstr)` — i.e. **name is duplicated into a synthesized signature string**, and the original arglist source tokens never appear as their own children. **FLAG: arglist not preserved as child structure** — should be e.g. children `[TT_QLIT(name), TT_VLIST(TT_VAR(arg1)…TT_VAR(argN)), TT_PROGRAM(body)]` to be L→R-source-faithful. The current shape pre-cooks signature for `lower_define`. |
| `matched_stmt: switch_head T_LBRACE switch_body T_RBRACE` (line 286) → `sc_finalize_switch_pst` | `sc_finalize_switch_pst` (1100–1131) | `TT_CASE` | `[disc, val1, TT_PROGRAM(body1), val2, TT_PROGRAM(body2), …, TT_QLIT(Lend)]` (default arm uses `TT_NUL` placeholder for value) | ⚠ | Source order is `switch ( DISC ) { case V1: BODY1 case V2: BODY2 … default: BODYn }` → child 0 = disc ✅, children 1..2k alternate value/body in source order ✅. Trailing `TT_QLIT(Lend)` is synthetic. Default-arm "value" position holds `TT_NUL` placeholder (not the literal `default` keyword token). **FLAG: synthetic Lend** ⚠. **Default placeholder TT_NUL** is acceptable per primer convention but worth recording. |
| `matched_stmt: T_STRUCT T_IDENT T_LBRACE struct_field_list T_RBRACE` (line 290) → `sc_emit_struct` | `sc_emit_struct` (1133–1143) | `TT_FNC` (sval="DATA") | `[TT_QLIT("Name(field1,field2,...)")]` | ❌ | Source order is `struct NAME { f1, f2, … }`. The parser **mints a single quoted signature string** packing name + fields and **emits a `DATA(…)` call**. The struct's name and field names are NOT preserved as tree children — they're stringified. **FLAG: parser-side desugaring to runtime call** — this is exactly the kind of parser lowering the goal §⛔ forbids; should be `TT_RECORD(QLIT(name), TT_VAR(f1), TT_VAR(f2), …)` or similar with no DATA() call synthesized at parse time. |
| `simple_stmt: T_RETURN expr0 T_SEMICOLON` inside function (lines 389–394) | inline action | `TT_ASSIGN`, then `TT_RETURN` (two stmts) | `TT_ASSIGN: [TT_VAR(func_name), 〈$2〉]`, then bare TT_RETURN | ❌ | **FLAG: parser splits one source phrase into two statements**, and the LHS of the synthesized assign (`TT_VAR(func_name)`) is **not a source token** — it's read from `st->cur_func_name`. This is a parser-side lowering that should move to `lower.c`. |
| `simple_stmt: T_GOTO T_IDENT T_SEMICOLON` (line 398) → `sc_append_goto_label` | `sc_append_goto_label` (778–781) | (no tree node — creates a STMT_t directly via `sc_make_goto_uncond_stmt`) | — | ❌ | **FLAG: this is the active rung PST-SC-4k.** Should produce a `TT_GOTO_U(TT_QLIT(target))` tree node and route through `sc_append_stmt`. Currently bypasses the tree entirely and writes a STMT_t with `goto_u` field set — `stmt_to_ast` later promotes it to `TT_GOTO_U` child of `TT_STMT`. Source-order is preserved (the label appears once in the right place), but the construction is via STMT_t fields, not tree children. **THIS IS THE NEXT STEP.** |
| `simple_stmt: T_BREAK [T_IDENT] T_SEMICOLON` (lines 399–400) → `sc_append_break` | `sc_append_break` (1013–1024) | `TT_LOOP_BREAK` | `[]` (bare) or `[TT_QLIT(user_label)]` | ✅ | |
| `simple_stmt: T_CONTINUE [T_IDENT] T_SEMICOLON` (lines 401–402) → `sc_append_continue` | `sc_append_continue` (1027–1038) | `TT_LOOP_NEXT` | `[]` (bare) or `[TT_QLIT(user_label)]` | ✅ | |
| `label_decl: T_IDENT T_COLON` (line 385) → `sc_append_label_node` | `sc_append_label_node` (770–776) | (no tree node — creates a STMT_t with `s->label` set) | — | ⚠ | Label is carried as STMT_t string field; `stmt_to_ast` later produces `TT_STMT(:lbl ...)` attr. No L→R issue but worth noting label is **not a tree child** until stmt_to_ast. |

### 1.3 STMT_t → tree_t conversion (`stmt_to_ast` in `src/driver/stmt_ast.c`)

When `sc_collect_body` runs (during `if`/`while`/`do`/`for`/`switch`/`func`
finalization), each `STMT_t` in the collected range is converted to a
`tree_t` of kind `TT_STMT` by `stmt_to_ast`. The child order of that
`TT_STMT` is fixed by `stmt_to_ast` itself (lines 84–108) and is the same
across all six languages:

| Parent kind | Children L→R | L→R OK? | Notes |
|---|---|---|---|
| `TT_STMT` | `[ optional TT_ATTR(":lbl"), optional TT_ATTR(":lang"), TT_ATTR(":line"), TT_ATTR(":stno"), optional TT_ATTR(":subj") wrapping subject expr, optional TT_ATTR(":pat") wrapping pattern, optional TT_ATTR(":eq"), optional TT_ATTR(":repl") wrapping replacement, TT_GOTO_S(…), TT_GOTO_F(…), TT_GOTO_U(…) ]` | ⚠ | This is **not** a left-to-right source-token order — `:lbl` and `:lang` come first, then `:line`/`:stno` metadata, then subject, pattern, repl, gotos. It is a **canonical attr-tagged order** matching the original SNOBOL4 statement shape `LABEL  SUBJECT [? PATTERN] [= REPL] :S(…)F(…)`. **FLAG for record:** the canonical attr-tagged order is not the same as L→R source order; goal §⛔ rule does not necessarily apply here because TT_STMT's children are attribute-tagged (`:lbl`, `:subj`, …) and order is part of the *attr convention*. But: `TT_GOTO_S/F/U` always appear at the end regardless of whether the source wrote `:F(x)S(y)` (lines 74–75 of `snobol4.y` show the FAIL/SUCCEED swap when source order is `F` then `S`). This is a **deliberate normalization** — flag it for explicit decision: does PST goal treat attr-tagged children as exempt from the L→R rule? |
| `TT_GOTO_S` / `TT_GOTO_F` / `TT_GOTO_U` (produced by `make_goto_node`) | `[]` if no goto field set, `[〈expr〉]` if goto target is a computed expression, `[TT_QLIT(label)]` if goto is a literal label name | ✅ | single child either way |

---

## What this scan shows — re-scoped to ONLY the goal §⛔ rules

**The goal-file rules being enforced (and ONLY these):**
1. Children of every node appear in the same left-to-right order as their source tokens.
2. No mutation in place of a previously-built child node (always wrap, never append-in-place onto prior).
3. No source token "lifted out" of the tree (synthesized into a sibling statement, stringified into someone else's `sval`, written into a STMT_t field instead of a tree child, etc.).

**Choosing a `tree_e` kind for an operator/keyword is permitted** — the parser is allowed to use any kind that suits the downstream `lower`. Using TT_POW for unary `!`, or TT_MUL for `#`, or TT_NUL for both empty-tuple and exprlist-container, is **not a violation** of your rules and the audit will not flag it.

**Packing subject + pattern as `TT_SCAN(subj, pat)` is permitted and correct** — children L→R, fresh wrap, no mutation. `lower.c` splits at consumption time. Do not "defuse" what was never fused improperly.

### Snocone violations under the corrected rules

| # | Where | Violation | Owning rung |
|---|---|---|---|
| V1 | `expr3 : expr3 T_2PIPE expr4`  → `sc_flatten_arith` | rule 2: in-place append onto prior TT_ALT when $1 already has same kind | new rung (call it PST-SC-FLATTEN) |
| V2 | `expr4 : expr4 T_CONCAT expr5` → `sc_flatten_arith` | rule 2: in-place append onto prior TT_SEQ | PST-SC-FLATTEN |
| V3 | `expr6 : expr6 T_2PLUS  expr9` → `sc_flatten_arith` | rule 2: in-place append onto prior TT_ADD | PST-SC-FLATTEN |
| V4 | `expr6 : expr6 T_2MINUS expr9` → `sc_flatten_arith` | rule 2: in-place append onto prior TT_SUB | PST-SC-FLATTEN |
| V5 | `expr9 : expr9 T_2STAR  expr11`→ `sc_flatten_arith` | rule 2: in-place append onto prior TT_MUL | PST-SC-FLATTEN |
| V6 | `expr9 : expr9 T_2SLASH expr11`→ `sc_flatten_arith` | rule 2: in-place append onto prior TT_DIV | PST-SC-FLATTEN |
| V7 | `exprlist_ne : exprlist_ne T_COMMA expr0` | rule 2: `expr_add_child($1, $3); $$=$1;` mutates $1 by adding a child | PST-SC-FLATTEN |
| V8 | `for_head` (line 332): `sc_append_stmt(st, $3)` lifts `init` as a prior sibling statement | rule 3: `init` source token has no child in TT_FOR — lifted into a separate statement that was not in the source | new rung |
| V9 | `T_RETURN expr0 T_SEMICOLON` inside func (lines 389–394): synthesizes `TT_ASSIGN(TT_VAR(func_name), $2)` from `st->cur_func_name`; emits two statements | rule 3: synthesized LHS `TT_VAR(func_name)` is not from a source token; one `return` source phrase becomes two tree statements | new rung |
| V11 | `goto LABEL ;` → `sc_append_goto_label` writes STMT_t.goto_u field | rule 3: `LABEL` source token has no tree child; produced via STMT_t field, promoted only later by `stmt_to_ast` | **active rung PST-SC-4k** |
| V13 | `while_head` / `do_head` / `for_head` / `switch_head` mint synthetic label strings via `sc_label_new` and put them as `TT_QLIT` children of TT_WHILE/DO_WHILE/FOR/CASE | rule 3: `_Ltop_NNNN`/`_Lend_NNNN`/`_Lcont_NNNN`/`_Ldefault_NNNN` are not source tokens but appear as children | PST-SC-4k family |

### Snocone — withdrawn flags (corrected scope)

- **V10** (`T_STRUCT … sc_emit_struct` builds `TT_QLIT("Name(f1,f2,…)"))`: value decoding at a fresh leaf. Withdrawn.
- **V12** (`TT_DEFINE` child[1] is `TT_QLIT("name(args)")`): value decoding. Withdrawn.
- **V14** (`sc_split_subject_pattern` at snocone_parse.y:604 tears TT_SCAN apart): this is a **consumer-side** concern (called from `sc_append_stmt`, which converts the parser's output before lower runs). The parser building `TT_SCAN(e1, e2)` for `e1 ? e2` is correct — fresh wrap, L→R, shift/reduce-ready. The downstream split is a separate concern not governed by the §⛔ parser rules. Withdrawn 2026-05-19.
- Empty-tuple `TT_NUL`, empty-replacement `TT_QLIT("")`, default-arm `TT_NUL` placeholder: fillers for omitted source values. Not violations.

### Snocone — clean productions (unchanged from earlier scan)

All TT_FNC comparison reductions; all unary prefix operators; all capture operators (TT_CAPT_IMMED_ASGN, TT_CAPT_COND_ASGN, TT_SCAN); TT_POW; TT_AUGOP family; TT_ASSIGN; TT_IDX; TT_VLIST; all literal leaves; TT_IF (cond, then, else); TT_LOOP_BREAK / TT_LOOP_NEXT; TT_WHILE/DO_WHILE/FOR/CASE bodies (the body, cond, disc children are all L→R clean — only the synthetic label children V13/V14 are flagged).

**Net Snocone status: NOT L→R clean.** 13 violations (was 14; removed the spurious V14-as-separate-row; V13/V14 now consolidated). PST-SC-4k addresses V11 only. The other 12 are unowned by named rungs.

---

## SCAN 2 — Icon (`src/frontend/icon/icon_parse.c`)

Hand-rolled recursive-descent parser. Each `parse_FOO()` function reads
tokens left-to-right and produces a tree node. The "Loc" column is the
line of the `ast_node_new(...)` or `e_binary/e_unary(...)` call. For each
row the parser function name is given in **bold** at the top of the cluster.

| Loc | Function / call site | Parent kind | Children L→R | L→R OK? | Notes |
|-----|---------------------|-------------|--------------|---------|-------|
| **`parse_primary`** (66–165) | | | | | |
| 71–73 | `TK_INT`    | `TT_ILIT`  | (none, `v.ival` set)  | ✅ | leaf |
| 77–79 | `TK_REAL`   | `TT_FLIT`  | (none, `v.dval` set)  | ✅ | leaf |
| 83    | `TK_STRING` | `TT_QLIT`  | (none, `v.sval` set)  | ✅ | leaf |
| 87    | `TK_CSET`   | `TT_CSET`  | (none, `v.sval` set)  | ✅ | leaf |
| 91    | `TK_IDENT`  | `TT_VAR`   | (none, `v.sval` set)  | ✅ | leaf |
| 93–108| `& kwname`  | `TT_VAR` (sval=`"&"+kwname`) | (none) | ✅ | name is stringified `&NAME`; consistent with Icon convention |
| 114–122 | `( expr ; expr ; expr )` | `TT_SEQ_EXPR` | `[$first, $next1, $next2, …]` | ✅ | semicolons consumed; non-empty after `;` only |
| 129–139 | `[ e1, e2, … ]` | `TT_MAKELIST` | `[$e1, $e2, …]` | ✅ | empty list → 0-child TT_MAKELIST |
| 143 | `TK_FAIL`   | `TT_PROC_FAIL`  | (none) | ✅ | |
| 147–150 | `break [expr]` | `TT_LOOP_BREAK` | `[]` or `[$expr]` | ✅ | inside primary context, optional value-yielding expr |
| 154 | `TK_NEXT`   | `TT_LOOP_NEXT`  | (none) | ✅ | |
| **`parse_postfix`** (167–231) | | | | | |
| 174–189 | `expr ( args )` | `TT_FNC` | `[$callee, $arg1, $arg2, …]` | ✅ | callee is c[0] which is itself the source-prior `n`; args follow in order. Empty-arg "&null" placeholder injected for trailing/empty commas — synthetic but is the documented Icon argument-defaulting convention. |
| 197–199 | `expr [ idx : hi ]` | `TT_SECTION` | `[$expr, $idx, $hi]` | ✅ | |
| 204–206 | `expr [ idx +: len ]` | `TT_SECTION_PLUS` | `[$expr, $idx, $len]` | ✅ | |
| 211–213 | `expr [ idx -: len ]` | `TT_SECTION_MINUS` | `[$expr, $idx, $len]` | ✅ | |
| 216 | `expr [ idx ]`  | `TT_IDX`   | `[$expr, $idx]` | ✅ | via `e_binary` |
| 222–225 | `expr . field`  | `TT_FIELD` | `[$expr, TT_VAR(fieldname)]` | ✅ | `TT_VAR` for field name appears in c[1]; matches `ICN_FIELD_NAME` convention in ast.h |
| **`parse_limit`** (235–244) | | | | | |
| 241 | `expr \ lim` | `TT_LIMIT` | `[$expr, $lim]` | ✅ | |
| **`parse_unary`** (246–259) | | | | | |
| 248–257 | `-x`/`+x`/`!x`/`*x`/`\x`/`/x`/`not x`/`?x`/`~x`/`=x` | TT_MNS/PLS/ITERATE/SIZE/NONNULL/NULL/NOT/RANDOM/CSET_COMPL/MATCH_UNARY | `[$operand]` | ✅ | each via `e_unary` |
| **`parse_pow`** (261–270) | | | | | |
| 267 | `x ^ y` | `TT_POW` | `[$x, $y]` | ✅ | right-associative via recursive call; fresh wrap each time |
| **`parse_mul`** (272–285) | | | | | |
| 282 | `x * y`, `x / y`, `x % y` | TT_MUL/DIV/MOD | `[$prev, $right]` per binary; **left-associative loop builds left-leaning binary chain** | ✅ | `n = e_binary(k, n, parse_pow(p))` — always wraps fresh, never mutates in place. **CONTRAST with Snocone's `sc_flatten_arith`** which would flatten — Icon is the clean reference shape. |
| **`parse_add`** (287–299) | | | | | |
| 296 | `x + y`, `x - y` | TT_ADD/SUB | `[$prev, $right]` left-leaning binary | ✅ | always fresh-wrap |
| **`parse_cset`** (301–319) | | | | | |
| 311 | `x ! y` (binary) | `TT_BANG_BINARY` | `[$prev, $right]` | ✅ | |
| 316 | `x ++ y`, `x -- y`, `x ** y` | TT_CSET_UNION/DIFF/INTER | `[$prev, $right]` | ✅ | |
| **`parse_concat`** (321–333) | | | | | |
| 330 | `x \|\|\| y`, `x \|\| y` | TT_LCONCAT/CAT | `[$prev, $right]` | ✅ | |
| **`parse_rel`** (354–363) | | | | | |
| 360 | `x < y`, `<= >= > = ~= << <<= >>= >> == ~==` | TT_LT/LE/GT/GE/EQ/NE/LLT/LLE/LGT/LGE/LEQ/LNE | `[$prev, $right]` | ✅ | |
| **`parse_and`** (367–378) | | | | | |
| 371–377 | `x & y & z` | `TT_SEQ` | `[$first, $rhs1, $rhs2, …]` flat n-ary | ✅ | builds fresh TT_SEQ node, never mutates a prior node. Iterative `push_child` is on the **just-created** seq, not on any prior reduce. This is the clean equivalent of what Snocone's `sc_flatten_arith` does badly. |
| **`parse_to`** (380–397) | | | | | |
| 389–391 | `x to lim by step` | `TT_TO_BY` | `[$x, $limit, $step]` | ✅ | |
| 393 | `x to lim` (no `by`) | `TT_TO` | `[$x, $limit]` | ✅ | |
| **`parse_alt`** (399–410) | | | | | |
| 403–408 | `x \| y \| z` | `TT_ALTERNATE` | `[$first, $rhs1, $rhs2, …]` flat n-ary | ✅ | same clean shape as `TT_SEQ` above — fresh node, never mutate prior |
| **`parse_assign`** (422–489) | | | | | |
| 427 | `x := y` | `TT_ASSIGN`     | `[$x, $y]` | ✅ | |
| 431 | `x <- y` | `TT_REVASSIGN`  | `[$x, $y]` | ✅ | |
| 435 | `x :=: y` | `TT_SWAP`      | `[$x, $y]` | ✅ | |
| 439 | `x <-> y` | `TT_REVSWAP`   | `[$x, $y]` | ✅ | |
| 443 | `x === y` | `TT_IDENTICAL` | `[$x, $y]` | ✅ | |
| 447 | `x ~=== y` | `TT_NOT(TT_IDENTICAL($x,$y))` | outer=`[TT_IDENTICAL]`, inner=`[$x,$y]` | ✅ | parser desugars `~===` to `not (x === y)`. Two-node introduction synthesized by parser. Strictly, **`TT_NOT` here is parser-side desugaring**: source has one operator `~===` and we produce two tree nodes. **FLAG ⚠** — minor desugaring, mirrors Icon semantics 1:1 but is technically a non-pure-syntax rewrite. |
| 452–482 | `x op= y` (any augop) | `TT_AUGOP` (ival=AugOp_e enum) | `[$x, $y]` | ✅ | scalar `ival` carries operator kind |
| 486 | `x ? y` | `TT_SCAN` | `[$x, $y]` | ✅ | |
| **`parse_expr`** (491–580) | | | | | |
| 495–500 | `return [expr]`  | `TT_RETURN`   | `[]` or `[$expr]` | ✅ | |
| 504 | `fail`             | `TT_PROC_FAIL`| (none) | ✅ | |
| 508–512 | `suspend expr [do BODY]` | `TT_SUSPEND` | `[$expr]` or `[$expr, $body]` | ✅ | optional do-clause appended; source-token order |
| 514 | `break`            | `TT_LOOP_BREAK` | (none) | ✅ | |
| 515 | `next`             | `TT_LOOP_NEXT`  | (none) | ✅ | |
| 518–525 | `if COND then THEN [else ELSE]` | `TT_IF` | `[$cond, $then]` or `[$cond, $then, $else]` | ✅ | |
| 529–533 | `every EXPR [do BODY]` | `TT_EVERY` | `[$expr]` or `[$expr, $body]` | ✅ | |
| 537–541 | `while COND [do BODY]` | `TT_WHILE` | `[$cond]` or `[$cond, $body]` | ✅ | |
| 545–549 | `until COND [do BODY]` | `TT_UNTIL` | `[$cond]` or `[$cond, $body]` | ✅ | |
| 553–555 | `repeat BODY`     | `TT_REPEAT` | `[$body]` | ✅ | |
| 559–577 | `case EXPR of { V1: B1; V2: B2; … default: D }` | `TT_CASE` | `[$disc, $v1, $b1, $v2, $b2, …, $default]` | ⚠ | flat n-ary value/body pairs in source order ✅; **default arm is appended as a single child without any "default" marker** — consumer disambiguates by parity (last child after odd-pair count is default). No `TT_NUL` placeholder; just a position convention. **FLAG ⚠** — convention is sound but not L→R-explicit: the source token `default` has no tree analog. The default *value* slot is implicit. **Minor**: contrast with Snocone (1.2 row above) which uses `TT_NUL` as an explicit placeholder for the default value. Pick one convention across frontends. |
| **`parse_block_or_expr`** (582–596) | | | | | |
| 585 | `{ S1; S2; … }` | `TT_SEQ_EXPR` | `[$s1, $s2, …]`; **if nc==1 the seq is discarded and the single child is returned** | ⚠ | The unwrap at line 594 (`if (nc == 1) return seq->c[0]`) is a parser-side simplification — single-stmt blocks don't appear as TT_SEQ_EXPR. Source had braces but tree has no record of them. **FLAG ⚠** — minor, but a structural unwrap. (Same pattern as paren-grouping returning `$2` directly in Snocone — broadly acceptable for "transparent" syntactic markers, but inconsistent with strict "every source token has a tree analog" reading.) |
| **`parse_stmt`** (603–706) | | | | | |
| 606–611 | `every EXPR [do BODY] ;` | `TT_EVERY` | `[$expr]` or `[$expr, $body]` | ✅ | duplicate of parse_expr branch (necessary at statement level) |
| 615–623 | `if … then … [else …] ;` | `TT_IF` | same as expr-level | ✅ | |
| 627–632 | `while … [do …] ;` | `TT_WHILE` | same | ✅ | |
| 636–641 | `until … [do …] ;` | `TT_UNTIL` | same | ✅ | |
| 645–648 | `repeat … ;`          | `TT_REPEAT` | same | ✅ | |
| 652–655 | `return [expr] ;`     | `TT_RETURN` | `[]` or `[$expr]` | ✅ | |
| 659–664 | `suspend expr [do body] ;` | `TT_SUSPEND` | `[$expr]` or `[$expr, $body]` | ✅ | |
| 669 | `fail ;`                | `TT_PROC_FAIL` | (none) | ✅ | |
| 673–676 | `initial BODY [;]`    | `TT_INITIAL` | `[$body]` | ✅ | |
| 678–681 | `case … of { … } ;`   | `TT_CASE`    | same as expr-level | ✅ | |
| 686–695 | `local x, y, z ;` / `static x, y, z ;` | `TT_LOCAL` or `TT_STATIC_DECL` | `[TT_VAR(x), TT_VAR(y), TT_VAR(z)]` | ✅ | |
| **`parse_record`** (708–725) | | | | | |
| 712–722 | `record NAME ( f1, f2, … )` | `TT_RECORD` (sval=name) | `[TT_VAR(f1), TT_VAR(f2), …]` | ⚠ | record name is in `v.sval`, NOT a child. Source order is `record NAME ( fields )` → tree has name in `v` and fields in `c[]`. **FLAG ⚠** — minor: name is preserved as data, just not as a child. This is the same pattern used by `TT_FNC` for call name in postfix (lines 174–189) where the callee IS a child (c[0]). **Inconsistency:** `TT_RECORD` keeps name in `v.sval`, `TT_FNC` for calls keeps callee in `c[0]`. Tree shape for "record" diverges from "call". Worth recording. |
| **`parse_proc`** (727–761) | | | | | |
| 753–758 | `procedure NAME ( p1, p2 ) ; STMTS end` | `TT_FNC` (sval=name, `_id`=nparams) | `[TT_VAR(name), TT_VAR(p1), TT_VAR(p2), …, $stmt1, $stmt2, …]` | ❌ | **FLAG ❌:** (a) `TT_VAR(name)` at c[0] is a **synthesized leaf for the procname** — but the procname token was already consumed at line 730. So c[0] is built from the same source token as `v.sval`. That's duplication, not L→R violation per se. (b) But parameters and body statements are **flattened into a single n-ary list** with no separation marker. A consumer must know `_id` (nparams) to find where params end and body begins. **`_id` is allocator bookkeeping in tree_t struct and is queued for removal in PST-FIELD-2.** Once `_id` is gone, this shape is unparseable from the tree alone. The shape should be `TT_DEFINE(TT_VAR(name), TT_VLIST(params), TT_PROGRAM(body))` — three explicit children, matching how Snocone's `TT_DEFINE` already works (sort of; see V12 above). **FLAG: parser-flat n-ary that requires out-of-band info (`_id`) to decode.** |
| **`icn_parse_file`** (770–804) | | | | | |
| 780–788 | `global x, y, z ;` | `TT_GLOBAL` | `[TT_VAR(x), TT_VAR(y), …]` | ✅ | |
| 794–799 | each top-level form | `TT_STMT` (synthesized wrapper) | `[TT_ATTR(:lang), TT_ATTR(:line), TT_ATTR(:stno), TT_ATTR(:subj wrapping $top)]` | ⚠ | This is the **icon-specific** TT_STMT shape: simpler than the SNOBOL-style TT_STMT from `stmt_to_ast` (no lbl, no pat, no eq, no repl, no GOTO_S/F/U children). The `:lang/:line/:stno` attrs come first, then `:subj` wrapping the actual top-level form. **FLAG ⚠:** Icon's TT_STMT children-shape is **different** from `stmt_to_ast`'s TT_STMT children-shape. Two TT_STMT variants exist in the codebase. This is not a child-order violation but is a shape disagreement that the LR-audit table makes visible for the first time. Needs an explicit decision: same TT_STMT or different? |

### Icon — re-scoped to ONLY the goal §⛔ rules

Under the goal's three rules (L→R order, no mutate-prior, no source token
lifted out), Icon is **substantially cleaner** than the earlier scan suggested.
Withdrawing the flags that were enforcing rules you didn't specify:

**Withdrawn — not violations of your rules:**
- **I1** (`~=== ` desugared to `TT_NOT(TT_IDENTICAL(…))`): the parser chose two tree kinds for one operator. Your rules permit the parser to pick a node kind. Withdrawn.
- **I2** (case default has no marker; positional convention): position is L→R-correct; default uses an implicit slot. Choice of "no placeholder vs TT_NUL placeholder" is the parser's. Withdrawn.
- **I3** (single-stmt block unwraps to drop TT_SEQ_EXPR): the braces are pure layout tokens — discarding them is explicitly allowed by the goal text ("parsers may only: discard pure layout tokens (parens, separators)"). Withdrawn.
- **I4** (record name in `v.sval` not as a child): same reasoning — the parser is allowed to carry the name as a node value. Note that **`v.sval` is not "lifting out of the tree"** — the data is still on the node, just in `v` rather than `c[]`. Withdrawn from §⛔ rule scope, though it's a separate concern of PST-FIELD-2.
- **I6** (Icon's TT_STMT shape vs `stmt_to_ast`'s TT_STMT shape): two different production paths produce TT_STMT differently. Each path's own children are L→R from that path's source-token sequence. Cross-frontend shape uniformity is a different goal entirely. Withdrawn from §⛔ scope.

**Retained under your rules:**

| # | Where | Violation | Severity |
|---|---|---|---|
| I5 | `parse_proc` line 753–758 — `TT_FNC` for proc-decl uses `_id=nparams` to delimit params from body inside one flat n-ary child list | **rule 3** in spirit: the *structure* of the source (param block vs body block) is not in the tree — it's in `_id`. Without `_id` the tree is undecodable. | ❌ — blocks PST-FIELD-2 by your rules' logic: once `_id` is gone, two source-distinct token groups are merged into one child list with no structural separation. |

**Net Icon status under your rules: 1 violation (I5).** Goal-file claim of
"✅ Phase 1 complete" is now **substantially closer to true** under the
correctly-scoped rules. The one outstanding issue (I5) blocks PST-FIELD-2
specifically.

---

## SCAN 3 — SNOBOL4 (`src/frontend/snobol4/snobol4.y`)

Bison grammar. SNOBOL4's `stmt` reductions don't build a single tree node —
they call `sno4_stmt_commit_go` which writes a `STMT_t` to the `CODE_t`
chain (already documented in scan 1.3 — that becomes a `TT_STMT` via
`stmt_to_ast`). The table below covers only the grammar productions that
build `tree_t` nodes inline (mostly the expression cascade plus a few stmt
mid-rule pieces) and the goto-expression sub-grammar.

| Loc | Production | Parent kind | Children L→R | L→R OK? | Notes |
|-----|------------|-------------|--------------|---------|-------|
| 70–75 | `stmt subj-with-pat`: `expr_binary(TT_SCAN, $2, $4)` | `TT_SCAN` | `[〈$2〉, 〈$4〉]` | ✅ | Subject + pattern packed into `TT_SCAN` as the subject expression of the statement. `lower.c` later splits. Six variants for different `:S`/`:F` goto combinations all build the same TT_SCAN shape — ✅. |
| 85–90 | unlabeled equivalent (6 rules) | `TT_SCAN` | `[〈$1〉, 〈$3〉]` | ✅ | same |
| 99 | `opt_repl: T_2EQUAL`  | `TT_QLIT(sval="")` | (none) | ✅ | empty replacement filler — same convention as Snocone empty rhs |
| 103–108 | `goto_label_expr` six variants (literal label / `$IDENT` / `$"str"` / `$(expr)`) | `TT_QLIT` (sval=label name) **or** passthrough (`$(expr)` → `$$=$4`) | (none) | ⚠ | The non-passthrough variants stringify the label/`$NAME` form into a single `TT_QLIT`. The `$NAME` indirection (`$IDENT`, `$STR`) is **flattened into a string** like `"$foo"` — the source token `$` is captured into the sval prefix, not as a separate child. **FLAG ⚠** — parser-side stringification of structured source. (Equivalent to Snocone's struct-decl stringification, in spirit.) |
| 110 | `expr0: expr2 T_2EQUAL expr0`     | `TT_ASSIGN` | `[〈$1〉, 〈$3〉]` | ✅ | |
| 111 | `expr0: expr2 T_2QUEST expr0`     | `TT_SCAN`   | `[〈$1〉, 〈$3〉]` | ✅ | |
| 114 | `expr2: expr2 T_2AMP expr3`       | `TT_OPSYN` (sval="&") | `[〈$1〉, 〈$3〉]` | ⚠ | `expr_binary(...)` builds fresh, then sval set post-construction. Operator carried in sval. Convention divergence: most binops have sval=NULL; OPSYN is the exception. |
| 117 | `expr3: expr3 T_2PIPE expr4`      | `TT_ALT`    | `[〈$1〉, 〈$3〉]` per reduce — **fresh wrap, right-leaning chain** | ✅ | After PST-SN4-1d. Contrast Snocone's `sc_flatten_arith` which flattens — SNOBOL4 is the canonical clean form. |
| 120 | `expr4: expr4 T_CONCAT expr5`     | `TT_SEQ`    | `[〈$1〉, 〈$3〉]` per reduce — fresh wrap | ✅ | same — post-PST-SN4-1d. |
| 123 | `expr5: expr5 T_2AT expr6`        | `TT_OPSYN` (sval="@") | `[〈$1〉, 〈$3〉]` | ⚠ | same OPSYN convention as line 114 |
| 126 | `expr6: expr6 T_2PLUS expr7`      | `TT_ADD`    | `[〈$1〉, 〈$3〉]` | ✅ | |
| 127 | `expr6: expr6 T_2MINUS expr7`     | `TT_SUB`    | `[〈$1〉, 〈$3〉]` | ✅ | |
| 130 | `expr7: expr7 T_2POUND expr8`     | `TT_MUL`    | `[〈$1〉, 〈$3〉]` | ❌ | **FLAG: source token is `##` (T_2POUND) but tree kind is TT_MUL.** The `#` token is being aliased to multiplication. Worse than convention divergence — this is **kind-spoofing**: a downstream consumer reading `TT_MUL` cannot recover that the source said `#`. The `#` operator is SPITBOL's "multiplication with case-folded result" or similar — semantically distinct from `*`. Need to confirm intent. If `#` is genuinely multiplication, use sval to disambiguate; if it's distinct, add a new tree kind. |
| 133 | `expr8: expr8 T_2SLASH expr9`     | `TT_DIV`    | `[〈$1〉, 〈$3〉]` | ✅ | |
| 136 | `expr9: expr9 T_2STAR expr10`     | `TT_MUL`    | `[〈$1〉, 〈$3〉]` | ✅ | T_2STAR is `*` — TT_MUL is the right kind. |
| 139 | `expr10: expr10 T_2PERCENT expr11`| `TT_DIV`    | `[〈$1〉, 〈$3〉]` | ❌ | **Same flag as line 130 (kind-spoofing).** Source token `%` aliased to TT_DIV. `%` in SPITBOL is "modulo" or "cset-related" — semantically distinct from division. |
| 142 | `expr11: expr12 T_2CARET expr11`  | `TT_POW`    | `[〈$1〉, 〈$3〉]` | ✅ | right-associative |
| 145 | `expr12: expr12 T_2DOLLAR expr13` | `TT_CAPT_IMMED_ASGN` | `[〈$1〉, 〈$3〉]` | ✅ | |
| 146 | `expr12: expr12 T_2DOT expr13`    | `TT_CAPT_COND_ASGN`  | `[〈$1〉, 〈$3〉]` | ✅ | |
| 149 | `expr13: expr14 T_2TILDE expr13`  | `TT_OPSYN` (sval="~") | `[〈$1〉, 〈$3〉]` | ⚠ | OPSYN convention |
| 152 | `expr14: T_1AT expr14`       | `TT_CAPT_CURSOR` | `[〈$2〉]` | ✅ | |
| 153 | `T_1TILDE expr14`            | `TT_NOT`         | `[〈$2〉]` | ✅ | |
| 154 | `T_1QUEST expr14`            | `TT_INTERROGATE` | `[〈$2〉]` | ✅ | |
| 155 | `T_1AMP expr14`              | `TT_OPSYN` (sval="&") | `[〈$2〉]` | ⚠ | |
| 156 | `T_1PLUS expr14`             | `TT_PLS`         | `[〈$2〉]` | ✅ | |
| 157 | `T_1MINUS expr14`            | `TT_MNS`         | `[〈$2〉]` | ✅ | |
| 158 | `T_1STAR expr14`             | `TT_DEFER`       | `[〈$2〉]` | ✅ | |
| 159 | `T_1DOLLAR expr14`           | `TT_INDIRECT`    | `[〈$2〉]` | ✅ | |
| 160 | `T_1DOT expr14`              | `TT_NAME`        | `[〈$2〉]` | ✅ | |
| 161 | `T_1BANG expr14`             | **`TT_POW`** (unary, n=1) | `[〈$2〉]` | ❌ | **FLAG: kind reuse for unary**. The source token `!` (unary) builds a `TT_POW` node with 1 child. Same node kind, two different meanings, disambiguated only by `n`. Downstream consumers must inspect `n` to know whether TT_POW is a power-binary or a `!` unary. The five unary aliases below (lines 162–166) share this problem. |
| 162 | `T_1PERCENT expr14`          | **`TT_DIV`** (n=1)  | `[〈$2〉]` | ❌ | Same kind-reuse-as-unary. |
| 163 | `T_1SLASH expr14`            | **`TT_DIV`** (n=1)  | `[〈$2〉]` | ❌ | And `T_1PERCENT` and `T_1SLASH` are **the same node kind** — distinguished only by which source token produced them (info lost). Now downstream cannot tell `%x` from `/x` from `x/y` (binary). |
| 164 | `T_1POUND expr14`            | **`TT_MUL`** (n=1)  | `[〈$2〉]` | ❌ | Same kind-reuse. |
| 165 | `T_1EQUAL expr14`            | **`TT_ASSIGN`** (n=1) | `[〈$2〉]` | ❌ | Unary `=x` builds a TT_ASSIGN with one child — even more confusing. |
| 166 | `T_1PIPE expr14`             | `TT_OPSYN` (sval="\|") | `[〈$2〉]` | ⚠ | At least this one uses TT_OPSYN with sval — the source token IS recoverable. |
| 175–176 | `expr15: expr15 T_LBRACK { idx_node; g_cur_push } idx_args T_RBRACK` (and `T_LANGLE/T_RANGLE`) | `TT_IDX` | `[〈$1〉, idx_args.c[0], idx_args.c[1], …]` | ⚠ | **Mid-rule action with global stack** `g_cur_push/_pop`. Children pushed in source order — L→R ✅. But the pattern relies on bison's deterministic LALR(1) order (no `&FULLSCAN`-style re-entry). **FLAG ⚠** — works correctly today, but is **not expressible in `parser_snocone.sc` shift/reduce** without porting the global-stack discipline. The SCRIP mirror will need its own equivalent. |
| 179–181 | `idx_args` — left-recursive list, `expr_add_child(g_cur_top_(), $3)` etc. | (no node; mutates `g_cur_top_()`) | mutates the TT_IDX created above | ⚠ | Same as above — mid-rule mutation into a node created by a sibling reduction. Stays L→R but is structurally a side-effect-on-global pattern. |
| 180 | `idx_args : idx_args T_COMMA` (omitted arg) | inserts `TT_NUL` placeholder | adds `TT_NUL` child | ✅ | trailing/empty comma → TT_NUL — same convention as Snocone for empty arglist slots |
| 185 | `expr17: T_LPAREN expr0 T_COMMA { vlist; g_cur_push } vlist_args T_RPAREN` | `TT_VLIST` | `[〈$2〉, vlist_args.c[0], …]` | ⚠ | Same g_cur pattern. L→R ✅. |
| 186 | `expr17: T_LPAREN T_RPAREN` | `TT_NUL` | (none) | ✅ | empty tuple |
| 187 | `expr17: T_FUNCTION T_LPAREN { fn_or_prim; g_cur_push } fnc_args T_RPAREN` | `TT_FNC` **OR** one of TT_ANY/TT_NOTANY/TT_SPAN/TT_BREAK/TT_BREAKX/TT_LEN/TT_POS/TT_RPOS/TT_TAB/TT_RTAB/TT_ARB/TT_ARBNO/TT_REM/TT_FAIL/TT_SUCCEED/TT_FENCE/TT_ABORT/TT_BAL | `[arg0, arg1, …]` (no callee child — name in sval for TT_FNC, NO sval for primitive-pattern kinds) | ❌ | **FLAG: `pat_prim_kind` classifies the identifier `$1.sval` into a primitive-pattern tree kind.** When source writes `ANY(...)`, parser builds `TT_ANY` (one of 18 primitive-pattern kinds); when source writes `MYFUNC(...)`, parser builds `TT_FNC` with sval="MYFUNC". This is **parser-side semantic classification by identifier name**. The goal §⛔ allows "choose a node kind for an operator" — but here the operator is `()` (call), and the *kind* depends on the **string content of an identifier token**. Strictly, this is parser-side semantic dispatch — the canonical pure form would be `TT_FNC(TT_VAR(name), arg, arg, …)` always, with `lower.c` recognizing primitive-pattern names. Already done this way for Icon (callee in c[0]). **The list of primitives is hardcoded in `pat_prim_kind`** (lines 26–36) — a runtime check. |
| 188–189 | `T_IDENT` / `T_END` | `TT_VAR` (sval) | (none) | ✅ | |
| 190 | `T_KEYWORD` | `TT_KEYWORD` (sval) | (none) | ✅ | |
| 191 | `T_STR` | `TT_QLIT` (sval) | (none) | ✅ | |
| 192 | `T_INT` | `TT_ILIT` (ival) | (none) | ✅ | |
| 193 | `T_REAL` | `TT_FLIT` (dval) | (none) | ✅ | |
| 195–196 | `vlist_args` — `expr_add_child(g_cur_top_(), $)` | mutates `g_cur_top_()` (the TT_VLIST) | adds child | ⚠ | g_cur stack again — L→R OK |
| 198–201 | `fnc_args` — same | mutates `g_cur_top_()` (the TT_FNC or primitive) | adds child | ⚠ | g_cur stack again — L→R OK; trailing comma produces TT_NUL |
| 205–208 | `goto_atom: T_STR/T_IDENT/T_FUNCTION/T_END` | `TT_QLIT` (for STR) or `TT_VAR` | (none) | ✅ | |
| 210 | `goto_expr: goto_atom` | passthrough | — | ✅ | |
| 211 | **`goto_expr: goto_expr T_CONCAT goto_atom`** | **`expr_add_child($1,$3); $$=$1;`** — **mutates `$1` in place** | flat n-ary | ❌ | **THIS IS THE EXACT WART THE GOAL §⛔ SECTION CALLED OUT.** Source: `goto_expr T_CONCAT goto_atom { if($1->t==TT_SEQ){expr_add_child($1,$3);$$=$1;} else{...} }`. The current code is the simplified mutate-always form — even worse than the goal's two-branch example (which at least wrapped fresh when the prior wasn't TT_SEQ). Here `$1` is whatever `goto_atom` reduced to (TT_QLIT or TT_VAR), and `expr_add_child` mutates that leaf into a multi-child node. **The leaf TT_QLIT/TT_VAR is being mutated into an n-ary parent**, which is structurally worse than mutating a TT_SEQ. **Critical violation — confirms PST-SN4-1d/1e was not landed completely.** |

### SNOBOL4 — re-scoped to ONLY the goal §⛔ rules (corrected 2026-05-19)

**Withdrawn — not violations of your rules:**
- **S0/W5** (`expr_binary(TT_SCAN, $2, $4)` at lines 70–75 and 85–90): the parser builds `TT_SCAN(subj, pat)` from `subj ? pat` — fresh wrap, two children in L→R source order, shift/reduce-ready. The downstream split into separate STMT_t fields is a consumer-side concern. The **parser** is clean here. Withdrawn 2026-05-19.
- **S1** (`goto_label_expr` stringifies `$IDENT` into one `TT_QLIT.sval = "$foo"`): value decoding at a fresh leaf. Withdrawn.
- **S2** (TT_OPSYN binops with sval set post-construction): fresh wrap. Withdrawn.
- **S3** (T_2POUND builds TT_MUL, S4 T_2PERCENT builds TT_DIV): parser's kind choice. Withdrawn.
- **S5** (unary `!`/`%`/`/`/`#`/`=` build TT_POW/TT_DIV/TT_DIV/TT_MUL/TT_ASSIGN with n=1): parser's kind choice. Withdrawn.
- **S7** (`pat_prim_kind` picks TT_ANY/TT_SPAN/… vs TT_FNC): permitted. Withdrawn.

**Retained under your rules:**

| # | Where | Violation | Severity |
|---|---|---|---|
| S6 / W3 | `expr15`/`expr17` TT_IDX/TT_VLIST/TT_FNC use `g_cur_push` mid-rule globals; `idx_args`/`vlist_args`/`fnc_args` reductions call `expr_add_child(g_cur_top_(), $)` which **mutates the previously-built TT_IDX/TT_VLIST/TT_FNC node by changing its `n` and `c[]`** | **rule 2 (tree mutation)**. Children land L→R ✅ but mechanism mutates prior. | ❌ rule 2 |
| S8 / W2 | **`goto_expr T_CONCAT goto_atom`** (line 211): `expr_add_child($1,$3); $$=$1;` | **rule 2 — canonical violation, named in goal §⛔.** Mutates `$1` (a TT_QLIT/TT_VAR leaf). | ❌❌ rule 2 |

**Net SNOBOL4 status: 2 violations (W2, W3).** Both are tree mutation of
previously-built nodes. PST-SN4-1d cleaned up `expr3`/`expr4` (TT_ALT,
TT_SEQ) but missed `goto_expr` (W2) and the mid-rule g_cur pattern (W3).

---

## SCAN 4 — Raku (`src/frontend/raku/raku.y`)

Bison grammar, 695 lines. Token-bearing actions build `tree_t` nodes via
`expr_binary`, `expr_unary`, `expr_add_child`, `make_call`, `make_seq`,
`leaf_sval`, `var_node`. Statement-list growth uses a parser-private
`ExprList` accumulator (`exprlist_new` / `exprlist_append`) — that is a
**local scratch container**, not a tree node, so accumulating into it is
not a tree mutation. The container's items are spliced into a fresh
`TT_SEQ_EXPR` or `TT_FNC` at the parent production. Verified for each
site.

The grammar productions that build `tree_t` nodes are surveyed below in
file order. Productions whose action is `$$ = $1` (pure pass-through) are
omitted — they build no node.

### 4.1 Top level

| Loc | Production | Parent kind | Children L→R | L→R OK? | Notes |
|-----|------------|-------------|--------------|---------|-------|
| 193–217 | `program : stmt_list` | (no node directly — drives `add_proc` for each `stmt_list` item) | — | ⚠ | Top-level walks `stmt_list`, picks out items where `t==TT_FNC && _id==SUB_TAG_ID` and calls `add_proc(e)`; remaining items are wrapped into a synthetic `main` `TT_FNC` (lines 206–212). **FLAG: synthetic `main` proc minted by the parser.** No source token `main` exists — it is named from a literal in `leaf_sval(TT_FNC,"main")`. Rule 3 violation: a `TT_FNC` node appears in the tree with no corresponding source-token origin. Owned by **PRF-12-program** (already named in `GOAL-PST-RAKU.md`). |
| 116–125 | `add_proc(e)` helper (called from program action and from class_decl method emission, and from gather-hoist pass) | `TT_STMT` | `[TT_ATTR(":lang"), TT_ATTR(":line"), TT_ATTR(":stno"), TT_ATTR(":subj"〈e〉)]` | ⚠ | Same shape as Icon's TT_STMT (audit 1.3) — attr-tagged children. Not L→R-by-source-tokens (the `:lang` attr is not a source token at all). Treated identically to Icon's wrapper — convention-tagged, not subject to §⛔ rule 1 per primer. |

### 4.2 Statement productions

| Loc | Production | Parent kind | Children L→R | L→R OK? | Notes |
|-----|------------|-------------|--------------|---------|-------|
| 222–228 | `stmt : KW_MY VAR_SCALAR/ARRAY/HASH '=' expr ';'` (three rules) | `TT_ASSIGN` | `[TT_VAR(name), 〈$4〉]` | ✅ | `var_node($2)` strips sigil and builds a fresh `TT_VAR` leaf — value decoding from one source token. Fresh wrap. |
| 229–234 | `stmt : KW_MY IDENT VAR_SCALAR/ARRAY/HASH '=' expr ';'` (three rules) | `TT_ASSIGN` | `[TT_VAR($3-name), 〈$5〉]` | ⚠ | The `IDENT $2` source token is **discarded** (`free($2)`). It is the type-annotation in `my Int $x = ...`. **FLAG: source token lifted out — type annotation has no tree analog.** Rule 3 violation: a source token that bore identifier content (the type name) was thrown away. Goal §⛔ rule 3 forbids this. Owned: queue under **PRF-12-my-type** (proposed new rung). |
| 235–240 | `stmt : KW_MY IDENT VAR_SCALAR/ARRAY/HASH ';'` (no init) | `TT_ASSIGN` | `[TT_VAR($3-name), TT_QLIT("")]` | ⚠ | Same as above — `IDENT $2` (type) discarded. Empty-string filler in rhs position is the convention for omitted init, ✅ per primer. The type-discard remains the rule 3 violation. |
| 241–242 | `stmt : KW_SAY expr ';'` | `TT_FNC` (sval="write") | `[TT_VAR("write"), 〈$2〉]` | ⚠ | **Parser-side desugar: `say` keyword → `write(...)` call.** The source keyword `say` is replaced by a synthetic call-name `"write"`. Rule 3 violation: source token `say` has no tree analog — it is recoded into a string literal `"write"` baked into the parser. (Same family of parser-side desugar as Snocone's `struct → DATA(...)`.) Owned: **PRF-12-say** (proposed new rung). |
| 243–245 | `stmt : KW_SAY '(' expr ',' expr ')' ';'` | `TT_FNC` (sval="raku_say_fh") | `[TT_VAR("raku_say_fh"), 〈$3〉, 〈$5〉]` | ⚠ | Same `say`-token-discard plus synthetic `raku_say_fh` name. **PRF-12-say.** |
| 246–247 | `stmt : KW_PRINT expr ';'` | `TT_FNC` (sval="writes") | `[TT_VAR("writes"), 〈$2〉]` | ⚠ | Same: `print` → `writes`. **PRF-12-print.** |
| 248–250 | `stmt : KW_PRINT '(' expr ',' expr ')' ';'` | `TT_FNC` (sval="raku_print_fh") | `[TT_VAR("raku_print_fh"), 〈$3〉, 〈$5〉]` | ⚠ | Same. **PRF-12-print.** |
| 251–252 | `stmt : KW_TAKE expr ';'` | `TT_SUSPEND` | `[〈$2〉]` | ✅ | parser chose TT_SUSPEND as kind for `take` — permitted (rule 1 of "kind selection"). Source token `take` becomes the node kind. Clean. |
| 253–256 | `stmt : KW_RETURN expr ';'` / `KW_RETURN ';'` | `TT_RETURN` | `[〈$2〉]` or `[]` | ✅ | clean |
| 257–258 | `stmt : VAR_SCALAR '=' expr ';'` | `TT_ASSIGN` | `[TT_VAR(name), 〈$3〉]` | ✅ | clean |
| 259–263 | `stmt : VAR_SCALAR '.' IDENT '=' expr ';'` | `TT_ASSIGN` | `[TT_FIELD(sval=$3, c=[TT_VAR($1)]), 〈$5〉]` | ✅ | `TT_FIELD` is fresh-built; outer `TT_ASSIGN` is fresh. Field name in `v.sval`, recipient (`$1`) in `c[0]` of TT_FIELD — that is the field-access convention. L→R source order: `$1` `.` `$3` `=` `$5` → tree has `$1` at FIELD's c[0], `$3` at FIELD's `v.sval`, `$5` at ASSIGN's c[1]. Same shape as Icon's `TT_FIELD` (audit 2.x). Clean. |
| 264–266 | `stmt : VAR_ARRAY '[' expr ']' '=' expr ';'` | `TT_FNC` (sval="arr_set") | `[TT_VAR("arr_set"), TT_VAR($1), 〈$3〉, 〈$6〉]` | ⚠ | **Parser-side desugar: `@arr[idx] = val` → `arr_set(arr, idx, val)`.** Source tokens `[ ] =` are all discarded; the `arr_set` call-name is synthesized. Rule 3 violation. **PRF-12-arr-hash-ops.** |
| 267–272 | `stmt : VAR_HASH '<' IDENT '>' '=' expr ';'` / `VAR_HASH '{' expr '}' '=' expr ';'` | `TT_FNC` (sval="hash_set") | `[TT_VAR("hash_set"), TT_VAR($1), TT_QLIT($3) or 〈$3〉, 〈$6〉]` | ⚠ | Same desugar — `%h<k> = v` → `hash_set(h, "k", v)`. **PRF-12-arr-hash-ops.** |
| 273–278 | `stmt : KW_DELETE VAR_HASH '<' IDENT '>' ';'` / `KW_DELETE VAR_HASH '{' expr '}' ';'` | `TT_FNC` (sval="hash_delete") | `[TT_VAR("hash_delete"), TT_VAR($2), TT_QLIT($4) or 〈$4〉]` | ⚠ | Same family. **PRF-12-arr-hash-ops.** |
| 279 | `stmt : expr ';'` | passthrough | — | ✅ | layout-only `;` discarded — permitted |
| 280–294 | `stmt : if_stmt \| while_stmt \| for_stmt \| given_stmt \| ...` | passthrough | — | ✅ | |
| 284–289 | `stmt : KW_TRY block` / `KW_TRY block KW_CATCH block` | `TT_FNC` (sval="raku_try") | `[TT_VAR("raku_try"), 〈$2〉]` or `[TT_VAR("raku_try"), 〈$2〉, 〈$4〉]` | ⚠ | **Parser-side desugar: `try { } catch { }` → `raku_try(blk, catch_blk)`.** Source keywords `try`/`catch` have no tree node-kind analog. **PRF-12-try.** |

### 4.3 Control-flow productions

| Loc | Production | Parent kind | Children L→R | L→R OK? | Notes |
|-----|------------|-------------|--------------|---------|-------|
| 296–303 | `if_stmt : KW_IF '(' expr ')' block [KW_ELSE block]` (3 variants) | `TT_IF` | `[cond, then]` or `[cond, then, else]` | ✅ | Source order matches. Pass-through of `else if_stmt` recursion in third alt also L→R ✅. Clean. |
| 304–306 | `while_stmt : KW_WHILE '(' expr ')' block` | `TT_WHILE` | `[cond, body]` | ✅ | clean |
| 308–312 | `unless_stmt : KW_UNLESS '(' expr ')' block [KW_ELSE block]` | `TT_IF` | `[TT_NOT(cond), then]` or `[TT_NOT(cond), then, else]` | ⚠ | **Parser-side desugar: `unless` → `if (not ...)`.** Source token `unless` has no tree-kind analog; the parser builds a `TT_IF` whose first child is `TT_NOT(cond)`. The wrap is fresh (no mutation) and L→R-sensible (the negation appears at the cond slot where the cond would have appeared). **Rule 3:** the source keyword `unless` has no analog — the parser chose `TT_IF` for it. **This is at the borderline:** the parser-kind-choice freedom (rule 1 of permissions) lets the parser pick TT_IF; the synthesized TT_NOT introduces an extra node not present in the source. Strict reading: rule 3 violation (one extra `TT_NOT` synthesized). Loose reading: TT_NOT IS the structural rendering of `unless`. **FLAG ⚠ for explicit decision.** |
| 314–316 | `until_stmt : KW_UNTIL '(' expr ')' block` | `TT_UNTIL` | `[cond, body]` | ✅ | parser uses TT_UNTIL kind — clean |
| 318–320 | `repeat_stmt : KW_REPEAT block` | `TT_REPEAT` | `[body]` | ✅ | clean |
| 322–334 | `for_stmt` (4 variants) | varies — see below | — | ❌ | Three sub-cases: |
| 323–326 | `for_stmt : KW_FOR add_expr OP_RANGE[/_EX] add_expr OP_ARROW VAR_SCALAR block` → `make_for_range` (line 100–113) | `TT_SEQ_EXPR` containing `[TT_ASSIGN(init), TT_WHILE(cond, body2)]`, where `body2 = TT_SEQ_EXPR([orig_body_children..., TT_ASSIGN(incr)])` | — | ❌ | **Massive parser-side desugar.** `for 1..10 -> $i { BODY }` is unrolled in the parser into: `i = 1; while (i <= 10) { BODY; i = i + 1; }`. Synthesized nodes: a TT_ASSIGN(init), a TT_LE comparison, a TT_ADD with TT_ILIT(1), an inner TT_ASSIGN(incr), a TT_WHILE wrapper, an outer TT_SEQ_EXPR. **None** of these structural pieces are source tokens. The body's children are also spliced into a freshly-built `body2` — that is splicing children OUT of `$7`'s original TT_SEQ_EXPR. Rule 3 violation (massive). Owned: **PRF-12-for-range** (already named). |
| 327–331 | `for_stmt : KW_FOR expr OP_ARROW VAR_SCALAR block` | `TT_EVERY` | `[TT_ITERATE(〈$2〉) with v.sval=$4-name, 〈$5〉]` | ⚠ | The loop variable's name is **stored in `v.sval` of the TT_ITERATE node**, not as a child. Source order `for EXPR -> VAR BLOCK` → `[ITERATE-wrapping-EXPR, BLOCK]`. The VAR sits inside TT_ITERATE's `v.sval`. Rule 3: source token `$4` (the var) appears in `v.sval`, not as a child. Per current scope corrections (value decoding at fresh leaves is allowed), this is **permitted** — the VAR contributes to a node value, the data is preserved on the node. ✅ under corrected scope. Borderline ⚠ for record. |
| 332–334 | `for_stmt : KW_FOR expr block` | `TT_EVERY` | `[〈$2〉 wrapped in TT_ITERATE iff $2->t==TT_VAR, 〈$3〉]` | ⚠ | **Parser inspects `$2->t` and conditionally wraps it.** `if ($2->t == TT_VAR) wrap_in_TT_ITERATE else use $2 directly`. **This is "inspect-kind-and-rearrange" — flagged in the goal §⛔ as a forbidden parser-action shape.** Rule 2 violation in spirit: the parser reads the kind of an existing child and produces a different tree shape based on it. Strictly, it's not mutating $2 — it's wrapping it conditionally, which is rule-compliant on its face. But it's the exact "inspect-kind-and-decide" pattern the goal §⛔ tells us to flag. **FLAG ⚠.** |

### 4.4 `given`/`when`

| Loc | Production | Parent kind | Children L→R | L→R OK? | Notes |
|-----|------------|-------------|--------------|---------|-------|
| 336–350 | `given_stmt : KW_GIVEN expr '{' when_list '}'` | `TT_CASE` | `[disc, val0, body0, val1, body1, …]` | ❌ | The `when_list` is an `ExprList` of `TT_SEQ_EXPR` pairs (built at lines 367–371). The action **unpacks each pair** by reading `pair->c[0]` and `pair->c[1]` and appending them individually to the TT_CASE. **Rule 2:** unpacking `pair` by reading its children and then `exprlist_free(whens)` frees the pair nodes — the pair TT_SEQ_EXPR is built, its children are stolen, then it is freed. This is functionally **dismantling a previously-built node** to repurpose its children. While the children themselves end up in source-order in TT_CASE ✅, the pair node has been destroyed. **FLAG ❌ rule 2.** (Strict reading.) Alternative: build each (val,body) pair directly as two ExprList items rather than wrapping them, then the freelist is just a working scratch. Owned: **PRF-12-given** (proposed). |
| 351–363 | `given_stmt : KW_GIVEN expr '{' when_list KW_DEFAULT block '}'` | `TT_CASE` | `[disc, val0, body0, …, TT_NUL, $6]` | ❌ | Same unpack-and-free. Plus default arm appends `TT_NUL` placeholder for the "value" position then `$6` for the body. The `TT_NUL` placeholder for default's value slot is the same Snocone convention (audit 1.2 row 7). |
| 365–371 | `when_list : when_list KW_WHEN expr block` | `TT_SEQ_EXPR` (pair, never reaches lower) | `[val, body]` | ✅ | pair node is fresh-built and L→R; ultimately consumed by `given_stmt` action |

### 4.5 Subroutine and class declarations

| Loc | Production | Parent kind | Children L→R | L→R OK? | Notes |
|-----|------------|-------------|--------------|---------|-------|
| 373–387 | `sub_decl : KW_SUB IDENT '(' [param_list] ')' block` | `TT_FNC` (sval=name, _id=SUB_TAG_ID, ival=nparams) | `[TT_VAR(name), param1, param2, …, body_child1, body_child2, …]` | ❌ | **Two violations:** (1) `_id` (= `SUB_TAG_ID`) is used to tag this node as a subroutine declaration, and `v.ival` carries `nparams`. Without those, the tree is undecodable — same I5-family issue as Icon's `parse_proc`. (2) The block `$6` is a TT_SEQ_EXPR; its children are **spliced** into `e` via `for (...) expr_add_child(e, body->c[i])` — **the block's children are removed from $6 and re-parented into $e**. The TT_SEQ_EXPR `body` node itself becomes a hollow shell (its `c[]` still holds pointers but those nodes now also live elsewhere). This is **transferring children out of a previously-built node** — rule 2 violation in spirit (the structure of `body` has been altered post-construction). **FLAG: PRF-12-sub already names this; PST-FIELD-1/2 covers `_nalloc`/`_id`.** Plus the child-stealing is a separate concern. |
| 389–419 | `class_decl : KW_CLASS IDENT '{' class_body_list '}'` | `TT_RECORD` (sval=cname) plus side-effects to `add_proc` and `raku_meth_register` and final `$$ = TT_NUL` | `TT_RECORD` children = `[TT_VAR(field1), TT_VAR(field2), …]` (only the `TT_VAR` items from class_body_list) | ❌ | **Heavy parser-side desugar:** (1) class body's `TT_FNC` items (methods, recognized by `_id==SUB_TAG_ID`) are **removed from class_body_list** and pushed to `add_proc` as standalone top-level procs — same family as the auto-hoisted gather defs. (2) Method names are **rewritten in place** (`item->v.sval = (char *)fname` line 407, `item->c[0]->v.sval = (char *)fname` line 409) — this is direct **mutation of a previously-built TT_FNC node** — rule 2 violation. (3) The `class_decl` action returns `TT_NUL` (line 418) instead of the record — the record was already added via `add_proc`. So a `class` statement leaves an empty TT_NUL in the stmt_list, and the actual record + methods land elsewhere via side-effect. Rule 3 violation: source tokens for the class declaration have no surviving tree position. **FLAG: PRF-12-class already names this.** |
| 421–448 | `class_body_list` (4 variants — has-field, method-with-args, method-no-args) | (returns an ExprList of mixed TT_VAR and TT_FNC items) | — | ⚠ | The TT_FNC items built here (lines 429–448) carry `_id=SUB_TAG_ID, ival=np+1` and embed a synthetic `TT_VAR("self")` param. **The synthetic "self" param is rule 3-flag worthy**: there is no source token `self` in `method foo(...)`, the parser invents it. **FLAG: PRF-12-class (synth-self).** |
| 450–458 | `named_arg_list` (2 variants) | (returns an ExprList of alternating `TT_QLIT(key)` + `〈val〉` items) | — | ✅ | local accumulator, L→R clean |
| 460–462 | `param_list` (2 variants) | (returns an ExprList of TT_VAR nodes) | — | ✅ | clean |
| 464–466 | `block : '{' stmt_list '}'` | `TT_SEQ_EXPR` (via `make_seq`) | `[stmt0, stmt1, …]` | ✅ | `make_seq` (line 66) builds fresh TT_SEQ_EXPR and `expr_add_child`s each ExprList item. Layout `{ }` discarded — permitted. Clean. |
| 467–469 | `closure : '{' expr '}'` | passthrough of $2 | — | ✅ | layout `{}` discarded |

### 4.6 Expression cascade

| Loc | Production | Parent kind | Children L→R | L→R OK? | Notes |
|-----|------------|-------------|--------------|---------|-------|
| 470–479 | `expr : VAR_SCALAR '=' expr` | `TT_ASSIGN` | `[TT_VAR($1), 〈$3〉]` | ✅ | clean |
| 472–477 | `expr : KW_GATHER block` | `TT_GATHER` | `[blk->c[0], blk->c[1], …]` | ❌ | **Splices block's children out of `$2` into the new TT_GATHER**, then `$2` (a TT_SEQ_EXPR) is left as a hollow shell. Same child-stealing as `sub_decl`. **Rule 2 (in spirit).** Plus: `TT_GATHER` is then **rewritten in place to `TT_FNC`** by `raku_hoist_gather_in_expr` (lines 636–654) in the post-parse pass — but that pass runs after parsing completes, so it is technically a separate-phase mutation. The parser's own rule 2 violation is the splicing. Owned: **PRF-12-gather** (proposed). |
| 481–482 | `cmp_expr : cmp_expr OP_AND/OP_OR add_expr` | `TT_SEQ` / `TT_ALT` | `[〈$1〉, 〈$3〉]` per reduce | ✅ | **Fresh wrap, right-leaning binary chain** — NOT flattened. Same canonical shape as Icon's `parse_mul`, SNOBOL4's post-PST-SN4-1d `expr3`/`expr4`. Contrasts with Snocone's `sc_flatten_arith` (V1–V6). **Clean.** |
| 483–490 | `cmp_expr : add_expr OP_EQ/NE/'<'/'>'/LE/GE/SEQ/SNE add_expr` | `TT_EQ/NE/LT/GT/LE/GE/LEQ/LNE` | `[〈$1〉, 〈$3〉]` | ✅ | clean |
| 491–508 | `cmp_expr : add_expr OP_SMATCH LIT_REGEX/MATCH_GLOBAL/SUBST` (3 variants) | `TT_FNC` (sval="raku_match"/"raku_match_global"/"raku_subst") | `[TT_VAR(name), 〈$1〉, TT_QLIT(regex_src)]` | ⚠ | **Parser-side desugar: `~~ /regex/` → `raku_match(...)`.** Source operator `~~` and the LIT_REGEX token are baked into a call. Plus the regex source string is stuffed into a TT_QLIT (value decoding at fresh leaf — permitted per scope correction). The **rule 3** issue is the `~~` operator and the `m//`/`s///` markers having no tree-kind analog. **FLAG: PRF-12-smatch** (proposed). |
| 511–514 | `range_expr` (2 variants) | `TT_TO` | `[〈$1〉, 〈$3〉]` | ⚠ | **Both `OP_RANGE` (`..`) and `OP_RANGE_EX` (`..^`) reduce to the same `TT_TO` kind** — the inclusive/exclusive distinction is lost. Per scope correction (kind choice is permitted, ONE kind for two operators is the parser's choice), this is ✅ under the corrected rules. But: the **source distinction is lost** — `1..10` and `1..^10` produce identical trees. **Rule 3 (loose):** the `^` (or its absence) source-token information has no tree analog. Stricter than "value decoding at fresh leaves" because the distinction is operator-semantic, not just a leaf payload. **FLAG ⚠ for explicit decision.** |
| 516–520 | `add_expr` (3 variants — `+`/`-`/`~`) | `TT_ADD/SUB/CAT` | `[〈$1〉, 〈$3〉]` | ✅ | **Fresh wrap, left-leaning binary chain via bison left-recursion** — clean. Same canonical shape as Icon. |
| 522–527 | `mul_expr` (4 variants — `*`/`/`/`%`/OP_DIV) | `TT_MUL/DIV/MOD/DIV` | `[〈$1〉, 〈$3〉]` | ⚠ | `/` and `OP_DIV` (= `div` keyword) **both reduce to TT_DIV** — same operator-fold issue as range_expr. Per scope correction: ✅ (kind choice). |
| 529–532 | `unary_expr : '-'/'!'  unary_expr` | `TT_MNS` / `TT_NOT` | `[〈$2〉]` | ✅ | clean |
| 534 | `postfix_expr : call_expr` | passthrough | — | ✅ | |

### 4.7 Call and field

| Loc | Production | Parent kind | Children L→R | L→R OK? | Notes |
|-----|------------|-------------|--------------|---------|-------|
| 535–540 | `call_expr : IDENT '(' arg_list ')'` | `TT_FNC` (sval=$1) | `[TT_VAR($1), arg0, arg1, …]` | ✅ | `make_call` (line 59) builds fresh TT_FNC with TT_VAR(name) at c[0]. Args spliced from local ExprList — local accumulator, not a tree node. Clean. |
| 541 | `call_expr : IDENT '(' ')'` | `TT_FNC` (sval=$1) | `[TT_VAR($1)]` | ✅ | clean |
| 542–551 | `call_expr : IDENT '.' KW_NEW '(' [named_arg_list] ')'` | `TT_FNC` (sval="raku_new") | `[TT_VAR("raku_new"), TT_QLIT($1), key0, val0, key1, val1, …]` | ⚠ | **Parser-side desugar: `Foo.new(k => v)` → `raku_new("Foo", "k", v, ...)`.** Source `.new(` syntax has no tree node-kind analog; the class name becomes a TT_QLIT arg, not a tree-position parent. **PRF-12-new** (proposed). |
| 552–563 | `call_expr : atom '.' IDENT '(' [arg_list] ')'` | `TT_FNC` (sval="raku_mcall") | `[TT_VAR("raku_mcall"), 〈$1〉, TT_QLIT($3), arg0, arg1, …]` | ⚠ | **Parser-side desugar: `obj.method(args)` → `raku_mcall(obj, "method", args)`.** Method-call syntax baked into a call to a runtime dispatch helper. **PRF-12-mcall** (proposed). |
| 564–568 | `call_expr : atom '.' IDENT` (field, no parens) | `TT_FIELD` (sval=$3) | `[〈$1〉]` | ✅ | field name in `v.sval`, recipient in c[0]. Same shape as line 259. Clean. |
| 569–571 | `call_expr : KW_DIE expr` | `TT_FNC` (sval="raku_die") | `[TT_VAR("raku_die"), 〈$2〉]` | ⚠ | `die` → `raku_die(...)` desugar. **PRF-12-die** (proposed). |
| 572–583 | `call_expr : KW_MAP/GREP/SORT closure expr` etc. | `TT_FNC` (sval="raku_map"/"raku_grep"/"raku_sort") | `[TT_VAR(name), 〈closure〉, 〈expr〉]` | ⚠ | **Parser-side desugar: higher-order builtins.** `map { ... } @arr` → `raku_map(closure, arr)`. Same family. **PRF-12-hof** (proposed). |
| 584 | `call_expr : atom` | passthrough | — | ✅ | |

### 4.8 Atoms

| Loc | Production | Parent kind | Children L→R | L→R OK? | Notes |
|-----|------------|-------------|--------------|---------|-------|
| 591 | `atom : LIT_INT` | `TT_ILIT` (ival) | (none) | ✅ | |
| 592 | `atom : LIT_FLOAT` | `TT_FLIT` (dval) | (none) | ✅ | |
| 593 | `atom : LIT_STR` | `TT_QLIT` (sval) | (none) | ✅ | |
| 594 | `atom : LIT_INTERP_STR` → `lower_interp_str` (75–98) | `TT_CAT` (right-leaning chain) or `TT_QLIT` | for `"a $x b"`: `TT_CAT(TT_CAT(TT_QLIT("a "), TT_VAR("x")), TT_QLIT(" b"))` | ⚠ | **Parser-side string interpolation lowering** — single source token `LIT_INTERP_STR` is **decomposed into multiple tree nodes** representing the literal/var alternation. Per scope correction "value decoding at fresh leaves is permitted" — but `lower_interp_str` is value decoding into a **multi-node tree structure**, not a single leaf. **Borderline case:** the decomposition is fresh-wrap, L→R-by-string-position-within-the-LIT_INTERP_STR-token, no in-place mutation. The decomposition replaces one source token with a fresh structural tree — but parser-kind freedom (rule 1 permission) lets the parser pick the shape for `LIT_INTERP_STR`. **Decision:** treat as **permitted** (analogous to choosing a node kind for an operator; the "operator" here is the interpolation syntax itself). **FLAG ⚠ for record only — not a violation.** |
| 595–597 | `atom : VAR_SCALAR/VAR_ARRAY/VAR_HASH` | `TT_VAR` (sval, sigil stripped) | (none) | ✅ | sigil-strip is value decoding at a fresh leaf — permitted |
| 598–602 | `atom : VAR_CAPTURE` (`$0`, `$1`, …) | `TT_FNC` (sval="raku_capture") | `[TT_VAR("raku_capture"), TT_ILIT(idx)]` | ⚠ | desugar **PRF-12-capture** (proposed) |
| 603–606 | `atom : VAR_NAMED_CAPTURE` (`$<name>`) | `TT_FNC` (sval="raku_named_capture") | `[TT_VAR("raku_named_capture"), TT_QLIT(name)]` | ⚠ | desugar **PRF-12-capture** |
| 607–608 | `atom : VAR_ARRAY '[' expr ']'` | `TT_FNC` (sval="arr_get") | `[TT_VAR("arr_get"), TT_VAR(name), 〈$3〉]` | ⚠ | indexing desugar — **PRF-12-arr-hash-ops** |
| 609–612 | `atom : VAR_HASH '<' IDENT '>'` / `VAR_HASH '{' expr '}'` | `TT_FNC` (sval="hash_get") | `[TT_VAR("hash_get"), TT_VAR(name), TT_QLIT($3) or 〈$3〉]` | ⚠ | **PRF-12-arr-hash-ops** |
| 613–616 | `atom : KW_EXISTS VAR_HASH …` | `TT_FNC` (sval="hash_exists") | `[TT_VAR("hash_exists"), TT_VAR(name), key]` | ⚠ | **PRF-12-arr-hash-ops** |
| 617 | `atom : IDENT` | `TT_VAR` (sval) | (none) | ✅ | clean |
| 618–622 | `atom : VAR_TWIGIL` (`$.foo`, `$!foo`) | `TT_FIELD` (sval=$1, sigil-bearing or stripped) | `[TT_VAR("self")]` | ⚠ | **Parser-synthesizes `self` reference** from a non-source token. Source token `$.foo` is a twigil — its semantic IS "field access on self" — so the parser bakes that in by adding `TT_VAR("self")` as the field recipient. Rule 3: `self` is not in the source. **FLAG ⚠** — but same kind of "the twigil's meaning IS this expansion" justification as `unless`. Strict reading: violation. Loose reading: structural rendering of the twigil. **PRF-12-twigil** (proposed). |
| 623 | `atom : '(' expr ')'` | passthrough | — | ✅ | layout-only parens discarded |

### 4.9 Post-parse passes (gather hoist)

| Loc | Production | Parent kind | Children L→R | L→R OK? | Notes |
|-----|------------|-------------|--------------|---------|-------|
| 632–686 | `raku_lower_hoist_gather_pass` (called at end of `raku_parse_string`, line 693) | (mutates the entire `raku_prog_result` tree post-parse) | — | ❌ | **This is a parser-internal post-pass that walks the tree and rewrites every TT_GATHER node into a TT_FNC reference plus emits a hoisted def at top level.** Specifically lines 647–653: `e->t = TT_FNC; e->v.sval = intern(gname); e->n = 0; e->c = NULL; e->_nalloc = 0;` — **direct in-place rewrite of the tree node's kind, sval, and child array** (after the parse phase but before the parser returns the tree). And lines 671–685: it splices new TT_STMT records into `prog->c[]` at the front by reallocating prog->c. **Rule 2 violation, multiple sites.** Strictly this happens post-parse, but it is inside `raku_parse_string` and is the parser's responsibility to do, so it is in scope. Owned: **PRF-12-gather** (proposed, same rung as the in-grammar `KW_GATHER block` action). |

### 4.10 Raku — re-scoped to ONLY the goal §⛔ rules

Under the three rules (L→R order, no mutate-prior, no source token lifted
out), Raku has **substantial work** but the violations are all of a
common shape: parser-side desugaring to runtime calls. The work item
**PRF-12** in `GOAL-PST-RAKU.md` already covers most of it.

**Withdrawn (not violations under your rules):**
- TT_TO for both `..` and `..^` (kind choice, parser's freedom).
- TT_DIV for both `/` and `div` (kind choice).
- TT_SUSPEND for `take` (kind choice — parser maps keyword to kind).
- TT_UNTIL for `until`, TT_REPEAT for `repeat` (kind choice).
- `lower_interp_str` decomposing LIT_INTERP_STR into TT_CAT chain (value decoding of one source token — analogous to operator-kind choice).
- TT_FIELD with name in `v.sval` (value decoding at fresh leaf).
- `var_node` sigil-strip (value decoding).
- Local ExprList accumulators (`stmt_list`, `arg_list`, `param_list`, `class_body_list`, `named_arg_list`, `when_list`) — not tree nodes.

**Retained under your rules:**

| # | Where | Violation | Owning rung |
|---|---|---|---|
| R1 | `program` synthesizes `main` TT_FNC wrapping orphan statements (lines 206–212) | rule 3: `main` is not a source token | PRF-12-program |
| R2 | `KW_MY IDENT VAR_*` (lines 229–240): the `IDENT` (type annotation) is `free()`'d | rule 3: source token discarded | PRF-12-my-type (new) |
| R3 | `KW_SAY expr ';'` → `TT_FNC("write")` (line 241) | rule 3: keyword `say` not in tree; "write" synthesized | PRF-12-say |
| R4 | `KW_SAY '(' expr ',' expr ')'` → `TT_FNC("raku_say_fh")` (line 243) | rule 3: keyword `say` not in tree; "raku_say_fh" synthesized | PRF-12-say |
| R5 | `KW_PRINT expr ';'` → `TT_FNC("writes")` (line 246) | rule 3 | PRF-12-print |
| R6 | `KW_PRINT '(' expr ',' expr ')'` → `TT_FNC("raku_print_fh")` (line 248) | rule 3 | PRF-12-print |
| R7 | `VAR_ARRAY '[' expr ']' '=' expr` → `arr_set` call (line 264) | rule 3: assignment-to-index syntax desugared | PRF-12-arr-hash-ops (new) |
| R8 | `VAR_HASH '<' IDENT '>' '=' expr` and `VAR_HASH '{' expr '}' '=' expr` → `hash_set` (lines 267, 270) | rule 3 | PRF-12-arr-hash-ops |
| R9 | `KW_DELETE VAR_HASH …` → `hash_delete` (lines 273, 276) | rule 3 | PRF-12-arr-hash-ops |
| R10 | `KW_TRY block [KW_CATCH block]` → `raku_try` call (lines 284, 287) | rule 3 | PRF-12-try (new) |
| R11 | `unless` → `TT_IF(TT_NOT(cond), …)` (lines 308–312) | rule 3 (borderline) | PRF-12-unless (new) — flag for decision |
| R12 | `for ... ` 1..N variant → `make_for_range` builds TT_SEQ_EXPR(TT_ASSIGN, TT_WHILE(...))` with synthesized init/incr/cond (lines 100–113, 323–326) | rule 3 (massive) + rule 2 (block children spliced into fresh body2) | PRF-12-for-range |
| R13 | `for EXPR block` inspects `$2->t==TT_VAR` and conditionally wraps in TT_ITERATE (lines 332–334) | rule 2 (in spirit — inspect-kind-and-rearrange) | PRF-12-for-range |
| R14 | `given_stmt` unpacks `when_list` pair nodes then frees them (lines 343–349, 355–361) | rule 2: pair TT_SEQ_EXPR built then dismantled and freed | PRF-12-given (new) |
| R15 | `sub_decl` splices block body's children into the TT_FNC node (lines 379–380, 385–386) | rule 2: `body` TT_SEQ_EXPR is hollowed out by child stealing | PRF-12-sub |
| R16 | `class_decl` rewrites method TT_FNC's `v.sval` and `c[0]->v.sval` in place (lines 407, 409) | rule 2: prior-built TT_FNC node mutated post-construction | PRF-12-class |
| R17 | `class_decl` hoists methods to top level via `add_proc`, returns `TT_NUL` (lines 411, 418) | rule 3: class declaration produces TT_NUL in stmt_list; the actual class+methods land via side-effect | PRF-12-class |
| R18 | `class_body_list KW_METHOD ...` synthesizes `TT_VAR("self")` param (lines 434, 444) | rule 3: `self` is not a source token | PRF-12-class (synth-self) |
| R19 | `expr : KW_GATHER block` splices block children into TT_GATHER (lines 472–477) | rule 2: `block` TT_SEQ_EXPR hollowed by child stealing | PRF-12-gather (new) |
| R20 | `OP_SMATCH LIT_REGEX/MATCH_GLOBAL/SUBST` → `raku_match`/`raku_match_global`/`raku_subst` calls (lines 491–508) | rule 3: `~~` operator has no tree-kind analog | PRF-12-smatch (new) |
| R21 | `IDENT '.' KW_NEW '(' …` → `raku_new` call (lines 542–551) | rule 3: `.new(` syntax baked into a runtime call | PRF-12-new (new) |
| R22 | `atom '.' IDENT '(' …` → `raku_mcall` (lines 552–563) | rule 3: method-call syntax baked | PRF-12-mcall (new) |
| R23 | `KW_DIE expr` → `raku_die` (lines 569–571) | rule 3 | PRF-12-die (new) |
| R24 | `KW_MAP/GREP/SORT closure expr` → `raku_map`/grep/sort (lines 572–583) | rule 3 | PRF-12-hof (new) |
| R25 | `VAR_CAPTURE` → `raku_capture(idx)`; `VAR_NAMED_CAPTURE` → `raku_named_capture(name)` (lines 598–606) | rule 3 | PRF-12-capture (new) |
| R26 | `VAR_TWIGIL` → `TT_FIELD(sval=$1, c=[TT_VAR("self")])` (lines 618–622) | rule 3: `self` synthesized | PRF-12-twigil (new) |
| R27 | `raku_lower_hoist_gather_pass` rewrites every `TT_GATHER` node's `t`/`v.sval`/`n`/`c` in place (lines 647–653) and splices new TT_STMTs into `prog->c[]` (lines 671–685) | rule 2: in-place rewrite of node kind + child array; rule 3: synthesized def stmts | PRF-12-gather |

**Net Raku status: 27 retained violations under the corrected scope.**
That is much more than Snocone's 11. **PRF-12** in `GOAL-PST-RAKU.md`
already names five rungs (gather, sub, class, program, for-range);
expanding to cover all 27 sites needs additional sub-rungs as listed
above. The rung naming preserves the existing `PRF-12-*` convention.

**Recurring theme:** ~18 of 27 violations are **parser-side desugaring of
Raku-specific syntactic sugar to runtime helper calls** (`say` → `write`,
`@arr[i] = v` → `arr_set`, `Foo.new` → `raku_new`, `try` → `raku_try`,
etc.). These belong in `lower.c` (or a `lower_raku.c` pre-pass). The
parser should produce a syntax-faithful tree (e.g. `TT_SAY(arg)`,
`TT_INDEX_SET(arr, idx, val)`, `TT_NEW(cls, args)`) and `lower` should
recognize those kinds and emit calls to the right runtime helpers.

The other ~9 violations are **child stealing** (block body children
moved into TT_FNC for sub_decl, into TT_GATHER for gather, into
TT_GATHER then rewritten by hoist pass) and **post-construction
mutation** (class method renaming, gather hoist rewriting). Both
are structural — fix patterns are: build the wrapper fresh from the
captured-but-not-spliced child references; defer hoisting/renaming
to lower.

---

## SCAN 5 — Rebus (`src/frontend/rebus/rebus.y`)

Bison grammar, 635 lines. **Hybrid state:** declaration-level structure
(records, function decls, case clause list) still uses `RDecl` /
`RProgram` / `RCase` C-struct types — these are **off-tree**, not
`tree_t`. Expressions and statements are `tree_t` (PST-RB-5b).
Per `GOAL-PST-REBUS.md`, the off-tree decl machinery is still owned by
the larger PST-RB family; the goal for this audit is the **tree-building
productions only** under the three §⛔ rules. Off-tree decl/case
plumbing is recorded but not graded against the §⛔ rules — those rules
apply to `tree_t` productions only.

Two parser-private dynamic accumulator types are used: `SAL` (string-array
list — used for record fields, function params/locals) and `TAL`
(`tree_t*`-array list — used for function-call/index arg lists). Neither
is a tree node; growing them in-place is not a tree mutation.

### 5.1 Off-tree decl machinery (not graded against §⛔ — recorded only)

| Loc | Production | Off-tree output | Notes |
|-----|------------|-----------------|-------|
| 120–122 | `program : decl_list` | sets `prog` (a `RProgram`) | top-level wrapper not built as `tree_t` |
| 124–140 | `decl_list` (3 rules) | appends `RDecl`s to `prog->decls` linked list | not a tree; pure list construction |
| 142–145 | `decl : function_decl \| record_decl` | passthrough of `RDecl*` | — |
| 152–163 | `record_decl : T_RECORD T_IDENT '(' opt_idlist ')'` | `RDecl{kind=RD_RECORD, name=$2, fields=$4->a}` | `name` and `fields` live on `RDecl`, not in `tree_t`. **Off-tree by design.** |
| 165–187 | `function_decl : T_FUNCTION T_IDENT '(' opt_params ')' opt_locals opt_initial stmt_list T_END` | `RDecl{kind=RD_FUNCTION, name=$2, params=$4->a, locals=$7->a, initial_tree=$8, body_tree=$9}` | name/params/locals are off-tree strings; `initial_tree` and `body_tree` are `tree_t` references. **Off-tree wrapper around tree_t children.** |
| 189–192, 194–197, 236–239 | `opt_params`/`opt_locals`/`opt_idlist` | builds `SAL` of strings | off-tree |
| 199–203 | `opt_initial : T_INITIAL compound_stmt \| T_INITIAL stmt ';' \| ε` | passthrough of `tree_t*` or NULL | feeds `RDecl.initial_tree` |
| 231–234 | `idlist_ne` | builds `SAL` | off-tree |
| 409–416 | `caselist` | builds linked list of `RCase` | each `RCase` carries `guard_tree` and `body_tree` which ARE `tree_t`, but the list-spine is off-tree |
| 418–433 | `caseclause` (2 variants) | `RCase{is_default, guard_tree, body_tree}` | guard_tree, body_tree are `tree_t`. The `is_default` flag and linked list ARE off-tree. |
| 619–628 | `arglist`/`arglist_ne` | builds `TAL` of `tree_t*` | local accumulator; not a tree node |

**This is the PST-RB ladder's remaining off-tree work** — owned by
`GOAL-PST-REBUS.md` rungs PST-RB-5* (decl/case plumbing rewrite). Not
audited here against §⛔ because they don't produce `tree_t` nodes.

### 5.2 stmt_list productions (in-place tree mutation candidates)

| Loc | Production | Parent kind | Children L→R | L→R OK? | Notes |
|-----|------------|-------------|--------------|---------|-------|
| 205–211 | `stmt_list : ε \| stmt_list_ne` | `TT_PROGRAM` (empty) or passthrough | `[]` empty, or passthrough | ⚠ | The empty case builds fresh empty `TT_PROGRAM`; the non-empty case passes through `stmt_list_ne` which itself does in-place mutation (see below). The fresh-TT_PROGRAM-on-empty case is ✅. |
| 213–218 | `stmt_list_ne : stmt ';'` | `TT_PROGRAM` | `[$1]` | ✅ | initial 1-child TT_PROGRAM, fresh wrap |
| 219 | `stmt_list_ne : compound_stmt` | passthrough of the TT_PROGRAM that compound_stmt built | — | ✅ | |
| 220–223 | `stmt_list_ne : stmt_list_ne stmt ';'` | mutates `$1` (a TT_PROGRAM) by `expr_add_child($1, $2)` | flat n-ary; **appends into prior** | ❌ | **Rule 2 violation — `expr_add_child($1, $3); $$ = $1;` mutates the previously-built TT_PROGRAM by adding a child.** Same exact pattern as Snocone's `exprlist_ne` (V7 in scan 1) and SNOBOL4's `goto_expr T_CONCAT goto_atom` (W2 in scan 3). This is the canonical §⛔ rule 2 example. Owned: **RB-C-1** (already named in `GOAL-PST-REBUS.md`). |
| 224–227 | `stmt_list_ne : stmt_list_ne compound_stmt` | mutates `$1` (a TT_PROGRAM) by appending each child of `$2` (also a TT_PROGRAM) into it | flat n-ary; **dismantles $2 (child-stealing) + appends into $1 (in-place)** | ❌ | **Double violation of rule 2:** (a) mutates `$1` by appending; (b) the loop `for (int i = 0; i < $2->n; i++) expr_add_child($1, $2->c[i])` steals every child of `$2` (the compound's TT_PROGRAM) and re-parents them under `$1`. `$2` is left as a hollow TT_PROGRAM with `n` unchanged but all its `c[]` pointers now also live under `$1`. Same "child stealing" pattern as Raku's `sub_decl` (R15). Owned: **RB-C-1**. |
| 228 | `stmt_list_ne : stmt_list_ne error ';'` | passthrough of `$1` after `yyerrok` | — | ✅ | error recovery, no tree work |

### 5.3 Statement productions

| Loc | Production | Parent kind | Children L→R | L→R OK? | Notes |
|-----|------------|-------------|--------------|---------|-------|
| 241–249 | `stmt : expr_as_stmt \| if_stmt \| ...` | passthrough | — | ✅ | |
| 250 | `stmt : T_EXIT` | `TT_LOOP_BREAK` | `[]` | ✅ | parser uses TT_LOOP_BREAK kind for Rebus `exit` keyword — permitted kind choice |
| 251 | `stmt : T_NEXT` | `TT_LOOP_NEXT` | `[]` | ✅ | |
| 252 | `stmt : T_FAIL` | `TT_PROC_FAIL` | `[]` | ✅ | |
| 253 | `stmt : T_STOP` | `TT_END` | `[]` | ✅ | clean |
| 254–258 | `stmt : T_RETURN opt_expr` | `TT_RETURN` | `[]` or `[〈$2〉]` | ✅ | clean |
| 259 | `stmt : compound_stmt` | passthrough (TT_PROGRAM from compound_stmt) | — | ✅ | |
| 262–263 | `expr_as_stmt : expr` | passthrough | — | ✅ | |
| 264–270 | `expr_as_stmt : expr '?' pat_expr` | `TT_SCAN` | `[subj, pat]` | ✅ | Fresh wrap, source order ✅. **Same pattern as SNOBOL4's TT_SCAN — permitted under corrected scope (a parser node built from N source positions is fine as long as fresh-wrap + L→R).** Withdrawn from earlier audit's flag list. |
| 271–278 | `expr_as_stmt : expr '?' pat_expr T_ARROW expr` | `TT_SCAN` | `[subj, pat, repl]` | ✅ | 3-child variant for replacement. Fresh wrap, L→R ✅. The downstream split into separate consumer fields is consumer-side. |
| 279–286 | `expr_as_stmt : expr T_QUESTMINUS pat_expr` | `TT_SCAN` | `[subj, pat, TT_NUL]` | ✅ | replace-with-null variant. TT_NUL as filler for "no replacement" is the same convention as Snocone empty-value slots — permitted. |
| 289–291 | `compound_stmt : '{' stmt_list '}'` | passthrough of TT_PROGRAM | — | ✅ | layout braces discarded — permitted |
| 293–295 | `stmt_body : stmt` | passthrough | — | ✅ | |

### 5.4 Control-flow productions

| Loc | Production | Parent kind | Children L→R | L→R OK? | Notes |
|-----|------------|-------------|--------------|---------|-------|
| 297–305 | `if_stmt : T_IF stmt T_THEN opt_semi stmt_body` | `TT_IF` | `[cond, then]` | ✅ | fresh wrap, L→R ✅ |
| 306–314 | `if_stmt : T_IF stmt T_THEN opt_semi stmt_body T_ELSE opt_semi stmt_body` | `TT_IF` | `[cond, then, else]` | ✅ | clean |
| 317–328 | `unless_stmt : T_UNLESS stmt T_THEN opt_semi stmt_body` | `TT_IF` | `[TT_NOT(cond), then]` | ⚠ | **Parser-side desugar: `unless` → `TT_IF(TT_NOT(...))`.** Same case as Raku R11. The `TT_NOT` wrap node is synthesized — no `T_NOT` source token. Comment in the action itself acknowledges: `/* unless cond then body == if ~cond then body */`. **FLAG ⚠ (rule 3 — strict) / ✅ (loose, kind choice).** New rung name: **RB-C-2 unless** (proposed). |
| 331–340 | `while_stmt : T_WHILE stmt T_DO opt_semi stmt_body` | `TT_WHILE` | `[cond, body]` | ✅ | clean |
| 342–351 | `until_stmt : T_UNTIL stmt T_DO opt_semi stmt_body` | `TT_UNTIL` | `[cond, body]` | ✅ | clean — TT_UNTIL is its own kind |
| 353–361 | `repeat_stmt : T_REPEAT opt_semi stmt_body` | `TT_REPEAT` | `[body]` | ✅ | clean |
| 363–374 | `for_stmt : T_FOR T_IDENT T_FROM expr T_TO expr T_DO opt_semi stmt_body` | `TT_FOR` (sval=loop_var) | `[from, to, TT_NUL, body]` | ⚠ | The loop variable name lives in `v.sval` (value decoding — permitted) not as a child. The omitted `by` slot is filled with `TT_NUL` placeholder — same convention as Rebus replace-with-null, ✅. Source order is `for VAR from FROM to TO do BODY` → children `[from, to, TT_NUL, body]`. **The order in the tree is from, to, by, body — which is the SOURCE-CLAUSE order, but the parser inserts TT_NUL for the missing `by`.** ✅ under corrected scope (TT_NUL filler is permitted). |
| 375–385 | `for_stmt : T_FOR T_IDENT T_FROM expr T_TO expr T_BY expr T_DO opt_semi stmt_body` | `TT_FOR` (sval=loop_var) | `[from, to, by, body]` | ✅ | clean — 4 children all from source |
| 388–406 | `case_stmt : T_CASE expr T_OF '{' caselist '}'` | `TT_CASE` | `[expr, TT_IF(guard,body), TT_IF(guard,body), …, TT_IF(TT_NUL,body), …]` | ❌ | **Two violations.** (a) The action **walks the off-tree RCase linked list ($5) and builds fresh TT_IF nodes per clause** — `tree_t *clause = ast_node_new(TT_IF); expr_add_child(clause, c->guard_tree); expr_add_child(clause, c->body_tree)`. This is creating tree structure from non-tree data. While the **child order in TT_CASE is L→R** ✅ (clauses appear in source order), each clause is a **synthesized TT_IF wrapper** — there is no `if`/`then` source token at each clause. Rule 3 violation: synthesized TT_IF kind wraps each clause where the source had only `guard:body`. (b) For the default arm, `expr_add_child(clause, ast_node_new(TT_NUL))` synthesizes a TT_NUL placeholder for the missing guard. This is **permitted** as a filler convention (per Snocone audit V14 withdrawal). The TT_IF wrapper is the violation. New rung: **RB-C-3 case-clause** (proposed) — should produce `TT_CASE(expr, guard0, body0, guard1, body1, …, TT_NUL, body_default)` flat n-ary alternating like Raku does (R14 / PRF-12-given), eliminating the TT_IF wrapper. |

### 5.5 Expression cascade

| Loc | Production | Parent kind | Children L→R | L→R OK? | Notes |
|-----|------------|-------------|--------------|---------|-------|
| 441–444 | `assign_expr : alt_expr T_ASSIGN assign_expr` | `TT_ASSIGN` | `[〈$1〉, 〈$3〉]` | ✅ | fresh wrap |
| 445–448 | `T_EXCHANGE` | `TT_SWAP` | `[〈$1〉, 〈$3〉]` | ✅ | |
| 449–456 | `T_ADDASSIGN` (`+:=`) | `TT_ASSIGN` | `[TT_VAR(strdup($1->v.sval)), TT_ADD($1, $3)]` | ❌ | **Massive set of violations.** (a) `lhs2 = ast_node_new(TT_VAR); lhs2->v.sval = strdup($1->v.sval ? $1->v.sval : "")` — reads the lhs's `v.sval` and builds a **second, synthesized** TT_VAR leaf with the same name. **The lhs appears twice in the tree** — once as `$1` (under TT_ADD) and once as the synthesized `lhs2` (under TT_ASSIGN). Rule 3: the lhs's second occurrence is a synthesized non-source-token leaf. (b) The assumption that `$1->v.sval` exists is fragile — `$1` could be any expression (`alt_expr` can be a complex expression), but the action assumes `$1` is a TT_VAR with a name. For non-TT_VAR lhs, this produces a malformed tree (an empty-name TT_VAR is created). (c) This is **parser-side desugaring** of augmented assignment — should produce `TT_AUGOP` with ival=op as Snocone and Icon do. Goal §⛔ rule 3 violation. New rung: **RB-C-4 augop** (proposed) — replace `+:=`/`-:=`/`||:=` desugaring with `TT_AUGOP(lhs, rhs)` carrying the operator in `ival`. |
| 457–463 | `T_SUBASSIGN` (`-:=`) | `TT_ASSIGN` | `[TT_VAR(synth), TT_SUB($1, $3)]` | ❌ | Same as above. |
| 464–470 | `T_CATASSIGN` (`\|\|:=`) | `TT_ASSIGN` | `[TT_VAR(synth), TT_CAT($1, $3)]` | ❌ | Same. |
| 473–479 | `alt_expr : alt_expr '\|' cat_expr` | `TT_ALT` | `[〈$1〉, 〈$3〉]` | ✅ | **Fresh wrap, right-leaning chain — clean.** Same canonical shape as Icon/Raku, contrasts with Snocone's `sc_flatten_arith`. |
| 481–491 | `cat_expr : cat_expr T_STRCAT/'&' cmp_expr` (2 rules, both reduce to TT_CAT) | `TT_CAT` | `[〈$1〉, 〈$3〉]` | ✅ | Two source operators (`\|\|` and `&`) reduce to same `TT_CAT` kind — kind choice, permitted. Source info partially lost: `&` and `\|\|` are not the same operator (one concatenates always, the other does so with whitespace handling — or something Rebus-specific). **Borderline:** like Raku's TT_TO for `..`/`..^`. Per corrected scope: ✅ (kind choice). |
| 493–507 | `cmp_expr : cmp_expr OP add_expr` (11 ops: `=` `T_NE` `<` `T_LE` `>` `T_GE` `T_SEQ` `T_SNE` `T_SLT` `T_SLE` `T_SGT` `T_SGE`) | `TT_EQ/NE/LT/LE/GT/GE/LEQ/LNE/LLT/LLE/LGT/LGE` | `[〈$1〉, 〈$3〉]` | ✅ | each fresh wrap |
| 509–513 | `add_expr : add_expr '+'/'-' mul_expr` | `TT_ADD/SUB` | `[〈$1〉, 〈$3〉]` | ✅ | fresh wrap, left-leaning binary chain via left-recursion. Clean. |
| 515–520 | `mul_expr : mul_expr '*'/'/'/'%'` | `TT_MUL/DIV/MOD` | `[〈$1〉, 〈$3〉]` | ✅ | |
| 522–526 | `pow_expr : unary_expr '^'/T_STARSTAR pow_expr` (2 rules → TT_POW) | `TT_POW` | `[〈$1〉, 〈$3〉]` | ✅ | both `^` and `**` reduce to TT_POW. Kind choice — ✅. Right-associative via right-recursion. |
| 528–547 | `unary_expr` (10 unary prefixes) | TT_MNS/NOT/NONNULL/ITERATE/CAPT_CURSOR/INDIRECT/CAPT_COND_ASGN | `[〈$2〉]` (or special cases) | mostly ✅ | |
| 530 | `'-' unary_expr` | `TT_MNS` | `[〈$2〉]` | ✅ | |
| 531 | `'+' unary_expr` | passthrough (`$$ = $2`) | — | ⚠ | **Unary plus is silently dropped** — the source `+x` becomes `x` with no tree analog for the `+` operator. Comment: `/* unary plus is identity */`. Rule 3 (strict): source token `+` lifted out of the tree. Loose: arithmetic identity, no information lost. **FLAG ⚠** — borderline like `unless`. |
| 532–533 | `'~' unary_expr` and `'\' unary_expr` | `TT_NOT` | `[〈$2〉]` | ⚠ | **Two different source operators (`~` and `\`) both reduce to TT_NOT**. Kind choice — ✅ per corrected scope, but source distinction lost. (`~` is likely string-not, `\` is structural-not — semantically distinct in Rebus.) Borderline. |
| 534 | `'/' unary_expr` | `TT_NONNULL` | `[〈$2〉]` | ✅ | clean |
| 535 | `'!' unary_expr` | `TT_ITERATE` | `[〈$2〉]` | ✅ | clean — parser maps `!x` to iterate kind |
| 536–539 | `'@' T_IDENT` | `TT_CAPT_CURSOR` (sval=$2) | (none, name in `v.sval`) | ⚠ | The `T_IDENT` token name is captured as `v.sval` rather than as a `TT_VAR` child. Value decoding at a fresh leaf — **permitted** under corrected scope. Borderline ⚠ for record. Note: `@` followed by an arbitrary IDENT is restricted at the parser level; other unaries take `unary_expr`. |
| 540 | `'$' unary_expr` | `TT_INDIRECT` | `[〈$2〉]` | ✅ | |
| 541–546 | `'.' unary_expr` | `TT_CAPT_COND_ASGN` | `[TT_NUL, 〈$2〉]` | ⚠ | **Parser synthesizes TT_NUL placeholder for the implicit subject.** Comment: `/* prefix dot = conditional capture with implicit subject */`. Rule 3 (strict): the implicit subject has no source token — but TT_NUL placeholders are explicitly permitted as filler convention (Snocone V14 withdrawal). Per corrected scope: ✅. |

### 5.6 Postfix and primary

| Loc | Production | Parent kind | Children L→R | L→R OK? | Notes |
|-----|------------|-------------|--------------|---------|-------|
| 551–569 | `postfix_expr : postfix_expr '(' arglist ')'` | `TT_FNC` | `[arg0, arg1, …]` or `[$1, arg0, arg1, …]` | ❌ | **Three violations.** (a) **Parser inspects `$1->t == TT_VAR`** to decide whether to put the name in `v.sval` or to put `$1` as `c[0]` — this is the §⛔ "inspect-kind-and-rearrange" forbidden pattern. **Rule 2 in spirit.** (b) For the TT_VAR case, the action does `$1->v.sval = NULL` after "stealing" the name — **mutating the previously-built TT_VAR node by clearing its sval** (line 559). **Rule 2 violation: in-place mutation of a built node.** (Worse, `$1` may then be unreachable as a leaf but still hold an empty-name TT_VAR that's leaked or freed inconsistently.) (c) The two-branch shape gives **TT_FNC two different tree shapes depending on callee type** — for `foo(args)` you get `TT_FNC(sval="foo")[args]`, for `(expr)(args)` you get `TT_FNC()[expr, args]`. Asymmetric child layout depending on parser-side kind inspection. **Owned: new rung RB-C-5 postfix-call** (proposed) — always produce `TT_FNC[callee, args...]` with callee as `c[0]` (Icon convention), and lower.c reads `c[0]` to dispatch built-in vs indirect call. |
| 570–579 | `postfix_expr : postfix_expr '[' arglist ']'` | `TT_IDX` | `[$1, arg0, arg1, …]` | ✅ | Source order matches; TT_NUL fillers for omitted args (line 576) are permitted; arglist TAL is freed. Clean. |
| 580–588 | `postfix_expr : postfix_expr '[' expr T_PLUSCOLON expr ']'` (section `[i +: len]`) | `TT_IDX` | `[$1, $3, $5]` | ⚠ | **Same kind (`TT_IDX`) used for both subscript `a[i,j,k]` and section `a[i +: len]`** — kind reuse for two distinct operators. Per corrected scope: ✅ (kind choice — Icon uses TT_SECTION_PLUS instead, but kind divergence between frontends is permitted). Borderline ⚠ for record. |
| 589–593 | `postfix_expr '.' primary` | `TT_CAPT_COND_ASGN` | `[〈$1〉, 〈$3〉]` | ✅ | clean |
| 594–598 | `postfix_expr '$' primary` | `TT_CAPT_IMMED_ASGN` | `[〈$1〉, 〈$3〉]` | ✅ | clean |
| 601–608 | `primary` (6 variants — STR, INT, REAL, KEYWORD, IDENT, parens) | TT_QLIT/ILIT/FLIT/KEYWORD/TT_VAR or passthrough | (none for leaves, or `$2` for parens) | ✅ | clean — paren passthrough discards layout, all others are fresh leaves with value decoding at a single source token. Note: `strdup($1)` (line 602–606) — fresh allocation of string content, not a "lifted token" concern. |
| 610–612 | `pat_expr : expr` | passthrough | — | ✅ | |
| 614–617 | `opt_expr : ε \| expr` | NULL or passthrough | — | ✅ | |

### 5.7 Rebus — re-scoped to ONLY the goal §⛔ rules

**Withdrawn (not violations under your rules):**
- TT_NUL fillers for omitted slots in `for` (no `by`), `case` (default guard), prefix-dot (implicit subject) — permitted convention.
- Two-source-operator-one-kind cases: `^`/`**` → TT_POW, `&`/`\|\|` → TT_CAT, `~`/`\` → TT_NOT (kind choice, permitted).
- TT_SCAN with 2 or 3 children for `subj ? pat` / `subj ? pat -> repl` / `subj ?- pat` — fresh wrap, L→R, consumer-side split is not a parser concern.
- Loop variable name in `v.sval` of TT_FOR (value decoding).
- `@T_IDENT` capturing identifier name in `v.sval` of TT_CAPT_CURSOR (value decoding).
- TT_IDX used for both subscript and section (kind reuse — kind choice).
- `'+' unary_expr` is identity passthrough — borderline; arithmetic identity loses no semantic info. Could be flagged but is the same shape as paren-passthrough.

**Retained under your rules:**

| # | Where | Violation | Owning rung | Status |
|---|---|---|---|---|
| Rb1 | `stmt_list_ne : stmt_list_ne stmt ';'` (line 220) | rule 2: `expr_add_child($1, $3); $$ = $1;` mutates prior TT_PROGRAM | **RB-C-1** | ✅ 2026-05-18 (compound_stmt child-steal fixed; list-append `expr_add_child($1,$2)` is accepted Bison idiom per corrected scope) |
| Rb2 | `stmt_list_ne : stmt_list_ne compound_stmt` (line 224) | rule 2 + child-stealing: appends every child of `$2` into `$1` then leaves `$2` hollow | **RB-C-1** | ✅ 2026-05-18 (`$2->c[i]` child-steal replaced; children now added via single `expr_add_child` per compound_stmt child) |
| Rb3 | `unless_stmt` (line 317) synthesizes TT_NOT wrapping cond | rule 3 (strict reading): synthesized TT_NOT kind not present as source token | **RB-C-2** | ✅ 2026-05-19 `83bc4ab3` (TT_UNLESS added; desugar moved to lower.c) |
| Rb4 | `case_stmt` (line 388) wraps each clause in synthesized TT_IF | rule 3: TT_IF synthesized per clause; source has only `guard:body` | **RB-C-3** | ✅ 2026-05-19 `ccc11220` (flat TT_CASE alternating pairs; RCase freed in case_stmt `90658061`) |
| Rb5 | `T_ADDASSIGN`/`T_SUBASSIGN`/`T_CATASSIGN` (lines 449–470): synthesizes a duplicate `TT_VAR(name)` lhs by reading `$1->v.sval` | rule 3: duplicated lhs is synthesized | **RB-C-4** | ✅ 2026-05-19 `0458da59` (TT_AUGOP; desugar in lower_tree_expr) |
| Rb6 | `postfix_expr : postfix_expr '(' arglist ')'` (line 551): inspects `$1->t == TT_VAR` and either steals `$1->v.sval` or wraps `$1` as a child | rule 2: inspect-kind-and-rearrange + mutates `$1->v.sval = NULL` | **RB-C-5** | ✅ 2026-05-19 `2a9aa511` (always TT_FNC[callee=c[0], args]; lower extracts name from c[0]) |

**Net Rebus status: 0 retained §⛔ violations. Phase 1 C COMPLETE 2026-05-19 (Sonnet 4.6).**

Off-tree machinery status: RDecl/RDKind/RProgram deleted `8af2e2e1`; RCase retained as
parser-local scratch with free loop `90658061` (Option A, documented in rebus.h).
`rebus_parsed_program` is now `tree_t*` of kind `TT_PROGRAM`.

---

## SCAN 6 — Prolog (`src/frontend/prolog/prolog_parse.c`)

Hand-rolled recursive-descent (Pratt-style operator-precedence) parser.
Tree-producing functions are `pt_primary`, `pt_term`, `pt_list`,
`pt_args`, `pt_binop`, `pt_make_clause`, `pt_flatten_conj`,
`pt_maybe_ifthenelse`. Each parses a chunk of source tokens and returns
a `tree_t*` (or, for `pt_args`, attaches children to an externally-built
parent).

**Hybrid state:** the non-DCG path is fully `tree_t` (post-PST-PL-6f); the
DCG path (`-->` clauses) still re-parses via `Term*` (`parse_term`,
`dcg_expand_clause`) and produces an off-tree `Term*` for `cl->head` and
`cl->body`. The audit grades the tree_t path only; the DCG/Term* path
is a separate axis owned by `GOAL-PST-PROLOG.md` rung **PST-PL-6f**
(in-progress) and beyond.

The top-level `prolog_parse` (line 1112) iterates clauses and builds a
linked list of `PlClause` structs. Each PlClause carries a `cl->tr`
(`tree_t*`) holding the clause's `pt_make_clause` result. **There is no
top-level TT_PROGRAM tree** — the program is the off-tree linked list.
This is a known mirror gap covered by `GOAL-PST-PROLOG.md` rungs
PST-PL-7* (tree-only program shape).

### 6.1 Off-tree machinery (not graded against §⛔ — recorded only)

| Loc | Function | Off-tree output | Notes |
|-----|----------|-----------------|-------|
| 1026–1110 | `parse_clause` | `PlClause{tr=tree_t*, head/body=Term* if DCG, nvar/var_names/var_terms if DCG, lineno}` | `cl->tr` is `tree_t*` (built via `pt_make_clause`). For DCG (`-->`) clauses, `cl->head` and `cl->body` are `Term*` (off-tree) and `cl->tr=NULL`. **Hybrid by design.** |
| 1112–1155 | `prolog_parse` | `PlProgram{head, tail, nclauses, nerrors}` linked list | not a `tree_t`. Owned: PST-PL-7. |
| 400–402 | `TreeScope` struct (`TSEntry e[256]`, `n`) | parser-local var name table | local working state, not in tree |

### 6.2 `ts_get` — variable interning

| Loc | Function | Parent kind | Children L→R | L→R OK? | Notes |
|-----|----------|-------------|--------------|---------|-------|
| 408–429 | `ts_get(ts, name)` | `TT_VAR` (sval=interned-name) | (none) | ✅ | **Fresh TT_VAR each call** — comment line 411–412: `/* Return a fresh TT_VAR node aliased to the same name; structural equivalence checked by name in 6c. */`. The `TreeScope` itself is parser-local working state (variable interning to share a string pointer between multiple TT_VAR occurrences within a clause). The tree has multiple TT_VAR leaves with `v.sval` pointing to the same interned string, which is value sharing — not tree sharing. Clean. |

### 6.3 `pt_list` — list literal `[e1, e2, ..., en | tail]`

| Loc | Function | Parent kind | Children L→R | L→R OK? | Notes |
|-----|----------|-------------|--------------|---------|-------|
| 436–469 | `pt_list` | `TT_MAKELIST` (v.ival=0 for proper list, =1 if `|tail` present) | `[e1, e2, …, en]` or `[e1, …, en, tail]` | ✅ | **Fresh wrap, L→R, `ast_push` is the standard tree append (not a mutation of a prior tree node).** The `v.ival=1` marker for "has explicit tail" is value decoding at the fresh leaf — permitted under corrected scope. Empty list (no elements, `]` immediately) builds a fresh empty TT_MAKELIST — ✅. Clean. |

### 6.4 `pt_args` — comma-separated arguments

| Loc | Function | Parent kind | Children L→R | L→R OK? | Notes |
|-----|----------|-------------|--------------|---------|-------|
| 471–489 | `pt_args(p, ts, parent)` | (no node — attaches to existing `parent`) | appends each parsed `tree_t*` child to `parent` via `ast_push(parent, a)` | ⚠ | **`pt_args` mutates `parent` by appending children to it.** This is **NOT** a §⛔ rule 2 violation — `parent` was created **fresh in the caller's frame** and is then immediately populated. The caller pattern is `tree_t *fnc = ast_node_new(TT_FNC); fnc->v.sval = strdup(...); pt_args(p, ts, fnc); return fnc;` — the node is created, populated, returned, in one contiguous logical step. Children are appended in source-token order ✅. This is **build-time population**, not **post-construction mutation of a prior child**. Distinguishing the two is what the goal §⛔ rule 2 is about. **Clean** under corrected scope. (Compare to Snocone's `expr_add_child($1, $3); $$=$1;` where `$1` is a node built in an earlier reduction.) |

### 6.5 `pt_binop` — binary operator reduce

| Loc | Function | Parent kind | Children L→R | L→R OK? | Notes |
|-----|----------|-------------|--------------|---------|-------|
| 493–499 | `pt_binop(op, lhs, rhs)` | `TT_FNC` (sval=op) | `[lhs, rhs]` | ✅ | **The canonical pure reduce.** Comment line 491–492: `/* Pure reduce action: wrap lhs and rhs as children of TT_FNC(op). No structural reasoning — just node(kind, children-in-source-order). */`. Fresh TT_FNC, op-name as sval (value decoding), lhs at c[0], rhs at c[1] in source token order. **Clean — this is the reference shape every other parser's binary-op productions should match.** |

### 6.6 `pt_flatten_conj` — n-ary conjunction flattening

| Loc | Function | Parent kind | Children L→R | L→R OK? | Notes |
|-----|----------|-------------|--------------|---------|-------|
| 508–516 | `pt_flatten_conj(t, prog)` | (no new node — populates an existing `prog` TT_PROGRAM) | recurses into `t`; if `t` is `TT_FNC(",")`, walks its children; else appends `t` to `prog` | ⚠ | **Inspects `t->t == TT_FNC && strcmp(t->v.sval, ",") == 0` to decide whether to recurse or just append.** This is the §⛔ "inspect-kind-and-decide" pattern, used **after construction** of the conjunction node. **Critical decision point:** is this a violation? **The pattern is a tree-walk consumer that reads child kinds to flatten n-ary structure — but it is called from `pt_make_clause` (line 549) and `pt_maybe_ifthenelse` (lines 530, 532), which are parser-internal helpers that produce final clause/IF nodes.** Strictly: the parser is reading `t->t` and `t->v.sval` to decide whether to unpack `t`. That is exactly what the goal §⛔ rule 2 forbids ("No reduction action may 'look inside' a previously-built child and decide to attach to it instead of wrapping it"). Although `pt_flatten_conj` does not **mutate** `t` (it leaves the comma-FNC node intact, just walks its children for the flatten), it does **dismantle structure built by `pt_binop`** — the comma-FNC nodes are walked and their children re-parented into `prog`. **The original comma-TT_FNC node and any intermediate comma-TT_FNCs in the chain are orphaned** (still allocated, but with their c[] children now also under `prog`). This is **child-stealing** — the same family as Raku's `sub_decl` (R15) and Rebus's `stmt_list_ne compound_stmt` (Rb2). **Rule 2 violation.** This is exactly what the existing rung **PST-PL-6h** in `GOAL-PST-PROLOG.md` flags. |

### 6.7 `pt_maybe_ifthenelse` — `;(->(C,T),E)` → TT_IF

| Loc | Function | Parent kind | Children L→R | L→R OK? | Notes |
|-----|----------|-------------|--------------|---------|-------|
| 521–538 | `pt_maybe_ifthenelse(semi_node)` | `TT_IF` (or passthrough of input) | input → if recognized: `[cond, then, else]`; else passthrough | ❌ | **Multiple violations in one function:** (a) **inspects `semi_node->t == TT_FNC`, `semi_node->v.sval == ";"`, `left->v.sval == "->"`** — three layers of inspect-kind-and-shape. (b) **`pt_flatten_conj` is called on `left->c[1]` and on `right`** — child stealing from the previously-built `;` and `->` nodes (Rule 2 — same as 6.6). (c) **The `;`-TT_FNC node and the `->`-TT_FNC node are both abandoned** (not deallocated, but orphaned). The resulting TT_IF takes `left->c[0]` (cond from the `->` node) and the two flattened TT_PROGRAMs as children. Strictly, the source tokens `;` and `->` are **lifted out of the tree** entirely — replaced by TT_IF. Rule 3 violation. (d) **Lines 535–536** then do conditional unwrap: `then_prog->n == 1 ? then_prog->c[0] : then_prog`. **This is "inspect-kind-and-rearrange"** post-construction. Even if it's the new node's own freshly-built child, **the choice between "use the child directly" and "use the wrapper" is made by reading `n`**. Owned: **PST-PL-6h** (already named in `GOAL-PST-PROLOG.md`). |

### 6.8 `pt_make_clause` — TT_CLAUSE wrapper

| Loc | Function | Parent kind | Children L→R | L→R OK? | Notes |
|-----|----------|-------------|--------------|---------|-------|
| 540–552 | `pt_make_clause(head_tr, body_tr)` | `TT_CLAUSE` | `[head_or_TT_NUL, TT_PROGRAM(body_flat...)]` | ⚠ | **Two concerns:** (a) Directive clauses (no head) → `head_tr=NULL` → ast_pushes `TT_NUL` as a filler. **TT_NUL placeholder is permitted** under corrected scope ✅. (b) **Body is wrapped in a fresh TT_PROGRAM and `pt_flatten_conj` is called to flatten the comma-tree into n-ary children.** This is the child-stealing from 6.6 — the parser disassembles the comma-TT_FNC chain that `pt_term` already built and re-builds it as a TT_PROGRAM. **Rule 2 violation by transitivity through `pt_flatten_conj`.** A clean alternative: keep the comma-TT_FNC chain intact under TT_CLAUSE's c[1]; lower.c flattens at consumption time. **Owned: PST-PL-6h.** |

### 6.9 `pt_primary` — leaves and parenthesized expressions

| Loc | Token kind handled | Parent kind | Children L→R | L→R OK? | Notes |
|-----|--------------------|-------------|--------------|---------|-------|
| 557–558 | `TK_VAR` | `TT_VAR` (via `ts_get`) | (none) | ✅ | |
| 559–563 | `TK_ANON` (`_`) | `TT_VAR` (sval=`"_"`) | (none) | ✅ | each anonymous `_` is a **fresh** unique TT_VAR — but they all share the literal string `"_"` via `strdup`. **Note:** this is **not** PST-PL-SC-3 territory; that was about how slot assignment treated them. Per scope correction this is value decoding. Clean. |
| 564–578 | `TK_INT`/`TK_FLOAT`/`TK_STRING` | `TT_ILIT`/`FLIT`/`QLIT` | (none) | ✅ | clean |
| 579–615 | `TK_ATOM` (atom or compound term `atom(...)`) | `TT_FNC` if `(`, special-directive atoms also `TT_FNC`, `TT_MAKELIST` for `[]`, else `TT_QLIT` | for compound: `[arg0, arg1, …]`; for bare atom: (none) | ⚠ | **Two subtle issues:** (a) **Parser inspects upcoming token (`TK_LPAREN`?) and decides whether to build a TT_FNC (compound) or TT_QLIT (atom).** This is **legitimate parser decision-making** — picking a node kind based on source-token lookahead is the parser's job. ✅ (rule 1 permission). (b) Lines 590–608: **the parser hardcodes a set of special directive atoms** (`dynamic`, `discontiguous`, `multifile`, `module_transparent`, `meta_predicate`, `use_module`, `ensure_loaded`, `mode`) that are recognized as "directive atom with one argument" even **without** following `(`. This is **parser-side semantic dispatch by identifier text** — analogous to SNOBOL4's `pat_prim_kind` (audit line 408). Per corrected scope, that pattern was **explicitly permitted** ("parser-side semantic dispatch by identifier text" — `pat_prim_kind` picking TT_ANY/TT_SPAN/… is the parser's free choice). **By the same rule, prolog's directive-atom-with-arg dispatch is also permitted.** ✅ under corrected scope. |
| 609–611 | `tk.text == "[]"` | `TT_MAKELIST` | (none) | ✅ | empty list atom |
| 616–617 | `TK_CUT` | `TT_CUT` | (none) | ✅ | clean |
| 619–627 | `TK_LPAREN expr TK_RPAREN` | passthrough of inner expr | — | ✅ | layout-only parens discarded |
| 628–629 | `TK_LBRACKET` → `pt_list` | TT_MAKELIST (from pt_list) | (see 6.3) | ✅ | |
| 630–644 | `TK_COMMA`/`TK_SEMI` as primary | `TT_FNC` (sval="," or ";") with explicit `(...)` args | `[arg0, arg1, …]` | ✅ | `,(a,b)` and `;(a,b)` written explicitly. Clean. The bare-comma/bare-semi case returns NULL. |
| 645–708 | `TK_OP` (binary or unary prefix operator used in prefix position or followed by `(`) | `TT_FNC` (sval=op-text) with various arities, or `TT_ILIT`/`FLIT` for unary minus/plus folding | varies | ⚠ | **Numeric folding:** `-NUM` and `-FLOAT` and `+NUM` and `+FLOAT` (lines 660–692) are **folded into the literal** at parse time. E.g. `-42` produces a single `TT_ILIT(v.ival=-42)`, NOT `TT_FNC("-")[TT_ILIT(42)]`. **This collapses two source tokens (`-` and `42`) into one fresh leaf via value decoding.** Per corrected scope: **value decoding at a fresh leaf is permitted** (the scope correction explicitly allows `$IDENT` → `TT_QLIT("$IDENT")` as multi-token value decoding). Clean. The non-folding cases (e.g. `\+ goal`, `\ x`, `- expr`, `+ expr` where expr is not a numeric literal) build `TT_FNC(op)[arg]` — fresh wrap, L→R, ✅. |
| 645–708 (cont.) | `TK_OP` followed by `(...)` — `op(args)` | `TT_FNC` (sval=op-text) | `[arg0, arg1, …]` | ✅ | clean |
| 645–708 (cont.) | `TK_OP` bare (no `(`, not handled above) | `TT_QLIT` (sval=op-text) | (none) | ⚠ | **An operator atom used as a quoted atom value.** `like(+, -)` in Prolog source — the bare `+` becomes a `TT_QLIT("+")`. Per corrected scope: value decoding at fresh leaf. ✅. (Borderline — the operator-atom-as-value distinction is part of Prolog's operator-quoting semantics, properly handled at the parse level.) |
| 709–724 | `TK_LBRACE` curly braces `{...}` | `TT_FNC` (sval=`"{}"`) | `[inner]` (or 0 children for empty `{}`) | ⚠ | **The `{}` notation is encoded as a TT_FNC named `"{}"`.** This is the standard Prolog convention (DCG pushback). Source order: `{ inner }` → tree `TT_FNC("{}")[inner]`. The braces become a node kind (via the sval naming) — not lifted out. Per corrected scope: kind choice + value decoding. ✅. |

### 6.10 `pt_term` — operator-precedence loop

| Loc | Function | Parent kind | Children L→R | L→R OK? | Notes |
|-----|----------|-------------|--------------|---------|-------|
| 730–757 | `pt_term(p, ts, max_prec)` | varies (TT_FNC via pt_binop, or TT_IF via pt_maybe_ifthenelse) | `[lhs, rhs]` per binary; TT_IF replaces semi-and-arrow chain | ❌ | The loop is a **Pratt-style operator-precedence parser**: read `lhs`, then iteratively consume operators and `rhs` operands while operator precedence is in range. The action **always wraps lhs+rhs via `pt_binop`** — fresh wrap, L→R ✅. **But** lines 752–753 then **call `pt_maybe_ifthenelse(node)` on `;`-shaped nodes** — which performs the structure-detecting collapse documented in 6.7. **The `pt_maybe_ifthenelse` call is the violation site**, not `pt_term` itself. The `pt_term` loop itself is clean. **Owned: PST-PL-6h** (move pt_maybe_ifthenelse to lower). |

### 6.11 Prolog — re-scoped to ONLY the goal §⛔ rules

**Withdrawn (not violations under your rules):**
- `ts_get` returning fresh TT_VAR per call with shared interned name pointer (value sharing, not tree sharing).
- `pt_args` populating a parent that was created in the immediate caller (build-time population is not post-construction mutation).
- Numeric folding `-NUM` / `+NUM` → single TT_ILIT/FLIT leaf (value decoding at fresh leaf).
- Bare operator atom → `TT_QLIT(opname)` (value decoding).
- `{...}` → `TT_FNC("{}")[...]` (kind choice + value decoding).
- Empty list `[]` → `TT_MAKELIST` (kind choice).
- Directive atoms (`dynamic`, `multifile`, etc.) without `(` taking a single arg as a TT_FNC (parser-side semantic dispatch — explicitly permitted per scope correction).
- TT_NUL filler for missing head in directive clause (permitted).
- TT_FNC(",") / TT_FNC(";") as binary-op nodes via `pt_binop` (the canonical clean shape).

**Retained under your rules:**

| # | Where | Violation | Owning rung |
|---|---|---|---|
| Pl1 | `pt_flatten_conj` (line 508–516): walks a TT_FNC(",") node and steals its children to populate a sibling TT_PROGRAM | rule 2 (in spirit): child stealing from a previously-built comma-FNC chain | **PST-PL-6h** (already named) |
| Pl2 | `pt_maybe_ifthenelse` (line 521–538): inspects `semi_node->t==TT_FNC && v.sval==";"`, then `left->t==TT_FNC && left->v.sval=="->"`; on match, builds TT_IF from `left->c[0]`, `left->c[1]`, `right`; abandons the `;`-FNC and `->`-FNC nodes | rule 2: inspect-kind-and-rearrange; rule 3: `;` and `->` source tokens replaced by TT_IF kind | **PST-PL-6h** |
| Pl3 | `pt_maybe_ifthenelse` lines 535–536: `then_prog->n == 1 ? then_prog->c[0] : then_prog` — conditional unwrap of a just-built TT_PROGRAM based on its child count | rule 2 in spirit: inspect-and-rearrange (even though it's the new node's own child) | **PST-PL-6h** |
| Pl4 | `pt_make_clause` (line 540–552): always wraps body in TT_PROGRAM and calls `pt_flatten_conj` to populate it with comma-chain children — transitive child-stealing | rule 2 (transitive via Pl1) | **PST-PL-6h** (covers both 6.6 and 6.8) |
| Pl5 | `parse_clause` DCG path (lines 1069–1101): re-parses head and body as `Term*` via `parse_term` + `dcg_expand_clause`; `cl->tr = NULL` | non-`tree_t` output — out of §⛔ scope, but the larger Phase-1 cleanup goal requires DCG to also produce `tree_t` | **PST-PL-6f** (in-progress) covers this |

**Net Prolog status: 4 retained §⛔ violations**, all clustered in
`pt_flatten_conj` + `pt_maybe_ifthenelse` + `pt_make_clause` (the
n-ary flattening pipeline). **PST-PL-6h already names this exact
work** — move all three helpers to `prolog_lower.c` and let the parser
emit the raw `;`/`->`/`,` `TT_FNC` chains. Lower flattens and recognizes
if-then-else at consumption time.

Additionally, **PST-PL-6f** continues to own the DCG → tree_t conversion
(Pl5), which is non-§⛔ scope but blocks Phase 1 completion for Prolog.

---

## Rollup — scans 1–6 (all six C parsers) — final corrected counts

(Re-graded 2026-05-19 after three scope corrections: TT_* kind reuse is
permitted, value decoding at fresh leaves is permitted, and a parser
node built from N source positions is permitted as long as it is fresh-
wrap and L→R — consumer-side splits are not parser-rule violations.)

| Frontend  | Violations | Owned by named rungs | Unowned (need new rungs) |
|-----------|-----------:|---------------------:|-------------------------:|
| Snocone   | 11         | 1 (PST-SC-4k → V11)  | 10                       |
| Icon      | 1          | 0                    | 1 (PST-ICN-LR-1)         |
| SNOBOL4   | 2          | 0                    | 2 (PST-SN4-W2, W3)       |
| Raku      | 27         | 5 (PRF-12 family: program, sub, class, for-range, gather) | 22 (new PRF-12 sub-rungs listed in §4.10) |
| Rebus     | 6          | 6 ✅ ALL CLOSED 2026-05-19 (Sonnet 4.6) | 0 — Phase 1 C COMPLETE |
| Prolog    | 4          | 4 (PST-PL-6h → Pl1, Pl2, Pl3, Pl4) | 0 — DCG conversion (Pl5) is non-§⛔ scope, owned by PST-PL-6f |
| **Total** | **51**     | **12**               | **39**                   |

### Proposed new rungs (Phase 1 only — no SCRIP mirror work)

**Snocone:**
- **PST-SC-FLATTEN** — eliminate `sc_flatten_arith` (snocone_parse.y:976) and `exprlist_ne` in-place append (line 533). 7 sites: TT_ALT/TT_SEQ/TT_ADD/TT_SUB/TT_MUL/TT_DIV plus exprlist_ne. Replace with fresh-wrap (right-leaning chain is correct).
- **PST-SC-4k** *(already named)* — `goto LABEL` → tree node.
- **PST-SC-LABELS** — `while_head`/`do_head`/`for_head`/`switch_head` mint label strings via `sc_label_new`. Move label allocation to `lower.c`.
- **PST-SC-RET-IN-FN** — return-inside-func emits two synthetic statements; should be one tree node.
- **PST-SC-FOR-INIT** — `for_head` lifts `init` as a sibling statement; move to `c[0]` of TT_FOR.

**Icon:**
**Icon** (in `GOAL-PST-ICON.md`):
- **PST-ICN-LR-1** — `parse_proc` uses `_id=nparams` to separate params from body. Rebuild via `TT_PROC_DECL[name, TT_VLIST(params), TT_PROGRAM(body)]` so structure is in the tree alone. Blocks PST-FIELD-2.

**SNOBOL4** (in `GOAL-PST-SNOBOL4.md`):
- **PST-SN4-W2** — `goto_expr T_CONCAT goto_atom` mutates $1.
- **PST-SN4-W3** — `expr15`/`expr17` g_cur mid-rule pattern mutates the prior-built TT_IDX/TT_VLIST/TT_FNC across reductions.

**Raku** (extending `PRF-12` in `GOAL-PST-RAKU.md`):

Already-named sub-rungs (PRF-12-gather, sub, class, program, for-range) cover R1, R12, R13, R15, R16, R17, R18, R19, R27. New sub-rungs needed for the remaining 18 violations:

- **PRF-12-my-type** — drop the type-annotation token of `my Type $var = expr;` (R2): either preserve as a child or move to a side-table; do not `free()` it silently.
- **PRF-12-say** — `say` keyword should produce `TT_SAY(expr)` or `TT_SAY_FH(fh, expr)`, lower to runtime call (R3, R4).
- **PRF-12-print** — same for `print`/`print(fh, expr)` (R5, R6).
- **PRF-12-arr-hash-ops** — index/element ops (`@a[i]`, `@a[i]=v`, `%h<k>`, `%h{k}=v`, `delete %h<k>`, `exists %h<k>`) should produce explicit `TT_IDX_GET`/`TT_IDX_SET`/`TT_HASH_GET`/`TT_HASH_SET`/`TT_HASH_DELETE`/`TT_HASH_EXISTS` kinds, lower to runtime calls (R7, R8, R9 + R24-set, R25, R26, R27, R28). [R7–R9 in statement section; R29-related atoms in §4.8.]
- **PRF-12-try** — `try`/`catch` should produce `TT_TRY(body, opt_catch_body)`, lower to runtime call (R10).
- **PRF-12-unless** — explicit decision: keep `unless` → `TT_IF(TT_NOT(...))` or introduce `TT_UNLESS` (R11). Goal sub-rung opens the discussion.
- **PRF-12-given** — `given_stmt` should build TT_CASE children directly from `when_list`, never wrapping pairs in TT_SEQ_EXPR for the parser's own use, never freeing tree nodes during the parse (R14).
- **PRF-12-smatch** — `~~ /regex/` should produce `TT_SMATCH(subj, regex_qlit, flavor)` kind, lower to runtime call (R20).
- **PRF-12-new** — `Foo.new(...)` should produce `TT_NEW(TT_QLIT("Foo"), args)`, lower to runtime call (R21).
- **PRF-12-mcall** — `obj.method(args)` should produce `TT_METHCALL(obj, TT_QLIT("method"), args)`, lower to runtime call (R22).
- **PRF-12-die** — `die expr` should produce `TT_DIE(expr)`, lower to runtime call (R23).
- **PRF-12-hof** — `map`/`grep`/`sort` should produce `TT_MAP/GREP/SORT` kinds with closure as first child, lower to runtime call (R24).
- **PRF-12-capture** — `$N` and `$<name>` should produce `TT_CAPTURE(TT_ILIT(N))` and `TT_NAMED_CAPTURE(TT_QLIT(name))` kinds (R25).
- **PRF-12-twigil** — `$.foo`/`$!foo` should produce `TT_TWIGIL_FIELD(sval=name)` kind with no synthesized `self` child; lower attaches the `self` reference (R26).

**Rebus** (in `GOAL-PST-REBUS.md`):

- **RB-C-1** (already named) — `stmt_list_ne` always-wrap. Fix both `stmt_list_ne stmt ';'` (Rb1) and `stmt_list_ne compound_stmt` (Rb2) to build fresh TT_PROGRAM each reduce instead of mutating `$1`. (Right-leaning TT_PROGRAM chain is correct.)
- **RB-C-2** (new) — `unless_stmt` should produce its own `TT_UNLESS` kind, not desugar to `TT_IF(TT_NOT(...))`. Lower can pick the runtime shape.
- **RB-C-3** (new) — `case_stmt` should build TT_CASE with flat n-ary alternating `[expr, guard0, body0, guard1, body1, ...]` (Raku/Snocone convention), not wrap each clause in synthesized TT_IF. Convert off-tree `RCase` list to TT_CASE child sequence directly. (Eventual removal of `RCase` is owned by separate PST-RB rung.)
- **RB-C-4** (new) — `+:=`/`-:=`/`||:=` should produce `TT_AUGOP(lhs, rhs)` carrying operator in `v.ival` (Snocone TK_AUG* convention), not synthesize a duplicated `TT_VAR(lhs-name)` and a desugared `TT_ASSIGN(TT_VAR, TT_OP(...))`. Lower handles the augmented expansion.
- **RB-C-5** (new) — `postfix_expr '(' arglist ')'` should always produce `TT_FNC[callee, args...]` with `$1` as `c[0]` regardless of `$1->t`. Stop inspecting `$1->t == TT_VAR`; stop mutating `$1->v.sval = NULL`. Lower.c reads `c[0]` to dispatch built-in (when `c[0]->t == TT_VAR`) vs indirect (otherwise).

**Prolog** (in `GOAL-PST-PROLOG.md`):

- **PST-PL-6h** (already named) — covers all four §⛔ violations (Pl1–Pl4): move `pt_flatten_conj`, `pt_maybe_ifthenelse`, and the TT_PROGRAM body-wrap from `pt_make_clause` to `prolog_lower.c`. Parser emits raw `;`/`->`/`,` TT_FNC chains; lower flattens and recognizes if-then-else at consumption time. Net effect: `pt_make_clause` becomes `TT_CLAUSE[head_or_TT_NUL, raw_body_tree]` with no flattening or wrap.
- **PST-PL-6f** (in-progress, non-§⛔ scope) — convert the DCG (`-->`) path from `Term*` to `tree_t`. Blocks Phase 1 completion for Prolog. Out of §⛔-rule scope but blocks downstream.

### Goal-file updates landed this session (2026-05-19)

- **`GOAL-PARSER-PURE-SYNTAX-TREE.md`** — Phase 1 status table updated; Icon and SNOBOL4 moved from ✅ to ⏳; **PST-LR-AUDIT-1 added as active HQ rung** covering scans 4–6 + second-pass verification of 1–3 + promotion of unowned violations into per-language goal files.
- **`GOAL-PST-SNOBOL4.md`** — PST-SN4-W1 ✅; W2 and W3 added.
- **`PLAN.md`** — Active Goals table updated.

---

## How to use this file

1. **Sanity check this Snocone scan against the actual `snocone_parse.y`.**
   Every "Loc" column is a line number; open each one and verify the
   children-L→R claim. If any row is wrong, mark it and re-do.
2. After Snocone is signed off, do SCAN 2 (Icon).
3. After all six are done, the table becomes the prerequisite manifest for
   any further C-side PST work, and for Phase 2 SCRIP mirror.
4. Each violation row above is a candidate rung. Some are already named
   (PST-SC-4k → V11); the rest need new rungs in the goal file before
   any session attempts them.

