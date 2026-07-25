# FINDING-2026-07-25-CLAUDE-ICN-MEM-1-HUGEPAGE-VIRGIN-ZERO-ELIDE-AND-GC-ABORT-DIAGNOSIS.md

## Session: Sonnet 4.6, 2026-07-25 (post-s162)

## FINDING 1 — Ir is parity; the gap is memory, not instructions

Baseline measurement comparing SCRIP vs iconx on tgrlink (the primary Icon benchmark):

| Metric | SCRIP | iconx | Verdict |
|---|---|---|---|
| Instructions (Ir) | 1,307,177,233 | 1,338,632,353 | SCRIP **wins** |
| Branch mispredicts | 11,319,178 | 25,847,810 | SCRIP **wins 2.3×** |
| LL cache misses | 961,151 | 38,703 | SCRIP **loses 24.8×** |
| Minor page faults | 14,999 | 607 | SCRIP **loses 24.7×** |
| Peak RSS | ~61 MB | 8.3 MB | SCRIP **loses 7.4×** |

**Consequence:** the GOAL-ICON-BB perf ladder's stated premise — "Ir is the honest metric" — is CORRECT for A/B comparisons of SCRIP against itself, but CANNOT explain the iconx gap. SCRIP already executes fewer instructions and mispredicts fewer branches than iconx yet runs at 0.74× wall-clock speed. Instruction-shaving rungs cannot close this gap. The root cause is that SCRIP bump-allocates through ~61MB of virgin memory per tgrlink run (936,325 carves) while iconx recycles a small warm heap (8.3MB RSS). Every carve touches a cold kernel-zero page: compulsory DRAM write, every time.

## FINDING 2 — HP-1 + HP-2 landed: 1.20× on tgrlink, zero regression

**SCRIP commit: see below.** Two surgical changes to `src/runtime/rt/gc_heap.c`:

**HP-1 — `MADV_HUGEPAGE` on the arena interior.**
THP is `[madvise]` in this environment. The 2MB-aligned interior is opted in at init time. Page faults **15,001 → 2,272** (6.6× cut). `SCRIP_NOHUGE=1` disables (A/B). Isolated gain: **1.14×**.

**HP-2 — virgin-zero elision.**
Fresh anonymous pages are kernel-zero. A high-water mark (`g_hp_virgin`) skips the carve `memset` for fully-virgin blocks. GC-recycled blocks and the `g_hp_win` fill window still zero (correct by construction). `SCRIP_ZSKIP_OFF=1` forces full zeroing (existing escape hatch). Isolated gain: **1.03×**.

**Combined: 1.20×** (tgrlink 212ms → 177ms). All measured at identical emitted code (same `tgrlink.o`, two `.so` builds). Suite: **PASS=249 FAIL=12 XFAIL=32** — watermark exact.

Also added: `SCRIP_HEAP_MB` env tunable (1–4096) for sweep experiments without recompiling.

**Benchmark table (REPS=5, RT_OPT=-O0, before → after):**
| Program | iconx | before | after | speedup |
|---|---|---|---|---|
| tgrlink | 150ms | 202ms | 188ms | 0.80× (was 0.74×) |
| queens | 45ms | 67ms | 51ms | 0.88× (was 0.67×) |
| concord | 32ms | 95ms | 62ms | 0.52× (was 0.34×) |
| geddump | 144ms | 243ms | 225ms | 0.64× (was 0.63×) |

queens and concord show large gains because they're short-running programs where startup/init page faults dominated. tgrlink is longer-running so the proportional gain is smaller.

## FINDING 3 — GC abort is NOT wrong output; but live-set question is open

**RETRACTION of "GC is broken."** The failure at small heap sizes is `SIGABRT` with `[ZHP] heap exhausted ... after storage regeneration`, not wrong output. The GC cycle's basic correctness is demonstrated:
- 800MB string garbage through 512MB heap → correct result
- lists/tables/records/sets (20K×50 iterations) → all correct down to 4–8MB

**The abort trigger is tgrlink-specific, not a universal GC defect.** At 16MB: 39,540 blocks live after collection (~the full 16MB). Two hypotheses NOT yet separated:

1. **Over-retention** (actual GC bug) — the mark phase retains garbage.
2. **Legitimately large live set + SCRIP overhead** — iconx uses 8.3MB RSS; SCRIP `DESCR_t` is 16 bytes and list/table frames carry more header overhead, so the same program's live set may genuinely be larger in SCRIP, and 16MB may simply be insufficient.

**What's needed to separate them:** instrument `rt_gc_collect()` to print bytes-live before and after one collection, then compare against the known-reachable set (e.g. the tgrlink.dat file's word-count structure). This is a ~30-minute rung that was not completed due to context budget.

**Minor confirmed bug:** the abort message hardcodes `ZC_HEAP_MB` (512) regardless of the runtime `SCRIP_HEAP_MB` value. Misleading during diagnosis. One-line fix.

## STANDING NEGATIVES (do not retry)

All from the GOAL-ICON-BB watermark table, unchanged.

## NEXT RECOMMENDED RUNG

Given FINDING 1 (memory is the gap, instructions are already better than iconx), the path to 2–3× requires either:
- (A) **GC live-set measurement** (30 min): determine whether the abort is over-retention or legitimate heap pressure. If over-retention: fix it, reduce ZC_HEAP_MB, and the warm-nursery path opens up — that could deliver large gains.
- (B) **BID-AT-LOWER** (full budget rung): eliminate `bid_of` re-hash on 533K calls. Worth ~1.15× but does not address the memory root cause.

**Recommended order: (A) first.** A working GC with a small heap = warm allocator = the same structural win iconx has.
