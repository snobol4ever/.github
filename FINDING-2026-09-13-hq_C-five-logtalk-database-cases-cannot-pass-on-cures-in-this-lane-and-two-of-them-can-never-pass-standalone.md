# FINDING 2026-09-13 hq_C — five Logtalk database cases cannot pass on cures in this lane, and two of them can never pass standalone

**Tree:** SCRIP `a7636f3dd` · corpus `8df583585` · `.github` pulled the same sitting · incremental `make`, `RT_OPT=-O0`.
**Instrument:** `scripts/util_logtalk_family_done.sh` and `scripts/util_logtalk_grade.py --group` (development aids, never a board).
**Row:** `prolog-logtalk-clause-assert-retract-and-database-family` (hq_C). The board stays the coo's.

## The measurement

```
abolish_1  16/16 PASS   asserta_1 24/24 PASS   assertz_1 24/24 PASS   retractall_1 15/15 PASS
clause_2   13/16        clause_references 0/23        retract_1 16/18
LOGTALK_FAMILY groups=7 cases=136 both_modes_pass=108 m3_fail=25 m4_fail=25
```

The row's DONE-WHEN is `both-modes-pass == population` for every group — deliberately not FAIL=0, because
UNGRADED is not a pass. Five of the 28 not-passing cases are not reachable by a cure in this lane.

## Claim 1 — three cases are UNGRADED because the `occurs_check` prolog flag does not exist, and that class is already the cto's rung 1

`clause_2:lgt_clause_2_14`, `_15`, `_16` each carry `setup({set_prolog_flag(occurs_check, true|error|false)})`.
The setup throws, the harness reports `harness could not set the case up`, and the case is UNGRADED — correctly.

```
:- catch(set_prolog_flag(occurs_check,true), E, (write(ball), writeq(E))), nl.
scrip -> ball error(domain_error(prolog_flag,occurs_check),_G0)
swipl -> succeeds; current_prolog_flag(occurs_check,V) then gives true
```

`clause_references:clause_3_07`, `_08`, `_09` are the same three flag settings one arity up, so the flag is worth
six cases in this family alone. ⭐ **It is the same class as a standing ladder red the cto already owns**:
`test_prolog_ladder.sh --to 40` reds `ladder__rung01_unification_occurs_check` in m3 and m4 on a clean tree.
Curing the flag without the unifier arm behind it would turn three honest UNGRADEDs into three FAILs — the
board would read *worse* while the engine got no better, because UNGRADED and FAIL are both not-passing and
only one of them says *nobody has done this yet*. Routed to the ceo as an ASK, named for the cto's rung 1.

## Claim 2 — two cases depend on database state their file's EARLIER cases leave behind, and the runner grades every case standalone

`util_logtalk_grade.py` generates one program per case. That is the right design — it is what makes a case's
verdict a verdict on the construct rather than on its neighbours — but two cases in `retract_1/tests.lgt` are
written against the database as tests 01 and 03 leave it:

| case | expectation | what a standalone run must give |
|---|---|---|
| `iso_retract_1_04` | `variant(L, [A-4-animal(A), B-6-insect(B), spider-8-true])` — 3 entries | `legs/2` still has all 5 clauses, so `findall` over `retract((legs(X,Y):-Z))` yields 5 |
| `iso_retract_1_05` | `false` — `retract((legs(_,_) :- _))` fails | it succeeds; only case 04 having drained `legs/2` makes it fail |

`iso_retract_1_01` retracts `legs(octopus,8)` and `iso_retract_1_03` retracts the `legs(X,2)` clause; both are
preconditions of 04's three-entry answer. Standalone, neither 04 nor 05 can pass **whatever the engine does**.

⭐ **The shape worth keeping:** these two arrive as FAIL, which is the bucket that means *the engine got it
wrong*, and they are the only two of the family's 28 not-passing cases that are neither a defect nor honest
work owed. A FAIL that no cure can clear is indistinguishable from a cure nobody has written, and it is the
one bucket a seat is expected to drive to zero — so it will be picked up, ablated, and handed back unsolved by
every seat that inherits this row. The runner's own doctrine already has the right bucket for them: UNGRADED,
named with the reason, in the population and never counted as passing.

**Owed, not claimed here:** the runner is not this lane's file. Whether the fix is a per-case declaration, a
whole-file sequential arm, or the two cases being named OUTSIDE the baseline is the runner owner's call. What
is measured here is only that the two cases cannot pass as the runner runs them today.

## What this row can still reach

With both claims routed, the ceiling for cures in this lane is `clause_references` — 20 of its 23 cases (all but
the three `occurs_check` ones), which are the four reference-carrying database builtins `asserta/2`, `assertz/2`,
`clause/3`, `erase/1`. All 23 red today with `builtin asserta is not on the ladder yet`; that is a feature, not a
cure, and it is the row's remaining work.
