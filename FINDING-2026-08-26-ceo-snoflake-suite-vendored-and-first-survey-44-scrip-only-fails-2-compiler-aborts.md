# FINDING — Ori Livneh's snoflake test suite is vendored (BSD-2-Clause) and first-surveyed: 44 SCRIP-only fails, 2 compiler aborts, dialect distance calibrated by a SPITBOL arm

**Seat:** ceo (on Lon's direct in-chat instruction: check the snoflake suite's license, vendor it if shared, run all of it) · **Date:** 2026-08-26 · **Mode:** FLEET-16
**Trees:** SCRIP `8d27b148` (runner landed after at `8e03e1e0`) / corpus `b1649085f` · RT_OPT `-O0` · timeout 8s · oracle `sbl -bf` via `lib_oracle_flags.sh`

## 1. LICENSE — YES, SHARED

[github.com/atdt/snoflake](https://github.com/atdt/snoflake) — a JavaScript SNOBOL4 runtime by **Ori Livneh** — is **BSD 2-Clause** (*"Copyright (c) 2012-2026, Ori Livneh … redistribution and use in source and binary forms, with or without modification, are permitted"*), plus `LICENSE-CSNOBOL4` for incorporated CSNOBOL4-derived material. Redistribution requires retaining the notices; both files are retained beside the vendored tree.

## 2. VENDORED

`corpus/packages/snobol4/snoflake_suite/` (corpus `b1649085f`): **180 fixture `.sno`** + `gimpel/` INCLUDE library (133 `.INC`, 4 `.IN`) + both LICENSE files + upstream README + `PROVENANCE.md` (upstream commit `54f7b801`, 2026-06-13). Reference clone: `/home/resources/snoflake-master` (outside the root per handoff-discovery law). ⛔ **Not wired into any board — no denominator change**; wiring is an HQ decision with its own attributed commit.

⭐ **The fixture format is self-describing and dialect-portable:** the header is legal SNOBOL4 comment lines (`@title/@options/@input/@expect/@match(exact|substring|error, /i)/@attribution/@nonstandard`), then a program that runs unmodified under any implementation — the expected output travels WITH the program. 45 fixtures carry embedded stdin; 7 are `@nonstandard` (implementation-defined; upstream's own cross-checks skip them).

## 3. THE FIRST SURVEY (runner: `SCRIP/scripts/test_snoflake_suite.sh`, rc=2-refusal, never skip-as-success)

Axes: SCRIP `8d27b148` · corpus `b1649085f` · RT_OPT `-O0` · timeout 8s · graded vs each fixture's **EMBEDDED** `@expect` (snoflake/SIL-3.11/CSNOBOL4 dialect, NOT SPITBOL refs). 173 standard + 7 NSTD.

| arm | PASS | FAIL | SKIP(cc) | NSTD pass |
|---|---|---|---|---|
| SCRIP mode-3 (`--run`) | 65 | 108 | — | 0/7 |
| SCRIP mode-4 (`--compile`) | 64 | 45 | 65 | 0/6 |
| `sbl -bf` (informational) | 107 | 66 | — | 2/7 |

## 4. WHAT THE SPITBOL ARM BUYS — THE DIALECT CALIBRATION

Even SPITBOL fails **66/173** of these fixtures: TRACE family, DUMP formats, `&`-keyword behaviors, real-number formatting, RANDOM-seeded gimpel programs, case-folding toggles, `csnobol4-extensions`. Those 66 are **dialect distance, not SCRIP defects** — grading SCRIP raw against this suite would overstate the defect surface by 2.5x. Per the dialect FACT RULE, the actionable set is the difference:

⭐ **44 fixtures where `sbl -bf` PASSES and SCRIP m3 FAILS** — genuine SCRIP gaps on SPITBOL-compatible programs:
`control-flow control-hide-list-control-line cursor-position-underline dump-ordered dump-variables eliza-modernized factorial-table fullscan-overlap fullscan-palindrome gimpel-array-functions gimpel-asm360-pli-once gimpel-binary-tree-linearize gimpel-code-function gimpel-combinatorics gimpel-linked-list-functions gimpel-l-one-compiler gimpel-read-list-functions gimpel-rseason-baseball gimpel-snobol-statement-reader gimpel-sorting-functions gimpel-stack-field-functions gimpel-state-functions gimpel-test-pattern-predicate gimpel-tree-pattern indirect-integer-and-keyword indirect-reference infix-to-polish input-output-streams kalah-opening-search keywords-and-code letter-count letter-counter n-queens numeric-comparison pattern-assignment-targets programmer-defined-functions real-to-integer-coercion scanner-behavior special-patterns statements stlimit-negative-stcount wang-theorem-prover word-count-table-convert word-ending-analysis`

## 5. ⛔ TWO COMPILER ABORTS — NAMED CRASH WITNESSES

`./scrip --compile` **rc=134 (SIGABRT, core dumped)** on `fullscan-overlap.sno` and `word-ending-analysis.sno`. A compiler abort on legal input is a defect regardless of dialect; both are also in the 44-set (sbl passes them). Mode-4's SKIP(cc)=65 otherwise means compile-or-link refused; m3 runs the same programs in-process, so the m3 column is the coverage floor.

## 6. CAVEATS RECORDED

- `@options` is not honored by the runner (3 fixtures: `case-fold-disabled`, `gimpel-bnorm-inorm-image-line`, `stlimit-host-option`) — their verdicts carry that caveat, printed in the OPTS line.
- `error`-mode grading = nonzero rc OR `/error/i` in combined output — convention documented in the script header.
- NSTD 0/7 under SCRIP vs 2/7 under sbl: informational only, never gated.

## 7. ROUTING

Runner is durable at `SCRIP/scripts/test_snoflake_suite.sh` (SCRIP `8e03e1e0`). HQs telegrammed: the 44-set and the two abort witnesses are mintable rows in the correctness lane; suite wiring into boards (denominator change) is an HQ decision. This FINDING is the survey of record; re-run the script rather than quoting these numbers on a moved tree.
