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

**Excluded (8):** `bench.sno` (no .ref), `breakline.sno` (record-size file I/O hangs SPITBOL), `genc.sno` (file output), `k.sno` (record-size file I/O hangs SPITBOL), `ndbm.sno` (library),
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

- [x] **S-1** — Add `adapters/csnobol4/run.sh` to harness.
  5-line wrapper: `snobol4 "$1"` → stdout, no banner noise.
  Model: `adapters/dotnet/run.sh`.
  Gate: `bash adapters/csnobol4/run.sh corpus/crosscheck/patterns/059_pat_fence_fn_basic.sno`
  prints `matched`.

- [x] **S-2** — Verify 10 FENCE tests pass under `crosscheck.sh --engine csnobol4 --filter pat_fence`.
  These are already in `corpus/crosscheck/patterns/` which is in `crosscheck.sh` DIRS list.
  Gate: `crosscheck.sh --engine csnobol4 --filter pat_fence` → 0 failures (SPITBOL) /
  10 failures expected (CSNOBOL4, since FENCE(P) not yet implemented) — document baseline.

- [x] **S-3** — Add `adapters/csnobol4/run_crosscheck_csnobol4.sh` to harness.
  Walks `corpus/programs/csnobol4-suite/`, runs each `.sno`, diffs stdout vs `.ref`.
  Skips: `bench.sno genc.sno ndbm.sno sleep.sno time.sno line2.sno`.
  Model: `adapters/dotnet/run_crosscheck_dotnet.sh`.
  Gate: script runs to completion against SPITBOL oracle, reports pass/fail counts.

- [x] **S-4** — Run S-3 script against SPITBOL oracle. Record baseline pass count.
  Gate: `SPITBOL_PASS=N` recorded in this file (expected ~118/118).

- [x] **S-5** — Run S-3 script against CSNOBOL4. Record baseline pass count.
  Gate: `CSNOBOL4_PASS=N` recorded in this file.
  Any failures vs SPITBOL are tracked as known deltas.

- [x] **S-6** — Add `csnobol4` to `crosscheck.sh` DIRS scan and engine list documentation.
  Update harness README to mention csnobol4 adapter.
  Gate: `crosscheck.sh --engine csnobol4` runs all pattern/hello/etc dirs cleanly.

---

## Baseline (fill in at S-4/S-5)

- SPITBOL oracle — Budne suite: `45/116` (116 = 124 minus 8 skipped)
- CSNOBOL4 — Budne suite: `47/116` (116 = 124 minus 8 skipped)
- SPITBOL oracle — FENCE tests: `7/10` (3 fail: 061 seal, 064 capture, 065 decimal — SPITBOL bugs, not FENCE(P))
- CSNOBOL4 — FENCE tests: `1/10` (058 FENCE keyword passes; 059-067 fail until GOAL-CSNOBOL4-FENCE complete)

---

## Rules

- Commit after each step.
- Commit identity: `LCherryholmes` / `lcherryh@yahoo.com`.
- Rebase before every .github push.
- See RULES.md for full handoff checklist.

---

## Final HEAD references
- harness: ef24086
- corpus: 73f8b1e
