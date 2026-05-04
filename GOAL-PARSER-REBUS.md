# GOAL-PARSER-REBUS.md — PARSER-REBUS pattern frontend in Snocone

**Repo:** corpus+one4all
**Branch:** `parser` (one4all only — `corpus` and `.github` stay on `main`)
**Sibling ladder:** `GOAL-LANG-REBUS.md`. The existing Rebus frontend
(`src/frontend/rebus/`) is the in-process oracle.

**Done when:** A Snocone program `parser_rebus.sc` reads Rebus source,
runs **one** `Compiland` PATTERN that builds the canonical IR tree on
the shared shift-reduce stack, and for every test program in the rung
corpus `tree_equal(existing_frontend_tree, parser_rebus_tree)` returns
true. Where a `.ref` file exists, executing both trees through the IR
interpreter produces byte-identical output.

⛔ **The deliverable is a PATTERN, not a procedure.** See `## Rubric`
below before writing any code. A line-at-a-time goto-driven state
machine — even one that emits the right tree shapes — is the wrong
deliverable and does not advance any rung.

---

## Status — session #62 attempt was REWORK, not landed

Sessions #62 (Claude Sonnet 4.7, 2026-05-03) wrote `parser_rebus.sc`
as a goto-driven line-at-a-time state machine that achieved tree
equivalence with the existing Rebus frontend on PASS=38 fixtures.

That code is the **wrong shape**. It does not use `Compiland`/`Command`/
`shift`/`reduce`/`nPush`/`nInc`/`nTop`/`nPop` — the canonical SNOBOL4-
family pattern spine the rest of this goal file specifies. The PASS=38
gate flagged tree equivalence but did not flag architectural shape;
that is a hole in the gate, not a clearance.

All seven rungs (RB-0..RB-6) are **REOPENED for rewrite as patterns**.
The 38 fixtures in `corpus/programs/rebus/parser/` are kept verbatim —
they are correct as gate input — but `parser_rebus.sc` itself is to be
rewritten from scratch following the model of `parser_snocone.sc`.

The rewrite does NOT have to be done all at once. The rung structure
below stages it: each rewritten rung lands when its pattern subtree
clears its fixture subset using the shift-reduce idiom.

---

## Rubric — what makes this a pattern parser

Before writing any `.sc` code, confirm every item below. If any
answer is "no", stop and rework.

1. **One root pattern, matched once against the entire source.** The
   driver reads stdin into a single string `Src` (concatenating all
   lines with newlines), then runs `Src ? Compiland`. **Exactly one
   `?` operator appears in the driver, ever.** Sub-patterns
   (`Command`, `expr`, `atom`, etc.) are referenced from inside
   `Compiland` via `*Sub`; they are never matched separately by the
   driver. There is no per-line slurp loop matching individual lines
   against patterns. After the single match, the driver walks the
   tree on the stack to call `TDump` per top-level child — that is
   emission, not parsing, and is allowed.

2. **`Compiland` has the canonical beauty.sc spine.** Literally:
   ```
   Compiland = nPush() ARBNO(*Command) reduce("'Parse'", 'nTop()') nPop();
   ```
   `Command` is one big alternation of sub-patterns, one per
   recognized construct. **One `Compiland`, period.** No
   `Compiland_v1` / `Compiland_v2`. No alternative spines. No
   per-rung Compilands.

3. **No goto, no labels — Snocone control flow only.** Snocone has
   `if`/`else`, `while`, structured patterns, and pattern alternation.
   That is enough for everything in this parser. **Zero goto. Zero
   labels.** This applies to the driver's stdin slurp too: write it
   as a `while ((Line = INPUT)) { Src = Src Line nl; }`, not as
   `read_loop:` / `goto read_loop`. The only legacy goto-style code
   in any current `parser_*.sc` is grandfathered for unrelated reasons
   (FW-3 deferred-call workaround); new code does not copy it.

4. **Tree construction uses the OPSYN binary operators `~` and `&`.**
   `semantic.sc` defines:
   ```
   OPSYN('~', 'shift', 2);
   OPSYN('&', 'reduce', 2);
   ```
   Write `*Integer ~ "'E_ILIT'"` not `shift(*Integer, "'E_ILIT'")`.
   Write `"'E_ALT'" & 'nTop()'` not `reduce("'E_ALT'", 'nTop()')`.
   The infix forms are the canonical surface; the function-call forms
   are the implementation. **Use the operators.** Never call
   `Push(Tree(...))` from a pattern escape — that is the procedural
   shortcut the OPSYN forms exist to replace.

5. **No user-defined functions called from inside parsing patterns.**
   A pattern match is pure pattern composition. The only functions
   that may be invoked from inside `Compiland` or any of its
   sub-patterns are the OPSYN-bound parsing operators and their
   counter companions:
   - `Shift` / `Reduce` (called by the `~` and `&` operators)
   - `PushCounter` / `IncCounter` / `DecCounter` / `PopCounter`
     (called by `nPush()` / `nInc()` / `nDec()` / `nPop()`)
   - `TopCounter` (read inside reduce-target expressions)

   That is the entire allowed surface for *user code* called from
   inside patterns. **No** `*assign('_x', ...)`, **no**
   `*push_qlit_from_strbody()`, **no** `*next_label()`, **no**
   `*format_arglist()` — none of those from inside a pattern.

   Snocone's built-in pattern primitives (LEN, SPAN, BREAK, ANY,
   NOTANY, FENCE, ARBNO, POS, RPOS, TAB, RTAB, REM, etc.) remain
   fully available — they are part of the pattern grammar, not
   user functions. So is the structural-test family (IDENT, DIFFER,
   GT, LT, etc.) when used inside patterns as `*IDENT(x, y)`
   guards. The line is: built-ins that ship with Snocone = OK;
   functions defined by the parser author = NOT OK from inside a
   pattern.

   If you need to transform a captured value before it lands on the
   stack, structure the grammar so that the pattern alone produces
   the desired match-span (see "String body capture idiom" below);
   if you need post-parse transformation, do it in a function that
   walks the tree AFTER `Src ? Compiland` returns.

   **String body capture idiom.** To shift `(E_QLIT "hi")` from
   source `"hi"`, the body must reach Shift without the surrounding
   quotes. Achieve this structurally — the opening and closing
   quotes are matched by sibling sub-patterns; only the body goes
   through `~`:
   ```snocone
   DQ_open = '"';   DQ_close = '"';   DQ_body = BREAK('"');
   SQ_open = "'";   SQ_close = "'";   SQ_body = BREAK("'");
   qlit_dq = DQ_open *DQ_body ~ "'E_QLIT'" DQ_close;
   qlit_sq = SQ_open *SQ_body ~ "'E_QLIT'" SQ_close;
   String  = (*qlit_dq | *qlit_sq);
   ```
   Match for `"hi"`: `DQ_open` consumes `"`; `*DQ_body` matches `hi`
   (BREAK stops at the closing quote); `~` shifts `tree('E_QLIT',
   'hi')`; `DQ_close` consumes the closing `"`. Pure pattern
   composition. Same idiom applies to any "matched span minus
   delimiters" capture. **No function calls.**

6. **No per-line state machine.** No `_rb_state = 0/1` toggle. No
   per-construct `_rb_*_kind` / `_rb_*_txt` global slots feeding hand-
   built `Tree(...)` calls in helper functions. Per-construct binding
   happens via the `~` operator's right operand (the tag) and the `&`
   operator's right operand (the child count, usually `nTop()`).

7. **All trees are n-ary. No left, no right.** Every fold of a
   variable-length list — alternation, concatenation, statement
   sequences, argument lists, parameter lists, body statements —
   uses the n-ary spine:
   ```
   X = nPush() *XList ("'X'" & 'nTop()') nPop();
   XList = nInc() *Item FENCE(<sep> *XList | epsilon);
   ```
   `a | b | c` becomes a flat `(E_ALT a b c)` with three children,
   NOT `(E_ALT (E_ALT a b) c)`. `f(a, b, c)` becomes a flat
   `(E_FNC f a b c)` with four children, NOT a nested chain.
   Hard-coded child counts in `&` (e.g. `"'E_ASSIGN'" & 2`) are
   reserved for genuinely fixed-arity productions like `lhs := rhs`
   — and even then, prefer the n-ary spine if the construction
   could plausibly grow. **The existing Rebus frontend produces
   binary E_ALT; that is a divergence to surface, not a constraint
   to conform to.** See `## Divergence-driven rungs` below.

8. **Counter helpers (`nPush`/`nInc`/`nTop`/`nPop`) appear at every
   n-ary fold site.** This is how the parser knows how many items
   to fold. The pair `nPush() ... reduce(t, 'nTop()') nPop()` opens
   a counter scope; `nInc()` inside the iteration body bumps it
   each pass.

9. **Sub-pattern names mirror `rebus.y`.** Use `function_decl`,
   `record_decl`, `pat_expr`, `expr`, `alt_expr`, etc. — the
   non-terminal names from `src/frontend/rebus/rebus.y`. Where a name
   conflicts with Snocone reserved syntax, suffix with `_pat`. Do not
   invent names like `MatchLine` / `BodyAltLine` / `IfLine` — those
   are line-fragments, not grammar non-terminals.

10. **One alternation in `Command` covers all top-level constructs.**
    In Rebus that is `function_decl | record_decl`. Statement-level
    forms (assign, match, alt, if, while, call, atom) live under a
    `stmt`-rooted sub-tree fired by `function_decl`'s body, not as
    peers of `function_decl`.

