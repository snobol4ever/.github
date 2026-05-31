# GOAL-PARSER-SNOCONE.md — PARSER-SNOCONE pattern-based frontend in Snocone

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ ABSOLUTE RULE — ZERO C BYRD BOX FUNCTIONS — NO EXCEPTIONS — READ THIS BEFORE WRITING CODE  ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                  ║
║  A C Byrd box (C BB) is ANY C function with this signature:                                     ║
║                                                                                                  ║
║      DESCR_t foo(void *zeta, int entry)                                                         ║
║                                                                                                  ║
║  implementing four-port logic (α / β / γ / ω).                                                  ║
║                                                                                                  ║
║  THERE MUST BE ZERO OF THESE IN THE CODEBASE. NOT ONE. NONE. EVER.                              ║
║                                                                                                  ║
║  ALL Byrd boxes are x86 ASSEMBLY emitted at runtime by the emitter.                             ║
║  If you want a BB, you EMIT it. You do not write a C function for it.                           ║
║                                                                                                  ║
║  The only permitted C functions with (void *zeta, int entry) signature are:                     ║
║    • icn_lazy_box  — infrastructure shim, not a generator                                       ║
║    • icn_bb_dcg    — infrastructure DCG driver, not a generator                                 ║
║                                                                                                  ║
║  If you just wrote DESCR_t foo(void *zeta, int entry) { ... } — DELETE IT.                     ║
║  Implement it as an IR_block_t DCG (ir_exec.c + lower_icn.c) driven by icn_bb_dcg.             ║
║  See IR_ICN_UPTO in ir_exec.c and lower_icn_upto() in lower_icn.c as the template.             ║
║                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

**Repo:** corpus+SCRIP
**Branch:** `parser` (SCRIP only — `corpus` and `.github` stay on `main`)
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
( cd /home/claude/SCRIP && git fetch origin parser 2>/dev/null; \
  git checkout parser 2>/dev/null || git checkout -b parser origin/parser 2>/dev/null || git checkout -b parser )
