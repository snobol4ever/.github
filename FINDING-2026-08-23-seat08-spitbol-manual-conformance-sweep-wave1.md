# FINDING 2026-08-23 seat08 — SPITBOL manual conformance sweep, wave 1 (Ch15/16/18 complete, Ch19 pending)

Row: `conformance-sweep-spitbol-manual` (rank 0, "the highest-yield row factory we have, and it has never been run"). This is the first time the manual's reference section has been walked construct-by-construct against SCRIP.

## Deliverable 1: the construct count nobody had

Source: `/home/claude/.tools/docs/spitbol-manual-v3.7.txt`, 15,132 lines, verified line count. Part III "Reference Manual" (Chapters 12-19) is the reference section. Enumerated by chapter:

| Chapter | Category | Count | Notes |
|---|---|---:|---|
| 15 | Unary operators | 15 | 9 defined + 6 reserved (`! % / # = \|`, no built-in semantics — available for user `OPSYN()`) |
| 15 | Binary operators | 16 | 11 defined (exponentiation counted once, 3 accepted spellings `^ ! **`) + 5 reserved (`& @ # % ~`) |
| 16 | Protected keywords | 19 | `&ABORT` ... `&UCASE` |
| 16 | Unprotected keywords | 18 | `&ABEND` ... `&TRIM` |
| 16 | Special names | 10 | `ABORT`(label) `CONTINUE` `END` `FRETURN` `INPUT` `NRETURN` `OUTPUT` `RETURN` `SCONTINUE` `TERMINAL` |
| 18 | Primitive patterns | 7 | `ABORT ARB BAL FAIL FENCE REM SUCCEED` |
| 19 | Built-in functions | 83 | unique names in the Function Summary (p.210-211), overload variants (e.g. `ITEM(array,..)`/`ITEM(table,..)`) not double-counted |
| **Total** | | **168** | |

Chapter 17 (Data Type Names, 9 types) and Chapter 14 (Statement forms) are exercised indirectly through the functions/operators that use them (`CONVERT`, `DATATYPE`, assignment, pattern-match) rather than enumerated as standalone constructs — they aren't independently invocable the way a function or keyword is.

## Deliverable 2: wave 1 results — Chapters 15, 16, 18 fully swept (85 of 168 constructs)

Methodology: for each construct, mint the smallest `.sno` witness — sourced from the manual's own worked example wherever the manual gives one (most do), never invented from scratch when a manual example existed. Run via `bash scripts/test_one_witness.sh <witness> <tag>`, which diffs m3 and m4 output against `x64/bin/sbl -bf` (mandatory `-bf` per RULES.md s189, timeout 15s per run). Witnesses live in `corpus/probe/conformance/`; the full batch re-runs via the new `scripts/test_conformance_spitbol_manual.sh`.

