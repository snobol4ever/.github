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
> **Cross-PARSER-* style (session #65):** the canonical beauty.sno /
> beauty.sc–derived style guide is
> `GOAL-PARSER-SNOBOL4.md ## Style Guidelines for parser_*.sc` —
> binding on every PARSER-* (SNOBOL4, Snocone, Icon, Prolog, Raku, Rebus).
> Read that section first; the principles below are Snocone-specific
> extensions.  PARSER-SC-INFRA-3 brings `parser_snocone.sc` into
> conformance.

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

## Naming & Design Principles — Snocone-specific (D1/D2/D3)

> ⛔ **Cross-PARSER-* style guidelines are canonical in
> `GOAL-PARSER-SNOBOL4.md ## Style Guidelines for parser_*.sc`.**
> That section is binding on every PARSER-* (SNOBOL4, Snocone, Icon,
> Prolog, Raku, Rebus): `White`/`Gray` baked into `$'tok'`, language
> keywords as `$'kw'`, non-keyword word-tokens as plain idents (`S = $' '
> 'S'`), `$' '`/`$'  '` invisible whitespace tokens, Shift via `~` and
> Reduce via `&` OPSYN, `nPush`/`nInc`/`nTop`/`nPop` n-ary counters,
> `E_*` IR tags, no leading underscores in user code, no `{ stmt; }`
> single-statement bodies, 120-char `/*===*/` and `/*---*/` dividers,
> horizontal-dense vertically-balanced wrapping. Read that section first;
> the principles below extend it with Snocone-specific decisions only.

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

### 3. Driver: top-level `Compiland`, no per-line goto loop (D1)

```
Compiland = nPush() ARBNO(*Command) reduce('Parse', 'nTop()') nPop();
Command   = simple_stmt | if_head | while_head | ... ;
```

---

## Rung ladder

### PARSER-SC-0 — atom — ✅ DONE
### PARSER-SC-1 — assignment — ✅ DONE
### PARSER-SC-INFRA-1 — Gen-based TDump — ✅ DONE
### PARSER-SC-INFRA-2 — canonical Compiland + tier ladder — ✅ DONE
### PARSER-SC-3 — control flow — ✅ DONE (PASS=21, session #65)

(Closed rungs — see git history for landed state.)

### PARSER-SC-INFRA-3 — style cleanup against canonical guide ⏳ NEXT

The canonical Style Guidelines for `parser_*.sc`
(`GOAL-PARSER-SNOBOL4.md ## Style Guidelines for parser_*.sc`) were
landed in session #65.  The existing `parser_snocone.sc` predates them
and violates several.  These are guidelines not laws — the parser
produces correct IR — but conformance makes it a clean reference for
the other PARSER-* sessions and prevents drift in SC-4/SC-5/SC-6.

The audit done in session #65 (canonical §-numbering):

| Canonical § | Guideline | Current state in `parser_snocone.sc` |
|---|---|---|
| §7 | No leading `_` in user identifiers | 8 violations: `_sc_lbl_n`, `_sc_while_ltop`, `_sc_while_lend`, `_sc_do_lcont`, `_sc_do_lend`, `_sc_strbody`, `_kw_rest`, `_parser_sc_done` |
| §8 | No `{ stmt; }` for single-statement body | 1 violation: line 383 `while (Line = INPUT) { Src = Src Line nl; }` |
| §8 | No blank lines as separators; use 120-char `/*===*/` / `/*---*/` rules | 63 blank lines; dividers are `//-----` at 71 chars (not 120) |
| §4 | `~` / `&` OPSYN over `shift(…)` / `reduce(…)` longhand | 4 `shift(` + 11 `reduce(` calls; only 2 `~` uses, 0 `&` uses |
| §3 | `$' '` / `$'  '` invisible-whitespace tokens defined once and reused | Not defined; grammar uses raw `*Gray` / `*White` / `nl_opt` ad-hoc |

Not violations (canonical guide explicitly permits or prefers):

- `sc_*` lower-case match-time helpers paired with `SC_*` upper-case
  build-time pattern-builder wrappers — §7's identifier table allows
  function names of the form `Push`, `IncCounter`, `nPush`; the lower/
  upper paired scheme is a Snocone-specific extension that does not
  contradict §7.  Keep.
- `E_*` IR tags (`E_ASSIGN`, `E_SCAN`, `E_ADD`, …) per §6 — already
  used throughout. Good.
- Line widths per §8 — zero lines exceed 120 chars. Good.

#### Steps

- [x] **Step 3a — drop leading underscores (§7).** Rename
  `_sc_lbl_n` → `sc_lbl_n`,
  `_sc_while_ltop` → `sc_while_ltop`,
  `_sc_while_lend` → `sc_while_lend`,
  `_sc_do_lcont` → `sc_do_lcont`,
  `_sc_do_lend` → `sc_do_lend`,
  `_sc_strbody` → `sc_strbody`,
  `_kw_rest` → `kw_rest`,
  `_parser_sc_done` → `parser_sc_done`.
  Verify nothing inside an EVAL string also references the underscored
  forms (the original comment block explained the EVAL constraint that
  motivated the underscores; that constraint goes away once the names
  no longer start with `_`).  Re-run gate; expect PASS=21 unchanged.
  **DONE session #65: 17 use sites renamed across 8 identifiers; two
  comment blocks trimmed of stale leading-underscore rationale; gate
  PASS=21 FAIL=0.**

- [x] **Step 3b — fix single-stmt `{ }` body (§8).** Line 383:
  `while (Line = INPUT) { Src = Src Line nl; }` →
  `while (Line = INPUT)   Src = Src Line nl;`.  Audit for any other
  single-stmt `{ }` bodies introduced after the initial scan.  Re-run
  gate. **DONE session #65: only one violation found (the driver's
  input-reader loop); fixed; gate PASS=21 FAIL=0.**

