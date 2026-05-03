# GOAL-PAT-ICON.md — PAT-ICON pattern-based frontend in Snocone

**Repo:** corpus+one4all
**Sibling ladder:** `GOAL-LANG-ICON.md`. The existing Icon frontend
(`src/frontend/icon/`) is the in-process oracle.

**Done when:** A Snocone program `pat_icon.sc` reads Icon source, runs
one `Compiland` PATTERN that builds the canonical IR tree, and for every
test program in the rung corpus
`tree_equal(existing_frontend_tree, pat_icon_tree)` returns true. Where
a `.ref` file exists, executing both trees through the IR interpreter
produces byte-identical output.

---

## Cross-pollination

All six PAT-* parsers share `Compiland`/`Shift`/`Reduce`/`Push`/`Pop`/`Top`/
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
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
```

Gate after setup:
```bash
bash /home/claude/one4all/scripts/test_smoke_icon.sh           # existing frontend baseline
bash /home/claude/one4all/scripts/test_pat_icon.sh             # NEW — written under PAT-IC-0
```

---

## Architecture reminder

```
source.icn
   │
   ├─→ icon_compile() → CODE_t* t1   (existing frontend)
   │
   └─→ pat_icon.sc Compiland → CODE_t* t2

tree_equal(t1, t2) → primary gate
execute(t1) vs execute(t2) → secondary gate (where .ref exists)
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

### PAT-IC-0 — atom — **next**

- [ ] Write `corpus/programs/icon/pat/pat_icon.sc` with `Compiland`
      handling one identifier or one integer or one quoted string.
- [ ] In-process two-frontend crosscheck.
- [ ] Write `scripts/test_pat_icon.sh`.
- [ ] Test corpus (3 NEW programs): `atom_id.icn`, `atom_int.icn`,
      `atom_str.icn`. `.ref` empty.
- **Sibling LANG rungs:** IC-1..IC-3 (lexer, atom).
- **Gate:** PASS=3.

### PAT-IC-1 — assignment (`x := expr`)

- [ ] `Command` handles Icon's `:=` assignment.
- [ ] Test corpus: existing 2 + **3 NEW**.
- **Sibling LANG rungs:** IC-4.
- **Gate:** PASS=8.

### PAT-IC-2 — write / arith

- [ ] `Command` handles `write(expr)` calls and `+ - * /` operators.
- [ ] Test corpus: existing + **NEW**.
- **Sibling LANG rungs:** IC-5..IC-6.
- **Gate:** PASS≥14.

### PAT-IC-3 — control flow (`if/then/else`, `while/do`)

- [ ] `Command` handles Icon's conditionals and loops.
- [ ] Test corpus: existing + **NEW**.
- **Sibling LANG rungs:** IC-7..IC-8.
- **Gate:** PASS≥20.

### PAT-IC-4 — procedure definition

- [ ] `Command` handles `procedure f(args) ... end`.
- **Sibling LANG rungs:** IC-9 (current active).
- **Gate:** PASS≥27.

### PAT-IC-5 — alternation generators (`expr1 | expr2`)

- [ ] `Command` handles `|` between expressions in generator context.
      Same lowering shape as Rebus; cross-pollinate.
- **Sibling LANG rungs:** IC-10 (when it lands).
- **Gate:** PASS≥33.

### PAT-IC-6 — `every/do` and `expr ? scan` (string scanning)

- [ ] `Command` handles `every expr do s` (generator-driven loop) and
      `expr ? scan_body` (string scanning context — BB_SCAN).
- **Sibling LANG rungs:** IC-11..IC-13 (when they land).
- **Gate:** PASS≥40.

---

## Invariants

- Icon's LANG ladder is at IC-9 active; PAT-IC does not race ahead.
- Test programs in `corpus/programs/icon/pat/` are owned by PAT-IC.
- `.ref` files captured at rung-land time.

---

## Watermark

PAT-IC-0 (initial — no .sc parser exists yet).