A grep that should produce zero hits in the rewritten parser:
```
grep -nE 'goto |^[a-z_]+:|_rb_state|_rb_atom_kind|emit_[a-z]|shift\(|reduce\(|Push\(Tree|\*[a-z_]+\(' parser_rebus.sc
```
The new `\*[a-z_]+\(` term catches function-call-from-pattern
escapes (`*assign(...)`, `*push_*()`, etc.). Pattern references
like `*Gray` or `*Compiland` use no parens and do not match.

A grep that should match exactly:
```
grep -c 'Src ? Compiland' parser_rebus.sc       # → 1
grep -c '?' parser_rebus.sc | <discounting ?'s in patterns>  # → 1 in driver
grep -c '^Compiland '   parser_rebus.sc         # → 1 (the definition)
grep -c '\*Compiland'   parser_rebus.sc         # → 0 (Compiland is the root, never referenced)
grep -c 'Compiland'     parser_rebus.sc         # → exactly 2 (def + driver use)
```

---

## Style Guidelines for parser_*.sc — canonical, derived from beauty.sno / beauty.sc

These guidelines are normative for every `parser_<lang>.sc` (PARSER-RB,
PARSER-SC, PARSER-SN, PARSER-IC, PARSER-PL, PARSER-RK).  They derive
directly from `corpus/programs/snobol4/demo/beauty/beauty.sno` and its
Snocone port `corpus/programs/snocone/demo/beauty/beauty.sc` — the
reference pattern parsers in the canon.  Read both end-to-end before
writing any parser.  Where this section and the per-language goal file
disagree, this section wins.

### 1. White / Gray attached at token definitions, not at use sites

`White` matches a contiguous run of horizontal whitespace (space, tab,
and per-language continuation conventions).  `Gray` is `*White |
epsilon` — optional whitespace.  Both are defined ONCE, near the top of
the parser file, beside the lex-token definitions:

```snocone
White = SPAN(' ' tab) FENCE(nl ('+' | '.') FENCE(SPAN(' ' tab) | epsilon) | epsilon)
      | nl ('+' | '.') FENCE(SPAN(' ' tab) | epsilon);
Gray  = *White | epsilon;
```

(Per-language continuation handling — beauty.sno's `+`/`.` glyphs in
column 1 — adapts per the host language; the Rebus continuation rule is
just `White = SPAN(' ' tab)` if the language has no continuation
syntax.)

**White / Gray are absorbed into the `$'kw'` and atomic-token
definitions, never written into grammar productions.**  Look at
`Expr0..Expr17` in beauty.sc lines 64-100: there is no `*Gray` or
`*White` in the operator-tier ladder.  All whitespace is already
inside the `$'op'` wrappers.

### 2. `$'kw'` for operator and keyword tokens; identifier names for word tokens

Operator and punctuation tokens get `$'op'` syntactic wrappers that
bake in the surrounding whitespace policy:

```snocone
// Binary operators — symmetric whitespace.
$'='  = *White '='  *White;   $'?'  = *White '?'  *White;
$'|'  = *White '|'  *White;   $'+'  = *White '+'  *White;
$'**' = *White '**' *White;   $'~'  = *White '~'  *White;
// Comma is gray-flanked (optional whitespace each side).
$','  = *Gray  ','  *Gray;
// Brackets are asymmetric: open paren absorbs trailing gray,
// close paren absorbs leading gray.
$'('  = '('  *Gray;   $')'  = *Gray ')';
$'['  = '['  *Gray;   $']'  = *Gray ']';
```

Snocone-reserved word tokens (`if`, `then`, `else`, `while`, `do`,
`function`, `record`, `end`) also get `$'kw'` wrappers — required
whitespace flanks where the language demands word boundaries:

```snocone
$'if'       = *Gray 'if'       *White;   // 'if' must be followed by whitespace
$'then'     = *White 'then'    *White;
$'function' = 'function' *White;          // at column-anchor positions
$'end'      = *White 'end'     *Gray;
```

Word tokens that are NOT Snocone-reserved get plain identifier names
with the optional-/required-space prefix folded in.  Beauty.sno's
`SGoto`/`FGoto` (lines 192-193) is the model:

```snocone
S = $' ' 'S';     // optional leading whitespace, literal 'S'
F = $' ' 'F';
SGoto = ('S' | 's') . *assign(.sf, *'S');   // case-tolerant variant
```

**Convention:** `$' '` (single space) is optional whitespace; `$'  '`
(two spaces) is required whitespace.  This carries directly from
beauty.sno.

**The grammar productions read clean.**  No `*White` / `*Gray` strewn
through `Expr0..Expr17` or `Stmt` or `Compiland`.  Whitespace lives in
the token wrappers, period.

### 3. AST decoration — beauty.sno's two equivalent forms

Beauty.sno presents two surface forms for stack-machine annotation,
related by OPSYN:

**Form A — explicit dot-conditional + function call:**
```
primitive . tx                                      // capture into global tx
epsilon . func(literal, tx)                         // perform action with tx
```

**Form B — function-call shorthand (after OPSYN):**
```
primitive . tx Func(literal, "tx")                  // single helper call
```

**Form C — infix operator shorthand (after OPSYN ~ / &):**
```
*primitive ~ 'TAG'                                  // shift  (= Shift(*primitive, 'TAG'))
("'TAG'" & 2)                                       // reduce 2 children into TAG
("'TAG'" & 'nTop()')                                // reduce nTop() children into TAG
("'TAG'" & '*(GT(nTop(), 1) nTop())')               // reduce only if >1 (else passthrough)
```

The OPSYN bindings live in `semantic.sc`:
```
OPSYN('~', 'shift',  2);     // *p ~ 'TAG'      ≡  shift(*p, 'TAG')
OPSYN('&', 'reduce', 2);     // ("'TAG'" & N)   ≡  reduce("'TAG'", N)
```

**Use the infix operators (Form C) wherever supported.**  beauty.sno
uses them throughout `Expr14..Expr17`, `Command`, `Goto`.  beauty.sc
also uses `~` and `&` inline (lines 80-100, 132).  When the host's
Snocone runtime does not yet parse infix `~`/`&`, fall back to the
function-call forms `shift(...)` / `reduce(...)` — both compile to the
same `Shift`/`Reduce` engine calls.

### 4. n-ary tree counters via `nPush()` / `nInc()` / `nTop()` / `nPop()`

For variable-length list folds (alternation, concatenation,
parameter/argument lists, statement sequences), use the n-ary spine.
beauty.sno line 119 / beauty.sc line 61:

```snocone
ExprList = nPush() *XList ("'ExprList'" & '*(GT(nTop(), 1) nTop())') nPop();
XList    = nInc()  (*Expr | epsilon ~ '') FENCE($',' *XList | epsilon);
```

`nPush()` opens a counter scope; `nInc()` bumps it for each list
element; `nTop()` reads the count at reduce time; `nPop()` closes the
scope.  These are pattern fragments returned by build-time helpers in
`semantic.sc`:

```
function nPush() { nPush = epsilon . *PushCounter(); return; }
function nInc()  { nInc  = epsilon . *IncCounter();  return; }
function nTop()  { nTop  = TopCounter();             return; }
function nPop()  { nPop  = epsilon . *PopCounter();  return; }
```

Decorate the AST construction with these counter operations; they are
the *only* match-time function-effects allowed inside a parsing
pattern besides Shift/Reduce.

### 5. AST tree-tag names — match the IR `EXPR_t` enum

Tree tags emitted by `~` and `&` MUST match the language's IR kind
names — the `E_*` strings from `src/ir/ir.h`'s `EXPR_t` /
`STMT_kind_t`.  Examples per language:

| Construct | Tag string |
|-----------|------------|
| Variable reference | `E_VAR` |
| Integer literal | `E_ILIT` |
| String literal | `E_QLIT` |
| Function call | `E_FNC` |
| Binary `+` | `E_ADD` |
| Binary `*` | `E_MUL` |
| Pattern alternation (n-ary) | `E_ALT` |
| Assignment | `E_ASSIGN` |
| Pattern match | `E_SCAN` |

For language-specific surface-syntax constructs that are lowered to
canonical IR by a post-parse pass (see Rubric item 5 above), use the
language-prefixed tag form: `RB_FUNC_DECL`, `RB_REC_DECL`, `IC_PROC`,
`PL_CLAUSE`, etc.  These tags live ONLY in the surface parse tree;
post-parse lowering rewrites them into the canonical `E_*` /
`STMT_*` shape that `tree_equal()` compares against.

### 6. Identifier naming — case discipline

| Kind | Convention | Examples |
|------|------------|----------|
| Pattern non-terminal (grammar production) | UpperCamelCase or matching BNF | `Expr`, `Stmt`, `Command`, `Compiland`, `function_decl`, `record_decl` |
| Token classifier | UpperCamelCase | `Id`, `Integer`, `Real`, `String`, `Function`, `BuiltinVar`, `ProtKwd` |
| Helper function (build-time, returns pattern fragment) | UpperCamelCase | `Shift`, `Reduce`, `RB_push_qlit` |
| Helper function (match-time effect) | snake_case or lowerCamel | `assign`, `match`, `rb_push_qlit`, `nInc` |
| Local pattern variable (intermediate) | lowerCamel or snake_case | `tx`, `sf`, `_kw_rest` (with caveat below) |
| Tag string constant | UpperCamelCase / `E_*` IR form | `E_VAR`, `RB_FUNC_DECL`, `Parse` |

