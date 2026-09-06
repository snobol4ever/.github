# FINDING: a BLOCKING gate read 3-of-5 because its mutator raced a blind `sleep 2` against a 1821ms run

Measured 2026-09-06 by hq_T, on hq_B's report. Gate:
`SCRIP/scripts/test_gate_progress_rows_carry_the_start_fingerprint.sh`, wired into `make test`
(Makefile:187). Cure: SCRIP `b6d2ae3f7`. **No product code changed.**

## The shape

Arms 3, 4 and 5 each assert that a run whose ground moves mid-flight appends ZERO rows and exits 2.
Each did it like this:

```sh
( sleep 2; <mutate the binary / move a HEAD> ) &
rc=$(run_harness "$W/b" "$W/b/db.tsv")
```

The scratch world is 8 trivial programs. **That run measures 1821ms.** The mutator sleeps 2000ms. So
the mutation lands after the append about as often as before it, and when the run wins the race the
ground never moved during it: rows are written, rc=0, and the arm reports a failure that is really a
statement about **box load**.

## Why it survived so long, and why two seats disagreed

* On origin it read 3/5, so `make test` was red for **every seat**, on a file none of them touched.
* hq_B measured arms 3, 4 and 5 red. An hour later on the same tree I measured arm4 **ok** and arm5
  **FAIL** — then arm4 FAIL twice more in a row. ⭐ Two competent seats, same tree, different arms:
  that disagreement was the tell, and it was read as "the gate is red" by both of us rather than as
  "the gate is not a function of the tree."
* I compounded it: my first reading said the gate was **not wired at all**, because I ran
  `make -n test-postoffice` on a tree **27 commits behind origin**, where the wiring commits
  (10a811868, 5a6dc4ff4) simply did not exist. I parked the row on that reading. ⛔ A census taken on
  a stale tree answers a question about a tree nobody has — the same class as the stale-binary
  refusal, one level up.

## What was NOT wrong

`util_progress_append.py` and `corpus_suite_harness.py` were correct throughout: `pin_context()` reads
the tree hashes and the driver+RT digest before the first program is graded, and
`assert_ground_unmoved()` is called by `append_rows()` before any write. **arm4 passing even once
(rows=0 rc=2) was proof the refusal worked** — and that datum was sitting in the output the whole time,
read as noise.

## The cure, and why not the obvious one

Growing the scratch suite was rejected on measurement: 8 → 120 entries moves the run only
1821ms → 2498ms, because nearly all of it is fixed startup. Widening a race you do not control is not a
fix, it is a longer odds bet.

`wait_grading()` polls (50ms, 30s cap) until the scratch `scrip` binary has been **executed at least
once**, which proves `pin_context()` has already run, since the harness pins before grading the first
program. Every mutation is then strictly ordered between the pin and the append — the property the arms
were always trying to assert, now stated rather than gambled on.

## Proven both directions

5/5 arms ok, four consecutive runs with arms 3/4/5 green every time. And **proven to still fail**:
against a mutant that early-returns out of `assert_ground_unmoved()`, the gate drops to 2/5 with
exactly arms 3/4/5 red. Mutant reverted, tree clean. A gate that cannot fail is not a gate.

## ⭐ The general form

**A test whose verdict depends on winning a race reports the machine, not the code** — and it reports
it in the vocabulary of a real defect, so every reader spends their time on the wrong tree. The tell is
never the red itself; it is **two runs of the same gate on the same tree disagreeing**. When that
happens, stop diagnosing the subject and go read the instrument's own timing. A fixed `sleep` beside a
measured duration is the same defect as a `timeout` tuned to a job's measured runtime: not a tight
bound, a flaky one.
