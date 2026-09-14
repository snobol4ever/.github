# FINDING — `hb_pinned` conflates NON-MOVEMENT with THE CONSERVATIVE INTERIOR SCAN, and rung 2 deletes both

- **Seat:** hq_V (CONCERN 4, GC HEAP STORAGE — the collector across all seven languages, MODE NONET)
- **Filed:** 2026-09-13 19:22 CDT
- **Trees:** SCRIP `e62070ca8` · corpus `7214b8d6e` · .github `a126f84d` (clean, incremental `make`, `-O0`)
- **Row:** `icon-gc-rung-2-every-live-aggregate-slides-and-hb-pinned-is-deleted` (rank 0, ASSIGNED:hq_V). Blocks `icon-every-image-call-leaks-a-pinned-block-so-micro-icn-exhausts-the-heap-where-iconx-stays-at-four-megabytes` (hq_I, rank 0).

## THE CLAIM

`hb_pinned` (`src/runtime/rt/gc_heap.c:12`) is read at **three** sites, and they are not one duty but two:

| site | duty |
|---|---|
| `gc_heap.c:681` | **D1 — DO NOT MOVE.** `h->fwd = h`, `dest` unchanged; the block keeps its address across the slide. |
| `gc_heap.c:656` (non-worklist mark arm) | **D2 — SCAN MY INTERIOR.** `gc_zeta_frame(h+1, h+size)` — a conservative 8-byte-window walk of the block's payload. |
| `gc_heap.c:668` (worklist mark arm, the default) | **D2**, same call. |

The row names D1 only (*"every live aggregate SLIDES"*). D2 is unnamed, and D2 is the reachability of everything those blocks point at. **Deleting `hb_pinned` deletes D2 as a side effect, and D2 is load-bearing.** Nothing else visits the interior of an `HB_WS` block.

## THE MEASUREMENT

Witness: `benchmark_point_class_add1` minted to thirteen lines (the one diff in the 4861-entry seven-frontend A/B sweep; a Raku `class Point` with `num` attributes and a `self.bless` in a 2000-iteration loop). Arm = `SCRIP_GC_STRESS=200`; the pin-off arm is a local, unlanded `hb_pinned` short-circuit, reverted before this filing.

```
PIN ON   [ZGC] regeneration #1 (PZ): blocks 1433->70 (pinned 70, fill 11) bytes 88032->88032 reclaimed 0     slots=94
PIN OFF  [ZGC] regeneration #1 (PZ): blocks 1433->56 (pinned  0, fill  0) bytes 88032->24832 reclaimed 63200 slots=80
```

**Fourteen live blocks are collected out from under the running program** the moment D2 goes. Not a stress artefact: the program's own output degrades in step, and the degradation is graded, not binary —

```
stress=50   13001.5 19002.5   rc=0   correct
stress=100  13001.5 19002.5   rc=0   correct
stress=200  (empty)           rc=0   WRONG ANSWER, silent
stress=400  (empty)           rc=0   WRONG ANSWER, silent
```

## THE SECOND READING: `reclaimed 0` IS hq_I's ROW

The PIN ON line reads **`bytes 88032->88032 reclaimed 0`**. On this witness the collector, running to completion, frees **not one byte** — all 70 live blocks are pinned. That is `icon-every-image-call-leaks-a-pinned-block…` measured from the collector's side rather than from `micro.icn`'s: the leak is not a missing free, it is D1 applied to every block that survives. hq_I's row is BLOCKED-ON this one for the right reason.

## WHAT THIS RETIRES

⛔ **The `strlen`/`rt_heap_strdup_c` truncated pointer is NOT a half-width store, and the fixup pass is not implicated.** I owed the cto an answer on `0xffff3170`; the answer is that it is a *read of a block that was reclaimed and re-issued*, not a store through a slot of the wrong width. The control is above: the same witness at stress=100 is correct and at stress=200 is empty, with no store path changed between them — a wrong-width store would not be dose-dependent on collection frequency. My own earlier reading (a `gc_slot_reg` width or offset defect) is withdrawn with it.

⛔ **The SIGSEGV is a second defect stacked on the first, and it is in the error reporter.** Backtrace on the pin-off arm:

```
scrip: error 107: record expected
#0  try_call_builtin_by_name_bl_s   by_name_dispatch.c:5889   idb->fields[fi][0]
#5  core_error_voice                core.c:469                imaging the offending value
#8  icn_field_get (fname="x")       pattern_match.c:1425      core_icn_error(107)
```

`icn_field_get` correctly detects the corrupted record and raises 107; `core_error_voice` then images the value it was handed and dereferences the same corruption. **The error voice images a value it has already been told is not a record.** That is an unowned instrument defect (hq_B's ONE ERROR VOICE), and it is why this class costs a seat a session: the crash you get is never the crash you have.

## WHAT RUNG 2 ACTUALLY REQUIRES

D1 cannot be deleted until D2 is **replaced by precise visiting, per payload shape**, not merely removed. Demonstrated for one shape this sitting: `DATBLK_t` (the `DT_DATA` type block) holds `char *name`, `char **fields`, each `fields[i]`, and `next` — **all four unvisited by `rt_gc_visit_descr`'s `DT_DATA` case, which visits only `&u->type`.** With D2 gone they dangle; that is the `idb->fields[fi]` crash above. A precise `gc_visit_datblk` walking those four (patch preserved at `datblk-precise-root.patch`, 37 lines) **removes the SIGSEGV and error 107 entirely** and leaves only the wrong answer from the remaining unconverted shapes. All four GC gates stay green with it applied.

It is **not landed**: with D1 still in force the blocks never move, so no DONE-WHEN can fail once and pass once on it. It lands with the shape split it belongs to, not before. That is a deliberate refusal, not an omission.

The blocker for the rest is the tag conflation — see `FINDING-2026-09-13-hq_V-one-tag-covers-four-payload-shapes-so-no-relocation-write-into-an-hb-ws-block-can-be-shown-legitimate.md`.
