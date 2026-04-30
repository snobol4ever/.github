# GOAL-SNOCONE-LANG-SPACE — Andrew's Final Snocone Vision + Lon's SPITBOL Space Restoration

**Repo:** one4all + corpus
**Working repo/build name:** `snocone` (no rename committed — see Naming notes below)
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
     `procedure name(args) {…}`, `return E;`, `freturn;`,
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

## Naming — open

Lon (session #4): "The name is not now SNOBOL6 nor will it likely
be.  We just have ideas is all."

The working repo/build name remains **`snocone`** through this
goal and likely beyond.  The name of the language itself is
unsettled.  Naming ideas explored in earlier sessions and not
selected:

- **SNOBOL6** — the joke version: SNOBOL4 was the line-by-line
  one missing structured control, SNOBOL5 is Gimpel's never-shipped
  successor, SNOBOL6 is the structured-control reboot picking up
  where 5 left off.  Funny but not a commitment.
- **Snocone** (Andrew's name) — historical resonance, but this is
  Andrew's-final-vision-plus-Lon's-restoration, not a clone.

Not selected.  No rename happens during this goal.  When and if a
name lands, a separate dedicated rename goal handles the source-
tree sweep cleanly.

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
| `if`/`else`/`while`/`do`/`for`/`procedure`/`return` etc. | C-style structured control | adopted unchanged |
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
  `for`/`procedure`/`return`/`{`/`}`/`;`).
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

### Q10. Language name — open (no commitment)

Lon session #1: "We will do Snocone different from Andrew Koenig.
We might later find a better name."

Lon session #3: "The new name would be funny if it was SNOBOL6
since all that was bad with SNOBOL4 as the line by line thing
and missing structured control.  And SNOBOL5 already exists."

Lon session #4: "The name is not now SNOBOL6 nor will it likely
be.  We just have ideas is all."

**Status:** open.  No name committed.  Working repo/build name
remains `snocone` indefinitely.  When and if a name lands, a
separate dedicated rename goal handles the source-tree sweep.

### Q11. Rename source tree — moot until Q10 lands

When and if Q10 picks a name, this question opens.  Until then:
no rename, no source-tree sweep, no file-extension change.

### Q12. Identity-op spelling — RESOLVED to `::` and `:!:` (session #4)

Andrew Koenig's `.sc` self-host source already defines them at
lines 45–46:

```snocone
bconv['::']  = binfo('IDENT', 6, 6, 0, 0, 1)
bconv[':!:'] = binfo('DIFFER', 6, 6, 0, 0, 1)
```

These are **Andrew's choices**, in his canonical self-host
source.  We adopt them verbatim.

The session-#3 ambiguity ("Let's keep `::` and `:!:` I suppose
for IDENT and DIFFER") is resolved here: Lon was directing us to
preserve what Andrew already had in his self-host, not invent
new spellings.  This Goal file's title was therefore correct to
say "Andrew's final vision plus space restoration."  The `.sno`
bootstrap source we examined first did not have `::`/`:!:`; the
`.sc` self-host does.  The `.sc` is the canonical Andrew source.

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

