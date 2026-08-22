# FINDING-2026-08-22-s253 — row bench-external-cpu-and-elapsed-clock (Lon s200 directive)

## THE DIRECTIVE
Lon, s200, in-chat: "what can we do to get CPU time versus elapsed time -- actually we want both;
there were special system calls with nanosecond clocks, why are we not using that." The brief framed
this as a credibility defect, not a precision one: the cross-engine harness measures each engine
with its OWN clock (harness.inc's `TIME()`, self-reported).

## ROOT CAUSE, CONFIRMED — THE TWO ENGINES' "ms" WERE NEVER THE SAME UNIT
This is worse than "self-timed." Grepped and read both sides directly:
- **SPITBOL's `TIME()` is CPU time.** `scripts/build_spitbol_oracle.sh` patches `x64/osint/systm.c`'s
  `zystm()` to `clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &tim)` before building the oracle. This has
  been true since the oracle was first built and is already half-documented:
  `scripts/util_bench_snobol4_engines.sh`'s own divisor table has said "fork snobol4ever/x64: ...
  (patched: CPU-time ms)" since s13 (2026-07-10) — the fact was on record, just never connected to
  the harness's own TIME()-based budget loop.
- **SCRIP's `TIME()` (`_TIME_`, `src/runtime/core/core.c`) is wall-clock** — `CLOCK_MONOTONIC`, same
  clock as the `--bench` flag (`src/driver/scrip.c`) and the GC walk timer (`gc_heap.c`).
- So every `harness.inc` benchmark's self-reported `ms:` line has been CPU-time for one engine and
  wall-clock for the other. Under an idle box the two nearly coincide (see MEASURED below) and the
  gap is invisible; under the 8-seat fleet's real load they diverge, because wall-clock keeps
  counting the seconds a descheduled process wasn't running and CPU-time does not — which is the
  mechanism, not a guess, behind the 2026-08-20 bake's 47.9% min_detectable floor (a floor that
  cannot see a 1.4x regression).

## CURE — ONE EXTERNAL INSTRUMENT, BLIND TO WHICH ENGINE IT TIMES
Per the brief's first step: no clock was added to SCRIP (would repeat the same conflict of
interest). New file `SCRIP/tools/bench_rusage.c` (built on demand, not committed as a binary, same
convention as the other `tools/*.c` utilities): forks `argv[1..]` unchanged (child's stdout/stderr
pass through untouched), `wait4()`s it, and prints one line to its own stderr:
```
BENCH_RUSAGE: elapsed_ns=<N> user_us=<N> sys_us=<N> maxrss_kb=<N> nivcsw=<N> nvcsw=<N> exit=<N>
```
`elapsed_ns` is `CLOCK_MONOTONIC` bracketing fork/wait4; the rest comes straight out of wait4's
rusage for exactly that one child (not a post-hoc `getrusage(RUSAGE_CHILDREN)`, which would
accumulate across every child ever reaped). Same binary, same code path, for `scrip` and `sbl`.

**Wired into `scripts/util_bench_snobol4_engines.sh`** (the cross-engine runner over the 15-program
`corpus/benchmarks/snobol4/` suite): invocation is now `bench_rusage timeout "$T" "$@" "$sno"` —
`bench_rusage` OUTSIDE, `timeout` INSIDE, deliberately in that order. Reversing it (`timeout
bench_rusage ...`) would let a timeout's SIGTERM kill `bench_rusage` while orphaning the actual
engine process still running underneath it — exactly the kind of leaked, invisible, cross-seat load
contamination this row exists to stop. With `timeout` as the direct child, its own wait() on the
engine before it exits propagates the engine's rusage up transitively when `bench_rusage` reaps
`timeout`, and the exit-code contract (124 on timeout, engine's own code otherwise) is unchanged.
Every row now prints `elapsed(ms)`, `cpu(ms)` (user+sys), `self(ms)` (old TIME()-based figure, kept
for continuity, never again the authority), `rss(kb)`, and `nivcsw`, and is flagged `LOAD` when
`nivcsw` exceeds `$BENCH_NIVCSW_THRESHOLD` (default 20). **That default is an uncalibrated first
guess, not a measured statistic** — it has not been baselined against a quiet-box nivcsw
distribution and should not be quoted as a validated cutoff; recalibrating it is open work.

**One pre-existing bug fixed along the way, found because it made the STATUS column useless for
validating this change:** the script's `.ref` diff stripped `ms:` lines but not `iters:` lines, so
every row FAILed unconditionally regardless of engine (confirmed on both `scrip` and `sbl-fork`
before the fix, ruling out an engine-specific regression) — `harness.inc`'s contract states the
`.ref` holds only the `check:` line, but the comparison never stripped the `iters:` line to match.
One-line fix, both `grep -vi 'ms:'` sites. Also fixed the divisor-table comment's `sbl -b` to `-bf`
(RULES.md oracle note, s189: `-b` alone SIGSEGVs unpredictably via SPITBOL's own error-recovery path
and case-folds names SCRIP treats as distinct) — comment-only, did not touch the executable divisor.

## MEASURED (idle-ish box, single sample each — not a quotable benchmark, just validation that the
instrument works and both engines run it identically)
Full 15-program suite, both engines, OK=15/FAIL=0/CRASH=0 after the diff fix. Sample (`fibonacci`):
SCRIP self=509.0ms, external elapsed=586.4ms, external cpu=585.8ms, nivcsw=15.
SPITBOL(fork) self=505.0ms, external elapsed=553.0ms, external cpu=552.7ms, nivcsw=10.
Self and external track closely for both engines here (elapsed≈cpu because these kernels are ~100%
CPU-bound with low nivcsw on this run) — the gap between self(ms) and external(ms) is process
startup + the harness's own calibration phase (ZCAL), which self(ms) deliberately excludes and the
external instrument deliberately includes; that gap is expected, not a bug, and should not be
mistaken for measurement error when the next seat reconciles the two.

