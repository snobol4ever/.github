# SNOBOL4-plus — Master Plan

> **For a new Claude session**: Read this file first. This is the single plan
> for the entire SNOBOL4-plus organization. All repos are developed together.
> Clone all repos immediately (see **Session Start — Clone All Repos** below).
> Then build CSNOBOL4 and SPITBOL (see **Session Start — Build Oracles**) — always.
> Then run the test suites in the repos you are working on to confirm baselines.
> The Tradeoff Prompt for SNOBOL4-jvm is at the bottom of that repo's section.

---

## Session Start — Clone All Repos

**Always clone all five repos at the start of every session.** Work spans multiple
repos simultaneously — corpus changes, cross-platform validation, shared test
programs. Having all repos present avoids mid-session interruptions.

```bash
cd /home/claude
git clone https://github.com/SNOBOL4-plus/SNOBOL4-dotnet.git &
git clone --recurse-submodules https://github.com/SNOBOL4-plus/SNOBOL4-jvm.git &
git clone https://github.com/SNOBOL4-plus/SNOBOL4-python.git &
git clone https://github.com/SNOBOL4-plus/SNOBOL4-csharp.git &
git clone https://github.com/SNOBOL4-plus/SNOBOL4-corpus.git &
wait
echo "All clones done."
```

Verify with:
```bash
for repo in SNOBOL4-dotnet SNOBOL4-jvm SNOBOL4-python SNOBOL4-csharp SNOBOL4-corpus; do
  echo "$repo: $(cd /home/claude/$repo && git log --oneline -1)"
done
```

All five repos live under `/home/claude/`. The `.github` repo (this plan) clones to
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

**Jeffrey Cooper, M.D.** (jcooper0) — medical doctor
- SNOBOL4-dotnet: full SNOBOL4/SPITBOL compiler + runtime → .NET/MSIL (C#)

Mission: **SNOBOL4 everywhere. SNOBOL4 now.**

---

## Repository Index

| Repo | Language | Status | Branch | Tests |
|------|----------|--------|--------|-------|
| [SNOBOL4-dotnet](https://github.com/SNOBOL4-plus/SNOBOL4-dotnet) | C# / .NET | Active | `main` | 1,466 passing / 0 failing |
| [SNOBOL4-jvm](https://github.com/SNOBOL4-plus/SNOBOL4-jvm) | Clojure / JVM | Active | `main` | 2,033 / 4,417 assertions / 0 failures |
| [SNOBOL4-python](https://github.com/SNOBOL4-plus/SNOBOL4-python) | Python + C | Active | `main` | — |
| [SNOBOL4-csharp](https://github.com/SNOBOL4-plus/SNOBOL4-csharp) | C# | Active | `main` | 263 passing |
| [SNOBOL4-corpus](https://github.com/SNOBOL4-plus/SNOBOL4-corpus) | SNOBOL4 | Corpus | `main` | — |

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
- [ ] **Snocone Step 2: expression parser** — `&&`, `||`, `~`, all comparison ops, `$`, `.`, precedence table. Steps 0 and 1 complete. See **Snocone Front-End Plan** section below.
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
- [ ] Write individual repo READMEs for all five repos
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
| 2 | Expression parser: `&&`, `\|\|`, `~`, `==`, `<=`, `*deferred`, `$`, `.` | | |
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
**Baseline**: 2033 tests / 4417 assertions / 0 failures — commit `e697056` (2026-03-09)

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
**Baseline**: 1,466 passing / 0 failing (2026-03-10, commit `3bce92c`)

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

## Standing Instruction — Small Increments, Commit Often

**The container resets without warning. Anything not pushed is lost.**

- Work in the smallest meaningful unit: one file, one function, or one test class.
- Commit and push **before** moving on to the next unit.
- For a new feature: write tests → push. Implement → push. Suite green → push.
- Never accumulate more than one logical unit of uncommitted work.
- After every push, confirm with `git log --oneline -1` that the remote received it.
- If a piece is not yet tested, commit it immediately as `WIP: <description>` so it is not lost.

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
