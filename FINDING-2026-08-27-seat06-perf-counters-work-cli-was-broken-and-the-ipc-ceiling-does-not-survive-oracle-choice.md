# FINDING — seat06: hardware counters WORK here (perf CLI was broken, not the kernel facility), and the IPC-3.20-vs-2.33 "1.4x ceiling" does not survive a re-measurement against the correct oracle

**Date:** 2026-08-27 · **Seat:** seat06 (`/home/claude06`) · **Topic:** row `perf-tooling-hardware-counters` (rank 0, PERF BLOCKER class) · **Status:** STEP 1 of the row's NEXT block, both halves, ANSWERED.
**Machine:** AMD Ryzen 7 PRO 8840U (Zen 4), kernel `6.17.0-1032-oem`, `perf_event_paranoid=1`. **Commits:** SCRIP `a532cfc4ea7a` · corpus `ac5f0db04b31` · .github `d317e0b4611e` (all freshly `pull --rebase`d this session). **RT_OPT `-O0`** (repo default, unchanged). ⛔ **Machine load average 10–21 on 16 cores throughout** — this session directly observed **≥11 concurrent seat roots** (`claude01/02/03/08/09/10/14/15/16/_P` + mine) running `cc1plus` from a live `ps aux`. See §4 for what that does and does not invalidate.

---

## 1. THE CAPABILITY QUESTION: ANSWERED. HARDWARE COUNTERS WORK. `GOAL-HQ-PERFORM.md:248`'s "HARDWARE COUNTERS DO NOT WORK HERE" IS FALSE AS A BLANKET CLAIM.

Tested in the brief's own order:

| step | result |
|---|---|
| `perf stat` (the `/usr/bin/perf` wrapper) | **FAILS**: `WARNING: perf not found for kernel 6.17.0-1032` (exit 2, no measurement) |
| `perf_event_open(2)` direct syscall | **WORKS.** `PERF_COUNT_HW_{INSTRUCTIONS,CPU_CYCLES,CACHE_REFERENCES,CACHE_MISSES,BRANCH_INSTRUCTIONS,BRANCH_MISSES,STALLED_CYCLES_FRONTEND}` all open and read cleanly, both `exclude_kernel=1` and `=0`. Only `STALLED_CYCLES_BACKEND` fails (`ENOENT` — not implemented for this PMU, not a permission error). |
| `/proc/sys/kernel/perf_event_paranoid` | `1` — matches `ARCH-PERF-TOOLING.md:44`'s own note ("own processes fine, kernel symbols not"); not a blocker for self-process counting, confirmed empirically. |
| `rdpmc` | **WORKS.** mmap'd the perf fd's page; `cap_user_rdpmc=1`. Direct low-overhead PMC reads are available, not just the `read()` syscall path. |
| PAPI fallback | Not installed (`papi_avail`/`papi_command_line` absent, `dpkg -l` confirms). Not needed — `perf_event_open` already answers the question. |

**⭐ ROOT CAUSE of the CLI failure, verified via `dpkg -L`:** `linux-tools-6.17.0-1032-oem` — the exact package `ARCH-PERF-TOOLING.md` §1 says to install, and apt history on this box confirms it WAS installed — genuinely does not ship a `perf` binary for this Ubuntu **-oem** kernel flavor. `dpkg -L linux-tools-6.17.0-1032-oem` lists only a directory; the sibling `-oem` tools directories for `6.17.0-{1020,1025}-oem` contain `acpidbg, cpupower, intel-speed-select, rtla, turbostat, usbip, usbipd, x86_energy_perf_policy` — no `perf`, on any of the three. This is a packaging gap for the OEM kernel flavor, not a permission or capability problem, and re-running the §1 install line will not fix it.