**No symbols starting with underscore in source code.**  Underscore
prefixes are reserved for compiler-generated identifiers (the IR
lowering pipeline emits `_g42`, `_lbl_3`, etc.).  Existing
`parser_*.sc` files that use names like `_sc_lbl_n` or `_kw_rest` are
grandfathered but new code does not introduce them — replace with
`scLblN` or `kwRest`.

**Variables start with a lowercase letter, snake_case for compounds.**
Functions usually start with an uppercase letter, then snake_case
afterwards.  This matches beauty.sno conventions.

### 7. Names track the official language specification

Non-terminal pattern names MUST mirror the host language's official
BNF.  For Rebus that is `src/frontend/rebus/rebus.y` (Bison grammar
based on Griswold TR 84-9): `function_decl`, `record_decl`,
`expr_stmt`, `if_stmt`, `while_stmt`, `case_stmt`, `match_stmt`,
`primary`, `postfix_expr`, `expr`, `pat_expr`, `cat_expr`, `alt_expr`,
`assign_expr`.

For Icon: per `src/frontend/icon/icon.y` and the Icon Programming
Language reference.  For Prolog: per ISO/IEC 13211-1.  Etc.

**Sources of truth, in order:**
1. The frontend's `.l` / lex header (token enum) and `.y` / parse module.
2. The lowering module's IR-tag enum and dumper.
3. The official BNF / language specification — only as a tiebreaker
   when (1) and (2) leave a name unspecified.

Invented names are reserved for the cross-PARSER spine (`Compiland`,
`Command`, helpers like `Push`/`Pop`/`Top`, `tree`/`Tree`/`TDump`/`stack`).
Per-language non-terminals are not invented.

### 8. Code layout — horizontal-first, 120 columns, no blank lines

| Rule | Style |
|------|-------|
| Maximum line length | 120 characters |
| Single-statement bodies | inline with semicolon: `if (x) action;` not `if (x) { action; }` |
| Multi-statement bodies | brace block `{ ... }` |
| Block separation | `//===` 120-char major divider, `//---` 120-char minor divider — NEVER a blank line |
| Multi-line wrapping | constant 2-space nested indentation |
| Vertical alignment | balance parentheses and binary operators vertically |
| Use of horizontal space | maximize — pack tokens onto one line where readable |

Single-statement `if`/`while`/`for` bodies always use the inline
semicolon form:

```snocone
// Correct:
if (DIFFER(line)) line = line ' ';
while (i = LT(i, n) i + 1) sum = sum + a[i];

// Incorrect:
if (DIFFER(line)) {
    line = line ' ';
}
```

When a long pattern definition exceeds 120 columns, wrap with
balanced parentheses and 2-space nested indent, lining up alternation
bars with the opening paren:

```snocone
Expr14 = '@' *Expr14 ("'@'" & 1)
       | '~' *Expr14 ("'~'" & 1)
       | '?' *Expr14 ("'?'" & 1)
       | *ProtKwd ~ 'ProtKwd'
       | *UnprotKwd ~ 'UnprotKwd'
       | *Expr15;
```

Section dividers replace blank lines:

```snocone
//===================================================================================================================
//  Atomic tokens
//===================================================================================================================

Integer = SPAN(digits);
Id      = ANY(&UCASE &LCASE) FENCE(SPAN('.' digits &UCASE '_' &LCASE) | epsilon);

//-------------------------------------------------------------------------------------------------------------------
//  Operator wrappers
//-------------------------------------------------------------------------------------------------------------------

$'='  = *White '='  *White;
$'|'  = *White '|'  *White;
```

The exact divider widths are 120 characters of `=` (major) or `-`
(minor), terminated by a comment line with the section title.

### 9. No goto, no labels

Snocone has structured `if`/`else`, `while`, `for`, structured pattern
alternation, and pattern `FENCE`.  That is enough for any
`parser_*.sc`.  **Zero `goto`.  Zero labels.**

The driver reads stdin into a single `Src` string, runs ONE
`Src ? Compiland`, then walks the resulting tree.  No
`read_loop:`/`mainErr:`/`mainEnd:` labels.  beauty.sc has them only
because it is a *mechanical* port from beauty.sno's SNOBOL4 goto-flow
— that is grandfathered, not a model to copy.

### 10. Driver shape — stdin slurp, one match, walk

```snocone
&FULLSCAN  = 1;

InitCounter();
InitStack();

src = '';
while (line = INPUT) src = src line nl;

if (src ? Compiland) {
    parseRoot = Pop();
    if (DIFFER(parseRoot)) {
        i = 0;
        while (i = LT(i, n(parseRoot)) i + 1) lower(c(parseRoot)[i]);
    }
} else {
    OUTPUT = 'Parse Error';
}
```

`lower()` is the post-parse tree-walk that emits canonical STMT TDump
lines.  Match-time helpers it calls (`Tree`, `TDump`, etc.) live in
`tree.sc`/`tdump.sc` and are not parsing functions.

### 11. The `nl` token — used directly, not wrapped

Snocone exposes `nl` as a single-character pattern primitive.  Use it
directly in patterns; do NOT define `nl_one = ANY(nl)` — that wrapping
both costs a function-call indirection AND can introduce backtracking
hazards under `ARBNO`.

```snocone
// Correct (beauty.sc style):
Comment = '*' BREAK(nl);
Command = nInc() FENCE(*Stmt reduce('Stmt', 7) (nl | ';'));

// Incorrect:
nl_one = ANY(nl);
stmt_line = ... *nl_one;
```

### 12. Self-check greps

A grep that should produce zero hits in any compliant `parser_*.sc`:

```
grep -nE 'goto |^[a-z_]+:|^_[A-Za-z]'      parser_*.sc   # → 0 (no goto/label/leading-underscore source ids)
grep -cE 'shift\(|reduce\('                 parser_*.sc   # → 0 IF runtime supports infix ~/&; otherwise OK
grep -cE 'Push\(Tree'                       parser_*.sc   # → 0 (no escape-hatch tree pushes from patterns)
grep -nE '^[A-Za-z_]+ *= *.*\*White'        parser_*.sc   # → only $'op' / token defs / White itself
grep -c '^(if|while)[^(]' -r parser_*.sc   # → 0 (always Snocone keyword usage with parens)
```

A grep that should match exactly:

```
grep -c 'src ? Compiland'  parser_*.sc      # → 1 (the ONE pattern match in driver)
grep -c '^Compiland '      parser_*.sc      # → 1 (the definition)
grep -cE ' ~ | & '          parser_*.sc      # → many (per construct)
grep -cE 'nPush|nInc|nTop|nPop' parser_*.sc # → ≥ counter-helper hits / parser table above
```

---

## Divergence-driven rungs — n-ary vs the existing frontend's binary

PAT-RB produces n-ary trees. The existing Rebus frontend
(`src/frontend/rebus/rebus_lower.c`) uses `expr_binary(E_ALT, ...)`
for `RE_ALT` — that is, every `|` is a binary node. So `a | b | c`
in the existing frontend is `(E_ALT (E_ALT a b) c)`, while PAT-RB
will produce `(E_ALT a b c)`. Same for `f(a, b, c)` arglist (the
existing frontend may or may not be n-ary there — re-verify per
rung), statement sequences, parameter lists, etc.

**This is intentional divergence, not a bug in PAT-RB.** Per the
"Done when" criterion at the top of this file, `tree_equal(t1, t2)`
must hold; for any rung where the existing frontend's tree is
binary-folded but PAT-RB's is n-ary, that gate will fail. That
failure is the rung's *output*: PAT-RB has discovered that the
existing frontend should be flattened.

**Rung procedure when n-ary divergence is found:**

1. PAT-RB produces n-ary tree per the canonical spine. Don't fold
   to binary "to make the gate pass."
2. The rung's commit message names the divergence explicitly:
   "PAT-RB-5: existing frontend produces binary E_ALT; PAT-RB
   produces n-ary E_ALT. Divergence reported — track upstream fix
   in GOAL-LANG-REBUS RB-5."
3. Open / update the upstream LANG rung to flatten the existing
   frontend's lowering. Until that lands, `tree_equal` failure on
   alt-bearing fixtures is *expected*; mark those fixtures as
   "divergence-pending" in the rung's gate description rather than
   counting them as FAIL.
4. When upstream lands, the divergence-pending fixtures become
   gating PASS without any change to PAT-RB.

The 38 fixtures in `corpus/programs/rebus/parser/` will not all
clear with one push under this regime. That is correct. PAT-RB's
job is not to mirror the existing frontend's bugs.

---

## Reference — `parser_snocone.sc` as the model

Read `corpus/programs/scrip/parser_snocone.sc` end-to-end before
starting. It is the closest sibling: same shared SC blob, same
`Compiland`/`Command` spine, hand-rolled expression-precedence ladder
(`Expr17` atoms → `Expr9` mul/div → `Expr6` add/sub → `Expr4` concat
→ `Expr3` alt → ...), and same shift/reduce idiom. Rebus's ladder
is shorter (no concat operator at this stage; alternation is at
statement level, not expression level — see `rebus.y`) but the
overall shape is identical.

Counter-helper hits per parser, for orientation (Rebus is the outlier):

| Parser | nPush/nInc/nTop/nPop hits |
|---|---|
| parser_snocone.sc | 9 |
| parser_snobol4.sc | 8 |
| parser_icon.sc | 5 |
| parser_prolog.sc | 4 |
| parser_raku.sc | 4 |
| **parser_rebus.sc (current, wrong shape)** | **0** |
| **parser_rebus.sc (target)** | **8+** |

