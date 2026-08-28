# FINDING 2026-08-28 seat01 — PROLOG `halt/0` AND `halt/1` ARE UNIMPLEMENTED: EVERY CALL FALLS THROUGH TO THE UNDEFINED-FUNCTION STUB (ERROR 22)

**Row:** `tests-consolidate-prolog` (postoffice task). **Tree:** SCRIP (pre-pristine dev build, `-O0`), corpus `545f0191`. Found while characterizing rung58-83 for conversion — not a task-infra bug, a real x86 codegen/runtime gap in the Prolog frontend.

## SUMMARY

`halt.` and `halt(N)` are listed in `lower_prolog.c`'s determinism-classifier table but have **no actual lowering arm or runtime implementation**. Any call to either falls through to `rt_proc_call_open`'s not-found path, which (per `FINDING-2026-08-27-seat11-unload-error-022-...md`, same stub, different call site) routes to `rt_ab_undef_fn_stub` — `core_runtime_error(22, "Undefined function called")`, `exit(1)`. The program's real work always completes correctly first; the failure is purely in the `halt` call itself doing the wrong thing instead of nothing happening.

## MINIMAL REPRO

```prolog
:- initialization(main).
main :- write(before), nl, halt.
```
```
$ ./scrip repro.pl < /dev/null
before

** Error 22 in statement 0
   Undefined function called
[rc=1]
```
`halt(0)` in place of `halt` reproduces identically. `before` prints fully and correctly — the crash is strictly on the `halt` call itself, confirmed by the minimal 2-line witness above (no other construct involved).

## ROOT CAUSE (precisely located, not guessed)

`src/lower/lower_prolog.c:1134`, inside `pl_det_goal_ok`'s `extra[]` array: `{ "true", "fail", ..., "halt", 0 }`. This array is consumed only by `pl_det_name_in` to answer "is this goal deterministic" for cut/backtrack classification — **it never synthesizes a call or emits any IR**. `halt` being present here means the classifier is satisfied and moves on; nothing downstream ever gives it a real implementation.

Compare to a working 0-arity builtin, `nl/0`, at `lower_prolog.c:645`:
```c
if (!strcmp(nm, "nl") && t->n == 0) {
    IR_t * call = build(cx, IR_CALL_PROLOG, γnext, ωfail); IR_LIT(call).sval = "$nl0";
    ...
}
```
`halt` has no equivalent `if (!strcmp(nm, "halt") ...)` arm anywhere in the file (checked: only the one classifier-list mention exists tree-wide in live, non-`.bak` source — the `.bak` JVM backend at `src/frontend/prolog/prolog_emit_jvm.c.bak` does have a real `halt/0`/`halt/1` handler, but that backend is dormant per CLAUDE.md's `IS_JVM` stub-out rule and not reachable from the x86 path). With no lowering arm, `main :- ..., halt.` compiles the `halt` goal as an ordinary unresolved procedure call, which is exactly what makes it hit `rt_proc_call_open`'s 0-return / `rt_ab_undef_fn_stub` path at runtime.

**A working landing spot already exists and could plausibly be reused, not built from scratch:** `src/runtime/by_name_dispatch.c:6309`, SNOBOL4's `BID_stop` dispatch, already does "flush optional message, `exit(0)`" — the same terminate-the-process semantic `halt/0` needs. `halt/1`'s argument is the process exit code (`exit(N)`), which `BID_stop` does not currently parametrize but would need to.

## IMPACT

Corpus-wide grep for a `halt` call in still-loose `tests/prolog/*.pl`: **11 files**, of which **10 are otherwise fully clean and blocked on nothing else** (confirmed by direct measurement, stdout byte-identical to `.expected` up to the crash): `rung70_name`, `rung71_byte_io`, `rung72_unget`, `rung73_display`, `rung74_dec10_io`, `rung75_number_atom`, `rung76_at_end_stream`, `rung77_read_stream`, `rung78_read_term_opts`, `rung80_dec10_streams`. The 11th, `rung79_stream_permission`, also calls `halt` in dead-code position after a separate PZ-4 crash earlier in the same program — not attributable to this bug, see the `tests-consolidate-prolog` task ledger. No already-converted suite exercises `halt` (checked `rung1-4x/*.ref`), so this finding does not unmask a false-green anywhere already landed. Likely wider than these 11 across the full corpus (`coverage/`, `frontend/`, `samples/`, standalones — unsurveyed by this session) — anyone auditing those should grep for `halt` before assuming a clean run.

## DISPOSITION

Not fixed here — this is a compiler frontend/runtime gap, out of `tests-consolidate-prolog`'s lane (same disposition this task has consistently given `prolog-multiclause-uninit-lexprep-frame`/PZ-4: characterize, route, leave loose). The 10 otherwise-clean files above are left loose, **not KEEP.md** (this is a bug, not a permanent design choice — same precedent as every PZ-4-blocked entry in this task). Mailed to hq_C as `prolog-halt-unimplemented-error22` (hq_C owns correctness/wrong-answer classes per this task's own standing convention, e.g. the exit-status-blind and OPSYN threads).
