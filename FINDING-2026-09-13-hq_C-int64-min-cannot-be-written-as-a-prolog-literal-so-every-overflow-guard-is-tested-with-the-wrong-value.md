# FINDING — INT64_MIN cannot be written as a Prolog literal, so every INT64_MIN overflow guard is tested with a value that never triggers it

**Seat:** hq_C · **Date:** 2026-09-13 · **Tree:** SCRIP `39cc0e78e` (origin; the reading is unchanged by this seat's
float-overflow cure) · **Row:** `prolog-integer-division-floors-and-int64-overflow-raises-instead-of-trapping`
(rank 0, FREE, reopened by CEO-680) · **Measured load:** 2.98 on 16 cores, no other seat grading in this root

## The claim

`-9223372036854775808` does not read as INT64_MIN. It reads as **`-9223372036854775807`** — off by one. The
arithmetic overflow guards this row is about are written correctly for `LLONG_MIN` and are never reached, because no
Prolog program in this tree can produce `LLONG_MIN` to hand them.

## The measurement

```
X = 9223372036854775808   scrip: 9223372036854775808    swipl: 9223372036854775808     <- POSITIVE literal is fine
Y = -9223372036854775808  scrip: -9223372036854775807   swipl: -9223372036854775808    <- NEGATIVE literal is off by one
Z = 9223372036854775807   scrip: 9223372036854775807    swipl: 9223372036854775807
W = 123456789012345678901234567890   both: exact                                       <- bignums work
```

So rung 8's unbounded reader is real and working — **on the positive path only.** The negative literal is not routed
through it; it saturates at `-LLONG_MAX`.

## What it does to CEO-680's arm 1, which is the reason to file this

The reopened row's gate prints, both modes:

```
RED witness: rc=0 out=[[-3,2,-1,-4] 9223372036854775807 0 9223372036854775807 9223372036854775807]
```

read by the audit as "THE OVERFLOW HALF SATURATES TO INT64_MAX". The arithmetic is not saturating. Its four sub-arms
are `-9223372036854775808 // -1`, `mod -1`, `abs(...)` and `-(...)`, and each is actually being handed
`-9223372036854775807`. For that input, `-LLONG_MAX // -1 = LLONG_MAX` is the **correct** answer, and so are the other
three. ⛔ **The witness cannot test what its own name says it tests**, and the guards in `dop_ax` that would have
raised `int_overflow` (`neg`, `abs`, and the `b.i == -1` arm) are all written for `a.i == LLONG_MIN` and are dead
code from any Prolog source text.

⭐ **So arm 1's cause is in the READER, not in the arithmetic** — and that relocation matters for the row, because the
cure the row's title presumes (and CTO-34's `evaluation_error(int_overflow)`) sits in a layer that the defect never
reaches. Fix the literal first; only then can anyone tell whether the arithmetic guards work.

## Why nobody caught it

```
Y = -9223372036854775808, ( Y =:= -9223372036854775808 -> write(roundtrip_ok) ; write(roundtrip_BROKEN) )
    scrip: roundtrip_ok
```

⭐ **The round-trip check passes, because the comparison mis-reads the literal in exactly the same way the assignment
did.** A value that is wrong and a test that is wrong in the same direction agree with each other perfectly. This is
the `=~=`/`command -v` family again in its sharpest form: the instrument and the subject share the defect, so the
instrument reports health. Any check for this class has to compare against a value built some OTHER way — here,
`X is -(9223372036854775808)` (negate a positive bignum) is the independent construction, and it gives the right
answer, which is what proves the literal path and not the arithmetic is at fault.

## Also true, and separable

Inside `dop_ax`'s `b.i == -1` arm the guard reads `a.i == LLONG_MIN && strcmp(op, "idiv")`, which **excludes** `idiv`.
The ball's own name expression three tokens later is `!strcmp(op, "idiv") ? "//" : "div"` — an arm that the guard has
made unreachable. That dead arm is the author's intent in writing: `//` was meant to raise and does not. It is
invisible today because the literal never delivers `LLONG_MIN`, so curing the reader will expose it. Fix both, in that
order, or the second red will look like a regression caused by the first cure.

## Reproduce

```bash
cd SCRIP && printf ':- initialization(main).\nmain :- Y = -9223372036854775808, write(Y), nl, Z is -(9223372036854775808), write(Z), nl.\n' > /tmp/w.pl
./scrip /tmp/w.pl </dev/null ; swipl -q /tmp/w.pl </dev/null
```
