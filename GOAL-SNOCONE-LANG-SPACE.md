# GOAL-SNOCONE-LANG-SPACE — SNOBOL6: SPITBOL Re-imagined with Structured Control

**Repo:** one4all + corpus
**Working repo/build name:** `snocone` (rename to `snobol6` deferred — see Q11 below)
**User-facing language name:** **SNOBOL6**
**Done when:** A new language called SNOBOL6 exists that is

  1. **A SPITBOL functional superset** — every SPITBOL operator
     (the nine printed unary, the eleven printed binary), every
     keyword, every primitive function, the full pattern-matching
     sublanguage, **`OPSYN`**, and every SPITBOL extension
     (multi-assign, embedded match-and-replace, alternative
     evaluation).  Snocone additionally provides C-style
     comparison-operator sugar (`==` `!=` `<` `<=` `>` `>=`,
     plus their string and ident counterparts) that lower to the
     SPITBOL functional forms.  A SPITBOL program that does not
     itself use `==`/`!=`/`<`/`<=`/`>`/`>=`/`===`/`!==`/`:==:`/etc.
     as binary operator characters runs unchanged under Snocone,
     modulo statement terminator (`;`) and label syntax.
  2. **Spaced like SPITBOL** — concatenation is juxtaposition
     (whitespace between value-yielding tokens); function call vs.
     concat is disambiguated by `f(args)` (zero space) vs.
     `f (args)` (space — concat); unary operators bind tight to
     their operand (no intervening space).
  3. **Control-flow like C/C++** — `if`, `else`, `while`, `do`,
     `for`, `switch`/`case`, `break`, `continue`, `return`.  No
     `goto` syntax (label-jumps via `:S(...)` etc. retained for
     SPITBOL-statement compatibility, but never required for new
     code).  Block delimiters `{` `}`.  Statement terminator `;`.
  4. **No `&&` and no `||`** — both are removed entirely.  In
     places C uses `&&`/`||`, Snocone uses SPITBOL's existing
     primitives: `&` is the keyword-name unary operator, `|` is
     pattern alternation, juxtaposition is concat, and SPITBOL's
     **alternative evaluation** `(expr1 , expr2 , expr3)` (comma
     as value-list inside parens) handles "first that succeeds"
     short-circuit semantics.
  5. **Conditional expressions backtrack** — the parenthesised
     condition of `if`, `while`, `do/while`, `do/until`, the test
     position of `for`, and the tag of `case` is a **single
     SPITBOL backtracking expression** that produces success or
     failure.  Specifically the SPITBOL form

         SUBJ ? PATTERN = REPLACEMENT

     is a legal condition.  The branch (then / else / loop body
     / fallthrough) is the success or failure exit of that
     expression — exactly the way SPITBOL's `:S(...)F(...)`
     branches work today, dressed in C clothing.
  6. **Implemented with Flex + Bison** — the lexer/parser dual
     coordination needed to make space-as-concat unambiguous is
     handled by Flex/Bison (no hand lexer/parser).  The lexer
     emits a synthetic CONCAT token at the appropriate boundaries
     using a "previous-token" state; the grammar treats CONCAT as
     a normal binary operator at SPITBOL priority 4.

This is **not** Andrew Koenig's 1978 Snocone.  Koenig's prototype
is an inspiration and the existing `.sc` corpus borrows his
surface syntax, but Lon's directive overrides any place where
Koenig's choices differ from this goal.  This is **a Snocone
redo** — the SPITBOL face-lift framing of session #1 was wrong.
We are making a new language.

---

## Naming — SNOBOL6

