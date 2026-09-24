# FINDING 2026-09-24 hq_snocone -- the monitor wires a SNOBOL4 variable whose name begins with `@` or `%` as a Raku ARRAY or HASH, so the first lock-step run of a bootstrap parser diverges on a plain string

**Measured by hq_snocone on SCRIP at the head of the trace-row landings (the non-slim call protocol cure, the intern-table
root), corpus `e37f7e483`, RT_OPT=-O0, incremental `make`; the harness `test_monitor_3way_sync_step_auto.sh`, participants
`spl scr`, on the transpiled `parser_rebus.sno` with `corpus/benchmarks/rebus/arith_loop.reb` on stdin.**

With tracing no longer changing a match result and the monitor's interned names rooted, the SPITBOL fork and SCRIP run the
Rebus parser in lock-step for 2593 steps (AGREE=2315, UNGRADED=277 -- every PATTERN and TABLE value the fork sends untyped)
and diverge exactly here:

```
| step | stno | spl                             | scr                             | source                                        |
| 2592 | 235  | LABEL stno=INT=235              | LABEL stno=INT=235              | parser_rebus.sno:237  InitStack (($'@S') = '') |
| 2593 | 235  | @235 VALUE @S = STRING(0)=''    | @235 VALUE @S = ARRAY           | parser_rebus.sno:237  InitStack (($'@S') = '') |
```

The program assigns the null string to the variable whose name is `@S` (`$'@S' = ''`, the bootstrap library's semantic stack
head; `#N`, `@B` and `@E` are its siblings). SPITBOL's fork wires the value as it is, a STRING of length 0. SCRIP's
`rt_trace_value` (src/runtime/core/core.c) rewrites the wire type by the NAME's first character:

```
if ((name[0] == '@' || name[0] == '%') && (val.v == DT_S || val.v == DT_SNUL)) wire.v = (name[0] == '@') ? DT_A : DT_T;
```

That rule exists for Raku, whose arrays and hashes are strings with 0x01 separators inside SCRIP and Array/Hash objects inside
the Rakudo fork, so the type must be lifted to agree with `rkx`. Against `spl` it turns a SNOBOL4 string into a false ARRAY.
Every bootstrap parser assigns to `$'@S'` in InitStack, so every parser's lock-step run will diverge at this row before its
grammar runs at all.

**What this is not.** Not a parser defect and not a SCRIP semantics defect: the untraced runs print the same tree, and the
step-2593 value is the right one on both sides. It is the instrument's type-lifting rule applied to a language whose oracle
does not lift.

**Where it goes.** The monitor's binary protocol is the ceo's coordination (CEO-1186); the rule needs to know which oracle it
faces or which language produced the variable, and both are the ceo's design choices (MONITOR-BINARY-DESIGN.md § THE PLUG
INTERFACE). Candidates, for the ceo to choose: lift only when the participant set names `rkx`; or lift only when the string
carries the Raku list encoding (which cannot tell an empty list from an empty string); or have the Raku lowerer mark its
sigil variables so the runtime need not read sigils off names. Until it is ruled, `monitor_run.sh parser_<lang>.sno --oracle`
reads DIVERGE rc=1 at this row for every bootstrap parser, and the assigned row's DONE-WHEN cannot read green by any change
inside hq_snocone's lane.

**Two neighbours found on the same road, both the ceo's instrument:** (1) the harness runs its `scr` participants with
`SCRIP_TRACE=${SCRIP_TRACE:-99999}`, a FINITE budget; when it runs out mid-program, EVALs compiled afterwards are compiled
untraced inside a traced program and their deferred user calls die of error 22 (the mixed state; witness: any parser on a
program with more than 99999 trace events, and ta4 in FINDING-2026-09-24-hq_snocone-tracing-changes-a-match-result-...);
(2) a mode-4 binary compiled with `--trace` but run without a runtime budget is the same mixed state the other way round
(the gate `test_gate_sno_tracing_does_not_change_a_match_result.sh` therefore runs its traced mode-4 binaries with the
budget set, as the harness does).
