# FINDING 2026-08-30 hq_C — roast PARSE-FAIL is an ALL-gaps-closed metric: curing 197 files' first error moved the count by 3

**Tree:** SCRIP `ead6fa89` → `d3c7dc90` · roast in-tier 986 · measured 2026-08-30, seat `hq_C`,
row `raku-roast-100-percent-compile` (rank 0, Lon's TRIO stand-up: "100% compile, no gaps at compile time").

## The claim

The row's DONE-WHEN grades `PARSE-FAIL` from `raku_roast_scoreboard.sh`. That is the right **bar** and a
**bad progress signal**, and a seat pacing the campaign by it will conclude the work is not moving.

Two real construct cures landed this pass. Their effect on the board:

| board | PASS | FAIL | **PARSE-FAIL** | NO-TAP | CRASH |
|---|---|---|---|---|---|
| baseline `ead6fa89` | 3 | 9 | **927** | 4 | 2 |
| after twigils | 3 | 9 | **925** | 6 | 2 |
| after qualified names | 3 | 9 | **924** | 7 | 2 |

**Three files.** The same two cures, measured per-construct instead:

| error class | before | after |
|---|---|---|
| `lex error: unexpected char '$'` (twigils) | **210** | **13** |
| `use Test::Util;` (qualified names) | **108** | **0** |

And measured per-file, comparing each file's failing line number across runs:

```
fully cured (no longer parse-fail):   5
advanced DEEPER into the file:      152   (median +9 lines, +1940 lines of source newly parsed)
regressed shallower:                  0
newly failing:                        0
```

## ⭐⭐ Why — and why it is not a defect in either instrument

A roast file is hundreds of lines exercising dozens of independent constructs. `PARSE-FAIL` is a
**per-file any-gap** metric, so a file leaves it only when its LAST gap closes. Curing a file's first
error just exposes its second: 166 of the 210 twigil failures were roast's standard preamble line
`use lib $*PROGRAM.parent(2).add(...)`, and the very next line is `use Test::Util;` — which is why the
second cure was worth taking immediately, and why even both together move so few files across the line.

**Neither number is wrong.** PARSE-FAIL is the correct completion bar — the row closes at 0 and must.
The per-construct histogram is the correct **progress** signal. Reporting only the first makes 197 cured
first-errors look like 3, and a campaign that looks stalled while it is working is one that gets
abandoned or re-scoped by whoever reads the board next. ⛔ The inverse trap is the dangerous one: near
the end, closing one last common construct will move PARSE-FAIL by hundreds at once, so **the curve is
not linear and mid-campaign extrapolation from it will be badly wrong in both directions.**

## The instrument

`scripts/util_raku_roast_error_histogram.sh` (landed `32f41604`) emits `file <TAB> line <TAB> source text`
for every in-tier parse/lex failure, so failures cluster by **construct**. bison's own message cannot do
this: **897 of 923 remaining failures carry the single string `syntax error`**, which discriminates
nothing. The script refuses rc=2 rather than reporting a histogram it could not populate.

## Measured next clusters (verified by ablation, not by grep)

| n | construct | witness |
|---|---|---|
| 33+ | colon method-call `.method: args` | `use lib $*PROGRAM.parent(2).add: 'packages/Test-Helpers';` |
| 13 | `{;` forced-block in `.map` | `@sines.map({; $_.key - f(90) => $_.value })` |
| 8 | `...` sequence operator | `my @list = (1 ... 10);` — `..`/`..^` exist, `...` does not |
| 8 | qualified name in class/role/grammar decl | `class Foo::Bar { }` — QIDENT now exists, decls do not take it |
| 4 | shaped-array binding | `my @arr := Array.new(:shape(2;2));` |
| 3 | versioned `use` | `use v6.e.PREVIEW;` |

⚠️ **Colon-call is the largest and is NOT a one-line addition.** `call_expr`/`postfix_expr` in `raku.y`
enumerate each base×shape combination (`VAR_SCALAR '.' IDENT '(' arg_list ')'`, …) rather than recursing
a general postfix chain, so a general `.method: args` needs that chain, in a grammar already carrying
115 shift/reduce and 12 reduce/reduce conflicts. Scope it as its own rung with room to grade it, and
hold the conflict counts flat as the acceptance signal — both cures this pass held them exactly.
