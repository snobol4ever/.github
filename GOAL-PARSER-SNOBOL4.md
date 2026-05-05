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

**Philosophy — decorate the grammar, do not plumb actions through it.**
The grammar pattern itself carries the tree-building decorations:
`shift(p, t)` consumes a token and pushes a leaf, `reduce(t, n)` pops
N stacked children and pushes an N-ary node.  The grammar reads
top-to-bottom as the language plus tree-shape annotations, with no
parallel scaffold of helper globals or `$'do_X'` action wrappers.

Per beauty.sno / beauty.sc, the pre-OPSYN form is:

```
primitive . tx epsilon . *Func(literal, tx)
```

This collapses to the function-call form:

```
primitive . tx Func(literal, "tx")
```

Where `Func` is `shift` or `reduce`.  With the OPSYN'd infix shortcuts
(`semantic.sc`):

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

#### 4a. Anti-pattern — function-based action plumbing

**Prefer to avoid** building a parallel plumbing layer of helper globals
(`_foo_node`, `_lhs`, `_op_tag`, ...), per-action wrapper patterns
(`$'save_lhs'`, `$'op_ADD'`, `$'do_assign'`, `$'binop_add'`, ...), and
companion functions (`stash_assign_target`, `build_assign`,
`expr_binop`, ...) when `shift`/`reduce` plus a stack and a counter
would build the same tree.  beauty.sno does not do this and the family
is more legible when individual `parser_*.sc` files don't either.

The stack and the n-counter are the persistent state most rules need.
`shift(P, 'E_VAR')` pushes the leaf when `P` matches; one or more
nested rules `reduce('E_ASSIGN', 2)`, `reduce('E_ADD', 2)`,
`reduce('E_FNC', 'nTop()')` fold them into the IR tree — n-ary
collections via `nPush()` ... `ARBNO(... nInc() *Child)` ... `nPop()`.
Anything that reads naturally as "push this leaf" or "pop these N and
make this kind of node" belongs in the pattern.  Helper functions are
appropriate for genuinely non-stack semantics (e.g. matching a
classifier list via `match(Functions, TxInList)`, lower-time name
remaps such as `say` → `write`).

These are guidelines, not laws.  When a Snocone runtime quirk forces
a workaround — the empirical `ARBNO(*func())`-fires-only-once bug
discovered in PARSER-PR is the textbook case — restore the minimal
helper needed and document the reason inline.  Don't fight a runtime
bug for the sake of style purity; fix the bug or note it and move
on.  See `GOAL-PARSER-PROLOG.md ## PR-7` for one such audit and the
caveats noted there.

A long block of `_xxx`-prefixed globals or `$'do_xxx'` /
`$'save_xxx'` patterns in a `parser_*.sc` is usually a sign that
stack-and-counter primitives were not exercised — worth a refactor
pass before further rungs land on top, but not an emergency.

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

**Avoid identifiers that start with `_`.**  Underscore-prefix is
reserved for compiler-generated names (synthetic labels, anonymous
bindings, internal scaffolds).  User code in `parser_*.sc` should
not spell one — not as a variable, not as a global, not as a struct
field, not as a helper function — except where Snocone itself
introduces the underscore at the language layer.

Existing `parser_*.sc` files that carry `_foo`-prefixed globals
(`_expr_node`, `_main_node`, `_rk_*`, `_e4lhs`, ...) predate this
guideline.  They are work-to-do, not established style worth copying
into new code.  Refactor opportunistically when you're already in
the file for other reasons; don't open a dedicated rung just to
rename them unless §4a's bigger refactor would also land.

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
  if (DIFFER(t)) return ;       // YES — single-line guard
  ```
  Braces are only for multi-statement bodies.  This applies to every
  control-flow head: `if`, `else`, `while`, `for`, `function` with
  a one-line body.
- **Section dividers, never blank lines:**
  - Major sections: `//============================...===============` (120 chars, `//=` prefix)
  - Minor sections: `//----------------------------...---------------` (120 chars, `//-` prefix)
  - Blank lines as separators are forbidden.  Use a divider comment.
  - The actual canon is `parser_snobol4.sc` — its `//===` 120-char
    bars are the literal model.  beauty.sc uses 80-char bars, which
    is grandfathered in that file but not for new `parser_*.sc`.
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
| SN-6 | function definition / call (generic `Id LPAREN args RPAREN` → E_FNC) | **PASS=58** |
| SN-7-0a | style audit remediation (mechanical fixes + decisions) | PASS=0/59 (style work; no tree change) |
| SN-7-1 | labels + assignment + tree-shape rewrite (IR tags + role-slot wrappers + alt-eats-LHS + arith-lassoc + paren-strip + 1-arg-Call + goto-direction-in-tag) | **PASS=59/59** ✅ session 2026-05-04 cont. #5 |

---

## Active rung ladder

### ✅ PARSER-FAMILY-LOOP — six-parser cross-pollination — COMPLETE

**Status:** ACTIVE.  All six parsers at 100% gate as of session
2026-05-04 cont. #5 (corpus@09ecd59).  Loop opens from a uniformly-
green baseline:

| Parser   | Gate          |
|----------|---------------|
| snobol4  | PASS=59/59 ✅ |
| icon     | PASS=51/51 ✅ |
| prolog   | PASS=54/54 ✅ |
| raku     | PASS=32/32 ✅ |
| snocone  | PASS=21/21 ✅ |
| rebus    | PASS=38/38 ✅ |

**Loop directives (binding on every iteration):**

1. **Operator picks one targeted concept per iteration.**  Examples:
   "rename `_foo` globals to bare names" (style §7), "promote
   goto-direction-baking-into-tag" (cross-language pattern),
   "convert `$'do_X'` action wrappers to inline `shift`/`reduce`"
   (style §4a), "tighten n-ary handling in arg lists" (RB/IC/PR
   share this idiom), etc.  The concept is named in one phrase the
   operator can repeat.

2. **Make the concept appear identical in all six `parser_*.sc`
   files.**  The literal goal: a `diff` of the six files, restricted
   to the targeted region, should show identical (or near-identical
   modulo language-specific names) shape.  Cross-pollination is the
   point — the family becomes more legible when the same concept
   reads the same way everywhere.

3. **Run all six gates after each change.**  No parser may drop
   below 100% during a loop iteration.  If a change breaks a gate,
   either fix the breakage in the same iteration or revert the
   iteration entirely.  The 100% baseline is the contract.

4. **One commit per iteration.**  Commit message names the concept
   and lists the per-parser before/after gate counts (all 100% on
   both sides per rule 3, but verbose for the audit trail).

5. **Do parser_snobol4.sc first when the concept might affect it.**
   Per Lon's standing instruction: "I know you must spend some time
   getting parser_snobol4.sc running, so do it first" (session
   2026-05-04 cont. #5).  The SN parser is the most complex and the
   most informative oracle for catching latent bugs in the shared
   `tdump.sc`/`semantic.sc`/`ShiftReduce.sc` infrastructure.

6. **If a SCRIP executable bug is found mid-iteration**, add a step
   to the relevant `GOAL-*` file capturing the bug + fix, then
   land the fix BEFORE continuing the iteration.  Do not work
   around SCRIP bugs in the `.sc` files when a small C-side fix
   would let all six parsers (and any future parser) use the
   correct syntax/semantics.

7. **Update this rung's gate-state table** at the bottom of every
   iteration with the post-iteration gate counts.  Append a new
   row per iteration; do not overwrite history.

