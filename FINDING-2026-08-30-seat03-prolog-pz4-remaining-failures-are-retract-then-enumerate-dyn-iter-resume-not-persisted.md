# FINDING 2026-08-30 seat03 — PZ-4's remaining rung14/rung15 failures are ALL "retract, then enumerate the SAME predicate via backtracking" — isolated to the by-name `"$dyn_iter"` generic dispatch, whose `resume` slot does not persist across a retry. NOT proven to be the same mechanism as this row's steps (a)-(f); may need its own, narrower fix.

## CONTEXT
Resumed `prolog-pz4-gamma-retain-activation-frames` via `next`'s dependency-inversion promotion (it directly blocks `prolog-multiclause-uninit-lexprep-frame`). seat11's immediately-prior pass (2026-08-30, current `## NEXT` at claim time) found the row's decade-long blocking dependency (`icon-n2-generator-activation-frames`) had finally landed DONE, and that as a side effect **rung13 is now 5/5 PASS with `SCRIP_PL_GAMMA_RETAIN` still default OFF**. They flagged rung14/15's remaining failures as sharing rung14's "stops after first solution" signature but said the other rung14/15 witnesses were "not individually re-verified this pass, flagging as the concrete next check." This FINDING is that check, taken further.

## CORRECTED FLOOR (verified fresh against a clean build, HEAD `d403c283`)
Using the harness's own comparison method (`corpus_suite_harness.py` `.rstrip("\n")`s both sides — a raw `diff` against the checked-in `.expected` files is misleading because those fixtures lack a final newline the programs correctly emit; three witnesses below look like MISMATCH under raw `diff` but are real PASSes):

