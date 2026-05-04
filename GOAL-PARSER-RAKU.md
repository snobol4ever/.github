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

### PARSER-RK-4.5 — style refactor to beauty.sc shape — recommended before RK-5

The current `parser_raku.sc` (806 lines, 27 helper functions, 110
`$'name'` action wrappers, 114 blank lines, 10 `_`-prefixed globals)
diverges from several canonical guidelines in
`GOAL-PARSER-SNOBOL4.md ## Style Guidelines for parser_*.sc`.  The
parallel PARSER-PROLOG session opened a comparable PR-7 audit
(`.github@6d31086`) — same shape, different language.

**These are guidelines, not laws.**  The empirical Snocone bug where
`ARBNO(*func())` only fires once on the first iteration is the
documented reason builder layers exist (see PARSER-PR PR-7 caveats).
If a sub-step below hits that bug at a callsite, restore the minimal
helper needed and document the reason inline — don't fight a runtime
bug for the sake of style purity.  The gate (PASS=32 FAIL=0) is the
arbiter.

The sub-steps below are ordered so each lands on a green gate and
each is independently revertable.  A session may do one and stop.

#### 4.5-a — section dividers and blank lines (cosmetic warm-up) — LANDED corpus@4d2a3d0

- [x] Replace blank-line-paragraph-separators with `//===…===` (major)
      or `//---…---` (minor) 120-char comment dividers.  Model:
      `corpus/programs/scrip/parser_snobol4.sc`.  Maps to §8.
- [x] Audit existing comment dividers — any that aren't 120 chars
      get retrimmed or extended.  beauty.sc's 80-char bars are
      grandfathered there but new files standardize on 120.
- **Gate:** PASS=32 FAIL=0 ✓ (52 minor 101-char → 51 major 120-char,
      one back-to-back pair collapsed; blank lines 114 → 64 with the
      remainder all in beauty.sc-canonical positions between `}` and
      next divider).

#### 4.5-b — single-statement bodies, no braces — LANDED corpus@b318fff

- [x] Walk the file's `function … { … }` blocks; any function whose
      body is a single statement followed by `nreturn;` collapses to
      `function name(args) statement ;` (or stays multi-statement
      where it actually has multiple statements).  Maps to §8.
- [x] Same audit on `if (x) { single ; }` / `while (cond) { single ; }`
      heads in the driver.
- **Gate:** PASS=32 FAIL=0 ✓ (zero functions qualified — every helper
      has 3+ statements; 2 if-heads in the driver collapsed).

#### 4.5-c — token-classifier rename to spec-name shape — LANDED corpus@3212b56

- [x] Audit `var_scalar`, `var_array`, `var_hash`, `int_pat`,
      `dstr_pat`, `sstr_pat`, `id_pat` against `raku.l` `TK_*`
      enum names.  Picked UpperCamel (matches `parser_snobol4.sc`'s
      `Integer` / `String` / `Id`).  Maps to §1.
- **Gate:** PASS=32 FAIL=0 ✓ (`VarScalar`, `VarArray`, `VarHash`,
      `LitInt`, `LitStrDQ`, `LitStrSQ`, `Ident` landed; internal
      helpers `ident_first` / `ident_rest` lowered).

#### 4.5-d — runtime helper functions to UpperSnake — LANDED session 2026-05-04

- [x] Rename the 27 helper functions to UpperSnake to match the
      cross-PARSER convention (`Push`, `Pop`, `TDump`, `IncCounter`,
      `nPush`).  e.g. `start_main` → `Start_Main`, `build_assign` →
      `Build_Assign`, `expr_binop` → `Expr_Binop`.  Maps to §7.
- **Note:** the BARE-runtime / pattern-producing distinction in §5
      still applies — `nPush()` / `nInc()` / `nPop()` (pattern-
      producing) are lowercase-`n` UpperSnake, callees `PushCounter`
      / `IncCounter` / `PopCounter` are pure UpperSnake.  Leave
      that asymmetry alone.
- **Gate:** PASS=32 FAIL=0 ✓ (done after 4.5-e on the 9 survivors;
      most of the original 27 were deleted by 4.5-e, so only 9
      renames needed: `Rk_Push_Var`, `Rk_Push_Param`, `Rk_Push_Qlit`,
      `Rk_Say_Done`, `Rk_Stash_For`, `Rk_Finish_For`, `Rk_Finish_Sub`,
      `Rk_Finish_Call`, `Rk_Finish_Main`.  Action-pattern helper
      names (`var_done`, `qlit_done`, `say_done`, etc.) stay
      lower_snake per §5 pattern-producing convention).

