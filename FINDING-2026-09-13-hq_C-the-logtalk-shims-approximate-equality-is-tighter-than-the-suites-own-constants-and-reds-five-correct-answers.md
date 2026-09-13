# FINDING — the Logtalk shim's `=~=` is tighter than the suite's own constants, and reds five answers that are byte-identical to the oracle

**Seat:** hq_C · **Date:** 2026-09-13 · **Tree:** SCRIP `39cc0e78e` (measured before this seat's float-overflow cure; the
cure does not touch any case named here) · **Instrument:** `SCRIP/scripts/lib_logtalk_lgtunit.pl`, `'=~='/2` + `lgt_near/2`

## The claim

Five cases in `corpus/packages/prolog/logtalk_iso` are RED for SCRIP **and would be RED for SWI-Prolog**, because the
shim's approximate-equality tolerance is tighter than the precision of the constants the suite writes. They are not
SCRIP defects. SCRIP's answer on all five is **byte-identical to swipl's**.

## The measurement

The shim accepts `A =~= B` when `abs(A-B) =< 1.0e-9` or `abs(A-B)/max(|A|,|B|) =< 1.0e-6`. Every `true(Var =~= Const)`
expectation in the suite was extracted (40 of them), its goal run under `swipl -q`, and the relative error of swipl's
own answer against the suite's own constant computed. Five exceed the shim's tolerance:

| case | swipl's answer | suite constant | relative error |
|---|---|---|---|
| `iso_tan_1_01` | `0.5463024898437905` | `0.5463` | **4.558e-06** |
| `lgt_asinh_1_01` | `1.1947632172871094` | `1.19476` | **2.693e-06** |
| `lgt_cosh_1_01` | `1.8106555673243747` | `1.81066` | **2.448e-06** |
| `lgt_acosh_1_01` | `1.3169578969248166` | `1.31696` | **1.597e-06** |
| `iso_integer_power_2_09` | `0.3535533905932738` | `0.353553` | **1.105e-06** |

SCRIP's answer for each of the five is the same double, digit for digit. The suite writes these constants to **five or
six significant digits** (`0.5463` is four), so the rounding error inherent in the literal is larger than `1.0e-6`
relative; the tolerance cannot accept a correct answer.

## Why the tolerance was set where it was, and what the error actually is

The shim's own comment says: *"`E is log(2.71828)` then `E =~= 1.0`; the true value is 0.999999327347282, a RELATIVE
error of 6.73e-7 ... 1.0e-6 is the loosest-needed value and is what lgtunit itself uses."*

`6.73e-7` is right, and `iso_log_1_02` really is that case. But it is the **loosest of the cases that were looked at**,
not the loosest in the suite — the true worst is `iso_tan_1_01` at `4.558e-06`, nearly seven times further out.
⭐ **THE SHAPE: a tolerance was calibrated from the worst case in a sample and written down as the worst case in the
population.** Nothing in the run said how many of the 40 expectations were consulted, and a tolerance that is too tight
does not announce itself — it reports a red, which is what a young frontend is expected to print anyway. The second
clause of the comment (*"is what lgtunit itself uses"*) could not be checked here at all: upstream `lgtunit` is **not
vendored** with the suite (`_PROVENANCE.md` vendors `tests/prolog/` only), so the shim reimplements a predicate whose
original nobody in this tree can read, and the reimplementation's justification is a claim about an absent file.

## What this costs

Five case-modes ×2 = ten rows of the Logtalk board are red for a reason that has nothing to do with the implementation
under test, and four of them sit inside one family row (`prolog-logtalk-arithmetic-functions-family`) as apparent
arithmetic defects. ⛔ **The direction matters:** this error reds correct answers rather than greening wrong ones, so it
is the safe direction — but it is still an instrument that cannot be satisfied, and a row whose remaining reds are
unsatisfiable can never close.

## What is NOT proposed here

⛔ **A tolerance is not something to loosen until the reds go away** — that is the false-green move, and it would make
the instrument unable to see a real arithmetic defect of five significant digits. The honest fix is to compare at the
precision the constant is actually written to (half a unit in its last written decimal place), which is
self-calibrating and carries no magic number; a flat `1.0e-5` would also clear all five but is a fudge factor chosen
to fit. Either way the change moves every Prolog seat's board, so it is routed as an ASK, not landed by this seat.

## Reproduce

```bash
cd SCRIP && for c in 'X is tan(0.5)' 'X is asinh(1.5)' 'X is cosh(1.2)' 'X is acosh(2.0)' 'X is 2**(-1.5)'; do
  echo ":- initialization((( $c ), write(X), nl))." > /tmp/w.pl
  printf '%-18s scrip=%s swipl=%s\n' "$c" "$(./scrip /tmp/w.pl </dev/null 2>&1)" "$(swipl -q /tmp/w.pl </dev/null 2>&1)"
done
```
