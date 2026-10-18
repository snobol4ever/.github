# GOAL-HQ-JVM — finish and polish snobol4ever/snobol4jvm

**Opened 2026-10-17 by Lon, in-chat to the ceo, verbatim:** *"We need to create two new HQ seats and their corresponding root folders (I'll do that part) for finishing and polishing snobol4ever/snobol4dotnet and snobol4ever/snobol4jvm. Call them HQ-DOTNET and HQ-JVM."* · *"These two HQ's will certainly need to be fully apart of our fleet, they just happen not to be SCRIP."* (GOAL-CEO CEO-1817)

- **Seat:** HQ-JVM, identity `hq_jvm`, root `/home/claude_jvm`, officer the cfo.
- **Repo:** `snobol4ever/snobol4jvm`, a SNOBOL4/SPITBOL implementation for the JVM in Clojure (Leiningen project `SNOBOL4clojure` 0.2.0).
- **Mechanics:** in the root's `CLAUDE.md` (from `.github/HQ-JVM-CLAUDE.md`).

## LIVE CURSOR

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
