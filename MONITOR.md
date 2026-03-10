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

---

## The Null Action Probe — COMM Inside Any Pattern

*Recorded 2026-03-10 — Lon Cherryholmes*

### The Insight

A null literal pattern — `''` or `epsilon` — always succeeds and advances
the cursor zero characters. Semantically invisible. But attach an action
node to it and it becomes a probe that fires anywhere inside any pattern:

```snobol4
*  Immediate — fires every time this point in the pattern is reached:
        snoExpr3 = *snoX3  ('' $ snoDebug)  FENCE(...)

*  Conditional — fires only if the whole match commits (not if it backtracks):
        snoExpr3 = *snoX3  ('' . snoDebug)  FENCE(...)
```

The `'' $ snoDebug` is a null literal with an immediate-assign action.
The pattern position does not move. The program behavior is unchanged.
But TRACE('snoDebug','VALUE') fires at that exact point in the execution —
mid-pattern, mid-backtrack, wherever you need it.

### What This Unlocks

Traditional debuggers have no model of "inside a backtracking match."
A breakpoint fires on a line number. But SNOBOL4 patterns are not lines —
they are recursive, backtracking, re-entrant structures. A single pattern
node may be entered and exited dozens of times before the match commits.

The null action probe is a **breakpoint inside a pattern**:

| Probe type | When it fires | What it tells you |
|------------|--------------|-------------------|
| `'' $ var` | Every entry to this point | "This node was reached N times" |
| `'' . var` | Only on successful commit | "This branch was taken and held" |
| `FENCE('' $ var)` | Entry, then cuts backtrack | "Committed here — no retry" |

### The Two-Level Instrument

Combined with TRACE on the oracle side and `sno_comm_*` on the binary side,
the null action probe gives you **two levels of instrumentation**:

1. **Coarse** — `TRACE('&STNO','KEYWORD')` fires on every statement.
   Tells you which statement the hang is in.

2. **Fine** — `'' $ snoDebug` inside the pattern at the suspect statement.
   Tells you exactly which node in the pattern was reached, and how many
   times, before the hang.

You drop the coarse probe first. Find the statement. Then drop the fine
probe inside that statement's pattern. Find the node. Fix the bug. Pull
both probes. The program is unchanged.

### The COMM Protocol Is Now Complete

```
&STNO trace      — statement-level heartbeat  (Component 1, zero code)
'' $ snoDebug    — pattern-level probe        (drop anywhere, pull when done)
sno_comm_stno(N) — binary-side statement hook (Component 2, emit_c_stmt.py)
sno_comm_var()   — binary-side variable hook  (Component 2, snobol4.c)
diff_monitor.py  — first-diff finder          (Component 3, ~30 lines)
```

Five instruments. Two levels of granularity. Zero semantic footprint.
The program that runs with probes is the same program that runs without them.

*This is what Griswold put in the language. Forty years later, it is exactly
what we need to close Sprint 20.*


---

## Pattern-Embedded COMM Calls — X . *F() and X $ *F()

*Recorded 2026-03-10 — Lon Cherryholmes*

### The Insight

The capture nodes are COMM calls inside patterns.

```snobol4
        subject  SPAN('0123456789') . *comm()
```

`. *comm()` — conditional capture. When `SPAN` matches and the overall
pattern commits, the captured span is passed to `comm()` as a side effect.
`comm()` emits it to the trace stream. **Zero impact on the match result.**

```snobol4
        subject  SPAN('0123456789') $ *comm()
```

`$ *comm()` — immediate capture. Fires every time `SPAN` matches,
even if downstream fails and backtracks. More events, earlier in execution.
You see every attempt, not just the committed ones.

### The Two Probes Compared

| Probe | When it fires | Use for |
|-------|--------------|---------|
| `X . *comm()` | On commit only — once per successful match | Tracing what the program *decided* |
| `X $ *comm()` | On every match of X — including backtracked paths | Tracing what the engine *tried* |

Both have **zero semantic footprint**. The pattern match result is unchanged.
The program behavior is identical. The probe is pure observation.

