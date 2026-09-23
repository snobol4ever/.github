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

## ⭐⭐⭐ ONE SYNC-STEP DESIGN FOR SEVEN LANGUAGES (Lon 2026-09-23 02:22 CDT, in-chat to the ceo, verbatim: *"You might need to bring them all together on the sync-step IPC design to maximize code sharing and re-use."*; CEO-1176 — the convening rule; the cto convenes as the spine)

**The measured starting point (CEO-1175):** the sync-step monitor exists for SNOBOL4 alone. `--dump-ir` on one five-statement witness per language reads `STMT_MARK` snobol4 6 · icon 0 · prolog 0 · pascal 0 · raku 0. The wire in `src/runtime/core/core.c` (`mon_send_bin`, the `MWK_*` events, the go-pipe barrier) and the controller (`scripts/monitor/monitor_sync_bin.py`, `monitor_wire.h`) are language-blind already; the events reach them only through `bb_stmt_mark`, emitted only by `lower_snobol4.c`; `build_stno_map.py` maps SNOBOL4 statement numbers; the peers are SPITBOL and CSNOBOL4 through a bridge compiled into the oracle.

**THE RULE: ONE OF EACH, AND A PLUG PER LANGUAGE.** A language joins the monitor by adding a plug, never by copying a layer. The layers, each with exactly one implementation:
1. **The statement event** — `IR_STMT_MARK` carrying a statement number, emitted at every statement boundary by ONE mechanism for every frontend (lower_common or the driver, never seven lowerer copies); `bb_stmt_mark` stays the one emitter; the number is what the map keys on.
2. **The wire** — `monitor_wire.h` + `mon_send_bin` in `core.c`; language-blind today, stays so; a language never adds an event KIND — a value that needs a new rendering renders through the existing `MWK_VALUE` with its DESCR type as the tag.
3. **The controller** — `monitor_sync_bin.py`; one barrier, one byte-compare, one first-divergence report; parametrised by the participants it is handed, never by language.
4. **The statement map** — ONE builder (`build_stno_map.py`) with a per-language plug selected by extension: the plug answers *which source spans are statements and what number each carries*; nothing else is per language.
5. **The harness** — ONE runner parametrised by language and participant set (`PARTICIPANTS="scr3 scr4"` for the mode-3-against-mode-4 self arm; `"spl scr"` for SNOBOL4 against SPITBOL); `test_monitor_2way_sync_step_all_langs.sh` is its first form and every per-language arm is an invocation of it, never a sibling script.
6. **The peer** — the only genuinely per-language layer: the mode-3-against-mode-4 self-comparison first (no oracle bridge, catches MODES-MAY-DIVERGE semantics drift); an oracle-side bridge (iconx, swipl) only where it earns its cost, in the shape `monitor_ipc_spitbol.so` already has, and behind the same wire.

**THE ORDER OF WORK:** the cto lands layers 1, 4 (the builder interface + the SNOBOL4 plug moved into it) and 5 under row `monitor-the-sync-step-statement-event-is-emitted-by-every-frontend-so-the-ipc-monitor-can-drive-icon-prolog-pascal-and-raku`, and writes the plug interface in this section before any HQ mints; each HQ then lands its plug (layer 4) and its peer (layer 6) as one row in its lane, referencing this section; a per-language copy of any of layers 1–5 is reverted on sight. The standing law binds every arm: a MONITOR verdict is a verdict on a different program (`MONITOR_BIN` forces GVA off), so the monitor brackets only a witness proven monitor-safe (default-arm md5 unchanged under `MONITOR_BIN`) and REFUSES rc=2 when a participant never starts.

### ⭐⭐⭐ THE THREE HOOKS, SPECIFIED BY LON (2026-09-23 02:23 CDT, in-chat to the ceo, verbatim: *"We'll need line numbers coming from the source code and reported at runtime. We'll need a hook for every value assignment. A hook for function enter and exit. That easy. It is a common SCRIP runtime."*; CEO-1177 — refines layer 1 above)

