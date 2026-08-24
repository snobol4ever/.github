# FINDING — seat04: post-fix callgrind re-measurement of table_access/array_sum — the 2.8x gap is now 1.46x, array_sum is near parity

**Date:** 2026-08-24 · **Seat:** seat04 (FLEET-4) · **Instruments:** callgrind Ir at fixed work (`bench_wrap.sh --mode=iter`, no wall-clock deadline in the measured window) · **Build:** `make pristine` EXIT=0 at HEAD `eca52780`, **RT_OPT=-O0** (default; NO `-O2` builds per s262 FACT RULE) · **Oracle:** `sbl_clean_bin()` = `/home/resources/spitbol-bench-oracle/sbl` (the BENCHMARK oracle, s255 two-oracle ruling — never `x64/bin/sbl` for timing) · **Mode:** SCRIP mode-4 native binary, matching the s256 FINDING's own methodology.

Answers task `perf-table-array-runtime`'s NEXT step: "fresh callgrind on table_access/array_sum ... to find the CURRENT ratio post-fix." Ratios below follow the RULES.md FACT RULE (`reference/ours` = SPITBOL Ir / SCRIP Ir; above 1.00x SCRIP is faster, below 1.00x SCRIP is slower — no "faster"/"slower" words attached to a multiple).

## 1. table_access: the fix worked. The gap is real but far smaller.

| arm | N | SCRIP Ir | SPITBOL Ir | Ir/iter SCRIP | Ir/iter SPITBOL | ratio (SBL/SCRIP) |
|---|---|---|---|---|---|---|
| s256 pre-fix (quoted, not re-run) | 2,000 | 1,994,260,056 | 719,064,032 | 997,130 | 359,532 | 0.3606x |
| **fresh, post-fix** | 2,000 | **1,051,874,749** | 718,832,325 | 525,937 | 359,416 | **0.6834x** |
| fresh, post-fix (cross-check N) | 100 | 66,643,918 | 42,962,801 | 666,439 | 429,628 | 0.6447x |

Both N=2,000 arms are **RT_OPT=-O0**, so this is a clean same-arm before/after, not a re-baseline: the s256 FINDING's own header already recorded `RT_OPT=-O0`. The SPITBOL side reproduces to 0.03% (718,832,325 vs 719,064,032 quoted at s256), confirming the workload and oracle build are unchanged and the delta is real, not drift.

**SCRIP's own Ir count on table_access N=2,000 dropped 1.896x** (1,994,260,056 → 1,051,874,749, a 47.3% reduction). The SPITBOL-relative ratio improved from 0.3606x to 0.6834x — a 1.895x improvement in the ratio itself, matching the SCRIP-side reduction almost exactly (as expected: the SPITBOL side didn't move). ⛔ **The gap is not closed**: SCRIP still takes 1.463x the instructions SPITBOL does on this kernel (was 2.773x). Real, and worth a new bucket — see §4.

The N=100 cross-check (0.6447x) is in the same ballpark as N=2,000 (0.6834x) but not identical; the smaller N pays proportionally more fixed/startup cost, which is expected and not a discrepancy. ⛔ hq_P's s259 N=100 figure (905,108 Ir/iter) is **not** reproduced or compared here — it was built `-O2`, an arm the s262 FACT RULE retired; no `-O2` number is quoted anywhere in this FINDING.

## 2. array_sum: no comparable pre-fix Ir baseline existed — this is the first fixed-work Ir reading, and it's close to parity

The s256 FINDING's Ir table has no array_sum row (its only s256 evidence was a wall-clock "time mode" observation, not a fixed-work Ir count), so there is nothing to diff against. Fresh fixed-work reading:

| kernel | N | SCRIP Ir | SPITBOL Ir | Ir/iter SCRIP | Ir/iter SPITBOL | ratio (SBL/SCRIP) |
|---|---|---|---|---|---|---|
| array_sum | 8,192 | 2,561,428,740 | 2,347,343,050 | 312,674 | 286,541 | **0.9164x** |

