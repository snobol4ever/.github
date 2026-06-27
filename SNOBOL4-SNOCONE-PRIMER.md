# SNOBOL4-SNOCONE-PRIMER.md — pattern matching cheat sheet for parser work

**Audience:** Future Claude sessions writing or editing `parser_*.sc` files.
**Purpose:** Avoid the mistakes that cost session #68 (2026-05-05) most of
its budget — treating SNOBOL4/Snocone pattern matching like a regex engine.
Update this file every time you discover something you wished you knew.

---

## THE most important thing — `.` vs `$` execution model

**This is the #1 source of bugs. Read it before anything else.**

There are two fundamentally different times when things run inside a pattern:

### `.` (conditional assignment) — fires AFTER the whole statement-level match succeeds

`PAT . VAR` captures the text matched by PAT into VAR, but only **after the whole
`if (Src ? Compiland)` match succeeds**. All the `.` actions across the entire
Compiland match fire at the end, **in the linear order they were encountered
during the successful match path**. They are a straight-line sequence of variable
assignments and code-gen calls. They do NOT fire on failed alternatives.

This is how `nPush()`, `nInc()`, `nPop()`, `Shift(...)`, `Reduce(...)` all work —
they are all `.`-based patterns. The whole pattern match is **pure cursor movement**.
The semantic actions are a **post-match linear sequence**.

**Consequence:** if you need a value (like a function name or label) that was captured
mid-match to survive later uses in that same linear sequence, you must capture it into a
NAMED variable via `.` at the right point, **not** rely on shared scratch variables like
`tx` — because those get overwritten by subsequent match elements before the sequence runs.

### `$` (immediate assignment) — fires DURING matching, not undone on backtrack

`PAT $ VAR` captures the text matched by PAT into VAR **immediately at match time**,
even if the overall match later fails and backtracks. This is how mid-match state
is fed forward:

```snocone
P $ tx $ *assert_can_fail(tx)   // capture tx NOW, immediately call assert on it
```

The second `$` is the idiomatic "fire a predicate and throw away the result" form.
`*assert_can_fail(tx)` is called immediately with the current value of `tx`. If it
returns failure, the match fails here. This is **not** a post-match sequence.

**Consequence:** `tx` is a shared scratch variable. Any `$ tx` anywhere in the
successful match path overwrites it. By the time `.`-based semantic helpers fire
at end-of-match, `tx` holds whatever the **last** `$ tx` set it to — not the first.

### The capture-naming rule

To preserve a name from mid-match for later semantic use, capture it into a
**dedicated named variable** using `.`:

```snocone
// CORRECT: captures just the Id text into captured_name (no leading whitespace)
$' ' (*Id . captured_name) $ *notmatch(captured_name, reserved)

// WRONG: captures the full Ident match including its internal $' ' whitespace
*Ident . captured_name    // captured_name = ' f', not 'f'
```

The critical pattern: eat whitespace BEFORE the `(...)` capture group, so the `.`
only sees the identifier text itself. The `$' '` outside the parens consumes
whitespace; the `(*Id . captured_name)` captures just the Id.

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

**Chaining `$` with a deferred function call** is the canonical way to
test the captured value against a set-classifier:

```snocone
SpecialNm = SPAN('.' digits &UCASE '_' &LCASE) $ tx $ *match(SpecialNms, TxInList);
```

The second `$` looks like an assignment but the right side is a
deferred function call returning `.dummy` (a name). The `$` "assigns
into" the throwaway name; the **side effect is the success/failure
of the embedded `match()`**. This is the beauty.sno idiom for
"capture-and-classify". See "Set-membership" below.

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

### Set-membership via space-separated word list (beauty.sno idiom)

When you need to classify a token as one of a small fixed set
(reserved words, builtin function names, keyword names), beauty.sno
uses a **space-separated string as the set** and a **boundary pattern**
to test membership. No arrays, no tables, no hash maps:

```snocone
SpecialNms  =  'ABORT CONTINUE END FRETURN NRETURN RETURN SCONTINUE START';
TxInList    =  (POS(0) | ' ') *upr(tx) (' ' | RPOS(0));
SpecialNm   =  SPAN('.' digits &UCASE '_' &LCASE) $ tx $ *match(SpecialNms, TxInList);
```

How `TxInList` works as a membership test against `SpecialNms`:
- `(POS(0) | ' ')` — left boundary: at start of string OR preceded by space
- `*upr(tx)` — the captured token, uppercased, used as a literal pattern
- `(' ' | RPOS(0))` — right boundary: followed by space OR at end of string

Applied to `'ABORT CONTINUE END ... START'` with `tx = 'CONTINUE'`,
this matches the bounded substring `'CONTINUE'` in the list. With `tx
= 'CONT'`, it fails because `CONT` is not whole-word-bounded in the
list. Same idiom for `BuiltinVars`, `ProtKwds`, `UnprotKwds`,
`Functions`.

### The double-`$` set-membership idiom — `pat $ tx $ *match(set, classifier)`

Reading right-to-left:

1. `pat` — a pattern that consumes the token from the **subject**
2. `$ tx` — immediate-capture the matched token into variable `tx`
3. `$ *match(set, classifier)` — the second `$` looks like another
   capture, but `*match(set, classifier)` is a deferred call to the
   function `match`. `match` returns `.dummy` (a name) on success and
   `freturn`s on failure. The `$` immediate-assigns the matched
   substring into the **name** that `match` returned (`.dummy` — a
   throwaway). The whole `$ *match(...)` construction succeeds iff
   `match` succeeds; its **purpose is the success/failure outcome**,
   not the assignment.

