# FINDING — snoflake re-baseline on the swapped oracle, and the four fixture reds characterized

**Seat:** seat01 · **Date:** 2026-09-04 · **Row:** `snoflake-re-baseline-on-the-swapped-oracle-and-the-four-fixture-reds`
**Measured at** SCRIP `0fa9c4cb` · corpus `33e747c2c` · RT_OPT=-O0 · oracle x64 `c0dc231` (post-swap, 18:19 CDT) · timeout 8s

## PART 1 — RE-BASELINE

| arm | hq_B's ~18:00 reading (SCRIP `943517c38`, pre-swap oracle) | this reading (SCRIP `0fa9c4cb`, post-swap oracle) | delta |
|---|---|---|---|
| m3 (`--run`) | PASS=84 FAIL=89 | PASS=85 FAIL=88 | +1 PASS / −1 FAIL |
| m4 (`--compile`) | PASS=84 FAIL=46 SKIP(cc)=44 | PASS=85 FAIL=49 SKIP(cc)=40 | +1 PASS / +3 FAIL / −4 SKIP(cc) |
| sbl `-bf` | PASS=107 FAIL=66 | PASS=107 FAIL=66 | unchanged (aggregate) |
| csnobol4 | PASS=168 FAIL=5 | PASS=168 FAIL=5 | unchanged, same 5 names as FINDING-2026-08-28-hq_C |

**⭐ Two independent things moved between the two readings, not one — do not attribute the m3/m4 delta to the oracle swap:**
1. **SCRIP's own source moved**, `943517c38` → `0fa9c4cb` (ordinary upstream landings, unrelated to snoflake). m3/m4 are graded against the fixture's own embedded `@expect`, never against `sbl` — so the oracle swap cannot be what moved them. The +1/+3/−4 shape (4 fixtures left SKIP(cc): 1 to PASS, 3 to FAIL) is upstream SCRIP progress/regression between the two commits, full stop.
2. **The sbl oracle binary was swapped** (x64 `c0dc231`, the SIGSEGV-on-exit class cured) — this is the only thing that could move the `sbl` arm, and by extension the OURS/DIALECT/FIXTURE triangulation the two dependent rows (`snoflake-ours-26-...`, `snoflake-dialect-60-...`) are built on.

**⛔ On (2), I can confirm the AGGREGATE is stable but not fully rule out a same-size bucket swap.** sbl reads PASS=107 FAIL=66 here, identical to hq_B's pre-swap ~18:00 reading *and* to FINDING-2026-08-28-hq_C's reading taken 7 days and one build ago — three independent measurements, one number. That is reasonably strong circumstantial evidence the exit-crash class doesn't intersect this suite's 180 fixtures at all. It is **not a fixture-level diff**: neither the ~18:00 reading nor the 08-28 FINDING recorded a per-fixture sbl fail *list*, only the aggregate count, so a same-size swap (one fixture FAIL→PASS, a different one PASS→FAIL, net zero) cannot be excluded from the record as it stands. **This FINDING now becomes that fixture-level baseline** — the full `FAIL-SBL` list below is captured specifically so the next re-run has something real to diff against, which is the gap hq_B's warning correctly identified.

