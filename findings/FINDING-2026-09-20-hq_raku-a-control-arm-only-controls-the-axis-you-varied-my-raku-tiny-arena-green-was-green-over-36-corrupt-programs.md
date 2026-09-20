# FINDING 2026-09-20 hq_raku — a control arm only controls the axis you varied: my raku tiny-arena green was green over 36 corrupt programs

*(This file was titled "…the raku share of the collector question is clean at one megabyte…" for forty minutes. It was renamed by its own author when the stress arm came back red. The original measurement is kept below in full, unedited, because the interesting thing about it is that it is correct and useless.)*

> ⛔⛔⭐⭐ **SUPERSEDED IN PART, BY ME, 40 MINUTES AFTER IT WAS WRITTEN — AND THE SUPERSESSION IS WORTH MORE THAN
> THE ORIGINAL.** Everything measured below is TRUE and was GREEN OVER A LIVE DEFECT. The same tree, the same
> binary, one knob added (`SCRIP_GC_STRESS=16`): **raku master m3 853 → 817, m4 853 → 824, 65 gradings lost, zero
> gained, 36 distinct programs, every one exit 0 with a plausible wrong answer.** ⛔ **RAKU IS NOT CLEAN AT THE
> TINY ARENA AND TENET CONDITION 1 IS NOT MET IN THIS LANE.** Rowed rank 0 as
> `raku-gc-thirty-six-programs-return-a-silently-wrong-answer-under-forced-collection-and-the-arena-ab-reads-green-over-all-of-them`.
>
> **WHY THE MEASUREMENT BELOW COULD NOT SEE IT, which is the reusable half and the reason this file was not
> deleted:** every arm below varies the **ARENA**, and this class moves along **STRESS**. `SCRIP_GC_STRESS` unset
> means ZERO forced collections (`gc_heap.c:245` sets collect-pending every N allocations), so a 1 MB window
> collects more often than nearly-never — which on programs this size is still nearly-never. **Two arms that
> differ only in the window agree with each other while both are wrong.** Measured first by hq_snobol4, relayed
> by hq_prolog, and it reached me one hour after I had published the green.
>
> ⭐⭐ **A CONTROL ARM ONLY CONTROLS THE AXIS YOU VARIED.** Say which axis the defect is expected to move along
> BEFORE trusting an A/B; if it is not the axis you varied, the zero you got is a measured property of the wrong
> experiment. A suite table that then names the arena turns that zero into something that READS AS COVERAGE,
> which is worse than silence. ⭐ What survives unchanged: the **fingerprint** method below (identical verdicts
> hide a differently-wrong answer, `FAIL == FAIL`), the census, and the whole REF-order section.
>
> ⭐ **THE ABLATION THAT CAME OUT OF THE RED, added here because it is the lead:** `("a","b").join("-")` is
> CORRECT at stress 1 while `.map({block})` and `G.parse` on the same shapes are wrong — so it is not the list,
> the literal, or methods in general, but the only two raku runtime entries that RE-ENTER EMITTED CODE THROUGH A
> SAVED CALL and hold collected-heap state across it: `rk_iter_open`/`rk_iter_step` and `rk_gram_enter_box`.
> `join` never leaves the runtime and survives.

**Tree:** SCRIP `5418432bb` · corpus `8486bb1e2` · `.github` `21e7958e` · RT_OPT=-O0 · incremental `make` (rc=0)
**Mode:** TENET. **Order:** MODE line 2 CONDITION 1 — *completeness does not open in a language until that language's
GC share is measured clean by oracle diff at the tiny arena* — and the ceo's telegram clause TWO.
**Measurer:** hq_raku. **Box:** 16 cores, shared with five other seats' boards; every arm below is correctness-graded,
never timed, so load is stamped and not load-bearing.

## THE CLAIM, AND EXACTLY HOW FAR IT REACHES

**No raku answer in four populations moves when the collector runs constantly.** It does NOT say the collector is
correct, and it clears no other lane. Four arms, each with its own denominator:

| arm | population | result |
|---|---|---|
| master, arena A/B | 1858 (program,mode) gradings | **0 verdict divergences** |
| master, output fingerprints | 40 printed non-passing gradings | **0 divergences in `fp=` or `rc`** |
| benchmarks+demos, arena A/B | 17 programs, oracle-correct refs | **17 of 17 identical** (verdict, `fp`, rc) |
| GC witnesses under stress | 3 witnesses × 8 stress points × 2 modes | **48 gradings, 0 mismatches** |

Arms 1 and 2 are ONE tree, ONE binary (`BINARY_AT_START 84d80bfb4f63 53d26946653b` printed by both arms), run twice:
`SCRIP_HEAP_MB=1` then `SCRIP_HEAP_MB` unset (`arena_mb=512`). Arm 4 is the ceo's own hq_snobol4 probe shape, which on
snobol4 reads **four of seven stress points silently wrong at exit 0**, re-run in raku at `SCRIP_GC_STRESS` 0,1,2,3,4,5,8,16.

## ⭐⭐ THE PART WORTH KEEPING: A VERDICT DIFF READS GREEN OVER THE CLASS IT IS MEANT TO CATCH

The totals were identical before I looked at anything else: 853/929 both modes at both arenas. **That proves nothing,
and stopping there would have been the whole failure.** Two things hide underneath equal totals, and they hide at
different depths:

1. **A SWAP** — one program flips green while another flips red. Caught by comparing per-program VERDICTS.
2. **A DIFFERENTLY-WRONG ANSWER** — a program that is FAIL at both arenas, failing with *different output* at each.
   **A per-program verdict diff cannot see this**: `FAIL == FAIL`. And this is precisely the shape the ceo measured on
   the snobol4 witness — a plausible wrong answer, exit 0, no diagnostic. The instrument built to catch the corruption
   would have reported GREEN over the corruption.

The cure is not a better verdict: it is to stop comparing verdicts. The harness already prints `[fp=<md5/8> rc=N]` on
every non-passing line, so the raw OUTPUT is comparable without re-running anything. **136 FAIL rows per arm were dark
to arm 1 and are graded by arm 2.** ⭐ The general form, which outlives this measurement: **when an instrument's
verdict is a LOSSY function of the observation, an A/B on the verdict is blind in exactly the region where the two
arms are both wrong — and that region is where a corruption bug lives, because corruption does not usually turn a
right answer into a right answer.**

## ⭐ THE SELF-PIN OBJECTION IS ANSWERED, NOT WAIVED

`SCORE.md` has warned since 09-03 that the raku master's refs are a SELF-PIN, not an oracle — they were written by us,
rung by rung. Under CEO-391/395 rule 3 that caps what a green cell proves. **It does not cap this one**, and the reason
is structural rather than a plea: this is an A/B between two arms on ONE tree, so both arms are graded against the same
ref and the ref subtracts out; and arm 2 compares raw output bytes to each other, not to any ref at all. **A self-pinned
ref is a weak oracle and a perfectly good DIFFERENCE DETECTOR.** Arm 3 removes the objection outright by using refs I
proved oracle-correct in the same sitting.

## ⛔ THE COMPLETENESS FACT THAT FELL OUT OF PROVING THE REFS — LON'S REF ORDER, WITH A NUMBER

Lon 2026-09-20, verbatim: *"Add a REF file for all benchmark and tests since how would you know what you are measuring
unless the output is correct."* The ceo measured 168 of 305 corpus benchmark and demo programs carrying no `.ref`.
**The raku share of that population is ZERO — 0 of 17 refless, and 0 of 3 refless GC witnesses.** But the order's real
question is the second clause, and answering it costs one command per program:

- **17 of 17 raku benchmark refs agree byte-for-byte with rakudo-local 2026.05.** The refs are correct.
- **Only 5 of those 17 benchmarks PASS.** Twelve do not: eleven are `rc=1` compile refusals (`fp=d41d8cd9`, the md5 of
  empty output) and one is a wrong answer at rc=0 (`pi-sequential-iteration`).

