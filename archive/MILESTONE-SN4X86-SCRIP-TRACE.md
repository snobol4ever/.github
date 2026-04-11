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
