# GOAL-SNOCONE-LANG-SPACE — Andrew's Final Snocone Vision + Lon's SPITBOL Space Restoration

**Repo:** one4all + corpus
**Language name:** **Snocone** (Andrew's name preserved — session #5)
**Done when:** A new Snocone exists that is exactly

> **Andrew Koenig's `.sc` self-host operator design (his "final vision"
> for the language he wrote in itself), plus Lon's restoration of
> SPITBOL's space-as-concat semantics — `&&`, `||`, and `%` removed,
> juxtaposition concat and alternative-eval `(,)` and OPSYN-`%`
> taking over.**

Andrew's `.sc` self-host (`SNOCONE.zip` lines 32–60) is the canonical
operator set we adopt.  His SPITBOL-implemented bootstrap (`.sno`,
`.snobol4`) is a slightly earlier and less-complete version of the
same language; we follow the `.sc` self-host where the two diverge.

This means the new Snocone is

  1. **Andrew's self-host operator set, kept verbatim** — every
     binary operator from his `.sc` lines 34–60 *except* the three
     Lon-removes-for-space (`&&`, `||`, `%`), and every unary
     operator from his `unaryop = ANY("+-*&@~?.$")` definition.
     Specifically: `=` `?` `|` (alternation) `>` `<` `>=` `<=`
     `==` `!=` `::` (IDENT) `:!:` (DIFFER) `:>:` `:<:` `:>=:`
     `:<=:` `:==:` `:!=:` `+` `-` `/` `*` `^` `.` `$` — 23 binary
     operators and 9 unary operators.
  2. **Lon's space restoration — `&&` removed, juxtaposition is
     concat.**  This is the SNOBOL4 / SPITBOL way: whitespace
     between two value-yielding tokens IS the concat operator.
     Andrew's `.sc` uses `&&`; we drop it and emit a synthetic
     CONCAT token from the lexer when prev-token-can-end and
     next-token-can-start with at least one whitespace char
     between them.  Same SPITBOL priority-4 right-associative
     slot, same semantics, just the surface character changes
     from `&&` to space.
  3. **Lon's alt-eval restoration — `||` removed, `(e1, e2, e3)`
     is alternative evaluation.**  This is a documented SPITBOL
     extension (Manual Ch.15): a parenthesised list of expressions
     separated by commas, evaluated left-to-right, value of the
     first to succeed becomes the value of the whole.  Andrew's
     `||` becomes the `,` form.  No semantic loss — alt-eval is
     the SPITBOL primitive his `||` was a less-flexible shortcut
     for.
  4. **Lon's OPSYN reservation — `%` removed as built-in
     modulo.**  Andrew lowered `%` to `REMDR()`.  We free `%` as
     a user-OPSYN slot (priority 10, matching SPITBOL's undefined-
     binary table).  Programs needing remainder use `REMDR(a, b)`
     directly.
  5. **`f(args)` vs `f (args)` disambiguation — restored from
     SPITBOL.**  Zero whitespace between identifier and `(` means
     function call; one or more whitespace chars means
     concatenation of the identifier with a parenthesised
     expression.  Andrew already wrote his `.sc` this way; we
     just enforce it via a special lexer token `IDENT_LPAREN_NOSP`.
  6. **Andrew's C-style structured control flow, kept verbatim**
     — `if (cond) {…} else {…}`, `while (cond) {…}`,
     `do {…} while (cond);`, `for (init; test; step) {…}`,
     `function name(args) {…}`, `return E;`, `freturn;`,
     `nreturn;`, block braces `{` `}`, statement terminator `;`.
     Andrew's grammar shape preserved exactly.
  7. **Conditions are SPITBOL backtracking expressions, NOT C-style
     booleans.**  This is the SNOBOL4 root: the parenthesised
     condition of `if`, `while`, `do/while`, `do/until`, `for`-test,
     and `case` tag is a single SPITBOL backtracking expression.
     Specifically the form `SUBJ ? PATTERN = REPLACEMENT` is a
     legal condition.  Branch (then/else/loop/fallthrough) is the
     success/failure exit, exactly the way SPITBOL's `:S(...)F(...)`
     branches work today.  This was Andrew's intent (his `*exp`
     production goes inside `if (...)` parens directly) and we
     keep it.
  8. **Implemented with Flex + Bison** — the lexer/parser dual
     coordination needed to make space-as-concat unambiguous is
     handled by Flex/Bison.  Andrew used hand-rolled SNOBOL4
     pattern matching for his lexer/parser; we use the modern
     equivalent.  The lexer maintains a previous-token state and
     emits synthetic CONCAT tokens; the grammar treats CONCAT as a
     normal binary operator at SPITBOL priority 4.

A correct SPITBOL program — modulo statement terminator (`;`) and
label syntax (`name:` not column-1) — runs unchanged under the new
Snocone.  Andrew's `.sc` self-host source itself can be read into
the new Snocone with only three mechanical edits per file: every
`&&` becomes a space, every `||` becomes `(...,...)` alt-eval, every
`%` (if any) becomes `REMDR(...)`.

---

## Naming — Snocone

Lon session #5: **the language is called Snocone.**  This is
Andrew Koenig's name, preserved.  Fitting since the language is
Andrew's `.sc` self-host vision (his `bconv[]` at lines 32–60 of
`snocone.sc`) plus Lon's restoration of SPITBOL space-as-concat
— not a new design.  The repo/build name `snocone` and the file
extension `.sc` already match.  No rename, no source-tree sweep.

