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
benefit all six.  Naming & design principles canonical in
GOAL-PARSER-SNOCONE.md.

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

---

## Open rungs

### PARSER-IC-7 — parenthesized primary `( expr )` and compound `{ ... }`  ← **active**

- [ ] `Expr11` gains `'(' Expr ')'` and `'{' (Stmt)* '}'` primaries.
      Compound block produces `(E_SEQ_EXPR ...)` (or unwraps to single child
      per the existing-frontend rule in `parse_block_or_expr`).  Without
      these, `subj ? (r := "ok")` and `every gen do { s1; s2 }` cannot be
      written in fixtures even though the underlying parsers handle the
      pieces.
- **Sibling LANG rungs:** none required — both forms exist in the LANG
      ladder upstream.
- **Gate:** PASS≥45.

### PARSER-IC-8b parser_icon.sc rewrite to canonical spine  ← **next after IC-7**

With IC-8a landed, binary `~` and `&` are usable in pattern definitions
across all six PARSER-* parsers.  IC-8b retrofits parser_icon.sc's
inner tier patterns to the canonical shape exemplified by
parser_snocone.sc:

- [ ] Atom branches in `Expr11` use `(*Atom ~ s_TYPE)` (operator form)
      or `shift(*Atom, s_TYPE)` (functional form, equivalent post-IC-8a).
      No more `epsilon . *expr_from_atom('E_ILIT', _atom_text)`.
- [ ] Binary tier patterns (`Expr4tail`, `Expr6tail`, `Expr7tail`) use
      `*L *op *R (r_TAG & 2)` instead of `Tree(tag, '', 2, L, R)` direct
      construction.
- [ ] N-ary collectors (alternation E_ALTERNATE, function invocation
      E_FNC arglist) use the canonical
      `nPush() ARBNO(nInc() *X) (r_TAG & 'nTop()') nPop()` recipe — no
      more `$'@II'`/`$'@AL'` helper stacks.
- [ ] Statement decomposition (`(STMT :subj ...)` wrapping) follows
      parser_snocone.sc's `sc_decompose_stmt` shape: a single helper
      that pops the top tree and re-wraps; called via deferred action
      at the Stmt boundary.  This is the ONE remaining function — and
      it is tree-building/semantic, not parsing.
- [ ] All `_expr_node` global slot references removed.  All
      `Tree(tag, '', 2, L, R)` direct constructions removed.  All
      `expr_*` parsing-state helpers removed (the `$'@II'`,
      `$'@AL'`, `$'@SC'` stacks become redundant once trees flow on
      the shared shift/reduce stack).
- **Sibling cross-pollination:** parser_rebus.sc and parser_snobol4.sc
      owe the same retrofit; the canonical helpers (sq, s_*, r_*,
      sc_decompose_stmt-equivalent) should be lifted into a shared
      file in `corpus/programs/scrip/` so all six PARSER-* parsers
      share one source of truth.
- **Gate:** PASS=40 preserved (same fixtures, same trees); zero
      `Tree(tag, '', 2, L, R)` calls remain in parser_icon.sc; zero
      parsing-state global slots remain; driver remains structured
      (no goto, already done in IC-6).

---

## Invariants

- Icon's LANG ladder is the upstream pacer; PAT-IC does not race ahead.
- Test programs in `corpus/programs/icon/parser/` are owned by PAT-IC.
- `.ref` files captured at rung-land time.

---

## Watermark

PARSER-IC-7 (PARSER-IC-8a landed: SCRIP snocone_parse.y gains expr5a tier for binary `~` `&` `#` `%` OPSYN slots, lowering to `E_FNC` with operator literal as sval; Compiland in parser_icon.sc converted from `reduce("'Parse'", 'nTop()')` to `("'Parse'" & 'nTop()')` operator form; PASS=40, smoke=5; no Snocone test suite regressions.  PARSER-IC-6 also landed: every/do + scan).