---

## Cross-pollination

All six PARSER-* parsers share `Compiland`/`Shift`/`Reduce`/`Push`/`Pop`/`Top`/
`tree`/`TDump`/`stack` from `corpus/programs/snocone/demo/beauty/`. Bug
fixes there benefit all six. Rebus shares lowering with SNOBOL4, so PAT-RB's
`expr ? pat` and `expr | expr` lift directly from PARSER-SN. The existing
Rebus frontend is younger than SNOBOL4's; PAT-RB does not silently match
divergences — report upstream.

Naming, layout, `White`/`Gray`, `$'name'` tokens, shift/reduce, n-ary
counters, identifier rules — canonical writeup in
`GOAL-PARSER-SNOBOL4.md ## Style Guidelines for parser_*.sc`.  Use BNF
names, `beauty.sc` names, `shift()`/`reduce()` over manual
`Push(Tree(...))`, no new labels/goto.

---

## Session Setup

```bash
( cd /home/claude/one4all && git fetch origin parser 2>/dev/null; \
  git checkout parser 2>/dev/null || git checkout -b parser origin/parser 2>/dev/null || git checkout -b parser )

bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
```

Gate after setup:
```bash
bash /home/claude/one4all/scripts/test_smoke_rebus.sh     # existing frontend baseline
bash /home/claude/one4all/scripts/test_parser_rebus.sh    # PAT-RB
```

---

## Architecture reminder

```
scrip --parser-crosscheck parser_rebus.sc tiny.reb
```

SCRIP runs `parser_rebus.sc` (which `-include`s the shared SC library from
`corpus/programs/scrip/`) against `tiny.reb`. PAT produces tree t2 via
`Compiland`; the existing frontend produces t1. Compared in memory
(`tree_equal`), executed in memory. No subprocesses, no temp files.

Shared SC library: `tree.sc  stack.sc  counter.sc  ShiftReduce.sc  semantic.sc`.

Compiland spine:
```
Compiland = nPush() ARBNO(*Command) reduce("'Parse'", 'nTop()') nPop();
```

---

## Rebus tree shapes (existing frontend, taken as oracle)

| Construct | Oracle `--dump-ir` (single-line form) |
|-----------|---------------------------------------|
| `function f() ... end` | `(STMT :subj (E_FNC DEFINE (E_QLIT "F()")))` then per-body STMTs, then `:go RETURN` `:lbl rb_N` |
| `record R(f1, f2)` | `(STMT :subj (E_FNC DATA (E_QLIT "R(F1,F2)")))` |
| `x` (bare atom) | `(STMT :subj (E_VAR X))` |
| `42` | `(STMT :subj (E_ILIT 42))` |
| `"hi"` | `(STMT :subj (E_QLIT "hi"))` |
| `x := y` | `(STMT :eq :subj (E_VAR X) :repl (E_VAR Y))` |
| `if c then s` | `(STMT :subj <c> :goS L_then :goF L_else)` then s, then merge label |
| `while c do s` | label, then `(STMT :subj <c> :goS body :goF after)` then s, loop back |
| `f()` | `(STMT :subj (E_FNC F))` |
| `x ? y` | `(STMT :subj (E_VAR X) :pat (E_VAR Y))` |
| `a \| b \| c` | left-assoc `(E_ALT (E_ALT a b) c)` per `rebus.y` `alt_expr` |

(The 38 fixtures in `corpus/programs/rebus/parser/` cover every shape
above; oracle outputs are stable.)

---

## Worked atom example — the smallest correct rung

This is the shape RB-0 must take in the rewrite. Read it, follow it.
**No functions are called from inside any pattern.** The grammar is
pure pattern composition.

```snocone
// Lex tokens — drop into the file once, used by every rung.
ws_run = SPAN(' ' tab);
ws_opt = (ws_run | epsilon);
nl_one = ANY(nl);   // matches exactly one newline char, pure primitive

Id      = (ANY(&UCASE &LCASE '_')
           (SPAN(&UCASE &LCASE digits '_') | epsilon));

Integer = SPAN(digits);

// String body capture idiom — quotes matched by sibling sub-patterns;
// only the body goes through `~`. No function calls. The match span
// of `*DQ_body` is the body text (BREAK stops at the closing quote);
// `~ "'E_QLIT'"` shifts tree('E_QLIT', body) onto the stack.
DQ_open  = '"';   DQ_close = '"';   DQ_body = BREAK('"');
SQ_open  = "'";   SQ_close = "'";   SQ_body = BREAK("'");
qlit_dq  = DQ_open *DQ_body ~ "'E_QLIT'" DQ_close;
qlit_sq  = SQ_open *SQ_body ~ "'E_QLIT'" SQ_close;
String   = (*qlit_dq | *qlit_sq);

// atom — Rebus's expr17 slice (id | integer | string).
// `~` is OPSYN'd to shift; rhs is the tree-tag string.
atom = FENCE(  *String
             | *Integer ~ "'E_ILIT'"
             | *Id      ~ "'E_VAR'"
            );

// stmt — for RB-0, a statement is just an atom in :subj position.
// Overall STMT shape: (STMT :subj <atom>).
// `&` is OPSYN'd to reduce; rhs is the child count (1 here, fixed-arity).
stmt = ws_opt *atom ws_opt nl_one ("'STMT_SUBJ'" & 1);

// Command — single top-level alternation. At RB-0, only `stmt`.
Command = nInc() *stmt;

// Compiland — the canonical beauty.sc spine. ONE root pattern.
// `'nTop()'` is the n-ary count: however many Commands matched,
// that many children fold into the Parse node.
Compiland = nPush() ARBNO(*Command) ("'Parse'" & 'nTop()') nPop();

// Driver — read whole stdin into Src, ONE pattern match, walk the result.
// No goto. No labels. No per-line matching.
InitCounter();
InitStack();

Src = '';
Line = INPUT;
while (DIFFER(Line)) {
    Src = Src Line nl;
    Line = INPUT;
}

if (Src ? Compiland) {
    parse_root = Top();
    i = 0;
    while (i = LT(i, n(parse_root)) i + 1)
        TDump(c(parse_root)[i]);
} else {
    OUTPUT = 'PARSER-RB: parse failed';
}
```

**Self-check before committing RB-0:**

```
grep -c 'goto '              parser_rebus.sc  # → 0
grep -cE '^[a-z_]+:'         parser_rebus.sc  # → 0
grep -c '_rb_state'          parser_rebus.sc  # → 0
grep -cE 'shift\(|reduce\('  parser_rebus.sc  # → 0
grep -cE 'Push\(Tree'        parser_rebus.sc  # → 0
grep -cE '\*[a-z_]+\('       parser_rebus.sc  # → 0  (no fn-call-from-pattern;
                                              #      *Sub references take no parens)
grep -cE 'nPush|nInc|nTop|nPop' parser_rebus.sc  # → ≥2  (1 nPush, 1 nPop in
                                                  #       Compiland; ≥1 nInc in
                                                  #       Command; ≥1 nTop in
                                                  #       Compiland's reduce)
grep -cE ' ~ | & '           parser_rebus.sc  # → ≥4  (3 ~ in atom; 1 & in stmt;
                                              #      1 & in Compiland)
grep -c 'Src ? Compiland'    parser_rebus.sc  # → 1  (the ONE pattern match)
grep -c 'Compiland'          parser_rebus.sc  # → exactly 2 (def + driver use)
grep -cE '^function '        parser_rebus.sc  # → 0  (no helper functions for
                                              #      RB-0; later rungs may add
                                              #      lowering passes that consume
                                              #      the parse tree, but never
                                              #      functions called from
                                              #      inside patterns)
```

The structural tests:
- "exactly 2 Compiland mentions" → one root pattern.
- "exactly 1 `Src ? Compiland`" → the entire source is matched once.
- "0 hits on `\*[a-z_]+\(`" → no function calls from patterns.
- "0 hits on `^function`" at RB-0 → grammar is patterns end-to-end.

---

## Rung ladder — REWRITES (all reopened)

The 38 fixtures in `corpus/programs/rebus/parser/` already exist and are
correct. Each rung's job is to bring `parser_rebus.sc`'s **shape** up to
spec for that fixture subset.

Every step below uses the OPSYN binary operators `~` (shift) and `&`
(reduce). Every list-fold uses the `nPush()`/`nInc()`/`nTop()`/`nPop()`
spine for n-ary trees. **No `goto`. No labels. No `Push(Tree(...))`
escapes from a pattern.** No left, no right.

### PARSER-RB-0a — Style Guidelines audit & cleanup — **next**

⚠ **These are guidelines, not laws.**  Each item below is a recommended
cleanup against the canonical style codified in
`## Style Guidelines for parser_*.sc`.  Strict conformance is the
default; deviate only with a brief inline `// note: ...` justifying why
the deviation is the better engineering choice in this spot.  The gate
is "every deviation is either fixed OR documented in a comment", not
"zero greps match".

Audit performed 2026-05-04 against
`corpus/programs/scrip/parser_rebus.sc` (current corpus HEAD `707bd5d`
plus two diagnostic patches from session #4 — A: flat mul/add tier
shape, B: `*stmt`→`*stmt_line`).  Violations enumerated below.

#### G1 — White / Gray strewn through grammar productions (HIGH)

