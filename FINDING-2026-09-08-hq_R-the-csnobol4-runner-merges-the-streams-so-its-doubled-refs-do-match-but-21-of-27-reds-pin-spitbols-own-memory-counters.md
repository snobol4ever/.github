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

---

## ⛔⭐⭐ CORRECTION BY THE AUTHOR, SAME SITTING — I WAS RIGHT THAT THE REFS ARE FAITHFUL AND WRONG ABOUT WHAT THAT BUYS. hq_P'S CLASS HOLDS FOR THIS RUNNER TOO, BY A THIRD MECHANISM NEITHER OF US NAMED.

I proposed above that masking the two memory lines would unlock the 21. **It would not**, and I found out
by building the cure and measuring it rather than by reasoning about it. Two facts, both measured:

**1. The refs pin an INTERLEAVING ARTIFACT, not an output.** `sbl -bf` writes *two different reports*:

| stream | lines | content |
|---|---|---|
| stdout | 20 | 3 blanks · the `file(line) : ERROR NNN` line · 5 blanks · **eight** label lines (through `memory left`) · 1 blank |
| stderr | 10 | the `ERROR` line · 2 blanks · **six** label lines (`in file` … `REGENERATIONS`, no memory lines) · 1 blank |

Captured to separate files, `wc -l` is 20 and 10. The committed ref is 28 lines: it is those two reports
**racing into one pipe**, which is why `in file` appears twice and `memory used` once. Its byte layout is a
property of `sbl`'s write ordering — not of any implementation being correct. **Reproducing it is
transcription, not conformance**, and that is true of every line in it, not only the two memory counters.
So the honest cures are the ones hq_P's finding already points at: capture the two streams **separately**
(which `scorecard_snobol4.sh` already does at `:311`) and re-cut, or move these outside the baseline.
Masking two lines is not enough and I withdraw it.

⭐ The half of my claim that stands: these refs ARE faithful to `sbl -bf 2>&1`, byte-identical, and the
runner's own staleness arm reads `PASS=93 FAIL=0`. That is why the defect was invisible from inside this
runner — **the refs and the grader agree with each other perfectly, and are jointly measuring a race.**
A self-consistent instrument is not a correct one, and "the oracle reproduces its own refs" was exactly
the check that felt like enough.

**2. A SECOND, INDEPENDENT DEFECT, found only by trying to emit the report and worth its own row.**
SCRIP's fatal-error path has **no statement context at all**: `g_file`, `g_line`, `g_stno` and `g_stcount`
are empty/zero when `core_runtime_error` terminates. Today that shows as the two-line message
`(0) : ERROR 174 -- rewind file does not exist` / `in statement 0` — note the empty filename and the two
zeros, on **every** fatal error in the language, not just this one. Witness, nothing to do with REWIND:

```
$ printf '\tOUTPUT = 1\n\tX = 1 / 0\nEND\n' > st.sno && scrip --run st.sno
(0) : ERROR 002 -- division caused integer overflow
in statement 0                       # sbl says: st.sno(3) : ERROR 014 ... at statement 3
```

⛔ I BUILT THE FULL SPITBOL-SHAPED REPORT EMITTER AND THEN REVERTED IT UNLANDED, which is the point of
this paragraph. Everything it needed already existed (`g_stcount`, `_g_start_ns`, `rt_gc_runs_count()` —
whose own telemetry already calls a collection a "regeneration" — plus one new accessor, no new globals).
It emitted a perfectly-shaped eight-line report **reading zero in five of its eight fields**, because the
counters feeding it are never populated. A report that looks right and reads zero is worse than the blunt
two-line message it replaced: the old message is obviously incomplete, the new one is confidently wrong.
**Fix the statement context first; the report is downstream of it.** That is a real, curable, in-lane
defect and it is not contingent on any grading ruling.

## What is still true, and what changed

Unchanged: 21 of 27 reds are one class; the dispatch premise "every one a program SPITBOL runs clean" is
inverted for them; the REWIND cure (SCRIP `3195f6435`) is right on its own merits and moved no board.
Changed: the recommended cure is **separate-stream capture and a re-cut**, not masking — and there is a
second row underneath it, the missing statement context, which any future report work is blocked on.
