# `lgint` is byte-identical to Arizona `iconx` once the three unbounded rows are removed — so 22 of its shipped-ref differences are jcon divergence, not our defects

**hq_I, 2026-09-10.** SCRIP `3bbdfc8c7` + the `^`-with-a-large-integer-exponent cure, corpus `dd661ede8`,
`RT_OPT=-O0`, modes 3 and 4 (byte-identical to each other). Row
`icon-jcon-lgint-large-integer-arithmetic-prints-every-digit-as-its-shipped-ref-oracle-cannot-finish`
(Lon 2026-09-10 *"Get lgint and toby working."*, CEO-491).

## The measurement that changes the ruling

CEO-491 ruled the shipped jcon `.std` stands as `lgint`'s expected output **because the oracle cannot
finish the program** — true, and correctly reasoned from what was known: `iconx` prints 142 of 452 lines
and then squares bignums forever inside `bigexp` at `-2 ^ 36472996377170786403`.

⭐ **But the unboundedness is confined to three rows, not to the program.** Only `|base| >= 2` with a
*positive* huge exponent runs away; every other row in `lgint` answers instantly. Delete just the three
big-`v` `bigexp` calls (`3 ^ 41 | 6 ^ 25 | -7 ^ 23`) from line 20 and Arizona `iconx` runs the whole
thing in under a second:

```
$ sed 's/every bigexp(3 | 6 | -7 | 3 \^ 41 | 6 \^ 25 | -7 \^ 23);/every bigexp(3 | 6 | -7);/' lgint.icn > lgint_bounded.icn
$ icont -s -o lgint_bounded.ora lgint_bounded.icn && ./lgint_bounded.ora   # 413 lines, rc=0
$ scrip lgint_bounded.icn                                                  # 413 lines, rc=0
$ diff  <oracle> <ours>   →  NO DIFFERENCES
```

**413 of 413 lines identical to the oracle, in both modes.** So "the oracle cannot grade `lgint`" is
false as stated: the oracle cannot grade **three rows** of it, and it grades the other 449 exactly.

## What that leaves

After the cure, `lgint` differs from the shipped jcon `.std` at **22 line positions** (44 `diff` lines —
⛔ `diff | grep -c '^[<>]'` counts both sides, which is how this row's first report said 76 and then 38).
Every one of the 22 is a line where **`iconx` and SCRIP agree and jcon differs**:

| n | class | jcon `.std` says | `iconx` **and** SCRIP say | how proven |
|---|---|---|---|---|
| 4 | `image()` of a large integer | `3 ^ 62 = 381520…809`, and `~10^N` one lower at 64/73/75 | `integer(~10^30)`, `~10^31`, `~10^35`, `~10^36` | probe `image(3 ^ (58 to 78))` under `iconx` |
| 17 | real formatting | Java shortest-round-trip: `4.111111111111111`, `-2.7368747340080914e19` | Icon's own: `4.111111111`, `-2.736874734e+19` | the 413-line bounded run above |
| 1 | `0 ^ v`, `v` a negative large integer | `error 201` | `error 204` | probe `bigexp(-7 ^ 23)` under `iconx` |

⛔ **The `image()` class is the one that would have been swallowed silently.** Taking jcon's line 62
verbatim would have made us print 30 digits where Arizona Icon prints `integer(~10^30)` — i.e. it would
have turned a *correct* implementation of `image()` into a defect, and the board would have called that
progress.

## The refinement CEO-491 needs

The ruling's principle is right; its scope was drawn one level too wide. Proposed narrowing:

> The jcon ref stands **only for the rows no oracle can reach** — in `lgint`, the four
> `|base| >= 2 ^ positive-huge-exponent` rows, whose `error 203` we now raise on jcon's authority.
> Every other row is graded against Arizona `iconx`, which reaches all of them.

Under that narrowing `lgint.std` needs 22 lines re-cut to the Arizona answers, after which `lgint`
passes byte-for-byte in both modes and **stays inside the graded denominator** — strictly better than
the alternative of parking it in `OUTSIDE_ARIZONA_BASELINE.tsv`, which only ever lowers the number.
⛔ The re-cut itself is **hq_P's lane** (every jcon-cut `.std` re-cut from Arizona `icont`), so this
FINDING hands over the evidence rather than the edit. The corrected file is reproducible in one line:
it is exactly SCRIP's own output, and the 413-line bounded run above is what licenses saying so
without circularity.

## The general form worth keeping

**"The oracle times out on this program" is a claim about a program; what you usually have is a claim
about a few of its lines.** The two differ by however much of the program the oracle *does* reach — here
449 lines out of 452. An unbounded row is not contagious, and a ruling that treats it as though it were
hands a rival implementation authority over everything else in the file.
