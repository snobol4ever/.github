# FINDING 2026-09-02 seat01 — a tight Raku loop exhausts SCRIP's 1024 MB workspace island around N≈50000

**Row:** `bench-grids-rebase-to-two-number-basis` (building Raku angles 1+2, mirroring Prolog's triangulator)
**Trees:** SCRIP `c9e9473f` (pristine `-O0`) · corpus `e7bbc6755` · .github `fe5dec2f`
**Class:** runtime/memory (RTCC lane, GOAL-RTCC.md) — not this row's lane, filed rather than fixed.

## Summary

Building angle-1/angle-2 instruments for Raku (test_bench_raku_timed.sh, bench_raku_fixed_iter.sh) requires
looping a self-timed kernel's own WORK bracket N times in one process (`for 1..N { ...original WORK... }`,
via the new `lib_raku_bench_wrap.sh`). Calibrating `string-escape.raku` (the cheapest of the 4 currently
self-timed Raku kernels — a `"\n" x 1000` build plus one `.trans()` call) at large N **aborts both m3 and
m4**, same signature either mode:

```
[WSI] workspace island exhausted (1024 MB, 1296522 blocks) — raise ZC_WSI_MB
```

## Repro

Same wrapped source, only N differs — confirmed on a pristine `-O0` tree, both modes:

| N | m3 | m4 |
|---|---|---|
| 32768 | rc=0, work_us=2183788 | (not separately re-timed, same wrap) |
| 49152 | rc=0, work_us=4886548 | — |
| 65536 | **rc=134 (SIGABRT)** | **rc=134 (SIGABRT)** |

So the threshold sits between 49152 and 65536 iterations of `my $d = "\n" x 1000; my $s = $d.trans(...)`
inside one process. `ZC_WSI_MB` is `src/ir/zeta_choices.h:8` — **a plain `#define ZC_WSI_MB 1024`, a
compile-time constant, not an environment variable** despite the abort message's "raise ZC_WSI_MB" phrasing,
which reads like a runtime knob and is not one. The abort site is `src/runtime/rt/gc_heap.c:235` and `:270`
(two `rt_ws_alloc` call sites hit the same `(g_wsi_wss - g_wsi_ws) < total` guard).

## Not root-caused — two live hypotheses, not distinguished here

1. **Missing/insufficient GC reclaim inside a tight loop.** Each of my wrapper's N iterations freshly
   `my`-declares `$d`/`$s`; the previous iteration's strings are unreachable the instant the next one starts
   and should be GC-eligible. ~1.3M blocks for a workload topping out around 2x the surviving-N string pairs
   suggests either the collector isn't running often enough inside a loop this tight, or blocks aren't being
   returned to `g_wsi_ws`/`g_wsi_wss` after a collection.
2. **The workload is legitimately larger than it looks.** `.trans()` on a 1000-char string with a 7-pair
   translation table could allocate more intermediate structure per call than the input/output size suggests
   (a naive per-character mechanism, temporary Str buffers, etc.) — 1.3M blocks / ~50K iterations ≈ 26
   blocks/iteration, plausible for either explanation without instrumentation this row didn't add.

Not distinguished because it needs `gc_heap.c` instrumentation or a debugger session — out of scope for a
benchmark-harness row per this repo's own lane discipline (RULES.md; CLAUDE.md § hard rules digest: no
scope creep into another lane's defect from an incidental discovery).

## Why this is filed, not fixed here

This row's job is angle-1/angle-2 *instruments*, not runtime memory management. The instruments now simply
avoid the cliff: `NMAX`/`CAL_NMAX` both default to 32768 (comfortably under the observed 49152–65536
threshold), documented at the point of use in `test_bench_raku_timed.sh` and `bench_raku_fixed_iter.sh`.
**This caps how large an N-times-looped Raku benchmark this harness can ever measure** — a real ceiling on
the instrument, not just on this one kernel, and worth the RTCC/runtime lane's attention independent of
benchmarking: any Raku program that allocates temporary strings/objects in a loop of tens of thousands of
iterations will hit the identical abort in ordinary (non-benchmark) use.

## Reproduction recipe for the next seat

```bash
cd SCRIP
. scripts/lib_raku_bench_wrap.sh
raku_bench_wrap ../corpus/benchmarks/raku/string-escape.raku 65536 /tmp/se65536.raku
./scrip --run /tmp/se65536.raku          # rc=134, "[WSI] workspace island exhausted"
```
