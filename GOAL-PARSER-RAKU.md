# GOAL-PARSER-RAKU.md — PARSER-RAKU pattern-based frontend in Snocone

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ ABSOLUTE RULE — ZERO C BYRD BOX FUNCTIONS — NO EXCEPTIONS — READ THIS BEFORE WRITING CODE  ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                  ║
║  A C Byrd box (C BB) is ANY C function with this signature:                                     ║
║                                                                                                  ║
║      DESCR_t foo(void *zeta, int entry)                                                         ║
║                                                                                                  ║
║  implementing four-port logic (α / β / γ / ω).                                                  ║
║                                                                                                  ║
║  THERE MUST BE ZERO OF THESE IN THE CODEBASE. NOT ONE. NONE. EVER.                              ║
║                                                                                                  ║
║  ALL Byrd boxes are x86 ASSEMBLY emitted at runtime by the emitter.                             ║
║  If you want a BB, you EMIT it. You do not write a C function for it.                           ║
║                                                                                                  ║
║  The only permitted C functions with (void *zeta, int entry) signature are:                     ║
║    • icn_lazy_box  — infrastructure shim, not a generator                                       ║
║    • icn_bb_dcg    — infrastructure DCG driver, not a generator                                 ║
║                                                                                                  ║
║  If you just wrote DESCR_t foo(void *zeta, int entry) { ... } — DELETE IT.                     ║
║  Implement it as an IR_block_t DCG (ir_exec.c + lower_icn.c) driven by icn_bb_dcg.             ║
║  See IR_ICN_UPTO in ir_exec.c and lower_icn_upto() in lower_icn.c as the template.             ║
║                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

**Repo:** corpus+SCRIP
**Branch:** `parser` (SCRIP only — `corpus` and `.github` stay on `main`)
**Sibling ladder:** `GOAL-LANG-RAKU.md` and `GOAL-RAKU-FRONTEND.md`.

## ⚡ PIVOT — session 2026-05-07 (post-RK-27)

**Old goal (RK-0 .. RK-27):** match the existing C frontend (`src/frontend/raku/`)
`--dump-ast` output byte-for-byte. That goal is **CLOSED at PASS=147 FAIL=0**;
~95% of `raku.y` productions are covered. The remaining 5% (sort-with-closure,
`:=` bind operator, etc.) is no longer the priority.

**New goal (RK-28 onward):** flush out the **entire Raku grammar** into
`parser_raku.sc`. We are no longer constrained by what SCRIP's C frontend
supports. Real-world Raku programs use features the C oracle has never seen
(string methods, regex DSL, junctions, meta-operators, signature literals,
`given`/`when` smartmatch chains, slurpy/optional params, twigils outside
classes, `loop {init;cond;step}`, hyper/zip operators, ...). We want the
**entire suite of reasonable Raku programs** to at least *parse without
aborting* and produce *some* IR tree.

**Tree shape:** stripped-down is fine. When a Raku construct has no clean
mapping to existing IR kinds, lower it to a generic `(E_FNC raku_<name> args...)`
call node — same convention `raku_match` / `raku_subst` / `raku_mcall` already
use. The tree must be a valid IR tree (well-formed, dumpable, no garbage
text); it does **not** need to round-trip through the rest of the runtime.
Goal is *parse coverage*, not *execution semantics*.

**Done when:** every program in a curated "real Raku" corpus parses to
completion without `Parse Error`, and the dumped tree is structurally
sane (every node has a known E_* kind; no orphan whitespace; no dangling
captures). Cross-check with `--dump-ast` is **best-effort**: where the C
oracle accepts a program, our tree should still match it (regression
guard); where the C oracle rejects, we accept and emit a placeholder.

Naming, BNF discipline, layout, `White`/`Gray`, `$'name'` tokens,
shift/reduce, n-ary counters, identifier rules — these are the
cross-PARSER style invariants.  Canonical writeup:
`GOAL-PARSER-SNOBOL4.md ## Style Guidelines for parser_*.sc`.
Token classifiers in `parser_raku.sc` mirror `raku.l` where overlap exists
(`var_scalar`, `var_array`, `kw_my`, `kw_say`, `op_add`, …); IR tags
mirror `ir.h` (`E_VAR`, `E_ILIT`, `E_QLIT`, `E_FNC`, `E_ASSIGN`,
`E_ADD`/`E_SUB`/`E_MUL`/`E_DIV`). For Raku features that have no `raku.l`
or `ir.h` precedent, invent token classifier names following the same
UpperCamel convention and lower to generic `E_FNC raku_<name>` nodes.

---

## Session Setup

```bash
( cd /home/claude/SCRIP && git fetch origin parser 2>/dev/null; git checkout parser 2>/dev/null || git checkout -b parser origin/parser 2>/dev/null || git checkout -b parser )

bash /home/claude/SCRIP/scripts/install_system_packages.sh
bash /home/claude/SCRIP/scripts/build_scrip.sh
```

