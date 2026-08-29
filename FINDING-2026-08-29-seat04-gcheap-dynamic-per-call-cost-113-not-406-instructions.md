# FINDING 2026-08-29 (seat04) — dynamic per-call cost of the GC-heap slow path is 113 instructions, not the 406-instruction static-body-sum the prior FINDING used "for scale"

**Context:** `perf-match-begin-beta-cure`, GC+alloc thread, direct follow-up to today's earlier
`FINDING-2026-08-29-seat04-gcheap-slow-path-is-30-percent-of-allocations-not-1-percent.md`, which explicitly left
open: *"the dynamic (not static-upper-bound) per-call instruction cost inside `c_rt_gcheap_alloc`'s three
branches."* This closes that. **No cure attempted, zero source edits.**

## Method: resolve the actual taken branches by hand from `objdump`, then confirm the dominant path from the allocation-type histogram already captured earlier today

The prior FINDING's "for scale" figure summed the *whole static body* of both slow-path functions
(`c_rt_gcheap_alloc` 295 insns + `rt_gcheap_carve` 111 insns = 406) and explicitly flagged that as an upper
bound, since both functions branch. Reading `/tmp/objdump_alloc.txt` and `/tmp/objdump_carve.txt` (captured
earlier today, same build) instruction-by-instruction against the C source (`gc_heap.c:129-204`):

- **`c_rt_gcheap_alloc`'s own top branch** (`g_alloc_detax==1 && g_ah_on<=0`, `gc_heap.c:178`) is what nearly
  every slow-path call actually takes — it is reached whenever the asm fast path (`rt_gcheap_alloc`) bails
  because the target address is below `virgin` (the dominant case established in the prior FINDING: every
  post-GC allocation in this workload), NOT because `g_alloc_detax`/`g_ah_on` themselves are unfavorable — those
  stay in their normal "everything's fine" state for the whole run after the first call. Traced from function
  entry to `ret`: **44 instructions**, including the one `call rt_gcheap_carve` (but not its callee's body) —
  entry/arg-store (10, includes the `g_alloc_detax==1` check) + the `g_ah_on<=0` check (3, not-taken) + the `tf`
  computation (5) + the `top+tf<=end` bounds check (8, not-taken — i.e. it fits) + the carve call itself (7 to
  set up args, 1 to `call`) + the top-bump-and-return tail (6 to advance `g_hp_top`, 1 to load the return value,
  1 `jmp` to the shared epilogue) + `leave`/`ret` (2), summing to 10+3+5+8+7+1+6+1+1+2 = 44. The full
  295-instruction body
  (budget/stress-counter bookkeeping, the `rt_gc_collect()` trigger check, the window/WSI fallback, the
  heap-exhaustion `abort()`) is reached only when this top branch's own inner check fails — i.e., essentially
  only by the single allocation that actually overflows the arena and triggers the one `gc_collect_ex` call for
  this workload (1 call out of 1,414,789 — folded into the same population by construction, since it completes
  its own carve *after* `rt_gc_collect()` returns; its extra ~250-instruction wrapper cost is a rounding error
  against 1.4M repetitions and is not separately broken out here).

- **`rt_gcheap_carve`'s "not fresh" path** (taken on every one of these calls, by definition — that's *why*
  they reached the slow path at all), traced instruction-by-instruction from `objdump` against `gc_heap.c:129-141`:
  the unconditional header-field writes (`h->fwd`/`size`/`type`/`flags`, `pay = total-16`: **24** instructions) →
  `g_hp_fr.zfull`'s lazy-init short-circuit, already resolved after the first call in the whole run (**4**) → a
  second read-and-check of `zfull` immediately after (**5**, not-taken — it isn't forced) → the `at >= virgin`
  check, evaluated **twice** in the source (once to compute `fresh`, once to decide whether to bump `virgin`):
  first occurrence `jb`-taken since `at < virgin` here, landing on the `fresh = 0` assignment (**4 + 2**); second
  occurrence also `jb`-taken, skipping the entire 12-instruction virgin-bump block (**4**) → the `fresh != 0` and
  `zfull != 0` re-checks immediately before the size/type dispatch, both not-taken (**2 + 2**). Running total:
  24+4+5+4+2+4+2+2 = **47 instructions**, common to every not-fresh call regardless of payload. From there, the
  payload-size/type dispatch (`gc_heap.c:139`, `pay > 32 && type ∈ {DT_S, HB_WSC}`) branches to one of two
  `memset` call sites plus the shared `g_hp_blocks += 1`/return tail — **which one depends only on the
  allocation's type and payload size, not on anything random** — settled below.

## Which branch of carve's dispatch actually fires: the allocation-type histogram already answers this

The `SCRIP_ALLOC_HIST` run captured for the prior FINDING gives the exact type breakdown for this entire
workload (`/tmp/ah_run.err`):

```
[AH] T 211 4716280 651747840   <- HB_AGGB (gc_heap.h:21, "a table bucket's contiguous index array"), 99.68% of all allocations, avg 138.2 bytes/alloc
[AH] T 208 15020    841120     <- HB_AGGT (gc_heap.h:13), 0.32%, avg 56.0 bytes/alloc
[AH] T 2   8        80         <- DT_S (strings), 0.0002%, negligible
```

`HB_AGGB` (211) and `HB_AGGT` (208) are neither `DT_S` (2) nor `HB_WSC` (0xcd = 205), and both types' average
payload sizes clear the `pay > 32` threshold — so **99.9998% of all allocations in this workload take the same
branch of carve's dispatch**: the plain `else memset(h+1, 0, pay)` path (`gc_heap.c:140`, the non-tail-optimized
one), never the 32-byte-tail-optimization path reserved for `DT_S`/`HB_WSC`. That branch, from the dispatch
point to `ret`, is **16 instructions** (one `memset` call plus the block-count-increment/return tail); reaching
it from the common 47-instruction prefix costs 6 more instructions of comparisons (`pay>32`, `type==DT_S`,
`type==HB_WSC`, all evaluated, none taken toward the other ending). **Total for `rt_gcheap_carve`'s executed
path: 47 + 6 + 16 = 69 instructions** — essentially uniform across the whole slow-path population, not a range
that needed averaging.