#### 4.5-e — eliminate the function-plumbing scaffold (the big one) — LANDED session 2026-05-04

- [x] Drop the helper-pattern scaffold (`$'do_assign'`, `$'save_lhs'`,
      `$'op_ADD'`, `$'binop_add'`, `$'do_say'`, `$'do_if2'`,
      `$'do_while'`, `$'start_call'`, `$'add_call_arg'`,
      `$'finish_call'`, …) and the matching `Build_*` / `Expr_Binop`
      / `Stash_*` / `Start_*` / `Finish_*` Snocone functions.
- [x] Replace with inline `shift(…)` / `reduce(…)` calls in the
      grammar pattern itself, exactly the way `beauty.sc` builds its
      tree.  The binop tower compresses to roughly the shape of
      `beauty.sc` lines 64–88; the n-ary call/sub/block machinery to
      `beauty.sc` lines 61–62 (`ExprList` / `XList`) and 91–100
      (`Expr17`).
- [x] Where a Snocone runtime quirk forces a small helper to remain
      (the `ARBNO(*func())` first-iteration bug noted in PR-7),
      keep the minimal helper and add a one-line `// retained for
      <reason>` comment.  Maps to §4 + §4a + the "guidelines not
      laws" caveat above.
- **Gate:** PASS=32 FAIL=0 ✓ (752 → 555 lines, 27 → 9 functions, 110+
      `$'name'` action wrappers eliminated, all per-tier `_e4lhs` /
      `_e6lhs` / `_e7lhs` / `_e4op` / `_e6op` / `_e7op` and the
      `_expr_node` / `_main_node` / `_rk_asgn_target` /
      `_rk_block_stk` / `_rk_sub_node` / `_rk_call_node` /
      `_rk_arg_stk` globals removed; binop towers `Expr4tail` /
      `Expr6tail` / `Expr7tail` collapsed to inline `(r_OP & 2)`;
      `IfStmt` / `WhileStmt` / `ReturnStmt` / `AssignStmt` use
      inline `reduce(...)` calls; nine helpers retained each with
      `// Retained: <reason>` comment per §4a).

#### 4.5-f — drop `_`-prefixed user globals (conditional on 4.5-e) — LANDED session 2026-05-04

- [x] Once the function-plumbing scaffold is gone, the
      `_`-prefixed user globals it referenced (`_expr_node`,
      `_main_node`, `_rk_asgn_target`, `_rk_for_iter`,
      `_rk_block_stk`, `_rk_sub_node`, `_rk_sub_list`,
      `_rk_call_node`, `_rk_arg_stk`, plus per-construct capture
      vars `_rk_vf` / `_rk_vr` / `_rk_strbody` / `_rk_itext` /
      `_rk_atf` / `_rk_atr` / `_rk_ff` / `_rk_fr` / `_rk_snf` /
      `_rk_snr` / `_rk_pf` / `_rk_pr` / `_rk_fnf` / `_rk_fnr`,
      and per-tier slots `_e4lhs` / `_e4op` / `_e6lhs` / `_e6op` /
      `_e7lhs` / `_e7op`, `_rk_sub_rev` / `_rk_sl`) should be
      removable — the stack and the n-counter cover the same
      ground.  Any survivor renames to lower_snake without the
      prefix.  Maps to §7.
- **Gate:** PASS=32 FAIL=0 ✓ (most globals from the original list
      were deleted by 4.5-e — `_expr_node`, `_main_node`,
      `_rk_asgn_target`, `_rk_block_stk`, `_rk_sub_node`,
      `_rk_call_node`, `_rk_arg_stk`, `_rk_itext`, `_rk_atf`,
      `_rk_atr`, all per-tier slots `_e4lhs`/`_e4op`/`_e6lhs`/
      `_e6op`/`_e7lhs`/`_e7op` are gone.  Survivors renamed to
      drop the underscore: dot-capture targets `rk_capvf`/`rk_capvr`/
      `rk_capstr`/`rk_capff`/`rk_capfr`/`rk_capsnf`/`rk_capsnr`/
      `rk_cappf`/`rk_cappr`/`rk_capfnf`/`rk_capfnr` (renamed to
      `rk_cap*` to make their parsing-state role explicit), plus
      `rk_for_iter` (loopvar stash) and `rk_sub_list` (cons-list
      of completed sub STMTs).  Driver locals `rk_sub_rev`/`rk_sl`/
      `parser_rk_done` also de-underscored.  Zero `_`-prefixed user
      identifiers remain).

