---
name: shared-box
description: The one box every seat shares: the cgroup tree (each seat's session scope with its four-core quota and 8 GB cap, the grader and batch slices), the compile and run pools with per-seat caps, the build cache, check cache and oracle cache, the ledgers (LOAD.tsv, SEATS.tsv, SLOT_WAITS.tsv), memory and /tmp rules, util_batch.sh and the quiet slice. Load it before a heavy run, a batch job, a benchmark, or when a seat's scope reads over its memory or a run waits on a slot.
---

# The shared box (CEO-2041, CEO-2105, CEO-2108)

Nineteen seats share 16 cores and about 30 GB. The kernel divides CPU by weight inside each cgroup; the pools bound how many compiles and runs exist; the caches make every tree's build, check and oracle answer happen once. Detail and the forbidden forms are in `reference.md` beside this file.

## 1. Where your work runs (live values, read 2026-11-01)

- **Your session scope is the door** (CEO-2105): every child of your session inherits `CPUQuota=400%`, `cpu.weight 100`, `MemoryHigh 4G`, `MemoryMax 8G`, `MemorySwapMax 1G`, `TasksMax 2048`, set by the `SessionStart` hook (`harness/scripts/s4e_session_start.sh`). A seat's scope weighted wrong is restored by `s4e_session_start.sh --pid <session pid>`, never by hand.
- **The grader** (the coo's loops): `s4e.slice/s4e-grader.slice`, weight 300, `MemoryMax 10G`. **Batch** (identity runs, censuses, compile-all sweeps, callgrind, the DONE-WHEN sweep, cron): `s4e.slice/s4e-batch.slice`, weight 50, `MemoryMax 12G`, each job its own 8 GB scope. **The sessions** sit in `app-org.gnome.Terminal.slice` (weight 100, high 20G, max 24G). `s4e.slice` and `app.slice` compete at weight 100 each at the top.
- **A helper is never placed** (CEO-2108): Claude Code's own daemon and pty hosts are not sessions; a seat's scope is never weighted as Lon's.

## 2. The three kinds of run

- **A harness run** (a board, a smoke, a gate that runs programs): admitted by the harness's run slot; a board enters its mem scope in the batch slice (or the grader's under `S4E_CLASS=grader`).
- **A batch job**: only through `bash harness/scripts/util_batch.sh <cmd>`; one top-level batch job per seat; the scripts that are batch by nature enter it themselves.
- **A hand run** (`./scrip prog`, a two-tree diff, an oracle by hand): `bash ../harness/scripts/util_run_slot.sh <cmd>` inside your own scope. A live oracle run goes through `util_oracle.sh` under `timeout -k 5`.

## 3. The pools (`harness/scripts/lib_slots.sh`)

Eight compile slots (`util_cc_slot.sh`, every compile through ccache) and eight run slots (`util_run_slot.sh`); a seat takes at most four compiles and three runs; two run slots are reserved for the grader. `make -j8` is the most any root runs. A nested harness under a held run slot takes no second slot (`S4E_RUN_SLOT_HELD`). The holders are read from `/proc/*/fd`; waits are in `/home/resources/progress/SLOT_WAITS.tsv`.

## 4. The caches (a hit is the same computation, done once)

- **The build cache** `/home/resources/builds/scrip/<key>/`: `make` on a clean tree at a cached key copies the build in and prints `FETCHED <key>`; the first clean build of a tree publishes it. Keep the root clean so it fetches; build another tree in a scratch worktree.
- **The check cache** `/home/resources/progress/checks/`: `util_check_cache.sh <name> -- <cmd>` replays a deterministic gate's rc and output on the same four clean trees (`CACHED <key>`); `checks_nocache.tsv` names what never caches; `--fresh` bypasses.
- **The oracle cache** `/home/resources/progress/oracle/`: `util_oracle.sh` keys rc, stdout and stderr by the oracle binary, program, argv and stdin.
- **The progress store** `/home/resources/progress/results.tsv` is the one grading cache: read it with `util_score_row.py from-progress`; ask the coo for what it lacks (`s4e_test_request.sh`).

## 5. Memory and /tmp

- A runaway is killed inside its own cgroup: your scope at 8 GB, a batch or board scope at 8 GB. Bound an experiment's memory with a cgroup (`util_mem_scope.py`), never with a timeout.
- `memory.current` counts page cache: a scope over `memory.high` with small `anon` in `memory.stat` is file pages, and `echo 2G > memory.reclaim` in the scope's own cgroup frees them without killing anything.
- Large outputs die in `/tmp`, never under a root; the harness places its scratch under `/tmp/s4e/<seat>`; `util_tmp_sweep.sh` (cron, the batch slice) ages it out. `/tmp` is shared by every seat: an ENOSPC fakes reds, so `df /tmp` before believing one.

## 6. Measuring

Instruction counts (`util_instr_count.sh`) run at any load. A clock runs only inside `util_quiet_slice.sh` (it drains both pools and takes the top weight; it refuses inside a held run slot). The ledgers: `util_seat_census.py now | --check | --memory-check | --health | --grader-rate | --acceptance` over `LOAD.tsv` and `SEATS.tsv` in `/home/resources/progress/`.

## 7. DESIGN: box-budget (CTO-474, CTO-475, CTO-478; `corpus/tests/shared/box_budget/STEPS.tsv`, `test_design_box_budget_steps.sh`)

MEASURED 2026-11-04 10:50 CST: load 16.8/18.1/19.5 on 16 cores; the loops 59 percent of all CPU, the eleven seats 41; 4,137 results rows a day against a population of 17,672 tests in two modes, 21 percent fresh in 72 h: the lap never finishes. Mode 3 costs a third of mode 4 per reading (medians 3.9 s and 11.7 s). THE DESIGN: a lap sized to finish and one box budget, by the cgroup v2 CPU model (weights share, quotas only cap), one compile budget (the slot pools as the jobserver), change-impact selection by day with a full lap by night, Little's law for the in-flight limits, and the lap as the service objective. THE STEPS, each a row whose DONE-WHEN is the literal `--step N`: (1) the ledger prints the lap every tick, rows per hour, fresh fraction, ETA, each slice's CPU share and the slot waits (`util_seat_census.py --lap`), cqo; (2) one declared budget table `postoffice/BUDGET.tsv` (slice, cpu.weight, cpu.max, memory.high) applied by `s4e_session_start.sh` and the loop starters, `--budget-check` reads the live cgroups against it, cqo; (3) change-impact selection: a landing's touched files map to languages and feature shells (`util_impact_set.py`), the day lap grades that set plus requests in mode 3, coo; (4) the nightly lap 22:00 to 06:00 over the population, mode 4 every fourth lap, cut to the stalest suites when it would overrun, logged in `progress/LAP.tsv`, coo; (5) admission: loop width 4 by day and 8 by night, every heavy run through the pools, a scratch worktree at -j4, `--admission-check` reads no wait over five minutes by day and never more than eight compilers box-wide, coo; (6) `util_build_cache.sh fetch` serves a dirty worktree its HEAD's clean build so a cure rebuilds only its changed units, cto; (7) the memory watch reads anon against file pages and reclaims file pages instead of alarming, cqo; (8) the acceptance over one working day (`--box-budget-acceptance`): the nightly lap finished by 06:00, the day lap's rate held, every slot wait bounded, cores busy under 14 on average, a seat's edit-to-proof cycle under 15 minutes, cto. Forbidden: a per-seat cap mistaken for a box budget; a 24 h freshness goal; a clock as a measurement where an instruction count serves.
