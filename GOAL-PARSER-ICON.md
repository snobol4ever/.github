# GOAL-PARSER-ICON.md — PARSER-ICON pattern-based frontend in Snocone

**Repo:** corpus+one4all
**Branch:** `pat` (one4all only — `corpus` and `.github` stay on `main`)
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
`tree`/`TDump`/`stack` from `corpus/programs/snocone/demo/beauty/`. Bug
fixes there benefit all six.

Icon shares broker mechanics with SNOBOL4 (BB_SCAN for pattern-match,
BB_PUMP for generators) per `GOAL-LANG-ICON`. Tree shape for Icon's
goal-directed expressions is the differentiator. The existing LANG-ICON
ladder is at IC-9; PAT-IC's later rungs wait for the LANG ladder to
mature features upstream.

---

## Naming & Design Principles  (canonical writeup in GOAL-PARSER-SNOCONE.md)

PARSER-* parsers must use names from:
1. The official BNF for the language being parsed (e.g. `snocone_parse.y`,
   `snobol4.y`, `rebus.y`, `raku.y`, `icon.y`, `prolog.y`).
   Tier names like `expr0`/`expr6`/`expr17` carry meaning across the
   ladder; hand-rolled aliases like `RhsExpr`/`ArithOp` do not.
2. The canonical Snocone self-host `beauty.sc` when the concept matches
   (`Integer`, `String`, `Id`, `Gray`, `White`, `$'='`, etc.).
3. `shift()`/`reduce()` from `ShiftReduce.sc` rather than manual
   `Push(Tree(...))` inside pattern escapes — the latter generates new
   Snocone synthetic labels per call, which can collide silently with
   labels in other `.sc` files in the same blob.
4. No new labels and goto unless absolutely necessary for readability.

See GOAL-PARSER-SNOCONE.md "Naming & Design Principles" for the full
writeup and the Session #62 lesson that motivated it.

---

## Session Setup

```bash
# Switch one4all to the shared parser branch. corpus and .github stay on main.
( cd /home/claude/one4all && git fetch origin parser 2>/dev/null; git checkout parser 2>/dev/null || git checkout -b parser origin/parser 2>/dev/null || git checkout -b parser )

bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
```

Gate after setup:
```bash
bash /home/claude/one4all/scripts/test_smoke_icon.sh           # existing frontend baseline
bash /home/claude/one4all/scripts/test_parser_icon.sh             # NEW — written under PARSER-IC-0
```

---

## Architecture reminder

```
scrip --parser-crosscheck parser_icon.sc tiny.icn
```

SCRIP runs `parser_icon.sc` (which `-include`s the shared SC library from
`corpus/programs/scrip/`) against `tiny.icn` — PAT produces IR tree t2
via `Compiland`; the existing frontend produces t1. Both compared in memory
(`tree_equal`), both executed in memory. No subprocesses, no temp files, no
on-disk diffs.

**Shared SC library** (`corpus/programs/scrip/` — tracked under PARSER-SN-INFRA-1):
```
tree.sc  stack.sc  counter.sc  ShiftReduce.sc  semantic.sc
```

Compiland spine:
```
Compiland = nPush() ARBNO(*Command) reduce('Parse', 'nTop()') nPop();
```

Icon-specific note: Icon's expression model is goal-directed — every
expression can succeed or fail and many can generate multiple values.
The IR tree carries this in the node tags (`SuccFail`, `AltGen`,
`Bound`). Token-level the language looks ALGOL-like; the semantics
divergence is in how trees are interpreted, not how they are shaped.

---

## Icon language reference (atom slice)

| Construct | Tree shape |
|-----------|------------|
| identifier `x` | `Name x` |
| integer `42` | `integer 42` |
| string `"hi"` | `string 'hi'` |
| `x := expr` | `(Stmt (Assign Name(x) ...))` |
| `procedure f(a) ... end` | `(Procedure f (Params a) Body)` |
| `if expr then s1 else s2` | `(If c Then Else)` |
| `every expr do s` | `(Every gen Body)` |
| `while expr do s` | `(While c Body)` |
| `expr1 \| expr2` (alternation) | `(AltGen e1 e2)` |
| `expr ? scan_body` | `(Scan subject Body)` |

(Full feature surface lives in `GOAL-LANG-ICON.md`.)

---

## Rung ladder

### PARSER-IC-0 — atom — **DONE** (session, this commit)

- [x] Write `corpus/programs/scrip/parser_icon.sc` with `Compiland`
      handling one identifier or one integer or one quoted string.