- **rung13: 5/5 PASS** — confirms seat11.
- **rung14: 0/2 PASS.** Both `retract_retract_basic` and `retract_retract_mixed` fail with the IDENTICAL signature: expected two lines (the remaining facts after one `retract`), got only the first.
- **rung15: 3/4 PASS**, not "the two named fails" as carried forward unverified — only `abolish_then_reassert` fails (same signature as rung14's two). `abolish_existing`, `abolish_one_of_two`, `abolish_then_query_fail` all correctly PASS today.

Combined corrected floor: **8/11** on the three rungs' backtrack/mutation witnesses, up from the documented original (`rung13 0/5 · rung14 2/5(ish) · rung15 1/5`). The remaining 3 failures are not three different problems — they are one signature, three witnesses.

## ISOLATED MECHANISM — minimal, corpus-free, 3-way controlled repro
```prolog
% testA_plain.pl -- no retract at all
:- assertz(f(a)). :- assertz(f(b)). :- assertz(f(c)).
main :- f(X), write(X), nl, fail.
main.
% -> a b c   (CORRECT)

% testB_retract_same.pl -- retract ON THE SAME predicate, then enumerate it
:- assertz(f(a)). :- assertz(f(b)). :- assertz(f(c)).
main :- retract(f(a)), f(X), write(X), nl, fail.
main.
% -> b        (WRONG -- swipl: b c)

% testC_retract_other.pl -- retract a DIFFERENT predicate, then enumerate the untouched one
:- assertz(f(a)). :- assertz(f(b)). :- assertz(f(c)). :- assertz(g(z)).
main :- retract(g(z)), f(X), write(X), nl, fail.
main.
% -> a b c   (CORRECT)
```
This cleanly rules out "any retract before any enumeration" (testC is fine) and "enumeration itself is broken" (testA is fine). **The defect requires retract to touch the exact predicate that is then multiply-enumerated in the same clause body.**

## ASM-DIFF-FIRST: testA and testB do not even take the same compiled path
`--compile` both witnesses and grepped the emitted `.s`:
- **testA's `f(X)`** compiles through `call_proc_staged` (`.Lcall_proc_staged_α_47_7`) — the ordinary, direct, staged-clause-call BB path used for any predicate the compiler can prove is never mutated on a path reaching this call. This is the SAME family of call site `pascal-m4-site1`/`bcps_spine_gen_arm` and this row's own steps (a)-(f) all target.
- **testB's `f(X)`** compiles through a completely different mechanism: a generic by-name builtin-generator call, `.Lcall_builtin_gen_α_..."$dyn_iter"`, resolved at runtime by `by_name_dispatch.c` to `rt_pl_dyn_iter_gen()` (`src/runtime/unification.c:1481`). `prolog_lower.c` reclassifies `f` as genuinely dynamic (not staged-static) the moment `retract(f(...))` is reachable in the same predicate, and routes every call to `f` through this generic runtime dispatch instead.

**This is the load-bearing fact for anyone designing a fix: the 3 remaining failures do not exercise the staged-call / `zframe_graph` mechanism steps (a)-(f) describe at all.** They exercise a separate, generic, name-resolved dispatch trampoline.

## RUNTIME TRACE — the `resume` slot does not survive the retry
Added temporary instrumentation to `rt_pl_dyn_iter_gen` and `rt_pl_dyn_retract_cell` (reverted before finishing, never committed — diff was reviewed clean via `git diff`/`git checkout --` before moving on). Running `testB_retract_same.pl`:
```
retract_cell: retracted='a', new_head -> 'b'
dyn_iter_gen ENTRY  *resume=0                          <- call 1 (fresh)
dyn_iter_gen INIT   it=0x...650  it->cur='b'
dyn_iter_gen LOOP   it->cur='b'                          -> prints "b", correctly advances it->cur to 'c'
dyn_iter_gen ENTRY  *resume=0                          <- call 2 (the retry after `fail`) -- SHOULD be the pointer to it=0x...650, is NOT
dyn_iter_gen INIT   it=0x...6a0  it->cur='b'              <- re-initializes from scratch, brand-new `it`, same starting clause
dyn_iter_gen LOOP   it->cur='b'
dyn_iter_gen ENTRY  *resume=129416210458272            <- call 3: NOW resume correctly carries call-2's `it` pointer...
dyn_iter_gen LOOP   it->cur='c'                           <- ...but no success was ever produced for 'b' the second time, and 'c' is never tried either -- program ends here, "b" printed once total
```
**The concrete bug: on the retry call (call 2), the caller passes `*resume == 0` instead of the value written by call 1.** The generator has no way to tell "this is a fresh top-level call" from "this is a retry whose resume slot got reset/lost," so it silently restarts. Exactly what happens between call 2 and call 3 (why the second 'b' attempt produces no output before `it->cur` has already advanced to 'c') was not traced further — flagged as the concrete next step, not chased this pass.

## WHY THIS WAS NOT ATTEMPTED HERE
Two independent reasons this stops at characterization:
1. **It is not proven this belongs to steps (a)-(f) at all.** Those steps (per this row's own GOAL and hq_C's matrix) describe the direct staged-call / `zframe_graph` prologue-pin mechanism. The by-name `"$dyn_iter"` trampoline (`call_builtin_gen_α`, `by_name_dispatch.c`) is a structurally different call site with its own args-passing and resume-threading convention — implementing (a)-(f) perfectly might not touch this path at all. Whoever has full context on how `call_builtin_gen_α`'s resume slot is supposed to be carried across a retry (is it a stack slot, a wired register, a BB-local per `ARCH-PROLOG-DESCR-ZETAS-hq_C.md` §5?) is better positioned to say whether this is the SAME shared mechanism wearing a different call shape, or a separate, local defect in the by-name trampoline alone.
2. Same standing discipline every predecessor on this row has kept: this touches shared calling-convention code reachable from every by-name generic-generator call (`"$dyn_iter"`, and structurally probably its siblings `"$dyn_assertz"`/`"$dyn_asserta"`/`"$call"` — not checked whether they share the same resume-threading code), not a locally-scoped one-clause fix — a wrong patch here risks the same class of regression this row's own history (hq_C's SNOBOL4-backtrack `op_zres` near-miss, seat12's genqueen root-cause-2) has repeatedly warned about.

## NEXT ACTOR
1. **Find where `call_builtin_gen_α`'s `resume` argument is stored between the initial call and the retry** (grep `bb_call_write_slot.cpp`/`bb_call_fn.cpp`/wherever "$dyn_iter"-shaped generic generator calls get their retry wiring — not yet located) and gdb/ASM-diff exactly why it reads back 0 specifically when the SAME clause body also calls `retract` on the enumerated predicate first. Strong candidate class per this row's own culture: a fixed-offset/shared-slot collision, same shape as `zd_omega_head`'s sibling row (`zd-omega-head-per-op-filter-...`) and PZ-4's own original four convergence FINDINGs — but NOT verified to be literally the same mechanism, don't assume.
2. **Answer the open question above** (is this in scope for steps a-f, or separate) before attempting any fix — it changes what "done" looks like for this row.
3. rung13/14/15's own gate scripts (`test_prolog_rung13/14/15.sh`) are confirmed stale (seat11) — they grade a per-family suite file `tests-consolidate-prolog`'s flattening has already absorbed into `ALL.pl`, so they silently report `PASS=0 FAIL=0 rc=0`. That repoint is `tests-consolidate-prolog`'s own lane (hq_B), not this row's — flagging, not fixing, matching established precedent.
4. Full corrected floor for whoever verifies next, name-for-name: rung13 5/5 · rung14 0/2 · rung15 3/4 (`abolish_then_reassert` only). `SCRIP_PL_GAMMA_RETAIN` flag flip still not attempted, and per point 1 above it's no longer obviously the right lever for these specific 3 remaining failures.

No SCRIP source changed (debug instrumentation added and reverted this pass, confirmed via `git diff`/`git status` clean before moving on). No corpus/.github source changed besides this FINDING.
