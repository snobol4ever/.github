# GOAL-PARSER-ICON.md — PARSER-ICON pattern-based frontend in Snocone

**Repo:** corpus+one4all
**Branch:** `parser` (one4all only — `corpus` and `.github` stay on `main`)
**Sibling ladder:** `GOAL-LANG-ICON.md`. The existing Icon frontend
(`src/frontend/icon/`) is the in-process oracle.

**Done when:** A Snocone program `parser_icon.sc` reads Icon source, runs
one `Compiland` PATTERN that builds the canonical IR tree, and for every
test program in the rung corpus
`tree_equal(existing_frontend_tree, parser_icon_tree)` returns true. Where
a `.ref` file exists, executing both trees through the IR interpreter
produces byte-identical output.

---

## Cross-pollination

All six PARSER-* parsers share `Compiland`/`Shift`/`Reduce`/`Push`/`Pop`/`Top`/
`tree`/`TDump`/`stack` from `corpus/programs/scrip/`. Bug fixes there
benefit all six.  Cross-PARSER style (naming, `White`/`Gray`, `$'name'`
tokens, shift/reduce, n-ary counters, identifier rules, 120-col layout)
is canonical in `GOAL-PARSER-SNOBOL4.md ## Style Guidelines for
parser_*.sc` — read it before authoring or modifying any `parser_*.sc`.

Icon shares broker mechanics with SNOBOL4 (BB_SCAN for pattern-match,
BB_PUMP for generators) per `GOAL-LANG-ICON`. Tree shape for Icon's
goal-directed expressions is the differentiator.  PAT-IC's later rungs
wait for the LANG ladder to mature features upstream.

---

## Session Setup

```bash
( cd /home/claude/one4all && git fetch origin parser 2>/dev/null; git checkout parser 2>/dev/null || git checkout -b parser origin/parser 2>/dev/null || git checkout -b parser )
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
```

Gate after setup:
```bash
bash /home/claude/one4all/scripts/test_smoke_icon.sh
bash /home/claude/one4all/scripts/test_parser_icon.sh
```

---

## Architecture reminder

PAT runs `parser_icon.sc` (which loads the shared SC library from
`corpus/programs/scrip/`) against an `.icn` source — produces IR tree
t2 via `Compiland`; the existing frontend produces t1 via `--dump-ir`.
Both compared via the gate script's normalized text diff.  No
subprocesses, no temp files, no on-disk diffs.

Shared SC library: `tree.sc  stack.sc  counter.sc  ShiftReduce.sc
semantic.sc  qize.sc  gen.sc  tdump.sc  assign.sc`.

Compiland spine:
```
Compiland = nPush() ARBNO( nInc() ws_opt Proc ws_opt ) reduce("'Parse'", 'nTop()') nPop();
```

Icon-specific note: Icon's expression model is goal-directed — every
expression can succeed or fail and many can generate multiple values.
The IR tree carries this in the node tags (`SuccFail`, `AltGen`,
`Bound`).  Token-level the language looks ALGOL-like; the semantics
divergence is in how trees are interpreted, not how they are shaped.

---

## Style guidelines — derived from beauty.sno / beauty.sc

The reference for `parser_<lang>.sc` style is the beauty pair:
`corpus/programs/snobol4/demo/beauty/beauty.sno` and
`corpus/programs/snocone/demo/beauty/beauty.sc`.  Read both
end-to-end before authoring or refactoring a PARSER-* file.  Every
guideline below is in active use there — they are not prescriptive
in the abstract, they are descriptive of the working artifact.

### Whitespace tokens — define once, never reference Gray/White directly

```snocone
Gray  = *White | epsilon;
White = SPAN(' ' tab) FENCE(...) | nl ('+' | '.') FENCE(...);
```

After these are defined, **the main grammar never names `Gray` or
`White` directly**.  All whitespace handling rides inside the
operator/bracket/keyword tokens below.  If the grammar mentions
`*White` or `*Gray` outside these token definitions, that's a smell
— factor it into a `$'op'` token or use `$' '` / `$'  '`.

### Operator and special-character tokens — `$'op'` form

```snocone
$'='  = *White '=' *White;       // binary operators: White on both sides
$'**' = *White '**' *White;
$',' = *Gray ',' *Gray;          // comma uses Gray (allows nl-continuation)
$'(' = '(' *Gray;                // open bracket: Gray after only
$')' = *Gray ')';                // close bracket: Gray before only
```

