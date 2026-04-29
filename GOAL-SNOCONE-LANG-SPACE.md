# GOAL-SNOCONE-LANG-SPACE — Snocone Looks Like SNOBOL4

**Repo:** one4all + corpus
**Done when:** Snocone source no longer needs the `&&` concatenation
operator.  Concatenation is expressed by juxtaposition (whitespace
between value-yielding tokens), exactly as in SNOBOL4.  Function
calls follow SNOBOL4 spacing: `f(args)` is a call, `f (expr)` is
`f` concatenated with `(expr)`.  Every `.sc` file in the corpus
runs through the new grammar with no `&&` token, and produces
output byte-identical to the pre-change form.

---

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
bash /home/claude/one4all/scripts/build_spitbol_oracle.sh
```

Gate after setup (the existing Snocone gates — these must remain
PASS=5, PASS=42 SKIP=3, PASS=49+ throughout the language change):

```bash
bash /home/claude/one4all/scripts/test_smoke_snocone.sh
bash /home/claude/one4all/scripts/test_beauty_snocone_all_modes.sh
bash /home/claude/one4all/scripts/test_smoke_unified_broker.sh
```

---

## Why this goal exists

Lon (session #67–#68): "we need to make Snocone more like SNOBOL4.
Let's remove the `&&` operator and follow X Y concat and F() function
space requirements.  It will look so much better."

The aesthetic payoff is real.  Today's `beauty.sc`:

```
Real = ( SPAN(digits)
      && ('.' && FENCE(SPAN(digits) | epsilon) | epsilon)
      && ('E' | 'e') && ('+' | '-' | epsilon) && SPAN(digits)
     | SPAN(digits) && '.' && FENCE(SPAN(digits) | epsilon)
     );
```

After:

```
Real = ( SPAN(digits)
         ('.' FENCE(SPAN(digits) | epsilon) | epsilon)
         ('E' | 'e') ('+' | '-' | epsilon) SPAN(digits)
       | SPAN(digits) '.' FENCE(SPAN(digits) | epsilon)
       );
```

That's what the canonical `beauty.sno` already looks like.  Snocone
ports stop being SNOBOL4-with-extra-noise and become SNOBOL4 with
structured-control sugar.  This is also a forcing function for
clean grammar design — every implicit-concat ambiguity that would
break the language has to be resolved cleanly, not papered over
with `&&`.

---

## Architecture (what changes, where)

### 1. Lexer (`src/frontend/snocone/snocone_lex.c` / `.l`)

Today `&&` is a token.  Tomorrow it isn't.  Whitespace between two
value-yielding tokens becomes the concat operator — a SNOBOL4-style
"silent token" emitted by the lexer.

The standard technique: lexer maintains a "previous token" state.
After emitting a value-yielding token (IDENT, NUMBER, STRING, `)`, `]`,
keyword that returns a value), if the next non-whitespace character
starts another value-yielding token AND there was at least one
whitespace character between them, emit a CONCAT token before the
next token.

**Function-call disambiguation** — the rule SNOBOL4 uses:

| Source     | Tokens                       |
|------------|------------------------------|
| `f(x)`     | IDENT(f) LPAREN IDENT(x) RPAREN — call form |
| `f (x)`    | IDENT(f) CONCAT LPAREN IDENT(x) RPAREN — concat with paren expr |
| `f( x )`   | IDENT(f) LPAREN IDENT(x) RPAREN — call (whitespace inside is fine) |

The lexer's "no whitespace between IDENT and LPAREN" check is what
distinguishes the two.  Once the lexer commits to call-form, the
whole arg list is parsed as a comma-separated arg list — no concat
token is emitted between IDENT(f) and LPAREN.  After the matching
RPAREN, normal whitespace-as-concat rules resume.

### 2. Grammar (`src/frontend/snocone/snocone_parse.c`)

Today the grammar has explicit `expr CONCAT expr` (where CONCAT is
`&&`).  Tomorrow it has the same rule but CONCAT is the
lexer-emitted token from the rule above.

**Precedence.** SNOBOL4's table (per SPITBOL manual section on
expression evaluation):

```
lowest:    | (alternation)
           ? (match in pattern context)
           , (arg separator — not really an op)
           &&  (currently — Snocone-only)
              ← concat will sit here, higher than | and ?
           = (assignment, but assignment is statement-level)
           + - (additive)
           * / % (multiplicative)
           ^ ! ** (exponent)
           unary ops: + - ~ @ * & . $ ?  (very tight)
