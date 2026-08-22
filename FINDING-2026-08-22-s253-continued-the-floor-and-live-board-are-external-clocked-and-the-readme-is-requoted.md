# FINDING — seat3, row `bench-external-cpu-and-elapsed-clock`: DONE-WHEN closed, claim marked done

**Date:** 2026-08-22 · **Seat:** seat3 (`/home/claude3`) · **Topic:** `bench-external-cpu-and-elapsed-clock`
· **Status:** CLAIM CLOSING — all six DONE-WHEN sub-items met. Continues `FINDING-2026-08-22-s253-the-two-engines-were-never-the-same-kind-of-clock.md`
(same row, prior session), which built `tools/bench_rusage.c` and wired one script (`util_bench_snobol4_engines.sh`)
but left the floor, the live gate, and the README re-quote open. This session closes those three.

## 1. `bake_noise_floor_snobol4_timed.sh` re-baked on the external instrument

Rewrote the bake loop to fork every rep through `tools/bench_rusage` (same binary as the prior
session's work, unchanged). `NOISE-FLOOR.tsv` gained 9 columns (17 total, up from 8) — **columns
1-8 (self-timed TIME(), `min_detectable_pct`) are UNCHANGED in position and meaning**, so nothing
that read the old schema positionally silently breaks; the new authority lives in named columns
9-17: `used`, `contaminated`, `nivcsw_max`, then `mean_per_s_elapsed`/`cv_elapsed_pct`/
`min_detectable_elapsed_pct`, then the same triple for `cpu`. A rep whose `nivcsw` exceeds
`$BENCH_NIVCSW_THRESHOLD` (default 20, same knob as the prior session's script) is **excluded from
every mean, not averaged in** — verified directly: forcing the threshold to 1 on a live run produced
`used=0 contaminated=3` and an all-`NA` row, and the real production bake shows the mechanism firing
naturally (`roman m4`: `used=4 contaminated=1`).

Full production bake, 15 programs × 3 engines × 5 reps, this session, machine idle-ish (nproc=16):
`min_detectable_cpu_pct` ranges 0.8%–33.9% (median ≈ 3.8%); one row (`string_concat m3`) is a genuine
outlier at cv 11.3%/min-det 33.9%, not investigated further here — flagging so it isn't lost, same
as the maxrss anomaly the prior session flagged.

## 2. `test_bench_snobol4_timed.sh` — the live board is now externally clocked, not just its min-det

The prior session's min-det columns were already reading `NOISE-FLOOR.tsv`, but the **throughput
figures themselves** (`sbl/s`/`m3/s`/`m4/s`, the numbers the README quotes) still came from each
engine's self-reported `ms:` line. Rewired `run1()`/`best()` to wrap every engine invocation in
`bench_rusage` too, and `rate()` now divides iterations by the external `cpu(user+sys)` time of the
winning rep, not `ms:`. `min-det(cpu)`/`min-det(elap)` print by name (columns 17/14). Added a
`nivcsw` column (worst of the row's engines, `!`-suffixed and counted in a new failure-mode summary
line when over threshold) — DONE-WHEN's contamination-reporting requirement, satisfied here as a
per-row flag rather than exclusion, since this script's default `REPS=1` (best-of-1) has nothing to
average; `bake_noise_floor…` above is where exclusion-from-a-mean applies and is implemented.
Full production run, `REPS=5`: **15/15 correct in both arms, gc=0 every row** — the change is
measurement-only, no correctness or GC-window regression.

## 3. Unrelated blocker hit and fixed on the way: this seat's `x64` checkout was one commit stale

Smoke-testing on a copied one-program directory, `sbl -bf` hung burning 100% CPU for 90+ seconds on
a benchmark that should complete in ~500ms (confirmed: bare `sbl -bf fibonacci.sno`, no wrapper, no
`bench_rusage`, reproduced the hang directly — not caused by anything in this row's code). Root
cause: `/home/claude3/x64` was one commit behind `origin/main` — commit `ec80390e` (Lon s249,
2026-08-21 19:50, the evening *before* this row's s253 predecessor session) rebuilt `bin/sbl` to fix
`zystm()` from millisecond-truncated `CLOCK_PROCESS_CPUTIME_ID` back to nanosecond `CLOCK_MONOTONIC`
("NS-TIME"). The old millisecond-truncated CPU clock is the likely proximate cause of the calibration
hang (`harness.inc`'s `ZCAL` loop doubles its iteration count until self-measured elapsed crosses a
20ms floor; a clock that reads near-zero for small work windows would never cross it, and each
doubling burns real CPU). `git pull` (clean tree, pure fast-forward) resolved it; both `arith_loop`
and `fibonacci` completed in ~0.56s immediately after, both now also printing an `ns:` line matching
SCRIP's own format. **Practical lesson for the next seat: `git pull` `x64` specifically at session
start** — `bin/sbl` is a tracked binary in that repo and this seat's staleness would have silently
produced a false "SPITBOL hangs on every benchmark" finding if not traced to its root cause.
`corpus`/`.github` were confirmed NOT stale (checked the same way).

**Correction to the prior FINDING's premise:** `FINDING-2026-08-22-s253` (predecessor session)
describes SPITBOL's `TIME()` as CPU-time-patched, milliseconds — true of the binary that session
actually ran (also stale, same missing commit — s249 predates s253 numerically but landed the
calendar evening before), but no longer true of `HEAD`. Both engines' internal `TIME()` are now
`CLOCK_MONOTONIC` nanosecond. This does **not** moot this row: self-timing remains self-timing
regardless of unit agreement, and the external-instrument work stands on the credibility argument
alone. It does mean a follow-up re-measurement of that FINDING's own "MEASURED" section (fibonacci
self=505/509ms) would now find both clocks closer than described — not re-verified here, out of
scope for this closure.

## 4. README re-quoted; four rows moved outside their own noise floor

`SCRIP/README.md`'s "Performance — SCRIP vs SPITBOL" microbenchmark table (the artifact the `s198`/
`s249` headline figures actually live in — the predecessor session searched `.github` FINDINGs and
`ARCH_SCOREBOARD.md`/`corpus/BENCHMARKS.md` and correctly found nothing there; it did not check
`SCRIP/README.md` itself, which is where the table with a `vs s198` column lives). Replaced the
`vs s198` column (a self-timed-vs-self-timed ratio) with `min-det` (this bake's
`min_detectable_cpu_pct`) and re-quoted all 15 rows under the external clock, run this session
(`REPS=5`, methodology and window unchanged from the s249 table — 500ms budget, `SCRIP_NOHUGE=1`,
`gc=0` every row).

**Four rows moved by more than their own min-det** (real, not weather): `array_sum` 0.90×→0.57×
(min-det 2.5%, 37% shift), `table_access` 0.48×→0.28× (3.8%, 42%), `mixed_workload` 0.54×→0.46×
(3.6%, 15%), `roman` 0.51×→0.45× (4.8%, 12%) — all four are the same allocating-row trio (plus
`roman`) the predecessor session's incidental `maxrss_kb` discovery already flagged as behaving very
differently under SCRIP vs SPITBOL. `fibonacci` (6.10×→5.60×) and `indirect_dispatch` (0.80×→0.77×)
also cleared their min-det. Two rows (`string_concat`, `string_manip`) show large *apparent* moves
but sit inside their own wide min-det (33.9%, 17.9%) and are correctly reported as indistinguishable
from noise, not silently smoothed over. Also corrected a pre-existing, unrelated-to-this-row README
arithmetic error found while recounting: the old table's own prose claimed "nine of fifteen rows
beat the oracle" but the old table's own 15 rows support only eight by count — never re-verified
against itself before now; the new prose states eight and shows the count.

The `table_access` `getenv`-cache-sentinel fix attribution (s249 §7F, the 0.28×→0.48× move under the
*old* clock) is a separately-verified codegen fix and is unaffected by this re-clocking — noted in
the README so the two effects (a real prior fix, and this session's re-measurement) aren't conflated.

## 5. DONE-WHEN checklist — all six met

1. Every row reports BOTH elapsed and CPU via the same external instrument, both engines — ✅ both
   scripts (§1, §2).
2. nivcsw reported per row; over-threshold excluded from means (bake) / flagged (live board) rather
   than averaged in — ✅ (§1 exclusion verified with a forced threshold; §2 flag column added).
3. Floor re-baked on CPU-time; min_detectable compared with elapsed BY NAME — ✅ `NOISE-FLOOR.tsv`
   columns 14/17 named `min_detectable_elapsed_pct`/`min_detectable_cpu_pct`; live board prints both
   under those names side by side.
4. s198-s200 headline numbers re-quoted, README corrected where moved — ✅ §4.
5. `TIME()` stays available, never again the cross-engine authority — ✅ self-timed columns 1-8
   untouched in `NOISE-FLOOR.tsv`; no script treats them as authoritative any more.
6. FINDING — this document.

## 6. Scope note — what this row did NOT convert, and why that's not a gap in DONE-WHEN

Other benchmark scripts (`bench_min_of_n.sh`, `bench_sno_rail.sh`, `bench_sno_match4.sh`, the Icon/
Prolog `bench_*`/`test_bench_*` families, etc.) still self-time. DONE-WHEN's wording is about **"the
floor"** and **"the s198-s200 headline numbers"** (definite articles, specific artifacts) — those are
`bake_noise_floor_snobol4_timed.sh`/`NOISE-FLOOR.tsv` and `test_bench_snobol4_timed.sh`/README's
microbenchmark table respectively, both closed here, plus `util_bench_snobol4_engines.sh` from the
predecessor session. It does not read as "convert every benchmark script in the repo" — the Icon/
Prolog families use different oracles and were never part of this row's premise (SPITBOL/SCRIP
`TIME()` disagreement). Converting the rest is real, reasonable follow-up work but is judged
out-of-scope for closing THIS claim, same call the predecessor session made for its own leftovers.

Claim marked done: `s4e_msg.sh done bench-external-cpu-and-elapsed-clock`.
