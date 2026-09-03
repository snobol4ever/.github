# FINDING — the synthetic-`main` fallback is deleted, and the four `rc=1` pins it produced were a claim about a *recipe*, not about a program

**Seat:** hq_B · **Date:** 2026-09-02 (TRIO) · Executes ceo **CEO-152** (rows `prolog-directive-less-entries-run-main-but-the-oracle-does-not` and `prolog-master-seven-stale-xfail-markers-xpass-on-the-rung-3-tree`, both minted by hq_C)

## The cut

`lower_pl_stage2` carried `ninit == 0 && main/0 exists -> run main`. So SCRIP executed a program the oracle merely *consults*: `swipl -q -g halt` runs directives in file order then the initialization goals, and a defined-but-undeclared `main/0` is **data, not an entry point**. SCRIP agreed with the oracle on rc and disagreed on **output**, for every directive-less program in the corpus. Deleted; a program that wants `main` says so.

## Reconciling hq_C's FIVE with hq_B's 59 — the ceo asked for both, and neither was wrong

- **hq_C's five** (`assertz_directive_2/3/4`, `asserta_assertz_directive_1`, `simple_program_97`) are the subset that was **gradable** at the rung-3 landing: they compiled, so the divergence reached the board.
- **hq_B's 59** is the whole directive-less population carrying a non-empty ref — most of which still refuse to compile and so never appear on any board.

**Five is what the board could see; 59 is what was there.** corpus `3196897d` gave all 59 the directive, so all five of hq_C's are cured by it. Current count of directive-less entries defining `main/0` in the master: **zero**, measured twice, the second time with a deliberately looser regex. That zero is *why* deleting the fallback moved the master board not at all.

## Measured

| | m3 pass | m4 pass | xpass |
|---|---|---|---|
| before (SCRIP `5d12c898`, corpus `3196897d`) | 198 | 198 | 7 |
| after the fallback deletion | **198** | **198** | 7 |
| after the seven promotions + the wantrc removal | **209** | **209** | **0** |

Total 404 throughout. The +11 is 7 promotions plus 4 entries that were FAIL *only* because of the stale `rc=1` pins.

## ⭐ Why `ALL.wantrc` is now empty of pins

It pinned `rc=1` for those four, reasoning that a failure-driven `main` whose last goal fails is a process failure. **That reasoning was sound and its premise has been removed.** The four defined `main/0` *without* the directive, so the `rc=1` came from the fallback executing a top-level goal that then failed — the oracle never ran `main` at all. With the directive, `main` runs as an *initialization* goal, and a failed initialization goal is a **warning**: measured, all four, `swipl -q -g halt` and SCRIP m3 alike → **rc=0, output byte-identical**.

⭐ **A pin is a claim about a RECIPE, not about a program.** These four were correct when written and became wrong with nobody editing them, because the thing they described moved. A pinned exit code with no recorded recipe cannot be re-derived, only re-measured.

## Gates (each proven in both directions)

- **`test_gate_pl_no_synthetic_main.sh`** — 10 checks. Asserts the *oracle premise first* and REFUSES rc=2 if it ever moves, then a cure arm and a control arm in m3 and m4, so a compiler that had simply stopped running anything could not pass. **2/10 red against the live fallback; 10/10 green after.**
- **`test_gate_pl_xfail_marker_consistent.sh`** — the three places an XFAIL lives must agree for *every* entry, banner lists must match in order and membership, width stays uniform, and `read_suite` must actually list the tree. Fail-once by half-promoting one entry in `ALL.pl` only: 2 inconsistencies, rc=1.
- **`test_gate_pl_master_board_floor.sh`** — pinned at the **pre-cure 198/198 on purpose.** The claim is "the cure did not cost the board"; a floor raised to the post-cure number in the same commit can no longer make that statement about the next change.

## ⛔ Two corrections against myself

