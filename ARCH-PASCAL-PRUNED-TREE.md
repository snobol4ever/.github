# ARCH-PASCAL-PRUNED-TREE.md — the tree the C Pascal parser hands to lower

hq_pascal, 2026-10-09. Authority: RULES.md FACT RULE — THE TREE IS THE PRUNED PARSE TREE (Lon 2026-10-03). Row:
`pascal-the-c-pascal-parser-builds-the-pruned-parse-tree-declared-types-kept-and-every-desugar-moves-to-lower-pascal-c-cto-2026-10-09`.
Witness: `SCRIP/scripts/test_gate_pas_the_c_parser_builds_the_pruned_parse_tree.sh`. Instrument: `scrip --dump-ast prog.pas` and `out/parser_pascal` print this tree.

## What changed

`src/parsers/pascal/pascal.y` keeps every production and every empty marker of the old grammar (the LALR automaton is state for state the old one: 380 states, the same
eight shift/reduce conflicts), and its actions only build nodes: one node per rule that fires, children in source order, a unit rule and a list-accumulating rule pruned,
a punctuation or keyword token with no meaning dropped. The tree is the old semantic front end's INPUT now: `src/lower/lower_pascal_tree.c` (`lower_pascal_tree`, called by
`scrip.c` and `polyglot.c` right after `pascal_compile`) walks it in source order and runs the old actions post-order, the old mid-rule actions at their positions, and returns
the tree `lower_pascal.c` has always consumed (a TT_PROGRAM of TT_PROC_DECL). The old type checker, scope tables, ISO 7185 refusals and desugars live there; the parser has
none. `pascal_sem_check` moved there too. A NULL return is the old "N ISO 7185 violation(s) in F -- no code generated" refusal.

## Node vocabulary (source order; `kids` are the children)

| construct (grammar) | node | kids |
|---|---|---|
| program | `TT_PROGRAM` | `TT_VAR name`, `TT_VLIST` of the program-parameter names (absent when none), `TT_BLOCK`, trailing `TT_ATTR :pragma` leftovers |
| block | `TT_BLOCK` | the declaration parts in source order, then the body (a `TT_SEQ_EXPR`) |
| label / const / type / var part | `TT_PART` sval `label` `const` `type` `var` | `TT_ILIT`s, or `TT_DECL`s |
| const definition | `TT_DECL` sval `const` | `TT_VAR name`, the constant: `TT_ILIT` `TT_FLIT` `TT_QLIT` `TT_CHRLIT` `TT_VAR`, or `TT_PLS`/`TT_MNS` of one |
| type definition | `TT_DECL` sval `type` | `TT_VAR name`, the type |
| variable declaration | `TT_DECL` sval `var` | `TT_VLIST` of `TT_VAR`, the type |
| named type | `TT_VAR` | — |
| `^T` | `TT_PTR_TYPE` | `TT_VAR T` |
| `[packed] array [i] of t` / `array [i, j] of t` | `TT_ARRAY_TYPE` | `TT_KEYWORD packed` when packed, the index type(s), the element type |
| `[packed] record ... end` | `TT_RECORD` | `TT_KEYWORD packed` when packed, a `TT_FIELDS` |
| record body | `TT_FIELDS` | `TT_DECL` sval `field` (`TT_VLIST` of names, the type) …, then the variant part (a `TT_CASE`) when present |
| variant part | `TT_CASE` | `TT_VAR tag` when named, `TT_VAR tag-type`, then `TT_ARM`s |
| variant arm / case-statement arm | `TT_ARM` | `TT_VLIST` of the constants, the record body (`TT_FIELDS`) or the statement |
| `[packed] set of t` | `TT_SET_TYPE` | `TT_KEYWORD packed` when packed, the base type |
| `[packed] file [of t]` | `TT_FILE_TYPE` | `TT_KEYWORD packed` when packed, the component type when present |
| `(a, b, c)` | `TT_ENUM_TYPE` | `TT_VAR`s |
| `lo .. hi` (type, and set-constructor range) | `TT_SUBRANGE` | the two bounds |
| procedure / function | `TT_PROCEDURE` / `TT_FUNCTION` | `TT_VAR name`, `TT_PARAMS` when present, `TT_VAR result-type` (functions that name one), then the `TT_BLOCK` or `TT_KEYWORD forward` |
| formal parameters | `TT_PARAMS` | `TT_DECL` sval `value` `var` (`TT_VLIST`, `TT_VAR type`), or `procedure` `function` (`TT_VAR name`, `TT_PARAMS` when present, `TT_VAR result` for a function) |
| `begin ... end` | `TT_SEQ_EXPR` | the statements; an empty statement is a `TT_SUCCEED` |
| `l: s` | `TT_LABEL_DEF` | `TT_ILIT l`, the statement |
| `v := e` | `TT_ASSIGN` | selector, expression |
| call | `TT_FNC` | `TT_VAR name`, then the arguments; an argument `e:w` or `e:w:f` is a `TT_FMT` (e, w[, f]) |
| `goto l` | `TT_GOTO_U` | `TT_ILIT l` |
| `if c then a [else b]` | `TT_IF` | c, a[, b] |
| `case e of ... end` | `TT_CASE` | e, `TT_ARM`s |
| `while c do s` | `TT_WHILE` | c, s |
| `repeat ss until c` | `TT_REPEAT` | `TT_SEQ_EXPR` of the statements, c |
| `for v := a to|downto b do s` | `TT_FOR` sval `to` or `downto` | `TT_VAR v`, a, b, s |
| `with r1, r2 do s` | `TT_WITH` | the selectors, s |
| `a[i, j]` `r.f` `p^` | `TT_IDX` `TT_FIELD` `TT_DEREF` | selector and indices; `TT_FIELD` takes `TT_VAR f` |
| `@x` | `TT_ADDR` | x |
| `[ ]`, `[a, b..c]` | `TT_SET` | the members (an expression or a `TT_SUBRANGE`) |
| `+ - * / div mod and or not in` | `TT_ADD` `TT_SUB` `TT_MUL` `TT_DIV` `TT_IDIV` `TT_MOD` `TT_CONJ` `TT_ALT` `TT_NOT` `TT_IN`; unary `TT_PLS` `TT_MNS` | operands in source order |
| `= <> < <= > >=` | `TT_EQ` `TT_NE` `TT_LT` `TT_LE` `TT_GT` `TT_GE` | the two operands |
| literals | `TT_ILIT` `TT_FLIT` `TT_QLIT` (a string) `TT_CHRLIT` (`#65`) | — |
| identifier in an expression | `TT_VAR` | — |

