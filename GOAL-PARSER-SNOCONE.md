# GOAL-PARSER-SNOCONE.md — PARSER-SNOCONE pattern-based frontend in Snocone

**Repo:** corpus+one4all
**Branch:** `parser` (one4all only — `corpus` and `.github` stay on `main`)
**Sibling ladder:** `GOAL-LANG-SNOCONE.md` and `GOAL-SNOCONE-IN-SNOCONE.md`.
The existing Snocone frontend (`src/frontend/snocone/`) is the in-process oracle.

**Done when:** A Snocone program `parser_snocone.sc` reads Snocone source,
runs one `Compiland` PATTERN that builds the canonical IR tree (same shape
SM-LOWER consumes), and for every test program in the rung corpus
`tree_equal(existing_frontend_tree, parser_snocone_tree)` returns true.
Where a `.ref` file exists, executing both trees through the IR interpreter
produces byte-identical output.

> **Cross-pollination (session #62):** D1 (no goto/label loops),
> D2 (names mirror the existing frontend), D3 (drive from a checked-in BNF
> in `corpus/programs/ebnf/`). See `GOAL-PARSER-ICON.md ## Design issues`
> for the canonical writeup. PARSER-SC-INFRA-2 is the SC instantiation.
>
> **D4 added this session:** beauty.sno style — `Gray`/`White` baked into
> `$'tok'` token globals (grammar never references whitespace directly);
> language keywords as `$'kw'`, non-keyword word-tokens as plain idents
> (`S = $' ' 'S'`); `$' '`/`$'  '` invisible whitespace tokens; Shift via
> `~` and Reduce via `&` OPSYN; `nPush()`/`nInc()`/`nTop()`/`nPop()` for
> n-ary trees; `E_*` IR tags; no leading underscores in user code; no `{
> }` around single-statement bodies; 120-char `/*===*/` and `/*---*/`
> dividers instead of blank lines; horizontal-dense, vertically-balanced
> wrapping. See `## Naming & Design Principles ### 5. beauty.sno style
> (D4)` below for the full rules. Applies to every `parser_<lang>.sc`.

---

## Cross-pollination

All six PARSER-* parsers share `Compiland`/`Shift`/`Reduce`/`Push`/`Pop`/`Top`/
`tree`/`TDump`/`stack` from `corpus/programs/snocone/demo/beauty/`. Bug fixes
there benefit all six. PARSER-SNOCONE is the most reflexive: a Snocone program
parsing Snocone using the same pattern primitives Snocone provides. Coupled to
`GOAL-SNOCONE-IN-SNOCONE` long-term: when both rungs near completion the
bootstrap cycle closes.

---

## Session Setup

```bash
( cd /home/claude/one4all && git fetch origin parser 2>/dev/null; \
  git checkout parser 2>/dev/null || git checkout -b parser origin/parser 2>/dev/null || git checkout -b parser )
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
```

Gate after setup:
```bash
bash /home/claude/one4all/scripts/test_smoke_snocone.sh        # existing frontend baseline
bash /home/claude/one4all/scripts/test_parser_snocone.sh       # this goal's gate
```

---

## Architecture reminder

```
scrip --parser-crosscheck parser_snocone.sc tiny.sc
```

SCRIP runs `parser_snocone.sc` (which `-include`s the shared SC library from
`corpus/programs/scrip/`) against `tiny.sc` — PAT produces IR tree t2 via
`Compiland`; the existing Snocone frontend produces t1. Both compared in
memory (`tree_equal`), both executed in memory. No subprocesses, no temp
files, no on-disk diffs.

**Shared SC library** (`corpus/programs/scrip/`):
```
tree.sc  stack.sc  counter.sc  ShiftReduce.sc  semantic.sc  gen.sc  tdump.sc
```

Compiland spine (identical across all six):
```
Compiland = nPush() ARBNO(*Command) reduce('Parse', 'nTop()') nPop();
```

Snocone-specific note: the existing Snocone frontend already lowers to LANG_SNO
IR via `snocone_lower.c`. PARSER-SC must produce the same post-lowering shape,
OR a pre-lowering tree the existing pipeline can consume — Lon decides per rung.

---

## Snocone language reference (atom slice)

| Construct | Tree shape |
|-----------|------------|
| identifier `x` | `Name x` |
| integer `42` | `integer 42` |
| string `"hi"` | `string 'hi'` |
| `x = expr;` | `(Stmt (Assign Name(x) ...))` |
| `function f(a,b) { ... }` | `(Function f (Params a b) Body)` |
| `if (c) { ... } else { ... }` | `(If c Then Else)` |
| `while (c) { ... }` | `(While c Body)` |
| `expr ? pat` | `(Match expr pat)` |

Full feature surface in `GOAL-LANG-SNOCONE.md`.

---

## Naming & Design Principles (D1/D2/D3/D4)

> **Cross-PARSER-* style is canonical in
> `GOAL-PARSER-SNOBOL4.md ## Style Guidelines for parser_*.sc`.**
> That section covers naming, `White`/`Gray`, `$'name'` tokens,
> shift/reduce, n-ary counters, `E_*` IR tags, identifier rules,
> and 120-col layout — binding on every PARSER-*.  The
> Snocone-specific D1/D2/D3 detail below extends it; read
> the canonical writeup first.

> **Canonical style guide:** `GOAL-PARSER-PROLOG.md § Style guide for parser_*.sc`.
> The full beauty.sno / beauty.sc–derived style rules (whitespace tokens,
> Gray/White/$'x' idiom, shift/reduce calling convention, naming, section
> separators, horizontal layout, structured control flow, no PR_* layer) live
> there and apply to all six `parser_<lang>.sc` files.  The sections below
> supplement with Snocone-specific design decisions (D1/D2/D3).

### 1. Names from the official BNF (D2/D3)

`src/frontend/snocone/snocone_parse.y` is the canonical grammar. Pattern-variable
names in the parser MUST mirror its expression-tier ladder:

```
expr0   assignment        (= += -= *= /= ^=)         → E_ASSIGN
expr1   pattern match     (?)                         → E_SCAN
expr3   pattern alt       (|, n-ary fold)             → E_ALT
expr4   concat            (juxtaposition, n-ary fold) → E_SEQ
expr5   comparison        (EQ NE LT GT LE GE LEQ ...) → E_FNC "EQ"...
expr6   additive          (+ -)                       → E_ADD / E_SUB
expr9   multiplicative    (* /)                       → E_MUL / E_DIV
expr11  exponent          (^, right-assoc)            → E_POW
expr12  pattern-bind      (binary . and $)            → E_CAPT_*
expr15  subscript         ([ ])                       → E_INDEX
expr17  atoms             (id, int, str, real, call)
```

`simple_stmt : expr0 T_SEMICOLON` — assignment is an `expr0`-level operator,
NOT statement-level. `sc_append_stmt` decomposes the top `E_ASSIGN(lhs, rhs)`
into `STMT { :eq=true, :subj=lhs, :repl=rhs }` post-parse
(`snocone_parse.y` line 1283).

### 2. Names from beauty.sc when concept matches (D2)

`corpus/programs/snocone/demo/beauty/beauty.sc` is the canonical Snocone self-host
pretty-printer; its `Expr0..Expr17` use `shift()`/`reduce()` from `ShiftReduce.sc`.
PARSER-SC reuses these names exactly.

```
Expr0 = *Expr1 FENCE($'=' *Expr0 reduce('=', 2) | epsilon);
Expr4 = nPush() *X4 reduce('..', '*(GT(nTop(), 1) nTop())') nPop();
X4    = nInc() *Expr5 FENCE(*White *X4 | epsilon);
Expr6 = *Expr7 FENCE($'+' *Expr6 reduce('+', 2) | $'-' *Expr6 reduce('-', 2) | epsilon);
Expr17 = ... shift(*Id, 'Id') | shift(*Integer, 'Integer') | shift(*String, 'String') ...
```

`$'='` accesses the variable named `=` (a pattern matching `=` surrounded by
optional whitespace) — embedding the pattern at build time, no runtime
indirection.

### 3. Use shift/reduce primitives, not manual Push(Tree(...))

`ShiftReduce.sc` provides `shift(*pat, type)` and `reduce(type, n)`. Hand-rolled
`Push(Tree(...))` inside pattern escapes generates synthetic labels per
call-site which can collide silently across the loaded blob. Don't.

### 4. Driver: top-level `Compiland`, no per-line goto loop (D1)

```
Compiland = nPush() ARBNO(*Command) reduce('Parse', 'nTop()') nPop();
Command   = simple_stmt | if_head | while_head | ... ;
```

### 5. beauty.sno style (D4) — applies to all `parser_*.sc`

`corpus/programs/snobol4/demo/beauty/beauty.sno` and its Snocone twin
`corpus/programs/snocone/demo/beauty/beauty.sc` are the canonical style
references for every `parser_<lang>.sc`.  Read them in full before editing
any frontend parser.  The conventions below are normative — sibling parsers
(`parser_snobol4.sc`, `parser_icon.sc`, `parser_prolog.sc`,
`parser_raku.sc`, `parser_rebus.sc`, `parser_snocone.sc`) all converge on
this shape.

**Whitespace lives in the tokens, not the grammar.**  `Gray = *White |
epsilon` (optional whitespace) and `White` (required whitespace) are
defined once.  Every operator/punctuation token absorbs the surrounding
gray it needs at the *token* definition site, so the grammar productions
that compose those tokens never reference `Gray` or `White` directly.
The grammar reads like clean BNF.

**`$'name'` quoted-name globals — one per token.**  Each operator or
punctuation symbol gets one `$'…'` definition with whitespace baked in:

```
$'='  = *White '=' *White;     // binary op: gray on both sides
$'**' = *White '**' *White;
$','  = *Gray ',' *Gray;
$'('  = '(' *Gray;             // open paren: gray after, none before
$')'  = *Gray ')';              // close paren: gray before, none after
$'if' = *White 'if' *White;    // language keyword
```

For **language reserved words** use `$'kw'` (e.g. `$'if'`, `$'while'`,
`$'function'`, `$'return'`).  For **non-reserved word-tokens** use a
plain identifier:

```
S = $' ' 'S';        // 'S' branch in goto field — leading optional space
F = $' ' 'F';
```

**`$' '` and `$'  '` — invisible whitespace tokens.**  One space inside
the quotes denotes optional whitespace; two spaces denotes required-one
whitespace separator.  Define them once and reuse:

```
$' '  = ws_opt;       // optional whitespace
$'  ' = ws_run;       // one-or-more required whitespace
```

This is the beauty.sno trick taken further — the grammar can read
`$'if' $'(' …` knowing the leading and trailing gray is absorbed by each
token.  No explicit `*Gray` clutter.

**Shift/Reduce shorthand via `~` and `&` OPSYN (`semantic.sc`).**

The longhand action form is

```
primitive . tx epsilon . *fn(literal, tx)
```

which becomes

```
primitive . tx Func(literal, "tx")
```

where `Func` is `Shift` or `Reduce`.  Shorter still — `semantic.sc` ships
`OPSYN('~', 'shift', 2)` and `OPSYN('&', 'reduce', 2)`, so the canonical
forms are:

```
*Id ~ 'Id'                              // Shift
*Function ~ 'Function' $'(' *ExprList $')' ('Call' & 2)
nPush() ARBNO(*Command) ('Parse' & 'nTop()') nPop()    // Reduce-with-EVAL
```

Inside `&`'s second arg, an `EXPRESSION`-typed value (a string returned
by `&`) is `EVAL`-ed at match time — that's how `'nTop()'` and
`'*(GT(nTop(), 1) nTop())'` work as variadic arities.

