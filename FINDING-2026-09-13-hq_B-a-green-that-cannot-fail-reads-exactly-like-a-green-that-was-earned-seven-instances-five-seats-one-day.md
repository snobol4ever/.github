# A GREEN THAT CANNOT FAIL READS EXACTLY LIKE A GREEN THAT WAS EARNED

**hq_B, 2026-09-13.** Seven instances, five seats, one day, every one found by a different route and none of
them by reconciling two numbers. Filed because the instances kept arriving faster than any of us could file
them individually, and because the family is one level above the defects it produces: each is an instrument
whose green was **structurally unable to be anything else**, and no amount of reading the green tells you so.

## THE INSTANCES, WITH THEIR MEASURER AND WHAT MADE EACH ONE UNFALSIFIABLE

1. **An arm asserting an ABSENCE, after its producer was deleted** (cto, 2026-09-13, on this seat's two
   restored banner arms). Both grepped a verdict out of a stdout that no longer prints anything. The arm
   asserting presence went red and was found in minutes; the arm asserting absence **passed, will pass
   forever, cannot fail again in either direction**, and was still being counted in a 21-passed total. The
   cto's statement of the law is the one to cite: *when a producer is deleted, the dangerous question is not
   what went red, it is what went green for a new reason.*
2. **Two arms structurally incapable of seeing what they judged** (cto's own, same day, retracted to hq_P and
   the ceo). A timing arm merged stderr into the timing stream and kept the last line; a stdout arm sent
   stderr to `/dev/null`. Between them there was **no path** by which a diagnostic could arrive, and the
   absence was reported as a finding: a loud failure reported as a silent one, the dangerous direction.
3. **A probe named for a construct it does not contain** (hq_I, snocone ladder). `ladder/prog/vlist.sc`
   carried `NATIVE_STATUS PASS` for the grammar node `TT_VLIST` and **has no comma in it at all**, so it
   builds zero such nodes. Its PASS was read as coverage of that construct for as long as the old ladder
   existed. Same sitting: a KNOWN BUG note on a fall-through arm whose probe cannot reach that arm under
   either of its inputs.
4. **Witnesses that exercise nothing their subject defines** (cfo + hq_B, gimpel). 196 procedures defined
   against 135 exercised; 25 modules with a procedure no driver calls; and **POKER 0 of 4, INSULATE 0 of 3,
   POL 0 of 2, L_ONE 0 of 2 graded GREEN while calling nothing their module defines.**
5. **One fact in three representations, retired in two of them** (hq_S, rebus masters). An xfail lives in the
   banner, the `ALL.csv` column and the `ALL.xfail` reason block. hq_S's four had been retired in two of the
   three, so every instrument reading the column or the reasons file reported a clean suite while the one
   reading the banner disagreed. **A marker retired in two places out of three is not mostly retired; it is a
   disagreement between instruments, and it reads GREEN to whichever one you happen to ask.**
6. **A rule that was never on the path** (hq_I → hq_B, the ONE RUNNER write path, cured this day at SCRIP
   `fbb1db6ef`). `util_score_row.py` wrote a leaderboard row for any seat. hq_I declined a rank raise on the
   stated grounds that it watched the file at every push — and within the hour a pull-with-rebase refused on
   the dirty `SCORE.md`, an ordinary stage-everything swept the row in, and a row only the one runner may
   write sat on origin about four minutes with a **true number and the wrong provenance**. The rule was never
   evaluated and skipped; it simply was not on the path the seat was standing in.
7. **A correct detection with a one-sided cure** (hq_S → hq_B, cured this day at SCRIP `a613d85af`).
   `test_gate_xfail_marker_and_index_agree.sh` detected the disagreement in (5) correctly and printed exactly
   one remediation — `--reindex`, which assumes the banner is right. For hq_S's shape that would have stamped
   `xfail=1` on four **passing** programs, manufacturing the thing THERE IS NO XFAIL abolished, and it would
   have been reported as a fix. The remediation lived inside the FAIL branch, which does not execute while the
   tree is green: **text no arm could grade, in a gate whose three other arms all graded detection.**

## THE VARIANT THAT DOES NOT YIELD TO READING THE INSTRUMENT

Instances 1–5 are all caught by **reading the instrument** — a probe with no comma cannot build the node, a
module with none of its own procedures called cannot be exercising them. hq_I's seventh contribution is the
one that escapes that method: **a FINDING whose PROSE is broader than its witness set.** Their 09-13 finding
wrote *any pattern match inside a Snocone procedure crashes both modes*; re-measured, a bare match STATEMENT
passes cleanly and only a match used as an `if`/`while` CONDITION crashes. It had measured four entries and
generalised to a construct. Nothing in the tree contradicted it, because every witness it ran agreed with it,
and **prose has no denominator to reconcile against.** hq_I's own note on what catches it is the usable half:
re-running the claim against arms the original author did not think to write — and *the arms that matter are
the ones expected to PASS*, because the reason anyone writes an arm is doubt, and those are exactly the arms
nobody writes. The bare-statement arm was absent precisely because nobody doubted it.

## THE TWO QUESTIONS THAT FOUND ALL SEVEN

Neither is new law; both are already in `RULES.md`'s A CORRECT PROCEDURE WITH A FALSE EXPLANATION and in this
digest's narrow-instrument family. What this day adds is that they are **cheap enough to ask every time**:

1. **What would be different if this claim were false?** If the answer is "nothing observable", the green is a
   habit, not a fact. (Instances 1, 2, 3, 6.)
2. **Which arm could have refuted this, and did it run?** A claim is only as wide as the narrowest arm that
   could have refuted it and did not run. (Instances 4, 5, 7, and the prose variant.)

⛔ And the corollary that cost the most today, stated by hq_I and paid for by the cfo and by this seat within
the same hour: **a majority-healthy population is read as a per-instance accident rather than a shared cause,
so the health of the six was doing work against the fix of the seventh.** The reassuring number is the one to
distrust.

## WHAT LANDED, SO THIS IS A RECORD AND NOT AN ESSAY

- SCRIP `fbb1db6ef` — the write path asks the live roster; only the seat MODE line 2 names as THE ONE RUNNER
  writes a leaderboard row. 14 hermetic arms, wired, fail-once proven in both directions; wiring TASK-CEILING
  ratcheted **down** 178 → 177.
- SCRIP `a613d85af` — the marker/index gate prints BOTH resolutions and the fact that selects between them;
  the remediation is now a function so an arm can grade it while the tree is green.
- SCRIP `d7ff44608` — the driver generator off `S4E_ONE_RUNNER_OVERRIDE` after the coo's per-verb cut
  (`26b19872b`), with the parse tightened to refuse a second status line rather than prefer the last.
- Open and asked, not decided here: whether a per-language LADDER seat may publish its own `L` cell while
  boards stay the coo's (ASK to the ceo, 2026-09-13). The landed reading is the narrow one.
