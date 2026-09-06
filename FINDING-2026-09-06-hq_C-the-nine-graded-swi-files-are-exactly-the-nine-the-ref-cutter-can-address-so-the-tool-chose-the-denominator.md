# FINDING 2026-09-06 hq_C — the 9 graded swi_tests files are exactly the 9 the ref cutter can ADDRESS, so the instrument chose the denominator

**Rows:** CEO-316 / THE PACKAGE LOCKDOWN · `prolog-swi-tests-refs-were-cut-through-a-shim-...` ·
`prolog-swi-tests-the-two-copies-of-test-string-are-not-identical-so-one-ref-grades-two-different-files`.
**Tree:** SCRIP `5fb318258`, corpus `df91fd349`, oracle `/usr/bin/swipl` 9.0.4. Measured, not quoted.

## The measurement

```
shipped .pl                = 249
declaring begin_tests      = 170
  top-level                =   9   <- addressable by util_swi_cut_refs.sh
  in subdirectories        = 161   <- NOT addressable
already have a .ref        =   9
basename collisions        =   9
```

`util_swi_cut_refs.sh` takes **basenames** and resolves `$SWIT/<base>.pl` — top level only:

```
$ bash scripts/util_swi_cut_refs.sh test_apply
⛔ REFUSE: .../swi_tests/test_apply.pl missing -- skipping test_apply     # it is at library/test_apply.pl
```

## The claim

**The set of files that have refs is identical to the set the cutter can reach.** Not approximately — exactly,
9 and 9. Nobody ever decided that these 9 programs were the swi conformance population. **A tool that
addresses by basename was pointed at a corpus that is organised by path, and the population it happened to be
able to name became the denominator.** The 9 were then quoted for weeks as *9 graded of 249 shipped*, which
reads as a statement about corpus coverage and is actually a statement about an argument parser.

⭐ **The same one line explains the `57×2` double count that has its own row.** Because addressing is by
basename and 9 basenames exist twice (`swi_tests/X.pl` and `swi_tests/core/X.pl`), one `.ref` is resolved for
two different files and every one of those 57 suite-lines is graded twice. **The double count and the tiny
denominator are not two problems. They are one addressing mode seen from two sides** — by-basename over a
by-path corpus both collides names and cannot descend.

## Why this blocks CEO-316 as written

CEO-316 (Lon 2026-09-06 09:31, *"grade EVERY SINGLE package program from Icon and Prolog"*) orders the refs
cut **this sitting, with seat12's cutter**. That cutter can address **9 of the 170**. The remaining **161
cannot be named to it at all** — this is not a slow path, it is a refusal. The order cannot be executed as
written until the cutter accepts paths.

⛔ **I did not fork the cutter, and that is deliberate.** hq_C built a second ref cutter earlier the same day,
it agreed with seat12's on 7 of 9, and it was **deleted rather than kept beside it** — two writers for one
artifact is the collision class (PROTOCOL 4c), and the seven agreements were the part that would have
*licensed* the bug. Writing a second path-aware cutter now would repeat exactly the mistake that retraction
was for. The cutter needs **one** change by **one** owner: accept a path, resolve refs beside the source
rather than by basename.

## What generalises

1. **An instrument's addressing mode silently defines the population it can measure**, and the population then
   gets read as a fact about the subject. Nothing in the number `9/249` says *this is how many the tool could
   name*.
2. **The failure was loud at the unit and invisible in aggregate.** `⛔ REFUSE: ... missing -- skipping` is a
   perfectly honest line, printed per file. Run over a default base set that already excludes the 161, it is
   never printed at all — the tool defaults to *every `*.ref` already in the dir*, so it only ever addresses
   files it has already succeeded on. **A default set derived from past output cannot discover what it missed.**
3. Same family as this seat's other finding today: 240 individually-honest exclusion notes composing into a
   denominator that cannot fall. **Both are aggregates that no amount of per-entry care can catch, because
   every entry is correct.** Only something that reads the POPULATION sees it.
