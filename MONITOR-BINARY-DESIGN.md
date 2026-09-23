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

### ⭐⭐⭐ STATUS 2026-09-23 03:12 CDT — LANDED AT SCRIP `ab085a22f` (ceo, CEO-1185): THE MONITOR DRIVES ICON, PROLOG, PASCAL AND RAKU

- **Shared layer, landed:** `rt_trace_stmt/_value/_call/_return` (hq_raku's four, rk dropped), one countdown flag `g_trace_budget` (`--trace[=N]`, `SCRIP_TRACE=N` at run time), the binary wire through `mon_emit_trace_bin` (MWK_LABEL/VALUE/CALL/RETURN, no SNOBOL4 name-table filter), dispatch names `__trace_*`, a value-less `__trace_return`.
- **Plugs, landed:** Raku (re-pointed, byte-identical trace), Icon (statement, call, value, return), Pascal (hq_pascal's parser injection re-gated and re-targeted; the interim `SCRIP_PAS_TRACE` handlers deleted — CEO-1179 fulfilled), Prolog (call at the predicate entry, return before each clause succeed, statement before each goal — **owed:** goal trees carry line 0, so the statement event fires only once the Prolog plug row gives goals a position, the clause/goal number).
- **Harness and gate, landed:** participants `scr3`/`scr4` in the one auto harness; `test_monitor_2way_sync_step_all_langs.sh` reads 4 of 4 (icon 13 steps · prolog 3 · pascal 25 · raku 15), wired REPORTED in `make test`; one witness per language under `scripts/monitor/witnesses/`.
- **Owed, by owner:** hq_prolog — goal positions; hq_snobol4 — the `SNO$STMT`/`comm_var` path migrated onto the shared hooks (the last plug; the SPITBOL bridge keeps working through the same wire); hq_icon — the per-language `positions()` map plug (the m3-vs-m4 arm needs no map, an oracle peer will); each HQ — a monitor-safe witness from its own master and the first real bug the technique finds; Lon — the gate (compile-time as landed, or a runtime flag).

## ⭐⭐⭐ HOW AN HQ USES IT (ceo 2026-09-23 03:17 CDT, CEO-1186 — Lon: *"finish up IPC sync-step monitor and let me know when the HQ's can begin to use"*; *"you can manufacture statement numbers versus line numbers if that is easier."*)

One command, from `SCRIP/`, on any source of Icon, Prolog, Pascal, Raku, SNOBOL4, Snocone or Rebus:

```bash
bash scripts/monitor_run.sh prog.icn            # --modes: mode 3 against mode 4 in lock-step; AGREE, or the controller's grid at the first divergence
bash scripts/monitor_run.sh prog.pl --trace     # the trace: ****N  L<pos> / name = value / name(args) / RETURN name = value
bash scripts/monitor_run.sh prog.sno --oracle   # SCRIP against the oracle in lock-step (SPITBOL for .sno, the instrumented iconx for .icn)
```

- **Before any lock-step verdict the wrapper checks monitor-safety itself:** the untraced stdout must equal the traced stdout with the `****` lines removed; if not, it REFUSES rc=2 — the trace changed the program and the verdict would be about a different one. Exit 0 no graded event diverged -- the verdict word is AGREE only when the controller's VERDICT line reads UNGRADED=0, otherwise UNGRADED=n naming every step a participant sent untyped (never compared, never a match; the coo, SCRIP `1fa63bb9f`, row monitor-the-controller-reads-an-untyped-value-as-agree-…); 1 diverge (a row on the language's rung), 2 could not measure.
- **The position unit is the language's own:** a source line where the frontend has one (Icon, Raku, Pascal, SNOBOL4's statement numbers), a MANUFACTURED statement number in lowering order where it has none (Prolog goals: `L1, L2, …` in the order the goals are lowered — both modes lower identically, so lock-step compares on it). Lon's word: manufacture when easier.
- **What `--trace` is:** the compile-time gate of the shared hooks (`rt_trace_stmt/_value/_call/_return`); `--trace=N` budgets N events; a mode-4 binary reads `SCRIP_TRACE=N` at run time. `SCRIP_TRACE` is ONE variable: it also arms SNOBOL4's `&TRACE` budget, so `--trace` on a `.sno` traces as `&TRACE = N` would.
- **What a divergence means:** mode 3 and mode 4 disagree on an event — a MODES-MAY-DIVERGE drift, cured on the language's rung with the witness minted into the master; the trace alone (`--trace`) is the debugging tool that found hq_pascal's three bugs in one sitting (CEO-1179).
- **`--oracle` today:** `.sno` holds SCRIP and the instrumented SPITBOL fork in lock-step; `.icn` holds SCRIP and the instrumented Arizona iconx (`icx`, since SCRIP `d85e6186d`); `.pl` holds SCRIP and the instrumented GNU Prolog (`gpx`, since SCRIP `4a9d5a698`); `.raku` holds SCRIP and the instrumented Rakudo 2026.05 (`rkx`, the cfo, SCRIP `3fd46dd77` -- `RAKUDO_MON_ROOT` names the prefix until Lon installs `/home/resources/rakudo-mon`); `.pas` holds SCRIP and the instrumented Free Pascal fork (`fpx`, since SCRIP `220cd725a`, the coo on Lon's word); Raku follows as MoarVM is instrumented in its own source by the cfo (§ THE ORACLES ARE INSTRUMENTED IN THEIR OWN SOURCE). SNOBOL4 is on the shared hooks since CEO-1187.

## ⛔⭐⭐⭐⭐ THE ORACLES ARE INSTRUMENTED IN THEIR OWN SOURCE (Lon 2026-09-23 04:3x CDT, in-chat to the ceo, verbatim: *"You did not implement a proper IPC, a binary communication, sync-step, monitor using PIPES or whatever IPC is available under Unix. You did some crazy gdb and other tool hybrid. So you failed miserably. Now it is time to do it again. Each oracle must be INSTRUMENTED with IPC COMM calls."* then *"No, you will implement each yourself"* — CEO-1189; SUPERSEDES the section below this one)

**The standard is the SPITBOL x64 fork.** `/home/resources/spitbol-fork-rebuilt/osint/monitor_ipc_runtime.c` is statically linked into `sbl`; `sbl.min` calls its five fire-points (`zysml` statement, `zysmv` value, `zysmc` call, `zysmr` return, `zysmw`); the library opens the two named pipes `MONITOR_READY_PIPE` / `MONITOR_GO_PIPE` lazily, writes one 13-byte little-endian header (`u32 kind | u32 name_id | u8 type | u32 value_len`) plus the value bytes per event, BLOCKS on the controller's one-byte ack after every record (that is the sync-step), interns names on the wire (`MWK_NAME_DEF` before first use), emits `MWK_END` at exit, and is a silent no-op when the pipes are unset — so the instrumented binary's untraced behaviour is the pristine oracle's. Every other oracle gets the same treatment, in this order: **Icon (landed by the ceo, SCRIP `d85e6186d`) → Prolog (landed by the ceo as GNU PROLOG, not swipl — Lon 2026-09-23 05:2x: *"Build IPC sync-step monitor into GNU Prolog just like you did for Icon"*; SCRIP `4a9d5a698`) → Pascal (FPC) and Raku (MoarVM), which Lon gave to the cfo and the coo at 06:0x (in-chat to the ceo, verbatim: *"I am about to give IPC for Raku and Pascal to CFO and COO."*) — RECORDED 06:32: Lon, in-chat to the coo, *"Build the Free Pascal Compiler (FPC) IPC sync-step monitor inside FPC just like CEO did for Icon and Prolog and get a few hello world type programs working, then hand off to HQ-PASCAL to complete"*, so FPC is the coo's (landed, SCRIP `220cd725a`, CEO-1192) and MoarVM the cfo's**. No gdb bridge, no debugger-hook script, no stderr-replay twin: a participant is the oracle's own engine speaking the wire from inside its interpreter or its generated code.

**The shared library** `SCRIP/scripts/monitor/oracles/monitor_ipc_lib.{c,h}` is the fork's library with the SPITBOL block reader removed: `mon_ipc_stmt(line)`, `mon_ipc_call(name,len)`, `mon_ipc_return(name,len,type,val,vlen)`, `mon_ipc_value(name,len,type,val,vlen)`, `mon_ipc_live()`. An oracle fork copies it into its source, adds one engine-specific fire-point file, and is built by `scripts/monitor/oracles/build_<lang>_mon.sh <prefix>` from the pristine drop under `/home/resources/` plus a versioned patch, ending in the CONTROL ARM (pipes unset: fork stdout and rc equal the pristine oracle's on the language's witness). The fork is a PARTICIPANT binary beside the pristine oracle, never the grader (RULES.md § Oracles, the ORACLE-SWAP PROCEDURE, Lon's go). `<LANG>_MON_ROOT` names the prefix; the default is `/home/resources/<lang>-mon`, which the ceo's harness classifier refuses to write — Lon or a seat that may write there installs it with the build script, and any seat builds its own copy in its root in seconds.

