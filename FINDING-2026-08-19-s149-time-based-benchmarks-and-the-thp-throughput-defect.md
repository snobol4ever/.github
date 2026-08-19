# FINDING 2026-08-19 s149 — THE BENCHMARK SUITE MEASURED THE WRONG VARIABLE, AND FIXING IT EXPOSED A 2.26x THROUGHPUT DEFECT HIDING UNDER TRANSPARENT HUGE PAGES

**Seat:** web (Claude Opus 5). **Goal:** `GOAL-SNOBOL4-100.md` (benchmarks suite, scorecard weight 10).
**Lon in-chat, verbatim in substance:** *"Work in benchmarks folder for SNOBOL4 and get TIME based measurements of iterations, NOT iteration based measurement of TIME."*
**Baseline:** SCRIP `f80c3f4d` · corpus `a51c7d25` · .github `b741e60f`. No codegen touched — this rung is instrument + corpus only.

---

## 1. THE INVERSION, AND WHY IT WAS OWED

The legacy family (`corpus/benchmarks/snobol4/*.sno`, 23 programs) fixes the loop count and prints the
elapsed ms. Three measured defects follow from that shape alone:

| defect | measurement |
|---|---|
| **RESOLUTION** | `TIME()` is integer milliseconds (manual p.244). `arith_loop` at 1,000,000 iterations reads **`10`** on scrip and **`10`** on `string_concat`. One significant digit — a 10% regression is invisible by construction. |
| **UNBOUNDED WALL COST** | The suite has no time budget; a slow engine takes arbitrarily longer on a fixed count. `var_access` (10M iterations) already costs 327 ms on scrip and would cost seconds on a slower arm. |
| **DEAD REFS** | ⛔ **All 23 programs print a nondeterministic ms delta while all 23 sibling `.ref` files hold a deterministic result** (`iterations: 1000000`, `result: 60000012`, …). No `.ref` can ever match. The runner's filter is `grep -vi 'ms:'`, which strips only `roman.sno`'s line — the other 22 emit a **bare number** that the filter does not catch. The benchmark suite's correctness oracle is inert. |

Inverting it — **fix the TIME, count the ITERATIONS** — repairs all three at once: the reported quantity
becomes a throughput directly comparable across engines, the suite's wall cost becomes
`budget x programs x engines` by construction, and a deterministic check phase can run first so the
`.ref` becomes a live oracle again.

## 2. WHAT LANDED

- **`SCRIP/scripts/gen_timed_bench_snobol4.sh`** — ONE AUTHORITY for the harness shape. Emits 12
  self-contained programs (house rule: `corpus/benchmarks/snobol4/README.md`) from a kernel table.
  Three phases per program: **CHECK** (fixed small count → deterministic `check:` line, ref-diffable) ·
  **CALIBRATE** (double the batch until one batch spans a TIME floor) · **MEASURE** (batches to a
  deadline, iterations counted).
- **`corpus/benchmarks/snobol4/timed/`** — 12 `.sno` + 12 oracle-baked `.ref` + `NOISE-FLOOR.tsv`.
  ⛔ Placed in a SUBDIRECTORY deliberately: the legacy runner globs `"$B"/*.sno`, which does not
  descend, so the 23 legacy programs and every artifact keyed to them are untouched. Blast radius zero.
- **`SCRIP/scripts/test_bench_snobol4_timed.sh`** — 3-engine runner (sbl / m3 / m4), reports iters/sec.
- **`SCRIP/scripts/bake_noise_floor_snobol4_timed.sh`** — measures and records the per-row noise floor.

**The calibration phase is time-based too, and it is load-bearing.** Measured on scrip, a batch of 4096
under-reports throughput by **13%** (63,312/ms vs ~73,000/ms) because the per-batch clock read is not yet
amortized. Guessing a batch size as an iteration count reintroduces the very error being removed; the
batch is derived from a ms floor instead. Rate is computed against ACTUAL elapsed, so deadline overshoot
(≤ one batch) does not bias it.

**Harness soundness, verified before any number was trusted:** K-independence (rate flat for calibration
floors 2–80 ms) and budget-independence (rate flat for budgets 250/500/1000/2000 ms, ≤2.5% spread).

## 3. ⛔ THE s148 INSTRUMENT ERROR REPEATED ITSELF IN THIS SEAT — AND WAS CAUGHT

