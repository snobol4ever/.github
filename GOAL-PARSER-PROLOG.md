# GOAL-PARSER-PROLOG.md — PARSER-PROLOG pattern-based frontend in Snocone

**Repo:** corpus+one4all
**Branch:** `parser` (one4all only — `corpus` and `.github` stay on `main`)
**Sibling ladder:** `GOAL-LANG-PROLOG.md` and `GOAL-PROLOG-IR-RUN.md`. The
existing Prolog frontend (`src/frontend/prolog/`) is the in-process oracle.

**Done when:** A Snocone program `parser_prolog.sc` reads Prolog source,
runs one `Compiland` PATTERN that builds the canonical IR tree, and for
every test program in the rung corpus
`tree_equal(existing_frontend_tree, parser_prolog_tree)` returns true.

---

## Cross-pollination

All six PARSER-* parsers share `Compiland`/`Shift`/`Reduce`/`Push`/`Pop`/`Top`/
`tree`/`TDump`/`stack` plus the `nPush`/`nInc`/`nTop`/`nPop` counter helpers
from `corpus/programs/scrip/`. Bug fixes there benefit all six.

Prolog is the most syntactically distinct of the six — clauses (`head :-
body.`), facts (`fact.`), terms with arity. The Compiland spine is identical
across all PARSER-*.

---

## Naming policy — anchor on existing frontend

⛔ Non-terminal and token names in `parser_prolog.sc` MUST match the
existing Prolog frontend's vocabulary, not be invented.

- **Tokens** — from `src/frontend/prolog/prolog_lex.h`: `TK_ATOM`, `TK_VAR`,
  `TK_ANON`, `TK_INT`, `TK_FLOAT`, `TK_STRING`, `TK_LPAREN`, `TK_RPAREN`,
  `TK_LBRACKET`, `TK_RBRACKET`, `TK_PIPE`, `TK_COMMA`, `TK_DOT`, `TK_LBRACE`,
  `TK_RBRACE`, `TK_OP`, `TK_NECK`, `TK_QUERY`, `TK_CUT`, `TK_SEMI`.
- **Non-terminals** — from `src/frontend/prolog/prolog_parse.c`: `clause`,
  `term`, `primary`, `args`, `list`.
- **IR node tags** — from `prolog_lower.c::expr_dump`: `E_CHOICE`, `E_CLAUSE`,
  `E_UNIFY`, `E_CUT`, `E_FNC`, `E_QLIT`, `E_ILIT`, `E_FLIT`, `E_VAR`, `E_ADD`,
  `E_SUB`, `E_MUL`, `E_DIV`.

Cross-PARSER spine names (`Compiland`, `Push`/`Pop`/`Top`, `nPush`/`nInc`/
`nTop`/`nPop`) are the only invented names — shared across all six PARSER-*.

See GOAL-PARSER-SNOBOL4.md "Style Guidelines for parser_*.sc" for the full
canonical writeup (binding on all six PARSER-*).

---

## Session Setup

```bash
( cd /home/claude/one4all && git fetch origin parser 2>/dev/null; git checkout parser 2>/dev/null || git checkout -b parser origin/parser 2>/dev/null || git checkout -b parser )
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
```

Gate after setup:
```bash
bash /home/claude/one4all/scripts/test_smoke_prolog.sh         # existing frontend baseline
bash /home/claude/one4all/scripts/test_parser_prolog.sh        # parser gate
```

---

## Architecture

```
scrip --parser-crosscheck parser_prolog.sc tiny.pl
```

SCRIP runs `parser_prolog.sc` (which `-include`s the shared SC library from
`corpus/programs/scrip/`) against `tiny.pl`. PAT produces IR tree t2 via
`Compiland`; the existing frontend produces t1. Compared in memory
(`tree_equal`), executed in memory.

**Shared SC library** (`corpus/programs/scrip/`):
```
tree.sc  stack.sc  counter.sc  ShiftReduce.sc  semantic.sc
```

