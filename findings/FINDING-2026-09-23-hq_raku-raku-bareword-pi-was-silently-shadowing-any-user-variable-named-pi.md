# FINDING 2026-09-23 hq_raku — bareword `pi`/`Inf`/`NaN`/`i` were silently shadowing same-named user variables (fixed); exposed a separate real-number stringification precision gap (not fixed)

## The bug that was fixed

`src/lower/lower_raku.c`'s `TT_VAR` case special-cased the bareword names `pi` (pre-existing),
and `Inf`/`NaN`/`i` (added this sitting), by matching on `t->v.sval` alone. But the Raku grammar strips
sigils before building a `TT_VAR` node uniformly for BOTH a bareword term (`pi`) and a sigiled variable
read (`$pi`) — both arrive with `.sval == "pi"`, indistinguishable by name. So the pre-existing `pi` check
was not "recognize the bareword constant `pi`", it was "treat ANY read of a variable literally named `pi`,
sigiled or not, as the constant 3.141592653589793" — a silent-wrong-answer bug for any program computing
into a variable named `$pi`.

**Measured, live in the corpus:** `corpus/tests/raku/ALL.raku` entry `benchmark_pi-sequential-iteration`
computes an iterative approximation of pi into `$pi` and prints it:
```raku
my $pi = 4.0 * $delta * $sum;
say $pi;
```
Before this sitting's fix, this printed the hardcoded constant `3.141592653589793` regardless of what the
loop actually computed — the loop's result was silently discarded. That the program is named
`pi-sequential-iteration` and the ref just happens to be close to real pi made this the kind of bug that
looks correct at a glance.

**The fix (this sitting, same commit as Inf/NaN/i):** the grammar (`raku.y`'s `var_node()`) now stamps
`e->slen = 1` on a `TT_VAR` leaf only when the source token carried no sigil at all (`IDENT`, not
`VAR_SCALAR`/`VAR_ARRAY`/`VAR_HASH` — the two lexer token classes are already distinct, `var_node()` is
just the single C helper both funnel through). The lowerer's bareword-constant checks now require
`t->slen == 1` in addition to the name match. (`tree_t.slen` was chosen over `tree_t.n` — `.n` is the real
child count and `--dump-ast`/`ast_print.c` blindly indexes `.c[0..n-1]`, so setting `.n=1` on a
childless leaf segfaults the printer immediately; `.slen` is unused by the Raku frontend and by
`ast_print.c` entirely, confirmed by grep before use.)

**Verified:** `$i = 42; say $i; say $i*2;` and `$pi`-as-a-real-variable both now behave as ordinary
variables, byte-identical to real Rakudo (`/usr/bin/raku`, checked directly). `pi`/`Inf`/`NaN`/`i` as
genuine barewords still resolve to their constants, also byte-identical to the oracle.

## What this exposed, not fixed: `rk_real_str`'s digit count disagrees with Rakudo's

With `$pi` now correctly computing and printing its real value, `benchmark_pi-sequential-iteration` FAILs
for a *different* reason: SCRIP prints `3.1415926535897643`, the oracle prints `3.141592653589764` — NOT
the same double (`float("3.1415926535897643") != float("3.141592653589764")` in Python, confirmed), and
not merely a shorter/longer rendering of the same bit pattern. The values agree to ~13 significant digits
and diverge after that, consistent with either a genuine floating-point summation-order difference
somewhere in this loop's arithmetic, or `rk_real_str`'s round-trip search (`by_name_dispatch.c:1261`, tries
precision 15/16/17 in order and stops at the first that round-trips through `strtod`) landing on a
different-but-also-round-tripping representation than whatever Rakudo's own formatter picks. **Not
diagnosed further this sitting** — it is a numeric-precision question, not a Raku-frontend one, and
deserves its own ASM-DIFF-style investigation (isolate the loop, compare SCRIP's `$sum`/`$pi` bit pattern
directly against a minimal Rakudo run of the same loop, before touching either the summation or the
formatter) rather than a guess under time pressure. Left as `benchmark_pi-sequential-iteration`'s current
FAIL reason in the RakM board.

## Also newly visible in this sitting's board: `benchmark_merge-sort` moved from FAIL to CRASH

Already disclosed in the Inf/NaN commit: fixing `Inf`-as-undeclared-variable let this program get past its
earlier compile-time rejection into a real SIGSEGV at runtime (`.Slip`/`Inf`-sentinel array comparison,
`gd_binop_relop`-adjacent — not traced further). Not a new defect this sitting exposed by the pi/i fix;
carried forward here only so the board's CRASH count has a named cause rather than reading as unexplained.
