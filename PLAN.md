# SNOBOL4-plus — Master Plan

> **For a new Claude session**: Read `DIRECTORY.md` first — it tells you exactly
> where to look for what. Then come back here for the section you need.
> This file is the single source of truth for the entire SNOBOL4-plus organization.
> The Tradeoff Prompt for SNOBOL4-jvm is at the bottom of that repo's section.

---

## Session Start — Clone All Repos

**Always clone all six repos at the start of every session.** Work spans multiple
repos simultaneously — corpus changes, cross-platform validation, shared test
programs. Having all repos present avoids mid-session interruptions.

```bash
cd /home/claude
git clone https://github.com/SNOBOL4-plus/SNOBOL4-dotnet.git &
git clone --recurse-submodules https://github.com/SNOBOL4-plus/SNOBOL4-jvm.git &
git clone https://github.com/SNOBOL4-plus/SNOBOL4-python.git &
git clone https://github.com/SNOBOL4-plus/SNOBOL4-csharp.git &
git clone https://github.com/SNOBOL4-plus/SNOBOL4-corpus.git &
git clone https://github.com/SNOBOL4-plus/SNOBOL4-tiny.git &
wait
echo "All clones done."
```

Verify with:
```bash
for repo in SNOBOL4-dotnet SNOBOL4-jvm SNOBOL4-python SNOBOL4-csharp SNOBOL4-corpus SNOBOL4-tiny; do
  echo "$repo: $(cd /home/claude/$repo && git log --oneline -1)"
done
```

All six repos live under `/home/claude/`. The `.github` repo (this plan) clones to
`/home/claude/.github`.

---

## Session Start — Build Oracles (ALWAYS)

**Every session must build CSNOBOL4 and SPITBOL from the uploaded source archives.**
These binaries are used for cross-engine validation, oracle triangulation, the Snocone
bootstrap, and benchmark comparison. They are never pre-installed — always build them.

Source archives are in `/mnt/user-data/uploads/`:
- `snobol4-2_3_3_tar.gz` — CSNOBOL4 2.3.3 source
- `x64-main.zip` — SPITBOL x64 source

```bash
apt-get install -y build-essential libgmp-dev m4 nasm

# Build CSNOBOL4 and SPITBOL in parallel
(
  mkdir -p /home/claude/csnobol4-src
  tar xzf /mnt/user-data/uploads/snobol4-2_3_3_tar.gz -C /home/claude/csnobol4-src/ --strip-components=1
  cd /home/claude/csnobol4-src
  ./configure --prefix=/usr/local 2>&1 | tail -1
  make -j4 2>&1 | tail -2
  make install 2>&1 | tail -1
  echo "CSNOBOL4 DONE"
) &

(
  unzip -q /mnt/user-data/uploads/x64-main.zip -d /home/claude/spitbol-src/

  # Patch systm.c: nanoseconds -> milliseconds (REQUIRED)
  cat > /home/claude/spitbol-src/x64-main/osint/systm.c << 'EOF'
#include "port.h"
#include "time.h"
int zystm() {
    struct timespec tim;
    clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &tim);
    long etime = (long)(tim.tv_sec * 1000) + (long)(tim.tv_nsec / 1000000);
    SET_IA(etime);
    return NORMAL_RETURN;
}
EOF

  cd /home/claude/spitbol-src/x64-main
  make 2>&1 | tail -2
  cp sbl /usr/local/bin/spitbol
  echo "SPITBOL DONE"
) &

wait
echo "Oracles ready."
```

**CSNOBOL4 `mstime.c` already returns milliseconds — no patch needed.**
**SPITBOL `systm.c` defaults to nanoseconds — always apply the patch above.**

| Binary | Invocation |
|--------|------------|
| `/usr/local/bin/spitbol` | `spitbol -b program.sno` |
| `/usr/local/bin/snobol4` | `snobol4 -b program.sno` |

---

## What This Organization Is

Two people building SNOBOL4 for every platform:

**Lon Jones Cherryholmes** (LCherryholmes) — software developer
- SNOBOL4-jvm: full SNOBOL4/SPITBOL compiler + runtime → JVM bytecode (Clojure)
- SNOBOL4-python: SNOBOL4 pattern matching library for Python (PyPI: `SNOBOL4python`)
- SNOBOL4-csharp: SNOBOL4 pattern matching library for C#
- SNOBOL4: shared corpus — programs, libraries, grammars
- SNOBOL4-tiny: native compiler → x86-64 ASM, JVM bytecode, MSIL (joint)