**n-ary tree assembly via `nPush()` / `nInc()` / `nTop()` / `nPop()`.**
For lists and repetitions of unknown length, push a counter frame, bump
it inside the repeating sub-pattern, reduce with `'nTop()'` (or
`'*(GT(nTop(), 1) nTop())'` for collapse-singleton-to-no-wrapper), pop:

```
ExprList = nPush() *XList ('ExprList' & '*(GT(nTop(), 1) nTop())') nPop();
XList    = nInc()  *Expr (*White *XList | epsilon);
```

**Tree tags use `E_*` from `ir.h` (`EXPR_t`).**  When the parser produces
the canonical IR the existing frontend consumes, the reduce tags are the
exact `E_*` enum names: `E_ASSIGN`, `E_ADD`, `E_SUB`, `E_MUL`, `E_DIV`,
`E_FNC`, `E_VAR`, `E_QLIT`, `E_ILIT`, `E_SCAN`, `E_SEQ`, `E_ALT`, etc.
beauty.sno uses display-friendly tags (`'='`, `'+'`, `'Call'`) because it
produces a pretty-printer tree, not IR.  Frontend parsers that feed
SM-LOWER must produce the IR shape — same skeleton, IR-flavored tags.

**No leading underscores in identifiers.**  Names beginning with `_` are
reserved for compiler-generated symbols (synthesized labels, internal
temporaries).  User-written `parser_<lang>.sc` code uses plain names.
Variables: lower case, snake_case (`tx`, `cur_func_name`, `nbody`).
Functions: leading capital, then snake (`Shift`, `Reduce`, `PushCounter`,
`TDump`, `IncLevel`).  Pattern-builder helpers that assemble action
patterns at build time follow the same scheme as the primitive they
wrap (`SC_finalize_if` builds an action-pattern; `sc_finalize_if` is the
match-time helper it calls — both lowercase-after-prefix is fine but
neither starts with `_`).

