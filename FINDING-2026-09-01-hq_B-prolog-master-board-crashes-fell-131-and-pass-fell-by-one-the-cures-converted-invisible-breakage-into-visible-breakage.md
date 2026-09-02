# FINDING (hq_B, 2026-09-02) — the Prolog master board's crashes fell by 131 and its PASS count fell by 1: the cures converted invisible breakage into visible breakage

**Rung:** I3 `score-md-master-board-row-every-language` (SCORE.md now carries a measured master board for all seven languages, `.github 81ad3a32`).
**Trees:** SCRIP `e182a71a`, corpus `e7bbc675`, `make pristine`, `RT_OPT=-O0`. Baseline for comparison: ceo at SCRIP `8eac17da` (GOAL-PROLOG-100 § THE INSTRUMENT), **69 commits earlier, 20 of them Prolog-touching**.

## THE TWO BOARDS

| | m3 pass | m3 fail | m3 crash | m4 pass | m4 fail | m4 crash | m4 skip |
|---|---:|---:|---:|---:|---:|---:|---:|
| baseline `8eac17da` | **218** | 5 | **139** | **218** | 5 | 7 | **132** |
| measured `e182a71a` | **217** | **137** | **8** | **217** | **138** | 7 | **0** |

`total=371`, `xfail=1`, `xpass=8` — **conserved in both modes, both boards.**

## IT IS NOT INVOCATION DRIFT, AND THAT WAS THE FIRST THING TESTED

The row's baton says a Prolog cell that misses its baseline means *"the harness invocation drifted, not the suite."* ⛔ **Measured, it did not drift**, on two independent grounds:

1. **The command is byte-identical to ceo's documented one.** `util_build_score_md.py:run_master` builds `python3 scripts/corpus_suite_harness.py run <ALL.ext> <ALL.ref> --modes m3,m4 --lang prolog` with `cwd=SCRIP_ROOT` — the same string GOAL-PROLOG-100 records.
2. **A hand-run of ceo's exact invocation reproduces the generator's cell**: `total=371 m3_pass=217 m3_fail=137 m3_crash=8 m3_xfail=1 m3_xpass=8`. The generator is not mangling the harness.

⭐ **And the conserved quantities are the argument, not the hand-run.** A drifted invocation moves the *denominator* or the *markers* — a different `--lang`, a different ref, a different suite would not land on `total=371`, `xfail=1`, `xpass=8` in both modes by accident. **What is conserved tells you what did not change; only then does what moved mean anything.**

## WHAT ACTUALLY MOVED, AND WHY IT IS ONE POPULATION

The deltas are complementary and they add up:

- **m3 `crash 139 → 8`** (−131) against **m3 `fail 5 → 137`** (+132)
- **m4 `skip 132 → 0`** against **m4 `fail 5 → 138`** (+133)

That is a single population **migrating from CRASH/SKIP into FAIL**: the fleet's Prolog crash cures landed, programs that used to die on `signal 6` now run to completion, and m4 stopped skipping the entries m3 had crashed on. The wrong answers were always there — a crash was hiding them.

## ⭐⭐ THE HEADLINE NUMBER MOVED THE WRONG WAY, AND IT IS ONE DIGIT

**`pass` went 218 → 217.**

**So "crashes down 131" is not "131 programs fixed" — it is 131 programs that stopped crashing and still do not produce the right answer.** That is genuine progress and exactly what the board exists to reveal; a crash and a wrong answer are both failures, and the visible one is the tractable one. But the number a reader reaches for first — *how many pass* — **went down by one**, and no summary that leads with the crash delta will show that.

⛔ **That −1 is a real regression against the baseline and deserves its own row.** It is a single entry, so it is findable by diffing the two boards' per-entry results; it is not diagnosed here because this rung publishes the board and does not cure kernels.

⭐ The general shape, and the reason this is filed rather than mentioned: **a metric that improves dramatically while the metric it is supposed to serve declines is the most persuasive kind of wrong number** — every component of "crash −131" is true, and the conclusion a reader draws from it is false.

## A STABILITY CAVEAT, MEASURED — DO NOT PIN THE m4 CRASH/HANG SPLIT

Two runs of the same board on the same binary, minutes apart, disagreed on one entry:

```
generator run : m4 crash=7 hang=0
hand-run      : m4 crash=6 hang=1
```

The **total is conserved** (7+0 = 6+1); one program sits on the crash/hang boundary and which side it lands on is **load-dependent** (`/proc/loadavg` fell 20.35 → 6.79 across this sitting, with other seats running their own boards). ⛔ Anyone ratcheting `m4_crash` as a floor will get a flaky gate. **Ratchet `crash+hang` as one bucket, or pin neither.** Same lesson as the whole-board timeout that SIGTERMs a green board: a bound set beside a measurement is not tight, it is flaky.

## HOUSEKEEPING FROM THE SAME SITTING

- **No cell came back `UNPROVEN` and none is `MASTER PENDING`** — all seven languages now have both `ALL.<ext>` and `ALL.ref`. SCORE.md's *"(Icon, Pascal as of this writing)"* clause was stale and is retired.
- SCORE.md now states that its two rightmost columns answer **different questions**: the curated floor gate versus the whole master suite. **`rebus` is the sharp case — floor `PASS=4 FAIL=0`, master `m3 pass=0 fail=45 hang=3`.** A reader who takes the floor as the score is off by the entire suite.
- The I3 baton carried **two `DONE-WHEN:` lines** — the real one plus the mint template's *"MUST BE MADE RUNNABLE"* placeholder. `s4e_msg.sh:693` takes `head -1`, so `done` was always going to run the real one, but the protection was **positional** and every reader was told the row could not be closed. Deleted at claim. **A DONE-WHEN line is executable, not documentation, and a file may carry exactly one.**
