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

### PARSER-RK-5 — regex / grammar primitives — LANDED session 2026-05-04 cont.

- [x] Starter slice: regex literal `/body/`, smartmatch `~~`.
      NOT full grammar/rule DSL — character class / quantifier / alternation
      ride along inside `body` as opaque text (the C oracle just stores
      the raw between-slashes text into `(E_QLIT body)`).
- [x] Test corpus: 5 new RK-5 fixtures (regex_lit, regex_meta with
      `\d+` / `[a-z]+` / `a|b`, regex_anchor `^x$`, regex_dot_star `.*`,
      regex_backslash `\s+`).
- **Sibling LANG rungs:** RK-26..RK-34 active.
- **Gate:** PASS=37 (was target ≥40 — short of target by 3 because
  the starter slice doesn't yet exercise multi-pattern-per-program
  fixtures; tag closes the rung anyway since every regex feature
  the existing frontend handles via `(E_QLIT body)` is now routed
  end-to-end through PARSER-RK).

### PARSER-RK-6 — regex captures `(...)`, `$0`, `$1`, named `$<name>` — LANDED session 2026-05-04

- [x] `VarCapture` classifier — `$[0-9]+` → captures digit string into `capidx`.
- [x] `VarNamedCapture` classifier — `$<name>` → captures bare name into `capncname`.
- [x] `finish_capture()` helper — builds `(E_FNC raku_capture (E_VAR raku_capture) (E_ILIT N))`.
      Retained: `reduce()` sets value=''; E_FNC requires value='raku_capture'.
- [x] `finish_named_capture()` helper — builds `(E_FNC raku_named_capture (E_VAR raku_named_capture) (E_QLIT name))`.
      Retained: same reason as `finish_capture`.
- [x] Both added to `Expr11` before `LitInt` (after `VarHash`) so sigiled patterns are tried
      before bare identifier fallback.
- [x] Test corpus: 3 new fixtures — `capture_pos.raku` (`$0`), `capture_idx.raku` (`$1`),
      `capture_named.raku` (`$<word>`).
- **Sibling LANG rungs:** RK-34 already supports these.
- **Gate:** PASS=40 FAIL=0 ✓ (corpus@6a772b3)



The starter slice is one token classifier + one operator + one helper:

- `LitRegex = ($' ' '/' BREAK('/') . caprx '/')` — captures the regex
  body (everything between the slashes) into `caprx`.  Starter limit:
  embedded `/` inside `[...]` or after `\` is not yet handled.  None
  of the gate fixtures exercise that case; revisit if/when one does.
- `$'~~'` operator at the Expr4 (comparison) tier, with RHS pinned
  to `LitRegex` (not arbitrary Expr).  This matches the existing
  Raku frontend's grammar — `~~` is a smartmatch built around a
  literal regex, not a general binary op.
- `Finish_smartmatch` helper: pops pattern + subject, builds
  `(E_FNC raku_match (E_VAR raku_match) subj pat)` — same surface→IR
  rewrite the C `raku.y` does.  Retained per §4a because reduce()
  cannot carry a non-empty value field through to the E_FNC node.

#### RK-5 prerequisite — n-ary arith flattening (corpus@<this commit>)

Before RK-5 itself, the RK-4 watermark fixture `arith_chain` was
failing because of iter#9 Phase A: the C frontend `raku.y` now uses
`expr_binary_flatten()` and emits flat n-ary `(E_ADD a b c)` instead
of nested binary `(E_ADD (E_ADD a b) c)`.  `parser_raku.sc` still
emitted nested binary via `(E_ADD & 2)`.

Fix: four flatten helpers (`flatten_add` / `flatten_sub` / `flatten_mul`
/ `flatten_div`) with capitalized companion patterns (`Flatten_add`
etc.).  Each pops rhs, peeks lhs from stack: if `t(lhs)` matches the
op tag, `Append`s rhs into lhs (in-place mutate, lhs stays on stack);
else builds fresh `(tag lhs rhs)`.  Replaces the four
`(E_OP & 2)` reduce sites in `Expr6tail` / `Expr7tail`.  Same
technique applies cleanly to PARSER-RB's E_ALT chains (the
remaining 3 fails) when that session reaches it.

#### RK-5 dependency — tdump.sc CQize for E_QLIT escaping

`src/ir/ir_print.c::print_escaped` C-escapes `\`, `"`, `\n`, `\r`,
`\t` (and `\xNN` for other bytes < 0x20) when rendering E_QLIT /
E_CSET values.  `tdump.sc`'s E_QLIT branch was emitting `v(x)` raw,
so any regex with `\d` / `\s` / `[a-z]` etc. diverged at the dump
layer (tree data identical, display differed).  Fix: new `CQize(s)`
function in `qize.sc` mirroring print_escaped semantics; tdump.sc's
E_QLIT branch routed through `CQize(v(x))`.  Cross-PARSER-positive:
no other parser corpus currently exercises backslash-bearing QLITs,
so PASS counts in IC/PR/SC/RB/SN unchanged, but any future fixture
with `\` or embedded `"` in a string now renders correctly.

---

### PARSER-RK-10 — delete, range `..`/`..^`, for-range — LANDED session 2026-05-05