**THE CONTRACT, per event kind (what SCRIP's plug and the instrumented oracle must both fire):**
- **STMT** — once at the start of every statement of every statement list, at any nesting, each time it executes, with the statement's own source line; a declaration, an `initial` clause header or a procedure header is not a statement. (Icon: `icont` emits a new icode opcode `Op_Stmt` at every element of every `N_Slist` and at a lone body statement; SCRIP's plug skips `TT_LOCAL`/`TT_STATIC_DECL`/`TT_INITIAL`.)
- **VALUE** — every store to a named variable, with the stored value; a store into a structure element or a trapped/substring variable is `<lval>` (the controller's name wildcard); keyword stores are no event. Types: string and null → STRING, integer → INTEGER (int64 LE), real → REAL (double), table → TABLE, list/record/set → DATA (SCRIP boxes them so), procedure → CODE, file → FILE, else UNKNOWN (graded UNGRADED on the controller's VERDICT line since SCRIP `1fa63bb9f` -- counted and named, never a match; until then it was a type-and-value wildcard that read AGREE). (Icon: the fire-point sits at the end of `GeneralAsgn`, so `:=`, augmented ops, `<-`, `:=:` and `<->` all report; SCRIP's hook precedes the store so a re-targeted γ port cannot skip it.)
- **CALL** — at entry of a user procedure with its name; builtins are never events.
- **RETURN** — at an explicit return with the returned value; suspend and fail are not events today on either side (extend both plugs together).
- **THE PROLOG READING OF THE CONTRACT (ceo, 2026-09-23, from the GNU Prolog lock-step):** a body goal is a statement; `,` `;` `|` `->` `*->` are not statements and are walked at any nesting; every other goal is ONE statement with its own first-token line — `\+ G`, `call(G)`, `findall/3`, `catch/3` and every other goal with a goal ARGUMENT fire one statement and NOTHING inside it from the plug (the argument is data on the oracle side; the callee's own clauses still report), a variable goal is a statement, directive goals are silent; CALL fires ONCE at the predicate's entry (a retry into another clause on backtracking is no event); RETURN fires at EVERY clause success with the empty STRING as its value (a tail call is not sealed under the trace so the caller's clause reports too); builtins AND the compiler's own library predicates are never events (SCRIP's plug breaches this today: `member/2`, `append/3`, `length/2`, `$length_/3` report with the prelude's lines — hq_prolog's row); VALUE is no event for Prolog today (extend both plugs together).
- The witness for each language lives in `scripts/monitor/witnesses/sync_step_<lang>.icn|pl|pas|raku`; a second, widened witness (`_2`) is the language HQ's row: it agrees to its end when the plug is complete.

**Icon, landed 2026-09-23 05:1x (SCRIP `d85e6186d`):** `icon-mon.patch` over `/home/resources/icon-master` (opdefs.h `Op_Stmt` 111, rproto.h, opcode.c, lcode.c, tcode.c, interp.r at `Op_Stmt` and `Op_Pret`, invoke.r at the `ctrace` site, oasgn.r at the end of `GeneralAsgn`, the runtime Makefile), `monitor_icx.c` (names a store the way iconx's `name()` does: globals by `gnames`, arguments/locals/statics by the proc's `lnames`), `build_icon_mon.sh` (4 s, control arm green). Participant `icx`; `monitor_run.sh prog.icn --oracle` = `icx scr`. Readings: `sync_step_icon.icn` DIVERGE at 2 (SCRIP counted the `local` line as a statement), DIVERGE at 5 (SCRIP's every-loop stores went unreported — the value hook hung off the assignment's γ port, which `lower_every` re-targets), then **AGREE at step 17** after the two plug cures; the widened `sync_step_icon_2.icn` agrees through 15 and diverges at 16 on a REAL SCRIP DEFECT: `s ||:= sq(i)` with `s == ""` stores INT 1 where Icon stores STRING "1" — hq_icon's row (`icon-monitor-the-instrumented-iconx-oracle-is-completed-and-used-…`, assigned on Lon's word: *"hand that off to HQ-ICON to complete and use"*). Own-language arm: Icon master m3 826/826 · m4 826/826. Refusal by name when the fork is absent.

**GNU Prolog, landed 2026-09-23 06:1x (SCRIP `4a9d5a698`):** `gprolog-mon.patch` over `/home/resources/gprolog-master` (the 1.6.0 drop; `/usr/bin/gprolog` is 1.4.5, so the participant is a 1.6.0 engine beside the recorded oracle): `Pl2Wam/pl2wam.pl` injects, for every USER predicate compiled to native code (never a `built_in`, aux, dynamic, multifile or public one, never a directive), a `call_c Pl_Mon_Call(at(name), arity)` at the predicate's entry before indexing, a `call_c Pl_Mon_Stmt(line)` before every body goal, and a `call_c Pl_Mon_Return` at the end of every clause (a fact included; the last goal becomes a `call`, so every clause success reports); `BipsPl/parse_supp.c` builds a MIRROR beside every term the reader reads once `Pl_Mon_Mirror_On_0` was called — `'$m'(StartLine, [MirrorLeft, MirrorRight])` per infix-operator compound, the start line for anything else — and `Pl2Wam/read_file.pl` carries the clause's mirror in its line span as `L1 - '$ln'(L2, Mirror)` so pl2wam stamps each goal with its own line (the clause's first line where the mirror does not align, e.g. term_expansion output); `EnginePl/monitor_gpx.c` spells the name `name/arity` as SCRIP's key does (the `at(N)` argument is a hash slot bounded by `pl_max_atom`, not `pl_nb_atom`); `build_gprolog_mon.sh <prefix>` builds fork and pristine (about 3 + 2.5 minutes), recompiles the two patched `.pl` with the stage-1 pl2wam (⛔ gplc finds pl2wam, wam2ma and ma2asm by PATH SEARCH — the fork's bin is prepended everywhere it is invoked, and `install-system install-links` is used because the drop's `install` fails on missing HTML docs), asserts the fire-points are in the witness's WAM, and ends in the control arm. Participant `gpx`, `.pl --oracle` = `gpx scr`. Readings: `sync_step_prolog.pl` AGREE at 9; `sync_step_prolog_2.pl` (indexing, cut, recursion, arithmetic, if-then-else chain, disjunction, negation, facts with a live choice point) AGREE at 57; `sync_step_prolog_3.pl` (multi-line clauses) DIVERGE at 2 before the mirror, AGREE at 16 after; `sync_step_prolog_4.pl` DIVERGES at 5 on SCRIP's library-predicate events and shows `atom_codes(A, "hi")` raising `type_error(list, hi)` — hq_prolog's row (Lon 06:1x: *"that is plenty good enough. hand it over to HQ-PROLOG."*). Three SCRIP plug cures under the trace gate: the statement wrap moved from `pl_leaf` to the goal dispatcher (user calls, `=`, `is`, comparisons and `!` fired nothing before), the tail-call seal is off under the trace (a sealed last call skipped the clause's RETURN), a variable goal is a statement. Own-language arm: Prolog master m3 563/563 · m4 480/480. Not instrumented on the oracle side today: dynamic/multifile/public predicates (their clauses are asserted terms — a `call_c` in data would not run), consulted (byte-code) programs, and anything inside a meta-argument. ⛔ The ceo's classifier refused the default-prefix install (`/home/resources/gprolog-mon`, "Modify Shared Resources") — Lon runs `bash SCRIP/scripts/monitor/oracles/build_gprolog_mon.sh /home/resources/gprolog-mon`; until then `GPROLOG_MON_ROOT` names a seat's private prefix and every seat builds its own in about six minutes.

**Free Pascal, landed 2026-09-23 07:3x (SCRIP `220cd725a`, the coo on Lon's 06:32 word; CEO-1192):** `fpc-mon.patch` over `/home/resources/FPCSource` (main, 3.3.1 of 2026-08-26; the recorded oracle `/usr/bin/fpc` is 3.2.2 and is the starting compiler, so the participant is a 3.3.1 engine BESIDE the 3.2.2 oracle, the gprolog shape) plus three files the build script copies in: `compiler/nmonipc.pas` (the injector), `rtl/inc/monipc.inc` + `monipch.inc` (the fire-points, the shared wire written in Pascal over the system unit's own `Fpopen/Fpwrite/Fpread/Fpclose` and `envp`, since a Free Pascal program links no libc; `MWK_END` from `InternalExit`). The fork's compiler takes `-gi` (`cs_monitor_ipc`): `pstatmnt.pas` fires STMT at the start of every element of a statement list (`begin`/`repeat` lists, never an empty statement) with the statement's own first-token line, VALUE after every store to a named variable (the function result under the function's name, a structure element as `<lval>`) and at the top of every for-loop iteration for its control variable; `psub.pas add_entry_exit_code` fires CALL at every user procedure's entry and RETURN at its exit label with the function's result (a procedure returns the empty STRING). Types: integer ordinals INTEGER, real REAL, char / shortstring / ansistring / packed char array STRING, boolean and enumerated values as their identifier (lower case, as SCRIP's `__pas_enum_name` spells it), else UNKNOWN. `build_fpc_mon.sh <prefix>` (about 45 s + 30 s for the pristine control build at load 3) installs `<prefix>/bin/fpc` (a driver: `ppcx64 -n -Fu<prefix>/lib/units`, so no `fpc.cfg` can point it at the 3.2.2 units; use `fpc -Miso -gi -o prog prog.pas`), asserts the fire-points are in the witness's binary and ends in the CONTROL ARM (pipes unset: stdout and rc equal the pristine 3.3.1 build's). Participant `fpx`; `.pas --oracle` = `fpx scr`. Readings: `sync_step_pascal.pas` AGREE at 15; `sync_step_pascal_2.pas` (function, procedure, if/else, while, char, boolean) AGREE at 25; `sync_step_pascal_3.pas` (enumerated type, repeat, a for loop over a procedure local) AGREE at 32; `sync_step_pascal_4.pas` DIVERGES at 3 on the NAMED GAP that is hq_pascal's first item: an array-element store is `<lval>` on the oracle side and no event in SCRIP's plug (`read`/`readln` stores are the other unreported store). Five SCRIP plug cures under the trace gate, untraced emission proven identical (`--dump-ir` 60/60, `--compile` 20/20 against the pre-cure binary): the statement line was the token AFTER the statement's (a mark-and-fill stack around each list element now gives the first token's line), the empty statement before `end` fired, the for loop stored past its limit under the trace and locals' control variables never reported, the runtime tap double-reported every global store in its raw boxing (`__trace_tap_off` is injected first, so every Pascal VALUE comes from the plug's own injection, function-result stores and enumerated variables included), and `__pas_chr`/`__pas_enum_name` built their string descriptor without `slen` so the wire sent `STRING(0)`. Not instrumented on the oracle side today: nothing known; not reported on SCRIP's side: element stores, `read`/`readln` stores. ⛔ The coo's classifier refused the default-prefix install — Lon runs `bash SCRIP/scripts/monitor/oracles/build_fpc_mon.sh /home/resources/fpc-mon` (about 75 s); until then `FPC_MON_ROOT` names a seat's private prefix (the coo's is `/home/claude_coo/.scratch/fpc-mon`) and every seat builds its own in about a minute.

