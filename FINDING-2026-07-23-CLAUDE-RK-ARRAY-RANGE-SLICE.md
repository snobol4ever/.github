# FINDING — RAKU-100: array range-slice `@a[LO..HI]` + float-dot investigation

**Session:** s2026-07-23c (continued) · GOAL-RAKU-BB · Claude Opus 4.8
**Rung LANDED:** ARRAY-RANGE-SLICE — `@a[1..3]` returns the sub-list `(2,3,4)`.
**Rung INVESTIGATED, NOT LANDED:** float trailing-dot — architectural entanglement documented below.

---

## PART 1 — LANDED: array range-slice

### Symptom (clean tree, after the range-materialization rung)
```
my @a = 1,2,3,4,5;
say @a[1..3].join(",");   # printed "2"  (want "2,3,4")
```
A range in subscript position returned a single element (the element at the range's
first value) instead of a slice. Direct counterpart of the value-position range bug:
`1..3` lowers to `IR_TO` (a generator), and `arr_get(@a, idx)` bound only the first
value → `arr_get(@a, 1)` = element 1 = `2`.

### Fix (grammar rewrite + one runtime fold — no IR/template/encoder)
Same shape as the value-position range fix, at the subscript site:
1. **`raku.y`** — helper `rk_arr_index(arr, idx)`: if `idx` is a `TT_TO`, build
   `__rk_arr_slice(arr, lo, hi)`; else the normal `TT_ARR_GET(arr, idx)` element access.
   Wired into the `VAR_ARRAY '[' expr ']'` production. `..^` flows through free.
2. **`by_name_dispatch.c`** — `__rk_arr_slice(arr, lo, hi)` walks the SOH-joined
   aggregate and copies elements at 0-based indices `lo..hi` inclusive into a new
   sub-aggregate (empty when `hi < lo`; clamps `lo` at 0). Registered in
   `rt_builtin_is_known` for mode-4 `@PLT`. Mirrors the `__rk_arr`/`arr_get` idioms.

Scalar subscript (`@a[2]`) is untouched — only a `TT_TO` index diverts to the slice.

### Verification — both modes, byte-identical
Suite **593 → 601** (+8), all `[m3 PASS] [m4 PASS]`, zero FAIL either mode. Smokes:
`slice_range_mid/_head/_sum/_single/_exclusive/_var_bounds` +
`slice_of_materialized_range` (proves it composes with the prior rung:
`my @r = 10..20; @r[2..5]` → "12,13,14,15") + `slice_scalar_index_unaffected`
(proves `@a[2]` still returns the scalar `3`).

Peers unchanged: **Icon 14/14** both modes, **SNOBOL4 7/7**. Conflicts **90 s/r 9 r/r
— zero delta** (semantic-action-only change). Lang-blind gate GREEN. Generated files
reproduce byte-for-byte (bison 3.8.2 / flex 2.6.4); `raku.lex.c` untouched.
Template-purity + concurrency audit rc=1 **pre-existing** (bb_call*.cpp + other-goal
doc anchors — not in this session's diff). No `.s` regen (no SNOBOL4/Icon codegen).

### Deferred
- `@a[*-1]` end-relative index (WhateverStar in subscript — parse error; its own rung).
- Multi-element list subscript `@a[0,2,4]` (comma slice — separate from range slice).
- Negative range endpoints, hash slices `%h{'a','b'}`, adverbial `:exists`/`:delete`.

---

## PART 2 — INVESTIGATED, NOT LANDED: float trailing-dot (`say sqrt(16)` → `4.`)

### Why it is NOT a simple isolated sink (the cursor called it "a formatting sink")
`say $real` / `print $real` route through `out_write_descr` (by_name_dispatch.c:4746),
whose real branch calls the **shared** `real_str` (string_ops.c:87) — explicitly the
"One real->string authority for the whole runtime: SPITBOL standard representation."
That function renders whole-valued doubles as `4.` (trailing dot, no zero) BY DESIGN:
it is SPITBOL-faithful, and SNOBOL4/Snocone/Icon/Prolog output + the SPITBOL/CSNOBOL4
crosscheck oracles all depend on it. `real_str` MUST NOT be changed for Raku's sake.

The Raku-only stringifier `rtos` (→ `gcvt(r,14)`, also leaves a trailing dot) is NOT
on the `say` path — it is reached only via `to_cstring` for Raku string METHODS
(`.Str`, `.gist`, interpolation). Patching `rtos` alone does nothing for `say` (proven:
edited it, rebuilt, `say sqrt(16)` still printed `4.`).

### The blocker
`out_write_descr` is the shared write sink; the `DT_R` value carries no language tag,
and the `use_gist` param threaded to it is actually the newline flag (`write` nl=1 =
both Raku `say` AND SNOBOL4 `OUTPUT`), so it does not distinguish languages. Per the
NO-LANGUAGE-IDENTITY-GLOBAL FACT RULE, a runtime language flag reachable downstream is
banned. So making Raku reals dotless on `say` without regressing SPITBOL peers needs
EITHER a language-routed write path (Raku `say`/`print` lowering to a Raku-specific
write builtin that formats reals the Raku way) OR a value-level Num/SPITBOL-real
distinction. Both are real design work, not a one-line sink fix.

### Recommendation for a future session
Make the Raku lowerer route `say`/`print` to a Raku write entry that formats `DT_R`
via a Raku formatter (dotless whole, shortest round-trip fractional, `Inf`/`-Inf`/`NaN`
spelling) while all non-Raku frontends keep `real_str`. This is a lowerer + one new
runtime function; it does NOT touch `real_str` or `out_write_descr`'s peer callers.
Scope it as its own rung with SNOBOL4/Icon/Prolog real-output smokes as the guardrail.

## Touched (Part 1 only — Part 2 changes were reverted)
- **SCRIP:** `src/parser/raku/raku.y` (+`rk_arr_index`, wired into subscript
  production), `src/parser/raku/raku.tab.c`/`raku.tab.h` (bison regen),
  `src/runtime/by_name_dispatch.c` (+`__rk_arr_slice` fold + registration),
  `scripts/test_smoke_raku.sh` (+8 smokes).
- **.github:** `GOAL-RAKU-BB.md` LIVE CURSOR + this finding.
