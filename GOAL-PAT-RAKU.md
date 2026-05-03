# GOAL-PAT-RAKU.md — PAT-RAKU pattern-based frontend in Snocone

**Repo:** corpus+one4all
**Branch:** `pat` (one4all only — `corpus` and `.github` stay on `main`)
**Sibling ladder:** `GOAL-LANG-RAKU.md` and `GOAL-RAKU-FRONTEND.md`. The
existing Raku frontend (`src/frontend/raku/`) is the in-process oracle.

**Done when:** A Snocone program `pat_raku.sc` reads Raku source, runs
one `Compiland` PATTERN that builds the canonical IR tree, and for every
test program in the rung corpus
`tree_equal(existing_frontend_tree, pat_raku_tree)` returns true. Where
a `.ref` file exists, executing both trees through the IR interpreter
produces byte-identical output.

---

## Cross-pollination

All six PAT-* parsers share `Compiland`/`Shift`/`Reduce`/`Push`/`Pop`/`Top`/
`tree`/`TDump`/`stack` from `corpus/programs/snocone/demo/beauty/`.
Bug fixes there benefit all six.

Raku is the youngest frontend in the family and the active LANG-RAKU
ladder is at RK-34 — pattern-match and grammar features are the active
work upstream. PAT-RK starts strictly atom-and-assignment to give the
LANG ladder room to mature, then climbs toward grammars in lockstep.

---

## Session Setup

```bash
# Switch one4all to the shared PAT branch. corpus and .github stay on main.
( cd /home/claude/one4all && git fetch origin pat 2>/dev/null; git checkout pat 2>/dev/null || git checkout -b pat origin/pat 2>/dev/null || git checkout -b pat )

bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
```

Gate after setup:
```bash
bash /home/claude/one4all/scripts/test_smoke_raku.sh           # existing frontend baseline
bash /home/claude/one4all/scripts/test_pat_raku.sh             # NEW — written under PAT-RK-0
```

---

## Architecture reminder

```
scrip --pat-crosscheck pat_raku.sc tiny.raku
```

SCRIP runs `pat_raku.sc` (which `-include`s the shared SC library from
`corpus/programs/snocone/lib/`) against `tiny.raku` — PAT produces IR tree t2
via `Compiland`; the existing frontend produces t1. Both compared in memory
(`tree_equal`), both executed in memory. No subprocesses, no temp files, no
on-disk diffs.

**Shared SC library** (`corpus/programs/snocone/lib/` — tracked under PAT-SN-INFRA-1):
```
tree.sc  stack.sc  counter.sc  ShiftReduce.sc  semantic.sc
```

Compiland spine:
```
Compiland = nPush() ARBNO(*Command) reduce('Parse', 'nTop()') nPop();
```

Raku-specific note: Raku has sigils (`$`, `@`, `%`, `&`) that prefix
identifiers and signal type. Token lexing must distinguish sigil+name
as a single token; the tree carries sigil in the tag (`(ScalarVar a)`,
`(ArrayVar a)`, `(HashVar a)`, `(CodeVar f)`).

---

## Raku language reference (atom slice)

| Construct | Tree shape |
|-----------|------------|
| `$x` | `ScalarVar x` |
| `@a` | `ArrayVar a` |
| `%h` | `HashVar h` |
| `&f` | `CodeVar f` |
| integer `42` | `integer 42` |
| string `'hi'` / `"hi"` | `string 'hi'` |
| `my $x = 5;` | `(Decl (Scope my) ScalarVar(x) Assign integer(5))` |
| `say $x;` | `(Stmt (Call say ScalarVar(x)))` |
| `sub f($a) { ... }` | `(Sub f (Params ScalarVar(a)) Body)` |
| `if $c { ... }` | `(If c Then)` |

(Full feature surface lives in `GOAL-LANG-RAKU.md` and
`GOAL-RAKU-FRONTEND.md`.)

---

## Rung ladder

### PAT-RK-0 — atom — **next**

- [ ] Write `corpus/programs/raku/pat/pat_raku.sc` with `Compiland`
      handling one sigiled identifier (`$x`/`@a`/`%h`/`&f`) or one
      integer or one quoted string.
- [ ] In-process two-frontend crosscheck.
- [ ] Write `scripts/test_pat_raku.sh`.
- [ ] Test corpus (5 NEW programs): `atom_scalar.raku`, `atom_array.raku`,
      `atom_hash.raku`, `atom_int.raku`, `atom_str.raku`. `.ref` empty.
- **Sibling LANG rungs:** RK-1..RK-3 (lexer, sigils).
- **Gate:** PASS=5.

### PAT-RK-1 — declaration + assignment

- [ ] `Command` handles `my $x = expr;` and bare `$x = expr;`.
- [ ] Test corpus: existing thin RK assignment tests + **NEW**.
- **Sibling LANG rungs:** RK-4..RK-6.
- **Gate:** PASS≥10.

### PAT-RK-2 — `say` and arith

- [ ] `Command` handles `say expr;` calls and `+ - * /` operators.
- [ ] Test corpus: existing + **NEW**.
- **Sibling LANG rungs:** RK-7..RK-10.
- **Gate:** PASS≥17.

### PAT-RK-3 — control flow (`if`, `while`, `for`)

- [ ] `Command` handles Raku conditionals and loops with brace bodies.
- [ ] Test corpus: existing + **NEW**.
- **Sibling LANG rungs:** RK-11..RK-18.
- **Gate:** PASS≥25.

### PAT-RK-4 — `sub` definition

- [ ] `Command` handles `sub name(params) { body }`.
- **Sibling LANG rungs:** RK-19..RK-25.
- **Gate:** PASS≥32.

### PAT-RK-5 — regex / grammar primitives

- [ ] `Command` handles a starter slice of Raku regex: literal,
      character class, quantifier, alternation. NOT full grammar/rule
      DSL — that's a later rung tracked when LANG-RAKU gets there.
- **Sibling LANG rungs:** RK-26..RK-34 active.
- **Gate:** PASS≥40.

---

## Invariants

- Raku's LANG ladder is at RK-34 active; PAT-RK does not race ahead.
  If the existing frontend can't yet handle a feature, neither does
  PAT-RK — the rung waits.
- Test programs in `corpus/programs/raku/pat/` are owned by PAT-RK.
- `.ref` files captured at rung-land time.

---

## Watermark

PAT-RK-0 (initial — no .sc parser exists yet).
