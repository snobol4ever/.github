# GOAL-PARSER-SNOBOL4.md — PARSER-SNOBOL4 pattern-based frontend in Snocone

**Repo:** corpus+one4all
**Branch:** `parser` (one4all only — `corpus` and `.github` stay on `main`)
**Sibling ladder:** `GOAL-LANG-SNOBOL4.md` — every PARSER-SN-N rung names its
sibling SN-K rung(s). The existing SNOBOL4 frontend (`src/frontend/snobol4/`)
is the oracle; PARSER-SN is a second frontend that must agree with it.

**Done when:** A Snocone program `parser_snobol4.sc` reads SNOBOL4 source,
runs one `Compiland` PATTERN that builds the canonical IR tree, and for
every test program in the rung corpus the parser's output matches the
existing frontend's `--dump-parse` output (whitespace-normalized per
FW-6 variant B).

> **Cross-pollination notice (session #62, 2026-05-03):** three design
> issues raised against PAT-IC apply to all six PARSER-* frontends.
> See `GOAL-PARSER-ICON.md ## Design issues` (D1–D3). Tracked under
> PARSER-IC-INFRA-1/-2 — when those land, the same refactor lands here.

---

## Cross-pollination

All six PARSER-* parsers share `Compiland`/`Shift`/`Reduce`/`Push`/`Pop`/`Top`/
`tree`/`TDump`/`stack` from `corpus/programs/scrip/`. Bug fixes there
benefit all six. Token-level rules and the `Command` body are language-
specific; the spine is identical:

```
Compiland = nPush() ARBNO(<inlined Command body>) reduce("'Parse'", 'nTop()') nPop()
```

PARSER-SN gets two oracles: the existing SNOBOL4 frontend (in-process
crosscheck) AND the SPITBOL byte-identical oracle from `GOAL-LANG-SNOBOL4`.
It is the safest place to start the family.

---

## Style Guidelines for `parser_*.sc` — canonical (binding on all six PARSER-*)

These guidelines apply to **every** `parser_<lang>.sc` in the family
(SNOBOL4, Snocone, Icon, Prolog, Raku, Rebus).  Sibling goal files
(`GOAL-PARSER-SNOCONE.md`, `GOAL-PARSER-ICON.md`, ...) cross-reference
this section.  The canonical model is `beauty.sno` /
`corpus/programs/snocone/demo/beauty/beauty.sc` — read both before
authoring or modifying any `parser_*.sc`.

### 1. Names match the official language specification

Pattern-variable names mirror the language's official BNF and the
existing frontend's parser/lexer.  Sources of truth, in priority order:

1. The frontend's own `.l` / `.y` (token enum, parse non-terminals)
   and lowering module's IR-tag enum (`expr_dump` or equivalent).
2. The official language standard (e.g. `corpus/programs/ebnf/s4-no.ebnf`
   for SNOBOL4; ISO/IEC 13211-1 for Prolog; analogous for the others).
3. `beauty.sno` / `beauty.sc` for self-host concepts (`Integer`,
   `String`, `Id`, `Real`, `Gray`, `White`, `Expr0..Expr17`, ...).

The cross-PARSER spine names (`Compiland`, `Command`, `shift`, `reduce`,
`Push`/`Pop`/`Top`, `nPush`/`nInc`/`nTop`/`nPop`, `tree`/`Tree`/`TDump`,
`stack`) are the only invented names; per-language non-terminals and
token classes are not invented.

**Operational oracle wins where canonical BNF and existing frontend
disagree.**  beauty.sno's arith rules are right-recursive; `snobol4.y`
and `--dump-parse` are left-associative.  PARSER-SN follows the oracle
(left-associative iterative folding) but keeps beauty.sno's tier names.

### 2. `White` and `Gray` are attached, never referenced in the main grammar

`White` matches required whitespace (including `+`/`.` continuation
across nl); `Gray` matches optional whitespace.  Per beauty.sno:

```
Gray  = *White | epsilon;
White = ( SPAN(' ' tab) FENCE(nl ('+' | '.') FENCE(SPAN(' ' tab) | epsilon) | epsilon)
        | nl ('+' | '.') FENCE(SPAN(' ' tab) | epsilon)
        );
```

Whitespace is **never** sprinkled into grammar rules directly.  It is
attached at the boundaries of operator and special-character tokens,
and it disappears from the visible grammar.  Inside the per-token
build-up (see §3), `*White`/`*Gray` decorate the token; outside, the
main grammar reads as if whitespace did not exist.

### 3. Reserved-word and special-character tokens use `$'name'` form

Tokens whose names would collide with Snocone reserved words, or that
are non-identifier punctuation, use Snocone's `$'...'` indirection:

```
$'='    = *White '='  *White;     // operator: optional whitespace each side
$'**'   = *White '**' *White;
$','    = *Gray  ','  *Gray;
$'('    = '('   *Gray;            // open-bracket: ws after only
$')'    = *Gray ')';              // close-bracket: ws before only
$'if'   = *White 'if' *White;     // (Snocone keyword example)
```

For tokens whose names are **not** Snocone reserved words, use a plain
identifier — the assignment LHS is just the name:

```
S = $' ' 'S';                     // optional-leading-space S goto-letter
F = $' ' 'F';
```

Two whitespace conventions to memorize:

| Form        | Meaning                              |
|-------------|--------------------------------------|
| `$' '`      | OPTIONAL whitespace (zero or more spaces/tabs) |
| `$'  '`     | REQUIRED whitespace (one or more)    |

The single-space and two-space `$' '`/`$'  '` token names are the
beauty.sno-legible convention — use them rather than spelling out
`*Gray`/`*White` at every grammar reference.

### 4. Tree-build decorations use shift/reduce, not bare deferred calls

The pre-OPSYN form is:

```
primitive . tx epsilon . *Func(literal, tx)
```

This collapses to the function-call form:

```
primitive . tx Func(literal, "tx")
```

Where `Func` is `shift` (consume token, push leaf) or `reduce` (pop N
children off the n-counter stack, push N-ary node with given tag).
With the OPSYN'd infix shortcuts (`semantic.sc`):

```
primitive ~ "tx"             // shift:  primitive consumed, leaf pushed under tag "tx"
("tx" & "expression")        // reduce: EVAL("expression") gives N; pop N, push N-ary tag "tx"
```

(The reduce form's expression is evaluated at match time via internal
`EVAL`; the most common values are an integer literal `2`, `1`, or
`'nTop()'` for n-ary collections.)

⚠ **Today PARSER-* parsers MUST use the function-call form**
`shift(p, t)` / `reduce(t, n)` rather than `~`/`&` infix.  Snocone's
parser binds `~` as a unary operator at parse time, so OPSYN at runtime
does not retro-rebind the infix form.  See `INFRA-11b` below — if/when
that is resolved, sibling parsers may revert to the verbatim
beauty.sno `~`/`&` infix.

### 5. n-ary trees use `nPush() ... nInc() ... nTop() / nPop()`

The same pattern-producing-function technique scales to variable-arity
children.  `nPush()` opens a counter frame, every contributing child
fires `nInc()` (embedded as a pattern, not as a deferred call — see
LESSON 1 in the Watermark), `nTop()` reads the count, `nPop()` closes
the frame:

```
ExprList  = nPush() *XList ("'ExprList'" & '*(GT(nTop(), 1) nTop())') nPop();
XList     = nInc() (*Expr | epsilon ~ '') FENCE($',' *XList | epsilon);
```

⚠ `nInc()`/`nPush()`/`nPop()`/`nTop()` are PATTERN-PRODUCING functions
— they return patterns that fire `IncCounter()`/`PushCounter()`/etc.
at MATCH time.  Embed them as patterns inside grammar rules, not as
side-effect calls inside escapes.  Inside escape-helper functions,
call the BARE runtime: `IncCounter()`, `Push()`, `Pop()`.  See LESSON 1
in the Watermark for the textbook error.

### 6. AST/IR tag names use `E_*` from `EXPR_t`

Tag strings inside `shift()` and `reduce()` calls must match the IR
tags emitted by the existing frontend's dumper — for SNOBOL4 these
are `E_VAR`, `E_ILIT`, `E_QLIT`, `E_RLIT`, `E_FNC`, `E_SEQ`, `E_ALT`,
`E_LEN`, `E_BREAK`, `E_SPAN`, `E_ANY`, `E_NOTANY`, `E_CAPT_COND_ASGN`,
`E_CAPT_IMMED_ASGN`, `E_KEYWORD`, `E_DEFER`, `E_IDX`, plus role-slot
wrappers `:lbl`, `:subj`, `:pat`, `:repl`, `:goS`, `:goF`, `:goU`,
`:eq`, `:end` (see "SNOBOL4 → existing-frontend tree shapes" below).
The beauty.sno-native tag names (`Stmt`, `Id`, `String`, `Call`,
`..`, `|`, ...) are the wrong shape for the `--dump-parse` oracle and
must be rewritten — see `GOAL-PARSER-PROLOG.md` and
`GOAL-PARSER-ICON.md` for the per-language tag tables.

### 7. Identifier conventions

| Kind             | Convention            | Examples                                  |
|------------------|-----------------------|-------------------------------------------|
| Variable         | lowercase snake_case  | `tx`, `sf`, `n_kids`, `cur_line`          |
| Function         | UpperCamelSnake       | `Push`, `Pop`, `TDump`, `IncCounter`, `nPush` |
| Pattern (rule)   | UpperCamel            | `Id`, `Integer`, `Expr0`, `ExprList`, `Stmt`, `Compiland` |
| Token (special)  | `$'...'`              | `$'='`, `$'**'`, `$','`, `$'('`, `$' '`   |
| AST tag          | `E_*` (per language)  | `E_VAR`, `E_ILIT`, `E_QLIT`, `E_FNC`      |
| Role-slot tag    | `:`-prefixed          | `:subj`, `:pat`, `:repl`, `:lbl`          |

⛔ **No identifier starts with `_`.**  Underscore-prefix is reserved
for compiler-generated names (synthetic labels, anonymous bindings,
internal scaffolds).  User code in `parser_*.sc` never spells one.

The goto-letter token names `S` (success) and `F` (failure) are the
exception that proves the rule — they are single uppercase letters,
neither pattern-rule nor function, defined per beauty.sno as
`S = $' ' 'S'` and `F = $' ' 'F'`.

### 8. Layout and formatting

These rules come from `RULES.md ## C code style` extended for
Snocone source:

- **120-character line maximum.**
- **Single-statement bodies live on one line, no braces:**
  ```
  if (x) statement ;            // YES
  if (x) { statement; }         // NO — gratuitous braces
  while (cond) IncCounter() ;   // YES
  ```
  Braces are only for multi-statement bodies.
- **Section dividers, never blank lines:**
  - Major sections: `/*====================...====================*/` (120 chars)
  - Minor sections: `/*--------------------...--------------------*/` (120 chars)
  - Blank lines as separators are forbidden — use comment dividers.
- **Maximize horizontal space.**  Pack related rules onto the same
  line where they fit within 120 cols.  beauty.sno's
  `$'=' = *White '=' *White; $'?' = *White '?' *White;` per line
  packing of the operator-token block is the model.
- **Multi-line wrapping uses constant 2-space nested indent with
  vertical balancing of parens and binary operators:**
  ```
  Real = ( SPAN(digits)
            ('.' FENCE(SPAN(digits) | epsilon) | epsilon)
            ('E' | 'e') ('+' | '-' | epsilon) SPAN(digits)
         | SPAN(digits) '.' FENCE(SPAN(digits) | epsilon)
         );
  ```
  The opening `(` aligns the first alternative's first token; each
  continuation line indents by 2 more; the matching `|` and `)` align
  vertically with the opener.

### 9. Read beauty.sno and beauty.sc end-to-end before authoring

The model is internalized, not consulted line-by-line.  Before opening
or modifying any `parser_*.sc`, read both source files in full:

- `corpus/programs/snobol4/demo/beauty/beauty.sno` — original SNOBOL4
  self-host beautifier.  Lines 47–245 are the grammar block; the rest
  is the pretty-printer.  This is the canonical manifestation of every
  rule above.
- `corpus/programs/snocone/demo/beauty/beauty.sc` — the Snocone port,
  same grammar shape, demonstrates how the SNOBOL4 patterns translate
  to `.sc` syntax (`shift()`/`reduce()` function-call form,
  `function ... { ... }` block syntax, structured `if`/`while`).

---

## Session Setup

```bash
( cd /home/claude/one4all && git fetch origin parser 2>/dev/null; git checkout parser 2>/dev/null || git checkout -b parser origin/parser 2>/dev/null || git checkout -b parser )

bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
bash /home/claude/one4all/scripts/build_spitbol_oracle.sh
```

Gate after setup:
```bash
bash /home/claude/one4all/scripts/test_smoke_snobol4.sh    # existing frontend baseline
bash /home/claude/one4all/scripts/test_scrip.sh            # INFRA watermark
bash /home/claude/one4all/scripts/test_parser_snobol4.sh   # PARSER-SN gate
```

---

## Architecture

```
scrip --pat-snobol4 tiny.sno
         │
         ├─→ existing SNOBOL4 frontend  → CODE_t* t1   (in-process)
         │
         └─→ parser_snobol4.sc Compiland  → CODE_t* t2 (in-process, Snocone)

normalized stdout (parser TDump) ≡ normalized stdout (--dump-parse)  ← gate
```

Long-term, the gate becomes `tree_equal(t1, t2)` via the planned
`scrip --parser-crosscheck` flag (FW-4, deferred). Today it is shell-level
byte-diff with whitespace normalization on both sides.

The driver builds Snocone trees on the shared stack via `Push`/`Pop` from
`stack.sc` and `Tree(...)` from `tree.sc`; the main loop pops each STMT
tree and dumps it via `TDump` from `tdump.sc`.

**Shared SCRIP runtime, Snocone-hosted (`.sc` files)** — all six PARSER
sessions use the same blob. Only `parser_<lang>.sc` changes per session.
Canonical blob order:

```
global.sc tree.sc stack.sc counter.sc ShiftReduce.sc semantic.sc
qize.sc gen.sc tdump.sc assign.sc parser_<lang>.sc
```

**Role-slot / flag wrapper convention** — scrip's `--dump-parse` emits
role-keyword children (`:subj`, `:repl`, `:lbl`, `:pat`, ...) and positional
flags (`:eq`, `:end`). The Snocone `tree(t,v,n,c)` shape doesn't carry
per-child role labels, so we encode roles as wrapper nodes with `:`-prefixed
type tags. `Tree(':subj', '', 1, child)` renders as `:subj <TLump-of-child>`.
`tree(':eq', '')` renders as bare `:eq`. IR-leaf kinds (`E_VAR`, `E_ILIT`,
`E_QLIT`) self-paren in `TValue` so a slot wrapping an IR leaf renders as
`:subj (E_VAR x)`.

---

## SNOBOL4 → existing-frontend tree shapes (the oracle)

Captured from `scrip --dump-parse` on the rung corpus.

| Construct | Existing frontend tree (canonical line) |
|-----------|-----------------------------------------|
| identifier `x`              | `(STMT :subj (E_VAR x))` |
| integer `42`                | `(STMT :subj (E_ILIT 42))` |
| string `'hi'`               | `(STMT :subj (E_QLIT "hi"))` (always double-quoted in dump) |
| `END` line at column 0      | `(STMT :lbl END :end)` |
| `x = 5`                     | `(STMT :eq :subj (E_VAR x) :repl (E_ILIT 5))` |
| `x = 'a' 'b'`               | `(STMT :eq :subj (E_VAR x) :repl (E_SEQ ...))` |
| `S 'a'`                     | `(STMT :subj (E_VAR S) :pat (E_QLIT "a"))` |
| `S 'a' 'b'`                 | `(STMT :subj (E_VAR S) :pat (E_SEQ (E_QLIT "a") (E_QLIT "b")))` |
| `S 'a' \| 'b'`              | `(STMT :subj (E_ALT (E_SEQ (E_VAR S) (E_QLIT "a")) (E_QLIT "b")))` (alt eats LHS) |
| `S ('a' \| 'b')`            | `(STMT :subj (E_VAR S) :pat (E_ALT ...))` (paren keeps split) |
| `S 'a' . X`                 | `(STMT :subj (E_VAR S) :pat (E_CAPT_COND_ASGN ...))` |
| `S 'a' $ X`                 | `(STMT :subj (E_VAR S) :pat (E_CAPT_IMMED_ASGN ...))` |
| `S 'a' = 'b'`               | `(STMT :eq :subj (E_VAR S) :pat ... :repl ...)` |
| `S = `  (empty repl)        | `(STMT :eq :subj (E_VAR S) :repl (E_QLIT ""))` |
| `S 'a' :S(L1)`              | `(STMT :subj (E_VAR S) :pat ... :goS L1)` |
| `LEN(3)` etc.               | `(E_LEN (E_ILIT 3))` — also E_BREAK, E_SPAN, E_ANY, E_NOTANY |
| `F(X)` etc.                 | `(E_FNC F (E_VAR X))` — generic call; name in v, args as children |
| `DEFINE('F(X)')`            | `(E_FNC DEFINE (E_QLIT "F(X)"))` — DEFINE spec is opaque to --dump-parse (DEFINE-as-distinct-IR-kind tracked under `GOAL-IR-DEFINE-KIND.md`) |
| `NOARG()`                   | `(E_FNC NOARG)` — zero-arg call, no children |

**The `:subj` / `:pat` split rule:** parse the body as one expression. If
the top is `E_SEQ` with N≥2 children → child 1 is `:subj`, rest is `:pat`
(unwrap if N=2, otherwise wrap in fresh `E_SEQ`). Any other top (E_ALT,
single atom, E_CAPT_*, E_LEN/BREAK/SPAN/ANY/NOTANY, arith, ...) →
whole expression is `:subj`, no `:pat`.

**Operator precedence** (loose → tight): `|` < concat < `.`/`$` < `^/!/**`
< `*` < `/` < `+/-` < unary `+/-` < atom. `.` and `$` are left-associative
per the oracle (`'a' . X . Y` → `((a . X) . Y)`), even though `s4-no.ebnf`
writes them right-recursively.

---

## Closed rungs — historical record

Step-by-step detail, root-cause writeups, and session-narrative live in git
history under the listed commits. This table is the load-bearing summary.

### INFRA ladder — all GREEN

| Rung | Title | Summary |
|------|-------|---------|
| INFRA-0  | Conditional/immediate-assign capture lvalue bug | `eval_code.c E_CAPT_*_ASGN` E_VAR target path needed lvalue branch |
| INFRA-1  | SCRIP source tree | `corpus/programs/scrip/` + base `.sc` runtime files |
| INFRA-2  | `global.sc` | Named char constants, bit-prefix slices, `digits`, `TRUE`, `FALSE` |
| INFRA-3  | `tdump.sc` (tree printing) | `TLump` + `TValue` ported |
| INFRA-4  | `assign.sc` + `match.sc` | `assign(name, expr)`, membership |
| INFRA-5a | Synthetic-label collision | `snocone_parse.y` `g_sc_label_seq` made monotonic |
| INFRA-5b | `if (str ? PAT = )` in expression | `interp_eval.c E_ASSIGN` E_SCAN-as-lvalue branch |
| INFRA-5c | `E_KEYWORD` dropped in `E_FNC` arg | `eval_code.c` strip `&` on NV lookup |
| INFRA-6  | `case.sc` (lwr/upr/cap/icase) | Verbatim port from beauty/case.sc |
| INFRA-7  | `qize.sc` | Verbatim; tdump TValue uses SqlSQize |
| INFRA-7a | Inline `*assign(...)` not firing | `eval_pat.c` E_CAPT_*_ASGN cases |
| INFRA-8  | `trace.sc` | Verbatim; silent when doDebug=0 |
| INFRA-9  | `omega.sc` | Pattern-construction tracing wrapper |
| INFRA-10 | OPSYN `~` and `&` runtime | Function-call dispatch via APPLY works (→ INFRA-11b) |

### Framework rungs — landed

| Rung | Title | Summary |
|------|-------|---------|
| FW-1 | Generalize TValue for non-scrip-IR leaf kinds | Generic-leaf branch — any letter-start tag with non-empty v(x) → `(TAG val)`; E_QLIT keeps double-quote special branch |
| FW-2 | Multi-child role-slot wrapper | `:`-prefix branch in TLump for n≥2 children → `:role (c1 c2 ...)` |
| FW-3 | Compiland-spine driver loop | Whole-program `Src ? Compiland` match; **Command body inlined** inside ARBNO to dodge the `*Q` indirection bug (see workarounds below) |
| FW-6 | Multi-line TLump / TDump | **Variant B adopted**: TDump uses `gen.sc` width-budget inline-or-fallback, gates normalize whitespace |

### Language rungs — landed

| Rung | Title | Gate |
|------|-------|------|
| SN-0 | atom (literal \| identifier) | PASS=3 |
| SN-1 | assignment | PASS=8 |
| SN-2 | tree-on-stack architectural pivot | PASS=8 (refactor; same corpus) |
| SN-3 | concat / arith — beauty.sno-named Expr-N tiers | PASS=16 |
| SN-4 | control flow (`:S` / `:F` / labels) | PASS=23 |
| SN-5 | patterns (LEN/BREAK/SPAN/ANY/NOTANY, `\|`, `.`, `$`, replacement) | PASS=43 |
| SN-6 | function definition / call (generic `Id LPAREN args RPAREN` → E_FNC) | **PASS=58** ✅ this session |

---

## Active rung ladder

### ⚠ PARSER-SN-7 — canonical shape (session 2026-05-03 PIVOT)

**Context.** Session 2026-05-03 attempted to land the beauty.sno
crosscheck on top of the existing `parser_snobol4.sc` (876 lines,
SN-0..SN-6 PASS=58).  Diagnostic crosscheck revealed ~1084 oracle
stmts vs ~502 parser stmts on beauty.sno — the parser silently
collapses or drops most constructs (bracket-index, &keyword,
continuation lines, deferred `*Id`, comment/control lines, `;`
separator).  More importantly, the underlying shape is wrong
relative to beauty.sno's own self-host grammar AND relative to the
sibling parsers (PARSER-IC, PARSER-PR, PARSER-RK, PARSER-RB) that
have all landed since SN-6.

**The wrong shape.**  `parser_snobol4.sc` today drives parsing through
25 Snocone *functions* (`Expr0..Expr17`, `_try_label`,
`_parse_body_goto`, `_parse_line_cmd`, `_call_args`, ...) called
imperatively per line — `Compiland` is `ARBNO( ... LineCmd nl_one )`
where `LineCmd` captures one line into `_cur_line` and fires
`*_parse_line_cmd()`, which then calls `_try_label`, then
`_parse_body_goto`, which calls `Expr`, which dispatches through
the Expr-N tower.  This is a hand-coded recursive-descent parser
hosted on Snocone, not a Snocone PATTERN parser.

**The right shape (canonical, set by beauty.sno itself).**  beauty.sno's
own grammar — the model PARSER-SN must mirror — is one chained
PATTERN, all `~`/`&` infix (semantically Shift/Reduce), with
`Comment | Control | Stmt` as alternation children of `Command`,
and a single `Compiland` PATTERN that ARBNOs over `*Command`
against the entire source.  Functions exist only for `nPush/nInc/
nTop/nPop`, `Tree`, `Push`/`Pop`, `Shift`/`Reduce`, `pp`, `ss` —
tree-building and semantics — never for parsing dispatch.

The siblings PARSER-IC (672 lines), PARSER-PR (429 lines), PARSER-RK
(755 lines), PARSER-RB (547 lines) all land this shape today.
PARSER-SN at 876 lines is the largest and the only outlier.

**Invariants for the rewrite (all binding):**

1. **One `Compiland` PATTERN, one match against the entire `Src`.**
   The shape is: `Compiland = nPush() ARBNO( nInc() <inlined Command body> ) reduce("'Parse'", 'nTop()') nPop();`
   where the Command body is the alternation `Comment | Control | Stmt`.
   `Src ? Compiland` runs once at the bottom of the driver.  No
   per-line dispatch.

2. **`shift(p, t)` / `reduce(t, n)` from `semantic.sc` for tree
   construction inside patterns.**  These are the OPSYN'd binary
   `~` / `&` of beauty.sno — same semantics, called as functions
   because of INFRA-11b (the Snocone parser binds `~` as unary
   `not` at parse time, before runtime OPSYN takes effect).  Use
   `shift(P, "'identifier'")` everywhere beauty.sno writes
   `(P ~ 'identifier')`, and `reduce("'TAG'", N)` everywhere
   beauty.sno writes `("'TAG'" & N)`.

3. **`nPush()` / `nInc()` / `nTop()` / `nPop()` for n-ary trees.**
   Every grammar rule that produces a variable-arity child list
   (alternation, sequence, expression list, statement body) wraps
   the body in `nPush() ... reduce("'TAG'", 'nTop()') nPop()` and
   each contributing child fires `nInc()` immediately before its
   shift/reduce.  This matches the sibling parsers and beauty.sno
   exactly.

4. **No Snocone `goto` when structured control would do.**  The driver
   uses `while ((Line = INPUT)) { ... }` to accumulate `Src`,
   `if (Src ? Compiland) { ... }` for the single top-level match,
   and `while (LE(i, n_kids)) { ... }` to walk the Parse tree's
   children for `TDump`.  No labels, no `goto` anywhere.  This
   tracks the PARSER-PR style invariant ("no goto/labels in this
   file").

5. **Functions only for tree building and semantics.**  Allowed: the
   shared `tree.sc` / `stack.sc` / `counter.sc` / `ShiftReduce.sc`
   helpers; `Tree(...)` constructors; `assign(name, expr)` /
   `match(s, p)` / `icase(s)` / `lwr` / `upr` from beauty's reuse;
   small `*deferred()` escapes that capture text into a global
   slot or shape a node before pushing.  Forbidden: any function
   that drives parse dispatch (no `Expr0..Expr17`, no `_try_label`,
   no `_parse_body_goto`, no `_parse_line_cmd`).  The Expr-N tower
   becomes Expr-N PATTERNS with the same names (`Expr`, `Expr0`,
   ..., `Expr17`) — beauty.sno's own names — chained by FENCE'd
   alternation per the precedence ladder.

**The rewrite proceeds in narrow rungs, each gated by a focused
fixture in `corpus/programs/snobol4/parser/`.**  This re-uses the
existing 58 fixtures as regression coverage AND extends them.  Each
rung lands a slice of the grammar, shaped per the invariants above.

#### PARSER-SN-7-0 — scaffolding

- [ ] Open a feature branch `parser-sn-rewrite` off `parser`.  Keep
      the existing `parser_snobol4.sc` reachable on `parser` until
      the rewrite hits PASS=58 parity.
- [ ] Write `parser_snobol4_v2.sc` from scratch on the parser_prolog.sc
      / parser_icon.sc model.  Body: token-class atom recognizers
      (`Id`, `Integer`, `String`, `Real`, `White`, `Gray`), the
      Expr-N tower as PATTERNS (not functions), `Goto`, `Stmt`,
      `Comment`, `Control`, `Command`, `Compiland`, and the driver.
- [ ] Land the gate-script update: `test_parser_snobol4.sh` loads
      `parser_snobol4_v2.sc`.  Gate goal: ALL 58 existing fixtures
      pass under the new shape, no regressions.
- [ ] On parity → swap `parser_snobol4_v2.sc` → `parser_snobol4.sc`,
      delete the old, merge `parser-sn-rewrite` → `parser`.
- **Gate:** PASS=58 FAIL=0 on the new shape, byte-identical output.

#### PARSER-SN-7-1 — bare label-only line

- [x] Fixture `cf_label_bare.sno` added (session 2026-05-03 — open
      against existing parser, will pass automatically once SN-7-0
      lands the canonical Stmt pattern with `Label = BREAK(' ' tab nl ';') ~ 'Label'`).
- [ ] Confirm PASS=59 after SN-7-0.

#### PARSER-SN-7-2 — &KEYWORD recognition

- [ ] Fixtures `kw_fullscan.sno`, `kw_maxlngth.sno`, `kw_ucase.sno`,
      `kw_lcase.sno` — assignment LHS, RHS, and pattern-arg uses of
      protected and unprotected keywords.
- [ ] Per beauty.sno: `ProtKwd = '&' SPAN(&UCASE &LCASE) ~ 'ProtKwd'`,
      `UnprotKwd = '&' SPAN(&UCASE &LCASE) ~ 'UnprotKwd'`.  These
      become alternatives in `Expr14`.
- **Gate:** keywords emit `(E_KEYWORD <NAME>)` matching the oracle.

#### PARSER-SN-7-3 — bracket index `x[i]`, `x[i, j]`

- [ ] Fixtures `idx_simple.sno`, `idx_multi.sno`, `idx_nested.sno`,
      `idx_in_assign_lhs.sno`.
- [ ] Add `Expr15` / `Expr16` per beauty.sno: `Expr15 = Expr17 FENCE( nPush() Expr16 ("'[]'" & 'nTop() + 1') nPop() | epsilon )`.
- **Gate:** `(E_IDX <obj> <i> ...)` matches the oracle.

#### PARSER-SN-7-4 — `+` / `.` continuation lines

- [ ] Fixtures `cont_plus.sno`, `cont_dot.sno`, `cont_chain.sno`.
- [ ] Per beauty.sno's `White` definition: continuation is part of
      the whitespace token class, swallowed by `White` between every
      two adjacent grammar units.  Specifically: `White = SPAN(' ' tab) FENCE( nl ('+' | '.') FENCE( SPAN(' ' tab) | epsilon ) | epsilon ) | nl ('+' | '.') FENCE( SPAN(' ' tab) | epsilon )`.
- **Gate:** multi-line continued statements emit a single STMT.

#### PARSER-SN-7-5 — comment & control lines

- [ ] Fixture `mixed_comment_control.sno`.
- [ ] Per beauty.sno: `Comment = '*' BREAK(nl)`, `Control = '-' BREAK(nl ';')`.
      Both alternatives of `Command` shift their captured text via
      `*Comment ~ 'comment' ("'Comment'" & 1) nl`.  At TDump time these
      contribute STMT children — but the existing scrip frontend's
      `--dump-parse` drops comments and processes control lines via
      preprocessor-include semantics.  PARSER-SN-7-5 must
      either drop these STMT children at emit-time OR (cleaner)
      have `Command` not emit them — match whichever the oracle does.
- **Gate:** comment/control lines do not produce extra STMTs in dump.

#### PARSER-SN-7-6 — `*Id` deferred-pattern reference

- [ ] Fixtures `defer_simple.sno` (`P = *Q`), `defer_alt.sno` (`P = *Q | *R`),
      `defer_in_pat.sno` (`x ? *P`).
- [ ] `Expr14`'s prefix-`*` branch: `'*' Expr14 & "'*' 1"` — the
      unary `*` in beauty.sno's Expr14 alternation list.  Must render
      as `(E_DEFER <child>)` in the oracle's tree shape.
- **Gate:** `*Id` constructs emit `(E_DEFER (E_VAR Id))`.

#### PARSER-SN-7-7 — `;` mid-line statement separator

- [ ] Fixture `semi_separator.sno` (`x = 1 ;* comment` and `x = 1; y = 2`).
- [ ] Per beauty.sno's `Command`: alternation tail is `(nl | ';')`.
      Each Command consumes either a newline or a semicolon; multiple
      Commands per source line are supported.
- **Gate:** semi-separated statements emit two STMTs.

#### PARSER-SN-7-8 — beauty.sno full crosscheck

- [ ] `parser_snobol4_v2.sc` parses `beauty.sno` (627-line `corpus/programs/snobol4/demo/beauty/beauty.sno`).
- [ ] `tree_equal` against `--dump-parse`'s tree returns true (use
      whitespace-normalized byte-diff until PARSER-SN-FW-4 lands).
- [ ] Running the parser-built tree through `--ir-run` produces output
      byte-identical to the SPITBOL oracle (Milestone 1 gate).
- **Gate:** beauty.sno PASSES under both oracles.

#### PARSER-SN-7-9 — style audit remediation (guidelines, not laws)

**Context.**  Audit of `parser_snobol4.sc` (200 lines, session
2026-05-04) against the nine § Style Guidelines for parser_*.sc.
Most guidelines are already honored; a few are genuine deviations,
and a few are guideline-vs-pragma tensions inherited from beauty.sno.
Each step below is a guideline, not a law — the intent is to record
the deviation and let the operator decide rather than silently leave
it.  Mixed checkboxes signal which are mechanical fixes vs decision
points.

**Already tracked elsewhere — not duplicated as steps here:**

  - § 6 (`E_*` IR tags) — every `shift()`/`reduce()` tag string today
    is the beauty.sno-native form (`'Stmt'`, `'Id'`, `'String'`,
    `'Real'`, `'Integer'`, `'Call'`, `'Comment'`, `'Control'`,
    `'Parse'`, `'ExprList'`, `'='`, `'?'`, `'|'`, `'..'`, `'@'`,
    `'+'`, `'-'`, `'/'`, `'*'`, `'%'`, `'^'`, `'$'`, `'.'`, `'~'`,
    `'&'`, `'#'`, `'!'`, `'[]'`, `'()'`, `'Label'`,
    `*(':' Brackets)`, `*(':' sf Brackets)`).  The wholesale rewrite
    to `STMT`/`E_VAR`/`E_QLIT`/`E_FNC`/`E_SEQ`/`E_ALT`/role-slot tags
    is **the centerpiece of PARSER-SN-7-1..7-7**, not a separate
    style step.

##### Mechanical fixes

- [ ] Drop the lone blank line at the boundary between `Command`
      and `Compiland` (currently around line 177 of
      `parser_snobol4.sc`).  Replace with a `/*---*/` minor divider or
      simply tighten — the `/*===*/` major divider above already
      separates the section.  § 8.
- [ ] Rewrite the input-reader loop to drop the single-statement
      braces:
      ```snocone
      while ((Line = INPUT)) Src = Src Line nl ;
      ```
      Currently:
      ```snocone
      while ((Line = INPUT)) {
          Src = Src Line nl;
      }
      ```
      The two-statement TDump loop below keeps its braces — that one
      is correct as-is.  § 8.

##### Optional polish — `$' '`/`$'  '` and `S`/`F` simple-letter tokens

- [ ] Decide whether to introduce the beauty.sno simple-identifier
      whitespace tokens (`$' ' = SPAN(' ' tab) | epsilon;` and
      `$'  ' = SPAN(' ' tab);`) and the goto-letter token rules
      (`S = $' ' 'S';` `F = $' ' 'F';`).  Today the parser uses
      `'S' | 's'` and `'F' | 'f'` literals inline at lines 134–135 —
      mechanically equivalent, but doesn't match the beauty.sno
      reading.  Bringing them in would also let `Goto`'s `*Gray`
      references collapse to bare `$' '` reads.  § 3 + § 2.
      Decision: keep parser concise (status quo) OR refactor for
      beauty.sno isomorphism.

##### Guideline-vs-pragma tension — `White`/`Gray` referenced in main grammar

- [ ] § 2 says "`White`/`Gray` are attached, never referenced in the
      main grammar".  Today `parser_snobol4.sc` references them in
      five places, all inherited verbatim from beauty.sno:
      * `X4 = nInc() *Expr5 FENCE(*White *X4 | epsilon);` (line 76)
        — required, this is how concat-juxtaposition (`E_SEQ`) detects
        the inter-token whitespace that *is* the `..` operator.
      * `Goto = *Gray ':' *Gray FENCE(...);` (lines 139–140) — the
        bracket-token `$' '`/`$'  '` rules don't carry the `:`
        delimiter, so `*Gray` is required around it explicitly.
      * `Stmt = *Label ( *White *Expr14 ... ($'?' | *White) *Expr1
        ... )` (lines 149–168) — column-sensitive whitespace before
        the body expression (`*White`) and as the implicit pattern
        delimiter (`($'?' | *White)`); both required by SNOBOL4's
        column-aware grammar.
      The guideline expresses an *intent* — keep whitespace out of
      sight when the grammar permits.  beauty.sno's own grammar
      cannot honor it in these five places because SNOBOL4
      column-sensitive parsing requires explicit `*White` reads at
      Stmt boundaries.  Decision: leave the five sites annotated
      with a one-line `// ws-here-is-required:<reason>` comment and
      mark the guideline as "honored except where grammar forbids".
      The author should not feel embarrassed about these references;
      they are correct.  § 2.

##### Audit-clean (no action — recorded for completeness)

- § 1 names match — pattern names `Id`, `Integer`, `Real`, `String`,
  `Expr0..Expr17`, `ExprList`, `XList`, `Label`, `Stmt`, `Comment`,
  `Control`, `Command`, `Compiland`, `Goto`, `Target`, `SGoto`,
  `FGoto`, `SorF` all match beauty.sno verbatim.  ✅
- § 3 `$'name'` form — all 24 special-char tokens carry the
  `$'...'` form (`$'='`, `$'?'`, `$'|'`, `$'+'`, ...).  ✅
- § 4 shift/reduce — every action site uses `~` (shift) and `&`
  (reduce) infix per beauty.sno.  ✅
- § 5 n-ary counters — `nPush()` / `nInc()` / `nTop()` / `nPop()`
  used as patterns inside grammar rules at every n-ary site
  (`ExprList`, `Expr3`, `Expr4`, `Expr15`, `Compiland`).  ✅
- § 7 identifier conventions — no `_`-prefixed identifiers; variables
  lowercase (`tx`, `sf`, `Brackets`, `Src`, `Line`, `ptree`, `i`,
  `nk`); pattern names PascalCase.  ✅
- § 8 layout — 120-col max respected (longest line is the divider
  comment at exactly 120); single-statement-no-braces honored
  outside the two cases above.  ✅ (with the two mechanical fixes)
- § 9 read beauty.sno — process guideline, honored.  ✅

**Gate:** the two mechanical-fix checkboxes flip to `[x]`; the two
decision-points are resolved (decided either way is fine — the goal
is for the file to either honor the guideline or carry a one-line
comment explaining why it cannot).  PASS count unchanged from
PARSER-SN-7-8 (style work does not change tree shapes).

### PARSER-SN-FW-4 — `scrip --parser-crosscheck` C-side flag (deferred)

- [ ] Add `--parser-crosscheck` flag to `scrip.c`. Reads two inputs:
      a `.sc` PARSER driver and a per-language source. Runs both
      frontends in-process; uses C-callable `tree_equal(CODE_t* a, CODE_t* b)`
      for structural compare; exposes Snocone `cross_emit_tree(t)` builtin
      to bridge Snocone's `struct tree { t, v, n, c }` to C-side IR.
- **Blocks:** PARSER-RK (whitespace-tolerant dump form). Others can use byte-diff.
- **Gate:** matching trees emit `OK`; PARSER-SN gate refactored to use it.

### PARSER-SN-FW-5 — root-cause TLump function-name slot wart (defensive)

- [ ] Reduce to a 4-line `.sc` repro: a function `f(x)` whose body ends
      with `f = literal f(child); return;` — does the recursive call clobber
      the parent frame's `f` slot? Bisect against the working line-63
      bracket form. Probable site: `interp_eval.c E_FNC` or `eval_code.c`
      E_ASSIGN/E_FNC interaction.
- [ ] On fix, revert the `sub`-local staging in `tdump.sc` and restore
      the canonical `TLump = TLump TLump(...)` shape.
- **Gate:** canonical shape works without staging; PARSER-SN gate stays green.

---

## Known scrip-Snocone runtime workarounds

These are real runtime bugs we route around. All six PARSER-* sessions
inherit the workarounds.

### FW-3 — ARBNO(...) deferred-call firing under Snocone — ✅ FIXED 2026-05-03

**Resolved at one4all@228bc06b.**  `interp_eval_pat E_FNC` now restores
the ARBNO/FENCE guards that had been removed in RS-5 (with the comment
"no frontend produces those").  Snocone's parser HAS no ARBNO/FENCE
keywords, so `ARBNO(p)` reaches `interp_eval_pat` as `E_FNC("ARBNO",
child)` — exactly what the removed guards were catching.  Without the
guards, `eval_node(e)` evaluated the inner pattern in value context,
freezing `E_DEFER(E_FNC)` children as DT_E literals and `pat_arbno`
iterated over a baked pattern with no live deferred refs.

The fix mirrors the existing pair in `interp_eval` (`interp_eval.c`
~line 2951).  Sibling fix to `one4all@d5623f26` (eval_expr →
interp_eval_pat).  Same class of Snocone-vs-SNOBOL4 context-evaluation
difference.

After fix: deferred calls fire correctly inside `ARBNO(...)` whether
inlined or referenced via `*Q`.  PARSER-SN parser now produces non-empty
tree output for all 59 fixtures (up from 0).  Remaining FAILs are tree-
shape mismatches (beauty.sno native shape vs `--dump-parse` shape) —
the next rung's work, not a runtime bug.

Historical note (the old FW-3 workaround text — preserved for context):

> Investigated session 2026-05-03: deferred calls written INLINE inside
> ARBNO or FENCE bodies do not fire. Assigned to a NAMED pattern first,
> they fire correctly — including inside ARBNO(*Q) and FENCE. The
> diagnosis was incomplete: the real issue was that interp_eval_pat
> E_FNC fell through to eval_node, dropping pattern context for both
> inline and *Q forms. The 'named pattern' workaround happened to route
> through E_VAR resolution that re-entered pattern context, masking the
> bug for non-pattern children.

8-line repro that flipped from broken to fixed:

```snocone
function fire(d) { OUTPUT = '  fire()'; fire = .dummy; nreturn; }
'aa' ? ARBNO(ANY('a') epsilon . *fire());
// Before: zero output.  After: 'fire()' twice.
```

### INFRA-11a — `subj ? pat` value context — ✅ FIXED 2026-05-03

**Resolved at one4all@d2547945, corpus@c8ee2a6.**  SNOBOL4 spec says
`subj ? pat` in expression context returns the matched substring on
success, NULSTR on failure.  scrip returned NULSTR on success in BOTH
runtime paths (--ir-run via `interp_eval`, default --sm-run via
`SM_PUSH_NULL_NOFLIP`).

Three coordinated edits in one4all:

  - `stmt_exec.c`: added globals `g_last_match_subj` /
    `g_last_match_start` / `g_last_match_end`.  Populated at Phase4
    entry on every successful `exec_stmt`.  These let downstream code
    recover the matched span without changing `exec_stmt`'s signature
    (3 callers).

  - `interp_eval.c` E_SCAN value-context branch: after `exec_stmt`
    returns ok=1, read the globals and return `BSTRVAL(span_buf,
    span_len)` instead of `NULVCL`.  Uses `GC_malloc` so the buffer
    outlives the call frame.  span_len==0 returns `NULVCL` (correct
    empty-match behavior).

  - `sm_prog.h`/`sm_prog.c`/`sm_interp.c`/`sm_codegen.c`/`sm_lower.c`:
    new SM opcode `SM_PUSH_LAST_MATCH`.  `sm_lower.c` E_SCAN now emits
    `SM_EXEC_STMT` followed by `SM_PUSH_LAST_MATCH` instead of
    `SM_PUSH_NULL_NOFLIP`.  Both `sm_interp` (default `--sm-run`) and
    `sm_codegen` (`--jit-run`) gained handlers that mirror
    `interp_eval`'s logic.  Fail path pushes `NULVCL` — preserves the
    SCAN-fail-as-NULSTR convention used inside boolean tests like
    `~(s ? p)` and `if (s ? p) {...}`.

corpus side:

  - `programs/scrip/smoke.sc`: the `icase` smoke test was relying on
    the old NULSTR return value to make its concat with `'icase-OK'`
    come through unchanged.  Rewritten to use the proper success-check
    idiom: `IDENT('eNd' ? _smoke_icp, 'eNd') 'icase-OK'`.  Per the
    goal-file note "On fix, revert smoke workarounds".

Verification: all three paths now byte-identical to SPITBOL oracle.

```snocone
r  = ('hi' ? 'hi');             // r=[hi]    sz=2
r2 = ('hello world' ? 'hello'); // r2=[hello] sz=5
```

Sibling fix to `one4all@d5623f26` (eval_expr) and `one4all@228bc06b`
(eval_pat E_FNC ARBNO/FENCE).  Same family of Snocone-vs-SNOBOL4
context-evaluation differences exposed by the PARSER-* sessions.

### INFRA-11b — OPSYN infix-grammar integration — ⚠ NEEDS REINVESTIGATION

The original diagnosis claimed `OPSYN('~', 'shift', 2)` doesn't work
because `~` binds as unary at parse time before runtime OPSYN takes
effect.  Quick probe at session 2026-05-03 PM **after** INFRA-11a/11c
landed shows `'foo' ~ 'Word'` DOES dispatch to `shift` correctly via
both inline and named-pattern forms.  The "INFRA-11b is broken"
observation may have been a downstream symptom of INFRA-11a/11c —
when SCAN returned NULSTR and `_qtag` lost the tag string, the
*result* of OPSYN dispatch looked wrong even though the dispatch
itself worked.

8-line probe (run after INFRA-11a/11c fixes — all three forms fire shift):

```snocone
function shift(p, t) { OUTPUT='shift t='t; shift=p; return; }
OPSYN('~', 'shift', 2);
'foo' ? ('foo' ~ 'Word');               // OK — dispatches to shift
'foo' ? shift('foo', 'Word2');          // OK — direct
'foo' ? APPLY('~', 'foo', 'Word3');     // OK — APPLY route
```

- [ ] Re-probe after INFRA-11a/11c: confirm whether INFRA-11b is real
      and, if so, characterize the actual failure mode (the original
      diagnosis is now suspect).  If it's truly working, retire this
      entry — the PARSER-* sessions could move from `shift(p, t)` /
      `reduce(t, n)` direct calls back to `~` / `&` infix per
      beauty.sno's verbatim grammar.
- [ ] Even if `~` works, `runtime/x86/snobol4_pattern.c::opsyn` ignores
      the `type` arg (`(void)type;`).  Document or honour.

### INFRA-11c — quoting wart in `reduce(t, n)` / `shift(p, t)` callers — ✅ FIXED 2026-05-03

**Resolved at corpus@c8ee2a6.**  `semantic.sc::reduce(t, n)` interpolated
`t` into an EVAL string without re-quoting, so callers had to pre-quote:
`reduce("'P'", 1)` worked, `reduce('P', 1)` resolved `P` as a NULSTR
variable inside EVAL.  Same wart in `shift`'s tag arg.

Fix (corpus): new `_qtag(t)` helper in `semantic.sc` detects pre-quoted
forms (first char `'` or `"`) and passes through; bare strings get
wrapped via `SQize` (qize.sc), which produces a complete quoted literal.
Both call patterns now work uniformly:

```snocone
shift(p, 'tag')      // bare       — works
shift(p, "'tag'")    // pre-quoted — works
reduce('P', 1)       // bare       — works
reduce("'P'", 1)     // pre-quoted — works
```

---

## Invariants

- PARSER-SN never edits existing-frontend code to make trees match. If
  trees diverge, report the divergence; only after Lon decides which
  side is wrong does anyone touch either frontend.
- Test programs in `corpus/programs/snobol4/parser/` are owned by
  PARSER-SN. Crosschecks against existing programs in
  `corpus/programs/snobol4/` treat those as read-only fixtures.
- `.ref` files are captured from the existing frontend at the moment
  the rung lands and are checked in. They are NOT re-captured on later
  rungs without an explicit decision.
- `corpus` and `.github` stay on `main`; only `one4all` uses the
  `parser` branch.

---

## Watermark

**INFRA + FW + SN-0..SN-6 LANDED. Gate PASS=58, FAIL=0**
(SN-6 landed session 2026-05-03 morning, 2026-04-28 evening AOE.)

**⚠ PARSER-SN-7 PIVOTED, session 2026-05-03 PM.**  Diagnostic
crosscheck of the existing `parser_snobol4.sc` against `beauty.sno`
revealed ~1084 oracle stmts vs ~502 parser stmts.  Root cause is
not a finite list of grammar gaps — the parser is the wrong shape.

SN-7-0 partial-landed session 2026-05-03 PM (corpus@8083c20):
`parser_snobol4_v2.sc` scaffold (239 lines) on the parser_prolog.sc
/ parser_icon.sc / beauty.sno model.  All 5 invariants honored.
Living alongside the wrong-shape `parser_snobol4.sc` (876 lines)
until SN-7-1..7 reach PASS=58 parity.  MVP scope:
atom STMTs, label-only line, labeled+atom-body line, END marker.
MVP gate state: PASS=4 FAIL=1 on 5 targeted fixtures (atom_id,
atom_int, atom_str, cf_label_only PASS; cf_label_bare FAIL because
its `x = 1` body needs assign — lands in SN-7-1).

**Two architectural lessons surfaced during SN-7-0**, captured
in commit message at corpus@8083c20 and reproduced here so future
sessions opening to this watermark see them immediately:

  LESSON 1 — `nInc()` / `nPush()` / `nPop()` / `nTop()` are
  PATTERN-PRODUCING FUNCTIONS, not side-effect functions.  They
  return patterns that fire IncCounter() / PushCounter() / etc.
  at MATCH time.  Embed them as patterns inside grammar rules
  (`ARBNO( nInc() ws_opt clause ws_opt ... )`); inside escape-helper
  functions, call the BARE runtime: `IncCounter()`, `Push()`,
  `Pop()`.  The first draft of `parser_snobol4_v2.sc` made the
  textbook error of writing `Stmt . *nInc()`, which evaluates
  `nInc()` to a pattern and silently discards it — `IncCounter`
  never runs.

  LESSON 2 — `POS(0)` matches only at ABSOLUTE position 0 of the
  subject, not at start-of-line.  Once the cursor advances past
  the first char of Src, `POS(0)` NEVER matches again.  EndMarker,
  Comment, Control therefore CANNOT use `POS(0)` to mean "column
  0 of this line".  The fix relies on linear cursor advance: each
  Stmt / Comment / Control consumes its own trailing `nl_one`, so
  the cursor lands exactly at start-of-next-line for the next
  Command iteration.

The right shape is set by beauty.sno itself: one `Compiland` PATTERN
matched once over the entire source, all `~`/`&` infix shift/reduce
(routed through `shift(p, t)` / `reduce(t, n)` per INFRA-11b),
n-ary trees built via `nPush/nInc/nTop/nPop`, `Comment | Control |
Stmt` as alternation children of `Command`, no Snocone goto, no
parsing-driver functions.  Sibling parsers (PARSER-IC, PARSER-PR,
PARSER-RK, PARSER-RB) all land this shape today.  PARSER-SN at 876
lines is the largest and the only outlier — by a wide margin.

PARSER-SN-7 is therefore re-scoped from "land beauty.sno gate on top
of existing parser" to "rewrite parser_snobol4.sc to canonical
shape, then land beauty.sno gate".  Eight narrow rungs: SN-7-0
scaffolding (PARTIAL-LANDED 2026-05-03), SN-7-1..7 grammar slices
each gated by a focused fixture, SN-7-8 beauty.sno crosscheck.
See "Active rung ladder" above for full ladder.

Session 2026-05-03 PM artifacts:
- `corpus/programs/snobol4/parser/cf_label_bare.sno` added — fixture
  for bare-label-only line (`START\n` form), pre-stage SN-7-1.
  Currently FAILs against existing parser, will PASS automatically
  once SN-7-0 lands the canonical Stmt pattern with
  `Label = BREAK(' ' tab nl ';') ~ 'Label'`.
- This GOAL file rewritten: PARSER-SN-7 expanded into 9 rungs.
- `parser_snobol4.sc` left UNTOUCHED on `parser` branch.  The
  rewrite work happens on a new `parser-sn-rewrite` branch off
  `parser` per SN-7-0.
- Sibling parsers untouched.  Gate state: SN PASS=58 FAIL=1 (the
  one FAIL is `cf_label_bare` — pre-staged for SN-7-1).

SN-6 history (preserved for reference): added function definition /
call to the parser. One change to `parser_snobol4.sc`:

- New `_call_args(fname)` helper parses `( args )` into an `E_FNC` tree
  with `v=fname` and one child per arg.  Empty arg list → 0-child tree.
  Supports up to 7 args via `Tree(...)` positional + overflow via
  `Append`.
- `Expr17`'s identifier branch now checks for an immediately adjacent
  `(` and dispatches to `_call_args` for generic calls, otherwise falls
  back to bare `E_VAR`.  Whitespace between `Id` and `(` is NOT a call
  — `F (X)` is concat, matching the oracle.
- The five pattern primitives (LEN/BREAK/SPAN/ANY/NOTANY) keep their
  distinct E_LEN/E_BREAK/E_SPAN/E_ANY/E_NOTANY type tags via the
  `_pat_prim_call` cascade, which runs before the generic-call path.
- DEFINE is intentionally treated as just another generic call —
  `--dump-parse` itself does not crack open the spec string at parse
  time, so `DEFINE('F(X)')` becomes `(E_FNC DEFINE (E_QLIT "F(X)"))`.

15 new test programs in `corpus/programs/snobol4/parser/fn_*.sno`
covering one/two/three-arg / zero-arg / nested calls, calls in stmt
position, calls in pattern, calls in arith, calls with string args,
and DEFINE in four forms (one-arg / multi-arg / with locals/labels /
no args / labeled line).

Sibling parser gates re-checked: `parser_snobol4.sc` is the only file
touched, no shared file changed; siblings unaffected (Icon 33/33,
Prolog 18/18, Raku 17/17, Rebus 25/25 — all green).

SN-5 history (preserved for reference): added pattern-matching to the
parser via three new tiers.  Pattern primitive recognizers (LEN/BREAK/
SPAN/ANY/NOTANY) added to `Expr17` via shared `_pat_prim_call(name, kind)`
helper.  New `Expr12` tier (capture: `.` / `$`) inserted between
`Expr11` (pow) and `Expr14` (unary), left-associative per the oracle.
New `Expr3` tier (alternation: `|`) inserted at top of ladder above
`Expr4` (concat), n-ary flat per the oracle.  `_parse_body_goto`
rewritten as expression-driven with `_split_subj_pat(lhs)` helper
encoding the subj/pat split rule.  `tdump.sc::TValue` E_QLIT branch
moved before the empty-value `"."` placeholder so `(E_QLIT "")` renders
correctly.

**Next milestone:** PARSER-SN-7-1 — labels + assignment

**Watermark (session 2026-05-03 SN-7-0 final):** corpus@afbc6be
PASS=3. $'op' whitespace operators added per beauty.sno.
Uppercase=build-time pattern-returner. lowercase=match-time nreturn.
OPEN: ARBNO(*Command) with Command=nInc() FENCE(...) gives n=0 in scrip.
Test shown to Lon for diagnosis. Next: resolve then SN-7-1 labels+assign.

**Watermark (session 2026-05-03 SN-7-0 scaffold):**
parser_snobol4.sc rewritten from scratch on canonical shape (corpus@d34b23c).
PASS=3 (atom_id, atom_int, atom_str). Shape invariants: ONE Compiland, shift/reduce
function calls, nPush/nInc/nTop/nPop as patterns, no goto, no parse functions.
Next: labels, assignment, full expression ladder. — scaffold
`parser_snobol4_v2.sc` on a `parser-sn-rewrite` branch, on the
parser_prolog.sc / parser_icon.sc / beauty.sno model, hit PASS=58
parity on existing fixtures, then move through SN-7-1..7 grammar
slices, finishing at SN-7-8 (beauty.sno full crosscheck).

**Watermark (session 2026-05-03 PM cont., one4all@228bc06b):**
ARBNO(...) deferred-call bug FIXED in `interp_eval_pat` E_FNC case.
This was the bug blocking PARSER-SN-7 since the eval_expr fix landed
at `d5623f26`.  Sibling fix — same Snocone-vs-SNOBOL4 pattern-context
class.  Snocone has no ARBNO/FENCE keywords, so `ARBNO(p)` is
`E_FNC("ARBNO", p)` — and the E_FNC pat-context guards had been
removed in RS-5 with the (Snocone-incorrect) comment "no frontend
produces those".

Restoring those guards mirrors `interp_eval`'s pair at
`interp_eval.c:2951` and resolves the documented FW-3 workaround
(now marked ✅ FIXED above).

Gate state: PARSER-SN now produces non-empty tree output for ALL 59
fixtures (was: empty for all 59).  PASS=0/59 because the parser
emits beauty.sno's native tree shape (`Stmt`/`Id`/`String`/`Call`/
`..`) instead of scrip `--dump-parse`'s shape (`STMT`/`E_VAR`/
`E_QLIT`/`E_FNC`/`E_SEQ`).  This is the IR-tag-rewriting work the
goal file already describes (FW-1, FW-2, role-slot wrappers).