Lon (session 2026-04-30 #3):

> "The new name would be funny if it was SNOBOL6 since all that
> was bad with SNOBOL4 as the line by line thing and missing
> structured control.  And SNOBOL5 already exists."

The user-facing language name is **SNOBOL6**.

The joke lands on three layers:

1. **SNOBOL4 (1968)** is the version everyone remembers — the
   line-by-line one with no structured control flow, where every
   loop is a labeled goto.  Its weakness in the eyes of modern
   programmers was *exactly* the missing structured control.
2. **SNOBOL5** does exist as a name — Gimpel's late-1970s
   announced successor that never shipped (sometimes called
   "Vanilla SNOBOL").  We are not reusing the name; we step over
   it.
3. **SNOBOL6** is the structured-control reboot that picks up
   where SNOBOL5 was supposed to.  The number tells the story:
   the line-by-line era ended at 4, the unbuilt successor was 5,
   and 6 is what should have happened — the same language with
   `if`/`while`/`for`/`do`/`switch`/`{`/`}`/`break`/`continue`,
   and juxtaposition concat from SPITBOL.

The source tree, scripts, test gates, and build targets continue
to use `snocone` through LS-6 to minimize the patch noise during
implementation.  A separate dedicated rename goal
(`GOAL-LANG-SNOBOL6-RENAME`) handles the source-tree rename,
file-extension change, and documentation updates as a single
sweep — so the structured-control work and the naming change
don't blur together in git history.  Open question Q11 (below)
captures the file-extension decision; the rename goal opens
after LS-6 lands.

---

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
bash /home/claude/one4all/scripts/build_spitbol_oracle.sh
```

Gate after setup (existing Snocone gates — must remain green
throughout the early design rungs, may regress and recover during
the implementation rungs LS-3..LS-7):

```bash
bash /home/claude/one4all/scripts/test_smoke_snocone.sh
bash /home/claude/one4all/scripts/test_beauty_snocone_all_modes.sh
bash /home/claude/one4all/scripts/test_smoke_unified_broker.sh
```

---

## Directive — what overrides Koenig

Lon: "Ignore Andrew Koenig where my directive overrides it."

The directive overrides Koenig in these specific places:

| Topic                          | Koenig 1978                 | This goal                                  |
|--------------------------------|-----------------------------|--------------------------------------------|
| Concat operator                | `&&`                        | space (juxtaposition), à la SPITBOL        |
| Alternative-eval / "or"        | `\|\|`                      | SPITBOL `(e1 , e2 , e3)` alternative-eval  |
| Numeric comparison ops         | `==` `!=` `<` `<=` `>` `>=` | **kept** (Lon session #2) — sugar lowering to `EQ()` `NE()` `LT()` `LE()` `GT()` `GE()` |
| String / lexical comparison    | `:==:` `:!=:` `:<:` `:<=:` `:>:` `:>=:` | **kept** — sugar lowering to `LEQ()` `LNE()` `LLT()` `LLE()` `LGT()` `LGE()` |
| Identity comparison            | (Koenig had none)           | **NEW**: spelling **TBD** — see Q12 below. Lowers to `IDENT()` `DIFFER()` (succeed/fail predicates) regardless of spelling. |
| Modulo                         | `%`                         | **reserved for `OPSYN`** — no built-in modulo. Use `REMDR(a,b)`. (Lon session #2: "If `%` is user config symbol it can not be used for modulo.") |
| Conditional in `if (cond)`     | C-like boolean              | SPITBOL backtracking expression (succeed/fail) |
| `for (init, test, step)`       | three comma-separated exprs | three semicolon-separated SPITBOL exprs (matches C; comma is reserved for value-lists) |
| Goto keyword                   | `go to label`               | `goto label;` (single keyword, C spelling) |

Koenig kept (no override needed):
- `if (cond) { … } else { … }`  — dangling `else` binds to innermost `if`, C semantics.
- `while (cond) { … }`
- `for (a; b; c) { … }`
- `do { … } while (cond);` and `do { … } until (cond);`
- `switch (expr) { case v1: … case v2: … default: … }`
- `procedure name(args) { … }`
- `return expr;` `freturn;` `nreturn;`
- block braces `{` `}` and statement terminator `;`
- empty statement `;`, empty block `{ }`
- **labels**: `name :` at the start of a clause names the following statement (Koenig L690)
- **goto**: `goto name;` (C spelling — Koenig used `go to`; we tighten to single-keyword `goto`)
- **`break;` and `break label;`** — see Q13 below. Lon session #3:
  "I like the labeled break since SNOBOL4 and Snocone has labels
  already.  Let's do that instead of C."  Snocone has labels in
  the language already, so labeled-break is a natural fit.  We
  also have `goto` — the SNOBOL6 escape valve — which arguably
  makes labeled-break redundant.  This is experimental; we will
  find out the pros and cons as we use it.
- **`continue;` and `continue label;`** — symmetric with `break`.

---

## Bare expressions, statements, failure, and newlines

Lon (session 2026-04-30 #2):

> "How does Snocone handle bare expressions that are not contained
> within an `if (...)` conditional expression?  Can they fail?"

A bare expression statement is just an expression followed by `;` —
no `if`, no `while`, no surrounding control flow.  Per Koenig's
`expcl` (line 348 of `snocone.sno`) and `dostmt` (line 384), the
bare expression lowers to a top-level SPITBOL statement with no
`:S(...)F(...)` decoration.  This matches the SNOBOL4 default:
**a statement that fails just falls through to the next statement.**
Failure of a bare expression has no further consequence.

```snocone
EQ(x, y);          // succeeds or fails; either way, next stmt runs
GT(x, 0)  x = -x;  // negate x if positive (succeed-and-side-effect idiom)
                   // bare-statement: no :S/:F branches generated
```

Failure-as-control-flow is reserved for the parenthesised conditions
of `if`, `while`, `do/while`, `do/until`, `for` (test position),
and `case` tags.  In those positions the success/failure exit
of the expression drives the branch; everywhere else, failure is
silent.

This is the SPITBOL way and Snocone does nothing different.

> "There is no special processing of new-line character."

Confirmed and binding.  The Snocone lexer treats newlines exactly
like blanks and tabs — they are whitespace, full stop.  Statement
boundary is `;` only.  No "implicit `;` at end of line", no `\`
continuation token, no off-side rule.  This means
`x = 1\ny = 2;` is **not** two statements — it is the single
expression `x = 1 y = 2` (which evaluates `1 y = 2` as a chain
and assigns the result to `x`, almost certainly not what was
meant).  Programs that lack `;` will produce surprising parses,
not error messages.  This is by design; matches C's lack of a
"forgot the semicolon" warning.

(For one-statement-per-line readability, source files conventionally
write each statement on its own line with `;` at the end — but the
parser does not care.)

> "Do implement `label:` and `goto label` statements."

Adopted.  Two productions:

```
label_stmt : IDENT ':' clause     // labels a clause; can stack: L1: L2: clause
goto_stmt  : GOTO IDENT ';'       // unconditional jump to label
```

Lowering: `label:` emits `label  ` at column 1 in the SPITBOL
output (Koenig's `emitlab`); `goto name;` emits `:(name)` at the
end of the previous statement, or as a standalone empty statement
if there is no previous expression (Koenig's `emitg(dest)`).

Snocone keyword: **`goto`** (single word — we tighten Koenig's
`go to` two-word form to the C single-keyword form).

`goto` is the escape hatch for any control-flow shape the
structured forms don't cover — labeled-break out of nested loops,
state-machine dispatch, retry-from-error.  Using it for ordinary
control flow is discouraged; the structured forms (`if`/`while`/
`for`/`do`/`switch`) cover the 95% case.

---

## SPITBOL Operator Precedence Table — the canonical source

Extracted verbatim from **SPITBOL Manual v3.7 Chapter 15, "Operators"**
(`spitbol-manual-v3_7.pdf`, the printed pages titled 181–183).

### Unary operators (all equal priority, higher than any binary, right-to-left)

| Op | Name           | Definition                                     |
|----|----------------|------------------------------------------------|
| `@` | at sign       | Assigns cursor position to its operand          |
| `~` | tilde         | Negates failure or success of its operand       |
| `?` | question mark | Interrogation — returns null if operand succeeds|
| `&` | ampersand     | Keyword                                          |
| `+` | plus          | Indicates positive numeric operand               |
| `-` | minus         | Negates numeric operand                          |
| `*` | asterisk      | Defers evaluation of expression                  |
| `$` | dollar sign   | Indirection                                      |
| `.` | period, dot   | Returns a name                                   |

Undefined unary operators (available for `OPSYN`):
`!`  `%`  `/`  `#`  `=`  `|`

### Binary operators (highest priority first)

| Op       | Assoc  | Pri | Definition                               |
|----------|--------|-----|------------------------------------------|
| `=`      | right  |  0  | Assignment                                |
| `?`      | left   |  1  | Pattern match                             |
| `\|`     | right  |  3  | Pattern alternation                       |
| *space*  | right  |  4  | **Concatenation or match**                |
| `+`      | left   |  6  | Addition                                  |
| `-`      | left   |  6  | Subtraction                               |
| `/`      | left   |  8  | Division                                  |
| `*`      | left   |  9  | Multiplication                            |
| `^` `!` `**` | right | 11 | Exponentiation                          |
| `$`      | left   | 12  | Immediate assignment (in pattern context) |
| `.`      | left   | 12  | Conditional assignment (in pattern ctx)   |

Undefined binary operators (available for `OPSYN`):

| Op | Assoc | Pri | |
|----|-------|-----|--|
| `&` | left  |  2  | Unused |
| `@` | right |  5  | Unused |
| `#` | left  |  7  | Unused |
| `%` | left  | 10  | Unused |
| `~` | right | 13  | Unused |

### SPITBOL extensions (Manual Ch.15 footnote)

- Multiple assignment: `A = B = C + 1`
- Embedded pattern matching/replacement: `A = (B ? C = D) + 1`
- **Alternative evaluation** — `A = (LT(I,J) I , GT(I,J) J , "Same")` —
  expressions in a parenthesised list separated by `,` are evaluated
  left to right until one succeeds; the value of the first succeeder
  is the value of the whole.

The alternative-evaluation extension is the **direct replacement
for `||`**.  It is already part of SPITBOL — we do not invent it.

---

## Comparison: SPITBOL precedence vs. Koenig `bconv[]`

Koenig's `bconv[]` table from `snocone.sno` lines 600–627:

| Op        | lp | rp | slp | srp | fn | Notes                    |
|-----------|----|----|-----|-----|----|--------------------------|
| `(`       | 0  |    |     |     |    | sentinel                 |
| `=`       | 1  | 2  | 0   | 1   |    | assign                   |
| `?`       | 2  | 2  | 1   | 1   |    | pattern match            |
| `\|`      | 3  | 3  | 2   | 2   |    | alternation              |
| `\|\|`    | 4  | 4  | 0   | 0   | fn | "or" — Koenig only       |
| `&&`      | 5  | 5  | 4   | 4   |    | concat — Koenig only     |
| `>`       | 6  | 6  | 0   | 0   | fn | GT()                     |
| `<`       | 6  | 6  | 0   | 0   | fn | LT()                     |
| `>=`      | 6  | 6  | 0   | 0   | fn | GE()                     |
| `<=`      | 6  | 6  | 0   | 0   | fn | LE()                     |
| `==`      | 6  | 6  | 0   | 0   | fn | EQ()                     |
| `!=`      | 6  | 6  | 0   | 0   | fn | NE()                     |
| `:>:`     | 6  | 6  | 0   | 0   | fn | LGT()                    |
| `:<:`     | 6  | 6  | 0   | 0   | fn | LLT()                    |
| `:>=:`    | 6  | 6  | 0   | 0   | fn | LGE()                    |
| `:<=:`    | 6  | 6  | 0   | 0   | fn | LLE()                    |
| `:==:`    | 6  | 6  | 0   | 0   | fn | LEQ()                    |
| `:!=:`    | 6  | 6  | 0   | 0   | fn | LNE()                    |
| `+`       | 7  | 7  | 5   | 5   |    | addition                 |
| `-`       | 7  | 7  | 5   | 5   |    | subtraction              |
| `/`       | 8  | 8  | 7   | 7   |    | division                 |
| `*`       | 8  | 8  | 8   | 8   |    | multiplication           |
| `%`       | 8  | 8  | 0   | 0   | fn | REMDR()                  |
| `^`       | 9  | 10 | 10  | 11  |    | exponentiation           |
| `.`       | 10 | 10 | 11  | 11  |    | name-of                  |
| `$`       | 10 | 10 | 11  | 11  |    | indirection              |

Where `lp`/`rp` are left/right output priorities (Pratt-style),
`slp`/`srp` are "stack left/right" priorities, and `fn=1` means
"emit as `OP(L,R)` rather than `L op R`".  The numeric scale (0..10)
is Koenig's; SPITBOL's printed table uses a different scale (0..13)
but the relative ordering is the same.

### Disagreements (where Koenig diverges from SPITBOL — to fix)

1. **`||` and `&&` exist in Koenig only.**  Both are removed in this goal.
2. **`==` `!=` `<` `<=` `>` `>=` (numeric comparison)** — Koenig
   added these as comparison syntax that lower to `EQ()`/`NE()`/etc.
   SPITBOL does **not** have these as binary operators.  Lon
   session #2 directs us to **keep all six** as Snocone-only
   comparison sugar.  They are binary operators at priority 6
   (same as `+`/`-`), `fn=1` lowering (emit as functional call),
   succeed/fail predicates whose value is the LHS on success.
3. **`:==:` `:!=:` `:<:` `:<=:` `:>:` `:>=:` (string lexical
   comparison)** — same reasoning as #2.  **Keep all six.**
   Lower to `LEQ()` `LNE()` `LLT()` `LLE()` `LGT()` `LGE()`
   respectively.  Priority 6, `fn=1`.
4. **`===` `!==` (identity comparison)** — NEW operators added by
   this goal (Koenig had no equivalent).  Lower to `IDENT()` and
   `DIFFER()` — succeed/fail predicates that test SNOBOL4 object
   identity (same value, same type, no coercion).  Priority 6,
   `fn=1`.  These two operators distinguish "same object" from
   "same numeric value" — SPITBOL programmers know the difference
   matters; making it lexically distinct from `==` is the win.
5. **`%`** — Koenig used `%` for modulo (lowering to `REMDR()`).
   Lon session #2: "If `%` is user config symbol it can not be
   used for modulo."  **Decision:** `%` is reserved as an
   undefined binary OPSYN slot (priority 10, matching SPITBOL's
   undefined-binary table) and as an undefined unary OPSYN slot.
   Modulo is `REMDR(a, b)` only — no operator syntax.
6. **`^` exponent right-priority `9/10`** — Koenig's table has
   `lp=9, rp=10`.  SPITBOL prints exponentiation at priority 11.
   **Decision:** match SPITBOL — exponent at priority 11, right
   associative.  The Koenig 9/10 split was a Pratt-parser
   implementation artifact; we use Bison precedence declarations
   and follow the printed SPITBOL table exactly.
7. **`,` (comma)** — Koenig's table doesn't list it because
   Koenig used `,` only inside `f(a,b)` arg lists.  In this goal
   `,` is also the alternative-evaluation separator inside
   parens.  Precedence: lower than `=` (priority -1, "below
   everything"), unparenthesised at top level it's a syntax error.

Net effect: **Snocone has SPITBOL's full operator set, plus 14
C-style comparison-sugar operators (six numeric + six string + two
identity), plus alternative-eval `,`, plus C-style control flow.**
Koenig's `&&`/`||`/`%` are removed; their SPITBOL equivalents
(SPACE for AND-ish, `(,)` for OR-ish, `REMDR()` for modulo) take
over.  `%` joins `&`/`@`/`#`/`~` as the five undefined binary
OPSYN slots.

---

## Architecture (what changes, where)

### 1. Lexer (`src/frontend/snocone/snocone.l` — NEW Flex source)

Today's `snocone_lex.c` is hand-written.  This goal replaces it
with a **Flex** source file that is processed by
`scripts/regenerate_parser_and_lexer_from_sources.sh` into
`snocone.lex.c`.  The Flex source maintains a small "previous
token" state and, on every emitted token, decides whether to
prepend a synthetic `TOK_CONCAT` based on these rules:

```
prev-token can-end-expr   AND   next-token can-start-expr
   AND   at least one whitespace char (or newline-with-+-continuation)
   between them    →    emit TOK_CONCAT before the next token
```

**Can-end-expr**: `IDENT`, `INTEGER`, `REAL`, `STRING`, `RPAREN`,
`RBRACKET`, `RBRACE`-of-block-expr (none today, reserved).

**Can-start-expr**: `IDENT`, `INTEGER`, `REAL`, `STRING`,
`LPAREN`, `LBRACKET`, unary-op (`*`, `&`, `~`, `@`, `.`, `$`,
`+`, `-`, `?`).

**Special-case: `f(`** — when `IDENT` is followed by `(` with
**zero whitespace between**, the lexer emits `IDENT_LPAREN_NOSP`
(call form) instead of `IDENT` + `LPAREN`.  Bison's grammar
has a single rule for call-form using this combined token.
After the matching `RPAREN`, the prev-token is set to
`RPAREN-of-call` which is can-end-expr.

**Special-case: `&IDENT`** — `&` followed by `IDENT` with zero
whitespace is a **keyword reference** (e.g. `&FULLSCAN`,
`&UCASE`).  The lexer emits `KEYWORD_NAME` as a single token,
not unary-`&` plus `IDENT`.

### 2. Grammar (`src/frontend/snocone/snocone.y` — NEW Bison source)

Bison precedence declarations match the SPITBOL table:

```
%right '='                          /* pri 0 */
%left  '?'                          /* pri 1 */
%right '|'                          /* pri 3 */
%right TOK_CONCAT                   /* pri 4 */
%left  '+' '-'                      /* pri 6 */
%left  '/'                          /* pri 8 */
%left  '*'                          /* pri 9 */
%right '^' '!' TOK_STARSTAR         /* pri 11 */
%left  '$' '.'                      /* pri 12 — dual-role: also unary */
%right TOK_UNARY                    /* highest — applied via %prec on unary rules */
```

Priority 2, 5, 7, 10, 13 left as gaps — those slots are the
SPITBOL undefined binary operators (`&`, `@`, `#`, `%`, `~`)
which can be wired up at runtime via `OPSYN`.  The grammar
includes catch-all rules `expr undef_binop expr` whose semantic
action consults the `OPSYN` table at compile time.

The conditional in `if`, `while`, `do`-`while`, `do`-`until`,
and `case` tag is a single `expr` non-terminal — **the same
backtracking expression that appears as a SPITBOL statement
subject/pattern/replacement chain**.  No special "boolean
expression" non-terminal is introduced.  Success/failure of
the expression drives the branch, exactly as SPITBOL's
`:S(...)F(...)` does.

### 3. Lowering (`src/frontend/snocone/snocone_lower.c`)

Every C-style control structure lowers to SNOBOL4 IR with `:S(...)F(...)`
branches:

| Snocone source            | SNOBOL4-IR equivalent                             |
|---------------------------|---------------------------------------------------|
| `expr;`  (bare statement) | emit `expr` as bare SPITBOL statement; failure is silent fall-through |
| `name : stmt`             | emit `name` at column 1 before lowered `stmt`     |
| `goto name;`              | append `:(name)` to current statement, or emit empty `:(name)` clause |
| `if (cond) S1`            | `cond  :F(after)` `S1` `after  …`                 |
| `if (cond) S1 else S2`    | `cond  :F(else)` `S1  :(after)` `else  S2` `after  …` |
| `while (cond) S`          | `top  cond  :F(after)` `S  :(top)` `after  …`     |
| `do S while (cond);`      | `top  S` `cond  :S(top)`                          |
| `do S until (cond);`      | `top  S` `cond  :F(top)` (until = while-not — failure repeats) |
| `for (init; cond; step) S`| `init` `top  cond  :F(after)` `S` `step  :(top)` `after  …` |
| `switch(e){case v: S; ..}`| chain of `IDENT(e, v)  :S(caseN)` plus a default fallthrough |
| `break;`                  | `:(after-of-innermost-enclosing-loop-or-switch)` (Q13: pending whether plain `break;` is permitted alongside labeled form, or labeled-only) |
| `break label;`            | `:(after-of-loop-or-switch-tagged-by-label)` — explicitly named target |
| `continue;`               | `:(top-of-innermost-enclosing-loop)` (Q13: same pending question as `break;`) |
| `continue label;`         | `:(top-of-loop-tagged-by-label)` |
| `return E;`               | `name = E  :(RETURN)`                             |
| `freturn;`                | `:(FRETURN)`                                       |
| `nreturn;`                | `:(NRETURN)` (`name = .x` already done before)    |
| `(e1, e2, e3)` (alt-eval) | already a SPITBOL extension — emit as-is to SPITBOL backend; for non-SPITBOL backends, lower to a chain of `:S(after)` branches |
| `EQ()` `NE()` `LT()` `LE()` `GT()` `GE()` (numeric comparison sugar `==` `!=` `<` `<=` `>` `>=`) | already SPITBOL primitives; emit functional form |
| `LEQ()` `LNE()` `LLT()` `LLE()` `LGT()` `LGE()` (lexical comparison sugar `:==:` `:!=:` `:<:` `:<=:` `:>:` `:>=:`) | already SPITBOL primitives; emit functional form |
| `IDENT()` `DIFFER()` (identity sugar — spelling TBD per Q12) | already SPITBOL primitives; emit functional form |

### 4. Corpus migration

Every `.sc` file in `corpus/programs/snocone/` gets:

- `&&` removed (replaced by space — the new concat operator)
- `||` removed (rewritten as `(,)` alternative-eval; if the `||`
  was used as boolean-or in a condition, the comma form
  preserves the short-circuit semantics)
- `go to NAME` → `goto NAME` (single keyword)
- Statement terminators verified — `;` already in use today

Comparison operators (`==` `!=` `<` `<=` `>` `>=` `:==:` `:!=:`
`:<:` `:<=:` `:>:` `:>=:`) are **kept** in the corpus — the new
grammar accepts them.  Identity comparison (`===` `!==`) is new
and not yet in the corpus; it can be adopted by hand where
desired but no mass rewrite is needed.

`%` does not currently appear as binary modulo in the corpus
(verify with `grep -n '[^&]% [^=]' corpus/programs/snocone/`);
if any uses appear, rewrite to `REMDR(a, b)`.

A migration script (`scripts/util_migrate_snocone_to_lang_space.py`)
does the mechanical sweep.  Manual review handles edge cases
(strings containing `&&` or `||`, `%` inside format specifiers, etc.).

---

## Open design questions (resolve before LS-3)

### Q1. `f(args)` vs `f (expr)` — strict zero-space rule

**Decision:** strict.  `f(` (zero chars between `f` and `(`) is a
function call; `f (` (one or more spaces/tabs) is `f` concat
`(expr)`.  This matches SPITBOL exactly and matches the user's
mental model.  The lexer implements it via the special token
`IDENT_LPAREN_NOSP` described above.

### Q2. What replaces `||` in conditions?

In Koenig: `if (DIFFER(x) || DIFFER(y)) { … }`

Three replacement options:

  **A.** Alternative-eval inside parens:
     `if ((DIFFER(x) , DIFFER(y))) { … }` — the `(e1,e2)` succeeds if
     either e1 or e2 succeeds.
  **B.** Pattern alternation `|` (only valid in pattern context;
     not appropriate for predicates).
  **C.** A user-defined `OPSYN` for `|` (or another undefined
     binary op) that does boolean-or.

**Decision:** A.  It is a SPITBOL extension that already does
exactly what's needed.  Document the idiom in RULES.md once
LS-7 lands.

### Q3. What replaces `&&` in conditions?

In Koenig: `if (~HOST(2) && nclause(1)) { … }`

In a SPITBOL backtracking-expression world, **juxtaposition is
already short-circuit AND** — `e1 e2` succeeds iff e1 succeeds
*and then* e2 succeeds.  So `if (~HOST(2) nclause(1)) { … }` is
the direct replacement, with a space where `&&` used to be.

**Decision:** juxtaposition (space-as-concat) replaces `&&` in
conditions.  This is the same mechanism that does string concat
in normal expressions — it's all one operator.

### Q4. `for (init; test; step)` — `;` not `,`

Koenig's original Snocone used `,` between the three parts of
`for`.  We use `;` to match C and to free `,` for alternative-eval.

**Decision:** `for (init; test; step) { … }`.  Matches C and
matches the C++ programmer's muscle memory.

### Q5. `do { … } while (cond);` vs `do { … } until (cond);`

Both supported.  `until` is the failure-repeats variant — the
loop body re-runs while `cond` *fails*.  This maps cleanly onto
SPITBOL's `:F(top)` branch and gives Snocone a natural
"failure-driven loop" that idiomatic SNOBOL4 already uses.

### Q6. `switch (e) { case v1: … case v2: … default: … }`

The `case` tag is a backtracking expression.  Lowering:

```
switch (e) { case v1: A; case v2: B; default: D; }
```

becomes:

```
   tmp = e
   IDENT(tmp, v1)   :S(c1)
   IDENT(tmp, v2)   :S(c2)
                    :(cd)
c1 A   :(after)
c2 B   :(after)
cd D
after
```

`break` is implicit at end of each case (no fall-through, matching
modern usage; explicit `fallthrough;` added in a later rung if
there is demand).

### Q7. Statement terminator — `;` mandatory

Every Snocone statement ends with `;`.  This is unambiguous given
the lexer's space-as-concat rule (a bare newline is whitespace,
not a terminator — so `1\n2` would be concat without `;`).  The
existing Snocone corpus already terminates statements with `;`.

### Q8. Comments — `//` to end of line, `/* … */` block

Already in use in current `.sc` files.  Keep both.

### Q9. Compatibility flag for old `.sc` files

**Decision:** none.  The migration script rewrites every existing
`.sc`.  After LS-7 lands, `&&` and `||` in `.sc` source are
syntax errors.  Same atomic-flip approach the previous version
of this goal called for.

### Q10. Working name — RESOLVED to SNOBOL6 (session #3)

Lon session #1: "We will do Snocone different from Andrew Koenig.
We might later find a better name."

Lon session #3: "The new name would be funny if it was SNOBOL6
since all that was bad with SNOBOL4 as the line by line thing
and missing structured control.  And SNOBOL5 already exists."

**Decision:** SNOBOL6 is the user-facing language name.  See the
Naming section near the top of this file for the rationale.  The
source tree, scripts, and build targets continue to use `snocone`
through LS-6 to keep the structured-control patch noise low; the
rename sweep is its own goal.  See Q11 below.

### Q11. Rename `snocone` → `snobol6` source-tree sweep — when?

The user-facing language name is SNOBOL6 (Q10).  The source tree,
build scripts, test gates, and file extensions all currently use
`snocone`.  When does the rename happen?

**Option A — atomic during this goal.**  Add an LS-8 step that
renames `src/frontend/snocone/` → `src/frontend/snobol6/`,
updates every script `test_smoke_snocone.sh` →
`test_smoke_snobol6.sh`, renames every `.sc` → new extension
(see file-extension question below), updates every reference in
`RULES.md`, `PLAN.md`, all goal files.  Single big sweep, single
commit train.

**Option B — deferred to its own goal.**  Open
`GOAL-LANG-SNOBOL6-RENAME` after LS-6 lands.  The structured-
control work (LS-1..LS-6) keeps using `snocone` paths/names
internally; user-facing docs and a `LANGUAGE.md` say "SNOBOL6";
the rename sweep happens cleanly in a single goal with no LS-N
work mixed in.

**File extension** — currently `.sc`.  Three candidates if we
rename: `.sn6`, `.s6`, `.sno6`, or keep `.sc` since it's already
in every gate and corpus path.

**Decision (default — Lon may overrule):** Option B for the rename
timing; extension TBD when the rename goal opens.  The rename is a
mechanical sweep that's clearer as its own commit than as the tail
of a structured-control overhaul.

### Q12. Identity-op spelling — `::` `:!:` vs `:===:` `:!==:` vs another form

Three candidate spellings for the new `IDENT()`/`DIFFER()` sugar:

  **A.** `::` and `:!:` — short, no collision with `:==:` (lexical
     equality, already taken).  Reads as "the colon-bracketed form,
     stripped to the bare comparison".  Two characters, fast to type.
     Lon session #3 wrote "`::` and `:!:`" which most naturally
     parses to this option.
  **B.** `:===:` and `:!==:` — three-equal-signs to lexically
     distinguish from the two-equal `:==:` `:!=:` lexical-comparison
     family.  Symmetric with the existing `:==:` family.  Five chars.
  **C.** `===` and `!==` — JS/Java/modern syntax, three chars, no
     colons.  Visually distinct from `==` `!=` but breaks the
     "the colons mean special" SNOBOL4 convention.

**Pending Lon's confirmation.**  Default placeholder until
confirmed: **Option A** (`::` and `:!:`), based on the most
natural reading of session #3's instruction "Let's keep `::` and
`:!:` I suppose for IDENT and DIFFER."  Once decided, every
reference to identity-comparison spelling in this file (the
directive table, the disagreements section, the lowering table)
gets the chosen spelling.

### Q13. `break;` / `continue;` — with optional label or labeled-only?

Lon session #3: "I like the labeled break since SNOBOL4 and
Snocone has labels already.  Let's do that instead of C."

Two readings of "instead of C":

  **A.** Both forms allowed: plain `break;` exits innermost loop/
     switch (the C default), `break label;` exits the loop/switch
     tagged by `label`.  Same for `continue`.  Java's design.
     Best of both — common case is short, nested-exit case is
     possible.
  **B.** Labeled-only: `break;` is a syntax error; `break label;`
     is the only form.  Forces the programmer to explicitly name
     the loop/switch they're exiting.  More verbose but no
     "innermost" trap.

Lon noted: "we do have `goto` here to solve needing Java's
labeled break" — which points at a third option:

  **C.** No `break`/`continue` at all.  The structured loops
     `if`/`while`/`do`/`for`/`switch` cover the common case, and
     `goto exit_label;` covers any nested-exit need.  Smallest
     keyword set.

Pros/cons matrix (this is experimental — we will find out):

| Choice | Pros | Cons |
|--------|------|------|
| A (both forms) | familiar; common case short; nested-exit possible; C/Java muscle memory | "innermost" rule needs documenting; trap remains for nested switch-in-loop |
| B (labeled only) | no innermost trap; explicit; readable on grep | verbose at every break; programmers will resist; punishes the common case |
| C (no break) | smallest keyword set; goto already covers everything; matches "SNOBOL6 has labels already" | every loop exit goes through goto, which we're trying to deprioritize for new code; symmetry with `continue` lost |

**Pending Lon's pick.**  Default placeholder until confirmed:
**Option A**, with the caveat that this is the experimental
choice and we may revisit if `break;` plain turns out to be a
trap in practice.

---

## Steps

> Convention: each step closes with a single commit (or back-to-back
> commits if `one4all`+`corpus` both touched), gates green where
> required, and the next-step pointer in `PLAN.md` updated.

### LS-0 ✅ — Read SPITBOL manual & extract canonical precedence (DONE)

- [x] LS-0.a — Read SPITBOL Manual Ch.15 "Operators" (printed pp.181-183).
- [x] LS-0.b — Extract unary table, binary table, undefined-op table,
      and SPITBOL extensions list verbatim into this Goal file.
- [x] LS-0.c — Extract Koenig's `bconv[]` table from `snocone.sno`
      (lines 600–627) into this Goal file.
- [x] LS-0.d — Identify every disagreement between the two and
      record the resolution.
- [x] LS-0.e — Resolve open design questions Q1–Q10 with a default
      decision (see above).  Lon may overrule any of these in LS-1.

### LS-1 — Lexer design specification

- [ ] LS-1.a — Write the complete lexer state machine in this
      Goal file: every "previous-token" state, every "can-end" set,
      every "can-start" set, every special-case rule (`f(`,
      `&IDENT`, `:` for goto-field, etc.).
- [ ] LS-1.b — Write a 50-line test corpus in this Goal file:
      input source on the left, expected token stream on the
      right.  Include every edge case (string with embedded `&&`,
      `f (x)` vs `f(x)`, `&FULLSCAN` vs `& FULLSCAN`,
      backtracking-condition in `if`, alternative-eval `(,,)`).
- [ ] LS-1.c — Lon reviews; revise until approved.
- [ ] No code yet.

### LS-2 — Grammar design specification

- [ ] LS-2.a — Write the complete Bison grammar skeleton in this
      Goal file: every non-terminal, every production, every
      precedence declaration, every action (in pseudocode that
      maps to the IR).
- [ ] LS-2.b — Show how every existing `.sc` construct lowers
      under the new grammar.  Specifically: every `if`/`while`/
      `for`/`do`/`switch`/`procedure` form in the corpus, every
      use of `&&`/`||`/`==`/`!=`/`<`/`<=`/`>`/`>=`/`%`/`:==:`/
      `:!=:`/`:>:`/`:<:`/`:>=:`/`:<=:` in the corpus.
- [ ] LS-2.c — Define the alternative-evaluation `(,,)` grammar
      production and its lowering for SPITBOL backend (pass-through)
      and non-SPITBOL backends (lowered to a chain of `:S(after)`
      branches).
- [ ] LS-2.d — Lon reviews; revise until approved.
- [ ] No code yet.

### LS-3 — Lexer implementation (Flex)

- [ ] LS-3.a — Create `src/frontend/snocone/snocone.l` (new Flex source).
- [ ] LS-3.b — Update `scripts/regenerate_parser_and_lexer_from_sources.sh`
      to handle Snocone's `.l` (the script may already be generic;
      if not, extend).
