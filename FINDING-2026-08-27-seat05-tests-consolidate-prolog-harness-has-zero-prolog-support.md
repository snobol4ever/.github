# FINDING 2026-08-27 seat05 — `tests-consolidate-prolog`: blocked before the correctness question even matters — the harness has zero Prolog support

**Date:** 2026-08-27 · **Seat:** seat05 (FLEET-16) · Zero source/corpus edits.

Quick, decisive check before investing in the deeper correctness question this row's own coordination note (seat08, same task file) already raised: `corpus_suite_harness.py`'s `LANG_CONFIGS` table (line 76) contains exactly one entry — `raku`. There is no Prolog config, no `.pl` extension mapping, no grading-mode wiring. Neither `convert` (format A, SNOBOL4-specific statement-join logic, per the harness's own docstring) nor `convert-blocks` (format B, needs a `LANG_CONFIGS` entry) can run against `tests/prolog` today. This is independent of, and more immediately dispositive than, the correctness concerns already on record:

- `prolog-next.task.md` (the Prolog dev-cursor row) is **still `state: PARKED`**, checked directly — the "very likely stale" characterization in the parent row's own investigation was speculative; the park header is current as of this check.
- `prolog-parser-corpus-vacuous-gate-422-files.task.md` (the row tracking `test_corpus_prolog_parser.sh`'s false-PASS-on-422-empty-files bug) is **still `state: FREE`** — unaddressed, not fixed since the parent row's own prior investigation found it.

**Net: even setting the vacuous gate and the park status aside, there is no tool capable of performing this row's conversion today.** Building Prolog `LANG_CONFIGS` support (extension, comment syntax for a banner if format B applies, and a grading mode — Prolog has no `--dump-ast` equivalent confirmed to exist, not checked further here) is real harness-development work, the same class as the Raku generalization seat08 already built, not a byproduct of converting one family.

**Not attempting anything.** Releasing — this needs harness work before it needs a scope ruling, and Prolog's own correctness state needs resolving independently either way (not this row's job). Consistent with, and reusing, seat08's own prior investigation in the parent row rather than re-deriving it.
