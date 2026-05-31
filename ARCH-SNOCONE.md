# ARCH-SNOCONE.md — Snocone Frontend & Language Spec

This is the single source of truth for Snocone — both the language
spec (surface syntax, operator semantics, statement structure) and
the architecture (lexer / grammar / driver implementation map). All
other Snocone documentation in this repo is either a one-line
pointer to this file or has been removed.

**Reference spec for expression semantics:** SPITBOL Manual v3.7 by
Mark B. Emmer and Edward K. Quillen (Catspaw, 2000) — 368 pages.
Snocone expression syntax and semantics are 100% identical to SPITBOL;
the only differences are control flow (C-style braces vs label-goto)
and newline-as-whitespace. Chapters 15 (Operators), 17 (Data Types),
18 (Patterns), and 19 (Functions) are authoritative for what Snocone
expressions mean. Frontends and runtimes never reinterpret these.

Frontend: SNOCONE. Produces shared IR (EXPR_t/STMT_t). See ARCH-IR.md.

---

## In one sentence

> Snocone is **Andrew Koenig's `.sc` self-host operator set, minus
> `&&` / `||` / `%`, plus C-style structured control flow, plus
> SPITBOL space-as-concat.**

A SPITBOL program that does not itself use `&&`, `||`, or `%` as
binary operators, and that uses `;` statement terminators with
`name:` label syntax (not column-1 labels), runs unchanged under
Snocone. **This functional-superset guarantee is a hard invariant.**

---

## Operator tables

### Binary operators (highest priority first — SPITBOL Manual Ch.15)

| Op       | Assoc  | Pri | Definition                               |
|----------|--------|-----|------------------------------------------|
| `=`      | right  |  0  | Assignment                                |
| `?`      | left   |  1  | Pattern match                             |
| `\|`     | right  |  3  | Pattern alternation                       |
| *space*  | right  |  4  | **Concatenation or match** (synthetic `T_CONCAT` token from lexer) |
| `+`      | left   |  6  | Addition                                  |
| `-`      | left   |  6  | Subtraction                               |
| `/`      | left   |  8  | Division                                  |
| `*`      | left   |  9  | Multiplication                            |
| `^` `!` `**` | right | 11 | Exponentiation                          |
| `$`      | left   | 12  | Immediate assignment (in pattern context) |
| `.`      | left   | 12  | Conditional assignment (in pattern ctx)   |

### Comparison-operator sugar (priority 6, all lower to function calls)

| Snocone surface | Lowers to |
|---|---|
| `==` `!=` `<` `<=` `>` `>=` | `EQ()` `NE()` `LT()` `LE()` `GT()` `GE()` (numeric) |
| `:==:` `:!=:` `:<:` `:<=:` `:>:` `:>=:` | `LEQ()` `LNE()` `LLT()` `LLE()` `LGT()` `LGE()` (lexical) |
| `::` `:!:` | `IDENT()` `DIFFER()` (identity — Andrew `.sc` lines 45–46) |

### Undefined binary operators (available for `OPSYN`)

| Op | Assoc | Pri |
|----|-------|-----|
| `&` | left  |  2  |
| `@` | right |  5  |
| `#` | left  |  7  |
| `%` | left  | 10  |
| `~` | right | 13  |

The lexer emits these as plain tokens; the grammar routes them
through the OPSYN catch-all production. **`%` was previously
Andrew's modulo (lowering to `REMDR()`); it is now reserved as a
user-OPSYN slot. Programs needing remainder write `REMDR(a, b)`
directly.**

### Unary operators (all equal priority, higher than any binary, right-to-left)

| Op | Name           | Definition                                     |
|----|----------------|------------------------------------------------|
| `@` | at sign       | Assigns cursor position to its operand          |
| `~` | tilde         | Negates failure or success of its operand       |
| `?` | question mark | Interrogation — returns null if operand succeeds|
| `&` | ampersand     | Keyword (with **zero-space**: `&IDENT` is one `KEYWORD_NAME` token) |
| `+` | plus          | Indicates positive numeric operand               |
| `-` | minus         | Negates numeric operand                          |
| `*` | asterisk      | Defers evaluation of expression                  |
| `$` | dollar sign   | Indirection                                      |
| `.` | period, dot   | Returns a name                                   |

