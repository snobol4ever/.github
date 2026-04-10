# MILESTONE-SN4X86-SCRIP-TRACE — TRACE/STOPTR/DUMP/SETEXIT + Monitor in scrip --ir-run

**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6
**Date:** 2026-04-10
**Goal:** Wire TRACE/STOPTR/DUMP/SETEXIT and the sync-step two-way monitor into
`scrip --ir-run` so the beauty suite can be driven by `monitor_sync.py` with
SPITBOL x64 as oracle. Gates MILESTONE-SN4X86-BEAUTY-PREREQS (19/19) and B-3.

---

## What already exists (do NOT rewrite)

### In `src/runtime/x86/snobol4.c` — complete, battle-tested

| Symbol | What it does |
|--------|-------------|
| `_TRACE_(args, n)` | Registers `name` into `trace_set[]`; `TRACE(v,'VALUE')` / `TRACE(f,'FUNCTION')` |
| `_STOPTR_(args, n)` | Removes `name` from `trace_set[]` |
| `_DUMP_(args, n)` | Prints all live variables to OUTPUT |
| `_SETEXIT_(args, n)` | Registers error-exit label |
| `trace_set[256]` | Hash table: names currently under VALUE trace |
| `trace_is_active(name)` | Returns 1 if name is in trace_set |
| `comm_var(name, val)` | Emits `VALUE RS name US val RS` to `monitor_fd`; then blocks on `monitor_ack_fd` for 'G'/'S' |
| `comm_stno(n)` | Increments `kw_stcount`; fires `sno_runtime_error(22)` when `kw_stlimit` exceeded |
| `monitor_fd` | Ready-pipe fd; opened from `MONITOR_READY_PIPE` env var in `SNO_INIT_fn()` |
| `monitor_ack_fd` | Go-pipe fd; opened from `MONITOR_GO_PIPE` env var in `SNO_INIT_fn()` |
| `kw_stcount`, `kw_stlimit`, `kw_ftrace` | Globals; wired in `NV_GET_fn`/`NV_SET_fn` |

All four builtins are already `register_fn()`'d in `SNO_INIT_fn()`.

### In `x64/monitor_ipc_spitbol.so` — SPITBOL participant IPC
SPITBOL uses `LOAD('MON_OPEN(STRING,STRING)STRING', ...)` → dlsym → `MON_OPEN()`.
This is the **SPITBOL side only**. `scrip` does not use LOAD — it uses the C-native path.

### In `test/monitor/monitor_ipc_sync.so` — scrip participant IPC (NOT USED)
The `.so` exists for CSNOBOL4. `scrip` again uses the C-native path in `snobol4.c`.

### In `test/monitor/monitor_sync.py` — sync-step barrier controller
Reads one `KIND RS name US value RS` record from each ready pipe, compares,
sends 'G'/'S' to each go pipe. Already handles 2-party case (pass `names=spl,scrip`).

### In `test/monitor/inject_traces.py` — trace preamble injector
Injects `TRACE(var,'VALUE')` + `TRACE(fn,'FUNCTION')` calls into any `.sno` file.
Reads `tracepoints.conf`. Output is a valid `.sno` with trace registrations prepended.

---

## The Gap — entirely in `scrip.c`

`scrip --ir-run` calls `SNO_INIT_fn()` ✅ (builtins registered, FIFOs opened).
But the assignment hook and function call/return hook are **never consulted**:

### Gap 1 — VALUE trace hook missing from `assign_to()`

In `scrip.c`, all assignments go through `assign_to()` (~line 220) or inline
`NV_SET_fn()` calls. Neither calls `comm_var()` after the write.

**Fix:** After every `NV_SET_fn(name, val)` in the `--ir-run` path, add:

```c
extern int    trace_is_active(const char *name);
extern void   comm_var(const char *name, DESCR_t val);

/* After NV_SET_fn(name, val): */
if (trace_is_active(name)) comm_var(name, val);
```

The cleanest insertion point is `assign_to()` for the NAMEVAL path, and the
inline `NV_SET_fn` calls at the pattern-match replacement sites (~lines 435, 446,
519, 798, 847, 1606, 1639, 1657).

Wrap in a helper to avoid repetition:

