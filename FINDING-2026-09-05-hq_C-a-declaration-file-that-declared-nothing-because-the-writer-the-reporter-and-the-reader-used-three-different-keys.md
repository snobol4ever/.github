# FINDING — prolog's MODES.tsv declared 39 families and bound 2, because the tool that WRITES it, the tool that REPORTS on it, and the tool that READS it used three different keys

**Seat:** hq_C · **Date:** 2026-09-05 · **Landed:** SCRIP `92f459d86`, corpus `975fee2ee`, harness `29ef4cbc3`

## THE BRIEF WAS RIGHT ABOUT THE CONCLUSION AND WRONG ABOUT THE CAUSE

Routed as: *"2 declared families route 134 RUN entries to `ast` — a false green."* Measured, that mechanism does not exist. All 134 `ast` entries **are** `family=parser`, correctly declared, and `_modes_for()` routes to `ast` **only** on an explicit `ast` declaration — an UNKNOWN entry falls through to the *stricter* m3,m4 run path. UNKNOWN could not hide a red; it could only over-grade.

The board *was* overstated, so the conclusion held. But the cause was somewhere else entirely, and the cause is what a fix has to follow.

## THREE DEFECTS, ONE SYMPTOM

`read_modes_decl()` keys MODES.tsv on ALL.csv's **`family`** column. Then:

1. **The writer used `origin`.** `additive_absorb()` wrote the sidecar from `modes_for_origin`, keyed `fam + "__" + name`. Every additively-absorbed family got a declaration matching nothing — inert, and indistinguishable from a real one. **37 of prolog's 39 keys were this.**
2. **The writer also ate the file's law.** `_additive_write_sidecar_merge()` skipped every line without a TAB — i.e. every comment — then rewrote the file from the surviving pairs. Each run silently deleted MODES.tsv's own governing text: the "DECLARED, NEVER DERIVED" ruling *and* the per-line `(evidence)` column that ruling **requires**. The file I found had 39 bare keys, no law, no evidence, and nothing in it said anything had been removed.
3. **The reporter named a third vocabulary.** The UNKNOWN reporter printed `origin.split("__")[0]` — an origin *prefix* — while the consumer keys on `family`. When those differ it printed a string that **could never be a valid key**.

⭐ **So the 37 orphaned keys were not carelessness. A tool told a human exactly what to write, and what it told them to write could not work.** Defect 3 manufactured the operator error that defect 1 also produced mechanically, and defect 2 erased the evidence column that would have made either visible.

⭐⭐ **AN ORPHANED KEY IS WORSE THAN AN ABSENT ONE.** An absent family is UNKNOWN and reports itself. An orphaned key is UNKNOWN **that looks answered**, so nobody goes looking. A file can be 95% decorative and read, to every human who opens it, as complete.

## THE FOURTH DEFECT — THE FLAG THAT DID THE OPPOSITE OF ITS OWN `--help`

`--by-modes-column`'s help: *"grade each entry by the `modes` column ... instead of grading every entry the same way."* For the run population it did precisely the opposite — the column only ever chose ast-vs-run, and every run entry was then graded with the **caller's** `--modes`.

Measured: 19 of prolog's 28 per-rung runners grade `--modes m3` **only**, so 83 entries were executed in m4 by the master and counted as m4 passes in a mode no runner claims.

```
before   m3 pass=390 fail=84      m4 pass=390 fail=41     (m4 denominator unstated, read as 477)
after    m3 n=477 pass=390 fail=84  m4 n=394 pass=309 fail=41
```
⭐ **The FAIL counts are identical.** Nothing was hidden — the error was entirely in the m4 *population and pass count*. A reader dividing by `total` got a rate over a denominator that did not exist, which is why each mode now prints its own `<m>_n`: a board that changes its arithmetic silently is the same defect one level up.

## MEASURED RESULT

| | before | after |
|---|---|---|
| MODES.tsv keys that bind | 2 of 39 | 67 of 67 |
| entries covered by a declaration | 374 | 531 of 649 |
| families with no runner, left UNDECLARED rather than guessed | — | 85 |

Prolog master, declaration repaired and per-entry modes honoured: 649 entries · 134 ast-graded · 515 run-graded · m3 n=515 pass=430 fail=82 crash=3 · m4 n=432 pass=349 fail=39 crash=3.

**Control arm** (this harness is shared by every language) — SNOBOL4 master over 12 shards on the same tree: total=1842, m3 n=1842 pass=1795 fail=1, m4 n=1842 pass=1795 fail=1 (`simple_output_67`, hq_P's lane). The snobol4 population is unchanged, as no snobol4 family declares a narrower mode set.

## A NOTE ON HOW THIS WAS MEASURED AT ALL

The first three attempts to grade a master suite in this session were worthless and I did not notice fast enough: one graded a desynced `ALL.ref`, one was killed by its own 2400s timeout under fleet load, one correctly refused on the stale-binary guard. The suite runs 1801+ entries serially and the box carries 20 seats.

`run --shard k/N` already exists, partitions the suite exactly once, and its boards **sum** to the monolithic board. Eight shards return in about a minute what one serial call had not finished in seventy. ⛔ **The instrument had the affordance the whole time; I serialized anyway and then waited on it.** A gate that takes an hour does not get run before a push — so an unshared serial board is not just slow, it is a gate that quietly stops being used.
