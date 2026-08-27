# FINDING — seat06: STEP 2 quiet(er)-box re-measurement — SCRIP and the instrumented SPITBOL oracle are statistically TIED in IPC (not a SCRIP win, not a SCRIP loss); SCRIP still clearly beats the clean oracle

**Date:** 2026-08-27 · **Seat:** seat06 (`/home/claude06`) · **Topic:** row `perf-tooling-hardware-counters`, STEP 2 (proposed in STEP 1, approved by hq_P same day). **Status:** STEP 2 executed; claim left RUNNING (DONE-WHEN still structurally refuses — no computed criterion exists yet).
**Machine:** AMD Ryzen 7 PRO 8840U (Zen 4), kernel `6.17.0-1032-oem`, `perf_event_paranoid=1`. **Commits (freshly pulled/rebuilt this session):** SCRIP `c8ed9953` (`make pristine` rebuild after the templates→`bb/x86/xa` reorg) · corpus `ac5f0db0` (unchanged since STEP 1 — same tree, apples-to-apples on the corpus axis) · .github `f0b1288f`. **RT_OPT `-O0`** (repo default, unchanged).

⛔ **TREE CAVEAT, stated up front:** between STEP 1 and this measurement, SCRIP's `git pull` also brought in one substantive (non-reorg) change to `src/lower/lower_snobol4.c` (`sno_pat_eff_kind` now also recognizes `&`-prefixed pattern keywords and preserves the original node type on non-match instead of forcing `TT_VAR`). This is **not** a re-run of STEP 1's exact binary — it is today's tree. Fixed-point verified byte-identical on all three binaries before any timing was trusted (see §1), so correctness on this witness is unaffected; the small instruction-count drift from STEP 1 (15,170M → ~15,17-15,20M, see §2) is within normal rep-to-rep jitter for this binary and not obviously attributable to that change, but it is named here rather than silently assumed away, per this project's own transcription/labeling FACT RULES.

---

## 1. FIXED-POINT VERIFIED FIRST (all three binaries)

Same trap as STEP 1: `beauty.sno`'s `-INCLUDE 'global.inc'` requires CWD=`corpus/include/`. From there, `beauty.sno < beauty.sno` on all three binaries produced output **byte-identical to the input** (md5 `f20461f9114d50414fc925df1482c9b9`, 40,943 bytes) — true fixed point, verified on **every one of the 27 timed reps below**, not just once. No mismatch occurred.

## 2. METHODOLOGY — WHAT "QUIETER" ACTUALLY MEANT (stated honestly, not oversold)

hq_P's mail said the box was getting quieter (FLEET-8 declared, redundant per-turn `make pristine` in the Stop-hook banner cured) and to run STEP 2 now rather than wait. **Measured, not assumed:** load average at the start of this row was **6.3–6.8–9.9** (1/5/15-min, 16 cores) — genuinely lower than STEP 1's sustained **10–21**, but this is a **reduction in contention, not a quiet box**: `ps aux` throughout this session continued to show multiple other seats' `cc1plus`/`scrip` processes running concurrently (this is `FLEET-8`, not DUO — 8+ seats are expected to be live). Per-core idle sampling (`/proc/stat`, 0.5s window) showed idle% varying by **20–60 percentage points across cores and shifting between successive samples taken minutes apart** — the "which cores are idle" answer is not stable on this shared box.

**cgroup cpuset isolation was attempted and is NOT available**: this session's own cgroup scope (`user.slice/.../vte-spawn-*.scope`) only has `memory` and `pids` delegated (`cgroup.controllers` at that scope), not `cpuset`, despite `cpuset` being a root controller — true core-exclusive reservation would require root/systemd delegation this session does not have. **Fallback used: `taskset` single-core pinning** (the task's own STEP 2 text names taskset as an acceptable alternative to a literally quiet box) — re-selected to whichever single core sampled most idle immediately before each run (core 5 for the reported run below; an earlier exploratory run used `-c 7,9`, see §4). This pins **our** process to one core; it does **not** prevent other seats' processes from also landing on that core — it only avoids the extra jitter of our own process migrating mid-run.

Workload, oracles, event set, and CWD trap handling: **identical to STEP 1** (`beauty.sno < beauty.sno`, CWD=`corpus/include/`, `perf stat -x,` via the recovered `/usr/lib/linux-tools-6.8.0-138/perf`, events `instructions,cycles,branch-instructions,branch-misses,stalled-cycles-frontend`). **Reps increased from 5 to 11** (odd, for a clean median) given this number is load-bearing for a ceiling decision — cheap to do, each full 3-binary×11-rep sweep completed in well under a minute.

## 3. RESULTS — the reported run (`taskset -c 5`, 11 reps each; full per-rep JSON in the task LEDGER)

