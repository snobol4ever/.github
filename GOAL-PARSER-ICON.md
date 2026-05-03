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

### PARSER-IC-INFRA-1 — check in canonical Icon BNF — **next (highest priority)**

- [ ] Add `corpus/programs/ebnf/icon.ebnf` — Griswold & Griswold
      Appendix B BNF in the dialect already used for SNOBOL4.
- [ ] Cross-link from goal file: every active rung from PARSER-IC-3
      onward must cite the BNF production it implements.
- **Deliverable:** one file checked in, no code changes.
- **Gate:** file exists, parses with the existing EBNF tool
      (`corpus/programs/lon/sno/ebnf.exe`).

### PARSER-IC-INFRA-2 — refactor parser_icon.sc to canonical names + Compiland-driven loop

- [ ] Rename invented pattern names per D2 table (table in Design
      issues section above).
- [ ] Replace goto/label main loop with `Compiland` PATTERN driving
      `ARBNO(*Command)` per D1.
- [ ] Cross-pollinate: parser_snobol4.sc, parser_snocone.sc,
      parser_rebus.sc, parser_raku.sc, parser_prolog.sc receive the
      same naming / structure update.
- [ ] All existing test gates stay green — PAT-SN, PAT-IC PASS=14,
      others.
- **Gate:** every PARSER-* gate green, no PASS regression. ✅ first
      then proceed to IC-3.

### PARSER-IC-3 — control flow (`if/then/else`, `while/do`)

- [ ] `Command` handles Icon's conditionals and loops.
- [ ] Test corpus: existing + **NEW**.
- **Sibling LANG rungs:** IC-7..IC-8.
- **Gate:** PASS≥20.

### PARSER-IC-4 — procedure definition

- [ ] `Command` handles `procedure f(args) ... end`.
- **Sibling LANG rungs:** IC-9 (current active).
- **Gate:** PASS≥27.

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
`RhsAtom`, `AssignLine`, `AtomLine`). The existing Icon frontend
(`src/frontend/icon/icon_parse.c`) is a recursive-descent parser
whose function names already define the canonical nonterminal
hierarchy:

```
parse_primary, parse_postfix, parse_unary, parse_limit,
parse_pow, parse_mul, parse_add, parse_cset, parse_concat,
parse_rel, parse_and, parse_to, parse_alt, parse_assign,
parse_expr, parse_block_or_expr, parse_do_clause, parse_stmt,
parse_record, parse_proc
```

PAT-IC patterns must use these names (dropping the `parse_` prefix
since PAT-IC's nonterminals **are** patterns, not procedures).
Canonical Snocone nonterminal names for IC-3+:

| C function       | PAT-IC pattern  |
|------------------|-----------------|
| `parse_primary`  | `Primary`       |
| `parse_postfix`  | `Postfix`       |
| `parse_unary`    | `Unary`         |
| `parse_limit`    | `Limit`         |
| `parse_pow`      | `Pow`           |
| `parse_mul`      | `Mul`           |
| `parse_add`      | `Add`           |
| `parse_concat`   | `Concat`        |
| `parse_rel`      | `Rel`           |
| `parse_and`      | `And`           |
| `parse_to`       | `To`            |
| `parse_alt`      | `Alt`           |
| `parse_assign`   | `Assign`        |
| `parse_expr`     | `Expr`          |
| `parse_stmt`     | `Stmt`          |
| `parse_proc`     | `Proc`          |

The IC-2 `AssignLine` / `AssignExprLine` pair collapses into one
`Assign` pattern that uses `Expr` on the rhs.

### D3 — Should be driven by an official BNF

The canonical Icon BNF lives in *The Icon Programming Language*,
3rd ed., Griswold & Griswold, Appendix B. PAT-IC should mirror
that grammar verbatim rather than re-deriving the precedence tower
from `icon_parse.c`. The C parser is itself a translation of that
BNF; using it as the shape source is one indirection too many.

**Action item:** check in `corpus/programs/ebnf/icon.ebnf` (the
canonical Icon BNF in the same EBNF dialect already used for
`s4-sp.ebnf` / `s4-no.ebnf`). Every PAT-IC nonterminal name then
maps 1-to-1 to a production in that BNF file. Same treatment for
the other five PARSER-* frontends — `snobol4.ebnf` already exists;
add `snocone.ebnf`, `rebus.ebnf`, `prolog.ebnf`, `raku.ebnf`. Track
this under PARSER-IC-INFRA-1 (new sub-rung, not an active IC-N).

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

PARSER-IC-INFRA-1 (PARSER-IC-2 landed: PASS=14; design issues D1/D2/D3 raised — INFRA-1 + INFRA-2 must land before IC-3).
