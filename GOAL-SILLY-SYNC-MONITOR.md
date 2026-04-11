# GOAL-SILLY-SYNC-MONITOR — Silly Sync Monitor

**Repo:** one4all (`test/ss-monitor/`)
**Done when:** `hello.sno` runs through the two-way sync-step monitor, both participants
reach clean EOF, controller exits 0, Silly produces correct output.

## What this is

A two-participant sync-step function monitor: CSNOBOL4 (oracle) vs Silly SNOBOL4 (target).
Both are C programs. Both are instrumented with `mon_hooks.h` at function entry/exit.
A Python controller lock-steps them event by event. First diverging function = bug name.
No bisecting. No reasoning. The monitor does the work.

⚠️ **ORACLE EXCEPTION (this goal only):** CSNOBOL4 is the oracle here by construction.
Silly is a faithful C rewrite of CSNOBOL4's SIL source. All other sessions use SPITBOL x64.

## Key paths

```
/home/claude/work/snobol4-2.3.3/snobol4   # CSNOBOL4 oracle binary
/home/claude/one4all/src/silly/            # Silly source
/home/claude/one4all/test/ss-monitor/      # monitor infrastructure (to be built)
```

## Steps

- [ ] **S-1** — Infrastructure builds: `mon_hooks.h`, `mon_hooks.c`, `wrap_snobol4.py`, `monitor_sync.py`, `run_ss_monitor.sh`, `Makefile` all compile/run without error. Gate: `make` in `test/ss-monitor/` succeeds.

- [ ] **S-2** — Ping test: controller + two trivial one-function C programs run through monitor. Controller prints `MATCH ENTER ping` and `MATCH EXIT ping OK`. Confirms FIFO plumbing end to end.

- [ ] **S-3** — CSNOBOL4 instrumented: `snobol4-mon` binary built, runs `hello.sno` alone. Controller shows full CSNOBOL4 call trace. This is ground truth — print and read it.

- [ ] **S-4** — Silly instrumented: `silly-mon` binary built, runs `hello.sno` alone. Controller shows Silly call trace. Compare visually against S-3 output. First divergence visible by eye.

- [ ] **S-5** — Two-way sync-step: both run together. Controller lock-steps event by event. First output is either `MATCH ENTER BEGIN`, `DIVERGE`, or `TIMEOUT [sly]`. Whatever prints names the bug.

- [ ] **S-6** — Hello world passes: `hello.sno` runs to completion. Both FIFOs close cleanly. Exit 0. Output: `PASS hello.sno`. Silly produces correct output for the first time.

## Monitor architecture summary

```
csn.evt  ← CSNOBOL4 writes events
csn.ack  ← controller writes G/S, CSNOBOL4 blocks reading
sly.evt  ← Silly writes events
sly.ack  ← controller writes G/S, Silly blocks reading
```

Timeout on any FIFO = infinite loop. Last event seen before silence = the looping function.

## Files to build

```
test/ss-monitor/
    mon_hooks.h        ~60 lines: FIFO API (open/enter/exit/ack)
    mon_hooks.c        implementation
    wrap_snobol4.py    parse snobol4.c 383 fns → emit wrapped version
    monitor_sync.py    2-participant barrier controller
    run_ss_monitor.sh  mkfifo + launch
    Makefile
```

## Commit identity

Always: `LCherryholmes` / `lcherryh@yahoo.com`

## Rules

- Test gate passes before every commit.
- Commit as `LCherryholmes` / `lcherryh@yahoo.com`.
- Rebase before every .github push.
- See RULES.md for full rules including handoff checklist.
