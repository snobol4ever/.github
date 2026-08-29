# FINDING: raku `xx` is statement-only, not expression-level — and that, not the `[...]` composer, is what blocks `rc-forest-fire-stringify`

**hq_P · 2026-08-29 · row `raku-frontend-real-world-syntax-gaps`, pass 18 · SCRIP `272fc30f`**

## What was closed

The **square-bracket array-literal composer `[ ... ]`** — pass 17 isolated it and handed it off with a starting
repro (`my @a = [1, 2, 3];` fails to parse). It had **zero** grammar presence: `[` reached the parser only as the
indexing bracket in `VAR_ARRAY '[' expr ']'`.

Shipped as four new `atom` alternatives **mirroring the four `'(' … ')'` list forms sitting immediately below them**
(`raku.y:1800-1806`), each building the same `__rk_arr` call the parenthesized and bare-comma array assignments
already build. **Zero new tokens** (`raku.tab.h` unchanged), **zero lexer change**.

⭐ **One deliberate semantic difference, which is the point of the construct:** `'(' expr ')'` collapses to bare
`$2` (grouping), but `[$x]` is a **one-element array**, so `'[' expr ']'` wraps in `__rk_arr`. Verified:
`my @b = [42]; say @b[0];` → `42`.

## ⭐⭐ The finding: `xx` is not an expression-level operator

`rc-forest-fire-stringify:8` reads:

```raku
my @grid  = [ flat (Empty, Tree, Burning) xx $w ] xx $h;
```

Pass 17 catalogued line 8's blockers as *the `[...]` composer* plus *`flat`'s missing runtime dispatch*. The
composer is now in — **and line 8 still fails to parse.** The cause was uncatalogued:

⛔ **`OP_REP_XX` carries a `%left` precedence declaration (`raku.y:447`) but appears in exactly TWO productions,
both statement-level** (`raku.y:492,505`: `… VAR_ARRAY '=' expr OP_REP_XX expr ';'`). **It cannot occur inside an
expression at all.** Line 8 has two `xx`: the outer one is statement-level and works; the inner one, inside the
brackets, is not.

⭐ **The decisive repro is bracket-free, which is what makes the diagnosis certain rather than plausible:**

```
say (1 xx 2);          ->  parse error      # no brackets involved at all
my @a = [1, 2] xx 3;   ->  1 2 1 2 1 2      # composer works as the LEFT operand of statement-level xx
my @a = [1 xx 2];      ->  parse error      # same failure, inside brackets
```

**A precedence declaration is not a production.** `%left OP_REP_XX` made `xx` *look* like a general operator to
anyone grepping for it — the token is declared, prioritized, and used — while the grammar only ever accepts it in
two fixed statement shapes. ⛔ **That is why it survived 17 passes uncatalogued: the evidence of generality was
present and misleading.**

⛔ Promoting `xx` to `expr` is real grammar surgery — the two existing statement productions become ambiguous
against a general `expr : expr OP_REP_XX expr` — **not a mechanical mirror.** It is the highest-value *bounded*
item now open on this row. `flat`'s missing dispatch arm is real and sits **behind** it.

## ⚠️ Second correction: `rc-9-billion-names` never reached its `[]`

It was catalogued as a `[...]`-composer consumer (`my $r = [];`, line 7). It **dies at line 1** on
`my @todo = $[1];` — the `$`-itemizer, catalog item (g) — and it is a **LEX** error (`unexpected char '$'`), not a
parse error. The `[]` fix is real but was never that kernel's first blocker.

## ⛔ Conflict delta was +1, and that is a discipline note, not a regression

**102/11 → 103/11 shift/reduce.** This row's prior passes achieved *zero* delta, so the bar deserves an explicit
amendment rather than a silent miss: **those constructs (`enum NAME <…>;`, `is copy`) were not expression-initial;
this one necessarily is.**

Measured on scratch copies before touching the real file, then located exactly — the new conflict lands in the one
state that **already carried 31 of identical shape**, and `'['` now reads there character-for-character like the
pre-existing `'('`:

```
'('  shift, and go to state 120         '['  shift, and go to state 62
'('  [reduce using rule 2 (stmt_list)]  '['  [reduce using rule 2 (stmt_list)]
```

Both resolve by **shift** (bracketed arm = discarded), which is the correct reading: `[` at a statement boundary
begins a new expression-statement. ⭐ **Structurally unavoidable for any new expression-initial token — so
"zero delta" cannot survive contact with this class of construct. Characterize it; don't chase it.**

## Control arms

Two full `make pristine` verifications, the second **after** a mid-pass rebase that pulled in `4cf66b91`
(`emit: SCRIP_ZD_MAP`) touching **`src/emitter/emit.cpp`, shared across every language** — re-run rather than
trusted, per this row's REBASE-BASELINE COROLLARY:

- `test_crosscheck_raku.sh` **51/51 FAIL=0**
- `test_smoke_raku.sh` **724/724 PASS both m3 and m4, REFUSED=0**
- full 17-kernel sweep **3/16, unchanged** — this pass advances kernels, it does not flip one
- m3 vs m4 **byte-identical** on the composer repro (m4 built by hand: `--compile` → `gcc -no-pie` → link)

Regenerated via `scripts/regenerate_parser_and_lexer_from_sources.sh`; pascal/rebus/snobol4/snocone's
incidentally-regenerated files reverted after confirming pure tool-version skew (their `.y`/`.l` untouched).