Undefined unary operators (available for `OPSYN`):
`!` `%` `/` `#` `=` `|`

### Dual-role operator disambiguation rule

The dual-role unary/binary operators (`& | ? $ . + - * / ^ ! @ # % ~`)
are **binary only when {W}OP{W}** — both sides whitespace. Without
right-side whitespace they are unary.

This is the SPITBOL/SNOBOL4 rule. Concretely:

- `2 * 3` (whitespace both sides) → binary multiply
- `A *B` (whitespace left only) → concat A with unary defer of B
- `*W` (no whitespace, expression start) → unary defer
- `1*2` (no whitespace either side) → **syntax error**, matching SPITBOL Error 231

The implementation enforces this rule consistently for all dual-role
operators including `+` `-` `*` `/` `^` — see GOAL-SNOCONE-BEAUTY
SB-6.E for the rung that landed this. `^` has no unary form (the
unary operator set is `+ - * & @ ~ ? . $`), so a tight or
unary-position `^` is a syntax error.

`!` is dual-role in a different way: defined-binary
(exponentiation, alternate spelling for `^` and `**`, priority 11)
AND undefined-unary (OPSYN-available, like `% / # = |`). The lexer's
binary cascade for `!` already follows the strict `{W}!{W}` rule;
the unary-position emit is tracked under SB-6.F (currently the
fallback collapses to `T_2CARET` instead of the correct `T_1BANG` —
narrow lexer-only fix, does not gate SB-6 self-host).

---

## Concatenation — whitespace IS the concat operator

Whitespace between two value-yielding tokens IS the concat operator.
The lexer emits a synthetic `T_CONCAT` token at the boundary; the
grammar treats it as a normal binary operator at SPITBOL priority 4,
right-associative.

```snocone
x = 'foo' 'bar';        // assigns 'foobar'
x = a /* comment */ b;  // concat across the comment — comments are whitespace
```

The lexer suppresses `T_CONCAT` injection before any token that
could be a binary operator (`.`, `$`, `+`, `-`, `*`, `?`, `&`, `~`,
`@`). Those tokens are left for the grammar to disambiguate via the
{W}OP{W} rule above.

---

## `f(x)` vs `f (x)` — the zero-space rule

`f(args)` with **zero whitespace** between the identifier and `(`
is a function call. `f (expr)` with one or more whitespace chars
between is `f` concat `(expr)`. Strict — same SPITBOL rule, enforced
by the lexer via the `IDENT_LPAREN_NOSP` token.

```snocone
result = f(x);          // call f with argument x
result = f (x);         // concat the value of f with the value of x
result = f /* */ (x);   // also concat — the comment is whitespace
```

---

## `&IDENT` — the keyword-name token

`&` followed by an identifier with **zero whitespace** is a keyword
reference (e.g. `&FULLSCAN`, `&UCASE`, `&ANCHOR`). Single `KEYWORD_NAME`
token carrying the full sequence.

If `& IDENT` (whitespace), the `&` becomes unary `AMPERSAND` followed
by `IDENT` — almost certainly a syntax error.

---

## Conditions are SPITBOL backtracking expressions

Not C-style booleans. The parenthesised condition of `if`, `while`,
`do/while`, `for`-test, and `case` tag is a single SPITBOL
backtracking expression. The success/failure exit drives the branch.

```snocone
if (subj ? pat = repl) {
    // match succeeded; subj has been mutated by the replacement
}

while (subj ? BREAK(',') . token ' ' = '') {
    // each iteration extracts the next comma-delimited token
}
```

A bare variable reference always succeeds (a bound name has a value).
`if (x)` therefore always takes the success branch — no truthy/falsy
semantics. The LS-4.w warning pass is a deferred TODO that would
flag this as "condition can never fail," but the construct is not an
error.

**Boolean AND is juxtaposition, not `&` or `&&`.** Inside `if (...)`,
`while (...)`, etc., write `if (IDENT(t(x), 'E_FNC') IDENT(v(x), ','))`
to mean "both predicates succeed" — they are concatenated in
backtracking-expression context. Using `&` is a syntax error
(documented session 2026-05-03 PARSER-PR-3 attempt). Boolean OR is
the alternation operator `|`.