So this fragment "consumes a token from the subject, then asserts that
the token belongs to the named set." The cursor in the main subject
is already past the token (because `pat` consumed it); the membership
test runs in **value space** against `set`.

`match` and `notmatch` are defined in `beauty/match.inc` (and ported
to `parser_*.sc` as needed):

```snocone
function match(subject, pattern) {
    match = .dummy;
    if (subject ? *pattern) { nreturn; }
    freturn;
}
function notmatch(subject, pattern) {
    notmatch = .dummy;
    if (subject ? *pattern) { freturn; }
    nreturn;
}
```

The first arg is the **subject string**, the second is the **pattern**.
`match` runs `subject ? *pattern` (a fresh pattern match in a separate
namespace), returns name `.dummy` on success or freturns on failure.
Both forms return `.dummy` so they can appear after `$` in a pattern.

This idiom is **the canonical SNOBOL4 way to classify a token by
set membership**. Use it instead of inventing one-off patterns.

### `*upr(tx)` — value computation as deferred pattern

`*func(args)` makes the function call deferred — at match time, evaluate
`func(args)` in value space and use the returned value as a **pattern**
in subject space. Because strings auto-coerce to literal-match patterns,
`*upr(tx)` becomes "a pattern that matches the literal string equal to
the uppercase of `tx`'s current value."

```snocone
omega = omega " $ tx *LEQ(upr(tx), '" upr(name) "')";
```

This is from `omega.inc` — building a classifier dynamically by
embedding `*LEQ(upr(tx), 'NAME')` into a generated EVAL string. The
inner `*LEQ(...)` does a lexical-comparison value test (succeeds iff
upr(tx) ≤ 'NAME'); the outer `$ tx` captured the token first.
Pure value-space classification, embedded in a pattern via `*`.

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

## Phase 2 SCRIP authoring addendum — library primitives every parser uses

The sections above cover the SPITBOL/Snocone pattern-matching mental
model. The sections below cover the **library primitives** that every
`parser_*.sc` depends on. Read this before writing or editing a parser.

### Library load order (what's already in scope)

When a parser_X.sc starts executing, the runtime has already loaded:

```
global.sc      tree.sc        stack.sc       counter.sc
semantic.sc    ShiftReduce.sc qize.sc        gen.sc
tdump.sc       assign.sc      match.sc       parser_X.sc
```

(plus `omega.sc` only when tracing is on, plus `trace.sc` for hooks).

So these names are pre-defined and ready to use:

| name | source | purpose |
|---|---|---|
| `shift(p, t)`, `reduce(t, n)` | semantic.sc | Phase-2 primitives — wrap `Shift`/`Reduce` via `EVAL` so they're pattern-typed |
| `nPush()`, `nPop()`, `nInc()`, `nTop()` | semantic.sc | counter-frame stack via `epsilon . *fn()` deferred-call wrappers |
| `Shift(t, v)`, `Reduce(t, n)` | ShiftReduce.sc | the actual workers — push leaf / pop-and-wrap-n |
| `Push(x)`, `Pop()` / `Pop(.var)`, `Top()` | stack.sc | tree stack (parser builds onto this) |
| `InitCounter()`, `InitStack()` | counter.sc, stack.sc | call ONCE before `Compiland` runs |
| `PushCounter()`, `PopCounter()`, `IncCounter()`, `TopCounter()`, `DecCounter()` | counter.sc | the workers behind `nPush`/`nPop`/etc. |
| `tree(t, v)`, `tree(t, v, n, c)`, `Tree(t, v, n, c1, c2, ...)` | tree.sc | tree-node constructors (lowercase = 2-arg or 4-arg; capitalized = variadic up to 8 kids) |
| `t(x)`, `v(x)`, `n(x)`, `c(x)` | tree.sc | field accessors via `struct tree { t, v, n, c }` |
| `Append(x, y)`, `Prepend(x, y)`, `Insert(x, y, pos)`, `Remove(x, pos)` | tree.sc | child-mutation helpers (NOT permitted in Phase 2 grammar rules) |
| `Equal(x, y)`, `Equiv(x, y)`, `Find(xn, y, f)`, `Visit(x, fnc)` | tree.sc | tree comparison / walk |
| `assign(name, expr)` | assign.sc | `$name = expr` (or `$name = EVAL(expr)` if `expr` is an EXPRESSION-type) |
| `match(subj, pat)`, `notmatch(subj, pat)` | match.sc | success-or-failure wrappers around `subj ? pat` |
| `Qize(s)`, `SQize(s)`, `DQize(s)` | qize.sc | quote-escape a string for embedding in EVAL strings |
| `TDump(x)` | tdump.sc | recursive tree dumper to OUTPUT (driver tail uses it) |
| `epsilon`, `nl`, `tab`, `bs`, `cr`, `ff`, `bSlash` | global.sc | predefined character constants |
| `digits`, `hex_digits`, `bin_digits`, `oct_digits` | global.sc | predefined cset strings |
| `TRUE`, `FALSE` | global.sc | `1` and `0` |
| `&FULLSCAN`, `&MAXLNGTH`, `&ALPHABET`, `&UCASE`, `&LCASE` | global.sc | SPITBOL keywords pre-configured |

**Forbidden for Phase 2 grammar rules** (these EXIST in the library
but must not be called from `Compiland` or any reduced grammar rule):
`Push`, `Pop`, `Top`, `Tree`, `tree`, `Append`, `Prepend`, `Insert`,
`Remove`, `IncCounter`, `TopCounter`, `shift_value`, `foldop`,
`reduce_call`, `reduce_prim`, `reduce_opsyn`. Permitted only in the
driver tail's root-retrieval `Pop()` and the library-internal code.

