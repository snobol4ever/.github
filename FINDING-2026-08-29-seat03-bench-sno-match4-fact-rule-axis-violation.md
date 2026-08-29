# FINDING — `bench_sno_match4.sh`'s printed `ratio=` is the wrong axis and doesn't use `lib_perf_fmt.sh`

## WHAT, WHERE
`scripts/bench_sno_match4.sh:66` (post-fix line numbers; see row `bench-sno-match4-progs-space-evasion` for
the two blocking bugs this row actually fixed — corpus flat-path resolution and `mkrep`'s single-token regex):
```
echo "$p: scrip_m4=${mm}ms sbl=${sm}ms ratio=$(python3 -c "print(f'{$mm/$sm:.2f}')") identity=OK"
```
`ratio = mm/sm = ours/reference` (ms, lower is faster) — the FACT RULE's axis is `reference/ours` (higher is
faster), and the terminal authority for printing it is `lib_perf_fmt.sh`'s `perf_mult`/`perf_pct`/`perf_row`
(RULES.md § FACT RULES; "the ONE AUTHORITY for printing a multiple; a harness that cannot load it REFUSES
rather than inventing a format"). This script never sources `lib_perf_fmt.sh` and prints a bare number with no
colour channel. Live sample from a real run today: `calculator-1-match: scrip_m4=5690ms sbl=1761ms ratio=3.23`
— read naively that suggests "3.23x", but on the mandated axis SCRIP is 1761/5690 = **0.31x** (i.e. running at
about a third of the reference's speed on this kernel), the opposite impression.

## WHY NOT FIXED HERE
Out of `bench-sno-match4-progs-space-evasion`'s scope (that row is PROGS-validation + the two DONE-WHEN
blockers named above; this is a reporting-format defect, not a correctness one) and not a DONE-WHEN blocker —
the script still exits 0 and the identity check still gates correctness. Didn't want to change a benchmark
script's stdout shape as a drive-by inside an unrelated row without review, in case anything greps `ratio=`.

## SUGGESTED CURE
Swap the python one-liner for `sm/mm` (or source `lib_perf_fmt.sh` and call `perf_mult` like the other bench
scripts do) and relabel the field so the axis is self-evident (`x_vs_sbl=` not `ratio=`).
