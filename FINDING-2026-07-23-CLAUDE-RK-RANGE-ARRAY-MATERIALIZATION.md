# FINDING — RAKU-100: value-position range materialization (`my @a = LO..HI`)

**Session:** s2026-07-23c · GOAL-RAKU-BB · Claude Opus 4.8
**Rung:** RANGE-ARRAY-MATERIALIZATION — `my @a = 1..5` builds a real 5-element aggregate.

---

## Symptom (reproduced on clean HEAD `afc6b46`)

```
my @a = 1..5;
say @a.elems;   # printed 1  (want 5)
say @a.sum;     # printed 1  (want 15)
say [+] @a;     # printed 1  (want 15)
```

A range assigned to an array in value position collapsed to a **single element**
(the range's first value). `.elems`/`.sum`/`.min`/`.max`/`[+]`/`[*]` all read that
one-element aggregate, so every one of them was wrong on the same input. The prior
cursor flagged this as next-rung item (b) and noted it was the shared root of the
`.sum`/`.min`/`[+]`-on-range failures.

## Root cause

`1..5` lowers to `TT_TO`, which becomes **`IR_TO` — a generator** (a Byrd box that
yields lo, lo+1, …, hi one value per β-resume). That is exactly right for
`for 1..5 -> $x { … }` (the for-loop pumps the generator). But `my @a = 1..5`
lowers as a plain `IR_ASSIGN` whose RHS is that generator, and `IR_ASSIGN` binds only
the **first γ value**. So `@a` got the string `"1"`, `.elems`→1.

The two lowering sites (`TT_ASSIGN` for `@a = …`, `TT_DECL` for `my Type @a = …`) both
fall through to a generic `lower_rv(RHS)` — neither materializes a range into an
aggregate the way the comma-list forms (`my @a = 1,2,3`) already do via `__rk_arr`.

## Fix (grammar rewrite + one runtime fold — no IR, no template, no codegen)

**Pitfall found first:** the natural place to gate this — the lowerer, keyed on the
LHS `@` sigil — DOES NOT WORK, because `var_node()` calls `strip_sigil()`; by the time
the AST reaches the lowerer the variable name is `a`, not `@a`. There is no
language-visible sigil downstream. The array-ness signal only exists at parse time
(the `VAR_ARRAY` token). So the rewrite belongs in the grammar, exactly where the
comma-list / `xx` array-decl forms already special-case their RHS.

1. **`raku.y`** — new helper `rk_arr_rhs(rhs)`: if `rhs` is a `TT_TO`, return a
   `__rk_range_arr(lo, hi)` call node; else return `rhs` unchanged. Wired into the two
   whole-array-decl-from-`expr` productions (`KW_MY VAR_ARRAY '=' expr` and
   `KW_MY IDENT VAR_ARRAY '=' expr`). This mirrors the existing `__rk_arr` wrapping of
   comma-lists — one helper, applied at the array-decl sites, NO-DUP-LOGIC.
   `..^` already lowers to `TT_TO` (exclusive end decremented at parse time in
   `rk_range_ex`), so exclusive ranges flow through the same helper for free.

2. **`by_name_dispatch.c`** — new runtime fold `__rk_range_arr(lo, hi)`: builds the
   SOH(`\x01`)-joined integer sequence `lo..hi` inclusive, mirroring the `__rk_arr`
   aggregate-construction idiom. Empty when `hi < lo` (`5..1` → `""` → `.elems`=0).
   Registered in `rt_builtin_is_known` for mode-4 `@PLT` emission.

Because the RHS becomes an ordinary `TT_FNC` call, it funnels through the proven
`lower_rcall` → `IR_ASSIGN` path that binds the single string result — same as every
other array-producing builtin. No new IR opcode, no BB template, no x86 encoder.

## Verification — both modes, byte-identical

Suite **580 → 593** (+13 smokes), all `[m3 PASS] [m4 PASS]`, zero silent FAIL either
mode. New smokes: `range_arr_elems/_sum/_min/_max/_reduce_add/_reduce_mul/_join/`
`_single/_empty/_var_bounds/_exclusive/_typed` + `range_for_generator_unaffected`.
The last one proves the `for 1..N` generator path is untouched (1..3 sums to 6).

Peers unchanged: **Icon 14/14** both modes, **SNOBOL4 7/7**. The shared-runtime edit
is a single isolated `if (!strcmp(fn,"__rk_range_arr"))` branch keyed on a
Raku-specific name — invisible to Icon/SNOBOL4.

Conflicts: **90 s/r, 9 r/r** — **zero delta** (the wrap adds no grammar ambiguity;
it rewrites an existing RHS node in a semantic action).

Gates: lang-blind emit gate GREEN. Generated files reproduce byte-for-byte
(bison 3.8.2 + flex 2.6.4); `raku.lex.c` byte-identical (only `raku.y` body changed).
Template-purity + concurrency audits rc=1 are **pre-existing** (flag
`bb_call.cpp`/`bb_call_write_slot.cpp` and `GOAL-SNOBOL4/ICON-BB.md` doc anchors —
none in this session's 6-file diff; proven via `git diff --stat HEAD`). No `.s` regen
(zero Raku `.s` in tree; no SNOBOL4/Icon codegen touched).

## Deferred (adjacent, not this rung)

- Bare `@a = 1..5` reassignment (no non-`my` whole-array production exists).
- Reverse ranges (`5..1` yields empty here; Rakudo also yields empty for `..`, so this
  is correct — `reverse` is `5…1` with the sequence op, a separate feature).
- Non-integer / char ranges (`'a'..'e'`), lazy/infinite ranges (`1..*`), range as a
  first-class `Range` object with `.min`/`.max`/`.bounds` methods. Value-position
  materialization to an integer array is the scoped RAKU-100 cut.

## Touched

- **SCRIP:** `src/parser/raku/raku.y` (+`rk_arr_rhs`, wired into 2 array-decl
  productions), `src/parser/raku/raku.tab.c`/`raku.tab.h` (bison regen),
  `src/runtime/by_name_dispatch.c` (+`__rk_range_arr` fold + registration),
  `scripts/test_smoke_raku.sh` (+13 smokes).
- **.github:** `GOAL-RAKU-BB.md` LIVE CURSOR + this finding.