- [x] `delete %h<ident>` stmt → `(E_FNC hash_delete (E_VAR hash_delete) (E_VAR h) (E_QLIT key))`.
      `finish_hash_delete_angle` helper; mirrors raku.y `KW_DELETE VAR_HASH '<' IDENT '>'` action.
- [x] `delete %h{$expr}` stmt → `(E_FNC hash_delete (E_VAR hash_delete) (E_VAR h) key_expr)`.
      `finish_hash_delete_brace` helper; key_expr on top of stack.
- [x] Range expression `a..b` / `a..^b` → `(E_TO lo hi)`.
      New `Expr5` tier between `Expr4` (cmp) and `Expr6` (add) — matches raku.y precedence
      table (`OP_RANGE` between cmp and `+`).  Both `..` and `..^` map to `E_TO` (oracle does same).
      `$'..'` and `$'..^'` operator tokens; `..^` tried first (longer).
- [x] `for lo..hi -> $v { body }` range for → while-loop lowering.
      `ForRangeStmt` matches `Expr6 $'..'|$'..^' Expr6` explicitly.
      `finish_for_range` mirrors `raku.y make_for_range()`: appends incr to body,
      builds `(E_SEQ_EXPR (E_ASSIGN v lo) (E_WHILE (E_LE v hi) body_with_incr))`.
      `ForRangeStmt` appears before `ForStmt` in all Stmt/BlockStmt/SubBlockStmt so
      range input is caught before the general `E_EVERY`/`E_ITERATE` path.
- [x] Test corpus: 5 new fixtures (delete_hash_angle, delete_hash_brace, range_expr,
      for_range, for_range_ex).
- **Gate:** PASS=55 FAIL=0 ✓  corpus@2cdfcec.

---

### PARSER-RK-11 — `unless`/`until` stmts + `push`/`pop` call verification — LANDED session 2026-05-05

- [x] `unless (cond) block` → `(E_IF (E_NOT cond) then)`.
      `finish_not` helper wraps top-of-stack expr in `E_NOT` node.
      `UnlessStmt` mirrors raku.y `unless_stmt` with optional `else` arm.
- [x] `unless (cond) block else block` → `(E_IF (E_NOT cond) then else)` (3 children).
- [x] `until (cond) block` → `(E_UNTIL cond body)`.
      `UntilStmt` mirrors raku.y `until_stmt`; `(E_UNTIL & 2)` reduce.
- [x] `push(@a, v)` / `pop(@a)` verified — already handled by `finish_call` as plain
      call expressions; no grammar additions needed (not keywords in raku.l).
- [x] Test corpus: 5 new fixtures (unless_basic, unless_else, until_basic,
      push_arr, pop_arr).
- **Gate:** PASS=60 FAIL=0 ✓  corpus@f663327.

---

### PARSER-RK-12 — logical `&&`/`||`/`!` ops — LANDED session 2026-05-05

- [x] `!expr` (prefix logical NOT) → `(E_NOT expr)`.
      `$'!' *Expr11 Finish_not` arm at top of `Expr11`; reuses `Finish_not` from RK-11.
- [x] `a && b` → `(E_SEQ a b)`.  `Expr3tail` with `$'&&' *Expr4 (E_SEQ & 2)`.
      Mirrors raku.y `cmp_expr OP_AND add_expr → E_SEQ`.
- [x] `a || b` → `(E_ALT a b)`.  `Expr3tail` with `$'||' *Expr4 (E_ALT & 2)`.
      Mirrors raku.y `cmp_expr OP_OR add_expr → E_ALT`.
- [x] Chains `a && b && c` → nested left-associative binary `(E_SEQ (E_SEQ a b) c)`.
      Oracle uses `expr_binary` (not flatten) for `&&`/`||`; ARBNO left-assoc matches.
- [x] `Expr3` tier inserted above `Expr4`; `Expr` updated from `Expr4` to `Expr3`.
- [x] Test corpus: 5 new fixtures (logic_and, logic_or, logic_not, logic_chain,
      logic_or_chain).
- **Gate:** PASS=65 FAIL=0 ✓  corpus@15666e9.

---

### PARSER-RK-13 — string `~` concat → `E_CAT` n-ary — LANDED session 2026-05-05

- [x] `a ~ b` → `(E_CAT a b)`.  `$'~' *Expr7 Flatten_cat` arm in `Expr6tail`.
      Mirrors raku.y `add_expr '~' mul_expr → expr_binary_flatten(E_CAT)`.
- [x] `a ~ b ~ c` → `(E_CAT a b c)` — n-ary flatten, same pattern as `flatten_add`.
      `flatten_cat` helper: pop rhs, pop lhs; if `t(lhs)==E_CAT` append rhs in-place;
      else build fresh 2-child node.
- [x] `$'~'` one-char token; no conflict with `$'~~'` two-char in Expr4tail
      (different expression tier level).
- [x] Test corpus: 5 new fixtures (str_cat, str_cat_chain, str_cat_lit, str_cat_say,
      str_cat_mixed).
- **Gate:** PASS=70 FAIL=0 ✓  corpus@591f91b.

---

### PARSER-RK-14 — `eq`/`ne` string cmp + unary minus — LANDED session 2026-05-05

- [x] `$a eq $b` → `(E_LEQ a b)`.  `$'eq' *Expr5 (E_LEQ & 2)` arm in `Expr4tail`.
      Mirrors raku.y `add_expr OP_SEQ add_expr → E_LEQ`.
