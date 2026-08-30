# FINDING 2026-08-30 seat07 — Raku `map`/`grep` parse correctly but generate ZERO code, either mode; `rc-perfect-shuffle`'s `flat` gap is necessary but nowhere near sufficient

## Context

Row `raku-frontend-real-world-syntax-gaps`, picked up at pass 31 to look at `rc-perfect-shuffle`'s
remaining line-5 gap (`flat map { @deck[$_, $_ + $mid] }, 0..($mid - 1)`), which the row's own pass
28-30 history calls "the ONLY remaining gap" on that line once the `map`-closure-comma fix (pass 29,
SCRIP `4d50c5d7`) landed. Before implementing `flat` (grammar promotion to a `KW_FLAT` token +
runtime, mirroring the `join`/`take` precedent), checked whether the `map` half of the line actually
*executes* — it does not, in either mode, and never has.

## The measurement

```
$ cat map_simple.raku
my @a = 1,2,3;
my @b = map { $_ + 1 }, @a;
say @b;

$ ./scrip --run map_simple.raku < /dev/null
[SMX] --run: mode-3 native emitter does not yet cover this program
(a box has no MEDIUM_BINARY arm — Raku map/grep). REJECTED — native BB emission pending
(no interpreter fallback).

$ ./scrip --compile --target=x86 -o /dev/null map_simple.raku < /dev/null
[SMX] --compile --target=x86: mode-4 native emitter does not yet cover this program
(a box has no MEDIUM_TEXT arm — Raku map/grep). REJECTED — native BB emission pending
(no interpreter fallback).
```

Both refusal strings are hard-coded in `src/driver/scrip.c` (lines ~1370 and ~1797) — this is a
deliberate, unconditional stub for the whole `map`/`grep` construct class, not a bug that fires on
some unusual input shape. Confirmed on the *simplest possible* case (single-scalar map body, no
slice, no nested structure) — this is not specific to `rc-perfect-shuffle`'s more elaborate
`@deck[$_, $_ + $mid]` slice-returning body.

## Why the row's own history didn't catch this

`test_smoke_raku.sh` (724/724, this row's standing "trustworthy control arm" per multiple passes)
has **zero** occurrences of `KW_MAP` or the literal `map` construct — it has never exercised `map`
at all, execution or otherwise. Pass 29's own "Verified before landing" section for the map-comma
grammar fix checked `/usr/bin/raku`'s output against SCRIP's `--dump-ast` output — i.e. it verified
*parse shape*, never *execution*. That is a completely correct and sufficient verification for what
pass 29 was actually fixing (a grammar ambiguity), but it means nothing in this row's 30-pass history
has ever run a `map` expression to completion, and the row's own "flat is the only remaining gap"
framing for `rc-perfect-shuffle` line 5 is consequently incomplete: `flat` is a real, additional,
independent gap (confirmed separately — no `KW_FLAT` token, no runtime case, see below), but even a
fully-correct `flat` implementation would still be riding on top of a `map` that emits no code at
all. This is the class of thing this file's own house law names directly: *"verify against real
corpus kernels, not a convenient green suite"* — this row's own GOAL line already says this about
the 51/51 crosscheck suite; the same caution turns out to also apply to `test_smoke_raku.sh` for
this specific construct.

## Secondary, smaller findings while investigating `flat` specifically

- `flat(@a)` **with parens already parses fine** via the pre-existing generic
  `IDENT '(' arg_list ')'` production (`flat` is not a keyword, just a bareword `IDENT`) — it fails
  only at runtime, `Error 5 Undefined function or operation`, because `by_name_dispatch.c` has no
  case for it. `flat @a;` **without parens also already parses, but only as a bare statement** — a
  narrow, pre-existing `stmt: IDENT VAR_ARRAY ';'` production (`raku.y:590`) exists for exactly the
  shape "bareword IDENT + one array variable", nothing more general. Neither of these two facts was
  previously recorded; both were assumed to be "no grammar path at all" for the bareword form, which
  is true only for `flat`-as-an-expression, not `flat`-as-a-bare-statement.
- The right shape for `flat`-as-expression, once `map`/`grep` codegen exists to make it worth
  landing, is a `KW_FLAT` token + `call_expr: KW_FLAT expr` production (single-arg, mirroring
  `KW_JOIN`'s multi-arg shape but without the comma-separated tail), reducing through
  `postfix_expr`→`expr` the same way `join`/`take` already do. The runtime primitive it wants,
  `rt_make_flat_agg` (`by_name_dispatch.c:1647`, already used by `__rk_arr`'s array-literal
  flattening), looks like the right building block — not independently verified end-to-end against
  this kernel's exact data shape, since there is no point doing so before `map` itself can run.

## Recommendation, not decided here

`map`/`grep` native BB emission (both media) is real, new codegen infrastructure — a "declared
sub/generator body compiled into a box" problem, not a grammar tweak, and it blocks more than just
this one kernel (`rc-perfect-shuffle` is simply the first place this row's own coverage sweep walked
into it). This is a bigger lift than anything this row has landed in 30 passes and, per this row's
own standing discipline for design-choice-sized work, is flagged rather than started. Whoever owns
BB-codegen-lane decisions (per CLAUDE.md, BB codegen work reads `ARCH-LANGUAGES.md` +
`GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md` first) is better positioned to scope it than a single
raku-frontend pass.