19 hits on `*White`/`*Gray` in productions that are not `$'op'`/token
definitions.  Concentrated in: `if_stmt`, `while_stmt`, `stmt_line`,
`function_decl`, `record_decl`.

- [ ] Define `$'if'`, `$'then'`, `$'while'`, `$'do'`, `$'function'`,
      `$'end'`, `$'record'` keyword wrappers absorbing the surrounding
      whitespace.  Required-space-after pattern for keywords that must
      be followed by an identifier or another keyword (`'function' *White`
      becomes `$'function' = 'function' *White;`).
- [ ] Rewrite `if_stmt`, `while_stmt` to use the new `$'if'`/`$'then'`/
      `$'while'`/`$'do'` wrappers; remove all `*White` from their RHS.
- [ ] Rewrite `function_decl`, `record_decl` to use `$'function'`,
      `$'end'`, `$'record'` and remove all `*White`/`*Gray` from their
      RHS except inside the `$'op'` wrappers themselves.
- [ ] Same for `stmt_line` — the leading/trailing `*Gray` should fold
      into a single $'stmt' or be removed if redundant after the `$'kw'`
      wrappers absorb whitespace at decl boundaries.

#### G2 — Missing `$'kw'` wrappers for keyword tokens (HIGH)

Currently only operator/punctuation tokens have `$'kw'` wrappers.
Every Snocone-reserved word and every Rebus keyword should have one.

- [ ] Add `$'if'`, `$'then'`, `$'else'`, `$'while'`, `$'do'`,
      `$'function'`, `$'end'`, `$'record'` per beauty.sno line
      192-196 model.

#### G3 — Use of `shift(...)`/`reduce(...)` instead of infix `~`/`&` (DEFERRED)

8 `shift(` calls, 18 `reduce(` calls, 0 infix `~`/`&` uses.  Per the
session #3 watermark Issue 3, the Snocone parser declares `T_2TILDE`
and `T_2AMP` tokens but has zero grammar productions for them — the
infix forms are not yet implemented in the runtime.

- [ ] **DO NOTHING here yet** — keep `shift(...)`/`reduce(...)`.
      Document the deviation in the file header with a one-line note:
      `// note: Snocone runtime does not yet parse infix ~/&; using`
      `// function-call forms shift()/reduce() instead.  See`
      `// GOAL-PARSER-REBUS.md session #3 watermark Issue 3.`
- [ ] Open a sibling rung in `GOAL-LANG-SNOCONE.md` (or a new
      `GOAL-SNOCONE-INFIX-OPSYN.md` if Lon prefers) to add grammar
      productions for `T_2TILDE` / `T_2AMP` to `snocone_parse.y`.
      Once that lands, every `parser_*.sc` flips in one pass.
- **Judgment note:** the `~`/`&` forms in beauty.sno are sugar.  The
      function-call forms compile to identical engine calls.  This is
      a readability cleanup, not a correctness gate — defer until the
      runtime supports it.

#### G6 — Leading-underscore source identifiers (MEDIUM)

Four hits: `_qtag` (in `semantic.sc`, not in this file), `_rb_callname`,
`_rb_n`, `_rb_strbody` (locals to this file).

- [ ] Rename `_rb_callname` → `rbCallname` (or `rbCallName`).
- [ ] Rename `_rb_n` → `rbLabelN` (the label counter — name should
      describe the role).
- [ ] Rename `_rb_strbody` → `rbStrBody`.
- **Judgment note:** `_qtag` lives in `semantic.sc` and is grandfathered
      per Style Guideline #6.  Do not touch it here.

#### G8 — Blank lines instead of `//===` / `//---` dividers (MEDIUM)

70 blank lines in a 455-line file.  Style says zero; replace each with
a divider comment, OR collapse adjacent declarations that are
conceptually one block.

- [ ] Sweep blank lines: between section headers and bodies, replace
      blank with appropriate `//===` (major) or `//---` (minor)
      divider at 120 chars.
- [ ] Inside a single conceptual block (e.g. several `$'op'` defs in
      a row), collapse blank lines without adding dividers.
- **Judgment note:** strict zero-blank-lines gets ugly fast in a 600+
      line file.  The intent is "structure shown by dividers, not by
      whitespace".  One blank line between major sections is fine if
      a `//===` header follows — but never two consecutive blanks.

#### G8 — Brace blocks for single-statement bodies (LOW)

Five hits in the post-parse lowering functions (`lower_function_decl`,
`lower_record_decl`, the driver):

```
while (i = LT(i, n(pm)) i + 1) {
    pstr = pstr (GT(i, 1) ',', '') REPLACE(v(c(pm)[i]), &LCASE, &UCASE);
}
```
should become:
```
while (i = LT(i, n(pm)) i + 1)
    pstr = pstr (GT(i, 1) ',', '') REPLACE(v(c(pm)[i]), &LCASE, &UCASE);
```
or, if it fits:
```
while (i = LT(i, n(pm)) i + 1) pstr = pstr (GT(i, 1) ',', '') REPLACE(v(c(pm)[i]), &LCASE, &UCASE);
```

- [ ] Convert the 5 single-statement brace blocks to inline form.
- **Judgment note:** Snocone's parser may or may not accept the
      brace-less form; verify with a 3-line test before sweeping.  If
      braces are required syntactically, leave them and document the
      deviation in the file header.

#### G10 — Driver local variable case (LOW)

Driver uses `Src`, `Line`, `parse_root` (mixed conventions).  Per
Guideline #6, variables are lowerCamel/snake_case.

- [ ] Rename driver locals: `Src`→`src`, `Line`→`line`,
      `parse_root`→`parseRoot`.
- **Judgment note:** beauty.sc itself uses `Src` and `Line` as driver
      locals (lines 547-557).  This is a cross-PARSER convention
      drift; either accept the inherited beauty.sc style here, OR
      open a sibling cleanup against beauty.sc and parser_snocone.sc
      to flip them in one pass.  **Recommend defer** until the larger
      cross-PARSER convention is decided.

#### G11 — `nl_one = ANY(nl)` wrapping (HIGH)

Five hits.  Per Style Guideline #11, `nl` is used directly.

- [ ] Delete `nl_one = ANY(nl);` definition (line 93).
- [ ] Replace every `nl_one` reference with bare `nl`:
      `stmt_line` (line 198), `blank_body` (line 206),
      `function_decl` body (lines 230, 232),
      `record_decl` body (line 241).
- **Judgment note:** `ANY(nl)` matches a single newline character;
      bare `nl` IS a single newline character.  These should be
      semantically identical; the wrapping just adds indirection.
      If a smoke test reveals a Snocone runtime quirk where bare `nl`
      behaves differently in some pattern context, document and
      revert — but the default is to use bare `nl`.

#### Gate

This rung's gate is operational, not stylistic.  After the cleanup:

- [ ] `bash scripts/test_parser_rebus.sh` produces some non-zero
      number of PASSes (currently 0).  Even one PASS clears this gate
      — the goal is "the cleanup didn't break anything that wasn't
      already broken", not "the rewrite landed".
- [ ] Self-check greps from `## Style Guidelines for parser_*.sc § 12`
      either pass OR have a documented deviation in a `// note: ...`
      comment in the file header.
