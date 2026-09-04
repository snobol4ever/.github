# FINDING: parenthesized comma-groups silently dropped Icon's "mutual evaluation" failure semantics

**Task:** `icon-arizona-suite-49-reds-censused-by-class-and-cured` (hq_B lane). **Trigger:** chasing
`tprintf` (named "cheapest untouched lead" by three consecutive prior sessions on this row).

## The bug

Icon defines `(e1, e2, ..., en)` as equivalent to `e1 & e2 & ... & en`: each must succeed in turn,
the value is the last one, and a failure anywhere aborts the whole group ("mutual evaluation").
SCRIP's parser instead built the same AST node (`TT_SEQ_EXPR`) for this construct that it uses for
its own semicolon-sequencing dialect extension `(e1; e2; ...)` — a genuinely different, SCRIP-only
construct (confirmed: real `icont` rejects `;` inside parens outright, `"missing right parenthesis"`)
whose intended semantics are unconditional sequencing, no failure propagation. `TT_SEQ_EXPR`'s own
lowering (`lower_icon.c` ~line 671) wires a failing element's β (failure) target to the *next*
element's entry instead of the true outer ω — correct for `;`, silently wrong for `,`.

Minimal repro (`icon_parse.c`/`lower_icon.c`, verified against `/home/resources/icon-master/bin/icont`):

```
x := "unchanged"; x := (1 = 2, "z"); write(image(x))
```

Real Icon and SCRIP now both print `"unchanged"` (the assignment's RHS fails since `1 = 2` fails,
so the assignment never happens, `x` keeps its old value). **Before this fix SCRIP printed `"z"`** —
it evaluated and returned the second element regardless of whether the first one succeeded, exactly
matching a plain C-style comma operator instead of Icon's own defined semantics. Isolated with three
progressively narrower repros (`(1=2, "z")` bare vs `(1=2) || "b"` vs `(1=2) & "z"`): explicit `&`
correctly propagates failure (`TT_CONJ`'s existing lowering is fine and was left untouched); the bare
comma form did not.

## The fix

One line, `icon_parse.c`'s comma-branch of the parenthesized-expression parser: build `TT_CONJ`
instead of `TT_SEQ_EXPR` for the comma-separated form. `&`'s own parser (`parse_and`) already builds
a flat N-ary `TT_CONJ` from exactly this shape (a base expression plus `push_child` in a loop), so
this reuses an already-correct, already-tested lowering path rather than adding one. `TT_SEQ_EXPR` is
shared with Pascal and Raku, but each language's parser feeds its own separate lowerer file (`lower_
pascal.c`, `lower_raku.c`) — Icon's parser only ever feeds `lower_icon.c`, so this change cannot reach
either other language. SCRIP `c3aa5bc8`.

## How it was found

Root-caused via `tprintf.icn` (`corpus/packages/icon/arizona_tests/general/`), whose linked `printf.
icn` library implementation uses exactly this idiom to conditionally prepend a sign: `wholepart :=
(signpart == "-", "-") || wholepart`. On real Icon, when `signpart` isn't `"-"`, the whole right-hand
side fails and the assignment is a no-op, leaving `wholepart` unsigned. SCRIP instead evaluated the
comma group unconditionally, so **every value's `%e`-formatted column got a spurious leading `-`**,
including zero and positive numbers — a maximally visible, 100%-reproducible symptom across the
suite's entire ~315-line output table, which is what made it findable at all (session after session
had flagged `tprintf` as "cheapest, untouched" without anyone actually diffing its output).

## Verification (no regression; blast radius as expected)

- Icon smoke: 15/15 both modes, unchanged.
- Icon STRICT rung suite: `PASS=73 FAIL=7 BADEXIT=1 XFAIL=24 MISSING=2 TOTAL=105` all three modes —
  byte-identical to the pre-fix baseline this task's own DONE-WHEN was re-cut to earlier the same day.
- Icon master board: **green and improved** (599/599 both modes, watermark 596→599) — but this
  measurement landed on a tree that also carried an unrelated concurrent commit
  (`0d482dac`, bounded self-recursive generators as the default); not attributed to this fix without
  isolating it, see below.
- `strip_comments.py --check`: clean, 0/383 flagged.
- `make test` (SNOBOL4 gate): unaffected as expected — this fix is scoped to `icon_parse.c`, which no
  other frontend's parser can reach — `PASS=1698 FAIL=0` both modes, confirms the blanket per-push
  gate rather than anything this change could plausibly have broken.

## Effect on THIS row's own board — smaller than hoped, and honestly attributed

`tprintf.icn` itself does **not** reach a full byte-exact PASS: the sign-corruption is completely
gone (confirmed directly, diff shrank from ~315 wrong lines to a handful), but two *other*,
independent, pre-existing issues remain — a `%16s` field-width padding gap on certain strings (not
yet investigated, may be its own small bug) and the already-known, already-minted arbitrary-precision
integer gap (`icon-arizona-class-bignum-not-implemented`) on `6.02e+23`'s integer/octal/hex columns.
Same pattern as every prior session on this row: a real, verified fix that measurably shrinks a
diff without completing it.

The Arizona board's own `m3_pass`/`m4_pass` moved 43→44 in the same sitting this fix landed, but
**that flip (`btrees`) is not this fix** — confirmed directly: `btrees.icn` contains no bare
parenthesized comma-conjunction expression at all (only ordinary comma-separated function-call
argument lists, a syntactically unrelated construct), and it was previously filed under the
generator-forward-reference-reservation class, which is exactly what the concurrent `0d482dac`
landing (self-recursive generators as the default) targets. Recording this fix's own contribution
honestly as: one real, oracle-verified, general-purpose language-conformance bug fixed, zero
Arizona-suite full-PASS flips of its own, in case a future session tries to attribute the 43→44 delta
to the wrong commit.

## Not investigated further this session

A pattern-based sweep (bare `(x, y)` shapes, common call-forms excluded by name) across all 39 other
current FAIL sources found zero candidate lines — weak evidence (a heuristic grep, not a semantic
one; could miss a differently-shaped instance) but consistent with this bug's blast radius inside
THIS suite being fully captured by `tprintf` alone. tprintf's own remaining `%16s` width gap is
untouched and may be a small, separate, quick lead — its own diff is now much shorter and easier to
read than before this fix.
