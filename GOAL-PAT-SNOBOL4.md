# GOAL-PAT-SNOBOL4.md — PAT-SNOBOL4 pattern-based frontend in Snocone

**Repo:** corpus+one4all
**Sibling ladder:** `GOAL-LANG-SNOBOL4.md` — every PAT-SN-N rung names its
sibling SN-K rung(s). The existing SNOBOL4 frontend (`src/frontend/snobol4/`)
is the oracle; PAT-SN is a second frontend that must agree with it.

**Done when:** A Snocone program `pat_snobol4.sc` reads SNOBOL4 source,
runs one `Compiland` PATTERN that builds the canonical IR tree
(`CODE_t*`-shaped, same shape SM-LOWER consumes today), and for every
test program in the rung corpus `tree_equal(existing_frontend_tree,
pat_snobol4_tree)` returns true. Where a `.ref` file exists, executing
both trees through the IR interpreter produces byte-identical output.

---

## Cross-pollination

All six PAT-* parsers share `Compiland`/`Shift`/`Reduce`/`Push`/`Pop`/`Top`/
`tree`/`TDump`/`stack` from `corpus/programs/snocone/demo/beauty/`. Bug
fixes there benefit all six PAT-* frontends. Token-level token rules and
the `Command` body are language-specific; the spine
`Compiland = nPush() ARBNO(*Command) reduce('Parse', 'nTop()') nPop()`
is identical across all six.

PAT-SN gets two oracles: the existing SNOBOL4 frontend (in-process tree
crosscheck) AND the SPITBOL byte-identical oracle that `GOAL-LANG-SNOBOL4`
already uses. PAT-SN is therefore the safest place to start the family.

---

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
bash /home/claude/one4all/scripts/build_spitbol_oracle.sh
```

Gate after setup:
```bash
bash /home/claude/one4all/scripts/test_smoke_snobol4.sh        # existing frontend baseline
bash /home/claude/one4all/scripts/test_pat_snobol4.sh          # NEW — written under PAT-SN-0
```

---

## Architecture reminder

```
source.sno
   │
   ├─→ snobol4_compile()  → CODE_t* t1   (existing frontend)
   │
   └─→ pat_snobol4.sc Compiland → CODE_t* t2

