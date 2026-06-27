# Sync-step monitor — binary protocol redesign

## Why

The current restored harness (`scripts/test_monitor_2way_sync_step.sh`,
`scripts/monitor/{inject_traces.py, monitor_sync.py, monitor_ipc_sync.c,
tracepoints.conf}`) speaks a TEXT wire protocol:

    KIND \x1E name \x1F value \x1E

The `value` field is produced by SNOBOL4-side `CONVERT($MONN, 'STRING')`,
which means every trace event runs through the runtime's stringification
code path:

  - CSNOBOL4 stringifies a user-DATA value as the prototype name (`'tree'`)
  - SPITBOL fails CONVERT on the same value → `'(undef)'`
  - Pattern values: CSNOBOL4 → `'PATTERN'`, SPITBOL → `'(undef)'`
  - ARRAY values: CSNOBOL4 → `"ARRAY('1:4')"`, SPITBOL → `'(undef)'`

We've been masking these with `IGNORE` regex rules in tracepoints.conf —
each rule is a string-processing operation in the controller AND a
lexical decision about what counts as "noise."  This is the lex/parse
contamination Lon flagged.

## What changes

Replace the text wire with a **binary, length-prefixed, type-tagged**
record format:

    record = u32 kind  |  u32 name_id  |  u8 type  |  u32 value_len  |  value_bytes

  - `kind`     : 1=VALUE, 2=CALL, 3=RETURN, 4=END
  - `name_id`  : index into a per-run name table (built at instrumentation
                 time by inject_traces.py from the matched INCLUDE/EXCLUDE
                 names; emitted as a sidecar `<run>.names` file the
                 controller reads at startup)
  - `type`     : SNOBOL4 datatype code:
                 0=NULL, 1=STRING, 2=INTEGER, 3=REAL, 4=NAME, 5=PATTERN,
                 6=EXPRESSION, 7=ARRAY, 8=TABLE, 9=CODE, 10=DATA, 11=FILE
  - `value_len`: number of bytes of `value_bytes` to follow
  - `value_bytes`:
                 STRING/NAME : raw SCBLK bytes (length=`value_len`)
                 INTEGER     : 8 bytes little-endian (length=8)
                 REAL        : 8 bytes IEEE754 little-endian (length=8)
                 PATTERN/ARRAY/TABLE/CODE/DATA/EXPRESSION/FILE/NULL
                             : empty (length=0)

Cross-dialect comparison is then byte-for-byte equality on the record.
No regex, no IGNORE rules, no lowercasing, no stringification.  Pattern
values from both oracles come out as `(type=5, len=0)` — they
automatically agree without any rule machinery.  STRING values agree
only when their bytes match exactly, which is the truthful comparison.

## What survives

- The FIFO pair-per-participant architecture (one .ready, one .go)
- The barrier-step semantics (write event, block on go-ack, repeat)
- The RS/US delimiter idea — but RS becomes a record-end *pad* byte
  for resync after a controller `'S'` ack only.  Records themselves
  are length-prefixed, so RS isn't needed to find boundaries.
- inject_traces.py's INCLUDE/EXCLUDE name-set computation — but it
  emits a names table sidecar instead of TRACE() registrations.
- monitor_sync.py's barrier loop.

## What goes away

- The MONVAL/MONCALL/MONRET SNOBOL4 callback functions in the
  inject_traces.py preamble.  They CONVERT to STRING; that's the
  whole point we're removing.
- The 4-arg `TRACE(var,VALUE,'',MONVAL)` SNOBOL4 wiring.
- The IGNORE rules in tracepoints.conf.
- The `value_after_ignore` function in monitor_sync.py.
- The `.upper()` name normalization in monitor_sync.py.

## What's needed

### 1. New SNOBOL4-callable C library  (`monitor_ipc_bin.c`)

Three functions, all LOAD()able with SNOBOL4 ABI:

```c
/* MON_OPEN(ready_path, go_path, names_path) → 0 or FAIL
 *   names_path is the per-run name table file (just a plain list of
 *   names, one per line; the index in the file is the name_id).
 *   Library mmap()s it once, builds a name→id hash table.
 */
lret_t MON_OPEN(LA_ALIST);

/* MON_PUT_VALUE(name, varcell) → 0 or FAIL
 *   name is the variable name string (SCBLK).  varcell is the descriptor
 *   of the variable's current value.  Library:
 *     - resolves name → id via hash table
 *     - inspects varcell.v (datatype tag) to decide type field
 *     - extracts raw bytes (length, ptr) for STRING/INTEGER/REAL only
 *     - assembles record into stack buffer, writev() to ready_fd
 *     - read(go_fd, 1) to block for ack
 */
lret_t MON_PUT_VALUE(LA_ALIST);

/* MON_PUT_CALL(fname) and MON_PUT_RETURN(fname, retval) — analogous. */
lret_t MON_PUT_CALL(LA_ALIST);
lret_t MON_PUT_RETURN(LA_ALIST);
```

Build as **three** .so files (one per ABI):

  - `monitor_ipc_bin_csn.so`  — uses CSNOBOL4 LDESCR layout
  - `monitor_ipc_bin_spl.so`  — uses SPITBOL LDESCR layout  (resides in x64/)
  - linked-in for scrip's snobol4.c — replaces existing `mon_send`

