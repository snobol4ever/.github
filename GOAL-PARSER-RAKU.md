# GOAL-PARSER-RAKU.md — PARSER-RAKU pattern-based frontend in Snocone

**Repo:** corpus+one4all
**Branch:** `parser` (one4all only — `corpus` and `.github` stay on `main`)
**Sibling ladder:** `GOAL-LANG-RAKU.md` and `GOAL-RAKU-FRONTEND.md`. The
existing Raku frontend (`src/frontend/raku/`) is the in-process oracle.

**Done when:** A Snocone program `parser_raku.sc` reads Raku source, runs
one `Compiland` PATTERN that builds the canonical IR tree, and for every
test program in the rung corpus the parser tree matches the existing
frontend's `--dump-ir` output (after whitespace normalization).

Naming, BNF discipline, layout, `White`/`Gray`, `$'name'` tokens,
shift/reduce, n-ary counters, identifier rules — these are the
cross-PARSER style invariants.  Canonical writeup:
`GOAL-PARSER-SNOBOL4.md ## Style Guidelines for parser_*.sc`.
Token classifiers in `parser_raku.sc` mirror `raku.l`
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

### PARSER-RK-3 — control flow (`if`, `while`, `for`) — LANDED session #64, PASS=25.

- [x] `stmt` handles Raku conditionals and loops with brace bodies.
- [x] Test corpus: 8 new RK-3 fixtures (if_basic, if_else, if_cmp_eq, while_basic, while_incr, for_basic, for_named, nested_if_while).
- **Sibling LANG rungs:** RK-11..RK-18.
- **Gate:** PASS=25 (was target ≥25).

### PARSER-RK-4 — `sub` definition — LANDED session #65, PASS=32.

- [x] `stmt` handles `sub name(params) { body }`.
- [x] Function call expressions: `name(args...)` → E_FNC in Expr11.
- [x] `return Expr ;` → E_RETURN. Sub-only programs suppress empty main.
- [x] Test corpus: 7 new RK-4 fixtures (sub_noparams, sub_params, sub_multi_stmt, sub_call, call_expr, sub_multi_params, sub_and_main).
- **Sibling LANG rungs:** RK-19..RK-25.
- **Gate:** PASS=32 (target ≥32). ✓

### PARSER-RK-4.5 — style refactor to beauty.sc shape — required before RK-5

The current `parser_raku.sc` violates several canonical guidelines
documented in `GOAL-PARSER-SNOBOL4.md ## Style Guidelines for parser_*.sc`
(authoritative across all six PARSER-* parsers).  Sharpened in
session 2026-05-04 after re-reading `beauty.sno` /
`corpus/programs/snocone/demo/beauty/beauty.sc` end-to-end.  The
file must be reshaped before any new rungs land on top of it.

Concrete violations to fix (each item maps to a §-numbered guideline):

- [ ] **§7 / §4a — eliminate `_`-prefixed user globals.**  Drop
      `_expr_node`, `_main_node`, `_rk_asgn_target`, `_rk_for_iter`,
      `_rk_block_stk`, `_rk_sub_node`, `_rk_sub_list`, `_rk_call_node`,
      `_rk_arg_stk`, `_rk_vf` / `_rk_vr` / `_rk_strbody` /
      `_rk_itext` / `_rk_atf` / `_rk_atr` / `_rk_ff` / `_rk_fr` /
      `_rk_snf` / `_rk_snr` / `_rk_pf` / `_rk_pr` / `_rk_fnf` /
      `_rk_fnr`, `_e4lhs` / `_e4op` / `_e6lhs` / `_e6op` /
      `_e7lhs` / `_e7op`, `_rk_sub_rev` / `_rk_sl`.
      Underscore prefix is reserved for compiler-generated names.
- [ ] **§4 / §4a — replace function-plumbing with inline shift/reduce.**
      Drop the helper-pattern scaffold (`$'do_assign'`, `$'save_lhs'`,
      `$'op_ADD'`, `$'binop_add'`, `$'do_say'`, `$'do_if2'`,
      `$'do_while'`, `$'start_call'`, `$'add_call_arg'`,
      `$'finish_call'`, ...) and the matching
      `build_*` / `expr_binop` / `stash_*` / `start_*` / `finish_*`
      Snocone functions.  Replace with inline `shift(...)` /
      `reduce(...)` calls in the grammar pattern itself, exactly the
      way `beauty.sc` builds its tree (see §4 example
      `Expr0 = *Expr1 FENCE($'=' *Expr0 reduce('=', 2) | epsilon);`
      for the binary-op shape, and `ExprList` /
      `XList` lines 61–62 of `beauty.sc` for the n-ary shape).
- [ ] **§8 — single-statement bodies, no braces.**  Drop the
      gratuitous `{ ... }` wrappers around one-statement function
      bodies and `if`/`while` heads — write `if (x) statement ;` and
      `while (cond) statement ;` directly.
- [ ] **§8 — section dividers, no blank lines.**  Replace blank-line
      separators with `//===...===` (major) or `//---...---` (minor)
      120-char dividers.  Model: `parser_snobol4.sc`.
- [ ] **§3 — keep `$' '` / `$'  '` whitespace tokens already in place.**
      The three stylistic passes from session #65 (RK-4 handoff
      below) for `$' '` / `$'  '` / classifier-baked whitespace are
      correct and stay.  This rung only removes the `_`-globals and
      the function-plumbing layer.