**Rakudo, landed 2026-09-23 07:xx CDT by the cfo on Lon's word (in-chat to the cfo, 06:3x: *"Build the Rakudo IPC sync-step monitor inside Rakudo just like CEO did for Icon and Prolog and get a few hello world type programs working, then hand off to HQ-RAKU to complete so he can use the instrumented Rakudo to find and fix bugs in SCRIP."*):** `rakudo-mon.patch` over the pristine `/home/resources/rakudo-2026.05.tar.gz` release (the shared oracle `rakudo-local` is that release; the fork is configured `--with-nqp=/home/resources/rakudo-local/bin/nqp-m`, so it runs on the oracle's own MoarVM and NQP and only the Rakudo compiler is rebuilt), four files: `src/vm/moar/ops/perl6_ops.c` registers the fire-points beside Rakudo's own extops (`Rakudo_mon_ops_init`), `src/vm/moar/Perl6/Ops.nqp` teaches the QAST compiler four ops `p6monstmt(line) · p6moncall(name) · p6monval(name, value) → value · p6monret(name, value) → value`, `tools/templates/moar/Makefile.in` compiles `monitor_rkx.c` and the shared `monitor_ipc_lib.c` into `libperl6_ops_moar.so`, and `src/Perl6/Actions.nqp` injects them into THE USER'S COMPILATION UNIT ONLY (`mon_active()`: never while `$*COMPILING_CORE_SETTING`, never under `--output`/`-o` -- every precompilation, so CORE and every installed module are never events -- and `RAKUDO_MON=0` turns the injection off for a control compile): `statementlist` wraps every statement that is not a routine/package/type/regex declaration as `QAST::Stmt(p6monstmt(line), stmt)` -- ⛔ INSIDE the statement's own node, never as a sibling, because Rakudo reads a block's first statement by index (`circumfix:sym<{ }>` decides hash-or-block from `[1][0][0]`, the CATCH/QUIT handler pushes `$_` into `[1][0]`); the one index reader that sees through the wrapper is patched (`mon_first_stmt_child`), and the first shape (a sibling node) broke `make install` itself because `Distribution::Hash.new({ name => … })` compiled as a Block; `comp_unit` prepends `p6moncall('main')` as SCRIP's plug spells the mainline; `routine_def`/`method_def` wrap the body AFTER its return handler and type check as `Stmts(p6moncall(name), p6monret(name, body))`, so an explicit `return` (which unwinds to the handler inside the wrap) and a fall-off value each report ONCE, as SCRIP's plug does; `assign_op` wraps every `=` store to a lexical `$`/`@`/`%` as `Stmts(:resultchild(0), store, p6monval(name, Var))` (the value is read back after the store; a scalar's name loses its sigil, `@a`/`%h` keep theirs, as SCRIP spells them) and `EXPR` does the same after a `&METAOP_ASSIGN` call (`+=`, `~=`, …). The hook nodes are marked `sunk`/`wanted` so the want/sink walkers leave them alone. `monitor_rkx.c` types a value by its storage spec (Str → STRING utf-8, Int → INTEGER int64 unless big, Num → REAL; Bool boxes as an Int), by its type name for Array/List/Seq/Slip/Range → ARRAY, Hash/Map → TABLE, Sub/Block/Method/Routine/Code → CODE, IO::Handle → FILE, and everything else -- Rat included -- as UNKNOWN with no bytes, ⛔ which the controller wildcarded on type AND value bytes until SCRIP `1fa63bb9f`, so a wrong SCRIP Rat read AGREE; since then that step is UNGRADED, counted and named on the VERDICT line and never a match -- a wrong Rat is still NOT CAUGHT, only VISIBLE (hq_raku's row when it matters: a Rat wants REAL from its numerator and denominator). `build_rakudo_mon.sh <prefix>` (measured from scratch, 307 s wall at load 12 on 16 cores: unpack, patch, configure, make, install; the three CORE settings dominate) asserts the four fire-points are in the witness's `--target=ast` and ends in the control arm (pipes unset: fork stdout and rc equal the pristine oracle's). Participant `rkx`, `.raku --oracle` = `rkx scr`; the rejected stderr-replay bridge (`raku_oracle_bridge.py`, the `.oracle.raku` twin, participant `rko`) is deleted. READINGS, all four hello-world witnesses AGREE with SCRIP event-for-event after four SCRIP plug cures under the trace gate: `sync_step_raku.raku` 21 steps, `sync_step_raku_2.raku` (say, interpolation, explicit and implicit returns, `+=`, if/else, while) 32, `sync_step_raku_3.raku` (recursion, `~=`, nested if in for) 86, `sync_step_raku_4.raku` (array and hash stores, list for, method calls) 32; two wider probes 36 and 33. THE FOUR SCRIP-SIDE CURES THE ORACLE EXPOSED (untraced emission unchanged: 889 Raku sources -- the master's distinct entries plus six probes -- compiled to `.s` by the parent tree and this one, 0 differ): (a) a statement's line was the line where the parser REDUCED it (a multi-line `for`/`if`/`while` reported its closing brace, sometimes the next statement's line), and a block's trailing statement without `;` had no line at all -- `raku.y` now runs with `%locations`, the lexer stamps every token's first line (a string literal keeps the line it opened on), and every statement carries the line of its FIRST token; (b) `my $u;` fired a VALUE of the empty string -- a bare declaration stores nothing, so it fires none (the parser marks the declaration's null); (c) `for @a -> $x` fired a VALUE for the loop variable, which is a parameter binding, not a store -- the synthesized `__decl` binding is silent (a range loop never fired one); (d) `use v6;` fired a STMT -- a pragma is not a statement; and on the wire, a `@`/`%`-named store (SCRIP keeps a Raku array as a `\x01`-joined string) is sent as ARRAY/TABLE with no bytes, as the oracle sends it, while the text trace keeps its `'312'` spelling. Own-language arm: the Raku master in both modes on this tree, see GOAL-CFO CFO-152 for the count. Not instrumented on the oracle side today: `.=` and the `||=`/`&&=`/`//=` test-assign forms, stores to attributes (`$!x`) and to `$_`-less specials, `return` with zero or several values (no event on either side), methods without a name; a `sub MAIN` reports as `MAIN` after `main`. ⛔ The classifier refuses the default-prefix install under `/home/resources` -- Lon runs `bash SCRIP/scripts/monitor/oracles/build_rakudo_mon.sh /home/resources/rakudo-mon` (about five minutes); until then `RAKUDO_MON_ROOT` names a seat's private prefix.

## ⭐⭐⭐ THE ORACLE-SIDE BRIDGES ARE EACH HQ'S OWN (Lon 2026-09-23 03:34 CDT, in-chat to the ceo, verbatim: *"You can have each HQ do their own."* — CEO-1186)

Lon asked (03:2x): *"How many third-party trace instrumentations have you accomplished so far? FPC? SWIPL? GNU Prolog? Rakudo?"* — the honest count is ZERO. SNOBOL4's three oracle participants (csnobol4 `csn`, the SPITBOL x64 fork `spl`, .NET `dot`) predate this design and were built by instrumenting each engine's source. For Icon, Prolog, Pascal and Raku the monitor on origin is SCRIP-against-SCRIP (mode 3 against mode 4, `scr3`/`scr4`) plus `--trace`. An oracle bridge is a participant that emits the same STMT/VALUE/CALL/RETURN events from the ORACLE's own execution over the same READY/GO pipes, so the controller can hold SCRIP and the oracle in lock-step. Each is its language HQ's row (`<lang>-monitor-oracle-bridge-*`, minted and assigned 2026-09-23 03:4x). The ceo's probe of each oracle, so no HQ starts from zero:

| Oracle | What it offers without an engine change | Events reachable | The catch |
|---|---|---|---|
| Icon, Arizona `icont`/`iconx` 9.5.25a | `&trace := -1` prints `file : line | proc(args)`, `proc returned v`, `proc suspended v`, `proc failed` to stderr, with source lines | CALL, RETURN (with lines) | statement and value events need an `iconx` fork — that is an oracle swap (RULES.md § Oracles, the ORACLE-SWAP PROCEDURE, Lon's go) |
| SWI-Prolog `swipl` | `user:prolog_trace_interception/4` under `trace`, `leash(-all)`: one hook per port (call/exit/redo/fail/unify) with the goal term and the frame; `clause_property(Cl, line_count(L))` at unify; goal lines through `library(prolog_clause)` `clause_info/4` | STMT (per goal), CALL, RETURN, VALUE (bindings at exit) | the bridge is pure Prolog loaded beside the witness — no engine change; SCRIP's Prolog STMT event carries only the line, so the bridge maps the call port to `L<line>` |
| GNU Prolog `gprolog` 1.4.5 | `trace` prints `Call: goal ?` / `Exit:` text and waits for a debugger keystroke per port | CALL, RETURN by parsing the debugger text with answers piped in | no hook API; do SWI first |
| Free Pascal `fpc -Miso -gl` | no runtime hook; `gdb -batch` on a `-gl` binary: `next` + `info line` walks statements by source line, `break` on every procedure gives entry/exit, `print v` after an assignment line gives its value | STMT, CALL, RETURN, VALUE | the bridge drives gdb with a script generated from the witness's source; slow, fine for a witness |
| Rakudo `raku` v2022.12 / MoarVM | no trace hook in the VM or the compiler; the ecosystem `Trace` module is NOT installed, `zef` is not on the box (a HEAD to raku.land answered HTTP 405, so the network is reachable) | none today | either Lon allows installing zef + Trace, or the bridge is a source-level injection of `note` calls on the oracle side |

The wrapper's `--oracle` arm is the seam: `monitor_run.sh` maps the extension to its participants (`sno) parts="spl scr"` today); a bridge lands by adding its participant to `test_monitor_3way_sync_step_auto.sh` (its allowed list and its start block) and its extension arm to the wrapper, and is proven the way every participant is: AGREE on the language's `sync_step_<lang>` witness, DIVERGE when the oracle side runs a one-line variant of the witness (fail-once), and a REFUSE with the participant's name when it never starts.

## ⭐⭐⭐ SNOBOL4 ON THE SHARED HOOKS — WHAT ITS OWN WIRE DID, WHAT WAS WRONG WITH IT, WHAT IS BETTER NOW (ceo 2026-09-23 04:04 CDT, CEO-1187; Lon: *"upgrade the SNOBOL4 to use your new wire. BTW, what is better about your new way? what was wrong with how SNOBOL4 did things?"* and *"Are you sure call/return do not work for SNOBOL4?"*)

**Correction first.** SNOBOL4 already had all four event kinds on its own wire — the ceo's table of 03:4x was wrong on that cell. The hook POINTS were SPITBOL's own: `comm_var` (the `sysmv` analogue, every named store including the pattern-capture and cell stores), `comm_call`/`comm_return` (`sysmc`, the DEFINE'd function's entry and its RETURN/FRETURN), the statement label tap in `bb_statement` (`sysml`), and the runtime sinks for indirect, subscript and element stores. Those points are RIGHT and they stay: they are exactly where the SPITBOL fork fires, which is what the oracle lock-step compares.

**What was wrong, measured on the witness `scripts/monitor/witnesses/sync_step_snobol4.sno` (a DEFINE'd function, an FRETURN, pattern captures, a table and an array element store, an indirect store, OUTPUT):**
1. **Two carriers, three switches.** `comm_var` forwarded a store only when `kw_trace > 0` (that is `SCRIP_TRACE`) or the name was TRACE'd; the rt.c sinks and the DEFINE taps forwarded only when `g_monitor_bin` (that is `MONITOR_BIN` at run time, and `--monitor` at COMPILE time for the label taps in `emit.cpp:1286`, which is why the m4 participant had to be compiled with `--monitor`). Which events a run carried depended on which of three switches were set.
2. **The human trace and the wire were two different outputs.** `comm_call` printed its `****` line only when NOT binary-monitored (`kw_ftrace > 0 && !g_monitor_bin`), so a monitored run had no readable trace and an unmonitored run had no wire; `--trace` on a `.sno` printed NOTHING (measured at `f93308995`: zero `****` lines).
3. **It had never been held against the oracle on an ordinary program.** On the unchanged tree the SPITBOL lock-step DIVERGED AT STEP 14 on the FIRST `OUTPUT = y`: SCRIP sent a VALUE event for the store to OUTPUT and SPITBOL does not (the store goes to the output association, not to a variable); and had that passed, it would have diverged at the first table element store, where SCRIP's fast path (`c_rt_table_assign_fast`) sent no `<lval>` event and SPITBOL sends one. Every SNOBOL4 program prints, so the SCRIP-against-SPITBOL arm was red on essentially every program and nobody had read it.
4. **The codegen switch.** `bb_call_proc_staged.cpp:189` disabled the static call convention under `g_monitor_bin`, and the DEFINE template carried a run-time GOT test of `g_monitor_bin` in its prologue and epilogue instead of a compile-time gate (a verdict on a different program — the CLAUDE.md hazard line).

**What is better now, measured:**
- **One flag.** `--trace` / `--trace=N` / `SCRIP_TRACE` gate every SNOBOL4 event at compile time (the statement tap, the DEFINE taps) and at the runtime sinks; `MONITOR_BIN`/`--monitor` is transport only (the pipe). The three SNOBOL4 plug entries are `sno_trace_value`, `sno_trace_call`, `sno_trace_return` in `core.c`, each a SNOBOL4 filter (the `_`/`&`/internal/output-association rules, the synthesized-name rule, RETURN/FRETURN on the wire as SPITBOL spells it) in front of the shared `rt_trace_*` hook; the statement tap calls `rt_trace_stmt(stno)` directly. `mon_emit_value_bin`, `mon_emit_call_bin`, `mon_emit_return_bin` are deleted.
- **The trace and the wire are one call.** `./scrip --trace --run x.sno` prints `****N  L<stno>` / `name = value` / `f()` / `RETURN f = v` like every other frontend (the witness: 24 statement, 7 value, 2 call, 2 return events), and the same call sends the wire record; the initialization-time stores of the pattern keywords (`ARB = PATTERN` …) are silenced until the first statement event, as the wire always silenced them.
- **SCRIP against SPITBOL AGREES on the witness, step 41 of 41** (⛔ READ SINCE SCRIP `1fa63bb9f` AS `AGREE=39 DIVERGE=0 UNGRADED=2`: SPITBOL sends the TABLE `t` and the ARRAY `a` untyped, so those two steps were never compared -- no divergence, and not 41 agreements either; the coo 2026-09-23), after two cures the old wire could never have shown: a store to OUTPUT, TERMINAL or any output-associated variable is not a value event (`sno_name_is_output_assoc`), and the table fast path emits `<lval>`.
- **SNOBOL4 is the fifth language on the one harness:** `monitor_run.sh x.sno --modes` (mode 3 against mode 4, AGREE at step 41) and `--oracle` (`spl scr`), and `test_monitor_2way_sync_step_all_langs.sh` reads `languages=5 pass=5`.
- **Untraced code is untouched:** mode-4 asm of the witness on the cure tree is byte-identical to the control tree's; the SNOBOL4 master is the own-language arm: m3 1960/1965, m4 1956/1965, all 14 reds standing on the control tree too (CEO-1187, SCRIP `9a1792707`).

**Found, not cured (not this row):** the `csn` participant (csnobol4's bridge, binary of 2026-08-22 carrying `MONITOR_READY_PIPE`) never opens its FIFO within 20 s and runs the program to completion — the 3-way `csn spl scr` REFUSES rc=2 on this box today, independent of SCRIP; and `DEFINE('f()')` placed after a call to `f()` runs in SCRIP where SPITBOL raises ERROR 022 (the ceo's first witness, both modes) — a SNOBOL4 row.

