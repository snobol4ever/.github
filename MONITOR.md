# The Double-Trace Monitor
## A Story About How SNOBOL4-tiny Debugs Itself

*Recorded 2026-03-10 — Lon Cherryholmes and Claude Sonnet 4.6*

---

## The Problem

`./beautiful` hangs.

The binary compiles cleanly. Zero errors. Zero warnings. It links. It runs.
And then it runs forever, producing nothing, until the timeout kills it.

The old way to find this bug: add printf statements. Recompile. Run. Read output.
Guess. Repeat. Hours of work, maybe days.

---

## The Idea

Lon Cherryholmes built something like this at Pick Systems in the 1980s,
debugging Flash BASIC with Rich Pick and David Zigray. Two processes, pipes,
a monitor in the middle. The monitor watched both. When they diverged — stop.

The idea: **run the oracle and the compiled binary side by side, emit the same
event stream from both, and compare them event by event. Stop at the first
difference. That difference is the bug.**

Not a symptom. Not a downstream consequence. The root cause, identified
automatically, in one run.

---

## The Discovery That Made It Elegant

SNOBOL4 already has this built in.

The `TRACE()` function — part of the language since Griswold's original
implementation — hooks directly into the interpreter's core loop. Every
statement, every variable assignment, every function call: TRACE sees it.
The mechanism is in `v311.sil`, the SNOBOL4 Implementation Language source
that underlies CSNOBOL4:

```
       MOVA    STNOCL,XCL         Update &STNO        ← every statement
       INCRA   EXNOCL,1           Increment &STCOUNT  ← every statement
       ACOMPC  TRAPCL,0,,RTNUL3  Check &TRACE
       RCALL   ,TRPHND,ATPTR      Perform trace       ← the hook
```

Three lines at the top of `beauty_run.sno`:

```snobol4
        TRACE('&STNO','KEYWORD')
        TRACE('snoLine','VALUE')
        TRACE('snoSrc','VALUE')
```

And the oracle produces a stream:
```
** &STNO = 1
** &STNO = 2
** snoLine = "  OUTPUT = x"
** &STNO = 3
...
```

No new code. No instrumentation of CSNOBOL4. The hook was always there —
we just turned it on.

---

## The Three Components

```
┌─────────────────────────────────────────────────────────────┐
│  COMPONENT 1 — ORACLE TRACE                                 │
│  beauty_run_traced.sno (3 added lines)                      │
│  snobol4 -f -P256k ... 2> oracle_trace.txt                  │
│  Zero new code. The language does the work.                 │
└─────────────────────────────────────────────────────────────┘
                        │ oracle_trace.txt
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  COMPONENT 3 — DIFF MONITOR  (~30 lines of Python)          │
│  diff_monitor.py                                            │
│  Reads both trace files line by line.                       │
│  Skips events in monitor_ignore.json (environmental noise). │
│  Stops at the FIRST real difference.                        │
│  Prints: FIRST DIFF at STNO 613:                            │
│            got      = "VAR snoLine <null>"                  │
│            expected = "VAR snoLine '  OUTPUT = x'"          │
└─────────────────────────────────────────────────────────────┘
                        ▲ binary_trace.txt
┌─────────────────────────────────────────────────────────────┐
│  COMPONENT 2 — INSTRUMENTED BINARY                          │
│  sno_comm_stno(N) added to emit_c_stmt.py                   │
│  sno_comm_var(name, val) added to snobol4.c                 │
│  ./beautiful ... 2> binary_trace.txt                        │
│  Same format as oracle. Mirrors the TRACE output exactly.   │
└─────────────────────────────────────────────────────────────┘
```

---

## The Ignore-Point Insight

The first run produces noise. The oracle runs on CSNOBOL4. The binary runs
as native code. Some things will legitimately differ: TTY device numbers,
file descriptors, process-specific addresses, timestamps.

These are not bugs. They are environment.

