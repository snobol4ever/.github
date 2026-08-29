# FINDING 2026-08-29 (seat04) — `rt_gcheap_carve`/`c_rt_gcheap_alloc` slow-path share is ~30% of all allocations by COUNT, not the 0.3–1.3% this row's sampled TIME-share readings implied — plus a correction to this row's own history about what these functions are

**Context:** `perf-match-begin-beta-cure`, GC+alloc thread, continuing directly from the prior FINDING (`FINDING-2026-08-29-seat04-gcheap-carve-alloc-attributable-via-perf-not-callgrind-sampling-unstable-under-fleet-load.md`), which left this exact question open: get a precise `rt_gcheap_carve`/`c_rt_gcheap_alloc`/`gc_collect_ex` number via more trials, a quieter window, or static counting. **No cure attempted, zero source edits.**

Trees at session start: SCRIP pulled 10 commits (`main`, clean fast-forward — includes an unrelated `backends/` → `interpreters/` rename), corpus pulled 117 commits (`main`, clean fast-forward — includes an unrelated Snocone test-fixture reorg; `table_access.sno`/`.ref` unchanged, confirmed by direct diff of mtimes/content before and after). Rebuilt `make` clean (exit 0) against the synced tree. Workload: `table_access.sno` via `bench_wrap.sh --mode=iter --n=15000`, mode-4 standalone binary (`./scrip --compile ... | gcc -no-pie ... -lscrip_rt -o bin`, this row's own established crash-free recipe), regenerated fresh against the synced corpus. Correctness reconfirmed: `check: 250500` (matches this row's established value) across every run in this FINDING.

## Correction to this row's own LEDGER: these are not "hand-written asm" and not "the allocation fast path"

Prior entries in this task file (`## LEDGER`, GC+alloc items) describe `rt_gcheap_carve`/`c_rt_gcheap_alloc` as "the allocation fast path in hand-written asm (`src/runtime/rtx/rtx_alloc.s`)". Reading the actual source: **both are plain C**, defined in `src/runtime/rt/gc_heap.c` (`rt_gcheap_carve` at line 129, `static`; `c_rt_gcheap_alloc` at line 176, extern). The only hand-written asm is `rt_gcheap_alloc` itself (`rtx_alloc.s:62-95`) — and its "armed" fast path (lines 68-92, confirmed via `objdump`: 32 static instructions, 31 of them executed on the taken fast path, the 32nd being the bailout `jmp` at `.Lga_slow`) **fully inlines carve's logic** (title/size/type/flags stores, virgin/top bump, block-count increment) and returns with **zero calls** — it does not invoke `c_rt_gcheap_alloc`/`rt_gcheap_carve` at all when armed and the target address is fresh (`>= virgin`). Those two C functions are reached only via `.Lga_slow: jmp c_rt_gcheap_alloc` — i.e., they are the **fallback/slow path**, taken when: the `rtx_gate_alloc` kill-switch is off, the allocator isn't yet "armed" (`g_alloc_detax`/`g_ah_on` gating), the bump would overflow the arena, or — the dominant case in this workload, below — the target address is **below `virgin`** (recycled/post-compaction memory that still owes a memset).

## The real question this row needed answered: how often does the slow path actually fire?

Two tracing attempts, both timing out, are themselves evidence:

- gdb breakpoint hit-counting (pending breakpoints into `libscrip_rt.so` — a plain `break fn_name` reports "not defined" and declines until `set breakpoint pending on` is set, since these symbols resolve only once the shared runtime library is mapped at `run` time; `commands 1 / silent / continue` per breakpoint to auto-resume through every hit) on all four symbols (`rt_gcheap_alloc`, `c_rt_gcheap_alloc`, `rt_gcheap_carve`, `gc_collect_ex`): **timed out at 300s**, never reached `info breakpoints`.
- Dropping `rt_gcheap_alloc` (called on literally every allocation, ~4.7M times, clearly the dominant trap volume) and tracing only the presumed-rare three: **still timed out at 120s.**
- `perf probe` (uprobes, which would count exactly with far less per-hit overhead than a full gdb ptrace round-trip): **unavailable in this sandbox** — `No permission to read tracefs` on `perf probe -l`/`perf probe -x`. This is a real, specific, environment-level tooling gap distinct from the callgrind/BB-label-size-0 gap this row already routed; worth recording for whoever next needs exact per-symbol call counts under this container's permission model.

A bounded rate probe (`ignore 1 49999` then `run`, so gdb stops exactly at the 50,000th hit instead of running to program exit) measured **50,000 hits of `c_rt_gcheap_alloc` in 19s** (~2,632 hits/s). At that rate a full trace of a call count in the hundreds-of-thousands-to-low-millions range would need many minutes — consistent with, not contradicting, the two timeouts above. **This alone falsifies the premise behind the prior FINDING's 0.3–1.3% figures being "meaningfully smaller" than `gc_collect_ex`/`table_set_descr_d`**: those were *time*-share samples: a function called millions of times can still show a small time-share if each call is cheap (111–295 static instructions, well under a microsecond), which is exactly what call-count share vs. time share means and why they are not interchangeable — this row's own data had only ever measured the latter for these two symbols.

## Exact answer, derived from two EXISTING zero-cost instrumentation paths (no new code, no sampling)

