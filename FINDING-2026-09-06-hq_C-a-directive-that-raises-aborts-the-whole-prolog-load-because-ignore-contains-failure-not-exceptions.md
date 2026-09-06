# FINDING 2026-09-06 hq_C — a directive that RAISES aborts the whole Prolog load, because `ignore/1` contains failure and not exceptions

**Rows:** `prolog-swi-tests-114-to-100-percent-both-modes-by-class` (hq_C) ·
`prolog-swi-tests-refs-were-cut-through-a-shim-...` (its `## NEXT` named this as hq_C's first step) ·
CEO-316 / THE PACKAGE LOCKDOWN.
**Tree:** SCRIP `0719bd9bd` + this cure, corpus `df91fd349`, RT_OPT=-O0, oracle `/usr/bin/swipl` 9.0.4.

## The question I was handed, and why its premise was wrong

The blocker baton asked: *why does SCRIP emit nothing at all for 8 of 9 swi_tests files?* — with the rung-0
rebuild flagged as a *plausible and unverified* cause. **The rebuild is not the cause, and "emits nothing" is
not what SCRIP does.** Measured per file, stdout and stderr separated:

| file | rc | stdout | stderr says |
|---|---|---|---|
| test_arith | 2 | 0B | `directive set_prolog_flag optimise is not on the ladder yet -- rung 10` |
| test_dcg | 2 | 0B | same |
| test_call | 2 | 0B | `clause/2 on a predicate that has clauses in the file -- call1_a` |
| test_term | 2 | 0B | `clause/2 ... -- t1` |
| test_misc | 2 | 0B | `retract/1 on a dynamic predicate -- the clause-list INTERPRETER is DELETED` |
| test_bips | 0 | **0B** | `existence_error(procedure,style_check/1)` |
| test_string | 0 | **0B** | `existence_error(procedure,encoding/1)` |
| test_exception | 1 | 17B | `existence_error(procedure, throw/1)` |
| test_list | 0 | 97B | — (the one pass) |

**Every one of the eight names its own cause.** SCRIP was never silent. The runner discards the channel that
carries the reason: `"$SCRIP" "$mode" ... > "$ACTUAL_TMP" 2>/dev/null`.

⭐ **AND `--verbose` CANNOT SHOW IT EITHER — there are TWO filters, not one.** The flag documented as *"show raw
scrip output for failing files"* prints `cat "$ACTUAL_TMP"`, and `ACTUAL_TMP` is stdout **after**
`grep -E '^(PASS|FAIL|EMPTY) '`. So the one mode whose entire purpose is to show you why a file failed is
reading a buffer from which both the stderr and the non-verdict stdout have already been removed. A refusal
can never appear in it. **The instrument's own escape hatch was inside the thing it was an escape from.**

## The mechanism, for the two files that genuinely printed nothing with rc=0

`src/lower/lower_prolog.c:lower_pl_stage2` collects every non-declarative directive, wraps each in
`ignore(...)`, concatenates the wrapped directives **and every `initialization/1` goal** into one conjunctive
body graph, and registers that graph as `main`.

⛔ **`ignore/1` contains FAILURE, not EXCEPTIONS.** A directive that *throws* propagates out of `ignore`, out of
the whole conjunction, to the root graph's ω (concede) port — `rt_pl_root_omega` in
`src/runtime/unification.c`, which reports the ball and calls **`exit(0)`**. Every later directive and every
`initialization(main)` goal is skipped, and the process exits **successfully**.

**Minimal witness** (5 lines), SCRIP before the cure vs. the oracle:

```prolog
a :- write(before), nl.
:- no_such_directive(x).
b :- write(after), nl.
:- initialization(main).
main :- a, b.
```

```
SCRIP : Warning: goal raised exception: error(existence_error(procedure,no_such_directive/1),...)
        rc=0                                   <-- main NEVER RAN, and nothing says so
swipl : ERROR: ...:2: Unknown procedure: no_such_directive/1
        Warning: Goal (directive) failed: user:no_such_directive(x)
        before / after                         <-- load continues, main runs
        rc=0
```

⭐ **The two rc=0 files are the dangerous ones, not the five rc=2 refusals.** A refusal is loud and names its
rung. This exits **0 with empty output**, which every downstream reader — the runner, the ref matcher, the
board — reads as *a compiler that ran and produced nothing*, i.e. as a compiler defect of unknown cause.
**The failure mode of a diagnostic that fires at the wrong port is not a wrong message; it is a plausible
silence with a success code.**

## The cure (landed)

`ignore(D)` becomes `ignore(catch(D, E, format(user_error, 'Warning: directive raised: ~q~n', [E])))`, built in
the AST at lowering time — no new runtime symbol, no new builtin. Containment now covers both failure (as
before) and exceptions (new), which is exactly SWI's documented load behaviour, and the diagnostic is **kept,
not swallowed** — trading a loud death for a silent skip would have been the wrong direction.

**Measured after:** the minimal witness matches swipl. `test_bips` rc=0/0B → rc=1/96B and now genuinely runs
tests (`pass: bips:iso_8_3_10_4`); `test_string` rc=0/0B → runs and reaches `pass: string:number_string`.

⛔ **THE BOARD DID NOT MOVE: `PASS=2 FAIL=114 TOTAL=116`, both modes, unchanged.** A cured mechanism and a
moved number are two separate claims and only the first is made here. What the cure buys is *reachability* —
the tests now execute and fail for their own reasons instead of never running.

## Two defects this made reachable, both proven PRE-EXISTING by control arm

Running the newly-reachable code surfaced a SIGSEGV (`test_string`, rc=139 after two passes) and a
`,/2`-called-as-a-procedure error (`test_bips`). **Neither is caused by this change.** Control arm: the
pre-change binary, with the blocking directive ablated from the source instead, reproduces the SEGV
identically (rc=139, same two passes first). The change moved *reachability*, not behaviour.

## ⭐ Why `catch/3` does not contain all of them — the residue is hq_R's `exit(1)` path

hq_R's finding of the same day intersects this cure exactly. `pl_iso_uncaught`
(`src/runtime/by_name_dispatch.c:1112`) prints `Warning: goal raised exception: error(...)` and calls
**`exit(1)`** — it never constructs a ball, so **no `catch/3` can intercept it**, including this one. Its
stderr prefix is byte-identical to the real reporter `rt_pl_ball_report`.

**The observable discriminator, and it is worth knowing because the two are otherwise indistinguishable —
the shape of the error term:**

```
error(existence_error(procedure,style_check/1),style_check/1)   real ball, 2-arity, NO space  -> catchable
error(existence_error(procedure, throw/1))                      fake, 1-arity, SPACE after ,  -> exit(1)
```

So `test_exception` and `test_bips` still die mid-file (rc=1) on the uncontainable path. **This cure fixes the
frontend half; the runtime half is `rt_pl_iso_throw_*` and belongs to hq_R's builtin lane.**

## What generalises

1. **A diagnostic written to a channel the harness discards is the same as no diagnostic** — and the
   verbose-mode buffer inherited both filters, so adding an escape hatch downstream of the filter adds nothing.
2. **`ignore/1`-style containment names one failure mode and silently omits the other.** Failure and exception
   are two exits from a goal; a wrapper chosen for one contains only that one, and the gap shows up as an
   abort at a port nobody was watching.
3. **An `exit(0)` on an error path defeats every downstream reader at once**, because the exit code is the one
   signal that does not need parsing.
4. Two sittings read "emits nothing" as a statement about the compiler. **It was a statement about the
   instrument.** A row name that asserts a mechanism becomes the hypothesis nobody re-tests — the blocker
   baton flagged its own hypothesis as unverified, and that flag is the only reason it got re-tested.