Compiland spine (uses the counter helpers — `nPush` opens a counter frame,
`nInc` bumps the count, `nTop` reads it, `nPop` closes the frame):
```
Compiland = nPush() ARBNO(*Command) reduce('Parse', 'nTop()') nPop();
```

Prolog-specific: PAT-PR's `Command` reduces to a `Clause` node (fact or
rule); program tree is `(Parse (Clause ...) (Clause ...) ...)`.

---

## Style guide for parser_*.sc — derived from beauty.sno / beauty.sc

These rules apply to every `parser_<lang>.sc` file.  They are derived by
reading `corpus/programs/snobol4/demo/beauty/beauty.sno` and its Snocone
translation `corpus/programs/snocone/demo/beauty/beauty.sc` as the canonical
style reference.  When a rule below is silent on a point, defer to beauty.

### Whitespace tokens — Gray / White, $'x' idiom

Define `Gray` (optional whitespace) and `White` (required whitespace) near the
top of the pattern section, exactly as beauty does.  Every token pattern that
can be preceded or followed by whitespace uses `Gray` or `White` rather than
inline `SPAN(' ' tab)`.  The token patterns themselves are *pure character
class matchers*; whitespace attachment is a caller-level concern.

Token patterns named with the `$'x'` idiom carry their own surrounding
whitespace.  Operators and punctuation are given `$'...'` names:

```snocon
$'='  = *White '='  *White;    // binary operator — required ws both sides
$':'  = *Gray  ':'  *Gray;     // punctuation — optional ws both sides
$'('  = '(' *Gray;             // open bracket — optional ws after only
$')'  = *Gray ')';             // close bracket — optional ws before only
```

The grammar body references `$'='`, `$':-'`, `$'('`, `$','`, etc. directly.
It never repeats `ws_opt` or `SPAN(' ' tab)` inline inside the grammar; all
whitespace absorption is hidden inside the `$'x'` tokens and `Gray`/`White`.

Word-token names that are not Snocone reserved words use plain identifiers:
`Atom`, `Var`, `Int`, `Str`, `F` (float), etc.  Snocone reserved words that
happen to be token names are escaped with the `$'word'` idiom: `$'is'`,
`$'not'`, `$'if'` — exactly as beauty uses `$'='`, `$'**'`.

Optional-whitespace shorthand: `$' '` = `*Gray` (a single space in the name
signals "optional").  Required-whitespace shorthand: `$'  '` = `*White` (two
spaces signal "required").  These two patterns need not be defined unless the
style is copied from beauty exactly; what matters is that all whitespace is
named and named consistently.

### Shift / Reduce calling convention

The primitive pattern + capture + action idiom has two equivalent spellings;
always use the **short form**:

```snocone
// Long form (beauty.sno SNOBOL4 only):
primitive . tx  epsilon . *Shift(tag, tx)

// Short form (beauty.sc and all parser_*.sc):
primitive ~ "tx"          // shift — binds matched text, emits leaf node
(tag & n)                 // reduce — pops n trees, builds parent node
```

`shift(pat, tag)` and `reduce(tag, n)` are the OPSYN-bound names from
`semantic.sc`.  The grammar body uses these directly; never spell out the
underlying `epsilon . *` boilerplate.  The beauty.sc grammar section is the
reference for what the calling-convention looks like in practice:

```snocone
Expr0 = *Expr1 FENCE($'=' *Expr0 reduce('=', 2) | epsilon);
Expr17 = FENCE(
             shift(*Function, 'Function') $'(' *ExprList $')' reduce('Call', 2)
           | shift(*Id, 'Id')
           | shift(*Integer, 'Integer')
           | ...
         );
```

The `nPush()` / `nInc()` / `nTop()` / `nPop()` counter helpers delineate
sub-repetition counts for n-ary tree children.  `nInc()` is embedded *inside*
the repeated arm, not as a trailing side-effect:

