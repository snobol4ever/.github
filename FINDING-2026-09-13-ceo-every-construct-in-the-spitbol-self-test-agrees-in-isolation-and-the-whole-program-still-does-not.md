# FINDING — every construct in the SPITBOL self-test agrees in isolation, and the whole program still does not

**ceo, 2026-09-13**, working Lon's ruling that all eight SPITBOL test programs are in (CEO-725).

`spitbol_testpgms/test1` is SPITBOL's own diagnostics program. The oracle raises errors at **25**
distinct statements running it; we raise at **22**, and **all 22 shared statement numbers match
exactly**. Three are missing: statement 137, which is the already-tolerated `VALUE()` oracle quirk,
and two more.

## What the missing raises are, and what they are not

Every `ERROR 29` in the program comes from the **undefined unary `!` operator**. SPITBOL has no `!`,
so evaluating one raises 29, the program's `SETEXIT` handler catches it and continues, and the error
count is the program's own score. There are sixteen distinct `!` shapes in the source.

⭐ **ALL SIXTEEN AGREE WITH THE ORACLE IN ISOLATION** — measured, one witness per shape, same
`&ERRLIMIT`/`SETEXIT` frame, both engines: `!(IDENT(A,'A') IDENT(B,'B'))`, `!(IDENT(D) IDENT(E))`,
`!LT` `!LE` `!EQ` `!NE` `!GT` `!GE`, `!INTEGER(12)`, `!INTEGER('12')`, `!LGT('XYZ','ABC')`,
`!LGT('ABC',NULL)`, `!APPLY(.EQ,1,1)`, `!APPLY(.EQ,0)`, `!APPLY(.EQ,1,1,1)`, and
`!IDENT(APPLY(.TRIM,'ABC '),'ABC')`. Sixteen of sixteen, byte-identical.

⛔ **SO THE RESIDUE IS A CUMULATIVE STATE EFFECT, NOT A CONSTRUCT.** The whole-program diff is
unchanged at nineteen lines after tonight's cure. Two `!` sites that raise correctly on their own do
not raise inside the full program.

## The hypothesis I had, and why I am recording that it was wrong

I read the source tail and concluded the two missing raises were `!APPLY(.EQ,0)` and
`!APPLY(.EQ,1,1,1)` — a call with too few arguments short-circuiting before the operator was reached.
That produced a **real, separate defect** which is cured and landed (`SCRIP c16f8fdf0`): a builtin
called with fewer arguments than it declares is now padded with null, as the oracle does. `EQ()`
succeeded on the oracle and failed for us; it now agrees.

**And test1 did not move.** The hypothesis was a reading, not a measurement, and the cure it produced
is good for its own reasons and is not this. ⭐ That is the whole entry: a plausible cause, a genuine
cure, and a board that does not move is the same shape as hq_R's `rewind1` — the most expensive way
to learn a red is not what you thought.

## What Lon's mechanism does about it

CEO-725 rules the eight programs are decomposed into the master's one-liner and banner-block entries.
The sixteen witnesses above are exactly those entries and every one is green. Once they are in the
master, the constructs are **graded and defended**, and "the whole 399-line program in one run" becomes
a separate and much narrower question about cumulative error-handler state rather than the thing
blocking sixteen constructs from being scored at all.

## Numbers, so nobody re-derives them

| reading | oracle | ours |
|---|---|---|
| statements raising an error | 25 | 22 |
| shared statement numbers | 22 | 22 |
| errors counted by the program | 29 | 24 |
| `&ERRLIMIT` left | 975 | 978 |
| `&STCOUNT` | 370 | 364 |

Also measured tonight and **not** cured: `SIZE()` answers `0` on the oracle and the empty string for
us even after the padding cure, so `SIZE` does not reach that dispatch — it has its own leaf. Named
here rather than folded into an unrelated commit.
