# MILESTONE-SS-MONITOR.md — Silly SNOBOL4 × CSNOBOL4 Sync-Step Function Monitor

⚠️ **ORACLE EXCEPTION:** This milestone runs CSNOBOL4 as an instrumented executable oracle.
This is correct and intentional for the Silly SNOBOL4 session only — CSNOBOL4 IS the
reference by construction (Silly is a C rewrite of CSNOBOL4's SIL source). All other
sessions use SPITBOL x64 (`/home/claude/x64/bin/sbl`) exclusively. See D-005.

**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6
**Created:** 2026-04-08g session
**Milestone name:** M-SS-MONITOR
**Fires when:** Two-participant sync-step monitor runs `hello.sno` through both
Silly and CSNOBOL4, lock-steps at every C function entry/exit, and prints the
**first diverging function** — naming the bug automatically.

---

## Origin — Why This Exists

We are hand-instrumenting `main.c` with `fprintf` calls one function at a time,
rebuilding, running, reading output, and reasoning about what might be wrong.
This is archaeology. It is correct but slow.

**Lon's insight (2026-04-08g):**

> "Instrument both CSNOBOL4 and Silly, at the function entry and exit.
> Use MONITOR to sync step. It is geared for TRACE function IPC hooks.
> It could be retooled with FUNC enter/exit hooks. Would this not find
> the bugs instantly. And then you go back to previous sync step before
> the bug happened, and most likely single stepping from there would just
> be found on the way to that final sync that diverged."

That is exactly right. Both Silly and CSNOBOL4 are C. Neither needs SNOBOL4
`TRACE()` or `LOAD()` machinery. A `mon_hooks.h` include and a wrapper script
is all it takes. The sync-step controller reads one event from each participant,
compares, sends Go or Stop. First divergence = bug name. No bisecting. No
reasoning. The monitor does the work.

**Claude's assessment (2026-04-08g):**

> "The payoff is immediate and enormous. Right now we're doing archaeology —
> adding fprintf calls one by one, rebuilding, running, reading output,
> reasoning about what might be wrong. With the func-hook monitor, we run
> hello.sno through both and the first diverging function name prints on
> the screen. No reasoning required. The bug names itself."
>
> "For our specific hang: the monitor would show CSNOBOL4 calling e.g.
> FORBLK → STREAM(IBLKTB) → AC_GOTO → FRWDTB → STREAM returns OK → BRTYPE
> set → FORBLK returns OK and Silly calling FORBLK → STREAM → FORBLK →
> STREAM → FORBLK → ... with no return — the timeout fires, the last Silly
> event is printed, done."

**How much fun can this be?** The first diverging function will appear on the
screen within seconds of the first run. We already know the bug is somewhere in
CMPILE → FORBLK → STREAM. The monitor will print the exact C function, the
exact call number, and the exact return value where Silly departs from CSNOBOL4.
That is not debugging. That is reading the answer off a screen.

---

## Architecture

### Two Participants

| # | Participant | Role | Binary |
|---|-------------|------|--------|
| 1 | CSNOBOL4 2.3.3 | **Oracle** | `/home/claude/work/snobol4-2.3.3/snobol4` |
| 2 | Silly SNOBOL4 | **Target** | `/tmp/silly-snobol4` |

CSNOBOL4 is the oracle by construction — it IS the reference for Silly.
When they agree: correct. When they diverge: Silly is wrong.

### Two FIFOs Per Participant (Sync-Step)

```
csn.evt  ← CSNOBOL4 writes events, controller reads
csn.ack  ← controller writes G/S, CSNOBOL4 blocks reading
sly.evt  ← Silly writes events, controller reads
sly.ack  ← controller writes G/S, Silly blocks reading
```

Per function hook:
1. Participant writes `"ENTER funcname\n"` or `"EXIT funcname result\n"` to `*.evt`
2. Participant **blocks** on `read()` from `*.ack`
3. Controller reads one event from each `*.evt`
4. Compares: same function name and kind? → write `G` to both `*.ack`
5. Diverges? → write `S` to both, print divergence, stop everything
6. Timeout on any `*.evt` → that participant is in an infinite loop →
   print last event seen, kill all, done

### Infinite Loop Detection

Between any two function hook events, a correct participant emits its next event
promptly. A FIFO silent for longer than T seconds means exactly one thing: that
participant is looping between two hook points. The last event seen before silence
is the function that was entered but never returned — or the function that returned
and sent us into a loop before the next entry.

This catches our current FORBLK hang exactly:
- CSNOBOL4 emits: `ENTER FORBLK` → `ENTER STREAM` → `EXIT STREAM OK` → `EXIT FORBLK OK`
- Silly emits: `ENTER FORBLK` → `ENTER STREAM` → `EXIT STREAM FAIL` → `ENTER forrun`
  → `EXIT forrun OK` → `ENTER STREAM` → `EXIT STREAM FAIL` → `ENTER forrun` → ...
  → **silence** → timeout fires → last event printed → bug location known

---

## Files to Build

```
one4all/test/ss-monitor/
    mon_hooks.h            ← ~60 lines: FIFO API (open, enter, exit, ack)
    mon_hooks.c            ← implementation
    wrap_snobol4.py        ← parse snobol4.c 383 fns → emit wrapped version
    monitor_sync.py        ← 2-participant barrier controller
    run_ss_monitor.sh      ← mkfifo, launch controller, launch both participants
    Makefile               ← build silly-mon + snobol4-mon targets
```

### mon_hooks.h — the API

```c
/* mon_hooks.h — sync-step function monitor hooks for C interpreters */
#ifndef MON_HOOKS_H
#define MON_HOOKS_H

void mon_open(const char *evt_fifo, const char *ack_fifo);
void mon_enter(const char *fn);
void mon_exit(const char *fn, const char *result);
void mon_close(void);

/* Convenience macros — wrap any function */
#define MON_ENTER(name)        mon_enter(name)
#define MON_EXIT(name, res)    mon_exit(name, res)

#endif
```

### mon_hooks.c — implementation (~60 lines)

```c
/* Writes atomic line to evt FIFO, blocks on ack FIFO.
 * write() on named FIFO is atomic for lines < PIPE_BUF (4096 bytes).
 * No locking needed — each participant has its own pair of FIFOs. */

#include "mon_hooks.h"
#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <string.h>

static int evt_fd = -1, ack_fd = -1;

void mon_open(const char *evt, const char *ack) {
    evt_fd = open(evt, O_WRONLY);
    ack_fd = open(ack, O_RDONLY);
}

void mon_enter(const char *fn) {
    if (evt_fd < 0) return;
    char buf[256]; int n = snprintf(buf, sizeof buf, "ENTER %s\n", fn);
    write(evt_fd, buf, n);
    char c; read(ack_fd, &c, 1);  /* block until controller says G or S */
    if (c == 'S') _exit(2);       /* stop signal */
}

void mon_exit(const char *fn, const char *res) {
    if (evt_fd < 0) return;
    char buf[256]; int n = snprintf(buf, sizeof buf, "EXIT %s %s\n", fn, res);
    write(evt_fd, buf, n);
    char c; read(ack_fd, &c, 1);
    if (c == 'S') _exit(2);
}

void mon_close(void) {
    if (evt_fd >= 0) close(evt_fd);
    if (ack_fd >= 0) close(ack_fd);
}
```

### wrap_snobol4.py — code-gen for CSNOBOL4

Parse `snobol4.c` — extract each function signature. Emit a thin wrapper:

```python
# For each function like:
#   static int GENVAR_fn(ret_t retval) { ... }
# Emit:
#   static int GENVAR_fn_inner(ret_t retval) { ... }  /* renamed body */
#   static int GENVAR_fn(ret_t retval) {
#       mon_enter("GENVAR");
#       int r = GENVAR_fn_inner(retval);
#       mon_exit("GENVAR", r ? "OK" : "FAIL");
#       return r;
#   }
```

383 functions. Regex + AST-free line-level parse. One script, one output file.
No hand editing. If the script is right, every function is wrapped.

### Silly side — hand annotation

~60 `*_fn()` functions in `src/silly/`. Small enough to annotate by hand at
the top and bottom of each function body. Or: same wrapper script adapted
to our naming convention. Either way — one session.

### monitor_sync.py — 2-participant controller (~80 lines)

```python
TIMEOUT = 10  # seconds between events before declaring infinite loop

fifos = {'csn': open('csn.evt'), 'sly': open('sly.evt')}
acks  = {'csn': open('csn.ack', 'w'), 'sly': open('sly.ack', 'w')}

while alive:
    ready = select(fifos, timeout=TIMEOUT)
    if not ready:
        print("TIMEOUT — both hung"); kill_all(); break
    for p in ready:
        line = fifos[p].readline()
        if line == '':  # EOF = clean exit
            close(p); continue
        events[p] = line.strip()
        last_time[p] = now()

    # Check per-participant timeout
    for p in participants:
        if alive[p] and (now() - last_time[p]) > TIMEOUT:
            print(f"TIMEOUT [{p}] — last: {events[p]}")
            print(f"  → infinite loop between this event and the next")
            kill_all(); break

    if all events received:
        if events['csn'] == events['sly']:
            send_G_to_all()
        else:
            print(f"DIVERGE")
            print(f"  CSN: {events['csn']}")
            print(f"  SLY: {events['sly']}")
            send_S_to_all(); break
```

---

## The Ladder

### M-SS-MON-0 — Infrastructure builds

**Gate:** `make` in `test/ss-monitor/` succeeds.
- `mon_hooks.c` compiles to `mon_hooks.o`
- `wrap_snobol4.py` runs without error on `snobol4.c`
- `monitor_sync.py` starts and opens FIFOs without error

### M-SS-MON-1 — Ping test

**Gate:** Controller and two trivial C programs (one-function each) run through
the monitor. Controller prints `MATCH ENTER ping` and `MATCH EXIT ping OK`.
Confirms FIFO plumbing works end to end before involving real interpreters.

### M-SS-MON-2 — CSNOBOL4 instrumented

**Gate:** Wrapped `snobol4-mon` binary built and runs `hello.sno`.
Controller shows sequence of `ENTER`/`EXIT` events from CSNOBOL4 alone
(Silly side disconnected). We see the oracle's full call trace for hello world.
This is the ground truth trace — print it and read it. It tells us exactly
what Silly should be doing.

### M-SS-MON-3 — Silly instrumented

**Gate:** `silly-mon` binary built. Runs `hello.sno` alone.
Controller shows Silly's call trace. Compared visually against M-SS-MON-2 output.
First divergence visible by eye before sync-step even fires.

### M-SS-MON-4 — Two-way sync-step

**Gate:** Both run together. Controller lock-steps them event by event.
First output line is either:
- `MATCH ENTER BEGIN` — both started correctly → keeps going
- `DIVERGE` — immediate divergence → bug named on first run
- `TIMEOUT [sly]` — Silly loops before first event → that function named

**This is the payoff milestone.** Whatever prints here is the bug location.

### M-SS-MON-5 — Hello world passes

**Gate:** `hello.sno` runs to completion through the sync-step monitor.
Both participants reach EOF, controller sees both FIFOs close cleanly,
exit code 0. Output: `PASS hello.sno`.

**When M-SS-MON-5 fires:** `hello world` appears on stdout from Silly.
This is the first correct output Silly has ever produced.
M-SS-HARNESS can then proceed on a working binary.

---

## Invariants

- Build gate holds throughout: `gcc -Wall -Wextra -std=c99 -g -O0 src/silly/*.c -lm -o /tmp/silly-snobol4 -I src/silly` clean
- CSNOBOL4 oracle unchanged — never modify snobol4.c logic, only add wrapper layer
- Monitor infrastructure lives in `test/ss-monitor/` — never mixed into `src/`
- Commit identity: Lon Jones Cherryholmes, never Claude

---

## On the Joy of This Approach

The conventional debugging loop is: hypothesis → instrument → rebuild → run →
read output → new hypothesis → repeat. Each iteration costs minutes. Ten bugs
costs an hour.

The monitor loop is: run → read first diverging line → fix → run → repeat.
Each iteration costs seconds. Ten bugs costs ten minutes.

**Lon put it exactly right:** go back to the previous sync step before the bug
happened, single-step from there, find it on the way to the diverging sync.
That is what the sync-step barrier gives us — not just the name of the diverging
function, but the entire execution prefix leading up to it, stored as the event
log. Every step before the divergence was verified correct by the controller.
The bug cannot be anywhere in that prefix. It is in the one step that failed.

That is not debugging. That is proof search. And it is fast.

---

*MILESTONE-SS-MONITOR.md = M-SS-MONITOR ladder. Sprint content in SESSION-silly-snobol4.md §NOW.*