- [x] In-process two-frontend crosscheck.
- [x] Write `scripts/test_parser_icon.sh`.
- [x] Test corpus (3 NEW programs): `atom_id.icn`, `atom_int.icn`,
      `atom_str.icn`. `.ref` empty.
- **Sibling LANG rungs:** IC-1..IC-3 (lexer, atom).
- **Gate:** PASS=3. ✅

### PARSER-IC-1 — assignment (`x := expr`) — **DONE** (this commit)

- [x] `Command` handles Icon's `:=` assignment.
- [x] Test corpus: existing 3 atoms + **5 NEW** (assign_int, assign_str,
      assign_var, assign_mixed, assign_seq).  Note: spec said "existing
      2 + 3 NEW" — verified via PARSER-SC-1 reference: actual landed
      pattern is 3 + 5 = 8, matching the gate target.
- **Sibling LANG rungs:** IC-4.
- **Gate:** PASS=8. ✅

### PARSER-IC-2 — write / arith — **DONE** (this commit)

- [x] `Command` handles `write(expr)` calls and `+ - * /` operators.
- [x] Test corpus: existing 8 + **6 NEW** (write_str, write_int, write_var,
      arith_add, arith_sub, write_arith).
- **Sibling LANG rungs:** IC-5..IC-6.
- **Gate:** PASS=14. ✅

### PARSER-IC-INFRA-1 — check in canonical Icon BNF — **DONE** (this commit)

- [x] Add `corpus/programs/ebnf/icon-grammar.h` — verbatim upstream
      copy (gtownsend/icon `src/h/grammar.h`, public domain).
- [x] Add `corpus/programs/ebnf/icon-sp.ebnf` — 1-to-1 translation
      into the project dialect (pipe-alternation form).
- [x] Add `corpus/programs/ebnf/icon-no.ebnf` — vertical-ellipsis
      variant for symmetry with `s4-no.ebnf`.
- [x] Add `corpus/programs/ebnf/README.md` — dialect + provenance.
- [x] Add `corpus/programs/ebnf/icon-references/` — JCON `parse.icn`
      + COPYRIGHT + `NOTES.md` for cross-corroboration of canonical
      names and LL(1) decomposition guidance.
- [x] D2 nonterminal-name table updated to use the canonical
      `program/decls/proc/expr/expr1a/expr1.../expr11/literal/...`
      hierarchy from `grammar.h` instead of the wrong
      `icon_parse.c`-derived names.
- **Deliverable:** five files + one subdirectory committed, no
      parser_icon.sc change yet.
- **Gate:** files exist, license-clean (icon: public domain;
      jcon: ABoR redistribution license, notice preserved). ✅

### PARSER-IC-INFRA-2 — refactor parser_icon.sc to canonical names + Compiland-driven loop — **DONE** (this commit)

- [x] Renamed pattern names per D2 table — every pattern now mirrors
      the canonical `program/decls/proc/expr/expr1a/expr1.../expr11/
      literal/...` hierarchy from `corpus/programs/ebnf/icon-sp.ebnf`.
      `Program/Proc/Prochead/Procbody/Stmt/Expr/Expr1/Expr2/Expr6/
      Expr7/Expr11/Comment/Blank` are the new names.  No
      `AtomPat/BinOpPat/ExprPat/WriteLine/AssignExprLine/BodyAtom/
      LhsAtom/RhsAtom/AssignLine/AtomLine` left.
