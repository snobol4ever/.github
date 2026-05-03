# GOAL-PAT-REBUS.md — PAT-REBUS pattern-based frontend in Snocone

**Repo:** corpus+one4all
**Sibling ladder:** `GOAL-LANG-REBUS.md`. The existing Rebus frontend
(`src/frontend/rebus/`) is the in-process oracle.

**Done when:** A Snocone program `pat_rebus.sc` reads Rebus source,
runs one `Compiland` PATTERN that builds the canonical IR tree, and
for every test program in the rung corpus
`tree_equal(existing_frontend_tree, pat_rebus_tree)` returns true.
Where a `.ref` file exists, executing both trees through the IR
interpreter produces byte-identical output.

---

## Cross-pollination

All six PAT-* parsers share `Compiland`/`Shift`/`Reduce`/`Push`/`Pop`/`Top`/
`tree`/`TDump`/`stack` from `corpus/programs/snocone/demo/beauty/`. Bug
fixes there benefit all six.

Rebus shares lowering with SNOBOL4 (Rebus lowers to LANG_SNO IR per
`GOAL-LANG-REBUS`), so PAT-RB and PAT-SN end up producing trees that
overlap heavily after lowering. PAT-RB's pattern-match (`expr ? pat`)
and alternation generators (`expr | expr`) are direct lifts of PAT-SN's
pattern handling — when PAT-SN-4 lands, PAT-RB-5 gets cheaper.

The existing `GOAL-LANG-REBUS` ladder is younger than SNOBOL4's; expect
the existing frontend to have gaps that PAT-RB will reveal as tree
divergences. Report divergences upstream; do not silently match.

---

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
```

Gate after setup:
```bash
bash /home/claude/one4all/scripts/test_smoke_rebus.sh          # existing frontend baseline
bash /home/claude/one4all/scripts/test_pat_rebus.sh            # NEW — written under PAT-RB-0
```

---

## Architecture reminder

```
source.reb
   │
   ├─→ rebus_compile() → CODE_t* t1   (existing frontend)
   │
   └─→ pat_rebus.sc Compiland → CODE_t* t2

tree_equal(t1, t2) → primary gate
execute(t1) vs execute(t2) → secondary gate (where .ref exists)
```

Compiland spine:
```
Compiland = nPush() ARBNO(*Command) reduce('Parse', 'nTop()') nPop();
```

---

## Rebus language reference (atom slice)

| Construct | Tree shape |
|-----------|------------|
| identifier `x` | `Name x` |
| integer `42` | `integer 42` |
| string `'hi'` | `string 'hi'` |
| `x := expr` | `(Stmt (Assign Name(x) ...))` |
| `function f(a) ... end` | `(Function f (Params a) Body)` |
| `if c then s` | `(If c Then)` |
| `while c do s` | `(While c Body)` |
| `expr ? pat` | `(Match expr pat)` (BB_SCAN — same lowering as SNOBOL4) |
| `expr \| expr` | `(AltGen left right)` (BB_PUMP) |
| `record R(f1,f2)` | `(Record R (Fields f1 f2))` |

(Full feature surface lives in `GOAL-LANG-REBUS.md`.)

---

## Rung ladder

### PAT-RB-0 — atom — **next**

- [ ] Write `corpus/programs/rebus/pat/pat_rebus.sc` with `Compiland`
      handling one identifier or one integer or one quoted string.
- [ ] In-process two-frontend crosscheck.
- [ ] Write `scripts/test_pat_rebus.sh`.
- [ ] Test corpus (3 NEW programs): `atom_id.reb`, `atom_int.reb`,
      `atom_str.reb`. `.ref` empty.
- **Sibling LANG rungs:** RB-1 (basic).
- **Gate:** PASS=3.

### PAT-RB-1 — assignment (`x := expr`)

- [ ] `Command` handles Rebus's `:=` assignment.
- [ ] Test corpus: existing 2 from RB-1 corpus + **3 NEW**.
- **Sibling LANG rungs:** RB-1.
- **Gate:** PASS=8.

### PAT-RB-2 — control flow (`if/then`, `while/do`)

- [ ] `Command` handles `if c then s`, `while c do s`. Note: Rebus does
      NOT use braces around bodies.
- [ ] Test corpus: existing RB-2 corpus + **NEW** edge cases.
- **Sibling LANG rungs:** RB-2 (current active rung).
- **Gate:** PASS≥12.

### PAT-RB-3 — functions (`function f(args) ... end`)

- [ ] `Command` handles function definitions and call sites.
- **Sibling LANG rungs:** RB-3.
- **Gate:** PASS≥18.

### PAT-RB-4 — pattern match (`expr ? pat`)

- [ ] `Command` accepts pattern-match expressions. Pattern body lifts
      directly from PAT-SN-4 pattern handling.
- **Sibling LANG rungs:** RB-4 (when it lands in the LANG ladder).
- **Gate:** PASS≥25.

### PAT-RB-5 — alternation generators (`expr | expr`)

- [ ] `Command` handles `|` between expressions in generator context.
      This is Rebus's signature feature beyond SNOBOL4.
- **Sibling LANG rungs:** RB-5.
- **Gate:** PASS≥32.

### PAT-RB-6 — records

- [ ] `Command` handles `record R(f1,f2)`.
- **Sibling LANG rungs:** RB-6.
- **Gate:** PASS≥38.

---

## Invariants

- Rebus's existing frontend is younger; tree divergences are likely to
  surface bugs in EITHER frontend. PAT-RB does not silently conform.
- Test programs in `corpus/programs/rebus/pat/` are owned by PAT-RB.
- `.ref` files captured at rung-land time.

---

## Watermark

PAT-RB-0 (initial — no .sc parser exists yet).
