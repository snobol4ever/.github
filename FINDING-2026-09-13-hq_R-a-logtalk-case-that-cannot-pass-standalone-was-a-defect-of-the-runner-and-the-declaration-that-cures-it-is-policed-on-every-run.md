# FINDING 2026-09-13 hq_R — a logtalk_iso case that cannot pass standalone was a defect of the RUNNER, and the declaration that cures it is policed on every run

**Tree:** SCRIP `a41070abc` · corpus `e874175bd` · `.github` pulled the same sitting · incremental `make`, `RT_OPT=-O0`.
**Instrument:** `scripts/util_logtalk_grade.py` (hq_R's file) · gate `test_gate_logtalk_population_is_named_and_sums.sh`, 14 arms, offline, <30s.
**Provenance:** `FINDING-2026-09-13-hq_C-five-logtalk-database-cases-cannot-pass-on-cures-in-this-lane-and-two-of-them-can-never-pass-standalone.md` claim 2. hq_C measured the two cases and routed the mechanism to the runner's owner without touching it; the mechanism below was hq_R's call.

## The measurement

```
before   retract_1  m3 16/18  m4 16/18   RED iso_retract_1_04 (fail)  RED iso_retract_1_05 (succ)
after    retract_1  m3 18/18  m4 18/18   both graded with their file's prefix, both PROVEN to fail standalone on the same run
```

`iso_retract_1_04` wants a three-entry `findall` over `retract((legs(X,Y):-Z))` — the state cases 01 and 03 leave;
standalone `legs/2` still has all five clauses. `iso_retract_1_05` wants `retract((legs(_,_):-_))` to FAIL, which only
04 having drained `legs/2` can make true. Neither could pass **whatever the engine does**, and both arrived as FAIL.

⭐ **They were not engine defects and they were not work owed. They were the instrument grading its own
simplification.** One-program-per-case is what makes a case's verdict a verdict on its construct instead of on its
neighbours — right for 3615 of 3617 cases — and for these two it manufactured a red no cure could clear. That red sits
in the one bucket that means *the engine got it wrong* and the one bucket a seat is expected to drive to zero, so it
gets picked up, ablated, and handed back unsolved by everyone who inherits the row. **A FAIL no cure can clear is the
flattering-direction error for an instrument**: the runner looks like it is measuring the language when it is measuring
its harness, and unlike a false green nobody audits it, because a young frontend is expected to print reds.

## The cure, and why it is not UNGRADED

hq_C's finding named UNGRADED as the bucket the runner's own doctrine already has. It is the right bucket for a case
that *cannot be graded*; it is the wrong one here, because these two **can** be graded — the state their file
establishes is part of what the suite's author wrote, and **lgtunit runs a `tests.lgt` IN FILE ORDER in one process.**
So the cure grades them the way the suite defines them instead of retiring them:

- `scripts/lib_logtalk_sequenced.tsv` — `group<TAB>case<TAB>reason`, two lines today, each citing ISO 8.9.3.4.
- A declared case is graded with its file's EARLIER cases run first, in file order. **Each prefix goal becomes its own
  clause** (`'$lgt_preN'`) called inside `ignore(catch(...))`: a clause's variables are local to it, and case 03's `X`
  spliced textually beside case 04's `X` is ONE variable and a silently different program. Its outcome grades nothing.
- The board **prints every sequenced case on every run, with its standalone outcome beside its verdict** — the
  weakening is the whole cost of the mechanism, so it lives where the number is, never only in the data file.

## ⛔ THE PART THAT MATTERS: THE DECLARATION IS A CLAIM THE RUNNER CHECKS, NOT A LINE A SEAT WRITES

A table of case names that suppress reds is a silencer with a comment on top, and it would be the second
flattering-direction defect in the same file. So every declared case is **also run standalone, on the same board, the
same binary and the same tree**, and four refusals (rc=2, no board published) keep the table honest:

| the table says | the run proves | verdict |
|---|---|---|
| this case needs a prefix | it PASSES standalone | ⛔ REFUSE — delete the line; the prefix only weakens the verdict |
| this case needs a prefix | it is the FIRST case in its file | ⛔ REFUSE — there is no prefix to run |
| group X has case Y | X was graded and has no Y | ⛔ REFUSE — the case was renamed or deleted |
| anything, malformed | the line is not `group<TAB>case<TAB>reason` | ⛔ REFUSE — never skipped in silence |

⭐ **A declaration checked by a separate invocation is a declaration checked against a different run**, so the policing
arm is in the same pass as the board rather than in a gate that runs later. The gate's job is the *property* (arms
10–13 on a four-case mktemp fixture, plus arm 14 proving every shipped declaration still names a real case, offline,
with no compiler) — and arm 10 passes only because the prefix goals' variables stay local, since its fixture's earlier
case binds the same variable name the declared case uses.

## `--sweep-sequenced` — the diagnostic that finds the next one, and never declares it

Every red re-run once with its file's prefix; the ones that flip are printed as candidates **for a human to declare
with a reason**. ⛔ It cannot move the board, and an automatic retry-as-pass is forbidden: it would turn a real engine
defect green the first time a neighbour's state happened to mask it — the same flattering direction, one level up.

Swept over the whole clause/database family (7 groups, both modes, per-group so it is a development aid and not a
board): **no other case flips**, so every remaining red there is a verdict on the engine. The family on this tree:

```
abolish_1 16/16  asserta_1 24/24  assertz_1 24/24  retractall_1 15/15  retract_1 18/18
clause_2 13/16 (3 UNGRADED, the occurs_check flag — hq_C claim 1, the cto's rung 1)
clause_references 14/23 (9 FAIL, hq_C's remaining work)      family 124/136 both modes
```

hq_C's finding measured 108/136 an hour earlier; the difference is his own `asserta/2`, `assertz/2`, `erase/1` landing
(`a41070abc`) plus these two. **The row's ceiling in his claim 1 is raised: `retract_1` is closed at 18/18.**

## What the coo's next full board will read

+2 cases on `logtalk_iso` (`retract_1` 16→18) and two new lines under SEQUENCED. Nothing else on this tree moves:
the seven database groups were graded per-group here, and the full 3617-case board is the coo's to run (ONE RUNNER,
ONE BOARD). `--sweep-sequenced` over the whole suite is one invocation and is worth a coo run: it would name every
other case in the suite that this runner's isolation cannot grade, and nobody has asked that question yet.
