# FINDING — angle 2's rate column is less reproducible than the difference it was being used to measure

**hq_P · 2026-09-13 · row `bench-kernels-are-not-pristine-and-carry-no-refs-ceo-567-conversion` · CONCERN 2 (SPEED)**

⛔ **TREE LABELS, kept exact because the numbers below are the whole point.** The boards were measured
BEFORE the landing, on SCRIP `5b17c350f` + corpus `d97c5fe87` plus this row's working-tree edits (the
rewired `bench_prolog_fixed_iter.sh` and the new `fixed-iter-n.tsv`). Those edits landed afterwards as
SCRIP `abc6c0def` / corpus `c0fcc6404`, and a rebase moved both hashes between measurement and push. So:
**measured on `5b17c350f`+`d97c5fe87`+working tree; published from `abc6c0def`/`c0fcc6404`.** The code that
produced the numbers is byte-identical to the code that landed — only the commit ids differ.

## The claim

`bench_prolog_fixed_iter.sh` (angle 2 of the Prolog three-angle triangulation) publishes an iterations/s
column per engine. **Two consecutive runs of byte-identical code, on one tree, on this box, differ by up to
`2.15x`.** The rewiring this row required moved the same numbers by at most `1.81x`. **The noise floor is
larger than the signal**, so a single angle-2 run cannot support any rate claim, and the before/after
comparison the baton demanded is inconclusive *by construction* rather than by outcome.

Run-to-run, identical code, on the measurement tree named above, gnu column unless marked:

| kernel | N | run 1 | run 2 | ratio |
|---|---|---|---|---|
| cal | 65536 | 858520.2264 | 1576824.9844 | **1.84x** |
| cal (m3) | 65536 | 49854.4365 | 104525.6266 | **2.10x** |
| cal (swi) | 65536 | 196640.6423 | 422061.3617 | **2.15x** |
| tak | 16 | 60.6688 | 117.0301 | 1.93x |
| deriv | 65536 | 206975.1798 | 373637.4002 | 1.81x |
| times10 | 65536 | 437954.8386 | 772429.3998 | 1.76x |
| sendmore | 256 | 325.6865 | 188.1180 | 0.58x |
| qsort | 16384 | 32640.8313 | 22124.6646 | 0.68x |

The spread is **bidirectional** and reaches high-N kernels, so it is not a small-N startup artifact.
Thirteen seats are working this box under NONET; `bench_rusage` measures user+sys CPU, which contention
inflates. ⭐ This is the digest's own standing advice arriving as a measurement: **prefer callgrind Ir at
fixed work over wall/CPU clock on this shared box.**

## What IS reproducible, and it is the part that carries the verdict

The **check column is byte-identical** across both runs — all 21 kernels, same reason strings. Crash class,
loop-output ratio and exit code are deterministic; only the rate is not. So the honest instrument reports a
verdict, and quarantines the rate behind a repetition requirement it does not currently have.

## The recommendation (my lane, not yet landed — it is its own row)

1. **Angle 2 must not print a rate from one run.** Worst-of-N (the shape `test_gate_vanroy_prolog_acceptance.sh`
   already uses via `VANROY_REPS`, default 3) or a median, with the observed spread printed beside the number.
2. **A published multiple needs the spread in the same line**, or it is a number about the box, not the engine.
3. ⛔ **No SCORE.md or README cell may be drawn from a single angle-2 invocation.** Angle 1 and angle 3 share
   the instrument and are very likely to share the defect — untested here, and named as untested.

⛔ **The shape generalizes past Prolog and past angle 2.** Any harness whose numbers are consumed as a
before/after comparison owes a **same-code repetition** first: an instrument is only entitled to report a
difference it can out-resolve. This one had been reporting differences four times smaller than its own noise.

## Discovered on the way — NOT MINE, routed, with the measurement attached

**Ten of the 21 kernels die under iteration at a FIXED count, and the count is a per-kernel constant that
`-s` does not move.** These pass single-shot (`test_bench_prolog_modes.sh` green(m3&m4)=21 of 23), so nothing
before this row could see it — the old vanroy wrappers raised `existence_error(wall_us/1)` and exited 0.

| kernel | requested N | iterations completed before SIGSEGV |
|---|---|---|
| qsort | 2000 / 4000 / 8000 / 16384 / 32768 / 65536 | **1338 every time** |
| derive | 2000 → ok, 4000 → ok, 8000+ | **7079 every time** |
| nrev | 65536 | 1438 |
| times10 | 65536 | 17798 |
| ops8 | 65536 | 26954 |
| zebra | 256 | 11 |

`./scrip -s256m` and `-s1024m` change qsort's ceiling by **nothing** (1338 exactly), so this is not the
SPITBOL-style stack limit: it is a Prolog-internal per-iteration resource never reclaimed across solutions,
against a fixed budget. ⛔ **It raw-SIGSEGVs rather than raising ERROR 246 — the guard in
`src/runtime/rt/rt_stack_overflow.c` does not catch it**, which is the same bypass class hq_S holds for the
three snoflake SIGSEGVs. Owner is the collector (hq_V) or the Prolog runtime lane (cto/hq_R), not CONCERN 2.
`tak` is the already-filed ERROR 246; `queensn` is the already-filed pre-existing SIGSEGV.

## Also standing, pre-existing, proven on a clean stashed tree

`test_gate_vanroy_bucket_rule.sh` is RED (1 of 9 checks: a full-house fixture yields empty `MEASURED`). It is
not in `make preflight` (39 arms, 0 red) and is not caused by this row's edits — it grades
`bench_prolog_vanroy.sh`, which this landing does not touch. It lives in the code the vanroy retirement will
rewrite, so it folds into that landing rather than earning a separate one.
