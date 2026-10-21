# GOAL-HQ-PACKAGES — THE VENDORED PROLOG TEST PACKAGES TO 100%

**Opened 2026-10-21 18:0x CDT by Lon in-chat to the ceo, verbatim:** *"Scan the fleet workload and determine a new HQ position which we can start to help get the queue cleared."* · *"I want to name it HQ-PACKAGES. I'm going now to create the folder."* (ceo CEO-1874). Seat `hq_packages`, root `/home/claude_packages`, digest `.github/HQ-PACKAGES-CLAUDE.md`, stocked by `.github/scripts/populate_packages_root.sh`. Prolog's law is `GOAL-PROLOG-100.md` and binds this seat; this file holds only the seat's cursor.

## WHY THIS SEAT

The ceo's scan of 2026-10-21 17:5x: of the three languages in `ORDER-OF-WORK` (icon prolog snobol4), Icon had 5 failing programs left and SNOBOL4 almost none, while Prolog's vendored packages held about 1,500 -- XsbTests 737 of 899, SWI 639 of 2768, TreallaTests 117 of 331, ProPuzzles 17 of 22 (SUITES.tsv). XSB's 737 had ONE row (claimed 92 h untouched) and Trealla's 117 had none, so the debt was larger than the queue said; hq_prolog held 3 claims with 23 FREE rows behind them and the spine conversion on top.

## THE LANE

XsbTests (`corpus/packages/prolog/xsb_tests`, suite key `xsb`), SWI (`swi_tests`, `swi`, tabling included), TreallaTests (`trealla_tests`, `trealla`), ProPuzzles (`puzzles`, `puzzles`), each to 100% over its printed denominator, each graded against the implementation it came from. hq_prolog keeps ProRungs, Logtalk, INRIA, GNU, ProRosetta and Prolog's spine arm; the cfo finishes the two SWI/GNU rows it holds. MODE's language lane `prolog` stays hq_prolog's: this seat works the rows the ceo reowns or assigns to it, and mints its own with `--owner hq_packages`.

## THE METHOD

1. Per suite, read the coo's newest rows (`results.tsv`, `util_suite_row_at_or_after.sh`), class the reds by test file and cause, and ROW each class with a witness DONE-WHEN cut from the oracle (no prose finish line; `mint` refuses one). A program the oracle gives no answer for leaves as NO_ORACLE_ANSWER (CEO-1696), never as debt.
2. Cure one class per landing: the row's DONE-WHEN plus at most eight representative programs (`test_feature_reps.sh`), push, `done`, `next`. Every pass of a package is the coo's (`s4e_test_request.sh <key> --part ...`).
3. The monitor bracket first (`monitor_run.sh <prog> --oracle`, gprolog or swipl fork), then ASM-DIFF-FIRST.

## LIVE CURSOR

- **2026-10-21 18:0x CDT, ceo (CEO-1874): the seat is opened.** The bus knows it (harness 21bc080: /home/claude_packages resolves to hq_packages in s4e_msg.sh, s4e_inbox_hook.sh, util_score_row.py). Lon creates the root; `populate_packages_root.sh` stocks it; the ceo flips MODE to seventeen seats and reowns the package rows when the session is live.