Operator tokens use `*White` symmetric.  Comma uses `*Gray` symmetric.
Open brackets get `*Gray` after; close brackets get `*Gray` before.
The pattern of which side gets what is fixed — copy it.

### Reserved-word tokens — `$'kw'` form

Snocone reserved words and language keywords use the same `$'name'`
syntax: `$'if'`, `$'then'`, `$'procedure'`, `$'end'`.  Define each
keyword token with leading optional whitespace baked in; trailing
required-whitespace stays explicit at each call site (varies by use).

### Identifier-shaped tokens that aren't Snocone reserved words

Use a plain identifier and prefix with `$' '` (optional whitespace):

```snocone
S = $' ' 'S';       // not Snocone-reserved, normal identifier
F = $' ' 'F';
```

### Invisible-whitespace shortcuts — `$' '` and `$'  '`

```snocone
$' '  = ws_opt;     // ONE space identifier  → optional whitespace
$'  ' = ws_run;     // TWO space identifier  → required whitespace
```

These let keyword and operator definitions read as the literal
source they match.  `$'if' $'  ' Cond` reads correctly: `if` then
required space then condition.

### Tree-builder shortcuts — OPSYN'd `~` and `&`

beauty's tree-build form is:

```snocone
primitive . tx . *Func(literal, tx)         // raw form
primitive . tx Func(literal, "tx")          // EVAL-friendly form
```

After OPSYN registers `~` (Shift) and `&` (Reduce) as binary
operators, the `parser_*.sc` files use the short forms exclusively:

```snocone
*Integer ~ 'Integer'              // shift: dot-capture into stack as 'Integer'
("'+'" & 2)                       // reduce: pop 2, push tree('+', _, 2, kids)
("'Parse'" & 'nTop()')            // reduce with frame-counted children
```

`EVAL` is used internally by the OPSYN'd reduce to evaluate the
count expression.  This is what makes `'nTop()'` and
`'*(GT(nTop(),1) nTop())'` work as the right-hand operand.

`r_nTop = '*(GT(nTop(),1) nTop())'` is the canonical "n-ary collector
with single-child unwrap" reduce-count expression.  When only one
item is on the frame, the EVAL fails and reduce silently leaves the
lone tree alone — verified with isolated probe.  This IS the
unwrap for E_SEQ_EXPR (`(expr)` and `{expr}`).

### Counter machinery — `nPush()`/`nInc()`/`nPop()`

Sub-repetition counts for n-ary tree children ride on a counter
stack.  `nPush()` opens a frame, `nInc()` bumps the current frame's
count by one (called inside the repetition body), `nPop()` closes.
The reduce uses `'nTop()'` to read the current frame's count as
the child count.  This is how `Parse`, alternation `|`, comma list,
and concat list all collect a variable number of children.

### IR / AST node names — `E_*` from `EXPR_t`

Every reduce-tag string is the corresponding `E_*` enumerator name
from `src/ir/ir.h:EXPR_t`.  Examples: `E_VAR`, `E_ILIT`, `E_QLIT`,
`E_ASSIGN`, `E_AUGOP`, `E_FNC`, `E_SEQ_EXPR`, `E_MNS`, `E_POW`.
The PARSER-IC convention defines `r_TAG = sq 'E_TAG' sq;` constants
once at the top of `parser_icon.sc` and uses `r_TAG` everywhere —
the EVAL-quoted form `'E_TAG'` is what `&` expects on the right.

### No identifiers starting with underscore

`_name` is reserved for generated code.  All hand-written
identifiers in `parser_*.sc` start with a letter.

### Variable / function naming

- **Variables** start with lowercase, snake_case: `id_pat`, `ws_opt`,
  `nl_one`, `cond_tree`.
- **Functions** start with uppercase, then snake_case (or mixed):
  `Push_list`, `Compiland`, `nPush`, `TDump`.
- **Reduce-tag constants** start with `r_`: `r_FNC`, `r_POW`.
- **Shift-tag constants** start with `s_`: `s_QLIT`, `s_ILIT`, `s_VAR`.

### One-statement bodies — no curly braces

```snocone
if (cond) statement;              // YES
if (cond) { statement; }          // NO
```

