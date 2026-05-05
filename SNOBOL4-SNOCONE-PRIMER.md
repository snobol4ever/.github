# SNOBOL4-SNOCONE-PRIMER.md — pattern matching cheat sheet for parser work

**Audience:** Future Claude sessions writing or editing `parser_*.sc` files.
**Purpose:** Avoid the mistakes that cost session #68 (2026-05-05) most of
its budget — treating SNOBOL4/Snocone pattern matching like a regex engine.
Update this file every time you discover something you wished you knew.

---

## Mental model — read this first or you will fail

Pattern matching has **two intertwined namespaces**, and every primitive
belongs to one or the other:

1. **Subject space** — the cursor moves through the subject string left to
   right (and backtracks). `SPAN`, `BREAK`, `LEN`, `POS`, `RPOS`, `TAB`,
   string literals, alternation `|`, concatenation (juxtaposition) — these
   live here. They consume subject characters.

2. **Value space** — Snocone variables, function returns, the values
   captured by `.` and `$`. `IDENT`, `DIFFER`, `EQ`, `LT`, `LEQ` — these
   are predicates over **values**, they do not move the cursor at all.
   Used as functions, they return success/failure with no side effect on
   the match.

The deferred-evaluation operator `*` is the **bridge** between these two
spaces. `*expr` says "at match time, evaluate `expr` in value space, take
the result, and re-enter subject space with it as a pattern (or pattern
function argument)." That single operator is why the language is more
powerful than a regex.

If you find yourself writing a regex-style "lookahead" or "anchor" trick,
stop. The idiomatic SNOBOL4 answer almost always involves `$` capturing
into a variable, then `*pred(var)` testing in value space.

---

## The big four operators

### `.` — conditional assignment

`PAT . VAR` matches whatever `PAT` matches and, **if the entire enclosing
match succeeds**, binds the matched substring to `VAR`. On backtracking,
the binding is undone. Use for **outputs**: things you want to keep only
if the whole match works.

```snocone
('GOLD' | 'BLUE') . shade   // shade gets value only on whole-match success
```

### `$` — immediate assignment

`PAT $ VAR` matches whatever `PAT` matches and **immediately** binds the
matched substring to `VAR`, even if the overall match later fails and
backtracks. Use for **mid-match state**: things you need to feed forward
into the rest of the pattern via `*`.

```snocone
SPAN(digits) $ n LEN(*n) . field   // capture n, then use it as a length
```

**Crucial corollary:** because `$` fires even on failure paths, you can
use it to capture, then test the captured value with a function predicate,
all without moving the cursor:

```snocone
Id $ tx *IDENT(tx, 'do')   // matches Id, captures into tx, succeeds iff tx == 'do'
```

That `*IDENT(tx, 'do')` is **value-space** — it tests a string equality.
The cursor does not advance during the test. Combine with the fact that
`Id` already consumed the full identifier, and you have a **correct
word-boundary keyword matcher**.

### `*` — deferred evaluation / unevaluated expression

`*expr` is **NOT** "match anything" (regex `*`). It's "evaluate `expr` in
value space at match time and use the result here in subject space."

- `*var` — at match time, fetch `var`'s value and use it as a pattern
- `*fn(a, b)` — at match time, call `fn(a, b)` and use the return as
  a pattern
- `*(expr)` — same, with arbitrary computation

Three uses of `*`:

1. **Recursive patterns** — `Expr0 = *Expr1 FENCE($'=' *Expr0 | epsilon)`.
   Without `*`, `Expr0` would try to use the value of `Expr0` at the
   moment of *definition* — which is undefined. With `*`, lookup is
   deferred to match time, by which point all definitions are in place.
2. **State-dependent matching** — `LEN(*n)` reads `n`'s current value
   each match.
3. **Side-effect calls** — `*func()` invokes `func` mid-match. Used
   pervasively for tree-building helpers (`Push`, `Pop`, `IncCounter`).

### `~` — negation

`~PAT` succeeds iff `PAT` fails, consuming nothing. Useful as a
zero-width predicate. Note: in scrip's grammar, `~` and `&` are also
OPSYN'd to `shift` and `reduce` (see `semantic.sc`) — context determines
which meaning applies.

---

## Idioms you must know

### Word boundary (keyword recognition)