- [ ] LS-3.c — Run the LS-1.b test corpus through the new lexer;
      every token stream matches.
- [ ] LS-3.d — Existing hand-written `snocone_lex.c` removed in
      same commit as the new generated `snocone.lex.c` lands.
- [ ] LS-3.e — Smoke test — `test_smoke_snocone.sh` MAY regress
      here because the parser hasn't caught up; that's expected
      and OK as long as LS-4 closes the gate again.

### LS-4 — Grammar implementation (Bison)

- [ ] LS-4.a — Create `src/frontend/snocone/snocone.y` (new Bison source).
- [ ] LS-4.b — `regenerate_parser_and_lexer_from_sources.sh`
      processes it into `snocone.tab.c` / `snocone.tab.h`.
- [ ] LS-4.c — Existing hand-written `snocone_parse.c` removed in
      same commit as the new generated `.tab.c` lands.
- [ ] LS-4.d — `test_smoke_snocone.sh` PASS=5 again.
- [ ] LS-4.e — `test_smoke_unified_broker.sh` PASS=49+ FAIL=0.

### LS-5 — Corpus migration script

- [ ] LS-5.a — Write `scripts/util_migrate_snocone_to_lang_space.py`.
      Rewrites: `&&` → space; `||` → `(,)`; `go to NAME` → `goto NAME`;
      any `%` modulo uses → `REMDR(a, b)`.  String literals untouched.
      Comment blocks untouched.  Comparison operators (`==`/`!=`/
      `<`/`<=`/`>`/`>=`/`:==:`/family) preserved as-is.
