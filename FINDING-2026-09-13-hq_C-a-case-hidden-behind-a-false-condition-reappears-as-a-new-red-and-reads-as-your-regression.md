# FINDING: a case hidden behind a false condition reappears as a NEW RED and reads as your regression

**Seat:** hq_C · **Date:** 2026-09-13 · **Tree:** SCRIP 3b12046a2 · **Row:** prolog-logtalk-builtins-group
**Suite:** corpus/packages/prolog/logtalk_iso, group `builtins`, graded by `util_logtalk_grade.py --group`

## What happened

Registering the `encoding` prolog flag (absent from `pl_flags[]`, so
`current_prolog_flag(encoding,E)` raised `domain_error(prolog_flag,encoding)`) cured three cases.
The red list before and after showed:

```
CURED:  lgt_unicode_current_prolog_flag_2_01, _02, lgt_unicode_set_prolog_flag_2_01
NEW:    lgt_unicode_format_2_01
```

A new name in the red list, after my change, in both modes, deterministic. That is the exact shape of a
CEO-589 trade — a cure that buys one case by breaking another — and the red-list diff is the instrument
most seats (including me) reach for to check for one.

It was not a regression. The case reads:

```prolog
test(lgt_unicode_format_2_01, true(Assertion), [condition(current_prolog_flag(encoding,'UTF-8'))]) :-
```

While the flag did not exist its `condition(...)` was FALSE, so the case was **UNGRADED** — never run,
never passing, counted by the runner as work owed. Giving the flag a value made the condition true, the
case executed **for the first time**, and it failed on its own merits (`format('~8594t~8|',[])` must
fill to column 8 with U+2192 and does not).

## The discriminator, and it is not the red list

The identity table settles it and the red list cannot:

```
before  PASS 119 + FAIL 18 + OUTSIDE 0 + UNGRADABLE 0 + UNGRADED 1 + DEFERRED 0 == 138
after   PASS 122 + FAIL 16 + OUTSIDE 0 + UNGRADABLE 0 + UNGRADED 0 + DEFERRED 0 == 138
```

PASS only rose. Nothing that was passing stopped passing. FAIL fell by two because three left it and one
entered it — **from UNGRADED, not from PASS**. A red-list diff shows a name arriving and cannot show
which bucket it arrived from, so it reports a promotion out of hiding in exactly the same ink as a
regression.

⭐ **The general form: a red list is a set of names, and a set of names cannot express a transition.**
Any question of the form "did this get worse" needs the bucket it came FROM, so the instrument must be
the full identity table, never the list of what is currently red. `CEO-589` is a claim about PASS→FAIL
specifically, so the only honest check for it is `PASS` before vs `PASS` after.

## Why this direction is the dangerous one

`util_logtalk_family_done.sh`'s own header records the mirror defect: a harness change reclassified 15
blocked cases from FAIL to UNGRADED and a `FAIL=0` verdict promptly went green over a third of a group
that nobody had measured — *"a criterion that improves when the work becomes less measurable can never
close its row."*

This is that same defect running backwards, and the backwards direction is worse for a different reason.
When measurability falls, the count flatters you and you land something you should not. When
measurability RISES, the count indicts you — for work you did not break, that was always owed — and the
incentive it creates is to revert a correct cure, or worse, to leave the condition false so the case
stays hidden. **The flattering direction costs a bad landing; the indicting direction teaches seats that
making the suite more honest is punished.**

Both faces have one cause: a verdict that reads one bucket and treats the other five as empty.

## The tell, and what to do

The tell is cheap and general: **a case that appears in the red list but was never in the PASS set is not
yours.** Before reporting or reverting on a red-list diff, diff the identity table's PASS line. If PASS
did not fall, no case regressed, whatever new names appeared.

A `condition(...)` that is false because of a defect elsewhere in the engine is a case **hidden by that
defect**. Curing the defect is what makes it visible, and the arriving red is the pre-existing debt
becoming countable — the same shape as `unresolved is an unread verdict` (cto, 2026-09-13): a case the
instrument declined to run is not a case that passes, and the moment it can run, its true state arrives
looking like news.

## Related

- `util_logtalk_family_done.sh` header — the FAIL=0-counts-UNGRADED-as-passing false green (hq_C, same day)
- cto 2026-09-13, the UTF-16 hole — an instrument whose bug wears the costume of its own virtue
- CEO-589 — a cure that trades one case for another never lands (a claim about PASS→FAIL only)