```snocone
ExprList = nPush() *XList reduce('ExprList', '*(GT(nTop(), 1) nTop())') nPop();
XList    = nInc() (*Expr | epsilon . '') FENCE($',' *XList | epsilon);
```

`reduce(tag, expr)` where `expr` is a quoted Snocone expression (not a plain
integer) is evaluated at reduce time via `EVAL`; this is how `nTop()` is read
as the arity of an n-ary node.

### Names — tokens, productions, functions, variables

| Kind | Rule | Example |
|------|------|---------|
| Token patterns | Mirror the official language spec and the existing frontend's `TK_*` enum, lowercased, no leading underscore | `Atom`, `Var`, `Int`, `Neck`, `Dot` |
| Operator / punctuation tokens | `$'symbol'` idiom | `$':-'`, `$','`, `$'('`, `$'|'` |
| Grammar productions | Mirror the official BNF non-terminal names and the existing frontend's parse-function names | `clause`, `term`, `primary`, `args`, `list` |
| Semantic / tree-builder functions | Upper_Snake_Case (first letter upper, rest snake) | `Shift`, `Reduce`, `Build_clause`, `Reduce_list` |
| Local variables inside functions | lower_snake_case | `head_name`, `body_tree`, `kids`, `i` |
| Cross-PARSER spine names | As specified: `Compiland`, `Push`/`Pop`/`Top`, `nPush`/`nInc`/`nTop`/`nPop` | — |

⛔ No identifier begins with `_`; that prefix is reserved for generated code.
⛔ No CamelCase (neither `headName` nor `HeadName`); use `head_name` /
   `Head_name` depending on kind.

### Section separators — `/*===*/` and `/*---*/` at column 120

Separate major sections with a `/*====...*/` banner (120 chars).
Separate sub-sections with a `/*----...*/` banner (120 chars).
Do *not* use blank lines between logical blocks; use the banner lines.

```snocone
/*========================================... (120 chars) ...=====*/
// Token classifiers
/*----------------------------------------... (120 chars) ...-----*/
```

### Horizontal space — 120-column maximum, 2-space indent for wraps

- Use horizontal space maximally; pack related assignments on one line where
  they fit: `$'=' = *White '=' *White;  $'|' = *White '|' *White;`
- When a pattern definition or expression exceeds 120 columns, wrap with
  **2-space continuation indent**, aligning open parens/brackets vertically:

```snocone
Expr6 = *Expr7
          FENCE(
            $'+' *Expr6 reduce('+', 2)
          | $'-' *Expr6 reduce('-', 2)
          | epsilon
          );
```

Binary operators (`|`, concatenation) go at the *start* of the continued line,
not the end.

### Control flow — structured only, no goto except where beauty uses goto

⛔ No `goto` / labels in driver loops or grammar helper code.  Use `while`,
`if`/`else`, `for`.  The legacy `goto` shape in `parser_snobol4.sc` is
grandfathered; new files do not copy it.

⛔ No single-statement curly-brace blocks.  Write `statement ;` instead of
`{ statement }`:

```snocone
// Wrong:
if (IDENT(x)) { return; }
// Correct (one statement):
if (IDENT(x)) return;
// Correct (multi-statement — braces OK):
if (DIFFER(t)) {
  kids[i] = Pop();
  i = i - 1;
}
```

### Grammar body — no inline whitespace, all whitespace in named tokens

The grammar pattern body reads like a clean BNF: only non-terminal references,
`$'x'` operator tokens, `shift(...)`, `reduce(...)`, `nPush`/`nInc`/`nPop`,
and `FENCE`/`ARBNO`/`epsilon`.  Whitespace handling is 100% encapsulated in
the `$'x'` token definitions and `Gray`/`White`; it does not appear inline in
grammar rules.

### No PR_* builder-function layer