**Jeffrey Cooper, M.D.** (jcooper0) — medical doctor
- SNOBOL4-dotnet: full SNOBOL4/SPITBOL compiler + runtime → .NET/MSIL (C#)

Mission: **SNOBOL4 everywhere. SNOBOL4 now.**

---

## Repository Index

| Repo | Language | Status | Branch | Tests |
|------|----------|--------|--------|-------|
| [SNOBOL4-dotnet](https://github.com/SNOBOL4-plus/SNOBOL4-dotnet) | C# / .NET | Active | `main` | 1,607 passing / 0 failing |
| [SNOBOL4-jvm](https://github.com/SNOBOL4-plus/SNOBOL4-jvm) | Clojure / JVM | Active | `main` | 1,896 / 4,120 assertions / 0 failures |
| [SNOBOL4-python](https://github.com/SNOBOL4-plus/SNOBOL4-python) | Python + C | Active | `main` | — |
| [SNOBOL4-csharp](https://github.com/SNOBOL4-plus/SNOBOL4-csharp) | C# | Active | `main` | 263 passing |
| [SNOBOL4-corpus](https://github.com/SNOBOL4-plus/SNOBOL4-corpus) | SNOBOL4 | Corpus | `main` | — |
| [SNOBOL4-tiny](https://github.com/SNOBOL4-plus/SNOBOL4-tiny) | C + Python | In progress | `main` | Sprint 0-1 underway |

---

## Quick Start — Each Repo

### SNOBOL4-dotnet
```bash
git clone https://github.com/SNOBOL4-plus/SNOBOL4-dotnet.git
cd SNOBOL4-dotnet
export PATH=$PATH:/usr/local/dotnet
dotnet build Snobol4.sln -c Release -p:EnableWindowsTargeting=true
dotnet test TestSnobol4/TestSnobol4.csproj -c Release
```
> **Linux note**: Always pass `-p:EnableWindowsTargeting=true` to `dotnet build` — `Snobol4W` is a Windows GUI project and will error without it. The test project itself is cross-platform.

### SNOBOL4-jvm
```bash
git clone --recurse-submodules https://github.com/SNOBOL4-plus/SNOBOL4-jvm.git
cd SNOBOL4-jvm
lein test
```
Reference oracles: `/usr/local/bin/spitbol` (SPITBOL v4.0f), `/usr/local/bin/snobol4` (CSNOBOL4 2.3.3)

### SNOBOL4-python
```bash
git clone https://github.com/SNOBOL4-plus/SNOBOL4-python.git
cd SNOBOL4-python
pip install -e ".[dev]"
pytest tests/
```

### SNOBOL4-csharp
```bash
git clone https://github.com/SNOBOL4-plus/SNOBOL4-csharp.git
cd SNOBOL4-csharp
dotnet build -c Debug src/SNOBOL4
dotnet test tests/SNOBOL4.Tests
```


### SNOBOL4-tiny
```bash
git clone https://github.com/SNOBOL4-plus/SNOBOL4-tiny.git
cd SNOBOL4-tiny
pip install --break-system-packages -e .
pytest test/
```
Layout: `src/ir/` (IR node graph), `src/codegen/` (emit_c.py template emitter), `src/runtime/` (runtime.c/h), `test/sprint0/` through `test/sprint4/` (test suite).
Sprint plan and design: `doc/DESIGN.md`, `doc/BOOTSTRAP.md`, `doc/DECISIONS.md`.

### SNOBOL4-corpus
```bash
git clone https://github.com/SNOBOL4-plus/SNOBOL4-corpus.git
```
Layout: `benchmarks/` (canonical .sno programs), `programs/` (lon/, ebnf/, rinky/, sno/, test/).
Used as submodule at `corpus/lon` in SNOBOL4-jvm and `corpus/` in SNOBOL4-dotnet.

---

## Organization Setup Log

| Date | What Happened |
|------|---------------|
| 2026-03-09 | GitHub org `SNOBOL4-plus` created. Jeffrey (jcooper0) invited — **PENDING: accept and promote to Owner**. |
| 2026-03-09 | `SNOBOL4-dotnet` created. All 6 branches mirrored from `jcooper0/Snobol4.Net`. PAT token scrubbed via `git filter-repo`. Merged to `main`. |
| 2026-03-10 | `SNOBOL4`, `SNOBOL4-jvm`, `SNOBOL4-python`, `SNOBOL4-csharp` all created and mirrored. Submodule updated to org. PyPI Trusted Publisher configured. |
| 2026-03-10 | Personal repos archived (read-only). To be deleted ~April 10, 2026. |
| 2026-03-10 | Org profile README written and published via `.github`. |
| 2026-03-09 | `SNOBOL4` repo renamed to `SNOBOL4-corpus`. Restructured: content under `programs/`, 14 canonical benchmark programs added to `benchmarks/`. `SNOBOL4-jvm` submodule URL updated. `SNOBOL4-dotnet` gains `corpus/` submodule + `benchmarks/Program.cs` runner. |
| 2026-03-10 | Cross-engine benchmark pipeline (Step 6). SPITBOL `systm.c` patched (ns→ms). CSNOBOL4 built from source. SNOBOL4-dotnet `Time.cs` fixed (ElapsedMilliseconds). `arith_loop.sno` updated to 1M iters + TIME() wrappers. SNOBOL4-jvm uberjar fixed: thin AOT launcher `main.clj` (zero requires, dynamic delegate). Results: SPITBOL 20ms, CSNOBOL4 140ms, JVM uberjar 8486ms. |
| 2026-03-10 | **Architecture session + org profile README.** Deep review of ByrdBox.zip, SNOBOL4-tiny, and all org repos. Key articulation: Byrd Box as code generation strategy (zero dispatch vs SPITBOL's 3-instruction NEXT); Forth kernel analogy (exact, not metaphorical); natural language horizon (chomsky-hierarchy.sno, transl8r_english, WordNet, Penn Treebank in 5 lines); Beautiful.sno solves the bootstrap. Org profile README expanded and pushed to `.github` (commit `ddbf477`): added "The Discovery", "The Natural Language Horizon", SNOBOL4-tiny section with Forth table, "The Deeper Point" (Griswold/McCarthy). No code changes — documentation and architecture session only. |

---

## Standing Instruction — Problems Go in the Plan

**Every time a problem is found, it is logged here before anything else.**
Three priority levels:

- **P1 — Blocking**: breaks the build, fails tests, or loses data. Fix immediately.
- **P2 — Important**: correctness gap, portability risk, or CI gap. Fix soon.
- **P3 — Polish**: dead code, naming, docs, nice-to-have. Fix when convenient.

After updating this file, always push to headquarters (`SNOBOL4-plus/.github`).

---

## Snapshot Protocol

A **snapshot** means: the repo is in a known-good state, committed, and pushed.
A local commit without a push is not a snapshot.

**When to snapshot:**
- Whenever all tests pass (zero failures) after a meaningful change.
- At the end of every session, regardless of state (commit WIP with a `WIP:` prefix if needed).
- Before any large refactor or risky change.
- Whenever this PLAN.md is updated.

**How to snapshot (SNOBOL4-dotnet):**
```bash
export PATH=$PATH:/usr/local/dotnet
dotnet test /home/claude/SNOBOL4-dotnet/TestSnobol4/TestSnobol4.csproj -c Release 2>&1 | tail -3
# Must show: Passed! - Failed: 0 before committing a non-WIP snapshot.
cd /home/claude/SNOBOL4-dotnet && git add -A && git commit -m "..." && git push
```

**Checklist before declaring a zero-failure snapshot:**
1. `dotnet test` shows `Failed: 0`.
2. Plugin DLLs are current — enforced automatically by the `ProjectReference` build-only
   deps added to `TestSnobol4.csproj` on 2026-03-10.  No manual plugin rebuilds needed.
3. `git push` completed — the remote is up to date.
4. PLAN.md updated with new test count and session log entry, then pushed to `.github`.

---

## Handoff Protocol

At the end of every session — whether work is complete or mid-stream — perform
the full handoff before closing. This is what the next Claude session needs to
pick up without re-explanation.

**Steps:**

1. **Snapshot all repos with work** (see Snapshot Protocol above).
   Commit + push every repo that was touched, even WIP. WIP commits get a `WIP:` prefix.

2. **Update PLAN.md** (this file):
   - Check off completed items in Outstanding Items.
   - Add new problems discovered during the session.
   - Add a session log entry: what was done, commit hashes, new test baseline.
   - Update the repo index test counts.
   - Push to `.github`.

3. **Update all other MD files** affected by the session's changes:
   - `ASSESSMENTS.md` — test counts, gaps resolved, new gaps found.
   - `BENCHMARKS.md` — if any benchmark numbers changed.
   - Repo-level `README.md` — if public-facing behavior changed.
   - Push each affected repo.

4. **Write the handoff prompt** — a small text block (fits in one chat input box)
   for the next Claude session. It must contain:
   - One sentence on what the project is.
   - Current test baseline for each active repo.
   - What was just completed this session (one line).
   - What to do next (one line).
   - Where to start.

   Template:
   ```
   SNOBOL4-plus org: two-person project building SNOBOL4 for every platform.
   Repos: SNOBOL4-dotnet ({pass}/{fail}), SNOBOL4-jvm ({tests}/{assertions}/0).
   Just done: {one line summary of this session}.
   Next: {top P1/P2 item from PLAN.md}.
   Start: clone all repos per PLAN.md, then read /home/claude/.github/PLAN.md.
   ```

---

## Outstanding Items

### P1 — Blocking
- [x] **SNOBOL4-dotnet**: `ErrorJump` field missing from `Executive.cs` — build failed entirely. Added `internal int ErrorJump` to `Executive` partial class. Build now clean (0 errors, 5 warnings). *(fixed 2026-03-09)*
- [x] **SNOBOL4-dotnet**: `MathLibrary` and `FSharpLibrary` not in `Snobol4.sln` and not referenced by `TestSnobol4.csproj` — on a clean clone `dotnet test` will not build plugin DLLs. Fixed: added both to solution; added all three plugin projects as `ProjectReference ReferenceOutputAssembly="false"` in `TestSnobol4.csproj` so MSBuild rebuilds them automatically before every test run. *(fixed 2026-03-10, commit `3bce92c`)*
- [ ] Jeffrey accepts GitHub org invitation → promote jcooper0 to Owner at https://github.com/orgs/SNOBOL4-plus/people

### P2 — Important
- [x] **SNOBOL4-dotnet**: 10 test failures — all fixed in commit `3bce92c` (2026-03-10), 1466/0:
  - `Step6_InitFinalize_StatementLimitAborts` — `StatementControl.cs`: catch `CompilerException` in threaded path so error 244 is recorded in `ErrorCodeHistory` rather than propagating uncaught.
  - 7 real-format tests — `RealConversionStrategy.TweakRealString`: suffix was `.0`; correct per SPITBOL (`sbl.min` gts27) and CSNOBOL4 (`lib/realst.c`) is trailing dot only — `"25."` not `"25.0"`. Changed to `str + "."`. Test assertions updated.
  - `Load_Area_FailureBranchBadClass`, `Load_Area_FailureBranchMissingFile` — `Load.cs`: call `NonExceptionFailure()` instead of `LogRuntimeException()` so `:F` branch is taken on LOAD() error.
- [ ] **SNOBOL4-dotnet**: No CI. F# is included in .NET 10 SDK (no separate workload needed — confirmed). Add GitHub Actions workflow: build solution in order, run full test suite. *(added then removed 2026-03-10 — revisit when needed)*
- [x] **SNOBOL4-dotnet** `benchmarks/Benchmarks.csproj` targets `net8.0` — should be `net10.0`. *(fixed 2026-03-10, commit `defc478`)*
- [ ] Verify SNOBOL4python 0.5.1 published to PyPI (check Actions tab)
- [ ] Remove old PyPI Trusted Publisher (`LCherryholmes/SNOBOL4python`)
- [ ] **SNOBOL4-jvm Sprint 23E**: inline EVAL! in JVM codegen — eliminate arithmetic bottleneck
- [x] **Snocone Step 2: expression parser** — `&&`, `||`, `~`, all comparison ops, `$`, `.`, precedence table. Steps 0 and 1 complete. See **Snocone Front-End Plan** section below. *(JVM: grammar + emitter done, 49 tests green, commit `9cf0af3`. dotnet: shunting-yard, 35 tests, commit `63bd297`.)*
- [ ] **SNOBOL4-python / SNOBOL4-csharp**: cross-validate pattern semantics against JVM
- [ ] Build unified cross-platform test corpus
- [ ] **Cross-engine coverage grid** — run the existing test suite against each engine and
  collect pass/fail into `SNOBOL4-corpus/COVERAGE.md`. The suite already provides coverage;
  this is purely a reporting/collection task. Grid dimensions:
  - **Rows**: individual functions, keywords (&ANCHOR, &TRIM, &STLIMIT, …), pattern
    primitives (BREAK, SPAN, ARB, ARBNO, FENCE, BAL, POS, RPOS, …), and language
    features (DEFINE/RETURN/FRETURN, recursion, indirect $, OPSYN, CODE(), named I/O,
    -INCLUDE, DATA()).
  - **Columns**: SPITBOL, CSNOBOL4, SNOBOL4-dotnet, SNOBOL4-jvm.
  - **Cells**: pass / fail / not-applicable / untested.
  - Source of truth is the test suite output — no manual entry. A script harvests
    results from `lein test` (JVM) and `dotnet test` (dotnet) and maps test names
    to feature categories.

### P3 — Polish
- [ ] **Execution control triad: `&STCOUNT` / `&STLIMIT` / `&TRACE`** — These three keywords form a complete development and testing tool inherited from the original SIL design. `&STCOUNT` tells you exactly where execution is. `&STLIMIT` stops execution at a given statement count — killing infinite loops and enabling binary search to the exact statement where behavior diverges. `&TRACE` shows what is happening as it happens. Workflow: run the same program on CSNOBOL4, SPITBOL, and our engine; compare `&STCOUNT` at failure; binary search with `&STLIMIT` to isolate the diverging statement instantly without a debugger. CSNOBOL4 disables `&STCOUNT` incrementing by default (`&STLIMIT = -1`) as a 1990s speed optimization — on modern hardware the counter increment is essentially free. Our dotnet and JVM engines should keep `&STCOUNT` always enabled. Speed-disable is a low priority.
- [ ] **SNOBOL4-dotnet**: `WindowsDll` and `LinuxDll` in `SetupTests.cs` are declared but never used — dead variables, remove.
- [ ] **SNOBOL4-dotnet**: `Test0.Test.cs` and `CTest_CODE0_NTest_CODE0.cs` contain hardcoded `C:\Users\jcooper\...` absolute paths — both are excluded from compilation but should be cleaned up or deleted.
- [x] Write org profile README — done 2026-03-10, commit `ddbf477`
- [ ] Write individual repo READMEs for all five repos (org README updated; individual repo READMEs still needed)
- [ ] Delete four archived personal repos after April 10, 2026

---

---
---

# Snocone Front-End Plan

## What This Is

A clean, purpose-built Snocone compiler written from scratch — targeting our own
IR directly, not generating intermediate SNOBOL4 text. No bootstrap required.
Snocone (Andrew Koenig, AT&T Bell Labs, 1985) adds C-like syntactic sugar to
SNOBOL4: `if/else`, `while`, `do/while`, `for`, `procedure`, `struct`, `&&`
explicit concatenation, `#include`. Same semantics as SNOBOL4. Just better syntax.

**Why:** SNOBOL4's goto-only control flow makes large programs hard to write and
read. Snocone fixes the syntax without changing any semantics. Our compilers
already handle the hard parts (patterns, backtracking, GOTO runtime). The
Snocone front-end is just a parser that desugars into what we already emit.

**Reference material**: `SNOBOL4-corpus/programs/snocone/`
- `snocone.sc` — the original compiler written in Snocone (reference + test)
- `snocone.snobol4` — compiled SNOBOL4 output (reference oracle)
- `report.htm` / `report.md` — Andrew Koenig's spec (USENIX 1985)

## Architecture

```
.sc source
    → Lexer        → tokens
    → Parser       → AST
    → Code gen     → SNOBOL4 IR  (same IR both engines already consume)
```

The code generator is tiny because SNOBOL4 is tiny. Every Snocone control
structure desugars to labels + gotos. `procedure` desugars to `DEFINE()` +
label. `struct` desugars to `DATA()`. `&&` → blank concatenation.

**For SNOBOL4-dotnet**: `SnoconeCompiler.cs` in `Snobol4.Common/Builder/`.
Invoked before the existing lexer when source has `.sc` extension or `--snocone` flag.
Output feeds directly into the existing `Lexer` → `Parser` → `Builder` pipeline.

**For SNOBOL4-jvm**: `snocone.clj` in `src/snobol4clojure/`.
Called from `compiler.clj` before `CODE!`. Returns the same IR maps.

## Incremental Milestones

| Step | What | Dotnet | JVM |
|------|------|--------|-----|
| 0 | Corpus: add Snocone reference files to SNOBOL4-corpus | ✓ `ab5f629` | ✓ `ab5f629` |
| 1 | Lexer: tokenize `.sc` correctly (identifiers, operators, strings, `#`) | ✓ `dfa0e5b` | ✓ `d1dec27` |
| 2 | Expression parser: `&&`, `\|\|`, `~`, `==`, `<=`, `*deferred`, `$`, `.` | ✓ dotnet `63bd297` | ✓ JVM `9cf0af3` |
| 3 | `if/else` → label/goto pairs | | |
| 4 | `while` / `do/while` → loop labels | | |
| 5 | `for (e1, e2, e3)` → init/test/step labels | | |
| 6 | `procedure` → `DEFINE()` + label + `:(RETURN)` | | |
| 7 | `struct` → `DATA()` | | |
| 8 | `#include` → file inclusion (reuse existing `-INCLUDE`) | | |
| 9 | Self-test: compile `snocone.sc` and diff output against `snocone.snobol4` | | |

Each step: write tests first, then implement, then confirm baseline still green.

## Key Semantic Rules (from Koenig spec)

- **Statement termination**: newline ends statement unless last token is an
  operator or open bracket (then continues). Semicolon also ends statement.
- **Concatenation**: `&&` (explicit) replaces blank (implicit). In generated
  SNOBOL4, `&&` → blank.
- **Comparison predicates**: `==`, `!=`, `<`, `>`, `<=`, `>=` → `EQ`, `NE`,
  `LT`, `GT`, `LE`, `GE`. String comparisons: `:==:` etc → `LEQ` etc.
- **`~`** (logical negation): if operand fails, `~` yields null; if succeeds, fails.
  In SNOBOL4: wrap in `DIFFER()` / `IDENT()` as appropriate.
- **`||`** (disjunction): left succeeds → value is left. Else value is right.
  In SNOBOL4: pattern alternation `|`.
- **`if (e) s1 else s2`** desugars to:
  ```
          e                    :F(sc_else_N)
          [s1]                 :(sc_end_N)
  sc_else_N [s2]
  sc_end_N
  ```
- **`while (e) s`** desugars to:
  ```
  sc_top_N  e                  :F(sc_end_N)
            [s]                :(sc_top_N)
  sc_end_N
  ```
- **`procedure f(a,b; local c,d)`** desugars to:
  ```
          DEFINE('f(a,b)c,d')  :(f_end)
  f       [body]               :(RETURN)
  f_end
  ```
- **Labels**: all global (SNOBOL4 constraint). Generated labels use `sc_N`
  prefix to avoid collisions. User labels pass through unchanged.

## Label Generation

Both implementations use a shared monotonic counter `sc_label_counter`.
Generated labels: `sc_1`, `sc_2`, etc. Never reused within a compilation unit.

## Session Log — Snocone

| Date | What |
|------|------|
| 2026-03-10 | Plan written. Corpus populated: `snocone.sc`, `snocone.sno`, `snocone.snobol4`, Koenig spec, README added to `SNOBOL4-corpus/programs/snocone/`. commit `ab5f629`. Step 1 (lexer) is next. |
| 2026-03-10 | **Licence research**: Phil Budne README states Emmer-restricted no-redistribution on snocone sources. Confirmed: `regressive.org/snobol4/csnobol4/curr/` updated May 2025 still states the restriction. Mark Emmer GPL'd SPITBOL 360 (2001) and Macro SPITBOL (2009) but Snocone restriction stands. |
| 2026-03-10 | **Corpus cleanup**: Removed `snocone.sc`, `snocone.sno`, `snocone.snobol4` (Emmer-restricted). Added Budne's 4 patch files (`README`, `snocone.sc.diff`, `snocone.sno.diff`, `Makefile`). Updated corpus README with three-party attribution + download instructions. SNOBOL4-corpus commit `b101a07`. |
| 2026-03-10 | **Step 1 complete — Snocone lexer (both targets)**. `SnoconeLexer.cs` + 57 tests (`TestSnoconeLexer.cs`) in SNOBOL4-dotnet commit `dfa0e5b`. `snocone.clj` + equivalent tests (`test_snocone.clj`) in SNOBOL4-jvm commit `d1dec27`. Self-tokenization of `snocone.sc`: 5,526 tokens, 728 statements, 0 unknown. Bug fixed in Clojure tokenizer (spurious `seg` arg). Step 2 (expression parser) is next. |
| 2026-03-10 | **Step 2 complete — Expression parser (both targets)**. dotnet: shunting-yard `SnoconeParser.cs` + 35 tests (`TestSnoconeParser.cs`), commit `63bd297`. JVM: instaparse PEG grammar (`snocone_grammar.clj`) + `insta/transform` emitter (`snocone_emitter.clj`) + 35 tests (`test_snocone_parser.clj`), all real snocone.sc expressions parse. Grammar fixes: real before integer in atom, capop excludes digit-following dot, juxtaposition concat (blank), `?` removed from unary ops, aref tag for `[...]`. `scan-number` OOM bug fixed (leading-dot infinite loop). JVM commit `9cf0af3`. Step 3 (`if/else`) is next. |

---
---

## Key Decisions (Permanent)

1. **Canonical repos are in the org.** Personal repos are archived and will be deleted.
2. **All default branches are `main`.**
3. **SNOBOL4-jvm submodule** points to `SNOBOL4-plus/SNOBOL4-corpus` (at `corpus/lon`). **SNOBOL4-dotnet submodule** points to `SNOBOL4-plus/SNOBOL4-corpus` (at `corpus`).
4. **PyPI publishes from `SNOBOL4-plus/SNOBOL4-python`** via Trusted Publisher (OIDC, no token).
5. **Jeffrey's authorship is preserved.** His commit history is intact throughout.
6. **This file is the single plan for all repos.** There are no separate per-repo PLAN.md files.

---

## Git Identity
```
user.name  = LCherryholmes
user.email = lcherryh@yahoo.com
```
Token: stored securely — do not commit. Request from user at session start if needed.

**How the user provides the token (encoded for security):**
The user pastes it as two words: `_<rest_of_token> <reverse_prefix>` (e.g. `_trYPI... phg`).
- The second word reversed gives the prefix: e.g. `phg` → `ghp`, so the full token is `ghp_<rest_of_token>`.
- The encoding keeps the plaintext token out of the chat transcript.

**CRITICAL — Claude must NEVER reconstruct or echo the plaintext token in any chat response.**
Decode it silently in bash only. Never write `ghp_...` in a chat message. Never confirm the
reconstructed value out loud. Use it only inside shell commands where it is not visible in the
chat transcript. This is the whole point of the encoding scheme.

Use in git remote URL (in bash only, never echoed to chat):
```bash
TOKEN=<decoded silently in shell>
git remote set-url origin https://LCherryholmes:$TOKEN@github.com/SNOBOL4-plus/<REPO>.git
```
Set this on every repo that needs pushing at the start of each session. Do NOT commit the token.

---
---

# SNOBOL4-jvm — Full Plan

## What This Repo Is

A complete SNOBOL4/SPITBOL implementation in Clojure targeting JVM bytecode.
Full semantic fidelity: pattern engine with backtracking, captures, alternation,
TABLE/ARRAY, GOTO-driven runtime, multi-stage compiler.

**Repository**: https://github.com/SNOBOL4-plus/SNOBOL4-jvm
**Test runner**: `lein test` (Leiningen 2.12.0, Java 21)
**Baseline**: 1,896 tests / 4,120 assertions / 0 failures — commit `9cf0af3` (2026-03-10)

---

## Session Log — SNOBOL4-jvm

| Date | Baseline | What Happened |
|------|----------|---------------|
| 2026-03-08 | 220/548/0 | Repo cloned; baseline confirmed. SPITBOL and CSNOBOL4 source archives uploaded. |
| 2026-03-08 (s4) | 967/2161/0 | SEQ nil-propagation fix; NAME indirect subscript fix. commit `fbcde8e`. |
| 2026-03-08 (S19) | 2017/4375/0 | Variable shadowing fix — `<VARS>` atom replaces namespace interning. commit `9811f5e`. |
| 2026-03-08 (S18B) | 1488/3249/0 | Catalog directory created. 13 catalog files. Step-probe bisection debugger (18C). |
| 2026-03-08 (S23A–D) | 1865/4018/0 | EDN cache (22×), Transpiler (3.5–6×), Stack VM (2–6×), JVM bytecode gen (7.6×). |
| 2026-03-08 (S25A–E) | — | -INCLUDE preprocessor, TERMINAL, CODE(), Named I/O channels, OPSYN. |
| 2026-03-09 (s15) | **2033/4417/0** | All Sprint 25 confirmed. Stable baseline `e697056`. |
| 2026-03-10 | **2033/4417/0** | Cross-engine benchmark pipeline (Step 6). Built SPITBOL (systm.c → ms) and CSNOBOL4 from source. arith_loop.sno at 1M iters: SPITBOL 20ms, CSNOBOL4 140ms, JVM uberjar 8486ms. Uberjar fixed via thin AOT launcher (main.clj) — zero requires, delegates to core at runtime. Preserves all Greek/symbol names in env/operators/engine_frame/match. commit `80c882e`. |
| 2026-03-10 | **1896/4120/0** | Snocone Step 2 complete: instaparse PEG grammar + emitter + 35 tests. Test suite housekeeping: arithmetic exhaustive (188→20), cmp/strcmp exhaustive (66→18), 4 duplicate test names fixed. `scan-number` OOM bug fixed (leading-dot real infinite loop). Commits `e8ae21b`…`9cf0af3`. |

---

## Oracle Setup — SNOBOL4-jvm

Source archives in `/mnt/user-data/uploads/`. Extract at session start:
```bash
mkdir -p /home/claude/csnobol4-src /home/claude/spitbol-src
tar xzf /mnt/user-data/uploads/snobol4-2_3_3_tar.gz -C /home/claude/csnobol4-src/ --strip-components=1 &
unzip -q /mnt/user-data/uploads/x64-main.zip -d /home/claude/spitbol-src/ &
wait
apt-get install -y build-essential libgmp-dev m4 nasm

# Patch SPITBOL systm.c: nanoseconds → milliseconds (REQUIRED — default is ns)
cat > /home/claude/spitbol-src/x64-main/osint/systm.c << 'EOF'
#include "port.h"
#include "time.h"
int zystm() {
    struct timespec tim;
    clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &tim);
    long etime = (long)(tim.tv_sec * 1000) + (long)(tim.tv_nsec / 1000000);
    SET_IA(etime);
    return NORMAL_RETURN;
}
EOF

# Build both in parallel
(cd /home/claude/csnobol4-src && ./configure --prefix=/usr/local 2>&1|tail -1 && make -j4 && make install && echo "CSNOBOL4 DONE") &
(cd /home/claude/spitbol-src/x64-main && make && cp sbl /usr/local/bin/spitbol && echo "SPITBOL DONE") &
wait
```
**CSNOBOL4 `mstime.c` already returns milliseconds — no patch needed.**
**SPITBOL `systm.c` defaults to nanoseconds — always apply the patch above.**

| Binary | Version | Invocation |
|--------|---------|------------|
| `/usr/local/bin/spitbol` | SPITBOL v4.0f | `spitbol -b -` |
| `/usr/local/bin/snobol4` | CSNOBOL4 2.3.3 | `snobol4 -` |

Three-oracle triangulation: both agree → use agreed output. Disagree → use SPITBOL, flag for review.

---

## File Map — SNOBOL4-jvm

| File | Responsibility |
|------|----------------|
| `env.clj` | globals, DATATYPE, NAME/SnobolArray deftypes, `$$`/`snobol-set!`, TABLE/ARRAY |
| `primitives.clj` | scanners: LIT$, ANY$, SPAN$, NSPAN$, BREAK$, BREAKX$, POS#, RPOS#, LEN#, TAB#, RTAB#, BOL#, EOL# |
| `match.clj` | MATCH state machine engine + SEARCH/MATCH/FULLMATCH/REPLACE/COLLECT! |
| `patterns.clj` | pattern constructors: ANY, SPAN, NSPAN, BREAK, BREAKX, BOL, EOL, POS, ARBNO, FENCE, ABORT, REM, BAL, CURSOR, CONJ, DEFER |
| `functions.clj` | built-in fns: REPLACE, SIZE, DATA, ASCII, CHAR, REMDR, INTEGER, REAL, STRING, INPUT, ITEM, PROTOTYPE |
| `grammar.clj` | instaparse grammar + parse-statement/parse-expression |
| `emitter.clj` | AST to Clojure IR transform |
| `compiler.clj` | CODE!/CODE: source text to labeled statement table; -INCLUDE preprocessor |
| `operators.clj` | operators, EVAL/EVAL!/INVOKE, comparison primitives |
| `runtime.clj` | RUN: GOTO-driven statement interpreter |
| `core.clj` | thin facade, explicit re-exports of full public API |
| `harness.clj` | Three-oracle diff harness |
| `generator.clj` | Worm test generator: rand-* and gen-* tiers |
| `jvm_codegen.clj` | Stage 23D: ASM-generated JVM `.class` bytecode |
| `transpiler.clj` | Stage 23B: SNOBOL4 IR → Clojure `loop/case` fn |
| `vm.clj` | Stage 23C: flat bytecode stack VM |

---

## Sprint History — SNOBOL4-jvm

| Sprint | Commit | Tests | What |
|--------|--------|-------|------|
| Sprints 6–14 | various | 220/548 | Runtime, patterns, engine, harness, oracle setup |
| Sprint 18D | `fbcde8e` | 967/2161/0 | SEQ nil-propagation; NAME indirect subscript fix |
| Sprint 18B | `0b5161c` | 1488/3249/0 | Catalog directory, 13 files |
| Sprint 18C | done | — | Step-probe bisection debugger |
| Session 11 | `555bd39` | 1749/3786/0 | Fix recursive DEFINE |
| Session 12–12c | various | 1865/4018/0 | RTAB/TAB, goto case folding, worm tests |
| Session 13–13d | various | 1865/4018/0 | Stages 23A–23D complete |
| Sprint 19 | `9811f5e` | 2017/4375/0 | Variable shadowing fix |
| Sprint 25A | `41eea5d` | — | -INCLUDE preprocessor |
| Sprint 25B | `28db14b` | — | LGT wired into INVOKE |
| Sprint 25C | `5bd8a38` | — | TERMINAL variable |
| Sprint 25D | `29e3b64` | 2030/4403/0 | Named I/O channels |
| Sprint 25E | `e697056` | **2033/4417/0** | OPSYN — **current baseline** |
| Sprint 25F | `5fbc8ea` | — | CODE(src) |

---

## Open Issues — SNOBOL4-jvm

| # | Issue | Status |
|---|-------|--------|
| 1 | CAPTURE-COND (`.`) assigns immediately like `$`; deferred-assign infra not built | Open |
| 2 | ANY(multi-arg) inside EVAL string — ClassCastException | Open |
| 3 | Sprint 23E — inline EVAL! in JVM codegen (arithmetic bottleneck) | **NEXT** |

All previous issues (variable shadowing, RTAB/TAB, goto case, NAME indirect, DEFINE recursion) are fixed.

---

## Acceleration Architecture — SNOBOL4-jvm (Sprint 23+)

| Stage | What | Status |
|-------|------|--------|
| 23A — EDN cache | Skip grammar+emitter via serialized IR | **DONE** `b30f383` — 22× per-program |
| 23B — Transpiler | SNOBOL4 IR → Clojure `loop/case`; JVM JIT | **DONE** `4ed6b7e` — 3.5–6× |
| 23C — Stack VM | Flat bytecode, 7 opcodes, two-pass compiler | **DONE** `d9e4203` — 2–6× |
| 23D — JVM bytecode gen | ASM-generated `.class`, DynamicClassLoader | **DONE** `c185893` — 7.6×; EVAL! still bottleneck |
| 23E — Inline EVAL! | Emit arith/assign/cmp directly into JVM bytecode | **NEXT** |
| 23F — Compiled pattern engine | Compile pattern objects to Java methods | PLANNED |
| 23G — Integer unboxing | Emit `long` primitives for integer variables | PLANNED |
| 23H — AOT .jar corpus cache | Skip re-transpile on repeated runs | PLANNED |
| 23I — Parallel worm/test runner | `pmap` across worm batch | PLANNED |
| 23J — GraalVM native-image | Standalone binary, 10ms startup | VISION |

**Key insight**: The IR produced by `CODE!` is already pure, serializable EDN — a hierarchical, homoiconic assembly language. Immutable at the IR level; only variable environment is mutable. This maps perfectly to the JVM model: code segment (immutable `.class`) + heap (mutable state).

---

## Corpus Plan — SNOBOL4-jvm (Sprint 25 continued)

### Remaining Gimpel programs (unblocked by Named I/O)
- `BCD_EBCD.SNO`, `INFINIP.SNO`, `L_ONE.SNO`, `L_TWO.SNO` — stdin only
- `POKER`, `RPOEM`, `RSEASON`, `RSTORY`, `STONE`, `ASM` — need named file I/O (now available)

### beauty.sno — the flagship
Self-contained SNOBOL4 beautifier (Lon Cherryholmes, 2002–2005). Reads SNOBOL4 source from stdin, builds parse tree, pretty-prints to stdout. Pipe it through itself.

**Blocker**: 19 `-INCLUDE` files (must be supplied by Lon). `-INCLUDE` preprocessor now done.

```bash
cat beauty.sno | snobol4clojure beauty.sno    # beautify itself from stdin
```

---

## Design Decisions (Immutable) — SNOBOL4-jvm

1. **ALL UPPERCASE keywords.** No case folding.
2. **Single-file engine.** `match.clj` is one `loop/case`. Cannot be split.
3. **Immutable-by-default, mutable-by-atom.** TABLE and ARRAY use `atom`.
4. **Label/body whitespace contract.** Labels flush-left, bodies indented.
5. **INVOKE is the single dispatch point.** Add both lowercase and uppercase entries.
6. **nil means failure; epsilon means empty string.**
7. **`clojure.core/=` inside `operators.clj`.** Bare `=` builds IR lists. Use `clojure.core/=` or `equal`.
8. **INVOKE args are pre-evaluated.** Never call `EVAL!` on args inside INVOKE.
9. **Two-tier generator discipline.** `rand-*` probabilistic. `gen-*` exhaustive lazy.
10. **Typed pools are canonical fixtures.** `I J K L M N` integers, `S T X Y Z` strings, `P Q R` patterns, `L1 L2` labels.
11. **Two-strategy debugging.** (a) run a probe; (b) read CSNOBOL4/SPITBOL source. Never speculate.

---

## Key Semantic Notes — SNOBOL4-jvm

**BREAK vs BREAKX**: `BREAK(cs)` does not retry on backtrack. `BREAKX(cs)` slides one char past each break-char on backtrack.

**FENCE**: `FENCE(P)` commits to P's match; backtracking INTO P blocked. `FENCE()` bare aborts the entire match.

**CONJ** (extension — no reference source): `CONJ(P, Q)` — P determines span, Q is pure assertion. Not in SPITBOL, CSNOBOL4, or standard SNOBOL4.

**$ vs . capture**: `P $ V` — immediate assign. `P . V` — conditional on full MATCH success. (Currently both assign immediately — deferred infra pending.)

**Operator precedence** (from v311.sil): `**`(50/50, right-assoc) > `*`/`/` > concat > `+`/`-` > `|`.

**Debugging file map**:
| Question | File |
|----------|------|
| ARBNO/ARB backtrack | `csnobol4-src/test/v311.sil` lines ~8254–8310 |
| ARBNO build | `csnobol4-src/snobol4.c` `ARBNO()` ~line 3602 |
| Dot (.) capture | `spitbol-src/bootstrap/sbl.asm` `p_cas` ~line 4950 |
| Pattern match dispatcher | `csnobol4-src/snobol4.c` `PATNOD()` ~line 3529 |
| CONJ | No reference — SNOBOL4clojure extension |

---

## Tradeoff Prompt — SNOBOL4-jvm

> **Read this before every design decision in SNOBOL4-jvm.**

1. **Single-file engine.** `match.clj` is one `loop/case`. `recur` requires all targets in the same function body. Do not refactor.
2. **Immutable-by-default, mutable-by-atom.**
3. **Label/body whitespace contract.** Labels flush-left, bodies indented. Tests must always indent statement bodies.
4. **INVOKE is the single dispatch point.** Add both lowercase and uppercase entries for every new function.
5. **nil means failure; epsilon means empty string.**
6. **ALL keywords UPPERCASE.**
7. **`clojure.core/=` inside `operators.clj`.** Bare `=` builds IR lists.
8. **INVOKE args are pre-evaluated.** Never call `EVAL!` on args arriving in INVOKE.
9. **Two-tier generator discipline.** `rand-*` probabilistic. `gen-*` exhaustive lazy.
10. **Typed pools are canonical fixtures.**

---
---

# SNOBOL4-dotnet — Full Plan

## What This Repo Is

Full SNOBOL4/SPITBOL implementation in C# targeting .NET/MSIL. GOTO-driven runtime, threaded bytecode execution, MSIL delegate JIT compiler, plugin system (LOAD/UNLOAD), Windows GUI (Snobol4W.exe).

**Repository**: https://github.com/SNOBOL4-plus/SNOBOL4-dotnet
**Test runner**: `dotnet test TestSnobol4/TestSnobol4.csproj -c Release`
**Baseline**: 1,607 passing / 0 failing (2026-03-10, commit `63bd297`)

```bash
cd SNOBOL4-dotnet
export PATH=$PATH:/usr/local/dotnet
dotnet build -c Release
dotnet test TestSnobol4/TestSnobol4.csproj -c Release
```

---

## Session Log — SNOBOL4-dotnet

| Date | What Happened |
|------|---------------|
| 2026-03-05 | Threaded execution refactor (Phases 1–5) complete. 15.9× speedup over Roslyn baseline on Roman. |
| 2026-03-06 | UDF savedFailure bug fixed (`var savedFailure = Failure` not `ErrorJump > 0`). Phase 9: Roslyn removal + arg list pooling. Phase 10: integer fast path. |
| 2026-03-07 | MSIL emitter Steps 1–13 complete. LOAD/UNLOAD plugin system. 1,413 → 1,484 tests. All merged to `main`. |
| 2026-03-10 | Fixed all 10 failing tests (commit `3bce92c`): real-to-string format (`"25."` not `"25.0"` — verified against SPITBOL `sbl.min` and CSNOBOL4 `realst.c`); LOAD() `:F` branch on error; `&STLIMIT` exception swallowed gracefully. Plugin DLLs now auto-built via `ProjectReference` build-only deps in `TestSnobol4.csproj`. Baseline: **1,466 / 0**. |
| 2026-03-10 | Fixed `benchmarks/Benchmarks.csproj` `net8.0` → `net10.0`. commit `defc478`. |
| 2026-03-10 | Added then removed GitHub Actions CI workflow — was triggering unwanted email notifications. commit `d212c85`. |
| 2026-03-10 | Documented `EnableWindowsTargeting=true` required for Linux builds (`Snobol4W` is Windows-only). Always pass `-p:EnableWindowsTargeting=true` to `dotnet build Snobol4.sln`. |
| 2026-03-10 | Confirmed 1,466/0 baseline under .NET 10 locally (`dotnet test` runs in ~17s). |
| 2026-03-10 | **Snocone Step 2 complete**: `SnoconeParser.cs` shunting-yard + 35 tests, 1607/0. commit `63bd297`. |

---

## Solution Layout — SNOBOL4-dotnet

```
Snobol4.Common/
  Builder/
    Builder.cs              ← compile pipeline (BuildMain, BuildCode, BuildEval, BuildForTest)
    BuilderResolve.cs       ← ResolveSlots() — VariableSlots, FunctionSlots, Constants
    BuilderEmitMsil.cs      ← MSIL delegate JIT compiler (Steps 1–13 complete)
    ThreadedCodeCompiler.cs ← emits Instruction[] from token lists
    Instruction.cs          ← OpCode enum + Instruction struct
    Token.cs                ← Token.Type enum + Token class
    ConstantPool.cs         ← interned Var pool
    FunctionSlot.cs / VariableSlot.cs
  Runtime/Execution/
    ThreadedExecuteLoop.cs  ← main dispatch loop
    ExecutionCache.cs       ← VarSlotArray, OperatorHandlers, OperatorFast()
    StatementControl.cs     ← RunExpressionThread()
    Executive.cs            ← partial class root, _reusableArgList
    MsilHelpers.cs          ← InitStatement, FinalizeStatement, ResolveLabel helpers
TestSnobol4/
  MsilEmitterTests.cs       ← MSIL emitter tests (Steps 1–13)
  ThreadedCompilerTests.cs
```

---

## MSIL Emitter — Steps 1–13 (All Complete)

`BuilderEmitMsil.cs` JIT-compiles each statement's expression-level token list into a `DynamicMethod` / `Func<Executive, int>` delegate at program load time. One `CallMsil` opcode invokes the cached delegate, replacing individual opcodes with a straight-line native call sequence.

| Step | What | Status |
|------|------|--------|
| 1–5 | Scaffolding, expression emission, var reads/writes, full operator coverage | **DONE** |
| 6 | Inline Init/Finalize into delegates | **DONE** |
| 7 | Delegate signature → `Func<Executive, int>` returning next IP | **DONE** |
| 8 | Absorb fall-through gotos | **DONE** |
| 9 | Absorb direct unconditional gotos `:(LABEL)` via `ResolveLabel()` | **DONE** |
| 10 | Absorb direct conditional gotos `:S/:F` via `ResolveGotoOrFail()` | **DONE** |
| 11 | Absorb indirect/computed gotos; `GotoIndirect`/`GotoIndirectCode` absorbed | **DONE** |
| 12 | Collapse execute loop — hot path is `CallMsil` + `Halt` only | **DONE** |
| 13 | TRACE hooks — TRACE/STOPTR callable from SNOBOL4 | **DONE** |

**Delegate return convention**: `>= 0` = jump to IP; `-1` = halt; `int.MinValue` = fall through.

---

## Next Step — SNOBOL4-dotnet

### Step 14 — Eliminate `Instruction[]` entirely (stretch goal)
Store delegates directly in `Func<Executive, int>[]`. Execute loop becomes:
```csharp
var stmts = StatementDelegates;
int ip = entryStatementIdx;
while (ip >= 0 && ip < stmts.Length)
{
    ip = stmts[ip](this);
    if (ip == int.MinValue) ip++;  // fall through
}
```
**Acceptance**: `PureDelegate_ThreadArrayGone` test passes. Full 1,484 suite green.

---

## Invariants — SNOBOL4-dotnet

- **1,484 tests green after every commit.**
- **Roslyn path (`UseThreadedExecution = false`)** must keep working via `LegacyDispatch()`.
- **`BuildEval` / `BuildCode`** must call `EmitMsilForAllStatements()` before next execute cycle.
- **Recursive `ThreadedExecuteLoop`** — `savedIP` / `savedFailure` / `savedErrorJump` save-restore discipline must be preserved.
- **`LastExpressionFailure`** — set just before `Done:` in the current loop; `RunExpressionThread` reads it.

---

## Open Issues — SNOBOL4-dotnet

| # | Issue | Severity |
|---|-------|----------|
| 1 | Pattern.Bal — hangs under threaded execution | Medium |
| 2 | Deferred expressions in patterns `pos(*A)` — TEST_Pos_009 | Low |
| 3 | TestGoto _DIRECT — CODE() dynamic compilation | Medium |
| 4 | OPSYN custom operator `!` alias | Low |
| 5 | DLL loading tests require local build of AreaLibrary.dll | Low |
| 6 | Function.InputOutput — hangs on Linux (hardcoded Windows paths) | Low |

---

## Token.Type Reference — SNOBOL4-dotnet

| Draft name | Actual `Token.Type` |
|------------|---------------------|
| `PLUS` | `BINARY_PLUS` |
| `MINUS` | `BINARY_MINUS` |
| `STAR` | `BINARY_STAR` |
| `SLASH` | `BINARY_SLASH` |
| `CARET` | `BINARY_CARET` |
| `BLANK` | `BINARY_CONCAT` |
| `BAR` | `BINARY_PIPE` |
| `PERIOD` | `BINARY_PERIOD` |
| `DOLLAR` | `BINARY_DOLLAR` |
| `EQUALS` | `BINARY_EQUAL` |
| `UNARY_MINUS` … (11 separate) | `UNARY_OPERATOR` — one case, dispatch on `t.MatchedString` |

---
---

# SNOBOL4-python — Plan

## What This Repo Is

SNOBOL4 pattern matching library for Python. C extension (`sno4py`) wrapping Phil Budne's SPIPAT engine. 7–11× faster than pure Python backend.

**Repository**: https://github.com/SNOBOL4-plus/SNOBOL4-python
**PyPI**: `pip install SNOBOL4python` (version 0.5.1)

## Outstanding Items — SNOBOL4-python
- [ ] Verify 0.5.1 published to PyPI (check Actions tab in repo)
- [ ] Remove old Trusted Publisher (`LCherryholmes/SNOBOL4python`) once 0.5.1 confirmed live
- [ ] Cross-validate pattern semantics against SNOBOL4-jvm

---
---

# SNOBOL4-csharp — Plan

## What This Repo Is

SNOBOL4 pattern matching library for C#. 263 tests passing.

**Repository**: https://github.com/SNOBOL4-plus/SNOBOL4-csharp
**Test runner**: `dotnet test tests/SNOBOL4.Tests`

## Outstanding Items — SNOBOL4-csharp
- [ ] JSON tests — disabled, pending port to delegate-capture API
- [ ] Cross-validate pattern semantics against SNOBOL4-jvm

---
---

# SNOBOL4-corpus — Plan

## What This Repo Is

Shared SNOBOL4 programs, libraries, grammars, and canonical benchmark programs
for all SNOBOL4-plus implementations.

**Repository**: https://github.com/SNOBOL4-plus/SNOBOL4-corpus

## Layout

```
benchmarks/     canonical .sno benchmark programs (shared by all impl runners)
programs/
  ebnf/         EBNF grammar programs
  inc/           include files (TZ, ebnf, etc.)
  rinky/         rinky programs
  sno/           general SNOBOL4 programs
  test/          test programs
```

## Submodule Usage

| Repo | Path | Note |
|------|------|------|
| SNOBOL4-jvm | `corpus/lon` | Runner reads `corpus/lon/benchmarks/` |
| SNOBOL4-dotnet | `corpus` | Runner reads `corpus/benchmarks/` |

## Outstanding Items — SNOBOL4-corpus
- [ ] Add beauty.sno include files when Lon supplies them
- [ ] Grow unified cross-platform benchmark programs
- [ ] Add `code_goto.sno` benchmark once CODE()+GOTO is working in dotnet

---
---

# SNOBOL4-tiny — Full Plan

## What This Repo Is

A native SNOBOL4 compiler using the **Byrd Box** compilation model. Every pattern
node — and eventually every expression — compiles to four inlined labeled entry
points (α/β/γ/ω) as straight C-with-gotos. No interpreter loop. No indirect
dispatch. The wiring between nodes *is* the execution. Goal-directed evaluation
exactly like Icon, compiled to native code.

**Repository**: https://github.com/SNOBOL4-plus/SNOBOL4-tiny
**Test runner**: `cc -o $test $test.c src/runtime/runtime.c && ./$test > got.txt && diff expected.txt got.txt`
**Baseline**: Sprint 0–1 complete (hand-written reference C files). Sprints 2–4 empty.
**Language**: C (runtime + emitted programs), Python (IR builder + emitter, Stages A–B)

---

## The Language Being Compiled — Three Stages

### Stage A — Pattern Engine (Sprints 0–7): Primitives + Codegen
A single pattern runs against a hardcoded subject. No user-visible language yet.
These sprints prove the compilation model and establish the full primitive vocabulary.

### Stage B — SNOBOL4tiny Language (Sprints 8–13): The Language
A real, minimal, compiled language. This is the language Lon described:

> *"Reads only from stdin, writes only to stdout. A set of patterns.
> A set of functions for immediate/conditional actions."*

```snobol4
* A SNOBOL4tiny program is:
*   1. A set of named pattern definitions
*   2. Action functions on match: immediate ($ VAR) / conditional (. VAR)
*   3. One entry point: MAIN (or last-defined pattern)
*   Input: stdin only.  Output: stdout only.  Compiled to native code.

DIGITS  = SPAN('0123456789')
WORD    = SPAN('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
TOKEN   = DIGITS | WORD
MAIN    = POS(0) ARBNO(TOKEN $ OUTPUT) RPOS(0)
```

Properties:
- **Compiled** — emits C-with-gotos → cc → native binary
- **Goal-directed** — α/β/γ/ω Byrd Box backtracking, exactly like Icon generators
- **stdin→stdout only** — no files, no environment, no side channels
- **Patterns + action nodes** — `$ OUTPUT` is immediate; `. VAR` is conditional
- **Mutually recursive** — `*NAME` deferred REF nodes allow full CFG grammars

This is Stage C from DECISIONS.md: named patterns, mutual recursion, the minimum
that makes SNOBOL4tiny a language rather than a pattern engine. It is also
Turing-complete for string recognition — it can express any context-free grammar.

### Stage C — SNOBOL4 Subset (Sprint 14+): The Horizon
Full SNOBOL4 statement model: subject, pattern, replacement, GOTO, variables,
INPUT/OUTPUT, DEFINE, DATA, END. Programs run unchanged on CSNOBOL4 and SPITBOL.
The λ bridge from Beautiful.sno maps the parse tree shape to IR directly.

---

## Architecture

```
SNOBOL4tiny source (.sno)
    → Parser (Python / Beautiful.sno Sprint 11+)   → IR node graph
    → emit_c.py                                     → C-with-gotos (.c)
    → cc                                            → native binary
    → stdin                                         → stdout
```

**Three codegen targets from one IR (Sprint 14+):**
- C-with-gotos → cc → any C target (x86-64, ARM, RISC-V)
- JVM bytecode via ASM library → ClassLoader
- MSIL via ILGenerator → .NET DynamicMethod

---

## The Eight Irreducible Primitives

Nothing smaller can express these. Everything else is derivable and should be
written in SNOBOL4tiny, not hardcoded as C templates.

| Primitive | α behavior | β behavior |
|-----------|-----------|-----------|
| LIT(s) | Match exact string s at cursor | Restore cursor, fail |
| ANY(cs) | Match one char in charset cs | Restore cursor, fail |
| SPAN(cs) | Match 1+ chars in cs (greedy) | Give back one char, retry |
| BREAK(cs) | Match 0+ chars not in cs | Deterministic — fail |
| LEN(n) | Advance cursor by n | Restore cursor, fail |
| POS(n) | Assert cursor == n | Fail (deterministic) |
| RPOS(n) | Assert cursor == len−n | Fail (deterministic) |
| ARB | Try 0 chars first, then 1, 2… | Advance by 1, retry |

**Derived (library words, not primitives):**
`ARBNO(P)` — derivable from ARB + CAT + ALT once those work.
`TAB(n)` — derivable from POS(n) after ARB.
`RTAB(n)` — derivable from RPOS(n) after ARB.
`NOTANY(cs)` — derivable from BREAK(cs) + LEN(1).

**Discipline (Forth rule):** Before adding any node type to `emit_c.py`,
write the derivation. If it can be expressed using existing primitives, it
is a library pattern, not a primitive.

---

## Action Nodes (λ)

Action nodes fire side effects. They do not advance the cursor.

| Node | Fires | Backtracks? |
|------|-------|-------------|
| `$ VAR` (immediate assign) | Every time left pattern succeeds | No — deterministic |
| `. VAR` (conditional assign) | Only when top-level match commits | No — deferred |
| `@ CURSOR` | On match — records cursor as integer | No |
| λ(fn) | Calls a named function on match | No |

**The key distinction:** `$` fires multiple times if downstream backtracks and
re-enters the enclosing pattern. `.` fires exactly once, after commit. This is
standard SNOBOL4 semantics — preserved exactly in the compiled model.

When `VAR == OUTPUT`, `$ OUTPUT` emits the captured span to stdout immediately.
This is the primary output mechanism of the SNOBOL4tiny language.

---

## Sprint Plan — Beautiful.sno Target

**Goal**: Compile Beautiful.sno to a native binary that self-beautifies correctly
and runs faster than SPITBOL. Every sprint adds exactly one mechanism needed to
reach that goal — nothing else. Easy first, recursion last.

### The Bootstrap Strategy

The `-INCLUDE` files are **not parsed** — they are compiled directly as C.
Each `.inc` file maps cleanly to a C module. This is not a compromise; it is
the right architecture. The SNOBOL4 source of those files exists as documentation
and oracle. The C is the implementation.

**Three tiers:**

| Tier | What | How |
|------|------|-----|
| 1 | Pattern engine nodes | Hardcoded C in `engine.c` — already started |
| 2 | Runtime library (the `.inc` files) | Hardcoded C in `runtime/` — one `.c` per `.inc` |
| 3 | Beautiful.sno body | Compiled by `emit_c.py` from SNOBOL4 source |

Tier 2 is written once and never regenerated. It is a permanent C library.
Tier 3 is the proof that the compiler works.

---

### Tier 2 — Runtime Library: `.inc` → `.c` Mapping

Each row is one C file to write. Complexity is honest: trivial = one afternoon,
moderate = one day, hard = two days.

| Inc file | C file | What it provides | Complexity |
|----------|--------|-----------------|------------|
| `global.inc` | `runtime/global.c` | char constants (nl, tab, bs, etc.), `digits` string | **trivial** |
| `case.inc` | `runtime/case.c` | `lwr()`, `upr()`, `cap()`, `icase()` — string case | **trivial** |
| `is.inc` | `runtime/is.c` | `IsSpitbol()` → 0, `IsSpitbol4()` → 1, `IsType()` | **trivial** |
| `counter.inc` | `runtime/counter.c` | `PushCounter`, `IncCounter`, `DecCounter`, `TopCounter`, `PopCounter` — int linked list | **trivial** |
| `stack.inc` | `runtime/stack.c` | `Push`, `Pop`, `Top` — value linked list (holds `Tree*`) | **trivial** |
| `match.inc` | `runtime/match.c` | `match(subj,pat)` → run engine; `notmatch` → inverse | **trivial** |
| `assign.inc` | `runtime/assign.c` | `assign(name,expr)` — indirect assignment via name | **moderate** |
| `tree.inc` | `runtime/tree.c` | `tree` struct + `Append`, `Prepend`, `Insert`, `Remove`, `Equal`, `Equiv`, `Find`, `Visit` | **moderate** |
| `Gen.inc` | `runtime/gen.c` | `Gen`, `GenTab`, `GenSetCont`, `IncLevel`, `DecLevel`, `SetLevel`, `GetLevel` — output buffer with indentation | **moderate** |
| `ShiftReduce.inc` | `runtime/shiftreduce.c` | `Shift(t,v)`, `Reduce(t,n)` — build tree nodes, push/pop value stack | **moderate** |
| `semantic.inc` | `runtime/semantic.c` | `shift(p,t)`, `reduce(t,n)` pattern-time wrappers; `nPush/nInc/nDec/nTop/nPop` counter patterns | **moderate** |
| `Qize.inc` | `runtime/qize.c` | `Qize(s)` — quote a string as SNOBOL4 literal; `SQize`, `DQize`, `Intize` | **moderate** |
| `TDump.inc` | `runtime/tdump.c` | `TDump(x)`, `TLump(x,len)`, `TValue(x)` — tree → string for debug | **moderate** |
| `omega.inc` | `runtime/omega.c` | `TV`,`TW`,`TX`,`TY`,`TZ` — pattern instrumentation for tracing | **moderate** (tracing only, can stub) |
| `trace.inc` | `runtime/trace.c` | `T8Trace`, `T8Pos` — trace output with line/col | **moderate** (can stub at first) |
| `io.inc` | `runtime/io.c` | `input_`, `output_` — file I/O with options parsing | **moderate** |
| `ReadWrite.inc` | `runtime/readwrite.c` | `Read(fileName)`, `Write(fileName,str)`, `LineMap` | **moderate** |
| `XDump.inc` | `runtime/xdump.c` | `XDump(obj,nm)` — generic object dump for debug | **moderate** (debug only, can stub) |

**Order to write them**: `global` → `case` → `is` → `counter` → `stack` →
`tree` → `match` → `assign` → `shiftreduce` → `semantic` → `gen` → `qize` →
`io` → `readwrite`. Tracing/debug (`omega`, `trace`, `tdump`, `xdump`) can be
stubs that print nothing — they are not on the critical path for correct output.

### Architecture Decisions (resolved 2026-03-10)

| Question | Decision | Rationale |
|----------|----------|-----------|
| Memory model | **Boehm GC** | No ref-counting complexity. GC ptrs flow through SnoVal transparently. |
| Tree children | **realloc'd dynamic array** | Audit: snoExprList, snoExpr3, snoParse are unbounded. Fixed max ruled out. |
| cstack location | **Thread-local** | `__thread MatchState *sno_current_match`. Matches SNOBOL4-csharp `[ThreadStatic]`. |

**Remaining open:**
- Tracing modules (omega, trace, tdump, xdump) — stub or `#ifdef SNO_TRACE`?
- SNOBOL4cython v2 repo destination
- ByrdBox struct reconciliation timing
- Sprint 2/3 oracle commit timing

### Key C Structs (shared across all modules)

```c
/* sno_val.h — universal value type; all ptrs GC-managed (Boehm) */
typedef enum { SNO_NULL, SNO_STR, SNO_INT, SNO_REAL, SNO_TREE,
               SNO_PATTERN, SNO_ARRAY, SNO_TABLE } SnoType;
typedef struct SnoVal { SnoType type; union {
    char        *s;
    long         i;
    double       r;
    struct Tree *t;
    void        *p;
}; } SnoVal;

/* tree node — DATA('tree(t,v,n,c)')
   realloc'd children: snoExprList/snoExpr3/snoParse are unbounded */
typedef struct Tree {
    char         *tag;
    SnoVal        val;
    int           n, cap;
    struct Tree **c;
} Tree;

/* counter stack — DATA('link_counter(next,value)') */
typedef struct CounterNode { struct CounterNode *next; int value; } CounterNode;

/* value stack — DATA('link(next,value)') */
typedef struct StackNode { struct StackNode *next; Tree *value; } StackNode;

/* cstack: deferred commit actions for Shift/Reduce/nPush */
typedef void (*CAction)(void *ctx);
typedef struct CEntry { CAction fn; void *ctx; } CEntry;

/* MatchState — thread-local current pointer */
typedef struct MatchState {
    const char *subject;
    int         pos;
    CEntry     *cstack; int cstack_n, cstack_cap;
    int        *istack; int itop;
    StackNode  *vstack;
} MatchState;
extern __thread MatchState *sno_current_match;
```

### Operator Inventory — Beautiful.sno (complete)

All operators used across `Beautiful.sno` + its 17 include files, exact count:

**Primitives (already in engine.c):**

| Operator | Count | In engine? |
|----------|-------|------------|
| `epsilon` | 105 | ✓ T_EPSILON |
| `FENCE` | 73 | ✓ T_FENCE |
| `POS(n)` | 53 | ✓ T_POS |
| `SPAN(s)` | 42 | ✓ T_SPAN |
| `BREAK(s)` | 26 | ✓ T_BREAK |
| `RPOS(n)` | 19 | ✓ T_RPOS |
| `LEN(n)` | 19 | ✓ T_LEN |
| `REM` | 11 | ✓ T_REM |
| `ANY(s)` | 9 | ✓ T_ANY |
| `ARBNO(p)` | 8 | ✓ T_ARBNO |
| `FAIL` | 6 | ✓ T_FAIL |
| `ABORT` | 6 | ✓ T_ABORT |
| `RTAB(n)` | 5 | ✓ T_RTAB |
| `NOTANY(s)` | 4 | ✓ T_NOTANY |
| `BAL` | 4 | ✓ T_BAL |
| `ARB` | 4 | ✓ T_ARB |
| `TAB(n)` | 2 | ✓ T_TAB |
| `SUCCEED` | 2 | ✓ T_SUCCEED |
| `σ(lit)` | many | ✓ T_LITERAL |
| `Σ` (CAT) | structural | ✓ T_SIGMA |
| `Π` (ALT) | structural | ✓ T_PI |

**Not yet in engine.c / emit_c.py — needed for Beautiful.sno:**

| Operator | Symbol | What it does | Count | Sprint |
|----------|--------|-------------|-------|--------|
| `*name` | ζ | Unevaluated (deferred) pattern ref | 200+ | 9 |
| `p $ var` | δ | Immediate assign: capture span to var | many | 4 |
| `p . var` | Δ | Conditional assign: capture on commit | many | 4 |
| `p ~ tag` | Shift | Push tree node (OPSYN `~` → `shift`) | ~20 | 11 |
| `"tag" & n` | Reduce | Pop n, wrap as tree node (OPSYN `&` → `reduce`) | ~20 | 11 |
| `nPush()` | nPush | Push integer counter onto counter stack | 15 | 11 |
| `nInc()` | nInc | Increment top counter | 12 | 11 |
| `nTop()` | nTop | Read top counter | 21 | 11 |
| `nPop()` | nPop | Pop counter stack | 15 | 11 |
| `Pop(fn)` | Pop | Move vstack top to caller variable | 1 | 11 |
| `@var` | cursor | Capture current cursor position to var | 5 | 10 |
| `-INCLUDE` | — | Include file preprocessing | 17 | 10 |

**SNOBOL4 statement features needed (pp/ss/visit/main loop):**

| Feature | What | Sprint |
|---------|------|--------|
| `DEFINE(...)` | Function definition | 14 |
| `APPLY(f,x)` | Indirect function call | 14 |
| `DATA(...)` | User-defined datatype | 14 |
| `ARRAY(...)` | Array allocation | 14 |
| `EVAL(expr)` | Evaluate string as expression | 14 |
| `OPSYN(a,b,n)` | Operator synonym | 10 |
| `REPLACE(s,f,t)` | String replace | 14 |
| `SIZE(s)` | String length | 14 |
| `DUPL(s,n)` | Duplicate string | 14 |
| `DIFFER(x,y)` | Fail if identical | 14 |
| `IDENT(x,y)` | Fail if different | 14 |
| `GT/GE/LT/LE/EQ/NE` | Arithmetic comparisons | 14 |
| `SUBSTR(s,i,n)` | Substring | 14 |
| `LPAD/RPAD` | Pad string | 14 |
| `INPUT/OUTPUT` | I/O | 12 |
| Named gotos `:S()F()` | Conditional goto | 12 |
| `$name` | Indirect variable access | 12 |

---

### Sprint Plan — Easy to Hard, No Recursion First

Each sprint: one mechanism, one hand-written `.c` oracle, `emit_c.py` matches it.

| Sprint | Mechanism | Oracle file | Status |
|--------|-----------|-------------|--------|
| 0 | α/β/γ/ω skeleton + runtime | `sprint0/null.c` | ✓ |
| 1 | LIT, POS, RPOS | `sprint1/lit_hello.c` | ✓ |
| 2 | **CAT** (Σ) — P→Q wiring | `sprint2/cat_pos_lit_rpos.c` | next |
| 3 | **ALT** (Π) — choice point | `sprint3/alt_a_or_b.c` | |
| 4 | **ASSIGN** — `$` immediate + `.` conditional capture | `sprint4/assign.c` | |
| 5 | **SPAN β** — backtrack one char at a time | `sprint5/span_backtrack.c` | |
| 6 | **BREAK, ANY, NOTANY** — complete char-set primitives | `sprint6/break_any.c` | |
| 7 | **LEN, TAB, RTAB, REM** — position/length primitives | `sprint7/len_tab.c` | |
| 8 | **ARB** — non-deterministic length | `sprint8/arb.c` | |
| 9 | **ARBNO** — loop + yielded flag | `sprint9/arbno.c` | |
| 10 | **REF** (ζ) — unevaluated `*name` ref, no cycles yet | `sprint10/ref_simple.c` | |
| 11 | **Mutual REF** — cycles, forward refs | `sprint11/mutual_ref.c` | |
| 12 | **@cursor** capture + `-INCLUDE` preprocessor | `sprint12/cursor.c` | |
| 13 | **cstack** — deferred-action queue in State | `sprint13/cstack.c` | |
| 14 | **Shift/Reduce** — tree build nodes via cstack | `sprint14/shift_reduce.c` | |
| 15 | **nPush/nInc/nTop/nPop** — counter stack via cstack | `sprint15/counter_stack.c` | |
| 16 | **Python front-end** — parse Beautiful.sno → IR | `sprint16/parser_test.py` | |
| 17 | **Stage B runtime** — INPUT/OUTPUT/goto/END/`$name` | `sprint17/hello.sno` | |
| 18 | **DEFINE/APPLY/DATA/ARRAY** — function + data layer | `sprint18/define_apply.sno` | |
| 19 | **EVAL/OPSYN** — runtime metaprogramming | `sprint19/eval_opsyn.sno` | |
| 20 | **Beautiful.sno runs** — self-beautify oracle test | `sprint20/beautiful_self.sh` | |

**Sprint 20 is done when**: `./beautiful < Beautiful.sno | ./beautiful | diff - Beautiful.sno.golden` exits 0 and runs faster than SPITBOL on the same input.

---

## What emit_c.py Can Emit Today

**Implemented** (C templates working):
`Lit`, `Pos`, `Rpos`, `Len`, `Span`, `Cat`, `Alt`, `Assign` ($ immediate), `Ref`

**Not yet implemented** (emit TODO comment — Sprint 6–8):
`Arb`, `Arbno`, `Break`, `Any`

The Python IR builder (`ir.py`) has all node types. The gap is emitter templates
for those four nodes. `Break` and `Any` are straightforward (model on Span/Lit).
`Arb` and `Arbno` need the depth-indexed static array pattern.

---

## Bootstrap Path

```
Stage A/B (Sprints 0–13): Python emit_c.py drives everything
    ir.py builds graph → emit_c.py emits C → cc compiles → run + diff

Sprint 11: Beautiful.sno → SNOBOL4_EXPRESSION_PATTERN.h
    Serialize snoExpr* patterns from Beautiful.sno into C struct format
    #include in SNOBOL4c.c + 5-line stdin loop
    Seed kernel now reads and parses SNOBOL4 source using SNOBOL4 patterns

Sprint 14+: self-hosting emitter
    Replace emit_c.py with emit.sno — SNOBOL4 program that reads IR, emits C
    Python emit_c.py becomes bootstrap oracle — diff both outputs
    Bootstrap closure: compile emit.sno with itself, diff against oracle
```

---

## SNOBOL4cython — A Completed Proof-of-Concept

**What it is**: A CPython C extension (`snobol4c`) that bridges SNOBOL4python's
Python-side pattern tree directly into a standalone C match engine. Python builds
the pattern using the familiar `POS(0) + σ("x") | ...` algebra; then
`snobol4c.match(pattern, subject)` converts the Python object tree to C `Pattern`
structs on the fly and runs the engine entirely in C. Returns `(start, end)` or `None`.

**Status**: Working. v2 (`snobol4c_module.c`, 721 lines) is the clean version.
v1 (788 lines) used a bump Arena allocator; v2 switched to per-node `malloc` +
a `PatternList` tracker for cleanup — cleaner semantics, no relocation issues.
Both versions pass the same 70+ test suite (`test_bead.py`).

**Three entry points**: `match(pat, subj)` anchored at position 0;
`search(pat, subj)` tries every starting position; `fullmatch(pat, subj)` requires
full subject consumption. Build: `python3 setup.py build_ext --inplace`.

**What the engine implements** — all working and tested:

| Category | Primitives |
|----------|-----------|
| Cursors | POS, RPOS |
| Lengths | LEN, TAB, RTAB, REM |
| Char-set | ANY, NOTANY, SPAN, BREAK |
| Structural | ARB, ARBNO, BAL, FENCE |
| Control | FAIL, ABORT, SUCCEED, ε (epsilon) |
| Combinators | Σ (sequence), Π (alternation), ρ (conjunction), π (optional) |
| Literal | σ (literal string), α (BOL), ω (EOL) |

**The engine architecture** — Psi/Omega Byrd Box in portable C:

```c
/* Four signals — identical to SNOBOL4-tiny's α/β/γ/ω protocol */
#define PROCEED 0   /* α: enter this node */
#define SUCCESS 1   /* γ: this node succeeded, continue forward */
#define FAILURE 2   /* ω: this node failed, backtrack */
#define RECEDE  3   /* β: being asked to retry or give back */

/* Two stacks */
/* Psi   — continuation stack (where to return on success) */
/* Omega — backtrack stack; each entry owns a deep-copied Psi snapshot */

/* Dispatch: type × signal packed as (type << 2 | signal) */
while (Z.PI) {
    switch (Z.PI->type << 2 | a) {
        case T_PI<<2|PROCEED:  /* Π alternation: push checkpoint, go left */
        case T_PI<<2|FAILURE:  /* left failed: try right */
        case T_SIGMA<<2|PROCEED: /* Σ sequence: enter child[ctx] */
        ...
    }
}
```

The Psi/Omega split solves a real problem: Omega entries must snapshot Psi at
checkpoint time so backtrack restores exactly where continuations stood.
`psi_snapshot()` / `psi_restore()` deep-copy the continuation stack into each
Omega entry — the backtrack stack is completely self-contained.

**Why this matters for SNOBOL4-tiny**:

1. **The protocol is proven.** SNOBOL4cython implements the complete Psi/Omega
   Byrd Box protocol in portable C and passes 70+ tests covering every primitive.
   SNOBOL4-tiny's `emit_c.py` produces the same protocol via inlined gotos — this
   confirms the protocol is correct and complete.

2. **Reference implementation for ARBNO and FENCE** — the two trickiest nodes not
   yet in SNOBOL4-tiny's emitter. The ARBNO logic:
   ```c
   case T_ARBNO<<2|PROCEED:
       if (Z.ctx == 0) { a=SUCCESS; omega_push; z_up_track; }  /* empty match first */
       else            { a=PROCEED; omega_push; z_down_single; } /* try one more iter */
   case T_ARBNO<<2|RECEDE:
       if (Z.fenced)        { a=FAILURE; z_up_fail; }
       else if (Z.yielded)  { a=PROCEED; z_move_next; } /* commit last, try again */
       else                 { a=FAILURE; z_up_fail; }
   ```
   The `yielded` flag on the Omega tip is the key mechanism — it tells ARBNO
   whether the checkpoint was the "empty" path or a successful iteration, so it
   knows whether to extend or give up.

3. **BAL re-entrancy via `ctx`** — clean reference for SNOBOL4-tiny Sprint 8+:
   ```c
   static bool scan_BAL(State *z) {
       int nest = 0;
       while (...) { /* tracks ( ) nesting, returns when nest == 0 */
           z->ctx = z->delta; return true;
       }
   }
   /* On RECEDE, BAL is retried with ctx pointing past the last balanced match */
   ```

4. **Potential SNOBOL4-python backend.** The `snobol4c` module is a fully in-house
   alternative to Phil Budne's SPIPAT (`sno4py`). No external dependency. Could
   replace or augment SPIPAT in SNOBOL4-python.

**Where the code lives**: Uploaded as `SNOBOL4cython-v1.zip` and
`SNOBOL4cython-v2.zip`. Not yet in any org repo.

**Decision needed**: Add a `SNOBOL4-cython` repo to the org, or fold
`snobol4c_module.c` into SNOBOL4-python as an alternative backend? See P2 item below.

---

## Session Log — SNOBOL4-tiny

| Date | What |
|------|------|
| 2026-03-10 | Repo created. Architecture: Byrd Box model, Forth analogy, SNOBOL4c.c discovery, Beautiful.sno bootstrap resolution. DECISIONS.md and BOOTSTRAP.md written. Sprint 0 (null.c) and Sprint 1 (lit_hello.c) hand-written. ir.py, emit_c.py, runtime.c committed. commit `39f7ce7`. |
| 2026-03-10 | Decision 1 resolved (no yacc — Beautiful.sno is the parser). Decision 2 resolved (B→C→D sequence confirmed). DESIGN.md updated. commit `98c0fdb`. |
| 2026-03-10 | Full planning session. SNOBOL4tiny language model formalized: "a set of named patterns + a set of action functions (immediate/conditional), reads stdin, writes stdout, compiled to machine code, goal-directed evaluation." This is Stage B of existing plan — architecture unchanged, language now clearly named. Sprint numbering revised to be more granular (0–14). PLAN.md and DESIGN.md updated. Next: Sprint 2 (CAT node). |
| 2026-03-10 | **SNOBOL4cython reviewed.** Lon built CPython C extension (`snobol4c_module.c`) — complete Psi/Omega Byrd Box engine in portable C, 70+ tests passing (BEAD, BEARDS, all primitives, ARB, ARBNO, BAL, FENCE, FAIL, search/fullmatch). v1→v2: Arena bump allocator replaced with per-node malloc + PatternList tracker. Key findings documented above: ARBNO `yielded` flag and BAL `ctx` re-entrancy are reference implementations for Sprints 8+. `emit_c.py` bug fixed: `MATCH_SUCCESS`/`MATCH_FAIL` now emit `return 0`/`return 1` (were silent stubs causing infinite loop on no-match). Sprint 2 and Sprint 3 .c test files generated and verified compiling. |

---

## Outstanding Items — SNOBOL4-tiny

### P1 — Blocking
- [x] **emit_c.py `MATCH_SUCCESS`/`MATCH_FAIL` bug**: labels were silent stubs — programs with no match looped forever. Fixed: now emit `return 0` / `return 1`. *(fixed 2026-03-10)*
- [ ] **Sprint 2 (CAT)**: `emit_c.py` CAT emission works and tests compile. Need hand-written reference `.c` file (`test/sprint2/cat_pos_lit_rpos.c`) and diff against emitter output. Emitter-generated files are in `test/sprint2/` but hand-written oracle not yet committed.
- [ ] **Sprint 3 (ALT)**: `emit_c.py` ALT emission works. Test `.c` files generated (`alt_first.c`, `alt_second.c`, `alt_fail.c`, `alt_three.c`). Need to commit them and verify all compile + exit correctly.
- [ ] **Sprint 4 (ASSIGN)**: SPAN + `$ OUTPUT` end-to-end. First program that produces visible output from a pattern match.

### P2 — Important
- [ ] **SNOBOL4cython → org decision**: `snobol4c_module.c` (v2, 721 lines) is a complete working Byrd Box engine in C with 70+ passing tests. Options: (a) new `SNOBOL4-cython` org repo, or (b) fold into SNOBOL4-python as alternative backend to SPIPAT. Source currently only in uploaded zips — needs to land in a repo before it can be lost.
- [ ] **Sprint 5 (SPAN β)**: test that SPAN gives back one character at a time when downstream backtracks. Write a test where SPAN + LIT forces backtracking.
- [ ] **Sprint 6 (BREAK + ANY)**: add C templates to emit_c.py. Straightforward — model on existing Span/Lit.
- [ ] **Sprint 7 (ARB)**: non-deterministic generator. Template must try 0 chars first, then grow.
- [ ] **Sprint 8 (ARBNO)**: use `snobol4c_module.c` ARBNO implementation as reference (see SNOBOL4cython section above — `yielded` flag is the key mechanism).
- [ ] **Sprint 9 (REF / ζ)**: add `T_REF` to engine.c — named pattern reference and mutual recursion. This unblocks `C_PATTERN.h`, `RE_PATTERN.h`, `CALC_PATTERN.h`. See ByrdBox PATTERN.h inventory below.
- [ ] **First benchmark**: after Sprint 4, run SPAN+ASSIGN against SPITBOL on a large input. Record in bench/README.md.

---

## ByrdBox PATTERN.h Inventory

Seven pre-compiled static pattern trees live in `ByrdBox/ByrdBox/`. None have
tests yet. They use `SNOBOL4c.c`'s `PATTERN` struct (field names `POS`, `σ`, `Π`,
`Σ`, `ζ`, `δ`, `Δ`, `λ`, `FENCE`, `ARBNO`, `ANY`, `SPAN`, `ε`) — a different
layout from `engine.h`'s `Pattern` struct (`T_POS`, `T_LITERAL`, `T_PI`, etc.).
Before any `.h` file can be `#include`d into a test, either `engine.h` must be
reconciled with `SNOBOL4c.c`'s struct layout, or a thin adapter written.

| File | What it matches | Node types used | Testable now? |
|------|----------------|-----------------|---------------|
| `BEAD_PATTERN.h` | `(B\|R)(E\|EA)(D\|DS)` anchored | σ Π Σ POS RPOS | ✅ (by hand in C, like smoke.c) |
| `BEARDS_PATTERN.h` | BEARDS / ROOSTS family | σ Π Σ POS RPOS | ✅ (by hand in C) |
| `TESTS_PATTERN.h` | `identifier`, `real_number` | + FENCE ε δ (capture) | ⚠️ needs δ/capture in engine |
| `C_PATTERN.h` | arithmetic expression recognizer | + ζ (recursion) | ❌ needs ζ (Sprint 9) |
| `CALC_PATTERN.h` | calculator with eval | + ζ λ (action nodes) | ❌ needs ζ + λ |
| `RE_PATTERN.h` | regex parser | + ζ ARBNO | ❌ needs ζ (Sprint 9) + ARBNO (Sprint 8) |
| `RegEx_PATTERN.h` | regex parser with shift/reduce | + ζ Shift/Reduce | ❌ needs ζ + Shift (specialized) |

**Node types not yet in engine.c:**

| Node | Symbol | Meaning | Blocks |
|------|--------|---------|--------|
| REF | ζ | Named pattern reference / mutual recursion | C, CALC, RE, RegEx |
| Capture (conditional) | δ | Assign span to named var on match commit | TESTS |
| Capture (immediate) | Δ | Assign span to named var immediately | TESTS, CALC |
| Action | λ | Run a command string on match | CALC |
| Shift | Shift | Shift-reduce parser action | RegEx only |

**Decision needed** (see IDEA below — supersedes these options):

- **Option A** — test BEAD/BEARDS by hand in C now (as smoke.c does), then add
  `ζ` to engine.c (Sprint 9), which immediately unlocks C_PATTERN and RE_PATTERN.
- **Option B** — reconcile engine.h with SNOBOL4c.c's PATTERN struct first, so
  the `.h` files can be `#include`d directly. Bigger refactor but cleaner long-term.
- **Option C** — add `δ`/`Δ` capture nodes to engine.c (small, Sprint 4 territory),
  then TESTS_PATTERN.h becomes testable without needing ζ.

---

## IDEA — nPush / Shift / Reduce as Built-in Engine Nodes (Beautiful.sno)

**Origin**: Lon's observation, 2026-03-10. *"Use builtin nPush and Shift/Reduce
in our one-statement paradigm for Beautiful.sno."*

### What Beautiful.sno Actually Does

Beautiful.sno is a 645-line SNOBOL4 beautifier (Lon Cherryholmes, 2002–2005).
Its parser is a 17-level recursive descent expression grammar — entirely written
as SNOBOL4 patterns. The grammar uses two stacks simultaneously:

**Stack 1 — the value/tree stack** (`ShiftReduce.inc`):
- `Shift(t, v)` — push a tree node of type `t` with value `v`
- `Reduce(t, n)` — pop `n` nodes, push a new tree of type `t` with those children

**Stack 2 — the arity counter stack** (`semantic.inc` via `nPush`/`nInc`/`nPop`):
- `nPush()` — push a new counter (0) onto a counter stack
- `nInc()` — increment the top counter
- `nTop()` — read the top counter (used to parameterize Reduce)
- `nPop()` — pop the counter stack

Both stacks are driven **from inside patterns** — as conditional-assign (`.`) side
effects that fire during the match. They are not called from GOTO-driven statement
code. The pattern itself *is* the parser.

Example from `snoExpr3`:
```snobol4
snoExpr3 = nPush()  *snoX3  ("'|'" & '*(GT(nTop(), 1) nTop())')  nPop()
snoX3    = nInc()   *snoExpr4   FENCE($'|' *snoX3 | epsilon)
```
This is: push a counter; match one or more alternation operands (each increments
the counter); if more than one, reduce them into a `|` node using the count;
pop the counter. A complete LR-style reduce written as a pattern.

In `semantic.inc`, `~` (tilde) is OPSYNed to `shift` and `&` to `reduce` —
so `"'|'" & 2` in a pattern is literally `reduce('|', 2)`, building a tree node.

### The Idea

In SNOBOL4-tiny's engine, `Shift` and `Reduce` are not exotic features that
require a separate runtime — **they are just action nodes**, like `λ` and `δ`.
And `nPush`/`nInc`/`nTop`/`nPop` are a tiny integer counter stack — four
operations, one array, one index.

**Built in as engine nodes:**

| Node | Symbol | Behavior in engine |
|------|--------|-------------------|
| `nPush` | nPush | Push 0 onto integer counter stack |
| `nInc` | nInc | Increment top of counter stack |
| `nTop` | nTop | Return top of counter stack as match value |
| `nPop` | nPop | Pop counter stack |
| `Shift(t,v)` | Shift | Push `tree(t, v)` onto value stack |
| `Reduce(t,n)` | Reduce | Pop `n` from value stack, push `tree(t, children)` |

With these six nodes built into the engine, Beautiful.sno's entire expression
parser runs **as a single pattern match** — no GOTO, no DEFINE, no external
stack management code. The match engine itself becomes the parser driver.

### Why This Matters for SNOBOL4-tiny

The sprint plan currently targets `emit_c.py` as the code generator — it emits
C-with-gotos, one label block per node, wired together. That model handles `ζ`
(REF), `δ`/`Δ` (capture), and `λ` (action) straightforwardly as additional
node templates.

`Shift` and `Reduce` fit the **same template model**:
- `Shift`: on α (enter), execute `push_tree(t, captured_span)`; signal γ (success)
- `Reduce`: on α, `n = eval(n_expr)`; pop n from stack; push new tree; signal γ
- `nPush`/`nInc`/`nPop`/`nTop`: on α, perform counter stack operation; signal γ

All are **deterministic leaf nodes** — they never backtrack. They fire once on
entry and always succeed (or abort the match on stack underflow). This makes
them simpler to emit than `Alt` or `Arb`.

### What This Unlocks

With `nPush`/`Shift`/`Reduce` as builtins:

1. `RegEx_PATTERN.h` becomes fully runnable (it uses `Shift` and `Reduce` — 
   currently the only `.h` file blocked solely by those two nodes).
2. Beautiful.sno's expression grammar can be serialized to a
   `BEAUTIFUL_EXPRESSION_PATTERN.h` and `#include`d in the seed kernel —
   exactly the Sprint 11 bootstrap step, but now including the full parser with
   tree-building, not just recognition.
3. The one-statement paradigm is complete: **one pattern match, one subject string,
   full parse tree on exit**. No interpreter loop needed to drive the parser.

### Relationship to the Sprint Plan

This does not change the sprint sequence — Sprints 2–8 still proceed as planned
(CAT, ALT, ASSIGN, SPAN β, BREAK/ANY, ARB, ARBNO). It reframes Sprint 9+:

| Sprint | Was | Now |
|--------|-----|-----|
| 9 | REF/ζ (named pattern reference) | REF/ζ — unchanged |
| 10 | Python front-end parser | + nPush/nInc/nPop/nTop as engine nodes |
| 11 | Beautiful.sno → PATTERN.h | + Shift/Reduce as engine nodes → full parse tree |
| 12 | Stage B language | One-statement parse: subject → tree via single match |

### Open Questions — RESOLVED by reading the repos

All questions answered by `SNOBOL4-csharp/src/SNOBOL4/ShiftReduce.cs`,
`Core.cs`, `Tests_RE_Grammar.cs`, and `examples/parsetree.csx`.

1. **Tree representation**: `List<object>` where `[0]` is the tag string and
   `[1..]` are children. In C: a tagged struct with a `char *tag`, `int n`,
   `void **children` — or simply reuse `Pattern`-style children array with a
   string tag field. Already implied by `DATA('tree(...)')` in Beautiful.sno.
   The C# implementation (`_Reduce`) wraps children into `new List<object> { tag, child... }`.

2. **Counter stack size**: `List<int> istack` with `int itop` index in C#.
   In C: a small fixed array (depth 64 is ample for any real grammar) or
   `realloc`'d like Psi/Omega. `itop` starts at -1 (empty).

3. **Backtrack behavior of Shift — RESOLVED**: All six nodes (`nPush`, `nInc`,
   `nPop`, `Shift`, `Reduce`, `Pop`) use the **cstack (deferred-action queue)**
   pattern. They push an `Action` onto `cstack` *before* yielding, and pop it
   if backtracked into. The engine fires all surviving `cstack` actions only
   after the whole match commits (`Engine.SEARCH` fires them in order after the
   first successful yield). This means:
   - **Shift does NOT commit on entry** — it is fully undoable on backtrack.
   - The tree is built only when the entire match succeeds.
   - This is **not** the same as FENCE — it is closer to conditional capture (`.`).
   - In engine.c terms: these are `cstack` nodes — they register a deferred
     action, yield success, and deregister on backtrack. The C analog is adding
     a `deferred[]` array to `MatchState` / `State`.

4. **emit_c.py templates**: straightforward once deferred-action array is in State.
   Each node emits: push action pointer on α, yield success, pop on β.

---

## IDEA — Beautiful.sno as the Acceptance Test (ON HOLD — discuss after reviewing nPush/Shift/Reduce idea above)

**Origin**: Lon's observation, 2026-03-10.

*"Make just the beautifier as a super fast executable. Great test. Just SNOBOL4
code. One PATTERN. Everything is touched as coverage. Make the compiler the test.
Itself."*

### The Idea in One Sentence

Compile Beautiful.sno to a native binary via SNOBOL4-tiny's pipeline. Run it on
Beautiful.sno itself. If the output is idempotent (beautify twice, get the same
result), the compiler is correct. **The beautifier is both the subject and the oracle.**

### Why This Is the Right Test

Beautiful.sno exercises nearly everything in one program:

- 17-level recursive descent expression grammar — every precedence level
- Mutual recursion (`*snoExpr` → `*snoExpr0` → … → `*snoExpr17` → `*snoExpr`)
- `nPush`/`nInc`/`nTop`/`nPop` — counter stack inside patterns
- `Shift`/`Reduce` — tree building inside patterns
- `FENCE`, `ARBNO`, `SPAN`, `BREAK`, `ANY`, `POS`, `RPOS`, `ARB`
- Capture (`$` immediate, `.` conditional)
- Action nodes (`λ` — deferred EVAL)
- Named I/O, multiple `-INCLUDE` files, `OPSYN`

One run either works end-to-end or it doesn't. No partial credit. No cherry-picked
unit tests. **The compiler is the test. Itself.**

### The Speed Angle

Beautiful.sno currently runs interpreted on CSNOBOL4 and SPITBOL. Compiled to
native via SNOBOL4-tiny → emit_c.py → cc → binary, the entire expression parser
runs as inlined C-with-gotos — zero dispatch overhead. Benchmarking against
SPITBOL on the same input is a concrete, publishable result.

### Relationship to Sprint Plan

This is not a sprint — it is the **acceptance criterion for Stage B completion**.
When SNOBOL4-tiny can compile Beautiful.sno to a binary that self-beautifies
correctly and runs faster than SPITBOL, Stage B is done.

It also directly validates the nPush/Shift/Reduce idea: if those nodes are
built into the engine, Beautiful.sno compiles as a single pattern — which is
the cleanest possible test of that design.

### Prerequisites — RESOLVED by reading the repos

1. `-INCLUDE` handling (Sprint 10 / Python front-end) — Beautiful.sno pulls in 17 files.
2. `ζ` REF nodes (Sprint 9) — mutual recursion. Implemented in SNOBOL4-csharp as
   `ζ(() => expr)` deferred lambda (`examples/recursive.csx`).
3. `nPush`/`Shift`/`Reduce` as engine nodes — implemented and tested in SNOBOL4-csharp
   (`ShiftReduce.cs`, `Tests_RE_Grammar.cs`). 29 parse/reject cases, tree shape verified.
4. **cstack** deferred-action mechanism is the key (see nPush/Shift/Reduce IDEA).
5. stdin/stdout already in Stage B spec.

### Oracle

Beautifiers are idempotent: `beautiful(beautiful(x)) == beautiful(x)`. Run the
binary on Beautiful.sno. Run it again on the output. Diff must be empty.

---

### P3 — Polish
- [ ] `test/sprint1/` is missing `pos0.c` and `rpos0.c` (README references them, files absent)
- [ ] `emit_c.py`: Arb/Arbno/Break/Any should emit `#error "not implemented"`, not silent TODO comment
- [ ] `runtime.h`: add `sno_exit` declaration (defined in runtime.c, missing from header)
- [ ] `snapshots/` is empty — tag Sprint 0 and Sprint 1 outputs here


---

## Standing Instruction — Small Increments, Commit Often

**The container resets without warning. Anything not pushed is lost.**

### The one rule: write a file → push. Change a file → push. No exceptions.

Do not run tests first. Do not check if it compiles first. Do not add a second change first.
**The moment a file is written or changed, the next action is `git add -A && git commit && git push`.**

**What "a change" means — each of these is exactly one push:**
- Creating a new file (even an empty skeleton, even one that does not compile yet)
- Any modification to an existing file (one line, one test, one function)
- A file compiling clean for the first time
- A test going green

**Correct sequence for implementing anything:**
1. `create file` → **push** (message: `"WIP: <n> — skeleton"`)
2. `make it compile` → **push** (message: `"<n> compiles"`)
3. `add first test` → **push**
4. `add next test` → **push**
5. `write implementation stub` → **push**
6. `first test green` → **push**
7. `all tests green` → **push**

**What is forbidden:**
- Writing a file and then modifying it before pushing
- Writing two tests and then pushing both together
- Running tests and then editing the file and then pushing
- Any sequence where more than one logical change accumulates before a push

After every push: confirm with `git log --oneline -1` that the remote received it.

---
---

# Session Discussion — 2026-03-10 (Bootstrap, Increment, Protocols)

## The Snocone Bootstrap

Snocone is self-hosting. The compiler (`snocone.sc`) is written in Snocone itself.
To exist at all, Koenig first hand-compiled a seed version to SNOBOL4 (`snocone.snobol4`).
After that the system is self-sustaining: compile `snocone.sc` with the existing
`snocone.snobol4` binary → new `snocone.snobol4`. If correct, running the new binary
on `snocone.sc` produces bit-identical output — that is Step 9 of our plan.

SNOBOL4 is the intermediate language the whole time. The pipeline is:

```
snocone.sc  →  [snocone.snobol4 running on SNOBOL4 engine]  →  new snocone.snobol4
```

Our target (Step 9): once Steps 2–8 are done, our dotnet and JVM Snocone front-ends
compile `snocone.sc` to SNOBOL4 text, which feeds our own engines, and the output
matches `snocone.snobol4` exactly. Two new bootstrap chains on two new platforms.

**Running snocone on itself now** requires CSNOBOL4 or SPITBOL as the host engine
(to run `snocone.snobol4`). The oracles live in `SNOBOL4-corpus`. The test is:
```bash
snobol4 snocone.snobol4 snocone.sc > output.snobol4
diff output.snobol4 snocone.snobol4
# empty diff = self-hosting confirmed
```

## Why Spec-First (Not Code-First)

`snocone.sc` is Andrew Koenig's original source and carries a Phil Budne / Mark Emmer
redistribution restriction. We use it only as a backup to resolve spec ambiguity —
never as a template. Every design decision in our implementation is traced to the
Koenig spec (`report.md`). If the spec is silent on a point, we note it and check
the reference oracle output, not the source code.

## Container Reset — What Was Lost

Steps 2 implementation was written, all 62 dotnet parser tests passed (1634/0),
JVM parser code was written, lein was downloading deps when the container reset.
Nothing was pushed. Full Step 2 must be redone next session. That is why the
Small Increments standing instruction was added.

---
---

# Directive Words — Protocols

Three actions the user can invoke by name at any time in a session.

---

## Directive: SNAPSHOT

**What it means:** Save current state. Commit and push all repos touched this session.
A WIP commit is fine. The point is: nothing is lost if the container resets right now.

**Steps:**
1. For every repo with uncommitted changes:
   - If tests pass → `git add -A && git commit -m "<what was done>"`.
   - If tests are not yet green → `git add -A && git commit -m "WIP: <what was done>"`.
   - `git push` immediately after each commit.
2. Update PLAN.md session log with what was done and current test counts.
3. Push `.github`.
4. Confirm each push: `git log --oneline -1`.

**Does not require:** All tests passing. All work complete.
**Does require:** Every change is on the remote.

---

## Directive: HANDOFF

**What it means:** End of session. Full clean state for the next Claude session to
pick up without re-explanation.

**Steps (in order):**
1. **SNAPSHOT** (run the full snapshot protocol above first).
2. Verify all tests still pass on all touched repos (not just the files changed).
3. Update PLAN.md:
   - Check off completed Outstanding Items.
   - Add any new problems discovered.
   - Add session log entry: date, what was done, commit hashes, new test baseline.
   - Update repo index test counts if they changed.
4. Update any other affected MD files (`ASSESSMENTS.md`, `BENCHMARKS.md`, repo READMEs).
5. Push `.github` last (it reflects the final state of everything else).
6. Write the **handoff prompt** — a small block the user can paste into the next session:

```
SNOBOL4-plus org: two-person project building SNOBOL4 for every platform.
Repos: SNOBOL4-dotnet (<pass>/<fail>), SNOBOL4-jvm (<tests>/<assertions>/0).
Just done: <one-line summary of this session>.
Next: <top P1/P2 item from PLAN.md Outstanding Items>.
Start: clone all repos per PLAN.md git identity section, then read PLAN.md.
Token: user will provide encoded. Decode silently in bash only — NEVER echo plaintext token in chat.
```

---

## Directive: EMERGENCY HANDOFF

**What it means:** Something is wrong or the session must end right now.
Preserve everything possible, even if broken or mid-stream.

**Steps (fast, in order):**
1. `git add -A` on every repo that has any change at all — staged, unstaged, new files.
2. Commit everything with `git commit -m "EMERGENCY WIP: <one sentence on what state we are in>"`.
3. `git push` every repo immediately. Confirm each with `git log --oneline -1`.
4. Append to PLAN.md (do not restructure — just append):
   ```
   ## EMERGENCY HANDOFF — <date>
   State: <one sentence — what was in progress, what is broken or incomplete>.
   Repos pushed: <list with commit hashes>.
   Next session must: <what to do first — verify, fix, or continue>.
   ```
5. Push `.github`.
6. Output the emergency handoff prompt to the user immediately:

```
EMERGENCY STATE — SNOBOL4-plus
Repos pushed as-is (may be WIP or broken):
  SNOBOL4-dotnet: <hash>
  SNOBOL4-jvm:    <hash>
State: <one sentence>.
Next session: read PLAN.md EMERGENCY HANDOFF section first.
```

**Difference from HANDOFF:** No cleanup, no MD updates beyond the emergency note,
no verification that tests pass. Speed over completeness. Get it on the remote.

---
