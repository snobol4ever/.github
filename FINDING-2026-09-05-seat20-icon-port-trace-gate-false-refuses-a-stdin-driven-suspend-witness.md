# FINDING 2026-09-05 seat20 — Icon port-trace gate false-refuses a stdin-driven suspend witness (class gap, not a compiler defect)

Row `fuzz-crash-class-and-port-trace-refs-over-the-three-open-languages` (hq_U task, FLEET-20). While
running this row's own DONE-WHEN chain (`test_gate_sno_port_trace_oracle_diff.sh` &&
`test_gate_pl_port_trace_oracle_diff.sh` && `test_gate_icn_port_trace.sh`) end to end, the third leg —
pre-existing, untouched by this row — came back UNPROVEN(2):

```
GATE UNPROVEN(2) [test_gate_icn_port_trace]: rung36_jcon_recogn__rung36_jcon_recogn m3: source contains
'suspend' but SCRIP_PL_TRACE=1 produced ZERO proc_gen lines -- the instrument is not firing, this is not
'no ports'
```

Reproduced twice (`--only 36`, isolated from the chain). Not a load artifact (system load was ~37 on 16
cores both times, but the failure mode is a clean zero-count refusal, not a timeout/rc=124).

## Root cause (ablated)

`corpus/tests/icon/ALL.csv` origin `rung36_jcon_recogn__rung36_jcon_recogn` extracts to a CFL-recognizer
program (`refs/jcon-master`-style demo, "V9SAM"):

```icon
procedure main()
   local line;
   while line := read() do
      if recogn(s,line) then write("accepted") else write("rejected");
end
procedure recogn(goal,text)
   return text ? (goal() & pos(0));
end
procedure s()
   suspend (="a" || s()) | (t() || ="b") | ="c";
end
procedure t()
   suspend (="d" || s() || ="d") | ="e" | ="f";
end
```

`main`'s entire body is gated on `read()` inside the `while` loop. `test_gate_icn_port_trace.sh` (via
`lib_gate.sh`'s shared witness-running shape) always runs a witness with `</dev/null`. With no stdin,
`read()` hits EOF on its very first call and the loop body — the only code path that ever calls `s`/`t`,
the actual `suspend`-containing procedures — never executes. Confirmed directly:

```
$ SCRIP_PL_TRACE=1 ./scrip rung36.icn </dev/null 2>&1 >/dev/null
(1) 0 Call: n0_call_icon read
(1) 0 Fail: n0_call_icon read -> pat_flat_ω r15=...
```

One `read` call, one `Fail`, nothing else. Zero `proc_gen` lines is the semantically CORRECT trace for
this witness under empty stdin — the gate's population filter (any origin whose extracted source
contains the literal token `suspend`) is right that this witness's code CONTAINS suspend, but the
gate's own fixed `</dev/null` invocation makes that code unreachable for this particular family of
witness. The gate's own refusal text ("the instrument is not firing, this is not 'no ports'") is the
correct response to the wrong diagnosis here: the instrument fired exactly once and correctly reported
the only thing that happened.

## Class, not a one-off

Any future Icon `suspend`-containing witness whose suspend path is reached only via stdin content (a
`read()`-driven recognizer/filter, the natural shape for corpus programs ported from real Icon programs
like the Arizona/`jcon-master` suites this origin's name suggests it came from) will hit the identical
false UNPROVEN(2), not because SCRIP regressed but because the gate never looks at `corpus/tests/icon/
ALL.in` (the per-entry stdin-fixture file the master-suite ANSWER grading already consults) before
deciding a witness is "suspend-reachable". `rung36_jcon_recogn` is the first witness in the `suspend`
population to actually need stdin; every earlier rung03-era witness this gate was built and proven
against is self-contained.

## Disposition (witnesses-only lane, not cured here)

This is `test_gate_icn_port_trace.sh` / Icon-lane territory (hq_B), not this row's SNOBOL4/Prolog
oracle-diff work, and per this row's own brief ("witnesses only, never compiler fixes") no fix is
attempted here — fixing it means teaching the gate to feed each origin's `ALL.in` fixture (when one
exists) instead of a blanket `</dev/null`, which is a real but separate change to a shared instrument
other suites also rely on. Filed so the row's DONE-WHEN state is honestly explained: the SNOBOL4 and
Prolog legs below are GREEN and were built/verified by this row; the Icon leg's non-green result on this
tree is this pre-existing, class-scoped gap, not a regression this row introduced or a defect in SCRIP
itself. `--to 35` (excluding rung 36) passes clean if a caller needs a green Icon leg today without
waiting on the fix.

## Receipts

- `bash SCRIP/scripts/test_gate_icn_port_trace.sh --only 36` → UNPROVEN(2), reproduced twice, 2026-09-05.
- `bash SCRIP/scripts/test_gate_icn_port_trace.sh --to 35` → PASS(0) (excludes the affected rung).
- tree: SCRIP=674319235 corpus=4e11cb9ee .github=d5b2c325b (at time of measurement).