Sibling parsers all green: IC=40/40, PR=48/48, RK=25/25, RB=38/38,
SC=13/13.  SNOBOL4 smoke 7/7, scrip(.sc) smoke all OK.

**Next milestone:** PARSER-SN-7-1 — labels + assignment, *and* tree-shape
rewrite to match scrip `--dump-parse` oracle.  The grammar matches
beauty.sno verbatim today; the parser_snobol4.sc needs role-slot
wrappers (`:lbl`, `:subj`, `:pat`, `:repl`) and IR-tag rewrites
(`Stmt`→`STMT`, `Id`→`E_VAR`, `String`→`E_QLIT`, `Integer`→`E_ILIT`,
`Call`→`E_FNC`, `..`→`E_SEQ`, `|`→`E_ALT`) before any fixture passes.
This is essentially the FW-2 multi-child role-slot wrapper convention
applied across the grammar.

**Watermark (session 2026-05-03 PM cont. #2, one4all@d2547945, corpus@c8ee2a6):**
INFRA-11a + INFRA-11c FIXED.  Both Snocone-runtime route-around bugs that
were blocking the PARSER-* family are cleared.  All six PARSER-* sessions
inherit the fix.

  - **INFRA-11a** — `subj ? pat` value context now returns matched
    substring per SNOBOL4 spec.  Three coordinated edits across
    interp_eval, sm_interp, sm_codegen, plus new SM opcode
    `SM_PUSH_LAST_MATCH` and supporting globals in stmt_exec.  Both
    `--ir-run` (Snocone) and default `--sm-run` (SNOBOL4) paths
    fixed.  smoke.sc icase test rewritten per the goal-file
    "revert smoke workarounds" note.

  - **INFRA-11c** — `_qtag(t)` helper in semantic.sc auto-quotes bare
    tag args.  Both `reduce('P', 1)` and `reduce("'P'", 1)` now work;
    same for `shift`.

  - **INFRA-11b** — REOPENED for re-investigation.  Quick probe after
    INFRA-11a/11c landed shows `~` infix DOES dispatch to OPSYN
    target.  Original diagnosis may have been a downstream symptom
    of 11a/11c.  If 11b is truly working, the PARSER-* sessions can
    drop the `shift(p,t)`/`reduce(t,n)` direct-call workaround and
    use `~`/`&` infix per beauty.sno's verbatim grammar.

Gate state unchanged at fix:
  - SNOBOL4 smoke 7/7, scrip(.sc) smoke all OK
  - PARSER-IC=40/40, PR=48/48, RK=25/25, RB=38/38, SC=13/13
  - PARSER-SN=0/59 (tree-shape mismatch — SN-7-1 grammar work)

**Next milestone (unchanged):** PARSER-SN-7-1 — labels + assignment +
tree-shape rewrite.  parser_snobol4.sc grammar matches today; emits
beauty.sno-native shape (`Stmt`/`Id`/`String`/`Call`/`..`) and needs
the FW-2 role-slot wrappers + IR-tag rewrites (`Stmt`→`STMT`,
`Id`→`E_VAR`, `String`→`E_QLIT`, `Integer`→`E_ILIT`, `Call`→`E_FNC`,
`..`→`E_SEQ`, `|`→`E_ALT`) to match scrip `--dump-parse` oracle.

**Open carry-over for future sessions:**
  - INFRA-11b re-investigation per probe above
  - PARSER-SC FENCE/`*deref` silent-fail bug (separate from INFRA-11b;
    documented in GOAL-PARSER-SNOCONE.md ~line 215, item 4 of the
    PARSER-SC-2 landed list).  Probable fix-site: eval_pat.c E_FENCE
    handling around how its inner is evaluated when first alt has a
    runtime deref.  Repro: `*Id FENCE('=' *Id | epsilon)` against
    `'x=y'` captures `[x]` instead of `[x=y]`; without FENCE same
    pattern captures `[x=y]`.

**Watermark (session 2026-05-04, doc-only):** Style Guidelines for
`parser_*.sc` promoted to canonical home in this goal file (§ Style
Guidelines for parser_*.sc — binding on all six PARSER-*).  Nine
sub-sections cover: (1) names match official language spec, (2)
`White`/`Gray` attached not referenced, (3) `$'name'` token form
including `$' '`/`$'  '` for optional/required whitespace and the
`S = $' ' 'S'` simple-identifier exception, (4) shift/reduce three
forms (`. tx . *Func` → function-call → `~`/`&` infix) with the
INFRA-11b function-call mandate, (5) n-ary counters with the LESSON 1
pattern-producing-function reminder, (6) `E_*` IR tags with role-slot
wrappers, (7) identifier conventions table + `_`-prefix prohibition,
(8) 120-col layout / single-statement-no-braces / `/*===*/` dividers /
horizontal packing / multi-line wrapping, (9) read beauty.sno and
beauty.sc end-to-end before authoring.  Sibling goal files
(`GOAL-PARSER-SNOCONE.md`, `GOAL-PARSER-PROLOG.md`,
`GOAL-PARSER-RAKU.md`, `GOAL-PARSER-ICON.md`,
`GOAL-PARSER-REBUS.md`) cross-reference this section as canonical.
No code changes; gates unchanged (PARSER-SN PASS=0 FAIL=59 — same as
session start, expected).

**Next milestone (unchanged):** PARSER-SN-7-1 — labels + assignment +
tree-shape rewrite.  parser_snobol4.sc grammar matches today; emits
beauty.sno-native shape (`Stmt`/`Id`/`String`/`Call`/`..`) and needs
the FW-2 role-slot wrappers + IR-tag rewrites (`Stmt`→`STMT`,
`Id`→`E_VAR`, `String`→`E_QLIT`, `Integer`→`E_ILIT`, `Call`→`E_FNC`,
`..`→`E_SEQ`, `|`→`E_ALT`) to match scrip `--dump-parse` oracle.