**Wrong** (what session #68 wasted hours on):

```snocone
kw_tail = FENCE(SPAN(&UCASE &LCASE digits '_') | epsilon) . kw_rest IDENT(kw_rest);
kw_if = ('if' kw_tail);
```

`FENCE` commits, so the conditional `.` is moot — it always assigns.
`IDENT(kw_rest)` with one arg checks `kw_rest == kw_rest` which is always
true. **The boundary check does nothing.** It works in fixtures only
because the lexer happens to put whitespace after every keyword.

**Right:**

```snocone
kw_if = (Id $ tx *IDENT(tx, 'if'));
```

`Id` consumes the entire identifier (one or more identifier chars).
`$ tx` immediately captures it. `*IDENT(tx, 'if')` runs in value space
— succeeds iff `tx` is exactly the string `'if'`. Word boundary is
**by construction** because `Id` already consumed everything that's
identifier-like.

### Reject reserved words from `Id`

```snocone
sc_reserved = POS(0) ('if' | 'else' | 'while' | 'do' | 'for') RPOS(0);
function notmatch(s, pat) {
    if (s ? *pat) { notmatch = .dummy; freturn; }
    notmatch = .dummy; nreturn;
}
Id    = (ANY(&UCASE &LCASE '_') FENCE(SPAN('.' digits &UCASE '_' &LCASE) | epsilon));
Ident = Id $ tx *notmatch(tx, sc_reserved);
```

`sc_reserved` is a pattern that, when applied to a string with `?`,
matches the **whole string** iff it's a reserved word — `POS(0)` and
`RPOS(0)` anchor to start and end. `notmatch(s, pat)` applies `pat` to
`s` as a fresh subject and inverts the result. `Ident` matches an
identifier, captures it, then succeeds iff it is NOT a reserved word.

The pattern `*pat` here matches `pat` against `tx` as a **separate
subject** (`tx ? *pat` inside `notmatch`). This is value-space pattern
application — completely distinct from matching in the original subject.

### Keyword tokens with whitespace envelope (the `$'X'` style)

Define each operator/punct token once with its required whitespace:

```snocone
White       = ( SPAN(' ' tab) FENCE(nl ('+' | '.') ... | epsilon) | nl ('+' | '.') ... );
Gray        = White | epsilon;       // optional whitespace
$'  '       = White;                 // double-blank alias = required whitespace
$' '        = Gray;                  // single-blank alias = optional whitespace
$'='        = $'  ' '=' $'  ';       // = with required whitespace both sides
$'('        = '(' $' ';              // ( with optional whitespace after
$')'        = $' ' ')';              // ) with optional whitespace before
```

Then in grammar productions, never write whitespace explicitly — use the
token names:

```snocone
Expr0 = *Expr1 FENCE($'=' *Expr0 ('E_ASSIGN' & 2) | epsilon);
```

`$'X'` is **Snocone indirect access** — the variable named exactly the
string `'X'`. `$'  '` is the variable whose name is two spaces. These are
real variables in the symbol table; they hold pattern values; they're
referenced via the `$` indirection operator (NOT to be confused with the
binary `$` immediate-assignment operator — same character, different
position).

### Build-time vs match-time helpers

Tree-building functions come in **pairs**: a lowercase `match-time`
worker that returns `.dummy` and `nreturn`s, and an Uppercase
`build-time` companion that returns a deferred-action pattern:

```snocone
function push_qlit() {
    Push(tree('E_QLIT', str_body));
    push_qlit = .dummy;
    nreturn;
}
function Push_qlit() {
    Push_qlit = (epsilon . *push_qlit());
    return;
}
```

The pattern `(epsilon . *push_qlit())` matches the empty string, then
fires `push_qlit()` as a side effect via the deferred-eval `*`. The
outer pattern uses `Push_qlit` (build-time), which expands to the
match-time pattern. This keeps the grammar readable.

The `.dummy` / `nreturn` shape on the worker is required because
`*func()` in pattern context needs the function to return a name (not a
value), and `nreturn` does that — see RULES.md "NRETURN functions".

### shift/reduce via OPSYN

`semantic.sc` does `OPSYN('~', 'shift', 2)` and `OPSYN('&', 'reduce', 2)`.
After this:

```snocone
*Integer ~ 'E_ILIT'           // shift: match Integer, push tree of type E_ILIT
('E_ADD' & 2)                 // reduce: pop 2 trees, push (E_ADD child1 child2)
('E_SEQ' & '*(GT(nTop(),1) nTop())')   // reduce: pop nTop() trees, push n-ary E_SEQ
```

`~` and `&` are infix calls to `shift(p, t)` and `reduce(t, n)`. The
right-hand side of `&` can be a string for static n, or a deferred
expression `*(...)` evaluated at match time for dynamic n.

### Counter stack (for n-ary tree-building)

`counter.sc` provides `nPush` / `nInc` / `nTop` / `nPop` — a stack of
counters. Used to count children produced by `ARBNO` so the right number
can be popped at reduce time:

```snocone
Expr3 = nPush() *X3 ('E_ALT' & '*(GT(nTop(), 1) nTop())') nPop();
X3    = nInc() *Expr4 FENCE($'|' *X3 | epsilon);
```

`nPush` opens a fresh counter at the start; `nInc` bumps it for each
`Expr4` matched; `nTop` reads it at reduce time; `nPop` discards on the
way out. The `GT(nTop(),1) nTop()` idiom: produce an n-ary `E_ALT` only
if there were 2+ alternatives, else fall through to the single child
(no wrapping).

### Recursive patterns vs left recursion

Pattern definitions are right-recursive by default. Left recursion
requires the iterative `ARBNO` + `foldop` shape:

```snocone
// Right-recursive (clean):
Expr0 = *Expr1 FENCE($'=' *Expr0 | epsilon);
// Right-assoc binary op chain.

// Iterative left-fold (left-assoc, n-ary flatten):
Expr6 = *Expr7 FENCE($'+' *Expr7 foldop('E_ADD') *Expr6cont | $'-' *Expr7 foldop('E_SUB') *Expr6cont | epsilon);
Expr6cont = FENCE($'+' *Expr7 foldop('E_ADD') *Expr6cont | $'-' *Expr7 foldop('E_SUB') *Expr6cont | epsilon);
```

`foldop` collapses same-tag chains into n-ary trees: see `ShiftReduce.sc`.

---

## Pattern primitives — the cheat table

| Primitive | Subject space? | Action |
|---|---|---|
| `'literal'`, `"literal"` | yes | match exact string |
| `LEN(n)` | yes | match `n` characters |
| `SPAN(chars)` | yes | match one or more of `chars` |
| `BREAK(chars)` | yes | match up to (not including) any char in `chars`; fails at EOS |
| `BREAKX(chars)` | yes | like `BREAK` but allows zero advance fall-through |
| `ANY(chars)` | yes | match exactly one char from `chars` |
| `NOTANY(chars)` | yes | match exactly one char NOT in `chars` |
| `TAB(n)` | yes | match through cursor position `n` |
| `RTAB(n)` | yes | match through `n` chars from end |
| `POS(n)` | yes | succeed iff cursor is at position `n` (zero-width) |
| `RPOS(n)` | yes | succeed iff cursor is `n` from end (zero-width) |
| `REM` | yes | match the rest of the subject |
| `ARB` | yes | match the shortest possible string (shy) |
| `ARBNO(P)` | yes | match zero or more of `P` (shy) |
| `epsilon`, `''` | yes | match empty string (always succeeds) |
| `FAIL` | yes | always fail (force backtrack) |
| `ABORT` | yes | fail and abort the entire match |
| `FENCE` | yes | zero-width; fails on backtrack (commit point) |
| `FENCE(P)` | yes | match `P`; on backtrack, do not retry inside |
| `SUCCEED` | yes | match empty; on backtrack, retry forward |
| `IDENT(a, b)` | NO — value | succeed iff `a` is identical to `b` |
| `IDENT(a)` | NO — value | succeed iff `a` is identical to itself (always true!) |
| `DIFFER(a, b)` | NO — value | succeed iff `a` differs from `b` |
| `DIFFER(a)` | NO — value | succeed iff `a` is non-null |
| `EQ`/`NE`/`LT`/`GT`/`LE`/`GE` | NO — value | numeric comparison predicates |
| `LEQ`/`LNE`/`LLT`/`LGT`/`LLE`/`LGE` | NO — value | lexical comparison predicates |
| `SIZE(s)` | NO — value | length of string |

The cheat is the **NO** column: those don't move the cursor. They're
predicates. Inside a pattern, you use them via `*pred(args)` so they
become deferred calls fired at match time.

---

## Anchored vs unanchored / fullscan

```snocone
&ANCHOR   = 0;   // unanchored: pattern can match anywhere in subject
&ANCHOR   = 1;   // anchored: pattern must match starting at position 0
&FULLSCAN = 1;   // exhaustive: explore all alternatives (parser default)
```

Per RULES.md: **always** `&ANCHOR = 0` and `&FULLSCAN = 1` for parser
work. Set both at the top of every parser file.

---

## Snocone-specific gotchas (vs SNOBOL4)

These bite repeatedly. See `ARCH-SNOCONE.md` for the canonical spec.

- **Whitespace is concat.** `'foo' 'bar'` evaluates to `'foobar'`. The
  lexer emits a synthetic `T_CONCAT` token at the boundary.
- **Newlines are whitespace.** Statements end with `;`, never with newline.
  `x = 1\ny = 2;` is **one** statement.
- **`f(x)` vs `f (x)` differ.** Zero-space = function call. Space = concat.
- **`&IDENT` = keyword, no space.** `& IDENT` is a syntax error.
- **`.` in identifiers.** SNOBOL4 allows `cl.type` as one ident; Snocone
  does not. `cl.type` lexes as `IDENT(cl) PERIOD IDENT(type)` — so use
  `_` for compound names: `cl_type`.
- **No `&&` or `||`.** AND is whitespace concat (`if (P1 P2)`); OR is
  alt-eval `(e1, e2, e3)` (NOT pattern alternation `|`).
- **No goto-field `:S(L)F(M)`.** Use structured control flow or `goto LABEL;`.
- **`if/else` requires braces.** `if (cond) A else B` is illegal Snocone —
  bodies must be `{ ... }`. (Bit me in session #68.)
- **Strings have no escapes.** `\n` is literally backslash-n. Use `nl`
  (predefined as the newline char), `tab`, `bs`, `cr`, `ff`, `bSlash`.
- **DATATYPE is uppercase in one4all.** `'NAME'`, `'PATTERN'`, `'STRING'`,
  `'INTEGER'`. SPITBOL returns lowercase. Tests must be case-portable
  (`REPLACE(DATATYPE(x), &LCASE, &UCASE)`).
- **Functions return via assignment-to-name.** `function foo() { foo = 5; return; }`.
  Three return shapes: `return` (success, value already in `foo`),
  `nreturn` (success, return name not value), `freturn` (failure).
- **`$varname = expr;`** is indirect assignment (assign to the variable
  whose name is in `varname`).

---

## Pair-shape for tree-building helpers (canonical)

When a grammar production needs to fire a side effect mid-match:

```snocone
// Match-time worker: lowercase, no args, returns .dummy via nreturn
function push_qlit() {
    Push(tree('E_QLIT', str_body));
    push_qlit = .dummy;
    nreturn;
}

// Build-time companion: Capitalized, returns the deferred pattern
function Push_qlit() {
    Push_qlit = (epsilon . *push_qlit());
    return;
}

// Used in grammar:
String = (DQ | SQ) Push_qlit();   // match a string, then fire push_qlit
```

When the worker needs match-time arguments (e.g. captured via `$`):

```snocone
function push_kw_var(name) {
    Push(tree('E_VAR', name));
    push_kw_var = .dummy;
    nreturn;
}
function Push_kw_var() {
    // EVAL builds a pattern that, at match time, calls push_kw_var
    // with the current value of captured_name
    Push_kw_var = EVAL("epsilon . thx . *push_kw_var(captured_name)");
    return;
}
```

The `EVAL` is needed when you want the deferred call to take its
arguments from a variable that holds the captured value.

---

## What the gates measure

```bash
bash scripts/test_smoke_snocone.sh        # 5 fixtures — basic Snocone front-end
bash scripts/test_parser_snocone.sh       # ~46 fixtures — PARSER-SC gate
```

Each `parser-fixtures/*.sc` is parsed two ways and compared
byte-for-byte (whitespace-normalized):

1. The reference: `scrip --dump-ir fixture.sc` (existing C frontend).
2. The candidate: `parser_snocone.sc` running through `--ir-run` with
   the shared library blob.

A fixture passes iff both produce the same IR tree. PASS=46 FAIL=0
means parity for everything in the fixture set; that does NOT mean
beauty.sc parses. Always run beauty.sc separately before claiming
"works":

```bash
SCRIP=/home/claude/one4all/scrip
SRC=/home/claude/corpus/programs/scrip
cat /home/claude/corpus/programs/snocone/demo/beauty/beauty.sc | \
  timeout 30 $SCRIP --ir-run $SRC/global.sc $SRC/tree.sc $SRC/stack.sc \
    $SRC/counter.sc $SRC/semantic.sc $SRC/ShiftReduce.sc $SRC/qize.sc \
    $SRC/gen.sc $SRC/tdump.sc $SRC/assign.sc $SRC/parser_snocone.sc 2>&1
```

Empty output = `Parse Error`. Each line of output is one IR statement.

---

## Failure modes I keep hitting

1. **Treating `IDENT(x)` as a tautology check.** It is. One-arg `IDENT`
   only checks the value is identical to itself. Always use two-arg form
   for actual equality testing: `IDENT(x, 'expected')`.

2. **Trying to use `~SPAN(...)` as a zero-width negative lookahead.**
   Sometimes works, sometimes interacts badly with the rest of the
   pattern. The robust idiom for "is this ident a keyword" is value-space:
   capture with `$`, test with `*IDENT(tx, 'kw')`.

3. **Assuming `.` provides a backtrackable test.** `.` is for output
   capture, not for testing. After `FENCE` it's also moot because
   `FENCE` commits.

4. **Writing `if (cond) A else B;` (no braces).** Illegal Snocone. The
   parse error message blamed line N+1 ("Parse Error"), not the actual
   problem. Always use braces for `if/else`.

5. **Assuming a fixture-set PASS=46 means the parser handles real
   programs.** It doesn't. The fixtures are minimal. Run beauty.sc.

6. **Defining `$'kw'` for Snocone reserved words.** The Snocone runtime
   stores `$'kw'` as a real variable; that variable does NOT clobber
   the lexer's hardcoded keyword table. So `$'if'` is **safe** — but
   I spent hours convinced it broke the lexer. The actual culprit was
   `if (...) A else B;` without braces. Both observations occurred in
   the same minute and I conflated them.

7. **Ignoring SKILL.md and ARCH files.** They contain the canonical
   answer to most of what I keep guessing about. Read them first.

8. **Probing instead of reading.** When I don't understand a primitive,
   the answer is in `spitbol-manual-v3_7.pdf` chapter on Pattern Matching
   (around page 56–87 for tutorial, ~page 124 for FENCE/FAIL/SUCCEED).
   Read the manual section before writing more probes.

---

## Reference file map

| Topic | Source of truth |
|---|---|
| Snocone language spec | `ARCH-SNOCONE.md` |
| SNOBOL4 frontend | `ARCH-SNOBOL4.md` |
| Pattern matching tutorial | SPITBOL Manual ch.6 (pp 55-) |
| FENCE / FAIL / SUCCEED | SPITBOL Manual ch.9 (pp 124-) |
| ARBNO recursion | SPITBOL Manual ch.9 (pp 121-) |
| `*` deferred eval | SPITBOL Manual ch.7 (pp 85-) |
| `$` immediate assignment | SPITBOL Manual ch.7 (pp 87-) |
| Canonical PARSER style | `GOAL-PARSER-SNOBOL4.md ## Style Guidelines for parser_*.sc` |
| Per-language parser | `GOAL-PARSER-{SNOBOL4,SNOCONE,ICON,PROLOG,RAKU,REBUS}.md` |
| Pattern library | `corpus/programs/scrip/{tree,stack,counter,ShiftReduce,semantic,assign,qize,gen,tdump,global}.sc` |
| Reference grammars | `corpus/programs/scrip/parser_snobol4.sc` (canonical) |
| Beauty source | `corpus/programs/snocone/demo/beauty/beauty.sc` |

Always cross-check `parser_snobol4.sc` for canonical idioms before
inventing a new one in another `parser_*.sc`.

---

## Update log

- **Created** session #68 (2026-05-05). Primary triggers: confused `.`
  vs `$`, broken `IDENT` one-arg boundary check, treating `~SPAN` as
  zero-width lookahead, conflating `$'kw'` definition with parser bug
  that was actually unbraced `if/else`. Lon spent an entire session
  walking me through fundamentals; this primer is the artifact.

When you discover a new failure mode or pattern idiom, **add it here**.
Do not let the next session repeat your mistakes.
