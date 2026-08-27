# FINDING 2026-08-27 seat05 — `tests-consolidate-snocone`: same harness gap as Prolog, plus Snocone correctness is independently confirmed in flux today

**Date:** 2026-08-27 · **Seat:** seat05 (FLEET-16) · Zero source/corpus edits.

Same decisive check as `tests-consolidate-prolog` (see that FINDING): `corpus_suite_harness.py`'s `LANG_CONFIGS` has exactly one entry (`raku`) — no `.sc`/Snocone support exists in either `convert` (SNOBOL4-specific) or `convert-blocks` (needs a `LANG_CONFIGS` entry). Conversion is not technically possible today.

Independent of that, the parent row's own ledger (`corpus-suites-consolidation.task.md`) already found, this same day, that Snocone's file *content* is actively unstable — three separate reasons, not one:
1. **AST-oracle drift**: seat08's own investigation found `tests/snocone/parser-fixtures/` (67 pairs) at PASS=8/FAIL=59 against its pinned `.ref` goldens — the compiler's AST shape moved (`TT_ASSIGN`-wrapping) and the fixtures never got re-pinned. Byte-equal-or-no-delete would refuse 59 of 67 as unconvertible anyway (needs a green original), and deciding whether to re-pin the oracle or fix the compiler is explicitly flagged as "a correctness call this row has no standing to make unilaterally."
2. **Two more, independent, same-day Snocone correctness findings** on the *separate* rung-ladder crosscheck corpus (not `parser-fixtures/`): `FINDING-2026-08-27-seat09-snocone-crosscheck-runner-rewired-...` (52 real parser gaps surfaced after fixing a dead-flag runner) and `FINDING-2026-08-27-seat07-snocone-crosscheck-35-remaining-fails-classified-...`, which headlines a freshly-discovered severe bug: basic `while`/`for` loops not iterating past the first pass.
3. Seat08's own conclusion, verbatim in substance: Snocone correctness is "unusually actively in flux TODAY across two unrelated corpora — a second, independent reason (beyond the parser-fixtures drift itself) not to touch Snocone's file *format* right now."

**Not re-investigating what seat08 already covered thoroughly — citing it.** The harness gap alone is sufficient to block this row; the correctness churn is a second, independent reason not to rush a fix even once the harness gap closes. Not attempting anything. Releasing.
