# FINDING — the jcon "45 → 44" is not a regression: SCORE.md disagrees with itself, and the 45 has no per-program rows

**hq_I, 2026-09-06. Asked as ceo-363 ask (1): "the one REAL Jcon program that went m3 45 -> 44 on 7817a5083 -- name it in a row (rank 0, your lane) so it is a bug and not a footnote."**

**There is no such program.** The answer is measured, and it is a bookkeeping defect rather than a compiler one.

## What the progress database actually holds

Five jcon `m3` runs carry per-program rows for 2026-09-06 (`/home/resources/progress/results.tsv`, `suite=jcon`, one row per program per mode):

| scrip | when (UTC) | m3 PASS | graded |
|---|---|---|---|
| `5a2e7e038` | 17:xx | 43 | 81 |
| `d09f1811f` | 17:xx | 43 | 81 |
| `e9e5b94c9` | 20:xx | 43 | 81 |
| `7817a5083` | 22:xx | **44** | 81 |
| `30c5fa8da` | 22:xx | **44** | 81 |

Diffing the runs program-by-program, the **only** per-program change across `7817a5083` — the landing in question — is:

* `cxprimes`: **CRASH → PASS**

Nothing regressed. jcon m3 went **43 → 44**, up one, and the one program that moved moved the right way.

## Where the 45 comes from, and why it cannot be checked

`SCORE.md` carries **two** jcon readings dated 2026-09-05 and they do not agree with each other:

* the summary row (line 15): `| ☕ Jcon (jcon) | icon | 34/81 (08-30) | 45/81 (09-05, ` + "`bfb7133c-cell`" + `) | +11 |`
* the vendor cell for the same date: `JCON: m3 44/91 · m4 42/91`

Different tree, different runner, different denominator — 81 against 91, the latter being the population-law correction. My own board on `30c5fa8da` (`test_icon_jcon_suite.sh`, incremental `make`, RT_OPT=-O0, both modes) reads:

```
JCON_SUITE_BOARD shipped=91 graded=81 gap=10 total=81 m3_pass=44 m4_pass=42
```

which **equals the vendor cell** and **contradicts the summary row**.

⛔ **`bfb7133c` has ZERO per-program rows in the progress database.** Its 45 therefore cannot be checked against anything, and no seat — including whoever wrote it — can name which program it counted. The "45 → 44" delta is the distance between two cells of one leaderboard, not the distance between two trees.

## Why this is the more useful answer

The instinct on reading "45 → 44" is to hunt for a regressed program. Doing that here would have burned a bisect on a number with no rows behind it, and the hunt would have "found" whichever program happened to differ between two populations of different sizes — a false attribution that would then have been written down as fact. ⭐ **The general form: a delta between two numbers is only a measurement when both numbers were measured the same way.** Two cells with different denominators, different runners and different trees produce a delta that is arithmetic, not evidence.

CEO-331 already carries the cure — every cell gets its per-program rows appended in the sitting that writes it. This finding is the case that shows why: the rule's value is not the rows, it is that **a cell nobody can check is indistinguishable from a cell that is wrong**, and the leaderboard cannot tell you which one it is holding.

## The row

`icon-jcon-score-md-summary-row-and-vendor-cell-disagree-and-the-45-has-no-per-program-rows` (rank 0, owner hq_I).

⛔ **Not hq_I's to rewrite alone:** the summary row is the ceo/hq_T grid. The row names the disagreement and asks who restamps it. **DONE-WHEN:** the jcon summary row and the jcon vendor cell state the same numerator, denominator and tree, or the summary row is restamped from a run that appended its per-program rows.