**No `{ stmt }` for a single-statement body — use `stmt;`.**

```
if (DIFFER(p))   Push(p);                  // good
if (DIFFER(p)) { Push(p); }                // wrong — no braces for one stmt
while (i = LT(i, n) i + 1)   c[i] = Pop(); // good
```

**No blank lines as section separators.**  Use exactly-120-char comment
rules:

```
/*======================================================================================================================*/
/*                              major section divider                                                                   */
/*======================================================================================================================*/

/*----------------------------------------------------------------------------------------------------------------------*/
/*  minor section divider                                                                                               */
/*----------------------------------------------------------------------------------------------------------------------*/
```

Both rules are exactly 120 characters edge-to-edge (matching the C-code
120-column rule from RULES.md).  Comments adjoin the next code block with
no blank line between them.

**Maximize horizontal density; wrap with 2-space nested indent and
balanced parens / binary operators.**  beauty.sno's tier-ladder rules are
a clinic in this — multi-line wrapping never breaks the visual structure
of `(A | B | C)` or `(left op right)` because the operators line up
column-wise:

```
Real = (  SPAN(digits)
            ('.' FENCE(SPAN(digits) | epsilon) | epsilon)
            ('E' | 'e')
            ('+' | '-' | epsilon)
            SPAN(digits)
       |  SPAN(digits) '.' FENCE(SPAN(digits) | epsilon)
       )
```

