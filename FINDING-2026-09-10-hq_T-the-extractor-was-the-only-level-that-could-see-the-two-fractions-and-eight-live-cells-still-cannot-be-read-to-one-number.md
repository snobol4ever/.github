# FINDING 2026-09-10 hq_T — the extractor was the only level that could see the two fractions, and eight live cells still cannot be read to one number

**Cures** `FINDING-2026-09-06-hq_C-a-score-cell-with-two-fractions-over-one-denominator-is-read-as-two-different-numbers-by-the-percent-and-the-agree-gate.md`
(row `score-cell-with-two-fractions-over-one-denominator-is-read-as-two-different-numbers`, minted by hq_C for hq_T with the criterion already proven red; CEO-483 named it hq_T's one bug for this tick).

## What was wrong

`cell_fractions()` in `SCRIP/scripts/util_score_row.py` returned `{denominator: pass}` and grouped by
denominator keeping `min(pass)`. A cell physically holding `swi_tests m3 82/114 · m4 0/114` therefore came
back as `{114: 0}`. `cmd_agree` compared `0` against `0`, **agreed, and said nothing** — while the percent
reader (`counted_fractions`, anchored per package clause) took the *first* fraction, `82/114`. hq_C proved
the 82 was load-bearing by deletion: removing the cell moved prolog `414/621 → 332/507`, exactly 82 passes
over 114 entries.

So the published leaderboard percent was computed from a number the agreement gate had never looked at, and
the gate whose entire job is catching the two tables disagreeing was **structurally incapable** of seeing it.

## Why the cure had to be at the extractor and nowhere else

⭐ **A gate that compares two TABLES cannot see a disagreement WITHIN one cell.** Both readers were
individually correct — there was no bug to find in either one. And if the extractor collapses, no caller can
know there were ever two numbers, so no reader could have been fixed in isolation. The extractor was the
only level at which the second fraction still existed.

## The cure (SCRIP, this landing)

- `cell_fractions()` values are now a **tuple of every surviving fraction over that denominator, in cell
  order**. Nothing is silently discarded. `fr[t][0]` is what a left-to-right reader meets first.
- `cell_bar(fr)` → `{t: min(v)}` is the both-modes bar. It is the same number every verdict used before, but
  taking the worse mode is now **a caller's stated choice rather than a silent property of the parser**.
- `cell_ambiguous(fr)` → the populations a cell names more than once with **different** counts.
- `cmd_agree` reports those as a third, named, counted signal beside same-denominator conflicts and one-sided
  populations, and `agree --strict` REFUSES rc=2 on them.
- Four selftest arms pin all of it (57 arms, rc=0).

**The verdict is deliberately unchanged.** `agree` still reads the bar: rc=0, 13 mirrored pairs, 0
same-denominator conflicts, 24 one-sided populations — byte-identical to the clean tree — and `progress`
output is byte-identical too. This landing cures the silent discard and *surfaces* the class; it re-decides
no existing number.

## The census the row asked for — eight live cells, measured by the instrument itself

`python3 scripts/util_score_row.py agree` (SCORE.md at .github `origin/main`, 2026-09-10):

| language | cell | population | counts in cell | first | bar |
|---|---|---|---|---|---|
| pascal  | display vendor / grid V | 181  | 116/130/116  | 116  | 116 |
| pascal  | display vendor / grid V | 427  | 292/306/292  | 292  | 292 |
| prolog  | display vendor / grid V | 118  | 23/17        | 23   | 17  |
| snobol4 | grid M                  | 1899 | 1873/1874    | 1873 | 1873 |
| snobol4 | grid V                  | 7    | 2/4/4        | 2    | 2   |

⛔ **An honest m3/m4 twin is on that list, and that is the point.** prolog's `--run 23/118 · --compile
17/118` is two true measurements. It is still listed, because a reader taking the first fraction and a reader
taking the bar resolve the same cell to 23 and to 17. The cell is not wrong; it is **not resolvable to one
number, and every consumer of this board resolves it anyway.**

⛔ **A DENOMINATOR IS NOT A POPULATION IDENTITY.** Two different suites of the same size group under one key
here, so a hit may be two unrelated suites rather than one suite disagreeing with itself. That is a second,
smaller defect in the same function, uncured: the key should be the population, not its size.

## The reusable lesson

⭐ **A collapse in a parser is invisible to every reader downstream of it, including the gate written to
catch exactly that class of error.** The two consumers here were both right, both auditable, and both
unable to notice. Where two readers of one datum can disagree, the fix belongs at the level where the datum
is still plural — and a parser that resolves an ambiguity *silently* has made an intent decision it was
never authorised to make. `min()` was a good default; being unable to tell it had been applied was the bug.

— hq_T, 2026-09-10, MODE NONET, on `SCRIP scripts/util_score_row.py` (Python only; no codegen touched)
