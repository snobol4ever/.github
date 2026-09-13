# FINDING — SPITBOL flushes subnormals to zero end to end and SCRIP keeps them end to end, so curing either half alone REGRESSES programs that pass by consistency

**hq_U, 2026-09-13 · SCRIP `5b17c350f` · corpus `d97c5fe87` · .github `d5bd712b` · MODE NONET**

Found on row `snobol4-spitbol-x64-tests-self-check-but-nothing-reads-their-verdict` while curing the
*other* end of the double range (`FINDING-2026-09-13-hq_U-the-numeric-fast-path-in-eval-never-reaches-the-lexer…`).
The arm described here was written, measured, **and withdrawn**; this file is why.

## The two engines

SPITBOL has no subnormals. Every value whose magnitude falls below `DBL_MIN` becomes zero — and not
only on the way in:

```
    A = 1.0e-300 ; B = 1.0e20 ; X = A / B        sbl -bf: X = 0.      X * B = 0.
    Y = 2.6308364999025777e-310                  sbl -bf: Y = 0.      Y * 1.0e300 = 0.
```

`X * B` and `Y * 1.0e300` are the decisive lines: they prove the value **is** zero, not merely
printed as zero. The behaviour is exactly SSE `FTZ` + `DAZ`, confirmed directly in C — with both bits
set, `strtod` still returns the subnormal bit pattern, but `b*c`, `x-y` and `p/q` all return `0`
where IEEE default arithmetic returns a subnormal.

SCRIP keeps subnormals everywhere: the lexer (`strtod`), the `EVAL` numeric fast path, the runtime
string→real coercion `to_real` (`src/runtime/core/core.c:2829`), and SSE arithmetic at IEEE default.

## ⭐ The finding — each engine is SELF-CONSISTENT, and that is what makes a partial cure dangerous

`math_diff` grades 15376 assertions through `chks(expression, expected)`, whose test is

```
    observed = EVAL(expression)
    diff = abs(observed - expected)
    LE(diff, 1.0e-12 * abs(expected))
```

Both engines pass it today, **for opposite reasons**:

- **SPITBOL:** `observed` = 0 − 0 = 0 (both literals flushed), `expected` coerces to 0, the tolerance
  `1.0e-12 * 0` is 0, and `LE(0,0)` passes.
- **SCRIP:** nothing is flushed, `observed` is the exact subnormal difference, `expected` coerces to
  the same subnormal, `diff` is 0, and `LE(0,0)` passes.

Flushing **only** in the EVAL fast path — the one-line change that flips `math_limits1` and
`math_limits4` — breaks that symmetry: `observed` becomes 0 while `expected` still coerces through
`to_real` to a live subnormal, so `diff` is 1.06e-310 against a tolerance of 0, and 12 assertions
fail. **Measured: `math_diff` m3 went green → red on exactly that**, and the board read 21/36 with a
regression rather than 19/36 clean. The arm was withdrawn and only the overflow half landed.

A second shape in the same file needs more than the scanner anyway:
`2.4634832395831848e-300 − 2.6308364999025777e-310` has **normal** operands and a **subnormal
difference**. SPITBOL returns 0 for it. No amount of scanner work reaches that — it is the
arithmetic result itself.

## What the cure actually is, and why it is a row and not a line

Faithfulness here is one decision taken in three places at once, or not at all:

1. the SNOBOL4 lexer (`sno_real_scan` already exists and is the hook),
2. the runtime string→real coercion (`to_real`),
3. the arithmetic result — `FTZ` + `DAZ` in `MXCSR`, set once in the runtime's startup.

⛔ **(3) is why this is not a local cure.** `to_real` and the MXCSR are **shared across all seven
frontends** — Icon reals, Pascal reals and Prolog floats all pass through them, and none of the three
has any reason to want SPITBOL's flush-to-zero. A landing owes SHARED-NODE VERDICT SCOPE on every
frontend that reaches them, and the honest question it has to answer first is whether the flush is
**scoped to the SNOBOL4/Snocone runtime** or applied process-wide. That is a ruling, not a patch.

## ⭐ The general form, which is the part worth carrying out of here

**Two engines that are each internally consistent can agree on a test for opposite reasons, and the
cure that makes one of them *more* correct in isolation makes the pair *less* correct.** The green
cell never said "these agree"; it said "these agree here." The tell is cheap and I nearly missed it:
after a one-line scanner change, a program that had nothing to do with the four under the row went
red — and the instinct is to treat that as noise from a contaminated board rather than as the
measurement telling you the class is wider than the row.

Corollary for the seven-point standard: **a suite whose assertions carry a relative tolerance can
pass with both sides zero.** `LE(diff, 1.0e-12 * abs(expected))` is a vacuous test when `expected`
underflows, and `math_diff`, `math_div`, `math_prod`, `math_read`, `math_cos`, `math_sin` and
`math_minus` all carry subnormal literals. Their green is partly the tolerance collapsing, not the
arithmetic agreeing — worth knowing before anyone cites that package as float coverage.

## Owed

A row: `snobol4-spitbol-flushes-subnormals-to-zero-and-scrip-does-not-cure-scanner-coercion-and-arithmetic-together-or-not-at-all`,
hq_U, with `math_limits1` and `math_limits4` as its DONE-WHEN (both proven red today) and `math_diff`
plus the Icon, Pascal and Prolog boards as its control arms.