s148 convicted the md5 blast-radius sweep for not knowing its own noise floor. **This seat committed the
same error in a subtler form and nearly shipped it:** the floor was measured on ONE kernel
(`arith_loop`, cv 1.3%) and was written into the runner header as a GLOBAL *"~4%"* constant. It is false.
Measured per row, dispersion runs **0.2% .. 34.6%**:

| row | sbl cv | m3 cv (shipping arm) |
|---|---|---|
| `arith_loop_t` | 0.8% | 1.4% |
| `func_call_t` | 1.2% | 3.8% |
| `string_manip_t` | 0.3% | **10.6%** |
| `string_pattern_t` | 0.7% | **22.8%** |
| `array_sum_t` | 0.8% | **34.6%** |
| `table_access_t` | 2.0% | **26.9%** |

**The noise floor is a property of the (KERNEL, ENGINE, THP-arm) triple, not of the harness.** It is now
baked per row in `NOISE-FLOOR.tsv` and printed by the runner as `min-det = 3*cv`. In the shipping arm
`table_access_t` m3 has a min-detectable difference of **80.7%** — that row could not have detected a 2x
regression, while looking exactly like a working benchmark. **The oracle (`sbl`) is tight everywhere
(cv 0.3–2.2%), so the dispersion is SCRIP's, not the container's.**

## 4. ⛔⭐ THE DEFECT THIS EXPOSED — TRANSPARENT HUGE PAGES COST UP TO 2.26x ON THE ALLOCATING PATH

`corpus/benchmarks/snobol4/README.md` already warns that `table_churn` must be measured with
`SCRIP_NOHUGE=1`. **That warning generalises to every allocating benchmark, and it is not merely a
measurement hygiene note — THP is costing real throughput.** Both arms, 5 reps, reproduced across two
independent bakes:

| row (m3) | `SCRIP_NOHUGE=0` (ships) | `SCRIP_NOHUGE=1` | gain | cv 0 → 1 |
|---|---|---|---|---|
| `table_access_t` | 2,675/s | **6,042/s** | **2.26x** | 26.9% → 2.2% |
| `array_sum_t` | 4,713/s | **5,468/s** | 1.16x | 34.6% → 2.9% |
| `string_pattern_t` | 2,877,871/s | **3,629,495/s** | 1.26x | 22.8% → 0.6% |
| `string_manip_t` | 2,682,541/s | 2,413,916/s | 0.90x | 10.6% → 1.6% |
| scalar rows (`arith_loop`, `func_call`, `op_dispatch`, `var_access`, `fibonacci`) | — | — | ~1.00x | already tight |

The signature is exact: **only rows that allocate are affected**, and for them THP is simultaneously a
throughput loss and the entire source of dispersion. Turning it off makes every row gate-able
(max cv across all 24 scrip rows: **3.9%**). ⛔ **NOT ROOT-CAUSED HERE** — this is minted and routed,
not fixed. The obvious suspect is the RBX heap-top / allocation frontier faulting 2 MiB pages it does not
fill, but that is a hypothesis, not a measurement, and the END-OF-CONTEXT LAW says route it rather than
open it.

**Consequence for the runner:** SCRIP engines default to `SCRIP_NOHUGE=1` as the *measurement condition*,
with the arm named in the output banner. `NOHUGE=0` reproduces the shipping-arm instability.

## 5. ⛔ A MODE-3/MODE-4 DIVERGENCE I REPORTED WAS AN INSTRUMENT ARTIFACT — RETRACTED IN-SEAT

The first table showed `table_access_t` m4:m3 = **1.62x** and `string_pattern_t` = 1.39x, which would have
read as a MODE34-IDENTICAL violation and could easily have been routed as a codegen defect. Under the
corrected instrument every row is **0.88–1.00x**. The divergence was THP weather. Recording this because
the near-miss is the point: *the first plausible table produced by an uncharacterized instrument is
exactly the kind of false signal the s33 "non-empty is not alive" class is made of.*

## 6. THE MEASUREMENT (REPS=3, best-of, `SCRIP_NOHUGE=1`, all 12 correctness-green in all 3 engines)

