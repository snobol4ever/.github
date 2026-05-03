# GOAL-PAT-SNOBOL4.md — PAT-SNOBOL4 pattern-based frontend in Snocone

**Repo:** corpus+one4all
**Branch:** `pat` (one4all only — `corpus` and `.github` stay on `main`)
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
# Switch one4all to the shared PAT branch. corpus and .github stay on main.
( cd /home/claude/one4all && git fetch origin pat 2>/dev/null; git checkout pat 2>/dev/null || git checkout -b pat origin/pat 2>/dev/null || git checkout -b pat )

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
scrip --pat-snobol4 tiny.sno
         │
         ├─→ existing SNOBOL4 frontend  → CODE_t* t1   (in-process)
         │
         └─→ pat_snobol4.sc Compiland  → CODE_t* t2   (in-process, Snocone)

tree_equal(t1, t2) → primary gate          (in memory, no files, no diff)
execute(t1) vs execute(t2) → secondary gate (in memory, where .ref exists)
```

**Invocation:** `scrip` gets a new mode `--pat-crosscheck`. When invoked:

```
scrip --pat-crosscheck pat_snobol4.sc tiny.sno
```

1. SCRIP runs the Snocone PAT driver `pat_snobol4.sc` (which `-include`s
   the shared SC library from `corpus/programs/snocone/lib/`) against
   `tiny.sno` as its input — producing IR tree t2 via the `Compiland` PATTERN.
2. SCRIP simultaneously runs the existing SNOBOL4 frontend on `tiny.sno`
   producing IR tree t1.
3. Both trees are compared in memory (`tree_equal`). Both are executed
   in memory and outputs compared. All sync is live, in-process — no
   subprocess, no temp files, no on-disk diffs.

**Shared SC library** (all six PAT sessions use these — separate files on the command line, no `-include`):
```
corpus/programs/snocone/lib/tree.sc
corpus/programs/snocone/lib/stack.sc
corpus/programs/snocone/lib/counter.sc
corpus/programs/snocone/lib/ShiftReduce.sc
corpus/programs/snocone/lib/semantic.sc
```

Each session invokes scrip with the full blob:
```
scrip --pat-crosscheck \
  corpus/programs/snocone/lib/tree.sc \
  corpus/programs/snocone/lib/stack.sc \
  corpus/programs/snocone/lib/counter.sc \
  corpus/programs/snocone/lib/ShiftReduce.sc \
  corpus/programs/snocone/lib/semantic.sc \
  corpus/programs/snocone/pat/pat_snobol4.sc \
  tiny.sno
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

### PAT-SN-INFRA-0 — Snocone conditional-assignment capture bug — ✅ DONE

Discovered during PAT-SN-0 setup. In the Snocone `--ir-run` and `--sm-run`
interpreter, `. var` (conditional assignment) inside a pattern returned the
**value** of the variable instead of its **lvalue** (NAME descriptor), so
captures silently wrote to an anonymous slot and the variable stayed empty.
Same bug in `$ var` (immediate assignment).

- [x] Reproduce: `s = 'hello'; s ? (LEN(3) . cap); OUTPUT = cap;` → printed empty.
- [x] Root cause: `eval_code.c` `E_CAPT_COND_ASGN` / `E_CAPT_IMMED_ASGN` — plain
      `E_VAR` target fell into `eval_node(tgt)` → `NV_GET_fn()` (value) instead
      of `NAME_fn()` (lvalue). `E_INDIRECT` branch was already correct.
- [x] Fix: added `else if (tgt->kind == E_VAR)` branch returning `NAME_fn(tgt->sval)`
      in both handlers in `eval_code.c`.
- [x] `test_smoke_snobol4.sh` PASS=7. `test_smoke_snocone.sh` PASS=5. No regressions.
- [x] Gate: `scrip --ir-run` on reproduce case prints `hel`. ✅

### PAT-SN-INFRA-1 — Shared SC library for all six PAT sessions — **next**

All six PAT parsers share the same Snocone runtime library. Extract and
clean the relevant files from `corpus/programs/snocone/demo/beauty/` into
`corpus/programs/snocone/lib/`. No `-include` inside Snocone — all files
are passed as a blob on the command line by the test script.

- [ ] Create `corpus/programs/snocone/lib/` directory.
- [ ] Copy and clean `tree.sc` → `lib/tree.sc` (no `xTrace` deps, self-contained).
- [ ] Copy and clean `stack.sc` → `lib/stack.sc`.
- [ ] Copy and clean `counter.sc` → `lib/counter.sc`.
- [ ] Copy and clean `ShiftReduce.sc` → `lib/ShiftReduce.sc`.
- [ ] Copy and clean `semantic.sc` → `lib/semantic.sc`.
- [ ] Write `lib/README.md` naming purpose and each file.
- [ ] Smoke-test: `scrip --ir-run lib/tree.sc lib/stack.sc lib/counter.sc lib/ShiftReduce.sc lib/semantic.sc smoke_lib.sc`
      where `smoke_lib.sc` calls `Shift('foo','bar')` then `Pop()` → prints `bar`.
- **Gate:** smoke test prints `bar`. No xTrace output.

### PAT-SN-0 — atom (literal | identifier) — blocked on INFRA-0 + INFRA-1

- [ ] Write `corpus/programs/snocone/pat/pat_snobol4.sc` with `Compiland`
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

PAT-SN-INFRA-1 (INFRA-0 capture bug fixed; next: create corpus/programs/snocone/lib/).
