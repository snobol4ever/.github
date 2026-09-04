# FINDING — a control arm that varies the data and holds a stale instrument fixed reads as confirmation

**hq_C, 2026-09-04. Measured. Diagnosed by hq_T, whose instrument it was; written up here because the
shape is general and not about SCORE.md.**

## What happened

Grading the rung-10b landing, `test_gate_score_tables_agree.sh` read **rc=1, 19 STALE lines**, including
what looked like a genuine same-denominator conflict: `raku: display vendor says 924/986, grid V says
4/986`. hq_T had just pushed `.github bf3802b0` claiming *"three same-denominator conflicts settled by
measurement — gate green"*.

I did the responsible thing and control-armed it before blaming anyone: stashed my own SCORE.md edit, ran
the gate on origin's file (**rc=1, 19 STALE**), re-applied my edit, ran it again (**rc=1, 19 STALE**).
Identical. I concluded — and reported to ceo, to hq_T, and to Lon — that the red was pre-existing on
origin, not mine, and that hq_T's "gate green" did not reproduce.

**Every one of those measurements was reproducible. The conclusion was wrong.**

## Why

The gate is two halves in two repos. `SCORE.md` is the DATA and lives in `.github`. The parser that reads
it is `scripts/util_score_row.py` and lives in **SCRIP**. I had rebased `.github` onto hq_T's commit — so
my data was current — while my SCRIP checkout was the tree I was grading, `4a4cbdbf4`, built on
`origin/main 4c7253e99`. The parser cure, SCRIP `2e85e1617`, landed after that.

Measured after the fact, and this is the whole finding in one table:

| tree | `2e85e1617` (the parser cure) |
|---|---|
| `4c7253e99` — the origin/main I merged from | **predates it** |
| `4a4cbdbf4` — my merge candidate, what I graded on | **predates it** |
| `6b7d0f2b6` — current main | has it → `GATE PASS(0)`, 13 mirrored pairs, **0** same-denominator conflicts, 20 one-sided |

hq_T's claim was true the whole time. The raku line was never a conflict: `924/986` is the roast
PARSE-FAIL count and `4/986` its PASS count, and they reconcile exactly — `4+9+924+7+1 = 945`, plus 41
missing, `= 986`. The pre-cure `cell_fractions` scraped every `N/D` pair out of prose as a PASS fraction,
and its drop-marker check only ever inspected the 20 characters **before** a fraction — but a label can
sit on either side of the number it names.

## The lesson, which is not about SCORE.md

**My control arm varied the DATA and held the INSTRUMENT fixed, and the instrument was the broken axis.**
Both arms ran the same stale parser, so the experiment could only ever return "same answer both ways" —
and that reads exactly like exoneration. A control arm proves *the variable you varied* is not the cause.
It says nothing whatever about the variable you held constant, and it does not announce which one you
held.

⭐ **The cheap test, and it costs one command:** before quoting a control arm, ask *which axis did I hold
fixed, and is the instrument on it?* If the instrument is on the held axis, the arm is not a control —
it is a repetition. Vary the instrument too: `git merge-base --is-ancestor <cure> HEAD` is the whole
check when the instrument lives in a repo you did not pull.

This is the same family as RULES.md § A CORRECT PROCEDURE WITH A FALSE EXPLANATION and the `command -v`
lesson in the seat digests, with one turn of the screw added: there, a right answer came with a wrong
reason. Here, **a right procedure came with a wrong reason and produced a wrong answer**, and the
procedure's own rigour is what made the wrong answer credible — to me, and very nearly to ceo and Lon,
because I reported it up.

⛔ **Second-order damage, recorded because it is the expensive part.** A false "your gate is still red"
aimed at the seat who had just fixed it is worse than silence: it spends their time re-verifying settled
work, and it teaches the org to discount that gate. I sent exactly that message. It is corrected, and
`.github 4bc6d4f0`'s commit message carries the same wrong framing — the "net zero staleness added" claim
in it is still true and independently measured, but its description of the gate as red on origin is not.
Commit messages are immutable; this file is the correction of record.

## Cross-references

- SCRIP `2e85e1617` — the parser cure · SCRIP `6b7d0f2b6` — current main · `.github bf3802b0` — hq_T's
  data cure · `.github 4bc6d4f0` — my commit carrying the wrong framing.
- The real, still-open class defect hq_T named and owns: `util_score_row.py write` updates only the
  DISPLAY row, so every board run stales the grid cell beside it. Half cured already
  (`util_apply_score_grid` merges cell by cell and binds the display BY SHAPE); the remaining half is
  teaching `write` to update both halves.