**61 witnesses covering 85 constructs** (several witnesses exercise more than one related construct together, e.g. the manual's own `$N LEN(*N) . FIELD` example covers both immediate-assignment `$` and conditional-assignment `.` in one program):

- **50 AGREE** (SCRIP m3 and m4 both byte-match the oracle).
- **11 DIVERGE**, filed as **9 new queue rows** (two rows each bundle two closely-related witnesses that look like the same root cause):

| Rank | Row | What's broken |
|---|---|---|
| 0 | `conform-defer-tab-span-crash` | m3 **SIGABRT**, m4 **link failure** (`undefined reference to 'PAT$0_ω'`) on the manual's own deferred-evaluation-as-pattern-function-argument example (p.87-88, `TAB(*I)`/`SPAN(*S)`) |
| 1 | `conform-amp-abort-fence-broken` | `&ABORT` / `&FENCE` (keyword-form primitive patterns) silently lose their special control-flow semantics; bare `ABORT`/`FENCE` and the other 5 keyword-form primitives (`&ARB &BAL &FAIL &REM &SUCCEED`) all work |
| 1 | `conform-line-lastline-crash` | reading `&LINE` or `&LASTLINE` truncates output and exits rc=1; `&STNO`/`&LASTNO` (sibling statement-number keywords) work fine |
| 1 | `conform-rtntype-not-tracked` | `&RTNTYPE` always empty instead of `'RETURN'`/`'FRETURN'` after a function returns |
| 1 | `conform-end-label-ignored` | `END <label>` silently ignored — execution always starts at the top of the program, never at the named label |
| 2 | `conform-fnclevel-not-tracked` | `&FNCLEVEL` stays 0 inside a function call instead of incrementing |
| 2 | `conform-file-keyword-empty` | `&FILE` reads empty and the process exits rc=1 on a one-line program |
| 2 | `conform-unary-interrog-gz5-gap` | manual's own unary-`?` example hits the known GZ#5 landed-subset FATAL (both modes) — likely a sibling of the already-fixed `comment.sno` GZ#5 gap, not a new bug class |
| 3 | `conform-case-keyword-mismatch` | `&CASE` reads 1 (SCRIP) vs 0 (`-bf` oracle) — flagged as probably a test-methodology artifact of the mandatory `-f` flag, not a language bug; needs an HQ ruling before anyone spends a session on it |

Each row's task file (`/home/resources/postoffice/tasks/<row>.task.md`) carries the measured oracle-vs-SCRIP output, a root-cause hypothesis where I had one, and a concrete `DONE-WHEN`. Per this row's brief, **none of these nine were cured** — discovery/classification/witness/row only, per "do not stop to cure what you find."

One correction worth recording: my first draft of the `&RTNTYPE` witness had a control-flow bug of my own (two `DEFINE` statements each jumping past the other) that made the *oracle itself* error. Caught it by reading the oracle's own output before concluding SCRIP was wrong — worth restating as a habit for whoever continues this sweep: **always check the oracle's own output first; an oracle error means your witness is broken, not that you found a bug.**

### Explicitly marked UNTESTABLE-HERE (with reason, not skipped silently)

- **11 reserved operator symbols** (6 unary `! % / # = |`, 5 binary `& @ # % ~`): the manual labels these "Unused... available for user definition using `OPSYN()`" — no built-in semantics exist to diff against. Testing `OPSYN()` attachment itself is a *different* construct (already in scope as a Ch19 function).
- **`&ABEND`, `&COMPARE`**: manual states both are explicitly inert in this implementation ("does not perform any useful function," "ignored... present for compatibility") — nothing to diff.
- **`CONTINUE`, `SCONTINUE`, and `ABORT`-as-special-label**: all three require a live `SETEXIT()` error-interception context; `SCONTINUE` specifically requires a genuine error 320 (user keyboard interrupt), which can't be safely or deterministically delivered inside a `timeout`-wrapped batch harness. Deliberately deferred rather than risking an unreliable witness — a good-sized follow-up sub-sweep on its own (SETEXIT + the three error-intercept special labels + `&ERRTEXT`/`&ERRTYPE` *after a real triggered error*, which wave 2 only checked at their inert initial values).
- **`&DUMP`, `&PROFILE`**: only their safe initial-value read was tested (both AGREE). Actually triggering the dump/profile file-output side effect was out of scope for this pass — verbose, cross-run-format-risk, and lower value than the control-flow/keyword-tracking bugs found above.

## Continuation — Chapter 19 (Functions), not yet started

83 built-in functions remain, grouped in the manual's own Function Summary order (p.210-211): Arrays and tables (6) → Compilation (2) → Function control (7) → Input/output (8) → Memory (3) → Miscellaneous (7) → Numeric (9) → Numeric comparison (7) → Object comparison (2) → Object creation (2) → Pattern match (12) → Program control (6) → Program-defined data type (3) → String comparison (6) → String synthesis (7). Recommend continuing in that order, reusing the `test_one_witness.sh` + `corpus/probe/conformance/` convention established here, and folding new results into `scripts/test_conformance_spitbol_manual.sh` (it already re-runs the whole directory, no changes needed as new witnesses are added).

The row's `## NEXT` has been rewritten with this exact cursor. `DONE-WHEN` (artifact-existence only) now technically passes — `corpus/probe` has witnesses and `scripts/test_conformance_spitbol_manual.sh` exists — but the row is being left **OPEN, not closed**: the brief is to sweep the *whole* reference section, and closing it at 85/168 constructs on a structural existence-check technicality would be exactly the false-green gap RULES.md warns about. Whoever picks up Chapter 19 should extend, not restart.