highest:   . $ (conditional value assignment in pattern context)
```

For Snocone we need to match this exactly, with concat sitting
where `&&` sits today.  No grammar surgery on precedence levels —
just renaming the operator and changing how it's lexed.

### 3. Corpus migration

Every `.sc` file gets `&&` removed.  The mechanical sweep is
straightforward but needs care:

- `X && Y` → `X Y` (typical case)
- Keep `&&` inside string literals untouched (e.g., the EVAL
  string `"epsilon . *Reduce('" && t && "', " && n && ")"` —
  but wait, that `&&` IS the concat in Snocone code so it gets
  removed too).
- Watch out for line continuation: `X &&\n    Y` → `X\n    Y`
  is fine because the newline-and-indent is whitespace.
- Be careful around `*White` and similar pattern-valued names —
  juxtaposing two IDENTs with no whitespace would look like
  one identifier; the lexer's value-yielding-token rule handles
  this correctly.

A Python script (`scripts/util_migrate_snocone_amp.py`) does the
sweep mechanically; manual review catches the edge cases.

---

## Open design questions (to resolve in LS-0..LS-2 before any code)

### Q1. Transition strategy — atomic flip vs. dual-syntax window

**Option A — Atomic flip.**  In one commit: lexer change + grammar
change + corpus sweep.  Single PR, clear before/after.  Risk:
huge diff, mistakes are hard to bisect.

**Option B — Dual-syntax window.**  Lexer accepts both `&&` and
whitespace-as-concat for one release.  Migrate corpus piecemeal.
Then a second commit removes `&&` recognition.  Risk: dual rules
create their own ambiguities (e.g., is `X && Y` two tokens or
three: X, CONCAT(=&&), Y?), and the window can stretch out.

**Recommendation:** Option A.  The corpus is small enough (~30 .sc
files) that a mechanical migration is feasible, and `&&` doesn't
overlap with any other Snocone construct, so the lexer change is
self-contained.  Keep the diff in two commits if the reviewer
prefers — one for one4all (lexer + grammar), one for corpus
(sweep) — but landed back-to-back.

### Q2. What is a "value-yielding token"?

The lexer needs to know when whitespace means concat.  The
predicate is: the previous token can end an expression, AND the
next token can start an expression.  Concretely:

| Previous can-end                      | Next can-start                       |
|--------------------------------------|--------------------------------------|
| IDENT, NUMBER, STRING                | IDENT, NUMBER, STRING                |
| RPAREN, RBRACKET                     | LPAREN, LBRACKET                     |
| keyword returning a value (e.g. `epsilon`, `&UCASE`) | keyword starting an expr             |
| unary postfix (none in SNOBOL4 today) | unary prefix (`*`, `&`, `~`, `@`, `.`, `$`) |

Things that can't end an expression: binary operators, `,`, `;`,
`{`, `(`, `[`, `if`, `while`, `else`, `return`.

If the previous token is in the "can-end" set and the next is in
the "can-start" set and at least one whitespace character
separates them, emit CONCAT.

### Q3. Function-call tightness rule — exactly no whitespace?

In classic SNOBOL4 the call form is `name(` with literally zero
characters between.  Modern parsers sometimes allow `name (` and
treat it as a call too — but that breaks the very disambiguation
we want.

**Decision:** Strict — `f(` must have zero intervening characters
(not even a space) for it to be a call.  `f (` is concat with a
parenthesized expression.  Matches SPITBOL.  Matches the user's
mental model.

### Q4. Comments and line continuation

Today: `// to end of line`, and `\n` ends a statement (with `;`
optional).  After the change: same rules, but whitespace now
includes line continuation.  No new constructs needed.  Verify:
multi-line patterns like `Real = ( SPAN(digits)\n    'foo' )`
work correctly — the newline+indent counts as whitespace, the
two values get a CONCAT between them.

### Q5. Statement separator — `;` becomes critical

Today: `;` ends a statement, but `&&` could span lines, so the
parser is somewhat flexible.  After: every statement MUST end
with `;` because juxtaposition over a newline still means concat
(if the next line's first token is value-yielding).  Conflict:

```
x = 1
y = 2
```

Without `;`, `1 y` parses as concat — wrong.  With Snocone today
the existing `;`-required rule already handles this.  So:
**every Snocone statement must end with `;`** (no change from
today).  The grammar treats `;` as the only statement terminator.
A bare newline is whitespace, not a terminator.

### Q6. Argument-list whitespace

`f(a b, c)` — what does this mean?

Option α: `a b` is `a` concat `b` as the first arg, `c` is the
second.  Two args.

Option β: Disallow concat in arg lists; require parens:
`f((a b), c)`.

**SNOBOL4 behaviour:** option α.  `f(a b, c)` is two args, first
is `a b` (concat).  Adopt the same.

### Q7. Backward compatibility — supporting `&&` indefinitely?

After LS-6 (final cleanup), `&&` is a syntax error.  No
backward-compatibility flag.  Snocone source files that still
have `&&` will not compile.  The mechanical sweep is part of the
goal — every `.sc` file in the corpus gets migrated in the same
commit train.

If a future user wants `&&` for some reason, they can use the
ASCII concat operator equivalent (whitespace), or wrap in a
function — Snocone has no other concat syntax to fall back on,
which is the point.

---

## Steps

- [ ] **LS-0** — Read SPITBOL manual sections on lexer / token /
  expression evaluation in full (sections 3, 4, 8 plus the
  precedence appendix).  Extract the canonical precedence table
  to this Goal file.  Compare against `snocone.sc`'s `bconv[]`
  table (already extracted in `GOAL-SNOCONE-BEAUTY.md`).  Identify
  every place the two disagree.

- [ ] **LS-1** — Lexer design.  Write down (in this Goal file) the
  exact lexer state machine: what counts as a value-yielding
  token, when whitespace emits CONCAT, how `IDENT(` is special-
  cased.  Plus a 30-line test corpus with expected token streams
  for every edge case.  No code yet.

- [ ] **LS-2** — Grammar design.  Write down (in this Goal file)
  the new precedence table and the grammar rule for concat.
  Show how every existing `&&` site lowers to the new rule.  No
  code yet.

- [ ] **LS-3** — Lexer implementation.  Edit `snocone_lex.c` (or
  the `.l` source if grammar-driven).  Run the 30-line test
  corpus from LS-1 through it.  All token streams match.

- [ ] **LS-4** — Grammar implementation.  Edit `snocone_parse.c`
  (or the `.y` source).  Add the concat rule.  Verify with a
  10-line `.sc` test that uses both `&&` and whitespace concat
  (only during transition; at LS-6 the `&&` gets removed).

- [ ] **LS-5** — Corpus migration script.  Write
  `scripts/util_migrate_snocone_amp.py` that mechanically
  rewrites every `&&` in every `.sc` file under
  `corpus/programs/snocone/`.  Edge cases (string-literal `&&`,
  multi-line continuation) handled or flagged.

- [ ] **LS-6** — Atomic landing.  In one commit train: lexer
  change + grammar change + corpus sweep + remove `&&` from
  the lexer.  All gates green.

- [ ] **LS-7** — Update `RULES.md`'s Snocone language-facts
  section to reflect the new syntax.  Update
  `GOAL-SNOCONE-BEAUTY.md`'s language-facts to drop `&&` from
  the binary-operator table.

---

## Invariants

- Gates remain at PASS=5, PASS=42 SKIP=3, PASS=49+ throughout.
- No `.sno` source files are modified — this goal is purely about
  Snocone (`.sc`).
- Generated parser/lexer files are regenerated and committed
  alongside the `.l`/`.y` sources, per RULES.md.
- Commit identity LCherryholmes / lcherryh@yahoo.com.

---

## Cross-goal coordination

- **GOAL-SNOCONE-BEAUTY (SB-5b active):**  This language change
  will make `beauty.sc` look almost identical to `beauty.sno`.
  Land SB-5b first (the `&` / `~` rewrite as `reduce()` /
  `shift()` calls), then this goal — the corpus sweep in LS-5
  will then sweep `beauty.sc` along with everything else.
- **GOAL-LANG-SNOCONE (D-1):**  The Snocone frontend ladder.
  This goal IS the next major milestone in that ladder.  When
  LS-7 lands, `GOAL-LANG-SNOCONE` advances from D-1 to D-2.
- **Other Snocone goals (CL-2, TB-1, SC-1):**  Frozen during the
  language transition.  After LS-6 they resume on the new syntax.
