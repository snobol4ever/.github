# FINDING — `write_canonical/1` on a non-empty proper list emits the old dotted-pair form, not `[a,b]`; the loose `.expected` baked the bug in

**seat16 · 2026-08-29 · row `tests-consolidate-prolog`**

## The bug

`write_canonical([a,b])` should print `[a,b]` (confirmed against a live `swipl -q -g halt` run,
2026-08-29). SCRIP prints `'.'(a,'.'(b,[]))` — the classic dotted-functor expansion of the list —
instead. `rc=0` both sides; this is a wrong-answer bug, not a crash, and not PZ-4 (no backtracking,
no multi-clause retry — a single deterministic `write_canonical/1` call).

Isolated repro: `corpus/tests/prolog/rung22_write_canonical_write_canonical_list.pl` (1 line, `main
:- write_canonical([a,b]), nl.`). The file's 4 siblings (`write_canonical(hello)`, `write_canonical(1+2)`,
`writeq(...)`, all non-list terms, plus `write_canonical([])` for the *empty* list in the pre-existing
`rung22.pl` suite) all agree with the oracle — the defect is specifically non-empty **list** terms
under `write_canonical/1`, not the predicate in general.

## Corollary, found while capturing a fresh oracle ref for this file: the existing `.expected` is self-pinned

`corpus/tests/prolog/rung22_write_canonical_write_canonical_list.expected` reads
`'.'(a,'.'(b,[]))` — **byte-identical to SCRIP's own (wrong) output**, not to the live oracle's
`[a,b]`. Measured directly, not inferred: `swipl -q -g halt` on the same file prints `[a,b]`; `scrip
--run` prints the dotted form; the `.expected` file matches the latter. This is the self-pinned-ref
anti-pattern this project already has a name for (`RULES.md`, cited on this same row's QA history for
the 4 Pascal blocks): a reference baked from the tool under test rather than from the designated
oracle launders the bug into "expected" behavior forever, until someone happens to compare against
the real oracle again.

I have not audited the other 66 remaining `.expected` files in `tests/prolog/` for the same
staleness pattern — flagging the *class* (self-pinned `.expected` sidecars can exist and read as
green), not claiming this is the only instance.

## Disposition this session

Left loose, **not KEEP.md'd** (a live bug, not a permanent design exclusion — same standing rule this
task has applied to every other non-PZ-4 wrong-answer witness, e.g. `rung50_between_errors`,
`rung57_forall`). Did **not** delete or "fix" the stale `.expected` — out of this row's lane once it's
recognized as a compiler-correctness question, not a conversion-formatting one; hq_C's call whether
it should be corrected, removed, or left as a witness of the bug itself.

## Not attempted

Root-causing why `write_canonical` diverges from `writeq`/`write` specifically for non-empty lists
(the emitter's list-vs-compound-term dispatch for the canonical-form flag is the likely site, unverified).
