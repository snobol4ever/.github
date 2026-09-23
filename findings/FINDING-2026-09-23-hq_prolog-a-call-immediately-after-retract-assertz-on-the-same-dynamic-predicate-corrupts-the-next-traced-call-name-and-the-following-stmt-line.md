# FINDING 2026-09-23 hq_prolog: a CALL immediately after `retract`/`assertz` on the same dynamic predicate corrupts the next traced CALL's name and the following STMT's line number

## WHAT WAS WRONG

Found via the IPC sync-step monitor (row
`prolog-monitor-the-instrumented-gprolog-oracle-is-completed-and-used-...`), witness
`scripts/monitor/witnesses/sync_step_prolog_4.pl` DIVERGE at step 35 — but the corruption is **not** a
monitor/oracle contract artifact (the `## NEXT` block's item 2 guessed "the oracle side does not instrument
dynamic predicates," which is a real, separate, still-open gap, but is not what this is). It reproduces in
plain `--trace` mode with no monitor involved at all, on a 4-line witness with no oracle in the loop:

```prolog
:- dynamic(counter/1).
counter(0).
bump :- retract(counter(N)), M is N + 1, assertz(counter(M)).
main :- retract(counter(N)), M is N+1, assertz(counter(M)), counter(C), write(C), nl.
:- initialization(main).
```

`--trace --run` output (SCRIP `<pre-this-session's-two-commits>`, unchanged by anything landed this
session):

```
****1        main/0()
****2        L3
****3        L3
****4        L3
****5        L3
****6        ()
****7        L209
****8        RETURN  = ''
****9        L3
1****10       L3
****11       RETURN main/0 = ''
```

Event 6 should read `counter/1()` (confirmed: calling `counter/1` **without** a preceding retract/assertz
in the same body traces correctly as `counter/1()` — see `/tmp/probe_dyn_direct.pl` in this session's
scratch). Event 7 should read a real source line (`L4`, or whatever the compiler numbers that goal) — `209`
is nowhere near this 4-line file. Event 8's RETURN name is empty for the same reason as event 6.

**Minimal repro, independent of `bump/0` entirely:** a direct `retract(counter(N)), M is N+1,
assertz(counter(M)), counter(C)` inside one clause body is sufficient; wrapping the retract/assertz in a
separate `bump/0` predicate first (the witness's own shape) reproduces identically at the second `bump`
call's *subsequent* `counter(C)` call, not at the second `bump` call itself in the smaller repro — the
common factor is **a call into a dynamic predicate whose clause list was mutated by `retract`+`assertz`
earlier in the same clause body**, not recursion depth or which predicate name is used.

## WHAT IS NOT THE CAUSE (ruled out this session)

- **Not oracle/monitor-side**: reproduces in bare `--trace`, no `monitor_run.sh`, no gpx participant.
- **Not the trace-name literal itself**: `counter/1`'s compiled box (`FN__counter$2F1` in the `--compile`
  `.s`) carries its own fixed `"counter/1"` / `"counter"` literals exactly like any other predicate; the
  literal is not per-call-site data and calling `counter/1` in isolation traces it correctly.
- **Not the double_quotes default change landed this session** (SCRIP, this row) — reproduces identically
  before and after that change; unrelated code paths (`unification.c` `plc_atom_op_text` /
  `by_name_dispatch.c` `pl_flags` are not on the trace-emission path at all).
- **Not the `PL_ATOM_OP_LEAF` / `rt_pl_atom_op_cell` string-ops path** — `retract`/`assertz`/`counter/1`
  never call into that code.

## WORKING HYPOTHESIS, NOT YET PROVEN

The symptom shape — an empty **name** on the CALL event immediately followed by a garbage **integer** on
the next STMT event — reads like two unrelated literal operands (a string-literal load feeding
`__trace_call`, and an integer-literal load feeding `__trace_stmt` on the very next goal) both drawing from
memory that a preceding `retract`/`assertz` **call** left in an unexpected state — i.e. a ζ-SPINE
depth/slot-reservation mismatch around the `$db_erase`/`$db_assertz_r`-family `IR_CALL` nodes, not a bug in
`pl_trace_named_wrap` or in `rt_trace_call`/`intern_name_bin` themselves (their C is straightforward and was
read in full this session). This is a hypothesis to verify with ASM-diff between `/tmp/probe_dyn_direct.pl`
and `/tmp/probe_dyn_after_assert.pl` `--compile` output around the `$db_erase`/`$db_assertz_r` call sites
and the following literal loads — not yet done; flagging the direction rather than guessing further.

## WHY THIS MATTERS BEYOND THE MONITOR WITNESS

This is a **correctness** bug in SCRIP's own trace/monitor instrumentation for a common, ordinary construct
(retract+assertz then re-read the same dynamic predicate — the standard "counter" idiom), independent of
whether anyone is running the sync-step monitor. It does not corrupt the *program's own answer* (both probe
files print the correct final value on stdout outside the `****` trace lines — monitor-safety's own
untraced-vs-traced-stdout check would not catch this because the corruption is confined to the `****` trace
lines it strips), but it means **no trace or monitor verdict is trustworthy for any Prolog program that
calls a dynamic predicate shortly after retracting/asserting into it**, which is exactly the shape of
witness 4's `bump`/`counter` idiom and is likely to recur across the INRIA/SWI/GNU boards' dynamic-database
families the moment the monitor is pointed at them.

## STATUS

Open. Not attempted as a cure this session (ASM-DIFF-FIRST per RULES.md needs the `.s` diff above before
touching `retract`/`assertz`'s call-site codegen or the ζ-depth bookkeeping around it — a guess-fix on
frame-slot allocation is exactly the class of change CEO-589 warns against landing blind). Folded into
`## NEXT` on the owning baton (`prolog-monitor-the-instrumented-gprolog-oracle-is-completed-and-used-...`)
in the same landing as this FINDING, per the standing rule that a FINDING's measured claims must not live
only in the file Lon periodically deletes.

Repro files this session (scratchpad, not corpus — mint as a corpus witness only if/when this becomes a
scored regression test): `/tmp/probe_dyn_direct.pl` (correct), `/tmp/probe_dyn_after_assert.pl` (corrupt),
`/tmp/probe_twice.pl` (the `bump`/`bump`/`counter` shape closest to the monitor witness).