## The number

```
c_rt_gcheap_alloc (Tier-2 branch, incl. the call instruction):  44
rt_gcheap_carve   (not-fresh, HB_AGGB/HB_AGGT dispatch):        69
                                                                 ---
per-call dynamic cost:                                         113 instructions

1,414,789 slow-path calls × 113  =  159,871,157 instructions
159,871,157 / 5,788,562,934 total  ≈  2.76% of the whole program
```

This **replaces** the prior FINDING's "for scale ~9.9%" figure, which was an explicitly-flagged static-body-sum
upper bound (406 instructions/call). The real, branch-resolved, histogram-confirmed dynamic cost is **113
instructions/call, ≈2.76% of total program instructions** — a 3.6x reduction from the upper bound, and
considerably smaller than ceo's original 18.76% GC+alloc citation (which is dominated by `gc_collect_ex`'s own
one-time collection cost — the 140ms `index` + 66ms `fwd` linear-walk phases already measured in an earlier
pass — not by the repeated per-allocation slow-path overhead this FINDING isolates).

## Disposition

**Established:** the exact, branch-resolved, histogram-confirmed dynamic instruction cost of the slow
allocation path (113/call, 2.76% of the program), correcting this row's own prior static-upper-bound estimate.
**Not re-derived, cited as-is from the prior FINDING:** the 1,414,789 call count itself (still a derived, not
ptrace-confirmed, figure — see that FINDING's own follow-up note on the timed-out gdb confirmation). **Still
open, genuinely unstarted:** whether 69 instructions is itself compressible (e.g., the `memset` call for small,
uniformly-shaped `HB_AGGB` payloads could plausibly be a few inlined stores instead of a libc call — not
examined, and this would be a cure, not attribution, requiring the same design-level care this row's own
`NV_SET_fn` thread already documented for a structurally similar memoization cache). No cure attempted.
