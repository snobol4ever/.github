# GOAL-PARSER-REBUS.md — PARSER-REBUS pattern-based frontend in Snocone

**Repo:** corpus+one4all
**Branch:** `pat` (one4all only — `corpus` and `.github` stay on `main`)
**Sibling ladder:** `GOAL-LANG-REBUS.md`. The existing Rebus frontend
(`src/frontend/rebus/`) is the in-process oracle.

**Done when:** A Snocone program `parser_rebus.sc` reads Rebus source,
runs one `Compiland` PATTERN that builds the canonical IR tree, and
for every test program in the rung corpus
`tree_equal(existing_frontend_tree, parser_rebus_tree)` returns true.
Where a `.ref` file exists, executing both trees through the IR
interpreter produces byte-identical output.

---

## Cross-pollination

All six PARSER-* parsers share `Compiland`/`Shift`/`Reduce`/`Push`/`Pop`/`Top`/
`tree`/`TDump`/`stack` from `corpus/programs/snocone/demo/beauty/`. Bug
fixes there benefit all six.

Rebus shares lowering with SNOBOL4 (Rebus lowers to LANG_SNO IR per
`GOAL-LANG-REBUS`), so PAT-RB and PARSER-SN end up producing trees that
overlap heavily after lowering. PAT-RB's pattern-match (`expr ? pat`)
and alternation generators (`expr | expr`) are direct lifts of PARSER-SN's
pattern handling — when PARSER-SN-4 lands, PARSER-RB-5 gets cheaper.

The existing `GOAL-LANG-REBUS` ladder is younger than SNOBOL4's; expect
the existing frontend to have gaps that PAT-RB will reveal as tree
divergences. Report divergences upstream; do not silently match.

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
bash /home/claude/one4all/scripts/test_smoke_rebus.sh          # existing frontend baseline
bash /home/claude/one4all/scripts/test_parser_rebus.sh            # NEW — written under PARSER-RB-0
```

---

## Architecture reminder

```
scrip --parser-crosscheck parser_rebus.sc tiny.reb
```

SCRIP runs `parser_rebus.sc` (which `-include`s the shared SC library from
`corpus/programs/scrip/`) against `tiny.reb` — PAT produces IR tree t2
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

### PARSER-RB-0 — atom — **next**

- [ ] Write `corpus/programs/scrip/parser_rebus.sc` with `Compiland`
      handling one identifier or one integer or one quoted string.
- [ ] In-process two-frontend crosscheck.
- [ ] Write `scripts/test_parser_rebus.sh`.
- [ ] Test corpus (3 NEW programs): `atom_id.reb`, `atom_int.reb`,
      `atom_str.reb`. `.ref` empty.
- **Sibling LANG rungs:** RB-1 (basic).
- **Gate:** PASS=3.

### PARSER-RB-1 — assignment (`x := expr`)

- [ ] `Command` handles Rebus's `:=` assignment.
- [ ] Test corpus: existing 2 from RB-1 corpus + **3 NEW**.
- **Sibling LANG rungs:** RB-1.
- **Gate:** PASS=8.

### PARSER-RB-2 — control flow (`if/then`, `while/do`)

- [ ] `Command` handles `if c then s`, `while c do s`. Note: Rebus does
      NOT use braces around bodies.
- [ ] Test corpus: existing RB-2 corpus + **NEW** edge cases.
- **Sibling LANG rungs:** RB-2 (current active rung).
- **Gate:** PASS≥12.

### PARSER-RB-3 — functions (`function f(args) ... end`)

- [ ] `Command` handles function definitions and call sites.
- **Sibling LANG rungs:** RB-3.
- **Gate:** PASS≥18.

### PARSER-RB-4 — pattern match (`expr ? pat`)

- [ ] `Command` accepts pattern-match expressions. Pattern body lifts
      directly from PARSER-SN-4 pattern handling.
- **Sibling LANG rungs:** RB-4 (when it lands in the LANG ladder).
- **Gate:** PASS≥25.

### PARSER-RB-5 — alternation generators (`expr | expr`)

- [ ] `Command` handles `|` between expressions in generator context.
      This is Rebus's signature feature beyond SNOBOL4.
- **Sibling LANG rungs:** RB-5.
- **Gate:** PASS≥32.

### PARSER-RB-6 — records

- [ ] `Command` handles `record R(f1,f2)`.
- **Sibling LANG rungs:** RB-6.
- **Gate:** PASS≥38.

---

## Invariants

- Rebus's existing frontend is younger; tree divergences are likely to
  surface bugs in EITHER frontend. PAT-RB does not silently conform.
- Test programs in `corpus/programs/rebus/parser/` are owned by PAT-RB.
- `.ref` files captured at rung-land time.

---

## Watermark

PARSER-RB-0 (initial — no .sc parser exists yet).