Full fixture-level lists, this run (for the two class rows to build on — do not re-run to get these, they're already here):

```
FAIL-M3 (88): arbitrarily-long-integers bubble-sort case-folding complex-multiplication-opsyn
control-hide-list-control-line control-hide-statement-numbers csnobol4-extensions eliza-duquet-original
eliza-modernized endfile-rewind-write-read errlimit eval-apply-opsyn fullscan-palindrome
gimpel-additional-string-functions gimpel-array-functions gimpel-asm-machine-m
gimpel-basic-string-functions gimpel-binary-tree-linearize gimpel-bnorm-inorm-image-line
gimpel-combinatorics gimpel-conversions gimpel-crack-cata-functions gimpel-dextern-loader
gimpel-fortran-blank-removal gimpel-function-tracing gimpel-general-purpose-macro
gimpel-generated-stack-functions gimpel-implementation-and-timing gimpel-infinip-arithmetic
gimpel-insulate-anchor gimpel-line-output gimpel-linked-list-functions gimpel-l-one-compiler
gimpel-l-two-compiler gimpel-merge-tournament-sort-variants gimpel-mfread-multi-file
gimpel-numeric-random-functions gimpel-oneway-cipher gimpel-pattern-functions
gimpel-permutation-functions gimpel-physical-quantities gimpel-poker-game
gimpel-print-width-functions gimpel-random-poem gimpel-random-story gimpel-random-string-functions
gimpel-read-list-functions gimpel-real-math-functions gimpel-snobol-statement-reader
gimpel-sorting-functions gimpel-stack-field-functions gimpel-state-functions gimpel-stone-game
gimpel-tree-pattern gimpel-visit-structure-functions indirect-integer-and-keyword
indirect-real-illegal-type infix-to-polish kalah-opening-search lexical-comparison
lowercase-indirect-and-apply math-functions n-queens numeric-keywords opsyn-case-fold
output-format-ignored pattern-assignment-targets recursive-balanced-pattern
recursive-expression-recognizer recursive-yz-pattern stack-opsyn stlimit-negative-stcount
stop-tracing string-pad syntactic-recognizer topological-sort trace-all-functions
trace-function-calls trace-keyword-fnclevel trace-label-flow trace-procedure trace-value-watch
twelve-days unload-builtin value-trace-during-match wang-theorem-prover word-count-table-convert
word-ending-analysis

FAIL-SBL (66): arbitrarily-long-integers bubble-sort case-folding character-set-keywords
complex-multiplication-opsyn control-hide-statement-numbers csnobol4-extensions eliza-duquet-original
endfile-rewind-write-read errlimit eval-apply-opsyn gimpel-additional-string-functions
gimpel-asm-machine-m gimpel-basic-string-functions gimpel-bnorm-inorm-image-line
gimpel-crack-cata-functions gimpel-dextern-loader gimpel-fortran-blank-removal
gimpel-function-tracing gimpel-general-purpose-macro gimpel-generated-stack-functions
gimpel-implementation-and-timing gimpel-infinip-arithmetic gimpel-insulate-anchor
gimpel-line-output gimpel-l-two-compiler gimpel-merge-tournament-sort-variants
gimpel-mfread-multi-file gimpel-numeric-random-functions gimpel-oneway-cipher
gimpel-pattern-functions gimpel-permutation-functions gimpel-physical-quantities gimpel-poker-game
gimpel-print-width-functions gimpel-random-poem gimpel-random-story gimpel-random-string-functions
gimpel-real-math-functions gimpel-stone-game gimpel-visit-structure-functions
indirect-real-illegal-type integer-negative-exponent lexical-comparison lowercase-indirect-and-apply
math-functions numeric-keywords opsyn-case-fold output-format-ignored recursive-balanced-pattern
recursive-expression-recognizer recursive-yz-pattern stack-opsyn stop-tracing string-pad
syntactic-recognizer topological-sort trace-all-functions trace-function-calls
trace-keyword-fnclevel trace-label-flow trace-procedure trace-value-watch twelve-days
unload-builtin value-trace-during-match

FAIL-CSN (5): case-fold-disabled eliza-duquet-original endfile-rewind-write-read
gimpel-asm-machine-m math-functions

OPTS not honored (3, runner caveat, unrelated to the 5 above): case-fold-disabled
gimpel-bnorm-inorm-image-line stlimit-host-option
```

**Consequence for the two dependent rows:** `snoflake-ours-26-...` and `snoflake-dialect-60-...` should build their triangulation from *this* run's three lists (FAIL-M3, FAIL-SBL, FAIL-CSN above), not from hq_B's ~18:00 numbers — the denominator is the same 180 fixtures but the m3 membership changed by one (check whichever fixture moved SKIP↔FAIL↔PASS against your own list before trusting it). `SCORE.md` was rewritten in place by this run's own execution of the suite runner (`snobol4/vendor` row, line 72) — that is a side effect of running the script, not a separate action taken here.

## PART 2 — THE 4 FIXTURE REDS, CHARACTERIZED

All four are in `FAIL-CSN` — nobody passes them, csnobol4 (the suite's home dialect) included — so per the task's own framing, each is a **fixture or runner defect, never a SCRIP codegen defect**, confirmed by direct inspection below. None of the four appear on the `OPTS not honored` list, so an unhonored `@options` directive is not the explanation for any of them.

### `eliza-duquet-original` → **vendored-fixture row** (unreachable `@expect`) + a separate, smaller parser finding
`@expect` wants a 5-line ELIZA-style transcript. **Neither oracle reaches it**: both `sbl` and `csnobol4`
print only `ENTER SCRIPT` and stop — the fixture's conversational engine never produces the rest of the
transcript under this harness's batch `@input` feed, for any engine. That alone makes the `@expect` block
unreachable as written; a local edit is not in scope (upstream, BSD-2-Clause, PROVENANCE.md) and would be
the shrunken-denominator move.
Separately, and not gating this fixture either way: **SCRIP m3 fails to *parse* it** (`snobol4:129: error:
parse error: syntax error`), where line 129 is well past the program's own `END` (line 121) — the trailing
text is a hand-written word-substitution table (`ALWAYS L /2/ D //` etc.) the ELIZA engine presumably reads
back at runtime via file I/O on its own source, a classic old-SNOBOL trick. SCRIP's parser keeps reading
and tries to compile that trailing data as statements; real SPITBOL and csnobol4 apparently stop at `END`
and never choke on it. Worth its own row (SCRIP parser: don't attempt to compile source past `END`), but
fixing it would not make this fixture pass — the oracles' own stall at `ENTER SCRIPT` is the binding
constraint, independent of SCRIP's parse behavior.

### `endfile-rewind-write-read` → **RUNNER row**
`OUTPUT(.W, 8, , 'tmp/endfile-cycle.dat')` names a **relative subdirectory** (`tmp/`) that the suite
runner's scratch `$RUN` (a fresh `mktemp -d`, no `tmp/` inside it) never creates. Real SPITBOL throws
**ERROR 160 "inappropriate file specification for output"** on exactly this — SPITBOL refuses to
auto-vivify the missing directory. SCRIP m3/m4 and csnobol4 don't hard-error but silently produce empty
reads (`FIRST: `/`SECOND: `/`REWOUND: ` with nothing after the colon) — consistent with a file that never
successfully got written to begin with. This is an environment precondition the harness doesn't set up,
not a SCRIP defect: fix belongs in `scripts/test_snoflake_suite.sh` (`mkdir -p "$RUN/tmp"` before the run
loop, or symlink it alongside the existing `*.INC`/`*.IN` setup at line 67).

### `gimpel-asm-machine-m` → **DIALECT row** (do not cure)
The fixture's own vendored include, `gimpel/RPAD.INC`, does `DEFINE('RPAD(S,N,C)')` — and **both SCRIP m3
and real `sbl` refuse it identically**: `ERROR 248 -- attempted redefinition of system function: RPAD`,
same function name, same error number. SCRIP is exactly tracking SPITBOL's protected-builtin-name behavior
here (RULES.md dialect law: matching `sbl` is correct, not a bug). Only `csnobol4` — a dialect without that
protected name — gets past the `DEFINE`, and even then it never reaches `@expect`: it times out (rc=124)
spinning on the last input line (`Z LOAD 0,0`) instead of halting after 6 lines, so csnobol4 doesn't
actually pass this one either, it just fails differently (timeout vs. hard error).

### `math-functions` → **DIALECT row** (do not cure)
Line 26, `X = SQRT(-1.0) :S(F1)F(F2)`, is written assuming SNOBOL4 goal-directed failure: SQRT of a
negative should just *fail* the assignment and branch to `F2` (`'sqrt of negative fails'`), then continue
to the final range check. **SCRIP (m3 and m4) and real `sbl` both instead raise a fatal, program-halting
error at that exact call** — `ERROR 314 -- sqrt argument negative` — before the `:S()F()` branch logic ever
runs, so neither ever reaches the last two expected lines. Only `csnobol4` treats it as recoverable and
prints the full expected transcript (module a cosmetic `-3` vs. `-3.` real-number formatting nit on an
earlier line, not the blocker). This is the textbook case the runner's own header comment already warns
about (snoflake tracks CSNOBOL4/SIL 3.11, SCRIP tracks SPITBOL) — SCRIP matching `sbl` byte-for-byte here
is correct behavior, not a defect.

## SUMMARY / ROUTING

| fixture | root cause | route |
|---|---|---|
| `eliza-duquet-original` | @expect unreachable by any engine (ELIZA engine stalls after banner under batch input) | vendored-fixture (no local edit — PROVENANCE.md note only if excluded) |
| `eliza-duquet-original` (secondary) | SCRIP parses past `END` and chokes on trailing non-code data | separate parser row, does not gate this fixture |
| `endfile-rewind-write-read` | harness scratch dir has no `tmp/` subdir; even `sbl` ERRORs on the missing dir | RUNNER row — `test_snoflake_suite.sh` |
| `gimpel-asm-machine-m` | `RPAD` collides with a protected builtin in both SCRIP and `sbl`; csnobol4 lacks that protection but times out anyway | DIALECT — do not cure |
| `math-functions` | `SQRT(-1.0)` is a fatal SPITBOL/SCRIP error, not a SNOBOL4-failure csnobol4 treats it as | DIALECT — do not cure |

None of the four are SCRIP codegen defects. Two are DIALECT (SCRIP correctly tracking SPITBOL), one is a
RUNNER gap (missing scratch subdirectory), one has a genuinely unreachable `@expect` plus an unrelated,
separately-worth-fixing SCRIP parser behavior (reading past `END`).
