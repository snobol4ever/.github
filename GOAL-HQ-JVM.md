# GOAL-HQ-JVM — finish and polish snobol4ever/snobol4jvm

**Opened 2026-10-17 by Lon, in-chat to the ceo, verbatim:** *"We need to create two new HQ seats and their corresponding root folders (I'll do that part) for finishing and polishing snobol4ever/snobol4dotnet and snobol4ever/snobol4jvm. Call them HQ-DOTNET and HQ-JVM."* · *"These two HQ's will certainly need to be fully apart of our fleet, they just happen not to be SCRIP."* (GOAL-CEO CEO-1817)

- **Seat:** HQ-JVM, identity `hq_jvm`, root `/home/claude_jvm`, officer the cfo.
- **Repo:** `snobol4ever/snobol4jvm`, a SNOBOL4/SPITBOL implementation for the JVM in Clojure (Leiningen project `SNOBOL4clojure` 0.2.0).
- **Mechanics:** in the root's `CLAUDE.md` (from `.github/HQ-JVM-CLAUDE.md`).

## LIVE CURSOR

- **2026-10-18, cures and SnoBench: snobol4jvm `c9ccfba`, harness `96fbbe3`.**
  - **Engine cures, each red first against the oracle, then green; `lein test` 2026 / 0:**
    - `abc0977`: `&ALPHABET` is the 256-character string.
    - `27acf35`: exponentiation as SPITBOL does it. Integer `**` integer stays an integer; `^` and `!` are synonyms; `0 ** 0` is error 018 and overflow is error 017; a negative exponent gives a real.
    - `c9ccfba`: a real prints as SPITBOL prints it: 15 significant digits, `2.` when integral, `0.<digits>e±N` outside 0.1 ≤ |x| < 10^15. `env/sstr` is the one value-to-text conversion for OUTPUT, TERMINAL, channels, concatenation and `STRING()`.
  - **SnoRungs chunk 1 re-graded at `c9ccfba`: 76 / 100** (was 67), 1 m 45 s.
  - **SnoBench under snobol4jvm** (`bench_snobol4jvm.sh`, harness `96fbbe3`, run at `abc0977`, load 8.2 → 3.6):
    - **12 of 23 kernels print their `.ref`.**
    - **Warm x is 0.0011 to 0.0082 on the 9 kernels that time:** snobol4jvm's interpreter is 120× to 900× slower per repetition than official SPITBOL. Each engine ran at its own K, with exit code 0 required.
    - **Cold x is n/a:** sbl finishes inside the 0.01 s clock tick, and snobol4jvm takes 0.7–14 s.
    - **Corrected:** an earlier run read 300 s / K for ten kernels, because killed runs still printed their ref. The exit-code check closed that.
- **2026-10-18, the first snobol4jvm reading is in the one record: snobol4jvm `abc0977`, harness `d230a6f`.**
  - **sno-rungs@jvm: 994 / 1994 (50%):** 955 FAIL and 45 HANG, at tree `d859a74`.
    - Published through `util_score_row.py from-progress --suite sno-rungs@jvm`, which opened the row through hq_dotnet's `--open`. The grid shows it.
    - The `-dirty` stamp is an uncommitted `test/` file, which is not in the jar.
  - **How it was graded** (Lon, verbatim: *"In reality most tests are run ONE AT A TIME, the Rungs are run 100 at a time."*):
    - 20 chunks of 100 from `corpus/tests/snobol4/PARTITION.tsv`, then `core` (34), each `S4E_ENGINE=jvm ... --modes m3 --partition chunk:NN`. Chunk wall times ran 53 s to 14 min.
    - `TIMEOUT=30 S4E_TIMEOUT_RETRY_FACTOR=3`: with the default 120 s and ×6 retry, every snobol4jvm hang costs 12 min.
    - **My error:** I first ran all 1,994 as one pass. It wrote zero rows in 41 min and was stopped.
    - Other suites run one test at a time.
  - **The jvm arm, on harness origin:**
    - `eb5a087`: `run_snobol4jvm.sh` and `build_snobol4jvm.sh`, plus gate arms 9a–9f;
    - `d230a6f`: `--paths`, plus arm 9g.
    - The gate reads 31/31, and each new arm has gone red when its feature was broken in a copy.
  - **Engine cures:** `abc0977` makes `&ALPHABET` the 256-character string. It had been a vector, so `REPLACE(&ALPHABET, …)` threw; Gimpel's `agt_driver` now matches its ref.
  - **Red census by family** (1,000 reds): `simple_output` 84, `arbno_pos_rpos_branch` 49 (9 hangs), `keyword` 29, `arbno_span_pos_branch` 20, `fence_pos_rpos_branch` 19, `user_function*` about 90, `datatype` 13.
    - Seen in chunk 1: `**` / `^` exponentiation, real formatting (SPITBOL prints `1.4142135623731` and `2.`), and `(e1, e2)` selection.
  - **SnoBench:** 12 of 23 kernels print their ref under snobol4jvm. The timing run, with K grown until SPITBOL spends 1 s, is in progress.
  - **Next:**
    - root-cause the reds per entry and mint one row per defect;
    - grade the packages (Gimpel, Budne, AIS) one test at a time;
    - publish SnoBench's multiples with their load.
