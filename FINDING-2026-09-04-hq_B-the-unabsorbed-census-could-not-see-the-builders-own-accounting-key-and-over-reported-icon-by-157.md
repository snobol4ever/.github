# FINDING 2026-09-04 hq_B — the unabsorbed census could not see the builder's own accounting key and over-reported icon by 157

**Row:** `icon-every-non-package-source-that-runs-with-output-absorbed-into-the-master-with-oracle-refs`
**Tree at measurement:** SCRIP `ae9ebfc20` · corpus `a0bc89d89`

## The two tools disagreed on one string

`util_unabsorbed_census.py` decides a source is **accounted** when it finds it named in
`corpus/tests/<lang>/ALL.excluded.txt`, and looked it up three ways: bare basename (`alt_arith`),
filename (`alt_arith.icn`), corpus-relative path (`tests/icon/parser/alt_arith.icn`).

`util_build_master_suite.py` writes that file keyed by **FAMILY** — the path under `corpus/tests/<lang>/`
with `os.sep` → `_` and the extension dropped (`discover_pairs`: `fam = rel[:-len(EXT)].replace(os.sep,
"_")`). For that same fixture it writes **`parser_alt_arith`**.

That string is none of the three the census tried. So **every properly-excluded source in a
subdirectory read as OWED**, each one already carrying a reason line the builder had written.

## Measured

| | before | after |
|---|---|---|
| icon owed | **219** | **62** |
| all-language accounted | 71 | 228 |

All **157** newly-recognised sources carry a non-empty reason (153 `parser/KEEP.md` keepers, 3
`unresolved/`, 1 `repro/`); **zero** were accounted with a blank reason, i.e. the fix converts no silent
skip into a false pass. The other six languages' numbers did not move — their excluded lists happen to
name only top-level sources.

⭐ **And that is exactly why this survived.** At the top level a family name *is* the basename, so every
source anyone spot-checked matched. The population that would have disproved the rule was the one the
instrument never sampled — the same shape as `command -v` answering *is it on PATH* when asked *does it
exist*, filed twice already in this tree and re-earned here on a different pair of tools.

⛔ `config/MODES.tsv` keys on the family name too (`parser_alt_arith	ast`). The convention was already
project-wide; only the census was outside it.

## Cure landed

`util_unabsorbed_census.py` now derives the family key for anything under `tests/<lang>/` and adds it to
the lookup. Four lines plus the comment block, no behaviour change for any source the census already
matched.

## Two things this fix does NOT reach

**1. The row's own DONE-WHEN cannot pass as written.** It runs

```
python3 scripts/corpus_suite_harness.py run ../corpus/tests/icon/ALL.* --lang icon --by-modes-column ...
```

`ALL.*` expands to six files (`ALL.csv ALL.excluded.txt ALL.icn ALL.in ALL.ref ALL.trace ALL.wantrc`) into
a runner taking two positionals. It exits rc=2 with `unrecognized arguments`, the `grep -qE "FAIL=0"`
finds nothing, and the DONE-WHEN prints **`RED: the master is not FAIL=0 both modes`** — a verdict about
argument parsing, worded as a verdict about the master. It is unfalsifiable: no state of the corpus can
make it green. Should read `ALL.icn ALL.ref`. Verified separately via `board_icon_master.sh`: FAIL=0 both
modes, 751 entries.

**2. A pairless source can never be accounted at all — so census rc=0 is unreachable today.**
`discover_pairs` skips any source with no sibling `.ref`/`.expected` *before* the exclusion list is built
(`continue  # pairless loose witnesses are not board members and are untouched`), so it never reaches
`excluded` and never gets a line. And `ALL.excluded.txt` is **fully regenerated** on every builder run
from that list, so a hand-authored line for such a source does not survive the next build.

That is **48 of icon's remaining 54** owed sources — every `benchmarks/icon` (36) and `demos/icon` (8)
file among them, none of which has a `.ref`. ⛔ The GOAL requires each to be *"NAMED in ALL.excluded.txt
with its reason — never a silent skip"*, and there is currently no mechanism by which that can be true.
Blocks this row and its six siblings. Needs either a preserved hand-authored section in
`ALL.excluded.txt`, or exclusion recorded before the pairing test — a builder change, filed as
`master-builder-accounts-pairless-sources-so-the-census-can-reach-zero`.
