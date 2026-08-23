# FINDING 2026-08-23 (seat03) — row `pre-s189-ref-sweep`: full-corpus sweep for folding-arm-contaminated `.ref` pins, ZERO found beyond the one hq_C already fixed

## HEADLINE

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

## RESULT

```
programs-with-ref: 1625   oracle-match: 1457   CASE-ONLY-DIVERGENCE: 0   other-diff: 74   skip: 94
```

wall-clock 27s. The 74 "other-diff" and 94 "skip" files are NOT folding-arm artifacts (verified: none match
the upper-case-both-sides-and-compare test) — they are a mix of already-tracked defects (e.g.
`demo_treebank`, seat03's own deliberate red from `vlist-expr-alternation`; the open
`json-match-capture-free-hang` timeout row), self-documented SCRIP-only extensions (`cn_*`
`&USER_DECLARED_CONSTANTS` probes), and historical csnobol4-suite programs with invocation requirements
(argv, multi-file assembly) beyond a simple stdin-fed single-file run. None were individually fixed or
changed here — per the brief's own instruction, a `.ref` may legitimately record behaviour `sbl` itself
fails on, and this sweep's job was to find the ONE specific signature (case-only divergence), not to
triage every pre-existing divergence in the corpus.

## METHODOLOGY ARTIFACT LEFT FOR WHOEVER TOUCHES THIS NEXT

`corpus/programs/snobol4/demo/json.sno` (already fixed) shows exactly one line of drift against a bare
`sbl -bf` re-derivation: an extra trailing `match_ms=0` line the pinned `.ref` doesn't have. Not a folding
issue (confirmed: it's an extra line, not a case change, and disappears from the "other-diff" bucket's
concern once you notice it's timing instrumentation) — flagged here rather than chased, since it's outside
this row's scope and the file's correctness (the part hq_C's row cured) is otherwise confirmed intact.

## WHAT WOULD REOPEN THIS ROW

`scripts/util_sweep_fold_arm_refs.sh` (new, this session) packages the Phase 2 method and is the row's own
DONE-WHEN (`pre-s189-ref-sweep.task.md`). Re-run it after any future `.ref` mint/update; a nonzero
CASE-ONLY-DIVERGENCE count is new work — investigate each hit with its own witness (which arm minted the
old pin, re-derive from `-bf`, diff), never blanket-overwrite.

## RECEIPTS

SCRIP `a0ebc660` (this session's own commit adds `scripts/util_sweep_fold_arm_refs.sh` on top), corpus
`90dbbb895` (unmodified by this row — zero `.ref` files changed). Oracle: `/home/resources/x64/bin/sbl -bf
-d512m -i64m` throughout (the ONE correctness arm, `lib_oracle_flags.sh`), matching
`scorecard_snobol4.sh`'s own `sbl_flags()`. `corpus/programs/lon/` excluded by construction in the sweep
script itself (`-not -path "$CORPUS/programs/lon/*"`), never walked, never read into this transcript or any
output file. Full sweep output + the four cross-validation runs against `scorecard_snobol4.sh oracle`
captured this session; `util_sweep_fold_arm_refs.sh` is re-runnable by anyone to reproduce the 1625/1457/
0/74/94 result.