The CSNOBOL4 and SPITBOL ABIs differ slightly (sizes, field offsets) —
this is already handled in the existing pair of .c files in the recovered
infrastructure; just port the changes per-ABI.

### 2. Rewrite inject_traces.py preamble

Drop MONVAL/MONCALL/MONRET DEFINE blocks entirely.

Emit:

```snobol4
        MON_NAMES_PATH = HOST(4,'MONITOR_NAMES_FILE')
        MON_READY      = HOST(4,'MONITOR_READY_PIPE')
        MON_GO         = HOST(4,'MONITOR_GO_PIPE')
        MON_SO         = HOST(4,'MONITOR_SO')
        LOAD('MON_OPEN(STRING,STRING,STRING)INTEGER',     MON_SO)
        LOAD('MON_PUT_VALUE(STRING,STRING)INTEGER',       MON_SO)
        LOAD('MON_PUT_CALL(STRING)INTEGER',               MON_SO)
        LOAD('MON_PUT_RETURN(STRING,STRING)INTEGER',      MON_SO)
        MON_OPEN(MON_READY, MON_GO, MON_NAMES_PATH)
*
        DEFINE('MV(N,T)V')                            :(MV_END)
MV      MV = MON_PUT_VALUE(N, $N)                     :(RETURN)
MV_END
        DEFINE('MC(N,T)')                             :(MC_END)
MC      MON_PUT_CALL(N)                               :(RETURN)
MC_END
        DEFINE('MR(N,T)V')                            :(MR_END)
MR      MR = MON_PUT_RETURN(N, $N)                    :(RETURN)
MR_END
*
        TRACE(name, VALUE, '', 'MV')   ; ... per included name
        TRACE(name, CALL,  '', 'MC')   ; ... per included function
        TRACE(name, RETURN, '', 'MR')  ; ... per included function
```

The trick: the TRACE callbacks `MV`/`MC`/`MR` do NO string work.  They
call straight into the LOAD()ed C function with the variable name and
the variable's value descriptor.  C reads the descriptor's raw bytes and
emits the binary record.

### 3. Names-file emission

inject_traces.py also writes `MONITOR_NAMES_FILE` (a temp file) with
one name per line.  Order = order TRACE() registers them.  The .so's
`MON_OPEN` reads it once and builds an in-memory hash for O(1) lookup.

### 4. Rewrite monitor_sync.py read loop

```python
def read_record(fd):
    hdr = os.read(fd, 13)  # 4+4+1+4
    if not hdr: return None
    kind, name_id, type_tag = struct.unpack('<II B', hdr[:9])
    value_len = struct.unpack('<I', hdr[9:13])[0]
    val = os.read(fd, value_len) if value_len else b''
    return (kind, name_id, type_tag, val)
```

Compare records as **tuples** for equality.  No string conversions.
Print events using the names-file (controller also reads it) for human
output only — never used in the comparison path.

### 5. Scrip-side: replace mon_send

Already in `src/runtime/x86/snobol4.c`.  Currently calls
`VARVAL_fn(val)` which CONVERTs to STRING.  Replace with direct
inspection of `val.v` (type tag) and raw bytes from `val.s`/`val.i`/
`val.r`/`val.ptr` per type.  This is the simplest of the three rewrites
because scrip's runtime is C-internal — no LOAD ABI dance.

## Effort estimate

- Binary record format + struct layout doc:        0.5 h
- monitor_ipc_bin.c (CSNOBOL4 + SPITBOL versions): 2.0 h
- inject_traces.py rewrite + names-file emission:  1.5 h
- monitor_sync.py rewrite:                         1.0 h
- scrip mon_send rewrite:                          1.0 h
- 2-way validation on hello + multi probes:        0.5 h
- 2-way validation on full beauty self-host:       1.0 h
- Wire scrip --run as 3rd participant:          1.0 h
                                                   ----
                                                   8.5 h  (one full session)

## Gates

After the binary protocol lands:
  - Smoke=7, Broker=49 unchanged
  - 2-way (CSNOBOL4 + SPITBOL) on full beauty self-host: 0 divergences,
    all events to END
  - 3-way (... + scrip --run): first divergence is the actual beauty
    self-host bug (currently SN-26c-parseerr-h sub-h2)
  - Same with --run and --run as the third slot

## Dependencies on prior work

- The interp.c set_and_trace fix (this session, line 953) is required
  for scrip to fire VALUE traces on plain `var = expr`.
- The recovered scripts/monitor/* infrastructure stays as the text-protocol
  reference for spotting bugs in the binary version (run both, compare).

## Files this plan touches

- SCRIP/scripts/monitor/monitor_ipc_bin.c                  (NEW)
- SCRIP/scripts/monitor/inject_traces.py                   (rewrite)
- SCRIP/scripts/monitor/monitor_sync.py                    (rewrite)
- SCRIP/scripts/monitor/tracepoints.conf                   (drop IGNOREs)
- SCRIP/scripts/test_monitor_2way_sync_step.sh             (minor edits)
- SCRIP/scripts/test_monitor_3way_sync_step.sh             (NEW)
- SCRIP/src/runtime/x86/snobol4.c (mon_send + comm_var/call/return)
- x64/monitor_ipc_bin_spl.c                                  (NEW; build .so)