---

## Statement boundary is `;` only — newlines are whitespace

Every Snocone statement ends with `;`. Newlines, tabs, and spaces
are all whitespace; the lexer treats them identically. There is no
implicit semicolon at end of line, no continuation token, no
off-side rule.

`x = 1\ny = 2;` is **one statement** (the expression `x = 1 y = 2`,
which evaluates `1 y = 2` as a chain and assigns to `x`, almost
certainly not what was meant). Programs that omit `;` produce
surprising parses, not error messages. This is by design.

(For one-statement-per-line readability, source files conventionally
write each statement on its own line with `;` at the end — but the
parser does not care.)

---

## Bare expression statements may fail silently

A statement that is just `expr;` with no surrounding control flow
lowers to a bare SPITBOL statement with no `:S(...)F(...)`
decoration. If it fails, control falls through to the next
statement.

```snocone
EQ(x, y);          // succeeds or fails; either way, next stmt runs
GT(x, 0)  x = -x;  // negate x if positive (succeed-and-side-effect idiom)
```

This is the SNOBOL4 default — failure-as-control-flow is reserved
for the parenthesised conditions listed above.

---

## Multi-line continuation — `+` / `.` at column 1

SNOBOL4-style continuation: when the next physical line's column 1
is `+` or `.`, the line is glued onto the previous one. The
continuation counts as whitespace for the CONCAT rule.

```snocone
   x = 'foo'
+         'bar'
```

emits `IDENT(x) ASSIGN STRING('foo') CONCAT STRING('bar')`. The
continuation is transparent.

---

## Comments

`// to end of line` and `/* ... */` block comments. Both count as
whitespace for the CONCAT rule. Block comments are non-nesting and
may span newlines.

```snocone
   x = 'foo' /* hello */ 'bar'
```

emits `IDENT(x) ASSIGN STRING('foo') CONCAT STRING('bar')` — the
comment is a whitespace gap, CONCAT fires across it.

---

## String literals — the SNOBOL4 rule, no escapes

A string starts with `'` or `"`. Body is everything up to the
matching delimiter. **Backslash is NOT an escape character.** To
embed a quote, use the other delimiter (`"can't"` or `'a"b'`), or
build via `CHAR(39)` etc. Newlines inside strings are not permitted.

---

## Identifiers

`[A-Za-z_][A-Za-z0-9_]*` — Andrew's `.sc` uses `_` for compound
names (`cl_type`, `or_binfo`). SNOBOL4 source-style names with `.`
(`cl.type`) are NOT identifiers in Snocone — they lex as `IDENT(cl)
PERIOD IDENT(type)`.

