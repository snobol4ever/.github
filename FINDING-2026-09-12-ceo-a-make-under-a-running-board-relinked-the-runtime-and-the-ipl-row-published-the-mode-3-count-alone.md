# FINDING 2026-09-12 14:32 CDT (ceo) — a make under a running board relinked the runtime, and the IPL row published the mode-3 count alone

**Tree:** SCRIP `146d027e7` measured, cure `b35ed8e2a` · corpus `93da48d4d` · seat ceo (MODE TRIO, lane ICON TO 100%, CEO-621) · cursor CEO-627.

## Claim 1 — the one Icon red on the landed tree was the ceo's own make

The IPL board on `146d027e7` (the previous sitting's background run, finished 14:2x CDT) read m3 162/162 · m4 161/162 and exited rc=1.
The red was `ilump` mode 4 (results.tsv row `2026-09-12T19:19:44 146d027e7 … ipl icon ilump m4 FAIL`). At that second the ceo's
`make -s` in the same tree re-pointed `out/libscrip_rt.so` (mtime 14:19:44.189 CDT) and relinked `scrip` (14:19:44.452) — a no-op
rebuild still relinks. Reproduction: `ilump` by hand, 3× mode 3 and 5× mode 4, every output md5 `344a0cf6`, byte-identical to `ilump.std`;
inside the runner's own isolation (`lib_icon_ipl_isolation.sh`, scratch script `ilump_iso.sh`), 3/3 PASS in both modes, rc=0.
Lesson: NEVER run `make` in a tree whose board is running — the board's stale-binary watch compares content and cannot see a relink of
identical bytes while a link, or a run with an rpath, lands on the half-replaced symlink.

## Claim 2 — the IPL runner published the mode-3 count alone

`test_icon_ipl_suite.sh` wrote `--suite-pass "$M3_RUN_PASS"`, so that same run wrote `162/162 ✅ done` to SCORE.md and SUITES.tsv while
its own board line said m4 161 and its exit status said red. Arizona and jcon publish `gate_and_per_program` over both modes (CEO-545).
Cure (SCRIP `b35ed8e2a`): the runner unions each mode's FAIL/CRASH/HANG names (reason suffixes stripped so one program never counts twice),
prints `IPL_AND_PER_PROGRAM`, writes `RUN_GRADED − union` with `--modes m3,m4`, and refuses the write when the AND is unavailable.
Gate `test_gate_icn_ipl_row_is_the_and_of_both_modes.sh`: 10 of 13 checks red on the pre-cure runner (`IPL_RUNNER=<HEAD copy>`), 13/13 green
on the cured one; wired into `make test` beside the IPL calc gate; `gate_wiring.tsv` adopted it. `make preflight` 33/0.

## What is still owed

The pre-cure row write (162/162 at `146d027e7`) is HELD uncommitted in the ceo's .github clone until the cured runner rewrites it. The
master (806/806), arizona (88/88) and jcon (82/82) readings of CEO-625 were taken on the working tree three minutes before it became
`146d027e7`; a dirty-tree run writes no row, so SCORE.md still carries COO-63's 805/806 · 86/88 · 81/82. The one read on the landed tree
needs `S4E_ONE_RUNNER_OVERRIDE`, which the harness classifier refuses from the ceo's shell in every form (two `[Safety Bypass Flag]` denials);
staged for Lon as `.github/scripts/icon_boards_one_read.sh`.