**Token / non-terminal names track the official language spec.**  This
is the existing D2/D3 rule restated: token names mirror the lexer's
`TK_*` enum (lowered to language identifier rules); non-terminal names
mirror the parse-grammar names (`expr0`, `simple_stmt`, `func_head`,
`if_head`).  The official BNF is the tiebreaker.  Spine helpers
(`Compiland`, `Command`, `Push`, `Pop`, `Top`, `tree`, `Tree`, `TDump`,
`stack`) are the only invented names — and they are shared across all
six PARSER-* parsers, so they are invented exactly once.

**Read beauty.sno end-to-end before editing any `parser_*.sc`.**  The
guidelines above are a checklist; beauty.sno is the worked example.

---

## Rung ladder

### PARSER-SC-0 — atom — ✅ DONE
### PARSER-SC-1 — assignment — ✅ DONE
### PARSER-SC-INFRA-1 — Gen-based TDump — ✅ DONE
### PARSER-SC-INFRA-2 — canonical Compiland + tier ladder — ✅ DONE
### PARSER-SC-3 — control flow — ✅ DONE (PASS=21, session #65)

(Closed rungs — see git history for landed state.)

### PARSER-SC-INFRA-3 — D4 style cleanup ⏳ NEXT

D4 (beauty.sno style) was added to this goal file in session #65. The
existing `parser_snocone.sc` predates D4 and violates several of its
guidelines.  These are guidelines not laws — the parser produces correct
IR — but bringing it up to D4 makes it a clean reference for the other
PARSER-* sessions and prevents drift in SC-4/SC-5/SC-6.

The audit done in session #65:

| Guideline (D4) | Current state in `parser_snocone.sc` |
|---|---|
| No leading `_` in user identifiers | 8 violations: `_sc_lbl_n`, `_sc_while_ltop`, `_sc_while_lend`, `_sc_do_lcont`, `_sc_do_lend`, `_sc_strbody`, `_kw_rest`, `_parser_sc_done` |
| No `{ stmt; }` for single-statement body | 1 violation: line 383 `while (Line = INPUT) { Src = Src Line nl; }` |
| No blank lines as separators; use 120-char `/*===*/` / `/*---*/` rules | 63 blank lines; current dividers are `//-----` 71-char (not 120) |
| `~` / `&` OPSYN over `shift(…)` / `reduce(…)` longhand | 4 `shift(` + 11 `reduce(` calls; only 2 `~` uses, 0 `&` uses |
| `$' '` / `$'  '` invisible-whitespace tokens defined once and reused | Not defined; grammar uses raw `*Gray` / `*White` / `nl_opt` ad-hoc |