The `PR_xxx()` pattern-builder indirection layer used in `parser_prolog.sc`
(rung PR-0..PR-6) is superseded by the direct `shift(...)` / `reduce(...)`
calling convention shown in beauty.  When rewriting or extending parser files,
remove `PR_*` builders and replace call sites with the direct `shift`/`reduce`
form.  Tree-builder functions that cannot be expressed as a plain `reduce(tag,
n)` (e.g. `Build_clause`, `Reduce_list`) are called via the `epsilon . *fn()`
mechanism — but that mechanism is still hidden inside the named function call
form `Fn_name()` placed inline in the grammar, not via a factory wrapper.

---

## Rung ladder

### PARSER-PR-0 — atom — **LANDED** (PASS=4)
Atoms, vars, ints, quoted strings followed by `.`.

### PARSER-PR-1 — facts — **LANDED** (PASS=11)
Bare facts and compound facts `f(a, b, c).`.

### PARSER-PR-2 — rules — **LANDED** (PASS=18)
Rules `head :- goal.` with single goal in body. Two-phase build
(`snapshot_head` + `mark_body` + `build_clause`); E_CHOICE/E_CLAUSE key
is head arity alone.

### PARSER-PR-3 — conjunction / disjunction (`,` / `;`) — **LANDED** (PASS=24)

- [x] `Command` handles `a, b, c` and `a ; b` in goal position.
- **Sibling LANG rungs:** PR-10..PR-12.
- **Gate:** PASS≥24. ✅

#### Oracle IR shapes (verified via `--dump-ir`)

| Source | IR shape |
|---|---|
| `foo :- a, b.` | `(E_CLAUSE foo/0 (E_FNC a) (E_FNC b))` — top-level `,` flattened |
| `foo :- a ; b.` | `(E_CLAUSE foo/0 (E_FNC ; (E_FNC a) (E_FNC b)))` — `;` wrapped, flat n-ary |
| `foo :- a, b ; c.` | `(E_CLAUSE foo/0 (E_FNC ; (E_FNC , (E_FNC a) (E_FNC b)) (E_FNC c)))` — nested `,` preserved |
| `foo :- a ; b ; c.` | `(E_CLAUSE foo/0 (E_FNC ; (E_FNC a) (E_FNC b) (E_FNC c)))` — flat n-ary `;` |
| `foo :- a, b, c, d.` | `(E_CLAUSE foo/0 (E_FNC a) (E_FNC b) (E_FNC c) (E_FNC d))` |

Three flattening rules (match prolog_parse.c::flatten_conj and
prolog_lower.c right-spine flattening):
1. **Top-level `,` in body**: flattened away into separate E_CLAUSE children.
2. **Inner `,` (nested in `;` or non-top)**: preserved as flat n-ary `(E_FNC ,)`.
3. **`;` always**: preserved as flat n-ary `(E_FNC ;)`.

Precedence: `,` (1000) tighter than `;` (1100). Grammar:
```
body := disj
disj := conj (';' ws_opt conj)*
conj := simple_goal (',' ws_opt simple_goal)*
simple_goal := tk_atom '(' args ')'  |  tk_atom
```

#### Test fixtures committed

`conj_two.pl`, `conj_three.pl`, `disj_two.pl`, `disj_three.pl`,
`conj_in_disj.pl`, `disj_compound.pl` in `corpus/programs/prolog/parser/`.
All have verified oracle output.

#### Critical Snocone gotchas (sessions ending 2026-05-03)

⚠️ **`*func()` immediate evaluations inside ARBNO arms only fire on the
FIRST iteration in `--ir-run` mode.** Verified empirically:
`ARBNO( ws_opt tk_comma ws_opt simple_goal . *inc_body_count() )` — the
ARBNO correctly iterates and `simple_goal` pushes goals to the stack on
every iteration, but `*inc_body_count()` only fires once. The cursor
advances correctly (so the ARBNO loops), but the standalone post-match
side effect is skipped.