The refactor preserves PASS=32 (gate must stay green: zero new
features land in this rung).  After the refactor, the file should
be visibly closer in size and shape to `beauty.sc` and
`parser_snobol4.sc` — ideally the binop expression tower
collapses onto roughly the same line count as `beauty.sc` lines
64–88, with no parallel helper-globals block.

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

PARSER-RK-4 LANDED (session #65, 2026-05-03) — PASS=32. Next: PARSER-RK-4.5
(style refactor to beauty.sc shape — see rung detail above), then PARSER-RK-5.

### Style guidelines sharpened (session 2026-05-04, doc-only)

Re-read `beauty.sno` and `corpus/programs/snocone/demo/beauty/beauty.sc`
end-to-end and updated the canonical style guidelines in
`GOAL-PARSER-SNOBOL4.md ## Style Guidelines for parser_*.sc`:

- §4 reframed around "decorate the grammar, do not plumb actions
  through it" — `shift` / `reduce` operate directly inside the
  grammar pattern, not via `epsilon . *fn()` action wrappers
  with parallel `_foo` helper globals.
- §4a added — anti-pattern callout: the function-based action
  plumbing layer (`$'do_X'` patterns, `_xxx` globals,
  `build_X` / `stash_X` / `expr_binop` helpers) is identified
  as a code smell.  beauty.sno does not do this.  Helper
  functions are appropriate only for genuinely non-stack
  semantics (classifier-list match, lower-time name remaps).
- §7 sharpened — `_`-prefix prohibition explicitly flags the
  `_expr_node` / `_rk_*` / `_eN*` globals in current
  `parser_raku.sc` as violations to be cleaned up, not as
  established style worth copying.
- §8 corrected — section divider syntax is `//===...===` /
  `//---...---` (Snocone line-comment, 120 chars), as actually
  used in `parser_snobol4.sc`, not `/*===*/` C-block-comment.
- New rung **PARSER-RK-4.5** inserted before RK-5: refactor
  `parser_raku.sc` to beauty.sc shape (drop `_`-globals, drop
  function-plumbing scaffold, switch to inline shift/reduce,
  preserve PASS=32).  RK-5 work resumes on the cleaned base.

The two beauty files remain the canonical model.  Any tension
between local convenience and the canonical model is resolved
in favour of the model — that is what makes the six
`parser_*.sc` family legible to all six sessions.

### PARSER-RK-4 — handoff (session #65, 2026-05-03)

RK-4 LANDED PASS=32 FAIL=0.  `parser_raku.sc` extended with sub
definition (`SubStmt` / `SubBlock` / `SubBlockStmt`), function call
expressions (`CallName` / `CallArgTail` in `Expr11`), and `return`
statement.  7 new corpus fixtures: `sub_noparams`, `sub_params`,
`sub_multi_stmt`, `sub_call`, `call_expr`, `sub_multi_params`,
`sub_and_main`.

Following RK-4 LANDED, three stylistic refactor passes landed in
`parser_raku.sc` to align with the beauty.sno / parser_icon.sc
cross-PARSER convention:

1. `corpus@f0b3257` — Inline `epsilon . *fn(args)` action sites
   refactored into named `$'name'` pattern definitions.  Convention:
   `$'do_X'` (zero-arg side-effect), `$'save_X'` (stash slot),
   `$'atom_X'` (leaf builder), `$'op_X'` (operator-tag saver),
   `$'binop_X'` (LHS/op/RHS fold).
2. `corpus@c8f3a16` — `$' '` / `$'  '` invisible-whitespace tokens.
   `$' ' = ws_opt`, `$'  ' = ws_run`.  Keyword tokens carry leading
   `$' '`: `$'if' = ($' ' 'if')`.  Operator tokens carry both sides:
   `$'+' = ($' ' '+' $' ')`.  Trailing `$'  '` only at sites needing
   lexical separation (`$'sub' $'  '`, `$'for' $'  '`, etc.).
3. `corpus@b5a8590` — `$' '` baked into atom classifiers themselves
   (`var_scalar`, `int_pat`, `dstr_pat`, `CallName`, `SubName`,
   `ForLoopvar`, `AssignTarget`, `SubParam`).  Grammar reads bare:
   `Expr11 = ( var_scalar $'atom_VAR' | int_pat . _rk_itext $'atom_ILIT' | ... )`.
   `nl_opt = (nl_one | epsilon)` named helper replaces inline
   `(nl_one | epsilon) $' '` in Block / SubBlock / Compiland.
   Zero `ws_opt` references in any grammar pattern definition.

### Cross-PARSER finding (logged for sibling parsers)

`ARBNO(X)` captures `X`'s pattern value at definition time.  When `X`
is rebound after the `ARBNO(X)` site (e.g. `CallArgTail = epsilon` early,
`CallArgTail = (...)` later), the ARBNO sees stale `epsilon` and matches
zero times.  Fix: write `ARBNO(*X)` for deferred lookup.  Discovered
during RK-4 with `ARBNO(*CallArgTail)` for comma-separated function call
args.

### Next session — PARSER-RK-5

Regex / grammar primitives starter slice: literal, character class,
quantifier, alternation.  Not full grammar/rule DSL.  Sibling LANG
rungs RK-26..RK-34 active.  Gate target ≥40.
