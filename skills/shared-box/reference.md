# The shared box: the reference

Verified 2026-11-01 against the live cgroup tree, `harness/scripts/` and `/home/resources/`. The design of record was CEO-2041 (2026-10-30), amended by CEO-2105 (the door, the weights) and CEO-2108 (the helper rule).

## 1. The tree

```
user-1000.slice
├─ session.slice                       the desktop session (untouched)
├─ cron session scopes                  each cron line re-homes itself into s4e-batch.slice with systemd-run --user --scope
└─ user@1000.service
   ├─ app.slice (weight 100)
   │  ├─ app-org.gnome.Terminal.slice   CPUWeight 100, MemoryHigh 20G, MemoryMax 24G
   │  │  └─ vte-spawn-<id>.scope        one per seat: CPUWeight 100, CPUQuota 400%, MemoryHigh 4G, MemoryMax 8G, MemorySwapMax 1G, TasksMax 2048
   │  ├─ app-s4e.slice/app-s4e-<seat>.slice   a seat's classless graded runs (so the census sees short-lived scopes)
   │  └─ the desktop's own scopes      no cap (protected by everyone else's caps)
   └─ s4e.slice (weight 100)
      ├─ s4e-grader.slice              CPUWeight 300, MemoryMax 10G: loop8.sh, tier1.sh, their children
      └─ s4e-batch.slice               CPUWeight 50, MemoryMax 12G: one 8 GB scope per job
```

A session of Lon's own (a non-seat root) gets CPUWeight 1000 and no cap; Lon's `!` commands inside a seat's tab run under that seat's door by design.

## 2. The registration and the ledger

- `s4e_session_start.sh` (the SessionStart hook, written into every root's `settings.local.json` by `util_fleet_settings.sh`, which Lon runs) reads its scope from `/proc/self/cgroup`, appends `seat, scope, pid, start` to `/home/resources/progress/SEATS.tsv` and applies the class properties. `--check` reads every seat scope's live weight and quota; `--pid <pid>` re-places one session; a helper prints SKIPPED.
- `util_seat_census.py` samples every scope's `cpu.stat`, `memory.*`, `pids.current`, the pool holders and each seat's /tmp, and appends to `LOAD.tsv` every five minutes from cron inside the batch slice. `now` prints the table.

## 3. The handshake of a sitting (the order every seat keeps)

1. Pull the four repos fast-forward. 2. `make` in the root: a clean root at origin's head fetches and compiles nothing. 3. Read MODE, the cursor, the batons, the inbox. 4. Answer every claim notice (overlap by population) and every ask before the first edit. 5. Take one row; cure it in a scratch worktree under the seat's own caps. 6. Prove with the handful (reps, smokes) and ask the coo for the suite by test request, never by running a board. 7. Land by the relay (code repos first, `.github` last). 8. Record: NEXT, LEDGER, cursor, `done`, `handoff_status.sh`.

## 4. The talk and the reply

| the talk | to | the reply |
|---|---|---|
| a claim notice | the cto and every live holder in the lane | "no overlap by population", naming the files, or the overlap and the order agreed, before the next edit |
| an ask (a ruling, a design gap, a dialect question) | the cto | the ruling in the owning skill's DESIGN section and a telegram, the same sitting; the asker carries on under a stated assumption |
| a test request (at most eight programs) | the coo | the verdict by telegram, from the progress store when it holds the tree |
| a landing | nobody | the key is the announcement: every root's next `make` fetches it; the coo's tier 1 grades it |
| an alarm (/tmp, load, a broken oracle, a dead mailbox) | the cto | the cure or the owner named, within the hour |
| a grant ask (a global, a runtime field, a permission prompt) | the cto, who puts it to Lon | Lon's word relayed verbatim; nothing lands before it |

## 5. What is forbidden

- `nice`, `ionice` or `cpulimit` in the harness (invisible across cgroups); a `cpu.max` cap on a class (the per-seat door is the one quota).
- A pool sized from the load average; a `make -j` above the seat cap in a script.
- A cache without a tree-hash key, read from a dirty tree, storing a board's verdict, or written in place (atomic rename only).
- A second ledger beside `LOAD.tsv`; a `ps`-based per-seat figure; a load number in a telegram that is not a `LOAD.tsv` reading.
- A ulimit on address space (the collector reserves `PROT_NONE`), `MemorySwapMax` unset on a seat or board scope, a cap on Lon's class.
- A calendar: the ROSTER and the weights are the schedule.
- A batch job outside `util_batch.sh`; a live oracle outside `util_oracle.sh`; a weighted scope or slice created by hand (only the hook and `util_batch.sh` create them).
- `pkill -f` a pattern (all seats share one OS user): kill only the PIDs you spawned.

## 6. The roll-out (CEO-2041's rows, state on 2026-11-01)

Steps 1 (the census), 2 (Lon's settings script), 3 (pool caps), 4 (the batch class), 6 (the build cache) and 7 (the check cache) are DONE. Step 5 (the grader in its slice, DONE-WHEN `util_seat_census.py --grader-rate`) is CLAIMED by the coo; step 8 (memory and /tmp, `--memory-check`) is PARKED; step 9 (the acceptance over a working day, `--acceptance 86400`) is the cto's; step 10 (the door and the helper rule, CEO-2105/2108) is ASSIGNED to the coo. The five numbers that say the box hums: builds fetched against compiles, `SLOT_WAITS.tsv` seconds per seat per hour (finish: none over 300), the grader's programs per hour (200 or more at 12 busy cores), cpu pressure under 30, /tmp under 60 percent.
