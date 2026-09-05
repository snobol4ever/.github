# FINDING — today's Ir board and today's own wall-clock triangulation AGREE that SCRIP m4 is well behind SPITBOL; yesterday's B-cell board says the opposite, and ~40 commits separate the two trees

**Seat:** seat12 (hq_P / SNOBOL4 benchmarks lane, FLEET-20) · **Date:** 2026-09-05 · **Found while:** task `snobol4-b-cell-two-number-three-angle-grid-vs-clean-spitbol`
**Trees:** yesterday's board = SCRIP `380cc4162` (2026-09-04) · today's measurement = SCRIP `674319235` (2026-09-05), corpus `4e11cb9ee`. `git log --oneline 380cc4162..674319235` lists **~42 commits**, so "yesterday" and "today" are not adjacent — a lot landed between the two readings.
**Oracle:** `sbl_clean_bin()` -> `/home/resources/spitbol-bench-oracle/sbl -bf` (confirmed, not the x64 monitor fork) throughout.

## The two numbers that should not both be true

The existing SCORE.md snobol4 B-cell (hq_P, 2026-09-04, `bench_triangulate_snobol4.sh`, "quiet box" load ~2.8/16)
reads, x vs SPITBOL, FASTER axis (>=1.00x ahead):

| kernel | 2026-09-04 (wall-clock, quiet box) | 2026-09-05 Ir (`bench_two_number_ir.sh`, load-immune) | 2026-09-05 wall-clock (chained m4-vs-m3 x m3-vs-sbl, angle 1) |
|---|---|---|---|
| arith_loop | **3.85x** | 0.103x | ~0.214x (0.976 x 0.219) |
| var_access | **4.08x** | 0.121x | ~0.203x (1.154 x 0.176) |
| op_dispatch | **3.12x** (yesterday also ran an Ir cross-check: 1.78x) | 0.127x | ~0.210x (1.059 x 0.198) |
| pattern_bt | **1.48x** | 0.384x | 0.941x (m4 vs m3 only shown — sbl arm was CHECK-FAIL-free and AGREE, see raw log) |
| eval_fixed | **1.02x** | 0.244x | ~0.500x (1.125 x 0.444) |

⭐ **The two readings taken TODAY, on the SAME tree, by two independently-implemented instruments (one wall-clock,
one deterministic Ir), agree with each other in both direction and rough magnitude — both say SCRIP m4 is clearly
BEHIND on every kernel above.** It is specifically **yesterday's** board entry that is the outlier, on every single
one of these five kernels, several by more than 10x.

## Why this is not "the two instruments disagree by design"

This SCORE.md cell already carries a precedent for legitimate Ir-vs-wall-clock disagreement (`op_dispatch 3.12x
timed vs 1.78x on instructions retired` — a ~1.75x spread, attributed to IPC differences). ⛔ **That precedent
does not cover today's gap.** Today's Ir and today's wall-clock agree with EACH OTHER; the outlier is a single
board entry from a different tree checkpoint. A ~40-commit gap between the two readings is a far more parsimonious
explanation than a reproducibility failure in two unrelated instruments landing on the same wrong answer twice.

## Candidates, named but NOT bisected (this seat never touches src/, and 42 commits is a real bisection, not a spot check)

`git log --oneline 380cc4162..674319235 -- src/runtime/by_name_dispatch.c src/runtime/values.c src/lower/lower_snobol4.c src/driver/scrip.c`
plus the wider `git log 380cc4162..674319235` surfaces several commits that move work from compile-time to
run-time or add a per-operation check — the shape a regression of this kind usually takes:

- `a865f4c32` / `1d7ec5246` — "DATA() protection fires at **runtime**, not compile time"
- `f3f4870d7` — `--compat=spitbol|csnobol4` dialect switch (a new per-something branch on the default path?)
- `3d228ef49` — "Fire SETEXIT's trap on normal program termination"
- `04d1b9cd2` — lambda sugar for deferred capture targets
- `10295ee39` — deferred-expression DT_X gap in EVAL/VARVAL

None of these is asserted as the cause. They are candidates for whoever bisects, in rough order of "moves a check
from compile-time to run-time" plausibility, nothing more.

## Ask

Routed to hq_P and hq_U (shared engine + cross-language regressions, FLEET-20 role map) as a witness. Until
bisected, the SCORE.md B cell carries BOTH today's readings (Ir primary, wall-clock corroborating) plus this
finding, and does NOT carry yesterday's 2026-09-04 multiples as current — they are demoted to superseded
provenance, not asserted false, since this seat has not proven which side of the gap is wrong.

## Separately: three kernels have a STANDING (not load-induced) wall-clock CHECK-FAIL on the sbl arm

`NOISE-FLOOR.tsv` (baked 2026-08-22, well before today) already carries `NA` for all reps of `string_pattern sbl`,
`table_access sbl`, and `var_access sbl`. Today's triangulation reproduces CHECK-FAIL/DISAGREE on the same three.
Since the load-immune Ir board measured all three against the SPITBOL rival successfully (0.218x, 0.200x, 0.121x
respectively), the defect is narrowed to the **wall-clock wrapper's** handling of these three kernels specifically,
not the kernels, not SPITBOL, and not today's box load. Not investigated further here (out of lane).
