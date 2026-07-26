# FINDING-2026-07-25-CLAUDE-RK-SUBSCRIPT-TAILS-AND-LIST-ASSIGN.md

**Goal:** GOAL-RAKU-BB (RAKU-100 coverage arc) · **Session:** s2026-07-25 · Claude Opus 5
**Watermark:** m3 601/0 → **633/0**, m4 601/0 → **633/0** (+32 smokes). Peers unchanged: Icon 14/14, SNOBOL4 7/7.
**Four rungs, four commits:** `38182ea0`, `64b2573a`, `fa6171cb`, `9e873067`.
**Conflicts:** 90 s/r / 9 r/r → **92 s/r / 9 r/r** (+2 s/r total, both attributed below; r/r FLAT).

---

## RUNG 1 — Whatever-star end-relative subscript `@a[*-N]` (`38182ea0`, +10 smokes)

**Canonical source read first.** `src/core.c/WhateverCode.rakumod:17` — `POSITIONS` calls the WhateverCode
with `list.elems`; `src/core.c/array_slice.rakumod:145` then does `SELF.AT-POS(pos)`. So the whole
construct reduces to ONE fact: **`*` in subscript position IS `.elems`**, and the surrounding arithmetic
is applied to it. Nothing about `*-1` is special-cased in Rakudo — it is generic WhateverCode application.

**Consequence for the implementation: this is a PURE GRAMMAR rung.** Because `.elems` already exists as a
proven `TT_METHCALL` node, `rk_arr_end_index` builds
`TT_ARR_GET(arr, BINOP(op, TT_METHCALL(arr,"elems"), off))` — reusing the existing arithmetic and
method-call paths end to end. **ZERO new runtime code, ZERO new AST kinds, ZERO new IR opcodes, ZERO new
x86 encoders, ZERO BB templates.** Generality falls out for free: `@a[*-1]`, `@a[*-2]`, `@a[*-$n]`,
`@a[*-(1+2)]` all work because the offset slot is a full `expr`.

**Conflicts: ZERO delta** (90/9 → 90/9). No `expr` in the grammar can begin with `'*'` (it is infix-only),
so `VAR_ARRAY '[' '*' …` is unambiguous on one token of lookahead.

### ⚠ NAMED BLOCKER — bare `@a[*]` is LEXICALLY AMBIGUOUS, do NOT redo naively
`raku.l:164` already owns `"[*]"` as the reduction-metaop token `OP_REDUCE` (the `[*]` product fold).
Flex longest-match therefore lexes `@a[*]` as `VAR_ARRAY OP_REDUCE` — the whole-list slice is
**unreachable from the grammar**, no matter what productions are added. This is a genuine lexical
collision between two real Raku constructs (`[*] @a` reduce vs `@a[*]` whole slice), NOT an oversight.
Resolving it needs lexer context (a start condition, or previous-token state, so `[*]` after a
`VAR_ARRAY` lexes as three tokens) — its own rung, with the `[*] @a` reduce smokes as the guard.
`@a[*-1]` is SAFE and unaffected: `"[*]"` requires a literal `]` in third position.

### ⚠ PRE-EXISTING, MEASURED, NOT INTRODUCED HERE — out-of-range read unwinds
`@a[*+0]` (index == elems) prints nothing and **silently terminates the enclosing statement sequence**.
Proven pre-existing by falsification on clean HEAD: **plain `@a[3]` on a 3-element array does exactly the
same thing** — so this is `arr_get` returning `FAILDESCR`, which rides the four-port ω spine outward and
unwinds, entirely independent of the Whatever star. Raku's semantics are `Nil`/`(Any)` for a read past the
end (an Array read past end is undefined, not a failure) and a *throw* for a negative index. The fix shape
is ALREADY IN THE TREE and named: `__rk_arr_at` (`by_name_dispatch.c`, minted for the s2026-07-22c
destructuring rung) is `arr_get` except it returns `NULVCL` instead of `FAILDESCR` for exactly this reason.
Its own rung — routing `arr_get` reads to Nil semantics touches every Raku subscript and wants peer guards.

---

## RUNG 2 — comma multi-element subscript `@a[i,j,k]` (`64b2573a`, +9 smokes)

Canonical: `array_slice.rakumod:117`, the `Iterable:D \positions` arm — positions are consumed **in the
order given**, so `@a[2,0]` is `(30,10)`, not sorted, and repeats are honored (`@a[0,0,0]`).

Grammar helper `rk_arr_pick` + new variadic runtime fold `__rk_arr_pick` in `by_name_dispatch.c`,
mirroring the `__rk_arr_slice` SOH-walk idiom (NO-DUP-LOGIC), registered in `rt_builtin_is_known` so
mode-4 emits the `@PLT` call. Out-of-range positions contribute an empty element (the SOH representation's
nearest thing to `Nil`) rather than failing the whole slice.

**Conflicts: ZERO delta** (90/9 held). Runtime `.c` touched → rebuilt BOTH `scrip` and `libscrip_rt` per
the goal file's KEY GOTCHA, and re-ran the peer gates against the fresh runtime.

---

## RUNG 3 — bare whole-array reassignment `@a = LIST` (`fa6171cb`, +7 smokes)

