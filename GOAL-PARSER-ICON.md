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

---

## Open rungs

### PARSER-IC-9 — augmented assigns + unary prefix + power  ← **next**

With the canonical spine in place (IC-8b), adding new operators is
mechanical: each new tier follows the `*L $'op' *R (r_TAG & N)` recipe
already established by Expr4/Expr6/Expr7.  Likely components, in
upstream pacer order:

- [ ] Augmented assigns at `Expr1`: `+:=` `-:=` `*:=` `/:=` `:=:` etc.
      Each lowers to its dedicated tag (E_AUGADD, E_AUGSUB, ...) per
      the existing frontend's --dump-ir output.  Add fixture per op.
- [ ] Unary prefix at `Expr10`: `-` `+` `~` `!` `*` `?` `@` `^` `\`.
      Each `'op' *Expr10 (r_TAG & 1)` chain into a new Expr10 tier.
      Add fixtures.
- [ ] Power `^` at `Expr8` (right-associative): `*Expr10 ($'^' *Expr8 (r_POW & 2) | epsilon)`.
- **Gate:** PASS≥50 (5+ NEW fixtures across the new operators).

Cross-pollination: same retrofit pattern applies to parser_rebus.sc
and parser_snobol4.sc — separate goal, see GOAL-PARSER-SNOBOL4.md and
GOAL-PARSER-REBUS.md.

---

## Invariants

- Icon's LANG ladder is the upstream pacer; PAT-IC does not race ahead.
- Test programs in `corpus/programs/icon/parser/` are owned by PAT-IC.
- `.ref` files captured at rung-land time.

---

## Watermark

PARSER-IC-9 (PARSER-IC-8b LANDED PASS=45 preserved: parser_icon.sc rewritten to canonical shift/reduce spine — `*L $'op' *R (r_TAG & 2)` binary tiers, `nPush() ARBNO(nInc() *X) (r_TAG & r_nTop) nPop()` n-ary collectors, `r_nTop = '*(GT(nTop(),1) nTop())'` for E_SEQ_EXPR single-child unwrap, ONE helper `ic_decompose_proc` for `(STMT :subj E_FNC pname kids)` re-wrap; zero `_expr_node`/`@II`/`@AL`/`@SC`/`@SQ` parsing-state; 871 → 366 lines (−505).  Subsequent style cleanup at corpus@de9ff24: invisible-whitespace tokens `$' ' = ws_opt` and `$'  ' = ws_run`, plus nine `$'kw'` keyword tokens (`$'if' $'then' $'else' $'while' $'do' $'every' $'return' $'end' $'procedure`); operator-token RHS uniformly `($' ' 'op' $' ')`; PASS=45 preserved.  PARSER-IC-7 ALSO LANDED: paren / compound primaries + beauty-style `$'op'` refactor, corpus@c6e4c2b).
