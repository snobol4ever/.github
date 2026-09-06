# swi_tests refs are re-cut from real swipl — the old "82/114 PASS" was mostly EMPTY matching EMPTY, not conformance

**seat12 (hq_T) · 2026-09-06 · row `prolog-swi-tests-refs-were-cut-through-a-shim-the-oracle-cannot-load-so-most-expected-verdicts-are-no-tests-ran` (rank 0)**
**Tree: SCRIP `b08893799` · corpus `b06b6ecd6` · .github `0183699c` + this landing · RT_OPT=`-O0` · incremental `make`**

## 1. The premise, confirmed before touching anything

`corpus/packages/prolog/swi_tests/*.ref` (9 files, 57 lines) were cut by running real swipl through our own
`corpus/tests/prolog/plunit.pl` shim. Real swipl refuses to load that shim: it will not let a user file redefine
its own system `set_prolog_flag/2` / `current_prolog_flag/2`. 51 of 57 lines read `EMPTY`. The task's own
DONE-WHEN, run as-is before any change: `EMPTY=51 of 57 lines`, `RED: test_list.ref demands FAIL memberchk for
a test real swipl PASSES`, exit 1 — reproduced exactly as the baton described it.

ceo ruling (routed into the baton by hq_C before clearing the message): re-cut from real swipl running its
**own** `library(plunit)`, never our shim — "the oracle is swipl, never our shim." hq_T (this row) owns the
denominator/census lane; the SCRIP-side runner arm belongs to hq_C and is untouched here.

## 2. Method — identity-keyed, not positional

`SCRIP/scripts/util_swi_cut_refs.sh` (new, committed). For each file, unit names come from `grep
'^:- begin_tests('` in the **source** (identity, not the old ref's line order). Each `(file, unit)` pair runs
in its **own** swipl subprocess: consult the file, `run_tests([Unit])`, then read the verdict from plunit's own
bookkeeping — `plunit:test_summary(Unit, Summary)` (the `passed`/`failed`/`failed_assertions`/`blocked`/`sto`
dynamic facts plunit itself asserts), applying the **identical** branching plunit's own `report/0` uses
(`/usr/lib/swi-prolog/library/plunit.pl` ~line 1345): all-zero → `EMPTY`, zero failures → `PASS`, else `FAIL`.
This was deliberate: under `-q`, plunit prints only unlabelled dots per test with no unit name attached, so
scraping dot-line positions back to a unit name is exactly the position-keyed-extraction class RULES.md's
INSTRUMENT LAWS forbid — a sibling unit's dots could not be told apart from the one under test. Reading
plunit's own per-unit facts sidesteps that entirely.

## 3. Two things the re-cut surfaced that are named here, not fixed here

**(a) Real SWI-Prolog 9.0.4 itself SIGABRTs** running `test_string.pl`'s `string` unit: a C-level assertion
failure in `modify_case_atom___LD` (`Assertion failed: c <= 0xff`), reached from `string_upper/2` via
`plunit_string:unit body/2`. Reproduced twice, isolated to that one unit (the sibling `string_bytes` unit runs
fine in its own process). `test_string.ref` records this unit as `EMPTY` because no verdict is available — but
this is **not** the legitimate "conforming loader genuinely runs zero tests" EMPTY the ceo ruling describes for
the other 51; it is an oracle crash. Flagging so nobody folds it into that population without noting the
difference. Not investigated further (a swipl/oracle-environment question, not a SCRIP one).

**(b) `test_dcg.pl` declares a 6th unit, `phrase`, that had no `.ref` line at all** (only 5 of 6 `begin_tests`
blocks were ever given a line). Added; real swipl reports `FAIL phrase`.

## 4. New census

| file | old (shim-cut) | new (real swipl, isolated per unit) |
|---|---|---|
| test_arith | 26× EMPTY | 24 PASS, 2 FAIL (`float_compare`, `max_integer_size`) |
| test_bips | 6× EMPTY | 5 PASS, 1 EMPTY (`bips_occurs_check_error` — legitimately gated off, unchanged) |
| test_call | 9× EMPTY | 8 PASS, 1 FAIL (`catch`) |
| test_dcg | 5× EMPTY | 5 PASS, 1 FAIL (`phrase`, new line) |
| test_exception | 2× FAIL | 2 PASS |
| test_list | 1× FAIL | 1 PASS |
| test_misc | 1× FAIL | 1 PASS |
| test_string | 1 FAIL, 1 PASS | 1 EMPTY (oracle crash, §3a), 1 PASS (unchanged) |
| test_term | 5× EMPTY | 4 PASS, 1 FAIL (`variant`) |
| **total** | 57 lines: 8 FAIL, 49 EMPTY | 58 lines: **51 PASS, 5 FAIL, 2 EMPTY** |

Task DONE-WHEN re-run after the fix: `EMPTY=2 of 58 lines`, `GREEN: the test_list witness ref no longer
contradicts the oracle`, exit 0.

The 5 new FAILs are real swipl verdicts surfacing for the first time and are **not diagnosed here** — that is
the parent row's job (`prolog-swi-tests-114-to-100-percent-both-modes-by-class`, which stays parked and must
re-derive its DONE-WHEN against these corrected refs, not the old ones).

## 5. SCORE.md impact — the number moved, and moved for the right reason

Before (measured 2026-09-02 against the broken refs, SCRIP `c6190d9e`): **m3 82/114 (71%) · m4 0/114**.

After (measured 2026-09-06 against the corrected refs, SCRIP `b08893799`): **m3 PASS=2/116 · m4 PASS=2/116**
(`test_list` only — the one file whose single trivial unit, `memberchk`, SCRIP already runs end-to-end through
the shim; every other file's raw SCRIP output is currently empty).

**This is not a new regression, and it is not caused by anything committed here.** The old 82/114 was inflated
because the broken refs said `EMPTY` for 51 lines, and SCRIP's own shim-based execution *also* produced `EMPTY`
for most of those lines (for unrelated, un-investigated reasons of its own) — two wrongs matching each other
and being counted as 51 "passes." Now that the refs correctly say `PASS` (because real swipl passes), SCRIP's
actual current raw output — empty for 8 of 9 files — no longer coincidentally matches, and the suite reports
what was already true about SCRIP's present coverage of this package. **Root-causing SCRIP's near-empty raw
output is out of hq_T's lane** (src/-side; hq_C/hq_R own it) and is not attempted here. It is plausibly
explained by the in-flight Prolog rung-0 rebuild, whose master board is explicitly ruled a REPORTED number, not
a landing gate, until rung 10 (RULES.md § THE PROLOG REBUILD GATE) — stated as a plausible explanation, not
re-verified against the current rung.

SCORE.md's `vendor`/`SWI` cell landed via `util_score_row.py write` from `test_prolog_swi_suite.sh`'s own
printed line (its sanctioned path — no hand-typed number). The separate detail row (`test_prolog_swi_suite.sh
(...)`, further down the file) is hand-annotated here as superseded, old text kept verbatim as provenance per
this file's own convention — its four named SCRIP defect classes are not re-verified against the current tree
and should not be cited as current without doing so.

## 6. What's committed

- **corpus** `b06b6ecd6`: 9 `.ref` files re-cut.
- **SCRIP** `b08893799`: `scripts/util_swi_cut_refs.sh` (new, reusable) — ceo's fleet-wide generalisation
  applies beyond this suite: *"a suite stuck at zero cannot tell you its oracle is broken... every shim-cut
  suite gets the same question."*
- **.github** (this landing): this FINDING, the task baton's `## LEDGER`/`## NEXT`, and the two SCORE.md cells
  named in §5.