There was **no `VAR_ARRAY '=' …` statement production at all** — only the four `KW_MY` forms. So
`@a = 4,5,6;` and even `@a = 9;` were hard parse errors after the declaration.

Canonical: `Array.rakumod` `STORE` — the `Iterable:D` arm builds a **fresh** `IterationBuffer` (assignment
REPLACES, never appends) and the `Mu \item` arm pushes exactly one element (so `@a = 9` is a 1-element
array). Implemented by mirroring the four proven `my`-forms minus `KW_MY`: plain `expr` (via `rk_arr_rhs`,
so ranges materialize), bare comma list, `xx` repetition, and parenthesized list.

### The +1 s/r conflict, characterized honestly
`-Wcounterexamples` **OOM-killed** in this container (tool limitation — recorded, not skipped). Three
substitute lines of evidence, in descending strength:
1. **Behavioral, on the exact ambiguous shape.** The conflict governs `VAR_ARRAY '=' . '('` — paren-LIST
   form vs an `expr` that merely starts with `(`. Verified: `@b = (1+2)` yields **elems 1** (parenthesized
   expression) while `@a = (7,8,9)` yields 3 — i.e. the default shift resolves CORRECTLY on both sides.
2. **No new conflict KIND.** The multiset of conflicting rule shapes extracted from `bison --report=all`
   is byte-identical to the pre-edit baseline's; the +1 is the same pre-existing dangling-expr family
   appearing in one additional state because `VAR_ARRAY`'s statement-start item set grew.
3. **Regression net.** Full suite 627/627 both modes, peers unchanged.

---

## RUNG 4 — trailing comma in lists, calls and subscripts (`9e873067`, +6 smokes)

`my @a = 1,2,3,;` / `(4,5,6,)` / `f(3,4,)` / `@c[0,2,]` were all parse errors. **ONE production** —
`arg_list: arg_list ','` — fixes every one of them at once, because `arg_list` is the shared list
nonterminal behind declarations, parenthesized lists, call arguments and (since rung 2) subscripts.
Trailing comma correctly does NOT add an element (`elems` == 3 for `1,2,3,`).

### ⚠ DROPPED ON CONFLICT DISCIPLINE — do not re-add without a cheaper factoring
Four further productions for the **single-element** trailing-comma list (`my @a = 42,;`, `@a = 42,;`,
`my @a = (42,);`, `@a = (42,);`) were written, built and measured, then **REVERTED**: they cost **+2 s/r**
that I could not characterize, and they buy essentially nothing — `my @a = 42,;` is semantically
IDENTICAL to `my @a = 42;`, which already produces a 1-element array (verified). Isolation measurement,
so the next session need not redo it:

| Variant | s/r | r/r |
|---|---|---|
| HEAD (after rung 3) | 91 | 9 |
| `arg_list ','` ONLY | **92** | 9 |
| + the four single-element forms | 94 | 9 |

**KEPT the +1** (`arg_list ','` — textbook list-trailing-separator conflict: shift when an `expr` follows,
reduce when `)`/`;`/`]` follows; those tokens cannot begin an `expr`, so the default resolution is the
only correct one). **DROPPED the +2.** Same discipline the s2026-07-22c session applied to the `++`/`--`
+2 r/r: uncharacterized conflict growth is reverted, not committed with a shrug.

---

## Gate/audit state at handoff

- Raku smokes **633/0 mode-3, 633/0 mode-4**; Icon **14/14**; SNOBOL4 **7/7**.
- Lang-blind gate (`test_gate_emit_no_lang.sh`) **GREEN**.
- Template-purity + concurrency audits at their **documented pre-existing baseline** — proven not-mine by
  `git diff --stat HEAD`: this session's diff touches only `src/parser/raku/raku.{y,tab.c,tab.h}`,
  `src/runtime/by_name_dispatch.c` and `scripts/test_smoke_raku.sh`. **Zero emitter, zero template files.**
- Toolchain provenance established BEFORE the first edit: bison 3.8.2 reproduced the committed
  `raku.tab.c` **byte-for-byte** from HEAD's `raku.y`. `raku.lex.c` untouched all session (no lexer edit).
- All builds `-O0` per the O0-DEV FACT RULE (`grep -c -O2` on the runtime build log == 0).
- No `.s` artifact regen: zero Raku `.s` in tree; no SNOBOL4/Icon codegen touched.

## NEXT RUNG (RAKU-100) — empirically probed on this session's HEAD, not inherited prose

(a) `@a[*]` whole-list slice — **blocked**, needs the lexer disambiguation named in rung 1.
(b) `arr_get` out-of-range → Nil instead of FAILDESCR (the `__rk_arr_at` shape) — unblocks `@a[*+N]`,
    past-the-end reads, and removes a silent-unwind class. Peer-guarded rung.
(c) single-element trailing-comma list — needs a conflict-free factoring (see the table above).
(d) `.map`/`.grep` as methods — still `[SMX]`-declined (native map/grep BB family; genuine codegen).
(e) `given`/`when` — same `[SMX]` box gap.
(f) `...` sequence operator (313 roast files; multi-session).
(g) RK-GRAM-3 native recursive-descent grammar engine — standing lead, fresh full-budget session.
