# HANDOFF — 2026-05-29 — Opus 4.8 — RAKU-BB RK-BB-5.4a + 5.4b (.method forms + paren array literal)

**Goal:** GOAL-RAKU-BB.md
**Repos touched:** SCRIP (code), .github (docs). corpus unchanged.
**HEAD SCRIP:** `56a30122`

## Summary

Landed RK-BB-5.4a (list-method postfix forms) and RK-BB-5.4b (parenthesized array literal).
Three commits, each green and regression-free.

| Commit | Rung | What | m2 | m4 |
|---|---|---|---|---|
| `dbb3d15f` | 5.4a | `.reverse/.unique/.sum/.elems/.head(N)/.tail(N)` postfix | 33→34 | 34→35 |
| `91bfae91` | 5.4a | `for @a.reverse -> $x` materialization | (hold) | (hold) |
| `56a30122` | 5.4b | `my @a = (1,2,3)` parenthesized literal | 34→35 | 35→36 |

**Net: GATE-RK mode-2 33→35/42, GATE-RK4 mode-4 34→36/42.** Two new gated probes
(`rk_listmeth`, `rk_paren_array`), each green in both modes and byte-identical across them.

## Design

### 5.4a — list-method forms (`dbb3d15f`)

The free-function forms `reverse(@a)`/`unique(@a)`/`sum(@a)`/`elems(@a)` already worked (5.0–5.3
value helpers). The gap was the **method** forms:
- `@a.reverse` parses to `TT_FIELD` (object + bare name) → `FIELD_GET` → null for a non-instance.
- `@a.head(2)` parses to `TT_METHCALL` → `raku_mcall`, which only resolves `DT_DATA` class
  instances → FAILDESCR for an SOH-array.

Both currently returned empty (not a crash). Fix is **pure lowering** — route the known
list-method names to the existing value helpers:
- `raku_is_listmeth(m)` whitelist = reverse/unique/sum/elems/head/tail.
- `lower.c` `TT_METHCALL`: after the class static-resolution `found_count==1` branch fails and
  **before** the `raku_mcall` fallback, if `g_lang==LANG_RAKU && raku_is_listmeth(mname)` →
  lower object (c[0]) + extras (c[2..]) + `SM_CALL_FN mname, 1+nextra`.
- `lower.c` `lower_field` (TT_FIELD): if `g_lang==LANG_RAKU && raku_is_listmeth(fname)` →
  lower object + `SM_CALL_FN fname, 1`, before the `FIELD_GET` path.

New value builtins in `raku_builtins_byname.c` (after `reverse`): **`head`/`tail`** — when
`nargs>=2` the **last** arg is the count N and `args[0..k-1]` is the list; `nargs==1` defaults
N=1. Flatten the list portion (SOH-array args split into segments), slice first/last N, re-SOH-join.
Pure value helpers, **no emitted x86** (FACT-clean), reachable mode-2 `sm_interp` SM_CALL_FN +
mode-4 `rt.c` rt_call → byte-identical.

**Class methods/fields untouched:** the redirect is gated on the list-method whitelist, so
`$obj.field`/`$obj.method(...)` keep FIELD_GET/raku_mcall. `rk_class26` byte-identical both modes.

### 5.4a (cont) — for-loop over a method-form invocant (`91bfae91`)

`for @a.reverse -> $x` ran away (output blew up) because the Raku `for CALL→$v` materialise-then-
iterate guard in `lower_every` keyed only on `gen_expr->c[0]->t == TT_FNC`. Widened it with
`raku_methform_listmeth(e)` (true for `TT_METHCALL`/`TT_FIELD` whose method is a list method).
The materialise body is generic (`lower_expr(c[0])` → store `__arr_N` → `lower_raku_iterate_arr`),
and `lower_expr` already produces an SOH-array for those nodes, so no other change needed.
for-CALL path (rk_fileio38, rk_map_grep_sort24) unaffected.

### 5.4b — parenthesized array literal (`56a30122`)

`my @a = (1,2,3)` failed: `'(' expr ')'` wraps a **single** expr, and `expr` has no comma-list,
so `(1,2,3)` was a parse error.

**Two candidate fixes tried:**
1. General atom `'(' expr ',' arg_list ')'` → `__rk_arr(...)`. Works, but **+2 s/r conflicts**
   (30→32) from interactions with method-chaining (`.`)/hash-subscript (`<...>`) postfix contexts,
   since an atom is reachable from many states. **Reverted.**
2. **Initializer-only** productions (chosen) — two `raku.y` rules (untyped + typed) mirroring the
   5.3 bare comma-list: `KW_MY [IDENT] VAR_ARRAY '=' '(' expr ',' arg_list ')' ';'` →
   `ASSIGN(@a, __rk_arr(expr, arg_list...))`. Restricting to the initializer RHS keeps it
   **NET-ZERO new conflicts (still 30)**. Reuses the existing `__rk_arr` builtin (5.3).

Single-element paren `(7)` stays scalar via the unchanged `'(' expr ')'`; bare comma-list
(`my @a = 1,2,3`) and scalar paren coexist. Parser regenerated:
`cd src/frontend/raku && bison -d --warnings=none -Wno-yacc -o raku.tab.c raku.y` (bison 3.8.2).

## Gates (live, end of session)

```
GATE-RK   mode-2:  35/42   (FAIL 7 = rk_re32/33/34/35/37 + rk_regex23 deferred + rk_stdio39 non-bug)
GATE-RK4  mode-4:  36/42   (FAIL 6 = deferred regex cluster)
Smoke raku/icon/prolog/snobol4/snocone: 5/5/5/13/5  HOLD
bison s/r conflicts: 30 (unchanged)
FACT RULE grep: 0
Build: clean
```

## Deferred / not done

- **`.join` method form** — `@a.join(",")` has the separator as the ARG and the list as the
  INVOCANT, i.e. arg-order swapped vs the `join(SEP, LIST)` free function (which already works).
  Not in the whitelist; do it with a small special-case push-order if a corpus case needs it.
- **for-loop over a method form** materialises but does NOT destructure (`-> $a, $b`) — n/a here.
- **RK-BB-5.4c (`zip`/`cross`)** — the real remaining work. Each output element is itself a list,
  so it needs a **nested-tuple representation** (STX-within-SOH or similar) that `for`/`say`/
  `.elems` consumers understand. NOT a pure value helper; broad blast radius. Design the rep
  first (how `say` renders a tuple, how `.elems` counts the outer list, how `for` binds each
  tuple). Recommend a fresh session with full budget.

## NEXT

RK-BB-5.4c (zip/cross, see above) or the deferred regex cluster under GOAL-RAKU-PAT-BB.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
