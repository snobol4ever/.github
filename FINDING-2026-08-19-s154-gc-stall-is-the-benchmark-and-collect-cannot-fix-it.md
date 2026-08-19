# FINDING 2026-08-19 s154 — THE ALLOCATING BENCHMARKS WERE MEASURING ONE GC STALL, NOT THROUGHPUT; `COLLECT()` PROVABLY CANNOT FIX IT; AND THE s149 THP VERDICT DOES NOT REPRODUCE

**Seat:** local `/home/claude3` (Claude Fable 5, then Opus 5). **Goal:** `GOAL-SNOBOL4-100.md` (benchmarks suite, scorecard weight 10).
**Baseline:** SCRIP `0570702a` · corpus `0a4a99e6`. No codegen touched — instrument + corpus only. Oracle: x64 `sbl` at `/home/claude/x64`.

---

## 1. THE DEFECT — A 500 ms BUDGET WAS REPORTING 1240 ms, AND THE OVERSHOOT *WAS* THE NUMBER

`harness.inc` fixes the time (`ZBUD=500`) and counts iterations. Measured, it was not holding: the two
allocating rows reported `ms:` far past their budget while the oracle landed on it.

| engine | ZK | batches | deadline | actual end | overshoot |
|---|---:|---:|---:|---:|---|
| `sbl` | 512 | 17 | 570 | 596 | 26 ms — **one batch, correct** |
| SCRIP m3 | 256 | 13 | 574 | 888 | 314 ms — **five batches** |

Per-batch timestamps name the cause exactly. SCRIP: `31 34 32 30 34 31 30 30 33 31 30 33` then **861**.
Oracle: `30 30 31 30 30 30 32 30 30 33 30 30 31 31 32 30` — flat. **Twelve normal batches and one 28×
outlier**, and because the outlier is what crosses the deadline, every run contains exactly one.

**The stall is the reported figure.** `table_access` steady state is 256 iters / 31 ms = **8,153/s**;
the suite published **2,684/s** (3328 iters / 1240 ms) because one pause is amortised into a half-second
window. The row read **0.23× of the oracle when the truth is 0.46×**; `array_sum` read **0.34×** when the
truth is **0.97× — parity**. Both were quoted in the s149 grid and in `README.md`'s "the C runtime it
calls into is 1.4–2.6× SLOWER than the oracle's" reading, which is overstated by this artifact.

## 2. ⛔ `COLLECT()` AT THE START DOES NOT WORK — TESTED, NOT REASONED

Lon's instruction was to guarantee no GC by calling `COLLECT()` before the measurement. **Measured, it
does not:**

| row | variant | iters | ms | stalls >200 ms | worst batch |
|---|---|---:|---:|---:|---:|
| table_access | baseline | 3328 | 1039 | 1 | 670 ms |
| table_access | **COLLECT() first** | 3840 | 1295 | **1** | 866 ms |
| array_sum | baseline | 4608 | 959 | 1 | 731 ms |
| array_sum | **COLLECT() first** | 5632 | 1021 | **1** | 754 ms |

