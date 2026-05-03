# GOAL-PAT-SNOCONE.md — PAT-SNOCONE pattern-based frontend in Snocone

**Repo:** corpus+one4all
**Sibling ladder:** `GOAL-LANG-SNOCONE.md` (and the closely related
`GOAL-SNOCONE-IN-SNOCONE.md`). The existing Snocone frontend
(`src/frontend/snocone/`) is the in-process oracle.

**Done when:** A Snocone program `pat_snocone.sc` reads Snocone source,
runs one `Compiland` PATTERN that builds the canonical IR tree (same
shape SM-LOWER consumes), and for every test program in the rung corpus
`tree_equal(existing_frontend_tree, pat_snocone_tree)` returns true.
Where a `.ref` file exists, executing both trees through the IR
interpreter produces byte-identical output.

---

## Cross-pollination

All six PAT-* parsers share `Compiland`/`Shift`/`Reduce`/`Push`/`Pop`/`Top`/
`tree`/`TDump`/`stack` from `corpus/programs/snocone/demo/beauty/`. Bug
fixes there benefit all six. PAT-SNOCONE is the most reflexively
satisfying of the six: a Snocone program parsing Snocone using the same
pattern primitives Snocone provides. Coupled to `GOAL-SNOCONE-IN-SNOCONE`
on the long-horizon: when both rungs near completion, the bootstrap
cycle closes.

---

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
```

Gate after setup:
```bash
bash /home/claude/one4all/scripts/test_smoke_snocone.sh        # existing frontend baseline
bash /home/claude/one4all/scripts/test_pat_snocone.sh          # NEW — written under PAT-SC-0
```

---

## Architecture reminder

```
source.sc
   │
   ├─→ snocone_compile() → CODE_t* t1   (existing frontend)
   │
   └─→ pat_snocone.sc Compiland → CODE_t* t2

tree_equal(t1, t2) → primary gate
execute(t1) vs execute(t2) → secondary gate (where .ref exists)
```

Compiland spine (identical across all six):
```
Compiland = nPush() ARBNO(*Command) reduce('Parse', 'nTop()') nPop();
```

Snocone-specific note: the existing Snocone frontend already lowers
to LANG_SNO IR via `snocone_lower.c`. PAT-SC must produce the same
post-lowering shape, OR produce a pre-lowering Snocone-flavored tree
that the existing lowering pipeline can consume — Lon decides per rung
which is in scope.

---

## Snocone language reference (atom slice)

| Construct | Tree shape |
|-----------|------------|
| identifier `x` | `Name x` |
| integer `42` | `integer 42` |
| string `"hi"` | `string 'hi'` |
| `x = expr;` | `(Stmt (Assign Name(x) ...))` |
| `function f(a,b) { ... }` | `(Function f (Params a b) Body)` |
| `if (c) { ... } else { ... }` | `(If c Then Else)` |
| `while (c) { ... }` | `(While c Body)` |
| `expr ? pat` | `(Match expr pat)` |

(Full feature surface lives in `GOAL-LANG-SNOCONE.md`.)

---

## Rung ladder

### PAT-SC-0 — atom — **next**

- [ ] Write `corpus/programs/snocone/pat/pat_snocone.sc` with `Compiland`
      handling: a single line that is one identifier, one integer, or
      one quoted string. Optional trailing `;`.
- [ ] In-process two-frontend crosscheck inside the .sc driver.
- [ ] Write `scripts/test_pat_snocone.sh`.
- [ ] Test corpus (3 NEW programs): `atom_id.sc`, `atom_int.sc`, `atom_str.sc`.
      `.ref` is empty.
- **Sibling LANG rungs:** SC-0 (lexer), SC-1 (atom).
- **Gate:** PASS=3.

### PAT-SC-1 — assignment

- [ ] `Command` handles `name = expr;` for atom expr.
- [ ] Test corpus: 5 (existing 2 + **3 NEW**).
- **Sibling LANG rungs:** SC-2.
- **Gate:** PASS=8 cumulative.

### PAT-SC-2 — arith / concat

- [ ] `Command` handles `+ - * /` and Snocone's concat operator.
- [ ] Test corpus: 5 NEW.
- **Sibling LANG rungs:** SC-3.
- **Gate:** PASS≥13.

### PAT-SC-3 — control flow

- [ ] `Command` handles `if (c) { ... }`, `if/else`, `while (c) { ... }`.
- [ ] Test corpus: existing snocone control programs + **NEW** edge cases.
- **Sibling LANG rungs:** SC-3, SC-4.
- **Gate:** PASS≥20.

### PAT-SC-4 — function def + call

- [ ] `Command` handles `function name(params) { body }` and call sites.
- **Sibling LANG rungs:** SC-5..SC-7.
- **Gate:** PASS≥30.

### PAT-SC-5 — pattern match `expr ? pat`

- [ ] `Command` accepts SNOBOL4-style pattern subexpressions on the
      right of `?`. This is where Snocone borrows SNOBOL4's pattern
      syntax. PAT-SN-4's pattern handling can be lifted; the embedding
      is what's new.
- **Sibling LANG rungs:** SC-8, SC-9 (pattern match).
- **Gate:** PASS≥40.

### PAT-SC-6 — full beauty.sc crosscheck

- [ ] PAT-SC parses `beauty.sc` end-to-end. `tree_equal` against the
      existing frontend's tree returns true. Both trees run identically
      under `--ir-run`.
- **Sibling LANG rung:** SC-final / `GOAL-SNOCONE-IN-SNOCONE` SS-N.
- **Gate:** beauty.sc round-trips.

---

## Invariants

- PAT-SC never edits the existing Snocone frontend to make trees match.
- Test programs in `corpus/programs/snocone/pat/` are owned by PAT-SC.
- `.ref` files captured at rung-land time, checked in, not silently
  re-captured later.
- The existing Snocone lowering (`snocone_lower.c`) is treated as
  load-bearing for OTHER goals and must not be perturbed by PAT-SC
  edits without explicit Lon approval.

---

## Watermark

PAT-SC-0 (initial — no .sc parser exists yet).
