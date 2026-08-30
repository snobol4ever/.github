# FINDING 2026-08-30 (ceo, CEO mode, Lon direct) — SWI plunit suite 0/114 → 92/114 (80%, gate green): one lowering cure; GNU board's run-gradable population 4 → 15

Lon's order: "We need numbers for SWI. Get the two Prolog suites working." Both now grade. Trees: SCRIP `98fc057b` (the cure) + `89d4e38a` (zls caps + README), corpus unchanged.

## The defect chain, each link witnessed
1. `test_prolog_swi_suite.sh` read PASS=0 FAIL=114 with empty actual output. Hand-run showed plunit executing but "% 0 passed, 0 failed" — **zero tests registered** (row plunit-test-discovery-registers-zero-tests).
2. Two-file witness (`:- write(dir_ran), nl.` + a main): dir_ran never printed — **every load directive was dropped whenever a real initialization goal existed** (row prolog-load-directives-dropped-when-main-exists). Mechanism: `lower_pl_stage2` excluded the synthetic `pj_dir_<N>` directive wrappers from the init-goal accumulator, a guard written for the old by-name-call era; the accumulator has inlined-not-called ever since, so the guard's hazard was gone and only its damage remained.
3. With the wrappers included, the goals rode ONE comma chain: the first unsupported `use_module` failed and aborted every goal after it (still zero tests), exiting rc=1. Reference semantics run each directive/initialization goal independently — warn naming the goal, continue, exit 0 (row prolog-failed-initialization-goal-exits-1-where-swipl-exits-0). Cure: per-goal `(Body ; warn-and-continue)`, source order preserved. No `->` needed — cross-goal backtracking does not exist in the reference semantics.

## Measured after (all fresh, same binary)
- SWI plunit vendor suite: **PASS=92 FAIL=22 of 114 (80%, runner's own gate met)** — from 0.
- GNU vendored tree (62 files): run-gradable **4 → 15** (their directives now build entry chains): ok_pass=6, ok_fail=9 (each fail a production-Prolog defect lead — row gnu-suite-9-run-fails-triage), lib=45, reject=2 (known parse-hang pair).
- Floor: SNOBOL4 corpus m3/m4 PASS=1672 FAIL=0 · both live gates OK · prolog smoke 5/5 both modes · icon 14/14 both · snocone 5/5. Re-verified TWICE (after the cure, and again after the zls caps raise).
- Rows closed as DONE in QUEUE.tsv: swi-tests-subdirs-invisible (recursive-find fix already landed, 18→114 files graded), plunit-test-discovery-registers-zero-tests, prolog-load-directives-dropped-when-main-exists, prolog-failed-initialization-goal-exits-1-where-swipl-exits-0.

## The capacity probe (stopped deliberately)
Compiling gprolog's 60 non-reject modules as ONE compiland hit four successive `zls: * table overflow` aborts (vslots, entries, fields, vslots again after a 4x raise). The loud refusal worked; the caps are the wrong design for compilands this size — rowed as `zls-tables-static-caps-vs-dynamic` with the probe as its acceptance witness. Caps stay raised 4x meanwhile (SCRIP `89d4e38a`).

## Transferable
A guard written for a mechanism that later got redesigned does not announce its own obsolescence — the exclusion was *correct when written* and had been pure damage since the inline accumulator landed, and nothing red pointed at it because its entire effect was silence (0 tests "passing" 0). The witness that cracked it was two lines. When a harness reports an impossible zero, reach for the smallest program that should print one line.
