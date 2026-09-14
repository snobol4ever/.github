# FINDING 2026-09-14 hq_T — roast is 1445 DARK, not 980 red, and its first-error histogram is a QUEUE, not a bottleneck

**Measured** on SCRIP `9a28ff0ee`, RT_OPT `-O0`, incremental `make`, roast tree `/home/resources/roast-master`
(unversioned), box clock 2026-09-14 ~03:2x UTC. Ordered by Lon in chat — *"get the package runner working"* —
and by ceo CEO-744, which asked whether 6 of 986 is even a measurement.

## 1. THE RUNNER WAS UNRUNNABLE BY THE SEAT THAT OWNS IT

`raku_roast_scoreboard.sh` called `one_runner_guard` on **line 2, before argument parsing**, so it was classed
a board in *every* mode and refused to every seat but the coo — including `--limit`, which prints
`ROAST_PARTIAL`, writes no SCORE row, and exists precisely to smoke the instrument.

Roast read 4 of 986 on 09-03 and 6 of 986 ten days later: the worst row on the board by a factor of thirty,
and **the seat responsible for it could not run the instrument to find out why.** That is the whole
explanation for ten days of no movement. ⭐ A guard that cannot be satisfied by the person responsible for
the thing it guards does not prevent bad measurement — it prevents measurement.

Cured (SCRIP `9a28ff0ee`): the guard is called once the mode is known, on the guard's own CEO-547 rule —
what makes a run a board is the population it grades *and the row it publishes*. Verified on this tree that
`--run`, the bare tier sweep and `--mode4` all still **REFUSE rc=2** with the guard's own unaltered message.
Only modes that write nothing are admitted.

## 2. 6 OF 986 IS NOT A MEASUREMENT OF RAKU CORRECTNESS

`--inventory` over all 1464 shipped `.t` files, nothing excluded:

| bucket | files | share |
|---|---:|---:|
| UNGRADED-PARSE | 1371 | 93.6% |
| UNGRADED-OTHER | 56 | 3.8% |
| UNGRADED-EMITTER | 14 | 1.0% |
| GRADED-FAIL | 11 | 0.8% |
| GRADED-PASS | 8 | 0.5% |
| UNGRADABLE-TIMEOUT | 3 | 0.2% |
| UNGRADED-NO-TAP | 1 | 0.1% |

**19 files of 1464 — 1.3% — ever reach our semantics.** The other 1445 are DARK: they say nothing about Raku
correctness in either direction. Read as a score, 6/986 says the compiler is 0.6% correct and implies years
of language work; what it actually measures is front-end coverage standing in front of a corpus nobody has
graded. Those two readings have opposite consequences and the number cannot distinguish them — which is
exactly the ceo's question, answered: **it is a real reading of "how many roast files run clean", and not a
measurement of the thing everyone has been reading it as.**

The manifest is its own finding: `manifest_lines=1154`, `in_tier=986`, and **42 files the 6.c manifest names
that the vendored tree does not contain** — so the 986 denominator has never been fully present on disk.

Encouraging, and genuinely unexpected: **`use Test`, `plan`, `ok`, `is` and `done-testing` all work today.**
The TAP vocabulary is not the gap. `plan`/`ok`/`is` are lexer keywords and `use` lowers to `IR_SUCCEED`, so
the harness layer the ceo suspected (ref cutting, fixture staging, rakudo invocation) is **not** the defect.
The staging is correct; the parser genuinely cannot read the files.

## 3. ⭐⭐ THE PART THAT CHANGES HOW THIS IS ATTACKED: THE HISTOGRAM IS A QUEUE

The obvious next move is to rank the blocking constructs and cure the top one. The instrument's own top line
is `use lib $*PROGRAM.parent(4).add: 'packages/Test-Helpers';` — **59 files**, four times the next entry,
and it is the standard roast preamble, so it looks like textbook leverage: one no-op cure, 59 files unlocked.

**Measured by ablation instead of assumed: delete that line from all 59 files and re-run.**

- **57 of 59 still parse-fail**, on ~40 different next constructs.
- 2 reach neither TAP nor a parse error.
- **0 move into a graded bucket.**

The cure would have been defensible from the histogram alone, would have looked like progress, and would
have bought **nothing measurable**. I came within one edit of spending the sitting on it — the grammar work
was scoped and the regeneration path checked before I thought to ablate.

⭐ **The reusable rule: a first-error histogram ranks what each file hits FIRST, which is not what is BLOCKING
it.** Curing the head of the list advances those files to their next error. Frequency tells you where the
queue is *long*; value lies where the queue is *short behind it*, and those are different lists. The only
honest unlock metric is ablation — *how many files become GRADED when this construct works* — which means
removing it and re-running, never counting occurrences. The runner now prints this caveat on every run,
beside the histogram, with the measurement, so the next reader cannot take the list for a work plan.

This is the same family as the several instruments this fleet has caught this week answering a narrower
question than the one asked (`command -v` for existence, `$?` after a pipeline, md5 of the driver for a
frontend change, a stale-artifact count read as an attribution). Here the instrument is correct and
complete, and it is the *inference from a correct reading* that is wrong.

## 4. WHAT THIS MEANS FOR THE ROW

Roast is a **broad, flat parser-coverage gap** — a long tail with no block-unlock anywhere in it — and not a
small number of missing constructs. Any plan promising a large roast jump from a handful of cures should be
disbelieved until an ablation backs it. The honest next step is to pick the ablation-ranked head of the
list, not the frequency-ranked one, and to expect the row to move slowly and truthfully.

⛔ Nothing here moved a denominator or excluded a case: every shipped file is counted and classified.

## SEE ALSO

- `scripts/raku_roast_scoreboard.sh` — `--inventory`, and the guard seam.
- `FINDING-2026-09-14-hq_T-a-program-that-must-refuse-to-compile-has-no-pass-shape-in-the-m4-arm.md`.