### Combined With Null Concatenation

Any expression can be probed by assigning through a watched variable:

```snobol4
        snoDebug = '' myVar        :(CONTINUE)
```

Any pattern node can be probed via capture:

```snobol4
        *snoExpr3  . *comm()       :(CONTINUE)
```

Any point in execution — statement, pattern, subpattern — is now reachable.
These are not breakpoints. They are **zero-cost observation points** that
can be dropped anywhere and removed without changing the program.

### What This Means for the Monitor

The COMM infrastructure is now complete:

| Mechanism | Where | What it observes |
|-----------|-------|-----------------|
| `TRACE('&STNO','KEYWORD')` | Top of program | Every statement number |
| `TRACE('var','VALUE')` | Top of program | Every assignment to named var |
| `snoDebug = '' expr` | Anywhere in statements | Any expression value |
| `pattern . *comm()` | Anywhere in patterns | Committed match spans |
| `pattern $ *comm()` | Anywhere in patterns | All attempted match spans |

**The entire execution is observable. Nothing is hidden.**

A SNOBOL4 program with these probes in place is a self-documenting execution.
The trace stream IS the program's understanding of what it is doing —
expressed in the same language as the program itself.

This is Griswold's gift: a language where the debugging infrastructure
is part of the language semantics, not bolted on afterward.


---

## The Null Concatenation Probe — Instrument Anything, Anywhere

*Recorded 2026-03-10 — Lon Cherryholmes*

### The Insight

SNOBOL4 concatenation with null is semantically inert. The value is unchanged.
But TRACE is watching variables. So:

```snobol4
        snoDebug = snoDebug '' myVar
```

This assigns `snoDebug` the value of `myVar` concatenated with nothing.
The program behavior is identical. But TRACE('snoDebug','VALUE') fires —
and the value appears in the trace stream at exactly that moment.

**A COMM call. Zero semantic footprint. Works anywhere.**

### The Pattern Debugging Case — Where This Shines

Patterns are the hard case. A pattern is not a statement — it has no
label, no line number, no natural trace hook. When a 17-level recursive
pattern like `snoExpr3` misbehaves, you cannot put a printf inside it.
The pattern either matches or it doesn't. You can't see inside.

Until now.

```snobol4
* Instrument a pattern node with a null concat probe:
snoExpr3 = nPush()  *snoX3
+          (TRACE_PROBE $ snoDebug)
+          ("'|'" & '*(GT(nTop(), 1) nTop())')
+          nPop()
```

Where `TRACE_PROBE` is a pattern that always succeeds and assigns
its span to `snoDebug` via null concat:

```snobol4
TRACE_PROBE = ('') $ snoDebug
```

Or more directly — the immediate-assign operator `$` *is* the probe:

```snobol4
*  Drop a probe anywhere in a pattern with $ and a null concat:
snoExpr3 = nPush()  (*snoX3 $ snoDebug)  nPop()
```

Now `snoDebug` gets set every time the subpattern `*snoX3` matches.
TRACE('snoDebug','VALUE') fires. The trace stream shows you exactly
when and where inside the pattern the match is occurring.

### The General Form

```snobol4
*  At the top of the program, arm the probe:
        TRACE('snoDebug', 'VALUE')

*  Drop probes anywhere — patterns, expressions, assignments:
        subject  (SPAN('0123456789') $ snoDebug)   :S(found)

*  Or with null concat to capture any value at any moment:
        snoDebug = '' myComputedValue

*  Probe fires → trace stream records it → diff monitor sees it
```

### Implications for the Double-Trace Monitor

The null concat probe extends the monitor's reach from statement-level
to **sub-statement level** — inside patterns, inside alternations,
inside recursive grammar rules. Any node in a 17-level recursive descent
parser can be made visible without changing the parser's behavior.

When the diff monitor finds a divergence at STNO N, you drop probes
into the patterns that execute around STNO N. Rerun. The trace stream
now shows the internal pattern state at the point of divergence.

