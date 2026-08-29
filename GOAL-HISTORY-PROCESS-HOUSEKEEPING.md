# GOAL-HISTORY-PROCESS-HOUSEKEEPING.md — closed rename, dead-parser-removal, and session-convention work

This is a consolidated historical record, not a live design doc — **nothing in this file describes an open
task.** It replaces four separate `GOAL-*.md` files, all now deleted, whose entire subject was a one-time
process or infrastructure initiative that finished and is no longer tracked anywhere else. Unlike the
`GOAL-HISTORY-INTERP-CHUNKS-BROKER.md` cluster (dead execution *architectures*), nothing here was ever about
how SNOBOL4/Icon/Prolog programs run — these are org/build/parser housekeeping closures. See RETIRED NAMES at
the end for the old→new mapping every stale cross-reference should resolve through.

Landed via `goal-files-major-consolidation` (task file, `/home/resources/postoffice/tasks/`), executing Lon's
2026-08-28 ruling steps (1)/(3) — grade against live source, consolidate by clustering. All four files carried
a clean, unanimous **HISTORICAL-CLOSED / safe-to-fold** verdict from the survey phase with no reserved question
attached; this landing independently re-ran the load-bearing checks rather than trusting the survey blind
(file existence, binary/symbol checks, a fresh commit-ancestry check on each cited hash) before folding.
`GOAL-DEAD-CODE-SWEEP.md`, part of the same "confidently-historical singles" shortlist the prior NEXT block
named, was deliberately **left out of this landing**: its own survey verdict called for one live re-check
before folding (`util_gc_dead_oracle.sh` re-run, count at the 18 backend-KEEP floor), and running that check
fresh here found the oracle script itself currently fails to relink (`undefined reference to rt_outer_call`,
`g_gva_active`, `bbprof_report`, `bin_audit_print` — a `--gc-sections` link-time gap, unrelated to whether dead
code actually remains). That failure is orthogonal to this file's cluster and is left for whoever owns
`GOAL-DEAD-CODE-SWEEP.md` next, noted in the task file's own ledger rather than silently retried into a
guessed verdict here.

## The one4all → SCRIP rename

