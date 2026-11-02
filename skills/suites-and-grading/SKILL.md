---
name: suites-and-grading
description: How SCRIP's correctness is graded: the corpus masters (one ALL.<ext> container per language with ALL.ref, ALL.csv and PARTITION.tsv), the packages and their runners, corpus_suite_harness.py, declared sizes and the compile and oracle arguments, the stored partitions (core, shells, chunks), the progress store results.tsv and the suite table SUITES.tsv and SCORE.md, exclusion classes and the denominator identity, the coo as the one testing officer, test requests, and the program ledger's three axes. Load it before grading a program, reading a score, adding entries or columns to a table, excluding a program, or filing a test request.
---

# Suites and grading

The coo is the ONE testing officer (CEO-1342 as amended): it runs the suites, the boards, the blocking set and the `.s` regeneration, and alone writes suite rows. A lander grades ONE program in both modes and runs the feature reps and smokes; it asks for anything more by test request. Detail is in `reference.md` beside this file.

## 1. The populations

- **The masters**: `corpus/tests/<lang>/` holds one flat container per language: `ALL.<ext>` (every entry, a CONTAINER, never a program), `ALL.ref` (each entry's ref, cut from the oracle; binary to git), `ALL.csv` (the index: entry, feature columns, declared sizes, `compile_args`, `oracle_args`), `PARTITION.tsv`, and `config/LADDER.tsv` for the construct ladder. The one extraction authority is `corpus_suite_harness.py extract MASTER REF NAME OUT`.
- **The packages**: `corpus/packages/<lang>/<pkg>/` (vendored suites with their own tables, `EXCLUDED.tsv` with a reason per row, runners `harness/scripts/test_<lang>_<pkg>_suite.sh` taking `S4E_CHUNK=entry:<name>`).
- **Demos and benchmarks**: `corpus/demos/`, `corpus/benchmarks/` (the only trees with committed `.s`).

## 2. Grading one program (what a lander does)

```bash
python3 ../harness/scripts/corpus_suite_harness.py run ../corpus/tests/<lang>/ALL.<ext> ../corpus/tests/<lang>/ALL.ref --lang <lang> --modes m3,m4 --partition entry:<name>
S4E_CHUNK=entry:<name> bash ../harness/scripts/test_<lang>_<pkg>_suite.sh
bash ../harness/scripts/test_feature_reps.sh <lang> <feature>
bash ../harness/scripts/test_smoke_<lang>.sh
bash ../harness/scripts/s4e_test_request.sh <suite-key> <entry>...        # at most eight; the coo grades
```

`--modes m3,m4` is mandatory; the two modes may diverge and each is graded against the oracle. A program runs at its DECLARED sizes (the entry's heap and stack, CEO-1353/1281); the declared size is a hard cap and out of stack is a bigger declared `-s`, never data moved.

## 3. The record

- **The progress store** `/home/resources/progress/results.tsv`: one row per reading (`ts_utc scrip corpus measurer class suite lang program mode outcome secs note fingerprint config`). A reading on a dirty tree is unread (CEO-2060). Read it with `util_score_row.py from-progress`.
- **The suite table** `/home/resources/progress/SUITES.tsv` (`key ... today_pass today_total tree ...`), shown by `.github/SCORE.md` § THE SUITE TABLE and printed by `.github/scripts/util_suite_banner.py` (the textual banner, verbatim, when Lon asks).
- **Stored partitions** (CEO-1676): `util_suite_partition.py build <ALL.csv>` writes the core (every distinctive feature covered three times), a shell per distinctive feature and chunks of at most 100 entries; `check` and `test_gate_suite_partitions_are_current.sh` refuse a table edited without its partition rebuilt. The coo's tier 2 runs the core plus the shells of the features a landing touches (`area_map.tsv`).

## 4. The rules

- **A ref is cut from the oracle, never from our output; no XFAIL.** An oracle that refuses, crashes or hangs gives NO_ORACLE_ANSWER: the program is excluded with the measurement, never counted as debt (CEO-1696/1934). A wrong exclusion costs more than a wrong cure.
- **The denominator identity**: PASS + FAIL + every named exclusion class equals the population the tree ships; no board prints a pass count whose denominator drops programs without naming them.
- **A row exists only while a measurement says so** (CEO-1386); a test that cannot measure refuses rc 2 (CEO-1680); no planted breakage.
- **A benchmark is a test**: every kernel has a ref and is graded for correctness; its speed is an instruction count (skill `speed-measurement`).
- **The masters carry no `.s`**; tests carry no artifacts (CEO-16).