tree_equal(t1, t2) → primary gate
execute(t1) vs execute(t2) → secondary gate (where .ref exists)
```

The `Compiland` pattern, copied verbatim from `beauty.sc:133`:

```
Compiland = nPush() ARBNO(*Command) reduce('Parse', 'nTop()') nPop();
```

Each rung adds rules to `Command`. `Shift(t,v)` pushes a leaf tree;
`Reduce(t,n)` pops n trees and pushes a parent. The two frontends must
produce the same tree shape — if they diverge, one is wrong.

---

## SNOBOL4 language reference (atom slice)

| Construct | Tree shape |
|-----------|------------|
| identifier `x` | `Name x` |
| integer `42` | `integer 42` |
| string `'hi'` | `string 'hi'` |
| `x = y` | `(Stmt (Assign Name(x) Name(y)))` |
| `OUTPUT = 'hi'` | `(Stmt (Assign BuiltinVar(OUTPUT) string('hi')))` |
| label `loop` | `(Label loop)` inside Stmt |
| `:S(label)` | Goto subtree at end of Stmt |

(Full feature surface lives in `GOAL-LANG-SNOBOL4.md`. PAT-SN climbs
toward parity but does not need to overtake the existing frontend.)

---

## Rung ladder

Each rung's `Test corpus` lists the SNOBOL4 programs that must pass
the gate after the rung lands. New programs (marked **NEW**) get
written under that rung along with their `.ref` files captured from
the existing frontend's `--ir-run` output.

### PAT-SN-0 — atom (literal | identifier) — **next**

- [ ] Write `corpus/programs/snobol4/pat/pat_snobol4.sc` with `Compiland`
      handling exactly: a single line that is one identifier or one
      integer or one string literal, optionally surrounded by whitespace.
- [ ] Wire two-frontend in-process crosscheck inside the .sc driver:
      call existing frontend, call PAT, run `tree_equal`, print PASS/FAIL.
- [ ] Write `scripts/test_pat_snobol4.sh` that walks the rung corpus.
- [ ] Test corpus (3 programs): `atom_id.sno`, `atom_int.sno`, `atom_str.sno`
      — all **NEW** under this rung. Each is one line. `.ref` is empty
      (atoms are no-ops in SNOBOL4).
- **Sibling LANG rungs:** SN-1 (basic lexer), SN-2 (atom recognition).
- **Gate:** `test_pat_snobol4.sh` reports PASS=3.

### PAT-SN-1 — assignment

- [ ] Extend `Command` to handle `name = expr` where `expr` is an atom.
- [ ] Test corpus (5 programs): existing
      `corpus/programs/snobol4/feat/...` 1–2 thin assignment programs +
      **3 NEW** covering `x = 5`, `x = 'hi'`, `x = y`. New `.ref`s captured
      from existing frontend.
- **Sibling LANG rungs:** SN-3, SN-4 (assignment).
- **Gate:** PASS=8 cumulative.

### PAT-SN-2 — concat / arith

- [ ] Extend `Command` for `expr1 expr2` (concat) and `expr1 + expr2`,
      `expr1 - expr2`, `expr1 * expr2`, `expr1 / expr2`.
- [ ] Test corpus: existing concat/arith programs + **5 NEW** covering
      operator precedence corners.
- **Sibling LANG rungs:** SN-5, SN-6.
- **Gate:** PASS≥13.

### PAT-SN-3 — control flow (`:S` / `:F` / labels)

- [ ] `Command` recognizes label-prefixed lines and trailing
      `:S(target)` / `:F(target)` / `:(target)` goto suffixes.
- [ ] Test corpus: existing label/goto programs + **NEW** covering
      simple loops and conditional branches.
- **Sibling LANG rungs:** SN-7, SN-8.
- **Gate:** PASS≥20.

### PAT-SN-4 — patterns (the SNOBOL4 jewel)

- [ ] `Command` accepts pattern-match statements `subject pattern = repl`
      and pattern primitives `LEN(n)`, `BREAK(s)`, `SPAN(s)`,
      `ANY(s)`, `NOTANY(s)`, alternation `|`, concatenation, conditional
      assignment `. var` and `$ var`.
- [ ] Test corpus: existing pattern programs + **NEW** covering each
      primitive.
- **Sibling LANG rungs:** SN-9..SN-15.
- **Gate:** PASS≥35.

### PAT-SN-5 — function definition / call

- [ ] `Command` accepts `DEFINE('f(args)label')` and call sites.
- **Sibling LANG rungs:** SN-16..SN-20.
- **Gate:** PASS≥50.

### PAT-SN-6 — beauty.sno crosscheck

- [ ] PAT-SN parses `beauty.sno` end-to-end. `tree_equal` against the
      existing frontend's tree returns true. Running PAT's tree through
      `--ir-run` produces output byte-identical to the SPITBOL oracle
      (the same gate Milestone 1 uses).
- **Sibling LANG rung:** SN-32 (beauty self-host).
- **Gate:** beauty.sno PASSES under both oracles.

---

## Invariants

- PAT-SN never edits existing-frontend code to make trees match. If
  trees diverge, the divergence is reported; only after Lon decides
  which side is wrong does anyone touch either frontend.
- Test programs in `corpus/programs/snobol4/pat/` are owned by PAT-SN.
  Crosschecks against existing programs in `corpus/programs/snobol4/`
  treat those as read-only fixtures.
- `.ref` files are captured from the existing frontend at the moment
  the rung lands, and are checked in. They do NOT get re-captured on
  later rungs without an explicit decision.

---

## Watermark

PAT-SN-0 (initial — no .sc parser exists yet).