Earlier sessions explored other naming ideas — Lon session #3 had
floated SNOBOL6 as a joke ("the structured-control reboot picking
up where SNOBOL5 left off") but session #4 walked it back ("not
now SNOBOL6 nor will it likely be").  Session #5 closed the
question by picking Snocone.

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

## What changes from Andrew's `.sc` self-host

Andrew's final-vision Snocone is the `.sc` self-host source he
shipped in `SNOCONE/snocone.sc` lines 32–60.  His SPITBOL-implemented
bootstrap (`snocone.sno`, `snocone.snobol4`) is a slightly earlier
version of the same language, missing the `::` and `:!:` operators
and the `struct` keyword.  The `.sc` is the *final* design — what
Andrew arrived at when he could write the language in itself.

We adopt his `.sc` operator set verbatim **with three deletions**
(Lon's "back to SPITBOL space-as-concat" directive):

| Topic                          | Andrew `.sc` self-host      | This goal                                                 |
|--------------------------------|-----------------------------|------------------------------------------------------------|
| Concat operator                | `&&` (pri 5, R)             | **REMOVED** — juxtaposition (SPACE, pri 4 SPITBOL, R)      |
| Alternative-eval / "or"        | `\|\|` (pri 4, fn lowering) | **REMOVED** — SPITBOL `(e1, e2, e3)` alt-eval extension    |
| Modulo                         | `%` → `REMDR()` (pri 8, fn) | **REMOVED** — reserved as user OPSYN slot; `REMDR(a,b)` directly |
| `for (init, test, step)`       | comma separator             | `for (init; test; step)` semicolon (frees `,` for alt-eval/value-lists) |
| `go to label`                  | (Andrew `.sno` only)        | `goto label;` (single keyword)                             |
| Conditional in `if (cond)`     | (already backtracking)      | unchanged — SPITBOL backtracking expression                |

We adopt **everything else** from Andrew's `.sc` verbatim:

| Andrew `.sc` operator | What it lowers to | Status                                             |
|-----------------------|-------------------|----------------------------------------------------|
| `=`                   | `=` (assign)      | adopted unchanged                                  |
| `?`                   | `?` (pat. match)  | adopted unchanged                                  |
| `\|`                  | `\|` (alternation)| adopted unchanged                                  |
| `>` `<` `>=` `<=` `==` `!=` | `GT` `LT` `GE` `LE` `EQ` `NE` | adopted unchanged — **6 numeric comparison sugar** |
| **`::`**              | **`IDENT()`**     | **adopted unchanged from Andrew's `.sc` line 45**  |
| **`:!:`**             | **`DIFFER()`**    | **adopted unchanged from Andrew's `.sc` line 46**  |
| `:>:` `:<:` `:>=:` `:<=:` `:==:` `:!=:` | `LGT` `LLT` `LGE` `LLE` `LEQ` `LNE` | adopted unchanged — **6 lexical comparison sugar** |
| `+` `-` `/` `*`       | `+` `-` `/` `*`   | adopted unchanged                                  |
| `^`                   | `**` (exponent)   | adopted unchanged                                  |
| `.` `$`               | `.` `$` (dual unary/binary) | adopted unchanged                       |
| `if`/`else`/`while`/`do`/`for`/`function`/`return` etc. | C-style structured control | adopted unchanged (Andrew's `procedure` keyword renamed to `function` — see Naming note below) |
| `{` `}` blocks        | block delimiters  | adopted unchanged                                  |
| `;` terminator        | statement end     | adopted unchanged                                  |
| `name :` labels       | label clause      | adopted unchanged                                  |
| `// to EOL` comments  | line comment      | adopted unchanged                                  |

We add **two things Andrew's `.sc` does not have** but that fit his
structured-control direction:

- `do {…} until (cond);` — failure-driven loop variant (Andrew has
  only `do/while`).  Maps cleanly onto SPITBOL `:F(top)` branch.
- `switch (e) { case v1: … case v2: … default: … }` — multi-way
  branch.  Andrew's `.sc` doesn't have this; we add it.  Lowers to
  a chain of `IDENT(tmp, vN) :S(cN)` predicates.

We add **`break`/`continue`** (Andrew has neither) — see Q13 below
for the form.  This is experimental; we will find out the pros and
cons as we use it.

We add **`struct`** as Andrew himself did in his `.sc` line 162 —
his self-host added a `struct` keyword on top of the SPITBOL
bootstrap.  Treat this as future work; not part of the LS-6 minimum.

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

## Comparison: SPITBOL precedence vs. Andrew Koenig `bconv[]`

Andrew Koenig's Snocone has **two slightly different operator
tables** in the source we have:

- **`snocone.sno`** and **`snocone.snobol4`** (bootstrap, written
  in SPITBOL): 25 entries, no `::` or `:!:`.
- **`snocone.sc`** (self-host, written in Snocone itself): 27
  entries, **adds `::` for `IDENT()` and `:!:` for `DIFFER()`**.

The `.sc` self-host is **Andrew's final vision** — what he was
willing to write the language as once he had a working compiler.
The bootstrap lacks two operators and the `struct` keyword that
his self-host adds.  We adopt the **`.sc` self-host** as canonical.

Koenig's `bconv[]` table from `snocone.sc` lines 32–60 (the
canonical Andrew source we adopt):

| Op        | lp | rp | slp | srp | fn | Notes                    |
|-----------|----|----|-----|-----|----|--------------------------|
| `(`       | 0  |    |     |     |    | sentinel                 |
| `=`       | 1  | 2  | 0   | 1   |    | assign                   |
| `?`       | 2  | 2  | 1   | 1   |    | pattern match            |
| `\|`      | 3  | 3  | 2   | 2   |    | alternation              |
| `\|\|`    | 4  | 4  | 0   | 0   | fn | "or" — REMOVED in this goal |
| `&&`      | 5  | 5  | 4   | 4   |    | concat — REMOVED (replaced by SPACE) |
| `>`       | 6  | 6  | 0   | 0   | fn | GT()                     |
| `<`       | 6  | 6  | 0   | 0   | fn | LT()                     |
| `>=`      | 6  | 6  | 0   | 0   | fn | GE()                     |
| `<=`      | 6  | 6  | 0   | 0   | fn | LE()                     |
| `==`      | 6  | 6  | 0   | 0   | fn | EQ()                     |
| `!=`      | 6  | 6  | 0   | 0   | fn | NE()                     |
| **`::`**  | **6** | **6** | **0** | **0** | **fn** | **IDENT() — Andrew `.sc` line 45** |
| **`:!:`** | **6** | **6** | **0** | **0** | **fn** | **DIFFER() — Andrew `.sc` line 46** |
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
| `%`       | 8  | 8  | 0   | 0   | fn | REMDR() — REMOVED (reserved as user OPSYN slot) |
| `^`       | 9  | 10 | 10  | 11  |    | exponentiation           |
| `.`       | 10 | 10 | 11  | 11  |    | name-of                  |
| `$`       | 10 | 10 | 11  | 11  |    | indirection              |

Where `lp`/`rp` are left/right output priorities (Pratt-style),
`slp`/`srp` are "stack left/right" priorities, and `fn=1` means
"emit as `OP(L,R)` rather than `L op R`".  The numeric scale (0..10)
is Andrew's; SPITBOL's printed table uses a different scale (0..13)
but the relative ordering is the same.

The session's earlier confusion about whether `::` and `:!:` were
"new operators we were adding" or "operators Andrew already had"
is resolved here: they are Andrew's, in his `.sc` self-host.  The
bootstrap `.sno` source he provided didn't have them, but the
self-host source — his final vision — did.

### What we change vs. Andrew's `.sc` self-host

The `.sc` self-host operator table (snocone.sc lines 32–60) is
the canonical Koenig design — what he wrote when he could
implement Snocone in itself.  This goal adopts it almost
verbatim.  Three changes for Lon's space-as-concat restoration:

1. **Drop `||` (Andrew `.sc` line 37).**  Andrew lowered `||` to
   `(...,...)` SPITBOL alt-eval at the binfo emission site
   (note `binfo('',4,4,0,0,1)` — empty `out` field, `fn=1`).
   We remove `||` from the surface and require the user to write
   the SPITBOL `(e1, e2, e3)` form directly.  Same lowering.
2. **Drop `&&` (Andrew `.sc` line 38).**  Andrew lowered `&&` to
   `' '` (space) at emit-time (`binfo(' ',5,5,4,4)`).  We remove
   `&&` from the surface and require the user to write the space
   directly.  The lexer emits a synthetic CONCAT token at the
   appropriate boundaries, lifting space from "whitespace, ignored"
   to "binary operator at SPITBOL priority 4."
3. **Drop `%` (Andrew `.sc` line 57).**  Andrew lowered `%` to
   `REMDR()`.  We remove `%` from the surface and reserve it as
   a user-OPSYN slot.  Programs needing remainder write
   `REMDR(a, b)` directly.

Plus two surface tightenings that don't change semantics:

4. **`for (init, test, step)` → `for (init; test; step)`.**
   Andrew's `.sc` uses commas; we switch to semicolons because
   `,` is now the alternative-eval separator inside parens.
   Frees `,` exclusively for value-lists.
5. **`go to label` → `goto label`.**  Andrew's bootstrap (`.sno`)
   uses two-word `go to`; his `.sc` self-host doesn't have a
   goto statement at all (his `dostmt` doesn't emit one — labels
   exist but only as branch targets via SPITBOL `:S(...)/F(...)`).
   We add single-keyword `goto` because a structured language
   still needs an escape hatch.

Plus a precedence renumbering (no semantic change):

6. **All operator priorities renumbered to the SPITBOL 0–13
   scale** (manual Ch.15 pp.181–183).  Andrew's `.sc` uses a
   0–10 scale; the relative ordering is identical except that
   Andrew's `^` has `lp=9, rp=10` (right-associative encoded as
   asymmetric Pratt priorities).  Bison handles right-
   associativity declaratively (`%right`), so we use SPITBOL's
   single priority 11 right-associative for `^`/`!`/`**`.  Result
   is byte-identical for any expression Andrew's `.sc` parses.

What Andrew's `.sc` had that we **did not change**:

- All 23 surviving binary operators (`=` `?` `|` `>` `<` `>=`
  `<=` `==` `!=` `::` `:!:` `:>:` `:<:` `:>=:` `:<=:` `:==:`
  `:!=:` `+` `-` `/` `*` `^` `.` `$`).
- All 9 unary operators (`@` `~` `?` `&` `+` `-` `*` `$` `.`).
- The `::` for IDENT and `:!:` for DIFFER spellings —
  **Andrew's choice** (`.sc` lines 45–46), not a Lon invention.
  Question Q12 from session #3 closes here: those are the
  spellings.
- C-style structured control flow (`if`/`else`/`while`/`do`/
  `for`/`function`/`return`/`{`/`}`/`;`).
- The `name :` label syntax.
- The `// to EOL` comment syntax.
- `do/while` (no `do/until` in Andrew — we add).
- The `f(args)` zero-space call vs. `f (expr)` space-separated
  concat distinction.

What we **add** that Andrew's `.sc` does not have:

7. **`switch (e) { case v1: … case v2: … default: … }`** — the
   `.sc` has no switch.  We add it; lowers to a chain of
   `IDENT(tmp, vN) :S(cN)` tests.
8. **`do {…} until (cond);`** — Andrew has only `do/while`.  We
   add `do/until` as the natural failure-driven companion;
   lowers to `:F(top)`.
9. **`break;` and `continue;`** (form pending Q13) — Andrew has
   neither.  Experimental.
10. **`,` (comma) as alternative-evaluation separator inside
    parens** — already a SPITBOL extension (Manual Ch.15
    footnote: `A = (LT(I,J) I, GT(I,J) J, "Same")`).  Andrew's
    `.sc` has comma only inside `f(a,b)` arg lists; we extend
    its use to alt-eval at SPITBOL priority -1 (below
    everything), unparenthesised at top level it's a syntax
    error.

Net effect: **Snocone is Andrew's `.sc` self-host operator set
minus three (`&&`, `||`, `%`), plus three structured constructs
(`switch`, `do/until`, `break`/`continue`), plus alt-eval comma,
implemented via Flex+Bison instead of hand-rolled SNOBOL4
patterns, with conditions remaining SPITBOL backtracking
expressions exactly as Andrew intended.**

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
| `IDENT()` `DIFFER()` (identity sugar — `::` `:!:` from Andrew's `.sc` lines 45–46) | already SPITBOL primitives; emit functional form |

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
grammar accepts them.  Identity comparison (`::` `:!:`) is new
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

### Q5. `do { … } while (cond);` — C-aligned (do/until removed)

`do/while` supported.  **`do/until` removed per Lon directive session
2026-04-30 #12** — Snocone follows C's loop forms exactly: `while` and
`do/while` only.  The `until` keyword is no longer in the lexer's
KW_TABLE; `do { … } until (…)` is a syntax error.

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

### Q10. Language name — RESOLVED to "Snocone" (session #5)

Lon session #1: "We will do Snocone different from Andrew Koenig.
We might later find a better name."

Lon session #3: "The new name would be funny if it was SNOBOL6
since all that was bad with SNOBOL4 as the line by line thing
and missing structured control.  And SNOBOL5 already exists."

Lon session #4: "The name is not now SNOBOL6 nor will it likely
be.  We just have ideas is all."

Lon session #5: "Q10: Snocone."

**Decision:** the language is called **Snocone**.  This is
Andrew's name preserved — fitting since the language is
Andrew's `.sc` self-host vision plus Lon's space restoration,
not a new design.  Repo/build name `snocone` already matches.
No rename happens.

### Q11. Rename source tree — N/A (session #5)

Lon session #5: "Q11: N/A."

The language name is Snocone (Q10), the repo/build name is
already `snocone`, the file extension `.sc` matches Andrew's
own choice.  Nothing to rename.  This question is closed
permanently.

### Q12. Identity-op spelling — RESOLVED to `::` and `:!:` (sessions #4 + #5)

Andrew Koenig's `.sc` self-host source already defines them at
lines 45–46:

```snocone
bconv['::']  = binfo('IDENT', 6, 6, 0, 0, 1)
bconv[':!:'] = binfo('DIFFER', 6, 6, 0, 0, 1)
```

These are **Andrew's choices**, in his canonical self-host
source.  We adopt them verbatim.

Lon session #5: "Q12: use `::` and `:!:`" — confirms.

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

## LS-1 Lexer specification

The Snocone lexer is a Flex source `src/frontend/snocone/snocone.l`
(replacing today's hand-written `snocone_lex.c`).  It has one job
that is non-trivial: deciding when whitespace is a CONCAT
operator and when it is just whitespace.  Everything else is
ordinary lexing.

### 1. Token set

The lexer emits these token kinds.  Tokens marked **NEW** do not
exist in today's `snocone_lex.c` (which is a sufficient pre-LS-3
inventory).

#### Literals and identifiers

| Token         | Matches                                              |
|---------------|------------------------------------------------------|
| `INTEGER`     | `[0-9]+` not followed by `.` or `[eE]`               |
| `REAL`        | `[0-9]+ \. [0-9]* ([eE][+-]?[0-9]+)?` or `[0-9]+ [eE][+-]?[0-9]+` or `\. [0-9]+ ([eE][+-]?[0-9]+)?` |
| `STRING`      | `'…'` or `"…"` — embedded quote of the other kind allowed; `\` is **not** an escape (SNOBOL4 strings are literal — to embed the same quote, use the other quote form, or use `CHAR(39)` etc.) |
| `IDENT`       | `[A-Za-z_][A-Za-z0-9_]*` — Andrew's `.sc` uses `_` for compound names (`cl_type`, `or_binfo`).  Today's lexer matches this rule.  SNOBOL4 source-style names with `.` (`cl.type`, `or.binfo`) are NOT identifiers in Snocone — they'd lex as `IDENT(cl) PERIOD IDENT(type)`. |
| `KEYWORD_NAME` **NEW** | `& IDENT` with **zero whitespace** between (`&FULLSCAN`, `&UCASE`, `&ANCHOR`).  Single token. |

The case-sensitivity rule from RULES.md (Snocone keeps the byte
sequence the user wrote) applies — no folding at lex time.

#### Operators (priority shown for grammar reference; lexer just emits)

| Token             | Matches      | Pri | Notes                              |
|-------------------|--------------|----:|------------------------------------|
| `ASSIGN`          | `=`          | 0   |                                    |
| `QUESTION`        | `?`          | 1   | also unary                         |
| `PIPE`            | `\|`         | 3   |                                    |
| `CONCAT` **NEW**  | (synthesized — never a literal char) | 4 | emitted by the prev/next-token rule, not by direct character match |
| `STR_EQ`          | `:==:`       | 6   | LEQ                                |
| `STR_NE`          | `:!=:`       | 6   | LNE                                |
| `STR_LT`          | `:<:`        | 6   | LLT                                |
| `STR_GT`          | `:>:`        | 6   | LGT                                |
| `STR_LE`          | `:<=:`       | 6   | LLE                                |
| `STR_GE`          | `:>=:`       | 6   | LGE                                |
| `STR_IDENT`       | `::`         | 6   | IDENT — Andrew `.sc` line 45       |
| `STR_DIFFER`      | `:!:`        | 6   | DIFFER — Andrew `.sc` line 46      |
| `EQ`              | `==`         | 6   | EQ                                 |
| `NE`              | `!=`         | 6   | NE                                 |
| `LE`              | `<=`         | 6   | LE                                 |
| `GE`              | `>=`         | 6   | GE                                 |
| `LT`              | `<`          | 6   | LT                                 |
| `GT`              | `>`          | 6   | GT                                 |
| `PLUS`            | `+`          | 6   | also unary                         |
| `MINUS`           | `-`          | 6   | also unary                         |
| `SLASH`           | `/`          | 8   |                                    |
| `STAR`            | `*`          | 9   | also unary                         |
| `CARET`           | `^` or `**`  | 11  | `**` is Andrew/SPITBOL synonym for `^` |
| `BANG_EXPONENT` **NEW** | `!`     | 11  | SPITBOL synonym for `^` (MUST disambiguate from leading-`!` of `!=`) |
| `PERIOD`          | `.`          | 12  | also unary                         |
| `DOLLAR`          | `$`          | 12  | also unary                         |
| `AT`              | `@`          |  —  | unary only (binary `@` is OPSYN slot pri 5) |
| `TILDE`           | `~`          |  —  | unary only (binary `~` is OPSYN slot pri 13) |
| `AMPERSAND`       | `&`          |  —  | unary only — but **see KEYWORD_NAME**: `&IDENT` no-whitespace is one token |
| `PERCENT` **NEW** | `%`          |  —  | unary OR binary OPSYN slot pri 10 — no built-in semantics; the parser hands it to OPSYN lookup |

**Removed** vs today's lexer: `OR` (was `||`), `CONCAT_AMP`
(was `&&`).  The lexer no longer recognizes these character
sequences as their own tokens — they become syntax errors via
the catch-all "unknown character" rule.

#### Compound-assign operators

Today's lexer has `+=` `-=` `*=` `/=` `%=` `^=` (SC pre-existing).
**Open question, not part of LS-1:** are these in scope for the
new Snocone or are they a Snocone-only sugar Andrew didn't have?
Andrew's `.sc` does not have compound-assigns.  We retain them in
the lexer for now; the grammar (LS-2) decides whether to accept
them as syntax or reject.  If accepted, lowering is the obvious
`a += b` → `a = a b` (concat for `+=`?  no — `a + b`); standard.

#### Punctuation

| Token         | Matches                                              |
|---------------|------------------------------------------------------|
| `LPAREN`      | `(`                                                  |
| `RPAREN`      | `)`                                                  |
| `LBRACE`      | `{`                                                  |
| `RBRACE`      | `}`                                                  |
| `LBRACKET`    | `[`                                                  |
| `RBRACKET`    | `]`                                                  |
| `COMMA`       | `,`                                                  |
| `SEMICOLON`   | `;`                                                  |
| `COLON`       | `:` — only emitted when **not** part of `:==:` `:!=:` `:<:` `:<=:` `:>:` `:>=:` `::` `:!:` (Flex longest-match handles this) |
| `IDENT_LPAREN_NOSP` **NEW** | `IDENT` immediately followed by `(` with **zero whitespace**.  Single token whose value is the identifier name; the `(` is consumed.  After the matching `RPAREN` of the call, prev-token bookkeeping treats it as `RPAREN_OF_CALL` for can-end-expr purposes. |

#### Keywords

The KW_TABLE must include (some are present today; some are
**NEW**; some are renamed):

`if`, `else`, `while`, `do`, `until` **NEW**, `for`, `switch` **NEW**,
`case` **NEW**, `default` **NEW**, `break`, `continue`, `goto`,
`return`, `freturn`, `nreturn`, `function` **RENAMED** (today's
lexer has `procedure` → rename to `function` since these forms
return a value — Lon session #7), `struct` (already present from
Andrew's `.sc`).

Removed from today's KW_TABLE: `then` (Andrew has no `then`;
today's lexer has it as a vestige — confirm during LS-3 that the
grammar doesn't depend on it; if so, remove).  Also remove: `go`,
`to` (already commented out).  Also remove: `procedure` (replaced
by `function`).

The lexer matches a leading-letter word against KW_TABLE; on hit
emits the keyword token, on miss emits `IDENT`.  Case-sensitive
match (RULES.md).

#### Trivia (whitespace and comments — never emitted as tokens)

| Trivia        | Matches                                              |
|---------------|------------------------------------------------------|
| line comment  | `// .* (?=\n|$)` — to end of line                    |
| block comment | `/\* … \*/`  — non-nesting, may span newlines        |
| whitespace    | `[ \t\n\r\f]+` — including newlines.  No `NEWLINE` token emitted. |
| line continuation `+` / `.` (SNOBOL4-style) | `^[+.]` at column 1 — already-existing behavior in today's lexer; preserve as transparent line-glue (mid-statement continuation) |

Important: today's lexer emits a `SNOCONE_NEWLINE` token.  In the
new design that token is **gone**.  Newlines are whitespace.  The
grammar (LS-2) will use `;` exclusively as the statement
terminator.

### 2. The previous-token state and CONCAT emission

This is the lexer's distinguishing feature: a synthetic CONCAT
token is emitted between two tokens A and B when A is value-
yielding-and-can-end-expr, B is value-yielding-and-can-start-expr,
and at least one whitespace character (space, tab, newline, line-
continuation `+`/`.`, comment) appears between them.

#### State variables (Flex extra data)

```c
typedef enum {
    PT_NONE,                  /* file start, after ; , ( [ { etc. */
    PT_VALUE,                 /* IDENT, INTEGER, REAL, STRING, KEYWORD_NAME, RPAREN_of_expr, RBRACKET, RPAREN_of_call */
    PT_BINOP,                 /* any binary operator just emitted (= ? | concat-yet-to-fire * + - etc.) */
    PT_UNARY_PREFIX,          /* a unary prefix op just emitted, expecting an operand */
    PT_OPEN,                  /* ( or [ or { just emitted (nothing yet inside) */
    PT_KW_BLOCK_OPENER,       /* if/while/for/switch/do/until/case keyword just emitted, expecting ( or { or expr */
    PT_KW_LOOPCTRL,           /* break/continue/goto/return/freturn/nreturn just emitted */
    PT_LABEL_COLON_PENDING,   /* IDENT followed by exactly `:` — could be label_name : OR (in expr context) the goto-field marker */
} PrevTokenClass;

typedef struct {
    PrevTokenClass  prev;
    int             whitespace_seen;  /* >0 if any whitespace between prev token and current */
    int             paren_depth;       /* tracks ( [ { nesting */
    int             call_paren_depth;  /* tracks call-style ( specifically — see below */
    /* call_paren_stack: each entry = depth-at-which-the-call-LPAREN-opened.
     * On RPAREN, if paren_depth+1 was a call entry, set prev=PT_VALUE (RPAREN_of_call). */
} LexerState;
```

#### Can-end-expr (sources of CONCAT on the LEFT side)

`PT_VALUE` is the can-end-expr class.  Specifically the token
just emitted was one of:

- `IDENT` — bare identifier (variable reference, function name)
- `INTEGER`, `REAL`, `STRING`
- `KEYWORD_NAME` (`&FULLSCAN` etc.)
- `RPAREN` — closing a parenthesised sub-expression OR closing a call's arg list
- `RBRACKET` — closing a subscript
- `RBRACE` of a block-expression — none in the language today; reserved

#### Can-start-expr (sources of CONCAT on the RIGHT side)

A token-class is can-start-expr if it could begin a new operand.

- `IDENT`, `INTEGER`, `REAL`, `STRING`, `KEYWORD_NAME`
- `LPAREN` — but **only** if it is NOT the call-form `(` (the
  call-form is consumed inside `IDENT_LPAREN_NOSP`)
- `LBRACKET` — subscripting — requires special handling because
  `a[0]` (no space) is a subscript, but `a [0]` (with space)
  must mean "concat a with `[0]`" — except `[0]` alone is not a
  legal expression in Snocone (no array literals), so `a [0]` is
  a syntax error, not a concat.  **For LS-1 we treat `[` as
  always part of subscript — i.e., `[` after a value-token is
  always subscript regardless of whitespace.**  This is a
  divergence from the strict space-as-concat rule but matches
  Andrew's `.sc` (which uses `list(*exp ..., blank ",")` — note
  `blank` permitted between `[` and content).
- Unary prefix operators: `*`, `&`, `~`, `@`, `.`, `$`, `+`, `-`, `?`

#### Tokens that block CONCAT (cannot start an expression)

These are can-end-expr tokens that the lexer must NOT emit
CONCAT after, even when they superficially look like values:

- `RPAREN` followed by binary op — no CONCAT (binary op consumes
  the value).  Example: `(a+b) * c` — the `*` is binary, not
  concat-then-unary.

These are can-start-expr tokens that the lexer must NOT emit
CONCAT before:

- A leading position in a top-level statement (`PT_NONE`,
  `PT_OPEN`, etc.) — first operand has no left side to concat to.

#### CONCAT emission rule

```
when about to emit token T:
    if prev == PT_VALUE
       and T is can-start-expr
       and whitespace_seen > 0:
        emit CONCAT first
    emit T
    update prev based on T
    whitespace_seen = 0
```

### 3. Special cases

#### 3.1 `f(args)` vs `f (expr)` — the zero-space rule

When the lexer matches `IDENT` and the very next character is
`(` with **zero whitespace** between, it emits the combined
token `IDENT_LPAREN_NOSP` (carrying the identifier name).

When `IDENT` is followed by whitespace and then `(`, it emits
`IDENT` then (after CONCAT injection) `LPAREN`.  The
parenthesised expression is concat'd to the identifier value.

Implementation: in Flex, the rule for `IDENT_LPAREN_NOSP` has
higher priority than the rule for plain `IDENT`.  The pattern is
literally `[A-Za-z_][A-Za-z0-9_.]*\(` — capturing the `(` as part
of the match — and the action emits the combined token, pushes
"call-LPAREN" on a stack so the matching `RPAREN` knows it's
closing a call.

#### 3.2 `&IDENT` — the keyword-name token

Same shape: `&[A-Za-z_][A-Za-z0-9_.]*` with no whitespace between
`&` and the identifier.  Emitted as `KEYWORD_NAME` carrying the
full sequence (e.g. `&FULLSCAN`).

If `& IDENT` (whitespace), the `&` becomes unary `AMPERSAND`,
followed by `IDENT` — almost certainly a syntax error, but we
emit two tokens and let the grammar complain.

#### 3.3 `:` after IDENT — label vs. goto-field colon

`name:` at statement start is a label.  `:` in the goto-field
position (`stmt :S(L) F(M)`) is a SPITBOL goto-field marker.

In Snocone we **do not have a goto-field** — the C-shaped
control flow uses `goto label;` instead.  So `:` is always a
label-suffix in our grammar.

The grammar (LS-2) handles the disambiguation: a leading
`IDENT COLON` at the statement-start position is a label; a
trailing `IDENT COLON` would be an error.  The lexer just emits
`COLON`; no special state.

#### 3.4 String literals — the SNOBOL4 rule, no escapes

A string starts with `'` or `"`.  Body is everything up to the
matching delimiter.  Backslash is NOT an escape character.  To
embed a quote, use the other delimiter (`"can't"` or `'a"b'`).
Newlines inside strings are NOT permitted (would have to be
multi-line continuation `+`/`.`).  Today's lexer already does
this; preserve.

#### 3.5 Multi-line continuation — `+` / `.` at column 1

SNOBOL4's continuation lines start with `+` or `.` at column 1.
This is a tokenizer-level concern: when the next physical line's
column 1 is `+` or `.`, the line is glued onto the previous one
and lex restarts mid-statement.  Today's lexer already handles
this via the `is_continuation()` predicate at lines 175–186.
Preserve verbatim.

For the new lexer's CONCAT rule: a continuation line counts as
whitespace between the two physical lines.  So:

```snocone
   x = 'foo'
+         'bar'
```

emits `IDENT(x) ASSIGN STRING('foo') CONCAT STRING('bar')`.
The continuation is transparent.

#### 3.6 Comments

Line and block comments are pure trivia.  They count as
whitespace for the CONCAT rule:

```snocone
   x = 'foo' /* hello */ 'bar'
```

emits `IDENT(x) ASSIGN STRING('foo') CONCAT STRING('bar')`.  The
comment is a whitespace gap — CONCAT fires across it.

### 4. What the lexer does NOT do

- No statement boundary detection — `;` is emitted as a token,
  not as an end-of-statement signal.  The grammar enforces
  statement structure.
- No precedence — the grammar's Bison `%left/%right` declarations
  handle precedence.  Lexer just emits one token per operator.
- No newline tokens — newlines are whitespace.  Today's
  `SNOCONE_NEWLINE` token is removed.
- No fold-case — case-sensitive byte-for-byte (RULES.md).
- No special handling of OPSYN slots — `%`, undefined-binary
  `&`, `@`, `#`, `~` are emitted as plain tokens; the grammar
  routes them via the OPSYN catch-all production.

### 5. Test corpus — expected token stream for every edge case

For each input source line below, the expected token stream is
shown in the comment.  This corpus is the LS-3 acceptance test —
the new lexer must produce exactly these streams.  CONCAT
appearances are highlighted with `« CONCAT »`.

```
// Test 1 — basic concat: two values separated by space
x y
// IDENT(x) « CONCAT » IDENT(y)

// Test 2 — call vs. concat-with-paren
f(x)
// IDENT_LPAREN_NOSP(f) IDENT(x) RPAREN
f (x)
// IDENT(f) « CONCAT » LPAREN IDENT(x) RPAREN

// Test 3 — keyword name vs. unary-amp
&FULLSCAN = 1;
// KEYWORD_NAME(&FULLSCAN) ASSIGN INTEGER(1) SEMICOLON
& FULLSCAN
// AMPERSAND IDENT(FULLSCAN)
//   (note: no CONCAT — AMPERSAND is unary prefix, prev is AMPERSAND
//    not a value-token, so no concat trigger)

// Test 4 — bare expression statement
EQ(x, 0) x = 1;
// IDENT_LPAREN_NOSP(EQ) IDENT(x) COMMA INTEGER(0) RPAREN
//   « CONCAT » IDENT(x) ASSIGN INTEGER(1) SEMICOLON
//   (note the CONCAT after the call's RPAREN — the call is a
//    value, "x" can-start-expr, whitespace between them)

// Test 5 — alt-eval (replaces ||)
A = (LT(I,J) I, GT(I,J) J, "Same");
// IDENT(A) ASSIGN LPAREN
//   IDENT_LPAREN_NOSP(LT) IDENT(I) COMMA IDENT(J) RPAREN « CONCAT » IDENT(I)
//   COMMA
//   IDENT_LPAREN_NOSP(GT) IDENT(I) COMMA IDENT(J) RPAREN « CONCAT » IDENT(J)
//   COMMA
//   STRING("Same")
//   RPAREN SEMICOLON

// Test 6 — backtracking-expression condition
if (x ? 'foo' = 'bar') doit();
// KW_IF LPAREN IDENT(x) QUESTION STRING('foo') ASSIGN STRING('bar') RPAREN
//   IDENT_LPAREN_NOSP(doit) RPAREN SEMICOLON

// Test 7 — string with embedded && (must NOT lex as CONCAT-AMP)
s = '&&';
// IDENT(s) ASSIGN STRING('&&') SEMICOLON

// Test 8 — string with embedded || (must NOT lex as OR)
s = '||';
// IDENT(s) ASSIGN STRING('||') SEMICOLON

// Test 9 — bare && in source is now a syntax error (gone from lexer)
x && y
// IDENT(x) AMPERSAND AMPERSAND IDENT(y)
//   (the & becomes two unary AMPERSAND tokens; grammar will reject —
//    no special "old && " token at all)

// Test 10 — bare || similarly
x || y
// IDENT(x) PIPE PIPE IDENT(y)
//   (the | becomes two PIPE tokens; grammar may accept as alternation
//    repeated, or reject — the lexer no longer recognizes ||)

// Test 11 — identity comparison ::  (Andrew's .sc spelling)
x :: y
// IDENT(x) STR_IDENT IDENT(y)

// Test 12 — DIFFER comparison :!:
x :!: y
// IDENT(x) STR_DIFFER IDENT(y)

// Test 13 — exponentiation synonyms
a ^ b
// IDENT(a) CARET IDENT(b)
a ** b
// IDENT(a) CARET IDENT(b)
a ! b
// IDENT(a) BANG_EXPONENT IDENT(b)

// Test 14 — % is not modulo, just an OPSYN slot character
x % y
// IDENT(x) PERCENT IDENT(y)
//   (the grammar will route this to OPSYN lookup; if no OPSYN
//    is defined for %, the parser/runtime raises an error)

// Test 15 — line continuation with +
x = 'foo'
+      'bar'
// IDENT(x) ASSIGN STRING('foo') CONCAT STRING('bar')
//   (the column-1 + on the second line is treated as whitespace
//    glue; CONCAT fires across the line break)

// Test 16 — block comment between values triggers CONCAT
x /* hi */ y
// IDENT(x) « CONCAT » IDENT(y)

// Test 17 — line comment
x = y;  // a comment
z = w;
// IDENT(x) ASSIGN IDENT(y) SEMICOLON IDENT(z) ASSIGN IDENT(w) SEMICOLON

// Test 18 — keywords vs. identifiers
if a then b
// KW_IF IDENT(a) IDENT(then) IDENT(b)
//   (after LS-3, "then" is removed from KW_TABLE → it's an IDENT;
//    the grammar will reject "if a then b" because the `if` body
//    must be `(expr) stmt` — no `then` keyword)
//   Actually with CONCAT this lexes:
// KW_IF « CONCAT-NO! » LPAREN-MISSING — see below

// Test 18b — corrected: keyword positions don't get prev=PT_VALUE
if (a) b
// KW_IF LPAREN IDENT(a) RPAREN « CONCAT » IDENT(b)
//   Wait — should there be CONCAT between RPAREN-of-if-cond and the body IDENT(b)?
//   YES, the lexer doesn't know that (a) was an `if` cond — it just sees
//   RPAREN followed by IDENT.  The CONCAT fires.  The grammar then must
//   have an `if-statement` production that consumes
//     KW_IF LPAREN expr RPAREN stmt
//   and the CONCAT in the token stream after the RPAREN is silently
//   absorbed because the next token-kind it sees is a stmt-starting
//   IDENT, not a binary-op continuation.  Need to verify: does Bison
//   reject CONCAT in a stmt-starting position?  Resolve in LS-2.

// Test 19 — labels
top: x = 1;
// IDENT(top) COLON IDENT(x) ASSIGN INTEGER(1) SEMICOLON

// Test 20 — goto
goto top;
// KW_GOTO IDENT(top) SEMICOLON

// Test 21 — break with optional label (Q13 placeholder)
break loop_done;
// KW_BREAK IDENT(loop_done) SEMICOLON
break;
// KW_BREAK SEMICOLON

// Test 22 — switch
switch (x) { case 1: a = 1; case 2: a = 2; default: a = 3; }
// KW_SWITCH LPAREN IDENT(x) RPAREN LBRACE
//   KW_CASE INTEGER(1) COLON IDENT(a) ASSIGN INTEGER(1) SEMICOLON
//   KW_CASE INTEGER(2) COLON IDENT(a) ASSIGN INTEGER(2) SEMICOLON
//   KW_DEFAULT COLON IDENT(a) ASSIGN INTEGER(3) SEMICOLON
//   RBRACE

// Test 23 — do/until
do { x = x + 1; } until (GT(x, 10));
// KW_DO LBRACE IDENT(x) ASSIGN IDENT(x) PLUS INTEGER(1) SEMICOLON RBRACE
//   KW_UNTIL LPAREN IDENT_LPAREN_NOSP(GT) IDENT(x) COMMA INTEGER(10) RPAREN
//   RPAREN SEMICOLON

// Test 24 — subscripting (call rule applies — `[` after value is subscript)
a[0]
// IDENT(a) LBRACKET INTEGER(0) RBRACKET
a [0]
// IDENT(a) LBRACKET INTEGER(0) RBRACKET
//   (no CONCAT — `[` is always subscript after a value, regardless of space)

// Test 25 — three-way mix of concat, call, subscript
A[i] f(j) "x"
// IDENT(A) LBRACKET IDENT(i) RBRACKET « CONCAT »
//   IDENT_LPAREN_NOSP(f) IDENT(j) RPAREN « CONCAT »
//   STRING("x")

// Test 26 — pattern with dot-binding (Andrew's .)
'foo' . target
// STRING('foo') « CONCAT » PERIOD IDENT(target)
//   Wait — `.` is binary at pri 12 in pattern context, AND unary
//   "name-of" at unary priority outside pattern context.  The lexer
//   doesn't know the context; it always emits PERIOD.  The grammar
//   resolves binary-vs-unary via Bison's %prec rules.
//   The CONCAT here is wrong if `.` is binary.  Resolve: look at
//   prev-token before emitting CONCAT — if prev is PT_VALUE and the
//   next token is a known-binary operator (like PERIOD when it appears
//   after a value), DON'T emit CONCAT.
//   Refine: see "CONCAT with following unary/binary ambiguity" below.

// Test 27 — nested call
f(g(x))
// IDENT_LPAREN_NOSP(f) IDENT_LPAREN_NOSP(g) IDENT(x) RPAREN RPAREN

// Test 28 — empty statement
;
// SEMICOLON

// Test 29 — empty block
{ }
// LBRACE RBRACE

// Test 30 — comma at top level (must be syntax error per grammar)
a, b
// IDENT(a) COMMA IDENT(b)
//   (the lexer emits; the grammar rejects unparenthesised comma at top
//    level. Inside `(...)` the same tokens become alt-eval.)
```

### 6. Open lexer-design issues to resolve in LS-2/LS-3

#### 6.1 CONCAT-vs-binary-operator ambiguity (Test 26)

The naive CONCAT rule emits CONCAT whenever PT_VALUE is followed
by something can-start-expr.  But `.` `$` `+` `-` `*` `?` are all
**both unary prefix AND binary**.  Example:

```
x . y         ← Andrew binary `.` → conditional-assign in pattern
x .y          ← unary `.` (name-of) on y, with concat from x?
x   . y       ← same as x . y (whitespace doesn't change anything)
```

Andrew's `.sc` resolves this contextually: `.` is binary unless
the preceding context is unary-expecting (e.g. just after a binary
op or after `(`).  In our grammar, we use Bison precedence to do
the same — so the lexer must NOT emit CONCAT before tokens that
could be binary operators.

**Refined rule:** the lexer emits CONCAT only before tokens that
can ONLY start an expression — IDENT, INTEGER, REAL, STRING,
KEYWORD_NAME, LPAREN-not-call, and the strict unary-only operators
`~`, `@`.  Before the dual-role tokens `.`, `$`, `+`, `-`, `*`,
`?`, `&`, the lexer does NOT inject CONCAT — those tokens are
left for the grammar to interpret as binary or unary based on
production rules.

This means `x y` is concat (`y` is IDENT, can-only-start-expr) but
`x . y` is binary `.` (no CONCAT before PERIOD).  The user gets
the SPITBOL semantics for free.

**Note:** Andrew's `.sc` self-host at lines 658–688 has the same
distinction — `unaryop = ANY("+-*&@~?.$")` is recognized only in
operand position, while `binaryop = ANY("+-*/<>=^.$?|%")` is
recognized only in binary position.  The Pratt parser's role-by-
position is what we replace with Bison precedence + explicit
CONCAT emission.

#### 6.2 What about the unary-only `~` and `@`?

`~` and `@` are unary-only (binary slots are OPSYN-reservable but
empty by default).  If the grammar accepts them as binary
(via OPSYN catch-all), the Test 26-style ambiguity also applies.

**Decision (default):** treat `~` and `@` exactly like `.`/`$`/etc.
— no CONCAT before them.  This matches their dual-role potential.

#### 6.3 `?` in unary vs binary

Andrew/SPITBOL `?` is binary (pattern-match) at priority 1.
Andrew also allows `?` as a unary "interrogation" operator
(returns null if operand succeeds — SPITBOL Manual p.181).

Same handling: no CONCAT before `?`.  The grammar disambiguates.

#### 6.4 Compound assigns `+=` `-=` `*=` `/=` `^=` `%=`

Today's lexer recognizes them.  Andrew's `.sc` does not.  **Open
question for LS-2:** keep them as Snocone-only sugar or remove?
For LS-1 we keep them in the lexer; LS-2 grammar decides.

If `%=` is kept, then `%` outside `%=` is OPSYN-only; if `%=` is
removed (since `%` has no built-in semantic), then dropping `%=`
is consistent.  Default placeholder: drop all compound-assigns
to stay aligned with Andrew.  Revisit if anyone misses them.

### 7. Acceptance for LS-3

The new Flex source must produce token streams identical to the
expected streams in §5 for every test.  An automated runner
script (`scripts/test_smoke_snocone_lex.sh`) compares actual
output (printed via the existing `snocone_token_kind_name()`
helper) against the expected.  Test corpus lives at
`tests/snocone/lex/*.in` with companion `*.expect.tokens` files.

---

## Steps

> Convention: each step closes with a single commit (or back-to-back
> commits if `one4all`+`corpus` both touched), gates green where
> required, and the next-step pointer in `PLAN.md` updated.

### LS-0 ✅ — Read SPITBOL manual + Andrew's three sources & extract canonical operator set (DONE)

- [x] LS-0.a — Read SPITBOL Manual Ch.15 "Operators" (printed pp.181-183).
- [x] LS-0.b — Extract unary table, binary table, undefined-op table,
      and SPITBOL extensions list verbatim into this Goal file.
- [x] LS-0.c — Extract Andrew's `bconv[]` table from `snocone.sno`
      bootstrap (lines 600–627) and from `snocone.sc` self-host
      (lines 32–60).  Identify the two extra operators (`::` for
      `IDENT()` and `:!:` for `DIFFER()`) that the self-host adds.
      Adopt the **`.sc` self-host as canonical Andrew source**.
- [x] LS-0.d — Identify every change vs Andrew's `.sc` self-host:
      drop `&&` (replaced by SPACE), drop `||` (replaced by SPITBOL
      alt-eval `(,)`), drop `%` (reserved as user OPSYN slot),
      switch `for(,,)` separator from `,` to `;`, add single-keyword
      `goto`.  Add `switch`/`case`, `do/until`, `break`/`continue`.
- [x] LS-0.e — Resolve open design questions Q1–Q12 (see above).
      Q12 (identity-op spelling) closed by reading Andrew's `.sc`:
      `::` and `:!:` are his choices, we adopt verbatim.  Q10
      (language name) re-opened by Lon session #4 and remains open
      with no commitment.  Q11 (rename) moot until Q10 lands.
      Q13 (break/continue form) still pending Lon's pick.

### LS-1 ✏️ — Lexer design specification (drafted, awaiting review)

- [x] LS-1.a — Lexer state machine written.  See top-level
      `## LS-1 Lexer specification` section §§ 1–4 for the token
      set, previous-token state model, CONCAT emission rule, and
      every special-case rule.
- [x] LS-1.b — Test corpus written.  See § 5 — 30 tests covering
      every edge case (`&&` in string, `f(x)` vs `f (x)`,
      `&FULLSCAN` vs `& FULLSCAN`, backtracking-condition in
      `if`, alt-eval `(,,)`, line-continuation `+`/`.`, comment
      between values, dual-role `.` `$` `+` `-` `*` `?`).
- [ ] LS-1.c — Lon reviews; revise until approved.
- [ ] LS-1.d — Open lexer-design issues in §6 resolved.  Three
      open: dual-role `.`/`$`/etc CONCAT-suppression rule (default
      placeholder: don't emit CONCAT before any token that could
      be binary), `~`/`@` handling (same), compound-assigns kept
      or dropped (default placeholder: drop, align with Andrew).
- [ ] No code yet.

### LS-2 — Grammar design specification

- [ ] LS-2.a — Write the complete Bison grammar skeleton in this
      Goal file: every non-terminal, every production, every
      precedence declaration, every action (in pseudocode that
      maps to the IR).
- [ ] LS-2.b — Show how every existing `.sc` construct lowers
      under the new grammar.  Specifically: every `if`/`while`/
      `for`/`do`/`switch`/`function` form in the corpus, every
      use of `&&`/`||`/`==`/`!=`/`<`/`<=`/`>`/`>=`/`%`/`:==:`/
      `:!=:`/`:>:`/`:<:`/`:>=:`/`:<=:` in the corpus.
- [ ] LS-2.c — Define the alternative-evaluation `(,,)` grammar
      production and its lowering for SPITBOL backend (pass-through)
      and non-SPITBOL backends (lowered to a chain of `:S(after)`
      branches).
- [ ] LS-2.d — Lon reviews; revise until approved.
- [ ] No code yet.

### LS-3 — Lexer implementation (Flex)

- [x] LS-3.a — `src/frontend/snocone/snocone.l` Flex source created (W{OP}W envelope pattern). one4all `02db637d`.
- [x] LS-3.b — `regenerate_parser_and_lexer_from_sources.sh` generates `snocone.lex.c`.
- [x] LS-3.c — LS-1.b 31-test acceptance corpus: 31/31 token streams match.
- [x] LS-3.d — Hand-written `snocone_lex.c` removed (moved to `archive/` in LS-4.k).
- [x] LS-3.e — Smoke gate green at LS-3 close (5/5).

**Design alignment:** the lexer follows `snobol4.l` lines 235-315 line-for-line — space envelops every binary operator via `{W}OP{W}` patterns; whitespace alone between two atoms lexes as `T_CONCAT`; unary forms of dual-role operators arrive bare and return `T_1*` tokens (arity-1 marker). Token names match `snobol4.tab.h` under the `T_<arity><charname>` scheme — `T_2EQUAL` (`=`), `T_2QUEST` (`?`), `T_2PIPE` (`|`), `T_2DOT` (`.`), `T_2DOLLAR` (`$`), etc., with matching `T_1*` unaries. The snobol4↔snocone name-equivalence invariant is preserved.

### LS-3.f — Lexer single-pass refactor (threaded-code FSM)

The session-#9 lexer accumulated tokens into a `ScTokenBuf` (two-pass design from LS-3.c standalone tests). One4all convention is single-pass Flex→Bison. After demonstrating that flex 2.6.4's NFA→DFA pass hangs at >180s on `{W}OP{W}` rules with comments folded into `{W}`, Lon directed a pivot to **threaded-code FSM**: one C function `sc_lex_next(LexCtx *ctx)` whose body is a graph of labelled `Label: [if (cond)] action; goto NEXT;` blocks. No `switch`/`for`/`while`/`do-while` in the FSM body. Comments-as-whitespace fall out for free via `S_LCOMMENT`/`S_BCOMMENT` sub-FSMs.

- [x] LS-3.f.1 — Threaded-code FSM lexer landed. `snocone.l`/`snocone.lex.c` deleted; `snocone_fsm.c` (~740 lines) added. LS-1.b 31/31 pass.
- [x] LS-3.f.2 — Two-pass machinery (`ScTokenBuf`, `snocone_lex2`, etc.) deleted. Header renamed `snocone_fsm.h` → public FSM API only.
- [x] LS-3.f.3 — Production gates remained green throughout.

### LS-4 — Grammar implementation (Bison)

All sub-rungs LANDED across sessions 2026-04-30 #3 through 2026-05-01 #6. Closed in dependency order; each one shipped its own side-channel parse-* gate. **Bison reports 0 shift/reduce and 0 reduce/reduce conflicts** at every rung.

- [x] LS-4.a — Skeleton `snocone.y`: atoms + arithmetic + paren-grouping + signed unary +/- + `;` stmts + top-level T_ASSIGNMENT split. Public entry `CODE_t *snocone_parse_program(const char *src, const char *filename)`. Token-namespace decoupling via `%code top` + `sc_kind_to_tok()` translation. **parse-a 35/35**.
- [x] LS-4.b — Comparison/identity tier `expr5`: 14 ops (`==`/`!=`/`<`/`<=`/`>`/`>=`, `:==:`/`:!=:`/`:<:`/`:>:`/`:<=:`/`:>=:`, `::`/`:!:`) lower to `E_FNC` named calls. T_FUNCTION call-form `EQ(2+2,4)`. **parse-b 119/119**.
- [x] LS-4.c — Pattern tiers: `expr1` match `?` → E_SCAN; `expr3` alternation `|` → E_ALT n-ary fold; `expr4` concat T_CONCAT → E_SEQ n-ary fold. Compound-assigns (`+=`/`-=`/`*=`/`/=`/`^=`) lower to clone-LHS pattern. `sc_clone_expr_simple` helper. **parse-c 66/66**.
- [x] LS-4.cn — Cosmetic rename: `snocone.y` → `snocone_parse.y`; `CODE_t` typedef alias of `Program` added; legacy `snocone_parse.c`/`.h` moved to `archive/`. Pure rename + typedef; semantics unchanged.
- [x] LS-4.d — Postfix subscript `a[i, j]` → E_IDX at new `expr15` tier. Left-recursive chaining: `a[i][j]` → `E_IDX(E_IDX(a,i), j)`; `a[i,j]` → single n-ary. **parse-d 79/79**.
- [x] LS-4.e — All remaining SPITBOL unary operators at `expr17` atoms tier: `*` E_DEFER, `.` E_NAME, `$` E_INDIRECT, `@` E_CAPT_CURSOR, `~` E_NOT, `?` E_INTERROGATE, `&` E_OPSYN, plus OPSYN-slot unaries `%`/`/`/`#`/`|`/`=` → E_OPSYN(op). **parse-e 71/71**.
- [x] LS-4.f — Control flow `if`/`else`/`while` (Lon's session-#11 decision: bare-name conds accepted as-is; warnings deferred to LS-4.w). Pascal/Algol balanced grammar `matched_stmt`/`unmatched_stmt`; emit-and-splice architecture (head reduces snapshot tail, body parses normally, finalize splices cond/labels). `opt_head_sep` absorbs spurious T_CONCAT after `)`. Synthetic labels `_Lend_NNNN`/`_Lelse_NNNN`/`_Ltop_NNNN`. **parse-f 118/118**.
- [x] LS-4.g — `do/while` and `for` (do/until removed per Lon directive — Snocone follows C exactly: `while` and `do/while` only). `do_body` non-terminal (brace-block only) resolves the T_WHILE-after-body ambiguity. **parse-g 95/95** (3 tests verify do/until is now a syntax error).
- [x] LS-4.h — `function`/`return`/`freturn`/`nreturn`. `func_head` at `matched_stmt` level. Function entry lowers to `DEFINE('NAME(args)') :(NAME_end)` then label `NAME` on body's first stmt then `NAME_end` pad. `return E;` → `name = E :(RETURN)`; `return;`/`freturn;`/`nreturn;` → bare gotos. Token rename pass: `T_KW_*` → `T_*` (Lon directive); `T_FUNCTION` (was call-form) renamed to `T_CALL`, `function` keyword takes `T_FUNCTION`; `E_FUNCTION` action label → `E_CALL`. **parse-h 85/85**.
- [x] LS-4.i.1 — `goto LABEL;` and `LABEL: stmt`. `label_decl` non-terminal eager-emits a label pad; LR(1) lookahead at T_COLON unambiguous. **parse-i (sub) 108/108**.
- [x] LS-4.i.2 — `break;`/`break LABEL;`/`continue;`/`continue LABEL;` per Lon's session-#2 Q13 → Option A (both forms). `LoopFrame` linked-list stack with eager label allocation. `for_lead` non-terminal moves pending labels to one-slot stash before `for`'s init parses. Pending-user-label tracking attaches stacked labels to loop frames. Lazy-emit `_Lcont_NNNN` pad only when body actually emits `continue`. Out-of-context `break;`/`continue;` calls `sc_error`. **parse-i +50 = 158/158**.
- [x] LS-4.i.3 — `switch (e) { case v1: S1; case v2: S2; default: SD; }` — Q6 modern no-fall-through (implicit break at end of each case). LR(1) lookahead at T_CASE/T_DEFAULT after stmt unambiguous. `SwitchHead` w/ disc/tmp/end/default labels + `cases[]` array. `cur_switch` field saved/restored for nested switches. Switch frames have `is_loop=0` so `break LABEL` from nested loop walks past them; continue-in-switch rejected. Stacked case labels suppress implicit break via tail-snapshot equality. **parse-i +45 = 203/203**.
- [x] LS-4.i.4 — Alt-eval `(a, b, c)` → `E_VLIST` (Q2-canonical replacement for Andrew's `||`). Three rule additions in `expr17` mirroring snobol4.y:194-196 byte-for-byte. Single-expr `(e)` grouping preserved (LR(1) disambiguates at T_RPAREN vs T_COMMA). Empty `()` → E_NUL. E_VLIST already in IR with downstream consumers in sm_lower/interp.c — pure grammar-surface addition. **parse-i +56 = 259/259**.
- [x] LS-4.i.5 — `struct NAME { f1, f2, ... }` (Andrew's `.sc` line 162 record-decl). Lowers to single bare-expr stmt `DATA('NAME(f1,f2,...)')`. `struct_field_list` left-recursive helper builds comma-joined string. End-to-end SPITBOL semantic verified: `DATA()` installs constructor + per-field accessors (each accessor doubling as L-value). No trailing `;`. Adjacent structs without separators parse cleanly. **parse-i +38 = 297/297**.
- [x] LS-4.j — `snocone_parse_program()` wired into `snocone_compile()` as production path. Smoke 5/5 confirms no legacy fallback active.
- [x] LS-4.k — Junk cleanup by **moving to archive, not deleting** (Lon's correction). `snocone_lower.{c,h}`, `snocone_control.{c,h}` moved from `src/frontend/snocone/` to `archive/`. `FRONTEND_SNOCONE` references only live `src/frontend/snocone/` files. Legacy synonym `function`→`procedure` reverted in archived lexer (no longer needed). One stray `#include "frontend/snocone/snocone_control.h"` in `src/driver/interp.c:26` removed in follow-up.
- [x] LS-4.l — **LANDED session 2026-05-01 #6.** Two fixes in `snocone_parse.y` close the 12 fence/match/semantic/trace × 3-mode FAILs.

      **Bug A — missing binary `.` and `$` operators** (parse errors in `fence`, `semantic`). `T_2DOT`/`T_2DOLLAR` were declared but had no rules using them; only the unary `T_1DOT`/`T_1DOLLAR` at expr17 were wired. Added new `expr12` tier between `expr11` (exponent) and `expr15` (subscript), mirroring snobol4.y:159-161:

          expr12 : expr12 T_2DOLLAR expr15  { E_CAPT_IMMED_ASGN }
                 | expr12 T_2DOT    expr15  { E_CAPT_COND_ASGN  }
                 | expr15

      Left-associative. `expr11` redirected through `expr12`.

      **Bug B — missing E_SCAN/E_SEQ split when committing a stmt** (runtime FAILs in `match`, `semantic`, `trace`). `sno4_stmt_commit_go` (snobol4.y:248-270) splits `E_SCAN(subj, pat)` and `E_SEQ(name, rest...)` out of `s->subject` into separate `s->subject`/`s->pattern` slots so the runtime's pattern-match engine fires. Snocone's `sc_append_stmt` and cond builders skipped this split — runtime then evaluated E_SCAN as a value (always succeeds), making `if (subj ? pat)` always take the success arm. Decisive isolated repro: `'xyz' ? ANY('aeiou')` succeeded in Snocone but correctly failed in SPITBOL oracle and in scrip's snobol4 mode.

      Fix: helper `sc_split_subject_pattern(EXPR_t **subj_io, EXPR_t **pat_io)` called from `sc_append_stmt` (after the E_ASSIGN split, so `subj ? pat = repl` correctly ends up with subject/pattern/replacement separately), `sc_make_cond_fail_stmt` (if/while), and `sc_make_cond_succ_stmt` (do/while). Replacement-side E_SCAN is left unchanged — `result = subj ? pat` evaluates E_SCAN as a value (the matched substring).

      **Beauty 3-mode 30/12/3 → 42/0/3** — LS-4.l acceptance MET. All gates green: smoke snocone 5/5, smoke snobol4 7/7 (no regression), broker 49/0, beauty 42/0/3, parse-a..i 965/965 (no regression), NEW **parse-j 90/90**. Combined parse-a..j **1055/1055**. Bison conflicts 0/0. Files: `snocone_parse.y` (~100 lines added), regenerated `snocone_parse.tab.{c,h}`, NEW `test/frontend/snocone/test_snocone_parse_j.c`, NEW `scripts/test_smoke_snocone_parse_j.sh`. one4all `a90c9edf`.

      **LS-4 closes** — the new Snocone front-end is the only Snocone front-end, byte-equivalent to SPITBOL on the full 14-subsystem beauty suite across `--ir-run`, `--sm-run`, `--jit-run`.

- [ ] LS-4.w — Condition-never-fails warning pass (deferred, low priority).
      At lowering time, inspect the condition expression of every `if`,
      `while`, `do/while`, `for`-test, and `case` tag.
      If the condition is a bare `E_VAR` or `E_KEYWORD` node (no operator,
      no pattern match, no function call) emit a compiler warning:
        `warning: condition 'c' is a variable reference and can never fail`
      (because a bound SNOBOL4 name always succeeds with its value).
      Function calls are NOT warned — `if (func())` is legitimate since
      the called function may return failure.  Operator expressions
      (`GT(x,0)`, `x ? pat`, `s :: t`, etc.) are NOT warned.
      Implementation: small `sc_cond_warn(Expr *e, const char *loc)`
      helper called from each cond-lowering site that reduces to a
      single E_VAR/E_KEYWORD check.  No new test gate required.

### LS-5 — Corpus migration script

- [x] LS-5.a — `scripts/util_migrate_snocone_to_lang_space.py` (~700 lines). Rewrites `&&` → space; `||` → `(a, b)` n-ary alt-eval; `go to NAME` → `goto NAME`. Strings and comments preserved verbatim. Single `|` (pattern alternation) untouched. `%` modulo NOT handled (regex can't safely distinguish binary from unary; corpus survey confirmed zero binary-`%` uses). Two-stage algorithm: whole-source `||` rewrite via paren-depth-aware tokenizer (necessary because operands span literal boundaries); then per-code-span `&&`/`go to` sweep. 24 inline unit tests, idempotent. one4all `5bcc7412`.
- [x] LS-5.b — Dry-runs on `tree.sc`, `roman.sc`, `treebank-array.sc`, `sc8_strings.sc` confirmed clean rewrites; surfaced one pre-existing edge case (`hello_literals.sc` — SNOBOL4-surface conventions outside the script's mandate).
- [x] LS-5.c — Applied to all 240 `.sc`; **69 files changed** (68 auto + 1 hand-fix `hello_literals.sc`: `#`→`//`, added `;`). Beauty 6/36/3 → 30/12/3 (24 tests recovered). corpus `a4aaf83`. Note: `sc8_strings.sc` `.ref` mismatch is pre-existing corpus-data drift, not migration-caused.
- [x] LS-5.d — **Session 2026-05-01 #7**: completed the LS-4.h `procedure` → `function` rename across the corpus and removed the lexer's backward-compat synonym. Companion script `scripts/util_migrate_snocone_procedure_to_function.py` (re-uses LS-5.a's `split_into_spans` helper for string/comment-aware rewriting; 7 inline self-tests; idempotent). **61 files changed, 297 replacements**. Plus 6 hand-fixes in `programs/snocone/corpus/`: removed `then` keyword from `sc4_control.sc` (4 lines) and `sc9_multiproc.sc` (3 lines) — `then` is no longer in KW_TABLE; removed erroneous `do` from `while (cond) do {…}` in `sc5_while.sc`, `sc6_for.sc`, `sc10_wordcount.sc` — `do` belongs in `do/while`, not `while`; rewrote `c = (a, b);` (alt-eval) to `c = a b;` (juxtaposition concat) in `sc8_strings.sc` — the original was written assuming the old `&&` concat; corrected stale `min(3,7)=7` to `min(3,7)=3` in `sc9_multiproc.ref` (verified against SPITBOL oracle: SPITBOL says `3`). One4all lexer change: removed `{ "procedure", T_FUNCTION }` from `snocone_lex.c` KW_TABLE (line 145). Bare `procedure` is now an IDENT — almost certainly a syntax error in any post-migration `.sc` file; LS-5.d's mass migration ensures no live `.sc` source is affected. **Effect on snocone/corpus directory: 5/10 → 10/10 PASS** under `--ir-run`. All four production gates remain green: smoke snocone 5/0, beauty 42/0/3, broker 49/0, smoke snobol4 7/0.

### LS-6 — Atomic landing

- [x] LS-6.a — The "single commit train" landed across the three
      preceding sessions in dependency order rather than in one
      atomic push: one4all `a90c9edf` (LS-4.l: lexer/grammar/build,
      session 2026-05-01 #6), corpus `a4aaf83` (LS-5.b/c: 69 `.sc`
      files migrated), .github `246b9c3` then `f01a813` then
      `cc84b8f` (LS-4.l close + goal-file compression). The
      train is whole; the atomic-push form is not how the work
      arrived. Recording reality, not rewriting history.
- [x] LS-6.b — **Verified green session 2026-05-01 #7**, on
      one4all `a90c9edf` + corpus `a4aaf83`:
      `test_smoke_snocone.sh` **PASS=5/0**,
      `test_beauty_snocone_all_modes.sh` **PASS=42 FAIL=0 SKIP=3**,
      `test_smoke_unified_broker.sh` **PASS=49 FAIL=0**.
      Bonus: `test_smoke_snobol4.sh` **PASS=7/0** (no regression
      on the shared SNOBOL4 frontend from the Snocone landing).
- [ ] LS-6.c — `beauty.sc` produces output byte-identical to its
      pre-migration `.ref` in all three Snocone modes. **Progress
      session 2026-05-01 #8: SB-6.D root cause identified and fixed
      (corpus only); two further grammar gaps in Snocone uncovered
      and one fixed. Third still open.**

      **SB-6.D — corpus fix.** Sessions #80/#81 framed this as a
      runtime "double-wrap" bug. It is not. The Snocone `Reduce` in
      `corpus/programs/snocone/demo/beauty/ShiftReduce.sc` had a
      faulty translation of SPITBOL's `:F(NRETURN)`:
      ```snocone
      n = EVAL(n);
      if (~DIFFER(n)) { nreturn; }   // doesn't catch EVAL failure
      ```
      Per SPITBOL Manual Ch.2 p.33, when EVAL fails the assignment
      is silently skipped and `n` keeps its prior EXPRESSION value;
      `DIFFER(EXPRESSION)` succeeds, `~DIFFER` fails, no nreturn,
      and `GE(n,1)` errors with "first arg not numeric". Verified
      runtime is innocent: ported the same broken if-form back to
      SNOBOL4 — **SPITBOL also errors with Error 109**. Fix:
      ```snocone
      if (~(t = EVAL(t))) { nreturn; }   // direct port of :F(NRETURN)
      ```
      `~` negates failure (Manual Ch.9 p.130); embedded `t = EVAL(t)`
      fails iff EVAL fails (RHS-fails-statement-fails rule). Tested
      against three cases (failing-expr / succeeding-expr / preserved-
      LHS) — matches SPITBOL `:F(NRETURN)` exactly. Same fix applied
      to both `t` and `n` parameters in `Reduce`. Stale comment block
      at lines 23-32 of ShiftReduce.sc that claimed "Snocone's
      `if (assignment)` does not propagate inner EVAL failure"
      corrected — that claim was either pre-LS-4.l grammar state or
      a flawed earlier probe; current Snocone correctly propagates
      embedded-assignment failure.

      **Grammar gap #1 (LANDED) — empty replacement RHS.**
      `beauty.sc::case.sc:22` uses statement-form `subj ? pat = ;`
      (match-replace with empty replacement) — also bare `x = ;`
      (assign null to x). Both are valid SPITBOL idioms; SPITBOL's
      `opt_repl` rule (snobol4.y:77) handles them via a dedicated
      `T_2EQUAL` no-RHS production yielding empty E_QLIT. Snocone's
      Bison grammar had only the binary `expr1 T_2EQUAL expr0` form,
      requiring a non-empty RHS, so `case.sc` failed to parse.
      Fix in `src/frontend/snocone/snocone_parse.y`: added second
      production
      ```
      expr0 : expr1 T_2EQUAL          { $$ = E_ASSIGN(lhs, '');  }
            | expr1 T_2EQUAL expr0    /* existing */
            | expr1                   /* fallback */
            ;
      ```
      Bison single-token lookahead distinguishes: if next token can
      start expr0 → shift (use binary form); else (T_SEMICOLON,
      T_RPAREN, etc.) → reduce to empty-RHS form. **Bison reports
      0 shift/reduce, 0 reduce/reduce conflicts.** This rule is
      faithful to SPITBOL's `opt_repl` semantics — empty RHS lowers
      to NULL (zero-length string) per Lon's session-#8 directive.

      **Grammar gap #2 (LANDED) — keyword-concat-keyword.**
      `case.sc:22` also uses `ANY(&UCASE   &LCASE)` — two keyword
      references concat'd via whitespace. The hand-written threaded-
      code lexer's `is_value_starter()` predicate (used by the
      CONCAT-injection trigger at S_DISPATCH) did not include `&`,
      so `KEYWORD_NAME` after a value-token with intervening
      whitespace failed to inject T_CONCAT and the parser saw two
      adjacent value tokens → syntax error. Fix in
      `src/frontend/snocone/snocone_lex.c`: added explicit CONCAT
      trigger for `&` followed by alpha (i.e. the start of a
      `&IDENT` keyword reference) when `had_ws && last_value`. The
      existing `S_OP_AMP` already had the same pattern for unary
      `&` operator; this just extends it to the `&IDENT` keyword
      dispatch path (line 252 of `snocone_lex.c`).

      **Grammar gap #3 (OPEN) — dense `if/else` with no whitespace
      separation between block-builders.** Discovered while running
      full beauty.sc end-to-end: `beauty.sc:284` and following lines
      use the dense one-liner form
      ```snocone
      if (DIFFER(x)) { OUTPUT='a'; } else { OUTPUT='b'; }
      ```
      which produces `snocone parse error: syntax error` regardless
      of whether `}` and `else` are space-separated. Confirmed
      pre-existing (reproduces against baseline `07d58f55` without
      any of session #8's fixes applied). Minimal repro:
      ```snocone
      ss_leaf = 'foo';
      if (DIFFER(ss_leaf)) { OUTPUT='a'; } else { OUTPUT='b'; }
      ```
      Probably an interaction between `T_RBRACE` followed by
      `T_ELSE` and the matched/unmatched `if` grammar in
      `snocone_parse.y` (LS-4.f territory — Pascal/Algol balanced
      grammar with `matched_stmt`/`unmatched_stmt`). NEXT SESSION:
      bisect to find the exact production that fails to fire and
      whether the fix is grammar-level (extra `opt_head_sep`-style
      consumer for stray T_CONCAT between `}` and `else`) or
      lexer-level (T_CONCAT erroneously injected between the two).

      **Verified green session 2026-05-01 #8** with all three
      session #8 fixes + SB-6.D corpus fix applied:
      `test_smoke_snocone.sh` 5/0, `test_beauty_snocone_all_modes.sh`
      42/0/3, `test_smoke_unified_broker.sh` 49/0,
      `test_smoke_snobol4.sh` 7/0, `test_gate_sn7_beauty_self_host.sh`
      51/0, `test_interp_broad_corpus_and_beauty.sh` 222/52
      (baseline unchanged — broad suite isn't sensitive to these
      fixes). **No regressions.** Beauty.sc end-to-end now compiles
      past `case.sc` (previously blocked at line 22) and is now
      blocked at `beauty.sc:284` on grammar gap #3 above. After #3
      lands, byte-identical comparison vs SPITBOL oracle on a small
      input is the next milestone for closing LS-6.c.

      **No `.ref` file** exists at `corpus/programs/snocone/demo/
      beauty/beauty.ref` yet — once gap #3 lands and beauty.sc runs
      end-to-end, generate via SPITBOL oracle on a representative
      input set and add to corpus.

      **Session 2026-05-01 #9 — gap #3 landed; T_CALL atomic +
      T_FUNCTION→T_DEFINE rename.** Three lexer/grammar fixes:
      (1) S_OP_EQ no longer requires `had_ws` — `OUTPUT='a'` (no
      spaces) now correctly emits T_ASSIGN instead of unary
      E_UN_EQUAL, allowing dense `if(){…}else{…}` one-liners to
      parse. (2) E_CALL redirects to E_IDENT when the matched range
      classifies as a keyword (e.g. `if(`, `while(`) so keywords
      retain their keyword tokens; the `(` is left for the next
      lexer call. (3) E_CALL also redirects to E_IDENT when the
      previous token is T_DEFINE, so `function name(` lexes as
      T_DEFINE T_IDENT T_LPAREN — definitions don't piggy-back on
      the call-form token.

      **Structural cleanup.** T_CALL now atomically consumes
      IDENT+`(`; the grammar form is `T_CALL exprlist T_RPAREN`
      (was `T_CALL T_LPAREN exprlist T_RPAREN`). T_FUNCTION renamed
      to T_DEFINE throughout (the keyword string `function` is
      unchanged). func_head reads `T_DEFINE T_IDENT T_LPAREN
      func_arglist opt_head_sep` (was `T_FUNCTION T_CALL T_LPAREN
      func_arglist`). T_CALL removed from sc_value_table (it is no
      longer a value-ender — semantically post-T_CALL is post-LPAREN
      inside the arg list, so `*` after `f(` correctly lexes as
      unary defer rather than binary multiplication). Added
      sc_payload_table + sc_kind_has_payload() predicate to
      distinguish "value-ender for CONCAT/binary decisions" from
      "carries text payload to parser thunk"; T_CALL is in the
      payload table (carries identifier name) but not the value
      table. Parser thunk uses sc_kind_has_payload() for the
      strdup-into-yylval decision.

      **Result.** beauty.sc now parses end-to-end with no syntax
      errors (previously blocked at line 22, then line 284, then
      line 70). Remaining failures are runtime-level (undefined
      functions because library .sc files like Gen.sc, Qize.sc,
      ReadWrite.sc aren't loaded by the driver), not parse-level.
      Gates green at commit f89dacad: `test_smoke_snocone.sh` 5/0,
      `test_beauty_snocone_all_modes.sh` 42/0/3,
      `test_smoke_unified_broker.sh` 49/0, `test_smoke_snobol4.sh`
      7/0, `test_gate_sn7_beauty_self_host.sh` 51/0. No
      regressions. NEXT SESSION: wire library-loading for beauty.sc
      so Gen.sc/Qize.sc/etc. are pulled in, then generate beauty.ref
      via SPITBOL oracle for byte-identical comparison.

### LS-7 — Documentation pass — LANDED session 2026-05-01 #7

- [x] LS-7.a — Created new `## Snocone language facts` section in
      `RULES.md` (between `## NRETURN functions` and `## Test gate
      before every commit`). Covers: no `&&` / no `||` / no
      built-in `%`; juxtaposition concat; alt-eval `(e1, e2, e3)`
      replaces `||`; `f(x)` zero-space rule; conditions are SPITBOL
      backtracking expressions; `;` statement boundary, newlines
      are whitespace; bare expressions may fail silently;
      `do/until` removed (Lon directive 2026-04-30 #12); identity
      comparisons `::` / `:!:` are Andrew's choices; SPITBOL
      functional-superset hard invariant.
- [x] LS-7.b — Updated `GOAL-SNOCONE-BEAUTY.md` "Snocone language
      facts" section (was "session #66", now "updated session
      2026-05-01 #7"). Operator table now strikes through removed
      `&&` / `||` / `%` rows, adds explicit `(whitespace)` row for
      space-as-concat, adds explicit notes that the front-end is
      the post-LS-4 Flex+Bison front-end. Section re-written for
      added constructs (`switch`, `break`/`continue`, `goto`,
      alt-eval, `struct`), `function` keyword (was `procedure`),
      conditions-as-backtracking-expressions, statement-terminator
      requirement, and the SPITBOL-superset invariant. Added
      Manual Ch.15 Operators (pp.181–183) and the alt-eval
      footnote to the SPITBOL-manual reference list.
- [x] LS-7.c — Added new `## Snocone front-end` section to
      `REPO-one4all.md` (between `## Key source paths` and
      `## Silly SNOBOL4 — cherry-picks from one4all`). Covers:
      LS-6 status (42/0/3 byte-equivalent across three modes);
      one-sentence goal statement; functional-superset invariant;
      key source paths table for `src/frontend/snocone/`; lexer
      shape (threaded-code FSM, T_CONCAT injection); grammar shape
      (Bison, 0/0 conflicts, SPITBOL Ch.15 priorities, conditions
      are backtracking expressions); build path through
      `regenerate_parser_and_lexer_from_sources.sh`; smoke gate
      commands and expected counts; SB-6.D dependency note.
- [x] LS-7.d — Created `corpus/programs/snocone/LANGUAGE.md`.
      Single short doc for the next reader: one-sentence goal,
      explicit "what changed from Andrew's original" table, how
      concat works, how `f(x)` vs `f (x)` work, conditions are
      SPITBOL backtracking expressions, `;` statement boundary,
      bare expressions may fail silently, comparison-operator
      sugar table, migration-script invocation, where the
      implementation lives. Stays under one screen of orientation
      for someone picking up a `.sc` file in this directory.

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
  `>=` and the lexical `:==:` family and `::` `:!:`) that
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
- `SNOCONE.zip` (Lon, session #1) — Andrew Koenig's original
  Snocone, three source files:
  - **`snocone.sc` — canonical Andrew source.**  This is the
    Snocone compiler written in Snocone itself.  `bconv[]` table
    at lines 32–60 is the operator definition we adopt.  Andrew's
    final design vision.
  - `snocone.sno` — bootstrap compiler in SPITBOL.  Slightly
    earlier version of the language: missing `::`/`:!:` operators
    and the `struct` keyword that the self-host adds.
  - `snocone.snobol4` — alternate bootstrap (essentially the
    same as `.sno` with formatting differences).
  This goal adopts Andrew's `.sc` operator set verbatim, with
  three deletions for Lon's space-as-concat restoration: `&&`
  (replaced by SPACE), `||` (replaced by alt-eval `(,)`), `%`
  (reserved as user OPSYN slot).  All other Andrew choices
  preserved.

