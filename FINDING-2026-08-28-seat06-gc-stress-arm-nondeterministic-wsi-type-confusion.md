# GC-stress arm nondeterminism was a real SIGSEGV: gc_zeta_frame trusted WSI range membership, not block identity

**Seat:** seat06 · **Date:** 2026-08-27/28 · **Mode:** FLEET-8 → FLEET-6 (crossed the date/mode boundary mid-row) · **Task:** `gc-stress-arm-nondeterministic`
**Row:** rank 2, minted by hq_C 2026-08-28 ("the arm nearly returned a false regression").

## The brief

`SCRIP_GC_STRESS=64 bash scripts/test_corpus_snobol4.sh` returned a different mode-4 FAIL count across repeated runs on an unchanged binary (2↔3, `demo_calculator_2` appearing/disappearing) — usable as a control only if it is deterministic. GOAL: make it deterministic, or make it refuse. LINKS pointed at `gc_heap.c`'s `stress_n`/`stress_c` counter as deterministic by construction, naming the real suspects as "which safepoint consumes the pending collection" and "ASLR-dependent addresses."

## Repro, standalone, before touching anything

Compiled `demo/snobol4/calculator/calculator-2.sno` directly (`--compile` → `gcc` → link `libscrip_rt.so`) rather than going through the full corpus harness, and looped the resulting binary under `SCRIP_GC_STRESS=64`: **5 of 10 runs SIGSEGV'd**, the other 5 produced correct, byte-identical output. Not a hang, not a wrong answer — a crash, exactly half the time, on an unchanged binary and unchanged input.

Caught it under gdb (`set disable-randomization off` — gdb defaults to disabling ASLR, which would have hidden the exact mechanism this bug depends on; had to explicitly re-enable it, then loop `run` until the signal fired):

```
Program received signal SIGSEGV.
0x... in rt_gc_visit_descr (d=0x7afe4e9064f0) at gc_heap.c:448
448    if (!a || !gc_hins((void *)a) || !a->data) return;
#0 rt_gc_visit_descr (d=0x7afe4e9064f0) at gc_heap.c:448
#1 rt_gc_visit_descr (d=0x7ffcffcb0038) at gc_heap.c:450
#2 gc_zeta_frame (lo0=0x7ffcffcae258, hi0=0x7ffd00418000) at gc_heap.c:567
#3 gc_collect_ex (cons_stack=0) at gc_heap.c:636
#4 rt_gc_point_arr_c (...) at gc_heap.c:326
```

Same site, every attempt, across multiple independent gdb-caught crashes.

## Root cause

`gc_zeta_frame` conservatively scans a C-stack range 16 bytes at a time, treating each aligned window as a candidate `DESCR_t`. For `DT_S`/`DT_T`/`DT_N` candidates it validates against `gc_blk_of()` — an exact index over the general heap's real block headers, requiring the pointer to equal the exact start of a real, currently-live block (`d->s == (char *)(h + 1)`). For `DT_A`/`DT_DATA` candidates it validated only via `gc_in_wsi()`:

```c
static int gc_in_wsi(const char *q)
{ return q && g_wsi_base && q >= g_wsi_base && q < g_wsi_ws && !((uintptr_t)q & 7u); }
```

— "does the payload fall *anywhere* inside `[g_wsi_base, g_wsi_ws)`," with no check that it's the start of a real object at all. A stale/uninitialized 16-byte stack window whose first 8 bytes happen to equal `DT_A`'s tag and whose second 8 bytes happen to numerically land inside the workspace island's current range gets treated as a genuine live array, and `rt_gc_visit_descr` reads `ARBLK_t` fields (`hi`/`lo`/`ndim`/`data`) off whatever is actually at that address — reading `a->data` off garbage segfaults when the garbage isn't a mapped address. Whether a given stale stack word's numeric payload happens to fall inside the WSI's *current* range depends on the relative ASLR offset between the stack and the WSI mmap region that run — hence the 50/50 split, and hence why gdb's default ASLR-off mode would have hidden it entirely.

