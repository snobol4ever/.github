#!/usr/bin/env bash
# bisect_probe_m1_findfix.sh — INVERTED wrapper around bisect_probe_m1.sh, for hunting the commit that
# FIXED M1 rather than the one that broke it.
#
# ⛔ WHY A WRAPPER AND NOT A FLAG: git bisect's vocabulary is fixed — "good" means the OLD state and "bad"
# the NEW one. When the old state is BROKEN and the new state WORKS (which is the case for rung C-0: 278
# bytes at cd13321e, fixed point at 457dc5d9), the polarity must be inverted or git reports the merge base
# as inconsistent and the run is meaningless. Measured the hard way by hq_C 2026-08-22: the first attempt
# ran `git bisect start 457dc5d9 cd13321e` against the UNinverted probe, which labels HEAD good and the
# base bad — the exact contradiction of what was declared.
#
# usage:  git bisect start <FIXED-commit> <BROKEN-commit>
#         git bisect run .github/probes/m1-bisect/bisect_probe_m1_findfix.sh
#   git's reported "first bad commit" IS THE CURE.
#
# exit 0 = still broken (git: "good"/old) · exit 1 = fixed (git: "bad"/new) · 125 = skip, unchanged
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$HERE/bisect_probe_m1.sh"; rc=$?
case "$rc" in 0) exit 1;; 1) exit 0;; *) exit "$rc";; esac