Not violations (D4 explicitly permits the existing scheme):

- `sc_*` lower-case match-time helpers paired with `SC_*` upper-case
  build-time pattern-builder wrappers — D4 §"No leading underscores"
  paragraph names this exact pairing as fine.
- `E_*` IR tags (`E_ASSIGN`, `E_SCAN`, `E_ADD`, …) — already used
  throughout. Good.
- Line widths — zero lines exceed 120 chars. Good.

#### Steps

- [ ] **Step 3a — drop leading underscores.** Rename
  `_sc_lbl_n` → `sc_lbl_n`,
  `_sc_while_ltop` → `sc_while_ltop`,
  `_sc_while_lend` → `sc_while_lend`,
  `_sc_do_lcont` → `sc_do_lcont`,
  `_sc_do_lend` → `sc_do_lend`,
  `_sc_strbody` → `sc_strbody`,
  `_kw_rest` → `kw_rest`,
  `_parser_sc_done` → `parser_sc_done`.
  Verify nothing inside an EVAL string also references the underscored
  forms (the comment block on lines 60-67 explains why some were `_`
  prefixed in the first place; that constraint goes away once the names
  no longer start with `_`).  Re-run gate; expect PASS=21 unchanged.

- [ ] **Step 3b — fix single-stmt `{ }` body.** Line 383:
  `while (Line = INPUT) { Src = Src Line nl; }` →
  `while (Line = INPUT)   Src = Src Line nl;`.  Re-run gate.

- [ ] **Step 3c — replace 71-char `//---` dividers with 120-char comment
  rules.** Major boundaries (token defs, helpers, builders, grammar tier,
  driver) get `/*===*/`; minor sub-boundaries get `/*---*/`. Drop the
  blank lines that currently separate sections — the rule now adjoins
  the next code block directly.  Re-run gate.

- [ ] **Step 3d — convert `shift(p, 't')` longhand to `p ~ 't'` and
  `reduce('t', n)` longhand to `('t' & n)`.** 15 call sites. Verify
  `semantic.sc` is in the runtime blob (it is — `test_parser_snocone.sh`
  loads it). Re-run gate; expect PASS=21 unchanged. The shift/reduce
  *functions* stay (still called by the OPSYN-installed `~`/`&`); only
  the *call form at the grammar* sites changes.

- [ ] **Step 3e — define `$' '` / `$'  '` once; sweep grammar.** Add at
  the top of the token-defs block:
  ```
  $' '  = *Gray;       // optional whitespace
  $'  ' = *White;      // required whitespace
  ```
  Then sweep the grammar replacing inline `*Gray` and `*White` with
  `$' '` and `$'  '` at composition sites. Token definitions themselves
  still use `*Gray` / `*White` directly (the `$' '` definition is itself
  `*Gray`, so re-using it inside `$'='` would be a self-reference).
  Re-run gate.

- **Sibling LANG rungs:** none — pure style.
- **Gate:** PASS=21 FAIL=0 unchanged. The five steps are independent
  and each leaves the gate green; commit per-step is fine.

### PARSER-SC-4 — function def + call

D4 applies — write this rung clean from the start.  Use `~`/`&` for all
new shift/reduce sites; use `$'function'`/`$'return'`/`$'freturn'`/
`$'nreturn'` keyword tokens; no leading underscores in any new
identifiers; no `{ stmt; }` single-statement bodies; 120-char dividers.

- [ ] `func_head : T_DEFINE T_IDENT T_LPAREN func_arglist opt_head_sep`
      (BNF line 701). Lowers to `(STMT :subj (E_FNC name (...args)))`.
- **Sibling LANG rungs:** SC-5..SC-7. **Gate:** PASS≥30.

### PARSER-SC-5 — pattern match `expr ? pat`

