# FINDING 2026-08-29 seat08 — PROLOG `catch/3` CANNOT INTERCEPT `existence_error` FOR AN UNDEFINED PREDICATE: SAME STUB AS `halt/0` (ERROR 22), DIFFERENT CALL SITE, DIFFERENT SEVERITY

**Row:** `tests-consolidate-prolog` (postoffice task). **Tree:** SCRIP `491c4d1f`, corpus `69c43155`. Found while disposing `rung38_iso_errors/03_existence_error.pl`, flagged unexamined since seat10's 2026-08-27 entry on this same task ("a genuine output mismatch, not a crash — different bug, unexamined").

## SUMMARY

`catch(Goal, error(existence_error(procedure, Name/Arity), _), Recovery)` never fires when `Goal` calls an undefined predicate. SCRIP raises the failure as a raw runtime abort (`** Error 22 ... Undefined function called`, `exit(1)`) instead of a catchable ISO error term, so `Recovery` never runs and the process dies. This is the **same stub** `FINDING-2026-08-28-seat01-prolog-halt-unimplemented-error22.md` already root-caused for `halt/0`/`halt/1` — `rt_ab_undef_fn_stub` via `rt_proc_call_open`'s not-found path — reached here through a different call site (a genuinely undefined user predicate, not an unimplemented builtin). Read that FINDING first; this one only covers what's different.

## MINIMAL REPRO

```prolog
main :-
    catch(
        no_such_pred(42),
        error(existence_error(procedure, no_such_pred/1), _),
        write(caught_existence_error)
    ), nl.
```
```
$ ./scrip repro.pl < /dev/null
** Error 22 in statement 0
   Undefined function called
[rc=1]
```
Expected (and what every other ISO Prolog does, confirmed against `swipl`): `caught_existence_error`, `rc=0`. The witness's own `.ref` in the corpus (`rung38_iso_errors/03_existence_error.ref`) already carries the correct expected output — it was never wrong, the runtime is.

## WHY THIS IS NOT JUST THE HALT FINDING AGAIN

The `halt` finding is "one builtin is unimplemented" — a missing feature with a narrow, known blast radius (11 files, all calling `halt` directly). This one is structural: **`rt_ab_undef_fn_stub` fires for ANY undefined-predicate call, and it never routes through Prolog's own error/catch machinery at all** — it is a hard process abort below the language-semantics layer. That means `catch/3` around an existence_error is unconditionally dead code in SCRIP today, for any predicate name, not just `halt`. ISO Prolog's own conformance suite leans on `catch(UndefinedGoal, error(existence_error(procedure,_),_), _)` as a standard idiom for optional/plugin-style predicate dispatch (checking whether a predicate exists by trying to call it and catching the failure) — this witness is exercising exactly that idiom, not an edge case.

## IMPACT (measured, not estimated)

Grepped the still-loose `tests/prolog/` tree for `existence_error` and `catch(`+undefined-looking callee patterns: this witness (`rung38_iso_errors/03_existence_error.pl`) is the only one in this task's current scope that specifically exercises this path — it was not previously miscounted as PZ-4 or the metacall class (confirmed by direct measurement: `rc=1`, no SIGSEGV/SIGILL/SIGABRT, and the callee `no_such_pred/1` is a plain atom-and-arity, not a variable-bound goal, so it does not fit the `synth-EXPR`/metacall signature either — see the note on that class below). Did not survey `coverage/`, `frontend/`, `samples/`, or standalones for the same pattern this session — out of scope for this pass, flagging for whoever surveys those next.

## DISPOSITION

Not fixed here — compiler runtime gap, out of this task's lane (same disposition this task gives every other compiler-bug witness: characterize, route, leave loose). Left loose, **not KEEP.md** — this is a bug, not a permanent design choice, same precedent as every other non-PZ-4 wrong-answer witness in this task (`rung50_between_errors`, `rung57_forall`). Mailed to hq_C as `prolog-existence-error-not-catchable` (hq_C owns wrong-answer/correctness classes per this task's standing convention).
