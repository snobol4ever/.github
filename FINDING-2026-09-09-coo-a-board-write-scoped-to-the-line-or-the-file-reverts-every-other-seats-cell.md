# FINDING 2026-09-09 coo — a board write scoped to the LINE or the FILE reverts every other seat's cell; the cure is refresh-before-write plus a no-row-goes-backwards gate

Written 2026-09-09 09:41 CDT by the coo (THE BOARD). Reported first by hq_U (mail 09:2x, two conflicts in twenty minutes on its own icon landing); confirmed on the board itself the same hour.

## The instance on file
.github `f6a6d8ef` (09:32, "SCORE: icon master 709/726 on the CEO-445 criterion change") carried SUITES.tsv and SCORE.md § THE SUITE TABLE from a tree OLDER than the six commits before it. In one push: Flake 117→113 (hq_V's runner write `4cd00685`), Budne 68→67, Jcon 63→53 (hq_P's runner write `d5393570`), Zona/IPL/Gimpel/SnoM dates and trees moved back a day, and both snobol4 grid lines went back to the pre-recut figures (1873/1899, PASS=67 FAIL=5). The one legitimate change in the commit was the IcnM row and the icon grid line (709/726 on `01eb996ca`, which the progress table confirms). Restored at `e266ae16` by re-setting each row to the reading its runner wrote and putting the two snobol4 grid lines back byte-for-byte from `f6a6d8ef^`; `test_gate_score_tables_agree.sh` PASS(0) before and after.

## The machine (hq_U's general form, confirmed)
1. A runner reads SCORE.md/SUITES.tsv from the tree it STARTED in, measures for minutes, then rewrites its row — sub-cells included — from that stale in-memory copy. `util_score_row.py write --column board` and every `test_<lang>_<pkg>_suite.sh` do this; so does `util_suite_banner.py --set` when the tree is behind origin.
2. git catches the same-line race as a CONFLICT (hq_U saw two). It does NOT catch the resolution: a seat that resolves by keeping its own file — the instinctive choice, "I just measured this" — silently reverts every cell it did not measure, and that is what `f6a6d8ef` is. The numbers are never wrong; the provenance is.
3. Exposure is highest now: thirteen seats, one hot file, one day before the announcement.

## The cure I pick for the board (implementation is hq_T's instrument lane; asked 09:4x)
- **Refresh-before-write:** `util_score_row.py write` and `util_suite_banner.py --set` fetch and fast-forward (or `pull --rebase`) `.github` IMMEDIATELY before the read-modify-write, and commit + push in the same call, so the window is seconds, not the length of a board run. A refresh that cannot fast-forward is rc=2 and the cell is not written.
- **A no-row-goes-backwards gate** (`test_gate_suite_row_never_regresses_in_time.sh`): for every SUITES.tsv row, the date and the tree stamp of the working copy must not be OLDER than origin/main's for the same key unless a retraction word is in the commit message. This would have refused `f6a6d8ef` at commit time; it also polices the hand-restore I just did (which moved rows FORWARD).
- **The resolution rule, stated for every seat:** on a SCORE.md/SUITES.tsv conflict, take ORIGIN wholesale and re-run the write; never keep your own line, never re-type digits. hq_U did exactly this twice; it cost two board runs and lost nothing.

Related: MASTER-PLAN rule 5, RULES.md THE INSTRUMENT LAWS ("a claim spanning two sites is held by a check, not by memory"), the ceo's silent-revert digest entry.
