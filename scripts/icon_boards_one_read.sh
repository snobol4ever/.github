#!/usr/bin/env bash
# icon_boards_one_read.sh — ONE read of the Icon master and the three Icon packages on the landed tree (ceo CEO-621/627).
# Lon runs it from the ceo seat with `! bash /home/claude_ceo/.github/scripts/icon_boards_one_read.sh`: the harness classifier
# refuses the one-runner override from the ceo's own shell in every form. Runs from the ceo's SCRIP clone on origin HEAD, one
# clean tree, ⛔ NO make while it runs (a no-op make relinks scrip and out/libscrip_rt.so under the board — the ilump precedent).
# Each runner writes its own SCORE.md row (util_score_row.py); this script prints the four board lines and the rows changed.
set -uo pipefail
ROOT="${S4E_HOME:-/home/claude_ceo}"; cd "$ROOT/SCRIP" || exit 2
[ -z "$(git status --short)" ] || { echo "⛔ REFUSE(2): SCRIP tree is dirty -- a board grades a clean tree on origin HEAD"; git status --short | head; exit 2; }
git fetch -q origin && [ "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)" ] || { echo "⛔ REFUSE(2): HEAD is not origin/main -- merge --ff-only first"; exit 2; }
make -s >/dev/null 2>&1 || { echo "⛔ REFUSE(2): make failed"; exit 2; }
export S4E_ONE_RUNNER_OVERRIDE="Lon for the ceo: CEO-621 one read of the Icon suites on the landed tree $(git rev-parse --short HEAD), the coo is quiet"
LOG="${TMPDIR:-/tmp}/icon_boards_one_read.$(date +%Y%m%dT%H%M%S)"; mkdir -p "$LOG"
echo "tree SCRIP=$(git rev-parse --short HEAD) corpus=$(git -C ../corpus rev-parse --short HEAD) start=$(date '+%H:%M:%S %Z') logs=$LOG"
for r in board_icon_master.sh test_icon_arizona_suite.sh test_icon_jcon_suite.sh test_icon_ipl_suite.sh; do
  t0=$(date +%s); timeout 1800s bash "scripts/$r" $(case $r in test_icon_arizona_suite.sh|test_icon_ipl_suite.sh) echo -v;; esac) > "$LOG/$r.log" 2>&1; rc=$?
  echo "=== $r rc=$rc $(( $(date +%s) - t0 ))s"
  grep -E 'ICON_MASTER|BOARD|AND_PER_PROGRAM|PACKAGE_INVENTORY|RUN_FAIL:|RUN_CRASH:|RUN_HANG:|FAIL:|REFUSE|rewrote|NOT UPDATED|OVERRIDE' "$LOG/$r.log" | head -20
done
echo "=== SCORE rows changed:"; git -C ../.github diff --stat -- SCORE.md SUITES.tsv; git -C ../.github diff SUITES.tsv | grep '^[-+][^-+]' | cut -c1-160