**Incidental discovery, not investigated further — flagging so it isn't lost:** `maxrss_kb` on
several benchmarks (`array_sum`, `mixed_workload`, `table_access`) is 200x+ SCRIP's footprint vs
SPITBOL's (SCRIP ~590-635 MB vs SPITBOL ~2.8 MB on the same kernel). This is exactly the kind of
signal the old harness had no way to surface at all. Worth its own row.

## NOT YET DONE — DONE-WHEN IS ONLY PARTIALLY MET, CLAIM LEFT OPEN
- Only `util_bench_snobol4_engines.sh` is wired to the external instrument. `bench_min_of_n.sh`,
  `test_bench_snobol4_timed.sh`, and the others under `scripts/bench_*.sh` / `scripts/test_bench_*.sh`
  are NOT yet converted.
- **The floor re-bake is NOT done.** The min_detectable/47.9% floor lives in
  `scripts/bake_noise_floor_snobol4_timed.sh`, a separate statistical instrument from the one edited
  here (different methodology, not inspected in depth this session) — re-baking it on the CPU-time
  statistic and naming its min_detectable against the elapsed one is the next concrete step.
- **The s198-s200 headline numbers were not located, therefore not re-quoted.** Searched `.github`
  FINDING files and `ARCH_SCOREBOARD.md`/`corpus/BENCHMARKS.md` for "s198"/"s199"/"s200"; nothing
  matched. They may be in-chat only, or on a BOARD.md window already rotated out (`QUEUE.tsv.bak.s198`
  exists at `/home/resources/postoffice/` if a byte-exact snapshot of that moment is needed). Next
  seat: ask Lon directly which numbers he means before re-baking anything against a guess.
- `TIME()` itself is untouched (correctly, per the brief) — still available, no longer cited as the
  cross-engine authority in the one script converted so far.

Claim `bench-external-cpu-and-elapsed-clock` intentionally NOT marked done — DONE-WHEN has five more
sub-items outstanding. Left LOCKED for continuation (by this seat or another) rather than freed,
since the instrument and its first integration are real, tested progress worth building on rather
than re-deriving.

## CROSS-REFERENCE, FOUND AFTER PUSHING — READ THIS BEFORE RE-BAKING ANYTHING
Sibling row `bench-timed-oracle-flag` closed at s200 (SCRIP `db8a9ced`, 2026-08-21 evening; see
`FINDING-2026-08-22-seat1-bench-timed-oracle-flag-was-closed-at-s200-...`) already re-baked
`bake_noise_floor_snobol4_timed.sh`'s floor once — but on a DIFFERENT axis. That row proved the
47.9% floor's TRIGGER is machine load, not the `-b`/`-bf` oracle flag (a controlled A/B on a quiet
box measured the flag's own timing effect at -0.3% ± 2.6%, i.e. zero), and made load VISIBLE
(nproc/loadavg now recorded in the bake header) so a loaded bake can't be silently compared against
a solo one again. It did **not** change the underlying statistic away from self-timed `TIME()`.

That is the missing half this row supplies, and the two findings now explain each other: **load is
the trigger, and the TIME()-unit mismatch this row found is why load hits the two engines
asymmetrically instead of just adding symmetric noise a min-of-N could absorb.** SPITBOL's
self-reported `ms` is CPU-time — being descheduled mid-run does not move it, so its iteration count
barely degrades under contention. SCRIP's self-reported `ms` is wall-clock — every descheduled
millisecond is counted against its budget, so its iteration count degrades directly with load. A
noise floor built on that pair isn't measuring symmetric jitter; it's measuring a comparison that
tilts against SCRIP specifically as load rises. `db8a9ced`'s load-visibility fix lets you SEE this
happening (and discard a loaded bake); this row's external CPU-time instrument is what would make
the comparison itself load-ROBUST instead of merely load-legible. Re-baking
`bake_noise_floor_snobol4_timed.sh` on `bench_rusage`'s `cpu(ms)` rather than `TIME()`'s self-report
is the natural next step and should be done with `db8a9ced`'s nproc/loadavg header carried forward,
not redone from scratch.
