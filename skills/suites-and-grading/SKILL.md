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

## 5. DESIGN-PLAN batch-grader: the grader moves into SCRIP (the cio 2026-11-05 on Lon's word; the SCRIP side CTO-515)
- **Lon's word (the cio's window, 2026-11-05 14:5x CST, verbatim)**: "For the test harness, you should move INTO SCRIP. Let scrip run a list of source files on the command line, and reset its base memory cleanly each time. Maybe with a new MMAP and memset clear etc. Should that not run blazingly fast?" MEASURED (the cio, `perf stat -e instructions:u`, SCRIP 52f53c466): one scrip run of a one-line program 7.4 M instructions; one harness run of ONE SnoRungs entry in m3 19.2 G; the program is under one percent of grading it.
- **The steps**: `corpus/tests/shared/batch_grader/STEPS.tsv` (eight steps, nine witnesses with refs cut from `sbl -bf` and icont/iconx, bg08's `.expect` for the hang the oracle cannot answer); `harness/scripts/test_design_batch_grader_steps.sh --list | --step N | --cut`. Executors: hq_runtime steps 1-4 and 6, the coo 5 and 7; one row per step. A scrip refusal of the switch reads RED, never REFUSED.
- **The list file** (`scrip --batch LIST --record FILE`, `--compile` for mode 4; never bare names, since several files on the command line are one polyglot document's sections, CTO-511): one row per program, tab-separated `name source stdin stdout stderr heap_kb stack_kb timeout_s [argv...]`, an empty stdin cell is /dev/null. **The record** (one row per program, list order): `name rc kind secs brk_kb`, kind one of RAN HANG CRASH REFUSED, brk_kb the row's sbrk(0) delta, 0 on every row.
- **The reset between rows (CTO-515)** is a restore of the pristine image, never a census of named statics (827 writable statics in libscrip_rt.so today, wrong by one at every landing). At --batch start, after the constructors, the loop snapshots every writable PT_LOAD segment of scrip and libscrip_rt.so (dl_iterate_phdr; 5.9 MB + 4.5 KB today), the mapping set (/proc/self/maps) and the fd set (/proc/self/fd). Between rows: fflush; munmap every mapping not in the baseline; remap the fixed windows (RT_PIN_BASE, RT_GVA_VA) with MAP_FIXED fresh anonymous pages; memcpy the image back; close every fd not in the baseline; the per-row set-up main does for one file (declared -d -s, stdin stdout stderr by dup2). The loop then re-reads the mapping set and refuses the batch if it differs from the baseline. The loop's state is ONE record g_batch outside the restored range (STATE-GLOBAL, CTO-501). g_runtime, g_lower and g_stage2 are inside the image; the single-file resets (rt_proc_reset, g_bb_alpha_seq_reset, proc_collect_reset, gva_collect_reset) are not the batch reset.
- **One exit**: every `exit(` on the run path becomes `rt_exit(rc)` and the `exit(` is deleted; rt_exit flushes, writes the record row and siglongjmps to g_batch when armed, else exits; the code is the oracle's (&CODE, the ball's exit_code). **The handlers**: SIGALRM SIGSEGV SIGBUS SIGFPE SIGILL SIGABRT on one sigaltstack, SA_ONSTACK|SA_SIGINFO, per row; setitimer ITIMER_REAL in timeout_s is the bound (not a measurement), kind HANG; a signal is kind CRASH and the batch goes on.
- **The kernel**: the row function is the one place a program runs under a fresh image; the persistent kernel (CTO-512's next level) is the same loop with the reset off; `k_run_cell`'s fork per cell retires then.

## 6. The oracles and the manuals (moved from CLAUDE.md 2026-11-05)

Every ref is cut from the language's oracle through its accessor in `harness/scripts/lib_oracle_flags.sh`, never a bare path, and through `util_oracle.sh` under `timeout -k 5` (one run slot, the answer cached by the bytes): SNOBOL4, Snocone and Rebus `sbl -bf` (`sbl_correctness_bin`, `/home/resources/x64/bin`); Icon `icont`/`iconx` (`icont_bin`, `iconx_bin`, Arizona 9.5.25a, semicolons required); Unicon `unicon_bin()` (13.3); Prolog swipl 9.0.4 (`swipl_bin`), GNU Prolog 1.6.0 (`gprolog_bin`, `gplc_bin`), XSB 5.0.0 (`xsb_bin`); Pascal `fpc -Miso` (3.2.2); Raku rakudo 2026.05 (`rakudo_bin`; the `raku` on PATH is 2022.12 and is not the oracle). `ls` the oracle before trusting an all-FAIL table: a missing oracle prints a plausible all-FAIL. Manuals: `/home/resources/manuals/<lang>/`; read the manual before ruling on a builtin or a syntax. A package program runs through its runner `test_<lang>_<pkg>_suite.sh` with `S4E_CHUNK=entry:<name>`; a master entry through `corpus_suite_harness.py run <ALL.ext> <ALL.ref> --lang <lang> --modes m3,m4 --partition entry:<name>`; a rung through `test_<lang>_ladder.sh --to N | --only N`. `perf` is the launcher `~/.local/bin/perf` (`perf --version` 6.8.12; the `/usr/bin/perf` shim warns for kernel 6.17 yet the counter works; never `apt install`).
