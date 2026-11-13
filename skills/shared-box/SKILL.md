---
name: shared-box
description: The one box every seat shares: the cgroup tree and seat scopes, the compile and run pools, the build cache, the ledgers, memory and /tmp rules, util_batch.sh. REQUIRED by the skill gate before editing the slot, batch or tick scripts.
---

# The shared box (CEO-2041, CEO-2105, CEO-2108)

Nineteen seats share 16 cores and about 30 GB. The kernel divides CPU by weight inside each cgroup; the pools bound how many compiles and runs exist; the caches make every tree's build, check and oracle answer happen once. Detail and the forbidden forms are in `reference.md` beside this file.

## 1. Where your work runs (live values, read 2026-11-01)

- **Your session scope is the door** (CEO-2105): every child of your session inherits `CPUQuota=400%`, `cpu.weight 100`, `MemoryHigh 4G`, `MemoryMax 8G`, `MemorySwapMax 1G`, `TasksMax 2048`, set by the `SessionStart` hook (`harness/scripts/s4e_session_start.sh`) from `BUDGET.tsv`'s `@SEAT` row. A spawned seat's scope, `s4e-seat-<seat>.scope` under `s4e-seats.slice`, is made by `spawn_fleet.sh` with the quota and the memory caps, and the hook applies the row less its `CPUQuota`, which `box_controller.sh` moves (the coo 2026-11-12 18:2x: before that cure all 33 seat scopes read no `MemorySwapMax` and no `TasksMax`). A seat's scope weighted wrong is restored by `s4e_session_start.sh --pid <session pid>`, never by hand.
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
- **The shared files** (the cio 2026-11-12, on Lon's "Can not ALL the seats share a corpus repo?" / "We should save huge space this way."): one read-only checkout of corpus, harness and .github under `/home/resources/shared`, kept at origin/main by `util_shared_pristine.sh update` under one lock; `util_relink_root.py ROOT` makes each clean tracked file of a root whose blob equals the pristine's a hard link to it and marks the repo `s4e.shared`, and `util_sync_root.sh` relinks a marked repo after its merge. A root keeps its own directories, so every relative path works and there is no symlink; its objects are borrowed from the coo root (`git clone --shared`; `git repack -A -d -l` drops a converted root's copies). MEASURED on the cio root: 2.7G of files and 4.4G of packs freed in under a minute, `fsck` clean. A pull or checkout replaces a file by a new inode, so a tree moves only at its own sync; an in-place write to a linked file fails EACCES instead of reaching every seat (`util_shared_pristine.sh selftest`, eight arms on scratch repos). A seat root carries the FULL corpus; sparse is for worktrees only (`s4e_worktree.sh`), and the links make the full tree cost nothing (the coo 2026-11-12 18:0x, on junior_13's measurement: fifteen roots made sparse by `populate_numbered_seat.sh` hid `demos/` and `benchmarks/`, so every demos suite listed 0 members there; the cio ran `git -C corpus sparse-checkout disable` then the relink on each and cured the script). Never chmod a pristine or a linked file writable; never `git gc`, `prune` or `repack` the coo root, whose objects every root borrows. SCRIP and its `out/` stay copies (the cto 2026-11-12, measured: a file's mtime lives on its inode, so a linked `out/` would let one root's make or fetch move every root's build times and defeat make and `gate_require_fresh`; that waits on a freshness contract read from `out/buildinfo`'s key, SCRIP's to cut). In the shared repos only git reads the mtime: no Makefile rule has a prerequisite in `../corpus` or `../harness`.

## 5. Memory and /tmp

- A runaway is killed inside its own cgroup: your scope at 8 GB, a batch or board scope at 8 GB. Bound an experiment's memory with a cgroup (`util_mem_scope.py`), never with a timeout.
- `memory.current` counts page cache: a scope over `memory.high` with small `anon` in `memory.stat` is file pages, and `echo 2G > memory.reclaim` in the scope's own cgroup frees them without killing anything.
- Large outputs die in `/tmp`, never under a root; the harness places its scratch under `/tmp/s4e/<seat>`; `util_tmp_sweep.sh` (cron, the batch slice) ages it out. `/tmp` is shared by every seat: an ENOSPC fakes reds, so `df /tmp` before believing one.

## 6. Measuring

Instruction counts (`util_instr_count.sh`) run at any load. A clock runs only inside `util_quiet_slice.sh` (it drains both pools and takes the top weight; it refuses inside a held run slot). The ledgers: `util_seat_census.py now | --check | --memory-check | --health | --grader-rate | --acceptance` over `LOAD.tsv` and `SEATS.tsv` in `/home/resources/progress/`.

## 7. DESIGN: box-budget (CTO-474, CTO-475, CTO-478; `harness/designs/box_budget/STEPS.tsv`, `test_design_box_budget_steps.sh`)

The full text of this section (about 2 KB) is in `reference.md` beside this file, under the same heading, moved there verbatim on 2026-11-06 so the skill loads light (Lon: "Go and trim any skill that needs it."). Read it before executing, cutting or ruling on a step of this design.

## 8. DESIGN: box-scheduler (CTO-496; `harness/designs/box_scheduler/STEPS.tsv`, `test_design_box_scheduler_steps.sh`; Lon 2026-11-04: "It appears COO needs help re-designing the ENTIRE FLEET system. It is a failure." / "There has been talk, and only talk, about using industry recognized ways of doing make and build load balancing and management." / "So get to it.")

The full text of this section (about 11 KB) is in `reference.md` beside this file, under the same heading, moved there verbatim on 2026-11-06 so the skill loads light (Lon: "Go and trim any skill that needs it."). Read it before executing, cutting or ruling on a step of this design.

## 9. DESIGN: fleet-control (the cio, 2026-11-07, on Lon's word: "SCRAP it and do it again the correct way"; `harness/designs/fleet_control/STEPS.tsv`, `test_design_fleet_control_steps.sh`)

The full text is `reference.md` section 9: the measurements of 2026-11-07, the law (kernel-enforced limits, fixed work once per hash, one controller on PSI, measured outcomes only, the cio's hand), the tools and the eight steps. It supersedes the 71 live rows of sections 7 and 8 and of fleet-queue, test-cycle, batch-grader and shared-development.