- [ ] The `RB_BODY n=0` bug (session #4 Bug C) may or may not be
      fixed by this cleanup.  If it is, the gate becomes PASS≥3
      (atom fixtures) and PARSER-RB-0 is jointly cleared with this
      rung.  If not, PARSER-RB-0 stays open.

**Sibling LANG rung:** none — pure parser-side style cleanup.

### PARSER-RB-0 — atom (rewrite) — **after RB-0a**

- [ ] Delete the wrong-shape `parser_rebus.sc` at corpus
      `f2d3077:programs/scrip/parser_rebus.sc`. Do not migrate code
      from it; the structure is wrong end-to-end. The git history
      preserves it.
- [ ] Write new `parser_rebus.sc` following the worked atom example
      above verbatim — `Compiland`, `Command`, `stmt`, `atom`, the
      lex tokens, the driver. Three test fixtures, no more.
- [ ] Self-check greps from the worked example all pass.
- [ ] PASS=3 on `atom_id`, `atom_int`, `atom_str`.
- **Sibling LANG rung:** RB-1.
- **Gate:** PASS=3 AND every grep self-check passes.

### PARSER-RB-1 — assignment `x := expr` (rewrite)

- [ ] Add an `assign` sub-pattern. Fixed-arity (lhs + rhs = 2):
      ```
      assign = *Id ~ "'E_VAR'" ws_opt ':=' ws_opt *atom ("'STMT_ASSIGN'" & 2);
      ```
      The lhs id is shifted as `E_VAR` so it lands on the stack as a
      tree node, not a raw string. The reduce folds `(lhs, rhs)` into
      a `STMT_ASSIGN` 2-child tree. (Reduce-target name is whatever
      maps cleanly to the canonical `(STMT :eq :subj :repl)` shape;
      pick the name once and reuse — invent a `'STMT_ASSIGN'` reducer
      target string in the parser, document the corresponding TDump
      rendering rule.)
- [ ] Add `*assign` to `Command`'s alternation BEFORE bare `*atom`.
- [ ] Self-check greps still pass; `& 2` count grows by one.
- **Sibling LANG rung:** RB-1.
- **Gate:** PASS=8 AND every grep self-check passes.

### PARSER-RB-2 — control flow `if/then`, `while/do` (rewrite)

- [ ] Add `if_stmt` and `while_stmt`. Surface-shape trees:
      `if_stmt = 'if' ws_run *expr ws_run 'then' ws_run *stmt ("'IF'" & 2);`
      `while_stmt = 'while' ws_run *expr ws_run 'do' ws_run *stmt ("'WHILE'" & 2);`
- [ ] **Defer label generation** (`:goS`/`:goF`/merge labels) to a
      separate `lower_*` walk applied to the parsed tree AFTER
      `Compiland` matches. The pattern produces the surface shape;
      the lowering walks the tree and emits the label-bearing STMTs
      via `TDump`. This mirrors how `rebus_lower.c` separates parse
      from lower in the existing C frontend.
- [ ] Lowering walk uses Snocone `function`s with `if/while/for`,
      not goto.
- **Sibling LANG rung:** RB-2.
- **Gate:** PASS=12 AND every grep self-check passes.

### PARSER-RB-3 — function decls + call sites (rewrite)

- [ ] Add `function_decl` to `Command`'s top-level alternation:
      ```
      function_decl = 'function' ws_run *Id ~ "'E_VAR'" ws_opt
                      '(' nPush() *params nPop() ')' ws_opt nl_one
                      nPush() ARBNO(*stmt) ('"E_FNC_DEFINE"' & 'nTop()') nPop()
                      ws_opt 'end' ws_opt nl_one;
      ```
      (Sketch — refine names against `rebus.y`. The two `nPush()/nPop()`
      pairs scope two independent counters: one for the params list,
      one for the body-stmt list.)
- [ ] `params = *params_inner;
      params_inner = nInc() *Id ~ "'E_VAR'" FENCE(ws_opt ',' ws_opt *params_inner | epsilon);`
      The params reduce folds into an `E_PARAMS` (or whatever sval
      the existing frontend uses for the parameter list — re-verify
      from oracle output).
- [ ] Add `call` for bare `f()` no-arg calls — fixed-arity `& 1`
      since arg count is zero, name-only.
- **Sibling LANG rung:** RB-3.
- **Gate:** PASS=18 AND every grep self-check passes.

### PARSER-RB-4 — pattern match `expr ? pat` (rewrite)

- [ ] Add `match_stmt`:
      ```
      match_stmt = *expr ws_opt '?' ws_opt *pat_expr ("'STMT_MATCH'" & 2);
      ```
      `pat_expr` is `expr` per `rebus.y` line 678 (no distinction at
      the syntax level; the `?` operator distinguishes context).
- [ ] Lift the `expr` ladder (precedence layers) directly from
      `parser_snobol4.sc`'s `Expr*` chain or `parser_snocone.sc`'s —
      whichever is closer to Rebus's `rebus.y` precedence tower.
      Re-verify per-tier names against `rebus.y`.
- **Sibling LANG rung:** RB-4.
- **Gate:** PASS=25 AND every grep self-check passes.

### PARSER-RB-5 — alternation generators `a | b | c` (rewrite, n-ary)

- [ ] Add `alt_expr` per the canonical n-ary spine from
      `corpus/programs/snocone/demo/beauty/beauty.sc:67-68`:
      ```
      alt_expr = nPush() *alt_list ("'E_ALT'" & '*(GT(nTop(), 1) nTop())') nPop();
      alt_list = nInc() *cat_expr FENCE(ws_opt '|' ws_opt *alt_list | epsilon);
      ```
      Note the reduce-count `'*(GT(nTop(), 1) nTop())'` — only emit
      an `E_ALT` reduce if there is more than one operand. A bare
      `a` (no `|`) leaves a single atom on the stack with no E_ALT
      wrapper. This matches beauty.sc's classic idiom and is the
      whole point of n-ary: `a | b | c` becomes `(E_ALT a b c)`,
      `a` stays as-is.
- [ ] `cat_expr` is whatever Rebus's next-tighter precedence layer
      is per `rebus.y` `cat_expr` (concat operator). At RB-5 if
      concat hasn't been added yet, `cat_expr` aliases to `atom`.
- [ ] **Divergence-driven gate.** The existing Rebus frontend
      produces binary E_ALT (see `## Divergence-driven rungs`).
      Alt-bearing fixtures (`alt_*.reb` — 7 of them) will FAIL the
      `tree_equal` gate in PAT-RB-5 until upstream LANG-RB-5 lands
      a flatten step in `rebus_lower.c`. Mark them
      "divergence-pending" in the rung commit, do NOT count as FAIL.
      Non-alt fixtures still gate normally.
- **Sibling LANG rung:** RB-5 (must be opened with a flatten task).
- **Gate:** PASS=25 (RB-4 baseline; alt fixtures divergence-pending)
      AND every grep self-check passes AND the divergence is reported
      upstream.
- **Final gate** (after upstream flatten lands): PASS=32.

### PARSER-RB-6 — record decls (rewrite)

- [ ] Add `record_decl` to `Command`'s top-level alternation:
      ```
      record_decl = 'record' ws_run *Id ~ "'E_VAR'" ws_opt
                    '(' nPush() *fields nPop() ')' ws_opt nl_one
                    ("'E_FNC_DATA'" & 'nTop() + 1');  // +1 for the name
      ```
      Same n-ary fold as `function_decl`'s params. The `+1` accounts
      for the leading record-name on the stack.
- [ ] `fields` mirrors `params_inner` from RB-3.
- [ ] Field-list joining into the existing-frontend's
      `"NAME(F1,F2)"` E_QLIT shape lives in a TDump rendering rule
      keyed on the reduce target, not in a hand-rolled emit
      function. (If the n-ary divergence applies here too —
      existing frontend folds fields into a single quoted string,
      PAT-RB keeps them as separate tree children — handle per
      `## Divergence-driven rungs`.)
- **Sibling LANG rung:** RB-6.
- **Gate:** PASS=38 (or PASS=N+divergence-pending) AND every grep
      self-check passes.

---

## Invariants

- Rebus's existing frontend is younger; tree divergences may surface
  bugs in EITHER frontend. PAT-RB does not silently conform.
- Test programs in `corpus/programs/rebus/parser/` are owned by PAT-RB.
- `.ref` files captured at rung-land time.
- **A rung is not landed until every rubric self-check passes AND
  the fixture gate passes (or the failing fixtures are documented
  as divergence-pending with an upstream LANG ticket).** Tree
  equivalence alone is not sufficient. Pattern shape is part of
  the deliverable.

---

## Watermark

PARSER-RB-0..RB-6 wrong-shape attempt landed sessions #62 (Claude
Sonnet 4.7, 2026-05-03) — PASS=38 FAIL=0 against 38 fixtures, but
the parser is a goto-driven line-at-a-time state machine, not a
Snocone pattern. **Every rubric item from #1 through #10 is
violated.** Rungs reopened for rewrite.

Reopened with explicit pattern architecture (session continuation,
2026-05-03):
  - One `Compiland` pattern, beauty.sc spine, matched ONCE against
    the entire concatenated source via a single `Src ? Compiland`.
  - No user-defined functions called from inside parsing patterns;
    only `Shift`/`Reduce` (via `~`/`&`) and counter primitives
    (`nPush`/`nInc`/`nTop`/`nPop`). Built-in pattern primitives
    (LEN, SPAN, BREAK, ANY, FENCE, ARBNO, etc.) remain available.
  - Body-capture idiom for delimited tokens: opening and closing
    delimiters matched by sibling sub-patterns; only the body
    goes through `~`. Demonstrated for E_QLIT in worked example.
  - OPSYN binary `~` (shift) and `&` (reduce) operators throughout.
  - `nPush()`/`nInc()`/`nTop()`/`nPop()` for every list-fold.
  - All trees n-ary; no left, no right.
  - Zero goto, zero labels.
  - Divergence-driven rungs handling for cases where the existing
    frontend produces binary trees that PAT-RB folds n-ary.

Current-tree heads: corpus `f2d3077`, one4all/parser `dd6ad80d`,
`.github` (this commit) — all on remote. The wrong-shape
`parser_rebus.sc` is in corpus at `f2d3077`; the rewrite starts
by deleting it and writing a fresh one following the worked atom
example above.

`test_parser_rebus.sh` carries the `normalize()` whitespace-collapse
upgrade from session #62 — keep that, it is correct.

The 38 fixtures in `corpus/programs/rebus/parser/` are correct —
keep them. The whole rewrite gates against the same 38 (with
divergence-pending markings as needed).

PARSER-RB-0 — next.

---

## Session 2026-05-03 continuation — PARSER-RB-0 rewrite INCOMPLETE

Session rewrote `parser_rebus.sc` from scratch with correct shape:
- One `Compiland` pattern, beauty.sc spine
- `nPush`/`nInc`/`nTop`/`nPop` n-ary folds
- `shift()`/`reduce()` function-call forms
- No goto, no labels in driver; structured `while`/`if` only
- Post-parse `lower_*` functions walk surface tree → emit STMT TDump lines
- No user functions called from inside patterns

**Three blocking issues — not yet resolved:**

### Issue 1 — HANG: blank_line in ARBNO does not guarantee cursor advance
`blank_line = ws_opt nl_one` — `ws_opt` can match empty; if `nl_one` also
fails, ARBNO spins. Fix: ensure `blank_line` always consumes at least one
newline. Replace with `(ANY(' ' tab nl) | epsilon)` or require `nl_one`
before `ws_opt`. Alternative: remove `blank_line` from `Command` entirely
and consume leading/trailing whitespace+newlines in `function_decl` and
`record_decl` preambles.

