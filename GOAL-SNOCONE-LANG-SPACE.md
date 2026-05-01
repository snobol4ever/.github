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

- [x] LS-3.a — Created `src/frontend/snocone/snocone.l` (new Flex source).
      one4all `02db637d` (W{OP}W envelope pattern, replacing the
      prev-token state machine of the first attempt `57b9d9e0`).
- [x] LS-3.b — `scripts/regenerate_parser_and_lexer_from_sources.sh`
      generates `snocone.lex.c` from `snocone.l`.
- [x] LS-3.c — Ran the LS-1.b test corpus through the new lexer via
      `test_snocone_lex2.c`; **31/31 token streams match**.
      one4all `02db637d`.
- [ ] LS-3.d — Existing hand-written `snocone_lex.c` removed in
      same commit as LS-4 Bison grammar lands.
- [ ] LS-3.e — Smoke test — `test_smoke_snocone.sh` MAY regress
      here because the parser hasn't caught up; that's expected.

**Design alignment (one4all `02db637d`):**

The new lexer follows snobol4.l lines 235-315 line-for-line:
space envelops every binary operator via `{W}OP{W}` patterns.
Whitespace alone between two atoms lexes as `T_CONCAT`.  Unary
versions of dual-role operators arrive bare (no leading W) and
return `T_1*` tokens (arity-1 form — the "1" prefix marks unary).
Token names match snobol4.tab.h for every concept equivalence,
under the post-session-#6 `T_<arity><charname>` scheme:
`T_IDENT`, `T_FUNCTION`, `T_INT`, `T_REAL`, `T_STR`, `T_KEYWORD`,
`T_CONCAT`, `T_2EQUAL` (`=`), `T_2QUEST` (`?`), `T_2PIPE` (`|`),
`T_2PLUS` (`+`), `T_2MINUS` (`-`), `T_2STAR` (`*`), `T_2SLASH` (`/`),
`T_2CARET` (`^`), `T_2DOLLAR` (`$`), `T_2DOT` (`.`),
`T_2AMP` (`&`), `T_2AT` (`@`), `T_2POUND` (`#`),
`T_2PERCENT` (`%`), `T_2TILDE` (`~`),
`T_LPAREN`, `T_RPAREN`, `T_LBRACK`, `T_RBRACK`, `T_COMMA`, plus
the matching `T_1*` unaries (`T_1PLUS`, `T_1MINUS`, `T_1STAR`,
`T_1SLASH`, `T_1PERCENT`, `T_1AT`, `T_1TILDE`, `T_1DOLLAR`,
`T_1DOT`, `T_1POUND`, `T_1PIPE`, `T_1EQUAL`, `T_1QUEST`,
`T_1AMP`, `T_1BANG`).  Multi-character ops keep their existing
character-name tokens (no arity ambiguity): `T_EQ`/`T_NE`/`T_LT`/
`T_GT`/`T_LE`/`T_GE` numeric, `T_LEQ`/`T_LNE`/`T_LLT`/`T_LGT`/
`T_LLE`/`T_LGE` lexical, `T_IDENT_OP`/`T_DIFFER` identity,
`T_PLUS_ASSIGN`/`T_MINUS_ASSIGN`/`T_STAR_ASSIGN`/`T_SLASH_ASSIGN`/
`T_CARET_ASSIGN` compound-assigns, `T_LBRACE`/`T_RBRACE`/
`T_SEMICOLON`/`T_COLON` punctuation, `T_KW_*` keywords.

The session-#6 rename (Lon directive: "I do not like the T_UN_*
names implying undo. Name things from the characters since this
tokens.") replaced the prior English-named binary tokens
(`T_ADDITION`, `T_SUBTRACTION`, `T_AMPERSAND`, ...) and `T_UN_*`
unary tokens with the symmetric arity-prefixed scheme.  Both
SNOBOL4 and Snocone moved in lockstep so the snobol4↔snocone
name-equivalence invariant is preserved; the rename is purely
cosmetic, semantics unchanged.

When LS-4 lands the Bison grammar, every operator token will be the
same identifier on both sides of the lex/parse boundary AND match
the SNOBOL4 grammar's name for the same concept.

### LS-3.f — Lexer single-pass refactor (NEW sub-step, session 2026-04-30 #1)

The session-#9 lexer (one4all `02db637d`) accumulates tokens into a
`ScTokenBuf` inside `snocone_lex2()` — a two-pass design left over
from the LS-3.c standalone token-stream tests.  one4all convention
(snobol4, raku, rebus) is single-pass Flex→Bison: each rule
`return T_*;` directly, Bison pulls via `yylex`.  Snocone must
match (Lon directive, session 2026-04-30 #1: "use clean emission
technique just like SNOBOL4, use one pass when ever possible").

**Session 2026-04-30 #2 — architectural pivot to threaded-code FSM.**
Two further Lon directives during the LS-3.f.1 implementation drove
the design away from Flex+Bison entirely:

  (a) "Space, tab, and newline are just simply whitespace.  And do
      not forget /* */ and //...\n patterns which must be embedded
      in the whitespace RE used as {W}."

  (b) "Use no switch statements... no for or while or do/until
      loops anywhere in the LEX code body of the FSM... pure FSM,
      label / [if] / action / goto columns lined up vertically."

Folding `LCOMMENT|BCOMMENT` into `{W}` proved infeasible: with ~30
`{W}OP{W}` rules, flex 2.6.4's NFA→DFA pass hangs at 0% CPU /
2.7 MB RSS for >180s on this input — verified with `--full`,
`-Cf`, `-CF`, `-Ca`, `-Cem`, `-Ce`, `-Cm` (none help).  Empirically
demonstrated and saved as a baseline: pre-refactor `snocone.lex.c`
on the same operator set with no comments-in-W compiles in <1s,
adding even just `LCOMMENT` to `W` triggers the hang.

Lon's choice (after weighing flex+bison vs CMPILE-style 256-byte
tables vs free-form C vs threaded-code FSM): **threaded-code FSM**.
The lexer becomes one C function `sc_lex_next(LexCtx *ctx)` whose
body is a graph of labelled blocks linked by `goto`.  Each line is
exactly `Label: [if (cond)]  action;  goto NEXT;` aligned in three
vertical columns.  No `switch`, `for`, `while`, or `do/while`
appears anywhere in the FSM body (verified post-preprocessor:
the only matches in the expanded source are the keyword-table
strings `"while"`, `"do"`, `"for"`, `"switch"`, which are data,
not control flow).  Loops are formed by backward-pointing gotos.

Comments-as-whitespace falls out for free: `S_LCOMMENT` and
`S_BCOMMENT`/`S_BC_STAR` are sub-FSMs that transition back into
`S_WS` on completion.  `x  /* hi */ + y` correctly emits
`IDENT ADDITION IDENT` because the entire whitespace+comment+
whitespace gap is consumed before the `+` decision.

- [x] LS-3.f.1 — Threaded-code FSM lexer **LANDED** session 2026-04-30 #2.
      `snocone.l` and `snocone.lex.c` deleted (broken flex source +
      truncated regen).  `snocone_fsm.c` added (~740 lines).  Single
      function `sc_lex_next(ctx)` returns one token kind per call.
      LS-1.b 31-test acceptance harness: **31/31 PASS**.  Production
      gates unchanged (link path still uses old hand-written
      `snocone_lex.c` until LS-4 wires in the new front-end):
      `test_smoke_snocone.sh` 5/5, `test_beauty_snocone_all_modes.sh`
      42/0/3, `test_smoke_unified_broker.sh` 49/0.  Token kind enum
      `ScKind` in `snocone_lex2.h` unchanged — same names match
      snobol4.tab.h conventions per RULES.md.  Note that this
      step's original acceptance criterion "Mirror snobol4.l
      %option reentrant noyywrap shape" is superseded: the FSM
      replaces flex entirely.