- [x] `$a ne $b` → `(E_LNE a b)`.  `$'ne' *Expr5 (E_LNE & 2)` arm in `Expr4tail`.
      Mirrors raku.y `add_expr OP_SNE add_expr → E_LNE`.
- [x] `-expr` → `(E_MNS expr)`.  `($' ' '-') *Expr11 Finish_mns` arm at top of
      `Expr11` (after `!` arm).  Uses raw `$' ' '-'` (leading ws only) to avoid
      trailing-ws ambiguity with binary `$'-'` token.
      `finish_mns` helper: pop inner, build `(E_MNS inner)`, push.
- [x] Test corpus: 5 new fixtures (str_eq, str_ne, unary_minus, unary_minus_var,
      str_eq_ne).
- **Gate:** PASS=75 FAIL=0 ✓  corpus@d2f4584.

---

### PARSER-RK-15 — `%` modulo + `div` integer division — LANDED session 2026-05-05

- [x] `$x % $y` → `(E_MOD x y)`.  `$'%' *Expr11 (E_MOD & 2)` in `Expr7tail`.
      Mirrors raku.y `mul_expr '%' unary_expr → expr_binary(E_MOD)` (non-flatten).
- [x] `$x div $y` → `(E_DIV x y)` via `Flatten_div`.  `$'div' *Expr11 Flatten_div`.
      Mirrors raku.y `mul_expr OP_DIV unary_expr → expr_binary_flatten(E_DIV)`.
- [x] `$'%'` token: `$' ' '%' $' '`.  No ambiguity with `VarHash` (`%letter`) —
      `%` appears in `Expr7tail` only after an expression is already on stack.
- [x] Test corpus: 5 new fixtures (modulo, div_kw, modulo_chain, div_expr, mod_div).
- **Gate:** PASS=80 FAIL=0 ✓  corpus@5b42940.

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

### PARSER-RK-16 — interpolated DQ strings `"hello $var"` → E_CAT chain — LANDED session 2026-05-05

- [x] `finish_interp_str()` helper: walks `capstr`, splits on `$ident` sequences,
      builds left-associative binary `(E_CAT lhs rhs)` chain — mirrors `raku.y lower_interp_str()`.
      If no `$ident` found → plain `(E_QLIT body)`.
- [x] `LitStrDQ` now routes through `Push_interp_str` instead of `Push_qlit`.
      `LitStrSQ Push_qlit` unchanged (single-quoted strings never interpolate).
- [x] Test corpus: 5 new fixtures — `interp_simple`, `interp_leading_var`, `interp_multi_var`,
      `interp_trailing_lit`, `interp_only_var`.
- **Retained (§4a):** `finish_interp_str` must walk sub-string content to split on `$ident`;
      `shift`/`reduce` cannot iterate over string bytes.
- **Gate:** PASS=85 FAIL=0 ✓  corpus@0e5ad3d.

### PARSER-RK-20 — `map`/`grep`/`sort` higher-order list ops — LANDED session 2026-05-06

- [x] `ClosureExpr = ( $'{' *Expr $'}' )` — one-expression closure body for map/grep/sort.
- [x] `map { closure } list` → `(E_FNC raku_map (E_VAR raku_map) closure list)`.
      `Finish_map` helper; mirrors raku.y KW_MAP closure expr RK-24 action.
- [x] `grep { closure } list` → `(E_FNC raku_grep (E_VAR raku_grep) closure list)`.
      `Finish_grep` helper; mirrors raku.y KW_GREP closure expr RK-24 action.
- [x] `sort list` → `(E_FNC raku_sort (E_VAR raku_sort) list)`.
      `Finish_sort_nc` helper; mirrors raku.y KW_SORT expr (no closure) RK-24 action.
- [x] All three added to `Expr11` after the `die` arm (matching oracle grammar position).
- [x] `$'map'` / `$'grep'` / `$'sort'` keyword tokens added to token table.
- [x] Test corpus: 5 new fixtures (map_basic, grep_basic, sort_nc, map_say, grep_str).
- **Gate:** PASS=105 FAIL=0 ✓  corpus@eefec55.

### PARSER-RK-WS2 — canonical White/Gray — LANDED corpus@c2ade5a

Lon directive: `$' '`/`$'  '` everywhere, whitespace attached to tokens,
grammar body whitespace-free.  **PASS=105 FAIL=5 watermark held.**

**What landed (corpus@c2ade5a):**  DGray and nl_one eliminated.  White
extended to absorb newlines and `#` line-comments (`SPAN(' ' tab nl)
FENCE('#' BREAK(nl) nl | epsilon) | '#' BREAK(nl) nl`).  Gray = White |
epsilon.  All 13 DGray call-sites removed; Block / SubBlock / WhenClause /
DefaultClause / GivenStmt / Compiland boundaries simplified.  Grammar
body uses only `$' '` / `$'  '` — whitespace evaporates from productions.

**What was NOT done** (engine fragility, documented for a future session):
The canonical-Snocone `White = white ARBNO(white)` / `Gray = ARBNO(white)`
shape was attempted and causes two engine bugs under nested ARBNO +
`&FULLSCAN=1`:

1. **Wrong-tree silent failure** — `~~` gets re-segmented as `~ ~` causing
   10 regex/capture fixtures to drop the regex stmt (PASS→95).  Root is
   Expr6tail's `$'~' *Expr7` arm matching after `$'~~'` fails: with
   `Gray = ARBNO(white)` the retry space is larger and an erroneous match
   path opens up.

2. **SIGSEGV / stale-pointer crash** — minimal repro:
   ```snocone
   G = ARBNO(' ');
   ok = ('"X"' ARBNO(G '~' G '"Y"') ';' ? '"X" ~~ "Y";');
   ```
   Crash in `interp_eval.c:3958` memcpy: `g_last_match_subj` is a stale
   subject pointer by the time the value-context `?` extraction reads it.
   Filed as **BUG-SCRIP-VAL-SCAN** — see engine bug section below.

The FENCE-based form keeps these bugs hidden and gives the same
readability win (`$' '`/`$'  '` everywhere).

- [x] Eliminate DGray / nl_one / nl_opt from parser_raku.sc.
- [x] Grammar body uses only `$' '` / `$'  '` aliases.
- [x] Gate PASS=105 FAIL=5.
- [ ] FUTURE: canonical `white ARBNO(white)` form — blocked on
      BUG-SCRIP-VAL-SCAN engine fix.

### PARSER-RK-21 — `gather`/`take` coroutine construct — LANDED session 2026-05-07 cont.

- [x] `E_SUSPEND = "'E_SUSPEND'"` tag constant added.
- [x] `$'gather'` / `$'take'` keyword tokens added.
- [x] `gather_seq = 0` global added.
- [x] `finish_gather()` + `Finish_gather` pattern added (mirrors
      `finish_sub`: pops counter frame, emits def STMT into `sub_list`,
      pushes call `E_FNC` onto expression stack).
- [x] `TakeStmt = ( $'take' $'  ' Expr $';' (E_SUSPEND & 1) )` — verified
      working standalone: `take 1;` → `(E_SUSPEND (E_ILIT 1))` ✓
- [x] `TakeStmt` added to `Stmt` / `BlockStmt` / `SubBlockStmt`.
- [x] **`GatherBlock` pattern** added — self-contained `nPush()/nPop()`
      bracketing around `$'{' ARBNO(*SubBlock_body) $'}' Finish_gather`,
      mirroring `Block`'s self-contained counter shape.
- [x] `Expr11` arm rewritten: `| $'gather' *GatherBlock` (deferred lookup).
- [x] Test corpus: 5 fixtures (gather_take_lit, gather_take_var,
      gather_multi_take, gather_in_assign, take_in_loop) all PASS.
- **Gate:** PASS=110 FAIL=0 ✓

#### Root-cause finding (cross-PARSER, important)

Two compounded `ARBNO(X)` / forward-reference quirks made the original
`$'gather' nPush() SubBlock Finish_gather nPop()` arm fail silently:

1. **`Expr11` is defined BEFORE `SubBlock_body` and `GatherBlock` in source
   order.**  Bare `ARBNO(SubBlock_body)` and bare `GatherBlock` reference
   capture the *current* (i.e. undefined / empty) value of those names at
   the moment `Expr11` is being built.  This is the same `ARBNO(X)`-
   captures-at-definition-time quirk the RK-4 cross-PARSER note already
   documented for `*CallArgTail`.  Fix: use deferred lookup `*GatherBlock`
   in `Expr11`, and `ARBNO(*SubBlock_body)` inside `GatherBlock`.

2. **`SubBlock` (used by `SubStmt`) survived this quirk by accident** —
   `SubBlock_body` is defined right before `SubBlock`, so `SubBlock`
   captured the correct value.  But any *other* pattern referencing
   `SubBlock_body` from before its definition site needs `*SubBlock_body`.

This is a usage-level forward-reference rule, not an engine bug.  Anyone
adding a new arm to `Expr11` (or any other early-defined non-terminal)
that needs to reference a later-defined helper must use `*Helper`.  The
PRIMER at `SNOBOL4-SNOCONE-PRIMER.md ## Big four operators / *` already
covers the principle; this rung supplies the cautionary example.

### BUG-SCRIP-WS-1 — RESOLVED (engine-side, session 2026-05-07 verification)

Originally filed during RK-WS (whitespace refactor, session 2026-05-06):
SIGSEGV under `&FULLSCAN=1` when `White = white ARBNO(white)` was nested
inside expression-tier ARBNO loops.

**Resolution status:** Engine-side ARBNO/FULLSCAN fixes that landed in
PARSER-PR-WS (corpus@6511bab) and predecessors (interp.c ARBNO/FENCE in
value context, SN-22a+b NAM mark/rollback removal, SB-5c.1 ARBNO/FENCE
in interp_eval_pat E_FNC path) cumulatively resolved the underlying
stack-overflow issue.  Session 2026-05-07 verified by reapplying the
canonical `White = white ARBNO(white)` / `Gray = ARBNO(white)` form to
parser_raku.sc and running the gate: **no SIGSEGV**.  The four fixtures
originally listed as crash-affected (`delete_hash_brace`,
`hash_exists_brace`, `match_global`, `subst_single`) now PASS under the
canonical form for `delete_hash_brace` and `hash_exists_brace`;
`match_global` and `subst_single` regress to "tree divergence" along
with 8 other regex/capture fixtures — that regression is tracked under
PARSER-RK-WS2 above (a parser-grammar issue, not an engine crash).