Snocone is **case-sensitive byte-for-byte** (per `RULES.md` "Case-
sensitive name space"). The lexer keeps the byte sequence the user
wrote — no folding at lex time.

---

## Control flow

C-style structured control. Block braces `{` `}` around every body.

```snocone
if (cond) { ... }
if (cond) { ... } else { ... }

while (cond) { ... }
do { ... } while (cond);            // do/while only — do/until removed

for (init; test; step) { ... }      // semicolons (Andrew used commas)

switch (e) {
    case v1: ... ;
    case v2: ... ;
    default: ... ;
}                                   // no fall-through; implicit break at end of each case

break;
break LABEL;                        // labeled break
continue;
continue LABEL;                     // labeled continue

goto LABEL;                         // single keyword (not Andrew's two-word `go to`)
LABEL: stmt                         // label clause; can stack: L1: L2: stmt
```

`goto` is the escape hatch for any control-flow shape the
structured forms don't cover — labeled-break out of nested loops,
state-machine dispatch, retry-from-error. Using it for ordinary
control flow is discouraged.

### Lowering map

| Snocone source            | SNOBOL4-IR equivalent                             |
|---------------------------|---------------------------------------------------|
| `expr;`  (bare statement) | emit `expr` as bare SPITBOL statement; failure is silent fall-through |
| `name : stmt`             | emit `name` at column 1 before lowered `stmt`     |
| `goto name;`              | append `:(name)` to current statement, or emit empty `:(name)` clause |
| `if (cond) S1`            | `cond  :F(after)` `S1` `after  ...`               |
| `if (cond) S1 else S2`    | `cond  :F(else)` `S1  :(after)` `else  S2` `after  ...` |
| `while (cond) S`          | `top  cond  :F(after)` `S  :(top)` `after  ...`   |
| `do S while (cond);`      | `top  S` `cond  :S(top)`                          |
| `for (init; cond; step) S`| `init` `top  cond  :F(after)` `S` `step  :(top)` `after  ...` |
| `switch(e){case v: S; ..}`| see "switch backends" below — chain or table |
| `break;` / `break LABEL;` | `:(after-of-innermost-or-labeled-loop-or-switch)` |
| `continue;` / `continue LABEL;` | `:(top-of-innermost-or-labeled-loop)`       |
| `(e1, e2, e3)` (alt-eval) | SPITBOL extension — emit as-is to SPITBOL backend; for non-SPITBOL backends, lower to a chain of `:S(after)` branches |

### Switch backends — chain vs label-table (compile-time selectable)

**Status:** open design idea (Lon, session 2026-05-02 #6). Not yet
implemented. See `GOAL-SNOCONE-SWITCH-BACKENDS.md` for the working
goal and milestones.

**Motivation.** `switch` over a string discriminator is the natural
target for SNOBOL4-style polymorphic dispatch — `:S($('pp_' t))F(...)`
in `beauty.sno` is a 30+ way string switch. Today's lowering is a
single shape: an if/else-if chain (per the `IDENT(e, v) :S(caseN)`
row in the lowering map). That's the right answer for small case
counts and the wrong answer for a 30-way dispatch in a hot loop.

**Two backends, one source language.**

1. **`chain`** — current behavior. Lowers to a sequence of
   `IDENT(e, vK)  :S(caseK)` followed by a default fallthrough. O(n)
   compares per dispatch. Wins for ≤ ~4 cases, smallest code, best
   branch-predictor behavior when one case dominates, and for cases
   over heterogeneous types or non-literal values.

2. **`table`** — perfect-hash jump table on the case literals.
   Compiler builds the hash at compile time (gperf-style) keyed on
   the literal case strings. Dispatch is one hash + one compare +
   one indirect branch. O(1). Wins for dense or large case sets,
   especially the polymorphic-AST-dispatch idiom. Requires every
   case label to be a compile-time literal of the same scalar type
   (string or integer); falls back to `chain` when any case violates
   that.

**Compile-time selection — three layers, narrowest wins:**

| Layer | Form | Scope |
|-------|------|-------|
| Per-site | `switch [[table]] (e) { ... }` / `switch [[chain]] (e) { ... }` | one switch only |
| File-level | `#pragma snocone switch=table` near top of file | rest of file |
| Driver flag | `--switch-style=chain\|table\|auto` on `scrip` | whole compile |

`auto` is the recommended default: choose `table` when (a) ≥ N cases
(N=5 is a sensible starting threshold) and (b) every case is a
compile-time string-or-integer literal of the same type. Otherwise
`chain`. The threshold lives in one place in the lowering pass and
is tunable.

**IR considerations.** The shared IR (`ir.h`) doesn't need a new
EKind — both backends lower to existing primitives. `chain` emits
the same sequence it does today. `table` emits a new lowering shape
in `sm_lower.c` (and per-backend equivalents in JVM/.NET/JS/WASM):
a constant table holding `(hash_key, label)` pairs plus a small
preamble computing `hash(e)` and indexing the table. The hash table
itself is data, not IR. No frontend changes beyond the optional
`[[chain|table]]` attribute parse.

**Why this matters for SNOBOL4-style dispatch.** `beauty.sno::pp`
and `beauty.sno::ss` each dispatch on tree-node-type strings (30+
distinct values). Today's `if/else-if` Snocone port (which is what
the chain lowering produces) is both slow and a fertile source of
copy-paste bugs (see SB-6.E.7 audit findings — beauty.sc had three
identical broken `if` conditions in `pp()`). A `table`-lowered
`switch` is faster and removes the entire class of "I copy-pasted
case 7 from case 6 and forgot to change the constant" bugs. The
source becomes:

```snocone
switch [[table]] (t) {
    case 'snoBuiltinVar': ppLeaf(x, t); break;
    case 'snoFunction':   ppLeaf(x, t); break;
    ...
    case 'snoComment':    SetLevel(0); GenSetCont(); Gen(v(c[1]) nl); break;
    default: error();
}
```

That **is** the original `:S($('pp_' t))` idiom expressed in
structured Snocone. The compiler then chooses chain or table based
on the heuristic.

---

## Functions

```snocone
function name (param1, param2) local1, local2 {
    ...
    return E;         // value via E (lowers to `name = E :(RETURN)`)
    return;           // bare `:(RETURN)`
    nreturn;          // pattern/name return — `:(NRETURN)`
    freturn;          // failure — `:(FRETURN)`
}
```

Statement terminator `;` is mandatory. Locals can be declared with
commas after the parameter list (canonical) or folded into the
parameter list with a comma separator (scrip dialect — both forms
accepted).

The keyword is `function`, not Andrew's `procedure` (rename per
LS-4.h, Lon session #7 — these forms return a value, name matches
role).