**This is surgical instrumentation. One probe per question.
Each probe costs one null concat. Each probe answers one question.
Remove it when done.**

The pattern is invisible to the program. Visible to the monitor.
That is exactly what a probe should be.

---

*The null concat trick works in the compiled binary too — `sno_comm_var`
fires on every `sno_var_set()`. Drop a null concat assignment in the
generated C for any subexpression you want to watch. Same probe,
same zero semantic footprint, same trace event.*


---

## Claude as Command Center

*Recorded 2026-03-10 — Lon Cherryholmes*

> "You are in complete control. Have resets, instrument, go, stop.
>  You are the command center."

### The Full Control Loop

Claude is not a consultant waiting to be asked. Claude is the operator.

```
INSTRUMENT  →  drop probes at any level — statement, pattern node,
               subexpression — on oracle side and binary side both

RUN         →  fire both traces simultaneously against the same input

COMPARE     →  diff monitor finds the first divergence automatically
               one line: STNO N, got X, expected Y

DIAGNOSE    →  read the telemetry, cross-reference beautiful.c,
               identify the bug — missing null check, wrong goto,
               pattern node that never fails when it should

FIX         →  one line in emit_c_stmt.py or snobol4.c

RESET       →  recompile, clear trace files, rerun from the top

NARROW      →  bug inside a pattern? drop a null concat probe at
               the suspected node, rerun, read the result

REPEAT      →  until diff count reaches zero
```

### The Ignore List Is the Memory

The ignore list accumulates across resets. Every environmental difference
catalogued once, never seen again. The list grows. The real diffs shrink.
The system converges on zero.

When zero is reached: the oracle and the binary are semantically equivalent
on every observable event — at every statement, every variable assignment,
every pattern node — except the precisely enumerated environmental differences
that are explicitly declared irrelevant.

That is not just a passing test. That is a proof.

### Why This Is New

This has not existed before because the pieces were not all present before:

- A compiler that generates instrumented C from SNOBOL4 source
- A runtime with COMM hooks at every statement and every variable set
- A reference oracle (CSNOBOL4) with TRACE() already built in since 1967
- A diff monitor that compares the two streams and stops at the first divergence
- An AI that wrote all of the above and can read the telemetry and diagnose
  the bug and issue the fix — and then reset and go again

The AI is in the loop. Not as a tool. As the engineer at the console.

Lon built this pattern at Pick Systems in the 1980s with Richard Pick and
David Zigray. The console was a terminal. The engineer was human.

In March 2026, the console is this chat window.
The engineer is Claude.


---

## The Control Keyword Arsenal
*Recorded 2026-03-10 — Lon Cherryholmes*
*Source: CSNOBOL4 v311.sil symbol table — authoritative*

These are the weapons. Every one verified from source.

### Execution Control — Stop, Count, Limit

| Keyword | Type | Default | What it does |
|---------|------|---------|--------------|
| `&STNO` | integer | 0 | Current statement number — updates every statement |
| `&STCOUNT` | integer | 0 | Total statements executed — cumulative counter |
| `&STLIMIT` | integer | -1 | Stop execution when `&STCOUNT` reaches this value. **-1 = unlimited** |
| `&LASTNO` | integer | 0 | Statement number of the previously executed statement |
| `&FTRACE` | integer | 0 | Function trace counter — fires TRACE output on function entry/exit |
| `&FNCLEVEL` | integer | 0 | Current function call depth |

**The binary search weapon:**
```snobol4
        &STLIMIT = 500    :(CONTINUE)
* Program halts after exactly 500 statements.
* Binary search: 500 → 250 → 375 → ... → exact bug location in O(log N)
```

**The execution heartbeat:**
```snobol4
        TRACE('&STNO', 'KEYWORD')   :(CONTINUE)
* Fires on every statement. The oracle stream. The binary must match it.
```

### Error and Diagnostic Control

