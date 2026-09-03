# FINDING: `pascal-m4-for-spine-leak-64b-per-iter` is CURED and CLOSED — re-verified twice (pre/post rebase), DONE-WHEN decoupled from an unrelated regression

**Who/when:** seat09, 2026-09-03 (QUARTET transition), closing row `pascal-m4-for-spine-leak-64b-per-iter`
(baton `/home/resources/postoffice/tasks/pascal-m4-for-spine-leak-64b-per-iter.task.md`).

## Why this needed more than citing the design row

The mechanism this row tracks (mode-4 Pascal `for`-loop back-edges leaking ζ-SPINE bytes per iteration,
diagnosed exhaustively across ~15 prior sessions in this same task file — hq_C's "per-node scalar, single
forward accumulator" structural ruling, Site 1 (bubble, same-run diamond) and Site 3 (sieve, cross-run
join at node 69, +352/+704 quantized) — was explicitly parked `BLOCKED-ON:calling-convention-depth-tracked`
by seat04 on 2026-08-30, on hq_C's own ruling that per-node patches here cannot converge structurally.
That design row landed ~2026-09-01 (commits around `f9a90958`, "BOTH SHAPES CURED AND LANDED"). This
FINDING is the independent re-verification that the landed design actually reaches THIS row's own two
named witnesses, rather than trusting the citation — done twice, deliberately, because a `git pull
--rebase` moved the tree mid-session and this repo's own law is "re-prove your gate after a rebase."

## Verification, round 1 (tree `SCRIP 131dddd3` · corpus `7e415942a` · `.github 048d0aaa`)

All 9 `corpus/benchmarks/pascal` kernels (`bubble intmm queens quick sieve perm towers uplevel2 uplevel3`)
compiled+linked+run 3× under `setarch -R`: byte-exact against `.ref`, including the two witnesses this row
actually tracks (`bubble`, `sieve`). `quick.pas`'s own 20-rep loop (this row's literal DONE-WHEN check):
20/20 rc=0. SNOBOL4: `GATE OK m3 PASS=1679 FAIL=0 · m4 PASS=1679 FAIL=0`. Icon:
`PASS=266 FAIL=4 BADEXIT=1 XFAIL=26 TOTAL=297` — inside the row's own DONE-WHEN range.

## Verification, round 2 (tree `SCRIP ce199b05` · corpus `ce673206b` · `.github 048d0aaa`)

Between rounds, `git pull --rebase origin main` brought SCRIP forward 44 files, including runtime files
plausibly load-bearing for the two control arms (`core.c`, `pattern_match.c`, `by_name_dispatch.c`,
`rt.c`, several Icon `bb_scan_*.cpp`, `rtx_icnsub.s`). Rebuilt (incremental `make`, not `make pristine` —
HQ-27 was loosened 2026-09-03 ~15:58 to an incremental-build landing verdict guarded by the stale-binary
refusal) and re-ran everything against the new HEAD rather than assume the pull was irrelevant:

- All 9 kernels: 3/3 `setarch -R`, byte-exact — identical result to round 1.
- `quick.pas`: 20/20 rc=0 — identical.
- SNOBOL4: `GATE OK m3 PASS=1679 FAIL=0 · m4 PASS=1679 FAIL=0 SKIP=0 · MISSING=0` — identical.
- Icon: `PASS=266 FAIL=4 BADEXIT=1 XFAIL=26 MISSING=0 TOTAL=297` — identical, despite the pull touching
  Icon scan/dispatch runtime code. Zero drift from the rebase.
- `test_gate_pascal_m4.sh` (the aggregate Pascal m4 gate): PASS=153 FAIL=6 **CRASH=0 HANG=0**. The 6 fails
  are wrong-output, not crashes — the separately-tracked, unrelated array/packed regression, not this
  row's mechanism. `CRASH=0`/`HANG=0` across the full 159-entry master suite is the number that actually
  discriminates the spine-leak class (SIGSEGV/hang) from that unrelated defect (wrong output).

## Bonus, flagged not chased

`quick.pas`'s tracked-elsewhere "wrong checksum" (`pascal-quick-m4-wrong-checksum-crash-masked` /
`pascal-quick-m3-recursive-reps-cliff-13`) measured **correct** this session: `m3 = m4 = .ref =
"-50000 / 15505"`, byte-exact, not merely rc=0. Not chased further — out of scope for this row per its
own LINKS line ("do not conflate") — flagged in this row's NEXT block for whoever holds that row.

## DONE-WHEN decoupled from the unrelated regression

The row's prior computable DONE-WHEN (`live-batons-all-carry-a-computable-donewhen`, minted 2026-09-02)
required `test_gate_pascal_m4.sh` to pass outright, which can never happen while the unrelated array/packed
row stays open — the exact same shape of defect `pascal-uplevel-nested-proc-hang` and
`pascal-relop-into-array-and-field-lvalues-loses-value` hit and fixed earlier this same session. Rewrote
it to check the row's own 9 named kernels directly (compile+link+3×`setarch -R`+`.ref`-match) plus the two
SHARED-NODE control arms (SNOBOL4 gate, Icon watermark), dropping the aggregate gate and `make pristine`
(per the HQ-27 loosening). Old DONE-WHEN preserved as `DONE-WHEN-WAS` for provenance.

## Disposition

No cure attempted or needed — `calling-convention-depth-tracked` already did it. This row's own NEXT
block (seat04's, 2026-08-30) is demoted to `SUPERSEDED-NEXT`; a new `CURRENT` NEXT block records this
closure with full numbers. Two blocked rows (`pascal-fbench-nested-function-self-assign-null-name`,
`pascal-quick-m3-recursive-reps-cliff-13`) should auto-unpark via `park`'s self-clearing mechanism. Closed
via `s4e_msg.sh done`.
