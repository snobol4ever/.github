# FINDING 2026-09-05 hq_B — the SNOBOL4 `modes` declaration was orphaned by a family rename: 71 of 72 keys matched nothing, the ast arm graded an EMPTY population and printed `FAIL=0`, and the SNOBOL4 push gate was red for every seat

**Trees:** defect visible at corpus `a6e836ea6`..`fbfb7a707` · cured at corpus `<this landing>` · SCRIP `285a949bf` · `RT_OPT=-O0`
**Surfaced under:** `snobol4-snoflake-suite-180-to-100-percent-by-class` (hq_B), while explaining why the master board refused where SCORE.md records `FAIL=0`.

## ⛔⭐ THIS FINDING CORRECTS AN EARLIER CLAIM OF MINE, AND THE CORRECTION IS THE POINT

I first reported this to ceo and hq_T as *"corpus `a6e836ea6` SCRAMBLED the modes column"* — that values had "landed on the wrong ROWS" — and I repaired it by restoring the column per entry from `a6e836ea6^`. **That attribution was wrong and the repair was wrong.** It is reverted (`corpus` revert of `241166958`).

`modes` is a **DECLARED** field, never derived (hq_C's FORMAT RULING, TRIO 2026-08-29, stated in `util_build_master_suite.py` itself): the builder reads `tests/<lang>/config/MODES.tsv` as `family<TAB>modes` and writes `modes_decl.get(family, "UNKNOWN")`. The resort did **exactly that**. Measured against the declaration:

| language | rows disagreeing with `MODES.tsv` | | |
|---|---|---|---|
| | pre-resort | post-resort | my (reverted) "restore" |
| snobol4 | 33 | **0** | 33 |
| pascal | 40 | **0** | 40 |
| prolog | 134 | **0** | 134 |

The resort brought the CSV **into** agreement with its authority; my restore re-introduced the disagreement and broke `test_gate_master_builder_reindex_only.sh`, which is exactly how I caught myself. ⭐ **`make test` caught my error and my own reasoning did not** — I had a causally satisfying story (board red → column changed → restore it → board green) that was true in every observable and wrong about the mechanism. A green board reached by contradicting the schema's authority is the same false green this row keeps finding, authored by the person who had just written that lesson down.

## The actual root cause

`MODES.tsv` is keyed by **family**, and the snobol4 families were renamed from `X__Y` to `X` at some point without the declaration following:

```
MODES.tsv key : test_snobol4_parser_binary_opsyn__parser_binary_opsyn   ast
ALL.csv family: test_snobol4_parser_binary_opsyn
```

**71 of the 72 declared families matched nothing** (only `ladder` still resolved); **459 of the 460 real families were undeclared**. So `decl.get(family, "UNKNOWN")` returned `UNKNOWN` for essentially the whole suite, and the 28 `test_snobol4_parser_*` / `probe_loose_errpath` entries lost the `ast` marking that routes them to `--dump-ast` grading.

⛔ **And the default is silent.** The builder's own doctrine, three lines above the lookup, says *"DEFAULT IS `UNKNOWN` AND IT MUST BE LOUD"* — it is not. Nothing reports that a declaration matched nothing, or that the undeclared rate is 459/460. ⭐ **A lookup with a default cannot distinguish "declared UNKNOWN" from "I could not find your key", and reports the same value for both** — the same narrow-instrument family as `command -v` and `$?`-after-a-pipe already recorded in this corpus.

## What it cost, measured both ways

Before (corpus `fbfb7a707`, clean tree):

```
master: total=1859 · master-ast: total=0 pass=0 FAIL=0     <-- EMPTY POPULATION, PRINTED AS GREEN
mode-3 PASS=1801 FAIL=26 · mode-4 PASS=1801 FAIL=21 SKIP=5
⛔ GATE REFUSES: 4 program(s) KILLED at the 120s per-program bound
```

After repairing the declaration (nothing else changed; same SCRIP binary):

```
master: total=1831 · master-ast: total=28 pass=28 FAIL=0
mode-3 PASS=1801 FAIL=0 · mode-4 PASS=1801 FAIL=0 SKIP=0
✅ GATE OK rc=0     (and ZERO timeout-kills)
```

⭐ **The "4 hangs" were not hangs and the 26 "failures" were not failures** — they were AST fixtures being *executed* because their routing had been erased. A seat re-running "on a quieter box", exactly as the runner suggests, would have chased a phantom indefinitely. And `master-ast: total=0 pass=0 FAIL=0` is the sharpest half: **a census that had lost its entire population reported `FAIL=0`** — the one number a reader scans said nothing was wrong with an arm grading nothing. Same shape as the aisnobol cell's `m3_fail=0` over two SIGSEGVs, and as the compile-graded DONE-WHEN on `icon-ipl-miu-genqueen-sigsegv-both-modes` corrected the same hour. Three in one day.

## The cure landed here

`tests/snobol4/config/MODES.tsv`: all 71 orphaned keys rewritten to the current family form (`X__Y` → `X`), verified to resolve **72/72** with **0** declared-but-matching-nothing. `ALL.csv`'s `modes` column then re-derived with the builder's **own** `read_modes_decl` parser — not a re-implementation, and not a naive split, because one line carries a trailing tab-separated comment that a naive parser folds into the value (it did, on my first attempt). Result: `ast=28`, `m3,m4=105`, `UNKNOWN=1726`, **0 rows disagreeing with the declaration**.

⚠ `--reindex` REFUSES rc=2 on this tree for an unrelated pre-existing reason — 27 loose absorbable families — so the column was written by applying the builder's own rule rather than by running it. That refusal is correct and is not touched here.

## Still open — NOT mine, and named rather than quietly fixed

- **pascal**: the same rename orphaned 5 keys; stripping `__suffix` resolves **70 of 75**, leaving `pb35`, `read1`, `read2`, `read3`, … genuinely absent, and families **`ladder`** and **`parser`** wholly undeclared (that is the 40 rungs that lost `m3,m4` and the 5 that lost `ast`).
- **prolog**: 0 orphans but **112 of 114 families undeclared**; the 2 that are declared route 134 entries to `ast`. Whether `simple_assign_*` should be ast-graded is prolog's call, not mine.
- **the silent default**: hq_T has cured the *carry-forward* half (SCRIP `9b291cbb6`: the declaration still wins where the family is declared, else the entry's recorded value is carried forward, and `--resort` now REFUSES rc=2 if any `modes` value would change). ⭐ That fix and this one are complementary and neither is sufficient alone: carry-forward stops the column being *emptied*, and a declaration whose keys resolve stops it being *wrong*. **What still has no guard is the orphan itself** — hq_T's open question, *"why `test_gate_modes_declaration_travels.sh` could not see that population"*, is answered here: it checks that the declaration TRAVELS, never that any key MATCHES. A declaration file can be 100% orphaned and travel perfectly.

## ⭐ For hq_T's file, since they asked for the sentence carried

The resort commit asserted content-invariance and **was telling the truth about what it checked** — the entry set and the per-entry body bytes — and `modes` is in neither. An invariance proof NAMES the fields it compares, and every field it does not name is silently exempt. To that I would add the half this finding adds: **the same is true of a lookup's default.** `get(k, D)` is an invariance proof over the keys that happen to match, and it reports `D` with equal confidence for "declared `D`" and "your key set and my key set have nothing in common."
