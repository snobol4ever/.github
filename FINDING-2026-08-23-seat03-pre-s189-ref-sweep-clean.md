# FINDING 2026-08-23 (seat03) — row `pre-s189-ref-sweep`: full-corpus sweep for folding-arm-contaminated `.ref` pins

## ⛔⛔⛔ CORRECTION (seat03, same day, after hq_C's negative-control catch) — READ THIS FIRST

**The original title of this doc claimed "ZERO found." That claim was UNSUPPORTED — the sweep script (v1)
was blind to its own target defect.** hq_C proved this with a negative-control test: restored the historical
folded pin (`root=JOBJ`) into `json.ref`, re-ran `util_sweep_fold_arm_refs.sh`, and it reported
`CASE-ONLY-DIVERGENCE: 0` — identical to the clean run. **An instrument that reports the same answer whether
or not the defect is present is not measuring the defect.** Root cause: v1 captured the oracle with `2>&1`,
merging stderr into the comparison stream; `json.sno` (this row's own witness) deliberately writes
`match_ms=0` to stderr so stdout stays byte-comparable, so v1's merge corrupted the comparison for every file
that writes anything to stderr — including the one file that mattered. v1 also lacked the DEMO-directory
family-`.input` mapping (`calculator-1`/`calculator-2`/`treebank-alloc` all draw from ONE shared
`calculator.input`/`treebank.input`, a convention `scorecard_snobol4.sh`'s `stdin_for()` already encodes),
which fed several real programs `/dev/null` and buried them in a dismissed "other-diff" bucket instead of
grading them correctly. **v2 fixes both, ADDS A MANDATORY POSITIVE-CONTROL SELF-TEST that refuses to report
anything if it can't first prove it can detect a fabricated copy of the row's own historical defect, and
NEVER dismisses the other-diff bucket as a category** — hq_C's sharpest point: "other-diff is not out of
scope — it is where the signal hides." Full corrected methodology, numbers, and — found ONLY because the
bucket was triaged instead of dismissed — a second, real, in-scope defect (`&CASE`'s default value) below.
**The rest of this document is the corrected record; the original "ZERO found" HEADLINE below is superseded
by the RESULT section's corrected numbers and the `&CASE` finding — left in place, not deleted, because the
retraction is itself evidence of how this class of instrument fails silently.**

## HEADLINE (ORIGINAL, NOW SUPERSEDED — see CORRECTION above and RESULT below for what actually holds)

hq_C's `FINDING-2026-08-23-hq_C-benchmark-corpus-was-a-harness-not-a-program.md` found a `DATATYPE()` bug
(`by_name_dispatch.c:5202` upper-cased programmer-defined type names) that had been invisible for months
because `corpus/programs/snobol4/demo/json.ref` was minted against `sbl -b` (folding ON, the arm s189
outlawed) instead of `-bf` — the pin agreed with SCRIP's bug forever. That doc's closing line: **"Any pin
older than s189 is suspect by construction. A corpus-wide sweep for refs whose spelling can only have come
from the folding arm is worth a row."** hq_C assigned that row to seat03 directly (cross-session message),
in place of continuing `vlist-expr-alternation` (released — full detail in that row's own task file).

**Result: a full re-derivation of every `.sno`/`.ref` pair in `corpus/` (1625 pairs, excluding the
off-limits `corpus/programs/lon/`) against `sbl -bf` finds ZERO additional case-folding-arm-contaminated
pins.** The json.ref defect appears to have been an isolated incident, not a symptom of a wider pattern.

## METHOD

Per hq_C's brief, verbatim in substance: **"re-derive, then diff; do not read for plausibility."** Two
phases:

**Phase 1 — targeted, by the four folding-sensitive constructs `lib_oracle_flags.sh`/s189 name** (`DATATYPE()`,
distinct-case labels/variables, `$('ABC')` indirect reference, `output` vs `OUTPUT`):

- Every `DATA`/`RECORD` prototype declaring a mixed-or-lower-case type name, intersected with files also
  calling `DATATYPE()` (the exact json shape): 4 hits. 2 already fixed by hq_C this session
  (`programs/snobol4/demo/json.sno`, `benchmarks/snobol4/demo/json.sno`). The remaining 2 —
  `crosscheck/rung11/1115_data_basic.sno`, `crosscheck/data/096_data_datatype_check.sno` — re-derived and
  read individually: `096_data_datatype_check` matches `sbl -bf` byte-for-byte (its source explicitly
  self-normalizes with `REPLACE(DATATYPE(a),&LCASE,&UCASE)`, sidestepping the whole question by design, with
  a comment saying so); `1115_data_basic` diverges from the oracle but for an unrelated reason (`ERROR 022 --
  undefined function called` on `VALUE()`, which real SPITBOL does not implement the way this test assumes —
  its `.ref` is SCRIP's own self-consistent PASS output, not oracle-derived, and is not a folding artifact).
- Every file whose name or source comments mention case/folding explicitly (`probe/cn/cn_t1_scalar_fold.sno`,
  `cn_var_cset_fold.sno`, `probe/mv/mv_icase_reduced.sno`, `crosscheck/rung2/218_direct_goto_cond.sno`,
  `crosscheck/patterns/152_pat_json_keyvalue_renamed.sno`, `beauty_suite/case_driver.sno`,
  `beauty_suite/omega_driver.sno`): 7 files, all re-derived, all clean. Two of the `cn_*` files are
  self-documented as `ORACLE_FAIL BY CONSTRUCTION` / `SCRIP-pinned` in their own source comments (they use
  `&USER_DECLARED_CONSTANTS`, a SCRIP-only extension `sbl` errors on regardless of folding arm) — confirmed
  empirically, not just read: `sbl -bf` on both gives `ERROR 251 -- keyword operand is not name of defined
  keyword`, exactly as their own comments predict. `mv_icase_reduced.sno`'s header comment cites the
  now-outdated `sbl -b` (pre-s189) as its oracle, but its actual output is a quoted string literal
  (`'PASS: icase matches'`), never a reflected identifier name, so it is folding-invariant regardless of
  which arm minted it — verified by re-deriving under `-bf` and matching.

**Phase 2 — full sweep, automated, not sampled.** Every `.sno` with a sibling `.ref` under `corpus/`
(1625 pairs) re-run under `sbl -bf`, output diffed against the pin. Every mismatch classified: if
upper-casing BOTH the fresh oracle output and the existing pin makes them identical, that is the general,
pattern-independent signature of a folding-arm-minted pin (folding upper-cases identifiers/labels/the
special `output`/`input` keyword; it never touches a quoted string literal's contents, so this signature
cannot arise any other way). If a mismatch survives upper-casing, it is a different, out-of-scope class of
divergence.

**Iterating on the sweep's own methodology, not trusting the first pass:** the first cut fed `/dev/null` to
every program (101 apparent diffs). Many of those were programs needing a `.input` sibling that wasn't being
fed — added `.input`/`.in` detection matching `scorecard_snobol4.sh`'s own `stdin_for()` convention and
re-ran (80 genuine diffs, still 0 case-only). Four remaining ambiguous cases
(`programs/csnobol4-suite/{atn,diag1,diag2,genc}.sno`, all found via the `$()`-indirect-reference
intersection) were cross-checked against the project's own canonical `scorecard_snobol4.sh oracle` command,
per that file's own documented rule ("a census is a harness; copy run_one, never re-derive it" —
`util_ref_mint.sh`): identical RC/byte-count both ways (`EMPTY`/`RC1`/`RC1`/`RC1` respectively), confirming
these are pre-existing invocation gaps this sweep's own ad-hoc harness didn't cause and doesn't need to
solve (`atn.sno` needs something this sweep's stdin/cwd handling doesn't provide; `diag1.sno` has no `END`
statement; `diag2.sno` hits an unrelated parse error at line 232; `genc.sno` is a translator tool expecting
a command-line filename argument) — none show any relationship to case-folding.

## RESULT (v2, corrected script, self-test-verified)

```
programs-with-ref: 1628   oracle-match: 1509   CASE-ONLY-DIVERGENCE: 0   other-diff: 27   skip: 92
```

wall-clock ~70s, positive-control self-test PASSED (proves the instrument can still detect a fabricated
`root=JOBJ`-shaped fixture before this number is trusted). Every one of the 27 "other-diff" files was
individually read and diffed this time — none dismissed by category:

- **`kw_defaults.sno`, `kw_direct_read.sno` — REAL, IN-SCOPE, CONFIRMED (see next section).** Not
  case-only-text, so the automated CASE-ONLY detector correctly does not (and structurally cannot) flag
  them, but they are the SAME root defect class the row exists to find.
- **`claws5_call.sno`, `claws5_cap.sno`** (`probe/callout/`) — confirmed clean once fed
  `corpus/benchmarks/snobol4/demo/claws5.dat` (their own header comment: *"runner redirects
  `<family>.dat`"*) — manually verified matching (modulo the already-handled `iters:`/`ns:`/`ms:` lines).
  This sweep's stdin resolution intentionally does not reach across directories (a same-name `.dat` in an
  unrelated probe directory would be a worse bug than the one being chased), so these two remain in
  `other-diff` by construction, not because anything is wrong with the pin.
- **22 `programs/csnobol4-suite/*.sno`** — the historical upstream SPITBOL test-suite source (unmodified
  since `snobol4-1.4.1`). Heterogeneous, individually-read causes, none case-only: missing `END` statements,
  programs expecting a command-line filename argument (`genc.sno`), `&DUMP`-triggered variable-state dumps
  this sweep's plain invocation doesn't trigger the same way the original authors' harness did (`a.sno`,
  `dump.sno`), floating-point formatting (`float.sno`), and — the one worth naming specifically —
  `case1.sno`, which is not a simple correctness witness at all: it is an explicit, self-described test of
  historical `-case`/`-CASE`/`-case N` IN-FILE compiler directives (mid-source fold-mode toggles, a
  Catspaw-era feature, "5/25/94 -plb"), so "does a bare `sbl -bf` run match this `.ref`" is not even the
  right question to ask of it — its divergence is real but orthogonal to this row's command-line-arm
  question. Four of the 22 (`atn`, `diag1`, `diag2`, `genc`) were additionally cross-validated against the
  canonical `scorecard_snobol4.sh oracle` harness (identical RC/byte-count both ways), confirming these are
  pre-existing invocation gaps, not an artifact of this sweep's own harness.
- **`BALREV_driver.sno`** (`programs/gimpel/`) — one extra trailing blank line in the fresh oracle run vs.
  the pin, with no `.input` present (fed `/dev/null`); not further root-caused, not case-only.

None of the 27 show the case-only signature. **skip (92)** is dominated by the already-documented
`cn_*` `&USER_DECLARED_CONSTANTS` probes (self-documented `ORACLE_FAIL BY CONSTRUCTION` in their own source
comments, confirmed empirically) and other SCRIP-only-extension or already-tracked-elsewhere programs (e.g.
`demo_treebank`, seat03's own deliberate red from `vlist-expr-alternation`; the open
`json-match-capture-free-hang` timeout row) — not individually re-triaged file-by-file this session (v1's
proven blindness was in the comparison logic that ALSO gates the match/other-diff split, not in the
oracle-liveness gate reused unchanged from `scorecard_snobol4.sh`, so this bucket carries lower risk of
hiding the same defect — but it has not been given the same exhaustive treatment as other-diff and a future
session should not assume it has).

## ⭐⭐ A SECOND, REAL DEFECT — FOUND ONLY BECAUSE THE BUCKET WAS TRIAGED, NOT DISMISSED

`&CASE` — SPITBOL's OWN case-folding-mode keyword — has a DIFFERENT default value depending on which oracle
arm reads it: `sbl -b` (folding) reports `&CASE` unset-default as `1`; `sbl -bf` (the mandated arm) reports
`0`. **`probe/kw/kw_defaults.ref` and `probe/kw/kw_direct_read.ref` are both pinned to `1`** — minted under
the wrong arm, the identical defect class as `json.ref`, just manifesting as a DIGIT rather than a folded
letter, which is exactly why the automated CASE-ONLY detector (upper-case-both-sides-and-compare) cannot and
does not catch it — `"1"` upper-cased is still `"1"`. **Confirmed live: `SCRIP --run` on both witnesses
currently prints `CASE=1`/`case=1` too** — SCRIP currently agrees with the wrong-arm pin, so this is not
merely a stale ref, it is a currently-invisible SCRIP correctness defect masked by it, structurally identical
to how `json.ref` masked the `DATATYPE()` bug for months. Scope confirmed narrow: `grep -rl '&CASE'` across
the whole corpus (excluding `programs/lon/`) finds 7 files; the other 5 all set `&CASE` explicitly
(`&CASE = 0`/`&CASE = 1`) rather than reading its default, so they are unaffected. **Not fixed here** — unlike
`json.ref`, fixing this means first deciding what SCRIP's `&CASE`-read default *should* be (0, matching
`-bf`, seems clearly correct given RULES.md's blanket case-sensitivity mandate, but the runtime change and
whatever currently reads `&CASE`'s default internally is unscoped by this row) and then re-minting both refs
— proposed as its own follow-up row, per the same split hq_C already used for `vlist-expr-alternation`'s
Defect B, rather than force it through here without a ruling.

## THE METHODOLOGY ARTIFACT WAS NOT A FOOTNOTE, IT WAS v1's ROOT CAUSE

The original version of this doc noted, as an aside, that `corpus/programs/snobol4/demo/json.sno` prints an
extra trailing `match_ms=0` line on stderr that the pinned `.ref` (stdout only) doesn't have, and moved on.
**That line is the entire reason v1 of this sweep was blind.** hq_C's negative-control catch traced it
exactly there. Left as a lesson: a "huh, minor, unrelated" observation during a sweep is sometimes the whole
bug in the sweep itself — worth a second look before filing it as a footnote, especially when it touches the
comparison mechanism rather than the thing being compared.

## WHAT WOULD REOPEN THIS ROW

`scripts/util_sweep_fold_arm_refs.sh` (v2, this session) packages the corrected method, runs a mandatory
positive-control self-test before reporting anything, and is the row's own DONE-WHEN
(`pre-s189-ref-sweep.task.md`). Re-run it after any future `.ref` mint/update; a nonzero
CASE-ONLY-DIVERGENCE count is new work, and so is the self-test failing outright (the instrument itself is
broken again). Investigate each hit with its own witness (which arm minted the old pin, re-derive from
`-bf`, diff), never blanket-overwrite. The `&CASE` finding above is also unresolved and worth its own row.

## RECEIPTS

SCRIP (this session's commits add `scripts/util_sweep_fold_arm_refs.sh`, both v1 and the v2 correction, on
top of `a0ebc660`), corpus unmodified by this row — zero `.ref` files changed, zero fixes applied. Oracle:
`/home/resources/x64/bin/sbl -bf -d512m -i64m` throughout (the ONE correctness arm, `lib_oracle_flags.sh`),
matching `scorecard_snobol4.sh`'s own `sbl_flags()`. `corpus/programs/lon/` excluded by construction in the
sweep script itself (`-not -path "$CORPUS/programs/lon/*"`), never walked, never read into this transcript
or any output file. v1's false-clean result (1625/1457/**0**/74/94) and v2's corrected, self-test-verified
result (1628/1509/**0**/27/92) are both in this doc's history on purpose — the retraction is the evidence.
`util_sweep_fold_arm_refs.sh` is re-runnable by anyone to reproduce the v2 result and its own self-test.
