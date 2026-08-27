# FINDING 2026-08-27 seat16 — canonical sweep script nominated; corpus suites path was a double-move, not a defect

## Context
`audit-corpus-what-is-ungated` task (postoffice/tasks/), STEP 3: hq_C's s272 §4 ruling delegated nomination of ONE canonical full-crosscheck-sweep script from 9 candidates to seat16, pre-authorizing ratification ("hq_C ratifies on sight").

## What was done
1. Located the 9 candidates via `FINDING-2026-08-23-seat16-corpus-coverage-audit-part2-harness-inventory-and-execution-triage.md` Part 1 (not `legacy-dash-flags-dead-scripts`, which the task file's pre-existing STEP 3 text pointed to imprecisely — that task covers a related-but-distinct legacy-flag problem).
2. Scored all 9 against hq_C's 4 criteria (refuses rc=2 on missing corpus / recurses / names MISSING explicitly / sources `lib_oracle_flags.sh`).
3. **Nominee: `test_corpus_snobol4.sh`** — clean pass on criteria 1 and 3 (explicit `[ ! -d "$CORPUS" ] -> exit 2`, named `MISSING_LIST`, final `exit 2` on any unresolved path). Criterion 4 is VACUOUS for this population: none of the 9 invoke `sbl` at runtime, all diff pre-baked `.ref` files; hq_C's "43 sbl callers, 4 correct" figure describes a disjoint population and does not apply here.
4. **CORRECTION to the ruling's literal scope**: "retire the other 8 by deletion" does not survive contact with what the 8 actually are. 5 of them are distinct tools by design, not sweep-gate competitors: `ab_board_sweep.sh` (A/B env-arm capture), `rtcc_board_sweep.sh` (RTCC attribution), `census_r12.sh` (register census, not a correctness tool), `test_mode34_parity.sh` (per-file m3/m4 divergence detail at finer grain), `test_smoke_snobol4_run.sh` (deliberately mode-4-only, matches CLAUDE.md's own `test_smoke_*` taxonomy by design). Only 3 are genuinely subsumed with zero unique value: `test_broad_corpus_snobol4.sh`, `test_crosscheck_snobol4.sh`, `test_regression_full_corpus.sh`. The third required its own check — its only distinguishing content (CSNOBOL4 Budne suite + FENCE crosscheck) is independently covered by `test_csnobol4_budne_suite.sh` and by `test_corpus_snobol4.sh` itself (confirmed by direct grep, not assumed).
5. Checked all 3 deletion candidates for dangling live-script references before touching anything: zero live calls found (one comment-only mention in `board_denominators.sh`; everything else is historical `.github/FINDING-*`/`GOAL-*` prose).
6. Deleted the 3, committed and pushed as `LCherryholmes <lcherryh@yahoo.com>`: SCRIP `186fbfe6`.

## The false alarm, and why it was a false alarm
Re-proving the gate post-push (a concurrent unrelated commit landed via `git pull --rebase`), `test_corpus_snobol4.sh` returned `GATE REFUSES (rc=2)`: line 121's `SUITES="$CORPUS/tests/snobol4"` didn't resolve `crosscheck/patterns` or `crosscheck/strings` against this checkout's corpus HEAD (`d671a2170`), which put those families under `corpus/suites/crosscheck/`.

Did not edit line 121 to match — flagged it to hq_C instead, non-blocking, and stopped there. hq_P (s274) confirmed why the refusal didn't reproduce on a fresher checkout: it was a **double move**. The consolidation first landed the families at `corpus/suites/crosscheck/` (this checkout's state, `d671a2170`); a LATER commit re-homed them again to `corpus/tests/snobol4/crosscheck/`, and the runner (line 121) was already updated to match the *second* move. `d671a2170` is confirmed an ancestor of current origin, not a divergent commit — this checkout was simply one step stale. hq_P re-ran the gate on a fresh checkout: `m3 PASS=365 FAIL=0, m4 PASS=365 FAIL=0 SKIP=0, MISSING=0, rc=0` — green.

**hq_P's point, worth preserving**: had line 121 been edited to match the stale tree instead of flagged, that edit would have silently broken the gate for everyone on current origin, and looked like a fix rather than a regression. Refuse-not-repair on an unexplained gate refusal, re-verify the checkout before touching the runner, is the standing rule this class of incident teaches. This specific path has moved three times in three days — no doc, this one included, should hardcode it; `grep -n SUITES= scripts/test_corpus_snobol4.sh` is the one-liner that can't go stale.

## Disposition
STEP 3 closed. Row `audit-corpus-what-is-ungated` remains open (row-factory task, no computable DONE-WHEN by design) — left FREE per every prior pass's convention.

## Session note
FLEET-8 stand-down (CEO, 2026-08-27, seats 09-16) landed immediately after this work closed. No further row picked up this session per that order.
