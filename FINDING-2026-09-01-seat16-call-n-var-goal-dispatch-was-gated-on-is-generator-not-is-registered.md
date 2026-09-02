# FINDING 2026-09-01 (seat16) — call/N and catch/3's var-goal path silently dropped every DETERMINISTIC user predicate; fixed with a one-line gate correction, not a rewrite

Row: `prolog-var-goal-dispatch-through-catch-call-silently-fails`. Tree: SCRIP `3c048661d` + this cure. RT_OPT `-O0`. Independent of the PZ-4/generator-resume family (confirmed again this session: the fix and every witness below are deterministic, no backtracking, no SUSPEND/generator machinery touched).

## Correction to the minted GOAL: two mechanisms, not one

The task's GOAL read *"Two witnesses, same shape, likely one mechanism."* Eight-witness bisection (table below) shows that's half right: they share a symptom (silent failure through a meta-call) but not a cause.

| witness | shape | before | after |
|---|---|---|---|
| `catch(G,_,fail)`, `G` bound via `=` to `double(21,R)` | goal via variable | FAIL (silent) | **PASS (42)** |
| `catch(double(21,R),_,fail)` — same goal, written directly | direct compound | PASS (42) already | unchanged |
| `call(add,3,4,R)` — `add` a **direct literal** atom, not a variable | direct, no indirection at all | **FAIL (silent)** | **PASS (7)** |
| `G=add, call(G,3,4,R)` | goal via variable | FAIL (silent) | **PASS (7)** |
| `call(double(21,R))` — call/1, direct literal compound | direct, no indirection | **FAIL (silent)** | **PASS (42)** |
| `call(inc,5,R)` — call/2, direct literal atom | direct, no indirection | **FAIL (silent)** | **PASS (6)** |
| `call(twoclause,X,Y)` — **multi-clause** user predicate via call/N | direct | PASS (a-1) already | unchanged |
| `call(write(hello))`, `call(is(R,21*2))` — builtins via call/1 | direct | PASS already | unchanged |

**catch/3's bug is genuinely about variable indirection** (direct compound goals already dispatched correctly). **call/N's bug has nothing to do with variables at all** — it failed for a *directly written* `call(add,3,4,R)` exactly as it failed for the variable-indirected form, and only for **deterministic** (single-clause) user predicates; a multi-clause one (`twoclause/2`) already worked. Both mechanisms bottom out in the same function, which is why they read as one shape from the outside.

## Root cause

Both `call/N` (`by_name_dispatch.c:4542`, builds a `PLCK_META` node) and a var-bound goal reaching `plc_build` (`:4557`) end up in `plc_build_resolved`'s fallback, which is the ONLY place that dispatches to a *runtime-resolved* (not statically known at lowering time) user predicate:
```c
if (rt_proc_is_generator(pib)) { plc_slv_t *s = plc_new(PLCK_PRED, cut); s->pi = strdup(pib); ... return s; }
rt_pl_iso_throw_pi("existence_error", "procedure", nm, n);
```
`rt_proc_is_generator` (`rt.c:713`) answers a narrower question than the one being asked: it returns the compiled procedure's `is_generator` flag — true only for predicates that need the SUSPEND/coroutine calling convention (multi-clause, or otherwise choice-point-bearing). A single-clause deterministic predicate is fully compiled and registered (`rt_proc_is_registered` is true) but `is_generator` is false, so the gate silently refused to build a `PLCK_PRED` node for it at all and fell straight through to `existence_error` — for a predicate that unquestionably exists.

**The callee this gate protects, `rt_proc_call_gen_h` (`rt.c:1098`), already handles both cases correctly** — it branches internally on `p->jmp_entry && p->is_generator` (coroutine path), `p->jmp_entry` alone, and a third plain frame-allocate-and-call path for everything else, reading the result back from the frame exactly as an ordinary deterministic call would. Redo through the same mechanism (`rt_proc_resume_frame_h`, `rt.c:1159`) is equally general: it looks up a coexpr generator by frame address, and falls through to the ordinary `fn(fb, 1)` β-port call otherwise, which a deterministic predicate answers with a clean FAIL. Nothing downstream of the gate assumes `is_generator`; the gate is simply asking the wrong question.

**The fix** (`by_name_dispatch.c:4552`): `rt_proc_is_generator(pib)` → `rt_proc_is_registered(pib)`. One line, no new globals, no signature change. Verified safe by construction (the callee already handles the non-generator case) and empirically (redo-through-call/N on a deterministic predicate was tested explicitly — see below).

## Verification

- Both minted witnesses (`call_directive_replace_4` / `catch_functor_directive_replace_1`, extracted from `corpus/tests/prolog/ALL.{pl,ref}` via `lib_master_extract.sh`): mode-3 **and** mode-4 print `7` / `42` respectively, byte-exact against `swipl -q -g halt` (matching the DONE-WHEN's own "taker cuts at claim" text).
- Eight-witness table above: every previously-failing case now passes; every previously-passing case (direct catch, builtins via call/1, multi-clause via call/N, a plain direct predicate call with no call/N at all) is unchanged.
- New witness, not in the original set: `call(add,3,4,R), write(R), nl, fail.` followed by a second `main` clause — the deterministic predicate correctly reports no second solution on redo (β-port FAIL), confirming the shared `rt_proc_call_gen_h`/`rt_proc_resume_frame_h` path is safe for the deterministic case in both directions, not just the forward call.
- `test_smoke_prolog.sh` 5/5 all three columns (m2/m3/m4). `test_prolog_rung_suite.sh`: PASS=4 FAIL=11 both modes — **unchanged from the measured baseline** (these 11 reds are a different, already-tracked population; this fix does not move that needle, nor should it — none of the 15 rung programs round-trip a runtime-resolved deterministic goal through `plc_build_resolved`).
- SNOBOL4 blocking floor (`make test`, run detached per the standing fleet-load recipe, loadavg ~12 at launch): pending at FINDING-write time, appended below once it lands.

## An unrelated, pre-existing defect surfaced by testing, NOT fixed here

Bisecting witness R (`call(add,3,4,R), write(R), nl, fail.` then a second `main` clause) exposed that **top-level multi-clause `main` does not fall through to its second clause on backtrack, at all, independent of this fix or of call/N**. Minimal control, zero user predicates beyond `write`/`nl`:
```
:- initialization(main).
main :- write(one), nl, fail.
main :- write(two), nl.
```
prints `one` then `Warning: initialization goal failed: main/0` — never reaches `two`. Reproduced identically with and without this session's fix, with and without any predicate call inside clause 1. This is a different mechanism (top-level goal/clause-alternative backtracking, not meta-call dispatch) and is flagged here only because it was found in the course of regression-testing this row; it is not this row's DONE-WHEN and was not investigated further. Worth a fresh row — it would affect any `:- initialization(main).` program relying on a fail-driven loop across multiple top-level clauses of `main`, which is a common idiom.
