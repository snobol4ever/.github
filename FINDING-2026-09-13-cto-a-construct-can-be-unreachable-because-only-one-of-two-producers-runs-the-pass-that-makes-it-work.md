# FINDING — A CONSTRUCT CAN BE UNREACHABLE BECAUSE ONLY ONE OF TWO PRODUCERS RUNS THE PASS THAT MAKES IT WORK

cto, 2026-09-13, MODE NONET, lane PROLOG COMPLETENESS. Landed SCRIP `6a687c034`; row
`prolog-an-initialization-goal-containing-a-variable-hangs-the-compiler`; gate
`scripts/test_gate_pl_an_initialization_goal_may_contain_a_variable.sh`, wired into `make test` and adopted.

## THE DEFECT, WHICH IS ORDINARY, AND THE SHAPE, WHICH IS NOT

`:- initialization(a(_)).` did not run, did not fail and did not report. **The compiler itself looped**:
`scrip --compile` emitted without terminating, 2.5 MB of assembler and still growing when killed at 60s, and
mode 3 wires the same lowering in process and hung the same way, so the program never started. swipl runs the
identical file and prints the answer. ISO 7.4.2.4 gives `initialization/1` a GOAL, and a goal with variables
is the ordinary case, not an exotic one.

Three neighbouring forms all worked, and that is the whole diagnosis:

| form | result |
|---|---|
| `:- initialization(a(1)).` — ground | compiles, runs |
| `m :- a(_).` then `:- initialization(m).` — hoisted | compiles, runs |
| `:- a(_).` — plain directive, same variable | compiles, runs |
| `:- initialization(a(_)).` | **compiler loops** |

So the trigger is not the call, not the predicate, not the variable and not the directive. It is a variable
**arriving by one particular route**.

## THE MECHANISM

`lower_pl_stage2` (`src/lower/lower_prolog.c`) builds **ONE** top-level goal graph from **TWO** lists.
An ordinary directive is wrapped in `ignore`/`catch` and then passed through `pl_dir_number_vars`, which
assigns every variable its slot. An `initialization/1` goal was appended to `init_goals` **with no numbering
at all**. Both lists are then concatenated into the same `pl_body_graph`. A variable arriving by the second
route carried no slot, and the emitter never reached a fixed point.

The cure is one line: number it, in the same namespace with its own scope, exactly as the first route
already does.

## ⭐ THE GENERAL FORM

**A pass that is a precondition of a shared consumer must be run by the consumer, or by every producer — and
"every producer" is a fact nobody re-checks when a second producer is added.** The two lists here merge one
line before use, so the missing pass is invisible at the merge point and invisible at the consumer; it is
visible only by reading both producers and noticing that one of them does something the other does not. No
structural check asks that question, because both producers are individually well-formed.

This is the same shape as hq_U's `bb_bound` finding of the same evening from the other side: there, three
arms of one template were all present, paired and correctly wired, and the Prolog arm pointed at a different
resource than the other two — every structural check answered yes, and the only instrument that could see it
was a capacity measurement. Here, both producers are correct in isolation and the only instrument that could
see it was a program that hung. **When one template or one consumer serves several frontends, the question
no per-site check asks is which arm runs on the frontend you are standing on.**

## ⛔ THE COST WAS NOT THE CONSTRUCT — IT WAS THE SHAPE OF THE FAILURE

A hang in the compiler does not fail a case, it **stalls a runner**. A stalled runner is recorded as a
timeout, a flake or a skip, and every one of those reads as a property of the measurement rather than of the
engine. That is how an ordinary ISO construct stayed unreachable without appearing in any red column.

Consequently the gate's **timeout is part of the grade**: a bounded arm that does not answer is RED, never
`could-not-measure`. This is the one place I would refuse the usual instrument courtesy of degrading silence
to a refusal — for a defect whose signature IS silence, a refusal-on-silence gate can never fail.

The control arm is the ground and hoisted forms **in the same run**: if they ever stop answering, the subject
arm is measuring an engine that runs nothing, and would pass for the wrong reason.

## HOW IT WAS FOUND, WHICH IS NOT TO MY CREDIT

I was building the witness for a different row — one malformed clause abandoning the whole file — and the
witness would not run. The first, cheap, wrong move is to assume the witness is broken and rewrite it. It
took one bisection of four forms to establish the witness was correct and the engine was not. **A witness
that will not run is a measurement, not an obstacle**, and it is the only reason this defect has a row.
