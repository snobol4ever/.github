# FINDING 2026-09-12 hq_T — moving a population blinds every instrument that derives it, and the gate stays green

**Measured while landing CEO-582** (`make test` loops and reports instead of aborting on the first red).
Tree: SCRIP `c4bdb475c` + the landing commit; corpus `227c678dd`; .github `7724941b`.

## The number

| derivation | before the restructure | after it, uncured | after the cure |
|---|---|---|---|
| `util_gate_wiring.py reachable()` — scripts `make test` runs | **292** | **103** | 294 (292 + the 2 new files) |
| its doubles walk — targets examined | `test`, `test-postoffice` | `test` | `test`, `test-sequential`, `test-postoffice` |

**189 gates would have read as run by nothing.** `test_gate_gate_wiring_ratchet.sh` — the instrument whose
entire job is to know which gates are wired — **printed `GATE PASS(0) ... (examined 28)` while blind.**

## What happened

`make test` was one target of ~155 recipe lines and make aborts on the first failing line, so a red at arm 15
killed the set 24s in and 131 arms never executed (cfo's census, CEO-582: eight non-green reported as one).
The cure makes `test:` a single line — `bash scripts/run_blocking_set.sh` — and the arms are now declared as
the recipe lines of a new `test-sequential:` target that the driver reads.

`util_gate_wiring.py` derives the wired set from `make -n test`. The moment the population moved one target
sideways, that expansion stopped naming it. Nothing errored. The instrument answered a narrower question than
the one it was asked, and — as always — it did not say so.

## The general form

⭐ **A target that DELEGATES its population is the same fact as a target that reads its population from a
FILE, and this very file already carried the lesson in that form.** `reachable()`'s own docstring says it:

> the moment a target reads its population from a file, EXPANDING THE RECIPE STOPS ANSWERING THE QUESTION YOU
> ASKED

— written after `make preflight` moved its arms to `scripts/preflight_arms.txt` and this instrument
"confidently called 22 of them run by nothing." The author filed the lesson as a fact about **files**. The
next move was a **target**, and the lesson did not reach it. That is the same decay this org keeps
re-measuring: *the address was kept and the shape was not.* (Cf. the `corpus/crosscheck/` glob lesson, filed
as a fact about one directory and nearly deleted with it.)

⛔ **And the detection half is the sharper one: re-running the gate and reading its colour could not find
this.** The ratchet was green before, green after, and blind in between. What found it was deriving the
number **on both trees and diffing** — `git stash`, re-derive, `git stash pop`. A population that silently
shrinks always shrinks in the comfortable direction, because fewer things examined means fewer things wrong.

## The rule this is offered as

**When a landing MOVES a population — to another target, another file, another runner — sweep every
instrument that DERIVES that population, and grade each one by re-deriving its count before and after, never
by re-running it and reading the verdict.** A derived census cannot tell you it lost its input.

The cure here is `DECLARATION_TARGETS = {"test": "test-sequential"}` in `util_gate_wiring.py`, with two
guards that are each load-bearing: the declaration target is followed **only if the Makefile declares it** (a
scratch fixture whose `test:` carries its own arms must not refuse, or the selftest dies), and it **inherits
the entry's requiredness** (a missing `test-sequential` must REFUSE, never slip into the skipped-and-named
bucket — that would drop 189 gates while the header reported only a skipped target).

## Neighbours

- `FINDING-2026-09-11-hq_V-a-source-level-assertion-is-not-a-measurement-of-behaviour.md` — the other half of
  the same week: hq_V's gate grepped for a correctly-spelled form, the form was spelled correctly, and the
  caller one frame up defeated it. Mine is an instrument blinded by what moved; theirs is an instrument that
  never watched the thing move. Both read green. `test_gate_make_test_loops_and_reports.sh` is written
  against that finding: it builds a scratch Makefile with a red at arm 2 of 4, runs `make test` through it,
  and **counts the arms that ran from the filesystem** rather than parsing a summary the driver wrote about
  itself.
- `RULES.md` § TRANSCRIPTION IS WHERE PROVENANCE DIES — the same disease in the copying direction.
- The denominator law: the cure's summary line prints `green + red + refused == arms` and REFUSES rc=2 when
  it does not close, so a run that dies partway can never again read as a clean one. That is the arm of the
  new gate that fires **no matter where** the loop stops.