```c
static inline void set_and_trace(const char *name, DESCR_t val) {
    NV_SET_fn(name, val);
    if (trace_is_active(name)) comm_var(name, val);
}
```

Replace `NV_SET_fn(name, val)` → `set_and_trace(name, val)` at all assignment
sites where `name` is a plain variable string (not a keyword — keywords are
excluded from VALUE trace per SIL).

### Gap 2 — CALL/RETURN trace hooks missing from `call_user_function()`

In `scrip.c`, `call_user_function()` (~line 310) manages user-defined function
calls. TRACE('fn','FUNCTION') registers both CALL and RETURN hooks (stored in
`trace_set` with a FUNCTION tag, distinct from VALUE).

**Fix:** Add at entry and exit of `call_user_function()`:

```c
extern int  trace_fn_active(const char *fname);   /* new helper in snobol4.c */
extern void comm_call(const char *fname);          /* new helper: emits CALL event */
extern void comm_return(const char *fname, DESCR_t retval); /* emits RETURN event */
```

Or use the existing `kw_ftrace` path: when `kw_ftrace > 0`, fire call/return
trace regardless of `trace_set` (per SIL &FTRACE semantics).

Implementation order: VALUE trace (Gap 1) first — it unblocks beauty_trace_driver.

### Gap 3 — `comm_stno()` not called from the --ir-run statement loop

`comm_stno(n)` is already called from the `trampoline.h` x86 emitter path.
In `scrip.c` the top-level statement loop already increments `kw_stcount` and
checks `kw_stlimit` (BP-0, committed in `bea4045f`). But it does NOT call
`comm_stno()` — meaning the monitor never sees STNO events.

**Fix:** Replace the manual `kw_stcount++` / stlimit check in the ir-run loop
with a single `comm_stno(stno)` call (which does both internally).

---

## Two-way monitor wiring — SPITBOL vs scrip

The monitor infra already supports 2-party runs. The `run_monitor_3way.sh`
launches 3 participants; a 2-way variant just skips the ASM compile+launch steps.

### New script: `test/monitor/run_monitor_2way.sh`

```bash
#!/bin/bash
# run_monitor_2way.sh <sno_file> [tracepoints_conf]
# Two-way sync-step monitor: SPITBOL x64 (oracle) vs scrip --ir-run.
# No compilation step. No JVM/NET/ASM participants.
# Exit 0 = agree. Exit 1 = diverge. Exit 2 = timeout.

set -uo pipefail
SNO=${1:?}
CONF=${2:-$(dirname "$0")/tracepoints.conf}
MDIR=$(cd "$(dirname "$0")" && pwd)
DIR=$(cd "$MDIR/../.." && pwd)
X64="$DIR/../../x64"          # /home/claude/x64
INC="${INC:-/home/claude/corpus/programs/snobol4/demo/inc}"
TIMEOUT="${MONITOR_TIMEOUT:-10}"
TMP=$(mktemp -d /tmp/monitor_2way_XXXXXX)
trap 'rm -rf "$TMP"' EXIT

base="$(basename "$SNO" .sno)"
echo "[2way] $base"

# Step 1: inject traces
python3 "$MDIR/inject_traces.py" "$SNO" "$CONF" > "$TMP/instr.sno"
python3 - "$TMP/instr.sno" << 'PYEOF'
import sys; path = sys.argv[1]
src = open(path).read()
src = src.replace(
    "        MON_READY_PIPE_       =  HOST(4,'MONITOR_READY_PIPE')\n",
    "        MON_READY_PIPE_       =  HOST(4,'MONITOR_READY_PIPE')\n"
    "        MON_GO_PIPE_   =  HOST(4,'MONITOR_GO_PIPE')\n")
src = src.replace("        MON_OPEN(MON_READY_PIPE_)",
                  "        MON_OPEN(MON_READY_PIPE_, MON_GO_PIPE_)")
open(path, 'w').write(src)
PYEOF

# Step 2: FIFOs — two per participant
for p in spl scrip; do mkfifo "$TMP/$p.ready"; mkfifo "$TMP/$p.go"; done

READY="$TMP/spl.ready,$TMP/scrip.ready"
GO="$TMP/spl.go,$TMP/scrip.go"

# Step 3: launch SPITBOL (uses LOAD → monitor_ipc_spitbol.so)
STDIN="${SNO%.sno}.input"; [ -f "$STDIN" ] || STDIN=/dev/null
(cd "$INC" && SNOLIB="$X64:$INC" \
    MONITOR_READY_PIPE="$TMP/spl.ready" MONITOR_GO_PIPE="$TMP/spl.go" \
    MONITOR_SO="$X64/monitor_ipc_spitbol.so" \
    "$X64/bin/sbl" "$TMP/instr.sno" < "$STDIN" \
    > "$TMP/spl.out" 2>"$TMP/spl.err") &
SPL_PID=$!

# Step 4: launch scrip --ir-run (uses C-native monitor in snobol4.c)
SNO_LIB="$INC" \
    MONITOR_READY_PIPE="$TMP/scrip.ready" MONITOR_GO_PIPE="$TMP/scrip.go" \
    "$DIR/scrip" --ir-run "$TMP/instr.sno" < "$STDIN" \
    > "$TMP/scrip.out" 2>"$TMP/scrip.err" &
SCRIP_PID=$!

# Step 5: controller
python3 "$MDIR/monitor_sync.py" \
    "$TIMEOUT" "spl,scrip" "$READY" "$GO" > "$TMP/ctrl.out" 2>&1 &
CTRL_PID=$!

wait $CTRL_PID; RC=$?
kill $SPL_PID $SCRIP_PID 2>/dev/null || true
wait 2>/dev/null || true
cat "$TMP/ctrl.out"
exit $RC
```

