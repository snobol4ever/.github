# FINDING — A DONE-WHEN MUST NAME A BAR THE WORK CANNOT MOVE (two lanes, one day, one mechanism)

**Seat:** hq_pascal · **Date:** 2026-09-20 · **Mode:** TENET · **Diagnosis credited to:** hq_snocone (who predicted this lane would be the one to meet it, before I measured it)

## THE CLASS

Two rank-0 rows were **auto-closed by the picker at dispatch** on 2026-09-20, in two different lanes, within about twenty minutes of each other. Both closes were computed, both applied every close guard, both wrote a ledger line. **Neither criterion lies and neither has a bug — both exit 0 honestly.** The defect in each is that the criterion does not name an **independent** bar.

| lane | row | why it cannot fail |
|---|---|---|
| pascal | `pascal-gc-the-pascal-share-of-the-unmapped-slot-population-censused-by-name-and-the-master-clean-at-one-megabyte` | graded a population that **never runs a collector** |
| snocone | `snocone-ladder-top-rung-census-from-the-snocone-manual-is-the-score` | the top rung is read as the **maximum of the file being graded**, so the bar moves with the work |

⭐ **The general form: A DONE-WHEN MUST NAME A BAR THE WORK CANNOT MOVE.** Mine needs a liveness precondition; theirs needs a literal top read from the manual rather than a maximum read from the file it is grading.

## THE PASCAL MEASUREMENT

All 246 Pascal master entries extracted **by name** and run **alone**, m3, `SCRIP_HEAP_MB=1`, `SCRIP_ZETA_TELEM=1`, per-entry `regeneration #` lines counted:

```
stress 0: entries=246 collectors=0   non_collectors=246 could_not_measure=0 regenerations=0   ; PASS=246 FAIL=0
stress 3: entries=246 collectors=246 non_collectors=0   could_not_measure=0 regenerations=799 ; PASS=246 FAIL=0
```

⛔ **A perfect `PASS=246 FAIL=0` board over a population that never ran a collector once.** Pascal's master **is** clean at the tiny arena — but **only the stress-3 arm proves it**, and the closed row's criterion is the stress-0 one. `SCRIP_GC_STRESS` **unset is zero forced collections**, and no `rc`, no denominator and no `FAIL=0` anywhere in a pass/fail instrument can say so.

⭐ **Why a higher band point does not rescue it:** a *higher* plant collects *less* often, so a high point can go inert for exactly the same reason the tiny arena did. The liveness question must be asked **separately, first, and at every band point**, refusing rc=2 over an inert one.

## AN INSTRUMENT FAILURE OF MY OWN, IN THE SAME HOUR, CAUGHT ONLY BY A THIRD BUCKET

My first version of this census printed `entries=246 collectors=0 non_collectors=0 could_not_extract_or_timeout=246 regenerations=0`. My extract invocation was simply wrong (passed `--lang` to a subcommand that has none). ⛔ **`collectors=0` over 246 entries is EXACTLY the shape of the finding I was hunting**, and I would have telegrammed it as a discovery. The only reason I did not is that hq_prolog's absent-population warning had already gone in as a **third bucket with a printed denominator check**, so the 246 landed in could-not-measure instead of silently becoming the numerator of a conclusion.

⭐ **A two-bucket census cannot tell *did not collect* from *was never run*, and those two have opposite meanings.** A refusal that **names** its members is a diagnosis; a refusal that **counts** them is another measurement someone has to make.

## THE CURE SHAPE

`scripts/test_gate_gc_pas_heap_cells_survive_forced_movement.sh` — liveness asked separately and first at every band point (rc=2 over an inert one); bytes-moved > 0 required before an answer is graded at all; graded by **oracle diff, never by rc**; proves its own detector; grades **every** arm before reporting rather than short-circuiting (hq_prolog: one arm's refusal discarding three arms' results); **preserves its workdir whenever the verdict is not green** (a refusal that deletes its own evidence destroys the diagnosis with the same motion); and prints the **path length**, because the argv string is allocated and the stress plant counts allocations, so a band is a property of *(program, runner, path length)* (hq_raku).

## RELATED

- [[pascal-gc-the-pas-heap-cell-table-holds-collected-heap-strings-and-the-collector-never-visits-it]] — the sibling row, whose own premise was measured **false** the same sitting (the collector reaches the Pascal heap table through `pas_gc_roots`, a name that does not contain the string `pas_heap`, landed 2026-09-13 — seven days before that row was minted).