- **2026-10-17/18, the harness and benchmarks first: snobol4jvm `d859a74`, harness `4679767` + four unpushed scripts.**
  - **Lon, in-chat to hq_jvm, verbatim:** *"The suite banner should represent the snobol4jvm program, not SCRIP."* · *"I suspect getting the test harness and benchmarks to run is the first order of business."* That puts the engine arm ahead of the test-equality rows.
  - **The ceo ruled CEO-1822:**
    - the engine is a runner setting, `S4E_ENGINE=scrip|dotnet|jvm`;
    - a port engine's board is its HQ's own;
    - one `results.tsv` and one `SUITES.tsv`, with rows keyed `suite@jvm`;
    - LANES carries `snobol4@jvm`, `snocone@jvm` and `rebus@jvm` for hq_jvm.
  - **Ownership:** hq_dotnet lands the admission row; mine, `jvm-the-runners-take-engine-jvm-...-ceo-1822` (rank 0, claimed), lands the jvm arm on it. My `GRID_TABLES` and `/home/resources/progress/snobol4jvm/SUITES.tsv` are a stopgap second board, replaced when the `@jvm` rows land.
  - **On origin (snobol4jvm):**
    - `25e6035`: `-main` runs the interpreter. The command line had run the Stage 3 VM, which drops every statement after a `DEFINE`'s goto; under it, 15 of 15 Gimpel drivers printed nothing.
    - `d859a74`: the uberjar AOT-compiles `core`. A start takes 1.4 s instead of 4–9 s, at about 300 MB; no class names collide under case folding.
  - **The jvm arm, measured, in my harness clone, unpushed until the admission lands:**
    - `build_snobol4jvm.sh`: runs `lein uberjar`, then records an AppCDS archive. A start then takes about 1.0 s at a quiet load.
    - `run_snobol4jvm.sh`: hq_dotnet's calling shape (`[-dNk] [-sNk] [-u STR] name.sno [-- args]`); `--binaries` refuses rc 2 on a stale jar; the JVM's log stays off stdout.
    - `board_snobol4jvm.sh`: to be rewritten onto the shared writers.
    - `bench_snobol4jvm.sh`: grades SnoBench's 23 kernels against `.ref`. It times them against official `sbl -bf`, cold as a process and warm as the (T(K) − T(1))/(K − 1) difference of the generated iter wrapper, and reports the bare `x`.
    - The draft engine mode for `corpus_suite_harness.py` is set aside at `.scratch/jvm-engine-mode-draft.patch`.
  - **Scratch readings (not in the record):** AIS **0 of 8** in 13 s. It is a real witness: `ENDING` prints nothing where `sbl` prints `BASH/BASE/BATHE/...` on the same stdin. Gimpel, Budne and SnoRungs are grading.
  - **Next:** land the jvm arm on hq_dotnet's admission; grade sno-rungs@jvm; run SnoBench; then cure the reds, one defect per commit.
- **2026-10-17, first sitting, continued: snobol4jvm `05a686d`, .github `fda47100`.**
  - **The banner** (Lon, in-chat to hq_jvm, verbatim: *"The test suite banner is wrong for this seat, since JVM is only SNOBOL4 and Snocone and Rebus."* · *"The test suite banners have the wrong languages."*): `util_suite_banner.py` `grid()` now keeps only the langs `GRID_LANGS` names for the seat. hq_jvm reads 16 suites (snobol4, snocone, rebus); every other seat is unchanged. Those rows are still SCRIP's measurements, not snobol4jvm's. snobol4jvm has no Rebus front end.
  - **The instrument:** row `jvm-every-test-namespace-fails-a-false-equality-written-the-way-the-suite-writes-it`, rank 1. Its mutant DONE-WHEN takes each test file's own `ns` form plus `(is (= 1 2))` and reads **21 of 56 failing**, so 35 are vacuous. Of those, 34 shadow `=` with a warning and `test-operators` does it silently. The earlier "33" was a miscount.
    - Its cure (an `ns` form that excludes the SNOBOL4 operators) turns `lein test` red with the 366 real failures. Those are then carried by the rank-2 and rank-3 rows.
  - **The tree:** `lein test` leaves `openo.tst`, `test.bin` and a file named `|cat >popen2.dat` behind; the engine has no pipe support. Row `jvm-lein-test-leaves-the-snobol4jvm-tree-as-it-found-it`, rank 4.
  - **The lein row's receipt** is written in its ledger.
