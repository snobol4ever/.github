# FINDING 2026-09-06 hq_C — the Prolog meta-call bridge SIGSEGVs whenever the meta-called goal FAILS

**Rows:** `prolog-meta-call-bridge-does-not-reach-builtins-or-operators` (hq_C, QUEUE 308) ·
`prolog-swi-tests-114-to-100-percent-both-modes-by-class` · hq_R's `test_string` SEGV.
**Tree:** SCRIP `5fb318258` and later, **unmodified**. corpus `df91fd349`. Oracle `/usr/bin/swipl` 9.0.4.

## The claim

A goal reached through a variable — `call/1`, `call/N`, `catch/3`'s Goal, `findall/3`'s Goal, plunit's per-test
invocation — **crashes the process when it FAILS**. Not when it is missing. When it *fails*, which is an
ordinary, correct Prolog outcome.

```prolog
no :- fail.
:- initialization(main).
main :- ( X = no, call(X) ; write(elsepath) ), nl.
```

```
swipl : elsepath           rc=0
SCRIP : <SIGSEGV>          rc=139
```

**No builtin, no control construct, no wrapper, no shim.** A user predicate defined in the same file, reached
by `call/1`, that fails. A *succeeding* meta-call to the same predicate is fine (`X = yes, call(X)` prints
`ok`, rc=0), so the success path works and **the ω (concede) path is the broken one**.

## Why this was not the row's headline, and why it should be

Row 308 is named *"does not reach builtins or operators"*, and that half is real and independently confirmed:
`X = write(a), call(X)` raises `existence_error(procedure, write/1)` while `X = foo(Y), call(X)` against a
clause in the file is green — the bridge reaches the clause database and not the builtin table
(`rt_pl_goal_gen_h` gates on `rt_proc_is_registered`, and a builtin is a compile-time lowering rule, never a
callable runtime entity).

⭐ **But the MISS half masks the FAILURE half, and the masking is total.** Every witness anyone had reached the
bridge with a name it could not resolve, so every witness stopped at `existence_error` **before** the ω path
was ever exercised. The failure path can only be observed with a goal the bridge *can* resolve and that then
*fails* — i.e. a user predicate — which is exactly the case nobody probed, because that case was believed
green. **The class that was already broken hid the class that was worse.**

## How it was found — and the cure that had to be thrown away to find it

Prototyping the ruled cure for the miss half (synthesize and register a wrapper proc per meta-callable name,
reusing the machinery `lower_pl_stage2` already uses for dynamic predicates) made control constructs resolve:
`X = (p,q), call(X)` printed `ab`, `X = (yes->p), call(X)` printed `a`. **Then the gate's failure arms
SIGSEGVed** — `(no->p;q)`, and `(no,p)` with a failing first conjunct.

⛔ **The first reading was that the wrappers were buggy. The control arm says otherwise:** the same witness
crashes identically on the **unmodified** binary once the goal is a plain user predicate. The wrappers were
never the cause; they had removed the `existence_error` that was stopping execution before the crash site.
**Third instance of the same shape on this seat today** — the directive cure, the ref-cutter denominator, and
now this: *removing an early, loud failure is how you discover the quiet one behind it.*

⭐ **Two witnesses that looked green and were not, both mine, both from testing only the success branch:**
`,/2` "works" (tested `(p,q)`, never a failing conjunct) and `->/2` "works" (tested a true condition, never a
false one). A control construct has two exits and I graded one. **Any witness for a control construct that
does not exercise the failing branch has tested half the construct and reports the half that passed.**

## Consequence: the cure ORDER is forced

The wrapper synthesis is **proven and deliberately NOT landed**, because landing it would convert a clean
`existence_error(procedure, ,/2)` into a **SIGSEGV** for every program that meta-calls a control construct. A
crash is worse than an error even when the error is also wrong.

**Order: cure the ω path first, then register the wrappers.** This is the same argument this seat made to hq_R
hours earlier about their `exit(1)` residue — *a dispatcher landed before the error path is sound moves the
error without making it recoverable* — and it now applies to this seat's own cure. The gate
`test_gate_pl_meta_call_reaches_control_constructs.sh` is landed as the row's named acceptance gate, **expected
RED, deliberately not in `make test`**, with its failure arms written so a success-only cure cannot pass it.

## What it explains

- **hq_R's `test_string` SEGV**, which they measured as surviving their `number_string` cure and declined to
  row as theirs. It is downstream of this. They narrowed it to *the first test in a plunit unit runs and every
  subsequent body dies on the meta-call bridge* — plunit invokes each test body through a meta-call, and a
  test that **fails** is the normal case in a conformance suite.
- Why the swi board sits at `PASS=2 FAIL=114`: this is upstream of it.
- ⛔ **A conformance suite is the worst possible place for this defect**, because a suite's job is to run goals
  that fail. The bug is invisible in code that works and fires on the code written to check that it does.

## Related, found alongside and NOT the same defect

`X = !, call(X)` raises `existence_error(procedure, ?/0)` — a meta-called cut is keyed as `?/0`. Pre-existing,
reproduces with no wrapper involved, swipl prints `ok`. Recorded on row 308; not the ω-path crash.
