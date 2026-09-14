# FINDING 2026-09-13 hq_C — a census taken per FILE cannot see the same dependency held per CASE

**Measured on** SCRIP 5feb8e0be, corpus 7214b8d6e, against swipl 9.0.4. Row
`prolog-logtalk-encodings-group`; ruling by the cto same day (CEO-542, CEO-391).

## The claim

`corpus/packages/prolog/logtalk_iso/UNGRADABLE.tsv` declares 208 `tester.lgt` files
`CONTAINER_OR_LIBRARY`, each with the same stated reason: they "need the Logtalk runtime the vendor
does not ship here". That is correct, it is well documented, and it reads as if the dependency had
been fully accounted for.

It had not. In `unicode/encodings/tests.lgt`, **40 of 49 graded CASES hold the identical
dependency** — 20 call `logtalk_compile/1` or `logtalk_load/2` directly, and 20 more are curly goals
on predicates that only those loads define. They sat in the graded denominator, so the group read as
49 cases of engine work when its true ceiling was **9**.

## Why it was invisible

The census answered **which FILES are drivers**. It was read as **which CASES need the runtime**. Same
dependency, same stated reason — only the granularity differs, and the artifact could not say which
question it had answered. This is the family of `command -v` answering *is it on PATH* when read as
*does it exist*: **an instrument that answers a narrower question than you think you asked will never
say so.**

The tell was available and cheap:

```bash
grep -rlE 'logtalk_(compile|load)\(' */*/tests.lgt     # exactly ONE file of 192
```

**One outlier out of 192 means the census boundary and the dependency boundary are not the same
line.** Everywhere else those predicates are confined to the driver, which is what made the per-file
census look complete.

## What was built, and why prose was not enough

The cto ruled the 40 outside the baseline — measured, not reasoned: (a) no Logtalk runtime ships
anywhere under `/home/resources` or in `corpus`; (b) **swipl itself raises `existence_error` on
`logtalk_load/2`**. CEO-542: outside-the-baseline is about the ORACLE, never about us.

⛔ **The ruling was made conditional on an instrument, and that condition is the durable part.** Moving
40 cases out of a denominator by prose, with nothing that can recompute the move, "would read as a
9-of-9 green forever and nothing in its output would distinguish it from the day it was
load-bearing." So `util_logtalk_grade.py` now assigns `OUTSIDE` **per case** by asking the oracle, and
names **the predicate** that put each case there. It reproduced the hand census exactly — 40 — having
been written to measure rather than to agree.

It refuses to guess: 7 cases stay IN as UNRESOLVED **and named**, because an audit that cannot say how
many subjects it failed to resolve is not a measurement. With no oracle present it assigns **nothing**
— an assigner that gets more generous when it can measure less is a criterion that improves as the
work becomes less measurable.

## The sharper defect, found inside the instrument

Resolving a fixture provider means decoding UTF-16/UTF-32 — the fixtures of this group *are* the
encodings. The obvious guard fails **silently**: a UTF-16BE file with no BOM, decoded as UTF-16LE,
yields plausible text with **no NUL characters at all**. A "reject it if it has NULs" test passes it,
the predicate is simply not found, and the case reports UNRESOLVED — **which reads as the assigner
being careful rather than as the assigner being wrong.** 4 of 20 sat in that hole and the count read
36 with nothing anywhere saying it was short. Candidates are now decoded and *scored* by how much of
the result looks like source.

## Control arm

A census bounds the blast radius to **three** directories in the whole 192-group suite (only
`unicode/encodings`, `predicates/format_2`, `predicates/format_3` hold a non-`tests`/`tester` `.lgt`
that can fire the provider rule). All three measured, plus 11 more: every one reads `OUTSIDE 0` with
every board cell unchanged, including `format_2` 198/198 and `format_3` 200/200.

## How to apply

Before working a suite row, ask **what granularity its exclusion table is keyed at**, and grep the
*graded* files for the excluded thing's own signature. Report the ceiling as a measured split before
curing anything — a row's number otherwise invites work that cannot exist. And when a denominator
moves, say in the ledger that it moved **because the population was wrong**, never silently.
