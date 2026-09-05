# Four of eight HQ roots could not write THE ONE LEADERBOARD, and the gate that pins the map passed green

**Measured by** hq_I (HQ-INSPECT), 2026-09-05 ~15:45–16:00 CDT, first sitting under OCTET.
**Trees** SCRIP `b812fb6d1` (the ceo's own 15:34–15:38 floor tree) · corpus `8972babeb` · .github `7598e1c57`.
**Cured in** SCRIP `f69818116`. **RT_OPT=-O0, incremental `make`** (PRISTINE BUILD IS LOOSENED, RULES.md:118).

## THE CLAIM

Lon opened `/home/claude_U`, `/home/claude_S`, `/home/claude_I` and `/home/claude_R` on 2026-09-05. `s4e_msg.sh`
learned all four (its case block, lines 96-100). `util_score_row.py`'s `derive_measurer()` learned none — it
carried `ceo hq_C hq_P hq_B hq_T` and nothing else. So from those four roots **every** suite, board and gate ran
to completion, printed a full and correct board, and then ended:

```
REFUSED(2) util_score_row: --measurer is required: an unattributed row is a claim with nobody behind it
    (got '', and the root '/home/claude_I' is not in the seat map, so it could not be derived)
⚠ SCORE.md NOT UPDATED -- record this row by hand (the REFUSED line above says why)
```

**Half the HQ roster was silently outside Lon's FACT RULE** that any run of any suite by any session updates the
leaderboard — the rule whose whole purpose is *"so whenever we want to know the state it is there not an hour
away of running tests."* Reproduced three times independently in one sitting: `test_icon_arizona_suite.sh`,
`test_icon_jcon_suite.sh` and `test_icon_ipl_suite.sh`, each printing its board and then failing to record it.

⭐ **The dangerous shape is that the board still prints.** The refusal is the last two lines under a screen of
results, so the failure is not "my run broke" but "I believe I recorded a number I did not." Any cell attributed
to hq_U, hq_S, hq_I or hq_R between ~15:00 and this cure was never written; the row a reader sees is the older
one, wearing its older stamp, with nothing anywhere saying an update was attempted and lost.

## WHY THE GATE DID NOT CATCH IT — THE HALF WORTH KEEPING

`test_gate_seat_identity_one_map.sh` exists for precisely this drift. It was **green throughout**, and it was
green for a reason its own header already knows better than:

> ⛔ THE MAP IS LIFTED FROM THE FILE, NOT RETYPED HERE. A gate carrying its own expected map would be a FOURTH
> copy, and would pass while the file it grades was wrong.

That is exactly right about the **mapping** — and the gate then hand-typed the **population**. ARM 2 carried
`ROOTS="/home/claude /home/claude_C /home/claude_P /home/claude_B /home/claude_T …"` plus synthetic numbered
seats, with the rationale that "roots are enumerated here because they are the org's roster, not a copy of the
mapping logic." The roster stopped at `claude_T`. The gate therefore compared ten roots, found all ten
consistent, and printed PASS over a map that was broken for four roots it had never been told existed.

⭐⭐ **The general form, and the reason this is filed rather than just fixed: a gate only ever grades the
population it is given, and a hand-maintained population is a second place a new fact must be registered — which
is the exact thing the gate was built to make impossible.** Lifting the *logic* and typing the *roster* feels
like single-sourcing, and is not. This is the same family as the digest's own ⭐⭐ lesson that an instrument
answering a narrower question than you think you asked will never say so: `ls dir/*.ext` over a tree you have not
listed, `$?` after a pipeline, `command -v` for existence. Here the narrower question was *"do the roots I
enumerated agree?"* and it was read as *"do the maps agree?"*

## THE CURE (both halves; the second is the one that lasts)

1. `derive_measurer()` maps all nine roots.
2. **ARM 2's roster is lifted out of the same case block the gate already lifts the map from**, so a tenth root
   is graded the moment the bus learns it. The lift REFUSES rc=2 rather than grade an empty roster — an empty
   literal-root list would make every assertion below it vacuously true and print the success shape over
   nothing. The synthetic numbered seats stay spelled out: they are `[0-9]` glob arms carrying no literal label,
   so nothing can lift them.

The header's deliberate asymmetry is untouched — on an *unrecognised* root the bus still invents a name and the
leaderboard still refuses, and ARM 3 still pins that. Only the roster changed.

## WITNESS, BOTH DIRECTIONS, PROVEN BEFORE THE CURE LANDED

With `derive_measurer()` reverted to its five-root form, on the new gate:

```
GATE FAIL: root /home/claude_U resolved to nothing (bus='hq_U' leaderboard='')
GATE FAIL: root /home/claude_S resolved to nothing (bus='hq_S' leaderboard='')
GATE FAIL: root /home/claude_I resolved to nothing (bus='hq_I' leaderboard='')
GATE FAIL: root /home/claude_R resolved to nothing (bus='hq_R' leaderboard='')
GATE FAIL(1) [test_gate_seat_identity_one_map]: 4 seat-identity map copies disagree … (examined 19 arms)
```

With the cure: `GATE PASS(0) … (examined 19 arms)`, and its own line reads **"graded 14 known roots"** where it
read 10. The instrument now fails on the defect it was built for and missed.

## ⚠ WHAT THIS FINDING DOES NOT CLAIM

It does not claim any *specific* published cell is wrong. The failure destroys writes, it does not corrupt them —
a lost update leaves the previous cell and its previous stamp intact and honest about its own age. The exposure
is that four HQs' work since ~15:00 CDT is missing from the board, not that the board lies. hq_U, hq_S and hq_R
have been mailed to re-record anything they ran.

## LANE NOTE (hq_I authored outside its lane, deliberately, and says so)

Instruments are hq_T's lane. hq_I authored this because it blocked HQ-INSPECT's own mandated first-sitting
deliverable (measure the Icon V cells and write the LANE REVIEW rows) and three sibling HQs at the same time,
and because a non-blocking finding filed into a queue nobody is draining under OCTET is, per RULES.md § THE TWO
MODES, the shape of not doing the work. hq_T is mailed and free to rework it.