- [ ] LS-5.b — Dry-run on a single file (`omega.sc` or similar small
      one); manual review; iterate until clean.
- [ ] LS-5.c — Apply to every `.sc` file under
      `corpus/programs/snocone/`.  Diff-review every file.

### LS-6 — Atomic landing

- [ ] LS-6.a — Land the new lexer + grammar + corpus migration in
      a single commit train: `one4all` first (lexer/grammar/build),
      `corpus` second (rewritten `.sc` files), `.github` last
      (this goal file marked LS-6 done, PLAN.md pointer advances).
- [ ] LS-6.b — All three gates green:
      `test_smoke_snocone.sh` PASS=5,
      `test_beauty_snocone_all_modes.sh` PASS=42 SKIP=3,
      `test_smoke_unified_broker.sh` PASS=49+ FAIL=0.
- [ ] LS-6.c — `beauty.sc` produces output byte-identical to its
      pre-migration `.ref` in all three Snocone modes.

### LS-7 — Documentation pass

- [ ] LS-7.a — Update `RULES.md`'s Snocone language-facts section:
      no `&&`, no `||`, juxtaposition concat, alt-eval `(,,)`,
      conditions are SPITBOL backtracking expressions.
- [ ] LS-7.b — Update `GOAL-SNOCONE-BEAUTY.md`'s language-facts
      table to drop `&&`/`||` and add the C-control flow + space
      semantics.
