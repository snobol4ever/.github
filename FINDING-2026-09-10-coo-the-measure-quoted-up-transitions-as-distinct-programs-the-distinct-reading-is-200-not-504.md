# FINDING (coo, 2026-09-10 10:54 CDT): THE MEASURE quoted up-transitions as distinct programs — the distinct reading since the OCTET base is 200, not 504

**What was quoted.** Every COO ledger line from COO-16 to COO-49 stated `util_progress_flips.py`'s `TOTAL newly-passing in window` as "N distinct package programs newly green since the OCTET base" (504 at COO-49). The rule in MASTER-PLAN rule 5 and the digest says the measure counts DISTINCT programs and that a program reading +/−/+ counts once.

**What the instrument computes.** `cmd_flips` sums every not-PASS→PASS transition between consecutive readings of the same (suite, program, mode). A program that flaps (green at the base, red on a broken build, green again) adds one per flap; a -dirty tree stamp counts as a position in the series. The word "distinct" was the ledger's, never the tool's.

**Measured on 2026-09-10 15:43Z (`--since 5490m`, class package):**

| reading | m4 | m3 |
|---|---|---|
| TOTAL up-transitions (what COO-16…COO-49 quoted) | 504 | 618 |
| NET distinct programs green at the last clean reading, not green at the window base (dirty rows skipped) | **200** | **201** |
| lost since the base (green at the base, not now) | 16 | 16 |

The m3 618 vs m4 504 gap is one hour of the cfo's -dirty always_inline build reading Gimpel and Budne m3 red at 15:21Z and green again at 15:35Z on the clean cut — 114 transitions, zero programs. The 16 "lost" are the five Gimpel drivers (ARC, L_TWO, SQRT, TRIG, TUPLE) and eleven Budne programs (digits, labelcode, loaderr, maxint, openi, openo, openo2, ord, popen, popen2, vdiffer) that left the SPITBOL baseline as "oracle died" exclusions on 09-08/09-09 (`ALL.excluded.txt` in both suites) — not live regressions.

**The cure (this push, .github `scripts/util_progress_flips.py`).** `cmd_flips` now prints a NET line beside TOTAL: distinct programs whose base reading (the last clean reading before the window, else the first clean reading inside it) was not PASS and whose latest clean reading is PASS, plus the lost count; `--names` lists the lost; `--include-dirty` restores dirty stamps as positions. TOTAL is kept and relabelled by this finding as transitions.

**The retraction.** Every citing sentence in GOAL-COO.md (12) is rewritten in place to "package UP-TRANSITIONS … RETRACTED COO-50". Any report that relayed 504 (or 494, 488, 466, 440, 427, 424) as programs to Lon carries the same correction: the number of distinct package programs newly green since 2026-09-06T20:31Z is **200** (m4) / **201** (m3) / **203** (either mode).

**Lesson.** A number is not the measure until the instrument prints the measure's own definition beside it. The tool said "newly-passing"; the ledger said "distinct"; nobody ran the definition.