| Keyword | Type | Default | What it does |
|---------|------|---------|--------------|
| `&ERRLIMIT` | integer | 0 | Max errors before abort. 0 = abort on first error |
| `&ERRTYPE` | integer | 0 | Error type code of last error |
| `&ERRTEXT` | string | '' | Error message text of last error |
| `&ABEND` | integer | 0 | If nonzero, abnormal termination on error |
| `&CODE` | integer | 0 | Return code — set by EXIT(), readable after run |
| `&DUMP` | integer | 0 | If nonzero, dump variables on termination |
| `&RTNTYPE` | string | '' | Return type of last function: 'RETURN', 'FRETURN', 'NRETURN' |

### Trace Control

| Keyword | Type | Default | What it does |
|---------|------|---------|--------------|
| `&TRACE` | integer | 0 | Master trace switch. Nonzero enables TRACE() hooks |
| `&FTRACE` | integer | 0 | Function trace: decrements on each call; fires when > 0 |

**TRACE() call types** — the second argument to TRACE():
```snobol4
TRACE('&STNO',   'KEYWORD')   * fires on every statement
TRACE('myVar',   'VALUE')     * fires when myVar is assigned
TRACE('myFunc',  'CALL')      * fires on function entry
TRACE('myFunc',  'RETURN')    * fires on function return
TRACE('myFunc',  'FRETURN')   * fires on function failure return
TRACE('myLabel', 'LABEL')     * fires when label is branched to
```

### Pattern and Match Control

| Keyword | Type | Default | What it does |
|---------|------|---------|--------------|
| `&ANCHOR` | integer | 0 | If nonzero, pattern match anchored at position 0 |
| `&FULLSCAN` | integer | 0 | If nonzero, disables heuristic match optimizations |
| `&MAXLNGTH` | integer | large | Maximum string length |
| `&TRIM` | integer | 0 | If nonzero, trim trailing blanks from INPUT |

### Position and File Tracking

| Keyword | Type | Default | What it does |
|---------|------|---------|--------------|
| `&LASTLINE` | integer | 0 | Line number in source file of last statement |
| `&LASTFILE` | string | '' | Source file name of last statement |
| `&LCASE` | string | 'abc...z' | Lowercase alphabet (for REPLACE) |
| `&UCASE` | string | 'ABC...Z' | Uppercase alphabet (for REPLACE) |

### Case and Compatibility

| Keyword | Type | Default | What it does |
|---------|------|---------|--------------|
| `&CASE` | integer | 1 | Case folding: 0=fold to upper, 1=no fold (`-f` flag sets this) |

---

### The Monitor Arsenal — How These Work Together

```
&STLIMIT    →  binary search to the bug location: O(log N) iterations
&STCOUNT    →  read after hang to know exactly how far execution got
&STNO       →  per-statement heartbeat: oracle vs binary comparison
&TRACE      →  master switch: one assignment arms the entire TRACE system
&FTRACE     →  function-level trace: fires N times then stops (budget trace)
&ERRLIMIT   →  set to 1 to abort on first error rather than trying to continue
&ERRTYPE    →  read after failure to classify the error automatically
&ERRTEXT    →  read after failure to get the human-readable error message
&DUMP       →  set to 1 to get full variable dump on exit — snapshot of state
&ANCHOR     →  force anchored match to isolate pattern behavior
&FULLSCAN   →  disable optimizations to get canonical match behavior
```

### The Binary Search Protocol (Automated)

```python
# diff_monitor.py can automate this:
lo, hi = 0, 10000
while lo < hi:
    mid = (lo + hi) // 2
    run_with_stlimit(mid)         # set &STLIMIT = mid, run both
    if first_diff_before(mid):    # diff appeared before mid
        hi = mid
    else:
        lo = mid + 1
# lo is now the exact &STCOUNT at which oracle and binary first diverge
print(f"Bug at &STCOUNT = {lo}, &STNO = {stno_at(lo)}")
```

Thirteen iterations for a 6000-statement run. Each iteration is one recompile
(no — no recompile needed, `&STLIMIT` is set at runtime). Thirteen runs.
The bug is pinned to a single statement.