- [x] **Step 3c — replace 71-char dividers with 120-char comment rules
  (§8).** All `//---` (71-char) dividers replaced with `//===` (120-char);
  all 63 blank separator lines removed (0 remaining). Gate PASS=21 FAIL=0.
  **DONE session #66 (2026-05-04): corpus @ `b52cfa2`.**

- [x] **Step 3d — convert longhand `shift`/`reduce` to `~`/`&` OPSYN
  (§4).** All 15 call sites converted: `shift(p, t)` → `p ~ t` (2 sites),
  `reduce(t, n)` → `(t & n)` (13 sites). INFRA-11b probe re-confirmed
  this session — `~`/`&` infix dispatch works correctly via OPSYN since
  INFRA-11a/11c landed (`'foo' ~ 'Word'` fires `shift`; `('Tag' & 2)`
  fires `reduce`).  Gate PASS=21 FAIL=0.
  **DONE session #66 (2026-05-04): corpus @ `a82b43c`.**

- [x] **Step 3d-bug — scrip pattern engine: `$'  ' = *White` alias does not behave
  identically to `*White` when used in recursive grammar rules.** ✅ FIXED session #67.
  Diagnosis complete session #66; SM-side fix coded; IR-side companion still pending.

  Discovered session #66 (2026-05-04) while attempting Step 3e.  Per the canonical
  style guide §3, `$' '` / `$'  '` aliases for optional/required whitespace should
  be defined once and used at all grammar composition sites.  Definition order:

  ```
  White    = SPAN(' ' tab);
  Gray     = (*White | epsilon);
  $' '     = *Gray;          // optional whitespace alias
  $'  '    = *White;          // required whitespace alias
  ```

  Replacing `*White` with `$'  '` in the X4 recursive sequencer
  `X4 = nInc() *Expr6 ($'  ' *X4 | epsilon)` (was: `(*White *X4 | epsilon)`)
  causes the `concat_seq` fixture to regress: input `x = "hello" name;` is parsed
  as **two** statements (`E_QLIT` then `E_VAR`) instead of one `(STMT :eq :subj
  (E_VAR x) :repl (E_SEQ (E_QLIT "hello") (E_VAR name)))`.  Sweeping the rest of
  the grammar compounds the failure into PASS=0 FAIL=21.  Minimal repro
  (instrumented with side-effect counter, no parser_snocone.sc dependency):

  ```snocone
  &FULLSCAN = 1;  &ANCHOR = 1;
  function nInc() { nInc = epsilon . *_inc(); return; }
  function _inc() { _n = _n + 1; _inc = .dummy; nreturn; }
  White = SPAN(' ' tab);   $'  ' = *White;   Atom = SPAN(&LCASE);
  XA = nInc() *Atom (*White *XA | epsilon);    // bare *White
  XB = nInc() *Atom ($'  ' *XB | epsilon);     // $'  ' alias
  _n = 0;  if ('a b c' ? XA RPOS(0)) OUTPUT = 'A: count=' _n;
  _n = 0;  if ('a b c' ? XB RPOS(0)) OUTPUT = 'B: count=' _n;
  // Pre-fix output: A: count=3   (XB silently fails RPOS(0), prints nothing)
  ```

  ### Root cause (full IR walk, session #66)

  `$'  ' = *White` lowers to: evaluate `*White` in value context → `E_DEFER` at
  `sm_lower.c:570-574` → `SM_PUSH_EXPR` baking a frozen `EXPR_t*` for `White`
  into a `DT_E` descriptor → assigned to variable `"  "` via `ASGN_INDIR`.

  When `$'  '` is later referenced in pattern context, the IR is
  `E_INDIRECT(E_QLIT "  ")` (verified via `--dump-ir`).  In `lower_pat_expr`
  (`sm_lower.c:240`), `E_INDIRECT` has no dedicated case — it falls through
  the `default:` (line 500-504) which calls `lower_expr` (value-context →
  `INDIR_GET` retrieves the DT_E) followed by `SM_PAT_DEREF`.

  At `sm_interp.c:473`, the original `SM_PAT_DEREF` handler:

  ```c
  case SM_PAT_DEREF: {
      DESCR_t v = sm_pop(st);
      if (v.v == DT_P)         pat_push(v);
      else if (v.v == DT_S)    pat_push(pat_lit(v.s));
      else                     pat_push(pat_ref(VARVAL_fn(v) ?: ""));   // ← bug
  }
  ```

  has **no `DT_E` branch**.  The DT_E descriptor falls through to the `else` —
  `VARVAL_fn` returns garbage (DT_E has no string-side meaning), `pat_ref("")`
  produces a degenerate empty-name deferred reference that matches epsilon at
  first invocation and binds the recursive expansion to a dead pattern node.

  Contrast: bare `*White` is `E_DEFER(E_VAR "White")` and lowers via the
  `SN-6` branch at `sm_lower.c:485-488` → `SM_PAT_REFNAME "White"` → match-time
  deferred-name lookup that re-resolves cleanly through recursion.

  ### SM-side fix LANDED (one4all @ HEAD-+1, session #66)

  Added DT_E branch to `SM_PAT_DEREF` mirroring `eval_pat.c::interp_eval_pat`'s
  `case E_VAR` (line 82-99) DT_E handling — calls `PATVAL_fn(d)` (the SIL
  PATVAL coercion in `snobol4_argval.c:104`), which routes DT_E through
  `EVAL_fn` to thaw the EXPR_t and coerces the result to DT_P.  Build green;
  parser gate PASS=21 FAIL=0 unchanged (no regression on currently-exercised
  paths since gate uses `--ir-run`, not `--sm-run`).

  ### IR-side fix STILL PENDING

  The parser gate (`test_parser_snocone.sh`) runs with `--ir-run`, so the
  binding regression repros under the IR tree-walk path too — the SM fix
  alone does not unblock Step 3e.  Companion fix needed:

  In `eval_pat.c::interp_eval_pat` (around line 82, where `E_VAR` is handled),
  add an analogous `case E_INDIRECT:` branch:

  ```c
  case E_INDIRECT: {
      /* $expr in pattern context — eval value, then PATVAL coerce.
       * Mirrors case E_VAR's DT_E thaw at line 95-96.  Fixes recursive-rule
       * binding regression from $'  ' = *White alias (Step 3d-bug). */
      DESCR_t v = eval_node(e);   /* INDIR_GET equivalent */
      if (v.v == DT_E && !v.ptr) return NULVCL;
      if (v.v == DT_E || v.v == DT_I || v.v == DT_R) return PATVAL_fn(v);
      return v;   /* DT_S / DT_P / etc. */
  }
  ```

  Place this BEFORE the `default:` at line 382, so `E_INDIRECT` no longer
  falls through to plain `eval_node(e)` (which leaves DT_E as-is, never
  coerces to DT_P).

  ### Verification plan after IR-side fix lands

  1. Run repro snippet above — XB should report `count=3` (matches XA).
  2. Re-attempt Step 3e in parser_snocone.sc — apply the divider-region defs
     (`$' ' = *Gray; $'  ' = *White;`) and sweep `*Gray`/`*White` →
     `$' '`/`$'  '` at the 13+ grammar composition sites.
  3. Gate must hold PASS=21 FAIL=0; smoke PASS=5 FAIL=0.
  4. If green, mark Step 3d-bug ✅ and Step 3e ✅ together and bump
     PARSER-SC-INFRA-3 to closed.