| benchmark | sbl/s | m3/s | m4/s | **m3:sbl** | min-det |
|---|---|---|---|---|---|
| `var_access_t` | 5.7M | 35.1M | 30.9M | **6.21x** | 11.6% |
| `func_call_t` | 8.5M | 41.4M | 40.3M | **4.88x** | 4.6% |
| `op_dispatch_t` | 6.8M | 32.3M | 32.2M | **4.73x** | 8.7% |
| `arith_loop_t` | 14.9M | 66.1M | 64.7M | **4.43x** | 7.0% |
| `fibonacci_t` | 3.9K | 17.0K | 17.0K | **4.34x** | 1.2% |
| `string_concat_t` | 3.4M | 10.4M | 9.8M | **3.04x** | 5.8% |
| `pattern_bt_t` | 2.0M | 2.0M | 1.9M | 0.98x | 7.0% |
| `eval_fixed_t` | 3.3M | 2.3M | 2.3M | 0.72x | 0.7% |
| `string_pattern_t` | 5.2M | 3.7M | 3.6M | 0.70x | 1.8% |
| `table_access_t` | 12.0K | 6.1K | 5.9K | 0.51x | 6.7% |
| `array_sum_t` | 12.6K | 5.4K | 5.3K | 0.43x | 8.8% |
| `string_manip_t` | 6.8M | 2.6M | 2.5M | 0.38x | 4.8% |

**The shape of the "ten times faster" claim, stated honestly: the emitted code is 4.3–6.2x the oracle on
the compiled scalar core; the C runtime it calls into is 1.4–2.6x SLOWER than the oracle's.** Every row
above 3x is code the emitter produces. Every row below 1x is a call into `src/runtime/`. That is a clean
split and it says where the next order of magnitude is: not in the codegen, in the runtime library.

## 7. MANUAL CONSTRUCTS READ BEFORE USE (per Lon's standing instruction)

- **`TIME()` (p.244)** — integer milliseconds since program start; **on Unix it is CPU time, excluding
  I/O wait**. ⛔ SCRIP's `_TIME_` (`core.c:975`) uses `CLOCK_MONOTONIC`, i.e. **elapsed wall time** —
  a documented-semantics divergence. Inert for this harness (a compute-bound deadline loop advances both
  clocks alike on an idle box) but it means a SCRIP benchmark that blocks on I/O charges the wait to the
  budget where SPITBOL would not. **Routed, not fixed.**
- **`TIME()` return type** — manual and oracle give **INTEGER**; SCRIP's C returns `REALVAL(...)`.
  Probed in both engines: `DATATYPE(TIME())` = `INTEGER` and `TIME()/2` behaves as integer division in
  both. No live divergence — recorded so the next seat does not re-derive it from the C alone.
- **`&STLIMIT` (p.191)** — `-1` is the documented way to inhibit the statement-count check and is
  explicitly *faster* ("internal counts will not have to be updated and checked"). ⛔ **All 23 legacy
  benchmarks use `&STLIMIT = 4294967295`, which still pays the per-statement increment and check on
  every statement of a benchmark loop.** The timed family uses `-1`.
- **`&STCOUNT`** — freezes once `&STLIMIT` goes negative, so it cannot serve as a free iteration counter.
  (Aside, measured, not chased: after `&STLIMIT = -1` the oracle reads `&STCOUNT` = 1, SCRIP = 3.)
- **`DEFINE(s)` / `DEFINE(s,name)` (p.219)** — with the second argument absent, **the entry label must
  equal the function name**. This caught a live bug in the generator, which was prefixing entry labels
  per phase and would have emitted `AFIB` for `DEFINE('FIB(N)')` → error 86.
- **`&ANCHOR`, `&TRIM`** — carried over from the legacy programs unchanged.

## 8. ⛔ NEXT SEAT — PICK UP EXACTLY HERE

1. **The THP defect (§4) is minted and unowned.** `table_access_t` is a 2.26x throughput recovery sitting
   behind one env var. Root-cause the allocating path's page behaviour; do NOT assume the RBX frontier
   without measuring.
2. **The legacy 23 have a dead correctness oracle (§1).** Every `.ref` is unmatchable. Either convert
   them to the timed shape (the generator takes a kernel table — the marginal cost per program is a
   table entry) or restore their deterministic output. ⛔ **Lon's call, not taken here**: conversion
   touches artifacts the scorecard's `benchmarks` suite (weight 10) and two sibling repos
   (`snobol4jvm`, `snobol4dotnet`) load by name.
3. **`TIME()` wall-vs-CPU (§7)** is a real semantics divergence from the manual and is unrouted.
4. The timed family is **not yet wired into `scorecard_snobol4.sh`** — deliberately, since adding a
   suite reweights META and that is a scoring decision, not a seat decision.