**⭐ A WORKING WORKAROUND EXISTS ALREADY ON THIS BOX, UNUSED:** `linux-tools-generic` (a *different*, older kernel's tools package, `6.8.0-138`) IS installed and DOES ship `perf` (`/usr/lib/linux-tools-6.8.0-138/perf`, v6.8.12). Verified it runs `perf stat` against the **actual running** 6.17.0-1032-oem kernel correctly (userspace `perf_event_open` ABI is stable across this version gap):
```
/usr/lib/linux-tools-6.8.0-138/perf stat -e instructions,cycles,branch-misses -- <cmd>
```
produces normal, sane output. This is a real, immediately-usable fix for every seat on this box: point at that binary directly (or fix `/usr/local/bin/perf`/PATH — **not done by this session**, since that is a shared-machine change across ~16 concurrent seats and outside this row's ask; flagging for HQ/Lon to apply if wanted).

**Consequence:** `GOAL-HQ-PERFORM.md:248` and the "Neither is currently reproducible" framing are **corrected by this row**. They ARE reproducible. What was broken was one specific CLI wrapper's kernel-version dispatch, not the PMU, not `perf_event_open`, not the container's privileges.

---

## 2. METHODOLOGY FOR THE RE-MEASUREMENT

Workload: `beauty self-host` (`beauty.sno < beauty.sno`), the same input `FINDING-2026-08-21-s251...` used (`corpus/demo/snobol4/beauty/beauty.sno`, the frozen SPITBOL-portable classic, **not** the live `corpus/crosscheck/beauty` BEAUTY-CN source, which is oracle-ungradable by design per `board_beauty_m1.sh`'s own header).

⭐ **A real methodology trap found and worked around, worth recording:** `beauty.sno` opens with `-INCLUDE 'global.inc'`. Run with CWD = the beauty demo directory (no `.inc` files there), **SPITBOL silently mis-runs**: exits 0, prints `ERROR 285 -- include file cannot be opened` to its own output stream, and produces 3,999 bytes instead of the correct 40,943 — a **plausible, non-crashing, wrong number** if you don't check output length/md5 against the input. `-INCLUDE` resolves relative to CWD for SPITBOL; SCRIP resolves it correctly regardless of CWD (a genuine, minor cross-engine behavioral difference, not investigated further — out of this row's scope). Fix: run with **CWD = `corpus/include/`** (where all the project's shared `.inc` files live), referencing `beauty.sno` by absolute path. Verified byte-identical (md5 `f20461f9114d50414fc925df1482c9b9`, matching the input file exactly — true fixed point) for **all three** binaries below from that CWD, every rep, before trusting any timing off them.

Three binaries, `beauty.sno < beauty.sno`, CWD=`corpus/include/`, 5 reps each:
- `scrip` — freshly built this session (`make`, post-pull, verified fixed-point).
- `x64/bin/sbl -bf` — the checked-in **instrumented** correctness oracle (monitor IPC bridge, per `lib_oracle_flags.sh`'s `sbl_correctness_bin()`).
- `spitbol-bench-oracle/sbl -bf` — the **clean** benchmark oracle (`sbl_clean_bin()`). Verified both `spitbol-bench-oracle/sbl` and `spitbol-bench-oracle/bin/sbl` are byte-identical here (md5 `bcea36eb2c8f9ec243c7cb4986124493`) — no split-binary trap on this box right now. Also verified: `sbl_clean_bin()`'s path in the live `lib_oracle_flags.sh` already correctly reads `/home/resources/spitbol-bench-oracle/sbl` — **the "hardcoded broken path" bug CLAUDE.md describes as verified-broken 2026-08-23 appears already fixed in the current tree.**

Instrument: real `perf stat -x,` (the recovered 6.8.0-138 binary), `-e instructions,cycles,branch-instructions,branch-misses,stalled-cycles-frontend`, one grouped open per run so all 5 counters schedule together (Zen 4 has enough general-purpose PMCs for 5 events — no multiplexing expected and none of the `TIME_ENABLED`/`TIME_RUNNING` divergence checked, noted as a residual gap). **Cross-validated** against an independently-written raw `perf_event_open` + fork/SIGSTOP/exec harness (not the `perf` binary at all) — instruction counts matched the `perf stat` runs to within noise (e.g. x64: 812.7M vs median 811.2M; clean: 232.75M vs median 232.1M), confirming both tools are attached and counting correctly. Cycle-derived metrics (IPC/branch-miss%/frontend-idle%) differed more between the two tools' single-shot runs — expected, see §4 — but **the direction of the headline finding in §3 replicated in both tools independently.**

---

## 3. RESULTS (median of 5 reps, `perf stat`; raw per-rep numbers in LEDGER of the task file)

| | instructions | cycles | **IPC** | branch-miss% | frontend-idle% |
|---|---|---|---|---|---|
| SCRIP m3 | 15,170,506,800 | 7,467,872,585 | **2.0286** | 0.4398% | 14.97% |
| SPITBOL `x64/bin/sbl` (**instrumented**) | 811,249,404 | 378,575,462 | **2.1432** | 0.8582% | 22.40% |
| SPITBOL `spitbol-bench-oracle/sbl` (**clean**) | 232,145,404 | 155,844,968 | **1.4899** | 2.1051% | 33.89% |

Sanity cross-checks against prior findings (all consistent, which is why the IPC finding below is trusted rather than dismissed as noise):
- x64/clean instruction ratio: **3.495×** — matches `ARCH-PERF-TOOLING.md`§8's independently-measured "~3.53x, 71.7% dead weight" almost exactly.
- SCRIP instruction count dropped 26,205M (s251) → 15,170M (now) = **1.727× fewer** — matches `GOAL-SNOBOL4-100.md`'s logged LIVE CURSOR figure "1.8185s → 1.0574s (**1.72×**)" almost exactly.
- SCRIP/x64 instruction ratio now 18.70× vs s251's 32.3× (32.3 / 1.72 = 18.78, matches).

## 4. ⛔ THE HEADLINE: THE "SCRIP WINS EVERY MICROARCHITECTURAL AXIS, IPC 3.20 VS 2.33, 1.4× CEILING" CLAIM DOES NOT SURVIVE, AND NOT IN THE DIRECTION ANYONE ASSUMED

Two independent problems with quoting the s251 numbers as current fact:

**(a) The absolute numbers are stale** — SCRIP's own instruction count has moved 1.72× since s251 (real, logged optimization work), so "3.20" is not even describing today's compiler. Under today's (heavily loaded) conditions SCRIP measures **IPC ≈ 2.03**, not 3.20.

**(b) The comparison is not oracle-invariant — and it *flips the winner*:**
- SCRIP (2.03) vs **x64 instrumented** oracle (2.14): **SPITBOL wins**, SCRIP is 0.95× its IPC.
- SCRIP (2.03) vs **clean** oracle (1.49): **SCRIP wins**, SCRIP is 1.36× its IPC.

Naive intuition says instrumentation (extra monitor call sites) should only ever make SPITBOL's numbers *worse* to remove, i.e. the clean oracle "should" look at least as good as the instrumented one. **The opposite happened**: the clean binary shows meaningfully *worse* IPC, *worse* branch-miss%, *worse* frontend-idle% than the instrumented one, on the same workload, same machine, same time window. This direction reproduced independently in the second (raw `perf_event_open`) harness (IPC 1.55 instrumented vs 1.15 clean). This is **not explained by this row** — no root cause is claimed, just the reproducible fact — and it is exactly the open question `ARCH-PERF-TOOLING.md`§8 flagged and left unanswered ("Flagging the question, not answering it").

**⛔ Confound that must be stated, not hidden:** this machine ran at load average 10–21 (16 cores) for the entire measurement, ~11 other seats compiling concurrently. Cycle-derived metrics (IPC, branch-miss%, frontend-idle%) are genuinely sensitive to cache/scheduler contention in a way raw instruction *retirement* counts are not — which is exactly why `callgrind Ir` is this project's default instrument and hardware counters are the "second half" the row's brief called them. Evidence the finding is not pure noise: (i) 5-rep spread within each binary was tight (SCRIP IPC 2.007–2.087, x64 2.09–2.21, clean 1.47–1.55 — configs never overlap each other's range despite the shared noisy machine); (ii) the qualitative instrumented-vs-clean direction reproduced in a second, independently-coded tool. Evidence it should still not be over-trusted as a precise number: the two tools' single-shot IPC values for the *same* binary differed by 0.4–0.6 absolute IPC, which is the size of the effect being reported. **Net call: the direction (clean oracle ≠ safe-by-default substitution, ceiling is not oracle-invariant) is trustworthy; the exact magnitude is not, pending a quiet-box remeasurement.**

## 5. RECOMMENDATIONS (routed to hq_P — performance HQ owns `GOAL-HQ-PERFORM.md` and `ARCH-PERF-TOOLING.md`; this seat does not self-edit HQ-only files)

1. `GOAL-HQ-PERFORM.md:248` — replace "HARDWARE COUNTERS DO NOT WORK HERE... Neither is currently reproducible" with: counters work (this row); the CLI wrapper was the only broken part; the 1.4×-ceiling arithmetic is now *actively contradicted* by a preliminary re-measurement, not merely unverified — needs a controlled (fleet-quiet, both-oracle) re-run before it can support a ranking decision again.
2. `ARCH-PERF-TOOLING.md` §7's "1.4x asm ceiling" and §8's still-open question — update to point at this FINDING; the ceiling should not be used to rank rows until re-derived cleanly.
3. `GOAL-HQ-PERFORM.md:257`'s session-setup line (`ls /home/resources/spitbol-clean/sbl`) is a stale path — the tree is `/home/resources/spitbol-bench-oracle/sbl` (already correct in `lib_oracle_flags.sh`; this one call site in the HQ goal file was not updated).
4. Fleet-wide `perf` CLI fix available and cheap (`/usr/lib/linux-tools-6.8.0-138/perf` works against the running kernel) — a symlink or PATH fix would restore `perf stat`/`perf record` for every seat on this box. Not applied by this session (shared-machine change, outside this row's scope) — HQ/Lon's call.
5. Any future beauty.sno-vs-SPITBOL timing must run with CWD=`corpus/include/` or equivalent explicit include-path handling — the silent-truncation failure in §2 is a live trap for any future timing script that doesn't check output length/md5.
6. A trustworthy re-run needs a fleet-quiet window (or `taskset`/`cgroup` isolation) — this row's numbers are good enough to overturn "not reproducible" and to flag the oracle-choice sensitivity, not good enough to re-plant a new precise ceiling number.