Reserve `{ ... }` for multi-statement bodies only.

### Comment dividers, not blank lines

Use 120-character `/*===*/` for major section breaks and `/*---*/`
for minor.  Do not use blank lines for visual separation.

```snocone
/*=====================================================================*/
//  Major section
/*=====================================================================*/
/*---------------------------------------------------------------------*/
//  Minor subsection
/*---------------------------------------------------------------------*/
```

### Horizontal density; balanced multi-line wrap

Pack each line up to 120 columns.  When a sequence does not fit,
wrap with constant 2-space indention, vertically aligning binary
operators and parentheses:

```snocone
Expr10  = (   $' ' '-' *Expr10 (r_MNS         & 1)
          |   $' ' '+' *Expr10 (r_PLS         & 1)
          |   $' ' '~' *Expr10 (r_CSET_COMPL  & 1)
          |   *Expr11
          );
```

### Token names track the official language specification

Keyword names, operator spellings, and grammar production names
mirror the upstream reference grammar — for Icon, `icon-sp.ebnf`
(1-to-1 with public-domain `gtownsend/icon` `src/h/grammar.h`).
Do not invent names where the upstream provides one.

---

## Canonical Snocone nonterminal names

Source of truth: `corpus/programs/ebnf/icon-sp.ebnf` (1-to-1 with
upstream gtownsend/icon `src/h/grammar.h`, public domain).
Convention: take the EBNF nonterminal name, capitalize the first
letter; multi-word names stay solid (`Prochead` not `ProcHead`).
Productions are numbered by precedence (`expr1` through `expr11`) —
not named after operator class.

| EBNF nonterminal | PAT-IC pattern  | Notes |
|------------------|-----------------|-------|
| `program`        | `Program`       | Top of grammar. |
| `decls` / `decl` | `Decls` / `Decl`| Declarations list. |
| `proc`           | `Proc`          | `procedure ... end`. |
| `prochead`       | `Prochead`      | Procedure header. |
| `procbody`       | `Procbody`      | Procedure body. |
| `record` / `global` / `link` / `invocable` | `Record`/`Global`/`Link`/`Invocable` | Top-level decls. |
| `expr`           | `Expr`          | Conjunction (top of expr tower). |
| `expr1a`         | `Expr1a`        | Scan (`?`). |
| `expr1`          | `Expr1`         | Assignment + augmented assigns. |
| `expr2`          | `Expr2`         | `to ... by ...`. |
| `expr3`          | `Expr3`         | Alternation `\|`. |
| `expr4`          | `Expr4`         | Comparison (numeric, string, equiv). |
| `expr5`          | `Expr5`         | Concat (`\|\|`, `\|\|\|`). |
| `expr6`          | `Expr6`         | Additive (`+`, `-`, `++`, `--`). |
| `expr7`          | `Expr7`         | Multiplicative (`*`, `/`, `%`, `**`). |
| `expr8`          | `Expr8`         | Power (`^`). |
| `expr9`          | `Expr9`         | Limit / activation / apply (`\\`, `@`, `!`). |
| `expr10`         | `Expr10`        | Unary prefix. |
| `expr11`         | `Expr11`        | Primary (literals, control structures, postfix). |
| `nexpr`          | `Nexpr`         | Possibly-empty expression. |
| `literal`        | `Literal`       | INTLIT / REALLIT / STRINGLIT / CSETLIT. |
| `if`             | `If`            | `if .. then .. else ..`. |
| `while`/`until`/`every`/`repeat` | `While`/`Until`/`Every`/`Repeat` | Loops. |
| `case` / `caselist` / `cclause`  | `Case` / `Caselist` / `Cclause`   | Case. |
| `section` / `sectop`             | `Section` / `Sectop`              | String section. |
| `exprlist` / `pdcolist`          | `Exprlist` / `Pdcolist`           | Argument lists. |
| `compound`                       | `Compound`                        | `{ nexpr; nexpr; ... }`. |
| `arglist` / `idlist` / `fldlist` | `Arglist` / `Idlist` / `Fldlist`  | Identifier lists. |
| `locals` / `retention` / `initial`| `Locals` / `Retention` / `Initial`| Procedure preambles. |

