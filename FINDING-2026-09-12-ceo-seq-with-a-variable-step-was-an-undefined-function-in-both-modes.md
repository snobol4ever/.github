# FINDING 2026-09-12 15:10 CDT (ceo) — seq() with a variable step was an undefined function in both modes

**Tree:** measured on SCRIP `b35ed8e2a`, cured `26bbc4c6f` · corpus `cb0301bb6` (the two IPL programs that exposed it, now graded) · seat ceo (lane ICON TO 100%) · cursor CEO-631.

## Measurement

Minting refs for IPL's `ipower` and `iseq` (`every i := seq(start, incr) \ limit do …`) read red in both modes:
`scrip: error 22: Undefined function called` at the `seq` line. Ablation: `seq(x, 1)` and `seq(1, 1)` answer 1 2; `seq(1, x)` raises 22.
`lower_seq` (`src/lower/lower_icon.c`) accepted only a constant step (`icn_const_step`) and returned NULL otherwise; `lower_call` then built
a generic by-name `IR_CALL` for "seq", and the runtime has no such function because Icon generators are compiled boxes, not calls —
so the miss surfaced as error 22 rather than as a wrong sequence.

## Cure

A variable step lowers as `i to (if j < 0 then INT64_MIN else INT64_MAX) by j`: a synthesized `TT_TO_BY` node (`ast_node_new`/`ast_push`,
the parser's own constructors) handed to `lower_to`, so the to-by box's sign-aware bound test (`bb_to_by.cpp`: `cmp rdx,0 / jl`) serves
both directions and every port is the one `to … by` already wires. Only a plain-variable step takes this path: a step that is an
arbitrary expression would be lowered twice (bound and step), so it still returns NULL and stays visibly red rather than double-evaluated.
No new global, no runtime discriminator, no template change.

## Proof

`test_gate_icn_seq_takes_a_variable_step.sh` — seven shapes (variable start, variable step, literal, one argument, NEGATIVE variable step,
both variable, omitted start), ref cut from icont at gate time, byte-identical in m3 and m4; `FAIL_ONCE=1` trips the diff arm (2 diff
lines per mode). Wired into `make test`. Control arms: `test_gate_emit_no_lang.sh` green, `test_smoke_icon.sh` 15/15 both modes,
`make preflight` 33/0; ipower and iseq PASS/PASS inside the IPL runner's isolation. The Icon master re-read is the coo's/Lon's board pass.

## Left standing, named

`fileprnt` (corpus `cb0301bb6`, a VISIBLE red): `error 103: string expected` at line 72, `&null || "|"` — an `@ascgen` that should fail
yields `&null`; the minimal exhausted-co-expression witnesses (2-way and 33-way alternations, inside a block, table assignment) all pass,
so the shape is narrower than "exhausted co-expression" and is the next ablation.
