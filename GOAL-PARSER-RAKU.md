# GOAL-PARSER-RAKU.md — PARSER-RAKU pattern-based frontend in Snocone

**Repo:** corpus+one4all
**Branch:** `parser` (one4all only — `corpus` and `.github` stay on `main`)
**Sibling ladder:** `GOAL-LANG-RAKU.md` and `GOAL-RAKU-FRONTEND.md`. The
existing Raku frontend (`src/frontend/raku/`) is the in-process oracle.

**Done when:** A Snocone program `parser_raku.sc` reads Raku source, runs
one `Compiland` PATTERN that builds the canonical IR tree, and for every
test program in the rung corpus the parser tree matches the existing
frontend's `--dump-ir` output (after whitespace normalization).

Naming, BNF discipline, and Snocone-style invariants are the
cross-PARSER ones — see `GOAL-PARSER-SNOCONE.md ## Naming & Design
Principles`. Token classifiers in `parser_raku.sc` mirror `raku.l`
(`var_scalar`, `var_array`, `kw_my`, `kw_say`, `op_add`, …); IR tags
mirror `ir.h` (`E_VAR`, `E_ILIT`, `E_QLIT`, `E_FNC`, `E_ASSIGN`,
`E_ADD`/`E_SUB`/`E_MUL`/`E_DIV`).

---

## Session Setup

```bash
( cd /home/claude/one4all && git fetch origin parser 2>/dev/null; git checkout parser 2>/dev/null || git checkout -b parser origin/parser 2>/dev/null || git checkout -b parser )

bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
```

Gate after setup:
```bash
bash /home/claude/one4all/scripts/test_smoke_raku.sh    # existing frontend baseline
bash /home/claude/one4all/scripts/test_parser_raku.sh   # PAT-RK gate
```

---

## Rung ladder

Closed rungs collapsed to one line; the active rung carries the spec.

- **PARSER-RK-0** (atom) — LANDED session #62, PASS=5.
- **PARSER-RK-1** (decl + assign) — LANDED session #62, PASS=10.
- **PARSER-RK-2** (`say` + arith `+ - * /`) — LANDED session #62, PASS=17.

### PARSER-RK-3 — control flow (`if`, `while`, `for`) — **next**

- [ ] `stmt` handles Raku conditionals and loops with brace bodies.
      Probe oracle for the IR shapes first: `if $c { say 1; }`,
      `while $c { ... }`, `for @a -> $x { ... }`.
- [ ] Test corpus: existing + **NEW** (target ≥8 new programs).
- **Sibling LANG rungs:** RK-11..RK-18.
- **Gate:** PASS≥25.

### PARSER-RK-4 — `sub` definition

- [ ] `stmt` handles `sub name(params) { body }`.
- **Sibling LANG rungs:** RK-19..RK-25.
- **Gate:** PASS≥32.

### PARSER-RK-5 — regex / grammar primitives

- [ ] Starter slice: literal, character class, quantifier, alternation.
      NOT full grammar/rule DSL.
- **Sibling LANG rungs:** RK-26..RK-34 active.
- **Gate:** PASS≥40.

---

## Invariants

- Raku's LANG ladder is at RK-34 active; PAT-RK does not race ahead.
  If the existing frontend can't yet handle a feature, neither does
  PAT-RK — the rung waits.
- Test programs in `corpus/programs/raku/parser/` are owned by PAT-RK.
- The implicit-`main`-wrapper insight is permanent: Raku's `program`
  rule synthesizes `(E_FNC main (E_VAR main) stmt…)` around all
  top-level body stmts. `parser_raku.sc` replicates this via
  `body_count` + `build_main_wrapper()`. Same shape applies at every
  rung — control flow / sub-defs nest inside this wrapper.
- For left-associative operator chains, wrap the operator+operand+
  action triple in a NAMED pattern (`mul_tail`, `add_tail`, …).
  Actions placed directly in an `ARBNO(...)` body do not fire on each
  iteration — they evaluate only at construction time. This idiom is
  cross-PARSER (parser_prolog uses it for arg lists; parser_raku uses
  it for arith chains).
- `say` lowers to `(E_FNC write (E_VAR write) <arg>)` in the IR —
  raku.y rewrites the name at lower-time. Future call-style stmts
  may have similar surface→IR name remappings; probe the oracle first.

---

## Watermark