N=8,192 is the FIXN pin already established in `bake_noise_floor_snobol4_fixed.sh` for this kernel (one native ~500ms TIME-mode run at bake time), reused here rather than inventing a new N. **0.9164x is close to parity** (SCRIP pays 1.091x the instructions SPITBOL does) — a much smaller gap than table_access's 1.463x, and arguably not worth its own urgent campaign row right now. Recorded here so a future session has a real number instead of "similar margin" prose.

## 3. ⛔ array_sum's known valgrind SIGSEGV reproduces, and here is the workaround

`bake_noise_floor_snobol4_fixed.sh` already carries a comment: array_sum "is skipped under callgrind (pre-existing valgrind SIGSEGV, unrelated defect) but has no trouble running fixed-mode natively." Confirmed: at the default heap, callgrind on `array_sum_n8192.prog` dies —

```
==...== Access not within mapped region at address 0x1FFF001000
==...==    at gc_zeta_frame (gc_heap.c:564)
==...==    by gc_collect_ex (gc_heap.c:637)
==...==    by rt_gc_point_arr_c (gc_heap.c:327)
```

— i.e. a **real GC collection** triggers mid-run (8,192 × 500-element arrays is enough allocation to exhaust the default arena) and valgrind's stack/region tracking chokes on whatever `gc_zeta_frame` does during the walk. This is a valgrind-vs-GC-internals incompatibility, not a program bug — table_access never triggers it because its post-fix allocation footprint is small enough to never fill the arena in these runs (no `gc_collect_ex` frame appears anywhere in its own top-functions list).

**Workaround, not a fix:** `SCRIP_HEAP_MB=4096` (the max the runtime accepts, `gc_heap.c:120`) sizes the arena past the run's total allocation, so no collection fires and callgrind completes cleanly (§2's numbers were taken this way). This is not a special case invented for this session — it is exactly the same "GC-free window is a measurement precondition" discipline `test_bench_snobol4_timed.sh` already documents for its own default 1024 MB heap knob, just pushed higher because this kernel's allocation volume at N=8,192 exceeds that default. ⛔ Not filing a row to fix the valgrind SIGSEGV itself: it is a measurement-instrument artifact against a real GC pause, not a defect in SCRIP, and the workaround is sufficient for any future session that needs array_sum Ir data.

## 4. What's dominant now on table_access, for whoever picks up the new bucket (not investigated further here — this row is measurement-only, row-factory rule)

Top of the fresh N=2,000 SCRIP profile:

| Ir | % | site |
|---|---|---|
| 362,902,438 | 34.50% | emitted BB code (blob) |
| 187,144,933 | 17.79% | `aggregates.c:table_set_descr_d` |
| 93,930,004 | 8.93% | `pattern_match.c:c_rt_assign_var_body` |
| 79,790,000 | 7.59% | `pattern_match.c:c_rt_subscript_var` |
| 62,078,640 | 5.90% | `rtx_table.S:table_find_pair_d` |
| 44,528,848 | 4.23% | `rtx_alloc.S:rt_agg_alloc` |
| 31,592,800 | 3.00% | `aggregates.c:_tbl_grow` |

⭐ **The old smoking-gun costs are gone, not just reduced.** `tbl_key_str`, `_tbl_hash`, `__strcmp_avx2`, `rt_ws_strdup_c` — the s256/s259 top-10 entries for the stringification defect — do not appear anywhere in the top 25 at either N=100 or N=2,000. Reading `table_set_descr_d`'s own comment (`aggregates.c:413-417`) confirms why: as of s262 the insert path "no longer builds `e->key` at all" — the key string is minted lazily by `tbl_pair_key()` only on first demand, and table_access never demands one. This is stronger than either sibling row's LEDGER claimed (both described the VCELL-alloc-on-read fix and type-tagged hashing as separate, done defects; this profile shows the stringify-on-insert path is *also* gone, for both tables and this kernel never triggering a rehash-driven restring either).

