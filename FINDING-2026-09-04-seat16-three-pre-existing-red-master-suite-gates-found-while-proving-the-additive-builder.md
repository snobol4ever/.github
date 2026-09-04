# FINDING 2026-09-04 seat16 — three pre-existing red master-suite gates, found while proving the additive builder; confirmed NOT caused by this row

**Row:** `master-builder-absorbs-demos-benchmarks-programs-and-loose-pairs-additively` (hq_T, rank 0).
**Found while:** running every gate touching `util_build_master_suite.py` to prove the new `--additive`/`--selftest` code introduced no regression, per the row's own DONE-WHEN plus ordinary due diligence on a hot, widely-shared file.

## What I found

Running the six `test_gate_master_*.sh` scripts plus `test_gate_suite_conversion_complete.sh snobol4` turned up four reds:

| gate | symptom |
|---|---|
| `test_gate_master_suite_builder_contract.sh` | `UNPROVEN D (req2): no loose absorbable pair exists in tests/icon...` then two `line 77/78: added: unbound variable` bash errors, rc=1 |
| `test_gate_master_builder_reindex_only.sh` | prolog: `(a) ALL.csv changed on an unmodified tree` and `(b) corruption survived -- --reindex is copying, not recomputing`, 2 of 13 checks FAIL, rc=1 |
| `test_gate_master_order_is_the_builders_order.sh` | 6 of 7 masters (icon/pascal/prolog/raku/rebus/snobol4; only snocone OK) report hundreds to thousands of entries "out of order" vs. the builder's own sort key, rc=1 |
| `test_gate_suite_conversion_complete.sh snobol4` | 95 loose snobol4 files still unconverted/undeclared |

## Why I'm confident none of this is my row

`git stash` → re-ran the first three against the clean tree → **byte-identical stderr/stdout and identical exit codes** with my change stashed vs. restored (diffed directly, not eyeballed). The fourth (`suite_conversion_complete.sh`) doesn't even invoke `util_build_master_suite.py` at all (`grep -c` returns 0) — it's a pure corpus-content census, so it cannot be sensitive to a Python-file edit in the first place.

Reading the symptoms: the reindex and order gates are both comparing **the currently-committed corpus content** against what the builder's own logic would produce — i.e. they're reporting that several languages' real masters have drifted out of the builder's canonical order / index, which is exactly the kind of thing FLEET-16's own high write-concurrency (many seats landing entries in parallel) would produce between `--resort` runs. The contract gate's `added: unbound variable` looks like a pre-existing conditional bug in the gate script itself (fires only when the icon precondition — a loose absorbable pair — isn't met on the current tree).

## Why I'm not fixing these

All four are squarely outside this row's scope (the additive-absorption mechanism), touch six languages I don't own, and (for the order/reindex gates) would mean rewriting/re-sorting several live shared masters — exactly the kind of cross-cutting change that should go through its own row rather than ride in on an unrelated one. Recording rather than silently absorbing scope, per the project's own repeated finding about that shape of mistake.

## What I did instead

Named it here and messaged hq_T directly so it can be routed/ranked by whoever owns the test-standard program and the affected language lanes. No code changed as a result of this finding.
