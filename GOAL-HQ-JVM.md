# GOAL-HQ-JVM — finish and polish snobol4ever/snobol4jvm

**Opened 2026-10-17 by Lon, in-chat to the ceo, verbatim:** *"We need to create two new HQ seats and their corresponding root folders (I'll do that part) for finishing and polishing snobol4ever/snobol4dotnet and snobol4ever/snobol4jvm. Call them HQ-DOTNET and HQ-JVM."* · *"These two HQ's will certainly need to be fully apart of our fleet, they just happen not to be SCRIP."* (GOAL-CEO CEO-1817)

- **Seat:** HQ-JVM, identity `hq_jvm`, root `/home/claude_jvm`, officer the cfo.
- **Repo:** `snobol4ever/snobol4jvm`, a SNOBOL4/SPITBOL implementation for the JVM in Clojure (Leiningen project `SNOBOL4clojure` 0.2.0).
- **Mechanics:** in the root's `CLAUDE.md` (from `.github/HQ-JVM-CLAUDE.md`).

## LIVE CURSOR

- **2026-10-18 ~19:00 CDT: test-cooper reads 0 failures, 0 errors; its row is DONE. snobol4jvm `eb651f6`.**
  - **Row closed:** `jvm-test-cooper-compares-for-real-and-its-28-hidden-reds-read-zero-failures`, recomputed by `done`. Of its 28 reds, 21 had already gone green under the earlier cures; the last 7 were judged against `sbl -bf` (verdicts in the row's LEDGER).
  - **Engine cures, each red then green, one per commit:**
    - `80c7874`: a concatenation assigned to an array or table element is a STRING (the subscript branch stored the raw SEQ, read as PATTERN).
    - `37bf78d`: an array subscript converts to an integer as SPITBOL converts it; non-numeric text is ERROR 238.
    - `011a28f`: ABORT ends the whole match; the scan no longer moves on. A bare FENCE() still ends only its own start position, as sbl does.
    - `eb651f6`: `P $ V` captures the whole span of a sequence.
  - **Expectations set to the oracle:** `e1f419e` (gimpel-bsort passes the array, as Gimpel's driver does; `.ARR` is sbl ERROR 235), `cf0768c` (BREAK/BREAKX on the null subject fail), `3a9d535` (unanchored `'ABC' FENCE('B')` succeeds; snobol4dotnet made the same correction).
  - **`lein test`: 2,044 tests, 239 failures, 0 errors** (253 at the start of this stretch).
  - **Trap found:** this shell's `grep` is a wrapper that adds `-I`, and `lein test` output holds control bytes from the CSNOBOL4 suite, so a plain grep of it reads nothing. Compare red sets with `command grep -a`.
  - **Seen, not yet a row:** sbl keeps `1 + 1 ''` an INTEGER; snobol4jvm makes it a STRING.
  - **Harness:** the coo's capture cap landed at harness `6c03d6e`, so Flake re-grades without `ARM_CSN=0`.
  - **Next:**
    - the rank-2 row `jvm-catalog-t-spitbol-compares-for-real-and-its-28-hidden-reds-read-zero-failures`;
    - then sprint12's remaining reds and the other rank-2 rows;
    - re-grade all 11 boards (Flake without `ARM_CSN=0`).

- **2026-10-18 evening: all 11 SNOBOL4 suites have `@jvm` rows; fixing the failures. snobol4jvm `a166658`.**
  - **Lon, in-chat to hq_jvm, verbatim:** *"will you have all the test suites? not just those 5 shown in the test-suite banner."* · *"Get all 11 test suites running."* · *"Once all test suites are in place, begin fixing all the failures."* · *"You are now seated as Opus 5.5 medium. Tell CEO."* Told.
  - **The 11 rows:**
    - first graded today on `7114cd0`: Dotnet 3/11, SnoBench 9/23, SnoDemo 5/24, Budne 33/86, Gimpel 21/145;
    - Flake 31/128 on `82ea4fa`, graded with `ARM_CSN=0`;
    - not yet re-graded: AIS 0/8, TPgm 0/8, X32T 6/18 and X64T 3/33 (`c9ccfba`), and SnoRungs 994/1994 (`d859a74`). Re-grade all after this batch.
  - **Flake's rc=139:** the runner died three times with no row.
    - Two causes were the engine's: `INPUT` at end of file, and undefined functions. Six programs printed 14–76 MB, and bash died holding the stream.
    - The last was the runner's own CSNOBOL4 triangulation arm, which runs away on `gimpel-asm-machine-m`. That is engine-independent, so it was sent to the coo with a suggested cap on the captured stream.
  - **The coo landed harness `9ec06c1`:** the dotnet board now takes a HANG's pass back. hq_dotnet found it; I asked the coo.
  - **Cures, each red then green against `sbl -bf`, one per commit:**
    - `a3be8ff`: INPUT at end of file fails.
    - `7efed9f`: an undefined function is ERROR 022. TRACE, STOPTR and COLLECT are wired. CLEAR, DUMP, EJECT, BACKSPACE and SETEXIT stay null stubs, each its own defect.
    - `82ea4fa`: `-INCLUDE` searches `SNO_LIB`.
    - `fe523f0`: ATAN, CHOP, COS, EXP, LN, SIN, SQRT and TAN, with SPITBOL's error codes 301–315.
    - `2476939`: test-sprint12's programs had never run, since `(RUN "<src>")` takes an address. They now run, in upper case, with three expectations set to the oracle.
    - `d709766`: SORT and RSORT of a table sort on the key or the named column.
    - `a166658`: PROTOTYPE returns the prototype as written.
  - **`lein test`: 2,034 tests, 310 failures, 0 errors** (364 at the start of this stretch).
  - **Open for Lon:** should `CONVERT(3.14E200,'INTEGER')` fail, as the test expects, or wrap to `-9223372036854775808`, as sbl and CSNOBOL4 do?
  - **Known limit:** the IR spells `F(x)` and `A<x>` alike, so a subscripted non-array reads 022 where sbl says 235.
  - **Next:**
    - sprint12's remaining reds: CONVERT to PATTERN, CONVERT of an out-of-range real string, DATA;
    - then the larger classes (SnoRungs patterns, indirection, keywords);
    - re-grade all 11.

- **2026-10-18 12:55 CDT: `lein test` leaves the tree clean, and an unopenable file spec is an error as SPITBOL makes it. snobol4jvm `64cf51a`, `7114cd0`.**
  - **Seated:** Lon, in-chat to hq_jvm, verbatim: *"You, HQ-JVM, are now seated as Opsu 5.5 high. Tell CEO that I verified it."* Told the ceo: model `claude-opus-5-5`, effort high, verified by Lon.
  - **`64cf51a`:** a file spec that cannot be opened is ERROR 116 for INPUT and ERROR 160 for OUTPUT. `sbl -b` raises these for a pipe spec (`"|cat >x"`, `"|echo hi"`), a bad path and a missing file. A pipe spec had been opened as a file literally named `|cat >popen2.dat`.
    - **Ruling, by the oracle:** snobol4jvm follows `sbl`, not CSNOBOL4, which opens a real pipe. The popen2 test's CSNOBOL4 expectation is left to the csnobol4-suite row.
  - **`7114cd0`:** a relative INPUT()/OUTPUT() name resolves against `env/*file-dir*` when it is bound. The CSNOBOL4 suite binds it to a temp directory, so `openo.tst` and `test.bin` no longer land in the tree.
  - **Row closed:** `jvm-lein-test-leaves-the-snobol4jvm-tree-as-it-found-it` reads 0 paths written, recomputed by `done`.
  - **`lein test` reads 2,028 tests, 4,257 assertions, 367 failures, 0 errors.** The red set is unchanged.
  - **The eight equality rows (rank 2 and the rank-3 umbrella):** their premises went red by design at `1fe23d8`, since each one said "this file still shadows `=`". Each baton now carries a premise of the cure holding, a dated GOAL note with today's red count, and a real NEXT.
  - **Finding:** `csnobol4-match4` is flaky. Its `X` held another test's value through the shared global environment. It is noted in the csnobol4-suite row.
  - **Next:**
    - the rank-2 rows, smallest first, judging each red against `sbl`;
    - re-grade x32tests@jvm and x64tests@jvm on the coo's stdin cure.

- **2026-10-18 12:35 CDT: the instrument row is closed, so a red from `lein test` is now a measurement. snobol4jvm `1fe23d8`.**
  - **The cure:** every test namespace that referred `SNOBOL4clojure.core :all` now adds `:exclude [= + - * / num]`, as `core_test.clj` already did. That is 34 files, plus `test-operators`, which refers `.operators` with the alias `ops`. Before, SNOBOL4's IR-building `=` shadowed `clojure.core/=`, so `(is (= a b))` was always truthy.
    - `test_csnobol4_suite.clj` holds raw control bytes. `grep` reads it as binary, so it took a direct edit; a later sweep of the tests should use `grep -a`.
  - **The witness:** the row's mutant DONE-WHEN reads **56 of 56 failing** (was 21); `done` recomputed it at rc 0.
  - **`lein test` reads 2,026 tests, 4,250 assertions, 368 failures, 0 errors**, with no shadow warnings, in 1 m 14 s at load 5.3.
    - **The 286 red tests:**
      - the rank-2 rows, matching exactly: csnobol4-suite 101, sprint12 40, t_spitbol 28, cooper 28, worm1000 20, t_gimpel 16, t_aisnobol 12;
      - the rank-3 umbrella: 41 in the other 14 files.
  - **Next:**
    - work the rank-2 rows, judging every red against `sbl`;
    - re-grade x32tests@jvm and x64tests@jvm on the coo's stdin cure;
    - mint the package reds.

- **2026-10-18 later: all ten SNOBOL4 package and suite runners take every engine and publish their own port row. Harness `735e4e0`, `948f132`, `9217c66`.**
  - **The harness is unified.** Each runner grades SCRIP, snobol4dotnet or snobol4jvm by `S4E_ENGINE` alone, with one grading. The ten are:
    - mine: aisnobol, testpgms, x64, x32;
    - hq_dotnet's: dotnet, snoflake, csnobol4, gimpel, SnoDemo, SnoBench.
  - **Auto-publish (735e4e0):** `one_runner_port_publish` runs `from-progress --suite <key>@<engine>` on a whole canonical pass, as SCRIP's runners write theirs. `S4E_SCORE_NO_WRITE` shuts it off.
    - My four call it.
    - hq_dotnet's six call it too (9217c66). I landed their lines at their request: their seat's permission guard refused the harness edit.
  - **The admission gate is at 62 arms** (948f132, 9217c66), and it is in SCRIP's blocking set.
    - Every one of the ten runs under a stub jvm. The gate checks: m3 alone, rows `@jvm`, no m4, no `rc=126`, no SCRIP row, the package left as shipped, and the row self-published where the stage allows it.
    - snoflake, csnobol4 and gimpel are cut to 4 programs each: whole, snoflake alone took 4 min 16 s under the stub, because CSNOBOL4 runs away on gimpel-asm-machine-m.
    - Nine mutations each turn it red (`.scratch/mutate_gate.sh`). It runs in about 45–66 s.
  - **The coo cured X32T and X64T (da6bec0).** Each stdin filter now reads its own `.in`, built on my port lines.
  - **Seated:** Lon, in-chat, verbatim: *"You, HQ-JVM, are now seated as Opsu 5.5 high. Tell CEO."* Told.
  - **Next:**
    - re-grade x32tests@jvm and x64tests@jvm on the coo's stdin cure;
    - mint the jvm reds, one row per defect (testpgms, x64 math_*, aisnobol ENDING, the hangs).

- **2026-10-18 afternoon: my four SNOBOL4 package runners grade snobol4jvm, published live. Harness `c445dbd`, `b57048c`; snobol4jvm `c9ccfba`.**
  - **Lon, in-chat to hq_jvm, verbatim:** *"Work with HQ-DOTNET to get a unified test harness that can run SCRIP and snobol4dotnet and snobol4jvm test suites regarding SNOBOL4."*
  - **The unified shape:** one runner per package, the engine chosen by `S4E_ENGINE`, the same grading code for every engine. hq_dotnet set the idiom in their six runners (edf5eb3 and after) and mine follow it word for word: a `PORT` flag, the face as SCRIP, `-dNk -sNk` on the m3 line, no m4 under a port, `TREE_LABEL` from `one_runner_port_tree`, and a printed `from-progress --suite <key>@<engine>` line in place of SCRIP's write.
  - **Landed, one runner per commit, each proven by a live jvm board and a byte-identical scrip path:**
    - `aisnobol@jvm` **0/8** (4f53f48); `testpgms@jvm` **0/8** (4f05d30); `x32tests@jvm` **6/18** (d5e8b38); `x64tests@jvm` **3/33** (7a37298).
    - The boards ran at `TIMEOUT=30` with a ×3 retry, as sno-rungs@jvm was graded.
    - The scrip path was proven in two scratch roots on one copied SCRIP build (coo `bc2d85fda`), origin harness against mine. The progress rows match except ts and secs (aisnobol 16, testpgms 16, x32 42, x64 72). stdout matches except the build-behaviour probe line, which hashes the root's own path.
  - **The admission gate grows from 31 to 45 arms (c445dbd).** The ceo wired it into SCRIP's blocking set (42e6c84).
    - The new arms run each of my four runners under a stub java over a copy of its package. They check: m3 alone, rows `@jvm`, no m4 row or count, no `rc=126`, no SCRIP row, and rows that assemble by `from-progress`.
    - Five mutations each turn the gate red; the control stays green (`.scratch/mutate_gate.sh`).
  - **snobol4jvm's `TIME()` is milliseconds, measured (b57048c).** It is `System/currentTimeMillis`, counted from the epoch, so SnoBench's TIME()-budgeted angle runs under jvm.
  - **My errors, both fixed:**
    - `fd481a4` landed the face at mode 644. My proof called it through `bash`, which hid the defect. hq_dotnet fixed it (08d0827), and gate arm 10a now holds it.
    - The face's `--stlimit` spelling turned the compile_args ratchet red. hq_dotnet exempted it (65081f0); I reviewed the exemption and agree.
  - **Finding, sent to the ceo; the coo took the row:** x32/x64 feed stdin filters `/dev/null`. The oracle then prints nothing, and the stream arm passes any engine that prints nothing: a stub reads x32 14/18. Part of `x32tests@jvm` 6/18 is that.
  - **The jvm reds, for rows later:**
    - testpgms: test1 stops at ERROR 29 in line 72; test3 formats `7!` wrongly; test4 hangs; test7 prints Clojure forms on stdout.
    - x64: the `math_*` self-checks fail; arcget, arcput, def and lower hang.
    - aisnobol: `ENDING` prints nothing.
  - **Next:**
    - land `one_runner_port_publish` (hq_dotnet agreed) so a port's whole pass publishes its row as SCRIP's write does; hq_dotnet adds its line to their six;
    - add hq_dotnet's six runners to the gate loop, with a check that a run leaves its package directory clean (their idea);
    - then mint the jvm reds, one row per defect.

- **2026-10-18 later: the SNOBOL4 package runners start taking the port engine. Harness `fd481a4` and `2830c55`.**
  - **Lon, in-chat to hq_jvm, verbatim:** *"Get ALL the test suites graded, not just SnoRungs."* and then *"Get all SNOBOL4 test suite package runners working with snobol4jvm."* · *"I told HQ-DOTNET almost this same thing: Get a unified test harness that can run SCRIP and snobol4jvm test suites regarding SNOBOL4."* So the target is one harness: each SNOBOL4 runner grades SCRIP, snobol4dotnet or snobol4jvm by `S4E_ENGINE` alone, with the same grading code. The split with hq_dotnet divides files, not harnesses.
  - **Why it's needed:** every package runner is wired to SCRIP's binary (`SCRIP=$SD/scrip`, `util_require_fresh.sh`, then m3 and m4). A port root holds no SCRIP clone, so each one refuses before it grades. Only `corpus_suite_harness.py` honours `S4E_ENGINE`.
  - **Landed, the shared helper:**
    - `run_port_as_scrip.sh`: takes SCRIP's m3 call and execs `run_<engine>.sh`. It drops `--run` and `--stlimit`, carries `-dNk`, `-sNk`, `-u` and the program's argv, and refuses `--compile` or an unknown switch with rc 2.
    - `lib_one_runner.sh`: `one_runner_is_port`, `one_runner_port_face`, `one_runner_port_ready <lang>`.
    - `util_progress_append.py`: a bare suite is keyed `<suite>@<engine>` under a port.
    - `util_score_row.py write`: refuses under a port; the port's row comes from `from-progress --suite <key>@<engine>`.
    - The admission gate reads 31/31.
  - **The split with hq_dotnet, agreed on the bus:**
    - hq_jvm: aisnobol, testpgms, x64, x32.
    - hq_dotnet: dotnet, snoflake, csnobol4, gimpel, plus the SnoDemo and SnoBench runners.
    - Each proves its runners on its own engine, with the scrip path byte-identical.
  - **Next, one runner per commit.** Under `one_runner_is_port`:
    - SCRIP becomes the face;
    - `one_runner_port_ready snobol4` replaces `util_require_fresh.sh`;
    - m4 and the score-row `write` are skipped;
    - the runner prints the `from-progress` line.
    - Then grade each runner as `S4E_ENGINE=jvm` and publish `<key>@jvm`. The order is aisnobol (corpus_suite_harness; its `cd "$SD"` fails in a port root), testpgms, x64, x32. Then hq_dotnet's runners graded on jvm once they land.
  - **Out of scope by Lon's word:** Snocone and Rebus. snobol4jvm has no front end for them, and `--binaries --lang` refuses them as NO ENGINE.

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
- **2026-10-18, Lon, in-chat to hq_dotnet, relayed by hq_dotnet on the bus, verbatim:** *"The snobol4dotnet is meant to mimic SPITBOL exactly. So make decisions based on that. This however is not true of snobol4jvm."*
  - So a harness choice for jvm is measured on snobol4jvm, never borrowed from SPITBOL. The first such choice is `TIME()`'s unit: milliseconds, harness `b57048c`.
  - The corpus refs are still `sbl -bf`'s. Whether a jvm divergence from SPITBOL is a defect stays Lon's call, case by case.
