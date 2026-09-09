# A CENSUS THAT NAMES FILES ACCUSED THREE INNOCENT ONES, AND THE MECHANISM IS NOT FOUND

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
| `grep -q` exits early → SIGPIPE kills the upstream `grep -vE` → `pipefail` makes that the verdict | every candidate file is **under 5KB** comment-stripped, and **0 of 140** exceed the 64KB pipe buffer, so the upstream grep always completes and exits 0 |
| fork failure / process-table pressure under load | the **sibling** census `gate_file_executes_scrip` forks *more* per file and reported `gates=140` in **every** run, including both red ones |
| the population wobbled | same — `gates=140` was constant across all twelve runs |
| an earlier arm rewrites files under `scripts/` | no in-place writes to `scripts/` anywhere in the gate |
| my own landing caused it | A/B: 1 red in 3 runs with the new probe, 0 in 3 without — then **8 consecutive clean runs with it on**. Not attributable either way, and the accused files have nothing to do with the change |

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

## OPEN

The mechanism. Whoever meets `UNMEASURED:` in an ARM 15 output has the recurrence this could not reproduce on demand
(twelve runs, three reds, none summonable) — **capture the file and the surrounding run before re-running**, because
re-running is what made this one vanish twelve times.
