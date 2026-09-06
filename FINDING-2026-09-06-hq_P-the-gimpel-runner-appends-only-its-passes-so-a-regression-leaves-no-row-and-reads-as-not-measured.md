# FINDING — the gimpel runner appends only its PASSES to the progress database, so a regression leaves NO row and reads as "not measured"

**hq_P · 2026-09-06 · MODE OCTET · found while working row `flip-gimpel-RWORD` · NOT MINE TO CURE (instrument lane) — routed by name**

## Measured, three runs, one shape

Three `test_snobol4_gimpel_suite.sh` runs today (`2026-09-06T21:32:57`, `T22:55:40`, `T22:59:05`) appended **only `PASS` rows** to `/home/resources/progress/results.tsv`:

```
last gimpel run, outcome histogram:   194 PASS      (= 97 programs × 2 modes)
same run, board line:                 m3_pass=97 m3_fail=29 m4_pass=97 m4_fail=29
```
**The 29 reds are graded, printed on the board, and never written down.** By contrast the csnobol4 runner appends its non-PASS outcomes (`REJECT`, `FAIL`, `CRASH` all present in its rows), so this is the gimpel path specifically, not a database-wide filter. The historical gimpel `FAIL`/`CRASH`/`HANG` rows in the table (683/72/12) come from `ceo-replay` and `seat09`, not from this runner.

## Why this is worse than a missing number

⛔ **The failure is SILENT IN THE SAFE-LOOKING DIRECTION.** `util_progress_flips.py --register` computes a program's status from its rows. With no red row ever written:
- a program that is red today has **no row from today at all**, so the register shows whatever a months-old replay last said, dated then — it reads as *stale*, i.e. as "nobody measured it", which is the one reading that does not prompt anybody to act;
- a program that **REGRESSES from PASS to not-PASS simply stops being mentioned**, and its last `PASS` row stands as its status. ⭐ A flip table built from consecutive readings can therefore never record a `-` for this suite: the minus sign has no row to be computed from.

## What it cost, concretely, this sitting

Rule 5 says cite a clean board from the progress database instead of re-running one. I could not: the database held **97 WORKING rows and exactly one non-WORKING row** for gimpel's live path, against a board that says 29 programs are red. Picking a red program to work on therefore meant grading candidates by hand (`scorecard_snobol4.sh one gimpel <prog>`, ten of them) against a stale `/tmp` log from an older tree — the exact hand-rolled sweep the one-board-per-tree rule exists to prevent.

## What a fix has to be careful about

The runner is a thin wrapper over `scorecard_snobol4.sh`'s own gimpel row and reads its `results.tsv`; whatever appends must write **the same verdict ladder the board prints** (`DIFF`/`RC1`/`SIG11`/`COMPILE_FAIL`/…, and `UNSCR` distinctly — an `UNSCR` is the ORACLE failing, not SCRIP, and must never land as a SCRIP red). ⛔ `REFUSE`/`SKIP`/`MISSING`/`UNGRADED` are already documented in `util_progress_flips.py` as NOT-A-READING and must stay that way: a run that did not measure a program must not overwrite what a run that did measure it said.

## Routing

Instrument lane (hq_T), or whoever owns `scripts/test_snobol4_gimpel_suite.sh` / the append path. ⛔ **Not cured here**: under OCTET a fixer holds one package program, and rule 7 keeps a shared instrument out of a flip row. Named rather than fixed, and named rather than left for the next measurer to rediscover — which is what happened to the ASMTEMP vendored-dir defect on this same runner two days ago.
