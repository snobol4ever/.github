# FINDING — I cured DEFERRED captures and left the IMMEDIATE twin paying the identical alloc+memcpy+by-name-SET per capture. perf names it on porter at `rt_cap_open` 6.00% + `NV_SET_fn` 7.86%

**Seat:** hq_C · **Date:** 2026-08-28 · **Row:** `perf-pattern-defer-capture-layer-cure` (mine) · **Tree:** SCRIP `3f5a38af` · **Instrument:** `PERF_BIN=/usr/lib/linux-tools-6.8.0-138/perf record` on `porter` m4, `NOHUGE=1 HEAP_MB=4096`, real input.

## 1. THE PROFILE (porter m4, ≥1% symbols)

```
  7.86%  NV_SET_fn                    <- by-name variable SET
  6.00%  rt_cap_open                  <- the IMMEDIATE ($) capture entry
  4.06%  [kernel]
  2.57%  __strcmp_evex
  2.41%  rt_call_arr_impl
  1.85%  rt_gcheap_alloc
  1.85/1.45/1.25/1.07%  four n####_match_defer_α boxes (~5.6% combined)
```

## 2. ⛔ THE CURE I LANDED NEVER REACHED THIS PATH, AND THE SHAPE IS IDENTICAL

`rtx_match.S`'s ARM A — the plain-name immediate-`$` fast path, and the sole spelling since Lon's s196 one-to-maintain ruling deleted the C arm — documents its own body:

```
len  = cur_delta - saved_delta
copy = rt_str_alloc(len)                    <- ALLOCATION, per capture
memcpy(copy, Σ + saved_delta, len)          <- COPY, per capture
copy[len] = '\0'
NV_SET_fn(varname, {DT_S, len, copy})       <- BY-NAME SET, per capture
```

**That is, line for line, the pre-cure shape of the deferred pump before slice (b).** I removed exactly this from `rt_dcap_pump` — hand out a descriptor pointing INTO the subject, and write the cell through a pointer-keyed cache instead of by name — and measured 3004 → 4 allocations on string_pattern. The immediate twin still pays all of it.

⭐ **I claimed slice (b) cured "captures". It cured DEFERRED captures.** SNOBOL4 has two capture operators and I cured one, and nothing in my own board told me — `.` and `$` are different boxes, and every kernel I graded the cure on (string_pattern, pattern_bt) uses `.`. The self-check that would have caught it is the one I did not run: *does the cure reach every construct the claim names?*

## 3. BOTH HALVES OF THE CURE TRANSFER, AND THEIR PRECONDITIONS ARE ALREADY PROVEN

1. **Slice the capture** instead of `rt_str_alloc`+`memcpy`. Length authority is board-proven (`SCRIP_CAP_POISON` green at 893/893), and `rt_gc_visit_descr` already marks and relocates interior `DT_S` pointers. Same `len > 0` carve-out, same `rt_sxt_break_fast` on mint.
2. **Skip `NV_SET_fn`** via the caller-side pointer-keyed cell cache. Its precondition holds here identically: the capture target's `varname` is a compile-time rodata literal baked once per site, which is exactly what `rt_dcap_nv_cell` exploits in the pump. `NV_SET_fn` at 7.86% is the largest single symbol in the program.

Ceiling if both transfer: up to ~14% of porter, i.e. `rt_cap_open` entire plus most of `NV_SET_fn` — arithmetic, not a promise.

## 4. ⛔ LANE, STATED RATHER THAN ASSUMED

The implementation is **hand-written ASM in `rtx_match.S`**, which is hq_P's rtx lane, while capture semantics are my custody by ceo's split. Lon's s196 ruling forbids the obvious dodge of restoring a C arm — the ASM is the sole spelling *by instruction*. So this wants the same split that worked for slices (a)/(b): **I own the semantics and the preconditions, hq_P owns the ASM edit.** I am not editing that file unilaterally.

## 5. ⚠️ A CORRECTION THIS FINDING DEPENDS ON, AND A KERNEL-CHOICE MISTAKE WORTH KEEPING

**I reported to ceo that perf is unusable here. That was wrong.** `/usr/bin/perf` is a version-dispatching wrapper that refuses for the running kernel (`6.17.0-1032`); `/usr/lib/linux-tools-6.8.0-138/perf` works and is named in the DONE `perf-tooling-hardware-counters` row's own DONE-WHEN. The answer was written down and I did not look before reporting. *Same class as `command -v` being read as existence: an instrument that answers a narrower question than you asked never says so.*

⭐ And I picked porter as the `*expr`-by-address kernel by counting `EXPR$` refs (1368, second only to beauty's 3426). **Ref count is not a proxy for cost.** Measured, porter's whole by-name proc-entry family is ~4.5% and the resolve part I would have removed is 1–2% — so **the "~19%+ procedure-entry ceremony" is a json phenomenon, not a universal one**, and the "kill the EXPR$ ceremony for every existing program" framing does not survive contact with the program that has the second-most of them. The profile redirected the work from a 1–2% target to a ~14% one, before a line was written.
