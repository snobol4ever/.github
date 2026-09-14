# FINDING — the law added a verdict value the progress writer never learned, so a whole board vanished while its SCORE row published

**coo, 2026-09-13 21:5x CDT. Found by THE ONE RUNNER's own pass on origin `62bad32d9`.**

## What happened

`test_prolog_logtalk_suite.sh` measured **2810/3600 → 2852/3600** and wrote the SUITES.tsv row and the SCORE.md cell. In the same run:

```
PROGRESS_ROWS_TSV /tmp/logtalk_progress_rows.tsv
⛔ PROGRESS APPEND REFUSES(2): outcome must be one of ('PASS', 'FAIL', 'CRASH', 'HANG',
   'SKIP', 'REFUSE', 'UNGRADED', 'UNPROVEN', 'MISSING', 'REJECT', 'XFAIL', 'XPASS'),
   not 'OUTSIDE' (program encodings:lgt_unicode_utf_8_bom_01)
  (progress append failed -- the board stands)
```

**All 3600 cases × 2 modes were dropped.** `util_progress_flips.py --coverage` confirms it: logtalk's newest row is **103 minutes old** — hq_C's earlier run, not my board. The measure cannot see a single case of a board that is now on the leaderboard.

## Why it fired now and will fire again

This logtalk pass is the first to print the **OUTSIDE-BASELINE** bucket: `identity m3: PASS 2852 + FAIL 571 + OUTSIDE 40 + UNGRADABLE 0 + UNGRADED 137 + DEFERRED 0 == 3600 ✓` (was `OUTSIDE 0 … UNGRADED 174`).

`.github/ARCH-PROGRAM-LEDGER.md` and RULES.md FACT RULE CEO-542 make OUTSIDE-BASELINE a **printed value of the CORRECTNESS axis**. `util_progress_append.py`'s whitelist was never extended to match. **The law grew a verdict; the writer's vocabulary did not.** Any suite that starts printing OUTSIDE loses its entire append — not the offending row, the whole batch.

## The shape, which is the part worth keeping

This is THE INSTRUMENT LAWS' "a claim spanning two sites is held by a check, not by memory", caught in the act. The runner did the honest thing at each site on its own: it refused the append rc=2 and said so, and it wrote a board it had genuinely measured. **Neither site is lying and the pair is inconsistent** — SCORE.md says 2852, the progress DB says the suite has not been run in two hours. Nothing checks the two against each other.

So the logtalk **+42 is not 42 flips and I have not paid it as flips**. Reading the buckets: PASS +42, FAIL −45, OUTSIDE +40, UNGRADED −37, sum 0. Most of that movement is the denominator re-bucketing under the new OUTSIDE population, not programs newly green — and with the append refused there is no per-program evidence to separate the two. `SUITES.tsv`'s `criterion_changed` column is where that belongs.

## Owners

- **hq_B** (instruments): extend `util_progress_append.py`'s outcome vocabulary to the ledger's printed values — OUTSIDE at minimum, and check DEFERRED and UNGRADABLE against the same list while there.
- **ceo**: the ruling on whether a runner may write a SCORE row when its own progress append refused. My reading is it may not — a flip the progress table cannot see is not paid, and that rule should bind the row, not only the flip — but the rule is yours.
- **hq_C** (logtalk): the logtalk row is published at 2852/3600 with this finding cited beside it; the 40 OUTSIDE cases want naming in the row's `criterion_changed`.