- [x] **Step 3e — define `$' '` / `$'  '` once; sweep grammar (§3).** ✅ DONE (grammar
  already used these aliases; Step 3d-bug fix in eval_pat.c unblocked the full gate
  PASS=21 FAIL=0 including concat_seq). session #67.

- [x] **Step 3f — full Snocone operator-token table.**  PARSER-SC currently
  defines only the operator subset exercised by the SC-0..SC-3 rung corpus
  (`( ) { } ; = ? | + - * /`).  Snocone the language has the full SNOBOL4
  operator set plus comparison and identity operators — confirmed by the
  existing frontend's `snocone_parse.y` token enum:

  ```
  T_2PLUS T_2MINUS T_2STAR T_2SLASH T_2CARET T_2EQUAL T_2QUEST T_2PIPE
  T_2DOLLAR T_2DOT T_2AMP T_2AT T_2POUND T_2PERCENT T_2TILDE
  T_1PLUS T_1MINUS T_1STAR T_1SLASH T_1PERCENT T_1AT T_1TILDE T_1DOLLAR
  T_1DOT T_1POUND T_1PIPE T_1EQUAL T_1QUEST T_1AMP T_1BANG
  T_EQ T_NE T_LT T_GT T_LE T_GE                            (numeric)
  T_LEQ T_LNE T_LLT T_LGT T_LLE T_LGE                      (lexical)
  T_IDENT_OP T_DIFFER                                      (`::` / `:!:`)
  T_PLUS_ASSIGN T_MINUS_ASSIGN T_STAR_ASSIGN
  T_SLASH_ASSIGN T_CARET_ASSIGN
  T_LPAREN T_RPAREN T_SEMICOLON T_COMMA T_LBRACK T_RBRACK
  T_LBRACE T_RBRACE T_COLON
  ```

  Add the missing `$'X'` token definitions to `parser_snocone.sc`'s
  operator-token block, in the same shape as siblings (`$' '` both sides
  for binary operators per the canonical style guide §3, plus the
  binary-as-canonical / `$' '`-sprinkled-at-unary-site rule from
  iter#6).  Concretely, add definitions for:

  - **Binary arith / pattern**: `$'^'`, `$'**'`, `$'!'`, `$'$'`, `$'.'`,
    `$'&'`, `$'@'`, `$'#'`, `$'%'`, `$'~'` (each defined as
    `$' ' 'X' $' '`).
  - **Comparison**: `$'=='`, `$'!='`, `$'<'`, `$'>'`, `$'<='`, `$'>='`
    (numeric); the lexical comparison operators in Snocone are typically
    spelled the same as numeric — the lexer disambiguates from context;
    if Snocone has distinct lexical-comparison spellings, mirror them
    here (check `snocone_lex.c`).
  - **Identity**: `$'::'`, `$':!:'`.
  - **Augmented assign**: `$'+='`, `$'-='`, `$'*='`, `$'/='`, `$'^='`.
  - **Punctuation**: `$','`, `$':'`, `$'['`, `$']'`.

  For dual-use operators (`-`, `+`, `*`, `/`, `%`, `&`, etc.), the
  canonical variable is the **binary** form (ws both sides); at unary
  sites in productions, use `$' ' 'X'` with raw literal (single `$' '`
  leading + raw `'X'`) per the iter#6 rule.

  Adding a token definition is harmless — defining `$'X'` doesn't alter
  the grammar, only makes the variable available for use when SC-4..SC-6
  bring in productions that need it.

  Gate: PASS=21 FAIL=0 unchanged (no production references the new
  variables yet).

  **DONE session 2026-05-05 (this iteration, with iter#6 fixes):**
  added 24 new operator-token definitions to `parser_snocone.sc`'s
  operator block (full set: `[ ] , : ^ ** ! $ . & @ # % ~ == != < > <=
  >= ==: !=: <: >: <=: >=: :: :!: += -= *= /= ^=`).  Reformatted the
  block into named subsections (bracketing, pri-0/1/3, arith binary,
  pattern-build, cursor/position, numeric comparison, lexical
  comparison, identity, augmented assign).  Each definition uses the
  binary-shape `$' ' 'X' $' '` per style §3.  Gate PASS=21 FAIL=0
  unchanged (operators defined but no current production references
  them).  All six parsers' gates verified 100% post-change.

- **Sibling LANG rungs:** none — pure style.
- **Gate:** PASS=21 FAIL=0 unchanged after every step.

### PARSER-SC-4 — function def + call ✅ DONE (PASS=36, session #67 cont.)

Canonical Style Guidelines apply (see top of file) — written clean from
the start.  Used `~`/`&` for all new shift/reduce sites; used
`$'function'`/`$'return'`/`$'freturn'`/`$'nreturn'` keyword tokens; no
leading underscores in any new identifiers; no `{ stmt; }` single-
statement bodies; 120-char dividers.

- [x] `func_head : T_DEFINE T_IDENT T_LPAREN func_arglist opt_head_sep`
      (BNF line 701). Lowers to 4+N stmts: DEFINE call, skip-goto,
      entry-label, body, end-label — mirrors snocone_parse.y
      sc_func_head_new + sc_finalize_function.
- [x] Function call form `f(args)` at Expr17 level — added `Call`,
      `ArgFirst`, `ArgRest`, `CallArgs` patterns plus `decompose_call`
      helper that lifts the function name from the first child's value
      slot into the E_FNC's value slot.
- [x] `return E;` lowers to `(STMT :eq :subj (E_VAR fname) :repl E :go RETURN)`;
      `return;`/`freturn;`/`nreturn;` lower to bare goto stmts via
      `make_goto_stmt`.
- [x] `BodyFn(var)` — function-body variant supporting return/freturn/
      nreturn statements, distinct from the plain `Body(var)` used by
      if/while/do.  Uses `*body_fn_cmd` deferred lookup so forward-
      reference to return_cmd etc. works.
- **Sibling LANG rungs:** SC-5..SC-7. **Gate:** PASS=36 (was 21).

Fixtures landed: `call_simple`, `call_noarg`, `call_one_arg`,
`call_three`, `call_stmt`, `func_empty`, `func_simple`, `func_args`,
`func_three_args`, `func_two_funcs`, `func_one_assign`, `func_body`,
`func_freturn`, `func_nreturn`, `func_def_call` (15 new fixtures).

### PARSER-SC-5 — pattern match `expr ? pat` ✅ DONE (PASS=46, session #67 cont.)

- [x] `Expr1 = *Expr3 FENCE($'?' *Expr1 reduce('E_SCAN', 2) | epsilon)` —
      already wired pre-SC-5 since Expr1 has had `(E_SCAN & 2)` since
      INFRA-2.  This rung's work was in `decompose_stmt`:
- [x] `decompose_stmt` extended to handle three Snocone scan-stmt
      lowerings (mirrors `sc_split_subject_pattern` +
      `sc_append_stmt` in `snocone_parse.y` lines 1287–1352):
      Form A — `E_ASSIGN(SCAN(s,p), r)` → `(STMT :eq :subj s :pat p :repl r)`;
      Form B — bare `E_SCAN(s,p)` → `(STMT :subj s :pat p)`;
      Form B′ — bare `E_SEQ(name-like, rest…)` → `(STMT :subj first :pat rest)`
      where rest is collapsed via `build_seq_or_single` (single child
      passes through; multiple wrap as E_SEQ).
- [x] Helpers added: `is_name_like` (succeeds on E_VAR / E_QLIT — extend
      to E_KEYWORD / E_INDIRECT when grammar produces them);
      `build_seq_or_single`; `split_subj_pat` (sets globals
      `split_subj` / `split_pat`).
- **Sibling LANG rungs:** SC-8, SC-9. **Gate:** PASS=46 (was 36).

Fixtures landed (10 new): `scan_simple`, `scan_replace`, `scan_in_expr`,
`scan_juxta`, `scan_juxta_replace`, `scan_juxta_three`, `scan_multi_pat`,
`scan_pat_var`, `scan_alt`, `scan_alt_replace`.

### PARSER-SC-6 — full beauty.sc crosscheck

**Session (2026-05-05) — SC-6a landed PASS=46; SC-6b in progress; naming collision blocker found.**

New constructs implemented and working (gate PASS=46 FAIL=0):
- `E_KEYWORD` (`&kw` atom), `E_IDX` (subscript `a[i]`), `E_FLIT` (real literal),
  `E_MNS` (unary minus), `E_DEFER`/`E_NOT`/`E_NAME`/`E_INDIRECT` (unary prefix ops),
  `Real` / `Keyword` token classifiers, `Expr15` subscript tier,
  parenthesized expression `(expr)` in Expr17, `goto_cmd`, `label_prefix`, `for_cmd`.

**SC-6a LANDED (2026-05-05) — White+NL fix + Expr11/Expr12 + Call restructure.**
Changes to `corpus/programs/scrip/parser_snocone.sc`:
- `White_h`/`Gray_h` — horizontal-only ws (no nl); used by `$'(g'` and Call opener.
- `White_expr` — continuation-only ws (nl only with `+`/`.` marker per S_CONT).
- `White = *White_expr | nl FENCE(SPAN(' ' tab)|epsilon)` — full ws including bare nl
  plus following indent (cursor lands at token after eating a continuation newline).
- `Gray = ARBNO(*White)`, `$' ' = Gray`, `$'  ' = White`.
- `$'(g' = Gray_h '(' $' '` — horizontal-only grouping-open paren (no NL before `(`).
- `Expr17` grouping paren: `$'(g' *Expr0 $')'` (was `$'(' *Expr0 $')'`).
- `Call` restructured: `(*Id . captured_call_name) FENCE(Gray_h '(' $' ' nPush()
  Push_call_name_var() CallArgs $')' Decompose_call() nPop())` — nPush/nInc only
  after `(` confirmed; `Push_call_name_var()` helper + build-time companion added.
- `E_CAPT_COND_ASGN`/`E_CAPT_IMMED_ASGN`/`E_CAPT_CURSOR`/`E_POW` E_* constants.
- `Expr12` — binary `.` (E_CAPT_COND_ASGN, left-assoc) and `$` (E_CAPT_IMMED_ASGN).
- `Expr11` — exponent `^` (E_POW, right-assoc); `Expr9` wired to `Expr11`.

**SC-6b blocker (2026-05-05) — naming collision with beauty.sc's own runtime.**
beauty.sc uses `nInc()`, `nPush()`, `nPop()`, `Push()`, `Pop()` as ITS OWN
internal variable/function names (it is itself a parser using the ShiftReduce
library). When parser_snocone.sc parses beauty.sc's source text and encounters
`nInc()` as a Call expression, `Push_call_name_var()` fires `IncCounter()` — the
SHARED counter.sc runtime — incrementing the Compiland-level n-ary counter as a
side effect. After all Call-level nPush/nPop pairs balance, the Compiland counter
ends with wrong values → 1-child ptree instead of full N-child tree.

Parsing advances to ~line 128 (`Command = nInc() FENCE(...)`) before the counter
corruption causes Compiland to emit a 1-child degenerate tree.

Possible fixes (Lon to decide):
(a) Rename parser_snocone.sc's counter/stack API to a distinct namespace
    (e.g. `sc_nInc`, `sc_nPush`, etc.) that doesn't collide with beauty.sc's names.
(b) Accept that beauty.sc is not a valid crosscheck target for SC-6b due to the
    reflexive naming collision, and use a different Snocone program for the crosscheck.
(c) Isolate counter/stack state so CALL-time side effects from parsing `nInc()` in
    beauty.sc's source don't leak into Compiland's outer counter frame.

The naming collision hypothesis was **incorrect** — `push_call_name_var()` calls
`IncCounter()` inside a `nPush()`/`nPop()` frame, so it is balanced. The actual
failure source is `Stmt` (beauty.sc lines 115-124): a 10-line multi-line statement
containing `*Expr14` (a tier not yet in parser_snocone.sc). The Stmt parse stops
short, and the trailing `$' '` in `stmt_body` then consumes the newline that should
feed X4's concat for the next line — causing Compiland to emit wrong output from
line 128 onward.

**Additional SC-6b gaps found (2026-05-05):**
- `*Expr14` at beauty.sc line 116: a tier between Expr12 and Expr15 not yet in
  parser_snocone.sc. Audit `snocone_parse.y` for all skipped levels.
- Fix the trailing-`$' '`-eats-continuation-newline issue in `stmt_body` so
  multi-line statements that don't end with `;` on their last line work correctly.

**Next session:** (1) Lon decides SC-6b crosscheck target (beauty.sc vs simpler
program). (2) Add missing Expr tiers. (3) Fix stmt_body trailing-ws issue. (4) Re-run.

- [x] **Step SC-6a:** Fix `Expr17` grouping paren and `Call` so that NL-inclusive
      White does not cause infinite recursion. Restructure `Call` so `nPush/nInc`
      side effects fire only after `$'('` succeeds. Then update `White` to include
      `nl`. Verify gate PASS=46. **DONE 2026-05-05: White/NL fix landed; gate PASS=46.**
- [ ] **Step SC-6b:** Run parser against `beauty.sc`. Fix any remaining parse failures
      iteratively until parser output matches oracle (whitespace-normalized).
      **BLOCKED on naming collision above — awaiting Lon decision on fix approach.**
- [ ] **Step SC-6c:** `tree_equal` against existing frontend returns true. Both trees
      execute identically under `--ir-run`.
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
PARSER-SC-3 ✅ PARSER-SC-INFRA-3 ✅ PARSER-SC-4 ✅ PARSER-SC-5 ✅
PARSER-SC-6 ⏳ (SC-6a ✅ SC-6f ✅ SC-6g ✅ SC-6h ✅ SC-6i ✅ landed; SC-6b next — Expr14 gap + stmt_body trailing-ws fix)**

Gate: PASS=46 FAIL=0. corpus @ `f79c025`. SC-6f/g/h/i landed: style edits,
kw_X=(Id$tx*IDENT), correct Id/Ident/sc_reserved structure: sc_reserved=POS(0)(...)RPOS(0),
notmatch(s,pat) helper, Ident=Id$tx*notmatch(tx,sc_reserved) rejects reserved words,
Expr17 E_VAR uses Ident. SC-6b next: Expr5/5a missing tiers + beauty.sc crosscheck.

**Session #67 cont. (2026-05-04) — PARSER-SC-5 landed (pattern-match scan stmt).**

`Expr1` already had `(E_SCAN & 2)` reduction since INFRA-2 — the rung's
work was entirely in `decompose_stmt`.  Mirrored the
`sc_split_subject_pattern` + `sc_append_stmt` two-step from
`snocone_parse.y` lines 1287-1352:

1. If TOP is `E_ASSIGN(lhs, rhs)`: try splitting lhs into subj+pat.
   If lhs splits → emit 4-part stmt `:eq :subj :pat :repl`.
   Else → standard 3-part `:eq :subj :repl`.
2. Else if TOP itself splits → emit 2-part `:subj :pat`.
3. Else → bare-expression `:subj`-only stmt.

`split_subj_pat` succeeds on either `E_SCAN(s,p)` or
`E_SEQ(name-like, rest…)` (Form 2: SNOBOL4 traditional juxtaposition
scan, e.g. `x  'foo'` with double-space).  `build_seq_or_single`
collapses a 1-element rest into a bare child, otherwise wraps as
E_SEQ.  `is_name_like` matches E_VAR / E_QLIT today; extend to
E_KEYWORD / E_INDIRECT when those frontend kinds reach the parser.

**Next rung:** PARSER-SC-6 — full beauty.sc crosscheck.

**Session #67 cont. (2026-05-04) — PARSER-SC-4 landed (function def + call).**

Added 4 keyword guards (`function`, `return`, `freturn`, `nreturn`),
9 match-time helpers (`decompose_call`, `func_head_save_name`,
`save_param_first`, `save_param_rest`, `make_define_stmt`,
`finalize_function`, `emit_return_value`, `emit_return_void`,
`emit_freturn`, `emit_nreturn`), 9 build-time companions, `Call` /
`ArgFirst` / `ArgRest` / `CallArgs` patterns at Expr17 level, `BodyFn`
variant for function bodies (uses `*body_fn_cmd` deferred lookup to
break the forward-reference cycle to return_cmd), and `func_cmd` /
`return_cmd` / `freturn_cmd` / `nreturn_cmd` grammar productions
wired into `Command`.

Two pattern-engine subtleties caught during write:
1. Dot-binding `*Id . captured_name` has lower precedence than
   concatenation in SNOBOL4 — `*kw_function $'  ' *Id . cn` parses as
   `(*kw_function $'  ' *Id) . cn`.  Fixed with explicit parens at
   each capture site: `(*Id . captured_name)`, `(*Id . captured_param)`.
2. `ARBNO(a | b | c | d)` does not reliably try alternatives in order
   when the alternation contains forward-referenced patterns.  The
   working pattern is `ARBNO(*body_fn_cmd)` with `body_fn_cmd =
   (return_cmd | freturn_cmd | nreturn_cmd | stmt_cmd)` defined later.

`finalize_function` push-count: emits N+4 stmts (DEFINE, goto, entry-
label, N body, end-label) but only N+3 IncCounter calls — the outer
`nInc()` in func_cmd already counts 1 for the whole construct.

**Next rung:** PARSER-SC-5 — pattern match `expr ? pat`.

**Session #67 (2026-05-04) — Step 3d-bug IR-side fix landed; INFRA-3 closed.**

IR-side companion fix landed in `eval_pat.c::interp_eval_pat`: added
`case E_INDIRECT:` branch before `default:` (mirroring `case E_VAR`'s
DT_E thaw at lines 95-96). When `$'  '` is referenced in pattern context,
`interp_eval_pat` now calls `eval_node(e)` (INDIR_GET) then coerces via
`PATVAL_fn` if DT_E/DT_I/DT_R — instead of falling through to `default:`
which returned DT_E as-is without pattern coercion.

Repro verification: `XA` (bare `*White`) and `XB` (`$'  '` alias) both
report `count=3` on `'a b c'`. Previously XB printed nothing (RPOS(0) fail).

Step 3e: grammar already used `$' '`/`$'  '` from a prior session. With
the engine fix in place, `concat_seq` and all 21 fixtures pass cleanly.
INFRA-3 is complete.

**Next rung:** PARSER-SC-4 — function def + call.

Root cause traced: `$'  ' = *White` stores a `DT_E` (frozen-EXPR) descriptor
as the variable's value; when later referenced in pattern context via
`E_INDIRECT`, the lowering falls through `lower_pat_expr`'s `default:` →
`lower_expr` (value path: `INDIR_GET` retrieves the DT_E) → `SM_PAT_DEREF`.
The original `SM_PAT_DEREF` handler at `sm_interp.c:473` had no DT_E branch
— it fell through to `VARVAL_fn` + `pat_ref("")`, producing a degenerate
empty-name deferred reference that broke recursive-rule binding.

Contrast: bare `*White` is `E_DEFER(E_VAR "White")` and lowers via the
SN-6 branch at `sm_lower.c:485-488` → `SM_PAT_REFNAME "White"` → match-time
deferred-name lookup that re-resolves cleanly through recursion.

SM-side fix landed in `sm_interp.c::SM_PAT_DEREF`: added DT_E branch that
calls `PATVAL_fn(d)` (SIL PATVAL coercion in `snobol4_argval.c:104`) to
thaw the frozen EXPR_t through `EVAL_fn` and coerce to DT_P.  Mirrors
the IR-side `case E_VAR` DT_E thaw at `eval_pat.c:82-99`.  Build green;
parser gate PASS=21 FAIL=0 unchanged.

IR-side companion fix STILL PENDING — the gate uses `--ir-run`, so the
binding regression also reproduces under the IR tree-walk path. Companion
fix is an analogous `case E_INDIRECT:` branch in `eval_pat.c::interp_eval_pat`
(insertion point and code skeleton recorded in the Step 3d-bug entry above).

Until the IR-side lands, Step 3e remains blocked.

**Session #66 (2026-05-04) — INFRA-3 Steps 3c + 3d landed; Step 3e blocked
on newly-filed Step 3d-bug.**

Step 3c (corpus @ `b52cfa2`): replaced 26 occurrences of 71-char `//---`
dividers with canonical 120-char `//===` dividers throughout
parser_snocone.sc; removed all 63 blank separator lines.  Gate PASS=21
FAIL=0; smoke PASS=5 FAIL=0.  File 391 → 328 lines.

Step 3d (corpus @ `a82b43c`): converted all 15 longhand `shift(p, t)` /
`reduce(t, n)` call sites in the grammar to `~` / `&` OPSYN infix form
(2 `shift` → `~`, 13 `reduce` → `&`).  INFRA-11b probe re-confirmed
this session: `'foo' ~ 'Word'` dispatches to `shift`, `('Tag' & 2)`
dispatches to `reduce` — both via OPSYN — since INFRA-11a/11c landed
2026-05-03.  Header comment "Constants for reduce()/shift()" updated to
"Constants for ~ / & OPSYN tags".  Gate PASS=21 FAIL=0.

Step 3e attempted and reverted: replacing grammar composition `*Gray` /
`*White` with `$' '` / `$'  '` aliases regresses the gate to PASS=0
FAIL=21 (empty parser output, no Parse Error message).  Bisected: the
X4 recursive sequencer alone — `X4 = nInc() *Expr6 ($'  ' *X4 |
epsilon)` — loses the chain after the first atom, dropping `concat_seq`
to FAIL.  Sweeping the rest of the grammar compounds the failure.
Isolated `$'  '` probes work; the bug surfaces only in the full
parser_snocone.sc combination of `nInc()` + `*Expr6` + `$'  '` recursion.
Filed as Step 3d-bug above; engine-level fix in `snobol4_pattern.c`
needed before Step 3e can land.

**Session #65 (2026-05-04) — PARSER-SC-3 watermark bump; cross-PARSER
style guidelines integrated; INFRA-3 Steps 3a + 3b banked.**

PARSER-SC-3 (control flow: `if_head`, `if_else`, `while_head`, `do_head`,
multi-line input handling) was implemented in a previous session but the
watermark was never bumped from PASS=13.  This session ran the gate, saw
PASS=21 FAIL=0 across the full control-flow fixture set, and bumped the
watermark to match reality.

Cross-PARSER-* style — derived from `beauty.sno` / `beauty.sc` and
called out by Lon this session — was promoted by sibling sessions to a
canonical home at
`GOAL-PARSER-SNOBOL4.md ## Style Guidelines for parser_*.sc`,
binding on every PARSER-* (SNOBOL4, Snocone, Icon, Prolog, Raku, Rebus).
Read that section for the full nine-section guide:

1. Names match the official language specification.
2. `White` / `Gray` are attached to tokens, never referenced in the
   main grammar.
3. Reserved-word and special-character tokens use `$'name'` form.
4. Tree-build decorations use `shift`/`reduce` (or the `~`/`&` OPSYN
   shorthand), not bare deferred calls.
5. n-ary trees use `nPush()` / `nInc()` / `nTop()` / `nPop()`.
6. AST/IR tag names use `E_*` from `EXPR_t`.
7. Identifier conventions (no leading `_`; pattern names UpperCamel;
   functions UpperCamelSnake; variables lowercase snake_case).
8. Layout: 120-char lines; single-statement bodies one-line no braces;
   `/*===*/` major and `/*---*/` minor dividers; no blank lines as
   separators.
9. Read beauty.sno / beauty.sc end-to-end before authoring.

These are guidelines not laws — existing parsers that violate them
still produce correct IR.  PARSER-SC-INFRA-3 is the cleanup rung that
brings `parser_snocone.sc` into conformance; sibling sessions can run
analogous cleanups (or absorb the corrections during their own next
rung).  The audit found 5 violation classes (8 leading underscores,
1 single-stmt body, 63 blank lines, 15 longhand `shift`/`reduce` call
sites, no `$' '`/`$'  '` whitespace tokens) and 3 already-clean items
(no lines >120, `E_*` tags throughout, paired `sc_*`/`SC_*` helpers
permitted).

INFRA-3 progress this session:

- **Step 3a (drop leading underscores) ✅** — 17 use sites renamed
  across 8 identifiers (`_sc_lbl_n` → `sc_lbl_n` and 7 others).  Two
  comment blocks trimmed of stale leading-underscore rationale.  Gate
  PASS=21 FAIL=0.
- **Step 3b (single-stmt `{ }` body) ✅** — driver's input-reader loop
  rewritten without braces; only one violation in the whole file.  Gate
  PASS=21 FAIL=0.
- **Steps 3c, 3d, 3e** — pending next session (divider sweep,
  `shift`/`reduce` → `~`/`&` conversion across 15 sites, `$' '`/`$'  '`
  token sweep).

**Open follow-ups (out of scope for this rung):**

- File a scrip pattern-engine bug for the FENCE/`*deref` interaction.
  Repro: `*Id FENCE('=' *Id | epsilon)` against `'x=y'` captures `[x]`
  instead of `[x=y]`; without FENCE the same pattern captures `[x=y]`.
- D3 BNF (`corpus/programs/ebnf/snocone.ebnf`) check-in skipped per Lon.

**Next rung:** PARSER-SC-INFRA-3 Step 3d-bug (continued) — apply the IR-side
companion fix in `eval_pat.c::interp_eval_pat case E_INDIRECT:` (skeleton
recorded in the Step 3d-bug entry above), verify against the repro and
parser gate, then proceed to Step 3e.
