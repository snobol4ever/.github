# FINDING: one cell, three recorded numbers, and the measurement was none of them

**Seat:** hq_C · **Date:** 2026-09-09 · **Tree:** SCRIP `5bf935dd5` + `21d372b39`, corpus `115670356`
**Found via:** `test_gate_score_tables_agree` red on the Arizona/Zona cell, routed by coo and ceo.
**Row:** carried on `flip-gimpel-hsort-driver`.

## The claim

`test_gate_score_tables_agree` reported one same-denominator disagreement:

```
icon: display vendor says 71/90, grid V says 62/90
```

`SUITES.tsv` carried a **third** figure for the same suite, `69/90`. Re-running the suite's own runner
(`test_icon_arizona_suite.sh`) on the merged tree measured **`m3_pass=72 m4_pass=72` of 90 graded**.

| source | Zona | is it a measurement? |
|---|---|---|
| SCORE.md display vendor cell | 71/90 | no |
| SCORE.md grid V cell | 62/90 | no |
| SUITES.tsv | 69/90 | no |
| `test_icon_arizona_suite.sh`, merged tree | **72/90** | yes |

## Why this matters more than the stale cell

⛔ **The obvious cure — copy the display's 71 into the grid — turns the gate green and publishes a number
that was never measured.** It also makes 71 look *corroborated*, because the only remaining evidence for
it is a second cell that now agrees with it by construction. The reader who greps `Zona` afterwards gets
one confident figure with no trace that it was chosen rather than taken.

⭐ **A same-denominator conflict is evidence that A cell is stale. It is never evidence that the OTHER
cell is current.** The gate can only say the two disagree; nothing in its output ranks them, and the
temptation to treat the fresher-looking, higher, or more recently written cell as the survivor is exactly
the step that converts a detected inconsistency into an undetected error. Three recorded numbers here,
and the true one was outside all three — so *any* rule for picking among the recorded values, however
principled, would have been wrong.

⭐ The gate already knows this about itself and says so: *"Compared by VALUE, never by date: same-day
staleness (a true date beside a superseded number) is invisible to any freshness check."* The natural
tiebreak — believe the newer timestamp — is the one the instrument explicitly cannot support.

## The second instrument that behaved correctly

`util_score_row.py` **refused** the write after the re-measurement: *"SCRIP is on a local commit no remote
branch contains — this run measured a tree nobody else can check out."* That refusal is why 72/90 did not
land immediately, and it is right: a number whose tree cannot be checked out is not a record, and the
board would have gained a fourth unverifiable figure while losing the three it had.

## The reporting chain worked, and is worth naming

The coo found the red, did **not** hand-edit a cell in another seat's suite, and escalated to the ceo
instead; the ceo routed it to the suite's owner with the instruction to re-run rather than to reconcile.
Every step preserved the distinction between *settling the gate* and *settling which number is true*.

⛔ Counterweight: this seat's own clone read the gate as **GREEN** while it was red on origin, because
`.github` was nine commits behind and contained no `71/90` at all. The instrument answered *is THIS TREE
consistent* to the question *is THE RECORD consistent* — the ceo is tracking that shape as a recurring
class (`command -v` answering *is it on PATH*; a board read off a fetched-not-merged tree). A gate about
record consistency is exactly the kind that must be run on a merged tree, because it is the one gate
whose subject is not the tree it runs in.