This rules out the accumulator-counter pattern that works fine outside
ARBNO. **The fix is to use the cross-PARSER spine's `nPush`/`nInc`/`nTop`/
`nPop` counter helpers** — these are designed specifically for "count what
I just pushed" inside ARBNO, used in `Compiland` itself. The mechanism is
already available; PR-3 just needs to use it. See how `Compiland` uses
`nPush()` / `ARBNO(nInc() ...)` / `reduce('...', 'nTop()')` / `nPop()`:
that is the canonical "count goals in ARBNO and read the count after"
pattern, and the answer for PR-3 conj/disj building.

⚠️ **`if (var)` where `var = 0` is TRUTHY in Snocone** — integer `0`
converts to string `"0"` which is non-null. Use `if (GT(var, 0))` or
`if (IDENT(var, 1))` for explicit comparisons. The `body_present`
flag used `if (body_present)` which silently appended a phantom child
on facts. Fixed via `if (GT(body_present, 0))` in `build_clause`.

⚠️ **Snocone boolean AND in `if (...)` is juxtaposition**, NOT `&` or `&&`.
Use `if (IDENT(t(x), 'E_FNC') IDENT(v(x), ','))`.

⚠️ **Pop() with no parameter** returns the popped value (function return).
`g = Pop()` works as expected. But calling `Pop()` from inside a
`*func()` immediate evaluation in an ARBNO arm runs into the same
"only fires once" problem above.

#### Recommended PR-3 strategy for next session

1. **Use `nPush`/`nInc`/`nTop`/`nPop` counter helpers** — same mechanism
   as `Compiland`. Open a frame for the body before the first `simple_goal`,
   `nInc()` per goal (placed where `simple_goal` is in the spine, NOT as
   a `*func()` after it), `nTop()` to read the count, `nPop()` to close.
   This is the documented spine pattern and avoids the ARBNO-`*func()` bug.
2. **Validate after each `str_replace`** with
   `bash /home/claude/one4all/scripts/test_parser_prolog.sh | tail -3` —
   PR-2 baseline must remain PASS=18 throughout.
3. **`build_clause` already has correct flatten logic** for top-level
   `(E_FNC ,)` — the upgrade landed cleanly during the 2026-05-03 session.
   Re-apply it (was reverted with rest of file). The `if (GT(body_present,
   0))` fix needs re-applying too.
4. **Add `disj` after `conj` works** — same nPush/nInc/nTop/nPop pattern,
   building `(E_FNC ;)` instead of `(E_FNC ,)`.
5. **Defer parenthesized body subterms** (`(a, b) ; c`), nested compound
   args, anon vars, arithmetic to later rungs.

### PARSER-PR-4 — lists (`[H|T]` / `[a,b,c]`) — **LANDED** (PASS=31)

- [x] `[]` empty list, `[a, b, c]` flat list, `[H|T]` head/tail, nested lists.
- **Gate:** PASS≥30. ✅
- **Fixtures:** list_empty, list_one, list_three, list_var, list_pipe,
  list_pipe_two, list_nested.
