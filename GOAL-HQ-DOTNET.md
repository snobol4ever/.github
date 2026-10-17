# GOAL-HQ-DOTNET — finish and polish snobol4ever/snobol4dotnet

**Opened 2026-10-17 by Lon, in-chat to the ceo, verbatim:** *"We need to create two new HQ seats and their corresponding root folders (I'll do that part) for finishing and polishing snobol4ever/snobol4dotnet and snobol4ever/snobol4jvm. Call them HQ-DOTNET and HQ-JVM."* · *"These two HQ's will certainly need to be fully apart of our fleet, they just happen not to be SCRIP."* (GOAL-CEO CEO-1817)

- **Seat:** HQ-DOTNET, identity `hq_dotnet`, root `/home/claude_dotnet`, officer the cfo.
- **Repo:** `snobol4ever/snobol4dotnet`, a SNOBOL4 + SPITBOL-extensions compiler in C#/.NET.
- **Mechanics:** in the root's `CLAUDE.md` (from `.github/HQ-DOTNET-CLAUDE.md`).

## LIVE CURSOR

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

- The oracle wins over this project's own behaviour unless Lon rules otherwise. Record every such ruling here with its date and words.
