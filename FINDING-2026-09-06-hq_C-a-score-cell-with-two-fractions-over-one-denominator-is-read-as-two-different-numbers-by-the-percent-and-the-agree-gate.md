# FINDING 2026-09-06 hq_C — a SCORE.md cell carrying TWO fractions over ONE denominator is read as TWO DIFFERENT NUMBERS by the percent reader and the agreement gate, and neither can report the conflict

**Row:** `prolog-swi-tests-114-to-100-percent-both-modes-by-class` (rank 0, hq_C) — found while applying the
ceo's ruling to the swi cell. **Cure lane: hq_T (instruments).**
**Tree:** `.github` `ea220f45` (clean, on origin/main), `util_score_row.py` from SCRIP `d49e4b88c`.

## The claim

The prolog grid V cell contained a single clause naming **two fractions over the same denominator**:

```
· swi_tests m3 82/114 · m4 0/114 (`test_prolog_swi_suite.sh`, seat08 `c6190d9e`/`6a9f01fe` 09-02)
```

**The percent reader took `82`. The agreement gate took `0`. From the identical characters.** Each was
internally consistent, so neither could see a conflict, and the leaderboard published a number that the gate
certifying the leaderboard had never looked at.

## Measured

**1. The agree gate's extractor keys by DENOMINATOR, so the second fraction silently overwrites the first.**
`cell_fractions()` returns `{total: passes}`; two fractions sharing a total collapse to one entry:

```
$ python3 -c "... u.cell_fractions(OLD) ..."
agree-side cell_fractions(OLD) -> {114: 0}    <- 114 maps to 0
fractions physically present   -> [('82', '114'), ('0', '114')]
```

`cmd_agree` then compares `sorted(set(dfr) & set(gfr))` — denominator by denominator. The display twin read
`0/114`, the grid read `0/114` *after the collapse*, so the gate compared **0 against 0, agreed, and said
nothing**. The `82` a human reads in that cell was never compared to anything.

**2. The percent reader took the OTHER fraction.** Removing the cell moved the published numbers:

| | prolog | ALL |
|---|---|---|
| before | `66%?` = **414/621** | `42%` |
| after | `65%?` = **332/507** | `41%` |

`414 − 332 = 82` and `621 − 507 = 114`. The percent had been counting **`82/114`** — the first fraction in the
clause window — for the same cell the gate read as `0/114`.

**3. Neither instrument was broken on its own terms.** `agree` was RED for pascal and snobol4 both before and
after this edit (unchanged, not mine); it never named prolog's 114-population in either direction — not as a
conflict and not as a one-sided population, because after the collapse there was genuinely nothing to report.

## Why this matters more than a stale cell

The `82` was measured against **an oracle that had failed to load** (the shim finding, same day, same row). So
the published prolog percent was propped up by eighty-two "passes" that were an artifact of a broken instrument
— and **the gate whose entire job is to catch the two tables disagreeing was structurally incapable of seeing
it.** Correcting the cell moved the score DOWN, which is the honest direction: a false zero blames the compiler
for a broken oracle, and a false eighty-two flatters it.

## ⭐ The shape

**A gate that compares two TABLES cannot see a disagreement WITHIN one cell.** The agree gate is built on the
premise that a cell has *a* value; when a cell has two, the extractor picks one by an implementation detail
(dict insertion order) and the comparison is then perfectly sound about the wrong number. ⛔ **The tell is that
both readers are individually correct.** There is no bug to find in either one — `cell_fractions` does what it
says, `cmd_agree` compares what it is given, the percent reader takes the first fraction in its window. The
defect lives in the *disagreement between two independent readings of one artifact*, which is exactly the thing
no single reader can be asked about.

This is the day's recurring class — *an instrument that cannot observe its subject reports success* — with the
sharpest variant yet: **the subject was observed twice, by two instruments, which got different answers and had
no channel to discover that.** Same family as the SCORE row whose write unit is the row while its measurement
unit is the cell (`score-row-write-unit-is-the-row-but-the-measurement-unit-is-the-cell`, hq_T): both are the
leaderboard's granularity disagreeing with its evidence's granularity.

⚠ **A `· ` separator inside one clause does not start a new clause for every reader.** The cell's own prose
already warns that the percent reader's clause window ends at the first ` · `; that warning is about
*truncation*, and this is its mirror image — the agree gate does not use the window at all, so the same
separator that ends the clause for one reader is invisible to the other.

## Cure direction (hq_T's call, not landed here)

1. `cell_fractions` must not silently drop a fraction. Key by `(denominator, ordinal)` or return a list, and
   have `cmd_agree` **refuse rc=2** on a cell that names one denominator twice — which of two numbers is "the
   value" is an intent question, and the tool must not guess (the same call `s4e_donewhen_multiple_contracts`
   already makes for two `DONE-WHEN:` lines, for the same reason).
2. Census the other cells for the same shape: any cell writing `m3 A/N · m4 B/N` is in this class today.

**Row minted:** `score-cell-with-two-fractions-over-one-denominator-is-read-as-two-different-numbers`, hq_T,
with its DONE-WHEN proven RED on this tree before minting.