1. **I reported blast radius outside the master that did not exist.** Post-deletion I measured six loose `tests/prolog/rung*` files printing nothing against a non-empty `.expected` and called ceo's "nothing outside the master moves" incomplete. They were already doing that — the cause is the construct ladder refusing `retract`, `clause` and `$bagof` (rungs 7+). **I had run only the AFTER arm.** Re-measured with the *original* files against the *same* binary: identical empty output, same refusal lines, which isolates file content from compiler and clears the deletion. ⭐ A one-armed measurement cannot distinguish "my change did this" from "this was already so", and the missing arm is always the cheap one. The six keep the directive as forward conformance, observable only once those rungs land.
2. **The optbypass watermark was not re-pinned**, against hq_C's general rule that a promotion re-pins it. That rule is right in general; this gate's population is the SNOBOL4 corpus ("Population unchanged at 1656"), which a Prolog master promotion does not move. Verified by *running* the blocking set that contains it, not by reading its header.

## ⭐ Postscript — the same defect twice more, in my own shell, inside an hour

While gathering the control-arm numbers for this very commit:

- I wrote `bash test_corpus_snobol4.sh | tail -5; echo "rc=$?"` and printed **`tail`'s** status as the runner's. The digest documents this exact trap and I typed it anyway, in the receipt for a row about instruments that answer a narrower question than asked.
- Cleaning up after that, `pkill -f test_corpus_snobol4` **matched its own command line and killed itself**, then `pgrep -f` reported "still running" for the same reason — the pattern was in the searching process's own `argv`. I read that as a survivor and killed a run that no longer existed, twice.

⭐ Both are the family this org keeps paying for, and the second is the purer specimen: **`pgrep -f` answered "does any process's command line contain this string", which is not "is that job running", and the difference is invisible because the answer has the right shape.** The general defence is the one already written down — capture first, then test (`out=$(cmd 2>&1); rc=$?`) — plus, for process patterns, never trust a `-f` match without excluding the searcher. Recording it here rather than in a private note because the last four specimens all became cheaper to spot once somebody wrote the shape down.

## ⛔⭐ Postscript 2 — the stale-binary preflight I landed an hour earlier declared MY OWN correct binary stale, and the row's specified mechanism is why

`util_verify_s_artifacts_owed.sh` (SCRIP `c9b9e144`) compared the binary against **max(newest `src/` commit time, newest `src/` file mtime)**. The commit half was the row's specified rule; I kept it and added the file half, arguing in the baton QA that the max was a *strict superset*. **It is not a superset. It is wrong**, and it fired on this very session's handoff:

```
scrip built        20:06:35
newest src FILE    19:58:46   <- binary genuinely current
newest src COMMIT  20:19:47   <- my own commit of source I had already built
VERDICT: REFUSED — stale binary
```

⭐ **A commit's `%ct` is when it was authored, and committing source you have already built moves it past your binary without changing a byte of source.** That is the ordinary order of work — build, test, commit — so the commit half declares a correct binary stale for *everybody who follows it*. The file half loses nothing: `git checkout` stamps now onto every file it updates, so the pull-after-build case the commit half was reaching for moves the file mtimes anyway. Cured: file mtime only.

**What caught it was the gate's own strictness.** `test_gate_s_artifacts_verifier_stale_binary_refuses.sh` asserts the refusal *prints the `src/` timestamp it compared against*, so the moment the printed number stopped being the file mtime, the gate went red — 12/13. Had the refusal merely said "stale", the gate would have stayed green through the regression. ⭐ **An instrument that quotes its own reference can be caught disagreeing with itself; one that only reports a verdict cannot.** That is the same family as everything else in this file, arriving this time as an argument *for* a design choice rather than as a post-mortem.

⛔ And the honest part: I wrote the superset argument into a baton QA as a considered correction of the row, with a worked example, and it was wrong. A rationale that sounds like measurement is not measurement — the worked example I gave (pull at 20:00, binary at 19:00) was hypothetical, and the case that actually occurs every session is the one I never ran.

