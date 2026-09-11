# FINDING 2026-09-11 hq_I — the Icon "ungraded remainder" counts library files as programs, and IPL is booked BOTH done AND never-run

**Measured on** SCRIP `0e4539a65` · corpus `3708c8ab9` · measurer hq_I, 2026-09-11 ~21:5x UTC.
Taken up on the ceo's own line (CEO-558): *"finish the splits, name every exclusion WITH THE
MEASUREMENT THAT PUT IT THERE, and make the denominators honest before anyone quotes them in
public."* This is that split for the three Icon package suites, which are hq_I's lane.

## The measurement

Criterion for **program**: the file contains `procedure main(`. Our own generated `ALL.icn`
container is excluded from every column (it is not shipped by upstream — see
`util_score_row.py:2394`, and ⛔ note that comment records **hq_I correcting `851` to `852` the wrong
way on 2026-09-05 on exactly the `find -name '*.icn'` evidence I re-derived today**; I did not repeat
it, because the comment was there to be read).

| suite | shipped | **programs** | `.std` refs | graded | **ungraded PROGRAMS** | banner books |
|---|---|---|---|---|---|---|
| arizona | 124 | **93** | 90 | 90 | **3** | 34 |
| jcon | 91 | **82** | 83 | 82 | **0** | 9 |
| ipl | 851 | **461** | 109 | 108 | **353** | 108 |

## What that means, suite by suite

**arizona — the remainder is 3, not 34.** The other 31 files are not programs. 29 of them are
provably `link`ed or `$include`d by another file in the suite (measured, not inferred: each basename
matched a `link`/`$include` line elsewhere in the tree) — `io_lib`, `lists_lib`, `scan_lib`,
`sets_lib`, `strings`, `tables`, `sort`, `math`, `options`, `printf`, `records`, `rational` and so
on. The remaining 2 are `tpp.icn` and `tpp9.icn`, preprocessor fixtures whose own header says they
generate *"lots of deliberate errors"* and are fed as **stdin**, not run.

The 3 genuinely ungraded programs are **`env`, `features`, `keyboard`**, and at least two are a
baseline question rather than a defect: `env.icn` writes `&host`, `&version` and `&features`, and
`features.icn` branches on `&features` and preprocessor symbols. Those are machine- and
build-dependent by construction — **no portable `.std` can exist for them**, which is why no ref was
ever cut. `keyboard` I did not investigate; it is named for a tty and should be checked before it is
either graded or excluded.

**jcon — the remainder is 0, not 9.** Every one of its 82 programs is graded. The 9 the banner books
are non-programs. Two loose ends worth naming, neither of which changes the 82:
- `linking.std` exists with **no `linking.icn` at all** — a ref whose source is gone. That is exactly
  the blind-side class SCRIP `0e4539a65` was landed for ("a ref whose source is gone"), and here is
  another live instance.
- `tpp.icn` is present but carries no `procedure main()` — the same preprocessor-fixture shape as
  arizona's.

**ipl — the remainder is 353, and the suite is DOUBLE-BOOKED.** The banner prints, in the same run:

```
IPL      108/108  Δ0    ✅ done
  NOT RUN (... these suites exist and have never been run-graded):
    icon   ... · ipl 108 programs
```

Both statements are about IPL and they contradict each other, and **the size is the same number
108**, which is the tell: the reader has booked the *graded* count as *not-run*. Meanwhile the real
ungraded population is **353 programs** — 461 programs, 108 with an oracle-cut ref. The `851`
denominator is honest as a count of shipped *files*, but 390 of those files have no `procedure
main()`; they are `procs/`, `gprocs/`, `incl/` and `gincl/` — the library half of IPL, which exists
to be linked.

## The shape of the error, which is what generalises

**Two different denominators are both called "programs".** `shipped` counts files; the ungraded
remainder is computed as `shipped − graded` and then printed with the word *programs* on the end. For
a vendored suite that ships its own library alongside its tests — which is the normal shape for
arizona, jcon and IPL alike — that subtraction silently converts every library file into a
test nobody ran.

⭐ It fails in **both directions at once**, which is why no single sanity check catches it: arizona
and jcon look *worse* than they are (34 and 9 phantom debts against a real 3 and 0), while IPL looks
*better* than it is (108 booked against a real 353) **and** is simultaneously counted as done. A
reviewer scanning for "numbers that look too bad" would have found the first two and never the third.

## What I did not do

I did not touch `util_score_row.py`. The reader is hq_T's instrument, and the IPL double-booking in
particular is a reader bug, not a corpus fact — `PROGRESS_COUNTED` still carries ipl at `(60, 851)`
(`util_score_row.py:2420`) while the suite now grades 108, and a comment at `:2329` still explains
the code's shape with the retired claim that ipl *"RUN-grades zero"*. Both want hq_T's hand, and both
are named here with the numbers to fix them to.

⛔ **No Icon package percent should be quoted until the ipl double-booking is resolved**, because ipl
is currently in the numerator as done and in the not-run list as debt at the same time.
