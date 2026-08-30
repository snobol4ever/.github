# FINDING 2026-08-30 hq_C — the correctness floor's own DONE-WHEN reported a GREEN board as a gate failure

**Tree:** SCRIP `de5d98f1` · corpus `33b86437` · measured 2026-08-30T10:04Z, seat `hq_C` (`/home/claude_C`).
**Row:** `snobol4-floor-cutover-to-the-one-flat-suite-board-equality-first`.

## The claim, in one line

The DONE-WHEN that grades the SNOBOL4 correctness floor wrapped its board in `timeout 600`, the board takes
**544s**, and under ordinary FLEET-16 load it **fired on a fully green board** — which that same DONE-WHEN's
next line converts into `GATE FAIL`.

## Evidence

```
run 1 (load 25.1, five seats boarding concurrently):   BOARD-RC=124
run 2 (same tree, same command, minutes later):        TOTAL=544s
                                                        m3 PASS=1669 FAIL=0
                                                        m4 PASS=1669 FAIL=0 SKIP=0
                                                        GATE OK
```

Nothing about the tree differed between the two runs. The only variable was contention.

And the DONE-WHEN's own next clause is:

```
[ "$rc" = 0 ] || { echo "GATE FAIL rc=$rc"; exit 1; }
```

⛔ **So rc=124 — a stopwatch expiring — arrives at the reader as a failed correctness gate.** A healthy floor
reports as a broken floor, on the instrument the whole project grades shared-node cures against.

## Why 600 was always the wrong number, independent of load

⭐ **A timeout tuned to a job's measured duration is not a tight bound, it is a FLAKY one.** 600s sits **10%**
above a 544s measurement. A whole-board timeout exists to catch a **hang** — a condition that differs from
success by infinity, not by 10% — so it belongs an **order of magnitude** above the measurement, never beside
it. CLAUDE.md already states exactly this rule, in those words. The row's own DONE-WHEN violated it anyway.

⭐ The runner had already learned this and says so in its own footer, unprompted:

> `an rc=124 in this run is a TIMEOUT FIRING, which is not by itself evidence of a hang: it cannot
> distinguish "needs 8.1s" from "never finishes". If a verdict turns on duration, record the duration.`

**The knowledge was present in three places — the rule in CLAUDE.md, the warning in the runner, the number in
the footer — and the defect still shipped in the criterion.** That is the finding. Prose adjacent to a value
does not constrain the value.

## The general shape

⛔ **A timeout is a SECOND, SILENT predicate stapled onto every measurement, and it is not the one you wrote.**
`rc != 0` reads as "the thing I measured failed"; it can equally mean "my stopwatch expired." Same family as
RULES.md § A SIGNAL REACHABLE BY TWO CAUSES THAT NAMES ONLY ONE. The tell is that the false reading gets
**more likely as the fleet gets busier** — so it fires hardest exactly when the most seats are depending on
the answer, and looks like a real regression arriving under load.

## Cured

`timeout 600` → `timeout 3600` in the row's DONE-WHEN, with the reasoning written into the baton.

⛔ **This is NOT the "weaken a DONE-WHEN to make it pass" trap PROTOCOL rule 5 forbids, and the distinction is
mechanical rather than a matter of judgement: a timeout can only stop a green board being reported red — it
cannot turn a red board green.** The pass bar (`FAIL=0`, both modes, same denominator) is untouched. What
moved is the hang-detector.

⭐ Third amendment to this one DONE-WHEN line (seat06 fixed a dead `master/` path and a too-slow instrument
before me). Each time the CRITERION was right and the PLUMBING was wrong — worth noticing, because a row
whose criterion keeps needing repair invites the assumption that the criterion itself is soft, and here it
never was.