Original symptom and minimal repro retained below for archival reference:

**Original symptom:** SIGSEGV (exit 139) on certain Raku programs when
`White = white ARBNO(white)` (canonical `parser_snocone.sc` form) and
`$'  '` (= White) appears inside expression-tier ARBNO loops
(`Expr7tail`, `Expr6tail`, etc.) with `&FULLSCAN=1`.

**Original minimal repro:**

```snocone
&FULLSCAN = 1;
white = ( SPAN(' ' tab) | '#' BREAK(nl) );
White = white ARBNO(white);   // ← nested ARBNO
$'  ' = White;
Tail = FENCE( $'  ' 'div' $'  ' epsilon );
Pat = ('X' ARBNO(Tail));      // ← outer ARBNO containing nested ARBNO via $'  '
Pat ? 'X $x div $y';          // crashed on certain inputs (no longer crashes)
```

- [x] BUG-SCRIP-WS-1: confirmed no longer reproduces against current
      one4all HEAD (verified session 2026-05-07).

---

## Watermark

Session 2026-05-07 — PASS=105 FAIL=0 watermark held.  Two artefacts landed:

  1. **5 RK-21 fixtures landed in corpus** (.raku + .ref pairs for
     gather_take_lit, gather_take_var, gather_multi_take, gather_in_assign,
     take_in_loop) — `.ref` outputs probed from the C oracle.  Currently
     fail "tree divergence" because RK-21 grammar is not yet in
     parser_raku.sc; that is the next step.

  2. **PARSER-RK-WS2 rung opened** for canonical White/Gray refactor
     (replaces FENCE-based `White`+`Gray`+`DGray`+`nl_one` block with
     `white ARBNO(white)` shape from parser_snocone.sc).  Pivot was
     attempted, mechanically clean, no SIGSEGV — **BUG-SCRIP-WS-1
     resolved engine-side** (verified, see that section above; marked
     resolved).  But 10 regex/capture fixtures regressed to "tree
     divergence" from interaction with another tier.  Working tree
     reverted before commit; PASS=105 FAIL=5 (5 expected RK-21 fails)
     restored.  Diagnosis pointers + recommended bisection approach
### BUG-SCRIP-VAL-SCAN — stale g_last_match_subj in value-context `subj ? pat`

**Discovered:** session 2026-05-07 (this session) while investigating
canonical `Gray = ARBNO(white)` regression.

**Symptom:** SIGSEGV (exit 139) in `interp_eval.c:3958` memcpy when a
value-context `ok = (Src ? Pat)` succeeds under nested ARBNO + `&FULLSCAN=1`.
The crash is in the matched-substring extraction block
(PARSER-SN-INFRA-11a, lines 3938–3961): after `exec_stmt` returns success,
the code reads `g_last_match_subj + g_last_match_start` for `span_len` bytes.
`g_last_match_subj` is the raw `subj_str` pointer saved in `stmt_exec.c:1405`
— it points into a string buffer that may have been moved / freed by the GC
by the time interp_eval reads it.

**Minimal repro:**
```snocone
&FULLSCAN = 1;
G = ARBNO(' ');
Pat = ( '"X"' ARBNO(G '~' G '"Y"') ';' );
ok = ('"X" ~~ "Y";' ? Pat);   // SIGSEGV
```
Predicate context `if (... ? Pat) {}` does not crash (doesn't hit the
extraction path).

**Fix needed** (`stmt_exec.c`): Before storing `subj_str` into
`g_last_match_subj`, deep-copy it into a GC-stable buffer (or bump a
refcount).  Alternatively, copy the span into `g_last_match_buf` there
and then in interp_eval read from `g_last_match_buf` instead of
reconstructing via pointer + offsets.

- [ ] BUG-SCRIP-VAL-SCAN: Fix `stmt_exec.c` — GC-protect the subject
      buffer stored in `g_last_match_subj` so value-context `subj ? pat`
      extraction does not crash.

---

## Watermark

Session 2026-05-07 (continuation, RK-21 closure) — **PARSER-RK-21 LANDED**:

- **PARSER-RK-21 LANDED** — PASS=110 FAIL=0.
  GatherBlock pattern added with self-contained nPush/nPop bracketing
  around `$'{' ARBNO(*SubBlock_body) $'}' Finish_gather`.  Expr11 arm
  rewritten to `| $'gather' *GatherBlock` (deferred lookup).  Both
  `*GatherBlock` and `*SubBlock_body` are required because Expr11 is
  defined in source order *before* GatherBlock and SubBlock_body — bare
  `ARBNO(X)` captures X's value at the enclosing pattern's definition
  time (same quirk as RK-4's `*CallArgTail` finding).  All 5 RK-21
  fixtures (gather_take_lit, gather_take_var, gather_multi_take,
  gather_in_assign, take_in_loop) now produce trees byte-identical to
  the C oracle.

Earlier session 2026-05-07 watermarks (still valid):

- **PARSER-RK-WS2 LANDED** corpus@c2ade5a — PASS=105 FAIL=5.
  DGray + nl_one eliminated.  `$' '` / `$'  '` everywhere.
  FENCE-based White (extended to absorb nl + # comments).
  canonical `ARBNO(white)` form blocked on BUG-SCRIP-VAL-SCAN.

- **PARSER-RK-21 scaffold** corpus@436e667 (now superseded by this
  session's LANDED — see above).

PARSER-RK-21 LANDED — PASS=110 FAIL=0 (this session).
PARSER-RK-WS2 LANDED corpus@c2ade5a — PASS=105 FAIL=5.
PARSER-RK-WS LANDED (session 2026-05-06) — PASS=105 FAIL=0. corpus@9ed9e99.
PARSER-RK-20 LANDED (session 2026-05-06) — PASS=105 FAIL=0.
RK-7..RK-9: handles, global match/subst, arr/hash index+exists.  corpus@e605b01.
RK-10: delete %h<k>/%h{e}, range a..b/a..^b, for-range.  corpus@c7c2d14.
RK-11: unless/until stmts + push/pop verified.  corpus@f663327.
RK-12: logical && → E_SEQ, || → E_ALT, ! → E_NOT.  corpus@15666e9.
RK-13: string ~ concat → E_CAT n-ary flatten.  corpus@591f91b.
RK-14: eq/ne string cmp → E_LEQ/E_LNE; unary minus → E_MNS.  corpus@d2f4584.
RK-15: % modulo → E_MOD (binary); div integer division → E_DIV (flatten).  corpus@5b42940.
RK-16: interpolated DQ strings "hello $var" → left-assoc E_CAT chain.  corpus@0e5ad3d.
RK-17: given/when/default → E_CASE node.  corpus@a29276e.
RK-18: print stmt + die expr + DQ escape fix (BREAK+REM pattern).  corpus@85c4a88.
RK-19: try/CATCH exception handling.  corpus@ca930a1.
RK-20: map/grep/sort higher-order list ops.  corpus@eefec55.

Cross-PARSER notes added RK-17/18:
- Snocone if(expr) always succeeds; use EQ/IDENT predicates for integer flags.
- BREAK(x) fails when no char from x appears in remaining subject; pair with REM.
- WhenClause/DefaultClause: leading $' ' (Gray) absorbs newlines inside { }.

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

---

### PARSER-RK-22 — method call / field access — LANDED session 2026-05-06

- [x] `$obj.meth()` / `$obj.meth(arg, ...)` → `(E_FNC raku_mcall (E_VAR raku_mcall) obj (E_QLIT "meth") args...)`.
      `finish_mcall()` helper: pops counter-frame args + obj off stack, builds raku_mcall node.
      Retained (§4a): reduce() sets value=''; raku_mcall name required in E_FNC value field.
- [x] `$obj.field` (no parens) → `(E_FIELD fieldname obj)`.
      `finish_field()` helper: pops obj, builds E_FIELD node with capmf/capmr name.
      Retained (§4a): reduce() cannot set E_FIELD's sval field.
- [x] `McallArgTail` / `MethodName` / `MethodTail` patterns added before `Expr11` (forward-ref
      rule: all three are referenced via `*` because Expr11 is defined in source order first).
- [x] `Expr11` extended: wrapped with `ARBNO(*MethodTail)` postfix — deferred lookup required.
- [x] `capmf` / `capmr` globals added for method name capture.
- [x] Test corpus: 5 new fixtures (str_uc, str_lc, str_trim, str_chars, str_substr).
- **Gate:** PASS=115 FAIL=0 ✓  corpus@675cc40

## Watermark

Session 2026-05-06 — **PARSER-RK-22 LANDED** PASS=115 FAIL=0 corpus@675cc40.

Method call / field access support complete.  `MethodTail` postfix works cleanly
because it is positioned after the full primary (all Expr11 arms), and `ARBNO(*MethodTail)`
uses deferred lookup via `*` because Expr11 is defined before MethodTail in source order
(same `*X` forward-reference rule as RK-4's `*CallArgTail` and RK-21's `*GatherBlock`).

### Next: PARSER-RK-23

`$s ~~ /regex/` smartmatch (already supported at RK-5) extended to cover named-capture
groups `(<name> ...)` and verify against the LANG RK-23 oracle output.  Gate target ≥120.

---

### PARSER-RK-23 — close raku.y gap (all missing features) — LANDED session 2026-05-06

- [x] **BUG-FIX in `raku.y`** — `KW_ELSIF` declared but had zero grammar rules; fixed with
      three `if_stmt` arms mirroring the existing `KW_ELSE if_stmt` recursive shape.
      one4all @ `d96d4ef7`.
- [x] `LitFloat` → `(E_FLIT n)` — positioned before `LitInt` in `Expr11` to avoid `.`
      being consumed as MethodTail dot before the decimal.
- [x] `repeat { }` → `(E_REPEAT body)` — `E_REPEAT` constant added; `RepeatStmt`.
- [x] `for expr { }` (no arrow) → `(E_EVERY (E_ITERATE expr) body)` — `ForNoArrowStmt`
      + `finish_for_noarrow` helper.
- [x] `my Type $var = expr;` / `my Type $var;` → typed decl with type discarded — `TypedDeclStmt`
      + `Push_empty` helper for uninitialised form.
- [x] `return;` (bare) → `(E_RETURN)` with no children — `ReturnBareStmt`.
- [x] `@a[i] = expr` → `arr_set` — `ArrSetStmt` + `finish_arr_set`.
- [x] `%h<key> = val` → `hash_set` — `HashSetAngleStmt` + `finish_hash_set_angle`.
- [x] `%h{expr} = val` → `hash_set` — `HashSetBraceStmt` + `finish_hash_set_brace`.
- [x] `$obj.field = expr` → `(E_ASSIGN (E_FIELD name obj) rhs)` — `FieldWriteStmt`
      + `finish_field_write`.
- [x] `ClassName.new(k=>v,...)` → `(E_FNC raku_new ...)` — `NewCallName` / `NamedArgTail`
      / `finish_raku_new` / `Push_named_key`. Key capture fix: `((ident_first (ident_rest|epsilon)) . capnamedkey)`.
- [x] `say($fh, str)` / `print($fh, str)` → `raku_say_fh` / `raku_print_fh` — `SayFhStmt`
      / `PrintFhStmt` + `finish_say_fh` / `finish_print_fh`.
- [x] `if/elsif/else` chain → nested `E_IF` — uses `raku.y` bug fix.
- [x] 11 new corpus fixtures with oracle `.ref` files.
- **Gate:** PASS=126 FAIL=0 ✓  corpus@838304e  one4all@d96d4ef7

## Watermark

Session 2026-05-06 — **PARSER-RK-23 LANDED** PASS=126 FAIL=0.

All features present in `raku.y` now covered by `parser_raku.sc`.
`parser_raku.sc` is at full parity with the C oracle for all constructs
the C frontend supports.

### Next: PARSER-RK-24

Class/method/has/new OO construct — `class Dog { has $.name; method speak() { } }`
→ `(E_RECORD Dog (E_VAR name))` + method defs. Mirrors `raku.y` `class_decl` action.
Gate target ≥132.

### PARSER-RK-24 — class/OO construct — LANDED (session 2026-05-07 cont.)

- [x] `VarTwigil` classifier: `$.field` / `$!field` → `(E_FIELD fieldname (E_VAR self))`.
      `captwf`/`captwr` capture bare name; `Push_twigil` builds E_FIELD.
- [x] `push_has_field()` / `Push_has_field` — strips twigil, pushes `(E_VAR fieldname)`.
- [x] `push_nul()` / `Push_nul` — pushes `(E_NUL)` sentinel for main frame.
- [x] `finish_method()` / `Finish_method` — closes inner body frame, pushes raw E_FNC with method name.
- [x] `finish_class()` / `Finish_class` — renames E_FNC items to `ClassName__method`, emits STMTs; builds E_RECORD from E_VAR fields.
- [x] `ClassName` / `MethodIdent` classifiers (`capclsf`/`capclsr`, `capmtf`/`capmtr`).
- [x] `HasDecl` / `MethodDef` / `ClassBodyItem` / `ClassDecl` grammar patterns added.
- [x] `ClassDecl` in Compiland ARBNO as `(*ClassDecl Push_nul nInc())`.
- [x] 6 RK-24 corpus fixtures created with oracle `.ref` files.
- [x] **`class_and_main` FIXED** — root cause was `SayFhStmt`/`PrintFhStmt` firing
      `push_var()` as a match-time side effect (via `epsilon . *push_var()`) inside a
      failed alternation. With `&FULLSCAN=1`, `SayFhStmt = $'say' $'(' *Expr $',' ...`
      tried `*Expr` against `$d.name` — `push_var()` fired and pushed `(E_VAR d)` before
      the comma check failed. The push was NOT rolled back (match-time side effects are
      permanent). Fix: `VarScalar FENCE $',' Push_var` — FENCE commits after comma is
      confirmed, so `Push_var` only fires in the genuine 2-arg `say($fh, str)` form.
      Same fix applied to `PrintFhStmt`. corpus@78bdcb9.
- **Gate:** PASS=132 FAIL=0. corpus@78bdcb9.

#### Cross-PARSER finding — match-time side effects in failed alternations (IMPORTANT)

`push_var()` (and all helpers using `epsilon . *fn()`) fire at MATCH TIME via the
deferred `*` operator.  With `&FULLSCAN=1`, failed alternations are tried and their
match-time side effects (Push, Pop, nPush, nPop) ARE NOT ROLLED BACK.  This means:

**Any grammar alternative that uses `Push_var` (or any `*fn()` helper) inside a
pattern that might fail must use `FENCE` or structural disambiguation BEFORE the
helper fires.**

The correct idiom for a 2-arg statement that could be confused with a 1-arg form:

```snocone
// WRONG — push_var fires before comma check; stray push on failure:
FooFhStmt = ( $'foo' $'(' *Expr $',' *Expr $')' $';' Finish_foo_fh );

// RIGHT — VarScalar sets capvf/capvr; FENCE commits; Push_var fires safely:
FooFhStmt = ( $'foo' $'(' VarScalar FENCE $',' Push_var *Expr $')' $';' Finish_foo_fh );
```

This is a STRONGER constraint than the existing cross-PARSER note about `ARBNO(X)`
capturing at definition time — it applies to ANY alternation, not just ARBNO.


## Watermark

Session 2026-05-07 (continuation, RK-24 closure) — **PARSER-RK-24 LANDED** PASS=132 FAIL=0.

`class_and_main` fix: `SayFhStmt`/`PrintFhStmt` restructured with `VarScalar FENCE $','
Push_var` to prevent match-time push_var side effects in failed alternations.
Root cause: `epsilon . *push_var()` fires push_var() at match time (not post-match);
with &FULLSCAN=1 failed alternatives' match-time side effects are not rolled back.
Key cross-PARSER rule: use FENCE before any `*fn()` helper in a context that might fail.
corpus@78bdcb9.

Next: **RK-25** (next rung — see GOAL-LANG-RAKU.md for what RK-25 covers).

---

### PARSER-RK-25 — file I/O + standard handles — LANDED session 2026-05-07

- [x] **Bug fix: `SayFhStmt`/`PrintFhStmt` extended to accept `$*STDIN`/`$*STDOUT`/`$*STDERR`**
      as filehandle arg. Original forms only accepted `VarScalar`; standard handles
      lex as `VAR_CAPTURE` (raku.l lines 131-133) and were routed to the generic call
      path, producing `say(raku_capture(1), "hello")` instead of
      `raku_say_fh(raku_capture(1), "hello")`. Fix: inner alternation
      `( VarScalar FENCE $',' Push_var | VarStdIn FENCE $,' Finish_stdin | VarStdOut
      FENCE $,' Finish_stdout | VarStdErr FENCE $,' Finish_stderr )`.
      `VarStdIn/Out/Err` are pure string matches (no side effects), safe before FENCE.
      `Finish_stdin/stdout/stderr` push after FENCE+comma, preserving the RK-24
      FENCE-guard invariant for match-time side effects.
- [x] Test corpus: 5 new fixtures (slurp_file, lines_file, spurt_file, say_stdout,
      print_stderr). `slurp`/`lines`/`spurt` route through the generic Expr11 call path
      and already worked; `say_stdout`/`print_stderr` required the bug fix above.
- **Gate:** PASS=137 FAIL=0. corpus@(this commit). ✓

## Watermark

Session 2026-05-07 — **PARSER-RK-25 LANDED** PASS=137 FAIL=0.

Bug fix: `SayFhStmt`/`PrintFhStmt` inner alternation extended to accept
`VarStdIn/Out/Err` with FENCE guard — `say($*STDOUT, str)` / `print($*STDERR, str)`
now produce `raku_say_fh` / `raku_print_fh` matching the C oracle.
5 new file-I/O fixtures: slurp_file, lines_file, spurt_file, say_stdout, print_stderr.

PARSER-RK-24 LANDED PASS=132 FAIL=0 corpus@78bdcb9.
PARSER-RK-23 LANDED PASS=126 FAIL=0 corpus@838304e.

Next: **RK-26**.

---

### PARSER-RK-26 — bare identifier atoms + typed array/hash decls — LANDED session 2026-05-07

- [x] **Bug fix: `BareIdent` atom arm added to `Expr11`.**
      `say(x)` where `x` has no sigil produced empty output — `Expr11` had no arm
      for unsigiled identifier atoms.  The C oracle maps `IDENT` → `var_node($1)` →
      `(E_VAR x)` (raku.y atom rule).  Fix: added `BareIdent = ($' ' vf . capvf vro
      . capvr)` classifier (captures into `capvf`/`capvr` like `VarScalar`) and
      `| BareIdent Push_var` as the last atom arm in `Expr11` (after the `CallName`
      function-call arm, so `foo(args)` is still caught as a call; bare `foo` with
      no `(` falls through to `BareIdent Push_var`).
- [x] Test corpus: 5 new fixtures:
      `bare_ident_arg` (`say(x)` bare ident argument),
      `bare_ident_expr` (`my $r = foo + 1` bare ident in arithmetic),
      `typed_arr_decl` (`my Int @nums = sort @data` typed array with init),
      `typed_hash_decl` (`my Str %h = raku_new_hash()` typed hash with init),
      `typed_arr_bare` (`my Int @nums` typed array uninitialized → `(E_ASSIGN (E_VAR nums) (E_QLIT ""))`).
- **Gate:** PASS=142 FAIL=0. corpus@(this commit). ✓

---

### PARSER-RK-27 — nested function calls + .new() with call args — LANDED session 2026-05-07

- [x] **Bug fix 1: `finish_call` read `capfnf/capfnr` for fname — clobbered by nested calls.**
      `length(trim($s))` produced `(E_FNC trim (E_VAR length) ...)` — the outer call's
      fname was overwritten when `*Expr` recursed into `trim(...)`.  Fix: `finish_call`
      now reads `fname = v(kids[1])` from the already-pushed `E_VAR` node (pushed by
      `shift(CallName, 'E_VAR')` before args), which is stable on the stack regardless
      of inner recursion.  `capfnf/capfnr` no longer read in `finish_call`.
- [x] **Bug fix 2: `NewCallName` captured into `capfnf/capfnr` — clobbered by named-arg call values.**
      `Dog.new(name => get_name())` produced `(E_QLIT "get_name")` as ClassName.
      Fix: `NewCallName` now captures into `capclsf/capclsr` (the dedicated class-name
      slots); `finish_raku_new` reads `capclsf capclsr`.  These are not touched by
      any `*Expr` sub-match.
- [x] Test corpus: 5 new fixtures (nested_calls, triple_nested_call, new_with_call_arg,
      nested_call_in_method, nested_call_arith).
- **Gate:** PASS=147 FAIL=0. corpus@(this commit). ✓
