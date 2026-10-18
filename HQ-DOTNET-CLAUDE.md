# CLAUDE.md

This file guides Claude Code in the root `/home/claude_dotnet`, the seat **HQ-DOTNET**.

## The seat

Lon opened this seat on 2026-10-17, saying to the ceo, verbatim: *"We need to create two new HQ seats and their corresponding root folders (I'll do that part) for finishing and polishing snobol4ever/snobol4dotnet and snobol4ever/snobol4jvm. Call them HQ-DOTNET and HQ-JVM."* He added: *"These two HQ's have ZERO to do with SCRIP. Not related at all."*

- **The work:** finish and polish **snobol4ever/snobol4dotnet**, a SNOBOL4 + SPITBOL-extensions compiler written in C# for .NET.
- **A fleet seat, not a SCRIP seat:** Lon, the same sitting, verbatim: *"These two HQ's will certainly need to be fully apart of our fleet, they just happen not to be SCRIP."* This seat is a full member of the snobol4ever fleet. It works through the postoffice like every seat (mail, queue rows, claims, MODE, the banner), and its officer is the cfo (completeness and correctness). Its code has nothing to do with SCRIP, the fleet's x86-64 compiler: the root holds no SCRIP clone, and SCRIP's internals (its zetas, its emitter, its suites) are not this seat's business.
- **The bus:** `harness/` beside your repos is a clone of `snobol4ever/harness`, the fleet's harness (the postoffice bus, the runners, the gates, the benchmarks, the monitor; Lon 2026-10-17, CEO-1819/1820). Run every bus verb from this root: `bash harness/scripts/s4e_msg.sh check`, `clear`, `next`, `done <topic>`, `send <seat> <topic> --stdin`, `mint <topic> 1 --owner hq_dotnet --stdin`; the Stop banner and the inbox hook run it from `.claude/settings.json`. Pull harness with the other repos (`git -C harness pull --ff-only`); never edit it to suit this seat -- a harness defect is one telegram to the ceo. No symlinks, ever: never create one, and `harness/scripts/test_gate_no_symlinks.sh` run from this root reads every repo here.
- **Rows:** a row's DONE-WHEN runs from this root, so it begins `cd "${S4E_HOME:-$PWD}/snobol4dotnet" || exit 2;` and names a command that measures (the failing test, the corpus program against the oracle), never prose. A topic carries no SCRIP language prefix, so `mint` needs `--owner hq_dotnet`.
- **Who directs it:** Lon, and the ceo through the bus; MODE line 2 of `/home/resources/postoffice/MODE` names this seat's business.
- **Where state lives:** in `.github/GOAL-HQ-DOTNET.md`. Its LIVE CURSOR is on top; keep it current and push it.

## The root

- **`snobol4dotnet/`** is the work. It is a clone of `git@github.com:snobol4ever/snobol4dotnet.git`, branch `main`.
- **`corpus/`** (`snobol4ever/corpus`) holds the SNOBOL4 programs to measure against, each with the reference output its oracle printed:
  - `corpus/tests/snobol4/ALL.sno`, `ALL.ref` and `ALL.csv`: 1,980 entries, a container that is never run whole.
  - `corpus/benchmarks/snobol4/`
  - `corpus/demos/snobol4/`
  - `corpus/packages/snobol4/{gimpel,spitbol_testpgms,spitbol_x64_tests,dotnet,…}`. `packages/snobol4/dotnet` came from this project's own test files.
  - Read programs and refs here; never edit corpus to make a port pass.
- **`.github/`** (`snobol4ever/.github`) is the org brain; this seat's GOAL file lives there.
- **`.scratch/`** is for scratch work. Scratch clones and build experiments go here, never inside a repo.

## Build and test (measured by the ceo on 2026-10-17 at `80c828a`, .NET SDK 10.0.110)

```bash
cd snobol4dotnet
dotnet build Snobol4.sln -m:4 -v:q                         # 11 s, 0 warnings, 0 errors
dotnet test TestSnobol4/TestSnobol4.csproj -m:4 -v:q       # 17 s: 2,084 tests, 2,072 passed, 12 FAILED
```

- **Projects:** `Snobol4` (the console compiler), `Snobol4W` (Windows), `Snobol4.Common` (the engine), `TestSnobol4` (the unit tests), `UnicodeTest`, `CustomFunction` (`AreaLibrary`, `ReflectLibrary`), `BenchmarkSuite1/2` and `benchmarks/`.
- **Bridge smokes:** `scripts/test_smoke_dot_bridge*.sh`.
- **The machine is shared.** The SCRIP fleet runs on the same 16 cores. Build with `-m:4` at most, run one test or benchmark process at a time, and read `uptime` before any long run.

## Oracles

SNOBOL4.NET follows SPITBOL: *"any statement about SPITBOL in the SPITBOL manual, applies to SNOBOL4.NET"*.

- **Correctness oracle:** `/home/resources/x64/bin/sbl`, the SPITBOL x64 fork that SCRIP's suites grade against. Run `sbl -h` for its switches; choose the case-folding switch this project's semantics want and write that choice in the GOAL file.
- **Timing:** time only against the official upstream at `/home/resources/spitbol-bench-oracle/sbl`, never the fork.
- **Second engine:** `/home/claude_ceo/csnobol4/snobol4` (CSNOBOL4), a reference engine.
- **Manuals:** greppable `/home/claude_ceo/.tools/docs/spitbol-manual-v3.7.txt` and `green-book.txt`. Grep these, never the PDFs.
- **The oracle decides:** when the oracle and this project disagree, the oracle wins unless Lon rules otherwise. Record every such ruling in the GOAL file.

## How to work

- Measure first: build, run the tests, and run corpus programs against the oracle. Every change starts from a red that a measurement shows and ends when that measurement reads green.
- One defect per commit, proven by its test, pushed the minute it is green.
- Prefer a real fix to a test edit. Never weaken a test to make it pass.
- Polish means:
  - nothing generated is tracked (`bin/`, `obj/`, `*.dll`, `*.pdb`, `*.cache`: six such files were tracked at `80c828a`);
  - a README that matches what the code does;
  - a clean build with no warnings;
  - tests that all pass and mean something.

## Commits

- **ONE IDENTITY:** `user.name "LCherryholmes"`, `user.email "lcherryh@yahoo.com"`, as both author and committer.
- **No trailers:** never add `Co-Authored-By:`, `🤖 Generated with` or `Claude-Session:`. The commit-msg hook in each repo refuses them.
- **Message mechanics:** pass commit messages through `git commit -F -` with a quoted heredoc (`<<'EOF'`), never `-m "…"`. Never amend a pushed commit, never force-push, never rewrite history.
- **Pull and push:** run `git pull --rebase` before every push. Push over SSH (`ssh -T -o BatchMode=yes git@github.com` self-tests it).
- **End of sitting:** leave nothing unpushed. Move the LIVE CURSOR in `.github/GOAL-HQ-DOTNET.md` and push `.github` last.