LL(1) decomposition: Snocone patterns cannot left-recurse; canonical
grammar is left-recursive throughout.  Each `Exprn` becomes
`Exprn = Exprn_plus_one ARBNO(Exprn_tail)` with a separately-named
tail pattern (deferred actions inside `ARBNO(...)` inline don't fire
reliably; `ARBNO(NamedPattern)` does).  See JCON's `tran/parse.icn`
in `corpus/programs/ebnf/icon-references/` for the recursive-descent
shape PAT-IC mirrors.

---

## Closed rungs

| Rung | Gate | Notes |
|------|------|-------|
| **PARSER-IC-0**       — atom                          | PASS=3  | identifier / integer / string atoms; in-process crosscheck driver landed |
| **PARSER-IC-1**       — assignment (`x := expr`)      | PASS=8  | 5 NEW assign fixtures (assign_int/str/var/mixed/seq) |
| **PARSER-IC-2**       — `write(expr)` + `+ - * /`     | PASS=14 | 6 NEW (write_str/int/var, arith_add/sub, write_arith) |
| **PARSER-IC-INFRA-1** — canonical Icon BNF in corpus  | files   | `icon-grammar.h` (verbatim public-domain), `icon-sp.ebnf` (project dialect), `icon-no.ebnf`, `icon-references/` (JCON parse.icn cross-corroboration), `README.md` |
| **PARSER-IC-INFRA-2** — refactor to canonical names + Compiland-driven loop | PASS=14 | Pattern names mirror `icon-sp.ebnf` (Program / Proc / Prochead / Procbody / Stmt / Expr / Expr1 / Expr2 / Expr6 / Expr7 / Expr11 / etc.).  Goto state-machine main loop replaced by `Compiland` PATTERN driving `ARBNO(Proc)`.  LL(1) decomposition: `Exprn = Exprn_higher ARBNO(Exprn_tail)`, tail in named pattern.  Per-level lhs vars (`_e1lhs`, `_e6lhs`, `_e7lhs`) avoid clobbering across the recursive call chain. |
| **PARSER-IC-3**       — control flow + comparison ops | PASS=20 | Added `Expr4`/`Expr4tail` (`= ~= < <= > >=`); `If`/`While` in `Expr11` (else inline-optional to dodge double-parse); `Expr1` restructured to `id_pat ws_opt ':='`-committed assign branch.  6 NEW fixtures.  **Cross-pollination bug fix in `corpus/programs/scrip/tdump.sc`**: multi-line fallback was guarded by `~(NULL *IDENT(n(x)))` — a no-op (pattern construction can't fail) — so wide trees fell through to `.` leaf branch.  Replaced with `DIFFER(n(x))`; extended branch to mirror TLump's role-slot (`:`-prefix) and internal-node `v(x)` sval emission.  Beauty source `programs/snocone/demo/beauty/TDump.sc` has the same bug; treatment owed under whichever goal owns beauty. |
| **PARSER-IC-4**       — procedure definition + return + variadic invocation | PASS=27 | Generalized `Prochead` to `'procedure' ws_run id_pat ws_opt '(' Arglist ')'`; new `ProcParam`/`ParamRest`/`Arglist` patterns; helpers renamed `start_proc_main`→`start_proc`, `finish_proc_main`→`finish_proc`; new `append_proc_param`.  New `ReturnStmt` at the Stmt level: with-value `'return' ws_run *Expr` first, bare `'return' ws_opt semi_opt` fallback; builds `(E_RETURN [expr])`.  **Variadic invocation** via dedicated `$'@II'` invocation-construction stack (struct `ic_ilink`), parallel to Compiland's stack — required (not a single-slot global) because invocations nest (`write(double(5))`).  7 NEW fixtures (proc_simple/oneparam/twoparam, proc_call_noargs/onearg/twoargs, proc_return). |
| **PARSER-IC-5**       — alternation generators (`expr1 \| expr2`) | PASS=33 | New `Expr3` slot between Expr2 and Expr4 per canonical EBNF.  Existing frontend flattens nested alternations into a single `(E_ALTERNATE a b c d)` — PAT-IC matches via dedicated `$'@AL'` alt-construction stack (struct `ic_alink`).  Single `expr_alt_step(savedLHS)` helper handles both first-`\|` (push fresh E_ALTERNATE) and subsequent `\|`s (append onto top-of-stack) via a `_e3built` flag; `expr_alt_enter`/`expr_alt_finish` save/restore the flag at Expr3 boundaries to support nested alternations.  6 NEW fixtures (alt_two/three/var/str/in_call/arith). |
| **PARSER-IC-6**       — `every [do body]` and `subj ? body` scan | PASS=40 | New `Every` branch in `Expr11` handles both `every gen` (1-child `E_EVERY`) and `every gen do body` (2-child `E_EVERY`) via two helpers `expr_every1`/`expr_every2`; saved generator in `_ic_evgen` to survive body parse.  New `Expr1a` slot between `Expr` and `Expr1` per canonical EBNF handles `subj ? body` building `(E_SCAN subj body)`; subjects saved on dedicated `$'@SC'` link()-stack (struct `ic_sclink`) so nested scans (`a ? b ? c`) don't clobber.  Critical fix: scan body uses `*Expr` (deferred reference) since `Expr` is defined below `Expr1a`; non-deferred reference produced a malformed pattern that silently bailed.  Driver loops rewritten from `goto` to `while` per RULES.md control-flow guidance.  7 NEW fixtures (every_simple/do/alt/novar, scan_simple/var/assign). |
| **PARSER-IC-8a**      — SCRIP grammar fix: binary `~` `&` `#` `%` OPSYN slots | PASS=40 preserved | New `expr5a` tier in `src/frontend/snocone/snocone_parse.y` between comparison (expr5) and additive (expr6).  Each binary OPSYN slot lowers to `E_FNC` with `sval` = operator literal, paralleling how comparison ops (T_EQ→"EQ", T_NE→"NE", etc.) lower today; runtime E_FNC dispatch consults the OPSYN table to find the registered handler.  Lexer already emitted T_2AMP/T_2TILDE/T_2POUND/T_2PERCENT (snocone_lex.c:543, 551, 547, 549) — only the parser needed the rule.  `%type <expr> expr5a` added (line 467).  After regeneration via `regenerate_parser_and_lexer_from_sources.sh` and `build_scrip.sh` rebuild, `'a' ~ 'b'` (after `OPSYN('~','f',2)`) invokes `f('a','b')` correctly.  Compiland in parser_icon.sc converted from `reduce("'Parse'", 'nTop()')` to `("'Parse'" & 'nTop()')` operator form as smoke test of the unblocked path; PASS=40 preserved.  Snocone test suite shows no new regressions (test_smoke_snocone, test_parser_snocone PASS=13, plus all language smoke tests PASS).  Pre-existing C-test breakage in `test/frontend/snocone/test_snocone_parse_a..j.c` (references stale `Program *`/`head` API) is unrelated to this change — verified by stash/repro before commit. |
| **PARSER-IC-7**       — paren `(expr)`/`(e1;e2)` + compound `{...}` primaries + beauty-style `$'op'` pattern-builder refactor | PASS=45 | Two changes in one session.  (a) Style refactor: every `epsilon . *fn(args)` replaced by a named `$'...'` pattern variable per beauty.sc / parser_snocone.sc idiom — `$'|'`/`$':='`/`$'?'`/`$','` op tokens, `$'invoke_arg'`/`$'append_stmt'`/`$'finish_proc'`/etc. side-effect builders, `$'atom_QLIT'`/`$'atom_ILIT'`/`$'atom_VAR'` atom builders, `$'save_eNlhs'`/`$'op_TAG'`/`$'binop_*'` per-tier savers and folds, `$'if2'`/`$'if3'`/`$'while2'`/`$'every1'`/`$'every2'`/`$'assign_id'` control-flow builders, `$'scan_push'`/`$'scan_finish'` scan builders.  PASS=40 preserved through refactor.  (b) IC-7 features: `Paren` and `Compound` primaries via dedicated `$'@SQ'` link()-stack (struct `ic_sqlink`), `ic_seq_push/append/finish` helpers, single-child unwrap matches existing-frontend `parse_block_or_expr`.  5 NEW fixtures: paren_expr/paren_seq/compound_one/compound_two/scan_paren.  corpus@c6e4c2b. |
| **PARSER-IC-8b**      — parser_icon.sc canonical-spine rewrite | PASS=45 preserved | Trees flow through the shared shift/reduce stack.  Binary tiers use `*L $'op' *R (r_TAG & 2)`.  N-ary collectors (alternation Expr3, function call Call, paren-seq Paren, compound Compound) use `nPush() ARBNO(nInc() *X) (r_TAG & 'nTop()' or r_nTop) nPop()` — the `r_nTop = '*(GT(nTop(),1) nTop())'` idiom is what makes single-child unwrap work for E_SEQ_EXPR (when only one item is on the frame, the EVAL fails and reduce silently leaves the lone tree alone — verified with isolated probe).  Atoms use `*P ~ T` operator form, except QLIT (which keeps the `dot-capture + ic_push_qlit()` exception so the string body excludes its quotes — same exception parser_snocone.sc keeps for `sc_push_qlit`).  Statement decomposition collapsed to ONE helper `ic_decompose_proc`: pops the proc-frame's nTop() children, reads pname from `v(child[1])` (the (E_VAR pname) callee shifted by Prochead), rebuilds (E_FNC pname kids), wraps in (STMT :subj ...).  Removed: every `expr_*` parsing-state helper, every `_expr_node` global slot, every `$'@II'`/`$'@AL'`/`$'@SC'`/`$'@SQ'` link()-stack, every `ic_inv_*`/`ic_alt_*`/`ic_scan_*`/`ic_seq_*` parsing-state helper, every `Tree(tag,'',2,L,R)` direct construction outside the one helper.  Net: 871 → 366 lines (−505).  Cross-pollination opportunity: parser_rebus.sc / parser_snobol4.sc owe the same retrofit.  corpus@ef1acd2. |
| **PARSER-IC-9**       — augmented assigns + unary prefix + power | PASS=51 | Three new operator tiers added in canonical-spine style.  (a) **Augmented assigns** at `Expr1`: tokens `$'+:='` `$'-:='` `$'*:='` `$'/:='` defined plus an alternation token `$'augop'` covering them; Expr1 gains a second branch `$'augop' *Expr1 (r_AUGOP & 2)` parallel to the `$':=' *Expr1 (r_ASSIGN & 2)` branch.  Operator literal is intentionally discarded — `--dump-ir` output is `(E_AUGOP lhs rhs)` regardless of which augop appeared in source.  (b) **Unary prefix** at new `Expr10` tier between `Expr11` and `Expr7`: per-op tokens `$'unary-'` `$'unary+'` `$'unary~'` `$'unary\\'` `$'unary!'` `$'unary*'` `$'unary?'` (only leading `$' '`, no required whitespace before operand); each branch is `$'unary-op' *Expr10 (r_TAG & 1)` recursing for stacked unaries; falls through to `*Expr11`.  Reduce tags: `r_MNS` `r_PLS` `r_CSET_COMPL` `r_NONNULL` `r_ITERATE` `r_SIZE` `r_RANDOM`.  (c) **Power** at new `Expr8` tier (right-assoc): `*Expr10 ($'^' *Expr8 (r_POW & 2) | epsilon)`.  `Expr7` retargeted from `*Expr11` to `*Expr8` so the multiplicative tier sits above the new power tier.  6 NEW fixtures: `augop_add` `augop_sub` `unary_minus` `unary_cset_compl` `unary_size` `pow_expr`.  Style: this rung was authored under the new "Style guidelines — derived from beauty.sno / beauty.sc" section added to this Goal file in the same commit (re-reads beauty.sno/beauty.sc, distills naming + horizontal-density + `Gray`/`White`/`$' '`/`$'  '`/`$'op'`/`$'kw'` token conventions). |

---

## Open rungs

### PARSER-IC-10-style — clean up guideline violations in `parser_icon.sc`  ← **next**

The new "Style guidelines" section is descriptive of beauty.sno /
beauty.sc, not yet fully applied to `parser_icon.sc`.  The audit below
lists every guideline currently violated, in the order to attack them.
These are guidelines, not laws — Lon may decline any item.  Each is
an independently landable sub-rung; do them one at a time, gate after
each (`bash /home/claude/one4all/scripts/test_parser_icon.sh` →
PASS=51 preserved).  Land in this order so each step rests on a clean
gate.

- [x] **Step 1 — underscore-prefixed identifiers.**  DONE this session.
      Renamed `_ic_strbody` → `ic_strbody` (str_pat dot-capture target +
      `ic_push_qlit` reference); deleted the no-op `_parser_ic_done = '';`
      sentinel at file end.  Gate PASS=51 preserved.
- [x] **Step 2 — curly-brace single-statement bodies.**  DONE this
      session.  Converted `while (Line = INPUT) { Src = Src Line nl; }`
      to `while (Line = INPUT) Src = Src Line nl;`.  Full file swept
      for other single-statement `{ ... }` — the remaining brace blocks
      (function bodies, the `if (Src ? Compiland) { ... }` driver
      conditional with else branch, and the proc-frame `while` loops)
      are all multi-statement and correctly keep braces.  Gate PASS=51.
- [x] **Step 3 — section dividers + blank lines combined sweep.**
      DONE this session.  Every `// -----` 71-char divider replaced
      with `/*===...===*/` 120-char major (top-level sections) or
      `/*---...---*/` 120-char minor (sub-sections within).  Every
      blank line between definitions removed; visual structure is now
      carried by the dividers alone.  50 dividers in file; 0 blank
      lines; 0 old-style dividers.  Gate PASS=51.
- [ ] **Step 4 — `Gray` / `White` naming alignment.**  ATTEMPTED and
      REVERTED this session — broke gate PASS=0/FAIL=51, restored to
      post-Step-3 state.  **Lesson learned (next session must read
      this before retry):** the rename can't keep the `$' '` / `$'  '`
      indirection layer.  The reference is **parser_snocone.sc**, not
      beauty.sc — beauty does NOT define `$' '` / `$'  '` at all.
      parser_snocone uses inline `*Gray` / `*White` directly inside
      every operator-token RHS: `$'+' = *Gray '+' *Gray;`.  Correct
      Step-4 sequence: (a) rename `ws_opt` → `Gray` (use form
      `Gray = (*White | epsilon);` with parens), `ws_run` → `White`
      (form `White = SPAN(' ' tab);`); (b) DELETE `$' '` and `$'  '`
      definitions entirely; (c) sweep the file: every `$' '` reference
      becomes `*Gray`, every `$'  '` reference becomes `*White`,
      including inside operator-token definitions (so `$'+' =
      ($' ' '+' $' ');` becomes `$'+' = *Gray '+' *Gray;`).  Don't
      attempt as a partial rename — the indirection through `$' '`
      after the rename does NOT semantically equal the eager
      `$' ' = ws_opt;` — verified this session by isolated probe.
      All-or-nothing.  Gate must be PASS=51 after.  ~59 occurrences
      of `$' '` and ~5 of `$'  '` to convert; mechanical sweep.
- [ ] **Step 5 — pseudo-token names → literal source forms.**  Two
      passes:
      (5a) Drop `$'unary-'`/`$'unary+'`/`$'unary~'`/`$'unary\\'`/
           `$'unary!'`/`$'unary*'`/`$'unary?'` family.  Inline each
           Expr10 branch as `*Gray '-' *Expr10 (r_MNS & 1)` etc.
           PASS=51.
      (5b) Drop `$'augop'` alternation token; inline the four
           `$'+:='`/`$'-:='`/`$'*:='`/`$'/:='` branches directly in
           Expr1 parallel to the `$':='` branch.  PASS=51.
      (5c) `$'qlit'` and `$'proc_wrap'` are side-effect dispatch
           points without literal source spellings.  Rename to
           capture intent in language terms — e.g. `qlit_done =
           (epsilon . *ic_push_qlit());` and `proc_done = (epsilon
           . *ic_decompose_proc());`.  PASS=51.
- [ ] **Step 6 — horizontal-density audit.**  Sweep for tighter
      packing within 120 columns; confirm multi-line wraps use
      constant 2-space indention with vertical-balanced parens and
      binary operators.  PASS=51.

- **Gate (overall):** PASS=51 preserved through every step; no new
  fixtures added under this rung.

### PARSER-IC-10 — fill out unary / augop coverage + introduce `to..by` and concat

After the style cleanup lands, this is the feature-coverage rung:

- [ ] More augmented-assign tokens at `Expr1`: `%:=` `^:=` `||:=` `++:=`
      `--:=` `**:=` `?:=` `=:=` `==:=` `~=:=` `<:=` `<=:=` `>:=` `>=:=`
      `<<:=` `<<=:=` `>>:=` `>>=:=` `===:=` `~===:=`.  Each gets one
      fixture; all dump as `(E_AUGOP lhs rhs)`.  Add the literal token
      branch in Expr1 (per IC-10-style Step 5b, no `$'augop'` umbrella).
- [ ] Remaining unary fixtures: `unary_plus`, `unary_nonnull` (`\`),
      `unary_iterate` (`!`), `unary_random` (`?`).  Already-wired
      branches; just need fixtures.
- [ ] Stacked unary: `--y`, `~~y` etc.  Already supported by the
      recursive `*Expr10`; needs fixtures.
- [ ] Special assignment forms at `Expr1`: `<-` (`E_REVASSIGN`),
      `:=:` (`E_SWAP`), `<->` (`E_REVSWAP`), `===` (`E_IDENTICAL`),
      `~===` (`E_NOT (E_IDENTICAL ...)`).  Each their own branch
      analogous to `:=`.
- [ ] **Expr2** — `to ... by ...` generation.  Currently
      `Expr2 = ( *Expr3 );` collapses through; needs `*Expr3 $'to'
      $'  ' *Expr3 ($'by' $'  ' *Expr3 (r_TOBY & 3) | (r_TO & 2) |
      epsilon)`.
- [ ] **Expr5** — concat `||` and `|||`.  New tier between Expr4 and
      Expr6: `*Expr6 ARBNO($'|||' *Expr6 (r_LCONCAT & 2) | $'||'
      *Expr6 (r_CONCAT & 2))`.
- **Gate:** PASS≥58 (≥7 NEW fixtures across the new operators).

Cross-pollination: same retrofit pattern applies to parser_rebus.sc
and parser_snobol4.sc — separate goals.

---

## Closed rungs (continued — new style guideline section)

The "Style guidelines — derived from beauty.sno / beauty.sc" section
above this rung table is part of the IC-9 commit.  It distills, for
all PARSER-* authors, the working idioms found in beauty.  Future
PARSER-* sessions should treat that section as binding for new
patterns and refactor scope.

---

## Invariants

- Icon's LANG ladder is the upstream pacer; PAT-IC does not race ahead.
- Test programs in `corpus/programs/icon/parser/` are owned by PAT-IC.
- `.ref` files captured at rung-land time.

---

## Watermark

PARSER-IC-10-style Step 4 (Steps 1-3 LANDED PASS=51 preserved corpus@fa61e95: Step 1 — `_ic_strbody` → `ic_strbody`, deleted no-op `_parser_ic_done` sentinel; Step 2 — single-statement `while (Line = INPUT) { ... }` braces dropped; Step 3 — every `// -----` 71-char divider replaced with 120-char `/*===*/` major or `/*---*/` minor, every blank line between definitions removed, 50 dividers in file, 0 blank lines, 0 old-style dividers.  Step 4 — `Gray`/`White` rename — ATTEMPTED and REVERTED this session due to broken gate; lesson: parser_snocone.sc not beauty.sc is the reference; beauty does not define `$' '`/`$'  '`; the Step-4 rename must DELETE the `$' '`/`$'  '` indirection layer and inline `*Gray`/`*White` directly in every operator-token RHS and grammar use site, all-or-nothing.  See Step 4 entry under IC-10-style for the corrected sequence.

PARSER-IC-9-prior (LANDED PASS=51 corpus@85c14d0: augmented assigns + unary prefix + power, plus a new "Style guidelines — derived from beauty.sno / beauty.sc" section in this Goal file.  IC-9 changes in `parser_icon.sc`: nine new reduce-tag constants (`r_AUGOP` `r_POW` `r_MNS` `r_PLS` `r_CSET_COMPL` `r_NONNULL` `r_ITERATE` `r_SIZE` `r_RANDOM`); four augop literal tokens (`$'+:='` `$'-:='` `$'*:='` `$'/:='`) plus alternation token `$'augop'`; seven unary-prefix tokens (`$'unary-'` `$'unary+'` `$'unary~'` `$'unary\\'` `$'unary!'` `$'unary*'` `$'unary?'`); new `Expr10` (unary, recursive on itself, falls through to `*Expr11`); new `Expr8` (right-assoc power); `Expr7` retargeted from `*Expr11` to `*Expr8`; `Expr1` gains `$'augop' *Expr1 (r_AUGOP & 2)` branch alongside the existing `:=` branch.  6 NEW fixtures: `augop_add` `augop_sub` `unary_minus` `unary_cset_compl` `unary_size` `pow_expr`).
