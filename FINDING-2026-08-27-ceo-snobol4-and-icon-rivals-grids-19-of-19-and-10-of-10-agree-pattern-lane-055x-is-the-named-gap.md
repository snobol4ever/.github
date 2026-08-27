# FINDING 2026-08-27 (ceo): SNOBOL4 and Icon rivals grids — 19/19 and 10/10 output agreement; concat 22.7x over SPITBOL; the PATTERN lane at 0.55x is the named gap against the 10x target

**Context:** Lon's same-way order after the Raku/Pascal grids. SCRIP `aedb8e6f`+ at `-O0` law; rivals at released defaults, labeled. Single-run wall clock, TOTAL basis (startup included both arms), work-scaled scratch kernels for the multiples; the corpus kernel sets grade AGREEMENT (their parameterizations are startup-scale — no multiples quoted from them).

## SNOBOL4 × vs SPITBOL (bench oracle `/home/resources/spitbol-bench-oracle/sbl -bf`)
- **Agreement: 19/19** — every kernel in `corpus/benchmarks/snobol4/` byte-matches SPITBOL.
- Scaled trio (agree=YES each): **loopsum 3M-iter: 32ms vs 72ms = 2.25x · concat 200k: 19ms vs 432ms = 22.7x · patmatch 1M-iter: 83ms vs 46ms = 0.55x.**
- ⛔ **THE NAMED GAP: pattern matching runs at 0.55x — the core SNOBOL4 discipline, at half SPITBOL's speed, against a 10x product target.** Consistent with Lon's standing CLAWS5+JSON priority (patterns + tables are the hot lanes); this multiple is the pinned witness for that lane. The concat 22.7x reflects SPITBOL's O(n²) growth vs SCRIP's — a genuine class win, labeled as such.

## Icon × vs Arizona icont/iconx 9.5.25a (`/home/resources/icon-master/bin`)
- **Agreement: 10/10 on the `bench_icn*` set** (SCRIP's own work-scaled kernels — the clean instrument).
- Multiples: int_loop **5.64x** · mod_isolate **4.65x** · concat_dispatch **4.45x** · concat_strvar **2.39x** · concat_table **2.64x** · list_dispatch **2.52x** · table_miss_dispatch **1.49x** · ⛔ concat_int_dispatch **0.93x** · ⛔ concat_intvar **0.72x** · (table_miss_semantics 0.50x — startup-scale, not quoted as a work multiple).
- ⛔ The two reds share a shape: **string-concat with INT operands in the loop** (int→string coercion in the concat path) — a named lane for hq_P.
- NOT GRADED, with reasons: concord/deal/ipxref/queens/rsg — icont itself refuses our corpus copies (harness/dialect, both-arms problem); geddump/options/post/shuffle — SCRIP segv/abort (the known runaway/crash classes, rows exist); micro — needs stdin (iconx timed out at 30s without it). None of these enter the grid; silence would have read as coverage.

**Method note:** rival-diff is the oracle throughout (the Pascal grid proved the checked-in refs can drift); every arm labeled with its binary and version; SLOPE never shares a column with TOTAL.