Gate after setup:
```bash
bash /home/claude/SCRIP/scripts/test_smoke_raku.sh    # existing frontend baseline
bash /home/claude/SCRIP/scripts/test_parser_raku.sh   # PAT-RK gate
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
      `corpus/SCRIP/parser_snobol4.sc`.  Maps to §8.
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

## Invariants (post-PIVOT, session 2026-05-07)

- **Coverage over conformance.** A parsed-and-trees program is a win,
  even if the tree differs from `--dump-ast`. A Parse Error is a loss.
- **No more LANG-ladder gating.** Pre-pivot, "PAT-RK does not race ahead
  of the LANG ladder" was the rule. Post-pivot, PAT-RK leads: when we
  parse a Raku construct the C frontend doesn't, we emit a placeholder
  tree (`(E_FNC raku_<name> args...)`) and move on. The C frontend may
  catch up later or never; that's a LANG-ladder problem, not ours.
- **Best-effort oracle parity.** Where `--dump-ast` succeeds, our tree
  should still match it (regression guard — the existing 147 fixtures
  stay green). Where `--dump-ast` fails, we accept and emit a tree;
  the gate just checks "did it parse and produce a non-empty tree".
- Test programs in `corpus/programs/raku/parser/` (oracle-matching) are
  owned by PAT-RK; new programs in `corpus/programs/raku/parser-coverage/`
  (no-abort-only) are also owned by PAT-RK.
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
  may have similar surface→IR name remappings; probe the oracle first
  when one exists, otherwise pick a `raku_<name>` placeholder.

---

## Rung ladder — POST-PIVOT (RK-28 onward)

**Anchored to the official Raku grammar**, `rakudo/src/Perl6/Grammar.nqp`
(5933 lines, 759 production rules, 495 unique non-terminals). This is
the *spec* — every rung below names the exact `proto`/`token`/`rule`
non-terminals it covers, drawn verbatim from `Grammar.nqp`. When in
doubt, the grammar file wins; this ladder paraphrases it.

### Discipline (NEVER BREAKS)

Every rung lands on a **green gate** before the next begins. The gate
is the existing `test_parser_raku.sh` (PASS=147 starting; rung deltas
add to it) **plus** the new `test_parser_raku_coverage.sh` (parse-only,
no oracle compare, see RK-28-A). Both must show no regression. Any
rung that breaks an earlier rung's fixture is reverted on the spot;
the rung's spec is then split smaller and retried. We do **not** push
forward through breakage — a half-landed rung is a stop-the-line.

The rung size discipline:

- One **proto** category per rung (e.g. RK-28 covers exactly
  `statement_control:sym<...>` arms; RK-29 covers
  `package_declarator:sym<...>` arms; …). Each rung is a single
  semantic surface.
- Inside a rung, **one `:sym<X>` arm at a time**. `if` first, gate;
  then `unless`, gate; then `while`, gate. Each arm = an internal
  micro-step. The rung is "landed" when every arm of its proto is
  passing the gate (or explicitly deferred to a later rung with a
  one-line note).
- Coverage fixtures are added **one per arm**. Tiny, named after the
  arm: `stmt_ctrl_if.raku`, `stmt_ctrl_unless.raku`, etc.
- After every arm, run **both gates**. Commit only when both green.

Where a rung's arm overlaps work already done by RK-3..RK-27 (e.g.
`statement_control:sym<if>` is already covered), the arm is marked
`✓ already covered` and the rung moves on. The gate still runs to
prove the existing coverage hasn't drifted.

### RK-28 — `statement_control:sym<...>` (the 19 statement-level keywords) — LANDED session 2026-05-07

Spec source: `Grammar.nqp` lines 1134–1391.  All 19 arms covered.

The full alternation set, in spec order:
- `if` ✓ already covered (RK-3, RK-23)
- `unless` ✓ already covered (RK-11)
- **`without`** ✓ LANDED — `(E_FNC raku_without cond block)`. Token + `Finish_without` + `WithoutStmt` + 3 anchors + 1 fixture.
- `while` ✓ already covered (RK-3)
- `repeat` ✓ already covered (RK-19, RK-23)
- `for` ✓ already covered (RK-3, RK-10, RK-23)
- **`whenever`** ✓ LANDED — `(E_FNC raku_whenever expr block)`. xblock shape (no parens).
- **`foreach`** ✓ LANDED — Perl-5 alias; reuses the existing `Finish_for` machinery for `(E_EVERY (E_ITERATE name expr) block)`. Note: official spec rejects `foreach` with `obs` panic; we accept for parse-coverage.
- **`loop`** ✓ LANDED (two arms) — `loop { block }` infinite → `(E_WHILE (E_ILIT 1) block)` (clean E_* reuse, no placeholder); `loop (init; cond; step) { block }` C-style → `(E_FNC raku_loop init cond step block)` placeholder.  Required new `LoopSubExpr` non-terminal that accepts assignment-as-expression (Raku's `Expr` includes `=` at the top tier; ours did not).
- **`need`** ✓ LANDED — `(E_FNC raku_need (E_QLIT "Module::Path"))`.
- **`import`** ✓ LANDED — `(E_FNC raku_import (E_QLIT modname))`.
- **`no`** ✓ LANDED — `(E_FNC raku_no (E_QLIT "strict"))`.
- **`use`** ✓ LANDED — `(E_FNC raku_use (E_QLIT "v6"))`.
- **`require`** ✓ LANDED — `(E_FNC raku_require (E_QLIT modname))`.
- `given` ✓ already covered (RK-17, RK-23)
- `when` ✓ already covered (RK-17)
- `default` ✓ already covered (RK-17)
- **`CATCH`** ✓ LANDED for free form (CATCH outside try) — `(E_FNC raku_catch_block block)` placeholder. CATCH inside try unchanged from RK-19/RK-23.
- **`CONTROL`** ✓ LANDED — `(E_FNC raku_control_block block)`.
- **`QUIT`** ✓ LANDED — `(E_FNC raku_quit_block block)`.

**Gate at RK-28 close (verified):** smoke PASS=5, oracle parity PASS=147 (unchanged
throughout — full regression protection held), coverage COV_PASS=13.

**Discovery during RK-28**: bare `my $i;` (no type annotation, no `=` initializer)
does not currently parse via either `TypedDeclStmt` (requires type) or `AssignStmt`
(requires `=`).  This is a pre-existing gap, surfaced when writing the loop_three
fixture.  **Filed for cleanup**: RK-28-cleanup or similar — add a `BareDeclStmt`
arm matching `$'my' $'  ' (VarScalar | VarArray | VarHash) $';' Push_empty (E_ASSIGN & 2)`
mirroring `KW_MY VAR_SCALAR ';'` → `(E_ASSIGN var (E_QLIT ""))` from raku.y line 267-271.

Per-arm micro-step pattern:
- [ ] Add token classifier (`KwWithout`, `KwWhenever`, `KwLoop`, …)
      mirroring `Grammar.nqp` keyword list.
- [ ] Add grammar arm to `Stmt` (or wherever the proto lands).
- [ ] Add coverage fixture in `parser-coverage/`.
- [ ] Run **both gates**. Commit if green; revert and split if not.

**Gate at RK-28 close:** `test_parser_raku.sh` PASS=147 (unchanged —
spec parity is regression-protected; new placeholder lowerings live
under coverage gate only). `test_parser_raku_coverage.sh` reports
13 new placeholder arms × 1 fixture = COV_PASS=13.

### RK-28-A — coverage gate infrastructure (lands FIRST, before any RK-28 arm) — LANDED session 2026-05-07

- [x] New script `scripts/test_parser_raku_coverage.sh`. Walks
      `corpus/programs/raku/parser-coverage/`. For each `.raku`,
      runs `parser_raku.sc` on stdin, captures stdout. PASSes iff:
      exit 0, stdout non-empty, no `Parse Error` in stdout, first
      line of trimmed stdout starts with `(STMT`. No oracle compare.
      Reports `COV_PASS=N COV_FAIL=M`.
- [x] New empty directory `corpus/programs/raku/parser-coverage/`
      (with a `README.md` explaining the parse-only contract).
- [x] Verify `test_parser_raku.sh` (oracle parity gate) reads
      ONLY from `parser/`, not `parser-coverage/`. The two are
      strictly separate.
- **Gate (verified):** `test_parser_raku.sh` PASS=147 unchanged.
      `test_parser_raku_coverage.sh` reports `COV_PASS=0 COV_FAIL=0`
      against an empty directory (script wired and working).
      `test_smoke_raku.sh` PASS=5 unchanged.

### RK-29 — `statement_prefix:sym<...>` (the 16 phasers + adverb prefixes) — LANDED session 2026-05-07

- [x] 15 block-only phasers (all-caps): BEGIN END INIT CHECK ENTER LEAVE KEEP UNDO FIRST NEXT LAST PRE POST CLOSE TEMP — `PHASER { block }` → `(E_FNC raku_phaser_<name> body)`.
- [x] 6 lowercase block-value phasers: do once start supply react quietly — `keyword { block }` → `(E_FNC raku_<name> body)`.
- [x] 5 list adverbs: race hyper lazy eager sink — `keyword EXPR ;` → `(E_FNC raku_<name> expr)`.
- [x] 26 keyword tokens, 26 finish_*/Finish_* pairs, 21 grammar productions, Stmt/BlockStmt/SubBlockStmt updated.
- [x] 26 fixtures in `parser-coverage/stmt_pfx_*.raku`.
- [x] `try` already covered (RK-19); `gather` already covered (RK-21).
- **Gate:** smoke PASS=5 FAIL=0, oracle PASS=147 FAIL=0, COV_PASS=39 FAIL=0. corpus@58a0be4.

Spec source: `Grammar.nqp` lines 1394–1432.

- **`BEGIN`** / **`CHECK`** / **`INIT`** / **`END`** — compile-time / run-time phasers.
- **`ENTER`** / **`LEAVE`** / **`KEEP`** / **`UNDO`** — block-scoped phasers.
- **`FIRST`** / **`NEXT`** / **`LAST`** — loop phasers.
- **`PRE`** / **`POST`** — assertion phasers.
- **`CLOSE`** — file-scope phaser.
- **`TEMP`** — dynamic-temporary phaser.
- **`race`** / **`hyper`** / **`lazy`** / **`eager`** / **`sink`** — list adverbs.
- **`try`** ✓ already covered (RK-19) as stmt; spec has it here too.
- **`do`** — `do { block }` value-from-block.
- **`gather`** ✓ already covered (RK-21).
- **`once`** — once-per-program block.
- **`start`** — promise/concurrency block.
- **`supply`** / **`react`** — concurrency block.
- **`quietly`** — warning-suppression block.

Lowering: each prefix takes a block/expr; emit
`(E_FNC raku_phaser_<name> body)` placeholder. One arm at a time, gate
after each.

**Gate at RK-29 close:** `test_parser_raku.sh` PASS=147 unchanged.
`test_parser_raku_coverage.sh` cumulative ≥ 13+18 = 31.

### RK-30 — `package_declarator:sym<...>` (the 10 package-class kinds)

Spec source: `Grammar.nqp` lines 1875–1934.

- **`package`** — generic package; `(E_FNC raku_package name body)`.
- **`module`** — module declaration.
- **`class`** ✓ already covered (RK-24).
- **`grammar`** — Raku grammar (THE big one — body opaque this rung).
- **`role`** — role definition (in speculative RK-39).
- **`knowhow`** — meta-protocol-level package.
- **`native`** — native (FFI) package.
- **`slang`** — language extension package.
- **`trusts`** — trusts declaration inside a package body.
- **`also`** — additional traits applied to current package.

Lowering: `(E_FNC raku_pkg_<kind> name body)` placeholder. Body is
captured as opaque E_QLIT this rung — proper structural parsing of
grammar/rule/token/regex bodies waits for RK-37+.

**Gate:** PASS=147; COV cumulative ≥ 31+8 = 39.

### RK-31 — `scope_declarator:sym<...>` (the 9 scope keywords)

Spec source: `Grammar.nqp` lines 2287–2309.

- **`my`** ✓ already covered (RK-1, RK-19, RK-23, RK-26).
- **`our`** — package-scoped variable.
- **`has`** ✓ already covered (RK-24).
- **`HAS`** — inline composite attribute.
- **`augment`** — open-class augmentation scope.
- **`anon`** — anonymous declaration.
- **`state`** — state variable (persists across calls).
- **`supersede`** — supersede declaration scope.
- **`unit`** — unit-scope declaration.

Lowering: each is a wrapper around a declaration. `our $x = 1;` →
`(E_FNC raku_scope_our (E_ASSIGN (E_VAR x) (E_ILIT 1)))`. `state` /
`anon` / `unit` / `augment` / `supersede` similar.

**Gate:** PASS=147; COV cumulative ≥ 39+6 = 45.

### RK-32 — `routine_declarator:sym<...>` + `multi_declarator:sym<...>`

Spec source: `Grammar.nqp` lines 2412–2424 + `multi_declarator` arms.

`routine_declarator`:
- **`sub`** ✓ already covered (RK-4).
- **`method`** ✓ already covered (RK-24).
- **`submethod`** — class-only method, not inherited.
- **`macro`** — AST-rewriting routine (deprecated but parseable).

`multi_declarator`:
- **`multi`** — multi sub/method dispatch.
- **`proto`** — proto routine declaration.
- **`only`** — singleton routine (default).

Lowering: existing sub_decl machinery wraps; placeholder name
`(E_FNC raku_multi sub_node)` etc.

**Gate:** PASS=147; COV cumulative ≥ 45+5 = 50.

### RK-33 — `regex_declarator:sym<...>` and `type_declarator:sym<...>`

Spec source: `Grammar.nqp` lines 2861–3005.

`regex_declarator` (THIS is where grammar/regex bodies live):
- **`rule`** — rule definition with `:sigspace`.
- **`token`** — token definition (no backtracking, no `:sigspace`).
- **`regex`** — regex definition (full backtracking).

`type_declarator`:
- **`enum`** — enum declaration.
- **`subset`** — subset type with where-clause.
- **`constant`** — compile-time constant.

Strategy: bodies opaque (E_QLIT) for regex_declarator. RK-37+ will
crack open the regex body language.

**Gate:** PASS=147; COV cumulative ≥ 50+6 = 56.

### RK-34 — `statement_mod_cond:sym<...>` and `statement_mod_loop:sym<...>`

Spec source: `Grammar.nqp` lines 1475–1486.

These are **postfix modifiers** — `say "hi" if $x;` is a stmt + mod.

`statement_mod_cond`:
- **`if`** — `STMT if EXPR;` → `(E_IF expr stmt)`.
- **`unless`** — → `(E_IF (E_NOT expr) stmt)`.
- **`when`** — `STMT when EXPR;` smartmatch arm at stmt level.
- **`with`** — `STMT with EXPR;` → `(E_FNC raku_with expr stmt)`.
- **`without`** — `STMT without EXPR;` → opposite of `with`.

`statement_mod_loop`:
- **`while`** — `STMT while EXPR;` → `(E_WHILE expr stmt)`.
- **`until`** — `STMT until EXPR;` → `(E_UNTIL expr stmt)`.
- **`for`** — `STMT for EXPR;` → `(E_EVERY (E_ITERATE expr) stmt)`.
- **`given`** — `STMT given EXPR;` topicalize.

These are *grammar shape* changes — every existing `Stmt` arm needs
an optional postfix modifier. Done as a Stmt-wrapper pattern.

**Gate:** PASS=147; COV cumulative ≥ 56+9 = 65.

### RK-35 — `term:sym<...>` (the 25 terminal forms)

Spec source: `Grammar.nqp` lines 1490–3121.

- `fatarrow`, `colonpair` — already partial via RK-23 named-args.
- `variable` ✓ via VarScalar/VarArray/VarHash.
- `package_declarator`/`scope_declarator`/`routine_declarator`/`multi_declarator`/`regex_declarator`/`type_declarator` — covered by RK-30..RK-33.
- `circumfix` — `(...)`, `[...]`, `{...}` parenthesised forms.
- `statement_prefix` — covered by RK-29.
- **`**`** — `**` whatever-star (slurpy whatever).
- **`*`** — `*` whatever (anonymous lambda placeholder).
- **`lambda`** — `-> $x { ... }` and `{ ... }` blocks as terms.
- `value` — see RK-36.
- **`unquote`** — `{{{ stmt }}}` quasi-quote escape.
- **`!!`** — produced inside `?? !!` ternary.
- **`::?IDENT`** — pseudo-package compile-time symbol.
- **`p5end`** / **`p5data`** — Perl-5 compat.
- **`undef`** — undefined value literal.
- **`new`** ✓ already covered (RK-23).
- **`self`** ✓ already covered (RK-24).
- **`now`**, **`time`**, **`nano`** — time terms.
- **`empty_set`** — `∅` Unicode.
- **`rand`** — random terminal.
- **`...`** — yada-yada (NYI).
- **`???`** — yada-yada (warning).

Lowering: most → `(E_FNC raku_term_<name>)` zero-arg placeholders.

**Gate:** PASS=147; COV cumulative ≥ 65+14 = 79.

### RK-36 — `value:sym<...>` and `number:sym<...>`

Spec source: `Grammar.nqp` `value` and `number` proto sections.

- `value:sym<quote>` ✓ already covered (LitStrSQ, LitStrDQ).
- `value:sym<number>` — covers `LIT_INT` and `LIT_FLOAT` ✓.
- **`value:sym<version>`** — `v6.c`, `v6.d.PREVIEW`.
- **`value:sym<rat>`** — rational literals `1/2`, `1.5`.
- **`value:sym<radix>`** — `:16<ff>`, `:2<1010>` radix literals.
- **`value:sym<complex>`** — `3+2i` complex.
- **`number:sym<bare_complex_number>`** / **`bare_rat_number`**.

Lowering: keep the literal text in E_QLIT; let runtime decide later.

**Gate:** PASS=147; COV cumulative ≥ 79+5 = 84.

### RK-37 — `infix:sym<...>` long tail (~80 operators)

Spec source: `Grammar.nqp` `infix:sym<...>` declarations.

The current parser handles `+`, `-`, `*`, `/`, `%`, `~`, `==`, `!=`,
`<`, `>`, `<=`, `>=`, `eq`, `ne`, `&&`, `||`, `..`, `..^`. The full
list adds:

- **Numeric**: `**` (exponent), `+&` (and-bitwise), `+|`, `+^`, `+<`, `+>`, `div`, `mod`, `gcd`, `lcm`.
- **String**: `~&`, `~|`, `~^`.
- **Boolean**: `^^` (xor), `//` (defined-or), `andthen`, `orelse`, `notandthen`.
- **Comparison**: `<=>` (numeric three-way), `leg` (string three-way), `cmp`, `===`, `eqv`, `=:=`.
- **Smart-match family**: `~~` ✓, `!~~`.
- **Set ops**: `(elem)`, `(cont)`, `(|)`, `(&)`, `(^)`, `(-)`, `(<=)`, `(<)`, `(>=)`, `(>)`.
- **Range/sequence**: `..` ✓, `..^`, `^..`, `^..^`, `...`, `...^`.
- **Functional**: `o` (compose), `R` (reverse-args), `X`, `Z`.
- **Assignment family**: `:=` (bind), `::=` (read-only bind), and all
  `OP=` augments — RK-29 in speculative ladder.

Per-operator approach: each `infix:sym<X>` adds one keyword classifier
and one grammar arm at the right precedence tier. Lower to
`(E_<TAG> lhs rhs)` if TAG exists in ir.h, else
`(E_FNC raku_op_<name> lhs rhs)`.

**This rung is large** — split into RK-37a (numeric+string ops,
~15), RK-37b (boolean+three-way, ~10), RK-37c (set ops, ~10),
RK-37d (range/sequence, ~6), RK-37e (functional + bind, ~6) —
each a separate commit, separate gate run.

**Gate at RK-37 close:** PASS=147; COV cumulative ≥ 84+47 = 131.

### RK-38 — `prefix:sym<...>` and `postfix:sym<...>`

Spec source: `Grammar.nqp` `prefix:sym` / `postfix:sym` declarations.

Prefixes: `!` ✓, `-` ✓, `+`, `~`, `?`, `|`, `||`, `++` (in RK-29
speculative), `--`, `^`, `let`, `temp`.
Postfixes: `++`, `--`, `[i]` ✓, `{k}` ✓, `<k>` ✓, `(args)` ✓,
`.method` ✓, `.()`, `.[]`, `.{}`, `.<>`.

**Gate:** PASS=147; COV cumulative ≥ 131+10 = 141.

### RK-39 — `circumfix:sym<...>` brackets/braces/quotes

Spec source: `Grammar.nqp` `circumfix:sym<...>` declarations.

- `( ... )` ✓ — parens.
- `[ ... ]` — array literal.
- `{ ... }` ✓ — block.
- `« ... »`, `<< ... >>` — quote-words.
- `< ... >` — quote-words bare.
- `:( ... )` — signature literal.
- `STATEMENT_LIST(... )` — eval-style.

**Gate:** PASS=147; COV cumulative ≥ 141+6 = 147.

### RK-40 — `quote:sym<...>` (the 13 quoting variants)

Spec source: `Grammar.nqp` `quote:sym<...>` declarations.

- `quote:sym<apos>` ✓ — `'...'` single-quote.
- `quote:sym<dblq>` ✓ — `"..."` double-quote.
- `quote:sym<q>` — `q[ ... ]` Q-form single.
- `quote:sym<qq>` — `qq[ ... ]` Q-form double.
- `quote:sym<Q>` — `Q[ ... ]` raw quote.
- `quote:sym<qw>` — `qw[ a b c ]` word list.
- `quote:sym<qx>` — `qx[ ... ]` shell exec.
- `quote:sym<qqx>` — `qqx[ ... ]` interpolated shell.
- `quote:sym</ />` ✓ — regex.
- `quote:sym<rx>` — `rx/ ... /` regex factory.
- `quote:sym<m>` — `m/ ... /` match (and `m:g/ ... /` ✓).
- `quote:sym<s>` — `s/ ... / ... /` substitution ✓.
- `quote:sym<tr>`, `quote:sym<TR>` — translation.

**Gate:** PASS=147; COV cumulative ≥ 147+8 = 155.

### RK-41 — Pod blocks

Spec source: `Grammar.nqp` `pod_*` rules.

- `=begin pod ... =end pod` — Pod block.
- `=head1`, `=head2`, etc. — directive blocks.
- `=for`, `=item`, `=comment`.
- `#|` and `#=` declarator-attached Pod.

Lowering: capture body as opaque E_QLIT inside
`(E_FNC raku_pod_<kind> (E_QLIT body))`.

**Gate:** PASS=147; COV cumulative ≥ 155+5 = 160.

### RK-42 — Regex/grammar body internals (the OTHER big one)

Spec source: `Grammar.nqp` `Perl6::RegexGrammar` (the inner-grammar slang).

Replace opaque E_QLIT bodies from RK-30 (`grammar`), RK-33
(`regex_declarator`), RK-40 (regex quote forms) with structured trees:

- `<rulename>` subrule call → `(E_FNC raku_subrule (E_QLIT name))`.
- `||` longest-token alternation; `|` first-match alternation.
- `<?ws>`, `<.ws>`, `<( ... )>` capture markers.
- `**` separated quantifier, `~` delimited list.
- `<commit>`, `<cut>`.
- `<[a..z]>`, `<-[0..9]>`, `<+[a..z]+digit>` character classes.
- `:i` / `:m` / `:s` adverbs.
- `:my $x = ...;` runtime declaration inside regex.

Per the existing PARSER-* convention, this rung is a separate
sub-grammar inside `parser_raku.sc` — a fresh `RegexCompiland` PATTERN
that takes opaque body text and produces a structured tree.

**Gate:** PASS=147; COV cumulative ≥ 160+10 = 170.

### RK-43 — MAIN signature, sub signatures (full)

Spec source: `Grammar.nqp` `signature` and `parameter` rules.

Signatures are deeply structured. Coverage scope:
- Optional params: `$x?`.
- Default values: `$x = 0` ✓ in speculative RK-34.
- Slurpy: `*@a`, `*%h`.
- Named: `:$x`, `:x($y)`.
- Typed: `Int $a` ✓ (RK-23).
- Constraints: `$a where { ... }`.
- Sub-signatures: `($a, ($b, $c))`.
- Capture: `\$captured`.
- Trait modifiers: `is rw`, `is copy`, `is required`.

**Gate:** PASS=147; COV cumulative ≥ 170+8 = 178.

### RK-44 — Pair / colonpair / fatarrow forms

Spec source: `Grammar.nqp` `colonpair`, `fatarrow`, `pair`.

- `:foo`, `:!foo`, `:foo<bar>`, `:foo(1)` — colonpair.
- `foo => 1` ✓ (RK-23 named args).
- `:bar(:baz)` — nested.

**Gate:** PASS=147; COV cumulative ≥ 178+4 = 182.

### RK-45 — Special variables (`$/`, `$!`, `$_`, `@*ARGS`, `%*ENV`, ...)

Spec source: `Grammar.nqp` `special_variable:sym<...>`.

The current `VarStdIn`/`VarStdOut`/`VarStdErr` (RK-25) covers the
three I/O ones. Spec adds: `$/`, `$!`, `$_`, `@*ARGS`, `%*ENV`,
`$*PROGRAM-NAME`, `$*KERNEL`, `$*DISTRO`, `$*VM`, `$*PERL`, `$*RAKU`,
`$*OUT`, `$*IN`, `$*ERR`, `&?ROUTINE`, `&?BLOCK`, `$?LINE`, `$?FILE`,
`$?CLASS`, `$?ROLE`, `::?CLASS`, `$=pod`, `$=finish`, ...

Lowering: each → `(E_VAR <stripped_name>)` or
`(E_FNC raku_specvar_<name>)` depending.

**Gate:** PASS=147; COV cumulative ≥ 182+12 = 194.

### RK-46 — `dotty:sym<...>` (the dotty-method variants)

Spec source: `Grammar.nqp` `dotty:sym<...>`.

- `.method` ✓ (RK-22 / RK-25).
- `.+method` — call all matching methods.
- `.*method` — call all, allow none.
- `.?method` — call if exists.
- `.&fn` — invoke as function.
- `.=method` — call and assign back.

**Gate:** PASS=147; COV cumulative ≥ 194+5 = 199.

### RK-47 — Meta-operators

Spec source: `Grammar.nqp` `*_meta_operator` protos.

- `prefix_circumfix_meta_operator`: `[+]`, `[\\+]`, etc.
- `infix_postfix_meta_operator`: `+=`, `-=`, etc. (in speculative RK-29).
- `infix_prefix_meta_operator`: `!==`, `!eq`.
- `infix_circumfix_meta_operator`: `>>op<<`, `«op»`.
- `postfix_prefix_meta_operator`: `>>op`.
- `prefix_postfix_meta_operator`: `op<<`.

**Gate:** PASS=147; COV cumulative ≥ 199+10 = 209.

### RK-48 — Trait modifiers (`is rw`, `does Bar`, `of Type`, ...)

Spec source: `Grammar.nqp` `trait_mod:sym<...>`.

- `trait_mod:sym<is>` — `is rw`, `is copy`, `is required`, …
- `trait_mod:sym<does>` ✓ partial (RK-39 speculative).
- `trait_mod:sym<hides>`.
- `trait_mod:sym<of>`.
- `trait_mod:sym<as>`.
- `trait_mod:sym<returns>`.
- `trait_mod:sym<handles>`.
- `trait_mod:sym<will>`.

**Gate:** PASS=147; COV cumulative ≥ 209+8 = 217.

### RK-49 — `terminator:sym<...>` and `eat_terminator` edge cases

Spec source: `Grammar.nqp` `terminator:sym<...>` and `eat_terminator`.

Make sure every `;`-or-newline-or-`}` terminator path the official
grammar accepts is also accepted by `parser_raku.sc`. This is a
**hardening rung** — no new productions, just edge cases that came
up during RK-28..RK-48.

**Gate:** PASS=147; COV cumulative bookkeeping; no new fixtures
unless edge cases surfaced.

### RK-50 — Real-world program corpus

Pull representative programs from rosetta-code-raku, rakudo's `t/`
directory, and the `examples/` of popular Raku modules. Verify each
parses and emits a structurally sane tree. This rung is the final
"never breaks" verification — any program in this curated corpus
that still hits Parse Error is a bug to backfill into earlier rungs.

**Gate:** PASS=147; COV ≥ 250 covering at least 50 distinct
real-world Raku programs.

### Beyond RK-50

- Inner-body parsing of regex/rule/token (RK-42 was opaque-only).
- Full `make`/`made`/`match` action methods.
- `MAIN`-driven command-line auto-parse.
- Full Pod content parsing (RK-41 was block-level only).

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
- [x] FUTURE: canonical `white ARBNO(white)` form — **WON'T DO.**
      The FENCE-based `White`/`Gray` is correct, readable, and passes all gates.
      Changing to `ARBNO(white)` form risks regex-tier re-segmentation bugs
      (documented in RK-WS2 above). No benefit justifies the risk.

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
      SCRIP HEAD (verified session 2026-05-07).

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
      SCRIP @ `d96d4ef7`.
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
- **Gate:** PASS=126 FAIL=0 ✓  corpus@838304e  SCRIP@d96d4ef7

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

---

## Watermark

Session 2026-05-07 (RK-29 LANDED, continuation) — **PARSER-RK-29 LANDED**

- smoke PASS=5, oracle PASS=147, COV_PASS=39 FAIL=0. corpus@58a0be4.
- 26 statement_prefix arms: 15 block-only phasers (BEGIN..TEMP), 6 block-value (do/once/start/supply/react/quietly), 5 list adverbs (race/hyper/lazy/eager/sink).
- Next: **RK-30** (`package_declarator:sym<...>` — the 10 package/class kinds).

Session 2026-05-07 (PIVOT + RK-28-A + RK-28 LANDED) — **PARSER-RK PIVOTED to
official-grammar coverage**, **RK-28-A coverage gate infra LANDED**,
**RK-28 (`statement_control:sym<...>`) FULLY LANDED with all 13 new arms**.

### Gates at handoff (all green, all verified post-final-edit)

- `test_smoke_raku.sh`: PASS=5 FAIL=0 (unchanged from session start)
- `test_parser_raku.sh`: PASS=147 FAIL=0 (unchanged throughout — full
  regression protection held; oracle parity gate is intact)
- `test_parser_raku_coverage.sh`: COV_PASS=13 COV_FAIL=0 (NEW gate;
  was 0/0 at session start)

### What changed this session

**Strategic pivot (top of GOAL file):** old goal of byte-for-byte oracle
parity with `--dump-ast` was CLOSED at PASS=147 (~95% of `raku.y`).  New
goal is full coverage of the OFFICIAL Raku grammar (`rakudo/Grammar.nqp`,
5933 lines, 759 productions, 495 unique non-terminals).  Real-world Raku
programs use features the C frontend has never seen — for those, we
emit placeholder `(E_FNC raku_<name> args...)` trees and accept that the
oracle gate cannot grade them.

**New rung ladder RK-28..RK-50** grounded in `Grammar.nqp`'s `proto`
skeleton.  Each rung covers one proto category (`statement_control`,
`statement_prefix`, `package_declarator`, etc.); each `:sym<X>` arm is
a separate micro-step with its own fixture; both gates run after every
arm with revert-on-red discipline.

**RK-28-A (coverage gate infrastructure):**
- New `SCRIP/scripts/test_parser_raku_coverage.sh` — parse-only gate.
  Four assertions per fixture: exit 0, non-empty output, no `Parse Error`
  substring, first non-blank line begins `(STMT`.  No oracle compare.
  Skips cleanly when `parser-coverage/` is empty or absent.
- New `corpus/programs/raku/parser-coverage/` directory with README.md
  documenting the parse-only contract and the naming convention
  (`stmt_ctrl_<arm>.raku`, `pkg_decl_<arm>.raku`, etc.).

**RK-28 (`statement_control:sym<...>`) — all 19 arms covered:**

13 newly-landed arms (one fixture each, in `parser-coverage/`):

| Arm | Lowering | Strategy |
|-----|----------|----------|
| `without` | `(E_FNC raku_without cond block)` | Placeholder |
| `whenever` | `(E_FNC raku_whenever expr block)` | Placeholder, xblock shape (no parens) |
| `foreach` | `(E_EVERY (E_ITERATE name expr) block)` | Reuses existing `for` machinery |
| `loop {}` | `(E_WHILE (E_ILIT 1) block)` | Clean E_* reuse, no placeholder |
| `loop (i;c;s) {}` | `(E_FNC raku_loop init cond step block)` | Placeholder + new `LoopSubExpr` |
| `use` | `(E_FNC raku_use (E_QLIT modname))` | Placeholder + new `ModuleName` |
| `no` | `(E_FNC raku_no (E_QLIT modname))` | Placeholder |
| `need` | `(E_FNC raku_need (E_QLIT modname))` | Placeholder |
| `import` | `(E_FNC raku_import (E_QLIT modname))` | Placeholder |
| `require` | `(E_FNC raku_require (E_QLIT modname))` | Placeholder |
| `CATCH` (free) | `(E_FNC raku_catch_block block)` | Placeholder; CATCH-inside-try unchanged |
| `CONTROL` | `(E_FNC raku_control_block block)` | Placeholder |
| `QUIT` | `(E_FNC raku_quit_block block)` | Placeholder |

Already-covered 6 arms (preserved from RK-3..RK-23): `if`, `unless`,
`while`, `repeat`, `for`, `given`/`when`/`default`.

### New non-terminals introduced this session

- **`LoopSubExpr`** — accepts `lhs = rhs` (assignment-as-expression) OR
  plain `Expr`.  Required because Raku's three-part `loop` allows
  assignments in init/step positions, but our top-level `Expr` does
  not include `=` (assignment is a stmt, not an expr).  FENCE-guarded
  before `Push_var` per the RK-24 match-time-side-effect rule.
- **`ModuleName`** — captures `Foo`, `Foo::Bar::Baz`, or `v6` /
  `v6.c` as a single string into `capmodname`.  Used by all 5
  module-load stmts (use/no/need/import/require).

### One stop-the-line caught and fixed

`stmt_ctrl_loop_three.raku` initially failed because the fixture used
bare `my $i;` (no `=`, no type annotation).  Diagnosed in isolation —
the existing parser handles `TypedDeclStmt` (requires type annotation)
and `AssignStmt` (requires `=`) but NOT bare `my $var ;`.  Fixed by
changing the fixture to `my $i = 0;`.  This is a pre-existing parser
gap, not something this session introduced.

**Filed for follow-up:** add a `BareDeclStmt` arm matching
`$'my' $'  ' (VarScalar | VarArray | VarHash) $';' Push_empty (E_ASSIGN & 2)`
to mirror raku.y lines 267–271 (`KW_MY VAR_SCALAR ';'` →
`(E_ASSIGN var (E_QLIT ""))`).  Owner: any future PARSER-RK session,
opportunistic — not blocking.

### Files touched (all four repos clean before commit on each)

- `corpus/SCRIP/parser_raku.sc` — 13 new keyword tokens
  (without, whenever, foreach, loop, use, no, need, import, require,
  CONTROL, QUIT — CATCH already existed), 13 new finishers, 14 new
  grammar productions (13 stmts + LoopSubExpr + ModuleName),
  3 anchor lists updated (Stmt, BlockStmt, SubBlockStmt).
- `corpus/programs/raku/parser-coverage/README.md` — new.
- `corpus/programs/raku/parser-coverage/stmt_ctrl_*.raku` — 13 fixtures.
- `SCRIP/scripts/test_parser_raku_coverage.sh` — new, executable.
- `.github/GOAL-PARSER-RAKU.md` — PIVOT block at top, Invariants
  rewritten, RK-28..RK-50 ladder grounded in Grammar.nqp, RK-28-A and
  RK-28 marked LANDED, this watermark.
- `.github/PLAN.md` — table line for PARSER-RAKU updated.

### Commit hashes at handoff

- SCRIP (`parser` branch): `7adcbdbd` — test_parser_raku_coverage.sh
- corpus (`main`): `6f1c61f` — RK-28 LANDED + 13 fixtures + parser_raku.sc grammar
- .github (`main`): this commit (push pending)

### Next session — RK-29 (`statement_prefix:sym<...>`)

`Grammar.nqp` lines 1394–1432.  The 16+ phasers and adverb prefixes:
BEGIN, CHECK, INIT, END, ENTER, LEAVE, KEEP, UNDO, FIRST, NEXT, LAST,
PRE, POST, CLOSE, TEMP, race, hyper, lazy, eager, sink, do, once,
start, supply, react, quietly.  `try` and `gather` already covered.

Per-arm discipline: one phaser at a time, both gates green between
every step.  Each lowers to `(E_FNC raku_phaser_<name> body)` placeholder.