- [ ] `Expr1 = *Expr3 FENCE($'?' *Expr1 reduce('E_SCAN', 2) | epsilon)`.
      `sc_split_subject_pattern` (`snocone_parse.y` 1306) shows
      `E_ASSIGN(E_SCAN(s, p), r)` → `STMT { :subj=s, :pat=p, :repl=r }`.
- **Sibling LANG rungs:** SC-8, SC-9. **Gate:** PASS≥40.

### PARSER-SC-6 — full beauty.sc crosscheck

- [ ] PARSER-SC parses `beauty.sc` end-to-end. `tree_equal` against the
      existing frontend returns true. Both trees run identically under
      `--ir-run`.
- **Sibling LANG rung:** SC-final / `GOAL-SNOCONE-IN-SNOCONE` SS-N.
- **Gate:** beauty.sc round-trips.

---

## Invariants

- PARSER-SC never edits the existing Snocone frontend to make trees match.
- Test programs in `corpus/programs/snocone/parser-fixtures/` are owned by
  PARSER-SC.
- `.ref` files captured at rung-land time, checked in, not silently
  re-captured.
- The existing Snocone lowering (`snocone_lower.c`) is load-bearing for OTHER
  goals; don't perturb without explicit Lon approval.

---

## Watermark

**PARSER-SC-0 ✅ PARSER-SC-1 ✅ PARSER-SC-INFRA-1 ✅ PARSER-SC-INFRA-2 ✅
PARSER-SC-3 ✅**

Gate: PASS=21 FAIL=0 (atom_*, assign_*, arith_*, concat_seq, if_simple,
if_else, if_seq, if_multi_body, while_simple, while_seq, do_simple,
do_with_stmt). Smoke (`test_smoke_snocone.sh`): PASS=5 FAIL=0.
Sibling parsers unaffected.

**Session #65 (2026-05-04) — D4 added; PARSER-SC-3 confirmed landed at
PASS=21.**

PARSER-SC-3 (control flow: `if_head`, `if_else`, `while_head`, `do_head`,
multi-line input handling) was implemented in a previous session but the
watermark was never bumped from PASS=13.  This session ran the gate, saw
PASS=21 FAIL=0 across the full control-flow fixture set, and bumped the
watermark to match reality.

Beyond the watermark fix, this session added **D4 — beauty.sno style** to
the design principles (`## Naming & Design Principles ### 5. beauty.sno
style (D4)`).  D4 codifies the conventions Lon called out from
`beauty.sno` / `beauty.sc`:

- `Gray` / `White` baked into `$'tok'` definitions; grammar productions
  never reference whitespace directly.
- `$'kw'` for language reserved words; non-reserved word-tokens as plain
  identifiers (`S = $' ' 'S'`).
- `$' '` (one space) and `$'  '` (two spaces) — invisible
  optional/required whitespace tokens.
- Shift via `~` and Reduce via `&` OPSYN (`semantic.sc`).
- `nPush()` / `nInc()` / `nTop()` / `nPop()` for n-ary trees.
- `E_*` IR tags from `EXPR_t` (already followed).
- No leading underscores in user identifiers — reserved for generated
  code.
- No `{ stmt; }` for single-statement bodies.
- 120-char `/*===*/` major and `/*---*/` minor dividers; no blank lines
  as separators.
- Horizontal-dense, vertically-balanced wrapping.
- Names track the official language spec (existing D2/D3 restated).

D4 is normative for every `parser_<lang>.sc`.  These are guidelines not
laws — existing parsers that violate them still produce correct IR.
PARSER-SC-INFRA-3 is the cleanup rung that brings `parser_snocone.sc`
into D4 conformance; sibling sessions can run analogous cleanups (or
absorb the corrections during their own next rung).

**Open follow-ups (out of scope for this rung):**

- File a scrip pattern-engine bug for the FENCE/`*deref` interaction.
  Repro: `*Id FENCE('=' *Id | epsilon)` against `'x=y'` captures `[x]`
  instead of `[x=y]`; without FENCE the same pattern captures `[x=y]`.
- D3 BNF (`corpus/programs/ebnf/snocone.ebnf`) check-in skipped per Lon.

**Next rung:** PARSER-SC-INFRA-3 — D4 style cleanup of
`parser_snocone.sc` (8 underscore renames, 1 single-stmt body fix,
divider sweep, shift/reduce → `~`/`&` conversion, `$' '`/`$'  '`
sweep). Five steps, each independently gate-green.
