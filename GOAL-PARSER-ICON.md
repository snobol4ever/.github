# GOAL-PARSER-ICON.md — PARSER-ICON pattern-based frontend in Snocone

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
`tree`/`TDump`/`stack` from `corpus/SCRIP/`. Bug fixes there
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
( cd /home/claude/SCRIP && git fetch origin parser 2>/dev/null; git checkout parser 2>/dev/null || git checkout -b parser origin/parser 2>/dev/null || git checkout -b parser )
bash /home/claude/SCRIP/scripts/install_system_packages.sh
bash /home/claude/SCRIP/scripts/build_scrip.sh
```

Gate after setup:
```bash
bash /home/claude/SCRIP/scripts/test_smoke_icon.sh
bash /home/claude/SCRIP/scripts/test_parser_icon.sh
```

---

## Architecture reminder

PAT runs `parser_icon.sc` (which loads the shared SC library from
`corpus/SCRIP/`) against an `.icn` source — produces IR tree
t2 via `Compiland`; the existing frontend produces t1 via `--dump-ast`.
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
| **PARSER-IC-3**       — control flow + comparison ops | PASS=20 | Added `Expr4`/`Expr4tail` (`= ~= < <= > >=`); `If`/`While` in `Expr11` (else inline-optional to dodge double-parse); `Expr1` restructured to `id_pat ws_opt ':='`-committed assign branch.  6 NEW fixtures.  **Cross-pollination bug fix in `corpus/SCRIP/tdump.sc`**: multi-line fallback was guarded by `~(NULL *IDENT(n(x)))` — a no-op (pattern construction can't fail) — so wide trees fell through to `.` leaf branch.  Replaced with `DIFFER(n(x))`; extended branch to mirror TLump's role-slot (`:`-prefix) and internal-node `v(x)` sval emission.  Beauty source `programs/snocone/demo/beauty/TDump.sc` has the same bug; treatment owed under whichever goal owns beauty. |
| **PARSER-IC-4**       — procedure definition + return + variadic invocation | PASS=27 | Generalized `Prochead` to `'procedure' ws_run id_pat ws_opt '(' Arglist ')'`; new `ProcParam`/`ParamRest`/`Arglist` patterns; helpers renamed `start_proc_main`→`start_proc`, `finish_proc_main`→`finish_proc`; new `append_proc_param`.  New `ReturnStmt` at the Stmt level: with-value `'return' ws_run *Expr` first, bare `'return' ws_opt semi_opt` fallback; builds `(E_RETURN [expr])`.  **Variadic invocation** via dedicated `$'@II'` invocation-construction stack (struct `ic_ilink`), parallel to Compiland's stack — required (not a single-slot global) because invocations nest (`write(double(5))`).  7 NEW fixtures (proc_simple/oneparam/twoparam, proc_call_noargs/onearg/twoargs, proc_return). |
| **PARSER-IC-5**       — alternation generators (`expr1 \| expr2`) | PASS=33 | New `Expr3` slot between Expr2 and Expr4 per canonical EBNF.  Existing frontend flattens nested alternations into a single `(E_ALTERNATE a b c d)` — PAT-IC matches via dedicated `$'@AL'` alt-construction stack (struct `ic_alink`).  Single `expr_alt_step(savedLHS)` helper handles both first-`\|` (push fresh E_ALTERNATE) and subsequent `\|`s (append onto top-of-stack) via a `_e3built` flag; `expr_alt_enter`/`expr_alt_finish` save/restore the flag at Expr3 boundaries to support nested alternations.  6 NEW fixtures (alt_two/three/var/str/in_call/arith). |
| **PARSER-IC-6**       — `every [do body]` and `subj ? body` scan | PASS=40 | New `Every` branch in `Expr11` handles both `every gen` (1-child `E_EVERY`) and `every gen do body` (2-child `E_EVERY`) via two helpers `expr_every1`/`expr_every2`; saved generator in `_ic_evgen` to survive body parse.  New `Expr1a` slot between `Expr` and `Expr1` per canonical EBNF handles `subj ? body` building `(E_SCAN subj body)`; subjects saved on dedicated `$'@SC'` link()-stack (struct `ic_sclink`) so nested scans (`a ? b ? c`) don't clobber.  Critical fix: scan body uses `*Expr` (deferred reference) since `Expr` is defined below `Expr1a`; non-deferred reference produced a malformed pattern that silently bailed.  Driver loops rewritten from `goto` to `while` per RULES.md control-flow guidance.  7 NEW fixtures (every_simple/do/alt/novar, scan_simple/var/assign). |
| **PARSER-IC-8a**      — SCRIP grammar fix: binary `~` `&` `#` `%` OPSYN slots | PASS=40 preserved | New `expr5a` tier in `src/frontend/snocone/snocone_parse.y` between comparison (expr5) and additive (expr6).  Each binary OPSYN slot lowers to `E_FNC` with `sval` = operator literal, paralleling how comparison ops (T_EQ→"EQ", T_NE→"NE", etc.) lower today; runtime E_FNC dispatch consults the OPSYN table to find the registered handler.  Lexer already emitted T_2AMP/T_2TILDE/T_2POUND/T_2PERCENT (snocone_lex.c:543, 551, 547, 549) — only the parser needed the rule.  `%type <expr> expr5a` added (line 467).  After regeneration via `regenerate_parser_and_lexer_from_sources.sh` and `build_scrip.sh` rebuild, `'a' ~ 'b'` (after `OPSYN('~','f',2)`) invokes `f('a','b')` correctly.  Compiland in parser_icon.sc converted from `reduce("'Parse'", 'nTop()')` to `("'Parse'" & 'nTop()')` operator form as smoke test of the unblocked path; PASS=40 preserved.  Snocone test suite shows no new regressions (test_smoke_snocone, test_parser_snocone PASS=13, plus all language smoke tests PASS).  Pre-existing C-test breakage in `test/frontend/snocone/test_snocone_parse_a..j.c` (references stale `Program *`/`head` API) is unrelated to this change — verified by stash/repro before commit. |
| **PARSER-IC-7**       — paren `(expr)`/`(e1;e2)` + compound `{...}` primaries + beauty-style `$'op'` pattern-builder refactor | PASS=45 | Two changes in one session.  (a) Style refactor: every `epsilon . *fn(args)` replaced by a named `$'...'` pattern variable per beauty.sc / parser_snocone.sc idiom — `$'|'`/`$':='`/`$'?'`/`$','` op tokens, `$'invoke_arg'`/`$'append_stmt'`/`$'finish_proc'`/etc. side-effect builders, `$'atom_QLIT'`/`$'atom_ILIT'`/`$'atom_VAR'` atom builders, `$'save_eNlhs'`/`$'op_TAG'`/`$'binop_*'` per-tier savers and folds, `$'if2'`/`$'if3'`/`$'while2'`/`$'every1'`/`$'every2'`/`$'assign_id'` control-flow builders, `$'scan_push'`/`$'scan_finish'` scan builders.  PASS=40 preserved through refactor.  (b) IC-7 features: `Paren` and `Compound` primaries via dedicated `$'@SQ'` link()-stack (struct `ic_sqlink`), `ic_seq_push/append/finish` helpers, single-child unwrap matches existing-frontend `parse_block_or_expr`.  5 NEW fixtures: paren_expr/paren_seq/compound_one/compound_two/scan_paren.  corpus@c6e4c2b. |
| **PARSER-IC-8b**      — parser_icon.sc canonical-spine rewrite | PASS=45 preserved | Trees flow through the shared shift/reduce stack.  Binary tiers use `*L $'op' *R (r_TAG & 2)`.  N-ary collectors (alternation Expr3, function call Call, paren-seq Paren, compound Compound) use `nPush() ARBNO(nInc() *X) (r_TAG & 'nTop()' or r_nTop) nPop()` — the `r_nTop = '*(GT(nTop(),1) nTop())'` idiom is what makes single-child unwrap work for E_SEQ_EXPR (when only one item is on the frame, the EVAL fails and reduce silently leaves the lone tree alone — verified with isolated probe).  Atoms use `*P ~ T` operator form, except QLIT (which keeps the `dot-capture + ic_push_qlit()` exception so the string body excludes its quotes — same exception parser_snocone.sc keeps for `sc_push_qlit`).  Statement decomposition collapsed to ONE helper `ic_decompose_proc`: pops the proc-frame's nTop() children, reads pname from `v(child[1])` (the (E_VAR pname) callee shifted by Prochead), rebuilds (E_FNC pname kids), wraps in (STMT :subj ...).  Removed: every `expr_*` parsing-state helper, every `_expr_node` global slot, every `$'@II'`/`$'@AL'`/`$'@SC'`/`$'@SQ'` link()-stack, every `ic_inv_*`/`ic_alt_*`/`ic_scan_*`/`ic_seq_*` parsing-state helper, every `Tree(tag,'',2,L,R)` direct construction outside the one helper.  Net: 871 → 366 lines (−505).  Cross-pollination opportunity: parser_rebus.sc / parser_snobol4.sc owe the same retrofit.  corpus@ef1acd2. |
| **PARSER-IC-9**       — augmented assigns + unary prefix + power | PASS=51 | Three new operator tiers added in canonical-spine style.  (a) **Augmented assigns** at `Expr1`: tokens `$'+:='` `$'-:='` `$'*:='` `$'/:='` defined plus an alternation token `$'augop'` covering them; Expr1 gains a second branch `$'augop' *Expr1 (r_AUGOP & 2)` parallel to the `$':=' *Expr1 (r_ASSIGN & 2)` branch.  Operator literal is intentionally discarded — `--dump-ast` output is `(E_AUGOP lhs rhs)` regardless of which augop appeared in source.  (b) **Unary prefix** at new `Expr10` tier between `Expr11` and `Expr7`: per-op tokens `$'unary-'` `$'unary+'` `$'unary~'` `$'unary\\'` `$'unary!'` `$'unary*'` `$'unary?'` (only leading `$' '`, no required whitespace before operand); each branch is `$'unary-op' *Expr10 (r_TAG & 1)` recursing for stacked unaries; falls through to `*Expr11`.  Reduce tags: `r_MNS` `r_PLS` `r_CSET_COMPL` `r_NONNULL` `r_ITERATE` `r_SIZE` `r_RANDOM`.  (c) **Power** at new `Expr8` tier (right-assoc): `*Expr10 ($'^' *Expr8 (r_POW & 2) | epsilon)`.  `Expr7` retargeted from `*Expr11` to `*Expr8` so the multiplicative tier sits above the new power tier.  6 NEW fixtures: `augop_add` `augop_sub` `unary_minus` `unary_cset_compl` `unary_size` `pow_expr`.  Style: this rung was authored under the new "Style guidelines — derived from beauty.sno / beauty.sc" section added to this Goal file in the same commit (re-reads beauty.sno/beauty.sc, distills naming + horizontal-density + `Gray`/`White`/`$' '`/`$'  '`/`$'op'`/`$'kw'` token conventions). |