| | instructions (median) | cycles (median) | **IPC (median)** | IPC min–max across 11 reps | branch-miss% | frontend-idle% |
|---|---|---|---|---|---|---|
| SCRIP m3 | 15,177,380,226 | 6,928,351,840 | **2.1906** | 2.126 – 2.240 | 0.41% | 15.57% |
| SPITBOL `x64/bin/sbl` (**instrumented**) | 810,330,553 | 369,404,605 | **2.1936** | 2.019 – 2.225 | 0.82% | 23.97% |
| SPITBOL `spitbol-bench-oracle/sbl` (**clean**) | 231,323,437 | 144,140,896 | **1.6048** | 1.530 – 1.697 | 1.98% | 31.05% |

## 4. ⛔ THE HEADLINE, STATED CAREFULLY: THE SCRIP-VS-INSTRUMENTED-ORACLE RANKING DOES NOT SURVIVE EITHER DIRECTION — IT IS NOISE AT CURRENT MEASUREMENT PRECISION

Applying this project's own standard from STEP 1 ("configs never overlap each other's range" as the bar for a trustworthy difference):

- **SCRIP vs clean oracle: ranges do NOT overlap** (2.126–2.240 vs 1.530–1.697). SCRIP beats the clean oracle **1.365x**, consistent in direction and magnitude with STEP 1's 1.362x. **This result is robust** — it has now reproduced across three independent runs (STEP 1 loaded, this session's exploratory `-c 7,9`/5-rep run, and this reported `-c 5`/11-rep run) under three different load/isolation conditions.
- **SCRIP vs instrumented oracle: ranges OVERLAP** (2.126–2.240 vs 2.019–2.225) — medians are within 0.15% of each other (2.1906 vs 2.1936, SCRIP/x64 = 0.9986x). By this project's own overlap criterion, **this is not a measurable difference at 11 reps**, not a SCRIP win and not a SCRIP loss.

**And the sign is unstable across runs, which is itself the finding:** STEP 1 (heavy load) read SCRIP **losing** (0.947x). This session's first exploratory pass (`taskset -c 7,9`, 5 reps, lighter but not-single-core-pinned load) read SCRIP **narrowly winning** (1.032x). This session's more careful pass (`taskset -c 5`, 11 reps) reads **a dead heat inside overlapping noise bands** (0.999x). Three measurements of nominally the same quantity, at three points along a "less contention" gradient, gave three different signs. **The honest conclusion is not "SCRIP now wins" — it is that this specific comparison (SCRIP vs the *instrumented* oracle) has never yet produced a signal that survives this project's own non-overlap bar**, on this shared, non-exclusive machine. The SCRIP-vs-*clean*-oracle comparison, by contrast, has produced a non-overlapping signal every single time it's been measured.

**Consequence for the row's brief:** the s251 "IPC 3.20 vs 2.33, 1.4x ceiling" claim remains what STEP 1 already found it to be — not currently supportable — but this session's data does **not** hand back a new precise ceiling number in either direction against the instrumented oracle. What it *does* hand back cleanly is: **SCRIP is instruction-count-bound relative to the clean oracle by a solid, repeatedly-measured ~1.36–1.4x IPC margin; the instrumented-oracle comparison needs either true core-exclusive isolation (root/cgroup delegation this session doesn't have) or enough reps at true fleet-quiet to shrink the overlap, before it can support a ranking claim at all.**

## 5. RECOMMENDATIONS (routed to hq_P — sovereign over `GOAL-HQ-PERFORM.md`/`ARCH-PERF-TOOLING.md`; this seat does not self-edit HQ-only files)

1. Do not re-plant a SCRIP-vs-instrumented-oracle ceiling number from this row at all — the honest state is "not distinguishable from noise at 11 reps under partial isolation," not a number.
2. The SCRIP-vs-clean-oracle ~1.36x IPC margin *is* trustworthy (non-overlapping across three independent measurement conditions) and can be cited as such if a clean-oracle-relative ceiling is useful.
3. True core-exclusive isolation needs `cpuset` cgroup delegation (or root) that this session's scope does not have — a shared-machine/ceo-level ask if a tighter instrumented-oracle number is ever wanted, same category as the `perf` PATH fix STEP 1 already routed to ceo.
4. Claim left RUNNING; DONE-WHEN is still prose (see task file) — this row is not closable by measurement yet and this session is not minting a DONE-WHEN unilaterally for someone else's row.

Full per-rep raw JSON (both the exploratory 5-rep/`-c 7,9` pass and the reported 11-rep/`-c 5` pass) recorded in the task file's LEDGER, `/home/resources/postoffice/tasks/perf-tooling-hardware-counters.task.md`.