- [x] LS-3.f.2 — **LANDED** session 2026-04-30 #2 (one4all `55a30bcb`).
      `test_snocone_lex2.c` moved to `test/frontend/snocone/
      test_snocone_fsm.c`.  `ScTokenBuf`, `ScToken2`, `LexerState`,
      `snocone_lex2()`, `sc_token_buf_free()` all DELETED — they were
      dead two-pass-design vestiges with no remaining callers.
      `snocone_lex2.h` renamed to `snocone_fsm.h` and stripped to just
      the public FSM API (`ScKind`, `LexCtx`, `sc_lex_next`,
      `sc_kind_is_value`, `sc2_kind_name`).  The harness now drives
      `sc_lex_next(ctx)` directly token-by-token; no buffer.  Net:
      ~470 lines deleted, ~70 added.
- [x] LS-3.f.3 — Production gates (`test_smoke_snocone.sh` 5/5 etc.)
      remain green throughout LS-3.f.1.  Confirmed at handoff —
      production link path uses old hand-written `snocone_lex.c`
      until LS-4.j wires in `sc_lex_next`.

### LS-4 — Grammar implementation (Bison) — RESTRUCTURED into smaller chunks

Lon directive (session 2026-04-30 #1): "Split out steps into smaller
chunks if needed."  Original LS-4.a–e replaced with finer-grained:

- [x] LS-4.a — **LANDED session 2026-04-30 #3.**  Skeleton `snocone.y`:
      atoms (T_INT, T_REAL, T_STR, T_IDENT, T_KEYWORD) + arithmetic
      (`+`, `-`, `*`, `/`, `^` — right-associative exponent) +
      paren-grouping + signed unary `+`/`-` + `;`-terminated
      statements + top-level `T_ASSIGNMENT` splitting into
      subject/replacement matching snobol4.y's `stmt_commit_go`
      pattern.  Public entry `Program *snocone_parse_program(const
      char *src, const char *filename)` at `src/frontend/snocone/
      snocone.y` (~600 lines incl. doc comments, generated
      `snocone.tab.c`/`.tab.h` committed alongside).  yylex thunk
      calls `sc_lex_next(ctx)` directly — single-pass per LS-4.j
      convention.  Token-namespace decoupling resolved cleanly via
      `%code top` block: aliases the FSM's `T_*` enum names to
      `SC_T_*` via `#define`/`#undef` around the
      `#include "snocone_lex.h"`, so a single translation table
      `sc_kind_to_tok()` is the only boundary between the FSM
      enum (1..N) and Bison's `enum sc_tokentype` (258+M).  File
      reorganisation: `snocone_fsm.c`/`.h` renamed to
      `snocone_lex.c`/`.h` (the standard frontend lexer name);
      old hand-written `snocone_lex.c`/`.h` moved to
      `one4all/archive/`; Makefile and 2 callsite includes
      (`snocone_control.c`, `snocone_parse.h`) redirected to the
      archive path; production path unchanged.
      `test_snocone_fsm.c` renamed to `test_snocone_lex.c`.
      New gate `test_smoke_snocone_parse_a.sh` runs
      `test_snocone_parse_a.c` (9 cases covering assignment IR
      shape, precedence, parens override, exponent right-assoc,
      unary minus, bare-expression statement subject-only,
      multiple statements, string and real literals — **35/35
      PASS**).  Production gates remain green: smoke 5/5,
      beauty 42/0/3, broker 49/0; FSM lex test 31/31.
- [x] LS-4.b — **LANDED session 2026-04-30 #4.**  Comparison/identity
      tier `expr5` added between `expr0` (assignment) and `expr6`
      (add/sub).  All 14 operators (`T_EQ`/`T_NE`/`T_LT`/`T_GT`/
      `T_LE`/`T_GE` numeric, `T_LEQ`/`T_LNE`/`T_LLT`/`T_LGT`/`T_LLE`/
      `T_LGE` lexical, `T_IDENT_OP`/`T_DIFFER` identity) lower to
      `E_FNC` named calls — `a == b` → `E_FNC("EQ", a, b)`,
      `a :: b` → `E_FNC("IDENT", a, b)`, `a :!: b` →
      `E_FNC("DIFFER", a, b)`.  Left-associative chaining via Bison
      left-recursion; `a == b == c` parses as
      `EQ(EQ(a,b), c)`.  Per Andrew's `bconv[]` (snocone.sc lines
      32–60) all comparisons sit at one priority BELOW arithmetic
      add/sub: `a + b == c + d` correctly parses as
      `EQ(a+b, c+d)`.  Plus T_FUNCTION call-form `EQ(2+2, 4)` →
      `E_FNC("EQ", E_ADD(2,2), E_ILIT(4))` via `expr17`'s new
      `T_FUNCTION T_LPAREN exprlist T_RPAREN` rule, mirroring
      `snobol4.y:197`.  T_FUNCTION elevated from no-value catch-all
      to `%token <str> T_FUNCTION`; new helper non-terminals
      `exprlist`/`exprlist_ne` mirror `snobol4.y:187-193`.  Ten
      additional comparison-tier `%token` declarations moved out of
      the catch-all "all other tokens" block into their own dedicated
      block.  T_COMMA promoted to its own `%token` line for visibility
      (was buried in catch-all).  No bison conflicts.  Headline gate
      from goal file met: parses `OUTPUT = EQ(2+2, 4)`.  New gate
      `test_smoke_snocone_parse_b.sh` runs `test_snocone_parse_b.c`
      (10 cases / **119/119 PASS** — every comparison op shape, the
      EQ(2+2,4) headline, precedence below `+`, zero-arg call,
      three-arg call, nested call, left-assoc chaining, mixed
      var/literal args).  Production gates remain green: smoke 5/5,
      beauty 42/0/3, broker 49/0; FSM lex test 31/31; LS-4.a
      parse-a 35/35.  This means LS-4.b shipped 154/154 (35+119)
      across both side-channel parser tests.
