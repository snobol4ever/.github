# GOAL-PARSER-PROLOG.md — PARSER-PROLOG pattern-based frontend in Snocone

**Repo:** corpus+one4all
**Branch:** `pat` (one4all only — `corpus` and `.github` stay on `main`)
**Sibling ladder:** `GOAL-LANG-PROLOG.md` and `GOAL-PROLOG-IR-RUN.md`. The
existing Prolog frontend (`src/frontend/prolog/`) is the in-process oracle.

**Done when:** A Snocone program `parser_prolog.sc` reads Prolog source,
runs one `Compiland` PATTERN that builds the canonical IR tree, and for
every test program in the rung corpus
`tree_equal(existing_frontend_tree, parser_prolog_tree)` returns true.
Where a `.ref` file exists, executing both trees through the IR
interpreter produces byte-identical output.


> **Cross-pollination notice (session #62, 2026-05-03):** three design
> issues raised against PAT-IC apply to all six PARSER-* frontends.
> See `GOAL-PARSER-ICON.md ## Design issues` (D1: drop goto/label
> driver loops; D2: nonterminal names must mirror the existing
> frontend, not invent new ones; D3: drive from a checked-in BNF in
> `corpus/programs/ebnf/`). Tracked under PARSER-IC-INFRA-1 and
> PARSER-IC-INFRA-2 — when those rungs land, the same refactor lands
> on this parser too.

---

## Cross-pollination

All six PARSER-* parsers share `Compiland`/`Shift`/`Reduce`/`Push`/`Pop`/`Top`/
`tree`/`TDump`/`stack` from `corpus/programs/snocone/demo/beauty/`. Bug
fixes there benefit all six.

Prolog is the most syntactically distinct of the six — clauses (`head :-
body.`), facts (`fact.`), terms with arity (`f(a, b)`), variables (uppercase
or `_`-prefixed), atoms (lowercase). The token model and clause shape
differ enough from the imperative five that PAT-PR's `Command` body has
the least overlap with the others. The Compiland spine is still identical.

LANG-PROLOG is at PR-17 active (string builtins rung40); PAT-PR follows
behind, never racing.

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
bash /home/claude/one4all/scripts/test_smoke_prolog.sh         # existing frontend baseline
bash /home/claude/one4all/scripts/test_parser_prolog.sh           # NEW — written under PARSER-PR-0
```

---

## Architecture reminder

```
scrip --parser-crosscheck parser_prolog.sc tiny.pl
```

SCRIP runs `parser_prolog.sc` (which `-include`s the shared SC library from
`corpus/programs/scrip/`) against `tiny.pl` — PAT produces IR tree t2
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

Prolog-specific note: in PROLOG the unit of work is the clause, not the
statement. So PAT-PR's `Command` reduces to a `Clause` node (fact or
rule), and the program tree is `(Parse (Clause ...) (Clause ...) ...)`.
Variables (capitalized or `_`-prefixed) are distinct lexical class from
atoms (lowercase) — token classification matters earlier here than in
the other five languages.

---

## Naming policy — anchor on ISO Prolog BNF + existing frontend

⛔ Non-terminal and token names in `parser_prolog.sc` MUST match the
existing Prolog frontend's vocabulary, not be invented. The cross-PARSER
spine names (`Compiland`, the helper functions `Push`/`Pop`/`Top`, etc.)
are the only invented names — those are shared across all six PARSER-*.

**Token names** — directly from `src/frontend/prolog/prolog_lex.h`:
`TK_ATOM`, `TK_VAR`, `TK_ANON`, `TK_INT`, `TK_FLOAT`, `TK_STRING`,
`TK_LPAREN`, `TK_RPAREN`, `TK_LBRACKET`, `TK_RBRACKET`, `TK_PIPE`,
`TK_COMMA`, `TK_DOT`, `TK_LBRACE`, `TK_RBRACE`, `TK_OP`, `TK_NECK`,
`TK_QUERY`, `TK_CUT`, `TK_SEMI`.

**Non-terminal names** — from `src/frontend/prolog/prolog_parse.c`:
`clause`, `term`, `primary`, `args`, `list`. These align with ISO/IEC
13211-1 BNF (ISO uses `clause`, `term`, `arg_list`, `list`).

**IR node names (oracle output)** — from `prolog_lower.c::expr_dump`:
`E_CHOICE`, `E_CLAUSE`, `E_UNIFY`, `E_CUT`, `E_FNC`, `E_QLIT`, `E_ILIT`,
`E_FLIT`, `E_VAR`, `E_ADD`, `E_SUB`, `E_MUL`, `E_DIV`. Parser-built trees
must use these exact tags so `tree_equal` / `--dump-ir` crosscheck holds.

(Full feature surface and the ISO BNF reference live in
`GOAL-LANG-PROLOG.md`.)

---

## Rung ladder

### PARSER-PR-0 — atom — **LANDED**

- [x] Write `corpus/programs/scrip/parser_prolog.sc` with `Compiland`
      handling one Prolog atom (lowercase identifier), one variable
      (uppercase or `_`-prefixed), one integer, or one quoted string,
      followed by `.`.
- [x] In-process two-frontend crosscheck.
- [x] Write `scripts/test_parser_prolog.sh`.
- [x] Test corpus (4 NEW programs): `atom_lower.pl`, `atom_var.pl`,
      `atom_int.pl`, `atom_str.pl`. `.ref` empty.
- **Sibling LANG rungs:** PR-1..PR-3 (lexer, atom/var distinction).
- **Gate:** PASS=4. ✅

### PARSER-PR-1 — facts (`name.` or `name(args).`) — **next**

- [ ] `Command` handles bare facts (zero-arg compound) and compound
      facts `f(a, b, c).`.
- [ ] Test corpus: existing thin Prolog fact tests + **NEW**.
- **Sibling LANG rungs:** PR-4..PR-6.
- **Gate:** PASS≥10.

### PARSER-PR-2 — rules (`head :- body.`)

- [ ] `Command` handles rules with a single goal in the body.
- [ ] Test corpus: existing + **NEW**.
- **Sibling LANG rungs:** PR-7..PR-9.
- **Gate:** PASS≥17.

### PARSER-PR-3 — conjunction / disjunction (`,` / `;`)

- [ ] `Command` handles `a, b, c` and `a ; b` in goal position.
- [ ] Test corpus: existing + **NEW**.
- **Sibling LANG rungs:** PR-10..PR-12.
- **Gate:** PASS≥24.

### PARSER-PR-4 — lists (`[H|T]` / `[a,b,c]`)

- [ ] `Command` handles list syntax including head/tail bar.
- **Sibling LANG rungs:** PR-13..PR-15.
- **Gate:** PASS≥30.

### PARSER-PR-5 — arithmetic (`is`, builtin operators)

- [ ] `Command` handles `X is Expr` and the arithmetic operators.
- **Sibling LANG rungs:** PR-16..PR-17 (current active includes string
      builtins rung40).
- **Gate:** PASS≥38.

### PARSER-PR-6 — queries / directives

- [ ] `Command` handles `?- goal.` queries.
- **Sibling LANG rungs:** PR-18 (when it lands).
- **Gate:** PASS≥45.

---

## Invariants

- Prolog's LANG ladder is at PR-17 active; PAT-PR does not race ahead.
- Test programs in `corpus/programs/prolog/parser/` are owned by PAT-PR.
- `.ref` files captured at rung-land time.
- Variables vs atoms distinction is first-class in the token classifier;
  do not collapse them and rebuild later — get it right at PARSER-PR-0.

## Style invariants (parser_prolog.sc)

- **No `goto`/labels** in the driver loop or anywhere else in
  `parser_prolog.sc` unless absolutely necessary for readability.
  `parser_snobol4.sc`'s `goto read_loop` / `goto read_done` style is
  legacy — use `while`-style structured flow (`while ((Line = INPUT))
  { Src = Src Line nl; }`) for the source-accumulator and result loop.
- **Names match the existing frontend.** Non-terminal names in the
  Snocone grammar mirror `prolog_parse.c`'s `parse_clause`/`parse_term`/
  `parse_primary`/`parse_args`/`parse_list`. Token-classifier names
  mirror `prolog_lex.h`'s `TK_*` (lowercased where Snocone identifier
  rules require). IR tags mirror `prolog_lower.c::expr_dump`'s
  `E_CLAUSE`/`E_CHOICE`/`E_VAR`/`E_ILIT`/`E_QLIT`/`E_FNC` etc.
- **Anchor on the BNF.** Where the existing frontend's names diverge
  from ISO/IEC 13211-1, prefer the ISO name only when ISO is also the
  name used in `GOAL-LANG-PROLOG.md`. Do not invent.

---

## Watermark

PARSER-PR-0 LANDED (PASS=4). Next: PARSER-PR-1 — compound facts.