- **`GOAL-SCRIP-RENAME.md`** (was: 136 ln) — carved 2026-05-30 after Lon's directive to eradicate the `one4all`
  name (the product's former private-repo identity, since deleted) in favor of the public `SCRIP` org repo.
  Seven gated rungs (RN-1 through RN-7), all checked off: build/test scripts, source, docs, `.github`
  operational docs, two literal file renames (`REPO-one4all.md`→`REPO-SCRIP.md`,
  `GOAL-README-ONE4ALL.md`→`GOAL-README-SCRIP.md`), corpus, and a final zero-check. **Re-verified this
  landing:** `REPO-SCRIP.md` exists, `REPO-one4all.md` is gone. The file's own "Session State" claimed
  `one4all` hits at "SCRIP 0 / corpus 0 / .github 0-except-this-file" — **that specific bookkeeping line had
  already gone stale by the survey phase** (63 live `.github` hits and 2 corpus hits by the time of survey,
  all confirmed to be sanctioned frozen historical narration, not live operational refs — the RENAME's actual
  policy was honored, only its own self-reported counter drifted as later documents accumulated the token in
  historical prose). Commit `c334861` (SCRIP) is a confirmed real ancestor of current SCRIP HEAD, re-checked
  directly by this landing (`git merge-base --is-ancestor`); `ec8bbbe` (corpus) and the `.github` hash do not
  resolve by exact hash today (same hash-drift class as elsewhere in this project's history — content-level
  verification is what actually proves the rename landed, not the recorded hash).

## CMPILE removal — unifying on the bison/flex parser

- **`GOAL-REMOVE-CMPILE.md`** (was: 189 ln) — excised `CMPILE.c`, a hand-written recursive-descent parser that
  ran in parallel with the bison/flex parser (`snobol4.tab.c`/`snobol4.lex.c`) and produced a separate
  `CMPND_t`/SIL-`stype` tree whose bridge into `EXPR_t` (`cmpnd_to_expr()`) was incomplete, silently misrouting
  some expressions (the immediate trigger was an omega-driver `EVAL(string)` bug leaking a raw `BINGFN` stype
  into an `EXPR_t` kind field). All 8 steps (S-1 through S-8) checked off: `parse_expr_pat_from_str` and
  `sno_parse_string` added to `snobol4.tab.c` as the bison-path replacements for the three CMPILE parse entry
  points (program / expression / statement-block), `eval_code.c`/`snobol4_pattern.c`/`scrip.c` migrated off
  CMPILE, omega driver 15/15, beauty suite ≥15/18. **Re-verified this landing:** the `scrip` binary in this
  checkout carries zero `cmpile` symbols (`nm scrip | grep -i cmpile` — empty) and zero `#include.*CMPILE`
  anywhere in `src/` — both of the file's own literal S-6 done-when checks, run fresh rather than trusted from
  the doc. Commit `476fd067` does not resolve in this checkout (hash-drift class), but the binary-level and
  source-grep checks are the stronger proof and both pass. **Cross-reference to fix in place of this file**:
  the still-live `GOAL-TWO-STEP-HUNT.md` names this file as a blocker ("blocks on `GOAL-REMOVE-CMPILE.md`") and
  a separate survey pass already established that block reads as resolved — `parse_expr_pat_from_str`/
  `g_eval_str_hook`/`interp_eval_pat` are this file's own completed deliverables, not a coincidentally-identical
  unrelated hook. Whoever next touches `GOAL-TWO-STEP-HUNT.md` should update its dependency note to point here
  rather than to a live file that no longer exists.

## Session-setup and self-contained-script conventions

Two files that together established how a session decides what to build/install and how test/build scripts
behave once written — both now fully absorbed into standing, currently-enforced policy rather than being
live projects in their own right.

- **`GOAL-SESSION-SETUP-REFINEMENT.md`** (was: 142 ln) — replaced the old one-size-fits-all
  `build_full_session_environment.sh` (which built packages/scrip/spitbol/csnobol4 regardless of what a given
  goal actually needed) with a per-goal-file `## Session Setup` block convention, plus a categorized setup
  table in the REPO file. All 5 steps (SR-1 through SR-5) checked off, including the rename to
  `install_everything_full_stack.sh` and RULES.md/PLAN.md updates. **Re-verified this landing:**
  `install_everything_full_stack.sh` exists; the old `build_full_session_environment.sh` name is gone. The
  policy this file created is not just historically closed but **still the literal live rule today** — root
  `CLAUDE.md`'s own "Session start — mandatory protocol" step 7 ("Run the goal file's `## Session Setup`
  scripts") is this file's SR-4/SR-5 outcome, word for word.
- **`GOAL-SELF-CONTAINED-SCRIPTS.md`** (was: 131 ln) — audited `SCRIP/scripts/` (then `SCRIP/test/`) for three
  recurring failure modes (required env vars, stdin hangs on programs that read `INPUT`, unhandled missing
  prerequisites) and fixed each named script to derive its own paths from `$0`, redirect `< /dev/null`
  unconditionally, and SKIP rather than hang or error when a prerequisite is absent. All 8 steps (SC-1 through
  SC-8) checked off. **Re-verified this landing:** all 7 scripts the file names as fixed or as the model
  template (`test_smoke_scrip_all_modes.sh`, `test_csnobol4_budne_suite.sh`,
  `test_interp_broad_corpus_and_beauty.sh`, `test_icon_all_rungs.sh`, `test_smoke_unified_broker.sh`,
  `test_broad_unified_broker.sh`, `build_parse_expr_unit_test.sh`) exist today under
  `SCRIP/scripts/` exactly as named. Its "scrip blocks on stdin only when the running program reads INPUT"
  finding is the same rule root `CLAUDE.md` states today ("Always redirect `< /dev/null` on scrip calls").

## RETIRED NAMES

Four source files, all deleted, replaced entirely by this one file:

| Retired name | Where its content now lives |
|---|---|
| `GOAL-SCRIP-RENAME.md` | § The one4all → SCRIP rename |
| `GOAL-REMOVE-CMPILE.md` | § CMPILE removal — unifying on the bison/flex parser |
| `GOAL-SESSION-SETUP-REFINEMENT.md` | § Session-setup and self-contained-script conventions |
| `GOAL-SELF-CONTAINED-SCRIPTS.md` | § Session-setup and self-contained-script conventions |

**Symbols/paths from the retired files that a stray grep might still turn up** (all confirmed dead or
superseded, listed once here rather than per-section): `CMPILE.c`/`CMPILE.h`, `cmpile_file`, `cmpile_lower`,
`cmpile_eval_expr`, `cmpnd_to_expr`, `cmpile_string`, `cmpile_init`, `cmpile_add_include`, `eval_via_cmpile`,
`CMPND_t`, `build_full_session_environment.sh` (renamed to `install_everything_full_stack.sh`),
`REPO-one4all.md` (renamed to `REPO-SCRIP.md`), `GOAL-README-ONE4ALL.md` (renamed to
`GOAL-README-SCRIP.md`), `one4all` / `ONE4ALL` / `One4all` as a live path/URL/var token (the bare word still
appears, correctly, inside frozen migration-history prose elsewhere — that is sanctioned, not a residual bug).