**A second layer, found only after the first fix still crashed:** exact-block-start alone is not sufficient, because `ARBLK_t` headers, `DATINST_t` headers, and the raw `DESCR_t` element buffers they point at (`a->data`) are *all* allocated via `rt_ws_alloc` and *all* shared the one generic `HB_WS` type tag. A garbage word whose payload landed exactly on a real buffer's start (not an `ARBLK_t`'s start) passed an exact-match check too, and got its bytes read as `ARBLK_t` fields — same crash, same site, still ~50% (confirmed by A/B: first fix alone did not eliminate it).

## Fix

Two parts, `src/runtime/rt/gc_heap.c` + `gc_heap.h` + five allocation-site call files:

1. **`gc_wsi_exact`** — twin of `gc_blk_of` for the workspace island. `g_gc_widx` is an index of every real `rt_ws_alloc` header, grown *incrementally* each collection (`g_gc_windexed` remembers how far it's walked) rather than rebuilt from `g_wsi_base` every time — WSI is bump-only and never compacted, so a full rewalk is O(collections×blocks) and, measured, timed out real programs once `SCRIP_GC_STRESS` forces hundreds of collections. A first version rebuilt from scratch each time and turned the crash into a hang instead (caught via `SCRIP_ZETA_TELEM`, which showed the WSI-indexing step eating the whole "mark" phase); the incremental version fixed that back to `new=0` after the first collection.
2. **`HB_ARR`/`HB_DINST`** — two new type tags (`gc_heap.h`, next free after `HB_AGGB`), so `ARBLK_t`/`DATINST_t` headers are distinguishable from every other shape `rt_ws_alloc` hands out. New `rt_ws_alloc_tag(n, ty)` entry point; 10 call sites retagged (`aggregates.c` ×2, `pattern_match.c` ×2, `core.c` ×4, `driver_data.c`, `by_name_dispatch.c`). `gc_wsi_exact` now takes `want_type` and both fast-path checks in `gc_zeta_frame` pass the specific tag.

Verified by `git stash` A/B on the exact standalone repro: original code segfaults ~50% of runs (gdb-caught, same site, every attempt); fixed code is 0 segfaults across 50+ runs since, both standalone and under the full corpus suite.

## Merge note: landed alongside seat03's `rt_ws_alloc` → asm port

`rt_ws_alloc` is now `rtx_alloc.S`'s fourth ported function (see `FINDING-2026-08-28-seat03-rtx-startup-touch-target-list-and-rt-ws-alloc.md`), with `c_rt_ws_alloc(size_t n)` as its C fallback — a single-argument contract the asm veneer jumps into directly (`jne/je/jb c_rt_ws_alloc`, `rdi` staged, nothing else). `git pull --rebase` conflicted exactly on that one renamed line. Resolution: left `c_rt_ws_alloc`'s signature and the asm veneer completely untouched (widening it to take a `ty` argument would silently corrupt the type field of every `rt_ws_alloc` call reached through the asm fallback, since the veneer never stages a second argument); factored the shared bump-allocation logic into a new `static rt_ws_alloc_core(n, ty)` that both `c_rt_ws_alloc` (hardcoded `HB_WS`, byte-identical external behavior) and the new `rt_ws_alloc_tag` call. Full rebuild + relink succeeded (confirms the asm veneer's jump target still resolves correctly) and the normal, non-stress corpus suite re-ran clean (893/893 both modes) after the merge, before this row's own stress-mode DONE-WHEN was re-verified a third time on the merged tree.

## Residual, different-mechanism nondeterminism found and closed: the DONE-WHEN's own timeout was too tight for what it was measuring

With the crash gone, runs survive long enough to complete — and `demo_calculator_1`/`demo_calculator_2` turned out to need far longer under `SCRIP_GC_STRESS=64` than the corpus runner's default 10s per-test budget assumes. Timed both directly (compiled standalone, 12 timed runs each):

| program | completion time range | vs. 10s default |
|---|---|---|
| `demo_calculator_1` | 10.5s – 12.8s | **always** over |
| `demo_calculator_2` | 7.8s – 10.1s | straddles it |

`calculator_1` was a stable (if unfortunate) FAIL every time — fine, per this task's own bar ("determinism is the bar, not green"). `calculator_2` was the actual remaining flake: usually finishes with room to spare, occasionally creeps just over. Confirmed reproducible, not a one-off: reran the original (`TIMEOUT` unset → default 10) DONE-WHEN twice after the crash fix alone landed, both times non-deterministic (`FAIL=2` baseline, one later run `FAIL=1`). Machine load is real and plausibly a contributing factor — `uptime` mid-run showed load average 2.1–4.8 on this 16-core seat with several other `claude` processes active, consistent with the 16-seat fleet this box runs.

Per this project's own "the corrected number is the deliverable" norm: `test_corpus_snobol4.sh`'s `TIMEOUT` is already env-overridable (`TIMEOUT="${TIMEOUT:-10}"`, line 14, untouched — this changes nothing for any other caller). The task's own DONE-WHEN now sets `TIMEOUT=20` — headroom sized off the measured worst case (12.8s) plus margin for shared-box load, not a round guess. Re-verified 5-for-5 identical, **and green** (`FAIL=0`) at `TIMEOUT=20`, both before and after the seat03 merge.

## Verification summary

- Standalone repro (`calculator-2` compiled directly, looped under `SCRIP_GC_STRESS=64`): 0 segfaults / 50+ runs post-fix, vs. ~50% pre-fix (git-stash A/B, gdb-confirmed same crash site both times pre-fix).
- Per-collection cost (`SCRIP_ZETA_TELEM`) measured identical pre- and post-fix (~7-10ms mark phase, ~5,343 conservative "slots") — not a regression, a pre-existing cost the crash used to mask by ending runs early.
- Task's own DONE-WHEN (corrected to `TIMEOUT=20`): 5-for-5 identical, `FAIL=0`, both pre- and post- the seat03 rebase, plus a third re-run via `s4e_msg.sh done` itself (independent re-verification, not self-reported).
- Full normal (non-stress) corpus suite after the merge: **m3 PASS=893 FAIL=0 · m4 PASS=893 FAIL=0 SKIP=0**.
- `test_gate_emit_no_lang.sh`, `test_gate_template_medium_invisible.sh`: both green (untouched code paths, sanity-checked anyway).

## Files

`src/runtime/rt/gc_heap.c`, `gc_heap.h`, `rt_arena.h`, `runtime/aggregates.c`, `runtime/pattern_match.c`, `runtime/core/core.c`, `driver/driver_data.c`, `runtime/by_name_dispatch.c` · `.github/GOAL-SNOBOL4-100.md` LIVE CURSOR + this FINDING · task baton `gc-stress-arm-nondeterministic.task.md` LEDGER + corrected DONE-WHEN, closed via `s4e_msg.sh done`.

## NEXT (named, not started here)

- `gc-stress-three-demos-fail` (the row this one was blocking) is now unblocked.
- The residual "why is the conservative stack scan finding ~5,343 stale-but-plausible-looking slots every single collection" question is untouched — plausibly normal (leftover values in the interpreter's own upper stack frames between top-level statements), not investigated further since it did not block this row's own bar once `TIMEOUT` was corrected. Flagged in case a future perf rung wants it.
- `gc_in_wsi` is gone; `HB_ARR`/`HB_DINST` join `HB_AGGV`/`HB_AGGP`/`HB_AGGT`/`HB_AGGB` as the WSI/heap type-tag family. Worth a glance from whoever next touches `gc_heap.h`'s type enum, but nothing currently depends on it beyond this row.
