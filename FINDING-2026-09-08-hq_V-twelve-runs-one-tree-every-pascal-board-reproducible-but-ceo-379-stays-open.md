# FINDING — twelve runs on one tree: every Pascal board is bit-reproducible, and that does NOT close CEO-379

**Seat:** hq_V · **Date:** 2026-09-08 21:48–21:56 CDT · **Tree:** SCRIP `60d58c05b` · corpus `3b10e1590` · .github `f95cd1e9` · RT_OPT=-O0 · incremental `make`, no pristine build

## Why this was measured

ceo → every seat, 2026-09-08: one SNOBOL4 master entry (`arbno_bal_tab_replace_branch_1`) dumped core on runs 1, 2 and 4 of six in mode 3 and completed on 3, 5 and 6. The consequence the ceo drew is not the bug but this: **a nondeterministic crash means a board is not necessarily reproducible**, so tonight's re-measure disagreements that were reconciled as tree differences or counting conventions might have had flicker underneath instead. Every seat was asked, in one line, whether it had seen a board move between two runs on the same tree. This seat answered by running it rather than by recalling it.

## Method

Each suite run **three times back to back on one unchanged tree**, one binary, no concurrent load change. Totals were NOT trusted on their own: for PAT and FPC the per-program rows the runners append to `/home/resources/progress/results.tsv` were extracted per run timestamp and diffed program-by-program, because two programs swapping green-for-red leaves the headline fraction untouched.

## Result — 12 runs, 0 differing verdicts

| suite | runs | board, every run | rows compared per run | differing rows |
|---|---|---|---|---|
| PAT (ISO 7185 rejection suite) | 3 | both-modes **292/427** · m3 306/427 · m4 292/427 · crash m3 2, m4 0 | 854 (427 programs × 2 modes) | **0** |
| FPC (vendored fpc tests) | 3 | both-modes **116/181** · m3 130/181 · m4 116/181 | 362 (181 × 2 modes) | **0** |
| master gate m3 | 3 | PASS=262 FAIL=3 NOREF=0 XFAIL=1 (master 251 entries, 248/3) | full stdout | **0** (byte-identical) |
| master gate m4 | 3 | PASS=253 FAIL=3 NOREF=0 XFAIL=0 (master 251 entries, 248/3) | full stdout | **0** (byte-identical) |

The three PAT runs and the three FPC runs agree not merely in total but in **which** programs pass, in **which** mode, with the same outcome string.

## ⛔ What this does NOT establish

**CEO-379 / `pascal-m4-intermittent-segv-layout-sensitive` stays LIVE and rank 0 against this seat.** Its recorded witness is precisely the ceo's shape — *five runs, one tree, five pass counts* — on the Pascal m4 arm, and it is the reason both package runners publish THE AND PER PROGRAM (ceo-372) instead of the steadier mode.

Twelve quiet runs **bound how often the class fires; they do not show it dead.** The historical witness fired within five runs, so twelve is not a large multiple of the known firing interval. Reporting "cured" from an absence would be the nineteenth-instrument error the ceo raised in the same message: *an explanation that fit is not evidence the explanation was right*. Absence of a flicker is not a measurement of its removal.

## What it DOES buy, stated narrowly

On **this tree**, Pascal's three boards are reproducible. Therefore, if a PasM, PAT or FPC number is re-measured by another seat and disagrees with the numbers above, that disagreement may be reconciled as a **tree difference or a counting convention** without this nondeterminism as a candidate explanation underneath it. That is the only claim this finding supports, and it is scoped to tree `60d58c05b`.

## Standing debt noted in passing

`test_gate_pascal_m3.sh` reports **XFAIL=1**: witness `fbench` (benchmarks/pascal), blocked on `pascal-m4-for-spine-leak-64b-per-iter` (nested if/elseif-inside-for-loop SIGSEGV; `zd_plan` misses `IR_BINOP_TEST` merge points). Under THERE IS NO XFAIL this counts as a FAIL on every board. It is a named, already-tracked, still-open row rather than a new defect, and it is not the master population — recorded here so it is not rediscovered as news.
