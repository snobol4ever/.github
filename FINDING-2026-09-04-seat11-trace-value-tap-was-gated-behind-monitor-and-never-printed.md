# FINDING — `TRACE()`/`&TRACE` VALUE tracing produced zero output because its runtime hook was only ever compiled in under `--monitor`, and even there had no direct stdout path; fixed for the VALUE case, CALL/RETURN and KEYWORD tracing remain broken

**seat11 (`/home/claude11`, Claude Sonnet 5), 2026-09-04, THE LOOP row
`snobol4-csnobol4-trace-builtin-and-ftrace-produce-zero-output` (hq_P lane, MODE FLEET-16
SNOBOL4-only). Task ASSIGNED to seat11 by hq_P; this FINDING is the receipt.**

## WHAT

`comm_var(name, val)` (`src/runtime/core/core.c`) is the runtime hook meant to back `TRACE(name)`
(VALUE type) and `&TRACE`. It was already correctly self-guarded internally (early-return unless a
trace/monitor is actually active), matching its own comment. But its **call site**
(`src/templates/bb/bb_assign_global.cpp`, the box that compiles every global-variable assignment)
only emitted the `call comm_var` instruction at all when `IF(g_monitor_bin && mon_vars_on(), ...)`
— i.e. only in binaries built with `--monitor`, which no ordinary `./scrip prog.sno` run or
`test_snobol4_csnobol4_suite.sh` invocation ever uses. Two of the four assignment code paths in that
file (the non-GVA `NV_SET_fn`/`call_bare NV_SET_fn` paths) had **no tap at all**, not even under
`--monitor`. And even when reached, `comm_var` only ever forwarded through `mon_send()` (the IPC
monitor protocol, requires a live `monitor_fd`) — unlike `comm_call`/`comm_return`, it had no direct
`fprintf(stdout, ...)` branch for the ordinary case. Net effect: `TRACE(name)` produced byte-empty
output in every normal run, matching all seven programs named in this row's GOAL.

`comm_call`/`comm_return` (the `&FTRACE`/`TRACE(name,"CALL")` backing) DO have a direct-print
branch already, correctly gated on `kw_ftrace > 0 && !g_monitor_bin` — but the only C caller of
either is `driver_call.c`'s `call_user_function`, reachable solely through the by-name-dispatch
fallback (`_usercall_hook`) used for indirect/dynamic calls. An ordinary statically-resolved
`DEFINE`'d call (`F(1)`) compiles straight through `bb_call_fn.cpp` → the callee's `bb_define.cpp`
entry → `bb_return.cpp`, none of which reference `comm_call`/`comm_return` at all. So CALL/RETURN
tracing is dead from the compiled path regardless of the monitor gate — a separate, deeper gap (see
NOT DONE below).

## FIX (this row, VALUE type only)

- `src/templates/bb/bb_assign_global.cpp`: dropped the `g_monitor_bin &&` half of the gate on all
  four assignment paths (two now tap where they previously had none), added `mon_var_trace_tap()`,
  a self-contained push-everything/call/pop-everything sequence (mirrors the existing
  `x86_pl_trace_ev` idiom byte-for-byte in structure) that calls the widened `comm_var` with the
  variable's value plus three **compile-time constants**: the source filename (embedded as a fresh
  `.rodata` string via the same dual-medium `lea [rip+__]` pattern `bb_call_fn.cpp` already uses for
  binary-vs-text safety), this box's `_.op_line`, and its `_.op_stno`. R8/R9/RCX are saved/restored
  around the call because R9 carries the live GVA base and R8 carries RTCC arg-tier state elsewhere
  in this same file — clobbering either without restore would be silent, distant corruption, not a
  crash.
- `src/emitter/emit.cpp`: `_.op_line` was computed **only** when DWARF `.loc` emission was on
  (`_dl`), and even then wasn't sticky — it read `bb_line_of(nd)` for the *current* node on every
  visit and reset to 0 whenever that specific node had no entry in `g_bb_src`, wiping the correct
  value read moments earlier for the enclosing statement. Made the computation unconditional and
  sticky (`if (_ln > 0) g_emit.op_line = _ln;`, matching how `op_stno` already behaves) while leaving
  the actual `.loc` directive emission gated exactly as before.
