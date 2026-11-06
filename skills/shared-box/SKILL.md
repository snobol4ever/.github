---
name: shared-box
description: The one box every seat shares: the cgroup tree (each seat's session scope with its four-core quota and 8 GB cap, the grader and batch slices), the compile and run pools with per-seat caps, the build cache, check cache and oracle cache, the ledgers (LOAD.tsv, SEATS.tsv, SLOT_WAITS.tsv), memory and /tmp rules, util_batch.sh and the quiet slice. Load it before a heavy run, a batch job, a benchmark, or when a seat's scope reads over its memory or a run waits on a slot.
---

# The shared box (CEO-2041, CEO-2105, CEO-2108)

Nineteen seats share 16 cores and about 30 GB. The kernel divides CPU by weight inside each cgroup; the pools bound how many compiles and runs exist; the caches make every tree's build, check and oracle answer happen once. Detail and the forbidden forms are in `reference.md` beside this file.

## 1. Where your work runs (live values, read 2026-11-01)

- **Your session scope is the door** (CEO-2105): every child of your session inherits `CPUQuota=400%`, `cpu.weight 100`, `MemoryHigh 4G`, `MemoryMax 8G`, `MemorySwapMax 1G`, `TasksMax 2048`, set by the `SessionStart` hook (`harness/scripts/s4e_session_start.sh`). A seat's scope weighted wrong is restored by `s4e_session_start.sh --pid <session pid>`, never by hand.
- **The grader** (the coo's loops): `s4e.slice/s4e-grader.slice`, weight 300, `MemoryMax 10G`. **Batch** (identity runs, censuses, compile-all sweeps, callgrind, the DONE-WHEN sweep, cron): `s4e.slice/s4e-batch.slice`, weight 50, `MemoryMax 12G`, each job its own 8 GB scope. **The sessions** sit in `app-org.gnome.Terminal.slice` (weight 100, high 20G, max 24G). `s4e.slice` (weight 200) outranks `app.slice` (weight 100) at the top (box-scheduler step 7, CTO-496).
- **A helper is never placed** (CEO-2108): Claude Code's own daemon and pty hosts are not sessions; a seat's scope is never weighted as Lon's.

## 2. The three kinds of run

- **A harness run** (a board, a smoke, a gate that runs programs): admitted by the harness's run slot; a board enters its mem scope in the batch slice (or the grader's under `S4E_CLASS=grader`).
- **A batch job**: only through `bash harness/scripts/util_batch.sh <cmd>`; one top-level batch job per seat; the scripts that are batch by nature enter it themselves.
- **A hand run** (`./scrip prog`, a two-tree diff, an oracle by hand): `bash ../harness/scripts/util_run_slot.sh <cmd>` inside your own scope. A live oracle run goes through `util_oracle.sh` under `timeout -k 5`.

## 3. The pools (`harness/scripts/lib_slots.sh`)

Eight compile slots (`util_cc_slot.sh`, every compile through ccache) and eight run slots (`util_run_slot.sh`); a seat takes at most four compiles and three runs; two run slots are reserved for the grader. `make -j8` is the most any root runs. A nested harness under a held run slot takes no second slot (`S4E_RUN_SLOT_HELD`). The holders are read from `/proc/*/fd`; waits are in `/home/resources/progress/SLOT_WAITS.tsv`.

**Admission to a class by GNU sem (fleet-queue step 18, the cio 2026-11-05; the coo and the cio ruled 17:4x).** `harness/scripts/SLOTS.tsv` is the class table (class, id, cap, timeout_s by day, timeout_night_s): `compile` `s4e-compile` 8, `run` `s4e-run` 8 (the grader's `run-grader` 2 plus the seats' `run-seats` 6, so the reservation is a pool, not a third sem), the seat shares `compile-seat` 4 and `run-seat` 3 (id prefix plus the seat name); its caps equal `lib_slots.sh`'s `S4E_*_DEFAULT` lines (the pools gate's arm 5 checks it). `bash ../harness/scripts/util_run_slot.sh --admit <compile|run> <command>...` takes at most TWO sems (the seat's share, then the pool) through a fixed holder, `util_slot_holder.sh`, kept on fd 6 and inherited by the command (a killed holder frees it); a timeout is a NEGATIVE `--semaphoretimeout` and refuses rc 2 with nothing run (a positive one steals the slot after the wait). Use it for a take that is rare and long: a batch job (`util_batch.sh` does), a build, a whole suite run, a landing. The per-entry and per-compile slots stay FLOCK files (`s4e_slot_hold`, `corpus_suite_harness.py _run_slot`): MEASURED 2026-11-05 (`perf stat -e instructions:u`, load 51 on 16 cores) a sem take is 327 M user instructions against 12-19 M for a flock take, and a marginal harness entry is 0.28 G. sem re-parses its argv through a shell, so a user's command never goes through it. `util_run_slot.sh --probe-sem` proves the mechanism on a scratch pool (seat share, pool cap, the grader's pool, two sems at most, kill frees, nested admission, refusals recorded) and prints one `SLOT by=sem class=... id=... cap=... timeout_s=...` line per class. The pool lives in `/tmp/s4e-sem` (`S4E_SEM_HOME`).

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

The full text of this section (about 2 KB) is in `reference.md` beside this file, under the same heading, moved there verbatim on 2026-11-06 so the skill loads light (Lon: "Go and trim any skill that needs it."). Read it before executing, cutting or ruling on a step of this design.

## 8. DESIGN: box-scheduler (CTO-496; `corpus/tests/shared/box_scheduler/STEPS.tsv`, `test_design_box_scheduler_steps.sh`; Lon 2026-11-04: "It appears COO needs help re-designing the ENTIRE FLEET system. It is a failure." / "There has been talk, and only talk, about using industry recognized ways of doing make and build load balancing and management." / "So get to it.")

The full text of this section (about 11 KB) is in `reference.md` beside this file, under the same heading, moved there verbatim on 2026-11-06 so the skill loads light (Lon: "Go and trim any skill that needs it."). Read it before executing, cutting or ruling on a step of this design.

