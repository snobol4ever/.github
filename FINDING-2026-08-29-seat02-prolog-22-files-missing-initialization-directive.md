# FINDING — the "~50 externally-blocked" prolog backlog was never fully re-swept: 22 of 56 sampled files are neither PZ-4 nor halt-unimplemented, they're missing their entry-point directive

**seat02 · 2026-08-29 · row `tests-consolidate-prolog`**

## What this corrects

seat09's 2026-08-29T12:20Z `## NEXT` block flagged a standing suspicion: their 19-of-25 discovery
(files believed "externally blocked" that were actually just never oracle-tested against the
current gate's full file list) might generalize to some fraction of the remaining ~50-file bucket,
but a systematic re-sweep of the rest was "not attempted."

This session ran that re-sweep. Of the 67 loose-but-undeclared files, 56 were not already
individually characterized (excludes `coverage_net_gaps.pl`/`queens.pl`/`sentences.pl` [PZ-4],
`rung50_between_enum/for_alias`, `rung66_current_stream`, `rung72_unget`, `rung73_display`,
`rung75_number_atom` [wrong-answer, already filed], `rung11_findall_findall_basic` [excluded,
hardcoded A/B-witness dependency], `rung22_write_canonical_write_canonical_list` [wrong-answer,
already filed]).

**Screened all 56 for a clean `scrip --run` (rc=0, no crash/hang, 8s timeout):**
- **33 crash** (rc=132/134/139) — this corroborates the PZ-4 characterization for these specifically;
  no correction needed for this subset. (Includes `rung56_ite_backtrack/rung56.pl` and
  `rung57_forall/rung57.pl`, both referenced elsewhere in this task's ledger as PZ-4-shaped but not
  previously listed by name in the "item 1" bucket description.)
- **23 ran cleanly to rc=0.** Ran all 23 through `corpus_suite_harness.py capture-oracle-refs --lang
  prolog --modes m3,m4` (staged via symlinks first, never pointed at the live tree until reviewed):
  **1 GREEN** (`rung02_facts_facts.pl` — converted this session, spot-checked byte-identical to its
  pre-existing `.expected`), **22 RED** — but not from a crash and not (as far as tested) from
  `prolog-halt-unimplemented-error22`.

## The 22 share exactly one root cause, confirmed directly, not inferred

None of the 22 has a `:- initialization(main).` (or any other main-invoking directive) — verified
by `grep -c 'initialization(main' <file>` across all 22, every count is 0. Every other correctly-formed
`.pl` file in this tree (checked `rung06_lists_lists.pl` and others converted this task) opens with
exactly that directive. Under `swipl -q -g halt file.pl` (this harness's standing oracle invocation),
loading a file with no such directive runs zero goals — `main/0` gets defined but never called, so the
real oracle's output is **empty**. SCRIP's `--run`/`--compile` invoke `main/0` regardless of whether a
directive requested it. Manually confirmed on `rung13_assertz_assertz_atom.pl`: scrip prints
`red\ngreen\nblue`, `swipl -q -g halt` prints nothing.

This is a structural scrip-vs-oracle disagreement about entry-point invocation on directive-less
files, not 22 separate wrong-answer bugs in 22 different features — every file in the cluster fails
for the identical reason. The 22, by feature family:
- `rung13_assertz_asserta_order`, `rung13_assertz_assertz_atom`, `rung13_assertz_assertz_compound`,
  `rung13_assertz_static_dynamic_mix` (4)
- `rung14_retract_retract_all`, `rung14_retract_retract_basic`, `rung14_retract_retract_mixed` (3)
- `rung15_abolish_abolish_existing`, `rung15_abolish_abolish_one_of_two`,
  `rung15_abolish_abolish_then_query_fail`, `rung15_abolish_abolish_then_reassert` (4)
- `rung44_setof_bagof_order`, `rung44_setof_basic`, `rung44_setof_caret`, `rung44_setof_empty_fail`,
  `rung44_setof_group` (5)
- `rung45_reflect_clause_facts`, `rung45_reflect_clause_findall`, `rung45_reflect_clause_nonexistent`,
  `rung45_reflect_current_predicate`, `rung45_reflect_predicate_property` (5)
- `rung83_write_family_metacall` (1)

## Addendum: all 22 have a pre-existing `.expected` sidecar, and most are self-pinned to scrip's own output

Checked (not skipped, unlike my first pass at this file): every one of the 22 has a loose `.expected`
sidecar. Compared each against a **fresh current-build** `scrip --run` (not the oracle — scrip's own
output), newline-insensitive:

- **16/22 match scrip's current output exactly** — `rung13_assertz_asserta_order/assertz_atom/
  assertz_compound/static_dynamic_mix`, `rung14_retract_retract_all`,
  `rung15_abolish_abolish_existing/one_of_two/then_query_fail`, `rung44_setof_bagof_order/basic/
  caret/empty_fail`, `rung45_reflect_clause_nonexistent/current_predicate/predicate_property`,
  `rung83_write_family_metacall`. This is the same self-pinned-`.expected` anti-pattern seat16 found
  on `rung22_write_canonical_write_canonical_list` (a reference baked from the tool under test, not
  the oracle) — here confirmed across 16 files at once, not a one-off.
- **6/22 diverge even from their own `.expected` under today's build**: `rung14_retract_retract_basic`,
  `rung14_retract_retract_mixed`, `rung15_abolish_abolish_then_reassert`, `rung44_setof_group`,
  `rung45_reflect_clause_facts`, `rung45_reflect_clause_findall`. Two readings, not distinguished this
  session: either these were also self-pinned at authoring time and scrip's retract/abolish/setof-
  with-multiple-solutions/clause-reflection behavior has since drifted, or they carry a second,
  independent bug on top of the missing-directive issue. Not root-caused — a proper ASM-diff
  investigation, out of this row's lane.

## Disposition this session

Left all 22 loose, **not KEEP.md'd** — this isn't a permanent design exclusion, and I'm not certain
which side of the disagreement is "wrong": adding the missing directive to these 22 corpus files
would make them match every sibling's convention and (mechanically) become convertible via the exact
same `capture-oracle-refs` pipeline just proven this session on `rung02_facts_facts` — but that
changes what each witness asserts as correct behavior, which reads as a content-authorship call
above this row's pay grade, not a conversion-formatting one. Equally plausible: scrip's auto-invoke of
`main/0` without a directive is the thing worth questioning. Not fixed either way — flagging the
class and its exact mechanism for a ruling.

## Not attempted

- Did not check whether scrip's Prolog frontend/ARCH docs document the auto-invoke-`main`-without-
  directive behavior as intentional.
- Did not root-cause the 6 files whose `.expected` diverges even from current scrip output (see
  addendum above) — that needs an ASM diff, not a conversion-row-level check.
- Did not re-verify the remaining ~33 PZ-4-signature crashes individually beyond the rc-code screen —
  their existing characterization stands uncorrected here.