PARSER-RK-2 LANDED (session #62, 2026-05-03) — PASS=17. Next: PARSER-RK-3.

### PARSER-RK-3 — emergency handoff (session #63, 2026-05-03) — WIP, broken

`parser_raku.sc` has been extended with control-flow scaffolding but
**control-flow stmts are not matching**. Gate is **PASS=17 / FAIL=8**:
all RK-2 fixtures still pass, all 8 new RK-3 fixtures fail with the
parser emitting an empty `(STMT :subj (E_FNC main (E_VAR main) ...))`
that omits the if/while/for entirely.

What landed (uncommitted in code, committed in this push):
- 8 new corpus fixtures in `corpus/programs/raku/parser/`:
  `if_basic`, `if_else`, `if_cmp_eq`, `while_basic`, `while_incr`,
  `for_basic`, `for_named`, `nested_if_while` — all oracle-clean,
  byte-checked against `--dump-ir`.
- `parser_raku.sc` extensions:
  - `wsnl_opt = (SPAN(' ' tab nl) | epsilon)` for cross-line whitespace
  - Comparison-operator tokens (`op_eq/ne/le/ge/lt/gt`)
  - Control-flow keyword tokens (`kw_if/else/while/for`, `op_arrow`,
    `raku_lbrace/rbrace/lparen/rparen`)
  - `cmp_expr` level above `add_expr` with E_LT/GT/EQ/NE/LE/GE
    builders via `build_binop`
  - `expr = cmp_expr` (top of expression tower)
  - Six new builder fns: `build_block_enter`, `build_block_exit`
    (using `PushCounter/TopCounter/PopCounter` from counter.sc to
    save/restore outer body_count across nested blocks),
    `build_if_else`, `build_if_no_else`, `build_while`, `build_for`
    (uses `for_iter_name` global to carry loopvar name into E_ITERATE)
  - `block` pattern: `'{' wsnl_opt ARBNO(*stmt) wsnl_opt '}'`
    with deferred `*stmt` to break the `stmt → block → stmt` cycle
  - `if_stmt`/`while_stmt`/`for_stmt` patterns
  - `stmt` reordered: control-flow first, then assign/say, then bare expr
  - `Compiland` final `wsnl_opt` to consume trailing newlines

Things that DEFINITELY work:
- All 17 RK-2 fixtures still pass. Comparison operators in expression
  context work (verified: `my $x = 1 < 2;` → `(E_ASSIGN $x (E_LT 1 2))`).
- The bare-expr `stmt` alternative still matches atoms.

Things that DON'T work — debug starting points for next session:
- Standalone `if ($x) { say($x); }` produces empty body. Same for
  `while`/`for`. The control-flow patterns are constructed but never
  fire on input. Last finding before handoff: even a stripped-down
  test `('if' SPAN(' ') 'hello') ? 'if hello'` returns "no match",
  which is unexpected. Likely root cause is a Snocone PATTERN quirk
  with `'if'` as a literal followed by a SPAN, OR with the `kw_if =
  ('if' ws_one)` named-pattern reference inside an alternation. Worth
  testing: replace `kw_if`/`kw_while`/`kw_for` with inline literals
  in `if_stmt`/`while_stmt`/`for_stmt` to isolate.
- The other suspect is `wsnl_opt` itself — if `nl` isn't a recognized
  Snocone built-in symbol in `SPAN`, the pattern would silently fail.
  Sibling parsers use `ANY(nl)` in `nl_one = ANY(nl)`; `SPAN(' ' tab nl)`
  may need `SPAN(' ' tab Char(10))` or similar.

### Design issue to address — block-body counting via nPush/nInc/nTop/nPop

The current implementation uses `PushCounter`/`TopCounter`/`PopCounter`
from counter.sc to save/restore outer body_count across blocks, plus
the `body_count` global. The sibling cross-PARSER spine
(`parser_prolog.sc`, `parser_icon.sc`) uses `nPush/nInc/nTop/nPop`
for stack-frame child counting — that's the canonical idiom. The
RK-3 builders should be refactored to use `nPush/nInc/nTop/nPop`
for block body counting too, removing the `body_count` global entirely
and aligning with the cross-PARSER convention. This is independent
of the FAIL=8 bug above (the bug is in pattern matching, not in
counting), but the refactor should land before RK-3 is declared LANDED.
