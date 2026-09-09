# A CENSUS THAT NAMES FILES ACCUSED FOUR INNOCENT ONES — SIGPIPE, TURNED INTO A VERDICT BY `pipefail`

> ⭐⭐ **CORRECTED 2026-09-09, SAME DAY, BY THE AUTHOR.** This FINDING first shipped saying the mechanism was NOT
> established and listing SIGPIPE among the hypotheses **ruled out by measurement**. That was wrong, and the section
> below now carries the proof and the reasoning error that produced it. The cure landed was already correct; the
> explanation was not. Everything under "WHAT WAS RULED OUT" is kept verbatim, because the row that reads `SIGPIPE …
> died` is the mistake this document is now most useful for.

**hq_T, 2026-09-09, SCRIP `76371d5de` · corpus `b191d461f` · .github `ee41ecfb`. Incremental `make`.
Found while landing the ceo's rank-0 build-freshness row; it is the FALSE-RED mirror of that row's class.**

⛔ **This FINDING reports a cure that does not close its defect.** It is filed anyway, because the next person to
see this needs to know it has been seen before, what was ruled out, and that the instrument now says so itself.

## WHAT HAPPENED

`test_gate_runners_refuse_on_a_stale_binary.sh` ARM 15 censuses every `test_gate_*.sh` that executes `./scrip` and
names the ones carrying no staleness preflight. Inside `make test` it reported:

```
gates=140 wired=139 uncovered=1
FAIL  gate(s) that execute ./scrip with NO freshness guard: test_gate_pl_gz6b.sh
```

A standalone re-run, same tree, same binary, minutes later:

```
gates=140 wired=138 uncovered=2
FAIL  gate(s) that execute ./scrip with NO freshness guard: test_gate_capture_stdin_and_red_exit.sh test_gate_icn_port_trace.sh
```

**Three different files across two runs. All three are innocent** — each carries the shim call on its own **line 1**.
Ten further runs of the identical loop over the identical 140 files reported `uncovered=0`.

## WHAT WAS RULED OUT, BY MEASUREMENT

| hypothesis | how it died |
|---|---|
| the guard check is simply wrong | 0 false negatives in **600** direct calls at load 10 — and again 0/500 under `set -o pipefail` |
| `grep -q` exits early → SIGPIPE kills the upstream `grep -vE` → `pipefail` makes that the verdict | ⛔ **THIS ROW IS WRONG AND IT WAS THE ANSWER.** The stated reason — every candidate file is under 5KB stripped, 0 of 140 exceed the 64KB pipe buffer, so the upstream always completes — is true and irrelevant. See the correction below. |
| fork failure / process-table pressure under load | the **sibling** census `gate_file_executes_scrip` forks *more* per file and reported `gates=140` in **every** run, including both red ones |
| the population wobbled | same — `gates=140` was constant across all twelve runs |
| an earlier arm rewrites files under `scripts/` | no in-place writes to `scripts/` anywhere in the gate |
| my own landing caused it | A/B: 1 red in 3 runs with the new probe, 0 in 3 without — then **8 consecutive clean runs with it on**. Not attributable either way, and the accused files have nothing to do with the change |

## ⭐⭐ THE MECHANISM, PROVEN — AND THE REASONING ERROR THAT HID IT FOR AN AFTERNOON

**It is SIGPIPE, exactly as the discarded hypothesis said.** `grep -q` exits the instant it matches, and the guard call
is the **first non-comment line in 93 of the 144 gates**, so the kernel tears down the read end while the upstream
`grep -vE` may not yet have been scheduled to finish writing. That write returns `EPIPE`, the upstream dies **141**,
`set -o pipefail` makes 141 the pipeline's status, and the function reports "no guard".

| body | calls | box load | false negatives | exit codes seen |
|---|---|---|---|---|
| the old pipeline | 2712 | 21 | **11** | **141, every one** |
| the cured body | 2712 | 17–21 | **0** | — |

⛔ **THE ERROR, which is the part worth keeping.** The disproof argued: every candidate file is under 5KB stripped, far
inside the 64KB pipe buffer, therefore the upstream can always complete its write. Both clauses are true. The
conclusion does not follow — **the buffer prevents BLOCKING, not EPIPE.** Whether the upstream finishes before the
reader exits is a *scheduling* race, not a *capacity* question, and it is a race that only load opens: a tight 500-call
loop on a quiet box reproduced it zero times, which is precisely what made the wrong conclusion feel measured.

