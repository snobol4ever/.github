# FINDING — the SNOBOL4 board could not say NO, and a moved file was invisible to it

**Seat:** `hq_C` (HQ-CORRECTNESS) · **Session:** s272 · **Date:** 2026-08-24 · **Mode:** FLEET-8
**Cure:** SCRIP `9873fe6e` · **Reported by:** seat04 (`q-corpus-demo-path-mismatch`) — this seat measured, cured and negative-tested it.

## THE CLAIM

`test_corpus_snobol4.sh` — the primary SNOBOL4 correctness board, and a member of the blocking set — carried
**two independent false-greens at once**. Both are cured and both are negative-tested in both directions.

| | before | after |
|---|---|---|
| a hardcoded corpus path stops resolving | silently dropped: **no PASS, no FAIL, no SKIP** | **rc=2, every missing row named** |
| mode-4 reports failures | **exit 0** | **rc=1** |
| green | exit 0 | rc=0, `MISSING=0` printed |

## DEFECT 1 — `run_test()` RETURNED SILENTLY ON A MISSING FILE

```
[ ! -f "$ref" ] && return
[ ! -f "$sno" ] && return
```

The board feeds `run_test` from three places. Two are **discovered** — `crosscheck` by `find`, `beauty` by glob —
and both filter a ref-less `.sno` *before* calling it, so for them a missing file is a legitimate "no oracle, not
a test". The third is **~40 hardcoded demo rows**. For those, a path that stops resolving is always a defect, and
those two lines made it **invisible**: the program simply left the denominator with no signal of any kind.

⭐ **This is the shrunken-denominator class, and it is the most dangerous shape a board has: a clean numerator over
a denominator nobody is watching.** `FAIL=0` reads as success in every log, dashboard and banner.

⛔ **The frequency is the real finding.** The demo paths were repointed **five times in one day** — `6ce46ebc`,
`dac73079`, `843cacfb`, `1177e66e`, `50923f55` — and **every single break was caught only because a human
recognised that the printed total had shrunk.** That is not an instrument; that is a person doing an instrument's
job from memory. It is also why three different SNOBOL4 totals (360, 362, 364) were each measured green on
2026-08-24 as the corpus moved underneath them.

⛔ **My own s271 hardening did not catch it, and the reason is the transferable part.** That guard REFUSES when
`$DEMO` or `$BEAUTY` is not a directory. It was written against the failure I had just seen — a *subtree* that
moved — and it is blind to the failure that followed: the subtree exists, and the **files inside it** re-nested.
A guard written against the last outage checks for the last outage.

## DEFECT 2 — THE SCRIPT NEVER EXITED NON-ZERO

The final statement was a `printf`. **The board exited 0 with any number of mode-4 failures.** `CLAUDE.md` has said
*"mode-4 is the hard gate"* throughout, and nothing anywhere enforced it — the same structure as the documented
`make test` false-green trap (a `.PHONY` target with no recipe), sitting inside the blocking set itself.

Now: **rc=0** green · **rc=1** real mode-4 failure · **rc=2** refused. m3 stays informational per the documented
contract, but is printed in the verdict line so it cannot hide.

## THE MEASUREMENT — NEGATIVE-TESTED IN BOTH DIRECTIONS

`make pristine`, `RT_OPT=-O0`, SCRIP `9873fe6e`, corpus `e6c0d6b72`. Re-proven after the rebase that landed it.

| run | rc | printed |
|---|---|---|
| green | **0** | m3 362/362 FAIL=0 · m4 362/362 FAIL=0 · SKIP=0 · MISSING=0 |
| `DEMO` pointed at an empty tree | **2** | 22 rows named, each with the path that failed |
| **the OLD script, same broken `DEMO`** | **0** | **`PASS=340 FAIL=0`** |
| one `.ref` deliberately wrong | **1** | denominator **held at 362**, `demo_hello` named in both modes |

⭐ **Row 3 is the whole bug, measured.** Same input, same tree: the old board reported a confident, entirely green
`PASS=340 FAIL=0` while 22 programs had left the corpus. The 22 is exactly the count seat04 predicted.

## THE RULE

⛔ **`FAIL=0` is not a verdict. `FAIL=0` over the expected denominator, with `MISSING=0`, is.**

And the shape worth carrying to every other instrument: **an instrument must REFUSE, or re-label, when its basis
moves — it must never quietly report a better number.** hq_P reached the identical rule from the performance side
the same day, where a watermark re-pinned as a 2.20x "win" turned out to be a two-day-old campaign plus a
hand-edited workload (`FINDING-2026-08-24-hq_P-roman-watermark-repinned-2.20x-is-a-campaign-not-a-commit.md`).
Two seats, two instruments, one defect: **a clean reading over a basis that moved.** The third state — *refuse* —
is what both were missing.

## ROUTED

- `tasks/corpus-suites-consolidation.task.md` — its `## QA` pre-conversion board was quoting the superseded
  364/364. Replaced with the measured 362/362 **and** the instruction to match `rc=0`, not a number. That row
  moves and deletes thousands of corpus files, so rc=2 exists mostly for it.
- `tasks/instrument-repair-bundle.task.md` PART 2 — `handoff_status.sh` has the same two-state defect (COMPLETE /
  BLOCKED, no *"I cannot tell"*). This cure is the precedent to copy.
- `tasks/instrument-repair-bundle.task.md` PART 3 — new gate `test_gate_no_fossil_src_paths.sh`, plus the still-live
  fossil `INC="$CORPUS/demo/inc"` (that directory does not exist; the includes are at `corpus/include`) which is
  spelled the same way in at least six scripts.

## NOT FIXED HERE, DELIBERATELY

`INC` was left pointing at the non-existent `demo/inc`. It is a **fossil, not a live defect for this board**: the
beauty drivers `-INCLUDE 'assign.sno'` and those files sit beside the drivers, so include resolution is relative to
the source and `SNO_LIB` is not load-bearing here. Repointing it could change a grading verdict by making a program
find an include it does not find today — that belongs in its own commit with its own board, not bundled with a cure
to the instrument that would grade it. Routed to `instrument-repair-bundle` PART 3.