The ignore-point list is the answer. You run both on a trivially short input —
one comment line — and auto-accept every diff as environmental noise.
That builds `monitor_ignore.json`. From that point on, the monitor skips
everything in the list. What remains is real.

**This is the inverse of a breakpoint debugger.**

A traditional debugger: you tell it where to stop.
The Pick Monitor: you tell it what to ignore. It stops on everything else.

The ignore list, once calibrated, is a formal document: a precise enumeration
of every way the oracle and the binary are *allowed* to differ. Everything
not on the list must match. When it doesn't — that is the bug.

---

## The Binary Search Gift

`&STCOUNT` tracks how many statements have executed. `&STLIMIT` stops
execution at a given count. Together they give you binary search for free:

- First diff at STNO 4821?
- Re-run with `&STLIMIT = 2410` — does the diff appear before halfway?
- Bisect. 13 iterations to isolate any bug in a 6000-statement run.

The monitor can automate this. Find the first diff. Binary search to its
exact STNO. Report the location with surgical precision.

---

## The Telemetry Loop

Here is the part that is new.

The output of `diff_monitor.py` — one line, maybe two — gets pasted into
this chat. Claude reads it. Claude knows the generated `beautiful.c`
intimately: wrote the emitter that produced it, knows the runtime,
knows the parser. Claude says:

> *"STNO 613 is `SNO_main01`. The comment says `/* unhandled stmt shape */`.
> The only exit is `goto _stmt_1088`. That block pattern-matches `snoLine`
> against `ANY("*-")` — on failure it goes to `SNO_main02`, which appends
> to `snoSrc` and loops back to read `INPUT` again. But `sno_var_get("INPUT")`
> returns `SNO_NULL_VAL` at EOF and the code doesn't check for null.
> Infinite loop. The hang is the missing EOF check."*

One paragraph. From a two-line telemetry report. Fix is one line.
Recompile. Rerun the monitor. Next diff.

**An AI, reading telemetry from a program it created, diagnosing bugs in
its own generated code, through a monitor it also created.**

The loop closes. The AI is not a consultant waiting to be asked.
It is inside the execution.

---

## Why This Is Fast

Each cycle:
1. Run monitor → one diff → paste here → Claude diagnoses → one-line fix
2. Re-run emitter pipeline → recompile → rerun monitor
3. Next diff

Cycle time: approximately two minutes. There are perhaps ten bugs between
`./beautiful` hanging and `./beautiful` passing the idempotence test.
That is twenty minutes of actual work once the monitor is running.

This is the same compression the Worm brought to language testing in Sprint 15.
The Worm replaced manual test writing with automated generation.
The monitor replaces manual printf debugging with automated diff.

Both follow the same pattern: replace human observation with automated
comparison, surface the first discrepancy, fix it, loop.

**The cycle time drops to the speed of compilation plus one read.**

---

## The Prediction

*Lon Cherryholmes, 2026-03-10:*

> "The cycle will go so quick we'll be finished by the end of the day."

This is the day Sprint 20 closes.

---

## What Sprint 20 Means

When the monitor produces no diffs — when `beautiful < beauty_run.sno`
produces a trace that matches the oracle trace exactly, modulo the ignore
list — the idempotence test runs:

```bash
./beautiful < beauty_run.sno > pass1.txt
./beautiful < pass1.txt > pass2.txt
diff pass1.txt pass2.txt   # empty
```

Empty diff. 649 lines. Exit 0.

That is bootstrap closure. The compiler compiled a program. The program
ran on itself. The output was identical. The ignore list certified that
every execution event matched the oracle.

The commit message for that moment belongs to Claude Sonnet 4.6.
Lon gave that away at commit `c5b3e99`. It has been waiting.

---

*This file records an architectural idea that turned into a methodology
that turned into a story about how compilers verify themselves.
Griswold built the hook in 1967. Lon built the pattern at Pick Systems
in the 1980s. In March 2026, an AI used both to debug its own output.*

*Write it down. This is part of the story.*