- `src/runtime/core/core.c`: `comm_var` gained a genuine `fprintf(stdout, ...)` branch, gated on
  `!g_monitor_bin && (kw_trace > 0 || trace_registered(name))`, formatted
  `%s:%ld stmt %lld: %s = %s, time = %g\n` — confirmed against the live oracle
  (`/home/resources/csnobol4/snobol4`) to be its exact shape (path:line, a runtime statement
  counter, name/value, elapsed seconds). Six other pre-existing `comm_var(name, val)` call sites
  (the interpretive/shadow-variable slow paths in `core.c`, `pattern_match.c`, `driver_globals.c`)
  needed updating to the new 5-arg signature; they pass `stmt_src_get_file(), 0, 0` since none of
  those call sites have per-statement line/stmt info available — an honest degradation, not a new
  defect, since none of them are the primary compiled path.
- `SCRIP/scripts/test_snobol4_csnobol4_suite.sh`: `compile_m4` was called with `$prog` (the absolute
  scratch-copy path) instead of `$relprog`, unlike the m3 call three lines above it which already
  carries a comment explaining exactly why that matters ("every self-path-referencing program
  (TRACE(), error messages, &FILE) embed[s] a throwaway tmpdir string instead of the bare name the
  .ref expects" — row `snobol4-csnobol4-thirty-regen-candidate-refs-stale-pin-or-real-defect`,
  seat07). This was inert while tracing produced no output at all; fixing the VALUE tap made it
  visible for the first time (`trace2` passed m3, failed m4 on path text alone). Wrapped the call in
  `(cd "$RUN" && compile_m4 "$relprog" ...)`, mirroring the m3 invocation's own subshell-cd pattern.

## EVIDENCE

`trace2.sno` (`-CASE 0`, so `foo`/`FOO` are genuinely distinct under SCRIP's case-sensitive design —
see NOT DONE re: `trace1.sno`) now matches its `.ref` byte-for-byte (after the suite's own
`time = xxx` masking) in **both modes**:
```
$ ./scrip corpus/packages/snobol4/csnobol4_suite/trace2.sno < /dev/null
trace2.sno:4 stmt 3: foo = 1, time = 0.00229197
trace2.sno:6 stmt 5: foo = 3, time = 0.00232809
$ cat corpus/packages/snobol4/csnobol4_suite/trace2.ref
trace2.sno:4 stmt 3: foo = 1, time = xxx
trace2.sno:6 stmt 5: foo = 3, time = xxx
```
Mode 4 (`--compile` → `as` → `gcc` → run) reproduces the same two lines exactly (module the
invocation path in the filename field, expected since m4 was run with a different argv[0] path
here).

**No regression**: `test_corpus_snobol4.sh` (the 1768-entry master board) reads identical to the
pre-existing baseline both before and after this change — `mode-3 PASS=1729 FAIL=2`,
`mode-4 PASS=1729 FAIL=1 SKIP=1`, the same two already-documented names
(`simple_output_276`, `user_function_len_defer_branch_6`) both times, re-confirmed on a clean,
otherwise-idle run after one run under heavy concurrent load transiently read FAIL=3 (not
reproducible; almost certainly a load-induced flake on this 16-seat shared box, not this change —
see the script's own printed caution that an `rc=124`/timeout-adjacent read cannot distinguish slow
from hung).

`test_snobol4_csnobol4_suite.sh` board (118 pairs): `m3 PASS 52→58, m4 PASS 52→57` (informational —
this run's numbers are a scouting datum per the harness's own dirty-tree notice; the landed row is
whichever clean-tree run happens after this commit). `trace2` left both RED lists entirely. The
`nqueens` CRASH-vs-FAIL split moved by one between two consecutive runs here, which is the
already-documented pre-existing ASLR-sensitive flake for that specific entry (see this suite's
row `snobol4-csnobol4-nqueens-sigsegv`), not something this change touches.