Lowering of `function name(args)`: emits `DEFINE('name(args)')
:(name_end)` then label `name` on body's first stmt then `name_end`
pad.

---

## `struct` declarations

Andrew's `.sc` line 162 self-host extension, adopted verbatim:

```snocone
struct NAME { f1, f2, f3 }          // no trailing `;`
```

Lowers to single bare-expression statement `DATA('NAME(f1,f2,f3)')`.
SPITBOL's `DATA()` installs the constructor plus per-field
accessors (each accessor doubling as an L-value).

---

## Alternative-evaluation `(e1, e2, e3)`

SPITBOL extension (Manual Ch.15 footnote): a parenthesised list of
expressions separated by `,` is evaluated left to right; the value
of the first to succeed is the value of the whole. If all fail,
`(...)` fails.

```snocone
result = (LT(I, J) I, GT(I, J) J, "Same");
```

This is the canonical replacement for Andrew's `||` operator — same
semantics, different surface (and already a SPITBOL primitive, not
something we invented).

The IR node is `E_VLIST` (n-ary, eager left-to-right, short-circuit
on first non-failing arm). Distinct from `E_ALT` (pattern alternation,
lazy at match time, with backtracking).

---

## What is NOT in Snocone

- Binary `&&` (replaced by whitespace concat)
- Binary `||` (replaced by alt-eval `(e1, e2, e3)`)
- Built-in modulo `%` (use `REMDR(a, b)`; `%` reserved as OPSYN slot)
- `do/until` (removed per Lon directive 2026-04-30 #12; use
  `while (~cond)` or `goto`-with-label)
- `then` keyword (Andrew has none; not in KW_TABLE)
- Two-word `go to` (use single-keyword `goto`)
- `procedure` keyword (renamed to `function`)
- SPITBOL goto-field `:S(L) F(M)` syntax — Snocone has no goto-field.
  Control flow uses structured forms or `goto LABEL;`. The `:` is
  always a label-suffix in Snocone grammar.
- Newline tokens. The lexer does not emit a newline token; newlines
  are whitespace, full stop.

---

## DATATYPE convention

SCRIP returns **uppercase** for built-in types (`"NAME"`,
`"PATTERN"`, `"STRING"`, `"INTEGER"`). This is intentional per
SNOBOL4 spec. SPITBOL x64 returns lowercase (a known divergence;
see `RULES.md` "DATATYPE case" table).

Tests that compare DATATYPE results must be portable across case —
compare against a runtime-derived token, never hardcode `'PATTERN'`
or `'pattern'`. See `RULES.md` "DATATYPE case — authoritative,
intentional per runtime" for the binding rule.

---

## Implementation map

### File layout (SCRIP)

| Path | What |
|------|------|
| `src/frontend/snocone/snocone_parse.y` | Bison grammar |
| `src/frontend/snocone/snocone_parse.tab.{c,h}` | Generated parser tables |
| `src/frontend/snocone/snocone_lex.c` | Threaded-code FSM lexer |
| `src/frontend/snocone/snocone_lex.h` | Public FSM API |
| `src/frontend/snocone/snocone_driver.{c,h}` | scrip-side entry point |
| `archive/snocone_lower.{c,h}` | Legacy lowering (archived in LS-4.k) |
| `archive/snocone_control.{c,h}` | Legacy control-flow lowering (archived in LS-4.k) |