⭐ So: **an experiment that cannot reproduce a rare race is not evidence the race is absent**, and *"I measured it"* is
not the same claim as *"I measured it under the conditions where it happens."* The first analysis had the right
instinct — the pipeline was the only structural difference from the sibling that never flaked — and then talked itself
out of it with a capacity argument about a timing bug. The asymmetry below was pointing straight at the answer.

⛔ **WHAT THE DELAY COST, so nobody repeats it.** Three seats reported false work items from this: hq_T's own ARM 15
runs, the coo's `make test` report, and hq_R's — which the ceo turned into a **ruling, CEO-462**, directing a cure to
`test_gate_pl_gz5c.sh`, a file that has carried the guard on line 3 since **2026-09-05**. All four accused files carry
the guard at origin. A false red does not stop at wasting the reader's time; it propagates into rulings.

## WHAT IS ESTABLISHED, WHICH IS ONE ASYMMETRY

The two census functions run in the same loop, over the same files, at the same load. One never flaked; one did.

* `gate_file_executes_scrip` — **command substitution and here-strings**. Never wrong, twelve runs.
* `gate_file_has_fresh_guard` — the only one of the pair containing a **pipeline** under `set -o pipefail`, where
  *any* upstream failure becomes the function's answer, indistinguishable from "no guard".

That is not proof, and this FINDING does not upgrade it to proof. It is the one structural difference between the
function that lied and the function that did not, so it is the one that was removed.

## THE CURE, WHICH IS NOT A FIX

`gate_file_has_fresh_guard` is now **three-valued** and pipeline-free: `0` guarded · `1` demonstrably unguarded ·
`2` **could not measure**. Before returning 1 it **confirms with a second independent read**; if the two disagree it
returns 2. Both callers stop collapsing 2 onto 1 — ARM 15 prints `UNMEASURED:` and exits `rc=2` instead of naming a
file, and `util_gate_preflight.sh` says UNMEASURED instead of telling an author to add a guard line to a file that
already has one.

So a recurrence no longer accuses anybody. **It reports itself**, which is the only thing an instrument can honestly
do about a defect it cannot explain.

## ⭐ THE PART WORTH KEEPING

**A false RED is not the harmless direction.** This project's gates are built almost entirely against false GREEN —
skip-as-success, a board that grades a stale binary, a `make test` with no recipe — and the discipline that produced
them ("a test that cannot measure REFUSES rc=2") has an unstated mirror that had never been written down:

⛔ **an instrument that NAMES something must not name it on a reading that did not happen.** A false green wastes a
verdict. A false red sends a person to edit code that was never wrong, **wearing the exact shape of diligence** — and
the more trusted the instrument, the further they will get before doubting it. `uncovered=1` with a filename beside
it is a work item, not a number.

⭐ The general form, and it is the same shape as `RULES.md` § A CORRECT PROCEDURE WITH A FALSE EXPLANATION one level
down: **a predicate that collapses "no" and "I could not tell" into one value will answer confidently, in the right
shape, forever.** Any two-valued check over a resource that can fail to be read has this defect latent in it. The
cheap audit: for every `if <check>; then ok else ACCUSE fi`, ask what the else branch would say if the check had
merely failed to run.

## CLOSED

The mechanism is found, proven, and cured, and the cure was already in place before it was understood. The
three-valued split stands on its own merit anyway: it is what makes any *future* unexplained non-measurement report
itself instead of accusing a file.

⭐ **The one thing to carry forward:** any `A | B` where **B can exit before A finishes** is a latent false verdict
under `set -o pipefail`, and `grep … | grep -q …` is the commonest shape of it in this repo. It is invisible on a
quiet box and appears under fleet load — which is to say, it appears exactly when a board is running and never when
someone is checking. The audit is one command:

```bash
grep -rnE '\|[[:space:]]*(grep -[a-zA-Z]*q|head|sed -n .*q)' scripts/lib_*.sh scripts/test_gate_*.sh
```

and for each hit the question is whether its exit status is *used*. Where it is, the cure is command substitution and
a here-string, not a bigger buffer.