---

## Open rungs

### PARSER-IC-10-style — clean up guideline violations in `parser_icon.sc`  COMPLETE

The new "Style guidelines" section is descriptive of beauty.sno /
beauty.sc, not yet fully applied to `parser_icon.sc`.  The audit below
lists every guideline currently violated, in the order to attack them.
These are guidelines, not laws — Lon may decline any item.  Each is
an independently landable sub-rung; do them one at a time, gate after
each (`bash /home/claude/SCRIP/scripts/test_parser_icon.sh` →
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
- [x] **Step 4 — `Gray` / `White` naming alignment.**  DONE.
      Renamed `ws_opt` → `White` (form `White = SPAN(' ' tab);`),
      `ws_run` → `Gray` wait — correct: `White = SPAN(' ' tab);`,
      `Gray = (*White | epsilon);`.  Deleted `$' '` and `$'  '`
      definitions and their comment block entirely.  Swept all
      ~64 occurrences: every `$' '` → `*Gray`, every `$'  '` →
      `*White` — including inside all operator-token and keyword-token
      RHSs (so `$'+' = ($' ' '+' $' ');` became `$'+' = (*Gray '+'
      *Gray);`).  Two-space `$'  '` replaced before one-space `$' '`
      to avoid partial match.  Note: `While` (the procedure construct)
      and `White` (the whitespace def) are distinct Snocone identifiers
      — no collision.  Gate PASS=51 FAIL=0 preserved.
- [x] **Step 5 — pseudo-token names → literal source forms.**  DONE.
      (5a) Dropped `$'unary-'`/`$'unary+'`/`$'unary~'`/`$'unary\\'`/
           `$'unary!'`/`$'unary*'`/`$'unary?'` family.  Inlined each
           Expr10 branch as `*Gray '-' *Expr10 (r_MNS & 1)` etc.
           PASS=51 preserved.
      (5b) Dropped `$'augop'` alternation token; inlined the four
           `$'+:='`/`$'-:='`/`$'*:='`/`$'/:='` branches directly in
           Expr1 parallel to the `$':='` branch (4 separate
           alternatives all with `(r_AUGOP & 2)`).  PASS=51 preserved.
      (5c) Renamed `$'qlit'` → `qlit_done = (epsilon . *ic_push_qlit());`
           and `$'proc_wrap'` → `proc_done = (epsilon
           . *ic_decompose_proc());` to capture intent in language
           terms.  Updated reference sites in Expr11 (`qlit_done`)
           and Proc (`proc_done`).  PASS=51 preserved.
- [x] **Step 6 — horizontal-density audit.**  DONE.  Packed three
      blocks two-per-line per parser_snocone.sc convention: keyword
      tokens (`$'if'`/`$'then'`/etc.), operator tokens (`$'|'`/`$':='`/
      etc.), augop tokens (`$'+:='`/`$'-:='`/etc.), and reduce-tag
      constants (`r_ASSIGN`/`r_SCAN`/etc.).  No lines exceed 120 cols.
      File length 419 → 371 lines (−48).  PASS=51 preserved.

- **Gate (overall):** PASS=51 preserved through every step; no new
  fixtures added under this rung.

### PARSER-IC-10 — fill out unary / augop coverage + introduce `to..by` and concat  COMPLETE

The feature-coverage rung is complete.  All checkbox items closed; gate
PASS=88 FAIL=0 (+37 over IC-9 baseline of 51).  Single corpus commit
(see Watermark for hash).

- [x] More augmented-assign tokens at `Expr1`: `%:=` `^:=` `||:=` `++:=`
      `--:=` `**:=` `?:=` `=:=` `==:=` `~=:=` `<:=` `<=:=` `>:=` `>=:=`
      `<<:=` `<<=:=` `>>:=` `>>=:=` `~==:=`.  All dump as
      `(E_AUGOP lhs rhs)`.  Each got its own literal token branch in
      Expr1 (no `$'augop'` umbrella per IC-10-style Step 5b).  Note:
      the prior goal text named `===:=` and `~===:=` — the actual Icon
      lexer uses `==:=` (string-eq augop) and `~==:=` (string-ne
      augop); the canonical spellings are taken from
      `src/frontend/icon/icon_lex.c:657-675`.  19 NEW fixtures.
- [x] Remaining unary fixtures: `unary_plus`, `unary_nonnull` (`\`),
      `unary_iterate` (`!`), `unary_random` (`?`).  4 NEW fixtures.
- [x] Stacked unary: `~~y`.  1 NEW fixture (note: `--y` would be
      ambiguous with cset-difference operator and the oracle rejects
      it — used `~~y` instead which the oracle parses as nested
      `(E_CSET_COMPL (E_CSET_COMPL (E_VAR y)))`).
- [x] Special assignment forms at `Expr1`: `<-` (`E_REVASSIGN`),
      `:=:` (`E_SWAP`), `<->` (`E_REVSWAP`), `===` (`E_IDENTICAL`),
      `~===` (`(E_NOT (E_IDENTICAL ...))` — built via two-step reduce
      `(E_IDENTICAL & 2) (E_NOT & 1)`).  5 NEW fixtures.
- [x] **Expr2** — `to ... by ...` generation.  Implemented as
      `*Expr3 FENCE($'to' $'  ' *Expr3 FENCE($'by' $'  ' *Expr3
      (E_TO_BY & 3) | (E_TO & 2)) | epsilon)`.  Tag is `E_TO_BY` (with
      underscore — confirmed against oracle), not `r_TOBY`.  3 NEW
      fixtures (range_to, range_to_by, range_paren).
- [x] **Expr5** — concat `||` and `|||`.  New tier between `Expr4`
      and `Expr6`: `*Expr6 ARBNO($'|||' *Expr6 (E_LCONCAT & 2) | $'||'
      *Expr6 (E_CAT & 2))`.  Tag for `||` is `E_CAT` (not
      `E_CONCAT`).  Expr4tail rewired from `*Expr6` to `*Expr5`.
      5 NEW fixtures (concat_two, concat_three, lconcat_two,
      concat_alt, concat_cmp).
- [x] **Negative-lookahead idiom** added for prefix-conflicting ops:
      `$'<'`, `$'>'`, `$'|'`, `$'||'`, `$'|||'` use the new
      `X @posA (ANY('reject_set') | epsilon) @posB *EQ(posA, posB)`
      idiom.  Required because Expr4tail's `$'<'` was greedily
      consuming `<` before Expr1's `$'<-'`/`$'<->'` could see it
      (parsed `x <- 1` as `x < (-1)`).  The deferred-eval
      `*EQ(posA, posB)` predicate succeeds iff the alternation took
      the epsilon branch (cursor didn't advance), giving true negative
      lookahead — neither FENCE+FAIL nor `(p FAIL | epsilon)` work
      (alternation backtracking restores cursor and epsilon
      succeeds).  Worth adding to the cross-PARSER style guidelines
      once verified across parser_snobol4.sc/parser_snocone.sc/etc.
- [x] **Snocone string-literal byte-fix in `parser_icon.sc`**: the
      previous `$'\\' = $' ' '\\' $' ';` token had RHS pattern
      `'\\'` which is **2 bytes** in Snocone (per
      `src/frontend/snocone/snocone_lex.c:348-351` — the lexer
      specializes only `''` (doubled quote) and `\n` (newline);
      every other byte is copied verbatim).  Changed to `'\'` (one
      byte) so the token actually matches a single-backslash unary
      operator.  This is **not a SCRIP bug** — it's correct Snocone
      semantics — but the parser_icon.sc had been wrong since IC-9
      and the unary `\` branch was unreachable.  The previous gate
      was PASS=51 because no unary_nonnull fixture existed.

- **Gate:** PASS=88 FAIL=0 (+37 NEW fixtures over IC-9's 51).

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

PARSER-IC-10 LANDED PASS=88 corpus@1744d3e: feature-coverage rung complete.  37 NEW fixtures over IC-9 baseline of 51.  Tokens added: 19 augops (`%:=` `^:=` `||:=` `++:=` `--:=` `**:=` `?:=` `=:=` `==:=` `~=:=` `<:=` `<=:=` `>:=` `>=:=` `<<:=` `<<=:=` `>>:=` `>>=:=` `~==:=`); 5 special-form ops (`<-` `<->` `:=:` `===` `~===`); 2 keywords (`to`, `by`); 2 concat (`||` `|||`).  9 new tag constants: `E_REVASSIGN` `E_SWAP` `E_REVSWAP` `E_IDENTICAL` `E_NOT` `E_TO` `E_TO_BY` `E_CAT` `E_LCONCAT`.  Grammar: Expr1 expanded with 19 augop branches + 5 special-form branches (longer-prefix-first ordering); Expr2 implements `to..by` via nested FENCE; Expr5 added between Expr4 and Expr6 (left-associative ARBNO over `|||` and `||`); Expr4tail rewired `*Expr6` -> `*Expr5`.  ~=== uses two-step reduce `(E_IDENTICAL & 2) (E_NOT & 1)` for `(E_NOT (E_IDENTICAL ...))`.  Negative-lookahead idiom introduced for `$'<'` `$'>'` `$'|'` `$'||'` `$'|||'`: `X @posA (ANY('reject_set') | epsilon) @posB *EQ(posA, posB)` — succeeds iff alternation took epsilon (cursor didn't advance), giving true negative lookahead; required because Expr4tail's `<` was greedily consuming before Expr1's `<-` could fire.  Fixed Snocone string-literal byte-bug: `$'\\\\' = $' ' '\\\\' $' ';` had RHS pattern `'\\\\'` = 2 bytes (per snocone_lex.c:348-351 only `''` and `\\n` specialized) so unary `\\` branch was unreachable since IC-9; corrected RHS to `'\\'` (1 byte).  Tag spelling corrections from goal text: oracle uses `==:=` (string-eq augop) and `~==:=` (string-ne augop) — not `===:=`/`~===:=`; tag for `||` is `E_CAT` not `E_CONCAT`; tag for `to..by` is `E_TO_BY` (with underscore) not `E_TOBY`.  Gate PASS=88 FAIL=0; smoke PASS=5 FAIL=0 preserved.  Next session: cross-pollinate negative-lookahead idiom and IC-10 feature retrofit to parser_rebus.sc / parser_snobol4.sc / parser_snocone.sc / parser_prolog.sc / parser_raku.sc per their own goals.

PARSER-IC-10-style (Steps 1-6 of IC-10-style ALL LANDED PASS=51 corpus@1734c42: Step 5 — pseudo-token name cleanup: 5a inlined `$'unary-'`/`$'unary+'`/`$'unary~'`/`$'unary\\'`/`$'unary!'`/`$'unary*'`/`$'unary?'` family directly into Expr10 as `*Gray 'op' *Expr10 (r_TAG & 1)`; 5b dropped `$'augop'` umbrella, inlined four augop literal branches into Expr1 each with `(r_AUGOP & 2)`; 5c renamed `$'qlit'` → `qlit_done` and `$'proc_wrap'` → `proc_done` to capture intent in language terms.  Step 6 — horizontal density: packed keyword tokens, operator tokens, augop tokens, and reduce-tag constants two-per-line per parser_snocone.sc convention.  File 419 → 371 lines (−48).  Gate PASS=51 FAIL=0 preserved through every sub-step.  IC-10-style COMPLETE; next is IC-10 feature coverage rung — augop expansion, more unary fixtures, special assignment forms, Expr2 to..by, Expr5 concat.

PARSER-IC-9-prior (LANDED PASS=51 corpus@85c14d0: augmented assigns + unary prefix + power, plus a new "Style guidelines — derived from beauty.sno / beauty.sc" section in this Goal file.  IC-9 changes in `parser_icon.sc`: nine new reduce-tag constants (`r_AUGOP` `r_POW` `r_MNS` `r_PLS` `r_CSET_COMPL` `r_NONNULL` `r_ITERATE` `r_SIZE` `r_RANDOM`); four augop literal tokens (`$'+:='` `$'-:='` `$'*:='` `$'/:='`) plus alternation token `$'augop'`; seven unary-prefix tokens (`$'unary-'` `$'unary+'` `$'unary~'` `$'unary\\'` `$'unary!'` `$'unary*'` `$'unary?'`); new `Expr10` (unary, recursive on itself, falls through to `*Expr11`); new `Expr8` (right-assoc power); `Expr7` retargeted from `*Expr11` to `*Expr8`; `Expr1` gains `$'augop' *Expr1 (r_AUGOP & 2)` branch alongside the existing `:=` branch.  6 NEW fixtures: `augop_add` `augop_sub` `unary_minus` `unary_cset_compl` `unary_size` `pow_expr`).

---

### PARSER-IC-11 — Expr tier expansion: str_cmp + mod + limit + subscript + section + field + repeat + until + list_ctor + break + next

**Status: LANDED PASS=104 corpus@fee8778**

#### Rungs completed this session

- [x] **IC-11-a** Expr6tail: `++` (E_CSET_UNION), `--` (E_CSET_DIFF) — longer-prefix-first before `+`/`-`
- [x] **IC-11-b** Expr7tail: `**` (E_CSET_INTER), `%` (E_MOD) — longer-prefix-first before `*`
- [x] **IC-11-c** Expr4tail: string comparisons `<<=`, `<<`, `>>=`, `>>`, `~==`, `==` (E_LLE/LLT/LGE/LGT/LNE/LEQ)
- [x] **IC-11-d** Expr9 tier: postfix `expr \ N` limit (E_LIMIT), left-assoc ARBNO
- [x] **IC-11-e** Expr11tail: postfix `x[i]` subscript (E_IDX), `x[i:j]` section (E_SECTION), `x.f` field (E_FIELD) via helpers push_subscript/push_section/push_field
- [x] **IC-11-f** Expr11 additions: `repeat` (E_REPEAT), `until` (E_UNTIL), `break` (E_LOOP_BREAK), `next` (E_LOOP_NEXT), `[list]` constructor (E_MAKELIST)
- [x] **IC-11-g** Token simplification: removed broken `*EQ` negative-lookahead from all new tokens — grammar alternation ordering (longer-prefix-first in each tail) is the correct disambiguation mechanism

#### SCRIP bug discovered — *EQ lookahead is a no-op (MUST FILE)

**Bug:** `*EQ(pos_a, pos_b)` in the pattern `@pos_a (ANY('...') | epsilon) @pos_b *EQ(pos_a, pos_b)` does NOT fail when `pos_a ≠ pos_b`. The deferred EQ call silently succeeds regardless of cursor delta. All existing `$'<'`/`$'>'` negative-lookahead tokens in IC-10 are no-ops; the grammar works only because of alternation ordering.

- [x] **BUG-SCRIP-EQ** — File step in GOAL-REWRITE-SCRIP.md: investigate why `*EQ(cursor_a, cursor_b)` in a pattern context does not propagate failure when integer args differ. Repro: `src = '++ 2'; src '+' @a (ANY('+') | epsilon) @b *EQ(a,b)` — should fail (b > a) but succeeds.

#### Fixtures added (16 new, corpus@fee8778)

str_eq_op, str_ne_op, str_lt_op, str_le_op, str_gt_op, str_ge_op, mod_op, limit_op, field_access, subscript_op, section_op, repeat_op, until_op, list_ctor, break_op, next_op

#### Known gaps deferred to IC-12

- Cset literal `'abc'` (E_CSET) — parser_icon.sc `str_pat` only handles `"..."` (E_QLIT); single-quote form needs a `cset_pat` alternative
- Augop forms of new ops: `++:=`, `--:=`, `**:=`, `%:=`, `<<=:=`, etc. (tokens defined, grammar not wired to Expr1 augop list)
- `case` expression (E_CASE)
- `create` expression  
- Global/local/static/initial declarations
- Multi-line compound bodies (oracle `--dump-ast` also rejects them — not fixable at parser_icon.sc level alone)

**Watermark — Next session:** Open IC-13. Priority order: (1) `create` expression (E_CREATE), (2) global/local/static/initial declarations, (3) cross-pollinate negative-lookahead idiom to other PARSER-* parsers.

---

### PARSER-IC-12 LANDED PASS=108 corpus@TBD

Cset literal, case expression, BUG-SCRIP-EQ filed.  4 NEW fixtures over IC-11 baseline of 104.

- **Cset literal** `'abc'` → `(E_CSET "aeiou")`: added `cset_pat = ("'" BREAK("'") . csetbody "'");`, `push_cset()` helper, `Push_cset` side-effect builder; wired as `$' ' cset_pat Push_cset` in `Expr11` (before `str_pat` — single-quote before double-quote); added `E_CSET = "'E_CSET'";` tag constant.  Fixed `tdump.sc` `TValue` to render `E_CSET` with double-quoted body (same as `E_QLIT` via `CQize`) — without this fix the generic IR-leaf branch rendered `(E_CSET aeiou)` without quotes, diverging from oracle.  Cross-pollination: any PARSER-* needing cset should add the same `TValue` branch to `tdump.sc`.
- **Case expression** `case E of { v:r; default:r }` → `(E_CASE dispatch v1 r1 ... default_result)`: added `$'case'`, `$'of'` keyword tokens; `CaseClause` and `CaseDefault` patterns; `Case` production using `nPush()/nInc()/nPop()` — dispatch expr counted as first nInc, each clause pair counted as two nInc (one for value, one for result), default result as one nInc.  `DGray` used around `of` keyword and inside `{ }` so inline case (all on one line) parses via `$' '` within tokens, outer layout via `DGray` in `Case`.  Wired `Case` into `Expr11` before other primaries.
- **Multi-line compound fix** — deferred: oracle (`--dump-ast`) also rejects multi-line `{ ... }` bodies (the existing C frontend only handles semicolon-separated single-line form).  No fixture can be added until both sides support it.  `DGray` definition kept in `parser_icon.sc` for future use by `Case` — not applied to `Compound`.
- **BUG-SCRIP-EQ** filed: `GOAL-REWRITE-SCRIP.md` RS-26 (steps RS-26a/b/c).  Marked `[x]` in IC-11 open-rung checkbox.
- New fixtures: `cset_lit`, `cset_compl_expr`, `case_simple`, `case_nodefault`.

---

### PARSER-IC-13 LANDED PASS=113 corpus@3a8f465

Global/local/static/initial/record declarations. 5 NEW fixtures over IC-12 baseline of 108.

- **`global id, id`** at top level → `(STMT :subj (E_GLOBAL (E_VAR id) ...))`: `push_global_top()`, `GlobalDecl` production wired into `Compiland` ARBNO alongside `Record` and `Proc`. `Compiland` ARBNO now uses `*DGray` (includes newlines) so blank lines between top-level items don't stall the loop.
- **`local id, id`** in proc body → `E_GLOBAL` stmt child inside `E_FNC`: `push_local_stmt()`, `LocalDecl` production wired into `StmtBody`.
- **`static id`** in proc body → also `E_GLOBAL` (same tag as local per oracle; ival differs in C but not in dump): `StaticDecl` shares `push_local_stmt`.
- **`initial { expr }`** in proc body → `(E_INITIAL child)`: `InitialStmt` production using `nPush/nInc/nPop` with `*DGray` inside braces. Bug during development: forgot `nInc()` after `*Expr` so `nTop()=0` → `(E_INITIAL)` with no children; fixed.
- **`record Name(f1, f2)`** at top level → `(STMT :subj (E_RECORD Name (E_VAR f1) ...))`: `push_record()`, `Record` production. Name shifted as `(E_VAR Name)` first child; `push_record` reads `v(kids[1])` for sval.
- **`DGray`** definition added (deep gray = `SPAN(' ' tab nl)`); used in `InitialStmt` body and `Compiland` ARBNO. Not applied to `Compound` (oracle C frontend also rejects multi-line `{ }`).
- Shared patterns: `DeclFirst`/`DeclRest`/`DeclIds` for comma-separated identifier lists.

**Next session (IC-14):** `create` expression (`E_CREATE` if it exists), `suspend`/`fail` statement forms, `link`/`invocable` top-level declarations, and cross-pollinating `DGray` Compiland fix to other PARSER-* parsers.

---

### PARSER-IC-14 LANDED PASS=116 corpus@b934eb5

`suspend [do body]` + `fail` statements + DGray fix. 3 NEW fixtures.

- **`suspend expr;`** → `(E_SUSPEND expr)`: `SuspendStmt` with nPush/nInc/nPop spine; optional `do body` branch via FENCE adds second child → 2-child `(E_SUSPEND expr body)`.
- **`fail;`** → `(E_PROC_FAIL)`: `FailStmt` = `$'fail' semi_opt nl_one (E_PROC_FAIL & 0)`. Zero children.
- **`DGray` redefined** to `ARBNO(SPAN(' ' tab nl) | '#' BREAK(nl) nl_one)` — properly consumes any number of consecutive blank lines and comment lines. Previous definition only handled one SPAN+comment sequence, so files with leading comment blocks produced no Compiland output. Used in Compiland ARBNO and Case/Initial bodies.
- New fixtures: `suspend_simple`, `suspend_do`, `fail_stmt`.
- `link`/`invocable`/`create` deferred: oracle C frontend doesn't support them.

**Next session (IC-15):** Real literal `E_FLIT` support (needed for rung15+); keyword expressions (`&pos`, `&subject`, etc.); cross-pollinate DGray Compiland fix to other PARSER-* parsers.

---

### PARSER-IC-15 LANDED PASS=118 corpus@e6e8cf7

Real literal + keyword expression. 2 NEW fixtures.

- **Real literal** `3.14` → `(E_FLIT 3.14)`: `exp_part` + `real_pat` patterns (handles `d.d`, `.d`, `d.de±N` forms); dot-capture into `rval`; `push_flit()` builds `tree('E_FLIT', rval)`. Wired in `Expr11` before `int_pat` (longer-prefix first: `3.14` would otherwise match `int_pat` as `3`). Caveat: exponent forms store source text, but oracle normalises via `%g` (e.g. `1.5e2` → `150`); fixtures use simple decimal forms where source = oracle.
- **Keyword expression** `&pos` → `(E_VAR &pos)`: `kw_prefix = '&'`; Expr11 branch `$' ' kw_prefix id_pat . kwname Push_kw`; `push_kw()` builds `tree('E_VAR', '&' kwname)` matching C frontend `sprintf("&%s", kwname)` → `e_leaf_sval(E_VAR, ...)`.
- New fixtures: `real_lit`, `kw_expr`.

**Next session (IC-16):** Exponent-form real literal normalization (parse `1.5e2` → store `150` by evaluating via `REAL()` or `integer()`); `not expr` → `(E_NOT expr)`; `E_FAIL` (bare `fail` as expression rather than statement).

---

### PARSER-IC-16 LANDED PASS=121 corpus@e214108

`not expr`, `fail` as expression, exponent real normalization. 3 NEW fixtures.

- **`not expr`** → `(E_NOT expr)`: added `$'not' = $' ' 'not';` keyword token; wired `$'not' $'  ' *Expr10 (E_NOT & 1)` in `Expr10` before the `*Expr11` fallthrough (parallel to other unary-prefix branches).
- **`fail` as expression** → `(E_PROC_FAIL)`: wired `$'fail' $' ' (E_PROC_FAIL & 0)` in `Expr11` alongside `$'break'`/`$'next'` zero-child primaries. `FailStmt` in `StmtBody` still matches `fail;` as a statement; the `Expr11` form covers `fail` in any expression context.
- **Exponent real normalization**: `push_flit()` already calls `REAL(rval)` giving `100.` for `1.0e2`. Normalization (`100.` → `100`) done in `tdump.sc` `TValue`/`TLump0` E_FLIT renderer. Two bugs encountered and resolved:
  1. **Positional anchors (`RPOS`, `LEN`) fail in pipeline function context (RS-27)**: when called from the full parser pipeline, `RPOS(0)` and `LEN(n)` inside a function resolve against the outer pattern subject (`Src`) rather than the local variable. Avoided by using SIZE arithmetic instead.
  2. **`v(x)` type mismatch**: `tree('E_FLIT', REAL(rval))` stores a real-typed descriptor; `v(x)` returns a real, not a string — `IDENT(pre '.', v(x))` fails on type mismatch even when the string representations are identical. Fixed by forcing string coercion: `fval = '' v(x)`.
  3. **Working fix** in `TValue` and `TLump0`: `fval = '' v(x); fval SPAN(digits) . pre; if (DIFFER(pre) IDENT(SIZE(pre)+1, SIZE(fval))) fval = pre;` — avoids both issues entirely.
- SCRIP bug RS-27 filed in `GOAL-REWRITE-SCRIP.md` with full root-cause analysis.
- New fixtures: `not_expr`, `fail_expr`, `real_exp`.

**Next session (IC-17):** `=E` match-expression rewrite as `match(E)` call (already in C frontend's `parse_unary`); `string@integer` activation expression (`E_ACTIVATE`); cross-pollinate DGray Compiland fix and IC-16 `not`/`fail` tokens to other PARSER-* parsers.

---

### PARSER-IC-17 LANDED PASS=124 corpus@c03df28

`=E` match rewrite, `/E` null test, `E1 ! E2` bang-binary. 3 NEW fixtures.

- **`=E` match rewrite** → `(E_FNC (E_VAR match) E)`: wired `$' ' '=' *Expr10 Push_match` in `Expr10`. `push_match()` pops the inner expr and builds `Tree('E_FNC','',2,tree('E_VAR','match'),inner)` — mirrors C frontend `parse_unary` TK_EQ branch.
- **`/E` null test** → `(E_NULL E)`: wired `$' ' '/' *Expr10 (E_NULL & 1)` in `Expr10`. Tag constant `E_NULL` added.
- **`E1 ! E2` bang-binary** → `(E_BANG_BINARY E1 E2)`: added `$'!' *Expr10 (E_BANG_BINARY & 2)` branch in `Expr9tail` alongside the existing limit `$'\\'` branch. Tag constant `E_BANG_BINARY` added.
- **Disambiguation bug fixed**: `$'==='` / `$'~==='` moved from `Expr1` into `Expr4tail` (before `$'=='` / `$'~=='`). Root cause: `Expr4tail`'s `$'=='` was consuming the first two `=` of `===`, leaving unary `=` (match) to consume the third → `(E_LEQ x (E_FNC match y))` instead of `(E_IDENTICAL x y)`. Fix: longer-prefix-first ordering in `Expr4tail` (canonical structural idiom). Regressions `special_identical` and `special_notident` resolved.
- New helper: `push_match()` / `Push_match`.
- New fixtures: `match_expr`, `null_expr`, `bang_binary` (+3).

**Next session (IC-18):** `@` activation binary `E1 @ E2` → `(E_AT E1 E2)` once oracle C frontend supports it (currently rejects `@` as parse error); cross-pollinate `/E` null + `=E` match + `E1!E2` bang-binary to other PARSER-* parsers; additional unary forms from `icon-sp.ebnf` expr10 list not yet covered (`BAR`, `CONCAT`, `LCONCAT`, `DOT`, `CARET`, `INTER`, `UNION`, `NMEQ`, `NMNE`, `SEQ`, `SNE`, `EQUIV`, `NEQUIV` unary forms — verify which the oracle actually accepts).


---

### PARSER-IC-20 IN PROGRESS — whitespace pivot (session #70, 2026-05-06)

**Pivot:** Lon directed whitespace cleanup to match `parser_snocone.sc` canonical style.
WIP stashed in corpus (`git stash`). Baseline: PASS=143 FAIL=0 @ corpus `9509eac`.

**Bug found:** 4 augop regressions (`augop_concat`, `augop_mod`, `augop_numeq`, `augop_sub`) after grammar-body changes. Token defs correct in isolation. Root cause is in grammar body after `// push_qlit` — narrowed by binary search.

**Next session:**
1. `cd /home/claude/corpus && git stash pop` — restore WIP
2. Binary-search grammar body to isolate which production breaks augop FENCE matching
3. Fix; verify PASS=143 FAIL=0; add new fixtures
4. Commit and push

---

### PARSER-IC-20 LANDED PASS=143 corpus@961fa58

Whitespace cleanup (canonical snocone style) + newline=whitespace + semicolon terminates statements.

**Whitespace changes:**
- `white = SPAN(' ' tab nl) | '#' BREAK(nl) nl` — newlines now part of whitespace
- `White = white ARBNO(white); Gray = White | epsilon`
- `$' '` = Gray (optional), `$'  '` = White (required). DGray eliminated.

**Keyword tokens:** identifier boundary check via `Id $ tx *IDENT(tx, 'kw')` — prevents matching prefix of longer identifier (e.g., `do` in `done`).

**Structural keywords excluded from `id_pat`:** `stmt_kw = POS(0) ('end' | 'procedure' | 'record' | 'global') RPOS(0)` — prevents `end` being parsed as `(E_VAR end)`.

**Newlines as whitespace:** All `nl_one` anchors removed; `Blank` production removed. Statements terminate with `;`. Expressions can span lines freely. Verified: `x := 1\n    + 2\n    + 3;` parses as `(E_ASSIGN x (E_ADD (E_ADD 1 2) 3))`.

**SCRIP engine bug worked around:** `Gray = White | epsilon` (ALT node) causes `bb_alt` null-pointer crash inside `Case` production when used inside ARBNO+FENCE. Fix: `CaseGray = ARBNO(white)` used inside case productions. Filed as part of the `BUG-SCRIP-EQ` family.

**~~Next session (IC-21) [BOGUS — cross-pollination step removed]:~~** File CaseGray bug in GOAL-REWRITE-SCRIP.md. ~~Cross-pollinate `white/White/Gray` canonical style to other PARSER-* files.~~ Run rung36 jcon crosscheck. COMPLETE.

---

### PARSER-IC-20.1 LANDED PASS=143 corpus@4f4658b

Token list reorganized snocone-style; grammar body uses token aliases throughout.

**Token list categories (parser_snocone.sc style):**
- **Brackets** (asymmetric Gray): `$'(' = '(' $' '`, `$')' = $' ' ')'`, etc.
- **Punctuation** (Gray both sides): `$','`, `$';'`, `$':'`, `$'.'`
- **Operators** (Gray both sides for unary/binary dual-use): `$'+'`, `$'-'`, `$'*'`, etc.
- **Comparisons** (longer-prefix first): `$'~==='`, `$'~=='`, ... `$'='`, `$'<'`, `$'>'`
- **Assignment/swap**: `$':=:'`, `$':='`, `$'<->'`, `$'<-'`
- **Augmented assignment**: `$'~==:='` ... `$'=:='`

**Grammar body cleanup — no more raw whitespace + literal punct:**
- `Expr10` uses `$'-'`, `$'+'`, `$'*'`, `$'?'`, `$'/'`, `$'='` directly (not `$' ' '-'`)
- `Compound` uses `$'{'` / `$'}'` tokens
- `Case` uses `$'{'` / `$'}'` tokens
- `Expr11tail` uses `$'['` / `$']'` / `$':'` tokens
- `Paren` / `ListCtor` add explicit leading `$' '` (since open brackets have no leading Gray)
- `Params` uses `($'[' $']' | epsilon)` instead of raw brackets
- `InitialStmt` uses `$'{'` / `$'}'` tokens

The grammar body now contains **zero raw `(`/`)`/`[`/`]`/`{`/`}`/`,`/`;`/`:` literals adjacent to whitespace patterns** — all whitespace is encoded in the token aliases.

**~~Next session (IC-21) [BOGUS — cross-pollination not a PARSER-ICON task]:~~** ~~Cross-pollinate canonical style to `parser_prolog.sc`, `parser_raku.sc`, `parser_rebus.sc`.~~ File the SCRIP engine bugs (ARBNO-in-FENCE cursor restoration, ALT-in-FENCE bb_alt null-ptr) in `GOAL-REWRITE-SCRIP.md` as `BUG-SCRIP-EQ` family. Run rung36 jcon crosscheck. COMPLETE.

---

### PARSER-IC-21 LANDED PASS=143 FAIL=0

Filed SCRIP engine bugs RS-28 (ALT-in-FENCE bb_alt null-ptr) and RS-29 (ARBNO-in-FENCE cursor restoration) in `GOAL-REWRITE-SCRIP.md`. Cross-pollination of `white/White/Gray` canonical style attempted for `parser_prolog.sc`, `parser_raku.sc`, `parser_rebus.sc` — **blocked by RS-28/RS-29**:

- **Prolog**: `White = white ARBNO(white)` + `Gray = White | epsilon` → SIGSEGV (RS-28 crash). `Gray = ARBNO(white)` → tree divergence (ARBNO slides past operator chars per BUG-SCRIP-WS-1). Deferred until RS-28/RS-29 fixed.
- **Raku**: already worked around via BUG-SCRIP-WS-1. No safe change.
- **Rebus**: already canonical (`White = white ARBNO(white)`, `Gray = ARBNO(white)`). No change needed.

Rung36 jcon crosscheck: `test_parser_icon.sh` PASS=143 FAIL=0. IPL gprocs: 2/2 oracle-parseable PASS (grecords.icn, lindrec.icn); 138 skip (oracle rejects `link` decls). IC-22 confirmed parser covers 100% of oracle-accepted constructs. Constructs the oracle itself rejects (`link`, `invocable`, `create`, `@` activation) are out-of-scope pending LANG-IC ladder progress.

**Next session (IC-23):** Add fixtures for constructs added but not yet independently tested. Expand to match any new LANG-IC ladder features as they land.

---

### PARSER-IC-24 LANDED PASS=153 corpus@42e4ea3

671 → 631 lines (-40). Removed 35 E_* constant definitions (E_ASSIGN, E_IF,
E_WHILE, etc.), r_nTop, stmt_kw, kw_prefix — all inlined directly into grammar
body. All 153 fixtures PASS=153 FAIL=0.

**RS-28 blocker for further compaction**: Both-sides Gray on keyword tokens
(Lon's design: `$' ' Id $ tx *IDENT(tx,'kw') $' '`) triggers the RS-28
null-ptr crash in bb_alt when the trailing Gray ALT node appears inside FENCE
contexts in the expression tower. Fix: `Gray = ARBNO(white)` instead of
`White | epsilon` eliminates the ALT node. Filed under GOAL-REWRITE-SCRIP.md
RS-28. Op-based operator tokens (SPAN technique) and full whitespace compaction
deferred to IC-25 pending RS-28 resolution or Gray fix.

**Next (IC-25)**: Fix `Gray = ARBNO(white)` (no ALT node), then apply
both-sides Gray keywords + Op-based operators → target ~350 lines.
