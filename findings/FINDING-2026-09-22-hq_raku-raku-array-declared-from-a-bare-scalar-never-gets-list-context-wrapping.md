# FINDING 2026-09-22 hq_raku — `my @arr = <scalar>` never gets list-context wrapping (elems falls back to a stringify+strlen guess)

**Not fixed this sitting — named rather than patched, because the correct fix touches array-assignment
lowering used everywhere, and the risk of regressing some of the 866 currently-passing RakM entries under
session time pressure outweighs landing it without full exploration.**

**Symptom, measured (drives the `scrip_test_rk_given18` RakM master FAIL):**

```raku
my @vals = '';        # should seed a 1-element array: ('',)
push(@vals, 1); push(@vals, 2); push(@vals, 3); push(@vals, 4);
for @vals -> $v { ... }   # oracle: 5 iterations ('', 1, 2, 3, 4); SCRIP: 4 (the '' is gone)
```

Isolated further:
```raku
my @a = 'x';  say @a.elems;   # 1  (looks right)
my @b = 0;    say @b.elems;   # 1  (looks right)
my @c = "";   say @c.elems;   # 0  (WRONG -- oracle says 1)
```

**Root cause, found via `--dump-ir`:** an array declared from a parenthesized list literal
(`my @d = (1,2,3);`) lowers RHS through a `CALL_BUILTIN "__rk_arr"` wrapper *before* the `ASSIGN` box --
the parser recognizes the `(...)` syntax and emits that wrapping call directly (grep confirms `__rk_arr` is
never referenced in `lower_raku.c` at all; it is purely a parser-level artifact of the paren-list
production). A bare scalar RHS (`my @c = "";`, `my @c = 'x';`, `my @c = 0;`) gets **no such wrapping at any
stage** -- the lowered IR is a plain `ASSIGN [LIT_STRING ""] var="@c"`, identical in shape to a scalar
assignment. `@c` ends up holding the raw scalar DESCR, never a real array/list aggregate.

Given that, `.elems` (and presumably other Positional operations) must be falling back to *something* for a
non-array DESCR rather than refusing -- and the fallback is consistent with "coerce to string, take
`strlen`": `'x'.elems -> strlen("x")=1` (right by coincidence), `0.elems -> strlen("0")=1` (right by
coincidence, since `(0).Str` is `"0"`), `''.elems -> strlen("")=0` (visibly wrong, and the only one of the
three whose *string form* has length != 1). This was not traced further (the `meth_call "elems"` dispatch
site was not located this sitting) -- the fallback's exact location is the next step, but it is very
unlikely to be the right fix on its own: even if `.elems` on a bare scalar were corrected to always answer
`1`, `push`/`for`/every other Positional op would still be operating on a bare scalar rather than a real
array, and each would need its own correct-by-luck-or-not fallback audited individually. **The general fix
belongs at assignment time, not scattered across every consumer.**

**Where the real fix belongs, and why it is NOT a one-line change:** Raku list-context coercion --
assigning a non-Iterable scalar to a `@`-sigil target should behave as if wrapped in `__rk_arr`, exactly as
the `(...)` literal path already does; assigning an actual Iterable/Positional (another array, a list-
returning call) must NOT be double-wrapped, or `my @b = @a;` turns into a 1-element array containing `@a`
as a single nested item. The decision needs to inspect the RHS's *shape* (or ultimately its runtime type)
at the `TT_ASSIGN` site (`src/lower/lower_raku.c:356`, the `t->c[0]->t == TT_VAR` arm) and possibly the
`TT_DECL` site (`:374`) if `my @x = ...;` ever routes through that arm instead (this sitting only confirmed
the `TT_ASSIGN` arm is what a bare `my @c = "";` actually uses). Getting the RHS-shape test right (literal /
scalar var / call-returning-list / already-array) without breaking `my @b = @a;`, `my @c = some_list_sub();`,
`my @d = %h.values;`, etc. is real design work, not a mechanical patch -- and RakM has 929 entries covering
many of those shapes already passing, so a wrong cut here risks a wide regression that would not show up
until the full board re-runs.

**Suggested approach for whoever picks this up:** find every currently-passing RakM/ladder/smoke entry of
the shape `my @X = <non-paren-RHS>;` first (a grep over `ALL.raku` for `my @\w+ = ` excluding lines whose
RHS starts with `(`), read what each RHS actually is (var/call/literal), and use that as the test matrix
*before* changing `TT_ASSIGN`'s lowering -- exactly the ASM-DIFF-FIRST discipline the repo already mandates,
applied to IR shape rather than assembly, since the passing/failing line here is architectural rather than
per-instruction.
