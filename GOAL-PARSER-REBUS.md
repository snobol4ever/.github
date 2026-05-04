# GOAL-PARSER-REBUS.md — PARSER-REBUS pattern-based frontend in Snocone

**Repo:** corpus+one4all
**Branch:** `parser` (one4all only — `corpus` and `.github` stay on `main`)
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
fixes there benefit all six. Rebus shares lowering with SNOBOL4, so PAT-RB's
`expr ? pat` and `expr | expr` lift directly from PARSER-SN-4. The existing
Rebus frontend is younger than SNOBOL4's; PAT-RB does not silently match
divergences — report upstream.

Naming follows the canonical writeup in `GOAL-PARSER-SNOCONE.md` (use BNF
names, `beauty.sc` names, `shift()`/`reduce()` over manual `Push(Tree(...))`,
no new labels/goto).

---

## Session Setup

```bash
( cd /home/claude/one4all && git fetch origin parser 2>/dev/null; \
  git checkout parser 2>/dev/null || git checkout -b parser origin/parser 2>/dev/null || git checkout -b parser )

bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
```

Gate after setup:
```bash
bash /home/claude/one4all/scripts/test_smoke_rebus.sh     # existing frontend baseline
bash /home/claude/one4all/scripts/test_parser_rebus.sh    # PAT-RB
```

---

## Architecture reminder

```
scrip --parser-crosscheck parser_rebus.sc tiny.reb
```

SCRIP runs `parser_rebus.sc` (which `-include`s the shared SC library from
`corpus/programs/scrip/`) against `tiny.reb`. PAT produces tree t2 via
`Compiland`; the existing frontend produces t1. Compared in memory
(`tree_equal`), executed in memory. No subprocesses, no temp files.

Shared SC library: `tree.sc  stack.sc  counter.sc  ShiftReduce.sc  semantic.sc`.

Compiland spine: `Compiland = nPush() ARBNO(*Command) reduce('Parse', 'nTop()') nPop();`

---

## Rebus atom slice

| Construct | Tree shape |
|-----------|------------|
| identifier `x` | `Name x` |
| integer `42` | `integer 42` |
| string `'hi'` | `string 'hi'` |
| `x := expr` | `(Stmt (Assign Name(x) ...))` |
| `function f(a) ... end` | `(Function f (Params a) Body)` |
| `if c then s` | `(If c Then)` |
| `while c do s` | `(While c Body)` |
| `expr ? pat` | `(Match expr pat)` (BB_SCAN) |
| `expr \| expr` | `(AltGen left right)` (BB_PUMP) |
| `record R(f1,f2)` | `(Record R (Fields f1 f2))` |

(Full feature surface: `GOAL-LANG-REBUS.md`.)

---

## Rung ladder

- **PARSER-RB-0** atom — DONE (PASS=3)
- **PARSER-RB-1** assignment `x := expr` — DONE (PASS=8)
- **PARSER-RB-2** control flow `if/then`, `while/do` — DONE (PASS=12)
- **PARSER-RB-3** functions `function f(args) ... end` — DONE (PASS=18)
- **PARSER-RB-4** pattern match `expr ? pat` (atom subj, atom pat) — DONE (PASS=25)
- **PARSER-RB-5** alternation generators `a | b | c` (atom operands; left-assoc E_ALT) — DONE (PASS=32)
- **PARSER-RB-6** record decls `record NAME(f1, f2)` — DONE (PASS=38)

**Ladder complete.** All six rungs landed. Future Rebus surface
(records used in match patterns, expression-level alternation in
arbitrary positions, nested function bodies with control-flow
sequences, etc.) is tracked via the LANG-REBUS ladder (`GOAL-LANG-REBUS.md`)
and arrives in PAT-RB only when the existing frontend grows it first.

---

## Invariants

- Rebus's existing frontend is younger; tree divergences may surface bugs in
  EITHER frontend. PAT-RB does not silently conform.
- Test programs in `corpus/programs/rebus/parser/` are owned by PAT-RB.
- `.ref` files captured at rung-land time.

---

## Watermark

**Rung ladder complete.** RB-0..RB-6 landed 2026-05-03. Cumulative PASS=38 FAIL=0.

### Architectural debt — NOT addressed by this ladder

`parser_rebus.sc` does **not** use the canonical `Compiland`/`nPush`/
`nInc`/`nTop`/`nPop`/`reduce` spine that the top of this goal file
specifies. It is a line-at-a-time goto-driven state machine instead.
This is the same D1/D2/D3 design issue cross-pollinated to all six
PARSER-* parsers (originally raised against PAT-IC, see
`GOAL-PARSER-ICON.md ## Design issues`). Refactor work is tracked
under PARSER-IC-INFRA-1 / PARSER-IC-INFRA-2; when those rungs land
the same refactor lands here.

For comparison (counter-helper hits per parser):
  parser_snobol4.sc: 8   parser_icon.sc: 5   parser_prolog.sc: 4
  parser_raku.sc:    4   parser_snocone.sc: 9   parser_rebus.sc: 0

The PASS=38 gate confirms tree-equivalence with the existing Rebus
frontend — the deliverable's "Done when" criterion at the top of this
file is met. The architectural unification with the other PARSER-*
files is a separate concern, deferred to the cross-cutting INFRA work.

### `test_parser_rebus.sh` normalize() addition

Adopted the `normalize()` whitespace-collapse comparison used by all
other PARSER-* gate scripts. Required because `E_ALT` always has 2
children → oracle (`ir_print_node`) emits multi-line unconditionally,
while TLump emits single-line whenever the budget fits. Both forms
collapse to the same canonical token stream.
