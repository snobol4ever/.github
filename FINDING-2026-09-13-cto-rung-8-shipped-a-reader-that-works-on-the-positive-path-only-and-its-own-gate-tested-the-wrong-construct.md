# FINDING — RUNG 8 SHIPPED A READER THAT WORKS ON THE POSITIVE PATH ONLY, AND ITS OWN GATE TESTED THE WRONG CONSTRUCT

**seat** cto · **date** 2026-09-13 · **MODE** NONET · **lane** PROLOG completeness, the ISO ladder
**row** `prolog-the-negative-literal-fold-clamps-every-unbounded-integer-to-minus-llong-max`
**gate** `scripts/test_gate_pl_a_negative_unbounded_integer_literal_reads_as_its_own_value.sh` (4 arms, m3+m4, wired into `make test`)

## THE DEFECT

`prolog_parse.c`, the unary-minus fold: `-` followed by `TK_INT` built a `TT_ILIT` from `-num.ival` and
**never looked at `num.big`**. `num.ival` is what `strtoll` returned, and on an out-of-range literal `strtoll`
sets `ERANGE` and **clamps to `LLONG_MAX`**. So every negative integer literal wider than 64 bits read as
`-9223372036854775807`.

Measured on SCRIP `e62070ca8`, m3 and m4, against swipl 9:

| source | SCRIP before | swipl |
|---|---|---|
| `X = -9223372036854775808` | `-9223372036854775807` | `-9223372036854775808` |
| `X = -123456789012345678901234567890` | `-9223372036854775807` | `-123456789012345678901234567890` |
| `X is -123456789012345678901234567890 * 2` | `evaluation_error(int_overflow)` | `-246913578024691357802469135780` |

The first row is the one to read twice: it is off by one **at a value that fits perfectly well in an int64**.
A 30-digit literal silently becoming a 19-digit one announces itself eventually; an off-by-one at `INT64_MIN`
does not.

## WHY RUNG 8'S OWN GATE DID NOT SEE IT — THE REUSABLE HALF

Rung 8 landed the unbounded reader and its gate holds an arm for negation:

```prolog
N is -(123456789012345678901234567890), write(f(N)), nl,
```

That is the **functor** form. The parser takes `-(` through the `TK_LPAREN` branch and builds a `-`/1 term —
it never reaches the literal fold at all. **A NEGATIVE LITERAL AND A NEGATED LITERAL ARE TWO CONSTRUCTS**, and
the gate exercised the operator while the subject of the rung was the reader. Rung 8 was green, honestly
green, and half-built.

This is the ladder rule biting from an unexpected side. *One rung is one construct* is normally read as a
limit on how much a rung may claim. It is also a demand on the arm: **an arm that reaches the subject through
a different construct is measuring that other construct.** The surface syntax `-123` and `-(123)` denote the
same term and the ISO standard describes them together; they are two paths through our parser, and only the
path the arm actually walks is under test.

## THE CURE

At the fold, when `num.big`, build `$pl_big` over `'-'` prepended to the digit text. No new code in
`bignum.c` and no new IR kind:

- `rt_big_from_str` already reads a leading sign (`bignum.c:203`).
- `rt_big_norm` already narrows anything that fits back to `DT_I` (`bignum.c:78-84`), and `big_fits_i64`
  handles the `INT64_MIN` boundary correctly (`:69-76`, `u == (uint64_t)INT64_MAX + 1u → INT64_MIN`).

So `-9223372036854775808` lands as a **plain `DT_I`** and the 30-digit literal lands as `DT_BIG`, with the
representation decided by the value and not by which path read it. The `$pl_big` construction, which existed
once in `pt_primary`, is now a `pt_big_lit` helper called from both sites — a second copy of it was the
shape that produced this defect in the first place.

**`t.big` is set on the decimal path only.** Both radix paths (`0x…` and `16'FF…`) return early through
`make_tok` without touching it, so the digit text a big token carries is always pure decimal and safe to
sign. That also names the next defect precisely rather than vaguely: the radix forms clamp through `strtoull`
with **no big flag at all**, and are a later rung.

## MEASUREMENT

- Gate **PROVEN RED FIRST** on the clean origin build: 2 subject arms red in both modes, **2 control arms
  green in both modes**. After: 4 of 4 green.
- **Logtalk `unbounded` family: 70 → 82 of 111, BOTH MODES.** Rung 8's floor raised 70 → 82 in the same
  commit — a floor left at the old number is no longer measuring.
- Prolog ISO rung gates 1–8 green; `test_smoke_prolog` 5/5/5 across mode 2, 3 and 4; comment gate 0;
  `make preflight` 43 arms 0 red.

## THE ARMS DISCRIMINATE, THEY DO NOT TRIP

Taking hq_B's bar back into my own lane: the gate carries 2 subject arms and 2 control arms, and the controls
pass in **both** trees — the positive literal of the same width, the functor negation rung 8 already held, an
in-range negative, `INT64_MIN`'s positive neighbour, and small arithmetic. A future regression in the positive
reader or in `bignum.c` lights the controls; a regression in the fold lights only the subject. The gate
therefore says **which half moved**, which is the difference between an arm that survives being inherited and
one that merely tells the next reader that something changed.

## ⛔ WHAT THIS CURE MADE REACHABLE — NAMED, NOT ABSORBED

Until this landing **no Prolog source could produce `INT64_MIN`**, so the `LLONG_MIN` overflow guards written
in CTO-34 were unreachable from any program. They are reachable now and they are wrong. Five int64 operations
raise `evaluation_error(int_overflow)` where swipl promotes:

`abs(X)` · `-(X)` · `X * -1` · `X // -1` · `0 - X`, each from `X = -9223372036854775808`; swipl answers
`9223372036854775808` to all five.

Already correct and staying so: `sign(X)` = `-1`, `X + 1` = `-9223372036854775807`, comparison against `0`.
**The class is one value wide**: every one of the five is an operation whose *result* is exactly `+2^63`, the
unique integer one past `INT64_MAX`, reachable only from `INT64_MIN`.

**This is not a regression and the record should say so.** Before the cure those five answered from
`-LLONG_MAX` and were **silently** wrong; they are now **loudly** wrong. Nothing moved from correct to
incorrect, and the unbounded family reached 82 **with this class present**, so it is priced into that number.
Its own row: `prolog-five-int64-operations-raise-int-overflow-where-the-oracle-promotes-at-exactly-two-to-the-63`.

## ⛔ AN INSTRUMENT ERROR OF MY OWN, LOGGED BECAUSE IT IS THE KIND I KEEP FINDING IN OTHERS

The probe that characterised those five carried a `t(cmp, (...), nl)` line — three arguments to a `t/2` I had
just defined — and the run ended in `existence_error(procedure, t/3)`. The five readings above it were sound
and the sixth never ran. **A probe that dies after printing is the easiest kind of partial measurement to
report as a whole one**, because the output looks like output. I noticed only because the arity in the error
was not an arity I had written on purpose.
