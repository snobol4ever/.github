# FINDING — m3 executes 3x m4 on beauty; the benchmark harness cannot be instrumented at all; and SCRIP already beats SPITBOL 4.4x on integer loops

**Session:** 2026-08-22 HQ, background discovery agent (HQ LAW 13 as amended). **RT_OPT=-O0**, callgrind whole-process Ir, oracle `sbl -bf`. Compile isolated by subtraction, never by callgrind toggles.

## ⛔ (1) THE BENCHMARK CORPUS CANNOT BE MEASURED UNDER ANY SLOW INSTRUMENT — FIFTH INSTRUMENT DEFECT

`corpus/benchmarks/snobol4/*.sno` are **wall-clock-budgeted** via `harness.inc` — "FIX THE TIME, COUNT THE ITERATIONS", running batches until `ZBUD`=500 ms elapses. **Under callgrind every arm self-shrinks its workload to fit 500 ms of *slowed* time, so all arms return near-identical Ir and every ratio collapses to ~1.0** — a full, plausible, entirely false table. This is the "non-empty is not alive" class again, in the timing dimension. All kernel numbers below are **fixed-work variants** (harness removed, N pinned), reproducing the oracle's exact check value; they are **not** the shipped benchmark.

## (2) MEASURED MATRIX

| Ir | beauty | arith_loop N=32M | array_sum N=8k | eval_fixed N=1.2M |
|---|---|---|---|---|
| C1 compile (TEXT) | 13,225,093,273 | 14,958,714 | 23,569,751 | 14,733,390 |
| C2 m4 run | 4,833,116,241 | 3,524,318,959 | CRASH @2,532,473,578 | 2,914,337,205 |
| C3 m3 total | 27,729,458,120 | 3,532,860,690 | CRASH @2,592,270,952 | 2,929,668,580 |
| C4 oracle `-bf` | 806,142,425 | 15,653,271,464 | 4,297,176,545 | 1,772,136,821 |

## ⛔ (3) m3 ≡ m4 IS VIOLATED ON THE FLAGSHIP PROGRAM

Kernels hold: arith_loop −0.18%, eval_fixed +0.02%, array_sum +1.4%. **beauty does not: m3 run-only 14,504,364,847 vs m4 4,833,116,241 = 3.00x (ESTIMATED by C3−C1).** Independently corroborated by native wall clock: m3 2.39 s − compile 1.31 s = 1.08 s vs m4 0.42 s = **2.6x**. C1 (TEXT, writing 11.7 MB of asm) likely *over*states BINARY compile, so **the true gap is ≥3x**. m3 ≡ m4 is a stated design invariant; on beauty it does not hold.

## ⭐ (4) SCRIP ALREADY BEATS SPITBOL 4.44x ON INTEGER LOOPS

m4 run vs oracle, MEASURED: **arith_loop 0.225x — SCRIP 4.44x FASTER**; eval_fixed 1.64x slower; **beauty 5.99x slower**. Median 1.64x slower, but the spread is **27x**, so the median is meaningless. **SCRIP wins integer/loop work and loses on beauty's pattern-and-string work.** That is the first measured evidence that compiled-beats-threaded is achievable here — and it localises where it is not yet.

## (5) COMPILE IS HALF OF MODE 3 ON REAL PROGRAMS

C1/C3: beauty **47.7%** · arith_loop 0.42% · eval_fixed 0.50% · array_sum 0.91%. Native: 1.31 s of 2.39 s = **55%**. Compile cost scales with **program size**, not workload — invisible on 10-line kernels with huge loops, **half the cost on a real program**.

## ⛔ (6) RETRACTION — THE 23.47% ORACLE-INSTRUMENTATION FIGURE IS WRONG AT RUNTIME

`SPL_PM_TRACE` set vs unset: **+622 instructions constant** on arith_loop and eval_fixed, +608 on array_sum (≈0.000004%). Only beauty shows real cost: 885,238,231 vs 806,142,425 = **+9.81%** (MEASURED). **The 23.47% was static code share, not dynamic cost, and is WITHDRAWN.** Consequences: the instrumentation is pattern-matcher-resident, not global; and the earlier "equalized 2.1x" — which stripped 23.47% from the oracle — must be recomputed (SPITBOL real ≈ 734 M, not 608 M). ⛔ The related claim that *"SCRIP's pattern engine already costs less than SPITBOL's, 206 M vs 255 M"* rested on attributing `zpm*` to instrumentation and is **WITHDRAWN pending re-measurement**.

## (7) INCIDENTAL DEFECT

`array_sum` SIGSEGVs **deterministically under valgrind in both modes** (at 2.532 G / 2.592 G Ir) while running correctly natively 3/3. A 32x larger valgrind stack crashed at the **identical Ir**, so it is not stack exhaustion — it looks like reliance on memory behaviour valgrind does not reproduce. The oracle runs the same program cleanly.
