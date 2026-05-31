# GOAL-SILLY-SYNC-MONITOR — Silly Sync Monitor

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ ABSOLUTE RULE — ZERO C BYRD BOX FUNCTIONS — NO EXCEPTIONS — READ THIS BEFORE WRITING CODE  ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                  ║
║  A C Byrd box (C BB) is ANY C function with this signature:                                     ║
║                                                                                                  ║
║      DESCR_t foo(void *zeta, int entry)                                                         ║
║                                                                                                  ║
║  implementing four-port logic (α / β / γ / ω).                                                  ║
║                                                                                                  ║
║  THERE MUST BE ZERO OF THESE IN THE CODEBASE. NOT ONE. NONE. EVER.                              ║
║                                                                                                  ║
║  ALL Byrd boxes are x86 ASSEMBLY emitted at runtime by the emitter.                             ║
║  If you want a BB, you EMIT it. You do not write a C function for it.                           ║
║                                                                                                  ║
║  The only permitted C functions with (void *zeta, int entry) signature are:                     ║
║    • icn_lazy_box  — infrastructure shim, not a generator                                       ║
║    • icn_bb_dcg    — infrastructure DCG driver, not a generator                                 ║
║                                                                                                  ║
║  If you just wrote DESCR_t foo(void *zeta, int entry) { ... } — DELETE IT.                     ║
║  Implement it as an IR_block_t DCG (ir_exec.c + lower_icn.c) driven by icn_bb_dcg.             ║
║  See IR_ICN_UPTO in ir_exec.c and lower_icn_upto() in lower_icn.c as the template.             ║
║                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

**Repo:** SCRIP (`test/ss-monitor/`)
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
/home/claude/csnobol4/snobol4   # CSNOBOL4 oracle binary
/home/claude/SCRIP/src/silly/            # Silly source
/home/claude/SCRIP/test/ss-monitor/      # monitor infrastructure (to be built)
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

- Build CSNOBOL4: `bash /home/claude/SCRIP/scripts/build_csnobol4_oracle.sh`. See REPO-csnobol4.md.
- Test gate passes before every commit.
- Commit as `LCherryholmes` / `lcherryh@yahoo.com`.
- Rebase before every .github push.
- See RULES.md for full rules including handoff checklist.

## Participant table

| # | Participant | Role | Binary |
|---|-------------|------|--------|
| 1 | CSNOBOL4 2.3.3 | **Oracle** | `/home/claude/csnobol4/snobol4` |
| 2 | Silly SNOBOL4 | **Target** | `/tmp/silly-snobol4` |

CSNOBOL4 is oracle by construction — it IS the reference for Silly. When they agree: correct. When they diverge: Silly is wrong.

## FIFO protocol (per function hook)

```
csn.evt  ← CSNOBOL4 writes events, controller reads
csn.ack  ← controller writes G/S, CSNOBOL4 blocks reading
sly.evt  ← Silly writes events, controller reads
sly.ack  ← controller writes G/S, Silly blocks reading
```

Per hook:
1. Participant writes `"ENTER funcname\n"` or `"EXIT funcname result\n"` to `*.evt`
2. Participant **blocks** on `read()` from `*.ack`
3. Controller reads one event from each `*.evt`
4. Same function name and kind? → write `G` to both `*.ack`
5. Diverges? → write `S` to both, print divergence, stop

Infinite loop detection: FIFO silent for >10 seconds = that participant is looping. Last event before silence names the function entered but never returned.

## Invariants

- Build gate throughout: `gcc -Wall -Wextra -std=c99 -g -O0 src/silly/*.c -lm -o /tmp/silly-snobol4 -I src/silly` clean
- Never modify `snobol4.c` logic — only add wrapper layer
- Monitor infrastructure lives in `test/ss-monitor/` — never mixed into `src/`

---

## Session Setup

```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
bash /home/claude/SCRIP/scripts/build_csnobol4_oracle.sh
bash /home/claude/SCRIP/scripts/build_spitbol_oracle.sh
bash /home/claude/SCRIP/scripts/build_monitor_ipc_shared_library.sh
bash /home/claude/SCRIP/scripts/build_ss_monitor_harness.sh
```
