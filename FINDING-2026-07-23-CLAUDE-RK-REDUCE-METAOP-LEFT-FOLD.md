# FINDING 2026-07-23 — Raku RAKU-100: reduction metaoperator `[OP]` (left-fold prefix listop)

## Rung
RAKU-100 recommended next-rung (c): reduction metaops `[+]`/`[*]` — "pure grammar rung." Verified
genuinely OPEN (grammar: 0 productions; smokes: 0; runtime: no reducer). Recommendation (b)
`my sub`/`my constant` was STALE — already landed s2026-07-19b (18 smokes, `KW_CONSTANT` present).

## Canonical semantics (Rakudo `src/core.c/metaops.rakumod`, `METAOP_REDUCE_LEFT(\op)`, lines 258-317)
For a binary left-associative infix op (`op.count == 2`, the `!!` branch, 298-316):
1. EMPTY list  → `op.()`   = the operator IDENTITY.
2. ONE element → `op.($x)` = that element, UNCHANGED (no coercion).
3. TWO+        → strict left fold `op(...op(op(a,b),c)...)`.

Spec-canonical identities (the `op.()` value): `[+]()`→`0`, `[*]()`→`1`, `[~]()`→`""`,
`[-]()`→`0`, `[min]()`/`[max]()`→ (empty → identity is `+Inf`/`-Inf` in Rakudo; we return the
Raku failure-avoidant `Nil`/empty-string sentinel used by the sibling `.min`/`.max` — see NOTE).
No live `raku`/`rakudo` binary is present in the sandbox, so the assertion oracle is the extracted
spec semantics + the smokes themselves (same oracle discipline the other RAKU-100 rungs use).

## Representation reality (this codebase)
Lists/arrays are `SOH`(`\x01`)-delimited strings (RK-OO-A3 note). Therefore:
- empty list  = the empty string `""` (no SOH).
- one element = a bare value string (no SOH) — INDISTINGUISHABLE from a scalar, which is exactly
  the Raku result we want (`[+] 5` == `5`).
- N elements  = `v1 \x01 v2 \x01 ... \x01 vN`.
The existing `.sum` fold (`by_name_dispatch.c:2966`) and `__rk_arr_min/max` (2918) are the structural
templates: `to_cstring` → walk segments split on `SOH` → fold. This rung generalizes that with the
operator and the empty-list identity varying.

## Three-layer implementation
- LEXER (`raku.l`): dedicated rules for the whole 3+char sequence `[+]`,`[-]`,`[*]`,`[~]`,`[min]`,
  `[max]` → one `OP_REDUCE` token carrying a canonical op tag (`"+" "-" "*" "~" "min" "max"`).
  Placed BEFORE the single-char `"["`→`'['` rule (line 162); flex longest-match makes `[+]` win
  over `[` + ... so ZERO conflict with array subscripting `@a[0]`.
- GRAMMAR (`raku.y`): `postfix_expr: OP_REDUCE postfix_expr` → `make_call("__rk_reduce_<op>")` with the
  list expr as the single child. Reuses the existing `make_call`/`expr_add_child` idiom (e.g. line
  154/371). No new precedence tier needed — `[OP] @a` binds like a prefix call over its operand.
- RUNTIME (`by_name_dispatch.c`): `__rk_reduce_add/sub/mul/cat/min/max` folds; registered in
  `rt_builtin_is_known` (line 261 list) so mode-4 emits the `@PLT` call. Numeric ops promote
  int→real on any real segment (mirrors `.sum`). `~` concatenates as strings. Empty→identity.

## NOTE (min/max empty-list)
True Rakudo `[min]()`/`[max]()` return `Inf`/`-Inf`. This codebase has no Inf literal surfaced in Raku
output yet, and the sibling `.min`/`.max` already return `Nil` on empty. For consistency with the
existing surface, `__rk_reduce_min/max` on empty return the same `Nil` sentinel `.min`/`.max` use.
Documented divergence from stock Rakudo, scoped to the unreachable empty-list corner; the `[+]/[*]/[~]`
identities (the common cases) ARE exact. Flagged for a future Inf-surface rung.

## PRE-EXISTING ORTHOGONAL GAP FOUND (NOT this rung — do not fix here)
`[+] 1..5` returns `1`, NOT `15`. Root cause is NOT the reducer: value-position range→array
materialization is broken independently. MEASURED on clean HEAD behavior:
- `my @a = 1..5; say @a.elems;` → `1`  (range stored as ONE opaque element, not expanded)
- `(1..5).sum` → `1`, `@a.sum` → `1`  (the sibling `.sum` gives the SAME wrong answer on the SAME input)
- `for 1..5 {...}` → correct (the CONTROL-FLOW path DOES expand the range; only the VALUE/assignment
  path does not).
So `[+]`/`[*]`/etc. on a range behave IDENTICALLY to `.sum`/`.min` on a range — the reducer is correct
for the list model as it actually exists; the range is simply not a multi-element list yet in value
position. Fixing range materialization is its own rung and would repair `.elems`/`.sum`/`.min`/`[+]`
all at once. Smokes here therefore use explicit comma-lists and array vars (which materialize
correctly); a range smoke is deliberately EXCLUDED and this gap is flagged for a "value-position range
materialization" rung.

Also observed (again NOT this rung): `[+] (1.5,2,0.5)` sums to `4.0` correctly but prints `4.`
(trailing-dot float formatting) — that is the separate known next-rung (a), untouched here.

## SUPPORTED OPERAND FORMS + one grammar-precedence limitation
WORKS (all m3+m4 verified): `[+] @arr` (array var), `[+] (1,2,3,4)` (parenthesized list),
`[+] ()` (empty), `[+] 5` (single term), `my $s = [+] @arr` (assignment position), `([+] @a)+([+] @b)`
(composition). The reduction operand is a `unary_expr`, so a parenthesized list or an array var is
captured whole — the dominant real-world / roast idiom.
LIMITATION (documented, not a reducer bug): the BARE unparenthesized `say [+] 1, 2, 3, 4` misparses,
because `say` has its OWN statement-level `KW_SAY expr ',' arg_list` comma productions, so it binds as
`say( ([+] 1), 2, 3, 4 )` → the reducer sees only `1`. This is a `say`/comma-precedence interaction,
NOT the reduction fold. Fixing it means teaching the reduction operand to swallow a looser-than-comma
list, which would perturb `say`'s statement grammar and risk the 566-test baseline — deferred as its
own precedence rung. Idiomatic `[+] (…)` / `[+] @a` are unaffected. Smokes use those forms.

## Both-mode discipline
Every smoke asserted under m3 (`--run`) AND m4 (`--compile` → as → gcc -no-pie -lscrip_rt). No number
reported from one mode alone (TESTING DIRECTIVE).
