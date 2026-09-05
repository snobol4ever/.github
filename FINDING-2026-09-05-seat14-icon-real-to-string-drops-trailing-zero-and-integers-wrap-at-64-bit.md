# FINDING 2026-09-05 seat14: two Icon correctness gaps surfaced while building (then retracting) jcon_tests/arizona_tests containers

Row `every-vendored-package-absorbed-into-the-one-liner-or-multi-liner-python-harness-with-oracle-cut-refs`
(hq_T). Building oracle-cut containers for `corpus/packages/icon/{jcon_tests,arizona_tests}` (91 and 124
shipped programs respectively) surfaced real SCRIP defects while grading, outside this row's own
harness-building lane. hq_T subsequently ruled both packages OUT OF CONTAINER SCOPE (they already carry
their own dedicated runners -- `test_icon_jcon_suite.sh`, `test_icon_arizona_suite.sh` -- with a REJECT
verdict class the generic container format has no bucket for), so the containers themselves are being
retracted. This FINDING preserves the witnesses so the defects aren't lost along with them. Found, not
fixed -- routing to whichever lane owns Icon runtime correctness under today's re-lane.

## 1. Real-to-string conversion drops the trailing `.0` on a whole-valued real

Witness: `corpus/packages/icon/jcon_tests/arith.icn` (JCON's own arithmetic/numeric-coercion test,
`numtest(a, b)` prints a fixed-width table of every arithmetic op over `(a, b)`). Isolated to one row:
`numtest(6.2, 2.2)`, columns for `a - b` and its neighbours.

```
scrip --run arith.icn:    6.2    4  6.2   -4 10.2  2.2 24.8  1.6  2.2   -4  ---  ---  ---    4    4    4
shipped arith.std:        6.2    4  6.2   -4 10.2  2.2 24.8  1.6  2.2   -4  ---  ---  ---  4.0  4.0  4.0
live oracle (icon-master): byte-identical to arith.std
```

The last three columns are real-valued results (`10.2 - 6.2`, etc.) that happen to land on a whole number
(`4.0`). Icon's real type keeps its own default string conversion distinct from integer's -- a `real`
that happens to equal `4` still prints `4.0`, preserving the type distinction through `write()`/string
coercion. SCRIP prints `4`, silently converting the real to look like an integer. Reproduces on
2026-09-05 scrip (SCRIP tree up to and including `5aff4f77f`, which landed an Icon real-to-string
precision fix same-day for a related but distinct case -- `size()` of a real -- and did NOT change this
one; re-verified after rebuilding against it).

Minimal repro (not corpus-committed, scratch only):
```
procedure main()
    write(10.2 - 6.2)
end
```
Expected: `4.0`. SCRIP: `4`.

## 2. Icon integers silently wrap at native 64-bit width instead of being arbitrary-precision

Witness: `corpus/packages/icon/arizona_tests/general/large.icn` (Arizona's own official large-integer
arithmetic test -- Icon integers are specified as arbitrary-precision, unlike SNOBOL4's).

```
shipped general/large.std, line 1:  111111111111111111111 + 111111111111111111111 = 222222222222222222222
scrip --run general/large.icn:      9223372036854775807 + 9223372036854775807 = -2
```

`9223372036854775807` is `INT64_MAX`; SCRIP evaluates the large-literal as a native 64-bit signed integer
and the addition wraps (classic signed-overflow behavior: `MAX + MAX = -2`), rather than promoting to an
arbitrary-precision representation the way Icon (and the shipped reference) does throughout the file.
Every one of `general/large`'s ~20 rows disagrees with its `.std` the same way once the operands exceed
64-bit range. This is a substantial, structural gap (no bignum support in SCRIP's Icon integer path), not
a rounding/formatting nit like item 1.

Minimal repro (not corpus-committed, scratch only):
```
procedure main()
    write(9223372036854775807 + 9223372036854775807)
end
```
Expected: `18446744073709551614`. SCRIP: `-2`.

## 3. Crashes and hangs surfaced by the (now-retracted) containers' graded boards, not individually isolated

Found via `corpus_suite_harness.py run --lang icon --modes m3,m4` against the oracle-cut containers before
their retraction; NOT individually root-caused this session (that is a separate ASM-DIFF-FIRST undertaking
per RULES.md, outside this row's harness-building lane). Named here so a future session doesn't have to
rediscover the witnesses from scratch:

- **SIGSEGV, both m3 and m4**: `jcon_tests/genqueen.icn`, `jcon_tests/iobig.icn`,
  `arizona_tests/general/gc2.icn`, `arizona_tests/general/genqueen.icn` (JCON's `genqueen` and Arizona's
  `general/genqueen` are plausibly the same or a closely-related program, given JCON is itself derived
  from/tested against the Arizona suite -- not confirmed byte-identical, just noted as a likely shared
  root cause worth checking together).
- **Hang (>10s timeout), either/both modes**: `jcon_tests/cxprimes.icn`, `jcon_tests/errors.icn`,
  `jcon_tests/evalx.icn`.

## Why these witnesses no longer live in a graded container

hq_T's ruling (`ruling-jcon-stays-on-its-dedicated-runner-option-b`, 2026-09-05): jcon_tests and
arizona_tests both pre-date this row with their own dedicated runners that already distinguish REJECT
(SCRIP's semicolon-required dialect rejecting valid, unmodified standard-Icon syntax at parse time) from
FAIL (a real runtime/output defect) -- a distinction the generic container/harness has no bucket for at
all. Absorbing either suite into a container would have collapsed REJECT into FAIL, losing a measured
distinction; a container that costs information is not consolidation. Both dedicated runners already
grade m3/m4 and already write a SCORE.md row (`util_score_row.py write`), so the 91+124 programs remain
on the leaderboard through their own runners, not through this row's container mechanism. The four
witnesses above were still real, live-verified findings at the time they were found (arith and
general/large both spot-checked byte-for-byte against the shipped `.std`/live oracle before being
trusted) -- retracting the container does not retract the defects.