- [x] Applied LL(1) decomposition per `icon-references/NOTES.md` —
      every left-recursive `Exprn` is `Exprn = Expr_higher
      ARBNO(Exprn_tail)` where `Exprn_tail` is a separately-named
      pattern (because deferred actions inline inside `ARBNO(...)`
      don't fire reliably in this runtime — verified by probe — but
      `ARBNO(NamedPattern)` does fire its named pattern's actions).
- [x] Replaced goto/label state-machine main loop with `Compiland`
      PATTERN driving `ARBNO(Proc)` per D1.  Procbody handles
      end-keyword detection via explicit tail recursion
      (`Procbody = (ProcbodyEnd | Stmt *Procbody)`) instead of a
      hand-rolled state variable.  The two remaining `goto`s in the
      driver are tiny counted loops over data (stdin read; emit
      walker over the parse tree's children) — same shape as
      `parser_snobol4.sc`.
- [x] Per-level lhs-save variables (`_e1lhs`, `_e6lhs`, `_e7lhs`)
      avoid clobbering across the recursive Expr1 → Expr6 → Expr7
      call chain — Snocone variables are global, so each precedence
      level needs its own name.
- [x] Updated `scripts/test_parser_icon.sh` to include `counter.sc`
      and `semantic.sc` in the runtime blob (required by the
      canonical Compiland spine for `nPush`/`nInc`/`nTop`/`reduce`).
- [x] PAT-IC gate stays at PASS=14, FAIL=0.  `test_smoke_icon.sh`
      stays at PASS=5, FAIL=0.  No regression.
- [ ] Cross-pollinate to parser_snobol4.sc, parser_snocone.sc,
      parser_rebus.sc, parser_raku.sc, parser_prolog.sc — deferred
      until each language has its own INFRA-1 BNF landed.  Tracked
      in those goal files' Cross-pollination notice.
- **Gate:** PAT-IC PASS=14, smoke PASS=5. ✅

### PARSER-IC-3 — control flow (`if/then/else`, `while/do`) — **DONE** (this commit)

- [x] `Command` handles Icon's conditionals and loops.  Added `Expr4`
      (comparison ops `=` `~=` `<` `<=` `>` `>=`) between `Expr2` and
      `Expr6` per the canonical EBNF tower; restructured `Expr1` to
      commit on `id_pat ws_opt ':='` lookahead instead of `Expr2 ws_opt
      ':='` (the latter ate the entire if-expression as Expr2 and
      polluted `_expr_node` via deferred actions before backtracking).
      Added `If` (with optional `else` branch via inline `(else_branch
      | epsilon)` to avoid double-parse) and `While` patterns inside
      `Expr11`, tried before bare-IDENT to avoid greedy capture of
      reserved words.  New helpers `expr_assign_id`, `expr_if2`,
      `expr_if3`, `expr_while2`.
- [x] Test corpus: existing 14 + **6 NEW** (cmp_eq, cmp_lt, if_then,
      if_else, if_cmp, while_do).
- [x] **Bug fix in `corpus/programs/scrip/tdump.sc` (cross-pollination
      benefit to all six PARSER-* parsers):** TDump's multi-line
      fallback was guarded by `if (~(NULL *IDENT(n(x))))`, which is a
      no-op — `NULL *IDENT(...)` is a pattern-construction expression
      that cannot fail at construction time, so `~(pattern_value)` is
      always FAIL and the multi-line branch was **never** entered.
      The bug never triggered before IC-3 because every prior PARSER-*
      tree fit inside TLump's 140-char one-line budget; IC-3's
      if/then/else trees (~152 chars) are the first to exceed it.
      Replaced with `if (DIFFER(n(x)))`.  Also extended the multi-line
      branch to mirror TLump's role-slot (`:`-prefix tag) handling and
      its internal-node `v(x)` sval emission, otherwise wide trees
      came out as `(STMT (":subj" (E_FNC (E_VAR main) ...)))` instead
      of `(STMT :subj (E_FNC main (E_VAR main) ...))`.  This is a
      **fix to the corpus shared library**, not a workaround in
      `parser_icon.sc` — the fix is in the file and benefits Snocone,
      SNOBOL4, Prolog, Rebus, Raku as soon as they hit a tree wider
      than 140 chars.  Note inherited from beauty source
      (`corpus/programs/snocone/demo/beauty/TDump.sc`) — that file
      should get the same treatment under whichever goal owns it.
- **Sibling LANG rungs:** IC-7..IC-8.
- **Gate:** PASS=20, FAIL=0.  smoke=5/0.  parser_snobol4=16/0,
      parser_prolog=18/0, parser_rebus=8/0 (no regression — same
      pre-existing parser_snocone 8/5 failure unrelated). ✅

### PARSER-IC-4 — procedure definition — **DONE** (this commit)

- [x] `Command` handles `procedure NAME(args) ... end`.  Generalized
      `Prochead` from the IC-2/IC-3-hardcoded `'procedure' ws_run 'main'
      ws_opt '(' ws_opt ')'` shape to `'procedure' ws_run id_pat
      ws_opt '(' ws_opt Arglist ws_opt ')'` — any procedure name, any
      arity.  New patterns: `ProcParam` (single param identifier),
      `ParamRest` (the `, IDENT` tail under ARBNO), `Arglist` (head +
      tail or empty).  The procedure's name is captured via
      `id_pat . _ic_pname` and seeded onto `_proc_node` by
      `*start_proc(_ic_pname)` (renamed from `start_proc_main()`).
      Each parameter appends an `(E_VAR <name>)` child onto _proc_node
      via `*append_proc_param(...)`, matching the existing frontend's
      tree shape: `(E_FNC f (E_VAR f) (E_VAR a) (E_VAR b) <body...>)`.
- [x] `return [expr];` recognized at the Stmt level (not Expr).  New
      `ReturnStmt` pattern alternation: with-value tried first
      (`'return' ws_run *Expr`), bare-return fallback second
      (`'return' ws_opt semi_opt`).  Builds `(E_RETURN expr)` or bare
      `(E_RETURN)`.  Tried before generic Expr-as-stmt so `return` is
      not consumed as a bare identifier.
- [x] **Variadic function invocation** in `Expr11`.  IC-2/IC-3 had
      single-arg `IDENT '(' Expr ')'`; IC-4 needs `IDENT '(' (Expr (','
      Expr)*)? ')'` — including the no-arg form `f()`.  Implemented
      via a dedicated invocation-construction stack `$'@II'` (cons-list
      via `struct ic_ilink { next, ival }`), parallel to the shared
      Compiland stack.  Push at `(`, append-on-top at each comma-
      separated arg, pop at `)`.  The stack is REQUIRED (not a
      single-slot global) because invocations nest: `write(double(5))`
      enters `double(5)`'s build phase while `write(...)` is still in
      progress, and a single global slot would clobber.
- [x] Test corpus: existing 20 + **7 NEW** (proc_simple, proc_oneparam,
      proc_twoparam, proc_call_noargs, proc_call_onearg,
      proc_call_twoargs, proc_return).
- **Sibling LANG rungs:** IC-9 (current active).
- **Gate:** PASS=27, FAIL=0.  smoke=5/0.  Cross-pollination: no
      regression in parser_snobol4=23/0, parser_prolog=18/0,
      parser_rebus=12/0 (those advanced via concurrent sessions; my
      changes are isolated to parser_icon.sc).  Pre-existing
      parser_snocone=0/13 is upstream-broken (session #63) —
      unaffected by IC-4. ✅

### PARSER-IC-5 — alternation generators (`expr1 | expr2`)

- [ ] `Command` handles `|` between expressions in generator context.
      Same lowering shape as Rebus; cross-pollinate.
- **Sibling LANG rungs:** IC-10 (when it lands).
- **Gate:** PASS≥33.

### PARSER-IC-6 — `every/do` and `expr ? scan` (string scanning)

- [ ] `Command` handles `every expr do s` (generator-driven loop) and
      `expr ? scan_body` (string scanning context — BB_SCAN).
- **Sibling LANG rungs:** IC-11..IC-13 (when they land).
- **Gate:** PASS≥40.

---

## Design issues — flagged session #62 (Lon, 2026-05-03)

These three issues were raised after PARSER-IC-2 landed PASS=14.
The IC-2 commit followed the IC-0/IC-1 template uncritically; the
template itself has these problems and they apply to all six PARSER-*
frontends (cross-pollination scope).

### D1 — Eliminate goto/label main loops

The existing driver loop in `parser_icon.sc` is:

```
main00: ... goto stateHeader / goto stateBody / goto mainErr;
stateHeader: ... goto main00;
stateBody:   ... goto main00 / goto stmtEnd / goto mainErr;
stmtEnd:     ... goto main00;
mainErr:     ... goto main00;
mainEnd: ...
```

This is a hand-rolled state machine in goto/label form because the
template predates `Compiland` being able to do the dispatch as a
PATTERN. The Snocone way is a single top-level `Compiland` PATTERN
that consumes the source via `ARBNO(*Command)` (per the architecture
reminder above), with `Command` being an alternation of all line
forms. No labels, no gotos, no `_proc_state` integer. The shape:

```
Command = ( ProcHeader | ProcEnd | WriteCall | AssignExpr | AtomBody | Comment | Blank );
Compiland = nPush() ARBNO(*Command) reduce('Parse', 'nTop()') nPop();
```

Goto is only justified when readability **requires** it (e.g., escape
from deeply nested loops); the current loop does not require it.

### D2 — Names must mirror existing code, not invent new ones

PAT-IC currently invents pattern names (`AtomPat`, `BinOpPat`,
`ExprPat`, `WriteLine`, `AssignExprLine`, `BodyAtom`, `LhsAtom`,
`RhsAtom`, `AssignLine`, `AtomLine`).

The canonical Icon grammar — `corpus/programs/ebnf/icon-sp.ebnf`,
landed under PARSER-IC-INFRA-1, which is a 1-to-1 translation of
upstream gtownsend/icon `src/h/grammar.h` (public domain) — defines
every nonterminal name PAT-IC must use. Production names are
**numbered by precedence** (`expr1` through `expr11`), not named
after operator class. This is intentional — the upstream grammar
intentionally separates structural precedence from operator
semantics.

Canonical Snocone nonterminal names (CamelCase pattern, lowercase
in the EBNF):

| EBNF nonterminal | PAT-IC pattern  | Notes |
|------------------|-----------------|-------|
| `program`        | `Program`       | Top of grammar. |
| `decls` / `decl` | `Decls` / `Decl`| Declarations list. |
| `proc`           | `Proc`          | `procedure ... end`. |
| `prochead`       | `Prochead`      | Procedure header. |
| `procbody`       | `Procbody`      | Procedure body. |
| `record`         | `Record`        | `record ID(...)`. |
| `global`         | `Global`        | `global ID, ID, ...`. |
| `link`           | `Link`          | `link "..."`. |
| `invocable`      | `Invocable`     | `invocable ...`. |
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

The PAT-IC convention: take the EBNF nonterminal name, capitalize
the first letter. Multi-word names stay solid (`Prochead` not
`ProcHead`) because the upstream is solid. The IC-2 `AssignLine` /
`AssignExprLine` pair collapses into part of `Expr1` per the
canonical grammar.

### D3 — Should be driven by an official BNF — **landed via INFRA-1**

The canonical Icon BNF is the yacc grammar in upstream
gtownsend/icon, file `src/h/grammar.h` — explicitly public domain
("This material is in the public domain. You may use and copy this
material freely." — gtownsend/icon README). PAT-IC mirrors this
grammar verbatim rather than re-deriving anything from
`icon_parse.c`. The C parser is itself a translation of this BNF;
using it as the shape source was one indirection too many.

**Provenance confirmed (session #62, Lon-supplied uploads):**
`icon-master.zip` and `jcon-master.zip` were checked against the
in-corpus copy. `icon-master/src/h/grammar.h` is byte-identical to
`corpus/programs/ebnf/icon-grammar.h`. JCON's independent LL(1)
recursive-descent parser (`jcon-master/tran/parse.icn`) uses the
exact same nonterminal hierarchy — its 43 `parse_*` procedures map
1-to-1 to the productions in `grammar.h`. Two independent
implementations (one yacc, one hand-rolled in Icon) converge on
the same names. `parse.icn` is now in
`corpus/programs/ebnf/icon-references/` for cross-reference.

**Landed under PARSER-IC-INFRA-1:**

- `corpus/programs/ebnf/icon-grammar.h` — verbatim upstream copy
  (provenance preserved, never edit).
- `corpus/programs/ebnf/icon-sp.ebnf` — pipe-alternation EBNF in
  the project dialect (1-to-1 with `icon-grammar.h`).
- `corpus/programs/ebnf/icon-no.ebnf` — vertical-ellipsis variant.
- `corpus/programs/ebnf/icon-references/` — JCON `parse.icn` +
  COPYRIGHT, `NOTES.md` documenting cross-corroboration and the
  LL(1) decomposition that INFRA-2 will need.
- `corpus/programs/ebnf/README.md` — provenance + dialect notes.

### LL(1) decomposition note for INFRA-2

Snocone patterns cannot left-recurse. `grammar.h` is left-recursive
throughout — `expr2 TO expr3`, `expr5 CONCAT expr6`, `expr6 PLUS
expr7`, `expr7 STAR expr8`, `expr11 LBRACK exprlist RBRACK`, etc.
INFRA-2 must decompose each left-recursive production the way JCON
does it: `Exprn = Exprn_plus_one (op Exprn_plus_one)*` via
`ARBNO(...)`. JCON also splits `expr11` into `parse_expr11a`
(literals + control structures + parenthesized expressions) plus
`parse_expr11suffix(lhs)` (postfix `[...]`, `{...}`, `(...)`, `.id`).
PAT-IC INFRA-2 mirrors that split: `Expr11 = Expr11a Expr11suffix`.

Same treatment is owed to the other five PARSER-* frontends:
`snobol4-*.ebnf` already exists; add `snocone-*.ebnf`,
`rebus-*.ebnf`, `prolog-*.ebnf`, `raku-*.ebnf` from their
respective canonical upstream grammars. Tracked under each
PARSER-*'s own INFRA-1 sub-rung (cross-pollination).

These three issues compose: D3 supplies the names, D2 enforces the
discipline of using them, D1 removes the dispatch-loop scaffolding
that is already obsolete.

---

## Invariants

- Icon's LANG ladder is at IC-9 active; PAT-IC does not race ahead.
- Test programs in `corpus/programs/icon/parser/` are owned by PAT-IC.
- `.ref` files captured at rung-land time.

---

## Watermark

PARSER-IC-5 (PARSER-IC-4 landed: `procedure NAME(args) ... end` with arbitrary names + variadic params, `return [expr]`, variadic invocation via dedicated `$'@II'` stack supporting nested calls; PASS=27, smoke=5; one4all parser branch HEAD `ac93b50a`, corpus HEAD `e7a0866`).
