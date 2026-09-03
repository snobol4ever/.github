# FINDING 2026-09-03 seat11 — Raku `@`-sigil params now alias the caller, which uncovered a second, older bug: `&&`/`||` share one flat precedence tier with comparisons

Row: `raku-array-params-pass-by-copy` (minted by ceo from the bench triage, rank 1). Witness:
`corpus/benchmarks/raku/insertion-sort.raku`. Measured on SCRIP `771d3f98` + this row's own commit.

## THE HEADLINE

**Two independent bugs, not one.** (1) A `@`/`%`-sigil sub parameter always got a private copy of the
caller's container — `insertion-sort(@a) { @a[$i] = ... }` sorted a throwaway copy and the caller's array
came back unchanged (prints `224`, the ref wants `0`). (2) Once (1) is fixed, the SAME kernel still failed
(`6` instead of `0`) because its `while $i >= 0 && @a[$i] > $key` loop condition has ALWAYS parsed wrong:
`raku.y`'s `cmp_expr` production folds `OP_AND`/`OP_OR` into the identical flat-left-recursive rule family
as the relational/chain-comparison operators, so `A && B > C` reduces as `(A && B) > C`, not `A && (B > C)`.
Bug (2) is not new and has nothing to do with array aliasing — it was simply never *observed* before,
because bug (1) always produced a wrong answer first, on every kernel anyone had tried, so nothing ever ran
far enough into a live `&&`-plus-comparison loop condition to expose it.

## BUG 1 — ARRAY/HASH PARAMS WERE BY-COPY, NOT BY-ALIAS

Root-caused but not fixed twice before on this same task file (seat15 2026-08-30, seat13 2026-08-30 — see
`raku-silent-wrong-answers.task.md` LEDGER): `@`/`%` sigil parameters must bind (alias) the caller's
container per Raku semantics; SCRIP gave the callee an independent copy. The mechanism that fixes this
already existed and was already load-bearing for **Pascal's `var` parameters** — nothing new had to be
invented:

- `stage2_t.proc_table[i].byref_mask` (`src/ir/stage2.h:35`) — a bit-per-parameter mask, populated for
  Pascal from the `var` keyword (`lower_pascal.c:722`) but hardcoded to `0` for Raku (`lower_raku.c`,
  pre-fix) and for Icon (`lower_icon.c:1389`, still `0`, untouched — out of scope for this row).
- `IR_VAR_REF` (`src/templates/bb/bb_var_ref.cpp`) — takes the address of a named local slot, tags it
  `DT_N | (1<<32)` (a "cell pointer" flavor already handled by both `rt_deref`'s asm fast path,
  `src/runtime/rt/rt_asm_helpers.S:32-37` `.Lrd_ptr`, and its C slow path, `rt_deref_slow`,
  `src/runtime/pattern_match.c:1474`).
- `IR_DEREF` (`src/templates/bb/bb_deref.cpp`) / `IR_ASSIGN_VAR` (`src/templates/bb/bb_assign_var.cpp`,
  runtime `rt_assign_var`, asm fast path `src/runtime/rtx/rtx_icnvar.s:24-31` `.Lav_cell`) — read/write
  *through* such a pointer instead of touching the local slot directly.

Fix, entirely in `src/lower/lower_raku.c` + `src/parsers/raku/raku.y`, no new IR op, no new global:

1. **Parser**: `raku.y`'s array-sigil param productions (`param_list : VAR_ARRAY | param_list ',' VAR_ARRAY`)
   now build the param through `rk_byref_param()`, which stamps a `TT_QLIT "@"` marker child onto the
   otherwise-unchanged `var_node()` result — the same "extra child as metadata" convention `rk_typed_param`
   (type) and `rk_slurpy_param` (`"*@"`/`"**@"`/`"*%"`) already use, so nothing downstream that walks params
   by name/count breaks. (Hash `%`-sigil params have **no** `param_list` production at all yet — a
   pre-existing, separate gap; the mask machinery below already covers `%` the day that production exists,
   nothing further to do here.)
2. **Registration** (`rk_param_byref_mask()`, called from `rk_register_proc()`): reads that marker per
   parameter position and sets `proc_table[i].byref_mask` accordingly — mirrors
   `lower_pascal.c:722`'s `var`-keyword read exactly, just keyed off the marker instead of a keyword.