- [ ] LS-7.c — Update `REPO-one4all.md`'s Snocone section to
      describe Flex/Bison build path and the SPITBOL-superset goal.
- [ ] LS-7.d — Add a short `programs/snocone/LANGUAGE.md` to
      corpus that summarises the language for the next reader.

---

## Invariants

- `test_smoke_snocone.sh`, `test_beauty_snocone_all_modes.sh`,
  `test_smoke_unified_broker.sh` must all close green at LS-6.
  May regress between LS-3 and LS-4 (lexer-without-parser window);
  must not stay regressed past LS-6.
- No `.sno` source files modified — this goal is purely about
  Snocone (`.sc`).
- Generated parser/lexer files (`*.lex.c`, `*.tab.c`, `*.tab.h`)
  are regenerated and committed alongside the `.l`/`.y` sources,
  per RULES.md "Editing `.y` or `.l` files".
- Commit identity LCherryholmes / lcherryh@yahoo.com per RULES.md.
- The new language is a **functional superset** of SPITBOL —
  every SPITBOL primitive function and operator works.  Snocone
  adds 14 comparison-operator characters (`==` `!=` `<` `<=` `>`
  `>=` and the lexical `:==:` family and `===` `!==`) that
  SPITBOL leaves undefined; Snocone adds C-style control flow.
  A SPITBOL program that does not itself use those character
  sequences as binary operators runs unchanged under Snocone,
  modulo `;` terminator and label syntax.  This is a hard
  invariant; any divergence is a bug.

