# FINDING 2026-08-28 hq_P — sizing the ARM-A `NV_SET_fn` skip: the lookup is HALF of `NV_SET_fn`, the skip is still worth ~11% of porter, and slice (1) is a separate additive ~14.2%

## Why this exists

`perf-pattern-defer-capture-layer-cure`'s brief is *"delete the `NV_SET_fn` call from `rt_cap_open` ARM A"*, sized at
~17% of `porter`. The row's own `## NEXT` opens with **"READ THIS BEFORE CUTTING THE ARM-A ASM — the briefed slice,
executed as written, would have shipped a wrong answer."** I followed that instruction to its conclusion, found a
second and different reason to pause, then **measured instead of arguing** — and the measurement corrected me.

## The source-level observation (right, and quantitatively useless on its own)

The skip is admitted by `NV_CELL_IF_FASTSET_fn`, which hq_C factored out of `NV_SET_fn` at s281 precisely so the
admission test cannot drift. It cannot. **But `NV_CELL_IF_FASTSET_fn` (`core.c:2402`) calls `_var_find_cached(name)`
— the same lookup `NV_SET_fn` performs** — and that lookup's *hit* path is hash + two compares + `strcmp`
(`core.c:2340`). So the skip replaces one PLT call with another that re-pays the expensive part.

I concluded from that the skip was "small", and proposed reordering slice (1) ahead of it. **That conclusion was
wrong.**

## The measurement

callgrind **Ir**, `-O0`, mode-4, SCRIP `92fdd601`, witness `corpus/benchmarks/snobol4/demo/porter.sno` over the first
2,000 lines of `porter.dat`. Total **77,012,736 Ir**; percentages are of that total. The input is truncated because
the quantity sought is a **ratio**, which is scale-invariant on a steady-state loop.

| symbol | inclusive Ir | % of porter | per call |
|---|---|---|---|
| `rt_cap_open` | 26,632,034 | 34.58% | — |
| `NV_SET_fn` | 21,046,578 | 27.33% | 179 Ir |
| ├─ `NV_CELL_IF_FASTSET_fn` — the lookup, **not** removable by the skip | 10,942,171 | 14.21% | 93 Ir |
| │   └─ `__strcmp_avx2` (self) | 3,474,156 | 4.51% | — |
| └─ `NV_SET_fn`'s own body — **what the skip removes** | ~10,104,407 | ~13.1% | 86 Ir |

`NV_CELL_IF_FASTSET_fn` is entered **117,474** times, from `NV_SET_fn`'s own fast-path line, so that is `NV_SET_fn`'s
call count too. **179 Ir per capture store: 93 lookup, 86 `NV_SET_fn` body** — the body being mostly `-O0` call
overhead, a 16-byte `DESCR_t` passed *and* returned by value on every store.

## What it means

- **The skip's ceiling is ~13.1%, netting ~11%** after the guards ARM A must retain (~15 Ir/call). That is not a
  follow-on. **The s279 order — skip first — stands, and my proposal to reverse it is withdrawn.**
- **Slice (1) is a separate, ADDITIVE ~14.2%**, because compile-time cell binding deletes the lookup the skip must
  keep paying. The two are not alternatives: **~25% of porter combined.**
- **The slow path is rare** — `_io_chan_find_by_var` 1.21%, `_io_chan_setup` 0.05% — so the cell fast path hits on
  nearly every store. That is what makes the skip worth wanting, and it also sizes the one regression mode: **on a
  fast-path MISS the skip pays the lookup twice**, once in ARM A and again inside the `NV_SET_fn` fallback. A rounding
  error at this hit rate; a real regression if the hit rate ever drops, so the fallback must be measured, not assumed.

## Four preconditions, unchanged by the sizing

`NV_CELL_IF_FASTSET_fn` is `NV_SET_fn`'s **admission test**, not its **preamble**. `NV_SET_fn` does work *before*
consulting it, and a caller that skips `NV_SET_fn` skips that work too:

1. `if (val.v == DT_S) rt_sxt_break_fast(val.s)` (`core.c:2410`) — ARM A always passes `DT_S`. **Inline it** (two
   instructions). Fresh `rt_str_alloc` memory is very unlikely to be `g_sxt_owner` (set only for a top-of-heap TTL
   block, `gc_heap.c:58`) — but "very unlikely" is the confidence level this row has already been burned by twice.
2. `g_protected_pat_vars_armed && is_protected_pat_name(name)` (`core.c:2411`) → `core_runtime_error(42)`. Not in the
   predicate; the fast path must fall back when armed.
3. **The three-way observer check after the cell write** (`core.c:2416`): `g_comm_dbg || trace_set_n || monitor_fd>=0`
   → `comm_var()`. Skip it and **TRACE silently stops reporting** — a wrong answer no board would catch. This is
   exactly the guard seat05 sized on `perf-nv-set-fn-o0-overhead`; Lon's pending `g_comm_any_active` grant would make
   it one load instead of three, in this hot path too.
4. The latched `SCRIP_EXPR_STORE_DBG` block (`core.c:2408`) — debug-only, but a behavioural difference; fallback set.

## A defect in the row's own DONE-WHEN

It selects the **newest** dated attribution TSV by mtime and requires *that* file to carry both witness kernels. It
currently fails with `new TSV missing the two witness kernels` — **not because the cure is unmet, but because an
unrelated dated TSV is newest.** Any seat appending an attribution TSV breaks it, and it will re-break after a correct
cure. Same class as the `tail -1` DONE-WHEN defect repaired at s278: **anchored on RECENCY rather than IDENTITY.**

**This is also why no dated TSV was appended for the measurement above** — doing so would have broken the criterion by
exactly the mechanism being reported. The data lives here and in the baton instead.

## Method note

The source read was right and told me nothing useful about size; the callgrind run answered in one shot. That is the
fourth time in this session that a measurement beat my reasoning, and the pattern is worth naming: **a correct
mechanism gives no scale.** The mechanism said "the lookup survives"; only the instrument said whether what dies with
it is 2% or 13%.
