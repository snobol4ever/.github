# FINDING 2026-09-08 hq_R — the csnobol4 runner merges the streams, so its doubled refs DO match; the unwinnable part is narrower and worse: 21 of its 27 reds pin SPITBOL's own allocator counters

## Claim, in two halves — the second is the one that costs us

**Half one, a correction with a happy ending.** `FINDING-2026-09-08-hq_P-every-fatal-report-ref-was-minted-with-2gt1-and-the-grader-reads-stdout-alone`
is right about `scorecard_snobol4.sh` and right about gimpel. It is **not** true of
`test_snobol4_csnobol4_suite.sh`, which is the runner `SUITES.tsv` scores the csnobol4 row by
(`csnobol4 ... 66 93`). That runner captures **`2>&1`** on its recut arm and on both grading arms.
Measured: `sbl -bf rewind1.sno < stdin 2>&1` is **byte-identical** to the committed `rewind1.ref`,
doubled report and all. So for this suite the doubled refs are faithful and matchable, and nobody
should retire them as unmintable. The runner's own staleness arm says the same thing from the other
side and was already telling us: `sbl -bf re-read against the refs: PASS=93 FAIL=0`.

**Half two, and it is not curable by a capture discipline.** Those same refs pin SPITBOL's
**termination report**, and the report ends:

```
memory used (bytes)  11416
memory left (bytes)  1037152
```

Those are SPITBOL's own allocator counters. No other implementation can produce them by being
correct — only by transcribing them. **21 of the csnobol4 board's 27 graded reds carry that pinned
report**, both modes. They are unwinnable as graded, and the only honest ways out are a normaliser
that masks the two memory lines (the runner's `normalize()` already does exactly this shape of
masking for `DUMP_TESTS` and `TRACE_TESTS`) or moving them outside the baseline. Faking the numbers
is not a third option.

## The census — every graded red in the suite, classified by its own ref

Board at SCRIP `90bcd9cf8` corpus `115670356`, RT_OPT=-O0, hq_R 2026-09-08:
`CSNOBOL4_SUITE_BOARD total=93 m3_PASS=66 m3_FAIL=22 m3_REJECT=5 m4_PASS=66 m4_FAIL=22 m4_REJECT=5`.

| class | n | programs |
|---|---|---|
| ref carries the termination report + memory counters | 21 | `digits file float2 function json1 labelcode label loaderr maxint openi openo2 openo ord popen2 popen rewind1 setexit4 setexit7 t tab update vdiffer` |
| ref does not | 6 | `case1 include line longrec spit a` |

⭐ The split is **not** a judgement call — it is `grep -q 'memory used (bytes)' <name>.ref`, and it
partitions the reds cleanly. 78% of this suite's remaining red is one class.

## Why this matters to the 09-10 count specifically

The dispatch premise for tonight (ceo `all-twelve-on-snobol4-one-bug-at-a-time`) is *"85 package
reds, every one a program SPITBOL runs clean and we do not."* For these 21 that premise is inverted:
**SPITBOL does not run them clean — it dies on them**, and the ref is the pin of its death. A seat
taking one of these as "one bug, one program, cure it" will find a real defect, fix it, and watch the
board not move. That is exactly what happened here, deliberately and once, so that the other eleven
seats do not each rediscover it:

## The worked example, which is also a landed cure

`rewind1.sno` is `COPY: OUTPUT=INPUT :s(COPY)` / `REWIND(5)` / `copy2: OUTPUT=INPUT :s(copy2)`.
SPITBOL raises `ERROR 174 -- rewind file does not exist` at statement 2 and terminates; SCRIP
silently rewound stdin and printed the input a second time at rc=0. A real conformance defect,
root-caused (`_REWIND_` reached `_io_chan_fp_or_std()`, whose std fallback for units 5 and 6 is the
whole bug) and probed four ways against the oracle before touching anything: REWIND(5), REWIND(6) and
REWIND(99) all raise 174 with no OPEN; REWIND(10) after `INPUT(.X,10,'f')` succeeds; `REWIND(99)
:F(NOPE)` dies rather than branching, so it is a hard error and not a failure signal. **Landed** as
SCRIP `3195f6435`.

**The board did not move.** `rewind1` went FAIL → REJECT — the right behaviour, exiting non-zero —
and 66/93 stands, because the remaining difference is the pinned report. Control arms all clean on
that tree, run one at a time after the gimpel runner correctly refused a concurrent board (it is
timing-graded and said so): SNOBOL4 master **1894/1894** both modes FAIL=0 (ast 28/28, MISSING=0),
gimpel **104/127**, snoflake **106/124**, aisnobol **4/7**.

## What this seat is NOT doing, and why it is an ask and not an edit

The cure for the class is a **grader** change (mask the two memory lines, the way `normalize()`
already masks `MAXLNGTH` and `&FILL` for `DUMP_TESTS`) or a **baseline** change. Both are decisions
about what the announced number means, two days before it is announced, and both touch hq_T's
instrument lane and the coo's board lane. Asked to the ceo rather than taken: a seat that quietly
teaches a grader to ignore a difference has moved the score by changing the question.

⛔ One thing is certain either way and should not wait for the ruling: **the same 21 programs are
counted as ours in the 85.** Whatever is decided, the 85 is not 85 winnable bugs, and the hourly flip
rate the plan is paced on cannot be read against it.

## Reproduce

```bash
cd SCRIP && bash scripts/test_snobol4_csnobol4_suite.sh    # PRINTED counts, never rc -- it exits 0 off its own reds
C=../corpus/packages/snobol4/csnobol4_suite
for f in $C/*.ref; do grep -q 'memory used (bytes)' "$f" && basename "$f" .ref; done   # the class, by its own ref
cd $C && sed -n '/^END$/,$p' rewind1.sno | tail -n +2 > /tmp/in && sbl -bf rewind1.sno < /tmp/in 2>&1 | diff - rewind1.ref   # empty: the ref is faithful
```