`/` is `TT_DIV` and `div` is `TT_IDIV`; no coercion node, no `MUL` by 1.0. A parenthesised expression is its inner node (precedence is the nesting).

New kinds, additive at the end of `tree_e` in `src/ir/ast.h`: `TT_BLOCK TT_PART TT_IDIV TT_IN TT_ADDR TT_SET TT_CHRLIT TT_SUBRANGE TT_FMT TT_WITH TT_ARRAY_TYPE TT_SET_TYPE
TT_FILE_TYPE TT_PTR_TYPE TT_ENUM_TYPE TT_ARM TT_PROCEDURE`.

## Source directives ride on the next leaf

The lexer does the conditional compilation (`{$ifdef}`, `{$if}`) and turns every directive an action reads into an EVENT text, `iso_error`, `mode_iso`, `seen_mode`,
`minenum N`, `packset N`, `packrec N`, `range 0|1`, `zerobased 0|1`, `overflow 0|1`, `align 0|1`, `codepage N`, `push`, `pop`, carried by the next leaf as
`(TT_ATTR :pragma (TT_QLIT "event"))`; events left at the end of the file ride on the `TT_PROGRAM`. The elaborator applies a leaf's events when it reads the leaf, so a
directive takes effect at its source position (`push`/`pop` keep the old stacks). `{$if}` reads the constants the parser has seen (a small environment in `pascal.y`).

## Proof

`scrip` with `SCRIP_PAS_DUMP_ELAB=1` (temporary) printed the elaborated tree of every program of the population before and after: master 252, benchmarks 11, FPC 181, PAT 427
and its P5 copies, P4, P5: identical trees, `--dump-ir` hashes and exit codes for all 1320; stderr identical as a sorted set for all but the programs that carry a syntax
error (the old parser printed the semantic diagnostic found before the syntax error; the new one stops at the syntax error).

## 1. AN ENUMERATION MEMBER'S SOURCE SPELLING IS AN ATTRIBUTE CHILD OF THE MEMBER LEAF; THE FOLDED TEXT STAYS THE NAME (the cto, 2026-10-29 14:3x CDT; hq_pascal's telegram of 14:2x on step 18, pf18_enum_write and symmetric-difference-1)

**MEASURED.** `pascal.l` folds every identifier to lower case at one site (line 138) and the lowerer compares the folded text at about 700 `strcmp` sites (lower_pascal_tree.c 582, lower_pascal.c 57, lower_pascal_types.c 56; no `strcasecmp`): the folded text IS the name of a Pascal identifier, because the language is case-insensitive, and that is the language's identity rule, not a desugar the tree law forbids. fpc writes an enumerated value by the member's DECLARED spelling (`Bob`, `Monday`), the one place Pascal's output surface shows an identifier's spelling; SCRIP prints `bob`. **RULED: hq_pascal's cure as proposed.** The enumeration MEMBER leaf alone carries an attribute child `(TT_ATTR :spelling <text>)` when the source spelling differs from the folded text, set by the enum-specific member rule in `pascal.y` from the lexer's last-identifier text (the context keywords' facility); the folded text stays the leaf's name, every lookup unchanged. It is an attribute IN the tree (no side table, no permission of CEO-1715 to ask), present on few leaves by construction. The tree moves for every program whose enumeration declares a member with an upper-case letter: hq_pascal counts them in the landing, and hq_snocone follows in `parser_pascal.sc` (the member rule keeps `tx` beside `lwr(tx)`: one conditional assignment). Carrying the source spelling on EVERY identifier leaf is refused for now: it would fold the 700 sites or shadow every name, for one output form. A second output form that shows a spelling (RTTI names, `GetEnumName`, an exception class in a message) is a new attribute site of the same shape, measured first. NOTED FOR THE ceo, a runtime row to mint for hq_pascal, not a design: a SCRIP Pascal string cannot hold a NUL (fillchar of a string with #0 empties it, find-the-missing-permutation needs it) -- the DESCR carries its length, so the defect is a Pascal string leaf that goes through a C string.
