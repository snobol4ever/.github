# FINDING-2026-08-22-hq_P-scoreboard-17-kernels-and-scrip-scales-worse

FROM hq_P (HQ-PERFORMANCE), s259. Closes the rank-0 row `bench-rebaseline-15-kernels-clean-oracle`
(it is **17** kernels, not 15). Replaces the s256 ratio table in `GOAL-HQ-PERFORM.md`, which predated the
`NV_*` memo and everything since. **Contains a correction to this seat's own headline number from earlier
today.**

## Method

Every kernel, both engines, identical treatment. SCRIP mode-4 native binary (compile excluded by
construction), RT_OPT=`-O2`, SCRIP `e88e77db`; oracle is the s255 clean benchmark binary
`/home/resources/spitbol-clean/sbl -bf -d512m -i64m` (⛔ never `x64/bin/sbl`). `valgrind --tool=callgrind`,
FIXED-WORK mode.

⭐ **Ir/iter is a TWO-POINT SLOPE, `(Ir(N2)-Ir(N1))/(N2-N1)`, not `total/N`.** That cancels fixed start-up
**exactly** instead of assuming it negligible — and it is not negligible: roman's start-up is **~9.3M Ir**,
which is 97% of an N=20 run. Every run of both engines was diffed against the kernel's `.ref` before its
number was used.

## The scoreboard — N=20 → 200

**Ratio > 1 means SCRIP is slower.** SCRIP wins 6 of 17.

| kernel | SCRIP Ir/iter | clean SPITBOL | ratio | verified |
|---|---|---|---|---|
| `fibonacci` | 587,785 | 979,240 | **0.60 — SCRIP 1.67x FASTER** | both |
| `var_access` | 490 | 646 | **0.76** | both |
| `func_call` | 419 | 518 | **0.81** | both |
| `op_dispatch` | 481 | 573 | **0.84** | both |
| `arith_loop` | 327 | 338 | **0.97** | both |
| `ident_call1` | 403 | 392 | 1.03 | ⛔ **UNVERIFIED** |
| `ident_call2` | 417 | 388 | 1.08 | ⛔ **UNVERIFIED** |
| `array_sum` | 323,349 | 254,317 | 1.27 | both |
| `eval_fixed` | 1,851 | 1,243 | 1.49 | both |
| `pattern_bt` | 3,933 | 1,790 | 2.20 | both |
| `indirect_dispatch` | 1,606 | 695 | 2.31 | both |
| `table_access` | 733,282 | 313,350 | 2.34 | both |
| `string_pattern` | 2,021 | 860 | 2.35 | both |
| `string_manip` | 1,872 | 699 | 2.68 | both |
| `mixed_workload` | 43,644 | 14,789 | 2.95 | both |
| `roman` | 29,168 | 5,966 | **4.89** | both |
| `string_concat` | 0.1 | 0.2 | ⛔ **degenerate** | both |

⭐ **The s256 shape holds and is now better attested:** SCRIP wins on scalar/register-resident work and loses
on tables, strings, patterns, and whole realistic programs. `mixed_workload` at **2.95x** is the most
representative single number on this board.

## ⛔ CORRECTION TO THIS SEAT'S OWN HEADLINE, PUBLISHED EARLIER TODAY

I published **roman = 5.46x** in `...hardened-nv-memo-is-17-percent-not-25.md`, in the cursor, and to hq_C.
**The correct same-method figure is 5.87x.** The SCRIP half (43,478.9 Ir/iter at N=20000) was right; the
error was dividing it by the **stale s256 SPITBOL figure of 7,966**, taken at a different N by a different
method, rather than measuring the oracle myself. Measured now: clean SPITBOL roman at N=20000 is
**148,252,805 Ir = 7,412.6/iter**.

⛔ **The error flattered us** — it reported the gap as smaller than it is. ✅ **The `-17.1%` improvement claim
is UNAFFECTED**, because that is SCRIP-vs-SCRIP against a baseline taken the same way.

**Rule adopted:** never divide a fresh number by an inherited one. If a ratio is published, **both halves are
measured in the same session by the same method.**

## ⭐⭐ THE NEW RESULT: SCRIP SCALES WORSE THAN SPITBOL

roman's work per iteration genuinely grows with N **by design** — the kernel converts a *different, larger*
integer each iteration (1001…1000+N), so numerals lengthen and recursion deepens. That is the kernel being
honest, not a defect. But measuring both engines across the same growth is diagnostic:

| regime | SCRIP Ir/iter | SPITBOL Ir/iter | ratio |
|---|---|---|---|
| small-N (20 → 200) | 29,167 | 5,966 | **4.89x** |
| large-N (2,000 → 20,000) | 43,845 | 7,438 | **5.89x** |
| **growth factor** | **1.50x** | **1.25x** | — |

⛔ **SCRIP's per-iteration cost grows 1.50x across that range where SPITBOL's grows 1.25x. The gap WIDENS
with input size.** Small benchmarks therefore *understate* how far behind we are on real work, and the 10x
target is harder at scale than this board's small-N column suggests.

⭐ This is consistent with the mechanism already found: roman's cost is dominated by a deferred node re-read
**by name** at every unanchored start position, so longer subjects mean more retries **and** each retry pays
a full name resolution. A by-name cost is inherently superlinear in subject length in a way SPITBOL's
`vrblk`-pointer discipline is not. **This is the strongest argument yet for the rank-1 `name-lookup-strcmp`
class** — it is not merely a constant factor.

## ⛔ Honest limits — three rows on this board are not fully trustworthy

1. **`ident_call1` / `ident_call2`: UNVERIFIED.** Their `.ref` files are **empty**, so there is no
   `check:` line to diff and neither engine's output was validated. Their ratios (1.03, 1.08) are printed
   for completeness and **must not be quoted as results.** ⭐ Two benchmark kernels with empty oracles is
   itself a defect — filed as a row.
2. **`string_concat`: degenerate.** Slope ≈ 0.1 Ir/iter — its work does not scale with `fixed_n` the way the
   others do (a pinned `ZK` reused as batch size). The **ratio is meaningless**; the kernel needs its own
   convention before it can appear on a board.
3. **Regime.** The main table is the **small-N** regime. Any kernel whose work per iteration varies with N
   (roman certainly; others unchecked) will read differently at larger N — roman moves 4.89 → 5.89. ⛔ A
   single-number ratio for such a kernel is incomplete without its N.

Not re-run for repeatability: callgrind Ir is deterministic, so repetition adds nothing on a fixed tree — but
every number here is void on a changed tree.
