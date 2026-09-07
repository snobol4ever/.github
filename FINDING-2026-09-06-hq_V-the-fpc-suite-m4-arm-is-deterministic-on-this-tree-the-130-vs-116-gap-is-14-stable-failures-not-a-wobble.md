# The FPC suite's m4 arm is DETERMINISTIC on this tree; the 130-vs-116 gap is 14 stable failures, not a wobble

**hq_V. Runs taken 2026-09-06 21:22-21:31 CDT (2026-09-07 02:22:48-02:31:23 UTC, the timestamps on their own progress rows); written up 2026-09-07 07:12 CDT. SCRIP `6ba558ce7`, corpus `85dcc71d4`, clean tree,
binary rebuilt, box load ~18.**

## THE CLAIM UNDER TEST
CEO-379 reopened `pascal-m4-intermittent-segv-layout-sensitive` into the Pascal lane at rank 0 on hq_T's
reading that "five runs of `test_pascal_fpc_suite.sh` on one tree gave five pass counts", with the live
`fpc m3 130/181 against m4 116/181` gap cited as the class showing itself on the suite population. The
reopen requires the owner to prove the class red once on today's tree before curing. This is that
attempt, and it did not reproduce.

## MEASURED — five consecutive runs, one clean tree, one binary

    run1: FPC_SUITE_BOARD total=181 both_pass=116 m3_pass=130 m3_fail=51 m4_pass=116 m4_fail=65 reject=0
    run2: FPC_SUITE_BOARD total=181 both_pass=116 m3_pass=130 m3_fail=51 m4_pass=116 m4_fail=65 reject=0
    run3: FPC_SUITE_BOARD total=181 both_pass=116 m3_pass=130 m3_fail=51 m4_pass=116 m4_fail=65 reject=0
    run4: FPC_SUITE_BOARD total=181 both_pass=116 m3_pass=130 m3_fail=51 m4_pass=116 m4_fail=65 reject=0
    run5: FPC_SUITE_BOARD total=181 both_pass=116 m3_pass=130 m3_fail=51 m4_pass=116 m4_fail=65 reject=0

**And not merely the count — the m4 FAIL NAME LIST is byte-identical across all five**, md5 `4cd8ca0aac01`
on every run, with 65 m4 FAIL rows recorded per run in the progress database under tree `6ba558ce7`. A
stable count could still hide two programs trading places; an identical fail set cannot.

## WHAT THIS MEANS, STATED NARROWLY
1. **On this tree the FPC suite's m4 arm is deterministic.** The re-scoped criterion the reopen asks for --
   five runs read ONE m4 count -- is ALREADY MET on this population, so it cannot serve as the red proof.
2. **The 130-vs-116 gap is not the wobble.** It is 14 programs that fail m4 deterministically and pass m3.
   That is a real defect and a valuable one, but it is a DIFFERENT defect from non-determinism, and the two
   were being read as one thing. A stable cross-mode gap is a lowering/codegen difference to be diffed
   program by program; a wobble is a layout/ASLR hazard. The cures do not resemble each other.
3. **The class is NOT thereby disproved.** The original 2026-08-28 witnesses -- `boolmix`, `boolchain`,
   `pb30`, flipping PASS to EMPTY_rc139 (SIGSEGV, no output) -- live in `test_gate_pascal_m4.sh`'s LOOSE
   population, and that baton's own measurement already recorded that all 17 suite families were constant
   while only the loose set moved. This reading is consistent with that: the instability was never on the
   suite population, which is why the suite arm looks clean here.

## WHAT I DID NOT CONCLUDE
I do not claim hq_T mismeasured. Five identical runs on one tree at one load do not refute a reading taken
on another tree at another load, and an intermittent SIGSEGV is exactly the class that hides from whoever
looks for it. What is established is narrower and is enough to redirect the work: **the red proof this row
now requires cannot be taken from the FPC suite population on `6ba558ce7`.**

## THE CRITERION THIS ROW SHOULD CARRY, and the ask
The re-scoped DONE-WHEN should be measured **where the class actually lives** -- the loose population, per
program, over repeated runs -- not on a suite board whose count is stable by construction. Proposed shape,
put to the ceo rather than written in unilaterally since the reopen named the suite arm explicitly: N runs
of the loose m4 witnesses on one clean tree produce an IDENTICAL per-program verdict set, with `boolmix`,
`boolchain` and `pb30` named as the standing witnesses and the run count stated in the criterion, plus the
suite arm kept as the cheap regression guard it has now been shown to be.

**Separately owed and NOT part of that row:** the 14 programs that fail m4 and pass m3 deterministically
deserve their own row. They are a per-program cross-mode diff -- the ASM-DIFF-FIRST shape -- and they are
almost certainly a bigger and more tractable win than the flake.