- [x] LS-4.c — **LANDED session 2026-04-30 #5.**  Three pattern
      operator tiers added — `expr1` (match `?` → E_SCAN,
      right-assoc, pri 1), `expr3` (alternation `|` → E_ALT n-ary
      fold, pri 3), `expr4` (concat T_CONCAT → E_SEQ n-ary fold,
      pri 4) — slotted between `expr0` (assignment) and `expr5`
      (comparison) so the precedence chain is now
      `=  <  ?  <  |  <  concat  <  ==  <  +/-  <  */  <  ^`,
      each operator binding tighter than the one to its left.
      `expr3`/`expr4` use the snobol4.y:131,134 idiom — when the
      left operand is already an n-ary node of the same kind we
      extend it with `expr_add_child`; otherwise create a fresh
      n-ary node.  Bison's left-recursion drives the fold one
      operand at a time, giving the n-ary collapse for free.
      Compound-assigns (`+=` `-=` `*=` `/=` `^=`) added at the
      `expr0` level alongside `=`; each lowers to a clone-LHS
      pattern: `a += b` → `E_ASSIGN(a, E_ADD(clone(a), b))`.
      New helper `sc_clone_expr_simple` does a shallow recursive
      clone (kind/ival/dval/sval/children) — required because the
      IR's tree representation forbids node aliasing (children
      pointer arrays would otherwise alias and double-free at
      cleanup).  Coverage sufficient for atomic LHS (E_VAR /
      E_KEYWORD / leaf literals); LS-4.d will extend for E_IDX
      subscripts when those land.  T_CONCAT, T_MATCH,
      T_ALTERNATION, T_PLUS_ASSIGN, T_MINUS_ASSIGN, T_STAR_ASSIGN,
      T_SLASH_ASSIGN, T_CARET_ASSIGN promoted out of the catch-all
      "all other tokens" block into dedicated sections (cosmetic
      organisation).  Header comment block consolidated and a
      precedence-table summary added inline.  No bison conflicts.
      **Headline gate from goal file met:** parses
      `s = 'hello' ' world'`  →
      `E_ASSIGN(s, E_SEQ(E_QLIT("hello"), E_QLIT(" world")))`.
      New gate `test_smoke_snocone_parse_c.sh` runs
      `test_snocone_parse_c.c` (14 test functions / **66/66 PASS**
      — concat 2-string headline, n-ary 4-child concat fold,
      var+string concat, alternation binary and 4-ary fold, alt
      below concat, match basic, match-pattern-is-alt, assign
      below match, plus-assign with clone-distinctness check,
      minus-assign, full compound-assign set (+=, -=, *=, /=, ^=),
      arithmetic-grouped-under-concat, full chain
      `result = subject ? a b | c d`).  Production gates remain
      green: smoke 5/5, beauty 42/0/3, broker 49/0; FSM lex 31/31;
      LS-4.a 35/35, LS-4.b 119/119.  Combined LS-4.{a,b,c} = 220/220.
      Lexer behaviour note recorded in test (`1+2` lexes as
      `T_INT T_UN_PLUS T_INT` per W{OP}W envelope rule — the
      grammar requires `1 + 2` for binary T_ADDITION; this is
      SNOBOL4 surface convention, not a parser bug, and was
      caught/documented during the LS-4.c test write-up).
