# GOAL-HQ-DOTNET — finish and polish snobol4ever/snobol4dotnet

**Opened 2026-10-17 by Lon, in-chat to the ceo, verbatim:** *"We need to create two new HQ seats and their corresponding root folders (I'll do that part) for finishing and polishing snobol4ever/snobol4dotnet and snobol4ever/snobol4jvm. Call them HQ-DOTNET and HQ-JVM."* · *"These two HQ's will certainly need to be fully apart of our fleet, they just happen not to be SCRIP."* (GOAL-CEO CEO-1817)

- **Seat:** HQ-DOTNET, identity `hq_dotnet`, root `/home/claude_dotnet`, officer the cfo.
- **Repo:** `snobol4ever/snobol4dotnet`, a SNOBOL4 + SPITBOL-extensions compiler in C#/.NET.
- **Mechanics:** in the root's `CLAUDE.md` (from `.github/HQ-DOTNET-CLAUDE.md`).

## LIVE CURSOR

- **2026-10-18 early — the harness runs snobol4dotnet (CEO-1822).** Lon's lane ruling: hq_dotnet runs the SNOBOL4 suites and benchmarks on the dotnet engine. The ceo's: the engine is a runner setting.
  - **Landed in harness:**
    - `707e10f`: `S4E_ENGINE`, the `lang@engine` lane, the dotnet arm, the DLL fingerprints, rows keyed `@dotnet`.
    - `25ac84e`: `run_m3` dispatches a port to its own runner script (`run_snobol4dotnet.sh`), in the calling shape agreed with hq_jvm. hq_jvm's `eb5a087` landed the jvm arm on it.
    - `71db7a8`: `from-progress` and the audit carry the `@engine` key, and grade a port in m3 alone.
    - The admission gate is 24 of 24; the admission row is DONE.
  - **Landed in `.github` `815f661f`:** this seat's grid reads only `@dotnet` rows (today "no row yet (engine dotnet)"), and SCRIP's views stay byte-identical.
  - **Engine defects the board found, each red-then-green with sbl as the oracle:**
    - `166fada`: OUTPUT was on stderr. That alone moved 60 rungs from 5 to 51 passing.
    - `4add3d8`: ARBNO of a null-matching argument repeated forever. SPITBOL requires each repetition to advance.
  - **Rows minted:** a `../` source path is resolved to a doubled path; the test host intermittently hangs or crashes.
  - **Noted, not yet minted:** a label after `;` (`...;EN;END`) raises error 23; program argv after the source is compiled as more source files.
  - **Next:** a scratch diagnostic pass of all 1,996 rungs (10 s bound, no retry) is finding the remaining hang classes. Then the live `sno-rungs@dotnet` board writes the first `@dotnet` row, then the package suites, then benchmarks against official SPITBOL.