Pre-collecting shifts the phase (more iterations complete before the pause lands) and cannot remove it:
these kernels allocate *continuously* — `table_access` builds a fresh `TABLE(512)` every iteration — so
the collection is driven by allocation volume accrued **inside** the window, not by inherited garbage.
Measured GC period ≈ 3,300–3,800 iterations against a window of ≈ 3,300–3,800. The window catches one
pause by construction. The manual predicts the direction (p. COLLECT: *"forcing garbage collections
before they are necessary will always increase execution time"*), and the elapsed went **up** in both rows.

**Two SPITBOL divergences found while reading it, routed not fixed.** The manual defines `COLLECT(i)`'s
argument as *a minimum number of words to be made available*, failing if it cannot be obtained. SCRIP's
`_COLLECT_` (`core.c:1239`) is `(void)a; (void)n;` — it **discards the argument**, so (a) it cannot be
used to pre-size the heap, which is exactly the lever this rung needed, and (b) it can never fail, so the
documented `COLLECT(n)` failure idiom silently succeeds.

## 3. THE REAL LEVER — THE COLLECTOR IS EXHAUSTION-TRIGGERED AND COSTS O(EVERY BLOCK EVER ALLOCATED)

`gc_heap.c:223` collects only when the arena is full (`if (g_hp_top + total > g_hp_end && …) rt_gc_collect()`),
and `SCRIP_HEAP_MB` (`:140`, range 1–4096, default `ZC_HEAP_MB` = **512**) sizes that arena. So a window
smaller than the arena is collection-free by construction:

| `SCRIP_HEAP_MB` | iters | ms (budget 500) | stalls | worst batch | GC regenerations |
|---|---:|---:|---:|---:|---:|
| default (512) | 3328 | **1211** | 1 | 835 ms | **1** |
| 1024 | **4096** | **500** | 0 | 34 ms | **0** |
| 2048 | 4096 | 518 | 0 | 36 ms | **0** |
| 4096 | 4096 | 500 | 0 | 35 ms | **0** |

⛔ **The telemetry for that single regeneration is the finding under the finding:**

```
[ZGC] regeneration #1 (LG): blocks 7352520->1548 (pinned 1548, fill 775)
                            bytes 536870848->536870848 reclaimed 0 win=536670208
```

**7,352,520 blocks walked to retain 1,548** — a live set of 0.02% — and `reclaimed 0` bytes. Cost tracks
total blocks ever allocated, not survivors. 835 ms to keep one 500-entry table. **This is a real runtime
defect, minted and UNOWNED here** (END-OF-CONTEXT LAW: routed, not opened). Sizing the heap does not fix
it — it defers it, and each deferred collection is larger.

**Fairness checked, not assumed:** the oracle is insensitive to the equivalent knob (`sbl -d1024m` gives
`table_access` 8704 iters either way), so it is already collection-free in this window. Raising SCRIP's
arena equalises the measurement condition; it does not hand SCRIP an advantage.

## 4. WHAT LANDED

- **`test_bench_snobol4_timed.sh`** — `HEAP` (default 1024) applied to m3/m4, and the **regeneration count
  is now counted per row and printed**. A row that collects is marked `GC<n>` and the run prints
  `⛔ N row(s) COLLECTED inside the measurement window -- those rates are stall figures, not throughput.`
  The gc flag travels with the *reported* rep (best-of-REPS), so a printed rate and its flag always
  describe the same run. **Revert-probe: at `HEAP=512` exactly `array_sum` and `table_access` go `GC1`
  and the banner fires, while `arith_loop` stays 0.** A gate that cannot go red proves nothing (s68).
- **`bake_noise_floor_snobol4_timed.sh`** — same GC-free condition; plus the BM-ONE catch-up it still
  owed (harness guard so legacy programs sharing the directory are skipped, and `NOHUGE` passed
  explicitly to m3/m4 so the `thp` column cannot lie about the arm it measured).
- **`NOISE-FLOOR.tsv`** — re-baked. It was unusable before: rows keyed `*_t` (pre-promotion names) baked
  at `nohuge=0`, while the runner looks up classic names at `nohuge=1` — **every lookup missed silently.**

## 5. ⛔ CORRECTION TO s149 §4 — THE DISPERSION WAS THE STALL LOTTERY, NOT THP

s149 attributed the allocating rows' dispersion to transparent huge pages and routed a 2.26× throughput
recovery behind `SCRIP_NOHUGE=1`. GC-free, the dispersion collapses **with THP unchanged**:

| row | s149 floor (GC-polluted) | this floor (GC-free) |
|---|---|---|
| `table_access` m3 | cv 12.4% · min-det **37.2%** | cv **1.9%** · min-det **5.6%** |
| `array_sum` m3 | cv 10.9% · min-det **32.6%** | cv **0.5%** · min-det **1.4%** |
| `array_sum` m4 | cv 11.9% · min-det 35.8% | cv **1.5%** · min-det 4.5% |

Whether an ~835 ms pause lands inside a 500 ms window is a coin flip; that bimodality was being baked as
variance. Those rows are now gate-able (a 2× regression was invisible at min-det 80.7%).

**And the THP direction itself does not reproduce on this box.** Interleaved arms (5 reps, alternating
order), THP **ON** is faster on every row and both engines: `table_access` m3 **1.21×** / m4 **1.22×**,
`array_sum` m3 **1.29×** / m4 **1.10×** — against s149's reported 2.26× *loss*. Mechanism, measured:
this host is unfragmented (`/proc/buddyinfo` 904 free order-10 blocks) and served **20,778 THP
allocations with `thp_fault_fallback=0` and `compact_stall=0`** — every huge page free, no compaction.
With `defrag=madvise`, a *fragmented* host makes `MADV_HUGEPAGE` pay synchronous direct compaction at
fault time, which is where a 2.26× loss comes from. **Neither measurement is wrong; the generalisation
is.** ⛔ **Consequence: a THP number is only meaningful with `compact_stall`/`thp_fault_fallback`
recorded beside it** — those counters are the discriminator, and no THP claim should be quoted without
them. The runner's `SCRIP_NOHUGE=1` default is left as-is pending Lon's ruling (it is now the
*documented* condition rather than a claimed 2.26× recovery), but note it measures an arm users do not
ship.

## 6. THE CORRECTED GRID — FIXED TIME, COUNTED ITERATIONS, GC-FREE

`ZBUD=500 ms`, `SCRIP_NOHUGE=1`, `SCRIP_HEAP_MB=1024`, best-of-3, all 12 correctness-green, gc 0 on every
row, m3≡m4 within 0.98–1.08×.

| benchmark | sbl/s | m3/s | m4/s | m3:sbl | was (GC-polluted) |
|---|---:|---:|---:|---:|---:|
| var_access | 8.5M | 59.5M | 64.3M | **7.01×** | 6.93× |
| func_call | 13.4M | 78.3M | 78.3M | **5.86×** | 5.82× |
| op_dispatch | 10.4M | 58.0M | 57.3M | **5.56×** | 6.28× |
| arith_loop | 23.5M | 115.6M | 121.2M | **4.92×** | 5.00× |
| fibonacci | 6.2K | 30.1K | 30.1K | **4.89×** | 4.85× |
| string_concat | 5.2M | 16.8M | 17.2M | **3.21×** | 3.18× |
| array_sum | 18.9K | 17.7K | 17.6K | **0.94×** | **0.34×** ⬅ |
| pattern_bt | 3.8M | 3.5M | 3.5M | 0.92× | 0.91× |
| string_pattern | 8.3M | 5.9M | 5.9M | 0.71× | 0.67× |
| eval_fixed | 5.8M | 3.7M | 3.7M | 0.63× | 0.67× |
| table_access | 16.8K | 8.1K | 8.2K | **0.48×** | **0.23×** ⬅ |
| string_manip | 9.4M | 2.6M | 2.7M | 0.28× | 0.30× |

Only the two allocating rows moved — the fix is targeted, which is itself evidence it is the right one.
The split s149 named still holds and is now stated on clean numbers: **emitted code runs 3.2–7.0× the
oracle; the C runtime it calls into runs 0.28–0.94×.** But the runtime's deficit is *smaller* than
published, and one of the two rows that carried the "3× slower on aggregates" story is at parity.

## 7. ⛔ NEXT SEAT — PICK UP EXACTLY HERE

1. **The GC is the biggest single performance item in this suite and is unowned.** Cost is O(blocks ever
   allocated), not O(live). 7.35M blocks walked for 1,548 survivors, `reclaimed 0`. Do not assume the
   RBX frontier without measuring — that is the same hypothesis s149 routed and nobody has tested.
2. **`COLLECT(n)` ignores its argument** (`core.c:1239`). Implementing the manual's minimum-words
   semantics would give programs a supported way to pre-size the heap, which is what this rung wanted.
3. **`TIME()` wall-vs-CPU** (manual p.244: Unix `TIME()` excludes I/O wait; SCRIP uses `CLOCK_MONOTONIC`)
   is still unrouted — carried from s149 §7, unchanged.
4. **The timed family is still not wired into `scorecard_snobol4.sh`** — deliberately; that reweights
   META and is Lon's call. It matters more now: two of its rows were feeding a false 0.23×/0.34×.
5. **Legacy-23 dead refs** (s149 §8.2) untouched and still unmatchable.
