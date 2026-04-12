# GOAL-CSNOBOL4-HARNESS — Wire CSNOBOL4 Tests into Harness Drivers

**Repo:** harness (`adapters/csnobol4/`, `crosscheck/`)
**Done when:** all 128 CSNOBOL4 tests run through harness drivers against CSNOBOL4 and SPITBOL oracle.

---

## What this is

Two sets of programs now live in corpus:

| Set | Location | Count | Harness-ready |
|-----|----------|-------|---------------|
| FENCE tests | `crosscheck/patterns/058–067` | 10 | Yes — already in crosscheck dirs |
| Budne suite | `programs/csnobol4-suite/` | 124 | 118 (6 excluded: bench, genc, ndbm, sleep, time, line2) |

**Missing:** `adapters/csnobol4/run.sh` and `run_crosscheck_csnobol4.sh`.
Everything else is already in place.

**Excluded (6):** `bench.sno` (no .ref), `genc.sno` (file output), `ndbm.sno` (library),
`sleep.sno` / `time.sno` (time-dependent, -INCLUDE), `line2.sno` (no .ref).

---

## Repos needed

```bash
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/harness  /home/claude/harness
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/corpus   /home/claude/corpus
# CSNOBOL4 binary must be built — see harness/oracles/csnobol4/BUILD.md
# SPITBOL oracle: /home/claude/x64/bin/sbl (clone snobol4ever/x64)
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
```

---

## Steps

- [ ] **S-1** — Add `adapters/csnobol4/run.sh` to harness.
  5-line wrapper: `snobol4 "$1"` → stdout, no banner noise.
  Model: `adapters/dotnet/run.sh`.
  Gate: `bash adapters/csnobol4/run.sh corpus/crosscheck/patterns/059_pat_fence_fn_basic.sno`
  prints `matched`.

- [ ] **S-2** — Verify 10 FENCE tests pass under `crosscheck.sh --engine csnobol4 --filter pat_fence`.
  These are already in `corpus/crosscheck/patterns/` which is in `crosscheck.sh` DIRS list.
  Gate: `crosscheck.sh --engine csnobol4 --filter pat_fence` → 0 failures (SPITBOL) /
  10 failures expected (CSNOBOL4, since FENCE(P) not yet implemented) — document baseline.

- [ ] **S-3** — Add `adapters/csnobol4/run_crosscheck_csnobol4.sh` to harness.
  Walks `corpus/programs/csnobol4-suite/`, runs each `.sno`, diffs stdout vs `.ref`.
  Skips: `bench.sno genc.sno ndbm.sno sleep.sno time.sno line2.sno`.
  Model: `adapters/dotnet/run_crosscheck_dotnet.sh`.
  Gate: script runs to completion against SPITBOL oracle, reports pass/fail counts.

- [ ] **S-4** — Run S-3 script against SPITBOL oracle. Record baseline pass count.
  Gate: `SPITBOL_PASS=N` recorded in this file (expected ~118/118).

- [ ] **S-5** — Run S-3 script against CSNOBOL4. Record baseline pass count.
  Gate: `CSNOBOL4_PASS=N` recorded in this file.
  Any failures vs SPITBOL are tracked as known deltas.

- [ ] **S-6** — Add `csnobol4` to `crosscheck.sh` DIRS scan and engine list documentation.
  Update harness README to mention csnobol4 adapter.
  Gate: `crosscheck.sh --engine csnobol4` runs all pattern/hello/etc dirs cleanly.

---

## Baseline (fill in at S-4/S-5)

- SPITBOL oracle — Budne suite: `?/118`
- CSNOBOL4 — Budne suite: `?/118`
- SPITBOL oracle — FENCE tests: `10/10`
- CSNOBOL4 — FENCE tests: `0/10` (expected until GOAL-CSNOBOL4-FENCE complete)

---

## Rules

- Commit after each step.
- Commit identity: `LCherryholmes` / `lcherryh@yahoo.com`.
- Rebase before every .github push.
- See RULES.md for full handoff checklist.