### Issue 2 — RUBRIC VIOLATION / HANG: user function called from qlit pattern
`qlit_dq = '"' DQ_body . _rb_strbody '"' epsilon . *Shift(s_QLIT, _rb_strbody)`
— `*Shift(...)` is a user function called from inside a pattern. Violates
rubric item 5. Also may cause the hang.
Fix: use the dot-conditional capture idiom WITHOUT calling Shift from the
pattern. Look at how `parser_snobol4.sc` handles String capture — it uses
`BREAK(.) . _strbody` global then calls `shift()` in the outer context, or
restructures so the body lands in a global that is then shifted in `primary`.

### Issue 3 — RUNTIME GAP: ~ and & binary OPSYN not supported
`T_2TILDE` and `T_2AMP` are declared in `snocone_parse.y` as tokens but
have **zero grammar productions** — the Snocone parser rejects them with
a syntax error. All six existing sibling parsers use `shift()`/`reduce()`
function-call forms. The rubric's `~`/`&` forms require a Snocone frontend
extension. Keep `shift()`/`reduce()` for now; open a separate goal to add
binary OPSYN support to snocone_parse.y if desired.

**Next session action:**
1. Fix Issue 1: restructure `Command` blank-line handling.
2. Fix Issue 2: restructure string capture to not call Shift from inside pattern.
   Model: `String = (SQ_open *SQ_body . _rb_s SQ_close | ...)` then in
   `primary` use `shift(*String, s_QLIT)` — but Shift captures the full
   match span including quotes. Better: follow `parser_snobol4.sc:44` which
   uses `. _strbody` dot-conditional to capture body into a global, then
   calls `shift()` from `primary` using a helper that reads `_strbody`.
   Allowed: dot-conditional assignment `pat . global` is NOT a function call —
   it is built-in pattern assignment. `*Shift(...)` IS a function call — banned.
3. Note Issue 3 in watermark; keep `shift()`/`reduce()` forms.
4. Gate: PASS=3 on atom_id, atom_int, atom_str.

corpus HEAD at emergency handoff: `bc52be1`
one4all/parser branch: `dd6ad80d` (unchanged)
.github: this update

---

## Session 2026-05-03 continuation #2 — beauty.sc-style refactor (INCOMPLETE)

Three architectural directions from Lon were applied to parser_rebus.sc:

### 1. Build-time pattern-builder helpers (RB_*)
Replaced raw `epsilon . *fn(args)` literals in pattern definitions with
build-time helpers that return pattern fragments via EVAL:
- `RB_save(.var, expr)` returns `epsilon . *assign('var', expr)`
- `RB_qlit_emit('_rb_strbody')` returns the push-E_QLIT fragment
- `RB_call_emit('_rb_callname')` returns the push-RB_CALL fragment

Pattern grammar now reads cleanly — no `*fn(...)` literal anywhere outside
the helper bodies themselves.  Same idiom as semantic.sc's nPush/nInc/nTop.

### 2. $'op' operator wrappers (beauty.sc lines 50-58 style)
```
$'(' = '(' *Gray;       $')' = *Gray ')';
$',' = *Gray ',' *Gray;
$':=' = *Gray ':=' *Gray;
$'?' = *Gray '?' *Gray;
$'|' = *Gray '|' *Gray;
$'+' = *Gray '+' *Gray;     // and -, *, /
```
Used throughout the expression ladder.

### 3. Direct quoted-form tag constants (no sq indirection, no s_/r_ prefixes)
```
// shift() tags (bare).
E_VAR  = 'E_VAR';
E_ILIT = 'E_ILIT';
E_QLIT = 'E_QLIT';

// reduce() tags (quote-embedded).
Parse        = "'Parse'";
RB_FUNC_DECL = "'RB_FUNC_DECL'";
RB_ASSIGN    = "'RB_ASSIGN'";
E_ALT        = "'E_ALT'";
... etc
nTop_gt1     = '*(GT(nTop(), 1) nTop())';
```
Each tag appears in exactly one context (shift OR reduce), so no _R suffix.
Call sites: `shift(*Id, E_VAR)`, `reduce(E_MUL, 2)`, `reduce(E_ALT, nTop_gt1)`.

### Architecture also corrected
- Command/Compiland use parser_snocone.sc idiom: `Command = (*func_cmd | *rec_cmd | *blank)` with nInc inside each decl alternative; `ARBNO(Command)` (no `*`).
- stmt_list uses the same shape.
- postfix_expr restructured: `id_call_pat = (Id . _rb_callname '(' *Gray ')')` captures the call-form atomically so the `(call | primary)` alternation has no shared prefix that traps FENCE.
- String body capture uses canonical dot-conditional `BREAK('"') . _rb_strbody` (built-in primitive, not a function call).

### One blocking issue — hangs on atom fixtures

Minimal-grammar bisection tests (`/tmp/test_g4.sc` with body; `/tmp/test_g5.sc`
with alt_expr nPush/X_alt/nPop) all parse correctly.  The full parser hangs.

**Suspected cause:** the doubled-FENCE chains in mul_expr / add_expr:
```
mul_expr = *postfix_expr
           FENCE(  $'*' *postfix_expr reduce(E_MUL, 2) FENCE($'*' *postfix_expr reduce(E_MUL, 2) | epsilon)
                 | $'/' *postfix_expr reduce(E_DIV, 2) FENCE($'/' *postfix_expr reduce(E_DIV, 2) | epsilon)
                 | epsilon
                );
```
This shape is non-canonical — parser_snocone.sc uses a flatter form.  Port
that shape exactly:
```
Expr9 = *Expr17
        ( *op_mul *Expr17 reduce(r_MUL, 2)
              (*op_mul *Expr17 reduce(r_MUL, 2) | epsilon)
        | *op_div *Expr17 reduce(r_DIV, 2)
              (*op_div *Expr17 reduce(r_DIV, 2) | epsilon)
        | epsilon
        );
```
No outer FENCE; flat alternation.  Likely the immediate fix.

**Next-session bisection plan:**
1. Strip mul_expr to `mul_expr = *postfix_expr`. Verify atom_id passes.
2. Restore add_expr identically. Verify.
3. Reintroduce mul_expr `*` chain in the parser_snocone.sc shape (no FENCE).
4. Reintroduce `/`, `+`, `-` similarly.
5. Once atoms pass, run full PASS=38 gate.

corpus HEAD: `9f6b32f`
one4all/parser branch: `dd6ad80d` (unchanged)
.github: this update follows

---

## Session 2026-05-03 continuation #3 — primary cleanup, bare tags

Lon's correction: the over-parameterized RB_qlit_emit('_rb_strbody') /
RB_call_emit('_rb_callname') helpers were noise — single-use globals
don't need parameter passing.  Renamed to match parser_snocone.sc:
  RB_qlit_emit(...) → RB_push_qlit()
  RB_call_emit(...) → RB_push_call()

primary now reads byte-identical to parser_snocone Expr17:
  primary = FENCE(  *String  RB_push_qlit()
                  | shift(*Integer, E_ILIT)
                  | shift(*Id,      E_VAR)
                 );

ALSO: dropped quote-embedding on all reduce() tags.  semantic.sc INFRA-11c
(commit c8ee2a6) added _qtag() which auto-quotes both shift and reduce
tag args.  All tags now bare:
  E_VAR        = 'E_VAR';
  E_ALT        = 'E_ALT';
  RB_ASSIGN    = 'RB_ASSIGN';
  Parse        = 'Parse';
  ... etc.
Call sites unchanged: shift(*Id, E_VAR), reduce(E_MUL, 2),
reduce(E_ALT, nTop_gt1), reduce(Parse, 'nTop()').

Hang remains unresolved.  Next session task unchanged:
- Strip mul_expr/add_expr doubled-FENCE chains.
- Port parser_snocone.sc's flat-alternation tier shape exactly.

corpus HEAD: 707bd5d
one4all/parser: dd6ad80d (unchanged)

---

## Session 2026-05-04 continuation #4 — style guidelines codified, two bug fixes

This session was opened by Lon to "play with the Rebus language grammar
PATTERN" and codify the canonical style for `parser_*.sc` parsers.

### 1. `## Style Guidelines for parser_*.sc` — new section above

Comprehensive 12-rule section added above the "Divergence-driven rungs"
heading.  Derived directly from beauty.sno (the SNOBOL4 reference) and
beauty.sc (its Snocone port) in `corpus/programs/snobol4/demo/beauty/`
and `corpus/programs/snocone/demo/beauty/`.  Covers:

  1. White / Gray defined once, attached at token sites (never strewn
     through grammar).
  2. `$'kw'` wrappers for Snocone-reserved words and operators;
     identifier names (with `$' '`/`$'  '` whitespace prefix) for
     non-reserved word tokens.
  3. The three equivalent surface forms for AST decoration (explicit
     dot-conditional, function-call shorthand, infix `~`/`&`) with
     OPSYN bindings from semantic.sc.
  4. n-ary tree counters (`nPush`/`nInc`/`nTop`/`nPop`).
  5. Tree-tag names matching the IR `EXPR_t` enum (`E_VAR`, `E_ADD`,
     etc.) plus language-prefix tags (`RB_*`) for surface-only
     constructs.
  6. Identifier naming case discipline (no leading-underscore source
     ids; functions UpperCamel, variables lowerCamel/snake).
  7. Non-terminal names mirror the official language BNF.
  8. Code layout — 120-col, single-stmt inline `if (x) action;`,
     `//===` and `//---` dividers replacing blank lines.
  9. Zero goto, zero labels.
  10. Driver shape: stdin slurp → `src ? Compiland` → tree walk.
  11. `nl` used directly as a pattern primitive — do NOT define
      `nl_one = ANY(nl)`.
  12. Self-check grep targets.

