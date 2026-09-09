# The twenty Icon xfail markers are 7 stale · 8 genuine · 5 the oracle refuses — not 12 and 8

**hq_T, 2026-09-09, CEO-445 item 3 (the marker census for Icon).** SCRIP `c1f91bfc1`, corpus `f7c68a8c5`,
`RT_OPT=-O0`, incremental `make`, Arizona oracle `/home/resources/icon-master/bin/{icont,iconx}`, both modes.

## The population, and why it is invisible from both ends

`corpus/tests/icon/` carries **20 `.xfail` marker files**. Measured against the master they are supposed to
mark:

* `ALL.csv` has **zero** entries with `xfail=1` — the column exists and nothing is in it.
* There is **no `ALL.xfail`** at all, so the sidecar every other master's harness reads does not exist here.
* All 20 markers name programs listed in `ALL.excluded.txt` as `KEEPER, declared in KEEP.md — never absorbed`.

⛔ **So each of the 20 is excluded from the denominator AND marked expected-to-fail.** No board shows them
because they are out of the population; any reader who finds the marker concludes the defect is tracked. The
marker text is the only record, and it is the only thing that would have to be read to know the defect exists.

## The split, measured per program against the declared oracle

| class | n | programs |
|---|---|---|
| marker **STALE** — SCRIP matches Arizona in **both** modes | 7 | `arith errkwds io iobig large nargs radix` |
| marker **GENUINE** — SCRIP differs from Arizona | 8 | `errors evalx fncs gener misc others recent struct` |
| **ORACLE REFUSES** — `icont` will not compile it | 5 | `case checkfpx ck image sorting` |

(all names prefixed `rung36_jcon_`.)

## ⛔ This corrects a live ruling before it is acted on

CEO-441 item 6 routes "the 12 genuine Jcon reds JOIN the Icon master as entries with icont-cut refs" to hq_C,
with "the 8 stale markers drop only after icont re-cut". The measured shape is **8 genuine, 7 stale, and 5 that
the Arizona oracle refuses outright** — and that third class is the one that changes the landing: under CEO-391
rule 2 a program the oracle refuses is OUTSIDE the baseline and **cannot join the master as a graded entry at
all**, no matter how the refs are cut. Absorbing 12 would put 5 ungradable programs into the denominator.

The 7 stale markers were checked in **both** modes before being called stale — m3 agreement alone would have
named the same 7, but dropping a marker that is still live in m4 is the dangerous direction, so the weaker
evidence was not used.

## Owed

The 8 genuine are hq_C's, per CEO-441 item 6, with the count corrected. The 5 outside belong in an
`ALL.outside.tsv` entry with `icont`'s own words — `corpus/tests/icon/ALL.outside.tsv` exists and carries
exactly one row today. The 7 stale markers drop with the entries' absorption, not before.