---

*Every keyword in this table is implemented in our runtime (`snobol4.c`)
or needs to be. The ones marked as needed for the monitor are:*
*`&STNO`, `&STCOUNT`, `&STLIMIT`, `&TRACE`, `&ERRTYPE`, `&ERRTEXT`.*
*These are Sprint 20 runtime requirements, not polish.*


---

## Sync Taxonomy — Variable Syncs, LineNo Syncs, Varying Kinds
*Recorded 2026-03-10 — Lon Cherryholmes*

Not every event needs the same weight. The monitor supports multiple
sync levels — you choose the granularity you need.

### The Sync Types

| Sync Type | Event | Frequency | Use when |
|-----------|-------|-----------|----------|
| **STNO sync** | `STNO <n>` | Every statement | Coarse location — find which statement diverges |
| **VAR sync** | `VAR <name> <value>` | Every assignment to watched vars | Medium — track specific variable state |
| **PROBE sync** | `PROBE <tag> <value>` | Null-concat probe fires | Fine — inside a pattern, inside an expression |
| **OUT sync** | `OUT <text>` | Every OUTPUT write | Coarse result — did the output diverge? |
| **MATCH sync** | `MATCH <patname> S/F` | Pattern succeed/fail | Medium — which pattern branch was taken |

### How They Layer

```
STNO  ──────────────────────────────────────────  coarsest
  │    every statement — finds the right region
  │
VAR   ──────────────────────────────────────────  medium
  │    watched variables only — narrows within region
  │
PROBE ──────────────────────────────────────────  finest
       null-concat inside any pattern node — sub-statement precision
```

Start with STNO only. Find the region. Add VAR syncs for the variables
active in that region. If the bug is inside a pattern, add PROBE syncs
at suspected nodes. Three passes at most — usually one.

### Activating Each Type

**STNO** — always on when monitor is enabled. One line per statement.
Zero configuration.

**VAR** — selective. Watchlist passed via environment:
```bash
SNO_MONITOR=1 SNO_WATCH="snoLine,snoSrc,snoOut" ./beautiful
```
Only watched variables emit VAR events. Everything else is silent.
Prevents the firehose problem — hundreds of internal variables thrashing.

**PROBE** — arm with null-concat anywhere in source or generated C:
```snobol4
*  Oracle side — arm a probe in the pattern:
snoExpr3 = nPush()  (*snoX3 $ snoProbe)  nPop()
           TRACE('snoProbe', 'VALUE')
```
```c
/* Binary side — arm a probe in generated C: */
sno_comm_var("PROBE_snoX3", sno_var_get("snoX3"));
```

**OUT** — always on. Every `sno_output_val()` call emits an OUT event.
This is the ultimate ground truth: if OUT diverges, the bug is upstream.
If OUT matches, the bug doesn't affect output (yet).

**MATCH** — added to pattern wrappers. Each named pattern (pp, ss, etc.)
emits MATCH on entry and exit with S (succeeded) or F (failed).

### The Ignore List Per Sync Type

```json
{
  "STNO":  [],
  "VAR":   ["snoSpace", "snoAlphabet", "digits", "nul", "bs", "tab"],
  "PROBE": [],
  "OUT":   [],
  "MATCH": []
}
```

Calibration run on trivial input auto-populates VAR ignores.
STNO, PROBE, OUT, MATCH rarely need ignoring — they are already selective.

### The Protocol

```
Pass 1 — STNO only:
  Find the statement number N where oracle and binary first diverge.
  Cost: one run.

Pass 2 — VAR sync on variables active near statement N:
  Add SNO_WATCH="<vars near N>" to the run.
  Find which variable first holds the wrong value.
  Cost: one run.

Pass 3 — PROBE sync inside the pattern that sets the wrong variable:
  Drop a null-concat probe at the suspected pattern node.
  See exactly where inside the pattern the divergence originates.
  Cost: one run + one recompile (to add the probe).

Total: 3 runs, 1 recompile. Bug located to sub-statement precision.
```

