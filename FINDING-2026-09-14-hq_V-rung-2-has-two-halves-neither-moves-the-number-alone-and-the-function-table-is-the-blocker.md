# FINDING — GC-5 RUNG 2 HAS TWO HALVES, NEITHER MOVES THE NUMBER ALONE, AND THE BLOCKER IS AN UNROOTED FUNCTION TABLE

**hq_V, 2026-09-14, SCRIP `c93fe08c6`, MODE NONET.** Measured on the rank-0 row
`icon-gc-rung-2-every-live-aggregate-slides-and-hb-pinned-is-deleted`. Every number below is from a build
I made and ran in this sitting; the two-arm comparisons name the `libscrip_rt.so` sha256 of each arm,
because an A/B that cannot prove its arms were two different libraries compared a build with itself
(`FINDING-2026-09-13-hq_V-a-runpath-to-an-absolute-out-directory...`).

## 1. THE 2×2, AND IT IS MULTIPLICATIVE RATHER THAN ADDITIVE

The rung's GOAL says the 4M-list churn "holds 604 MB instead of settling at the 128 MB pacing line", and
attributes it to fragmentation because live blocks do not move. I built all four cells. Witness is the
rung's own: `every i := 1 to 4000000 do L := [i, i+1, i+2]`, answer `done 3` in every cell.

| | **unpaced** (origin) | **paced** (one added line) |
|---|---|---|
| **pinned** (origin) | 604 MB, 1 collection | 555 MB, 25 collections |
| **sliding** (rung 2's cure) | 604 MB, 1 collection | **161 MB**, 5 collections |

- origin, pinned+unpaced: `so=6c3a2504a7a1a537`, RSS 604376 KB
- sliding+unpaced: `so=94334ff8f461dae8`, RSS 604364 KB
- pinned+paced: `so=4943f4d63e548dfa`, RSS 555228 KB
- sliding+paced: `so=4cbf74a4ed2919fa`, RSS 161008 KB (and 31196 KB at `SCRIP_GC_LINE_MB=16`)

⭐ **NEITHER HALF MOVES THE NUMBER ALONE.** Sliding alone changes RSS by 12 KB in 604 MB — 0.002%.
Pacing alone reclaims **zero bytes on every one of its 25 collections** (telemetry: `reclaimed 0
win=536830080` each time) because pinned blocks cannot be compacted, so it re-opens the same window 25
times. Together they give 604 → 161 MB. **This is why the rung has resisted several sittings:** a seat
implementing the half the GOAL names measures no improvement and reasonably concludes the cure is wrong.

## 2. THE STATED MECHANISM IS WRONG: IT IS NOT FRAGMENTATION

With sliding on, the collector's own telemetry on the first regeneration reads
`blocks 8388596->55 (pinned 0, fill 0) bytes 536870880->13024 reclaimed 536857856`. It compacts 536 MB
into 13 KB. Nothing is fragmented. The 604 MB is **resident pages already touched before the first
collection ever runs**, and compaction does not return pages to the OS. The heap reaches 536 MB before
collecting because **`rt_pinned_alloc_core` (`gc_heap.c:244`) collects only at heap exhaustion and never
consults the pacing line** — the paced checks live at `gc_heap.c:194` and `:208`, inside `rt_gcheap_alloc`,
which the pinned allocator does not go through. Proof it is the allocator and not the setting: on origin
the churn takes exactly **one** collection at `SCRIP_GC_LINE_MB` = default, 128, 64 **and 16** — the
configured line makes no difference at all, because it is never read on that path.

⭐ **SO THE TWO HALVES ARE ONE CHANGE.** Deleting `rt_pinned_alloc`, which the rung already requires, is
not only about movability: it is what puts those ~410 allocation sites onto the paced path. The rung's
two clauses are the same edit seen from two sides, and the GOAL states only one of them.

## 3. THE BLOCKER, ROOT-CAUSED: THE FUNCTION TABLE HAS NO ROOT AND PINNING IS ALL THAT HIDES IT

Making the four types slide segfaults a **five-statement SNOBOL4 program**, 20 runs of 20. gdb:

```
#0  __strcmp_evex ()
#1  APPLY_fn (name=0x4536f0 "CHAR", ...) at src/runtime/core/core.c:3785
#2  rt_call_arr_impl (...) at src/runtime/by_name_dispatch.c:5181
```

`core.c:3785` is `strcmp(e->name, name)` over the `_func_buckets` chain. Read from the source, not inferred:

- `_func_buckets` is a **static array of pointers** (`core.c:3554`).
- Its entries are `FNCBLK_t *fe = rt_pinned_alloc(sizeof(FNCBLK_t))` (`core.c:3571`, `:3739`) — **in the
  collected heap**.
- `core_gc_roots` (`core.c:4200`) walks `_var_buckets` and `_udef_types`. **It never walks
  `_func_buckets`.** `rt_gc_ws_roots` (`rt/rt.c:1357`) visits only the name-save stack. No other root scan
  reaches it.

So every FNCBLK block, its `name`, its `next` chain and its `entry_label` are unmarked and unregistered.
**Pinning is the only thing keeping the static bucket array's pointers valid.** Rung 2 deletes pinning,
the blocks move, the spine dangles.

⭐ **THE SENTENCE: A BLOCK THAT SURVIVES ONLY BECAUSE IT CANNOT MOVE HAS NO ROOT — IT HAS AN ALIBI.**
This is the third member of a class this seat has now hit three times in a week: a heap pointer read only
by emitted code (the baked immediate, cured), a heap pointer held in a plain C local (the Prolog atom
row, filed), and now a heap pointer held in a static C array no scan walks. All three are invisible to
every root scan, and all three are harmless *only* while the block is pinned.

## 4. ⛔ THE FOUR GC GATES DO NOT COVER THE CLASS

`test_gate_gc_aggregates_are_collectable_not_immortal`, `..._pacing_bounds_a_churning_program`,
`..._pas_heap_table_is_a_movable_root` and `..._aggregate_interiors_are_marked_not_only_slotted` **all four
pass rc=0 on the sliding build that segfaults the five-statement witness.** The only instrument in the
fleet that reds it is `test_gate_sno_a_by_name_call_survives_collect`, landed earlier this same sitting
for an unrelated reason. A seat could have taken rung 2's slide half, seen four green GC gates, and
shipped it. Sizing the witness set for the collector is no longer a nice-to-have.

## 5. WHAT IS NOT CLAIMED

Nothing was landed: the tree is pristine at `c93fe08c6` and the working experiments are reverted. The
pacing line I added to `rt_pinned_alloc_core` is a **probe to attribute the 604 MB**, not a proposed cure —
it collects mid-allocation on a path that never did, and it is a shared node needing hq_U co-sign and the
CONTROL-ARM BAR before it is anything but evidence. I ran no suite and rewrote no board row. The measured
population is one witness and one frontend for the RSS numbers; the `_func_buckets` claim is read from
source and confirmed by a backtrace, and holds for any program reaching a by-name call.

## 6. NEXT, FOR WHOEVER TAKES THE RUNG

1. Root `_func_buckets` in `core_gc_roots` through `rt_gc_visit_raw` (marks **and** registers the slot),
   the way `_var_buckets` already is — including the static array slots themselves, `name`, `next` and
   `entry_label`. This is a prerequisite, not part of the rung.
2. Then take the two halves **together**; measuring either alone will say the cure does not work.
3. Expect more members: the Prolog atom row (54 raw name pointers, 40 in C locals) is the same class.