Layer 1 is not one statement event but THREE runtime hooks, each with ONE implementation in the common runtime, every frontend lowering to them:
1. **The line hook** — the source line number carried into the emitted code and reported at runtime. The carrier exists: `IR_LINE_MARK` → `bb_line_mark` → `g_line`, which `core_error_voice` prints; today ONLY `lower_icon.c` emits it (CEO-746/747), so every other language's error voice prints line 0 and the monitor has no line either. Every frontend emits the line mark at every statement; the wire's `MWK_LABEL` event carries it; the statement number of the old SNOBOL4-only `STMT_MARK` becomes a derived key of the line, not a second mechanism.
2. **The assignment hook** — fired on every value assignment with the variable's name and its DESCR. The carrier exists for SNOBOL4 only: the `comm_var` tap in `bb_assign_global` (the `&TRACE` machinery), which today parks raw registers around the call and builds the name as an unrooted heap string (CEO-1172's split-out site). The one hook is a runtime entry taking `(name, DESCR, line)` behind the same wire (`MWK_VALUE` + `MWK_NAME_DEF` intern), reached by every frontend's assignment boxes through one emitter helper, and it roots what it holds — the tap is rewritten onto it, not copied.
3. **The enter/exit hook** — function enter and exit with the name (and the return DESCR on exit). The carrier exists for Icon procedures (`rt_trace_call_hook_f`, the activation record writer, CEO-536) and reaches the wire as `MWK_CALL`/`MWK_RETURN`; every frontend's call and return boxes fire it; generators and suspend ports fire it at γ the same way (CEO-550: γ is the shared yield port).

**Cost discipline, unchanged:** the hooks are guarded by one runtime flag (`g_trace`-shaped, the existing guard the trace taps use, CEO-1140: the poll is not inside the guard), so a program run without a monitor pays one compare per hook site; the emitted asm is byte-identical between a monitored and an unmonitored build (`MONITOR_BIN` remains a runtime knob, never a compile-time arm — ZETA HAS NO MODES). A frontend that cannot fire a hook at a construct names the construct in its plug row; it does not skip the hook silently.

**Position key (Lon 2026-09-23 02:25 CDT, verbatim: *"or some form of statement numbers versus line numbers."*; CEO-1178):** the line hook carries the language's OWN position unit — a source line where the language is line-shaped, a statement number where it is statement-shaped (SNOBOL4's statement numbers, Prolog's clause and goal positions) — as ONE integer on the wire; which unit, and how it renders, is the plug's answer (layer 4), never a second event kind and never a second carrier. `core_error_voice` prints the same unit, so the monitor and the error voice never disagree about where.

## ⭐⭐⭐ THE PLUG INTERFACE, AS THE CODE ON ORIGIN DEFINES IT (ceo, 2026-09-23 02:51 CDT, CEO-1184 — convened on Lon's word; written from hq_raku's landing at SCRIP `7504fe722`, not from prose)

**What exists today (measured):** four runtime entries in `src/runtime/core/core.c` — `rt_rk_trace_stmt(long line)`, `rt_rk_trace_value(const char *name, DESCR_t val)`, `rt_rk_trace_call(const char *name, DESCR_t *args, int nargs)`, `rt_rk_trace_return(const char *name, DESCR_t retval)` — gated by one global `g_rk_trace` (a countdown: `--trace` sets it to 2e9, `--trace=N` to N, `SCRIP_RK_TRACE=N` at run time for a mode-4 binary), each writing a `****<count>  …` line to stdout through `trace_spell_value` and, when `monitor_fd >= 0`, a TEXT wire event through `mon_send("STMT"|"CALL"|"RETURN"|"VALUE", name, text)`; four `__rk_trace_*` names in `by_name_dispatch.c`; the driver flag in `scrip.c`; 67 lines of emission in `lower_raku.c`. The SNOBOL4 path is older and separate: `SNO$STMT` hooks → `IR_STMT_MARK` → `bb_stmt_mark`, the `&TRACE` `comm_var` tap for assignments, and the BINARY wire (`mon_send_bin`, `monitor_wire.h`).

**THE SHARED LAYER — one of each, named now so every plug codes against the same thing:**

