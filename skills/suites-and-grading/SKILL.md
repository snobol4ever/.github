---
name: suites-and-grading
description: How SCRIP is graded: the corpus masters and packages, the runners, corpus_suite_harness.py, results.tsv, SUITES.tsv, exclusions, the coo as the one testing officer. REQUIRED by the skill gate before editing the suite tables or the harness.
---

# Suites and grading

The coo is the ONE testing officer (CEO-1342 as amended): it runs the suites, the boards, the blocking set and the `.s` regeneration, and alone writes suite rows. A lander grades ONE program in both modes and runs the feature reps and smokes; it asks for anything more by test request. Detail is in `reference.md` beside this file.

## 1. The populations

- **The masters**: `corpus/tests/<lang>/` holds one flat container per language: `ALL.<ext>` (every entry, a CONTAINER, never a program), `ALL.ref` (each entry's ref, cut from the oracle; binary to git), `ALL.csv` (the index: entry, feature columns, declared sizes, `compile_args`, `oracle_args`), `PARTITION.tsv`, and `LADDER.tsv` for the construct ladder, beside the container (CIO-55). The one extraction authority is `corpus_suite_harness.py extract MASTER REF NAME OUT`.
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
- **The tests layout** (CIO-24, 2026-11-10): `corpus/tests/` holds one folder per language and a language folder holds its container files and its role files at one level, nothing else (CIO-55: no `config/` folder; `LADDER.tsv` beside the container in every master, the companion search path `ALL.path`; the other six keep `config/` for their other files until their own clean-up); `python3 harness/scripts/util_tests_layout_census.py [--lang L] [--list] [--check]` classes every other tracked file (an orphan pair no cell grades, a duplicate of an entry, a pair the exclusion list names, a program with no ref, sidecars, tables, documents) and names what under `corpus/tests/` is not a language. A program's input is its stdin and its answer is its stdout (Lon 2026-11-10: "each program should have a *.stdout and a *.stdin file, not a *.ref file"): and the container is two groups (Lon: "Let's have two groups, one liner and multi liner. Their storage can then be optimized."): `ONE.<ext>` with `ONE.stdout`, one program and its one line of answer per line number, for an entry that is one program line, one stdout line and no stdin; `MULTI.md` for every other entry (CIO-25; Lon: "How about storing the multi liners in a SCRIPtix MD file using the triple-backticks for a clean delineation." / "This way the files can be viewed nicely."): one section a test, a `## <entry name>` heading, then the program in a fence tagged with the language as Scriptix spells it, a fence tagged `stdin` when the test has input, and a fence tagged `stdout`, so a test's parts sit together; a fence is a line of three backticks or one more than the longest run inside the block, read line-anchored; the harness extracts a section and runs it as an entry, and `scrip` is never handed `MULTI.md` whole (a Scriptix `.md` is one polyglot program); `ALL.csv` stays the one index of both with a `group` column. A directory converts by `corpus_suite_harness.py regroup` (CIO-24 f); until its conversion lands it holds `ALL.<ext>`, `ALL.ref` and `ALL.in`, and the reader takes either.
- **The cycle's inventory** (CIO-22, 2026-11-10): `python3 harness/scripts/util_cycle_inventory.py` prints one line per suite row: the container files (`ALL.<ext>`, `ALL.ref`, `ALL.csv`, `PARTITION.tsv`), entries in the table, the container and the cycle's cells, cell names the container lacks (the harness refuses that cell rc 2), entries no cell names, OWED, and the last finished lap's cells by exit code. `--owed KEY` lists a row's owed programs with the builder's reason; `--check` is the structural verdict, `--check-lap` adds the lap; a row whose every cell is held in `CYCLE.skip` is counted by neither. **OWED** is a program `ALL.omit` leaves out by the builder's own measurement that neither `EXCLUDED.tsv` nor `CONTAINERS.tsv` declares out: the package tables are the denominator (CIO-19), so it is cured by the attribute the deleted runner applied (stdin, `out_files`, `stderr`, a mask row, a CONTRACT key) and absorbed, or declared in `EXCLUDED.tsv` with its class and the row's total moved with a stamp; never left between the two. `ALL.csv`'s `out_files`, `stderr` and `timeout_s` are read by the builder before any oracle run and written back, as the grader reads them. The cycle (`harness/scripts/s4e_cycle.sh`) launches `master` and `pkg` rows of `SUITE_RUNNERS.tsv` only, writes a suite row only when a cell of the lap graded that suite, and re-executes itself at a lap start when the sync changed its text.
- **Stored partitions** (CEO-1676): `util_suite_partition.py build <ALL.csv>` writes the core (every distinctive feature covered three times), a shell per distinctive feature and chunks of at most 100 entries; `check` and `test_gate_suite_partitions_are_current.sh` refuse a table edited without its partition rebuilt. The coo's tier 2 runs the core plus the shells of the features a landing touches (`area_map.tsv`).

## 4. The rules

- **A ref is cut from the oracle, never from our output; no XFAIL.** An oracle that refuses, crashes or hangs gives NO_ORACLE_ANSWER: the program is excluded with the measurement, never counted as debt (CEO-1696/1934). A wrong exclusion costs more than a wrong cure.
- **The denominator identity**: PASS + FAIL + every named exclusion class equals the population the tree ships; no board prints a pass count whose denominator drops programs without naming them.
- **A row exists only while a measurement says so** (CEO-1386); a test that cannot measure refuses rc 2 (CEO-1680); no planted breakage.
- **A benchmark is a test**: every kernel has a ref and is graded for correctness; its speed is an instruction count (skill `speed-measurement`).
- **The masters carry no `.s`**; tests carry no artifacts (CEO-16).

## 5. DESIGN-PLAN batch-grader: the grader moves into SCRIP as `scrip --harness` (Lon 2026-11-05; the cio's plan; the SCRIP side CTO-515 as amended by CTO-522)

The full text of this section (about 6 KB) is in `reference.md` beside this file, under the same heading, moved there verbatim on 2026-11-06 so the skill loads light (Lon: "Go and trim any skill that needs it."). Read it before executing, cutting or ruling on a step of this design.

## 6. The oracles and the manuals (moved from CLAUDE.md 2026-11-05)

Every ref is cut from the language's oracle through its accessor in `harness/scripts/lib_oracle_flags.sh`, never a bare path, and through `util_oracle.sh` under `timeout -k 5` (one run slot, the answer cached by the bytes): SNOBOL4, Snocone and Rebus `sbl -bf` (`sbl_correctness_bin`, `/home/resources/x64/bin`); Icon `icont`/`iconx` (`icont_bin`, `iconx_bin`, Arizona 9.5.25a, semicolons required); Unicon `unicon_bin()` (13.3); Prolog swipl 9.0.4 (`swipl_bin`), GNU Prolog 1.6.0 (`gprolog_bin`, `gplc_bin`), XSB 5.0.0 (`xsb_bin`); Pascal `fpc -Miso` (3.2.2); Raku rakudo 2026.05 (`rakudo_bin`; the `raku` on PATH is 2022.12 and is not the oracle). `ls` the oracle before trusting an all-FAIL table: a missing oracle prints a plausible all-FAIL. Manuals: `/home/resources/manuals/<lang>/`; read the manual before ruling on a builtin or a syntax. A package program runs through its runner `test_<lang>_<pkg>_suite.sh` with `S4E_CHUNK=entry:<name>`; a master entry through `corpus_suite_harness.py run <ALL.ext> <ALL.ref> --lang <lang> --modes m3,m4 --partition entry:<name>`; a rung through `test_<lang>_ladder.sh --to N | --only N`. `perf` is the launcher `~/.local/bin/perf` (`perf --version` 6.8.12; the `/usr/bin/perf` shim warns for kernel 6.17 yet the counter works; never `apt install`).

## 7. DESIGN-PLAN test-cycle: the loops redesigned for 10x (the cto, CTO-522, 2026-11-05; Lon in the cio's window 16:5x, verbatim: "We must speed up the test suite runs by 10x. Yipper skipper!!!" / "CTO is to complete redesign the test suite CYCLE loops."; the coo executes the grading steps, the cio the queue and the tick, the cqo the ledger)

The full text of this section (about 7 KB) is in `reference.md` beside this file, under the same heading, moved there verbatim on 2026-11-06 so the skill loads light (Lon: "Go and trim any skill that needs it."). Read it before executing, cutting or ruling on a step of this design.

## 8. DESIGN-PLAN run-switches: SCRIP reads every master, warms Prolog, runs a package in its own layout, and dialect is one attribute (the cto, CTO-575, 2026-11-10; CIO-59)

The full text is in `reference.md` beside this file, under the same heading: the reader's file fences and dialect column, the one oracle table, the warm parent for the two switches, the package switch `scrip --run-files`. Read it before executing, cutting or ruling on a step of this design (`harness/designs/run_switches/STEPS.tsv`, `test_design_run_switches_steps.sh`).