---

## Cross-goal coordination

- **GOAL-SNOCONE-BEAUTY (SB-6.D active):** the `beauty.sc`
  language-change sweep is part of LS-5/LS-6 here.  SB-6.D's
  ongoing investigation of `EVAL(EXPRESSION)` at the Reduce call
  site is independent — that bug must be fixed before LS-6 lands
  or LS-6 will fail the byte-identical gate.  Coordinate
  explicitly when SB-6.D closes.
- **GOAL-LANG-SNOCONE (D-1):** the Snocone frontend ladder.
  This goal IS the next major milestone in that ladder.  When
  LS-7 lands, `GOAL-LANG-SNOCONE` advances from D-1 to D-2.
- **GOAL-SNOCONE-CLAWS5 (CL-2), -TREEBANK-LIST (TB-1), -IR-BB
  (SC-1), -DEMOS (SD-1):** frozen during the language transition.
  Resume on the new syntax after LS-6.
- **GOAL-LANG-SNOBOL4 (SN-32 done):** independent.  SNOBOL4
  frontend is unchanged — only the Snocone frontend is affected.

---

## Reference materials

- `spitbol-manual-v3_7.pdf` — SPITBOL Manual Release 3.7 (Mark
  Emmer / Robert B. K. Dewar, Catspaw Inc.).  Ch.15 "Operators"
  pp.181–183 is the canonical precedence source.  Lon will
  arrange for this PDF to be added to corpus or `.github`
  knowledge per RULES.md's "no preloaded reference material" rule.
- `SNOCONE/snocone.sno`, `SNOCONE/snocone.sc`, `SNOCONE/snocone.snobol4`
  — Andrew Koenig's original 1978 Snocone compiler (uploaded by Lon
  this session).  `bconv[]` table at `snocone.sno` lines 600–627
  cited above.  This goal **diverges** from Koenig where Lon's
  directive overrides; the upload is reference, not template.
