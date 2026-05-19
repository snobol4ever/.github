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

## SCAN 4 — Raku — pending

## SCAN 5 — Rebus — pending

## SCAN 6 — Prolog — pending

---

## Rollup — scans 1–3 (Snocone, Icon, SNOBOL4) — final corrected counts

(Re-graded 2026-05-19 after three scope corrections: TT_* kind reuse is
permitted, value decoding at fresh leaves is permitted, and a parser
node built from N source positions is permitted as long as it is fresh-
wrap and L→R — consumer-side splits are not parser-rule violations.)

| Frontend  | Violations | Owned by named rungs | Unowned (need new rungs) |
|-----------|-----------:|---------------------:|-------------------------:|
| Snocone   | 11         | 1 (PST-SC-4k → V11)  | 10                       |
| Icon      | 1          | 0                    | 1 (PST-ICN-LR-1)         |
| SNOBOL4   | 2          | 0                    | 2 (PST-SN4-W2, W3)       |

### Proposed new rungs (Phase 1 only — no SCRIP mirror work)

**Snocone:**
- **PST-SC-FLATTEN** — eliminate `sc_flatten_arith` (snocone_parse.y:976) and `exprlist_ne` in-place append (line 533). 7 sites: TT_ALT/TT_SEQ/TT_ADD/TT_SUB/TT_MUL/TT_DIV plus exprlist_ne. Replace with fresh-wrap (right-leaning chain is correct).
- **PST-SC-4k** *(already named)* — `goto LABEL` → tree node.
- **PST-SC-LABELS** — `while_head`/`do_head`/`for_head`/`switch_head` mint label strings via `sc_label_new`. Move label allocation to `lower.c`.
- **PST-SC-RET-IN-FN** — return-inside-func emits two synthetic statements; should be one tree node.
- **PST-SC-FOR-INIT** — `for_head` lifts `init` as a sibling statement; move to `c[0]` of TT_FOR.

**Icon:**
- **PST-ICN-LR-1** — `parse_proc` uses `_id=nparams` to separate params from body. Rebuild so structure is in the tree alone. Blocks PST-FIELD-2.

**SNOBOL4** (in `GOAL-PST-SNOBOL4.md`):
- **PST-SN4-W2** — `goto_expr T_CONCAT goto_atom` mutates $1.
- **PST-SN4-W3** — `expr15`/`expr17` g_cur mid-rule pattern mutates the prior-built TT_IDX/TT_VLIST/TT_FNC across reductions.

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

