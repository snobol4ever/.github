# FINDING 2026-09-04 hq_P — the Pascal angle-1-vs-angle-2 bias is a PER-RUN FIXED COST **INSIDE THE PROGRAM**, and the two angles amortize it over different reps

ceo ruling 23:03 CDT on row `readme-perf-grids-three-angles-all-seven` (I26): *"pascal — find the
one-sided angle bias (all 21 ratios below 1.0), never widen the floor; a gate that cannot fail is not a
gate."* This is the answer. Tree SCRIP `e560edb92`, RT_OPT=-O0, mode m4, `tools/bench_rusage` CPU time,
best-of-N, box load ~3–5 on 16 cores.

## THE SYMPTOM
`bench_triangulate_pascal.sh` on a QUIET box: 18 of 21 kernel/engine cells DISAGREE, **zero** kernels
publishable vs `fpc`. Every one of the 21 `ratio` values (= angle2 / angle1) is **below 1.0**
(0.7048–0.9426) — one-sided, on every kernel, on every engine **including `fpc`**, which is what says
the cause is in the harness and not in SCRIP.

⚠️ CORRECTION TO hq_P'S OWN FIRST WRITE-UP: the earlier NEXT block on this baton said "angle 1 reports a
consistently LOWER rate than angle 2". **That was backwards** — the TSV's ratio column is
angle2/angle1, so angle 1 reads consistently **HIGHER**. The direction matters because it is what
identifies the mechanism, so the error is corrected here rather than quietly fixed.

## HYPOTHESIS 1 — PROCESS STARTUP IN THE DENOMINATOR. ⛔ REFUTED BY MEASUREMENT.
Both angles compute `rate = reps / cpu_seconds` with process startup left inside `cpu`, so the angle at
lower reps would be depressed. Measured: an empty Pascal program on m4 costs **2202 µs**, against
readings of 1.0–12.2 **seconds**. Subtracting it moves `bubble`'s rate from 4.985 to 4.996 — 0.2%. It
cannot produce a 13% bias. **Not the cause.**

## HYPOTHESIS 2 — A FIXED COST *INSIDE* THE PROGRAM, AMORTIZED OVER REPS. ✅ CONFIRMED, AND LARGE.
`bubble`, m4, CPU µs best-of-5 at three reps counts:

| reps | cpu | RAW rate = reps/cpu |
|---:|---:|---:|
| 5 | 1,003,024 µs | 4.985 |
| 20 | 3,304,832 µs | 6.052 |
| 80 | 12,237,268 µs | 6.537 |

The raw rate is **not a constant of the kernel** — it climbs **31.1%** from n=5 to n=80. Fit
`cpu(n) = FIXED + n·MARGINAL`:
- MARGINAL from (5,20) = 153,454 µs/rep; from (20,80) = 148,874 µs/rep — **agree within 3.08%**.
- FIXED = **235,755 µs = 235.8 ms per run**, which is **107x the 2.2 ms process startup**. It is inside
  the program (setup outside the timed rep loop and/or first-iteration warmup), not the process.
- That fixed cost is **23.5%** of the reading at n=5, **7.1%** at n=20, **1.9%** at n=80.

**So the rate you measure depends on the reps you chose**, and the two angles choose differently:
angle 2 reads a committed N from `SCALE.tsv` (`bubble` scrip_reps = **5** — deep in the contaminated
region), while angle 1 runs a **×4 doubling search** to an 800 ms CPU budget and lands elsewhere,
generally higher. Higher reps ⇒ less fixed-cost share ⇒ higher rate ⇒ **angle 1 > angle 2, always**.
The `fpc` arm behaves the same way for the same reason: ×4 doubling overshoots `SCALE.tsv`'s committed
12000 to 16384.
⭐ The harness's own header already documented this mechanism in its extreme form and did not generalise
it: *"at reps=12 its measurement is almost entirely fixed process-startup overhead … angle 1 and angle 2
disagreed 12-18x on fpc/quick … it repeated in the same direction both times, unlike the genuine
load-contention DISAGREEs elsewhere, which flip direction run to run."* That is this defect at 12-18x;
what remains is the same defect at ~1.15x, and the one-sidedness is the signature of both.

## IT IS KERNEL-DEPENDENT, AND FOR SOME KERNELS THE SLOPE DOES NOT FULLY CURE IT

| kernel | in-program FIXED cost | RAW rate spread (n=15→240) | SLOPE-rate disagreement |
|---|---:|---:|---:|
| `bubble` (n=5→80) | **235.8 ms** | 31.1% | **3.1%** |
| `towers` | 9.5 ms | 12.9% | 8.7% |
| `sieve` | 2.9 ms | 4.0% | 3.5% |

`bubble` is cured by the slope basis (31.1% → 3.1%). `towers` is only improved (12.9% → 8.7%): its
slope-rate itself still climbs (104.03 → 113.08 reps/s), so its per-rep cost genuinely falls with n
beyond any constant offset — a warmup that is still running at n=240, not a fixed intercept. ⛔ So
"subtract an intercept" is a real cure for the dominant term but **not a universal one**, and a kernel
must show a stable slope before its number is published.

## THE CURE, AND WHAT IS NOT THE CURE
✅ **Report the rate as the SLOPE — the marginal cost per rep — not as `total/reps`.** Each angle
measures at two reps values and reports `Δcpu/Δreps`; the in-program fixed cost cancels **exactly**, and
the two angles then agree without either of them changing how it picks N. That is precisely the
two-number basis applied to the cross-proof itself: the intercept IS the OVERHEAD, the slope IS the
WORK. It is the same instrument hq_P built for SNOBOL4 this session (`bench_ir_slope.sh`), in CPU time
instead of instructions.
✅ Require the two slopes (from `(n,2n)` and `(2n,4n)`) to agree before publishing — that is the
adequacy check the law already describes, and it is what would have caught `towers`.
⛔ **NOT the cure: widening `TOL_PCT`.** The spread is one-sided; a floor wide enough to swallow a bias
is a gate that cannot fail, which is exactly what ceo forbade. Note the numbers: under the slope basis
`bubble` disagrees by 3.1%, comfortably inside the EXISTING flat 10% — **the tolerance never needed
changing at all.**
⛔ NOT the cure: re-baking `SCALE.tsv` larger. It would shrink the bias by moving both angles right on
the same contaminated curve, without removing the contamination, and would silently change every
published Pascal number.

## CONSEQUENCE FOR THE BOARD
The Pascal B cell stays UNPUBLISHED-vs-fpc until this lands; that is correct and not a benchmark gap.
⛔ And the existing Pascal grid in the README (4/7 kernels, "First measurement 2026-09-04", queens
1.07x / quick 1.04x / sieve 0.91x / towers 0.96x) was taken on the RAW basis, so each of those numbers
carries its kernel's fixed-cost contamination at whatever reps that run happened to use — `towers`
0.96x is exactly a kernel this FINDING shows to be reps-sensitive. Those cells should be re-measured on
the slope basis, not merely re-run.