- [x] LS-4.cn — **LANDED session 2026-04-30 #7.**  Cosmetic /
      naming-symmetry rung between LS-4.c and LS-4.d.  Three
      coordinated changes:

      **1. File rename** — `snocone.y` →
      `snocone_parse.y`; generated artifacts `snocone.tab.{c,h}`
      → `snocone_parse.tab.{c,h}`.  Now matches the
      `snocone_lex.{c,h}` companion: a Snocone reader sees the
      pair (lex, parse) at a glance rather than a `.y` whose
      relationship to `_lex.{c,h}` requires reading the regen
      script.  Performed via `git mv` to preserve history.

      **2. CODE_t typedef** — `typedef Program CODE_t;` added
      in `src/frontend/snobol4/scrip_cc.h`.  Symmetric with
      `EXPR_t`: `EXPR_t` is the IR for one expression (the type
      EVAL operates on, per `eval_code.c:6-9`); `CODE_t` is the
      IR for a list of statements (the type CODE operates on,
      per `eval_code.c:11-14`).  `CODE_t` is a typedef *alias* of
      `Program` — every existing call site that uses
      `Program *` continues to work.  New code may use either
      name.  Snocone parser migrated as the first user:
      `ScParseState.prog` → `.code`, public entry signature
      changed from `Program *snocone_parse_program(...)` to
      `CODE_t *snocone_parse_program(...)`.

      **3. Legacy parser moved to archive/** — The session-#7
      file rename created an unintended interaction: with
      `snocone_parse.y` next to the legacy hand-written
      `snocone_parse.c` in the same directory, GNU Make's
      built-in `.y.c` suffix rule clobbered the legacy parser
      during the next build.  Initially worked around with
      `.SUFFIXES:` in `src/Makefile`; permanent fix is to
      relocate the legacy parser to `archive/`.  Both legacy
      files (`snocone_parse.c` Sprint-SC1 shunting-yard parser
      + `snocone_parse.h` API header) moved via `git mv` to
      `archive/snocone_parse.c` and `archive/snocone_parse.h`.
      Two `#include "snocone_parse.h"` callsites updated to
      `#include "../../../archive/snocone_parse.h"`
      (`snocone_lower.h` and `snocone_control.c`).  Makefile
      `FRONTEND_SNOCONE` updated to reference
      `../archive/snocone_parse.c` alongside the
      already-archived `../archive/snocone_lex.c`.  The
      `.SUFFIXES:` workaround removed — no longer needed since
      the `.y` and `.c` are now in different directories.

      **Archive cleanup invariant** updated: the four
      `archive/snocone_lex.*` references from LS-4.a become
      **six** after LS-4.cn (the two new
      `archive/snocone_parse.h` includer-side mentions in
      `snocone_lower.h` and `snocone_control.c`, plus the
      Makefile entry for `archive/snocone_parse.c`).  LS-4.j
      must end with zero such references — verify with
      `grep -rn 'archive/snocone' src/ scripts/ test/` returning
      empty, plus confirming `archive/snocone_parse.c` and
      `archive/snocone_parse.h` are deletable.

      All gates green throughout: smoke snobol4 7/7, smoke
      snocone 5/5, beauty 42/0/3, broker 49/0, parse-a 35/35,
      parse-b 119/119, parse-c 66/66, FSM lex 31/31.  Combined
      frontend tests **251/251**.  Pure rename-and-typedef
      change; semantics unchanged.
- [x] LS-4.d — **LANDED session 2026-04-30 #8.**  Postfix subscript
      `a[i, j]` parses and lowers to E_IDX.  Single rung, single
      grammar tier, no surprises.

      **Grammar shape** — new `expr15` tier inserted between
      `expr11` (exponent) and `expr17` (atoms), mirroring
      `snobol4.y:183` exactly:

          expr15 : expr15 T_LBRACK exprlist T_RBRACK
                                { E_IDX node; subject as child[0];
                                  index expressions drained from the
                                  exprlist temporary into remaining
                                  children }
                 | expr17        ;

      Left-recursive on the same tier so `a[i][j]` chains
      naturally to `E_IDX(E_IDX(a, i), j)`, while
      `a[i, j]` produces a single n-ary `E_IDX(a, i, j)`.  The
      `exprlist` non-terminal already exists from LS-4.b
      (function-call argument lists); reused without modification.
      Empty subscript `a[]` is permitted at the grammar level via
      the empty-list arm of `exprlist` — yields `E_IDX(a)` with
      just the subject.  Semantic legality of empty subscripts is
      a downstream concern.

      **Lexer** — no changes.  `[` was already emitted
      unconditionally as `T_LBRACK` regardless of preceding
      whitespace (snocone_lex.c E_LBRACK rule); `a[i]` and
      `a [i]` lex identically — no CONCAT injection between value
      and `[`, matching Test 24's "no CONCAT before subscript"
      requirement from the goal file.

      **`expr11` redirect** — exponentiation now delegates to
      `expr15` instead of directly to `expr17`, so subscript
      binds tighter than `^` (e.g. `a[i] ^ 2` parses as
      `(a[i]) ^ 2`).  Other tiers above (mul/div, add/sub,
      compare, concat, alt, match, assign) inherit the new
      tightness automatically through the existing delegation
      chain.

      **Compound-assign LHS** — `a[i] += 1` lowers to
      `E_ASSIGN(a[i], E_ADD(clone(a[i]), 1))` correctly: the
      `sc_clone_expr_simple` helper from LS-4.c already handles
      E_IDX recursively (its switch-by-kind copies sval/ival/dval
      and recursively clones every child, which works for any
      n-ary node — the LS-4.c comment already anticipated this:
      "Coverage … plus n-ary E_IDX / E_FNC for `a[i] += 1`…").
      Verified by pointer-distinctness check in the test: the
      LHS subtree and the RHS-embedded clone share no nodes
      anywhere in the tree (no double-free risk at cleanup).

      **Token block reorganization** — `T_LBRACK` and `T_RBRACK`
      promoted out of the catch-all "unused" `%token` block
      into a labeled "LS-4.d" block, matching the convention
      established by LS-4.b/c (each rung's tokens move from the
      catch-all into a labeled block when they pick up rules).

      **Testing** — `test/frontend/snocone/test_snocone_parse_d.c`
      (15 test functions, 79 assertions) covers the headline
      `a[i, j]` two-index gate plus: single index, empty
      subscript, two-deep chaining `a[i][j]`, three-deep
      chaining `a[i][j][k]`, string keys `T['key']`, expression
      children `a[1+2, 3*4]`, call-then-subscript `f(x)[i]`,
      paren-then-subscript `(a+b)[i]`, compound-assign with
      subscript LHS (with deep clone-distinctness + no-shared-
      nodes verification), subscript-in-concat `a[i] b`,
      subscript-in-arith `a[i] + b[j]`, plain-assign with
      subscript LHS `a[i] = 5`, nested subscripts `a[b[c]]`,
      and subscript-below-exponent `a[i] ^ 2`.  Runner
      `scripts/test_smoke_snocone_parse_d.sh` matches the
      parse-c shape.

      **Bison build** — zero shift/reduce conflicts.
      `expr15` left-recursion is the only choice point and Bison
      resolves it cleanly because the LR(1) lookahead at
      `T_LBRACK` is unambiguous after any `expr17`.

      All gates green: parse-a 35/35, parse-b 119/119, parse-c
      66/66, **parse-d 79/79**, smoke snocone 5/5, beauty
      42/0/3, broker 49/0.  Combined parse gates **299/299**
      (was 220/220 before this rung).  Side-channel — the
      LS-4.d parser is not yet wired into scrip's production
      driver; that happens at LS-4.j.  Production driver still
      uses the legacy `archive/snocone_parse.c` shunting-yard
      parser, hence the smoke/beauty/broker gates remain
      green even though they don't exercise `expr15`.

      **Forward note re: LS-4.f** — when `if`/`else` lands, use
      the balanced `matched_stmt` / `unmatched_stmt` clause-
      phrase split (Pascal/Algol style, zero conflicts) rather
      than C's default-shift conflict acceptance.  Goal file's
      meticulousness about hierarchy points to the balanced
      grammar being the right fit for Snocone, even though the
      shift-default would compile.
- [x] LS-4.e — **LANDED session 2026-04-30 #9** (one4all `a929d72b`).
      All remaining SPITBOL unary operators added to the Snocone Bison
      grammar at `expr17` (atoms tier, highest priority): `*expr` →
      E_DEFER, `.expr` → E_NAME, `$expr` → E_INDIRECT, `@expr` →
      E_CAPT_CURSOR, `~expr` → E_NOT, `?expr` → E_INTERROGATE,
      `&expr` → E_OPSYN("&"), and OPSYN-slot unaries `%expr` `/expr`
      `#expr` `|expr` `=expr` → E_OPSYN(op).  Chains nest right-to-
      left: `~.x` → E_NOT(E_NAME(x)).  Binary context preserved:
      `a + *b` → E_ADD(a, E_DEFER(b)).  Zero new Bison conflicts.
      Gate `test_smoke_snocone_parse_e.sh` runs
      `test_snocone_parse_e.c` (19 functions / **71/71 PASS**).
      Combined parse gates 370/370 (was 299/299).  Production gates
      unchanged (smoke 5/5, beauty 42/0/3, broker 49/0).
- [x] LS-4.f — **LANDED session 2026-04-30 #10** (one4all `c4337189`).
      `c4337189`).  Control flow `if`/`else`/`while` parses, lowers
      to flat SPITBOL :F/:(uncond)-style stmts, and passes 118/118
      side-channel assertions across 15 test cases.  **Held open
      pending Lon's resolution of an open semantic question
      surfaced at handoff:**

      > Does `if (c) {…}` (bare bound name as cond) lower to the
      > same shape as `if (DIFFER(c)) {…}` (real backtracking expr)?

      Current behaviour: `if (c)` accepts a bare expression and
      emits `cond :F(Lend)`.  When `cond` is a bare bound name,
      that statement always succeeds (the SNOBOL4 default for an
      assigned variable reference is succeed-with-value), so the
      `:F(Lend)` branch can never fire — runtime-correct but
      IR-misleading.  Three resolutions on the table:

      1. **Accept as-is**, document the gotcha — bare-name conds
         always-succeed, programs that want failure need DIFFER /
         EQ / `?match` / etc.
      2. **Restrict to operator-yielding expressions** at parse
         time — `if (c)` is a syntax error; `if (DIFFER(c))` /
         `if (GT(x, 0))` / `if (s ? pat)` etc. are accepted.
      3. **Auto-wrap bare names** — `if (c)` lowers identically to
         `if (DIFFER(c))`.  Most "what the C programmer probably
         meant" semantics, but most surprising in a SPITBOL world.

      **Lon's decision (session 2026-04-30 #11):** Option 1 — accept
      as-is.  Bare-name conditions are legal Snocone; they always
      succeed at runtime, which is correct SPITBOL behaviour.  Warnings
      for the always-succeeds case are deferred to LS-4.w (low
      priority).  LS-4.f is therefore ready to land as committed.

      **Implementation choices made this session (all working in
      `c4337189`):**
      - Pascal/Algol balanced grammar `matched_stmt` /
        `unmatched_stmt` for dangling-else.  Zero shift/reduce
        and zero reduce/reduce conflicts.
      - **Emit-and-splice architecture.**  `if_head` /
        `while_head` reduce on `T_RPAREN` of the head, snapshot
        `st->code->tail`, emit nothing.  Body parses normally.
        Parent rule's final action calls `sc_finalize_if_no_else`
        / `sc_finalize_if_else` / `sc_finalize_while` to splice
        cond-stmt and label-stmts into the linked list at the
        correct positions.  The eager-emit-via-MRA approach was
        attempted first and produced 96 reduce/reduce conflicts
        (Bison was killed running `-Wcounterexamples`); snapshot
        + final-action splice keeps emissions out of the contended
        region.
      - `else_keyword` non-terminal snapshots tail at
        `T_KW_ELSE` so the else-body splice point is known.  One
        non-terminal shared between matched-else and unmatched-else
        rules — distinct anonymous MRAs at the same parser state
        would have been a conflict.
      - `opt_head_sep` non-terminal absorbs the spurious `T_CONCAT`
        that the LS-3 W{OP}W lexer synthesizes between `)` of an
        if/while head and a value-starting body token (e.g.
        `if (c) y = 1` — between `)` and `y`).  Inside an
        expression that CONCAT is meaningful concat; after a head
        it must be discarded.  Empty-production keeps brace-block
        bodies (`if (c) {…}`) working with no changes.
      - Lowering shapes (verified by tests):
          `if (C) S`         → `cond:F(Lend); <S>; Lend`
          `if (C) S1 else S2`→ `cond:F(Lelse); <S1>; :(Lend); Lelse; <S2>; Lend`
          `while (C) S`      → `Ltop; cond:F(Lend); <S>; :(Ltop); Lend`
      - Synthetic labels `_Lend_NNNN`, `_Lelse_NNNN`,
        `_Ltop_NNNN` (4-digit per-parse counter, underscore prefix
        avoids collision with user labels).
      - `IfHead` / `WhileHead` heap structs added to `%union`
        (forward-declared in the prologue, full layout in the
        epilogue).
      - **Empty-then-S1 splice ordering bug fixed:** when
        `before_else == h->before_body`, after step (1) splices
        `cond_stmt`, the correct anchor for the goto+Lelse chain
        is `cond_stmt` itself, not the original `before_else`
        (which would re-prepend before cond).

      **Test gate** `scripts/test_smoke_snocone_parse_f.sh` runs
      `test/frontend/snocone/test_snocone_parse_f.c` — 15 functions
      / **118/118 PASS**.  Coverage: if-no-else, if-else, while,
      block bodies, empty blocks, dangling-else (else binds to
      inner-if), while-inside-if, if-inside-while, pre-existing
      stmts (splice integrity), post-existing stmts, unique labels
      across adjacent constructs, if-else with both branches
      block-wrapped, empty then-branch with else (the splice-
      ordering edge case), chained `else if`.

      All production gates green: `test_smoke_snocone.sh` 5/5,
      `test_smoke_unified_broker.sh` 49/0,
      `test_beauty_snocone_all_modes.sh` 42/0/3.  Combined parse
      gates **488/488** (was 370/370).  Side-channel only — LS-4.j
      wires the new parser into scrip's production driver.

      Smoke gate `if_eq`/`while` from the original LS-4.f goal-file
      step description still PASSes via the legacy
      `archive/snocone_parse.c` shunting-yard parser (production
      driver still uses that until LS-4.j).  When LS-4.j lands, the
      smoke gate will exercise the new Bison parser and any
      cond-semantics decision Lon makes here gates that
      milestone.
- [x] LS-4.g — **LANDED session 2026-04-30 #11** (one4all `4cef1dc6`). `do/while` and `for` parse and lower correctly. (`do/until` initially added, then **removed per Lon directive session 2026-04-30 #12** — Snocone follows C's loop forms exactly: `while` and `do/while` only.) `do_body` non-terminal (brace-block only) resolves the grammar ambiguity where T_KW_WHILE after a matched_stmt body would be indistinguishable from a new while_head. `sc_finalize_do_while` (onsuccess loops back), `sc_finalize_for` (init→Ltop→cond:F→body→step→:(Ltop)→Lend). New gate `test_smoke_snocone_parse_g.sh`: **95/95 PASS** (3 tests verify do/until is now a syntax error). Combined parse gates **583/583** (488+95).
- [x] LS-4.h — **LANDED session 2026-04-30 #13** (one4all `ddc44b59`,
      preceded by `1c72f7f6` for the LS-4.h grammar additions and the
      first `T_KW_*` → `T_*` rename pass).
      `function`/`return`/`freturn`/`nreturn` parse and lower to the
      SPITBOL idiom.

      **Grammar shape** — `func_head` non-terminal at the
      `matched_stmt` level (no dangling-else risk; a function
      definition is a self-contained block).  Two body shapes —
      brace-block with stmts and brace-block-empty.  Helper
      non-terminals `func_arglist` (3 productions: empty `)`,
      single-IDENT `)`, `func_arglist_ne )`) and `func_arglist_ne`
      (2 productions: 2-IDENT base case, left-recursive
      append) build the comma-separated arg string left-to-right,
      yielding `"a"`, `"a,b"`, `"a,b,c"`, etc., as a single
      malloc'd string handed to `sc_func_head_new`.

          func_head : T_FUNCTION T_CALL T_LPAREN func_arglist opt_head_sep
                          { sc_func_head_new(st, $2, $4); }

      The `T_CALL` token is the FSM's IDENT-followed-by-zero-
      space-`(` call-form token (also used at `expr17` for
      call-style expressions); it carries the function name string.
      The `T_LPAREN` is consumed separately because the FSM emits
      `T_CALL` and `T_LPAREN` as **two adjacent tokens** even
      though the source text has no whitespace between them — same
      pattern as `expr17`'s call-form rule.

      `simple_stmt` gets four new alternates for the return forms:

          | T_RETURN expr0 T_SEMICOLON  { sc_append_return(st, $2); }
          | T_RETURN T_SEMICOLON        { sc_append_return(st, NULL); }
          | T_FRETURN T_SEMICOLON       { sc_append_freturn(st); }
          | T_NRETURN T_SEMICOLON       { sc_append_nreturn(st); }

      **Lowering shapes** (verified by tests):

          function NAME(args) { body }
              DEFINE('NAME(args)')   (bare-expr E_FNC)
              :(NAME_end)            (skip-the-body uncond goto)
              NAME    <body>         (entry-point label, body stmts)
              NAME_end               (label pad, skip target)

          return E ;     ->   <fn> = E :(RETURN)   (assignment+goto)
          return ;       ->   :(RETURN)
          freturn ;      ->   :(FRETURN)
          nreturn ;      ->   :(NRETURN)

      **Implementation notes:**
      - `ScParseState` gets a `cur_func_name` field; saved on the
        `FuncHead` struct's `prev_func` slot when a function head
        fires, restored at finalize.  Defends against nested
        function definitions even though Andrew's `.sc` doesn't
        have them.
      - `sc_func_head_new` does the work eagerly: emits
        `DEFINE('NAME(args)')` (E_FNC subject, no goto) and
        `:(NAME_end)` (bare goto, no subject) immediately, then
        snapshots `st->code->tail` as the entry-point splice
        anchor.  No body has been parsed yet at this point —
        Bison runs head's action at the close-paren reduction.
      - Body stmts append normally to `st->code` via
        `sc_append_stmt` / `sc_append_chain`.
      - `sc_finalize_function` splices the entry-point label
        `NAME` after the goto stmt (so the body's first stmt
        carries the label by SNOBOL4's "labels attach to next
        non-empty stmt" rule), appends `NAME_end` at the tail,
        restores `cur_func_name`.
      - `sc_append_return` checks `cur_func_name` for the
        return-with-value case: if inside a function and a value
        is present, lowers to `fn = E :(RETURN)`; otherwise
        lowers to a bare goto.

      **Token rename — `T_KW_*` → `T_*`** (Lon directive,
      session 2026-04-30 #13).  All Snocone keyword tokens drop
      the `KW_` infix.  17 tokens renamed across `snocone_lex.h`,
      `snocone_lex.c`, `snocone_parse.y`, `test_snocone_lex.c`:
      `T_IF`, `T_ELSE`, `T_WHILE`, `T_DO`, `T_UNTIL`, `T_FOR`,
      `T_SWITCH`, `T_CASE`, `T_DEFAULT`, `T_BREAK`, `T_CONTINUE`,
      `T_GOTO`, `T_RETURN`, `T_FRETURN`, `T_NRETURN`, `T_STRUCT`,
      and `T_FUNCTION_KW` for the `function` keyword (placeholder
      while `T_FUNCTION` was still occupied by the call-form
      token).  Pure cosmetic rename; semantics unchanged.

      **Second rename pass** (Lon directive, same session #13):
      `T_FUNCTION` → `T_CALL` (the IDENT-followed-by-zero-space-`(`
      call-form token from the FSM); `T_FUNCTION_KW` → `T_FUNCTION`
      (the `function` keyword now takes the cleaner name).  Done as
      a three-step swap via a `T_FUNCTION_TEMPSWAP` holding name to
      avoid aliasing during the rename.  FSM internal action label
      `E_FUNCTION` → `E_CALL` for symmetry with the new token name
      (the `E_` prefix in `snocone_lex.c`'s threaded FSM means
      "emit-then-return", and the suffix mirrors the token name).
      Stale "_KW suffix to avoid colliding" rationale comment
      removed from `snocone_parse.y`.  Generated
      `snocone_parse.tab.c`/`.tab.h` regenerated from source.

      **Smoke-test rename** — `scripts/test_smoke_snocone.sh`
      changed `procedure Double(n)` → `function Double(n)` in the
      `procedure` smoke case.  The legacy `archive/snocone_lex.c`
      keyword table picks up `"function"` as a synonym for
      `"procedure"` (same `SNOCONE_KW_PROCEDURE` enum value), so
      the production driver — still using the legacy
      shunting-yard parser until LS-4.j — accepts the new
      keyword without further change.  When LS-4.j removes the
      legacy parser, this synonym entry can go too.

      **Test gate** `scripts/test_smoke_snocone_parse_h.sh` runs
      `test/frontend/snocone/test_snocone_parse_h.c` — 15 test
      functions / **85/85 PASS**.  Coverage: empty-body function,
      single-arg + return-bare, return-with-value, freturn,
      nreturn, two-arg, three-arg, surrounding-stmts splice
      integrity, multi-body-stmt function, return-uses-correct-
      enclosing-name, function-with-if-inside, two-functions-in-
      sequence, top-level-bare-return, function-with-while-
      inside, DEFINE call shape verification.  Combined parse
      gates **668/668** (was 583/583).

      **All gates green:** FSM lex 31/31, parse a/b/c/d/e/f/g/h
      35+119+66+79+71+118+95+85 = 668/668, smoke snocone 5/5
      (using `function` keyword via legacy synonym), beauty
      3-mode 42/0/3, unified broker 49/0.  Bison emitted zero
      shift/reduce and zero reduce/reduce conflicts.

      Side-channel only — the LS-4.h grammar additions are not
      wired into scrip's production driver path until LS-4.j.
- [ ] LS-4.i — `switch`/`case`/`default`, `break`/`continue`, `goto`,
      `struct`, alt-eval `(a, b, c)` → `E_VLIST`.  beauty.sc-class
      programs reachable.

      LS-4.i broken into sub-steps for clean incremental commits:

- [x] LS-4.i.1 — **LANDED session 2026-05-01 #1.**  `goto LABEL;`
      and `LABEL: stmt` prefix parse and lower to flat SNOBOL4 idiom.

      **Grammar shape** — two tiny additions:

          simple_stmt : ...
                      | T_GOTO T_IDENT T_SEMICOLON
                              { sc_append_goto_label(st, $2); free($2); }
                      ;

          label_decl  : T_IDENT T_COLON
                              { sc_emit_label_pad(st, $1); free($1); }
                      ;

          matched_stmt   : ... | label_decl matched_stmt   ;
          unmatched_stmt : ... | label_decl unmatched_stmt ;

      The `label_decl` non-terminal fires its semantic action eagerly
      at the colon — emits a label-only pad stmt into `st->code`
      before the trailing stmt parses.  In SNOBOL4 a label on a
      label-only pad chains forward to the next non-empty stmt, so
      `top: x = 1;` produces `[label-pad "top"] [x = 1]` and a goto
      to `top` lands semantically on the assignment.  No mid-rule
      actions, no snapshots, no splice — the label-eager-emit
      pattern is the cleanest fit.

      **Lowering shapes** (verified by tests):

          goto NAME ;       ->   stmt: subject=NULL, go.uncond="NAME"
          NAME : stmt       ->   stmt: label="NAME", subject=NULL, go=NULL
                                 followed by inner stmt's stmts.

      **Disambiguation note** — at stmt-start, on T_IDENT with
      lookahead T_COLON, Bison's LR(1) resolves cleanly: T_COLON does
      not appear in any expression rule's FOLLOW set, so the only
      viable parse is to shift T_COLON into label_decl rather than
      reduce T_IDENT to expr17.  Bison emits zero shift/reduce or
      reduce/reduce conflicts.

      **Helpers added** (epilogue):
        sc_emit_label_pad(st, name)   — append label-only no-op stmt
        sc_append_goto_label(st, tgt) — append :(tgt) bare goto stmt

      Both reuse the existing sc_make_label_stmt /
      sc_make_goto_uncond_stmt / sc_append_chain machinery.

      **Test gate** `scripts/test_smoke_snocone_parse_i.sh` runs
      `test/frontend/snocone/test_snocone_parse_i.c` — 15 test
      functions / **108/108 PASS**.  Coverage: bare goto, goto in
      sequence, label before assign, label+goto loop, label before
      block, label before if (synthetic `_Lend` follows user label),
      label before while (user label sits before synthetic `_Ltop`
      pad — chain semantics preserved), multiple goto targets,
      stacked labels (`first: second: x = 1;` — recursive label_decl
      rule), label before empty stmt, label inside function body
      (between function entry-point label and body stmts), label
      with preceding stmts (splice integrity), label whitespace
      variants (`L:`, `L :`, `L  :  `, `L :x` all OK), goto
      whitespace variants, label inside while body (correct
      placement after synthetic cond stmt).  Combined parse gates
      **776/776** (was 668/668).

      All production gates green: smoke snocone 5/5, beauty 3-mode
      42/0/3, unified broker 49/0.  Bison emitted zero shift/reduce
      and zero reduce/reduce conflicts.

      Side-channel only — LS-4.j wires the new parser into scrip's
      production driver.

- [ ] LS-4.i.2 — `break;` / `break LABEL;` / `continue;` /
      `continue LABEL;`.  Per Q13 default placeholder: Option A
      (both plain and labeled forms accepted), pending Lon's pick.
      Plain `break;` exits innermost enclosing loop or switch;
      `break LABEL;` exits the loop/switch tagged by user label.
      Same for continue (innermost loop only — switch/case has no
      continue target).  Lowering uses a "loop stack" in
      ScParseState that is pushed at each while/do/for/switch head
      and popped at finalize; each entry carries the synthetic
      end-label (for break) and top-label (for continue), plus the
      user label (if any) attached just before the loop.  `break`
      without an enclosing loop or switch is a parse-time error;
      `continue` without an enclosing loop is also an error.

      **Session 2026-05-01 #2 (EMERGENCY HANDOFF — implementation
      landed and gate-green; side-channel test extension is the
      remaining work):**

      Lon's session-#2 directive: Q13 → Option A (both plain and
      labeled forms accepted).  Implementation lands in
      `snocone_parse.y` only — no other source touched.

      **Implementation shape (committed in this handoff, all gates
      green throughout):**

      Grammar additions in `simple_stmt`:
      ```
      | T_BREAK T_SEMICOLON              { sc_append_break(st, NULL);  }
      | T_BREAK T_IDENT T_SEMICOLON      { sc_append_break(st, $2);    }
      | T_CONTINUE T_SEMICOLON           { sc_append_continue(st, NULL); }
      | T_CONTINUE T_IDENT T_SEMICOLON   { sc_append_continue(st, $2); }
      ```
      Plus a tiny `for_lead : T_FOR { sc_pending_to_stash(st); }`
      non-terminal that fires before init parses, moving any
      pending user labels to a one-slot stash.  This is needed
      because init's `sc_append_stmt` call would otherwise clear
      pending before `sc_for_head_new` could capture them onto the
      loop frame.  (For while/do, the head action runs before any
      stmt commit; pending is alive there.)  `for_head` was
      reshaped to consume `for_lead` as its first symbol.

      `LoopFrame` struct + linked-list stack rooted at
      `ScParseState.loop_top`:
      ```c
      typedef struct LoopFrame {
          char    *cont_label;      /* continue target */
          char    *end_label;       /* break target    */
          char   **user_labels;     /* labels attached at loop entry */
          int      user_labels_count;
          int      is_loop;         /* 0=switch (LS-4.i.3); 1=loop */
          int      cont_used;       /* lazy-emit flag — see below */
          struct LoopFrame *outer;
      } LoopFrame;
      ```

      Eager label allocation in `sc_while_head_new` /
      `sc_do_head_new` / `sc_for_head_new` — each head now also
      allocates `cont_label` and `end_label` up front, stores them
      on its head struct, and pushes a `LoopFrame` carrying
      `strdup`'d copies of those labels.  `sc_finalize_*` reuses
      the head's `cont_label` / `end_label` so any `break`/
      `continue` stmts emitted DURING body parsing target the same
      label names the finalize lays down.  Each finalize calls
      `sc_loop_pop`.  For while loops, `cont_label` is the same
      `_Ltop_NNNN` always emitted, so no separate `Lcont` pad is
      needed.  For do/while and for, `cont_label` is a separate
      `_Lcont_NNNN` that finalize splices in just before the cond
      stmt (do/while) or just before the step stmt (for) — but
      lazy-emit: only spliced when the body actually emitted a
      `continue` (`cont_used` flag set by `sc_append_continue`).
      This preserves the exact LS-4.f/g lowering shape for code
      that doesn't use continue, keeping all 95 existing parse-g
      tests green without modification.

      Pending-user-label tracking: `sc_emit_label_pad` (called
      from `label_decl`'s action) was extended to call
      `sc_pending_label_add` after emitting the pad.  Stacked
      labels (`a: b: while(...)`) accumulate — both `a` and `b`
      attach to the same loop frame, so `break a;` and `break b;`
      both work (Java-style).  `sc_append_stmt`,
      `sc_append_return`, `sc_append_freturn`, `sc_append_nreturn`,
      `sc_append_goto_label` all clear pending at entry — they
      consume any preceding label.  Head functions consume-and-
      clear pending into the loop frame's `user_labels[]` array.

      `sc_loop_find_by_user_label` walks innermost-first; switch
      frames are skipped when `want_loop=1` (continue case).
      `sc_loop_find_innermost` handles the unlabeled case.

      `sc_append_break` / `sc_append_continue` — emit a bare goto
      to the resolved frame's end/cont label.  Out-of-context
      (`break;` at top level, etc.) and unresolved-label cases
      call `sc_error` and emit nothing.

      `snocone_parse_program` got a cleanup pass: drains pending,
      stash, and any leftover loop frames before returning.

      **Gate state at handoff (all green, zero regressions):**
      ```
      smoke snocone:               5/5
      beauty 3-mode:               42/0/3
      unified broker:              49/0
      parse-a..i (side-channel):   776/776 (35+119+66+79+71+118+95+85+108)
      FSM lex acceptance:          31/31
      Bison conflicts:             0 shift/reduce, 0 reduce/reduce
      ```
      LS-4.i.1's 108 parse-i tests remain unchanged (LS-4.i.2
      added zero new tests in `test_snocone_parse_i.c` — that's
      the work session #3 needs to do).

      **End-to-end smoke verification at handoff (saved as
      `docs/LS-4.i.2-session-2026-05-01-smoke-driver.c`):**
      Five hand-built smoke cases, all pass:

      1. Bare `break;` and `continue;` in single while-loop —
         `break;` lowers to `:(_Lend_NNNN)` of innermost, `continue;`
         to `:(_Ltop_NNNN)` of innermost (same as while's back-edge
         label, so no extra pad emitted).
      2. Labeled `break outer;` and `continue outer;` from nested
         inner loop targeting outer-loop labels — both gotos
         correctly reference the outer frame's end/cont labels.
      3. `break;` at top level — parse fails with sc_error
         "break outside of loop or switch".
      4. `for (...) { ... continue; ... }` — `_Lcont_NNNN` pad is
         emitted (lazy-emit triggered by `cont_used=1`).
      5. `for (...) { ... }` without continue — no `_Lcont_*` label
         appears in the IR (lazy-emit suppressed).

      **What's left for session #3 to close LS-4.i.2:**

      Write ~12-15 ASSERT-based test functions in
      `test/frontend/snocone/test_snocone_parse_i.c` covering the
      same shapes the smoke driver verifies, plus:
      - bare break/continue in while, do/while, for
      - labeled break/continue, single level of nesting and two
        levels
      - stacked labels (`a: b: while(...)` — break a; AND break b;
        both targeting same loop)
      - Lcont-pad lazy-emit for do/while+continue and for+continue
      - Lcont-pad SUPPRESSED for do/while-no-continue and for-no-
        continue (parse-g shape preserved)
      - the "label-on-non-loop-stmt followed by loop" disambiguation
        (`a: x = 1; while(...) {...}` — `a` attaches to assignment,
        not to loop; pending cleared by sc_append_stmt)
      - Error cases — break outside loop, continue outside loop,
        break/continue with unresolved labels — all should yield
        snocone_parse_program returning NULL with nerrors > 0.

      Use the existing parse-i test functions as templates.  The
      `test_smoke_snocone_parse_i.sh` runner is already in place
      and needs no changes.

      Reference smoke driver in `docs/` provides exact expected
      label-name shapes (`_Ltop_0001`, `_Lend_0002`, `_Lcont_NNNN`)
      and demonstrates working ASSERT idioms for label-target
      checking.  Builds & runs in <1s.

      Smoke verification command for session #3 to confirm baseline
      before adding tests:
      ```bash
      cc -Wall -o /tmp/ls4i2_smoke \
          docs/LS-4.i.2-session-2026-05-01-smoke-driver.c \
          src/frontend/snocone/snocone_parse.tab.c \
          src/frontend/snocone/snocone_lex.c \
          -I src/frontend/snocone -I src/frontend/snobol4 -I src
      /tmp/ls4i2_smoke   # expect "ALL SMOKE CHECKS PASSED"
      ```

      one4all working tree CLEAN at HEAD `10a7bf03`.

- [ ] LS-4.i.3 — `switch (e) { case v1: S1; case v2: S2; default: SD; }`.
      Lowers to:
          tmp = e
          IDENT(tmp, v1)  :S(c1)
          IDENT(tmp, v2)  :S(c2)
                          :(cd)
        c1  S1  :(after)
        c2  S2  :(after)
        cd  SD
        after
      Each case body falls through to the next case implicitly;
      explicit `break;` is needed for non-fall-through (Q6).

- [ ] LS-4.i.4 — Alt-eval `(a, b, c)` → `E_VLIST`.  Pure expression-
      tier change at expr0 / paren-grouping.  When a comma-separated
      list of expressions appears inside parens at top level,
      construct an n-ary `E_VLIST` node.  The SPITBOL backend can
      pass it through verbatim; non-SPITBOL backends lower to a
      chain of `:S(after)` branches.

- [ ] LS-4.i.5 — `struct NAME { field, field, ... };`.  Andrew's
      `.sc` line 162 has this — a struct keyword that defines a
      named record with a list of fields.  Lowers to per-field
      accessor function definitions following SPITBOL's TABLE
      idiom, or directly to PROTOTYPE/DATA.  Smallest scope —
      defer to last so the four control-flow sub-steps land first.

- [ ] LS-4.j — Wire-in only.  Add `snocone_parse.tab.c` to
      `src/Makefile` `FRONTEND_SNOCONE` (matching `FRONTEND_SNO`'s
      shape).  Collapse `snocone_compile()` to a thin wrapper
      around `snocone_parse_program()` (~5 lines — mirror
      `sno_parse_string()` at `snobol4.y:316`).  Snocone block in
      `regenerate_parser_and_lexer_from_sources.sh` already added
      in LS-4.a (session 2026-04-30 #3 — cosmetic pull-forward,
      only generates `.tab.c`/`.tab.h` since the lexer is the
      hand-written FSM, not Flex).
      **No file deletions in this step.**  The legacy archive
      files are still on disk and still referenced by
      `snocone_lower.c`/`snocone_control.c` — those go in LS-4.k.
      Goal of LS-4.j: the Bison parser path becomes the production
      path; the legacy parser path becomes dead code (unreached
      but still compiled).  Smoke gate green at end of LS-4.j
      using the new parser.

- [ ] LS-4.k — **Junk cleanup — by moving to archive, not deleting.**
      Now that LS-4.j has the new Bison parser wired into
      `snocone_compile()`, the legacy shunting-yard parser path is
      dead code in the live tree.  Move it out of `src/` into
      `archive/`, alongside the legacy lexer/parser already moved
      there in LS-4.a.

      **Files moved (`git mv` to preserve history):**
      - `src/frontend/snocone/snocone_lower.c` →
        `archive/snocone_lower.c`
      - `src/frontend/snocone/snocone_lower.h` →
        `archive/snocone_lower.h`
      - `src/frontend/snocone/snocone_control.c` →
        `archive/snocone_control.c`
      - `src/frontend/snocone/snocone_control.h` →
        `archive/snocone_control.h`

      These are the Sprint-SC1 token-stream-to-IR lowerer and the
      compile-driver glue that the archived hand-written parser
      fed into.  They are dead code in the live tree once LS-4.j
      points `snocone_compile()` at the Bison parser, but they
      are working code with real history — exactly what the
      `archive/` directory is for.

      **No `.c` or `.h` files are deleted.**  Same principle that
      LS-4.a applied to the legacy lexer/parser: *move to archive,
      never delete*.  The archive is the historical record.  An
      archive is for preservation; deletion would unmake the
      record.

      **Other edits in the same commit:**
      - `src/Makefile`: drop the four `FRONTEND_SNOCONE` lines
        feeding `../archive/snocone_lex.c`,
        `../archive/snocone_parse.c`,
        `frontend/snocone/snocone_lower.c`, and
        `frontend/snocone/snocone_control.c` into the build.
        After this, `FRONTEND_SNOCONE` references only the live
        `src/frontend/snocone/` files: `snocone_lex.c`,
        `snocone_parse.tab.c`, `snocone_driver.c`.
      - `archive/snocone_lex.c`: revert the LS-4.h
        `{ "function", SNOCONE_KW_PROCEDURE }` keyword-table
        synonym entry.  That edit existed only to keep the
        production smoke green while the archive was still in
        the build path.  Once LS-4.j unwires the archive from
        the build, the synonym is moot, and reverting restores
        the archived file to byte-equivalence with what was
        archived in LS-4.a.
      - `src/frontend/snocone/snocone_lex.h:15` doc-comment
        mentioning `one4all/archive/snocone_lex.c` — leave as
        is; it correctly describes legitimate history (the FSM
        replaced what is now in the archive).

      **Files NOT touched** (this list exists so future sessions
      don't repeat the deletion mistake from session #13's first
      LS-4.k draft):
      - `archive/snocone_lex.{c,h}`, `archive/snocone_parse.{c,h}`
        — kept verbatim as the historical record (modulo the
        LS-4.h synonym revert above).  Lon's correction this
        session: "why would you delete a file from the archive?
        Is that the archive archive, the trash?"  Answer: no —
        the archive is for preservation, period.
      - `archive/snocone_lower.{c,h}`, `archive/snocone_control.{c,h}`
        — these are the four files just moved here by this very
        step.  After they arrive, they stay.
      - `docs/LS-4-session-2026-04-30-1-attempt.snocone.y` —
        kept; saved attempt for reference per RULES.md
        diagnostic-patches-stay-in-docs convention.
      - `docs/LS-4-session-2026-04-30-1-findings.md` — kept;
        architectural findings prose.

      **Invariant at end of LS-4.k:** zero references to
      `archive/snocone` from `src/Makefile`, `src/`, `scripts/`,
      or `test/`.  Verify with:

          grep -rn 'archive/snocone' src/Makefile src/ scripts/ test/
          ls src/frontend/snocone/snocone_lower.* \
             src/frontend/snocone/snocone_control.* 2>/dev/null

      Both commands must return empty.  And the archive
      directory grows by four files, preserving everything that
      was working code.  Build still succeeds and all gates
      remain green:
      - smoke snocone:        5/5
      - beauty 3-mode:        42/0/3
      - unified broker:       49/0
      - parse-a..i:           ≥668/668 (whatever LS-4.i grew to)
      - FSM lex acceptance:   31/31

      **Why LS-4.k is its own step:** the move is mechanical
      but the rename diff touches every callsite that
      `#include`d the moved headers.  Keeping it separate from
      LS-4.j makes the two diffs reviewable individually —
      LS-4.j shows the new parser taking over, LS-4.k shows the
      dead glue moving from `src/` into `archive/`.  Either step
      can be reverted independently if a regression surfaces.

      **Why move-not-delete:** the archive is the project's
      record of working code that no longer fits the live
      build.  Deletion loses that record.  `git log` preserves
      *changes*, but the archive preserves *the file at the
      moment it left the live tree* in a place where someone
      can still `cat` or `grep` it without spelunking through
      git history.  That's the whole point of having an
      `archive/` directory.

