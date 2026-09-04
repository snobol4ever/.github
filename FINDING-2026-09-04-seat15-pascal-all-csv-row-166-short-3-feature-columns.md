# FINDING 2026-09-04 seat15 — pascal ALL.csv row 166 (`ladder__rung10_pointers`) is short 3 feature columns

**Measured** building `util_feature_coverage_census.py` (task feature-coverage-census-hundreds-per-feature-and-combinations-all-seven), corpus `990c8db3` (post-2026-09-04 pull):

```
$ python3 -c "
import csv
with open('corpus/tests/pascal/ALL.csv', newline='') as f:
    r = csv.reader(f); hdr = next(r)
    for lineno, rec in enumerate(r, start=2):
        if lineno == 166: print(len(rec)); print(rec)
"
55
['165', 'ladder__rung10_pointers', 'ladder__rung10_pointers', 'ladder', 'block', '0', '33', 'm3,m4', '1', '0', '0', '1', '0', '1', '1', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '1', '0', '0', '0', '1', '1', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '1', '1', '0', '0', '0', '0', '0', '1']
```

Header (`corpus/tests/pascal/ALL.csv` line 1) has **58** fields (8-column prefix + 50 feature columns). File line 166 — the `ladder__rung10_pointers` entry, `rank`=165 — has **55**, i.e. is short exactly **3** trailing feature columns. Every neighboring row (165, 167, …) has the full 58. This is not an artifact of naive comma-splitting: parsed with Python's `csv` module (which correctly treats the quoted `"m3,m4"` `modes` field as one column), so the count is real.

## IMPACT

`util_feature_coverage_census.py` (and, if it exists, any other reader that trusts every row to match the header width) REFUSES `--lang pascal` outright on this row rather than silently reading the 3 missing trailing feature columns as `0` — which would be a **hand-typed / not-filled-by-the-builder-from-source** false zero, exactly the class GOAL-TEST-SUITE-CONSISTENCY.md sec THE STANDARD point 8 rules out ("Absorbed programs count toward coverage only when their feature columns are FILLED by the builder from the source, never hand-typed"). So this one malformed row currently blocks the feature-coverage census for the entire Pascal master, not just this entry.

## CAUSE — not investigated further, flagged not fixed

Not traced to a specific commit or builder code path in this pass (out of lane: Pascal ladder-row content is hq_P's/seat10's, not the instrument row's). Likely candidates, unconfirmed: a builder run that absorbed `ladder__rung10_pointers` before three feature columns existed in the schema and never got backfilled, or a hand-edit that dropped a trailing comma-run. `git log -p -- corpus/tests/pascal/ALL.csv` around the rung-10 pointer-types landing (SCORE.md's Pascal row cites rung10 minted 2026-09-03 by seat10) is the next step for whoever cures this.

## CURE — not a hand-typed patch

The right fix reruns the builder against `ladder__rung10_pointers`' real source so the 3 columns are filled *from the program*, matching this same file's own convention elsewhere — never hand-typed 0s/1s to make the field count agree. Whoever holds the Pascal ladder rows (hq_P lane) is best placed to know which 3 of the 50 feature columns are the trailing ones for this schema version and what the pointer-rung program actually exercises.

Reproduce the refusal directly: `python3 SCRIP/scripts/util_feature_coverage_census.py --lang pascal` (from `/home/claude15`).
