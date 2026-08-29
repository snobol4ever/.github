# FINDING — `forall/2` gives a wrong answer on a mixed-parity list; NOT PZ-4, no crash

**seat02 · 2026-08-29 · row `tests-consolidate-prolog` · SCRIP HEAD `fef0c2fd`**

## Context

`tests-consolidate-prolog`'s NEXT block groups `rung56_ite_backtrack` and `rung57_forall` together as
"1-entry families, 100% red — KEEP.md is their only exit," implying both need the same PZ-4-style
"leave loose, corroborate" treatment as the task's many other red witnesses. Verifying both by direct
measurement (not inheriting the grouping) shows they are NOT the same shape.

## `rung56_ite_backtrack` — confirmed genuine PZ-4, no new information

`timeout 8 scrip --run rung56.pl` → `*** stack smashing detected ***`, rc=134 (SIGABRT). The source
(`\+`-guarded backtrack, if-then-else inside a fail-driven `member/2` enumeration, a `between/3`
generator) is squarely inside `prolog-multiclause-uninit-lexprep-frame`'s already-documented trigger
set. No policy question here: this gets exactly the same treatment as every other PZ-4-blocked witness
in this task (rung44, rung50, rung58, etc.) — left loose, not KEEP.md'd, since PZ-4-blocked is this
task's own repeated standing precedent for "not a permanent design choice."

## `rung57_forall` — NOT a crash. A deterministic, oracle-confirmed WRONG ANSWER

`scrip --run rung57.pl` exits **rc=0** with clean output:
```
all_even
all_even2
vacuous_true
```
Expected (`rung57.ref`, and independently reproduced against the real `swipl` oracle):
```
all_even
not_all2
vacuous_true
```

The second line disagrees. Source line 2: `forall(member(Y,[2,3,4]), Y mod 2 =:= 0) -> write(all_even2)
; write(not_all2)`. `3` is odd, so `forall/2` over `[2,3,4]` must fail (not every element is even) and
the `else` arm should fire, printing `not_all2`. scrip's `forall/2` instead reports success
(`all_even2`) — a real logic defect in the `forall/2` implementation for a mixed-parity list, not a
memory-safety crash. Lines 1 and 3 (`forall` over an all-even list, and the vacuously-true empty-list
case) are both correct, so this isn't "forall never works" — it's specific to a list containing a
failing element.

## Why this matters for the task

Grouping this with rung56 under "KEEP.md is their only exit" would have buried a genuine, previously
uncharacterized correctness bug inside PZ-4 corroboration traffic, where it reads as "one more
already-understood crash" rather than what it is: a new, distinct, oracle-confirmed wrong-answer bug.
Not root-caused here (out of this row's lane — this is a test-consolidation task, not a `forall/2`
debugging session); mailed to `hq_C` per RULES.md's own split ("a wrong ANSWER belongs to hq_C").

## Disposition for `tests-consolidate-prolog`

Leave `rung57_forall` loose, **not** KEEP.md'd (a bug, not a permanent design choice — same standing
rule this task already applies to `rung50_between_errors`, the other non-PZ-4 wrong-answer witness it
found). Convert once the `forall/2` defect is fixed.
