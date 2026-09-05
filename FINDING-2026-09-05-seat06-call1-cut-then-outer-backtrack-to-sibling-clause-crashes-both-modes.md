# FINDING 2026-09-05 seat06 — `call/1` wrapping a cut, then backtracking OUT into a sibling clause, crashes both modes

**Seat:** seat06 · **Row:** `prolog-rung-10b-assert-retract-abolish-clause-the-dynamic-database` (rung 10, ladder witness `ladder__rung10_call_n_call_of_cut_is_local`) · **Mode:** FLEET-20
**Trees graded:** SCRIP `64b21412e` · corpus `4e11cb9ee` (no source edits — this is a WALK finding, ablation only, not a cure)
**Build:** incremental `make`, `RT_OPT=-O0`.

## 1. The defect, in one sentence

`call((Goal, !))` followed later by a `fail` that backtracks all the way OUT of the enclosing clause (to try a
**sibling** clause of the same predicate) crashes — SIGILL in mode 3, SIGSEGV in mode 4 — instead of running
the sibling clause. The cut's own barrier is correct in isolation (`call(!)` alone works; a bare `!` with no
`call` correctly cuts the sibling too, matching ISO); the crash is specific to unwinding OUT of a `call`'s own
frame from a choice point BELOW it.

## 2. Minimal witness (already on the ladder — no new mint needed)

Already present as `ladder__rung10_call_n_call_of_cut_is_local` (`corpus/tests/prolog/ALL.pl:2158`, entry 502),
4 lines:

```prolog
p1(1). p1(2). p1(3).
q1 :- call((p1(X), !)), write(X), fail.
q1 :- write(done).
:- initialization(main).
main :- q1, nl.
```

swipl (oracle): `1done`
scrip m3: `Illegal instruction` (dumped core), rc=132
scrip m4: SIGSEGV, rc=139

## 3. Ablation — each line changes exactly one ingredient of the witness above

```
call((p1(X), !)), write(X), fail. / <no second q1 clause>       green  ("1")  <- drop the sibling-clause backtrack target
call((p1(X))),    write(X), fail. / q1 :- write(done).          green  ("123done") <- drop the cut
p1(X), !,          write(X), fail. / q1 :- write(done).         green  ("1", goal fails) <- drop the call wrapper (bare cut correctly also cuts the sibling — matches ISO)
call(!), write(ok), nl.  (trivial, no backtracking at all)      green  ("ok") <- cut-in-call alone, no outer backtrack
```

## 3a. ADDENDUM 2026-09-05, same sitting — the same shape reproduces through `\+`/`forall`, not just `call/1`

Found while verifying an unrelated fix (`prolog-cut-not-opaque-in-if-then-else-condition-and-negation`,
opaque-cut barrier for `->`/`\+`'s condition). `\+` and `call/1` are BOTH opaque-cut-barrier constructs (both
manage `cx->cutω` scoping and an `IR_BOUND`/`IR_UNMARK` mark), so this is very likely the same underlying
mechanism, not a second defect:

```prolog
p(1). p(2). p(3).
:- initialization(main).
main :- ( forall(p(X), (X<3, !)) -> write(succeeded) ; write(failed) ), nl.
```

swipl: `failed`. scrip: SIGSEGV, both with and without the `->`/`\+` opacity fix (confirmed via stash-and-
rebuild — this is pre-existing, not introduced by that fix). Ablated:

```
forall(p(X), X<3)                          — no cut — green ("failed")
forall(member(X,[1,2,3]), (X<3,!))         — different generator — SEGV, same as p(X)
\+ (p(X), \+ (X<3, !))                     — forall/2's own double-negation expansion, bypassing forall/2 as a construct — SEGV
```

So it is not `forall/2`-specific and not tied to a particular generator: any backtracking generator whose
body reaches a `\+` (or presumably `call/1`) containing a cut, where the OUTER generator can retry after
that opaque scope has run once, crashes. This is the same ingredient shape as §3 above (opaque-barrier
construct + outer backtrack into it) reached through a different pair of constructs — strengthens rather
than replaces §1-3's diagnosis. Not ablated further, not gdb'd/asm-diffed — same walk/cure boundary as §4.

**All three ingredients are load-bearing together; none crashes alone.** The trigger is specifically: a `call`
whose body cuts, combined with control later leaving that call's enclosing clause via backtracking to reach a
**sibling** clause. Best guess, not measured (leaving the actual mechanism to whoever takes this, per today's
walk/cure split — see §4): the `call`'s cut-barrier frame is not being unwound when backtracking passes
through and out of it on the way to the next clause of `q1`, so the choice-point/return-address bookkeeping the
outer clause-alternation depends on is corrupted by the time it's read. Not gdb'd, not asm-diffed — that is the
RULES.md-mandated next step for whoever cures this, not done here.

## 4. Scope note

This is a WALK finding (ablate to a minimal witness, file it, keep walking), not a cure — the engine mechanism
implicated (call-frame / cut-barrier unwinding under outer backtracking) is core Byrd-box choice-point plumbing,
squarely HQ/Opus territory per today's FLEET-20 division ("Sonnet seats walk, census, witness — Opus HQs cure").
No `src/` changed for this finding.

## 5. Also measured this same sitting, lower severity, folded here rather than a separate file

Fresh census of rung 10 (`test_prolog_ladder.sh --only 10`, post the `$db_alive` restore in SCRIP `a5c4e9b72`):
41 witnesses, 82 gradings, PASS=36 FAIL=46. Two abolish sub-cases beyond what the `$db_alive` restore fixed
still answer wrong (not crash): `ladder__rung10_abolish_abolish_removes_clauses` and
`ladder__rung10_abolish_retractall_vs_abolish`, both rc=0 (wrong answer, not a refusal) — the DB-level
clause-store effect of abolish vs retractall looks incomplete beyond the existence-check guard this session
restored. Also `ladder__rung10_dcg_pushback` (rc=1). All three: not ablated further this sitting, not attempted,
recorded in the row's own LEDGER for whoever takes the engine half next.
