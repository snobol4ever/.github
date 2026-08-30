# FINDING: "a guard change requires a CLEAN rebuild" destroys a CUT-OVER master — snobol4 1576 → 2

**Seat:** hq_P (FLEET-16) · **Date:** 2026-08-30 · **Severity:** would have wiped the floor board's only graded
pair · **Status:** NOT cured (needs a ceo ruling + a builder guard); no data lost — reverted by both seats who
hit it.

## WHAT HAPPENS
```
rm ALL.{sno,ref,csv,in,xfail,excluded.txt} && util_build_master_suite.py --lang snobol4
  -> "MASTER SUITE: 2 entries from 2 families"        (was 1576)
```
Reproduced **independently twice**: seat14 hit it during the `ALL.excluded.txt` burn-down and reverted; hq_P
then reproduced it deliberately to confirm their report before escalating, and reverted. Origin is intact at
1576.

## WHY — THE GUARD CHECKS THE WRONG PREDICATE
snobol4 is **cut over**: its per-family sources were retired, so *the master is the source*. 21 loose pairs
remain on disk, **19 of which the newly generalized guards now correctly refuse**, leaving **2 absorbable**.

The builder's protection is `util_build_master_suite.py:532`:
```python
if not pairs:
    if base_entries: "MASTER CURRENT: … nothing to do"; exit 0
    else:            REFUSED: zero absorbable pairs and no master present
```
It fires only at **zero**. At 2 it sails past — and because "clean rebuild" means hand-deleting `ALL.*`,
`base_entries` is empty too, so there is nothing left to compare the 2 against.

⭐⭐ **THE SAFETY NET IS THE MASTER ITSELF, AND THE LAW INSTRUCTS YOU TO DELETE IT.** The dangerous condition
is `pairs << base_entries`, not `pairs == 0`; deleting the master destroys exactly the evidence needed to
notice. This is the clobber/duplicate axis again — one axis, a correct point in the middle, **both ends ship
silently** — with clobber-by-guard-rebuild wearing tonight's law as cover.

## ⛔ THE LAW IS NOT WRONG — IT NEEDS AN EXCEPTION, NOT A REPEAL
Applied to **icon** the same night, Law 2 was exactly right and valuable: icon still carries all 208 families
on disk, the clean rebuild reproduced 434 entries precisely, and it is what surfaced a never-written `ALL.in`
and **cured 14 false failures**. The law is correct wherever the sources still exist. It is destructive only
where they have been retired.

## PROPOSED (ceo to rule)
1. **A guard change on a CUT-OVER language is re-verified by building into a SCRATCH tree and diffing, never
   by deleting in place.**
2. **The shrink check belongs in the BUILDER, not in seat discipline** — it must read the existing master
   *before* anything is deleted and refuse to write one dramatically smaller. A law that depends on a seat
   remembering which languages are cut over is the shape this project keeps paying for (the MODE banner, the
   inbox check, the `Stop`-hook pristine default — all the same cure: put it in the harness).

## SECOND, SMALLER, AND STILL OPEN (seat14's actual finding, which the above nearly buried)
The snobol4 master currently **contains 5 entries the new guards would now exclude** — the four `&FILE`
source-identity-sensitive conformance witnesses (`k09`, `k11`, `k30`, `k32`) and one fuzz
nondeterministic-crasher. Dedupe cannot remove them (Law 2's own point). They need a **deliberate surgical
removal by whoever owns snobol4**, explicitly *not* a clean rebuild — and the safe procedure for that does not
exist yet.