**Usage:**
```bash
cd /home/claude/one4all
INC=/home/claude/corpus/programs/snobol4/demo/inc
BEAUTY=/home/claude/corpus/programs/snobol4/beauty

# Single driver:
bash test/monitor/run_monitor_2way.sh $BEAUTY/beauty_trace_driver.sno

# All 5 failing drivers:
for name in Gen Qize TDump XDump omega; do
    bash test/monitor/run_monitor_2way.sh $BEAUTY/beauty_${name}_driver.sno
done
```

---

## Implementation order

| Step | Task | File | Gate |
|------|------|------|------|
| T-0 | Add `set_and_trace()` helper; replace `NV_SET_fn` at all assignment sites | `scrip.c` | `beauty_trace_driver` passes via stdout diff |
| T-1 | Replace manual stcount/stlimit with `comm_stno(stno)` in ir-run loop | `scrip.c` | STNO events appear in ready pipe |
| T-2 | Add CALL/RETURN hooks in `call_user_function()` | `scrip.c` | CALL/RETURN events in pipe |
| T-3 | Write `run_monitor_2way.sh` | `test/monitor/` | `[2way] beauty_trace_driver → EXIT 0` |
| T-4 | Run 2-way monitor on all 5 failing drivers; read first diverging event | — | First divergence line names each bug |

**T-0 is the key unlock.** Once VALUE trace fires through `comm_var()`, the
sync-step barrier works and the monitor pinpoints every subsequent divergence
without manual printf debugging.

---

## SPITBOL invocation note

SPITBOL `bin/sbl` requires `cd $INC` before running (or `SNOLIB=$X64:$INC`) so
`-INCLUDE` files resolve. The `bootsbl` binary in `x64/` is the bootstrap loader;
for monitor runs use `bin/sbl` directly (it handles LOAD() for the `.so`).

SPITBOL emits its listing header to stdout — the monitor controller ignores
non-trace lines (they don't match the `KIND RS ...` wire format).

---

## Baseline

- one4all HEAD: `f23ef24c`
- `--ir-run` PASS=193/203 · beauty suite 14/19
- Monitor: 0/5 failing drivers wired (this milestone wires all 5)

## Gate

```bash
cd /home/claude/one4all
INC=/home/claude/corpus/programs/snobol4/demo/inc
BEAUTY=/home/claude/corpus/programs/snobol4/beauty
for name in Gen Qize TDump XDump omega; do
    bash test/monitor/run_monitor_2way.sh $BEAUTY/beauty_${name}_driver.sno
done
# → all EXIT 0 (SPITBOL agrees with scrip at every trace step)
# → beauty suite 19/19
```

**Fires:** MILESTONE-SN4X86-BEAUTY-PREREQS complete → B-3 self-hosting.