#### 4.5-g — preserve the parts already aligned

- [x] `$' '` / `$'  '` / classifier-baked whitespace tokens from
      the three session-#65 stylistic passes (corpus@f0b3257,
      c8f3a16, b5a8590).  These are correct beauty.sno-shape and
      stay.  No work — listed for completeness so they aren't
      accidentally undone.

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

PARSER-RK-4.5-d / 4.5-e / 4.5-f LANDED (session 2026-05-04 cont.) —
PASS=32 FAIL=0.  All seven sub-steps of PARSER-RK-4.5 are now done
(4.5-a/b/c earlier in the session, 4.5-d/e/f later, 4.5-g was a
no-op preservation note).  `parser_raku.sc` is fully aligned with
the beauty.sc / parser_icon.sc cross-PARSER style.

Final state: 752 → 555 lines, 27 → 9 functions (UpperSnake'd),
zero `_`-prefixed user identifiers, function-plumbing scaffold
gone.  Inline `shift()` / `reduce()` decorate the grammar
directly.  Nine helpers retained each with `// Retained: <reason>`
comment per §4a:
  Rk_Push_Var / Rk_Push_Param / Rk_Push_Qlit (sigil/quote strip),
  Rk_Say_Done (say→write remap),
  Rk_Stash_For / Rk_Finish_For (E_ITERATE name + E_EVERY build),
  Rk_Finish_Sub / Rk_Finish_Call / Rk_Finish_Main (E_FNC value-
    field name from captures; reduce() can't supply non-empty value).

Next session: PARSER-RK-5 (regex / grammar primitives starter
slice — literal, character class, quantifier, alternation; sibling
LANG rungs RK-26..RK-34 active; gate target ≥40).

### PARSER-RK-4.5-d / 4.5-e / 4.5-f — handoff (session 2026-05-04 cont.)

The 4.5 ladder landed in three commits, each on a green gate
PASS=32 FAIL=0:

- **4.5-e first** (corpus@c478e13) — function-plumbing scaffold
  eliminated.  752 → 555 lines, 27 → 9 functions.  The big rung.
- **4.5-d on survivors** — the 9 retained helpers renamed to
  UpperSnake with `Rk_` prefix (`Rk_Push_Var`, `Rk_Finish_Main`,
  etc.).  Action-pattern names (`var_done`, `qlit_done`, `say_done`,
  `stash_for`, `for_done`, `sub_done`, `call_done`, `main_done`,
  `param_done`) stay lower_snake per §5 pattern-producing rule.
- **4.5-f after 4.5-d** — leading underscore dropped on all user
  globals.  Most originals were already gone with 4.5-e; survivors
  renamed: dot-capture targets `_rk_vf` → `rk_capvf` etc. (the
  `cap` infix makes their dot-capture role explicit), `_rk_for_iter`
  → `rk_for_iter`, `_rk_sub_list` → `rk_sub_list`, plus driver
  locals.  Zero `_`-prefixed user identifiers remain.

Three commits make 4.5-d and 4.5-f independently revertable from
4.5-e if needed; in practice they are pure renames over a
working gate so revert risk is low.

### PARSER-RK-4.5-e — handoff (session 2026-05-04 cont.)

The teardown landed cleanly with one tricky restructure: the
original Compiland used `_main_node` as a global accumulator
patched by `$'append_stmt'` actions; the new Compiland uses a
nested counter frame (inner frame counts main-body stmts, outer
frame holds the resulting STMT for `reduce('Parse', 1)`).
`SubStmt` does NOT increment the inner main frame because subs
go to `rk_sub_list` and don't leave anything on the stack —
only `Stmt` calls `nInc()` inside the ARBNO body.  Pattern:

    Compiland = nPush() nPush()
                ARBNO( (SubStmt | (Stmt nInc())) nl_opt )
                main_done nPop() nInc()
                (r_Parse & 1) nPop();

Two mistakes worth recording for sibling parsers:

1. `LitInt shift(LitInt, s_ILIT)` matches LitInt TWICE.  `shift(p, t)`
   is itself a complete pattern (`p . thx . *Shift(t, thx)`); writing
   the bare pattern in front duplicates the match.  Correct form:
   just `shift(LitInt, s_ILIT)` alone.
2. For function calls where the IR node carries the callee name as
   value (`(E_FNC double (E_VAR double) ...)`), `reduce(r_FNC, 'nTop()')`
   produces `(E_FNC '' (E_VAR double) ...)` — value field is always
   empty.  A small `Rk_Finish_Call()` helper (read `rk_capfnf`/`rk_capfnr`
   captures, build E_FNC with name in value, append children from
   counter frame) is required.  Same pattern repeats for
   `Rk_Finish_Sub` and `Rk_Finish_Main`.

### PARSER-RK-4.5-a / 4.5-b / 4.5-c — handoff (session 2026-05-04 cont.)

Three sub-steps landed in three commits, each on a green gate:

- **4.5-a** `corpus@4d2a3d0` — 52 minor 101-char `//---` dividers
  promoted to 51 major 120-char `//===` dividers (one back-to-back
  pair collapsed); blank lines reduced 114 → 64.  Remaining blanks
  all sit between `}` and next divider — beauty.sc's lived shape.
- **4.5-b** `corpus@b318fff` — 2 single-statement `if (cond) { stmt; }`
  bodies in the driver collapsed to `if (cond) stmt;`.  Zero helper
  functions qualified (each has 3+ statements: body + `name = .dummy`
  + `nreturn`).
- **4.5-c** `corpus@3212b56` — token classifiers renamed to
  UpperCamel: `var_scalar` → `VarScalar`, `int_pat` → `LitInt`,
  `id_pat` → `Ident`, etc.  Now matches `parser_snobol4.sc`'s
  `Integer` / `String` / `Id` cross-PARSER convention.  The internal
  classifier helpers (`ident_first`, `ident_rest`) stay lower_snake
  since they are not grammar-visible tokens.

### Recommendation for next session — reorder 4.5-d after 4.5-e

The original sub-step order put 4.5-d (rename 27 helpers to
UpperSnake) before 4.5-e (delete the function-plumbing scaffold).
On reflection, that's churn: 4.5-e will delete most of those 27
functions, so renaming first means doing the work twice.  Better
order:

1. **4.5-e first** — delete the action-plumbing layer; identify
   which (if any) helpers genuinely survive (non-stack semantics,
   classifier-list match, lower-time name remap).
2. **4.5-d next, on the survivors only** — rename the small set
   that remain to UpperSnake.
3. **4.5-f** — drop `_`-prefixed user globals (already conditional
   on 4.5-e in the rung text).

The rung order in this goal file is left as 4.5-d → 4.5-e → 4.5-f
for documentation continuity, but the next session is invited to
do them in order 4.5-e → 4.5-d → 4.5-f if it agrees with the
reasoning above.

### Style guidelines sharpened (session 2026-05-04, doc-only)

Re-read `beauty.sno` and `corpus/programs/snocone/demo/beauty/beauty.sc`
end-to-end and updated the canonical style guidelines in
`GOAL-PARSER-SNOBOL4.md ## Style Guidelines for parser_*.sc`:

- §4 reframed around "decorate the grammar, do not plumb actions
  through it" — `shift` / `reduce` operate directly inside the
  grammar pattern, not via `epsilon . *fn()` action wrappers
  with parallel `_foo` helper globals.
- §4a added — function-based action plumbing identified as a
  guideline-level anti-pattern, with explicit "guidelines, not
  laws" caveat: when a Snocone runtime quirk forces a workaround
  (the `ARBNO(*func())`-fires-only-once bug PARSER-PR documented
  in PR-7), keep the minimal helper and document inline.  The
  gate is the arbiter, not style purity.
- §7 softened — `_`-prefix prohibition reframed as "avoid", with
  explicit guidance to refactor opportunistically rather than open
  dedicated rungs just for renames.
- §8 corrected — section divider syntax is `//===...===` /
  `//---...---` (Snocone line-comment, 120 chars), as actually
  used in `parser_snobol4.sc`, not `/*===*/` C-block-comment.
- New rung **PARSER-RK-4.5** inserted before RK-5: refactor
  `parser_raku.sc` to beauty.sc shape — broken into seven ordered
  sub-steps (4.5-a..4.5-g) so each lands on a green gate and is
  independently revertable.  Recommended, not gating: a session
  may do one sub-step and stop, or skip 4.5 entirely if regex is
  the priority.

The two beauty files remain the canonical model.  Tension between
local convenience and the canonical model resolves in favour of
the model — but the gate (PASS=32 FAIL=0) is the arbiter, and
runtime quirks override style.

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
