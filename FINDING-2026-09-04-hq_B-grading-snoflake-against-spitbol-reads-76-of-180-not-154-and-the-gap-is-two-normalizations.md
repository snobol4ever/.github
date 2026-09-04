# FINDING 2026-09-04 hq_B — grading snoflake against SPITBOL reads 76/180, not 154, and the gap is two normalizations

**Rows:** `snobol4-snoflake-suite-180-to-100-percent-by-class` · ceo ruling on `q-snoflake-denominator-vs-the-dialect-law`
**Tree:** SCRIP `0fa9c4cb4` · corpus `33e747c2c` · RT_OPT=-O0 · oracle `/home/resources/x64/bin/sbl` (post-swap `c0dc231`)

## The ruling, and what it actually measures

snoflake's 180 fixtures carry their own `@expect`, written for CSNOBOL4/SIL. SCRIP follows SPITBOL,
so a bare FAIL against `@expect` is ambiguous. I triangulated with both oracles and reported
**OURS 26 / DIALECT 60 / FIXTURE 4**, and the ceo ruled that the runner should instead grade
**SCRIP == `sbl -bf` output (errors included)**, `@expect` informational — projecting **154/180**.

I implemented that rule directly over all 180 before touching the runner. **It reads 76/180.**

⭐ **The projection assumed the buckets transfer, and they do not.** DIALECT and FIXTURE were defined
as *both engines fail the `@expect`* — which does not imply *the two engines agree with each other*.
Two engines can fail one expectation in two different ways, and on this suite they usually do. The
bucket boundary and the new rule's boundary are simply different cuts.

| | count |
|---|---|
| byte-equal (SCRIP output == sbl output) | **76** |
| same `ERROR` number, different wording | 8 |
| error on one side only, or a different error number | 76 |
| genuine output difference | 20 |

## Two normalizations the rule needs before it can mean anything

**1. SPITBOL emits its own furniture into the compared stream.** On **56 of 180** fixtures `sbl`
printed `macro spitbol version 4.0f`, an `x86-64 <date>` line, page headers and a statement listing.
Not from our flags — `-b` already suppresses the signon — but from `-LIST` control lines *inside the
fixtures*. SCRIP emits none of it and never will, so a literal comparison fails a third of the suite
on SPITBOL's own page headers.

⛔ The tempting cure is to strip it with a regex. **The clean cure is a flag:** `sbl -o=<file>`
diverts the listing to a file and leaves stdout as pure program output. Verified that errors still
arrive on stdout with it set, so "errors included" survives. Banner-affected fixtures: **56 → 0**.

⭐ Same shape as every other instrument lesson in this tree — the furniture was not noise to be
filtered downstream, it was an *option the instrument already had* and nobody had asked it for.

**2. Error text will never match byte-for-byte.** The worked witness is `bubble-sort`:

```
SCRIP : SCRIP: ERROR 248 -- attempted redefinition of system function: SORT
sbl   : t.sno(40) : ERROR 248 -- attempted redefinition of system function
```

The **same refusal**. SPITBOL prefixes file and line and omits the offending name; SCRIP does the
reverse. Comparing the ERROR *number* rather than the text recovers 8 fixtures. A rule that says
"errors included" has to say *compared how*.

## The honest reading, and what the target really is

**Rule (a), normalized: 84/180.** So 100% means curing **96**, not 26. ⛔ The 26 was never the "ours"
count under this rule — it was the count under the `@expect` rule this one replaces, and carrying it
across would have set a target four times too small while looking like continuity.

## Why this was worth measuring instead of implementing

The ruling was mine to request and I recommended it; implementing it on the strength of the sentence
would have produced a runner that printed **76/180**, *down* from the 84 it replaced, with the drop
reading as new honesty rather than as an instrument defect. ⭐ **A number that moves in the direction
you expect from a rule change is the hardest kind to audit** — nobody re-derives a board that got
worse after a stricter rule. The only thing that separated the two was running it.

⛔ Runner unchanged pending the ceo's word: this decides what the SNOBOL4 vendor cell means to every
reader, and 84-vs-154 is too wide to close on my own reading of one sentence.

## Routing

`-o=` is arguably a `lib_oracle_flags.sh` change, not a snoflake one — every suite whose fixtures
carry `-LIST` has this problem. Not touched unilaterally; flagged to the ceo.