**1. Exact total allocation count for the whole run**, via `SCRIP_ALLOC_HIST=1` (existing env-gated diagnostic, `gc_heap.c:149-173`; forces `g_hp_fr.armed=0` unconditionally per `gc_heap.c:190`, so every allocation — regardless of which path would normally serve it — routes through `c_rt_gcheap_alloc` and gets tallied in `g_ah_tn[]`/`g_ah_tb[]`). This changes *which internal path* serves each allocation, not *how many* allocations the program logic issues, so the total is valid for the normal run too. Output unchanged (`check: 250500`):

```
total_n=4731308   total_bytes=652589040
```

**2. Exact pre/post-GC block and byte counts**, via `SCRIP_ZETA_TELEM=1` (existing diagnostic, already used by this row in an earlier pass) on a normal (AH-off) run of the identical binary/workload:

```
[ZGC] regeneration #1 (LG): blocks 3316519->197 (pinned 0, fill 0) bytes 536870896->27104 reclaimed 536843792 win=0 slots=204 interior=0
```

**3. The derivation.** `virgin` tracks the highest address any carve has ever reached (`gc_heap.c:136-137`); at the moment of collection this is (to within the pinned/fill terms, both 0 here) the pre-collection `top`, i.e. `arena_start + 536,870,896`. After compaction, `top` resets to `arena_start + 27,104` (the surviving live bytes). So the gap that must be closed by fresh allocation before any address is `>= virgin` again is exactly `reclaimed = 536,843,792` bytes. Bytes allocated **after** the collection are `total_bytes − pre_GC_bytes = 652,589,040 − 536,870,896 = 115,718,144` — **far short of the 536,843,792-byte gap**. So `top` never catches back up to `virgin` for the rest of the run: **every single post-GC allocation is "below virgin" and takes the slow path, all the way to program exit.** Therefore:

```
slow-path calls = total_allocations − pre_GC_block_count
                = 4,731,308 − 3,316,519
                = 1,414,789   (≈29.9% of all allocations)
```

(± a small O(1) correction: the very first allocation of the whole run also takes the slow path unconditionally, since `g_alloc_detax` starts at 0 — negligible against 1.4M.) Reading `c_rt_gcheap_alloc`'s three internal call sites to `rt_gcheap_carve` (`gc_heap.c:178,193,197`) against its one non-carving exit (`abort()` on heap exhaustion, `:202-203`, which cannot fire in a passing run): **every successful `c_rt_gcheap_alloc` call invokes `rt_gcheap_carve` exactly once**, so this same 1,414,789 figure applies to both symbols — they rise and fall together, 1:1, on this workload.

This is a **~23–100x correction** over the prior FINDING's sampled 0.3–1.3% (call-count share, not time share — the two are not the same measurement and should not be read as contradicting each other; the earlier percentages likely remain roughly right for the *time* these symbols consume, just not for how *often* they're reached).

## Static instruction body sizes (this row's own β/NV_SET_fn objdump methodology, `-O0 -g`, no sampling)

| symbol | static body length | note |
|---|---:|---|
| `rt_gcheap_alloc` (real asm, every allocation attempt) | 32 insns | 31 executed on the fast/armed/fresh path; the 32nd is the `.Lga_slow` bailout `jmp`, taken only on gate-off/unarmed/overflow/recycled |
| `c_rt_gcheap_alloc` (C, slow path) | 295 insns | **whole-function static body, not a per-call dynamic count** — has 3 internal early-return branches; average executed-per-call is necessarily less than 295, not measured this pass |
| `rt_gcheap_carve` (C, slow path) | 111 insns | same caveat: static body, not confirmed straight-line |

Total program instructions for this exact workload (`perf stat -e instructions:u`, 3 individual invocations — this row's own established contention-robust technique, **not** `-r N` aggregate or sampling): `5,788,568,547` / `5,788,553,703` / `5,788,566,552` — spread ~15K out of 5.79B (~0.00026%), confirms individual invocations stay reliable even under today's visible FLEET-16 load (this container is running all 16 seats' processes concurrently — confirmed directly via `ps aux` showing other seats' live `cc1plus`/`as` invocations during this session).

**For scale only, explicitly NOT a measured dynamic figure:** `1,414,789 × (295+111) ≈ 574M` instructions ≈ **9.9%** of the 5.79B total, if every static instruction in both function bodies executed on every slow-path call (an upper bound, since both functions branch). This lands in the same order of magnitude as ceo's original 18.76% GC+alloc citation (which also includes `gc_collect_ex`'s own cost, not part of this figure) — consistent with a real, sizeable lever, and nowhere near the 0.3-1.3% this row had been carrying forward.

## Disposition

**Established, exact, not sampled:** total allocations (4,731,308), pre/post-GC split (3,316,519 / 1,414,789), `gc_collect_ex` count (1, reconfirmed fresh this pass on the rebuilt tree — matches the earlier pass's figure exactly), static instruction body sizes, total program instructions. **Still open:** a true ptrace-confirmed exact hit count (a long gdb trace, ~9 minutes projected from the measured 2,632 hits/s rate, was launched and may land after this FINDING is pushed — if its number disagrees with the 1,414,789 derived here, that disagreement is itself the next thing to chase, not something to silently reconcile); the *dynamic* (not static-upper-bound) per-call instruction cost inside `c_rt_gcheap_alloc`'s three branches; whether `perf probe` can be enabled for this sandbox at all (worth a environment/ops question, not a code question). **Not started:** any cure — this remains an attribution pass. The GC index/fwd redesign (item 2's other open half) and the DONE-WHEN ruling (item 5) are unchanged by this pass and still need, respectively, design sign-off and a ceo ruling, exactly as the prior `## NEXT` recorded.