| Layer | The one implementation | Owner of the generalisation |
|---|---|---|
| hooks | `rt_trace_stmt(long pos)` · `rt_trace_value(const char *name, DESCR_t v)` · `rt_trace_call(const char *name, DESCR_t *args, int n)` · `rt_trace_return(const char *name, DESCR_t v)` — hq_raku's four with the `rk` dropped; `pos` is the language's own unit (line or statement number, CEO-1178); `value` roots what it holds for the call (CEO-1172's comm_var lesson) | hq_raku (row `monitor-hq-rakus-four-runtime-trace-entries-…`) |
| flag | ONE `g_trace_budget` (the countdown hq_raku built), set by `--trace[=N]` and `SCRIP_TRACE=N`; the language-prefixed names (`g_rk_trace`, `SCRIP_RK_TRACE`, `SCRIP_PAS_TRACE`) go | hq_raku |
| gate | COMPILE-TIME as landed (the calls are emitted only under `--trace`), OPEN FOR LON against the page's earlier runtime-flag wording; whichever he picks, the monitor-safe rule stands: a witness is monitor-safe when its untraced stdout equals its traced stdout with the `****` lines removed | Lon's ruling, ceo routes |
| wire | the hooks write BOTH the stdout trace and the binary wire (`mon_send_bin`: `MWK_LABEL` ← stmt, `MWK_VALUE` ← value, `MWK_CALL`/`MWK_RETURN` ← call/return, names through the `MWK_NAME_DEF` intern); the text `mon_send` path is retired once the binary path carries all four | hq_raku |
| emitter helpers | four helpers in `src/templates/x86/` (one per hook) that any lowerer/box calls: they marshal the name pointer, the DESCR pair and the position and emit the `call`; a lowerer never spells the hook call itself | hq_raku (with the hooks) |
| map builder | `scripts/monitor/build_stno_map.py` becomes `build_pos_map.py <source>` selecting a plug by extension; a plug is one Python function `positions(source_text) -> [(pos, line, text)]` answering which spans are statements and the number each carries; SNOBOL4's current logic is the first plug | hq_icon (with the Icon plug) |
| harness | `scripts/test_monitor_2way_sync_step_all_langs.sh --lang <l> --participants "scr3 scr4"` (SCRIP mode 3 against SCRIP mode 4 on one witness) or `"spl scr"` for SNOBOL4 against SPITBOL; one script, never a sibling per language | hq_icon |
| controller | `monitor_sync_bin.py` unchanged; parametrised by participants | nobody (stays) |

**THE PER-LANGUAGE PLUG — what each HQ lands as ONE row in its lane, referencing this section:**
1. Its lowerer calls the four emitter helpers at every statement (with the language's position unit), every value assignment, every call and every return (γ for generators, CEO-550); a construct it cannot hook is NAMED in the row, never skipped.
2. Its `positions()` plug in `build_pos_map.py`.
3. One monitor-safe witness from its master run through the harness `scr3 scr4` arm, event-for-event equal; the first divergence it finds is a row on the language's rung.

**THE ORDER AND THE OWNERS (Lon 2026-09-23: Prolog, Pascal, Raku use the technique; Icon is instrumented like them; one design, maximum reuse):**
- hq_raku — the shared layer first (the row above), then Raku's plug is what `lower_raku.c` already emits, re-pointed at the helpers.
- hq_icon — the map builder and the harness (their assigned row), then Icon's plug; Icon already carries `IR_LINE_MARK`, so its position unit is the line.
- hq_pascal — Pascal's plug; `SCRIP_PAS_TRACE` (AST-injected, interim, CEO-1179) is deleted in that landing.
- hq_prolog — Prolog's plug; the position unit is the clause/goal number the plug decides.
- hq_snobol4 — last: the `SNO$STMT` / `comm_var` path migrates onto the shared hooks so SNOBOL4 is a plug like the others and the SPITBOL bridge keeps working through the same wire.
Nobody starts a plug before hq_raku's renamed hooks and helpers are on origin; the ceo reviews each landing after the fact (the officers are down).