- **2026-10-17, first sitting: snobol4jvm `8923cd8`. The suite reads green, but 285 of its tests are red underneath.**
  - **Done:**
    - Row 0 (symlinks), `407cc01`: the 140 lower-case `.inc`/`.in` links in `corpus/gimpel/SNOBOL4` are now byte-identical real copies (cmp: 140 of 140). The symlink gate reads OK.
    - Row 1 (lein test), closed by its DONE-WHEN: Leiningen 2.13.0 is in `~/.local/bin`, on OpenJDK 21.0.11. `lein test` reads **2,022 tests, 4,246 assertions, 0 failures, 0 errors, in 68 s**; the README claims 1,896 and 4,120.
  - **The finding: that green is hollow.**
    - 34 test namespaces refer `SNOBOL4clojure.core :all` with no `:exclude`, so SNOBOL4's IR-building `=` replaces `clojure.core/=`. The run prints 34 `WARNING: = already refers to` lines, one per namespace. `test-operators` does the same silently.
    - `(is (= a b))` then returns the list `(= a b)`, which is always truthy. `clojure.main -e` shows `(is (= 1 2))` returning `(= 1 2)` with no FAIL.
    - In a scratch worktree, with the 1,654 such lines in 31 files rewritten to `clojure.core/=`, the suite reads **366 failures in 285 tests, 0 errors**.
  - **Rows minted:**
    - Rank 2, one per large namespace, each closed by `lein test <ns>` printing no shadow warning and 0 failures: csnobol4-suite 101, sprint12 40, cooper 28, t_spitbol 28, worm1000 20, t_gimpel 16, t_aisnobol 12.
    - Rank 3, `jvm-no-test-namespace-shadows-clojure-equality-and-lein-test-reads-zero-failures`: the other 14 files (40 tests) and the whole-suite truth.
  - **Next:**
    - Work the rank-2 rows: for each namespace, compare for real, then judge every red against `sbl`.
    - Choose `sbl`'s case-folding switch and record it under RULINGS.
    - Then measure the corpus table (item 3 of the sitting plan below).
- **2026-10-17 — the seat opened.** The ceo found, at `f35d392`:
  - OpenJDK 21.0.11 is installed, but there is no `lein`, no `clojure` CLI and no `~/.m2`, so nothing can build yet.
  - The README claims "tests 1,896 / 0 failures". The last commit adds `test_csnobol4_suite.clj`: 126 tests, 116 Budne and 10 FENCE.
  - The working tree is clean and current with origin.
- **First sitting:**
  1. Install Leiningen for this user, run `lein deps` and `lein test`, and record the measured count here.
  2. Mint one row per failing test: owner `hq_jvm`, DONE-WHEN the failing test.
  3. Measure the SPITBOL agreement over `corpus/` and write the table here: the master `tests/snobol4/ALL.sno` entries, the benchmarks, the demos and the SNOBOL4 packages, each run under snobol4jvm against its `.ref`. Choose the oracle switches and record that choice.
  4. Mint the reds and cure them one per commit, before any polish.

## THE GOAL, IN ORDER

1. **Correct:** every test passes, and every corpus program the oracle answers matches its ref.
2. **Polished:**
   - nothing generated tracked (`target/`, class files);
   - a clean `lein check`;
   - a README whose badges and numbers match a run you made.
3. **Measured:** benchmark numbers against official SPITBOL (`/home/resources/spitbol-bench-oracle/sbl`), quoted as the bare multiple `x` (reference time over this port's time), each with its load stamped and the JVM's warm-up stated.

## RULINGS

- The oracle wins over this project's own behaviour unless Lon rules otherwise. Record every such ruling here with its date and words.
- **Oracle switches, hq_jvm's choice (2026-10-17):** correctness `/home/resources/x64/bin/sbl -bf` and timing `/home/resources/spitbol-bench-oracle/sbl -bf`.
  - `-b` suppresses the signon; `-f` does not fold source case. That matches snobol4jvm, which never folds, and the corpus refs, which are cut from `sbl -bf`.
- **2026-10-17, Lon, in-chat to hq_jvm:** *"The test suite banner is wrong for this seat, since JVM is only SNOBOL4 and Snocone and Rebus."* · *"The suite banner should represent the snobol4jvm program, not SCRIP."*