3. **Per-invocation context**: `rcx_t` (was 4 fields, now +3: `cur_proc`, `cur_byref_mask`, `cur_nparams`,
   a stack-local struct, not a global) is populated once at the top of `lower_raku_proc()` by matching
   `proc_table[i].proc == pd`. `rk_name_is_byref(cx, name)` answers "is this bare local name one of the
   *current* sub's byref params" in O(nparams).
4. **Call site** (`lower_rcall()`): for a callee with a nonzero byref mask, a bare-variable argument at a
   byref position lowers to `IR_VAR_REF` (take the caller's address) instead of a value read — mirrors
   `lower_pascal.c:213-230` `pas_call_args_brm()`'s two-branch shape (plain `IR_VAR_REF` for a fresh
   variable, forward the existing pointer unchanged — `IR_VAR` — if the argument is *itself* an
   already-aliased byref parameter, so `a(@x)` calling `b(@x)` calling `c(@x)` chains one address, not
   three).
5. **Reads inside the callee** (`lower_rv`'s `TT_VAR` case): a byref name now lowers to
   `IR_DEREF(IR_VAR(name))` instead of a bare `IR_VAR(name)` — the slot holds a pointer, not the value.
6. **Element writes** (`TT_ARR_SET`): a byref target lowers to `IR_ASSIGN_VAR(IR_VAR(name), arr_set_pure(...))`
   instead of `IR_ASSIGN(name, ...)` — write *through* the pointer so the mutation lands in the caller's
   storage, not a disconnected local copy. (Whole-array reassignment, `@a = newval` inside a byref-bound
   sub, was **not** touched — insertion-sort and every regression probe below only ever mutate by index;
   flagged, not fixed, in case a future kernel needs it.)

Verified with 15 independent hand-written probes (single write, read-then-write, nested for/while, `.end`
method calls, hyphenated sub names, computed indices, cross-iteration read-after-write, multi-hop forwarding)
before ever re-running the real kernel — ASM-DIFF-FIRST's "mint the smallest repro" step is what surfaced
bug 2 cleanly instead of it hiding inside insertion-sort's own complexity.

## BUG 2 — `&&`/`||` NEVER HAD THEIR OWN PRECEDENCE TIER

`raku.y:476-479` already **declares** the intended precedence (`%left OP_OR` looser than `%left OP_AND`
looser than the comparison operators) — this ordering was correct and has presumably sat there unused.
The production rules never implemented it: `cmp_expr : cmp_expr OP_AND divis_expr | cmp_expr OP_OR divis_expr
| cmp_expr OP_EQ divis_expr | ... | cmp_expr '>' divis_expr | ...` puts `&&`/`||` in the *identical*
flat-left-recursive family as `==`/`!=`/`<`/`>`/`<=`/`>=` (which are deliberately flat, via `rk_chain_cmp`,
to support Raku's real chained-comparison syntax, e.g. `0 <= $i < 10`). Because `divis_expr` (comparison
operators' right-hand nonterminal) cannot itself contain a comparison or `&&`/`||`, LALR has no shift option
once it sees `cmp_expr OP_AND divis_expr` with a relational operator as lookahead — it must reduce, and the
reduced `cmp_expr` then becomes the LEFT operand of the *next* operator instead of the right operand's
sub-expression.

Confirmed directly, not inferred, via `--dump-ast` on `while $i >= 0 && @a[$i] > 0 { ... }`:

```
pre-fix:  (TT_GT (TT_SEQ (TT_GE (TT_VAR i) (TT_ILIT 0)) (TT_ARR_GET (TT_VAR a) (TT_VAR i))) (TT_ILIT 0))
          --  i.e. ($i >= 0 && @a[$i]) > 0        (WRONG — matches neither operand's real scope)
post-fix: (TT_SEQ (TT_GE (TT_VAR i) (TT_ILIT 0)) (TT_GT (TT_ARR_GET (TT_VAR a) (TT_VAR i)) (TT_ILIT 0)))
          --  i.e. $i >= 0 && (@a[$i] > 0)         (correct)
```

This is a parser-precedence bug, general to `&&`/`||` combined with **any** relational operator on either
side — insertion-sort's specific loop condition is just the first witness anyone has actually reached.

### THE FIX

`raku.y`: two new stratification levels, `or_expr` and `and_expr`, inserted between `tern_expr` and
`cmp_expr` (`tern_expr : or_expr ... | or_expr` instead of `cmp_expr`; `or_expr : or_expr OP_OR and_expr |
and_expr`; `and_expr : and_expr OP_AND cmp_expr | cmp_expr`), and the two `cmp_expr OP_AND/OP_OR divis_expr`
rules deleted from `cmp_expr` itself. `cmp_expr` keeps every relational/chain/smatch rule byte-identical —
chained comparisons (`rk_chain_cmp`) are untouched. `tern_expr` and everything above it (`expr`) needed no
change: `cmp_expr` had exactly one other consumer in the whole grammar (`tern_expr`'s own two rules) plus
the `%type` declaration, so the blast radius is the six touched lines, not a grammar-wide rewrite.
`bison -d --warnings=none -Wno-yacc` reports the same zero shift/reduce conflicts on `raku.y` before and
after (verified both ways, not assumed).

## VERIFICATION

- `insertion-sort.raku` byte-exact against `.ref` (`0`), both bugs required to be fixed together for this.
- `test_smoke_raku.sh`: `PASS=722 FAIL=0 REFUSED=2 / 724`, **both modes**, unchanged from the pre-existing
  baseline this same task file already recorded (`raku-silent-wrong-answers.task.md` LEDGER, seat13
  2026-08-30: "REFUSED=2/724 both modes, confirmed via a stash-and-rerun control arm that REFUSED=2 is
  pre-existing on origin/main HEAD") — zero regressions from either grammar or lowering change.
- SNOBOL4 blocking set + `strip_comments.py --check` + the cheap gates run via `make pristine && make test`
  (pristine required for a gate verdict per HQ-27) — see this row's LEDGER for the exact tally at push time.
- 15 hand-written byref probes (see task LEDGER) plus the two ad-hoc precedence probes above, all
  independently re-checked after the grammar fix landed on top of the lowering fix.

## NOT ATTEMPTED, correctly out of scope for this row

- Hash (`%`-sigil) parameter aliasing — the grammar has no `param_list` production for a bare `%h` parameter
  at all yet, so there is nothing for the mask/deref machinery to bind to. The mechanism already handles it
  the day that production exists (same marker convention, same mask, same call-site/read/write logic).
- Whole-array reassignment (`@a = ...`) inside a byref-bound sub — untouched, see step 6 above.
- Joining `insertion-sort` to the benchmark grid with a measured multiple, as this row's original GOAL text
  (minted 2026-08-30) asked for. That instruction predates `corpus/benchmarks/raku/README.md`'s
  "two-number basis" self-timed/triangulated methodology (hq_B, 2026-09-01/02): a kernel only joins the grid
  once it carries `wall_us()`/`wall_ms()` brackets and its angle-1/angle-2 rates cross-prove AGREE via
  `bench_triangulate_raku.sh` — a separate, real piece of work (and, per that same README, the triangulator
  currently reports DISAGREE fleet-wide pending a noise floor, independent of anything here). Bracketing
  `insertion-sort.raku` for that pipeline is left as a follow-up, not folded into this correctness fix under
  time pressure.
- Icon's own `byref_mask = 0` hardcode (`lower_icon.c:1389`) — same shape as Raku's pre-fix state, a
  different language's row.

## RECEIPTS

- `src/lower/lower_raku.c` — `rk_param_byref_mask`, `rk_name_is_byref`, `rk_callee_byref_mask`,
  `rcx_t` (+3 fields), `lower_rcall`, `lower_rv` (`TT_VAR`), `TT_ARR_SET`, `rk_register_proc`,
  `lower_raku_proc` — this row's commit.
- `src/parsers/raku/raku.y` — `rk_byref_param`, the `param_list` `VAR_ARRAY` rules, `%type`, `or_expr`/
  `and_expr`/`cmp_expr`/`tern_expr` — this row's commit.
- Precedent mirrored, unmodified: `src/lower/lower_pascal.c:190-345` (`pas_callee_byref_mask`,
  `pas_call_args_brm`, `pas_name_is_byref`, the `IR_ASSIGN_VAR`/`arr_set_pure` byref-write shape).
- `src/ir/stage2.h:35`, `src/runtime/rt/rt.c:397-444,1733-1742` (`byref_mask` storage + accessors, shared,
  language-agnostic, already wired to the driver at `src/driver/scrip.c:1462` etc.).
- `corpus/benchmarks/raku/insertion-sort.raku`, `.ref`.
- Prior art naming this exact gap without fixing it: `raku-silent-wrong-answers.task.md` LEDGER, seat15
  2026-08-30 ("the fix site is presumably wherever a sub parameter's `@`-sigil binding is set up in
  `lower_raku.c`").