`strip_comments.py --check`, `test_gate_icn_scan_argtype.sh`,
`test_gate_ref_cutters_refuse_a_dead_oracle.sh` all still pass. `make test`'s overall non-zero exit
is the pre-existing, already-documented `user_function_len_defer_branch_6` m4 red (GOAL-SNOBOL4-100
LIVE CURSOR, 2026-09-04 18:37 CDT entry: "Until the cure lands the m4 arm of `make test` is red on
origin for exactly this entry") — unrelated to and unchanged by this row.

## NOT DONE / OUT OF SCOPE

Of the seven programs named in this row's GOAL, only the VALUE-tracing mechanism itself is fixed
here. That resolves `trace2.sno` outright. The other six stay red, each for a **different,
independent** reason — do not re-derive any of this without re-checking, but do not assume it is
still true either:

- **`trace1.sno`**: no `-CASE 0` pragma, so live `csnobol4` case-FOLDS `foo`/`FOO` to one variable
  (`FOO`) in its own default dialect; SCRIP is deliberately case-sensitive
  (`CLAUDE.md` § Semantics), so `foo`/`FOO` are two different variables here and only the
  `TRACE('foo')`-registered one traces. Likely a permanent, accepted oracle-quirk divergence for
  *this specific file*, not a SCRIP defect — needs a ruling, not a fix, if it's ever to leave RED.
- **`keytrace.sno`**: uses `TRACE("STCOUNT", "KEYWORD")` (and similar for `FNCLEVEL`/`STFCOUNT`/
  `ERRTYPE`). `_TRACE_` (`core.c`) only registers the `"VALUE"` type string; `"KEYWORD"` (and the
  single-letter abbreviations `t.sno` also uses — `'f'`/`'v'`/`'k'`) fall through and register
  nothing. Even if they did, keyword mutation (e.g. `g_stcount++` in `keywords.c`'s
  `rt_stmt_enter`) happens at dozens of scattered direct-C-increment sites, not through one
  chokepoint `comm_var` can be spliced beside — this is a materially bigger, separate task.
- **`ftrace.sno`, `trfunc.sno`, `t.sno`**: need CALL/RETURN tracing, which (per WHAT above) requires
  wiring `comm_call`/`comm_return`-equivalent hooks into the actual compiled call boxes
  (`bb_call_fn.cpp` for the call site, `bb_define.cpp`/`bb_return.cpp` for entry/return), reformatting
  their output to CSNOBOL4's `level N call of NAME(args)` / `level N RETURN of NAME = value` shape
  (confirmed against the live oracle; `comm_call`'s current dead-code format is SPITBOL's own
  `****N  NAME()`, which is wrong for *this* oracle too), and a genuine nesting-safe call-depth
  counter — the existing `kw_fnclevel`/`rt_k_level` machinery is Icon-specific and itself incomplete
  per its own in-source comment ("Entry-side increment still NOT YET LANDED"). Not attempted here:
  real risk to `bb_call_fn.cpp`/`bb_define.cpp`, two of the most heavily-used, least-forgiving files
  in the compiler, is materially higher than the well-isolated `bb_assign_global.cpp` change made
  here, and deserves its own dedicated row with its own ASM-DIFF-FIRST pass rather than being rushed
  in beside this one.
- **`spit.sno`**: fails for a wholly unrelated reason confirmed by direct inspection — a `FATAL
  lower_snobol4 (GZ#5 subset)` pattern-matching refusal on a construct outside the landed SN4-PAT
  subset, hit before any of its three `TRACE(.a, .value)`-style lines would even run. Not a tracing
  defect at all.

An audit of whether OTHER (non-package, non-named) corpus entries rely on VALUE tracing and newly
pass as a side effect of this fix was not done beyond what `test_corpus_snobol4.sh`'s unchanged
FAIL=2/FAIL=1 already proves (nothing newly broke; whether anything newly *fixed* elsewhere in the
1768-entry master was not individually inventoried).

## WATERMARK

`SCRIP/src/emitter/emit.cpp`, `SCRIP/src/runtime/core/core.c`, `SCRIP/src/runtime/core/core.h`,
`SCRIP/src/templates/bb/bb_assign_global.cpp`, `SCRIP/src/runtime/pattern_match.c`,
`SCRIP/src/driver/driver_globals.c`, `SCRIP/scripts/test_snobol4_csnobol4_suite.sh`. corpus
untouched. `.github`: this FINDING + the task baton's LEDGER/NEXT.
