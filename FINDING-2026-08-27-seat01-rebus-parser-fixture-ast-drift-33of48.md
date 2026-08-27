# FINDING 2026-08-27/28 seat01 — Rebus `parser/` AST-dump oracles have drifted from current `--dump-ast` output on 33 of 48 gradeable fixtures; same class already found in Snocone and Icon

## Context
Working `tests-consolidate-rebus` (fan-out child of `corpus-suites-consolidation`). `corpus/tests/rebus/parser/` holds 96 `.reb` files, 48 with a committed `.ref` (the other 48 have no oracle at all — never in scope for grading either way). Before converting anything, ran an independent, unpiped sweep of all 48 pairs via `scrip --dump-ast`, diffed against the committed `.ref` (same discipline as `FINDING-2026-08-27-seat08-parser-fixture-ast-oracles-drifted-...md`, which found the identical pattern in Snocone `parser-fixtures/` 59/67 red and Icon `parser/` 153/153 red — this is now a third language showing the same shape).

## What was found
**PASS=15, FAIL=33.** Sample (`fib.reb`):
```
committed .ref:  (STMT :subj (TT_NUL) :goS rb_2 :goF rb_3)
                 (STMT :lbl rb_2)
                 (STMT :subj (TT_FNC LE (TT_VAR N) (TT_ILIT 1)))
                 (STMT :go rb_4)
current --dump-ast: (STMT :subj (TT_FNC LE (TT_VAR N) (TT_ILIT 1)) :goS rb_2 :goF rb_3)
                    (STMT :lbl rb_2)
                    (STMT :eq :subj (TT_VAR FIB) :repl (TT_VAR N))
```
The condition test and its `:goS`/`:goF` fields now fold onto one STMT node instead of splitting across a `TT_NUL` placeholder plus a separate condition statement. The program still **runs correctly** (`./scrip --run fib.reb` prints `13`, the right answer) — this is an AST *shape* change, not a correctness regression in execution. One systematic node-shape simplification plausibly explains a cluster this size (consistent with the Snocone/Icon precedent, where one shape change also explained a uniform-looking cluster), but this is not fixture-by-fixture confirmed, and deciding whether the new shape is the compiler's correct current intent (regen the 33 stale `.ref`s) or a regression (something to fix in the compiler) is a correctness call this row has no standing to make unilaterally.

Full list of the 33 failing stems is recorded with the same reason in `corpus/tests/rebus/parser/KEEP.md`.

## What was done about it (in scope for this row)
Passed the 33 as `--skip`/`--skip-reason` to `corpus_suite_harness.py convert-blocks`, converted the 15 clean pairs into `corpus/tests/rebus/parser.reb`/`.ref`, added a `rebus` entry to `LANG_CONFIGS` (mirroring raku's, validated against a real sample first per the table's own docstring rule), wrote `scripts/test_rebus_parser_fixtures.sh`. Did **not** touch the compiler or regenerate any `.ref`. Pushed: SCRIP `94b5b7b5`, corpus `34994da2`.

## Not attempted / left open
- Root-causing which AST shape (old `.ref` vs current `--dump-ast`) is correct — same open question as the Snocone/Icon finding, arguably now the same underlying triage since it may be one general parser/lowering-shape change hitting all three languages' fixture ladders rather than three independent drifts. Worth checking by whoever owns that triage.
- The 48 no-`.ref` stems — need an oracle written before they can be graded at all (same disposition as raku's 50 no-ref `parser/` files).
- `corpus/tests/rebus/*.reb` (3 top-level files, not the parser ladder) are separately tracked and broken: `rebus-corpus-100pct-broken.task.md`.

## Secondary, gate-tooling finding (affects all six `tests-consolidate-*` rows, not just this one)
`scripts/test_gate_suite_conversion_complete.sh <lang>` (SCRIP `75310d6a`, the new shared DONE-WHEN authority) globs every `*.<ext>` file under `tests/<lang>/` except under `crosscheck/`. For the format-(B) languages (raku, rebus), the suite output itself lands as `tests/<lang>/<family>.<ext>` — same extension, not under `crosscheck/` — so it is not automatically exempted and must also appear as a substring somewhere in a `KEEP.md`, or the gate reports it as an undeclared loose file. Confirmed this is pre-existing and general, not specific to this row's work: `bash scripts/test_gate_suite_conversion_complete.sh raku` currently reports 104 undeclared loose files against the already-converted raku row too. In this row's case it resolved by accident (the suite filename happens to appear as a substring inside `tests/rebus/parser/KEEP.md`'s own explanatory prose), which is not a reliable mechanism. Worth a deliberate decision from whoever owns the gate: exempt top-level `<family>.<ext>` suite files the same way `crosscheck/` is exempted, or require them declared on purpose rather than by prose accident.