This section is normative for all six `parser_*.sc` (PARSER-RB,
PARSER-SC, PARSER-SN, PARSER-IC, PARSER-PL, PARSER-RK).  Sibling
PARSER-* goal files cross-reference here; future style-related changes
land in this single canonical section, then flow to siblings via
cross-reference.

### 2. SCRIP build environment — `libgc-dev` required

`scripts/build_scrip.sh` failed at session start with:
```
src/runtime/x86/snobol4.h:21:10: fatal error: gc/gc.h: No such file or directory
```
Resolved by `apt-get install -y libgc-dev`.  Suggests
`scripts/install_system_packages.sh` should ensure libgc-dev is in its
package list (the install script may already do so but timed out
during this session — verify next session).  No source changes; this
is a diagnostic note for the next session that hits the same.

### 3. Two bug fixes applied to `parser_rebus.sc` (incremental, not landed)

The current parser hangs on every fixture (PASS=0 FAIL=38, all exit
124 timeout).  Two confirmed bugs identified and patched, but a third
hang remains:

**Bug A — doubled-FENCE chains in mul_expr/add_expr (FIXED):**
The previous session's `mul_expr` used:
```
FENCE($'*' *postfix_expr reduce(...) FENCE($'*' *postfix_expr reduce(...) | epsilon) | ... | epsilon)
```
which causes infinite spin in the ARBNO/FENCE interaction.  Replaced
with parser_snocone.sc's flat-alternation tier shape (no outer FENCE):
```
mul_expr = *postfix_expr
           ( $'*' *postfix_expr reduce(E_MUL, 2) ($'*' *postfix_expr reduce(E_MUL, 2) | epsilon)
           | $'/' *postfix_expr reduce(E_DIV, 2) ($'/' *postfix_expr reduce(E_DIV, 2) | epsilon)
           | epsilon
           );
```
Same for `add_expr`.

**Bug B — `*stmt` referenced but `stmt` undefined (FIXED):**
`if_stmt` and `while_stmt` referenced `*stmt` which was never defined.
The actual statement-line non-terminal is `stmt_line`.  Replaced.

**Bug C — stmt_list captures n=0 (UNRESOLVED):**
After A and B, isolated bisection shows `stmt_list` with
`ARBNO(body_one)` where `body_one = (*stmt_item | *blank_body)` matches
the input but the resulting RB_BODY tree has 0 children — `stmt_item`
fails to capture the body line, falling through to `blank_body` which
just consumes a newline.  Suspected cause: the order of nInc / shift
inside the `stmt_item` chain causes the counter increment to commit
before the actual shift, so on FENCE backtrack the count is correct
but no tree was pushed.  Bisection trace:
```
&FULLSCAN = 1; ... stmt_list = nPush() ARBNO(body_one) reduce(RB_BODY, 'nTop()') nPop();
Src = '  x' nl 'end' nl;     // 8 chars
Src ? stmt_list  →  MATCH t=RB_BODY n=0
```

Next-session task is to bisect further — instrument `stmt_item` /
`stmt_line` directly, confirm whether Shift fires, then either fix the
ordering or, more likely, REWRITE parser_rebus.sc from scratch
following the new Style Guidelines section (1-12) above.  The current
file accumulates four sessions of incremental-fix scar tissue and is
no longer the cleanest path forward.  Per Rubric and per goal "Status"
section: the rewrite is the task; this session's bug-fix patches are
diagnostic, not the deliverable.

### 4. State at session end

| Repo | HEAD | Note |
|------|------|------|
| corpus | 707bd5d (unchanged on remote) | local has Bug A and Bug B patches uncommitted |
| one4all/parser | dd6ad80d (unchanged) | |
| .github | this commit | adds Style Guidelines section + this watermark |

The uncommitted local patches in corpus are diagnostic, not the
deliverable.  Next session should either (a) commit them as
intermediate progress and continue bisecting, or (b) discard them and
rewrite parser_rebus.sc fresh per the new Style Guidelines.  Lon
chooses; the goal-rubric position is that rewrite is the cleaner path.

PARSER-RB-0 — still next.

---

## Session 2026-05-04 continuation #5 — RB-0a partial; fresh rewrite landed; END-leak blocker

EMERGENCY HANDOFF — RB-0a and RB-0 both incomplete.

### Work landed this session

Started executing PARSER-RB-0a sub-tasks.  Discarded the 455-line
scar-tissue `parser_rebus.sc` and wrote a fresh 134-line atoms-only
parser following the new ## Style Guidelines.  Landed at corpus HEAD
`da12182`.

Style guidelines applied:
  - **G1** — White/Gray confined to token wrappers; zero *White/*Gray
    in any grammar production
  - **G2** — Added `$'function'`, `$'end'`, `$'record'`, `$'if'`,
    `$'then'`, `$'while'`, `$'do'` keyword wrappers
  - **G6** — Renamed `_rb_strbody`/`_rb_n` → `rbStrBody`/`rbLabelN`
  - **G8** — `//===` / `//---` dividers; single-statement while bodies
    inline (no braces)
  - **G11** — `nl_one` deleted; bare `nl` used per beauty.sc
  - **G3** — DEFERRED (Snocone runtime gap, documented in file header
    note)
  - **G10** — DEFERRED (driver `Src`/`Line` per beauty.sc convention,
    documented in file header note)

### Behavior change

Hang RESOLVED.  Parser produces complete tree output for the
function/main shape.  Failure mode shifted from `exit 124` (timeout)
on all 38 fixtures to tree-equality FAIL — still PASS=0 FAIL=38, but
real progress.

### Blocker for next session — END-leak in body iteration

`func_body = nPush() ARBNO(nInc() *stmt) reduce(RB_BODY, nTop()) nPop();`
works structurally, but produces a spurious `(STMT :subj (E_VAR END))`
in the body output.

Mechanism: when ARBNO iteration consumes `'end'` as a bare Id via
`shift(*Id, E_VAR)`, then the outer trailing `'end' nl` in
`function_decl` can't match, so ARBNO backtracks one iteration.  At
that point `nInc()` decrements correctly BUT the previously-shifted
`tree('E_VAR', 'end')` node REMAINS on the stack (Shift's stack-push
side-effect is not undone on pattern backtrack).  `reduce(RB_BODY,
nTop())` then folds the wrong set of children.

Tested negative-lookahead idioms — none worked as zero-width pattern
predicate in this Snocone runtime:

| Idiom | Result |
|-------|--------|
| `(~(*Gray 'end' kw_tail))` | tilde negates value, not zero-width pattern |
| `(~ResWord) Id_raw`        | same — Id still matched 'end' |
| `('end' kw_tail FAIL | epsilon)` | FAIL primitive not implemented for patterns |
| `@bp ... 'end' kw_tail TAB(bp)` | overall pattern fails |

### Recommended next-session approach

Apply the beauty.sno § 24-28 / beauty.sc § 24-32 idiom:
**`*match(List, NotInList)`** where the match-time guard predicate
IS pattern-composable — it's the built-in `match()` pattern primitive
in `semantic.sc`, not user code (see Rubric § 5 — built-in primitives
are allowed inside patterns).  Shape:

```snocone
ResWords    = 'end function record if then else while do until ' ...;
NotResWord  = (POS(0) | ' ') *upr(rbIdRaw) (' ' | RPOS(0));
Id_raw      = ANY(&UCASE &LCASE '_') (SPAN(&UCASE &LCASE digits '_') | epsilon);
//  Id captures into rbIdRaw, then match() asserts rbIdRaw IS in
//  ResWords iff we want this to FAIL.  The 'NotInList' direction is
//  negation of 'TxInList' from beauty.sc — implementation: a *match
//  variant or a fresh predicate.
Id = Id_raw . rbIdRaw . *match_NotIn(ResWords, NotInList);
```

Verify that `semantic.sc`'s `match()` helper supports the inverse
("FAIL if found") form.  If not, add it as a sibling helper
`match_NotIn(List, Predicate)` — that's the same call signature as
`match()` and is idiomatic per beauty.sno.

**Alternative:** introduce `shift_when_not_keyword(p, t, list)`
build-time helper that wraps `shift(p, t)` with the reserved-word
filter; cleaner surface for callers but same underlying mechanism.

### Status

| Repo | HEAD | State |
|------|------|-------|
| corpus | `da12182` | fresh atoms-only parser_rebus.sc, END-leak blocker |
| one4all/parser | `dd6ad80d` | unchanged |
| .github | this commit | RB-0a partially done; watermark updated |

Steps remaining in PARSER-RB-0a (per session #4 enumeration):
- [ ] G1, G2, G6, G8, G11 — DONE in this session's rewrite
- [ ] G3 — DEFERRED, documented in file header
- [ ] G8 (blank-line sweep) — N/A in fresh file (zero blanks)
- [ ] G8 (single-stmt brace blocks) — DONE in fresh file (inline form)
- [ ] G10 — DEFERRED, documented in file header
- [ ] **Gate** — currently PASS=0; gate clears when END-leak fixed.

Steps remaining in PARSER-RB-0:
- [ ] Resolve END-leak via `match()` predicate idiom above
- [ ] PASS=3 on `atom_id`, `atom_int`, `atom_str`

PARSER-RB-0a + PARSER-RB-0 — joint clearance once END-leak resolved.