So **twelve of seventeen raku benchmarks would have been TIMED on an answer that is not the right answer** — which is
Lon's sentence exactly, arriving from the other side: the refs were not missing, they were correct and unconsulted.
⛔ A timing over those twelve is not a slow measurement or a fast one, it is not a measurement.

## ⛔ AN INSTRUMENT TRAP EVERY HQ IS ABOUT TO HIT, BECAUSE LON'S ORDER SENDS ALL SIX AT THEIR ORACLES

Four of the 17 read UNMEASURED at first because rakudo exited 1. **They are the SELF-TIMED kernels and they need
`-I. -Mprelude_rakudo`; the file's own header says so.** I was one step from writing "4 of 17 have no usable ref" —
a well-formed wrong answer about a gap that does not exist. The only reason I caught it is that my script printed the
four BY NAME instead of folding them into a count. ⭐ **An oracle arm that exits non-zero is COULD-NOT-MEASURE and must
be named, never counted as a gap: a reader cannot tell a program with no ref from a program whose oracle you invoked wrongly.**

And the second half, which is worse because it is silent: **running the oracle with `-I.` inside the corpus tree writes
`benchmarks/raku/.precomp/` into it.** The corpus then reads DIRTY, and `util_score_row.py` correctly REFUSES to land
any SCORE.md row — *"this run measured a tree nobody else can check out"*. The refusal is right; the surprise is that
**the act of verifying your refs is what disarmed your own leaderboard duty**, and nothing connects the two events for
the reader. ⛔ THE CURE IS THE WRITER, NOT AN IGNORE RULE — which is `corpus/.gitignore`'s own stated doctrine at its
icon-scratch entry (*"an ignore rule left standing alone would silence a symptom while the writer lives"*). **Copy the
prelude to a scratch dir and use `-I<scratch>`:** proven here — same answer, `rc=0`, `.precomp` lands outside the tree,
`git status --porcelain` stays at 0. ⭐ **The class is not rakudo's:** icont writes `.u` files, swipl writes `.qlf`,
fpc writes `.o`/`.ppu`. Every HQ about to grade its refs against its own oracle should run that oracle from a scratch
cwd, or discover its boards refusing later and not know why.

## THE CENSUS HALF, FOR COMPLETENESS

`util_gc_census.py maps --zls-langs raku`: **graded=922 no_layout=7 (declared=2, defect=5), unkinded=0 holes=0, GREEN**
(was no_layout=9 graded=918 at `621c08866`; `benchmark_rc-man-or-boy-test` and `benchmark_point_class_add2` gained
layouts on the `:=` bind landing). The two DECLARED are role-composition diagnostics the master's own `ALL.wantrc`
declares must not compile — correct and permanent, not defects. **The five defects are front-end parse refusals and
not collector holes, and that is measured rather than assumed: every no_layout entry is ALSO red on the master board,
so the set is a SUBSET of the master's own reds.** They are rowed elsewhere
(`raku-the-sequence-operator-is-a-real-list-headed-operator-never-a-range-alias`,
`raku-the-six-benchmark-graphs-with-no-frame-layout-are-cured-one-construct-family-at-a-time`).

## REPRODUCE

```
cd SCRIP && make
SCRIP_HEAP_MB=1 python3 scripts/corpus_suite_harness.py run ../corpus/tests/raku/ALL.raku \
    ../corpus/tests/raku/ALL.ref --lang raku --modes m3,m4 --by-modes-column
env -u SCRIP_HEAP_MB python3 scripts/corpus_suite_harness.py run ../corpus/tests/raku/ALL.raku \
    ../corpus/tests/raku/ALL.ref --lang raku --modes m3,m4 --by-modes-column
# then diff BOTH the per-program verdicts (progress DB) AND the printed [fp= rc=] pairs.
```
⛔ Diff both. The first diff alone is the green-over-the-bug reading this finding exists to name.
