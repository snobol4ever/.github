# HANDOFF — 2026-05-29 — Opus 4.8 — RAKU-BB RK-BB-5.0..5.3 (Seq consumers + array literal)

**Goal:** GOAL-RAKU-BB.md
**Repos touched:** SCRIP (code), .github (docs). corpus unchanged.
**HEAD SCRIP:** `36e41ed6`

## Summary

Landed RK-BB-5.0..5.3: the list/array **Seq-consumer** cluster plus the **comma-list
array initializer**. Five commits, each green and regression-free.

| Commit | Rung | What | m2 | m4 |
|---|---|---|---|---|
| `a4bc02d4` | 5.0 | `reverse` | 28→29 | 29→30 |
| `8b10f978` | 5.1 | `unique` + `sum` | 29→30 | 30→31 |
| `ed321adc` | 5.2 | `join` | 30→31 | 31→32 |
| `f9425b68` | 5.x | array-arg coverage (test-only) | 31→32 | 32→33 |
| `36e41ed6` | 5.3 | comma-list array init `my @a=1,2,3` | 32→33 | 33→34 |

**Net: GATE-RK mode-2 28→33/40, GATE-RK4 mode-4 29→34/40.**

## Design

All consumers are **pure value helpers** in `src/runtime/interp/raku_builtins_byname.c`,
added to `raku_try_call_builtin_by_name` (the non-mutating dispatcher reachable from BOTH
mode-2 `sm_interp.c` SM_CALL_FN AND mode-4 `rt.c` rt_call). They:
- flatten every arg into an element vector (a single SOH-array arg splits into its segments;
  a scalar is one element), modelled on the existing `elems`/`arr_get`/junction code;
- emit **no x86 bytes** → FACT-clean by construction (the FACT rule governs emitted opcodes,
  not C value helpers);
- touch **no BB/SM/XA template** and **no lowering** (5.0–5.2);
- produce **byte-identical** output in mode-2 and mode-4 (verified per test).

Semantics:
- `reverse(LIST/@arr)` — reverse element order. `for reverse(...) -> $i` rides the **existing**
  `for CALL(...) -> $v` materialization branch (lower.c ~1693): the call result (an SOH-array
  string) is stored to a temp and iterated via `lower_raku_iterate_arr`. No new lowering.
- `unique(LIST/@arr)` — dedup preserving first occurrence (exact string match).
- `sum(LIST/@arr)` — numeric fold; INTVAL when every element parses as a full integer, else REALVAL.
- `join(SEP, LIST/@arr)` — args[0] is the separator; args[1..] flattened and joined. Composes:
  `join(",", reverse(1,2,3))` → `3,2,1`.

### 5.3 — comma-list array initializer (the grammar bit)

**Diagnostic that drove this:** `reverse(@a)`/`sum(@a)`/etc. were NEVER blocked by a parser gap —
they work fine on push-built `@arrays` (proven by the 5.x test-only commit). The actual gap was the
**initializer** `my @a = 1,2,3` (comma list), which simply had no production.

Fix: two `raku.y` productions (untyped + typed), each accepting
`KW_MY [IDENT] VAR_ARRAY '=' expr ',' arg_list ';'` and building
`ASSIGN(@a, __rk_arr(expr, arg_list...))`. The single-element rule `... '=' expr ';'` is unchanged;
after parsing the RHS `expr`, lookahead `;` reduces to the single rule and lookahead `,` shifts into
the comma-list rule — a **clean LALR distinction** → **net-zero new shift/reduce conflicts (still 30)**.

`make_call("__rk_arr")` adds a name-dup `c[0]` (lowering skips it), so the new `__rk_arr` builtin
receives `args[]` = the elements and packs them into an **in-order** SOH-array (it's `reverse` minus
the reversal). `my @a = (1,2,3)` (parenthesized) was deliberately NOT attempted — a list-atom is more
conflict-prone; bare comma-list first.

**Parser regen:** `cd src/frontend/raku && bison -d --warnings=none -Wno-yacc -o raku.tab.c raku.y`
(the recipe in `scripts/regenerate_parser_and_lexer_from_sources.sh`; bison 3.8.2). raku.l untouched
(no new tokens), so no flex regen.

## New tests (test/raku/)

rk_reverse, rk_unique_sum, rk_join, rk_seq_consumers_arr, rk_array_literal — all with `.expected`;
all pass mode-2 (`test_raku_ir_rungs.sh`) and mode-4 (`test_raku_mode4_rung.sh`) byte-identically.

## Gates (all verified at `36e41ed6`)

```
GATE-RK   mode-2:   33/40   (FAIL 7)
GATE-RK4  mode-4:   34/40   (FAIL 6 = deferred regex cluster, unchanged)
smoke raku/icon/prolog/snobol4/snocone: 5/5/5/13/5  HOLD
bison s/r conflicts: 30 (unchanged)
FACT grep (seg_byte/SL_B/sl_emit_one/emit_standard_blob outside templates): 0
build: clean
```

## NEXT — RK-BB-5.4..N

In rough order of leverage:
- **(a)** `.method(N)` parsing — `@a.tail(2)`, `@a.head(N)`, `@a.reverse`. Unblocks the method-form
  consumers the goal explicitly names (`tail`/`head`). The gap is method-call-with-args; the runtime
  builtins for tail/head are trivial once the AST arrives.
- **(b)** parenthesized array literal `my @a = (1,2,3)` — needs a list-atom; weigh conflict cost.
- **(c)** `zip`/`cross` multi-Seq drivers — each output element is itself a list, so this needs a
  **nested-tuple representation** (e.g. STX-within-SOH, like the hash encoding) plus consumer support
  for tuple-valued loop vars. The goal groups these as "(later)"; it is the substantial item.

## Notes / caveats

- `say @a` (bare array, no parens) still parse-errors — separate `say`-of-bare-array gap, unrelated.
- `say reverse(1,2,3)` prints the raw SOH-array (same as any array value reaching `say`); tests use the
  `for ...` / assign-then-iterate idioms instead, which render per-element.
- `min`/`max`/`sort`/`elems` already existed (min/max via the Icon by-name chain).

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