### Lexer

Single-pass threaded-code FSM in `snocone_lex.c` — one C function
`sc_lex_next(LexCtx *ctx)` whose body is a graph of labelled
`Label: action; goto NEXT;` blocks. No `switch` / `for` / `while` /
`do-while` in the FSM body. The FSM maintains a previous-token
state and emits a synthetic `T_CONCAT` token when a value-yielding
token is followed by another with whitespace between — that is the
space-as-concat implementation.

Comments fold into whitespace via `S_LCOMMENT` / `S_BCOMMENT`
sub-FSMs. Token names follow the `T_<arity><charname>` scheme
matching `snobol4.tab.h` — `T_2EQUAL` (`=`), `T_2DOT` (`.`),
`T_2DOLLAR` (`$`) for binary; `T_1*` for unary.

### Grammar

Bison parser in `snocone_parse.y`, generated to
`snocone_parse.tab.{c,h}`. Bison reports 0 shift/reduce and 0
reduce/reduce conflicts at every rung. Precedence declarations
match SPITBOL Manual Ch.15 priorities 0–13. The conditional in
`if`, `while`, `do/while`, `for`-test, and `case` tag is a single
`expr` non-terminal — the same backtracking expression that appears
as a SPITBOL statement subject/pattern/replacement chain. No special
"boolean expression" non-terminal.

Public entry: `CODE_t *snocone_parse_program(const char *src,
const char *filename)`.

### Build path

`.l` and `.y` source edits require regeneration:

```bash
bash scripts/regenerate_parser_and_lexer_from_sources.sh
```

This regenerates `snocone_parse.tab.{c,h}` (also any other front-
end's `.tab.{c,h}` and `.lex.c`). Per `RULES.md` "Editing `.y` or
`.l` files," the `.y`/`.l` source AND the updated generated files go
in the **same commit** — never edit the generated files directly
for grammar or lexer logic. Generated files are checked in so
normal builds do not require bison/flex on the build machine; flex
and bison are installed via `scripts/install_system_packages.sh`
when a regeneration is needed.

### Smoke gate (per-session, before every commit touching Snocone)

```bash
bash scripts/test_smoke_snocone.sh                 # PASS=5 FAIL=0
bash scripts/test_beauty_snocone_all_modes.sh      # PASS=42 FAIL=0 SKIP=3
bash scripts/test_smoke_unified_broker.sh          # PASS=49 FAIL=0
```

---

## Corpus migration

The `scripts/util_migrate_snocone_to_lang_space.py` script does the
mechanical sweep:

- `&&` → space (the new concat operator)
- `||` → `(a, b)` n-ary alt-eval (preserves short-circuit semantics)
- `go to NAME` → `goto NAME`

Strings and comments preserved verbatim. Single `|` (pattern
alternation) untouched. Idempotent.

Manual review handles edge cases (strings containing `&&` or `||`
literally, format specifiers using `%`, etc.).

A companion script `scripts/util_migrate_snocone_procedure_to_function.py`
handles the `procedure` → `function` rename.

---

## Authority and scope

This file is the single source of truth for Snocone language and
front-end architecture. The earlier sources have been consolidated
here:

- `GOAL-SNOCONE-LANG-SPACE.md` (deleted — work complete, content here)
- `RULES.md` "Snocone language facts" (now a one-line pointer to this file)
- `REPO-SCRIP.md` "Snocone front-end" (now a one-line pointer)
- `corpus/programs/snocone/LANGUAGE.md` (deleted — pointer in corpus README)
- `GOAL-SNOCONE-BEAUTY.md` "Snocone language facts" (deleted — pointer here)

Andrew Koenig's original Snocone (`SNOCONE.zip`: `snocone.sc`,
`snocone.sno`, `snocone.snobol4`) is historical context, not
authoritative for our Snocone. The authoritative implementation is
`snocone_lex.c` + `snocone_parse.y` in this tree; this document is
the spec they implement.
