# ARCH-SUITE-PARTITIONS — THE STORED PARTITION OF EVERY SUITE: A CORE, FEATURE SHELLS, BOUNDED CHUNKS

**Opened 2026-10-11 13:0x CDT by the ceo (CEO-1676), on Lon's word, in-chat to the ceo, verbatim:** *"One of the main take-aways concerning test suites, is that subsets need to be identified independent of a query against the attribute file for the long running test suites. So to partition them as major cores, and shells around that core with each major feature broken out. Or some kind of clustered partitioning."* and *"One reason for the subsets on large suites is so they can be run in chunks even when the full regressions are being run in its "spare" time."* The law is RULES.md § ONE TESTING OFFICER clause (9); the instrument is `SCRIP/scripts/util_suite_partition.py`; the artifact is `PARTITION.tsv` beside every suite table.

## 1. Why a stored partition, not a query

Under the three tiers (CEO-1673) the feature subset per landing was computed by querying the attribute rows through the carrier map: a lowerer carrier selected its whole language (about an hour) and a shared node selected every table, so the "subset" was the suite and the red reached its lane hours late. A partition is built ONCE from the attribute table, committed beside it, and looked up by name at run time: `core`, `shell:<feature>`, `chunk:NN`. The lookup costs nothing, the subset is bounded by construction, and the long suites become sequences of bounded chunks the loop runs in its spare time between smokes and feature subsets.

## 2. The partition (what `util_suite_partition.py build <ALL.csv>` writes)

- **Features.** The table's feature columns (everything after the fixed columns). A feature marked by more than half the entries is UBIQUITOUS (`write`, `nl`, `directive`, `procedure`, `package`, `unify`, …) and is not a partitioning feature: it belongs to the core by definition. The rest are DISTINCTIVE.
- **The core.** The entries that cover every distinctive feature at least three times (`--core-k 3`), chosen by the entries marking the most distinctive features first: the suite's representative set, run with every feature subset. A table with no distinctive feature (PAT, the SWI test files, roast, Flake, the spitbol decks) takes one representative per cluster, capped at a tenth of the suite.
- **The shells.** For each distinctive feature F, every entry marking F (non-disjoint; the `shells` column lists each entry's distinctive features). A landing that touches F runs the core plus `shell:F`.
- **The clusters.** Every non-core entry in exactly one cluster: the cluster of its RAREST distinctive feature; an entry marking none clusters by its `family` column; a table without feature columns clusters by the entry's directory (roast's chapters, the SWI directories) or its name family.
- **The chunks.** The clusters packed whole, largest first, into chunks of at most `--chunk-entries 100` entries (a cluster larger than a chunk is split in order). A chunk is the unit of the full regression. Chunks are sized by entry count until every runner records the program's seconds in its progress row (`secs` reads 0 for nearly every suite today, CEO-1676 row (c)); `--secs results.tsv --suite-key K` sizes them by seconds once known.
- **Determinism.** The same table gives the same file byte for byte; `util_suite_partition.py check <ALL.csv>` rebuilds in memory and compares, and `test_gate_suite_partitions_are_current.sh` runs that over every table in the blocking set: a table edited without its partition rebuilt is a red.

## 3. The measured shape (corpus d156f1e51, 2026-10-11)

| suite | entries | features (ubiq / distinctive) | core | clusters | chunks |
|---|---|---|---|---|---|
| SnoRungs | 1980 | 39 (0 / 39) | 33 | 172 | 20 |
| IcnRungs | 904 | 61 (3 / 58) | 26 | 108 | 9 |
| ProRungs | 563 | 38 (3 / 35) | 54 | 61 | 6 |
| RakRungs | 993 | 37 (2 / 35) | 43 | 48 | 10 |
| Logtalk | 3617 | 204 (5 / 199) | 395 | 188 | 33 |
| INRIA | 445 | 74 (4 / 70) | 117 | 49 | 4 |
| ProPuzzles | 268 | 26 (5 / 21) | 18 | 73 | 3 |
| ProRosetta | 512 | 37 (4 / 33) | 41 | 87 | 5 |
| Trealla | 329 | 40 (5 / 35) | 34 | 34 | 3 |
| IPL | 851 | 62 (1 / 61) | 21 | 39 | 9 |
| PasRosetta | 319 | 51 (12 / 39) | 36 | 56 | 3 |
| roast | 1464 | none (clustered by chapter directory) | 136 | 136 | 15 |

The core is 2–11% of a suite with feature columns. ProPuzzles' 1h51m becomes three chunks of about 40 minutes at today's rates and shrinks further once `secs` sizes them; Logtalk's 33 minutes becomes 33 chunks of about a minute.

## 4. How the loop uses it (the coo's rows, CEO-1676)

- **(a) Runners take `--partition core|shell:<feature>|chunk:NN`** (the masters through `corpus_suite_harness.py`, the packages through their runners' shared entry filter), grade only that subset, write progress rows per program as today, and never write the suite's score row from a subset.
- **(b) The suite row is assembled from the latest per-program readings** (`util_score_row.py` learns a from-progress form): a suite's row moves as its chunks are re-read, and it is CURRENT at a tree when every chunk has a reading at or after that tree; the row names the oldest chunk tree beside the newest.
- **(c) Every runner records `secs`** in its progress row (the column exists; `util_progress_append.py`'s contract says "the program's own seconds when the runner knows them, else 0"); then chunks are sized by seconds.
- **(d) The loop cycles the chunks** of every suite in its spare time, one chunk at a time, pre-empted at chunk boundaries by tier 1 and tier 2; tier 2 is `core` plus the `shell:` of each feature the landing's diff marks (through `area_map.tsv`), never more.

## 5. What a seat does with it

Nothing per landing (CEO-1671: one DONE-WHEN). A seat that cures a feature may read its shell's entries by name from `PARTITION.tsv` to pick a witness; it never runs the shell. A landing that adds entries or feature columns to a table rebuilds the partition in the same landing (`util_suite_partition.py build`), or the gate names it.
