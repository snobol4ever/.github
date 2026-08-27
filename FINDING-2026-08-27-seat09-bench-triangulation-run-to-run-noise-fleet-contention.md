# FINDING — seat09: two independent SNOBOL4 3-angle triangulation runs, 9 minutes apart, on identical code, disagree with EACH OTHER more than either disagrees internally — run-to-run noise, not a SCRIP regression

**Date:** 2026-08-27 · **Seat:** seat09 (`/home/claude09`) · **Topic:** row `bench-triangulation-3angle` (now CLOSED — this finding does not block it; it questions whether ANY absolute-throughput number measured on this box right now is citable). **Status:** measured, not root-caused; routed to hq_P (postoffice `send`, topic `bench-noise-fleet-contention`) same day; this file is the durable record the postoffice message is not.

**Commits:** corpus `8e85e50d` (both raw TSVs) · SCRIP `1f79ed2f` (unrelated stale-comment fix found along the way). **RT_OPT `-O0`.** Machine: same 16-core shared box as every seat in FLEET-12.

---

## 1. WHAT WAS RUN

`bash scripts/bench_triangulate_snobol4.sh` (bare, full 18-kernel corpus, all three engines sbl/m3/m4), run twice on **identical code**: once unattended in an earlier session (13:37:28Z), once by this session as one blocking foreground call specifically to avoid this root's Stop-hook `make pristine` race (13:46:15Z). Both runs completed clean (no REFUSED, no CHECK-FAIL) and both TSVs are committed as the raw record — **neither is being cited as a performance claim**, which is the point of this finding.

## 2. THE COMPARISON — same kernel, same engine, same code, 9 minutes apart

| kernel | engine | 13:37 angle1_rate | 13:46 angle1_rate | delta |
|---|---|---|---|---|
| func_call | sbl | 21,800,000 | 16,200,000 | −26% |
| var_access | sbl | 5,400,000 | 9,000,000 | +67% |
| roman | sbl/m3/m4 | ratios 0.89/0.80/0.74 (**DISAGREE**, all 3) | ratios 0.99/1.02/1.04 (**AGREE**, all 3) | verdict flip, zero code change |

Verdict tally: the 13:37 run reads mostly DISAGREE across the 18-kernel board; the 13:46 run reads 6/18 AGREE, 12/18 DISAGREE — a **different** 12, not a stable subset. `TOL_PCT=10` (the triangulator's default cross-angle tolerance) cannot hold against a signal that moves 25–70% between two back-to-back runs of unchanged code, regardless of which specific kernels either single run happens to flag.

## 3. TWO MEASURED, NON-EXCLUSIVE CANDIDATE CAUSES — NEITHER CONFIRMED AS DOMINANT

1. **FLEET-12 CPU contention.** `uptime` at run time: load average 4.74/5.34/5.14 on a 16-core box. Independently observed via `/proc/<pid>/cwd` running concurrently at measurement time: seat12 (`make pristine`+`make all`), seat08, seat11 (same), hq_C (gate tests), hq_P (`scrip` invocations). Nothing serializes a benchmark window on one root against a build/test window on another — FLEET-12 means up to 12 seats sharing this box's cores with no coordination on that axis.
2. **Angle 1 vs angle 2 HEAP mismatch.** `test_bench_snobol4_timed.sh` defaults `HEAP=1024`MB; `bench_snobol4_fixed_iter.sh` defaults `HEAP=4096`MB — a deliberate, already-documented difference (item 1's LEDGER on this row, seat15) to avoid GC contamination on angle 2's longer fixed-iteration windows. Real, but this finding's §2 evidence is angle-1-vs-itself across two runs, which HEAP mismatch alone cannot explain — contention is the better fit for that specific comparison, though it doesn't rule out HEAP mismatch contributing to the angle1-vs-angle2 DISAGREE verdicts themselves.

## 4. CONVERGENT, INDEPENDENT EVIDENCE — THIS IS NOT AN ISOLATED READING

`FINDING-2026-08-27-seat06-quiet-box-remeasurement-scrip-ties-instrumented-oracle-still-beats-clean.md` (same day, unrelated row `perf-tooling-hardware-counters`, different methodology — `perf stat` IPC on `beauty.sno` self-host, not throughput on the 18 benchmark kernels) independently found: *"the sign is unstable across runs"* — SCRIP-vs-instrumented-oracle IPC ranking flipped across three measurements taken along a decreasing-load gradient (STEP 1 heavy load: SCRIP loses 0.947x; lighter/unpinned: SCRIP wins 1.032x; `taskset`-pinned/11-rep: dead heat 0.999x, ranges overlapping). Two seats, two different measurement instruments, two different rows, same day, same box — both converge on: **this shared machine's contention is large enough to flip the sign of a performance comparison, not just shift its magnitude.** Neither finding alone would be more than a suspicious anecdote; together they are a machine-level measurement-environment problem.

## 5. NOT DONE THIS PASS, AND WHY

Not root-causing further (isolating contention from the HEAP axis would need a controlled run at true fleet-quiet, which this seat cannot schedule) and not re-running a third time (a third noisy sample doesn't resolve which axis dominates, it just adds a data point). Row `bench-triangulation-3angle` is CLOSED — its DONE-WHEN is about the *tooling* existing and working, which it does (verified fresh, `exit=0`); this finding is about whether the tooling's *output* can be trusted on this box *right now*, a distinct question deliberately left open for hq_P.

## 6. RECOMMENDATIONS (routed to hq_P — sovereign over `GOAL-HQ-PERFORM.md`/`ARCH-PERF-TOOLING.md`; this seat does not self-edit HQ-only files)

1. Treat both committed TSVs (`triangulation-20260827T{133728,134615}Z.tsv`) as raw record only, not as citable kernel-level performance numbers, until re-measured under conditions this file's §3/§4 don't undermine.
2. Consider whether a benchmark campaign needs the same kind of boundary `ORACLE-SWAP-PROCEDURE` (RULES.md § Oracles) already requires for shared-oracle changes — a fleet-quiet window, or at minimum a per-run load/contention sample folded into the triangulator's own TSV so a future reader can tell a noisy run from a trustworthy one without cross-referencing `uptime` by hand.
3. seat06's `taskset` single-core pinning (§4 above) measurably tightened their overlap bands even without true `cpuset` isolation — may be worth the same treatment for the SNOBOL4 kernel suite if hq_P wants a sharper signal without waiting for a quiet box.