bash /home/claude/SCRIP/scripts/install_system_packages.sh
bash /home/claude/SCRIP/scripts/build_scrip.sh
```

Gate after setup:
```bash
bash /home/claude/SCRIP/scripts/test_smoke_snocone.sh        # existing frontend baseline
bash /home/claude/SCRIP/scripts/test_parser_snocone.sh       # this goal's gate
```

---

## Architecture reminder

```
scrip --parser-crosscheck parser_snocone.sc tiny.sc
```

SCRIP runs `parser_snocone.sc` (which `-include`s the shared SC library from
`corpus/SCRIP/`) against `tiny.sc` — PAT produces IR tree t2 via
`Compiland`; the existing Snocone frontend produces t1. Both compared in
memory (`tree_equal`), both executed in memory. No subprocesses, no temp
files, no on-disk diffs.

**Shared SC library** (`corpus/SCRIP/`):
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

### PARSER-SC-INFRA-3 — style cleanup against canonical guide ✅ DONE (session #67)

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
  `E_INDIRECT(E_QLIT "  ")` (verified via `--dump-ast`).  In `lower_pat_expr`
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

  ### SM-side fix LANDED (SCRIP @ HEAD-+1, session #66)

  Added DT_E branch to `SM_PAT_DEREF` mirroring `eval_pat.c::interp_eval_pat`'s
  `case E_VAR` (line 82-99) DT_E handling — calls `PATVAL_fn(d)` (the SIL
  PATVAL coercion in `snobol4_argval.c:104`), which routes DT_E through
  `EVAL_fn` to thaw the EXPR_t and coerces the result to DT_P.  Build green;
  parser gate PASS=21 FAIL=0 unchanged (no regression on currently-exercised
  paths since gate uses `--interp`, not `--interp`).

  ### IR-side fix STILL PENDING

  The parser gate (`test_parser_snocone.sh`) runs with `--interp`, so the
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
Changes to `corpus/SCRIP/parser_snocone.sc`:
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
- [x] **Step SC-6b:** Run parser against `beauty.sc`. Fix any remaining parse failures
      iteratively until parser output matches oracle (whitespace-normalized).
      **DONE 2026-05-06 session 3:** Diff (A) FIXED via flatten_arith. Diff (B) FIXED
      via one-character `*if_cmd` recursion fix.  Three new fixtures added (if_else_if,
      if_else_if_else_if, if_else_if_else); all byte-identical to oracle. Gate PASS=50 FAIL=0.

      **Diff (A) FIXED — `flatten_arith` post-parse step (corpus @ 05a1bea):**
      Added `flatten_arith(x)` + `sc_flatten_ops` to `parser_snocone.sc`.
      Called from `decompose_stmt` after `top = Pop()`. Converts right-recursive binary
      arithmetic chains to n-ary: E_SUB(a,E_SUB(b,c)) → E_SUB(a,b,c). E_ADD/E_SUB/E_MUL/E_DIV
      flattened; E_POW right-associative (not flattened). Fixture `arith_sub_nary` added.
      Gate PASS=47 FAIL=0.

      **Diff (B) FIXED 2026-05-06 session 3 — bare `if_cmd` was not recursive:**
      The hypothesis from session 2 about post-match DOT firing order was **wrong**.
      The actual root cause: the else-if branch grammar
      `| nPush() if_cmd Save_nbody('if_nelse') nPop()` referenced `if_cmd` as a
      bare identifier without the deferred-evaluation operator `*`.  Per SPITBOL
      Manual Ch 9 ("Recursive Patterns"), a recursive pattern definition must use
      `*` to defer the self-reference to match time — bare `if_cmd` captures the
      OLD value of `if_cmd` (null/empty) at pattern-build time.

      Symptom: when the else body was an inline `if_cmd`, the inner if was NOT
      matched recursively as the else body (because bare `if_cmd` matched epsilon),
      so it fell out of the inner Compiland match.  The outer `Finalize_if_else`
      then fired with empty else body (allocating `Lelse_0001`/`Lend_0002`),
      and `ARBNO(*Command)` at top level then matched the inner `if (...)` as a
      separate top-level command (allocating `Lend_0003`).  This presented as
      a "label-ordering" bug but was really a missing-recursion bug.

      Fix: `if_cmd | nPush() if_cmd ...`  →  `| nPush() *if_cmd ...` (one-char addition).
      Verification: `if (x==1) { y=2; } else if (x==3) { y=4; }` produces output
      byte-identical to the oracle's `--dump-ast`; same for triple else-if and
      else-if-else.  Gate PASS=50 FAIL=0 (3 new fixtures: if_else_if,
      if_else_if_else_if, if_else_if_else).  beauty.sc: 1148/1148 stmts; the
      previous structural diff in 2 if-else-if instances is gone.

- [x] **Step SC-6b-bug:** Fix parser_snocone.sc Compiland's `nTop()` timing so the
      first stmt isn't dropped from the parse tree on large inputs.  Discovered
      and refined 2026-05-06 session 4.  **FIXED session 5 (2026-05-06).**

      **Fix:** replaced `(E_Parse & 'nTop()')` with `reduce_prim(E_Parse)` at
      Compiland line 654 (`corpus/SCRIP/parser_snocone.sc`).
      `reduce_prim(tag)` (defined in `semantic.sc`) produces
      `epsilon . *ReducePrim(tag)` — fires `ReducePrim` at match time, which
      calls `TopCounter()` as its very first operation before popping any args.
      This eliminates all concern about the EVAL'd pattern's `nTop()` binding
      time.  Verified: 5-stmt test and head-10 beauty.sc test both produce
      byte-identical output to oracle; `&FULLSCAN = 1` correctly appears as
      first stmt in all tests.  Gate PASS=50 FAIL=0.

      **Symptom (refined this session):** running parser_snocone.sc against the
      full 587-line beauty.sc produces output where exactly the first stmt
      `&FULLSCAN = 1;` is missing — every other stmt is byte-identical to the
      oracle.  Adding 10 prefix stmts (`pp1 = 1; ... pp10 = 10;`) to beauty.sc
      reproduces it: only `pp1` is dropped, `pp2`..`pp10` plus all of beauty
      come through correctly.  Across `--interp`, `--interp`, `--run`:
      identical symptom.

      **Diagnosis (this session):** the bug is in `parser_snocone.sc`, NOT the
      scrip executable.  Instrumenting the driver to print `n(ptree)` after
      `Pop()` shows `n_kids=1147` for full beauty.sc (oracle: 1148 stmts), and
      `child[1]` contains the SECOND oracle stmt.  So the parse tree under
      `Parse` has one fewer child than expected, and the missing one is the
      first-pushed (bottom of stack).

      The mechanism: Compiland's grammar is
      ```
      Compiland = nPush() ARBNO(Command) (E_Parse & 'nTop()') nPop();
      ```
      `(E_Parse & 'nTop()')` is OPSYN-dispatch to `reduce(E_Parse, 'nTop()')`.
      Inside `reduce`, the second arg is a STRING `'nTop()'` (not an
      EXPRESSION), so it falls through the `IDENT(DATATYPE(n), 'EXPRESSION')`
      check unevaluated.  Then `reduce` returns
      `EVAL("epsilon . *Reduce('E_Parse', nTop())")` — `nTop()` is embedded as
      a function call into the resulting pattern, called at MATCH-time when
      the `.`-action fires.

      `Reduce(t, n)` then pops `n` items from the tree stack.  If `n` is one
      less than the actual stack size, the FIRST-pushed (bottom-of-stack)
      item is left untouched on the stack while the top `n` items are popped
      into `c[1..n]`.  Result: tree with `n` children where the very first
      (oldest) stmt is missing.  This precisely matches the symptom.

      Why `nTop()` returns one less than the actual IncCounter count on
      large inputs: not yet diagnosed.  Hypotheses to investigate:
      1. `Reduce`'s `.`-action fires before all of `ARBNO(Command)`'s last
         `IncCounter()` actions have completed — possible if scrip's `.`-action
         queue has insertion-point semantics that put outer registrations
         ahead of late-arriving inner ones in some edge case.
      2. The deferred-eval of `nTop()` inside the EVAL'd pattern is captured
         too early (e.g., at pattern-build time rather than match time).
      3. ARBNO with very many iterations has a quirk where the final iteration's
         tail actions don't all register.

      **Why it's not a scrip executable bug:** the symptom is deterministic
      across all three backends, depends on input content (large simple
      file works fine, small complex file works, only specific complex large
      content fails), and points exactly to the off-by-one stack drop pattern
      consistent with the `(E_Parse & 'nTop()')` formulation.

      **Probable fix to try first:** replace `(E_Parse & 'nTop()')` with
      `reduce_prim('E_Parse')` which uses `ReducePrim(tag)` from
      `corpus/SCRIP/ShiftReduce.sc`.  ReducePrim reads
      `TopCounter()` internally at match time — same as `nTop()` but
      called as the very first operation inside the `.`-action body,
      eliminating any concern about the EVAL'd pattern's binding time.
      Expected single-line change at parser_snocone.sc:653 (Compiland's
      reduce position).

      **Separate issue — SIGSEGV/heap-corruption at intermediate input sizes
      (n=198..300 of beauty.sc head -N):** distinct symptom from the
      first-stmt drop.  Not yet investigated; may be a real scrip runtime
      memory-safety bug, or may be a downstream consequence of the same
      grammar timing issue when the partial input creates an inconsistent
      stack state.  File separately as `SC-6b-bug-segfault` after `SC-6b-bug`
      lands and we can re-test cleanly.

- [x] **Step SC-6b-bug-segfault:** SIGSEGV/heap-corruption at intermediate input
      sizes (`head -198..-300 beauty.sc`).  **FIXED session 5 (2026-05-06).**

      **Root cause:** `cache_get_fresh` in `stmt_exec.c` shallow-copied the
      `arbno_t` struct via `memcpy`.  `arbno_t` contains a heap-allocated
      `stack` pointer that `bb_arbno` may `realloc()` as iteration depth
      exceeds the initial capacity (`ARBNO_INIT_CAP = 8`).  The shallow copy
      shared the `stack` pointer between the cache template and the fresh copy.
      When the fresh copy's `bb_arbno` grew past cap and `realloc`'d its stack,
      the cache template's `stack` became a dangling pointer.  The next
      `cache_get_fresh` call for the same node copied that dangling pointer into
      another fresh copy → writes to freed memory → heap corruption → SIGABRT /
      SIGSEGV.  Valgrind confirmed: "Invalid write at bb_arbno:148" and
      "Invalid free / realloc" from the inner arbno called via `bb_deferred_var`
      nested inside the outer `ARBNO(*Command)`.

      **Fix:** `cache_get_fresh` now deep-copies `arbno_t`'s `stack` array when
      the node is an ARBNO (`n.fn == bb_arbno`), so each fresh copy owns its
      own allocation.  Additionally unified the `arbno_frame_t` / `arbno_t`
      definitions into `bb_box.h` (canonical), replacing the two inconsistent
      local definitions in `bb_boxes.c` (no `nam_mark`) and `stmt_exec.c`
      (with `nam_mark`) — the size mismatch made the deep copy incorrect even
      after the initial fix attempt.

      **Verification:** `head -198`, `-220`, `-250`, `-300` of beauty.sc all
      exit rc=0 (was SIGSEGV/SIGABRT).  Gate PASS=50 FAIL=0 unchanged.

- [x] **Step SC-6c-bug:** Off-by-one in Compiland counter — first STMT stranded
      on tree stack. **FIXED session 8 (2026-05-06): root cause was global variable
      clobber, not counter timing. See fix note below.**

      **Symptom (unchanged):** parser_snocone.sc on full beauty.sc (587 lines)
      produces 1147 stmts instead of oracle's 1148. The missing stmt is always
      `&FULLSCAN = 1` (the very first stmt) — it remains stranded at the bottom
      of the tree stack after `reduce_prim(E_Parse)` pops 1147 items.

      **Smaller reproduction (NEW this session):**

      Minimal trigger isolated to `/tmp/wraptest.sc` (~38 lines, diff=1) and
      `/tmp/redux.sc` (~20 lines, diff=3 — multiple off-by-ones).  Both extracted
      from beauty.sc lines 200-237 (`pp` function's `Stmt` branch).

      Bisection on `head -N beauty.sc` (closing functions manually to keep
      oracle-parseable):

      | h156 + lines 163-N | oracle | parser | diff |
      |--------------------|-------:|-------:|-----:|
      | h156 + 163-200     | 210    | 210    | 0    |
      | h156 + 163-215     | 0(✗)   | 1      | -    |
      | h156 + 163-335     | 500    | 499    | **1**|

      Bug appears between input lines 200-237 of beauty.sc — within the `Stmt`
      branch of `pp(x)`, which contains nested if + `else if (DIFFER(ppAsgn))`
      + nested ifs with assignment statements. Removing the else-if structure
      reduces diff to 0; reproducing gives diff≥1.  This strongly suggests the
      bug is in the **else-if-recursion branch** at line 625 of
      parser_snocone.sc:

      ```
      | nPush() *if_cmd Save_nbody('if_nelse') nPop()
      ```

      when the inner `*if_cmd` itself contains nested ifs with body statements.

      **Two-stack instrumentation results (NEW this session):**

      Instrumented `Push`/`Pop` in `stack.sc` and `PushCounter`/`PopCounter`/
      `IncCounter` in `counter.sc` with frame-depth tracking, plus per-finalize
      push/inc trackers in `parser_snocone.sc`.  Findings:

      - **STMT-tagged Push at depth=1: 1147** (one short of expected 1148)
      - **IncCounter at depth=1: 1147** (matches what `reduce_prim` reads via
        `TopCounter`)
      - STMT pushes at depths 2-7 occur normally (983 + 737 + 272 + 39 + 22 + 11),
        all expected to be popped by their enclosing `pop_body` and re-pushed at
        the outer frame as part of the if/while/for/func flattening.
      - First STMT push at depth 1 happens at counter=1 (FULLSCAN's nInc fired
        correctly).  All depth-1 STMT pushes line up with monotonic
        IncCounter(N+1)→Push(N+1) ordering.  No corruption mid-stream.
      - Per-finalize push/inc deltas (counts of pushes within each finalize_X
        and IncCounters in its tail loop) add up to a CONSISTENT TOTAL with
        the expected `outer_nInc + finalize_inc == finalize_pushes` formula
        for every construct: `if`, `if-else`, `while`, `do`, `for`, `function`,
        `for_head_alloc`.  Paper math is balanced.

      **Where the missing stmt goes:**

      The data is consistent with **one Push(STMT) happening at depth ≥ 2 that
      should have happened at depth = 1**, OR equivalently, **one IncCounter()
      that should fire at depth = 1 fires at depth ≥ 2 instead**.  Frame-depth
      counting at every Push/Inc confirms the former for the full-beauty case:
      total STMT pushes summed across all depths is 3211, but only 1147 land
      at depth 1 — exactly one fewer than 1148.

      **Architectural suspicion (next session start here):**

      The bug is structural in the if-else-if recursion path.  The pattern at
      line 625, `| nPush() *if_cmd Save_nbody('if_nelse') nPop()`, opens a fresh
      counter frame, runs the inner `*if_cmd` inside it, captures its top into
      `if_nelse`, then pops the frame.  After `nPop`, control returns to outer
      `Finalize_if_else` which calls `pop_body(if_nelse)` to drain the inner if's
      generated STMTs from the data stack.

      Hypothesis: when the inner `*if_cmd`'s body contains another nested
      if-else-if (multi-level cascade), some `IncCounter` call inside an inner
      finalize lands in the OUTER `nPush()` frame from line 625 instead of the
      INNERMOST frame opened by the inner if's Body — because pattern action
      timing (the dot-action `*finalize_X` firing on a particular cursor pass
      through the pattern) interacts subtly with how SNOBOL4 evaluates
      `nPush()`/`nPop()` actions during recursion.  Not yet confirmed.

      **Files touched this session (ALL REVERTED before push):**
      - `corpus/SCRIP/parser_snocone.sc` — instrumentation in every
        `finalize_*`, `emit_*`, `decompose_stmt`, plus dump output at end of
        driver
      - `corpus/SCRIP/counter.sc` — `dbg_frame_depth` /
        `dbg_inc_compiland` tracking in `PushCounter`/`PopCounter`/`IncCounter`
      - `corpus/SCRIP/stack.sc` — `dbg_push_compiland` /
        `dbg_push_stmt_d1` tracking in `Push`/`Pop`

      Per RULES.md "Diagnostic patches are diagnostic — never commit them",
      all three files reverted to corpus@HEAD before handoff.  Gates remain
      smoke PASS=5 / parser PASS=50.

      **Next session fix plan (refined):**

      1. Re-apply the depth-tracking instrumentation (kept as a one-shot diff
         in this session's notes — see mechanism above).
      2. Run on `/tmp/redux.sc` (diff=3, ~20 lines, fastest iteration loop).
      3. Add per-construct firing trace: log `(construct, depth_at_firing,
         frame_id)` for every `*_cmd`'s outer `nInc()` firing.  Cross-reference
         with depth-1 stmt pushes — find the firing whose nInc landed at the
         wrong depth.
      4. Likely fix: either restructure the `nPush() *if_cmd ... nPop()` branch
         at line 625 to correctly account for inner finalize timing, or change
         the inner if's `Finalize_if`/`Finalize_if_else` action timing so its
         IncCounter loop fires inside the right frame.
      5. Verify on /tmp/redux.sc (expect diff=0), then /tmp/wraptest.sc, then
         full beauty.sc.  Gate PASS=50 FAIL=0.

      **Reproducible repros saved (paths only, contents in commit history):**

      ```
      /tmp/redux.sc       # ~20 lines, diff=3 — fastest repro
      /tmp/wraptest.sc    # ~38 lines, diff=1 — single off-by-one
      ```

- [x] **Step SC-6c:** `tree_equal` against existing frontend returns true. Both trees
      execute identically under `--interp`.  **DONE session 8 (2026-05-06): beauty.sc
      produces 1148/1148 stmts, byte-identical to oracle after normalization.
      corpus @ 7a17ff0. Gate PASS=50 FAIL=0.**
- **Sibling LANG rung:** SC-final / `GOAL-SNOCONE-IN-SNOCONE` SS-N.
- **Gate:** beauty.sc round-trips.

### PARSER-SC-7 — augmented assign (`+=` `-=` `*=` `/=` `^=`) ✅ DONE (PASS=55)

Token definitions already existed. Added `reduce_augmented(op)` / `Reduce_augmented(op)`
helpers and five new FENCE branches in `Expr0`. `reduce_augmented` pops rhs and lhs,
pushes `E_ASSIGN(lhs, Tree(op, lhs, rhs))`. Tree nodes are immutable value semantics;
sharing lhs in two child positions is safe (mirrors `sc_clone_expr_simple` in C frontend).
`Reduce_augmented` uses EVAL to embed the op string into the deferred-call pattern.
corpus @ `10e7c0c`. Gate: PASS=55 FAIL=0 (was 50).

- [x] Add `Expr0` FENCE branches for each augmented-assign token: `$'+=' *Expr0 Reduce_augmented(E_ADD)` etc.
- [x] Add `reduce_augmented(op)` / `Reduce_augmented(op)` helpers that build `E_ASSIGN(lhs, E_op(lhs, rhs))`.
- [x] Fixtures: `augmented_add`, `augmented_sub`, `augmented_mul`, `augmented_div`, `augmented_pow`.
- **Gate:** PASS=55 FAIL=0 (+5 from SC-6).

### PARSER-SC-8 — `break` and `continue` ✅ DONE (PASS=60)

Added `sc_break_stk` / `sc_continue_stk` front-push colon-separated stacks (same pattern
as `sc_if_nthen_stk`). `push_break/pop_break/top_break_label` and continue counterparts.
`emit_break` / `emit_break_label` / `emit_continue` / `emit_continue_label` helpers.

Key fix: `finalize_while` reads `Ltop`/`Lend` from the stacks (via `top_break_label` /
`top_continue_label`) rather than from the `while_ltop`/`while_lend` globals — this fixes
nested-loop label reuse (same root cause as SC-6c's `if_nthen` global clobber).

`for_head_alloc` allocates `_Lcont` first then `_Lend` (matching oracle order); sets
`sc_for_cont_used=0`. `finalize_for` emits `_Lcont` label before step only when
`sc_for_cont_used != 0`.

Added `$'break'` / `$'continue'` keyword tokens; `break_cmd` / `continue_cmd` productions
wired into `Command`. corpus @ `3420666`. Gate: PASS=60 FAIL=0 (was 55).

- [x] Add `sc_break_stk` / `sc_continue_stk` string stacks; push targets in `while_cmd`, `do_cmd`, `for_cmd` after label alloc; pop after finalize.
- [x] Add `break_cmd` / `continue_cmd` productions emitting goto to top of respective stacks.
- [x] Labeled forms: `break label;` / `continue label;` emit goto named label directly.
- [x] Fixtures: `break_while`, `continue_while`, `break_for`, `continue_for`, `break_nested`.
- **Gate:** PASS=60 FAIL=0 (+5 from SC-7).

### PARSER-SC-9 — `struct` definition ✅ DONE (PASS=63, session 10, 2026-05-07)

`snocone_parse.y`: `T_STRUCT T_IDENT T_LBRACE struct_field_list T_RBRACE` lowers to
a `DATA(...)` call (program-defined data type). Fields are comma-separated identifiers
inside braces.

- [x] Add `$'struct'` keyword token; add `struct_cmd` production using `save_struct_field_first`/`save_struct_field_rest` helpers (mirrors param_first/param_rest). `Emit_struct()` uses `epsilon . thx . *emit_struct()` — reads `cur_struct_name` and `sc_struct_fields` as globals at match time (no EVAL embedding).
- [x] `struct_field_list`: `struct_field_first ARBNO(struct_field_rest) | epsilon` — accumulates into `sc_struct_fields` global.
- [x] Emit `(STMT :subj (E_FNC DATA (E_QLIT "name(f1,f2,...)")))` for non-empty; `"name()"` for empty.
- [x] Handle empty body `struct T {}` via `| epsilon` in `struct_field_list`.
- [x] Fixtures: `struct_simple`, `struct_fields`, `struct_empty`. corpus @ (see commit).
- **Gate:** PASS=63 FAIL=0 (+3 from SC-8).

### PARSER-SC-10 — `switch` / `case` / `default` ✅ DONE (PASS=67, session 11, 2026-05-07)

`snocone_parse.y`: `T_SWITCH T_LPAREN expr0 T_RPAREN` followed by case clauses.
Each `case val:` lowers to a conditional branch; `default:` is unconditional.
Allocate `Lswitch_end` as break target (SC-8's break stack).

- [x] Add `$'switch'`/`$'case'`/`$'default'` keyword tokens.
- [x] `switch_head_alloc()`: allocates `_Lswitch_t`, `_Lend`, `_Ldefault` labels (in that order), emits `tmp=disc` stmt to outer frame, pushes `_Lend` to break stack.
- [x] `switch_case_label()`: pops case value FIRST (before implicit-break push), stores `(label, value)` in `sc_sw_cases[]` array, emits case label pad, tracks `sc_sw_last_body_n` for implicit-break detection.
- [x] `switch_default_label()`: emits `_Ldefault` label pad, records default entry with null value.
- [x] `finalize_switch()`: builds dispatch chain (IDENT probes + catchall goto), pushes dispatch then body then `_Lend` — `tmp=disc` already on outer frame from `switch_head_alloc`.
- [x] Implicit break: emitted by `switch_case_label`/`switch_default_label` when previous case body was non-empty (`nTop() != sc_sw_last_body_n`).
- [x] Explicit `break;` reuses SC-8's break_cmd — produces double goto (matches oracle).
- [x] Fixtures: `switch_simple`, `switch_default`, `switch_fallthrough`, `switch_break`.
- **Gate:** PASS=67 FAIL=0 (+4 from SC-9).

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
PARSER-SC-INFRA-3 ✅ PARSER-SC-3 ✅ PARSER-SC-4 ✅ PARSER-SC-5 ✅
PARSER-SC-6 ✅ — PASS=50 FAIL=0; beauty.sc 1148/1148 byte-identical.
PARSER-SC-7 ✅ — PASS=55 FAIL=0; augmented assign (+= -= *= /= ^=).
PARSER-SC-8 ✅ — PASS=60 FAIL=0; break/continue with loop-label stacks.
PARSER-SC-9 ✅ — PASS=63 FAIL=0; struct definition → DATA() call.
PARSER-SC-10 ✅ — PASS=67 FAIL=0; switch/case/default.

🏁 GOAL COMPLETE. All rungs done. Gate: PASS=67 FAIL=0. corpus @ 860c823.**

### SC-6c-bug + SC-6c session 2026-05-06 (session 8) — LANDED; PARSER-SC-6 CLOSED

**Root cause (confirmed by instrumentation):** `if_nthen` and `if_nelse` are global
variables. When the outer `if_cmd`'s else-if branch uses `nPush() *if_cmd ... nPop()`,
the recursive `*if_cmd` also calls `Body('if_nthen')` — overwriting the `if_nthen` value
saved by the outer then-body. The outer `finalize_if_else` then reads the clobbered
`if_nthen` (e.g. 1 instead of 8), so `pop_body` under-pops the then-body stmts,
stranding them on the data stack.

Previous hypothesis (previous sessions) was counter-frame depth error. Actual cause
is simpler: shared global name collision under recursion.

**Fix:** `save_if_nthen()` / `restore_if_nthen()` push/pop `if_nthen` onto a
front-push colon-separated string stack `sc_if_nthen_stk` (no ARB — uses
`SPAN('0123456789') . top (':' REM . rest | '')` for O(1) pop). The else-if branch:
```
| Save_if_nthen() nPush() *if_cmd Save_nbody('if_nelse') nPop() Restore_if_nthen()
```
Encounter order ensures save fires before inner `*if_cmd` dot-actions (which clobber
`if_nthen`) and restore fires before `Finalize_if_else` reads `$if_nthen`. Correct for
arbitrary nesting depth.

**corpus @ 7a17ff0.** Smoke PASS=5, parser PASS=50. beauty.sc: 1148/1148, byte-identical.

### SC-6c-bug session 2026-05-06 (session 7) — bug isolated to 20-line repro; two-stack instrumentation refines diagnosis

**Approach this session — two-stack audit per Lon's hint:** instrumented BOTH
the data stack (`Push`/`Pop` in `stack.sc`) AND the counter stack
(`PushCounter`/`PopCounter`/`IncCounter` in `counter.sc`) with frame-depth
tracking, plus per-finalize push/inc trackers in `parser_snocone.sc`.

**Key new evidence:**

1. **STMT-tagged Push at depth=1: 1147** (one short of expected 1148).
2. **IncCounter at depth=1: 1147** (matches what `reduce_prim` reads via
   `TopCounter`).
3. STMT pushes at depths 2-7 occur normally (983 + 737 + 272 + 39 + 22 + 11)
   — these are body STMTs popped by `pop_body` and re-pushed at outer frames.
4. **First STMT push at depth 1 happens at counter=1** (FULLSCAN's nInc fires
   correctly).  Every depth-1 STMT push lines up with monotonic
   IncCounter(N+1)→Push(N+1) ordering.  **No corruption mid-stream.**
5. Per-finalize push/inc deltas all balance on paper:
   `outer_nInc + finalize_inc == finalize_pushes` for every construct.

**The missing stmt is being pushed at depth ≥ 2 instead of depth 1**, OR
equivalently, **one IncCounter that should fire at depth = 1 fires at depth
≥ 2 instead**.  Frame-depth counting confirms: 3211 total STMT pushes across
all depths, but only 1147 land at depth 1.

**Bug isolation:**

Bisection on synthetic `head -156 + lines 163-N + close` shows the bug
appears only when the `pp` function's `Stmt` branch (beauty.sc lines 200-237)
is included.  That branch contains a deeply-nested if + `else if (DIFFER(ppAsgn))`
+ inner ifs with assignment statements.

Two repros saved (paths only, see commit history for content):
- `/tmp/wraptest.sc` — 38 lines, diff=1
- `/tmp/redux.sc` — 20 lines, diff=3 (multi off-by-ones)

**Architectural suspicion (next session start point):**

Bug is structural in the if-else-if recursion path at line 625 of
`parser_snocone.sc`:

```
| nPush() *if_cmd Save_nbody('if_nelse') nPop()
```

When the inner `*if_cmd`'s body contains another nested if-else-if (multi-
level cascade), some `IncCounter` call inside an inner finalize lands in the
OUTER `nPush()` frame instead of the INNERMOST frame.  Pattern action timing
(when each `*finalize_X` dot-action fires during recursion) interacts with
how `nPush()`/`nPop()` boundaries are crossed.  Not yet confirmed — needs
re-instrumented per-construct firing trace logging
`(construct, depth_at_firing, frame_id)`.

**Files touched this session — ALL REVERTED before push** per RULES.md
"Diagnostic patches are diagnostic — never commit them":
- `corpus/SCRIP/parser_snocone.sc` — instrumented every
  `finalize_*`, `emit_*`, `decompose_stmt`; dump output at end of driver
- `corpus/SCRIP/counter.sc` — `dbg_frame_depth` + per-frame
  IncCounter tracking
- `corpus/SCRIP/stack.sc` — depth-1 Push/Pop counters + STMT-tag
  filtering

Gates remain smoke PASS=5 / parser PASS=50.

### SC-6b-bug session 2026-05-06 (session 5) — reduce_prim fix LANDED; PASS=50 FAIL=0

**Fix:** one-line change at `parser_snocone.sc:654`:
```
(E_Parse & 'nTop()')  →  reduce_prim(E_Parse)
```
`reduce_prim(tag)` is defined in `semantic.sc` as
`EVAL("epsilon . *ReducePrim(" tag ")")`.  At match time `ReducePrim(tag)`
calls `TopCounter()` as its very first substantive operation — before any
stack pops — guaranteeing it reads the fully-incremented count.

**Verification:** 5-stmt simple input: byte-identical to oracle, all 5 stmts
present.  `head -10 beauty.sc`: byte-identical to oracle, `&FULLSCAN = 1`
correctly first.  Gate PASS=50 FAIL=0, smoke PASS=5 FAIL=0.

**Remaining:** SC-6b-bug-segfault (SIGSEGV at intermediate beauty.sc sizes)
and SC-6c (full beauty.sc parse still times out at 60s — performance issue,
not correctness).

### SC-6b-bug session 2026-05-06 (session 4) — diagnosis refined: parser bug, not scrip bug

Continuing investigation of the first-stmt-drop symptom from session 3.
Original session 3 hypothesis was that this is a scrip executable
memory-safety bug (SIGSEGV / heap corruption at intermediate sizes
suggested it).  **Session 4 evidence reverses this:** the first-stmt drop
on the full file is a deterministic parser_snocone.sc grammar bug.

Key experiments this session:
1. Prepend N simple stmts to beauty.sc, run parser, see what's dropped:
   - With 1 prefix `aa = 11;`: `aa` dropped, `&FULLSCAN` first in output.
   - With 2 prefix: `aa` dropped, `bb` is first.
   - With 10 prefix: `pp1` dropped, `pp2..pp10` then `&FULLSCAN` come through.
   → Conclusion: exactly the first stmt is dropped, regardless of content.
2. Instrumenting the driver's TDump loop with `OUTPUT = 'n_kids=' n(ptree)`:
   - Full beauty.sc: `n_kids=1147` (oracle has 1148 stmts).
   - `child[1]` (the FIRST surviving child) carries oracle's stmt #2.
   → Conclusion: the parse tree's children list is short by 1; the first
     pushed STMT (oldest, bottom-of-stack) is being left on the tree stack
     after `Reduce(E_Parse, nTop())` pops `nTop()` items.
3. Across `--interp`, `--interp`, `--run`: identical symptom — rules
   out backend-specific issues.
4. With 5000 simple stmts: works perfectly, all 5000 parsed, first present.
   Bug requires SPECIFIC complex content (function definitions + if-cascades
   like beauty.sc's `pp` function), not just size.

**Mechanism:** Compiland uses `(E_Parse & 'nTop()')` — OPSYN-dispatched to
`reduce(E_Parse, 'nTop()')` where the second arg is a STRING, embedding
`nTop()` inside the EVAL'd pattern's `.`-action body. `Reduce(t, n)` pops
`n` items from the tree stack at match time.  If `n` is one short, the
first-pushed item is stranded on the stack while the top `n` items are
popped into `c[1..n]`.  Symptom matches.

**Why `nTop()` returns one less than IncCounter count on large inputs:
not yet pinpointed.** Three hypotheses (in goal file Step SC-6b-bug above);
the most actionable is: replace `(E_Parse & 'nTop()')` with
`reduce_prim('E_Parse')` from `ShiftReduce.sc` — `ReducePrim(tag)` reads
`TopCounter()` internally as its first operation, eliminating any
EVAL/binding-time concerns about when `nTop()` evaluates.

**Files left unchanged this session.** The `*if_cmd` fix and three new
fixtures from session 3 remain in place.  Instrumentation added to
parser_snocone.sc during diagnosis was reverted before push.

**Separate issue from SC-6b-bug — SIGSEGV / heap corruption at intermediate
file sizes (`head -198..-300 beauty.sc`):** distinct from the first-stmt
drop; those break the parse entirely (no output) rather than producing a
short-by-one tree.  Filed in goal as `SC-6b-bug-segfault` to investigate
after SC-6b-bug lands.

### SC-6b session 2026-05-06 (session 3) — `*if_cmd` recursion fix; SC-6b CLOSED

**Diff (B) FIXED — one-character `*if_cmd` addition.** Previous diagnosis
(post-match DOT firing order) was wrong; the actual cause was that the bare
`if_cmd` reference in the else-if grammar branch wasn't recursing.  Per
SPITBOL Manual Ch 9, recursive pattern self-references must use `*`.  Without
`*`, the pattern engine captures the OLD value of `if_cmd` (null) at build
time, so the inline else-if matches epsilon, the outer Finalize_if_else
fires with empty else body, and `ARBNO(*Command)` then re-matches the inner
if at top level — producing the apparent "label-ordering" bug.

Fix: `parser_snocone.sc` line 594, `if_cmd` → `*if_cmd`.  Gate PASS=50 FAIL=0
with three new fixtures (if_else_if, if_else_if_else_if, if_else_if_else),
all byte-identical to oracle.  beauty.sc 1148/1148 stmts; the previous
structural diff in 2 if-else-if instances is gone.

**SC-6b-bug FILED (new):** scrip executable stability when parser runs on
full beauty.sc.  After Diff (B) fix, the only remaining diff with oracle is
the very first stmt `&FULLSCAN = 1;` being silently dropped from output.
Bisecting on `head -N beauty.sc` shows non-deterministic output
(empty/corrupted/SIGSEGV/heap-corruption) at intermediate N values.
Symptoms vary with input size in a way no Snocone-level grammar could control —
canonical scrip runtime memory-safety bug.  See Step SC-6b-bug for full
characterization.

**Methodology this session:** read SPITBOL Manual chapters 6, 7, 9, 18
(pattern matching tutorial + reference algorithm) end-to-end.  The
`.`/`$`/`*`/`~` operator semantics and the "recursive patterns require `*`"
rule were the keys to spotting Diff (B)'s real cause.  Lon supplied the
SPITBOL Manual PDF this session; the prior diagnosis missed because the
firing-order story was plausible but the actual cause was upstream of
firing-order entirely.

### SC-6b session 2026-05-06 (session 2) — flatten_arith DONE; if-else-if label ordering diagnosed

**Diff (A) FIXED: `flatten_arith` post-parse step.** Added to `parser_snocone.sc` (corpus @ 05a1bea):
- `sc_flatten_ops = ' E_ADD  E_SUB  E_MUL  E_DIV '`
- `flatten_arith(x)`: bottom-up recursive. Merges binary node into n-ary when child[2].tag == self.tag.
  Mirrors C-frontend `expr_binary_flatten` from PARSER-FAMILY-LOOP iter#9.
- Called from `decompose_stmt` immediately after `top = Pop()`.
- New fixture `arith_sub_nary.sc`: `x = a - b - c;` → `E_SUB(a,b,c)`. PASS.
- Gate: PASS=47 FAIL=0 (was 46).

**Diff (B) DIAGNOSED — if-else-if label ordering, NOT YET FIXED.** See Step SC-6b above.
Post-match DOT action ordering: outer `Finalize_if_else` fires before inner `Finalize_if`
in if-else-if chains, causing outer Lend label to appear before else body instead of after.
Two instances in beauty.sc. `if_else_if` fixture withheld from gate until fixed.

**beauty.sc status:** 1148/1148 stmts, oracle count matches exactly. 1 structural diff remains.

### SC-6b session 2026-05-06 — Lon whitespace refactor landed; PASS=46 FAIL=0

Lon uploaded a major rewrite of `parser_snocone.sc` with a new unified
whitespace/token design. Six bugs found and fixed during gate recovery
(PASS=0 → PASS=46 FAIL=0):

1. **Missing E_* constants** — `E_PLS`, `E_BANG`, `E_PCT`, `E_SLASH`,
   `E_POUND` added. `E_PLUS` ref fixed to `E_PLS`; four `E_XXX` placeholders
   replaced with proper names.
2. **`push_qlit` stale capture var** — used old `strbody`; changed to `token`
   to match Lon's new uniform-capture design.
3. **`push_ilit` self-assign typo** — body assigned to `push_flit` instead of
   `push_ilit`.
4. **Missing `Push_ilit()` build-time wrapper** — `Push_flit` existed but
   `Push_ilit` was absent. This was the proximate cause of Error 5 /
   PASS=0: every fixture hit an undefined-function call at match time.
5. **Bracket/brace whitespace policy settled** with Lon:
   - `(` and `[` — no leading ws (preserves `f(a)` vs `f (a)`, `a[i]` vs `a [i]`).
   - `)` `}` `]` `{` — Gray on both sides.
6. **Keyword tokens bake trailing Gray** — all 10 keywords now defined as
   `$' ' Id $ tx *IDENT(tx, 'kw') $' '`. This absorbed the gap between
   keywords and following expressions/identifiers (e.g. `return a;` now
   matches `return_cmd` without an explicit `$'  '` at the call site).
   All 6 redundant `$'  '` after keyword tokens in productions removed.

No SCRIP executable bugs found this session.

**Next:** SC-6b beauty.sc crosscheck — Lon to decide crosscheck target
(beauty.sc direct, or a simpler program without continuation markers).

### SC-6b session 2026-05-05 — structural work landed, beauty.sc crosscheck blocked

Changes landed this session (gate PASS=46 FAIL=0 throughout):

**Expression tier ladder restructured to match beauty.sno exactly (Expr0–Expr17):**
- Added `Expr2` (binary `&`, right-assoc), wired `Expr1 → Expr2 → Expr3`.
- Added `Expr7` (binary `#`), `Expr8` (binary `/`), `Expr10` (binary `%`) — split out of old `Expr5a`/`Expr6`.
- Added `Expr13` (binary `~`, right-assoc) between Expr12 and Expr14.
- Added full `Expr14` unary-prefix tier (from beauty.sno): `@ ~ + - * $ . ! % / #`.
- **Snocone-specific Expr14 restriction:** Removed `= | & ?` from Expr14 unary prefix.
  These are binary-only operators in Snocone. Their presence caused `x = (expr)` to parse
  as `x` concatenated with `=(expr)` at the X4 level (unary `=` grabbed the binary `=`).
  This is a language difference from SNOBOL4 that beauty.sno cannot encode.
- `Expr12` now uses `$'$' *Expr12` / `$'.' *Expr12` right-recursive per beauty.sno.
- `Expr11` now accepts `$'^' | $'!' | $'**'` per beauty.sno.
- Removed custom `Expr5a` tier; `Expr5` now has `$'@'` cursor + comparison operators per beauty.sno.
- `Expr6` now wired to `Expr7` (was `Expr9`), FENCE-based per beauty.sno (was ARBNO).
- `Expr15/Expr16` restructured per beauty.sno: `Expr16 = nInc() $'[' *ExprList $']' FENCE(*Expr16|epsilon)`.
- Added `ExprList`/`XList` patterns (used by Expr16 and Expr17 call args).
- Added `E_INDEX` constant alias for `E_IDX`; added `r_nTopP1` constant.
- **Bug fix:** `$'['` was `$' ' '[' $' '` (whitespace on both sides) — subscript `a[i]`
  failed because no space before `[`. Fixed to `'[' $' '` (no leading ws) per beauty.sno.

**beauty.sc crosscheck blocker:**
The `White = SPAN(' ' tab nl)` definition (newline is whitespace, per Lon) means that
`+` continuation markers at the start of continuation lines in beauty.sc are parsed as
the unary `+` operator (Expr14), not as whitespace continuation markers. This causes
multi-line expressions in beauty.sc (e.g. `Real = ( SPAN(digits)\n+  ...\n )`) to parse
differently from the oracle. The oracle (C frontend) handles `+` continuation at the
lexer level; our pattern parser sees `+` as an operator.

**Next session options:**
(a) Accept that beauty.sc is not a valid crosscheck target due to `+` continuation markers,
    and use a different Snocone program (without continuation markers) for SC-6b crosscheck.
(b) Pre-process the input to strip `+`/`.` continuation markers before parsing.
(c) Add a special `start-of-line +` recognition that treats line-leading `+`/`.` as
    whitespace continuation (not operators) — but this requires cursor position awareness.

Lon decides. Gate remains PASS=46 FAIL=0.

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

IR-side companion fix STILL PENDING — the gate uses `--interp`, so the
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
