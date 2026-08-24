# FINDING 2026-08-24 (seat16) — corpus coverage audit: closing STEP 4 (probe/ liveness), two real gaps found

⛔ **CORRECTION added 2026-08-24, same day, by seat16 after seat15's independent re-triage — kept as an addendum, original text below left intact for provenance.** The "`witness_icn_options_dash_branch.icn` currently prints nothing where `.ref` expects `dash`... wrong-answer, not a crash" claim in the `probe/icn/` section below is **not a SCRIP bug**. seat15 (task `probe-icn-glob-invisible`, LEDGER, 2026-08-24T22:2xZ) showed the bare invocation this pass's sub-agent used can never reach the witness's `dash`-printing branch by the program's own logic (empty `args` list), while invoking it with `-- -x` reproduces the `.ref` byte-for-byte — so all 11 `probe/icn/` witnesses are in fact currently correct; this was a mistriaged invocation, not a wrong answer. The coverage gap itself (nothing sweeps `probe/icn/`) and the STEP-4 count correction (74 vs. 68 subdirectories) below are unaffected and stand. The standalone bug row this FINDING minted, `probe-icn-options-dash-branch-fail`, should be treated as CLOSED-NOT-A-BUG by whoever next touches it; the real remaining question (per-witness-args vs. regenerated `.ref`) now lives on `probe-icn-glob-invisible`'s STEP 1.

**Task:** `audit-corpus-what-is-ungated`. Fifth pass on this task. The prior (fourth) pass's LEDGER entry already stated "STEP 4 BELOW IS NOW RESOLVED, NOT OPEN" (citing the addendum FINDING's SUITES-table read), but the task file's own `## NEXT` block still carried the old STEP 4 text verbatim ("Untouched this round; still the single biggest remaining unknown in the census") — a STALE-ORIENTATION instance inside the baton meant to prevent exactly that. This pass re-verified the resolved claim from source before trusting it, closed STEP 4 properly, and — because re-verification meant actually walking all 69 then-unconfirmed subdirectories rather than re-citing the prior claim — found two genuine gaps no prior pass's `.sno`-oriented methodology could have surfaced.

## Headline: the count itself was wrong, and two directories share this task's own bug shape

`corpus/probe/` is **74** subdirectories, not the 68 every prior pass (first FINDING onward) assumed — 5 confirmed-gated (`bb`, `clobarm`, `fz`, `kw`, `cn`) + 69 unconfirmed, not 63. Cause of the discrepancy not chased down; flagged rather than guessed at.

Of the 69: 64 are COVERED by `scorecard_snobol4.sh`'s `probes_misc` SUITES row (a recursive `find … -name '*.sno' -not -path '*/bb/*'`, confirmed by tracing `run_one`'s grading logic directly — including the no-`.ref`-file case, which falls back to live-oracle comparison rather than silently passing). 1 (`json_fence0_leak`, `.json` fixtures not `.sno`) has its own dedicated gate, `test_gate_json_fence0_leak.sh`. 2 (`carve/` — closed-question microbenchmark tooling; `zone/` — an explicitly abandoned s136 research thread, its own README says verbatim "DIRECTION UNKNOWN. DO NOT INHERIT THESE AS 81 BUGS") are not correctness-witness directories at all and were never a coverage question.

The remaining **2 are genuine gaps, and they are the same blind spot this whole task exists to find**: `probe/icn/` (11 files, `.icn`+`.ref`) and `probe/plz/` (9 files, `.pl`+`.ref`) are the only two non-SNOBOL4 witness directories under `probe/`, and `probes_misc`'s glob is `*.sno` only — both are structurally invisible to the one mechanism that sweeps everything else in this tree, for the same reason the parent brief's own JSON hang sat green: not on any list.

## `probe/icn/` — coverage gap plus a live bug it was hiding

Live run (`scrip --run` vs `.ref`, fresh `make`, not `make pristine` — a spot-check, not a gate verdict) of all 11: 10 pass. 1 — `witness_icn_options_dash_branch.icn` — currently prints nothing where `.ref` expects `dash` (`rc=0` both ways; wrong-answer, not a crash). Checked against every `*.task.md` and `QUEUE.tsv` under plausible names (`argslot`, `frameslot`, `carve_leak`, `pos0_stale`, `options_dash_branch`) — zero hits. This was not a known, tracked red; it was invisible because nothing runs the directory at all. Minted as its own row (`probe-icn-options-dash-branch-fail`) separate from the wiring gap, matching this task's own convention of splitting "nothing sweeps this" from "and here is what it would have caught" (see `crosscheck-snocone-dead-runner-181-files` vs. its sibling crash/hang rows).

New row: `probe-icn-glob-invisible` (QUEUE.tsv rank 3) — wire the sweep, blocked on the bug row above landing first so the new sweep opens green-except-none rather than green-with-a-blind-spot swapped for a silent red.

## `probe/plz/` — coverage gap, deliberately NOT chased into a bug claim

Live run of all 9: 1 passes (`plz_p1_single_clause`); 8 SEGFAULT (rc=139) — two-clause, fail-driven, recursion, disjunction, member, cut/commit, cut-bars-retry, guard-then-cut. This looks alarming in isolation, but `/home/resources/postoffice/tasks/prolog-next.task.md` shows active PZ-1(b)-(e) work in flight (LIVE CURSOR at PZ-1(d) landed, PZ-1(c) next) — an 8/9 failure rate on a Prolog-zeta corpus mid-implementation is plausibly expected, not a regression, and this pass had no Prolog-domain context to tell the difference. Per this task's own repeated rule ("do not weaken DONE-WHEN to make it pass"; ASM-DIFF-FIRST's general spirit of not asserting a diagnosis from a symptom alone), the new row's DONE-WHEN deliberately refuses rather than guessing.

New row: `probe-plz-glob-invisible` (QUEUE.tsv rank 5) — first action is asking the `prolog-next` owner which of the two this is, not writing a sweep.

Noted in passing, not investigated, possibly related: `test_prolog_rung_suite.sh` currently SKIPs outright ("corpus not found at /home/claude16/corpus/prolog") — collateral from the 2026-08-24 corpus re-grid (`ceo`'s inbox broadcast this session read on pickup) moving paths under `tests/{lang}/`. Recorded on the `probe-plz-glob-invisible` row for whoever picks it up; not chased further here.

## STEP 4 close-out

Rewrote the task file's `## NEXT` STEP 4 entry to state resolution plus the two new rows, rather than leaving the fourth pass's LEDGER claim and the file's own visible text disagreeing. `probe/` can be dropped from this audit's remaining-unknowns list. The task's overall DONE-WHEN is still correctly un-computable — STEP 6's HQ coverage-policy ruling (already asked, per the fourth pass) remains the real path to closing this row, now with one fewer open step feeding it.

## Not reached this session (explicit, not silent)

Did not touch STEPs 1/2/3/5/7 (separate rows or already someone else's next action per the task file). Did not re-derive or re-verify anything the fourth pass's addendum FINDING already settled beyond the specific claim (STEP 4 / probe/ coverage) this pass needed to trust before building on it.