**Candidate first iterations** (operator picks; ordered roughly by
tractability):

  - **iter#9 — SNOBOL4 left-associative arith assumption: re-examine
    and possibly remove.**  Right now `parser_snobol4.sc` builds
    arithmetic right-recursively (because beauty.sno's `Expr6`/`Expr8`/
    `Expr9` etc. are `*Expr_n FENCE($'op' *Expr_n (... & 2) | epsilon)`
    — right recursion), and then `rw_expr` walks the result and rotates
    each right-recursive arith chain into left-associative form because
    the `--dump-parse` oracle emits left-associative trees.  This
    rotation is the **only reason `is_rotatable` and the rotation block
    exist in `rw_expr` after iter#7**.  Lon's question: is the
    "oracle wants left-associative" claim right?  If `(a + b) + c` and
    `a + (b + c)` evaluate to the same value (commutativity for `+`,
    `*`; not for `-`, `/`, `^`, `$`, `.`), and if SM-LOWER lowers the
    same regardless of associativity shape, then **right-associative IR
    is fine for `+` and `*`** and the rotation can be skipped.  For
    `-`/`/` (non-commutative), associativity matters semantically:
    `a - b - c` must mean `(a - b) - c`, not `a - (b - c)`.  But that
    semantic could be captured by changing the GRAMMAR to be left-
    recursive (iterative, à la Icon's `*Expr8 ARBNO(Expr7tail)` shape),
    not by post-parse rotation.  Steps:

    1. Read `parser_snobol4.sc` `is_rotatable` + the rotation block in
       `rw_expr` to confirm scope (today: 7 binary tags — `E_ADD E_SUB
       E_MUL E_DIV E_POW E_CAPT_IMMED_ASGN E_CAPT_COND_ASGN`).
    2. Pick a sample: `a - b - c`.  Does the oracle (`scrip --dump-parse`)
       emit `(E_SUB (E_SUB a b) c)` (left-assoc)?  Check the SN-3 fixture
       output to confirm.
    3. If left-assoc IS what the oracle emits, then the legitimate
       options are:
       (a) **Rewrite the grammar to be left-recursive** (Icon-style:
           `Expr_n = *Expr_{n+1} ARBNO(Expr_n_tail)` where the tail
           pattern fires the reduce after each match).  Then the
           parse-time tree is already left-assoc and rotation is
           unnecessary.
       (b) **Change the oracle** (the existing C frontend's
           `expr_dump` / lower path) to emit right-assoc — only
           justified if SM-LOWER does not actually care about the
           tree shape, OR if the change is one-time and pays off
           elsewhere.  Probably not the right call (the existing
           frontend is the "in-process oracle" PARSER-SN must agree
           with; touching it is a different goal).
       (c) **Keep the rotation** (status quo).
    4. The right answer is almost certainly **(a)**.  beauty.sno
       chose right-recursion because SNOBOL4 PATTERN can't trivially
       express left-recursion (the recursion would left-eat without
       progress).  But the iterative `ARBNO(tail)` idiom is fine —
       Icon, Raku, and Rebus already use it; PARSER-SN can too.
    5. Land the grammar rewrite for the seven tiers; remove
       `is_rotatable`; remove the rotation block in `rw_expr`.
       Verify the gate holds at PASS=59/59.

    The win: less code; the grammar reads as the language's actual
    associativity; `rw_expr` becomes pure structural rewrite (paren
    strip + ExprList unwrap + Call dispatch) with no associativity
    knowledge.

  - **iter#10 — FENCE sweep, second pass: low-level lexical and
    other `(P | epsilon)` sites.**  iter#8 fenced the high-level
    Expr-tier alternations.  Other places where backtracking is
    pre-known useless and a `FENCE(...)` would prevent thrashing:

    - **Lexical token classifiers** of the form
      `(first (rest | epsilon))` — once `first` matches, `rest`
      either matches or it doesn't, and the matcher should not
      backtrack into `epsilon` if `rest` half-matches and then
      fails downstream.  Audit candidates:
      * Snocone `Id`, `kw_tail`
      * Icon `id_pat`, `Comment`, etc.
      * Prolog `Atom`, `Var`, `Atom_first/Atom_rest` composition
      * Raku token classifiers (`Ident`, `vro`, `fro`, `snro`,
        `pro`, `fnro`, etc.)
      * Rebus `Id`
      * SNOBOL4's already-FENCE'd token classifiers (e.g. `Real`)
        as the model.
    - **Driver-level `nl_opt = (nl_one | epsilon)`** and similar.
    - **`semi_opt = (';' | epsilon)`** in Icon.
    - **Anywhere a grammar rule has `(P | epsilon)` and `P` does
      not start with whitespace-only`** — once any non-empty
      substring of `P` matches, you've committed; failure should
      propagate, not retry as epsilon.

    Verification: each FENCE addition either preserves the gate at
    100% (if the case truly was useless backtracking) or causes
    a regression (if there was a real failure-recovery path being
    relied on).  In the latter case, back out that specific FENCE
    and document why.

    Scope: all six parsers; sweep the same kind of site in each
    file to keep the iteration concept-identical per loop rule 2.

  - **§7 `_`-prefix prohibition sweep.**  Style guideline §7
    forbids `_foo` identifiers; existing parsers carry many
    (`_e4lhs`, `_main_node`, `_rk_*`, `_expr_node`).  Pure
    mechanical rename + verify gates stay green.  Lowest risk,
    highest cross-pollination payoff.
  - **§4a function-based action plumbing teardown.**  Replace
    `$'do_X'` action wrappers + per-action helper functions with
    inline `shift`/`reduce`.  Bigger diffs but produces the
    cleanest cross-parser shape.
  - **n-ary arg-list idiom unification.**  RB's `bare_call` /
    `X_params` / `X_fields`, IC's argument lists, PR's compound
    terms — all use the same `nPush() ... ARBNO(nInc() ...) reduce(TAG, nTop()) nPop()`
    pattern with minor variations.  Pick one canonical shape;
    bring all six to it.
  - **Goto-direction-in-tag pattern (SN-only today).**  Only
    relevant if other languages have analogous cross-statement-
    stale-global issues.  Probably not — `:S`/`:F` is SNOBOL4-
    specific syntax — but worth a survey.
  - **Driver-loop stdin slurp idiom.**  All six parsers have
    `while ((Line = INPUT)) Src = Src Line nl;` with minor
    variations (some keep braces, some don't; some use `=` some
    `:=`).  Trivial unification.

**Iteration log:** loop opened session 2026-05-04 cont. #6.

| #  | Concept | SN | IC | PR | RK | SC | RB | Commit | Notes |
|----|---------|----|----|----|----|----|----|----|----|
| 1  | White-encodes-comments + canonical `$' '`/`$'  '` everywhere | 59→59 | 51→51 | 54→54 | 32→32 | 21→21 | 38→38 | (this session) | All six rewritten to canonical form: `White` first (per-language continuation/comment rules), `Gray = White \| epsilon`, `$' ' = Gray`, `$'  ' = White`. All `*White`/`*Gray` references in grammar replaced by `$'  '`/`$' '`. Per-language `White` bodies: SNOBOL4 keeps `+`/`.` continuation + adds `;*` inline trailing-comment; Icon/Rebus/Raku fold `'#' BREAK(nl)`; Prolog folds `'%' BREAK(nl)` + `Block = '/*' ARBNO(BREAK('*') ANY('*')) '/'`; Snocone folds `'//' BREAK(nl)` + same `Block`. Snocone gained `empty_cmd = $' ' $';' $' ' nl_opt` + Command alternative for C-style `;;/* hello */;;` empty-stmt semantics (Lon directive). Dead code removed: parser_icon.sc `Comment` rule (duplicate of `Blank` after `#` moved into White); parser_raku.sc `# REM` pre-filter at input loop (now native via White); parser_prolog.sc `comment`/old `trivia` collapsed (`trivia = ARBNO(White \| nl)`). Smoke verified: SNOBOL4 `;;` `;*` work; Snocone `;;/* hello */;;` matches oracle; Icon/Rebus/Raku/Prolog `#`/`%`/`//` line comments handled. Smoke-tested SNOBOL4 7/7, scrip(.sc) all OK. |
| 2  | Aligned token blocks with `$' '`/`$'  '` whitespace surrogates | 59→59 | 51→51 | 54→54 | 32→32 | 21→21 | 38→38 | corpus@d41add5 | All operator and keyword token definitions: LHS and `=` column-aligned within each block; whitespace embedded as `$' '` (optional) or `$'  '` (required) — no raw `' '` strings in token bodies; outer parens removed from Icon and Raku definitions. Per-language whitespace direction: Icon keywords `$' '` before only; operators `$' '` both sides; Prolog `$'is'` uses `$'  '` both sides (required lexical separation); `$'.'` before only; Rebus stmt-start keywords `$' '` before + `$'  '` after; mid-expr keywords (`then`/`do`) `$'  '` both sides; `$'('` fixed from bare `'('` to `$' ' '(' $' '`. Snocone operators alignment-only; keywords remain `kw_tail`-guarded (identifier-boundary guard required). |
| 3  | Correct bracket/keyword whitespace per SNOBOL4 model | 59→59 | 51→51 | 54→54 | 32→32 | 21→21 | 38→38 | corpus@3e58061 | Open brackets: no left ws, `$' '` right. Close brackets: `$' '` left, no right. Keywords: `$' '` left only (next token's left-ws is effective suffix). Binary ops unchanged. Snocone `(`/`{` kept `$' '` both sides — whitespace-sensitive like SNOBOL4; `if`/`while`/`do` grammar requires left-ws on `(` to absorb space between keyword and paren. Rebus `$'end'` ws before only; `$'then'`/`$'do'` left-ws only. Fixed Icon typo `'+:='$' '` (missing space) that caused .sc parse failure. |
| 4  | ⚠ SUPERSEDED IN-SESSION → iter#5 — three-/four-letter prefix on every helper + pair-named pattern builders | 59→59 | 51→51 | 54→54 (no change) | 32→32 (no change) | 21→21 | 38→38 | (not committed) | Session 2026-05-04 cont. #7. Started landing `sno_*`/`SNO_*`, `sc_*`/`SC_*`, `reb_*`/`REB_*`, `icon_*`/`ICON_*`, `pl_*`/`PL_*`, `raku_*`/`RAKU_*` per pair-name convention from `parser_snocone.sc`'s `sc_save_cond`/`SC_save_cond` model. Four parsers landed locally (SN, SC, IC, RB) — gates green. **Mid-session pivot**: Lon decided the prefix should be one letter, not 3-4. Renames done so far need to roll forward to one-letter scheme; PR and RK never landed. Iter#4 is therefore aborted as a commit — superseded by iter#5 below before any `git push` happened. Local edits to `parser_{snobol4,icon,rebus}.sc` will be redone under the one-letter scheme in iter#5; `parser_snocone.sc` was untouched. |
| 5  | Pair-shape semantic instrumentation + bare names (NO language prefix) — every in-pattern semantic action uses lowercase worker + Capitalized companion, names differ by case only | 59→59 | 51→51 | 54→54 | 32→32 | 21→21 | 38→38 | (this session) | Session 2026-05-05. **Lon directive supersedes the one-letter-prefix iter#5 plan**: SCRIP will support multi-program/modules so each `parser_*.sc` is its own program with its own global dictionary — no namespace-collision defense needed in `.sc` files. Canonical pair-shape technique: every semantic-action embedded inside a pattern is a function pair where the lowercase worker does the side effect (`Push(tree(...))`, sets self to `.dummy`, `nreturn`s) and the Capitalized companion is either (Form 1) a pattern variable assigned to `epsilon . *worker()` for no-arg case, or (Form 2) a function returning `EVAL("epsilon . thx . *worker(...)")` for arg-passing case. Grammar references the Capitalized companion only — bare name (Form 1) or with parens (Form 2). All `sc_`/`SC_`/`rb_`/`RB_`/`ic_`/`Rk_`/`rk_` prefixes stripped. Surface tag-string constants in rebus (`RB_FUNC_DECL` etc.) stripped to `FUNC_DECL`. Wire-protocol `'rb_'` literal in `new_label` body STAYS (oracle emits `rb_N` labels). Rebus capture-slot `rbStrBody` → `strbody`; raku `*_done` companion names rewritten to action verbs (`var_done` → `Push_var`, `say_done` → `Finish_say`, `stash_for` → `Store_for_iter`, etc.). Prolog: 13 inline `epsilon . *Capitalized()` call sites converted to companion references; 9 no-arg companions use Form 1, 5 arg-taking companions (`Push_var`, `Push_atom_body`, `Push_neg_int`, `Reduce_compound`, `Snapshot_head`) use Form 2. Plain helpers not embedded in patterns (`assign_anon_slots`, `resolve_var`) lowercased without companions. SNOBOL4 unchanged — no in-pattern instrumentation (uses only `shift`/`reduce` from `semantic.sc`). **No SCRIP C-side bugs encountered.** All six gates 100% throughout. |
| 6  | Use `$'X'` token variables in productions (binary form canonical, `$' '` sprinkled at unary site) + full Snocone operator-token table | 59→59 | 51→51 | 54→54 | 32→32 | 21→21 | 38→38 | (this session) | Session 2026-05-05. Every place a grammar production used inline `$' ' 'X'` for a punctuation/operator that already had a `$'X'` token defined is now using the variable. **Rule for dual-use operators (`-`, `+`, `*`, etc.)**: the variable `$'X'` is the **binary** form (`$' ' 'X' $' '`); at **unary** sites the production uses literal `$' ' 'X'` (single leading `$' '` + raw `'X'`). Per-parser changes: **Icon** added `$'~'`, `$'!'`, `$'\\'` to operator block (only-unary in Icon — defined in binary shape for consistency though only used unary); replaced `$' ' '(' ... $' ' ')'` with `$'(' ... $')'` in `Call` and `Prochead`; in `Expr10` unary tower, `~`/`\\`/`!` use `$'X'` variables, dual-use `-`/`+`/`*`/`?` keep `$' ' 'X'` literal form. **SNOBOL4** added `$':'` token; replaced `$' ' ':' ... ':' $' '` with `$':'` in `Goto`. **Prolog** added leading `$' '` to unary minus (`'-' Int . p_negi` → `$' ' '-' Int . p_negi`). **Snocone** added 24 missing operator tokens (Step 3f from `GOAL-PARSER-SNOCONE.md`): `[ ] , : ^ ** ! $ . & @ # % ~ == != < > <= >= ==: !=: <: >: <=: >=: :: :!: += -= *= /= ^=` — full set per `snocone_parse.y` token enum (`T_2*` binary, comparisons, identity, augmented assign).  Snocone block reorganized with named subsections (bracketing, pri-0/1/3, arith binary, pattern-build, cursor/position, numeric comparison, lexical comparison, identity, augmented assign).  No production references the new snocone tokens yet — they will be wired in as SC-4..SC-6 land. **No SCRIP C-side bugs encountered.** |
| 7  | parser_snobol4.sc only — remove rw_tag rewrite layer; grammar emits canonical IR (E_*) tags directly | 59→59 | 51→51 | 54→54 | 32→32 | 21→21 | 38→38 | (this session) | Session 2026-05-05. **Lon directive: scope is parser_snobol4.sc only**, the layer that previously parsed beauty.sno-native tag names ("'+'", "'..'", "'\|'", "'Id'", "'String'", etc.) into the parse tree, then walked the tree with `rw_tag` mapping each native tag to its canonical IR tag (`E_ADD`, `E_SEQ`, `E_ALT`, `E_VAR`, `E_QLIT`, etc.) is now removed. Grammar emits the canonical IR tag directly via the OPSYN'd `&` reduce shorthand: `("'+'" & 2)` → `(E_ADD & 2)`, `("'\|'" & '...')` → `(E_ALT & '...')`, `("'..'" & '...')` → `(E_SEQ & '...')`, `*Id ~ 'Id'` → `*Id ~ E_VAR`, `*Integer ~ 'Integer'` → `*Integer ~ E_ILIT`, `*Real ~ 'Real'` → `*Real ~ E_RLIT`, `*ProtKwd ~ 'ProtKwd'` and `*UnprotKwd ~ 'UnprotKwd'` → `~ E_KEYWORD`, capture operators `'$'`/`'.'` binary → `E_CAPT_IMMED_ASGN`/`E_CAPT_COND_ASGN`, unary `'+'`/`'-'` → `E_PLS`/`E_MNS`. **String capture switched to inner-body capture + Push_qlit worker** (canonical pair-shape from iter#5): `DQ`/`SQ` patterns now BREAK-capture into `str_body`; grammar uses `*String Push_qlit` to push `(E_QLIT body)` with quotes already stripped — replaces the old `rw_expr` String quote-strip branch. IR-tag string constants added at the top of the file (`E_VAR`, `E_ILIT`, `E_QLIT`, `E_RLIT`, `E_KEYWORD`, `E_SEQ`, `E_ALT`, `E_ADD`, `E_SUB`, `E_MUL`, `E_DIV`, `E_POW`, `E_PLS`, `E_MNS`, `E_CAPT_IMMED_ASGN`, `E_CAPT_COND_ASGN`). `rw_tag` function deleted. `rw_expr` simplified: dropped tag-rename calls, dropped String quote-strip branch (now done at parse time). Left-rotation predicate `DIFFER(new_t, t)` replaced by explicit `is_rotatable(t)` test against the seven binary-arith / capt-asgn IR tags that beauty.sno builds right-recursively. `rw_call`, `pp_stmt` unchanged in shape. Tags that beauty.sno used and `rw_tag` left untouched (`'='`, `'?'`, `'@'`, `'#'`, `'%'`, `'~'`, `'&'`, `'!'`, `'/'`, `'\|'` unary, `'[]'`, `','`, `'()'`, `'Call'`, `'ExprList'`, `'Stmt'`, `'Comment'`, `'Control'`, `'Label'`) stay as literal-byte tags — they're either internal wrappers stripped before TDump or unary forms not exercised by the SN gate corpus. Net effect on parser_snobol4.sc: 27-line `rw_tag` dispatch table removed; replaced by 14-line `is_rotatable` + IR-tag constants block; grammar reads more directly with no rename-table indirection. **No SCRIP C-side bugs encountered.** Other five parsers untouched. |
| 8  | FENCE around all the right levels — prevent useless backtracking thrashing using SNOBOL4 Expr gauntlet as the model | 59→59 | 51→51 | 54→54 | 32→32 | 21→21 | 38→38 | (this session) | Session 2026-05-05. SNOBOL4's `Expr0..Expr14` tower already used the canonical `*Expr_n FENCE($'op' *Expr_n (... & 2) \| epsilon)` form (model parser); the other five parsers had bare `( ... \| epsilon )` alternations that allow backtracking across already-committed operator branches. Wrapping each tail in `FENCE(...)` makes the grammar fail fast on the unique committed branch — once `$'+'` matches, the matcher does not retry the `epsilon` arm if the right-hand expression fails to parse. Per-parser changes: **Snocone** Expr9, Expr6 (FENCE outer alt + inner second-iteration FENCE preserved); X4, X3, Expr1, Expr0 (FENCE bare alt). **Icon** Expr8, Expr7tail, Expr6tail, Expr4tail, X3, Expr1, Expr1a (FENCE all). **Prolog** args, args_tail, list, mul_expr, add_expr, is_expr, unify_expr (FENCE all). **Raku** Expr7tail, Expr6tail, Expr4tail (FENCE around the bare alternation). **Rebus** alt_expr ARBNO body, expr, match_or_expr, stmt, func_body_stmt, X_params, opt_params, X_fields, opt_fields (FENCE all). SNOBOL4 itself unchanged — was already canonical. **No SCRIP C-side bugs encountered.** All six gates 100% throughout. |
| 9  | ✅ LANDED — n-ary trees everywhere with children in source order; flatten arith/concat/alt chains in C frontends; runtime n-ary lowering; flatten/rotate split in parser_*.sc | 0→59 | 51→51 | 54→54 | 31→31 | 21→21 | 35→38 | one4all@4393ce1e + corpus@61d825d (SN regression fix) + corpus@408fbe0 (iter#10 supersedes Phase D) + corpus@09d7f80 (RB Phase D, sibling session) | Sessions 2026-05-06 + 2026-05-04 cont. **Phases A+B+C committed at one4all@4393ce1e** (despite EMERGENCY HANDOFF commit message saying "uncommitted" — that was the watermark text, the actual commit landed). Phase D: parser_snobol4.sc landed at corpus@6c504d5 with a regression — `is_flatten_op`/`is_rotate_op` used `is_xxx = 0; return;` for false branch; in Snocone `if (cond)` is signal-based (every value is truthy; only `freturn` takes the else branch); both predicates were always-true → flatten path constructed `Tree(t, '', 0)` discarding `v(x)` → all 59 SN fixtures emitted `(STMT :subj .)` → SN PASS=0/59. Fixed at **corpus@61d825d** by changing the false branch to `is_xxx = .dummy; freturn;`.  SN restored to 59/59. Phase D for RK and RB: superseded for SN by iter#10 (see row 10); RB closed by sibling session at corpus@09d7f80 (alt_expr n-ary fold, RB PASS=38/38); RK still pending (1 fail: arith_chain). **Phase E (FENCE sweep, second pass — SN PARTIAL LANDED at corpus@c6bb327):** parser_snobol4.sc had only iter#10's three new ARBNO tail rules unfenced (Expr8tail, Expr9tail, Expr11tail); each wrapped in FENCE() to commit on the operator match.  Audit of remaining bare `(P | epsilon)` sites in parser_snobol4.sc found marginal-value (Real exponent sign) and risky-to-touch (Gray = White | epsilon top-level whitespace token) — left alone.  **Phase E for the other five parsers** is out of scope for this goal; the cross-pollination loop iteration that formally lands Phase E across the family will sweep them. **Cleanup CR-1..CR-5** (Rebus RExpr → EXPR_t double layer): now lower priority — RB Phase D closed without it.  Standing question: do we still want to remove RExpr now that RB is green, or leave the cleanup for a dedicated future session? |
| 9.5 | parser_snobol4.sc regression fix — `is_flatten_op`/`is_rotate_op` use `freturn` for false branch | 0→59 | 51→51 | 54→54 | 31→31 | 36→36 | 35→35 | corpus@61d825d | Session 2026-05-04 cont. Both predicate functions used `is_xxx = 0; return;` for the false case.  In Snocone, `if (cond)` is signal-based — every value (including 0 and '') is truthy; only `freturn` takes the else branch.  Both predicates were always-true in their callers (`if (is_flatten_op(t))` always entered the then-branch), sending every leaf into the flatten path inside `rw_expr`.  The flatten path constructs `Tree(t, '', 0)` — empty value — discarding `v(x)`.  All 59 SN fixtures emitted `(STMT :subj .)` instead of `(STMT :subj (E_VAR x))` etc.  Fix: change false branch to `is_xxx = .dummy; freturn;` so `if (is_xxx(t))` correctly fails and the rewrite walk falls through to the structural default path.  Two-line change (each predicate); 4-line diff total.  **Not a SCRIP C-side bug** — this is a `.sc`-language semantics: SNOBOL4-style functions signal success/failure separately from value, and any value return is success.  `freturn` is the correct failure signal in if-context.  **Probe verification:** `if(0)`, `if('')`, `if(rzero())` (where rzero returns 0 via plain return) all enter the then-branch; only `if(rfail())` (where rfail uses `.dummy + freturn`) takes the else-branch. |
| 10 | parser_snobol4.sc only — arith Expr-tier grammar iterative left-recursive (no post-flatten); new shared `foldop()`/`FoldOp()` flatten-or-binary worker | 59→62 | 88→88 | 54→54 | 31→31 | 46→46 | 38→38 | corpus@408fbe0 | Session 2026-05-04 cont. Removes the post-parse flatten layer in `parser_snobol4.sc` by rewriting the four arith/exp Expr-tier rules (Expr6 +/-, Expr8 /, Expr9 *, Expr11 ^/!/**) from beauty.sno's right-recursive form `*Expr_n FENCE($'op' *Expr_n (TAG & 2) \| epsilon)` to iterative left-recursive form `Expr_n = *Expr_{n+1} ARBNO(Expr_n_tail)` with a new shared `foldop(t)` build-time pattern-builder paired with `FoldOp(t)` match-time worker.  **`FoldOp` semantics**: pop rhs, pop lhs; if `t(lhs) == t`, append rhs as another child of lhs (extends flat n-ary chain); otherwise build fresh binary `Tree(t, '', 2, lhs, rhs)`.  Mirrors C-frontend `expr_binary_flatten()` shape exactly.  Same-tag chains build flat n-ary at parse time (`(E_ADD a b c d)`); mixed-op chains build left-binary at the precedence-tier boundary (`(E_SUB (E_ADD a b) c)`).  E_POW: parser produces flat n-ary same-tag chains `(E_POW 2 3 2)`; runtime `LOWER_NARY_RFOLD` emits the right-associative fold semantically — tree shape and runtime semantics decoupled cleanly.  **Files changed:** `programs/scrip/ShiftReduce.sc` (+27 lines: `FoldOp(t, rhs, lhs)` worker), `programs/scrip/semantic.sc` (+10 lines: `foldop(t)` pattern-builder), `programs/scrip/parser_snobol4.sc` (-27 lines net: four Expr-tier rules rewritten; `is_flatten_op()` removed; flatten branch in `rw_expr` removed; rotate branch for `E_CAPT_*_ASGN` binary kept since runtime is still strictly binary for those).  Three new fixtures lock in iter#10 correctness: `arith_mixed_addsub.sno` (`y = 1 + 2 - 3` — same-tier mixed-op latent bug), `arith_pow_chain.sno` (`y = 2 ** 3 ** 2` — POW flat n-ary right-fold), `arith_chain_long.sno` (`y = 1 - 2 + 3 - 4 + 5` — 5-element mixed chain).  **Latent bug fixed**: `1 + 2 - 3` was producing `(E_ADD 1 (E_SUB 2 3))` under the post-flatten approach; oracle emits `(E_SUB (E_ADD 1 2) 3)`.  No existing fixture exercised this case before iter#10.  **Cross-pollination opportunity flagged**: parser_icon.sc, parser_prolog.sc, parser_raku.sc, parser_snocone.sc all share the same latent same-tier-mixed-op bug today (verified manually: `1+2+3` against parser_icon emits `(E_ADD (E_ADD 1 2) 3)` while oracle emits `(E_ADD 1 2 3)`); their gate corpora don't exercise it.  When the loop opens iter#11+ for those parsers, `foldop()`/`FoldOp()` are now in the shared infra ready to use.  **No SCRIP C-side bugs encountered.** |

#### Open question — Snocone `for` statement (raised session 2026-05-06, unverified)

Lon raised: "Did Snocone somehow lose the `for` statement?"  This session
did not investigate.  iter#9 Phase A's only Snocone change is in
`snocone_parse.y` lines ~1021-1045 (the `expr6`/`expr9`/`expr11` arith
productions wired through `expr_binary_flatten` / `expr_binary_flatten_right`)
— statement-level grammar was not touched, and `PARSER-SC` gate stayed at
21/21 throughout this session, so iter#9 is unlikely to be the cause.
The observation may predate iter#9 — possibly long-standing.

**Next session, when picking this up:** grep `frontend/snocone/snocone_parse.y`
for `for`, check `corpus/programs/snocone/` for any `for`-using fixture,
and try a minimal `for (i = 1; LE(i, 10); i = i + 1) { ... }` against
scrip directly (`--dump-parse` and `--ir-run`).  If `for` is genuinely
missing or broken, open a dedicated step under `GOAL-LANG-SNOCONE.md` or
`GOAL-PARSER-SNOCONE.md` (whichever fits), not under PARSER-SN.  Do not
let it block iter#9 finish or the Rebus RExpr cleanup.

#### Cleanup — Rebus RExpr → EXPR_t double layer (next session, BEFORE finishing iter#9)

**Lon directive (session 2026-05-06):** "Get rid of two layers regarding Rebus
RExpr AST versus EXPR_t.  Go direct."  Five frontends (SNOBOL4 .y, Snocone .y,
Raku .y, Icon recursive-descent, Prolog driver) build `EXPR_t` directly in
their reduce actions / parse functions.  Rebus is the lone outlier — its
bison reduce actions build `RExpr` (a separate AST type with its own
`REKind` enum, its own `rexpr_new`/`rbinop` allocators, and a `left`/`right`
binary-only structure), then a second pass in `rebus_lower.c` walks the
RExpr tree and produces `EXPR_t`.

There is no good reason for the indirection.  Two AST types, two enum sets,
two allocators, two visitor walks — all to produce the same final IR every
other frontend produces directly.  The RExpr layer doubles the code surface,
forces every flatten / rotate / canonicalization decision to happen twice
(or pick a layer, as iter#9 had to in `rebus_lower.c::RE_ADD`), and hides
the IR shape from the bison actions.  This is friction, not architecture.

**Steps:**

- [x] **Step CR-1 — Inventory the Rebus AST surface.**  List every `RExpr`
      / `RStmt` / `REKind` / `RSKind` use site.  Sources: `frontend/rebus/
      rebus.h` (struct + enum defs), `rebus.y` (every reduce action),
      `rebus.l` (likely RExpr-free but verify), `rebus_lower.c` (the
      walker), `rebus_emit.c` (Rebus-AST pretty-printer — keep or drop?
      decide in CR-2), and any other file that names RExpr.
      **DONE (session 2026-05-04 cont.#8):** RExpr/RStmt used in: `rebus.h`
      (struct + enum defs + allocators), `rebus.y` (all reduce actions build
      RExpr*/RStmt*/RDecl*), `rebus_lower.c` (walker: RProgram→CODE_t),
      `rebus_lower.h` (public API — this is the only API scrip calls),
      `rebus_emit.c` (pretty-printer), `rebus_print.c` (AST printer),
      `rebus_main.c` (standalone driver).  `rebus.l` is RExpr-free (confirmed).
      Nothing outside `src/frontend/rebus/` uses RExpr/RStmt directly.
      The scrip driver calls only `rebus_compile()` from `rebus_lower.h`.

- [x] **Step CR-2 — Decide rebus_emit.c fate.**  This file contains the
      `RE_ADD: emit_expr_atom(e->left,out); fprintf(out,"+");` style
      pretty-printer for Rebus syntax.  Three options: (a) port to walk
      `EXPR_t` directly (Snocone-style `expr_dump`), (b) delete entirely
      if no live caller, (c) keep as a debug-only path on EXPR_t.
      Decision drives CR-3 / CR-4 scope.
      **DECIDED (session 2026-05-04 cont.#8):** Option (b) — delete.
      `rebus_emit.c` and `rebus_print.c` have no live callers in the scrip
      build.  Their only caller is `rebus_main.c`, a standalone driver not
      in the scrip Makefile.  All three files (`rebus_emit.c`,
      `rebus_print.c`, `rebus_main.c`) and the standalone
      `src/frontend/rebus/Makefile` will be deleted in CR-4.
      The two compile lines for `rebus_emit.o` and `rebus_print.o` in the
      top-level `Makefile` (lines 106-107) will also be removed — they
      compile to dead-code objects that are linked into scrip but have no
      reachable callers from scrip's live path.

- [ ] **Step CR-3 — Rewrite reduce actions to build EXPR_t directly.**
      Every `rbinop(RE_ADD, $1, $3, yylineno)` becomes
      `expr_binary_flatten(E_ADD, $1, $3)` (mirroring Snocone's `.y`).
      Every `rexpr_new(RE_..., lineno)` becomes the appropriate `expr_new`
      / `expr_unary` / `expr_binary` / `make_fnc(...)` call.  Keep the
      lineno carried via `EXPR_t::lineno` (or wherever it lives — verify
      against current snobol4.y reduce actions).  Same shapes that
      `rebus_lower.c::lower_expr` produces today, just produced inline at
      reduce time instead of via a second walk.  Token-class shapes
      (`RE_ADDASSIGN` → `E_ASSIGN(lhs, E_ADD(clone(lhs), rhs))` per
      snocone_parse.y model) move into the .y action too.

- [ ] **Step CR-4 — Delete rebus_lower.c (or the parts CR-3 absorbs).**
      Whatever logic doesn't move into reduce actions stays — but the
      layer's purpose (RExpr → EXPR_t conversion) is gone.  Update
      `Makefile` if needed.  Delete `RExpr` / `RStmt` / `REKind` / `RSKind`
      from `rebus.h` once they have no live users.

- [ ] **Step CR-5 — Verify Rebus smoke + PARSER-RB gates still pass.**
      `bash scripts/test_smoke_rebus.sh` and
      `bash scripts/test_parser_rebus.sh`.  This cleanup is a refactor —
      no behavioral change expected, just fewer files / less indirection.

**This step lands BEFORE iter#9 finishes** — once the Rebus layer is gone,
the iter#9 Phase A change in `rebus_lower.c::RE_ADD` (currently using
`expr_binary_flatten`) moves naturally into `rebus.y`'s reduce action, and
the iter#9 Phase D parser_rebus.sc work proceeds with one less moving part.

### ⚠ SUPERSEDED — PARSER-FAMILY-LOOP iter#5 (one-letter prefix scheme)

**Status:** SUPERSEDED (session 2026-05-05).  Lon directed that SCRIP will
support multi-program execution / modules, so each `parser_*.sc` is its own
program with its own global dictionary.  No namespace-collision defense is
needed in the `.sc` files themselves.  The iteration that actually landed
under iter#5 is the **pair-shape + bare-name** unification (see iteration
log row 5 above) — every in-pattern semantic action uses a lowercase worker
+ Capitalized companion pair with no language prefix.

The one-letter prefix scheme below is preserved for historical context
and in case a future module-less SCRIP environment ever forces the
collision question back open.  Nothing here is binding.

**Concept (Lon directive, session 2026-05-04 cont. #7):** All six `parser_*.sc`
files plus `scrip.sc` will be loaded into one SCRIP process simultaneously when
SCRIP becomes self-hosting (Milestone 2).  SNOBOL4 and Snocone have a single
flat global symbol table — function names, top-level globals, and tag-name
constants all share one namespace.  Snocone's `function NAME(args, locals)`
lowers to a SPITBOL `DEFINE('NAME(args,locals)')` whose args/locals are
auto-saved/restored slots in the global table — the function NAME itself lives
in the global table.  Two parsers defining `function rw_tag` would collide;
two parsers defining a global `head_name` would collide.  No module / import /
export concept exists today, and we are not adding one.

**Resolution:** every parser-private identifier — function name, global
variable, tag-string constant, pattern-builder companion — gets a one-letter
prefix denoting the language subsystem:

| Letter | Worker prefix | Pattern-builder prefix | Language subsystem |
|--------|---------------|------------------------|--------------------|
| `S`    | `s_`          | `S_`                   | SNOBOL4            |
| `C`    | `c_`          | `C_`                   | Snocone            |
| `R`    | `r_`          | `R_`                   | Raku               |
| `I`    | `i_`          | `I_`                   | Icon               |
| `P`    | `p_`          | `P_`                   | Prolog             |
| `B`    | `b_`          | `B_`                   | Rebus              |
| `X`    | `x_`          | `X_`                   | SCRIP (scrip.sc)   |

Pair-name shape (canonical model: `parser_snocone.sc`):
```
function c_save_cond() { c_saved_cond = Pop(); c_save_cond = .dummy; nreturn; }
function C_save_cond() { C_save_cond = EVAL("epsilon . thx . *c_save_cond()"); return; }
```
Or simple pattern variable for no-param case:
```
function s_push_qlit() { Push(tree('E_QLIT', s_strbody)); s_push_qlit = .dummy; nreturn; }
function S_push_qlit() { S_push_qlit = epsilon . *s_push_qlit(); return; }
```
Grammar reads as language-token + Capitalized-letter verb:
```
atom = *String S_push_qlit() | shift(*Integer, E_ILIT) | ...
```

**Names should announce action.**  Lon's directive: avoid placeholder
suffixes like `_done`.  Use verbs (`push`, `pop`, `store`, `save`, `make`,
`build`, `finish`, `decompose`, `emit`, `lower`).

**Steps (binding):**

- [ ] **Step 0 — Verify Snocone uses only the global variable dictionary
      and not function-level slots** beyond SPITBOL's auto-save/restore
      mechanism.  Confirmed in this session via `snocone_parse.y` — the
      `function NAME(args) { body }` form lowers to `DEFINE('NAME(args,locals)')`
      where args+locals are auto-saved global slots, and the function name
      itself goes into the same global symbol table as variables.  No
      separate function-local namespace exists.  Two parsers defining the
      same function name would overwrite each other when loaded into one
      process.  Step 0 is "read this paragraph and confirm — no code work".

- [ ] **Step 1 — `parser_snobol4.sc`** to `s_*` workers, `S_*` pattern-builders.
      Existing local edits (worker names `sno_*`) need rolling back to one-letter
      `s_*`.  Since these are post-parse helpers (called from driver, not
      embedded in PATTERN), no `S_*` companions are needed; just `s_pp_stmt`,
      `s_rw_expr`, `s_rw_call`, `s_rw_tag`, `s_rw_goto_slot`.  Pattern-block
      verbatim from beauty.sno; do not touch it.

- [ ] **Step 2 — `parser_snocone.sc`** to `c_*` / `C_*`.  Existing helpers
      already prefixed `sc_*`/`SC_*` — bulk rename to `c_*`/`C_*`.  Globals
      `sc_lbl_n`, `sc_strbody`, `sc_saved_cond`, `sc_while_ltop`, `sc_while_lend`,
      `sc_do_lcont`, `sc_do_lend`, EVAL-string param values (`'sc_if_nthen'` etc.)
      all become `c_*`.  `r_nTop` → `c_n_top`.

- [ ] **Step 3 — `parser_rebus.sc`** to `b_*` / `B_*`.  Existing local edits
      (worker names `reb_*`, builder `REB_*`, surface tags `REB_*`) roll forward
      to `b_*`/`B_*`.  Surface tag string values: `'REB_FUNC_DECL'` → `'B_FUNC_DECL'`
      etc.  Wire-protocol label prefix `'rb_'` (in `reb_new_label` →
      `b_new_label`) **stays** `'rb_'` because the existing C oracle emits
      `rb_else_N`/`rb_end_N` — that string is a wire-protocol identity, not a
      private identifier, and renaming it would break the gate.  Document this
      exception inline.

- [ ] **Step 4 — `parser_icon.sc`** to `i_*` / `I_*`.  Existing local edits
      (worker names `icon_*`, builders `ICON_*`) roll forward to `i_*`/`I_*`.
      `icon_n_top` → `i_n_top`.

- [ ] **Step 5 — `parser_raku.sc`** to `r_*` / `R_*`.  Today: mixed-case
      `Rk_Push_Var`, `Rk_Push_Param`, `Rk_Push_Qlit`, `Rk_Say_Done`,
      `Rk_Stash_For`, `Rk_Finish_For`, `Rk_Finish_Sub`, `Rk_Finish_Call`,
      `Rk_Finish_Main`; pattern names `var_done`, `param_done`, `qlit_done`,
      `say_done`, `stash_for`, `for_done`, `sub_done`, `call_done`, `main_done`;
      capture-slot globals `rk_capvf`, `rk_capvr`, `rk_cappf`, `rk_cappr`,
      `rk_capstr`, `rk_capff`, `rk_capfr`, `rk_capsnf`, `rk_capsnr`, `rk_capfnf`,
      `rk_capfnr`; helper globals `rk_for_iter`, `rk_sub_list`; helper functions
      `rk_slink`.  All become `r_*` workers + `R_*` pattern-builders, named
      action-verbs not `*_done`.  Suggested final names: `R_push_var`,
      `R_push_param`, `R_push_qlit`, `R_finish_say`, `R_store_for_iter`,
      `R_finish_for`, `R_finish_sub`, `R_finish_call`, `R_finish_main`.
      Capture slots: `r_capvf`, `r_capvr`, `r_cappf`, ... (drop the `rk_` →
      `r_` swap).  Apply consistent `*_done` → action-verb rewrites.

- [ ] **Step 6 — `parser_prolog.sc`** to `p_*` / `P_*`.  Today: globals
      `var_table`, `var_next`, `head_name`, `head_arity`, `body_present`,
      capture slots `q_body`, `s_body`, `p_text`, `p_name`, `le_text`, `p_negi`,
      `h_text`; helpers `Reset_var_scope`, `Resolve_var`, `Push_var`,
      `Assign_anon_slots`, `Push_atom_body`, `Push_nil`, `Push_neg_int`,
      `Reduce_is`, `Reduce_list`, `Reduce_compound`, `Reduce_conj`,
      `Reduce_disj`, `Snapshot_head`, `Mark_body`, `Build_clause`,
      `Build_directive`.  All become `p_*` workers.  Inline-pattern call sites
      `epsilon . *Push_atom_body(q_body)` etc. wrap into named pattern-builders
      `P_push_atom_body(p_q_body)` (function returning EVAL'd pattern), then
      grammar reads `Qatom P_push_atom_body('p_q_body')`.  `q_body`/`s_body`/
      etc. capture slots become `p_q_body`/`p_s_body`/etc.

      ⚠ **Conflict alert:** `p_text` / `p_name` / `p_negi` already collide with
      the new `p_*` worker prefix shape — they're capture slots, not helpers,
      so they take the `p_` prefix anyway, but the bare-letter post-prefix
      names are now `p_p_text` (capture slot named "p_text" with the prefix).
      Resolution: rename capture slots to remove the legacy single-letter `p_`
      prefix from their suffix — `p_text` (head-clause) → `p_h_text` (already
      `h_text`); `p_name` → `p_a_name` (compound name); `p_negi` → `p_neg_int`.
      Pick whatever reads cleanest while staying within the `p_*` namespace.

- [ ] **Step 7 — `scrip.sc`** Snocone-hosted SCRIP runtime (when it lands).
      Same one-letter scheme: **`X` / `x_*` / `X_*` for SCRIP itself**
      (decided session 2026-05-04 cont. #7).  Mnemonic: X for executable /
      cross-cutting / the SCRIP target itself.  Letter is now reserved across
      all six parsers — no parser-private identifier may begin `x_` or `X_`.
      Not part of iter#5; flagged here so the next prefix-collision reasoning
      has the full picture.

- [ ] **Step 8 — Verify all six gates 100% after each per-parser landing.**
      Per loop rule 3: no parser may drop below 100% during a loop iteration.
      Gates: SN=59, IC=51, PR=54, RK=32, SC=21, RB=38.  Run after each step.

- [ ] **Step 9 — One commit for the whole iteration** per loop rule 4.
      Commit message names the concept ("PARSER-FAMILY-LOOP iter#5: one-letter
      language prefix on every parser-private identifier") and lists per-parser
      before/after gate counts.

- [ ] **Step 10 — Update this iteration log table** with iter#5 row;
      append, do not overwrite history.

**Open question for Step 7 (SCRIP itself):**  When `scrip.sc` lands as
co-equal seventh `.sc` file, what letter does it get?  `T` (target),
`X` (executable), or other?  Not blocking iter#5; record decision before
scrip.sc work begins.



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

#### PARSER-SN-7-0a — style audit remediation (guidelines, not laws) — **DO BEFORE SN-7-1**

**Why this is next.**  The style guidelines were promoted to canonical
home in `## Style Guidelines for parser_*.sc` (session 2026-05-04
commit 34c2aa8).  This rung captures the audit of `parser_snobol4.sc`
(200 lines) against those nine guidelines and lands the small fixes
**before** the grammar-slice rungs SN-7-1..7-7 begin churning the
file.  Ordering rationale: the file is small now; tag-rewrite work in
SN-7-1..7-7 is going to triple the diff surface; landing style fixes
upstream of that churn means the grammar-slice diffs stay clean and
reviewable.

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

- [x] Drop the lone blank line at the boundary between `Command`
      and `Compiland` (currently around line 177 of
      `parser_snobol4.sc`).  Replace with a `/*---*/` minor divider or
      simply tighten — the `/*===*/` major divider above already
      separates the section.  § 8.  **DONE session 2026-05-04**:
      replaced with a 120-char `//----` minor divider matching the
      `//====` major-divider style used elsewhere in the file.
- [x] Rewrite the input-reader loop to drop the single-statement
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
      is correct as-is.  § 8.  **DONE session 2026-05-04**: braces
      removed; TDump's two-statement loop kept as-is.

##### Optional polish — `$' '`/`$'  '` and `S`/`F` simple-letter tokens

- [x] Decide whether to introduce the beauty.sno simple-identifier
      whitespace tokens (`$' ' = SPAN(' ' tab) | epsilon;` and
      `$'  ' = SPAN(' ' tab);`) and the goto-letter token rules
      (`S = $' ' 'S';` `F = $' ' 'F';`).  Today the parser uses
      `'S' | 's'` and `'F' | 'f'` literals inline at lines 134–135 —
      mechanically equivalent, but doesn't match the beauty.sno
      reading.  Bringing them in would also let `Goto`'s `*Gray`
      references collapse to bare `$' '` reads.  § 3 + § 2.
      Decision: keep parser concise (status quo) OR refactor for
      beauty.sno isomorphism.  **DECIDED session 2026-05-04**: keep
      status quo (inline `'S'|'s'` / `'F'|'f'` literals).  Decision
      comment landed inline above `SGoto`: "conciseness over
      isomorphism."  Refactor to beauty.sno simple-identifier form
      remains available later if a sibling parser's audit finds the
      isomorphism worthwhile.

##### Guideline-vs-pragma tension — `White`/`Gray` referenced in main grammar

- [x] § 2 says "`White`/`Gray` are attached, never referenced in the
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
      they are correct.  § 2.  **DONE session 2026-05-04**: all five
      sites annotated inline with `// ws-here-is-required:<reason>`
      comments (X4 juxtaposition-concat; Goto's two `*Gray` reads
      around `':'`; Stmt's `*White` body-prefix and `*White` before
      `'='` replacement; Stmt's `($'?' | *White)` subj/pat
      delimiter).  Guideline §2 status: "honored except where
      grammar forbids" — recorded as canonical interpretation for
      the family.

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
comment explaining why it cannot).  PASS count unchanged (style work
does not change tree shapes).

#### PARSER-SN-7-1 — bare label-only line + assignment + tree-shape rewrite — ✅ LANDED 2026-05-04

- [x] Fixture `cf_label_bare.sno` added (session 2026-05-03 — open
      against existing parser, will pass automatically once SN-7-0
      lands the canonical Stmt pattern with `Label = BREAK(' ' tab nl ';') ~ 'Label'`).
- [x] Confirm PASS=59 after SN-7-0.  **DONE session 2026-05-04 cont. #5
      at corpus@85bdd30.  Gate: PASS=59 FAIL=0 — full corpus parity.**

Six targeted fixes landed in this rung (all in `parser_snobol4.sc`,
zero shared-file changes; sibling parsers untouched):

  1. **Goto direction in node tag.**  Replaced `SorF` + single
     reduce tag `("*(':' sf Brackets)" & 1)` (which produces an
     identical tag for both S and F gotos and required reading the
     stale `sf` global at pp_stmt time) with named `Sgo`/`Fgo`/`Ugo`
     helper patterns.  Each helper bakes the direction directly into
     the goto node tag via `reduce(E_goS, 1)`/`reduce(E_goF, 1)`/
     `reduce(E_goU, 1)`.  Three new globals at top of file:
     `E_goU = "':go'"`, `E_goS = "':goS'"`, `E_goF = "':goF'"`.
     `rw_goto_slot` simplified to `tree(t(g), v(c(g)[1]))` — no
     more cross-statement `sf` staleness (the bug behind the
     `cf_goto_sf` SIGSEGV-then-:goF-on-S-goto failures).

  2. **Optional second `:` between two gotos.**  beauty.sno's
     grammar didn't allow `:S(L1):F(L2)` (only `:S(L1)F(L2)`); the
     existing scrip frontend accepts both.  Added `(':' *Gray | epsilon)`
     between the two gotos in `Goto`'s SorF / FrS alternatives.

  3. **Unconditional goto tag.**  Oracle uses `:go` (not `:goU`)
     for unconditional gotos.  Now matches.

  4. **`rw_call` 1-arg / 0-arg branching.**  beauty.sno's
     `ExprList = nPush() *XList ("'ExprList'" & '*(GT(nTop(), 1) nTop())')`
     only fires the reduce when `nTop() > 1` (i.e. 2+ args).  With
     1 arg, `c(call)[2]` is the bare arg node, not an ExprList
     wrapper.  With 0 args, ExprList reduces with `nTop()=0`
     producing a 0-child ExprList.  `rw_call` now branches on
     `IDENT(t(args), 'ExprList')` to compute `na` correctly and
     iterate / append the right way.  This was the root cause of
     all `fn_call_*` and `pat_LEN/BREAK/SPAN/ANY/NOTANY` failures.

  5. **`rw_expr` left-rotation.**  beauty.sno builds `a + b + c`
     as `(a (b c))` (right-recursive); oracle wants `((a b) c)`
     (left-associative).  Added a left-rotation step: when a node
     is binary (n=2) and its right child has the same IR tag,
     iteratively flatten into a left chain.  Applies uniformly to
     `E_ADD`/`E_SUB`/`E_MUL`/`E_DIV`/`E_POW`/`E_SEQ`.

  6. **`rw_expr` paren strip.**  beauty.sno's `Target` and
     parenthesized expressions create a transparent `'()'` node
     wrapper; oracle drops it.  `rw_expr` now treats `t='()'` as
     an unwrap operator (return `rw_expr(c(x)[1])`).

Plus two `pp_stmt` fixes for STMT shape:

  7. **Alt-eats-LHS rule** — when `ppPatrn` is non-empty and parses
     to a top-level `E_ALT` (and was NOT paren-wrapped), fold
     `subj_ir` into the first arm of `E_ALT` to build
     `(E_ALT (E_SEQ subj 'a') 'b' 'c')` and emit only `:subj`
     (no `:pat`).  Paren-wrap defeats the fold per oracle:
     `S ('a' | 'b')` keeps the split as `:subj S :pat (E_ALT ...)`.
     Detection: `t(ppPatrn) ? '()'` distinguishes the two cases.

  8. **Empty replacement** — `S 'a' = ` (with `=` but no RHS) emits
     `:repl (E_QLIT "")` per oracle.  Previously dropped the empty
     repl entirely.

  9. **Unary `E_MNS` / `E_PLS`** — `rw_tag` now maps `'-'`/`'+'`
     with `n=1` to `E_MNS`/`E_PLS` (previously kept literal tags).

Net diff: `parser_snobol4.sc` 374 → 410 lines (+93/-38).  Verbatim
PATTERN block invariant relaxed in the `Goto` block only — the
deviation is minimal (named helper patterns + direction baked into
tag) and documented inline.  All other PATTERN-block lines unchanged
from beauty.sno.

Sibling gate state at land: IC=51/51, PR=54/54, RK=32/32, SC=21/21
(all green; untouched).  RB=18/38 (pre-existing situation,
unrelated to this rung — see Open carry-over).

#### PARSER-SN-7-2 — &KEYWORD recognition

- [x] Fixtures `kw_fullscan.sno`, `kw_maxlngth.sno`, `kw_ucase.sno`,
      `kw_lcase.sno` — assignment LHS, RHS, and pattern-arg uses of
      protected and unprotected keywords.
- [x] Per beauty.sno: `ProtKwd = '&' SPAN(&UCASE &LCASE) ~ 'ProtKwd'`,
      `UnprotKwd = '&' SPAN(&UCASE &LCASE) ~ 'UnprotKwd'`.  These
      become alternatives in `Expr14`.  Fix: `~ E_KEYWORD` was capturing
      the full `&NAME` text (including `&`) but oracle emits name-only.
      Rewrote both alternatives as `'&' shift(SPAN(&UCASE &LCASE), E_KEYWORD)`
      — consume `&` before capture, shift just the name.  ProtKwd and
      UnprotKwd produce identical trees so collapsed to one alternative.
- **Gate:** keywords emit `(E_KEYWORD <NAME>)` matching the oracle. ✅ PASS=66/66

#### PARSER-SN-7-3 — bracket index `x[i]`, `x[i, j]`

- [x] Fixtures `idx_simple.sno`, `idx_multi.sno`, `idx_nested.sno`,
      `idx_in_assign_lhs.sno`.
- [x] Add `Expr15` / `Expr16` per beauty.sno: `Expr15 = Expr17 FENCE( nPush() Expr16 ("'[]'" & 'nTop() + 1') nPop() | epsilon )`.
      Two fixes needed: (1) `"'[]'"` → `E_IDX` constant (add `E_IDX = "'E_IDX'"` to
      constants block); (2) `rw_expr` E_IDX case: flatten ExprList bracket-group
      children directly into E_IDX (oracle emits flat children; default walk
      produced E_SEQ wrapper via ExprList→E_SEQ path).
- **Gate:** `(E_IDX <obj> <i> ...)` matches the oracle. ✅ PASS=70/70

#### PARSER-SN-7-4 — `+` / `.` continuation lines

- [x] Fixtures `cont_plus.sno`, `cont_dot.sno`, `cont_chain.sno`.
- [x] Per beauty.sno's `White` definition: continuation is part of
      the whitespace token class, swallowed by `White` between every
      two adjacent grammar units.  Already implemented — `White` already
      contained `nl ('+' | '.') FENCE(SPAN(' ' tab) | epsilon)`. No
      parser_snobol4.sc changes needed; all three fixtures passed immediately.
- **Gate:** multi-line continued statements emit a single STMT. ✅ PASS=73/73

#### PARSER-SN-7-5 — comment & control lines

- [x] Fixture `mixed_comment_control.sno`.
- [x] Per beauty.sno: `Comment = '*' BREAK(nl)`, `Control = '-' BREAK(nl ';')`.
      Already implemented — `Command` alternative for `*Comment` fires without
      emitting a STMT; comments silently consumed. No parser_snobol4.sc changes.
- **Gate:** comment/control lines do not produce extra STMTs in dump. ✅ PASS=74/74

#### PARSER-SN-7-6 — `*Id` deferred-pattern reference

- [x] Fixtures `defer_simple.sno` (`P = *Q`), `defer_alt.sno` (`P = *Q | *R`),
      `defer_in_pat.sno` (`x ? *P`).
- [x] `Expr14`'s prefix-`*` branch: was `"'*'" & 1` — hardcoded tag `*` instead of
      `E_DEFER`. Added `E_DEFER = "'E_DEFER'"` constant; fixed `Expr14` to use it.
- **Gate:** `*Id` constructs emit `(E_DEFER (E_VAR Id))`. ✅ PASS=77/77

#### PARSER-SN-7-7 — `;` mid-line statement separator

- [x] Fixture `semi_separator.sno` (`x = 1 ;* comment` and `x = 1; y = 2`).
- [x] Per beauty.sno's `Command`: alternation tail is `(nl | ';')`.
      Already implemented. No parser_snobol4.sc changes needed.
- **Gate:** semi-separated statements emit two STMTs. ✅ PASS=78/78

#### PARSER-SN-7-7b — emit E_* tags directly from grammar; delete rw_tag and all beauty.sno-native tag strings — ✅ LANDED corpus@0390853

**Goal:** The grammar PATTERN block shifts and reduces using canonical IR tags
(`E_VAR`, `E_ILIT`, `E_QLIT`, `E_RLIT`, `E_FNC`, `E_SEQ`, `E_ALT`,
`E_ADD`, `E_SUB`, `E_MUL`, `E_DIV`, `E_POW`, `E_PLS`, `E_MNS`,
`E_CAPT_IMMED_ASGN`, `E_CAPT_COND_ASGN`, `E_KEYWORD`, `E_DEFER`,
`E_IDX`, `E_LEN`, `E_BREAK`, `E_SPAN`, `E_ANY`, `E_NOTANY`) directly.
No post-parse tag-rename walk.  `rw_tag` is deleted entirely.  `rw_expr`
becomes a pure structural rewrite (paren-strip, ExprList-unwrap,
E_IDX-flatten, E_CAPT_*-rotation, String-quote-strip) with no tag
knowledge.  `rw_call` dispatches on the already-canonical `fname` value
and constructs the right E_* node directly.

**What changes:**

- [x] **Step 1 — Grammar: replace beauty.sno-native shift/reduce tags with E_*.**
      Every `shift(P, 'Id')` → `shift(P, E_VAR)`.  Every `reduce(\"'..'\", N)` →
      `reduce(E_SEQ, N)`.  Full rename table (grammar sites only):
      | Old tag | New tag | Site |
      |---------|---------|------|
      | `'Id'`         | `E_VAR`              | `Expr17` Id shift |
      | `'Integer'`    | `E_ILIT`             | `Expr17` Integer shift |
      | `'String'`     | `E_QLIT`             | `Expr17` String shift (see Step 2) |
      | `'Real'`       | `E_RLIT`             | `Expr17` Real shift |
      | `'Call'`       | `E_FNC`              | `Expr17` Call reduce |
      | `'..'`         | `E_SEQ`              | `Expr4`/`X4` reduce |
      | `'|'`          | `E_ALT`              | `Expr3`/`X3` reduce |
      | `'$'` (binary) | `E_CAPT_IMMED_ASGN` | `Expr12` reduce |
      | `'.'` (binary) | `E_CAPT_COND_ASGN`  | `Expr12` reduce |
      | `'+'` (binary) | `E_ADD`              | already `foldop(E_ADD)` ✅ |
      | `'-'` (binary) | `E_SUB`              | already `foldop(E_SUB)` ✅ |
      | `'*'` (binary) | `E_MUL`              | already `foldop(E_MUL)` ✅ |
      | `'/'` (binary) | `E_DIV`              | already `foldop(E_DIV)` ✅ |
      | `'^'`/`'!'`/`'**'` | `E_POW`         | already `foldop(E_POW)` ✅ |
      | `'-'` (unary)  | `E_MNS`              | `Expr14` reduce |
      | `'+'` (unary)  | `E_PLS`              | `Expr14` reduce |
      | `'*'` (unary/defer) | `E_DEFER`       | already `reduce(E_DEFER, 1)` ✅ |
      | `'&'` keyword  | `E_KEYWORD`          | already `shift(..., E_KEYWORD)` ✅ |
      Add IR-tag string constants at top of file for every tag not already there:
      `E_VAR`, `E_ILIT`, `E_RLIT`, `E_FNC`, `E_SEQ`, `E_ALT`,
      `E_CAPT_IMMED_ASGN`, `E_CAPT_COND_ASGN`, `E_MNS`, `E_PLS`,
      `E_LEN`, `E_BREAK`, `E_SPAN`, `E_ANY`, `E_NOTANY`,
      `E_ADD`, `E_SUB`, `E_MUL`, `E_DIV`, `E_POW`.
      (E_KEYWORD, E_DEFER, E_IDX, E_Parse, E_goU/S/F already present.)

- [x] **Step 2 — String: capture inner text at parse time via Push_qlit worker.**
      `Expr17` String branch: instead of `*String ~ E_QLIT` (which shifts
      the full `'...'`/`"..."` including delimiters), capture the inner body
      with a `Push_qlit` pair-shape worker (canonical iter#5 pattern):
      ```
      function push_qlit() { Push(tree(E_QLIT, str_body)); push_qlit = .dummy; nreturn; }
      function Push_qlit() { Push_qlit = epsilon . *push_qlit(); return; }
      ```
      `SQ`/`DQ` patterns already BREAK-capture into a slot; re-use that
      capture slot as `str_body`.  Grammar: `*String Push_qlit()` replaces
      `*String ~ E_QLIT`.  Quotes are stripped at match time; `rw_expr`
      String-quote-strip branch is deleted.

- [x] **Step 3 — rw_tag: delete entirely.**  Once grammar emits E_* directly,
      the tag-rename dispatch table is dead.  Remove `function rw_tag(...)`.
      Remove all call sites in `rw_expr` (`new_t = rw_tag(t, n(x))`; the
      `DIFFER(new_t, t)` rotation guard; the `result = Tree(new_t, ...)` path).

- [x] **Step 4 — rw_expr: simplify to pure structural.**  After Step 3,
      `rw_expr` only needs:
      - `'()'` paren unwrap (unchanged)
      - `E_QLIT` String-quote-strip **deleted** (handled at parse time in Step 2)
      - `E_FNC` / Call dispatch → `rw_call` (tag is now `E_FNC` not `'Call'`)
      - `ExprList` transparent unwrap (unchanged)
      - `E_IDX` flatten (tag is already `E_IDX`) (unchanged)
      - `E_CAPT_*_ASGN` left-rotation (tags are now canonical) — check
        guard changes from `DIFFER(new_t, t)` to direct `IDENT(t, E_CAPT_IMMED_ASGN)` etc.
      Update `rw_call`: `IDENT(t(x), 'Call')` guard → `IDENT(t(x), E_FNC)`;
      `fname = v(c(x)[1])` stays; dispatch on `fname` for LEN/BREAK/SPAN/ANY/NOTANY
      stays; generic E_FNC path stays.  (rw_call shape barely changes.)

- [x] **Step 5 — Verify and run gate.**  `bash scripts/test_parser_snobol4.sh`
      must report PASS=78 FAIL=0.  No fixture output should change (tags
      were already correct in the oracle; grammar now produces them directly).

- [x] **Step 6 — Commit.**  One commit, `parser_snobol4.sc` only (shared
      infra files unchanged).  Message: `PARSER-SN-7-7b: grammar emits E_* tags
      directly; delete rw_tag (PASS=78/78)`.

- **Gate:** PASS=78 FAIL=0.

#### ⚠ PARSER-SN-7-7c — full keyword/function/builtin inventory + classifier patterns — **CURRENT STEP**

**Goal:** parser_snobol4.sc is missing the complete identifier-classification
machinery that beauty.sno carries. Add it so the grammar can distinguish
`Function`, `BuiltinVar`, `SpecialNm`, `ProtKwd`, `UnprotKwd` from plain `Id`
at parse time — matching beauty.sno's structure exactly.

**What beauty.sno has that we lack:**

Classifier string tables (word-list membership strings):
```
SpecialNms  =  'ABORT CONTINUE END FRETURN NRETURN RETURN SCONTINUE START'
BuiltinVars =  'ABORT ARB BAL FAIL FENCE INPUT OUTPUT REM TERMINAL'
ProtKwds    =  'ABORT ALPHABET ARB BAL FAIL FENCE FILE FNCLEVEL '
               'LASTFILE LASTLINE LASTNO LCASE LINE REM RTNTYPE '
               'STCOUNT STNO SUCCEED UCASE'
UnprotKwds  =  'ABEND ANCHOR CASE CODE COMPARE DUMP ERRLIMIT '
               'ERRTEXT ERRTYPE FTRACE INPUT MAXLNGTH OUTPUT '
               'PROFILE STLIMIT TRACE TRIM FULLSCAN'
Functions   =  'ANY APPLY ARBNO ARG ARRAY ATAN BACKSPACE BREAK BREAKX '
               'CHAR CHOP CLEAR CODE COLLECT CONVERT COPY COS DATA '
               'DATATYPE DATE DEFINE DETACH DIFFER DUMP DUPL EJECT '
               'ENDFILE EQ EVAL EXIT EXP FENCE FIELD GE GT HOST '
               'IDENT INPUT INTEGER ITEM LE LEN LEQ LGE LGT LLE '
               'LLT LN LNE LOAD LOCAL LPAD LT NE NOTANY OPSYN OUTPUT '
               'POS PROTOTYPE REMDR REPLACE REVERSE REWIND RPAD RPOS '
               'RSORT RTAB SET SETEXIT SIN SIZE SORT SPAN SQRT STOPTR '
               'SUBSTR TAB TABLE TAN TIME TRACE TRIM UNLOAD'
```

Membership test machinery:
```
TxInList  =  (POS(0) | ' ') *upr(tx) (' ' | RPOS(0))
```
(`match(List, TxInList)` from assign.sc tests whether `tx` (uppercased) appears
as a whole word in `List`.)

Classifier patterns in Expr17:
```
Function   =  SPAN('.' digits &UCASE '_' &LCASE) $ tx $ *match(Functions, TxInList)
BuiltinVar =  SPAN('.' digits &UCASE '_' &LCASE) $ tx $ *match(BuiltinVars, TxInList)
SpecialNm  =  SPAN('.' digits &UCASE '_' &LCASE) $ tx $ *match(SpecialNms, TxInList)
ProtKwd    =  '&' SPAN(&UCASE &LCASE) $ tx $ *match(ProtKwds, TxInList)
UnprotKwd  =  '&' SPAN(&UCASE &LCASE) $ tx $ *match(UnprotKwds, TxInList)
```

Expr17 call branch uses `*Function` not `*Id` for classified calls:
```
|  *Function ~ E_VAR $'(' *ExprList $')' (E_FNC & 2)
|  *Function ~ E_VAR
|  *BuiltinVar ~ E_VAR
|  *SpecialNm  ~ E_VAR
|  *Id ~ E_VAR   (plain unclassified identifier — fallback)
```

Expr14 keyword branches already work syntactically (`'&' shift(..., E_KEYWORD)`)
but do not validate membership. ProtKwd/UnprotKwd patterns can replace the
bare `SPAN` to add validation. Tree output is identical either way (both emit
`E_KEYWORD`) but the grammar becomes more faithful to beauty.sno.

**Steps:**

- [x] **Step 1 — Compile the definitive keyword/function inventory.**
      Consult (clone if needed):
      - `corpus/programs/snobol4/demo/beauty/beauty.sno` lines 60–92
      - `snobol4ever/x64` repo — check snobol4.h / keyword tables
      - `snobol4ever/x32` repo — check s.min / keyword tables
      - `snobol4ever/csnobol4` repo — check v311.sil / keyword tables
      Cross-reference all four. The union is the complete list. Note any
      discrepancies. beauty.sno's lists are the primary model; extend with
      any names found in the runtime repos that beauty.sno omits.

- [x] **Step 2 — Add classifier string tables to parser_snobol4.sc.**
      After the E_* constants block, add:
      ```
      SpecialNms  = '...';
      BuiltinVars = '...';
      ProtKwds    = '...';
      UnprotKwds  = '...';
      Functions   = '...';
      ```
      Use the complete verified list from Step 1. Multi-line strings use
      Snocone string concatenation.

- [x] **Step 3 — Add TxInList pattern and classifier patterns.**
      ```
      TxInList  =  (POS(0) | ' ') *upr(tx) (' ' | RPOS(0));
      Function  =  SPAN('.' digits &UCASE '_' &LCASE) $'$' tx $'$' *match(Functions, TxInList);
      BuiltinVar = SPAN('.' digits &UCASE '_' &LCASE) $'$' tx $'$' *match(BuiltinVars, TxInList);
      SpecialNm  = SPAN('.' digits &UCASE '_' &LCASE) $'$' tx $'$' *match(SpecialNms, TxInList);
      ProtKwd    = '&' SPAN(&UCASE &LCASE) $'$' tx $'$' *match(ProtKwds, TxInList);
      UnprotKwd  = '&' SPAN(&UCASE &LCASE) $'$' tx $'$' *match(UnprotKwds, TxInList);
      ```
      Note: beauty.sno uses `$ tx $` (immediate-assign capture into tx).
      In Snocone pattern syntax this is `$'$' tx $'$'` (using the token
      variables). Verify the exact Snocone form against parser_icon.sc or
      parser_prolog.sc which use similar capture patterns.

- [x] **Step 4 — Update Expr14 to use ProtKwd/UnprotKwd classifiers.**
      Replace the bare `'&' shift(SPAN(&UCASE &LCASE), E_KEYWORD)` with:
      ```
      |  *ProtKwd   shift(tx, E_KEYWORD)
      |  *UnprotKwd shift(tx, E_KEYWORD)
      ```
      Both emit `E_KEYWORD` with the name (without `&`) as value — same as
      before, but now validated against the membership lists.

- [x] **Step 5 — Update Expr17 to use classifier patterns.**
      Replace the current `*Id ~ E_VAR $'(' *ExprList $')' (E_FNC & 2)` /
      `*Id ~ E_VAR` alternatives with the full beauty.sno ordering:
      ```
      |  *Function  ~ E_VAR $'(' *ExprList $')' (E_FNC & 2)
      |  *Function  ~ E_VAR
      |  *BuiltinVar ~ E_VAR
      |  *SpecialNm  ~ E_VAR
      |  *Id         ~ E_VAR
      ```
      Order matters: Function tried first (has membership test), plain Id last.

- [x] **Step 6 — Verify gate PASS=78 FAIL=0.**
      `bash scripts/test_parser_snobol4.sh` — no fixture output should change
      (oracle tree shapes are unaffected by classifier membership; all these
      identifiers still emit `E_VAR` or `E_FNC` or `E_KEYWORD`).

- [x] **Step 7 — Commit.**
      `parser_snobol4.sc` only. Message:
      `PARSER-SN-7-7c: full keyword/function/builtin inventory + classifier patterns (PASS=78/78)`

- **Gate:** PASS=78 FAIL=0.

#### PARSER-SN-7-8 — beauty.sno full crosscheck

- [ ] `parser_snobol4_v2.sc` parses `beauty.sno` (627-line `corpus/programs/snobol4/demo/beauty/beauty.sno`).
- [ ] `tree_equal` against `--dump-parse`'s tree returns true (use
      whitespace-normalized byte-diff until PARSER-SN-FW-4 lands).
- [ ] Running the parser-built tree through `--ir-run` produces output
      byte-identical to the SPITBOL oracle (Milestone 1 gate).
- **Gate:** beauty.sno PASSES under both oracles.

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

**Next milestone:** PARSER-SN-7-0a — style audit remediation
(guidelines, not laws).  Two mechanical fixes (drop blank line, drop
single-stmt braces) + two decision points (`$' '`/`S`/`F` tokens;
`White`/`Gray` rationale comments).  PASS count unchanged; lands
upstream of SN-7-1..7-7 grammar churn so style fixes don't tangle
with tag-rewrite diffs.  After SN-7-0a: PARSER-SN-7-1 — labels +
assignment + tree-shape rewrite (FW-2 role-slot wrappers + IR-tag
rewrites `Stmt`→`STMT`, `Id`→`E_VAR`, `String`→`E_QLIT`,
`Integer`→`E_ILIT`, `Call`→`E_FNC`, `..`→`E_SEQ`, `|`→`E_ALT`) to
match scrip `--dump-parse` oracle.

**Watermark (session 2026-05-04 cont.):** SN-7-9 (the style-audit
remediation rung added earlier this session) renamed to **SN-7-0a**
and relocated from the ladder tail to its proper position **between
SN-7-0 and SN-7-1** — i.e. the immediate next-up rung.  Rationale:
file is small now (200 lines), tag-rewrite work in SN-7-1..7-7 will
triple the diff surface, landing style fixes upstream keeps the
grammar-slice diffs reviewable.  Step content unchanged from the
prior commit; only position and numbering changed.  PLAN.md
goals-table entry updated to point at SN-7-0a as the active step.

**Watermark (session 2026-05-04 cont. #2): PARSER-SN-7-0a LANDED.**
All four checkboxes flipped to `[x]`:
  - Mechanical fix 1: blank line between `Command` and `Compiland`
    replaced with a 120-char `//----` minor divider.
  - Mechanical fix 2: input-reader loop `while ((Line = INPUT))` had
    its single-statement braces removed; now reads
    `while ((Line = INPUT)) Src = Src Line nl ;`.  TDump's
    two-statement loop kept braced (correct as-is).
  - Decision point §3 (`$' '`/`S`/`F` tokens): **status quo kept**;
    inline `'S'|'s'` / `'F'|'f'` literals retained.  Decision recorded
    as inline comment above `SGoto`: "conciseness over isomorphism."
  - Decision point §2 (`White`/`Gray` in main grammar): **all five
    sites annotated** with `// ws-here-is-required:<reason>` inline
    comments — X4 juxtaposition-concat, two `*Gray` reads around `':'`
    in `Goto`, two `*White` reads in `Stmt` (body prefix, before `=`),
    and `($'?' | *White)` subj/pat delimiter in `Stmt`.  Guideline §2
    canonical interpretation now: "honored except where grammar
    forbids" — binding on the family.

Gate state after SN-7-0a: **PASS=0 FAIL=59 — unchanged**, as expected
(style work does not change tree shapes).  Sibling parsers untouched;
no shared file changed.  120-col limit honored everywhere.

Setup notes for the next session: `libgc-dev` was not pre-installed
in the container — `install_system_packages.sh` did install it after
the apt lock cleared.  No bug; one-time install.

**Watermark (session 2026-05-04 cont. #4, partial — handoff):**

⚠ TASK INCOMPLETE.  Original task: apply unified style guidelines to
all six parser_*.sc files.  Completed five; parser_snobol4.sc not done.

Five sibling parsers unified to canonical style (corpus@9ab0f4f):
- E_FOO = "'E_FOO'" tag naming (self-quoting, name matches IR spec)
- /*===*/ /*---*/ section dividers (120 chars)
- \$'  '/\$' ' whitespace tokens (beauty.sno convention)
- Unified driver bottom across all six
- Gates all held: prolog PASS=54, icon PASS=51, snocone PASS=21,
  raku PASS=32, rebus PASS=18.

parser_snobol4.sc: STYLE PASS NOT DONE.  The file received a partial
SN-7-1 attempt (pp_stmt + rw_expr + rw_call + rw_goto_slot helpers)
that lifts gate to PASS=27 FAIL=32 but does NOT apply the unified
style guidelines that the other five received.  The pattern block is
verbatim beauty.sno (zero chars changed) — that part is correct.

⚠ Open question for next session: is the partial SN-7-1 work worth
keeping as a starting point, or should it be reverted to the clean
beauty.sno-verbatim baseline (PASS=0 FAIL=59) and the style pass
applied first as a separate clean commit?  The intent stated by Lon
was: do the style pass on all six FIRST, then SN-7-1 work happens
on top.  This session inverted that order for parser_snobol4.sc.

Passing: atom/{id,int,str}, assign/{int,str,var,mixed,seq}, cf/{label_bare,
label_only,label_assign,loop,goto_f,goto_u,repl_{empty,with_goto}},
concat/{str,two}, fn_call_{zero,two,three,str,nested,expr_arg}, fn_define,
pat_{cond,immed,label_pat,repl,seq_two,seq_three,alt_paren}.

Key insight discovered: single-line `if (flag) stmt;` in Snocone does NOT
behave as expected — the statement always executes. Must use `if (flag) { stmt; }`.
Also: `DIFFER(x)` returns '' (empty string) as VALUE; the success/failure
is only meaningful directly in an `if()` condition, not via assignment.

Remaining failures fall into four categories:
1. Goto direction: sf global stale across multi-stmt tree walk. The goto
   direction (S/F/unconditional) must come from the tree node itself, not
   the global sf. The tag string is always the literal "*(':' sf Brackets)"
   or "*(':' Brackets)"; direction must be stored in the child node or
   inferred differently.
2. ExprList arg passing: rw_call iterates c(args)[i] but the ExprList
   node from beauty.sno wraps args differently than expected.
3. Arith left-assoc: beauty.sno builds right-recursive arith trees;
   oracle is left-associative. Needs tree rotation in rw_expr.
4. Alt/seq split: E_ALT top-level body should not be split; only E_SEQ
   with n>=2 triggers :subj/:pat split.

Rule for next session: DO NOT TOUCH any pattern that Compiland references
downstream. The pattern block is golden. Only the helper functions
(pp_stmt, rw_expr, rw_call, rw_goto_slot, rw_tag) may be edited.

**Next milestone:** PARSER-SN-7-1 — bare label-only line confirm +
labels + assignment + tree-shape rewrite (FW-2 role-slot wrappers +
IR-tag rewrites `Stmt`→`STMT`, `Id`→`E_VAR`, `String`→`E_QLIT`,
`Integer`→`E_ILIT`, `Call`→`E_FNC`, `..`→`E_SEQ`, `|`→`E_ALT`) to
match scrip `--dump-parse` oracle.  This is the first rung where the
gate flips from PASS=0 to a positive number.

**SN-7-1 prep notes (session 2026-05-04 cont. #2, end-of-session):**
captured oracle shapes for the six simplest fixtures so the next
session opens with target-vs-current side-by-side already known:

| Fixture        | Oracle (--dump-parse)                                            | Parser today                                       |
|----------------|------------------------------------------------------------------|----------------------------------------------------|
| atom_id        | `(STMT :subj (E_VAR x))` `(STMT :lbl END :end)`                  | `(Stmt . (Id x) . . . . .)` `(Stmt (Label END) . . . . . .)` |
| atom_int       | `(STMT :subj (E_ILIT 42))`                                       | `(Stmt . (Integer 42) . . . . .)`                  |
| atom_str       | `(STMT :subj (E_QLIT "hi"))`                                     | `(Stmt . (String 'hi') . . . . .)`                 |
| cf_label_only  | `(STMT :lbl LOOP :subj (E_VAR x))`                               | `(Stmt (Label LOOP) (Id x) . . . . .)`             |
| cf_label_bare  | `(STMT :lbl START)` then `(STMT :eq :subj (E_VAR x) :repl (E_ILIT 1))` | (depends on Label/empty-body rewrite)        |
| assign_int     | `(STMT :eq :subj (E_VAR x) :repl (E_ILIT 5))`                    | `(Stmt . (Id x) (Integer 5) ('=' '=') . . .)`      |

Two structural shifts needed in `parser_snobol4.sc`:

1. **Tag string rewrites in shift()/reduce() calls** — these are
   straightforward find-and-replace at the leaf level:
   - `Id` shift → `E_VAR`
   - `Integer` shift → `E_ILIT`
   - `String` shift → `E_QLIT` (note: oracle double-quotes; current
     parser single-quotes — TValue branch in tdump.sc may need a check)
   - `Real` shift → `E_RLIT`
   - `Call` reduce → `E_FNC`
   - `..` reduce → `E_SEQ`
   - `|` reduce → `E_ALT`
   - `'.'` reduce → `E_CAPT_COND_ASGN`
   - `'$'` reduce → `E_CAPT_IMMED_ASGN`
   - `ProtKwd`/`UnprotKwd` shift → `E_KEYWORD` (SN-7-2 territory but
     the leaf rewrite lands here)
   - `LEN`/`BREAK`/`SPAN`/`ANY`/`NOTANY` reduce → `E_LEN`/`E_BREAK`/
     `E_SPAN`/`E_ANY`/`E_NOTANY` (currently routed via _pat_prim_call)

2. **`Stmt` reduce shape change — the harder part.**  Today
   `Command` reduces with `("'Stmt'" & 7)`, building a 7-positional
   tuple `(Stmt label expr14 expr1 sf goto extras...)`.  The
   `--dump-parse` oracle uses **role-slot wrappers** with `:`-prefixed
   tags — N varies per statement (label-only is 1 child, atom-stmt is
   1 child wrapped as `:subj`, assignment is 3 children `:eq :subj
   :repl`, full pat-match is 4-5 children, end-marker is 2 children
   `:lbl :end`).  The 7-tuple-with-`.`-placeholders shape has to be
   replaced by per-arm conditional pushes that emit only the role-slot
   children that actually fired.  Per the goal-file FW-2 description
   (above): `Tree(':subj', '', 1, child)` renders as `:subj <TLump>`,
   bare `:eq` is `tree(':eq', '')`.

The cleanest path is probably a **rewrite of the `Stmt` rule** — split
it into named alternatives (`StmtLabelOnly`, `StmtAtom`, `StmtAssign`,
`StmtPatMatch`, `StmtPatReplace`, `StmtEnd`) that each push their own
role-slot children + final `STMT` reduce with `nTop()` (variable
arity).  That trades the `& 7` fixed-arity for `& 'nTop()'` n-ary
collection per the canonical n-ary pattern (§5).  The `END` line is
its own alternative (oracle: `(STMT :lbl END :end)` — needs a `:end`
flag-wrapper child).

**Shared file impact:** none expected.  Tag strings are local to
`parser_snobol4.sc`; `tdump.sc`'s `TValue` already handles `E_QLIT`
double-quoting (per SN-5 history note), `E_VAR`/`E_ILIT` self-paren,
and the FW-1 generic-leaf branch.  The `:`-prefix branch in `TLump`
(FW-2) renders role-slot wrappers correctly today — verified by
sibling parsers IC=40/40, PR=48/48, RK=25/25, RB=38/38 all using
this convention.

**Order of work for SN-7-1 (suggested):**
  1. Leaf tag rewrites first (`Id`→`E_VAR`, etc.) — small diff,
     individual fixtures will still FAIL because Stmt shape is
     wrong, but the leaf-level tags will be right and visible in
     the diff output.
  2. Rewrite `Command`/`Stmt` to emit role-slot wrappers + n-ary
     `STMT` reduce.  Start with the three simplest cases —
     atom-only, label-only, label+atom — and confirm 3-5 fixtures
     PASS.
  3. Add `:eq` flag and `:repl` slot for assignment — confirm
     `assign_*` fixtures PASS.
  4. END-line alternative with `:end` flag — confirm all label-bare
     and END-handling fixtures PASS.
  5. Sweep remaining fixtures; categorize residual FAILs for
     SN-7-2..7-7.

PASS target for SN-7-1: at minimum the cf_label_bare fixture
(PARSER-SN-7-1's own gate per the rung table), realistically 10-20
of the 59 fixtures (the atom/label/assign cluster).  Pattern-match
fixtures (`pat_*`) likely defer to SN-7-2..7-6.

**Watermark (session 2026-05-04 cont. #3):** SN-7-1 is the next
session's work.  No code changes this session beyond the SN-7-0a
landing already at corpus@7d5a85a / .github@eebd8d8.  Gates green:
SN PASS=0 FAIL=59 (unchanged; flips on SN-7-1), SNOBOL4 smoke 7/7,
scrip(.sc) smoke OK.  Sibling parsers untouched (IC=40/40 PR=48/48
RK=25/25 RB=38/38 SC=13/13 per prior session record).

**Watermark (session 2026-05-04 cont. #5, corpus@85bdd30):**
**PARSER-SN-7-1 LANDED.  Gate flipped PASS=27 → PASS=59 (full
parity).**  Single commit, single file changed (`parser_snobol4.sc`,
+93/-38).  Sibling parsers untouched and verified green: IC=51/51,
PR=54/54, RK=32/32, SC=21/21.  Six targeted fixes + three pp_stmt
shape fixes — see SN-7-1 entry above for the per-fix breakdown.

Session opened on PASS=27/59 baseline (the partial SN-7-1 attempt
recorded in the prior watermark).  Pivoted from the sibling-style
unification work to a focused SN-7-1 landing per Lon's direction:
"loop toward perfection on parser_snobol4.sc first, then we loop
on six-parser concept-identical changes."  Six categories of bug
identified up-front and fixed in order:

  1. `rw_call` 1-arg / 0-arg branching — biggest impact (10+ FAILs).
  2. `rw_expr` paren-strip — fixed `concat_paren`, `arith_paren`.
  3. `rw_tag` unary `E_MNS`/`E_PLS` — fixed `arith_unary`.
  4. `rw_expr` left-rotation — fixed `arith_lassoc*`.
  5. Goto direction in tag — fixed `cf_goto_sf` SIGSEGV + `:goU`/`:go`
     mismatch.  Required deviating from beauty.sno's verbatim PATTERN
     block (named `Sgo`/`Fgo`/`Ugo` helpers in place of `SorF` +
     single tag); deviation documented inline.
  6. `pp_stmt` alt-eats-LHS + paren-defeat-fold + empty-replacement.

The "no SCRIP bug to fix" path was clean: no C-side changes needed
this session.  The `cf_goto_sf` SIGSEGV-then-:goF-on-S-goto bug was
NOT a SCRIP bug — it was a stale-`sf`-global design issue in the
prior `parser_snobol4.sc` rewrite.  Fixed entirely in the `.sc`
file.

**Open carry-over for next session:**
  - **PARSER-RB cleared.**  Initially flagged this session as a
    regression (RB=18/38 vs prior watermark's RB=38/38), but the
    18/38 was the actual rung state — the RB-2/3/4/5 rungs had
    not yet landed.  Per Lon's directive "fix rebus before we
    begin looping", session 2026-05-04 cont. #5 also landed
    PARSER-RB-2/3/4/5 in a single commit (corpus@09ecd59).
    Final gate: RB=38/38.  All six parsers now at 100%.
  - **INFRA-11b re-investigation.**  Carries from prior session.
    Quick probe shows `~`/`&` infix DOES dispatch to OPSYN target;
    if confirmed working, the family can drop the
    `shift(p,t)`/`reduce(t,n)` direct-call workaround.
  - **PARSER-SC FENCE/`*deref` silent-fail bug.**  Documented in
    `GOAL-PARSER-SNOCONE.md`.  Not addressed this session.
  - **SN-7-2 onward.**  Now that SN-7-1's PASS=59/59 parity is
    achieved on the existing fixture corpus, SN-7-2..7-7 add new
    fixture clusters (keywords, brackets, continuation lines,
    `;` separator, comments/control, `*Id` deferred-pattern ref)
    that extend beyond what the SN-0..SN-6 corpus exercised.
    SN-7-8 is the beauty.sno full crosscheck — the milestone gate.
  - **Six-parser cross-pollination.**  Lon's stated next-step
    workflow: "in a loop, take my direction for a targeted fix to
    all six parser_*.sc files, make the change, make that concept
    appear identical in all six, then run the test."  This session
    did NOT enter that loop — it landed SN-7-1 first to bring
    parser_snobol4.sc up to PASS=59/59 parity.  Next session opens
    in the loop; first targeted concept is operator's choice.
    Candidates the operator may pick from:
      * Promote the goto-direction-in-tag pattern across siblings
        (only relevant if any sibling parser has analogous
        cross-statement-stale-global issues — likely not, since
        SNOBOL4's `:S`/`:F` is a SNOBOL4-specific syntax).
      * Style guideline §7: `_`-prefix prohibition — none of the
        six parsers comply yet; this is a pure mechanical sweep.
      * Style guideline §4a: function-based action plumbing
        anti-pattern — flagged on at least PARSER-RK historically.
      * `rw_call` n-ary handling pattern — the 1-arg / 0-arg
        ExprList branching may have analogues in PARSER-PR
        (Prolog's compound terms) or PARSER-IC (Icon's argument
        lists) where a similar nTop()-conditional reduce is used.

**Next milestone:** PARSER-SN-7-2 (keyword recognition) when SN
work resumes; six-parser fix loop when Lon directs.

**Watermark (session 2026-05-04 cont. #6):** PARSER-FAMILY-LOOP
iteration #1 LANDED — White-encodes-comments cross-pollination.
All six `parser_*.sc` brought to a single canonical whitespace-token
shape:

  - `White` defined first per language (continuation/comment rules
    folded in: SNOBOL4 `+`/`.` continuation + `;*` inline trailing
    comment; Icon/Rebus/Raku `'#' BREAK(nl)`; Prolog `'%' BREAK(nl)`
    + `Block = '/*' ARBNO(BREAK('*') ANY('*')) '/'`; Snocone
    `'//' BREAK(nl)` + same `Block`).
  - `Gray = White | epsilon;` — bare reference, no `*` deferral
    (order makes deferral unnecessary).
  - `$' '  = Gray;` and `$'  ' = White;` — invisible-whitespace
    aliases with the beauty.sno `$' '` (optional) / `$'  '`
    (required) convention.
  - All grammar rules use `$' '`/`$'  '` only — no remaining
    `*White` or `*Gray` references anywhere.

Snocone gained C-style empty-statement semantics (Lon directive):
new `empty_cmd = $' ' $';' $' ' nl_opt;` plus Command alternative.
`x = 1;;/* hello */;;` and longer chains parse cleanly, output
matching the oracle byte-for-byte.

Dead code removed:
  - `parser_icon.sc` `Comment` rule (duplicate of `Blank` after
    `#` moved into White) and its `| Comment` alternative in
    `StmtBody`.
  - `parser_raku.sc` per-line `# REM` pre-filter at the input
    accumulation loop (now native via White).
  - `parser_prolog.sc` `comment` definition collapsed into White;
    `trivia` rewritten as `ARBNO(White | nl)`.

Gates (all unchanged at 100%): SN=59 IC=51 PR=54 RK=32 SC=21 RB=38.
Smoke: SNOBOL4 7/7 green; scrip(.sc) all OK.  Smoke-tested per
language: SNOBOL4 `;;`/`;*`, Icon `#` line + trailing, Rebus `#`,
Raku `#`, Prolog `%` + `/* */` + leading comment line, Snocone
`//` + `/* */` + `;;/* hello */;;` (oracle-matched).

**Next:** operator picks iteration #2 concept.

**Watermark (session 2026-05-04 cont. #7):** PARSER-FAMILY-LOOP iter#4
ABORTED IN-SESSION before any commit; superseded by iter#5 (one-letter
language prefix scheme).

Iter#4 concept (3-4-letter prefix `sno_`/`SNO_`, `sc_`/`SC_`,
`reb_`/`REB_`, `icon_`/`ICON_`, `pl_`/`PL_`, `raku_`/`RAKU_`) was
discussed and partial-landed locally on `parser_snobol4.sc`,
`parser_icon.sc`, and `parser_rebus.sc` (gates green at SN=59, IC=51,
RB=38).  Mid-session Lon directed a pivot to **one-letter** prefix
(`s_`/`S_`, `c_`/`C_`, `r_`/`R_`, `i_`/`I_`, `p_`/`P_`, `b_`/`B_`)
since the six `parser_*.sc` will load simultaneously into one SCRIP
process at Milestone 2 — and SCRIP/SNOBOL4/Snocone use a single flat
global symbol table (function names, top-level globals, and tag-string
constants all share one namespace; SPITBOL DEFINE auto-saves args/locals
but the function NAME itself lives in the global table).  Local
`parser_*.sc` edits reverted to iter#3 baseline (corpus@3e58061);
iter#4 row in iteration log marked SUPERSEDED.

**Iter#5 specifics** (next session opens here):

  - Worker prefix is lowercase letter + underscore: `s_pp_stmt`,
    `c_save_cond`, `b_lower_decl`, etc.
  - Pattern-builder companion prefix is uppercase letter + underscore:
    `S_push_qlit`, `C_save_cond`, `B_push_qlit`, etc.
  - Tag-string constants for parser-private surface tags also take the
    prefix: `B_FUNC_DECL`, `B_REC_DECL`, `B_ASSIGN`, `B_ALT`, etc.
  - Cross-parser shared IR-tag constants (`E_VAR`, `E_QLIT`, `E_ILIT`,
    `E_FNC`, `E_SEQ`, `E_ALT`, `E_Parse`, `E_ASSIGN`, ...) stay
    unprefixed — they are language-neutral final-IR identifiers.
  - Capture-slot globals (e.g. `q_body`, `s_body`, `p_text`,
    `rk_capvf`, `ic_strbody`, `rbStrBody`, `sc_strbody`) take the
    prefix.  Where the existing slot name already has a single-letter
    prefix that collides with the new scheme (Prolog's `p_text`,
    `p_name`, `p_negi`), rename to `p_h_text`, `p_a_name`, `p_neg_int`
    or similar — pick the cleanest reading that stays in `p_*`.
  - Wire-protocol identities — string values that the C oracle also
    emits, e.g. Rebus's `'rb_else_N'` / `'rb_end_N'` label format —
    are NOT renamed.  The Snocone parser's label-prefix string
    `'rb_'` (in `b_new_label`'s output) stays `'rb_'` and the
    function-side identifier renames around it.  Document inline at
    each such site.
  - Names should announce action.  Lon's directive: avoid placeholder
    suffixes like `_done` (current Raku has many).  Use verbs:
    `push`, `pop`, `store`, `save`, `make`, `build`, `finish`,
    `decompose`, `emit`, `lower`.

**Open question for next session — Step 7:** RESOLVED session 2026-05-04
cont. #7 — **`X` / `x_*` / `X_*` reserved for SCRIP** (scrip.sc) when
Milestone 2's Snocone-hosted runtime lands.  Mnemonic: X for executable /
cross-cutting.  Letter is reserved across all six parsers — no
parser-private identifier may begin `x_` or `X_`.

**Next milestone (iter#5):** ten-step landing per the bullet list in
"⚠ CURRENT STEP — PARSER-FAMILY-LOOP iter#5" above.  Steps 1-6 are
the per-parser renames; Steps 8-10 are gate verification + commit +
log update.  All six gates must hold at 100% at the end.

**Watermark (session 2026-05-04 cont.):** PARSER-FAMILY-LOOP **iter#9 closed**
(see iteration log row 9 — Phases A+B+C committed at one4all@4393ce1e the
prior session despite watermark text mis-stating "uncommitted"; SN regression
fix at corpus@61d825d; iter#10 supersedes Phase D for SN; RB closed by
sibling session at corpus@09d7f80) and **iter#10 LANDED** at corpus@408fbe0.

iter#10 summary: arith Expr-tier grammar in parser_snobol4.sc rewritten from
beauty.sno's right-recursive form `*Expr_n FENCE($'op' *Expr_n (TAG & 2) |
epsilon)` to iterative left-recursive form `Expr_n = *Expr_{n+1}
ARBNO(Expr_n_tail)` for the four arith/exp tiers (Expr6 +/-, Expr8 /,
Expr9 *, Expr11 ^/!/**). New shared `foldop(t)` build-time pattern-builder
in `semantic.sc` paired with `FoldOp(t, rhs, lhs)` match-time worker in
`ShiftReduce.sc`: pop rhs, pop lhs; if `t(lhs) == t`, append rhs as another
child of lhs (extends flat n-ary chain); otherwise build fresh binary.
Mirrors C-frontend `expr_binary_flatten()` shape exactly. Same-tag chains
build flat n-ary at parse; mixed-op chains build left-binary at tier
boundaries. Removes `is_flatten_op()` predicate and the flatten branch in
`rw_expr` (rotate branch for `E_CAPT_*_ASGN` binary kept since runtime is
still strictly binary for those).

**Latent same-tier mixed-op bug fixed**: `1 + 2 - 3` was producing
`(E_ADD 1 (E_SUB 2 3))` under the post-flatten approach because the
right-recursive Expr6 grammar mixed `+` and `-` at the same RHS recursion;
oracle emits `(E_SUB (E_ADD 1 2) 3)`. Three new fixtures lock this in:
`arith_mixed_addsub.sno` (1+2-3), `arith_pow_chain.sno` (2**3**2 right-fold),
`arith_chain_long.sno` (1-2+3-4+5 five-element mixed chain).

**Cross-pollination opportunity** flagged in commit message for future
iterations: parser_icon.sc, parser_prolog.sc, parser_raku.sc,
parser_snocone.sc all share the same latent same-tier-mixed-op bug today.
Verified manually: `1+2+3` against parser_icon emits
`(E_ADD (E_ADD 1 2) 3)` while oracle emits `(E_ADD 1 2 3)`; same shape
mismatch as SN had. Their gate corpora don't exercise it. When the loop
opens iter#11+ for those parsers, `foldop()`/`FoldOp()` are now in shared
infra ready to use. No changes to existing reduce/shift OPSYN binding.

Final gate state (after sibling-session syncs):
  PARSER-SN PASS=62/62 ✅ (mine, +3 fixtures vs. 59 baseline)
  PARSER-IC PASS=88/88 ✅
  PARSER-PR PASS=54/54 ✅
  PARSER-RK PASS=31/32 (one pre-existing fail: arith_chain — iter#9 RK
                       Phase D pending; same `foldop` cross-pollination
                       fix would close it)
  PARSER-SC PASS=46/46 ✅
  PARSER-RB PASS=38/38 ✅ (sibling session closed iter#9 RB Phase D)
  All smoke gates green; SNOBOL4 7/7; scrip(.sc) all OK.

**No SCRIP C-side bugs encountered** during iter#10 work. Two `.sc`-level
gotchas surfaced and are documented:
  1. The `is_xxx = 0; return;` pattern for predicate-false return is wrong
     in Snocone — caller's `if (is_xxx())` always enters then-branch
     because every value (including 0 and '') is truthy in signal-based
     conditional context. Use `is_xxx = .dummy; freturn;` to signal failure.
  2. `EQ('', N)` fails (success/failure semantics, not boolean) — usable
     in pattern context but conditions on it the way `if (n(x) == 2)`
     would in C don't apply. Test count via `EQ(n(x), 2)` directly in
     `if(...)` works because `EQ` succeeds only when equal.

**Next milestone:** operator picks. Candidates:
  - **iter#11**: cross-pollinate `foldop()` to the four other affected
    parsers (IC, PR, RK, SC). RK arith_chain closes simultaneously.
  - **iter#9 Phase E**: FENCE sweep, second pass across all six parsers.
  - **Cleanup CR-1..CR-5**: Rebus RExpr → EXPR_t double-layer removal —
    now lower priority since RB closed Phase D without it. Standing
    question whether to land it as architectural cleanup or defer
    indefinitely. Context: RExpr has `~287 lines` of type defs in
    `rebus.h`; `rebus_lower.c` is ~732 lines (RExpr→EXPR_t walker plus
    structured-stmt → label+goto STMT_t lowering); statement-level
    lowering doesn't easily fold into reduce actions because it needs
    label-counter + loop-stack state (snocone solves this with
    `ScParseState` in `.y` actions — feasible but substantial port).
    Standalone `rebus -p`/`-e` debug binary (rebus_main.c, rebus_emit.c,
    rebus_print.c) is dead code — no live caller in scripts/.
  - **iter#10b**: same-pattern audit — the surviving `is_rotate_op`
    rotation block in parser_snobol4.sc's `rw_expr` exists only because
    runtime `E_CAPT_*_ASGN` handlers are strictly binary. Once those go
    n-ary, that block deletes too. Cross-references runtime work.

**Watermark (session 2026-05-04 cont. continued):** **Phase E (FENCE
sweep, second pass) — parser_snobol4.sc PARTIAL LANDED** at
corpus@c6bb327.  Three iter#10 ARBNO tail rules wrapped in FENCE():
`Expr8tail` (single-op `/`), `Expr9tail` (single-op `*`),
`Expr11tail` (three-way alt `^/!/**`).  Three-line diff.

Cross-pollination across all six parsers iter#11 closed: parser_*.sc
gates are all 100%:

  PARSER-SN PASS=62/62 ✅
  PARSER-IC PASS=88/88 ✅
  PARSER-PR PASS=60/60 ✅ (sibling session +6 fixtures via PARSER-PR-8b)
  PARSER-RK PASS=37/37 ✅ (sibling session +6 fixtures via PARSER-RK-5,
                          which ALSO landed n-ary arith flatten —
                          cross-pollination of iter#10 foldop pattern
                          arrived independently for RK)
  PARSER-SC PASS=46/46 ✅
  PARSER-RB PASS=38/38 ✅

**Outstanding work specific to parser_snobol4.sc:** essentially none.
The parser_snobol4.sc file is at canonical-shape parity with the C
frontend oracle for the entire 62-fixture corpus, with iter#7 (no
rw_tag), iter#8 (FENCE first pass), iter#10 (iterative left-recursive
arith with foldop), and Phase E (FENCE on iter#10 tail rules) all
landed.  The surviving `is_rotate_op` rotation block in `rw_expr` is
the only structural artifact remaining; it's there because runtime
`E_CAPT_*_ASGN` handlers are strictly binary, and removing it requires
runtime work outside this goal's scope (iter#10b).

**Next milestone candidates** (operator picks; SN-specific options
are exhausted, so the candidates broaden):

  - **PARSER-SN-7-2 onward**: fixture-cluster expansion under the
    SN-7 ladder.  The current 62 fixtures don't exercise: keyword
    recognition (`&UCASE`, `&LCASE`, etc.), bracket-index `x[i]`,
    `+`/`.` continuation lines, `*Id` deferred-pattern reference,
    `;` mid-line statement separator, comment/control lines.  Each
    is its own narrow rung (SN-7-2..7-7) with focused fixtures.
    SN-7-8 is the beauty.sno full crosscheck — the milestone gate.

  - **iter#10b**: same-pattern audit — once runtime `E_CAPT_*_ASGN`
    handlers go n-ary, the `is_rotate_op` rotation block in
    parser_snobol4.sc's `rw_expr` deletes too.  Cross-references
    runtime work (out of `parser_snobol4.sc` scope).

  - **Cleanup CR-1..CR-5** (Rebus RExpr → EXPR_t double layer):
    deferred indefinitely now that RB closed Phase D without it.

  - **PARSER-SN-FW-4**: `scrip --parser-crosscheck` C-side flag
    (deferred, on the goal-file ladder).  Replaces shell-level
    byte-diff with C-callable `tree_equal` and Snocone-bridge
    `cross_emit_tree`.

**Watermark (session 2026-05-05):** **PARSER-SN-7-2 LANDED** — &KEYWORD
recognition.  Four fixtures: `kw_fullscan.sno`, `kw_maxlngth.sno`,
`kw_ucase.sno`, `kw_lcase.sno`.  Bug fixed: `*ProtKwd ~ E_KEYWORD` and
`*UnprotKwd ~ E_KEYWORD` were shifting the full `&NAME` text (including
`&`), but oracle emits name-only `(E_KEYWORD FULLSCAN)`.  Fix: expanded
both alternatives to `'&' shift(SPAN(&UCASE &LCASE), E_KEYWORD)` — consume
`&` before the capture so `shift` sees only the name portion.  ProtKwd and
UnprotKwd are identical structurally (both `'&' SPAN(&UCASE &LCASE)`) so
collapsed to one alternative.  PASS=66/66 ✅.

**PARSER-SN-7-3 LANDED** — bracket index `x[i]`, `x[i,j]`.  Four
fixtures: `idx_simple.sno`, `idx_multi.sno`, `idx_nested.sno`,
`idx_in_assign_lhs.sno`.  Two fixes: (1) `E_IDX = "'E_IDX'"` constant
added (Expr15 was using hardcoded `"'[]'"`); (2) `rw_expr` E_IDX case
added — flattens ExprList bracket-group children directly into E_IDX
(default walk produced E_SEQ wrapper; oracle emits flat children).
PASS=70/70 ✅.

**Watermark (session 2026-05-05 cont.):** **PARSER-SN-7-4 through SN-7-7
LANDED** — continuation lines, comment/control lines, `*Id` defer,
`;` separator.

- SN-7-4 (cont_plus, cont_dot, cont_chain): no changes needed — White
  already handled `nl '+'/'.` continuation. PASS=73/73.
- SN-7-5 (mixed_comment_control): no changes needed — Command already
  silently consumed comment lines. PASS=74/74.
- SN-7-6 (defer_simple, defer_alt, defer_in_pat): added `E_DEFER =
  "'E_DEFER'"` constant; fixed Expr14 `'*' *Expr14 ("'*'" & 1)` →
  `(E_DEFER & 1)`. PASS=77/77.
- SN-7-7 (semi_separator): no changes needed. PASS=78/78.

**Watermark (session 2026-05-05 cont.):** **EMERGENCY REVERT** — parser_snobol4.sc restored to SN-7-1 base (corpus@85bdd30).

Root cause found: iter#7 changed X4 from `FENCE(*White *X4 | epsilon)` to `FENCE($'  ' *X4 | epsilon)`, and iter#10 introduced ARBNO(Expr6tail) etc. These changes broke ARBNO(*Command) inside Compiland — when Expr6's ARBNO(Expr6tail) tries `$'+'` (White '+' White), White consumes a space then '+' fails; SNOBOL4 backtracking restores the nam-assignment stack, which undoes nInc() side effects from Command's counter. Result: Compiland ARBNO gets 0 matches for any statement with a concat RHS containing a deferred call (`A *f`, `(A|B) *upr(tx)` etc.).

SN-7-1 grammar uses `*White` (deferred) everywhere — backtracking safe. beauty.sno parses fully: 434 STMTs, reaches END. PASS=62 (16 fails are SN-7-2/7-3/7-6 fixtures that postdate SN-7-1 and need targeted grammar fixes on top).

**Next session:** starting from this SN-7-1 base, apply changes one at a time from iter#7 diff and find exact commit that breaks beauty.sno parsing. Then fix that change before re-applying downstream improvements.

**Watermark (session 2026-05-05, corpus@efcbf2d): PASS=78 FAIL=0 ✅ — SN-7-2/7-3/7-6 + arith left-assoc landed.**

All 16 previously-failing fixtures now pass. Changes all in `parser_snobol4.sc` only; no shared file touched.

**SN-7-2** (&KEYWORD): `Expr14` `*ProtKwd ~ 'ProtKwd'` / `*UnprotKwd ~ 'UnprotKwd'` → `'&' shift(SPAN(&UCASE &LCASE), E_KEYWORD)`. Consume `&` before capture; shift name-only. Both alts identical so collapsed to one. `E_KEYWORD = "'E_KEYWORD'"` constant added.

**SN-7-6** (defer): `Expr14` `'*' *Expr14 ("'*'" & 1)` → `'*' *Expr14 reduce(E_DEFER, 1)`. `E_DEFER = "'E_DEFER'"` constant added. Dead `'&' *Expr14` unary removed (& now consumed by keyword prefix).

**SN-7-3** (bracket index): `E_IDX = "'E_IDX'"` constant added; `Expr15` uses it. `rw_expr` E_IDX case: when child is ExprList, its children are individually `rw_expr`'d and appended to E_IDX — producing `(E_IDX A 1 2)` not `(E_IDX A (E_SEQ 1 2))`.

**Arith left-assoc (iter#10 re-applied safely)**: Replaced right-recursive `Expr6`/`Expr8`/`Expr9`/`Expr11` with FENCE-based iterative left-recursive form using `foldop()`/`FoldOp()` from shared infra. Each tier: `Expr6 = *Expr7 FENCE($'+' *Expr7 foldop(E_ADD) *Expr6cont | $'-' ... | epsilon); Expr6cont = FENCE(...)`. FENCE preserved (unlike iter#10's ARBNO) to prevent backtracking from unwinding `nInc()` side-effects inside `Compiland`'s `ARBNO(*Command)` — the root cause of the emergency revert. `FoldOp`: pop rhs+lhs; if `t(lhs)==t` append rhs (flat n-ary same-op chain); else fresh binary (mixed-op left-assoc). Removed left-rotation from `rw_expr` for arith. `E_CAPT_*_ASGN` rotation kept (runtime still strictly binary).

beauty.sno parse fidelity preserved: 434 STMTs (same as SN-7-1 baseline). All smoke gates green. Other five parsers untouched.

**Next milestone:** SN-7-8 — beauty.sno full crosscheck (parser vs `--dump-parse` oracle, whitespace-normalized). 434/1084 STMTs currently match shape; many constructs in beauty.sno not yet handled by the parser (missing: POS, RPOS, CURSOR, TAB, RTAB, ARBNO, FENCE, LGT, LEQ etc. as pattern primitives; `E_IDX` on complex exprs; multi-bracket chains). Or: PARSER-FAMILY-LOOP next iteration (operator picks).

**Watermark (session 2026-05-05, corpus@0390853): PASS=78 FAIL=0 ✅ — SN-7-7b landed: E_* direct + rw_tag deleted.**

Three changes landed this session, all in `parser_snobol4.sc` only:

**iter#2/3 catch-up (corpus@ebb9b72):** Whitespace-token canonicalization —
`$'  '`/`$' '` form applied to parser_snobol4.sc to match the other five
parsers. `Gray = *White | epsilon` → `Gray = White | epsilon`; all operator
tokens `*White 'op' *White` → `$'  ' 'op' $'  '`; all bracket tokens updated;
X4, Sgo/Fgo, Goto, Stmt all use `$'  '`/`$' '` throughout. PASS=78 FAIL=0.

**SN-7-7b (corpus@0390853):** Grammar now emits canonical E_* IR tags directly
at every shift/reduce site. `rw_tag` dispatch table deleted entirely (27 lines
gone). `rw_expr` is now a pure structural rewrite: paren-strip, ExprList-unwrap,
E_IDX-flatten, E_CAPT_*_ASGN left-rotation — no tag knowledge. String quotes
stripped at parse time via dot-capture + `Push_qlit` pair-shape worker. Net:
−91 lines. PASS=78 FAIL=0.

Key implementation notes for next session:
- `E_*` string constants are pre-quoted (`E_VAR = "'E_VAR'"`) for use in
  reduce()/shift() pattern calls. BUT in `rw_expr`/`rw_call`/`pp_stmt` helper
  functions, all `IDENT(t, ...)` and `Tree(...)` calls use bare string literals
  (`'E_VAR'` not `E_VAR`) — because `t(x)` returns the bare tag string, not
  the pre-quoted form. This distinction is critical.
- `ExprList` internal tag kept as `'ExprList'` (not changed to E_SEQ) to
  disambiguate from grammar-built E_SEQ concat nodes. `rw_expr` and `rw_call`
  both test `IDENT(t, 'ExprList')` for arg-list nodes.
- `Push_qlit` uses `tree('E_QLIT', str_body)` with bare `'E_QLIT'` string
  (not the `E_QLIT` constant) for the same reason.
- E_CAPT_*_ASGN left-rotation in `rw_expr` still needed — grammar is right-
  recursive for `.`/`$` capture operators; oracle is left-associative.

**Next milestone:** SN-7-8 — beauty.sno full crosscheck. Or PARSER-FAMILY-LOOP
next iteration (operator picks). context window was ~90% at handoff.

**Watermark (session 2026-05-05 cont., corpus@0390853): SN-7-7c added as current step.**

Session observation: parser_snobol4.sc is missing beauty.sno's complete
identifier-classification machinery — the `Functions`, `BuiltinVars`,
`SpecialNms`, `ProtKwds`, `UnprotKwds` word-list tables, the `TxInList`
membership-test pattern, the `match()` helper, and the `Function`/`BuiltinVar`/
`SpecialNm`/`ProtKwd`/`UnprotKwd` classifier patterns in Expr14/Expr17.
Currently `Expr17` uses bare `*Id` for all identifiers and `Expr14` uses
a bare `SPAN` for keywords — syntactically correct but unfaithful to
beauty.sno's structure and incomplete for SN-7-8 crosscheck.

SN-7-7c is inserted before SN-7-8 to add this inventory. Step 1 requires
consulting x64, x32, csnobol4 repos for definitive lists; beauty.sno's
lists are the primary model. Context window was ~96% at handoff — next
session opens fresh to execute SN-7-7c steps 1-7.
**Watermark (session 2026-05-05 cont., corpus@0fba291): SN-7-7c LANDED PASS=78 FAIL=0 ✅.**

Cross-runtime symbol inventory complete. Sources scanned: SPITBOL x64 `sbl.min`
sv-classes (svfnf/svfnn/svfnp/svfpr/svfnk/svfpk/svknm/svkvc/svkvl/svkwc/svlbl
+ class-0 TERMINAL); SPITBOL x32 `s.min` (verified ≡ x64 byte-identical
inventory); csnobol4 `v311.sil` KNLIST (unprot kw), KVLIST (prot kw), FNLIST
(user functions). Final lists are the union with one resolved conflict:
ERRTEXT/ERRTYPE classify as **UnprotKwds** per SPITBOL+beauty.sno (settable
keywords), not ProtKwds (csnobol4 quirk).

**Final inventory** (counts in parens):
- Functions   (123) — full SPITBOL+csnobol4 union, including BLOCKS extensions
                      (BCHAR, DEPTH, FREEZE, FUNCTION, HEIGHT, HOR, LABEL,
                      MERGE, NODE, NORM_REG, OVY, PAR, PRINT, REP, SER, SLAB,
                      THAW, VALUE, VDIFFER, VER, WIDTH, ...)
- UnprotKwds  (21)  — incl. csnobol4 extras FATALLIMIT, FILL, GTRACE
- ProtKwds    (28)  — incl. csnobol4 extras COMPNO, DIGITS, FATAL, GCTIME,
                      MAXINT, PARM, PI, STEXEC, STFCOUNT
- BuiltinVars (7)   — ABORT ARB BAL FAIL REM SUCCEED TERMINAL (per beauty.sno)
- SpecialNms  (8)   — ABORT CONTINUE END FRETURN NRETURN RETURN SCONTINUE START

**Implementation deviations from goal-file Step 3/4 prescription** (all required
to make membership-test work in the Snocone runtime; intent and gate unchanged):

1. **Step 3 form** — used bare-operator `pat $ tx $ *sn_match(L, TxInList)` not
   `pat $'$' tx $'$' *match(L, TxInList)`. Verified against omega.sc usage
   and snocone_parse.y T_2DOLLAR (binary E_CAPT_IMMED_ASGN at expr12).
   Inlined helpers `sn_match`/`sn_upr` to avoid expanding the shared parser
   blob (other five PARSER-* parsers don't need them; zero blast radius).

2. **Step 4 form** — used `'&' shift(*ProtKwd, E_KEYWORD)` not
   `*ProtKwd shift(tx, E_KEYWORD)`. The goal-file form treats `tx` as the
   pattern arg to `shift(p, t)` — but `shift` expects a pattern. More
   importantly, the alternative `*ProtKwd Push_kwd` (with `Push_kwd =
   epsilon . *push_kwd()` reading `tx`) FAILS because the dot-capture
   deferred call fires only when the enclosing match completes — by that
   time later patterns have rebound `tx`. The fix: `shift(p, t)` expands to
   `p . thx . *Shift(t, thx)` where `thx` is the runtime's scratch global
   that gets read AT the moment the sub-pattern's capture completes (the
   canonical thx-relay idiom used throughout semantic.sc). So consume `&`
   outside, classifier is bare (just the membership-test SPAN+match), and
   `shift(*ProtKwd, E_KEYWORD)` does the rest correctly.

3. **Step 5 fallback retained** — kept `*Id ~ E_VAR $'(' *ExprList $')'
   (E_FNC & 2)` and `*Id ~ E_VAR` AFTER the classifier alternatives, so
   user-defined functions/variables (not in any list) still parse.

**No SCRIP runtime bug encountered.** All edits in `parser_snobol4.sc` only;
shared blob and other parsers untouched. Net diff: +79/-2 lines.

**Next milestone:** SN-7-8 — beauty.sno full crosscheck. Many constructs in
beauty.sno still not handled by the parser (missing pattern primitives POS,
RPOS, CURSOR, TAB, RTAB, ARBNO, FENCE, LGT, LEQ, etc., though these are now
recognized as Functions in classification — the grammar still needs to accept
them where they appear as pattern primitives in Expr-positions). Or:
PARSER-FAMILY-LOOP next iteration (operator picks).
