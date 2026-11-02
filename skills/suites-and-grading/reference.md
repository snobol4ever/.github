# Suites and grading: the reference

Verified 2026-11-01 against the harness (`corpus_suite_harness.py` subcommands `capture-oracle-refs convert convert-blocks run partition extract extract-family pin-ref extension-ref extension-check list smoke`), the corpus and `/home/resources/progress/`. Consolidated from ARCH-SUITE-PARTITIONS and ARCH-PROGRAM-LEDGER, retired (`.github/RETIRED-ARCH-PAGES.tsv`).

## 1. The stored partition (CEO-1676)

A partition is built once from the attribute table, committed beside it, and looked up by name at run time (a query per landing selected whole languages). Features: a feature marked by more than half the entries is ubiquitous and belongs to the core; the rest are distinctive. The core: the entries covering every distinctive feature at least three times (`--core-k 3`), most-featured first; a table with no distinctive feature takes one representative per cluster, capped at a tenth of the suite. Shells: every entry marking feature F. Clusters: each non-core entry in the cluster of its rarest feature (else its family column, else its directory). Chunks: clusters packed whole, largest first, at most `--chunk-entries 100`; by seconds once runners record `secs` (`--secs results.tsv --suite-key K`). Deterministic: the same table gives the same file byte for byte. Runners take `--partition core|shell:<feature>|chunk:NN|entry:<name>`, write progress rows per program, and never write a suite row from a subset; a suite row is assembled from the latest per-program readings and names its oldest chunk tree.

## 2. The program ledger's three axes (the cto, 2026-09-11)

Every program is accounted on three independent axes, and UNKNOWN is a value, never zero: COMPLETENESS (its feature vector, or NONE, or UNKNOWN), CORRECTNESS (PASS, FAIL, an exclusion class with its measurement, UNGRADED, or a ruled deferral), SPEED (an instruction-count multiple per rival, or UNPROVEN, NOT-A-BENCHMARK, UNKNOWN). A program is a FILE (a repo path) or a RUNGS ENTRY (a named entry inside `tests/<lang>/ALL.<ext>`); a file absorbed into a master keeps both identities while it survives. A ledger is derived live by globbing the tree and joining the sources, never hand-maintained; it refuses rc 2 when a source is missing rather than print a partial table. A deferral is a ruling Lon gave, printed beside the pass line, never subtracted in silence. (The `OUTSIDE_CLPFD` deferral class is retired, CEO-1966.)

## 3. The kernel convention (CEO-567, CEO-1221)

A kernel is a pristine source that is the meat of the test; wrapping and messaging are generated around it by the harness, never hand-edited in, so the kernel compared across engines is byte-identical by construction; every program has a ref. Since CEO-1912 and CEO-2035 the speed measure is the instruction count of the wrapped run (skill `speed-measurement`), not the 2026-09 three-angle wall clock.

## 4. Who runs what

- The lander: one program both modes, `test_feature_reps.sh <lang> <feature>` (at most eight representatives), `test_smoke_<lang>.sh` for every language touched (all eight for shared code), then `s4e_test_request.sh`; never a board.
- The coo: the round robin (`loop8.sh`) and tier 1 (`tier1.sh`) in `s4e-grader.slice`, the verifier reds, the test requests, the boards, the blocking set (`make test`), the emission identity, the suite rows, the textual banner.
- Refs: `util_ref_mint.sh` and `util_add_ladder_witness.py` cut a witness's ref from the oracle (twice); `corpus_suite_harness.py capture-oracle-refs` for a table.
