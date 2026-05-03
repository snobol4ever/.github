# GOAL-PAT-PROLOG.md — PAT-PROLOG pattern-based frontend in Snocone

**Repo:** corpus+one4all
**Sibling ladder:** `GOAL-LANG-PROLOG.md` and `GOAL-PROLOG-IR-RUN.md`. The
existing Prolog frontend (`src/frontend/prolog/`) is the in-process oracle.

**Done when:** A Snocone program `pat_prolog.sc` reads Prolog source,
runs one `Compiland` PATTERN that builds the canonical IR tree, and for
every test program in the rung corpus
`tree_equal(existing_frontend_tree, pat_prolog_tree)` returns true.
Where a `.ref` file exists, executing both trees through the IR
interpreter produces byte-identical output.

---

## Cross-pollination

All six PAT-* parsers share `Compiland`/`Shift`/`Reduce`/`Push`/`Pop`/`Top`/
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

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
```

Gate after setup:
```bash
bash /home/claude/one4all/scripts/test_smoke_prolog.sh         # existing frontend baseline
bash /home/claude/one4all/scripts/test_pat_prolog.sh           # NEW — written under PAT-PR-0
```

---

## Architecture reminder

```
source.pl
   │
   ├─→ prolog_compile() → CODE_t* t1   (existing frontend)
   │
   └─→ pat_prolog.sc Compiland → CODE_t* t2

tree_equal(t1, t2) → primary gate
execute(t1) vs execute(t2) → secondary gate (where .ref exists)
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

## Prolog language reference (atom slice)

| Construct | Tree shape |
|-----------|------------|
| atom `foo` (lowercase) | `Atom foo` |
| variable `X` (uppercase) | `Var X` |
| variable `_x` | `Var _x` |
| integer `42` | `integer 42` |
| string `"hi"` | `string 'hi'` |
| compound `f(a, b)` | `(Compound f (Args ...))` |
| list `[a, b, c]` | `(List ...)` |
| fact `fact.` | `(Clause head=fact body=true)` |
| rule `head :- body.` | `(Clause head body)` |
| conjunction `a, b` | `(And a b)` |
| disjunction `a ; b` | `(Or a b)` |
| query `?- goal.` | `(Query goal)` |

(Full feature surface lives in `GOAL-LANG-PROLOG.md`.)

---

## Rung ladder

### PAT-PR-0 — atom — **next**

- [ ] Write `corpus/programs/prolog/pat/pat_prolog.sc` with `Compiland`
      handling one Prolog atom (lowercase identifier), one variable
      (uppercase or `_`-prefixed), one integer, or one quoted string,
      followed by `.`.
- [ ] In-process two-frontend crosscheck.
- [ ] Write `scripts/test_pat_prolog.sh`.
- [ ] Test corpus (4 NEW programs): `atom_lower.pl`, `atom_var.pl`,
      `atom_int.pl`, `atom_str.pl`. `.ref` empty.
- **Sibling LANG rungs:** PR-1..PR-3 (lexer, atom/var distinction).
- **Gate:** PASS=4.

### PAT-PR-1 — facts (`name.` or `name(args).`)

- [ ] `Command` handles bare facts (zero-arg compound) and compound
      facts `f(a, b, c).`.
- [ ] Test corpus: existing thin Prolog fact tests + **NEW**.
- **Sibling LANG rungs:** PR-4..PR-6.
- **Gate:** PASS≥10.

### PAT-PR-2 — rules (`head :- body.`)

- [ ] `Command` handles rules with a single goal in the body.
- [ ] Test corpus: existing + **NEW**.
- **Sibling LANG rungs:** PR-7..PR-9.
- **Gate:** PASS≥17.

### PAT-PR-3 — conjunction / disjunction (`,` / `;`)

- [ ] `Command` handles `a, b, c` and `a ; b` in goal position.
- [ ] Test corpus: existing + **NEW**.
- **Sibling LANG rungs:** PR-10..PR-12.
- **Gate:** PASS≥24.

### PAT-PR-4 — lists (`[H|T]` / `[a,b,c]`)

- [ ] `Command` handles list syntax including head/tail bar.
- **Sibling LANG rungs:** PR-13..PR-15.
- **Gate:** PASS≥30.

### PAT-PR-5 — arithmetic (`is`, builtin operators)

- [ ] `Command` handles `X is Expr` and the arithmetic operators.
- **Sibling LANG rungs:** PR-16..PR-17 (current active includes string
      builtins rung40).
- **Gate:** PASS≥38.

### PAT-PR-6 — queries / directives

- [ ] `Command` handles `?- goal.` queries.
- **Sibling LANG rungs:** PR-18 (when it lands).
- **Gate:** PASS≥45.

---

## Invariants

- Prolog's LANG ladder is at PR-17 active; PAT-PR does not race ahead.
- Test programs in `corpus/programs/prolog/pat/` are owned by PAT-PR.
- `.ref` files captured at rung-land time.
- Variables vs atoms distinction is first-class in the token classifier;
  do not collapse them and rebuild later — get it right at PAT-PR-0.

---

## Watermark

PAT-PR-0 (initial — no .sc parser exists yet).
