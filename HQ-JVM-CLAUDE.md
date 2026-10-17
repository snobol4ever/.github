# CLAUDE.md

This file guides Claude Code in the root `/home/claude_jvm`, the seat **HQ-JVM**.

## The seat

Lon opened this seat on 2026-10-17, saying to the ceo, verbatim: *"We need to create two new HQ seats and their corresponding root folders (I'll do that part) for finishing and polishing snobol4ever/snobol4dotnet and snobol4ever/snobol4jvm. Call them HQ-DOTNET and HQ-JVM."* He added: *"These two HQ's have ZERO to do with SCRIP. Not related at all."*

- **The work:** finish and polish **snobol4ever/snobol4jvm**, a full SNOBOL4/SPITBOL implementation for the JVM written in Clojure.
- **A fleet seat, not a SCRIP seat:** Lon, the same sitting, verbatim: *"These two HQ's will certainly need to be fully apart of our fleet, they just happen not to be SCRIP."* This seat is a full member of the snobol4ever fleet. It works through the postoffice like every seat (mail, queue rows, claims, MODE, the banner), and its officer is the cfo (completeness and correctness). Its code has nothing to do with SCRIP, the fleet's x86-64 compiler: the root holds no SCRIP clone, and SCRIP's internals (its zetas, its emitter, its suites) are not this seat's business.
- **The bus without a SCRIP clone:** the postoffice scripts still live in SCRIP's `scripts/` until they move to `snobol4ever/harness` (Lon's question of 2026-10-17, CEO-1817). This seat runs them read-only from the ceo root's clone, with `S4E_HOME` naming this root. Define this once per shell:

  ```bash
  s4e() { S4E_HOME=/home/claude_jvm bash /home/claude_ceo/SCRIP/scripts/s4e_msg.sh "$@"; }
  ```

  then `s4e check`, `s4e clear`, `s4e next`, `s4e done <topic>`, `s4e send <seat> <topic> --stdin`, `s4e mint <topic> 1 --owner hq_jvm --stdin`. The Stop banner and the inbox hook run automatically from `.claude/settings.json`. Never edit anything under `/home/claude_ceo`; a bus defect is one telegram to the ceo.
- **Rows:** a row's DONE-WHEN runs from this root, so it begins `cd "${S4E_HOME:-$PWD}/snobol4jvm" || exit 2;` and names a command that measures (the failing test, the corpus program against the oracle), never prose. A topic carries no SCRIP language prefix, so `mint` needs `--owner hq_jvm`.
- **Who directs it:** Lon, and the ceo through the bus; MODE line 2 of `/home/resources/postoffice/MODE` names this seat's business.
- **Where state lives:** in `.github/GOAL-HQ-JVM.md`. Its LIVE CURSOR is on top; keep it current and push it.

## The root

- **`snobol4jvm/`** is the work. It is a clone of `git@github.com:snobol4ever/snobol4jvm.git`, branch `main`.
  - It is a Leiningen project: `project.clj`, `defproject SNOBOL4clojure "0.2.0"`, Clojure 1.10.3, instaparse, core.matrix, criterium, tools.trace.
  - Source is in `src/`, tests in `test/`; there are also `bench/`, `corpus/`, `doc/`, `resources/` and `CHANGELOG.md`.
- **`corpus/`** (`snobol4ever/corpus`) holds the SNOBOL4 programs to measure against, each with the reference output its oracle printed:
  - `corpus/tests/snobol4/ALL.sno`, `ALL.ref` and `ALL.csv`: 1,980 entries, a container that is never run whole.
  - `corpus/benchmarks/snobol4/`
  - `corpus/demos/snobol4/`
  - `corpus/packages/snobol4/{gimpel,spitbol_testpgms,spitbol_x64_tests,csnobol4_suite,…}`
  - Read programs and refs here; never edit corpus to make a port pass.
- **`.github/`** (`snobol4ever/.github`) is the org brain; this seat's GOAL file lives there.
- **`.scratch/`** is for scratch work. Scratch clones, downloaded tools and build experiments go here, never inside a repo.

## Build and test (what the ceo found on 2026-10-17 at `f35d392`)

- **No build tool yet.** Java is OpenJDK 21.0.11, but there is no `lein`, no `clojure` CLI and no `~/.m2`.
- **Your first job:** install Leiningen for this user. Its self-installing `lein` script goes on the PATH (for example `~/.local/bin`). Then run `lein deps` and `lein test`, and record the measured count in the GOAL file's cursor.
- **The README's claim to check:** "tests 1,896 / 0 failures", and the last commit adds `test_csnobol4_suite.clj` (126 tests: 116 Budne + 10 FENCE).
- **The machine is shared.** The SCRIP fleet runs on the same 16 cores. Run one JVM test or benchmark process at a time, and read `uptime` before any long run.

## Oracles

- **Correctness oracle:** `/home/resources/x64/bin/sbl`, the SPITBOL x64 fork that SCRIP's suites grade against. Run `sbl -h` for its switches; choose the case-folding switch this project's semantics want and write that choice in the GOAL file.
- **Timing:** time only against the official upstream at `/home/resources/spitbol-bench-oracle/sbl`, never the fork.
- **Second engine:** `/home/claude_ceo/csnobol4/snobol4` (CSNOBOL4), a reference engine.
- **Manuals:** greppable `/home/claude_ceo/.tools/docs/spitbol-manual-v3.7.txt` and `green-book.txt`. Grep these, never the PDFs.
- **The oracle decides:** when the oracle and this project disagree, the oracle wins unless Lon rules otherwise. Record every such ruling in the GOAL file.

## How to work

- Measure first: install the tool, run the tests, and run corpus programs against the oracle. Every change starts from a red that a measurement shows and ends when that measurement reads green.
- One defect per commit, proven by its test, pushed the minute it is green.
- Prefer a real fix to a test edit. Never weaken a test to make it pass.
- Polish means:
  - nothing generated is tracked (`target/`, class files);
  - a README whose badges and numbers match a run you made;
  - a clean `lein check`;
  - tests that all pass and mean something.

## Commits

- **ONE IDENTITY:** `user.name "LCherryholmes"`, `user.email "lcherryh@yahoo.com"`, as both author and committer.
- **No trailers:** never add `Co-Authored-By:`, `🤖 Generated with` or `Claude-Session:`. The commit-msg hook in each repo refuses them.
- **Message mechanics:** pass commit messages through `git commit -F -` with a quoted heredoc (`<<'EOF'`), never `-m "…"`. Never amend a pushed commit, never force-push, never rewrite history.
- **Pull and push:** run `git pull --rebase` before every push. Push over SSH (`ssh -T -o BatchMode=yes git@github.com` self-tests it).
- **End of sitting:** leave nothing unpushed. Move the LIVE CURSOR in `.github/GOAL-HQ-JVM.md` and push `.github` last.
