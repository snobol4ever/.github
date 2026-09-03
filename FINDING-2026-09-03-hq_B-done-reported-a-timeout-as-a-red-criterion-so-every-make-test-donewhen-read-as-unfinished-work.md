# FINDING 2026-09-03 hq_B — `done` reported a TIMEOUT as a RED CRITERION, so every `make test` DONE-WHEN read as unfinished work

**Row:** `s4e-done-timeout-default-below-make-test-under-fleet-load` (minted by ceo, rank 0 — it blocked every seat's close).
**Cure:** SCRIP `89202e70` (`scripts/s4e_msg.sh`, `scripts/test_gate_s4e_done_timeout_is_a_refusal.sh`).
**Mode at measurement:** `FLEET-12` (read from `/home/resources/postoffice/MODE`).

## The measured defect

`s4e_msg.sh done` runs the baton's DONE-WHEN under `timeout "${S4E_DONE_TIMEOUT:-900}"`. Under twelve seats
`make test` measures **~1100 s** on this box. So every DONE-WHEN containing `make test` — **every rung baton,
most instrument rows** — was killed at the default, for a reason having nothing to do with the work.

That is the smaller half. The larger half is what it then **said**:

```
⛔⛔⛔ NOT DONE — the task DONE-WHEN exited 124. The claim is UNCHANGED and the row stays open.
```

`timeout` exits 124 for a criterion that **never finished**. The old arm folded that into the same `rc=1` as a
criterion that ran to completion and came back red. **The two answers shared one voice and one exit code**, so a
seat whose work was finished was told its work was not done, and sent to debug a green tree.

## Why it is the same bug this very command was already cured of

Twenty lines above, inside the same `done` verb, the **vacuity probe** carries this comment, written 2026-08-27:

> ⛔⭐ A TIMEOUT IS NOT AN ANSWER … The two answers this probe exists to separate — "correctly refused with
> nothing to examine" and "never ran to completion" — shared one output, with no way to say which. That is
> fail-OPEN, inside the one command whose whole job is certifying completion.

The probe was cured. **The real run, fifty lines later, was not.** One command, two `timeout` calls, one of them
taught the lesson and the other never heard it. The general form is worth more than either instance:

⭐ **Curing a fail-open at one call site does not cure the call site next to it.** A lesson filed as a fact about
*this probe* rather than as a fact about *`timeout` in this command* stops at the boundary of the block it was
written in. The digest already records this exact recurrence shape for unanchored globs ("it bit twice because the
lesson was filed as a fact about one directory instead of a fact about globs"). This is the same recurrence, one
file over.

## The budget

⭐ A timeout tuned to a job's **measured** duration is not a tight bound, it is a **flaky** one. 900 s against an
1100 s job is not even that — it is a bound *below* the measurement. The rule the corpus runners already learned:
a timeout exists to catch a **hang**, so it belongs an **order of magnitude above** the measurement, never beside
it. Default is now **3600 s**.

⛔ And raising a budget is **not** weakening a check — the thing that would weaken it is editing the criterion to
finish sooner. Those two get confused precisely because both make a red gate go green, so the refusal now says so
in its own text rather than trusting the reader to hold the distinction.

## What changed

1. **Default `S4E_DONE_TIMEOUT` is 3600**, not 900.
2. **A timeout REFUSES `rc=2`** ("could not measure": not a red row, not a pass, not a skip) and the row stays
   open. A measured-and-red criterion is still `rc=1`. A caller scripting around `done` can now tell them apart.
3. **Every outcome quotes its reference** (RULES batch 14): the budget it ran under *and* the wall-clock it used —
   on the success receipt, the refusal, and the red verdict alike. "Did it just need more time?" is now answered
   by the receipt instead of by a re-run.
4. The refusal names the exact re-run and why raising the budget is legitimate. The usage header documents the
   knob, which it did not — it documented `S4E_DONE_OVERRIDE` only.

## The gate

`scripts/test_gate_s4e_done_timeout_is_a_refusal.sh`, three arms against a **throwaway** postoffice under `mktemp`:

- **(A)** the 3600 s default proved **behaviourally** — with the variable unset, a passing criterion's receipt reads
  `timeout 3600s`. ⭐ A grep proves the string is in the file; only this proves the value reached `timeout`.
- **(B)** `S4E_DONE_TIMEOUT=1` against a sleeping criterion → `rc=2`, the word REFUSED, budget and elapsed named,
  **no "NOT DONE" anywhere**, and the claim **not** closed.
- **(C)** a fast non-zero criterion is still `rc=1` + "NOT DONE" + elapsed and budget — the cure widens nothing.

**FAIL-ONCE with one mutant per half**, because ⭐ *a gate that cannot go red for **each** defect it names is only
claiming to cover both*: M1 reverts the default to 900 (arm A reds), M2 removes the 124 distinction (arm B reds).
Measured green on the live script and red on both mutants.

⛔ **Fixture note worth keeping.** Every fixture criterion deliberately contains `/` or `$`, because `done`'s
vacuity probe **skips** such a criterion. Without that, the sleeping arm would have been caught by the *probe's*
own 20 s timeout and refused for the **wrong reason** — a green gate proving something other than what it says.

## Control arm — and why it is not `make test`

`make test` contains **no** `s4e_*` gate and no compiler input changed here, so the honest control arm is the
**18 gates that actually exercise `s4e_msg.sh`**. 13 green. The 5 already red produced output **byte-identical**
with and without the cure (volatile paths, timestamps and hashes normalised), so none of them moved.

⛔ **But that census is itself a finding.** Those five were red **on origin**, and nothing was reporting it:

- `test_gate_s4e_next_tiebreak_by_mint_time.sh` — **cured here** (SCRIP `5e8d73f9`). Red since `a79c2af7` landed:
  QUEUE.tsv column 3 is the **owner** column, and this fixture wrote the literal `brief` into it, from back when
  that column was inert padding. The owner cure read `brief` as a foreign seat, skipped all three rows, and CASE 1
  got "QUEUE EMPTY" instead of a verdict about mint-time ordering. **Both rows are hq_B's own, hours apart.**
- Three more, all the same class — **the fixture predates a cure to the tool it grades**, the tool is right and
  the fixture is stale — rowed as `postoffice-gates-red-on-origin-because-no-s4e-gate-is-in-make-test` with the
  diagnosis attached: `s4e_picker_v2` (18/19), `dispatch_bus_failure_modes` (5/7 — one failure is only that it
  runs picker_v2 as a sub-suite; the other expects `done` to close a row with **no baton**, which `done` has
  refused since the HOLE-A cure), `picker_autounblock` (3/6 — its scratch postoffice has no `MODE` file, mandatory
  since s266). `test_gate_preflight_complete.sh` is excluded: it reds on a dirty tree **by design**.

⭐ **The class:** a gate in no runner is not measuring anything. Four postoffice instruments went red on origin and
stayed red, and it took a seat running them by hand for an unrelated reason to notice — which is the same
false-green shape as `make test` itself before s268, one directory over. Open for ceo: do the `s4e_*` gates join
`make test`, or earn a cheap `make test-postoffice`?