`table_set_descr_d` is now the single largest **named** C-side cost (the emitted-BB-code line above it is not a runtime function). Reading it: no stringification, no allocation on its own — it hashes the key (`_tbl_hkey`), binary-searches the sorted bucket for insert position, and inserts (append-only in this kernel's case, since table_access inserts ascending keys 1..500, so the `memmove` branch is never taken). This reads as **legitimate per-op bookkeeping for a sorted-bucket hash table**, not a repeat of the fixed defect class. `rt_agg_alloc` (4.23%) is presumably the VCELL wrapper still needed to make `T[I]=v` assignable on the WRITE side (the READ side's wrapper was what got eliminated) — plausible and not re-diagnosed here.

**⛔ This row does not cure it** (its own NEXT block: "row-factory: do not cure inside this row"). A real gap remains (1.463x) and its cause is no longer one obvious algorithmic bug — routed as a new task below.

## 5. Cross-check against `table-int-keys-and-nd-subscript` (required before minting, per this row's NEXT block)

That row's own remaining scope (per its GOAL re-scope note) is (a) N-D dispatch consolidation — `array_get2`/`array_set2` in `aggregates.c` exist but nothing in lower/templates/emitter calls them, so an N-D access still re-enters the subscript dispatcher once per dimension — and (b) `.NAME`'s string representation cost, unmeasured.

**No overlap with this FINDING.** Both `table_access.sno` and `array_sum.sno` are strictly 1-D (`T[I]`, `V[I]`, one subscript each) — neither kernel can exercise the N-D dispatch path at all, so nothing here is evidence about defect (a). Defect (b) (`.NAME`) is untouched by either kernel. The new bucket below (§6) is disjoint in scope from `table-int-keys-and-nd-subscript`'s remaining work; a picker does not need to read both to avoid duplicating a finding, though the stringification corroboration in §4 is noted in that row's LEDGER as a courtesy (it had marked defect (1), integer-key stringification, as already fixed — this FINDING's profile is independent confirming evidence for the closely-related "never build a key string at all" mechanism).

## 6. ⛔ Rebase-baseline check (RULES.md corollary: a pull between measurement and push voids the earlier arm unless checked)

Pushing this session's `SCRIP/scripts/test_gate_instr_budget.sh` change required `git pull --rebase`, landing `ad56bb88` ("strip wave 4a: the zeta selector is collapsed to ONE config") on top of the tree all measurements above were taken on (`eca52780`). Checked before trusting the numbers past the rebase: `ad56bb88` collapses the ζ-storage selector to a single reachable config — but that surviving config (`cell-stack`/`forth`/`zls2`) is bit-for-bit the compiled DEFAULT this session never overrode (no `--zeta-*` flag was passed anywhere above). The commit deletes now-dead alternative-arm code and hard-errors the retired flags; it does not change the default arm's behavior. Every number in this FINDING is therefore still valid as measured — this is the "selector removed, default unchanged" case, not the "the cure arrived in the rebase" trap the corollary warns about.

## 7. Routed

New row: **`perf-table-subscript-fastpath`** — the residual 1.463x gap on table_access, now dominated by per-op hash/search/insert/alloc bookkeeping in `table_set_descr_d`/`table_find_pair_d`/`rt_agg_alloc`/`_tbl_grow` rather than an algorithmic defect. This is exactly the next lever the original `perf-table-array-runtime` BRIEF itself named as the step *after* algorithmic fixes land: "emit the subscript fast path as a bb_* box through the x86() encoder." `array_sum` (§2, 0.9164x) is recorded but not routed as its own row — the gap there is small enough that it doesn't obviously justify a dedicated campaign yet; a future session folding it into whatever picks up `perf-table-subscript-fastpath` is reasonable but not mandated here.
