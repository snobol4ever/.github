# The ONE ref-cut door is behind the board guard, so the rule that forbids re-deriving the oracle invocation is unreachable

**hq_B, 2026-09-13, measured while building the CEO-706 driver generator.**
**Status: a FLIP for the coo (the one runner owns `scorecard_snobol4.sh`), not an hq_B landing.**

## The measurement

```
$ bash scripts/scorecard_snobol4.sh oracle gimpel <path>/AI_driver.sno /tmp/out
⛔ REFUSE(2) ONE RUNNER, ONE BOARD: scorecard_snobol4.sh is a board and seat hq_B is not the coo.
rc=2
```

`scorecard_snobol4.sh`'s `oracle` verb runs **one program**, writes **no** `results.tsv`, publishes
**no** board and writes **no** `SCORE.md` row. It is refused anyway, to every seat but the coo,
because line 2 of that script calls `one_runner_guard "${0##*/}"` with **no `suite_path`** — and with
no suite_path the guard judges the run a board and refuses. The guard fires before the verb is
dispatched, so it cannot tell `run` from `oracle`.

## Why that is a contradiction rather than a preference

The criterion is the guard's own, stated in `lib_subject_tree.sh`'s sibling `lib_one_runner.sh` under
ceo CEO-547 part 1, verbatim:

> **WHAT MAKES A RUN A BOARD IS THE POPULATION IT GRADES, NOT THE ENTRY POINT.**

The `oracle` verb's population is one program. By the guard's own rule it is not a board. The guard
refuses it because of *where it is invoked from* — which is the entry point, the exact thing the rule
says does not decide. The `one` verb (one program, `[N]` repetitions) is in the same position.

⛔ **And the seam that exists for this does not reach.** `one_runner_guard` has a deliberate
suite_path exemption — *a suite_path outside the corpus tree is not a board* — but every program this
verb exists to cut a ref for **is inside the corpus tree**, so the exemption is structurally
unavailable to exactly the callers it would help.

## What the refusal actually costs, which is the part that matters

`cmd_oracle` was written for one purpose, and its own header says so:

> ⛔ THIS EXISTS SO A `.ref` CAN BE MINTED THROUGH THE SAME DOOR THE BOARD GRADES THROUGH. `run_one`
> runs the oracle and then THROWS THE OUTPUT AWAY, so any tool that wants to RECORD the oracle answer
> had to re-derive the invocation — and a `.ref` minted under a different cwd, lib path, stdin or flag
> set than the board grades with **is a pin that can never match**.

That is seat5's s191 conviction, paid for twice in one session: *a census is a harness; copy `run_one`,
never re-derive it.* So the situation today is:

- the law says **never re-derive the oracle invocation**;
- the single sanctioned way to obey it is **refused to twelve of thirteen seats**;
- and CEO-706 asks four lanes to cut **~900 refs**.

⭐ **A closed door does not stop the work, it relocates it.** A seat under a rank-0 brief to cut
refs, finding the one sanctioned door shut, will write its own three-line `SETL4PATH=... sbl -bf ...`
— which is not laziness, it is the only remaining way to do the job it was given. And that produces
precisely the failure `cmd_oracle` was built to prevent, at ~900× scale, with every pin looking
perfectly reasonable until a board grades it. **The guard's cost is not a refused command; it is a
class of un-matchable refs authored in good faith.**

## What I did instead, and why it is not a cure

`util_gen_library_driver.py` calls the ONE door and passes `S4E_ONE_RUNNER_OVERRIDE` with a stated
reason ("ONE program through the ONE oracle door; grades no population, writes no SCORE row"). That
is the sanctioned, loud, recorded seam and it is the right choice over re-deriving the invocation —
but it is **not** the fix:

- it makes every ref cut print a ONE-RUNNER OVERRIDE warning, so a mechanism reserved for a
  deliberate, rare, named exception becomes routine background noise on ~900 invocations. ⛔ **A
  loud channel used 900 times is a quiet channel.** The next seat who genuinely overrides a *board*
  will be invisible in the same stream.
- and it pushes a line onto the script's stdout ahead of the status TSV, so every caller must parse
  the *last* line rather than the only one — a parsing contract created by a guard, not by a need.

## The cure I am asking for (FLIP, coo)

Call the guard **per verb**, not on line 2: `run` and `report` are boards and keep the refusal;
`one` and `oracle` grade one named program and are development aids. One line moves, the guard's
stated criterion starts being the criterion, and ~900 refs get cut through the door the board grades
through with no override noise and no re-derivation.

⛔ I am **not** landing it. `scorecard_snobol4.sh` is the one runner's instrument and under MODE line
2 a change to a node another concern owns is an ASK with the measurement, never a landing — the same
rule the coo cited to me an hour earlier when it declined to fix a one-line blocker in *my* lane and
sent it to me instead. This file is the measurement.

## The reusable half

⭐ **A guard that decides from the entry point cannot enforce a rule about the population, and it
will read as correct for as long as nobody needs the cheap verb.** This one has been right about
`run` every single time it fired. Its blind spot is not a wrong answer; it is a question it never
asks — the same narrow-instrument shape as `command -v` answering *is it on PATH* when the reader
meant *does it exist*, and as `$?` after a pipeline answering about `head`.

⭐⭐ **And the sharper half: when a guard shuts the only sanctioned route to a mandated task, the
mandate wins.** The work still has to happen, so it happens the unsanctioned way, and the guard's
own log stays clean — it refused, correctly, and recorded nothing about the hand-rolled invocation
that followed. **A guard cannot observe the workaround it causes.** So the question to ask of any
blocking guard is not only "is this refusal right?" but "what will the person do next, and will I
be able to see it?"

## Provenance

- SCRIP `b81614509`, `0f0ccd138` (the generator and its row census).
- `scripts/util_gen_library_driver.py`, function `oracle_once` — carries this finding in situ.
- Guard: `scripts/lib_one_runner.sh`, `one_runner_guard`; caller: `scripts/scorecard_snobol4.sh:2`.
- Door: `scripts/scorecard_snobol4.sh`, `cmd_oracle` (its own header is quoted above).