- [ ] LS-4.l — Final gate confirmation after LS-4.j + LS-4.k.
      `test_smoke_snocone.sh` PASS=5 (using the new Bison
      parser, no legacy fallback).  `test_smoke_unified_broker.sh`
      PASS=49+ FAIL=0.  `test_beauty_snocone_all_modes.sh`
      PASS=42 FAIL=0 SKIP=3.  Combined parse-a..i gates
      ≥668/668.  This is the rung that closes "LS-4 the new
      Snocone front-end is the only Snocone front-end."

- [ ] LS-4.w — Condition-never-fails warning pass (deferred, low priority).
      At lowering time, inspect the condition expression of every `if`,
      `while`, `do/while`, `do/until`, `for`-test, and `case` tag.
      If the condition is a bare `E_VAR` or `E_KEYWORD` node (no operator,
      no pattern match, no function call) emit a compiler warning:
        `warning: condition 'c' is a variable reference and can never fail`
      (because a bound SNOBOL4 name always succeeds with its value).
      Function calls are NOT warned — `if (func())` is legitimate since
      the called function may return failure.  Operator expressions
      (`GT(x,0)`, `x ? pat`, `s :: t`, etc.) are NOT warned for the
      same reason.  Implementation: a small `sc_cond_warn(Expr *e,
      const char *loc)` helper called from each lowering site that
      emits reduces to a single `E_VAR`/`E_KEYWORD` check — one-liner
      per call site.  Warning is printed to stderr; compilation
      continues normally (never fatal).  No new test gate required
      at this step — existing smoke/beauty/broker gates cover
      regression; a handful of manual spot-checks suffice.

**Architectural lesson recorded** (`docs/LS-4-session-2026-04-30-1-findings.md`):
the two-pass design (lex into buffer, then parse from buffer) felt
natural for testing in LS-3.c but creates an unnecessary impedance
mismatch at LS-4 — a thunk that translates one enum to another, plus
a `ScParseState` that owns a buffer cursor instead of letting Flex
own its scanner state.  Single-pass Flex→Bison via the standard
`yylex` API is one4all's established convention; Snocone matches.

**Saved attempt** (session 2026-04-30 #1):
`docs/LS-4-session-2026-04-30-1-attempt.snocone.y` — ~870-line draft
showing IR-construction semantic actions correctly (those port
unchanged into the proper single-pass design); only the lex/parse
plumbing was wrong.  Not committed to the source tree (`src/frontend/
snocone/` clean).

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

