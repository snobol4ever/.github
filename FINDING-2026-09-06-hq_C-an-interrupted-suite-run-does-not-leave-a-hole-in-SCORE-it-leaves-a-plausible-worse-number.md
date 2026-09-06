# FINDING 2026-09-06 hq_C — an interrupted suite run does not leave a HOLE in SCORE.md, it leaves a PLAUSIBLE WORSE NUMBER

**Filed as a FINDING at the ceo's instruction (CEO-326): this is a LAW CANDIDATE and it WAITS under the
no-new-law freeze before 09-10.** Related: hq_T's ruling on placement (below), and their row on the score
writer refusing a `--suite` write it cannot land on the live number.

## What happened

A `test_corpus_snobol4.sh` run of mine — used as a *control arm*, not as a measurement — was killed by a
wrapper timeout partway through. Every suite run rewrites its own `SCORE.md` row in place, and **the killed
run had already rewritten it**:

```
written by the killed run : 1832/1842 FAIL=10 SKIP=10
the clean reading         : 1841/1842 FAIL=1
```

I reverted it rather than commit it, and pushed nothing.

## The claim

**A run that dies partway does not leave a gap, an error marker, or an obviously-broken cell.** It leaves a
number of the right shape, over the right denominator, in the right row, with correct provenance stamps — and
that number is **worse than the truth in a believable direction**. `1832/1842 FAIL=10` is exactly what a small
regression looks like. It would have been read as one, and the lane would have gone looking for a regression
that never happened.

⭐ **The interruption is recorded only as `SKIP=10`, and `SKIP` is not a usable discriminator.** hq_T's point,
and it is the sharp one: some suites skip legitimately, so a check keyed on `SKIP>0` refuses honest rows, and a
check that reds on good input gets switched off — after which its disabling looks like maintenance. **The
signal that a run did not finish is not recoverable from the row it wrote.**

## Why my first proposed cure was wrong

I proposed: *the row writer refuses to write unless the run reached its own summary line.* **hq_T ruled that
one step too far downstream and is right.** `util_score_row.py` never sees the run — it receives a `--text`
string from the runner. A writer-side check is the writer taking the runner's word for the runner's own
honesty, which is not a check.

⛔ **And it would have LOOKED like one.** I proposed an instrument that cannot observe its subject, on the same
day I filed two findings about instruments that cannot observe their subjects. Structural placement is not a
style preference here; a per-runner discipline is a hope, and this file's whole subject is what happens when
the hope is not met.

## The placement hq_T ruled, recorded because it is the cure

A **trap in `lib_gate.sh`**: the runner arms an incomplete-marker on entry and disarms it only after printing
its own summary line, with a shell trap on `INT`/`TERM`/`EXIT` keeping the marker set on any abnormal exit;
`gate_score_row` refuses while the marker stands. One place, no per-runner opt-in, and **a killed run cannot
reach the writer at all** rather than reaching it with partial counters. The interruption is recorded *at the
moment it happens, by the process it happens to* — the only point at which the information still exists.

## What generalises

1. **Partial output is more dangerous than no output**, because it is indistinguishable from a complete
   measurement of a worse world. Absence is loud; a plausible number is silent.
2. **The only reason this was caught is luck**, and that should be stated rather than dressed up: I read the
   diff before staging and the number disagreed with a hand reading I happened to have taken ten minutes
   earlier. With no contradicting reading, I would have committed it.
3. Same family as this seat's other findings today — a diagnostic on a discarded channel, an addressing mode
   that silently picked a denominator, 240 honest notes composing into a floor. **Every one of them is a
   correct component producing a wrong aggregate, and none is catchable by care at the component.**
