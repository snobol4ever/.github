# FINDING — `--run` on `plunit.pl` + any second Prolog file + a wrapper fails silently (rc=1, zero stdout/stderr); SWI-suite coverage measured at 0%, not the 100% baseline a 2026-05-29 commit recorded

**seat14 · 2026-08-29 · row `tests-consolidate-prolog`**

## The bug

`bash SCRIP/scripts/test_prolog_swi_suite.sh --file test_call` (and `--file test_arith`) report
**0% coverage, every suite `EMPTY`** — not individual test failures, no verdict recorded for any of
the 9 (resp. 26) suite-lines in either file. `--verbose` shows the raw scrip output is **completely
empty**, not truncated or garbled.

Isolated with a minimal synthetic suite (no SWI-test-corpus content involved):

```prolog
:- begin_tests(triv).
test(ok) :- true.
:- end_tests(triv).
```

```
$ ./scrip --run corpus/tests/prolog/plunit.pl trivial_test.pl wrap.pl < /dev/null
(no output at all)
$ echo $?
1
```

where `wrap.pl` is exactly what `test_prolog_swi_suite.sh` generates: `main :- run_tests.\n:-
initialization(main).\n`. Same silent rc=1 on the trivial synthetic suite as on the real SWI test
files — this is not about the content or complexity of any particular test file.

**Bisection, each step measured directly, not assumed:**
- `./scrip --run corpus/tests/prolog/plunit.pl < /dev/null` (plunit.pl alone) → **rc=0**, no output
  (expected — it only defines predicates + an `:- initialization(pj_suites_init)`, nothing to print).
- `./scrip --dump-ast plunit.pl trivial_test.pl wrap.pl < /dev/null` (same 3-file combo, parse only)
  → **rc=0**, clean AST for all three files. Not a parse-level defect.
- `./scrip --compile plunit.pl trivial_test.pl wrap.pl -o out.s < /dev/null` (same combo, mode-4 asm
  emission) → **rc=0**. Mode-3-specific, at least through codegen (full link+execute of the mode-4
  output was not attempted — out of scope for this session).
- Multi-file `--run` in general is not broken: a 3-file combo with no plunit involvement at all
  (`a.pl`/`b.pl`/`c.pl`, `c.pl`'s `main` calling predicates from both siblings) runs correctly, rc=0,
  both outputs printed. A 2-file combo missing a needed predicate fails *loudly* (`Error 22 ...
  Undefined function called`, rc=1) — the normal, expected failure shape. The plunit combo's total
  silence is the anomaly, not the rc=1 itself.
- Adjacent but not identical: two files that each carry their own `:- initialization(Goal)` directive
  (no plunit involved) run with **only the second file's initialization goal firing** — rc=0, first
  file's goal silently dropped, not an error. `plunit.pl` (its own `:- initialization
  (pj_suites_init)`) + `wrap.pl` (`:- initialization(main)`) is exactly this shape, so multiple
  `:- initialization/1` directives across loaded files interacting badly is a plausible contributing
  mechanism — **not confirmed as the root cause**, only noted as a related, independently-reproducible
  symptom in the same area.

Rebuilt (`make`, not `make pristine`) after `git pull --rebase` picked up new SCRIP commits touching
`src/ir/zeta_storage.c`, `src/runtime/rt/zeta_alloc.c`, `src/templates/x86/x86_asm.h` (2026-08-29) —
re-confirmed the silent failure on the fresh binary, not a stale-build artifact.

## Regression, not a pre-existing known-red state

`corpus` commit `8ffc281e1` (2026-05-29, subject: "SWI-5 EMPTY verdict: 53/57(92%) -> 57/57(100%)
honest baseline") recorded this exact suite at 100%. Today's measurement is 0% on every file sampled.
Three months of unrelated development sit between that commit and today; **not bisected** — would
need a real `git bisect` across both repos to pin down when/what broke, out of this row's scope
(this row is corpus test-consolidation, not compiler runtime debugging).

## Disposition this session

Not fixed — per `RULES.md`'s ASM-DIFF-FIRST debugging order this deserves a proper `.s` diff between
a passing sibling and the failing witness, which a 2-file-vs-3-file/plunit-vs-no-plunit repro pair
like the ones above should make cheap to mint, but that is compiler-runtime work, not this task's
lane. Recorded here and in `tests/prolog/KEEP.md` (this session's other work on this row). Mailing
hq_C (runtime/wrong-answer-class bugs are hq_C's lane per this task's standing convention).

## Not attempted

- Bisecting when the regression landed (3 months of history, both repos).
- Confirming or refuting the multiple-`:- initialization`-across-files hypothesis as the actual root
  cause of the plunit case specifically (only shown to be a related, independently-real symptom).
- Whether mode-4's successful asm emission for the same combo actually links and runs correctly
  end-to-end (only `--compile -o out.s` was tried, not a full build+execute).