- **2026-10-17 night — Lon: *"I suspect getting the test harness and benchmarks to run is the first order of business."***
  - **Benchmarks (this repo's runner) run.** `dotnet run --project benchmarks/Benchmarks.csproj -c Release` did not compile (`CS8803`; cured in `0ff85f8`). After that it found no programs: every entry SKIPped, since it looked in `corpus/benchmarks/` and ignored `CORPUS` (cured in `1972f32`). Now 13 of 15 entries measure, all in-process: Roman_1776 33.6 ms, Fibonacci_18 48.0 ms, PatternBacktrack_500 44.8 ms. The other two programs are not in the corpus. Still owed:
    - the Result column reads `?` for 12 of 13, so its correctness check is vacuous;
    - in-process times are not comparable with `sbl` process times; the `x` multiple of THE GOAL item 3 needs a whole-process timing beside the official SPITBOL.
  - **The fleet harness can grade snobol4dotnet with no harness edit.** `.scratch/dn/bin/scrip_as_dotnet.sh` takes the m3 call (`scrip --run [switches] prog.sno`) and runs `dotnet Snobol4.dll -b -f [-dNk -sNk -u] prog.sno`. Its output on a rungs program is byte-identical to the ref. But `corpus_suite_harness.py` refuses this seat rc 2, ONE SEAT, ONE LANGUAGE, because `LANES: snobol4=coo`. It refuses even over a plain-copy scratch population with a scratch progress table. **Blocked on a lane ruling**: the snobol4 suites on the dotnet engine as hq_dotnet's own board, with rows tagged by engine. Asked of the ceo (topic `banner-scoped-to-snobol4-landed`) and of Lon.
  - **Banner:** the ceo landed `.github` `5ed9a61d`: this seat's grid is the 11 snobol4 rows, footnoted as SCRIP's readings until a runner grades dotnet.
  - **Found on the way:** snobol4dotnet treats every argument after the first source file as another file to compile, so a program's own argv (HOST(2,n)) never reaches it. To be minted.
- **2026-10-17 evening — the first row, `dotnet-testsnobol4-reads-every-unit-test-passed-twelve-fail-at-80c828a-ceo-1817`, CLAIMED and still open.**
  - **The "12 FAILED" was an aborted run.** At `80c828a` the test host crashes with a stack overflow 3 s in, during `TEST_Csnobol4_file` (named by `--blame`). The summary line still printed counts ("Failed: 14, Total: 2087" here), so the number was never a measurement.
  - **Cured in `12201c0`.** `ExecuteLoop` caught the fatal `CompilerException` at every level, and it also runs function bodies, so an error inside a function resumed the caller: it looped one call deep and overflowed two deep. SPITBOL and CSNOBOL4 both stop at the first error. Only the outermost `ExecuteLoop` catches now. `TEST_Define_007/008` were red and are green.
  - **The suite now completes: 2,505 tests, 2,429 passed, 74 FAILED, 2 skipped.** Every failure is in `CorpusRef_Csnobol4Suite` (Budne's CSNOBOL4 suite, expectations inline). The 2 skips are `[Ignore]`d "fix pending" tests.
  - **Next:** triage the 74 against `sbl`. A failure where SNOBOL4.NET differs from SPITBOL is a defect, minted one row each. An expectation that is CSNOBOL4-only behaviour (`file.sno`'s FILE functions, which `sbl` answers with error 22) is a question for Lon. The baton's `## NEXT` has the steps.
  - **Watch:** one full run hung once (testhost idle 10 min) and four others finished in 8–12 s. Re-run under `--blame-hang` until it recurs, then mint it.
  - **Landed:** `snobol4dotnet/CLAUDE.md` (`b69c86a`), the repo's own guidance for Claude Code.
- **2026-10-17 — the seat opened.** The ceo measured, at `80c828a`, .NET SDK 10.0.110, in a scratch clone:
  - `dotnet build Snobol4.sln -m:4` succeeds in 11 s with 0 warnings and 0 errors.
  - `dotnet test TestSnobol4/TestSnobol4.csproj -m:4` takes 17 s: **2,084 tests, 2,072 passed, 12 FAILED.**
  - Six build outputs are tracked in git (`*.dll`, `*.pdb`, `*.cache`).
  - The working tree is clean and current with origin.
- **First sitting:**
  1. Re-measure the build and the tests in this root. Name the 12 failing tests here, and mint one row per defect: owner `hq_dotnet`, DONE-WHEN the failing test.
  2. Measure the SPITBOL agreement over `corpus/` and write the table here: the master `tests/snobol4/ALL.sno` entries, the benchmarks, the demos and the SNOBOL4 packages, each run under Snobol4.NET against its `.ref`. Choose the oracle switches and record that choice.
  3. Mint the reds. Cure them one per commit, before any polish.

## THE GOAL, IN ORDER

1. **Correct:** every unit test passes, and every corpus program the oracle answers matches its ref.
2. **Polished:**
   - no build output tracked;
   - a clean build, no warnings;
   - a README that matches what the code does today;
   - the bridge smokes (`scripts/test_smoke_dot_bridge*.sh`) green.
3. **Measured:** benchmark numbers against official SPITBOL (`/home/resources/spitbol-bench-oracle/sbl`), quoted as the bare multiple `x` (reference time over this port's time), each with its load stamped.

## RULINGS

- **Batches, Lon 2026-10-18, in this seat's chat, verbatim:** *"You better be running tests in batches of 100."* The unit suite runs through `snobol4dotnet/scripts/test_in_batches.sh`: 26 batches, each in its own bounded test host, and a batch that hangs or crashes is named NOT RUN. A board runs one partition part at a time (`--partition core` and `chunk:01`..`chunk:20`, 100 entries each, the suite's own `PARTITION.tsv`). Never one whole-population process. This seat's DONE-WHENs measure the same way.
- **Lane, Lon 2026-10-17 night, in this seat's chat, answering "Who should run the SNOBOL4 suites and benchmarks on the snobol4dotnet engine?":** *"hq_dotnet runs them."* The snobol4 suites and benchmarks on the dotnet engine are this seat's own board. LANES gets an engine-qualified entry, and the rows carry engine=dotnet so they never mix with SCRIP's. This seat gets the adapter or a proper engine option into the harness with the ceo.
- The oracle wins over this project's own behaviour unless Lon rules otherwise. Record every such ruling here with its date and words.
- **Scope, Lon 2026-10-17, in this seat's chat, verbatim:** *"The test suite banner is wrong since .NET supports only SNOBOL4, actually SPITBOL."* · *"The test suite banner has the wrong list of languages."* · *"The suite banner should represent the snobol4dotnet executable program, not SCRIP."* SNOBOL4.NET's language is SNOBOL4 in the SPITBOL dialect and nothing else, and this seat's banner grades the snobol4dotnet executable, not SCRIP. Both points went to the ceo by telegram (topic `banner-languages-wrong-for-hq-dotnet`). Landing it needs an engine setting in the harness's SNOBOL4 runners, engine-tagged rows in SUITES.tsv, and a banner that renders its own seat's engine. The ceo decides whether the ceo lands it or assigns the dotnet arm to this seat.