### Function-return mechanics — four shapes, not three

| shape | use when | example |
|---|---|---|
| `Fnc = value; return;` | normal success returning a value | `qtag = "''"; return;` |
| `Fnc = .dummy; nreturn;` | success returning a NAME (so the call can appear after `*` in a pattern) | `assign = .dummy; nreturn;` |
| `Fnc = value; nreturn;` | success returning a name AND setting `Fnc`'s slot to a specific value (rare; used by `Pop` and `TopCounter`) | `Pop = value($'@S'); ... nreturn;` |
| `freturn;` | failure (caller's pattern fails or `if (~fn(...))` succeeds) | `if (~DIFFER($'@S')) { freturn; }` |

Critical rules:

- **`nreturn` requires `Fnc = something` first.** The "name" returned is
  the function-name variable. If you forget to assign before `nreturn`,
  the previous value of that name lingers.
- **`freturn` overrides any pending value.** Whether or not you assigned
  to `Fnc`, `freturn` causes the caller's match to fail at the call site.
- **Functions used after `*` in a pattern MUST return a name** (i.e.
  end in `nreturn`, or `return` after `Fnc = .dummy`). The deferred-eval
  operator `*fn()` expects a NAME-typed result it can re-enter pattern
  space with. A pure-value `return` from a `*fn()` site is wrong.
- **Functions used as predicates (in `if`, `while`)** can use either
  return form. `freturn` is the failure signal that `~fn(...)` inverts.

Reading exercise: `Shift` in `ShiftReduce.sc` ends with both
`if (Shift = IDENT(v) .v(s)) { nreturn; }` and `Shift = DIFFER(v) .dummy; nreturn;` —
two paths, both `nreturn`-ing a name (one captures into `s`'s value, the
other returns `.dummy`).

### Unary `.` (name operator) vs binary `.` (conditional assignment)

These look identical but operate at completely different times.

- **Binary `.` (pattern operator):** `PAT . VAR` — captures matched
  text into VAR if the whole match succeeds. Post-match, value-typed.
- **Unary `.` (value operator):** `.var` — returns the NAME of `var`.
  Evaluated immediately, returns a NAME data type. Used as:
  - argument to indirection: `$(.foo)` ≡ `foo` ≡ `$'foo'`
  - target of `nreturn`: `Fnc = .dummy; nreturn;`
  - first arg to `assign`: `assign(.captured_name, token)` — the `.`
    makes `captured_name` a NAME so `assign` can do `$name = expr`
    indirection on it.

Mental shortcut: **left of a pattern `.` is a pattern; left of unary
`.` is nothing (it's prefix); right of unary `.` is a variable name**.
Manual ref: SPITBOL ch.7 p.86; ch.15 p.181.

### `$varname` — indirect assignment / read

`$expr` evaluates `expr` to a string, then accesses the variable whose
name is that string. Used pervasively:

- **Library-internal:** `$'@S'` (stack head), `$'#N'` (counter top),
  `$'@B'` / `$'@E'` (begin/end-tag stacks) — variable names that
  contain non-identifier characters (literal `@`, `#`) must be reached
  via `$'…'` because regular Snocone idents can't have those characters.
- **Parser-internal:** `$varname = TopCounter();` (parser_snocone.sc) —
  write into the variable whose **name is the string held in `varname`**.
- **Read form:** `n = $nthen_v;` — read the variable named by `nthen_v`.

Two ways to write `$x`:
- `$x` — when `x` is a variable already holding the target name.
- `$'literal_name'` — when the target name is a fixed string.

Both produce the same indirect access. Both are the same `$` unary
operator; the second form's `'literal_name'` is just a string literal
fed to `$`.

### `assign` — the indirect-write helper, and why `.captured_X` precedes it

```snocone
assign = function assign(name, expression) { ...; $name = expression; nreturn; }
```

A call like `*assign(.captured_name, token)` fires this at match time
and writes the current value of `token` into `captured_name`. The
`.captured_name` is **the unary-`.` form** that turns the identifier
`captured_name` into a NAME data type so `$name = expression` works as
indirect assignment.

**Why use `assign` instead of writing `$varname = expr;` directly?**
Because `*func()` is the only way to fire arbitrary code mid-match. You
can't put `$varname = expr;` directly inside a pattern — patterns are
expressions, not statements. So you wrap the assignment in a function
and fire it via `*`. The `assign` library function is the canonical
generic form.

### `OPSYN` — `~` is `shift`, `&` is `reduce`

`semantic.sc` opens with:

```snocone
OPSYN('~', 'shift', 2);
OPSYN('&', 'reduce', 2);
```

This means inside every parser, the **infix forms `~` and `&` are
direct calls to `shift` and `reduce`**:

```snocone
*Integer ~ 'TT_ILIT'          // ≡ shift(*Integer, 'TT_ILIT')
('TT_ADD' & 2)                // ≡ reduce('TT_ADD', 2)
```

The longhand `shift(...)` / `reduce(...)` function-call form and the
infix `~` / `&` form are interchangeable. Phase 2 goals accept either.
Most existing parser_*.sc files use the function-call form for clarity.

### `EVAL(...)` — building patterns at run-time from captured arguments

When a build-time helper needs to embed the **current value** of a
variable into the pattern it's returning, `EVAL` is required. Example
(parser_snocone.sc):

```snocone
function Save_nbody(var) {
    Save_nbody = EVAL("epsilon . thx . *save_nbody('" var "')");
    return;
}
```

Why EVAL? At the moment `Save_nbody('if_nthen')` is **called**, `var`
holds `'if_nthen'`. We want the resulting pattern to embed that exact
string, not a reference to `var`. EVAL takes the assembled string and
compiles it to a pattern, baking in the current value.

Without EVAL, the returned pattern would call `save_nbody(var)` at match
time, but by then `var` may be reused with a different value.

Phase 2 goals require this idiom less often than Phase 1 helpers did —
because grammar rules now embed values via `assign(.tmp, val) shift(tmp, kind)`
instead of `shift_value(val, kind)`. But the parsers still use EVAL inside
their token-aliasing layer at the top of the file. Leave that alone.

### `epsilon . *fn()` — the canonical fire-side-effect pattern

```snocone
Some_helper = epsilon . *some_helper();
```

Reads as: match the empty string (always succeeds, doesn't move
cursor), then conditionally assign the matched empty text into the
name returned by `some_helper()` (which is `.dummy`, a throwaway).

The **side effect is the body of `some_helper`** firing at match time.
The `.` here is binary conditional-assignment — it fires after the
whole enclosing match succeeds. The empty-string capture is discarded.

This is **how every library helper that needs to fire mid-pattern wraps
its match-time worker**. The pattern produced by `nPush()`,
`nInc()`, `nPop()` etc. is exactly this shape.

For mid-match firing (not waiting until enclosing-match success), the
form is `epsilon $ *fn()` — same idea but using immediate `$`.

### Multi-assign-in-condition idiom (SPITBOL extension)

Every loop and conditional in the library uses this shape:

```snocone
while (i = GT(i, 1) i - 1) { ... }          // counter.sc
while (v = DIFFER(b) value(b)) { ... }      // begin-tag dump
if (~(t = EVAL(t))) { nreturn; }            // ShiftReduce.sc
```

How it parses: `=` is low-precedence, right-associative. The RHS is
evaluated as a **value-and-predicate** chain. Reading
`i = GT(i, 1) i - 1`:

1. Evaluate `GT(i, 1)` — predicate. If false → whole expression fails,
   `i` is **not** assigned, `while` sees failure, loop exits.
2. If true, `GT(i, 1)` returns `i` (its first arg).
3. Concatenate with `i - 1` — string concat producing the new value.
   Wait, no: SNOBOL4's `GT` returns its second arg on success. Read
   the manual: `GT(a, b)` succeeds and returns `a` if `a > b`. So
   `GT(i, 1) i - 1` is "GT-test, then if succeeded value is `i - 1`".
4. Assign the result to `i`. Now `i` holds `i_old - 1`.
5. The `while`'s condition is the value of the whole `=` — non-null,
   so loop continues.

The pattern: **predicate at the start of the value gates the assign**.
If the predicate fails, no side effect; loop exits cleanly. Manual ch.9
"Binary Operator Extensions" p.128.

This appears everywhere in library code. When reading library code,
parse `=` first, then read the RHS as "predicate-gate then value".

### Alternative-evaluation `(e1, e2, e3)`

A parenthesized comma-list is **NOT** a tuple. It's a fall-through
evaluator: try `e1`; if it succeeds, that's the result; otherwise try
`e2`; etc. If all fail, the whole list fails.

Used pervasively:

```snocone
OUTPUT = GT(xTrace, 4) (DIFFER($'@B') value($'@B'), 'FAIL') ...
// → if @B non-null, output its value; else output 'FAIL'

Tree = tree(t, v, (GT(nc, 0) nc, NULL), (GT(nc, 0) ARRAY('1:' nc), NULL));
// → if nc > 0, use nc and ARRAY(...); else use NULL for both fields
```

Manual ch.9 p.128, ch.15 p.183. The SNOBOL4 equivalent of expression-
level `||`-with-fallback.

### `struct foo { f1, f2 }` Snocone sugar

Snocone adds a struct keyword on top of SNOBOL4's `DATA` function:

```snocone
struct tree { t, v, n, c }
```

Is exactly:

```snocone
DATA('tree(t,v,n,c)')
```

Creates:
- Constructor function `tree(v1, v2, v3, v4)` returning a new instance.
- Field accessors `t(obj)`, `v(obj)`, `n(obj)`, `c(obj)`.
- Field setters via accessor-on-left: `n(obj) = newval;`.

All four core types — `tree`, `link` (stack), `link_counter`,
`link_tag` — are declared this way in their library files.

### `Pop()` vs `Pop(.var)` — dual signature

`stack.sc` defines `function Pop(var)` with two operating modes:

- **`Pop()`** — no arg; returns the popped value via `Pop = value(...)
  ; return;`. Use in expression position: `x = Pop();`.
- **`Pop(.var)`** — one NAME arg; returns `.dummy` and writes the value
  into `$var` indirectly; ends with `nreturn`. Use in pattern position:
  `*Pop(.dummy)` or via `pop = epsilon . *Pop(.dummy);` to discard.

Phase 2 grammar rules don't call `Pop` directly (that's forbidden); the
dual signature matters only for **reading library code**, and for the
driver tail's root-retrieval after `Compiland`.

### `$' '`, `$'  '`, `$'token'` — variable names that are punctuation

A literal string after `$` becomes the name of a variable. So:

```snocone
$'  '   = White;     // variable whose name is two spaces holds the White pattern
$' '    = Gray;      // variable whose name is one space holds the Gray pattern
$'+'    = $'  ' '+' $'  ';  // variable named '+' holds the token-with-ws pattern
$'if'   = $' ' Id $ tx *IDENT(tx, 'if') $' ';  // keyword token
```

In grammar rules, `$'+'` reads as "the value of the variable whose name
is `+`" — which is the pattern. So `$'+' *Expr` reads as "match the +
token (with whitespace envelope) then match `*Expr`". The `$` here is
unary indirection — exactly the same operator as in `$varname`, just
applied to a string literal.

### `upr` / `lwr` — runtime-builtin, NOT library

These appear in `omega.sc` (`LEQ(upr(tx), 'NAME')`) but are NOT
defined in any `.sc` file. They're SPITBOL/Snocone runtime built-ins
returning uppercase / lowercase versions of a string.

Most parsers define their own equivalent inline. parser_snobol4.sc:

```snocone
function sn_upr(s) { sn_upr = REPLACE(s, &LCASE, &UCASE); return; }
```

Use a local pure-string preprocessor like `sn_upr` rather than
assuming `upr`/`lwr` exist — they may behave differently between SCRIP
and SPITBOL, and the local form is portable.

### Cheat for Phase 2 grammar-rule writing

Inside any grammar rule, the only permitted primitives are:

```
shift(p, kind)              // match pat p, push leaf of kind
shift(p, '')                // match-and-discard
reduce(kind, n)             // pop n items, wrap, push
reduce(kind, 'nTop()')      // variable arity from counter
nPush() / nPop()            // counter frame
nInc()                      // bump counter (one per L→R sibling)
nTop()                      // read counter
assign(.var, val)           // set parser-scratch var; usually as *assign(.x, v)
```

Pure string preprocessors (functions with **no** tree-state ops) also
permitted: `dq_unescape`, `unescape_q`, `sn_match`, `sn_upr`, `notmatch`,
`match`, `Qize`, `SQize`, `DQize`.

Forbidden everywhere except library-internal and driver tail:
`Push`, `Pop` (in rules), `Tree`, `tree`, `Append`, `Prepend`, `Insert`,
`Remove`, `IncCounter`, `TopCounter`, `shift_value`, `foldop`,
`reduce_call`, `reduce_prim`, `reduce_opsyn`, every `function X()
{ Push/Pop/Tree/Append/... }`.

The driver tail (after `if (Src ? Compiland) {`) is permitted to
call `Pop()` once to retrieve the root tree for `TDump`.

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
- **DATATYPE is uppercase in SCRIP.** `'NAME'`, `'PATTERN'`, `'STRING'`,
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

1. The reference: `scrip --dump-ast fixture.sc` (existing C frontend).
2. The candidate: `parser_snocone.sc` running through `--run` with
   the shared library blob.

A fixture passes iff both produce the same IR tree. PASS=46 FAIL=0
means parity for everything in the fixture set; that does NOT mean
beauty.sc parses. Always run beauty.sc separately before claiming
"works":

```bash
SCRIP=/home/claude/SCRIP/scrip
SRC=/home/claude/corpus/SCRIP
cat /home/claude/corpus/programs/snocone/demo/beauty/beauty.sc | \
  timeout 30 $SCRIP --run $SRC/global.sc $SRC/tree.sc $SRC/stack.sc \
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

9. **Using `*Ident . captured_name` to capture a bare identifier.** `*Ident`
   includes the internal `$' '` whitespace consumer, so `. captured_name` captures
   `' f'` not `'f'`. Always use `$' ' (*Id . captured_name)` — eat the whitespace
   OUTSIDE the capture group, then capture just the Id text.

10. **Using `tx` in EVAL-based post-match helpers to get a mid-match value.**
    `tx` is a shared scratch variable set by `$ tx` (immediate). By the time
    post-match `.`-based helpers fire (end of whole Compiland match), `tx` holds
    whatever the **last** `$ tx` in the whole match set it to — not what was
    current at the capture site. Use a dedicated `captured_name` / `captured_param`
    etc. variable set via `.` at the right point in the grammar.

11. **Missing semicolons on pattern definitions.** Snocone's frontend may silently
    misparse a definition missing its trailing `;`, merging it with the next line
    into a wrong pattern. Example: `White = white ARBNO(white)` without `;` caused
    `White` to become `white ARBNO(white) Gray` (merged with the next line `Gray = ...`),
    making `White` fail for all multi-statement inputs. Always check the definition
    line ends with `;`.

12. **Confusing a SCRIP engine bug with a parser logic bug (and vice versa).**
    If ARBNO stops after one iteration and you cannot explain why from first principles,
    check for a missing `;` or a stale variable reference (`*kw_else` when `kw_else`
    no longer exists) before assuming the engine is broken.

13. **`notmatch(s, pat)` vs old `notmatch(s, pat, r)` with `*pat`.** The new
    signature passes `pat` as a pattern value directly. In the body, `if (s ? pat)`
    works because `pat` IS the pattern. Do NOT write `if (s ? *pat)` — that would
    dereference `pat` as a variable name, not use it as the pattern itself.

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
| Pattern library | `corpus/SCRIP/{tree,stack,counter,ShiftReduce,semantic,assign,qize,gen,tdump,global}.sc` |
| Reference grammars | `corpus/SCRIP/parser_snobol4.sc` (canonical) |
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

- **Updated** session #69 (2026-05-05). Lon rewrote `parser_snocone.sc`
  and corrected two deep misconceptions: (a) the `.` vs `$` execution model
  (`.` fires post-match in linear sequence; `$` fires immediately during match);
  (b) `*Ident . captured_name` captures whitespace — use `$' ' (*Id . captured_name)`
  instead. Additional bugs found and fixed: missing `;` on `White` definition caused
  silent misparse and multi-statement ARBNO failure; `*Ident . captured_X` throughout
  Call/func/goto/label/param patterns all needed the `$' ' (*Id . captured_X)` fix.
  The new `White = white ARBNO(white)` / `Gray = ARBNO(white)` design and token-baked
  `$' '` design are now confirmed correct and working. PASS=46 FAIL=0.

When you discover a new failure mode or pattern idiom, **add it here**.
Do not let the next session repeat your mistakes.

14. **Global scratch variables clobbered by `*pat` recursion.** When a pattern
    calls itself recursively (e.g. `*if_cmd` inside the else-if branch of `if_cmd`),
    any global variable set by a dot-action inside the recursive call will OVERWRITE
    the value set by the outer call — even if the outer call set it correctly before
    the recursion. This is the `if_nthen` bug (SC-6c-bug): the outer then-body saved
    `if_nthen=8` correctly, but the recursive `*if_cmd` (for the else-if body) also
    called `Body('if_nthen')` and saved `if_nthen=1`, clobbering the outer value.
    Fix: use a push/pop stack (string-encoded, e.g. colon-separated front-push) to
    save and restore any global variable that a recursive pattern also writes.
    Pattern: `Save_X() nPush() *recursive_pat ... nPop() Restore_X()`
    where `save_x` pushes the current value and `restore_x` pops it back.
    Stack pop without ARB: `SPAN(digits) . top (':' REM . rest | '')`.

---

## Handoff note — session 11 (2026-05-07) end state

Gates: smoke PASS=5 FAIL=0, parser PASS=67 FAIL=0. corpus @ HEAD.

**SC-10 landed:** switch/case/default. Key lessons:

19. **Pop case value BEFORE implicit-break push.** `switch_case_label` pops the case value expr from the tree stack. If implicit-break push happens first, it lands on top and `Pop()` grabs the goto instead of the value. Always pop the expression you need before pushing anything new.

20. **tmp=disc stmt lives on the OUTER frame, not inside Body.** `switch_head_alloc` fires before `Body('sw_nbody')` opens its inner `nPush`. So the tmp-assign goes to the Compiland frame directly (via `nInc()` in `switch_cmd`). `finalize_switch`'s `pop_body(n)` only sees body stmts (case labels + bodies). Push dispatch chain and remaining body AFTER `pop_body`, not including `body[1]` as tmp.

21. **Implicit-break tracking: use null-string sentinel for "first case".** `sc_sw_last_body_n = ''` (null) means no previous case yet. `DIFFER(sc_sw_last_body_n)` fails on null, so first case never gets a spurious implicit break. After each case label, set `sc_sw_last_body_n = nTop()` (inner frame counter). At next case, if `nTop() != sc_sw_last_body_n`, the body was non-empty → emit implicit break.

22. **`$'case'` consumed in Command, so `case_cmd` starts at the value.** `Command = ... | $'case' case_cmd | ...` — the `$'case'` token is part of the Command alternation, NOT part of `case_cmd`. `case_cmd = *Expr0 Switch_case_label() $':'`.

**Next:** SC-11 to be defined by Lon. The GOAL file's rung ladder is now complete through SC-10. Possible next rungs: alt-eval `(e1, e2, e3)`, multi-file `-include`, or the `tree_equal` crosscheck gate.

Gates: smoke PASS=5 FAIL=0, parser PASS=63 FAIL=0. corpus @ HEAD.

**SC-9 landed:** struct definition → DATA() call. Key implementation notes:
- `Emit_struct()` uses `epsilon . thx . *emit_struct()` with NO EVAL embedding — `emit_struct()` reads `cur_struct_name` and `sc_struct_fields` as globals at match time. This avoids the EVAL-captures-at-build-time trap.
- `struct_field_list = struct_field_first ARBNO(struct_field_rest) | epsilon` — the `| epsilon` branch handles empty `struct T {}` and leaves `sc_struct_fields = ''`, producing `DATA('T()')`.
- `cur_struct_name` assigned via `. *assign(.cur_struct_name, token)` in `struct_cmd` — fires before `Emit_struct()` in the post-match linear sequence.
- **Next:** SC-10 (switch/case/default). Read `snocone_parse.y` lines around `T_SWITCH`/`sc_switch_head_new`/`sc_finalize_switch` for the C frontend lowering. SC-8's break stack is reused as the switch's break target.

Gates: smoke PASS=5 FAIL=0, parser PASS=60 FAIL=0. corpus @ `3420666`.

**SC-7 landed:** augmented assign (`+=` `-=` `*=` `/=` `^=`). Key implementation note:
- `E_*` constants like `E_ADD = "'E_ADD'"` hold strings WITH surrounding single quotes — designed for EVAL embedding only. In direct Snocone code use string literals: `Tree('E_ASSIGN', ...)`.
- `Reduce_augmented(op)` uses `EVAL("epsilon . thx . *reduce_augmented(" op ")")` — NO extra quotes around `op` because `op` already IS `'E_ADD'`.
- Tree nodes are immutable value semantics — sharing lhs in two child positions is safe.

**SC-8 landed:** break/continue with loop-label stacks. Key lessons:

15. **Global loop-label variables (while_ltop/while_lend) are clobbered by nested loops.**
    Same root cause as SC-6c's `if_nthen` clobber. Fix: `finalize_while` reads the
    labels from the break/continue stacks (via `top_break_label()`/`top_continue_label()`)
    instead of the globals `while_ltop`/`while_lend`. The stacks hold the right value
    for the current (innermost) loop throughout finalize.

16. **Label allocation order must match oracle exactly — no normalization in gate.**
    The gate compares label names byte-for-byte. `_Lcont_0001, _Lend_0002, _Ltop_0003`
    means `_Lcont` must be allocated first in `for_head_alloc`. Verify oracle allocation
    order before implementing any new label allocations.

17. **`BREAK(':')` fails when the stack has only one element (no `:` in string).**
    Use `SPAN('_' digits &LCASE &UCASE) . top (':' REM . rest | '')` to parse both
    single-element (`_Lend_0002`) and multi-element (`_Lend_0004:_Lend_0002`) stacks.

18. **Function name collision in pattern capture.** `BREAK(':') . top_break_label`
    captures into the function's OWN name variable (Snocone convention), clobbering
    the return value slot. Always use a distinct local variable name for captures:
    `SPAN(...) . top` then `top_break_label = top`.

**Next:** SC-9 (struct). See GOAL-PARSER-SNOCONE.md for full spec.

**Exact commits:**
- corpus @ `7a17ff0` — SC-6c-bug fix: save_if_nthen/restore_if_nthen
- .github @ (see below) — PRIMER + GOAL + PLAN updated

**SC-6c-bug / SC-6c status:** BOTH CLOSED. PARSER-SC-6 fully done.
beauty.sc: 1148/1148 stmts, byte-identical to oracle. The bug was a global variable
clobber (not a counter-frame depth issue as previous sessions suspected).

**Critical things the next Claude must know (in addition to earlier entries):**
- Global variables set by dot-actions are clobbered when a pattern recurses into itself.
  `if_nthen` was overwritten by nested `*if_cmd`. Fix pattern: `Save_X() nPush() *rec nPop() Restore_X()`.
- Stack pop without ARB: `SPAN(digits) . top (':' REM . rest | '')` — O(1), no ARB.
- **Never use ARB** — Lon's rule. Use BREAKX, BREAK, SPAN, or REM instead.

---

## Handoff note — session 2026-05-07 (PARSER-RK-24 closure)

**PARSER-RK-24 LANDED** — PASS=132 FAIL=0. corpus@78bdcb9.

19. **Match-time side effects in failed alternations are NOT rolled back.**
    `epsilon . *push_var()` — the `*push_var()` fires at MATCH TIME (via deferred `*`
    operator), not post-match like `.`. With `&FULLSCAN=1`, the engine explores ALL
    alternation paths, including ones that ultimately fail. Any match-time side effect
    (`Push`, `Pop`, `nPush`, `nPop`, `nInc`) from a FAILED alternative PATH is permanent.
    
    The `class_and_main` bug: `SayFhStmt = $'say' $'(' *Expr $',' ...` — when
    `say($d.name)` was tried, the inner `*Expr` matched `$d` via `VarScalar Push_var`,
    firing `push_var()` and pushing `(E_VAR d)`. The comma check then failed — but
    `(E_VAR d)` stayed on the tree stack, becoming a stray child of main.
    
    **Rule**: Any grammar alternative using `*fn()` helpers (push_var, nPush, nInc, etc.)
    inside a pattern that might fail MUST use `FENCE` or structural disambiguation to
    prevent the side effect from firing before failure is certain:
    
    ```snocone
    // WRONG — push_var fires before comma check, stray push on failure:
    FooFhStmt = ( $'foo' $'(' *Expr $',' *Expr $')' $';' Finish_foo_fh );
    
    // RIGHT — FENCE after VarScalar, before Push_var:
    FooFhStmt = ( $'foo' $'(' VarScalar FENCE $',' Push_var *Expr $')' $';' Finish_foo_fh );
    ```
    
    This is a stronger constraint than the `ARBNO(X)` definition-time capture rule —
    it applies to ANY alternation point where a helper with side effects is used.
    Scan all grammar alternatives for this pattern when adding new statement forms.


20. **SNOBOL4/Snocone `while` loop idiom pre-increments before the body.**

    The canonical SNOBOL4 loop `while (i = LT(i, n) i + 1) { body }` assigns
    `i = LT(i,n)` (which returns `i` on success), then concatenates `i + 1`...
    
    Actually in Snocone, `while (i = LT(i, n) i + 1)` means: evaluate `LT(i, n)`
    (returns `i` if `i < n`, else fails); then evaluate `i + 1` (arithmetic, giving
    `i+1`); assign that value to `i`. So the condition ADVANCES `i` before the body.
    
    **Consequence:** to iterate `i` from 2 to N, you must initialize `i = 1` (not `i = 2`),
    because the first condition evaluation gives `i = LT(1, N) 2 = 2` and then the body
    runs with `i = 2`. Starting at `i = 2` causes the body to first run with `i = 3`.
    
    **Safer pattern — explicit post-increment (no ambiguity):**
    ```snocone
    i = 2;
    while (GE(i, 0) LT(i, idxN + 1)) {
        // body uses i = 2, 3, ..., idxN
        i = i + 1;
    }
    ```
    
    Or simply count DOWN (as in `decompose_call`/`decompose_sub`):
    ```snocone
    i = nargs;
    while (GE(i, 1)) { ... use kids[i] ...; i = i - 1; }
    ```
    
    Both forms are unambiguous and avoid the pre-increment trap.
    
    **Discovered:** parser_rebus.sc RB-FW-10 (2026-05-07) — `lower_atom(E_IDX)`
    else-branch started `idxI=2` but the first body iteration saw `idxI=3`, skipping
    the second arg of `a[2, 3]`.


---

## Assumption verification grid — SCT-SN4-ERR041 session (2026-05-21d, Opus 4.7)

During the SCT-SN4-ERR041 fix, every SNOBOL4/SPITBOL/Snocone fact relied on was
recorded, then verified against the SPITBOL Manual v3.7 (fetch:
`https://raw.githubusercontent.com/spitbol/x32/master/docs/spitbol-manual-v3.7.pdf`),
the library source in `corpus/SCRIP/`, and empirical runs under `sbl -bf`. Result:
24 confirmed TRUE, 1 FALSE, 2 refined. Keep this grid — it is a vetted reference for
the next parser session.

| # | Fact | Verdict | Evidence |
|---|------|---------|----------|
| 1 | ERROR 041 = "FIELD function argument is wrong datatype" | ✅ TRUE | Manual App D (error-code table, code 41) |
| 2 | `DATA('tree(t,v,n,c)')` makes field accessors `t/v/n/c` that demand the matching type, else ERROR 041 | ✅ TRUE | Manual Ch 8 (Program-Defined Data Types); empirical `t('not_a_tree')`→041 |
| 3 | `OUTPUT = (failing-expr)` emits **no line at all** | ✅ TRUE | Empirical. (Earlier "blank lines" were `OUTPUT =` with empty RHS — null assignment — emitting a blank, NOT failing-RHS lines.) |
| 4 | `reduce(t, n)` net stack change = −(n−1) | ✅ TRUE | ShiftReduce.sc: Pop loop ×n, Push ×1 |
| 5 | `shift(p, t)` pushes `tree(t, matched_text)`, net +1 | ✅ TRUE | semantic.sc + ShiftReduce.sc |
| 6 | nPush/nInc/nTop/nPop are a counter stack independent of the semantic stack | ✅ TRUE | counter.sc (link_counter linked list) |
| 7 | `reduce('TT_STMT','nTop()')` uses the EXPRESSION-DATATYPE check inside `Reduce` | ❌ FALSE | The `'nTop()'` string is build-time-interpolated into the EVAL pattern as a bare `nTop()` call resolved at MATCH time, returning INTEGER. The EXPRESSION-DATATYPE branch in `Reduce` serves a different path. |
| 8 | Counter is a contract: each `nInc()` ↔ one net item on the semantic stack at frame end | ✅ TRUE | The bug + fix proves it |
| 9 | A `reduce(t,k)` inside a sub-pattern lowers the surrounding net count by k−1; grammar must account | ✅ TRUE | Bug analysis, validated by fix |
| 10 | `POS(0)`/`RPOS(0)` are zero-width subject anchors (start/end) | ✅ TRUE | Manual Ch 6 (POS/RPOS) |
| 11 | `ARBNO(P)` matches 0+ of P, shy | ✅ TRUE | Manual Ch 9 ("behaves like ( \"\" \| PAT \| PAT PAT \| … )") |
| 12 | `FENCE(P)` matches P; backtracking from outside does not re-enter | ✅ TRUE | Manual Ch 9 + Ch 19 ("pass through pattern on rematch") |
| 13 | `*expr` (unary star) defers evaluation to match time | ✅ TRUE | Manual Ch 7 (Unevaluated Expressions) |
| 14 | `epsilon` matches the empty string, always succeeds | ✅ TRUE (refined) | NOT a SPITBOL primitive — a project convention: an undeclared var is null, and null in pattern context matches empty. Empirical: `DATATYPE(epsilon)=STRING`, `SIZE(epsilon)=0` |
| 15 | `'literal'` and `"literal"` interchangeable | ✅ TRUE | Manual Ch 3 |
| 16 | xTrace is a project-local global | ✅ TRUE | global.sc:29 |
| 17 | `OUTPUT = expr` writes a line iff expr succeeds | ✅ TRUE | Empirical (see #3 for the empty-RHS caveat) |
| 18 | `?` is binary pattern-match, priority 1 | ✅ TRUE | Manual Ch 15 priority table; Ch 9 |
| 19 | Semantic stack `$'@S'` is one global linked list across the whole parse | ✅ TRUE | stack.sc |
| 20 | Popping one too many reaches the previous statement's TT_STMT, producing a wrong-typed child | ✅ TRUE | xTrace walk + fix |
| 21 | Driver tail iterates `c(ptree)[i]`; the type error surfaces at the iteration site | ✅ TRUE | Trace pinned it to `cmd = ITEM(c(ptree),i)` |
| 22 | `OPSYN('~','shift',2)` and `OPSYN('&','reduce',2)` | ✅ TRUE | semantic.sc lines 1–2 |
| 23 | `sbl -bf`: `-b` suppress sign-on, `-f` disable case-folding | ✅ TRUE | Manual Ch 13 option list |
| 24 | `scrip --dump-sno` is the transpile entry; `lower_sno.c` walks the AST | ✅ TRUE | Verified by running |
| 25 | `--dump-ast` (oracle) uses attribute form `(STMT :eq :subj …)`; candidate uses positional `(TT_STMT …)` | ✅ TRUE | Empirical, both run |
| 26 | Implicit pattern-match by juxtaposition (`SUBJECT PATTERN`, whitespace = match) is standard SNOBOL4 | ✅ TRUE | Manual Ch 6 ("In SNOBOL4, a blank can signify a pattern match as well as concatenation") |
| 27 | Counter-frame invariant: (pushes within frame) == nTop() at frame end | ✅ TRUE | Same as #8 |

**Takeaway for future parser work:** #7's correction matters when reasoning about how
`reduce(tag, 'nTop()')` resolves arity — it is a match-time `nTop()` call baked into the
EVAL'd pattern string, not a datatype-dispatched re-evaluation. And #14: `epsilon` works
only because undeclared variables are null; never assume it is a defined primitive.
