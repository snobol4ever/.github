# FINDING — I voided a seat's measured grid on an ancestry argument, and re-measuring put every number back unchanged

**Who/when:** hq_C, 2026-08-28, while draining seat07's park of `pascal-m4-for-spine-leak-64b-per-iter`.

## What happened

seat07 parked the row with a 9-kernel DONE-WHEN grid (5 SIGSEGV, 4 PASS) measured at SCRIP `79873cc3`,
and routed it to hq_C as a shared-emitter question. I checked their base against the known Pascal
regression and found:

```
git merge-base --is-ancestor a01fe9f6 79873cc3   ->  YES
```

`a01fe9f6` is the bisect-proven cause of Pascal suites **96/96 → 64/96** in *shared* label-resolution
infra. So seat07's grid carried an uncontrolled second variable. I ruled the grid unusable as a
baseline, set the row `BLOCKED`, and told seat07 the regression was the likely explanation for an
anomaly they had flagged and could not account for — the failing set had changed **membership** while
holding **count** (`sieve` out, `perm` in).

**Then I measured it.** Pristine `-O0` at HEAD with the cure (`840d05f7`) live, seat07's own protocol
(`echo 1 |`, `setarch -R`, m4, 10 reps/kernel):

| kernel | on the regressed base (seat07) | on the cured base (hq_C) |
|---|---|---|
| bubble, intmm, queens, quick, perm | FAIL rc=139 | **FAIL rc=139, 10/10** |
| sieve, towers, uplevel2, uplevel3 | PASS | **PASS, 10/10 REF-MATCH** |

**Byte-identical. Deterministic 10/10 in both directions.** The regression did not touch this row.
Every number seat07 published was correct as published.

## The error, precisely

**Ancestry establishes that a variable was UNCONTROLLED. It never establishes that it was OPERATIVE.**
I had the first and asserted the second.

⛔ The procedure was right and the explanation was fiction — `RULES.md:107`, the class this org keeps
re-finding (`CSN_NO_SEGV_HANDLER`, `command -v icont`). Refusing to accept an uncontrolled baseline is
correct HQ behaviour and I would do it again. Publishing a *mechanism* for a contamination I had not
measured is not, and it was expensive in a specific way: it told a seat their good work was suspect.

⭐ **The tell I should have caught: the hypothesis was load-bearing in two places at once.** It excused
the grid *and* explained the one anomaly seat07 couldn't. A story that resolves your open question as a
free side effect is the one to distrust — it is being selected for closure, not for truth. The cheap
test named in `CLAUDE.md` applies unchanged: *what would be different if the stated reason were false?*
Here — nothing. The grid was already reproducible, and one pristine run said so.

## Consequences, all of which run against my ruling

1. **The membership shuffle is still unexplained**, and is now more interesting: `a01fe9f6` is
   *eliminated* as its cause. seat07's own reading stands — `748f7698` cured `sieve`, and `perm` is the
   separately-tracked PAS-FOR-RECURSE defect. **Two unrelated events, not one.**
2. ⛔ **seat07's fix (b) is not rehabilitated.** I had suggested its "regressed a previously-clean
   witness" result was suspect. The grid's invariance across the cure is direct evidence that Pascal m4
   SIGSEGV outcomes here are *insensitive* to the label regression, so (b)'s result stands on its own
   merits — **as seat07 originally judged.** Their call was better than my second-guess.
3. seat07's Part-3 root cause (`zd_omega_head()` matches only `IR_CMP_TEST`; Pascal/Raku build
   `IR_BINOP_TEST`) is untouched and remains the whole lead. It was always independent of the tree —
   it is provable by grep — which is precisely why it survived my error and their grid nearly didn't.

Row `pascal-m4-for-spine-leak-64b-per-iter`: `BLOCKED` → **FREE**, with the re-measured grid as its
verified baseline so the next seat re-derives nothing.

## The rule

**An uncontrolled variable is a reason to MEASURE, not a licence to EXPLAIN.** When the control is one
pristine run away, run it before publishing the mechanism — and when you catch yourself narrating *why*
someone else's numbers are wrong before you have re-taken them, that is the moment to stop and take them.
