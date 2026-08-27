# FINDING — `handoff_status.sh`'s own `util_verify_s_artifacts_owed.sh` check runs `make pristine` against the SAME live tree a session may be building, with no lock, and can silently corrupt it

**Seat:** `seat03` · 2026-08-27 · found while working `vlist-v05-m4-sigsegv-m3-m4-divergence` (unrelated to that row's own defect — this is build infrastructure, not codegen)
**Tree:** SCRIP `82663608`

## 1. What happened

Session-start `make pristine` failed twice in a row with `/usr/bin/ld: cannot find out/rt_pic-<tag>/<name>.o` for a shifting ~20-file subset, despite every named source file existing and compiling cleanly in isolation. First failure was self-inflicted (a botched `nohup make pristine &` of my own escaped harness tracking and raced a second, properly-tracked retry — both `rm -rf`ing and rebuilding `out/rt_pic-<tag>/` concurrently). That was found and fixed (killed the orphan, confirmed via `/proc/<pid>/cwd`).

**The second failure had no such cause.** After the orphan was dead and exactly one `make pristine` was running in my own tree, it *also* failed the same way. `ps -eo pid,ppid,lstart,cmd` traced the surviving process's parent chain:

```
make pristine (1985392) ← util_verify_s_artifacts_owed.sh (1985380) ← handoff_status.sh (1985379)
    ← handoff_status.sh (1984787) ← timeout 300 bash handoff_status.sh (1984784) ← systemd --user
```

This is **not mine** — it is the `Stop` hook's own `s4e_msg.sh banner` chain (RULES.md § THE MAIL CHANNEL: the `Stop` hook fires every time a session stops responding, and the banner it prints depends on `handoff_status.sh`, which per RULES.md's Handoff sequence step 4 runs `util_verify_s_artifacts_owed.sh` as a WARN-only check). That script's own doc comment says it checks for owed `.s` artifacts "against a disposable LOCAL CLONE of corpus" — **but the `make pristine` it runs to get a working compiler is against the real, live SCRIP tree** (`cwd=/home/claude03/SCRIP`, confirmed directly), not a disposable copy. Only the corpus half is isolated; the compiler build is not.

## 2. Why this matters beyond my own self-collision

A session that is mid-build (any `make`/`make pristine`, for any reason — a gate run, a rebuild after `git pull --rebase`, anything) and then **stops responding for any reason while that build is still running** — waiting on its own background task, a tool-permission prompt, anything that yields a turn — will have the `Stop` hook fire `handoff_status.sh` → `util_verify_s_artifacts_owed.sh`, which starts its **own, independent** `make pristine` (`rm -rf $(OBJ) $(RT_OBJDIR) ... ./scrip` then rebuild) against the exact same tree, with **no lock, no check for an in-flight build, no coordination of any kind**. Two `make pristine` processes racing in one tree reliably produces exactly the missing-object signature above: whichever one's `rm -rf` fires while the other has partially rebuilt wins, and the loser's link step fails against files that no longer exist.

This is a **general, silent, fleet-wide hazard**, not specific to this seat or this row: any session whose own build happens to still be running when it yields a turn is exposed to it, and the resulting failure (`ld: cannot find X.o`) looks exactly like a source or Makefile defect — costing real time misdiagnosing infrastructure noise as a code bug (it cost this session most of a turn before the true cause was traced via `/proc/<pid>/cwd` and parent-chain walking).

**Separately, and additionally:** at the moment this was measured (07:03–07:20), `ps aux` showed every one of the 16 seats plus `hq_P`/`hq_C` running `make pristine` (or equivalent) concurrently on this one shared box — a real, unavoidable resource-contention window at fleet-wide session start that is outside any one seat's control and not itself a defect, just worth naming as the backdrop this race was found against.

## 3. What was NOT done

This is filed as a FINDING, not a fix — `handoff_status.sh`/`util_verify_s_artifacts_owed.sh` is HQ-minted infrastructure (hq_C, s272) outside this row's lane, and no source or script change was made. Evidence (PIDs, timestamps, parent chains, log excerpts) is reproducible on any seat by watching `ps -eo pid,ppid,lstart,cmd | grep handoff_status` during a session-start build.

## 4. Suggested direction (not a ruling — HQ's call)

`util_verify_s_artifacts_owed.sh`'s own `make pristine` needs either: (a) a lock file / mutex so it refuses or waits rather than racing a concurrent build in the same tree, or (b) to build in a disposable worktree copy the way it already does for corpus, or (c) to skip its own rebuild and reuse whatever `scrip`/`out/libscrip_rt.so` already exists if one is present and not mid-build. Any of the three would remove the race; which is HQ's call, not this row's.

## 5. Recovery used this session

Killed only the process tree confirmed (via `/proc/<pid>/cwd`) to be my own orphan; left the `handoff_status.sh`-owned build alone once identified; after it finished (also failed, same signature, consistent with the race having already been in progress before I could tell it apart from mine), ran one further solo `make pristine` with no competing process in the tree — succeeded cleanly (`scrip` 221488 bytes, `libscrip_rt.so` built, verified against `corpus/probe/vlist_select/c01` and the full `test_corpus_snobol4.sh` gate: 365/365 both modes).