- **Notes:** Lists are right-spined cons cells using functor `.` (the
  Prolog list-cell convention) terminated by `(E_FNC [])`. Mutual
  recursion list ↔ arg via the `list_elem` indirection (literal
  alternation copy of arg's body) — dodges the FW-3 scrip-Snocone bug
  where `*Q` indirection inside ARBNO suppresses deferred calls in Q.

### PARSER-PR-5 — arithmetic (`is`, builtin operators) — **LANDED** (PASS=42)

- [x] `+ - * /` left-associative arith ladder.
- [x] `is` body operator → `(E_FNC is L R)` named compound.
- [x] `=` unification → `(E_UNIFY L R)` kind-only.
- [x] Parens for precedence override.
- [x] Negative integer literals (`-N` folds into `(E_ILIT -N)`).
- **Bonus:** nested compound args (`foo(bar(a))`) handled by primary
  recursion (`primary` absorbed both `arg` and `simple_goal`).
- **Gate:** PASS≥38. ✅ (PASS=42, exceeded by 4)
- **Fixtures:** arith_is_int, arith_is_add, arith_is_chain, arith_is_paren,
  arith_is_subleft, arith_is_var, arith_unify, arith_unify_expr,
  arith_neg_int, plus bonus compound_nested, compound_nested_two.
- **Notes:** Expression ladder `primary < mul_expr < add_expr < is_expr <
  unify_expr` mirrors prolog_parse.c precedence.  `=` and arith use the
  OPSYN-bound `reduce(r_KIND, 2)` directly (kind-only n-ary trees).
  `is` uses `*reduce_is()` semantic helper because it builds a named
  E_FNC compound (`Reduce()` forces empty value).  Args (compound calls
  + list elements) use TAIL-RECURSION via `*args_tail` instead of
  ARBNO, because `*unify_expr` (forward ref into the ladder) cannot
  appear inside ARBNO without triggering FW-3 (deferred actions inside
  the deferred Q get suppressed).

### PARSER-PR-6 — queries / directives — **LANDED** (PASS=48)

- [x] Top-level directive `:- Goal.` produces `(STMT :subj <body>)`
      directly — no `E_CHOICE`/`E_CLAUSE` wrap, no top-level `,`
      flattening, body raw under `:subj`.
- [x] Per-directive variable scope reset (matches per-clause behavior).
- [x] Mixed directive + clause files produce one STMT per top-level form.
- **Gate:** PASS≥45. ✅ (PASS=48, exceeded by 3)
- **Fixtures:** dir_atom, dir_compound, dir_conj, dir_disj, dir_arith,
  dir_with_clause.
- **Notes:** No separate `?-` query syntax — the existing Prolog
  frontend rejects it, so PARSER-PR mirrors that.  New tree-builder
  semantic `build_directive` pops one body tree and pushes the
  `(STMT :subj <body>)` envelope.  Compiland's ARBNO body widened from
  `clause` to `top_form = (directive | clause)`.

---

## Invariants

- Prolog's LANG ladder is at PR-17 active; PAT-PR does not race ahead.
- Test programs in `corpus/programs/prolog/parser/` are owned by PAT-PR.
- `.ref` files captured at rung-land time.
- Variables vs atoms distinction is first-class in the token classifier.

---

### PARSER-PR-7 — style conformance to beauty.sno / beauty.sc — ⏳ NEXT

`parser_prolog.sc` was written before the canonical style guide was written
down (PR-0..PR-6 predate the guide).  Audit performed 2026-05-04 against
`## Style guide for parser_*.sc` finds the following gaps.  These are
guidelines, not laws — land each as its own micro-rung with the gate held
at PASS=48 throughout.  PASS may rise as rules become more uniform.

#### Audit findings — 7 violations to address

| # | Guideline | Current state in `parser_prolog.sc` | Target |
|---|-----------|-------------------------------------|--------|
| 1 | `Gray` / `White` named whitespace | `ws_one` / `ws_run` / `ws_opt` invented locally; no `Gray` / `White` defined | Define `Gray = *White \| epsilon;` and `White = SPAN(' ' tab nl);` (Prolog has no continuation lines, so no nl-`+` glue).  Retire `ws_*`. |
| 2 | `$'x'` idiom for operator / punctuation tokens | `tk_lparen`, `tk_rparen`, `tk_comma`, `tk_semi`, `tk_dot`, `tk_neck`, `tk_pipe`, `tk_lbracket`, `tk_rbracket`, `op_eq`, `op_pls`, `op_mns`, `op_mul`, `op_div`, `op_is` — all use `tk_*` / `op_*` invented prefixes; whitespace is glued inline at use sites | Rename to `$'('`, `$')'`, `$','`, `$';'`, `$'.'`, `$':-'`, `$'\|'`, `$'['`, `$']'`, `$'='`, `$'+'`, `$'-'`, `$'*'`, `$'/'`, `$'is'`.  Each carries its own `*Gray` / `*White` per the Gray/White rules in the style guide. |
| 3 | No inline `ws_opt` / `SPAN` in grammar body | Grammar arms repeat `ws_opt tk_comma ws_opt`, `ws_opt tk_rbracket`, `ws_opt tk_pipe ws_opt`, etc. | After (2) lands, all whitespace is inside the `$'x'` tokens; grammar reads as clean BNF with zero inline `ws_opt`. |
| 4 | Names mirror the existing frontend's `TK_*` enum | `tk_atom`, `tk_var`, `tk_int`, `tk_string`, `tk_qatom` — closer to `TK_*` than to BNF, but inconsistent (lowercased + `tk_` prefix invented) | Rename token classifiers per the style-guide names table: `Atom`, `Var`, `Int`, `Str`, `Qatom` (or `Qstr`).  Mirror `prolog_lex.h` `TK_ATOM`/`TK_VAR`/`TK_INT`/`TK_STRING` semantically but drop the `tk_` prefix per "plain identifiers for non-reserved word tokens". |
| 5 | Builder functions = `Upper_Snake_Case`; locals = `lower_snake_case`; no `_` prefix | All 14 runtime fns are correct (`push_var`, `reduce_compound`, `build_clause`).  All 14 PR_* builders use `PR_` prefix (`PR_push_var`, `PR_reduce_compound`).  Capture vars use camelCase (`pText`, `qBody`, `leText`, `pNegi`, `pName`, `hText`) to dodge the EVAL underscore-lex bug | Two changes: (a) Rename runtime fns to `Upper_Snake` per style guide (`push_var` → `Push_var`, `reduce_compound` → `Reduce_compound`).  (b) Eliminate the `PR_*` layer entirely (item 7 below) — once gone, capture vars no longer flow through EVAL and can revert to plain `lower_snake_case` (`p_text`, `q_body`, `le_text`, `p_negi`, `p_name`, `h_text`). |
| 6 | Section separators `/*===*/` and `/*---*/` at column 120 | File uses `//-----...---` (78-col, double-slash form) and blank lines between blocks | Rewrite separators as 120-col `/*======...=====*/` for major sections and `/*------...-----*/` for sub-sections; remove blank lines that the separators replace. |
| 7 | No `PR_*` pattern-builder layer | 14 `PR_xxx()` builders with EVAL-spliced capture-var names (the entire post-PR-6 "beauty pass") | Remove all `PR_*` builders.  Replace each call site with the direct equivalent.  Two cases: (a) Side-effect builders that just wrap `epsilon . *fn()` with no args (e.g. `PR_push_nil()`, `PR_reduce_conj()`, `PR_mark_body()`) → callsite becomes `epsilon . *Push_nil()`.  (b) Side-effect builders that EVAL-splice a capture name (`PR_push_var('pText')`) → callsite becomes `. *Push_var(p_text)` using the standard SNOBOL4 capture+action idiom (since the capture var name is now lexically present at the action site, not splice-substituted). |

#### Strategy

- **Land items in order 6 → 1 → 2 → 3 → 4 → 5 → 7.**  Order matters:
  separators (6) is cosmetic-only and can land first as a warm-up; (1)+(2)
  are token-layer changes that must land together to avoid an intermediate
  grammar-half-uses-Gray state; (7) is the biggest rewrite and goes last.
- **Hold PASS=48 FAIL=0 after every micro-rung.**  Run
  `bash /home/claude/one4all/scripts/test_parser_prolog.sh | tail -3` after
  every `str_replace`.
- **No semantic change.**  Output IR trees must be byte-identical to current
  for every fixture.  This is pure refactoring.
- **Use git diff to verify diff size per micro-rung.**  Items 6, 4, 5a, 7
  should be search-and-replace style diffs.  Items 1, 2, 3 land together
  and are the largest single diff.

#### Caveats — guidelines, not laws

- The PR-3 watermark documents an empirical bug: `*func()` immediate
  evaluations inside `ARBNO` arms only fire on the first iteration.  If
  removing the `PR_*` layer (item 7) re-exposes that bug — i.e. a callsite
  that worked through a `PR_*` builder breaks when written direct — leave a
  `PR_*` builder in place for that one callsite and document it inline.
  The bug is the binding constraint, not the style.
- The capture-var rename (item 5b) depends on item 7 landing first.  If
  item 7 stalls on the ARBNO bug above, leave the camelCase capture-var
  names alone — they exist for a real reason.
- `Compiland`, `Push`/`Pop`/`Top`, `nPush`/`nInc`/`nTop`/`nPop` are
  cross-PARSER spine names and stay as-is.

#### Steps

- [ ] **PR-7-6**  Rewrite section separators to 120-col `/*===*/` / `/*---*/`; remove blank-line spacers.  Gate: PASS=48 FAIL=0.
- [ ] **PR-7-1**  Define `Gray` and `White`; retire `ws_one` / `ws_run` / `ws_opt`.  Gate: PASS=48 FAIL=0.
- [ ] **PR-7-2**  Convert `tk_*` punctuation + `op_*` operators to `$'x'` form, embedding `*Gray` / `*White` per style guide.  Gate: PASS=48 FAIL=0.
- [ ] **PR-7-3**  Remove all inline `ws_opt` / `ws_run` from grammar body (should follow naturally from PR-7-2).  Gate: PASS=48 FAIL=0.
- [ ] **PR-7-4**  Rename `tk_atom` → `Atom`, `tk_var` → `Var`, `tk_int` → `Int`, `tk_string` → `Str`, `tk_qatom` → `Qatom`.  Gate: PASS=48 FAIL=0.
- [ ] **PR-7-5a** Rename runtime fns to `Upper_Snake_Case` (`push_var` → `Push_var`, etc.).  Gate: PASS=48 FAIL=0.
- [ ] **PR-7-7**  Remove all `PR_*` pattern-builder fns; replace call sites with direct `epsilon . *Fn()` / `. *Fn(var)` forms.  Watch for the ARBNO `*func()` bug — if a callsite breaks, restore that one builder and note inline.  Gate: PASS=48 FAIL=0.
- [ ] **PR-7-5b** (Conditional on PR-7-7 success.) Rename camelCase capture vars (`pText`, `qBody`, `leText`, `pNegi`, `pName`, `hText`) to `lower_snake_case` (`p_text`, `q_body`, `le_text`, `p_negi`, `p_name`, `h_text`).  Gate: PASS=48 FAIL=0.

---

## Watermark

PARSER-PR-6 LANDED (PASS=48).  All ladder rungs PR-0..PR-6 landed.

**Beauty pass (post-PR-6):** 14 `PR_*` pattern-builder fns added
following beauty.sno semantic.inc::shift / reduce convention; 56
inline `[. *]xxx(...)` callsites in the grammar replaced with
`PR_xxx(...)` builder calls.  Capture vars renamed from `_pName`
style to camelCase (pText, qBody, leText, sBody, pNegi, pName, hText)
because scrip-Snocone EVAL cannot lex underscore-leading identifiers
inside the EVAL'd pattern body.  Direct `.name` calling convention is
documented inline as an alternative for cases where the runtime fn
wants a NAME (none of ours do).  Gate unchanged: PASS=48 FAIL=0.

Next: PARSER-PR-7 rung — style conformance to the canonical
`parser_*.sc` style guide (added 2026-05-04 from beauty.sno / beauty.sc).
Eight micro-rungs PR-7-1..PR-7-7-5b documented above.  Feature rungs
(same-functor E_CHOICE merging, anonymous variables `_`, parenthesized
body subterms, DCG sugar) deferred until PR-7 lands.

**Next session:** start with PR-7-6 (cosmetic separators, low risk) as warm-up,
then proceed in the documented order.  Hold PASS=48 FAIL=0 after every
micro-rung.
