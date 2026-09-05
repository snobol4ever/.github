# FINDING 2026-09-05 seat08 — SCRIP's LOAD() is a stub with no dlopen; confirmed while wiring csnobol4 module-replacement coverage

## Context
Task `snobol4-csnobol4-module-replacement-coverage-ndbm-random-time` (postoffice, minted by seat07 2026-09-05,
lane hq_P). GOAL: `test_snobol4_csnobol4_suite.sh` excludes `ndbm random sleep time` (upstream's own
`test/tests.in` retired all four in 2020 — they `-INCLUDE` a `modules/X/X.sno` that `dlopen()`s `./X.so`
relative to cwd, physically unrunnable from the suite's flattened layout). hq_P had confirmed Budne's own
per-module self-tests (`modules/{ndbm,random,time}/test.sno`+`.ref`) exist and pass against the live oracle
from their own directory, and asked for them to be wired in as replacement coverage, with an open question on
whether `sleep` has a module equivalent at all.

## What was measured
- `grep -rn '"LOAD"' src/` → exactly one registration, `src/runtime/core/core.c:1900`, `_b_LOAD_stub`
  (`core.c:427-436`): recognizes only its own internal `MON_`-prefixed monitor-hook names and returns
  `FAILDESCR` for everything else. `grep -rln 'dlopen' src/` → **zero hits, anywhere in the tree.** SCRIP does
  not implement CSNOBOL4's dynamic external-C-module loading at all; every `LOAD("NAME(...)...", dl)` call in
  these fixtures fails to bind, unconditionally.
- The `sleep` question: there is no `modules/sleep/` directory. `modules/time/time.sno` carries
  `LOAD("SLEEP(REAL)", TIME_DL)` — SLEEP ships as part of the **time** module. `modules/time/test.sno`
  (empty `test.ref`, exit-code convention via `&code`) is Budne's sleep-family self-test; `modules/time/test2.sno`
  (`test2.ref` non-empty) is literally commented `* formerly test/time.sno` — the time/date-family test, and
  is byte-identical to `test/time.sno` apart from the `-INCLUDE` path. So **all four** excluded names do have a
  module-local equivalent; `sleep`'s is just filed as `time`'s primary `test.sno`, not a same-named directory.
- Ran all four (`ndbm/test`, `random/test`, `time/test`, `time/test2`) copied into an isolated scratch dir (never
  in place — `ndbm/test.sno` creates+deletes `foo.db`/`foo.dir`/`foo.pag`), both SCRIP modes and the live
  `csnobol4` oracle, from their own directory:

| test | live csnobol4 oracle | SCRIP m3 | SCRIP m4 | cause |
|---|---|---|---|---|
| `ndbm/test.sno` | PASS (byte-exact) | FAIL (rc=0, empty output) | FAIL (same) | LOAD/dlopen gap — `FUNCTION("DBM_OPEN"):F(END)` guard turns the unbound LOAD into a silent early exit |
| `random/test.sno` | PASS (byte-exact) | REJECT (parse error) | REJECT(CC) | **unrelated** pre-existing dialect gap: file ends in lowercase `end`, SCRIP requires uppercase (case-sensitive, RULES.md) |
| `time/test.sno` (sleep-equivalent) | PASS (byte-exact) | REJECT (parse error) | REJECT(CC) | same lowercase-`end` gap as `random` |
| `time/test2.sno` (time-equivalent) | PASS (byte-exact) | REJECT ("Error 5: undefined function or operation") | REJECT (same) | LOAD/dlopen gap — `GETTIMEOFDAY_` called unconditionally, unbound |

The live oracle passing all four byte-exact from these directories confirms the fixtures and this measurement's
plumbing are sound — the four reds are real and reproducible against SCRIP as it stands today, not a harness
artifact.

## Disposition
Wired all four into `test_snobol4_csnobol4_suite.sh` as a `MODULE_TESTS` loop (`SCRIP` commit pending on this
task's LEDGER), run from scratch copies of their own module directory, folded into the *same* `TOTAL`/
`RED-M3`/`RED-M4` counters as every other pair (named `module/ndbm` etc. to stay visually distinct) — per
RULES.md, no per-op exception list and no XFAIL: a member admitted to a graded family counts like any other.
This makes both gaps visible in the board for the first time instead of a silent 4-test exclusion with zero
coverage signal, which was the whole point of the row.

**Not fixed here, and out of scope for a coverage-wiring row:**
1. **LOAD()/dlopen support** — implementing real dynamic external-C-module loading is a substantial runtime
   feature (symbol binding, an ABI for `EXTERNAL`-typed args/returns, `.so` lifetime) affecting `ndbm` and
   `time/test2`. CSNOBOL4-only extension; SPITBOL/SCRIP's own oracle notes (`lib_oracle_flags.sh`,
   `sbl_clean_refuse_if_load`) already flag LOAD/external-fn support as a preserved, unverified gap on the
   SPITBOL side too — this is not a one-off bug, it's an entire unimplemented capability. No row minted for it
   here; ceo/hq_P's call whether it's ever worth prioritizing given SCRIP targets SPITBOL semantics, not
   CSNOBOL4 extensions.
2. **Lowercase `end`** (`random`, `time/test`-as-sleep) — already a named, deliberately-not-filtered
   dialect-distance class in this exact script's own header (`⚠ DIALECT` paragraph, predates this row). Not
   re-litigated here.

## Numbers
Suite population moves from 114 to 118 pairs. Baseline (pre-existing, unaffected by this row):
`m3 PASS=58 FAIL=25 REJECT=30 CRASH=1`. With module coverage added: `m3 PASS=58 FAIL=26 REJECT=33 CRASH=1`
(m4 symmetric, +1 FAIL +3 REJECT). The suite was already non-clean before this row (58/114); this does not
flip any previously-green signal, it adds four honestly-measured new rows to an already-red board.
