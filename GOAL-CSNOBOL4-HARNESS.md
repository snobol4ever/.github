# GOAL-CSNOBOL4-HARNESS — Wire CSNOBOL4 Tests into Harness Drivers

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ ABSOLUTE RULE — ZERO C BYRD BOX FUNCTIONS — NO EXCEPTIONS — READ THIS BEFORE WRITING CODE  ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                  ║
║  A C Byrd box (C BB) is ANY C function with this signature:                                     ║
║                                                                                                  ║
║      DESCR_t foo(void *zeta, int entry)                                                         ║
║                                                                                                  ║
║  implementing four-port logic (α / β / γ / ω).                                                  ║
║                                                                                                  ║
║  THERE MUST BE ZERO OF THESE IN THE CODEBASE. NOT ONE. NONE. EVER.                              ║
║                                                                                                  ║
║  ALL Byrd boxes are x86 ASSEMBLY emitted at runtime by the emitter.                             ║
║  If you want a BB, you EMIT it. You do not write a C function for it.                           ║
║                                                                                                  ║
║  The only permitted C functions with (void *zeta, int entry) signature are:                     ║
║    • icn_lazy_box  — infrastructure shim, not a generator                                       ║
║    • icn_bb_dcg    — infrastructure DCG driver, not a generator                                 ║
║                                                                                                  ║
║  If you just wrote DESCR_t foo(void *zeta, int entry) { ... } — DELETE IT.                     ║
║  Implement it as an IR_block_t DCG (ir_exec.c + lower_icn.c) driven by icn_bb_dcg.             ║
║  See IR_ICN_UPTO in ir_exec.c and lower_icn_upto() in lower_icn.c as the template.             ║
║                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

**Repo:** harness (`adapters/csnobol4/`, `crosscheck/`), plus test classes in SCRIP, snobol4dotnet, snobol4jvm
**Done when:** all 126 tests (116 Budne + 10 FENCE) are wired into harness and into each runtime's native test suite, with baselines recorded.

---

## What this is

Two sets of programs live in corpus:

| Set | Location | Count | Harness-ready |
|-----|----------|-------|---------------|
| FENCE tests | `crosscheck/patterns/058–067` | 10 | Yes — already in crosscheck dirs |
| Budne suite | `programs/csnobol4-suite/` | 124 | 116 (8 excluded — see below) |

**Excluded (8):** `bench.sno` (no .ref), `breakline.sno` (record-size file I/O hangs SPITBOL), `genc.sno` (file output), `k.sno` (record-size file I/O hangs SPITBOL), `ndbm.sno` (library), `sleep.sno` / `time.sno` (time-dependent, -INCLUDE), `line2.sno` (no .ref).

**Tests that read from INPUT (stdin is embedded in .sno after END):**
`atn.sno`, `crlf.sno`, `longrec.sno`, `rewind1.sno`, `sudoku.sno`, `trim0.sno`, `trim1.sno`, `uneval2.sno` — for these, stdin data lives below the `END` line in the .sno file itself; each runtime's test must feed that data as stdin.

---

## Repos needed

```bash
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/harness      /home/claude/harness
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/corpus       /home/claude/corpus
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/SCRIP      /home/claude/SCRIP
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4dotnet /home/claude/snobol4dotnet
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4jvm   /home/claude/snobol4jvm
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
```

---

## Steps

- [x] **S-1** — Add `adapters/csnobol4/run.sh` to harness.
  5-line wrapper: `snobol4 "$1"` → stdout, no banner noise.
  Model: `adapters/dotnet/run.sh`.
  Gate: `bash adapters/csnobol4/run.sh corpus/crosscheck/patterns/059_pat_fence_fn_basic.sno`
  prints `matched`.

- [x] **S-2** — Verify 10 FENCE tests pass under `crosscheck.sh --engine csnobol4 --filter pat_fence`.
  Gate: `crosscheck.sh --engine csnobol4 --filter pat_fence` → 0 failures (SPITBOL) /
  10 failures expected (CSNOBOL4, since FENCE(P) not yet implemented) — document baseline.

- [x] **S-3** — Add `adapters/csnobol4/run_crosscheck_csnobol4.sh` to harness.
  Walks `corpus/programs/csnobol4-suite/`, runs each `.sno`, diffs stdout vs `.ref`.
  Skips the 8 excluded files.
  Gate: script runs to completion against SPITBOL oracle, reports pass/fail counts.

- [x] **S-4** — Run S-3 script against SPITBOL oracle. Record baseline pass count.

- [x] **S-5** — Run S-3 script against CSNOBOL4. Record baseline pass count.

- [x] **S-6** — Add `csnobol4` to `crosscheck.sh` DIRS scan and engine list documentation.
  Update harness README to mention csnobol4 adapter.

- [x] **S-7** — Add `test/run_csnobol4_suite.sh` to **SCRIP**.
  Shell runner using `scrip`. Runs 116 Budne tests + 10 FENCE tests.
  Model: `test/run_interp_broad.sh`.
  For tests with stdin data embedded below END: extract it and feed as stdin.
  Gate: script runs to completion, reports PASS/FAIL counts.

- [x] **S-8** — Add `CorpusRef_FenceTests.cs` and `CorpusRef_Csnobol4Suite.cs` to **snobol4dotnet**.
  Pattern: match `CorpusRef_Patterns.cs` exactly — inline the .sno source as a C# verbatim string, inline the .ref as the expected value.
  For tests with stdin embedded below END: split at END, pass the tail as `inputText` to `RunWithInput`.
  Read every .sno and .ref before writing a single test method.
  Gate: `dotnet test` compiles and all 126 test methods are present.

- [x] **S-9** — Add `test_csnobol4_suite.clj` to **snobol4jvm**.
  Pattern: match `test_runtime.clj` — inline source string, `CODE`/`RUN`/`with-out-str`, `is (= expected actual)`.
  For tests with stdin: verify how snobol4jvm handles INPUT before writing those tests.
  Read every .sno and .ref before writing a single test.
  Gate: `lein test SNOBOL4clojure.test-csnobol4-suite` compiles clean.

---

## Baseline (recorded at S-4/S-5)

- SPITBOL oracle — Budne suite: `45/116`
- CSNOBOL4 — Budne suite: `47/116`
- SPITBOL oracle — FENCE tests: `7/10` (3 fail: 061 seal, 064 capture, 065 decimal — SPITBOL bugs)
- CSNOBOL4 — FENCE tests: `1/10` (058 keyword passes; 059–067 fail until GOAL-CSNOBOL4-FENCE complete)

---

## Rules

- Commit identity: `LCherryholmes` / `lcherryh@yahoo.com`.
- Rebase before every .github push.
- See RULES.md for full handoff checklist.

---

## Final HEAD references
- harness: ef24086
- corpus: 73f8b1e

## Baseline (S-7 scrip)

- scrip — Budne + FENCE: `8/126` (10 FENCE all fail; scrip FENCE(P) not yet impl)

## Final HEAD references (updated)
- SCRIP: 7321eebb
- snobol4jvm: f35d392
- snobol4dotnet: 1414bb0
